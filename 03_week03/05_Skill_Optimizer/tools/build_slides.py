#!/usr/bin/env python3
"""สร้างสไลด์ Skill_Optimizer_Slides.html ของบท (ภาคทฤษฎี + ภาค LAB)

  python tools/build_slides.py            (รันบนเครื่อง จากโฟลเดอร์ของบท)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพ กราฟ หรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง โค้ด และพรอมต์ของ LAB: อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ตัวเลขผลของแต่ละรุ่น: อ่านจาก runs/results.json และ runs/<รุ่น>/gate.txt
- ภาพอธิบายและขั้นตอนข้างภาพ: tools/slides_figures.py · เครื่องมือเรนเดอร์ (ไฟล์กลาง ไม่มีเนื้อหาเฉพาะบท): tools/slides_engine.py
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_figures import FIGS

FIG = {f["img"]: f for f in FIGS}

from slides_engine import (md, sec, walk, table, codes, para, prompt, eye, CTX, add, note, fig, explain, tiles, cards,
                           versus, bars, tbl, code, heat_color)

S = E.slide
SECS = E.load("README.md")

# ------------------------------------------------------------------ ผลจริงจาก runs/
RES = json.loads(E.read("runs/results.json"))


def pct(x):
    return "%.1f%%" % (x * 100)


def gate(cand):
    txt = E.read("runs/%s/gate.txt" % cand)
    m = re.search(r"(\S+) แทน (\S+)\s*$", txt.strip())
    g = {"cand": m.group(1), "base": m.group(2), "accept": "ACCEPT" in txt}
    m = re.search(r"^รวม: .*?· เกณฑ์ ([\d.]+) จุด", txt, re.M)
    g["th"] = m.group(1) if m else None
    return g


def nfig(key, post=""):
    f = FIG[key]
    return explain(f["title"], "img/%s.jpg" % key, f["steps"], post)


# ------------------------------------------------------------------ เนื้อหาเฉพาะของสไลด์
STEPS = {  # ขั้นตอนข้างภาพเดิมของ README (เรียบเรียงจากข้อความของหัวข้อนั้นใน README.md)
    "problem": ["AI อ่านโจทย์ แล้วเขียนโค้ดตามข้อกำหนดที่ระบุชัดครบทุกข้อ",
                "ถึงจุดที่โจทย์ไม่ได้บอก AI ต้องเดาเอง",
                "ตัวตรวจของร้านตรวจ **ทั้ง 2 ประเภท** โค้ดจึงไม่ผ่าน",
                "AI ไม่ได้ผิดเพราะเขียนโค้ดไม่เป็น แต่ผิดเพราะ **ไม่มีใครบอกความรู้แฝงของทีม**"],
    "job": ["ค้นหาความรู้แฝงที่ขาดไป จากข้อที่ AI ทำผิดตอนตรวจ",
            "เขียนลงใน **สกิล** (คู่มือที่ AI อ่านก่อนเขียนโค้ด)",
            "ปรับสกิลทีละรุ่น จนโค้ดผ่านตัวตรวจครบทุกข้อ ทุกครั้ง",
            "แก้ได้แค่สกิล ห้ามแก้โค้ด"],
    "loop": ["**วัดรุ่นฐาน**: ให้ Agent ทำทุกงานด้วยสกิลรุ่นปัจจุบัน",
             "**วิเคราะห์ข้อที่พลาด**: โค้ดผิดข้อกำหนดข้อไหน เพราะสกิลเขียนไม่ชัดตรงไหน",
             "**แก้ไม่เกิน 3 จุด**: คัดลอกสกิลเป็นรุ่นใหม่ แล้วแก้ตามสาเหตุ",
             "**วัดซ้ำ**: วัดรุ่นใหม่ด้วยวิธีเดียวกับขั้น 1 ทุกอย่าง",
             "**ประตูรับ**: เทียบคะแนนสองรุ่น → ACCEPT รุ่นใหม่เป็นรุ่นฐาน · REJECT ทิ้งรุ่นใหม่"],
}
CHECK_GROUPS = [("ข้อกำหนดที่ระบุชัด", ["contract", "basic", "boundary"], "navy"),
                ("ความรู้แฝงข้อ 2 · การปัดเศษ", ["half_up", "no_drift"], ""),
                ("ความรู้แฝงข้อ 3 · ข้อมูลนำเข้า", ["reject_value", "reject_type"], ""),
                ("ความรู้แฝงข้อ 4 · CLI", ["cli_ok", "cli_error"], ""),
                ("ความรู้แฝงข้อ 5 · เทสต์", ["tests"], ""),
                ("นโยบายธุรกิจ C1 C2 S1 S2", ["policy"], "warn")]
LABS = {1: ("วัดผลตั้งต้น", "noskill", "v0", "n15-lab1-steps"), 2: ("วิเคราะห์ข้อผิดพลาด", "v0", "v1", "n16-lab2-steps"),
        3: ("เติมความรู้แฝงจากทีม", "v1", "v2", "n17-lab3-steps"), 4: ("ทำกติกาให้ตรวจสอบได้", "v2", "v3", "n18-lab4-steps"),
        5: ("ย่อสกิลเพื่อลดต้นทุน", "v3", "v4", "n19-lab5-steps")}
NAME = {"noskill": "ไม่มีสกิล"}


def vname(v):
    return NAME.get(v, "`%s`" % v)


def fileflow(prefix, mid):
    return E.fileflow(table(prefix, "Input"), mid)


def result_slide(n):
    short, base, cand, _ = LABS[n]
    g, rb, rc = gate(cand), RES[base], RES[cand]
    diff = lambda part: (rc[part]["score"] - rb[part]["score"]) * 100
    d = lambda part: "จาก %s · **%+.1f จุด**" % (pct(rb[part]["score"]), diff(part))
    tone = lambda part: "bad" if diff(part) < -0.05 else ""
    tok = (rc["all"]["context_tokens"] / rb["all"]["context_tokens"] - 1) * 100
    items = [("Training Set", pct(rc["train"]["score"]), d("train"), tone("train")),
             ("Validation Set", pct(rc["val"]["score"]), d("val"), tone("val")),
             ("คะแนนรวมของ %s" % vname(cand), pct(rc["all"]["score"]), d("all") + (" · เกณฑ์ %s จุด" % g["th"] if g["th"] else ""), tone("all")),
             ("ประตูรับ", "ACCEPT" if g["accept"] else "REJECT",
              "รับ %s แทน %s" % (vname(cand), vname(base)) if g["accept"] else "ใช้ %s ต่อ" % vname(base), "ok" if g["accept"] else "bad"),
             ("โทเคนขาเข้าต่อ Trial", "%+.1f%%" % tok, "{:,} → {:,}".format(rb["all"]["context_tokens"], rc["all"]["context_tokens"]), "warn")]
    body = tiles(items) + note(eye("LAB %d" % n))
    return S("ผลจริง LAB %d: %s → %s" % (n, vname(base), vname(cand)), body, tag="runs/results.json", cls="mid")


# รายการตรวจผลของแต่ละ LAB · เรียบเรียงจากตาราง Input/Output พรอมต์ และ "ผลจริง" ของ LAB นั้นใน README.md
CHECKS = {
    "ขั้น 0.1": {
        "items": [
            "มีโฟลเดอร์ `Teaching/my-skill-optimizer/` และมีไฟล์ครบ: `SKILL.md` · `scripts/skillopt.py` · `references/source.md` · `references/suite.md` · `references/issues.md`",
            "`scripts/skillopt.py` มีครบ 7 คำสั่ง: `lint` `run` `grade` `report` `failures` `null` `gate`",
            "`references/source.md` มีตาราง ส่วนของสกิล | มาจากข้อไหนของเปเปอร์ | เหมือนหรือต่าง",
            "รายงานมีผลทดสอบ `gate` 5 คู่ (`noskill` → `v0` → `v1` → `v2` → `v3` → `v4`) และตัดสินตรงกับ `runs/<รุ่นใหม่>/gate.txt` ทุกคู่",
        ],
        "ref": "ผลของผู้สอน: ใช้ 14 นาที · ไม่เรียกโมเดล · `gate` ตรงทุกตัวอักษร (ACCEPT 4 คู่ · REJECT 1 คู่) · `null` `lint` `report` ตรงกับไฟล์ที่เก็บไว้",
        "note": "เครื่องมือที่สร้างเองไม่ต้องเหมือนใครทุกบรรทัด สิ่งที่ต้องตรงคือ **รูปแบบ** และ **ผลตัดสิน**",
    },
    "ขั้น 0.2": {
        "items": [
            "รายงานเป็นตาราง รายการ | ผล",
            "`my-skill-optimizer` ถูกติดตั้งเป็น global skill ชื่อ `skill-optimizer` ของบัญชี yolo",
            "ใน container มี `/workspace/sklab/suite/` และ `/workspace/sklab/runs/v0/skills/` (โครงโฟลเดอร์เดิม)",
            "`suite/check_grader.py` ผ่าน: เฉลยอ้างอิงผ่าน 10/10 ห้าโจทย์ และ 11/11 โจทย์ค่าส่ง",
            "มีบัญชี `yolo` ที่ล็อกอินแล้วอย่างน้อย 1 บัญชี",
        ],
        "ref": "ผลของผู้สอน: ติดตั้งสกิล ✅ · คัดลอกโจทย์ ✅ · ตัวตรวจผ่าน ✅ · บัญชีที่ใช้ได้ `yolo1` `yolo2` `yolo3` · ใช้ 1 นาที",
        "note": "ตรวจตัวตรวจก่อนเสมอ ถ้าเครื่องวัดผิด ตัวเลขหลังจากนี้ใช้ไม่ได้ทั้งหมด",
    },
    "LAB 1": {
        "items": [
            "`runs/noskill/trials/` และ `runs/v0/trials/` มีรุ่นละ 18 โฟลเดอร์ (6 โจทย์ × 3 รอบ) รวม 36 Trial",
            "`runs/report.md` มีตารางเทียบ `noskill` กับ `v0` · `runs/results.json` ถูกเขียน",
            "`runs/v0/null.txt` มีความแกว่งของ `v0` แยกชุด train · val · all",
            "`runs/v0/gate.txt` มีบรรทัด `ผล:` ของการตัดสิน `noskill` → `v0`",
            "ผลของ Validation Set ที่เก็บลงเครื่อง มีแค่คะแนนและต้นทุน (ไม่มีผลรายข้อ)",
        ],
        "ref": "ผลของผู้สอน: ไม่มีสกิล 45.3% → `v0` 67.9% (+22.6 จุด · เกณฑ์ 2.6) · ACCEPT · ผ่านครบทุกข้อ 0/18 ทั้งสองรุ่น · ใช้ 4 นาที",
    },
    "LAB 2": {
        "items": [
            "`runs/ISSUES.md` มีตาราง ปัญหา | พบกี่ Trial | สาเหตุ | ทางแก้ · เก็บเฉพาะสาเหตุที่พบมากกว่า 1 Trial",
            "`runs/v1/skills/money-coder/SKILL.md` ต่างจาก `v0` ไม่เกิน 3 จุด",
            "`runs/v1/trials/` มี 18 โฟลเดอร์ · วัดด้วยค่าเดียวกับ `v0`",
            "`runs/v1/gate.txt` มีผลตัดสิน `v0` → `v1` · `runs/report.md` มีทุกรุ่น",
            "ดูว่า Claude จัดการข้อ `policy` อย่างไร: เดากฎเอง หรือจดเป็นปัญหาเปิด",
        ],
        "ref": "ผลของผู้สอน: รวม 67.9% → 93.5% (+25.6 จุด · เกณฑ์ 2.3) · ACCEPT · แก้ 3 จุด (`cli_ok`/`cli_error` · `tests` · `reject_type`) · `policy` ยัง 0/6 และถูกจดเป็นปัญหาเปิด · ใช้ 5 นาที",
    },
    "LAB 3": {
        "items": [
            "`runs/v2/skills/money-coder/SKILL.md` มีนโยบายค่าส่งและนโยบายเงินคืน เขียนเป็นนโยบายของร้าน ไม่มี Input หรือคำตอบของข้อตรวจ",
            "แก้ไม่เกิน 3 จุดจากรุ่นฐาน",
            "`runs/v2/trials/` มี 18 โฟลเดอร์ · `runs/v2/gate.txt` มีผลตัดสิน `v1` → `v2`",
            "`runs/ISSUES.md` ปิดปัญหา `policy` · `runs/report.md` มี `v2`",
        ],
        "ref": "ผลของผู้สอน: Training 95.2% → 100.0% · รวม 93.5% → 96.7% (+3.2 จุด · เกณฑ์ 2.0) · ACCEPT · `policy` 0/6 → 6/6 · Validation ยัง 90% · ใช้ 5 นาที",
    },
    "LAB 4": {
        "items": [
            "`runs/v3/skills/money-coder/SKILL.md` แก้ไม่เกิน 3 จุด ให้เป็นกติกาที่ตรวจสอบได้ ไม่มี Input หรือคำตอบของข้อตรวจ",
            "ไม่มีการเปิดผลรายข้อ Trace หรือโค้ดของ Validation Set",
            "`runs/v3/trials/` มี 18 โฟลเดอร์ · `runs/v3/gate.txt` มีผลตัดสิน `v2` → `v3`",
            "ถ้า REJECT: ใช้ `v2` ต่อ และไม่วัดซ้ำเพื่อให้ผ่าน",
            "`runs/ISSUES.md` และ `runs/report.md` ถูกอัปเดต",
        ],
        "ref": "ผลของผู้สอน: Validation 90.0% → 100.0% · รวม 96.7% → 100.0% (+3.3 จุด · เกณฑ์ 2.0) · ACCEPT · แก้ 2 จุด · โทเคนขาเข้า +10.2% · ใช้ 7 นาที",
    },
    "LAB 5": {
        "items": [
            "`runs/v4/skills/money-coder/SKILL.md`: กติกาละ 1 บรรทัด ไม่เกิน 60 ตัวอักษร (นับเป็น 1 จุด ไม่แก้อย่างอื่น)",
            "`runs/v4/trials/` มี 18 โฟลเดอร์ · `runs/v4/gate.txt` มีผลตัดสิน `v3` → `v4`",
            "ถ้า REJECT: ใช้ `v3` ต่อ ไม่แก้ `v4` เพิ่ม และไม่วัดซ้ำ",
            "รายงานมีโทเคนขาเข้าเทียบกับรุ่นฐาน และข้อตรวจของ Training Set ที่เปลี่ยนไป",
            "`runs/ISSUES.md` จดว่าการย่อแบบนี้ได้ผลหรือไม่ เพราะอะไร",
        ],
        "ref": "ผลของผู้สอน: รวม 100.0% → 80.3% (−19.7 จุด) · REJECT · สกิลสั้นลง 81% แต่โทเคนขาเข้าลดแค่ 5.2% · `cli_ok` และ `cli_error` 12/12 → 0/12 · ใช้ 6 นาที",
    },
}
VARY = "ตัวเลขของคุณอาจต่างจากของผู้สอน เพราะ Agent เขียนไม่เหมือนกันทุกครั้ง (ข้อ 2.7) · สิ่งที่ต้องมีเหมือนกันคือไฟล์ผลและคำตัดสินของ `gate`"


def check(key, title):
    c = CHECKS[key]
    return E.check_slide(key, c["items"], c["ref"], c.get("note") or VARY, title)


def gate_slide(cand, kicker, title):
    txt = E.read("runs/%s/gate.txt" % cand).strip()
    body = ('<p>ข้อความที่คำสั่ง <code>gate</code> พิมพ์จริง เก็บไว้ที่ <a href="runs/%s/gate.txt" target="_blank">'
            '<code>runs/%s/gate.txt</code></a></p>%s'
            '<table class="c2"><thead><tr><th>ส่วนของข้อความ</th><th>อ่านว่า</th></tr></thead><tbody>'
            '<tr><td><code>train:</code> <code>val:</code> <code>รวม:</code></td><td>คะแนนของรุ่นฐาน → รุ่นใหม่ (ผลต่างเป็นจุด) แยกตามชุด</td></tr>'
            '<tr><td><code>เกณฑ์</code></td><td>ค่าที่มากกว่าระหว่าง <code>eps</code> 2.0 จุด กับ <code>z</code> 1.5 × ความแกว่งของส่วนต่างสองรุ่น ของชุดนั้น</td></tr>'
            '<tr><td><code>ผล:</code></td><td>คำตัดสินของโปรแกรม · <span class="v accept">ACCEPT</span> = exit 0 · <span class="v reject">REJECT</span> = exit 1</td></tr>'
            '</tbody></table>') % (cand, cand, E.pre_html(txt, "text", "term"))
    return E.S(kicker, "ผลดิบของ gate · " + title, body, tag="runs/%s/gate.txt" % cand, maxfs=1.1)


def compare_slides(kicker):
    """โค้ดจริงของ Agent จาก runs/ (โจทย์เงินคืน รอบที่ 1): ไม่มีสกิล เทียบกับ v3 · ผลตรวจอ่านจาก grade.json"""
    def one(label):
        base = "runs/%s/trials/t4-cashback-r1" % label
        g = json.loads(E.read(base + "/grade.json"))
        return base, E.read(base + "/sandbox/solve.py").rstrip().split("\n"), g["checks"]

    def head(name, base):
        return '<h3 class="lead">%s<span> · <a href="%s/sandbox/solve.py" target="_blank">เปิดไฟล์ solve.py</a></span></h3>' % (name, base)

    def two(left, right, fl=1.15, fr=1):
        return '<div class="cols"><div class="col" style="flex:%s">%s</div><div class="col" style="flex:%s">%s</div></div>' % (fl, left, fr, right)

    b0, c0, k0 = one("noskill")
    b3, c3, k3 = one("v3")
    cut = next(k for k, l in enumerate(c3) if l.startswith("def _main"))
    bad = [c for c in k0 if not c["pass"]]
    fails = "".join('<div class="cardx bad"><h4><code>%s</code></h4><p>%s</p></div>' % (c["id"], E.esc(c["note"])) for c in bad)
    s1 = E.S(kicker, "โค้ดจริงของ Agent ตอนไม่มีสกิล: ผ่าน %d จาก %d ข้อ" % (len(k0) - len(bad), len(k0)), two(
        head("ไม่มีสกิล · โจทย์เงินคืน รอบที่ 1", b0) + E.pre_html("\n".join(c0), "python"),
        '<h3 class="lead">ข้อความจากตัวตรวจ (grade.json)</h3><div class="fails">%s</div>' % fails, 1, 1.05), tag="runs/noskill", cls="cmp", maxfs=1.2)
    ok3 = sum(1 for c in k3 if c["pass"])
    s2 = E.S(kicker, "โค้ดจริงของ Agent ด้วยสกิล `v3`: ผ่าน %d จาก %d ข้อ" % (ok3, len(k3)), two(
        head("สกิลรุ่น v3 · ส่วนฟังก์ชัน", b3) + E.pre_html("\n".join(c3[:cut]).rstrip(), "python"),
        head("สกิลรุ่น v3 · ส่วน CLI", b3) + E.pre_html("\n".join(c3[cut:]), "python"), 1, 1), tag="runs/v3", cls="cmp", maxfs=1.2)
    rows = [
        ("`type(amount) is not int` · `type(birthday) is not bool` → `raise ValueError`", "ความรู้แฝงข้อ 3 ตรวจสอบข้อมูลนำเข้า", "`reject_value` `reject_type`"),
        ("`birthday and tier in (\"gold\", \"platinum\")`", "นโยบาย C1 สิทธิ์เดือนเกิดเฉพาะ gold และ platinum", "`policy`"),
        ("`num // _DEN` บนตัวเศษจำนวนเต็ม ไม่มี `float`", "ความรู้แฝงข้อ 1 และนโยบาย C2 เงินคืนปัดลง", "`contract` `no_drift` `policy`"),
        ("`_main()` อ่าน JSON จาก stdin · ตอบ `{\"ok\": …}` · `return 0` หรือ `return 2`", "ความรู้แฝงข้อ 4 สัญญาการเรียกผ่าน CLI", "`cli_ok` `cli_error`"),
        ("ไฟล์ `test_solve.py` ที่ส่งคู่กัน", "ความรู้แฝงข้อ 5 ชุดทดสอบหน่วย", "`tests`"),
    ]
    tab = E.table_html({"t": "table", "head": ["ส่วนของโค้ด `v3`", "มาจากกติกาข้อไหนของสกิล", "ข้อตรวจที่ผ่าน"], "rows": [list(r) for r in rows]})
    s3 = E.S(kicker, "โค้ดแต่ละส่วนของ `v3` มาจากกติกาข้อไหนของสกิล", tab, tag="ตารางหลัก")
    return [s1, s2, s3]


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    agenda = table("Skill Optimizer", "ภาค")
    labtab = table("3 ·", "LAB")
    labrow = {re.match(r"\[(\d)\]", r[0]).group(1): r for r in labtab["rows"]}

    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    title = SECS[0]["text"].split("·")
    add({"raw": ('<div class="shade"></div><div class="inner"><div class="small">03_week03 · บทที่ 05</div><h1>%s</h1>'
                 '<div class="sub">%s</div><div class="hint">กด <span class="kbd">→</span> หรือ <span class="kbd">Space</span> เพื่อไปต่อ · '
                 '<span class="kbd">O</span> สารบัญ · <span class="kbd">F</span> เต็มจอ · คลิกภาพเพื่อขยาย</div><div class="imgnote">ภาพจำลอง</div></div>')
         % (E.esc(title[0].strip()), E.esc("·".join(title[1:]).strip())),
         "cls": "cover", "style": ' style="background-image:url(img/g01-cover.jpg)"', "title": "ปก", "kicker": "", "tag": "", "lead": ""})

    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("ทั้งเรื่องในภาพเดียว: แก้ไฟล์ข้อความไฟล์เดียว คะแนนจาก %s เป็น %s" % (pct(RES["noskill"]["all"]["score"]), pct(RES["v3"]["all"]["score"])),
            "img/r04-path.png", "ผลจริงจาก 108 Trial · โมเดลไม่ถูกแตะ สิ่งเดียวที่แก้คือ `SKILL.md` · ที่มาของแต่ละก้าวอยู่ในภาค LAB"))
    parts, cur = [], None
    for r in agenda["rows"]:
        if r[0].strip():
            cur = {"name": E.plain(r[0]), "do": r[3], "secs": []}
            parts.append(cur)
        cur["secs"].append((E.plain(r[1]), r[2]))
    road = "".join('<div class="partbox %s"><div class="ph">%s<small>%s</small></div>%s</div>' % (
        "lab" if "LAB" in p["name"] else "", p["name"], md(p["do"]),
        "".join('<div class="secbox"><b>%s</b><span>%s</span></div>' % (md(a), md(b)) for a, b in p["secs"])) for p in parts)
    add(S("บทนี้แบ่งเป็น 2 ภาค 4 ส่วน", '<div class="road">%s</div>' % road + note(
        "ทฤษฎีจากงานวิจัยต้นทาง (SkillOpt) อ่านเพิ่มได้ที่ [`01_theory/README.md`](01_theory/README.md) · รายละเอียดเต็มของทุกหัวข้ออยู่ใน [`README.md`](README.md)",
        "info"), cls="mid"))
    add(S("วิธีใช้สไลด์นี้", cards([
        ("ไปหน้าถัดไป / ก่อนหน้า", '<p><span class="kbd">→</span> <span class="kbd">Space</span> / <span class="kbd">←</span> หรือปุ่มมุมขวาล่าง</p>'),
        ("สารบัญทุกหน้า", '<p><span class="kbd">O</span> แล้วคลิกหน้าที่ต้องการ · <span class="kbd">F</span> เต็มจอ</p>'),
        ("ขยายภาพ", "คลิกที่ภาพ · คลิกอีกครั้งหรือ Esc เพื่อปิด"),
        ("คัดลอกพรอมต์ของ LAB", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** ให้ข้อความเดียวกับ `README.md` ตรงตัวอักษร แม้พรอมต์ถูกแบ่งแสดง 2 หน้า", "warn"),
        ("ตรวจผลหลังรัน", "สไลด์ **ตรวจผลของคุณ** ต่อจากพรอมต์ทุก LAB · ติ๊กได้ และจำค่าไว้ในเบราว์เซอร์นี้", "warn"),
        ("เปิดไฟล์จริง", "ลิงก์สีน้ำเงินเปิดไฟล์ในโฟลเดอร์ของบท · เปิดสไลด์จากโฟลเดอร์ `05_Skill_Optimizer`"),
    ]), cls="mid"))

    # ===== ภาคทฤษฎี
    CTX.update(kicker="", group="ภาคทฤษฎี")
    alert = next(b for b in sec("ภาคทฤษฎี") if b["t"] == "alert")
    add(E.divider("ภาคทฤษฎี", "โจทย์ และวิธีปรับสกิล", "".join(E.render(x) for x in alert["blocks"]), "img/s01-theory.jpg"))

    # ----- 1 · โจทย์
    CTX.update(kicker="ภาคทฤษฎี · 1 · โจทย์และข้อกำหนดของร้าน", group="ภาคทฤษฎี · 1 · โจทย์และข้อกำหนดของร้าน")
    add(E.divider("1", "โจทย์และข้อกำหนดของร้าน", "<p>โจทย์คืออะไร · โค้ดแบบไหนถูก แบบไหนผิด · ใครเป็นคนตรวจ</p>", "img/s02-problem.jpg", small="ภาคทฤษฎี"))
    add(fig("ร้าน BaanKafe ให้ AI เขียนโค้ดคิดเงิน 6 งาน", "img/g09-suite.png",
            "งานละ 1 ฟังก์ชัน ในไฟล์ `solve.py` · งาน 1–4 ใช้หาข้อผิดเพื่อปรับสกิล · งาน 5–6 เก็บไว้ทดสอบ ไม่เปิดดูตอนปรับ"))
    add(fig("ร้านมีข้อกำหนด 2 ประเภท แต่ AI ได้รับแค่ประเภทเดียว", "img/g18-shop-rules.png",
            "**ข้อกำหนดที่ระบุชัด** อยู่ในโจทย์ → AI รู้ · **ความรู้แฝงของทีม** ไม่เคยถูกเขียนลงโจทย์ → AI ไม่รู้"))
    add(explain("ปัญหา: AI ทำตามโจทย์ครบ แต่ยังถูกตัดสินว่าผิด", "img/g19-problem.png", STEPS["problem"]))
    add(S("ตัวอย่างจริง: เงินคืน silver ของยอด 200 บาท ที่ซื้อในเดือนเกิด", versus(
        'cashback(20000, "silver", True)',
        ("AI ทำตามโจทย์", "20000 × 1.5% × 2", "600", "โจทย์บอกว่า \"เดือนเกิด ได้เงินคืน 2 เท่า\" แต่ไม่ได้บอกว่าระดับไหนได้สิทธิ์ · AI ให้ทุกระดับ"),
        ("คำตอบที่ถูกของร้าน", "20000 × 1.5%", "300", "ร้านให้สิทธิ์เดือนเกิดเฉพาะ gold และ platinum · พนักงานทุกคนรู้ แต่ไม่เคยเขียนลงโจทย์")), cls="mid"))
    add(explain("งานของเรา: เขียนความรู้แฝงลงในสกิล", "img/g20-our-job.png", STEPS["job"]))
    add(nfig("n02-rules"))
    add(nfig("n01-glossary"))

    t = table("ความรู้แฝงกลุ่ม 1", "ข้อ")
    rows = []
    for r in t["rows"]:
        for part in r[3].split("·"):
            m = re.search(r"^(.*?)(\d+)/(\d+)\s*$", part.strip())
            rows.append(("ข้อ %s · %s" % (r[0], r[1]) + (" — %s" % m.group(1).strip() if m.group(1).strip() else ""), r[2],
                         int(m.group(2)), int(m.group(3)), "%s/%s" % (m.group(2), m.group(3))))
    add(S("มาตรฐานการเขียนโค้ด 5 ข้อ: ไม่มีสกิล AI ทำถูกแค่ไหน", bars(rows) + note(
        "ตัวเลขจากผล LAB 1 (Training Set 12 Trial) · ส่วนข้อกำหนดที่ระบุชัด (สูตรและค่าขอบเขต) AI ทำถูก 12/12"), tag="ความรู้แฝงกลุ่ม 1"))
    for k in ("n03-std1-integer", "n04-std2-rounding", "n05-std3-validation", "n06-std4-cli", "n07-std5-tests"):
        add(nfig(k))
    add(nfig("n08-policies"))
    add(tbl("นโยบาย 4 ข้อ: โจทย์บอกอย่างหนึ่ง ทีมทำอีกอย่างหนึ่ง", table("ความรู้แฝงกลุ่ม 2", "ข้อ"),
            post=note("C1 และ C2 คือกรณีที่โจทย์เขียน **กว้างกว่าที่ร้านทำจริง** ซึ่งพบบ่อยในงานจริง"), tag="ความรู้แฝงกลุ่ม 2"))
    add(nfig("n09-skill-role"))
    add(fig("วิธีทำ: ทดลองเป็นรอบ", "img/g21-one-round.png",
            "เราไม่รู้ล่วงหน้าว่าเขียนสกิลแบบไหน Agent จึงจะทำตาม จึงต้อง **แก้สกิล ให้ Agent เขียนจริง แล้ววัด**"))
    add(code("ตัวอย่างงาน 1 ชิ้น: โจทย์ `cashback` ที่ Agent ได้รับ", codes("1.4")[0]["text"],
             post=note("นี่คือข้อกำหนดที่ระบุชัดทั้งหมดของงานนี้ · ไม่มีความรู้แฝงของทีมอยู่ในนี้")))
    add(nfig("n10-cashback-steps"))
    add(tbl("ลองคิดด้วยมือ 5 กรณี", table("1.4", "#"),
            post=note("กรณี 1–2 ตอบได้จากโจทย์อย่างเดียว · กรณี 3–5 โจทย์ไม่ได้บอก ต้องรู้ความรู้แฝงของทีม")))
    add(nfig("n11-deliverables"))
    add(code("งานที่ถูกข้อกำหนด ใช้ได้ครบ 3 แบบ", codes("1.5")[0]["text"],
             post='<p class="cap">ผลข้างบนรันจากเฉลยอ้างอิง <a href="suite/ref/t4-cashback/solve.py" target="_blank"><code>suite/ref/t4-cashback/</code></a></p>'))
    add(fig("แบบไหนถูก แบบไหนผิด: ทุกกรณีของ `cashback`", "img/d03-examples.png",
            "ช่อง \"Output ที่ผิด\" คือคำตอบที่ Agent เคยตอบจริง · คลิกภาพเพื่อขยาย"))
    add(fig("ใครเป็นคนตรวจ: ตัวตรวจรู้ข้อกำหนดครบทั้ง 2 ประเภท", "img/g22-grader-knows-all.png",
            "ตัวตรวจคือโปรแกรม Python 1 ไฟล์ [`suite/grade.py`](suite/grade.py) · เขียนครั้งเดียว ใช้ตรวจทุกงานและทุกรุ่น"))
    add(fig("ตัวตรวจตรวจผลงาน 4 วิธี", "img/d02-grader.png", "ตัวตรวจตรวจ **โค้ดที่ได้** ไม่ได้ตรวจคำพูดของ Agent"))
    ct = {E.plain(r[1]): r[2] for r in table("ตัวตรวจตรวจอย่างไร", "#")["rows"]}
    grp = [(head, '<div class="chips">%s</div>' % "".join('<div class="ck"><code>%s</code><span>%s</span></div>' % (c, md(ct[c])) for c in ids), tone)
           for head, ids, tone in CHECK_GROUPS]
    add(S("ข้อตรวจ 11 แบบ จัดตามข้อกำหนดที่ตรวจ", cards(grp, 3) + note(
        "คะแนนของ 1 Trial = ข้อที่ผ่าน ÷ จำนวนข้อตรวจของงานนั้น (งานละ 10 ข้อ · งานค่าส่ง 11 ข้อ)", label="คะแนน")))
    add(S("ข้อความตอนไม่ผ่าน คือเบาะแสของความรู้แฝง", E.pre_html(codes("ตัวอย่างผลตรวจ")[0]["text"], "text", "term") + cards([
        ("✗ `cli_ok` ✗ `cli_error`", "ตอบ JSON คนละรูปแบบ และ exit code ผิด → **ความรู้แฝงข้อ 4**: รูปแบบคำตอบและ exit code ที่ร้านใช้", "bad"),
        ("✗ `policy`", "silver ในเดือนเกิดได้ 2 เท่าตามโจทย์ แต่ร้านไม่ให้ → **นโยบาย C1**: สิทธิ์เดือนเกิดเฉพาะ gold และ platinum", "bad"),
    ], 2), tag="cashback · v0 · 7/10", maxfs=1.2))
    add(code("ข้างใน `grade.py`: ข้อกำหนดแต่ละประเภทอยู่ตรงไหน", codes("ตัวตรวจตรวจอย่างไร", "python")[0]["text"], "python",
             post=note("นโยบายธุรกิจ 4 ข้อไม่อยู่ในโจทย์ มีอยู่ **ในตัวตรวจเท่านั้น** · Agent ที่ถูกวัดต้องไม่เห็นไฟล์นี้")))

    # ----- 2 · วิธีปรับสกิล
    CTX.update(kicker="ภาคทฤษฎี · 2 · วิธีปรับสกิล", group="ภาคทฤษฎี · 2 · วิธีปรับสกิล")
    add(E.divider("2", "วิธีปรับสกิล", "<p>ปรับสกิลอย่างไร · รู้ได้อย่างไรว่ารุ่นใหม่ดีกว่าจริง</p>"
                  "<p><b>การปรับสกิล = เขียนความรู้แฝงให้ชัดจน Agent ไม่ต้องเดา</b> แล้ววัดว่าโค้ดถูกข้อกำหนดมากขึ้นจริง</p>",
                  "img/s03-method.jpg", small="ภาคทฤษฎี"))
    add(fig("ทำไมต้องวัด: ดูดี ไม่ใช่หลักฐาน", "img/g03-why-measure.png",
            "อ่านสกิล 2 รุ่นแล้วบอกไม่ได้ว่ารุ่นไหนทำให้โค้ดถูกข้อกำหนดมากกว่า ต้อง **วัด** ด้วยงานจริง"))
    l3, l4 = json.loads(E.read("runs/v3/lint.json")), json.loads(E.read("runs/v4/lint.json"))
    add(S("ถ้าตัดสินด้วยตา จะเลือก `v4` ซึ่งแย่กว่า", versus(
        "",
        ("v4 · ดูด้วยตา: สั้น กติกาละ 1 บรรทัด ดูดีกว่า", "{:,} ไบต์".format(l4["total_bytes"]), pct(RES["v4"]["all"]["score"]), "วัดจริงได้คะแนนน้อยกว่า"),
        ("v3 · ดูด้วยตา: ยาว", "{:,} ไบต์".format(l3["total_bytes"]), pct(RES["v3"]["all"]["score"]), "วัดจริงผ่านครบทุกข้อตรวจ")) +
        note("ตัวอย่างจากผล LAB 5"), cls="mid"))
    add(fig("เปรียบกับการปรับสูตรกาแฟ", "img/g14-analogy.png",
            "สูตร = สกิล · ลูกค้าหลายคนชิม = งาน 6 ชิ้น · ใบให้คะแนน = ตัวตรวจ · ชงซ้ำรสยังต่าง = ความแกว่งของการวัด · เก็บหรือทิ้ง = ประตูรับ"))
    add(explain("วงรอบ 5 ขั้น", "img/g02-loop.png", STEPS["loop"]))
    add(fig("ไพป์ไลน์ของ 1 Trial: Generate → Grade", "img/d05-trial-t4-cashback.png",
            "ตัวอย่างจริง: รุ่น `v0` · โจทย์ `t4-cashback` · รอบที่ 1 → ผ่าน 7 จาก 10 ข้อ = **0.7** · คลิกภาพเพื่อขยาย"))
    add(S("คะแนนมาจากตัวตรวจ ไม่ใช่จากคำพูดของ Agent",
          '<p class="bigq">Agent บอกว่า <em>"เทสต์ทั้ง 7 ข้อผ่าน"</em><br>แต่คะแนนคือ <em>0.7</em></p>'
          '<p class="bigsub">ตัวตรวจรันโค้ดที่ได้ 3 วิธี: เรียกฟังก์ชัน · รันเป็นโปรแกรม · รันเทสต์<br>Trial แต่ละครั้งเริ่มใหม่ทั้งหมด Agent จำครั้งก่อนไม่ได้</p>', maxfs=1.2))
    add(fig("การวัดสกิล 1 รุ่น = 18 Trial", "img/d01-pipeline.png",
            "1 รุ่น วัด 18 Trial = 6 งาน × 3 รอบ · **คะแนนของรุ่น = ค่าเฉลี่ยของ 18 Trial** · ทุกรุ่นใช้โจทย์ ตัวตรวจ โมเดล และจำนวนรอบชุดเดียวกัน"))
    t = table("2.5", "รอบ")
    cells = ['<div></div><div class="grp">Training Set</div><div class="grp val">Validation Set</div><div></div>'] + \
            ['<div class="hh">%s</div>' % E.plain(h) for h in t["head"][1:]]
    for r in t["rows"]:
        cells.append('<div class="hr">รอบ %s</div>' % r[0])
        cells += ['<div class="hc" style="background:%s">%s</div>' % (heat_color(float(v)), v) for v in r[1:]]
    v0 = RES["v0"]
    add(S("คะแนนทั้ง 18 Trial ของ `v0`: งานเดิม สกิลเดิม คะแนนยังไม่เท่ากันทุกรอบ", '<div class="heat">%s</div>' % "".join(cells) + tiles([
        ("Training · เฉลี่ย 12 Trial", pct(v0["train"]["score"]), "4 งานแรก", ""),
        ("Validation · เฉลี่ย 6 Trial", pct(v0["val"]["score"]), "2 งานหลัง", "warn"),
        ("รวม · เฉลี่ย 18 Trial", pct(v0["all"]["score"]), "คะแนนของรุ่น `v0`", "ok")]) + note(
        "นี่คือเหตุผลที่ต้องทำงานเดิมซ้ำ 3 รอบ (ข้อ 2.7)"), tag="ผล LAB 1"))
    add(fig("แบ่งงานเป็น 2 ชุด", "img/g05-split.png",
            "**Training Set** 4 งานแรก: เปิดดูข้อที่ผิด เพื่อหาสาเหตุและแก้สกิล · **Validation Set** 2 งานหลัง: ดูแค่คะแนนรวม เพื่อตัดสิน"))
    add(nfig("n12-train-val-cases"))
    add(fig("ความแกว่งของการวัด (Measurement Noise)", "img/g06-noise.png",
            "สกิลเดิม งานเดิม ทำซ้ำยังได้คะแนนไม่เท่ากัน · ถ้ารุ่นใหม่มากกว่ารุ่นฐาน 1 จุด บอกไม่ได้ว่าสกิลดีขึ้น หรือแค่บังเอิญ"))
    add(S("ทางแก้: ผลต่างต้องมากกว่าเกณฑ์ จึงนับว่าดีขึ้นจริง",
          '<div class="formula">เกณฑ์ = ค่าที่มากกว่าระหว่าง&nbsp; 2 จุด &nbsp;กับ&nbsp; 1.5 × ความแกว่งของผลต่างสองรุ่น</div>' + tiles([
              ("ความแกว่งของผลต่าง", "1.6 จุด", "Standard Error ของผลต่าง `v0` → `v1`", ""),
              ("1.5 × ความแกว่ง", "2.3 จุด", "มากกว่าเกณฑ์ขั้นต่ำ 2 จุด", ""),
              ("เกณฑ์ที่ใช้", "2.3 จุด", "ของคะแนนรวม", "warn"),
              ("ผลต่างจริง", "+25.6 จุด", "มากกว่าเกณฑ์หลายเท่า", "ok")]) + note(
              "ตั้งแต่ `v2` คะแนนของแต่ละงานเท่ากันทุกรอบ ความแกว่งที่วัดได้เป็น 0 เกณฑ์จึงใช้ขั้นต่ำ 2 จุด"), tag="ตัวอย่างจากผล LAB 2", cls="mid"))
    add(fig("ประตูรับ (Acceptance Gate)", "img/g07-gate.png",
            "กติกาตัดสินที่เขียนไว้ล่วงหน้า โปรแกรมเป็นผู้ตัดสิน เราไม่เลือกเองหลังเห็นผล · ต้นทุนในบทนี้ = โทเคนขาเข้าต่อ Trial"))
    vt = table("2.8", "ตัดสิน")
    add(S("ตัวอย่างการตัดสินจริง 3 ครั้ง", cards([
        (r[0] + " · " + r[5].replace("**", ""),
         "<p>Training %s · Validation %s<br><b>รวม %s จุด</b> · ต้นทุน %s</p><p>%s</p>" % (r[1], r[2], r[3], r[4], md(r[6])),
         "ok" if "ACCEPT" in r[5] else "bad") for r in vt["rows"]], 3) + note(
        "ในบทนี้ยังไม่มีรุ่นที่ผ่านด้วยเงื่อนไขต้นทุน (คะแนนเท่าเดิม ต้นทุนลดอย่างน้อย 10%) · ลองทำได้ในแบบฝึกหัดข้อ 4"),
        tag="ผล LAB 2 · LAB 4 · LAB 5", cls="mid"))
    add(fig("แก้สกิลตรงไหนก่อน: 3 ระดับ", "img/g08-ladder.png",
            "ระดับบนได้ผลแน่นอนกว่า · การปรับสกิลในบทนี้ส่วนใหญ่คือการย้ายกติกาจาก **ระดับ 3** ขึ้นไป **ระดับ 2**"))
    add(S("จากคำแนะนำกว้าง ๆ เป็นกติกาที่ตรวจได้: ตัวอย่างจริง", versus(
        "",
        ("ระดับ 3 · คำแนะนำกว้าง ๆ · v0", "รับ JSON และตอบเป็น JSON", "0/12", "Agent เดารูปแบบเอง และเดาไม่เหมือนกันทุกครั้ง (`cli_ok` ผ่าน 0/12 Trial)"),
        ("ระดับ 2 · กติกาที่ตรวจได้ · v1", 'สำเร็จตอบ {"ok": true, "result": …} exit 0', "12/12", "ระบุค่า รูปแบบ และ exit code · Agent ไม่ต้องเดา (`cli_ok` ผ่าน 12/12 Trial)")), cls="mid"))
    rt = table("2.9", "กติกา")
    add(S("กติกาของการแก้ 4 ข้อ", cards([((k + 1, r[0]), r[1]) for k, r in enumerate(rt["rows"])], 2), cls="mid"))
    add(fig("สกิล 1 รุ่น = 1 โฟลเดอร์", "img/g12-folders.png",
            "สร้างรุ่นใหม่ด้วยการคัดลอกโฟลเดอร์ของรุ่นฐาน · ห้ามแก้รุ่นเดิม · เก็บรุ่นที่ REJECT ไว้ด้วย เป็นหลักฐานว่าลองแล้วไม่ได้ผลเพราะอะไร"))
    add(fig("อัลกอริทึมทั้งหมด: ขั้น 0 ถึง 5", "img/g13-algorithm.png",
            "ขั้น 0 (ตรวจตัวตรวจ) ทำครั้งเดียวก่อนเริ่ม: ถ้าตัวตรวจผิด คะแนนทุกรุ่นหลังจากนั้นใช้ไม่ได้"))
    add(fig("Algorithm 1 พร้อมคำสั่งของ `skillopt.py`", "img/d04-algorithm.png",
            "ซ้าย = ขั้น · กลาง = ทำอะไร · ขวา = คำสั่งที่ทำขั้นนั้น · เครื่องมือนี้ผู้เรียนสร้างเองใน LAB 0"))

    # ===== ภาค LAB
    CTX.update(kicker="", group="ภาค LAB")
    alert = next(b for b in sec("ภาค LAB") if b["t"] == "alert")
    add(E.divider("ภาค LAB", "ลงมือทำ 6 ขั้น และสรุปผล", "".join(E.render(x) for x in alert["blocks"]), "img/s04-lab.jpg"))
    CTX.update(kicker="ภาค LAB · 3 · ลงมือทำ", group="ภาค LAB · 3 · ลงมือทำ")
    add(fig("ภาค LAB: ลงมือทำ 6 ขั้น", "img/g23-lab-map.png", "LAB 0 สร้างเครื่องมือและเตรียม · LAB 1–5 วัดและปรับสกิล รุ่นละ 1 LAB"))
    use = para("3 ·", "**วิธีใช้:**")["lines"]
    tip = next(b for b in walk(sec("ภาค LAB")) if b["t"] == "p" and b["lines"][0].startswith("ผลจริงทุกตัว"))["lines"][0]
    add(S("ก่อนเริ่ม LAB", cards([
        ("วิธีใช้", use[0].replace("**วิธีใช้:**", "").strip().replace("📋 ", ""), "warn"),
        ("ต้องมี", use[1].replace("**ต้องมี:**", "").strip(), "warn"),
        ("ผลจริงในสไลด์", tip, "navy")], 3) + note(
        "ทุก LAB มีลำดับเดียวกัน: ภาพขั้นตอน → ไฟล์เข้าและออก → พรอมต์ (คัดลอก) → ตรวจผลของคุณ → ผลจริงของผู้สอน", label="ลำดับ"), cls="mid"))
    add(fig("หลังรันแต่ละ LAB ได้ไฟล์อะไร และเอาไปใช้ต่ออย่างไร", "img/d06-lab-files.png"))
    add(nfig("n13-experiment-plan"))
    add(code("ข้อความที่ Agent ทุกตัวได้รับ", codes("โจทย์ 6 ข้อ")[0]["text"],
             post=note("เหมือนกันทุกรุ่น ต่างกันแค่โจทย์ที่ต่อท้าย (ตัวอย่าง: `t4-cashback`) · โจทย์เต็มทั้ง 6 ข้อ: [`suite/suite.json`](suite/suite.json)")))
    add(code("โครงสร้างโฟลเดอร์: 1 รุ่น = 1 โฟลเดอร์", codes("โครงสร้างโฟลเดอร์")[0]["text"],
             post=note("`money-coder` อยู่ใน `runs/<รุ่น>/skills/` เท่านั้น ห้ามเป็น global skill (ไม่เช่นนั้น Trial แบบไม่มีสกิลจะเห็นสกิลด้วย)", label="ระวัง")))

    # ----- LAB 0
    CTX.update(kicker="ภาค LAB · LAB 0 · เตรียมเครื่องมือและโจทย์", group="LAB 0")
    r = labrow["0"]
    facts = lambda r: ('<p>%s</p><div class="facts"><div><span class="fl">Trial</span>%s</div><div><span class="fl">เวลาจริง</span>%s</div>'
                       '<div><span class="fl">ผลจริง</span>%s</div></div>') % (md(r[1]), md(r[2]), md(r[3]), md(r[4]))
    add(E.divider("LAB 0", "เตรียมเครื่องมือและโจทย์", facts(r), small="ภาค LAB · 3 · ลงมือทำ"))
    t01 = "ขั้น 0.1 · สร้างสกิล `skill-optimizer`"
    add(fig("ขั้น 0.1 · สร้างสกิล `skill-optimizer` ใน 6 ขั้น", "img/g24-build-skill.png",
            "ทำบนเครื่อง ไม่ใช้ container · ที่มา: เปเปอร์ SkillOpt · รูปแบบ: [`skillopt_format.md`](skillopt_format.md)"))
    add(E.prompt_slides(prompt("ขั้น 0.1"), CTX["kicker"], t01))
    add(check("ขั้น 0.1", t01))
    ft, tt = table("ขั้น 0.1", "ไฟล์ที่ได้ใน"), table("ขั้น 0.1", "ทดสอบกับผลเดิม")
    add(S("ผลจริงขั้น 0.1: ได้เครื่องมือ 5 ไฟล์", cards(
        [("%s · %s บรรทัด" % (r[0], r[1]), r[2]) for r in ft["rows"]] +
        [("ทดสอบกับผลเดิมใน `runs/`", "<ul>%s</ul>" % "".join("<li>%s: %s</li>" % (md(r[0]), md(r[1])) for r in tt["rows"]), "ok")], 3) +
        note(eye("ขั้น 0.1")), tag="ผลของผู้สอน"))
    t02 = "ขั้น 0.2 · ติดตั้งเครื่องมือ และตรวจตัวตรวจ"
    add(nfig("n14-lab0-setup"))
    add(S("ขั้น 0.2 · ไฟล์เข้าและออก", fileflow("ขั้น 0.2", "ขั้น 0.2<small>ยังไม่วัดอะไร</small>"), cls="mid"))
    add(E.prompt_slides(prompt("ขั้น 0.2"), CTX["kicker"], t02))
    add(check("ขั้น 0.2", t02))

    # ----- LAB 1–5
    for n in range(1, 6):
        short, base, cand, figkey = LABS[n]
        lt = "LAB %d · %s" % (n, short)
        CTX.update(kicker="ภาค LAB · %s" % lt, group="LAB %d" % n)
        head = next(s["text"] for s in SECS if s["text"].startswith("LAB %d" % n))
        add(E.divider("LAB %d" % n, head.split("·", 1)[1].strip(), facts(labrow[str(n)]), small="ภาค LAB · 3 · ลงมือทำ"))
        add(nfig(figkey))
        add(S("%s · ไฟล์เข้าและออก" % lt, fileflow("LAB %d" % n, "LAB %d<small>วัด %s Trial</small>" % (n, labrow[str(n)][2])), cls="mid"))
        add(E.prompt_slides(prompt("LAB %d" % n), CTX["kicker"], lt))
        add(check("LAB %d" % n, lt))
        add(result_slide(n))
        add(fig("ประตูรับตัดสิน %s → %s อย่างไร" % (vname(base), vname(cand)), "img/r03-threshold-%s-%s.png" % (base, cand)))
        if n == 1:
            add(gate_slide(cand, CTX["kicker"], lt))
            add(fig("สกิลรุ่น `v0`: 5 บรรทัด เขียนจากความจำ", "img/d08-skill-v0.png",
                    "รุ่น `noskill` = โฟลเดอร์ `./skills` ว่าง Agent ได้รับแค่โจทย์ · ไฟล์จริง: [`runs/v0/skills/money-coder/SKILL.md`](runs/v0/skills/money-coder/SKILL.md)"))
            t = table("LAB 1", "ความรู้แฝง")
            rows = []
            for r in t["rows"]:
                m = re.search(r"(\d+)/(\d+)", r[3])
                rows.append((r[0], "`v0` เขียนว่า %s → %s" % (r[1], r[2]), int(m.group(1)), int(m.group(2)), r[3]))
            add(S("เขียนชัด Agent ทำตามได้ · เขียนกว้าง Agent ต้องเดา", bars(rows) + note(
                "\"ห้ามใช้ float\" → 12/12 · \"ตอบเป็น JSON\" → 0/12"), tag="v0 · Training Set 12 Trial"))
            continue
        add(fig("สกิลเปลี่ยนอย่างไร: `%s` → `%s`" % (base, cand), "img/d07-skill-diff-%s-%s.png" % (base, cand),
                "สกิลเต็มของรุ่นนี้: [`runs/%s/skills/money-coder/SKILL.md`](runs/%s/skills/money-coder/SKILL.md) · คลิกภาพเพื่อขยาย" % (cand, cand)))
        if n == 2:
            pp = para("LAB 2", "ข้อความที่ตัวตรวจบอกเรื่อง")
            add(tbl("ปัญหาที่ Claude พบ และจุดที่แก้ใน `v1`", table("LAB 2", "ปัญหา"),
                    post=note(pp["lines"][0], "info")))
        elif n == 3:
            ul = next(b for b in walk(sec("LAB 3")) if b["t"] == "ul" and b["items"][0].startswith("เขียนเป็นนโยบาย"))
            add(code("2 บรรทัดที่ Claude เพิ่มใน `v2`", codes("LAB 3", "markdown")[0]["text"], "markdown",
                     post=cards([("ไม่ใช่เฉลย", ul["items"][0], "ok"), ("มีขอบเขตกำกับ", ul["items"][1], "ok")], 2), maxfs=1.2))
        elif n == 4:
            pp = para("LAB 4", "ไม่มีข้อที่ผิดให้ดู")
            add(tbl("กติกากว้าง 2 ข้อ ที่ Agent บอกเองว่าต้องเดา", table("LAB 4", "กติกาใน"), pre="<p>%s</p>" % md(pp["lines"][0])))
        elif n == 5:
            qt = table("LAB 5", "คำถาม")
            add(code("สกิล `v4` ทั้งไฟล์ และเหตุผลที่ไม่ได้ผล", codes("LAB 5", "markdown")[0]["text"], "markdown",
                     post=cards([(r[0], r[1], "bad" if k == 0 else "warn") for k, r in enumerate(qt["rows"])], 2), maxfs=1.2))

    # ----- 4 · สรุป
    CTX.update(kicker="ภาค LAB · 4 · สรุปและแบบฝึกหัด", group="ภาค LAB · 4 · สรุปและแบบฝึกหัด")
    add(E.divider("4", "สรุปและแบบฝึกหัด", "<p>ผลของทุกรุ่น · บทเรียนจากผลจริง · โจทย์ให้ลองต่อ</p>", "img/s05-summary.jpg", small="ภาค LAB"))
    add(fig("เส้นทางการปรับสกิลจริง", "img/r04-path.png", "คะแนนรวมของ `noskill` `v0` `v1` `v2` `v3` `v4` และผลตัดสินของประตูรับ"))
    add(fig("คะแนนเฉลี่ยของแต่ละรุ่น", "img/r01-scores.png"))
    add(fig("ข้อตรวจ 11 แบบ: รุ่นไหนผ่านกี่ Trial", "img/r02-checks.png", "เฉพาะ Training Set · ผลรายข้อของ Validation Set ถูกปิดไว้"))
    pp = para("4.1", "รวม 108 Trial")
    add(tbl("ผลของทุกรุ่น", table("4.1", "รุ่น"), post=note(pp["lines"][0], "info")))
    add(nfig("n20-lessons"))
    add(compare_slides(CTX["kicker"]))
    add(nfig("n21-exercises"))
    add(nfig("n22-limits"))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบบท", "ถัดไป: WikiSkill",
                  '<p>ให้ AI จดสมุดความรู้ แล้วเขียนสกิลจากสมุด · ใช้งาน <code>money-coder</code> เดิม เทียบกับ Skill Optimizer → '
                  '<a href="../06_WikiSkill/README.md" target="_blank">../06_WikiSkill/README.md</a></p>'
                  '<p>รายละเอียดเต็มของบทนี้: <a href="README.md" target="_blank">README.md</a> · รูปแบบของเครื่องมือ: '
                  '<a href="skillopt_format.md" target="_blank">skillopt_format.md</a> · ทฤษฎีต้นทาง (SkillOpt): '
                  '<a href="01_theory/README.md" target="_blank">01_theory/README.md</a></p>', "img/s05-summary.jpg"))
    return E.SL


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out="Skill_Optimizer_Slides.html", title="Skill Optimizer · Slides")
