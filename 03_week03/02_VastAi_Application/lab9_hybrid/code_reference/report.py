"""LAB 9: read every result file of the lab -> metrics.json + 6 charts (English labels).

Inputs (in --results, default /workspace/lab9):
  loadtest.json               step 3  ladder, synchronous API, 1 GPU (baseline)
  loadtest_hybrid.json        step 6  ladder, hybrid (gateway + queue + 1 worker)
  loadtest_hybrid_2gpu.json   step 8  ladder, hybrid with 2 workers
  burst_sync.json / burst_hybrid.json   step 7  200 jobs within 10 s
  killtest.json               step 9  90 jobs, gpu1 worker killed at second 4
Outputs (in --out): metrics.json and
  1_latency_vs_users.png  2_throughput_vs_users.png  3_scaling_vs_gpus.png
  4_burst_sync_vs_hybrid.png  5_express_vs_normal.png  6_kill_worker_timeline.png
Run: python report.py [--results /workspace/lab9] [--out /workspace/lab9/report]
"""
import argparse, json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--results", default="/workspace/lab9")
ap.add_argument("--out", default="/workspace/lab9/report")
args = ap.parse_args()
R, OUT = Path(args.results), Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)

def load(name):
    for p in (R / name, R / "code" / name):
        if p.exists():
            return json.loads(p.read_text())
    raise SystemExit(f"missing {name} in {R}")

SLO = 10.0
C = {"sync": "#d1495b", "h1": "#00798c", "h2": "#edae49", "ideal": "#7a7a7a",
     "express": "#d1495b", "normal": "#00798c"}
plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": 0.3, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})

# ---------- 1) ladders: capacity, best throughput ----------
ladders = {
    "sync": ("Synchronous API, 1 GPU (baseline)", load("loadtest.json"), 1),
    "h1": ("Hybrid queue, 1 GPU worker", load("loadtest_hybrid.json"), 1),
    "h2": ("Hybrid queue, 2 GPU workers", load("loadtest_hybrid_2gpu.json"), 2),
}
systems = {}
for key, (label, d, gpus) in ladders.items():
    lv = sorted(d["levels"], key=lambda l: l["users"])
    cap = d["max_users_meeting_slo"]
    at_cap = next(l for l in lv if l["users"] == cap)
    systems[key] = {
        "label": label, "gpus": gpus, "capacity_users": cap, "first_failing_users": d["first_failing_users"],
        "p95_at_capacity_sec": at_cap["p95_sec"], "p50_at_capacity_sec": at_cap["p50_sec"],
        "max_images_per_sec": max(l["images_per_sec"] for l in lv),
        "gpu_util_at_capacity_pct": at_cap["gpu_util_pct"][:gpus],
        "levels": [{k: l.get(k) for k in ("users", "images_per_sec", "p50_sec", "p95_sec", "p99_sec",
                                          "failed_pct", "gpu_util_pct", "avg_images_per_batch", "slo_pass")}
                   for l in lv],
    }
base, h1, h2 = systems["sync"], systems["h1"], systems["h2"]
for s in systems.values():
    s["x_baseline_capacity"] = round(s["capacity_users"] / base["capacity_users"], 2)
    s["x_baseline_images_per_sec"] = round(s["max_images_per_sec"] / base["max_images_per_sec"], 2)
eff_users = h2["capacity_users"] / (2 * h1["capacity_users"])
eff_ips = h2["max_images_per_sec"] / (2 * h1["max_images_per_sec"])
h2["efficiency_vs_hybrid_1gpu_users_pct"] = round(100 * eff_users, 1)
h2["efficiency_vs_hybrid_1gpu_images_per_sec_pct"] = round(100 * eff_ips, 1)
est3 = {"gpus": 3, "note": "estimated = hybrid 1 GPU x 3 x efficiency measured at 2 GPUs (not measured)",
        "capacity_users": int(h1["capacity_users"] * 3 * min(eff_users, 1.0)),
        "max_images_per_sec": round(h1["max_images_per_sec"] * 3 * min(eff_ips, 1.0), 2)}

def cap_marker(ax, s, key, y):
    ax.plot(s["capacity_users"], y, marker="*", ms=16, color=C[key], mec="black", mew=0.7, zorder=5)
    ax.annotate(f"capacity {s['capacity_users']}", (s["capacity_users"], y), textcoords="offset points",
                xytext=(8, -16), fontsize=9, color=C[key], fontweight="bold")

# chart 1: latency p50 / p95 vs N
fig, ax = plt.subplots(figsize=(9, 5.2))
for key, s in systems.items():
    n = [l["users"] for l in s["levels"]]
    ax.plot(n, [l["p95_sec"] for l in s["levels"]], "-o", color=C[key], lw=2, ms=4, label=f"{s['label']} - p95")
    ax.plot(n, [l["p50_sec"] for l in s["levels"]], "--", color=C[key], lw=1.4, alpha=0.8, label=f"{s['label']} - p50")
    cap_marker(ax, s, key, s["p95_at_capacity_sec"])
ax.axhline(SLO, color="black", ls=":", lw=1.5)
ax.text(0.99, SLO + 0.25, "SLO: p95 <= 10 s", fontsize=9, ha="right", transform=ax.get_yaxis_transform())
ax.set(xlabel="Concurrent users (N)", ylabel="Wait until image is received (s)",
       title="Wait time vs concurrent users (star = capacity: largest N that meets the SLO)", ylim=(0, 15))
ax.legend(fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig(OUT / "1_latency_vs_users.png"); plt.close(fig)

# chart 2: images/s vs N
fig, ax = plt.subplots(figsize=(9, 5))
for key, s in systems.items():
    n = [l["users"] for l in s["levels"]]
    ax.plot(n, [l["images_per_sec"] for l in s["levels"]], "-o", color=C[key], lw=2, ms=4, label=s["label"])
    ax.axvline(s["capacity_users"], color=C[key], ls=":", lw=1)
    ax.annotate(f"max {s['max_images_per_sec']} img/s", (n[-1], s["levels"][-1]["images_per_sec"]),
                textcoords="offset points", xytext=(4, 4), fontsize=9, color=C[key])
ax.set(xlabel="Concurrent users (N)", ylabel="Images delivered per second",
       title="Throughput vs concurrent users (dotted line = capacity of each system)")
ax.set_ylim(0, max(s["max_images_per_sec"] for s in systems.values()) * 1.2)
ax.legend(fontsize=9, loc="upper left")
fig.tight_layout(); fig.savefig(OUT / "2_throughput_vs_users.png"); plt.close(fig)

# chart 3: scaling vs GPUs
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
for ax, field, unit, est_v, eff in ((axes[0], "capacity_users", "Capacity (users at p95 <= 10 s)", est3["capacity_users"], eff_users),
                                     (axes[1], "max_images_per_sec", "Max images per second", est3["max_images_per_sec"], eff_ips)):
    ideal = [h1[field] * g for g in (1, 2, 3)]
    ax.plot([1, 2, 3], ideal, "--", color=C["ideal"], lw=1.5, label="ideal (100% efficiency)")
    ax.plot([1, 2], [h1[field], h2[field]], "-o", color=C["h1"], lw=2.2, ms=8, label="hybrid queue (measured)")
    ax.plot([2, 3], [h2[field], est_v], ":", color=C["h1"], lw=1.5)
    ax.plot(3, est_v, "o", ms=9, mfc="white", mec=C["h1"], mew=2, label="3 GPUs (estimated)")
    ax.annotate(f"{est_v}\nestimated", (3, est_v), textcoords="offset points", xytext=(-62, -6), fontsize=9,
                color=C["h1"], fontstyle="italic")
    ax.plot(1, base[field], "s", ms=9, color=C["sync"], label="synchronous baseline (measured)")
    for g, v in ((1, h1[field]), (2, h2[field])):
        ax.annotate(f"{v}", (g, v), textcoords="offset points", xytext=(8, -4), fontsize=9)
    ax.annotate(f"{base[field]}", (1, base[field]), textcoords="offset points", xytext=(8, -4), fontsize=9, color=C["sync"])
    ax.text(2, h2[field] * 0.55, f"efficiency at 2 GPUs\n= {eff * 100:.0f}%", ha="center", fontsize=9,
            bbox=dict(boxstyle="round", fc="#f3f3f3", ec="#bbbbbb"))
    ax.set(xlabel="Number of GPUs (one worker per GPU)", ylabel=unit, xticks=[1, 2, 3], xlim=(0.6, 3.4))
    ax.set_ylim(0, max(ideal) * 1.15)
    ax.legend(fontsize=8, loc="upper left")
axes[0].set_title("Capacity vs GPUs"); axes[1].set_title("Max throughput vs GPUs")
fig.suptitle("Scaling the hybrid system: 1 -> 2 GPUs measured, 3 GPUs estimated", fontsize=11)
fig.tight_layout(); fig.savefig(OUT / "3_scaling_vs_gpus.png"); plt.close(fig)

# ---------- 2) burst: synchronous vs hybrid ----------
bs, bh = load("burst_sync.json"), load("burst_hybrid.json")
burst = {}
for key, d in (("sync", bs), ("hybrid", bh)):
    s = d["summary"]
    burst[key] = {"jobs": s["jobs"], "ok": s["ok"], "ok_pct": s["ok_pct"], "gave_up": s["gave_up"],
                  "wait_p50_sec": s["wait_p50_sec"], "wait_p95_sec": s["wait_p95_sec"], "wait_max_sec": s["wait_max_sec"],
                  "first_answer_p50_sec": s["first_answer_p50_sec"],
                  "images_drawn_by_server": d["images_drawn_by_server"], "images_wasted": d["images_wasted"],
                  "answers_429": s["answers_429"], "jobs_got_429": s["jobs_got_429"],
                  "peak_backlog": d["peak_backlog"], "drained_after_sec": d["drained_after_sec"],
                  "by_priority": {p: {k: v[k] for k in ("jobs", "ok", "wait_p50_sec", "wait_p95_sec", "wait_max_sec")}
                                  for p, v in d["by_priority"].items()}}

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
ax = axes[0]
for key, d, lab in (("sync", bs, "Synchronous API (users give up after 30 s)"), ("h1", bh, "Hybrid queue (1 worker)")):
    tl = d["backlog_every_0_5s"]
    ax.plot([p["t"] for p in tl], [p["backlog"] for p in tl], color=C[key], lw=2, label=lab)
ax.axvspan(0, 10, color="#999999", alpha=0.12)
ax.text(5, 8, "200 jobs arrive\n(first 10 s)", ha="center", va="bottom", fontsize=8)
ax.set(xlabel="Time since burst start (s)", ylabel="Jobs waiting or running on the server",
       title="Backlog over time during a 200-job burst (1 GPU)")
ax.legend(fontsize=8, loc="upper right")
ax = axes[1]
cats = ["Users who got\ntheir image", "Users who\ngave up", "Images drawn\nfor nobody (wasted)"]
x = range(len(cats)); w = 0.38
vs = [burst["sync"]["ok"], burst["sync"]["gave_up"], burst["sync"]["images_wasted"]]
vh = [burst["hybrid"]["ok"], burst["hybrid"]["gave_up"], burst["hybrid"]["images_wasted"]]
b1 = ax.bar([i - w / 2 for i in x], vs, w, color=C["sync"], label="Synchronous")
b2 = ax.bar([i + w / 2 for i in x], vh, w, color=C["h1"], label="Hybrid queue")
ax.bar_label(b1, fontsize=9); ax.bar_label(b2, fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(cats, fontsize=8.5)
ax.set(ylabel="Jobs (out of 200)", title="Outcome of the burst", ylim=(0, 230))
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "4_burst_sync_vs_hybrid.png"); plt.close(fig)

# chart 5: express vs normal wait (hybrid burst)
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1, 1.4]})
ax = axes[0]
stats_k = [("wait_p50_sec", "p50"), ("wait_p95_sec", "p95"), ("wait_max_sec", "max")]
bp = bh["by_priority"]
for i, (p, off) in enumerate((("express", -0.2), ("normal", 0.2))):
    bars = ax.bar([j + off for j in range(3)], [bp[p][k] for k, _ in stats_k], 0.38, color=C[p],
                  label=f"{p} ({bp[p]['jobs']} jobs)")
    ax.bar_label(bars, fmt="%.1f", fontsize=9)
ax.set_xticks(range(3)); ax.set_xticklabels([n for _, n in stats_k])
ax.set(ylabel="Wait until image is received (s)", title="Express vs normal jobs in the burst")
ax.legend(fontsize=9)
ax = axes[1]
for p in ("normal", "express"):
    js = [j for j in bh["jobs"] if j["priority"] == p and j.get("ok")]
    ax.scatter([j["arrive_sec"] for j in js], [j["wait_sec"] for j in js], s=16 if p == "normal" else 34,
               color=C[p], alpha=0.75, label=p, edgecolor="white", linewidth=0.4)
ax.set(xlabel="Arrival time within the burst (s)", ylabel="Wait (s)", title="Every job: arrival time vs wait")
ax.legend(fontsize=9)
fig.suptitle("Priority queue: express jobs jump ahead of normal jobs (hybrid, 1 worker, 200-job burst)", fontsize=11)
fig.tight_layout(); fig.savefig(OUT / "5_express_vs_normal.png"); plt.close(fig)

# ---------- 3) kill test ----------
kt = load("killtest.json")
ks, tl = kt["summary"], kt["timeline_every_0_5s"]
fig, ax = plt.subplots(figsize=(10.5, 5.2))
t = [p["t"] for p in tl]
ax.plot(t, [p["waiting"] for p in tl], color="#00798c", lw=2, label="waiting in queue")
ax.plot(t, [p["running"] for p in tl], color="#edae49", lw=2, label="running (taken by a worker)")
ax.plot(t, [p["done"] for p in tl], color="#30638e", lw=2.4, label="done")
ax.plot(t, [p["dead"] for p in tl], color="#d1495b", lw=2, label="dead-letter queue (bad job)")
ax.step(t, [p["redelivered"] for p in tl], where="post", color="#6a4c93", lw=1.6, ls="--", label="redelivered")
down_end = ks.get("victim_back_sec", t[-1])
ax.axvspan(ks["kill_sec"], down_end, color="#d1495b", alpha=0.08)
ymax = max(p["done"] for p in tl) * 1.12
for x, lab in ((ks["last_submit_sec"], "90 jobs sent"), (ks["kill_sec"], f"SIGKILL {ks['victim']}"),
               (ks["all_finished_sec"], "all jobs finished"), (ks["restart_sec"], f"restart {ks['victim']}"),
               (down_end, f"{ks['victim']} back")):
    ax.axvline(x, color="#555555", ls=":", lw=1)
    ax.text(x + 0.2, ymax * 0.97, lab, rotation=90, va="top", fontsize=8, color="#333333")
ax.text((ks["kill_sec"] + down_end) / 2, ymax * 0.45, f"only 1 worker alive\n({ks['victim']} down)",
        ha="center", fontsize=9, color="#d1495b")
ax.set(xlabel="Time since first job (s)", ylabel="Jobs", ylim=(0, ymax),
       title=f"Kill a worker mid-work: {ks['good_jobs_done']}/{ks['good_jobs_sent']} good jobs done, "
             f"{ks['good_jobs_lost']} lost, {ks['redelivered_jobs']} redelivered, "
             f"{ks['bad_jobs_dead_lettered']} bad job -> dead-letter")
ax.legend(fontsize=8.5, loc="center right")
fig.tight_layout(); fig.savefig(OUT / "6_kill_worker_timeline.png"); plt.close(fig)

# ---------- metrics.json ----------
metrics = {
    "slo": {"p95_sec_max": SLO, "failed_pct_lt": 1.0},
    "capacity_table": [
        {"gpus": s["gpus"], "architecture": s["label"], "capacity_users": s["capacity_users"],
         "max_images_per_sec": s["max_images_per_sec"], "p95_at_capacity_sec": s["p95_at_capacity_sec"],
         "x_baseline_capacity": s["x_baseline_capacity"],
         "efficiency_vs_hybrid_1gpu_pct": s.get("efficiency_vs_hybrid_1gpu_users_pct", 100.0 if k == "h1" else None)}
        for k, s in systems.items()],
    "estimate_3_gpus": est3,
    "ladders": systems,
    "burst": burst,
    "kill_worker": ks,
    "charts": sorted(p.name for p in OUT.glob("*.png")),
}
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=1))
for row in metrics["capacity_table"]:
    print(row)
print("3 GPUs (estimated):", est3)
print("charts:", metrics["charts"])
