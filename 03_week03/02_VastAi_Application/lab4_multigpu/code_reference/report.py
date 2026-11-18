"""Report for LAB 4: 1 GPU vs 2 GPU training speed and money per epoch.

Reads   results/raw/bench/bench_1gpu.json, bench_2gpu.json  (one per run, from bench.py)
        results/raw/bench/bench_<N>gpu/gpu_util.csv, cpu.csv (raw per-second samples)
        results/raw/prices.json                               (market prices + the rented machine)
Writes  results/metrics.json
        results/images/1_epoch_time.png  2_speedup.png  3_cost_per_epoch.png  4_bottleneck.png

  ideal        = sec/epoch on 1 GPU / number of GPUs
  speedup      = sec/epoch on 1 GPU / sec/epoch on N GPUs
  efficiency   = speedup / number of GPUs
  $ per epoch  = $ per hour * sec/epoch / 3600

Usage:  python code/report.py
"""
import csv, json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "raw"
IMG = ROOT / "results" / "images"

C_1 = "#4C78A8"      # 1 GPU
C_2 = "#F58518"      # 2 GPU
C_IDEAL = "#54A24B"  # ideal line
C_GREY = "#9D9D9D"


def load_run(n):
    run = json.loads((RAW / "bench" / f"bench_{n}gpu.json").read_text())
    # cross-check the GPU util mean from the raw per-second samples (all samples with util > 0)
    rows = list(csv.DictReader(open(RAW / "bench" / f"bench_{n}gpu" / "gpu_util.csv")))
    busy = [int(r["util_pct"]) for r in rows if int(r["util_pct"]) > 0]
    run["_raw_util_busy_mean"] = round(sum(busy) / len(busy), 1) if busy else None
    run["_raw_samples"] = len(rows)
    return run


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    prices = json.loads((RAW / "prices.json").read_text())
    runs = {1: load_run(1), 2: load_run(2)}
    t1 = runs[1]["sec_per_epoch"]
    step1 = runs[1]["sec_per_step"]
    rented = prices["rented"]["usd_per_hour"]

    rows = []
    for n, r in runs.items():
        sec = r["sec_per_epoch"]
        ideal = t1 / n
        speedup = t1 / sec
        market = prices["market"][f"{n}gpu"]["usd_per_hour"]
        util = list(r["gpu_util_mean"].values())
        rows.append({
            "gpus": n,
            "sec_per_epoch": sec,
            "ideal_sec_per_epoch": round(ideal, 2),
            "speedup": round(speedup, 3),
            "ideal_speedup": n,
            "efficiency_pct": round(100 * speedup / n, 1),
            "sec_per_step": r["sec_per_step"],
            "step_compute_sec": step1,                                  # 1-GPU step = pure compute for 32 images/GPU
            "step_extra_sec": round(r["sec_per_step"] - step1, 4),     # added by running on N GPUs
            "steps_per_epoch": r["steps_per_epoch"],
            "images_per_sec": r["images_per_sec"],
            "gpu_util_mean_pct": r["gpu_util_mean"],
            "gpu_util_avg_pct": round(sum(util) / len(util), 1),
            "cpu_cores_used": r["cpu_cores_used"],
            "machine_cpu_threads": r["machine_cpu_threads"],
            "allreduce_80mb_ms": (r["allreduce_80mb"] or {}).get("median_ms"),
            "allreduce_busbw_GBps": (r["allreduce_80mb"] or {}).get("busbw_GBps"),
            "map50": r["map50"],
            "market_usd_per_hour": market,
            "market_usd_per_epoch": round(market * sec / 3600, 5),
            "rented_usd_per_hour": rented,
            "rented_usd_per_epoch": round(rented * sec / 3600, 5),
            "epoch_seconds_all": r["epoch_seconds"],
        })

    best_market = min(rows, key=lambda x: x["market_usd_per_epoch"])
    best_rented = min(rows, key=lambda x: x["rented_usd_per_epoch"])
    metrics = {
        "source": {"runs": ["raw/bench/bench_1gpu.json", "raw/bench/bench_2gpu.json"], "prices": "raw/prices.json"},
        "setup": {k: runs[1][k] for k in ("model", "epochs", "imgsz", "batch_per_gpu", "seed", "train_images")},
        "gpu_topology": "GPU0-GPU1 = PHB (PCIe through the CPU host bridge, no NVLink)",
        "prices": prices,
        "rows": rows,
        "cheapest_per_epoch": {"market": f"{best_market['gpus']} GPU", "rented_machine": f"{best_rented['gpus']} GPU"},
    }
    (ROOT / "results" / "metrics.json").write_text(json.dumps(metrics, indent=2))

    r1, r2 = rows
    labels = ["1 GPU", "2 GPU"]
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

    # 1) seconds per epoch vs ideal
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    bars = ax.bar(labels, [r1["sec_per_epoch"], r2["sec_per_epoch"]], color=[C_1, C_2], width=0.55)
    ax.plot(labels, [r1["ideal_sec_per_epoch"], r2["ideal_sec_per_epoch"]], "--o", color=C_IDEAL, lw=2,
            label="ideal = 1-GPU time / GPUs")
    for b, v in zip(bars, [r1["sec_per_epoch"], r2["sec_per_epoch"]]):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f} s", ha="center", va="bottom", fontweight="bold")
    ax.annotate(f"ideal {r2['ideal_sec_per_epoch']:.1f} s", (1, r2["ideal_sec_per_epoch"]), xytext=(12, -14),
                textcoords="offset points", color=C_IDEAL)
    ax.set_ylabel("seconds per epoch (lower is better)")
    ax.set_title("Time per epoch: measured vs ideal (YOLO11m, RTX 3090)")
    ax.set_ylim(0, r1["sec_per_epoch"] * 1.2)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(IMG / "1_epoch_time.png", dpi=150); plt.close(fig)

    # 2) speedup vs ideal
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot([1, 2], [1, 2], "--o", color=C_IDEAL, lw=2, label="ideal (linear)")
    ax.plot([1, 2], [r1["speedup"], r2["speedup"]], "-o", color=C_2, lw=2.5, ms=8, label="measured")
    ax.annotate(f"{r2['speedup']:.2f}x  (efficiency {r2['efficiency_pct']:.0f}%)", (2, r2["speedup"]),
                xytext=(-20, -55), textcoords="offset points", color=C_2, fontweight="bold", ha="center")
    ax.annotate("2.00x", (2, 2), xytext=(-40, 6), textcoords="offset points", color=C_IDEAL)
    ax.set_xticks([1, 2]); ax.set_xticklabels(labels)
    ax.set_xlim(0.8, 2.2); ax.set_ylim(0.8, 2.2)
    ax.set_ylabel("speedup vs 1 GPU (higher is better)")
    ax.set_title("Speedup: measured vs ideal")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(IMG / "2_speedup.png", dpi=150); plt.close(fig)

    # 3) $ per epoch: market price vs the rented machine
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = [0, 1]; w = 0.36
    m = [r1["market_usd_per_epoch"], r2["market_usd_per_epoch"]]
    rt = [r1["rented_usd_per_epoch"], r2["rented_usd_per_epoch"]]
    b1 = ax.bar([i - w / 2 for i in x], m, w, color=[C_1, C_2], label="market price (cheapest offer)")
    b2 = ax.bar([i + w / 2 for i in x], rt, w, color=[C_1, C_2], alpha=0.45, hatch="//", edgecolor="white",
                label=f"rented machine vapp-lab4 (${rented:.3f}/h, 2 GPU)")
    for bars, vals, hours in ((b1, m, [r1["market_usd_per_hour"], r2["market_usd_per_hour"]]), (b2, rt, [rented, rented])):
        for b, v, h in zip(bars, vals, hours):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.0002, f"${v:.4f}\n(${h:.3f}/h)", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("USD per epoch (lower is better)")
    ax.set_title("Money per epoch")
    ax.set_ylim(0, max(rt + m) * 1.35)
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    fig.tight_layout(); fig.savefig(IMG / "3_cost_per_epoch.png", dpi=150); plt.close(fig)

    # 4) bottleneck: step time split + GPU util vs CPU cores used
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.6))
    comp = [r1["step_compute_sec"], r2["step_compute_sec"]]
    extra = [0, r2["step_extra_sec"]]
    a.bar(labels, comp, color=C_1, width=0.55, label="compute (same as 1-GPU step)")
    a.bar(labels, extra, bottom=comp, color=C_2, width=0.55, label="extra on 2 GPU (sync / gradient all-reduce)")
    a.text(0, comp[0] / 2, f"{comp[0]*1000:.0f} ms", ha="center", color="white", fontweight="bold")
    a.text(1, comp[1] / 2, f"{comp[1]*1000:.0f} ms", ha="center", color="white", fontweight="bold")
    a.text(1, comp[1] + extra[1] + 0.005, f"+{extra[1]*1000:.0f} ms\n(all-reduce 80 MB = {r2['allreduce_80mb_ms']:.0f} ms)",
           ha="center", va="bottom", fontsize=9)
    a.set_ylabel("seconds per step (32 images per GPU)")
    a.set_title("Time per step")
    a.set_ylim(0, (comp[1] + extra[1]) * 1.4)
    a.legend(frameon=False, loc="upper left", fontsize=9)

    gl = ["1 GPU\nGPU0", "2 GPU\nGPU0", "2 GPU\nGPU1"]
    gv = [r1["gpu_util_mean_pct"]["gpu0"], r2["gpu_util_mean_pct"]["gpu0"], r2["gpu_util_mean_pct"]["gpu1"]]
    bb = b.bar(gl, gv, color=[C_1, C_2, C_2], width=0.55)
    for bar, v in zip(bb, gv):
        b.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:.1f}%", ha="center")
    b.set_ylim(0, 115); b.set_ylabel("GPU utilization (%)")
    b2_ = b.twinx()
    b2_.plot([0, 1.5], [r1["cpu_cores_used"], r2["cpu_cores_used"]], "D-", color=C_GREY, lw=2, ms=8,
             label=f"CPU cores used (of {r1['machine_cpu_threads']} threads)")
    for xx, v in ((0, r1["cpu_cores_used"]), (1.5, r2["cpu_cores_used"])):
        b2_.annotate(f"{v:.1f} cores", (xx, v), xytext=(-20, 12), textcoords="offset points", color="#555")
    b2_.set_ylim(0, r1["machine_cpu_threads"]); b2_.set_ylabel("CPU cores used")
    b2_.spines["top"].set_visible(False)
    b2_.legend(frameon=False, loc="upper right", fontsize=9)
    b.set_title("GPU utilization vs CPU used")
    fig.suptitle("Where the time goes", fontweight="bold")
    fig.tight_layout(); fig.savefig(IMG / "4_bottleneck.png", dpi=150); plt.close(fig)

    for r in rows:
        print(f"{r['gpus']} GPU  {r['sec_per_epoch']:7.2f} s/epoch  ideal {r['ideal_sec_per_epoch']:7.2f}  "
              f"speedup {r['speedup']:.2f}x  eff {r['efficiency_pct']:5.1f}%  "
              f"market ${r['market_usd_per_hour']:.4f}/h -> ${r['market_usd_per_epoch']:.5f}/epoch  "
              f"rented ${r['rented_usd_per_hour']:.4f}/h -> ${r['rented_usd_per_epoch']:.5f}/epoch")
    print("raw util check (busy samples):", {n: runs[n]["_raw_util_busy_mean"] for n in runs})
    print("saved", ROOT / "results" / "metrics.json", "and", IMG)


if __name__ == "__main__":
    main()
