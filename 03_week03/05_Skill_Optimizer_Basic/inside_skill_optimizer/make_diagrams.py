#!/usr/bin/env python3
"""วาดแผนภาพของโฟลเดอร์นี้ (รันบนเครื่อง จากโฟลเดอร์ของบท):  python inside_skill_optimizer/make_diagrams.py"""
import os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
sys.path.insert(0, HERE)
import charts
import mini_gate

charts.OUT = os.path.join(HERE, "img")
shot = charts.shot
MONO = "font-family:Consolas,monospace"
CARD = "background:#fff;border:3px solid #E5D9CC;border-radius:20px;padding:14px 18px"


def box(color, title, sub, note, flex="1"):
    return """<div style='%s;flex:%s;border-top:13px solid %s'>
      <div style='%s;font-size:30px;font-weight:800;color:#4A2F1F'>%s</div>
      <div style='font-size:23px;color:#4A2F1F;margin:6px 0 4px;font-weight:700'>%s</div>
      <div style='font-size:21px;color:#7A6557;line-height:1.35'>%s</div></div>""" % (CARD, flex, color, MONO, title, sub, note)


def arrow():
    return "<div style='font-size:40px;color:#6F4E37;align-self:center;font-weight:800'>➜</div>"


def commands():
    row1 = "".join([box("#6F4E37", "lint", "วัดขนาดของสกิล", "นับบรรทัด ตัวอักษร ไฟล์<br>ตรวจลิงก์ที่เสีย"), arrow(),
                    box("#E76F51", "run", "ให้ AI ทำงานจริง", "1 งาน × 1 รอบ = 1 Trial<br><b>คำสั่งเดียวที่ใช้โทเคน</b>", "1.25"), arrow(),
                    box("#F4A261", "grade", "ให้คะแนนซ้ำ", "ใช้เมื่อแก้ตัวตรวจ<br>ไม่เรียก AI ใหม่")])
    row2 = "".join([box("#2A9D8F", "report", "ตารางเทียบรุ่น", "คะแนนเฉลี่ย เวลา โทเคน<br>แยก Training / Validation"),
                    box("#2A9D8F", "failures", "ข้อที่ผิด", "เฉพาะ Training Set<br>พร้อมที่อยู่ของ Trace"),
                    box("#2A9D8F", "null", "ความแกว่ง", "รุ่นเดียวกัน รันซ้ำ<br>คะแนนต่างกันแค่ไหน"),
                    box("#6BBF59", "gate", "ตัดสิน", "ACCEPT หรือ REJECT<br>เทียบรุ่นใหม่กับรุ่นฐาน")])
    body = """<h1>skillopt.py มี 7 คำสั่ง</h1>
    <div class='sub' style='margin-bottom:12px'>ทุกคำสั่งอ่านและเขียนไฟล์ในโฟลเดอร์ suite/runs/ · มีแค่ run ที่เรียก AI</div>
    <div style='font-size:26px;font-weight:800;color:#6F4E37;margin-bottom:8px'>ขั้นวัด: สร้างข้อมูล</div>
    <div style='display:flex;gap:10px'>%s</div>
    <div style='text-align:center;font-size:36px;color:#6F4E37;font-weight:800;margin:4px 0 0'>▼</div>
    <div style='font-size:26px;font-weight:800;color:#2A6F68;margin-bottom:8px'>ขั้นอ่านผล: คำนวณจากข้อมูลเดิม ไม่ใช้โทเคน</div>
    <div style='display:flex;gap:16px'>%s</div>""" % (row1, row2)
    shot("d10-commands", body, 690)


def run_inside():
    steps = [("#2A9D8F", "1 สร้างโฟลเดอร์ว่าง", "sandbox/", "1 Trial มีโฟลเดอร์ของตัวเอง<br>งานจึงไม่ปนกัน"),
             ("#2A9D8F", "2 วางสกิล", "sandbox/skills/", "คัดลอกสกิลรุ่นที่จะวัด<br>ไม่มีสกิล = ไม่วาง"),
             ("#2A9D8F", "3 เติมโจทย์ลงพรอมต์", "suite.json", "พรอมต์เหมือนกันทุกรุ่น<br>ต่างกันแค่โจทย์"),
             ("#E76F51", "4 เรียก AI", "yoloN -p \"…\"", "AI ทำงานใน sandbox<br>มีเวลาจำกัดต่อ Trial"),
             ("#F4A261", "5 เก็บหลักฐาน", "transcript.jsonl<br>metrics.json", "ทุกคำสั่งของ AI<br>เวลา โทเคน จำนวนคำสั่ง"),
             ("#6BBF59", "6 ให้คะแนน", "grade.py → grade.json", "ตัวตรวจรันโค้ดใน sandbox<br>ผ่านกี่ข้อ")]
    cells = []
    for c, t, f, n in steps:
        cells.append("""<div style='%s;flex:1;border-top:13px solid %s'>
          <div style='font-size:25px;font-weight:800;color:#4A2F1F'>%s</div>
          <div style='%s;font-size:19px;color:#2A6F68;margin:6px 0'>%s</div>
          <div style='font-size:19px;color:#7A6557;line-height:1.35'>%s</div></div>""" % (CARD, c, t, MONO, f, n))
    body = """<h1>ข้างในคำสั่ง run: 1 Trial ทำ 6 ขั้น</h1>
    <div class='sub' style='margin-bottom:14px'>run ทำแบบนี้กับทุกงาน ทุกรอบ และรันพร้อมกันหลาย Trial (กระจายไปหลายบัญชี)</div>
    <div style='display:flex;gap:8px'>%s</div>
    <div style='margin-top:16px;font-size:25px;color:#4A2F1F'>ผลของ 1 Trial อยู่ที่ <span style='%s;color:#2A6F68'>suite/runs/&lt;รุ่น&gt;/&lt;งาน&gt;-r&lt;รอบ&gt;/</span> · คำสั่งอื่นทุกคำสั่งอ่านจากโฟลเดอร์นี้</div>""" % (
        (arrow().replace("40px", "30px")).join(cells), MONO)
    shot("d11-run", body, 460)


def noise():
    rows = mini_gate.load("v0")
    by = {}
    for r in rows:
        by.setdefault(r["task"], []).append(round(r["score"]))
    h, vs = "", []
    for t, v in by.items():
        var = statistics.variance(v)
        vs.append(var)
        h += "<tr style='background:#fff'><td style='padding:7px 14px;%s;font-size:23px;border-radius:12px 0 0 12px'>%s</td>%s<td style='padding:7px 14px;font-size:24px;text-align:right;font-weight:700;border-radius:0 12px 12px 0;color:%s'>%.1f</td></tr>" % (
            MONO, t, "".join("<td style='padding:7px 14px;font-size:24px;text-align:center'>%d</td>" % x for x in v),
            "#E76F51" if var else "#7A6557", var)
    mv = statistics.mean(vs)
    se = (mv / len(rows)) ** 0.5
    se_b = mini_gate.se_of_mean(mini_gate.load("noskill"))
    sd = (se ** 2 + se_b ** 2) ** 0.5
    th = "font-size:22px;color:#7A6557;padding:0 14px 4px;font-weight:400"
    calc = [("ค่าเฉลี่ยของความแปรปรวน", "%.1f" % mv),
            ("ความแกว่งของค่าเฉลี่ย v0 = √(%.1f ÷ %d Trial)" % (mv, len(rows)), "%.2f จุด" % se),
            ("ความแกว่งของผลต่าง ไม่มีสกิล → v0 = √(%.2f² + %.2f²)" % (se_b, se), "%.2f จุด" % sd),
            ("threshold = ค่าที่มากกว่าระหว่าง 2.0 กับ 1.5 × %.2f" % sd, "%.1f จุด" % max(2.0, 1.5 * sd))]
    c = "".join("<div style='display:flex;justify-content:space-between;background:#fff;border:3px solid #E5D9CC;border-radius:14px;padding:9px 18px;margin-bottom:8px;font-size:25px'><span>%s</span><b>%s</b></div>" % x for x in calc)
    body = """<h1>ความแกว่งคิดอย่างไร: ตัวอย่างจริงของ v0</h1>
    <div class='sub' style='margin-bottom:8px'>งานเดียวกัน สกิลเดียวกัน รัน 3 รอบ · ถ้าคะแนน 3 รอบไม่เท่ากัน งานนั้นมีความแกว่ง</div>
    <div style='display:flex;gap:30px'>
      <table style='border-collapse:separate;border-spacing:0 5px;flex:1.05'>
        <tr><th style='%s;text-align:left'>งาน</th><th style='%s'>รอบ 1</th><th style='%s'>รอบ 2</th><th style='%s'>รอบ 3</th><th style='%s;text-align:right'>ความแปรปรวน</th></tr>%s</table>
      <div style='flex:1;padding-top:34px'>%s</div></div>""" % (th, th, th, th, th, h, c)
    shot("d12-noise", body, 530)


if __name__ == "__main__":
    commands()
    run_inside()
    noise()
