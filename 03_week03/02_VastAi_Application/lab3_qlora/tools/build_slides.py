#!/usr/bin/env python3
"""สร้างสไลด์ LAB3_QLoRA_Slides.html ของ LAB 3 · QLoRA โมเดลเล็กให้แชทบอทร้านนวด

  python tools/crops.py                   (ครั้งแรก: ตัดส่วนสำคัญของภาพหน้าจอเป็น img/cNN-*.jpg)
  python tools/build_slides.py            (รันจากโฟลเดอร์ของบท)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · ภาพเป็นตัวอธิบาย ข้อความข้างภาพไม่เกิน 3 ข้อ · ตารางเฉพาะจุดที่ต้องโฟกัส
เนื้อหาชนิดเดียวกันใช้รูปแบบสไลด์เดียวกันเสมอ:
  ภาพของขั้น / ทฤษฎี      = explain() ภาพซ้าย + ข้อเรียงเลขขวา
  ผลจริงจากคำตอบของ AI    = crop() ส่วนหนึ่งของภาพหน้าจอจริง (ภาพใหญ่) + ตัวเลขจริง
  อ่านผลอย่างไร           = explain() ภาพที่แสดงประเด็นหลัก + 3 ข้อ หรือ statement() ภาพถ่ายพร้อมประโยคเดียว
  เปรียบเทียบสองฝั่ง      = pair() ภาพคู่ ซ้าย Base ขวา Fine-tuned
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง โค้ด พรอมต์ (code fence ชนิด text) และข้อ "อ่านผลอย่างไร": อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ตัวเลขผล: อ่านจาก results/metrics.json · ประโยคที่ยกจาก README ถูกตรวจด้วย q() ว่ามีอยู่ในหัวข้อนั้นของ README
- ภาพใหม่: tools/slides_figures.py · ภาพตัดจากภาพหน้าจอจริง: tools/crops.py · เครื่องมือเรนเดอร์: tools/slides_engine.py
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, codes, para, CTX, add, note, fig, explain, tiles, cards,
                           bars, tbl, code)
from slides_figures import FIGS, FIGS2

S = E.slide
SECS = E.load("README.md")
FIG = {f["img"]: f for f in FIGS + FIGS2}
OUT, TITLE = "LAB3_QLoRA_Slides.html", "LAB 3 · QLoRA โมเดลเล็กให้แชทบอทร้านนวด · Slides"
M = json.loads(E.read("results/metrics.json"))
VAL, DS, TR, E2E = M["validation_set"], M["dataset"], M["training"], M["e2e_26_cases"]
COST = M["machines_and_cost_usd"]

# ------------------------------------------------------------------ CSS เฉพาะเด็คนี้ (ฟอนต์ สี และการนำทางเป็นของ engine)
E.CSS += r"""
.prog{display:flex;gap:8px;margin-top:26px;flex-wrap:wrap}
.prog span{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;
  font-size:19px;color:rgba(255,255,255,.75);border:2px solid rgba(255,255,255,.35)}
.prog span.done{background:rgba(255,255,255,.18);color:#fff;border-color:rgba(255,255,255,.5)}
.prog span.now{background:var(--orange);color:#fff;border-color:var(--orange)}
.prog span.gap{width:18px;border:0}
.stmt{flex:1 1 0;min-height:0;position:relative;border-radius:14px;overflow:hidden;background-size:cover;background-position:center}
.stmt .band{position:absolute;left:0;top:0;bottom:0;width:52%;padding:44px 46px;display:flex;flex-direction:column;justify-content:center;gap:.7em;
  background:linear-gradient(90deg,rgba(10,22,44,.92) 0%,rgba(10,22,44,.82) 70%,rgba(10,22,44,0) 100%);color:#fff}
.stmt .band .say{font-size:1.75em;font-weight:700;line-height:1.35;margin:0}
.stmt .band ol{margin:0;padding-left:1.2em;font-size:1.02em;line-height:1.5;color:#e8eef8}
.stmt .band ol li{margin:.3em 0}
.stmt .band code{background:rgba(255,255,255,.14);color:#fff}
.stmt .imgnote{position:absolute;right:14px;bottom:10px;font-size:13px;color:rgba(255,255,255,.8)}
.crop{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:14px}
.crop .shot{flex:1 1 0;min-height:0;display:flex;align-items:center;justify-content:center;background:#fff;border:1px solid var(--line);
  border-radius:12px;padding:10px;box-shadow:0 2px 10px rgba(18,48,94,.06)}
.crop .shot img{width:100%;height:100%;object-fit:contain;cursor:zoom-in}
.divider .small{margin-bottom:22px}
.wx{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:14px}
.wx .shot{flex:1 1 0;min-height:0;display:flex;align-items:center;justify-content:center}
.wx .shot img{width:100%;height:100%;object-fit:contain;cursor:zoom-in;border-radius:10px}
.wx .row{flex:none;display:flex;gap:16px}
.wx .row .stp{flex:1 1 0;min-width:0}
.crop .tiles .tile{padding:14px 20px}
.crop .tiles .num{font-size:2.1em}
.crop .cap{margin:0}
.pair{flex:1 1 0;min-height:0;display:flex;gap:26px}
.pair .pc{flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:10px}
.pair .pc .lab{font-weight:700;font-size:1.05em;padding:6px 14px;border-radius:8px;align-self:flex-start}
.pair .pc.ok .lab{background:var(--green-soft);color:var(--green)}
.pair .pc.bad .lab{background:var(--red-soft);color:var(--red)}
.pair .pc .im{flex:1 1 0;min-height:0;display:flex;align-items:center;justify-content:center}
.pair .pc .im img{max-width:100%;max-height:100%;object-fit:contain;border-radius:10px;border:1px solid var(--line);cursor:zoom-in}
.pair .pc p{margin:0;line-height:1.45}
.said{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--navy);border-radius:10px;padding:10px 18px;margin-bottom:14px;line-height:1.45}
"""

# ------------------------------------------------------------------ ตัวช่วยอ่าน README
RAW = {}
_cur = None
for _ln in E.read("README.md").split("\n"):
    _m = re.match(r"^#{1,4}\s+(.*)$", _ln)
    if _m:
        _cur = _m.group(1).strip()
        RAW[_cur] = []
    elif _cur is not None:
        RAW[_cur].append(_ln)


def raw(prefix):
    for k, v in RAW.items():
        if k.startswith(prefix):
            return "\n".join(v)
    raise KeyError("ไม่พบหัวข้อ %r" % prefix)


def q(prefix, s):
    """ข้อความที่มีตัวเลข ต้องมีอยู่ตรงตัวในหัวข้อ prefix ของ README (กันตัวเลขที่พิมพ์ผิดด้วยมือ)"""
    if s not in raw(prefix):
        raise KeyError("ข้อความ %r ไม่อยู่ในหัวข้อ %r ของ README" % (s, prefix))
    return s


def took(prefix):
    """บรรทัด *ใช้เวลา ...* ใต้ภาพผลของขั้น"""
    p = para(prefix, "*ใช้เวลา")
    return p["lines"][0].strip("*")


def pct(x):
    return ("%.1f%%" % x).replace(".0%", "%") if x in (0, 100) else "%.1f%%" % x


def have(src):
    return os.path.exists(os.path.join(E.ROOT, src))


def keep(s, *words):
    """หน้าปกและหน้าคั่น: ห้ามตัดคำภาษาไทยกลางคำ (ครอบคำด้วย nowrap) · br = ขึ้นบรรทัดใหม่ก่อนคำนั้น"""
    for w in words:
        br = w.startswith("\n")
        w = w.lstrip("\n")
        if w not in s["raw"]:
            raise KeyError("ไม่พบ %r ในสไลด์ %r" % (w, s["title"]))
        s["raw"] = s["raw"].replace(w, ("<br>" if br else "") + '<span style="white-space:nowrap">%s</span>' % w, 1)
    return s


def nimg(key):
    return "img/%s.jpg" % key


def nfig(key, steps=None, title=None, post=""):
    """สไลด์ ภาพ + ข้อเรียงเลข ของภาพใหม่ใน slides_figures.py"""
    f = FIG[key]
    return explain(title or f["title"], nimg(key), steps if steps is not None else f["steps"], post)


def statement(title, src, say, items, tag=""):
    """ภาพถ่ายเต็มพื้นที่ + แถบซ้ายมีประโยคหลัก 1 ประโยค และข้อสั้น ๆ ไม่เกิน 3 ข้อ"""
    ol = "".join("<li>%s</li>" % md(x) for x in items)
    body = ('<div class="stmt" style="background-image:url(%s)"><div class="band"><p class="say">%s</p><ol>%s</ol></div>'
            '<div class="imgnote">ภาพจำลอง</div></div>') % (src, md(say), ol)
    return S(title, body, tag=tag, maxfs=1.2)


def crop(title, src, items, full, cap="ส่วนหนึ่งของคำตอบจริง"):
    """ส่วนหนึ่งของภาพหน้าจอจริง (ตัดจากภาพเต็ม ไม่แก้พิกเซล) แสดงใหญ่ + ตัวเลขจริงด้านล่าง + ลิงก์ภาพเต็ม"""
    img = E.img_tag({"t": "img", "src": src, "alt": E.plain(title)})
    side = "".join('<div class="tile %s"><div class="k">%s</div><div class="num">%s</div><div class="s">%s</div></div>'
                   % (tone, md(k), num, md(s)) for k, num, s, tone in items)
    body = ('<div class="crop"><div class="shot">%s</div>%s<p class="cap">%s</p></div>'
            % (img, '<div class="tiles">%s</div>' % side if items else "", md(cap + " · ภาพเต็ม: [%s](%s)" % (full, full))))
    return S(title, body, tag="ผลรอบจริง", maxfs=1.15)


def widex(title, src, steps, post="", tag=""):
    """ภาพกว้าง (ตาราง กราฟ ภาพตัด) เต็มความกว้าง + ข้อเรียงเลขเป็นแถวด้านล่าง (ไม่เกิน 3 ข้อ)"""
    img = E.img_tag({"t": "img", "src": src, "alt": E.plain(title)})
    row = "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(steps))
    return S(title, '<div class="wx"><div class="shot">%s</div><div class="row">%s</div>%s</div>' % (img, row, post), tag=tag, maxfs=1.15)


def pair(title, said, a, b, tag=""):
    """ภาพคู่ · a, b = (ป้าย, ภาพ, คำบรรยาย, โทน ok|bad)"""
    out = []
    for lab, src, cap, tone in (a, b):
        out.append('<div class="pc %s"><span class="lab">%s</span><div class="im">%s</div><p>%s</p></div>'
                   % (tone, md(lab), E.img_tag({"t": "img", "src": src, "alt": E.plain(lab)}), md(cap)))
    head = '<div class="said">%s</div>' % md(said) if said else ""
    return S(title, head + '<div class="pair">%s</div>' % "".join(out), tag=tag, maxfs=1.15)


VARY = "ตัวเลขของคุณอาจต่างจากของผู้สอน เพราะ AI เขียนโค้ดไม่เหมือนกันทุกครั้ง และเครื่องที่เช่าได้ต่างกัน · สิ่งที่ต้องมีเหมือนกันคือไฟล์ผลครบและข้อสรุปตามหลักฐาน"


def check(key, items, ref, title, note_text=VARY):
    return E.check_slide(key, items, "ผลของผู้สอน: " + ref, note_text, title)


def progress(n, total=10):
    out = []
    for k in range(1, total + 1):
        if k == 9:
            out.append('<span class="gap"></span>')
        out.append('<span class="%s">%d</span>' % ("now" if k == n else "done" if k < n else "", k))
    return '<div class="prog">%s</div>' % "".join(out)


def step_divider(n, title, what, result):
    key = "ขั้นที่ %d ·" % n
    sub = ('<p>%s</p><p><b>เวลาจริง</b> %s</p><p><b>ผลจริง</b> %s</p>%s'
           % (md(what), md(took(key)), md(result), progress(n)))
    part = "ส่วนที่ 2 จาก 4 · ภาค LAB" if n <= 8 else "ส่วนที่ 3 จาก 4 · สกิลเวอร์ชัน 0"
    return E.divider("ขั้นที่ %d จาก 10" % n, title, sub, small=part)


def part_divider(n, name, title, sub, img=""):
    return E.divider(name, title, "<p>%s</p>" % md(sub), img if have(img) else "", small="ส่วนที่ %d จาก 4" % n)


def prompt_of(n, title):
    return E.prompt_slides(E.prompt_code("ขั้นที่ %d ·" % n), CTX["kicker"], "ขั้นที่ %d · %s" % (n, title))


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    vb, vf = VAL["base"], VAL["finetuned"]
    eb, ef = E2E["B_base"], E2E["C_finetuned"]

    # ===== เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    CT, CS, CSM = ("LAB 3 · QLoRA โมเดลเล็กให้แชทบอทร้านนวด",
                   "โมเดลเล็ก 4B บน GPU ที่ถูกกว่า ตอบได้ดีแค่ไหน และการเทรนเพิ่มด้วย QLoRA ช่วยให้ดีขึ้นหรือไม่",
                   "สัปดาห์ที่ 3 · 02 VastAi Application · LAB 3")
    add(keep(E.cover(CT, CS, "img/s01-cover.jpg", small=CSM), "\nโมเดลเล็กให้แชทบอทร้านนวด"))
    CTX["kicker"] = "ภาพรวมของ LAB"
    add(fig("ผลของทั้ง LAB: ชุดทดสอบ 26 เคสผ่าน %d/%d เท่ากัน แต่ Validation Set ดีขึ้นจาก %s เป็น %s"
            % (eb["passed"], eb["total"], pct(vb["correct_pct"]), pct(vf["correct_pct"])),
            "results/val_compare.png",
            "ซ้าย: ชุดทดสอบ 26 เคส Base ตกเคส %d และ Fine-tuned ตกเคส %d (ผล 26/26 ของโมเดลครูอ้างจากบทที่แล้ว) · "
            "ขวา: ดูแท่งแรก **คำตอบที่ถูกบน Validation Set 85 คำตอบ**" % (eb["failed_cases"][0], ef["failed_cases"][0]),
            tag="results/val_compare.png"))
    add(explain("LAB นี้มี 4 ส่วน และส่วนที่ใช้เวลามากที่สุดคือภาค LAB", nimg("n21-plan"), [
        "**ภาคพื้นฐาน**: โจทย์ของร้าน Dataset โมเดล และทฤษฎี 7 ข้อ",
        "**ภาค LAB ขั้นที่ 1–8**: เช่าเครื่อง ทำ Dataset เทรน วัดผล แล้วลบเครื่อง",
        "**สกิลเวอร์ชัน 0 (ขั้นที่ 9–10)** และ **สรุป** ผลกับข้อจำกัด"]))
    add(S("วิธีใช้สไลด์ชุดนี้", cards([
        ("เลื่อนหน้า", '<p><span class="kbd">→</span> <span class="kbd">Space</span> ถัดไป · <span class="kbd">←</span> ก่อนหน้า</p>'),
        ("สารบัญและเต็มจอ", '<p><span class="kbd">O</span> เปิดสารบัญ · <span class="kbd">F</span> เต็มจอ · คลิกภาพเพื่อขยาย</p>'),
        ("คัดลอกพรอมต์", "<p>ปุ่ม <b>คัดลอกพรอมต์ทั้งหมด</b> ให้ข้อความตรงตัวอักษรกับ README แล้ววางในช่องพิมพ์ของ Claude Code ทีละขั้น</p>"),
        ("ตรวจผลของคุณ", "<p>หน้า <b>ตรวจผลของคุณ</b> ติ๊กได้ทีละข้อ เบราว์เซอร์จำค่าที่ติ๊กไว้ และมีผลของผู้สอนให้เทียบด้านล่าง</p>")], 2), cls="mid"))

    # ===== 1 · ภาคพื้นฐาน
    CTX.update(kicker="", group="ภาคพื้นฐาน")
    add(part_divider(1, "ภาคพื้นฐาน", "โจทย์ ข้อมูล โมเดล และทฤษฎีที่ต้องรู้",
                     "ทำไมร้านจึงอยากเปลี่ยนเป็นโมเดลเล็ก ข้อมูลเทรนมาจากไหน LoRA และ QLoRA ทำงานอย่างไร และวัดผลอย่างไรให้เชื่อได้",
                     nimg("p21-shop")))
    CTX.update(kicker="ภาคพื้นฐาน · โจทย์", group="ภาคพื้นฐาน · โจทย์")
    add(fig("คำถามของ LAB: โมเดลเล็กบน GPU ที่ถูกกว่าราว 3 เท่า ตอบได้ดีพอหรือไม่", "image/why3-qlora.png",
            "แชทบอทของบทที่แล้วใช้ **โมเดลใหญ่ 27B** บน RTX 5090 · LAB นี้ลอง **โมเดลเล็ก 4B** บน RTX 3090 แล้วสอนเพิ่มด้วย **QLoRA**"))

    # --- Dataset
    CTX.update(kicker="ภาคพื้นฐาน · Dataset", group="ภาคพื้นฐาน · Dataset")
    add(nfig("n22-dataset-layers", [
        "สคริปต์สร้างคำถามลูกค้า %d บท (%s ข้อความ 12 ชนิด) แล้วโมเดลครูเป็นผู้ตอบ" % (DS["dialogs_total"], format(DS["user_messages_total"], ",")),
        "คำตอบที่ผิดเงื่อนไขถูกทิ้งทั้งบท เหลือ **%d บท** แบ่งเป็น Training Set %d บท (%d คำตอบ) และ Validation Set %d บท (%d คำตอบ)"
        % (DS["passed"], DS["train"], DS["train_assistant_turns"], DS["val"], DS["val_assistant_turns"]),
        "ชุดทดสอบ 26 เคสของบทที่แล้วไม่อยู่ใน Dataset · ชื่อและเบอร์โทรทุกรายการเป็นค่าสุ่ม"],
        title="Dataset ของ LAB นี้สร้างขึ้นเอง: สคริปต์เขียนคำถาม แล้วโมเดลครูเป็นผู้ตอบ"))
    add(fig("ตัวอย่างจริงของ Dataset: คำถามของลูกค้า คำตอบของครู และเงื่อนไขของคำตอบ", nimg("c21-dataset-top"),
            "ส่วนบนของ `results/dataset_samples.jpg` จากขั้นที่ 3 · ดูคอลัมน์ขวาสุด **เงื่อนไขของคำตอบ** ที่ใช้ตรวจคำตอบของครู · "
            "[ภาพเต็ม](results/dataset_samples.jpg)", tag="results/dataset_samples.jpg"))
    add(code("ข้อมูล 1 รายการเป็นบทสนทนา 3 บทบาท พร้อมเงื่อนไขของคำตอบ", codes("รู้จัก Dataset", "json")[0]["text"], "json",
             pre="<p>บรรทัดจริงจาก <code>data/train.jsonl</code> (ย่อ system prompt)</p>"))
    add(explain("แต่ละช่องของข้อมูลมีหน้าที่ต่างกัน และ expects คือ label ที่ใช้ตรวจคำตอบ", nimg("n23-record"), [
        "**messages** คือสิ่งที่โมเดลเห็น: system prompt ชุดเดียวกับเว็บจริง ข้อความลูกค้า และคำตอบของครูที่ผ่านการตรวจ",
        "**expects** กำหนดว่าคำตอบต้องมี (`has`) ห้ามมี (`not`) ต้องตอบภาษาใด (`lang`) และต้องมีแท็กจองหรือไม่ (`booking`)",
        "**now** คือวันเวลาของบทนั้น ไม่ซ้ำกันทั้ง 570 บท โมเดลจึงต้องคิดคำว่า \"พรุ่งนี้\" จาก prompt"]))
    kinds = sorted(DS["per_kind"].values(), key=lambda k: k["passed"] / k["total"])
    add(S("Dataset มีอคติ: คำถามภาษาอังกฤษผ่าน 25/50 และการจองครบในข้อความเดียวผ่าน 17/40",
          bars([(k["kind_th"], "", k["passed"], k["total"], "%d/%d" % (k["passed"], k["total"])) for k in kinds[:6]])
          + note("สองชนิดนี้จึงมีตัวอย่างน้อย และโมเดลเล็กได้เรียนน้อยตามไปด้วย · ชนิดที่เหลือผ่านตั้งแต่ %d/%d ขึ้นไป · "
                 "Validation Set มีเพียง %d บท บางชนิดเหลือ 1–2 บท ตัวเลขรายชนิดจึงแกว่งง่าย"
                 % (kinds[6]["passed"], kinds[6]["total"], DS["val"])),
          tag="6 ชนิดที่ผ่านน้อยที่สุด · results/metrics.json"))

    # --- โมเดล
    CTX.update(kicker="ภาคพื้นฐาน · โมเดล", group="ภาคพื้นฐาน · โมเดล")
    t = {r[0]: r[1] for r in table("รู้จักโมเดลที่ใช้", "หัวข้อ")["rows"]}
    add(explain("โมเดลนักเรียนคือ Qwen3-4B-Instruct โมเดลเล็กที่นำมาเทรนเพิ่ม", "image/model-qwen3-4b.png", [
        "**Input** เป็นข้อความ: system prompt (กติกาและข้อมูลร้าน ราว 1,000 token) ประวัติแชท และข้อความล่าสุดของลูกค้า",
        "**ขนาด**: " + t["ขนาด"],
        "**Base** คือโมเดลตามที่โหลดมา (`qwen3-4b-base`) ส่วน **Fine-tuned** คือโมเดลเดียวกันเสียบ LoRA Adapter (`qwen3-4b-sabaijai`)"]))
    blocks = list(walk(sec("รู้จักโมเดลที่ใช้")))
    t2 = next(b for b in blocks if b["t"] == "table" and b["head"][1].startswith("Qwen3.8"))
    t2 = {r[0]: r[1] for r in t2["rows"]}
    add(explain("โมเดลครู Qwen3.8 27B ใช้ตอบคำถามเพื่อทำ Dataset แล้วลบเครื่องทันที", "image/model-qwen27b.png", [
        "**ขนาด**: " + t2["ขนาด"],
        "**ใน LAB นี้**: " + t2["ใน LAB นี้"],
        "ผล **26/26** ของโมเดลครูบนชุดทดสอบ **อ้างจากบทที่แล้ว ไม่ได้รันซ้ำใน LAB นี้**"]))

    # --- ทฤษฎี 1 LoRA
    CTX.update(kicker="ภาคพื้นฐาน · ทฤษฎี 1 จาก 7 · LoRA", group="ภาคพื้นฐาน · ทฤษฎี")
    add(explain("LoRA ไม่แก้ weight เดิม แต่เพิ่มเมทริกซ์เล็ก 2 ตัวแล้วเทรนเฉพาะส่วนนั้น", "image/t3-lora.png", [
        "ตรึง weight เดิมไว้ทั้งหมด แล้วเพิ่มเมทริกซ์ A และ B ข้างชั้น Linear แต่ละชั้น",
        "ผลที่ได้คือไฟล์ **Adapter** ขนาดเล็กที่ใช้คู่กับ Base Model",
        q("1 · LoRA", "Full Fine-tuning ต้องปรับ weight ราว 4,000 ล้านตัว") + " ส่วน LoRA ใช้หน่วยความจำน้อยกว่าและเสี่ยง Overfitting น้อยกว่า"]))
    add(explain("ผลของชั้นเท่ากับทางเดิม W·x บวกทางเสริม (α / r)·B·A·x", "image/t3-lora-how.png", [
        "`W·x` คือทางเดิมที่ **Frozen** ส่วน `B·A·x` คือทางเสริมที่เทรน",
        "**Rank r** คือความจุของทางเสริม **Alpha α** คือตัวคูณความแรง · เริ่มต้น B = 0 โมเดลจึงตอบเหมือนเดิมก่อนเทรน",
        "LAB นี้ใช้ " + q("1 · LoRA", "Rank 8 · Alpha 16 · dropout 0.05") + " กับชั้น Linear 7 ชนิด ทั้ง 36 block"]))
    t = {r[0]: r[1] for r in table("1 · LoRA", "รายการ")["rows"]}
    add(explain("ใน LAB นี้ LoRA เทรนราว 0.4% ของโมเดล และได้ไฟล์ Adapter 63 MB", "image/t3-lora-size.png", [
        "**ตัวอย่าง 1 ชั้น `q_proj`**: " + t["ตัวอย่าง 1 ชั้น (`q_proj` ขนาด 2560 → 4096)"],
        "**ทั้งโมเดล**: " + t["ทั้งโมเดล"], "**ไฟล์ที่ได้**: " + t["ไฟล์ที่ได้"]]))

    # --- ทฤษฎี 2 QLoRA
    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 2 จาก 7 · QLoRA"
    add(explain("QLoRA โหลด Base Model แบบ 4-bit แล้วตรึงไว้ และเทรน LoRA Adapter ทับลงไป", "image/t3-qlora.png", [
        "**Quantization** คือการเก็บ weight แต่ละตัวด้วยจำนวนบิตที่น้อยลง (16 บิต → 4 บิต)",
        "บทสนทนาของ LAB นี้ยาว " + q("2 · Quantization", "เฉลี่ยราว 1,900 token ต่อบท") + " และตอนเทรน GPU ต้องเก็บค่ากลางของทุกชั้นไว้คำนวณ gradient",
        "Base Model ยิ่งกินที่น้อย ยิ่งเหลือที่ให้บทสนทนายาวบน **การ์ด 24 GB** ที่เช่าได้ถูก"]))
    add(explain("NF4 วาง 16 ระดับให้ถี่ใกล้ 0 เพราะ weight ส่วนใหญ่อยู่ใกล้ 0", "image/t3-nf4.png", [
        "**NF4** แบ่งค่าของ weight เป็น 16 ระดับ และ **Double Quantization** บีบค่าสเกลของแต่ละกลุ่มอีกชั้น",
        "ตอนคำนวณ weight ถูกแปลงกลับเป็น bfloat16 ชั่วคราว และ gradient ไปปรับเฉพาะ A และ B",
        "ส่งทีละ 1 บท แล้วสะสม gradient 8 บทต่อการปรับ weight 1 ครั้ง เพื่อไม่ให้ VRAM ล้น"]))
    add(fig("QLoRA ใน LAB นี้เทรน 165 step ใน 35.6 นาที บน RTX 3090 24 GB", "image/t3-qlora-result.png",
            "VRAM สูงสุด **22.9 GB** เป็นค่าที่ PyTorch **จองไว้** ซึ่งสูงกว่าที่ใช้จริง · ตอนให้บริการ vLLM โหลด Base Model ความละเอียดเต็ม แล้วเสียบ Adapter ตัวเดิม"))

    # --- ทฤษฎี 3 Distillation
    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 3 จาก 7 · Knowledge Distillation"
    add(explain("Knowledge Distillation: ครูตอบก่อน แล้วคำถามกับคำตอบของครูกลายเป็น Training Data", "image/t3-distill.png", [
        "ถ่ายความสามารถของโมเดลใหญ่ (**Teacher**) ให้โมเดลเล็ก (**Student**) โดยเรียนจากข้อความคำตอบของครู (response-based)",
        "ร้านนี้ไม่มีคำตอบตัวอย่างหลายร้อยบท และการจ้างคนเขียนทั้งแพงและช้า",
        "จ่ายค่าเช่าเครื่องครูครั้งเดียวในเวลาสั้น เพื่อได้โมเดลเล็กที่ใช้ได้ทุกวัน"]))
    add(fig("สายพาน 5 ช่องของ Distillation: ครูก็ตอบผิดได้ จึงต้องกรองก่อนใช้สอน", "image/t3-distill-pipeline.png",
            q("3 · Knowledge Distillation", "ผ่าน **485 บท (85.1%)** โดยผ่านตั้งแต่ครั้งแรก 466 และผ่านหลังตอบใหม่ 19") + " · ค่าเช่าเครื่องครู **$0.33**"))
    rs = list(DS["drop_main_reason"].items())
    add(S("85 บทที่ถูกทิ้ง: เหตุผลอันดับแรกคือลูกค้าถามภาษาอังกฤษ แต่ครูตอบภาษาไทย",
          bars([(k, "", v, DS["dropped"], "%d บท" % v) for k, v in rs]) + note("ความยาวของทุกแท่งเทียบกับ %d บทที่ถูกทิ้ง" % DS["dropped"]),
          tag="results/metrics.json"))

    # --- ทฤษฎี 4 split
    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 4 จาก 7 · Data Leakage"
    add(explain("ข้อมูล 3 ชุดต้องไม่ซ้ำกัน ถ้าข้อสอบรั่วเข้าข้อมูลเทรน คะแนนจะสูงเกินจริง", "image/t3-split-leak.png", [
        q("4 · Training", "ห้ามซ้ำตรงตัว และความคล้ายต้องต่ำกว่า 0.75") + " · ผลจริงคือซ้ำ **0 ข้อความ** และความคล้ายสูงสุด **0.72**",
        "**Validation Set** ใช้ดู loss ระหว่างเทรน เลือก Adapter ที่ดีที่สุด และเทียบ Base กับ Fine-tuned",
        "**ข้อควรระวัง**: Validation Set มาจากแม่แบบประโยคชุดเดียวกับ Training Set จึงวัดได้เพียงว่าโมเดล **ตอบคำถามแบบที่ครูสอนได้ดีแค่ไหน**"]))

    # --- ทฤษฎี 5 loss
    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 5 จาก 7 · Validation loss"
    t = table("5 · อ่าน Validation loss", "ช่วงของกราฟ")
    add(widex("Validation loss ลงเร็วใน 20 step แรก แล้วราบที่ราว 0.31 จึงหยุดที่ 3 Epoch", "results/loss_curve.png",
                ["**%s** (%s): %s" % (r[0], md(r[1]), r[2]) for r in t["rows"]],
                post=note("ดูเส้นแดง (Validation loss) เทียบกับเส้นฟ้า (Training loss) ในช่วงท้าย · loss ต่ำแปลว่าเลียนแบบครูได้ใกล้ "
                          "**ไม่ได้แปลว่าตอบถูกทุกข้อ**", label="อ่านกราฟ")))

    # --- ทฤษฎี 6 วัดผล 2 ชั้น
    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 6 จาก 7 · วัดผล 2 ชั้น"
    add(explain("ไม้บรรทัด 2 อันละเอียดไม่เท่ากัน: 1 เคสมีน้ำหนัก 3.8% แต่ 1 คำตอบมีน้ำหนัก 1.2%", "image/t3-eval-rulers.png", [
        "**ชุดทดสอบ 26 เคส**: Playwright พิมพ์ในเว็บจริงเหมือนลูกค้า และตรวจว่ามีคำหรือตัวเลขที่กำหนด",
        "โมเดลเล็กที่ยังไม่เทรนก็ผ่าน 25/26 แล้ว จึง **เหลือที่ให้ดีขึ้นได้เพียง 1 เคส**",
        "**Validation Set 85 คำตอบ** ตรวจด้วยเงื่อนไขชุดเดียวกับที่ใช้กรองคำตอบของครู ที่ temperature 0"]))

    # --- ทฤษฎี 7 ต้นทุน
    CTX["kicker"] = "ภาคพื้นฐาน · ทฤษฎี 7 จาก 7 · ต้นทุน"
    add(fig("ราคาถูกลงราว 3.1 เท่าเป็นข้อเท็จจริง แต่คุณภาพต้องดูจากผลของขั้นที่ 5 และ 7", "image/t3-cost.png",
            "แชทบอทเปิดตลอดเวลา ถ้าเปิดทั้งเดือนจะเป็นราว $536 เทียบกับราว $174 · "
            + q("7 · ต้นทุน", "Adapter ทำให้ช้าลงราว 8% (55.0 → 50.6 token ต่อวินาที)")))

    # --- การทดลอง
    CTX.update(kicker="ภาคพื้นฐาน · การทดลอง", group="ภาคพื้นฐาน · การทดลอง")
    add(nfig("n01-experiment", [
        "**A = โมเดลครู 27B** บน RTX 5090 ผล 26/26 **อ้างจากบทที่แล้ว ไม่ได้รันซ้ำ**",
        "**B = Base** และ **C = Base + LoRA** (Rank 8, Alpha 16, 3 Epoch, learning rate 0.0002, seed 0) อยู่บน server เดียวกัน เว็บเดียวกัน prompt เดียวกัน",
        "วัด 2 ชั้น: Validation Set 85 คำตอบ (temperature 0) และชุดทดสอบ 26 เคสผ่านเว็บจริง พร้อมรันซ้ำ 5 รอบผ่าน API"],
        title="การทดลองเทียบ 3 แขนด้วยตัววัดชุดเดียวกัน"))

    # ===== 2 · ภาค LAB
    CTX.update(kicker="", group="ภาค LAB")
    add(keep(part_divider(2, "ภาค LAB", "ขั้นที่ 1–8: จากคำถามลูกค้า ถึงชุดทดสอบ 26 เคส",
                          "ทุกขั้นมีลำดับเดียวกัน คือภาพของขั้น พรอมต์ ตรวจผลของคุณ ผลจริง และวิธีอ่านผล · "
                          + q("การทดลอง", "ทำตามลำดับขั้นที่ 1 → 8 ให้ครบในรอบเดียว"), "img/s02-lab.jpg"),
             "ถึงชุดทดสอบ 26 เคส"))
    CTX.update(kicker="ภาค LAB · แผนที่", group="ภาค LAB")
    add(fig("LAB มี 10 ขั้น ทุกขั้นคือ 1 พรอมต์ และโค้ดทุกไฟล์ AI เขียนให้", "image/lab3-overview.png",
            "ขั้นที่ **1–8** คืองานหลัก · ขั้นที่ **9–10** เก็บงานเป็นสกิลเวอร์ชัน 0 · ขั้นที่ 6 ทำบนเครื่องของเรา นอกนั้นใช้เครื่องเช่าบน Vast.ai"))
    mins = M["minutes_per_step"]
    names = {1: "สร้างคำถามลูกค้า", 2: "เปิดโมเดลครู (RTX 5090)", 3: "ครูตอบ แล้วคัดเป็น Dataset", 4: "เทรน QLoRA (RTX 3090)",
             5: "AI server 2 โมเดล + วัดผล", 6: "ต่อเว็บแชทบอท (เครื่องของเรา)", 7: "ชุดทดสอบ 26 เคส", 8: "ลบเครื่อง สรุปค่าใช้จ่าย",
             9: "สรุปเป็นสกิล v0", 10: "ลองใช้สกิล v0"}
    mx = max(float(mins[str(n)]) for n in range(1, 11))
    add(S("เวลาจริงของแต่ละขั้น: ขั้นที่ 4 เทรนนานที่สุด และขั้นที่ 1–8 รวม %.0f นาที" % M["minutes_total_steps_1_to_8"],
          bars([("%d · %s" % (n, names[n]), "", float(mins[str(n)]), mx, "%s นาที" % mins[str(n)]) for n in range(1, 11)])
          + note("ขั้นที่ 2–5 และ 7 ใช้เครื่องเช่า เงินจึงเดินตามเวลาที่เครื่องเปิด · ความยาวแท่งเทียบกับขั้นที่ใช้เวลานานที่สุด", label="อ่านแผนภาพ"),
          tag="results/metrics.json"))
    add(explain("ก่อนเริ่มต้องมี 4 อย่าง: key, Claude Code, container และ Docker", nimg("n24-before"), [
        "ทำ [LAB 0](../README.md) ของบทเพื่อเตรียม key 3 ตัว แล้วเปิด Claude Code ที่โฟลเดอร์ `02_VastAi_Application`",
        "ขั้นที่ 2–5 และ 7–8 ทำงานใน container `multi-account` ด้วยสกิล vastai ส่วนขั้นที่ 6 รันเว็บด้วย Docker บนเครื่องของเรา",
        "เว็บแชทบอทและชุดทดสอบ 26 เคสเป็นระบบเดิมจาก[บทที่แล้ว](../../01_VastAi_Skill/) ซึ่งขั้นที่ 1 คัดลอกมาใช้ต่อ"]))

    # --- ขั้นที่ 1
    T1 = "เตรียมแชทบอทเดิม และเขียนโค้ดสร้างคำถามลูกค้า"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 1 จาก 10 · สร้างคำถามลูกค้า", group="ขั้นที่ 1")
    add(step_divider(1, T1, "คัดลอกเว็บและชุดทดสอบเดิม แล้วเขียน `make_questions.py` ขั้นนี้ยังไม่เช่าเครื่อง",
                     "%d บท 12 ชนิด และซ้ำกับชุดทดสอบ 0 ข้อความ" % DS["dialogs_total"]))
    add(nfig("n02-step1-questions", [
        "คัดลอกเว็บแชทบอทเป็น `code/web` และชุดทดสอบ 26 เคสเป็น `code/e2e` โดยไม่แก้ต้นฉบับ",
        "`make_questions.py` สร้างคำถามจากแม่แบบประโยค สุ่มชื่อ เบอร์ บริการ และวันเวลา (seed 2026) ทุกข้อความมีเงื่อนไขของคำตอบ",
        "ตรวจว่าไม่ซ้ำหรือคล้ายข้อความของชุดทดสอบ แล้วเก็บที่ `data/questions.jsonl` ซึ่งยังไม่มีคำตอบ"],
        title="ขั้นที่ 1 สร้างคำถามลูกค้าที่มีเงื่อนไขของคำตอบกำกับทุกข้อความ"))
    add(prompt_of(1, T1))
    add(check("step1", [
        "มี `lab3_qlora/code/web` และ `lab3_qlora/code/e2e` ที่คัดลอกจากบทที่แล้ว โดยต้นฉบับไม่ถูกแก้",
        "`lab3_qlora/code/make_questions.py` รันได้ และได้ `lab3_qlora/data/questions.jsonl` อย่างน้อย 500 บท",
        "ตารางจำนวนบทแยกตามชนิด มีทั้งคำถามทั่วไปและการจองคิว 5 แบบ",
        "ทุกข้อความของลูกค้ามีเงื่อนไขของคำตอบกำกับไว้ (ดูจากตัวอย่าง 2 บทในคำตอบ)",
        "ผลตรวจกับชุดทดสอบ: ข้อความที่ตรงกัน 0 · ความคล้ายสูงสุดต่ำกว่า 0.75",
        "นับจำนวนข้อความในไฟล์เอง แล้วเทียบกับตัวเลขในคำตอบของ AI"],
        "%d บท 12 ชนิด · ข้อความลูกค้าในไฟล์ %s ข้อความ · ซ้ำ 0 · ความคล้ายสูงสุด 0.72 · %s"
        % (DS["dialogs_total"], format(DS["user_messages_total"], ","), took("ขั้นที่ 1 ·")), "ขั้นที่ 1 · " + T1))
    add(crop("ผลจริงขั้นที่ 1: ได้ %d บท 12 ชนิด และไม่มีข้อความใดซ้ำกับชุดทดสอบ" % DS["dialogs_total"], nimg("c23-step1-leak"), [
        ("บทสนทนาฝั่งลูกค้า", "%d บท" % DS["dialogs_total"], "12 ชนิด · seed 2026", "ok"),
        ("ข้อความซ้ำกับชุดทดสอบ", "0", "เทียบกับ 49 ข้อความ (26 เคส + ปุ่มลัด)", "ok"),
        ("ความคล้ายสูงสุด", "0.72", "ต่ำกว่าเกณฑ์ 0.75", "")], "image/lab3-step1.png",
        cap="ส่วนหนึ่งของคำตอบจริง · โค้ด: [code_reference/make_questions.py](code_reference/make_questions.py)"))
    add(nfig("n25-count-check", [
        "ต้องได้อย่างน้อย 500 บท และครบทั้งคำถามทั่วไปและการจองคิว 5 แบบ · รอบจริงได้ **570 บท 12 ชนิด**",
        "เงื่อนไขของคำตอบ เช่น \"ต้องมีแท็กจองที่เวลาเป็น 13:00 (เวลาหลังเปลี่ยน)\" คือ label ที่ใช้ทั้งกรองคำตอบของครูและวัดผลโมเดลเล็ก",
        "คำตอบของ AI รวมข้อความลูกค้าได้ 993 แต่ไฟล์นับได้จริง **998 ข้อความ** จึงต้องตรวจตัวเลขของ AI กับไฟล์เสมอ"],
        title="อ่านผลขั้นที่ 1: ตัวเลขในคำตอบของ AI ต้องตรวจกับไฟล์จริง"))

    # --- ขั้นที่ 2
    T2 = "เช่า RTX 5090 แล้วเปิดโมเดลครู"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 2 จาก 10 · เปิดโมเดลครู", group="ขั้นที่ 2")
    add(step_divider(2, T2, "เช่าเครื่องแรง ติดตั้ง NInfer เปิดโมเดลครู 27B แล้วลองถามจากนอกเครื่อง",
                     "RTX 5090 $0.745 ต่อชั่วโมง และใช้ VRAM 31.5 จาก 32.6 GB"))
    add(nfig("n26-step2-teacher", [
        "**เช่า RTX 5090 1 ใบ** ราคารวมไม่เกิน $1.20 ต่อชั่วโมง ป้ายเครื่อง `vapp-lab3-teacher`",
        "**ติดตั้ง NInfer** แบบเดียวกับบทที่แล้ว เปิดไฟล์ `qwen3_8_27b_nvfp4.ninfer` ให้ตอบแบบไม่แสดงขั้นคิด และใช้ API key ที่สุ่มใหม่",
        "**ลองถามจากนอกเครื่อง** แล้วเขียนค่าเชื่อมต่อไว้ที่ `lab3_qlora/teacher.env`"],
        title="ขั้นที่ 2 เช่า RTX 5090 แล้วเปิดโมเดลครู 27B ด้วย NInfer"))
    add(prompt_of(2, T2))
    add(check("step2", [
        "มีเครื่องป้าย `vapp-lab3-teacher` 1 เครื่อง เป็น RTX 5090 ราคารวมไม่เกิน $1.20 ต่อชั่วโมง",
        "โมเดลครูตอบคำถามภาษาไทยจากนอกเครื่องได้ โดยไม่แสดงขั้นคิด",
        "มีไฟล์ `lab3_qlora/teacher.env` (ที่อยู่ ชื่อโมเดล key) และไม่มีค่า key แสดงบนจอ",
        "ตารางสรุปมี GPU · ราคา · ที่ตั้ง · เวลาเปิดโมเดล · คำตอบ · VRAM และบอกว่าเครื่องยังเปิดอยู่"],
        "RTX 5090 $0.745 ต่อชั่วโมง ที่ Texas · VRAM 31.5 จาก 32.6 GB · ราว 53 token ต่อวินาที · " + took("ขั้นที่ 2 ·"),
        "ขั้นที่ 2 · " + T2,
        "ตั้งแต่ขั้นนี้ **เงินเริ่มเดิน** ให้ทำขั้นที่ 3 ต่อทันที · " + VARY))
    add(crop("ผลจริงขั้นที่ 2: โมเดลครูใช้ VRAM เกือบเต็มการ์ด 32 GB", nimg("c24-step2-table"), [
        ("ราคาที่เช่าได้", "$0.745", "ต่อชั่วโมง · RTX 5090 ที่ Texas", "warn"),
        ("VRAM ที่ใช้", "31.5 GB", "จาก 32.6 GB · การ์ด 24 GB ใช้ไม่ได้", ""),
        ("ความเร็ว", "ราว 53", "token ต่อวินาที", "")], "image/lab3-step2.png",
        cap="ส่วนหนึ่งของคำตอบจริง · ที่อยู่เครื่องในภาพเป็นค่าตัวอย่าง"))
    add(statement("อ่านผลขั้นที่ 2: เครื่องแพงต้องเปิดให้สั้นที่สุด", nimg("p22-meter"),
                  "ตั้งแต่ขั้นนี้ค่าเช่าเริ่มเดินชั่วโมงละ $0.745 จึงต้องทำขั้นที่ 3 ต่อทันที เพราะขั้นที่ 3 จะลบเครื่องนี้", [
                      "โมเดลครูใช้ VRAM 31.5 จาก 32.6 GB จึงต้องใช้ RTX 5090 และใช้การ์ด 24 GB ไม่ได้",
                      "ในรอบจริง AI เปิดไฟล์วิธีติดตั้ง NInfer ของบทที่แล้วมาดูเอง ถ้าไม่มีไฟล์นั้น AI จะอ่านจากหน้าโครงการ NInfer และอาจใช้เวลานานขึ้น",
                      "`teacher.env` มี API key และไฟล์ `.gitignore` ของ LAB กันไฟล์ `*.env` ไว้แล้ว"]))

    # --- ขั้นที่ 3
    T3 = "ให้ครูตอบ แล้วคัดเป็น Dataset"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 3 จาก 10 · ทำ Dataset", group="ขั้นที่ 3")
    add(step_divider(3, T3, "เขียน `make_dataset.py` ส่งคำถามให้ครูตอบ กรองคำตอบ แบ่งชุด ทำภาพตัวอย่าง แล้วลบเครื่องครู",
                     "ผ่าน %d จาก %d บท ได้ Training Set %d บท และ Validation Set %d บท" % (DS["passed"], DS["dialogs_total"], DS["train"], DS["val"])))
    add(nfig("n27-step3-dataset", [
        "ครูตอบทีละข้อความด้วย system prompt ข้อมูลร้าน และ temperature 0.3 แบบเดียวกับเว็บจริง",
        "ตรวจด้วยเงื่อนไขของคำตอบ ผิดให้ตอบใหม่ได้ 1 ครั้ง ยังผิดทิ้งทั้งบท แล้วแบ่ง 90/10 ด้วย seed 7",
        "สรุปผลใน `dataset_report.json` ทำภาพ `dataset_samples.jpg` แล้ว **ลบเครื่อง `vapp-lab3-teacher`** และตรวจว่าไม่เหลือ"],
        title="ขั้นที่ 3 ครูตอบทุกข้อความ คำตอบถูกตรวจและแบ่งชุด แล้วเครื่องครูถูกลบ"))
    add(prompt_of(3, T3))
    add(check("step3", [
        "มี `code/make_dataset.py` · `data/train.jsonl` · `data/val.jsonl` ในรูปแบบ messages พร้อมเงื่อนไขของคำตอบแต่ละข้อ",
        "มี `results/dataset_report.json` และ `results/dataset_samples.jpg` (6 แถวจาก Training Set + เคสทดสอบ 3 เคส)",
        "ตารางสรุปมีจำนวนต่อชนิดคำถาม และเหตุผลที่ถูกทิ้ง",
        "เครื่อง `vapp-lab3-teacher` ถูกลบ และตรวจแล้วว่าไม่เหลือ",
        "อ่านส่วน \"ทำต่างจากที่สั่ง\" ในคำตอบของ AI"],
        "%d → ผ่าน %d บท (85.1%%) · Training %d · Validation %d · ทิ้ง %d · ค่าเช่าเครื่องครู $0.33 · %s"
        % (DS["dialogs_total"], DS["passed"], DS["train"], DS["val"], DS["dropped"], took("ขั้นที่ 3 ·").split(" · ")[0]),
        "ขั้นที่ 3 · " + T3))
    add(crop("ผลจริงขั้นที่ 3: ครูที่ผ่านชุดทดสอบครบ ก็ยังตอบผิดเงื่อนไข 15% ของบท", nimg("c25-step3-summary"), [
        ("ผ่านการคัด", "%d บท" % DS["passed"], "จาก %d บท (85.1%%)" % DS["dialogs_total"], "ok"),
        ("เรียกครู", format(DS["teacher_calls"], ","), "ครั้ง ใน 6 นาที 47 วินาที", ""),
        ("ค่าเช่าเครื่องครู", "$0.33", "เปิดรวม 21 นาที · ถูกลบในขั้นนี้", "")], "image/lab3-step3.png",
        cap="ส่วนหนึ่งของคำตอบจริง: ตารางตัวเลขรวม · คำตอบเต็ม: [results/answers/3_dataset.md](results/answers/3_dataset.md)"))
    add(widex("อ่านผลขั้นที่ 3: ถ้าไม่กรองคำตอบของครู โมเดลเล็กจะเรียนคำตอบที่ผิดไปด้วย", nimg("c22-dataset-rows"), [
        "เปิด `results/dataset_samples.jpg` แล้วดูว่าคำตอบของครูตรงกับเงื่อนไขในคอลัมน์ขวาหรือไม่",
        "เครื่องครูถูกลบในขั้นนี้ เปิดรวม 21 นาที ค่าเช่า $0.33 (เวลา $0.26 + ดาวน์โหลด 25.3 GB $0.07)",
        "AI ตัดสินใจเองว่า \"1,147.50\" เป็นเลขเดียวกับ 1147.50 · การตัดสินใจแบบนี้เปลี่ยนจำนวนบทที่ผ่านได้ จึงควรอ่านส่วน \"ทำต่างจากที่สั่ง\" ทุกครั้ง"]))

    # --- ขั้นที่ 4
    T4 = "เช่า RTX 3090 เขียนโค้ดเทรน QLoRA แล้ว Training"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 4 จาก 10 · เทรน QLoRA", group="ขั้นที่ 4")
    add(step_divider(4, T4, "เช่าเครื่องราคาถูก เขียน `train.py` (และ `run.sh` สำหรับเทรนต่อเมื่อหลุด) แล้วเทรน 3 Epoch",
                     "Validation loss ลดจาก %.3f เป็น %.3f และได้ Adapter 63 MB" % (TR["val_loss_before"], TR["best_val_loss"])))
    add(nfig("n28-step4-train", [
        "เช่า **RTX 3090 1 ใบ** ราคาไม่เกิน $0.40 ต่อชั่วโมง ป้าย `vapp-lab3` และเปิดพอร์ต 8000 ไว้ให้ AI server",
        "`train.py` โหลด Qwen3-4B-Instruct-2507 แบบ 4-bit แล้วเทรน LoRA rank 8 ทุกชั้น Linear 3 Epoch โดยคิด loss เฉพาะคำตอบของผู้ช่วย",
        "วัด Validation loss ก่อนเทรนและทุก 20 step เก็บ adapter รอบที่ loss ต่ำสุด เทรนต่อได้แม้การเชื่อมต่อหลุด แล้วเก็บผลกลับมาที่ `lab3_qlora/results`"],
        title="ขั้นที่ 4 เทรน QLoRA บน RTX 3090 และเก็บ Adapter ที่ดีที่สุด"))
    add(prompt_of(4, T4))
    add(check("step4", [
        "มีเครื่องป้าย `vapp-lab3` เป็น RTX 3090 ราคาไม่เกิน $0.40 ต่อชั่วโมง",
        "`code/train.py` โหลดแบบ 4-bit เทรนเฉพาะ LoRA rank 8 และคิด loss เฉพาะคำตอบของผู้ช่วย",
        "มี Validation loss ก่อนเทรนและทุก 20 step · adapter ที่เก็บคือ step ที่ loss ต่ำสุด (ไม่จำเป็นต้องเป็น step สุดท้าย)",
        "บนเครื่องของคุณมี `results/adapter/` · `results/train_log.json` · `results/loss_curve.png`",
        "ตารางสรุปบอกว่าเครื่องยังเปิดอยู่ (ใช้ต่อในขั้นที่ 5)"],
        "$0.241 ต่อชั่วโมง · %d step ใน 35.6 นาที · Validation loss %.3f → %.3f (step %d) · VRAM ที่จองสูงสุด %.1f GB · adapter 63 MB"
        % (TR["total_steps"], TR["val_loss_before"], TR["best_val_loss"], TR["best_step"], TR["peak_vram_gb"]),
        "ขั้นที่ 4 · " + T4))
    add(crop("ผลจริงขั้นที่ 4: Validation loss ลดจาก %.3f เป็น %.3f ในเวลาเทรน 35.6 นาที" % (TR["val_loss_before"], TR["best_val_loss"]),
             nimg("c26-step4-table"), [
        ("Validation loss", "%.3f" % TR["best_val_loss"], "จาก %.3f · ต่ำสุดที่ step %d" % (TR["val_loss_before"], TR["best_step"]), "ok"),
        ("เวลาเทรน", "35.6 นาที", "%d step · RTX 3090" % TR["total_steps"], ""),
        ("VRAM สูงสุด (จอง)", "%.1f GB" % TR["peak_vram_gb"], "Adapter 63 MB", "")], "image/lab3-step4.png",
        cap="ส่วนหนึ่งของคำตอบจริง: ตารางสรุปผล · " + took("ขั้นที่ 4 ·")))
    add(fig("กราฟ loss ของรอบจริง: Adapter ที่เก็บไว้มาจาก step %d ไม่ใช่ step สุดท้าย" % TR["best_step"], "results/loss_curve.png",
            "ดูวงกลมดำบนเส้นแดง · Training loss ลงต่อถึงราว 0.12 ขณะที่ Validation loss หยุดที่ 0.31 แปลว่า **เริ่ม Overfitting** และเทรนเกิน 3 Epoch ไม่น่าได้อะไรเพิ่ม",
            tag="results/loss_curve.png"))
    add(nfig("n29-vram-reserved", [
        "**VRAM 22.9 GB เป็นค่าที่ PyTorch จองไว้** ไม่ใช่ค่าที่ใช้จริง พรอมต์ไม่ได้ระบุวิธีวัด AI จึงเลือกเอง ถ้าต้องการค่าที่ใช้จริงต้องระบุในพรอมต์",
        "ในรอบจริงคำสั่งสร้างเครื่องพิมพ์ key ของเครื่องเช่าออกจอ 1 ครั้ง · key นั้นใช้ไม่ได้อีกเมื่อลบเครื่อง แต่แสดงว่าคำสั่ง \"ห้ามแสดง key\" ยังพลาดได้",
        "โฟลเดอร์ Adapter (63 MB) อยู่ที่ `lab3_qlora/results/adapter` บนเครื่องของคุณ และไม่ได้เก็บในรีโปเพราะไฟล์ใหญ่"],
        title="อ่านผลขั้นที่ 4: ค่าที่ AI รายงานขึ้นกับวิธีวัดที่ AI เลือกเอง"))

    # --- ขั้นที่ 5
    T5 = "เปิด AI server 2 โมเดล แล้ววัดผลบน Validation Set"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 5 จาก 10 · วัดผลบน Validation Set", group="ขั้นที่ 5")
    add(step_divider(5, T5, "เขียน `serve.sh` เปิด vLLM ที่มี 2 ชื่อโมเดลบน server เดียว และ `eval_val.py` วัดทั้งสองโมเดลด้วยคำถามเดียวกัน",
                     "คำตอบที่ถูกเพิ่มจาก %s เป็น %s" % (pct(vb["correct_pct"]), pct(vf["correct_pct"]))))
    add(nfig("n03-step5-serve", [
        "`serve.sh` ให้ vLLM โหลด Base Model ครั้งเดียว แล้วลงทะเบียน Adapter เป็นชื่อโมเดลอีกชื่อ: `qwen3-4b-base` และ `qwen3-4b-sabaijai`",
        "`eval_val.py` ให้ทั้ง 2 โมเดลตอบทุกข้อความใน Validation Set ด้วยประวัติแชทเดียวกัน (temperature 0)",
        "ตรวจด้วยเงื่อนไขของคำตอบใน Dataset วัดความเร็วและ VRAM แล้วเก็บที่ `results/val_eval.json`"],
        title="ขั้นที่ 5 server เดียวมี 2 ชื่อโมเดล จึงเทียบ Base กับ Fine-tuned ได้ตรง"))
    add(prompt_of(5, T5))
    add(check("step5", [
        "`code/serve.sh` เปิด vLLM ที่พอร์ต 8000 และมี 2 ชื่อโมเดล `qwen3-4b-base` กับ `qwen3-4b-sabaijai`",
        "`lab3_qlora/chatbot.env` มีที่อยู่ key และชื่อโมเดลทั้ง 2 · ไม่มีค่า key แสดงบนจอ",
        "`results/val_eval.json` มีตัวเลข 6 ตัวของข้อ 5 ในพรอมต์ ครบทั้ง 2 โมเดล พร้อมความเร็วและ VRAM",
        "ตารางสรุปมีตัวอย่างคำถาม 2 ข้อที่สองโมเดลตอบต่างกัน",
        "ดูตัวหารของแต่ละแถว ก่อนสรุปว่าดีขึ้นหรือแย่ลง"],
        "คำตอบที่ถูก %s → %s · ใส่แท็กจองทั้งที่ข้อมูลไม่ครบ %s → %s · ความเร็ว %.1f กับ %.1f token ต่อวินาที · %s"
        % (pct(vb["correct_pct"]), pct(vf["correct_pct"]), pct(vb["booking_tag_too_early_pct"]), pct(vf["booking_tag_too_early_pct"]),
           vb["tokens_per_s_overall"], vf["tokens_per_s_overall"], took("ขั้นที่ 5 ·")),
        "ขั้นที่ 5 · " + T5))
    add(crop("ผลจริงขั้นที่ 5: Fine-tuned ตอบถูก %d จาก %d ข้อ เทียบกับ %d ข้อของ Base"
             % (round(vf["correct_pct"] * vf["n_turns"] / 100), vf["n_turns"], round(vb["correct_pct"] * vb["n_turns"] / 100)),
             nimg("c27-step5-examples"), [
        ("คำตอบที่ถูก", pct(vf["correct_pct"]), "จาก %s ของ Base · **+7 จุด**" % pct(vb["correct_pct"]), "ok"),
        ("ใส่แท็กจองทั้งที่ข้อมูลไม่ครบ", pct(vf["booking_tag_too_early_pct"]), "จาก %s (77 ข้อ)" % pct(vb["booking_tag_too_early_pct"]), "ok"),
        ("ความเร็ว", "%.1f" % vf["tokens_per_s_overall"], "token ต่อวินาที · Base %.1f" % vb["tokens_per_s_overall"], "warn")], "image/lab3-step5.png",
        cap="ส่วนหนึ่งของคำตอบจริง: 2 ข้อที่สองโมเดลตอบต่างกัน คือราคานักศึกษา (600 บาท ลด 15%) และการจองเวลา 08:00 ก่อนร้านเปิด"))
    add(tbl("Base เทียบ Fine-tuned ทีละตัววัด: แถวที่มี ↓ ยิ่งต่ำยิ่งดี", table("ขั้นที่ 5 ·", "ตัววัด"),
            post=note("**ตัวหารเล็ก**: แถวแท็กจองมี 8 ข้อ แถวภาษาอังกฤษมี 2 ข้อ · 100% → 0% จาก 2 ข้อยังสรุปอะไรไม่ได้")))
    add(nfig("n30-booking-early", [
        "คำตอบที่ถูกเพิ่มจาก 74 เป็น 80 ข้อจาก 85 ข้อ (+7 จุด) · Fine-tuned แก้ข้อที่ Base ผิดได้ 8 ข้อ แต่ **ทำผิดเพิ่ม 2 ข้อที่ Base เคยถูก** (ถามเงื่อนไขโปร 10% แล้วตอบสั้นเกินจนไม่บอกวัน)",
        "แถวที่สำคัญต่อระบบจริงคือ **ใส่แท็กจองทั้งที่ข้อมูลไม่ครบ** 6.5% → 1.3% เพราะแท็กที่ออกผิดจังหวะคือการจองปลอมในฐานข้อมูล",
        "คำถามใน Validation Set มาจากแม่แบบเดียวกับ Training Set ผลนี้จึงบอกว่าโมเดล **ตอบเหมือนครูมากขึ้นในคำถามแบบที่ครูสอน**"],
        title="อ่านผลขั้นที่ 5: Fine-tune ช่วยชัดบน Validation Set โดยเฉพาะเรื่องแท็กจอง"))

    # --- ขั้นที่ 6
    T6 = "ต่อเว็บแชทบอทเข้ากับ 2 โมเดล"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 6 จาก 10 · ต่อเว็บแชทบอท", group="ขั้นที่ 6")
    add(step_divider(6, T6, "แก้เว็บแชทบอทเดิม เพิ่มตัวเลือกโมเดล หน้า `/compare` และ API สลับโมเดลเริ่มต้น แล้วรันด้วย Docker บนเครื่องของเรา",
                     "หน้าแชท `/compare` และ `/bookings` ใช้งานได้ และจองคิวสำเร็จ 1 รายการ"))
    add(nfig("n04-step6-web", [
        "หน้าแชทเดิมเพิ่มตัวเลือกโมเดล Base / Fine-tuned ถ้าไม่เลือกจะใช้โมเดลเริ่มต้นของเว็บ ซึ่งสลับได้ขณะเว็บเปิด",
        "หน้า `/compare` รับคำถาม 1 ข้อ แล้วแสดงคำตอบ 2 โมเดลคู่กัน พร้อมเวลา token ต่อวินาที และผลตรวจแท็กจอง",
        "รันด้วย Docker Compose บน **เครื่องของเรา** project `vapp-lab3` พอร์ต 3403 โดยไม่เปลี่ยนส่วนที่ชุดทดสอบ 26 เคสใช้"],
        title="ขั้นที่ 6 เว็บแชทบอทเลือกโมเดลได้ และมีหน้าเทียบคำตอบ 2 โมเดล"))
    add(prompt_of(6, T6))
    add(check("step6", [
        "เปิดเว็บ + PostgreSQL ได้ด้วยคำสั่งเดียว · Docker Compose project `vapp-lab3` · พอร์ต 3403",
        "หน้าแชทมีตัวเลือกโมเดล Base / Fine-tuned · ไม่เลือก = ใช้โมเดลเริ่มต้นของเว็บ",
        "หน้า <http://localhost:3403/compare> แสดงคำตอบ 2 โมเดลคู่กัน พร้อมเวลา token ต่อวินาที และผลตรวจแท็กจอง",
        "จองคิว 1 รายการแล้วขึ้นในหน้า <http://localhost:3403/bookings>",
        "ไฟล์ของชุดทดสอบ 26 เคสใน `code/e2e` ไม่ถูกแก้"],
        "หน้าแชท · `/compare` · `/bookings` · `/api/model` · จองคิวของ มานี ใจดี สำเร็จ · " + took("ขั้นที่ 6 ·"),
        "ขั้นที่ 6 · " + T6))
    add(crop("หน้า /compare ของเว็บจริง: คำถามเดียวกัน Base ตอบ 460 บาท (ผิด) ส่วน Fine-tuned ตอบ 510 บาท (ถูก)",
             nimg("c32-compare-answers"), [], "results/web/demo_compare_discount.png",
             cap="ส่วนหนึ่งของหน้าเว็บจริง · ราคานักศึกษาของนวดไทย 2 ชั่วโมงคือ 600 บาท ลด 15% · ทั้งคู่ไม่มีแท็กจอง · [GIF](results/web/demo_compare_discount.gif)"))
    add(fig("จองคิวสำเร็จด้วย Fine-tuned: การ์ดจองปรากฏในแชท แล้วรายการขึ้นในหน้ารายการจอง", "results/web/demo_booking_tuned.gif",
            "GIF อื่นของเว็บจริง: [หน้าแชท Base](results/web/demo_chat_base.gif) · [Fine-tuned](results/web/demo_chat_tuned.gif) · "
            "[/compare คำถามภาษาอังกฤษ](results/web/demo_compare_english.gif)", tag="results/web/"))
    add(nfig("n31-closed-refusal", [
        "ตอน AI ลองจองคิว Fine-tuned ปฏิเสธในข้อความแรกโดยอ้างว่า \"ตอนนี้ร้านปิด\" ทั้งที่ลูกค้าขอจองพรุ่งนี้ 14:00 ต้องยืนยันอีกรอบจึงจองได้",
        "เป็นผลข้างเคียงของการเรียนให้ระวังเรื่องเวลา",
        "เว็บเปลี่ยนโมเดลด้วยค่า `model` ในคำขอเท่านั้น และหน้า `/compare` ถามทีละโมเดล การเทียบ A/B และตัวเลข token ต่อวินาทีจึงตรงกัน"],
        title="อ่านผลขั้นที่ 6: โมเดลที่เทรนแล้วก็ยังตอบผิดได้"))

    # --- ขั้นที่ 7
    T7 = "รันชุดทดสอบ 26 เคสกับทั้ง 2 โมเดล"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 7 จาก 10 · ชุดทดสอบ 26 เคส", group="ขั้นที่ 7")
    add(step_divider(7, T7, "เขียน `run-both.sh` `compare.mjs` และ `repeat.mjs` รันชุดทดสอบเดิมกับ 2 โมเดล แล้วรันซ้ำอีก 5 รอบต่อโมเดล",
                     "Base %d/%d และ Fine-tuned %d/%d · **Fine-tune ไม่ได้ทำให้ผ่านเพิ่ม**" % (eb["passed"], eb["total"], ef["passed"], ef["total"])))
    add(nfig("n05-step7-e2e", [
        "`run-both.sh` สลับโมเดลเริ่มต้นของเว็บ ล้างตารางจองกับประวัติแชท แล้วรันชุดทดสอบ 26 เคสกับ Base และ Fine-tuned",
        "`compare.mjs` ทำตารางรายเคส พร้อมคำตอบจริงของเคสที่ผลต่างกัน",
        "`repeat.mjs` รันโจทย์ 26 เคสเดิมซ้ำอีก 5 รอบต่อโมเดลผ่าน API เพื่อดูว่าผลแกว่งหรือไม่"],
        title="ขั้นที่ 7 รันชุดทดสอบ 26 เคสกับทั้ง 2 โมเดล แล้วรันซ้ำ 5 รอบ"))
    add(prompt_of(7, T7))
    add(check("step7", [
        "มี `code/e2e/run-both.sh` · `compare.mjs` · `repeat.mjs` และไฟล์เคสทดสอบเดิมไม่ถูกแก้",
        "`results/e2e/` มีตารางเทียบ · `compare.json` · `repeat.json` · รายงานของแต่ละโมเดล · GIF ของเคสที่ผลต่างกันไม่เกิน 4 เคส",
        "ตาราง 3 แถว: โมเดลใหญ่ 27B (อ้างจากบทที่แล้ว) · Base · Fine-tuned พร้อมจำนวนผ่าน ค่าเฉลี่ยรันซ้ำ 5 รอบ และเคสที่ไม่ผ่าน",
        "รายงานตามจริงแม้ Fine-tuned ไม่ดีขึ้น"],
        "Base %d/%d (ตกเคส %d) · Fine-tuned %d/%d (ตกเคส %d) · รันซ้ำ 5 รอบได้ %d ทุกรอบทั้งสองโมเดล · %s"
        % (eb["passed"], eb["total"], eb["failed_cases"][0], ef["passed"], ef["total"], ef["failed_cases"][0],
           eb["repeat"]["mean"], took("ขั้นที่ 7 ·")),
        "ขั้นที่ 7 · " + T7))
    img = E.img_tag({"t": "img", "src": nimg("c31-e2e-chart"), "alt": "กราฟชุดทดสอบ 26 เคส"})
    side = tiles([
        ("A · โมเดลครู 27B", "26/26", "**อ้างจากบทที่แล้ว ไม่ได้รันซ้ำ**", ""),
        ("B · Base", "%d/%d" % (eb["passed"], eb["total"]), "ตกเคส %d (late-time) · รันซ้ำ %s" % (eb["failed_cases"][0], ", ".join(map(str, eb["repeat"]["scores"]))), "warn"),
        ("C · Fine-tuned", "%d/%d" % (ef["passed"], ef["total"]), "ตกเคส %d (followup-2h) · รันซ้ำ %s" % (ef["failed_cases"][0], ", ".join(map(str, ef["repeat"]["scores"]))), "warn")])
    add(S("ผลจริงขั้นที่ 7: ผ่าน %d/%d เท่ากัน แต่ตกคนละเคส และตกเคสเดิมทุกรอบ" % (eb["passed"], eb["total"]),
          '<div class="ex"><div class="fig" style="flex:.8 1 0">%s</div><div class="side fitbox">%s%s</div></div>' % (
              img, side.replace('class="tiles"', 'class="tiles" style="flex-direction:column"'),
              note("ตารางรายเคสทั้ง 26 เคส: [results/e2e/COMPARE.md](results/e2e/COMPARE.md) · ภาพหน้าจอคำตอบของ AI: [image/lab3-step7.png](image/lab3-step7.png)", label="ที่มา")),
          tag="results/val_compare.png", maxfs=1.15))
    t = table("ขั้นที่ 7 ·", "เคส")
    c19, c21 = t["rows"][0], t["rows"][1]
    add(pair("เคส 19: Fine-tuned ตีความ \"อันที่ถูกกว่า\" ผิด ซึ่งเป็นความผิดจริง", "**ลูกค้าพิมพ์** " + md(c19[1]),
             ("Base ผ่าน", "results/e2e/diff-gifs/case19-followup-2h-base.gif", md(c19[2]), "ok"),
             ("Fine-tuned ไม่ผ่าน", "results/e2e/diff-gifs/case19-followup-2h-ft.gif", md(c19[3]), "bad"),
             tag="results/e2e/diff-gifs/"))
    add(pair("เคส 21: Base ตอบเนื้อหาไม่ผิด แต่ตกเพราะไม่มีเลข \"21\" ตามเกณฑ์", "**ลูกค้าพิมพ์** " + md(c21[1]),
             ("Base ไม่ผ่าน", "results/e2e/diff-gifs/case21-late-time-base.gif", md(c21[2]), "bad"),
             ("Fine-tuned ผ่าน", "results/e2e/diff-gifs/case21-late-time-ft.gif", md(c21[3]), "ok"),
             tag="results/e2e/diff-gifs/"))
    add(explain("อ่านผลขั้นที่ 7: สองโมเดลใกล้กันเกินกว่าที่ชุดทดสอบ 26 เคสจะตัดสินได้", "image/t3-eval-rulers.png", [
        "**Fine-tune ไม่ได้ทำให้ผ่านเพิ่มบนชุดทดสอบนี้**: ได้เคส 21 มา แต่เสียเคส 19 ที่ Base ทำได้ ผลรวมเท่าเดิมที่ 25/26",
        "**ไม่ใช่ความบังเอิญของ temperature**: รันซ้ำ 5 รอบ แต่ละโมเดลตกเคสเดิมทุกรอบ",
        "1 เคสมีน้ำหนัก 3.8% และ Base ผ่าน 25 เคสแล้ว จึงเหลือที่ให้ดีขึ้นเพียง 1 เคส · ผ่านเทสต์แบบจับคำไม่เท่ากับตอบถูก และตกไม่เท่ากับตอบผิด"]))
    add(nfig("n32-what-ft-taught", [
        "Fine-tune ทำให้โมเดลเล็กตอบเหมือนครูมากขึ้นในเรื่องที่ Dataset สอน คือลีลา รูปแบบ และความระวังเรื่องการจอง",
        "ไม่ได้ทำให้เก่งขึ้นในเรื่องที่ Dataset ไม่ได้เน้น เช่น การตีความคำอ้างอิงข้ามข้อความ (เคส 19)",
        "โมเดลเล็ก 4B ผ่าน 25/26 ตั้งแต่ยังไม่เทรน บนเครื่องที่ถูกกว่าราว 3.1 เท่า แต่ยังไม่เท่า 26/26 ของโมเดลใหญ่ที่อ้างจากบทที่แล้ว จึง **ยังสรุปไม่ได้ว่าแทนกันได้**"],
        title="ข้อสรุปที่ตรงกับหลักฐาน: Fine-tune ทำให้ตอบเหมือนครูมากขึ้น แต่ไม่ได้เก่งขึ้นทุกเรื่อง"))

    # --- ขั้นที่ 8
    T8 = "ลบเครื่อง ปิดเว็บ สรุปค่าใช้จ่าย"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 8 จาก 10 · ปิดงาน", group="ขั้นที่ 8")
    add(step_divider(8, T8, "จดข้อมูลเครื่อง ลบเครื่อง ปิดเว็บ และตรวจว่าไฟล์ของทุกขั้นกลับมาอยู่บนเครื่องของเราครบ · **ห้ามข้ามขั้นนี้**",
                     "ไม่มีเครื่องค้าง และค่าเช่ารวมขั้นที่ 1–8 คือ $%.2f" % COST["total_official_round"]))
    add(nfig("n06-step8-cleanup", [
        "จดข้อมูลเครื่องป้าย `vapp-lab3*` ก่อนลบ ได้แก่ GPU ราคาต่อชั่วโมง เวลาที่เปิด และปริมาณดาวน์โหลด",
        "ลบทุกเครื่องที่ป้ายขึ้นต้นด้วย `vapp-lab3` แล้วตรวจว่าไม่เหลือ โดยไม่แตะเครื่องป้ายอื่น และปิดเว็บบนเครื่องของเรา",
        "ไฟล์ที่ยังอยู่แค่ใน container ให้คัดลอกกลับมา แล้วสรุปค่าเช่า (ราคาต่อชั่วโมง × ชั่วโมง + ค่าดาวน์โหลด)"],
        title="ขั้นที่ 8 ลบเครื่อง ปิดเว็บ และเก็บไฟล์ให้ครบ"))
    add(prompt_of(8, T8))
    add(check("step8", [
        "ไม่มีเครื่องป้าย `vapp-lab3*` เหลือ (ตรวจด้วยคำสั่งค้นเครื่อง ไม่ใช่ดูจากคำตอบอย่างเดียว)",
        "เว็บที่พอร์ต 3403 ปิดแล้ว",
        "โค้ดใน `lab3_qlora/code` และผลใน `lab3_qlora/results` อยู่บนเครื่องของคุณครบทุกขั้น",
        "ตารางค่าเช่า (ราคาต่อชั่วโมง × ชั่วโมง + ค่าดาวน์โหลด) และเทียบราคา RTX 3090 กับ RTX 5090"],
        "เครื่องครู $0.33 + เครื่องนักเรียน $0.36 = $%.2f · ไม่มีเครื่องค้าง · %s" % (COST["total_official_round"], took("ขั้นที่ 8 ·")),
        "ขั้นที่ 8 · " + T8))
    t = table("ขั้นที่ 8 ·", "เครื่อง")
    add(crop("ผลจริงขั้นที่ 8: เครื่องแพงเปิดสั้นที่สุด และค่าเช่ารวมคือ $%.2f" % COST["total_official_round"], nimg("c28-step8-table"), [
        ("%s · %s" % (md(t["rows"][0][0]), t["rows"][0][1]), t["rows"][0][4].split("= ")[-1].replace("**", ""),
         "%s ต่อชั่วโมง · เปิด %s" % (t["rows"][0][2], t["rows"][0][3]), ""),
        ("%s · %s" % (md(t["rows"][1][0]), t["rows"][1][1]), t["rows"][1][4].split("= ")[-1].replace("**", ""),
         "%s ต่อชั่วโมง · เปิด %s" % (t["rows"][1][2], t["rows"][1][3]), ""),
        ("รวมขั้นที่ 1–8", t["rows"][2][4].replace("**", ""), "ไม่มีเครื่องค้าง", "ok")], "image/lab3-step8.png",
        cap="ส่วนหนึ่งของคำตอบจริง: ค่าเช่าของเครื่อง `vapp-lab3` (เครื่องครูถูกลบไปแล้วในขั้นที่ 3)"))
    add(S("อ่านผลขั้นที่ 8: เทรนจริง 35.6 นาที แต่เครื่องนักเรียนเปิด 84 นาที",
          bars([("RTX 5090 · เครื่องครู", "เปิดเฉพาะตอนที่ครูต้องตอบ (ขั้นที่ 2–3)", 21, 84, "21 นาที"),
                ("RTX 3090 · เครื่องนักเรียน", "ขั้นที่ 4–5 และ 7", 84, 84, "84 นาที"),
                ("ในจำนวนนั้นเป็นการเทรนจริง", "ขั้นที่ 4", 35.6, 84, "35.6 นาที")])
          + note("เวลาที่เหลือของเครื่องนักเรียนคือการติดตั้ง โหลดโมเดล เปิด server วัดผล และรันชุดทดสอบ · "
                 "ในรอบจริงไฟล์ของขั้นที่ 4–5 บางส่วนยังอยู่แค่ใน container และขั้นนี้คัดลอกกลับมาให้", label="อ่านแผนภาพ"),
          tag="README · ขั้นที่ 8"))

    # ===== 3 · สกิล v0
    CTX.update(kicker="", group="ปิดท้าย · สกิล v0")
    add(part_divider(3, "สกิลเวอร์ชัน 0", "เก็บงานทั้ง LAB ไว้ทำซ้ำในคำสั่งเดียว",
                     "ถ้าต้องทำซ้ำ เช่น เปลี่ยนจำนวน Epoch ไม่ควรต้องวาง 8 พรอมต์ใหม่ · สกิลเก็บวิธีทำงานที่สำเร็จแล้วพร้อมโค้ดที่ใช้ได้จริง",
                     nimg("p23-skill")))
    CTX.update(kicker="สกิลเวอร์ชัน 0", group="ปิดท้าย · สกิล v0")
    add(fig("จากพรอมต์ทีละขั้นสู่สกิลเวอร์ชัน 0 ที่ทำซ้ำได้ในคำสั่งเดียว", "image/skill-v0.png",
            "ภาพแสดงตัวอย่าง 7 พรอมต์ · LAB นี้มีงานหลัก **8 พรอมต์**"))
    T9 = "สรุป LAB เป็นสกิลเวอร์ชัน 0"
    CTX.update(kicker="สกิลเวอร์ชัน 0 · ขั้นที่ 9 จาก 10 · สร้างสกิล", group="ขั้นที่ 9")
    add(step_divider(9, T9, "AI อ่านพรอมต์ โค้ด และผลของ LAB แล้วเขียน `SKILL.md` พร้อมคัดลอกโค้ดที่ใช้ได้แล้วเข้าไปในสกิล",
                     "สกิล `qlora-chatbot-tune` · [skill_v0/SKILL.md](skill_v0/SKILL.md)"))
    add(prompt_of(9, T9))
    add(check("step9", [
        "`lab3_qlora/skill_v0/SKILL.md` มี name · description (ใช้เมื่อไร) · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน",
        "สกิลบอกค่าที่ปรับได้ครบพร้อมค่าเริ่มต้น: GPU · เพดานราคา · ป้ายเครื่อง · โมเดลตั้งต้น · จำนวน Epoch · Dataset ใหม่หรือเดิม · เปิดเว็บหรือไม่",
        "`lab3_qlora/skill_v0/scripts/` มีโค้ดที่ใช้ได้แล้วจาก `lab3_qlora/code`",
        "ติดตั้งที่ `.claude/skills/qlora-chatbot-tune` แล้วปิดและเปิด Claude Code ใหม่ 1 ครั้ง"],
        "SKILL.md 94 บรรทัด + โค้ดใน `skill_v0/scripts/` · " + took("ขั้นที่ 9 ·").split(" · สกิลที่ได้")[0],
        "ขั้นที่ 9 · " + T9,
        "หลังขั้นนี้ให้ **ปิดแล้วเปิด Claude Code ใหม่ 1 ครั้ง** สกิลที่เพิ่งติดตั้งจึงถูกมองเห็น · ถ้า AI ตอบว่าไม่รู้จักสกิล ให้เปิดใหม่อีกครั้ง"))
    add(crop("ผลจริงขั้นที่ 9: สกิล qlora-chatbot-tune มีลำดับงาน 5 ช่วง พร้อมค่าที่ปรับได้", nimg("c29-step9-skill"), [
        ("SKILL.md", "94", "บรรทัด · มีกติกาเรื่องเงิน", "ok"),
        ("โค้ดในสกิล", "scripts/", "คัดลอกจาก `lab3_qlora/code`", ""),
        ("เวลา", "3.5 นาที", "ไม่ต้องเช่าเครื่อง", "")], "image/lab3-step9.png",
        cap="ส่วนหนึ่งของคำตอบจริง: สกิลทำอะไรได้ · สกิลที่ได้: [skill_v0/SKILL.md](skill_v0/SKILL.md)"))

    T10 = "ลองใช้สกิลเวอร์ชัน 0"
    CTX.update(kicker="สกิลเวอร์ชัน 0 · ขั้นที่ 10 จาก 10 · ลองใช้สกิล", group="ขั้นที่ 10")
    add(step_divider(10, T10, "AI ตัวใหม่ได้คำสั่ง 3 บรรทัด แล้วเช่าเครื่อง เทรน 1 Epoch เปิด server วัดผล และลบเครื่องเอง โดยใช้โค้ดในสกิล",
                     "ผ่านในรอบแรก แต่ 1 Epoch ได้คำตอบที่ถูกเพียง 84.7% → 85.9%"))
    add(prompt_of(10, T10))
    add(check("step10", [
        "เครื่องป้าย `vapp-lab3-skill` ราคาไม่เกิน $0.40 ต่อชั่วโมง ถูกสร้าง แล้วถูกลบเมื่อจบงาน",
        "AI ใช้โค้ดใน `scripts/` ของสกิล ไม่เขียนโค้ดใหม่ · ไม่เปิดโมเดลครูและเว็บ",
        "`lab3_qlora/results/skill_test/` มีผลวัด Base เทียบ Fine-tuned บน Validation Set",
        "ตารางสรุปมีผลก่อนและหลัง · เวลาที่ใช้ · ค่าใช้จ่าย และยืนยันว่าเครื่องถูกลบแล้ว"],
        "Base 84.7% → Fine-tuned 85.9% · Validation loss 1.004 → 0.382 · เครื่องเปิด 73.6 นาที · รวมประมาณ $0.29",
        "ขั้นที่ 10 · " + T10))
    add(crop("ผลจริงขั้นที่ 10: คำสั่งเดียวแทน 3 พรอมต์ได้ แต่ 1 Epoch ยังไม่พอ", nimg("c30-step10-table"), [
        ("คำตอบที่ถูก (1 Epoch)", "85.9%", "จาก Base 84.7% · เพิ่ม 1.2 จุด", "warn"),
        ("Validation loss", "0.382", "จาก 1.004 · ยังลงอยู่ตอนจบ", ""),
        ("เครื่องเปิด", "73.6 นาที", "รวมประมาณ $0.29", "")], "image/lab3-step10.png",
        cap="ส่วนหนึ่งของคำตอบจริง: ผลก่อนและหลังเทรน · ผลอยู่ที่ [results/skill_test/](results/skill_test/)"))
    add(tbl("สั่งทีละขั้นเทียบกับสกิล v0: คำสั่งน้อยลง แต่ไม่ได้เร็วกว่า", table("ขั้นที่ 10 ·", "")))
    add(nfig("n33-same-round", [
        "สกิล v0 **ผ่านในรอบแรก** แทน 3 พรอมต์ด้วยคำสั่งเดียว แต่ **ไม่ได้เร็วกว่า** เพราะเจอปัญหาใหม่ 3 จุด",
        "**1 Epoch ยังไม่พอ**: คำตอบที่ถูกเพิ่มเพียง 1.2 จุด เทียบกับ 7 จุดของ 3 Epoch และ Validation loss ยังลงอยู่ตอนจบ",
        "Base ของสองรอบได้ 87.1% กับ 84.7% ทั้งที่เป็นโมเดลเดียวกัน จึงต้องเทียบ Base กับ Fine-tuned **ในรอบเดียวกัน**"],
        post=note("เวลา 23 จาก 74 นาทีหมดไปกับการดึงไฟล์กลับจากเครื่องที่อัปโหลดช้า และค่าเช่าเดินตลอดเวลานั้น", label="เวลา"),
        title="อ่านผลขั้นที่ 10: เทียบ Base กับ Fine-tuned ในรอบเดียวกันเสมอ"))
    t = table("ขั้นที่ 10 ·", "จุดที่ v0")
    add(explain("สกิล v0 ยังไม่สมบูรณ์: 5 จุดที่ควรแก้ในเวอร์ชัน 1", nimg("n34-v0-fixes"),
                ["%s<br>**v1:** %s" % (r[0], r[1]) for r in t["rows"]]))

    # ===== 4 · สรุป
    CTX.update(kicker="", group="สรุป")
    add(part_divider(4, "สรุป", "โมเดลเล็กถูกกว่าราว 3.1 เท่า และผ่าน 25/26 ตั้งแต่ยังไม่เทรน",
                     "Fine-tune ช่วยบน Validation Set แต่ไม่ได้ทำให้ผ่านชุดทดสอบเพิ่ม", nimg("p24-summary")))
    CTX.update(kicker="สรุป", group="สรุป")
    add(fig("ผลรวม: ชุดทดสอบแยกสองโมเดลไม่ออก แต่ Validation Set เห็นความต่าง 7 จุด", "results/val_compare.png",
            "ดูแผงขวา · คำตอบที่ถูก %s → %s · ใส่แท็กจองเร็วเกิน %s → %s · ลงท้าย \"ครับ\" %s → %s"
            % (pct(vb["correct_pct"]), pct(vf["correct_pct"]), pct(vb["booking_tag_too_early_pct"]), pct(vf["booking_tag_too_early_pct"]),
               pct(vb["ends_with_krub_pct"]), pct(vf["ends_with_krub_pct"])), tag="results/val_compare.png"))
    add(tbl("ตารางสรุป 3 แขน: ชุดทดสอบ 26 เคสบนเว็บจริง", table("ขั้นที่ 7 ·", "แขน"),
            post=note("แขน A เป็นผลที่ **อ้างจากบทที่แล้ว ไม่ได้รันซ้ำ** · B และ C อยู่บน server เดียวกัน เว็บเดียวกัน prompt เดียวกัน")))
    add(fig("สิ่งที่ได้เรียนจาก LAB นี้มี 6 ข้อ และทุกข้อมาจากผลของรอบจริง", nimg("n35-lessons"),
            "ครูตอบผิดจนถูกทิ้ง 85 จาก 570 บท (15%) · ชุดทดสอบ 1 เคสมีน้ำหนัก 3.8% · AI รายงาน 993 ข้อความ แต่ไฟล์มี 998 ข้อความ · "
            "เก็บ Adapter ที่ Validation loss ต่ำสุด และลบเครื่องทุกครั้งที่จบงาน"))
    add(S("ข้อจำกัด: สิ่งที่ LAB นี้ยังสรุปไม่ได้ หรือยังไม่ผ่าน", cards([
        ("Fine-tune ไม่ได้ทำให้ผ่านเพิ่ม", "ชุดทดสอบ 26 เคส: Base 25/26 และ Fine-tuned 25/26 โดยได้เคส 21 แต่เสียเคส 19", "bad"),
        ("ยังแทนโมเดลใหญ่ไม่ได้เต็มตัว", "ยังไม่เท่า 26/26 ของโมเดลใหญ่ที่อ้างจากบทที่แล้ว และ LAB นี้ไม่ได้รันโมเดลใหญ่ซ้ำ", "bad"),
        ("Validation Set มาจากแม่แบบเดียวกับ Training Set", "บอกได้ว่าตอบเหมือนครูมากขึ้นในคำถามแบบที่ครูสอน ไม่ใช่คำถามทุกแบบ", "warn"),
        ("ตัวหารเล็ก", "แถวแท็กจองมี 8 ข้อ ภาษาอังกฤษ 2 ข้อ และ Validation Set 48 บท บางชนิดเหลือ 1–2 บท", "warn"),
        ("สกิล v0 ยังไม่สมบูรณ์", "ไม่ตรึงเวอร์ชันไลบรารี เลือกเครื่องจากราคาอย่างเดียว และ 1 Epoch ยังไม่พอ", "warn"),
        ("`POST /api/reset` ไม่มีการป้องกัน", "AI เพิ่มไว้ล้างตารางก่อนแต่ละรอบ เว็บที่ใช้งานจริงไม่ควรมีช่องทางนี้", "warn")], 3), cls="mid"))
    CTX.update(kicker="", group="จบ")
    add(E.divider("จบ LAB 3", "รายละเอียดเต็มของทุกขั้นอยู่ใน README",
                  '<p>อ่านต่อ: <a href="README.md" target="_blank">README.md</a> · พรอมต์ทั้ง 10 ขั้น: '
                  '<a href="PROMPTS.md" target="_blank">PROMPTS.md</a> · กลับ <a href="../README.md" target="_blank">หน้ารวมของบท</a></p>'))
    return E.SL


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
