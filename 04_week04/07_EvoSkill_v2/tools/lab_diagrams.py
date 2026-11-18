#!/usr/bin/env python3
"""วาดแผนภาพของภาค LAB เป็น PNG ลง img/

  python tools/lab_diagrams.py [ชื่อภาพ ...]      (รันบนเครื่อง จากโฟลเดอร์ของบท · ใช้ Chrome headless)

ตัวเลขและข้อความของภาพที่มาจากการรันจริงอ่านจาก runs/ (state.json · skills_vK/ · legs/runs/*/trials/*/grade.json) ไม่มีค่าที่พิมพ์เอง
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import ROOT, USER, ADAPT, SOLVER, EVOLVER, FILE, BAD, INK, MUTE, shot, card, e


def state(run):
    return json.load(open(os.path.join(ROOT, "runs", run, "state.json"), encoding="utf-8"))


def has(run):
    return os.path.isfile(os.path.join(ROOT, "runs", run, "state.json"))


def pct(x):
    return "%.1f%%" % (x * 100)


# ------------------------------------------------------------------ d02 สร้างสกิล evoskill ใน 6 ขั้น (LAB 0.1)
def build_skill():
    steps = [("1 ศึกษา", "อ่านเปเปอร์ แล้วสรุป<br>Agent 3 ตัว · ใครเห็นอะไร<br>ลำดับของ 1 การรัน"),
             ("2 ออกแบบ", "<span class='mono'>references/<br>source.md</span><br>ส่วนของสกิล มาจาก<br>ข้อไหนของเปเปอร์"),
             ("3 สร้าง", "<span class='mono'>scripts/<br>evoskill.py</span><br>12 คำสั่ง ตามรูปแบบ"),
             ("4 เขียน", "<span class='mono'>prompts/</span> 3 ไฟล์<br><span class='mono'>SKILL.md</span><br><span class='mono'>references/<br>workspace.md</span>"),
             ("5 ทดสอบ", "ไม่เรียกโมเดล<br>status และ noise<br>การรันจำลอง 2 epochs<br>การรั่วและการล็อก"),
             ("6 รายงาน", "ตาราง ไฟล์ | หน้าที่<br>และผลทดสอบ 3 ข้อ")]
    cols = [INK, EVOLVER, USER, SOLVER, ADAPT, INK]
    steps = [(t, b.replace("class='mono'", "class='mono' style='font-size:19px;color:#2A6F68'")) for t, b in steps]
    cards = "".join(card(c, t, "", b, "padding:14px 14px;min-height:230px") for (t, b), c in zip(steps, cols))
    cards = "<div style='display:grid;grid-template-columns:repeat(6,1fr);gap:12px;width:100%%'>%s</div>" % cards
    body = """<h1>LAB 0.1 · สร้างสกิล evoskill ใน 6 ขั้น</h1>
    <div class='sub'>พรอมต์เดียว ให้ Claude Code สร้างเครื่องมือจากเปเปอร์และไฟล์รูปแบบ · ทำบนเครื่อง ไม่ใช้ container และไม่เรียกโมเดลอื่น</div>
    <div class='row' style='gap:14px;margin-bottom:18px'>
      <div class='card' style='flex:1;border-left:14px solid %s'><div style='font-size:24px;color:%s'>ที่มา</div>
        <div style='font-size:28px;font-weight:800'>เปเปอร์ EvoSkill v2 (arXiv:2610.25931)</div><div class='note'>และสรุปภาษาไทยใน 01_theory/</div></div>
      <div class='card' style='flex:1;border-left:14px solid %s'><div style='font-size:24px;color:%s'>รูปแบบที่ต้องทำตาม</div>
        <div class='mono' style='font-size:28px;font-weight:800'>evoskill_format.md</div><div class='note'>โฟลเดอร์งาน · คำสั่ง · ไฟล์ของ 1 การรัน · กติกาของวงรอบ</div></div>
      <div class='card' style='flex:1;border-left:14px solid %s'><div style='font-size:24px;color:%s'>ใช้ร่วมกับ</div>
        <div class='mono' style='font-size:28px;font-weight:800'>my-skill-optimizer/</div><div class='note'>เครื่องมือของบท 05 ที่รัน rollout ของ Solver</div></div>
    </div>
    <div class='row' style='gap:6px'>%s</div>
    <div class='card' style='margin-top:18px;border:4px dashed %s;background:#F1FAF8'>
      <span style='font-size:28px;font-weight:800;color:%s'>ผลที่ได้:</span>
      <span class='mono' style='font-size:27px'> my-evoskill/ </span>
      <span style='font-size:26px'>→ ติดตั้งใน container เป็น global skill ชื่อ <b class='mono'>evoskill</b> (LAB 0.2)</span></div>""" % (
        INK, MUTE, EVOLVER, MUTE, SOLVER, MUTE, cards, EVOLVER, INK)
    shot("img/d02-build-skill.png", body)


# ------------------------------------------------------------------ d03 แผนที่ของภาค LAB
LABS = [("0", INK, "สร้างเครื่องมือ", "สร้างสกิล <span class='mono'>evoskill</span> จากเปเปอร์<br>แล้วติดตั้งใน container"),
        ("1", ADAPT, "เตรียมสนาม", "การรัน <span class='mono'>e1</span> · Benchmark Adaptor<br>ล็อก และตรวจการรั่ว"),
        ("2", EVOLVER, "รันจนจบ", "การรัน <span class='mono'>e1</span> · ดู Evolver ทีละตา<br>แล้ววัด Test Set"),
        ("3", USER, "บอกเพิ่ม 1 ประโยค", "การรัน <span class='mono'>n1</span> · ผู้ใช้เติมข้อความ<br>ในโฟลเดอร์ reference"),
        ("4", BAD, "เห็นแต่คะแนน", "การรัน <span class='mono'>p1</span> · Evolver ไม่ได้เห็น<br>เฉลยของชุดใดเลย"),
        ("5", FILE, "ตัดความจำ", "การรัน <span class='mono'>f1</span><br>เซสชันใหม่ทุก epoch"),
        ("6", SOLVER, "โมเดลเล็ก", "การรัน <span class='mono'>h1</span> · haiku เป็นทั้ง<br>Solver และ Evolver"),
        ("7", INK, "ความแกว่ง", "ไม่ใช้โทเคน · ถ้ามีประตูรับ<br>จะเกิดอะไรขึ้น")]


def lab_map():
    cards = "".join("""<div class='card' style='border-top:14px solid %s;padding:14px 18px;min-height:150px'>
      <div style='font-size:22px;color:%s'>LAB %s</div><div style='font-size:30px;font-weight:800;line-height:1.2'>%s</div>
      <div style='font-size:22px;color:%s;line-height:1.4;margin-top:8px'>%s</div></div>""" % (c, MUTE, n, t, MUTE, b) for n, c, t, b in LABS)
    body = """<h1>ภาค LAB · ลงมือทำ 8 ขั้น</h1>
    <div class='sub'>ทุก LAB = คัดลอกพรอมต์ 1 กล่อง → วางใน Claude Code Desktop → อ่านผล · LAB 1–6 ไม่มีคนเขียนหรือแก้สกิล</div>
    <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:14px'>%s</div>""" % cards
    shot("img/d03-lab-map.png", body)


# ------------------------------------------------------------------ d05 สกิลทั้งไฟล์ (ไฟล์จริง)
def skill_full(run="e1", k=None):
    st = state(run)
    k = k or st["epochs"]
    d = os.path.join(ROOT, "runs", run, "skills_v%d" % k)
    names = sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n, "SKILL.md")))
    blocks, total = "", 0
    for name in names:
        txt = open(os.path.join(d, name, "SKILL.md"), encoding="utf-8").read().rstrip("\n")
        total += len(txt.encode("utf-8"))
        others = sorted(f for f in os.listdir(os.path.join(d, name)) if f != "SKILL.md")
        blocks += """<div class='card' style='border-top:14px solid %s;padding:16px 20px;margin-bottom:16px'>
          <div class='mono' style='font-size:24px;font-weight:800;margin-bottom:8px'>%s/SKILL.md <span style='font-weight:400;color:%s;font-size:20px'>%d บรรทัด%s</span></div>
          <pre style='margin:0;column-count:2;column-gap:36px;white-space:pre-wrap;word-break:break-word;font-family:Consolas,"Leelawadee UI",monospace;font-size:15px;line-height:1.42;color:#3B2A20'>%s</pre></div>""" % (
            EVOLVER, e(name), MUTE, txt.count("\n") + 1, (" · ไฟล์แนบ: " + ", ".join(others)) if others else "", e(txt))
    body = """<h1>ชุดสกิลที่ Evolver เขียน (%s · skills_v%d) ทั้งไฟล์</h1>
    <div class='sub'><span class='mono'>runs/%s/skills_v%d/</span> · สกิล %d ตัว · SKILL.md รวม %s ไบต์ · ไฟล์จริง ไม่มีคนเขียนหรือแก้</div>%s""" % (
        run, k, run, k, len(names), format(total, ","), blocks)
    shot("img/d05-skill-%s.png" % run, body)


# ------------------------------------------------------------------ r05 ข้อตรวจใดผ่าน (อ่านจาก grade.json ของ rollout ที่เก็บไว้)
CHECKS = [("contract", "รูปแบบของฟังก์ชัน", "ข้อกำหนดที่ระบุชัด"), ("basic", "กรณีปกติ", "ข้อกำหนดที่ระบุชัด"),
          ("boundary", "ค่าขอบของเงื่อนไข", "ข้อกำหนดที่ระบุชัด"),
          ("no_drift", "1 เงินเป็นจำนวนเต็มสตางค์", "มาตรฐานการเขียนโค้ด"), ("half_up", "2 ปัดครึ่งขึ้น ครั้งเดียว", "มาตรฐานการเขียนโค้ด"),
          ("reject_value", "3 ปฏิเสธค่าที่ผิด", "มาตรฐานการเขียนโค้ด"), ("reject_type", "3 ปฏิเสธชนิดที่ผิด", "มาตรฐานการเขียนโค้ด"),
          ("cli_ok", "4 รันเป็นโปรแกรม (สำเร็จ)", "มาตรฐานการเขียนโค้ด"), ("cli_error", "4 รันเป็นโปรแกรม (ข้อมูลผิด)", "มาตรฐานการเขียนโค้ด"),
          ("tests", "5 มีเทสต์อย่างน้อย 6 ข้อ", "มาตรฐานการเขียนโค้ด"), ("policy", "นโยบายธุรกิจ 4 ข้อ", "นโยบายธุรกิจ")]


def leg_checks(run, leg):
    """ข้อตรวจ -> (ผ่าน, ทั้งหมด) ของ leg นั้น · อ่านจาก grade.json ของทุก rollout"""
    out = {}
    for g in glob.glob(os.path.join(ROOT, "runs", run, "legs", "runs", leg, "trials", "*", "grade.json")):
        ch = json.load(open(g, encoding="utf-8")).get("checks")
        for c in ch if isinstance(ch, list) else []:
            a, b = out.get(c["id"], (0, 0))
            out[c["id"]] = (a + (1 if c["pass"] else 0), b + 1)
    return out


def coverage(runs=None, split="train", out=None):
    """ตาราง ข้อตรวจ x การรัน: split=train ใช้ leg v2_train (ชุดสกิลของ epoch 2) · split=test ใช้ leg vE_test"""
    runs = [r for r in (runs or ["e1", "n1", "p1", "f1", "h1"]) if has(r)]
    cols = []
    for r in runs:
        st = state(r)
        cols.append((r, ("v%d_train" % (st["epochs"] - 1)) if split == "train" else "v%d_test" % st["epochs"]))
    data = [("ไม่มีสกิล (%s)" % runs[0], leg_checks(runs[0], "base_" + split))] + [(r, leg_checks(r, leg)) for r, leg in cols]
    th = "".join("<th style='text-align:center;font-size:23px;color:%s'><b>%s</b></th>" % (INK, n) for n, _ in data)
    tr, last = "", None
    for cid, name, group in CHECKS:
        if not any(cid in d for _, d in data):
            continue
        cells = ""
        for _, d in data:
            if cid not in d:
                cells += "<td style='text-align:center;color:%s'>–</td>" % MUTE
                continue
            a, b = d[cid]
            r = a / b if b else 0
            col = ADAPT if r >= 0.999 else (BAD if r <= 0.34 else SOLVER)
            cells += "<td style='text-align:center'><span class='badge' style='background:%s;min-width:100px'>%d/%d</span></td>" % (col, a, b)
        gcol = {"ข้อกำหนดที่ระบุชัด": ADAPT, "มาตรฐานการเขียนโค้ด": INK, "นโยบายธุรกิจ": BAD}[group]
        tr += "<tr><td style='border-left:14px solid %s;width:215px;font-size:20px;color:%s'>%s</td><td style='width:390px'><b>%s</b> <span class='mono' style='font-size:19px;color:%s'>%s</span></td>%s</tr>" % (
            gcol, MUTE, group if group != last else "", name, MUTE, cid, cells)
        last = group
    title = "ชุดสกิลของแต่ละการรันผ่านข้อตรวจใด · " + ("Training Set (ชุดสกิลของ epoch 2)" if split == "train" else "Test Set (ชุดสกิลของ epoch สุดท้าย)")
    body = """<h1>%s</h1>
    <div class='sub'>จำนวน rollout ที่ผ่านข้อตรวจนั้น · ผลจริงจาก <span class='mono'>runs/&lt;ชื่อ&gt;/legs/runs/&lt;leg&gt;/trials/*/grade.json</span> · Evolver ไม่เห็นตารางนี้ เห็นแค่คะแนนรวมของแต่ละ rollout ·
      <span class='badge adapt'>ผ่านครบ</span> <span class='badge solver'>ผ่านบางส่วน</span> <span class='badge bad'>ไม่ผ่าน</span></div>
    <table class='t' style='border-spacing:0 5px'><tr><th>ประเภท</th><th>ข้อตรวจ</th>%s</tr>%s</table>""" % (title, th, tr)
    shot(out or "img/r05-coverage-%s.png" % split, body)


if __name__ == "__main__":
    for w in sys.argv[1:] or ["build_skill", "lab_map"]:
        if ":" in w:
            f, arg = w.split(":", 1)
            globals()[f](*arg.split(","))
        else:
            globals()[w]()
