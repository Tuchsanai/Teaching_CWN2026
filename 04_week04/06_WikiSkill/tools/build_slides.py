#!/usr/bin/env python3
"""สร้างสไลด์ WikiSkill_Slides.html ของบท (ภาคทฤษฎี + ภาค LAB)

  python tools/build_slides.py            (รันบนเครื่อง จากโฟลเดอร์ของบท)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพ กราฟ หรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง โค้ด ข้อสังเกต และพรอมต์ของ LAB: อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ตัวเลขผลของแต่ละชุดสกิล: อ่านจาก runs/results.json · runs/<workspace>/status.txt · runs/<ชุด>/gate-*.txt
- ภาพอธิบายและขั้นตอนข้างภาพ: tools/slides_figures.py · เครื่องมือเรนเดอร์ (ไฟล์กลาง ไม่มีเนื้อหาเฉพาะบท): tools/slides_engine.py
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, codes, para, prompt, eye, CTX, add, note, fig, explain, tiles, cards,
                           versus, bars, tbl, code)
from slides_figures import FIGS

S = E.slide
SECS = E.load("README.md")
FIG = {f["img"]: f for f in FIGS}
OUT, TITLE = "WikiSkill_Slides.html", "WikiSkill · Slides"
TH = "01_theory/img/"

# ------------------------------------------------------------------ ผลจริงจาก runs/
RES = json.loads(E.read("runs/results.json"))


def pct(x):
    return "%.1f%%" % (x * 100)


def sc(label, part="all"):
    return pct(RES[label][part]["score"])


def perfect(label, part="all"):
    return "%d/%d" % (RES[label][part]["perfect"], RES[label][part]["n"])


def status(ws):
    """อ่าน runs/<ws>/status.txt (ข้อความที่คำสั่ง status พิมพ์) เป็นค่าที่ใช้ในสไลด์"""
    txt = E.read("runs/%s/status.txt" % ws)
    g = lambda pat: re.search(pat, txt).group(1)
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in txt.split("\n") if re.match(r"^\|\s*\d+\s*\|", l)]
    return {"base": g(r"Baseline Validation[^:]*: ([\d.]+%)"), "skill": g(r"สกิลที่ใช้งาน: (\S+)"), "trials": g(r"Inference Agent (\d+) ครั้ง"),
            "calls": g(r"Maintainer \+ Proposer (\d+) ครั้ง"), "rows": rows, "stop": txt.strip().split("\n")[-1]}


def gate(path):
    """ข้อความที่คำสั่ง gate ของ skill-optimizer พิมพ์ → (รับหรือไม่, บรรทัดรวม ถ้ามี, ข้อความทั้งหมด)"""
    txt = E.read(path).strip()
    m = re.search(r"^รวม: (\S+) → (\S+) \(([^)]+)\) · เกณฑ์ ([\d.]+) จุด", txt, re.M)
    return {"accept": "ACCEPT" in txt.split("\n")[-1], "sum": m.groups() if m else None, "txt": txt}


def eyes(prefix):
    """ข้อสังเกต (👀) ทุกข้อของหัวข้อ เรียงตามลำดับใน README"""
    return [" ".join([b["lines"][0][1:].strip()] + b["lines"][1:]) for b in walk(sec(prefix))
            if b["t"] == "p" and b["lines"][0].startswith("👀")]


def tabh(prefix, col, start):
    """ตารางในหัวข้อ prefix ที่หัวคอลัมน์ลำดับ col ขึ้นต้นด้วย start (ใช้เมื่อหัวคอลัมน์แรกว่างหรือซ้ำกัน)"""
    for b in walk(sec(prefix)):
        if b["t"] == "table" and len(b["head"]) > col and E.plain(b["head"][col]).startswith(start):
            return b
    raise KeyError("ไม่พบตารางที่คอลัมน์ %d ขึ้นต้นด้วย %r ในหัวข้อ %r" % (col, start, prefix))


def nfig(key, post=""):
    f = FIG[key]
    return explain(f["title"], "img/%s.jpg" % key, f["steps"], post)


def wide(title, src, below, cap="", tag=""):
    """ภาพแนวนอนกว้าง + ชิ้นส่วนด้านล่าง (การ์ดหรือตัวเลข)"""
    b = {"t": "img", "src": src, "alt": E.plain(title)}
    return S(title, E.fig_html(b, True) + below + ('<p class="cap">%s</p>' % md(cap) if cap else ""), tag=tag, maxfs=1.15)


def term(path):
    return E.pre_html(E.read(path).strip(), "text", "term")


def ul(items):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % md(x) for x in items)


# รายการตรวจผลของแต่ละ LAB · เรียบเรียงจากตาราง Input/Output พรอมต์ และ "ผลจริง" ของ LAB นั้นใน README.md
CHECKS = {
    "ขั้น 0.1": {
        "items": [
            "มีโฟลเดอร์ `Teaching/my-wikiskill/` และมีไฟล์ครบ: `SKILL.md` · `scripts/wikiskill.py` · `prompts/` 3 ไฟล์ (`maintainer` `proposer` `proposer_nowiki`) · `references/source.md` · `references/workspace.md`",
            "`scripts/wikiskill.py` มีครบ 8 คำสั่ง: `init` `baseline` `rollout` `maintain` `propose` `gate` `loop` `status`",
            "`references/source.md` มีตาราง ส่วนของสกิล | มาจากข้อไหนของเปเปอร์ | เหมือนหรือต่าง",
            "ทดสอบ (ก): `status` ของทุก workspace ใน `runs/` พิมพ์ตรงกับ `status.txt`",
            "ทดสอบ (ข): Apply `proposal.json` ที่เก็บไว้ใหม่ ได้ `candidate/skills` และ `proposal.diff` เหมือนที่เก็บไว้",
            "ทดสอบ (ค): วงรอบจำลอง 2 รอบ ได้ ACCEPTED 1 รอบ และ REJECTED 1 รอบ · รอบที่ถูกปฏิเสธ `skills` คงเดิม แต่ `wiki` ยังอยู่ครบ",
        ],
        "ref": "ผลของผู้สอน: ใช้ 21 นาที · ไม่เรียกโมเดลอื่น · ได้ 7 ไฟล์ (`scripts/wikiskill.py` 1,144 บรรทัด) · ทดสอบผ่านทั้ง 3 ข้อ",
        "note": "เครื่องมือที่สร้างเองไม่ต้องเหมือนใครทุกบรรทัด สิ่งที่ต้องตรงคือ **รูปแบบ** ใน `wikiskill_format.md` · การเรียกโมเดลจริงยังไม่ได้ทดสอบในขั้นนี้ (รู้ผลใน LAB 1)",
    },
    "ขั้น 0.2": {
        "items": [
            "รายงานเป็นตาราง รายการ | ผล",
            "`my-wikiskill` ถูกติดตั้งเป็น global skill ชื่อ `wikiskill` ของบัญชี yolo (อยู่ข้างสกิล `skill-optimizer` ของบท 05)",
            "ใน container มี `/workspace/wklab/suite/` และ `/workspace/wklab/runs/so-v3/skills/`",
            "`suite/check_grader.py` ผ่าน: เฉลยอ้างอิงผ่าน 10/10 แปดโจทย์ และ 11/11 โจทย์ค่าส่ง",
            "มีบัญชี `yolo` ที่ล็อกอินแล้วอย่างน้อย 1 บัญชี",
        ],
        "ref": "ผลของผู้สอน: ติดตั้งสกิล ✅ · มี `skill-optimizer` อยู่แล้ว ✅ · ตัวตรวจผ่าน ✅ · บัญชีที่ใช้ได้ `yolo1` `yolo2` `yolo3` · ใช้ 1 นาที",
        "note": "ตรวจตัวตรวจก่อนเสมอ ถ้าเครื่องวัดผิด ตัวเลขหลังจากนี้ใช้ไม่ได้ทั้งหมด",
    },
    "LAB 1": {
        "items": [
            "`runs/w1/raw/iter-01/` มี Trace ของ Training 12 ไฟล์ และ `summary.md`",
            "`runs/w1/wiki/` มี `index.md` · `log.md` · `skill-impact.md` และหน้าใน `patterns/`",
            "`runs/w1/skills/` มีสกิลที่วงรอบสร้าง (โฟลเดอร์ละ 1 สกิล มี `SKILL.md`)",
            "`runs/w1/status.txt` มีตารางของทุกรอบ และบรรทัด `สถานะ:` ที่บอกเหตุผลที่วงรอบหยุด",
            "รายงานมีตาราง ขั้น | ชั้นที่เปลี่ยน | ไฟล์ที่เกิดหรือเปลี่ยน | สรุป 1 บรรทัด",
            "ผลของ Validation Set ที่เก็บลงเครื่อง มีแค่คะแนนและต้นทุน (ไม่มีผลรายข้อ)",
        ],
        "ref": "ผลของผู้สอน: Validation 45.0% → 93.3% → 100.0% ใน 2 รอบ · ข้อเสนอผ่าน Gate ทั้ง 2 ครั้ง · สกิล `solve-py-contract` · 42 Trial · ใช้ 15 นาที",
    },
    "LAB 2": {
        "items": [
            "`runs/noskill/trials/` · `runs/so-v3/trials/` · `runs/w1/trials/` มีชุดละ 27 โฟลเดอร์ (9 โจทย์ × 3 รอบ) รวม 81 Trial",
            "`runs/report.md` มีตารางเทียบ 3 ชุด · `runs/results.json` ถูกเขียน",
            "`runs/w1/gate-noskill.txt` และ `runs/w1/gate-so-v3.txt` มีบรรทัด `ผล:` ของการตัดสิน",
            "`runs/w1/failures.txt` มีข้อตรวจที่ `w1` ยังไม่ผ่าน ของชุด train และชุด test",
            "ผลรายข้อของ Test Set ถูกเปิดหลังวัดครบทั้ง 3 ชุดแล้วเท่านั้น",
        ],
        "ref": "ผลของผู้สอน: ไม่มีสกิล 46.9% · `so-v3` 100.0% · `w1` 97.9% (Test 100.0%) · `noskill` → `w1` ACCEPT · `so-v3` → `w1` REJECT · `policy` 0/6 · ใช้ 6 นาที",
    },
    "LAB 3": {
        "items": [
            "`runs/w2/` เป็น workspace ใหม่ มี `raw/` `wiki/` `skills/` และ `status.txt`",
            "`loop` ถูกเริ่ม **ครั้งเดียว** และรันจนวงรอบหยุดเอง",
            "`runs/w2/trials/` มี 27 โฟลเดอร์ · `runs/report.md` มี 4 ชุด (`noskill` `so-v3` `w1` `w2`)",
            "รายงานมีตารางเทียบ `w1` กับ `w2`: จำนวนรอบ · pattern ใน `wiki/index.md` · ข้อเสนอและผลตัดสิน · คะแนน",
            "รายงานบอกสิ่งที่เหมือนกันและสิ่งที่ต่างกัน",
        ],
        "ref": "ผลของผู้สอน: `w2` ใช้ 1 รอบ (Validation 100.0% ตั้งแต่รอบแรก) · สกิล `solve-py-deliverable` 76 บรรทัด · รวม 96.8% · Test 97.8% · `policy` 0/6 · ใช้ 12 นาที",
    },
    "LAB 4": {
        "items": [
            "`runs/n1/` มี `raw/` และ `skills/` แต่ **ไม่มี** `wiki/`",
            "บรรทัดแรกของ `runs/n1/status.txt` ลงท้ายด้วย `wiki: ไม่ใช้`",
            "`runs/n1/trials/` มี 27 โฟลเดอร์ · `runs/report.md` มี 5 ชุด",
            "รายงานมีตารางเทียบ `n1` กับ `w1` และ `w2`: จำนวนรอบ · จำนวน Trial · จำนวนการเรียกโมเดลของผู้ปรับสกิล · คะแนน",
            "รายงานบอกสิ่งที่ `n1` ไม่มีเมื่อจบ",
        ],
        "ref": "ผลของผู้สอน: `n1` ใช้ 1 รอบ · 24 Trial · เรียกโมเดลของผู้ปรับสกิล 5 ครั้ง · รวม 95.7% · Test 95.6% · เหลือสกิลอย่างเดียว · ใช้ 7 นาที",
    },
    "ขั้น 5.1": {
        "items": [
            "`runs/w1p/skills/` = สกิลของ `w1` ที่แก้ไม่เกิน 3 จุด · ไฟล์ใน `runs/w1` ไม่ถูกแก้",
            "นโยบายถูกเขียนเป็นนโยบายของร้าน ไม่มี Input หรือคำตอบของข้อตรวจ",
            "`runs/w1p/trials/` มี 27 โฟลเดอร์ · วัดด้วยค่าเดียวกับ LAB 2",
            "`runs/w1p/gate-w1.txt` และ `runs/w1p/gate-so-v3.txt` มีบรรทัด `ผล:`",
            "ถ้า REJECT: ไม่แก้ `w1p` เพิ่ม และไม่วัดซ้ำเพื่อให้ผ่าน (ไปขั้น 5.2)",
        ],
        "ref": "ผลของผู้สอน: Training 95.2% → 100.0% (`policy` 0/6 → 6/6) · Validation 100.0% → 96.7% · Test 100.0% → 93.3% · รวม 97.9% → 97.0% · REJECT",
    },
    "ขั้น 5.2": {
        "items": [
            "`runs/w1q/skills/` สร้างจาก `runs/w1/skills` (ไม่ใช่จาก `w1p`) · แก้ไม่เกิน 3 จุด",
            "นโยบายแต่ละข้อมีขอบเขต: ค่าส่งใช้กับฟังก์ชันคิดค่าส่งเท่านั้น · เงินคืนใช้กับฟังก์ชันคิดเงินคืนสมาชิกเท่านั้น",
            "`runs/w1q/trials/` มี 27 โฟลเดอร์",
            "`runs/w1q/gate-w1.txt` และ `runs/w1q/gate-so-v3.txt` มีบรรทัด `ผล:` · `runs/report.md` มี 7 ชุด",
            "รายงานมีจุดที่แก้ใน `w1q` เทียบกับ `w1p`",
        ],
        "ref": "ผลของผู้สอน: Training · Validation · Test 100.0% ทั้ง 3 ชุด (ผ่านครบ 27/27) · รวม 97.9% → 100.0% (+2.1 จุด · เกณฑ์ 2.0) · `w1` → `w1q` ACCEPT · `so-v3` → `w1q` REJECT (โทเคนขาเข้ามากกว่า 12%)",
    },
}
VARY = ("ตัวเลขของคุณอาจต่างจากของผู้สอน เพราะ AI ไม่ตอบเหมือนกันทุกครั้ง (LAB 3 แสดงให้เห็น) · "
        "สิ่งที่ต้องมีเหมือนกันคือไฟล์ผล และรูปแบบของ `status` กับ `gate`")


def check(key, title):
    c = CHECKS[key]
    return E.check_slide(key, c["items"], c["ref"], c.get("note") or VARY, title)


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    agenda = table("WikiSkill ·", "ภาค")
    labtab = table("3 ·", "LAB")
    labrow = {re.match(r"\[(\d)\]", r[0]).group(1): r for r in labtab["rows"]}
    facts = lambda r: ('<p>%s</p><div class="facts"><div><span class="fl">Trial</span>%s</div><div><span class="fl">เวลาจริง</span>%s</div>'
                       '<div><span class="fl">ผลจริง</span>%s</div></div>') % (md(r[1]), md(r[2]), md(r[3]), md(r[4]))
    total = re.search(r"รวม (\d+) Trial", para("4.1", "รวม")["lines"][0]).group(1)

    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    t = SECS[0]["text"].split("·")
    add(E.cover(t[0].strip(), "·".join(t[1:]).strip(), "img/g01-cover.jpg", small="03_week03 · บทที่ 06"))

    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("ทั้งเรื่องในภาพเดียว: ไม่มีคนเขียนสกิล ได้ %s · คนตอบคำถาม 4 ข้อ ได้ %s" % (sc("w1"), sc("w1q")), "img/r03-all.png",
            "ผลจริงจาก %s Trial · `w1` = สกิลที่ WikiSkill สร้างเองจากชุดสกิลว่าง · `w1q` = `w1` + นโยบายธุรกิจที่ทีมตอบ · ที่มาของแต่ละแท่งอยู่ในภาค LAB" % total))
    add(wide("WikiSkill ใน 4 ขั้น: ทำโจทย์ → จดลงสมุดความรู้ → เขียนสกิลจากสมุด → วัดแล้วตัดสิน", "img/d00-story.png",
             '<p class="bigsub" style="text-align:center">ต่างจากบท 05 ที่จุดเดียว: <b>ไม่มีคนเขียนสกิล</b> ระบบเริ่มจากชุดสกิลว่างและสมุดว่าง</p>',
             "สกิลที่ไม่ผ่านถูกทิ้ง แต่สิ่งที่จดลงสมุดความรู้ยังอยู่ · ทำซ้ำจนคะแนน Validation เต็ม หรือครบจำนวนรอบ"))
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
        "ทฤษฎีจากงานวิจัยต้นทาง (WikiSkill) อ่านเพิ่มได้ที่ [`01_theory/README.md`](01_theory/README.md) · "
        "รายละเอียดเต็มของทุกหัวข้ออยู่ใน [`README.md`](README.md)", "info"), cls="mid"))
    add(S("วิธีใช้สไลด์นี้", cards([
        ("ไปหน้าถัดไป / ก่อนหน้า", '<p><span class="kbd">→</span> <span class="kbd">Space</span> / <span class="kbd">←</span> หรือปุ่มมุมขวาล่าง</p>'),
        ("สารบัญทุกหน้า", '<p><span class="kbd">O</span> แล้วคลิกหน้าที่ต้องการ · <span class="kbd">F</span> เต็มจอ</p>'),
        ("ขยายภาพ", "คลิกที่ภาพ · คลิกอีกครั้งหรือ Esc เพื่อปิด"),
        ("คัดลอกพรอมต์ของ LAB", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** ให้ข้อความเดียวกับ `README.md` ตรงตัวอักษร แม้พรอมต์ถูกแบ่งแสดง 2 หน้า", "warn"),
        ("ตรวจผลหลังรัน", "สไลด์ **ตรวจผลของคุณ** ต่อจากพรอมต์ทุก LAB · ติ๊กได้ และจำค่าไว้ในเบราว์เซอร์นี้", "warn"),
        ("เปิดไฟล์จริง", "ลิงก์สีน้ำเงินเปิดไฟล์ในโฟลเดอร์ของบท · เปิดสไลด์จากโฟลเดอร์ `06_WikiSkill`"),
    ]), cls="mid"))

    # ===== ภาคทฤษฎี
    CTX.update(kicker="", group="ภาคทฤษฎี")
    alert = next(b for b in sec("ภาคทฤษฎี") if b["t"] == "alert")
    add(E.divider("ภาคทฤษฎี", "โจทย์ (ฉบับย่อ) และ WikiSkill", "".join(E.render(x) for x in alert["blocks"]), "img/s01-theory.jpg"))

    # ----- 1 · โจทย์ (ฉบับย่อ)
    CTX.update(kicker="ภาคทฤษฎี · 1 · โจทย์ (ฉบับย่อ)", group="ภาคทฤษฎี · 1 · โจทย์ (ฉบับย่อ)")
    add(E.divider("1", "โจทย์ (ฉบับย่อ)", "<p>โจทย์เดิมของบท 05 คืออะไร · บทนี้เปลี่ยนอะไร</p>", small="ภาคทฤษฎี"))
    add(fig("โจทย์เดิมของบท 05: Agent ไม่ได้รับความรู้แฝงของทีม แต่ตัวตรวจรู้ครบ", "img/d01-problem.png", para("1 ·", "บทนี้ใช้")["lines"][0]))
    add(nfig("n01-what-changed"))
    tt = table("1.2", "โจทย์")
    add(S("Test Set 3 ข้อ: โจทย์ที่ไม่เคยถูกใช้ปรับสกิลทั้งสองวิธี", cards([(r[0], "<p>%s</p><p>%s</p>" % (md(r[1]), md(r[2]))) for r in tt["rows"]], 3) +
          note(para("1.2", "Test Set ตรวจ")["lines"][0], "info"), tag="suite/suite.json", cls="mid"))

    # ----- 2 · WikiSkill
    CTX.update(kicker="ภาคทฤษฎี · 2 · WikiSkill", group="ภาคทฤษฎี · 2 · WikiSkill")
    add(E.divider("2", "WikiSkill", "<p>WikiSkill คืออะไร · ทำงานอย่างไร · นำมาใช้กับโจทย์นี้อย่างไร</p>"
                  "<p><b>สกิลเป็นเพียงฉบับย่อของความรู้ ณ ขณะหนึ่ง</b> เหตุผล หลักฐาน และสิ่งที่เคยลองแล้วไม่ได้ผล ต้องมีที่อยู่ของตัวเอง</p>",
                  "img/s02-wikiskill.jpg", small="ภาคทฤษฎี"))
    p21 = para("2.1", "วิธีปรับสกิล")["lines"]
    add(explain("ปัญหา: ความรู้ของแต่ละรอบหายไป", TH + "g02-forget-vs-remember.png",
                [p21[0], p21[1]] + ["**%s**: %s" % (r[0], r[1]) for r in table("2.1", "อาการ")["rows"]]))
    add(explain("แนวคิด: มีสมุดความรู้คั่นกลาง", TH + "g01-three-layers.png",
                ["%s ตอบว่า %s · %s · ผู้ใช้: %s" % tuple(r) for r in tabh("2.2", 1, "ตอบคำถาม")["rows"]] +
                [para("2.2", "สกิลเป็นเพียง")["lines"][0]]))
    add(fig("สถาปัตยกรรม 3 ชั้น: สกิลย้อนกลับได้ แต่ Wiki มีแต่เพิ่ม", TH + "t03-layers.png",
            " · ".join("**%s** `%s` %s" % (r[0], E.plain(r[1]), r[3]) for r in table("2.3", "ชั้น")["rows"])))
    add(fig("ส่วนประกอบ 4 ตัว และสิทธิ์ต่อแต่ละชั้น", TH + "t04-roles.png",
            "แต่ละส่วนประกอบอ่านและเขียนได้เฉพาะบางชั้น · Inference Agent อ่านได้แค่ **Skills Layer**"))
    add(explain("ใครทำอะไร: ส่วนประกอบ 4 ตัว", TH + "g05-two-roles.png",
                ["%s: %s (เรียกโมเดล: %s)" % tuple(r) for r in table("2.4", "ส่วนประกอบ")["rows"]]))
    add(fig("หนึ่งรอบของ WikiSkill ด้วยตัวเลขจริง", TH + "t05-iteration.png", para("2.5", "ตัวเลขในภาพ")["lines"][0]))
    add(fig("Algorithm 1 ทีละบรรทัด", TH + "t06-algorithm.png",
            "เครื่องมือ `wikiskill` ที่สร้างใน LAB 0 ทำตามอัลกอริทึมนี้ทุกบรรทัด · คำสั่งของแต่ละบรรทัดอยู่ใน [`wikiskill_format.md`](wikiskill_format.md)"))
    rt = table("2.7", "กติกา")
    add(S("กติกา 3 ข้อที่ทำให้ WikiSkill ต่างจากวงรอบทั่วไป", cards([((k + 1, re.sub(r"^\d+\s*", "", r[0])), r[1]) for k, r in enumerate(rt["rows"])], 3) +
          note(para("2.7", "เหตุผลของการออกแบบ")["lines"][0], "info"), cls="mid"))
    add(fig("กติกาข้อ 1–2: สกิลย้อนกลับได้ แต่ความรู้ไม่หาย", TH + "g03-rollback.png",
            "สกิลที่ไม่ผ่านถูกทิ้ง ใช้ของเดิม · Wiki จดไว้ว่าเคยลองแล้วไม่ผ่าน"))
    add(fig("กติกาข้อ 3: คนทำงานอ่านแค่คู่มือ", TH + "g04-agent-no-wiki.png",
            "Agent อ่านเฉพาะสกิล · Wiki อยู่หลังร้าน Agent ไม่เห็น"))
    add(nfig("n02-paper-vs-chapter"))
    last = table("2.8", "ประเด็น")["rows"][-1]
    add(S("จุดที่บทนี้เพิ่มจากเปเปอร์ คือคำถามหลักของภาค LAB",
          '<p class="bigq">นโยบายธุรกิจ มีใน Training 2 ข้อ<br>แต่ <em>ไม่มีใน Validation</em></p>'
          '<p class="bigsub">%s · ในเปเปอร์: %s · ในบทนี้: %s<br>%s</p>' % (
              md(last[0]), md(last[1]), md(last[2]), md(para("2.8", "แถวสุดท้าย")["lines"][0])), cls="mid", maxfs=1.2))
    add(S("คำถาม 5 ข้อที่ภาค LAB จะตอบ", cards([((r[0], "LAB " + r[2]), r[1]) for r in table("2.9", "#")["rows"]], 3), cls="mid"))

    # ===== ภาค LAB
    CTX.update(kicker="", group="ภาค LAB")
    alert = next(b for b in sec("ภาค LAB") if b["t"] == "alert")
    add(E.divider("ภาค LAB", "ลงมือทำ 6 ขั้น และสรุปผล", "".join(E.render(x) for x in alert["blocks"]), "img/s03-lab.jpg"))
    CTX.update(kicker="ภาค LAB · 3 · ลงมือทำ", group="ภาค LAB · 3 · ลงมือทำ")
    add(fig("ภาค LAB: ลงมือทำ 6 ขั้น", "img/d03-lab-map.png",
            "LAB 0 สร้างเครื่องมือ · LAB 1 รันทีละขั้น · LAB 2 วัดสกิลที่ได้ · LAB 3 รันซ้ำ · LAB 4 ตัด Wiki ออก · LAB 5 เติมความรู้จากทีม"))
    use = para("3 ·", "**วิธีใช้:**")["lines"]
    tip = next(b for b in walk(sec("ภาค LAB")) if b["t"] == "p" and b["lines"][0].startswith("ผลจริงทุกตัว"))["lines"][0]
    add(S("ก่อนเริ่ม LAB", cards([
        ("วิธีใช้", use[0].replace("**วิธีใช้:**", "").strip().replace("📋 ", ""), "warn"),
        ("ต้องมี", use[1].replace("**ต้องมี:**", "").strip(), "warn"),
        ("ผลจริงในสไลด์", tip, "navy")], 3) + note(
        "ทุก LAB มีลำดับเดียวกัน: ภาพขั้นตอน → ไฟล์เข้าและออก → พรอมต์ (คัดลอก) → ตรวจผลของคุณ → ผลจริงของผู้สอน", label="ลำดับ"), cls="mid"))
    add(nfig("n03-experiment-plan"))
    add(code("โครงสร้างโฟลเดอร์: 1 การรัน WikiSkill = 1 workspace = 1 โฟลเดอร์", codes("โครงสร้างโฟลเดอร์")[0]["text"],
             post=note("สกิลที่วงรอบสร้าง อยู่ใน `runs/<workspace>/skills/` เท่านั้น ห้ามเป็น global skill · ที่ทำงานใน container คือ `/workspace/wklab/`", label="ระวัง")))

    # ----- LAB 0
    CTX.update(kicker="ภาค LAB · LAB 0 · เตรียมเครื่องมือและโจทย์", group="LAB 0")
    add(E.divider("LAB 0", "เตรียมเครื่องมือและโจทย์", facts(labrow["0"]), small="ภาค LAB · 3 · ลงมือทำ"))
    t01 = "ขั้น 0.1 · สร้างสกิล `wikiskill`"
    add(fig("ขั้น 0.1 · สร้างสกิล `wikiskill` ใน 6 ขั้น", "img/d02-build-skill.png",
            "ทำบนเครื่อง ไม่ใช้ container · ที่มา: เปเปอร์ WikiSkill · รูปแบบ: [`wikiskill_format.md`](wikiskill_format.md)"))
    add(E.prompt_slides(prompt("ขั้น 0.1"), CTX["kicker"], t01))
    add(check("ขั้น 0.1", t01))
    ft = table("ขั้น 0.1", "ไฟล์ที่ได้ใน")
    add(S("ผลจริงขั้น 0.1: ได้เครื่องมือ %d ไฟล์" % len(ft["rows"]),
          cards([(r[0], "**%s บรรทัด** · %s" % (r[1], r[2])) for r in ft["rows"]], 3) +
          note(para("ขั้น 0.1", "**ผลจริง**")["lines"][0].replace("**ผลจริง** · ", ""), "info"), tag="ผลของผู้สอน"))
    tst = table("ขั้น 0.1", "ทดสอบ")
    add(S("ผลจริงขั้น 0.1: ทดสอบ 3 ข้อโดยไม่เรียกโมเดล", cards(
        [(r[0], r[1], "warn" if "⚠️" in r[1] else "ok") for r in tst["rows"]], 2) + note(eye("ขั้น 0.1")), tag="ผลของผู้สอน"))
    t02 = "ขั้น 0.2 · ติดตั้งเครื่องมือ และตรวจตัวตรวจ"
    add(nfig("n04-lab0-setup"))
    add(S("ขั้น 0.2 · ไฟล์เข้าและออก", E.fileflow(table("ขั้น 0.2", "Input"), "ขั้น 0.2<small>ยังไม่วัดอะไร</small>",
                                                out_label="OUTPUT · สิ่งที่ได้ใน container"), cls="mid"))
    add(E.prompt_slides(prompt("ขั้น 0.2"), CTX["kicker"], t02))
    add(check("ขั้น 0.2", t02))

    # ----- LAB 1
    def lab_open(n, figkey, mid):
        head = next(s["text"] for s in SECS if s["text"].startswith("LAB %d" % n))
        lt = "LAB %d · %s" % (n, re.sub(r"\s*\(.*?\)\s*$", "", head.split("·", 1)[1].strip()).split(":")[0])
        CTX.update(kicker="ภาค LAB · " + head, group="LAB %d" % n)
        add(E.divider("LAB %d" % n, head.split("·", 1)[1].strip(), facts(labrow[str(n)]), small="ภาค LAB · 3 · ลงมือทำ"))
        if figkey:
            add(nfig(figkey))
            add(S("%s · ไฟล์เข้าและออก" % lt, E.fileflow(table("LAB %d" % n, "Input"), "LAB %d<small>%s</small>" % (n, mid)), cls="mid"))
            add(E.prompt_slides(prompt("LAB %d" % n), CTX["kicker"], lt))
            add(check("LAB %d" % n, lt))
        return lt

    lab_open(1, "n05-lab1-steps", "วงรอบของ WikiSkill · %s Trial" % labrow["1"][2])
    st = status("w1")
    r1, r2 = st["rows"][0], st["rows"][1]
    e1 = eyes("LAB 1")
    add(S("ผลจริง LAB 1: ไม่มีใครบอกกฎ Validation จาก %s เป็น %s ใน 2 รอบ" % (st["base"], r2[7]), tiles([
        ("ชุดสกิลว่าง (baseline)", st["base"], "Validation = R_best เริ่มต้น", ""),
        ("หลังรอบที่ 1", r1[7], "%s · **%s**" % (r1[6], r1[9]), "ok"),
        ("หลังรอบที่ 2", r2[7], "%s · **%s** → หยุด" % (r2[6], r2[9]), "ok"),
        ("Trial ของ Inference Agent", st["trials"], "Maintainer + Proposer %s ครั้ง" % st["calls"], "warn")]) + note(e1[0]),
        tag="runs/w1/status.txt", cls="mid"))
    add(fig("เส้นทางของ `w1`: Validation ของชุดสกิลว่าง แล้วสกิลที่เสนอในแต่ละรอบ", "img/r01-path-w1.png",
            para("LAB 1", "**ผลจริง:**")["lines"][0].replace("**ผลจริง:** ", "")))
    add(tbl("รอบที่ 1 ทีละขั้น: แต่ละคำสั่งเปลี่ยนชั้นใด", table("LAB 1", "ขั้น")))
    add(fig("สมุดความรู้ของ `w1` เมื่อจบ: `wiki/index.md` 7 บรรทัด", "img/d04-wiki-w1.png", e1[1]))
    x2 = tabh("LAB 1", 1, "รอบที่ 1")
    add(S("รอบที่ 2: Wiki ทำงานข้ามรอบ จึงอ่านน้อยลงและแก้เฉพาะจุด", cards([
        ("รอบที่ 1 · Wiki ว่าง", ul("**%s**: %s" % (r[0], r[1]) for r in x2["rows"])),
        ("รอบที่ 2 · มี Wiki ของรอบที่ 1", ul("**%s**: %s" % (r[0], r[2]) for r in x2["rows"]), "ok")], 2), tag="runs/w1/history", cls="mid"))
    add(code("สิ่งที่รอบที่ 2 แก้ในสกิล: เกณฑ์จำนวนเทสต์", codes("LAB 1", "diff")[0]["text"], "diff",
             post=note("diff นี้โปรแกรมจดไว้ใน [`wiki/skill-impact.md`](runs/w1/wiki/skill-impact.md) · ข้อเสนอรอบที่ 1 เป็น `create` ทั้งสกิล รอบที่ 2 เป็น `patch` เฉพาะส่วนเทสต์", "info")))
    add(fig("สกิลที่ได้ทั้งไฟล์: `%s` (107 บรรทัด)" % st["skill"], "img/d05-skill-w1.png",
            "ไฟล์จริง: [`SKILL.md`](runs/w1/skills/solve-py-contract/SKILL.md) · [`PURPOSE.md`](runs/w1/skills/solve-py-contract/PURPOSE.md) (สกิลนี้แก้ pattern ใดใน Wiki) · คลิกภาพเพื่อขยาย"))

    # ----- LAB 2
    lab_open(2, "n06-lab2-steps", "วัด 3 ชุดสกิล · %s Trial" % labrow["2"][2])
    e2 = eyes("LAB 2")
    pol = RES["w1"]["train"]["checks"]["policy"]
    add(S("ผลจริง LAB 2: สกิลที่ไม่มีคนเขียน ได้ %s บน Test Set" % sc("w1", "test"), tiles([
        ("ไม่มีสกิล", sc("noskill"), "ผ่านครบทุกข้อ %s" % perfect("noskill"), ""),
        ("`so-v3` · Skill Optimizer", sc("so-v3"), "ผ่านครบทุกข้อ %s" % perfect("so-v3"), ""),
        ("`w1` · WikiSkill", sc("w1"), "ผ่านครบทุกข้อ %s" % perfect("w1"), "ok"),
        ("Test Set ของ `w1`", sc("w1", "test"), "`so-v3` %s · ไม่มีสกิล %s" % (sc("so-v3", "test"), sc("noskill", "test")), "ok"),
        ("ข้อตรวจ `policy` ของ `w1`", pol, "งานค่าส่งและงานเงินคืน", "bad")]) + note(e2[0]), tag="runs/results.json", cls="mid"))
    add(fig("คะแนนของสกิล 3 ชุดบนโจทย์ 9 ข้อ", "img/r02-compare.png", "ไม่มีสกิล · `so-v3` (Skill Optimizer บท 05) · `w1` (WikiSkill) · ชุดละ 27 Trial"))
    g0, g3 = gate("runs/w1/gate-noskill.txt"), gate("runs/w1/gate-so-v3.txt")
    gt = table("LAB 2", "gate")
    add(S("gate ของบท 05 ตัดสิน: ดีกว่าไม่มีสกิลมาก แต่ยังแทน `v3` ไม่ได้", cards([
        (r[0], r[1], "ok" if g["accept"] else "bad") for r, g in zip(gt["rows"], (g0, g3))], 2) +
        '<p>ข้อความที่คำสั่ง <code>gate</code> พิมพ์จริง (<a href="runs/w1/gate-so-v3.txt" target="_blank"><code>runs/w1/gate-so-v3.txt</code></a>)</p>' +
        E.pre_html(g3["txt"], "text", "term"), tag="runs/w1/gate-*.txt", maxfs=1.2))
    add(fig("สกิลแต่ละชุดครอบคลุมความรู้ข้อใด", "img/r05-coverage.png",
            "`w1` ผ่านมาตรฐานการเขียนโค้ดครบ แต่นโยบายธุรกิจ **%s** · (ภาพนี้มี `w1p` และ `w1q` ของ LAB 5 ด้วย)" % pol))
    kt = table("LAB 2", "ความรู้แฝง")
    add(S("ข้อเดียวที่ `w1` ยังไม่ผ่าน คือ `policy`", E.pre_html(codes("LAB 2", "text")[1]["text"], "text", "term") + cards([
        (r[0] + " · " + E.plain(r[1]), r[2], "ok" if "ได้ครบ" in r[1] else "bad") for r in kt["rows"]], 2) + note(e2[1]),
        tag="runs/w1/failures.txt", maxfs=1.2))

    # ----- LAB 3
    lab_open(3, "n07-lab3-steps", "วงรอบใหม่ + วัดสกิล · %s Trial" % labrow["3"][2])
    e3 = eyes("LAB 3")
    s2 = status("w2")
    add(fig("เส้นทางของ `w2`: สกิลที่เสนอในรอบแรกได้ Validation %s วงรอบจึงหยุด" % s2["rows"][0][7], "img/r01-path-w2.png",
            "ค่าทุกตัวเหมือน `w1` · สกิลที่ได้ชื่อ `%s` · %s" % (s2["skill"], s2["stop"])))
    add(tbl("รันซ้ำด้วยค่าเดิม: ผลรวมใกล้กัน แต่เส้นทางต่างกัน", tabh("LAB 3", 1, "w1"), post=note(e3[0])))
    add(S("`w2` หยุดเร็วกว่า เพราะ Validation ผ่านครบตั้งแต่รอบแรก",
          '<p class="bigq">Validation 6 Trial ผ่านครบ<br><em>ไม่ได้แปลว่าสกิลครบ</em></p>' + note(e3[1]), cls="mid", maxfs=1.2))

    # ----- LAB 4
    lab_open(4, "n08-lab4-steps", "วงรอบแบบไม่ใช้ wiki + วัดสกิล · %s Trial" % labrow["4"][2])
    e4 = eyes("LAB 4")
    add(fig("เส้นทางของ `n1`: ไม่มี Wiki สกิลที่เสนอในรอบแรกได้ Validation 100% วงรอบจึงหยุด", "img/r01-path-n1.png",
            para("LAB 4", "เปเปอร์รายงาน")["lines"][0]))
    at = {r[0]: r for r in tabh("LAB 4", 1, "มี Wiki")["rows"]}
    tile = lambda k, tone="": (k, at[k][3].replace("**", ""), "`w1` %s · `w2` %s" % (at[k][1].replace("**", ""), at[k][2]), tone)
    add(S("ผลจริง LAB 4: ตัด Wiki ออก คะแนนไม่ต่างกันชัดเจน", tiles([
        tile("คะแนนรวม 27 Trial"), tile("Test Set"), tile("รอบที่ใช้"), tile("การเรียกโมเดลของผู้ปรับสกิล", "ok"),
        tile("Trial ที่เทสต์ไม่ถึง 6 ข้อ", "bad")]) + note(e4[0]), tag="ไม่มี Wiki · n1", cls="mid"))
    heads = tabh("LAB 4", 1, "มี Wiki")["head"]
    add(S("สิ่งที่ต่างชัดคือสิ่งที่เหลือเมื่อจบ", cards([
        (heads[k], ul(["**เหลือ**: " + at["สิ่งที่เหลือเมื่อจบ"][k], "**เรื่องนโยบายธุรกิจ**: " + at["เรื่องนโยบายธุรกิจ"][k]]), "bad" if k == 3 else "ok")
        for k in (1, 2, 3)], 3) + note(e4[1]), cls="mid"))

    # ----- LAB 5
    lt = lab_open(5, "", "")
    add(explain("ความรู้บางอย่างไม่อยู่ใน Trace: ต้องถามทีม", TH + "g06-ask-team.png", [
        "WikiSkill หานโยบายธุรกิจเองไม่ได้ แต่ Wiki จดไว้ว่าต้องถามอะไร",
        "ผู้เรียนรับบทคนในทีม ตอบเรื่องที่ Wiki จดว่ายังไม่ยืนยัน",
        "เติมลงสกิลด้วยวิธีของบท 05: แก้ไม่เกิน 3 จุด → วัด → gate"]))
    add(nfig("n09-lab5-steps"))
    for step, ws, name in (("ขั้น 5.1", "w1p", "เติมนโยบาย 4 ข้อ (`w1p`)"), ("ขั้น 5.2", "w1q", "กำกับขอบเขตของนโยบาย (`w1q`)")):
        title = "%s · %s" % (step, name)
        g = gate("runs/%s/gate-w1.txt" % ws)
        add(S("%s · ไฟล์เข้าและออก" % step, E.fileflow(table(step, "Input"), "%s<small>วัด 27 Trial</small>" % step), cls="mid"))
        add(E.prompt_slides(prompt(step), CTX["kicker"], title))
        add(check(step, title))
        d = lambda part: "จาก %s · **%+.1f จุด**" % (sc("w1", part), (RES[ws][part]["score"] - RES["w1"][part]["score"]) * 100)
        tone = lambda part: "bad" if RES[ws][part]["score"] < RES["w1"][part]["score"] - 0.0005 else ""
        ey = eyes(step)
        add(S("ผลจริง%s: `w1` → `%s` · %s" % (step, ws, "ACCEPT" if g["accept"] else "REJECT"), tiles([
            ("Training Set", sc(ws, "train"), d("train") + " · `policy` %s" % RES[ws]["train"]["checks"]["policy"], tone("train")),
            ("Validation Set", sc(ws, "val"), d("val"), tone("val")),
            ("Test Set", sc(ws, "test"), d("test"), tone("test")),
            ("คะแนนรวมของ `%s`" % ws, sc(ws), d("all") + " · เกณฑ์ %s จุด" % g["sum"][3], tone("all")),
            ("gate ของบท 05", "ACCEPT" if g["accept"] else "REJECT", "รับ `%s` แทน `w1`" % ws if g["accept"] else "ใช้ `w1` ต่อ", "ok" if g["accept"] else "bad")]) +
            (note(ey[0]) if ws == "w1p" else note(para(step, "**ผลจริง:**")["lines"][0].replace("**ผลจริง:** ", ""), "info")),
            tag="runs/%s/gate-w1.txt" % ws, cls="mid"))
        if ws == "w1p":
            add(code("นโยบายถูกทุกข้อ แต่ข้อสุดท้ายเขียนเป็นกติกาทั่วไป", codes(step, "diff")[0]["text"], "diff",
                     post='<p>ผลใน Test Set · งานคืนเงินคอร์ส <code>x2-refund</code> ของ <code>w1p</code></p>' +
                          E.pre_html(codes(step, "text")[1]["text"], "text", "term"), maxfs=1.2))
        else:
            add(code("`w1q`: นโยบายชุดเดิม แต่บอกว่าใช้กับฟังก์ชันใด", codes(step, "diff")[0]["text"], "diff",
                     post=note(para(step, "รุ่นที่ถูกปฏิเสธ")["lines"][0], "info"), maxfs=1.2))
    gq = table("ขั้น 5.2", "gate")["rows"]
    add(S("ความรู้ชุดเดียวกัน เขียนต่างกันแค่ขอบเขต ผลตัดสินกลับด้าน", versus(
        "",
        ("w1p · นโยบายเขียนกว้าง", "เงินที่ร้านจ่ายออก ให้ปัดลง", "REJECT", E.plain(gq[0][1]).replace("REJECT · ", "")),
        ("w1q · นโยบายมีขอบเขต", "ใช้กับฟังก์ชันคิดเงินคืนสมาชิกเท่านั้น", "ACCEPT", E.plain(gq[0][2]).replace("ACCEPT · ", ""))) +
        note(eyes("ขั้น 5.2")[0]), tag="gate w1 → รุ่นใหม่", cls="mid"))
    add(fig("หลังเติมนโยบาย: `w1p` และ `w1q` ผ่าน `policy` ครบ เท่ากับ `v3` ของบท 05", "img/r05-coverage.png",
            "`w1` ไม่ผ่าน `policy` · `w1p` และ `w1q` ผ่านครบ · ต่างกันที่ `w1p` ทำงานอื่นพัง"))
    add(S("`w1q` ได้ %s เท่ากับ `v3` แต่ยังแทน `v3` ไม่ได้" % sc("w1q"),
          '<p>ข้อความที่คำสั่ง <code>gate</code> พิมพ์จริง (<a href="runs/w1q/gate-so-v3.txt" target="_blank"><code>runs/w1q/gate-so-v3.txt</code></a>)</p>' +
          term("runs/w1q/gate-so-v3.txt") + note(eyes("ขั้น 5.2")[1]), tag="gate so-v3 → w1q", maxfs=1.2))

    # ----- 4 · สรุป
    CTX.update(kicker="ภาค LAB · 4 · สรุปและแบบฝึกหัด", group="ภาค LAB · 4 · สรุปและแบบฝึกหัด")
    add(E.divider("4", "สรุปและแบบฝึกหัด", "<p>เทียบกับ Skill Optimizer · บทเรียนจากผลจริง · โจทย์ให้ลองต่อ</p>", "img/s04-summary.jpg", small="ภาค LAB"))
    add(fig("คะแนนของสกิลทุกชุดบนโจทย์ 9 ข้อ", "img/r03-all.png", "ไม่มีสกิล · `w1` · `w2` · `n1` · `w1p` · `w1q` · `so-v3` ของบท 05 · ชุดละ 27 Trial"))
    add(tbl("ผลของทุกชุด", table("4.1", "ชุดสกิล"), post=note(para("4.1", "รวม")["lines"][0], "info")))
    add(fig("ต้นทุนของการปรับสกิล: Skill Optimizer เทียบกับ WikiSkill", "img/r04-effort.png",
            "Trial ระหว่างปรับ และสิ่งที่คนต้องทำ ของทั้งสองวิธี บนโจทย์เดียวกัน"))
    add(tbl("เทียบกับ Skill Optimizer ของบท 05", table("4.2", "ประเด็น")))
    add(S("คำตอบของคำถาม 5 ข้อ จากผลจริง", cards([((r[0], r[1]), r[2]) for r in table("4.3", "#")["rows"]], 3), tag="ผล LAB 1–5", maxfs=1.2))
    add(nfig("n10-lessons"))
    lt4 = table("4.4", "ผล")["rows"]
    add(S("อีก 2 บทเรียน: เรื่อง Wiki และเรื่องต้นทุน", cards([(lt4[k][0], lt4[k][1], "warn") for k in (4, 6)], 2), cls="mid"))
    add(S("เลือกใช้เมื่อไร", cards([((k + 1, r[0]), r[1]) for k, r in enumerate(table("4.5", "สถานการณ์")["rows"])], 2), cls="mid"))
    add(nfig("n11-exercises"))
    add(nfig("n12-limits"))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบบท", "ถัดไป: EvoSkill v2",
                  '<p>ให้ Agent 3 ตัวปรับสกิลกันเอง → <a href="../07_EvoSkill_v2/README.md" target="_blank">../07_EvoSkill_v2/README.md</a></p>'
                  '<p>รายละเอียดเต็มของบทนี้: <a href="README.md" target="_blank">README.md</a> · รูปแบบของเครื่องมือ: '
                  '<a href="wikiskill_format.md" target="_blank">wikiskill_format.md</a> · ทฤษฎีต้นทาง (WikiSkill): '
                  '<a href="01_theory/README.md" target="_blank">01_theory/README.md</a> · '
                  '<a href="01_theory/WikiSkill_Theory_Slides.html" target="_blank">สไลด์ของทฤษฎี</a></p>', "img/s04-summary.jpg"))
    return E.SL


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
