#!/usr/bin/env python3
"""สร้างสไลด์ LAB5_Cluster_VLM_Slides.html ของ LAB 5 (เทรน VLM บนคลัสเตอร์ 2 เครื่อง)

  python tools/build_slides.py            (รันจากโฟลเดอร์ของบท)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · อธิบายด้วยภาพที่มีป้ายอยู่ในภาพ · ข้อความข้างภาพไม่เกิน 3-4 ข้อ
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง พรอมต์ และข้อสังเกต: อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ตัวเลขที่เขียนในโครงเรื่อง: ผ่าน n() ซึ่งตรวจว่าข้อความนั้นมีอยู่ใน README.md จริง (ถ้าไม่มี สร้างไม่ผ่าน)
- ภาพตัดจากภาพหน้าจอคำตอบจริง: img/cNN-*.jpg (ตัดจาก image/lab5-stepN.png โดยไม่แก้พิกเซล)
- ภาพอธิบายและภาพถ่าย: tools/slides_figures.py · เครื่องมือเรนเดอร์: tools/slides_engine.py
- รูปแบบหน้าเพิ่มเติมของเด็คนี้ (ภาพใหญ่ + ข้อข้างภาพ, กราฟ + ตัวเลข, ภาพคู่, ภาพถ่ายพร้อมประโยคเดียว, แถบเวลา)
  อยู่ในไฟล์นี้ (CSS2 และฟังก์ชัน pic chart pair band shot timeline)
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, codes, para, CTX, add, note, fig, explain, tiles, cards, bars, tbl, code)

S = E.slide
SECS = E.load("README.md")
OUT, TITLE = "LAB5_Cluster_VLM_Slides.html", "LAB 5 · เทรน VLM บนคลัสเตอร์ 2 เครื่อง · Slides"
README = re.sub(r"\*\*|`", "", E.read("README.md"))
MAYDIFF = "ตัวเลขของคุณอาจต่างจากของผู้สอน เพราะเครื่องเช่า เครือข่าย และคำตอบของ AI ต่างกันในแต่ละรอบ"

# ------------------------------------------------------------------ รูปแบบหน้าเพิ่มเติมของเด็คนี้
CSS2 = r"""
.pic{flex:1 1 0;min-height:0;display:flex;gap:28px;align-items:stretch}
.pic .fig{flex:2.3 1 0;min-width:0;min-height:0}
.pic .side{flex:1 1 0;min-width:0;display:flex;flex-direction:column;justify-content:center;gap:.5em}
.pic .side>*{flex:none;margin:0}
.pic.wide .fig{flex:3 1 0}
.mt{background:#fff;border:1px solid var(--line);border-left:7px solid var(--teal);border-radius:12px;padding:.38em .75em .45em;box-shadow:0 2px 6px rgba(18,48,94,.05)}
.mt .k{font-size:.7em;font-weight:600;color:var(--muted);line-height:1.35}
.mt .num{font-size:1.55em;font-weight:700;color:var(--navy);line-height:1.15;white-space:nowrap}
.mt .s{font-size:.72em;color:var(--muted);line-height:1.35}
.mt.ok{border-left-color:var(--green)}.mt.ok .num{color:var(--green)}
.mt.bad{border-left-color:var(--red)}.mt.bad .num{color:var(--red)}
.mt.warn{border-left-color:var(--orange)}
.shot{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:12px}
.shot .fig{flex:1 1 0;min-height:0}
.pts{flex:none;display:grid;grid-template-columns:repeat(var(--n,3),minmax(0,1fr));gap:12px}
.pts .stp{font-size:.82em}
.capl{flex:none;color:var(--muted);text-align:center;font-size:.8em;line-height:1.45}
.capl a{color:#1d5fd0}
.pair{flex:1 1 0;min-height:0;display:flex;gap:26px;align-items:stretch}
.pair>div{flex:1 1 0;min-width:0;min-height:0;display:flex;flex-direction:column;gap:8px}
.pair .fig{flex:1 1 0;min-height:0}
.pair .ph{flex:none;font-weight:700;color:var(--navy);font-size:.92em;text-align:center}
.pair pre.code{flex:none;font-size:.82em;margin:auto 0}
.slide.band{padding:0;background-size:cover;background-position:center;color:#fff}
.band .bandbox{position:absolute;left:0;right:0;bottom:0;padding:120px 96px 54px;background:linear-gradient(0deg,rgba(6,13,26,.94) 0%,rgba(6,13,26,.82) 55%,rgba(6,13,26,0) 100%)}
.band .bandbox .small{font-size:20px;font-weight:600;color:#8fe0dc;margin-bottom:10px}
.band .bandbox h1{font-size:50px;line-height:1.25;margin:0;color:#fff;max-width:1350px}
.band b{color:#ffd28a}
.band .imgnote{bottom:auto;top:14px}
.mrow{flex:none;display:flex;gap:16px}.mrow .mt{flex:1;min-width:0}
.band .bandbox p{font-size:25px;color:#d6e4fb;margin:16px 0 0;line-height:1.5;max-width:1350px}
.divider .inner .big{margin-top:34px}
.prog{display:flex;gap:10px;margin-top:6px}
.prog span{width:58px;height:12px;border-radius:6px;background:rgba(255,255,255,.2)}
.prog span.done{background:#8fe0dc}.prog span.cur{background:var(--orange)}
.tl{flex:none;display:flex;gap:4px;align-items:stretch;height:78px}
.tl div{min-width:0;border-radius:9px;background:var(--teal);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:.7em;line-height:1.2;overflow:hidden;white-space:nowrap}
.tl div b{color:#fff;font-size:1.25em}
.tl div.loc{background:var(--navy)}.tl div.sk{background:var(--orange)}
.tlcap{flex:none;color:var(--muted);font-size:.78em;text-align:center}
"""
E.CSS += CSS2


def n(s):
    """ข้อความที่มีตัวเลข ซึ่งต้องมีอยู่ใน README.md ตรงตัว (ไม่นับ ** และ `)"""
    if re.sub(r"\*\*|`", "", s) not in README:
        raise KeyError("ไม่พบข้อความ %r ใน README.md" % s)
    return s


def tab2(prefix, head1):
    for b in walk(sec(prefix)):
        if b["t"] == "table" and len(b["head"]) > 1 and E.plain(b["head"][1]).startswith(head1):
            return b
    raise KeyError("ไม่พบตารางที่คอลัมน์ที่สองขึ้นต้นด้วย %r ในหัวข้อ %r" % (head1, prefix))


def row(t, key):
    for r in t["rows"]:
        if E.plain(r[0]).startswith(key):
            return r
    raise KeyError("ไม่พบแถว %r" % key)


def bold(s):
    return s.replace("**", "")


def lead(prefix):
    return next(" ".join(b["lines"]) for b in sec(prefix) if b["t"] == "p")


def took(prefix):
    for b in sec(prefix):
        if b["t"] == "p" and b["lines"][0].startswith("*ใช้เวลา"):
            return re.match(r"\*ใช้เวลา\s*([^·*(]+)", b["lines"][0]).group(1).strip()
    raise KeyError("ไม่พบบรรทัดใช้เวลาในหัวข้อ %r" % prefix)


def img(src, alt):
    return E.img_tag({"t": "img", "src": src, "alt": E.plain(alt)})


def stps(pts):
    return "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(pts))


def mtiles(nums):
    return "".join('<div class="mt %s"><div class="k">%s</div><div class="num">%s</div><div class="s">%s</div></div>'
                   % (tone, md(k), v, md(s)) for k, v, s, tone in nums)


def pic(title, src, pts, tag="", post="", wide=False):
    """ภาพใหญ่ราว 70% ของหน้า + ข้อพูด 2-4 ข้อด้านข้าง"""
    return S(title, '<div class="pic%s"><div class="fig">%s</div><div class="side fitbox">%s%s</div></div>'
             % (" wide" if wide else "", img(src, title), stps(pts), post), tag=tag, maxfs=1.25)


def chart(title, src, nums, cap="", tag="", pts=(), below=False):
    """กราฟจริงขนาดใหญ่ + ตัวเลขผลจริงเป็นกล่องเล็กเรียงด้านข้าง (below=True: เรียงใต้กราฟ สำหรับกราฟแนวกว้าง) + บรรทัดบอกว่าดูตรงไหน"""
    if below:
        body = '<div class="shot"><div class="fig">%s</div><div class="mrow">%s</div></div>' % (img(src, title), mtiles(nums))
    else:
        body = '<div class="pic"><div class="fig">%s</div><div class="side fitbox">%s%s</div></div>' % (img(src, title), mtiles(nums), stps(pts))
    if cap:
        body += '<p class="capl">%s</p>' % md(cap)
    return S(title, body, tag=tag, maxfs=1.25)


def pair(title, left, right, cap="", tag=""):
    """ภาพคู่ซ้าย-ขวา · left/right = (หัวเล็ก, html)"""
    col = lambda x: '<div>%s%s</div>' % ('<div class="ph">%s</div>' % md(x[0]) if x[0] else "", x[1])
    body = '<div class="pair">%s%s</div>' % (col(left), col(right))
    if cap:
        body += '<p class="capl">%s</p>' % md(cap)
    return S(title, body, tag=tag, maxfs=1.2)


def figbox(src, alt):
    return '<div class="fig">%s</div>' % img(src, alt)


def band(sentence, photo, sub="", small=""):
    """ภาพถ่ายเต็มหน้า + ประโยคเดียวบนแถบด้านล่าง"""
    raw = '<div class="bandbox">%s<h1>%s</h1>%s</div><div class="imgnote">ภาพจำลอง</div>' % (
        '<div class="small">%s</div>' % small if small else "", md(sentence), "<p>%s</p>" % md(sub) if sub else "")
    return {"raw": raw, "cls": "band", "style": ' style="background-image:url(%s)"' % photo, "title": E.plain(sentence),
            "kicker": "", "tag": "", "lead": ""}


def shot(k, title, pts, src=None):
    """ส่วนหนึ่งของคำตอบจริง (ตัดจากภาพหน้าจอ แสดงใหญ่) + ข้อ "อ่านผลอย่างไร" แบบย่อ + ลิงก์ภาพเต็ม
    แต่ละภาพตัดเป็นช่วงเดียวต่อเนื่องจากภาพหน้าจอ (ไม่ต่อหลายช่วงเข้าด้วยกัน)"""
    src = src or "img/c%02d-step%d-answer.jpg" % (k, k)
    body = ('<div class="shot"><div class="fig">%s</div><p class="capl">ส่วนหนึ่งของคำตอบจริงในขั้นที่ %d · '
            'ภาพหน้าจอเต็ม: <a href="image/lab5-step%d.png" target="_blank">image/lab5-step%d.png</a></p>'
            '<div class="pts" style="--n:%d">%s</div></div>') % (img(src, title), k, k, k, len(pts), stps(pts))
    return S(title, body, tag="คำตอบจริง", maxfs=1.2)


def prog(k, total):
    return '<div class="prog">%s</div>' % "".join(
        '<span class="%s"></span>' % ("cur" if j == k else "done" if j < k else "") for j in range(1, total + 1))


def step_div(k, result):
    p = "ขั้นที่ %d ·" % k
    head = next(s["text"] for s in SECS if s["text"].startswith(p))
    total = 9 if k <= 9 else 11
    where = "ภาค LAB · ขั้นที่ %d จาก 9" % k if k <= 9 else "ปิดท้าย · ขั้นที่ %d จาก 11" % k
    sub = "%s<p>%s</p><p>เวลาจริง: <b>%s</b> · ผลจริง: %s</p>" % (prog(k, total), md(lead(p)), took(p), md(result))
    return E.divider("ขั้นที่ %d" % k, head.split("·", 1)[1].strip(), sub, small=where)


def prompt_of(k, title):
    return E.prompt_slides(E.prompt_code("ขั้นที่ %d ·" % k), CTX["kicker"], "ขั้นที่ %d · %s" % (k, title))


def timeline():
    steps = [s["text"] for s in SECS if re.match(r"ขั้นที่ \d+ ·", s["text"])]
    out = []
    for h in steps:
        k = int(h.split(" ")[1])
        t = took("ขั้นที่ %d ·" % k)
        m = float(re.search(r"[\d.]+", t).group())
        cls = "loc" if k == 9 else "sk" if k >= 10 else ""
        out.append('<div class="%s" style="flex:%.1f 1 0" title="%s"><b>%d</b>%s</div>' % (cls, m, E.plain(h), k, t.replace("ราว ", "") if m >= 20 else ""))
    return '<div class="tl">%s</div>' % "".join(out)


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    # ===== 1 · เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    add(E.cover("LAB 5 · เทรน VLM บนคลัสเตอร์ 2 เครื่อง (เครื่องละ 2 GPU)",
                "VRAM ไม่พอจะเทรนอย่างไร · เพิ่มเครื่องแล้วเร็วขึ้นกี่เท่า คุ้มเงินไหม",
                "image/lab5-why.png", small="สัปดาห์ที่ 3 · VastAi Application · LAB 5"))
    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("เพิ่มเป็น 2 Node แล้วเร็วขึ้น %s ซึ่งขึ้นกับ Effective Batch มากกว่าแนวทาง" % n("1.14–1.86 เท่า"),
            "results/images/speedup_vs_nodes.png",
            "ดูเส้นทึบ 2 เส้น (Effective Batch 32) ที่อยู่ใกล้เส้นประ **Ideal** และเส้นจุด 2 เส้น (Effective Batch 8) ที่อยู่ต่ำกว่ามาก · "
            "ที่ 3 Node เป็นแถบ **ประมาณการ** จากเวลาที่วัดได้ ไม่ใช่ผลวัด", tag="results/metrics.json"))
    add(fig("บทนี้มี 4 ส่วน ได้แก่ ภาคพื้นฐาน ภาค LAB 9 ขั้น การสร้างสกิลเวอร์ชัน 0 และสรุป", "img/n21-roadmap.jpg",
            "ภาค LAB ทุกขั้นคือ 1 พรอมต์ และโค้ดทุกไฟล์ AI เขียนให้จากพรอมต์ เริ่มจากโฟลเดอร์ว่าง"))
    add(S("วิธีใช้สไลด์ชุดนี้", cards([
        ("เปลี่ยนหน้า", "กด **→** หรือ **Space** ไปหน้าถัดไป · **←** ย้อนกลับ · **O** เปิดสารบัญ · **F** เต็มจอ"),
        ("ภาพ", "คลิกภาพเพื่อขยาย ภาพคำตอบของ AI มีลิงก์ไปยังภาพหน้าจอเต็ม"),
        ("พรอมต์", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** ให้ข้อความตรงกับ README ทุกตัวอักษร แล้ววางในช่องพิมพ์ของ Claude Code"),
        ("ตรวจผลของคุณ", "หลังรันแต่ละขั้น ติ๊กรายการตรวจผล แล้วเทียบกับผลของผู้สอนที่อยู่ใต้รายการ")], 2), cls="mid"))

    # ===== 2 · ภาคพื้นฐาน
    CTX.update(kicker="", group="ภาคพื้นฐาน")
    add(E.divider("ภาคพื้นฐาน", "VRAM ตอนเทรนไปอยู่ที่ไหน และ 2 แนวทางเมื่อ VRAM จำกัด",
                  "<p>ปัญหา · Dataset · โมเดล · ทฤษฎี 6 ข้อที่ใช้อ่านผลของ LAB</p>", "img/s01-theory.jpg"))
    CTX.update(kicker="ภาคพื้นฐาน · ปัญหา", group="ภาคพื้นฐาน · ปัญหา Dataset โมเดล")
    add(fig("LAB 2 เทรนรุ่น 2B บน GPU 24 GB ได้สบาย แต่รุ่น %s ใหญ่กว่าราว 4 เท่า VRAM จึงตึงมาก" % n("8B"), "image/lab5-why.png",
            "คำถามของการทดลอง: **เมื่อ VRAM จำกัด จะเทรนอย่างไร** และ **เพิ่มเครื่อง (Node) แล้วเร็วขึ้นกี่เท่า คุ้มเงินไหม**"))
    t = table("ทำไปเพื่ออะไร", "")
    add(fig("เราวัดจริง 2 แนวทาง แล้วขยายแต่ละแนวทางจาก 1 เครื่องเป็น 2 เครื่อง", "img/n22-two-approaches.jpg",
            "**A** %s ปิด Gradient Checkpointing · **B** %s เปิด Gradient Checkpointing" % (row(t, "ชื่อ")[1], bold(row(t, "ชื่อ")[2]))))

    CTX["kicker"] = "ภาคพื้นฐาน · รู้จัก Dataset"
    ts = table("รู้จัก Dataset", "ชุด")
    add(chart("Dataset CORD-v2 คือรูปถ่ายใบเสร็จจริง แต่ละใบคู่กับเฉลย JSON", "results/dataset_samples.jpg",
              [(r[0], r[1] + " <small>ใบ</small>", "%s รายการ · %s" % (r[2], r[3]), "warn" if r[3] == "ไม่ได้ใช้" else "") for r in ts["rows"]],
              "ใบเสร็จจากร้านอาหาร คาเฟ่ และร้านค้าในอินโดนีเซีย · NAVER CLOVA · CC BY 4.0 · ภาพย่อให้ด้านยาวไม่เกิน 1280 px"))
    add(pair("label 1 รายการ คือคำตอบที่โมเดลต้องเขียนเองเมื่อเห็นรูปใบเสร็จ",
             ("รูปใบเสร็จ train_353", figbox("img/c00-train353-receipt.jpg", "ใบเสร็จ train_353")),
             ("เฉลย JSON ของใบนี้", E.pre_html(codes("รู้จัก Dataset", "json")[0]["text"], "json")),
             "total %s · topping นับเป็นอีกบรรทัด ราคา 0 · ภาพใบเสร็จตัดจาก `results/dataset_samples.jpg`" % n("18999 = 17272 + 1727")))
    add(fig("กติกาของเฉลย: คัดลอกชื่อตามตัวอักษร ตัวเลขเป็นจำนวนเต็ม และค่าที่ใบไม่พิมพ์เป็น null", "img/n23-label-rules.jpg",
            "ตัวอย่างตัวเลขจำนวนเต็ม: %s" % n('"17,272" → 17272')))

    CTX["kicker"] = "ภาคพื้นฐาน · รู้จักโมเดล"
    tm = table("รู้จักโมเดลที่ใช้", "หัวข้อ")
    add(fig("Qwen3-VL-8B ใช้ VRAM %s แต่เทรนเพียง LoRA %s parameter (%s)" % (n("16.34 GiB"), n("3,833,856"), n("0.044%")),
            "image/model-qwen3vl-8b.png",
            "Vision Encoder + ส่วนภาษา 36 Layer · %s parameter · เทรนเฉพาะ `q_proj` กับ `v_proj` เพื่อให้ Gradient ที่ส่งข้ามเครื่องมีขนาดเล็ก (ทฤษฎีข้อ 4) · รุ่น 2B ของ LAB 2 ใช้ VRAM ตอนเทรน %s"
            % (n("8.77 พันล้าน"), n("8.55 GB"))))

    # ----- ทฤษฎี 6 ข้อ
    CTX.update(kicker="ภาคพื้นฐาน · ทฤษฎี 1 · VRAM", group="ภาคพื้นฐาน · ทฤษฎี")
    add(fig("โหลดโมเดลได้ไม่ได้แปลว่าเทรนได้ เพราะน้ำหนักอย่างเดียวใช้ไป %s ของ GPU" % n("69%"), "image/lab5-vram.png",
            "ตอนเทรน GPU เก็บ 3 อย่างพร้อมกัน คือ **น้ำหนักโมเดล** **Activation** ของทุก Layer และ **logits + Gradient + optimizer**"))
    tv = table("1 · VRAM", "สิ่งที่เก็บ")
    add(pic("Gradient Checkpointing เก็บ Activation เป็นจุด ๆ แล้วคำนวณซ้ำตอน Backward", "image/lab5-gradcp.png", [
        "**Activation** %s" % row(tv, "Activation")[2],
        "**เปิด Gradient Checkpointing** ได้ VRAM คืน แลกกับเวลาคำนวณที่เพิ่มขึ้น",
        "**logits + Gradient + optimizer** %s" % row(tv, "logits")[2]]))
    al = next(b for b in sec("1 · VRAM") if b["t"] == "alert")
    al_lines = next(b for b in al["blocks"] if b["t"] == "p")["lines"]
    b = {"t": "img", "src": "results/images/peak_vram.png", "alt": "VRAM สูงสุดต่อ GPU"}
    add(S("ผลวัดขั้นที่ 3: ปิด Gradient Checkpointing ต้องใช้ GPU 2 ใบ ส่วนเปิดแล้วพอ 1 ใบที่ batch 1",
          E.fig_html(b, True) + '<p class="capl">ดูแท่งลายขีดที่ชนเส้น 24 GB ซึ่งคือกรณี Out of Memory</p>' +
          note(" ".join(al_lines[1:]), label=bold(al_lines[0])), tag="results/raw/vram_probe.json", maxfs=1.1))

    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 2 · Model Parallelism เทียบ Data Parallelism"
    tn = tab2("2 · Model", "แนวทาง A")
    ra, ru, rv = row(tn, "ใบเสร็จต่อวินาที"), row(tn, "GPU util"), row(tn, "VRAM")
    add(chart("บนเครื่องเดียวกัน B ได้ %s ใบเสร็จต่อวินาที เร็วกว่า A %s" % (bold(ra[2]).split(" ")[0], n("1.74 เท่า")), "image/lab5-a-vs-b.png", [
        ("แนวทาง A · 1 replica", ra[1] + " <small>ใบ/วินาที</small>", "GPU util %s · VRAM %s" % (ru[1], rv[1]), ""),
        ("แนวทาง B · 2 replica", bold(ra[2]).split(" ")[0] + " <small>ใบ/วินาที</small>", "GPU util %s · VRAM %s" % (ru[2], rv[2]), "ok")],
        "A แก้ปัญหาโมเดลใส่ GPU 1 ใบไม่ลง โดยให้ GPU 2 ใบ **ผลัดกันทำงาน** · B แก้ปัญหาความช้า โดยให้ GPU 2 ใบทำงาน **พร้อมกัน** กับใบเสร็จคนละใบ · "
        "ตัวเลขจาก 1 Node ที่ Effective Batch 8 (ขั้นที่ 4)", tag="ผลขั้นที่ 4"))

    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 3 · Gradient Accumulation"
    te = table("3 · Gradient", "Effective Batch")
    add(pic("Effective Batch เท่ากับจำนวน replica คูณจำนวนใบที่แต่ละ replica สะสม", "image/lab5-accum.png", [
        "ป้อนใบเสร็จทีละ 1 ใบแล้ว **สะสม Gradient** จึงได้ Gradient ที่นิ่งเหมือน batch ใหญ่ แม้ VRAM พอแค่ batch 1",
        "Effective Batch เท่ากันทำให้เทียบ 1 Node กับ 2 Node ได้อย่างยุติธรรม เช่น B ที่ Effective Batch 8 = %s (1 Node) และ %s (2 Node)" % (row(te, "8")[3], row(te, "8")[4]),
        n("เทรนจริง 400 ใบที่ Effective Batch 8 = ปรับน้ำหนัก 50 ครั้ง")]))

    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 4 · ข้ามเครื่อง"
    add(band("เครื่องเช่า 2 เครื่องอยู่คนละที่ ต่างเจ้าของ และไม่มีเครือข่ายภายในร่วมกัน", "img/p22-two-sites.jpg",
             "Node 1 อยู่ที่ %s และ Node 2 อยู่ที่ %s ห่างกัน RTT %s Gradient จึงต้องส่งผ่านอินเทอร์เน็ต" % (n("Quebec (แคนาดา)"), n("Utah (สหรัฐฯ)"), n("55.5 ms")),
             small="ทฤษฎี 4 · ข้ามเครื่อง"))
    add(pic("ข้ามเครื่องใช้ Coordinator เฉลี่ย Gradient แบบ Synchronous ผ่านพอร์ตเดียว", "image/lab5-star.png", [
        "**Coordinator** รับ Gradient จากทุก replica เฉลี่ย แล้วส่งค่าเฉลี่ยกลับ ทุก replica จึงปรับน้ำหนักด้วยค่าเดียวกัน",
        "**Synchronous** คือรอให้ครบทุกตัวก่อนเฉลี่ย จึงต้องรอ replica ที่ **ช้าที่สุด** ทุกครั้ง",
        "replica ทุกตัว **ต่อออกมาหา** พอร์ตเดียวบน Node 1 ซึ่งต่างจาก DDP ของ LAB 4 ที่ใช้ All-reduce ผ่าน PCIe ในเครื่องเดียว"]))
    tw = table("4 · ข้ามเครื่อง", "ค่าที่วัด")
    b = {"t": "img", "src": "image/lab5-lora-size.png", "alt": "ขนาด Gradient"}
    add(S("ส่ง Gradient ข้ามอินเทอร์เน็ตได้เพราะเทรนเฉพาะ LoRA ซึ่งเล็กลงราว %s" % n("2,300 เท่า"),
          E.fig_html(b, True) + note("ขนาด Gradient ที่ส่ง %s · เวลาสื่อสาร 2 Node (A · Effective Batch 8) = %s · %s" % (
              row(tw, "ขนาด")[1], row(tw, "เวลาสื่อสารต่อครั้ง · 2 Node")[1],
              n("เวลาสื่อสารส่วนใหญ่คือ เวลารอ replica ที่ช้ากว่า ไม่ใช่เวลาส่งข้อมูล")), label="ผลวัด"), maxfs=1.1))

    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 5 · Speedup และเงินต่อ Epoch"
    add(fig("ความคุ้มวัดด้วย 3 ค่า คือ Speedup, Efficiency และเงินต่อ Epoch", "img/n24-metrics.jpg",
            "ทุกครั้งที่ปรับน้ำหนักต้องจ่ายค่าส่งและค่ารอราว %s **ไม่ว่าครั้งนั้นจะสะสมกี่ใบ**" % n("1.6–3 วินาที")))
    tc = table("5 · ต้นทุน", "กรณี")
    rc = {r[0]: r for r in tc["rows"]}
    sp = lambda k: "สื่อสาร %s ของเวลา ได้ %s (Efficiency %s)" % (rc[k][2], bold(rc[k][3]), rc[k][4])
    add(pic("Effective Batch ใหญ่ขึ้น ต้นทุนสื่อสารต่อใบจึงเล็กลง และ Speedup เข้าใกล้ 2 เท่า", "image/lab5-eb-comm.png", [
        "**แนวทาง A** ที่ Effective Batch 8 %s · ที่ 32 %s" % (sp("A · Effective Batch 8"), sp("A · Effective Batch 32")),
        "**แนวทาง B** ที่ Effective Batch 8 %s · ที่ 32 %s" % (sp("B · Effective Batch 8"), sp("B · Effective Batch 32")),
        "2 Node ราคา %s ต่อชั่วโมง เท่ากับ %s ของ 1 Node **เงินต่อ Epoch จึงแพงขึ้นทุกกรณี**" % (n("$0.924"), n("2.23 เท่า"))], tag="ผลขั้นที่ 5"))

    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 6 · เลือกแนวทาง"
    td = table("6 · เลือก", "สถานการณ์")
    add(pic("เพิ่ม Node คือการซื้อเวลา ไม่ใช่การประหยัดเงิน", "image/lab5-decide.png", [
        "**เลือก B** เมื่อโมเดลเทรนบน GPU 1 ใบได้ที่ batch 1 เพราะ%s" % md(row(td, "โมเดลเทรนบน")[2]).replace("เร็วกว่า", " เร็วกว่า", 1),
        "**เลือก A** เมื่อโมเดล 1 ชุดเทรนบน 1 ใบไม่ได้ %s" % md(row(td, "โมเดล 1 ชุด")[2]),
        "**เพิ่ม Node** เมื่อใช้ Effective Batch 32 ขึ้นไปได้ (%s) ส่วนที่ Effective Batch 8 %s" % (
            bold(row(td, "อยากเสร็จ")[2]).replace("ได้ ", ""), md(row(td, "Effective Batch เล็ก")[2]))]))

    CTX.update(kicker="ภาคพื้นฐาน · การทดลอง", group="ภาคพื้นฐาน · การทดลอง")
    add(pic("การทดลองมี 2 แนวทาง × 1 และ 2 Node × Effective Batch 8 และ 32", "img/n01-experiment.jpg", [
        n("แต่ละแนวทางวัดที่ Effective Batch 8 และ 32 รวม 8 รอบ"),
        "**ค่าที่ตรึงไว้** %s" % n("learning rate 0.0002 · seed 0 · คิด loss เฉพาะส่วนคำตอบ JSON · ป้อนทีละ 1 ใบ"),
        "**วัดคุณภาพ** %s" % n("เทรนจริง 400 ใบ 1 Epoch ด้วยคลัสเตอร์ 2 Node แล้ววัดบน Test Set 100 ใบ")]))

    # ===== 3 · ภาค LAB
    CTX.update(kicker="", group="ภาค LAB")
    add(E.divider("ภาค LAB", "9 ขั้น ทุกขั้นคือ 1 พรอมต์ เริ่มจากโฟลเดอร์ว่าง",
                  "<p>%s</p>" % md(n("9 ขั้นรวมราว 3 ชั่วโมง · Node 1 เปิด 3 ชม. 00 นาที · Node 2 เปิด 1 ชม. 56 นาที · $2.44")), "img/s02-lab.jpg"))
    CTX.update(kicker="ภาค LAB · แผนที่", group="ภาค LAB · แผนที่และสิ่งที่ต้องมี")
    b = {"t": "img", "src": "image/lab5-overview.png", "alt": "LAB 5 มี 9 ขั้น"}
    add(S("ขั้นที่ 1–8 ทำบนเครื่องเช่า ขั้นที่ 9 ทำบนเครื่องของเรา และขั้นที่ 10–11 สร้างสกิล",
          E.fig_html(b, True) + timeline() +
          '<p class="tlcap">แถบล่างคือเวลาจริงของแต่ละขั้นตามสัดส่วน (นาที) · สีเขียวน้ำทะเล = เครื่องเช่า · สีน้ำเงิน = เครื่องของเรา · สีส้ม = สกิล</p>',
          maxfs=1.1))
    add(fig("ก่อนเริ่มต้องทำ LAB 0 เปิด Claude Code ที่โฟลเดอร์ของบท และรู้ว่าเงินเริ่มเดินเมื่อไร", "img/n25-before-start.jpg",
            "โฟลเดอร์ของบทคือ `02_VastAi_Application` · Node 1 คิดเงินตั้งแต่ขั้นที่ 1 และ Node 2 ตั้งแต่ขั้นที่ 5 จนกว่าจะลบในขั้นที่ 8 · **ต้องทำขั้นที่ 8 ทุกครั้ง** แม้งานระหว่างทางจะล้ม"))

    def lab(k, short, result):
        CTX.update(kicker="ภาค LAB · ขั้นที่ %d · %s" % (k, short) if k <= 9 else "ปิดท้าย · ขั้นที่ %d · %s" % (k, short),
                   group="ขั้นที่ %d · %s" % (k, short))
        add(step_div(k, result))

    # ----- ขั้นที่ 1
    lab(1, "เช่า Node 1", "RTX 3090 2 ใบ · " + n("Quebec (แคนาดา) $0.414/ชม. 12 cores"))
    add(pic("ขั้นที่ 1 เช่า Node 1 ที่เครื่องอื่นในคลัสเตอร์ต่อเข้ามาได้", "img/n02-step1-rent.jpg", [
        "**ค้นหา** เครื่อง RTX 3090 2 ใบในเครื่องเดียว ราคารวมไม่เกิน $0.60 ต่อชั่วโมง เน็ต 500 Mbps ขึ้นไป ตั้งป้าย `vapp-lab5-n1`",
        "**เลือกภูมิภาค** ที่มีเครื่องผ่านเงื่อนไขอย่างน้อย 2 เครื่องที่ public IP คนละตัว เผื่อเช่า Node 2 ในขั้นที่ 5",
        "**เปิดพอร์ต 9000** ให้เครื่องอื่นต่อเข้ามา แล้วรอจนเห็น GPU ครบ ถ้าเกิน 8 นาทีให้ลบแล้วเช่าใหม่"]))
    add(prompt_of(1, "เช่า Node 1"))
    add(E.check_slide("s1", [
        "ได้เครื่อง **RTX 3090 2 ใบ** ในเครื่องเดียว ราคารวมไม่เกิน $0.60 ต่อชั่วโมง ป้าย `vapp-lab5-n1`",
        "ตารางสรุปมีครบ: GPU · VRAM ต่อใบ · ราคา · ที่ตั้ง · CPU cores · ความเร็วเน็ตขาเข้า/ขาออก · ค่ารับส่งข้อมูลต่อ GB",
        "มี **ที่อยู่และพอร์ต** ที่เครื่องอื่นจะใช้ต่อเข้ามา (พอร์ตภายนอกที่จับคู่กับพอร์ต 9000)",
        "AI บอกว่าเครื่อง **ยังเปิดอยู่** (เงินเริ่มเดินตั้งแต่ขั้นนี้)"],
        "ผลของผู้สอน: RTX 3090 2 ใบ VRAM 24 GB ต่อใบ · %s · ใช้เวลา %s (เครื่องแรกเปิดไม่ขึ้น AI ลบแล้วเช่าใหม่เอง)" % (n("$0.414 ต่อชั่วโมง ที่ Quebec แคนาดา 12 cores"), took("ขั้นที่ 1 ·")),
        MAYDIFF, "ขั้นที่ 1 · เช่า Node 1"))
    add(shot(1, "replica ทุกตัวจะต่อเข้ามาที่ที่อยู่และพอร์ตในแถวท้ายของตาราง", [
        "Vast.ai จับคู่พอร์ต 9000 ในเครื่องกับพอร์ตภายนอกอีกเลขหนึ่ง",
        "เครื่องเช่าเปิดไม่ขึ้นเป็นเรื่องปกติ ข้อ 5 ของพรอมต์ทำให้ AI ไม่รอเปล่า",
        "AI เลือกแคนาดาเพราะเป็นประเทศเดียวที่มีเครื่องผ่านเงื่อนไข 2 เครื่องที่ public IP คนละตัว",
        "ตั้งแต่ขั้นนี้เงินเริ่มเดิน ชั่วโมงละ %s" % n("$0.414")]))

    # ----- ขั้นที่ 2
    lab(2, "เตรียมโมเดลและ Dataset", n("Training Set 800 ใบ 2,416 รายการ"))
    add(pic("ขั้นที่ 2 ติดตั้งแพ็กเกจ โหลดโมเดล %s และแปลงเฉลยเป็น JSON" % n("17 GB"), "img/n29-step2.jpg", [
        "**ติดตั้ง** transformers peft datasets accelerate matplotlib แล้วโหลด `Qwen/Qwen3-VL-8B-Instruct`",
        "**เขียน `code/receipt_data.py`** โหลด CORD-v2 แปลงเฉลยเป็น JSON และเก็บข้อความสั่งโมเดลไว้ที่เดียว",
        "**ทำภาพตัวอย่าง** 6 ใบพร้อมเฉลย · `HF_TOKEN` ห้ามแสดงค่าและห้ามทิ้งไว้บนเครื่อง"]))
    add(prompt_of(2, "เตรียม Node 1 โมเดล และ Dataset"))
    add(E.check_slide("s2", [
        "ได้ Training / Validation / Test = **800 / 100 / 100 ใบ**",
        "มีไฟล์ `lab5_cluster_vlm/code/receipt_data.py` ที่เก็บข้อความสั่งโมเดลไว้ที่เดียว",
        "เปิด `results/dataset_samples.jpg` แล้ว JSON เฉลยตรงกับรูปใบเสร็จ",
        "AI ยกเฉลย JSON 1 ใบและอธิบายทีละช่อง · ไม่มี `HF_TOKEN` ค้างบนเครื่องที่เช่า"],
        "ผลของผู้สอน: ใช้เวลา %s · %s · %s" % (took("ขั้นที่ 2 ·"), n("โหลดโมเดล 136 วินาที"), n("แปลงใบเสร็จ 1,000 ใบ 79 วินาที")),
        MAYDIFF, "ขั้นที่ 2 · เตรียมโมเดลและ Dataset"))
    add(shot(2, "ต้องได้ 800 / 100 / 100 ใบ และโมเดลขนาด 17 GB บน disk", [
        "เปิด `results/dataset_samples.jpg` ดูว่า JSON เฉลยตรงกับรูป",
        "ข้อความสั่งโมเดลเก็บไว้ที่เดียวใน `receipt_data.py` ตอนเทรนและตอนวัดผลจึงใช้ชุดเดียวกัน",
        "AI ส่ง `HF_TOKEN` ให้เครื่องเช่าเฉพาะตอนรันงาน แล้วตรวจซ้ำว่าไม่มี token ค้างบนเครื่อง"]))

    # ----- ขั้นที่ 3
    lab(3, "หาขีดจำกัด VRAM", "A ต้องใช้ GPU 2 ใบ · B ได้แค่ batch 1")
    add(pic("ขั้นที่ 3 ลองเทรน 10 step ด้วยใบเสร็จที่หนักที่สุด แยกเป็น 4 กรณี", "img/n30-step3.jpg", [
        "**เขียน `code/vram_probe.py`** โหลดแบบ bfloat16 ใส่ LoRA rank 8 เฉพาะ `q_proj` `v_proj`",
        "**แนวทาง A** ปิด Gradient Checkpointing ลอง GPU 1 ใบ แล้วลอง 2 ใบที่แบ่ง Layer ใบละราวครึ่ง",
        "**แนวทาง B** เปิด Gradient Checkpointing บน GPU 1 ใบ ลอง batch 1 แล้ว batch 2 · ห้ามปรับค่าเพื่อให้ผลออกมาตามที่คาด"]))
    add(prompt_of(3, "หาขีดจำกัด VRAM ของ GPU 24 GB"))
    add(E.check_slide("s3", [
        "ตารางมีครบ 5 กรณี (A 1 ใบ · A 2 ใบ · B batch 1 · B batch 2) พร้อม VRAM สูงสุดต่อใบและวินาทีต่อ step",
        "**A · GPU 1 ใบ** ขึ้น Out of Memory · **A · GPU 2 ใบ** เทรนได้",
        "**B · batch 1** เทรนได้ · **B · batch 2** ขึ้น Out of Memory",
        "มีไฟล์ `results/raw/vram_probe.json` และ AI ตอบว่าน้ำหนักโมเดลใช้ VRAM เท่าไร"],
        "ผลของผู้สอน: น้ำหนักโมเดล %s · A 1 ใบ %s · B batch 1 เทรนได้ที่ %s · ใช้เวลา %s" % (n("16.34 GiB"), n("Out of Memory ที่ 23.00 GiB"), n("20.26 GiB"), took("ขั้นที่ 3 ·")),
        MAYDIFF, "ขั้นที่ 3 · หาขีดจำกัด VRAM"))
    add(tbl("ผลขั้นที่ 3: ปิด Gradient Checkpointing ต้องใช้ 2 ใบ ส่วนเปิดแล้วพอ 1 ใบแต่ได้แค่ batch 1", table("1 · VRAM", "กรณี"),
            post=note("ใบเสร็จ `train_000` · 1,685 token · ผลดิบ `results/raw/vram_probe.json`")))
    add(shot(3, "น้ำหนักโมเดลใช้ 16.34 GiB ก่อนเริ่มเทรน จึงเหลือที่ให้ Activation ราว 7 GiB เท่านั้น", [
        "%s ที่ batch 2 ขอเพิ่มไม่ได้ คือ logits ของใบเสร็จ 2 ใบ (%s)" % (n("1.91 GiB"), n("1,685 token × คลังศัพท์ 151,936 คำ")),
        "AI ลองแบ่ง Layer 18/18 ก่อน พบว่า GPU 1 สูงกว่า %s จึงย้าย 1 Layer เป็น 19/17 และเก็บผลทั้งสองแบบ" % n("1.2 GiB"),
        "PyTorch มองไม่เห็น GPU ในตอนแรกเพราะ driver ของเครื่องกับ image ไม่เข้ากัน AI หาทางแก้เอง"]))

    # ----- ขั้นที่ 4
    t4 = table("ขั้นที่ 4 ·", "แนวทาง")
    lab(4, "วัดความเร็ว 1 Node", "B ได้ %s ใบเสร็จต่อวินาที A ได้ %s (Effective Batch 8)" % (bold(t4["rows"][1][4]), t4["rows"][0][4]))
    add(pic("ขั้นที่ 4 เขียน Coordinator และ worker แล้ววัด 4 รอบบน Node 1 เป็นเส้นฐาน", "img/n31-step4.jpg", [
        "**`code/coordinator.py`** ใช้แค่ CPU เปิดพอร์ต 9000 รับ Gradient ของ LoRA จากทุก replica เฉลี่ยแล้วส่งกลับ",
        "**`code/worker.py`** คือ replica 1 ตัว · A แบ่งโมเดลบน GPU 2 ใบ · B ใช้ GPU 1 ใบและเปิด Gradient Checkpointing",
        "**วัด 4 รอบ** คือ A และ B ที่ Effective Batch 8 และ 32 บันทึกเวลาคำนวณ เวลาสื่อสาร VRAM GPU util และ checksum"]))
    add(prompt_of(4, "เขียนตัวเทรนแบบคลัสเตอร์ แล้ววัด 1 Node"))
    add(E.check_slide("s4", [
        "มี `code/coordinator.py` `code/worker.py` `code/run_node1.sh` และผลดิบ 4 รอบใน `results/raw`",
        "ตาราง 4 รอบมีวินาทีต่อการปรับน้ำหนัก 1 ครั้ง แยก **คำนวณ / สื่อสาร** และใบเสร็จต่อวินาที",
        "**B เร็วกว่า A** บนเครื่องเดียวกัน และ GPU util ของ A ราวครึ่งหนึ่ง",
        "checksum ของ replica ในรอบเดียวกัน **ตรงกัน** · ขนาด Gradient ที่ส่งราว 7.67 MB"],
        "ผลของผู้สอน: A %s · B %s ใบเสร็จต่อวินาที (Effective Batch 8) · ใช้เวลา %s" % (t4["rows"][0][4], bold(t4["rows"][1][4]), took("ขั้นที่ 4 ·")),
        MAYDIFF, "ขั้นที่ 4 · วัดความเร็ว 1 Node"))
    mx = max(float(bold(r[4])) for r in t4["rows"])
    add(S("ผลขั้นที่ 4: B เร็วกว่า A %s บนเครื่องเดียวกัน" % n("ราว 1.7–1.8 เท่า"),
          bars([("แนวทาง %s · Effective Batch %s" % (r[0], r[2]), "%s replica · VRAM %s · GPU util %s · %s วินาทีต่อครั้ง (คำนวณ / สื่อสาร)" % (r[1], r[5], r[6], r[3]),
                 float(bold(r[4])), mx, "**%s** ใบ/วินาที" % bold(r[4])) for r in t4["rows"]]) +
          note("แท่งยาวสุดคือ B ที่ Effective Batch 32 · บน 1 Node เวลาสื่อสารของ A เกือบเป็นศูนย์"),
          tag="ผลขั้นที่ 4", cls="mid"))
    add(shot(4, "บน 1 Node การสะสมมากขึ้นไม่ได้ทำให้เร็วขึ้น ตัวเลขนี้จะเปลี่ยนเมื่อข้ามเครื่อง", [
        "A ใช้ GPU ทีละใบ (util ราว 50%) ส่วน B ใช้เกือบเต็ม แม้ต้องคำนวณซ้ำจาก Gradient Checkpointing",
        "เวลา %s วินาทีของ B คือเวลาที่ replica ซึ่งเสร็จก่อนรออีกตัว เพราะใบเสร็จยาวไม่เท่ากัน" % n("0.36–0.70"),
        "AI ตีความว่าวัด 20 ครั้งแล้วเฉลี่ยครั้งที่ 4–20 และบอกไว้ในคำตอบ ถ้าต้องการแบบอื่นให้เขียนในพรอมต์ให้ชัด"]))

    # ----- ขั้นที่ 5
    t5 = table("ขั้นที่ 5 ·", "แนวทาง")
    lab(5, "เช่า Node 2 วัด 2 Node", "Speedup %s" % " · ".join("%s-%s %s" % (r[0], r[1], bold(r[5])) for r in t5["rows"]))
    add(pic("ขั้นที่ 5 เพิ่ม Node 2 เข้าคลัสเตอร์ แล้ววัด 4 รอบเดิมด้วยโค้ดเดิม", "img/n32-step5.jpg", [
        "**เช่า Node 2** RTX 3090 2 ใบ ป้าย `vapp-lab5-n2` ใกล้ Node 1 ที่สุด แต่ **public IP ต้องคนละตัว**",
        "**เตรียมให้เหมือน Node 1** แล้วทดสอบการต่อเข้าพอร์ตของโปรแกรมกลางและวัด RTT",
        "**วัด 4 รอบ** ที่ Effective Batch เท่าเดิม A มี 2 replica และ B มี 4 replica แต่ละ replica จึงสะสมน้อยลงครึ่งหนึ่ง"]))
    add(prompt_of(5, "เช่า Node 2 แล้ววัดคลัสเตอร์ 2 Node"))
    add(E.check_slide("s5", [
        "Node 2 ป้าย `vapp-lab5-n2` ต่อเข้าพอร์ตของโปรแกรมกลางบน Node 1 ได้ และ AI บอก RTT",
        "ตารางเทียบ 1 Node กับ 2 Node ครบ 4 รอบ พร้อม **Speedup** และ **Efficiency**",
        "เวลาคำนวณบน 2 Node ลดลงราวครึ่งหนึ่ง แต่มีเวลาสื่อสารเพิ่มขึ้น",
        "checksum ของทุก replica ทั้งสอง Node ตรงกัน · ผลดิบอยู่ใน `results/raw` · เครื่องยังเปิดอยู่ทั้ง 2 เครื่อง"],
        "ผลของผู้สอน: Node 2 ที่ Utah %s · RTT %s · Speedup %s · ใช้เวลา %s" % (
            n("$0.510"), n("55.5 ms"), " / ".join(bold(r[5]) for r in t5["rows"]), took("ขั้นที่ 5 ·")),
        MAYDIFF + " · ถ้าตัวเลขแปลก ให้ดูเวลารายครั้งแล้ววัดซ้ำ", "ขั้นที่ 5 · เช่า Node 2 วัด 2 Node"))
    add(S("ผลขั้นที่ 5: เพิ่มเป็น 2 Node ได้ %s ที่ Effective Batch 8 แต่ได้ %s ที่ 32" % (n("1.14–1.26 เท่า"), n("1.80–1.86 เท่า")),
          bars([("แนวทาง %s · Effective Batch %s" % (r[0], r[1]), "1 Node %s → 2 Node %s วินาทีต่อครั้ง" % (r[2], r[3]),
                 float(bold(r[5]).rstrip("×")), 2, "**%s** · %s" % (bold(r[5]), r[6])) for r in t5["rows"]]) +
          note("แท่งเต็มคือ Ideal 2 เท่า · ตัวเลขในวงเล็บคือเวลาคำนวณ / เวลาสื่อสาร"), tag="ผลขั้นที่ 5", cls="mid"))
    add(fig("เวลาคำนวณลดลงครึ่งหนึ่ง แต่เวลาสื่อสารเพิ่มเป็น 2–3 วินาทีต่อครั้ง", "results/images/time_per_update.png",
            "ดูส่วนสีแดง (สื่อสาร) บนแท่ง 2 Node ทุกคู่ ซึ่งมีขนาดใกล้กันไม่ว่าจะสะสมกี่ใบ · สีเขียว = คำนวณ"))
    b = {"t": "img", "src": "results/images/network_stall.png", "alt": "เครือข่ายสะดุด"}
    add(S("เครือข่ายระหว่างเครื่องเช่าไม่นิ่ง รอบ B ที่ Effective Batch 32 จึงต้องวัดใหม่",
          E.fig_html(b, True) + '<p class="capl">เส้นสีแดงคือครั้งแรกที่เน็ตสะดุดในครั้งที่ 3–4 · เส้นสีน้ำเงินคือครั้งที่วัดใหม่ ซึ่งตารางใช้</p>' +
          note(" ".join(para("ขั้นที่ 5 ·", "**บทเรียนเรื่องเครือข่าย**")["lines"]).replace("**บทเรียนเรื่องเครือข่าย** ", ""), label="บทเรียนเรื่องเครือข่าย"),
          maxfs=1.1))
    add(shot(5, "เวลาที่เพิ่มขึ้นบน 2 Node ส่วนใหญ่คือการรอ replica ที่ช้ากว่า", [
        "เวลาคำนวณลดลงครึ่งหนึ่ง (เช่น A: %s วินาที) แต่เวลาสื่อสารเพิ่มจาก 0.04 เป็น 2–3 วินาทีต่อครั้ง" % n("9.14 → 4.28"),
        "Node 2 คำนวณเร็วกว่า Node 1 ราว 20% replica บน Node 2 จึงเสร็จก่อนแล้วรอ และเวลารอนี้ถูกนับเป็นเวลาสื่อสาร",
        "เครื่องที่สองในแคนาดาใช้ IP เดียวกับ Node 1 AI จึงไปเช่าที่ Utah แทน · ตั้งแต่ขั้นนี้จ่าย %s" % n("$0.924 ต่อชั่วโมง")]))

    # ----- ขั้นที่ 6
    t6 = table("ขั้นที่ 6 ·", "")
    r6 = row(t6, "เวลาเทรน")
    lab(6, "เทรนจริง A และ B", "A %s · B %s · checksum ตรงกันทุก replica" % (r6[1], bold(r6[2])))
    add(pic("ขั้นที่ 6 เทรนจริง 400 ใบทีละแนวทางบนคลัสเตอร์ 2 Node", "img/n03-step6-train.jpg", [
        "**รอบแรก แนวทาง A** มี 2 replica (Node ละ 1 ตัว โมเดลแบ่งบน GPU 2 ใบ) สะสมตัวละ 4 ใบ",
        "**รอบสอง แนวทาง B** มี 4 replica (GPU ละ 1 ตัว) สะสมตัวละ 2 ใบ เริ่มจากโมเดลตั้งต้นใหม่",
        "ทั้งสองรอบปรับน้ำหนัก **50 ครั้ง** แล้ว **ตรวจ checksum** และเก็บ adapter ไว้ที่ `results/adapter_A` และ `results/adapter_B`"]))
    add(prompt_of(6, "เทรนจริงด้วยคลัสเตอร์ 2 Node ทั้งสองแนวทาง"))
    add(E.check_slide("s6", [
        "เทรนครบ 2 รอบ (A แล้ว B) รอบละ 50 ครั้งของการปรับน้ำหนัก",
        "loss ช่วงท้ายต่ำกว่าช่วงต้นทั้งสองแนวทาง",
        "checksum ของน้ำหนัก LoRA **ตรงกันทุก replica** ในแต่ละรอบ",
        "มีโฟลเดอร์ `results/adapter_A` และ `results/adapter_B` พร้อม loss ทุกครั้งและเวลาที่ใช้"],
        "ผลของผู้สอน: เวลาเทรน 400 ใบ A %s · B %s · loss %s (A) · adapter %s · ใช้เวลา %s" % (
            r6[1], bold(r6[2]), row(t6, "loss")[1], row(t6, "ขนาด")[1], took("ขั้นที่ 6 ·")),
        MAYDIFF, "ขั้นที่ 6 · เทรนจริง A และ B"))
    add(chart("ผลขั้นที่ 6: B เสร็จเร็วกว่า A %s และเส้น loss ของทั้งสองแนวทางทับกัน" % n("22%"), "results/images/loss_curve.png", [
        ("เวลาเทรน 400 ใบ · A", r6[1].replace(" วินาที", "") + " <small>วินาที</small>", "replica %s" % row(t6, "replica")[1], ""),
        ("เวลาเทรน 400 ใบ · B", bold(r6[2]).replace(" วินาที", "") + " <small>วินาที</small>", "replica %s" % row(t6, "replica")[2], "ok"),
        ("loss · A", row(t6, "loss")[1], "เฉลี่ย 10 ครั้งแรก → 10 ครั้งสุดท้าย", ""),
        ("loss · B", row(t6, "loss")[2], "เฉลี่ย 10 ครั้งแรก → 10 ครั้งสุดท้าย", "")],
        "เส้นทับกันเพราะแต่ละครั้งใช้ใบเสร็จ 8 ใบชุดเดียวกัน ต่างกันแค่วิธีแบ่งงาน · VRAM สูงสุดต่อใบ A %s · B %s · checksum ตรงกันทุก replica ทั้งสองรอบ"
        % (row(t6, "VRAM")[1], row(t6, "VRAM")[2]), tag="ผลขั้นที่ 6"))
    add(shot(6, "checksum ตรงกันทุก replica จึงเก็บ adapter จากตัวไหนก็ได้ 1 ชุด", [
        "วิธีแบ่งงานไม่เปลี่ยนสิ่งที่โมเดลเรียน loss ของ A และ B จึงลดลงเท่ากัน",
        "ระหว่างรอบ B เน็ตสะดุด 1 ครั้ง (%s) การเทรนเดินต่อจนจบ" % n("ครั้งที่ 21 ใช้ 16.6 วินาที"),
        "การดึงไฟล์ %s กลับจาก Node 1 หลุดซ้ำ ๆ AI จึงส่งจาก Node 1 ไป Node 2 แล้วดึงจาก Node 2" % n("30 MB")]))

    # ----- ขั้นที่ 7
    t7 = table("ขั้นที่ 7 ·", "")
    j7, s7, f7 = row(t7, "JSON"), row(t7, "ยอดรวม"), row(t7, "Item F1")
    lab(7, "Evaluation บน Test Set", "Item F1 %s → %s / %s · ยอดรวมตรง %s → %s" % (f7[1], bold(f7[2]), bold(f7[3]), bold(s7[1]), s7[2]))
    add(pic("ขั้นที่ 7 วัดผล 3 โมเดลบน Test Set 100 ใบ", "img/n04-step7-eval.jpg", [
        "**วัด 3 โมเดล** คือ Base · Fine-tuned A · Fine-tuned B (Base + adapter ของแต่ละแนวทาง)",
        "**อ่าน Test Set ทั้ง 100 ใบ** ด้วยข้อความสั่งเดียวกับตอนเทรน ตอบแบบไม่สุ่ม และแบ่งงานไป GPU ทั้ง 4 ใบ",
        "**ให้คะแนน** JSON อ่านได้ · ยอดรวมตรงทุกหลัก · Item F1 (ชื่อและราคาตรงเฉลย) · วินาทีต่อใบ"]))
    add(prompt_of(7, "Evaluation: Base เทียบ Fine-tuned บน Test Set"))
    add(E.check_slide("s7", [
        "วัดครบ 3 โมเดล (Base · Fine-tuned A · Fine-tuned B) บน Test Set ทั้ง 100 ใบ",
        "ตารางมี JSON อ่านได้ · ยอดรวมตรง · Item F1 · วินาทีต่อใบ และแถวเทียบรุ่น 2B ของ LAB 2",
        "มีคำตอบรายใบ ตัวเลขสรุป กราฟแท่ง และภาพตัวอย่าง 4 ใบใน `results/eval`",
        "AI ยกตัวอย่าง 2 ใบที่ Fine-tuned อ่านถูกแต่ Base อ่านผิด"],
        "ผลของผู้สอน: Item F1 %s → %s (A) / %s (B) · ยอดรวมตรง %s → %s · ใช้เวลา %s" % (
            f7[1], bold(f7[2]), bold(f7[3]), bold(s7[1]), s7[2], took("ขั้นที่ 7 ·")),
        MAYDIFF, "ขั้นที่ 7 · Evaluation บน Test Set"))
    add(chart("ผลขั้นที่ 7: Item F1 ขึ้นราว 10 จุด แต่ยอดรวมตรงลดลง %s" % n("2.1 จุด"), "results/eval/images/accuracy_3models.png", [
        ("Item F1 · Base", f7[1] + " <small>%</small>", "", ""),
        ("Item F1 · Fine-tuned A / B", "%s / %s" % (bold(f7[2]), bold(f7[3])) + " <small>%</small>", "", "ok"),
        ("ยอดรวมตรง · Base", bold(s7[1]) + " <small>%</small>", "", ""),
        ("ยอดรวมตรง · Fine-tuned A / B", "%s / %s" % (s7[2], s7[3]) + " <small>%</small>", "ลดลงหลัง Fine-tune", "bad")],
        "เทียบแท่งกลุ่มกลาง (Total exact) ที่สีน้ำเงินและสีส้มต่ำกว่าสีเทา กับกลุ่มขวา (Item F1) ที่สูงกว่า · JSON อ่านได้ %s / %s / %s · A กับ B ได้คุณภาพแทบเท่ากัน"
        % (j7[1], j7[2], j7[3]), tag="results/eval/metrics.json", below=True))
    # 2 ภาพแยกกัน แต่ละภาพตัดเป็นช่วงเดียวต่อเนื่องจาก results/eval/images/examples.jpg (ใบ test_035 และ test_091)
    b1 = {"t": "img", "src": "img/c07-examples.jpg", "alt": "ตัวอย่างคำตอบ test_035: เฉลย Base และ Fine-tuned A"}
    b2 = {"t": "img", "src": "img/c07b-examples.jpg", "alt": "ตัวอย่างคำตอบ test_091: เฉลย Base และ Fine-tuned A"}
    add(S("ตัวอย่างจริง: Base ใส่จำนวนไว้หน้าชื่อสินค้า และบางใบเติม tax กับ total เอง",
          '<div style="display:flex;flex-direction:column;gap:.5em">%s%s</div>' % (E.fig_html(b1, True), E.fig_html(b2, True))
          + '<p class="capl">คอลัมน์: เฉลย · Base · Fine-tuned A · บน: %s · ล่าง: %s ส่วนเฉลยคือ 21000 · สีแดง = ผิด (Fine-tuned A ยังสะกดชื่อสินค้าผิด 1 รายการ) · '
          'ภาพเต็ม 4 ใบ: <a href="results/eval/images/examples.jpg" target="_blank">results/eval/images/examples.jpg</a></p>'
          % (n("test_035 Base ใส่จำนวนหน้าชื่อสินค้าทุกบรรทัดจึงถูก 0 จาก 4 ส่วน Fine-tuned ถูกครบ 4"), n("test_091 Base เติม tax 3000 และ total 24000 เอง")),
          maxfs=1.1))
    tl = tab2("ขั้นที่ 7 ·", "LAB 5")
    add(shot(7, "ต้องดูทีละตัววัด เพราะ Fine-tuning ไม่ได้ทำให้ดีขึ้นทุกตัววัดเสมอ", [
        "ยอดรวมตรงลดลงเพราะ 2 ใบตอบ total เป็น `null` ทั้งที่ใบพิมพ์ไว้ และ 1 ใบตอบ `\"price\":0000` ทำให้ JSON อ่านไม่ได้",
        "A กับ B ได้คุณภาพแทบเท่ากัน ตรงกับ loss ที่ทับกันในขั้นที่ 6",
        "เทียบกับ LAB 2 ไม่ได้ตรง ๆ เพราะ LAB 5 เทรน %s เฉพาะ %s ส่วน LAB 2 เทรน %s ทุก Linear และวัดเวลาด้วย %s" % (
            md(row(tl, "ข้อมูล")[1]), md(row(tl, "LoRA")[1]).replace("เฉพาะ ", ""), md(row(tl, "ข้อมูล")[2]), row(tl, "วิธีวัด")[2])]))

    # ----- ขั้นที่ 8
    t8 = table("ขั้นที่ 8 ·", "เครื่อง")
    lab(8, "ลบทุกเครื่อง", "ลบครบ 2 เครื่อง ไม่มีเครื่องค้าง · ยอดรวมทั้ง LAB %s" % bold(row(t8, "รวม")[7]))
    add(pic("ขั้นที่ 8 ตรวจผลให้ครบ ลบทุกเครื่อง แล้วอ่านยอดที่ถูกคิดเงินจริง", "img/n05-step8-delete.jpg", [
        "**ตรวจผลใน `results`** ให้ครบก่อนลบ ได้แก่ ผลดิบขั้นที่ 3–5 · adapter A และ B · ผล Evaluation",
        "**บันทึก `results/raw/nodes.json`** (GPU ที่ตั้ง ราคา อายุเครื่อง ยอดที่ถูกคิด) โดยไม่ใส่ IP และเลขเครื่อง",
        "**ลบทุกเครื่องที่ป้ายขึ้นต้นด้วย `vapp-lab5-n`** แล้วตรวจว่าไม่มีเครื่องค้าง โดยไม่แตะเครื่องป้ายอื่น"]))
    add(prompt_of(8, "ลบทุกเครื่องและสรุปค่าใช้จ่าย"))
    add(E.check_slide("s8", [
        "AI ตรวจว่าผลกลับมาครบใน `results` ก่อนลบ (ผลดิบขั้นที่ 3–5 · adapter A และ B · ผล Evaluation)",
        "มีไฟล์ `results/raw/nodes.json` ที่ **ไม่มี** IP และเลขเครื่อง",
        "**ไม่มีเครื่องป้าย `vapp-lab5-n` เหลือ** แล้วเปิดหน้า Instances ของ Vast.ai ดูอีกครั้ง",
        "ตารางค่าใช้จ่ายจริงแยกเครื่อง: อายุเครื่อง · ราคาต่อชั่วโมง · GPU · disk · รับส่งข้อมูล · ยอดรวม"],
        "ผลของผู้สอน: Node 1 %s · Node 2 %s · รวม %s · ใช้เวลา %s" % (
            bold(row(t8, "Node 1")[7]), bold(row(t8, "Node 2")[7]), bold(row(t8, "รวม")[7]), took("ขั้นที่ 8 ·")),
        "ยอดของคุณขึ้นกับเวลาที่เครื่องเปิดจริงและราคาของเครื่องที่ได้", "ขั้นที่ 8 · ลบทุกเครื่อง"))
    add(S("ผลขั้นที่ 8: ค่าเช่าทั้ง LAB %s" % bold(row(t8, "รวม")[7]), tiles([
        ("Node 1 · %s" % row(t8, "Node 1")[1], bold(row(t8, "Node 1")[7]), "เปิด %s · %s/ชม." % (row(t8, "Node 1")[2], row(t8, "Node 1")[3]), ""),
        ("Node 2 · %s" % row(t8, "Node 2")[1], bold(row(t8, "Node 2")[7]), "เปิด %s · รับส่งข้อมูล %s" % (row(t8, "Node 2")[2], row(t8, "Node 2")[6]), ""),
        ("เครื่องแรกที่เปิดไม่ขึ้น", row(t8, "Node 1 เครื่องแรก")[7], "ค่า disk", "warn"),
        ("รวมทั้ง LAB", bold(row(t8, "รวม")[7]), "ยอดที่ถูกคิดจริง", "ok")]), tag="results/raw/nodes.json", cls="mid"))
    add(band("เทรนจริงรวม%s แต่ Node 1 เปิด 3 ชั่วโมง" % n("ราว 13 นาที"), "img/p23-meter.jpg",
             "**เงินเดินตลอดเวลาที่เครื่องเปิด** รวมช่วงที่ AI เขียนโค้ดและช่วงที่เครือข่ายมีปัญหา จึงต้องลบเครื่องทันทีเมื่อเก็บผลครบ",
             small="ขั้นที่ 8 · สิ่งที่ต้องจำ"))
    add(shot(8, "ต้องเห็นว่าไม่มีเครื่องป้าย vapp-lab5-n เหลือ แล้วเปิดหน้า Instances ตรวจอีกครั้ง", [
        "เครื่องที่เปิดไม่ขึ้นก็ถูกคิดค่า disk (%s)" % n("$0.008"),
        "Node 2 จ่ายค่ารับส่งข้อมูล %s ส่วนใหญ่คือการโหลดโมเดล 17 GB ส่วน Node 1 ไม่ถูกคิด" % n("$0.237"),
        "ยอดในตารางอ่านจากรายการคิดเงินของ Vast.ai หลังลบเครื่อง"]))

    # ----- ขั้นที่ 9
    t9 = table("ขั้นที่ 9 ·", "แนวทาง")
    lab(9, "สรุปผลและเงินต่อ Epoch", "ถูกที่สุด B · 1 Node · Effective Batch 32 (%s) · เร็วที่สุด B · 2 Node (%s)" % (n("$0.058"), n("4.6 นาทีต่อ Epoch")))
    add(fig("ขั้นที่ 9 ไม่ใช้เครื่องเช่า report.py อ่านผลดิบทั้งหมด แล้วคำนวณทุกตัวเลขในที่เดียว", "img/n26-report.jpg",
            "เงินต่อ Epoch = เวลาที่ใช้กับ Training Set 800 ใบ × ราคาต่อชั่วโมงรวมทุก Node ที่ใช้ · ประมาณการ 3 Node ต้องบอกชัดว่าไม่ใช่ผลวัด"))
    add(prompt_of(9, "สรุปตาราง กราฟ และเงินต่อ Epoch"))
    add(E.check_slide("s9", [
        "มีไฟล์ `code/report.py` และ `results/metrics.json` ที่มีทุกตัวเลข (VRAM · Gradient · RTT · Evaluation · checksum)",
        "มีกราฟ 4 รูปใน `results/images`: Speedup พร้อมเส้น Ideal · เวลาต่อการปรับน้ำหนัก · VRAM สูงสุด · เงินต่อ Epoch",
        "ตารางสรุป 8 กรณี (A/B × 1/2 Node × Effective Batch 8/32)",
        "ประมาณการ 3 Node ระบุว่า **คำนวณจากเวลาที่วัดได้ ไม่ใช่ผลวัด** และ AI ตอบครบ 4 คำถาม"],
        "ผลของผู้สอน: Speedup %s · เงินต่อ Epoch %s ถึง %s · ใช้เวลา %s" % (
            n("1.26 1.86 1.14 และ 1.80 เท่า"), n("$0.058"), n("$0.187"), took("ขั้นที่ 9 ·")),
        MAYDIFF, "ขั้นที่ 9 · สรุปผลและเงินต่อ Epoch"))
    add(fig("เงินต่อ Epoch แพงขึ้นทุกกรณีเมื่อเพิ่ม Node", "results/images/cost_per_epoch.png",
            "เทียบแท่งสีอ่อน (1 Node %s ต่อชั่วโมง) กับแท่งสีเข้มที่อยู่ข้างกัน (2 Node %s ต่อชั่วโมง) · ถูกที่สุดคือ B · 1 Node · Effective Batch 32"
            % (n("$0.414"), n("$0.924"))))
    t3n = table("ขั้นที่ 9 ·", "กรณี")
    add(chart("ประมาณการ 3 Node (ไม่ใช่ผลวัด): Effective Batch 8 แทบไม่เร็วขึ้น และ B อาจช้าลง", "results/images/speedup_vs_nodes.png",
              [(r[0] + " · %s replica" % r[1], md(r[2]).replace(" (อาจช้าลง)", ""), "Efficiency %s%s" % (r[3], " · อาจช้าลง" if "ช้าลง" in r[2] else ""),
                "bad" if "ช้าลง" in r[2] else "") for r in t3n["rows"]],
              "ดูแถบแนวตั้งที่ 3 Node · " + " ".join(para("ขั้นที่ 9 ·", "**ประมาณการ 3 Node**")["lines"]).replace("**ประมาณการ 3 Node** ", ""),
              tag="ประมาณการ"))
    add(shot(9, "เพิ่ม Node คือการซื้อเวลา ไม่ใช่การประหยัดเงิน", [
        "กรณีที่ดีที่สุดจ่ายเพิ่ม 22%% (%s) เพื่อให้เสร็จเร็วขึ้น 1.80 เท่า" % n("$0.058 → $0.071"),
        "เร็วที่สุดคือ B · 2 Node · Effective Batch 32 (%s)" % n("4.6 นาทีต่อ Epoch ที่ $0.071"),
        "A แพงกว่า B ต่อ Epoch ราว 1.7–1.8 เท่าบน 1 Node (%s) เพราะ GPU ว่างครึ่งหนึ่งแต่จ่ายค่าเครื่องเท่าเดิม" % n("$0.103–0.106 เทียบ $0.058–0.061")]))

    # ===== ปิดท้าย · สกิล v0
    CTX.update(kicker="ปิดท้าย · สกิลเวอร์ชัน 0", group="ปิดท้าย · สกิล v0")
    add(E.divider("ปิดท้าย", "เก็บงานทั้ง LAB เป็นสกิลเวอร์ชัน 0", "<p>ทำซ้ำได้ในคำสั่งเดียว แทนการวาง 9 พรอมต์ใหม่</p>"))
    add(fig("สกิลเก็บวิธีทำงานที่สำเร็จแล้วพร้อมโค้ด ให้ AI ทำซ้ำได้ในคำสั่งเดียว", "image/skill-v0.png",
            "ถ้าต้องทำซ้ำ เช่น เปลี่ยนจำนวน Node แนวทาง หรือ Effective Batch ไม่ควรต้องวาง 9 พรอมต์ใหม่"))

    lab(10, "สร้างสกิล v0", "สกิล `cluster-vlm-train` พร้อมโค้ด 14 ไฟล์ใน `skill_v0/scripts`")
    add(pic("ขั้นที่ 10 AI อ่านพรอมต์ โค้ด และผลของ LAB แล้วเขียน SKILL.md", "img/n33-step10.jpg", [
        "**ดูงานทั้งหมด** จาก `PROMPTS.md` โค้ดใน `code` และผลใน `results`",
        "**เขียน `skill_v0/SKILL.md`** ชื่อ `cluster-vlm-train` มีค่าที่ปรับได้พร้อมค่าเริ่มต้น ขั้นตอน เกณฑ์ตรวจผ่าน และกติกาเรื่องเงิน",
        "**คัดลอกโค้ดที่ใช้ได้แล้ว** ไปไว้ใน `skill_v0/scripts` แล้วติดตั้งเป็นสกิลของโปรเจกต์ที่ `.claude/skills/cluster-vlm-train`"]))
    add(prompt_of(10, "ให้ AI สร้างสกิล v0"))
    add(E.check_slide("s10", [
        "มีไฟล์ `lab5_cluster_vlm/skill_v0/SKILL.md` ที่มี name และ description",
        "SKILL.md มีค่าที่ปรับได้ครบ: รุ่น GPU · จำนวน Node · เพดานราคา · แนวทาง · Effective Batch · จำนวนใบ · ป้ายเครื่อง · โฟลเดอร์ผล",
        "มีโค้ดใน `skill_v0/scripts` และสกิลถูกติดตั้งที่ `.claude/skills/cluster-vlm-train`",
        "ปิดแล้วเปิด Claude Code ใหม่ 1 ครั้ง สกิลที่เพิ่งติดตั้งจึงจะถูกมองเห็น"],
        "ผลของผู้สอน: ใช้เวลา %s · ไม่ต้องเช่าเครื่อง · AI แก้สคริปต์ %s ให้รับค่าที่ปรับได้" % (took("ขั้นที่ 10 ·"), n("8 จาก 14 ไฟล์")),
        "SKILL.md ของคุณไม่ต้องเหมือนของผู้สอนทุกบรรทัด สิ่งที่ต้องมีคือค่าที่ปรับได้ ขั้นตอน เกณฑ์ตรวจผ่าน และกติกาเรื่องเงิน",
        "ขั้นที่ 10 · สร้างสกิล v0"))
    add(shot(10, "ส่วนที่ AI บอกว่ายังไม่ได้ทดสอบกับเครื่องจริงคือจุดที่ต้องระวัง", [
        "AI แก้สคริปต์ %s ให้รับค่าที่ปรับได้ และบอกตรง ๆ ว่าส่วนไหนยังไม่ได้ทดสอบ" % n("8 จาก 14 ไฟล์"),
        "ขั้นที่ 11 จะใช้สกิลกับเครื่องจริง ส่วนที่ยังไม่ได้ทดสอบจึงอาจพลาดได้",
        "หลังขั้นนี้ให้ปิดแล้วเปิด Claude Code ใหม่ 1 ครั้ง สกิลที่เพิ่งติดตั้งจึงจะถูกมองเห็น"]))

    t11 = table("ขั้นที่ 11 ·", "")
    sp11 = row(t11, "Speedup")
    lab(11, "ลองใช้สกิลทำซ้ำ", "แนวทาง B Speedup %s · ค่าเช่า %s" % (sp11[2].split(" / ")[0], row(t11, "ค่าเช่า")[2]))
    add(pic("ขั้นที่ 11 ใช้สกิล cluster-vlm-train ทำงานแบบย่อซ้ำใน 1 พรอมต์", "img/n06-step11-skill.jpg", [
        "**เช่า RTX 3090 2 ใบ 2 เครื่อง** ป้าย `vapp-lab5-skill-n1` และ `vapp-lab5-skill-n2`",
        "**วัดความเร็ว** 1 Node เทียบ 2 Node ที่ Effective Batch 32 แล้ว **เทรนจริง 200 ใบ** และวัดผลบน Test Set",
        "**ลบทุกเครื่อง** แล้วเก็บผลไว้ที่ `results/skill_v0_run` โดยไม่เขียนทับผลเดิม"]))
    add(prompt_of(11, "ลองใช้สกิลทำซ้ำในคำสั่งเดียว"))
    add(E.check_slide("s11", [
        "AI ใช้สกิล `cluster-vlm-train` และเช่าเครื่องป้าย `vapp-lab5-skill-n1` และ `vapp-lab5-skill-n2`",
        "ได้ Speedup ของ 2 Node ที่ Effective Batch 32 และเวลาแต่ละขั้น",
        "ได้ยอดรวมตรงและ Item F1 ก่อน vs หลัง บน Test Set",
        "ผลอยู่ที่ `results/skill_v0_run` ไม่ทับผลเดิม · **ลบทุกเครื่องแล้ว** และรายงานค่าใช้จ่ายจริง"],
        "ผลของผู้สอน: Speedup %s · Item F1 %s · ยอดสุดท้ายในใบแจ้งหนี้ %s" % (sp11[2], row(t11, "Test Set: Item F1")[2], n("$0.87")),
        "Speedup ของคลัสเตอร์ขึ้นกับคู่เครื่องที่ได้ ตัวเลขของคุณจึงต่างได้มาก · ข้อสรุปที่ทำซ้ำได้คือทิศทาง", "ขั้นที่ 11 · ลองใช้สกิลทำซ้ำ"))
    add(S("ผลขั้นที่ 11: 1 พรอมต์ทำงานแทน 9 พรอมต์ แต่ Speedup ต่างไปตามคู่เครื่อง", tiles([
        ("จำนวนพรอมต์", "%s → %s" % (row(t11, "จำนวนพรอมต์")[1], bold(row(t11, "จำนวนพรอมต์")[2])), "สั่งทีละขั้น → สกิล v0", "ok"),
        ("Speedup", sp11[2].split(" / ")[0], "Efficiency %s · สั่งทีละขั้นได้ %s" % (sp11[2].split(" / ")[1], sp11[1]), "warn"),
        ("เวลา", row(t11, "เวลา")[2], "สั่งทีละขั้น %s" % row(t11, "เวลา")[1], ""),
        ("ค่าเช่า", row(t11, "ค่าเช่า")[2], "สั่งทีละขั้น %s" % row(t11, "ค่าเช่า")[1], "")]) +
        note("รอบสกิลเป็นแบบย่อ (แนวทาง B · เทรน 200 ใบ) · เครื่อง %s" % row(t11, "เครื่อง")[2]), tag="results/skill_v0_run", cls="mid"))
    tv1 = table("ขั้นที่ 11 ·", "จุดที่ v0")
    if not os.path.exists("img/n27-v0-bug.jpg"):      # ภาพยังไม่ผ่านการตรวจ: ใช้การ์ดจากตารางของ README แทน
        add(S("v0 ยังไม่สมบูรณ์: บั๊กใน run_train.sh ทำให้ worker ต่อผิดที่และการเทรนค้าง",
              cards([("v0 พลาด", tv1["rows"][0][0], "bad"), ("ควรแก้ใน v1", tv1["rows"][0][1], "ok")], 2), tag="จุดที่ v0 ยังพลาด 1/2", cls="mid"))
    else:
     add(fig("v0 ยังไม่สมบูรณ์: บั๊กใน run_train.sh ทำให้ worker ต่อผิดที่และการเทรนค้าง", "img/n27-v0-bug.jpg",
            "AI แก้เฉพาะสำเนาที่ใช้รัน ไฟล์ใน `skill_v0/` ยังเป็นฉบับเดิม · v1 ควรใช้สคริปต์ที่แก้แล้วจาก "
            "[results/skill_v0_run/raw/scripts_patched/](results/skill_v0_run/raw/scripts_patched/run_train.sh) และรันกับคลัสเตอร์จริงก่อนถือว่าใช้ได้",
            tag="จุดที่ v0 ยังพลาด 1/2"))
    add(S("จุดที่ v0 ยังพลาดอีก 4 ข้อ แก้ด้วยพรอมต์อีก 1 อันแล้วลองใช้ซ้ำ",
          cards([(("%d" % (k + 2), "จุดที่พลาด"), "<p>%s</p><p><b>แก้:</b> %s</p>" % (md(r[0]), md(r[1]))) for k, r in enumerate(tv1["rows"][1:])], 2),
          tag="จุดที่ v0 ยังพลาด 2/2", cls="mid"))
    add(shot(11, "สกิล v0 ทำงานจบและลบเครื่องเอง แต่ระหว่างทาง AI ต้องแก้บั๊กในสคริปต์ของสกิล 1 จุด", [
        "ฟังก์ชัน `ssh_n` ใช้ตัวแปร `i` โดยไม่ประกาศ `local` จึงไปทับตัวนับ Node ของลูป worker ได้ที่อยู่ของโปรแกรมกลางผิด เข้าร่วมได้ 2 จาก 4 replica",
        "การเทรนรอบแรกค้างราว 14 นาที AI แก้เฉพาะสำเนาที่ใช้รัน (เพิ่ม `local rc i`) ไฟล์ในสกิลยังไม่ได้แก้"], src="img/c11b-step11-bug.jpg"))
    add(shot(11, "รอบสกิล 2 Node ได้ Speedup 1.44× (Efficiency 72%) บนคู่เครื่องนี้ ไม่ถึง 1.80× ของรอบหลัก", [
        "เวลาคำนวณลดลงครึ่งหนึ่ง (%s วินาที) แต่เวลาสื่อสารของเครื่องคู่นี้สูงกว่า (%s วินาที) จึงได้ 1.44 เท่า ไม่ถึง 1.80 เท่า" % (n("19.87 → 9.95"), n("4.35 เทียบ 1.62")),
        "Speedup ขึ้นกับคู่เครื่องที่ได้ ข้อสรุปที่ทำซ้ำได้คือทิศทาง ไม่ใช่ตัวเลขตัวเดียว",
        "คุณภาพไปทางเดียวกับรอบหลัก Item F1 ขึ้น ยอดรวมตรงลดลง 2.1 จุดเท่ากัน และเทรนน้อยกว่า (200 ใบ) Item F1 จึงขึ้นน้อยกว่า"]))

    # ===== 4 · สรุป
    CTX.update(kicker="สรุป", group="สรุป")
    add(E.divider("สรุป", "VRAM จำกัดเลือกแนวทางตาม Gradient Checkpointing · เพิ่ม Node คือการซื้อเวลา", "<p>ผลรวม · ตารางสรุป · บทเรียน · ข้อจำกัด</p>"))
    add(pair("เพิ่ม Node ทำให้เร็วขึ้นไม่ถึง 2 เท่า และทำให้เงินต่อ Epoch แพงขึ้นทุกกรณี",
             ("Speedup เทียบจำนวน Node", figbox("results/images/speedup_vs_nodes.png", "Speedup เทียบจำนวน Node")),
             ("เงินต่อ Epoch", figbox("results/images/cost_per_epoch.png", "เงินต่อ Epoch")),
             "ซ้าย: Effective Batch ใหญ่ใกล้ Ideal กว่า และที่ 3 Node เป็นแถบ **ประมาณการ** ไม่ใช่ผลวัด · ขวา: แท่ง 2 Node (สีเข้ม) สูงกว่า 1 Node (สีอ่อน) ทุกคู่",
             tag="results/metrics.json"))
    add(tbl("ตารางสรุป 8 กรณี: ถูกที่สุดคือ B · 1 Node · Effective Batch 32 และเร็วที่สุดคือ B · 2 Node · Effective Batch 32", t9))
    add(S("บทเรียนจาก LAB นี้", cards([(("%d" % (k + 1), "บทเรียน"), x) for k, x in enumerate(readpts("ขั้นที่ 9 ·"))], 2), cls="mid"))
    tlim = table("การทดลอง", "ข้อจำกัด")
    add(S("ข้อจำกัดของผลชุดนี้ที่ต้องอ่านก่อนนำตัวเลขไปใช้",
          cards([(r[0], r[1], "warn") for r in tlim["rows"]], 3), cls="mid"))
    add(S("สิ่งที่ไม่ผ่านหรือยังไม่ดีขึ้น", cards([
        ("ยอดรวมตรงลดลงหลัง Fine-tune", "Base %s → Fine-tuned A / B %s / %s · 2 ใบตอบ total เป็น `null` และ 1 ใบ JSON อ่านไม่ได้" % (bold(s7[1]), s7[2], s7[3]), "bad"),
        ("ยอดรวมตรงของ 8B ยังไม่ถึง 100%", " ".join(para("ขั้นที่ 7 ·", "สิ่งที่พูดได้")["lines"]).replace("สิ่งที่พูดได้: ", "") +
         " (2B Fine-tuned ของ LAB 2 ได้ %s)" % s7[5], "warn"),
        ("เพิ่ม Node ที่ Effective Batch 8", "เร็วขึ้นแค่ %s แต่จ่ายแพงขึ้น %s ต่อชั่วโมง" % (n("1.14–1.26 เท่า"), n("2.23 เท่า")), "warn"),
        ("สกิล v0 ยังมีบั๊ก", "รอบทดสอบสกิลได้ Speedup %s และต้องแก้บั๊กใน `run_train.sh` ระหว่างทาง" % sp11[2].split(" / ")[0], "bad")], 2), cls="mid"))

    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบ LAB 5", "ต้องลบทุกเครื่องเสมอ แม้งานระหว่างทางจะล้ม",
                  '<p>รายละเอียดเต็มของ LAB นี้: <a href="README.md" target="_blank">README.md</a> · พรอมต์ทั้งหมด: <a href="PROMPTS.md" target="_blank">PROMPTS.md</a></p>',
                  "img/p25-closing.jpg"))
    return E.SL


def readpts(prefix):
    bl = sec(prefix)
    for k, b in enumerate(bl):
        if b["t"] == "p" and b["lines"][0].strip() == "**อ่านผลอย่างไร**":
            return [x.rstrip(":").rstrip() for x in bl[k + 1]["items"]]
    raise KeyError("ไม่พบ อ่านผลอย่างไร ในหัวข้อ %r" % prefix)


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
