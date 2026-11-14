#!/usr/bin/env python3
"""วาดแผนภาพของภาค LAB เป็น PNG ลง img/

  python tools/lab_diagrams.py [ชื่อภาพ ...]      (รันบนเครื่อง จากโฟลเดอร์ของบท · ใช้ Chrome headless)

ตัวเลขและข้อความของภาพที่มาจากการรันจริงอ่านจาก runs/ (state.json · results.json · wiki/ · skills/) ไม่มีค่าที่พิมพ์เอง
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import ROOT, RAW, WIKI, SKILL, GATE, BAD, INK, MUTE, LINE, MONO, shot, card, arrow, e


def pct(x):
    return "%.1f%%" % (x * 100)


def state(ws):
    return json.load(open(os.path.join(ROOT, "runs", ws, "state.json"), encoding="utf-8"))


def results():
    return json.load(open(os.path.join(ROOT, "runs", "results.json"), encoding="utf-8"))


def read(*parts):
    return open(os.path.join(ROOT, *parts), encoding="utf-8").read()


def has(ws):
    return os.path.isfile(os.path.join(ROOT, "runs", ws, "state.json"))


# ------------------------------------------------------------------ d02 สร้างสกิล wikiskill ใน 6 ขั้น (LAB 0.1)
def build_skill():
    steps = [("1 ศึกษา", "อ่านเปเปอร์ แล้วสรุป<br>3 ชั้น · 4 ส่วนประกอบ<br>Algorithm 1"),
             ("2 ออกแบบ", "<span class='mono'>references/<br>source.md</span><br>ส่วนของสกิล มาจาก<br>ข้อไหนของเปเปอร์"),
             ("3 สร้าง", "<span class='mono'>scripts/<br>wikiskill.py</span><br>8 คำสั่ง ตามรูปแบบ"),
             ("4 เขียน", "<span class='mono'>prompts/</span> 3 ไฟล์<br><span class='mono'>SKILL.md</span><br><span class='mono'>references/<br>workspace.md</span>"),
             ("5 ทดสอบ", "ไม่เรียกโมเดล<br>status · Apply<br>วงรอบจำลอง 2 รอบ"),
             ("6 รายงาน", "ตาราง ไฟล์ | หน้าที่<br>และผลทดสอบ 3 ข้อ")]
    cols = [INK, WIKI, RAW, SKILL, GATE, INK]
    steps = [(t, b.replace("class='mono'", "class='mono' style='font-size:19px;color:#2A6F68'")) for t, b in steps]
    cards = "".join(card(c, t, "", b, "padding:14px 14px;min-height:210px") for (t, b), c in zip(steps, cols))
    cards = "<div style='display:grid;grid-template-columns:repeat(6,1fr);gap:12px;width:100%%'>%s</div>" % cards
    body = """<h1>LAB 0.1 · สร้างสกิล wikiskill ใน 6 ขั้น</h1>
    <div class='sub'>พรอมต์เดียว ให้ Claude Code สร้างเครื่องมือจากเปเปอร์และไฟล์รูปแบบ · ทำบนเครื่อง ไม่ใช้ container และไม่เรียกโมเดลอื่น</div>
    <div class='row' style='gap:14px;margin-bottom:18px'>
      <div class='card' style='flex:1;border-left:14px solid %s'><div style='font-size:24px;color:%s'>ที่มา</div>
        <div style='font-size:28px;font-weight:800'>เปเปอร์ WikiSkill (arXiv:2608.27454)</div><div class='note'>และสรุปภาษาไทยใน 01_theory/</div></div>
      <div class='card' style='flex:1;border-left:14px solid %s'><div style='font-size:24px;color:%s'>รูปแบบที่ต้องทำตาม</div>
        <div class='mono' style='font-size:28px;font-weight:800'>wikiskill_format.md</div><div class='note'>โฟลเดอร์งาน · คำสั่ง · ไฟล์ของ 3 ชั้น · กติกาของวงรอบ</div></div>
    </div>
    <div class='row' style='gap:6px'>%s</div>
    <div class='card' style='margin-top:18px;border:4px dashed %s;background:#F1FAF8'>
      <span style='font-size:28px;font-weight:800;color:%s'>ผลที่ได้:</span>
      <span class='mono' style='font-size:27px'> my-wikiskill/ </span>
      <span style='font-size:26px'>→ ติดตั้งใน container เป็น global skill ชื่อ <b class='mono'>wikiskill</b> (LAB 0.2)</span></div>""" % (
        INK, MUTE, WIKI, MUTE, cards, WIKI, INK)
    shot("img/d02-build-skill.png", body, 660)


# ------------------------------------------------------------------ d01 โจทย์ใน 1 ภาพ (ชุดเดียวกับบท 05)
def problem():
    def li(items, size=23):
        return "".join("<div style='font-size:%dpx;line-height:1.45;padding:2px 0'>%s</div>" % (size, x) for x in items)
    body = """<h1>โจทย์เดิมของบท 05: AI ได้รับข้อมูลไม่ครบ</h1>
    <div class='sub'>ร้าน BaanKafe ให้ AI เขียนฟังก์ชันคิดเงิน · โจทย์บอกแค่ข้อกำหนดที่ระบุชัด ส่วนความรู้แฝงของทีมไม่มีใครเขียนให้</div>
    <div class='row' style='gap:18px;align-items:stretch'>
      <div class='card' style='flex:1;border-top:14px solid %s'>
        <div style='font-size:29px;font-weight:800'>Agent ได้รับ</div>
        <div style='font-size:22px;color:%s;margin:2px 0 8px'>ข้อกำหนดที่ระบุชัด (Explicit Requirement)</div>
        %s</div>
      <div class='card' style='flex:1.25;border-top:14px solid %s'>
        <div style='font-size:29px;font-weight:800'>Agent ไม่ได้รับ</div>
        <div style='font-size:22px;color:%s;margin:2px 0 8px'>ความรู้แฝงของทีม (Tacit Knowledge)</div>
        <div style='font-size:23px;font-weight:800;color:%s'>กลุ่ม 1 · มาตรฐานการเขียนโค้ด 5 ข้อ (ทุกงาน)</div>%s
        <div style='font-size:23px;font-weight:800;color:%s;margin-top:8px'>กลุ่ม 2 · นโยบายธุรกิจ 4 ข้อ (ค่าส่ง · เงินคืน)</div>%s</div>
      <div class='card' style='flex:0.9;border-top:14px solid %s'>
        <div style='font-size:29px;font-weight:800'>ตัวตรวจ (Grader)</div>
        <div style='font-size:22px;color:%s;margin:2px 0 8px'>รู้ครบทั้งสองประเภท</div>
        %s</div>
    </div>
    <div class='card' style='margin-top:18px;border:4px dashed %s;background:#FFF6EC'>
      <div style='font-size:27px;line-height:1.5'><b>สิ่งเดียวที่ปรับได้ = สกิล</b> (คู่มือที่ Agent อ่านก่อนเขียนโค้ด) ·
      บท 05: คนเขียนสกิลรุ่นแรก แล้วปรับทีละรุ่น · <b>บทนี้: เริ่มจากไม่มีสกิล ให้ WikiSkill สร้างเอง</b></div></div>""" % (
        GATE, MUTE, li(["งานนี้ต้องคำนวณอะไร", "เช่น <span class='mono'>gold</span> ได้เงินคืน 2.5%", "ซื้อไม่ถึง 100 บาท ไม่ได้เงินคืน", "เดือนเกิด ได้เงินคืน 2 เท่า"]),
        BAD, MUTE, INK, li(["1 เงินเป็นจำนวนเต็มสตางค์", "2 ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย", "3 ข้อมูลผิดต้อง <span class='mono'>ValueError</span>",
                            "4 รันเป็นโปรแกรม รับและตอบ JSON", "5 มีเทสต์อย่างน้อย 6 ข้อ"], 22),
        INK, li(["S1 รับเองที่ร้าน ไม่คิดค่าส่ง · S2 ส่งด่วนไม่เกิน 20 กก.", "C1 เดือนเกิด 2 เท่า เฉพาะ gold และ platinum · C2 เงินคืนปัดลง"], 21),
        INK, MUTE, li(["รันโค้ดที่ Agent เขียน", "กับ Input ที่ซ่อนไว้", "ตรวจ <b>10 หรือ 11 ข้อ</b>ต่องาน", "คะแนน = ข้อที่ผ่าน ÷ ข้อทั้งหมด"]), SKILL)
    shot("img/d01-problem.png", body, 790)


# ------------------------------------------------------------------ d03 แผนที่ของภาค LAB
LABS = [("0", INK, "สร้างเครื่องมือ", "สร้างสกิล <span class='mono'>wikiskill</span> จากเปเปอร์<br>ติดตั้งใน container"),
        ("1", WIKI, "รันทีละขั้น", "workspace <span class='mono'>w1</span><br>ดู 3 ชั้นเปลี่ยนทีละขั้น"),
        ("2", GATE, "วัดสกิลที่ได้", "โจทย์ 9 ข้อ เทียบกับ<br>ไม่มีสกิล และ <span class='mono'>v3</span> ของบท 05"),
        ("3", RAW, "รันซ้ำ", "workspace <span class='mono'>w2</span> ค่าเดิมทุกค่า<br>ผลซ้ำได้แค่ไหน"),
        ("4", BAD, "ตัด Wiki ออก", "workspace <span class='mono'>n1</span><br>การทดลองตัดส่วนประกอบ"),
        ("5", SKILL, "เติมความรู้จากทีม", "รุ่น <span class='mono'>w1p</span> และ <span class='mono'>w1q</span><br>ต่อยอดด้วยวิธีของบท 05")]


def lab_map():
    cards = "".join("""<div class='card' style='border-top:14px solid %s;padding:14px 16px;min-height:200px'>
      <div style='font-size:22px;color:%s'>LAB %s</div><div style='font-size:29px;font-weight:800;line-height:1.2'>%s</div>
      <div style='font-size:22px;color:%s;line-height:1.4;margin-top:8px'>%s</div></div>""" % (c, MUTE, n, t, MUTE, b) for n, c, t, b in LABS)
    body = """<h1>ภาค LAB · ลงมือทำ 6 ขั้น</h1>
    <div class='sub'>ทุก LAB = คัดลอกพรอมต์ 1 กล่อง → วางใน Claude Code Desktop → อ่านผล · LAB 1–4 ไม่มีคนเขียนหรือแก้สกิล</div>
    <div style='display:grid;grid-template-columns:repeat(6,1fr);gap:12px'>%s</div>""" % cards
    shot("img/d03-lab-map.png", body, 430)


# ------------------------------------------------------------------ d04 สารบัญของ Wiki (ไฟล์จริง)
def wiki_index(ws="w1"):
    st = state(ws)
    lines = [l for l in read("runs", ws, "wiki", "index.md").split("\n") if l.startswith("- [")]
    rows = ""
    for l in lines:
        m = re.match(r"- \[([^\]]+)\]\([^)]*\):?\s*(.*)", l)
        name, desc = m.group(1), m.group(2)
        desc = desc if len(desc) <= 230 else desc[:228] + "…"
        rows += """<tr><td style='border-left:14px solid %s;width:400px;vertical-align:top'><b class='mono' style='font-size:22px'>%s</b></td>
          <td style='font-size:21px;line-height:1.4'>%s</td></tr>""" % (WIKI, e(name), e(desc))
    body = """<h1>สมุดความรู้ของ %s เมื่อจบ: wiki/index.md</h1>
    <div class='sub'>ไฟล์จริงที่ Wiki Maintainer เขียน · 1 บรรทัดต่อ 1 pattern บอก ปัญหา สาเหตุ และวิธีแก้ · Skill Proposer เห็นสารบัญนี้ก่อน แล้วเลือกเปิดหน้าเต็มเอง</div>
    <table class='t'><tr><th>pattern (%d หน้า)</th><th>บรรทัดในสารบัญ</th></tr>%s</table>""" % (ws, len(lines), rows)
    shot("img/d04-wiki-%s.png" % ws, body, 225 + 91 * len(lines))


# ------------------------------------------------------------------ d05 สกิลทั้งไฟล์ (ไฟล์จริง)
def skill_full(ws="w1", out=None, title=None):
    d = os.path.join(ROOT, "runs", ws, "skills")
    name = sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n, "SKILL.md")))[0]
    txt = read("runs", ws, "skills", name, "SKILL.md").rstrip("\n")
    nlines = txt.count("\n") + 1
    wrapped = sum(1 + len(l) // 78 for l in txt.split("\n"))
    body = """<h1>%s</h1>
    <div class='sub'><span class='mono'>runs/%s/skills/%s/SKILL.md</span> · %d บรรทัด · %s ไบต์ · ไฟล์จริงทั้งไฟล์ ไม่มีคนเขียนหรือแก้</div>
    <div class='card' style='border-top:14px solid %s;padding:18px 22px'>
      <pre style='margin:0;column-count:2;column-gap:36px;white-space:pre-wrap;word-break:break-word;font-family:Consolas,"Leelawadee UI",monospace;font-size:15.5px;line-height:1.42;color:#3B2A20'>%s</pre></div>""" % (
        title or "สกิลที่ WikiSkill สร้าง (%s) ทั้งไฟล์" % ws, ws, name, nlines,
        format(len(txt.encode("utf-8")), ","), SKILL, e(txt))
    shot(out or "img/d05-skill-%s.png" % ws, body, 215 + int(wrapped / 2 * 22.2))


# ------------------------------------------------------------------ r05 ความรู้แฝงข้อใดที่สกิลแต่ละชุดครอบคลุม (Training Set)
CHECKS = [("contract", "รูปแบบของฟังก์ชัน", "ข้อกำหนดที่ระบุชัด"), ("basic", "กรณีปกติ", "ข้อกำหนดที่ระบุชัด"),
          ("boundary", "ค่าขอบของเงื่อนไข", "ข้อกำหนดที่ระบุชัด"),
          ("no_drift", "1 เงินเป็นจำนวนเต็มสตางค์", "มาตรฐานการเขียนโค้ด"), ("half_up", "2 ปัดครึ่งขึ้น ครั้งเดียว", "มาตรฐานการเขียนโค้ด"),
          ("reject_value", "3 ปฏิเสธค่าที่ผิด", "มาตรฐานการเขียนโค้ด"), ("reject_type", "3 ปฏิเสธชนิดที่ผิด", "มาตรฐานการเขียนโค้ด"),
          ("cli_ok", "4 รันเป็นโปรแกรม (สำเร็จ)", "มาตรฐานการเขียนโค้ด"), ("cli_error", "4 รันเป็นโปรแกรม (ข้อมูลผิด)", "มาตรฐานการเขียนโค้ด"),
          ("tests", "5 มีเทสต์อย่างน้อย 6 ข้อ", "มาตรฐานการเขียนโค้ด"), ("policy", "นโยบายธุรกิจ 4 ข้อ", "นโยบายธุรกิจ")]


def coverage(labels=None, out="img/r05-coverage.png"):
    """labels = [(ป้ายใน results.json, ชื่อที่แสดง, คำอธิบาย)]"""
    R = results()
    labels = [l for l in (labels or [("noskill", "ไม่มีสกิล", ""), ("w1", "w1", "WikiSkill · ไม่มีคนเขียน"),
                                     ("so-v3", "v3 ของบท 05", "คนเขียนและบอกนโยบาย"),
                                     ("w1p", "w1p", "LAB 5.1 · นโยบายเขียนกว้าง"), ("w1q", "w1q", "LAB 5.2 · นโยบายมีขอบเขต")]) if l[0] in R]
    th = "".join("<th style='text-align:center;font-size:23px;color:%s'><b>%s</b><br><span style='font-size:19px'>%s</span></th>" % (INK, n, d) for _, n, d in labels)
    tr, last = "", None
    for cid, name, group in CHECKS:
        cells = ""
        for lb, _, _ in labels:
            v = (R[lb]["train"].get("checks") or {}).get(cid)
            if not v:
                cells += "<td style='text-align:center;color:%s'>–</td>" % MUTE
                continue
            a, b = [int(x) for x in v.split("/")]
            r = a / b if b else 0
            col = GATE if r >= 0.999 else (BAD if r <= 0.34 else SKILL)
            cells += "<td style='text-align:center'><span class='badge' style='background:%s;min-width:110px'>%s</span></td>" % (col, v)
        gcol = {"ข้อกำหนดที่ระบุชัด": GATE, "มาตรฐานการเขียนโค้ด": INK, "นโยบายธุรกิจ": BAD}[group]
        tr += "<tr><td style='border-left:14px solid %s;width:230px;font-size:20px;color:%s'>%s</td><td style='width:400px'><b>%s</b> <span class='mono' style='font-size:19px;color:%s'>%s</span></td>%s</tr>" % (
            gcol, MUTE, group if group != last else "", name, MUTE, cid, cells)
        last = group
    body = """<h1>สกิลแต่ละชุดครอบคลุมความรู้ข้อใด (Training Set)</h1>
    <div class='sub'>จำนวน Trial ที่ผ่านข้อตรวจนั้น จาก 12 Trial (ข้อตรวจที่มีเฉพาะบางโจทย์มีตัวหารน้อยกว่า) · ผลจริงจาก <span class='mono'>runs/results.json</span> ·
      <span class='badge gate'>ผ่านครบ</span> <span class='badge skill'>ผ่านบางส่วน</span> <span class='badge bad'>ไม่ผ่าน</span></div>
    <table class='t' style='border-spacing:0 5px'><tr><th>ประเภท</th><th>ข้อตรวจ</th>%s</tr>%s</table>""" % (th, tr)
    shot(out, body, 345 + 72 * len(CHECKS))


if __name__ == "__main__":
    for w in sys.argv[1:] or ["problem", "build_skill", "lab_map"]:
        globals()[w]()
