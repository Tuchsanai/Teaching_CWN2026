#!/usr/bin/env python3
"""สร้างสไลด์ EvoSkill_v2_Slides.html ของบท (ภาคทฤษฎี + ภาค LAB)

  python tools/build_slides.py            (รันบนเครื่อง จากโฟลเดอร์ของบท)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพ กราฟ หรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง โค้ด ข้อสังเกต และพรอมต์ของ LAB: อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ตัวเลขผลของแต่ละการรัน: อ่านจาก runs/<ชื่อ>/state.json (คะแนนของแต่ละ leg · ตาของ Evolver · Benchmark Adaptor)
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
OUT, TITLE = "EvoSkill_v2_Slides.html", "EvoSkill v2 · Slides"
TH = "01_theory/img/"
THEORY_DECK = "01_theory/EvoSkill_v2_Theory_Slides.html"

# ------------------------------------------------------------------ ผลจริงจาก runs/<ชื่อ>/state.json
RUNS = "e1 e2 v1 n1 n2 f1 f2 f3 p1 p2 h1 h2".split()
ST = {r: json.loads(E.read("runs/%s/state.json" % r)) for r in RUNS}
VAL = ("base_val", "v1_val", "v2_val", "v3_val")


def leg(r, k):
    return ST[r]["legs"][k]


def pc(r, k):
    return "%.1f%%" % (leg(r, k)["score"] * 100)


def ps(r, k="v3_test"):
    return "%d/%d" % (leg(r, k)["passes"], leg(r, k)["n"])


def test(r):
    return pc(r, "v3_test")


def base(r):
    return pc(r, "base_test")


def vals(r):
    return " → ".join(pc(r, k) for k in VAL)


def evo_cost(r):
    return "$%.2f" % sum(t["cost_usd"] for t in ST[r]["turns"])


def evo_secs(r):
    return "%d" % round(sum(t["wall_s"] for t in ST[r]["turns"]))


def solver_cost(r):
    return "$%.2f" % sum(l["cost_usd"] for l in ST[r]["legs"].values())


def rollouts(r):
    return sum(l["n"] for l in ST[r]["legs"].values())


def mean_test(rs):
    return "%.1f%%" % (100 * sum(leg(r, "v3_test")["score"] for r in rs) / len(rs))


def span(rs):
    s = sorted(rs, key=lambda r: leg(r, "v3_test")["score"])
    return test(s[0]), test(s[-1])


SEEN = ["e1", "e2", "v1", "n1", "n2", "f1", "f2", "f3"]     # การรันที่ Evolver (sonnet) ได้เห็นเฉลยของ Training
SPREAD = max(max(leg(r, "v3_test")["score"] for r in g) - min(leg(r, "v3_test")["score"] for r in g)
             for g in (("e1", "e2", "v1"), ("n1", "n2"), ("f1", "f2", "f3"), ("p1", "p2"))) * 100


# ------------------------------------------------------------------ ตัวช่วยอ่าน README.md
def C(s):
    """ข้อความจาก README ที่ใช้ในสไลด์: ไม่มีอีโมจิ"""
    return s.replace("✅ ", "").replace("✅", "").replace("📋 ", "").replace("👀 ", "").replace("⚠️ ", "").strip()


def eyes(prefix):
    """ข้อสังเกต (👀) ทุกข้อของหัวข้อ เรียงตามลำดับใน README · คืนรายการของบรรทัด"""
    return [[b["lines"][0][1:].strip()] + b["lines"][1:] for b in sec(prefix) if b["t"] == "p" and b["lines"][0].startswith("👀")]


def tabh(prefix, col, start):
    """ตารางในหัวข้อ prefix ที่หัวคอลัมน์ลำดับ col ขึ้นต้นด้วย start (ใช้เมื่อหัวคอลัมน์แรกว่างหรือซ้ำกัน)"""
    for b in walk(sec(prefix)):
        if b["t"] == "table" and len(b["head"]) > col and E.plain(b["head"][col]).startswith(start):
            return b
    raise KeyError("ไม่พบตารางที่คอลัมน์ %d ขึ้นต้นด้วย %r ในหัวข้อ %r" % (col, start, prefix))


def row(t, key):
    """แถวแรกของตารางที่คอลัมน์แรกมีข้อความ key"""
    for r in t["rows"]:
        if key in E.plain(r[0]):
            return r
    raise KeyError("ไม่พบแถวที่มี %r ในตารางที่หัวคอลัมน์คือ %r" % (key, t["head"]))


def ncode(prefix, k=0):
    """กล่องโค้ดลำดับ k ของหัวข้อ ไม่นับกล่องพรอมต์"""
    return [b for b in sec(prefix) if b["t"] == "code"][k]["text"]


def parts(text):
    return [x.strip() for x in text.split(" · ")]


def ul(items):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % md(x) for x in items)


def em(text):
    return md(text).replace("<b>", "<em>").replace("</b>", "</em>")


def real(prefix):
    """ข้อความหลัง "ผลจริง" ในย่อหน้า **ผลจริง** ของหัวข้อ prefix (ไม่มีอีโมจิ)"""
    p = para(prefix, "**ผลจริง")["lines"][0]
    return C(re.sub(r"^\*\*ผลจริง:?\*\*:?\s*·?\s*", "", p))


# ------------------------------------------------------------------ ชิ้นส่วนเฉพาะบท
def nfig(key, steps=None, post=""):
    f = FIG[key]
    return explain(f["title"], "img/%s.jpg" % key, steps or f["steps"], post)


def wide(title, src, below, cap="", tag=""):
    """ภาพแนวนอนกว้าง + ชิ้นส่วนด้านล่าง"""
    b = {"t": "img", "src": src, "alt": E.plain(title)}
    return S(title, E.fig_html(b, True) + below + ('<p class="cap">%s</p>' % md(cap) if cap else ""), tag=tag, maxfs=1.15)


def quote(title, big, sub, tag="", post=""):
    """ประโยคหลัก 1 ประโยคตัวใหญ่ + คำอธิบาย"""
    return S(title, '<p class="bigq">%s</p><p class="bigsub">%s</p>%s' % (em(big), md(sub), post), tag=tag, cls="mid", maxfs=1.2)


def figrow(title, srcs, cap):
    imgs = "".join('<div class="fig">%s</div>' % E.img_tag({"t": "img", "src": s, "alt": E.plain(title)}) for s in srcs)
    return S(title, '<div class="figrow">%s</div><p class="cap">%s</p>' % (imgs, md(cap)), maxfs=1.1)


def turn_cards(prefix, vcol=2, extra=None):
    """ตาราง ตา | Evolver ทำอะไร | ... | Validation หลังจากนั้น → การ์ด 3 ใบ"""
    t = table(prefix, "ตา")
    out = []
    for r in t["rows"]:
        text = r[1]
        if extra is not None:
            text = "<p>%s</p><p><b>%s</b>: %s</p>" % (md(r[1]), md(t["head"][extra].replace("ที่ใด", "")), md(r[extra]))
        out.append(((E.plain(r[0]).split(" · ")[0], "Validation " + E.plain(r[vcol])), text))
    return cards(out, 3)


def check(key, items, ref, title, note_text=""):
    vary = ("ตัวเลขของคุณอาจต่างจากของผู้สอน เพราะ AI ไม่ตอบเหมือนกันทุกครั้ง (การตั้งค่าเดียวกันของบทนี้ได้ Test Set ต่างกันได้ถึง %.0f จุด) · "
            "สิ่งที่ต้องมีเหมือนกันคือไฟล์ผล และรูปแบบของ `status`" % SPREAD)
    return E.check_slide(key, items, "ผลของผู้สอน: " + ref, note_text or vary, title)


def sanity():
    """ตัวเลขที่อ่านจาก state.json ต้องตรงกับที่ README เขียน (กันไฟล์ผลกับ README ไม่ตรงกัน)"""
    raw = E.read("README.md")
    for r in RUNS:
        for v in (test(r), pc(r, "v3_val").rstrip("%")):
            assert v in raw, "คะแนน %s ของการรัน %s ไม่อยู่ใน README.md" % (v, r)
        assert rollouts(r) == 78, r
    assert evo_cost("e1") in raw and solver_cost("e1") in raw, "ต้นทุนของการรัน e1 ไม่ตรงกับ README.md"


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    sanity()
    agenda = table("EvoSkill v2 ·", "ภาค")
    t11, t12 = table("1 ·", "ชุดโจทย์"), table("1.1", "")
    labtab = table("3 ·", "LAB")
    labrow = {re.match(r"\[(\d)\]", r[0]).group(1): r for r in labtab["rows"]}
    t41 = table("4.1", "การตั้งค่า")
    SETTING, cur = {}, ""
    for r in t41["rows"]:
        cur = E.plain(r[0]) if r[0].strip() else cur
        SETTING[E.plain(r[1])] = cur
    t42 = table("4.2", "ประเด็น")
    why = "ทำไมได้ต่ำกว่าสองบทก่อน"

    def facts(r):
        return ('<p>%s</p><div class="facts"><div><span class="fl">การรัน</span>%s</div><div><span class="fl">rollout</span>%s</div>'
                '<div><span class="fl">เวลาจริง</span>%s</div><div><span class="fl">ผลจริง</span>%s</div></div>') % (
            md(r[1]), md(r[2]), md(r[3]), md(r[4]), md(r[5]))

    def lab_open(n):
        head = next(s["text"] for s in SECS if s["text"].startswith("LAB %d" % n))
        name = head.split("·", 1)[1].strip()
        CTX.update(kicker="ภาค LAB · " + head, group="LAB %d" % n)
        add(E.divider("LAB %d" % n, name, facts(labrow[str(n)]), small="ภาค LAB · 3 · ลงมือทำ"))
        return "LAB %d · %s" % (n, re.sub(r"\s*\(.*?\)\s*$", "", name))

    def lab_do(n, lt, figkey, items, ref, note_text="", flow_mid=""):
        add(nfig(figkey))
        add(S("%s · ไฟล์เข้าและออก" % lt, E.fileflow(table("LAB %d" % n, "Input"), "LAB %d<small>%s</small>" % (n, flow_mid)), cls="mid"))
        add(E.prompt_slides(prompt("LAB %d" % n), CTX["kicker"], lt))
        add(check("LAB %d" % n, items, ref, lt, note_text))

    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    t = SECS[0]["text"].split("·")
    add(E.cover(t[0].strip(), "·".join(t[1:]).strip(), "img/g01-cover.jpg", small="03_week03 · บทที่ 07"))

    CTX["kicker"] = "ภาพรวมของบท"
    lo, hi = span(SEEN)
    plo, phi = span(["p1", "p2"])
    add(fig("ทั้งเรื่องในภาพเดียว: Evolver ที่เห็นเฉลยได้ %s ถึง %s บน Test Set · เห็นแต่คะแนนได้ %s ถึง %s" % (lo, hi, plo, phi),
            "img/r03-compare.png",
            "ผลจริงจาก 12 การรันของบทนี้ เทียบกับ Skill Optimizer (บท 05) และ WikiSkill (บท 06) บนโจทย์ชุดเดียวกัน · ที่มาของแต่ละแท่งอยู่ในภาค LAB และส่วนที่ 4"))
    alg = table("2.5", "ขั้น")["rows"]
    add(wide("EvoSkill v2 ใน 4 ขั้น: %s" % " → ".join("%s %s" % (E.plain(r[0]), E.plain(r[1])) for r in alg), "img/d00-story.png",
             '<p class="bigsub" style="text-align:center">%s: %s</p>' % (md(alg[2][0]), md(alg[2][2])),
             "ขั้น epoch K ทำซ้ำทุก epoch · ที่มาของแต่ละขั้นอยู่ในภาคทฤษฎี ส่วนที่ 2"))
    pts, cur = [], None
    for r in agenda["rows"]:
        if r[0].strip():
            cur = {"name": E.plain(r[0]), "do": r[3], "secs": []}
            pts.append(cur)
        cur["secs"].append((E.plain(r[1]), r[2]))
    road = "".join('<div class="partbox %s"><div class="ph">%s<small>%s</small></div>%s</div>' % (
        "lab" if "LAB" in p["name"] else "", p["name"], md(p["do"]),
        "".join('<div class="secbox"><b>%s</b><span>%s</span></div>' % (md(a), md(b)) for a, b in p["secs"])) for p in pts)
    add(S("บทนี้แบ่งเป็น 2 ภาค 4 ส่วน", '<div class="road">%s</div>' % road + note(
        "ทฤษฎีจากงานวิจัยต้นทาง อ่านเพิ่มได้ที่ [`01_theory/README.md`](01_theory/README.md) · "
        "รายละเอียดเต็มของทุกหัวข้ออยู่ใน [`README.md`](README.md)", "info"), cls="mid"))
    add(S("วิธีใช้สไลด์นี้", cards([
        ("ไปหน้าถัดไป / ก่อนหน้า", '<p><span class="kbd">→</span> <span class="kbd">Space</span> / <span class="kbd">←</span> หรือปุ่มมุมขวาล่าง</p>'),
        ("สารบัญทุกหน้า", '<p><span class="kbd">O</span> แล้วคลิกหน้าที่ต้องการ · <span class="kbd">F</span> เต็มจอ</p>'),
        ("ขยายภาพ", "คลิกที่ภาพ · คลิกอีกครั้งหรือ Esc เพื่อปิด"),
        ("คัดลอกพรอมต์ของ LAB", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** ให้ข้อความเดียวกับ `README.md` ตรงตัวอักษร แม้พรอมต์ถูกแบ่งแสดง 2 หน้า", "warn"),
        ("ตรวจผลหลังรัน", "สไลด์ **ตรวจผลของคุณ** ต่อจากพรอมต์ทุก LAB · ติ๊กได้ และจำค่าไว้ในเบราว์เซอร์นี้", "warn"),
        ("เปิดไฟล์จริง", "ลิงก์สีน้ำเงินเปิดไฟล์ในโฟลเดอร์ของบท · เปิดสไลด์จากโฟลเดอร์ `07_EvoSkill_v2`"),
    ]), cls="mid"))

    # ===== ภาคทฤษฎี
    CTX.update(kicker="", group="ภาคทฤษฎี")
    alert = next(b for b in sec("ภาคทฤษฎี") if b["t"] == "alert")
    add(E.divider("ภาคทฤษฎี", "โจทย์ (ฉบับย่อ) และ EvoSkill v2", "".join(E.render(x) for x in alert["blocks"]), "img/s01-theory.jpg"))

    # ----- 1 · โจทย์ (ฉบับย่อ)
    CTX.update(kicker="ภาคทฤษฎี · 1 · โจทย์ (ฉบับย่อ)", group="ภาคทฤษฎี · 1 · โจทย์ (ฉบับย่อ)")
    add(E.divider("1", "โจทย์ (ฉบับย่อ)", "<p>โจทย์เดิมของบท 05 และ 06 คืออะไร · บทนี้เปลี่ยนอะไร</p>", small="ภาคทฤษฎี"))
    add(fig("โจทย์เดิมของบท 05: Agent ไม่ได้รับความรู้แฝงของทีม แต่ตัวตรวจรู้ครบ", "../06_WikiSkill/img/d01-problem.png", para("1 ·", "บทนี้ใช้")["lines"][0]))
    add(S("ชุดโจทย์ 9 ข้อ: Training 4 · Validation 2 · Test 3", cards([
        (r[0], "<p>%s</p><p>%s</p>" % (md(r[1]), md(r[2]))) for r in t11["rows"]], 3), tag="โจทย์เดิมของบท 05 และ 06", cls="mid"))
    add(nfig("n02-what-changed", ["**%s**: บท 05 %s · บท 06 %s · บทนี้ **%s**" % (r[0], r[1], r[2], r[3].replace("**", ""))
                                  for r in (t12["rows"][k] for k in (0, 1, 3, 5))]))
    same = para("1.1", "โจทย์ ตัวตรวจ")["lines"][0].split("**เหมือน")
    add(quote("สิ่งที่ไม่เปลี่ยน: โจทย์ ตัวตรวจ และ Solver", "**เหมือน" + same[1], same[0].strip()))
    q = parts(para("1.1", "คำถามใหม่ของบทนี้")["lines"][0])
    add(quote("คำถามใหม่ของบทนี้", q[0].replace("คำถามใหม่ของบทนี้: ", ""), " · ".join(q[1:])))

    # ----- 2 · EvoSkill v2
    CTX.update(kicker="ภาคทฤษฎี · 2 · EvoSkill v2", group="ภาคทฤษฎี · 2 · EvoSkill v2")
    add(E.divider("2", "EvoSkill v2", "<p>EvoSkill v2 คืออะไร · ทำงานอย่างไร · นำมาใช้กับโจทย์นี้อย่างไร</p>", small="ภาคทฤษฎี"))
    add(fig("ข้อสังเกตตั้งต้น: พลาดซ้ำ = ขาดคำแนะนำ ไม่ใช่ขาดความสามารถ", TH + "g01-fail-again.png", para("2.1", "Agent ที่ไม่มีสกิล")["lines"][0]))
    ag = table("2.2", "Agent")
    add(explain("EvoSkill v2 คือ Agent 3 ตัว", TH + "g02-three-agents.png", ["**%s**: %s · %s" % (E.plain(r[0]), r[1], r[2]) for r in ag["rows"]]))
    add(fig("สถาปัตยกรรม: เตรียมครั้งเดียวก่อนการรัน · วนทุก epoch · วัด Test Set หลังการรัน", TH + "t02-architecture.png",
            "ชุดสกิลถัดไปกลับไปที่ **Solver** ทุก epoch · คำอธิบายเต็มของแต่ละกล่อง: [ทฤษฎี](01_theory/README.md)"))
    send = table("2.3", "สิ่งที่ส่ง")
    add(explain("ผู้ใช้ส่ง 3 อย่าง: คำสั่ง ข้อมูล ตัวตรวจ", TH + "t03-adaptor.png",
                [para("2.3", "EvoSkill v2 ไม่มีพรอมต์")["lines"][0]] + ["**%s** %s: %s" % tuple(r) for r in send["rows"]]))
    add(fig("ใครเห็นอะไร: Evolver ไม่เห็น Validation · Test และตัวตรวจ ได้แต่คะแนน", TH + "t05-who-sees.png",
            "อ่านทีละแถว: Benchmark Adaptor · Solver · Evolver · โปรแกรมควบคุมการรัน"))
    add(fig("เครื่องของ Evolver: เห็นอะไร แก้อะไรได้", TH + "t04-evolver-view.png", para("2.4", "การกันข้อมูลทำโดย")["lines"][0]))
    add(fig("อัลกอริทึม: ไม่มีบรรทัด \"ถ้าคะแนนดีขึ้นจึงรับ\"", TH + "t06-algorithm.png",
            "ขั้นของเครื่องมือ: " + " · ".join("%s `%s`" % (E.plain(r[0]), E.plain(r[1])) for r in alg) + " · LAB 1 และ LAB 2 รันคำสั่งเหล่านี้ทีละขั้น"))
    add(fig("การตัดสินใจออกแบบ 4 ข้อของ Evolver", TH + "t07-design-choices.png", para("2.6", "เหตุผลของแต่ละข้อ")["lines"][0]))
    r5 = t12["rows"][5]
    add(explain("ข้อที่ 4 คือจุดที่ต่างจากสองบทก่อนมากที่สุด: ไม่มีประตูรับ", TH + "g08-accept-all.png",
                ["%s · บท 05: %s" % (r5[0], r5[1]), "บท 06: %s" % r5[2], "บทนี้: %s" % r5[3], "epoch K: %s" % alg[2][2]]))
    paper = table("2.7", "ประเด็น")
    pick = [row(paper, k) for k in ("ขนาดของการรัน", "Solver", "Evolver และ", "การแยกเครื่อง", "ความรู้แฝงเฉพาะงาน")]
    add(S("นำมาใช้กับโจทย์นี้: เหมือนเปเปอร์ทุกขั้น ต่างที่ขนาดงานและวิธีแยกเครื่อง", cards([
        (r[0], "<p><b>เปเปอร์</b>: %s</p><p><b>บทนี้</b>: %s</p>" % (md(r[1]), md(r[2])), "warn" if "ความรู้แฝง" in r[0] else "") for r in pick], 3) +
        note(para("2.7", "เครื่องมือของบทนี้")["lines"][0] + " · แถวอื่นของตารางอยู่ใน [`README.md`](README.md) ข้อ 2.7", "info"), tag="ข้อ 2.7", maxfs=1.2))
    add(S("คำถาม 7 ข้อที่ภาค LAB จะตอบ", cards([((r[0], "LAB " + r[2]), r[1]) for r in table("2.8", "#")["rows"]], 4), cls="mid"))

    # ===== ภาค LAB
    CTX.update(kicker="", group="ภาค LAB")
    alert = next(b for b in sec("ภาค LAB") if b["t"] == "alert")
    add(E.divider("ภาค LAB", "ลงมือทำ %d ขั้น · สรุป · แบบฝึกหัด" % len(labtab["rows"]), "".join(E.render(x) for x in alert["blocks"]), "img/s02-lab.jpg"))
    CTX.update(kicker="ภาค LAB · 3 · ลงมือทำ", group="ภาค LAB · 3 · ลงมือทำ")
    add(fig("ภาค LAB: ลงมือทำ %d ขั้น" % len(labtab["rows"]), "img/d03-lab-map.png",
            "LAB 0 สร้างเครื่องมือ · LAB 1 เตรียมสนาม · LAB 2 รันจนจบ · LAB 3–6 เปลี่ยนทีละอย่าง · LAB 7 ความแกว่ง (ไม่ใช้โทเคน)"))
    add(nfig("n00-how-to-lab"))
    use = para("3 ·", "**วิธีใช้:**")["lines"]
    tip = next(b for b in walk(sec("ภาค LAB")) if b["t"] == "p" and b["lines"][0].startswith("ผลจริงทุกตัว"))["lines"][0]
    add(S("ก่อนเริ่ม LAB", cards([
        ("วิธีใช้", C(use[0].replace("**วิธีใช้:**", "")), "warn"),
        ("ต้องมี", use[1].replace("**ต้องมี:**", "").strip(), "warn"),
        ("ผลจริงในสไลด์", tip, "navy")], 3) + note(
        "ทุก LAB มีลำดับเดียวกัน: ภาพขั้นตอน → ไฟล์เข้าและออก → พรอมต์ (คัดลอก) → ตรวจผลของคุณ → ผลจริงของผู้สอน → กราฟ → จุดสำคัญ", label="ลำดับ"), cls="mid"))
    plan = table("แผนการทดลอง", "หัวข้อ")
    add(S("ข้อมูล 9 ข้อ แบ่งเป็น 3 ชุด: Evolver เห็นเฉพาะ Training", cards([
        (E.plain(r[0]), r[1], tone) for r, tone in zip((row(plan, k) for k in ("Training", "Validation", "Test")), ("ok", "warn", "bad"))], 3) +
        note(row(plan, "Input")[0].replace("**", "") + ": " + row(plan, "Input")[1], "info"), tag="แผนการทดลอง", cls="mid", maxfs=1.2))
    add(S("1 การรัน = 78 rollout: นับอย่างไร และใช้โมเดลใด", cards([
        (E.plain(r[0]), r[1]) for r in (row(plan, k) for k in ("1 rollout", "การให้คะแนน", "1 การรัน", "โมเดล"))], 2), tag="แผนการทดลอง", cls="mid", maxfs=1.2))
    add(code("โครงสร้างโฟลเดอร์: 1 การรัน = 1 โฟลเดอร์ใน runs/", codes("โครงสร้างโฟลเดอร์")[0]["text"],
             post=note(" · ".join("%s: %s" % (r[0], r[1]) for r in table("โครงสร้างโฟลเดอร์", "ที่")["rows"]), label="ที่ทำงาน")))

    # ----- LAB 0
    r00 = lab_open(0)
    ft = table("ขั้น 0.1", "ไฟล์ที่ได้ใน")
    tst = table("ขั้น 0.1", "ทดสอบ")
    ntest = sum(1 for r in tst["rows"] if "✅" in r[1])
    nlines = row(ft, "evoskill.py")[1]
    real01 = real("ขั้น 0.1")
    t01 = "ขั้น 0.1 · สร้างสกิล `evoskill`"
    CTX["kicker"] = "ภาค LAB · LAB 0 · ขั้น 0.1"
    add(nfig("n03-lab0-steps"))
    add(fig("ขั้น 0.1 · สร้างสกิล `evoskill` ใน 6 ขั้น", "img/d02-build-skill.png",
            "ทำบนเครื่อง ไม่ใช้ container · ที่มา: เปเปอร์ EvoSkill v2 · รูปแบบ: [`evoskill_format.md`](evoskill_format.md)"))
    add(E.prompt_slides(prompt("ขั้น 0.1"), CTX["kicker"], t01))
    ctests = [C(r[0]) + ": " + C(r[1]) for r in tst["rows"] if "✅" in r[1]]
    add(check("ขั้น 0.1", [
        "มีโฟลเดอร์ `my-evoskill/` และมีไฟล์ครบ: " + " · ".join("`%s`" % E.plain(r[0]) for r in ft["rows"]),
        "`scripts/evoskill.py` มีครบ 12 คำสั่ง: `init` `adapt` `audit` `base` `turn` `rollout` `test` `run` `status` `noise` `eval` `export`",
        "`references/source.md` มีตาราง ส่วนของสกิล | มาจากข้อไหนของเปเปอร์ | เหมือนหรือต่าง",
        "ทดสอบ (ก): `status` และ `noise` ของการรันที่เก็บไว้ พิมพ์ตรงกับ `status.txt` และ `noise.txt`",
        "ทดสอบ (ข): การรันจำลอง 2 epochs จนจบ `test`: `skills_v1` และ `skills_v2` ถูกเก็บทั้งคู่ · Test ใช้ `skills_v2` · ใน `evo/` ไม่มีสิ่งใดของ Validation และ Test",
        "ทดสอบ (ค): Adaptor จำลองคัดลอกโจทย์ของ Validation ลง `reference/` → หยุดที่ `adapt` · แก้ `setup/tasks.json` หลังล็อก → คำสั่งถัดไปหยุด",
        "รายงานเป็นตาราง ไฟล์ | หน้าที่ และผลทดสอบ 3 ข้อ"],
        "%s · ได้ %d ไฟล์ (`scripts/evoskill.py` %s บรรทัด) · ทดสอบผ่าน %d ข้อ" % (real01, len(ft["rows"]), nlines, ntest), t01,
        "เครื่องมือที่สร้างเองไม่ต้องเหมือนใครทุกบรรทัด สิ่งที่ต้องตรงคือ **รูปแบบ** ใน `evoskill_format.md` · การแยกเครื่องด้วย `unshare` และการเรียกโมเดลจริงยังไม่ได้ทดสอบในขั้นนี้ (รู้ผลใน LAB 1)"))
    add(S("ผลจริงขั้น 0.1: ได้เครื่องมือ %d ไฟล์" % len(ft["rows"]),
          cards([(r[0], "**%s บรรทัด** · %s" % (r[1], r[2])) for r in ft["rows"]], 3), tag="ผลของผู้สอน · " + real01.split(" · ")[0], maxfs=1.15))
    add(S("ผลจริงขั้น 0.1: ทดสอบ 3 ข้อโดยไม่เรียกโมเดล", cards(
        [(C(r[0]), C(r[1]), "warn" if "⚠️" in r[1] else "ok") for r in tst["rows"]], 2), tag="ผลของผู้สอน", maxfs=1.2))
    e01 = " ".join(eyes("ขั้น 0.1")[0])
    p01 = parts(e01)
    add(S("การรันจริงครั้งแรกสอนอะไร: เครื่องวัดต้องแยก \"Solver ทำผิด\" ออกจาก \"Solver ไม่ได้ทำ\"", cards([
        ("เหตุการณ์", p01[0].replace("**สิ่งที่การรันจริงครั้งแรกสอน:**", "").strip(), "bad"),
        ("สิ่งที่แก้", p01[1], "ok")], 2) + note(p01[2], "info"), tag="ผลของผู้สอน", cls="mid", maxfs=1.2))
    t02 = "ขั้น 0.2 · ติดตั้งเครื่องมือ และตรวจตัวตรวจ"
    CTX["kicker"] = "ภาค LAB · LAB 0 · ขั้น 0.2"
    add(S("ขั้น 0.2 · ไฟล์เข้าและออก", E.fileflow(table("ขั้น 0.2", "Input"), "ขั้น 0.2<small>ยังไม่วัดอะไร</small>",
                                                 out_label="OUTPUT · สิ่งที่ได้ใน container"), cls="mid"))
    add(E.prompt_slides(prompt("ขั้น 0.2"), CTX["kicker"], t02))
    real02 = real("ขั้น 0.2")
    add(check("ขั้น 0.2", [
        "รายงานเป็นตาราง รายการ | ผล",
        "`my-evoskill` ถูกติดตั้งเป็น global skill ชื่อ `evoskill` ของบัญชี yolo (อยู่ข้างสกิล `skill-optimizer` ของบท 05)",
        "ใน container มี `/workspace/evlab/bench/`",
        "`bench/check_grader.py` ผ่าน: เฉลยอ้างอิงผ่านครบ และเฉลยที่จงใจใส่ความผิดไม่ผ่านเฉพาะข้อนั้น",
        "มีบัญชี `yolo` ที่ล็อกอินแล้วอย่างน้อย 1 บัญชี"], real02, t02,
        "ตรวจตัวตรวจก่อนเสมอ ถ้าเครื่องวัดผิด ตัวเลขหลังจากนี้ใช้ไม่ได้ทั้งหมด"))
    add(fig("ทำไมต้องตรวจตัวตรวจก่อน: คะแนนสูงขึ้น ไม่ได้แปลว่าสกิลดีขึ้น", TH + "g04-grader-exploit.png", C(" ".join(eyes("ขั้น 0.2")[0]))))

    # ----- LAB 1
    A = ST["e1"]["adapt"]
    r1 = table("LAB 1", "รายการ")["rows"]
    lt = lab_open(1)
    add(fig("Benchmark Adaptor เตรียมสนามก่อนเริ่ม: ล็อกโจทย์และตัวตรวจ ก่อนมีสกิลตัวแรก", TH + "g09-adaptor.png", " ".join(eyes("LAB 1")[0])))
    lab_do(1, lt, "n04-lab1-steps", [
        "มีการรันชื่อ `e1` และรันเฉพาะขั้น `adapt` (ยังไม่มี rollout)",
        "`setup/` มี `benchmark_plugin.py` · `freeze.json` · `audit.md` · `reference/` มีเฉพาะของชุด Training",
        "`audit.md` ไม่พบของ Validation หรือ Test และไม่พบโค้ดของตัวตรวจ",
        "เปิดดู `turns/adaptor/message.md` และ `actions.md` แล้ว",
        "รายงานเป็นตาราง รายการ | ผล (เวลา เครื่องมือ ค่าใช้จ่าย · จำนวนโจทย์แต่ละชุด · ไฟล์ใน reference · ผลตรวจการรั่ว)",
        "รายงานบอกสิ่งที่ Adaptor ทำเองโดยไม่ได้สั่ง"], real("LAB 1"), flow_mid="Benchmark Adaptor · ขั้น adapt")
    e1 = eyes("LAB 1")
    add(S("ผลจริง LAB 1: สนามถูกล็อกใน %d วินาที ก่อนที่ Evolver จะเริ่มทำงาน" % round(A["wall_s"]), tiles([
        ("Benchmark Adaptor", "%d วินาที" % round(A["wall_s"]), "เครื่องมือ %d ครั้ง · $%.2f" % (A["tool_calls"], A["cost_usd"]), ""),
        ("โจทย์ที่ล็อกแล้ว", "%d ข้อ" % sum(A["tasks"].values()), "train %(train)d · validation %(validation)d · test %(test)d" % A["tasks"], ""),
        ("`reference/`", "%d ไฟล์" % A["reference"]["files"], "เฉลยอ้างอิงของ Training %d ไฟล์" % A["reference"]["answers"], "warn"),
        ("ตรวจการรั่ว", "ไม่พบ" if not A["reference"]["leaks"] else "พบ", "ของ Validation หรือ Test · โค้ดของตัวตรวจ", "ok")]) +
        note(" ".join(e1[0])), tag="runs/e1/state.json", cls="mid"))
    own = parts(row(table("LAB 1", "รายการ"), "ทำเอง")[1])
    add(S("สิ่งที่ Adaptor ทำเองโดยไม่ได้สั่ง: กันชื่อโจทย์ของ Validation และ Test ไม่ให้รั่ว",
          cards([((k + 1, "ทำเอง"), x, "ok") for k, x in enumerate(own)], 3) +
          note("เปิดดูได้ที่ [`runs/e1/setup/`](runs/e1/setup/) · [`runs/e1/reference/`](runs/e1/reference/)", "info"),
          tag="turns/adaptor/actions.md", cls="mid"))
    k1 = parts(" ".join(e1[1]))
    add(quote("เฉลยอ้างอิงใน Reference Folder มีนโยบายธุรกิจที่โจทย์ไม่ได้เขียน", k1[0], k1[1]))

    # ----- LAB 2
    lt = lab_open(2)
    lab_do(2, lt, "n05-lab2-steps", [
        "ขั้น `base` → `turn` → `rollout` ของ epoch 1 ถูกรันทีละขั้น และรายงานบอกไฟล์ที่เกิดหลังแต่ละขั้น",
        "มี `turns/turn_1/actions.md` และ `skills_v1/` · รายงานสรุปว่า Evolver ทำอะไร และเขียนสกิลอะไร",
        "การรันจบแล้ว: มี `skills_v1/` `skills_v2/` `skills_v3/` และ `turns/turn_1` ถึง `turn_3`",
        "`export` แล้วโฟลเดอร์ `e1` ถูกคัดลอกมาแทน `runs/e1` · มี `status.txt` และ `noise.txt` ในโฟลเดอร์นั้น",
        "รายงานมีตาราง ขั้น | ไฟล์ที่เกิด | สรุป 1 บรรทัด · สรุป 3 ตาของ Evolver · ตาราง status · ข้อตรวจที่ไม่ผ่านใน Test Set"],
        real("LAB 2"), flow_mid="base → turn → rollout · 78 rollout")
    T = ST["e1"]["turns"]
    add(S("ผลจริง LAB 2: Test Set จาก %s เป็น %s ด้วย Evolver 3 ตา" % (base("e1"), test("e1")), tiles([
        ("Test Set · ไม่มีสกิล", base("e1"), "ผ่านครบทุกข้อ %s" % ps("e1", "base_test"), ""),
        ("Test Set · `skills_v3`", test("e1"), "ผ่านครบทุกข้อ %s" % ps("e1"), "ok"),
        ("Validation หลัง epoch 3", pc("e1", "v3_val"), vals("e1"), ""),
        ("Evolver 3 ตา", evo_cost("e1"), "%s วินาที · Bash %d ครั้ง" % (evo_secs("e1"), sum(x["bash"] for x in T)), "warn"),
        ("rollout ของ Solver", "%d" % rollouts("e1"), solver_cost("e1"), "")]) +
        note("ชุดสกิลของ epoch 1: `%s` %.1f KB · ไฟล์ผล: [status](runs/e1/status.txt) · [noise](runs/e1/noise.txt) · [`runs/e1/`](runs/e1/)" % (
            "` + `".join(sorted(T[0]["skills"], reverse=True)), T[0]["skill_md_bytes"] / 1024), "info"),
        tag="runs/e1/state.json", cls="mid"))
    add(fig("เส้นทางของ `e1`: ขึ้นใน epoch 1 แล้วขยับเล็กน้อย ทั้ง Training และ Validation", "img/r01-path-e1.png",
            "เส้นประ = Training (Evolver เห็น) · เส้นทึบ = Validation (Evolver ไม่เห็น) · ไม่มี rollout ใดผ่านครบทุกข้อ"))
    add(fig("Evolver ทำอะไรในแต่ละตา: อ่านเฉลย → ทดสอบแล้วเดา → ทดลองแก้", TH + "t15-evolver-turns.png",
            "บันทึกของแต่ละตา: " + " · ".join(r[3] for r in table("LAB 2", "ตา")["rows"])))
    st3 = [b["lines"][0] for b in sec("LAB 2") if b["t"] == "p" and b["lines"][0].startswith("**เรื่องที่")]
    add(S("ผลของ e1 มี 3 เรื่องที่ควรอ่านแยกกัน", cards([
        ((k + 1, "เรื่องที่ %d" % (k + 1)), x.strip("*").split("·", 1)[1].strip(), tone)
        for k, (x, tone) in enumerate(zip(st3, ("ok", "bad", "warn")))], 3), tag="การรัน e1", cls="mid"))
    # เรื่องที่ 1
    bl = sec("LAB 2")
    s1 = next(bl[k + 1]["lines"][0] for k, b in enumerate(bl) if b["t"] == "p" and b["lines"][0].startswith("**เรื่องที่ 1"))
    t6 = tabh("LAB 6", 2, "haiku")
    pol = re.search(r"`policy` ผ่าน (\d+/\d+)", row(t6, "นโยบายธุรกิจ")[1]).group(1)
    wpol = re.search(r"`policy` (\d+/\d+)", s1).group(1)
    add(S("เรื่องที่ 1 · " + st3[0].strip("*").split("·", 1)[1].strip(), versus(
        "ข้อตรวจ policy ของ Training (งานค่าส่งและงานเงินคืน)",
        ("บท 06 · WikiSkill", "ไม่มีใครได้เห็นเฉลย", wpol, "หานโยบายธุรกิจเองไม่ได้"),
        ("บทนี้ · EvoSkill v2 (e1)", "Evolver อ่านเฉลยของงานค่าส่งและงานเงินคืน", pol, "ผ่านครบตั้งแต่ epoch 1")) +
        note(s1, "info"), tag="runs/e1/skills_v3", cls="mid"))
    # เรื่องที่ 2
    add(nfig("n06-too-broad"))
    rep = tabh("LAB 2", 3, "v1")
    x2 = row(rep, "x2-refund")
    add(code("เรื่องที่ 2 · หลักฐาน: สกิลเขียนกว้าง · `x2-refund` ผิดทั้ง 3 rollout", ncode("LAB 2"),
             post=note("`x2-refund` ใน Test Set: " + " · ".join("%s %s" % (h, c) for h, c in zip(rep["head"][1:], x2[1:])) +
                       " · ไม่มีประตูรับ และ Validation 2 โจทย์ไม่มีงานแบบนี้")))
    # เรื่องที่ 3
    g3 = tabh("LAB 2", 1, "สิ่งที่ตัวตรวจพบ")
    steps = ["epoch %s · ตัวตรวจพบ %s · Evolver เห็น %s → %s" % (r[0], r[1], r[2], r[3]) if r[2].strip() != "–"
             else "epoch %s · ตัวตรวจพบ %s → %s" % (r[0], r[1], r[3]) for r in g3["rows"]]
    add(nfig("n07-blind-guess", steps))
    add(tbl("เรื่องที่ 3 · " + st3[2].strip("*").split("·", 1)[1].strip(), g3,
            post=note(para("LAB 2", "Solver ส่งไฟล์เทสต์")["lines"][0])))
    # รันซ้ำ
    guess, tstr = row(rep, "การเดา"), row(rep, "ข้อ tests")
    best = max(("e1", "e2", "v1"), key=lambda r: leg(r, "v3_test")["score"])
    add(S("รันซ้ำด้วยการตั้งค่าเดิม 3 ครั้ง: Test Set %s · %s · %s เท่ากัน แต่เดินคนละเส้นทาง" % (test("e1"), test("e2"), test("v1")),
          cards([("`%s` · Test Set %s (%s)" % (r, test(r), ps(r)),
                  ul(["**เดาเรื่อง 0.1 ที่ขาด**: " + guess[k + 1], "**ข้อ `tests` ใน Test Set**: " + tstr[k + 1], "**`x2-refund`**: " + x2[k + 1]]),
                  "ok" if r == best else "warn") for k, r in enumerate(("e1", "e2", "v1"))], 3),
          tag="e1 · e2 · v1", maxfs=1.2))
    ey = " ".join(eyes("LAB 2")[1])
    ep = ey.split(" · ", 1)
    add(quote("การตั้งค่าเดียวกัน เส้นทางต่างกัน แต่ติดเพดานเดียวกัน", ep[0], ep[1]))

    # ----- LAB 3
    lt = lab_open(3)
    p3 = [b["lines"][0] for b in sec("LAB 3") if b["t"] == "p"]
    add(code("สิ่งเดียวที่เปลี่ยน: คำสั่งของผู้ใช้ให้ Reference Folder มี `README.md` เพิ่ม 1 ประโยค", ncode("LAB 3"),
             pre="<p>%s</p><p>%s</p>" % (md(p3[0]), md(p3[1])), maxfs=1.2))
    lab_do(3, lt, "n08-lab3-steps", [
        "มีการรัน `n1` ที่ใช้ `bench/instruction_with_note.md` และรันจนจบ (วัด Test Set แล้ว)",
        "`reference/README.md` มีข้อความ 1 ประโยค: ผลงานที่ได้คะแนนเต็มประกอบด้วย `solve.py` และ `test_solve.py`",
        "`export` แล้วโฟลเดอร์ `n1` ถูกคัดลอกมาแทน `runs/n1`",
        "รายงานมีเนื้อหาของ `reference/README.md` และตาราง status ของ `n1` เทียบ `e1`",
        "รายงานสรุป 3 ตาของ Evolver: ทำอะไร · ข้อสรุป · คะแนน Validation หลังจากนั้น · ข้อตรวจที่ไม่ผ่านใน Test Set"],
        real("LAB 3"), flow_mid="การรันใหม่ n1 · 78 rollout")
    e3 = eyes("LAB 3")
    add(S("ผลจริง LAB 3: เพิ่ม 1 ประโยค Test Set เป็น %s ทั้งสองการรัน" % test("n1"), tiles([
        ("`e1` · ไม่มีหมายเหตุ", test("e1"), "ผ่านครบทุกข้อ %s" % ps("e1"), ""),
        ("`n1` · เพิ่ม 1 ประโยค", test("n1"), "ผ่านครบทุกข้อ %s" % ps("n1"), "ok"),
        ("`n2` · รันซ้ำ", test("n2"), "ผ่านครบทุกข้อ %s" % ps("n2"), "ok"),
        ("ต้นทุนของ Evolver", evo_cost("n1"), "`e1` %s · `n2` %s" % (evo_cost("e1"), evo_cost("n2")), "warn")]) +
        note(" ".join(e3[0])), tag="runs/n1 · runs/n2", cls="mid"))
    add(fig("เส้นทางของ `n1`: Training เต็มตั้งแต่ epoch 1 · Validation ค่อย ๆ ขึ้น", "img/r01-path-n1.png",
            "สกิลให้ Solver ส่ง `test_solve.py` หรือไม่ · `e1`: %s · `n1`: %s" % (
                row(tabh("LAB 3", 2, "n1"), "สกิลให้ Solver")[1], row(tabh("LAB 3", 2, "n1"), "สกิลให้ Solver")[2])))
    add(S("`n1` ทีละตา: ให้ส่งไฟล์เทสต์ตั้งแต่ตาแรก แล้วตาที่ 2–3 ไม่แก้อะไร", turn_cards("LAB 3"), tag="runs/n1/turns", maxfs=1.2))
    v3 = " ".join(e3[1])
    v3p = parts(v3)
    add(quote("Validation ที่ขยับ ไม่ได้มาจากการแก้สกิล", v3p[1], v3p[0]))
    c3 = " ".join(e3[2])
    add(quote("เพดานของทุกการรันที่เห็นเฉลย", c3.split(":**")[0].strip("*"), c3.split(":**")[1].strip()))
    l3 = parts(para("LAB 3", "บทเรียน:")["lines"][0])
    add(quote("บทเรียนของ LAB 3", l3[0].replace("บทเรียน: ใน EvoSkill v2 ", ""), l3[1]))

    # ----- LAB 4
    lt = lab_open(4)
    t4p = tabh("LAB 4", 2, "p1")
    lab_do(4, lt, "n09-lab4-steps", [
        "มีการรัน `p1` ที่ใช้ `bench/instruction_score_only.md` และรันจนจบ",
        "`reference/` มีเฉพาะโจทย์ของ Training (ไม่มีเฉลยของชุดใดเลย)",
        "`export` แล้วโฟลเดอร์ `p1` ถูกคัดลอกมาแทน `runs/p1`",
        "รายงานมีรายการไฟล์ใน `reference/` · ตาราง status ของ `p1` เทียบ `e1` · สรุป 3 ตาของ Evolver",
        "รายงานแสดงเนื้อหาของ `evo/evolver_workspace/` (บันทึกที่ Evolver เขียนให้ตัวเอง) และข้อตรวจที่ไม่ผ่านใน Test Set"],
        real("LAB 4"), flow_mid="การรันใหม่ p1 · 78 rollout")
    add(S("ผลจริง LAB 4: ไม่มีเฉลย Test Set เหลือ %s และ %s" % (test("p1"), test("p2")), tiles([
        ("`e1` · เห็นเฉลย", test("e1"), "`reference/` %d ไฟล์" % ST["e1"]["adapt"]["reference"]["files"], ""),
        ("`p1` · เห็นแต่คะแนน", test("p1"), "`reference/` %d ไฟล์ (ไม่มีเฉลย)" % ST["p1"]["adapt"]["reference"]["files"], "bad"),
        ("`p2` · รันซ้ำ", test("p2"), "ผ่านครบทุกข้อ %s" % ps("p2"), "bad"),
        ("Validation `p1` หลัง epoch 1", pc("p1", "v1_val"), "ต่ำกว่าไม่มีสกิล %s" % pc("p1", "base_val"), "bad")]) +
        note("สิ่งที่ไม่เคยค้นพบ · `e1`: %s · `p1`: %s" % (row(t4p, "ไม่เคยค้นพบ")[1], row(t4p, "ไม่เคยค้นพบ")[2])), tag="runs/p1 · runs/p2", cls="mid"))
    add(fig("เส้นทางของ `p1`: Validation ตกใน epoch 1 แล้วขึ้นทีละ epoch", "img/r01-path-p1.png", para("LAB 4", "การตั้งค่าที่สองของเปเปอร์")["lines"][0]))
    add(S("ไม่มีเฉลยให้เทียบ: Evolver ใช้คะแนนของ epoch ถัดไปเป็นคำตอบ", turn_cards("LAB 4", vcol=2), tag="runs/p1/turns", maxfs=1.2))
    add(code("บันทึกที่ Evolver เขียนให้ตัวเอง: แต่ละ epoch คือการทดลอง 1 ครั้ง", ncode("LAB 4"),
             pre="<p>%s</p>" % md(para("LAB 4", "บันทึกที่ Evolver")["lines"][0]),
             post=note("ชุดสกิลสุดท้ายของ `p1` คือการทดลองของ epoch 3 ที่ยังไม่มีใครตรวจ และถูกนำไปวัด Test Set ทันที"), maxfs=1.2))
    obs = next(b for b in sec("LAB 4") if b["t"] == "ul")["items"]
    obs = [re.match(r"\*\*(.+?):?\*\*\s*(.*)$", x).groups() for x in obs]
    add(S("3 เรื่องที่เห็นจากการรันที่มีแต่คะแนน", cards([((k + 1, a), b, "warn") for k, (a, b) in enumerate(obs)], 3), cls="mid"))
    pp = parts(para("LAB 4", "**ผู้สอนรันซ้ำ (`p2`):**")["lines"][0])
    add(S("รันซ้ำ `p2`: Evolver ทดลองวิธีปัดเศษต่างกันตามชนิดงาน ได้ %s" % test("p2"), tiles(
        [("Validation · %s" % ("ไม่มีสกิล" if k == 0 else "epoch %d" % k), pc("p2", v), "", "") for k, v in enumerate(VAL)] +
        [("Test Set", test("p2"), "ผ่านครบทุกข้อ %s" % ps("p2"), "bad")]) + note(" · ".join(pp[2:]), "info"), tag="runs/p2", cls="mid"))

    # ----- LAB 5
    lt = lab_open(5)
    add(fig("เซสชันเดียวตลอดการรัน: สิ่งที่ LAB นี้ตัดออกคือความจำของ Evolver", TH + "g06-stateful.png",
            para("LAB 5", "เปเปอร์ให้เหตุผล")["lines"][0]))
    lab_do(5, lt, "n10-lab5-steps", [
        "มีการรัน `f1` ที่เพิ่ม `--fresh-session` และรันจนจบ",
        "`export` แล้วโฟลเดอร์ `f1` ถูกคัดลอกมาแทน `runs/f1`",
        "รายงานมีตาราง status ของ `f1` เทียบ `e1`",
        "รายงานสรุป 3 ตาของ Evolver รวมทั้งตานั้นรู้เรื่องของตาก่อนจากที่ใด",
        "รายงานแสดงไฟล์ใน `evo/evolver_workspace/` และข้อตรวจที่ไม่ผ่านใน Test Set"],
        real("LAB 5"), flow_mid="การรันใหม่ f1 · 78 rollout")
    e5 = eyes("LAB 5")
    one, fresh = ("e1", "e2", "v1"), ("f1", "f2", "f3")
    add(S("ผลจริง LAB 5: ไม่พบว่าเซสชันเดียวดีกว่า · Test Set เฉลี่ย %s และ %s" % (mean_test(one), mean_test(fresh)), bars(
        [("`%s` · %s" % (r, "เซสชันเดียว" if r in one else "เซสชันใหม่ทุก epoch"), "", leg(r, "v3_test")["score"], 1,
          "%s · %s" % (test(r), ps(r))) for r in one + fresh]) + note(e5[0][0]), tag="Test Set · 6 การรัน"))
    add(fig("เส้นทางของ `f1`: รูปร่างเดียวกับ `e1`", "img/r01-path-f1.png",
            "Validation ของ `f1`: %s · ของ `e1`: %s" % (vals("f1"), vals("e1"))))
    add(S("`f1` ทีละตา: เซสชันใหม่ยังส่งต่อความรู้ผ่านไฟล์โน้ตได้", turn_cards("LAB 5", vcol=3, extra=2), tag="runs/f1/turns", maxfs=1.2))
    add(quote("สิ่งที่ชี้ขาดไม่ใช่ความจำของเซสชัน", e5[0][1].split(":")[0], e5[0][1].split(":", 1)[1].strip(),
              post=note(" ".join(e5[1]), "warn")))

    # ----- LAB 6
    lt = lab_open(6)
    lab_do(6, lt, "n11-lab6-steps", [
        "มีการรัน `h1` ที่เพิ่ม `--solver-model haiku --evolver-model haiku` และรันจนจบ",
        "`export` แล้วโฟลเดอร์ `h1` ถูกคัดลอกมาแทน `runs/h1`",
        "รายงานมีตาราง status ของ `h1` เทียบ `e1`",
        "รายงานมีชื่อและ description ของสกิลใน `skills_v3` และไฟล์ใน `evo/evolver_workspace/`",
        "รายงานมีต้นทุนรวมของ Evolver 3 ตา และของ Solver · ข้อตรวจที่ไม่ผ่านใน Test Set"],
        real("LAB 6"), flow_mid="การรันใหม่ h1 · 78 rollout")
    e6 = eyes("LAB 6")
    add(S("ผลจริง LAB 6: haiku ปรับสกิลของตัวเองได้ %s แต่รันซ้ำได้ %s" % (test("h1"), test("h2")), tiles([
        ("`h1` · haiku ทั้งคู่", test("h1"), "จาก %s · ผ่านครบทุกข้อ %s" % (base("h1"), ps("h1")), "ok"),
        ("`e1` · sonnet ทั้งคู่", test("e1"), "จาก %s · ผ่านครบทุกข้อ %s" % (base("e1"), ps("e1")), ""),
        ("ต้นทุนของ Evolver 3 ตา", evo_cost("h1"), "`e1` %s" % evo_cost("e1"), "warn"),
        ("ต้นทุนของ Solver %d rollout" % rollouts("h1"), solver_cost("h1"), "`e1` %s" % solver_cost("e1"), "warn"),
        ("`h2` · รันซ้ำ", test("h2"), "จาก %s · ผ่านครบทุกข้อ %s" % (base("h2"), ps("h2")), "bad")]) +
        note(parts(" ".join(e6[0]))[0]), tag="runs/h1 · runs/h2", cls="mid"))
    add(fig("เส้นทางของ `h1`: haiku ขึ้นใน epoch 1 แล้วตกลงเล็กน้อย", "img/r01-path-h1.png", para("LAB 6", "เปเปอร์รายงานว่า")["lines"][0]))
    pr, cli = row(t6, "นโยบายธุรกิจ"), row(t6, "รันเป็นโปรแกรม")
    add(S("จุดที่ต่าง: haiku พบนโยบายธุรกิจ แต่ไม่ได้เขียนลงสกิล · และไม่พบโหมดรันเป็นโปรแกรม", cards([
        (t6["head"][1], ul(["**%s**: %s" % (pr[0], pr[1]), "**%s**: %s" % (cli[0], cli[1])])),
        (t6["head"][2], ul(["**%s**: %s" % (pr[0], pr[2]), "**%s**: %s" % (cli[0], cli[2])]), "warn")], 2) +
        note(" ".join(e6[1])), tag="runs/h1/evo/evolver_workspace", maxfs=1.2))
    h2 = parts(para("LAB 6", "**ผู้สอนรันซ้ำ (`h2`):**")["lines"][0])
    add(S("รันซ้ำ `h2` ได้ Test Set %s: เส้นทางคล้าย `h1` แต่ต่างที่ไฟล์เทสต์" % test("h2"), cards([
        ("เหมือน `h1`", ul(h2[4:7]), "warn"),
        ("ต่างจาก `h1`", h2[7], "ok")], 2) + note(" · ".join(h2[1:4]), "info"), tag="runs/h2", cls="mid", maxfs=1.2))

    # ----- LAB 7
    lt = lab_open(7)
    add(fig("ทำครั้งเดียว แยกไม่ออกว่าพลาดจริงหรือบังเอิญ", TH + "g07-three-attempts.png", para("LAB 7", "LAB นี้ไม่ใช้โทเคน")["lines"][0]))
    gt = tabh("LAB 7", 1, "เทียบบน")
    ge = [r for r in gt["rows"] if E.plain(r[0]) == "n1"]
    lab_do(7, lt, "n12-lab7-steps", [
        "`noise` ของการรัน `e1` `n1` `p1` `f1` `h1` ถูกรัน และบันทึกที่ `runs/<ชื่อ>/noise.txt`",
        "ไม่มี rollout หรือ Agent ใหม่ถูกรัน",
        "คำตอบข้อ 1: leg ที่มีโจทย์ผ่านบางครั้ง หรือคะแนนต่างกันระหว่างครั้ง",
        "คำตอบข้อ 2: การเทียบที่ช่อง \"รับ\" ไม่ใช่ 0/9 หรือ 9/9 · ชุดสกิลที่ประตูรับนั้นจะทิ้ง และคะแนน Test ของชุดนั้น (ดู `status` ของการรันนั้น)"],
        "ใช้ 2 วินาที · " + " · ".join("`n1` %s รับ %s" % (r[1], E.plain(r[3])) for r in ge) + " · `p1` ไม่มีสกิล → v1 ต่ำกว่าทั้ง 9 คู่",
        "LAB นี้อ่านผลที่มีอยู่ ถ้าใช้ไฟล์ผลของผู้สอน ตัวเลขต้องตรงกันทุกตัว", flow_mid="noise · ไม่ใช้โทเคน")
    nt = tabh("LAB 7", 1, "โจทย์")
    add(S("Solver ทำโจทย์เดิมซ้ำด้วยชุดสกิลเดิม คะแนนไม่เท่ากัน", cards([
        (r[0], '<p style="font-family:var(--mono);font-size:1.3em;font-weight:700;color:var(--navy)">%s</p><p>%s</p>' % (E.esc(r[2]), md(r[1])), "warn")
        for r in nt["rows"]], 5) + note(para("LAB 7", "ก่อนมีสกิล")["lines"][0], "info"),
        tag="คะแนน 3 ครั้งของโจทย์เดียว", cls="mid", maxfs=1.15))
    add(S("ประตูรับแบบวัดโจทย์ละ 1 ครั้ง: การตัดสินขึ้นกับว่าสุ่มได้ rollout ครั้งไหน", bars([
        ("%s · %s · %s" % (r[0], r[1], r[2]), "", int(E.plain(r[3]).split("/")[0]), 9,
         "รับ %s" % E.plain(r[3])) for r in gt["rows"]]) +
        '<p class="cap">%s</p>' % md("แท่ง = สัดส่วนของ 9 คู่ที่ประตูรับจะ **รับ** ชุดสกิลใหม่ (เทียบบน Validation) · แถวที่ไม่ใช่ 0/9 หรือ 9/9 = ผลตัดสินขึ้นกับโชค"),
        tag="runs/*/noise.txt", maxfs=1.0))
    e7 = eyes("LAB 7")
    a7, c7 = parts(" ".join(e7[0])), parts(" ".join(e7[2]))
    add(quote("ประตูรับแบบวัดครั้งเดียว จะตัดสินการแก้ที่ดีด้วยโชค", a7[1], a7[0] + " · " + " · ".join(a7[2:])))
    add(quote("อีกด้านหนึ่ง: ประตูรับจับชุดที่เดาผิดได้", *(lambda x: (x[0].split(":", 1)[1].strip(), " · ".join(x[1:])))(parts(" ".join(e7[1])))))
    add(quote("แต่ประตูรับที่ใช้ Validation ชุดนี้ ก็จับงานคืนเงินคอร์สไม่ได้", c7[-1], " · ".join(c7[:-1])))

    # ----- 4 · สรุปและแบบฝึกหัด
    CTX.update(kicker="ภาค LAB · 4 · สรุปและแบบฝึกหัด", group="ภาค LAB · 4 · สรุปและแบบฝึกหัด")
    add(E.divider("4", "สรุปและแบบฝึกหัด", "<p>เทียบกับบท 05 และ 06 · บทเรียนจากผลจริง · โจทย์ให้ลองต่อ</p>", "img/s03-summary.jpg", small="ภาค LAB"))
    tot = parts(para("4.1", "รวมทั้งบท")["lines"][0])
    add(fig("ทั้ง %d การรัน: Validation ราย epoch และ Test Set ของชุดสกิลสุดท้าย" % len(RUNS), "img/r02-runs.png",
            para("4.1", "5 การรันแรก")["lines"][0]))
    for ttl, grp, cap in (("เห็นเฉลย · เฉลย + หมายเหตุ · เห็นแต่คะแนน", RUNS[:7], ""),
                          ("เซสชันใหม่ทุก epoch · haiku ทั้ง Solver และ Evolver", RUNS[7:], md(tot[0] + " · [`README.md`](README.md) ข้อ 4.1"))):
        add(S("Test Set ของชุดสกิลจาก epoch สุดท้าย: " + ttl, bars(
            [("`%s` · %s" % (r, SETTING[r]), "", leg(r, "v3_test")["score"], 1, "%s · %s" % (test(r), ps(r))) for r in grp]) +
            ('<p class="cap">%s</p>' % cap if cap else ""), tag="runs/*/state.json", maxfs=1.1))
    add(fig("ชุดสกิลของแต่ละการรันผ่านข้อตรวจใด · Test Set", "img/r05-coverage-test.png",
            "นโยบายเงินคืนที่เขียนกว้างทำให้ `x2-refund` ผิดในเกือบทุกการรัน · ข้อ `tests` ผ่านเฉพาะการรันที่ Solver ส่งไฟล์เทสต์ครบเกณฑ์"))
    add(fig("Test Set 3 ข้อ: EvoSkill v2 ได้ต่ำกว่าบท 05 และ 06 ทั้งที่เห็นเฉลย", "img/r03-compare.png",
            "%s · บท 05: %s · บท 06: %s · บทนี้: **%s**" % (E.plain(row(t42, "คะแนน")[0]), row(t42, "คะแนน")[1], row(t42, "คะแนน")[2].split(" · ")[0],
                                                                   row(t42, "คะแนน")[3].split(" · ")[0])))
    ppl = row(t42, "สิ่งที่คนทำ")
    add(fig("แรงที่ใช้ปรับสกิล: 3 บท 3 วิธี", "img/r04-effort.png",
            "%s · บท 05: %s · บท 06: %s · บทนี้: **%s**" % (ppl[0], ppl[1], ppl[2], ppl[3])))
    c41 = [b["lines"][0] for b in sec(why) if b["t"] == "p"]
    add(figrow("ทำไมได้ต่ำกว่าสองบทก่อน: 2 สาเหตุ และทั้งสองมาจากการออกแบบโดยตั้งใจ", ["img/n07-blind-guess.jpg", "img/n06-too-broad.jpg"],
               "ซ้าย · %s · ขวา · %s" % (c41[1].strip("*"), c41[3].strip("*"))))
    add(tbl(c41[1].strip("*"), tabh(why, 1, "บท 05 และ 06"), post=note(c41[2], "info")))
    w = tabh(why, 1, "บท 06 (")
    add(S(c41[3].strip("*"), versus(
        "ข้อความในสกิล: " + E.plain(w["rows"][1][2]),
        (md(w["head"][2]), "ที่มา: " + E.plain(w["rows"][0][2]), E.plain(w["rows"][2][2]), w["rows"][3][2]),
        (md(w["head"][1]), "ที่มา: " + E.plain(w["rows"][0][1]), E.plain(w["rows"][2][1]), w["rows"][3][1])) +
        note(c41[4], "info"), tag="งานคืนเงินคอร์สของ Test Set", cls="mid", maxfs=1.2))
    keep = ("นโยบายธุรกิจ 4 ข้อ", "ผู้ปรับสกิลเห็นอะไร", "สิ่งที่กันสกิล", "สิ่งที่คนทำ", "ความรู้ที่เหลือ")
    add(tbl("เทียบ 3 วิธีบนโจทย์เดียวกัน", {"t": "table", "head": t42["head"], "rows": [row(t42, k) for k in keep]},
            post=note("แถวอื่นของตารางนี้ (คะแนน · ต้นทุน · ขนาดของสกิล) อยู่ใน [`README.md`](README.md) ข้อ 4.2", "info")))
    add(S("คำตอบของคำถาม 7 ข้อ จากผลจริง", cards([((r[0], r[1]), r[2]) for r in table("4.3", "#")["rows"]], 4), tag="ผล LAB 1–7", maxfs=1.2))
    t44 = table("4.4", "ผล")
    lim = table("4.7", "ข้อจำกัด")["rows"]
    q2 = parts([r for r in table("4.3", "#")["rows"] if r[0].strip() == "2"][0][2])[0]
    add(nfig("n13-lessons", [
        "**พบนโยบายธุรกิจจากเฉลย:** " + q2,
        row(t44, "11 จาก 12")[1],
        row(t44, "ตาที่ 3")[1],
        row(t44, "เพิ่ม 1 ประโยค")[1],
        "**%s:** %s" % (lim[0][0], lim[0][1])]))
    more = [row(t44, k) for k in ("เซสชันใหม่ทุก epoch", "haiku:", "p1 epoch 1", "LAB 0:")]
    add(S("บทเรียนจากการตั้งค่าอื่น: เซสชันใหม่ · โมเดลเล็ก · ชุดที่เดาผิด · เครื่องวัด",
          cards([((k + 6, E.plain(r[0])), r[1], "warn") for k, r in enumerate(more)], 2), tag="ผล LAB 4–6 และ LAB 0", maxfs=1.2))
    t45 = table("4.5", "สถานการณ์")
    add(S("เลือกใช้เมื่อไร", cards([((k + 1, r[1]), "<p><b>เมื่อ</b> %s</p><p>%s</p>" % (md(r[0]), md(r[2])),
                                     "bad" if "ยังไม่ควร" in r[1] else "ok" if r[1].startswith("EvoSkill") else "")
                                    for k, r in enumerate(t45["rows"])], 3), maxfs=1.1))
    ex = table("4.6", "#")["rows"]
    add(S("แบบฝึกหัด 7 ข้อ", cards([((r[0], r[2]), r[1]) for r in ex], 4) + note(
        "โจทย์เต็มของแต่ละข้อ: [`README.md`](README.md) ข้อ 4.6", "info"), cls="mid", maxfs=1.0))
    pick = [lim[k] for k in (0, 1, 2, 3, 6, 8)]
    add(S("ข้อจำกัดของการทดลองนี้", cards([((k + 1, r[0]), r[1], "warn") for k, r in enumerate(pick)], 3) +
          note("ข้อจำกัดอีก %d ข้อ (Progressive Disclosure · การแยกเครื่อง · บัญชีที่ใช้) อยู่ใน [`README.md`](README.md) ข้อ 4.7" % (len(lim) - len(pick)), "info"),
          maxfs=1.2))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบบท", "อ่านต่อ",
                  '<p>ทฤษฎีของบทนี้: <a href="01_theory/README.md" target="_blank">01_theory/README.md</a> · '
                  '<a href="%s" target="_blank">สไลด์ของทฤษฎี</a></p>'
                  '<p>รูปแบบของเครื่องมือ: <a href="evoskill_format.md" target="_blank">evoskill_format.md</a> · '
                  'เครื่องมือที่ให้ผลในบทนี้: <code>../../00_resource/skills/evoskill</code></p>'
                  '<p>รายละเอียดเต็มของบทนี้: <a href="README.md" target="_blank">README.md</a> · ผลดิบ: '
                  '<a href="runs/" target="_blank">runs/</a></p>'
                  '<p>โจทย์เดียวกัน ปรับสกิลด้วยวิธีอื่น: <a href="../06_WikiSkill/README.md" target="_blank">WikiSkill</a> · '
                  '<a href="../05_Skill_Optimizer/README.md" target="_blank">Skill Optimizer</a></p>' % THEORY_DECK, "img/s03-summary.jpg"))
    return E.SL


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
