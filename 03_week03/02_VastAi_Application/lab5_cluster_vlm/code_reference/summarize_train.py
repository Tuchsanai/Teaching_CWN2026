"""LAB 5 · step 6: summarize the 2-node training runs (A, B) -> results/raw/train_2node/summary.json + losses.csv."""
import csv, json, os, sys
R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "results")
T = os.path.join(R, "raw", "train_2node")
out, rows = {}, []
for ap in ["A", "B"]:
    d = os.path.join(T, ap)
    c = json.load(open(os.path.join(d, "coordinator.json")))
    ws = [json.load(open(os.path.join(d, f))) for f in sorted(os.listdir(d)) if f.startswith("worker_r")]
    loss = [s["loss_mean"] for s in c["per_step"]]
    peak = max(max(s["peak_vram_gib"]) for w in ws for s in w["per_step"])
    seen = set(); [seen.update(s["receipts"]) for w in ws for s in w["per_step"]]
    ad = os.path.join(R, f"adapter_{ap}", "adapter_model.safetensors")
    out[ap] = {"replicas": c["replicas"], "accum_per_replica": c["accum_per_replica"],
               "effective_batch": c["effective_batch"], "updates": c["steps"],
               "unique_receipts": len(seen),
               "train_wall_s": c["train_wall_s"],
               "round_wall_s_incl_model_load": int(open(os.path.join(d, "round_wall_s.txt")).read()),
               "model_load_s_per_replica": [w["load_s"] for w in ws],
               "loss_first10_mean": round(sum(loss[:10]) / 10, 4),
               "loss_last10_mean": round(sum(loss[-10:]) / 10, 4),
               "loss_first": loss[0], "loss_last": loss[-1],
               "peak_vram_gib_per_gpu_max": peak,
               "peak_vram_gib_per_replica": [max(max(s["peak_vram_gib"]) for s in w["per_step"]) for w in ws],
               "checksums": c["checksums"], "checksums_match": c["checksums_match"],
               "adapter_bytes": os.path.getsize(ad)}
    rows += [[ap, s["step"], s["loss_mean"], s["step_wall_s"]] for s in c["per_step"]]
json.dump(out, open(os.path.join(T, "summary.json"), "w"), indent=2)
with open(os.path.join(T, "losses.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["approach", "update", "loss_mean", "update_wall_s"]); w.writerows(rows)
print(json.dumps(out, indent=1))
