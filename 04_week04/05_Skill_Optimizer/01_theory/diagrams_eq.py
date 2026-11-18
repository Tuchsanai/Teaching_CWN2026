#!/usr/bin/env python3
"""ภาพของส่วนที่ 5 (สมการ 1-3) · สมการเรียงพิมพ์ด้วย KaTeX (LaTeX จริง) แล้วถ่ายภาพใน Chrome

  python 01_theory/diagrams_eq.py            (รันบนเครื่อง จากโฟลเดอร์ของบท)

คะแนน Validation ในภาพอ่านจาก runs/<รุ่น>/trials/<งาน>-r<รอบ>/grade.json ไม่มีค่าที่พิมพ์เอง
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(HERE, "tools"))
import charts
import slides_engine as E

charts.OUT = os.path.join(HERE, "img")
MONO = "font-family:Consolas,monospace"
INK, MUTE, LINE = "#4A2F1F", "#7A6557", "#E5D9CC"
TEAL, ORANGE, GREEN, RED, BROWN, PURPLE = "#1F8A7D", "#E0822F", "#3F9A35", "#D9573A", "#6F4E37", "#7B55B0"
VERS = [("noskill", "ไม่มีสกิล"), ("v0", "v0"), ("v1", "v1"), ("v2", "v2"), ("v3", "v3"), ("v4", "v4")]
VAL = ["v1-parking-fee", "v2-net-pay"]


def val_scores():
    out = {}
    for lab, _ in VERS:
        out[lab] = [json.load(open(os.path.join(ROOT, "runs", lab, "trials", "%s-r%d" % (t, r), "grade.json"), encoding="utf-8"))["score"]
                    for t in VAL for r in (1, 2, 3)]
    return out


def shot(name, body, height):
    """ถ่ายภาพ โดยฝัง CSS และฟอนต์ของ KaTeX ไว้ในหน้า"""
    charts.shot(name, "<style>%s .katex{font-size:1em} .katex-display{margin:0}</style>%s" % (E.katex_css(body), body), height)


def K(src, display=False):
    return E.tex(src, display)


def C(color, src):
    return r"\textcolor{%s}{%s}" % (color, src)


def badge(n, color, size=40):
    return "<span style='display:inline-flex;align-items:center;justify-content:center;width:%dpx;height:%dpx;border-radius:50%%;background:%s;color:#fff;font-size:%dpx;font-weight:800;flex:none'>%s</span>" % (
        size, size, color, int(size * 0.6), n)


def eqbox(src, size=54):
    return "<div style='background:#fff;border:4px solid %s;border-radius:22px;padding:14px 10px 12px;text-align:center;font-size:%dpx;color:%s'>%s</div>" % (
        LINE, size, INK, K(src, True))


D_TR, D_SEL, D_TEST, S_STAR = r"D_{\text{tr}}", r"D_{\text{sel}}", r"D_{\text{test}}", r"s^{\star}_{\text{sel}}"
EQ2 = r"%s = %s \; %s %s %s" % (
    S_STAR, C(ORANGE, r"\operatorname*{arg\,max}_{%s}" % C(GREEN, r"s \,\in\, \mathcal{C}(%s)" % D_TR)),
    C(PURPLE, r"\frac{1}{|%s|}" % D_SEL), C(TEAL, r"\sum_{x \in %s}" % D_SEL), C(RED, "r(s)"))
EQ3 = r"\text{Test}(%s) = %s %s %s%s%s" % (
    C(ORANGE, S_STAR), C(TEAL, r"\frac{1}{|%s|}" % D_TEST), C(TEAL, r"\sum_{x \in %s}" % D_TEST),
    C(RED, "r("), C(ORANGE, S_STAR), C(RED, ")"))


def part(n, color, sym, title, text):
    return """<div style='flex:1;background:#fff;border-radius:18px;padding:14px 18px;border-top:12px solid %s'>
      <div style='display:flex;align-items:center;gap:14px;height:62px'>%s<span style='font-size:32px'>%s</span></div>
      <div style='font-size:27px;font-weight:800;color:%s;margin:8px 0 4px'>%s</div>
      <div style='font-size:23px;line-height:1.4'>%s</div></div>""" % (color, badge(n, color), K(C(color, sym)), INK, title, text)


def eq2_anatomy():
    m = lambda t: "<span style='font-size:1.02em'>%s</span>" % K(t)
    parts = "".join([
        part(1, RED, "r(s)", "คะแนนของงาน 1 ชิ้น", "ได้จาก <b>สมการ 1</b><br>เมื่อโมเดลทำงาน %s ด้วยสกิล %s" % (m("x"), m("s"))),
        part(2, TEAL, r"\sum_{x \in %s}" % D_SEL, "บวกทุกงาน", "บวกคะแนนของงาน <b>ทุกชิ้น</b><br>ในชุด %s" % m(D_SEL)),
        part(3, PURPLE, r"\frac{1}{|%s|}" % D_SEL, "หารด้วยจำนวนงาน", "ได้ <b>คะแนนเฉลี่ย</b> ของสกิล %s<br>%s = จำนวนงานในชุด" % (m("s"), m("|%s|" % D_SEL))),
        part(4, ORANGE, r"\operatorname{arg\,max}", "เลือกรุ่นที่ดีที่สุด", "ทำข้อ 1–3 กับสกิล <b>ทุกรุ่น</b><br>แล้วตอบว่า <b>รุ่นไหน</b> เฉลี่ยสูงสุด")])
    body = """<h1>สมการ 2: เลือกสกิลรุ่นที่ดีที่สุด</h1>
    <div class='sub' style='margin-bottom:14px'>สีในสมการ ตรงกับสีของการ์ดด้านล่าง · อ่านตามเลข 1 → 4 คือจากขวาไปซ้ายของสมการ (ข้างในออกข้างนอก)</div>
    %s
    <div style='display:flex;gap:12px;margin-top:16px'>%s</div>
    <div class='note' style='margin-top:14px'>%s ใต้ arg max = "สกิล %s ทุกรุ่นที่สร้างขึ้นระหว่างเทรนด้วยข้อมูล %s" ·
      %s ทางซ้าย = ชื่อของสกิลที่ถูกเลือก</div>""" % (
        eqbox(EQ2), parts, m(C(GREEN, r"s \in \mathcal{C}(%s)" % D_TR)), m("s"), m(D_TR), m(S_STAR))
    shot("t07-eq2", body, 650)


def eq2_worked():
    V = val_scores()
    v0 = V["v0"]
    chips = "".join("<span style='%s;font-size:26px;font-weight:700;background:#FBE9E4;color:%s;border-radius:10px;padding:4px 8px'>%.1f</span>" % (MONO, RED, x) for x in v0)
    def card(n, color, title, inner):
        return """<div style='flex:1;background:#fff;border-radius:18px;padding:12px 18px;border-top:12px solid %s'>
          <div style='display:flex;align-items:center;gap:12px;font-size:26px;font-weight:800;color:%s'>%s%s</div>%s</div>""" % (color, INK, badge(n, color), title, inner)
    c1 = card(1, RED, "คะแนนของงานแต่ละชิ้น", "<div style='font-size:21px;color:%s;margin:8px 0 6px'>parking_fee 3 รอบ · net_pay 3 รอบ</div><div style='display:flex;gap:6px'>%s</div>" % (MUTE, chips))
    c2 = card(2, TEAL, "บวกทุกงาน", "<div style='%s;font-size:21px;margin-top:14px;white-space:nowrap'>%s</div><div style='%s;font-size:40px;font-weight:800;color:%s'>= %.1f</div>" % (
        MONO, " + ".join("%.1f" % x for x in v0), MONO, TEAL, sum(v0)))
    c3 = card(3, PURPLE, "หารด้วยจำนวนงาน", "<div style='%s;font-size:25px;margin-top:14px'>%.1f ÷ 6</div><div style='%s;font-size:40px;font-weight:800;color:%s'>= %.1f%%</div>" % (
        MONO, sum(v0), MONO, PURPLE, sum(v0) / 6 * 100))
    means = [(nm, sum(V[lab]) / 6 * 100) for lab, nm in VERS]
    best = max(m for _, m in means)
    bars = ""
    for nm, m in means:
        top = abs(m - best) < 1e-9
        bars += """<div style='flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end'>
          <div style='font-size:28px;font-weight:800;color:%s'>%s%.1f%%</div>
          <div style='width:120px;height:%dpx;background:%s;border-radius:12px 12px 0 0'></div>
          <div style='font-size:26px;font-weight:800;color:%s;margin-top:6px'>%s</div></div>""" % (
            ORANGE if top else INK, "★ " if top else "", m, int(m * 1.9), ORANGE if top else "#D9CFC3", INK, nm)
    c4 = """<div style='background:#fff;border-radius:18px;padding:12px 18px 14px;border-top:12px solid %s;margin-top:12px'>
      <div style='display:flex;align-items:center;gap:12px;font-size:26px;font-weight:800;color:%s'>%sทำข้อ 1–3 กับสกิลทุกรุ่น แล้วเลือกรุ่นที่เฉลี่ยสูงสุด (arg max)</div>
      <div style='display:flex;gap:8px;align-items:flex-end;height:270px;margin-top:6px'>%s</div></div>""" % (ORANGE, INK, badge(4, ORANGE), bars)
    body = """<h1>สมการ 2 คิดตามทีละขั้น ด้วยคะแนนจริงของ LAB</h1>
    <div class='sub' style='margin-bottom:12px'>ขั้น 1–3 คิดให้ดูกับสกิลรุ่น <b>v0</b> · D<sub>sel</sub> ของ LAB = Validation Set (2 งาน × 3 รอบ = 6 ค่า) · ขั้น 4 เทียบทุกรุ่น</div>
    <div style='display:flex;gap:12px'>%s%s%s</div>%s
    <div class='note' style='margin-top:10px'>max ตอบว่าค่าสูงสุดคือ <b>%.1f%%</b> · arg max ตอบว่ารุ่นที่ได้ค่านั้นคือ <b>%s</b> · ถ้ามีรุ่นที่เสมอกัน กติกาของเปเปอร์ไม่รับรุ่นใหม่ (ต้องสูงกว่าเดิม)</div>""" % (
        c1, c2, c3, c4, best, " และ ".join(nm for nm, m in means if abs(m - best) < 1e-9))
    shot("t07b-eq2-worked", body, 765)


def eq3_anatomy():
    m = lambda t: "<span style='font-size:1.02em'>%s</span>" % K(t)
    parts = "".join([
        part(1, ORANGE, S_STAR, "สกิลที่เลือกแล้ว", "คำตอบของ <b>สมการ 2</b><br>ใช้รุ่นนี้ <b>รุ่นเดียว</b>"),
        part(2, RED, "r(%s)" % S_STAR, "คะแนนของงาน 1 ชิ้น", "ได้จาก <b>สมการ 1</b><br>แต่งาน %s มาจาก %s" % (m("x"), m(D_TEST))),
        part(3, TEAL, r"\frac{1}{|%s|} \sum_{x \in %s}" % (D_TEST, D_TEST), "เฉลี่ยทุกงาน", "วิธีเฉลี่ยเหมือนสมการ 2<br>เปลี่ยนชุดข้อมูลเป็น %s" % m(D_TEST))])
    body = """<h1>สมการ 3: รายงานผลของสกิลที่เลือก</h1>
    <div class='sub' style='margin-bottom:14px'>ไม่มี arg max เพราะไม่ได้เลือกอะไรแล้ว · เป็นการวัดอย่างเดียว บนข้อมูลที่ไม่เคยถูกใช้มาก่อน</div>
    %s<div style='display:flex;gap:12px;margin-top:16px'>%s</div>""" % (eqbox(EQ3), parts)
    shot("t07c-eq3", body, 600)


def grid():
    """ตารางเดียวที่เห็นทั้ง 3 สมการ: แถว = สกิล 1 รุ่น · คอลัมน์ = งาน 1 ชิ้น"""
    V = val_scores()
    means = {lab: sum(v) / 6 * 100 for lab, v in V.items()}
    best = max(means.values())
    th = "font-size:19px;color:%s;font-weight:700;padding:2px 0;text-align:center" % MUTE
    rows = ""
    for lab, nm in VERS:
        top = abs(means[lab] - best) < 1e-9
        cells = "".join("<td style='width:78px;text-align:center'><span style='display:inline-block;width:64px;padding:7px 0;border-radius:10px;background:#FBE9E4;color:%s;%s;font-size:23px;font-weight:700'>%.1f</span></td>" % (RED, MONO, x) for x in V[lab])
        tcell = "".join("<td style='width:78px;text-align:center'><span style='display:inline-block;width:64px;padding:7px 0;border-radius:10px;background:%s;color:%s;%s;font-size:23px;font-weight:700'>%s</span></td>" % (
            ("#FFF1DD" if top else "#F3EDE4"), (ORANGE if top else "#C9BDB0"), MONO, "?" if top else "–") for _ in range(3))
        rows += """<tr><td style='font-size:25px;font-weight:800;color:%s;padding:5px 14px 5px 6px;white-space:nowrap'>%s%s</td>%s
          <td style='padding-left:14px'><span style='display:inline-block;min-width:140px;padding:7px 14px;border-radius:10px;background:%s;color:%s;font-size:25px;font-weight:800;text-align:center'>%.1f%%</span></td>
          <td style='width:26px'></td>%s
          <td style='padding-left:14px'><span style='display:inline-block;min-width:120px;padding:7px 14px;border-radius:10px;background:%s;color:%s;font-size:23px;font-weight:800;text-align:center'>%s</span></td></tr>""" % (
            INK, "★ " if top else "", nm, cells, ("#FFE3C2" if top else "#EFE6FA"), (ORANGE if top else PURPLE), means[lab], tcell,
            ("#FFE3C2" if top else "#F3EDE4"), (ORANGE if top else "#C9BDB0"), "ผลที่รายงาน" if top else "ไม่วัด")
    table = """<table style='border-collapse:separate;border-spacing:0 3px'>
      <tr><th></th><th colspan='6' style='%s;background:#E6F3F1;border-radius:10px;color:%s;font-size:22px;padding:6px 0'>D<sub>sel</sub> · งาน 6 ชิ้น (LAB: parking_fee 3 รอบ · net_pay 3 รอบ)</th>
          <th style='%s'>เฉลี่ยบน D<sub>sel</sub></th><th></th>
          <th colspan='3' style='%s;background:#FBE9E4;border-radius:10px;color:%s;font-size:22px;padding:6px 0'>D<sub>test</sub> 🔒</th><th style='%s'>เฉลี่ยบน D<sub>test</sub></th></tr>
      %s</table>""" % (th, TEAL, th, th, RED, th, rows)
    def leg(n, color, t):
        return "<div style='flex:1;display:flex;gap:12px;align-items:flex-start;background:#fff;border-radius:16px;padding:10px 14px;border-left:10px solid %s'>%s<div style='font-size:22px;line-height:1.35'>%s</div></div>" % (color, badge(n, color, 36), t)
    legend = "".join([
        leg(1, RED, "<b>สมการ 1</b> = <b>1 ช่อง</b><br>คะแนน r ของงาน 1 ชิ้น ด้วยสกิล 1 รุ่น"),
        leg(2, PURPLE, "<b>สมการ 2 (ส่วนใน)</b> = <b>เฉลี่ย 1 แถว</b><br>คะแนนเฉลี่ยของสกิลรุ่นนั้นบน D<sub>sel</sub>"),
        leg(3, ORANGE, "<b>สมการ 2 (arg max)</b> = <b>เลือกแถว</b><br>แถวที่เฉลี่ยสูงสุด คือ s<sup>★</sup><sub>sel</sub>"),
        leg(4, BROWN, "<b>สมการ 3</b> = <b>เฉลี่ยแถวที่เลือก</b> บน D<sub>test</sub><br>ตัวเลขที่รายงาน")])
    body = """<h1>ตารางเดียว เห็นทั้ง 3 สมการ</h1>
    <div class='sub' style='margin-bottom:10px'>แถว = สกิล 1 รุ่น · คอลัมน์ = งาน 1 ชิ้น · ตัวเลขใน D<sub>sel</sub> เป็นคะแนน Validation จริงของ LAB · LAB ไม่มี D<sub>test</sub> ช่องนั้นจึงเป็น "?"</div>
    <div style='background:#fff;border:3px solid %s;border-radius:20px;padding:12px 16px;display:flex;justify-content:center'>%s</div>
    <div style='display:flex;gap:10px;margin-top:12px'>%s</div>""" % (LINE, table, legend)
    shot("t05b-eq-grid", body, 770)


if __name__ == "__main__":
    for w in sys.argv[1:] or ["grid", "eq2_anatomy", "eq2_worked", "eq3_anatomy"]:
        globals()[w]()
