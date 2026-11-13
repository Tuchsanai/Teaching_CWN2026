#!/usr/bin/env python3
"""วาดภาพของ README หลักเป็น PNG ลง img/ จากผลจริง

  python tools/charts.py            (รันบนเครื่อง จากโฟลเดอร์ของบท หลัง bash tools/pull.sh)

ตัวเลขของบทนี้อ่านจาก runs/<ชื่อ>/state.json · ตัวเลขของบท 05 และ 06 อ่านจาก ../06_WikiSkill/results/results.json
และ ../06_WikiSkill/runs/w2/state.json (วัดบน Test Set ชุดเดียวกัน) ไม่มีค่าที่พิมพ์เอง
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import ROOT, USER, ADAPT, SOLVER, EVOLVER, FILE, BAD, INK, MUTE, LINE, shot

GREY = "#BCAAA4"
RUNS = [("e1", "e1 · เห็นเฉลยของ Training", "การตั้งค่าหลัก (Fine-grained Ground Truth)"),
        ("e2", "e2 · รันซ้ำของ e1", "การตั้งค่าเดียวกับ e1 ทุกค่า"),
        ("n1", "n1 · เฉลย + หมายเหตุ 1 ประโยค", "ผู้ใช้บอกว่างานที่ได้คะแนนเต็มมี 2 ไฟล์"),
        ("p1", "p1 · เห็นแต่คะแนน", "ไม่มีเฉลยใน Reference Folder"),
        ("f1", "f1 · เซสชันใหม่ทุก epoch", "เหมือน e1 แต่ Evolver ไม่ใช้ --resume"),
        ("f2", "f2 · รันซ้ำของ f1", "การตั้งค่าเดียวกับ f1 ทุกค่า"),
        ("h1", "h1 · haiku ทั้ง Solver และ Evolver", "Self-evolution ของโมเดลเล็ก")]


def state(ws):
    p = os.path.join(ROOT, "runs", ws, "state.json")
    if not os.path.isfile(p):
        return None
    st = json.load(open(p, encoding="utf-8"))
    return st if st.get("phase") == "test" else None


def pct(x):
    return "%.1f%%" % (x * 100)


def pill(color, text, size=22):
    return "<span style='display:inline-block;background:%s;color:#fff;border-radius:12px;padding:3px 13px;font-weight:700;font-size:%dpx;white-space:nowrap'>%s</span>" % (color, size, text)


# ------------------------------------------------------------------ d00 เรื่องทั้งหมดในภาพเดียว
def story():
    def c(color, n, title, sub, body):
        return """<div class='card' style='flex:1;border-top:14px solid %s;padding:14px 16px'>
          <div style='font-size:28px;font-weight:800;color:%s;line-height:1.2'>%s %s</div>
          <div class='mono' style='font-size:21px;color:#2A6F68;margin-top:4px'>%s</div>
          <div style='font-size:22px;color:%s;line-height:1.38;margin-top:6px'>%s</div></div>""" % (color, INK, n, title, sub, MUTE, body)
    ar = "<div class='arrow'>➜</div>"
    cards = ar.join([
        c(ADAPT, "1", "เตรียมสนาม", "adapt · ครั้งเดียว", "<b>Benchmark Adaptor</b> อ่านคำสั่งของผู้ใช้ แล้วทำรายการโจทย์ที่ล็อกแล้ว กับโฟลเดอร์อ้างอิง"),
        c(SOLVER, "2", "ทำโจทย์", "base · rollout", "<b>Solver</b> เขียนโค้ดคิดเงินของร้าน BaanKafe โจทย์ละ <b>3 ครั้ง</b> ตัวตรวจให้คะแนน"),
        c(EVOLVER, "3", "เขียนสกิล", "turn", "<b>Evolver</b> อ่านผลของชุด Training ทดลองด้วย bash แล้วเขียนชุดสกิลถัดไป"),
        c(INK, "4", "วัดครั้งเดียว", "test", "ชุดสกิลของ <b>epoch สุดท้าย</b> ถูกวัดกับ Test Set ที่ไม่เคยถูกใช้")])
    body = """<h1>EvoSkill v2: ปรับสกิลด้วย Agent 3 ตัว</h1>
    <div class='sub'>โจทย์เดียวกับบท 05 และ 06 · ต่างกันที่ผู้เขียนสกิลเป็น <b>Agent ตัวเดียวที่อยู่ตลอดการรัน</b> มี bash ให้ทดลอง และ <b>ไม่มีประตูรับ</b></div>
    <div class='row' style='gap:10px;align-items:stretch'>%s</div>
    <div style='text-align:center;font-size:29px;color:#6F4E37;font-weight:800;margin:14px 0 2px'>↺ ขั้น 2 และ 3 ทำซ้ำ 3 epoch · ชุดสกิลของทุก epoch ถูกรับ</div>""" % cards
    shot("img/d00-story.png", body)


# ------------------------------------------------------------------ r01 เส้นทางของ 1 การรัน
def path(ws, title, sub):
    st = state(ws)
    if not st:
        return
    L, T, E = st["legs"], st["turns"], st["epochs"]
    W, H, x0, y0, lo = 1090, 500, 90, 60, 30

    def X(k):
        return x0 + 110 + k * (W - x0 - 260) / float(E)

    def Y(s):
        return y0 + (100 - s * 100) / float(100 - lo) * (H - y0 - 100)
    svg = ""
    for s in range(lo, 101, 10):
        svg += "<line x1='%d' y1='%.0f' x2='%d' y2='%.0f' stroke='%s' stroke-width='2'/><text x='%d' y='%.0f' font-size='21' fill='%s' text-anchor='end'>%d%%</text>" % (
            x0, Y(s / 100.0), W - 20, Y(s / 100.0), LINE, x0 - 10, Y(s / 100.0) + 7, MUTE, s)
    tr = [(0, L["base_train"]["score"])] + [(k, L["v%d_train" % k]["score"]) for k in range(1, E) if "v%d_train" % k in L]
    va = [(0, L["base_val"]["score"])] + [(k, L["v%d_val" % k]["score"]) for k in range(1, E + 1)]
    for pts, col, dash in ((tr, SOLVER, "stroke-dasharray='14 9'"), (va, EVOLVER, "")):
        svg += "<polyline points='%s' fill='none' stroke='%s' stroke-width='7' %s/>" % (" ".join("%.0f,%.0f" % (X(k), Y(max(s, lo / 100.0))) for k, s in pts), col, dash)
    for k, s in tr:
        same = abs(s - dict(va)[k]) < 0.035
        svg += "<rect x='%.0f' y='%.0f' width='20' height='20' fill='%s' stroke='#fff' stroke-width='3' transform='rotate(45 %.0f %.0f)'/>" % (X(k) - 10, Y(s) - 10, SOLVER, X(k), Y(s))
        svg += "<text x='%.0f' y='%.0f' font-size='23' font-weight='800' fill='%s' text-anchor='end'>%s</text>" % (X(k) - 20, Y(s) + (-12 if not same else -14), "#C9772F", pct(s))
    for k, s in va:
        svg += "<circle cx='%.0f' cy='%.0f' r='13' fill='%s' stroke='#fff' stroke-width='4'/>" % (X(k), Y(s), EVOLVER)
        svg += "<text x='%.0f' y='%.0f' font-size='23' font-weight='800' fill='%s' text-anchor='start'>%s</text>" % (X(k) + 20, Y(s) + 32, "#1F7A6F", pct(s))
    for k in range(E + 1):
        t = next((t for t in T if t["k"] == k), None)
        svg += "<text x='%.0f' y='%d' font-size='23' font-weight='800' fill='%s' text-anchor='middle'>%s</text>" % (X(k), H - 56, INK, "ไม่มีสกิล" if k == 0 else "epoch %d" % k)
        if t:
            svg += "<text x='%.0f' y='%d' font-size='19' fill='%s' text-anchor='middle'>สกิล %.1f KB · ไฟล์อื่น %d</text>" % (X(k), H - 30, MUTE, t["skill_md_bytes"] / 1024.0, len(t["skill_other_files"]))
            svg += "<text x='%.0f' y='%d' font-size='19' fill='%s' text-anchor='middle'>Evolver %.0f วินาที · Bash %d</text>" % (X(k), H - 6, MUTE, t["wall_s"], t["bash"])
    bt, ft = L["base_test"], L["v%d_test" % E]

    def tcard(name, s, col):
        return """<div style='background:#fff;border:3px solid %s;border-left:14px solid %s;border-radius:16px;padding:10px 14px;margin-bottom:12px'>
          <div style='font-size:21px;color:%s'>%s</div><div style='font-size:38px;font-weight:800;color:%s;line-height:1.1'>%s</div>
          <div style='font-size:20px;color:%s'>ผ่านครบ 10 ข้อ %d/%d rollout</div></div>""" % (LINE, col, MUTE, name, INK, pct(s["score"]), MUTE, s["passes"], s["n"])
    right = "<div style='font-size:25px;font-weight:800;color:%s;margin-bottom:8px'>Test Set (Held-out)</div>%s%s<div style='font-size:20px;color:%s;line-height:1.4'>Evolver รวม %d ตา<br>%.0f วินาที · $%.2f</div>" % (
        INK, tcard("ไม่มีสกิล", bt, GREY), tcard("skills_v%d (epoch สุดท้าย)" % E, ft, INK), MUTE, len(T), sum(t["wall_s"] for t in T), sum(t["cost_usd"] for t in T))
    body = """<h1>%s</h1><div class='sub'>%s &nbsp; %s &nbsp; %s</div>
    <div class='row' style='align-items:flex-start'><div class='card' style='padding:10px 12px'><svg width='%d' height='%d'>%s</svg></div><div style='flex:1'>%s</div></div>""" % (
        title, sub, pill(SOLVER, "◆ เส้นประ = Training (Evolver เห็น)", 20), pill(EVOLVER, "● เส้นทึบ = Validation (Evolver ไม่เห็น)", 20), W, H, svg, right)
    shot("img/r01-path-%s.png" % ws, body)


# ------------------------------------------------------------------ r02 ทุกการรันของบทนี้
def runs_table():
    rows = ""
    for ws, name, desc in RUNS:
        st = state(ws)
        if not st:
            continue
        L, T, E = st["legs"], st["turns"], st["epochs"]
        va = [L["base_val"]["score"]] + [L["v%d_val" % k]["score"] for k in range(1, E + 1)]
        ft, bt = L["v%d_test" % E], L["base_test"]
        steps = " → ".join("<b>%s</b>" % pct(v) if i == len(va) - 1 else pct(v) for i, v in enumerate(va))
        w = ft["score"] * 100
        bar = "<div style='position:relative;height:38px;background:#F1E9DE;border-radius:10px'><div style='position:absolute;left:0;top:0;height:38px;width:%.1f%%;background:%s;border-radius:10px'></div><div style='position:absolute;left:%.1f%%;top:0;height:38px;width:4px;background:%s'></div><div style='position:absolute;left:12px;top:4px;font-size:23px;font-weight:800;color:#fff'>%s</div></div>" % (
            w, EVOLVER if ft["passes"] == ft["n"] else SOLVER, bt["score"] * 100, INK, pct(ft["score"]))
        rows += "<tr><td style='border-left:14px solid %s;width:390px'><b style='font-size:24px'>%s</b><br><span style='font-size:19px;color:%s'>%s</span></td><td style='font-size:22px;width:430px'>%s</td><td style='width:330px'>%s</td><td style='font-size:22px;text-align:center'>%d/%d</td><td style='font-size:22px;text-align:center'>$%.2f</td></tr>" % (
            EVOLVER, name, MUTE, desc, steps, bar, ft["passes"], ft["n"], sum(t["cost_usd"] for t in T))
    body = """<h1>ทุกการรันของบทนี้</h1>
    <div class='sub'>ผลจริง · Solver = sonnet / effort medium (ยกเว้น h1) · 3 epochs · โจทย์ละ 3 ครั้ง · แต่ละการตั้งค่ารัน 1 ครั้ง (e1 และ f1 มีรันซ้ำ) · ขีดสีเข้มบนแท่ง = คะแนน Test ตอนไม่มีสกิล</div>
    <table class='t'><tr><th>การรัน</th><th>Validation ราย epoch (0 → 3)</th><th>Test Set · ชุดของ epoch สุดท้าย</th><th>ผ่านครบ 10 ข้อ</th><th>ต้นทุนของ Evolver</th></tr>%s</table>""" % rows
    shot("img/r02-runs.png", body)


# ------------------------------------------------------------------ r03 เทียบกับบท 05 และ 06 บน Test Set
def compare():
    p6 = os.path.join(ROOT, "..", "06_WikiSkill", "results", "results.json")
    R = json.load(open(p6, encoding="utf-8")) if os.path.isfile(p6) else {}
    items = []
    if "noskill-test" in R:
        items.append(("ไม่มีสกิล", "วัดในบท 06", GREY, R["noskill-test"]["test"]))
    if "so-v3" in R:
        items.append(("Skill Optimizer v3", "บท 05 · คนเขียน แล้วปรับ 3 รอบ", USER, R["so-v3"]["test"]))
    for k, nm in (("w1-final", "WikiSkill (w1)"), ("w2-final", "WikiSkill (w2)")):
        if k in R:
            items.append((nm, "บท 06 · เริ่มจากว่าง", FILE, R[k]["test"]))
    for ws, name, desc in RUNS:
        st = state(ws)
        if st and ws in ("e1", "n1", "p1", "f1"):
            s = st["legs"]["v%d_test" % st["epochs"]]
            items.append(("EvoSkill v2 (%s)" % ws, name.split(" · ", 1)[1], EVOLVER, {"score": s["score"], "perfect": s["passes"], "n": s["n"], "context_tokens": s["context_tokens"]}))
    cols = ""
    for name, desc, col, s in items:
        h = s["score"] * 100
        cols += """<div style='flex:1;text-align:center'><div style='height:330px;display:flex;flex-direction:column;justify-content:flex-end'>
          <div style='font-size:27px;font-weight:800;color:%s'>%s</div><div style='font-size:19px;color:%s;margin-bottom:4px'>ผ่านครบ %d/%d</div>
          <div style='height:%.0fpx;background:%s;border-radius:12px 12px 0 0;margin:0 9px'></div></div>
          <div style='font-size:21px;font-weight:800;color:%s;line-height:1.2;margin-top:8px;height:52px'>%s</div><div style='font-size:18px;color:%s;line-height:1.25;margin-top:2px;height:46px'>%s</div>
          <div style='font-size:18px;color:%s;margin-top:6px'>%s โทเคน/rollout</div></div>""" % (
            INK, pct(s["score"]), MUTE, s["perfect"], s["n"], h * 2.5, col, INK, name, MUTE, desc, MUTE, format(int(s["context_tokens"]), ","))
    body = """<h1>Test Set 3 ข้อ: EvoSkill v2 เทียบกับบท 05 และ 06</h1>
    <div class='sub'>ผลจริง · โจทย์ ตัวตรวจ Solver (sonnet / effort medium) และพรอมต์ของ Solver ชุดเดียวกันทุกแท่ง · 3 โจทย์ × 3 ครั้ง = 9 rollout ต่อแท่ง · ตัวเลขของบท 05 และ 06 มาจากผลของบท 06</div>
    <div class='card'><div style='display:flex;align-items:flex-end'>%s</div></div>
    <div class='note' style='margin-top:10px'>สิ่งที่ผู้ปรับสกิลเห็นไม่เท่ากัน: บท 05 และ 06 อ่าน <b>ข้อความของตัวตรวจ</b> ของชุด Training ได้ · EvoSkill v2 ได้ <b>แต่คะแนน</b> และ (ถ้าผู้ใช้ให้) เฉลยของชุด Training</div>""" % cols
    shot("img/r03-compare.png", body)


# ------------------------------------------------------------------ r04 แรงที่ใช้ปรับสกิล
def effort():
    cols = []
    cols.append(("Skill Optimizer", "บท 05", USER, [("สกิลรุ่นแรก", "คนเขียน 5 บรรทัด"), ("ผู้ปรับสกิล", "Claude ตามพรอมต์ของคน"), ("เห็นอะไรจากตัวตรวจ", "ข้อตรวจที่ไม่ผ่าน"),
                                                    ("รอบ (รับ · ไม่รับ)", "5 (4 · 1)"), ("rollout ระหว่างปรับ", "108"), ("คนสั่งงาน", "5 พรอมต์")]))
    p = os.path.join(ROOT, "..", "06_WikiSkill", "runs", "w2", "state.json")
    if os.path.isfile(p):
        w = json.load(open(p, encoding="utf-8"))
        H = w["history"]
        tr = w["baseline"]["trials"] + sum(h["train"]["trials"] + (h.get("val") or {}).get("trials", 0) for h in H)
        acc = sum(1 for h in H if h.get("accepted"))
        oc = sum((h.get("maintainer") or {}).get("cost_usd") or 0 for h in H) + sum((h.get("proposer") or {}).get("cost_usd") or 0 for h in H)
        cols.append(("WikiSkill (w2)", "บท 06", FILE, [("สกิลรุ่นแรก", "ว่าง"), ("ผู้ปรับสกิล", "Maintainer + Proposer"), ("เห็นอะไรจากตัวตรวจ", "ข้อความของตัวตรวจใน Trace"),
                                                        ("รอบ (รับ · ไม่รับ)", "%d (%d · %d)" % (len(H), acc, len(H) - acc)), ("rollout ระหว่างปรับ", str(tr)), ("คนสั่งงาน", "1 คำสั่ง"),
                                                        ("ต้นทุนของผู้ปรับสกิล", "$%.2f" % oc)]))
    for ws in ("e1", "n1", "f1"):
        st = state(ws)
        if not st:
            continue
        L, T = st["legs"], st["turns"]
        dev = sum(s["n"] for lb, s in L.items() if not lb.endswith("_test"))
        cols.append(("EvoSkill v2 (%s)" % ws, "บทนี้", EVOLVER, [("สกิลรุ่นแรก", "ว่าง"), ("ผู้ปรับสกิล", "Evolver " + ("เซสชันใหม่ทุก epoch" if st["cfg"]["fresh_session"] else "เซสชันเดียว")),
                                                               ("เห็นอะไรจากตัวตรวจ", "คะแนน 0 ถึง 1" + (" + เฉลย" if st["adapt"]["reference"]["answers"] else "")),
                                                               ("รอบ (รับ · ไม่รับ)", "%d (%d · 0)" % (len(T), len(T))), ("rollout ระหว่างปรับ", str(dev)), ("คนสั่งงาน", "1 คำสั่ง"),
                                                               ("ต้นทุนของผู้ปรับสกิล", "$%.2f" % sum(t["cost_usd"] for t in T))]))
    html = ""
    for name, ch, col, rows in cols:
        tr = "".join("<div style='display:flex;justify-content:space-between;gap:8px;border-top:2px solid %s;padding:7px 0;font-size:20px'><span style='color:%s'>%s</span><b style='text-align:right'>%s</b></div>" % (LINE, MUTE, k, v) for k, v in rows)
        html += "<div class='card' style='flex:1;border-top:14px solid %s;padding:12px 14px'><div style='font-size:26px;font-weight:800;color:%s'>%s</div><div style='font-size:19px;color:%s;margin-bottom:6px'>%s</div>%s</div>" % (col, INK, name, MUTE, ch, tr)
    body = """<h1>แรงที่ใช้ปรับสกิล: 3 บท 3 วิธี</h1>
    <div class='sub'>ผลจริงของแต่ละบท · rollout ระหว่างปรับ = การทำโจทย์ของ Solver บน Training และ Validation (ไม่รวมการวัด Test Set ตอนจบ)</div>
    <div class='row' style='align-items:stretch;gap:12px'>%s</div>""" % html
    shot("img/r04-effort.png", body)


if __name__ == "__main__":
    story()
    for ws, name, desc in RUNS:
        st = state(ws)
        if st:
            c = st["cfg"]
            path(ws, "เส้นทางของการรัน %s" % name, "ผลจริง · Solver %s · Evolver %s%s" % (c["solver_model"], c["evolver_model"], " · เซสชันใหม่ทุก epoch" if c["fresh_session"] else ""))
    runs_table()
    compare()
    effort()
