#!/usr/bin/env python3
"""สร้างสไลด์ WikiSkill_Theory_Slides.html ของบททฤษฎี (01_theory/README.md)

  python tools/build_slides.py        (รันจากโฟลเดอร์ 01_theory)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพหรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส (ป้าย "ตารางหลัก")
รายละเอียดเต็ม (กล่อง "ในเครื่องมือ" ของข้อ 8.1-8.10 · ตาราง Ablation · คำศัพท์) อยู่ใน 01_theory/README.md

ที่มาของเนื้อหา
- ตาราง โค้ด ย่อหน้า และตัวเลขทุกตัว: อ่านจาก 01_theory/README.md ตอนสร้าง (ขั้นตอนข้างภาพของข้อ 8.x มาจากตารางของข้อนั้น)
- ข้อความที่เขียนในไฟล์นี้ (หัวข้อของสไลด์ คำบรรยายใต้ภาพ) ถูกตรวจตอนสร้างว่าตัวเลขทุกตัวมีอยู่ใน README (check_numbers)
- ภาพการ์ตูนใหม่ และภาพถ่ายของหน้าปกและหน้าคั่น: tools/slides_figures.py
- เครื่องมือเรนเดอร์ (ไฟล์กลางของสกิล readme-slides ไม่แก้): tools/slides_engine.py
"""
import html, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import md, plain, sec, walk, table, codes, para, CTX, add, note, fig, explain, tiles, cards, tbl, code

S = E.slide
SECS = E.load("README.md")
OUT, TITLE = "WikiSkill_Theory_Slides.html", "WikiSkill Theory · Slides"
PAPER = "https://arxiv.org/abs/2608.27454"


def M(title, body, tag="", maxfs=1.65):
    """สไลด์การ์ดหรือตัวเลขใหญ่ที่เนื้อหาน้อย: จัดกลางหน้า และยอมให้ตัวอักษรขยายจนเต็มหน้า"""
    return S(title, body, tag=tag, cls="mid", maxfs=maxfs)


def tblM(title, t, post=""):
    """ตารางหลักที่สั้น: จัดกลางหน้า"""
    return S(title, E.table_html(t) + post, tag="ตารางหลัก", cls="mid", maxfs=1.5)


def codeM(title, text, lang="text", pre="", post=""):
    """โค้ดหรือผลจริงที่สั้น: จัดกลางหน้า"""
    return S(title, pre + E.pre_html(text, lang) + post, cls="mid", maxfs=1.5)


# ------------------------------------------------------------------ ตัวช่วยอ่าน README
def P(prefix, start):
    """ข้อความของย่อหน้า (ทุกบรรทัดต่อกัน) ที่ขึ้นต้นด้วย start ในหัวข้อ prefix"""
    return " ".join(para(prefix, start)["lines"])


def body_of(text):
    """ตัดป้ายตัวหนาที่ขึ้นต้นย่อหน้าออก เช่น '**ในเครื่องมือ:** ...' -> '...'"""
    return re.sub(r"^\*\*.+?\*\*\s*", "", text)


def tool(prefix):
    """กล่อง 'ในเครื่องมือ' ของหัวข้อ: แนวคิดนี้คือคำสั่งใดของ wikiskill.py"""
    return note(body_of(P(prefix, "**ในเครื่องมือ:**")), label="ในเครื่องมือ")


def table2(prefix, head1):
    """ตารางในหัวข้อ prefix ที่หัวคอลัมน์ที่สองขึ้นต้นด้วย head1 (ใช้เมื่อหัวคอลัมน์แรกซ้ำกันหรือว่าง)"""
    for b in walk(sec(prefix)):
        if b["t"] == "table" and len(b["head"]) > 1 and plain(b["head"][1]).startswith(head1):
            return b
    raise KeyError("ไม่พบตารางที่คอลัมน์ที่สองขึ้นต้นด้วย %r ในหัวข้อ %r" % (head1, prefix))


def kv(t, r, cols):
    """ช่องของแถว r เป็นบรรทัด 'หัวคอลัมน์: ค่า'"""
    return "".join("<p><b>%s:</b> %s</p>" % (md(plain(t["head"][c])), md(r[c])) for c in cols)


def numbered(cell):
    """'**1 ลืม**' -> (1, 'ลืม')"""
    n, name = plain(cell).split(" ", 1)
    return (n, name)


def nums(text):
    return re.findall(r"\d+(?:\.\d+)?%", text)


def pieces(text):
    """แบ่งเหตุผลเป็นข้อ: ตามเลข (1) (2) (3) ถ้ามี ไม่เช่นนั้นตามเครื่องหมาย ·"""
    if "(1)" in text:
        return [x.strip() for x in re.split(r"\s*\(\d\)\s*", text) if x.strip()]
    return [x.strip() for x in text.split(" · ") if x.strip()]


# ------------------------------------------------------------------ ข้อ 8.1-8.10: การตัดสินใจออกแบบ 1 ข้อ = 1 สไลด์
DEC = {   # ข้อความหลักของสไลด์ (เรียบเรียงจากหัวข้อและแถว "WikiSkill เลือก" ของข้อนั้น) · ภาพ
    1: ("สกิลต้องสั้น ความรู้จึงต้องมีชั้นของตัวเอง", "img/n02-skill-short.jpg"),
    2: ("Raw Layer ห้ามแก้ เพราะ Wiki เป็นการตีความ และการตีความผิดได้", "img/n03-raw-immutable.jpg"),
    3: ("ย้อนกลับเฉพาะสกิล: การทดลองที่ล้มเหลวคือความรู้ชิ้นใหม่", "img/g03-rollback.png"),
    4: ("Inference Agent ห้ามอ่าน Wiki: ความผิดพลาดคือสัญญาณที่ใช้ปรับสกิล", "img/g04-agent-no-wiki.png"),
    5: ("แยก 2 บทบาท: Wiki Maintainer วินิจฉัย · Skill Proposer สั่งยา", "img/g05-two-roles.png"),
    6: ("`skill-impact.md` เขียนโดยโปรแกรม เพราะเป็นข้อเท็จจริงจากการวัด", "img/n04-program-record.jpg"),
    7: ("ทำไม Skill Proposer ต้องเป็น ReAct และเริ่มจาก index", ""),
    8: ("สุ่ม Trace ให้ Wiki Maintainer จำนวนคงที่ และมีทั้งที่ผ่านและไม่ผ่าน", ""),
    9: ("ข้อเสนอต้องเล็ก: 1 สกิลต่อรอบ และแก้แบบ patch", "img/n05-small-patch.jpg"),
    10: ("Gate รับเฉพาะเมื่อดีกว่า R_best และหยุดเมื่อได้ 100%", "img/n06-strict-gate.jpg"),
}


def decision(n, evidence=False, max_reasons=3):
    """ภาพด้านซ้าย + ขั้นตอนด้านขวา: คำถาม -> สิ่งที่เลือก -> เหตุผลทีละข้อ (ข้อความจากตารางของข้อ 8.n ใน README)
    ข้อที่ไม่มีภาพ (8.7 ใช้ภาพเต็มสไลด์นำหน้า · 8.8) แสดงเป็นการ์ด"""
    title, img = DEC[n]
    d = {plain(r[0]): r[1] for r in table("8.%d " % n, "")["rows"]}
    CTX["kicker"] = "ขั้น 8 · วิธีคิดในการออกแบบ · ข้อ 8.%d" % n
    head = []
    if "คำถาม" in d:
        head.append(("คำถาม", d["คำถาม"], "navy"))
    if "ทางเลือก" in d:
        head.append(("ทางเลือก", "%s → **WikiSkill เลือก %s**" % (d["ทางเลือก"], d["WikiSkill เลือก"]), "ok"))
    else:
        head.append(("WikiSkill เลือก", d["WikiSkill เลือก"], "ok"))
    rs = pieces(d["เหตุผล"])
    if len(rs) > max_reasons:
        rs = rs[:max_reasons - 1] + [" · ".join(rs[max_reasons - 1:])]
    items = head + [("เหตุผล", r, "") for r in rs]
    items += [("ข้อแลกเปลี่ยน", r, "warn") for r in pieces(d.get("ข้อแลกเปลี่ยน", ""))[:2]]
    ev = note(d["หลักฐานในเปเปอร์"], label="หลักฐานในเปเปอร์") if evidence and "หลักฐานในเปเปอร์" in d else ""
    if img:
        return explain(title, img, ["**%s:** %s" % (k, v) for k, v, _ in items], ev)
    return M(title, cards(items, 3 if len(items) > 4 else 2) + ev)


def quiz(a, b):
    qs = [x for x in sec("ขั้น 12") if x["t"] == "details"][a:b]
    body = "".join('<details class="qa"><summary>%s</summary>%s</details>' % (md(q["summary"]), "".join(E.render(x) for x in q["blocks"])) for q in qs)
    return S("ตรวจความเข้าใจ ข้อ %d–%d" % (a + 1, b), body + '<p class="cap">ตอบเองก่อน แล้วคลิกที่คำถามเพื่อดูคำตอบ</p>', cls="quiz", maxfs=1.3)


def same_issue():
    """ปัญหาเดียวกันใน 3 ชั้น: บรรทัดนำ + ข้อความจริงของแต่ละชั้น (จาก runs/w1/)"""
    blocks, out = sec("เรื่องเดียวกัน"), []
    for k, b in enumerate(blocks):
        if b["t"] == "p" and b["lines"][0].startswith("**ชั้น"):
            m = re.match(r"\*\*(.+?)\*\*\s*(.+?)\s*\(\[", b["lines"][0])
            c = blocks[k + 1]
            out.append('<h3 class="lead">%s <span>%s</span></h3>%s' % (md(m.group(1)), md(m.group(2).replace("*", "**")), E.pre_html(c["text"], c["lang"])))
    return "".join(out)


def road():
    """แผนของบท: 3 ภาค · คำถามของแต่ละขั้นมาจากตาราง 'อ่านตามลำดับนี้'"""
    q = [plain(r[1]) for r in table("อ่านตามลำดับนี้", "ขั้น")["rows"]]
    parts = [("ภาค 1", "แนวคิดและวิธีการ", "", [("ขั้น 1–3 · ปัญหาและแนวคิด", q[0:3]), ("ขั้น 4–7 · โครงสร้าง วงรอบ และอัลกอริทึม", q[3:7])]),
             ("ภาค 2", "วิธีคิดในการออกแบบ", "", [("ขั้น 8 · การตัดสินใจ 10 ข้อ", q[7:8])]),
             ("ภาค 3", "หลักฐาน", "lab", [("ขั้น 9 · เปรียบเทียบ และผลในเปเปอร์", q[8:9]), ("ขั้น 10–12 · โจทย์ของบทนี้ ข้อจำกัด ทบทวน", q[9:12])])]
    out = []
    for big, name, cls, secs_ in parts:
        boxes = "".join('<div class="secbox"><b>%s</b><span>%s</span></div>' % (md(h), md(" · ".join(x))) for h, x in secs_)
        out.append('<div class="partbox %s"><div class="ph">%s<small>%s</small></div>%s</div>' % (cls, big, name, boxes))
    return '<div class="road">%s</div>' % "".join(out)


def check_numbers(slides):
    """ตัวเลขทุกตัวในสไลด์ (ทศนิยม เปอร์เซ็นต์ และเลข 3 หลักขึ้นไป) ต้องมีอยู่ใน README · ไม่มีอีโมจิในข้อความของสไลด์"""
    src, bad = E.read("README.md"), []
    for k, s in enumerate(slides):
        text = html.unescape(re.sub(r"<[^>]+>", " ", s.get("raw") or " ".join((s["title"], s["kicker"], s["body"]))))
        bad += [(k + 1, t) for t in sorted(set(re.findall(r"\d[\d,]*\.\d+%?|\d+%|\d[\d,]{2,}", text))) if t not in src]
        bad += [(k + 1, "emoji " + t) for t in re.findall("[\U0001F300-\U0001FAFF]", text)]
    assert not bad, "ข้อความในสไลด์ที่ไม่ตรงกับ README (หน้า, ข้อความ): %s" % bad
    print("ตรวจตัวเลข: ตัวเลขทุกตัวใน %d สไลด์มีอยู่ใน README · ไม่มีอีโมจิ" % len(slides))


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    order = table("อ่านตามลำดับนี้", "ขั้น")["rows"]
    over = {plain(r[0]): r[1] for r in table("ภาพรวมใน 1 หน้า", "")["rows"]}

    # ===== เปิด: ปก -> ทั้งเรื่องในภาพเดียว -> ทั้งทฤษฎีใน 1 หน้า -> แผนของบท
    CTX.update(kicker="", group="เริ่มต้น")
    add(E.cover("ทฤษฎี · WikiSkill", "คอมไพล์ประสบการณ์เป็นความรู้ แล้วจึงแก้สกิลจากความรู้", "img/s01-cover.jpg",
                small="03_week03 · บทที่ 06 · ภาคทฤษฎีจากเปเปอร์ arXiv:2608.27454"))
    CTX["kicker"] = "ทั้งทฤษฎีใน 1 หน้า"
    one = body_of(P("ทฤษฎี WikiSkill", "**WikiSkill ในประโยคเดียว:**")).split(" · ")
    cite = para("ทฤษฎี WikiSkill", "เปเปอร์ต้นทาง:")["lines"][0].replace("เปเปอร์ต้นทาง: ", "").replace("*", "")
    add(explain("WikiSkill ในภาพเดียว: มี Wiki คั่นกลางระหว่าง Trace ดิบกับสกิล", "img/g01-three-layers.png", one, note(cite, label="เปเปอร์")))
    tone = {"ปัญหา": "bad", "แนวคิด": "navy", "ผลในเปเปอร์": "warn", "ผลในบทนี้": "ok"}
    add(S("ทั้งทฤษฎีใน 1 หน้า: ปัญหา → แนวคิด → วงรอบ → เหตุผล → ผล", cards([(k, v, tone.get(k, "")) for k, v in over.items()], 3), cls="mid"))
    add(S("สไลด์ชุดนี้เดินตามลำดับนี้", road() + note(
        "รายละเอียดเต็มอยู่ใน [`01_theory/README.md`](README.md) · ภาคปฏิบัติ (LAB 0–5) อยู่ใน [สไลด์ของบท](../WikiSkill_Slides.html)", "info"), cls="mid"))

    # ===== ภาค 1 · แนวคิดและวิธีการ
    CTX.update(kicker="", group="ภาค 1 · ขั้น 1–3 · ปัญหาและแนวคิด")
    add(E.divider("ภาค 1", "แนวคิดและวิธีการ", "<p>%s</p>" % md(" · ".join(plain(r[1]) for r in order[0:3])), "img/s02-how.jpg", small="ขั้น 1–7"))

    CTX["kicker"] = "ขั้น 1 · วงรอบการปรับสกิล"
    add(fig("ทุกวิธีปรับสกิลทำ 4 ขั้นเดียวกัน: Rollout → Analyze → Propose → Gate", "img/t01-loop.png", P("ขั้น 1 ", "วิธีปรับสกิลอัตโนมัติ")))
    t, v = table("ขั้น 1 ", "ขั้น"), table("ขั้น 1 ", "คำ")
    add(S("ทบทวนจากบท 05: 4 ขั้นของวงรอบ และคำศัพท์ที่ใช้ทั้งชุด",
          cards([(numbered(r[0]), "<p>%s</p><p><b>ในบท 05:</b> %s</p>" % (md(r[1]), md(r[2])), "") for r in t["rows"]], 4) +
          cards([(plain(r[0]), r[1], "navy") for r in v["rows"]], 4), cls="mid"))

    CTX["kicker"] = "ขั้น 2 · ปัญหา: ความรู้กระจัดกระจาย"
    add(fig("ปัญหา: ข้อสรุปของแต่ละรอบถูกใช้ครั้งเดียว แล้วหายไปกับประวัติ", "img/t02-problem.png", P("ขั้น 2 ", "ขั้น 2 ของวงรอบ")))
    t = table("ขั้น 2 ", "อาการ")
    add(M("3 อาการที่เกิดเมื่อความรู้ไม่มีที่เก็บ", cards([(numbered(r[0]), r[1], "bad") for r in t["rows"]], 3)))
    ex = para("ขั้น 2 ", "**ตัวอย่างจากบท 05:**")["lines"]
    add(explain("บท 05 เคยเจอปัญหานี้: `ISSUES.md` คือ Wiki ที่เขียนด้วยมือ", "img/g02-forget-vs-remember.png",
                body_of(ex[0]).split(" → ") + ex[1:]))

    CTX["kicker"] = "ขั้น 3 · แนวคิดหลัก: คอมไพล์ประสบการณ์เป็นความรู้"
    t = table2("ขั้น 3 ", "ของดิบ")
    add(explain("คอมไพล์ประสบการณ์เป็นความรู้: ของดิบ → สิ่งที่เรียบเรียงแล้ว → สิ่งที่ใช้ทำงาน", "img/n01-compile.jpg",
                ["**%s:** %s → %s → %s" % (plain(r[0]), r[1], r[2], r[3]) for r in t["rows"]],
                note(P("ขั้น 3 ", "เปเปอร์ได้แนวคิด"), label="ที่มาของแนวคิด")))
    t = table2("ขั้น 3 ", "ตอบคำถาม")
    add(M("Trace · Wiki · สกิล ตอบคำถามคนละข้อ จึงไม่ควรเก็บรวมกัน", cards([(r[0], kv(t, r, (1, 2, 3)), c) for r, c in zip(t["rows"], ("navy", "", "warn"))], 3)))
    a, b = body_of(P("ขั้น 3 ", "**ประโยคที่ต้องจำ:**")).split(" · ")
    add(S("ประโยคที่ต้องจำ", '<p class="bigq">%s</p><p class="bigsub">%s</p>' % (md(a), md(b)), maxfs=1.2))

    CTX.update(kicker="ขั้น 4 · สถาปัตยกรรม 3 ชั้น", group="ภาค 1 · ขั้น 4–5 · โครงสร้าง")
    add(fig("สถาปัตยกรรม 3 ชั้น: Raw Layer · Wiki Layer · Skills Layer", "img/t03-layers.png",
            "แต่ละชั้นมี **ผู้เขียน ผู้อ่าน และวิธีเปลี่ยนแปลง** ต่างกัน · มีเพียง Skills Layer ที่ย้อนกลับได้"))
    add(code("workspace จริงหลังรันจบ: 3 ชั้น = 3 โฟลเดอร์", codes("ขั้น 4 ")[0]["text"], "text", post=tool("ขั้น 4 ")))
    add(S("เรื่องเดียวกัน เขียนต่างกันใน 3 ชั้น: ปัญหา \"รันเป็นโปรแกรมไม่ได้\"", same_issue(), tag="ผลจริง runs/w1", cls="wide-copy"))
    t = table("เรื่องเดียวกัน", "")
    add(M("จากงาน 1 งาน → หลักฐานจากหลายงาน → ทุกงานในอนาคต", cards(
        [(t["head"][c], "".join("<p><b>%s:</b> %s</p>" % (md(r[0]), md(r[c])) for r in t["rows"]), tn) for c, tn in ((1, "navy"), (2, ""), (3, "warn"))], 3)))

    CTX["kicker"] = "ขั้น 5 · ส่วนประกอบ 4 ตัว"
    add(fig("ส่วนประกอบ 4 ตัว: แต่ละตัวเห็นและแก้ได้เฉพาะสิ่งที่จำเป็นต่อหน้าที่", "img/t04-roles.png",
            "**Inference Agent** ห้ามอ่าน Wiki Layer · **Gating and Rollback** เป็นโปรแกรม ไม่ใช่โมเดล"))
    t = table("ขั้น 5 ", "ส่วนประกอบ")
    add(S("ใครรับอะไร ส่งอะไร และเรียกโมเดลกี่ครั้ง", cards([(plain(r[0]), kv(t, r, (1, 2, 3, 4)), c) for r, c in zip(t["rows"], ("navy", "", "warn", "ok"))], 2)))

    CTX.update(kicker="ขั้น 6 · เดิน 1 รอบด้วยผลจริง", group="ภาค 1 · ขั้น 6 · เดิน 1 รอบด้วยผลจริง")
    add(E.divider("ขั้น 6", "เดิน 1 รอบด้วยผลจริง", "<p>%s</p>" % md(P("ขั้น 6 ", "ตัวอย่างทั้งหมด"))))
    add(fig("1 รอบของ WikiSkill = 4 ขั้น และทุกขั้นคือ 1 คำสั่งของ `wikiskill.py`", "img/t05-iteration.png",
            "ตัวเลขจริงของรอบที่ 1 จาก `runs/w1/` · 4 สไลด์ถัดไปเดินทีละขั้นตามภาพนี้"))
    CTX["kicker"] = "ขั้น 6.1 · Rollout: Agent ทำโจทย์ → Raw Layer"
    add(codeM("Rollout: Agent ทำโจทย์โดยไม่มีสกิล และไม่มีงานใดผ่านครบทุกข้อ", codes("6.1")[0]["text"],
              pre=E.render(para("6.1", "Agent (sonnet)")), post=tool("6.1")))
    CTX["kicker"] = "ขั้น 6.2 · Wiki Maintainer: Trace → Wiki Layer"
    add(S("Wiki Maintainer: เรียกโมเดลครั้งเดียว เปลี่ยน Trace เป็นหน้า pattern",
          E.fileflow(table("6.2", "รับเข้า"), "Wiki Maintainer<small>%s</small>" % plain(P("6.2", "เรียกโมเดล").split(" · ")[0]),
                     in_label="รับเข้า", out_label="ส่งออก") + "<p>%s</p>" % md(P("6.2", "เรียกโมเดล")) + tool("6.2"), cls="mid"))
    t = table("6.2", "pattern")
    tn = lambda kind: "ok" if "สำเร็จ" in kind else "warn" if "ยังไม่ยืนยัน" in kind else "navy" if "พฤติกรรม" in kind else "bad"
    add(S("pattern 6 หน้าของรอบที่ 1: จดทั้งสิ่งที่ผิด สิ่งที่ทำถูก และสิ่งที่ยังไม่รู้",
          cards([(r[0], kv(t, r, (1, 2)), tn(r[1])) for r in t["rows"]], 3) + note(P("6.2", "สองหน้าท้าย"))))
    CTX["kicker"] = "ขั้น 6.3 · Skill Proposer: Wiki + Trace → ข้อเสนอ"
    p63 = para("6.3", "เปิด Trace")["lines"]
    add(codeM("Skill Proposer เลือกเปิดไฟล์เอง: ไม่ได้อ่านทุก Trace และไม่ได้อ่านทุกหน้าของ Wiki", codes("6.3")[0]["text"], "text",
              pre="<p>%s</p>" % md(P("6.3", "Proposer ได้รับ")), post=note(p63[0])))
    add(codeM("ข้อเสนอของรอบที่ 1: สร้างสกิลใหม่ พร้อม `PURPOSE.md` ที่ชี้กลับไปยัง Wiki", codes("6.3")[1]["text"], "markdown",
              pre="<p>%s</p>" % md(p63[1]), post=tool("6.3")))
    CTX["kicker"] = "ขั้น 6.4 · Gating and Rollback: ข้อเสนอ → รับหรือย้อนกลับ"
    got, best = nums(codes("6.4")[0]["text"])
    add(S("Gating and Rollback: สกิลที่เสนอได้คะแนนมากกว่า R_best จึงรับ", tiles([
        ("R_best ก่อนหน้า", best, "Validation ของชุดสกิลว่าง", ""), ("Validation ของสกิลที่เสนอ", got, "วัดจากโฟลเดอร์ `candidate/`", ""),
        ("ผล", "ACCEPTED", "มากกว่า R_best", "ok")]) + E.render(para("6.4", "โปรแกรมวางสกิล")) + E.render(para("6.4", "จากนั้นโปรแกรม")) + tool("6.4"), cls="mid", maxfs=1.55))
    CTX["kicker"] = "ขั้น 6.5 · รอบที่ 2: Wiki ทำงานข้ามรอบ"
    t = table("6.5", "สิ่งที่ทำ")
    add(S("รอบที่ 2: Wiki Maintainer ไม่ได้เริ่มจากศูนย์", "<p>%s · %s</p>" % (md(P("6.5", "รอบที่ 2 Agent")), md(body_of(P("6.5", "**Maintainer ไม่ได้เริ่มจากศูนย์**")))) +
          cards([((k + 1, plain(r[0])), r[1], "") for k, r in enumerate(t["rows"])], 3) + E.pre_html(codes("6.5")[0]["text"]), cls="wide-copy"))
    add(tblM("Skill Proposer อ่านน้อยลง เพราะ index บอกแล้วว่าเรื่องใดจบ เรื่องใดยังเปิดอยู่", table2("6.5", "รอบที่ 1"),
             post=note(P("6.5", "ข้อเสนอของรอบที่ 2"))))
    add(M("สองเรื่องที่ต้องรู้เกี่ยวกับตัวอย่างจริงนี้", cards([
        ("เรื่องที่ Wiki จดไว้ แต่สกิลไม่แก้", body_of(P("6.5", "**เรื่องที่ Wiki จดไว้")), "warn"),
        ("ข้อจำกัดของตัวอย่างจริง", body_of(P("6.5", "**ข้อจำกัดของตัวอย่างจริง:**")), "navy")], 2)))

    CTX.update(kicker="ขั้น 7 · อัลกอริทึม", group="ภาค 1 · ขั้น 7 · Algorithm 1")
    add(fig("Algorithm 1 ทีละบรรทัด: 1 คำสั่งของ `wikiskill.py` = 1 กลุ่มบรรทัด", "img/t06-algorithm.png",
            "เลขทางซ้าย = บรรทัดใน Algorithm 1 ของเปเปอร์ · ทางขวา = คำสั่งที่ทำบรรทัดนั้น · คลิกภาพเพื่อขยาย"))
    add(code("Algorithm 1 ฉบับอ่านง่าย: สถานะของระบบมี 3 ตัว", codes("ขั้น 7 ")[0]["text"], "text", pre="<p>%s</p>" % md(P("ขั้น 7 ", "สถานะของระบบ"))))
    t = table("ขั้น 7 ", "บรรทัด")
    add(M("สามบรรทัดที่ทำให้ WikiSkill ต่างจากวงรอบทั่วไป", cards(
        [("บรรทัด " + r[0], "<p>%s</p><p><b>ถ้าตัดออก:</b> %s</p>" % (md(r[1]), md(r[2])), c) for r, c in zip(t["rows"], ("", "warn", "navy"))], 3)))
    t = table("ขั้น 7 ", "k")
    rows = [r for r in t["rows"] if r[0].strip().isdigit()]
    stop = next(r for r in t["rows"] if not r[0].strip().isdigit())
    add(S("สถานะจริงของ `w1`: W โตขึ้นทุกรอบ · S เปลี่ยนเฉพาะเมื่อผ่าน Gate", tiles(
        [("k = %s · %s" % (r[0], r[4]), r[3], "**S:** %s<br>**W:** %s" % (r[1], r[2]), "ok" if r is rows[-1] else "") for r in rows]) +
        note("%s · %s" % (stop[4], P("ขั้น 7 ", "W โตขึ้นทุกรอบ"))), cls="mid", maxfs=1.55))

    # ===== ภาค 2 · วิธีคิดในการออกแบบ
    CTX.update(kicker="", group="ภาค 2 · ขั้น 8 · วิธีคิดในการออกแบบ")
    add(E.divider("ภาค 2", "วิธีคิดในการออกแบบ", "<p>%s</p>" % md(P("ขั้น 8 ", "ส่วนนี้ตอบว่า")), "img/s03-design.jpg", small="ขั้น 8 · การตัดสินใจ 10 ข้อ"))
    add(decision(1))
    add(decision(2))
    add(decision(3))
    add(decision(4))
    add(fig("ถ้า Agent อ่าน Wiki ได้ Trace จะดูดี และสกิลจะไม่ครบในตัวเอง", "img/t07-agent-no-wiki.png",
            "**หลักฐานในเปเปอร์:** " + next(r[1] for r in table("8.4 ", "")["rows"] if plain(r[0]) == "หลักฐานในเปเปอร์")))
    add(decision(5))
    add(decision(6))
    CTX["kicker"] = "ขั้น 8 · วิธีคิดในการออกแบบ · ข้อ 8.7"
    add(fig("Skill Proposer อ่านความรู้ทีละชั้น: index → pattern → Trace", "img/t08-disclosure.png",
            "ได้รับเฉพาะสารบัญตั้งแต่ต้น แล้วใช้เครื่องมือ `Read` เปิดเฉพาะหน้าที่ต้องใช้ (ReAct = คิด → เปิดไฟล์ → คิดต่อ)"))
    add(decision(7))
    add(decision(8))
    add(decision(9))
    add(decision(10, max_reasons=2))
    CTX["kicker"] = "ขั้น 8 · วิธีคิดในการออกแบบ · สรุป"
    t = table("สรุปการออกแบบ", "หลัก")
    add(S("สรุป: หลัก %d ข้อ และผลในระบบ" % len(t["rows"]), cards([((k + 1, r[0]), r[1], "") for k, r in enumerate(t["rows"])], 4), cls="mid"))

    # ===== ภาค 3 · หลักฐาน
    CTX.update(kicker="", group="ภาค 3 · ขั้น 9 · เปรียบเทียบ และผลในเปเปอร์")
    add(E.divider("ภาค 3", "หลักฐาน: ในเปเปอร์ และในโจทย์ของบทนี้", "<p>%s</p>" % md(" · ".join(plain(r[1]) for r in order[8:10])),
                  "img/s04-evidence.jpg", small="ขั้น 9–12"))
    CTX["kicker"] = "ขั้น 9.1 · เทียบกับวิธีปรับสกิลก่อนหน้า"
    add(fig("ทุกวิธีใช้วงรอบเดียวกัน ต่างกันที่วิธีเก็บสิ่งที่เรียนรู้", "img/t09-methods.png",
            "WikiSkill เก็บใน **Wiki Layer ที่แยกออกมาและไม่ถูกย้อนกลับ** · การเรียกโมเดลของผู้ปรับสกิลต่อรอบไม่ขึ้นกับจำนวนโจทย์ Training"))
    t = table("9.1", "วิธี")
    add(M("WikiSkill ทำต่างจาก 3 วิธีก่อนหน้าอย่างไร", cards([(r[0], kv(t, r, (1, 2)), "") for r in t["rows"]], 3)))
    CTX["kicker"] = "ขั้น 9.2 · เทียบกับ Skill Optimizer ของบท 05"
    add(tbl("บท 05 คนกำกับทีละรุ่น · บทนี้โมเดล 2 บทบาทรันเองทั้งวงรอบ", table2("9.2", "Skill Optimizer")))
    CTX["kicker"] = "ขั้น 9.3 · ผลในเปเปอร์"
    add(fig("ผลในเปเปอร์: WikiSkill ได้ค่าเฉลี่ยสูงสุดทุกโมเดล", "img/t11-paper-results.png", P("9.3", "เปเปอร์ทดลอง").replace(" ข้อค้นพบหลัก", "")))
    t = table("9.3", "ข้อค้นพบ")
    add(S("ข้อค้นพบหลัก %d ข้อ" % len(t["rows"]), cards(
        [((k + 1, r[0]), r[1], "warn" if r is t["rows"][-1] else "") for k, r in enumerate(t["rows"])], 3), cls="mid"))
    add(fig("Ablation: Wiki ที่สะสมข้ามรอบคือส่วนที่ทำให้ดีขึ้นมากที่สุด", "img/t12-ablation.png", P("9.3", "การตัดส่วนประกอบ")))
    CTX["kicker"] = "ขั้น 9.4 · พลวัตของสกิลและ Wiki ในเปเปอร์"
    add(fig("พลวัตในเปเปอร์: ข้อเสนอส่วนใหญ่ถูกปฏิเสธ แต่ Wiki โตทุกรอบ", "img/t15-dynamics.png", P("9.4", "เปเปอร์นับว่า")))
    t = table("9.4", "ข้อสังเกต")
    add(M("การย้อนกลับเป็นเรื่องปกติของวงรอบ ไม่ใช่ข้อผิดพลาด", cards(
        [((k + 1, plain(r[0])), "<p><b>%s</b></p><p>%s</p>" % (md(r[1]), md(r[2])), "") for k, r in enumerate(t["rows"])], 2)))
    add(fig("กรณีศึกษา: ข้อเสนอที่ถูกปฏิเสธ ทำให้รอบถัดมาเสนอกฎที่เจาะจงกว่า", "img/t14-case-study.png", P("9.4", "กรณีศึกษา")))
    cost = re.sub(r"^\(Table 7\):\s*", "", body_of(P("9.4", "**ต้นทุนของผู้ปรับสกิล**")))
    m, p_, tot = re.search(r"Maintainer (\d+) ครั้ง", cost), re.search(r"Proposer (ราว [\d–]+ รอบ)", cost), re.search(r"\d+ \+ T_ReAct", cost)
    add(S("ต้นทุนของผู้ปรับสกิลต่อรอบ ไม่ขึ้นกับจำนวนโจทย์ Training", tiles([
        ("Wiki Maintainer", m.group(1), "ครั้งต่อรอบ", ""), ("Skill Proposer", "T_ReAct", p_.group(1), ""),
        ("รวมต่อรอบ", tot.group(0), "ไม่ขึ้นกับจำนวนโจทย์ Training", "ok")]) + note(cost, label="Table 7"), cls="mid", maxfs=1.6))

    CTX.update(kicker="ขั้น 10 · นำมาใช้กับโจทย์ของบทนี้", group="ภาค 3 · ขั้น 10 · นำมาใช้กับโจทย์ของบทนี้")
    add(E.divider("ขั้น 10", "นำมาใช้กับโจทย์ของบทนี้", "<p>%s</p>" % md(P("ขั้น 10 ", "ขั้นนี้ตอบว่า"))))
    t = table("10.2", "ข้อค้นพบ")
    r0, r1, r2 = (nums(r[1]) for r in t["rows"][:3])
    head, tail = over["ผลในบทนี้"].split(" · ", 1)
    add(S("ผลจริงของบทนี้: " + head, tiles([
        ("ไม่มีสกิล", r0[0], "จุดเริ่มต้น", ""), ("WikiSkill · `w1`", r0[1], t["rows"][0][2] + "กับเปเปอร์", "ok"),
        ("Test Set · `w1`", r1[0], "งานที่ไม่เคยเห็น · `w2` ได้ " + r1[1], "ok"), ("ไม่มี Wiki", r2[2], "มี Wiki ได้ %s และ %s" % (r2[0], r2[1]), "warn")]) +
        note(tail), cls="mid", tag="ผลจริง runs/", maxfs=1.6))
    CTX["kicker"] = "ขั้น 10.1 · เปเปอร์กับบทนี้"
    t = table("10.1", "ประเด็น")
    add(S("เปเปอร์กับบทนี้ต่างกัน %d ประเด็น และมีผลต่อการอ่านผล" % len(t["rows"]), cards(
        [(r[0], kv(t, r, (1, 2, 3)), "warn" if r is t["rows"][-1] else "") for r in t["rows"]], 3)))
    CTX["kicker"] = "ขั้น 10.2 · ผลจริงเทียบกับข้อค้นพบของเปเปอร์"
    t = table("10.2", "ข้อค้นพบ")
    same = sum(plain(r[2]).startswith("ตรง") for r in t["rows"])
    add(tblM("ผลจริงตรงกับเปเปอร์ %d จาก %d ข้อ · อีก %d ข้อต่าง เพราะงานเล็กและจบเร็ว" % (same, len(t["rows"]), len(t["rows"]) - same), t))
    CTX["kicker"] = "ขั้น 10.3 · สิ่งที่บทนี้พบเพิ่ม: ความรู้ที่ไม่อยู่ใน Trace"
    t = table("10.3", "ความรู้แฝง")
    add(explain("สิ่งที่บทนี้พบเพิ่ม: ความรู้บางอย่างไม่อยู่ใน Trace", "img/g06-ask-team.png",
                ["**%s** (%s): %s → **%s**" % (r[0], r[1], r[2].replace("**", ""), r[3]) for r in t["rows"]] + [P("10.3", "สิ่งที่ Wiki ให้")]))
    t = table("10.3", "ชั้น")
    add(M("นโยบายธุรกิจไม่เข้าสกิล ด้วยเหตุผล %d ชั้น และทุกชั้นมาจากการออกแบบที่ตั้งใจ" % len(t["rows"]), cards(
        [((k + 1, r[0]), kv(t, r, (1, 2)), "") for k, r in enumerate(t["rows"])], 3)))
    a, b = P("10.3", "ข้อสรุป:").replace("ข้อสรุป: ", "").split(" · ", 1)
    add(S("ข้อสรุปของขั้น 10", '<p class="bigq">%s</p><p class="bigsub">%s</p>' % (md(a.replace("**", "")), md(b)), maxfs=1.2))
    add(tblM("ความรู้เฉพาะงานต้องมาพร้อมขอบเขต และต้องผ่านการวัด", table("10.3", "รุ่น"), post=note(P("10.3", "`w1p` ยืนยัน"))))

    CTX.update(kicker="ขั้น 11 · ข้อจำกัด", group="ภาค 3 · ขั้น 11–12 · ข้อจำกัด และทบทวน")
    t = table("ขั้น 11 ", "ข้อจำกัด")
    add(S("ข้อจำกัด %d ข้อ: สิ่งที่ WikiSkill ยังทำไม่ได้" % len(t["rows"]), cards(
        [((k + 1, r[0]), "<p>%s</p><p><b>ที่มา:</b> %s</p>" % (md(r[2]), md(r[1])), "warn" if "ผลจริง" in r[1] else "") for k, r in enumerate(t["rows"])], 3), cls="mid"))
    CTX["kicker"] = "ขั้น 12 · ทบทวน"
    add(quiz(0, 4))
    add(quiz(4, 8))

    CTX.update(kicker="", group="จบ")
    add(E.divider("จบภาคทฤษฎี", "ต่อไป: ลงมือทำใน LAB",
                  '<p>ภาคปฏิบัติ: <a href="../WikiSkill_Slides.html" target="_blank">สไลด์ของบท (LAB 0–5)</a> · '
                  '<a href="../README.md" target="_blank">README หลัก</a> · '
                  '<a href="../wikiskill_format.md" target="_blank">รูปแบบของ <code>wikiskill</code></a></p>'
                  '<p>รายละเอียดเต็มของทฤษฎี: <a href="README.md" target="_blank">01_theory/README.md</a> · เปเปอร์: '
                  '<a href="%s" target="_blank">arXiv:2608.27454</a></p>' % PAPER, "img/s01-cover.jpg"))
    check_numbers(E.SL)
    return E.SL


E.CSS += """
.qa{background:#fff;border:1px solid var(--line);border-left:7px solid var(--teal);border-radius:10px;padding:.45em .8em;line-height:1.45}
.qa summary{cursor:pointer;font-weight:600;color:var(--navy)}
.qa[open]{border-left-color:var(--green);background:#f5fcf7}
.qa p{margin:.4em 0 0;font-size:.92em}
.slide.quiz .body{overflow:auto}
.slide.wide-copy pre.code{padding-right:6.5em}
"""

if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
