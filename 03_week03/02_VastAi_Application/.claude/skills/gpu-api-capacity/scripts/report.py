#!/usr/bin/env python3
"""LAB 5 report: read every result file, write metrics.json and PNG charts.

usage: python report.py [results_dir]   (default: ../results next to this file)

skill v0: works with any subset of runs (e.g. only base1 + gpu2). Missing runs are skipped,
charts that need them are not drawn. SLO is read from the result files (loadgen --slo-p95/--slo-err).
"""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "results"))

LADDER = ["base1", "batch1", "gpu1", "gpu2"]
LB = ["lc2", "rr_slow", "lc_slow"]
FAILOVER = ["fo_noretry", "fo_retry"]
LABEL = {
    "base1": "1 GPU · one request at a time",
    "batch1": "1 GPU · micro-batching",
    "gpu1": "1 GPU · micro-batching + 4 proc",
    "gpu2": "2 GPU · micro-batching + 4 proc",
    "lc2": "2 GPU · least_conn",
    "rr_slow": "2 GPU · round-robin · 1 slow",
    "lc_slow": "2 GPU · least_conn · 1 slow",
}
GPUS = {"base1": 1, "batch1": 1, "gpu1": 1, "gpu2": 2, "lc2": 2, "rr_slow": 2, "lc_slow": 2}
COLOR = {"base1": "#9aa0a6", "batch1": "#f29900", "gpu1": "#1a73e8", "gpu2": "#188038",
         "lc2": "#a142f4", "rr_slow": "#d93025", "lc_slow": "#a142f4"}
SLO_MS = 500.0
SLO_ERR = 0.01

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})


def load(name):
    p = os.path.join(RES, f"{name}.json")
    if not os.path.exists(p):
        raise SystemExit(f"missing result file: {p}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def have(name):
    return os.path.exists(os.path.join(RES, f"{name}.json"))


def passes(r):
    return r["latency_ms"]["p95"] <= SLO_MS and r["error_rate"] < SLO_ERR


def replica_share(r):
    g = {}
    for k, v in r["per_replica"].items():
        rep = k.split("-")[0]
        g[rep] = g.get(rep, 0) + v
    tot = sum(g.values()) or 1
    return {k: round(v / tot * 100, 1) for k, v in sorted(g.items())}


def ladder_summary(name):
    d = load(name)
    points = sorted(d["levels"] + d.get("bisect", []), key=lambda r: r["users"])
    # re-check runs (same N run again) — file name pattern <name>_recheck*.json
    rechecks = {}
    for p in glob.glob(os.path.join(RES, f"{name}_recheck*.json")):
        with open(p, encoding="utf-8") as f:
            for r in json.load(f):
                rechecks.setdefault(r["users"], []).append(r)

    strict = d.get("capacity_users")

    def ok_at(r):
        if passes(r):
            return True
        rc = rechecks.get(r["users"], [])
        return bool(rc) and sum(passes(x) for x in rc) > len(rc) / 2

    effective = 0
    for r in points:
        if ok_at(r):
            effective = r["users"]
        else:
            break
    at_cap = next((r for r in points if r["users"] == effective), None)
    best = max(points, key=lambda r: r["throughput_rps"])
    out = {
        "label": LABEL[name], "gpus": GPUS[name],
        "cluster_conf": dict(l.split("=", 1) for l in d["cluster_conf"].strip().splitlines() if "=" in l),
        "capacity_users_strict": strict,
        "capacity_users": effective,
        "max_throughput_rps": best["throughput_rps"], "max_throughput_at_users": best["users"],
        "points": [{"users": r["users"], "pass": passes(r), "throughput_rps": r["throughput_rps"],
                    "p50_ms": r["latency_ms"]["p50"], "p95_ms": r["latency_ms"]["p95"],
                    "p99_ms": r["latency_ms"]["p99"], "error_rate": r["error_rate"],
                    "gpu_util_pct": r["gpu_util_pct"], "cpu_cores": r["cpu_cores"],
                    "batch_mean": r["batch_mean"], "replica_share_pct": replica_share(r)} for r in points],
    }
    if rechecks:
        out["rechecks"] = {str(n): [{"p95_ms": x["latency_ms"]["p95"], "throughput_rps": x["throughput_rps"],
                                     "pass": passes(x)} for x in v] for n, v in rechecks.items()}
        out["note"] = ("strict rule stopped at the first failing N; that N was re-run and passed "
                       "(majority), so capacity_users continues past it")
    if at_cap:
        out["at_capacity"] = {"throughput_rps": at_cap["throughput_rps"], "p95_ms": at_cap["latency_ms"]["p95"],
                              "gpu_util_pct": at_cap["gpu_util_pct"], "cpu_cores": at_cap["cpu_cores"],
                              "batch_mean": at_cap["batch_mean"], "replica_share_pct": replica_share(at_cap)}
    return out


def failover_summary(name):
    d = load(name)
    return {"users": d["users"], "duration_s": d["duration_s"],
            "events": [{"at_s": e["at_s"], "cmd": e["cmd"], "took_s": round(e["finished_s"] - e["started_s"], 1)}
                       for e in d["events"]],
            "requests_total": d["requests_total"], "ok_total": d["ok_total"], "errors_total": d["errors_total"],
            "error_rate": round(d["errors_total"] / max(d["requests_total"], 1), 4),
            "error_kinds": d["error_kinds_total"], "phases": d["phases"], "track": d["track"],
            "worst_second_p95": d["worst_second_p95"], "per_second": d["per_second"]}


def main():
    global SLO_MS, SLO_ERR
    present = [n for n in LADDER + LB if have(n)]
    if not present:
        raise SystemExit(f"no ladder result files in {RES}")
    slo = load(present[0]).get("slo", {})
    SLO_MS = slo.get("p95_ms", SLO_MS)
    SLO_ERR = slo.get("error_rate_lt", SLO_ERR)
    m = {"slo": {"p95_ms": SLO_MS, "error_rate_lt": SLO_ERR}, "runs": {}, "failover": {}}
    for n in present:
        m["runs"][n] = ladder_summary(n)
    for n in FAILOVER:
        if have(n):
            m["failover"][n] = failover_summary(n)

    R = m["runs"]
    ladder = [n for n in LADDER if n in R]
    one_gpu = [n for n in ladder if GPUS[n] == 1]
    # reference "1 GPU" row: gpu1 (same architecture as gpu2) if measured, else the best 1-GPU run
    ref = "gpu1" if "gpu1" in R else (max(one_gpu, key=lambda n: R[n]["capacity_users"]) if one_gpu else None)
    m["reference_1gpu_run"] = ref
    base = R[ref] if ref else None
    rows = []
    for n in ladder:
        r = R[n]
        if not base:
            continue
        x_cap = r["capacity_users"] / base["capacity_users"]
        x_thr = r["max_throughput_rps"] / base["max_throughput_rps"]
        rows.append({"run": n, "gpus": r["gpus"], "label": r["label"],
                     "capacity_users": r["capacity_users"], "capacity_users_strict": r["capacity_users_strict"],
                     "max_throughput_rps": r["max_throughput_rps"],
                     "p95_at_capacity_ms": r.get("at_capacity", {}).get("p95_ms"),
                     "x_vs_1gpu_capacity": round(x_cap, 2), "x_vs_1gpu_throughput": round(x_thr, 2),
                     "efficiency_capacity": round(x_cap / r["gpus"], 3),
                     "efficiency_throughput": round(x_thr / r["gpus"], 3),
                     "x_vs_base1_capacity": (round(r["capacity_users"] / R["base1"]["capacity_users"], 2)
                                             if "base1" in R and R["base1"]["capacity_users"] else None)})
    m["scaling"] = rows
    g2 = next((r for r in rows if r["run"] == "gpu2"), None)
    if ref != "gpu1":
        m["scaling_note"] = (f"gpu1 not measured: x_vs_1gpu / efficiency use {ref} (different architecture), "
                             "so they mix the effect of the architecture and of the 2nd GPU · no 3-GPU estimate")
    if g2 and ref == "gpu1" and R["gpu2"].get("at_capacity"):
        eff_c, eff_t = g2["efficiency_capacity"], g2["efficiency_throughput"]
        m["estimate_3gpu"] = {
            "note": "calculation, not measured: 1-GPU value x 3 x 2-GPU efficiency",
            "capacity_users": round(base["capacity_users"] * 3 * eff_c),
            "max_throughput_rps": round(base["max_throughput_rps"] * 3 * eff_t, 1),
            "server_cpu_cores_needed_approx": round(R["gpu2"]["at_capacity"]["cpu_cores"]["server"] / 2 * 3, 1),
        }
    with open(os.path.join(RES, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)

    charts = [chart_latency(R), chart_throughput(R)]
    if g2 and ref and "estimate_3gpu" in m:
        charts.append(chart_scaling(R, rows, m["estimate_3gpu"], ref))
    if all(n in R for n in ["gpu2", "lc2", "rr_slow", "lc_slow"]):
        charts.append(chart_lb(R))
    if all(n in m["failover"] for n in FAILOVER):
        charts.append(chart_failover(m["failover"]))
    print("metrics.json +", ", ".join(charts))
    for r in rows:
        print(f"{r['run']:7s} GPU={r['gpus']} cap={r['capacity_users']:4d} (strict {r['capacity_users_strict']}) "
              f"thr_max={r['max_throughput_rps']:7.1f} p95@cap={r['p95_at_capacity_ms']} "
              f"x1gpu={r['x_vs_1gpu_capacity']} eff={r['efficiency_capacity']}")
    print("3 GPU estimate:", m.get("estimate_3gpu", "(not computed: needs gpu1 + gpu2)"))
    print("DONE")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(RES, name), bbox_inches="tight")
    plt.close(fig)
    return name


def chart_latency(R):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for n in [x for x in LADDER if x in R]:
        r = R[n]
        xs = [p["users"] for p in r["points"]]
        ys = [p["p95_ms"] for p in r["points"]]
        ax.plot(xs, ys, "o-", color=COLOR[n], label=f"{r['label']} (cap {r['capacity_users']})", ms=4)
        cap = r.get("at_capacity")
        if cap:
            ax.plot(r["capacity_users"], cap["p95_ms"], "*", color=COLOR[n], ms=17, mec="black", zorder=5)
            ax.annotate(f"N={r['capacity_users']}", (r["capacity_users"], cap["p95_ms"]), textcoords="offset points",
                        xytext=(6, -14), fontsize=9, color=COLOR[n], fontweight="bold")
        for nn, rc in r.get("rechecks", {}).items():
            ax.plot([int(nn)] * len(rc), [x["p95_ms"] for x in rc], "o", mfc="white", mec=COLOR[n], ms=6)
            spike = next(p for p in r["points"] if p["users"] == int(nn))
            ax.annotate("one-off spike,\nre-run x3 passed", (int(nn), spike["p95_ms"]), textcoords="offset points",
                        xytext=(8, 4), fontsize=8, color=COLOR[n])
    ax.axhline(SLO_MS, color="#d93025", ls="--", lw=1.4)
    ax.text(1.05, SLO_MS * 1.06, f"SLO p95 = {SLO_MS:.0f} ms", color="#d93025", fontsize=9)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("Concurrent users N")
    ax.set_ylabel("Latency p95 (ms, log)")
    ax.set_title("Latency p95 vs concurrent users  (star = capacity)")
    ax.legend(fontsize=9, loc="upper left")
    return save(fig, "latency_p95_vs_users.png")


def chart_throughput(R):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for n in [x for x in LADDER if x in R]:
        r = R[n]
        pts = [p for p in r["points"]]
        ax.plot([p["users"] for p in pts], [p["throughput_rps"] for p in pts], "o-", color=COLOR[n],
                label=f"{r['label']} (max {r['max_throughput_rps']:.0f} req/s)", ms=4)
        cap = r.get("at_capacity")
        if cap:
            ax.plot(r["capacity_users"], cap["throughput_rps"], "*", color=COLOR[n], ms=17, mec="black", zorder=5)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Concurrent users N")
    ax.set_ylabel("Throughput (req/s)")
    ax.set_title("Throughput vs concurrent users  (star = capacity)")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_ylim(bottom=0)
    return save(fig, "throughput_vs_users.png")


def chart_scaling(R, rows, est, ref="gpu1"):
    g1 = next(r for r in rows if r["run"] == ref)
    g2 = next(r for r in rows if r["run"] == "gpu2")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, key, eff_key, title, unit in [
            (axes[0], "capacity_users", "efficiency_capacity", "Capacity (users at SLO)", "users"),
            (axes[1], "max_throughput_rps", "efficiency_throughput", "Max throughput", "req/s")]:
        v1, v2 = g1[key], g2[key]
        v3 = est[key]
        ax.plot([0, 1, 2, 3], [0, v1, 2 * v1, 3 * v1], "--", color="#9aa0a6", label="ideal (linear)")
        ax.plot([1, 2], [v1, v2], "o-", color="#188038", lw=2.2, ms=9, label="measured")
        ax.plot([2, 3], [v2, v3], ":", color="#188038")
        ax.plot(3, v3, "o", mfc="white", mec="#188038", ms=9, label="3 GPU estimate (calc.)")
        ax.annotate(f"{v1:.0f}", (1, v1), xytext=(-28, 6), textcoords="offset points")
        ax.annotate(f"{v2:.0f}\nx{v2 / v1:.2f} · eff {g2[eff_key] * 100:.0f}%", (2, v2),
                    xytext=(8, -26), textcoords="offset points", color="#188038", fontweight="bold")
        ax.annotate(f"~{v3:.0f}", (3, v3), xytext=(-34, 6), textcoords="offset points", color="#188038")
        ax.set_xticks([1, 2, 3])
        ax.set_xlim(0.5, 3.4)
        ax.set_ylim(0, 3.3 * v1)
        ax.set_xlabel("Number of GPUs")
        ax.set_ylabel(unit)
        ax.set_title(title)
        ax.legend(fontsize=8, loc="upper left")
    fig.suptitle(f"Scaling 1 -> 2 GPU (1 GPU = {R[ref]['label']} · 2 GPU = {R['gpu2']['label']})",
                 fontweight="bold")
    return save(fig, "scaling_vs_gpus.png")


def chart_lb(R):
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5), gridspec_kw={"height_ratios": [1.3, 1]})
    pairs = [("Equal replicas", "gpu2", "lc2"), ("Replica 2 slower (+40 ms/image)", "rr_slow", "lc_slow")]
    for col, (title, rr, lc) in enumerate(pairs):
        ax = axes[0][col]
        for n, c, lab in [(rr, "#d93025", "round-robin"), (lc, "#a142f4", "least_conn")]:
            r = R[n]
            ax.plot([p["users"] for p in r["points"]], [p["p95_ms"] for p in r["points"]], "o-", color=c, ms=4,
                    label=f"{lab} (cap {r['capacity_users']})")
            if r.get("at_capacity"):
                ax.plot(r["capacity_users"], r["at_capacity"]["p95_ms"], "*", color=c, ms=16, mec="black", zorder=5)
        ax.axhline(SLO_MS, color="#d93025", ls="--", lw=1.2)
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xlabel("Concurrent users N")
        ax.set_ylabel("Latency p95 (ms, log)")
        ax.set_title(title)
        ax.legend(fontsize=9, loc="upper left")
        # bottom: capacity bars + request share of each replica at capacity
        ax = axes[1][col]
        names = [rr, lc]
        caps = [R[n]["capacity_users"] for n in names]
        bars = ax.bar(["round-robin", "least_conn"], caps, color=["#d93025", "#a142f4"], width=0.5)
        for b, n in zip(bars, names):
            sh = R[n]["at_capacity"]["replica_share_pct"]
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                    f"{b.get_height():.0f} users\nGPU0 {sh.get('gpu0', 0):.0f}% / GPU1 {sh.get('gpu1', 0):.0f}%",
                    ha="center", va="bottom", fontsize=9)
        ax.set_ylim(0, max(caps) * 1.35)
        ax.set_ylabel("Capacity (users at SLO)")
        ax.set_title("Capacity + request share per replica")
    fig.suptitle("Load balancing: round-robin vs least_conn (2 GPU)", fontweight="bold")
    return save(fig, "lb_rr_vs_least_conn.png")


def chart_failover(F):
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
    for ax, (n, title) in zip(axes, [("fo_noretry", "NGINX retry OFF"), ("fo_retry", "NGINX retry ON")]):
        f = F[n]
        ps = f["per_second"]
        t = [p["t"] for p in ps]
        g0 = [p["ok_by_replica"].get("gpu0", 0) for p in ps]
        g1 = [p["ok_by_replica"].get("gpu1", 0) for p in ps]
        er = [p["errors"] for p in ps]
        ax.bar(t, g0, color="#1a73e8", label="OK · replica GPU0", width=0.85)
        ax.bar(t, g1, bottom=g0, color="#188038", label="OK · replica GPU1", width=0.85)
        ax.bar(t, er, bottom=[a + b for a, b in zip(g0, g1)], color="#d93025", label="error", width=0.85)
        for e in f["events"]:
            kill = "kill" in e["cmd"]
            ax.axvline(e["at_s"] - 0.5, color="black", ls="--" if kill else ":", lw=1.2)
        ymax = max(a + b + c for a, b, c in zip(g0, g1, er)) * 1.25
        ax.set_ylim(0, ymax)
        ax.text(14.7, ymax * 0.93, "GPU1 killed", ha="right", fontsize=9)
        restart = next(e for e in f["events"] if "start" in e["cmd"])
        ax.text(29.7, ymax * 0.93, f"restart cmd (ready after {restart['took_s']:.0f} s)", ha="left", fontsize=9)
        ax.set_ylabel("Requests per second")
        ax.set_title(f"{title}: {f['errors_total']} errors / {f['requests_total']} requests "
                     f"({f['error_rate'] * 100:.1f}%) · N={f['users']}")
        ax.legend(fontsize=8, loc="upper right", ncol=3, bbox_to_anchor=(1, 0.88))
    axes[1].set_xlabel("Time (s)")
    fig.suptitle("Replica failure during load (2 GPU, round-robin)", fontweight="bold")
    return save(fig, "failover_timeline.png")


if __name__ == "__main__":
    main()
