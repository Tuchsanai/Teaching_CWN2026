"""LAB 8 report: read every experiment JSON in results/ -> metrics.json + charts (English labels).

  python report.py                       # reads ../results, writes ../results/metrics.json + ../results/charts/*.png
  python report.py --results /path/to/results

Experiments it looks for (any that are missing are skipped):
  baseline/        sync API, 1 GPU, no queue (user gives up after 30 s)
  queue_1worker/   gateway + RabbitMQ + 1 GPU worker
  queue_2worker/   gateway + RabbitMQ + 2 GPU workers (one per GPU, same queue)
Each folder: level_NXX.json (one load level), sweep_summary.json, burst.json (60 jobs in 10 s).
  worker_kill/killtest.json   60 jobs in 10 s on 2 workers, GPU-1 worker SIGKILLed at 20 s
                              -> metrics.json "worker_kill" + charts/worker_kill_cumulative.png

Definitions
  capacity N       = largest N that met the SLO (p95 <= 20 s and fail < 1 %) in the sweep
  max throughput   = highest jobs/min seen in any level of the sweep
  burst throughput = jobs finished / time until the queue was drained (a saturated system)
  speed-up         = value with g GPUs / value with 1 GPU
  efficiency       = speed-up / g
  3-GPU estimate   = CALCULATED, not measured: 1-GPU value x 3 x efficiency measured at 2 GPUs
"""
import argparse
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent

SYSTEMS = [  # folder, label, number of GPUs, color (fixed categorical order)
    ("baseline", "Sync API, 1 GPU (no queue)", 1, "#1baf7a"),
    ("queue_1worker", "Queue, 1 worker (1 GPU)", 1, "#2a78d6"),
    ("queue_2worker", "Queue, 2 workers (2 GPUs)", 2, "#eb6834"),
]
TEXT = "#3d3d3a"
MUTED = "#8a897f"
GRID = "#e4e3dd"
SLO_COLOR = "#c0392b"

plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": TEXT, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold",
    "axes.titlesize": 12, "legend.frameon": False, "figure.dpi": 110,
})


def load(path):
    return json.loads(path.read_text()) if path.exists() else None


def read_system(folder):
    if not folder.exists():
        return None
    levels = []
    for p in sorted(folder.glob("level_N*.json")):
        d = load(p)
        levels.append({k: d.get(k) for k in (
            "users", "jobs_per_min", "latency_p50_s", "latency_p95_s", "latency_p99_s",
            "fail_pct", "gpu_util_avg_pct", "gpu_util_per_gpu_pct", "loadgen_cpu_avg_pct",
            "queue_length_max", "server_wait_p95_s", "server_gpu_p50_s", "timeout_s",
            "workers", "slo_pass")})
    levels.sort(key=lambda r: r["users"])
    sweep = load(folder / "sweep_summary.json") or {}
    slo = sweep.get("slo", {"p95_s_max": 20, "fail_pct_below": 1})
    for r in levels:  # recompute so every system is judged by the same rule
        r["slo_pass"] = (r["latency_p95_s"] is not None and r["latency_p95_s"] <= slo["p95_s_max"]
                         and r["fail_pct"] < slo["fail_pct_below"])
    passing = [r for r in levels if r["slo_pass"]]
    cap = max(passing, key=lambda r: r["users"]) if passing else None
    best = max(levels, key=lambda r: r["jobs_per_min"]) if levels else None
    burst = load(folder / "burst.json")
    b = None
    if burst:
        drain = burst.get("queue_empty_at_s") or burst.get("server_drained_after_s")
        b = {k: burst.get(k) for k in (
            "jobs", "within_s", "succeeded", "failed", "fail_pct", "latency_p50_s",
            "latency_p95_s", "queue_length_max", "queue_peak_at_s", "queue_empty_at_s",
            "server_drained_after_s", "server_jobs_redelivered", "workers")}
        b["drain_s"] = drain
        b["burst_jobs_per_min"] = round(burst["succeeded"] / (burst["server_drained_after_s"] / 60), 2)
        b["queue_timeline"] = [(r["t"], r["queue_length"]) for r in burst.get("queue_timeline", [])
                               if r.get("queue_length") is not None]
    return {"levels": levels, "slo": slo,
            "capacity_users": cap["users"] if cap else 0,
            "p95_at_capacity_s": cap["latency_p95_s"] if cap else None,
            "jobs_per_min_at_capacity": cap["jobs_per_min"] if cap else None,
            "max_jobs_per_min": best["jobs_per_min"] if best else None,
            "max_jobs_per_min_at_users": best["users"] if best else None,
            "first_n_tested": levels[0]["users"] if levels else None,
            "burst": b}


def scaling(sys1, sys2):
    out = {"gpus": [1, 2]}
    for key, name in (("capacity_users", "capacity"), ("max_jobs_per_min", "max_throughput"),
                      ("burst_jobs_per_min", "burst_throughput")):
        v1 = sys1["burst"][key] if key == "burst_jobs_per_min" else sys1[key]
        v2 = sys2["burst"][key] if key == "burst_jobs_per_min" else sys2[key]
        speed = v2 / v1 if v1 else None
        out[name] = {"1_gpu": v1, "2_gpu": v2,
                     "speedup_x": round(speed, 2) if speed else None,
                     "efficiency_pct": round(100 * speed / 2, 1) if speed else None}
    return out


def estimate_3gpu(sys1, sc):
    """CALCULATED from measured numbers - not a measurement."""
    est = {"is_measured": False,
           "method": "value_1gpu x 3 x efficiency_measured_at_2gpu "
                     "(assumes each added GPU helps as much as the 2nd one did, and that the "
                     "gateway, RabbitMQ and CPU are not the bottleneck)"}
    e_cap = sc["capacity"]["efficiency_pct"] / 100
    e_tp = sc["max_throughput"]["efficiency_pct"] / 100
    e_b = sc["burst_throughput"]["efficiency_pct"] / 100
    raw_users = sys1["capacity_users"] * 3 * e_cap
    est["capacity_users_raw"] = round(raw_users, 2)
    est["capacity_users"] = math.floor(raw_users + 1e-9)
    est["max_jobs_per_min"] = round(sys1["max_jobs_per_min"] * 3 * e_tp, 2)
    est["burst_jobs_per_min"] = round(sys1["burst"]["burst_jobs_per_min"] * 3 * e_b, 2)
    est["burst_60_drain_s"] = round(60 / est["burst_jobs_per_min"] * 60, 1)
    est["ideal_capacity_users"] = sys1["capacity_users"] * 3
    return est


# ---------------------------------------------------------------- charts
def mark_capacity(ax, s, color, key):
    lv = next((r for r in s["levels"] if r["users"] == s["capacity_users"]), None)
    if lv:
        ax.scatter([lv["users"]], [lv[key]], s=170, marker="*", color=color, zorder=5,
                   edgecolor="white", linewidth=1.5)
        ax.annotate(f"capacity N={lv['users']}", (lv["users"], lv[key]), textcoords="offset points",
                    xytext=(8, -14), color=TEXT, fontsize=9)


def chart_latency(systems, out):
    fig, ax = plt.subplots(figsize=(8, 5))
    slo = 20
    for folder, label, _, color in SYSTEMS:
        s = systems.get(folder)
        if not s:
            continue
        slo = s["slo"]["p95_s_max"]
        n = [r["users"] for r in s["levels"]]
        ax.plot(n, [r["latency_p95_s"] for r in s["levels"]], "-o", color=color, lw=2, ms=7,
                label=f"{label} - p95")
        ax.plot(n, [r["latency_p50_s"] for r in s["levels"]], "--", marker="o", mfc="white",
                color=color, lw=1.5, ms=6, label=f"{label} - p50")
        if folder != "baseline":
            mark_capacity(ax, s, color, "latency_p95_s")
    ax.axhline(slo, color=SLO_COLOR, lw=1.5, ls=":")
    ax.text(ax.get_xlim()[1], slo, f"SLO p95 = {slo:g} s ", color=SLO_COLOR, ha="right",
            va="bottom", fontsize=9)
    ax.set_xlabel("Concurrent users (N)")
    ax.set_ylabel("Time from submit to result (s)")
    ax.set_title("Latency vs concurrent users (star = capacity: largest N meeting the SLO)")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(out / "latency_vs_users.png")
    plt.close(fig)


def chart_throughput(systems, out):
    fig, ax = plt.subplots(figsize=(8, 5))
    for folder, label, _, color in SYSTEMS:
        s = systems.get(folder)
        if not s:
            continue
        n = [r["users"] for r in s["levels"]]
        ax.plot(n, [r["jobs_per_min"] for r in s["levels"]], "-o", color=color, lw=2, ms=7, label=label)
        if folder != "baseline":
            mark_capacity(ax, s, color, "jobs_per_min")
    ax.set_xlabel("Concurrent users (N)")
    ax.set_ylabel("Successful jobs per minute")
    ax.set_title("Throughput vs concurrent users (4 receipts per job)")
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(out / "throughput_vs_users.png")
    plt.close(fig)


def chart_scaling(sys1, sys2, est, out):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    panels = [("capacity_users", "Capacity (concurrent users meeting SLO)", "users"),
              ("max_jobs_per_min", "Max throughput (jobs/min)", "jobs/min")]
    for ax, (key, title, unit) in zip(axes, panels):
        v1, v2 = sys1[key], sys2[key]
        ax.plot([1, 2, 3], [v1, 2 * v1, 3 * v1], ls="--", color=MUTED, lw=1.5,
                label="Ideal (linear: 1 GPU x g)")
        ax.plot([1, 2], [v1, v2], "-o", color="#eb6834", lw=2, ms=9, label="Measured")
        ax.plot([2, 3], [v2, est[key]], ":", color="#eb6834", lw=1.5)
        ax.scatter([3], [est[key]], s=90, facecolor="white", edgecolor="#eb6834", lw=2, zorder=5,
                   label="Estimated (calculated, not measured)")
        for g, v, tag in ((1, v1, ""), (2, v2, ""), (3, est[key], " (est.)")):
            ax.annotate(f"{v:g}{tag}", (g, v), textcoords="offset points", xytext=(8, -4),
                        color=TEXT, fontsize=9)
        ax.set_xticks([1, 2, 3])
        ax.set_xlabel("Number of GPUs (1 worker per GPU)")
        ax.set_ylabel(unit)
        ax.set_title(title)
        ax.set_ylim(bottom=0)
        ax.set_xlim(0.7, 3.4)
        ax.legend(fontsize=8, loc="upper left")
    fig.suptitle("Scaling with GPUs vs ideal linear scaling", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out / "scaling_vs_gpus.png")
    plt.close(fig)


def chart_burst(systems, out):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for folder, label, _, color in SYSTEMS[1:]:
        s = systems.get(folder)
        if not s or not s["burst"]:
            continue
        b = s["burst"]
        t = [x[0] for x in b["queue_timeline"]]
        q = [x[1] for x in b["queue_timeline"]]
        ax.plot(t, q, color=color, lw=2, label=f"{label}: drained in {b['drain_s']:.0f} s")
        if b["drain_s"]:
            ax.axvline(b["drain_s"], color=color, lw=1, ls=":")
    ax.set_xlabel("Time since the first job was sent (s)")
    ax.set_ylabel("Jobs waiting in the queue")
    ax.set_title("Burst of 60 jobs in 10 s: queue length over time")
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(out / "burst_queue_length.png")
    plt.close(fig)


WORKER_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#8e5bd6"]


def read_killtest(path):
    d = load(path)
    if not d:
        return None
    keep = ("jobs", "within_s", "workers", "kill", "sent", "accepted", "succeeded", "failed",
            "lost", "done_by_worker", "redelivered_jobs", "latency_p50_s", "latency_p95_s",
            "ok_latency_max_s", "errors", "server_drained_after_s", "server_jobs_done",
            "server_jobs_failed", "server_jobs_redelivered", "dead_letter_queue",
            "queue_length_max", "gpu_util_per_gpu_pct")
    m = {k: d.get(k) for k in keep}
    m["redelivered_count"] = len(d.get("redelivered_jobs") or [])
    m["no_job_lost"] = d.get("lost") == 0 and d.get("succeeded") == d.get("sent")
    return m, d.get("done_timeline") or []


def chart_killtest(m, timeline, out):
    fig, ax = plt.subplots(figsize=(8.5, 5))
    workers = sorted({r["worker"] for r in timeline} | set(m["workers"] or []))
    for i, w in enumerate(workers):
        ts = [r["t"] for r in timeline if r["worker"] == w]
        color = WORKER_COLORS[i % len(WORKER_COLORS)]
        short = w.split("-")[-1].upper()
        killed = w == m["kill"].get("worker")
        lab = f"Worker {short}: {len(ts)} jobs" + (" (killed)" if killed else "")
        ax.step([0] + ts, list(range(len(ts) + 1)), where="post", color=color, lw=2, label=lab)
        for r in timeline:
            if r["worker"] == w and r["redelivered"]:
                y = ts.index(r["t"]) + 1
                ax.scatter([r["t"]], [y], s=120, marker="D", facecolor="white", edgecolor=color,
                           lw=2, zorder=5)
                ax.annotate("redelivered job", (r["t"], y), textcoords="offset points",
                            xytext=(8, -12), color=TEXT, fontsize=9)
    all_t = [r["t"] for r in timeline]
    ax.step([0] + all_t, list(range(len(all_t) + 1)), where="post", color=MUTED, lw=1.5, ls="--",
            label=f"All workers: {len(all_t)} of {m['sent']} jobs")
    k = m["kill"].get("at_s")
    if k is not None:
        ax.axvline(k, color=SLO_COLOR, lw=1.5, ls=":")
        ax.text(k, ax.get_ylim()[1] * 0.97, f"  SIGKILL GPU-{m['kill']['gpu']} worker at {k:.0f} s",
                color=SLO_COLOR, va="top", fontsize=9)
    ax.set_xlabel("Time since the first job was sent (s)")
    ax.set_ylabel("Jobs finished (cumulative)")
    ax.set_title(f"Worker killed mid-burst: {m['jobs']} jobs in {m['within_s']:g} s, "
                 f"{m['lost']} lost")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=9, loc="lower right")
    fig.tight_layout()
    fig.savefig(out / "worker_kill_cumulative.png")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(HERE.parent / "results"))
    args = ap.parse_args()
    res = Path(args.results)
    charts = res / "charts"
    charts.mkdir(parents=True, exist_ok=True)

    systems = {f: s for f, *_ in SYSTEMS if (s := read_system(res / f))}
    metrics = {"workload": {"receipts_per_job": 4, "think_s": 10, "level_s": 75, "warmup_s": 15,
                            "burst": "60 jobs within 10 s", "model": "Qwen/Qwen3-VL-2B-Instruct",
                            "gpu": "RTX 3090"},
               "slo": {"p95_s_max": 20, "fail_pct_below": 1},
               "systems": {}}
    for folder, label, gpus, _ in SYSTEMS:
        s = systems.get(folder)
        if s:
            m = {k: v for k, v in s.items()}
            if m["burst"]:
                m["burst"] = {k: v for k, v in m["burst"].items() if k != "queue_timeline"}
            metrics["systems"][folder] = {"label": label, "gpus": gpus, **m}

    chart_latency(systems, charts)
    chart_throughput(systems, charts)
    if "queue_1worker" in systems and "queue_2worker" in systems:
        sc = scaling(systems["queue_1worker"], systems["queue_2worker"])
        est = estimate_3gpu(systems["queue_1worker"], sc)
        metrics["scaling"] = sc
        metrics["estimate_3gpu"] = est
        chart_scaling(systems["queue_1worker"], systems["queue_2worker"], est, charts)
    chart_burst(systems, charts)
    kt = read_killtest(res / "worker_kill" / "killtest.json")
    if kt:
        metrics["worker_kill"] = kt[0]
        chart_killtest(kt[0], kt[1], charts)
        print("worker_kill", {k: kt[0][k] for k in ("sent", "succeeded", "lost",
                                                    "redelivered_count", "done_by_worker")})

    (res / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(json.dumps({k: metrics.get(k) for k in ("scaling", "estimate_3gpu")}, indent=2))
    for f, s in systems.items():
        print(f, "capacity", s["capacity_users"], "max jobs/min", s["max_jobs_per_min"],
              "drain", s["burst"] and s["burst"]["drain_s"])
    print("charts:", sorted(p.name for p in charts.glob("*.png")))


if __name__ == "__main__":
    main()
