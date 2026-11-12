#!/usr/bin/env python3
"""วาดกราฟผลจริงของบทนี้เป็น PNG ลง img/

  python tools/charts.py            (รันบนเครื่อง จากโฟลเดอร์ของบท หลัง bash tools/pull.sh)

ตัวเลขทุกตัวอ่านจาก runs/<workspace>/state.json และ results/results.json ไม่มีค่าที่พิมพ์เอง
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import ROOT, RAW, WIKI, SKILL, GATE, BAD, INK, MUTE, LINE, shot

R = json.load(open(os.path.join(ROOT, "results", "results.json"), encoding="utf-8"))


def state(ws):
    return json.load(open(os.path.join(ROOT, "runs", ws, "state.json"), encoding="utf-8"))


def pct(x):
    return "%.1f%%" % (x * 100)


# ------------------------------------------------------------------ r01 เส้นทางของ 1 workspace
def path(ws, out, title, sub):
    st = state(ws)
    H = st["history"]
    W, Hh, x0, y0 = 1480, 540, 120, 90
    xs = [0] + [h["k"] for h in H]
    lo = 30

    def X(k):
        return x0 + 80 + k * (W - x0 - 200) / max(1, len(xs) - 1)

    def Y(s):
        return y0 + (100 - s * 100) / (100 - lo) * (Hh - y0 - 90)
    svg = ""
    for s in range(lo, 101, 10):
        svg += "<line x1='%d' y1='%.0f' x2='%d' y2='%.0f' stroke='%s' stroke-width='2'/><text x='%d' y='%.0f' font-size='22' fill='%s' text-anchor='end'>%d%%</text>" % (
            x0 - 10, Y(s / 100), W - 30, Y(s / 100), LINE, x0 - 22, Y(s / 100) + 8, MUTE, s)
    best = [(0, st["baseline"]["val_score"])] + [(h["k"], h["r_best_after"]) for h in H]
    for (k1, s1), (k2, s2) in zip(best, best[1:]):          # เส้น R_best (ขั้นบันได)
        svg += "<path d='M%.0f %.0f L%.0f %.0f L%.0f %.0f' stroke='%s' stroke-width='7' fill='none'/>" % (
            X(k1), Y(s1), X(k2), Y(s1), X(k2), Y(s2), GATE)
    svg += "<circle cx='%.0f' cy='%.0f' r='16' fill='%s' stroke='#fff' stroke-width='4'/><text x='%.0f' y='%.0f' font-size='26' font-weight='800' fill='%s' text-anchor='middle'>%s</text>" % (
        X(0), Y(best[0][1]), INK, X(0), Y(best[0][1]) - 26, INK, pct(best[0][1]))
    for h in H:
        x = X(h["k"])
        if h.get("val_score") is not None:
            col = GATE if h["accepted"] else BAD
            svg += "<circle cx='%.0f' cy='%.0f' r='18' fill='%s' stroke='#fff' stroke-width='4'/>" % (x, Y(h["val_score"]), col)
            svg += "<text x='%.0f' y='%.0f' font-size='27' font-weight='800' fill='%s' text-anchor='middle'>%s</text>" % (
                x, Y(h["val_score"]) - 54, INK, pct(h["val_score"]))
            svg += "<text x='%.0f' y='%.0f' font-size='21' font-weight='800' fill='%s' text-anchor='middle'>%s</text>" % (
                x, Y(h["val_score"]) - 26, col, h["outcome"])
        svg += "<rect x='%.0f' y='%.0f' width='22' height='22' fill='%s' transform='rotate(45 %.0f %.0f)'/>" % (
            x - 66, Y(h["train_score"]) - 11, RAW, x - 55, Y(h["train_score"]))
        svg += "<text x='%.0f' y='%.0f' font-size='21' fill='%s' text-anchor='middle'>%s</text>" % (
            x - 55, Y(h["train_score"]) - 24, RAW, pct(h["train_score"]))
    for k in xs:
        h = next((h for h in H if h["k"] == k), None)
        svg += "<text x='%.0f' y='%d' font-size='27' font-weight='800' fill='%s' text-anchor='middle'>%s</text>" % (
            X(k), Hh - 44, INK, "เริ่มต้น" if k == 0 else "รอบ %d" % k)
        lab = "ชุดสกิลว่าง" if k == 0 else ("%s · pattern %s หน้า" % ((h["proposal"] or {}).get("action", "-"), h.get("patterns_total", "-"))
                                           if st["cfg"]["use_wiki"] else (h["proposal"] or {}).get("action", "-"))
        svg += "<text x='%.0f' y='%d' font-size='21' fill='%s' text-anchor='middle'>%s</text>" % (X(k), Hh - 14, MUTE, lab)
    body = """<h1>%s</h1><div class='sub'>%s<br>
      <span class='badge gate'>● Validation ของสกิลที่เสนอ (รับ)</span> <span class='badge bad'>● ไม่รับ</span>
      <span class='badge raw'>◆ Training ของสกิลก่อนแก้</span> <span style='color:%s;font-weight:800'>━ R_best</span></div>
    <svg width='%d' height='%d' style='font-family:inherit'>%s</svg>""" % (title, sub, GATE, W, Hh, svg)
    shot(out, body, 760)


# ------------------------------------------------------------------ r02 เทียบชุดสกิลบนโจทย์ 9 ข้อ
def compare(labels, out, title, sub):
    """labels = [(ป้ายใน results.json, ชื่อที่แสดง, คำอธิบาย, สี)]"""
    cols = ""
    for lb, name, note, color in labels:
        r = R[lb]
        bars = ""
        for sp, c in (("train", RAW), ("val", SKILL), ("test", WIKI)):
            s = r[sp]
            if not s["n"]:
                bars += "<div style='width:78px'></div>"
                continue
            bars += """<div style='width:78px;height:%.0fpx;background:%s;border-radius:10px 10px 0 0;position:relative'>
              <span style='position:absolute;top:-32px;left:-6px;width:90px;text-align:center;font-size:23px;font-weight:700;color:%s'>%.1f</span></div>""" % (
                s["score"] * 330, c, INK, s["score"] * 100)
        a = r["all"]
        cols += """<div style='flex:1;display:flex;flex-direction:column;align-items:center'>
          <div style='height:380px;display:flex;align-items:flex-end;gap:10px;border-bottom:4px solid %s;padding:0 8px'>%s</div>
          <div style='font-size:26px;font-weight:800;color:%s;margin-top:10px;border-bottom:8px solid %s;padding-bottom:2px;white-space:nowrap'>%s</div>
          <div style='font-size:21px;color:%s;margin-top:6px;text-align:center;line-height:1.3;white-space:nowrap'>%s</div>
          <div style='font-size:23px;margin-top:8px;text-align:center;line-height:1.4;white-space:nowrap'>ผ่านครบ <b>%d/%d</b> Trial<br><b>%s</b> โทเคนต่อ Trial</div></div>""" % (
            INK, bars, INK, color, name, MUTE, note, a["perfect"], a["n"], format(a["context_tokens"], ","))
    body = """<h1>%s</h1><div class='sub'>%s ·
      <span class='badge raw'>Training</span> <span class='badge skill'>Validation</span> <span class='badge wiki'>Test (ไม่เคยถูกใช้ปรับสกิล)</span></div>
    <div class='row' style='gap:12px;margin-top:36px'>%s</div>""" % (title, sub, cols)
    shot(out, body, 760)


# ------------------------------------------------------------------ r03 ต้นทุนของการปรับ
def effort(rows, out):
    """rows = [(ชื่อ, สี, [(หัวข้อ, ค่า)])]"""
    heads = [h for h, _ in rows[0][2]]
    th = "<th></th>" + "".join("<th style='font-size:22px'>%s</th>" % h for h in heads)
    tr = ""
    for name, color, vals in rows:
        tr += "<tr><td style='border-left:14px solid %s;font-size:27px;font-weight:800;color:%s;width:300px;white-space:nowrap'>%s</td>%s</tr>" % (
            color, INK, name, "".join("<td style='font-size:24px;white-space:nowrap'>%s</td>" % v for _, v in vals))
    body = """<h1>ต้นทุนของการปรับสกิล: Skill Optimizer เทียบกับ WikiSkill</h1>
    <div class='sub'>โจทย์ ตัวตรวจ และโมเดลที่ทำโจทย์ (sonnet / effort medium) ชุดเดียวกัน · ต่างกันที่ผู้ปรับสกิลและวิธีเก็บความรู้</div>
    <table class='t'><tr>%s</tr>%s</table>""" % (th, tr)
    shot(out, body, 215 + 70 * len(rows))


if __name__ == "__main__":
    import run_charts  # รายการกราฟของบทนี้ (แยกไฟล์เพื่อให้แก้รายการได้ง่าย)
