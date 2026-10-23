#!/usr/bin/env python3
"""kcquest.py — เปิดดูข้างใน KC-QUEST ทีละขั้นด้วยตัวเลขจริง (โหมดสอน · ไม่ใช้โทเคน)

ใช้โค้ดจริงจาก tools/orch.py (ฟังก์ชันเดียวกับที่ LAB 04.2 ใช้แจกงานจริง) + ตัวจำลองเวลาของ tools/planner.py
แล้วแสดงทุกตัวเลขที่อัลกอริทึมคิดในแต่ละรอบแจกงาน: ① จัดลำดับ → ② กรอง → ③ ให้คะแนน → ④ เลือก + จอง

คำสั่ง (รันจากโฟลเดอร์ 03_KC_QUEST):
  python tools/kcquest.py rounds                     สรุปทุกรอบแจกงาน: นาทีที่ · งานที่พร้อม · ใครได้งานไหน
  python tools/kcquest.py explain --round 4 --png    อธิบายรอบที่ 4 ทีละขั้น → พิมพ์ + out/kcquest/round-4.md (+ round-4.png)

ตัวเลือก (ใช้ได้ทุกคำสั่ง):
  --tasks FILE        กราฟงาน (ค่าเริ่มต้น examples/catfood/tasks.json = แผนจาก LAB 02)
  --quota FILE        โควตาของบัญชี (ค่าเริ่มต้น examples/quota_lesson.json = สถานการณ์ของบทเรียน)
  --max-agents N      worker พร้อมกันสูงสุด (ค่าเริ่มต้น 6)
  --weights "urgency=0.4,fit=0.2,session=0.15,speed=0.15,load=-0.1"   เปลี่ยนน้ำหนัก (ใส่บางตัวก็ได้ · 0 = ปิดตัวแปรนั้น)
  --safety 1.3        ตัวเผื่อ σ
  --out DIR           โฟลเดอร์ผลลัพธ์ (ค่าเริ่มต้น out/kcquest)
"""
import argparse, copy, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import planner  # noqa: E402  (โหลด orch.py + ตัวจำลองเวลา)
orch = planner.orch

NAME = {"urgency": "U ใกล้หมดอายุ", "fit": "F พอดีถัง", "session": "R ว่าง 5 ชม.", "speed": "V เร็ว×วิกฤต", "load": "L งานล้น", "bonus": "B โบนัส"}
SHORT = {"urgency": "U", "fit": "F", "session": "R", "speed": "V", "load": "L", "bonus": "B"}
COLOR = {"urgency": "#e67e22", "fit": "#2e9e5b", "session": "#2b7bd6", "speed": "#8e44ad", "load": "#c0392b", "bonus": "#7f8c8d"}

def g(x, n=2):
    """ปัดเลขให้อ่านง่าย: 0.5454 → 0.55 · 33.230 → 33.23 · 7.0 → 7"""
    return f"{round(x, n):g}"

# ---------------------------------------------------------------- run + record
def run_plan(a):
    """จำลองทั้งแผนด้วย planner.simulate แล้ว "ดักจด" ทุกครั้งที่ KC-QUEST ถูกเรียก (สถานะบัญชีก่อนแจก + งานที่พร้อม)"""
    out = os.path.join(LAB, a.out) if not os.path.isabs(a.out) else a.out
    os.makedirs(out, exist_ok=True)
    run = orch.Run(out)
    run.cfg = copy.deepcopy(run.cfg)
    run.cfg["max_agents"] = a.max_agents
    if a.safety: run.cfg["safety"] = a.safety
    for kv in filter(None, (a.weights or "").replace(" ", "").split(",")):
        k, _, v = kv.partition("=")
        if k not in orch.FACTORS: sys.exit(f"ERROR ไม่รู้จักตัวแปร {k} (มี: {', '.join(orch.FACTORS)})")
        run.cfg["weights"][k] = float(v)
    tasks = (orch.jload(a.tasks, {}) or {}).get("tasks", [])
    if not tasks: sys.exit(f"ERROR อ่านงานจาก {a.tasks} ไม่ได้")
    snaps = planner.load_snaps(run, a.quota, [], {})
    cost = {t["id"]: float(t.get("est_mtok") or run.cfg["size_mtok"][t.get("size", "M")]) for t in tasks}
    rec, real = [], orch.plan_assignments
    def spy(items, states, cfg, fw, fi):
        before = copy.deepcopy(states)
        res = real(items, states, cfg, fw, fi)
        if res: rec.append({"items": copy.deepcopy(items), "states": before, "fw": fw, "fi": fi, "result": res})
        return res
    orch.plan_assignments = spy
    try:
        plan, rounds, peak, orch_acc, _ = planner.simulate(run, tasks, snaps, cost)
    finally:
        orch.plan_assignments = real
    for r, x in zip(rounds, rec): x["t_min"] = r["t_min"]
    rank, _, _ = planner.raw_ranks(tasks, cost)
    return run, tasks, cost, rank, plan, rec, orch_acc, out

# ---------------------------------------------------------------- rounds
def cmd_rounds(a):
    run, tasks, cost, rank, plan, rec, orch_acc, out = run_plan(a)
    W = run.cfg["weights"]
    L = [f"น้ำหนัก: " + " · ".join(f"{SHORT[k]} {g(v)}" for k, v in W.items() if v) + f" · σ = {run.cfg['safety']} · ตัวคุมวง (กันโควตาไว้ 20%) = {orch_acc}", "",
         "| รอบ | นาทีที่ | งานที่พร้อม (เรียงตามลำดับเลือก) | ได้งาน |", "|---|---|---|---|"]
    for k, x in enumerate(rec, 1):
        got = " · ".join(f"{tid}→{c['account']}" + (" (ส่งต่อ)" if m == "relay" else "") for tid, c, m, _ in x["result"])
        L.append(f"| {k} | {x['t_min']} | {', '.join(i['id'] for i in x['items'])} | {got} |")
    cnt = {}
    for p in plan.values():
        if p.get("status") == "planned": cnt.setdefault(p["account"], []).append(p["id"])
    span = max([p["end"] for p in plan.values() if p.get("end")] + [0]) * 60
    L += ["", "**สรุป:** " + " · ".join(f"`{acc}` {len(v)} งาน" for acc, v in sorted(cnt.items())) + f" · เวลารวม ≈ {span:.0f} นาที"]
    txt = "\n".join(L)
    print(txt); open(os.path.join(out, "rounds.md"), "w", encoding="utf-8").write(txt + "\n")

# ---------------------------------------------------------------- explain
def cmd_explain(a):
    run, tasks, cost, rank, plan, rec, orch_acc, out = run_plan(a)
    if not 1 <= a.round <= len(rec): sys.exit(f"ERROR มี {len(rec)} รอบ (ใช้ --round 1..{len(rec)} · ดูรายการด้วยคำสั่ง rounds)")
    x = rec[a.round - 1]; cfg = run.cfg; W, sig = cfg["weights"], cfg["safety"]
    states = copy.deepcopy(x["states"]); items = x["items"]; by = {t["id"]: t for t in tasks}
    mx = max(rank.values())
    L = [f"# KC-QUEST รอบที่ {a.round} · นาทีที่ {x['t_min']}", "",
         f"งานที่พร้อมทำ (งานที่รอเสร็จครบแล้ว): **{', '.join(i['id'] for i in items)}** · worker ว่าง {x['fw']} ที่ · ตัวคุมวง = `{orch_acc}`", ""]
    # สถานะบัญชี
    L += ["## สถานะบัญชีตอนเริ่มรอบ (หลังหักงานที่กำลังรันแล้ว)", "",
          "| บัญชี | เหลือ 5 ชม. $H^5$ | เหลือสัปดาห์ $H^w$ | อีกกี่ชม.หมดอายุ $T$ | อีกกี่ชม. 5 ชม.รีเซ็ต | $r^5$ (%/M) | $r^w$ (%/M) | slot | ทำอยู่ |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s in states:
        sr = "–" if s.get("sreset_h") is None else g(s["sreset_h"], 1)
        L.append(f"| {s['account']}{' 🎩' if s['is_orch'] else ''} | {g(s['h_s'])}% | {g(s['h_w'])}% | {g(s['hours_left'], 1)} | {sr} | {g(s['rs'])} | {g(s['rw'])} | {s['slots']} | {s['used']} |")
    L += ["", "🎩 = ตัวคุมวง (orchestrator): กันโควตาไว้ $Q$ = 20% และเว้น 1 slot ไว้คุมงาน", ""]
    # ① จัดลำดับ
    opts = {i["id"]: orch.choose_account(i["need"], i["crit"], states, cfg, kind_only=i.get("only"), avoid=i.get("avoid") or (), image=i.get("image")) for i in items}
    key = lambda i: (min(len(opts[i["id"]]), 3) if opts[i["id"]] else 9, -i["crit"], -i["need"])
    order = sorted(items, key=key)
    L += ["## ① จัดลำดับ: งานไหนได้เลือกก่อน", "",
          f"κ = rank ÷ rank สูงสุดของทั้งกราฟ ({g(mx)}) · เรียงตาม: **บัญชีที่รับได้น้อยก่อน (MRV)** → κ มากก่อน → ขนาด c มากก่อน", "",
          "| ลำดับ | งาน | rank | κ | c (M tok) | เงื่อนไขพิเศษ | บัญชีที่รับได้ |", "|---|---|---|---|---|---|---|"]
    for n, i in enumerate(order, 1):
        sp = ("เฉพาะ " + i["only"]) if i.get("only") else ("งานรูป" if i.get("image") else "–")
        L.append(f"| {n} | {i['id']} | {g(rank[i['id']])} | {g(i['crit'], 3)} | {g(i['need'])} | {sp} | {len(opts[i['id']])} ({', '.join(c['account'] for c in opts[i['id']]) or 'ไม่มี'}) |")
    L.append("")
    picks = {tid: c["account"] for tid, c, _, _ in x["result"]}
    fw, fi, svg_rows = x["fw"], x["fi"], []
    for i in order:
        tid, c_j = i["id"], i["need"]
        if (i.get("image") and fi <= 0) or (not i.get("image") and fw <= 0):
            L += [f"## {tid}: worker เต็มแล้ว → รอรอบหน้า", ""]; continue
        L += [f"## งาน {tid} · {by[tid].get('title', '')} · c = {g(c_j)} M tok", "", "### ② กรอง: บัญชีไหนทำงานนี้จนจบได้", "",
              "$C_a = \\min\\Big(\\dfrac{H^5 - m^5 - Q}{\\sigma\\, r^5},\\ \\dfrac{H^w - m^w - Q}{\\sigma\\, r^w}\\Big)$ · ผ่านเมื่อ $c_j \\le C_a$ · "
              f"σ = {sig} · m = เส้นเผื่อ (โควตาที่ใช้ได้ใน 15 นาที อย่างน้อย 2%)", "",
              "| บัญชี | slot ว่าง? | ถัง 5 ชม. | ถังสัปดาห์ | $C_a$ | ผล |", "|---|---|---|---|---|---|"]
        for s in states:
            if i.get("only") and s["kind"] != i["only"] or i.get("image") and s["kind"] != "cyolo":
                L.append(f"| {s['account']} | – | – | – | – | ❌ งานนี้ให้ {i.get('only') or 'cyolo'} เท่านั้น |"); continue
            need_free = s["slots"] - (1 if s["is_orch"] else 0)
            if not i.get("image") and s["used"] >= need_free:
                L.append(f"| {s['account']} | ❌ ทำอยู่ {s['used']}/{need_free} | – | – | – | ❌ slot เต็ม |"); continue
            Q = cfg["orch_min_headroom"] + 5 if s["is_orch"] else 0
            m5, mw = orch.margin(s, cfg, "session", s["used"] + 1), orch.margin(s, cfg, "week", s["used"] + 1)
            r5 = max(0.0, s["h_s"] - m5 - Q) / (sig * s["rs"]); rw = max(0.0, s["h_w"] - mw - Q) / (sig * s["rw"])
            t5 = f"({g(s['h_s'])} − {g(m5)}{f' − {Q}' if Q else ''}) ÷ ({sig}×{g(s['rs'])}) = {g(r5)}"
            sr = s.get("sreset_h")
            if sr is not None:
                before = cfg["speed_mtok_h"].get(s["kind"], 6.0) * sr
                if r5 >= before:
                    r5 = before + (100 - m5) / (sig * s["rs"])
                    t5 += f" → รีเซ็ตใน {g(sr, 1)} ชม. ได้โควตาใหม่ = **{g(r5)}**"
            C = min(r5, rw); assert abs(C - orch.capacity(s, cfg, Q)) < 1e-6
            tw = f"({g(s['h_w'])} − {g(mw)}{f' − {Q}' if Q else ''}) ÷ ({sig}×{g(s['rw'])}) = {g(rw)}"
            ok = c_j <= C
            L.append(f"| {s['account']}{' 🎩' if s['is_orch'] else ''} | ✅ {s['used']}/{need_free} | {t5} | {tw} | **{g(C)}** | "
                     f"{'✅ ' + g(c_j) + ' ≤ ' + g(C) if ok else '❌ ' + g(c_j) + ' > ' + g(C) + ' (ทำไม่จบ)'} |")
        cands = orch.choose_account(c_j, i["crit"], states, cfg, kind_only=i.get("only"), avoid=i.get("avoid") or (), image=i.get("image"))
        L.append("")
        if not cands:
            L += ["ไม่มีบัญชีไหนปิดงานนี้คนเดียวได้ → ใช้โหมด **ส่งต่อตามแผน (relay)**: เริ่มที่บัญชีที่ดีสุดแล้วย้ายงานต่อเมื่อใกล้เพดาน", ""]
            res = next(r for r in x["result"] if r[0] == tid)
            cands = res[3]
        L += ["### ③ ให้คะแนน: ใครเหมาะที่สุด", "",
              f"$S = 100 \\times (" + " + ".join(f"{g(w)}\\,{SHORT[k]}" for k, w in W.items() if w) + ")$ · ค่าแต่ละตัวอยู่ในช่วง 0..1", "",
              "| บัญชี | " + " | ".join(NAME[k] for k, w in W.items() if w) + " | คะแนน S |", "|---|" + "---|" * (sum(1 for w in W.values() if w) + 1)]
        for c in cands:
            L.append(f"| {c['account']} | " + " | ".join(g(c["parts"].get(k, 0), 3) for k, w in W.items() if w) + f" | **{c['score']}** |")
        best = cands[0]; p = best["parts"]
        L += ["", f"แทนค่าของ `{best['account']}`: S = 100 × (" + " + ".join(f"{g(w)}×{g(p.get(k, 0), 3)}" for k, w in W.items() if w)
              + f") = **{best['score']}**", ""]
        if len(cands) > 1: L.append(f"อันดับ 2 `{cands[1]['account']}` ได้ {cands[1]['score']} → ห่างกัน {g(best['score'] - cands[1]['score'], 1)} คะแนน")
        svg_rows.append((tid, cands, best["account"]))
        # ④ เลือก + จอง
        s = next(s for s in states if s["account"] == best["account"])
        h5, hw, used = s["h_s"], s["h_w"], s["used"]
        orch.reserve_on(states, best["account"], best["qs"], best["qw"], i.get("image"))
        L += ["", f"### ④ เลือก + จอง → `{best['account']}`", "",
              f"จองโควตาที่ประเมินไว้ทันที (σ × r × c) ให้งานถัดไปในรอบเดียวกันเห็นว่าเหลือน้อยลง:", "",
              f"- 5 ชม.: {g(h5)} − ({sig}×{g(s['rs'])}×{g(c_j)} = {g(best['qs'])}) = **{g(s['h_s'])}%**",
              f"- สัปดาห์: {g(hw)} − ({sig}×{g(s['rw'])}×{g(c_j)} = {g(best['qw'])}) = **{g(s['h_w'])}%**",
              f"- งานที่ทำอยู่: {used} → **{s['used']}**", ""]
        assert picks.get(tid) == best["account"], (tid, picks.get(tid), best["account"])
        if i.get("image"): fi -= 1
        else: fw -= 1
    md = "\n".join(L)
    path = os.path.join(out, f"round-{a.round}.md")
    open(path, "w", encoding="utf-8").write(md + "\n")
    print(md)
    if a.png and svg_rows:
        svg = os.path.join(out, f"round-{a.round}.svg")
        open(svg, "w", encoding="utf-8").write(render_scores(svg_rows, W, f"KC-QUEST รอบที่ {a.round} · นาทีที่ {x['t_min']} · คะแนนแยกตามตัวแปร"))
        png = planner.to_png(svg)
        print(f"\nภาพ: {png or svg}")
    print(f"ไฟล์: {path}")

def render_scores(rows, W, title):
    """แท่งคะแนนแยกส่วน: แต่ละแถว = (งาน, บัญชี) · ความยาวแต่ละสี = น้ำหนัก × ค่าตัวแปร × 100 · สีแดงทางซ้าย = ค่าปรับ L"""
    X0, LW, SC, RH, Y0 = 40, 190, 9.0, 40, 130
    n = sum(len(c) for _, c, _ in rows) + len(rows)
    W_ = X0 + LW + 120 + 60 * SC + 120; H = Y0 + n * RH + 80
    zero = X0 + LW + 120
    S = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_}" height="{H}" viewBox="0 0 {W_} {H}" font-family="Sarabun, Tahoma, sans-serif">',
         f'<rect width="{W_}" height="{H}" fill="#fff"/><rect width="{W_}" height="64" fill="#2b7bd6"/>',
         f'<text x="{X0}" y="42" font-size="24" font-weight="700" fill="#fff">{planner.esc(title)}</text>']
    lx = X0
    for k, w in W.items():
        if not w: continue
        S.append(f'<rect x="{lx}" y="84" width="20" height="20" rx="4" fill="{COLOR[k]}"/>'
                 f'<text x="{lx + 28}" y="100" font-size="17" fill="#333">{planner.esc(NAME[k])} ×{g(w)}</text>')
        lx += 60 + 11 * len(NAME[k])
    y = Y0
    for tid, cands, win in rows:
        S.append(f'<text x="{X0}" y="{y + 26}" font-size="20" font-weight="700" fill="#111">งาน {tid}</text>'); y += RH
        for c in cands:
            S.append(f'<text x="{X0 + 24}" y="{y + 26}" font-size="18" fill="#333">{c["account"]}</text>')
            x = zero
            for k, w in W.items():
                if not w: continue
                v = 100 * w * c["parts"].get(k, 0)
                if v >= 0:
                    S.append(f'<rect x="{x}" y="{y + 8}" width="{v * SC}" height="{RH - 14}" fill="{COLOR[k]}"/>'); x += v * SC
                else:
                    S.append(f'<rect x="{zero + v * SC}" y="{y + 8}" width="{-v * SC}" height="{RH - 14}" fill="{COLOR[k]}" fill-opacity="0.85"/>')
            hot = c["account"] == win
            S.append(f'<text x="{x + 10}" y="{y + 27}" font-size="19" font-weight="{700 if hot else 400}" fill="{"#dc5a1e" if hot else "#555"}">'
                     f'{c["score"]}{" ★ ได้งาน" if hot else ""}</text>')
            y += RH
    S.append(f'<line x1="{zero}" y1="{Y0}" x2="{zero}" y2="{y}" stroke="#999" stroke-dasharray="4 4"/>')
    S.append(f'<text x="{X0}" y="{H - 28}" font-size="16" fill="#666">ความยาวแต่ละสี = น้ำหนัก × ค่าตัวแปร × 100 · สีแดงทางซ้ายเส้นประ = ค่าปรับ (ถูกหักออก) · ตัวเลขท้ายแท่ง = คะแนนรวม S</text>')
    S.append("</svg>")
    return "\n".join(S)

def main():
    for f in (sys.stdout, sys.stderr):
        try: f.reconfigure(encoding="utf-8")
        except Exception: pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", choices=["rounds", "explain"])
    ap.add_argument("--tasks", default=os.path.join(LAB, "examples", "catfood", "tasks.json"))
    ap.add_argument("--quota", default=os.path.join(LAB, "examples", "quota_lesson.json"))
    ap.add_argument("--max-agents", type=int, default=6)
    ap.add_argument("--weights"); ap.add_argument("--safety", type=float)
    ap.add_argument("--round", type=int, default=1); ap.add_argument("--png", action="store_true")
    ap.add_argument("--out", default=os.path.join("out", "kcquest"))
    a = ap.parse_args()
    if not a.cmd: print(__doc__); return
    {"rounds": cmd_rounds, "explain": cmd_explain}[a.cmd](a)

if __name__ == "__main__":
    main()
