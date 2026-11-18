"""LAB 5 · step 5: 1 Node vs 2 Node table from the raw results.

    python compare_nodes.py --raw lab5_cluster_vlm/results/raw

Per run (measured updates only, warm-up excluded):
    sec/update   = mean wall time of one weight update at the coordinator
    compute      = mean over replicas of the time spent on forward+backward
    comm         = mean over replicas of send + wait + receive
                   (wait also contains time spent waiting for the slowest replica)
    receipts/s   = Effective Batch / sec/update
    speedup      = receipts/s (2 Node) / receipts/s (1 Node), same approach and Effective Batch
    efficiency   = speedup / 2 (twice the machines)
"""
import argparse
import glob
import json
import os


def load(run_dir):
    c = json.load(open(os.path.join(run_dir, "coordinator.json")))
    w = c["warmup_excluded"]
    workers = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(run_dir, "**", "worker_r*.json"), recursive=True))]
    meas = c["per_step"][w:]
    sec = sum(m["step_wall_s"] for m in meas) / len(meas)
    comp, comm, grad = [], [], set()
    for wk in workers:
        for r in wk["per_step"][w:]:
            comp.append(r["compute_s"])
            comm.append(r["comm_s"])
            grad.add(r["grad_mb_sent"])
    sums = [wk["lora_checksum_sha256"] for wk in workers]
    return {"replicas": c["replicas"], "accum": c["accum_per_replica"], "eb": c["effective_batch"],
            "n_measured": len(meas), "sec_per_update": sec,
            "compute_s": sum(comp) / len(comp), "comm_s": sum(comm) / len(comm),
            "receipts_per_s": c["effective_batch"] / sec, "grad_mb": sorted(grad),
            "workers_found": len(workers), "checksums_match": len(set(sums)) == 1 and len(sums) == c["replicas"],
            "checksum": sums[0][:12] if sums else None,
            "hosts": sorted({h.get("host") for h in c["replicas_info"]})}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="lab5_cluster_vlm/results/raw")
    a = ap.parse_args()
    rows = []
    for name in ["A_eb8", "A_eb32", "B_eb8", "B_eb32"]:
        one = load(os.path.join(a.raw, "runs_node1", name))
        two = load(os.path.join(a.raw, "runs_2node", name))
        sp = two["receipts_per_s"] / one["receipts_per_s"]
        rows.append({"run": name, "node1": one, "node2": two, "speedup": sp, "efficiency": sp / 2})
        for tag, r in (("1 Node", one), ("2 Node", two)):
            print(f"{name:7s} {tag}: replicas {r['replicas']} accum {r['accum']} · {r['sec_per_update']:.2f} s/update "
                  f"(compute {r['compute_s']:.2f} / comm {r['comm_s']:.2f}) · {r['receipts_per_s']:.3f} receipts/s · "
                  f"grad {r['grad_mb']} MB · checksums match {r['checksums_match']} ({r['workers_found']} workers, {r['hosts']})")
        print(f"{name:7s} speedup {sp:.2f}x · efficiency {sp / 2:.0%}")
    with open(os.path.join(a.raw, "compare_nodes.json"), "w") as f:
        json.dump(rows, f, indent=2)


if __name__ == "__main__":
    main()
