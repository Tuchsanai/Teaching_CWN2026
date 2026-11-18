#!/usr/bin/env python3
"""report.py — สรุปผล LAB 6 จากทุกชุดในโฟลเดอร์ results/

อ่าน   results/loadtest_*.json  (ผลยิงโหลดแต่ละชุด)  และ  results/precheck_*.json|txt  (ผลตรวจ GPU ก่อนวัด)
สร้าง  results/metrics.json  และกราฟ 4 รูปในโฟลเดอร์เดียวกัน
  - ttft_p95_vs_n.png       TTFT p95 เทียบ N + เส้น SLO + จุดความจุ
  - speed_p5_vs_n.png       ความเร็วต่อผู้ใช้ p5 เทียบ N + เส้น SLO (เกณฑ์ที่ทำให้ Continuous Batching ไม่ผ่าน)
  - throughput_vs_n.png     token/วินาทีรวมเทียบ N
  - capacity_vs_gpus.png    ความจุเทียบจำนวน GPU + เส้น ideal
และถ้ามี results/loadtest_mix_*.json (คำถามยาว 20% · เทียบวิธีกระจายงานของ NGINX) สร้างเพิ่ม
  - lb_ttft_p95.png         TTFT p95 (รวม / คำถามสั้น / คำถามยาว) round robin เทียบ least_conn
  - lb_running_per_gpu.png  จำนวนคำถามที่ GPU แต่ละใบกำลังทำ ทุกวินาที ของทั้ง 2 วิธี
  และหัวข้อ "lb_compare" ใน metrics.json

กติกาความจุ: ระดับ N สูงสุดที่ผ่าน SLO และทุกระดับที่ต่ำกว่า (ที่วัด) ก็ผ่าน · ระดับที่วัดซ้ำใช้ค่ากลาง (median)
SLO: TTFT p95 ≤ 2 s · ความเร็วต่อผู้ใช้ p5 ≥ 15 token/s · error < 1%

ใช้:  python code/report.py [--results lab6_llm_chat/results]
"""
import argparse, glob, json, os, re, statistics, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SLO = {"ttft_p95_max_s": 2.0, "speed_p5_min_tok_s": 15.0, "error_rate_max": 0.01}
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]   # สีตามชุด เรียงตายตัว
INK, MUTED, GRID = "#2b2b2b", "#6b6b6b", "#e4e2dc"
MEDIAN_KEYS = ["ttft_p50", "ttft_p95", "ttft_p99", "speed_p50", "speed_p5", "agg_tok_s", "error_rate"]


# ---------------- อ่านผล ----------------
def arch_of(server):
    gpus, mode, lb = int(server.get("GPUS", 1)), server.get("MODE", "batch"), server.get("LB", "least_conn")
    th = {"batch": "Continuous Batching", "single": "ตอบทีละคำถาม"}.get(mode, mode)
    en = {"batch": "Continuous Batching", "single": "one request at a time"}.get(mode, mode)
    if gpus > 1:
        th += f" · vLLM {gpus} ตัว หลัง NGINX {lb}"
        en += f" ({gpus} vLLM, NGINX {lb})"
    return gpus, mode, lb, th, en


def judge(m):
    return (m.get("ttft_p95") is not None and m["ttft_p95"] <= SLO["ttft_p95_max_s"]
            and m.get("speed_p5") is not None and m["speed_p5"] >= SLO["speed_p5_min_tok_s"]
            and m["error_rate"] < SLO["error_rate_max"])


def final_of(level):
    """ค่าที่ใช้ตัดสิน: วัดครั้งเดียวใช้ค่านั้น · วัดซ้ำใช้ median ของทุกครั้ง (คำนวณใหม่จาก runs)"""
    runs = level["runs"]
    if len(runs) == 1:
        return dict(runs[0])
    m = dict(runs[0])
    for k in MEDIAN_KEYS:
        vals = [r[k] for r in runs if r.get(k) is not None]
        m[k] = round(statistics.median(vals), 4) if vals else None
    return m


def capacity(levels):
    cap, cap_level = 0, None
    for L in sorted(levels, key=lambda x: x["N"]):
        if not L["pass"]:
            break
        cap, cap_level = L["N"], L
    return cap, cap_level


def load_set(path):
    d = json.load(open(path, encoding="utf-8"))
    gpus, mode, lb, th, en = arch_of(d.get("server", {}))
    levels = []
    for L in d["levels"]:
        f = final_of(L)
        ok = judge(f)
        row = {"N": L["N"], "pass": ok, "repeated": len(L["runs"]) > 1, "n_runs": len(L["runs"]),
               "borderline": L.get("borderline", []),
               "ttft_p50": f["ttft_p50"], "ttft_p95": f["ttft_p95"], "ttft_p99": f["ttft_p99"],
               "speed_p50": f["speed_p50"], "speed_p5": f["speed_p5"], "agg_tok_s": f["agg_tok_s"],
               "error_rate": f["error_rate"], "requests": f["requests"],
               "requests_per_backend": L["runs"][0].get("requests_per_backend"),
               "gpu": L["runs"][0].get("gpu"), "loadgen_cpu_pct_total": f.get("loadgen_cpu_pct_total"),
               "fail_reasons": [k for k, bad in (
                   ("ttft_p95", f["ttft_p95"] is None or f["ttft_p95"] > SLO["ttft_p95_max_s"]),
                   ("speed_p5", f["speed_p5"] is None or f["speed_p5"] < SLO["speed_p5_min_tok_s"]),
                   ("error", f["error_rate"] >= SLO["error_rate_max"])) if bad]}
        if row["repeated"]:
            row["runs"] = [{k: r.get(k) for k in ["ttft_p50", "ttft_p95", "speed_p5", "speed_p50", "agg_tok_s",
                                                  "error_rate", "requests"]} for r in L["runs"]]
        levels.append(row)
    cap, cap_level = capacity(levels)
    label = d.get("label") or os.path.basename(path)[9:-5]
    return {"label": label, "file": os.path.basename(path), "gpus": gpus, "mode": mode, "lb": lb,
            "architecture": th, "architecture_en": en, "started": d.get("started"), "config": d.get("config"),
            "levels_measured": [L["N"] for L in levels], "capacity_users": cap,
            "capacity_agg_tok_s": cap_level["agg_tok_s"] if cap_level else None,
            "capacity_ttft_p95": cap_level["ttft_p95"] if cap_level else None,
            "capacity_speed_p5": cap_level["speed_p5"] if cap_level else None,
            "max_agg_tok_s": max((L["agg_tok_s"] or 0) for L in levels),
            "first_fail_N": next((L["N"] for L in sorted(levels, key=lambda x: x["N"]) if not L["pass"]), None),
            "repeated_levels": [L["N"] for L in levels if L["repeated"]], "levels": levels}


def load_prechecks(res):
    out = {}
    for p in sorted(glob.glob(os.path.join(res, "precheck_*.json"))):
        out[os.path.basename(p)[9:-5]] = json.load(open(p, encoding="utf-8"))
    for p in sorted(glob.glob(os.path.join(res, "precheck_*.txt"))):   # ชุดเก่าที่เก็บเป็นข้อความ
        key = os.path.basename(p)[9:-4]
        if key in out:
            continue
        txt = open(p, encoding="utf-8").read()
        idle = re.search(r"idle GPU(\d).*?:\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)", txt)
        load = re.search(r"temp max ([\d.]+) C, clock avg ([\d.]+) MHz", txt)
        speeds = [float(x) for x in re.findall(r"speed=([\d.]+)", txt)]
        g = {"gpu_index": int(idle.group(1)) if idle else 0}
        if idle:
            g["idle"] = {"temp_c": float(idle.group(2)), "clock_mhz": float(idle.group(3)),
                         "clock_max_mhz": float(idle.group(4))}
        if load:
            g["load"] = {"temp_max_c": float(load.group(1)), "clock_mhz_mean": float(load.group(2))}
        if speeds:
            g["single_user"] = {"speed_tok_s_median": statistics.median(speeds)}
        out[key] = {"source": os.path.basename(p), "gpus": [g]}
    return out


# ---------------- กราฟ ----------------
def style(ax, title, xlabel, ylabel):
    ax.set_title(title, loc="left", fontsize=12, color=INK, pad=10)
    ax.set_xlabel(xlabel, color=MUTED); ax.set_ylabel(ylabel, color=MUTED)
    ax.grid(True, color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED)


def plot_vs_n(sets, key, path, title, ylabel, slo=None, slo_label=None, mark_cap=True, logx=True,
              cap_offsets=None, slo_left=False, legend_loc="best"):
    """cap_offsets = {label ของชุด: (dx, dy, ha)} ขยับป้ายความจุไม่ให้ทับกัน"""
    cap_offsets = cap_offsets or {}
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)
    for i, s in enumerate(sets):
        c = COLORS[i % len(COLORS)]
        xs = [L["N"] for L in s["levels"]]; ys = [L[key] for L in s["levels"]]
        ax.plot(xs, ys, color=c, linewidth=2, marker="o", markersize=5, label=s["architecture_en"])
        rx = [L["N"] for L in s["levels"] if L["repeated"]]; ry = [L[key] for L in s["levels"] if L["repeated"]]
        if rx:
            ax.scatter(rx, ry, s=90, facecolors="none", edgecolors=c, linewidths=1.5, zorder=4)
        if mark_cap and s["capacity_users"]:
            cy = next(L[key] for L in s["levels"] if L["N"] == s["capacity_users"])
            ax.scatter([s["capacity_users"]], [cy], marker="*", s=260, color=c, edgecolors="white", linewidths=1.2, zorder=5)
            dx, dy, ha = cap_offsets.get(s["label"], (6, 8, "left"))
            ax.annotate(f"capacity {s['capacity_users']}", (s["capacity_users"], cy), textcoords="offset points",
                        xytext=(dx, dy), ha=ha, fontsize=9, color=INK)
    if slo is not None:
        ax.axhline(slo, color=MUTED, linestyle="--", linewidth=1.2)
        ax.annotate(slo_label, (0 if slo_left else 1, slo), xycoords=("axes fraction", "data"),
                    xytext=(4 if slo_left else -4, 4), textcoords="offset points",
                    ha="left" if slo_left else "right", fontsize=9, color=MUTED)
    if logx:
        ax.set_xscale("log", base=2)
        ticks = sorted({L["N"] for s in sets for L in s["levels"]})
        ticks = [t for t in ticks if t in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512) or t == ticks[-1]]
        ax.set_xticks(ticks); ax.set_xticklabels([str(t) for t in ticks])
    style(ax, title, "Concurrent users N", ylabel)
    h, l = ax.get_legend_handles_labels()
    h += [plt.Line2D([], [], marker="*", color=MUTED, linestyle="", markersize=12),
          plt.Line2D([], [], marker="o", markerfacecolor="none", color=MUTED, linestyle="", markersize=9)]
    l += ["capacity (SLO pass)", "repeated (median)"]
    ax.legend(h, l, frameon=False, fontsize=8.5, loc=legend_loc)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def plot_capacity(table, est3, path):
    rows = [r for r in table if r["mode"] == "batch"]
    if not rows:
        return
    base = next(r for r in rows if r["gpus"] == 1)["capacity_users"]
    gmax = max(3, max(r["gpus"] for r in rows))
    fig, ax = plt.subplots(figsize=(7, 4.8), dpi=150)
    gx = list(range(0, gmax + 1))
    ax.plot(gx, [base * g for g in gx], color=MUTED, linestyle="--", linewidth=1.5, label=f"ideal ({base} x GPUs)")
    xs = [r["gpus"] for r in rows]; ys = [r["capacity_users"] for r in rows]
    ax.plot(xs, ys, color=COLORS[0], linewidth=2, marker="o", markersize=8, label="measured")
    for r in rows:
        ax.annotate(f"{r['capacity_users']} ({r['speedup_vs_1gpu']:.2f}x)", (r["gpus"], r["capacity_users"]),
                    textcoords="offset points", xytext=(-10, 10), ha="right", fontsize=9, color=INK)
    if est3:
        ax.plot([rows[-1]["gpus"], 3], [rows[-1]["capacity_users"], est3["users"]], color=COLORS[0],
                linestyle=":", linewidth=1.5)
        ax.scatter([3], [est3["users"]], s=70, facecolors="white", edgecolors=COLORS[0], linewidths=1.8, zorder=4,
                   label="estimate (not measured)")
        ax.annotate(f"~{est3['users']} (est.)", (3, est3["users"]), textcoords="offset points", xytext=(-10, 10),
                    ha="right", fontsize=9, color=INK)
    ax.set_xticks(gx); ax.set_xlim(0, gmax + 0.3); ax.set_ylim(0, base * gmax * 1.12)
    style(ax, "Capacity vs number of GPUs (Continuous Batching)", "GPUs", "Concurrent users within SLO")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


# ---------------- เทียบวิธีกระจายงาน (คำถามยาว 20%) ----------------
LB_NAME = {"round_robin": "Round Robin", "least_conn": "least_conn"}
GPU_OF_PORT = {"8001": "GPU 0", "8002": "GPU 1"}


def load_lb_compare(res):
    rows = []
    for p in sorted(glob.glob(os.path.join(res, "loadtest_mix_*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        lb = d.get("server", {}).get("LB") or d["label"].replace("mix_", "")
        f = d["levels"][0]["runs"][0]
        q = f.get("queue", {})
        per_gpu = {GPU_OF_PORT.get(port, port): {"running_mean": v["running_mean"], "running_max": v["running_max"],
                                                  "waiting_mean": v["waiting_mean"], "waiting_max": v["waiting_max"]}
                   for port, v in sorted(q.items())}
        bk = f.get("by_kind", {})
        rows.append({"lb": lb, "name": LB_NAME.get(lb, lb), "file": os.path.basename(p), "users": f["N"],
                     "long_frac": d["config"].get("long_frac"), "long_max_tokens": d["config"].get("long_max_tokens"),
                     "short_max_tokens": d["config"].get("max_tokens"),
                     "measure_s": f["measure_window_s"], "warmup_s": d["config"].get("warmup_s"),
                     "requests": f["requests"], "error_rate": f["error_rate"],
                     "ttft_p50": f["ttft_p50"], "ttft_p95": f["ttft_p95"], "ttft_p99": f["ttft_p99"],
                     "speed_p5": f["speed_p5"], "speed_p50": f["speed_p50"], "agg_tok_s": f["agg_tok_s"],
                     "pass_slo": judge(f), "per_gpu": per_gpu,
                     "requests_per_backend": f.get("requests_per_backend"),
                     "gpu_util": {GPU_OF_PORT.get(str(8001 + int(i)), i): g["util_mean"]
                                  for i, g in (f.get("gpu") or {}).items()},
                     "short": bk.get("short"), "long": bk.get("long"),
                     "timeseries": f.get("timeseries", [])})
    rows.sort(key=lambda r: 0 if r["lb"] == "round_robin" else 1)
    return rows


def plot_lb_ttft(rows, path):
    groups = [("all", "All requests", lambda r: r["ttft_p95"]),
              ("short", "Short (<=150 tok)", lambda r: (r["short"] or {}).get("ttft_p95")),
              ("long", "Long (<=600 tok)", lambda r: (r["long"] or {}).get("ttft_p95"))]
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)
    w = 0.36
    for i, r in enumerate(rows):
        xs = [g + (i - 0.5) * w for g in range(len(groups))]
        ys = [fn(r) or 0 for _, _, fn in groups]
        ax.bar(xs, ys, width=w * 0.92, color=COLORS[i], label=f"{r['name']} ({r['users']} users)")
        for x, y in zip(xs, ys):
            ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=9,
                        color=INK)
    ax.axhline(SLO["ttft_p95_max_s"], color=MUTED, linestyle="--", linewidth=1.2)
    ax.annotate("SLO 2 s", (1, SLO["ttft_p95_max_s"]), xycoords=("axes fraction", "data"), xytext=(-4, 4),
                textcoords="offset points", ha="right", fontsize=9, color=MUTED)
    ax.set_xticks(range(len(groups))); ax.set_xticklabels([g[1] for g in groups])
    ax.set_ylim(0, max(SLO["ttft_p95_max_s"], max((fn(r) or 0) for r in rows for _, _, fn in groups)) * 1.18)
    style(ax, "TTFT p95: Round Robin vs least_conn (20% long answers)", "", "TTFT p95 (s)")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def plot_lb_running(rows, path):
    fig, axes = plt.subplots(len(rows), 1, figsize=(8, 2.9 * len(rows) + 0.4), dpi=150, sharex=True, sharey=True)
    if len(rows) == 1:
        axes = [axes]
    gcol = {"GPU 0": COLORS[0], "GPU 1": COLORS[1]}
    for ax, r in zip(axes, rows):
        for port, gname in GPU_OF_PORT.items():
            pts = [(t["t"], t["running"].get(port)) for t in r["timeseries"] if t["running"].get(port) is not None]
            wts = [(t["t"], t["waiting"].get(port)) for t in r["timeseries"] if t["waiting"].get(port) is not None]
            if not pts:
                continue
            m = r["per_gpu"].get(gname, {})
            ax.plot([a for a, _ in pts], [b for _, b in pts], color=gcol[gname], linewidth=1.8,
                    label=f"{gname} running (mean {m.get('running_mean', 0):.0f})")
            if any(b for _, b in wts):
                ax.plot([a for a, _ in wts], [b for _, b in wts], color=gcol[gname], linewidth=1.2, linestyle=":",
                        label=f"{gname} waiting (mean {m.get('waiting_mean', 0):.0f})")
        ax.axhline(256, color=MUTED, linestyle="--", linewidth=1)
        ax.annotate("max-num-seqs 256 per vLLM", (0, 256), xycoords=("axes fraction", "data"), xytext=(4, 4),
                    textcoords="offset points", fontsize=8.5, color=MUTED)
        style(ax, f"{r['name']} · {r['users']} users", "", "Requests in flight")
        ax.legend(frameon=False, fontsize=8, loc="lower right", ncol=2)
    axes[-1].set_xlabel("Seconds after warm-up", color=MUTED)
    axes[0].set_ylim(0, 300)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


# ---------------- main ----------------
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # คอนโซล Windows ภาษาไทย (cp874) พิมพ์ ≈ ไม่ได้
    except Exception:
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(here, "..", "results"))
    a = ap.parse_args()
    res = os.path.normpath(a.results)

    sets = [load_set(p) for p in sorted(glob.glob(os.path.join(res, "loadtest_*.json")))
            if not os.path.basename(p).startswith("loadtest_mix_")]   # ชุด mix_ = เทียบวิธีกระจายงาน แยกต่างหาก
    order = {"single": 0, "batch": 1}
    sets.sort(key=lambda s: (order.get(s["mode"], 9), s["gpus"], s["lb"]))

    # ตารางตามจำนวน GPU: เท่าของ 1 ใบ เทียบกับ 1 GPU ของสถาปัตยกรรมเดียวกัน · efficiency = เท่า ÷ จำนวน GPU
    table = []
    for s in sets:
        base = next((b for b in sets if b["mode"] == s["mode"] and b["gpus"] == 1), None)
        sp = s["capacity_users"] / base["capacity_users"] if base and base["capacity_users"] else None
        tp = s["capacity_agg_tok_s"] / base["capacity_agg_tok_s"] if base and base["capacity_agg_tok_s"] else None
        table.append({"label": s["label"], "gpus": s["gpus"], "mode": s["mode"], "architecture": s["architecture"],
                      "capacity_users": s["capacity_users"], "agg_tok_s_at_capacity": s["capacity_agg_tok_s"],
                      "ttft_p95_at_capacity_s": s["capacity_ttft_p95"], "speed_p5_at_capacity": s["capacity_speed_p5"],
                      "speedup_vs_1gpu": round(sp, 3) if sp is not None else None,
                      "efficiency_pct": round(100 * sp / s["gpus"], 1) if sp is not None else None,
                      "tok_s_ratio_vs_1gpu": round(tp, 3) if tp is not None else None,
                      "vs_single_1gpu_x": None})
    single = next((s for s in sets if s["mode"] == "single" and s["gpus"] == 1), None)
    if single and single["capacity_users"]:
        for r in table:
            r["vs_single_1gpu_x"] = round(r["capacity_users"] / single["capacity_users"], 1)

    # ประมาณ 3 ใบ (คำนวณ ไม่ใช่ผลวัด): ความจุ 1 ใบ × 3 × efficiency ของ 2 ใบ ปัดลงเป็นขั้นละ 64 คนตามที่วัด
    est3 = None
    b1 = next((r for r in table if r["mode"] == "batch" and r["gpus"] == 1), None)
    b2 = next((r for r in table if r["mode"] == "batch" and r["gpus"] == 2), None)
    if b1 and b2 and b2["efficiency_pct"]:
        raw = b1["capacity_users"] * 3 * b2["efficiency_pct"] / 100
        est3 = {"users": int(round(raw)), "users_raw": round(raw, 1), "step_64_floor": int(raw // 64 * 64),
                "assumption": f"ความจุ 1 ใบ {b1['capacity_users']} × 3 × efficiency ของ 2 ใบ {b2['efficiency_pct']}% "
                              "(สมมติ NGINX/CPU ไม่เป็นคอขวด) — เป็นการคำนวณ ไม่ใช่ผลวัด"}

    metrics = {"slo": SLO, "capacity_rule": "ระดับ N สูงสุดที่ผ่าน SLO และทุกระดับที่ต่ำกว่าที่วัดก็ผ่าน · ระดับที่วัดซ้ำใช้ค่ากลาง (median)",
               "capacity_by_set": {s["label"]: s["capacity_users"] for s in sets},
               "table_by_gpus": table, "estimate_3gpu": est3,
               "repeated_levels": {s["label"]: [{"N": L["N"], "borderline": L["borderline"], "runs": L["runs"],
                                                 "median": {k: L[k] for k in ("ttft_p95", "speed_p5", "agg_tok_s", "error_rate")},
                                                 "pass": L["pass"]} for L in s["levels"] if L["repeated"]] for s in sets},
               "precheck": load_prechecks(res), "sets": sets}
    lbc = load_lb_compare(res)
    if lbc:
        metrics["lb_compare"] = [{k: v for k, v in r.items() if k != "timeseries"} for r in lbc]
    mp = os.path.join(res, "metrics.json")
    json.dump(metrics, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    plot_vs_n(sets, "ttft_p95", os.path.join(res, "ttft_p95_vs_n.png"), "TTFT p95 vs concurrent users",
              "TTFT p95 (s)", SLO["ttft_p95_max_s"], "SLO 2 s",
              cap_offsets={"batch_1gpu": (-8, 10, "right"), "batch_2gpu": (8, -16, "left")})
    plot_vs_n(sets, "speed_p5", os.path.join(res, "speed_p5_vs_n.png"), "Per-user speed p5 vs concurrent users",
              "tokens/s per user (p5)", SLO["speed_p5_min_tok_s"], "SLO 15 tok/s",
              cap_offsets={"batch_1gpu": (-10, -16, "right"), "batch_2gpu": (8, 10, "left")}, slo_left=True,
              legend_loc="upper right")
    plot_vs_n(sets, "agg_tok_s", os.path.join(res, "throughput_vs_n.png"), "Total throughput vs concurrent users",
              "Total tokens/s", mark_cap=True)
    plot_capacity(table, est3, os.path.join(res, "capacity_vs_gpus.png"))

    print(f"{'ชุด':<14}{'GPU':>4}{'ความจุ':>8}{'tok/s รวม':>11}{'TTFT p95':>10}{'เท่า':>7}{'eff%':>7}")
    for r in table:
        print(f"{r['label']:<14}{r['gpus']:>4}{r['capacity_users']:>8}{r['agg_tok_s_at_capacity'] or 0:>11.1f}"
              f"{r['ttft_p95_at_capacity_s'] or 0:>10.3f}{r['speedup_vs_1gpu'] or 0:>7.2f}{r['efficiency_pct'] or 0:>7.1f}")
    if est3:
        print(f"ประมาณ 3 ใบ ≈ {est3['users']} คน (คำนวณ ไม่ใช่ผลวัด)")
    n_fig = 4
    if lbc:
        plot_lb_ttft(lbc, os.path.join(res, "lb_ttft_p95.png"))
        plot_lb_running(lbc, os.path.join(res, "lb_running_per_gpu.png"))
        n_fig += 2
        print(f"\nเทียบวิธีกระจายงาน (คำถามยาว {100 * (lbc[0]['long_frac'] or 0):.0f}%)")
        print(f"{'วิธี':<13}{'ผู้ใช้':>6}{'TTFT p95':>10}{'สั้น':>7}{'ยาว':>7}{'p5 tok/s':>10}{'tok/s รวม':>11}"
              f"{'GPU0 ทำ':>9}{'GPU1 ทำ':>9}{'GPU0 รอ':>9}{'GPU1 รอ':>9}")
        for r in lbc:
            g0, g1 = r["per_gpu"].get("GPU 0", {}), r["per_gpu"].get("GPU 1", {})
            print(f"{r['name']:<13}{r['users']:>6}{r['ttft_p95']:>10.2f}{(r['short'] or {}).get('ttft_p95', 0):>7.2f}"
                  f"{(r['long'] or {}).get('ttft_p95', 0):>7.2f}{r['speed_p5']:>10.1f}{r['agg_tok_s']:>11.0f}"
                  f"{g0.get('running_mean', 0):>9.1f}{g1.get('running_mean', 0):>9.1f}"
                  f"{g0.get('waiting_mean', 0):>9.1f}{g1.get('waiting_mean', 0):>9.1f}")
    print("saved", mp, f"+ {n_fig} กราฟ")


if __name__ == "__main__":
    main()
