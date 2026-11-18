#!/usr/bin/env python3
"""สร้างสไลด์ EvoSkill_v2_Theory_Slides.html ของบททฤษฎี (01_theory/README.md)

  python tools/build_slides.py        (รันจากโฟลเดอร์ 01_theory)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพหรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส (ป้าย "ตารางหลัก")
ภาพของเราและภาพต้นฉบับจากเปเปอร์ (img/paper/ · CC BY 4.0) อยู่ในสไลด์ที่ติดกันของหัวข้อเดียวกัน เพื่อให้เทียบกันได้
รายละเอียดเต็ม (กล่อง "ในเครื่องมือ" ของทุกขั้น · ตารางไฟล์ของ source code ต้นฉบับ ข้อ 15.4) อยู่ใน 01_theory/README.md

ที่มาของเนื้อหา
- ตาราง โค้ด ย่อหน้า และตัวเลขทุกตัว: อ่านจาก 01_theory/README.md ตอนสร้าง (ขั้นตอนข้างภาพของข้อ 11.x มาจากตารางของข้อนั้น)
- ข้อความที่เขียนในไฟล์นี้ (หัวข้อของสไลด์ คำบรรยายใต้ภาพ) ถูกตรวจตอนสร้างว่าตัวเลขทุกตัวมีอยู่ใน README (check_numbers)
- ภาพการ์ตูนใหม่ และภาพถ่ายของหน้าปกและหน้าคั่น: tools/slides_figures.py
- เครื่องมือเรนเดอร์ (ไฟล์กลางของสกิล readme-slides ไม่แก้): tools/slides_engine.py
"""
import html, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import md, plain, sec, walk, table, codes, para, CTX, add, note, fig, explain, tiles, cards, tbl

S = E.slide
SECS = E.load("README.md")
OUT, TITLE = "EvoSkill_v2_Theory_Slides.html", "EvoSkill v2 Theory · Slides"
PAPER = "https://arxiv.org/abs/2610.25931"
REPO = "https://github.com/sentient-agi/EvoSkill/tree/v2"


def M(title, body, tag="", maxfs=1.65):
    """สไลด์การ์ดหรือตัวเลขใหญ่ที่เนื้อหาน้อย: จัดกลางหน้า และยอมให้ตัวอักษรขยายจนเต็มหน้า"""
    return S(title, body, tag=tag, cls="mid", maxfs=maxfs)


def codeM(title, text, lang="text", pre="", post=""):
    """โค้ดหรือผลจริงที่สั้น: จัดกลางหน้า"""
    return S(title, pre + E.pre_html(text, lang) + post, cls="mid wide-copy", maxfs=1.5)


def paper(title, src, cap):
    """ภาพต้นฉบับจากเปเปอร์ (ไม่ได้แก้ไข) วางต่อจากภาพของเราในหัวข้อเดียวกัน"""
    return fig(title, src, "**ภาพจากเปเปอร์** (Huang et al., 2026 · CC BY 4.0) · " + cap, tag="ภาพจากเปเปอร์")


# ------------------------------------------------------------------ ตัวช่วยอ่าน README
def P(prefix, start):
    """ข้อความของย่อหน้า (ทุกบรรทัดต่อกัน) ที่ขึ้นต้นด้วย start ในหัวข้อ prefix"""
    return " ".join(para(prefix, start)["lines"])


def body_of(text):
    """ตัดป้ายตัวหนาที่ขึ้นต้นย่อหน้าออก เช่น '**ในโค้ด:** ...' -> '...'"""
    return re.sub(r"^\*\*.+?\*\*\s*", "", text)


def incode(prefix):
    """กล่อง 'ในเครื่องมือ' ของหัวข้อ: แนวคิดนี้ทำโดยคำสั่งใดของสกิล evoskill (อ้างข้อของ evoskill_format.md)"""
    return body_of(P(prefix, "**ในเครื่องมือ:**"))


def imgs(prefix):
    return [b for b in sec(prefix) if b["t"] == "img"]


def kvd(prefix):
    """ตารางหัวว่าง 2 คอลัมน์ของข้อ 11.x (อาจมีมากกว่า 1 ตารางในข้อเดียว) -> {หัวแถว: ข้อความ}"""
    d = {}
    for b in walk(sec(prefix)):
        if b["t"] == "table" and not plain(b["head"][0]):
            d.update({plain(r[0]): r[1] for r in b["rows"]})
    return d


def kv(t, r, cols):
    """ช่องของแถว r เป็นบรรทัด 'หัวคอลัมน์: ค่า'"""
    return "".join("<p><b>%s:</b> %s</p>" % (md(plain(t["head"][c])), md(r[c])) for c in cols)


def nums(text):
    return re.findall(r"\d+(?:\.\d+)?%", text)


def pieces(text):
    """แบ่งข้อความเป็นข้อ: ตามเลข (1) (2) (3) ถ้ามี ไม่เช่นนั้นตามเครื่องหมาย · ที่อยู่นอกวงเล็บและนอกโค้ด"""
    if "(1)" in text:
        return [x.strip() for x in re.split(r"\s*\(\d\)\s*", text) if x.strip()]
    out, cur, depth, code, i = [], "", 0, False, 0
    while i < len(text):
        if text.startswith(" · ", i) and depth == 0 and not code:
            out.append(cur.strip())
            cur, i = "", i + 3
            continue
        ch = text[i]
        if ch == "`":
            code = not code
        elif ch == "(" and not code:
            depth += 1
        elif ch == ")" and not code:
            depth = max(0, depth - 1)
        cur += ch
        i += 1
    out.append(cur.strip())
    return [x for x in out if x]


def failbars(items, den):
    """แท่งจำนวน rollout ที่ไม่ผ่านข้อตรวจ: ยิ่งไม่ผ่านมาก แท่งยิ่งแดง (กลับด้านกับ E.bars ซึ่งใช้กับสัดส่วนที่ผ่าน)"""
    out = []
    for name, n, sub in items:
        r = n / den
        tone = "low" if r >= 0.99 else "mid" if r >= 0.5 else ""
        out.append('<div class="bar"><div class="lb">%s%s</div><div class="tr"><div class="fl %s" style="width:%d%%"></div></div>'
                   '<div class="vl">%d/%d</div></div>' % (md("`%s`" % name), "<small>%s</small>" % md(sub) if sub else "", tone, round(r * 100), n, den))
    return '<div class="bars">%s</div>' % "".join(out)


# ------------------------------------------------------------------ ข้อ 11.1-11.10: การตัดสินใจออกแบบ 1 ข้อ = 1 สไลด์
DEC = {   # ข้อความหลักของสไลด์ (เรียบเรียงจากหัวข้อและแถว "EvoSkill v2 เลือก" ของข้อนั้น) · ภาพ · แถวของตารางที่เป็นขั้นข้างภาพ
    1: ("Evolver เป็น Agent ที่มี bash: คำอธิบายต้องถูกทดสอบก่อนเขียนลงสกิล", "img/g05-agent-vs-call.png", ("เหตุผล",)),
    2: ("Evolver เป็นเซสชันเดียวตลอดการรัน: ความเข้าใจต้องสะสม", "img/g06-stateful.png", ("เหตุผล",)),
    3: ("Solver ทำโจทย์ละ 3 ครั้ง: แยกการพลาดซ้ำออกจากการพลาดครั้งนี้พอดี", "img/g07-three-attempts.png", ("เหตุผล",)),
    4: ("รับชุดสกิลของทุก epoch: ไม่ตัดสินด้วยคะแนนที่แกว่ง", "img/g08-accept-all.png", ("เหตุผลข้อ 2", "เหตุผลข้อ 3")),
    5: ("แยก Benchmark Adaptor ออกจาก Evolver: ผู้ถูกวัดต้องไม่เป็นผู้กำหนดการวัด", "img/n03-separate-adaptor.jpg", ("เหตุผล",)),
    6: ("ผู้ใช้เป็นผู้ให้ตัวตรวจ และ Evolver ได้เฉพาะคะแนน 0 ถึง 1", "img/n04-score-only.jpg", ("เหตุผล", "ข้อแลกเปลี่ยน")),
    7: ("วัด Validation ทุก epoch แต่ไม่ใช้ตัดสิน: เป็นมาตรวัดสำหรับคน", "img/n05-validation-meter.jpg", ("เหตุผล", "สิ่งที่ Validation เผย")),
    8: ("prompt ของ Evolver สั้นมาก: กติกาถูกบังคับโดยโครงของเครื่อง ไม่ใช่ด้วยถ้อยคำ", "img/n06-short-prompt.jpg", ("เหตุผล", "เทียบกับบท 06")),
    9: ("staging เริ่มจากชุดเดิม: ค่าเริ่มต้นคือ \"ไม่เปลี่ยน\" Evolver จึงเลือกไม่แก้ได้", "", ("เหตุผล", "ในการรันของเรา")),
    10: ("ขนาดของการรันอยู่ในคำสั่งของผู้ใช้: ไม่มีสัญญาณในระบบที่จะบอกให้หยุด", "", ("เหตุผล", "ข้อสังเกตจากการรันของเรา")),
}
SPLIT = ("เหตุผล",)                       # แถวที่แบ่งเป็นหลายขั้น (ตามเครื่องหมาย · หรือเลขข้อ)
TONE = {"คำถาม": "navy", "EvoSkill v2 เลือก": "ok", "ทางเลือก": "ok", "ข้อแลกเปลี่ยน": "warn", "ในการรันของเรา": "navy",
        "ข้อสังเกตจากการรันของเรา": "warn"}


def decision(n, post_key="", max_reasons=3, post_label=""):
    """ภาพด้านซ้าย + ขั้นตอนด้านขวา: คำถาม -> สิ่งที่เลือก -> เหตุผลทีละข้อ (ข้อความจากตารางของข้อ 11.n ใน README)
    ข้อที่ไม่มีภาพ (11.9 · 11.10) แสดงเป็นการ์ด"""
    title, img, keys = DEC[n]
    d = kvd("11.%d " % n)
    CTX["kicker"] = "ขั้น 11 · วิธีคิดในการออกแบบ · ข้อ 11.%d" % n
    items = []
    if "คำถาม" in d:
        items.append(("คำถาม", d["คำถาม"]))
    if "ทางเลือก" in d:
        items.append(("ทางเลือก", "%s → **EvoSkill v2 เลือก %s**" % (d["ทางเลือก"], d["EvoSkill v2 เลือก"].replace("**", ""))))
    else:
        items.append(("EvoSkill v2 เลือก", d["EvoSkill v2 เลือก"]))
    for k in keys:
        rs = pieces(d[k]) if k in SPLIT else [d[k]]
        if len(rs) > max_reasons:
            rs = rs[:max_reasons - 1] + [" · ".join(rs[max_reasons - 1:])]
        items += [(k, r) for r in rs]
    post = note(d[post_key], label=post_label or post_key) if post_key else ""
    if img:
        return explain(title, img, ["**%s:** %s" % (k, v) for k, v in items], post)
    return M(title, cards([(k, v, TONE.get(k, "")) for k, v in items], 3 if len(items) > 4 else 2) + post)


def evidence(n, title, keys, tones=("", "ok", "warn"), cols=0):
    """การ์ดหลักฐานของข้อ 11.n: แถว 'หลักฐานในเปเปอร์' · 'ในการรันของเรา' · 'ข้อแลกเปลี่ยน' ของตารางข้อนั้น"""
    d = kvd("11.%d " % n)
    return M(title, cards([(k, d[k], t) for k, t in zip(keys, tones)], cols or len(keys)), maxfs=1.5)


def quiz(a, b):
    qs = [x for x in sec("ขั้น 16") if x["t"] == "details"][a:b]
    body = "".join('<details class="qa"><summary>%s</summary>%s</details>' % (md(q["summary"]), "".join(E.render(x) for x in q["blocks"])) for q in qs)
    return S("ตรวจความเข้าใจ ข้อ %d–%d" % (a + 1, a + len(qs)), body + '<p class="cap">ตอบเองก่อน แล้วคลิกที่คำถามเพื่อดูคำตอบ</p>', cls="quiz", maxfs=1.3)


def road():
    """แผนของสไลด์ชุดนี้: 3 ภาค · คำถามของแต่ละขั้นมาจากตาราง 'อ่านตามลำดับนี้'"""
    q = [plain(r[1]) for r in table("อ่านตามลำดับนี้", "ขั้น")["rows"]]
    parts = [("ภาค 1", "แนวคิดและโครงสร้าง", "", [("ขั้น 1–3 · ทำไมต้องปรับสกิล", q[0:3]), ("ขั้น 4–8 · Agent 3 ตัว และการกันข้อมูล", q[3:8])]),
             ("ภาค 2", "การรันจริงและวิธีคิด", "", [("ขั้น 9–10 · เดิน 1 การรัน และอัลกอริทึม", q[8:10]), ("ขั้น 11 · การตัดสินใจออกแบบ 10 ข้อ", q[10:11])]),
             ("ภาค 3", "หลักฐานและการเปรียบเทียบ", "lab", [("ขั้น 12–13 · ผลในเปเปอร์ และวิธีอื่น", q[11:13]), ("ขั้น 14–16 · ข้อจำกัด เปเปอร์กับ LAB ทบทวน", q[13:16])])]
    out = []
    for big, name, cls, secs_ in parts:
        boxes = "".join('<div class="secbox"><b>%s</b><span>%s</span></div>' % (md(h), md(" · ".join(x))) for h, x in secs_)
        out.append('<div class="partbox %s"><div class="ph">%s<small>%s</small></div>%s</div>' % (cls, big, name, boxes))
    return '<div class="road">%s</div>' % "".join(out)


def turn(k, title, tone=""):
    """1 ตาของ Evolver ในการรัน e1: เวลาและจำนวนคำสั่ง + คะแนน Training ก่อนและหลัง + สิ่งที่ทำ + ข้อสรุป (แถวที่ k ของตารางข้อ 9.2)"""
    t = table("9.2", "ตา")
    r = t["rows"][k - 1]
    who = [x.strip() for x in r[0].split(" · ")]                      # "1 · 72 วินาที · Bash 9 ครั้ง"
    val, trn = nums(r[3]), nums(r[4])                                 # คอลัมน์ 3 = Validation ก่อน → หลัง · คอลัมน์ 4 = Training ก่อน → หลัง
    ts = [("ตาที่ %s" % who[0], who[1], who[2], ""),
          ("Validation · `skills_v%s`" % who[0], val[1], "หลัง Solver ใช้ · ก่อนตานี้ %s" % val[0], "ok" if val[0] != val[1] else "warn")]
    if len(trn) == 2:
        ts += [("Training · `skills_v%s`" % who[0], trn[1], "หลัง Solver ใช้ · ก่อนตานี้ %s" % trn[0], "ok" if trn[0] != trn[1] else "warn")]
    else:
        ts += [(plain(t["head"][4]), "–", plain(r[4]).strip("()"), "")]
    body = tiles(ts) + cards([(t["head"][1], r[1], "navy"), (t["head"][2], r[2], tone)], 2)
    return S(title, body, cls="mid", maxfs=1.45, tag="ผลจริง runs/e1")


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
    top = {plain(r[0]): r[1] for r in table("ทฤษฎี EvoSkill v2", "")["rows"]}

    # ===== เปิด: ปก -> ทั้งเรื่องในภาพเดียว -> แผนของสไลด์ชุดนี้
    CTX.update(kicker="", group="เริ่มต้น")
    add(E.cover("ทฤษฎี · EvoSkill v2", "ปรับสกิลของ Agent ด้วย Agent 3 ตัว โดยไม่แตะโมเดล", "img/s01-cover.jpg",
                small="03_week03 · บทที่ 07 · ภาคทฤษฎีจากเปเปอร์ arXiv:2610.25931"))
    CTX["kicker"] = "ทั้งเรื่องในภาพเดียว"
    t = table("ขั้น 4 ", "ช่วง")
    add(explain("EvoSkill v2 ในภาพเดียว: Agent 3 ตัว ปรับสกิลโดยไม่แตะโมเดล", "img/g02-three-agents.png",
                ["**%s · %s:** %s (%s)" % (r[0], plain(r[1]), r[2], r[3]) for r in t["rows"]],
                note(top["เปเปอร์"].replace("*", "") + " · " + plain(top["อ่านต้นฉบับ"]), label="เปเปอร์")))
    CTX["kicker"] = "แผนของสไลด์ชุดนี้"
    kinds = table("ทฤษฎี EvoSkill v2", "แบบ")["rows"]
    add(S("สไลด์ชุดนี้เดินตามลำดับนี้: แนวคิด → การรันจริง → หลักฐาน", road() + note(
        "**ภาพมี 2 แบบ:** %s = %s · %s = %s" % (plain(kinds[0][0]), kinds[0][1], plain(kinds[1][0]), kinds[1][1]), "info") + note(
        "รายละเอียดเต็มอยู่ใน [`01_theory/README.md`](README.md) · ภาคปฏิบัติ (LAB) อยู่ใน [สไลด์ของบท](../EvoSkill_v2_Slides.html)", "info"), cls="mid"))

    # ===== ภาค 1 · แนวคิดและโครงสร้าง
    CTX.update(kicker="", group="ภาค 1 · ขั้น 1–3 · ทำไมต้องปรับสกิล")
    add(E.divider("ภาค 1", "แนวคิดและโครงสร้าง", "<p>%s</p>" % md(" · ".join(plain(r[1]) for r in order[0:4])), "img/s02-concept.jpg", small="ขั้น 1–8"))

    CTX["kicker"] = "ขั้น 1 · ข้อสังเกตตั้งต้น: พลาดแล้วมักพลาดซ้ำ"
    add(explain("ข้อสังเกตตั้งต้น: Agent ที่ไม่มีสกิล พลาดแล้วมักพลาดโจทย์เดิมซ้ำ", "img/g01-fail-again.png",
                [P("ขั้น 1 ", "เปเปอร์เริ่มจาก")] + ["**ตีความ:** " + x for x in pieces(body_of(P("ขั้น 1 ", "**ตีความ:**")))]))
    t, ts = table("ขั้น 1 ", "การวัด"), []
    for r in t["rows"]:
        a, b = re.match(r"(.*?)\s*\((.*)\)$", r[2]).groups()
        ts.append(("%s · %s" % (plain(r[0]), r[1]), re.search(r"\d+ จาก \d+", r[2]).group(0), b if "จาก" in a else a, "bad"))
    add(S("ในโจทย์ที่พลาดอย่างน้อย 1 ครั้ง ส่วนใหญ่พลาดครบทั้ง 3 ครั้ง", '<p class="cap">%s</p>' % md(plain(t["head"][2])) + tiles(ts) +
          note(P("ขั้น 1 ", "ในบทนี้ตรงกับ"), label="ในบทนี้"), cls="mid", maxfs=1.5))
    t = table("ขั้น 1 ", "สาเหตุของการพลาด")
    add(M("พลาดเพราะขาดคำแนะนำ แก้ได้ด้วยการเขียนคำแนะนำให้ = สกิล", cards(
        [(r[0], "**%s:** %s" % (plain(t["head"][1]), r[1]), tn) for r, tn in zip(t["rows"], ("warn", "ok"))], 2) +
        note(P("ขั้น 1 ", "คำแนะนำเป็นภาษาธรรมชาติ"), "info")))

    CTX["kicker"] = "ขั้น 2 · สกิล และสิ่งที่ถูกปรับ"
    t = table("ขั้น 2 ", "")
    add(explain("ปรับสกิล = แก้ข้อความที่โมเดลอ่านตอนทำงาน โมเดลและ Agent Harness ไม่ถูกแตะ", "img/n01-tune-skill.jpg",
                ["**%s:** เทรนโมเดล = %s → ปรับสกิล = %s" % (r[0], r[1], r[2]) for r in t["rows"]],
                note(P("ขั้น 2 ", "EvoSkill v2 เป็น"), label="ชั้นที่วางซ้อน")))
    t = table("ขั้น 2 ", "ส่วนของสกิล")
    add(S("สกิล 1 ตัว = โฟลเดอร์ 1 โฟลเดอร์ ที่ Agent เปิดอ่านทีละส่วน", "<p>%s</p>" % md(P("ขั้น 2 ", "**สกิลในเปเปอร์นี้**")) + cards(
        [((k + 1, r[0]), "<p>%s</p><p><b>%s:</b> %s</p>" % (md(r[1]), md(t["head"][2]), md(r[2])), "") for k, r in enumerate(t["rows"])], 4), cls="mid"))
    t = table("ขั้น 2 ", "คำถามย่อย")
    add(S("คำถามของเปเปอร์: ควรปรับสกิลอย่างไรจึงดีที่สุด", "<p>%s</p>" % md(P("ขั้น 2 ", "คำถามของเปเปอร์จึงไม่ใช่")) + cards(
        [((k + 1, r[0]), "<p><b>%s:</b> %s</p><p>อ่านต่อ: %s</p>" % (md(t["head"][1]), md(r[1]), md(r[2])), "") for k, r in enumerate(t["rows"])], 4), cls="mid"))

    CTX["kicker"] = "ขั้น 3 · จาก EvoSkill v1 สู่ v2"
    add(fig("v2 เปลี่ยน 2 อย่าง: รวมผู้ปรับสกิลเป็น Evolver ตัวเดียว และเพิ่ม Benchmark Adaptor", "img/t01-v1-v2.png", P("ขั้น 3 ", "ชื่อเปเปอร์สรุป").replace("*", "")))
    t = table("ขั้น 3 ", "")
    add(M("สิ่งที่เปลี่ยน 2 อย่าง และสิ่งที่คงไว้ 1 อย่าง", cards([(r[0], kv(t, r, (1, 2)), tn) for r, tn in zip(t["rows"], ("", "", "navy"))], 3)))

    CTX.update(kicker="ขั้น 4 · ภาพรวม: Agent 3 ตัว", group="ภาค 1 · ขั้น 4–5 · Agent 3 ตัว และ Benchmark Adaptor")
    add(fig("อ่านจากบนลงล่าง = ลำดับเวลา: ก่อนการรัน → แต่ละ epoch → หลังการรัน", "img/t02-architecture.png",
            "**ในเครื่องมือ:** " + " · ".join(pieces(incode("ขั้น 4 "))[:3])))
    t = table("ขั้น 4 ", "คำ")
    add(S("คำที่ใช้ตลอดสไลด์ชุดนี้: rollout · epoch · ตา · leg", cards([(r[0], r[1], "navy") for r in t["rows"]], 3), cls="mid"))
    t, im = table("ขั้น 4 ", "ในภาพต้นฉบับ"), imgs("ขั้น 4 ")[1]
    add(paper(im["alt"], im["src"], "เทียบกับภาพก่อนหน้า: " + " · ".join("%s = %s" % (plain(r[0]), plain(r[1])) for r in t["rows"][:3])))

    CTX["kicker"] = "ขั้น 5 · Benchmark Adaptor"
    tin, tout = table("ขั้น 5 ", "สิ่งที่ส่ง"), table("ขั้น 5 ", "ผลลัพธ์")
    add(explain("Benchmark Adaptor: ผู้ใช้อธิบายงานเป็นข้อความ แล้ว Agent เตรียมสนามทดลองให้", "img/g09-adaptor.png", [
        P("ขั้น 5 ", "**ปัญหาที่แก้:**"),
        "**ผู้ใช้ส่ง %d อย่าง:** %s" % (len(tin["rows"]), " · ".join(plain(r[0]) for r in tin["rows"])),
        "**Benchmark Adaptor เขียน %d อย่าง:** %s" % (len(tout["rows"]), " · ".join(r[0] for r in tout["rows"])),
        P("ขั้น 5 ", "จากนั้นโปรแกรม")]))
    add(fig("เข้า 3 อย่าง ออก 2 อย่าง แล้วโปรแกรมล็อกด้วย hash", "img/t03-adaptor.png",
            "**ตัวตรวจ:** " + tin["rows"][2][1] + " · คลิกภาพเพื่อขยาย"))
    add(M("กติกาของ Reference Folder: ต้องไม่มีของ Validation · Test · ตัวตรวจ", cards(
        [(r[0], kv(tout, r, (1, 2)), tn) for r, tn in zip(tout["rows"], ("", "warn"))], 2) + note(P("ขั้น 5 ", "จากนั้นโปรแกรม"), "info"), maxfs=1.5))
    t = table("ขั้น 5 ", "การตั้งค่า")
    add(M("คำสั่งของผู้ใช้กำหนดว่า Evolver เห็นอะไร: บทนี้ทำตามเปเปอร์ทั้ง 2 แบบ", "<p>%s</p>" % md(P("ขั้น 5 ", "**คำสั่งของผู้ใช้เป็นตัวกำหนด")) + cards(
        [(r[0], kv(t, r, (1, 2)), tn) for r, tn in zip(t["rows"], ("ok", "warn"))], 2), maxfs=1.5))
    r = {plain(x[0]): x[1] for x in table("ขั้น 5 ", "รายการ")["rows"]}
    n_task, split_ = re.match(r"โจทย์ (\d+ ข้อ) = (.*)$", r["plug-in"]).groups()
    n_ref, ref_ = r["reference/"].split(": ", 1)
    cost = r["เวลา · เครื่องมือ · ค่าใช้จ่าย"].split(" · ")
    add(S("ผลจริงของบทนี้ (`e1`): Benchmark Adaptor แบ่งชุดตรงกับผู้ใช้ และไม่พบการรั่ว", tiles([
        ("plug-in", n_task, split_, ""), ("`reference/`", n_ref, ref_, ""), ("ค่าใช้จ่าย", cost[2], "เรียกเครื่องมือ " + cost[1], ""),
        ("ตรวจการรั่วอัตโนมัติ", "ไม่พบ", r["ตรวจการรั่วอัตโนมัติ"].replace("ไม่พบ", "", 1), "ok")]) +
        note(r["สิ่งที่ Adaptor ทำเองโดยไม่ได้สั่ง"], label="ทำเองโดยไม่ได้สั่ง"), cls="mid", tag="ผลจริง runs/e1", maxfs=1.5))

    CTX.update(kicker="ขั้น 6 · Solver และ Progressive Disclosure", group="ภาค 1 · ขั้น 6–8 · Solver · Evolver · การกันข้อมูล")
    t = table("ขั้น 6 ", "คุณสมบัติ")
    add(explain("Solver: เห็น `description` ของสกิลตลอดเวลา และเปิดเนื้อหาเต็มเมื่อตรงกับงาน", "img/g10-disclosure.png",
                ["**%s:** %s" % (r[0], r[1]) for r in t["rows"]]))
    add(codeM("`description` ตัดสินว่าสกิลจะถูกเปิดหรือไม่ จึงถูกปรับได้เช่นเดียวกับเนื้อหา", codes("ขั้น 6 ")[0]["text"],
              pre="<p>%s</p><p>%s</p>" % (md(P("ขั้น 6 ", "**ผลที่ตามมา:**")), md(P("ขั้น 6 ", "description ที่ Evolver ของเรา"))),
              post=note(P("ขั้น 6 ", "ตัวอย่างจากเปเปอร์").replace("*", ""), label="ในเปเปอร์")))

    CTX["kicker"] = "ขั้น 7 · Evolver และสิ่งที่มันได้รับ"
    add(fig("Evolver = Claude Code 1 เซสชัน ที่อยู่ตั้งแต่ epoch แรกถึง epoch สุดท้าย", "img/t04-evolver-view.png",
            plain(P("ขั้น 7 ", "**สิ่งที่อยู่บนเครื่องของ Evolver**")) + " · ป้าย **อ่าน** = หลักฐานและประวัติ · ป้าย **เขียน** = งานที่กำลังเขียนและความจำส่วนตัว"))
    t = table("ขั้น 7 ", "สิ่งที่ Evolver ได้รับ")
    add(S("Evolver ได้รับ 3 อย่าง และข้อความประจำ epoch มีไม่กี่บรรทัด", cards(
        [((k + 1, r[0]), "<p>%s</p><p><b>%s:</b> %s</p>" % (md(r[1]), md(t["head"][2]), md(r[2])), "") for k, r in enumerate(t["rows"])], 3) +
        "<p>%s</p>" % md(P("ขั้น 7 ", "ข้อความประจำ epoch ที่ส่งจริง")) + E.pre_html(codes("ขั้น 7 ")[0]["text"]), cls="wide-copy"))
    t = table("ขั้น 7 ", "กลุ่ม")
    add(S("บนเครื่องของ Evolver มีโฟลเดอร์ %d กลุ่ม" % len(t["rows"]), cards(
        [((k + 1, r[0]), "<p>%s</p><p>%s</p>" % (md(r[1]), md(r[2])), "warn" if k >= 3 else "") for k, r in enumerate(t["rows"])], 3), cls="mid"))
    t = table("ขั้น 7 ", "ชั้น")
    add(S("ความจำของ Evolver มี 3 ชั้น: บริบทของเซสชันหายได้ สิ่งที่เขียนลงไฟล์ไม่หาย", cards(
        [((k + 1, r[0]), kv(t, r, (1, 2)), "warn" if k == 0 else "ok") for k, r in enumerate(t["rows"])], 3) +
        note(body_of(P("ขั้น 7 ", "**ทำไมต้องมีโฟลเดอร์ส่วนตัว:**")), label="ทำไมต้องมีโฟลเดอร์ส่วนตัว") +
        note(" · ".join(pieces(incode("ขั้น 7 "))[:3]), label="ในเครื่องมือ"), cls="mid", maxfs=1.5))

    CTX["kicker"] = "ขั้น 8 · การกันข้อมูล และช่องโหว่ของตัวตรวจ"
    t = table("ขั้น 8 ", "อันตราย")
    add(explain("Evolver เห็นเฉพาะชุด Training: กันอันตราย 2 แบบที่ไม่ทิ้งร่องรอย", "img/g03-isolation.png",
                [P("ขั้น 8 ", "**อันตราย 2 แบบ")] + ["**%s:** %s → **กัน:** %s" % (r[0], r[1], r[2]) for r in t["rows"]]))
    add(fig("ใครเห็นอะไร: การกันทำโดยโปรแกรมควบคุมการรัน ไม่ใช่ด้วยการขอร้องใน prompt", "img/t05-who-sees.png",
            P("ขั้น 8 ", "การกันนี้ทำโดย") + " · **ในเครื่องมือ:** " + " · ".join(pieces(incode("ขั้น 8 "))[:2])))
    t = table("ขั้น 8 ", "รับประกัน")
    add(M("การกันข้อมูลรับประกันได้เพียงอย่างเดียว", cards(
        [(t["head"][0], t["rows"][0][0], "ok"), (t["head"][1], t["rows"][0][1], "bad")], 2)))
    t = table("ขั้น 8 ", "ลำดับ")
    add(explain("เรื่องจริงในเปเปอร์: Evolver พบช่องโหว่ของตัวตรวจ คะแนนขึ้นทั้งที่ผลงานไม่ได้ถูกต้องขึ้น", "img/g04-grader-exploit.png",
                [r[1] for r in t["rows"]] + [P("ขั้น 8 ", "บทนี้ทำตาม")], note(body_of(P("ขั้น 8 ", "**บทเรียน:**")), label="บทเรียน")))

    # ===== ภาค 2 · การรันจริงและวิธีคิด
    CTX.update(kicker="", group="ภาค 2 · ขั้น 9 · เดิน 1 การรันด้วยผลจริง")
    add(E.divider("ภาค 2", "การรันจริง อัลกอริทึม และวิธีคิดในการออกแบบ", "<p>%s</p>" % md(" · ".join(plain(r[1]) for r in order[8:11])),
                  "img/s03-run.jpg", small="ขั้น 9–11"))
    CTX["kicker"] = "ขั้น 9 · เดิน 1 การรันด้วยผลจริง"
    add(fig("การรัน `e1` ทั้งเส้น: adapt → base → (turn → rollout) 3 รอบ → test", "img/t14-run-timeline.png", P("ขั้น 9 ", "การรัน `e1`:")))
    CTX["kicker"] = "ขั้น 9.1 · adapt และ base: เตรียมสนาม แล้ววัดเส้นฐาน"
    t = table("9.1", "leg")
    add(S("เส้นฐาน: เมื่อไม่มีสกิล ไม่มี rollout ใดผ่านครบทุกข้อ", tiles(
        [("%s · %s" % (r[0], r[1]), r[3], "%s %s (จาก %s rollout)" % (plain(t["head"][4]), r[4], r[2]), "bad") for r in t["rows"]]),
        cls="mid", tag="ผลจริง runs/e1", maxfs=1.6))
    p = para("9.1", "ข้อตรวจที่ไม่ผ่าน")["lines"]
    head, rest = p[0].split(": ", 1)
    den = int(re.search(r"จาก (\d+) rollout", head).group(1))
    fails = [re.match(r"`(\w+)` (\d+)(?: \((.*)\))?$", x).groups() for x in rest.split(" · ")]
    add(S("ตัวตรวจรู้ว่าข้อใดไม่ผ่าน แต่ Evolver เห็นแค่ตัวเลข 1 ตัวต่อ rollout", "<p>%s</p>" % md(head) +
          failbars([(a, int(b), c or "") for a, b, c in fails], den) + "<p>%s</p>" % md(p[1]) + E.pre_html(codes("9.1")[0]["text"], "json"),
          tag="ผลจริง runs/e1", cls="wide-copy"))

    CTX["kicker"] = "ขั้น 9.2 · สามตาของ Evolver"
    add(fig("สามตาของ Evolver: พบกฎของร้าน 4 ข้อ → เดาผิดเรื่อง 0.1 ที่ขาด → ทดลองย้ายไฟล์เทสต์ซึ่งผิดทาง", "img/t15-evolver-turns.png",
            "ทั้ง 3 ตาอยู่ในเซสชันเดียวกัน · 3 สไลด์ถัดไปเดินทีละตา · คลิกภาพเพื่อขยาย"))
    add(turn(1, "ตาที่ 1: พบกฎของร้าน 4 ข้อจากเฉลยของ Training แล้วเขียนสกิลตัวเดียว", "ok"))
    add(turn(2, "ตาที่ 2: ทดสอบจนตัดสมมติฐานทิ้งได้ แต่เดาผิดว่า 0.1 ที่ขาดคืออะไร", "warn"))
    add(turn(3, "ตาที่ 3: ตัดข้อสันนิษฐานเรื่อง float ทิ้ง แล้วทดลองย้ายไฟล์เทสต์ ซึ่งผิดทาง", "warn"))
    t = table("9.2", "เห็นอะไร")
    add(S("สามตานี้ตรงกับแนวคิดของเปเปอร์ 3 ข้อ", cards([((k + 1, r[1]), r[0], "") for k, r in enumerate(t["rows"])], 3), cls="mid", maxfs=1.5))

    CTX["kicker"] = "ขั้น 9.3 · ทำไมติดที่ 90%"
    t, h = table("9.3", "epoch"), table("9.3", "สิ่งที่ Evolver มี")
    add(S("ทำไมติดที่ 90%: ข้อความของตัวตรวจบอกสาเหตุ แต่ Evolver เห็นแค่ `0.9`", "<p>%s</p>" % md(P("9.3", "ตั้งแต่ epoch 1")) + cards(
        [("epoch %s" % r[0], "<p><b>%s:</b> %s</p><p><b>%s:</b> %s</p>" % (md(t["head"][1]), md(r[1]), md(t["head"][2]), md(r[2])), "bad") for r in t["rows"]], 2) + cards(
        [(h["head"][c], "".join("<p>%s</p>" % md(r[c]) for r in h["rows"]), tn) for c, tn in ((0, "ok"), (1, "warn"))], 2), tag="ผลจริง runs/e1"))
    why = pieces(P("9.3", "Evolver ใช้เทสต์ของเฉลย"))
    add(S("ราคาของการที่ Evolver ได้แต่คะแนน", '<p class="bigq">%s</p><p class="bigsub">%s</p>' % (md(why[0].replace("**", "")), md(why[1])) +
          note(why[2]), maxfs=1.2))

    CTX["kicker"] = "ขั้น 9.4 · test: วัดครั้งเดียวด้วยชุดของ epoch สุดท้าย"
    t = table("9.4", "Test Set")
    add(S("Test Set: จาก %s เป็น %s แต่ยังไม่มี rollout ใดผ่านครบทุกข้อ" % (plain(t["rows"][0][1]), plain(t["rows"][1][1])), tiles(
        [("Test Set · " + r[0], plain(r[1]), "%s %s" % (plain(t["head"][2]), r[2]), tn) for r, tn in zip(t["rows"], ("", "ok"))]) +
        "<p>%s</p>" % md(P("9.4", "ข้อที่ไม่ผ่านใน Test Set")), cls="mid", tag="ผลจริง runs/e1", maxfs=1.6))
    add(explain("นโยบายที่เขียนกว้างเกินหลักฐาน ทำให้งานคืนเงินคอร์สของ Test ผิด", "img/n02-broad-policy.jpg",
                pieces(P("9.4", "เฉลยของ Training บอกเพียง"))))
    add(codeM("หลักฐานจริง: สกิลบอกให้ปัดลง ตัวตรวจคาด 113 แต่ได้ 112", codes("9.4")[0]["text"],
              post=note(" · ".join(pieces(incode("9.4"))[:1]), label="ในเครื่องมือ")))
    cs = []
    for x in pieces(body_of(plain(P("9.4", "ต้นทุน:")).replace("ต้นทุน: ", ""))):
        who, money = re.match(r"(.*) (\$[\d.]+)$", x).groups()
        cs.append((who, money, "", "ok" if "Evolver" in who else ""))
    add(S("ต้นทุนของ `e1`: เกือบทั้งหมดคือ rollout ของ Solver ไม่ใช่ Evolver", tiles(cs), cls="mid", tag="ผลจริง runs/e1", maxfs=1.6))

    CTX.update(kicker="ขั้น 10 · อัลกอริทึม", group="ภาค 2 · ขั้น 10 · อัลกอริทึม")
    add(fig("อัลกอริทึม 10 บรรทัด: ไม่มีบรรทัด \"ถ้าคะแนนดีขึ้นจึงรับ\"", "img/t06-algorithm.png", P("ขั้น 10 ", "เปเปอร์ไม่ได้เขียน") + " · คลิกภาพเพื่อขยาย"))
    add(tbl("เทียบกับ Algorithm 1 ของ WikiSkill (บท 06): รับเสมอ และ Validation ไม่ใช้ตัดสิน", table("ขั้น 10 ", "จุด")))
    t = table("ขั้น 10 ", "K")
    rows = [r for r in t["rows"] if r[0].strip().isdigit()]
    last = next(r for r in t["rows"] if not r[0].strip().isdigit())
    add(S("สถานะจริงของ `e1`: ทุกชุดถูกรับ · Validation จาก %s เป็น %s" % (rows[0][3], rows[-1][3]), tiles(
        [("K = %s · Validation" % r[0], r[3], "**S:** %s<br>Training %s<br>%s" % (r[1], r[2], r[4]), "") for r in rows] +
        [("Test Set · " + last[1], nums(last[4])[0], last[4].split(":")[0], "ok")]) +
        note(" · ".join(pieces(incode("ขั้น 10 "))[1:]), label="ในเครื่องมือ"), cls="mid", tag="ผลจริง runs/e1", maxfs=1.4))

    CTX.update(kicker="ขั้น 11 · วิธีคิดในการออกแบบ", group="ภาค 2 · ขั้น 11 · วิธีคิดในการออกแบบ")
    add(E.divider("ขั้น 11", "วิธีคิดในการออกแบบ", "<p>%s</p>" % md(P("ขั้น 11 ", "ส่วนนี้ตอบว่า"))))
    add(fig("Four Design Choices: การตัดสินใจ 4 ข้อที่เปเปอร์ยกเป็นผลงานหลัก", "img/t07-design-choices.png",
            "ข้อ 11.1–11.4 · ทั้ง 4 ข้อเป็นสิ่งที่ต่างจากวิธีที่เปเปอร์นำมาเทียบ"))
    add(decision(1))
    add(evidence(1, "หลักฐาน: SkillOpt เรียกโมเดล 40 ครั้ง ไม่มีครั้งใดเปิดไฟล์ Excel ได้", ("หลักฐานในเปเปอร์", "ในการรันของเรา")))
    add(decision(2))
    add(evidence(2, "หลักฐาน: ตาที่ 2 และ 3 รันสคริปต์ที่เขียนไว้ในตาก่อน", ("หลักฐานในเปเปอร์", "ในการรันของเรา")))
    m = re.search(r"\((`f1` `f2` `f3`)\) ได้ Test ([\d.% ·]+?) เทียบกับเซสชันเดียว \((`e1` `e2` `v1`)\) (\d[\d.]*%) ทั้ง 3 การรัน = (.*)$", kvd("11.2 ")["ผลที่ ไม่ยืนยัน เปเปอร์"])
    add(S("ผลของเราไม่ยืนยันข้อนี้: เริ่มเซสชันใหม่ทุก epoch ก็ได้ Test ไม่ต่ำกว่าเซสชันเดียว", tiles([
        ("เริ่มเซสชันใหม่ทุก epoch · " + m.group(1), m.group(2), "Test Set ของ 3 การรัน", "warn"),
        ("เซสชันเดียว · " + m.group(3), m.group(4), "Test Set ของ 3 การรัน · ได้เท่ากันทั้งหมด", "")]) + note(m.group(5), label="ไม่ยืนยันเปเปอร์"),
        cls="mid", tag="ผลจริง runs/", maxfs=1.2))
    add(decision(3))
    add(fig("Solver ทำโจทย์เดิมซ้ำ ผลไม่เหมือนกันทุกครั้ง", "img/t08-mixed-tasks.png", "**หลักฐานในเปเปอร์:** " + kvd("11.3 ")["หลักฐานในเปเปอร์"]))
    add(evidence(3, "ในการรันของเรา: โจทย์และสกิลเดียวกัน ได้ 0.5 · 0.3 · 0.5", ("ในการรันของเรา", "ข้อแลกเปลี่ยน"), ("ok", "warn")))
    add(decision(4))
    add(fig("ประตูรับตัดสินด้วยผลต่างที่เล็กกว่าความแกว่ง", "img/t09-rejected.png", "**เหตุผลข้อ 1:** " + kvd("11.4 ")["เหตุผลข้อ 1"]))
    add(evidence(4, "หลักฐานและราคา: epoch สุดท้ายอาจไม่ใช่ชุดที่ดีที่สุด", ("หลักฐานในเปเปอร์", "ข้อแลกเปลี่ยน"), ("", "warn")))
    ps = pieces(kvd("11.4 ")["ในการรันของเรา"])     # [ตรงกับเปเปอร์ · ราคา · ตาสุดท้ายเป็นการทดลอง (e1) · (p2) · ไม่มีขั้นตัดสิน]
    assert len(ps) == 5, ps
    ours = [("สิ่งที่ตรงกับเปเปอร์", ps[0].split(": ", 1)[1], "ok"),
            ("สิ่งที่เป็นราคา", " · ".join([ps[1].split(": ", 1)[1]] + [re.sub(r"^และ", "", x) for x in ps[2:4]]), "warn"),
            ("เมื่อไม่มีขั้นตัดสิน", re.sub(r"^และเมื่อไม่มีขั้นตัดสิน\s*", "", ps[4]), "warn")]
    add(M("ในการรันของเรา: `p1` ถอนการทดลองเองได้ แต่ชุดที่ถูกวัด Test ยังเป็นการทดลอง", cards(ours, 3), tag="ผลจริง runs/", maxfs=1.5))
    add(decision(5))
    add(decision(6))
    a, b = pieces(kvd("11.6 ")["ในการรันของเรา"])
    add(S("ในการรันของเรา: ผู้ใช้บอกเพิ่ม 1 ประโยค แล้ว Test ได้ %s" % nums(b)[0], tiles([
        ("`e1` · Evolver ได้แต่คะแนน", re.search(r"ติดที่ ([\d.]+)", a).group(1), "ต่อ rollout", "warn"),
        ("`n1` และ `n2` · ผู้ใช้เพิ่มหมายเหตุ 1 ประโยค", nums(b)[0], "Test Set ทั้งคู่", "ok")]) + cards([("`e1`", a, "warn"), ("`n1` และ `n2`", b, "ok")], 2),
        cls="mid", tag="ผลจริง runs/", maxfs=1.5))
    add(decision(7))
    add(decision(8, post_key="สิ่งที่ prompt เตือนเรื่องคุณภาพของสกิล", post_label="สิ่งเดียวที่ prompt เตือน"))
    add(decision(9))
    add(decision(10))
    CTX["kicker"] = "ขั้น 11 · วิธีคิดในการออกแบบ · สรุป"
    t = table("สรุปการออกแบบ", "หลัก")
    add(S("สรุป: หลัก %d ข้อ และผลในระบบ" % len(t["rows"]), cards([((k + 1, r[0]), r[1], "") for k, r in enumerate(t["rows"])], 4), cls="mid"))

    # ===== ภาค 3 · หลักฐานและการเปรียบเทียบ
    CTX.update(kicker="", group="ภาค 3 · ขั้น 12 · ผลในเปเปอร์")
    add(E.divider("ภาค 3", "หลักฐาน: ผลในเปเปอร์ วิธีอื่น และ LAB ของบทนี้", "<p>%s</p>" % md(" · ".join(plain(r[1]) for r in order[11:15])),
                  "img/s04-evidence.jpg", small="ขั้น 12–16"))
    CTX["kicker"] = "ขั้น 12.1 · ทดลองอย่างไร"
    t = table("12.1", "หัวข้อ")
    add(S("เปเปอร์ทดลองกับ 2 benchmark ที่ผ่านเมื่อถูกทุกจุด", cards(
        [(t["head"][c], "".join("<p><b>%s:</b> %s</p>" % (md(r[0]), md(r[1] if plain(r[c]) == "เช่นเดียวกัน" else r[c])) for r in t["rows"]), tn)
         for c, tn in ((1, ""), (2, "navy"))], 2) + note(P("12.1", "วิธีที่นำมาเทียบ"), "info")))
    t = table("12.1", "แบบ")
    add(M("แต่ละการเทียบทำ 2 แบบ ตามสิ่งที่ผู้ปรับสกิลเห็น", cards([(r[0], kv(t, r, (1, 2)), tn) for r, tn in zip(t["rows"], ("ok", "warn"))], 2)))

    CTX["kicker"] = "ขั้น 12.2 · ได้ผลแค่ไหน"
    t, im = table("12.2", "ข้อค้นพบ"), imgs("12.2")
    add(fig("ผลในเปเปอร์: เมื่อเห็น Ground Truth ละเอียด EvoSkill v2 สูงสุดทั้งสอง benchmark", im[0]["src"], t["rows"][0][1]))
    add(S("ข้อค้นพบ %d ข้อของผลบน Held-out Test" % len(t["rows"]), cards([((k + 1, r[0]), r[1], "") for k, r in enumerate(t["rows"])], 2), cls="mid", maxfs=1.5))
    mp = table("12.2", "ในภาพต้นฉบับ")["rows"]
    same = lambda r: "ในภาพต้นฉบับ: %s → ในภาพของเรา: %s" % (plain(r[0]), plain(r[1]))
    add(paper(im[1]["alt"], im[1]["src"], "ซ้าย = Held-out · ขวา = คะแนนราย epoch · " + same(mp[0])))
    add(paper(im[2]["alt"], im[2]["src"], "ซ้าย = Held-out · ขวา = คะแนนราย epoch · " + same(mp[2])))
    add(paper(im[3]["alt"], im[3]["src"], "Held-out ทั้งสองแบบ · " + same(mp[1])))

    CTX["kicker"] = "ขั้น 12.3 · สิ่งที่คะแนนราย epoch บอก"
    t, im = table("12.3", "สังเกต"), imgs("12.3")
    add(fig("คะแนนราย epoch: Training ขึ้นมากกว่า Validation หลายเท่า", im[0]["src"], "**%s** = %s" % (t["rows"][0][0], t["rows"][0][1])))
    add(S("สิ่งที่คะแนนราย epoch บอก %d ข้อ" % len(t["rows"]), cards([((k + 1, r[0]), r[1], "warn" if k == 0 else "") for k, r in enumerate(t["rows"])], 3), cls="mid", maxfs=1.5))
    add(paper(im[1]["alt"], im[1]["src"], P("12.3", "ภาพของเราแสดง")))

    CTX["kicker"] = "ขั้น 12.4 · ต้นทุนของผู้ปรับสกิล"
    t = table("12.4", "ข้อค้นพบ")
    add(fig("ต้นทุนของผู้ปรับสกิลต่อ 1 จุดที่เพิ่ม ต่ำสุดทั้ง 4 การเทียบ", imgs("12.4")[0]["src"], "**%s:** %s" % (t["rows"][0][0], t["rows"][0][1])))
    add(S("อ่านต้นทุนอย่างระวัง: ตัวเลขนี้ไม่รวม rollout ของ Solver", cards(
        [((k + 1, r[0]), r[1], "warn" if r is t["rows"][-1] else "") for k, r in enumerate(t["rows"])], 3), cls="mid", maxfs=1.5))
    CTX["kicker"] = "ขั้น 12.5 · สกิลที่ได้หน้าตาอย่างไร"
    t = table("12.5", "benchmark")
    add(M("สกิลที่ได้ในเปเปอร์: ชุดหนึ่งมีสคริปต์ 5 ไฟล์ อีกชุดไม่มีสคริปต์เลย", cards(
        [(r[0], kv(t, r, (1, 2, 3)), "") for r in t["rows"] if "บทนี้" not in r[0]], 2)))

    CTX.update(kicker="ขั้น 13 · เปรียบเทียบกับวิธีอื่น", group="ภาค 3 · ขั้น 13–14 · เปรียบเทียบ และข้อจำกัด")
    add(fig("ทุกระบบมีวงรอบ เสนอ → วัด → ทำซ้ำ เหมือนกัน ที่ต่างคือขั้นเสนอ", "img/t13-methods.png",
            "2 แถวบน = วิธีที่เปเปอร์นำมาเทียบ · 2 แถวกลาง = วิธีของบท 05 และ 06 · แถวล่าง = EvoSkill v2 · คลิกภาพเพื่อขยาย"))
    CTX["kicker"] = "ขั้น 13.1 · เส้นแบ่งที่เปเปอร์ใช้"
    t = table("13.1", "กลุ่ม")
    add(S("เส้นแบ่งที่เปเปอร์ใช้: ขั้นเสนอการแก้ทำอย่างไร", cards(
        [(r[0], "<p>%s</p><p><b>%s:</b> %s</p>" % (md(r[1]), md(t["head"][2]), md(r[2])), "ok" if "v2" in r[2] else "") for r in t["rows"]], 2) +
        note(P("13.1", "ทุกระบบมีวงรอบ"), "info"), cls="mid", maxfs=1.5))
    CTX["kicker"] = "ขั้น 13.2 · กับ WikiSkill ของบท 06"
    add(tbl("WikiSkill เก็บความรู้ใน Wiki และมี Gate · EvoSkill v2 เก็บในเซสชันและรับทุก epoch", table("13.2", "ประเด็น")))
    CTX["kicker"] = "ขั้น 13.3 · กับ Skill Optimizer ของบท 05"
    t = table("13.3", "ประเด็น")
    add(M("บท 05 และ EvoSkill v2 เห็นปัญหาเดียวกัน (คะแนนแกว่ง) แต่ตอบคนละทาง", cards(
        [(t["head"][c], "".join("<p><b>%s:</b> %s</p>" % (md(r[0]), md(r[c])) for r in t["rows"]), tn) for c, tn in ((1, "navy"), (2, ""))], 2), maxfs=1.5))

    CTX["kicker"] = "ขั้น 14 · ข้อจำกัด"
    t = table("ขั้น 14 ", "ข้อจำกัด")
    card = lambda k, r: ((k + 1, r[0]), "<p>%s</p><p><b>%s:</b> %s</p>" % (md(r[2]), md(t["head"][1]), md(r[1])), "" if plain(r[1]).startswith("เปเปอร์") else "warn")
    pap = [card(k, r) for k, r in enumerate(t["rows"]) if plain(r[1]).startswith("เปเปอร์")]
    our = [card(k, r) for k, r in enumerate(t["rows"]) if not plain(r[1]).startswith("เปเปอร์")]
    add(S("ข้อจำกัดที่เปเปอร์รายงาน %d ข้อ" % len(pap), cards(pap, 3), cls="mid"))
    add(S("ข้อจำกัดอีก %d ข้อ ที่พบจากการรันของเราและจาก source code" % len(our), cards(our, 2), cls="mid", maxfs=1.5))

    CTX.update(kicker="ขั้น 15.1 · ตรงกันตรงไหน", group="ภาค 3 · ขั้น 15–16 · เปเปอร์เทียบกับ LAB และทบทวน")
    add(fig("อัลกอริทึม → สกิล evoskill ของบทนี้ → source code ต้นฉบับ", "img/t16-code-map.png",
            "รายการไฟล์เต็มอยู่ในข้อ 15.4 ของ [`01_theory/README.md`](README.md) · source code ต้นฉบับ: [github.com/sentient-agi/EvoSkill](%s) (branch `v2`)" % REPO))
    t = table("15.1", "ชิ้นส่วน")
    add(S("LAB ของเราตรงกับเปเปอร์ %d ชิ้นส่วน" % len(t["rows"]), cards([(r[0], kv(t, r, (1, 2)), "ok") for r in t["rows"]], 3), cls="mid"))
    CTX["kicker"] = "ขั้น 15.2 · ต่างกันตรงไหน และทำไม"
    t = table("15.2", "หัวข้อ")
    n = len(t["rows"])
    add(S("LAB ต่างจากเปเปอร์ %d หัวข้อ และทุกข้อมีเหตุผล (1/2)" % n, cards([(r[0], kv(t, r, (1, 2, 3)), "") for r in t["rows"][:5]], 3), cls="mid"))
    add(S("LAB ต่างจากเปเปอร์ %d หัวข้อ และทุกข้อมีเหตุผล (2/2)" % n, cards([(r[0], kv(t, r, (1, 2, 3)), "") for r in t["rows"][5:]], 2), cls="mid"))
    CTX["kicker"] = "ขั้น 15.3 · ผลของ LAB อ่านด้วยภาษาของเปเปอร์"
    t = table("15.3", "เปเปอร์บอกว่า")
    r = next(x for x in t["rows"] if x[0].startswith("เห็นเฉลยของ Training"))
    a, b = nums(r[1])[:2]                            # e1 · p1 (ค่าที่ 3 คือ p2 อยู่ในวงเล็บ)
    add(S("%s: Test %s เทียบ %s" % (r[0], a, b), tiles([
        ("`e1` · Evolver เห็นเฉลยของ Training", a, "Test Set", "ok"), ("`p1` · Evolver เห็นแค่คะแนน", b, "Test Set", "warn")]) +
        note(P("15.3", "ผลของทุกการรัน"), "info"), cls="mid", tag="ผลจริง runs/", maxfs=1.6))
    lab = lambda r, tn="": (r[0], "<p><b>%s:</b> %s</p>" % (md(t["head"][1]), md(r[1])), tn)
    add(S("สิ่งที่เปเปอร์บอก เกิดซ้ำใน LAB ของเรา (1/2)", cards([lab(r) for r in t["rows"][:5]], 3), cls="mid", tag="ผลจริง runs/"))
    add(S("สิ่งที่เปเปอร์บอก เกิดซ้ำใน LAB ของเรา (2/2)", cards([lab(r) for r in t["rows"][5:8]], 3), cls="mid", tag="ผลจริง runs/", maxfs=1.5))
    add(S("สองเรื่องที่ต้องอ่านอย่างระวัง: เซสชันเดียว และกฎเฉพาะงานในเฉลย", cards(
        [lab(r, "warn") for r in t["rows"][8:]], 2), cls="mid", tag="ผลจริง runs/", maxfs=1.5))

    CTX["kicker"] = "ขั้น 16 · ทบทวน"
    add(quiz(0, 5))
    add(quiz(5, 9))

    CTX.update(kicker="", group="จบ")
    add(E.divider("จบภาคทฤษฎี", "ต่อไป: ลงมือทำใน LAB",
                  '<p>ภาคปฏิบัติ: <a href="../EvoSkill_v2_Slides.html" target="_blank">สไลด์ของบท (LAB)</a> · '
                  '<a href="../README.md#ภาค-lab" target="_blank">README หลัก: ภาค LAB</a> · '
                  'เครื่องมือ: สกิล <a href="../../../00_resource/skills/evoskill/" target="_blank"><code>evoskill</code></a> · '
                  '<a href="../evoskill_format.md" target="_blank">รูปแบบของสกิล (<code>evoskill_format.md</code>)</a></p>'
                  '<p>รายละเอียดเต็มของทฤษฎี: <a href="README.md" target="_blank">01_theory/README.md</a> · เปเปอร์: '
                  '<a href="%s" target="_blank">arXiv:2610.25931</a> · source code: <a href="%s" target="_blank">github.com/sentient-agi/EvoSkill</a></p>'
                  % (PAPER, REPO), "img/s01-cover.jpg"))
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
