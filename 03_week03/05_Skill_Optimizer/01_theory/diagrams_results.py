#!/usr/bin/env python3
"""ภาพของส่วนที่ 8 (ผลในเปเปอร์) และส่วนที่ 9 (ผลของ LAB) ของบททฤษฎี

  python 01_theory/diagrams_results.py        (รันบนเครื่อง จากโฟลเดอร์ของบท)

ตัวเลขของเปเปอร์คัดจาก Table 1 และ Table 3 ของ arXiv:2605.23904 (ค่าอยู่ใน PAPER ด้านล่าง)
ตัวเลขของ LAB อ่านจาก runs/results.json และ runs/<รุ่น>/gate.txt
"""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import charts
from charts import shot

charts.OUT = os.path.join(HERE, "img")
MONO = "font-family:Consolas,monospace"
INK, MUTE, LINE = "#4A2F1F", "#7A6557", "#E5D9CC"
TEAL, ORANGE, GREEN, RED, BROWN, PURPLE, GREY = "#1F8A7D", "#E0822F", "#3F9A35", "#D9573A", "#6F4E37", "#7B55B0", "#CFC4B8"

BENCH = ["SearchQA", "Spreadsheet", "OfficeQA", "DocVQA", "LiveMath", "ALFWorld"]
# Table 1 · GPT-5.5 · direct chat · คะแนนบน Test Split (%)
PAPER = [("ไม่มีสกิล", [77.7, 41.8, 33.1, 78.8, 37.6, 83.6]),
         ("คนเขียนสกิล", [81.8, 72.9, 66.9, 90.1, 38.4, 91.8]),
         ("LLM เขียนครั้งเดียว", [80.9, 43.2, 51.7, 89.6, 40.0, 93.3]),
         ("Trace2Skill", [82.4, 49.6, 65.7, 90.6, 52.0, 87.3]),
         ("TextGrad", [81.4, 41.1, 42.0, 87.2, 49.2, 82.8]),
         ("GEPA", [84.8, 73.6, 63.9, 89.1, 43.2, 85.8]),
         ("SkillOpt", [87.3, 80.7, 72.1, 91.2, 66.9, 95.5])]
# Table 3 · SearchQA, SpreadsheetBench, LiveMath
ABL = [("ครบทุกส่วน (ค่าตั้งต้น)", [87.1, 77.5, 61.3], TEAL, "–"),
       ("ไม่จำกัด Learning Rate", [84.6, 75.7, 57.3], ORANGE, "6.2.3"),
       ("ไม่มี Rejected-Edit Buffer", [85.5, 72.9, 58.9], RED, "6.3"),
       ("ไม่มี Meta Skill", [85.1, 75.7, 58.1], PURPLE, "6.4.2"),
       ("ไม่มี Meta Skill และ Slow Update", [86.3, 55.0, 59.7], PURPLE, "6.4")]


def main_results():
    no, so = PAPER[0][1], PAPER[-1][1]
    cols = ""
    for b, a, c in zip(BENCH, no, so):
        cols += """<div style='flex:1;display:flex;flex-direction:column;align-items:center'>
          <div style='font-size:27px;font-weight:800;color:%s;margin-bottom:4px'>+%.1f</div>
          <div style='display:flex;gap:8px;align-items:flex-end;height:360px'>
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%%'>
              <div style='font-size:22px;color:%s'>%.1f</div><div style='width:70px;height:%dpx;background:%s;border-radius:10px 10px 0 0'></div></div>
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%%'>
              <div style='font-size:22px;font-weight:800;color:%s'>%.1f</div><div style='width:70px;height:%dpx;background:%s;border-radius:10px 10px 0 0'></div></div></div>
          <div style='font-size:24px;font-weight:800;color:%s;margin-top:8px'>%s</div></div>""" % (
            GREEN, c - a, MUTE, a, int(a * 3.3), GREY, TEAL, c, int(c * 3.3), TEAL, INK, b)
    legend = """<div style='display:flex;gap:26px;font-size:23px;margin-bottom:6px'>
      <span><span style='display:inline-block;width:22px;height:22px;background:%s;border-radius:5px;vertical-align:-3px'></span> ไม่มีสกิล</span>
      <span><span style='display:inline-block;width:22px;height:22px;background:%s;border-radius:5px;vertical-align:-3px'></span> ใช้สกิลที่ SkillOpt เทรน</span>
      <span style='color:%s;font-weight:800'>ตัวเลขสีเขียว = คะแนนที่เพิ่มขึ้น (จุด)</span></div>""" % (GREY, TEAL, GREEN)
    avg = sum(c - a for a, c in zip(no, so)) / 6
    body = """<h1>ผลหลักของเปเปอร์: ไม่มีสกิล เทียบกับ SkillOpt</h1>
    <div class='sub' style='margin-bottom:10px'>โมเดล GPT-5.5 แบบ Direct Chat · คะแนนบน Test Split (%%) · โมเดลตัวเดียวกันทั้งสองแท่ง ต่างกันแค่มีสกิลหรือไม่มี · ที่มา: Table 1 ของเปเปอร์</div>
    %s<div style='display:flex;gap:6px;background:#fff;border:3px solid %s;border-radius:20px;padding:14px 16px'>%s</div>
    <div class='note' style='margin-top:12px'>เพิ่มขึ้นเฉลี่ย <b>+%.1f จุด</b> · เพิ่มมากที่สุดในงานที่ต้องทำหลายขั้นและใช้เครื่องมือ (Spreadsheet, OfficeQA, LiveMath)</div>""" % (legend, LINE, cols, avg)
    shot("t14-main-results", body, 745)


def methods():
    th = "font-size:21px;color:%s;font-weight:700;padding:4px 0;text-align:center" % MUTE
    rows = ""
    best = [max(r[1][i] for r in PAPER) for i in range(6)]
    second = [sorted((r[1][i] for r in PAPER), reverse=True)[1] for i in range(6)]
    for name, vals in PAPER:
        so = name == "SkillOpt"
        cells = ""
        for i, v in enumerate(vals):
            bg, fg, w = ("#DDF1EE", TEAL, 800) if v == best[i] else (("#FFF1DD", ORANGE, 700) if v == second[i] else ("#F7F2EB", INK, 400))
            cells += "<td style='width:150px;text-align:center;padding:3px 4px'><span style='display:block;padding:8px 0;border-radius:10px;background:%s;color:%s;font-weight:%d;font-size:25px;%s'>%.1f</span></td>" % (bg, fg, w, MONO, v)
        avg = sum(vals) / 6
        rows += """<tr><td style='font-size:25px;font-weight:%d;color:%s;padding:3px 16px 3px 8px;white-space:nowrap'>%s</td>%s
          <td style='padding-left:14px;font-size:25px;font-weight:800;color:%s;%s'>%.1f</td></tr>""" % (800 if so else 600, TEAL if so else INK, name, cells, TEAL if so else INK, MONO, avg)
    head = "<tr><th></th>%s<th style='%s;padding-left:14px'>เฉลี่ย</th></tr>" % ("".join("<th style='%s'>%s</th>" % (th, b) for b in BENCH), th)
    body = """<h1>SkillOpt เทียบกับวิธีอื่น</h1>
    <div class='sub' style='margin-bottom:12px'>โมเดล GPT-5.5 แบบ Direct Chat · คะแนนบน Test Split (%%) · <span style='color:%s;font-weight:800'>เขียวอมฟ้า = ดีที่สุดในคอลัมน์</span> ·
      <span style='color:%s;font-weight:800'>ส้ม = อันดับสอง</span> · ที่มา: Table 1 ของเปเปอร์</div>
    <div style='background:#fff;border:3px solid %s;border-radius:20px;padding:12px 16px'><table style='border-collapse:separate;border-spacing:0 2px;width:100%%'>%s%s</table></div>
    <div class='note' style='margin-top:12px'>3 แถวแรก = ไม่ปรับ หรือเขียนครั้งเดียว · Trace2Skill, TextGrad, GEPA = วิธีปรับอัตโนมัติจากงานวิจัยอื่น · SkillOpt ดีที่สุดทุกคอลัมน์</div>""" % (TEAL, ORANGE, LINE, head, rows)
    shot("t15-methods", body, 690)


def ablation():
    base = ABL[0][1]
    names = ["SearchQA", "SpreadsheetBench", "LiveMath"]
    th = "font-size:21px;color:%s;font-weight:700;padding:4px 0;text-align:left" % MUTE
    rows = ""
    for name, vals, col, sec in ABL:
        cells = ""
        for v, b in zip(vals, base):
            d = v - b
            bar = int(abs(d) * 9)
            dtxt = "" if abs(d) < 1e-9 else "<span style='color:%s;font-weight:800'>%+.1f</span>" % (RED, d)
            cells += """<td style='width:310px;padding:4px 6px'><div style='display:flex;align-items:center;gap:10px'>
              <span style='%s;font-size:26px;font-weight:700;width:70px'>%.1f</span>
              <span style='display:inline-block;height:20px;width:%dpx;background:%s;border-radius:6px'></span><span style='font-size:23px'>%s</span></div></td>""" % (MONO, v, bar, RED, dtxt)
        rows += """<tr style='background:#fff'><td style='font-size:24px;font-weight:800;color:%s;padding:10px 14px;border-left:12px solid %s;border-radius:12px 0 0 12px;white-space:nowrap'>%s</td>%s
          <td style='font-size:21px;color:%s;padding-right:14px;border-radius:0 12px 12px 0;text-align:right;white-space:nowrap'>%s</td></tr>""" % (INK, col, name, cells, MUTE, ("ข้อ " + sec) if sec != "–" else "")
    head = "<tr><th style='%s;padding-left:26px'>การตั้งค่า</th>%s<th style='%s;text-align:right;padding-right:14px;white-space:nowrap'>อธิบายใน</th></tr>" % (
        th, "".join("<th style='%s;padding-left:6px'>%s</th>" % (th, n) for n in names), th)
    body = """<h1>ถอดออกทีละส่วน แล้วคะแนนลดเท่าไร (Ablation)</h1>
    <div class='sub' style='margin-bottom:12px'>แถวแรก = ระบบครบทุกส่วน · แถวถัดไป = ถอดออก 1 ส่วนแล้วเทรนใหม่ · แท่งและตัวเลขสีแดง = คะแนนที่ลดลงเทียบกับแถวแรก (จุด) · ที่มา: Table 3 ของเปเปอร์</div>
    <table style='border-collapse:separate;border-spacing:0 7px;width:100%%'>%s%s</table>
    <div class='note' style='margin-top:10px'>ทุกส่วนที่ถอดออกทำให้คะแนนลด · ลดมากที่สุดเมื่อไม่มีความจำข้าม Epoch ทั้งสองอย่าง (SpreadsheetBench −22.5 จุด)</div>""" % (head, rows)
    shot("t16-ablation", body, 640)


def lab_descent():
    R = json.load(open(os.path.join(ROOT, "runs", "results.json"), encoding="utf-8"))
    G = {}
    for f in glob.glob(os.path.join(ROOT, "runs", "*", "gate.txt")):   # runs/<รุ่นใหม่>/gate.txt
        G[os.path.basename(os.path.dirname(f))] = "ACCEPT" in open(f, encoding="utf-8").read()
    labs = [("noskill", "ไม่มีสกิล"), ("v0", "v0"), ("v1", "v1"), ("v2", "v2"), ("v3", "v3"), ("v4", "v4")]
    cols, cur = "", None
    for lab, nm in labs:
        sc = R[lab]["all"]["score"] * 100
        err = 100 - sc
        tok = R[lab]["all"]["context_tokens"]
        ok = G.get(lab)
        col = BROWN if ok is None else (GREEN if ok else RED)
        verdict = "จุดเริ่มต้น" if ok is None else ("ACCEPT" if ok else "REJECT")
        cols += """<div style='flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end'>
          <div style='font-size:27px;font-weight:800;color:%s'>%.1f</div>
          <div style='width:120px;height:%dpx;background:%s;opacity:%s;border-radius:12px 12px 0 0;min-height:6px'></div>
          <div style='font-size:26px;font-weight:800;color:%s;margin-top:6px'>%s</div>
          <div style='font-size:22px;font-weight:800;color:%s'>%s</div>
          <div style='font-size:20px;color:%s'>คะแนน %.1f%%</div>
          <div style='font-size:20px;color:%s'>%s โทเคน</div></div>""" % (
            col, err, int(err * 4.6), col, "0.55" if ok is False else "1", INK, nm, col, verdict, MUTE, sc, MUTE, format(int(tok), ","))
    body = """<h1>ผลของ LAB อ่านแบบภูมิประเทศ: เดินลงเนินทีละก้าว</h1>
    <div class='sub' style='margin-bottom:8px'>ความสูงของแท่ง = ความผิดพลาด = 100 − คะแนนรวม (%%) · ยิ่งเตี้ยยิ่งดี · ตัวเลขจาก results/ ของ LAB</div>
    <div style='display:flex;gap:6px;align-items:flex-end;height:470px;background:#fff;border:3px solid %s;border-radius:20px;padding:14px 18px'>%s</div>
    <div class='note' style='margin-top:12px'>v0 → v2 = ลงเนิน 3 ก้าวจนถึงพื้น · v3 = ความสูงเท่าเดิมแต่ต้นทุนลด (LAB รับ) · v4 = ก้าวที่ทำให้สูงขึ้น ถูกปฏิเสธ สกิลที่ใช้ต่อยังเป็น v3</div>""" % (LINE, cols)
    shot("t17-lab-descent", body, 720)


if __name__ == "__main__":
    for w in sys.argv[1:] or ["main_results", "methods", "ablation", "lab_descent"]:
        globals()[w]()
