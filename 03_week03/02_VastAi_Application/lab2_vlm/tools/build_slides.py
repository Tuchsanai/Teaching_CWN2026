#!/usr/bin/env python3
"""สร้างสไลด์ LAB2_VLM_Slides.html ของ LAB 2 · Fine-tune VLM อ่านใบเสร็จ แล้วต่อเข้าเว็บ

  python tools/make_crops.py              (ครั้งแรก หรือเมื่อภาพหน้าจอของ README เปลี่ยน)
  python tools/build_slides.py            (รันจากโฟลเดอร์ lab2_vlm)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · ภาพเป็นตัวอธิบาย ข้อความข้างภาพไม่เกิน 3-4 ข้อ · หัวข้อของสไลด์คือข้อความหลัก
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md

ที่มาของเนื้อหา
- ตาราง โค้ด และพรอมต์ของทุกขั้น: อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ตัวเลขผล: results/metrics.json และ results/skill_v0_run/eval/metrics.json · ตัวเลขอื่นอ่านจาก README.md
  (ข้อความที่ยกจาก README ผ่าน R() ถูกตรวจว่ามีอยู่ในหัวข้อนั้นจริง ถ้า README เปลี่ยน การสร้างจะหยุดพร้อมบอกจุด)
- ภาพบางส่วนของคำตอบจริง img/cNN-*.jpg: tools/make_crops.py (ตัดจากภาพเดิม ไม่แก้พิกเซล)
- ภาพอธิบายและภาพถ่ายใหม่: tools/slides_figures.py · เครื่องมือเรนเดอร์: tools/slides_engine.py (ไม่แก้)
- รูปแบบสไลด์เฉพาะของเด็คนี้ (ภาพใหญ่ + ข้อความสั้น · ข้อความบนภาพถ่าย · ภาพคู่ · แผนภาพตามสัดส่วน): ฟังก์ชันและ CSS ในไฟล์นี้
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, codes, para, CTX, add, note, fig, explain, tiles, cards, bars, tbl)
from slides_figures import FIGS

S = E.slide
SECS = E.load("README.md")
FIG = {f["img"]: f for f in FIGS}
OUT, TITLE = "LAB2_VLM_Slides.html", "LAB 2 · Fine-tune VLM อ่านใบเสร็จ · Slides"

M = json.loads(E.read("results/metrics.json"))
M9 = json.loads(E.read("results/skill_v0_run/eval/metrics.json"))
B, F, T = M["base"], M["fine_tuned"], M["training"]
NSTEP = 9

# ------------------------------------------------------------------ CSS เฉพาะเด็คนี้ (ต่อท้าย CSS ของ engine)
E.CSS += """
/* ภาพใหญ่ราว 2/3 ของสไลด์ + ข้อความสั้นด้านขวา */
.ex.big .fig{flex:2.4 1 0}
.ex.big .side{gap:.45em}
.ex.half .fig{flex:1.1 1 0}
.side .cap{text-align:left;font-size:.82em}
.side .lead2{font-size:1.02em;font-weight:600;color:var(--navy);line-height:1.45}
/* ตัวเลขใหญ่แบบเรียงลง (ข้างภาพหลักฐาน) */
.vt{background:#fff;border:1px solid var(--line);border-left:8px solid var(--navy);border-radius:12px;padding:.35em .8em .45em}
.vt.ok{border-left-color:var(--green)}.vt.bad{border-left-color:var(--red)}.vt.warn{border-left-color:var(--orange)}
.vt .num{font-size:1.75em;font-weight:700;line-height:1.15;color:var(--navy)}
.vt.ok .num{color:var(--green)}.vt.bad .num{color:var(--red)}
.vt .k{font-size:.82em;color:#2b3648;line-height:1.4}
/* ภาพคู่ ก่อน/หลัง */
.pair{flex:1 1 0;min-height:0;display:flex;gap:26px}
.pair .pc{flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:.4em}
.pair .pc .fig{flex:1 1 0;min-height:0}
.pair .pc .cap{font-size:.86em}
.pair .pc .hd3{font-weight:700;color:var(--navy);text-align:center}
.pair .pc.bad .hd3{color:var(--red)}.pair .pc.good .hd3{color:var(--green)}
/* ข้อความเดียวบนภาพถ่าย */
.slide.stmt{padding:0;background:#0d2447 center/cover no-repeat;color:#fff}
.stmt .band{position:absolute;left:0;right:0;bottom:0;padding:120px 96px 64px;
  background:linear-gradient(0deg,rgba(6,13,26,.94) 0%,rgba(6,13,26,.82) 55%,rgba(6,13,26,0) 100%)}
.stmt .kick{font-size:21px;font-weight:600;color:#8fe0dc;margin:0 0 10px}
.stmt .say{font-size:46px;font-weight:700;line-height:1.35;margin:0;max-width:1350px}
.stmt .say b{color:#ffd28a}
.stmt .sub2{font-size:24px;color:#d6e4fb;line-height:1.55;margin:16px 0 0;max-width:1350px}
/* ตำแหน่งของขั้นบนหน้าคั่น */
.divider .inner .small{margin-bottom:26px}
.prog{display:flex;gap:10px;margin-top:34px;align-items:center}
.prog span{width:46px;height:46px;border-radius:50%;border:2px solid rgba(255,255,255,.45);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:rgba(255,255,255,.6)}
.prog span.done{background:rgba(143,224,220,.25);border-color:#8fe0dc;color:#cdf3f1}
.prog span.on{background:#f08a24;border-color:#f08a24;color:#fff;transform:scale(1.18)}
.prog i{width:14px;height:2px;background:rgba(255,255,255,.35)}
.prog i.gap{width:34px;background:none;border-top:2px dashed rgba(255,255,255,.35);height:0}
/* แผนภาพตามสัดส่วนจริงของ q_proj */
.scale{flex:1 1 0;min-height:0;display:flex;gap:40px;align-items:center;justify-content:center}
.scale svg{height:100%;max-height:640px;width:auto;flex:0 1 auto}
.scale .side{flex:0 0 30%;display:flex;flex-direction:column;gap:.5em}
/* ภาพกว้างเต็มสไลด์ + แถวด้านล่าง */
.stk{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:.55em}
.stk .fig{flex:1 0 0;min-height:500px}
.stk .row{flex:none;display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:14px;align-items:stretch}
.stk .row>*{margin:0}
.stk .cap{flex:none;margin:0;font-size:.85em}
.stk.tight .row{font-size:.8em}
.stk.tight .stp{padding:.3em .7em}
/* ภาพ + โค้ด */
.ex.code .fig{flex:.75 1 0}
.ex.code .side{flex:1.25 1 0}
"""


# ------------------------------------------------------------------ ตัวช่วยอ่าน README
def sectext(prefix):
    return json.dumps(sec(prefix), ensure_ascii=False)


def R(prefix, *texts):
    """คืนข้อความเดิม หลังตรวจว่าทุกข้อความอยู่ในหัวข้อ prefix ของ README จริง (กันตัวเลขที่ไม่มีที่มา)"""
    st = sectext(prefix)
    for t in texts:
        if t not in st:
            raise KeyError("ไม่พบข้อความ %r ในหัวข้อ %r ของ README" % (t, prefix))
    return texts[0] if len(texts) == 1 else texts


def took(prefix):
    """คำบรรยายใต้ภาพหน้าจอของขั้น (*ใช้เวลา ...*)"""
    for b in walk(sec(prefix)):
        if b["t"] == "p" and b["lines"][0].startswith("*ใช้เวลา"):
            t = " ".join(b["lines"])
            return t[1:-1] if t.startswith("*") and t.endswith("*") else t
    raise KeyError("ไม่พบบรรทัดใช้เวลาในหัวข้อ %r" % prefix)


def minutes(prefix):
    return re.match(r"ใช้เวลา (\d+) นาที", took(prefix)).group(1)


def readpts(prefix):
    """รายการใต้ **อ่านผลอย่างไร** ของหัวข้อ"""
    bl = sec(prefix)
    for k, b in enumerate(bl):
        if b["t"] == "p" and b["lines"][0].strip() == "**อ่านผลอย่างไร**":
            return bl[k + 1]["items"]
    raise KeyError("ไม่พบ อ่านผลอย่างไร ในหัวข้อ %r" % prefix)


def bullets(prefix):
    return next(b for b in sec(prefix) if b["t"] == "ul")["items"]


def lead(prefix):
    """ย่อหน้าแรกใต้หัวข้อของขั้น (ขั้นนี้ทำอะไร)"""
    return next(b for b in sec(prefix) if b["t"] == "p")["lines"][0]


def strip_b(s):
    return s.replace("**", "")


def after_head(s):
    """ตัดหัวตัวหนาของรายการทฤษฎี (**ทำไมต้องใช้** ...) ออก"""
    return re.sub(r"^\*\*[^*]+\*\*\s*", "", s)


def pct(x):
    return "%.1f%%" % x


# ------------------------------------------------------------------ รูปแบบสไลด์ของเด็คนี้
def img(src, alt):
    return E.img_tag({"t": "img", "src": src, "alt": alt})


def stp(points):
    return "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(points))


def big(title, src, points, post="", tag=""):
    """ภาพราว 2/3 ของสไลด์ + ข้อความสั้นไม่เกิน 3-4 ข้อด้านขวา (ภาพอธิบาย ภาพผล ภาพตัวอย่าง)"""
    s = explain(title, src, points, post)
    s["body"] = s["body"].replace('<div class="ex">', '<div class="ex big">', 1)
    s["tag"] = tag
    return s


def vtiles(items):
    """ตัวเลขใหญ่เรียงลง · items = [(ตัวเลข, คำอธิบาย, โทน)]"""
    return "".join('<div class="vt %s"><div class="num">%s</div><div class="k">%s</div></div>' % (t, n, md(k)) for n, k, t in items)


def evidence(title, crop, full, side, tag=""):
    """ส่วนหนึ่งของคำตอบจริง (ภาพที่ตัดมา ไม่กว้างมาก) ด้านซ้าย + ตัวเลขหรือข้อสังเกตด้านขวา"""
    body = ('<div class="ex big"><div class="fig">%s</div><div class="side fitbox">%s'
            '<p class="cap">ส่วนหนึ่งของคำตอบจริง · <a href="%s" target="_blank">ภาพเต็ม</a></p></div></div>') % (img(crop, E.plain(title)), side, full)
    return S(title, body, tag=tag, maxfs=1.25)


def vt1(num, k, tone=""):
    return vtiles([(num, k, tone)])


def pt1(n, text):
    return '<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (n, md(text))


def stacked(title, crop, cells, cap="", full="", tag="", tight=False):
    """ภาพกว้าง (ส่วนหนึ่งของคำตอบจริง หรือภาพผล) เต็มความกว้างสไลด์ + แถวตัวเลขหรือข้อสังเกตด้านล่าง"""
    if full:
        cap = (cap + " · " if cap else "") + 'ส่วนหนึ่งของคำตอบจริง · [ภาพเต็ม](%s)' % full
    body = '<div class="stk%s"><div class="fig">%s</div><div class="row" style="--n:%d">%s</div>%s</div>' % (
        " tight" if tight else "", img(crop, E.plain(title)), len(cells), "".join(cells), '<p class="cap">%s</p>' % md(cap) if cap else "")
    return S(title, body, tag=tag, maxfs=1.05)


def pair(title, a, b, post=""):
    """ภาพคู่ · a, b = (หัวเล็ก, ภาพ, คำบรรยาย, โทน "bad" | "good" | "")"""
    col = lambda d: '<div class="pc %s"><div class="hd3">%s</div><div class="fig">%s</div><p class="cap">%s</p></div>' % (
        d[3], md(d[0]), img(d[1], E.plain(d[0])), md(d[2]))
    return S(title, '<div class="pair">%s%s</div>%s' % (col(a), col(b), post), maxfs=1.15)


def statement(say, photo, kick="", sub=""):
    """ข้อความเดียวตัวใหญ่บนภาพถ่าย (ภาพจำลอง)"""
    style = ' style="background-image:url(%s)"' % photo if E.photo(photo) else ""
    raw = ('<div class="band">%s<p class="say">%s</p>%s</div>%s') % (
        '<p class="kick">%s</p>' % md(kick) if kick else "", md(say), '<p class="sub2">%s</p>' % md(sub) if sub else "",
        '<div class="imgnote">ภาพจำลอง</div>' if style else "")
    return {"raw": raw, "cls": "stmt", "style": style, "title": E.plain(say)[:90], "kicker": "", "tag": "", "lead": ""}


def progress(n):
    out = []
    for k in range(1, NSTEP + 1):
        if k > 1:
            out.append('<i class="gap"></i>' if k == 8 else "<i></i>")
        out.append('<span class="%s">%d</span>' % ("on" if k == n else "done" if k < n else "", k))
    return '<div class="prog">%s</div>' % "".join(out)


def first(*srcs):
    return next((s for s in srcs if os.path.exists(s)), srcs[-1])


# ------------------------------------------------------------------ 1 ขั้นของ LAB (ลำดับคงที่)
STEP_PHOTO = {1: "img/p23-rent.jpg", 2: "img/p22-receipts.jpg", 3: "img/p24-train.jpg", 4: "img/s02-lab.jpg",
              5: "img/p25-eval.jpg", 6: "img/p26-web.jpg", 7: "img/p27-off.jpg", 8: "img/p28-skill.jpg", 9: "img/p28-skill.jpg"}


def step(n, prefix, name, result_sub, picture, checks, ref, results, k=0):
    """หน้าคั่น (ขั้นที่ n จาก 9) → ภาพของขั้น → พรอมต์ → ตรวจผล → ผลจริงและการอ่านผล"""
    part = "ขั้นที่ %d จาก %d · %s" % (n, NSTEP, "การทดลอง" if n <= 7 else "เก็บงานเป็นสกิล")
    add(E.divider("ขั้นที่ %d" % n, name, "<p>%s</p><p>ใช้เวลาจริง %s นาที · %s</p>%s" % (md(lead(prefix)), minutes(prefix), md(result_sub), progress(n)),
                  first(STEP_PHOTO[n], "img/s02-lab.jpg"), small=part))
    add(picture)
    add(E.prompt_slides(E.prompt_code(prefix, k), CTX["kicker"], "ขั้นที่ %d · %s" % (n, name)))
    add(E.check_slide("step%d" % n, checks, "ผลของผู้สอน: " + ref,
                      "ตัวเลขและถ้อยคำในคำตอบของคุณอาจต่างจากของผู้สอนได้ เพราะ AI เขียนโค้ดและเลือกเครื่องเองในแต่ละรอบ "
                      "ให้ตรวจว่าครบตามรายการ", "ขั้นที่ %d · %s" % (n, name)))
    for s in results:
        add(s)


def begin(n, name):
    """ตั้งหัวเล็กและกลุ่มในสารบัญของขั้น · เรียกก่อนสร้างสไลด์ของขั้นนั้น"""
    CTX.update(kicker="ภาค LAB · ขั้นที่ %d จาก %d · %s" % (n, NSTEP, name), group="ขั้นที่ %d · %s" % (n, name))


def nsteps(key):
    return FIG[key]["steps"]


def qproj_svg(qr):
    """W (2,048 × 2,048) เทียบ A (8 × 2,048) และ B (2,048 × 8) วาดตามสัดส่วนจริง · ความหนาของ A และ B ขยายเป็น 4 px ให้มองเห็น"""
    side = 420.0
    thin = max(4.0, side * 8 / 2048)
    w0, a0 = 60, 60 + side + 120
    return ('<svg viewBox="0 0 1000 720" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans Thai, sans-serif">'
            '<rect x="%d" y="90" width="%d" height="%d" rx="6" fill="#dfe6f1" stroke="#12305e" stroke-width="3"/>'
            '<text x="%d" y="290" text-anchor="middle" font-size="40" font-weight="700" fill="#12305e">W (Frozen)</text>'
            '<text x="%d" y="340" text-anchor="middle" font-size="26" fill="#12305e">%s</text>'
            '<text x="%d" y="390" text-anchor="middle" font-size="30" font-weight="700" fill="#12305e">%s ตัว</text>'
            '<rect x="%d" y="120" width="%d" height="%.1f" fill="#f08a24"/>'
            '<text x="%d" y="110" font-size="28" font-weight="700" fill="#b85d00">A (เทรน) %s · %s ตัว</text>'
            '<rect x="%d" y="200" width="%.1f" height="%d" fill="#f08a24"/>'
            '<text x="%d" y="240" font-size="28" font-weight="700" fill="#b85d00">B (เทรน)</text>'
            '<text x="%d" y="280" font-size="26" fill="#b85d00">%s · %s ตัว</text>'
            '<text x="%d" y="700" font-size="22" fill="#5b6b82">วาดตามสัดส่วนจริงของขนาดเมทริกซ์ · ความหนาของ A และ B ขยายเป็น %d px เพื่อให้มองเห็น</text>'
            '</svg>') % (w0, side, side, w0 + side / 2, w0 + side / 2, qr["W เดิม (Frozen)"][1], w0 + side / 2, qr["W เดิม (Frozen)"][2],
                         a0, side, thin, a0, qr["A (เทรน)"][1], qr["A (เทรน)"][2],
                         a0, thin, side, a0 + 26, a0 + 26, qr["B (เทรน)"][1], qr["B (เทรน)"][2], w0, thin)


def build():
    # ===== 1 · เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    title = SECS[0]["text"].split("·", 1)
    add(E.cover("Fine-tune VLM อ่านใบเสร็จ", title[1].split("อ่านใบเสร็จ")[1].strip() + "สมุดรายจ่าย · LoRA จากใบเสร็จ 800 ใบ บน RTX 4090 เครื่องเดียว",
                first("img/s01-cover.jpg", "../image/cover.jpg"), small="03_week03 · 02_VastAi_Application · " + title[0].strip()))
    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("LoRA Adapter ขนาด %s MB ทำให้ยอดรวมตรงจาก %s เป็น %s และ Item F1 จาก %s เป็น %s" % (
        T["adapter_size_mb"], pct(B["total_exact_pct"]), pct(F["total_exact_pct"]), pct(B["item_f1_pct"]), pct(F["item_f1_pct"])),
        "results/eval/images/base_vs_ft.png",
        "ให้เทียบแท่งสีน้ำเงิน (Fine-tuned) กับแท่งสีเทา (Base) ในแต่ละตัวชี้วัด · Test Set 100 ใบ · ที่มา `results/metrics.json`"))
    add(fig("บทนี้มี 3 ส่วน และ LAB ทั้ง 9 ขั้นใช้พรอมต์ขั้นละ 1 อัน", first("img/n21-plan.jpg", "image/lab2-overview.png"),
            R("ทำไปเพื่ออะไร", "LAB นี้มี **9 ขั้น** (7 ขั้นของการทดลอง + 2 ขั้นเก็บงานเป็นสกิล)") + " โค้ดทุกไฟล์ AI เขียนจากพรอมต์ โดยเริ่มจากโฟลเดอร์ว่าง"))
    add(S("วิธีใช้สไลด์นี้", cards([
        ("ไปหน้าถัดไป / ก่อนหน้า", '<p><span class="kbd">→</span> <span class="kbd">Space</span> / <span class="kbd">←</span> หรือปุ่มมุมขวาล่าง</p>'),
        ("สารบัญทุกหน้า", '<p><span class="kbd">O</span> แล้วคลิกหน้าที่ต้องการ · <span class="kbd">F</span> เต็มจอ</p>'),
        ("ขยายภาพ", "คลิกที่ภาพ · คลิกอีกครั้งหรือ Esc เพื่อปิด"),
        ("คัดลอกพรอมต์ของแต่ละขั้น", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** ให้ข้อความเดียวกับ `README.md` ตรงตัวอักษร แม้พรอมต์ถูกแบ่งแสดง 2 หน้า", "warn"),
        ("ตรวจผลหลังรัน", "สไลด์ **ตรวจผลของคุณ** ต่อจากพรอมต์ทุกขั้น ติ๊กได้ และเบราว์เซอร์นี้จะจำไว้", "warn"),
        ("เปิดไฟล์จริง", "ลิงก์เปิดไฟล์ในโฟลเดอร์ของบท ให้เปิดสไลด์จากโฟลเดอร์ `lab2_vlm`"),
    ]), cls="mid"))

    # ===== 2 · พื้นฐาน
    CTX.update(kicker="", group="พื้นฐาน")
    add(E.divider("พื้นฐาน", "ปัญหา ข้อมูล โมเดล และทฤษฎี 5 ข้อ", "<p>สิ่งที่ต้องเข้าใจก่อนเริ่ม LAB: ร้านค้าต้องการอะไร ใช้ข้อมูลชุดใด ใช้โมเดลใด และ LoRA ทำงานอย่างไร</p>"))
    CTX.update(kicker="พื้นฐาน · ปัญหาและ Dataset", group="พื้นฐาน · ปัญหาและ Dataset")
    add(statement(para("ทำไปเพื่ออะไร", "ร้านค้ามีใบเสร็จ")["lines"][0], "img/p21-shop.jpg", kick="ปัญหาของร้านค้า"))
    q = para("ทำไปเพื่ออะไร", "คำถามของการทดลอง")["lines"][0].replace("คำถามของการทดลอง: ", "")
    add(fig("เป้าหมายคือถ่ายรูปใบเสร็จ แล้วให้ VLM อ่านลงสมุดรายจ่ายแทนการพิมพ์เอง", "image/why4-vlm.png", "คำถามของการทดลอง: " + q))

    ds = table("รู้จัก Dataset", "หัวข้อ")
    label = codes("รู้จัก Dataset", "json")[0]["text"]
    side = (E.pre_html(label, "json") + '<p class="cap">%s</p><p class="cap">%s · ผู้จัดทำ %s · สัญญาอนุญาต %s · ภาพตัวอย่าง 6 ใบ: '
            '<a href="results/dataset_samples.jpg" target="_blank">results/dataset_samples.jpg</a></p>') % (
        md(para("รู้จัก Dataset", "**label 1 รายการ**")["lines"][0]), md(strip_b(ds["rows"][0][1]).split("·")[0].strip()),
        md(ds["rows"][1][1]), ds["rows"][3][1])
    add(S("CORD-v2 คือรูปถ่ายใบเสร็จจริง และทุกใบมีเฉลยเป็น JSON เช่นใบ train_234",
          '<div class="ex code"><div class="fig">%s</div><div class="side fitbox">%s</div></div>' % (img("img/c13-train234.jpg", "ใบเสร็จ train_234"), side),
          tag="results/dataset_samples.jpg", maxfs=1.25))
    sp = {r[0]: r for r in table("รู้จัก Dataset", "ชุด")["rows"]}
    add(big("Dataset แบ่งเป็น 3 ชุดตามที่ผู้จัดทำให้มา และแต่ละชุดมีหน้าที่ต่างกัน", "img/n02-data-split.jpg",
            ["**%s** %s ใบ (%s รายการสินค้า) ใช้%s" % (k, sp[k][1], sp[k][2], sp[k][3]) for k in ("Training Set", "Validation Set", "Test Set")]))
    lab_rows = {E.plain(r[0]): r for r in table("รู้จัก Dataset", "ช่อง")["rows"]}
    add(big(R("รู้จัก Dataset", "กติกาในคอลัมน์ขวาคือสิ่งที่โมเดลสำเร็จรูปยังไม่รู้ และเป็นสิ่งที่ LAB นี้จะสอนเพิ่ม"), "img/n01-label-rules.jpg",
            ["`price` คือ" + strip_b(lab_rows["price"][1]) + " เป็นจำนวนเต็ม (\"12,000\" → 12000)",
             "ใบไม่พิมพ์จำนวน = `qty` 1 · ใบไม่พิมพ์ subtotal หรือ tax = `null`",
             "`total` ของ" + strip_b(lab_rows["total"][2]).replace("ใบนี้คือ", "ใบ `train_234` คือ")]))

    CTX.update(kicker="พื้นฐาน · โมเดล", group="พื้นฐาน · โมเดล")
    mt = {E.plain(r[0]): r[1] for r in table("รู้จักโมเดลที่ใช้", "หัวข้อ")["rows"]}
    add(fig("Qwen3-VL-2B-Instruct รับภาพและคำสั่ง แล้วตอบเป็นข้อความ ซึ่ง LAB นี้สั่งให้เป็น JSON", "image/model-qwen3vl.png",
            "%s · %s" % (mt["ขนาด"], mt["ใน LAB นี้"])))

    CTX.update(kicker="พื้นฐาน · ทฤษฎีข้อ 1 จาก 5", group="พื้นฐาน · ทฤษฎี")
    b1 = bullets("1 · VLM")
    add(big("VLM รับภาพและข้อความพร้อมกัน แล้วเขียนคำตอบเป็นข้อความทีละ token", "image/t4-vlm.png", [after_head(x) for x in b1[1:]]))
    CTX["kicker"] = "พื้นฐาน · ทฤษฎีข้อ 2 จาก 5"
    b2 = bullets("2 · Structured")
    add(big("Structured Output กำหนดให้โมเดลตอบเป็นช่องที่แน่นอน จึงให้คะแนนด้วยโปรแกรมได้", "image/t4-structured.png", [after_head(x) for x in b2[1:]]))
    mt2 = {E.plain(r[0]).split(" (")[0]: r for r in table("2 · Structured", "ตัวชี้วัด")["rows"]}
    add(big("ผลของการทดลองตัดสินด้วยตัวชี้วัด 3 ตัว ซึ่งโปรแกรมคำนวณได้เองทุกใบ", first("img/n22-metrics.jpg", "image/t4-structured.png"), [
        "**JSON Validity** คือคำตอบอ่านเป็น JSON ได้กี่ % · ใน LAB นี้ได้ " + mt2["JSON Validity"][2],
        "**Exact Match ของยอดรวม** นับว่าถูกเมื่อ `total` ตรงเฉลยทุกหลัก เช่น " + mt2["Exact Match ของยอดรวม"][2],
        "**Item F1** นับรายการว่าถูกเมื่อชื่อและราคาตรงเฉลย · " + mt2["Item F1"][2]]))

    CTX["kicker"] = "พื้นฐาน · ทฤษฎีข้อ 3 จาก 5 · แนวคิดหลักของ LAB"
    lt = {E.plain(r[0]): r for r in table("3 · LoRA", "")["rows"]}
    add(big("LoRA แช่แข็งน้ำหนักเดิมทั้งหมด แล้วเทรนเฉพาะเมทริกซ์เล็กที่เพิ่มเข้าไป", "image/lora-why.png", [
        "Full Fine-tuning ปรับ parameter ทั้ง %s ตัว ส่วน LoRA ปรับเพียง %s" % (strip_b(lt["parameter ที่ถูกปรับ"][1]).replace("ทั้ง ", ""), strip_b(lt["parameter ที่ถูกปรับ"][2])),
        "ผลที่ได้คือไฟล์ **LoRA Adapter** ซึ่งใช้คู่กับโมเดลเดิม โมเดลเดิม" + strip_b(lt["โมเดลเดิม"][2]),
        "หลายงานบน server เดียว: " + lt["หลายงานบน server เดียว"][2]]))
    cfg = {E.plain(r[0]): r for r in table("3 · LoRA", "ค่าที่ตั้งในขั้นที่ 3")["rows"]}
    add(big("ข้อมูลวิ่งสองทาง ผ่าน W เดิมทางหนึ่ง และผ่าน A กับ B ที่เทรนอีกทางหนึ่ง แล้วนำผลมารวมกัน", "image/lora-how.png", [
        R("3 · LoRA", "ตอนเทรน `W` ไม่ขยับ มีแต่ `A` กับ `B` ที่ถูกปรับ"),
        R("3 · LoRA", "เริ่มต้น `B = 0` โมเดลจึงตอบเหมือนเดิมก่อนเทรน"),
        "Rank `r` = %s และ Alpha `α` = %s · ใส่ที่%s ไม่แตะ %s" % (cfg["Rank r"][1], cfg["Alpha α"][1], cfg["ชั้นที่ใส่"][1].replace("ชั้น Linear ของ Language Model: ", "ชั้น Linear ของ Language Model "), cfg["ชั้นที่ไม่แตะ"][1])]))
    q = None
    for t in (b for b in walk(sec("3 · LoRA")) if b["t"] == "table"):
        if E.plain(t["head"][1]) == "ขนาด":
            q = t
    qr = {E.plain(r[0]): r for r in q["rows"]}
    tot = strip_b(qr["ส่วนที่เทรนของชั้นนี้"][2]).split(" = ")
    add(S("ในชั้น q_proj ส่วนที่เทรนมีเพียง %s ตัว คิดเป็น %s" % (tot[0], tot[1].replace("`", "")),
          '<div class="scale">%s<div class="side">%s</div></div>' % (qproj_svg(qr), stp([
              R("3 · LoRA", "ตัวอย่างจริง 1 ชั้นจากไฟล์ Adapter ของ LAB นี้ (`q_proj` ของ Language Model)"),
              "`A` และ `B` มีขนาดเพียง 8 แถวหรือ 8 คอลัมน์ ตาม Rank `r` = 8",
              "ส่วนที่เทรนของชั้นนี้ %s ตัว = %s" % (tot[0], tot[1])])), tag="results/adapter/", maxfs=1.25))
    res = next(b for b in sec("3 · LoRA") if b["t"] == "ul" and "34.9 MB" in b["items"][0])["items"]
    add(fig("Adapter ที่ได้มีขนาด 34.9 MB เล็กกว่าโมเดลเดิมราว 115 เท่า", "image/lora-result.png", res[0]))
    add(big("LoRA ไม่ได้สอนให้โมเดลอ่านออก แต่สอนกติกาของงาน", first("img/n23-lora-rules.jpg", "img/n01-label-rules.jpg"), [res[1], res[2]]))

    CTX["kicker"] = "พื้นฐาน · ทฤษฎีข้อ 4 จาก 5"
    b4 = bullets("4 · Training")
    add(big("validation loss ยังลดลงใน Epoch ที่ 2 แสดงว่ายังไม่เกิด Overfitting", "results/train/loss_curve.png",
            [after_head(b4[1]), after_head(b4[2]), after_head(b4[3]) + " (จุดสีแดงในกราฟ)"]))
    CTX["kicker"] = "พื้นฐาน · ทฤษฎีข้อ 5 จาก 5"
    b5 = bullets("5 · ระบบ")
    add(big("เว็บอยู่บนเครื่องของเรา ส่วน Base และ LoRA อยู่บน AI server เดียวบนเครื่องเช่า", "image/lab2-system.png", [after_head(x) for x in b5[1:]]))

    CTX["kicker"] = "พื้นฐาน · การทดลอง"
    ex = {E.plain(r[0]): r[1] for r in table("การทดลอง", "หัวข้อ")["rows"]}
    add(big("การทดลองเทียบ Base กับ Fine-tuned โดยให้ทุกอย่างอื่นเหมือนกัน", "img/n03-ab-setup.jpg", [
        ex["เทียบ A กับ B"], "วัดผลบน " + ex["วิธีวัด"], "%s · %s" % (ex["เครื่อง"], ex["เวลาและค่าเช่าจริง"])], tag="README · การทดลอง"))

    # ===== 3 · ภาค LAB
    CTX.update(kicker="ภาค LAB", group="ภาค LAB")
    add(E.divider("ภาค LAB", "9 ขั้น ขั้นละ 1 พรอมต์", "<p>%s</p>%s" % (md(R("ทำไปเพื่ออะไร", "โค้ดทุกไฟล์ AI เขียนให้จากพรอมต์ เริ่มจากโฟลเดอร์ว่าง")), progress(0)),
                  "img/s02-lab.jpg"))
    add(fig("ขั้นที่ 1–7 คือการทดลอง และขั้นที่ 8–9 เก็บงานทั้งหมดเป็นสกิล", "image/lab2-overview.png",
            para("การทดลอง", "ทำตามลำดับ")["lines"][0]))
    top = SECS[0]["blocks"][0]["lines"][0]
    assert "02_VastAi_Application" in top and "LAB 0" in top
    add(big("ก่อนเริ่มต้องทำ LAB 0 และเปิด Claude Code ที่โฟลเดอร์ของบท", first("img/n24-before.jpg", "image/lab2-overview.png"), [
        "ทำ [LAB 0](../README.md#lab-0--เตรียม-key-3-ตัว) ให้มี key 3 ตัว · `HF_TOKEN` อยู่ในไฟล์ `.env` ของโฟลเดอร์ปัจจุบัน และห้ามแสดงค่า",
        "เปิด Claude Code ที่โฟลเดอร์ " + R("LAB 2", "`02_VastAi_Application`") + " · ทุกพรอมต์เริ่มด้วยบรรทัด container `multi-account` และสกิล `vastai`",
        "ทำขั้นที่ 1 → 7 ให้จบในรอบเดียว เพราะเงินเริ่มเดินตั้งแต่ขั้นที่ 1 จนกว่าจะลบเครื่องในขั้นที่ 7",
        "โค้ดที่ AI เขียนอยู่ใน `lab2_vlm/code` ซึ่งเริ่มจากว่าง · โค้ดจากรอบจริงอยู่ใน [code_reference/](code_reference/) ไว้เทียบ"]))

    # ----- ขั้นที่ 1
    p1 = "ขั้นที่ 1"
    rp1 = readpts(p1)
    begin(1, "เช่าเครื่อง GPU")
    step(1, p1, "เช่าเครื่อง GPU", R(p1, "RTX 4090 ที่แคนาดา ราคา $0.398 ต่อชั่วโมง"),
         big("AI ค้นหาและเช่าเครื่อง แล้วทดสอบความเร็วโหลดก่อนใช้จริง", "img/n04-step1-rent.jpg", nsteps("n04-step1-rent")),
         ["ได้เครื่อง RTX 4090 1 ใบ ป้าย `vapp-lab2` ราคารวมไม่เกิน $0.80 ต่อชั่วโมง",
          "เครื่องเปิดพอร์ต 8000 · image PyTorch ที่มี CUDA 12.8 · disk 60 GB",
          "มีผลทดสอบโหลดจาก Hugging Face ไม่ช้ากว่า 20 MB/s (เครื่องที่ช้ากว่าถูกลบแล้ว)",
          "คำตอบเป็นตารางภาษาไทย: GPU · ราคาต่อชั่วโมง · ประเทศ · ความเร็วโหลด · เวลาที่รอจนเครื่องพร้อม",
          "AI บอกว่าเครื่องยังเปิดอยู่"],
         "เครื่องแรก%s จึงลบทิ้ง · เครื่องที่สองเป็น%s โหลดได้ %s พร้อมใน %s" % R(p1, "ที่โปแลนด์ราคา $0.382 โหลดจาก Hugging Face ได้ 0.84 MB/s",
                                                                                   "RTX 4090 ที่แคนาดา ราคา $0.398 ต่อชั่วโมง", "49–72 MB/s", "56 วินาที"),
         [stacked("เครื่องแรกโหลดได้เพียง 0.84 MB/s จึงถูกลบ ส่วนเครื่องที่ใช้โหลดได้ 49–72 MB/s", "img/c01-step1-table.jpg", [
                   vt1("0.84 MB/s", "เครื่องแรก (ลบทิ้ง) · โมเดล 4 GB จะใช้เวลาเกิน 1 ชั่วโมง · ถูกคิด **$0.047**", "bad"),
                   vt1(R(p1, "49–72 MB/s"), "เครื่องที่ใช้ · RTX 4090 · แคนาดา · $0.398 ต่อชั่วโมง", "ok"),
                   vt1("56 วินาที", "เวลาที่รอจนเครื่องที่ใช้พร้อม")], full="image/lab2-step1.png", tag=took(p1).split("·")[0].strip()),
          big("ราคาต่อชั่วโมงยังไม่ใช่ต้นทุนทั้งหมดของการเช่าเครื่อง", first("img/n25-step1-cost.jpg", "img/n04-step1-rent.jpg"), rp1)])

    # ----- ขั้นที่ 2
    p2 = "ขั้นที่ 2"
    rp2 = readpts(p2)
    begin(2, "เตรียมเครื่องและ Dataset ใบเสร็จ")
    step(2, p2, "เตรียมเครื่องและ Dataset ใบเสร็จ", "Training 800 · Validation 100 · Test 100 ใบ",
         big("สคริปต์ receipt_data.py แปลงเฉลยเป็น JSON และเก็บ Prompt ชุดเดียวที่ทุกขั้นใช้ร่วมกัน", first("img/n26-step2-data.jpg", "img/c13-train234.jpg"), [
             "**ติดตั้ง** vllm peft datasets matplotlib บนเครื่องเช่า แล้วโหลด Qwen3-VL-2B-Instruct",
             "**โหลด** CORD-v2 ตั้งชื่อใบตามชุดและลำดับ (เช่น `test_020`) และย่อภาพด้านยาวไม่เกิน 1280 px",
             "**แปลงเฉลย** เป็น JSON และเก็บ **ข้อความสั่งโมเดล** ชุดเดียว ใช้ทั้งตอนเทรน ตอนวัดผล และในเว็บ",
             "**ทำภาพตัวอย่าง** 6 ใบคู่กับ JSON เฉลย → `results/dataset_samples.jpg`"]),
         ["ได้ Training Set 800 · Validation Set 100 · Test Set 100 ใบ",
          "มีไฟล์ `lab2_vlm/code/receipt_data.py` ที่เก็บข้อความสั่งโมเดลภาษาอังกฤษ",
          "มีภาพ `lab2_vlm/results/dataset_samples.jpg`: ใบเสร็จ 6 ใบคู่กับ JSON เฉลย",
          "คำตอบยกเฉลย JSON 1 ใบ และอธิบายทีละช่อง",
          "ไม่มีการแสดงค่า `HF_TOKEN` และไม่มี token เหลือบนเครื่องเช่า · AI บอกว่าเครื่องยังเปิดอยู่"],
         "%s · %s" % R(p2, "เตรียมภาพ 1,000 ใบใน 54 วินาที", "Training Set 800 ใบ 2,416 รายการ Validation Set 100 ใบ 270 รายการ Test Set 100 ใบ 287 รายการ"),
         [stacked("ได้ข้อมูล 800 / 100 / 100 ใบ และเฉลยของ test_020 แสดงว่า price คือยอดของบรรทัด", "img/c02-step2-split.jpg",
                  [pt1(1, rp2[1]), pt1(2, rp2[2]), pt1(3, rp2[3])], full="image/lab2-step2.png", tag=R(p2, "test_020"))])

    # ----- ขั้นที่ 3
    p3 = "ขั้นที่ 3"
    rp3 = readpts(p3)
    tr = {E.plain(r[0]): r[1] for r in table(p3, "หัวข้อ")["rows"]}
    begin(3, "Training: Fine-tune ด้วย LoRA")
    step(3, p3, "Training: Fine-tune ด้วย LoRA", "เทรน %s นาที · parameter ที่เทรน %s%%" % (T["train_time_min"], round(T["trainable_pct"], 2)),
         big("โมเดลเห็นใบเสร็จทีละใบ สะสม gradient 4 ใบ แล้วจึงปรับน้ำหนักของ LoRA 1 ครั้ง", first("img/n27-step3-accum.jpg", "image/lora-how.png"), [
             "**ใส่ LoRA** rank 8 (alpha 16) เฉพาะชั้น Linear ของส่วนภาษา ไม่แตะส่วนมองภาพ → `code/train.py`",
             "**เทรน** 800 ใบ 2 Epoch learning rate 0.0002 seed 0 · ป้อนทีละ 1 ใบ สะสม gradient 4 ใบ = 400 step",
             "**คิด loss** เฉพาะส่วนคำตอบ JSON · วัด validation loss ก่อนเทรนและหลังทุก Epoch",
             "**รันให้ทนการเชื่อมต่อหลุด** ด้วย `code/run_train.sh` แล้วเก็บ Adapter กราฟ loss และตัวเลขการเทรน"]),
         ["มี `lab2_vlm/code/train.py` และ `lab2_vlm/code/run_train.sh`",
          "คำตอบบอกจำนวน parameter ที่เทรนเทียบทั้งโมเดล (ควรอยู่ราว 0.41%)",
          "validation loss หลัง Epoch 2 ไม่สูงกว่าหลัง Epoch 1",
          "มีไฟล์ Adapter ใน `lab2_vlm/results/adapter/` และกราฟ loss ป้ายภาษาอังกฤษ",
          "คำตอบบอกเวลาเทรน · VRAM สูงสุด · ขนาดไฟล์ adapter · และว่าเครื่องยังเปิดอยู่"],
         "%s · validation loss %s · %s · VRAM %s · Adapter %s" % (strip_b(tr["parameter ที่เทรน"]), tr["validation loss"], tr["เวลาเทรน"],
                                                                 tr["VRAM สูงสุด"], tr["ไฟล์ Adapter"].split(" →")[0]),
         [stacked("เทรนเพียง 0.41% ของ parameter ใช้เวลา 9.2 นาที และได้ Adapter 34.9 MB", "img/c03-step3-table.jpg", [
                   vt1("%.2f%%" % T["trainable_pct"], "parameter ที่เทรน · {:,} จาก {:,}".format(T["trainable_params"], T["total_params"]), "ok"),
                   vt1("%.4f" % T["val_loss"]["epoch_2"], "validation loss หลัง Epoch 2 · จาก %.4f (ก่อนเทรน) → %.4f (Epoch 1)" % (
                       T["val_loss"]["epoch_0"], T["val_loss"]["epoch_1"]), "ok"),
                   vt1("%s GB" % T["peak_vram_gb"], "VRAM สูงสุด จาก 24 GB · เวลาเทรน %s นาที %d step" % (T["train_time_min"], T["optimizer_steps"])),
                   vt1("%s MB" % T["adapter_size_mb"], "ไฟล์ Adapter ใน `results/adapter/`")],
                  full="image/lab2-step3.png", tag="results/metrics.json"),
          big("loss ร่วงเร็วใน 20 step แรก เพราะโมเดลจับรูปแบบ JSON ได้เร็ว", "results/train/loss_curve.png", [rp3[0], rp3[2], rp3[3]])])

    # ----- ขั้นที่ 4
    p4 = "ขั้นที่ 4"
    rp4 = readpts(p4)
    begin(4, "เปิด AI server สองโมเดล")
    step(4, p4, "เปิด AI server สองโมเดล", "server พร้อมใน 167 วินาที · ทดสอบผ่าน 3 ข้อ",
         big("vLLM โหลดโมเดลเดิมครั้งเดียว แล้วให้บริการทั้ง receipt-base และ receipt-ft", first("img/n28-step4-serve.jpg", "image/lab2-system.png"), [
             "**เขียน** `code/serve.sh` เปิด AI server แบบ OpenAI-compatible ด้วย vLLM ที่พอร์ต 8000",
             "**2 โมเดลบน GPU ใบเดียว**: `receipt-base` (โมเดลเดิม) และ `receipt-ft` (โมเดลเดิม + LoRA adapter)",
             "**ใช้ API key** ที่สุ่มขึ้นและเก็บไว้บนเครื่องเช่าเท่านั้น",
             "**ทดสอบจากนอกเครื่อง 3 ข้อ** แล้วเขียน `code/receipt.env` ให้เว็บใช้"]),
         ["รายการโมเดลจากนอกเครื่องเห็นทั้ง `receipt-base` และ `receipt-ft`",
          "ส่งใบเสร็จจาก Test Set 1 ใบให้ `receipt-ft` พร้อม key แล้วได้ JSON กลับมา",
          "ส่งแบบไม่มี key แล้วถูกปฏิเสธ",
          "มีไฟล์ `lab2_vlm/code/receipt.env` ครบ 4 ค่า · คำตอบไม่แสดงค่า key",
          "คำตอบบอกเวลาที่ server ใช้เปิด และว่าเครื่องยังเปิดอยู่"],
         R(p4, "server เปิดใน 167 วินาที ทดสอบจากนอกเครื่องผ่าน 3 ข้อ เห็น receipt-base และ receipt-ft ส่งใบ test_020 พร้อม key ได้ JSON ใน 4.9 วินาที ส่งแบบไม่มี key ได้ 401"),
         [stacked("server พร้อมใน 167 วินาที และผ่านการทดสอบจากนอกเครื่องครบ 3 ข้อ", "img/c04-step4-tests.jpg", [
                   vt1("4.9 วินาที", "ส่ง `test_020` พร้อม key แล้วได้ JSON กลับมา", "ok"),
                   vt1("401", "ส่งแบบไม่มี key แล้วถูกปฏิเสธ", "ok"), pt1(1, rp4[2])],
                  full="image/lab2-step4.png", tag=R(p4, "167 วินาที")),
          ])
    add(statement(rp4[1] + " · " + rp4[3], "img/s02-lab.jpg", kick="ภาค LAB · ขั้นที่ 4 จาก 9 · ความปลอดภัยของ key", sub=rp4[0]))

    # ----- ขั้นที่ 5
    EXCAP = ('สีแดง = ไม่ตรงเฉลย · แต่ละแถว: ชื่อใบ | เฉลย (Ground truth) | Base | Fine-tuned · ส่วนหนึ่งของภาพผลจริง · '
             '[ภาพเต็ม](results/eval/images/examples.jpg)')
    p5 = "ขั้นที่ 5"
    rp5 = readpts(p5)
    begin(5, "Evaluation: Base เทียบ Fine-tuned บน Test Set")
    step(5, p5, "Evaluation: Base เทียบ Fine-tuned บน Test Set",
         "ยอดรวมตรง %s → %s · Item F1 %s → %s" % (pct(B["total_exact_pct"]), pct(F["total_exact_pct"]), pct(B["item_f1_pct"]), pct(F["item_f1_pct"])),
         big("ขั้นที่ 5 ส่ง Test Set ทีละใบให้ทั้งสองโมเดล แล้วให้คะแนนด้วยโปรแกรม", "img/n05-step5-eval.jpg", nsteps("n05-step5-eval")),
         ["มี `lab2_vlm/code/eval.py` และ `lab2_vlm/results/metrics.json`",
          "ทั้งสองโมเดลถูกวัดครบ 100 ใบ ด้วยข้อความสั่งเดียวกับตอนเทรน temperature 0",
          "มีกราฟแท่ง Base vs Fine-tuned และภาพตัวอย่าง 4 ใบ (สีแดง = ผิด) ข้อความภาษาอังกฤษ",
          "คำตอบเป็นตาราง Base vs Fine-tuned: JSON อ่านได้ · ยอดรวมตรง · Item F1 · วินาทีต่อใบ",
          "มีตัวอย่าง 2 ใบที่ Fine-tuned อ่านถูกแต่ Base อ่านผิด · ผล LoRA adapter และกราฟ loss กลับมาที่ `lab2_vlm/results`"],
         "JSON อ่านได้ %s / %s · ยอดรวมตรง %s / %s · Item F1 %s / %s · วินาทีต่อใบ %s / %s (Base / Fine-tuned) · ตัวอย่าง test_086 และ test_051" % (
             pct(B["json_readable_pct"]), pct(F["json_readable_pct"]), pct(B["total_exact_pct"]), pct(F["total_exact_pct"]),
             pct(B["item_f1_pct"]), pct(F["item_f1_pct"]), B["sec_per_receipt"], F["sec_per_receipt"]),
         [fig("Fine-tuned ดีกว่า Base ทั้งยอดรวมตรงและ Item F1 และยังตอบเร็วกว่า", "results/eval/images/base_vs_ft.png",
              "ยอดรวมวัดเฉพาะ %d ใบที่เฉลยมียอดรวม · กราฟขวา: วินาทีต่อใบ · %s" % (F["total_receipts_scored"], rp5[2])),
          S("ยอดรวมถูกครบ %d ใบ และรายการที่อ่านถูกเพิ่มขึ้น %d รายการ" % (F["total_receipts_scored"], F["items_correct"] - B["items_correct"]), tiles([
              ("JSON อ่านได้", pct(F["json_readable_pct"]), "Base %s · ต่าง %s" % (pct(B["json_readable_pct"]), M["improvement_points"]["json_readable_pct"]), ""),
              ("ยอดรวมตรงทุกหลัก", pct(F["total_exact_pct"]), "Base %s · **+%s จุด**" % (pct(B["total_exact_pct"]), M["improvement_points"]["total_exact_pct"]), "ok"),
              ("Item F1", pct(F["item_f1_pct"]), "Base %s · **+%s จุด**" % (pct(B["item_f1_pct"]), M["improvement_points"]["item_f1_pct"]), "ok"),
              ("รายการที่ถูก", "%d/%d" % (F["items_correct"], F["items_ground_truth"]), "Base %d · **+%d**" % (B["items_correct"], F["items_correct"] - B["items_correct"]), "ok"),
              ("วินาทีต่อใบ", "%s" % F["sec_per_receipt"], "Base %s · %s" % (B["sec_per_receipt"], R(p5, "เร็วขึ้น 26%")), "")])
            + note(rp5[1]), cls="mid", tag="results/metrics.json"),
          stacked("Base อ่านตัวอักษรออก แต่ผิดกติกาของงาน: test_040 หยิบราคาต่อหน่วย และ test_051 ตัดคำออกจากชื่อ", "img/c09-examples-a.jpg", [
              pt1(1, "test_040: Base หยิบราคาต่อหน่วย 27000 และ 7000 ยอดรวม 48000 · Fine-tuned ได้ยอดรวม 68000 ถูก"),
              pt1(2, "test_051: Base ตัด (TA) ออกจากชื่อทุกบรรทัดและตอบยอดรวม 334011 · Fine-tuned ถูก 3 จาก 4 รายการ ยอดรวม 334000 ถูก")],
              cap=EXCAP, tag="results/eval/images/examples.jpg", tight=True),
          stacked("test_086 เอายอด CASH เป็นยอดรวม และ test_091 นับบรรทัดเงินทอนเป็นสินค้า", "img/c10-examples-b.jpg", [
              pt1(1, "test_086: Base ตอบยอดรวม 52000 ซึ่งเป็นยอด CASH · Fine-tuned ตอบ 22000 ถูก"),
              pt1(2, "test_091: Base นับบรรทัด TL CASH CG เป็นสินค้า · Fine-tuned ถูกทั้งหมด"),
              pt1(3, rp5[3])],
              cap=EXCAP, tag="results/eval/images/examples.jpg", tight=True)])
    for t in ("Base หยิบราคาต่อหน่วย 27000 และ 7000 ยอดรวม 48000", "Fine-tuned ได้ยอดรวม 68000 ถูก", "Base ตัด (TA) ออกจากชื่อทุกบรรทัดและตอบยอดรวม 334011",
              "Fine-tuned ถูก 3 จาก 4 รายการ ยอดรวม 334000 ถูก", "Base ตอบยอดรวม 52000 ซึ่งเป็นยอด CASH", "Fine-tuned ตอบ 22000 ถูก",
              "Base นับบรรทัด TL CASH CG เป็นสินค้า", "Fine-tuned ถูกทั้งหมด"):
        R(p5, t)

    # ----- ขั้นที่ 6
    p6 = "ขั้นที่ 6"
    rp6 = readpts(p6)
    begin(6, "สร้างเว็บสมุดรายจ่ายแล้วทดสอบ")
    step(6, p6, "สร้างเว็บสมุดรายจ่ายแล้วทดสอบ", "ผ่านเว็บ Fine-tuned ได้ยอดรวมถูก 3 จาก 3 ใบ · Base ผิดทั้ง 3 ใบ",
         big("เว็บสมุดรายจ่ายอยู่บนเครื่องของเรา และเรียก AI server บนเครื่องเช่า", first("img/n29-step6-web.jpg", "results/web/web-compare-test092.png"), [
             "**เขียนเว็บ** Next.js + PostgreSQL ที่ `code/web` เปิดด้วย docker compose ที่ http://localhost:3404",
             "หน้า **อ่านใบเสร็จ**: อัปโหลดรูปหรือกดใบเสร็จตัวอย่าง → เลือก Base / Fine-tuned / เทียบสองโมเดล → บันทึกเป็นรายจ่าย",
             "**ใบเสร็จตัวอย่าง** 6 ใบจาก Test Set พร้อมเฉลย จึงขึ้น ✓/✗ ทีละบรรทัด · หน้า **รายจ่าย** แสดงจำนวนใบและรายจ่ายรวม",
             "key อยู่ฝั่ง server ของเว็บเท่านั้น · ใช้ข้อความสั่งโมเดลชุดเดียวกับ `receipt_data.py`"]),
         ["เปิด http://localhost:3404 ได้ เป็นหน้าเว็บภาษาไทย",
          "เลือกใบเสร็จตัวอย่างแล้วเห็น ✓/✗ เทียบเฉลยทีละบรรทัด และโหมดเทียบสองโมเดลทำงาน",
          "กดบันทึกเป็นรายจ่ายแล้ว หน้ารายจ่ายแสดงจำนวนใบ รายจ่ายรวม และลบได้",
          "คำตอบเป็นตาราง: ใบเสร็จ · โมเดล · รายการที่อ่านถูก · ยอดรวมถูกหรือผิด · เวลา สำหรับ test_092 test_051 test_020",
          "คำตอบไม่แสดงค่า key และบอกว่าเครื่องบน Vast.ai ยังเปิดอยู่"],
         R(p6, "test_092 Base ถูก 0 จาก 1 Fine-tuned ถูก 1 จาก 1, test_051 Base ถูก 0 จาก 4 Fine-tuned ถูก 3 จาก 4, test_020 ทั้งสองโมเดลถูก 3 จาก 5 ยอดรวม Base ผิดทั้ง 3 ใบ Fine-tuned ถูกทั้ง 3 ใบ ใช้เวลา 0.7 ถึง 1.9 วินาที"),
         [stacked("ผ่านเว็บ Fine-tuned ได้ยอดรวมถูกทั้ง 3 ใบ ส่วน Base ผิดทั้ง 3 ใบ", "img/c06-step6-table.jpg", [
                   pt1(1, rp6[0]),
                   pt1(2, R(p6, "test_092 Base ถูก 0 จาก 1 Fine-tuned ถูก 1 จาก 1, test_051 Base ถูก 0 จาก 4 Fine-tuned ถูก 3 จาก 4, test_020 ทั้งสองโมเดลถูก 3 จาก 5")
                       + " · " + R(p6, "ใช้เวลา 0.7 ถึง 1.9 วินาที"))], full="image/lab2-step6.png", tag="ผลขั้นที่ 6"),
          fig("ใบ test_092 ในโหมดเทียบสองโมเดล: Base นับเงินสดและเงินทอนเป็นสินค้า ส่วน Fine-tuned ถูกทั้งหมด", "results/web/web-compare-test092.png",
              "Base นับ CASH กับ CHANGE เป็นสินค้า ยอดรวม Rp 250.000 ผิด · Fine-tuned ได้ TICKET CP 4 ใบ ยอดรวม Rp 240.000 ถูก"),
          big("ใบ test_020 ทั้งสองโมเดลสะกดชื่อผิดเหมือนกัน ซึ่งเป็นข้อจำกัดของการมองภาพ", "results/web/web-compare-test020.gif", [rp6[1], rp6[2], rp6[3]]),
          pair("กดบันทึกเป็นรายจ่าย แล้วข้อมูลจะถูกเก็บใน PostgreSQL และแสดงในหน้ารายจ่าย",
               ("1 · บันทึกใบ test_051", "results/web/web-save.gif", "อ่านใบ test_051 กดบันทึกเป็นรายจ่าย แล้วเปิดหน้ารายจ่าย", ""),
               ("2 · หน้ารายจ่าย", "results/web/web-expenses.png",
                R(p6, "หน้ารายจ่าย: ใบเสร็จที่บันทึก 4 ใบ รายจ่ายรวม Rp 1.285.859 พร้อมตารางรายใบที่มีปุ่มดูรายการและลบ"), ""))])

    # ----- ขั้นที่ 7
    p7 = "ขั้นที่ 7"
    rp7 = readpts(p7)
    begin(7, "ลบเครื่องและสรุปค่าใช้จ่าย (ห้ามข้าม)")
    step(7, p7, "ลบเครื่องและสรุปค่าใช้จ่าย (ห้ามข้าม)", "ยอดรวมทั้ง LAB $0.58",
         big("ตรวจผลให้ครบก่อน แล้วจึงลบเครื่อง เพราะเงินเดินตลอดเวลาที่เครื่องเปิด", "img/n06-step7-destroy.jpg", nsteps("n06-step7-destroy")),
         ["ผลใน `lab2_vlm/results` ครบ: metrics.json กราฟ ภาพตัวอย่าง และ LoRA adapter",
          "ไม่มีเครื่องป้าย `vapp-lab2` เหลือในบัญชี (เปิดหน้า [Instances](https://cloud.vast.ai/instances/) ดูอีกครั้ง)",
          "ไม่มีเครื่องป้ายอื่นถูกแตะ",
          "เว็บปิดแล้ว แต่รายจ่ายที่บันทึกไว้ยังอยู่",
          "คำตอบบอกค่าใช้จ่ายจริง: อายุเครื่อง · ราคาต่อชั่วโมง · GPU · disk · รับส่งข้อมูล"],
         R(p7, "เครื่องเปิดอยู่ราว 1.24 ชั่วโมง ราคา $0.398 ต่อชั่วโมง GPU $0.476 disk $0.014 ดาวน์โหลด 14.5 GB $0.038 รวม $0.529") +
         " · " + took(p7).split("·", 1)[1].strip(),
         [stacked("ค่าเช่าทั้ง LAB คือ $0.58 และค่า GPU คือราว 90% ของบิล", "img/c07-step7-cost.jpg", [
                   vt1("$0.476", "GPU · เครื่องเปิดอยู่ราว 1.24 ชั่วโมง · disk $0.014 · ดาวน์โหลด 14.5 GB $0.038", "warn"),
                   vt1("$0.537", "ใบแจ้งหนี้ของ Vast.ai (คำตอบของ AI รวมได้ $0.529)"),
                   vt1("$0.58", "รวมเครื่องแรกที่ลบทิ้ง: $0.537 + $0.047", "ok")], full="image/lab2-step7.png", tag=R(p7, "$0.537")),
          statement(rp7[1], first("img/p29-meter.jpg", "img/s02-lab.jpg"), kick="ภาค LAB · ขั้นที่ 7 จาก 9", sub=rp7[2] + " · " + rp7[0])])

    # ----- ขั้นที่ 8-9 · สกิล
    CTX.update(kicker="ภาค LAB · ปิดท้าย", group="ปิดท้าย · สกิลเวอร์ชัน 0")
    add(fig("เก็บงาน 7 ขั้นที่สำเร็จแล้วเป็นสกิล เพื่อให้ทำซ้ำได้ในคำสั่งเดียว", "image/skill-v0.png",
            next(b for b in sec("ปิดท้าย") if b["t"] == "p")["lines"][0].split("·")[1].strip()))
    p8 = "ขั้นที่ 8"
    alert = next(b for b in sec(p8) if b["t"] == "alert")
    restart = " ".join(next(x for x in alert["blocks"] if x["t"] == "p")["lines"]).replace("⚠️", "").strip()
    begin(8, "สร้างสกิลเวอร์ชัน 0")
    step(8, p8, "สร้างสกิลเวอร์ชัน 0", "ไม่ต้องเช่าเครื่อง · ได้สกิล receipt-vlm-finetune",
         big("AI อ่านพรอมต์ โค้ด และผลของ LAB แล้วเขียน SKILL.md พร้อมโค้ดที่ใช้ได้จริง", first("img/n30-step8-skill.jpg", "image/skill-v0.png"), [
             "**ดูงานทั้งหมด** จาก `PROMPTS.md` โค้ดใน `lab2_vlm/code` และผลใน `lab2_vlm/results`",
             "**เขียน** `skill_v0/SKILL.md` ชื่อ `receipt-vlm-finetune`: ค่าที่ปรับได้ · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน",
             "**คัดลอกโค้ด** ที่ใช้ได้แล้วไปไว้ที่ `skill_v0/scripts` ไม่ต้องเขียนใหม่",
             "**เรียกใช้สกิล vastai** ต่อ แล้วติดตั้งเป็นสกิลของโปรเจกต์ที่ `.claude/skills/receipt-vlm-finetune`"]),
         ["มี `lab2_vlm/skill_v0/SKILL.md` ที่มี name และ description บอกว่าใช้เมื่อไร",
          "SKILL.md มีค่าที่ปรับได้พร้อมค่าเริ่มต้น · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน (ลบเครื่องเสมอ)",
          "มีโค้ดใน `lab2_vlm/skill_v0/scripts` (เตรียม Dataset เทรน เปิด server วัดผล)",
          "มีสกิลที่ `.claude/skills/receipt-vlm-finetune` ของโฟลเดอร์ปัจจุบัน",
          "ไม่มีการ commit"],
         R(p8, "สร้างสกิล receipt-vlm-finetune แล้ว ทำงาน 7 ขั้นได้ในคำสั่งเดียว มีเกณฑ์ตรวจผ่าน กติกาเรื่องเงิน ตารางค่าที่ปรับได้ เช่น epochs 2 lora_rank 8"),
         [stacked("สกิล receipt-vlm-finetune มีตารางค่าที่ปรับได้ เช่น epochs 2 และ lora_rank 8", "img/c08-step8-params.jpg", [
                   pt1(1, R(p8, "สร้างสกิล receipt-vlm-finetune แล้ว ทำงาน 7 ขั้นได้ในคำสั่งเดียว")
                       + " · สกิลที่ได้: [skill_v0/SKILL.md](skill_v0/SKILL.md) และโค้ดใน [skill_v0/scripts/](skill_v0/scripts/)"),
                   note("**ก่อนขั้นที่ 9:** " + restart, "warn")], full="image/lab2-step8.png")])

    p9 = "ขั้นที่ 9"
    rp9 = readpts(p9)
    cmp = table(p9, "")
    crow = {E.plain(r[0]): r for r in cmp["rows"]}
    f9, b9 = M9["fine_tuned"], M9["base"]
    begin(9, "ลองใช้สกิลทำซ้ำในคำสั่งเดียว")
    step(9, p9, "ลองใช้สกิลทำซ้ำในคำสั่งเดียว",
         "ยอดรวมตรง %s → %s · Item F1 %s → %s · ค่าเช่า %s" % (pct(b9["total_exact_pct"]), pct(f9["total_exact_pct"]), pct(b9["item_f1_pct"]),
                                                             pct(f9["item_f1_pct"]), strip_b(crow["ค่าเช่า"][2]).split(" (")[0]),
         big("ขั้นที่ 9 ใช้พรอมต์เดียวแทน 7 พรอมต์ และเทรนเพียง 1 Epoch", "image/skill-v0.png", [
             "**สั่งทีละขั้น (ขั้นที่ 1–7):** %s พรอมต์ · %s Epoch · เวลาทั้งหมด %s · ค่าเช่า %s" % (
                 strip_b(crow["จำนวนพรอมต์"][1]), crow["จำนวน Epoch"][1], crow["เวลาทั้งหมด"][1], crow["ค่าเช่า"][1]),
             "**สกิล v0:** %s พรอมต์ · %s Epoch · เวลาทั้งหมด %s · ค่าเช่า %s" % (
                 strip_b(crow["จำนวนพรอมต์"][2]), crow["จำนวน Epoch"][2], crow["เวลาทั้งหมด"][2], crow["ค่าเช่า"][2]),
             lead(p9)]),
         ["ได้ผลใน `lab2_vlm/results/skill_v0_run` และผลเดิมใน `lab2_vlm/results` ไม่ถูกเขียนทับ",
          "คำตอบบอกยอดรวมตรงและ Item F1 ก่อน vs หลังบน Test Set",
          "คำตอบบอกเวลาแต่ละขั้นและค่าใช้จ่ายจริง",
          "ไม่มีเครื่องป้าย `vapp-lab2-skill` เหลือในบัญชี",
          "AI ใช้โค้ดในสกิล ไม่เขียนใหม่ · ไม่มีการ commit"],
         "ยอดรวมตรง %s → %s · Item F1 %s → %s · %s" % (pct(b9["total_exact_pct"]), pct(f9["total_exact_pct"]), pct(b9["item_f1_pct"]), pct(f9["item_f1_pct"]),
                                                       R(p9, "เทรน 4.8 นาที เครื่องแรกเป็น RTX 4090 Laptop 16 GB จึงลบทิ้ง ลบเครื่องแล้ว ค่าใช้จ่ายจริง $0.228")),
         [fig("สกิล v0 กับ 1 Epoch ได้ยอดรวมตรง %s และ Item F1 %s" % (pct(f9["total_exact_pct"]), pct(f9["item_f1_pct"])),
              "results/skill_v0_run/eval/images/base_vs_ft.png",
              "ให้เทียบแท่งสีน้ำเงินกับรอบ 2 Epoch ของขั้นที่ 5 (%s และ %s) · Test Set 100 ใบ · ที่มา `results/skill_v0_run/eval/metrics.json`" % (
                  pct(F["total_exact_pct"]), pct(F["item_f1_pct"]))),
          stacked("สกิล v0 ทำงานผ่านในรอบแรก โดยไม่ต้องเขียนโค้ดใหม่ และค่าใช้จ่ายจริงคือ $0.228", "img/c11-step9-cost.jpg",
                  [pt1(1, rp9[0]), pt1(2, rp9[2]),
                   vt1("$0.228", R(p9, "เครื่องแรกเป็น RTX 4090 Laptop 16 GB จึงลบทิ้ง") + " · " + R(p9, "เทรน 4.8 นาที") + " · " + took(p9).split("·")[0].strip(), "warn")],
                  full="image/lab2-step9.png"),
          big("สกิล v0 ยังพลาด 4 จุดในรอบทดสอบ และต้องแก้ในเวอร์ชัน 1", first("img/n31-v0-issues.jpg", "image/skill-v0.png"),
              ["%s → **v1:** %s" % (r[0], r[1]) for r in table(p9, "จุดที่ v0 ยังพลาด")["rows"]], tag="README · ขั้นที่ 9")])

    # ===== 4 · สรุป
    CTX.update(kicker="สรุป", group="สรุป")
    add(E.divider("สรุป", "Adapter %s MB เปลี่ยนผลได้มากเพียงใด" % T["adapter_size_mb"], "<p>ผลรวม ตารางสรุป บทเรียน และข้อจำกัด</p>",
                  first("img/s01-cover.jpg", "img/s02-lab.jpg")))
    add(S("Fine-tune ทั้งสองรอบดีกว่า Base และรอบ 2 Epoch ดีกว่ารอบ 1 Epoch เล็กน้อย", bars([
        ("ยอดรวมตรง · Base", "", B["total_exact_pct"], 100, pct(B["total_exact_pct"])),
        ("ยอดรวมตรง · Fine-tuned 2 Epoch", "ขั้นที่ 5", F["total_exact_pct"], 100, pct(F["total_exact_pct"])),
        ("ยอดรวมตรง · Fine-tuned 1 Epoch", "สกิล v0", f9["total_exact_pct"], 100, pct(f9["total_exact_pct"])),
        ("Item F1 · Base", "", B["item_f1_pct"], 100, pct(B["item_f1_pct"])),
        ("Item F1 · Fine-tuned 2 Epoch", "ขั้นที่ 5", F["item_f1_pct"], 100, pct(F["item_f1_pct"])),
        ("Item F1 · Fine-tuned 1 Epoch", "สกิล v0", f9["item_f1_pct"], 100, pct(f9["item_f1_pct"]))])
        + note("ที่มา `results/metrics.json` และ `results/skill_v0_run/eval/metrics.json`", "info"), tag="ผลรวม"))
    add(tbl("สั่งทีละขั้นกับสกิล v0 ได้ผลใกล้กัน แต่สกิลใช้พรอมต์ เวลา และเงินน้อยกว่า", cmp, post=note(rp9[1])))
    add(big("บทเรียนจาก LAB 2", first("img/n32-lessons.jpg", "image/skill-v0.png"), [
        rp3[0],
        R("4 · Training", "ถ้าวัดผลด้วยใบที่โมเดลเคยเห็น คะแนนจะสูงเกินจริง"),
        rp7[1],
        next(b for b in sec(p9) if b["t"] == "p" and b["lines"][0].startswith("วิธีปรับ"))["lines"][0]]))
    add(big("ข้อจำกัดที่ยังเหลือ: ผลยังไม่สมบูรณ์ 4 เรื่อง", first("img/n33-limits.jpg", "img/n31-v0-issues.jpg"), [
        rp5[3], rp6[1], rp6[3],
        "สกิล v0 ยังพลาด 4 จุดในรอบทดสอบ (เพดานราคา · เกณฑ์ VRAM · ดึงผลกลับช้า · สคริปต์ที่ยังไม่เคยรัน) ต้องแก้ใน v1"]))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบ LAB 2", "ตรวจอีกครั้งว่าไม่มีเครื่องค้างในบัญชี",
                  '<p>รายละเอียดเต็มของ LAB นี้: <a href="README.md" target="_blank">README.md</a> · พรอมต์ทั้ง 9 ขั้น: '
                  '<a href="PROMPTS.md" target="_blank">PROMPTS.md</a> · กลับหน้ารวมของบท: <a href="../README.md" target="_blank">../README.md</a></p>'))
    return E.SL


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
