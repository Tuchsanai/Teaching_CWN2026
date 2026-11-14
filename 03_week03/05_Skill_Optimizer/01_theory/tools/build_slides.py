#!/usr/bin/env python3
"""สร้างสไลด์ SkillOpt_Theory_Slides.html ของบททฤษฎี (01_theory/README.md)

  python 01_theory/tools/build_slides.py        (รันจากโฟลเดอร์ของบท 05_Skill_Optimizer หรือจาก 01_theory ก็ได้)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพหรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส
รายละเอียดเต็ม (ตารางสัญลักษณ์ คำอธิบายทีละบรรทัดของ Algorithm 1) อยู่ใน 01_theory/README.md

ที่มาของเนื้อหา
- ตารางและข้อความ: อ่านจาก 01_theory/README.md ตอนสร้าง (สัญลักษณ์ LaTeX ถูกแปลงเป็น HTML ด้วย tex())
- ภาพการ์ตูนใหม่และขั้นตอนข้างภาพ: tools/slides_figures.py · สมการแสดงด้วยภาพ t06 t07 t07c (เรียงพิมพ์ด้วย MathML)
- เครื่องมือเรนเดอร์ (ไฟล์กลาง): tools/slides_engine.py
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import md, sec, walk, table, codes, para, CTX, add, note, fig, explain, tiles, cards, versus, tbl, code
from slides_figures import FIGS

S = E.slide
FIG = {f["img"]: f for f in FIGS}
SYM = {r"\theta": "θ", r"\eta": "η", r"\nabla": "∇", r"\tau": "τ", r"\arg\max": "arg max", r"\max": "max", r"\in": "∈", r"\sum": "∑",
       r"\cdot": "·", r"\leftarrow": "←", r"\lvert": "|", r"\rvert": "|", r"\times": "×", r"\star": "★", r"\tilde{s}": "s̃",
       r"\mathcal{C}": "𝒞", r"\mathcal{B}": "ℬ", r"\qquad": " ", r"\;": " ", r"\,": " "}


def tex(text):
    """แปลงสัญลักษณ์ LaTeX ในบรรทัด ($...$) เป็น HTML ที่อ่านได้ในสไลด์ (ไม่แตะสมการแบบ $$...$$ ซึ่งสไลด์ใช้ภาพแทน)"""
    def one(m):
        t = m.group(1)
        t = re.sub(r"\\text\{([^}]*)\}", r"\1", t)
        for k in sorted(SYM, key=len, reverse=True):
            t = t.replace(k, SYM[k])
        t = re.sub(r"\^\{([^}]*)\}", r"<sup>\1</sup>", t)
        t = re.sub(r"_\{([^}]*)\}", r"<sub>\1</sub>", t)
        t = re.sub(r"_(\w)", r"<sub>\1</sub>", t)
        return re.sub(r"\s+", " ", t).strip()
    return re.sub(r"(?<!\$)\$([^$\n]+)\$(?!\$)", one, text)


SECS = E.load("README.md", transform=tex)


def nfig(key, post=""):
    f = FIG[key]
    return explain(f["title"], "img/%s.jpg" % key, f["steps"], post)


def rows_cards(t, cols=3, head=0, text=1, tones=None, numbered=False):
    """แถวของตาราง 2-3 คอลัมน์ -> การ์ด (หัวข้อ = คอลัมน์ head · ข้อความ = คอลัมน์ text)"""
    items = []
    for k, r in enumerate(t["rows"]):
        h = (k + 1, r[head]) if numbered else r[head]
        body = r[text] if isinstance(text, int) else " · ".join(r[c] for c in text)
        items.append((h, body, (tones or [""] * 99)[k % len(tones or [""])]))
    return cards(items, cols)


def decision(n):
    """การตัดสินใจออกแบบ 1 ข้อ (ข้อ 10.n): ตาราง 2 คอลัมน์ -> การ์ด 6 ใบตามลำดับ คำถาม ... ใน LAB"""
    title = next(s["text"] for s in SECS if s["text"].startswith("10.%d " % n))
    t = table("10.%d " % n, "")
    tone = {"คำถาม": "navy", "ทางเลือก": "", "สิ่งที่เลือก": "ok", "เหตุผล": "", "หลักฐาน": "warn", "ใน LAB ของเรา": "warn"}
    items = [(E.plain(r[0]), r[1], tone.get(E.plain(r[0]), "")) for r in t["rows"]]
    return S("การตัดสินใจที่ %d: %s" % (n, title.split(" ", 1)[1]), cards(items, 3), tag="วิธีคิดในการออกแบบ", cls="mid")


def quiz(a, b):
    qs = [x for x in sec("11 ·") if x["t"] == "details"][a:b]
    body = "".join('<details class="qa"><summary>%s</summary>%s</details>' % (md(q["summary"]), "".join(E.render(x) for x in q["blocks"])) for q in qs)
    return S("ตรวจความเข้าใจ ข้อ %d–%d" % (a + 1, b), body + '<p class="cap">ตอบเองก่อน แล้วคลิกที่คำถามเพื่อดูคำตอบ</p>', cls="quiz", maxfs=1.3)


def build():
    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    add(E.cover("ทฤษฎี · SkillOpt", "ปรับสกิลเหมือนเทรนโมเดล", "../img/s01-theory.jpg",
                small="03_week03 · บทที่ 05 · ภาคทฤษฎีจากเปเปอร์ arXiv:2605.23904"))
    CTX["kicker"] = "0 · ทั้งทฤษฎีใน 1 หน้า"
    add(nfig("g10-overview"))
    add(nfig("g12-design-principles"))
    add(S("บทนี้เดินตามลำดับนี้", cards([
        ("ข้อ 1–4 · ทบทวน และแนวคิด", "Gradient Descent ทำงานอย่างไร · ทำไมเทรนสกิลแทนน้ำหนัก · อะไรตรงกับอะไร · ทำไมการปรับข้อความจึงยาก", "navy"),
        ("ข้อ 5–7 · วิธีการ", "โจทย์ในรูปสมการ 3 สมการ · หนึ่งก้าวของ SkillOpt (Forward · Backward · Gate · ความจำ) · Algorithm 1", ""),
        ("ข้อ 8 · หลักฐาน", "ได้ผลแค่ไหน · ส่วนไหนสำคัญ · ย้ายไปใช้ที่อื่นได้หรือไม่ · สกิลที่ได้หน้าตาอย่างไร", "warn"),
        ("ข้อ 9–11 · เชื่อมกับ LAB", "LAB `money-coder` ตรงและต่างจากเปเปอร์ตรงไหน · วิธีคิดในการออกแบบ 7 ข้อ · ตรวจความเข้าใจ", "ok"),
    ], 2) + note("รายละเอียดเต็มอยู่ใน [`01_theory/README.md`](README.md) · ภาคปฏิบัติอยู่ใน [สไลด์ของบท](../Skill_Optimizer_Slides.html)", "info"), cls="mid"))

    # ===== 1 · Gradient Descent
    CTX.update(kicker="1 · การเทรนโมเดลด้วย Gradient Descent", group="1 · การเทรนโมเดลด้วย Gradient Descent")
    add(E.divider("1", "การเทรนโมเดลด้วย Gradient Descent", "<p>ต้องเข้าใจส่วนนี้ก่อน เพราะ SkillOpt ยืมโครงของมันมาทั้งชุด</p>", small="ทบทวน"))
    t = table("1 ·", "ขั้น")
    add(explain("การเทรนโมเดล = พาลูกบอลเดินลงเนินของ Loss ทีละก้าว", "img/g01-gradient-descent.png",
                ["**%s:** %s (%s)" % (r[0].split(" ", 1)[1], r[1], r[2]) for r in t["rows"]]))
    add(fig("สูตรปรับน้ำหนัก 1 ก้าว: น้ำหนักใหม่ = น้ำหนักเดิม − ขนาดก้าว × ทิศที่ทำให้ Loss เพิ่ม", "img/t04-gd-step.png",
            "Gradient บอกทิศ ณ จุดที่ยืนอยู่เท่านั้น จึงเดินทีละน้อยแล้วคำนวณใหม่ · SkillOpt ใช้เหตุผลชุดเดียวกัน"))
    add(S("คำที่ใช้คู่กับการเทรน 7 คำ", rows_cards(table("1 ·", "คำ"), cols=4, text=(1, 2)) + note(
        "ทุกคำนี้จะมีคู่ของมันใน SkillOpt (ข้อ 3)", label="จำไว้")))

    # ===== 2 · แนวคิด
    CTX.update(kicker="2 · แนวคิดของเปเปอร์", group="2–4 · แนวคิด")
    add(E.divider("2", "เทรนสกิล ไม่เทรนน้ำหนัก", "<p>ถ้าสิ่งที่ Agent ขาดคือ <b>วิธีทำงาน</b> ทำไมต้องไปแก้น้ำหนักของโมเดล</p>", small="แนวคิดของเปเปอร์"))
    add(fig("เทรนน้ำหนักของโมเดล เทียบกับ เทรนข้อความของสกิล", "img/g02-weights-vs-skill.png",
            "สกิล = ข้อความภาษาคนที่ใส่ให้ Agent ก่อนทำงาน · โมเดลถูกล็อก · สิ่งเดียวที่ถูกปรับคือข้อความ"))
    add(nfig("g11-four-ways"))
    add(tbl("การเทรนโมเดลแบบเดิม เทียบกับ SkillOpt", table("2 ·", ""), post=note(
        "ถ้าสกิลคือสิ่งที่ถูกปรับ ก็ควรปรับมันอย่างมีวินัยแบบเดียวกับการเทรนโมเดล: มีหลักฐานต่อก้าว มีขนาดก้าว มีการตรวจ และมีทิศทางที่ต่อเนื่อง", label="คำตอบของเปเปอร์")))

    CTX["kicker"] = "3 · เทียบทีละแนวคิด"
    add(fig("แนวคิดของการเทรนโมเดล มีคู่ใน SkillOpt ทุกตัว", "img/t01-mapping.png", "ซ้าย = ชื่อแนวคิด · กลาง = ในการเทรนโมเดล · ขวา = สิ่งที่ทำหน้าที่เดียวกันใน SkillOpt"))
    t = table("3 ·", "ตรงกัน")
    add(S("การเปรียบนี้ตรงแค่ไหน", cards([("ตรงกัน", "<ul>%s</ul>" % "".join("<li>%s</li>" % md(r[0]) for r in t["rows"]), "ok"),
                                         ("ไม่ตรงกัน", "<ul>%s</ul>" % "".join("<li>%s</li>" % md(r[1]) for r in t["rows"]), "bad")], 2) + note(
        "ข้อเสนอแก้เป็นภาษาไม่รับประกันว่าได้ผล จึงต้องมี **Validation Gate ทุกก้าว**", label="ผลที่ตามมา"), cls="mid"))
    add(S("ปุ่มปรับ 4 ปุ่ม และสิ่งที่แต่ละปุ่มคุม", rows_cards(table("3 ·", "ปุ่ม"), cols=4, text=(2, 3), numbered=True) + note(
        "ถ้าสกิลรุ่นติดกันต่างกันมาก ประวัติว่าแก้อะไรแล้วได้ผลจะใช้กับรุ่นถัดไปไม่ได้ ความนิ่งจึงเป็นหัวใจ", label="ทำไม"), cls="mid"))

    CTX["kicker"] = "4 · ภูมิประเทศของความผิดพลาด"
    add(fig("ภูมิประเทศของความผิดพลาด: 1 จุด = สกิล 1 รุ่น · ความสูง = ความผิดพลาด", "img/g03-landscape.png",
            "ต่างจากการเทรนโมเดล: **เรามองไม่เห็นพื้นผิวนี้** จะรู้ความสูงของจุดใด ต้องให้โมเดลทำงานจริงด้วยสกิลรุ่นนั้นแล้ววัด"))
    add(fig("แก้ตามใจ เทียบกับ แก้ทีละก้าว", "img/g04-adhoc-vs-bounded.png",
            "ก้าวสั้นทำให้รู้ว่าข้อไหนทำให้คะแนนเปลี่ยน และประวัติของก้าวก่อนยังใช้กับรุ่นถัดไปได้"))
    add(nfig("g14-three-difficulties"))
    add(S("SkillOpt = เดินทีละก้าว และรับเมื่อดีขึ้นเท่านั้น", rows_cards(table("4.3", "คุณสมบัติ"), cols=2, text=(1, 2), numbered=True) + note(
        "ศัพท์ของวิชา Optimization: Local Search ที่รับก้าวใหม่เมื่อค่าที่วัดได้ดีขึ้น · เป็นคำอธิบายของบทเรียน ไม่ใช่คำของเปเปอร์", label="หมายเหตุ"), cls="mid"))

    # ===== 5 · สมการ
    CTX.update(kicker="5 · โจทย์ในรูปสมการ", group="5 · โจทย์ในรูปสมการ")
    add(E.divider("5", "โจทย์ในรูปสมการ", "<p>3 สมการต่อกันเป็นสายเดียว: <b>วัด</b> งาน 1 ชิ้น → <b>เลือก</b> สกิลรุ่นที่ดีที่สุด → <b>รายงาน</b> ผลของรุ่นที่เลือก</p>", small="วิธีการ"))
    add(fig("ตารางเดียว เห็นทั้ง 3 สมการ", "img/t05b-eq-grid.png", "แถว = สกิล 1 รุ่น · คอลัมน์ = งาน 1 ชิ้น · ตัวเลขในช่อง = คะแนน"))
    add(fig("ข้อมูล 3 ชุดทำหน้าที่ต่างกัน", "img/t05-eq-overview.png",
            "D<sub>tr</sub> ให้ประสบการณ์ · D<sub>sel</sub> ใช้ตัดสินรับหรือไม่รับ · D<sub>test</sub> ใช้รายงานผลครั้งเดียวตอนจบ"))
    add(fig("สมการ 1: การทำงาน 1 ครั้ง ได้บันทึกการทำงานและคะแนน", "img/t06-eq1.png",
            "ใน LAB: `h( sonnet , cashback , v0/SKILL.md ) → ( Trace ของ Trial นั้น , 0.7 )` · M และ h ไม่เปลี่ยน คะแนนจึงเป็นฟังก์ชันของสกิล"))
    add(fig("สมการ 2: เลือกสกิลรุ่นที่ได้คะแนนเฉลี่ยบน D<sub>sel</sub> สูงสุด", "img/t07-eq2.png", "อ่านจากขวาไปซ้าย: คะแนนของงาน 1 ชิ้น → บวกทุกงาน → หารด้วยจำนวนงาน → เลือกรุ่นที่สูงสุด"))
    add(fig("สมการ 2 คิดตามด้วยคะแนนจริงของ LAB", "img/t07b-eq2-worked.png", "max ตอบว่าค่าสูงสุดเท่ากับเท่าไร · arg max ตอบว่า **รุ่นไหน** ได้ค่านั้น"))
    add(fig("สมการ 3: รายงานผลของรุ่นที่เลือก บนงานที่ไม่เคยเห็น", "img/t07c-eq3.png", "ทำครั้งเดียวตอนจบ · LAB ของเราไม่มี D<sub>test</sub> (แบบฝึกหัดข้อ 2)"))
    t1, t2 = table("5.2", "ถ้าเลือกด้วย"), None
    add(S("ทำไมต้องมีข้อมูล 3 ชุด", cards([
        ("ทำไมสร้างจาก D<sub>tr</sub> แต่เลือกด้วย D<sub>sel</sub>", "สกิลถูกแก้จากข้อผิดของ D<sub>tr</sub> คะแนนบนชุดนั้นจึงสูงเสมอ · D<sub>sel</sub> ไม่ถูกใช้หาวิธีแก้ ถ้าคะแนนขึ้นที่นี่ด้วย แปลว่าสกิลดีขึ้นจริง", "ok"),
        ("ทำไมรายงานด้วย D<sub>test</sub> ไม่ใช่ D<sub>sel</sub>", "สกิลถูกเลือกเพราะได้คะแนนบน D<sub>sel</sub> สูงสุดในหลายรุ่น ส่วนหนึ่งมาจากความบังเอิญ เหมือนทอยลูกเต๋า 10 ครั้งแล้วรายงานเฉพาะครั้งที่แต้มสูงสุด", "warn"),
    ], 2) + note("สมการทั้ง 3 ไม่ได้บอกว่าสกิลรุ่นใหม่ **สร้างขึ้นมาอย่างไร** นั่นคือเนื้อหาของข้อ 6", label="ต่อไป"), cls="mid"))

    # ===== 6 · หนึ่งก้าว
    CTX.update(kicker="6 · หนึ่งก้าวของ SkillOpt", group="6 · หนึ่งก้าวของ SkillOpt")
    add(E.divider("6", "หนึ่งก้าวของ SkillOpt", "<p>Forward Pass (ลองทำงาน) → Backward Pass (หาวิธีแก้สกิล) → Validation Gate (รับ หรือ ไม่รับ)</p>", small="วิธีการ"))
    CTX["kicker"] = "6.1 · Forward Pass: Rollout"
    t = table("6.1", "ลำดับ")
    add(explain("Forward Pass: โมเดลที่ถูกล็อกลองทำงานจริง แล้วบันทึกทุกอย่าง", "img/g05-forward-pass.png", [r[1] for r in t["rows"]]))
    add(fig("Trajectory 1 ใบ เก็บอะไร", "img/g05b-trajectory.png", "คะแนนบอกว่า **ผิด** · Trajectory บอกว่า **ผิดเพราะอะไร** ซึ่งเป็นสิ่งที่ Backward Pass ต้องใช้"))
    CTX["kicker"] = "6.2 · Backward Pass: Minibatch Reflection"
    t = table("6.2", "ขั้น")
    add(explain("Backward Pass: จากหลักฐานที่ได้ ควรแก้สกิลตรงไหน", "img/g06-backward-pass.png", ["**%s:** %s" % (r[0].split(" ", 1)[1], r[1]) for r in t["rows"]]))
    add(fig("อ่านทีละกลุ่ม จึงเห็นข้อผิดที่เกิดซ้ำ", "img/g06b-minibatch.png", "อ่านทีละงานได้วิธีแก้เฉพาะงานนั้น · งานที่ผิดบอกว่าสกิลขาดอะไร · งานที่ถูกบอกว่าอะไรต้องรักษาไว้"))
    add(fig("ข้อเสนอแก้มี 3 แบบ: add · replace · delete", "img/t08-edits.png", "Optimizer เสนอเป็น Edit ทีละข้อ ไม่เขียนสกิลใหม่ทั้งไฟล์ ทุก Edit จึงตรวจย้อนได้ว่ามาจากหลักฐานกลุ่มไหน"))
    add(fig("Learning Rate ของข้อความ = จำนวน Edit สูงสุดต่อก้าว", "img/g06c-learning-rate.png", "เริ่มที่ 4 ลดแบบ Cosine จนเหลือ 2 · ช่วงต้นสกิลยังขาดมาก ช่วงท้ายควรเก็บรายละเอียดโดยไม่ทำของเดิมพัง"))
    add(nfig("g13-optimizer-inside"))
    add(tbl("เกณฑ์จัดอันดับ 4 ข้อ ของ Optimizer", table("6.2.6", "ลำดับ"), post=note(
        "เกณฑ์ข้อ 3 และ 4 คือสิ่งเดียวกับ \"ห้ามใส่ Input หรือคำตอบของข้อตรวจ\" และ \"ทำกติกาให้ตรวจสอบได้\" ใน LAB ของเรา")))
    add(fig("เดินตามตัวอย่างจริง: `v0` → `v1` ของ LAB", "img/t10-reflection-example.png",
            "ข้อ D พบบ่อยเป็นอันดับ 2 แต่ถูกเว้นไว้ เพราะข้อมูลไม่พอจะเขียนเป็นกฎ = Reflection บอกได้ว่าความรู้ขาดตรงไหน แต่บางครั้งความรู้ต้องมาจากคน"))
    add(fig("Backward Pass เทียบ 3 ทาง", "img/t11-backward-three-way.png", "หลักฐาน → หาทิศ → รวมทิศ → จำกัดก้าว เหมือนกันทั้ง Gradient Descent · SkillOpt · LAB ของเรา"))
    CTX["kicker"] = "6.3 · Validation Gate และ Rejected-Edit Buffer"
    t = table("6.3", "ลำดับ")
    add(explain("Validation Gate: ลองแล้ววัด ก่อนรับ", "img/g07-validation-gate.png", [r[1] for r in t["rows"]]))
    add(fig("ตัวอย่างการตัดสิน 6 ก้าว (ตัวเลขสมมติ)", "img/t09-gate-timeline.png", "สกิลปัจจุบันไม่เคยแย่ลง · เท่ากันก็ไม่รับ · ก้าวถัดไปเริ่มจากสกิลปัจจุบันเสมอ"))
    add(S("ทำไมเท่ากันก็ไม่รับ", rows_cards(table("6.3", "เหตุผล"), cols=3, numbered=True), cls="mid"))
    add(fig("Rejected-Edit Buffer: ก้าวที่ผิดถูกจดไว้เตือนก้าวถัดไป", "img/g07b-buffer.png", "จด Edit ที่ลอง และคะแนนที่ลดลง · อยู่ภายใน Epoch เดียว · ใน LAB คือ `runs/ISSUES.md`"))
    CTX["kicker"] = "6.4 · Slow Update และ Meta Skill"
    t = table("6.4.1", "ลำดับ")
    add(explain("Slow Update: เทียบสกิลของ Epoch ก่อนกับปัจจุบัน บนงานชุดเดียวกัน", "img/g08-slow-update.png", [r[1] for r in t["rows"]]))
    add(fig("ไฟล์สกิลมี 2 ส่วน: ส่วนกฎทั่วไป และส่วนที่ถูกป้องกัน", "img/t12-skill-anatomy.png", "ก้าวปกติแก้ส่วนที่ถูกป้องกันไม่ได้ จึงเขียนทับบทเรียนระยะยาวไม่ได้"))
    add(fig("Meta Skill: สมุดส่วนตัวของ Optimizer", "img/g09-meta-skill.png", "จดว่าแก้แบบไหนได้ผล แบบไหนถูกปฏิเสธ · โมเดลที่ทำงานไม่เห็น และไม่ถูกส่งออกไปกับสกิล"))
    add(tbl("ความจำ 3 แบบ เทียบกัน", table("6.4.3", ""), post=note(
        "ถอดทั้ง Meta Skill และ Slow Update ออก SpreadsheetBench ลดจาก 77.5 เหลือ 55.0 (Table 3 ของเปเปอร์)", label="หลักฐาน")))

    # ===== 7 · Algorithm 1
    CTX.update(kicker="7 · Algorithm 1", group="7 · Algorithm 1")
    add(fig("โครงของ Algorithm 1: วงซ้อน 2 ชั้น", "img/t13-timeline.png", "วงนอก = Epoch · วงใน = ก้าว (Forward → Backward → Gate) · ท้าย Epoch ที่ 2 เป็นต้นไปมี Slow Update และ Meta Skill"))
    add(fig("Algorithm 1 ทีละบรรทัด เทียบกับการเทรนโมเดล", "img/t02-algorithm.png", "จุดที่ต่างที่สุด: การเทรนโมเดลวัด Validation ท้าย Epoch · SkillOpt วัด **ทุกก้าว** · คลิกภาพเพื่อขยาย"))
    add(S("สิ่งที่อัลกอริทึมจำไว้ 5 อย่าง", rows_cards(table("7.2", "ตัวแปร"), cols=3, text=(1, 2)), cls="mid"))
    add(tbl("ค่าตั้งต้นในเปเปอร์", table("7.4", "ค่า"), post=note(
        "ค่าตัวเลขที่แน่นอนมีผลไม่มาก แต่ **การมีอยู่** ของแต่ละกลไกมีผลชัดเจน (ข้อ 8.4)")))

    # ===== 8 · ผล
    CTX.update(kicker="8 · ผลในเปเปอร์", group="8 · ผลในเปเปอร์")
    add(E.divider("8", "ผลในเปเปอร์", "<p>ทดลองอย่างไร · ได้ผลแค่ไหน · ส่วนไหนของระบบที่ทำให้ได้ผล · ใช้นอกการทดลองได้แค่ไหน</p>", small="หลักฐาน"))
    add(S("ทดลองอย่างไร", rows_cards(table("8.1", "หัวข้อ"), cols=3) + note(
        "6 Benchmark: SearchQA · SpreadsheetBench · OfficeQA · DocVQA · LiveMath · ALFWorld", "info"), cls="mid"))
    add(fig("ผลหลัก: โมเดลตัวเดียวกัน ต่างกันแค่มีสกิลหรือไม่มี", "img/t14-main-results.png", "GPT-5.5 เพิ่มเฉลี่ย **+23.5 จุด** · งานที่คะแนนตั้งต้นต่ำได้เพิ่มมาก เช่น SpreadsheetBench 41.8 → 80.7"))
    add(fig("เทียบกับวิธีอื่น 6 วิธี", "img/t15-methods.png", "วิธีปรับอัตโนมัติบางวิธีทำให้แย่ลงได้ · SkillOpt ดีที่สุดหรือเท่ากับดีที่สุดใน 52 จาก 52 การทดลอง"))
    add(fig("ถอดออกทีละส่วน (Ablation)", "img/t16-ablation.png", "ถอดส่วนไหนแล้วคะแนนลด แปลว่าส่วนนั้นมีผลจริง · ถอดความจำระยะยาวทั้งหมด เสียหายมากที่สุด"))
    add(nfig("g15-transfer"))
    add(tbl("ย้ายสกิลไปใช้ที่อื่น โดยไม่เทรนเพิ่ม", table("8.5", "ย้ายอย่างไร"), post=note(
        "สกิลเก็บ **วิธีทำงาน** ไม่ใช่คำตอบของงานที่ใช้เทรน · แต่ได้มากบ้างน้อยบ้าง ก่อนย้ายไปใช้จริงต้องวัดใหม่")))
    add(S("ผลนี้มาจากอะไรกันแน่: คำอธิบายอื่นที่ถูกตัดออก", rows_cards(table("8.7", "คำอธิบายอื่น"), cols=3, text=(1, 2), tones=["bad"]), cls="mid"))
    add(fig("Optimizer ต้องเก่งแค่ไหน", "img/t20-optimizer-strength.png", "Optimizer ทำงานเฉพาะตอนเทรน · ใช้โมเดลตัวเดียวกับที่ทำงานก็ยังได้ 56–74% ของผล = วงรอบเองมีส่วนสำคัญ"))
    add(nfig("g17-learned-skill"))
    add(fig("สกิลที่เทรนเสร็จ: ขนาด จำนวนก้าว และต้นทุน", "img/t19-learned-skills.png", "LiveMath ได้ +29.3 จุด และ OfficeQA ได้ +39.0 จุด จากก้าวที่ถูกรับเพียงก้าวเดียว"))
    rules = next(b for b in walk(sec("8.9")) if b["t"] == "table" and E.plain(b["head"][1]).startswith("กฎ"))
    add(tbl("กฎที่สกิลเรียนรู้ได้ เป็นวิธีทำงาน ไม่ใช่คำตอบ", rules, post=note(
        "ไม่มีกฎข้อใดเอ่ยถึงคำถาม ไฟล์ หรือชื่อเฉพาะ จึงเป็นเหตุผลที่สกิลย้ายไปใช้ที่อื่นได้ · สรุปความจาก Figure 4 ของเปเปอร์"), tag="สรุปความ"))
    t = next(b for b in walk(sec("8.9")) if b["t"] == "table" and E.plain(b["head"][0]) == "กรณี")
    add(S("สกิลค่อย ๆ เปลี่ยนอย่างไร: 2 กรณีศึกษา", cards([
        ("%s · คะแนน Test %s" % (r[0], r[3]), "<p><b>เริ่มจาก:</b> %s</p><p><b>Edit ที่ถูกรับเพิ่ม:</b> %s</p>" % (md(r[1]), md(r[2])), "ok") for r in t["rows"]], 2) + note(
        "SkillOpt ไม่ได้แทนสกิลเดิมด้วยข้อความใหม่ แต่เพิ่มข้อกำหนดรอบข้อผิดที่เกิดซ้ำ · เหมือน `v0` → `v3` ของ LAB"), cls="mid"))
    add(nfig("g16-limitations"))

    # ===== 9 · เทียบกับ LAB
    CTX.update(kicker="9 · เทียบกับ LAB ของบทนี้", group="9–11 · เชื่อมกับ LAB")
    add(E.divider("9", "เทียบกับ LAB ของบทนี้", "<p>LAB <code>money-coder</code> คือ SkillOpt ขนาดเล็กที่มีคนกำกับ</p>", small="เชื่อมกับ LAB"))
    add(fig("SkillOpt ในเปเปอร์ เทียบกับ LAB ของบทนี้", "img/t03-vs-lab.png", "ชิ้นส่วนทุกชิ้นของ SkillOpt มีสิ่งที่ทำหน้าที่เดียวกันใน LAB · คลิกภาพเพื่อขยาย"))
    add(tbl("วงรอบของรีโปต้นฉบับ เทียบกับคำสั่งของเรา", table("9.1", "ขั้นของรีโปต้นฉบับ"), post=note(
        "รีโปต้นฉบับ: [github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) · เครื่องมือของเรา: `skillopt.py` ที่ผู้เรียนสร้างใน LAB 0", "info")))
    add(fig("ผลของ LAB อ่านแบบภูมิประเทศ", "img/t17-lab-descent.png", "ความผิดพลาดลดจาก 54.7 เหลือ 0 ใน 4 ก้าวที่ถูกรับ · `v4` คือก้าวที่ถูกปฏิเสธ และถูกจดลง `ISSUES.md`"))
    add(tbl("LAB ต่างจากเปเปอร์ตรงไหน และทำไม", table("9.3", "หัวข้อ")))

    CTX["kicker"] = "10 · วิธีคิดในการออกแบบ"
    add(fig("วิธีคิดในการออกแบบ: การตัดสินใจ 7 ข้อ", "img/t18-design-decisions.png", "ทุกข้ออ่านตามลำดับเดียวกัน: คำถาม → ทางเลือก → สิ่งที่เลือก → เหตุผล → หลักฐาน → ใน LAB ของเรา"))
    for n in range(1, 8):
        add(decision(n))
    add(S("ทุกการตัดสินใจตอบคำถามเดียวกัน",
          '<p class="bigq">ทำอย่างไรให้การแก้ข้อความ<br>ซึ่ง<em>ไม่มีอะไรรับประกันว่าดีขึ้น</em><br>กลายเป็นกระบวนการที่ควบคุมได้ และตรวจย้อนได้</p>'
          '<p class="bigsub">ล็อกโมเดล · ตรวจก่อนรับ · เชื่อหลักฐานที่เกิดซ้ำ · จำกัดขนาดของก้าว · สกิลที่ส่งออกต้องเล็ก</p>', maxfs=1.2))

    CTX["kicker"] = "11 · ตรวจความเข้าใจ"
    add(quiz(0, 5))
    add(quiz(5, 10))
    CTX.update(kicker="", group="จบ")
    add(E.divider("จบภาคทฤษฎี", "ต่อไป: ลงมือทำใน LAB",
                  '<p>ภาคปฏิบัติ: <a href="../Skill_Optimizer_Slides.html" target="_blank">สไลด์ของบท (ภาคทฤษฎีของโจทย์ และ LAB 0–5)</a> · '
                  '<a href="../README.md" target="_blank">README หลัก</a></p>'
                  '<p>รายละเอียดเต็มของทฤษฎี: <a href="README.md" target="_blank">01_theory/README.md</a> · เปเปอร์: '
                  '<a href="https://arxiv.org/abs/2605.23904" target="_blank">arXiv:2605.23904</a></p>', "../img/s04-lab.jpg"))
    return E.SL


E.CSS += """
.qa{background:#fff;border:1px solid var(--line);border-left:7px solid var(--teal);border-radius:10px;padding:.45em .8em;line-height:1.45}
.qa summary{cursor:pointer;font-weight:600;color:var(--navy)}
.qa[open]{border-left-color:var(--green);background:#f5fcf7}
.qa p{margin:.4em 0 0;font-size:.92em}
.slide.quiz .body{overflow:auto}
"""

if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out="SkillOpt_Theory_Slides.html", title="SkillOpt Theory · Slides")
