#!/usr/bin/env python3
"""สร้างสไลด์ LAB6_Image_API_Slides.html ของ LAB 6 (API ตรวจภาพ YOLO · ความจุผู้ใช้พร้อมกัน)

  python tools/build_slides.py            (รันจากโฟลเดอร์ของบท)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · อธิบายด้วยภาพก่อน ข้อความข้างภาพไม่เกิน 3 ข้อ · ตารางเฉพาะผลที่ต้องอ่านรายแถว
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง โค้ด และพรอมต์: อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร จาก code fence ชนิด text ของแต่ละขั้น)
- ข้อความที่เรียบเรียงในไฟล์นี้: ตัวเลขทุกตัวถูกตรวจด้วย Q() ว่ามีอยู่ใน README.md จริง (ไม่มีตัวเลขที่พิมพ์ขึ้นเอง)
- ภาพคำตอบจริงของ Claude Code: img/cNN-stepN.jpg คือส่วนที่ตัดจาก image/lab6-stepN.png (ไม่แก้พิกเซล) มีลิงก์ไปภาพเต็ม
- ภาพอธิบายใหม่และขั้นตอนข้างภาพ: tools/slides_figures.py · เครื่องมือเรนเดอร์: tools/slides_engine.py
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, codes, para, CTX, add, note, fig, explain, tiles, cards,
                           versus)
from slides_figures import FIGS, FIGS2

S = E.slide
SECS = E.load("README.md")
FIG = {f["img"]: f for f in FIGS + FIGS2}
OUT, TITLE = "LAB6_Image_API_Slides.html", "LAB 6 · API ตรวจภาพ YOLO · Slides"
README = E.read("README.md")
NSTEP = 11

# รูปแบบเฉพาะของเด็คนี้ (ไม่แก้ engine): ข้อความหลักบนภาพถ่าย · ภาพคำตอบจริงเต็มกว้าง + 3 ข้อด้านล่าง · ภาพ + โค้ด
E.CSS += r"""
.stmt{padding:0;background-size:cover;background-position:center;color:#fff}
.stmt .shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,13,26,.94) 0%,rgba(6,13,26,.8) 48%,rgba(6,13,26,.15) 82%)}
.stmt .inner h1{font-size:50px;line-height:1.3;margin-top:auto}
.stmt .inner .sub{font-size:27px;margin-bottom:auto}
.shot{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:14px}
.shot .fig{flex:1 1 0;min-height:180px}
.shot .pts{flex:none;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.shot .pts .stp{font-size:.8em;align-items:flex-start}
.shot .src{flex:none;font-size:.7em;color:var(--muted);text-align:center;line-height:1.4}
.figcode{flex:1 1 0;min-height:0;display:flex;gap:26px;align-items:center}
.figcode .fig{flex:1.25 1 0;height:100%;min-width:0}
.figcode .side{flex:1 1 0;min-width:0}
.figcode pre.code{font-size:.66em}
.divider .inner .big{margin-top:30px;line-height:1.2}
"""


# ------------------------------------------------------------------ ตัวช่วย
def Q(s):
    """ตรวจว่าตัวเลขทุกตัวในข้อความที่เรียบเรียงเองมีอยู่ใน README.md · คืนข้อความเดิม"""
    for num in re.findall(r"\d[\d,]*(?:\.\d+)?", E.plain(s)):
        if num not in README:
            raise ValueError("ตัวเลข %r ไม่มีใน README.md: %s" % (num, s))
    return s


def QL(items):
    return [Q(x) for x in items]


def row(t, key):
    for r in t["rows"]:
        if E.plain(r[0]).startswith(key):
            return r
    raise KeyError("ไม่พบแถว %r" % key)


def cell(t, key, col):
    return E.plain(row(t, key)[col]).replace("¹", "").strip()


def tbl(title, t, pre="", post="", tag="ตารางหลัก"):
    """ตารางหลัก · ตัด *ตัวเอียง* ของ Markdown ที่ engine ไม่แปลง"""
    t = dict(t, rows=[[c[1:-1] if len(c) > 2 and c[0] == "*" and c[-1] == "*" and c[1] != "*" else c for c in r] for r in t["rows"]])
    return E.tbl(title, t, pre, post, tag)


def nfig(key, title=None):
    f = FIG[key]
    return explain(title or f["title"], "img/%s.jpg" % key, f["steps"])


def step(n):
    return sec("ขั้นที่ %d ·" % n)


def step_title(n):
    for s in SECS:
        if s["text"].startswith("ขั้นที่ %d ·" % n):
            return s["text"].split("·", 1)[1].strip()
    raise KeyError(n)


def first_p(n):
    return " ".join(next(b for b in step(n) if b["t"] == "p")["lines"])


def took(n):
    """เวลาจริงของขั้น จากบรรทัดตัวเอียงใต้ภาพคำตอบ"""
    for b in step(n):
        if b["t"] == "p" and b["lines"][0].startswith("*ใช้เวลา"):
            return b["lines"][0].strip("*").split(" · ")[0].strip()
    raise KeyError(n)


def alert_text(blocks, k=0):
    al = [b for b in walk(blocks) if b["t"] == "alert"][k]
    return " ".join(" ".join(x["lines"]) for x in al["blocks"] if x["t"] == "p").replace("⚠️", "").strip()


def shot(n, title, pts, src_note=""):
    """ส่วนหนึ่งของคำตอบจริงของ Claude Code ในขั้น n (ตัดจากภาพเต็ม ไม่แก้พิกเซล) แสดงเต็มกว้าง + 3 ข้อด้านล่าง"""
    img = E.img_tag({"t": "img", "src": "img/c%02d-step%d.jpg" % (n, n), "alt": E.plain(title)})
    side = "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(Q(x))) for k, x in enumerate(pts))
    src = ('ส่วนหนึ่งของคำตอบจริง%s · <a href="image/lab6-step%d.png" target="_blank">เปิดภาพคำตอบเต็ม</a>'
           % ((" · " + md(Q(src_note))) if src_note else "", n))
    return S(Q(title), '<div class="shot"><div class="fig">%s</div><div class="pts">%s</div><p class="src">%s</p></div>' % (img, side, src),
             tag="คำตอบจริง", maxfs=1.25)


def statement(kicker, quote, sub, img):
    """ข้อความหลักตัวใหญ่บนภาพถ่าย"""
    raw = ('<div class="shade"></div><div class="inner"><div class="small">%s</div><h1>%s</h1><div class="sub">%s</div>'
           '<div class="imgnote">ภาพจำลอง</div></div>') % (kicker, md(quote), sub)
    return {"raw": raw, "cls": "stmt", "style": ' style="background-image:url(%s)"' % img, "title": E.plain(quote),
            "kicker": "", "tag": "", "lead": ""}


def figcode(title, src, code_text, lang, post=""):
    img = E.img_tag({"t": "img", "src": src, "alt": E.plain(title)})
    return S(title, '<div class="figcode"><div class="fig">%s</div><div class="side">%s%s</div></div>'
             % (img, E.pre_html(code_text, lang), post), maxfs=1.2)


def divider(n, result):
    sub = '<p>%s</p><p>เวลาจริง: <b>%s</b> · ผลจริง: <b>%s</b></p>' % (md(first_p(n)), took(n), md(Q(result)))
    return E.divider("ขั้นที่ %d" % n, step_title(n), sub, small="ภาค LAB · ขั้นที่ %d จาก %d" % (n, NSTEP))


def check(n, items, ref, note_text="ตัวเลขของคุณต่างจากของผู้สอนได้ เพราะโค้ดเป็นของ AI ในรอบของคุณและเครื่องที่เช่าได้ต่างกัน"):
    return E.check_slide("s%d" % n, QL(items), Q(ref), note_text, "ขั้นที่ %d · %s" % (n, step_title(n)))


def prompt_of(n):
    return E.prompt_slides(E.prompt_code("ขั้นที่ %d ·" % n), CTX["kicker"], "ขั้นที่ %d · %s" % (n, step_title(n)))


def group(n):
    CTX.update(kicker="ภาค LAB · ขั้นที่ %d จาก %d · %s" % (n, NSTEP, step_title(n)), group="ขั้นที่ %d · %s" % (n, step_title(n)))


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    T = table("การทดลอง", "จำนวน GPU")                     # ตารางผลสรุปของทั้ง LAB
    r1, r2, r3, r4 = T["rows"][:4]
    cap = lambda r: E.plain(r[2]).replace("¹", "").strip()

    # ===== 1 · เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    add(E.cover("LAB 6 · API ตรวจภาพ YOLO", "GPU 1 ใบรับผู้ใช้พร้อมกันได้กี่คน แล้วเพิ่มด้วย Micro-batching, หลาย process และ Load Balancer เป็น 2 ใบ",
                "img/s01-cover.jpg", small="สัปดาห์ที่ 3 · 02 VastAi Application · LAB 6"))
    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("GPU ใบเดิมรับได้ %s → %s → %s คน และ 2 GPU รับได้ %s คน ภายใต้เกณฑ์เดียวกัน" % (cap(r1), cap(r2), cap(r3), cap(r4)),
            "image/why5-api.png", "ทุกแบบใช้เกณฑ์เดียวกัน: **Latency p95 ≤ 500 ms และ error < 1%**"))
    add(fig("บทนี้มี 3 ภาค: พื้นฐานและทฤษฎี, LAB ขั้นที่ 1–9 และสกิลเวอร์ชัน 0", "img/n23-plan.jpg",
            Q("ภาคพื้นฐานมีทฤษฎี 9 ข้อ · ภาค LAB วัด 4 แบบและทดลองเสริม 2 เรื่อง · ขั้นที่ 10–11 เก็บงานทั้งหมดเป็นสกิล")))
    add(S("วิธีใช้สไลด์ชุดนี้", cards([
        ("เลื่อนหน้า", '<p>กด <span class="kbd">→</span> หรือ <span class="kbd">Space</span> ไปต่อ · <span class="kbd">←</span> ย้อนกลับ · <span class="kbd">O</span> สารบัญ · <span class="kbd">F</span> เต็มจอ</p>'),
        ("คลิกภาพเพื่อขยาย", "ภาพคำตอบของ Claude Code ในสไลด์เป็นส่วนที่ตัดมา ลิงก์ใต้ภาพเปิดภาพคำตอบเต็ม"),
        ("ปุ่มคัดลอกพรอมต์", "หน้าพรอมต์ทุกหน้ามีปุ่ม **คัดลอกพรอมต์ทั้งหมด** ได้ข้อความตรงกับ README ทุกตัวอักษร แม้พรอมต์ถูกแบ่งแสดง 2 หน้า"),
        ("รายการตรวจผล", "หลังรันแต่ละขั้น ให้ติ๊กสิ่งที่เห็นในผลของคุณ เบราว์เซอร์จำค่าที่ติ๊กไว้ แล้วเทียบกับผลของผู้สอนใต้รายการ"),
    ], 2), cls="mid"))

    # ===== 2 · ภาคพื้นฐาน
    CTX.update(kicker="ภาคพื้นฐาน · โจทย์ ข้อมูล และโมเดล", group="ภาคพื้นฐาน · โจทย์ ข้อมูล โมเดล")
    add(E.divider("ภาคพื้นฐาน", "โจทย์ ข้อมูล โมเดล และทฤษฎีที่ต้องรู้", "<p>ก่อนวัด ต้องรู้ว่าวัดอะไร ด้วยเกณฑ์อะไร และตัวเลขแต่ละตัวหมายถึงอะไร</p>"))
    add(statement("โจทย์ของเจ้าของระบบ", "GPU 1 ใบ รองรับผู้ใช้พร้อมกันได้กี่คน แล้วออกแบบระบบอย่างไรให้รับได้มากขึ้น",
                  "<p>เราไม่เดา แต่<b>วัดจริง</b> 4 แบบบนเครื่องเดียวกัน ด้วยเกณฑ์เดียวกัน</p>", "img/p20-owner.jpg"))
    add(fig("ข้อมูลทดสอบคือชุดคำขอ: รูปหน้างานก่อสร้าง 6 รูป ที่ผู้ใช้จำลองทุกคนส่งวนไป", "results/dataset_samples.jpg",
            Q("รูป 640 × 640 px ขนาด 40.7–78.1 KB จาก Test Set ของ Construction Site Safety รุ่น 28 (CC BY 4.0) · `sample-4` มีวัตถุ 79 ชิ้น หนักกว่ารูปอื่น")))
    add(figcode("คำขอ 1 ครั้ง: ส่งรูปพร้อม API key ไปที่ `POST /v1/detect` แล้วได้ JSON กลับ", "img/n24-request.jpg",
                codes("รู้จักข้อมูลที่ใช้ทดสอบ", "json")[0]["text"], "json",
                '<p class="cap">%s</p>' % md(Q("ตัวอย่างจริงของ `sample-3.jpg` (ตัดรายการวัตถุให้สั้น) · `box` คือกรอบ [x1, y1, x2, y2] "
                                              "เป็นพิกเซล · `confidence` ขั้นต่ำ 0.35"))))
    add(fig("โมเดล YOLO11s จาก LAB 1: รับภาพ 1 รูป ตอบเป็นกรอบ คลาส และ Confidence", "image/model-yolo11s.png",
            " ".join(para("รู้จักโมเดลที่ใช้", "โมเดลเล็กแบบนี้")["lines"])))

    CTX.update(kicker="ภาคพื้นฐาน · ทฤษฎีที่ต้องรู้", group="ภาคพื้นฐาน · ทฤษฎี")
    add(fig("1 · เพิ่มผู้ใช้หลังระบบอิ่มตัว ได้คิวที่ยาวขึ้น ไม่ได้ Throughput เพิ่ม", "image/t5-users-throughput.png",
            Q("`Latency เฉลี่ย ≈ N ÷ Throughput` (กฎของ Little) · ที่ N=32: 32 ÷ 61.5 ≈ 520 ms วัดจริง p50 = 515 ms")))
    add(fig("2 · ค่าเฉลี่ยซ่อนคนที่โชคร้าย เกณฑ์คุณภาพจึงตั้งที่ p95", "image/t5-percentile.png",
            Q("2 GPU ที่ N=64 รอบแรก p50 = 93 ms แต่ p95 = 1,752 ms · วัดซ้ำ 3 ครั้ง p95 ได้ 147 / 145 / 149 ms")))
    add(fig("3 · รองรับได้ N คน คือ N สูงสุดที่ผ่าน SLO โดยทุกระดับที่ต่ำกว่าก็ผ่านด้วย", "image/t5-slo-knee.png",
            alert_text(sec("3 · SLO"))))
    add(fig("4 · Closed-loop: ผู้ใช้ N คนส่งรูป รอคำตอบ แล้วส่งรูปถัดไปทันที", "image/t5-closed-loop.png",
            Q("ตัวยิงโหลดอยู่บนเครื่องเดียวกับ server · เรียกจากนอกเครื่องใช้ราว 1.1 วินาทีต่อคำขอ แต่ยิงในเครื่องใช้ 26–38 ms")))
    add(fig("4 · วัดครั้งเดียวเชื่อไม่ได้: ทั้ง 2 เหตุการณ์ ผลหลังวัดซ้ำต่างจากผลครั้งแรก", "img/n25-remeasure.jpg",
            Q("ระบบ 2 GPU: N=64 วัดซ้ำ 3 ครั้งผ่านหมด และ N=128, 160, 176 ผ่าน · Baseline: 18 คน 39.5 req/s → 22 คน 63 req/s "
              "· ระดับที่ไม่ผ่านเพียงครั้งเดียวขณะที่ระดับสูงกว่าผ่าน ให้วัดซ้ำก่อนสรุป และรายงานทั้งสองค่า")))
    add(fig("5 · แบบทีละคำขอ GPU ทำงานเพียง 20%: คอขวดคือ Python process เดียว ไม่ใช่ GPU", "image/t5-bottleneck.png",
            alert_text(sec("5 · หาคอขวด"))))
    add(fig("6 · ปัญหา: server เรียกโมเดลทีละรูป คำขอต่อคิวทั้งที่ GPU ยังว่าง", "image/mb-problem.png",
            "เวลาเรียกโมเดลราว 15 ms ต่อรูปเท่าเดิม แต่ **เวลารอคิว** โตตาม N"))
    add(fig("6 · Micro-batching: รวมคำขอที่มาใกล้กันเป็นชุดเดียว แล้วเรียกโมเดลครั้งเดียว", "image/mb-how.png",
            "รวมได้สูงสุด 32 รูป รอคำขอเพิ่มไม่เกิน 5 ms · ขนาด batch ปรับตามโหลดเอง"))
    add(fig("6 · ผล: GPU ใบเดิมรองรับ 22 → 52 คน (2.4 เท่า)", "image/mb-result.png", alert_text(sec("6 · Micro-batching"))))
    add(fig("7 · หลาย process ต่อ GPU 1 ใบ: 52 → 104 คน เพราะ Python 1 process ใช้ CPU ได้ทีละ 1 core", "image/mp-how.png",
            alert_text(sec("7 · หลาย process"))))
    add(fig("8 · Load Balancer คือประตูเดียวที่แจกงานให้หลาย replica", "image/lb-what.png",
            Q("NGINX ใช้ CPU 0.48 core ที่ 650 req/s จึงไม่ใช่คอขวด · คำขอกระจาย 49.6% / 50.4%")))
    add(fig("8 · เมื่อมี replica ช้า least_conn ส่งงานตามงานค้าง จึงดีกว่าการแจกวนเท่ากัน", "image/lb-rr-vs-lc.png",
            alert_text(sec("8 · Load Balancer"), 0)))
    add(fig("8 · เมื่อ replica ล่มกลางทาง NGINX ต้องส่งคำขอที่ล้มต่อให้ตัวอื่น (retry)", "image/lb-failover.png",
            alert_text(sec("8 · Load Balancer"), 1)))
    add(fig("9 · Throughput เพิ่ม 2.00 เท่า แต่ความจุเพิ่ม 1.69 เท่า เพราะความจุตัดสินด้วย p95", "image/t5-efficiency.png",
            Q("`Speedup = ความจุ k ใบ ÷ ความจุ 1 ใบ` · `Efficiency = Speedup ÷ k` · **3 ใบเป็นค่าคำนวณ ไม่ใช่ผลวัด**")))

    # ===== 3 · ภาค LAB
    CTX.update(kicker="ภาค LAB · แผนที่", group="ภาค LAB · แผนที่และสิ่งที่ต้องมี")
    add(E.divider("ภาค LAB", "11 ขั้น 11 พรอมต์ บนเครื่องเช่าเครื่องเดียว",
                  Q("<p>ขั้นที่ 1–9 คืองานหลัก · ขั้นที่ 10–11 เก็บงานทั้งหมดเป็นสกิลเวอร์ชัน 0</p>"), "img/s02-lab.jpg"))
    add(fig("ทุกขั้นคือ 1 พรอมต์ และโค้ดทุกไฟล์ AI เขียนให้จากโฟลเดอร์ว่าง", "image/lab6-overview.png",
            "ทำตามลำดับขั้นที่ 1 → 11 ให้ครบในรอบเดียว"))
    add(fig("ก่อนเริ่ม LAB ต้องเตรียม 5 อย่าง", "img/n26-prereq.jpg",
            Q("key 3 ตัวมาจาก [LAB 0](../README.md) · โค้ดที่ AI เขียนจะอยู่ใน `lab6_image_api/code/` ซึ่งตอนเริ่มยังไม่มี · "
              "เครื่องเปิดค้างและคิดเงินตั้งแต่ขั้นที่ 1 ถึงขั้นที่ 9")))
    add(fig("วัด 4 แบบบนเครื่องเดียวกัน ด้วยเกณฑ์ p95 ≤ 500 ms และ error < 1%", "image/lab6-system.png",
            Q("ไล่ N = 1, 4, 16, 32, 64, 128, 256, 512, 1024 ระดับละ 20 วินาที ไม่นับ 5 วินาทีแรก · ตัวยิงโหลดรันบนเครื่องเดียวกับ server · "
              "เครื่อง RTX 3090 2 ใบ เพดาน $0.60 ต่อชั่วโมง (ได้จริง $0.395) ได้ใช้ CPU ราว 27 core")))

    # ----- ขั้นที่ 1
    group(1)
    add(divider(1, "RTX 3090 2 ใบ $0.395 ต่อชั่วโมง · ได้ใช้ CPU 27.4 cores"))
    add(nfig("n01-step1-rent"))
    add(prompt_of(1))
    add(check(1, ["ได้เครื่องที่มี **RTX 3090 2 ใบในเครื่องเดียว** ป้าย `vapp-lab6` ราคารวมไม่เกิน **$0.60 ต่อชั่วโมง**",
                  "CPU ที่ได้ใช้จริง **24 cores ขึ้นไป** (ไม่ใช่จำนวน core ที่เครื่องแสดง)",
                  "เปิดพอร์ต **8080** แล้ว และเข้าไปเห็น **GPU ครบ 2 ใบ**",
                  "AI สรุปตาราง GPU · ราคาต่อชั่วโมง · ที่ตั้ง · CPU cores · เวลาที่รอ แล้วบอกว่า **เครื่องยังเปิดอยู่**"],
                 "ผลของผู้สอน: RTX 3090 2 ใบ ใบละ 24 GB · $0.395 ต่อชั่วโมง · California · ได้ใช้ CPU 27.4 cores จากทั้งเครื่อง 192 · รอจนพร้อมราว 8 นาที 22 วินาที",
                 "เครื่อง ราคา และเวลารอของคุณต่างจากนี้ได้ ขึ้นกับเครื่องที่ว่างในตลาดขณะนั้น"))
    add(shot(1, "ได้ RTX 3090 2 ใบ ราคา $0.395 ต่อชั่วโมง และได้ใช้ CPU จริง 27.4 core", [
        "เช่า **2 ใบตั้งแต่แรก** แม้ขั้นที่ 2–5 ใช้ใบเดียว เพื่อให้ทุกแบบวัดบนเครื่องเดียวกัน",
        "เครื่องแสดง CPU 192 core แต่ได้ใช้จริง **27.4 core** ซึ่งสำคัญ เพราะงานส่วนใหญ่ของ LAB นี้อยู่ที่ CPU",
        "ราคาตอนค้น $0.353 รวมค่า disk 40 GB เป็น $0.395 ต่อชั่วโมง และ **เริ่มคิดเงินตั้งแต่ขั้นนี้** จนลบเครื่องในขั้นที่ 9"]))

    # ----- ขั้นที่ 2
    group(2)
    add(divider(2, "6 รูปได้คำตอบครบ · ไม่มี key ได้ 401 · โมเดลราว 24 ms ต่อรูป"))
    add(nfig("n20-step2-server"))
    add(prompt_of(2))
    add(check(2, ["มี `lab6_image_api/code/server.py` (FastAPI) และ server เปิดบน **GPU ใบแรก** พอร์ต 8080 โหมดทีละคำขอ",
                  "`/health` ตอบว่าพร้อม หลังอุ่นโมเดลครบทุกขนาด batch",
                  "ส่งรูปทั้ง 6 รูปพร้อม key ได้คำตอบครบ · ส่งแบบไม่มี key ได้ **401**",
                  "JSON มีช่อง `detections` `replica` `timing_ms` `batch_size` และ AI อธิบายแต่ละช่อง",
                  "มีภาพ `lab6_image_api/results/dataset_samples.jpg` และ **ไม่มีค่า key** ในคำตอบ"],
                 "ผลของผู้สอน: 6 รูปได้ 200 ครบ · ไม่มี key ได้ 401 · sample-3 เจอ 7 วัตถุ · โมเดลเฉลี่ยราว 24 ms ต่อรูป · เรียกจากนอกเครื่องราว 1.1 วินาที"))
    add(shot(2, "เวลาภายใน server ราว 30 ms แต่วัดจากนอกเครื่องได้ราว 1.1 วินาที", [
        "ส่งรูปทั้ง 6 รูปพร้อม key ได้คำตอบ 200 ครบ ส่วนคำขอที่ไม่มี key หรือ key ผิดได้ **401** และ key ไม่ปรากฏในคำตอบ",
        "ส่วนต่างเกือบทั้งหมดคือเวลาของเครือข่าย ขั้นที่ 4 จึงให้ **ตัวยิงโหลดรันบนเครื่องเดียวกับ server**",
        "server อุ่นโมเดลครบทุกขนาด batch ก่อนตอบว่าพร้อม และมีโหมด Micro-batching ที่ยังไม่เปิดใช้จนถึงขั้นที่ 5"]))

    # ----- ขั้นที่ 3
    group(3)
    add(divider(3, "ผู้ใช้เข้าได้ทางเดียวคือ NGINX พอร์ต 8080"))
    add(nfig("n03-step3-cluster"))
    add(prompt_of(3))
    add(check(3, ["มี `lab6_image_api/code/cluster.sh` เปิดระบบด้วยค่า 3 ตัว (replica · process · batch) มีคำสั่งดูสถานะและปิด",
                  "NGINX ฟังพอร์ต **8080** · server ฟังภายในเครื่องเท่านั้น",
                  "ระบบเปิดแบบพื้นฐาน: replica 1 ตัว 1 process batch = 1",
                  "ทดสอบผ่าน 8080: `/health` · ส่งรูปพร้อม key ได้คำตอบ · ไม่มี key ได้ **401**",
                  "AI วาดแผนภาพข้อความเส้นทางของคำขอ และไม่แสดงค่า key"],
                 "ผลของผู้สอน: ผู้ใช้ → พอร์ตภายนอกของ Vast.ai → NGINX พอร์ต 8080 → server พอร์ต 9000 → GPU 0 · ส่งรูปได้ 200 เจอ 18 วัตถุ · ยิงตรงพอร์ต 9000 จากนอกเครื่องเข้าไม่ได้"))
    add(shot(3, "คำขอทุกครั้งผ่าน NGINX พอร์ต 8080 ส่วนพอร์ต 9000 ของ server เข้าจากนอกเครื่องไม่ได้", [
        "`cluster.sh` มีคำสั่ง up, status และ down · การเพิ่ม process (ขั้นที่ 5) และ replica (ขั้นที่ 6) ใช้คำสั่งเดิม เปลี่ยนเพียงตัวเลข 3 ตัว",
        "AI ลด worker ของ NGINX เหลือ 8 ตัว เพราะค่าปกติจะเปิดเท่าจำนวน core ที่เครื่องแสดง (192) ซึ่งเกินจำเป็น",
        "header `X-Upstream` ในคำตอบบอกว่า process ใดเป็นผู้ตอบ ใช้ตรวจการแจกงานในขั้นถัดไป"]))

    # ----- ขั้นที่ 4
    group(4)
    add(divider(4, "GPU 1 ใบ แบบทีละคำขอ รองรับ 22 คน (63 req/s)"))
    add(explain("ขั้นที่ 4: ตัวยิงโหลดจำลองผู้ใช้ N คน แล้วไล่ N จนเกินเกณฑ์", "image/t5-closed-loop.png", QL([
        "เขียน `loadgen.py` รัน **บนเครื่องเดียวกับ server** ยิงเข้าทาง Load Balancer · รอเกิน 10 วินาทีนับเป็น error",
        "ไล่ N = 1, 4, 16, 32, 64, 128, 256, 512, 1024 ระดับละ 20 วินาที (5 วินาทีแรกเป็น warm-up)",
        "หยุดเมื่อไม่ผ่าน 2 ระดับติดกัน แล้ว **ซอยครึ่ง** หา N ที่พอดีเกณฑ์อีก 3 รอบ",
        "เก็บ Throughput · p50 p95 p99 · error · GPU · CPU ของทุกส่วน คู่กันทุกระดับ แล้ววัดระบบพื้นฐาน ตั้งชื่อผลว่า `base1`"])))
    add(prompt_of(4))
    add(check(4, ["มี `lab6_image_api/code/loadgen.py` และผล `base1` เป็น JSON ในโฟลเดอร์ results บนเครื่อง",
                  "การวัดจบด้วยคำว่า **DONE**",
                  "ตารางทุกระดับ N มี Throughput · p50 / p95 / p99 · error · GPU · CPU",
                  "มีประโยค \"GPU 1 ใบ รองรับผู้ใช้พร้อมกันได้ N คน ที่ p95 ≤ 500 ms\"",
                  "AI บอก GPU utilization ตอนเต็มความจุ และคอขวดอยู่ที่ไหน"],
                 "ผลของผู้สอน (วัดซ้ำบน server ฉบับแก้แล้ว): 22 คน · 63 req/s · p95 368 ms · GPU ราว 20% · คอขวดคือ Python process เดียว · การวัดครั้งแรกได้ 18 คน / 39.5 req/s"))
    bt = table("ขั้นที่ 4 ·", "N")
    add(tbl("ผลจริง base1: p95 ผ่านถึง N=22 แล้วเกิน 500 ms ตั้งแต่ N=24", bt,
            post=note(" ".join(para("ขั้นที่ 4 ·", "**GPU 1 ใบ แบบทีละคำขอ")["lines"]), label="สรุป")))
    add(fig("เวลาเรียกโมเดลคงที่ราว 15 ms ส่วนเวลารอคิวโตตาม N", "results/time_breakdown_base1.png",
            Q("ดูแท่งสีแดง: เวลารอใน server โตจาก 254 ms (N=16) เป็น 514 ms (N=32) และ 1,387 ms (N=64)")))
    add(shot(4, "GPU 1 ใบแบบทีละคำขอรองรับ 22 คน ขณะที่ GPU ทำงานเพียงราว 20%", [
        "Throughput แบนที่ราว 61–63 req/s ตั้งแต่ N=16 ซึ่งเท่ากับ 1 ÷ เวลาเรียกโมเดลราว 15–16 ms เพิ่มผู้ใช้จึงได้เพียงคิวที่ยาวขึ้น",
        "NGINX และตัวยิงโหลดใช้ CPU ราว 0.05 core จึงไม่ใช่คอขวด และไม่รบกวนผลวัด",
        "Throughput ของแต่ละระดับแกว่งได้ (46–63 req/s) จากการวัดเพียง 15 วินาที ความจุจึงมีความละเอียดราว ±2 คน"],
        "การวัดซ้ำด้วยพรอมต์เดิม · การวัดครั้งแรกได้ 18 คน / 39.5 req/s บน server ที่ยังมีบั๊ก"))

    # ----- ขั้นที่ 5
    group(5)
    t5 = table("ขั้นที่ 5 ·", "")
    hd = [E.plain(h) for h in t5["head"]]
    add(divider(5, "GPU ใบเดิม 22 → 52 → 104 คน (4.7 เท่า) ค่าเช่าเท่าเดิม"))
    add(explain("ขั้นที่ 5: ไม่เขียนโค้ดใหม่ เปิดระบบใหม่ 2 แบบบน GPU ใบเดิม แล้ววัดซ้ำ", "img/n27-step5-configs.jpg", QL([
            "**Micro-batching**: replica 1 ตัว 1 process batch = 32 · ตั้งชื่อผลว่า `batch1`",
            "**Micro-batching + 4 process**: replica 1 ตัว 4 process batch = 32 ทั้ง 4 ใช้ GPU ใบเดียวกัน · ตั้งชื่อผลว่า `gpu1`",
            "ใช้ตัวเปิดระบบ ตัวยิงโหลด และเกณฑ์ SLO เดิม แต่ละรอบนานราว 4 นาที แล้วเทียบกับ `base1`"])))
    add(prompt_of(5))
    add(check(5, ["ได้ผล 2 รอบ `batch1` และ `gpu1` ทั้งคู่จบด้วยคำว่า **DONE**",
                  "ตารางเทียบ 3 แบบ: รองรับผู้ใช้ · Throughput สูงสุด · p95 · batch เฉลี่ย · GPU · CPU · กี่เท่าของ Baseline",
                  "ลำดับความจุ: **ทีละคำขอ < Micro-batching < Micro-batching + 4 process**",
                  "AI บอกคอขวดของแต่ละแบบ และบอกว่าเครื่องยังเปิดอยู่"],
                 "ผลของผู้สอน: 22 → 52 → 104 คน · 63 → 157 → 325 req/s · GPU 20% → 36% → 78%",
                 "ถ้าผลแย่ลงอย่างไม่มีเหตุผล (รอบแรกของ batch1 ได้ 4 คน) ให้ AI หาบั๊กก่อนสรุป · ตัวเลขของคุณต่างได้ แต่ลำดับควรเหมือนกัน"))
    add(S("GPU ใบเดิม ค่าเช่าเท่าเดิม รับได้ 22 → 52 → 104 คน (4.7 เท่า)", tiles([
        (hd[c], cell(t5, "รองรับผู้ใช้", c),
         "%s · GPU %s · **%s**" % (cell(t5, "Throughput", c), cell(t5, "GPU", c), cell(t5, "เท่าของ", c)), "ok" if c == 3 else "")
        for c in (1, 2, 3)]) + note("เท่าของ Baseline เขียนเป็น ผู้ใช้ / Throughput · ที่มา: ตารางขั้นที่ 5 ของ README", label="อ่านค่า")
        + note(Q("Throughput ที่ N=1 และ N=4 ของ `batch1`, `gpu1` และ `gpu2` ต่ำกว่าจริงราว 1 ใน 3 จากบั๊กของตัวยิงโหลดที่ AI พบในขั้นที่ 8 "
                 "แต่ไม่กระทบค่าความจุ เพราะความจุไม่ได้ตัดสินที่ระดับนั้น"), label="ข้อควรรู้"),
        tag="results/base1 · batch1 · gpu1", cls="mid"))
    add(fig("คอขวดย้ายจาก process เดียว ไปที่ CPU ของ process เดียว แล้วจึงถึง GPU", "results/bottleneck_gpu_cpu.png",
            Q("ดูแท่งสีส้ม: Micro-batching อย่างเดียวดัน GPU ได้ 36% เพราะงานอ่านคำขอ ถอด JPEG และแปลงผลยังอยู่บน process เดียว · "
              "แบ่งเป็น 4 process แล้ว GPU ขึ้นถึง 78% · CPU ของ server 1.3 → 2.1 → 6.1 core")))
    add(shot(5, "AI ต้องแก้บั๊กใน server ของตัวเองก่อนจึงได้ 52 และ 104 คน", [
        "ตารางของ AI: Micro-batching 52 คน 157.3 req/s และ + 4 process 104 คน 325.1 req/s · คอลัมน์ทีละคำขอเป็นค่าก่อนวัดซ้ำ (18 คน 39.5 req/s) ค่าที่ใช้คือ 22 คน",
        "รอบแรกของ `batch1` ได้เพียง 4 คน เพราะ server เรียกโมเดลคนละ thread ทุกครั้ง GPU จึงต้องเตรียมแผนคำนวณใหม่ครั้งละราว 2.65 วินาที",
        "AI แก้ 4 บรรทัดให้เรียกโมเดลบน thread เดียวเสมอ แล้ววัดใหม่ ผลที่ **แย่ลงอย่างไม่มีเหตุผล** จึงเป็นสัญญาณให้หาบั๊ก"]))

    # ----- ขั้นที่ 6
    group(6)
    add(divider(6, "1 ใบ 104 คน → 2 ใบ 176 คน (1.69 เท่า, Efficiency 85%)"))
    add(explain("ขั้นที่ 6: เปิด replica ตัวละ 1 GPU หลัง Load Balancer แล้ววัดซ้ำ", "image/lb-what.png", QL([
        "เปิดระบบแบบ **replica 2 ตัว** ตัวละ 4 process batch = 32 (แบบเดียวกับ `gpu1`) · ตั้งชื่อผลว่า `gpu2`",
        "วัดด้วยวิธีและเกณฑ์ SLO เดิม แล้วสรุปตาราง 4 แถว",
        "**เท่าของ 1 ใบ** และ **Efficiency** เทียบกับ `gpu1` ซึ่งใช้สถาปัตยกรรมเดียวกัน",
        "ประมาณการ 3 ใบ โดยบอกชัดว่า **เป็นการคำนวณ ไม่ใช่ผลวัด**"])))
    add(prompt_of(6))
    add(check(6, ["ได้ผล `gpu2` จบด้วยคำว่า **DONE**",
                  "ตาราง 4 แถว: จำนวน GPU · สถาปัตยกรรม · รองรับผู้ใช้ · Throughput · p95 · เท่าของ 1 ใบ · Efficiency",
                  "เท่าของ 1 ใบและ Efficiency **เทียบกับ gpu1** ไม่ใช่ Baseline",
                  "ประมาณการ 3 ใบ ระบุว่าเป็นการคำนวณ · บอกสัดส่วนคำขอของ 2 replica และคอขวด"],
                 "ผลของผู้สอน: 104 → 176 คน (1.69 เท่า, Efficiency 85%) · Throughput 325 → 651 req/s (2.00 เท่า) · ตามกติกาเข้ม 32 คน · คำขอกระจาย 49.6% / 50.4%",
                 "ถ้ามีระดับที่ไม่ผ่านครั้งเดียวขณะที่ระดับสูงกว่าผ่าน ให้วัดซ้ำก่อนสรุป และรายงานทั้งสองค่า · ตัวเลขของคุณต่างได้"))
    add(S("2 GPU รับได้ 176 คน แต่ตามกติกาเข้มได้ 32 คน", tiles([
        ("ความจุ 2 ใบ", cap(r4), Q("จาก 104 คนของ 1 ใบ · **1.69 เท่า**"), "ok"),
        ("Efficiency ความจุ", "85%", Q("Throughput 2.00 เท่า = 100%"), ""),
        ("Throughput สูงสุด", "651", Q("req/s · จาก 325 req/s"), ""),
        ("ตามกติกาเข้ม", "32", Q("คน · ระดับ N=64 รอบแรกไม่ผ่าน"), "warn"),
    ]) + note(Q("ประมาณการ 3 ใบ (คำนวณ ไม่ใช่ผลวัด): 104 × 3 × 0.85 ≈ 264 คน"), label="3 ใบ"), tag="results/gpu2.json", cls="mid"))
    add(fig("N=64 รอบแรกสะดุดครั้งเดียว: p95 1,752 ms ขณะที่ p50 ยัง 93 ms", "results/p50_p95_gpu2.png",
            Q("ดูยอดแหลมของเส้นแดงที่ N=64 · วัดซ้ำ 3 ครั้งผ่านหมด (วงกลมเขียว p95 147 / 145 / 149 ms) · ในรอบที่สะดุด GPU ทั้ง 2 ใบตกเหลือราว 30%")))
    add(fig("Throughput เพิ่ม 2.00 เท่าบนเส้น ideal แต่ความจุเพิ่ม 1.69 เท่า", "results/scaling_vs_gpus.png",
            Q("ความจุตัดสินด้วย p95: ที่ 96 คนต่อ GPU ระบบ 2 ใบได้ p95 557 ms เทียบกับ 424 ms ของ 1 ใบ · "
              "วงกลมโปร่งที่ 3 ใบเป็น **ค่าคำนวณ ไม่ใช่ผลวัด** (server จะใช้ CPU ราว 18.5 core)")))
    add(shot(6, "AI รายงานความจุ 2 ใบทั้ง 2 ค่า: 176 คน และ 32 คนตามกติกาเข้ม", [
        "ในรอบที่สะดุด p50 ยังปกติ (93 ms) จึงเป็นอาการค้างชั่วขณะ ไม่ใช่ระบบเต็ม · AI ไม่ได้หาสาเหตุ และไม่ได้แก้ไฟล์ผลเดิม",
        "Throughput 651.1 req/s เพิ่ม 2.00 เท่าพอดี GPU ทั้ง 2 ใบทำงานราว 80% และคำขอกระจาย 49.6% / 50.4%",
        "คอขวดคือ GPU · server ใช้ CPU 12.4 core จากที่ได้ราว 27 core · NGINX ใช้ 0.48 core และตัวยิงโหลดใช้ 0.46 core"],
        "คำตอบขั้นนี้เป็นภาษาอังกฤษ · แถวทีละคำขอในภาพเป็นค่าก่อนวัดซ้ำ"))

    # ----- ขั้นที่ 7
    group(7)
    rs = table("ขั้นที่ 7 ·", "")
    add(divider(7, "replica ช้า 1 ตัว: round-robin 32 คน · least_conn 72 คน"))
    add(explain("ขั้นที่ 7: เทียบวิธีแจกงาน round-robin กับ least_conn", "image/lb-rr-vs-lc.png", QL([
        "เพิ่มความสามารถให้ตัวเปิดระบบ: **เลือกวิธีแจกงาน** และสั่งให้ replica ที่เลือก **ช้าลงรูปละกี่ ms** ได้",
        "replica เท่ากัน: เปิดแบบ least_conn วัดความจุ ตั้งชื่อผลว่า `lc2` (เทียบกับ `gpu2`)",
        "replica ไม่เท่ากัน: ให้ replica ตัวที่ 2 ช้าลงรูปละ 40 ms แล้ววัด `rr_slow` และ `lc_slow`",
        "สรุป 2 ตาราง พร้อมสัดส่วนคำขอที่แต่ละ replica ได้"])))
    add(prompt_of(7))
    add(check(7, ["ตัวเปิดระบบเลือก round-robin / least_conn ได้ และสั่งให้ replica ที่เลือกช้าลงได้",
                  "ได้ผล 3 รอบ `lc2` · `rr_slow` · `lc_slow` จบด้วย **DONE** ทุกรอบ",
                  "ตาราง (ก) replica เท่ากัน และ (ข) มี replica ช้า 1 ตัว พร้อมสัดส่วนคำขอ",
                  "ตรวจว่าสองฝั่งของแต่ละการเทียบ **ต่างกันแค่วิธีแจกงาน** (ค่า NGINX ชุดเดียวกัน)"],
                 "ผลของผู้สอน: replica ช้า round-robin 32 คน 169 req/s แบ่ง 50.0 : 50.0 · least_conn 72 คน 403 req/s แบ่ง 79.4 : 20.6 · replica เท่ากันยังสรุปไม่ได้"))
    gv = lambda k, c: cell(rs, k, c)
    add(S("(ข) replica ช้า 1 ตัว: least_conn รับได้ 2.25 เท่าของ round-robin", versus("",
        ("round-robin (rr_slow)", "แบ่งงาน " + gv("สัดส่วน", 1), gv("รองรับ", 1),
         "Throughput %s · GPU %s" % (gv("Throughput", 1), gv("GPU", 1))),
        ("least_conn (lc_slow)", "แบ่งงาน " + gv("สัดส่วน", 2), gv("รองรับ", 2).split(" (")[0],
         "**%s** · Throughput %s · GPU %s" % (gv("รองรับ", 2).split(" (")[1].rstrip(")"), gv("Throughput", 2), gv("GPU", 2))))
        + note("ทั้งสองรอบใช้ค่า NGINX ชุดเดียวกัน ต่างกันเพียงวิธีแจกงาน จึงเป็นการเทียบที่ใช้สรุปได้", label="ทำไมเชื่อได้"),
        tag="results/rr_slow · lc_slow", cls="mid"))
    eq = [t for t in walk(step(7)) if t["t"] == "table"][1]
    add(fig("(ก) replica เท่ากัน: %s กับ %s ยังสรุปไม่ได้ว่า least_conn ดีกว่า" % (cell(eq, "รองรับ", 1).split(" (")[0], cell(eq, "รองรับ", 2)),
            "img/n28-twovars.jpg",
            Q("Throughput สูงสุดแทบเท่ากัน (%s กับ %s) และแบ่งงาน 50 : 50 ทั้งคู่ · ค่า 176 ยังขึ้นกับการวัดซ้ำระดับที่สะดุด (ตามกติกาเข้ม 32) · "
              "ต้องวัด round-robin ซ้ำด้วยค่า NGINX ชุดเดียวกันก่อนสรุป" % (cell(eq, "Throughput", 1), cell(eq, "Throughput", 2)))))
    add(fig("เมื่อมี replica ช้า เส้น least_conn ตัด SLO ที่ 72 คน ส่วน round-robin ตัดที่ 32 คน", "results/lb_rr_vs_least_conn.png",
            "ดูกราฟขวาบน · กราฟซ้ายคือกรณี replica เท่ากัน ซึ่งยังสรุปไม่ได้ · แถวล่างคือความจุและสัดส่วนคำขอของแต่ละ replica"))
    add(shot(7, "round-robin ยังส่งงานครึ่งหนึ่งให้ replica ที่ช้า ส่วน least_conn ย้ายงานไปตัวเร็วเอง", [
        "round-robin แบ่งงาน 50 : 50 งานจึงไปกองที่ตัวช้า และ GPU 0 ทำงานเพียง 48% ทั้งที่ยังว่าง",
        "least_conn เห็นว่าตัวช้ามีงานค้างมาก จึงส่งงานราว 80% ไปที่ตัวเร็ว รับได้ 72 คน เทียบกับ 32 คน",
        "AI เพิ่มค่า `zone` ให้ NGINX ในขั้นนี้ ทำให้คู่ (ก) ต่างกัน 2 ตัวแปร หลักที่ต้องใช้คือ **เปลี่ยนทีละตัวแปร**"]))

    # ----- ขั้นที่ 8
    group(8)
    ft = [t for t in walk(step(8)) if t["t"] == "table"][0]
    add(divider(8, "ไม่ส่งซ้ำ error 36.9% · ส่งซ้ำ error 0"))
    add(explain("ขั้นที่ 8: ปิด replica ตัวที่ 2 กลางการยิงโหลด แล้วดูว่าผู้ใช้เห็น error หรือไม่", "image/lb-failover.png", QL([
        "ตัวเปิดระบบ **ปิดกะทันหันและเปิดคืน** replica ทีละตัวได้ และเลือกได้ว่า NGINX **ส่งซ้ำ** หรือไม่",
        "ตัวยิงโหลดมี **โหมดยิงระดับเดียว** เก็บผลรายวินาที และสั่งคำสั่งตามวินาทีที่กำหนดได้",
        "ยิงด้วยผู้ใช้หนึ่งในสามของความจุ 2 ใบ นาน 45 วินาที ปิด replica ตัวที่ 2 ที่วินาทีที่ 15 เปิดคืนที่วินาทีที่ 30",
        "ทำ 2 รอบ: `fo_noretry` (ไม่ส่งซ้ำ) · `fo_retry` (ส่งซ้ำ)"])))
    add(prompt_of(8))
    add(check(8, ["ตัวเปิดระบบปิดและเปิดคืน replica ได้ และเลือกได้ว่า NGINX ส่งซ้ำหรือไม่",
                  "ตัวยิงโหลดมีโหมดยิงระดับเดียวที่เก็บผลรายวินาที",
                  "ได้ผล 2 รอบ `fo_noretry` และ `fo_retry`",
                  "ตารางเทียบ error · Throughput ก่อน / ระหว่าง / หลัง · p95 แย่สุด · เวลาจน replica กลับมารับงาน",
                  "ตรวจว่าจำนวนผู้ใช้ที่ยิงคิดจากความจุค่าไหน (32 ÷ 3 หรือ 176 ÷ 3)"],
                 "ผลของผู้สอน: ผู้ใช้ 11 คน · ไม่ส่งซ้ำ error 5,474 / 14,822 (36.9%) · ส่งซ้ำ error 0 / 9,601 · เปิด replica คืนใช้ราว 92 วินาที"))
    fv = lambda k, c: cell(ft, k, c)
    add(S("เมื่อ NGINX ส่งซ้ำ ผู้ใช้ไม่เห็น error เลย", versus("",
        ("NGINX ไม่ส่งซ้ำ (fo_noretry)", "error / คำขอทั้งหมด", fv("error", 1).split(" (")[0],
         "**" + fv("error", 1).split(" (")[1].split(")")[0] + "** · 502 และ 503 · Throughput ก่อน / ระหว่าง / หลัง %s" % fv("Throughput", 1)),
        ("NGINX ส่งซ้ำ (fo_retry)", "error / คำขอทั้งหมด", fv("error", 2),
         "Throughput ก่อน / ระหว่าง / หลัง %s" % fv("Throughput", 2)))
        + note(Q("ผู้ใช้ 11 คน · ยิง 45 วินาที · ปิด replica ตัวที่ 2 วินาทีที่ 15 · สั่งเปิดคืนวินาทีที่ 30 · replica ที่เปิดคืนกลับมารับงานหลังราว 92 วินาที"), label="เงื่อนไข")
        + note(Q("โหลดเบามาก: ผู้ใช้ 11 คนคิดจากความจุตามกติกาเข้ม (32 ÷ 3) ไม่ใช่ 176 ÷ 3 ≈ 59 คน replica ที่เหลือจึงรับได้สบาย "
                 "(190 req/s จากเพดาน 325) · ผลนี้บอกได้ว่า retry กัน error ได้ แต่ **ยังไม่ได้ทดสอบเมื่อโหลดใกล้ความจุ**"), label="ข้อจำกัด"),
        tag="results/fo_noretry · fo_retry", cls="mid"))
    add(fig("คำขอรายวินาที: รอบไม่ส่งซ้ำมีแท่ง error สีแดงต่อเนื่อง รอบส่งซ้ำไม่มีเลย", "results/failover_timeline.png",
            Q("error ในรอบไม่ส่งซ้ำไม่ลดลงตามเวลา เพราะโค้ดรอบนี้ตั้ง `max_fails=0` NGINX จึงยังแจกงานให้ตัวที่ล่ม · "
              "ระบบจริงควรมีทั้ง health check ที่ตัดตัวล่มออก และ retry")))
    add(shot(8, "ทั้ง 2 รอบ replica ที่เปิดคืนใช้ราว 92 วินาทีกว่าจะกลับมารับงาน", [
        "รอบไม่ส่งซ้ำมีคำขอรวมมากกว่า (14,822 เทียบกับ 9,601) เพราะ error ตอบกลับทันที ให้นับ **เฉพาะคำขอที่สำเร็จ**",
        "เปิด replica คืนใช้ราว 92 วินาที เพราะต้องอุ่นโมเดลครบทุกขนาด batch 1–32 ก่อนรับงาน ระบบจริงควรมี replica สำรองเปิดรอไว้ (N+1)",
        "AI พบบั๊ก 2 จุด: ตัวยิงโหลดหยุดยิงก่อนเวลาใน process ที่มีผู้ใช้คนเดียว และการเปิด replica คืนใช้ CPU จนชนโควตาของเครื่องเช่า"],
        "AI ต้องรันใหม่หลังแก้บั๊ก ขั้นนี้จึงใช้เวลา 42 นาที 46 วินาที"))

    # ----- ขั้นที่ 9
    group(9)
    ct = [t for t in walk(step(9)) if t["t"] == "table"][0]
    add(divider(9, "เครื่องเปิด 2 ชั่วโมง 40 นาที · ค่าเช่าตามบิล $1.02"))
    add(nfig("n21-step9-close"))
    add(prompt_of(9))
    add(check(9, ["มี `lab6_image_api/code/report.py` และ `lab6_image_api/results/metrics.json` ที่รวมทุกชุดผล",
                  "มีกราฟ PNG ชุดหลักและชุดเสริม เปิดแล้วอ่านออก",
                  "ผลทั้งหมดและโค้ดทุกไฟล์กลับมาอยู่ในโฟลเดอร์ของบทบนเครื่องคุณ",
                  "**ไม่มีเครื่องป้าย `vapp-lab6` ค้างในบัญชี**",
                  "สรุปค่าใช้จ่ายจริง: อายุเครื่อง · ราคาต่อชั่วโมง · ยอดที่ถูกคิด"],
                 "ผลของผู้สอน: เครื่องเปิด 2 ชั่วโมง 40 นาที · $0.395 ต่อชั่วโมง · ยอดในบิล $1.02",
                 "ยอดเงินของคุณขึ้นกับราคาเครื่องและเวลาที่ใช้ · เครื่องที่ลืมลบคิดเงินต่อทุกชั่วโมง"))
    add(S("ทั้ง LAB ใช้เงินราว $1", tiles([(E.plain(r[0]), E.plain(r[1]).split(" (")[0], md(r[1].split(" (", 1)[1].rstrip(")")) if " (" in r[1] else "",
                                                 "ok" if k == 2 else "") for k, r in enumerate(ct["rows"])])
          + note(Q("เครื่องที่ลืมลบคิดเงินต่อชั่วโมงละ $0.395 จึงต้องตรวจทุกครั้งว่าไม่มีเครื่องป้าย `vapp-lab6` ค้างในบัญชี"), label="ตรวจทุกครั้ง"),
          tag="README · ขั้นที่ 9", cls="mid"))
    add(shot(9, "ตารางสุดท้ายรายงานความจุ 2 ใบทั้ง 2 ค่า และใช้ Baseline 22 คนที่วัดซ้ำ", [
        "รายงานที่ดีต้องบอกค่าที่ไม่สวยด้วย: AI ระบุทั้ง 176 คน และ 32 คนตามกติกาเข้ม พร้อมเหตุผล",
        "ปรับระบบบนใบเดิมก่อนได้ **4.7 เท่าโดยค่าเช่าเท่าเดิม** แล้วจึงเพิ่มใบ ซึ่งได้ **1.69 เท่า แต่จ่ายเพิ่ม 2 เท่า**",
        "ประมาณการ 3 ใบ 264 คน เป็นการคำนวณ ไม่ใช่ผลวัด"],
        "AI อ่านค่าใช้จ่ายได้ $1.011 · กราฟ 5 ภาพอยู่ในภาพคำตอบเต็ม"))

    # ----- ปิดท้าย: สกิล v0
    CTX.update(kicker="ปิดท้าย · สกิลเวอร์ชัน 0", group="ปิดท้าย · สกิล v0")
    add(E.divider("ปิดท้าย", "เก็บงานทั้ง LAB เป็นสกิลเวอร์ชัน 0",
                  "<p>%s</p>" % md(" ".join(para("ปิดท้าย", "เราเพิ่งสั่งงาน")["lines"]))))

    group(10)
    add(divider(10, "สกิล gpu-api-capacity · SKILL.md + scripts 11 ไฟล์ · ไม่ต้องเช่าเครื่อง"))
    add(explain("ขั้นที่ 10: AI อ่านพรอมต์ โค้ด และผลของ LAB แล้วเขียนเป็นสกิล", "image/skill-v0.png", QL([
        "ดูพรอมต์ทุกขั้นใน `PROMPTS.md` · โค้ดใน `code/` · ผลใน `results/`",
        "สร้างสกิล `gpu-api-capacity` ที่ `skill_v0/SKILL.md` มี name และ description",
        "ในสกิลมี: ค่าที่ปรับได้พร้อมค่าเริ่มต้น · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน",
        "เก็บโค้ดที่พิสูจน์แล้วไว้ที่ `skill_v0/scripts` แล้วติดตั้งที่ `.claude/skills/gpu-api-capacity`"])))
    add(prompt_of(10))
    add(check(10, ["มี `lab6_image_api/skill_v0/SKILL.md` ที่มี name และ description บอกว่าใช้เมื่อไร",
                   "สกิลมีค่าที่ปรับได้พร้อมค่าเริ่มต้น · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน",
                   "โค้ดที่พิสูจน์แล้วอยู่ใน `lab6_image_api/skill_v0/scripts`",
                   "สกิลติดตั้งที่ `.claude/skills/gpu-api-capacity` แล้ว **ปิดและเปิด Claude Code ใหม่ 1 ครั้ง**"],
                  "ผลของผู้สอน: SKILL.md และ scripts 11 ไฟล์ · ใช้เวลา 6 นาที 12 วินาที · ไม่ต้องเช่าเครื่อง",
                  "เนื้อหาในสกิลของคุณต่างจากของผู้สอนได้ เพราะเขียนจากโค้ดและผลในรอบของคุณ"))
    add(shot(10, "ได้สกิล gpu-api-capacity ที่มี SKILL.md กับ scripts 11 ไฟล์ และเกณฑ์ตรวจผ่านจากรอบจริง", [
        "ค่าเริ่มต้น: RTX 3090 2 ใบ เพดาน $0.60 ต่อชั่วโมง และ SLO p95 ≤ 500 ms กับ error < 1%",
        "เกณฑ์ตรวจผ่านใส่ตัวเลขจากรอบจริง 22, 52, 104 และ 176 คน",
        alert_text(sec("ขั้นที่ 10 ·"))]))

    group(11)
    cmp_t = [t for t in walk(step(11)) if t["t"] == "table"][0]
    add(divider(11, "1 พรอมต์ · 17 นาที · $0.10 · 2 GPU ได้ 192 คน"))
    add(nfig("n22-step11-reuse"))
    add(prompt_of(11))
    add(check(11, ["AI ใช้สกิล `gpu-api-capacity` และโค้ดใน `scripts/` โดยไม่เขียนโค้ดใหม่",
                   "เครื่องป้าย `vapp-lab6-skill` ถูกเช่า แล้ว **ลบ** เมื่อจบ",
                   "ผลอยู่ที่ `lab6_image_api/results_skill`",
                   "ตารางความจุ 2 แบบ เทียบกับผลรอบหลัก และค่าใช้จ่ายจริง"],
                  "ผลของผู้สอน: 1 GPU ทีละคำขอ 28 คน 61 req/s · 2 GPU 192 คน 660 req/s · ใช้เวลา 16 นาที 49 วินาที · ยอดในบิล $0.102"))
    add(tbl("สั่งทีละขั้น 9 พรอมต์ เทียบกับสกิล v0 คำสั่งเดียว", cmp_t, post=note(reads11()[1], label="ข้อสังเกต")))
    add(shot(11, "สกิล v0 ผ่านในรอบแรก: 1 GPU ทีละคำขอ 28 คน และ 2 GPU 192 คน", [
        "AI ตัวใหม่ได้คำสั่ง 3 บรรทัด แล้วเช่า ติดตั้ง วัด 2 แบบ ลบเครื่อง และสรุปบิลเองทั้งหมด โดยไม่ต้องแก้บั๊กซ้ำ",
        "Baseline ได้ 28 คน ไม่ใช่ 22 คน ทั้งที่ Throughput เท่ากัน (61 กับ 63 req/s) เพราะระดับ N หยาบกว่า การซอยครึ่งจึงไปลงที่ 28, 34, 40 แทน 20, 22, 24",
        "ตัวเลข 6.9 เท่า (28 → 192 คน) ปนผลของเทคนิคบนใบเดิมกับ GPU ใบที่ 2 เพราะรอบย่อไม่ได้วัดแบบ 1 ใบ Micro-batching + 4 process"],
        "คำตอบเป็นภาษาอังกฤษ · เครื่องเปิดรวม 14.4 นาที AI อ่านค่าใช้จ่ายได้ $0.097"))
    lim = [t for t in walk(step(11)) if t["t"] == "table"][1]
    add(S("สกิล v0 ยังไม่สมบูรณ์: 6 จุดที่ควรแก้ในเวอร์ชันถัดไป", cards([(r[0], "<p><b>v1</b>: %s</p>" % md(r[1]), "warn") for r in lim["rows"]], 3),
          tag="README · ขั้นที่ 11"))

    # ===== 4 · สรุป
    CTX.update(kicker="สรุปบท", group="สรุปบท")
    add(E.divider("สรุป", "ทีละคำขอ %s คน → 2 GPU %s คน" % (cap(r1), cap(r4)), "<p>ผลรวม · ตารางสรุป · บทเรียน · ข้อจำกัด</p>"))
    add(fig("เส้น p95 ของ 4 แบบตัดเส้น SLO 500 ms ที่ %s, %s, %s และ %s คน" % (cap(r1), cap(r2), cap(r3), cap(r4)), "results/latency_p95_vs_users.png",
            "ดาวคือความจุของแต่ละแบบ · ยอดแหลมของ 2 GPU ที่ N=64 คือการสะดุดครั้งเดียว ซึ่งวัดซ้ำ 3 ครั้งแล้วผ่าน"))
    add(tbl("ตารางสรุปของทั้ง LAB: 1 ใบ 104 คน → 2 ใบ 176 คน (1.69 เท่า, Efficiency 85%)", T,
            post=note(" ".join(para("การทดลอง", "\"เท่าของ 1 ใบ\"")["lines"]), label="อ่านตาราง")))
    add(fig("บทเรียนของ LAB นี้: ปรับใบเดิมให้เต็มก่อน แล้วจึงเพิ่ม GPU", "img/n29-lessons.jpg",
            Q("Micro-batching + 4 process ได้ 4.7 เท่าโดยค่าเช่าเท่าเดิม ส่วน GPU ใบที่ 2 ได้ 1.69 เท่า แต่จ่ายเพิ่ม 2 เท่า")))
    add(S("ข้อจำกัด: สิ่งที่ LAB นี้ยังไม่ได้พิสูจน์", cards([
        ("ความจุ 2 ใบมี 2 ค่า", Q("ตามกติกาเข้มได้ **32 คน** · ค่า 176 มาจากการวัดซ้ำระดับที่สะดุด และมีความละเอียดเพียงช่วงซอยครึ่ง 16 คน"), "warn"),
        ("3 ใบเป็นการคำนวณ", "เครื่องนี้มี 2 GPU จึงวัดไม่ได้ · ใช้สมมติฐานว่า Efficiency และ CPU ยังพอ", "warn"),
        ("replica เท่ากัน: ยังสรุปไม่ได้", "round-robin กับ least_conn ต่างกัน 2 ตัวแปร (วิธีแจกงานและค่า `zone`)", "bad"),
        ("Failover ทดสอบที่โหลดเบา", "ยังไม่ได้ทดสอบว่าเมื่อโหลดใกล้ความจุแล้วเหลือ GPU ใบเดียวจะยังผ่าน SLO หรือไม่", "bad"),
        ("ทุกส่วนอยู่บนเครื่องเดียว", "ระบบจริงต้องบวกเวลาเครือข่ายระหว่างเครื่อง และ Load Balancer ต้องมีตัวสำรอง", ""),
        ("ตัวเลขของโค้ดรอบนี้", "รูปมีแค่ 6 รูปขนาดเท่ากัน · ของคุณจะได้ตัวเลขไม่เท่านี้ แต่ลำดับควรเหมือนกัน", ""),
    ], 3), cls="mid"))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบบท", "ถัดไป: สั่งปรับสกิลเป็น v1 ตามตาราง แล้วใช้ซ้ำ",
                  '<p>รายละเอียดเต็มของบทนี้: <a href="README.md" target="_blank">README.md</a> · พรอมต์ทั้งหมด: <a href="PROMPTS.md" target="_blank">PROMPTS.md</a></p>'))
    return E.SL


def reads11():
    bl = step(11)
    for k, b in enumerate(bl):
        if b["t"] == "p" and b["lines"][0] == "**อ่านผลอย่างไร**":
            return next(x for x in bl[k + 1:] if x["t"] == "ul")["items"]
    raise KeyError(11)


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
