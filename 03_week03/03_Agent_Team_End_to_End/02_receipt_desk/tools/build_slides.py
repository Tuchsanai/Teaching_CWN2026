#!/usr/bin/env python3
"""สร้างสไลด์ ReceiptDesk_Slides.html ของหัวข้อที่ 2 · ReceiptDesk

  python tools/build_slides.py            (รันจากโฟลเดอร์ 02_receipt_desk)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพ กราฟ หรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- พรอมต์ทั้ง 19 ขั้น: code fence ชนิด text ของ README.md (ตรงตัวอักษร) ผ่าน E.prompt_code()
- ตัวเลขผล: ตาราง และย่อหน้า "ผลจริง" ของ README.md (อ่านตอนสร้าง)
- "อ่านผลอย่างไร": รายการของ README.md ของขั้นนั้น (รวมรายการย่อย)
- ภาพอธิบายใหม่และขั้นตอนข้างภาพ: tools/slides_figures.py · เครื่องมือเรนเดอร์: tools/slides_engine.py
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, codes, para, CTX, add, note, fig, explain, tiles, cards,
                           versus, bars, tbl, code)
from slides_figures import FIGS

S = E.slide
SECS = E.load("README.md")
FIG = {f["img"]: f for f in FIGS}
OUT, TITLE = "ReceiptDesk_Slides.html", "ReceiptDesk · Slides"
README_LINES = E.read("README.md").split("\n")


# ------------------------------------------------------------------ ตัวช่วยอ่าน README
def nfig(key, post=""):
    f = FIG[key]
    return explain(f["title"], "img/%s.jpg" % key, f["steps"], post)


def step(n):
    return "ขั้นที่ %d ·" % n


def head(n):
    """ชื่อขั้นจากหัวข้อของ README (ตัด "ขั้นที่ N · " ออก)"""
    for s in SECS:
        if s["text"].startswith(step(n)):
            return s["text"].split("·", 1)[1].strip()
    raise KeyError(n)


def result(n):
    """ย่อหน้า **ผลจริง** ของขั้น n (ไม่รวมคำว่า ผลจริง)"""
    p = para(step(n), "**ผลจริง**")
    return " ".join(p["lines"]).replace("**ผลจริง**", "").strip()


def minutes(n):
    m = re.search(r"ประมาณ ([\d.]+) นาที", result(n))
    return m.group(1) if m else ""


def reads(n_or_prefix):
    """รายการใต้ **อ่านผลอย่างไร** ของหัวข้อ · คืน [(ข้อความ, [รายการย่อย])] อ่านจากบรรทัดดิบเพื่อเก็บระดับย่อย"""
    prefix = step(n_or_prefix) if isinstance(n_or_prefix, int) else n_or_prefix
    i = next(k for k, l in enumerate(README_LINES) if l.startswith("#") and l.lstrip("#").strip().startswith(prefix))
    while not README_LINES[i].startswith("**อ่านผลอย่างไร"):
        i += 1
    i += 1
    out = []
    while i < len(README_LINES) and (README_LINES[i].startswith("- ") or README_LINES[i].startswith("  - ")):
        l = README_LINES[i]
        if l.startswith("  - "):
            out[-1][1].append(l[4:].strip())
        else:
            out.append((l[2:].strip(), []))
        i += 1
    return out


def item_html(text, subs):
    h = "<p>%s</p>" % md(text)
    if subs:
        h += "<ul>%s</ul>" % "".join("<li>%s</li>" % md(x) for x in subs)
    return h


def read_slides(n, title, per=4, cols=2):
    """สไลด์ "อ่านผลอย่างไร" เป็นการ์ด (เกิน per ข้อ แบ่ง 2 หน้า)"""
    items = reads(n)
    chunks = [items[k:k + per] for k in range(0, len(items), per)]
    if len(chunks) > 1 and len(chunks[-1]) == 1 and per > 3:
        chunks = [items[:len(items) - 2], items[len(items) - 2:]] if len(items) > 4 else [items]
    out = []
    for c, ch in enumerate(chunks):
        t = title + (" (ต่อ)" if c else "")
        out.append(S(t, cards([((k + 1 + sum(len(x) for x in chunks[:c]), ""),
                                 item_html(a, b), "") for k, (a, b) in enumerate(ch)], cols), tag="อ่านผลอย่างไร · README", cls="mid"))
    return out


def step_divider(n, what, img=""):
    sub = "<p>%s</p><p><b>ผลจริง:</b> %s</p>" % (md(what), md(result(n)))
    return E.divider("ขั้นที่ %d" % n, head(n), sub, img)


def prompt_slides(n):
    return E.prompt_slides(E.prompt_code(step(n)), CTX["kicker"], "ขั้นที่ %d · %s" % (n, head(n)))


NOTE_AI = "ผลของคุณอาจต่างจากของผู้สอนได้ เพราะเอกสาร โค้ด และตัวเลขเกิดจาก AI ในแต่ละรอบ สิ่งที่ต้องตรงคือ **รูปแบบของผล** และ **เกณฑ์ที่ใช้ตัดสิน**"
NOTE_GPU = "ตัวเลขเวลาและค่าเช่าขึ้นกับเครื่องที่เช่าได้และผลของ AI ในรอบนั้น ของคุณจึงต่างจากของผู้สอนได้ · สิ่งที่ต้องตรงคือ **การเทียบกับเกณฑ์ใน Requirement**"


def check(n, items, note_text=NOTE_AI):
    return E.check_slide("s%d" % n, items, "ผลของผู้สอน: " + result(n), note_text, "ขั้นที่ %d · %s" % (n, head(n)))


def cnum(rows, col):
    return {E.plain(r[0]): E.plain(r[col]) for r in rows}


# ------------------------------------------------------------------ รายการตรวจผลของแต่ละขั้น (เรียบเรียงจากพรอมต์และผลจริงใน README)
CHECKS = {
    1: ["มีไฟล์ `docs/USER-STORIES.md` ทุกข้อเขียนแบบ \"ในฐานะ… ฉันต้องการ… เพื่อ…\" มีรหัส US-xx ระดับ Must / Should / Could และเกณฑ์ยอมรับ",
        "ทุก User Story อ้างคำพูดในบันทึกการสัมภาษณ์ที่เป็นที่มา",
        "ครบทุกบทบาทที่ลูกค้าพูดถึง: พนักงานบัญชี · หัวหน้าทีม · เจ้าของสำนักงาน · ลูกค้าของสำนักงาน",
        "ท้ายไฟล์มี 2 ตาราง: จุดที่ลูกค้าพูดขัดกันเอง และคำถามที่ต้องถามลูกค้าเพิ่ม · มีหัวข้อ \"นอกขอบเขต\""],
    2: ["มีไฟล์ `docs/REQUIREMENTS.md` ทุก FR อ้างรหัส User Story",
        "ทุก BR เป็นตัวเลขที่ตรวจได้ พร้อมค่าตัวอย่าง ต่ำกว่า / เท่ากับ / สูงกว่า เส้นแบ่ง",
        "มี NFR อย่างน้อย 6 เรื่อง รวมเกณฑ์ของโมเดลที่วัดได้บน Test Set และ SLO ของงานปกติกับงานด่วน",
        "มีกติกาของงานด่วน: ใครตั้งได้ แซงคิวอย่างไร งานปกติค้างได้ไม่เกินเท่าใด",
        "จุดที่ลูกค้าขัดกันถูกบันทึกเป็น \"ข้อสมมติ\" พร้อมเหตุผล"],
    3: ["มีไฟล์ `docs/DESIGN.md` ที่มีแผนภาพ Mermaid 4 ภาพ: Architecture · ER Diagram · ลำดับการทำงาน · สถานะของงาน",
        "มี API Contract ระหว่างเว็บกับ gateway รวมคำตอบเมื่อคิวเต็มและการใช้ API key",
        "มีการออกแบบคิว 3 เรื่อง: Priority Queue · Backpressure · Dead-letter Queue และงานไม่หายเมื่อ Worker ล่ม",
        "มีโหมด `BUG_MODE=1` และรายชื่อบั๊กอยู่ใน `docs/BUGS-SECRET.md` ที่เดียว",
        "มีไฟล์ `docs/TEST-DATA.md` ที่มีกรณีขอบของทุก Business Rule พร้อมผลที่คาดหวัง"],
    4: ["มีโฟลเดอร์ `plan/` ที่มีไฟล์บล็อก ภาพ DAG ภาพ Gantt และไฟล์แผน",
        "จำนวนบล็อก 12–14 และใช้ครบ 6 สกิล: review · debate · best_of · yolo · cyolo · image",
        "บล็อกกติกา Business Rule ใช้ `review` ที่ผู้ทำกับผู้ตรวจเป็นคนละ CLI",
        "แผนใช้เฉพาะบัญชี yolo1, yolo2, yolo3, cyolo1 และ agent พร้อมกันไม่เกิน 4",
        "สรุปบอก Critical Path และเวลารวมของแผน"],
    5: ["มีภาพ Gantt ของ 2 แผนใหม่ใน `plan/whatif`",
        "ตารางเทียบ 3 แผน: เวลารวม · Critical Path · บัญชีที่งานหนักที่สุด · บล็อกที่วางไม่ได้",
        "ไฟล์บล็อกเดิมไม่ถูกแก้",
        "มีคำแนะนำว่าควรรันแผนใด พร้อมเหตุผล 2–3 บรรทัด"],
    6: ["มีโฟลเดอร์ `app/` ที่มีไฟล์ที่ทีมสร้าง",
        "มีรายงานแผนเทียบของจริง ภาพ Gantt ของจริง และภาพเทียบแผนใน `plan/`",
        "ตารางสรุปมีนาทีตามแผน นาทีจริง โทเคน และสถานะของทุกบล็อก",
        "บล็อกที่ล้มหรือถูกบล็อกถูกรายงานตามจริง ไม่มีโค้ดที่เขียนแทนทีม"],
    7: ["รันต่อ run เดิม ไม่มี run ใหม่ และบล็อกที่เสร็จแล้วไม่ถูกรันซ้ำ",
        "บล็อกที่ไม่ผ่านการตรวจถูกแก้ตามข้อที่ผู้ตรวจขอในรอบล่าสุด",
        "มีรายงานแผนเทียบของจริงฉบับใหม่ใน `plan/`",
        "สรุปบอกโทเคนรวมของทั้งสองรอบ"],
    8: ["ขอบเขตการตรวจของบล็อกกติกา Business Rule ถูกเขียนใหม่ตามข้อ 1 ของพรอมต์",
        "มีไฟล์ `plan/FOLLOW-UPS.md` ที่จดข้อนอกขอบเขตพร้อมระดับความรุนแรง",
        "เกณฑ์ของบล็อกอื่นไม่ถูกแก้",
        "รายงานแผนเทียบของจริงใหม่แสดงสถานะของทุกบล็อก"],
    9: ["เช่าเครื่อง RTX 3090 2 ใบในเครื่องเดียว ราคารวมไม่เกิน $0.60 ต่อชั่วโมง ติดป้าย `e2e-receipt`",
        "นับจำนวนใบเสร็จของ Training / Validation / Test Set ได้",
        "มีไฟล์ `results/dataset_samples.jpg` ที่มีใบเสร็จ 6 ใบคู่กับ JSON เฉลย",
        "สรุปบอกช่องที่ Requirement ใช้ตัดสิน และว่าเครื่องยังเปิดอยู่"],
    10: ["เทรน 2 รอบด้วยค่าเดิมทุกอย่าง: GPU 1 ใบ และ GPU 2 ใบ",
         "มีตาราง (ก) เวลาต่อ Epoch · Speedup · Efficiency · เงินต่อ Epoch",
         "มีตาราง (ข) ตัวชี้วัดก่อนเทรน หลังเทรน เกณฑ์ และผลตัดสิน Acceptance Gate",
         "ตัดสินตามเกณฑ์ใน Requirement ทั้ง Acceptance Gate และความคุ้มของการเพิ่ม GPU",
         "มีผลวัด กราฟ และตัวอย่างคำตอบใน `results/model`"],
    11: ["vLLM 2 ตัวอยู่หลัง NGINX `least_conn` และ gateway ไม่รับคำขอที่ไม่มี API key",
         "เว็บเปิดที่พอร์ต 3420 และเรียก gateway บนเครื่อง GPU ได้",
         "ใบเสร็จ 5 ใบถึงสถานะรอตรวจ และยอดรวมในฐานข้อมูลตรงกับที่ gateway ตอบ",
         "สิ่งที่แก้ถูกจดไว้ใน `results/deploy`"],
    12: ["มีโค้ดยิงโหลดใน `loadtest/` และผลเป็นไฟล์ตัวเลขกับกราฟ 2 รูปใน `results/capacity`",
         "เวลาของ 100 ใบ เมื่อมี Worker 1 ตัว และ 2 ตัว เทียบกับ SLO ของงานปกติ",
         "งานด่วนมีผลครบภายใน SLO และลำดับการอ่านมีด่วนติดกันไม่เกิน 4 ใบ",
         "คิวเต็มถูกปฏิเสธด้วยคำตอบที่ออกแบบไว้ และงานที่รับไว้ไม่หาย",
         "Worker ล่มกลางงานแล้วงานครบทุกใบ · ไฟล์เสียเข้า Dead-letter Queue หลังลองครบ 3 ครั้ง"],
    13: ["มีไฟล์ `test/CHARTERS.md` 6 ข้อ รูปแบบ \"สำรวจ… ด้วย… เพื่อหา…\" และทุก Business Rule มี Charter รับผิดชอบ",
         "subagent 6 ตัวทำงานพร้อมกัน ตัวละ 1 Charter และ 1 session",
         "บันทึกใน `test/exploration` เขียนผลที่คาดหวังก่อนลอง แล้วจึงบันทึกผลจริง ✅ ⚠️ ❌ พร้อมภาพหน้าจอ",
         "มีไฟล์ `test/EXPLORATION.md` ที่มีตารางความเสี่ยง P1 / P2 / P3"],
    14: ["มีไฟล์ `test/TEST-PLAN.md` โครง 8 หัวข้อ และ Test Case 45–60 ข้อ ในกลุ่ม 5.1–5.8",
         "ทุก Test Case มีขั้นตอน ผลที่คาดหวังที่คำนวณให้ดู ที่มา (FR/BR) และระดับ P1–P3",
         "Test Case ที่ต้องกำหนดผลอ่านให้แน่นอน ระบุว่ารันกับตัวอ่านจำลอง",
         "มีไฟล์ `test/PLAN-REVIEW.md` จากผู้ตรวจที่ไม่ใช่ผู้เขียน และข้อรุนแรงสูงถูกแก้"],
    15: ["มีไฟล์ทดสอบใน `test/e2e` 1 ไฟล์ต่อกลุ่ม",
         "Test Case ที่ใช้ตัวอ่านจำลองรันกับเว็บพอร์ต 3421 ข้อที่เหลือรันกับพอร์ต 3420",
         "ข้อที่ล้มถูกคัดแยกเป็น เว็บผิด · แผนผิด · เทสต์ผิด และผลที่คาดหวังไม่ถูกแก้ให้ตรงกับเว็บ",
         "มี `test/TEST-REPORT.md` 6 ส่วน และหน้า `test/index.html` ที่เปิดดูหลักฐานได้",
         "มีผลตัดสินตาม Exit Criteria"],
    16: ["มีไฟล์ `test/BUG-HUNT.md` ที่มีบั๊กทีละตัว พร้อมขั้นตอนทำซ้ำ ผลที่คาดหวัง ผลจริง และหลักฐาน",
         "เปิด `BUGS-SECRET` หลังเขียนรายงานบั๊กเสร็จ แล้วนับว่าจับได้กี่ตัวจาก 3 ตัว",
         "มีไฟล์ `DELIVERY.md` ที่มีตาราง User Story → Requirement → Test Case → ผล ผล Acceptance Gate และผล Capacity Test",
         "เว็บกลับเป็นโหมดปกติ (ปิด `BUG_MODE`)"],
    17: ["LoRA และผลวัดถูกคัดลอกกลับมาที่ `results/model` ก่อนลบเครื่อง",
         "ไม่มีเครื่องป้าย `e2e-receipt` เหลืออยู่ (ตรวจซ้ำแล้ว)",
         "เว็บและฐานข้อมูลบนเครื่องนี้หยุดทั้ง 2 ชุด",
         "ตารางสรุป: เวลาที่เปิดเครื่อง · ค่าเช่ารวม · โทเคนรวมของทีม",
         "เปิดหน้า Instances ของ Vast.ai ดูด้วยตาอีกครั้งว่าว่าง"],
    18: ["มีไฟล์ `skill_v1/SKILL.md` และสกิลถูกติดตั้งที่ `.claude/skills/agent-team-delivery`",
         "สกิลมี 4 ระยะ: Requirement → Planning → Build · Train · Deploy → Verification",
         "มีสิ่งที่เพิ่มในเวอร์ชัน 1 ครบ 5 เรื่อง และค่าที่ปรับได้พร้อมค่าเริ่มต้น",
         "มีเกณฑ์ตรวจผ่านของแต่ละระยะ จุดที่ถามคน และกติกาเรื่องเงิน",
         "เปิด Claude Code ใหม่ 1 ครั้ง แล้วสกิลถูกมองเห็น"],
    19: ["ผลอยู่ใน `results/skill_v1_run` และชื่อแผนคือ `receiptdesk-skill`",
         "สกิลทำถึงระยะ Planning แล้วหยุดรอคนอนุมัติ ไม่รันทีมจริงและไม่เช่าเครื่อง",
         "มีตารางเทียบกับรอบที่ทำทีละขั้น: User Story · FR · BR · จำนวนบล็อก · Critical Path · เวลารวมของแผน"],
}
GPU_STEPS = {9, 10, 11, 12, 17}

WHAT = {  # ประโยคสั้นบนหน้าคั่น: ขั้นนี้ทำอะไร (เรียบเรียงจากพรอมต์ของขั้นนั้น)
    1: "แปลงบันทึกการสัมภาษณ์เป็น User Story ที่อ้างคำพูดของลูกค้าได้ทุกข้อ",
    2: "แปลง User Story เป็น FR · BR · NFR ที่เป็นตัวเลขตรวจได้ รวมเกณฑ์ของโมเดลและ SLO",
    3: "ออกแบบระบบ 2 ฝั่ง คิว 3 เรื่อง และข้อมูลทดสอบของทุก Business Rule",
    4: "แตกงานเป็นบล็อกด้วยสกิล dag-planner แล้ววาด DAG และ Gantt",
    5: "วางแผนอีก 2 แบบจากบล็อกเดิม เพื่อรู้ข้อจำกัดของทีมก่อนเสียเงิน",
    6: "ทีม agent 4 บัญชีรันแผนจริง แล้วรายงานแผนเทียบของจริง",
    7: "รันต่อ run เดิมเฉพาะบล็อกที่ยังไม่เสร็จ",
    8: "คนกำหนดขอบเขตการตรวจใหม่ แล้วรันต่อจนครบทุกบล็อก",
    9: "เช่าเครื่อง RTX 3090 2 ใบ ดาวน์โหลดโมเดลกับ Dataset และอธิบาย label",
    10: "เทรนด้วย LoRA บน GPU 1 ใบเทียบ 2 ใบ แล้วตัดสินด้วย Acceptance Gate",
    11: "เปิดฝั่ง AI บนเครื่อง GPU และเว็บบนเครื่องนี้ แล้วส่งใบเสร็จทั้งเส้นทาง",
    12: "วัดความจุเทียบ SLO และทดสอบงานด่วน คิวเต็ม Worker ล่ม และไฟล์เสีย",
    13: "เขียน Test Charter 6 ข้อ แล้วให้ผู้ทดสอบ 6 ตัวสำรวจเว็บพร้อมกัน",
    14: "เขียน Test Plan จาก Requirement แล้วให้ผู้ตรวจคนละบัญชีตรวจไขว้",
    15: "เขียนและรัน Playwright Test กับเว็บ 2 ชุด แล้วตัดสินตาม Exit Criteria",
    16: "รันชุดเดิมกับ BUG_MODE=1 เพื่อดูว่าจับบั๊กที่ซ่อนไว้ได้ครบไหม แล้วเขียนรายงานส่งมอบ",
    17: "เก็บผลกลับ ลบเครื่อง และสรุปค่าใช้จ่ายทั้งงาน",
    18: "เก็บสิ่งที่งานรอบนี้สอนเข้าสกิล agent-team-delivery เวอร์ชัน 1",
    19: "ใช้สกิลด้วยคำสั่งเดียวกับบันทึกสัมภาษณ์เดิม แล้วเทียบกับรอบที่ทำทีละขั้น",
}


# ------------------------------------------------------------------ ชิ้นส่วนเฉพาะของเด็คนี้ (รอบที่ 2: นำด้วยภาพ)
CSS2 = """
.ex.w65 .fig{flex:1.95 1 0}
.ex.w55 .fig{flex:1.2 1 0}
.ex .side .stp ul{margin:.25em 0 0 1.1em;padding:0}
.ex .side .stp li{margin:.1em 0}
.tiles.mini{gap:14px;flex:none}
.tiles.mini .tile{padding:.35em .7em .45em;border-top-width:5px}
.tiles.mini .tile .num{font-size:1.55em}
.tiles.mini .tile .k{font-size:.7em}
.tiles.mini .tile .s{font-size:.7em}
.stk{flex:none;display:grid;grid-template-columns:repeat(var(--cols,2),1fr);gap:.55em}
.body>.fig.wide.crop img{max-height:48vh;object-fit:contain}
.trio,.pair{flex:1 1 0;min-height:0;display:flex;gap:24px}
.trio figure,.pair figure{flex:1;min-width:0;margin:0;display:flex;flex-direction:column;gap:.5em}
.trio .fig{flex:1 1 0;min-height:0}
.trio .fig img{width:100%;height:100%;object-fit:cover}
.trio figcaption,.pair figcaption{line-height:1.45}
.trio figcaption b,.pair figcaption b{color:var(--navy);display:block;font-size:1.08em;margin-bottom:.15em}
.pair .fig{flex:1 1 0;min-height:0}
.pair figcaption{text-align:center}
.pair.rows{flex-direction:column;gap:14px}
.pair.rows figure{flex:none;flex-direction:row;align-items:center;gap:18px}
.pair.rows .fig{flex:none;width:74%}
.pair.rows .fig img{width:100%;height:auto}
.pair.rows figcaption{flex:1;text-align:left}
.p3{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:12px}
.p3 .row{flex:1 1 0;min-height:0;display:flex;gap:18px;align-items:stretch}
.p3 .row .cardx{flex:0 0 31%;margin:0}
.p3 .row .fig{flex:1 1 0;min-height:0;justify-content:flex-start}
.ppl{flex:1 1 0;min-height:0;display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.ppl .pp{background:#fff;border:1px solid var(--line);border-radius:14px;padding:.7em .8em;display:flex;flex-direction:column;gap:.35em;box-shadow:0 3px 10px rgba(18,48,94,.06)}
.ppl .pp img{width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:10px}
.ppl .pp h4{margin:.2em 0 0;color:var(--navy)}
.ppl .pp h4 small{display:block;color:var(--muted);font-weight:500}
.ppl .pp ul{margin:0;padding-left:1.1em;line-height:1.45;font-size:.92em}
.divider.band .inner h1{font-size:50px;line-height:1.35;max-width:1050px}
.divider .inner .small{margin-bottom:40px}
"""
E.CSS += CSS2


def _img(src, alt):
    return E.img_tag({"t": "img", "src": src, "alt": E.plain(alt)})


def pts(points, start=1):
    """รายการเรียงเลข · ข้อหนึ่งเป็นข้อความ หรือ (ข้อความ, [รายการย่อย])"""
    out = []
    for k, x in enumerate(points):
        t, subs = x if isinstance(x, tuple) else (x, [])
        h = md(t) + ("<ul>%s</ul>" % "".join("<li>%s</li>" % md(s) for s in subs) if subs else "")
        out.append('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + start, h))
    return "".join(out)


def pic(title, src, points, post="", w="", top="", tag=""):
    """ภาพใหญ่ด้านซ้าย + ประเด็นเรียงเลขด้านขวา · top = แถบตัวเลขผลจริงเหนือภาพ"""
    body = top + '<div class="ex %s"><div class="fig">%s</div><div class="side fitbox">%s%s</div></div>' % (
        w, _img(src, title), pts(points), post)
    return S(title, body, tag=tag, maxfs=1.25)


def stack(title, src, points, cap="", cols=2, tag=""):
    """ภาพจริง (ตัดเฉพาะส่วน) เต็มความกว้าง + ประเด็นด้านล่าง"""
    body = ('<div class="fig wide crop">%s</div>' % _img(src, title) + ('<p class="cap">%s</p>' % md(cap) if cap else "")
            + '<div class="stk fitbox" style="--cols:%d">%s</div>' % (cols, pts(points)))
    return S(title, body, tag=tag, maxfs=1.2)


def pair(title, a, b, post="", tag="", rows=False):
    """ภาพ 2 ภาพเทียบกัน · a, b = (src, หัว, คำบรรยาย)"""
    figs = "".join('<figure><div class="fig">%s</div><figcaption><b>%s</b>%s</figcaption></figure>' % (_img(s, h), md(h), md(c))
                   for s, h, c in (a, b))
    return S(title, '<div class="pair%s">%s</div>%s' % (" rows" if rows else "", figs, post), tag=tag, maxfs=1.15)


def trio(title, items):
    figs = "".join('<figure><div class="fig">%s</div><figcaption><b>%s</b>%s</figcaption></figure>' % (_img(s, h), md(h), md(c))
                   for s, h, c in items)
    return S(title, '<div class="trio">%s</div>' % figs, maxfs=1.15)


def band(title, sub_html, img, small=""):
    """ข้อความเดียวตัวใหญ่บนภาพถ่ายเต็มหน้า"""
    d = E.divider("", title, sub_html, img, small)
    d["cls"] += " band"
    return d


def step_divider(n, what, img=""):
    r = result(n)
    r = ("<p><b>ผลจริง:</b> %s</p>" % md(r)) if ":" in r else "<p><b>เวลาที่ใช้จริง:</b> %s</p>" % md(r.strip("() "))
    return E.divider("ขั้นที่ %d" % n, head(n), "<p>%s</p>%s" % (md(what), r), img,
                     small="ขั้นที่ %d จาก 19 · %s" % (n, phase_of(n)))


def phase_of(n):
    return ("ระยะ A · Requirement" if n <= 3 else "ระยะ B · Planning" if n <= 5 else "ระยะ C · Build · Train · Deploy" if n <= 12
            else "ระยะ D · Verification" if n <= 17 else "ปิดท้าย · สกิลเวอร์ชัน 1")


REF = {}


def check(n, items, note_text=NOTE_AI):
    return E.check_slide("s%d" % n, items, "ผลของผู้สอน: " + REF.get(n, result(n)), note_text, "ขั้นที่ %d · %s" % (n, head(n)))


def lab_head(n, what_img=None):
    """หน้าคั่น → (ภาพของขั้น) → พรอมต์ → ตรวจผล"""
    add(step_divider(n, WHAT[n]))
    if what_img:
        add(what_img)
    add(prompt_slides(n))
    add(check(n, CHECKS[n], NOTE_GPU if n in GPU_STEPS else NOTE_AI))


def rcards(n, title, items, cols=3, tag="อ่านผลอย่างไร · README"):
    """ประเด็นอ่านผลที่ไม่มีภาพประกอบ (การ์ด 1 หน้า)"""
    return S(title, cards([((k + 1, ""), item_html(a, b), "") for k, (a, b) in enumerate(items)], cols), tag=tag, cls="mid")


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    title = SECS[0]["text"].split("·", 1)[1].strip()
    deliv = reads(16)[-1][0]
    t1 = table(step(1), "รายการ")
    c1 = cnum(t1["rows"], 1)
    n_us = sum(int(v) for k, v in c1.items() if k.startswith("User Story"))
    t17 = table(step(17), "รายการ")
    c17 = cnum(t17["rows"], 1)
    REF[1] = "%s: User Story %d ข้อ (Must %s · Should %s · Could %s) · จุดขัดกัน %s จุด · คำถาม %s ข้อ" % (
        result(1).strip(), n_us, c1["User Story ระดับ Must"], c1["User Story ระดับ Should"], c1["User Story ระดับ Could"],
        c1["จุดที่ลูกค้าพูดขัดกันเอง"], c1["คำถามที่ต้องถามลูกค้าเพิ่ม"])
    REF[17] = "%s: ค่าเช่ารวม %s · เครื่องป้าย e2e-receipt %s" % (result(17).strip(), E.plain(c17["ค่าเช่ารวม"]),
                                                                 E.plain(c17["เครื่องป้าย e2e-receipt"]))

    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    add(E.cover(title, "จากบันทึกสัมภาษณ์ลูกค้า ถึงระบบที่ทดสอบแล้วและรายงานส่งมอบ ด้วยทีม AI และ GPU ที่เช่า",
                "image/cover.jpg", small="03_week03 · Agent Team End-to-End · หัวข้อที่ 2"))
    CTX["kicker"] = "ภาพรวมของบท"
    add(pic("ทั้งเรื่องในภาพเดียว: ระบบครบทุกส่วนและรับโหลดได้ แต่ยังส่งมอบไม่ได้", "img/n41-delivery.jpg", [
        "ทีม agent สร้างระบบครบ %s และเปิดบริการบนเครื่อง GPU ที่เช่าได้ (ขั้นที่ 6–11)" % "14 จาก 14 บล็อก",
        "Capacity Test และ Failure Test ผ่านทุกการทดสอบ (ขั้นที่ 12)",
        "รายงานส่งมอบ: **ยังไม่พร้อมใช้งานจริง** · " + deliv.split(":", 1)[1].strip() + " (ขั้นที่ 10, 15, 16)"]))
    add(pic("บทนี้เดินตาม 4 ระยะของงาน แล้วปิดท้ายด้วยการปรับสกิล", "img/n01-four-phases.jpg", FIG["n01-four-phases"]["steps"],
            post=note("รายละเอียดเต็มอยู่ใน [`README.md`](README.md) · พรอมต์ทั้ง 19 ขั้นอยู่ใน [`PROMPTS.md`](PROMPTS.md)", "info")))
    add(S("วิธีใช้สไลด์นี้", cards([
        ("ไปหน้าถัดไป / ก่อนหน้า", '<p><span class="kbd">→</span> <span class="kbd">Space</span> / <span class="kbd">←</span> หรือปุ่มมุมขวาล่าง</p>'),
        ("สารบัญทุกหน้า", '<p><span class="kbd">O</span> แล้วคลิกหน้าที่ต้องการ · <span class="kbd">F</span> เต็มจอ</p>'),
        ("ขยายภาพ", "คลิกที่ภาพ · คลิกอีกครั้งหรือกด Esc เพื่อปิด"),
        ("คัดลอกพรอมต์ของแต่ละขั้น", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** ให้ข้อความเดียวกับ `README.md` ตรงตัวอักษร", "warn"),
        ("ตรวจผลหลังรัน", "สไลด์ **ตรวจผลของคุณ** อยู่ต่อจากพรอมต์ทุกขั้น ติ๊กได้ และเบราว์เซอร์นี้จำค่าไว้", "warn"),
        ("เปิดไฟล์จริง", "ลิงก์สีน้ำเงินเปิดไฟล์ในโฟลเดอร์ของบท จึงควรเปิดสไลด์จากโฟลเดอร์ `02_receipt_desk`"),
    ]), cls="mid"))

    # ===== เรื่องราวของลูกค้า
    CTX.update(kicker="เรื่องราวของลูกค้า", group="เรื่องราวและการสัมภาษณ์")
    add(E.divider("เรื่องราว", "สำนักงานบัญชี ใส่ใจการบัญชี", "<p>%s</p>" % md(para("1 ·", "สำนักงานบัญชี")["lines"][0]),
                  "image/r1-send.jpg"))
    add(trio("ใบเสร็จเข้ามาเป็นรูปถ่าย พนักงานพิมพ์ทีละใบ และสิ้นเดือนยอดเริ่มผิด", [
        ("image/r1-send.jpg", "ลูกค้าถ่ายรูปใบเสร็จส่งมา", para("1 ·", "ร้านค้าส่งรูป")["lines"][0]),
        ("image/r2-typing.jpg", "พนักงานพิมพ์ยอดทีละใบ", para("1 ·", "พนักงาน 4 คน")["lines"][0]),
        ("image/r3-monthend.jpg", "สิ้นเดือนงานเข้าพร้อมกัน", para("1 ·", "บางวัน")["lines"][0])]))
    question = " ".join(para("1 ·", "**คำถามของหัวข้อนี้")["lines"]).strip("*").replace("คำถามของหัวข้อนี้: ", "")
    add(band(question, "", "image/r3-monthend.jpg", small="คำถามของหัวข้อนี้"))

    CTX["kicker"] = "การสัมภาษณ์ลูกค้า"
    add(fig("ทีมพัฒนาสัมภาษณ์ผู้เกี่ยวข้อง 4 คนก่อนเขียนเอกสารใด ๆ", "image/r4-interview.jpg",
            "บันทึกฉบับเต็ม: [`INTERVIEW.md`](INTERVIEW.md) · บริษัทและบุคคลเป็นตัวอย่างสมมติ (ภาพจำลอง)"))
    people = []
    for r in table("2 ·", "")["rows"]:
        src = re.search(r'src="([^"]+)"', r[0]).group(1)
        name, role = r[1].split("<br>")
        quotes = [q.strip() for q in r[2].split("<br>")]
        people.append('<div class="pp"><img src="%s" alt="%s"><h4>%s<small>%s</small></h4><ul>%s</ul></div>'
                      % (src, E.plain(name), md(name), md(role), "".join("<li>%s</li>" % md(q) for q in quotes)))
    add(S("ผู้ให้สัมภาษณ์ 4 คนต้องการคนละอย่าง", '<div class="ppl">%s</div>' % "".join(people), tag="ภาพบุคคลเป็นภาพจำลอง"))
    obs = para("2 ·", "**สังเกต:**")["lines"][0].replace("**สังเกต:**", "").split("·")
    add(pic("ความต้องการ 2 คู่ขัดกันเอง ทีมต้องเลือกทางและแจ้งลูกค้า", "img/n21-conflicts.jpg",
            [obs[0].strip(), obs[1].strip()],
            post=note("ทางที่ทีมเลือกอยู่ในขั้นที่ 2 (ข้อสมมติ) และขั้นที่ 3 (Priority Queue)", "info")))

    # ----- ภาพรวมของงานและความรู้พื้นฐาน
    CTX.update(kicker="ภาพรวมของงาน", group="ภาพรวมของงาน")
    add(fig("ทุกข้อของ Requirement อ้างย้อนกลับถึงคำพูดของลูกค้าได้", "image/trace.png",
            "ตัวอย่าง 3 เส้นทาง: คำพูด → User Story → Requirement → สิ่งที่ System Design ต้องมี"))
    dt = table("3 ·", "ลำดับ")
    add(pic("ระยะ A ได้เอกสาร 4 ชิ้นต่อกันเป็นสาย แต่ละชิ้นตอบคำถามคนละข้อ", "img/n22-doc-chain.jpg",
            ["%s ตอบว่า%s · ผลจริง **%s**" % (r[1], r[2], r[3]) for r in dt["rows"]], tag="README · ระยะ A"))
    ds = table(step(9), "ชุด")
    model = " ".join(para(step(9), "**รู้จักโมเดล**")["lines"]).replace("**รู้จักโมเดล** · ", "").split("·")
    dsn = " ".join(para(step(9), "**รู้จัก Dataset**")["lines"]).replace("**รู้จัก Dataset** · ", "")
    add(pic("โมเดลรับรูปใบเสร็จกับคำสั่ง แล้วตอบเป็น JSON", "img/n23-model-io.jpg", [
        "โมเดล: " + model[0].strip() + " · " + model[1].strip(),
        "Input: " + model[2].replace("Input:", "").strip() + " · Output: " + model[3].replace("Output:", "").strip(),
        "Dataset: " + dsn + " · " + " · ".join("%s %s ใบ" % (r[0], r[1]) for r in ds["rows"]),
        model[4].strip()]))

    # ===== ภาค LAB
    CTX.update(kicker="ภาค LAB", group="ภาค LAB · แผนที่")
    add(E.divider("ภาค LAB", "19 ขั้น จากบันทึกสัมภาษณ์ถึงสกิลเวอร์ชัน 1",
                  "<p>ทุกขั้นใช้ลำดับเดียวกัน: หน้าคั่น → ภาพของขั้น → พรอมต์ → ตรวจผล → ผลจริง → การอ่านผล</p>"))
    phases = [("A · Requirement", range(1, 4), ""), ("B · Planning", range(4, 6), ""), ("C · Build · Train · Deploy", range(6, 13), "warn"),
              ("D · Verification", range(13, 18), "warn"), ("สกิลเวอร์ชัน 1", range(18, 20), "ok")]
    add(S("แผนที่ของ LAB: 19 ขั้นใน 4 ระยะ และขั้นปิดท้าย", cards([
        (p, "<ul>%s</ul>" % "".join("<li><b>%d</b> %s</li>" % (n, md(head(n))) for n in rng), tone) for p, rng, tone in phases], 5), cls="mid"))
    add(pic("ก่อนเริ่ม: Claude Code, container ที่มี 4 บัญชี และ key ของ Vast.ai", "img/n25-setup.jpg", [
        "ทำ[หัวข้อที่ 1](../01_sitesafe_inspect/README.md)ก่อน เพราะใช้สกิลและวิธีทำงานแบบเดียวกัน",
        next(l for l in README_LINES if l.startswith("เมื่อทำเอง")),
        "เปิด Claude Code ที่โฟลเดอร์ `02_receipt_desk` วางทีละพรอมต์ และเปิดหน้าต่างใหม่ทุกขั้น",
        "container `multi-account` มีบัญชี yolo1, yolo2, yolo3, cyolo1 สำหรับทีม agent และสกิล dag-planner · agent-team · vastai",
        "key ของ Vast.ai อยู่ในไฟล์ `.env` ของโฟลเดอร์ ห้ามแสดงค่า key และห้ามข้ามขั้นที่ 17"],
        post=note("ค่าเช่ารวมทั้งงานในรอบของผู้สอน **%s**" % E.plain(c17["ค่าเช่ารวม"]), "info")))

    # ===== ระยะ A
    CTX.update(kicker="ระยะ A · Requirement", group="ระยะ A · Requirement")
    add(E.divider("ระยะ A", "จากคำพูดเป็น Requirement", "<p>ขั้นที่ 1–3 จาก 19 · ยังไม่เขียนโค้ด</p>", "image/r4-interview.jpg"))

    CTX.update(kicker="ระยะ A · ขั้นที่ 1", group="ขั้นที่ 1 · User Story")
    lab_head(1, pic("ขั้นที่ 1 เปลี่ยนคำพูดในบันทึกเป็น User Story ที่อ้างที่มาได้ทุกข้อ", "img/n26-quote-to-story.jpg", [
        "อ่านบันทึกใน `INTERVIEW.md`", "เขียน User Story แบบ \"ในฐานะ… ฉันต้องการ… เพื่อ…\" ทุกบทบาท พร้อมรหัส ระดับ และเกณฑ์ยอมรับ",
        "ทุกข้อ **อ้างคำพูด** ที่เป็นที่มา และไม่เพิ่มความต้องการที่ลูกค้าไม่ได้พูด",
        "รวบรวมจุดที่ลูกค้าพูดขัดกันเอง คำถามที่ต้องถามเพิ่ม และสิ่งที่อยู่ \"นอกขอบเขต\""]))
    add(pic("ผลจริง: User Story %d ข้อ · จุดขัดกัน %s จุด · คำถาม %s ข้อ" % (
        n_us, c1["จุดที่ลูกค้าพูดขัดกันเอง"], c1["คำถามที่ต้องถามลูกค้าเพิ่ม"]), "img/n27-unanswered.jpg", reads(1),
        top=tiles([(r[0].replace("User Story ระดับ ", "User Story · "), r[1], "", "warn" if "ขัด" in r[0] else "") for r in t1["rows"]]).replace(
            'class="tiles"', 'class="tiles mini"'), tag="ผลจริง · อ่านผล · README"))

    CTX.update(kicker="ระยะ A · ขั้นที่ 2", group="ขั้นที่ 2 · Requirement")
    lab_head(2, nfig("n02-model-metrics"))
    r2 = result(2)
    nums = dict((k, re.search(k + r" (\d+) ข้อ", r2).group(1)) for k in ("FR", "BR", "NFR", "ข้อสมมติ"))
    add(tbl("Business Rule ทุกข้อมีค่าตัวอย่างที่เส้นแบ่ง: ต่ำกว่า · เท่ากับ · สูงกว่า", table(step(2), "รหัส"),
            post=note("ตัวอย่าง 5 จาก 14 ข้อ · ค่าที่เส้นแบ่งคือจุดที่บั๊กมักซ่อนอยู่ (ขั้นที่ 16)")))
    slo = table(step(2), "เรื่อง")
    add(pic("SLO: ชุด 100 ใบเสร็จภายใน 30 นาที และงานด่วนเสร็จภายใน 5 นาที", "img/n28-slo-lanes.jpg",
            ["**%s**: %s" % (r[0], r[1]) for r in slo["rows"]], tag="SLO และกติกาของงานด่วน"))
    add(pic("ผลจริง: FR %s · BR %s · NFR %s และข้อสมมติ %s ข้อที่ลูกค้าต้องยืนยัน" % (nums["FR"], nums["BR"], nums["NFR"], nums["ข้อสมมติ"]),
            "img/n29-assumption.jpg", reads(2), top=tiles([
                ("Functional Requirement", nums["FR"], "ระบบต้องทำอะไรได้", ""), ("Business Rule", nums["BR"], "กติกาเป็นตัวเลข มีเส้นแบ่ง", ""),
                ("Non-functional Requirement", nums["NFR"], "ต้องดีแค่ไหน", ""), ("ข้อสมมติ", nums["ข้อสมมติ"], "ค่าที่ทีมตั้งเอง", "warn")]).replace(
                'class="tiles"', 'class="tiles mini"'), tag="ผลจริง · อ่านผล · README"))

    CTX.update(kicker="ระยะ A · ขั้นที่ 3", group="ขั้นที่ 3 · System Design")
    lab_head(3, pic("ระบบมี 2 ฝั่ง: เว็บบนเครื่องนี้ และฝั่ง AI บนเครื่อง GPU ที่เช่า", "img/n34-deploy-path.jpg", [
        "**เครื่องนี้** (docker compose): web Next.js · dispatcher · PostgreSQL · volume ของรูปใบเสร็จ",
        "dispatcher ส่งใบเสร็จไป **API gateway** ด้วย HTTPS + `X-API-Key` และถามสถานะ",
        "gateway แยกงานด่วนกับงานปกติเข้า **RabbitMQ** 2 คิว · ใบที่ล้มเหลวครบ 3 ครั้งไป `receipts.dlq`",
        "**GPU Worker** 2 ตัวขออ่านรูปผ่าน **NGINX** `least_conn` ไปยัง vLLM 2 ตัว (GPU ละ 1 ตัว)"],
        post='<p class="cap">แผนภาพเต็มของ README: <a href="image/gen-arch.png" target="_blank"><code>image/gen-arch.png</code></a></p>', w="w65"))
    add(fig("งาน 1 ใบมี 5 สถานะ: รออ่าน → กำลังอ่าน → รอตรวจ → ยืนยันแล้ว หรือ อ่านไม่ได้", "image/gen-state.png",
            "อ่านล้มเหลวครั้งที่ 1–2 หรือ Worker ล่ม → กลับไป **รออ่าน** · ล้มเหลวครบ 3 ครั้ง → **อ่านไม่ได้** (Dead-letter Queue)"))
    add(nfig("n03-queue-design"))
    r3 = result(3)
    v3 = [re.search(p, r3).group(1) for p in (r"ตาราง (\d+)", r"API (\d+)", r"ข้อมูลทดสอบ (\d+) แถว", r"ตอบไม่ได้ (\d+) ข้อ")]
    add(pic("ผลจริง: ตาราง %s · API %s · ข้อมูลทดสอบ %s แถว และใช้ 2 คิวแทนคิวเดียว" % tuple(v3[:3]), "img/n30-two-queues.jpg", reads(3),
            top=tiles([("ตารางในฐานข้อมูล", v3[0], "ER Diagram", ""), ("API", v3[1], "API Contract", ""),
                       ("ข้อมูลทดสอบ", v3[2], "แถว · กรณีขอบของทุก BR", ""), ("คำถามที่ยังตอบไม่ได้", v3[3], "ต้องวัดบนเครื่องจริง", "warn")]).replace(
                'class="tiles"', 'class="tiles mini"'), tag="ผลจริง · อ่านผล · README"))

    # ===== ระยะ B
    CTX.update(kicker="ระยะ B · Planning", group="ระยะ B · Planning")
    add(E.divider("ระยะ B", "วางแผนงานให้ทีม AI", "<p>ขั้นที่ 4–5 จาก 19 · วางแผนเท่านั้น ยังไม่รันจริง</p>", "img/p21-planning.jpg"))
    CTX.update(kicker="ระยะ B · ขั้นที่ 4", group="ขั้นที่ 4 · DAG และ Gantt")
    bt = table(step(4), "บล็อก")
    special = [r for r in bt["rows"] if "**" in r[1]]
    lab_head(4, pic("DAG 14 บล็อก: สายวิกฤตคือ B01 → B02 → B04 → B11 → B14", "plan/dag.png", [
        "%s · สกิล %s · ขนาด %s · รอ %s · %s" % (r[0], r[1], r[2], r[3], r[4]) for r in special],
        post=note("**ดูลูกศรสีส้ม:** สายวิกฤต B01 → B02 → B04 → B11 → B14 · แต่ละกล่องบอกสกิล ขนาด rank และบัญชี · ลูกศรชี้บล็อกที่ต้องรอ · สกิลใหม่ 2 ตัว (`debate` และ `best_of`) อยู่ตรงจุดที่ไม่มีคำตอบเดียว", "info"),
        w="w65"))
    add(pic("ผลจริง: %s" % result(4).replace("(ประมาณ 3 นาที): ", ""), "plan/gantt-plan.png", reads(4), w="w65",
            tag="ผลจริง · อ่านผล · README"))

    CTX.update(kicker="ระยะ B · ขั้นที่ 5", group="ขั้นที่ 5 · What-if")
    lab_head(5)
    wt = table(step(5), "แผน")
    gimg = {"receiptdesk": "plan/gantt-plan.png", "receiptdesk-2": "plan/whatif/gantt-receiptdesk-2.png",
            "receiptdesk-nocodex": "plan/whatif/gantt-receiptdesk-nocodex.png"}
    rows = []
    for r in wt["rows"]:
        name = E.plain(r[0])
        tone = "ok" if r[3].startswith("14") else "bad"
        rows.append('<div class="row"><div class="cardx %s"><h4>%s</h4><p>agent พร้อมกัน %s · %s</p><p><b>วางได้ %s</b> · %s</p><p>%s</p></div>'
                    '<div class="fig">%s</div></div>' % (tone, md(r[0]), r[1], md(r[2]), r[3], md(r[4]), md(r[5]), _img(gimg[name], name)))
    add(S("ผลจริง: มีแผนเดียวที่วางได้ครบ 14 บล็อก", '<div class="p3">%s</div>' % "".join(rows)
          + '<p class="cap">แผน <code>receiptdesk-2</code> วางได้ 8 บล็อก ไม่มี B06, B12 และ B14 · <code>debate</code> และ <code>best_of</code> ใช้ 3 agent เกินเพดาน</p>', tag="ผลจริง · README", maxfs=1.1))
    add(rcards(5, "What-if ใช้เวลา 2 นาที และบอกข้อจำกัดของทีมก่อนเสียเงิน", reads(5), cols=2))

    # ===== ระยะ C
    CTX.update(kicker="ระยะ C · Build · Train · Deploy", group="ระยะ C · Build · Train · Deploy")
    add(E.divider("ระยะ C", "สร้างระบบ เทรนโมเดล และเปิดบริการ", "<p>ขั้นที่ 6–12 จาก 19 · ทีม agent สร้างระบบ · เช่า GPU 2 ใบ · วัดความจุ</p>",
                  "img/s01-gpu-build.jpg"))

    CTX.update(kicker="ระยะ C · ขั้นที่ 6", group="ขั้นที่ 6 · Agent Team")
    r6 = result(6)
    lab_head(6)
    t6 = table(step(6), "บล็อก")
    add(pic("ผลจริง: " + r6.split(":", 1)[1].strip(), "plan/gantt-actual.png", [
        "**%s** · สกิล %s · แผน %s นาที · จริง %s นาที · %s โทเคน · **%s**" % (r[0], r[1], r[2], r[3], r[4], r[5]) for r in t6["rows"]],
        post=note(r6.split(":", 1)[0].strip("() "), "info"), w="w55", tag="ผลจริง · README"))
    add(rcards(6, "บล็อก review ไม่ผ่าน แล้วงานท้ายแผนหยุดทั้งสาย", reads(6)))

    CTX.update(kicker="ระยะ C · ขั้นที่ 7", group="ขั้นที่ 7 · รันต่อ")
    lab_head(7)
    t7 = table(step(7), "รอบตรวจ")
    add(pic("ผลจริง: รันต่อแล้ว B03 ยังไม่ผ่าน และ B04, B11, B12, B14 ยังถูกบล็อก", "image/compare-run2.png",
            ["รอบตรวจที่ %s: %s" % (r[0], r[1]) for r in t7["rows"]], post=note("ผู้ตรวจขอกรณีขอบของไฟล์ PDF ใหม่ทุกรอบ · " + result(7), "info"), w="w65", tag="ผลจริง · README"))
    add(rcards(7, "การรันต่อซ้ำโดยไม่เปลี่ยนอะไรน่าจะได้ผลเดิม จุดนี้คนต้องตัดสินใจ", reads(7)))

    CTX.update(kicker="ระยะ C · ขั้นที่ 8", group="ขั้นที่ 8 · คนตัดสินใจ")
    lab_head(8, nfig("n04-review-scope"))
    add(pic("ผลจริง: ครบ 14 จาก 14 บล็อก · แผน 63.5 นาที ของจริง 92.0 นาที", "plan/compare.png", reads(8),
            post=note(result(8), "info"), w="w55", tag="ผลจริง · อ่านผล · README"))
    t8 = table(step(8), "บล็อก")
    add(S("บล็อกที่ค้างทั้ง 5 บล็อกเสร็จในรอบนี้", bars([
        (r[0], "%s → %s · %s นาที" % (E.plain(r[1]), E.plain(r[2]), r[3]), 1, 1, "%s โทเคน" % r[4]) for r in t8["rows"]]),
        tag="ผลจริง · README"))

    CTX.update(kicker="ระยะ C · ขั้นที่ 9", group="ขั้นที่ 9 · เช่า GPU และ Dataset")
    lab_head(9, explain("ใบเสร็จ 6 ใบจาก Training Set คู่กับ JSON เฉลย", "results/dataset_samples.jpg", [
        "`menu[].nm` · `cnt` · `price`: ชื่อสินค้า · จำนวน · ราคาของบรรทัดนั้น",
        "`sub_total.subtotal_price` · `tax_price`: ยอดก่อนภาษี · ภาษีหรือค่าบริการ",
        "`total.total_price` (สีแดง): **ยอดรวมที่ต้องจ่าย** ช่องที่ Requirement ใช้ตัดสิน",
        "`total.cashprice` · `changeprice`: เงินที่จ่าย · เงินทอน"]))
    add(S("ผลจริง: " + result(9).split(":", 1)[1].strip(), tiles([(r[0], r[1], "ใบเสร็จ", "") for r in ds["rows"]])
          + cards([((k + 1, ""), item_html(a, b), "warn" if k else "") for k, (a, b) in enumerate(reads(9))], 3),
          tag="ผลจริง · อ่านผล · README", cls="mid"))

    CTX.update(kicker="ระยะ C · ขั้นที่ 10", group="ขั้นที่ 10 · Training และ Acceptance Gate")
    lab_head(10, pic("ขั้นที่ 10 เทรนด้วยค่าเดิมบน GPU 1 ใบและ 2 ใบ แล้วตัดสินด้วย Acceptance Gate", "img/n32-train-gate.jpg", [
        "เทรน Qwen3-VL-2B ด้วย LoRA จาก Training Set 400 ใบ 1 Epoch ค่าเดิมทุกอย่าง 2 รอบ: GPU 1 ใบ และ GPU 2 ใบ",
        "วัดเวลาต่อ Epoch แล้วคิด Speedup · Efficiency · เงินต่อ Epoch",
        "วัดผลบน Test Set ก่อนเทรนและหลังเทรน ตามตัวชี้วัดใน Requirement",
        "ตัดสิน 2 เรื่องตามเกณฑ์: Acceptance Gate ผ่านหรือไม่ และการเพิ่ม GPU คุ้มหรือไม่"]))
    sp = table(step(10), "จำนวน GPU")
    g2 = sp["rows"][1]
    r10 = reads(10)
    add(pic("ผลจริง: เพิ่ม GPU คุ้ม · Speedup %s ผ่านเกณฑ์ ≥ 1.6 เท่า" % E.plain(g2[2]), "results/model/train_speed_loss.png",
            ["เวลาต่อ Epoch: %s **%s** (เงินต่อ Epoch %s) · %s **%s** (เงินต่อ Epoch %s)" % (
                sp["rows"][0][0], sp["rows"][0][1], sp["rows"][0][4], g2[0], g2[1], g2[4]),
             "**Speedup %s** (เกณฑ์ใน Requirement ≥ 1.6 เท่า) · **Efficiency %s** (Speedup ÷ จำนวน GPU)" % (E.plain(g2[2]), E.plain(g2[3])),
             r10[0], r10[1]], w="w55", tag="ผลจริง · อ่านผล · README"))
    add(fig("การเทรนช่วยมาก แต่ยังไม่ถึงเกณฑ์ทุกตัว: ดูแท่งสีน้ำเงินที่ยังต่ำกว่าเส้นประสีแดง", "results/model/metrics_before_after.png",
            "ตัวชี้วัด M1 ถึง M7 บน Test Set ก่อนและหลังเทรน · เส้นประสีแดงคือเกณฑ์ใน Requirement"))
    add(tbl("Acceptance Gate ไม่ผ่าน: ผ่าน 2 จาก 6 ตัวชี้วัด", table(step(10), "ตัวชี้วัด"),
            post=note("Gate ต้องผ่าน M1–M6 ทุกตัว · M1 ขาด 1 ใบจาก Test Set 95 ใบ")))
    add(pic("Acceptance Gate หยุดโมเดลที่ดูดีขึ้นมาก แต่ยังไม่ถึงที่ลูกค้าขอ", "img/n33-gate-stop.jpg", r10[2:],
            tag="อ่านผลอย่างไร · README"))

    CTX.update(kicker="ระยะ C · ขั้นที่ 11", group="ขั้นที่ 11 · Deployment")
    lab_head(11, pic("ขั้นที่ 11 เปิดฝั่ง AI บนเครื่อง GPU และเว็บบนเครื่องนี้ แล้วส่งใบเสร็จทั้งเส้นทาง", "img/n34-deploy-path.jpg", [
        "เปิด **vLLM 2 ตัว** (GPU ละ 1 ตัว ใช้โมเดลที่เทรนแล้ว) หลัง **NGINX** `least_conn`",
        "เปิด **RabbitMQ**, **API gateway** และ **GPU Worker 2 ตัว** จากโค้ดในโฟลเดอร์ `app/` และตั้ง API key ใหม่ 1 ตัว",
        "เปิดเว็บและฐานข้อมูลบนเครื่องนี้ด้วย docker compose ที่พอร์ต 3420",
        "ส่งใบเสร็จจาก Test Set 5 ใบผ่านหน้าเว็บ แล้วเทียบยอดรวมในฐานข้อมูลกับที่ gateway ตอบ"], w="w65"))
    t11 = table(step(11), "ส่วนของระบบ")
    add(stack("ผลจริง: ทุกส่วนทำงาน และใบเสร็จ 5 ใบถึงสถานะรอตรวจใน 7.2 วินาที", "img/c11-upload.jpg",
            ["**%s** (%s): %s" % (r[0], E.plain(r[1]), r[2]) for r in t11["rows"]],
            cap='ส่วนหนึ่งของหน้าจริงหลังส่ง 5 ไฟล์: "รับแล้ว 5 ใบ" และตัวนับงานที่ค้างในคิว 5 / 400 · [ภาพเต็ม](results/deploy/upload_5.png)', cols=3, tag="ผลจริง · README"))
    add(pic("ผู้ใช้รอ 7.2 วินาที ส่วนใหญ่เป็นรอบ poll ไม่ใช่เวลาของ GPU", "img/n35-wait-time.jpg", reads(11), w="w55",
            tag="อ่านผลอย่างไร · README"))

    CTX.update(kicker="ระยะ C · ขั้นที่ 12", group="ขั้นที่ 12 · Capacity Test")
    lab_head(12, fig("GPU Worker 2 ตัวอ่าน 100 ใบครบเร็วกว่า 1 ตัวราว 2 เท่า: เทียบเส้นสีส้มกับเส้นสีน้ำเงิน", "results/capacity/capacity_1v2_workers.png",
                     "จำนวนใบเสร็จที่มีผลสะสมตามเวลา · Worker 2 ตัว (สีส้ม) · Worker 1 ตัว (สีน้ำเงิน)"))
    add(fig("งานด่วน 10 ใบแซงงานปกติที่ค้างอยู่ 66 ใบ และเสร็จใน 5.7 วินาที", "results/capacity/urgent_priority.png",
            "งานด่วน (สีส้ม) · งานปกติ (สีน้ำเงิน) ยังเดินต่อจนครบ 100 ใบ"))
    add(tbl("ผลจริง: ผ่านทุกการทดสอบ ทั้งความจุ งานด่วน คิวเต็ม Worker ล่ม และไฟล์เสีย", table(step(12), "การทดสอบ")))
    r12 = reads(12)
    add(pic("คอขวดของงานนี้ไม่ใช่ GPU แต่เป็นคนที่ต้องตรวจใบที่ติดธง", "img/n36-human-bottleneck.jpg", r12[:3],
            tag="อ่านผลอย่างไร · README"))
    add(pic("ข้อจำกัดของการวัดความจุรอบนี้ และจุดที่ควรตามดู", "results/capacity/capacity_1v2_workers.png", r12[3:], w="w55",
            tag="อ่านผลอย่างไร · README"))

    # ===== ระยะ D
    CTX.update(kicker="ระยะ D · Verification", group="ระยะ D · Verification")
    add(E.divider("ระยะ D", "พิสูจน์ว่าระบบทำตาม Requirement", "<p>ขั้นที่ 13–17 จาก 19 · %s</p>" % md(para("6 ·", "ระยะ C จบที่")["lines"][0]),
                  "img/s02-verify.jpg"))

    CTX.update(kicker="ระยะ D · ขั้นที่ 13", group="ขั้นที่ 13 · Exploration")
    lab_head(13, pic("ขั้นที่ 13 ผู้ทดสอบ 6 ตัวสำรวจเว็บพร้อมกัน ตัวละ 1 Test Charter", "img/n37-six-testers.jpg", [
        "อ่าน Requirement แล้วเขียน **Test Charter** 6 ข้อ รูปแบบ \"สำรวจ… ด้วย… เพื่อหา…\"",
        "รีเซ็ตข้อมูลทดสอบ 1 ครั้ง แล้วสั่ง subagent 6 ตัวในข้อความเดียว ตัวละ 1 session ของ playwright-cli",
        "เขียน **ผลที่คาดหวังจาก Requirement ก่อนลอง** แล้วบันทึกผลจริง ✅ ⚠️ ❌ พร้อมภาพหน้าจอ",
        "รวมผลไว้ที่ `test/EXPLORATION.md` พร้อมตารางความเสี่ยง P1 / P2 / P3",
        "ห้ามเปิดโค้ดใน `app/` และห้ามเปิดไฟล์ BUGS-SECRET"]))
    t13 = table(step(13), "Charter")
    add(S("ผลจริง: " + result(13).split(":", 1)[1].strip(), bars([
        (r[0], r[1], int(r[2]), int(r[2]) + int(r[3]) + int(r[4]), "✅ %s · ⚠️ %s · ❌ %s" % (r[2], r[3], r[4])) for r in t13["rows"]]),
        tag="ผลจริง · README"))
    r13 = reads(13)
    add(stack("ไม่มี ❌ ไม่ได้แปลว่าไม่มีปัญหา: ⚠️ 2 ข้อเป็นความเสี่ยงระดับ P1", "img/c13-risk-table.jpg", [r13[2]],
              cap="ส่วนหนึ่งของผลจริง: ตารางความเสี่ยงใน [ภาพสรุปการสำรวจฉบับเต็ม](test/exploration/EXPLORATION.png)", cols=1,
              tag="อ่านผลอย่างไร · README"))
    add(stack("ผู้ทดสอบ 6 ตัวทำงานพร้อมกัน เวลาจริงจึงเท่ากับตัวที่ช้าที่สุด", "img/c13-charters.jpg", [r13[0], r13[1], r13[3]],
              cap="ส่วนหนึ่งของผลจริง: เวลาและผลของแต่ละ Charter", cols=3, tag="อ่านผลอย่างไร · README"))

    CTX.update(kicker="ระยะ D · ขั้นที่ 14", group="ขั้นที่ 14 · Test Plan")
    lab_head(14, nfig("n05-test-types"))
    t14 = table(step(14), "กลุ่ม")
    tot = t14["rows"][-1]
    add(pic("ผลจริง: " + result(14).split(":", 1)[1].strip(), "img/n39-expected-from-req.jpg", reads(14), w="w55",
            top=tiles([("Test Case", E.plain(tot[1]), "กลุ่ม 5.1–5.8", ""), ("ระดับ P1", E.plain(tot[2]), "จาก %s ข้อ" % E.plain(tot[1]), ""),
                       ("ข้อที่ผู้ตรวจพบ", E.plain(tot[3]), "แก้แล้ว %s ข้อ" % E.plain(tot[4]), "warn")]).replace('class="tiles"', 'class="tiles mini"'),
            tag="ผลจริง · อ่านผล · README"))

    CTX.update(kicker="ระยะ D · ขั้นที่ 15", group="ขั้นที่ 15 · Playwright Test")
    lab_head(15, stack("หน้าหลักฐานการทดสอบ: อัตราผ่านรวม 80.7% และอัตราผ่านของ P1 87.5%", "img/c15-report-top.jpg", [],
                       cap="ส่วนหนึ่งของหน้าจริง [`test/index.html`](test/index.html) · [ภาพเต็ม](test/evidence/test-report.png)"))
    t15 = table(step(15), "กลุ่ม")
    add(S("ผลจริง: ผ่าน 46 · ล้ม 11 · บล็อก 2 · ผลตัดสินคือยังส่งมอบไม่ได้", bars([
        (r[0], "ล้ม %s · บล็อก %s · %s" % (r[2], r[3], r[4]), int(r[1]), int(r[1]) + int(r[2]) + int(r[3]), "ผ่าน %s/%d" % (r[1], int(r[1]) + int(r[2]) + int(r[3])))
        for r in t15["rows"] if r[1].strip().isdigit()]), tag="ผลจริง · README"))
    r15 = reads(15)
    add(pic("ข้อที่ล้มถูกคัดแยกก่อนแก้ และผลที่คาดหวังไม่ถูกแก้ให้ตรงกับเว็บ", "img/n40-triage.jpg", [r15[2], r15[0], r15[1]], w="w55",
            tag="อ่านผลอย่างไร · README"))
    add(pic("ตัวอ่านจำลองทำให้รันได้โดยไม่ใช้ GPU แต่การรันพร้อมกันมีราคา", "img/n05-test-types.jpg", r15[3:], tag="อ่านผลอย่างไร · README"))

    CTX.update(kicker="ระยะ D · ขั้นที่ 16", group="ขั้นที่ 16 · Bug Hunt")
    lab_head(16, nfig("n06-boundary-bugs"))
    add(pair("ผลจริง: จับได้ 3 จาก 3 บั๊ก · รอบ BUG_MODE=1 ล้ม 19 ข้อ", ("img/c15b-report-tiles.jpg", "รอบปกติ (ขั้นที่ 15)", "ล้ม 11 ข้อ · [ภาพเต็ม](test/evidence/test-report.png)"),
             ("img/c16b-bughunt-tiles.jpg", "รอบ BUG_MODE=1", "ล้ม 19 ข้อ · [ภาพเต็ม](test/evidence/bug-hunt/report.png)"),
             post='<p class="cap">ส่วนบนของหน้าหลักฐานจริง 2 รอบ · %s</p>' % md(result(16)), tag="ผลจริง · README", rows=True))
    t16 = table(step(16), "บั๊กที่ซ่อนไว้")
    r16 = reads(16)
    add(S("บั๊กที่ซ่อนไว้ทั้ง 3 ตัว และ Test Case ที่จับได้", cards([
        (r[0], "<p>Test Case: %s</p><p><b>ความรุนแรง: %s</b></p>" % (md(r[1]), md(r[2])), "bad" if "วิกฤต" in r[2] else "warn")
        for r in t16["rows"]], 3) + note(r16[2][0]), tag="ผลจริง · README", cls="mid"))
    add(pic("รายงานส่งมอบบอกลูกค้าตรง ๆ ว่ายังไม่พร้อมใช้งานจริง", "img/n41-delivery.jpg", [r16[4], r16[1], r16[3]], tag="อ่านผลอย่างไร · README"))

    CTX.update(kicker="ระยะ D · ขั้นที่ 17", group="ขั้นที่ 17 · ลบเครื่อง")
    lab_head(17)
    add(S("ผลจริง: เครื่องถูกลบแล้ว ค่าเช่ารวม %s" % E.plain(c17["ค่าเช่ารวม"]), cards([
        (E.plain(r[0]), '<p style="font-size:1.35em"><b>%s</b></p>' % md(r[1].replace("**", "")),
         "ok" if "ลบแล้ว" in r[1] else "warn" if "ค่าเช่ารวม" in r[0] else "") for r in t17["rows"]], 3),
        tag="ผลจริง · README", cls="mid"))
    add(pic("เครื่องเปิด 4 ชั่วโมง 48 นาที แต่ใช้งานหนักจริงเพียงช่วงสั้น", "img/n42-machine-time.jpg", reads(17), w="w55",
            tag="อ่านผลอย่างไร · README"))

    # ===== ปิดท้าย: สกิลเวอร์ชัน 1
    CTX.update(kicker="ปิดท้าย · สกิลเวอร์ชัน 1", group="ปิดท้าย · สกิลเวอร์ชัน 1")
    add(E.divider("ปิดท้าย", "ปรับสกิลเป็นเวอร์ชัน 1", "<p>ขั้นที่ 18–19 จาก 19 · %s</p>" % md(para("7 ·", "หัวข้อที่ 1 จบด้วย")["lines"][0]),
                  "img/p22-skill.jpg"))
    CTX.update(kicker="ปิดท้าย · ขั้นที่ 18", group="ขั้นที่ 18 · สกิลเวอร์ชัน 1")
    t18 = table(step(18), "สิ่งที่เพิ่ม")
    lab_head(18, pic("เวอร์ชัน 1 เพิ่ม 5 เรื่องที่งานรอบนี้สอน", "img/n43-skill-v1.jpg",
                     ["**%s** (มาจากขั้นที่ %s): %s" % (r[0], r[1], r[2]) for r in t18["rows"]], tag="README · ขั้นที่ 18"))
    r18 = []
    for x in result(18).split(":", 1)[1].split("·"):
        m = re.match(r"\s*(.*?)\s*(\d+)\s*(\S+)\s*$", x)
        r18.append((m.group(1), m.group(2), m.group(3), ""))
    add(S("ผลจริง: สกิลเวอร์ชัน 1 ได้ %s ไฟล์ พร้อมบันทึกกับดัก %s ข้อ" % (r18[0][1], r18[2][1]), tiles(r18)
          + cards([((k + 1, ""), item_html(a, b), "") for k, (a, b) in enumerate(reads(18))], 3),
          tag="ผลจริง · อ่านผล · README", cls="mid"))
    pg = table(step(18), "ระยะ")
    add(pic("แต่ละระยะมีเกณฑ์ตรวจผ่าน และจุดที่ต้องถามคนก่อนทำต่อ", "img/n44-phase-gates.jpg",
            ["**%s**: %s · **ถามคน:** %s" % (r[0], r[1], r[2]) for r in pg["rows"]], w="w55", tag="README · ขั้นที่ 18"))

    CTX.update(kicker="ปิดท้าย · ขั้นที่ 19", group="ขั้นที่ 19 · ลองใช้สกิล")
    lab_head(19)
    add(tbl("ผลจริง: สกิลได้ 14 บล็อกและ Critical Path เดียวกับการทำทีละขั้น แผนรวม 53.8 นาที เทียบกับ 63.5 นาที", table(step(19), "เรื่อง"), post=note(result(19), "info")))
    add(pic("สกิลวางแผน 14 บล็อกด้วยคำสั่งเดียว แล้วหยุดรอคนอนุมัติ", "results/skill_v1_run/plan/gantt-plan.png", reads(19), w="w55",
            post='<p class="cap">Gantt ของแผน <code>receiptdesk-skill</code> · 4 บัญชี · เวลารวมประมาณ 53.8 นาที</p>', tag="อ่านผลอย่างไร · README"))

    # ===== สรุป
    CTX.update(kicker="สรุป", group="สรุป")
    add(E.divider("สรุป", "ระบบเปิดได้และรับโหลดได้ แต่ยังไม่ทำตามที่ลูกค้าขอครบ", "<p>%s</p>" % md(deliv), "img/p23-delivery.jpg"))
    gate = table(step(10), "ตัวชี้วัด")["rows"]
    cap = table(step(12), "การทดสอบ")["rows"]
    tr = table(step(15), "กลุ่ม")["rows"][-1]
    must = re.search(r"(\d+) จาก (\d+) เรื่อง", result(16))
    bug = re.search(r"(\d+) จาก (\d+) บั๊ก", result(16))
    p1 = re.search(r"\\frac\{(\d+)\}\{(\d+)\}", [l for l in README_LINES if "อัตราผ่านของ P1" in l and "frac" in l][0].split("อัตราผ่านของ P1")[1])
    npass = sum(1 for r in gate if E.plain(r[4]).startswith("ผ่าน"))
    ngate = sum(1 for r in gate if r[0].startswith("M"))
    tpass, tfail, tblock = int(E.plain(tr[1])), int(E.plain(tr[2])), int(E.plain(tr[3]))
    add(S("ภาพรวมของหลักฐาน: ผ่านเกือบทุกด่าน ยกเว้นโมเดลและข้อบกพร่องที่ยังเปิดอยู่", bars([
        ("บล็อกของทีม agent", "ขั้นที่ 8 · หลังคนกำหนดขอบเขตการตรวจ", 14, 14, "14/14"),
        ("Capacity Test และ Failure Test", "ขั้นที่ 12", sum(1 for r in cap if r[3] == "ผ่าน"), len(cap), "%d/%d" % (sum(1 for r in cap if r[3] == "ผ่าน"), len(cap))),
        ("บั๊กที่ซ่อนไว้ที่จับได้", "ขั้นที่ 16", int(bug.group(1)), int(bug.group(2)), "%s/%s" % bug.groups()),
        ("Playwright Test · P1", "ขั้นที่ 15", int(p1.group(1)), int(p1.group(2)), "%s/%s" % p1.groups()),
        ("Playwright Test · ทั้งหมด", "ขั้นที่ 15 · ไม่นับข้อที่ถูกบล็อก %d ข้อ" % tblock, tpass, tpass + tfail, "%d/%d" % (tpass, tpass + tfail)),
        ("User Story ระดับ Must ที่มีหลักฐานว่าผ่าน", "ขั้นที่ 16", int(must.group(1)), int(must.group(2)), "%s/%s" % must.groups()),
        ("Acceptance Gate ของโมเดล", "ขั้นที่ 10 · ต้องผ่านทุกตัว", npass, ngate, "%d/%d" % (npass, ngate)),
    ]), tag="ตัวเลขจาก README"))
    add(tbl("หัวข้อนี้ยากกว่าหัวข้อที่ 1 ตั้งแต่ Requirement จนถึงการทดสอบ", table("สิ่งที่ยากขึ้น", "เรื่อง")))
    add(S("บทเรียนของหัวข้อนี้", cards([
        (("1", "What-if ก่อนรันทีม"), reads(5)[0][0], ""),
        (("2", "คนกำหนดขอบเขตการตรวจ"), reads(8)[2][0], ""),
        (("3", "Acceptance Gate หยุดโมเดลที่ยังไม่ถึงเกณฑ์"), reads(10)[-1][0], "warn"),
        (("4", "ตัวอ่านจำลองแยกจากโมเดลจริง"), reads(15)[3][0], "ok"),
        (("5", "ทดสอบที่เส้นแบ่ง"), reads(16)[0][0], "ok"),
        (("6", "เช่าเครื่องเท่าที่ใช้"), reads(17)[1][0], "warn"),
    ], 3), cls="mid"))
    g10 = reads(10)[2]
    add(pic("ข้อจำกัด 1: โมเดลยังไม่ผ่าน Acceptance Gate ด้วยเหตุ 3 เรื่อง", "results/model/metrics_before_after.png", g10[1],
            post=note(g10[0].split(":")[0], "info"), w="w55", tag="README · ขั้นที่ 10"))
    add(pic("ข้อจำกัด 2: สิ่งที่ยังเปิดอยู่ในระบบและในการวัด", "img/n34-deploy-path.jpg", [
        "**ข้อบกพร่องที่ยังเปิดอยู่:** " + reads(15)[0][0],
        "**ข้อมูลที่ Dataset ไม่มี:** " + reads(9)[1][0],
        "**ความปลอดภัยของ gateway:** " + reads(11)[3][1][1],
        ("**การวัดความจุ:**", reads(12)[3][1])], w="w55", tag="README · ภาพรวมระบบ",
        post='<p class="cap">ภาพรวมระบบฉบับเต็ม: <a href="image/architecture.png" target="_blank"><code>image/architecture.png</code></a></p>'))
    add(E.divider("จบหัวข้อที่ 2", "ReceiptDesk", '<p>รายละเอียดเต็มของหัวข้อนี้: <a href="README.md" target="_blank">README.md</a> · '
                  'พรอมต์ทั้ง 19 ขั้น: <a href="PROMPTS.md" target="_blank">PROMPTS.md</a> · '
                  'รายงานส่งมอบ: <a href="DELIVERY.md" target="_blank">DELIVERY.md</a></p>', "image/cover.jpg"))
    return E.SL


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
