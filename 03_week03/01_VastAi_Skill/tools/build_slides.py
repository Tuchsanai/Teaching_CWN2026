#!/usr/bin/env python3
"""สร้างสไลด์ VastAi_Skill_Slides.html ของบท 01_VastAi_Skill (ภาคทฤษฎี + ภาค LAB 0-7)

  python tools/build_slides.py                       (รันจากโฟลเดอร์ของบท)
  python tools/build_slides.py --prompts-md <ไฟล์>   เขียนพรอมต์ของ readme.md เป็นกล่อง > [!IMPORTANT] ลงไฟล์ (ใช้กับ verify_slides.py)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพ กราฟ หรือภาพหน้าจอจริงพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส
รายละเอียดเต็มของทุกหัวข้ออยู่ใน readme.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ข้อความ ตาราง ตัวเลข และพรอมต์ของ LAB: อ่านจาก readme.md ตอนสร้าง (พรอมต์ตรงตัวอักษร · ตัวเลขดึงด้วย rx() ไม่พิมพ์ซ้ำด้วยมือ)
- กลุ่มและจำนวนเคสทดสอบของแชทบอท: อ่านจาก chatbot/e2e/cases.json
- ภาพ: ภาพเดิมของบทใน image/ · ภาพใหม่ (sNN nNN) ดู tools/slides_figures.py · เครื่องมือเรนเดอร์: tools/slides_engine.py

ส่วนที่เฉพาะบทนี้ (ไม่อยู่ใน slides_engine.py)
- readme.md ใช้กล่องโค้ด ```text เป็นพรอมต์ (ไม่ใช่กล่อง > [!IMPORTANT]) → prompts_of() และ pslides()
- ภาพหน้าจอ "พรอมต์ + ผลที่ควรได้" สูงมาก → shot() แสดงเต็มความกว้างโดยเริ่มที่หัวข้อ "ผลที่ควรได้" และคลิกเพื่อดูทั้งภาพ
"""
import collections, json, os, re, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import md, sec, walk, table, codes, CTX, add, note, fig, explain, tiles, cards, versus, tbl, code
from slides_figures import FIGS

S = E.slide
README = "readme.md"
IMG = "image/"
OUT, TITLE = "VastAi_Skill_Slides.html", "เช่า GPU บน Vast.ai ด้วยสกิล vastai · Slides"
SECS = E.load(README, transform=lambda t: re.sub(r"<details>\s*\n\s*<summary>", "<details><summary>", t))
FIG = {f["img"]: f for f in FIGS}
CASES = json.loads(E.read("chatbot/e2e/cases.json"))["cases"]
HOW = "วางในช่องพิมพ์ของ Claude Code ที่เปิดโฟลเดอร์ของบทนี้ แล้วกด Enter"
LEAD = "ให้ Claude Code เช่า GPU จริงบน Vast.ai แทนเรา แล้วใช้ GPU นั้นรันโมเดลภาษาให้แชทบอทร้านค้า"
CHECK_NOTE = "เครื่องตรวจได้แค่ว่าคำตอบ**มีคำสำคัญ**หรือไม่ · คำตอบที่ผ่านเครื่องตรวจอาจยังผิดความหมาย คนจึงต้องเทียบกับ baseline อีกชั้น"
# LAB: (ทำอะไร, ค่าใช้จ่าย) สำหรับหน้าแผนที่ LAB และหน้าคั่นของแต่ละ LAB
LABS = {
    "LAB 0": ("เตรียมบัญชี Vast.ai · API key · กุญแจ SSH", "เติมเครดิต $5–10"),
    "LAB 1": ("ติดตั้งสกิล `vastai` ใน container", "ฟรี"),
    "LAB 2": ("ตั้งค่าบัญชีให้พร้อมเช่า", "ฟรี"),
    "LAB 3": ("หาเครื่องและเปรียบเทียบราคา", "ฟรี"),
    "LAB 4": ("เช่า RTX 4090 → ssh → ลบเครื่อง", "≈ $0.02"),
    "LAB 5": ("เช่า RTX 5090 แล้วเปิด AI server (NInfer + Qwen)", "≈ $0.9 ต่อชั่วโมง"),
    "LAB 6": ("ต่อแชทบอทร้านค้าเข้ากับ AI server แล้วทดสอบ 26 เคส", "(เครื่องเดิม)"),
    "LAB 7": ("ปิดทุกอย่าง", "หยุดเสียเงิน"),
}
VARY = "ราคาและเครื่องในตลาดเปลี่ยนตลอดเวลา ตัวเลขของคุณจะไม่เหมือนของผู้สอน ให้ดูที่วิธีคิด"


# ------------------------------------------------------------------ ตัวช่วยอ่าน readme.md
def flat(prefix):
    return list(walk(sec(prefix)))


def heading(prefix):
    return next(s["text"] for s in SECS if s["text"].startswith(prefix))


def clean(s):
    """ตัดอีโมจิและเครื่องหมายนำของ readme ออก (สไลด์ไม่ใช้อีโมจิในข้อความ)"""
    return re.sub(r"[⚠🟠🔵✔]️?\s*", "", s).strip()


def star(s):
    """คำบรรยายใต้ภาพของ readme (*...*) → ข้อความ"""
    s = s.strip()
    return s[1:-1].strip() if s.startswith("*") and s.endswith("*") else s


def image(prefix, name):
    return next(b for b in flat(prefix) if b["t"] == "img" and name in b["src"])


def cap(prefix, name):
    """คำบรรยายที่อยู่ใต้ภาพ name ในหัวข้อ prefix"""
    bl = flat(prefix)
    k = next(i for i, b in enumerate(bl) if b["t"] == "img" and name in b["src"])
    nx = bl[k + 1] if k + 1 < len(bl) else None
    if nx and nx["t"] == "p" and nx["lines"][0].startswith("*"):
        return star(nx["lines"][0])
    raise KeyError("ไม่พบคำบรรยายใต้ภาพ %r" % name)


def ptext(prefix, start):
    """ย่อหน้าของหัวข้อ prefix ที่ขึ้นต้นด้วย start (บรรทัดแรก)"""
    for b in flat(prefix):
        if b["t"] == "p" and b["lines"][0].startswith(start):
            return b["lines"][0]
    raise KeyError("ไม่พบย่อหน้า %r ในหัวข้อ %r" % (start, prefix))


def plist(prefix, start="1. "):
    """รายการเรียงเลข (1. 2. 3.) ของหัวข้อ prefix → รายการข้อความ"""
    for b in flat(prefix):
        if b["t"] == "p" and b["lines"][0].startswith(start):
            return [re.sub(r"^\d+\.\s*", "", l) for l in b["lines"]]
    raise KeyError("ไม่พบรายการเรียงเลขในหัวข้อ %r" % prefix)


def ul_after(prefix, start):
    """รายการ (- ...) ที่อยู่ถัดจากย่อหน้าที่ขึ้นต้นด้วย start"""
    bl = flat(prefix)
    for i, b in enumerate(bl):
        if b["t"] == "p" and b["lines"][0].startswith(start):
            return next(x for x in bl[i + 1:] if x["t"] == "ul")["items"]
    raise KeyError("ไม่พบรายการหลัง %r ในหัวข้อ %r" % (start, prefix))


def first_ul(prefix):
    return next(b for b in flat(prefix) if b["t"] == "ul")["items"]


def read_result(prefix):
    return ul_after(prefix, "**อ่านผลอย่างไร**")


def prompts_of(prefix):
    """พรอมต์ของหัวข้อ = กล่องโค้ด ```text ที่ขึ้นต้นด้วย "ทำงานใน container" """
    return [b for b in flat(prefix) if b["t"] == "code" and b["text"].startswith("ทำงานใน container")]


def all_prompts():
    return [b for s in SECS for b in walk(s["blocks"]) if b["t"] == "code" and b["text"].startswith("ทำงานใน container")]


def pslides(block, title):
    """สไลด์พรอมต์ (ตรงตัวอักษร + ปุ่มคัดลอก) จากกล่องโค้ดของ readme"""
    return E.prompt_slides({"blocks": [{"t": "p", "lines": [HOW]}, block]}, CTX["kicker"], title)


def plines(block, pat):
    """บรรทัดของพรอมต์ที่ตรงกับ pat (ตัดเครื่องหมายนำออก)"""
    return [re.sub(pat, "", l) for l in block["text"].split("\n") if re.match(pat, l)]


def rx(pat, text, g=1):
    """ดึงตัวเลขหรือคำจากข้อความของ readme · ไม่พบ = readme เปลี่ยน ให้แก้ตัวค้น"""
    m = re.search(pat, text)
    if not m:
        raise KeyError("ไม่พบ %r ใน %r" % (pat, text[:80]))
    return m.group(g)


def alt_steps(alt):
    """alt ของภาพภาพรวม LAB ("LAB 4: 1 เช่า... 2 รอ... 3 ...") → รายการขั้น"""
    body = alt.split(":", 1)[1].strip()
    return [re.sub(r"^\d\s+", "", x).strip() for x in re.split(r" (?=\d )", body)]


def bold1(s):
    """ทำคำแรกเป็นตัวหนา"""
    a, _, b = s.strip().partition(" ")
    return "**%s** %s" % (a, b)


# ------------------------------------------------------------------ ชิ้นส่วนเฉพาะบท
def gif_size(src):
    with open(os.path.join(E.ROOT, src), "rb") as f:
        return struct.unpack("<HH", f.read(10)[6:10])


def result_top(src):
    """ตำแหน่ง (px) ของหัวข้อ "ผลที่ควรได้" ในภาพหน้าจอ = วงกลมแดงหมายเลข 2 · ไม่มี Pillow = ประมาณจากสัดส่วน"""
    w, h = E.img_size(src)
    try:
        from PIL import Image
    except ImportError:
        return int(h * 0.3), w
    im = Image.open(os.path.join(E.ROOT, src)).convert("RGB")
    px, runs = im.load(), []
    for y in range(h):
        red = sum(1 for x in range(40, 100) if px[x, y][0] > 180 and px[x, y][1] < 90 and px[x, y][2] < 90)
        if red > 8:
            if runs and y - runs[-1][1] <= 3:
                runs[-1][1] = y
            else:
                runs.append([y, y])
    return (max(0, runs[1][0] - 28) if len(runs) > 1 else 0), w


def shot(title, src, caption="", post="", tag="ผลที่ควรได้"):
    """ภาพหน้าจอสูง: แสดงเต็มความกว้าง เริ่มที่หัวข้อ "ผลที่ควรได้" · คลิกเพื่อดูทั้งภาพ"""
    top, w = result_top(src)
    wd, ht = E.img_size(src)
    body = ('<div class="fig shot"><img src="%s" alt="%s" width="%d" height="%d" style="margin-top:-%.2f%%">'
            '<span class="zoom">คลิกภาพเพื่อดูทั้งภาพ</span></div>') % (src, E.html.escape(E.plain(title)), wd, ht, top * 100.0 / w)
    if caption:
        body += '<p class="cap">%s</p>' % md(caption)
    return S(title, body + post, tag=tag, maxfs=1.1)


def points(title, items, two=False, tag="", post=""):
    """รายการเรียงเลขเต็มความกว้าง (ข้อความจาก readme)"""
    rows = "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(items))
    return S(title, '<div class="pts %s">%s</div>' % ("two" if two else "", rows) + post, tag=tag, cls="mid", maxfs=1.3)


def facts(what, items):
    return "<p>%s</p><div class=\"facts\">%s</div>" % (md(what), "".join(
        '<div><span class="fl">%s</span>%s</div>' % (k, md(v)) for k, v in items if v))


def nfig(key, steps, title=None, post=""):
    return explain(title or FIG[key]["title"], "%s%s.jpg" % (IMG, key), steps, post)


def gif_slide(n, title):
    """1 เคสทดสอบ: GIF ด้านซ้าย · สิ่งที่ลูกค้าทำ เงื่อนไข และคำตอบ ด้านขวา (จากตารางของ readme)"""
    bl = sec("LAB 6")
    k = next(i for i, b in enumerate(bl) if b["t"] == "p" and b["lines"][0].startswith("**เคส %d**" % n))
    act = bl[k]["lines"][0].split("·", 1)[1].strip()
    im, row = bl[k + 1], bl[k + 2]["rows"][0]
    w, h = gif_size(im["src"])
    real = row[2] if E.vlen(row[2]) <= 170 else ""
    side = [("ลูกค้าทำ", act, "navy"), ("เครื่องตรวจ", row[0], ""), ("คำตอบที่ควรได้ (baseline)", row[1], "ok")]
    if real:
        side.append(("คำตอบจริง", real, "warn"))
    html = "".join('<div class="cardx %s"><h4>%s</h4><p>%s</p></div>' % (t, a, md(b)) for a, b, t in side)
    return S(title, '<div class="ex"><div class="fig"><img src="%s" alt="%s" width="%d" height="%d"></div><div class="side fitbox">%s</div></div>'
             % (im["src"], E.html.escape(E.plain(im["alt"])), w, h, html), tag="GIF จากการทดสอบ", maxfs=1.15)


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    labs = ["LAB %d" % n for n in range(8)]
    labrow = {k: (k, LABS[k][0], LABS[k][1]) for k in labs}

    def lab_divider(n, what, time=""):
        name = heading("LAB %d ·" % n).split("·", 1)[1].strip()
        CTX.update(kicker="ภาค LAB · LAB %d · %s" % (n, name), group="LAB %d · %s" % (n, E.plain(name)))
        add(E.divider("LAB %d" % n, name, facts(what, [("ค่าใช้จ่าย", labrow["LAB %d" % n][2]), ("เวลาโดยประมาณ", time)]), small="ภาค LAB"))
        return name

    def took(prefix, name):
        return rx(r"ใช้เวลา(ประมาณ[^·]+)", cap(prefix, name)).strip()

    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    intro = sec("เช่า GPU")
    add(E.cover(E.plain(SECS[0]["text"]), LEAD, IMG + "cover.jpg", small="03_week03 · บทที่ 01"))
    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("ทั้งเรื่องในภาพเดียว: แชทบอทร้านค้าที่ใช้โมเดลภาษาบน GPU ที่ AI เช่าให้", IMG + "lab6-overview.png",
            "ทุกขั้นทำด้วยพรอมต์ Copy & Paste ใน **Claude Code** และงานทั้งหมดเกิดใน container `multi-account`"))
    theory = [s["text"] for s in SECS if s["level"] == 2 and re.match(r"\d ·", s["text"])]
    box = lambda cls, name, small, inner: '<div class="partbox %s"><div class="ph">%s<small>%s</small></div>%s</div>' % (cls, name, small, inner)
    road = box("", "ภาคทฤษฎี", "%d หัวข้อ" % len(theory),
               "".join('<div class="secbox"><b>%s</b></div>' % md(t) for t in theory))
    road += box("lab", "ภาค LAB", "%d LAB · พรอมต์ Copy &amp; Paste" % len(labs), '<div class="grid2">%s</div>' % "".join(
        '<div class="secbox"><b>%s</b><span>%s</span></div>' % (k, md(labrow[k][1])) for k in labs))
    add(S("บทนี้มี 2 ภาค: เข้าใจก่อน แล้วลงมือเช่าเครื่องจริง", '<div class="road">%s</div>' % road + note(
        "รายละเอียดเต็มของทุกหัวข้ออยู่ใน [`readme.md`](readme.md)", "info"), cls="mid"))
    add(S("วิธีใช้สไลด์นี้", cards([
        ("ไปหน้าถัดไป / ก่อนหน้า", '<p><span class="kbd">→</span> <span class="kbd">Space</span> / <span class="kbd">←</span> หรือปุ่มมุมขวาล่าง</p>'),
        ("สารบัญทุกหน้า", '<p><span class="kbd">O</span> แล้วคลิกหน้าที่ต้องการ · <span class="kbd">F</span> เต็มจอ</p>'),
        ("ขยายภาพ", "คลิกที่ภาพ · ภาพหน้าจอของผลแสดงเฉพาะส่วนบน คลิกเพื่อดูทั้งภาพ · คลิกอีกครั้งหรือ Esc เพื่อปิด"),
        ("คัดลอกพรอมต์ของ LAB", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** ให้ข้อความเดียวกับ `readme.md` ตรงตัวอักษร", "warn"),
        ("ตรวจผลหลังรัน", "สไลด์ **ตรวจผลของคุณ** ต่อจากพรอมต์ของ LAB · ติ๊กได้ และจำค่าไว้ในเบราว์เซอร์นี้", "warn"),
        ("เปิดไฟล์จริง", "ลิงก์สีน้ำเงินเปิดไฟล์ในโฟลเดอร์ของบท · เปิดสไลด์จากโฟลเดอร์ `01_VastAi_Skill`"),
    ]), cls="mid"))

    # ===== ภาคทฤษฎี
    CTX.update(kicker="", group="ภาคทฤษฎี")
    add(E.divider("ภาคทฤษฎี", "สิ่งที่ต้องเข้าใจก่อนเช่าเครื่องจริง",
                  "<p>%s</p>" % " · ".join(md(t.split("·", 1)[1].strip()) for t in theory), IMG + "s01-theory.jpg"))

    # 1 · สกิล
    h = "1 · สกิล"
    CTX.update(kicker="ภาคทฤษฎี · " + heading(h), group="ภาคทฤษฎี · " + E.plain(heading(h)))
    t = table(h, "ชิ้น")
    add(explain("สกิล `vastai` ทำงานได้เมื่อมีครบ %d ชิ้น" % len(t["rows"]), IMG + "concept-01-three-parts.png",
                [ptext(h, "Vast.ai คือ")] + ["%s — %s" % (r[0], r[1]) for r in t["rows"]]))
    add(S("ทั้ง %d ชิ้นติดตั้งใน container ไม่ได้ติดตั้งบนเครื่องของเรา" % len(t["rows"]),
          cards([((k + 1, r[0]), "ติดตั้งด้วย %s" % r[2]) for k, r in enumerate(t["rows"])], 3) + note(ptext(h, "ทั้ง ")), cls="mid"))

    # 2 · กุญแจ
    h = "2 · กุญแจ"
    CTX.update(kicker="ภาคทฤษฎี · " + heading(h), group="ภาคทฤษฎี · " + E.plain(heading(h)))
    t = table(h, "กุญแจ")
    add(explain("กุญแจ %d ดอก: ดอกหนึ่งสั่งงานบัญชี อีกดอกเข้าเครื่องที่เช่า" % len(t["rows"]), IMG + "concept-02-two-keys.png",
                [x for r in t["rows"] for x in ("%s — %s" % (clean(r[0]), r[1]), "%s เก็บที่ %s" % (clean(r[0]), r[2]))]))
    t = table(h, "ไฟล์")
    add(S("กุญแจ SSH มี %d ไฟล์เสมอ: ไฟล์หนึ่งเปิดเผยได้ อีกไฟล์ห้ามส่งให้ใคร" % len(t["rows"]),
          cards([("%s · %s" % (r[0], r[1]), r[2], tone) for r, tone in zip(t["rows"], ("ok", "bad"))], 2)
          + note(ptext(h, "เครื่องที่เช่าจะรับ")), cls="mid"))

    # 3 · เครื่องคิดเงินตอนไหน
    h = "3 · เครื่อง"
    CTX.update(kicker="ภาคทฤษฎี · " + heading(h), group="ภาคทฤษฎี · " + E.plain(heading(h)))
    im = image(h, "concept-03")
    add(explain(E.plain(cap(h, "concept-03")).replace(" — ", ": "), im["src"],
                [bold1(x) for x in im["alt"].split(":", 1)[1].split("→")]))

    # 4 · เพดานราคา
    h = "4 · เพดาน"
    CTX.update(kicker="ภาคทฤษฎี · " + heading(h), group="ภาคทฤษฎี · " + E.plain(heading(h)))
    p = ptext(h, "สกิลของ Vast.ai").split(" · ")
    add(explain("สกิลไม่มีเพดานราคาในตัว เราเขียนเพดานไว้ในพรอมต์เอง", IMG + "concept-04-price-cap.png",
                p + ["ราคาไม่เกินเพดาน → AI เช่าได้เลย", "ราคาเกินเพดาน → AI หยุดแล้วถามเรา"]))

    # 5 · โมเดลใหญ่เกิน GPU
    h = "5 · โมเดล"
    CTX.update(kicker="ภาคทฤษฎี · " + heading(h), group="ภาคทฤษฎี · " + E.plain(heading(h)))
    p = ptext(h, "โมเดล Qwen").split(" · ")
    add(explain("โมเดลใหญ่เกิน GPU จึงต้องบีบอัดด้วย quantization", IMG + "concept-09-quantization.png",
                p + [rx(r"(เหมือน.+)$", image(h, "concept-09")["alt"]).replace("เหมือน", "เปรียบได้กับการ", 1)]))

    # ===== ภาค LAB
    CTX.update(kicker="", group="ภาค LAB")
    add(E.divider("ภาค LAB", "ลงมือทำ %d LAB ด้วยพรอมต์ Copy & Paste" % len(labs),
                  "<p>%s</p>" % md(next(b for b in sec("ภาค LAB") if b["t"] == "p")["lines"][0]), IMG + "s03-lab.jpg"))
    CTX["kicker"] = "ภาค LAB · ก่อนเริ่ม"
    add(S("แผนที่ของ LAB: LAB ไหนฟรี LAB ไหนเสียเงินจริง", cards([
        (k, "%s<br>**%s**" % (labrow[k][1], labrow[k][2]), "warn" if "$" in labrow[k][2] else "ok") for k in labs], 4), cls="mid"))
    warn = clean(next(b for b in intro if b["t"] == "alert")["blocks"][0]["lines"][0])
    add(S("ก่อนเริ่ม: จำไว้ว่าเครื่องคิดเงินจริง",
          note(warn, "bad")
          + note("ทุก LAB มีลำดับเดียวกัน: ภาพขั้นตอน → พรอมต์ (คัดลอก) → ตรวจผลของคุณ → ผลที่ควรได้ → อ่านผลอย่างไร", label="ลำดับ"), cls="mid"))

    # ----- LAB 0
    lab_divider(0, sec("LAB 0")[0]["lines"][0])
    h1, h2, h3, ho = "ขั้นที่ 1 · สมัคร", "ขั้นที่ 2 · ใส่", "ขั้นที่ 3 · สร้าง", "ทางเลือก"
    add(explain("ขั้นที่ 1 · สมัครและเติมเครดิตด้วยตัวเอง ห้ามให้ AI กรอกข้อมูลบัตร", IMG + "vast-02-billing.png",
                plist(h1) + [cap(h1, "vast-02")]))
    add(points("ขั้นที่ 2 · ใช้กุญแจ SSH ที่เตรียมไว้ให้ในโฟลเดอร์ `Devtool_SSH/`", plist(h2),
               post=note(clean(next(b for b in sec(h2) if b["t"] == "alert")["blocks"][0]["lines"][0]), "bad")))
    for n, tt in [("vast-03", "เปิดหน้า Keys แท็บ SSH Keys แล้วกด + New"), ("vast-04", "วาง public key ทั้งบรรทัด แล้วกด Save"),
                  ("vast-05", "มีแถวใหม่ในตาราง = ใส่กุญแจ SSH สำเร็จ")]:
        add(fig("ขั้นที่ 2 · " + tt, image(h2, n)["src"], clean(cap(h2, n)), tag="ภาพหน้าจอจริง"))
    t = table(ho, "ระบบ")
    add(code("ทางเลือก · สร้างกุญแจ SSH ของตัวเองด้วยคำสั่งเดียว", codes(ho, "bash")[0]["text"], "bash",
             pre=cards([("%s · %s" % (r[0], r[1]), r[2]) for r in t["rows"]], 2), post=note(ptext(ho, "โปรแกรมถาม"), "info")))
    add(fig("ได้ไฟล์ใหม่ในโฟลเดอร์ `Devtool_SSH/`: private key เก็บไว้ public key เอาไปใส่เว็บ", IMG + "ssh-keygen-files.png",
            cap(ho, "ssh-keygen") + " · " + ptext(ho, "ใช้กุญแจของตัวเองแล้ว")))
    for n, tt in [("vast-06", "เปิดแท็บ API Keys แล้วกด + New"), ("vast-07", "เอาติ๊ก Billing/Earning → Write ออก: AI แก้การเงินของบัญชีไม่ได้"),
                  ("vast-08", "คัดลอก key ทันที แล้ววางลง `.env` ก่อนกด Close")]:
        add(fig("ขั้นที่ 3 · " + tt, image(h3, n)["src"], clean(cap(h3, n)), tag="ภาพหน้าจอจริง"))
    add(code("วาง key ลงไฟล์ `.env` ทันที เพราะเห็นได้ครั้งเดียว", codes(h3, "text")[0]["text"], "text",
             pre="<p>%s</p>" % md(ptext(h3, "คัดลอกไฟล์")), post=note(ptext(h3, "ห้ามใส่"), label="ระวัง")))
    add(E.check_slide("LAB 0", ["บัญชี Vast.ai มีเครดิต (เติมเองด้วยมือ)",
                                "แท็บ **SSH Keys** มีแถวของ public key ที่ใส่",
                                "API key ถูกสร้างโดยเอาติ๊กที่ **Billing/Earning → Write** ออก",
                                "ไฟล์ `.env` มีบรรทัด `VAST_API_KEY=` ไม่มีเครื่องหมายคำพูดครอบ และไม่มี comment ต่อท้ายบรรทัด"],
                      "", "LAB นี้ทำบนเว็บและบนเครื่องเราเอง ยังไม่ใช้ Claude Code", "LAB 0 · บัญชีและกุญแจพร้อม"))

    # ----- LAB 1
    h = "LAB 1 ·"
    pr = prompts_of(h)[0]
    lab_divider(1, ptext(h, "เปิด Claude Code"), took(h, "lab1-install"))
    add(explain("LAB 1 · Claude Code ติดตั้งเฉพาะสิ่งที่ยังไม่มีใน container", IMG + "lab1-overview.png", plines(pr, r"^\d+\.\s*")))
    add(pslides(pr, "LAB 1 · ติดตั้งสกิล `vastai`"))
    rr = read_result(h)
    add(E.check_slide("LAB 1", [rr[0], "สกิล `vastai` อยู่ใน path ของทั้ง Claude และ Codex", "คำสั่ง `vastai` และคำสั่ง `ssh` มีเวอร์ชันหรือ path แสดงในตาราง"],
                      cap(h, "lab1-install"), "เวอร์ชันที่ได้อาจใหม่กว่าในภาพของผู้สอน", "LAB 1 · ติดตั้งครบ"))
    add(shot("ผลที่ควรได้ของ LAB 1: ตารางบอกว่าแต่ละรายการมีอยู่แล้วหรือเพิ่งติดตั้ง", IMG + "lab1-install.png", cap(h, "lab1-install")))
    add(points("อ่านผล LAB 1: ทำไม Claude Code ถามขออนุญาต และสกิลถูกประเมินว่าเสี่ยง", rr[1:]))

    # ----- LAB 2
    h = "LAB 2 ·"
    pr = prompts_of(h)[0]
    lab_divider(2, next(b for b in sec(h) if b["t"] == "p")["lines"][0], took(h, "lab2-setup"))
    add(explain("LAB 2 · นำกุญแจทั้งสองดอกเข้า container แล้วตรวจบัญชี", IMG + "lab2-overview.png", plines(pr, r"^\d+\.\s*")))
    add(pslides(pr, "LAB 2 · ตั้งค่าบัญชี"))
    rr = read_result(h)
    add(E.check_slide("LAB 2", [rr[0], "public key ลงทะเบียนกับบัญชีแล้ว", "คำตอบไม่แสดงอีเมล key หรือ token"],
                      cap(h, "lab2-setup"), "", "LAB 2 · บัญชีพร้อมเช่า"))
    add(shot("ผลที่ควรได้ของ LAB 2: เครดิตพอ และไม่มีเครื่องเปิดค้าง", IMG + "lab2-setup.png", cap(h, "lab2-setup")))
    add(points("อ่านผล LAB 2: ตั้งค่าครั้งเดียว LAB ถัดไปไม่ต้องส่ง key อีก", rr[1:]))

    # ----- LAB 3
    h, h1, h2, h3 = "LAB 3 ·", "ขั้นที่ 1 · เทียบ", "ขั้นที่ 2 · ค้น", "ขั้นที่ 3 · ถาม"
    name = lab_divider(3, next(b for b in sec(h) if b["t"] == "p")["lines"][0])
    base = CTX["kicker"]
    t = table(h1, "ส่วน")
    add(explain("ราคาของเครื่องมี %d ส่วน ไม่ใช่แค่ค่า GPU" % len(t["rows"]), IMG + "lab3-overview.png",
                ["%s — %s" % (r[0], r[1]) for r in t["rows"]]))
    CTX["kicker"] = base + " · " + heading(h1)
    pr = prompts_of(h1)[0]
    add(pslides(pr, "LAB 3 · " + heading(h1)))
    rr = read_result(h1)
    add(fig("ค่า GPU ถูกที่สุด ไม่ได้แปลว่าจ่ายรวมถูกที่สุด", IMG + "lab3-search-chart.png", cap(h1, "lab3-search.png"), tag="กราฟจากผลจริง"))
    add(S("เครื่องเดียวกัน เรียงคนละแบบ ได้ผู้ชนะคนละเครื่อง", versus(
        "งานตัวอย่าง: " + rx(r"งานตัวอย่าง \((.+?)\)", pr["text"]),
        ("ค่า GPU ถูกที่สุด · " + rx(r"\((\w+) \$", rr[0]), "ค่า GPU " + rx(r"(\$[\d.]+/ชม\.)", rr[0]), "รวม " + rx(r"จ่ายรวม (\$[\d.]+)", rr[0]), rr[0]),
        ("จ่ายรวมถูกที่สุด · " + rx(r"\((\w+) \$", rr[1]), rx(r"(อันดับ \d+ ของราคา GPU)", rr[1]), "รวม " + rx(r"(\$[\d.]+)\)", rr[1]), rr[1])), cls="mid"))
    add(shot("ผลที่ควรได้ของขั้นที่ 1: ตารางเรียงตามราคา GPU และตารางเรียงตามค่าใช้จ่ายรวม", IMG + "lab3-search.png", cap(h1, "lab3-search.png")))
    add(points("อ่านผลให้ครบ: ความน่าเชื่อถือ และระยะเวลาที่ใช้เครื่อง", rr[2:]))
    t = table(h1, "อยากได้")
    add(S("ลองเปลี่ยนเงื่อนไขเอง: แก้บรรทัดในพรอมต์แล้ววางใหม่ ไม่เสียเงิน", cards([(r[0], "แก้ในพรอมต์: " + r[1]) for r in t["rows"]], 3), cls="mid"))

    CTX["kicker"] = base + " · " + heading(h2)
    add(pslides(prompts_of(h2)[0], "LAB 3 · " + heading(h2)))
    rr = read_result(h2)
    add(fig("การค้น 1 ครั้งไม่ได้เห็นทั้งตลาด", IMG + "lab3-limits-chart.png", cap(h2, "lab3-limits-chart"), tag="กราฟจากผลจริง"))
    add(S("การค้นมีเพดาน และระบบไม่เตือนว่าผลถูกตัด", tiles([
        ("เพดานของการค้น 1 ครั้ง", rx(r"สูงสุด (\d+) เครื่อง", rr[0]) + "<small> เครื่อง</small>", rx(r"(ขอ .+ เท่าเดิม)", E.plain(rr[0])), "warn"),
        ("RTX 4090 ทั้งตลาด", rx(r"ทั้งหมด (\d+) เครื่อง", rr[1]) + "<small> เครื่อง</small>", rx(r"(การค้นครั้งเดียว.+)$", rr[1]), ""),
        ("เครื่องที่ซ้ำกันทุกครั้งที่ค้น", rx(r"เพียง (\d+) เครื่อง", rr[2]) + "<small> เครื่อง</small>", rx(r"^(.+?) แต่", E.plain(rr[2])), "bad"),
        ("เงื่อนไขที่ใช้ค้นได้", rx(r"มี (\d+) อย่าง", rr[5]) + "<small> อย่าง</small>", rx(r"(ใน \d+ กลุ่ม)", rr[5]), "ok")])
        + note(rr[3]), cls="mid", tag="ผลของรอบตัวอย่าง"))
    add(points("ก่อนสรุปว่าถูกที่สุด: เติมเงื่อนไขให้แคบลง แล้วค้นซ้ำ", [rr[2], rr[4], rr[5]]))
    add(shot("ผลที่ควรได้ของขั้นที่ 2: ตารางของแต่ละข้อ และข้อควรระวัง", IMG + "lab3-limits.png", cap(h2, "lab3-limits-chart")))

    CTX["kicker"] = base + " · " + heading(h3)
    bl = flat(h3)
    scen = [(i, b["lines"][0].strip("*")) for i, b in enumerate(bl) if b["t"] == "p" and b["lines"][0].startswith("**สถานการณ์")]
    add(nfig("n01-scenarios", ul_after(h3, "**สิ่งที่ได้จากทั้ง"),
             "ถามตลาดด้วยสถานการณ์จริง %d แบบ: ไม่เช่าเครื่องและไม่เสียเงิน" % len(scen),
             post=note(next(b for b in sec(h3) if b["t"] == "p")["lines"][0].split(" · ")[-1], "info")))
    for k, (i, nm) in enumerate(scen):
        end = scen[k + 1][0] if k + 1 < len(scen) else len(bl)
        part = bl[i:end]
        pr = next(b for b in part if b["t"] == "code")
        concl = next(b["lines"][0] for b in part if b["t"] == "p" and b["lines"][0].startswith("**ข้อสรุป:**")).replace("**ข้อสรุป:**", "").strip()
        im = next(b for b in part if b["t"] == "img")
        add(pslides(pr, nm))
        add(shot("ผลของ" + nm, im["src"], post=note(concl, label="ข้อสรุป")))
    add(E.check_slide("LAB 3", ["ขั้นที่ 1 ได้ทั้งตารางที่เรียงตามราคา GPU และตารางที่เรียงตามค่าใช้จ่ายรวม",
                                "AI บอกว่าเครื่องที่ถูกที่สุดของสองตารางเป็นเครื่องเดียวกันหรือไม่ พร้อมเหตุผล",
                                "ขั้นที่ 2 ได้ตารางครบทุกข้อ และข้อควรระวังเมื่อผลการค้นถูกตัดจำนวน",
                                "ขั้นที่ 3 ทุกคำถามได้ข้อสรุป หรือคำตอบตรง ๆ ว่าทำไม่ได้",
                                "ไม่มีเครื่องถูกเช่า: หน้า Instances ยังว่าง"],
                      cap(h1, "lab3-search.png"), VARY, "LAB 3 · " + E.plain(name)))

    # ----- LAB 4
    h, h1, h2 = "LAB 4 ·", "ขั้นที่ 1 · เช่า", "ขั้นที่ 2 · ลบ"
    pay = next(b for b in sec(h) if b["t"] == "p")["lines"][0]
    name = lab_divider(4, pay, took(h1, "lab4-rent"))
    base = CTX["kicker"]
    add(explain("LAB 4 · เช่า รอ ssh เข้าไปดู GPU แล้วลบเครื่อง ในรอบเดียว", IMG + "lab4-overview.png",
                alt_steps(image(h, "lab4-overview")["alt"]), post=note(pay, "bad")))
    CTX["kicker"] = base + " · " + heading(h1)
    pr = prompts_of(h1)[0]
    add(pslides(pr, "LAB 4 · " + heading(h1)))
    rr = read_result(h1)
    add(shot("ผลที่ควรได้ของขั้นที่ 1: เครื่อง running และผล nvidia-smi จากเครื่องที่เช่า", IMG + "lab4-rent.png", cap(h1, "lab4-rent")))
    add(points("อ่านผล: ราคาไม่เกินเพดาน และคำสั่งรันบนเครื่องที่เช่าจริง", rr))
    add(fig("หน้า Instances แสดงเครื่องเดียวกับที่ AI เช่าให้", IMG + "lab4-console.png", clean(cap(h1, "lab4-console")), tag="ภาพหน้าจอจริง"))
    CTX["kicker"] = base + " · " + heading(h2)
    add(pslides(prompts_of(h2)[0], "LAB 4 · " + heading(h2)))
    r2, c2 = read_result(h2), cap(h2, "lab4-destroy")
    add(S("ลบเครื่องทันทีหลังใช้ ค่าใช้จ่ายของรอบตัวอย่างจึงน้อยมาก", tiles([
        ("เครื่องเปิดอยู่", rx(r"เปิดอยู่ ([\d.]+) นาที", c2) + "<small> นาที</small>", "ตั้งแต่เช่าจนลบ", ""),
        ("Vast.ai เรียกเก็บ", rx(r"เรียกเก็บ (\$[\d.]+)", c2), "ยอดของรอบตัวอย่าง", "ok"),
        ("เครื่องค้างในบัญชี", rx(r"Total: (\d+) instances", r2[0]), "ต้องเห็น `%s`" % rx(r"`(Total: \d+ instances)`", r2[0]), "ok")])
        + note(r2[1]), cls="mid", tag="ผลของรอบตัวอย่าง"))
    add(shot("ผลที่ควรได้ของขั้นที่ 2: ลบแล้ว ไม่มีเครื่องค้าง และตารางค่าใช้จ่าย", IMG + "lab4-destroy.png", c2))
    add(E.check_slide("LAB 4", [rr[0], rr[1], r2[0]], c2, VARY, "LAB 4 · " + E.plain(name)))

    # ----- LAB 5
    h, hw, hp = "LAB 5 ·", "ทำไมต้องมีไฟล์สูตร", "วางพรอมต์"
    pay = next(b for b in sec(h) if b["t"] == "p")["lines"][0]
    name = lab_divider(5, pay, took(hp, "lab5-server"))
    add(explain("LAB 5 · AI ทำตามสูตรตั้งแต่เช่าเครื่องจนได้ค่าเชื่อมต่อ", IMG + "lab5-overview.png",
                alt_steps(image(h, "lab5-overview")["alt"]), post=note(pay, "bad")))
    t = table(hw, "เหตุผล")
    add(explain("ทำไมต้องมีไฟล์สูตร: งานที่เสียเงินต้องทำซ้ำได้เหมือนเดิม", IMG + "lab5-why-recipe.png",
                ["%s — %s" % (r[0], r[1]) for r in t["rows"]]))
    add(tbl("ทุกส่วนของสูตรมีที่มา เปิดดูต้นทางเทียบได้", table(hw, "ส่วนของสูตร"),
            pre="<p>%s</p>" % md(ptext(hw, "**สูตร** คือ").split(" · ")[0]), post=note(ptext(hw, "สูตรสั่งให้ AI").replace(" · ", " "))))
    t = table(hw, "ค่าในพรอมต์")
    pr = prompts_of(hp)[0]
    add(S("พรอมต์กำหนดแค่ %d ค่า ที่เหลืออยู่ในสูตร" % len(t["rows"]), cards([(r[0], r[1], "warn") for r in t["rows"]], 3)
          + E.pre_html(pr["text"].split("\n")[-1], "text"), cls="mid"))
    add(pslides(pr, "LAB 5 · เปิด AI server ตามสูตร"))
    rr = read_result(hp)
    c5, a5 = cap(hp, "lab5-server"), image(hp, "lab5-server")["alt"]
    add(E.check_slide("LAB 5", [rr[0], rr[1], rr[3], "ราคาต่อชั่วโมงไม่เกิน `MAX_DPH` ที่เขียนในพรอมต์"], c5, VARY, "LAB 5 · " + E.plain(name)))
    add(S("ผลของรอบตัวอย่าง: AI server พร้อมใช้ และตอบภาษาไทยได้", tiles([
        ("ราคาเครื่อง RTX 5090 ต่อชั่วโมง", rx(r"ราคา (\$[\d.]+) ต่อชั่วโมง", a5), "ไม่เกินเพดาน `%s`" % rx(r"(MAX_DPH=[\d.]+)", pr["text"]), ""),
        ("build NInfer", rx(r"build NInfer (\d+ นาที)", a5) + "<small> %s</small>" % rx(r"build NInfer \d+ นาที (\d+ วินาที)", a5), "โหลดโมเดล %s · เปิด server %s" % (
            rx(r"โหลดโมเดล (\d+ วินาที)", a5), rx(r"เปิด server (\d+ วินาที)", a5)), ""),
        ("ความเร็ว (token ต่อวินาที)", rx(r"ความเร็ว ([\d.]+) token", a5), "โมเดล `%s`" % rx(r"โมเดล (\S+)", a5), "ok"),
        ("VRAM ที่ใช้", rx(r"VRAM (\d+) จาก", a5) + "<small> MiB</small>", "จาก %s MiB" % rx(r"จาก (\d+) MiB", a5), "warn")])
        + note(rr[2]), cls="mid", tag="ผลของรอบตัวอย่าง"))
    add(shot("ผลที่ควรได้ของ LAB 5: ตารางของเครื่อง โมเดล เวลา และผลทดสอบ", IMG + "lab5-server.png", c5))
    add(fig("หน้า Instances ระหว่างที่ AI server ทำงาน: VRAM เกือบเต็มเป็นเรื่องปกติ", IMG + "lab5-console.png", cap(hp, "lab5-console"),
            tag="ภาพหน้าจอจริง"))

    # ----- LAB 6
    h = "LAB 6 ·"
    pr = prompts_of(h)[0]
    c6 = cap(h, "lab6-test")
    name = lab_divider(6, next(b for b in sec(h) if b["t"] == "p")["lines"][0].split(" · ")[1], took(h, "lab6-test"))
    add(explain("LAB 6 · เปิดแชทบอทใน container แล้วทดสอบเหมือนลูกค้าจริง", IMG + "lab6-overview.png", plines(pr, r"^\d+\.\s*")))
    groups = collections.OrderedDict()
    for c in CASES:
        groups.setdefault(c["group"], []).append(c)
    add(S("ชุดทดสอบ %d เคส แบ่งเป็น %d กลุ่ม" % (len(CASES), len(groups)), cards([
        ("%s · %d เคส" % (g, len(cs)), "ตัวอย่าง: " + cs[0]["action"].split(" → ")[0]) for g, cs in groups.items()], 3)
        + note("รายการเคสทั้งหมด: [`chatbot/e2e/cases.json`](chatbot/e2e/cases.json) · โค้ดแชทบอทและชุดทดสอบเตรียมไว้ให้แล้วในโฟลเดอร์ `chatbot/`", "info"),
        cls="mid", tag="chatbot/e2e/cases.json"))
    add(pslides(pr, "LAB 6 · เปิดแชทบอทแล้วทดสอบ"))
    rr = read_result(h)
    add(E.check_slide("LAB 6", ["โฟลเดอร์ `chatbot_result/` มี `TEST_REPORT.md` · `results.json` · โฟลเดอร์ `gifs`",
                                "ตารางสรุปมีครบทุกเคส และบอกเคสที่ไม่ผ่านพร้อมเหตุผล",
                                "เปิด `chatbot_result/TEST_REPORT.md` แล้วเทียบคำตอบที่ควรได้กับคำตอบจริงทีละเคส",
                                "คำตอบไม่แสดงค่า key"], c6,
                      "คำตอบของโมเดลแต่ละรอบไม่เหมือนกันทุกตัวอักษร จำนวนเคสที่ผ่านของคุณอาจต่างจากของผู้สอน", "LAB 6 · " + E.plain(name)))
    add(S("ผลของรอบตัวอย่าง: คำตอบมีคำสำคัญครบทุกเคส", tiles([
        ("ผ่านเครื่องตรวจ", rx(r"ผ่าน (\d+/\d+)", rr[0]), rx(r"หมายถึง(.+?) ·", rr[0]).strip(), "ok"),
        ("เคสถามต่อเนื่องที่ผ่าน", rx(r"ทั้ง (\d+) เคส", rr[1]) + "<small> เคส</small>", rx(r"= (.+?) เช่น", rr[1]), "ok"),
        ("เวลาที่ใช้", rx(r"ประมาณ (\d+ นาที)", c6), "ผลอยู่ในโฟลเดอร์ `chatbot_result/`", "")])
        + note(rr[1]), cls="mid", tag="ผลของรอบตัวอย่าง"))
    add(shot("ผลที่ควรได้ของ LAB 6: ตารางของทุกเคส และคำตอบที่ควรดูซ้ำ", IMG + "lab6-test.png", c6))
    add(gif_slide(3, "เคส 3 · ถามราคา: บอทตอบรายการบริการพร้อมราคาจากฐานข้อมูล"))
    add(gif_slide(16, "เคส 16 · จองคิว: ให้ข้อมูลครบแล้วได้การ์ดจองสำเร็จ"))
    add(gif_slide(20, "เคส 20 · ถามต่อเนื่อง: บอทจำราคาเดิมแล้วคิดส่วนลดนักศึกษา"))
    found = [re.match(r"^(เคส \d+(?: และ \d+)?) (.*)$", x) for x in rr[3:]]
    add(S("ผ่านเครื่องตรวจไม่ได้แปลว่าคำตอบดีทั้งหมด: คนยังต้องเทียบกับ baseline",
          cards([(m.group(1), m.group(2), "warn") for m in found if m], 3) + note(CHECK_NOTE), cls="mid"))

    # ----- LAB 7
    h = "LAB 7 ·"
    pr = prompts_of(h)[0]
    must = next(b for b in sec(h) if b["t"] == "p")["lines"][0]
    name = lab_divider(7, must)
    add(explain("LAB 7 · ลบเครื่อง ปิดแชทบอท แล้วสรุปค่าใช้จ่าย", IMG + "lab7-overview.png", plines(pr, r"^\d+\.\s*"), post=note(must, "bad")))
    add(pslides(pr, "LAB 7 · ปิดทุกอย่าง"))
    rr, c7 = read_result(h), cap(h, "lab7-close")
    add(E.check_slide("LAB 7", [rr[0], "แชทบอทถูกปิดแล้ว", rr[2]], c7, VARY, "LAB 7 · " + E.plain(name)))
    add(S("เครื่องคิดเงินทุกนาที ลบแล้วจึงหยุดจ่าย", tiles([
        ("เครื่อง RTX 5090 เปิดอยู่", rx(r"เปิดอยู่ ([\d.]+) นาที", c7) + "<small> นาที</small>", "ตั้งแต่ LAB 5 ถึง LAB 7", ""),
        ("Vast.ai เรียกเก็บ", rx(r"เรียกเก็บ (\$[\d.]+)", c7), "ยอดของรอบตัวอย่าง", "ok"),
        ("เครื่องค้างในบัญชี", rx(r"บัญชี (\d+) เครื่อง", rr[0]), "ดูหน้า Instances อีกครั้งว่าว่าง", "ok")])
        + note(rr[1]), cls="mid", tag="ผลของรอบตัวอย่าง"))
    add(shot("ผลที่ควรได้ของ LAB 7: ไม่มีเครื่องค้าง และตารางค่าใช้จ่าย", IMG + "lab7-close.png", c7))

    # ===== สรุป
    h = "สรุป"
    CTX.update(kicker="", group="สรุป")
    add(E.divider("สรุป", "สิ่งที่ได้ และสิ่งที่ควรจำ", "<p>ผลของทุก LAB · ข้อควรจำ · แบบฝึกหัด</p>", IMG + "s04-summary.jpg"))
    CTX["kicker"] = "สรุป"
    add(tbl("ทั้งบทในตารางเดียว: ได้อะไร และจ่ายเท่าไร", table(h, "LAB"),
            post=note("ค่าใช้จ่ายเป็นของรอบตัวอย่าง · " + VARY, "info")))
    rem = ul_after(h, "**สิ่งที่ควรจำ**")
    add(fig("สิ่งที่ควรจำ %d ข้อ" % len(rem), IMG + "n02-remember.jpg", "แต่ละข้อมาจากผลของ LAB · รายละเอียดอยู่ในสไลด์ถัดไป"))
    add(points("สิ่งที่ควรจำ: ดูราคารวม เขียนเพดาน และ destroy ทุกครั้ง", rem, two=True))
    ex = plist(h)
    add(S("แบบฝึกหัด %d ข้อ: ทำซ้ำด้วยเงื่อนไขและข้อมูลของตัวเอง" % len(ex),
          cards([((k + 1, "แบบฝึกหัด"), x) for k, x in enumerate(ex)], 2)
          + note(warn, "bad"), cls="mid"))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบบท", "ทดลองเสร็จทุกครั้ง: `destroy` เท่านั้นที่หยุดจ่าย",
                  '<p>รายละเอียดเต็มของบทนี้: <a href="readme.md" target="_blank">readme.md</a></p>'
                  '<p>สูตรของ LAB 5: <a href="chatbot/NINFER_RECIPE.md" target="_blank">chatbot/NINFER_RECIPE.md</a> · '
                  'เคสทดสอบของ LAB 6: <a href="chatbot/e2e/cases.json" target="_blank">chatbot/e2e/cases.json</a></p>'))
    return E.SL


E.CSS += """
.fig.shot{display:block;position:relative;overflow:hidden;border-radius:12px;border:1px solid var(--line);background:#fff;box-shadow:0 6px 22px rgba(18,48,94,.16)}
.fig.shot img{display:block;width:100%;max-width:none;max-height:none;height:auto;border-radius:0;box-shadow:none}
.fig.shot .zoom{position:absolute;right:14px;bottom:12px;font-size:15px;font-weight:600;color:#fff;background:rgba(18,48,94,.88);border-radius:999px;padding:4px 14px;pointer-events:none}
.fig.shot::after{content:"";position:absolute;left:0;right:0;bottom:0;height:70px;background:linear-gradient(rgba(255,255,255,0),rgba(255,255,255,.95));pointer-events:none}
.pts{display:flex;flex-direction:column;gap:.5em}
.pts.two{display:grid;grid-template-columns:1fr 1fr;gap:.55em 20px}
.road .grid2{display:grid;grid-template-columns:1fr 1fr;gap:.5em}
.road .secbox span{font-size:.78em}
.cardx h4 code{overflow-wrap:anywhere}
"""

if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) > 2 and sys.argv[1] == "--prompts-md":
        boxes = ["> [!IMPORTANT]\n> ```text\n%s\n> ```\n" % "\n".join(("> " + l).rstrip() for l in b["text"].split("\n")) for b in all_prompts()]
        open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(boxes))
        print("wrote %d prompts -> %s" % (len(boxes), sys.argv[2]))
    else:
        E.write(build(), out=OUT, title=TITLE)
