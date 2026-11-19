#!/usr/bin/env python3
"""สร้างสไลด์ LAB8_Job_Queue_Slides.html ของ LAB 8 (ระบบคิวอ่านใบเสร็จด้วย VLM)

  python tools/build_slides.py            (รันจากโฟลเดอร์ของบท lab8_job_queue)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · อธิบายด้วยภาพ กราฟ หรือภาพหน้าจอที่อ่านได้ พร้อมประเด็นพูดไม่เกิน 3-4 ข้อ
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

รูปแบบสไลด์ที่ใช้ (เนื้อหาชนิดเดียวกันใช้รูปแบบเดียวกันเสมอ)
- fig()    ภาพเต็มสไลด์ + คำบรรยาย 1 บรรทัด          : ภาพอธิบายที่อ่านได้ในตัว และกราฟจริงที่มีคำแนะนำการอ่าน
- wide()   ภาพราว 68% ของสไลด์ + ประเด็นพูด 2-4 ข้อ   : แนวคิดที่ต้องมีตัวเลขหรือข้อสังเกตประกอบภาพ
- crop()   ส่วนหนึ่งของภาพหน้าจอคำตอบจริง + ผลที่ได้   : ผลจริงของทุกขั้น (มีลิงก์ไปภาพเต็ม)
- p95chart() กราฟแท่งที่เรียงพิมพ์จากตารางของ README   : ผลการไล่ N ของขั้นที่ 2-4 พร้อมเส้น SLO
- statement() ข้อความเดียวตัวใหญ่บนภาพถ่าย           : ข้อสรุปที่ผู้ฟังควรจำ
- หน้าคั่น: บอกตำแหน่ง "ส่วนที่ k จาก 4" และ "ขั้นที่ n จาก 9" พร้อมแถบความคืบหน้า

ที่มาของเนื้อหา
- ตาราง ข้อความ และพรอมต์ของทุกขั้น: อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร จาก code fence ชนิด text)
- ตัวเลขผล: อ่านจากตารางของ README.md (ซึ่งมาจาก results/metrics.json) หรือคัดจากคำบรรยายภาพหน้าจอใน README.md
- ภาพอธิบายใหม่: tools/slides_figures.py · ภาพตัดจากภาพหน้าจอคำตอบ: img/cNN-*.jpg · เครื่องมือเรนเดอร์: tools/slides_engine.py
"""
import html as H
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, para, CTX, add, note, fig, explain, tiles, cards, tbl)
from slides_figures import FIGS

S = E.slide
ITAL = re.compile(r"(?<![*\\])\*(?![*\s])([^*\n]+?)(?<![\s\\*])\*(?!\*)")


def no_italic(text):
    """ตัวเอียง *x* และ \\* ของ Markdown → ข้อความธรรมดา (เครื่องมือเรนเดอร์รู้จักแค่ตัวหนา) · ไม่แตะ code fence และ `code`"""
    out = []
    for k, part in enumerate(re.split(r"(```.*?```)", text, flags=re.S)):
        if k % 2:
            out.append(part)
            continue
        bits = re.split(r"(`[^`\n]*`)", part)
        out.append("".join(b if j % 2 else ITAL.sub(r"\1", b).replace("\\*", "*") for j, b in enumerate(bits)))
    return "".join(out)


SECS = E.load("README.md", transform=no_italic)
FIG = {f["img"]: f for f in FIGS}
OUT, TITLE = "LAB8_Job_Queue_Slides.html", "LAB 8 · ระบบคิวอ่านใบเสร็จด้วย VLM · Slides"
plain = E.plain

# ------------------------------------------------------------------ CSS เฉพาะเด็คนี้ (ต่อท้าย CSS ของเครื่องมือ ไม่แก้เครื่องมือ)
E.CSS += r"""
.ex.wide{gap:26px}
.ex.wide .fig{flex:2.25 1 0}
.ex.wide .side{flex:1 1 0}
.ex.tall .fig{flex:1 1 0}
.ex.tall .side{flex:1.25 1 0}
.ex .side .stp.pt .n{background:var(--teal)}
.cropfig{flex:1 1 0;min-height:0}
.cpts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.3em 1.2em;font-size:.8em;line-height:1.4}
.cpts .cp{display:flex;gap:.5em;align-items:flex-start}
.cpts .cp .n{flex:none;width:1.5em;height:1.5em;border-radius:50%;background:var(--navy);color:#fff;font-weight:700;font-size:.8em;display:flex;align-items:center;justify-content:center;margin-top:.1em}
.chartbox{flex:1 1 0;min-height:0;display:flex;align-items:center;justify-content:center}
.chartbox svg{height:100%;width:auto;max-width:100%;background:#fff;border-radius:12px;box-shadow:0 6px 22px rgba(18,48,94,.12)}
.divider .prog{display:flex;gap:10px;margin-top:26px;align-items:center}
.divider .prog span{width:44px;height:10px;border-radius:6px;background:rgba(255,255,255,.22)}
.divider .prog span.done{background:rgba(125,211,252,.75)}
.divider .prog span.now{background:#f59e0b;width:70px}
.divider .prog em{font-style:normal;font-size:20px;color:#cfe0ff;margin-left:8px}
.divider.stmt .inner h1{font-size:58px;line-height:1.3;max-width:900px}
.divider.stmt .inner .big{display:none}
.divider.stmt .inner .sub{max-width:820px;font-size:27px;line-height:1.55}
"""


# ------------------------------------------------------------------ ตัวค้นเนื้อหาใน README
def row(t, key, col=0):
    """แถวของตารางที่คอลัมน์ col ขึ้นต้นด้วย key"""
    for r in t["rows"]:
        if plain(r[col]).startswith(key):
            return r
    raise KeyError("ไม่พบแถว %r" % key)


def ul(prefix, k=0):
    """รายการหัวข้อย่อย (bullet) ลำดับที่ k ของหัวข้อ prefix"""
    return [b for b in walk(sec(prefix)) if b["t"] == "ul"][k]["items"]


def reads(prefix):
    """bullet ใต้ "**อ่านผลอย่างไร**" ของหัวข้อ"""
    bl, hit = sec(prefix), False
    for b in bl:
        if b["t"] == "p" and b["lines"][0].startswith("**อ่านผลอย่างไร**"):
            hit = True
        elif hit and b["t"] == "ul":
            return b["items"]
    raise KeyError("ไม่พบ อ่านผลอย่างไร ใน %r" % prefix)


def alert(prefix, k=0):
    """ข้อความในกล่อง > ของหัวข้อ (ลำดับ k)"""
    a = [b for b in sec(prefix) if b["t"] == "alert"][k]
    return " ".join(" ".join(x["lines"]) for x in a["blocks"] if x["t"] == "p")


def ptext(prefix, start):
    return " ".join(para(prefix, start)["lines"])


def evidence(prefix):
    """ย่อหน้า **หลักฐานจาก LAB นี้** / **ตัวเลขจาก LAB นี้** ของหัวข้อ (ไม่รวมคำนำ)"""
    for st in ("**หลักฐานจาก LAB นี้**", "**ตัวเลขจาก LAB นี้**"):
        try:
            return ptext(prefix, st)[len(st):].strip()
        except KeyError:
            pass
    raise KeyError(prefix)


def step_info(n):
    """คำอธิบาย 1 บรรทัดใต้หัวข้อของขั้น และบรรทัดเวลา (ตัวเอียง) ของขั้น n"""
    bl = sec("ขั้นที่ %d " % n)
    desc = next(b for b in bl if b["t"] == "p")["lines"][0]
    t = next(b for b in bl if b["t"] == "p" and b["lines"][0].startswith("ใช้เวลา"))["lines"][0]
    return desc, t


def step_title(n):
    return next(s["text"] for s in SECS if s["text"].startswith("ขั้นที่ %d " % n))


def num(s):
    """"12.2 s" → 12.2"""
    return float(re.search(r"[\d.]+", plain(s)).group(0))


# ------------------------------------------------------------------ รูปแบบสไลด์ของเด็คนี้
def side_points(points, numbered=True):
    return "".join('<div class="stp%s"><span class="n">%s</span><span>%s</span></div>' % (
        "" if numbered else " pt", k + 1 if numbered else "•", md(x)) for k, x in enumerate(points))


def wide(title, src, points, post="", tall=False, numbered=False):
    """ภาพราว 68% ของสไลด์ + ประเด็นพูด 2-4 ข้อด้านขวา (tall=True สำหรับภาพแนวตั้ง)"""
    img = E.img_tag({"t": "img", "src": src, "alt": plain(title)})
    return S(title, '<div class="ex %s"><div class="fig">%s</div><div class="side fitbox">%s%s</div></div>' % (
        "tall" if tall else "wide", img, side_points(points, numbered), post), maxfs=1.25)


def crop(title, src, full, points):
    """ส่วนหนึ่งของภาพหน้าจอคำตอบจริง (ตัดจากภาพเต็ม ไม่แก้พิกเซล) เต็มความกว้างสไลด์ + ผลที่ได้เป็นแถบด้านล่าง"""
    img = E.img_tag({"t": "img", "src": src, "alt": plain(title)})
    pts = "".join('<div class="cp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(points))
    return S(title, '<div class="fig cropfig">%s</div><div class="cpts">%s</div><p class="cap">ส่วนหนึ่งของคำตอบจริง · %s</p>' % (
        img, pts, md("[ดูภาพหน้าจอเต็ม](%s)" % full)), tag="ผลจริง", maxfs=1.05)


def statement(text, sub, img):
    """ข้อความเดียวตัวใหญ่บนภาพถ่าย"""
    d = E.divider("", text, "<p>%s</p>" % md(sub), img)
    d["cls"] += " stmt"
    d["title"] = plain(text)
    return d


def progress(k, n, label):
    return '<div class="prog">%s<em>%s</em></div>' % (
        "".join('<span class="%s"></span>' % ("done" if j < k else "now" if j == k else "") for j in range(n)), label)


def part_div(k, title, sub, img):
    return E.divider("ส่วนที่ %d จาก 4" % k, title, "<p>%s</p>%s" % (md(sub), progress(k - 1, 4, "ส่วนที่ %d จาก 4" % k)), img)


def step_div(n, result):
    desc, t = step_info(n)
    head = step_title(n).split("·", 1)[1].strip()
    sub = '<p>%s</p><p>%s</p><p><b>ผลจริง:</b> %s</p>%s' % (md(desc), md(t), md(result), progress(n - 1, 9, "ขั้นที่ %d จาก 9" % n))
    return E.divider("ขั้นที่ %d จาก 9" % n, head, sub)


def nfig(key, post=""):
    """สไลด์ ภาพ + ขั้นตอน ของภาพการ์ตูนรอบแรกใน slides_figures.py"""
    f = FIG[key]
    return explain(f["title"], "img/%s.jpg" % key, f["steps"], post)


def prompt_step(n, short):
    return E.prompt_slides(E.prompt_code("ขั้นที่ %d " % n), CTX["kicker"], "ขั้นที่ %d · %s" % (n, short))


def p95chart(groups, series, ymax, slo=20.0, foot=""):
    """กราฟแท่ง p95 ต่อระดับ N (เรียงพิมพ์จากตาราง README ทุกค่า) พร้อมเส้น SLO
    groups = ["N = 1", ...] · series = [(ชื่อ, สี, [ค่า], [ข้อความใต้แท่ง])]"""
    W, Hh, l, r, t, b = 1180, 560, 86, 24, 64, 112
    pw, ph = W - l - r, Hh - t - b
    y = lambda v: t + ph * (1 - v / ymax)
    out = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans Thai, Leelawadee UI, sans-serif" role="img">' % (W, Hh)]
    for g in range(0, int(ymax) + 1, 10):
        out.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#e3e9f2"/>' % (l, W - r, y(g), y(g)))
        out.append('<text x="%d" y="%.1f" font-size="20" fill="#5b6b80" text-anchor="end">%d</text>' % (l - 12, y(g) + 7, g))
    out.append('<text x="22" y="%d" font-size="20" fill="#5b6b80" transform="rotate(-90 22 %d)" text-anchor="middle">p95 (วินาที)</text>' % (t + ph / 2, t + ph / 2))
    gw = pw / len(groups)
    bw = min(120, gw * 0.62 / len(series))
    for gi, gname in enumerate(groups):
        x0 = l + gi * gw + (gw - bw * len(series)) / 2
        for si, (_, color, vals, notes) in enumerate(series):
            v = vals[gi]
            if v is None:
                continue
            x = x0 + si * bw
            over = v > slo
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="%s"/>' % (x + 4, y(v), bw - 8, y(0) - y(v), color))
            out.append('<text x="%.1f" y="%.1f" font-size="22" font-weight="700" fill="%s" text-anchor="middle">%s</text>' % (
                x + bw / 2, y(v) - 10, "#c92a2a" if over else "#12305e", H.escape("%.1f" % v)))
            if notes and notes[gi]:
                out.append('<text x="%.1f" y="%d" font-size="19" font-weight="600" fill="%s" text-anchor="middle">%s</text>' % (
                    x + bw / 2, t + ph + 62, "#c92a2a" if "100" in notes[gi] or "ไม่ผ่าน" in notes[gi] else "#15803d", H.escape(notes[gi])))
        out.append('<text x="%.1f" y="%d" font-size="23" font-weight="700" fill="#12305e" text-anchor="middle">%s</text>' % (
            l + gi * gw + gw / 2, t + ph + 32, H.escape(gname)))
    out.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#c92a2a" stroke-width="3" stroke-dasharray="10 7"/>' % (l, W - r, y(slo), y(slo)))
    out.append('<text x="%d" y="%.1f" font-size="20" font-weight="700" fill="#c92a2a" text-anchor="start">SLO: p95 ≤ %g วินาที</text>' % (l + 8, y(slo) - 10, slo))
    lx = l + 10
    for name, color, _, _ in series:
        out.append('<rect x="%d" y="18" width="22" height="22" rx="4" fill="%s"/><text x="%d" y="37" font-size="21" fill="#1c2533">%s</text>' % (
            lx, color, lx + 30, H.escape(name)))
        lx += 60 + 13 * len(name)
    if foot:
        out.append('<text x="%d" y="%d" font-size="18" fill="#5b6b80">%s</text>' % (l, Hh - 12, H.escape(foot)))
    out.append("</svg>")
    return '<div class="chartbox">%s</div>' % "".join(out)


def chart_slide(title, svg, cap, tag=""):
    return S(title, svg + '<p class="cap">%s</p>' % md(cap), tag=tag, maxfs=1.1)


# ผลจริงข้างภาพหน้าจอคำตอบของแต่ละขั้น (ข้อความจากคำบรรยายภาพหน้าจอใน README.md)
SHOT = {
    1: ["เครื่อง 2× RTX 3090 ราคา $0.394/ชม. ที่ Quebec แคนาดา CPU 12 cores", "เครื่องพร้อมใช้งานใน **34 วินาที**",
        "Test Set มี **100 ใบ** ใบเสร็จตัวอย่างมี 1, 1, 1, 5, 4, 1 รายการ"],
    2: ["GPU 1 ใบรองรับผู้ใช้พร้อมกันได้ **2 คน** ที่ p95 ≤ 20 วินาที",
        "N = 1 ได้ 3.0 งาน/นาที p95 12.2 วินาที และ N = 2 ได้ 6.0 งาน/นาที p95 11.8 วินาที", "N = 4 และ 6 **ล้ม 100%**",
        "งานถล่ม: สำเร็จ 2 งาน ล้ม 58 งาน และ server อ่านงานที่ผู้ใช้เลิกรอไปแล้ว 58 งาน"],
    3: ["p95 ของคิว 1 Worker คือ 13.0, 15.8, 36.7 และ 57.7 วินาที ที่ N = 1, 2, 4, 6 โดยล้ม **0%** ทุกระดับ",
        "งานถล่ม: สำเร็จ **60/60** p95 624.5 วินาที คิวยาวสุด 58 งาน และคิวว่างที่ 651 วินาที",
        "AI แก้ปัญหาของเครื่องเช่าเอง 2 เรื่อง (RabbitMQ เปิดไม่ขึ้น และ CUDA error 804) ควรอ่านส่วนนี้ในคำตอบของคุณด้วย"],
    4: ["1 GPU กับ 1 Worker รองรับ 2 คน ได้ 6.0 งาน/นาที p95 15.8 วินาที",
        "2 GPU กับ 2 Worker รองรับ **4 คน** ได้ 11.0 งาน/นาที p95 13.9 วินาที เป็น 2.00 เท่า", "3 GPU เป็น **ค่าประมาณ** 6 คน ไม่ใช่ผลวัด",
        "เวลาระบายคิวงานถล่ม 651 วินาที (1 Worker) และ 319 วินาที (2 Worker)"],
    5: ["SIGKILL Worker ของ GPU ใบที่ 2 ที่วินาทีที่ 20.0 ขณะที่คิวยังเหลือ 55 งาน", "เสร็จ **60/60** งาน และคิวหมดที่วินาทีที่ 656",
        "ส่งซ้ำ 1 งาน (`d8a6166ead19`) ซึ่ง Worker GPU0 ทำเสร็จที่วินาทีที่ 33.2", "Worker GPU0 ทำ 58 งาน และ Worker GPU1 ทำ 2 งาน"],
    7: ["ผลใน `results` ครบ 19 ไฟล์ และกราฟ 5 รูป", "ลบเครื่อง `vapp-lab8` แล้ว ไม่มีเครื่องป้ายนี้ค้าง และปิดเว็บแล้ว",
        "อายุเครื่อง 1.985 ชั่วโมง ราคา $0.3937/ชม. รวม **$0.781**"],
    8: ["สร้างสกิล `vlm-queue-capacity` เวอร์ชัน 0 และติดตั้งเป็นสกิลของโปรเจกต์แล้ว **แต่ยังไม่ได้ลองใช้จริง**",
        "สกิลเช่า 2 GPU ติดตั้งโมเดลกับ RabbitMQ ยิงโหลด ทำรายงาน และลบเครื่องเสมอ",
        "ค่าที่ปรับได้ เช่น gpu, max_price $0.60, label, levels, SLO และมีไฟล์ 7 ไฟล์ใน `scripts/`"],
    9: ["Baseline 2 คน คิว 1 Worker 2 คน คิว 2 Worker 4 คน **2.0 เท่า** ตรงกับผลเดิม",
        "เครื่อง 2× RTX 3090 ราคา $0.340/ชม.",
        "งานถล่ม: Baseline 2/60 คิว 1 Worker ระบาย 708 วินาที คิว 2 Worker ระบาย 355 วินาที",
        "เครื่องเปิดรวม 1 ชั่วโมง 23 นาที ค่าใช้จ่ายจริง **$0.478**"],
}

MAYDIFFER = "ตัวเลขของคุณอาจต่างจากของผู้สอนได้ เพราะได้เครื่องเช่าคนละเครื่อง และโค้ดที่ AI เขียนให้ไม่เหมือนกันทุกครั้ง"
C_SYNC, C_Q1, C_Q2 = "#2f9e6e", "#3b6fd8", "#e8801c"   # สีเดียวกับกราฟใน results/charts


def build():
    main = table("ทำไปเพื่ออะไร", "จำนวน GPU")
    sync, q1, q2, q3 = main["rows"]
    exp = table("การทดลอง", "หัวข้อ")
    machine, cost = row(exp, "เครื่อง")[1], row(exp, "เวลาและค่าเช่าจริง")[1]

    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    add(E.cover("LAB 8 · อ่านใบเสร็จด้วย VLM เป็นงานคิว", "วัดฐาน GPU 1 ใบ แล้วเพิ่มด้วย RabbitMQ + GPU Worker เป็น 2 ใบ",
                "img/s01-cover.jpg", small="สัปดาห์ที่ 3 · Vast.ai Application · LAB 8"))
    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("GPU 1 ใบรับผู้ใช้พร้อมกันได้ 2 คน เมื่อเพิ่มเป็น 2 ใบด้วยระบบคิวรับได้ 4 คน", "image/why7-queue.png",
            "ทุกแบบวัดด้วยเกณฑ์เดียวกัน คือเวลารอผล **p95 ≤ 20 วินาที** และงานล้มน้อยกว่า 1%"))
    headline = plain(para("ทำไปเพื่ออะไร", "**1 ใบ")["lines"][0])
    add(S("ผลวัดจริง: " + headline, tiles([
        ("API Synchronous (Baseline) · GPU %s ใบ" % sync[0], plain(sync[2]) + " คน", "%s งาน/นาที · งานถล่ม%s" % (sync[3], sync[5]), "warn"),
        ("ระบบคิว Worker 1 ตัว · GPU %s ใบ" % q1[0], plain(q1[2]) + " คน", "%s งาน/นาที · งานถล่ม %s" % (q1[3], q1[5]), ""),
        ("ระบบคิว Worker 2 ตัว · GPU %s ใบ" % q2[0], plain(q2[2]) + " คน", "%s งาน/นาที · งานถล่ม %s · **%s**" % (q2[3], q2[5], q2[6]), "ok"),
    ]) + note("GPU %s ใบ · %s: %s คน · %s งาน/นาที · ระบาย %s" % (q3[0], q3[1], q3[2], q3[3], q3[5]), label="ประมาณการ"), cls="mid"))
    add(fig("บทนี้มี 4 ส่วน เริ่มจากพื้นฐานและทฤษฎี แล้วจึงลงมือทำ LAB", "img/n21-roadmap.jpg",
            "ส่วนที่ 3 ใช้เครื่องเช่าที่คิดเงินตลอด จึงควรอ่านส่วนที่ 1 และ 2 ให้เข้าใจก่อนเริ่ม"))
    add(S("สไลด์ชุดนี้เปลี่ยนหน้าด้วยปุ่มลูกศร และคัดลอกพรอมต์ได้ครบทั้งพรอมต์", cards([
        ("ปุ่มลูกศร หรือ Space", "เปลี่ยนหน้า กด **O** เพื่อเปิดสารบัญ และกด **F** เพื่อแสดงเต็มจอ"),
        ("คลิกภาพ", "ขยายภาพเต็มจอ เพื่ออ่านตัวเลขในกราฟและภาพหน้าจอ"),
        ("ปุ่ม คัดลอกพรอมต์ทั้งหมด", "คัดลอกพรอมต์ของขั้นนั้นครบทั้งพรอมต์ ตรงกับ README ทุกตัวอักษร"),
        ("ตรวจผลของคุณ", "ติ๊กรายการที่ตรวจแล้วบนเครื่องของคุณ เบราว์เซอร์จะจำค่าที่ติ๊กไว้"),
    ], 2), cls="mid"))

    # ===== ส่วนที่ 1 · พื้นฐาน
    CTX.update(kicker="", group="ส่วนที่ 1 · พื้นฐาน")
    add(part_div(1, "พื้นฐาน: ข้อมูล โมเดล และนิยามของผู้ใช้",
                 "LAB นี้ **ไม่เทรนโมเดล** ใช้ Dataset เป็นชุดคำขอสำหรับยิงโหลด และวัด **ความจุของระบบ**", "img/p22-receipt.jpg"))
    CTX["kicker"] = "ส่วนที่ 1 · ข้อมูลทดสอบ"
    cord = table("รู้จักข้อมูลที่ใช้ทดสอบ", "หัวข้อ")
    add(wide("ข้อมูลทดสอบคือใบเสร็จจริง 6 ใบจาก Test Set ของ CORD-v2 พร้อมเฉลยเป็น JSON", "results/dataset_samples.jpg", [
        "CORD-v2 จัดทำโดย %s เผยแพร่ด้วยสัญญาอนุญาต %s" % (row(cord, "ใครทำ")[1], row(cord, "สัญญาอนุญาต")[1]),
        "แบ่งเป็น " + row(cord, "การแบ่งชุด")[1],
        "LAB นี้ใช้ " + row(cord, "LAB นี้ใช้")[1]]))
    lab = table("รู้จักข้อมูลที่ใช้ทดสอบ", "ช่อง")
    add(wide("เฉลยของใบเสร็จ test_020 มีรายการ ยอดก่อนภาษี ค่าบริการ ภาษี และยอดรวม", "samples/test_020.jpg",
             ["%s: %s<br>ค่าใน test_020: **%s**" % (r[0], r[1], r[2]) for r in lab["rows"]],
             note(ptext("รู้จักข้อมูลที่ใช้ทดสอบ", "ตัวเลขเก็บเป็นข้อความ")), tall=True))
    CTX["kicker"] = "ส่วนที่ 1 · โมเดล"
    model = table("รู้จักโมเดลที่ใช้", "หัวข้อ")
    job = next(b for b in walk(sec("รู้จักข้อมูลที่ใช้ทดสอบ")) if b["t"] == "table" and plain(b["head"][1]).startswith("ตัวยิงโหลด"))
    gpu_t = row(job, "เวลาที่ GPU ใช้")
    add(wide("Qwen3-VL-2B-Instruct อ่านภาพใบเสร็จแล้วเขียนผลเป็น JSON และเป็นงานของ GPU ที่ใช้วัดความจุ", "image/model-qwen3vl.png", [
        "ขนาด: " + row(model, "ขนาด")[1],
        "ตัวยิงโหลดส่งใบเสร็จ 4 ใบเป็น 1 งาน GPU ใช้ %s ส่วนเว็บส่ง 1 ใบต่องาน ใช้ %s" % (gpu_t[1], gpu_t[2]),
        alert("รู้จักโมเดลที่ใช้")]))

    # ===== ส่วนที่ 2 · ทฤษฎี
    CTX.update(kicker="", group="ส่วนที่ 2 · ทฤษฎี")
    add(part_div(2, "ทฤษฎี: 7 แนวคิดที่ใช้อ่านผลของ LAB นี้",
                 "ผู้ใช้และ SLO, Throughput และ Latency, Little's Law, Synchronous กับ Job Queue, RabbitMQ, Scaling และระบบจริง",
                 "img/p23-theory.jpg"))
    CTX["kicker"] = "ทฤษฎี 1 · ผู้ใช้ งาน และ SLO"
    add(fig("ผู้ใช้ 1 คนวนส่งงาน รอผล และคิด 10 วินาที ก่อนส่งงานใหม่ (Closed loop)", "image/t7-user-job.png",
            "**SLO** (Service Level Objective) คือเวลารอผล p95 ≤ 20 วินาที และงานล้มน้อยกว่า 1% · **รองรับได้ N คน** คือ N มากที่สุดที่ยังผ่าน SLO"))
    add(wide("ผู้ใช้ 1 คนส่ง 2.9 งาน/นาที GPU 1 ใบทำได้ 5.44 งาน/นาที จึงรับได้ราว 2 คน", "img/n22-capacity.jpg", [
        "1 งานใช้ GPU ราว 11 วินาที ผู้ใช้จึงส่งงานใหม่ทุกราว 21 วินาที (รอ 11 + คิด 10)",
        "ไล่ N = 1, 2, 4, 6, 8 ระดับละ 75 วินาที โดยไม่นับ 15 วินาทีแรก",
        "การไล่ N ทีละ 2 ทำให้ความจุที่ได้หยาบ จึงดูงาน/นาทีและเวลาระบายงานถล่มประกอบเสมอ"]))
    add(statement("ตัวเลข 2 คนไม่ได้แปลว่าระบบอ่อน แต่แปลว่างานหนัก",
                  "ถ้างานเบาลง (เช่น ส่งใบละ 1 งาน) หรือ Think time ยาวขึ้น GPU ใบเดิมจะรับคนได้มากขึ้น "
                  "จึงต้องบอกนิยามของผู้ใช้และงานทุกครั้งที่รายงานความจุ", "img/p21-heavy.jpg"))
    CTX["kicker"] = "ทฤษฎี 2 · Throughput และ Latency"
    add(fig("เวลารอผลคงที่จนถึงจุดอิ่มตัว แล้วชันขึ้นเป็นเส้นตรง", "results/charts/latency_vs_users.png",
            "ดูเส้นสีส้ม (2 Worker) ซึ่งข้ามเส้น SLO 20 วินาทีหลัง N = 4 · ดาวคือจุดความจุของแต่ละแบบ"))
    pt = table("2 · Throughput", "แบบ")
    add(wide("p95 บอกเวลาของคนที่รอนาน ซึ่งค่าเฉลี่ยซ่อนไว้", "img/n23-percentile.jpg",
             ["%s ที่ N = %s: p50 %s · p95 **%s** · p99 %s<br>%s" % (r[0], r[1], r[2], r[3], r[4], r[5]) for r in pt["rows"]],
             note(ul("2 · Throughput")[0].replace("**คืออะไร** ", ""), label="นิยาม")))
    add(fig("เมื่อ GPU อิ่มตัว Throughput ไม่เพิ่มอีก ผู้ใช้ที่เพิ่มเข้ามากลายเป็นคิวที่ยาวขึ้น", "results/charts/throughput_vs_users.png",
            "API Synchronous ตกเป็น 0 ที่ N = 4 · คิว 1 Worker แบนที่ 5–6 งาน/นาที · คิว 2 Worker แบนที่ 11 งาน/นาที"))
    CTX["kicker"] = "ทฤษฎี 3 · Little's Law"
    add(wide("Little's Law: จำนวนผู้ใช้พร้อมกันเท่ากับ Throughput คูณเวลาหนึ่งรอบของผู้ใช้", "img/n24-little.jpg", [
        "เมื่อ GPU ทำได้สูงสุด X_max แล้ว เวลารอผลจะโตเป็นเส้นตรง **R ≈ N ÷ X_max − Z**",
        "1 Worker: X_max = 5.44 งาน/นาที = 0.0907 งาน/วินาที เวลาอ่าน 1 งาน S ≈ 11 วินาที และ Z = 10 วินาที",
        "จุดอิ่มตัว **N\\* ≈ X_max × (S + Z)** ≈ 0.0907 × 21 ≈ 1.9 คน"]))
    ll = table("3 · กฎของ Little", "แบบ")
    add(wide("ค่าที่ Little's Law ทำนายต่างจากค่าที่วัดได้ไม่ถึง 2 วินาที", "results/charts/little_law.png",
             ["%s ที่ N = %s: ทำนาย **%s** วัดได้ (p50) **%s**" % (plain(r[0]).split(" (")[0], r[1], r[2], r[3]) for r in ll["rows"]],
             note(ptext("3 · กฎของ Little", "ใช้ออกแบบได้"), label="ใช้ออกแบบ")))

    CTX["kicker"] = "ทฤษฎี 4 · Synchronous กับ Job Queue"
    add(fig("งานถล่ม 60 งาน: API Synchronous ได้ผล 2 งาน ส่วนระบบคิวได้ผลครบ 60 งาน", "image/t7-sync-vs-queue.png",
            "คิวไม่ทำให้ GPU เร็วขึ้น ความจุของ GPU 1 ใบยังเป็น 2 คนทั้งสองแบบ สิ่งที่คิวเปลี่ยนคือ งานไม่ล้มเพราะ timeout แต่รอนานขึ้น"))
    add(wide("API แบบ Synchronous มีปัญหา 3 ข้อเมื่อโหลดเกิน ระบบคิวแก้ด้วยการแยกผู้รับงานออกจากผู้ทำงาน", "img/n25-sync-problems.jpg", [
        "Job Queue: `POST /jobs` ได้ `job_id` กลับทันที งานไปรอในคิว แล้วผู้ใช้ถามผลที่ `GET /jobs/{id}` เป็นระยะ",
        "การเชื่อมต่อของผู้ใช้ปิดทันทีที่ได้ `job_id` จึงไม่มี timeout ฝั่งผู้ใช้",
        "เพิ่ม Worker ได้โดยไม่ต้องแก้ฝั่งผู้ใช้"]))
    add(fig("ระบบคิวของ LAB นี้: gateway รับงาน RabbitMQ พักงาน และ Worker 1 ตัวต่อ GPU 1 ใบ", "image/lab8-system.png",
            "`POST /jobs` ได้ `job_id` ทันที ผลเก็บใน SQLite และเมื่อคิวเกิน 1000 งาน gateway ตอบ `503`"))

    CTX["kicker"] = "ทฤษฎี 5 · RabbitMQ"
    mq = table("5.1 ", "ส่วน")
    add(wide("RabbitMQ รับงานจาก Producer พักไว้ใน Queue แล้วส่งต่อให้ Consumer ที่ว่าง", "image/mq7-flow.png", [
        "Producer คือ gateway: " + row(mq, "Producer")[3],
        "Queue ของ LAB นี้: " + row(mq, "Queue")[3],
        evidence("5.1 ")]))
    add(fig("Exchange ใช้ routing key เลือกคิว LAB นี้ใช้ Default Exchange ซึ่ง routing key คือชื่อคิว", "image/mq7-routing.png",
            "งานมีชนิดเดียว จึงใช้ Default Exchange: **routing key = ชื่อคิว** (`receipts.jobs`)"))
    add(fig("Competing Consumers: Worker 2 ตัวแย่งงานจากคิวเดียว และแต่ละงานไปถึง Worker ตัวเดียว", "image/mq7-competing.png",
            evidence("5.3 ")))
    add(fig("Worker ส่ง ack หลังทำเสร็จ เมื่อ Worker ถูกฆ่ากลางงาน งานจึงกลับเข้าคิวและถูกทำต่อ", "image/mq7-ack.png",
            "**At-least-once delivery**: งานไม่หาย แต่อาจถูกทำ 2 ครั้ง ผลจึงต้องเขียนทับได้ (Idempotent)"))
    add(fig("Prefetch = 1: Worker ถือทีละงาน งานที่เหลืออยู่ในคิวกลาง", "image/mq7-prefetch.png", evidence("5.5 ")))
    add(wide("คิวต้อง Durable ข้อความต้อง Persistent งานพังไป DLQ และคิวมีเพดานความยาว", "image/mq7-safety.png", [
        ul("5.6 ")[1].split("**", 2)[-1].strip(),
        "ผลจริง: " + ul("5.7 ")[3].replace("**ตัวเลขจาก LAB นี้** ", "") + " และ " + ul("5.8 ")[3].replace("**ตัวเลขจาก LAB นี้** ", ""),
        ul("5.6 ")[3].replace("**ข้อจำกัด** ", "ข้อจำกัด: ")]))
    add(wide("งานที่ใช้เวลาราว 11 วินาทีเหมาะกับ Queue ส่วนงานสั้นเหมาะกับ Load Balancer", "image/mq7-vs-lb.png", [
        "Load Balancer **ผลัก** งานไปหา server (Push) ส่วน Worker ของคิว **ดึง** งานเมื่อว่าง (Pull)",
        evidence("5.9 ")]))

    CTX["kicker"] = "ทฤษฎี 6–7 · Scaling และระบบจริง"
    sc = table("6 · Scaling", "ตัววัด")
    add(wide("GPU 2 ใบได้ความจุ 2 เท่าของ 1 ใบ จุดที่วัดได้ทับเส้น Ideal", "results/charts/scaling_vs_gpus.png",
             ["%s: 1 ใบ %s → 2 ใบ %s (%s, Efficiency %s)" % (plain(r[0]), r[1], r[2], r[3], r[4]) for r in sc["rows"][:3]]
             + ["%s: %s → %s (%s)" % (plain(sc["rows"][3][0]), sc["rows"][3][1], sc["rows"][3][2], sc["rows"][3][3])],
             note(ul("6 · Scaling", 1)[0] + " · วงกลมกลวงที่ 3 ใบคือ **ค่าประมาณ ไม่ใช่ผลวัด**")))
    add(fig("ใน LAB ทุกส่วนอยู่บนเครื่องเดียว ส่วนในระบบจริงแยกไปอยู่คนละเครื่อง", "image/t7-production.png",
            ul("7 · ในระบบจริง")[3].replace("**ตัวเลขจาก LAB นี้** ", "")))

    # ===== ส่วนที่ 3 · LAB
    CTX.update(kicker="", group="ส่วนที่ 3 · LAB")
    add(part_div(3, "LAB: 7 ขั้นจากเช่าเครื่องถึงลบเครื่อง", "%s · เวลาและค่าเช่าจริง: %s" % (machine, cost), "img/s02-lab.jpg"))
    CTX["kicker"] = "ส่วนที่ 3 · การทดลอง"
    add(nfig("n01-experiment"))
    add(fig("LAB มี 9 ขั้น ขั้นละ 1 พรอมต์ และขั้นที่ 1–7 ใช้เครื่องเช่าที่คิดเงินตลอด", "image/lab8-overview.png",
            "ทำขั้นที่ 1–7 ให้ครบในรอบเดียว และ **ห้ามข้ามขั้นที่ 7** (ลบเครื่อง) · ขั้นที่ 8–9 เก็บงานทั้งหมดเป็นสกิล"))
    add(wide("ก่อนเริ่มต้องเตรียมให้ครบ 4 อย่าง", "img/n27-prereq.jpg", [
        "ทำ [LAB 0](../README.md) ของบทก่อน (เตรียม key 3 ตัว)",
        "เปิด Claude Code ที่โฟลเดอร์ของบท `02_VastAi_Application` (โฟลเดอร์ปัจจุบันในพรอมต์หมายถึงโฟลเดอร์นี้)",
        "ทุกพรอมต์ทำงานใน container `multi-account` โฟลเดอร์ `/workspace/vastapp_lab` ด้วยสกิล vastai",
        "รอบจริงใช้เครื่อง 2× RTX 3090 · " + cost], numbered=True))

    # ขั้นที่ 1
    CTX.update(kicker="ขั้นที่ 1 จาก 9 · เช่าเครื่อง", group="ขั้นที่ 1 · เช่าเครื่อง")
    add(step_div(1, "เครื่อง 2× RTX 3090 ราคา $0.394/ชม. พร้อมใน 34 วินาที และได้ภาพ `results/dataset_samples.jpg`"))
    add(nfig("n02-step1-rent"))
    add(prompt_step(1, "เช่าเครื่อง 2 GPU และดูตัวอย่างใบเสร็จ"))
    add(E.check_slide("step1", ["AI เช่าเครื่องเดียวที่มี RTX 3090 **2 ใบ** ราคารวมไม่เกิน **$0.60/ชม.** ป้าย `vapp-lab8`",
                                "AI เข้าไปเห็น GPU ครบ 2 ใบ",
                                "มีไฟล์ `lab8_job_queue/results/dataset_samples.jpg` ใบเสร็จ 6 ใบคู่กับ JSON เฉลย",
                                "คำตอบมีตาราง GPU · ราคา · ที่ตั้ง · CPU cores · เวลาที่รอ · จำนวนใบเสร็จใน Test Set",
                                "คำตอบบอกว่า **เครื่องยังเปิดอยู่**"],
                      "ผลของผู้สอน: 2× RTX 3090 · $0.394/ชม. · Quebec แคนาดา · CPU 12 cores · พร้อมใน 34 วินาที · Test Set 100 ใบ",
                      MAYDIFFER, "ขั้นที่ 1"))
    add(crop("เครื่องพร้อมใน 34 วินาที และ Test Set มี 100 ใบ", "img/c01-step1.jpg", "image/lab8-step1.png", SHOT[1]))
    r1 = reads("ขั้นที่ 1 ")
    add(wide("เครื่องที่ถูกที่สุดไม่ใช่เครื่องที่ดีที่สุดเสมอ และเมื่อเช่าแล้วเครื่องเริ่มคิดเงินทันที", "img/n28-step1-read.jpg", r1[1:]))

    # ขั้นที่ 2
    CTX.update(kicker="ขั้นที่ 2 จาก 9 · Baseline", group="ขั้นที่ 2 · Baseline")
    add(step_div(2, reads("ขั้นที่ 2 ")[0]))
    add(nfig("n03-step2-baseline"))
    add(prompt_step(2, "Baseline: API ตรงบน GPU 1 ใบ"))
    add(E.check_slide("step2", ["มีไฟล์ `code/sync_api.py` และ `code/loadtest.py` ในโฟลเดอร์ `lab8_job_queue`",
                                "ไล่ N = 1, 2, 4, 6 … แล้วหยุดเมื่อไม่ผ่าน SLO 2 ระดับติดกัน",
                                "ตารางมี N · งาน/นาที · p50 · p95 · % ล้ม · GPU util · CPU ตัวยิง",
                                "มีประโยค \"GPU 1 ใบ รองรับผู้ใช้พร้อมกันได้ N คน ที่ p95 ≤ 20 วินาที\"",
                                "ผลงานถล่มบอกว่าสำเร็จกี่งาน ล้มกี่งาน และ server อ่านงานที่ผู้ใช้เลิกรอไปแล้วกี่งาน",
                                "คำตอบไม่แสดงค่า key"],
                      "ผลของผู้สอน: รองรับ **2 คน** · N = 4 ล้ม 100% · งานถล่มสำเร็จ 2 งาน ล้ม 58 งาน",
                      MAYDIFFER, "ขั้นที่ 2"))
    add(crop("GPU 1 ใบแบบ Synchronous รองรับผู้ใช้พร้อมกันได้ 2 คน และงานถล่มได้ผลเพียง 2 จาก 60 งาน", "img/c02-step2.jpg",
             "image/lab8-step2.png", SHOT[2]))
    b2 = table("ขั้นที่ 2 ", "N")
    add(chart_slide("Baseline ผ่าน SLO ที่ N = 2 แล้วล้ม 100% ตั้งแต่ N = 4", p95chart(
        ["N = %s" % plain(r[0]) for r in b2["rows"]],
        [("API Synchronous · GPU 1 ใบ", C_SYNC, [num(r[3]) for r in b2["rows"]], ["ล้ม %s%%" % plain(r[4]) for r in b2["rows"]])], 40),
        "แท่งสูง 30.0 วินาทีคือผู้ใช้เลิกรอที่เพดาน 30 วินาที · งาน/นาที %s · GPU util %s" % (
            " / ".join(r[1] for r in b2["rows"]), " / ".join(r[5] for r in b2["rows"])), tag="results/baseline/"))
    r2 = reads("ขั้นที่ 2 ")
    add(wide("เกินความจุแล้วล้มเป็นลูกโซ่ เพราะ server ยังอ่านงานที่ไม่มีใครรอแล้ว", "img/n29-chain.jpg", r2[1:]))

    # ขั้นที่ 3
    CTX.update(kicker="ขั้นที่ 3 จาก 9 · ระบบคิว 1 Worker", group="ขั้นที่ 3 · ระบบคิว 1 Worker")
    add(step_div(3, "ความจุยังเป็น 2 คน แต่ไม่มีงานล้ม และงานถล่มได้ผล 60/60"))
    add(explain("ขั้นที่ 3: เขียน gateway กับ Worker แล้ววัดซ้ำบน GPU ใบเดิม", "image/lab8-system.png", [
        "**gateway.py**: API gateway พอร์ต 8000 · `POST /jobs` คืน `job_id` ทันที · `GET /jobs/{id}` · `GET /stats` · เก็บผลใน SQLite",
        "**worker.py**: Worker 1 ตัวต่อ GPU 1 ใบ · Durable + Persistent · Prefetch = 1 · ack หลังอ่านเสร็จ · DLQ · คิวไม่เกิน 1000 งาน",
        "**ติดตั้ง RabbitMQ** พร้อมหน้า management ปิด API แบบ Synchronous แล้วเปิด gateway กับ Worker บน GPU ใบแรก",
        "**ปรับ loadtest.py** ให้ส่งผ่านคิว (ไม่มีเพดาน 30 วินาที) แล้วยิงโหลดแบบเดียวกับขั้นที่ 2 ทุกอย่าง"]))
    add(prompt_step(3, "ระบบคิว: gateway + RabbitMQ + Worker 1 ตัว"))
    add(E.check_slide("step3", ["มีไฟล์ `code/gateway.py` และ `code/worker.py` · ทดสอบส่ง 1 งานผ่านคิวได้",
                                "ตารางเทียบ Baseline กับคิว 1 Worker ที่ N เดียวกัน: p95 · % ล้ม · งาน/นาที",
                                "งานถล่ม 60 งาน: สำเร็จกี่งาน · p95 · คิวยาวสุด · ระบายคิวหมดในกี่วินาที",
                                "อ่านส่วนปัญหาที่ AI เจอและแก้เองบนเครื่องเช่าในคำตอบ",
                                "คำตอบไม่แสดงค่า key และบอกว่าเครื่องยังเปิดอยู่"],
                      "ผลของผู้สอน: ความจุ **2 คน** · ล้ม 0% ทุกระดับ · งานถล่ม 60/60 · p95 624 s · คิวยาวสุด 58 งาน · ระบายหมดใน 651 s",
                      MAYDIFFER, "ขั้นที่ 3"))
    add(crop("ระบบคิว 1 Worker ล้ม 0% ทุกระดับ และงานถล่มได้ผลครบ 60 จาก 60 งาน", "img/c03-step3.jpg", "image/lab8-step3.png", SHOT[3]))
    c3 = table("ขั้นที่ 3 ", "N")
    r3 = reads("ขั้นที่ 3 ")
    add(chart_slide("ที่ N เดียวกัน Baseline ล้ม 100% ตั้งแต่ N = 4 ส่วนระบบคิวล้ม 0% แต่รอนานขึ้น", p95chart(
        ["N = %s" % plain(r[0]) for r in c3["rows"]],
        [("Baseline", C_SYNC, [num(r[1]) for r in c3["rows"]], ["ล้ม %s%%" % plain(r[3]) for r in c3["rows"]]),
         ("คิว 1 Worker", C_Q1, [num(r[2]) for r in c3["rows"]], ["ล้ม %s%%" % plain(r[4]) for r in c3["rows"]])], 60),
        "ความจุยังเป็น 2 คนเท่า Baseline · งาน/นาที Baseline %s · คิว %s" % (
            " / ".join(r[5] for r in c3["rows"]), " / ".join(r[6] for r in c3["rows"])), tag="results/queue_1worker/"))
    bt = table("ขั้นที่ 3 ", "งานถล่ม")
    ok, wt, drain, rate = row(bt, "สำเร็จ"), row(bt, "เวลารอผล"), row(bt, "ระบายคิว"), row(bt, "งาน/นาที")
    add(wide("งานถล่ม 60 งาน: Baseline ได้ผล 2 งาน ส่วนระบบคิวได้ผลครบ 60 งานแต่รอเกือบ 10 นาที", "image/t7-sync-vs-queue.png", [
        "Baseline: สำเร็จ %s · p50 / p95 %s · %s · ผู้ใช้ได้ %s งาน/นาที" % (plain(ok[1]), wt[1], drain[1], rate[1]),
        "คิว 1 Worker: สำเร็จ **%s** · p50 / p95 %s · ระบายหมดใน %s · %s งาน/นาที" % (plain(ok[2]), wt[2], drain[2], rate[2]),
        r3[2], r3[3]]))

    # ขั้นที่ 4
    CTX.update(kicker="ขั้นที่ 4 จาก 9 · 2 Worker", group="ขั้นที่ 4 · 2 Worker")
    add(step_div(4, reads("ขั้นที่ 4 ")[0]))
    add(explain("ขั้นที่ 4: เปิด Worker ตัวที่ 2 บน GPU ใบที่ 2 ต่อเข้าคิวเดิม", "image/mq7-competing.png", [
        "**เปิด Worker ตัวที่ 2** บน GPU ใบที่ 2 · ทั้งสองตัวแย่งกันหยิบงานจากคิวเดียวกัน",
        "**ยิงโหลดแบบเดียวกับขั้นที่ 3**: ไล่ N เริ่มที่ 4 จนเลยจุดอิ่มตัว + งานถล่ม 60 งาน",
        "**report.py** สร้าง `metrics.json` และกราฟ: p50/p95 เทียบ N · งาน/นาที · Scaling · ความยาวคิวตอนงานถล่ม",
        "**ประมาณการ 3 GPU** จากผลที่วัดได้ และบอกชัดว่าเป็นการคำนวณ ไม่ใช่ผลวัด"]))
    add(prompt_step(4, "เพิ่มเป็น 2 Worker แล้วสรุปเป็นกราฟ"))
    add(E.check_slide("step4", ["Worker 2 ตัวต่อคิวเดียวกัน (1 ตัวต่อ GPU 1 ใบ)",
                                "มีไฟล์ `code/report.py` · `metrics.json` และกราฟป้ายภาษาอังกฤษ 4 รูป",
                                "ตารางความจุ: จำนวน GPU · สถาปัตยกรรม · N · Throughput สูงสุด · p95 · เท่าของ 1 ใบ · Efficiency",
                                "มีประโยค \"1 ใบ N₁ คน → 2 ใบ N₂ คน (x เท่า, efficiency y%)\" และเวลาระบายคิวของ 1 และ 2 Worker",
                                "ค่า 3 GPU ถูกบอกว่าเป็น **การคำนวณ ไม่ใช่ผลวัด**"],
                      "ผลของผู้สอน: 1 ใบ 2 คน → 2 ใบ 4 คน (2.0 เท่า, Efficiency 100%) · ระบายงานถล่ม 651 → 319 s",
                      MAYDIFFER, "ขั้นที่ 4"))
    add(crop("GPU 2 ใบรองรับ 4 คน เป็น 2.0 เท่าของ GPU 1 ใบ", "img/c04-step4.jpg", "image/lab8-step4.png", SHOT[4]))
    t4 = table("ขั้นที่ 4 ", "N")
    add(chart_slide("คิว 2 Worker ผ่าน SLO ที่ N = 4 แล้วอิ่มตัวที่ราว 11 งาน/นาที", p95chart(
        ["N = %s" % plain(r[0]) for r in t4["rows"]],
        [("คิว 2 Worker · GPU 2 ใบ", C_Q2, [num(r[3]) for r in t4["rows"]], [plain(r[7]) for r in t4["rows"]])], 50),
        "ล้ม 0%% ทุกระดับ · งาน/นาที %s · รอคิว p95 %s" % (" / ".join(r[1] for r in t4["rows"]), " / ".join(r[5] for r in t4["rows"])),
        tag="results/queue_2worker/"))
    r4 = reads("ขั้นที่ 4 ")
    add(wide("ตอนงานถล่ม 2 Worker ระบายคิวหมดใน 319 วินาที เร็วกว่า 1 Worker (651 วินาที) 2 เท่า", "results/charts/burst_queue_length.png",
             r4, note("ทั้งสองเส้นขึ้นถึง 58 งานที่วินาทีที่ 10 · เส้นสีส้ม (2 Worker) ชันกว่าสองเท่า", label="อ่านกราฟ")))

    # ขั้นที่ 5
    CTX.update(kicker="ขั้นที่ 5 จาก 9 · ฆ่า Worker", group="ขั้นที่ 5 · ฆ่า Worker")
    add(step_div(5, "ส่ง 60 งาน · เสร็จ 60 · หาย 0 · ส่งซ้ำ 1 งาน"))
    add(explain("ขั้นที่ 5: ฆ่า Worker ของ GPU ใบที่ 2 กลางงานถล่ม แล้วนับงาน", "image/mq7-ack.png", [
        "**ส่งงานถล่ม 60 งาน** ภายใน 10 วินาที ขณะ Worker เปิดอยู่ 2 ตัว",
        "**ฆ่า Worker ของ GPU ใบที่ 2** แบบกะทันหัน (SIGKILL) ที่วินาทีที่ 20",
        "**รอจนงานหมดคิว** นับงานที่เสร็จ งานที่ถูกส่งซ้ำ และวาดกราฟงานเสร็จสะสมแยกตาม Worker",
        "**เก็บผลทั้งหมดกลับ** `results/` แล้วเปิด Worker ให้ครบ 2 ตัวอีกครั้ง"]))
    add(prompt_step(5, "ฆ่า Worker กลางงาน แล้วเก็บผลกลับ"))
    add(E.check_slide("step5", ["คำตอบบอก: ส่งกี่งาน · เสร็จกี่งาน · ส่งซ้ำกี่งาน · แต่ละ Worker ทำกี่งาน",
                                "จำนวนงานที่เสร็จเท่ากับจำนวนงานที่ส่ง (งานไม่หาย)",
                                "มีกราฟงานเสร็จสะสมตามเวลา แยกตาม Worker",
                                "`lab8_job_queue/results` มี JSON ของทุกการทดลอง `metrics.json` และกราฟ",
                                "Worker กลับมาเปิดครบ 2 ตัว และเครื่องยังเปิดอยู่"],
                      "ผลของผู้สอน: ส่ง 60 · เสร็จ 60 · หาย 0 · ส่งซ้ำ 1 · GPU0 ทำ 58 · GPU1 ทำ 2 · คิวว่างที่ 656 s",
                      MAYDIFFER, "ขั้นที่ 5"))
    add(crop("ฆ่า Worker ที่วินาทีที่ 20 แล้วงานยังเสร็จครบ 60 จาก 60", "img/c05-step5.jpg", "image/lab8-step5.png", SHOT[5]))
    k5 = table("ขั้นที่ 5 ", "ส่ง")
    h, r = k5["head"], k5["rows"][0]
    add(wide("งานไม่หาย: เสร็จ 60 จาก 60 และมีงานถูกส่งซ้ำเพียงงานเดียวที่อยู่ในมือ", "results/charts/worker_kill_cumulative.png", [
        "%s %s · %s %s · %s **%s** · %s **%s** · %s %s" % (h[0], r[0], h[1], r[1], h[2], plain(r[2]), h[3], plain(r[3]), h[5], r[5]),
        "%s %s งาน คือ `d8a6166ead19` ซึ่งอยู่ในมือ GPU1 ตอนถูกฆ่า และ GPU0 ทำเสร็จที่วินาทีที่ 33.2" % (h[4], r[4]),
        "%s %s งาน · %s %s งาน · %s %s" % (h[6], r[6], h[7], r[7], h[8], r[8])]))
    r5 = reads("ขั้นที่ 5 ")
    add(wide("ระบบช้าลงแต่ไม่พัง เพราะ 3 กลไกของ RabbitMQ ทำงานร่วมกัน", "img/n31-no-loss.jpg", r5))

    # ขั้นที่ 6
    CTX.update(kicker="ขั้นที่ 6 จาก 9 · เว็บดูคิว", group="ขั้นที่ 6 · เว็บดูคิว")
    add(step_div(6, "ส่งใบเสร็จ 6 ใบเป็น 6 งาน เสร็จครบ · Worker 2 ตัวรับงานสลับกัน 3 / 3"))
    add(nfig("n04-step6-web"))
    add(prompt_step(6, "สร้างเว็บดูคิวแบบสด แล้วทดสอบ"))
    add(E.check_slide("step6", ["เว็บเปิดที่ `http://localhost:3407` ด้วย docker compose ชื่อโปรเจกต์ `vapp-lab8`",
                                "หน้าเว็บเห็นความยาวคิว · การ์ด Worker แต่ละตัว · ตารางงานล่าสุด อัปเดตทุก 1 วินาที",
                                "ส่งใบเสร็จตัวอย่าง 6 ใบเป็น 6 งาน แล้วเสร็จทุกงาน · กดงานที่เสร็จแล้วเห็นรายการที่อ่านได้",
                                "API key อยู่ใน `code/web/.env` ฝั่ง server ของ Next.js · เบราว์เซอร์ไม่เห็น key",
                                "ลองส่งเป็นชุดใหญ่ (เช่น 60 งาน) แล้วดูคิวยาวขึ้นและหดลง"],
                      "ผลของผู้สอน: 6/6 งาน · GPU0 ทำ 3 งาน · GPU1 ทำ 3 งาน · รอคิว 0.0–5.9 s · อ่าน 2.0–5.0 s",
                      MAYDIFFER + " · ยอดรวมที่ Base Model อ่านได้ก็อาจต่างกัน", "ขั้นที่ 6"))
    r6 = reads("ขั้นที่ 6 ")
    add(tbl("ส่ง 6 งานผ่านเว็บ เสร็จครบ 6 จาก 6 และงานที่ส่งทีหลังรอคิวนานขึ้น (0.0 → 5.9 วินาที)", table("ขั้นที่ 6 ", "ใบเสร็จ"),
            post=note(r6[4] + " · ตารางเดียวกับในคำตอบจริง [ดูภาพหน้าจอเต็ม](image/lab8-step6.png)"), tag="ผลจริง"))
    add(wide("หน้าเว็บตอนส่ง 30 งาน: คิวยาว 27 งาน และ Worker ทั้ง 2 ตัวกำลังอ่าน", "results/web/web-queue-busy.png", r6[:3]))
    add(fig("กดงานที่เสร็จแล้ว จะเห็นรูปใบเสร็จคู่กับรายการที่อ่านได้", "results/web/web-job-result.png", r6[3]))
    add(fig("Worker 2 ตัวช่วยกันระบายคิว (ภาพเคลื่อนไหวแบบเร่งเวลา)", "results/web/web-drain-timelapse.gif",
            "ความยาวคิวลดลงจนเป็น 0 ขณะที่ตัวนับงานของ Worker ทั้ง 2 ตัวเพิ่มขึ้น"))

    # ขั้นที่ 7
    CTX.update(kicker="ขั้นที่ 7 จาก 9 · ลบเครื่อง", group="ขั้นที่ 7 · ลบเครื่อง")
    add(step_div(7, reads("ขั้นที่ 7 ")[0]))
    add(nfig("n05-step7-cleanup"))
    add(prompt_step(7, "ลบเครื่องและสรุปค่าใช้จ่าย"))
    add(E.check_slide("step7", ["`lab8_job_queue/results` มีผลครบ: JSON ของทุกการทดลอง · `metrics.json` · กราฟ",
                                "คำตอบมีประโยค \"ไม่มีเครื่องป้าย vapp-lab8 ค้างอยู่\"",
                                "ปิดเว็บใน `code/web` แล้ว",
                                "สรุปค่าใช้จ่ายจริง: อายุเครื่อง · ราคาต่อชั่วโมง · GPU · disk · รับส่งข้อมูล · รวม"],
                      "ผลของผู้สอน: เครื่องเปิด 1.985 ชั่วโมง · รวม **$0.781**",
                      "ค่าใช้จ่ายของคุณขึ้นกับราคาเครื่องที่ได้และเวลาที่ใช้ · ห้ามข้ามขั้นนี้ เครื่องที่ลืมลบคิดเงินต่อทุกชั่วโมง", "ขั้นที่ 7"))
    c7 = table("ขั้นที่ 7 ", "รายการ")
    r7 = reads("ขั้นที่ 7 ")
    add(crop("ลบเครื่องแล้ว ค่าใช้จ่ายของ LAB ทั้งหมดคือ $0.781", "img/c07-step7.jpg", "image/lab8-step7.png", [
        " · ".join("%s **%s**" % (plain(r[0]), plain(r[2])) if plain(r[0]) == "รวม" else "%s %s (%s)" % (plain(r[0]), plain(r[2]), r[1])
                   for r in c7["rows"]),
        SHOT[7][2], SHOT[7][0], SHOT[7][1], r7[1], r7[2]]))

    # ===== ส่วนที่ 4 · สกิลเวอร์ชัน 0 และสรุป
    CTX.update(kicker="", group="ส่วนที่ 4 · สกิลเวอร์ชัน 0")
    add(part_div(4, "เก็บงานทั้ง LAB เป็นสกิลเวอร์ชัน 0 แล้วสรุปผล", " ".join(para("ปิดท้าย", "เราเพิ่งสั่งงาน")["lines"]),
                 "img/p24-skill.jpg"))
    CTX["kicker"] = "ส่วนที่ 4 · สกิลเวอร์ชัน 0"
    add(fig("พรอมต์ 7 ขั้นที่สำเร็จแล้ว ถูกเก็บเป็นสกิลที่ทำซ้ำได้ใน 1 พรอมต์", "image/skill-v0.png",
            "SKILL.md บอก **ใช้เมื่อไร ค่าที่ปรับได้ ขั้นตอน และกติกาเรื่องเงิน** แล้วปรับเป็น v1 เมื่อพบจุดที่พลาด"))
    CTX.update(kicker="ขั้นที่ 8 จาก 9 · สร้างสกิล v0", group="ขั้นที่ 8 · สร้างสกิล v0")
    add(step_div(8, "สกิล `vlm-queue-capacity` เวอร์ชัน 0 ติดตั้งเป็นสกิลของโปรเจกต์ · ไฟล์ 7 ไฟล์ใน `scripts/`"))
    add(prompt_step(8, "สร้างสกิลเวอร์ชัน 0"))
    add(E.check_slide("step8", ["มีไฟล์ `lab8_job_queue/skill_v0/SKILL.md` ที่มี name และ description",
                                "SKILL.md มีค่าที่ปรับได้พร้อมค่าเริ่มต้น · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน",
                                "โค้ดที่ใช้ได้แล้ว (ยกเว้นเว็บ) อยู่ใน `skill_v0/scripts`",
                                "สกิลติดตั้งที่ `.claude/skills/vlm-queue-capacity` และเรียกใช้สกิล vastai ต่อ",
                                "ปิดแล้วเปิด Claude Code ใหม่ 1 ครั้งก่อนขั้นที่ 9"],
                      "ผลของผู้สอน: สร้างและติดตั้งแล้ว · ค่าที่ปรับได้ เช่น gpu · max_price $0.60 · label · levels · SLO",
                      "เนื้อหา SKILL.md ของคุณจะต่างจากของผู้สอน เพราะ AI เรียบเรียงจากงานของคุณเอง", "ขั้นที่ 8"))
    add(crop("สกิล vlm-queue-capacity ติดตั้งแล้ว แต่ยังไม่ได้ลองใช้จริง", "img/c08-step8.jpg", "image/lab8-step8.png", SHOT[8]
             + [alert("ขั้นที่ 8 ").replace("⚠️", "").strip()]))
    CTX.update(kicker="ขั้นที่ 9 จาก 9 · ลองใช้สกิล", group="ขั้นที่ 9 · ลองใช้สกิล")
    add(step_div(9, reads("ขั้นที่ 9 ")[0]))
    add(prompt_step(9, "ลองใช้สกิลทำซ้ำในคำสั่งเดียว"))
    add(E.check_slide("step9", ["AI ใช้สกิล `vlm-queue-capacity` เช่าเครื่องป้าย `vapp-lab8-skill` เอง",
                                "ได้ตารางความจุ 1 / 2 GPU เทียบ Baseline กับคิว 1 และ 2 Worker",
                                "ผลอยู่ใน `results/skill_v0_run` ไม่เขียนทับผลเดิม",
                                "เครื่องถูกลบเมื่อจบ และมีค่าใช้จ่ายจริง"],
                      "ผลของผู้สอน: Baseline 2 คน · คิว 1 Worker 2 คน · คิว 2 Worker 4 คน (2.0 เท่า) · $0.478",
                      "เวลาระบายคิวของคุณอาจต่างไปตามเครื่องที่ได้ แต่อัตราส่วนราว 2 เท่าควรคงอยู่", "ขั้นที่ 9"))
    add(crop("รอบที่ใช้สกิลได้ข้อสรุปเดิม: 1 ใบ 2 คน → 2 ใบ 4 คน", "img/c09-step9.jpg", "image/lab8-step9.png", SHOT[9]))
    sv = table("ขั้นที่ 9 ", "")
    g = lambda k: row(sv, k)
    add(S("สั่งทีละขั้นใช้ 7 พรอมต์ ส่วนสกิล v0 ใช้ 1 พรอมต์และได้ผลเดียวกัน", tiles([
        ("จำนวนพรอมต์", "%s → %s" % (g("จำนวนพรอมต์")[1], plain(g("จำนวนพรอมต์")[2])), "สั่งทีละขั้น → สกิล v0", "ok"),
        ("1 ใบ → 2 ใบ", plain(g("1 ใบ")[2]), "รอบหลัก: " + plain(g("1 ใบ")[1]), "ok"),
        ("คิว 2 Worker", plain(g("คิว 2 Worker")[2]).split(" · ")[0], "ระบายงานถล่ม %s (รอบหลัก %s)" % (
            plain(g("คิว 2 Worker")[2]).split(" · ")[1].replace("ระบายงานถล่ม ", ""),
            plain(g("คิว 2 Worker")[1]).split(" · ")[1].replace("ระบายงานถล่ม ", "")), ""),
        ("เครื่องเปิด / ค่าใช้จ่ายจริง", plain(g("เครื่องเปิด")[2]), "รอบหลัก: " + plain(g("เครื่องเปิด")[1]), ""),
    ]), cls="mid"))
    r9 = reads("ขั้นที่ 9 ")
    add(wide("ตัวเลขเปลี่ยนตามเครื่อง แต่อัตราส่วน 2 เท่ายังคงอยู่", "results/skill_v0_run/charts/scaling_vs_gpus.png", r9[1:],
             note("กราฟจริงของรอบที่ใช้สกิล (`results/skill_v0_run/charts/`)", label="กราฟ")))
    v0 = table("ขั้นที่ 9 ", "จุดที่ v0")
    add(wide("สกิล v0 ยังมี 5 จุดที่ต้องแก้ในเวอร์ชันถัดไป", "img/n33-v0-fixes.jpg", [
        "ข้อ 2 มีผลต่อการวัด: " + plain(v0["rows"][1][0]).split("จึงมี ", 1)[-1],
        "ข้อ 5: " + plain(v0["rows"][4][0]),
        "วิธีปรับคือสั่ง AI ด้วยพรอมต์อีก 1 พรอมต์ให้แก้สกิลตามรายการนี้ แล้วลองใช้ซ้ำ"]))

    # ===== สรุป
    CTX.update(kicker="สรุป", group="สรุป")
    add(fig("ทุกแบบวัดด้วยเกณฑ์เดียวกัน: Synchronous 2 คน คิว 1 Worker 2 คน คิว 2 Worker 4 คน", "results/charts/latency_vs_users.png",
            "ดาวแต่ละดวงคือ N มากที่สุดที่ p95 ยังอยู่ใต้เส้น SLO 20 วินาที"))
    add(tbl("ตารางสรุป: 1 ใบ 2 คน → 2 ใบ 4 คน (2.0 เท่า, Efficiency 100%)", main,
            post=note(" ".join(para("ทำไปเพื่ออะไร", "ตัวเลขเป็นจำนวนเต็ม")["lines"]))))
    add(fig("สิ่งที่ได้เรียนรู้จาก LAB นี้มี 4 ข้อ", "img/n34-lessons.jpg",
            "อยากรับ 10 คนที่ R ≤ 20 วินาที ต้องมี X ≥ 0.33 งาน/วินาที ≈ **4 Worker** (ค่าคำนวณจาก Little's Law)"))
    add(fig("ข้อจำกัด: สิ่งที่ LAB นี้ไม่ได้วัด", "img/n35-limits.jpg",
            "ตัวเลข 3 GPU คำนวณจาก 1 ใบ × 3 × Efficiency ที่วัดได้ตอน 2 ใบ โดยสมมติว่า gateway, RabbitMQ และ CPU ยังไม่เป็นคอขวด"))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบ LAB 8", "รายละเอียดเต็ม ผลดิบ และโค้ดตัวอย่างอยู่ใน README",
                  '<p>อ่านต่อ: <a href="README.md" target="_blank">README.md</a> · พรอมต์ทั้ง 9 ขั้น: '
                  '<a href="PROMPTS.md" target="_blank">PROMPTS.md</a> · ผลทั้งหมด: '
                  '<a href="results/metrics.json" target="_blank">results/metrics.json</a></p>'))
    return E.SL


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
