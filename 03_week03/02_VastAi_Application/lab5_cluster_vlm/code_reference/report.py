"""LAB 5 · step 9: summary tables, metrics.json and graphs from the raw results (no rented machine needed).

    python lab5_cluster_vlm/code/report.py --results lab5_cluster_vlm/results

Reads
    raw/vram_probe.json                   step 3  VRAM limit
    raw/runs_node1/<run>/                 step 4  1 Node (coordinator.json + worker_r*.json)
    raw/runs_2node/<run>/                 step 5  2 Node
    raw/net_probe.json                    step 5  RTT between the nodes
    raw/nodes.json                        price per hour of each node
    raw/train_2node/summary.json          step 6  training on the cluster
    eval/metrics.json                     step 7  Evaluation

Definitions (measured weight updates only, warm-up excluded as recorded by the coordinator)
    sec/update     mean wall time of one weight update at the coordinator
    compute        mean over replicas of forward + backward time
    communication  mean over replicas of send + wait + receive (wait includes waiting for the slowest replica)
    other          sec/update - compute - communication (optimizer step, averaging at the coordinator)
    receipts/s     Effective Batch / sec/update
    speedup        receipts/s of this run / receipts/s of 1 Node, same approach and Effective Batch
    efficiency     speedup / number of nodes
    cost/epoch     (800 receipts / receipts/s) in hours x sum of price per hour of all nodes used

Writes results/metrics.json and results/images/*.png (graph text in English).
"""
import argparse
import glob
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TRAIN_SET = 800
RUNS = ["A_eb8", "A_eb32", "B_eb8", "B_eb32"]
GPUS_PER_NODE = 2
COLORS = {"A": "#2f6db5", "B": "#d9822b"}


def load_run(run_dir):
    c = json.load(open(os.path.join(run_dir, "coordinator.json")))
    w = c["warmup_excluded"]
    workers = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(run_dir, "worker_r*.json")))]
    meas = c["per_step"][w:]
    sec = sum(m["step_wall_s"] for m in meas) / len(meas)
    comp, comm, send, wait, recv, util, grad = [], [], [], [], [], [], set()
    peak = 0.0
    for wk in workers:
        for r in wk["per_step"][w:]:
            comp.append(r["compute_s"])
            comm.append(r["comm_s"])
            send.append(r["send_s"])
            wait.append(r["wait_s"])
            recv.append(r["recv_s"])
            util.extend(r["gpu_util_pct"])
            grad.add(r["grad_mb_sent"])
        for r in wk["per_step"]:  # peak VRAM over the whole run, not only measured updates
            peak = max(peak, max(r["peak_vram_gib"]))
    mean = lambda xs: sum(xs) / len(xs)
    sums = [wk["lora_checksum_sha256"] for wk in workers]
    hosts = sorted({h.get("host") for h in c["replicas_info"]})
    compute_s, comm_s = mean(comp), mean(comm)
    return {
        "nodes": len(hosts),
        "gpus": len(hosts) * GPUS_PER_NODE,
        "replicas": c["replicas"],
        "accum_per_replica": c["accum_per_replica"],
        "effective_batch": c["effective_batch"],
        "updates_total": c["steps"],
        "warmup_excluded": w,
        "updates_measured": len(meas),
        "sec_per_update": sec,
        "compute_s": compute_s,
        "comm_s": comm_s,
        "comm_breakdown_s": {"send": mean(send), "wait": mean(wait), "recv": mean(recv)},
        "other_s": max(0.0, sec - compute_s - comm_s),
        "receipts_per_s": c["effective_batch"] / sec,
        "gpu_util_mean_pct": mean(util),
        "peak_vram_gib_per_gpu": peak,
        "grad_mb_per_replica_per_update": sorted(grad),
        "checksum_sha256": sums[0] if sums else None,
        "checksums_match": len(set(sums)) == 1 and len(sums) == c["replicas"],
        "workers_found": len(workers),
    }


def estimate_3_nodes(one, two, approach):
    """Calculation from measured times, NOT a measurement.

    per-receipt compute c   = 1-Node compute / receipts per replica (speed of Node 1)
    2-Node overhead         = 2-Node sec/update - c x receipts per replica at 2 Node
    3 Node: replicas        = 3 (A) or 6 (B); the slowest replica gets ceil(EB / replicas) receipts
    sec/update (optimistic) = c x ceil(EB / replicas) + 1 x 2-Node overhead
    sec/update (pessimistic)= c x ceil(EB / replicas) + 2 x 2-Node overhead
                              (two remote nodes share the link into the coordinator on Node 1)
    """
    eb = one["effective_batch"]
    c = one["compute_s"] / one["accum_per_replica"]
    overhead = two["sec_per_update"] - c * two["accum_per_replica"]
    replicas = 3 * (1 if approach == "A" else GPUS_PER_NODE)
    per = math.ceil(eb / replicas)
    out = {"replicas": replicas, "gpus": 6, "receipts_on_slowest_replica": per,
           "even_split": eb % replicas == 0, "compute_per_receipt_s": c, "overhead_2node_s": overhead}
    for tag, k in (("optimistic", 1), ("pessimistic", 2)):
        t = c * per + k * overhead
        sp = one["sec_per_update"] / t
        out[tag] = {"sec_per_update": t, "receipts_per_s": eb / t, "speedup": sp, "efficiency": sp / 3}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="lab5_cluster_vlm/results")
    a = ap.parse_args()
    R = a.results
    raw = os.path.join(R, "raw")
    img = os.path.join(R, "images")
    os.makedirs(img, exist_ok=True)

    nodes = json.load(open(os.path.join(raw, "nodes.json")))
    price = {1: nodes["vapp-lab5-n1"]["price_usd_per_hour"]}
    price[2] = price[1] + nodes["vapp-lab5-n2"]["price_usd_per_hour"]

    rows = []
    est = {}
    for name in RUNS:
        approach, eb = name.split("_eb")
        one = load_run(os.path.join(raw, "runs_node1", name))
        two = load_run(os.path.join(raw, "runs_2node", name))
        for r in (one, two):
            sp = r["receipts_per_s"] / one["receipts_per_s"]
            epoch_s = TRAIN_SET / r["receipts_per_s"]
            r.update({
                "approach": approach, "run": name, "speedup": sp, "efficiency": sp / r["nodes"],
                "price_usd_per_hour": price[r["nodes"]], "epoch_s": epoch_s,
                "usd_per_epoch": epoch_s / 3600 * price[r["nodes"]],
            })
            rows.append(r)
        est[name] = estimate_3_nodes(one, two, approach)
    rows.sort(key=lambda r: (r["approach"], r["effective_batch"], r["nodes"]))

    # step 5, first try of B_eb32 (network stall) — kept for the record, not used in the table
    stall = load_run(os.path.join(raw, "runs_2node", "B_eb32_try1_network_stall"))
    b32_1 = next(r for r in rows if r["run"] == "B_eb32" and r["nodes"] == 1)
    stall["speedup_vs_1node"] = stall["receipts_per_s"] / b32_1["receipts_per_s"]

    vram = json.load(open(os.path.join(raw, "vram_probe.json")))
    net = json.load(open(os.path.join(raw, "net_probe.json")))
    train = json.load(open(os.path.join(raw, "train_2node", "summary.json")))
    ev = json.load(open(os.path.join(R, "eval", "metrics.json")))
    gpu_total = vram[0]["gpu_total_gib"]

    metrics = {
        "lab": "LAB 5 · cluster fine-tuning of Qwen3-VL-8B (LoRA) on 2 nodes x 2 RTX 3090",
        "definitions": {
            "sec_per_update": "mean wall time of one weight update (warm-up updates excluded)",
            "receipts_per_s": "Effective Batch / sec_per_update",
            "speedup": "receipts_per_s / receipts_per_s of 1 Node, same approach and Effective Batch",
            "efficiency": "speedup / nodes",
            "usd_per_epoch": f"{TRAIN_SET} receipts / receipts_per_s, in hours, x sum of price per hour of all nodes used",
        },
        "prices_usd_per_hour": {"node1": price[1], "node2": price[2] - price[1], "1_node": price[1], "2_nodes": price[2]},
        "runs": rows,
        "runs_excluded": {"B_eb32_2node_try1_network_stall": {
            "reason": "link between the nodes stalled at updates 3-4 (gradient send 8-13 s); re-measured with the same code",
            "sec_per_update": stall["sec_per_update"], "receipts_per_s": stall["receipts_per_s"],
            "speedup_vs_1node": stall["speedup_vs_1node"], "checksums_match": stall["checksums_match"]}},
        "estimate_3_nodes": {
            "note": "CALCULATED from measured 1-Node and 2-Node times, NOT measured. Assumes the third node "
                    "computes at Node 1 speed; Effective Batch 8 and 32 do not split evenly over 3 or 6 replicas, "
                    "so the slowest replica gets ceil(EB / replicas) receipts.",
            "runs": est},
        "vram_limit_step3": {
            "gpu": vram[0]["gpu_name"], "gpu_total_gib": gpu_total,
            "weights_gib": vram[0]["weights_gib_total"], "seq_len": vram[0]["seq_len"],
            "image_tokens": vram[0]["image_tokens"], "answer_tokens": vram[0]["answer_tokens"],
            "test_receipt": vram[0]["receipt"],
            "cases": [{k: v[k] for k in ("case", "gpus", "batch", "gradient_checkpointing", "result",
                                         "peak_gib_per_gpu", "sec_per_step")} | {"layers_gpu0": v.get("layers_gpu0")}
                      for v in vram]},
        "gradient": {
            "trainable_params": vram[0]["trainable_params"],
            "total_params": vram[0]["total_params"],
            "dtype": "bf16",
            "mb_per_replica_per_update": rows[0]["grad_mb_per_replica_per_update"][0],
        },
        "network_step5": {  # target address left out on purpose
            "rtt_ms": net["rtt_ms"], "tcp_connect_ms": net["tcp_connect_ms"],
            "bulk_payload_mb": net["bulk_payload_mb"], "bulk_roundtrip_s": net["bulk_roundtrip_s"],
            "bulk_one_way_mbps_est": net["bulk_one_way_mbps_est"]},
        "training_step6": train,
        "evaluation_step7": {"models": ev["models"], "improvement_points_vs_base": ev["improvement_points_vs_base"],
                             "reference_qwen3_vl_2b": ev["reference_qwen3_vl_2b"], "settings": ev["settings"]},
        "checksums": {
            "runs": {f"{r['run']}_{r['nodes']}node": {"sha256": r["checksum_sha256"], "replicas": r["replicas"],
                                                       "match": r["checksums_match"]} for r in rows},
            "training_step6": {k: {"sha256": v["checksums"][0], "replicas": v["replicas"],
                                   "match": v["checksums_match"]} for k, v in train.items()},
        },
        "billing": {"lab_total_billed_usd": nodes.get("lab_total_billed_usd"),
                    "node1_usd": nodes["vapp-lab5-n1"]["billed_usd"]["total"],
                    "node2_usd": nodes["vapp-lab5-n2"]["billed_usd"]["total"]},
    }
    with open(os.path.join(R, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

    # 1 · speedup vs nodes
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot([1, 2, 3], [1, 2, 3], "--", color="#888", label="Ideal (speedup = nodes)")
    for name, style in (("A_eb8", ":o"), ("A_eb32", "-o"), ("B_eb8", ":s"), ("B_eb32", "-s")):
        ap_, eb = name.split("_eb")
        rr = [r for r in rows if r["run"] == name]
        xs, ys = [r["nodes"] for r in rr], [r["speedup"] for r in rr]
        ax.plot(xs, ys, style, color=COLORS[ap_], lw=2, ms=7, label=f"Approach {ap_} · EB {eb} (measured)")
        e = est[name]
        ax.plot([2, 3], [ys[-1], e["optimistic"]["speedup"]], style[0], color=COLORS[ap_], lw=1, alpha=0.4)
        ax.vlines(3, e["pessimistic"]["speedup"], e["optimistic"]["speedup"], color=COLORS[ap_], lw=5, alpha=0.35)
        ax.annotate(f"{ys[-1]:.2f}x", (2, ys[-1]), textcoords="offset points", xytext=(8, -4), fontsize=9,
                    color=COLORS[ap_])
    ax.text(3.1, 1.6, "3 nodes:\nestimate only,\ncalculated from\nmeasured times\n(bar = range)", fontsize=9,
            color="#555", va="center")
    ax.set_xticks([1, 2, 3])
    ax.set_xlim(0.8, 3.75)
    ax.set_ylim(0.6, 3.2)
    ax.set_xlabel("Number of nodes (2 x RTX 3090 each)")
    ax.set_ylabel("Speedup vs 1 node (receipts/s)")
    ax.set_title("Speedup when adding nodes")
    ax.legend(fontsize=9, loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(img, "speedup_vs_nodes.png"), dpi=150)
    plt.close(fig)

    # 2 · time per update: compute vs communication
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = [f"{r['approach']} · EB {r['effective_batch']}\n{r['nodes']} node" for r in rows]
    x = range(len(rows))
    c = [r["compute_s"] for r in rows]
    m = [r["comm_s"] for r in rows]
    o = [r["other_s"] for r in rows]
    ax.bar(x, c, color="#4a8f5c", label="Compute (forward + backward)")
    ax.bar(x, m, bottom=c, color="#c94f4f", label="Communication (send + wait + receive)")
    ax.bar(x, o, bottom=[a_ + b_ for a_, b_ in zip(c, m)], color="#bbb", label="Other (optimizer, averaging)")
    for i, r in enumerate(rows):
        ax.text(i, r["sec_per_update"] + 0.5, f"{r['sec_per_update']:.1f} s", ha="center", fontsize=9)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Seconds per weight update")
    ax.set_title("Time per weight update: compute vs communication")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(img, "time_per_update.png"), dpi=150)
    plt.close(fig)

    # 3 · peak VRAM per GPU
    fig, ax = plt.subplots(figsize=(10, 5))
    names, vals, cols, hatch = [], [], [], []
    probe_label = {"A-1gpu": "A · 1 GPU\nno GC", "A-2gpu-split18": "A · 2 GPU\nsplit 18/18",
                   "A-2gpu-split19": "A · 2 GPU\nsplit 19/17", "B-b1": "B · batch 1\nGC on",
                   "B-b2": "B · batch 2\nGC on"}
    for v in sorted(vram, key=lambda v: list(probe_label).index(v["case"])):
        names.append("probe\n" + probe_label[v["case"]])
        vals.append(max(v["peak_gib_per_gpu"]))
        cols.append(COLORS[v["case"][0]])
        hatch.append("xx" if v["result"] == "oom" else "")
    for r in rows:
        names.append(f"run {r['approach']}\nEB {r['effective_batch']} · {r['nodes']}N")
        vals.append(r["peak_vram_gib_per_gpu"])
        cols.append(COLORS[r["approach"]])
        hatch.append("")
    bars = ax.bar(range(len(vals)), vals, color=cols, edgecolor="white")
    for b, h, v in zip(bars, hatch, vals):
        if h:
            b.set_hatch(h)
            b.set_edgecolor("black")
            ax.text(b.get_x() + b.get_width() / 2, v + 0.3, "OOM", ha="center", fontsize=9, weight="bold")
        else:
            ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.1f}", ha="center", fontsize=8)
    ax.axhline(gpu_total, color="#c00", ls="--")
    ax.text(len(vals) - 0.5, gpu_total + 0.3, f"RTX 3090 24 GB ({gpu_total} GiB usable)", ha="right",
            color="#c00", fontsize=9)
    ax.axvline(4.5, color="#999", lw=0.8)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(names, fontsize=7.5)
    ax.set_ylim(0, 29)
    ax.set_ylabel("Peak VRAM per GPU (GiB)")
    ax.set_title("Peak VRAM per GPU · step 3 limit probe (left) and cluster runs (right)")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=COLORS["A"], label="Approach A (model split over 2 GPUs, no GC)"),
                       Patch(color=COLORS["B"], label="Approach B (1 GPU per model copy, GC on)"),
                       Patch(facecolor="white", edgecolor="black", hatch="xx", label="Out of memory")],
              fontsize=9, loc="upper center", ncol=3, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(img, "peak_vram.png"), dpi=150)
    plt.close(fig)

    # 4 · cost per epoch
    fig, ax = plt.subplots(figsize=(8, 5))
    vals = [r["usd_per_epoch"] for r in rows]
    bars = ax.bar(range(len(rows)), vals, color=[COLORS[r["approach"]] for r in rows],
                  alpha=[0.55 if r["nodes"] == 1 else 1.0 for r in rows][0])
    for b, r in zip(bars, rows):
        b.set_alpha(0.55 if r["nodes"] == 1 else 1.0)
        ax.text(b.get_x() + b.get_width() / 2, r["usd_per_epoch"] + 0.003,
                f"\\${r['usd_per_epoch']:.3f}\n{r['epoch_s'] / 60:.1f} min", ha="center", fontsize=8.5)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel(f"USD per epoch ({TRAIN_SET} receipts)")
    ax.set_title(f"Cost per epoch · 1 node \\${price[1]:.3f}/h · 2 nodes \\${price[2]:.3f}/h (light = 1 node)")
    ax.set_ylim(0, max(vals) * 1.25)
    fig.tight_layout()
    fig.savefig(os.path.join(img, "cost_per_epoch.png"), dpi=150)
    plt.close(fig)

    # console summary
    print(f"{'run':7s} N GPU rep EB   s/upd  comp  comm  rec/s  speedup eff   $/h    min/ep $/epoch peakGiB chk")
    for r in rows:
        print(f"{r['run']:7s} {r['nodes']} {r['gpus']:3d} {r['replicas']:3d} {r['effective_batch']:2d} "
              f"{r['sec_per_update']:7.2f} {r['compute_s']:5.2f} {r['comm_s']:5.2f} {r['receipts_per_s']:6.3f} "
              f"{r['speedup']:6.2f}x {r['efficiency']:4.0%} {r['price_usd_per_hour']:.4f} "
              f"{r['epoch_s'] / 60:6.1f} {r['usd_per_epoch']:.4f} {r['peak_vram_gib_per_gpu']:5.2f} {r['checksums_match']}")
    print("3-node estimate (calculated, not measured):")
    for k, e in est.items():
        print(f"  {k}: {e['replicas']} replicas, slowest gets {e['receipts_on_slowest_replica']} receipts, "
              f"overhead {e['overhead_2node_s']:.2f} s -> speedup {e['pessimistic']['speedup']:.2f}-"
              f"{e['optimistic']['speedup']:.2f}x (eff {e['pessimistic']['efficiency']:.0%}-{e['optimistic']['efficiency']:.0%})")
    print(f"excluded B_eb32 try1: {stall['sec_per_update']:.2f} s/update, speedup {stall['speedup_vs_1node']:.2f}x")


if __name__ == "__main__":
    main()
