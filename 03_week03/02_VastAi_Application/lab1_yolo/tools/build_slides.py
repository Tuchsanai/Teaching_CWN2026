#!/usr/bin/env python3
"""สร้างสไลด์ LAB1_YOLO_Slides.html ของ LAB 1 · เทรน YOLO ตรวจหมวกนิรภัย แล้วต่อเข้าเว็บ

  python tools/crop_answers.py            (ครั้งแรก: ตัดส่วนสำคัญของภาพหน้าจอคำตอบเป็น img/cNN-*.jpg)
  python tools/build_slides.py            (รันจากโฟลเดอร์ lab1_yolo)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · ภาพเป็นตัวอธิบาย ข้อความข้างภาพไม่เกิน 3 ข้อ
เนื้อหาชนิดเดียวกันใช้ layout เดียวกันทั้งเด็ค
  photo_band()  ภาพถ่ายเต็มหน้า + ประโยคเดียวบนแถบ      (โจทย์ของบท)
  big()         ภาพใหญ่ราว 2/3 ของหน้า + 2-3 ข้อด้านข้าง  (ทฤษฎี และภาพของแต่ละขั้น)
  evidence()    ภาพผลจริงเต็มความกว้าง + 3 ข้อด้านล่าง    (คำตอบจริงที่ตัดเฉพาะส่วนสำคัญ และกราฟจริง)
  time_chart() cost_bar() compare_bars()  ตัวเลขผลจริงเรียงพิมพ์เป็นกราฟ (ตัวเลขตรงกับ README และไฟล์ผล)

ที่มาของเนื้อหา
- ตาราง ข้อความ และพรอมต์ของทุกขั้น: อ่านจาก README.md ตอนสร้าง (พรอมต์ = code fence ชนิด text ตรงตัวอักษร)
- ตัวเลขผล: results/run_info.json · results/metrics.json · results/skill_v0_run/metrics.json และ README.md
- ภาพใหม่: tools/slides_figures.py · ภาพตัดจากคำตอบจริง: tools/crop_answers.py · เครื่องมือเรนเดอร์: tools/slides_engine.py
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, para, CTX, add, note, fig, explain, cards, bars, tbl)
from slides_figures import FIGS

S = E.slide
SECS = E.load("README.md")
FIG = {f["img"]: f for f in FIGS}
OUT, TITLE = "LAB1_YOLO_Slides.html", "LAB 1 · เทรน YOLO ตรวจหมวกนิรภัย · Slides"

RI = json.loads(E.read("results/run_info.json"))
M = json.loads(E.read("results/metrics.json"))
M10 = json.loads(E.read("results/skill_v0_run/metrics.json"))
COST = RI["cost_usd"]

VARY = "ตัวเลขและข้อความของคุณอาจต่างจากของผู้สอน เพราะ AI เขียนโค้ดไม่เหมือนกันทุกครั้ง และเครื่องเช่าแต่ละเครื่องต่างกัน สิ่งที่ต้องมีเหมือนกันคือไฟล์และเกณฑ์ในรายการด้านบน"
PART = "ส่วนที่ %d จาก 4"
CROP_CAP = "ส่วนหนึ่งของคำตอบจริง คลิกภาพเพื่อขยาย หรือเปิด[ภาพเต็ม](%s)"

EXTRA_CSS = r"""
.band{padding:0;background-size:cover;background-position:center;color:#fff}
.band .shade{position:absolute;inset:0;background:linear-gradient(0deg,rgba(6,13,26,.92) 0%,rgba(6,13,26,.55) 34%,rgba(6,13,26,0) 62%)}
.band .say{position:absolute;left:72px;right:72px;bottom:70px;font-size:40px;line-height:1.42;font-weight:600;max-width:1300px}
.band .say small{display:block;font-size:20px;font-weight:600;color:#9fe3df;margin-bottom:10px;letter-spacing:.02em}
.band .imgnote{position:absolute;right:22px;bottom:12px;font-size:13px;color:rgba(255,255,255,.7)}
.ex.big .fig{flex:2.1 1 0}
.ex.big .side{gap:.7em}
.ex.big .stp{font-size:.92em}
.evi{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:14px}
.evi .fig{flex:1 1 0;min-height:200px}
.evi.wide{justify-content:center}.evi.wide .fig{flex:none;min-height:0}.evi.wide .fig img{width:100%;max-height:none}
.pts{flex:none;display:grid;grid-template-columns:repeat(var(--n,3),1fr);gap:26px}
.pt{display:flex;gap:.6em;align-items:flex-start;border-top:4px solid var(--teal);padding-top:.5em;line-height:1.45;font-size:.88em}
.pt .n{flex:none;width:1.7em;height:1.7em;border-radius:50%;background:var(--navy);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:.85em}
.pt.bad{border-color:var(--red)}
.tch{display:flex;flex-direction:column;gap:.55em}
.tch .row{display:grid;grid-template-columns:11em 9em 1fr;gap:.8em;align-items:center}
.tch .nm{font-family:var(--mono);font-size:.82em}
.tch .vd{font-weight:700;font-size:.85em;padding:.12em .6em;border-radius:6px;text-align:center}
.tch .vd.ok{background:var(--green-soft);color:var(--green)}.tch .vd.bad{background:var(--red-soft);color:var(--red)}
.tch .vd small{font-weight:500}
.tch .bb{display:flex;flex-direction:column;gap:4px}
.tch .ln{display:flex;align-items:center;gap:.5em;font-size:.8em;line-height:1.2}
.tch .ln i{display:block;height:15px;border-radius:4px;flex:none}
.tch .ln.m i{background:var(--orange)}.tch .ln.r i{background:#8aa3c4}
.tch .key{display:flex;gap:2em;font-size:.82em;color:var(--muted);margin-left:21.6em}
.tch .key span:before{content:"";display:inline-block;width:1.4em;height:.8em;border-radius:3px;margin-right:.45em;vertical-align:middle}
.tch .key .km:before{background:var(--orange)}.tch .key .kr:before{background:#8aa3c4}
.cb{display:flex;flex-direction:column;gap:.5em}
.cb .stack{display:flex;height:64px;border-radius:10px;overflow:hidden;border:1px solid var(--line)}
.cb .seg{display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:.82em;white-space:nowrap;overflow:hidden}
.cb .lab{display:flex;flex-wrap:wrap;gap:.4em 1.6em;font-size:.86em}
.cb .lab span:before{content:"";display:inline-block;width:.9em;height:.9em;border-radius:3px;margin-right:.4em;vertical-align:-.05em;background:var(--c)}
.cb .tot{display:flex;justify-content:space-between;font-size:.9em}
.cmp{display:flex;flex-direction:column;gap:.45em}
.cmp .row{display:grid;grid-template-columns:9em 1fr 1fr;gap:1em;align-items:center}
.cmp .hd2{font-weight:700;color:var(--navy);font-size:.9em}
.cmp .k{font-weight:600;font-size:.88em}
.cmp .c{display:flex;align-items:center;gap:.5em;font-size:.82em;line-height:1.25}
.cmp .c i{display:block;height:16px;border-radius:4px;flex:none;background:#8aa3c4}
.cmp .c.s i{background:var(--teal)}
.divider .small{font-weight:700;letter-spacing:.03em;margin-bottom:22px}
"""


def f3(x):
    return "%.3f" % x


def usd(x):
    return "$%.3f" % x


def ms(x):
    """มิลลิวินาทีปัดครึ่งขึ้น มีจุลภาค (2076.5 -> 2,077)"""
    return format(int(x + 0.5), ",")


def has(src):
    return os.path.exists(os.path.join(E.ROOT, src))


def pick(*srcs):
    """ภาพแรกที่มีอยู่จริง (ภาพใหม่ของรอบนี้ก่อน แล้วจึงภาพเดิม)"""
    for s in srcs:
        if s and has(s):
            return s
    return srcs[-1]


def items_after(prefix, head):
    bs = sec(prefix)
    for k, b in enumerate(bs):
        if b["t"] == "p" and b["lines"][0] == head:
            for x in bs[k + 1:]:
                if x["t"] == "ul":
                    return x["items"]
    raise KeyError("ไม่พบรายการหลัง %r ในหัวข้อ %r" % (head, prefix))


def caption(prefix):
    for b in sec(prefix):
        if b["t"] == "p" and b["lines"][0].startswith("*") and not b["lines"][0].startswith("**"):
            return " ".join(b["lines"])[1:-1]
    return ""


def intro(prefix):
    return next(" ".join(b["lines"]) for b in sec(prefix) if b["t"] == "p")


def alt(src):
    for s in SECS:
        for b in walk(s["blocks"]):
            if b["t"] == "img" and b["src"] == src:
                return b["alt"]
    m = re.search(r"!\[([^\]]*)\]\(%s\)" % re.escape(src), E.read("README.md"))
    if m:
        return m.group(1)
    return ""


def answer(n):
    return alt("image/lab1-step%d.png" % n).split("และคำตอบ: ", 1)[1]


def heading(n):
    for s in SECS:
        if s["text"].startswith("ขั้นที่ %d · " % n):
            return s["text"]
    raise KeyError(n)


def prompt_lines(n, last):
    t = E.prompt_code(heading(n))["blocks"][0]["text"]
    return [l[3:] for l in t.split("\n") if re.match(r"^[1-%d]\. " % last, l)]


def img(src, a=""):
    return E.img_tag({"t": "img", "src": src, "alt": E.plain(a or alt(src) or src)})


def steps_html(items):
    return "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(items))


# ------------------------------------------------------------------ layout ของเด็คนี้
def photo_band(toc, src, say, small=""):
    """ภาพถ่ายเต็มหน้า + ประโยคเดียวบนแถบล่าง"""
    raw = ('<div class="shade"></div><div class="say">%s%s</div><div class="imgnote">ภาพจำลอง</div>'
           % ("<small>%s</small>" % small if small else "", md(say)))
    return {"raw": raw, "cls": "band", "style": ' style="background-image:url(%s)"' % src, "title": toc, "kicker": "", "tag": "", "lead": ""}


def big(title, src, points, post="", tag=""):
    """ภาพใหญ่ราว 2/3 ของหน้า + ข้อความ 2-3 ข้อด้านข้าง"""
    body = '<div class="ex big"><div class="fig">%s</div><div class="side fitbox">%s%s</div></div>' % (img(src, title), steps_html(points), post)
    return S(title, body, tag=tag, maxfs=1.3)


def pts_html(points, bad=()):
    return '<div class="pts" style="--n:%d">%s</div>' % (len(points), "".join(
        '<div class="pt%s"><span class="n">%d</span><span>%s</span></div>' % (" bad" if k in bad else "", k + 1, md(x))
        for k, x in enumerate(points)))


def evidence(title, src, points, cap="", tag="ผลจริง", bad=()):
    """ภาพผลจริงเต็มความกว้าง (ภาพตัด หรือกราฟจริง) + ข้อความ 2-3 ข้อด้านล่าง"""
    wide = " wide" if E.fig_nat_h({"src": src}) < 420 else ""
    body = '<div class="evi%s"><div class="fig">%s</div>%s</div>' % (wide, img(src, title), pts_html(points, bad))
    if cap:
        body += '<p class="cap">%s</p>' % md(cap)
    return S(title, body, tag=tag, maxfs=1.25)


def divider(n, short, result, photo):
    h = heading(n)
    sub = "<p>%s</p><p><b>เวลา:</b> %s</p><p><b>ผลจริง:</b> %s</p>" % (md(intro(h)), md(caption(h)), md(result))
    return E.divider("ขั้นที่ %d" % n, h.split(" · ", 1)[1], sub, photo, small="ภาค LAB · ขั้นที่ %d จาก 10" % n)


def prompt_step(n, short):
    return E.prompt_slides(E.prompt_code(heading(n)), CTX["kicker"], "ขั้นที่ %d · %s" % (n, short))


def check(n, items, short, note_text=VARY):
    return E.check_slide("step%d" % n, items, "ผลของผู้สอน: " + answer(n), note_text, "ขั้นที่ %d · %s" % (n, short))


def time_chart(web):
    """เวลาที่โมเดลใช้ เทียบกับเวลาส่งรูปไป-กลับ ของรูปตัวอย่าง 6 รูป (ตัวเลขจาก results/run_info.json)"""
    top = max(w["roundtrip_ms"] for w in web)
    rows = []
    for w in web:
        vd = '<span class="vd ok">ผ่าน</span>' if w["passed"] else '<span class="vd bad">ไม่ผ่าน<br><small>ไม่สวมหมวก %d คน</small></span>' % w["no_hardhat"]
        bm = '<div class="ln m"><i style="width:%.2f%%"></i>%.1f ms</div>' % (max(0.4, 72 * w["inference_ms"] / top), w["inference_ms"])
        br = '<div class="ln r"><i style="width:%.2f%%"></i>%s ms</div>' % (72 * w["roundtrip_ms"] / top, format(w["roundtrip_ms"], ",.1f"))
        rows.append('<div class="row"><span class="nm">%s</span>%s<div class="bb">%s%s</div></div>' % (w["image"], vd, bm, br))
    key = '<div class="key"><span class="km">เวลาที่โมเดลใช้</span><span class="kr">เวลาส่งรูปไป-กลับ</span></div>'
    return '<div class="tch">%s%s</div>' % ("".join(rows), key)


def cost_bar(mm, failed, total):
    """ใบเสร็จเป็นแท่งต่อกัน · ความยาวตามจำนวนเงิน (ตัวเลขจาก results/run_info.json)"""
    segs = [("GPU", mm["gpu"], "#12305e"), ("Disk", mm["disk"], "#0f8f8c"), ("ดาวน์โหลด", mm["download"], "#e87f1c"),
            ("เครื่องที่เปิดไม่ขึ้น 3 เครื่อง", failed, "#c92a2a")]
    st = "".join('<div class="seg" style="flex:%.4f;background:%s">%s</div>' % (v, c, usd(v) if v > 0.06 else "") for _, v, c in segs)
    lab = "".join('<span style="--c:%s">%s <b>%s</b></span>' % (c, k, usd(v)) for k, v, c in segs)
    tot = ('<div class="tot"><span>เครื่องหลัก (ยอดสุดท้ายในใบแจ้งหนี้) <b>%s</b></span><span>รวมทั้ง LAB <b>%s</b></span></div>'
           % (usd(mm["total"]), usd(total)))
    return '<div class="cb"><div class="stack">%s</div><div class="lab">%s</div>%s</div>' % (st, lab, tot)


def num(cell):
    m = re.search(r"[\d.,]+", cell.replace("$", ""))
    return float(m.group(0).replace(",", "")) if m else None


def compare_bars(t):
    """ตารางเทียบ 2 คอลัมน์ของ README เป็นแท่งคู่ · ข้อความในแต่ละช่องคัดจาก README ตรงตัว"""
    rows = ['<div class="row hd2"><span></span><span>%s</span><span>%s</span></div>' % (md(t["head"][1]), md(t["head"][2]))]
    for r in t["rows"]:
        a, b = num(r[1]), num(r[2])
        if a is None or b is None:
            ca, cb_ = '<div class="c">%s</div>' % md(r[1]), '<div class="c s">%s</div>' % md(r[2])
        else:
            top = max(a, b)
            ca = '<div class="c"><i style="width:%.1f%%"></i>%s</div>' % (max(2, 55 * a / top), md(r[1]))
            cb_ = '<div class="c s"><i style="width:%.1f%%"></i>%s</div>' % (max(2, 55 * b / top), md(r[2]))
        rows.append('<div class="row"><span class="k">%s</span>%s%s</div>' % (md(r[0]), ca, cb_))
    return '<div class="cmp">%s</div>' % "".join(rows)


def cover(title, sub, src, small=""):
    return E.cover(title, sub, src, small)


# ------------------------------------------------------------------ เด็ค
def build():
    ds = RI["dataset"]
    va = RI["val_mAP50"]
    sv = RI["server_test"]
    web = RI["web_test"]
    k10 = RI["skill_v0_run"]
    b, a = M["before"], M["after"]
    ap = a["AP50_per_class"]
    apb = b["AP50_per_class"]
    mm = COST["main_machine"]
    m = RI["machine"]
    inf = [w["inference_ms"] for w in web]
    rts = [w["roundtrip_ms"] for w in web]
    npass = sum(1 for w in web if w["passed"])
    nh_test = M["test_boxes_per_class"]["NO-Hardhat"]
    obs = items_after("รู้จัก Dataset", "**ข้อสังเกต**")

    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    add(cover("LAB 1 · เทรน YOLO ตรวจหมวกนิรภัย แล้วต่อเข้าเว็บ",
              "เช่า GPU มาเทรนต่อด้วยข้อมูลของเรา แล้วโมเดลดีขึ้นแค่ไหน และนำไปต่อกับเว็บจริงได้อย่างไร",
              "img/s01-site.jpg", small="สัปดาห์ที่ 3 · Vast.ai Application · LAB 1"))
    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("เทรนต่อ %.0f วินาที mAP50 บน Test Set เพิ่มจาก %s เป็น %s และค่าเช่าทั้ง LAB คือ %s"
            % (RI["train_seconds"], f3(b["mAP50"]), f3(a["mAP50"]), usd(COST["lab_total"])),
            "results/images/ap50_per_class.png",
            "แท่งสีเทาคือโมเดลก่อนเทรน ซึ่งมีคะแนนเฉพาะ Person และ vehicle ส่วนแท่งสีน้ำเงินคือโมเดลหลังเทรน ซึ่งมีคะแนนทุกคลาส (AP50 รายคลาส บน Test Set %d ภาพ)" % M["test_images"],
            tag="results/metrics.json"))
    add(fig("บทนี้มี 4 ส่วน คือ ภาคพื้นฐาน งานหลัก 8 ขั้น สกิลเวอร์ชัน 0 และสรุป", pick("img/n21-roadmap.jpg", "image/lab1-overview.png"),
            "ภาคพื้นฐานอธิบายสิ่งที่ต้องรู้ก่อนลงมือ จากนั้นจึงทำ 10 ขั้น ขั้นละ 1 พรอมต์"))
    add(S("วิธีใช้สไลด์: เลื่อนหน้า คัดลอกพรอมต์ และติ๊กตรวจผลของตัวเอง", cards([
        ("เลื่อนหน้า", '<p><span class="kbd">→</span> หรือ <span class="kbd">Space</span> ไปหน้าถัดไป และ <span class="kbd">←</span> ย้อนกลับ</p>'),
        ("สารบัญและเต็มจอ", '<p><span class="kbd">O</span> เปิดสารบัญ และ <span class="kbd">F</span> เต็มจอ</p>'),
        ("ขยายภาพ", "คลิกภาพเพื่อดูขนาดเต็ม ภาพคำตอบจริงอ่านได้ชัดเมื่อขยาย"),
        ("คัดลอกพรอมต์ทั้งหมด", "ปุ่มบนสไลด์พรอมต์คัดลอกพรอมต์ครบทุกบรรทัดตรงกับ README แล้วนำไปวางในช่องพิมพ์ของ Claude Code"),
        ("ตรวจผลของคุณ", "หลังรันแต่ละขั้น ให้ติ๊กรายการที่ตรวจแล้ว เบราว์เซอร์จะจำค่าที่ติ๊กไว้"),
        ("รายละเอียดเต็ม", 'ทุกตารางและคำอธิบายอยู่ใน [README.md](README.md)'),
    ], 3), cls="mid"))

    # ===== ภาคพื้นฐาน
    CTX.update(kicker="", group="ภาคพื้นฐาน")
    add(E.divider("ภาคพื้นฐาน", "โจทย์ ข้อมูล โมเดล และทฤษฎีที่ต้องใช้",
                  "<p>เหตุที่ต้องเทรนเอง หน้าตาของ Dataset สิ่งที่ YOLO11s รับและตอบ และทฤษฎี 9 ข้อ</p>",
                  pick("img/p22-study.jpg", "img/s01-site.jpg"), small=PART % 1))
    CTX.update(kicker="ภาคพื้นฐาน · โจทย์", group="ภาคพื้นฐาน · โจทย์และข้อมูล")
    if has("img/p21-monitor.jpg"):
        add(photo_band("โจทย์ · คนเฝ้ากล้องทั้งวันไม่ไหว", "img/p21-monitor.jpg",
                       "ผู้ควบคุมงานไม่สามารถเฝ้ากล้องทุกตัวได้ตลอดวัน LAB นี้จึงสร้างเว็บที่ตรวจรูปหน้างาน แล้วบอกว่าใครไม่สวมหมวกนิรภัย",
                       small="โจทย์ของ LAB 1"))
    add(fig("โมเดลสำเร็จรูปรู้จักคน แต่ไม่รู้จักหมวกนิรภัย จึงต้องเทรนต่อด้วยข้อมูลของเรา", "image/why1-yolo.png",
            " ".join(para("ทำไปเพื่ออะไร", "โมเดลสำเร็จรูป")["lines"])))

    CTX["kicker"] = "ภาคพื้นฐาน · Dataset"
    t = {r[0]: r[1] for r in table("รู้จัก Dataset", "หัวข้อ")["rows"]}
    add(big("Dataset มีภาพหน้างานก่อสร้าง %s ภาพ แต่ละภาพมีกรอบเฉลยหลายกรอบจาก 10 คลาส"
            % format(ds["train_images"] + ds["valid_images"] + ds["test_images"], ","), "results/dataset_samples.jpg",
            ["**Training Set** %s ภาพ (%s กรอบ) ใช้เทรนโมเดล" % (format(ds["train_images"], ","), format(ds["train_boxes"], ",")),
             "**Validation Set** %d ภาพ (%d กรอบ) และ **Test Set** %d ภาพ (%d กรอบ)" % (ds["valid_images"], ds["valid_boxes"], ds["test_images"], ds["test_boxes"]),
             obs[2]],
            post=note("%s · %s · สัญญาอนุญาต %s" % (t["ชื่อ"], t["รูปแบบ"], t["สัญญาอนุญาต"]), label="ที่มา"),
            tag="ภาพจริง 8 รูปจาก Training Set"))
    add(big("label 1 บรรทัดคือกรอบ 1 กรอบ เขียนเป็นคลาสตามด้วยจุดกลาง ความกว้าง และความสูง", pick("img/n01-label.jpg", "results/dataset_samples.jpg"),
            ["ไฟล์ `.txt` 1 ไฟล์ต่อภาพ มี **บรรทัดละ 1 กรอบ** รูปแบบ `คลาส x_กลาง y_กลาง กว้าง สูง` ค่า 0–1 เทียบกับขนาดภาพ",
             "`5 0.52 0.48 0.21 0.67` คือคลาสหมายเลข 5 (**Person**) จุดกลางกรอบอยู่กลางภาพ",
             "กรอบกว้าง 21% และสูง 67% ของภาพ ภาพ 1 ภาพมีได้หลายสิบกรอบ"]))
    rows = sorted(ds["train_boxes_per_class"].items(), key=lambda x: -x[1])
    add(S("Person มีกรอบมากกว่า vehicle หรือ Mask ราว 6 เท่า Dataset นี้จึงมีคลาสไม่สมดุล",
          bars([(c, "", n, rows[0][1], format(n, ",")) for c, n in rows]) + note(obs[0]),
          tag="กรอบใน Training Set"))

    CTX["kicker"] = "ภาคพื้นฐาน · โมเดล"
    mt = {r[0]: r[1] for r in table("รู้จักโมเดลที่ใช้", "หัวข้อ")["rows"]}
    add(big("YOLO11s รับภาพ 1 รูป แล้วตอบเป็นรายการกรอบ แต่ละกรอบมีคลาสและ Confidence", "image/model-yolo11s.png",
            ["**Input** %s · **Output** %s" % (mt["Input"], mt["Output"]),
             "**ขนาด** %s ของ Ultralytics เทรนมาก่อนบน COCO 80 คลาส" % mt["ขนาด"],
             "**ใช้ใน LAB นี้** %s" % mt["LAB นี้ใช้ทำอะไร"]]))

    CTX.update(kicker="ภาคพื้นฐาน · ทฤษฎี", group="ภาคพื้นฐาน · ทฤษฎี 9 ข้อ")
    add(big("ทฤษฎี 1 · Object Detection ให้กรอบหลายกรอบจากรูปเดียว แต่ละกรอบมีคลาส Confidence และพิกัด", "image/t1-detection.png",
            ["Object Detection ตอบว่ามีอะไร อยู่ตรงไหน เป็นรายการกรอบ",
             "การจำแนกทั้งรูป (Classification) ตอบได้คำเดียวต่อรูป แต่งานความปลอดภัยต้องรู้ว่าคนไหนไม่สวมหมวกและมีกี่คน",
             "ใน LAB นี้ใช้ 8.5 ms ต่อรูปบน RTX 4090 และรูป `no_hardhat_1` ได้ 33 กรอบในครั้งเดียว"]))
    add(big("ทฤษฎี 2 · Fine-tuning ไม่ต้องเริ่มจากศูนย์ จึงใช้ข้อมูลน้อยและเทรนเร็ว", "image/t1-why-finetune.png",
            ["เริ่มจากโมเดลที่เทรนกับ Dataset ใหญ่มาแล้ว (Pre-trained บน COCO 80 คลาส) แล้ว **เทรนต่อ** ด้วยข้อมูลของเรา",
             "การเทรนจากศูนย์ต้องใช้ภาพจำนวนมากและเวลานาน ส่วนโมเดล Pre-trained รู้จักขอบ รูปร่าง และคนอยู่แล้ว"]))
    add(big("ทฤษฎี 2 · Fine-tuning เปลี่ยนส่วนทำนายคลาสจาก 80 คลาสของ COCO เป็น 10 คลาสของเรา", "image/t1-finetune.png",
            ["ส่วนที่สกัดลักษณะของภาพถูกใช้ต่อ ส่วนที่ทำนายคลาสถูกเปลี่ยนเป็น 10 คลาส แล้วปรับ weight ทั้งโมเดล",
             "ใน LAB นี้ใช้ %s ภาพ เทรน %.0f วินาที mAP50 เพิ่มจาก %s เป็น %s" % (format(ds["train_images"], ","), RI["train_seconds"], f3(b["mAP50"]), f3(a["mAP50"]))]))
    st = {r[0]: r for r in table("3 · Training", "ชุด")["rows"]}
    add(big("ทฤษฎี 3 · ตัดสินผลด้วย Test Set ที่โมเดลไม่เคยเห็น เพราะภาพที่เคยเห็นให้คะแนนสูงเกินจริง", "image/t1-split.png",
            ["**Training Set** %s ภาพ ใช้%s" % (st["Training Set"][1], st["Training Set"][2]),
             "**Validation Set** %s ภาพ ใช้%s" % (st["Validation Set"][1], st["Validation Set"][2]),
             "**Test Set** %s ภาพ ใช้%s" % (st["Test Set"][1], st["Test Set"][2])],
            post=note("mAP50 บน Validation Set ได้ %s แต่บน Test Set ได้ %s" % (f3(va["epoch50"]), f3(a["mAP50"])), label="ใน LAB นี้")))
    add(evidence("ทฤษฎี 4 · mAP50 ขึ้นเร็วในช่วงแรกแล้วแบน ส่วน loss ของทั้งสองชุดลดลงพร้อมกัน", "results/images/curves.png",
                 ["1 Epoch คือโมเดลเห็นภาพ Training Set ครบ 1 รอบ ใน LAB นี้ใช้ราว 10 วินาทีต่อ Epoch",
                  "กราฟซ้าย: ถ้า loss ของ Training ลดแต่ของ Validation กลับเพิ่ม แปลว่าเริ่ม Overfitting รอบนี้ลดลงพร้อมกัน จึงยังไม่ Overfitting",
                  "กราฟขวา: mAP50 บน Validation Set ได้ %s ที่ Epoch 10, %s ที่ Epoch 25 และ %s ที่ Epoch 50" % (f3(va["epoch10"]), f3(va["epoch25"]), f3(va["epoch50"]))],
                 cap="กราฟจริงของ LAB นี้", tag="results/images/curves.png"))
    mp = {r[0]: r for r in table("5 · IoU", "ตัวชี้วัด")["rows"]}
    add(big("ทฤษฎี 5 · IoU วัดว่ากรอบซ้อนกับเฉลยเท่าใด และ mAP รวมผลทุกคลาสเป็นตัวเลขเดียว", "image/t1-map.png",
            ["IoU = พื้นที่ซ้อนทับ ÷ พื้นที่รวมของกรอบทำนายกับกรอบเฉลย",
             "AP คือคะแนนของ 1 คลาส และ mAP คือค่าเฉลี่ย AP ของทุกคลาส (0–1 ยิ่งสูงยิ่งดี)",
             "หลังเทรน **mAP50** (%s) ได้ %s ส่วน **mAP50-95** (%s) ได้ %s" % (mp["mAP50"][1], mp["mAP50"][2], mp["mAP50-95"][1], mp["mAP50-95"][2])]))
    add(big("ทฤษฎี 6 · Confidence Threshold คือเส้นตัดว่าจะเชื่อกรอบไหน", "image/t1-confidence.png",
            ["AI server ของ LAB นี้ส่งเฉพาะกรอบที่ได้ 0.35 ขึ้นไป",
             "ตั้งต่ำจะเจอมากขึ้นแต่เตือนผิดมากขึ้น ตั้งสูงจะเตือนผิดน้อยลงแต่หลุดมากขึ้น",
             "เว็บตัดสินไม่ผ่านเมื่อมีกรอบ NO-Hardhat ที่ผ่านเกณฑ์อย่างน้อย 1 กรอบ ในภาพเทียบของขั้นที่ 4 มีกรอบ NO-Hardhat ที่ได้เพียง 0.37"]))
    add(big("ทฤษฎี 7 · เวลาที่ผู้ใช้รอเกือบทั้งหมดคือเครือข่าย ไม่ใช่เวลาของโมเดล", "image/lab1-system.png",
            ["Inference Server โหลดโมเดลค้างไว้บน GPU แล้วรอรับรูปทาง HTTP ตอบกลับเป็น JSON",
             "ฝั่ง server ของเว็บเป็นผู้แนบ **API key** ค่า key จึงไม่ถูกส่งถึงเบราว์เซอร์",
             "โมเดลใช้ราว 20 ms ต่อรูป แต่เวลาส่งรูปไป-กลับคือ 540–2,077 ms เพราะเครื่องเช่าอยู่ California"]))
    add(big("ทฤษฎี 8 · ค่าเช่า GPU คิดตามเวลาที่เครื่องเปิด ไม่ใช่เวลาที่เทรน", "image/t1-cost.png",
            ["คิดเงินตามเวลาที่เครื่องเปิด (GPU + disk) บวกค่ารับส่งข้อมูล เครื่องที่ลืมลบและเครื่องที่เปิดไม่ขึ้นก็ถูกคิดเงิน",
             "ราคาตอนค้นหา ($0.366) คิด disk ขนาดเริ่มต้น เมื่อขอ disk 40 GB ราคาจริงเป็น $0.408 ต่อชั่วโมง",
             "LAB นี้เทรน 8.5 นาที แต่เครื่องเปิด 52 นาที ค่าเช่ารวมเครื่องที่เปิดไม่ขึ้น 3 เครื่องคือ **%s**" % usd(COST["lab_total"])]))
    add(big("ทฤษฎี 9 · Vibe coding ตรึงค่าที่ต้องเทียบได้ และปล่อยวิธีเขียนโค้ดให้ AI", "image/t1-vibe.png",
            ["เราบอกสิ่งที่ต้องการเป็นข้อ ๆ แล้ว AI เขียนโค้ด รัน แก้เอง และอธิบายโค้ดให้ฟัง",
             "ค่าที่ต้องตรึง ได้แก่ โมเดลตั้งต้น Epoch ขนาดภาพ batch seed วิธีวัด และรูปแบบข้อมูลระหว่าง server กับเว็บ",
             "ใน LAB นี้ AI เขียนสคริปต์ 5 ไฟล์ (486 บรรทัด) และเว็บ 30 ไฟล์"]))

    # ===== ภาค LAB
    CTX.update(kicker="ภาค LAB", group="ภาค LAB · ก่อนเริ่ม")
    add(E.divider("ภาค LAB", "10 ขั้น 10 พรอมต์ จากโฟลเดอร์ว่างถึงสกิล v0",
                  "<p>%s</p>" % md(" ".join(para("ทำไปเพื่ออะไร", "LAB นี้มี")["lines"])), "img/s02-gpu.jpg", small=PART % 2))
    add(fig("แผนที่ของ LAB: ขั้นที่ 1–8 คืองานหลัก และขั้นที่ 9–10 เก็บงานเป็นสกิล v0", "image/lab1-overview.png",
            "ขั้นที่ 6 และ 7 ทำบน **เครื่องของเรา** ขั้นอื่นทำบน **เครื่องเช่า** บน Vast.ai"))
    ex = {r[0]: r[1] for r in table("การทดลอง", "หัวข้อ")["rows"]}
    add(big("การทดลองเทียบโมเดลก่อนเทรนกับหลังเทรน บน Test Set เดียวกัน", pick("img/n02-experiment.jpg", "image/t1-why-finetune.png"),
            ["**ก่อนเทรน** คือ `yolo11s` ที่เทรนบน COCO และ **หลังเทรน** คือโมเดลเดิมเทรนต่อ 50 Epoch (ภาพ 640 · batch 32 · seed 0)",
             "วัดด้วย **Test Set 82 ภาพ** และสคริปต์เดียวกันทั้งสองโมเดล ได้ mAP50 mAP50-95 AP50 รายคลาส และเวลาต่อรูป",
             "เครื่อง %s" % ex["เครื่อง"]]))
    add(big("ก่อนเริ่ม: เตรียมเครื่องมือให้ครบ แล้วทำขั้นที่ 1 ถึง 10 ให้จบในรอบเดียว", pick("img/n24-setup.jpg", "image/lab1-overview.png"),
            ["ทำ [LAB 0](../README.md) ก่อน เพื่อเตรียม key 3 ตัว",
             "เปิด Claude Code ที่โฟลเดอร์ `02_VastAi_Application` ซึ่งพรอมต์เรียกว่าโฟลเดอร์ปัจจุบัน ขั้นที่ใช้เครื่องเช่าทำงานผ่านสกิล `vastai` ใน container `multi-account`",
             "คัดลอกพรอมต์ทีละขั้น วางในช่องพิมพ์ของ Claude Code แล้วรอจนจบก่อนไปขั้นถัดไป"],
            post=note(ex["เวลาและค่าเช่าจริง"], label="เวลาและค่าเช่าจริง")))

    # ----- ขั้นที่ 1
    CTX.update(kicker="ภาค LAB · ขั้นที่ 1 จาก 10 · เช่าเครื่อง GPU", group="ขั้นที่ 1 · เช่าเครื่อง GPU")
    add(divider(1, "เช่าเครื่อง GPU", "%s · %s ต่อชั่วโมง · %s" % (m["gpu"], usd(m["dph_total"]), m["location"]), pick("img/p23-rack.jpg", "img/s02-gpu.jpg")))
    add(big("ขั้นที่ 1: เช่าเครื่องตามเกณฑ์ แล้วตรวจว่าเห็น GPU จริง", "img/n03-rent.jpg", FIG["n03-rent"]["steps"]))
    add(prompt_step(1, "เช่าเครื่อง GPU"))
    add(check(1, ["ได้ RTX 4090 1 ใบ ราคารวมไม่เกิน $0.70 ต่อชั่วโมง และเครื่องมีป้าย `vapp-lab1`",
                  "AI เข้าไปในเครื่องแล้วเห็น GPU จริง",
                  "มีตารางภาษาไทย: GPU · ราคาต่อชั่วโมง · ที่ตั้ง · CPU cores · เวลาที่รอจนเครื่องพร้อม",
                  "เครื่องที่เปิดไม่ขึ้นถูกลบหมดแล้ว",
                  "AI บอกว่าเครื่องยังเปิดอยู่ (เงินเริ่มเดินแล้ว)"], "เช่าเครื่อง GPU"))
    add(evidence("ได้ RTX 4090 ราคา %s ต่อชั่วโมง หลังจากเครื่อง 3 เครื่องแรกเปิดไม่ขึ้น" % usd(m["dph_total"]), "img/c01-step1.jpg",
                 ["ได้เครื่องที่ %s มี %d CPU cores ราคาตอนค้นหาคือ $0.366 แต่ราคาจริงเป็น %s เพราะขอ disk 40 GB" % (m["location"].split(",")[0], m["cpu_cores"], usd(m["dph_total"])),
                  "เครื่องเช่าเปิดไม่ขึ้นได้ บางเครื่อง running แต่ SSH เข้าไม่ได้ บางเครื่องค้างที่ loading ทั้ง 3 เครื่องถูกคิดเงินรวม %s จึงต้องลบทันที" % usd(COST["machines_failed_to_start"]),
                  "ตั้งแต่ขั้นนี้เงินเริ่มเดินชั่วโมงละ $0.41 จนกว่าจะลบเครื่องในขั้นที่ 8"],
                 cap=caption(heading(1)) + " · " + CROP_CAP % "image/lab1-step1.png", bad=(1,)))

    # ----- ขั้นที่ 2
    CTX.update(kicker="ภาค LAB · ขั้นที่ 2 จาก 10 · เตรียม Dataset", group="ขั้นที่ 2 · เตรียม Dataset")
    add(divider(2, "เตรียม Dataset", "Training %s · Validation %s · Test %s ภาพ · ภาพตัวอย่าง 8 รูป" % (
        format(ds["train_images"], ","), ds["valid_images"], ds["test_images"]), pick("img/p24-photos.jpg", "img/s01-site.jpg")))
    add(big("ขั้นที่ 2: Dataset ลงเครื่องเช่าโดยตรง และกลับมาเฉพาะภาพตัวอย่าง", "img/n04-dataset.jpg", FIG["n04-dataset"]["steps"]))
    add(prompt_step(2, "เตรียม Dataset และดูตัวอย่างภาพ"))
    add(check(2, ["Training Set %s · Validation Set %d · Test Set %d ภาพ และ %d คลาส" % (
                      format(ds["train_images"], ","), ds["valid_images"], ds["test_images"], len(ds["train_boxes_per_class"])),
                  "มีไฟล์ `lab1_yolo/results/dataset_samples.jpg` เป็นตาราง 8 รูปจาก Training Set พร้อมกรอบเฉลยและชื่อคลาส",
                  "กรอบและชื่อคลาสในภาพตัวอย่างตรงกับสิ่งที่เห็นในภาพ",
                  "มีจำนวนกรอบของแต่ละคลาสใน Training Set",
                  "ค่า key ไม่ปรากฏในคำตอบ และไม่ถูกทิ้งไว้บนเครื่องเช่า"], "เตรียม Dataset"))
    add(evidence("ได้ %s / %d / %d ภาพ ตรงกับที่ Dataset ระบุ แต่คำตอบเป็นภาษาอังกฤษ" % (
        format(ds["train_images"], ","), ds["valid_images"], ds["test_images"]), "img/c02-step2.jpg",
        ["Training Set %s ภาพ (%s กรอบ) Validation Set %d ภาพ (%d กรอบ) และ Test Set %d ภาพ (%d กรอบ) ครบ 10 คลาส"
         % (format(ds["train_images"], ","), format(ds["train_boxes"], ","), ds["valid_images"], ds["valid_boxes"], ds["test_images"], ds["test_boxes"]),
         "เปิดดู `results/dataset_samples.jpg` ว่ากรอบและชื่อคลาสตรงกับสิ่งที่เห็นในภาพ",
         "คำตอบของรอบนี้เป็นภาษาอังกฤษทั้งที่สั่งให้สรุปภาษาไทย ถ้าต้องการให้พิมพ์ต่อว่า \"สรุปอีกครั้งเป็นภาษาไทย\""],
        cap=caption(heading(2)) + " · " + CROP_CAP % "image/lab1-step2.png", bad=(2,)))
    add(big("ค่า key หลุดไปอยู่ในผลคำสั่งของ AI ได้ เมื่อเกิดขึ้นต้องสร้าง key ใหม่ทันที", pick("img/n26-key.jpg", "img/n04-dataset.jpg"),
            ["ในรอบจริง AI เผลอสั่งตรวจไฟล์ `.env` จนค่า key ไปปรากฏในผลคำสั่งของตัวเอง",
             "AI แจ้งให้เปลี่ยน key เอง (ดูย่อหน้า About the key ในภาพคำตอบหน้าก่อน)",
             "ถ้าเจอแบบนี้ ให้สร้าง key ใหม่ที่ Roboflow ทันที"], tag="เหตุการณ์จริง"))

    # ----- ขั้นที่ 3
    CTX.update(kicker="ภาค LAB · ขั้นที่ 3 จาก 10 · Training 50 Epoch", group="ขั้นที่ 3 · Training")
    add(divider(3, "Training", "เทรน %.0f วินาที · mAP50 บน Validation Set ที่ Epoch 50 = %s" % (RI["train_seconds"], f3(va["epoch50"])),
                pick("img/p25-gpu.jpg", "img/s02-gpu.jpg")))
    add(big("ขั้นที่ 3: AI เขียน train.py จาก requirement แล้วนำไปเทรนบนเครื่องเช่า", pick("img/n27-train.jpg", "image/t1-vibe.png"),
            prompt_lines(3, 3)))
    add(prompt_step(3, "เขียนโค้ดเทรน แล้ว Training 50 Epoch"))
    add(check(3, ["มีไฟล์ `lab1_yolo/code/train.py` ที่เริ่มจาก `yolo11s` ของ COCO",
                  "เทรนครบ 50 Epoch (ภาพ 640 · batch 32 · seed 0) และมีเวลาที่ใช้เทรน",
                  "มี mAP50 บน Validation Set ที่ Epoch 10, 25 และ 50",
                  "AI อธิบายโค้ด 3–5 บรรทัดว่าแต่ละส่วนทำอะไร",
                  "AI บอกว่าเครื่องยังเปิดอยู่"], "Training 50 Epoch"))
    add(evidence("10 Epoch แรกได้ mAP50 %s แล้วค่อย ๆ แบนจนถึง %s ที่ Epoch 50" % (f3(va["epoch10"]), f3(va["epoch50"])), "img/c03-step3.jpg",
                 ["mAP50 บน Validation Set ได้ %s ที่ Epoch 10, %s ที่ Epoch 25 และ %s ที่ Epoch 50 ใช้เวลาเทรน %.0f วินาที"
                  % (f3(va["epoch10"]), f3(va["epoch25"]), f3(va["epoch50"]), RI["train_seconds"]),
                  "10 Epoch แรกได้ 81% ของผลสุดท้าย ส่วน Epoch 43 ถึง 50 เพิ่มเพียง 0.006 การเทรนนานกว่านี้จึงได้เพิ่มไม่มาก",
                  "สคริปต์ของรอบนี้เทรนต่อจากจุดเดิมได้ถ้ารันซ้ำ ซึ่งมาจากข้อ 3 ของพรอมต์"],
                 cap=caption(heading(3)) + " · " + CROP_CAP % "image/lab1-step3.png"))
    add(big("การรันครั้งแรกล้ม แล้ว AI แก้เอง โค้ดที่ AI เขียนพังได้ แต่ AI ต้องรันจริงจนผ่าน", pick("img/n28-crash.jpg", "image/t1-vibe.png"),
            ["การรันครั้งแรกหยุดหลัง Epoch 1 เพราะโค้ดส่วนพิมพ์ความคืบหน้าอ่านค่า loss ผิดชนิด",
             "AI แก้โค้ดเอง แล้วเทรนใหม่จนครบ 50 Epoch",
             "ตัวเลขในหน้าก่อนมาจากการรันรอบที่สอง ซึ่งรันครบ"], tag="เหตุการณ์จริง"))

    # ----- ขั้นที่ 4
    CTX.update(kicker="ภาค LAB · ขั้นที่ 4 จาก 10 · Evaluation ก่อน vs หลังเทรน", group="ขั้นที่ 4 · Evaluation")
    add(divider(4, "Evaluation", "mAP50 บน Test Set จาก %s เป็น %s" % (f3(b["mAP50"]), f3(a["mAP50"])), pick("img/p26-compare.jpg", "img/s01-site.jpg")))
    add(big("ขั้นที่ 4: วัด 2 โมเดลด้วยวิธีเดียวกัน แล้วเก็บผลกลับมา", "img/n05-eval.jpg", FIG["n05-eval"]["steps"][:4]))
    add(prompt_step(4, "เขียนโค้ดวัดผล แล้ว Evaluation"))
    add(check(4, ["มี `lab1_yolo/code/eval.py` และ `lab1_yolo/results/metrics.json`",
                  "มีภาพ 3 ชนิด: ภาพเทียบก่อน/หลัง 5 ภาพ · กราฟแท่ง AP50 รายคลาส · กราฟ loss และ mAP ต่อ Epoch",
                  "มีไฟล์โมเดล `lab1_yolo/results/weights/best.pt` บนเครื่องของเรา",
                  "`lab1_yolo/results/samples` มี 6 รูป: 3 รูปพบคนไม่สวมหมวก · 3 รูปทุกคนสวมหมวก",
                  "ตารางก่อน vs หลังมี mAP50 · mAP50-95 · AP50 ของ 5 คลาส · เวลาต่อรูป"], "Evaluation"))
    add(evidence("mAP50 บน Test Set เพิ่มจาก %s เป็น %s ด้วยความเร็วเท่าเดิม" % (f3(b["mAP50"]), f3(a["mAP50"])), "img/c04-step4.jpg",
                 ["mAP50 เพิ่มจาก %s เป็น **%s** และ mAP50-95 จาก %s เป็น **%s** บน Test Set %d ภาพ"
                  % (f3(b["mAP50"]), f3(a["mAP50"]), f3(b["mAP50-95"]), f3(a["mAP50-95"]), M["test_images"]),
                  "Validation ได้ %s แต่ Test ได้ %s ต่ำกว่าเล็กน้อยเป็นเรื่องปกติ เพราะ `best.pt` ถูกเลือกจาก Validation Set" % (f3(va["epoch50"]), f3(a["mAP50"])),
                  "เวลาต่อรูป %.2f ms และ %.2f ms เท่าเดิม เพราะเป็นโมเดลขนาดเดิม" % (b["ms_per_image"], a["ms_per_image"])],
                 cap=caption(heading(4)) + " · ตัวเลขทั้งหมดอยู่ใน [results/metrics.json](results/metrics.json) · " + CROP_CAP % "image/lab1-step4.png"))
    add(evidence("ค่าเฉลี่ยสูงไม่ได้แปลว่าดีทุกคลาส NO-Hardhat ซึ่งสำคัญที่สุดได้เพียง %s" % f3(ap["NO-Hardhat"]), "results/images/ap50_per_class.png",
                 ["ก่อนเทรน มีคะแนนเฉพาะคลาสที่ COCO มี (Person %s · vehicle %s) คลาสอื่นได้ 0 เพราะ **โมเดลไม่มีคลาสนั้น** ไม่ใช่เพราะมองไม่เห็น"
                  % (f3(apb["Person"]), f3(apb["vehicle"])),
                  "หลังเทรน สูงสุดคือ **Hardhat %s** และต่ำสุดคือ **Safety Cone %s**" % (f3(ap["Hardhat"]), f3(ap["Safety Cone"])),
                  "**NO-Hardhat %s** ทั้งที่เป็นคลาสสำคัญที่สุดของงานนี้ (Test Set มีเพียง %d กรอบ) ก่อนใช้งานจริงต้องเก็บภาพคลาสนี้เพิ่ม" % (f3(ap["NO-Hardhat"]), nh_test)],
                 cap="ดูแท่งสีน้ำเงินของ NO-Hardhat และ Safety Cone ซึ่งต่ำกว่าคลาสอื่นอย่างชัดเจน", tag="results/metrics.json", bad=(2,)))
    add(fig("ตัวอย่างจริง 1 ภาพ: ก่อนเทรนเห็นแค่ Person ส่วนหลังเทรนเห็น Hardhat, NO-Hardhat และ NO-Safety Vest",
            "results/images/before_after_2.jpg", "กรอบ **NO-Hardhat** สีแดงในภาพขวาได้ Confidence เพียง 0.37 ใกล้เกณฑ์ 0.35 ของเว็บ"))

    # ----- ขั้นที่ 5
    CTX.update(kicker="ภาค LAB · ขั้นที่ 5 จาก 10 · AI server", group="ขั้นที่ 5 · AI server")
    add(divider(5, "AI server", "/health ได้ %d · ส่งรูปพร้อม key ได้ %d กรอบ · ไม่มี key ได้ %d" % (sv["health"], sv["detect_boxes"], sv["no_key"]),
                pick("img/p27-cables.jpg", "img/s02-gpu.jpg")))
    st5 = FIG["n06-api"]["steps"]
    add(big("ขั้นที่ 5: สัญญา API ระหว่าง AI server กับเว็บ", "img/n06-api.jpg", [st5[0], st5[1] + " ไม่มี key หรือ key ผิด ตอบ **401**", st5[3]],
            post=note(st5[4])))
    add(prompt_step(5, "เขียนโค้ด AI server แล้วเปิดใช้งาน"))
    add(check(5, ["มี `lab1_yolo/code/serve.py` · server เปิดที่พอร์ต 8080 บนเครื่องเช่า และทำงานต่อได้แม้การเชื่อมต่อหลุด",
                  "`/health` ตอบว่าพร้อม ชื่อโมเดล `ppe-yolo11s` และรายชื่อคลาส โดยไม่ใช้ key",
                  "ส่งรูปจาก Test Set พร้อม key แล้วได้กรอบ",
                  "ส่งแบบไม่มี key ถูกปฏิเสธ (401)",
                  "มีไฟล์ `lab1_yolo/code/web/.env` ที่มี `YOLO_BASE_URL` `YOLO_API_KEY` `YOLO_MODEL=ppe-yolo11s` · ไม่มีค่า key ในคำตอบ"],
              "AI server"))
    add(evidence("AI server ผ่านทั้ง 3 ข้อทดสอบ และคนที่ไม่มี key ใช้ไม่ได้", "img/c05-step5.jpg",
                 ["`/health` ได้ %d ส่งรูปพร้อม key ได้ %d กรอบ และส่งแบบไม่มี key ได้ %d ซึ่งยืนยันว่าคนไม่มี key ใช้ไม่ได้" % (sv["health"], sv["detect_boxes"], sv["no_key"]),
                  "รูปแรกใช้ %d ms จากนั้นราว %d ms มากกว่า 8.5 ms ของขั้นที่ 4 เพราะ server จับเวลาทั้งคำสั่งทำนาย ไม่ใช่เฉพาะช่วงของโมเดล" % (sv["inference_ms_first"], sv["inference_ms_typical"]),
                  "ข้อ 2–4 ของพรอมต์คือสัญญา API จึงเขียนซ้ำในพรอมต์ขั้นที่ 6 และไฟล์ `lab1_yolo/code/web/.env` เชื่อมเว็บกับโมเดล ไฟล์นี้ไม่ถูกเก็บขึ้น git"],
                 cap=caption(heading(5)) + " · " + CROP_CAP % "image/lab1-step5.png"))

    # ----- ขั้นที่ 6
    CTX.update(kicker="ภาค LAB · ขั้นที่ 6 จาก 10 · เว็บ SiteSafe", group="ขั้นที่ 6 · เว็บ SiteSafe")
    add(divider(6, "เว็บ SiteSafe", "เว็บ Next.js + PostgreSQL ที่ http://localhost:3401 · ลองส่งรูป 1 รูปได้ผลจริง", pick("img/p28-tablet.jpg", "img/s01-site.jpg")))
    pr6 = prompt_lines(6, 8)
    add(big("ขั้นที่ 6: AI สร้างเว็บบนเครื่องเรา ที่ส่งรูปต่อไปยัง AI server โดย key ไม่ถึงเบราว์เซอร์", pick("img/n29-sitesafe.jpg", "image/lab1-system.png"),
            [pr6[1], pr6[3], pr6[4]]))
    add(prompt_step(6, "สร้างเว็บตรวจความปลอดภัยหน้างาน"))
    add(check(6, ["เว็บเปิดได้ที่ http://localhost:3401 ด้วย docker compose (project `vapp-lab1`)",
                  "หน้าแรก: อัปโหลดหรือกดรูปตัวอย่าง แล้วได้รูปพร้อมกรอบ และป้าย ผ่าน หรือ ไม่ผ่าน",
                  "ใต้ป้ายผลมีจำนวนคน สวมหมวก ไม่สวมหมวก ไม่สวมเสื้อสะท้อนแสง เวลาที่โมเดลใช้ และเวลาไป-กลับ",
                  "มีหน้าประวัติ และมุมบนแสดงว่า AI server พร้อมไหม",
                  "ไฟล์ `lab1_yolo/code/web/.env` ยังอยู่ และไม่มีค่า key ในหน้าเว็บที่เบราว์เซอร์ได้รับ"], "เว็บ SiteSafe"))
    add(evidence("เว็บเปิดได้ และรูปแรกที่ลองส่งได้ผล ไม่ผ่าน ตรงกับรูป", "img/c06-step6.jpg",
                 ["ลองส่งรูป `no_hardhat_1.jpg` ได้ผล **ไม่ผ่าน** พบ NO-Hardhat 8 กรอบ โมเดลใช้ 32.1 ms และเวลาไป-กลับ 954.5 ms",
                  "key อยู่ใน container ฝั่ง server ของเว็บเท่านั้น และ AI ตรวจแล้วว่าไม่มีค่า key ในหน้าเว็บที่ส่งให้เบราว์เซอร์",
                  "พรอมต์ขั้นนี้ไม่มีบรรทัด container เพราะเว็บทำงานบนเครื่องเรา หน้าตาเว็บของคุณอาจต่างไป เพราะพรอมต์ไม่ได้กำหนดการออกแบบ"],
                 cap=caption(heading(6)) + " · " + CROP_CAP % "image/lab1-step6.png"))

    # ----- ขั้นที่ 7
    CTX.update(kicker="ภาค LAB · ขั้นที่ 7 จาก 10 · ทดสอบเว็บ", group="ขั้นที่ 7 · ทดสอบเว็บ")
    add(divider(7, "ทดสอบเว็บ", "%d รูป · ผ่าน %d · ไม่ผ่าน %d · ตรงกับชื่อรูปทุกรูป" % (len(web), npass, len(web) - npass), pick("img/p29-phone.jpg", "img/s01-site.jpg")))
    add(prompt_step(7, "ทดสอบเว็บกับรูปตัวอย่าง"))
    add(check(7, ["เว็บเปิดอยู่และต่อ AI server ได้",
                  "ส่งรูปใน `lab1_yolo/results/samples` ครบ 6 รูป",
                  "กลุ่ม `all_hardhat` ได้ ผ่าน · กลุ่ม `no_hardhat` ได้ ไม่ผ่าน",
                  "ผลทั้ง 6 ครั้งขึ้นในหน้าประวัติ",
                  "มีตาราง รูป · ผล · จำนวนคนไม่สวมหมวก · เวลาที่โมเดลใช้ · เวลาไป-กลับ"], "ทดสอบเว็บ"))
    add(S("โมเดลใช้ %.0f–%.0f ms แต่ผู้ใช้รอ %s–%s ms เวลาเกือบทั้งหมดคือการส่งรูปข้ามอินเทอร์เน็ต" % (min(inf), max(inf), ms(min(rts)), ms(max(rts))),
          time_chart(web) + '<p class="cap">ผลตรงกับชื่อรูปทุกรูป กลุ่ม `all_hardhat` ผ่านทั้งหมด กลุ่ม `no_hardhat` ไม่ผ่านทั้งหมด และรูปแรกช้าที่สุด '
          '([ภาพคำตอบจริง](image/lab1-step7.png))</p>'.replace("`all_hardhat`", "<code>all_hardhat</code>").replace("`no_hardhat`", "<code>no_hardhat</code>").replace(
              "([ภาพคำตอบจริง](image/lab1-step7.png))", '(<a href="image/lab1-step7.png" target="_blank">ภาพคำตอบจริง</a>)'),
          tag="results/run_info.json"))
    add(big("หน้าเว็บจริงแสดงรูปพร้อมกรอบ ป้ายผล และตัวเลขใต้ป้าย", "img/c11-web-result.jpg",
            ["ป้ายผล **ไม่ผ่าน** เมื่อพบ NO-Hardhat ที่ผ่านเกณฑ์ 0.35 อย่างน้อย 1 กรอบ",
             "รูปนี้พบผู้ไม่สวมหมวกนิรภัย 8 คน จากจำนวนคน 9 คน เวลาที่โมเดลใช้ 43.0 ms และเวลาส่งรูปไป-กลับ 2109 ms",
             "รูปชุดนี้ถูกเลือกตามผลของโมเดลเอง จึงตรงทุกรูป กับรูปใหม่จากหน้างานจริง โมเดลยังหลุดได้ เพราะ AP50 ของ NO-Hardhat คือ %s" % f3(ap["NO-Hardhat"])],
            post='<p class="cap">ส่วนหนึ่งของหน้าจอจริง · <a href="results/web/web_result_1.png" target="_blank">ภาพเต็ม</a></p>', tag="ผลจริง"))
    add(E.slide("อัปโหลดรูปเอง หรือกดรูปตัวอย่าง แล้วเว็บวาดกรอบและขึ้นป้ายผลทันที",
                '<div class="figrow">%s</div><p class="cap">%s</p>' % (
                    "".join('<div class="fig">%s</div>' % img(s) for s in ["results/web/web_upload_flow.gif", "results/web/web_sample_pass.gif"]),
                    md("ซ้าย: อัปโหลดรูปเอง ได้ **ไม่ผ่าน** · ขวา: กดรูปตัวอย่างที่ทุกคนสวมหมวก ได้ **ผ่าน**")), maxfs=1.1))
    add(fig("หน้าประวัติเก็บผลทุกครั้งใน PostgreSQL ตรวจทั้งหมด 22 รูป ผ่าน 10 ไม่ผ่าน 12", "img/c12-web-history.jpg",
            "ส่วนหนึ่งของหน้าจอจริง กดแต่ละแถวเพื่อดูรายละเอียดของการตรวจครั้งนั้น · [ภาพเต็ม](results/web/web_history.png)", tag="ผลจริง"))

    # ----- ขั้นที่ 8
    CTX.update(kicker="ภาค LAB · ขั้นที่ 8 จาก 10 · ลบเครื่องและสรุปค่าใช้จ่าย", group="ขั้นที่ 8 · ลบเครื่อง")
    add(divider(8, "ลบเครื่อง", "ไม่มีเครื่องค้าง · ยอดสุดท้ายของเครื่องหลัก %s · รวมทั้ง LAB %s" % (usd(mm["total"]), usd(COST["lab_total"])),
                pick("img/p30-off.jpg", "img/s02-gpu.jpg")))
    pr8 = prompt_lines(8, 2)
    add(big("ขั้นที่ 8: ลบเครื่อง ตรวจว่าไม่มีเครื่องค้าง ปิดเว็บ แล้วสรุปบิลจริง", pick("img/n31-shutdown.jpg", "image/t1-cost.png"),
            pr8 + ["ลบเครื่องแล้วทุกอย่างบนเครื่องหายหมด โมเดลอยู่ที่ `lab1_yolo/results/weights/best.pt` ตั้งแต่ขั้นที่ 4"]))
    add(prompt_step(8, "ลบเครื่องและสรุปค่าใช้จ่าย"))
    add(check(8, ["ไม่มีเครื่องป้าย `vapp-lab1` เหลือในบัญชี แล้วเปิดหน้า Instances ของ Vast.ai ดูอีกครั้ง",
                  "เครื่องป้ายอื่นไม่ถูกแตะ",
                  "เว็บปิดแล้ว โดยประวัติการตรวจยังอยู่",
                  "มีสรุป อายุเครื่อง · ราคาต่อชั่วโมง · ยอด GPU · disk · รับส่งข้อมูล",
                  "ไฟล์ `lab1_yolo/results/weights/best.pt` ยังอยู่บนเครื่องของเรา"], "ลบเครื่อง",
              "ยอดที่อ่านทันทีหลังลบเครื่องต่ำกว่ายอดสุดท้าย เพราะบิลลงบัญชีช้ากว่าเวลาจริง " + VARY))
    add(S("เทรน %.1f นาที แต่เครื่องเปิด %.0f นาที ค่าเช่ารวมทั้ง LAB จึงเป็น %s" % (RI["train_seconds"] / 60, mm["age_hours"] * 60, usd(COST["lab_total"])),
          '<div class="evi"><div class="fig">%s</div></div>' % img("img/c08-step8.jpg", "คำตอบจริงของขั้นที่ 8")
          + cost_bar(mm, COST["machines_failed_to_start"], COST["lab_total"])
          + '<p class="cap">%s · ภาพบนคือส่วนหนึ่งของคำตอบจริง (<a href="image/lab1-step8.png" target="_blank">ภาพเต็ม</a>) แท่งล่างคือยอดในใบแจ้งหนี้</p>' % md(caption(heading(8))),
          tag="results/run_info.json", maxfs=1.2))

    # ===== ปิดท้าย: สกิลเวอร์ชัน 0
    CTX.update(kicker="ปิดท้าย · สกิลเวอร์ชัน 0", group="ปิดท้าย · สกิล v0")
    add(E.divider("ปิดท้าย", "เก็บงานทั้ง LAB เป็นสกิลเวอร์ชัน 0", "<p>%s</p>" % md(intro("ปิดท้าย")), pick("img/p31-binder.jpg", ""), small=PART % 3))
    add(fig("สกิลคือวิธีทำงานที่สำเร็จแล้ว (SKILL.md) รวมกับโค้ดที่ใช้ได้แล้ว (scripts/)", "image/skill-v0.png",
            "ทำทีละขั้น 8 พรอมต์ แล้วให้ AI สรุปเป็น **SKILL.md** พร้อม **scripts/** จากนั้นทำซ้ำได้ใน 1 พรอมต์ และปรับเป็น v1 เมื่อเจอจุดพลาด"))

    CTX.update(kicker="ปิดท้าย · ขั้นที่ 9 จาก 10 · สร้างสกิล v0", group="ขั้นที่ 9 · สร้างสกิล v0")
    add(divider(9, "สร้างสกิล v0", "สกิล `yolo-ppe-train` พร้อม `scripts/` 5 ไฟล์", pick("img/p31-binder.jpg", "")))
    pr9 = prompt_lines(9, 5)
    add(big("ขั้นที่ 9: AI อ่านงานของขั้นที่ 1–8 แล้วเขียน SKILL.md และเก็บโค้ดเข้า scripts/", pick("img/n32-skill.jpg", "image/skill-v0.png"),
            [pr9[1], pr9[2], pr9[3]]))
    add(prompt_step(9, "สร้างสกิลเวอร์ชัน 0"))
    warn = next(" ".join(x["lines"]) for bb in sec(heading(9)) if bb["t"] == "alert" for x in bb["blocks"] if x["t"] == "p")
    warn = warn.replace("⚠️", "").strip()
    add(check(9, ["มี `lab1_yolo/skill_v0/SKILL.md` ชื่อ `yolo-ppe-train` มี name และ description",
                  "SKILL.md มีค่าที่ปรับได้พร้อมค่าเริ่มต้น · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน (ลบเครื่องเสมอ)",
                  "`lab1_yolo/skill_v0/scripts/` มีสคริปต์เทรน วัดผล และ AI server",
                  "สกิลเรียกใช้สกิล `vastai` ต่อ ไม่เขียนวิธีใช้ Vast.ai ซ้ำ",
                  "ติดตั้งที่ `.claude/skills/yolo-ppe-train` ของโฟลเดอร์ปัจจุบัน"], "สร้างสกิล v0", warn))
    add(evidence("สกิล yolo-ppe-train ทำงาน 7 ขั้นได้ในคำสั่งเดียว", "img/c09-step9.jpg",
                 ["คำตอบระบุขั้นงาน 7 ขั้น ตั้งแต่เช่าเครื่องจนลบเครื่อง และให้สกิล `vastai` ทำงานส่วนของ Vast.ai",
                  "สกิลมีตารางค่าที่ปรับได้ เกณฑ์ตรวจผ่าน และกติกาเรื่องเงิน โค้ด 5 ไฟล์อยู่ใน `skill_v0/scripts/`",
                  caption(heading(9)).split(" · สกิลที่ได้")[0]],
                 cap="สกิลที่ได้: [skill_v0/SKILL.md](skill_v0/SKILL.md) · " + CROP_CAP % "image/lab1-step9.png"))

    CTX.update(kicker="ปิดท้าย · ขั้นที่ 10 จาก 10 · ใช้สกิลทำซ้ำ", group="ขั้นที่ 10 · ใช้สกิลทำซ้ำ")
    add(divider(10, "ใช้สกิลทำซ้ำ", "เทรน 10 Epoch · mAP50 จาก %s เป็น %s · ค่าเช่า %s" % (f3(M10["before"]["mAP50"]), f3(M10["after"]["mAP50"]),
                                                                                   usd(COST["skill_v0_run"]["total"])), "img/s02-gpu.jpg"))
    add(prompt_step(10, "ลองใช้สกิลทำซ้ำในคำสั่งเดียว"))
    add(check(10, ["AI ใช้สกิล `yolo-ppe-train` และโค้ดใน `scripts/` โดยไม่เขียนโค้ดใหม่",
                   "เทรน 10 Epoch บนเครื่องป้าย `vapp-lab1-skill` และไม่เปิดเว็บ",
                   "ผลอยู่ที่ `lab1_yolo/results/skill_v0_run` · ผลเดิมใน `lab1_yolo/results` ไม่ถูกเขียนทับ",
                   "มี mAP50 ก่อน vs หลังบน Test Set · เวลาแต่ละขั้น · ค่าใช้จ่ายจริง",
                   "เครื่องถูกลบแล้ว"], "ใช้สกิลทำซ้ำ"))
    r10 = items_after(heading(10), "**อ่านผลอย่างไร**")
    add(evidence("สกิล v0 ผ่านในรอบแรกด้วยพรอมต์ 4 บรรทัด และได้ mAP50 %s จาก 10 Epoch" % f3(M10["after"]["mAP50"]), "img/c10-step10.jpg",
                 [r10[0],
                  "เครื่องพร้อมใน 51 วินาที ขณะที่ขั้นที่ 1 ใช้ 38 นาที อายุเครื่องรวม %.1f นาที และลบเครื่องแล้ว" % k10["machine_age_minutes"],
                  r10[1]],
                 cap=caption(heading(10)).replace("[results/skill_v0_run/](results/skill_v0_run/)", "results/skill_v0_run/") + " · " + CROP_CAP % "image/lab1-step10.png"))
    add(S("สกิล v0 ลดพรอมต์จาก 5 เหลือ 1 และได้ mAP50 %s หรือ 92%% ของผล 50 Epoch" % f3(M10["after"]["mAP50"]),
          compare_bars(table(heading(10), "")) + note(r10[2] + " · " + r10[3]), tag="README · ขั้นที่ 10"))

    # ===== สรุป
    CTX.update(kicker="สรุป", group="สรุป")
    add(E.divider("สรุป", "ผลรวม บทเรียน และสิ่งที่ยังไม่ผ่าน", "<p>Fine-tune บน GPU เช่า แล้วต่อเป็น AI server เว็บ และสกิล v0</p>",
                  pick("img/p32-sunset.jpg", "img/s01-site.jpg"), small=PART % 4))
    add(S("mAP50 บน Test Set เพิ่มจาก %s เป็น %s ด้วย 50 Epoch และ %s ด้วยสกิล v0 แบบ 10 Epoch" % (f3(b["mAP50"]), f3(a["mAP50"]), f3(M10["after"]["mAP50"])),
          bars([("ก่อนเทรน", "yolo11s ของ COCO", b["mAP50"], 1, f3(b["mAP50"])),
                ("หลังเทรน 50 Epoch", "ขั้นที่ 3–4 · %.0f วินาที" % RI["train_seconds"], a["mAP50"], 1, f3(a["mAP50"])),
                ("สกิล v0 · 10 Epoch", "ขั้นที่ 10", M10["after"]["mAP50"], 1, f3(M10["after"]["mAP50"]))])
          + note("mAP50 เต็ม 1.0 · Test Set %d ภาพ · สคริปต์วัดผลเดียวกัน" % M["test_images"], label="ที่มา"),
          tag="metrics.json", cls="mid"))
    names = {1: "เช่าเครื่อง GPU", 2: "เตรียม Dataset", 3: "Training 50 Epoch", 4: "Evaluation", 5: "AI server", 6: "เว็บ SiteSafe",
             7: "ทดสอบเว็บ 6 รูป", 8: "ลบเครื่อง", 9: "สร้างสกิล v0", 10: "ใช้สกิลทำซ้ำ"}
    res = {1: "%s · %s ต่อชั่วโมง" % (m["gpu"], usd(m["dph_total"])),
           2: "%s / %d / %d ภาพ · %d คลาส" % (format(ds["train_images"], ","), ds["valid_images"], ds["test_images"], len(ds["train_boxes_per_class"])),
           3: "%.0f วินาที · mAP50 (Validation) %s" % (RI["train_seconds"], f3(va["epoch50"])),
           4: "mAP50 (Test) %s → %s" % (f3(b["mAP50"]), f3(a["mAP50"])),
           5: "/health %d · กรอบ %d · ไม่มี key %d" % (sv["health"], sv["detect_boxes"], sv["no_key"]),
           6: "ลองส่ง 1 รูป ได้ผลจริง",
           7: "ผ่าน %d · ไม่ผ่าน %d · ตรงทุกรูป" % (npass, len(web) - npass),
           8: "เครื่องหลัก %s · รวมทั้ง LAB %s" % (usd(mm["total"]), usd(COST["lab_total"])),
           9: "`yolo-ppe-train` + `scripts/`",
           10: "mAP50 %s · %s" % (f3(M10["after"]["mAP50"]), usd(COST["skill_v0_run"]["total"]))}
    tt = {"head": ["ขั้น", "งาน", "เวลา", "ผลจริง"],
          "rows": [[str(n), names[n], caption(heading(n)).split(" · ")[0], res[n]] for n in range(1, 11)]}
    add(tbl("ตารางสรุป: 10 ขั้น 10 พรอมต์ ได้โมเดล เว็บ และสกิลที่ทำซ้ำได้", tt,
            post=note("เวลาจาก README ของแต่ละขั้น ขั้นที่ 1 รอบจริงใช้ 38 นาที เพราะเครื่อง 3 เครื่องแรกเปิดไม่ขึ้น", label="หมายเหตุ")))
    add(fig("บทเรียนของ LAB นี้มี 6 ข้อ ตั้งแต่ความคุ้มค่าของ Fine-tuning จนถึงการทำซ้ำด้วยสกิล", pick("img/n33-lessons.jpg", "image/skill-v0.png"),
            "Fine-tuning %s ภาพ %.0f วินาที ได้ mAP50 จาก %s เป็น %s ส่วน NO-Hardhat ยังได้ %s · เทรน %.1f นาที แต่เครื่องเปิด %.0f นาที · โมเดลใช้ %.0f–%.0f ms แต่เวลาไป-กลับ %s–%s ms · โค้ดเทรนล้มในการรันครั้งแรก 1 จุด แล้ว AI แก้เอง"
            % (format(ds["train_images"], ","), RI["train_seconds"], f3(b["mAP50"]), f3(a["mAP50"]), f3(ap["NO-Hardhat"]),
               RI["train_seconds"] / 60, mm["age_hours"] * 60, min(inf), max(inf), ms(min(rts)), ms(max(rts)))))
    add(big("ข้อจำกัดของโมเดล: ยังไม่พร้อมใช้กับหน้างานจริง", "img/c13-noharhat.jpg",
            ["**NO-Hardhat ยังอ่อน** AP50 %s ก่อนใช้งานจริงต้องเก็บภาพคลาสนี้เพิ่ม" % f3(ap["NO-Hardhat"]),
             "**รูปตัวอย่างถูกเลือกตามผลของโมเดลเอง** เว็บจึงตรงทุกรูป แต่กับรูปใหม่จากหน้างานจริง โมเดลยังหลุดได้",
             obs[3]],
            post='<p class="cap">ภาพหลังเทรนของขั้นที่ 4: กรอบ NO-Hardhat สีแดงได้ Confidence เพียง 0.37</p>', tag="ยังไม่ผ่าน"))
    v1 = table(heading(10), "จุดที่ v0")
    add(tbl("สิ่งที่ยังไม่ผ่าน: สกิล v0 ยังพลาด %d จุด ที่ควรแก้ใน v1" % len(v1["rows"]), v1,
            post=note(" ".join(para(heading(10), "วิธีปรับ")["lines"]), label="ทำต่อ"), tag="ยังไม่ผ่าน"))

    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบ LAB 1", "โมเดลตรวจหมวกนิรภัย เว็บ SiteSafe และสกิล v0",
                  '<p>รายละเอียดเต็มของทุกขั้น: <a href="README.md" target="_blank">README.md</a> · '
                  'พรอมต์ทั้ง 10 ขั้น: <a href="PROMPTS.md" target="_blank">PROMPTS.md</a></p>', pick("img/p32-sunset.jpg", "img/s01-site.jpg")))
    return E.SL


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
    p = os.path.join(E.ROOT, OUT)
    page = open(p, encoding="utf-8").read().replace("</style>", EXTRA_CSS + "</style>", 1)
    open(p, "w", encoding="utf-8", newline="\n").write(page)
