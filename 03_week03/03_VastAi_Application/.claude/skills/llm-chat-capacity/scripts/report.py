#!/usr/bin/env python3
"""LAB 6 report: read every loadtest_*.json in the results folder, write metrics.json + charts there.

usage: python report.py [results_dir]     (default: ../results next to this script)
"""
import glob, json, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "results"))

# fixed categorical order (colour follows the run, never its rank)
COLORS = {"single_1gpu": "#eb6834", "batch_1gpu": "#2a78d6", "batch_2gpu": "#1baf7a"}
FALLBACK = ["#eda100", "#e87ba4", "#008300"]
INK, MUTED, GRID = "#2b2b2b", "#6b6b6b", "#e4e3de"


def is_lb_run(r):
    """load-balancer comparison runs (loadtest_lb_*.json, mixed short/long answers) are reported separately"""
    return r.get("label", "").startswith("lb_")


LB_NAME = {"round_robin": "Round Robin", "least_conn": "least_conn"}
LB_COLORS = {"round_robin": "#eb6834", "least_conn": "#2a78d6"}
GPU_COLORS = ["#1baf7a", "#8a5cd1"]          # GPU 0 / GPU 1 (same in every panel)


def load_lb_runs():
    """one row per loadtest_lb_*.json: TTFT, speed, throughput and in-flight requests per GPU"""
    out = []
    for p in sorted(glob.glob(os.path.join(RES, "loadtest_lb_*.json"))):
        r = json.load(open(p, encoding="utf-8"))
        if not r.get("levels") or not is_lb_run(r):
            continue
        L = r["levels"][0]
        lb = r.get("server", {}).get("lb", "?")
        ports = sorted(L["vllm_queue"])               # port8001 = GPU 0, port8002 = GPU 1
        per_gpu = []
        for i, port in enumerate(ports):
            q = L["vllm_queue"][port]
            ts = [pt[port]["running"] for pt in L.get("vllm_timeseries", []) if port in pt]
            per_gpu.append({
                "gpu": i, "backend": f"vllm-{i + 1}",
                "running_avg": q["running_avg"], "running_max": q["running_max"],
                "running_min": min(ts) if ts else None,
                "waiting_avg": q["waiting_avg"], "waiting_max": q["waiting_max"],
                "requests_done": L["requests_per_backend"].get(f"vllm-{i + 1}", 0),
                "long_requests_done": L.get("by_kind", {}).get("long", {}).get("requests_per_backend", {}).get(f"vllm-{i + 1}", 0),
                "sm_clock_mhz_avg": L.get("gpu_sm_clock_mhz_avg", {}).get(str(i)),
                "temp_c_max": L.get("gpu_temp_c_max", {}).get(str(i)),
            })
        run_avg = [g["running_avg"] or 0 for g in per_gpu]
        kinds = L.get("by_kind", {})
        out.append({
            "label": r["label"], "file": os.path.basename(p), "lb": lb, "lb_name": LB_NAME.get(lb, lb),
            "users": L["users"], "window_s": r["config"]["duration_s"] - r["config"]["warmup_s"],
            "warmup_s": r["config"]["warmup_s"], "long_frac": r["config"].get("long_frac"),
            "max_tokens_short": r["config"]["max_tokens"], "max_tokens_long": r["config"].get("long_max_tokens"),
            "requests_counted": L["requests_counted"], "error_rate": L["error_rate"],
            "ttft_p50_s": L["ttft_s"]["p50"], "ttft_p95_s": L["ttft_s"]["p95"], "ttft_p99_s": L["ttft_s"]["p99"],
            "speed_p5_tok_s": L["speed_tok_s_per_user"]["p5"], "speed_p50_tok_s": L["speed_tok_s_per_user"]["p50"],
            "total_tok_s": L["total_tok_s"],
            "ttft_p95_short_s": kinds.get("short", {}).get("ttft_s", {}).get("p95"),
            "ttft_p95_long_s": kinds.get("long", {}).get("ttft_s", {}).get("p95"),
            "tokens_mean_short": kinds.get("short", {}).get("completion_tokens_mean"),
            "tokens_mean_long": kinds.get("long", {}).get("completion_tokens_mean"),
            "per_gpu": per_gpu,
            "running_gap_avg": round(max(run_avg) - min(run_avg), 2) if run_avg else None,
            "slo_pass": L["slo"]["pass"],
            "timeseries": [{"t": pt["t"],
                            **{f"gpu{i}": pt[port]["running"] for i, port in enumerate(ports) if port in pt},
                            **{f"gpu{i}_wait": pt[port]["waiting"] for i, port in enumerate(ports) if port in pt}}
                           for pt in L.get("vllm_timeseries", [])],
        })
    order = {"round_robin": 0, "least_conn": 1}
    return sorted(out, key=lambda x: order.get(x["lb"], 9))


def plot_lb(lbr, path):
    """left: TTFT p95 per method (all / short / long) · right: in-flight requests per GPU over time, one panel per method"""
    fig = plt.figure(figsize=(14, 4.8))
    gs = fig.add_gridspec(1, 1 + len(lbr), width_ratios=[1.1] + [1.4] * len(lbr))
    ax0 = fig.add_subplot(gs[0])
    groups = [("all", "ttft_p95_s"), ("short ≤150", "ttft_p95_short_s"), ("long ≤600", "ttft_p95_long_s")]
    w = 0.8 / len(lbr)
    for j, r in enumerate(lbr):
        xs = [k + (j - (len(lbr) - 1) / 2) * w for k in range(len(groups))]
        ys = [r[key] or 0 for _, key in groups]
        bars = ax0.bar(xs, ys, w * 0.92, color=LB_COLORS.get(r["lb"], FALLBACK[j]), label=r["lb_name"])
        for b, y in zip(bars, ys):
            ax0.annotate(f"{y:.2f}", (b.get_x() + b.get_width() / 2, y), textcoords="offset points",
                         xytext=(0, 3), ha="center", fontsize=8, color=INK)
    slo = 2.0
    ax0.axhline(slo, color=INK, ls="--", lw=1.2)
    ax0.text(1.0, slo * 1.12, f"SLO {slo:g} s", fontsize=8, color=INK, ha="center")
    ax0.set_xticks(range(len(groups))); ax0.set_xticklabels([g for g, _ in groups])
    ax0.set_yscale("log")
    ax0.set_ylim(0.1, max(r["ttft_p95_s"] for r in lbr) * 4)
    style(ax0, f"TTFT p95 (N={lbr[0]['users']}, log scale)", "", "seconds")
    ax0.legend(frameon=False, fontsize=9, loc="upper right")
    ymax = max((pt.get(f"gpu{i}", 0) for r in lbr for pt in r["timeseries"] for i in range(2)), default=1)
    share = None
    for j, r in enumerate(lbr):
        ax = fig.add_subplot(gs[1 + j], sharey=share); share = share or ax
        for g in r["per_gpu"]:
            i = g["gpu"]
            t = [pt["t"] for pt in r["timeseries"] if f"gpu{i}" in pt]
            y = [pt[f"gpu{i}"] for pt in r["timeseries"] if f"gpu{i}" in pt]
            ax.plot(t, y, color=GPU_COLORS[i], lw=1.8, label=f"GPU {i} running (avg {g['running_avg']:.0f})")
            wq = [pt.get(f"gpu{i}_wait", 0) for pt in r["timeseries"] if f"gpu{i}" in pt]
            if any(wq):
                ax.plot(t, wq, color=GPU_COLORS[i], lw=1.2, ls="--", label=f"GPU {i} waiting (avg {g['waiting_avg']:.0f})")
        ax.axhline(r["users"] / 2, color=MUTED, ls=":", lw=1.2)
        ax.text(1, r["users"] / 2 + ymax * 0.02, f"even split {r['users'] // 2}", fontsize=8, color=MUTED)
        ax.set_ylim(0, ymax * 1.15)
        style(ax, f"{r['lb_name']}: requests in progress per GPU", "seconds into measured window",
              "running requests" if j == 0 else "")
        ax.legend(frameon=True, framealpha=0.9, edgecolor="none", fontsize=9, loc="center right")
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def load_runs():
    runs = []
    for p in sorted(glob.glob(os.path.join(RES, "loadtest_*.json"))):
        r = json.load(open(p, encoding="utf-8"))
        if not r.get("levels") or is_lb_run(r):
            continue
        srv = r.get("server", {})
        gpus = int(srv.get("gpus", 1))
        mode = srv.get("mode", "?")
        lb = srv.get("lb", "")
        slo = r["slo"]
        levels = sorted(r["levels"], key=lambda L: L["users"])
        passed = [L for L in levels if L["slo"]["pass"]]
        cap = max(passed, key=lambda L: L["users"]) if passed else None
        arch = ("Continuous Batching" if mode == "batch" else "ทีละคำถาม (no batching)")
        if gpus > 1:
            arch += f" × {gpus} vLLM หลัง NGINX {lb}"
        runs.append({
            "label": r["label"], "file": os.path.basename(p), "gpus": gpus, "mode": mode, "lb": lb,
            "architecture": arch, "slo": slo, "stopped_reason": r.get("stopped_reason"),
            "capacity_users": cap["users"] if cap else 0,
            "capacity_level": cap,
            "peak_total_tok_s": max(L["total_tok_s"] for L in levels),
            "levels": [{
                "users": L["users"], "pass": L["slo"]["pass"],
                "ttft_p95_s": round(L["ttft_s"]["p95"], 3),
                "speed_p5_tok_s": round(L["speed_tok_s_per_user"]["p5"], 2),
                "total_tok_s": L["total_tok_s"], "error_rate": L["error_rate"],
                "requests_per_backend": L.get("requests_per_backend", {}),
                "gpu_util_pct": L.get("gpu_util_pct", {}),
            } for L in levels],
        })
    return runs


def gpu_table(runs):
    """one row per run; 'x of 1 GPU' compares with the 1-GPU run of the same mode."""
    base = {r["mode"]: r for r in runs if r["gpus"] == 1}
    rows = []
    for r in sorted(runs, key=lambda r: (r["mode"] != "single", r["gpus"])):
        b = base.get(r["mode"])
        x = r["capacity_users"] / b["capacity_users"] if b and b["capacity_users"] else None
        c = r["capacity_level"]
        rows.append({
            "gpus": r["gpus"], "architecture": r["architecture"], "label": r["label"],
            "capacity_users": r["capacity_users"],
            "total_tok_s_at_capacity": c["total_tok_s"] if c else None,
            "ttft_p95_s_at_capacity": round(c["ttft_s"]["p95"], 3) if c else None,
            "x_of_1gpu": round(x, 2) if x is not None else None,
            "efficiency_pct": round(100 * x / r["gpus"], 1) if x is not None else None,
        })
    return rows


def style(ax, title, xlabel, ylabel):
    ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="bold")
    ax.set_xlabel(xlabel, color=MUTED); ax.set_ylabel(ylabel, color=MUTED)
    ax.grid(True, color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#bdbcb5")
    ax.tick_params(colors=MUTED)


def color_of(r, i):
    return COLORS.get(r["label"], FALLBACK[i % len(FALLBACK)])


def plot_ttft(runs, path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    slo = runs[0]["slo"]
    for i, r in enumerate(runs):
        n = [L["users"] for L in r["levels"]]
        col = color_of(r, i)
        for ax, key in ((axes[0], "ttft_p95_s"), (axes[1], "speed_p5_tok_s")):
            ax.plot(n, [L[key] for L in r["levels"]], "-o", color=col, lw=2, ms=6, label=r["label"])
            if r["capacity_users"]:
                L = next(L for L in r["levels"] if L["users"] == r["capacity_users"])
                ax.plot(L["users"], L[key], marker="*", ms=17, color=col, mec="white", mew=1.5, zorder=5)
                ax.annotate(f"cap {r['capacity_users']}", (L["users"], L[key]), textcoords="offset points",
                            xytext=(6, 8), fontsize=9, color=INK)
    axes[0].axhline(slo["ttft_p95_max_s"], color=INK, ls="--", lw=1.2)
    axes[0].text(1, slo["ttft_p95_max_s"] * 1.06, f"SLO {slo['ttft_p95_max_s']:g} s", color=INK, fontsize=9)
    axes[1].axhline(slo["speed_p5_min_tok_s"], color=INK, ls="--", lw=1.2)
    axes[1].text(1, slo["speed_p5_min_tok_s"] * 1.06, f"SLO {slo['speed_p5_min_tok_s']:g} tok/s", color=INK, fontsize=9)
    for ax in axes:
        ax.set_xscale("symlog", linthresh=8); ax.set_xlim(left=0.8)
    axes[0].set_yscale("log")
    style(axes[0], "TTFT p95 vs N", "Concurrent users (N)", "TTFT p95 (s)")
    style(axes[1], "Per-user speed p5 vs N", "Concurrent users (N)", "tokens/s per user (p5)")
    axes[0].legend(frameon=False, fontsize=9)
    fig.text(0.01, 0.01, "★ = capacity (largest N passing all SLOs)", fontsize=9, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(path, dpi=150); plt.close(fig)


def plot_tput(runs, path):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for i, r in enumerate(runs):
        n = [L["users"] for L in r["levels"]]
        ax.plot(n, [L["total_tok_s"] for L in r["levels"]], "-o", color=color_of(r, i), lw=2, ms=6, label=r["label"])
        if r["capacity_users"]:
            L = next(L for L in r["levels"] if L["users"] == r["capacity_users"])
            ax.plot(L["users"], L["total_tok_s"], marker="*", ms=17, color=color_of(r, i), mec="white", mew=1.5, zorder=5)
    ax.set_xscale("symlog", linthresh=8); ax.set_xlim(left=0.8); ax.set_ylim(bottom=0)
    style(ax, "Total throughput vs N", "Concurrent users (N)", "Total tokens/s")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def plot_capacity(runs, path):
    batch = sorted([r for r in runs if r["mode"] == "batch"], key=lambda r: r["gpus"])
    fig, ax = plt.subplots(figsize=(7, 4.6))
    if batch:
        c1 = next((r["capacity_users"] for r in batch if r["gpus"] == 1), None)
        g = [r["gpus"] for r in batch]; c = [r["capacity_users"] for r in batch]
        if c1:
            gx = list(range(1, max(g) + 1))
            ax.plot(gx, [c1 * k for k in gx], "--", color=MUTED, lw=1.5, label="ideal (linear)")
        ax.plot(g, c, "-o", color=COLORS["batch_1gpu"], lw=2, ms=9, label="measured (batching)")
        for x, y in zip(g, c):
            ax.annotate(f"{y}", (x, y), textcoords="offset points", xytext=(8, -4), fontsize=10, color=INK)
        ax.set_xticks(range(1, max(g) + 1))
    ax.set_ylim(bottom=0); ax.set_xlim(0.7, (max(r["gpus"] for r in batch) if batch else 1) + 0.3)
    style(ax, "Capacity vs GPUs", "GPUs", "Users passing SLO (N)")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def main():
    runs = load_runs()
    if not runs:
        sys.exit(f"no loadtest_*.json in {RES}")
    table = gpu_table(runs)
    out = {
        "results_dir": RES,
        "capacity": {r["label"]: {k: r[k] for k in ("gpus", "mode", "lb", "architecture", "capacity_users",
                                                      "peak_total_tok_s", "stopped_reason", "levels")} for r in runs},
        "table_by_gpu": table,
        "slo": runs[0]["slo"],
        "charts": ["ttft_p95_vs_n.png", "throughput_vs_n.png", "capacity_vs_gpus.png"],
    }
    json.dump(out, open(os.path.join(RES, "metrics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    plot_ttft(runs, os.path.join(RES, "ttft_p95_vs_n.png"))
    plot_tput(runs, os.path.join(RES, "throughput_vs_n.png"))
    plot_capacity(runs, os.path.join(RES, "capacity_vs_gpus.png"))
    print(f"{'GPU':>3} {'architecture':<45} {'N':>5} {'tok/s':>8} {'TTFTp95':>8} {'x1GPU':>6} {'eff%':>6}")
    for t in table:
        print(f"{t['gpus']:>3} {t['label']:<45} {t['capacity_users']:>5} {t['total_tok_s_at_capacity'] or 0:>8.0f} "
              f"{t['ttft_p95_s_at_capacity'] or 0:>8.2f} {t['x_of_1gpu'] or 0:>6.2f} {t['efficiency_pct'] or 0:>6.1f}")
    print("wrote", os.path.join(RES, "metrics.json"), "+ 3 charts")
    lbr = load_lb_runs()
    if lbr:
        m = json.load(open(os.path.join(RES, "metrics.json"), encoding="utf-8"))
        m["lb_compare"] = [{k: v for k, v in r.items() if k != "timeseries"} for r in lbr]
        m["charts"].append("lb_compare.png")
        json.dump(m, open(os.path.join(RES, "metrics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        plot_lb(lbr, os.path.join(RES, "lb_compare.png"))
        print(f"\n{'LB':<12} {'N':>4} {'TTFTp95':>8} {'spd p5':>7} {'tok/s':>7} {'GPU0 run avg/max':>17} {'GPU1 run avg/max':>17} {'wait avg':>8}")
        for r in lbr:
            g = r["per_gpu"]
            print(f"{r['lb_name']:<12} {r['users']:>4} {r['ttft_p95_s']:>8.2f} {r['speed_p5_tok_s']:>7.1f} {r['total_tok_s']:>7.0f} "
                  f"{g[0]['running_avg']:>9.1f}/{g[0]['running_max']:<7.0f} {g[1]['running_avg']:>9.1f}/{g[1]['running_max']:<7.0f} "
                  f"{sum(x['waiting_avg'] or 0 for x in g):>8.1f}")
        print("wrote lb_compare (metrics.json) + lb_compare.png")


if __name__ == "__main__":
    main()
