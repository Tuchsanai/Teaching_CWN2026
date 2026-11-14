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


def trial_example(label="v0", trial="t4-cashback-r1"):
    """1 Trial จริงตั้งแต่โจทย์ถึงคะแนน · ทุกอย่างอ่านจาก suite/suite.json และ runs/<รุ่น>/trials/<Trial>/ ไม่มีค่าที่พิมพ์เอง"""
    import html, json, re
    esc = html.escape
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(root, "runs", label, "trials", trial)
    task_id, rep = trial.rsplit("-r", 1)
    suite = json.load(open(os.path.join(root, "suite", "suite.json"), encoding="utf-8"))
    task = [x for x in suite["tasks"] if x["id"] == task_id][0]
    message = suite["prompt"].replace("{brief}", task["brief"]).replace("`", "")
    m = json.load(open(os.path.join(d, "metrics.json"), encoding="utf-8"))
    g = json.load(open(os.path.join(d, "grade.json"), encoding="utf-8"))
    code = open(os.path.join(d, "sandbox", "solve.py"), encoding="utf-8").read()
    tp = os.path.join(d, "sandbox", "test_solve.py")
    tests = open(tp, encoding="utf-8").read() if os.path.isfile(tp) else ""
    n_tests = len(re.findall(r"^\s*def test_", tests, re.M))
    tokens = m["input_tokens"] + m["cache_read"] + m["cache_write"]
    ok = [c["id"] for c in g["checks"] if c["pass"]]
    bad = {c["id"]: c["note"] for c in g["checks"] if not c["pass"]}

    def col(color, num, title, sub, inner, flex):
        return """<div style='flex:%s;min-width:0;background:#fff;border:3px solid #E5D9CC;border-top:14px solid %s;border-radius:22px;padding:12px 14px'>
          <div style='font-size:29px;font-weight:800;color:#4A2F1F'><span style='color:%s'>%s</span> %s</div>
          <div style='font-size:20px;color:#7A6557;margin:0 0 8px'>%s</div>%s</div>""" % (flex, color, color, num, title, sub, inner)

    def box(txt, size=16, color="#2A6F68"):
        return ("<div style='%s;font-size:%dpx;background:#F6EFE6;border-radius:12px;padding:8px 10px;color:%s;line-height:1.42;"
                "margin-bottom:7px;overflow-wrap:anywhere'>%s</div>" % (MONO, size, color, txt))

    def way(name, lines, passed):
        mark = "<span style='color:#2F6B22'>✓ ผ่าน</span>" if passed else "<span style='color:#A63D25'>✗ ไม่ผ่าน</span>"
        return """<div style='border:2px solid %s;border-radius:12px;padding:6px 10px;margin-bottom:7px;background:%s'>
          <div style='font-size:18px;font-weight:800;color:#4A2F1F;white-space:nowrap'>%s &nbsp;%s</div>
          <div style='%s;font-size:15px;color:#4A2F1F;line-height:1.4;overflow-wrap:anywhere'>%s</div></div>""" % (
            "#6BBF59" if passed else "#E76F51", "#EEF8EA" if passed else "#FDEDE8", name, mark, MONO, "<br>".join(lines))

    # ① Input: ข้อความเต็มที่ Agent ได้รับ
    msg_html = "<br>".join(esc(l) for l in message.split("\n"))
    c1 = col("#6F4E37", "①", "Input", "ข้อความที่ Agent ได้รับ (โจทย์ %s) และสกิลที่วางไว้ให้" % task_id,
             box(msg_html, 15, "#4A2F1F") + box("./skills/money-coder/SKILL.md &nbsp;← สกิลรุ่น %s" % label if label != "noskill" else "(ไม่มีโฟลเดอร์ ./skills)", 15), "2.25")

    # ② Generate: คำสั่งจริงของ Agent
    cmds = []
    for c in m.get("commands", []):
        try:
            name, arg = c.split(" ", 1)
            inp = json.loads(arg)
            s = inp.get("command") or inp.get("file_path") or arg
        except ValueError:                      # คำสั่งยาวถูกตัดที่ 400 ตัวอักษร จึงไม่ใช่ JSON ครบ
            mm = re.search(r'"command": "(.*)', c, re.S)
            s = mm.group(1).replace("\\n", "\n").replace('\\"', '"') if mm else c
        first = s.split("\n")[0].strip()
        more = " …" if ("\n" in s or len(first) > 40) else ""
        cmds.append(esc(first[:40]) + more)
    c2 = col("#2A9D8F", "②", "Generate", "คำสั่งที่ Agent ใช้",
             "".join(box("%d&nbsp; %s" % (i + 1, c), 15) for i, c in enumerate(cmds[:5]))
             + "<div style='font-size:19px;color:#4A2F1F;line-height:1.4'>%d คำสั่ง · %.1f วินาที<br>%s โทเคนขาเข้า</div>" % (
                 m["tool_calls"], m["wall_s"], format(tokens, ",")), "1.25")

    # ③ Output: ไฟล์ และบรรทัดสำคัญของโค้ด
    sig = (re.search(r"^def %s\(.*$" % re.escape(task_id.split("-", 1)[1].replace("-", "_")), code, re.M) or re.search(r"^def \w+\(.*$", code, re.M)).group(0)
    prints = [l.strip() for l in code.split("\n") if "print(" in l][:2]
    files = "solve.py · %d บรรทัด" % code.count("\n") + ("<br>test_solve.py · %d เทสต์" % n_tests if tests else "<br>(ไม่มี test_solve.py)")
    c3 = col("#2A9D8F", "③", "Output", "ไฟล์ที่ Agent ส่ง",
             box(files, 16) + box(esc(sig[:60]) + "<br>&nbsp;&nbsp;…<br>" + "<br>".join(esc(l[:60]) for l in prints), 14), "1.3")

    # ④ Grade: 3 วิธี
    def split_note(n):
        head, _, tail = n.partition(" · พลาด")
        return [esc(head)] + (["พลาด" + esc(tail)] if tail else [])
    fn_bad = [k for k in ("policy", "reject_type", "reject_value", "no_drift", "half_up", "boundary", "basic", "contract") if k in bad]
    fn_checks = [c["id"] for c in g["checks"] if c["id"] not in ("cli_ok", "cli_error", "tests")]
    w1 = way("เรียกฟังก์ชันด้วย Input ที่ซ่อน", ["<b>%s</b>: " % fn_bad[0] + split_note(bad[fn_bad[0]])[0]] + split_note(bad[fn_bad[0]])[1:]
             + (["และไม่ผ่านอีก: " + " ".join(fn_bad[1:])] if fn_bad[1:] else []), False) if fn_bad else \
        way("เรียกฟังก์ชันด้วย Input ที่ซ่อน", ["ผ่านทุกข้อ: " + " ".join(fn_checks)], True)
    cli_bad = [k for k in ("cli_ok", "cli_error") if k in bad]
    if cli_bad:
        mm = re.match(r"stdin (.*) ต้องได้ (.*?) แต่ได้ (.*)$", bad[cli_bad[0]])
        lines = ["<b>%s</b> ส่ง: %s" % (cli_bad[0], esc(mm.group(1)[:90])), "ต้องได้: " + esc(mm.group(2)), "ได้: " + esc(mm.group(3)[:90])] if mm else [esc(bad[cli_bad[0]][:200])]
        w2 = way("รันเป็นโปรแกรม (JSON ทาง stdin)", lines + (["และไม่ผ่านอีก: " + " ".join(cli_bad[1:])] if cli_bad[1:] else []), False)
    else:
        w2 = way("รันเป็นโปรแกรม (JSON ทาง stdin)", ["ผ่านทั้ง cli_ok และ cli_error"], True)
    w3 = way("รันเทสต์ที่ Agent เขียน", ["python3 -m unittest → %d เทสต์ ผ่าน (ต้องมีอย่างน้อย 6)" % n_tests], True) if "tests" in ok else \
        way("รันเทสต์ที่ Agent เขียน", [esc(bad["tests"][:170])], False)
    c4 = col("#F4A261", "④", "Grade", "ตัวตรวจรันโค้ดที่ได้ 3 วิธี", w1 + w2 + w3, "2.2")

    chips = "".join("<span style='%s;font-size:19px;background:#E3F3DE;border:2px solid #6BBF59;color:#2F6B22;border-radius:10px;padding:2px 8px;margin-right:5px'>✓ %s</span>" % (MONO, c) for c in ok) \
        + "".join("<span style='%s;font-size:19px;background:#FBE3DC;border:2px solid #E76F51;color:#A63D25;border-radius:10px;padding:2px 8px;margin-right:5px'>✗ %s</span>" % (MONO, c) for c in bad)
    sm = "font-size:34px;color:#6F4E37;align-self:center;font-weight:800"
    ar = "<div style='%s'>➜</div>" % sm
    body = """<h1 style='font-size:42px'>1 Trial: จากโจทย์ สู่โค้ด สู่คะแนน</h1>
    <div class='sub' style='margin-bottom:10px'>ตัวอย่างจริง: รุ่น %s · โจทย์ %s · รอบที่ %s · บัญชี %s · โมเดล %s</div>
    <div style='display:flex;gap:5px;align-items:stretch'>%s%s%s%s%s%s%s</div>
    <div style='margin-top:10px;background:#fff;border:3px solid #E5D9CC;border-radius:18px;padding:10px 16px'>
      <span style='font-size:28px;font-weight:800;color:#4A2F1F'>⑤ Score = ข้อที่ผ่าน ÷ ข้อตรวจทั้งหมด = %d ÷ %d = %s</span>
      <div style='margin-top:6px;line-height:2'>%s</div></div>""" % (
        label, task_id, rep, m["account"], m["model"], c1, ar, c2, ar, c3, ar, c4, len(ok), len(g["checks"]), g["score"], chips)
    shot("d05-trial-" + task_id, body, 900)


def trial_examples(label="v0"):
    """ภาพ 1 Trial ของโจทย์ Training ทุกข้อ (รอบที่ 1) · โจทย์ Validation ถูกปิดผลรายข้อ จึงไม่มีภาพ"""
    import json
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    suite = json.load(open(os.path.join(root, "suite", "suite.json"), encoding="utf-8"))
    for x in suite["tasks"]:
        if x["split"] == "train":
            trial_example(label, x["id"] + "-r1")


LAB_FILES = [  # (LAB, ชื่อสั้น, รุ่นที่วัดใน LAB นี้, ไฟล์ที่ได้เพิ่ม, เอาไปใช้ต่ออย่างไร)
    ("LAB 0", "เตรียมเครื่องมือและโจทย์", None,
     ["my-skill-optimizer/|เครื่องมือ (บนเครื่อง)", "/workspace/sklab/suite/|โจทย์และตัวตรวจ (ใน container)", "/workspace/sklab/runs/v0/skills/|สกิลรุ่นแรก"],
     "ทุก LAB สั่งงานผ่านเครื่องมือนี้"),
    ("LAB 1", "การวัดผลตั้งต้น", "v0",
     ["runs/noskill/trials/|18 Trial แบบไม่มีสกิล", "runs/v0/trials/|18 Trial ของ v0", "runs/v0/gate.txt|ผลตัดสิน noskill → v0", "runs/report.md|ตารางเทียบทุกรุ่น"],
     "LAB 2 อ่านข้อที่ผิดของ v0 จาก trials/"),
    ("LAB 2", "ปรับรอบที่ 1: วิเคราะห์ข้อผิดพลาด", "v1",
     ["runs/ISSUES.md|ปัญหา สาเหตุ ทางแก้", "runs/v1/skills/|สกิลรุ่นใหม่", "runs/v1/trials/|18 Trial ของ v1", "runs/v1/gate.txt|ผลตัดสิน v0 → v1"],
     "ISSUES.md บอกปัญหาที่ยังเปิด → ถามทีมใน LAB 3"),
    ("LAB 3", "ปรับรอบที่ 2: เติมความรู้แฝงจากทีม", "v2",
     ["runs/v2/skills/|สกิล + นโยบายธุรกิจ", "runs/v2/trials/|18 Trial ของ v2", "runs/v2/gate.txt|ผลตัดสิน v1 → v2", "runs/ISSUES.md|ปิดปัญหา policy"],
     "Training เต็มแล้ว → LAB 4 ดูกติกาที่ยังกว้าง"),
    ("LAB 4", "ปรับรอบที่ 3: ทำกติกาให้ตรวจสอบได้", "v3",
     ["runs/v3/skills/|สกิลที่กติกาชัดขึ้น", "runs/v3/trials/|18 Trial ของ v3", "runs/v3/gate.txt|ผลตัดสิน v2 → v3"],
     "รุ่นที่ถูกรับเป็นรุ่นฐานของ LAB 5"),
    ("LAB 5", "การทดลองควบคุม: ย่อสกิลเพื่อลดต้นทุน", "v4",
     ["runs/v4/skills/|สกิลฉบับย่อ", "runs/v4/trials/|18 Trial ของ v4", "runs/v4/gate.txt|ผลตัดสินเทียบรุ่นฐาน"],
     "รุ่นที่ใช้งานจริง = รุ่นล่าสุดที่ถูกรับ"),
]


def lab_files():
    """หลังรันแต่ละ LAB ได้ไฟล์อะไร และเอาไปใช้ต่ออย่างไร · คะแนนและผลตัดสินอ่านจาก runs/ (รุ่นที่ยังไม่ได้รันจะไม่แสดงตัวเลข)"""
    import json
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rp = os.path.join(root, "runs", "results.json")
    R = json.load(open(rp, encoding="utf-8")) if os.path.isfile(rp) else {}
    cards = ""
    for i, (lab, name, ver, files, nxt) in enumerate(LAB_FILES):
        badge = ""
        if ver and ver in R:
            gp = os.path.join(root, "runs", ver, "gate.txt")
            verdict = ("ACCEPT" if "ACCEPT" in open(gp, encoding="utf-8").read() else "REJECT") if os.path.isfile(gp) else ""
            col = {"ACCEPT": "#6BBF59", "REJECT": "#E76F51", "": "#6F4E37"}[verdict]
            badge = ("<span style='float:right;font-size:20px;font-weight:800;color:#fff;background:%s;border-radius:10px;padding:2px 10px'>%s %.1f%% %s</span>"
                     % (col, ver, R[ver]["all"]["score"] * 100, verdict))
        rows = "".join("<div style='margin-bottom:3px'><span style='%s;font-size:17px;color:#2A6F68'>%s</span>"
                       "<span style='font-size:17px;color:#7A6557'> &nbsp;%s</span></div>" % (MONO, f.split("|")[0], f.split("|")[1]) for f in files)
        cards += """<div style='background:#fff;border:3px solid #E5D9CC;border-top:12px solid %s;border-radius:20px;padding:10px 14px'>
          <div style='font-size:24px;font-weight:800;color:#4A2F1F'>%s%s</div>
          <div style='font-size:19px;color:#7A6557;margin-bottom:6px'>%s</div>
          <div style='font-size:17px;font-weight:800;color:#6F4E37;margin-bottom:3px'>ได้ไฟล์เพิ่ม</div>%s
          <div style='margin-top:6px;background:#FFF4E0;border-radius:10px;padding:5px 9px;font-size:18px;color:#4A2F1F'><b>ใช้ต่อ ➜</b> %s</div></div>""" % (
            "#6F4E37" if i == 0 else "#2A9D8F", lab, badge, name, rows, nxt)
    body = """<h1 style='font-size:42px'>หลังรันแต่ละ LAB ได้ไฟล์อะไร และเอาไปใช้ต่ออย่างไร</h1>
    <div class='sub' style='margin-bottom:10px'>ทุกอย่างอยู่ในโฟลเดอร์ runs/ · 1 รุ่น = 1 โฟลเดอร์ · ป้ายขวาบน = คะแนนรวมและผลตัดสินของรุ่นที่วัดใน LAB นั้น</div>
    <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px'>%s</div>""" % cards
    shot("d06-lab-files", body, 900)


def skill_rules(version):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f = os.path.join(root, "runs", version, "skills", "money-coder", "SKILL.md")
    return [l[2:].strip() for l in open(f, encoding="utf-8").read().split("\n") if l.startswith("- ")], os.path.getsize(f)


def skill_diff(base="v0", cand="v1"):
    """สกิลเปลี่ยนอย่างไรระหว่างสองรุ่น · อ่านกติกา (บรรทัดที่ขึ้นต้นด้วย "- ") จาก SKILL.md ของทั้งสองรุ่นแล้วเทียบกัน"""
    import difflib, html, json, math
    esc = html.escape
    a, size_a = skill_rules(base)
    b, size_b = skill_rules(cand)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    R = json.load(open(os.path.join(root, "runs", "results.json"), encoding="utf-8"))
    gate = open(os.path.join(root, "runs", cand, "gate.txt"), encoding="utf-8").read()
    verdict = "ACCEPT" if "ACCEPT" in gate else "REJECT"
    CH = 125                                           # ตัวอักษรต่อบรรทัดโดยประมาณ ที่ขนาด 21px

    def lines(s):
        return max(1, math.ceil(len(s) / CH))

    def row(kind, text, n=None):
        style = {"same": ("#F3EEE7", "#E5D9CC", "#7A6557", "คงเดิม"), "old": ("#FBE3DC", "#E76F51", "#A63D25", "เดิม"),
                 "new": ("#E3F3DE", "#6BBF59", "#2F6B22", "ใหม่"), "add": ("#E3F3DE", "#6BBF59", "#2F6B22", "เพิ่ม")}[kind]
        deco = "text-decoration:line-through;" if kind == "old" else ""
        return ("<div style='display:flex;gap:10px;margin-bottom:6px'><div style='width:84px;flex:none;text-align:center;font-size:19px;font-weight:800;"
                "color:#fff;background:%s;border-radius:10px;padding:5px 0;align-self:flex-start'>%s</div>"
                "<div style='flex:1;background:%s;border:2px solid %s;border-radius:12px;padding:6px 12px;font-size:21px;line-height:1.42;color:%s;%soverflow-wrap:anywhere'>%s</div></div>"
                % (style[1] if kind != "same" else "#B9A999", style[3], style[0], style[1], style[2], deco, esc(text)))

    body, h, n_change = "", 0, 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            for s in a[i1:i2]:
                short = s if len(s) <= 96 else s[:94] + " …"
                body += row("same", short)
                h += 48
        else:
            olds, news = a[i1:i2], b[j1:j2]
            for k in range(max(len(olds), len(news))):
                if k < len(olds):
                    short = olds[k] if len(olds[k]) <= 192 else olds[k][:190] + " …"
                    body += row("old", short)
                    h += 18 + 30 * lines(short)
                if k < len(news):
                    body += row("new" if k < len(olds) else "add", news[k])
                    h += 18 + 30 * lines(news[k])
                    n_change += 1
                body += "<div style='height:6px'></div>"
                h += 6
    sb, sc = R[base]["all"]["score"] * 100, R[cand]["all"]["score"] * 100
    col = "#6BBF59" if verdict == "ACCEPT" else "#E76F51"
    head = """<h1 style='font-size:40px'>สกิลเปลี่ยนอย่างไร: %s → %s</h1>
    <div class='sub' style='margin-bottom:12px'>กติกา %d ข้อ → %d ข้อ · เปลี่ยน %d จุด · ขนาดไฟล์ %s → %s ไบต์ ·
      คะแนนรวม %.1f%% → %.1f%% <span class='badge' style='background:%s;font-size:21px;padding:3px 12px'>%s</span></div>""" % (
        base, cand, len(a), len(b), n_change, format(size_a, ","), format(size_b, ","), sb, sc, col, verdict)
    shot("d07-skill-diff-%s-%s" % (base, cand), head + body, 215 + h)


def skill_diffs():
    for base, cand in (("v0", "v1"), ("v1", "v2"), ("v2", "v3"), ("v3", "v4")):
        skill_diff(base, cand)


def skill_full(version="v0"):
    """สกิลทั้งไฟล์ของ 1 รุ่น · อ่านจาก runs/<รุ่น>/skills/money-coder/SKILL.md · รุ่น noskill ไม่มีไฟล์ จึงแสดงสิ่งที่ Agent ได้รับแทน"""
    import html, json, math, re
    esc = html.escape
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    R = json.load(open(os.path.join(root, "runs", "results.json"), encoding="utf-8"))
    a = R[version]
    gp = os.path.join(root, "runs", version, "gate.txt")
    verdict = ("ACCEPT" if "ACCEPT" in open(gp, encoding="utf-8").read() else "REJECT") if os.path.isfile(gp) else ""
    col = {"ACCEPT": "#6BBF59", "REJECT": "#E76F51", "": "#6F4E37"}[verdict]
    badge = "<span class='badge' style='background:%s;font-size:21px;padding:3px 12px'>%s</span>" % (col, verdict) if verdict else ""
    score = "Training %.1f%% · Validation %.1f%% · รวม <b>%.1f%%</b> %s" % (
        a["train"]["score"] * 100, a["val"]["score"] * 100, a["all"]["score"] * 100, badge)
    f = os.path.join(root, "runs", version, "skills", "money-coder", "SKILL.md")
    CH = 130
    if not os.path.isfile(f):
        body = """<h1 style='font-size:40px'>ไม่มีสกิล (รุ่น noskill)</h1>
        <div class='sub' style='margin-bottom:14px'>%s</div>
        <div style='background:#fff;border:3px dashed #B9A999;border-radius:18px;padding:22px 26px;font-size:26px;color:#7A6557;line-height:1.6'>
          โฟลเดอร์ <span style='%s;color:#2A6F68'>./skills</span> ว่าง · Agent ได้รับแค่โจทย์ 1 ข้อ<br>
          ไม่มีใครบอกมาตรฐานการเขียนโค้ดของร้าน และไม่มีใครบอกนโยบายธุรกิจ</div>""" % (score, MONO)
        shot("d08-skill-noskill", body, 330)
        return
    src = open(f, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", src, re.S)
    front = dict(l.split(":", 1) for l in m.group(1).split("\n") if ":" in l)
    rest = src[m.end():]
    rules = [l[2:].strip() for l in rest.split("\n") if l.startswith("- ")]
    intro = [l.strip() for l in rest.split("\n") if l.strip() and not l.startswith("- ") and not l.startswith("#")]
    h = 0
    cards = ""
    for i, r in enumerate(rules, 1):
        n = max(1, math.ceil(len(r) / CH))
        h += 22 + 30 * n
        cards += ("<div style='display:flex;gap:10px;margin-bottom:6px'><div style='width:44px;flex:none;text-align:center;font-size:22px;font-weight:800;"
                  "color:#fff;background:#2A9D8F;border-radius:10px;padding:5px 0;align-self:flex-start'>%d</div>"
                  "<div style='flex:1;background:#fff;border:2px solid #E5D9CC;border-radius:12px;padding:6px 12px;font-size:21px;line-height:1.42;"
                  "color:#3B2A20;overflow-wrap:anywhere'>%s</div></div>" % (i, esc(r)))
    desc = front.get("description", "").strip()
    head = """<h1 style='font-size:40px'>สกิล money-coder รุ่น %s (ทั้งไฟล์)</h1>
    <div class='sub' style='margin-bottom:10px'>กติกา %d ข้อ · %s ไบต์ · %s</div>
    <div style='background:#F6EFE6;border-radius:12px;padding:8px 14px;margin-bottom:8px;font-size:19px;color:#7A6557;line-height:1.45'>
      <span style='%s;color:#2A6F68'>description:</span> %s<br>%s</div>""" % (
        version, len(rules), format(os.path.getsize(f), ","), score, MONO, esc(desc), esc(" ".join(intro)))
    shot("d08-skill-" + version, head + cards, 250 + 30 * math.ceil(len(desc) / 120) + h)


def skill_fulls():
    for v in ("noskill", "v0", "v1", "v2", "v3", "v4"):
        skill_full(v)


if __name__ == "__main__":
    which = sys.argv[1:] or ["pipeline", "grader", "examples", "algorithm", "trial_examples", "lab_files", "skill_diffs", "skill_fulls"]
    for w in which:
        globals()[w]()
