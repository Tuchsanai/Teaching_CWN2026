"""Step 12 · numbers + 2 charts from results/capacity/raw/*.json (run on this PC after lt.sh pull)."""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "capacity" / "raw"; OUT = ROOT / "results" / "capacity"
B, O = "#2a78d6", "#eb6834"                       # categorical slots 1-2 (validated default palette)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
R = {p.stem: json.loads(p.read_text(encoding="utf8")) for p in RAW.glob("*.json")}

def style(ax):
    ax.set_facecolor("#fcfcfb"); ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2)

def cum(xs):
    xs = sorted(xs); return [0] + xs, [0] + list(range(1, len(xs) + 1))

# ---- numbers
runs = [("run1", "capacity_1w", "capacity_2w"), ("run2", "capacity_1w_run2", "capacity_2w_run2")]
rows = []
for tag, a, b in runs:
    one, two = R[a], R[b]
    rows.append({"run": tag, "t_1worker_s": one["makespan_s"], "t_2workers_s": two["makespan_s"],
                 "rate_1worker_per_min": one["rate_per_min"], "rate_2workers_per_min": two["rate_per_min"],
                 "max_latency_1w_s": one["max_latency_s"], "max_latency_2w_s": two["max_latency_s"],
                 "accept_100_1w_s": one["accept_all_s"], "accept_100_2w_s": two["accept_all_s"],
                 "speedup": round(one["makespan_s"] / two["makespan_s"], 2)})
m1 = sum(r["t_1worker_s"] for r in rows) / 2; m2 = sum(r["t_2workers_s"] for r in rows) / 2
summary = {
    "capacity": rows, "mean_t_1worker_s": round(m1, 1), "mean_t_2workers_s": round(m2, 1),
    "mean_speedup": round(m1 / m2, 2), "efficiency": round(m1 / m2 / 2, 2), "slo_normal_s": 1800,
    "urgent": {k: R["urgent"][k] for k in ("urgent_all_done_s", "urgent_finish_s", "claim_window",
               "max_urgent_in_a_row", "normals_in_window", "normal_done_before_urgent", "normal_all_done_s", "g5_response")},
    "queuefull": {k: v for k, v in R["queuefull"].items() if k != "queue_before"},
    "crash": R["crash"], "dlq": R["dlq"],
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf8")
with open(OUT / "capacity.csv", "w", newline="", encoding="utf8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps({k: summary[k] for k in ("capacity", "mean_t_1worker_s", "mean_t_2workers_s", "mean_speedup", "efficiency")}, indent=1))

# ---- chart 1: completion curves, 1 vs 2 workers
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150); fig.patch.set_facecolor("#fcfcfb"); style(ax)
for tag, a, b in runs:
    ls = "-" if tag == "run1" else "--"
    for key, col, lab in ((a, B, "1 GPU worker"), (b, O, "2 GPU workers")):
        x, y = cum(R[key]["curve"])
        ax.step(x, y, where="post", color=col, lw=2, ls=ls, label=f"{lab} · {tag} ({R[key]['makespan_s']:.0f} s)")
ax.set_xlabel("Elapsed time since the first submission (s)", color=INK)
ax.set_ylabel("Receipts with a result (cumulative)", color=INK)
ax.set_title(f"Normal batch of 100 receipts · mean speedup {m1/m2:.2f}× (efficiency {m1/m2/2:.0%})",
             color=INK, loc="left", fontsize=12)
ax.text(0.99, 0.04, "NFR-02 SLO: 1,800 s (30 min), far beyond this axis", transform=ax.transAxes,
        ha="right", color=INK2, fontsize=9)
ax.set_ylim(0, 105); ax.set_xlim(0, None)
ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1, 0.1), labelcolor=INK)
fig.tight_layout(); fig.savefig(OUT / "capacity_1v2_workers.png"); plt.close(fig)

# ---- chart 2: urgent while normal receipts are pending
u = R["urgent"]; tu = u["t_urgent_rel"]
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150); fig.patch.set_facecolor("#fcfcfb"); style(ax)
x, y = cum(u["curve_normal"]); ax.step(x, y, where="post", color=B, lw=2, label="Normal job (100 receipts)")
x, y = cum(u["curve_urgent"]); ax.step(x, y, where="post", color=O, lw=2, label="Urgent job (10 receipts)")
ax.axvline(tu, color=INK2, lw=1, ls=":")
ax.text(tu + 1, 92, f"G5 set urgent at {tu:.0f} s\n10/10 urgent done in {u['urgent_all_done_s']:.1f} s\n(SLO NFR-03: 300 s)",
        color=INK, fontsize=9, va="top")
ax.text(0.01, 0.97, f"Claim order after the urgent call: {u['claim_window']}  (U = urgent, N = normal; max {u['max_urgent_in_a_row']} U in a row, BR-10 limit 4)",
        transform=ax.transAxes, color=INK2, fontsize=9, va="top")
ax.set_xlabel("Elapsed time since the first submission (s)", color=INK)
ax.set_ylabel("Receipts with a result (cumulative)", color=INK)
ax.set_title("Urgent job overtakes 66 pending normal receipts (2 GPU workers)", color=INK, loc="left", fontsize=12)
ax.set_ylim(0, 105); ax.set_xlim(0, None)
ax.legend(frameon=False, loc="lower right", labelcolor=INK)
fig.tight_layout(); fig.savefig(OUT / "urgent_priority.png"); plt.close(fig)
print("saved", [p.name for p in OUT.iterdir()])
