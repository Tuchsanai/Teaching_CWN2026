"""Training speed benchmark: YOLO11m (COCO-pretrained) on hard-hat-workers, 1 or 2 GPUs.

Same settings every run: 5 epochs, imgsz 640, batch 32 images per GPU, seed 0,
no validation during training (one validation at the end only).

Writes one JSON per run:  <out>/bench_<N>gpu[_tag].json
  sec_per_epoch   mean of epochs 2..E-1 (first = warm-up, last = includes final validation)
  sec_per_step    sec_per_epoch / optimizer steps per epoch
  map50           mAP50 on the Validation Set at the end
  gpu_util_mean   mean GPU util (%) of each GPU over the steady epochs
  cpu_cores_used  CPU seconds used by the whole job (all processes) / wall seconds, over the steady epochs
  allreduce_ms    (2 GPUs only) time to all-reduce an 80 MB gradient between the GPUs

Raw data kept next to the JSON: results.csv, gpu_util.csv, cpu.csv, train.log.

Usage:
  python bench.py --gpus 1
  python bench.py --gpus 2
  python bench.py --gpus 1 --fraction 0.05 --epochs 2 --tag smoke     # quick test
"""
import argparse, csv, json, math, os, socket, subprocess, sys, threading, time
from pathlib import Path


# ---------------------------------------------------------------- helpers
def gpu_snapshot():
    """Per-GPU util / memory and the list of processes on the GPUs."""
    q = subprocess.check_output(["nvidia-smi", "--query-gpu=index,name,utilization.gpu,memory.used",
                                 "--format=csv,noheader,nounits"], text=True)
    gpus = []
    for line in q.strip().splitlines():
        i, name, util, mem = [x.strip() for x in line.split(",")]
        gpus.append({"index": int(i), "name": name, "util": int(util), "mem_mib": int(mem)})
    apps = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory",
                                    "--format=csv,noheader"], text=True).strip()
    return gpus, [a for a in apps.splitlines() if a.strip()]


def check_gpus_free(n):
    gpus, apps = gpu_snapshot()
    if len(gpus) < n:
        sys.exit(f"need {n} GPUs, machine has {len(gpus)}")
    busy = [g for g in gpus[:n] if g["mem_mib"] > 500 or g["util"] > 5]
    if apps or busy:
        sys.exit(f"GPUs are not free -> processes: {apps}  busy: {busy}")
    print(f"[check] {n} GPU(s) free:", [(g['index'], g['name'], f"{g['util']}%", f"{g['mem_mib']}MiB") for g in gpus[:n]])
    return gpus[:n]


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def _allreduce_worker(rank, world, port, nbytes, iters, q):
    import torch, torch.distributed as dist
    torch.cuda.set_device(rank)
    dist.init_process_group("nccl", init_method=f"tcp://127.0.0.1:{port}", rank=rank, world_size=world)
    x = torch.ones(nbytes // 4, dtype=torch.float32, device="cuda")
    for _ in range(10):                                   # warm-up (NCCL builds its rings here)
        dist.all_reduce(x)
    torch.cuda.synchronize()
    times = []
    for _ in range(iters):
        dist.barrier(); torch.cuda.synchronize()
        t = time.perf_counter(); dist.all_reduce(x); torch.cuda.synchronize()
        times.append((time.perf_counter() - t) * 1000)
    if rank == 0:
        q.put(times)
    dist.destroy_process_group()


def allreduce_bench(world=2, mb=80, iters=50):
    import torch.multiprocessing as mp
    nbytes = mb * 1024 * 1024
    ctx = mp.get_context("spawn"); q = ctx.Queue()
    mp.spawn(_allreduce_worker, args=(world, free_port(), nbytes, iters, q), nprocs=world, join=True)
    t = sorted(q.get())
    med = t[len(t) // 2]
    busbw = nbytes * 2 * (world - 1) / world / (med / 1000) / 1e9      # NCCL "bus bandwidth" GB/s
    res = {"size_mb": mb, "iters": iters, "median_ms": round(med, 2),
           "mean_ms": round(sum(t) / len(t), 2), "min_ms": round(t[0], 2), "busbw_GBps": round(busbw, 2)}
    print("[all-reduce]", res)
    return res


class Monitor(threading.Thread):
    """Every second: GPU util of each GPU + CPU seconds of the whole job (this process and all its children).
    Also notes the wall-clock time when each epoch row appears in results.csv."""

    def __init__(self, ngpu, outdir, csv_path):
        super().__init__(daemon=True)
        import psutil
        self.psutil, self.ngpu, self.outdir, self.csv_path = psutil, ngpu, outdir, csv_path
        self.stop_evt = threading.Event()
        self.gpu_rows, self.cpu_rows, self.epoch_marks = [], [], {}
        self.proc = psutil.Process(os.getpid())
        self.seen = {}                                     # (pid, create_time) -> last cpu seconds
        self.dead = 0.0                                    # cpu seconds of processes that have exited
        self.smi = subprocess.Popen(
            ["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used", "--format=csv,noheader,nounits", "-lms", "1000"],
            stdout=subprocess.PIPE, text=True)
        threading.Thread(target=self._read_smi, daemon=True).start()

    def _read_smi(self):
        for line in self.smi.stdout:
            p = [x.strip() for x in line.split(",")]
            if len(p) == 3 and p[0].isdigit():
                self.gpu_rows.append((time.time(), int(p[0]), int(p[1]), int(p[2])))

    def job_cpu_seconds(self):
        alive = {}
        procs = [self.proc] + self.proc.children(recursive=True)
        for p in procs:
            if p.pid == self.smi.pid:
                continue
            try:
                ct = p.cpu_times(); alive[(p.pid, p.create_time())] = ct.user + ct.system
            except self.psutil.Error:
                pass
        for k, v in self.seen.items():                      # processes gone since last sample
            if k not in alive:
                self.dead += v
        self.seen = alive
        return self.dead + sum(alive.values())

    def run(self):
        while not self.stop_evt.is_set():
            now = time.time()
            self.cpu_rows.append((now, self.job_cpu_seconds()))
            if self.csv_path.exists():
                n = max(0, len(self.csv_path.read_text().strip().splitlines()) - 1)
                for e in range(1, n + 1):
                    self.epoch_marks.setdefault(e, now)
            time.sleep(1)

    def stop(self):
        self.stop_evt.set(); self.join(5); self.smi.terminate()
        with open(self.outdir / "gpu_util.csv", "w", newline="") as f:
            csv.writer(f).writerows([("time", "gpu", "util_pct", "mem_mib"), *self.gpu_rows])
        with open(self.outdir / "cpu.csv", "w", newline="") as f:
            csv.writer(f).writerows([("time", "job_cpu_seconds"), *self.cpu_rows])

    def window_stats(self, t0, t1):
        util = {}
        for g in range(self.ngpu):
            v = [u for t, i, u, _ in self.gpu_rows if i == g and t0 <= t <= t1]
            util[f"gpu{g}"] = round(sum(v) / len(v), 1) if v else None
        c = [(t, s) for t, s in self.cpu_rows if t0 <= t <= t1]
        cores = round((c[-1][1] - c[0][1]) / (c[-1][0] - c[0][0]), 2) if len(c) > 1 else None
        return util, cores


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpus", type=int, choices=[1, 2], required=True)
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch-per-gpu", type=int, default=32)
    ap.add_argument("--fraction", type=float, default=1.0, help="share of Training Set images to use")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8, help="dataloader workers per GPU")
    ap.add_argument("--model", default="yolo11m.pt")
    ap.add_argument("--data", default="/workspace/hardhat")
    ap.add_argument("--out", default="/workspace/bench")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    name = f"bench_{a.gpus}gpu" + (f"_{a.tag}" if a.tag else "")
    out = Path(a.out) / name
    if out.exists():
        import shutil; shutil.rmtree(out)
    out.mkdir(parents=True)

    gpus = check_gpus_free(a.gpus)
    topo = subprocess.check_output(["nvidia-smi", "topo", "-m"], text=True)
    allreduce = allreduce_bench(a.gpus) if a.gpus > 1 else None

    # data.yaml with absolute paths (the Roboflow one uses ../train/images)
    import yaml
    src = yaml.safe_load(open(Path(a.data) / "data.yaml"))
    data_yaml = out / "data.yaml"
    yaml.safe_dump({"path": a.data, "train": "train/images", "val": "valid/images", "test": "test/images",
                    "nc": src["nc"], "names": src["names"]}, open(data_yaml, "w"))
    n_train = len(list((Path(a.data) / "train/images").iterdir()))
    n_used = round(n_train * a.fraction) if a.fraction < 1 else n_train
    total_batch = a.batch_per_gpu * a.gpus
    steps = math.ceil(n_used / total_batch)

    from ultralytics import YOLO
    import ultralytics, torch
    model = YOLO(a.model)
    csv_path = out / "train" / "results.csv"
    mon = Monitor(a.gpus, out, csv_path); mon.start()
    t_start = time.time()
    model.train(data=str(data_yaml), epochs=a.epochs, imgsz=a.imgsz, batch=total_batch, seed=a.seed,
                deterministic=True, val=False, plots=False, workers=a.workers, fraction=a.fraction,
                device=list(range(a.gpus)) if a.gpus > 1 else 0, project=str(out), name="train", exist_ok=True)
    t_end = time.time()
    mon.stop()

    rows = list(csv.DictReader(open(csv_path)))
    rows = [{k.strip(): v for k, v in r.items()} for r in rows]
    cum = [float(r["time"]) for r in rows]
    per_epoch = [round(c - p, 2) for c, p in zip(cum, [0.0] + cum[:-1])]
    steady = per_epoch[1:-1] if len(per_epoch) > 2 else per_epoch      # drop first + last epoch
    sec_per_epoch = sum(steady) / len(steady)

    # steady window for util / CPU: from end of epoch 1 to end of epoch E-1
    marks = mon.epoch_marks
    if a.epochs > 2 and 1 in marks and (a.epochs - 1) in marks:
        w0, w1, wnote = marks[1], marks[a.epochs - 1], f"epochs 2..{a.epochs - 1}"
    else:
        w0, w1, wnote = t_start, marks.get(a.epochs, t_end), "whole run (too few epochs for a steady window)"
    util, cores = mon.window_stats(w0, w1)
    last = rows[-1]

    res = {
        "run": name, "gpus": a.gpus, "gpu_names": [g["name"] for g in gpus],
        "model": a.model, "epochs": a.epochs, "imgsz": a.imgsz, "batch_per_gpu": a.batch_per_gpu,
        "batch_total": total_batch, "seed": a.seed, "workers_per_gpu": a.workers, "fraction": a.fraction,
        "train_images": n_used, "steps_per_epoch": steps,
        "epoch_seconds": per_epoch,
        "sec_per_epoch": round(sec_per_epoch, 2),
        "sec_per_step": round(sec_per_epoch / steps, 4),
        "images_per_sec": round(n_used / sec_per_epoch, 1),
        "map50": round(float(last["metrics/mAP50(B)"]), 4),
        "map50_95": round(float(last["metrics/mAP50-95(B)"]), 4),
        "gpu_util_mean": util,
        "cpu_cores_used": cores,
        "machine_cpu_threads": os.cpu_count(),
        "steady_window": {"what": wnote, "seconds": round(w1 - w0, 1)},
        "allreduce_80mb": allreduce,
        "wall_seconds": round(t_end - t_start, 1),
        "versions": {"ultralytics": ultralytics.__version__, "torch": torch.__version__, "cuda": torch.version.cuda},
        "gpu_topology": topo,
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    js = Path(a.out) / f"{name}.json"
    js.write_text(json.dumps(res, indent=2))
    (out / f"{name}.json").write_text(json.dumps(res, indent=2))
    print("[result]", json.dumps({k: res[k] for k in ("run", "sec_per_epoch", "sec_per_step", "map50",
                                                      "gpu_util_mean", "cpu_cores_used", "allreduce_80mb")}))
    print("saved", js)


if __name__ == "__main__":
    main()
