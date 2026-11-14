#!/usr/bin/env python3
"""สร้างสไลด์ Skill_Optimizer_Slides.html ของบท (ภาคทฤษฎี + ภาค LAB)

  python tools/build_slides.py            (รันบนเครื่อง จากโฟลเดอร์ของบท)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพ กราฟ หรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง โค้ด และพรอมต์ของ LAB: อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ตัวเลขผลของแต่ละรุ่น: อ่านจาก runs/results.json และ runs/<รุ่น>/gate.txt
- ภาพอธิบายและขั้นตอนข้างภาพ: tools/slides_figures.py · เครื่องมือเรนเดอร์: tools/slides_engine.py
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_figures import FIGS

md = E.inline
FIG = {f["img"]: f for f in FIGS}

# ------------------------------------------------------------------ ค้นบล็อกใน README.md
README = E.parse(E.read("README.md").split("\n"))
SECS, _cur = [], None
for _b in README:
    if _b["t"] == "h" and _b["level"] <= 4:
        _cur = {"level": _b["level"], "text": _b["text"], "blocks": []}
        SECS.append(_cur)
    elif _cur is not None:
        _cur["blocks"].append(_b)


def sec(prefix):
    for s in SECS:
        if s["text"].startswith(prefix):
            return s["blocks"]
    raise KeyError(prefix)


def walk(blocks):
    for b in blocks:
        yield b
        if b["t"] in ("details", "alert"):
            yield from walk(b["blocks"])


def table(prefix, head0):
    return next(b for b in walk(sec(prefix)) if b["t"] == "table" and E.plain(b["head"][0]).startswith(head0))


def codes(prefix, lang=None):
    return [b for b in walk(sec(prefix)) if b["t"] == "code" and (lang is None or b["lang"] == lang)]


def para(prefix, start):
    return next(b for b in walk(sec(prefix)) if b["t"] == "p" and b["lines"][0].startswith(start))


def prompt(prefix):
    return next(b for b in sec(prefix) if b["t"] == "alert" and any(x["t"] == "code" for x in b["blocks"]))


def eye(prefix):
    p = para(prefix, "👀")
    return " ".join([p["lines"][0][1:].strip()] + p["lines"][1:])


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


# ------------------------------------------------------------------ ตัวสร้างสไลด์
SL, CTX = [], {"kicker": "", "group": ""}


def add(s):
    for x in s if isinstance(s, list) else [s]:
        x["group"] = CTX["group"]
        SL.append(x)


def S(title, body, tag="", cls="", maxfs=1.4):
    return E.S(CTX["kicker"], title, body, tag=tag, cls=cls, maxfs=maxfs)


def note(text, kind="eye", label="ข้อสังเกต"):
    if kind == "eye":
        return '<div class="note eye"><span class="lbl">%s</span><span>%s</span></div>' % (label, md(text))
    return '<div class="note %s">%s</div>' % (kind, md(text))


def fig(title, src, cap="", tag=""):
    """ภาพเต็มสไลด์ + คำบรรยาย 1 บรรทัด"""
    b = {"t": "img", "src": src, "alt": E.plain(title)}
    body = E.fig_html(b, bool(cap)) + ('<p class="cap">%s</p>' % md(cap) if cap else "")
    return S(title, body, tag=tag, maxfs=1.1)


def explain(title, src, steps, post=""):
    """ภาพด้านซ้าย + ขั้นตอนเรียงเลขด้านขวา"""
    side = "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(steps))
    if not os.path.exists(os.path.join(E.ROOT, src)):
        return S(title, '<div class="ex"><div class="side fitbox">%s%s</div></div>' % (side, post))
    img = E.img_tag({"t": "img", "src": src, "alt": E.plain(title)})
    return S(title, '<div class="ex"><div class="fig">%s</div><div class="side fitbox">%s%s</div></div>' % (img, side, post), maxfs=1.25)


def nfig(key, post=""):
    f = FIG[key]
    return explain(f["title"], "img/%s.jpg" % key, f["steps"], post)


def tiles(items):
    out = []
    for k, num, s, tone in items:
        out.append('<div class="tile %s"><div class="k">%s</div><div class="num">%s</div><div class="s">%s</div></div>' % (tone, md(k), num, md(s)))
    return '<div class="tiles">%s</div>' % "".join(out)


def cards(items, cols=3):
    out = []
    for it in items:
        head, text, tone = (list(it) + [""])[:3]
        badge = ""
        if isinstance(head, tuple):
            badge, head = '<span class="n">%s</span>' % head[0], head[1]
        text = text if text.startswith("<") else "<p>%s</p>" % md(text)
        out.append('<div class="cardx %s"><h4>%s%s</h4>%s</div>' % (tone, badge, md(head), text))
    return '<div class="cards" style="--cols:%d">%s</div>' % (cols, "".join(out))


def versus(call, bad, good):
    def box(cls, d):
        return ('<div class="sidebox %s"><div class="hd2">%s</div><div class="calc">%s</div><div class="bigv">%s</div><p>%s</p></div>'
                % (cls, d[0], E.esc(d[1]), E.esc(d[2]), md(d[3])))
    top = '<div class="callbox">%s</div>' % E.esc(call) if call else ""
    return top + '<div class="vs">%s%s</div>' % (box("bad", bad), box("good", good))


def bars(rows):
    out = []
    for label, sub, num, den, text in rows:
        r = num / den if den else 0
        tone = "" if r >= 0.99 else "mid" if r >= 0.5 else "low"
        out.append('<div class="bar"><div class="lb">%s%s</div><div class="tr"><div class="fl %s" style="width:%d%%"></div></div>'
                   '<div class="vl">%s</div></div>' % (md(label), "<small>%s</small>" % md(sub) if sub else "", tone, round(r * 100), md(text)))
    return '<div class="bars">%s</div>' % "".join(out)


def tbl(title, t, pre="", post="", tag="ตารางหลัก"):
    return S(title, pre + E.table_html(t) + post, tag=tag)


def code(title, text, lang="text", pre="", post="", maxfs=1.3):
    return S(title, pre + E.pre_html(text, lang) + post, maxfs=maxfs)


def heat_color(v):
    hue = max(0, min(130, (v - 0.4) / 0.6 * 130))
    return "hsl(%d,62%%,80%%)" % hue


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
    t = table(prefix, "Input")
    ins = [r[0] for r in t["rows"] if r[0].strip()]
    outs = [r[1] for r in t["rows"] if len(r) > 1 and r[1].strip()]
    col = lambda cls, head, items: '<div class="ffcol %s"><div class="ffh">%s</div>%s</div>' % (
        cls, head, "".join('<div class="file">%s</div>' % md(x) for x in items))
    return ('<div class="ff">%s<div class="ffar">➜</div><div class="ffmid">%s</div><div class="ffar">➜</div>%s</div>'
            % (col("in", "INPUT · ไฟล์ที่ใช้", ins), mid, col("out", "OUTPUT · ไฟล์ที่ได้เพิ่มหลังรัน", outs)))


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
    add(E.check_slide("ขั้น 0.1", CTX["kicker"], t01))
    ft, tt = table("ขั้น 0.1", "ไฟล์ที่ได้ใน"), table("ขั้น 0.1", "ทดสอบกับผลเดิม")
    add(S("ผลจริงขั้น 0.1: ได้เครื่องมือ 5 ไฟล์", cards(
        [("%s · %s บรรทัด" % (r[0], r[1]), r[2]) for r in ft["rows"]] +
        [("ทดสอบกับผลเดิมใน `runs/`", "<ul>%s</ul>" % "".join("<li>%s: %s</li>" % (md(r[0]), md(r[1])) for r in tt["rows"]), "ok")], 3) +
        note(eye("ขั้น 0.1")), tag="ผลของผู้สอน"))
    t02 = "ขั้น 0.2 · ติดตั้งเครื่องมือ และตรวจตัวตรวจ"
    add(nfig("n14-lab0-setup"))
    add(S("ขั้น 0.2 · ไฟล์เข้าและออก", fileflow("ขั้น 0.2", "ขั้น 0.2<small>ยังไม่วัดอะไร</small>"), cls="mid"))
    add(E.prompt_slides(prompt("ขั้น 0.2"), CTX["kicker"], t02))
    add(E.check_slide("ขั้น 0.2", CTX["kicker"], t02))

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
        add(E.check_slide("LAB %d" % n, CTX["kicker"], lt))
        add(result_slide(n))
        add(fig("ประตูรับตัดสิน %s → %s อย่างไร" % (vname(base), vname(cand)), "img/r03-threshold-%s-%s.png" % (base, cand)))
        if n == 1:
            add(E.gate_slide(cand, CTX["kicker"], lt))
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
    add(E.compare_slides(CTX["kicker"]))
    add(nfig("n21-exercises"))
    add(nfig("n22-limits"))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบบท", "ถัดไป: WikiSkill",
                  '<p>ให้ AI จดสมุดความรู้ แล้วเขียนสกิลจากสมุด · ใช้งาน <code>money-coder</code> เดิม เทียบกับ Skill Optimizer → '
                  '<a href="../06_WikiSkill/README.md" target="_blank">../06_WikiSkill/README.md</a></p>'
                  '<p>รายละเอียดเต็มของบทนี้: <a href="README.md" target="_blank">README.md</a> · รูปแบบของเครื่องมือ: '
                  '<a href="skillopt_format.md" target="_blank">skillopt_format.md</a> · ทฤษฎีต้นทาง (SkillOpt): '
                  '<a href="01_theory/README.md" target="_blank">01_theory/README.md</a></p>', "img/s05-summary.jpg"))
    return SL


E.CSS += """
.slide.mid .body{justify-content:center;gap:.8em}
.cardx h4 code{font-size:.9em}
"""

if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build())
