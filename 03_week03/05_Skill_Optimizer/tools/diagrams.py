#!/usr/bin/env python3
"""วาดแผนภาพอธิบายโจทย์ (ไพป์ไลน์การทดลอง และวิธีทำงานของ Grader) เป็น PNG

  python tools/diagrams.py        (รันบนเครื่อง จากโฟลเดอร์ของบท · ใช้ Chrome headless เหมือน charts.py)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from charts import shot

MONO = "font-family:Consolas,monospace"
CARD = "background:#fff;border:3px solid #E5D9CC;border-radius:22px;padding:16px 20px"


def card(color, title, file, note, width=""):
    return """<div style='%s;%s;border-top:14px solid %s'>
      <div style='font-size:31px;font-weight:800;color:#4A2F1F'>%s</div>
      <div style='%s;font-size:23px;color:#2A6F68;margin:5px 0 7px'>%s</div>
      <div style='font-size:23px;color:#7A6557;line-height:1.35'>%s</div></div>""" % (CARD, width, color, title, MONO, file, note)


def arrow(txt="➜"):
    return "<div style='font-size:44px;color:#6F4E37;align-self:center;font-weight:800'>%s</div>" % txt


def pipeline():
    row1 = "".join([
        card("#6F4E37", "โจทย์ 6 ข้อ", "suite/suite.json", "กติกาธุรกิจของแต่ละฟังก์ชัน<br>แบ่ง Training 4 · Validation 2", "flex:1"),
        card("#6F4E37", "ตัวตรวจ (Grader)", "suite/grade.py", "โค้ด Python ที่เราเขียนเอง<br>ตรวจข้อกำหนดของร้าน 10–11 ข้อ", "flex:1"),
        card("#6F4E37", "สกิล 1 รุ่น", "runs/v0/skills/money-coder/SKILL.md", "มาตรฐานของร้านที่เขียนให้ AI อ่าน<br>สิ่งเดียวที่เปลี่ยนในแต่ละรุ่น", "flex:1")])
    row2 = arrow("").join([]) + "".join([
        card("#2A9D8F", "1 เตรียมโฟลเดอร์ว่าง", "sandbox/", "วางสกิลไว้ใน<br>./skills", "flex:1"), arrow(),
        card("#2A9D8F", "2 Agent เขียนโค้ด", "solve.py · test_solve.py", "อ่านโจทย์และสกิล<br>แล้วเขียนเอง", "flex:1.15"), arrow(),
        card("#F4A261", "3 ตัวตรวจให้คะแนน", "grade.py → grade.json", "รันโค้ดของ Agent<br>ผ่านกี่ข้อจาก 10–11", "flex:1.1"), arrow(),
        card("#6BBF59", "4 รวมผลและตัดสิน", "report · gate", "เฉลี่ย 18 Trial เทียบรุ่นฐาน<br>ACCEPT หรือ REJECT", "flex:1.15")])
    body = """<h1>ไพป์ไลน์การทดลองของสกิล 1 รุ่น</h1>
    <div class='sub' style='margin-bottom:14px'>คนเตรียม 3 อย่าง · ที่เหลือ skill-optimizer รันให้อัตโนมัติ</div>
    <div style='font-size:27px;font-weight:800;color:#6F4E37;margin-bottom:8px'>คนเตรียม (ครั้งเดียว)</div>
    <div style='display:flex;gap:22px'>%s</div>
    <div style='text-align:center;font-size:40px;color:#6F4E37;font-weight:800;margin:6px 0 2px'>▼</div>
    <div style='font-size:27px;font-weight:800;color:#2A6F68;margin-bottom:8px'>skill-optimizer รันให้ (คำสั่ง run → report → gate)</div>
    <div style='display:flex;gap:10px'>%s</div>
    <div style='margin-top:18px;font-size:26px;color:#4A2F1F'><span class='badge teal'>ขั้น 1–3 = 1 Trial</span>
      ทำซ้ำ 6 โจทย์ × 3 รอบ = <b>18 Trial ต่อ 1 รุ่น</b> · ทุกรุ่นใช้โจทย์และตัวตรวจชุดเดิม จึงเทียบกันได้</div>""" % (row1, row2)
    shot("d01-pipeline", body, 840)


def grader():
    rows = [
        ("teal", "1", "เรียกฟังก์ชัน แล้วเทียบกับคำตอบที่ถูก", "shipping_fee(5019, 50, False)", "ต้องได้ 8029",
         "contract · basic · half_up · no_drift · boundary · policy"),
        ("orange", "2", "เรียกด้วย input ที่ผิด", "cashback(-1, \"gold\", False)", "ต้อง raise ValueError",
         "reject_value · reject_type"),
        ("brown", "3", "รันเป็นโปรแกรม ส่ง JSON เข้าทาง stdin", "python3 solve.py", "ต้องตอบ {\"ok\": true, \"result\": 500}",
         "cli_ok · cli_error"),
        ("green", "4", "รันเทสต์ที่ Agent เขียนมา", "python3 -m unittest -q test_solve", "ต้องผ่าน และมี 6 เทสต์ขึ้นไป",
         "tests"),
    ]
    h = ""
    for color, no, how, call, want, checks in rows:
        h += """<div style='%s;display:flex;align-items:center;gap:22px;margin-bottom:14px;padding:14px 22px'>
          <div class='badge %s' style='font-size:34px;width:64px;text-align:center'>%s</div>
          <div style='flex:1.25'><div style='font-size:29px;font-weight:800;color:#4A2F1F'>%s</div>
            <div style='%s;font-size:23px;color:#2A6F68;margin-top:5px'>%s</div></div>
          <div style='flex:0.95;font-size:25px;color:#4A2F1F'>%s</div>
          <div style='flex:1;%s;font-size:22px;color:#7A6557;text-align:right'>%s</div></div>""" % (
            CARD, color, no, how, MONO, call, want, MONO, checks)
    body = """<h1>ตัวตรวจ (Grader) ตรวจผลงานอย่างไร</h1>
    <div class='sub' style='margin-bottom:16px'>grade.py = โค้ด Python ที่เราเขียนครั้งเดียว · ตรวจ 4 วิธี รวม 10–11 ข้อต่องาน · คะแนน = ข้อที่ผ่าน ÷ จำนวนข้อตรวจของงานนั้น</div>
    <div style='display:flex;gap:22px;font-size:23px;color:#7A6557;padding:0 22px 6px'>
      <div style='width:64px'></div><div style='flex:1.25'>วิธีตรวจ และตัวอย่าง</div><div style='flex:0.95'>ผลที่ต้องได้</div><div style='flex:1;text-align:right'>ข้อตรวจ</div></div>
    %s
    <div style='font-size:25px;color:#4A2F1F;margin-top:6px'>คำตอบที่ถูกคำนวณอยู่ในตัวตรวจ ตามข้อกำหนดทั้ง 2 ประเภท รวมนโยบายธุรกิจ · Agent ไม่เห็นตัวตรวจและ input ที่ใช้ตรวจ</div>""" % h
    shot("d02-grader", body, 720)


def examples():
    """ตัวอย่าง input -> output ที่ถูกและผิดของฟังก์ชัน cashback (ค่าที่ผิดมาจาก Trial จริงใน results/runs)"""
    rows = [  # (ทดสอบเพื่อดูอะไร, input, ความหมายของ input, ถูก, ผิด, ที่มาของค่าที่ผิด, ข้อตรวจ)
        ("ระบุชัด + ความรู้แฝง 1<br>กรณีธรรมดา คิดถูกไหม", "cashback(20000, \"gold\", False)", "ซื้อ 200 บาท · สมาชิก gold · ไม่ใช่เดือนเกิด", "500", "", "ทุก Trial ทำถูก", "contract basic"),
        ("ข้อกำหนดที่ระบุชัด<br>ขอบของเงื่อนไข 100 บาท", "cashback(9999, \"gold\", False)", "ซื้อ 99.99 บาท (ต่ำกว่า 100 บาท)", "0", "", "ทุก Trial ทำถูก", "boundary"),
        ("นโยบายธุรกิจ C1<br>silver ได้ 2 เท่าในเดือนเกิดไหม", "cashback(20000, \"silver\", True)", "silver ซื้อ 200 บาท ในเดือนเกิด → ได้อัตราปกติ 1.5%", "300", "600", "ไม่มีสกิล · v0", "policy"),
        ("นโยบายธุรกิจ C2<br>เงินที่ร้านจ่ายออก ปัดลงไหม", "cashback(10020, \"gold\", False)", "ซื้อ 100.20 บาท → เงินคืน 250.5 สตางค์", "250", "251", "v0", "policy"),
        ("ความรู้แฝงข้อ 3<br>ค่านอกช่วง ปฏิเสธไหม", "cashback(-1, \"gold\", False)", "ยอดซื้อติดลบ", "ValueError", "0", "ไม่มีสกิล", "reject_value"),
        ("ความรู้แฝงข้อ 3<br>ชนิดข้อมูลผิด ปฏิเสธไหม", "cashback(20000.0, \"gold\", False)", "ยอดซื้อเป็นเลขทศนิยม ไม่ใช่จำนวนเต็ม", "ValueError", "500.0 · TypeError", "ไม่มีสกิล · v0", "reject_type"),
        ("ความรู้แฝงข้อ 4<br>รันเป็นโปรแกรม ตอบถูกไหม", "stdin {\"tier\": \"gold\", …}", "ข้อมูลเดียวกับแถวแรก ส่งเป็นข้อความ JSON", "{\"ok\": true, \"result\": 500}", "{\"cashback\": 500}", "v0", "cli_ok"),
        ("ความรู้แฝงข้อ 4<br>ข้อมูลผิด แจ้งถูกรูปแบบไหม", "stdin {\"tier\": \"bronze\", …}", "bronze = ระดับสมาชิกที่ร้านไม่มี", "{\"ok\": false, …} exit 2", "{\"error\": …} exit 1", "v0", "cli_error"),
        ("ความรู้แฝงข้อ 5<br>มีเทสต์มาด้วยไหม", "python3 -m unittest -q test_solve", "รันเทสต์ที่ AI เขียนมาพร้อมโค้ด", "6 เทสต์ขึ้นไป ผ่าน", "ไม่มีไฟล์เทสต์", "ไม่มีสกิล", "tests"),
    ]
    th = "font-size:23px;color:#7A6557;text-align:left;padding:0 10px 4px;font-weight:400"
    chip = "display:inline-block;border-radius:12px;padding:4px 9px;%s;font-size:19px;white-space:nowrap" % MONO
    h = ""
    for why, inp, mean, ok, bad, src, chk in rows:
        wrong = ("<span style='%s;background:#FBE3DC;border:2px solid #E76F51;color:#A63D25'>%s</span>"
                 "<div style='font-size:18px;color:#7A6557;margin-top:2px'>%s</div>" % (chip, bad, src)) if bad else \
                "<span style='font-size:20px;color:#7A6557'>%s</span>" % src
        h += """<tr style='background:#fff'>
          <td style='padding:7px 12px;font-size:20px;font-weight:700;color:#4A2F1F;border-radius:14px 0 0 14px;line-height:1.3'>%s</td>
          <td style='padding:7px 10px'><div style='%s;font-size:20px;color:#2A6F68;white-space:nowrap'>%s</div>
            <div style='font-size:19px;color:#7A6557;margin-top:2px;white-space:nowrap'>%s</div></td>
          <td style='padding:7px 10px'><span style='%s;background:#E3F3DE;border:2px solid #6BBF59;color:#2F6B22'>%s</span></td>
          <td style='padding:7px 10px;white-space:nowrap'>%s</td>
          <td style='padding:7px 10px;%s;font-size:19px;color:#4A2F1F;border-radius:0 14px 14px 0;white-space:nowrap'>%s</td></tr>""" % (
            why, MONO, inp, mean, chip, ok, wrong, MONO, chk)
    body = """<h1>ฟังก์ชัน cashback: แบบไหนถูก แบบไหนผิด</h1>
    <div class='sub' style='margin-bottom:8px'>cashback(ยอดซื้อเป็นสตางค์, ระดับสมาชิก, ซื้อในเดือนเกิดหรือไม่) → เงินคืนเป็นสตางค์ · Output ที่ผิดทุกค่ามาจาก Trial จริง</div>
    <table style='border-collapse:separate;border-spacing:0 6px;width:100%%;table-layout:fixed'>
      <colgroup><col style='width:275px'><col style='width:415px'><col style='width:350px'><col style='width:262px'><col style='width:178px'></colgroup>
      <tr><th style='%s'>ทดสอบข้อกำหนดข้อไหน</th><th style='%s'>Input และความหมาย</th><th style='%s'>Output ที่ถูก</th><th style='%s'>Output ที่ผิด</th><th style='%s'>ข้อตรวจ</th></tr>%s</table>""" % (
        th, th, th, th, th, h)
    shot("d03-examples", body, 940)


def algorithm():
    INK, MUTE, LINE = "#4A2F1F", "#7A6557", "#E5D9CC"
    TEAL, ORANGE, GREEN, RED, BROWN = "#2A9D8F", "#F4A261", "#6BBF59", "#E76F51", "#6F4E37"
    L = [("", "รับเข้า", "สกิลรุ่นแรก S<sub>0</sub> · งาน Training 4 งาน · งาน Validation 2 งาน · ตัวตรวจ", "", ""),
         ("0", "ตรวจตัวตรวจ", "เฉลยต้องได้ 10/10 · เฉลยที่จงใจผิด 1 จุด ต้องตกเฉพาะข้อนั้น", "check_grader.py", TEAL),
         ("1", "วัดรุ่นฐาน", "คะแนน(S<sub>0</sub>) = ค่าเฉลี่ยของ 6 งาน × 3 รอบ = 18 Trial", "run · report", ORANGE),
         ("", "ทำซ้ำ k = 1, 2, …", "", "", BROWN),
         ("2", "　วิเคราะห์ข้อที่ผิด", "ข้อที่ผิดของ S<sub>k−1</sub> เฉพาะ Training → สาเหตุที่พบมากกว่า 1 Trial → ISSUES.md", "failures", GREEN),
         ("3", "　คัดลอกแล้วแก้", "S′ = สำเนาของ S<sub>k−1</sub> ที่แก้ไม่เกิน 3 จุด (โฟลเดอร์ใหม่)", "lint", ORANGE),
         ("4", "　วัดรุ่นใหม่", "คะแนน(S′) ด้วยงาน จำนวนรอบ และโมเดล ชุดเดียวกับรุ่นฐาน", "run · report", TEAL),
         ("5", "　ประตูรับ", "Training ไม่ลด · Validation ไม่ลด · รวมดีขึ้นเกินเกณฑ์ หรือเท่าเดิมแต่ต้นทุนลด ≥ 10%", "gate", GREEN),
         ("", "　　ถ้าผ่านครบ 3 ข้อ", "<b>ACCEPT</b>: S<sub>k</sub> = S′ (รุ่นใหม่เป็นรุ่นฐาน)", "gate", GREEN),
         ("", "　　ถ้าไม่", "<b>REJECT</b>: S<sub>k</sub> = S<sub>k−1</sub> (ทิ้ง S′ · จดเหตุผลลง ISSUES.md)", "gate", RED),
         ("", "　หยุดเมื่อ", "ไม่มีข้อที่ผิดซ้ำ และคะแนนหรือต้นทุนไม่ดีขึ้นแล้ว", "", BROWN),
         ("", "ส่งออก", "สกิลรุ่นฐานล่าสุด S<sub>k</sub> และ ISSUES.md", "", INK)]
    rows = ""
    for no, name, txt, cmd, col in L:
        rows += """<div style='display:flex;align-items:center;gap:16px;background:#fff;border-radius:12px;padding:8px 16px;margin-bottom:7px;border-left:12px solid %s'>
          <div style='%s;width:86px;font-size:22px;color:%s'>%s</div>
          <div style='width:300px;font-size:25px;font-weight:800;color:%s;white-space:pre'>%s</div>
          <div style='flex:1;font-size:23px'>%s</div>
          <div style='%s;width:210px;font-size:21px;color:#2A6F68;text-align:right'>%s</div></div>""" % (
            col or LINE, MONO, MUTE, ("ขั้น " + no) if no else "", INK, name, txt, MONO, cmd)
    body = """<h1>Algorithm 1: วงรอบของ Skill Optimizer</h1>
    <div class='sub' style='margin-bottom:18px'>เลขทางซ้าย = ขั้นของอัลกอริทึม · ทางขวา = คำสั่งของ <span style='%s'>skillopt.py</span> ที่ทำขั้นนั้น ·
      S<sub>k</sub> = สกิลรุ่นฐานหลังรอบที่ k · S′ = สกิลรุ่นใหม่ที่ยังไม่ถูกรับ</div>%s""" % (MONO, rows)
    shot("d04-algorithm", body, 900)


if __name__ == "__main__":
    which = sys.argv[1:] or ["pipeline", "grader", "examples", "algorithm"]
    for w in which:
        globals()[w]()
