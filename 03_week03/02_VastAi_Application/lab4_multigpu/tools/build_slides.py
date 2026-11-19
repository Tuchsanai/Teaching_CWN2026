#!/usr/bin/env python3
"""สร้างสไลด์ LAB4_MultiGPU_Slides.html ของ LAB 4 (1 GPU เทียบ 2 GPU)

  python tools/build_slides.py            (รันจากโฟลเดอร์ของบท lab4_multigpu)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · นำด้วยภาพ กราฟ หรือแผนภาพพร้อมขั้นตอน · มีตารางเฉพาะจุดที่ต้องโฟกัส
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง พรอมต์ และข้อความ "อ่านผลอย่างไร": อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ตัวเลขผล: results/metrics.json (รอบทีละขั้น) และตาราง/ข้อความของ README.md
- แผนภาพ 4 ชิ้น (label · การทดลอง · ทางเชื่อม · เงินเดิน) วาดเป็น HTML จากตัวเลขของ README
  ถ้ามีภาพการ์ตูน img/<ชื่อ>.jpg ของ tools/slides_figures.py อยู่ จะใช้ภาพนั้นแทนแผนภาพ
- ท้ายไฟล์ตรวจว่าตัวเลขทุกตัวในสไลด์มีอยู่ใน README.md หรือไฟล์ผล
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
OUT, TITLE = "LAB4_MultiGPU_Slides.html", "LAB 4 · 1 GPU เทียบ 2 GPU · Slides"
README = E.read("README.md")
M = json.loads(E.read("results/metrics.json"))
R1, R2 = M["rows"]


def rx(pattern, text=README):
    """ค่าจากข้อความของ README (กลุ่มแรกของ regex) · ไม่พบ = หยุดสร้าง"""
    m = re.search(pattern, text)
    if not m:
        raise KeyError("ไม่พบ %r ใน README" % pattern)
    return m.group(1)


def f1(x):
    return "%.1f" % x


# ------------------------------------------------------------------ ตัวช่วยอ่าน README
def first_p(prefix):
    return " ".join(next(b for b in sec(prefix) if b["t"] == "p")["lines"])


def minutes(prefix):
    """เวลาที่ใช้ของขั้น จากบรรทัด *ใช้เวลา ...* ใต้ภาพของขั้นนั้น"""
    return rx(r"ใช้เวลา (\d+) นาที", " ".join(para(prefix, "*ใช้เวลา")["lines"]))


def reading(prefix):
    """รายการ "อ่านผลอย่างไร" ของหัวข้อ"""
    bl = sec(prefix)
    for k, b in enumerate(bl):
        if b["t"] == "p" and b["lines"][0] == "**อ่านผลอย่างไร**":
            return bl[k + 1]["items"]
    raise KeyError("ไม่พบ อ่านผลอย่างไร ในหัวข้อ %r" % prefix)


def ul_after(prefix, start):
    bl = sec(prefix)
    for k, b in enumerate(bl):
        if b["t"] == "p" and b["lines"][0].startswith(start):
            return bl[k + 1]["items"]
    raise KeyError(start)


def steps_html(items):
    return "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(items))


def points(title, items, pre="", post=""):
    """สไลด์ข้อสังเกตเรียงเลข (ใช้กับ "อ่านผลอย่างไร")"""
    return S(title, pre + '<div class="plist">%s</div>' % steps_html(items) + post, cls="mid", maxfs=1.35)


def figrow(title, srcs, cap):
    figs = "".join('<div class="fig">%s</div>' % E.img_tag({"src": s, "alt": plain_alt(s)}) for s in srcs)
    return S(title, '<div class="figrow">%s</div><p class="cap">%s</p>' % (figs, md(cap)), maxfs=1.1)


def plain_alt(src):
    for b in walk([x for s in SECS for x in s["blocks"]]):
        if b["t"] == "table":
            for r in b["rows"]:
                for c in r:
                    m = re.search(r"!\[(.*?)\]\(%s\)" % re.escape(src), c)
                    if m:
                        return m.group(1)
        if b["t"] == "img" and b["src"] == src:
            return b["alt"]
    return src


# ------------------------------------------------------------------ แผนภาพ HTML (แทนภาพการ์ตูนเมื่อยังไม่มีไฟล์ภาพ)
CSS = """<style>
.plist{display:flex;flex-direction:column;gap:.55em}
.dg{flex:1.5 1 0;min-width:0;display:flex;flex-direction:column;justify-content:center;gap:.6em;background:#fbf8f1;border:1px solid var(--line);border-radius:14px;padding:.8em 1em}
.dg .hd{font-weight:700;color:var(--navy);text-align:center;font-size:1.05em}
.lbl5{display:flex;justify-content:center;gap:.35em;font-family:var(--mono);font-size:1.25em;font-weight:600}
.lbl5 span{padding:.2em .45em;border-radius:8px;color:#fff}
.lb1{background:#0f8f8c}.lb2{background:#e87f1c}.lb3{background:#6d4bb3}
.lrow{display:flex;gap:.8em;align-items:center;justify-content:center}
.lrow svg{flex:none;width:15em;height:15.8em}
.lmean{display:flex;flex-direction:column;gap:.45em;font-size:.9em}
.lmean div{border-left:6px solid;padding:.25em .6em;background:#fff;border-radius:8px}
.ab{display:flex;gap:.8em;align-items:stretch}
.lane{flex:1;background:#fff;border:2px solid var(--line);border-radius:12px;padding:.5em .6em;display:flex;flex-direction:column;gap:.4em;align-items:center}
.lane h5{margin:0;font-size:1em;color:var(--navy)}
.gpus{display:flex;gap:.4em}
.gpu{width:4.2em;height:2.6em;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.78em;color:#fff;background:#0f8f8c}
.gpu.off{background:#cfd6df;color:#7b8794}
.lock{flex:1.15;background:#fff7ec;border:2px dashed #e87f1c;border-radius:12px;padding:.5em .7em;font-size:.84em;line-height:1.5}
.lock b{color:#e87f1c}
.ladder{display:flex;flex-direction:column;gap:.35em}
.rung{display:flex;align-items:center;gap:.7em;background:#fff;border-radius:10px;padding:.35em .7em;border-left:10px solid}
.rung code{font-size:1em;min-width:6.5em}
.rung .me{margin-left:auto;background:var(--navy);color:#fff;border-radius:8px;padding:.1em .6em;font-size:.8em;font-weight:700;white-space:nowrap}
.rung.hit{outline:3px solid var(--navy)}
.arrowv{font-size:.8em;color:var(--muted);text-align:center}
.tl{display:flex;height:3.4em;border-radius:10px;overflow:hidden;border:2px solid var(--navy)}
.tl div{display:flex;align-items:center;justify-content:center;font-size:.72em;font-weight:700;color:#fff;border-right:2px solid #fff;text-align:center;line-height:1.2;min-width:0}
.tl .trn{background:#0f8f8c}.tl .oth{background:#7b93b8}.tl .gap{background:#cfd6df;color:#4a5668}
.meter{display:flex;justify-content:space-between;font-size:.85em;color:var(--muted)}
.meter b{color:#c92a2a}
.tl div{font-size:1em}
.tlleg{display:grid;grid-template-columns:1fr 1fr;gap:.25em .9em;font-size:.82em;line-height:1.4}
.tlleg b{display:inline-block;min-width:1.4em;color:var(--navy)}
</style>"""
CSS_DONE = [False]


def css():
    if CSS_DONE[0]:
        return ""
    CSS_DONE[0] = True
    return CSS


def diagram_label():
    raw = rx(r"\n`(1 [0-9. ]+)`\n")
    c, x, y, w, h = raw.split()
    X, Y, W_, H_ = (float(v) for v in (x, y, w, h))
    size = rx(r"ทุกภาพ (\d+) × \d+")
    t = table("รู้จัก Dataset", "ช่อง")
    px = 200.0
    svg = ('<svg viewBox="-12 -12 224 236"><rect x="0" y="0" width="200" height="200" fill="#e9eef5" stroke="#12305e" stroke-width="2"/>'
           '<line x1="%.1f" y1="0" x2="%.1f" y2="200" stroke="#e87f1c" stroke-dasharray="4 3"/>'
           '<line x1="0" y1="%.1f" x2="200" y2="%.1f" stroke="#e87f1c" stroke-dasharray="4 3"/>'
           '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#15803d" stroke-width="3"/>'
           '<circle cx="%.1f" cy="%.1f" r="4" fill="#e87f1c"/>'
           '<text x="100" y="214" font-size="11" text-anchor="middle" fill="#12305e">ภาพ %s × %s px</text></svg>') % (
        X * px, X * px, Y * px, Y * px, (X - W_ / 2) * px, (Y - H_ / 2) * px, W_ * px, H_ * px, X * px, Y * px, size, size)
    mean = "".join('<div style="border-color:%s"><b>ช่อง %s</b> · %s</div>' % (col, r[0], md(r[2])) for r, col in zip(t["rows"], ("#0f8f8c", "#e87f1c", "#6d4bb3")))
    return ('<div class="dg"><div class="hd">label 1 บรรทัด = 1 กรอบ</div>'
            '<div class="lbl5"><span class="lb1">%s</span><span class="lb2">%s %s</span><span class="lb3">%s %s</span></div>'
            '<div class="lrow">%s<div class="lmean">%s</div></div></div>') % (c, x, y, w, h, svg, mean)


def diagram_experiment():
    t = {r[0]: r[1] for r in table("การทดลอง", "หัวข้อ")["rows"]}
    fixed = t["ค่าที่ตรึงไว้"]
    lane = lambda name, sub, on2: ('<div class="lane"><h5>%s</h5><div class="gpus"><div class="gpu">GPU 0</div><div class="gpu%s">GPU 1</div></div>'
                                   '<div style="font-size:.8em;text-align:center">%s</div></div>') % (name, "" if on2 else " off", md(sub))
    return ('<div class="dg"><div class="hd">เครื่องเดียวกัน · RTX 3090 2 ใบ</div><div class="ab">%s<div class="lock"><b>ค่าที่ตรึงไว้</b><br>%s</div>%s</div>'
            '</div>') % (lane("A · GPU 1 ใบ", "อีกใบว่าง", False), md(fixed), lane("B · GPU 2 ใบ", "DDP", True))


def diagram_topology():
    t = table("3 · ทำไม Scaling", "ค่า")
    cols = ("#15803d", "#7cb342", "#e87f1c", "#c92a2a")
    rows = []
    for r, col in zip(t["rows"], cols):
        hit = "PHB" in r[0]
        txt = r[1].replace(" · **เครื่องใน LAB นี้**", "")
        rows.append('<div class="rung%s" style="border-color:%s">%s<span>%s</span>%s</div>' % (
            " hit" if hit else "", col, md(r[0]), md(txt), '<span class="me">เครื่องใน LAB นี้</span>' if hit else ""))
    return ('<div class="dg"><div class="hd">ค่าที่คำสั่ง <code>nvidia-smi topo -m</code> รายงาน</div><div class="arrowv">ดี (เร็ว)</div><div class="ladder">%s</div>'
            '<div class="arrowv">แย่ (ช้า)</div></div>') % "".join(rows)


def diagram_meter():
    names = ["1 เช่า", "2 Dataset", "3 bench + 1 GPU", "4 2 GPU", "5 รายงาน", "6 ลบ"]
    mins = [int(minutes("ขั้นที่ %d" % k)) for k in range(1, 7)]
    opened = float(rx(r"เครื่องเปิด ([\d.]+) นาที"))
    price = rx(r"ชั่วโมงละ (\$[\d.]+)")
    cells = "".join('<div class="oth" style="flex:%d">%s</div>' % (m, n.split()[0]) for n, m in zip(names, mins))
    gap = opened - sum(mins)
    cells += '<div class="gap" style="flex:%.1f">อื่น ๆ</div>' % gap
    legend = "".join('<div><b>%s</b> %s · %d นาที</div>' % (n.split()[0], n.split(" ", 1)[1], m) for n, m in zip(names, mins))
    return ('<div class="dg"><div class="hd">เครื่องเปิด %s นาที · เงินเดินชั่วโมงละ %s ตลอดแถบ</div><div class="tl">%s</div>'
            '<div class="meter"><span>เช่าเครื่อง → <b>เริ่มคิดเงิน</b></span><span><b>หยุดคิดเงิน</b> ← ลบเครื่อง</span></div>'
            '<div class="tlleg">%s<div><b>อื่น ๆ</b> เวลาที่เครื่องเปิด นอกเวลาของ 6 ขั้น</div></div>'
            '</div>') % (rx(r"เครื่องเปิด ([\d.]+) นาที"), price, cells, legend)


DIAGRAMS = {"n01-label": diagram_label, "n02-experiment": diagram_experiment, "n03-topology": diagram_topology, "n04-meter": diagram_meter}


def nfig(key, steps=None, title=None):
    """ภาพใหม่ + ขั้นตอน · ถ้ายังไม่มีไฟล์ภาพ ใช้แผนภาพ HTML ของหัวข้อนั้นแทน"""
    f = FIG[key]
    steps = steps or f["steps"]
    title = title or f["title"]
    src = "img/%s.jpg" % key
    if os.path.exists(os.path.join(E.ROOT, src)):
        return explain(title, src, steps)
    return S(title, css() + '<div class="ex">%s<div class="side fitbox">%s</div></div>' % (DIAGRAMS[key](), steps_html(steps)), maxfs=1.2)


# ------------------------------------------------------------------ ส่วนของ LAB แต่ละขั้น
STEP = {
    1: dict(
        what=["เช่า RTX 3090 **2 ใบในเครื่องเดียว** ราคารวมไม่เกิน $0.60 ต่อชั่วโมง · ป้าย `vapp-lab4`",
              "เลือกเครื่อง verified ต่อ SSH ได้ตรง CPU 16 cores ขึ้นไป ไม่อยู่ในจีน แล้วเอา **เครื่องที่ถูกที่สุด**",
              "image PyTorch 2.8 ที่มี CUDA 12.8 · disk 60 GB",
              "รอจนเข้าไปเห็น GPU ครบ 2 ใบ · เกิน 10 นาทียังไม่พร้อม ให้ลบแล้วเช่าเครื่องอื่น",
              "รายงานว่า **GPU ต่อถึงกันแบบไหน** (NVLink หรือ PCIe และข้าม CPU socket ไหม)"],
        check=["ได้เครื่องป้าย `vapp-lab4` ที่มี RTX 3090 **2 ใบในเครื่องเดียว** ราคาไม่เกิน $0.60 ต่อชั่วโมง",
               "AI เข้าเครื่องแล้วเห็น GPU ครบ 2 ใบ",
               "ตารางสรุปมีครบ: GPU · ราคาต่อชั่วโมง · ที่ตั้ง · CPU cores · GPU ต่อถึงกันแบบไหน",
               "รู้ว่าเครื่องของคุณมี NVLink หรือไม่ และ 2 ใบอยู่ CPU socket เดียวกันหรือไม่",
               "AI บอกว่าเครื่องยังเปิดอยู่"],
        ref="ผลของผู้สอน: RTX 3090 2 ใบ · %s/ชม. · %s · 32 cores · `PHB` ไม่มี NVLink · อยู่ CPU socket เดียวกัน" % (
            "$%.3f" % M["prices"]["rented"]["usd_per_hour"], M["prices"]["rented"]["geolocation"].split(",")[0]),
        note="เครื่อง ราคา และที่ตั้งของคุณอาจต่างจากของผู้สอน ขึ้นกับข้อเสนอในตลาดตอนที่เช่า · ทางเชื่อมของเครื่องที่ได้จะกำหนดว่า 2 GPU เร็วขึ้นได้แค่ไหน"),
    2: dict(
        what=["ติดตั้ง `ultralytics` และ `roboflow` บนเครื่องเช่า",
              "ดาวน์โหลด hard-hat-workers รุ่น 13 ของ joseph-nelson ในรูปแบบ YOLO",
              "ใช้ `ROBOFLOW_API_KEY` จาก `.env` · **ห้ามแสดงค่า key และห้ามทิ้ง key ไว้บนเครื่องเช่า**",
              "เขียน `code/show_samples.py` ทำภาพตัวอย่าง 8 รูป วาดกรอบจาก label จริง → `results/dataset_samples.jpg`",
              "สรุปจำนวนภาพ จำนวนกรอบของแต่ละคลาส ขนาด Dataset และยก label จริง 1 บรรทัด"],
        check=None, ref=None,
        note="จำนวนภาพควรตรงกับของผู้สอนเพราะเป็น Dataset รุ่นเดียวกัน · ภาษาของคำตอบอาจต่างได้ (รอบจริง AI ตอบเป็นภาษาอังกฤษ เนื้อหาเหมือนกัน)"),
    3: dict(
        what=["เขียน `code/bench.py` สคริปต์เดียว รับจำนวน GPU (1 หรือ 2) แล้วเทรน `yolo11m`",
              "ค่าเดียวกันทุกรอบ: 5 Epoch · ภาพ 640 · batch 32 ภาพต่อ GPU · seed 0 · วัด Validation ครั้งเดียวตอนจบ",
              "บันทึกผลรอบละ 1 ไฟล์ JSON: วินาทีต่อ Epoch · วินาทีต่อ step · mAP50 · GPU util · CPU ที่ใช้จริง",
              "ถ้าใช้ 2 GPU วัดเวลา **all-reduce** ของ gradient 80 MB เพิ่ม",
              "ลองรันสั้น (ภาพ 5% 2 Epoch) ทั้ง 1 และ 2 GPU ก่อน แล้วจึงรันจริงด้วย GPU 1 ใบ"],
        check=["มี `lab4_multigpu/code/bench.py` ที่รับจำนวน GPU 1 หรือ 2",
               "รอบลองสั้นรันผ่านทั้ง 1 และ 2 GPU (mAP50 ของรอบสั้นเป็น 0 ได้ ถือว่าปกติ)",
               "รอบจริง 1 GPU ครบ 5 Epoch และมีไฟล์ JSON ของรอบนั้น",
               "ตารางสรุปมีครบ: วินาทีต่อ Epoch · วินาทีต่อ step · GPU util · CPU ที่ใช้กี่ core · mAP50",
               "วินาทีของ Epoch 2–4 ใกล้กัน (การวัดนิ่ง)"],
        ref="ผลของผู้สอน: %s วินาทีต่อ Epoch · %.3f วินาทีต่อ step · GPU util %s%% · CPU %s core · mAP50 %.3f" % (
            f1(R1["sec_per_epoch"]), R1["sec_per_step"], f1(R1["gpu_util_avg_pct"]), f1(R1["cpu_cores_used"]), R1["map50"]),
        note="วินาทีต่อ Epoch ของคุณจะต่างจากนี้ตามเครื่องที่ได้ · สิ่งที่ต้องเหมือนคือวิธีวัดและค่าที่ตรึงไว้"),
    4: dict(
        what=["รัน `code/bench.py` เดิมจากขั้นที่ 3 **ค่าเดิมทุกอย่าง** เปลี่ยนแค่จำนวน GPU เป็น 2 ใบ",
              "เทรนต่อได้แม้การเชื่อมต่อหลุด · รายงานทุก 2–3 นาที และรอจนเสร็จ",
              "ถ้าต้องแก้สคริปต์ ให้ **รันรอบ 1 GPU ใหม่ด้วย** เพื่อให้ 2 รอบเทียบกันได้",
              "สรุปเทียบ 1 กับ 2 GPU: วินาทีต่อ Epoch · เร็วขึ้นกี่เท่า · วินาทีต่อ step · GPU util · CPU · all-reduce · mAP50"],
        check=["รอบ 2 GPU ครบ 5 Epoch ด้วยสคริปต์เดิม (ถ้าสคริปต์ถูกแก้ รอบ 1 GPU ถูกรันใหม่แล้ว)",
               "step ต่อ Epoch ลดลงราวครึ่งหนึ่ง",
               "ตารางเทียบมีครบ: วินาทีต่อ Epoch · เร็วขึ้นกี่เท่า · วินาทีต่อ step · GPU util · CPU · เวลา all-reduce · mAP50",
               "เห็น GPU util ของทั้ง 2 ใบ",
               "mAP50 ของ 2 รอบใกล้กัน"],
        ref="ผลของผู้สอน: %s → %s วินาทีต่อ Epoch · เร็วขึ้น %.2f× · %d → %d step ต่อ Epoch · %.3f → %.3f วินาทีต่อ step · mAP50 %.3f / %.3f" % (
            f1(R1["sec_per_epoch"]), f1(R2["sec_per_epoch"]), R2["speedup"], R1["steps_per_epoch"], R2["steps_per_epoch"],
            R1["sec_per_step"], R2["sec_per_step"], R1["map50"], R2["map50"]),
        note="Speedup ของคุณขึ้นกับทางเชื่อมระหว่าง GPU ของเครื่องที่ได้ · เครื่องที่มีทางเชื่อมดีกว่าอาจได้ใกล้ 2 เท่ากว่านี้"),
    5: dict(
        what=["ค้นราคาตลาดของ RTX 3090 แบบ 1 ใบ และ 2 ใบ ที่ถูกที่สุด",
              "นำผลของทั้ง 2 รอบ (JSON และข้อมูลดิบ) กลับมาที่ `results/raw`",
              "เขียน `code/report.py` คำนวณ ideal · speedup · efficiency · เงินต่อ Epoch → `results/metrics.json`",
              "ให้สคริปต์วาดกราฟ 4 รูปไว้ที่ `results/images`",
              "ตอบ 3 ข้อ: เร็วขึ้นกี่เท่า · แบบไหนคุ้มเงินที่สุดต่อ 1 Epoch · ทำไมไม่เร็วขึ้นตามจำนวน GPU"],
        check=["มี `lab4_multigpu/results/metrics.json` และกราฟ 4 รูปใน `lab4_multigpu/results/images`",
               "มี `lab4_multigpu/code/report.py` และผลดิบของทั้ง 2 รอบใน `lab4_multigpu/results/raw`",
               "ตารางมี ideal · speedup · efficiency · ราคาต่อชั่วโมง · เงินต่อ Epoch ของทั้ง 1 และ 2 GPU",
               "เงินต่อ Epoch คิดทั้งราคาตลาด และราคาเครื่องที่เช่าจริง",
               "คำตอบ 3 ข้ออ้างตัวเลขที่วัดได้"],
        ref="ผลของผู้สอน: Speedup %.2f× · Efficiency %s%% · เงินต่อ Epoch ราคาตลาด $%.4f กับ $%.4f · บนเครื่องที่เช่า $%.4f กับ $%.4f" % (
            R2["speedup"], f1(R2["efficiency_pct"]), R1["market_usd_per_epoch"], R2["market_usd_per_epoch"],
            R1["rented_usd_per_epoch"], R2["rented_usd_per_epoch"]),
        note="ราคาตลาดเปลี่ยนตลอด คำตอบเรื่อง \"คุ้มไหม\" ของคุณจึงอาจพลิกจากของผู้สอนได้ ต้องคิดจากราคา ณ วันที่เช่า"),
    6: dict(
        what=["ลบเครื่องป้าย `vapp-lab4`",
              "ตรวจว่าไม่มีเครื่องป้ายนี้ค้างในบัญชี · **ห้ามแตะเครื่องป้ายอื่น**",
              "สรุปค่าใช้จ่ายจริง: อายุเครื่อง · ราคาต่อชั่วโมง · ยอดที่ถูกคิด (GPU · disk · รับส่งข้อมูล)"],
        check=["AI รายงานว่าลบ `vapp-lab4` แล้ว และไม่มีเครื่องป้ายนี้ค้างในบัญชี",
               "เปิดหน้า [Instances](https://cloud.vast.ai/instances/) ของ Vast.ai แล้วไม่เห็นเครื่องนี้",
               "สรุปมีอายุเครื่อง · ราคาต่อชั่วโมง · ยอดแยก GPU · disk · รับส่งข้อมูล",
               "เครื่องป้ายอื่นในบัญชี (ถ้ามี) ยังอยู่ครบ"],
        ref="ผลของผู้สอน: เครื่องเปิด %s นาที · %s/ชม. · ยอดที่ AI อ่านได้ %s · ยอดสุดท้ายในใบแจ้งหนี้ %s" % (
            rx(r"เครื่องเปิด ([\d.]+) นาที"), rx(r"ชั่วโมงละ (\$[\d.]+)"), rx(r"รวม (\$[\d.]+)\]"), rx(r"ใบแจ้งหนี้ของ Vast.ai คือ \*\*(\$[\d.]+)\*\*")),
        note="ยอดของคุณขึ้นกับเวลาที่เครื่องเปิดจริง · ยอดในใบแจ้งหนี้อาจสูงกว่าที่ AI อ่านได้ทันทีหลังลบเล็กน้อย"),
    7: dict(
        what=["อ่านพรอมต์ทุกขั้นใน `PROMPTS.md` โค้ดใน `code` และผลใน `results`",
              "เขียนสกิล `multigpu-speedup` ที่ `skill_v0/SKILL.md`: name · description · ค่าที่ปรับได้ · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน",
              "คัดลอกโค้ดที่ใช้ได้แล้วจาก `code` ไปไว้ใน `skill_v0/scripts` ไม่เขียนใหม่",
              "ให้สกิลเรียกใช้สกิล `vastai` ต่อ แล้วติดตั้งที่ `.claude/skills/multigpu-speedup`"],
        check=["มี `lab4_multigpu/skill_v0/SKILL.md` ที่มี name และ description",
               "มีโค้ดใน `lab4_multigpu/skill_v0/scripts` (คัดลอกจาก `code`)",
               "SKILL.md มีค่าที่ปรับได้พร้อมค่าเริ่มต้น: รุ่น GPU · จำนวน GPU · เพดานราคา · Epoch · ป้ายเครื่อง และกติกาลบเครื่องเสมอ",
               "ติดตั้งแล้วที่ `.claude/skills/multigpu-speedup` ของโฟลเดอร์ปัจจุบัน",
               "ปิดแล้วเปิด Claude Code ใหม่ 1 ครั้งก่อนไปขั้นที่ 8"],
        ref="ผลของผู้สอน: สร้างสกิล `multigpu-speedup` · ไม่ต้องเช่าเครื่อง · สกิลที่ได้: [skill_v0/SKILL.md](skill_v0/SKILL.md)",
        note="เนื้อหาของ SKILL.md ของคุณจะไม่เหมือนของผู้สอนทุกบรรทัด สิ่งที่ต้องมีคือหัวข้อตามข้อ 2 ของพรอมต์"),
    8: dict(
        what=["ใช้สกิล `multigpu-speedup` **ในคำสั่งเดียว**: RTX 3090 2 ใบ · ราคาไม่เกิน $0.60 ต่อชั่วโมง · ป้าย `vapp-lab4-skill`",
              "เทรนรอบละ 3 Epoch เสร็จแล้วลบเครื่อง",
              "เก็บผลที่ `results/skill_v0_run` · **ห้ามเขียนทับผลเดิม** ใน `results`",
              "สรุป: วินาทีต่อ Epoch · speedup · เงินต่อ Epoch · เวลาแต่ละขั้น · ค่าใช้จ่ายจริง"],
        check=["AI ทำครบในพรอมต์เดียว: เช่า · เตรียม Dataset · เทรน 1 และ 2 GPU · ทำรายงาน · ลบเครื่อง",
               "มีผลใน `lab4_multigpu/results/skill_v0_run` และผลเดิมใน `results` ไม่ถูกเขียนทับ",
               "เครื่องป้าย `vapp-lab4-skill` ถูกลบแล้ว (ดูหน้า Instances ซ้ำ)",
               "สรุปมีวินาทีต่อ Epoch · speedup · เงินต่อ Epoch · เวลาแต่ละขั้น · ค่าใช้จ่ายจริง"],
        ref=None,
        note="รอบนี้เช่าเครื่องใหม่ ตัวเลขจึงต่างจากรอบทีละขั้นได้ · ถ้าทางเชื่อมเป็นแบบเดียวกัน Speedup ควรใกล้กัน"),
}
NAME = {}
NSTEPS = 8

# ขั้นตอนข้างภาพของแต่ละขั้น (ประโยคเต็ม เรียบเรียงจากพรอมต์และ README)
WHAT = {
    1: ["AI เช่า RTX 3090 **2 ใบในเครื่องเดียว** ราคาไม่เกิน $0.60 ต่อชั่วโมง ป้าย `vapp-lab4`",
        "เลือกเครื่อง verified ที่ต่อ SSH ได้ตรง มี CPU 16 cores ขึ้นไป ไม่อยู่ในจีน และถูกที่สุด",
        "ใช้ image PyTorch 2.8 กับ CUDA 12.8 และ disk 60 GB ถ้ารอเกิน 10 นาที ให้ลบแล้วเช่าใหม่",
        "ต้องรายงานว่า **GPU 2 ใบต่อถึงกันแบบไหน**"],
    2: ["AI ติดตั้ง `ultralytics` กับ `roboflow` แล้วดาวน์โหลด hard-hat-workers รุ่น 13 ในรูปแบบ YOLO",
        "key อ่านจาก `.env` โดย **ไม่แสดงค่า และไม่ทิ้งไว้บนเครื่องเช่า**",
        "สคริปต์ `code/show_samples.py` วาดกรอบจาก label จริงลงภาพตัวอย่าง 8 รูป",
        "คำตอบต้องมีจำนวนภาพ จำนวนกรอบของแต่ละคลาส และ label จริง 1 บรรทัด"],
    3: ["AI เขียน `code/bench.py` สคริปต์เดียวที่รับจำนวน GPU เป็น 1 หรือ 2",
        "ทุกรอบใช้ค่าเดียวกัน คือ 5 Epoch ภาพ 640 batch 32 ภาพต่อ GPU และ seed 0",
        "ลองรันสั้นด้วยภาพ 5% จำนวน 2 Epoch ทั้ง 1 และ 2 GPU ก่อน แล้วจึงรันจริงด้วย GPU 1 ใบ",
        "ผลของแต่ละรอบเก็บเป็นไฟล์ JSON 1 ไฟล์"],
    4: ["รัน `code/bench.py` ตัวเดิมด้วย **ค่าเดิมทุกอย่าง** เปลี่ยนเพียงจำนวน GPU เป็น 2 ใบ",
        "การเทรนต้องเดินต่อได้แม้การเชื่อมต่อหลุด และ AI รายงานความคืบหน้าทุก 2–3 นาที",
        "ถ้าต้องแก้สคริปต์ ต้อง **รันรอบ 1 GPU ใหม่ด้วย** เพื่อให้สองรอบเทียบกันได้"],
    5: ["AI ค้นราคาตลาดของ RTX 3090 แบบ 1 ใบ และ 2 ใบ ที่ถูกที่สุด",
        "ผลดิบของทั้ง 2 รอบถูกนำกลับมาไว้ที่ `results/raw`",
        "`code/report.py` คำนวณ ideal, speedup, efficiency และเงินต่อ Epoch ลง `results/metrics.json` แล้ววาดกราฟ 4 รูป",
        "คำตอบต้องตอบ 3 คำถาม คือ เร็วขึ้นกี่เท่า แบบไหนคุ้มเงินที่สุด และทำไมไม่เร็วขึ้นตามจำนวน GPU"],
    6: ["AI ลบเครื่องป้าย `vapp-lab4` แล้วตรวจว่าไม่มีเครื่องป้ายนี้ค้างในบัญชี",
        "**ห้ามแตะเครื่องที่มีป้ายอื่น**",
        "คำตอบสรุปอายุเครื่อง ราคาต่อชั่วโมง และยอดที่ถูกคิดแยกเป็น GPU, disk และการรับส่งข้อมูล"],
    7: ["AI อ่านพรอมต์ทุกขั้นใน `PROMPTS.md` โค้ดใน `code` และผลใน `results`",
        "เขียนสกิล `multigpu-speedup` ที่ `skill_v0/SKILL.md` ให้มีค่าที่ปรับได้ ขั้นตอน เกณฑ์ตรวจผ่าน และกติกาเรื่องเงิน",
        "คัดลอกโค้ดที่ใช้ได้แล้วไปไว้ใน `skill_v0/scripts` แทนการเขียนใหม่",
        "สกิลเรียกใช้สกิล `vastai` ต่อ และติดตั้งที่ `.claude/skills/multigpu-speedup`"],
    8: ["พรอมต์เดียวสั่งให้ใช้สกิล `multigpu-speedup` กับเครื่อง RTX 3090 2 ใบ ราคาไม่เกิน $0.60 ต่อชั่วโมง ป้าย `vapp-lab4-skill`",
        "เทรนรอบละ 3 Epoch แล้วลบเครื่องเมื่อเสร็จ",
        "ผลเก็บที่ `results/skill_v0_run` และ **ห้ามเขียนทับผลเดิม** ใน `results`"],
}
STEP_IMG = {1: "n26-step1", 2: "n27-step2", 3: "n28-step3", 4: "n29-step4", 5: "n30-step5", 6: "n31-step6", 7: "n32-step7", 8: "n33-step8"}
STEP_PHOTO = {1: "p22-rent", 2: "p23-data", 3: "p24-onegpu", 4: "p25-twogpu", 5: "p26-report", 6: "p27-delete", 7: "p28-skill", 8: "p29-auto"}

CSS2 = """<style>
.ex.px .fig{flex:2.1 1 0}
.ex.px .side{flex:1 1 0}
.ex.px .side .cap{text-align:left;font-size:.82em}
.ansv{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:.45em}
.ansv .fig{flex:1 1 0;min-height:0}
.ansv .fig img{box-shadow:0 0 0 1px var(--line),0 6px 22px rgba(18,48,94,.16)}
.ansv .cap{font-size:.78em;margin:0}
.arow{flex:none;display:grid;grid-template-columns:repeat(var(--n),1fr);gap:.6em}
.arow .stp{font-size:.86em}
.pairs{display:flex;flex-direction:column;gap:.75em}
.pairs .lg{display:flex;gap:1.4em;font-size:.82em;color:var(--muted)}
.pairs .lg i{display:inline-block;width:1em;height:1em;border-radius:3px;vertical-align:-.15em;margin-right:.35em}
.prow{display:grid;grid-template-columns:12em 1fr;gap:.2em 1em;align-items:center}
.prow .pl{font-weight:700;color:var(--navy);line-height:1.3}
.prow .pl small{display:block;font-weight:400;color:var(--muted);font-size:.78em}
.prow .pb{display:flex;flex-direction:column;gap:.25em}
.pbr{display:flex;align-items:center;gap:.6em}
.pbr .f{height:1.15em;border-radius:6px;min-width:4px}
.pbr .v{font-family:var(--mono);font-weight:700;color:var(--navy);font-size:.9em;white-space:nowrap}
.pa .f{background:#4f79b3}.pb2 .f{background:var(--orange)}
.stk{display:flex;flex-direction:column;gap:.8em}
.stk .row{display:grid;grid-template-columns:11em 1fr;gap:1em;align-items:center}
.stk .nm{font-weight:700;color:var(--navy);line-height:1.3}
.stk .nm small{display:block;font-weight:400;color:var(--muted);font-size:.8em}
.stk .tr{display:flex;height:2.1em;border-radius:8px;overflow:hidden}
.stk .tr div{display:flex;align-items:center;justify-content:center;color:#fff;font-family:var(--mono);font-weight:700;font-size:.82em;white-space:nowrap}
.stk .hd{background:#c92a2a}.stk .hm{background:#15803d}
</style>"""
CSS2_DONE = [False]


def css2():
    if CSS2_DONE[0]:
        return ""
    CSS2_DONE[0] = True
    return CSS2


def have(src):
    return os.path.exists(os.path.join(E.ROOT, src))


def pts_html(items):
    return "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(items))


def picside(title, src, items, cap="", tag="", cls="px"):
    """ภาพใหญ่ราว 2 ใน 3 ของสไลด์ + ข้อพูด 2-4 ข้อด้านขวา"""
    img = E.img_tag({"src": src, "alt": plain_alt(src) if not src.startswith("img/") else E.plain(title)})
    side = pts_html(items) + ('<p class="cap">%s</p>' % md(cap) if cap else "")
    return S(title, css2() + '<div class="ex %s"><div class="fig">%s</div><div class="side fitbox">%s</div></div>' % (cls, img, side),
             tag=tag, maxfs=1.25)


def answer(n, title, items, extra=""):
    """ส่วนหนึ่งของคำตอบจริง (ภาพตัดจากภาพหน้าจอของขั้นนั้น) + ข้ออ่านผล"""
    cap = "ส่วนหนึ่งของคำตอบจริง · [ดูภาพเต็ม](image/lab4-step%d.png)%s" % (n, extra)
    src = "img/c%02d-step%d-answer.jpg" % (n, n)
    img = E.img_tag({"src": src, "alt": "ส่วนหนึ่งของคำตอบจริงของขั้นที่ %d" % n})
    row = '<div class="arow" style="--n:%d">%s</div>' % (len(items), pts_html(items))
    return S(title, css2() + '<div class="ansv"><div class="fig">%s</div><p class="cap">%s</p>%s</div>' % (img, md(cap), row),
             tag="คำตอบจริง", maxfs=1.2)


def nfig2(key, title, cap, fallback):
    src = "img/%s.jpg" % key
    return fig(title, src, cap) if have(src) else fallback()


def pairs(rows, names=("1 GPU", "2 GPU"), colors=("#4f79b3", "#e87f1c")):
    """แท่งคู่เทียบ 2 แบบ · rows = [(ป้าย, คำอธิบายย่อย, ค่า A, ข้อความ A, ค่า B, ข้อความ B)] · ความยาวแท่งเทียบกับค่าที่มากกว่าในแถว"""
    lg = '<div class="lg"><span><i style="background:%s"></i>%s</span><span><i style="background:%s"></i>%s</span></div>' % (
        colors[0], names[0], colors[1], names[1])
    out = []
    for lab, sub, a, at, b, bt in rows:
        m = max(a, b) or 1
        bar = lambda cls, v, t: '<div class="pbr %s"><div class="f" style="width:%.1f%%"></div><span class="v">%s</span></div>' % (cls, 78 * v / m, t)
        out.append('<div class="prow"><div class="pl">%s%s</div><div class="pb">%s%s</div></div>' % (
            md(lab), "<small>%s</small>" % md(sub) if sub else "", bar("pa", a, at), bar("pb2", b, bt)))
    return css2() + '<div class="pairs">%s%s</div>' % (lg, "".join(out))


def step_divider(n, prefix, result):
    title = prefix.split("·", 1)[1].strip()
    NAME[n] = title
    img = "img/%s.jpg" % STEP_PHOTO[n]
    return E.divider("ขั้นที่ %d" % n, title, "<p>%s</p><p>ใช้เวลา <b>%s นาที</b> · ผลจริง: %s</p>" % (
        md(first_p(prefix)), minutes(prefix), md(result)), img=img if have(img) else "", small="ภาค LAB · ขั้นที่ %d จาก %d" % (n, NSTEPS))


def step_core(n, prefix, shot_title):
    st = STEP[n]
    src = "img/%s.jpg" % STEP_IMG[n]
    if have(src):
        add(picside(shot_title, src, WHAT[n]))
    else:
        add(explain(shot_title, "image/lab4-step%d.png" % n, WHAT[n]))
    add(E.prompt_slides(E.prompt_code(prefix), CTX["kicker"], "ขั้นที่ %d · %s" % (n, NAME[n])))
    add(E.check_slide("step%d" % n, st["check"], st["ref"] + " · ใช้ %s นาที" % minutes(prefix), st["note"], "ขั้นที่ %d · %s" % (n, NAME[n])))


def part_divider(k, big, title, sub, img):
    return E.divider(big, title, sub, img=img if have(img) else "", small="ส่วนที่ %d จาก 4" % k)


def build():
    ds = {r[0]: r[1] for r in table("รู้จัก Dataset", "หัวข้อ")["rows"]}
    split = table("รู้จัก Dataset", "ชุด")["rows"]
    exp = {r[0]: r[1] for r in table("การทดลอง", "หัวข้อ")["rows"]}
    cmp8 = table("ขั้นที่ 8", "")
    c8 = {E.plain(r[0]): r for r in cmp8["rows"]}
    t4 = {E.plain(r[0]): r for r in table("ขั้นที่ 4", "ค่าที่วัด")["rows"]}
    opened = rx(r"เครื่องเปิด ([\d.]+) นาที")
    price = rx(r"ชั่วโมงละ (\$[\d.]+)")
    invoice = rx(r"ใบแจ้งหนี้ของ Vast.ai คือ \*\*(\$[\d.]+)\*\*")
    ai_read = rx(r"รวม (\$[\d.]+)\]")
    ratio = rx(r"\$0\.351 \(([\d.]+) เท่า\)")

    # ===== 1 · เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    cov = E.cover("LAB 4 · 1 GPU เทียบ 2 GPU", "เทรนงานเดิมบน 1 GPU เทียบ 2 GPU: เร็วขึ้นกี่เท่า คุ้มเงินไหม", "img/s00-cover.jpg",
                  small="สัปดาห์ที่ 3 · เช่า GPU บน Vast.ai มาเทรนโมเดล · LAB 4")
    cov["raw"] += "<style>.divider .inner .small{margin-bottom:26px;font-size:24px}</style>"
    add(cov)
    CTX["kicker"] = "ภาพรวมของ LAB"
    add(fig("คำถามของ LAB: จ่ายเพิ่มเกือบ 2 เท่าเพื่อ GPU ใบที่สอง แล้วจะเทรนเร็วขึ้น 2 เท่าหรือไม่", "image/why2-multigpu.png",
            "เราตอบคำถามนี้ด้วยการวัด โดยเทรนงานเดียวกัน 2 รอบบนเครื่องเดียวกัน ต่างกันเพียงจำนวน GPU"))
    add(fig("คำตอบ: 2 GPU เร็วขึ้น %.2f เท่า แต่ราคาตลาดแพงขึ้น %s เท่า เงินต่อ Epoch จึงไม่ได้ถูกลง" % (R2["speedup"], ratio),
            "image/t2-cost.png",
            "1 GPU ใช้เงิน **$%.4f** ต่อ Epoch ส่วน 2 GPU ใช้ **$%.4f** ต่อ Epoch แต่ได้งานเสร็จเร็วกว่า" % (R1["market_usd_per_epoch"], R2["market_usd_per_epoch"]),
            tag="results/metrics.json"))
    plan_fb = lambda: S("LAB นี้มี 4 ส่วน", cards([
        (("1", "พื้นฐาน"), "Dataset โมเดล YOLO11m และทฤษฎี 4 ข้อ", "navy"),
        (("2", "ภาค LAB ขั้นที่ 1–6"), "เช่าเครื่อง 2 GPU เทรน 1 และ 2 GPU สรุปผล แล้วลบเครื่อง · %s" % exp["เวลาและค่าเช่าจริง"], ""),
        (("3", "ปิดท้าย ขั้นที่ 7–8"), "เก็บงานเป็น **สกิลเวอร์ชัน 0** แล้วลองใช้ในคำสั่งเดียว", "ok"),
        (("4", "สรุป"), "ผลรวม ตารางเทียบ บทเรียน และจุดที่ v0 ยังไม่ผ่าน", "warn")], 2), cls="mid")
    add(nfig2("n21-roadmap", "LAB นี้มี 4 ส่วน: พื้นฐาน ภาค LAB 6 ขั้น การเก็บงานเป็นสกิล และสรุป",
              "ภาค LAB ทั้ง 6 ขั้นทำบนเครื่องเช่าเครื่องเดียวกัน · %s" % exp["เวลาและค่าเช่าจริง"], plan_fb))
    add(S("วิธีใช้สไลด์ชุดนี้", cards([
        ("เลื่อนหน้า", '<p>กด <span class="kbd">→</span> หรือ <span class="kbd">Space</span> เพื่อไปต่อ และ <span class="kbd">←</span> เพื่อย้อนกลับ</p>', ""),
        ("สารบัญและเต็มจอ", '<p>กด <span class="kbd">O</span> เปิดสารบัญ และ <span class="kbd">F</span> เต็มจอ · คลิกภาพเพื่อขยาย</p>', ""),
        ("คัดลอกพรอมต์", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** ให้พรอมต์ครบทั้งก้อน ตรงกับ README ทุกตัวอักษร แล้ววางในช่องพิมพ์ของ Claude Code ทีละขั้น", "warn"),
        ("ตรวจผลของคุณ", "หน้า **ตรวจผลของคุณ** ติ๊กได้ทีละข้อ และมีผลของผู้สอนไว้เทียบ ตัวเลขของคุณอาจต่างจากของผู้สอน", "ok")], 2), cls="mid"))

    # ===== 2 · พื้นฐาน
    CTX.update(kicker="พื้นฐาน · Dataset และโมเดล", group="พื้นฐาน · Dataset และโมเดล")
    add(part_divider(1, "พื้นฐาน", "Dataset โมเดล และทฤษฎีที่ต้องรู้", "<p>ก่อนวัดความเร็ว เราต้องรู้ว่าเทรนอะไร ด้วยโมเดลอะไร และวัดด้วยตัวเลขใด</p>", "img/p21-site.jpg"))
    why = para("รู้จัก Dataset", "**ทำไมใช้ชุดนี้**")["lines"][0].replace("**ทำไมใช้ชุดนี้** ", "")
    add(picside("Dataset: ภาพคนงานหน้างาน ตีกรอบที่ศีรษะ บอกว่าสวมหมวกนิรภัยหรือไม่", "results/dataset_samples.jpg", [
        "กรอบสีเขียวคือ `helmet` (สวมหมวกนิรภัย) กรอบสีแดงคือ `head` (ไม่สวมหมวก)",
        "ภาพที่เอียงและสี่เหลี่ยมดำเป็น Augmentation ที่ Dataset รุ่นนี้เพิ่มไว้แล้ว",
        "**เหตุที่ใช้ชุดนี้** " + why.split(" · ")[0] + " 1 Epoch จึงมีหลายร้อย step และเวลาที่วัดได้นิ่งพอจะเทียบกัน"],
        cap="ภาพตัวอย่าง 8 รูปจาก Training Set ซึ่งได้จากพรอมต์ขั้นที่ 2"))
    mx = max(int(r[2].replace(",", "")) + int(r[3].replace(",", "")) for r in split)
    rows = []
    for r in split:
        h, m = int(r[2].replace(",", "")), int(r[3].replace(",", ""))
        rows.append('<div class="row"><div class="nm">%s<small>%s ภาพ</small></div><div class="tr" style="width:%.1f%%">'
                    '<div class="hd" style="flex:%d">%s</div><div class="hm" style="flex:%d">%s</div></div></div>' % (
                        r[0], r[1], 100, h, r[2], m, r[3]))
    add(S("กรอบ helmet มีมากกว่า head ราว 3 เท่าในทุกชุด ข้อมูลจึงไม่สมดุล", css2() +
          '<div class="pairs"><div class="lg"><span><i style="background:#c92a2a"></i>กรอบ <code>head</code></span>'
          '<span><i style="background:#15803d"></i>กรอบ <code>helmet</code></span></div></div>' +
          '<div class="stk">%s</div>' % "".join(rows) +
          '<p class="cap">แต่ละแถบแสดงสัดส่วนของกรอบ head กับ helmet ภายในชุดนั้น</p>' +
          note("Dataset ทั้งชุดมี %s และ %s ทุกภาพมีขนาด %s และใช้พื้นที่ %s · สัญญาอนุญาต %s" % (
              ds["ขนาด"].split(" · ")[0], ds["ขนาด"].split(" · ")[1], ds["ขนาด"].split(" · ")[2].replace("ทุกภาพ ", ""), ds["ขนาด"].split(" · ")[3], ds["สัญญาอนุญาต"]), label="Dataset"),
          tag="README · รู้จัก Dataset", cls="mid"))
    add(nfig("n01-label"))
    md_ = {r[0]: r[1] for r in table("รู้จักโมเดลที่ใช้", "หัวข้อ")["rows"]}
    add(fig("โมเดล YOLO11m รับภาพ 1 รูป แล้วตอบเป็นกรอบ คลาส และ Confidence", "image/model-yolo11m.png",
            "%s · ใน LAB นี้เป้าหมายคือ **วัดความเร็ว** ไม่ใช่ทำโมเดลให้แม่นที่สุด" % md_["ขนาด"]))

    CTX.update(kicker="พื้นฐาน · ทฤษฎีที่ต้องรู้", group="พื้นฐาน · ทฤษฎี")
    add(explain("ทฤษฎี 1 · DDP: ทุก GPU มีสำเนาโมเดลครบชุด แล้วแบ่งภาพใน Batch กันคนละส่วน", "image/t2-ddp.png", [
        "แต่ละ GPU รับภาพ 32 ภาพ คำนวณ Forward + Backward แล้วได้ Gradient ของตัวเอง",
        "**All-reduce** เฉลี่ย Gradient ของทุกใบให้เป็นค่าเดียวกัน",
        "ทุกใบปรับ (Update) โมเดลด้วยค่าเดียวกัน โมเดลทุกสำเนาจึงยังเหมือนกัน"]))
    t1 = table("1 · Data-parallel", "")
    ips = next(r for r in t1["rows"] if r[0].startswith("ภาพต่อวินาที"))
    add(nfig2("n22-halfsteps", "Batch รวมโตขึ้น 2 เท่า จำนวน step ต่อ Epoch จึงเหลือครึ่งเดียว",
              "ภาพต่อวินาทีเพิ่มจาก **%s** เป็น **%s** · ถ้าแต่ละ step ใช้เวลาเท่าเดิม Epoch จะเร็วขึ้น 2 เท่าพอดี" % (ips[1], ips[2]),
              lambda: S("Batch รวมโตขึ้น 2 เท่า จำนวน step ต่อ Epoch จึงเหลือครึ่งเดียว", tiles([
                  (E.plain(r[0]), "%s → %s" % (r[1], r[2]), "1 GPU → 2 GPU", "") for r in t1["rows"]]), cls="mid")))
    add(fig("แต่ละ step ของ 2 GPU ช้าลงจาก %d เป็น %d ms เพราะต้อง Sync กัน" % (round(R1["sec_per_step"] * 1000), round(R2["sec_per_step"] * 1000)),
            "image/t2-step.png", "ดูส่วนสีส้มของแท่ง 2 GPU ซึ่งเป็นเวลาที่เพิ่มขึ้นจากการ Sync **+%d ms ต่อ step**" % round(R2["step_extra_sec"] * 1000)))
    t2 = {r[0]: r for r in table("2 · Speedup", "ค่า")["rows"]}
    add(explain("ทฤษฎี 2 · Speedup %.2f เท่า คิดเป็น Efficiency %s ของ Ideal" % (R2["speedup"], rx(r"1\.74 ÷ 2 = \*\*(\d+%)\*\*")), "image/t2-speedup.png", [
        "**Speedup** = %s หมายถึงเร็วขึ้นกี่เท่า" % t2["Speedup"][1],
        "**Ideal** คือ %s และ **Efficiency** = %s หมายถึงได้กี่ %% ของ Ideal" % (t2["Ideal"][1], t2["Efficiency"][1]),
        "วัดเป็นวินาทีต่อ Epoch โดยไม่นับ Epoch แรกและ Epoch สุดท้าย",
        "ใน LAB นี้ " + para("2 · Speedup", "**ตัวเลขจาก LAB นี้**")["lines"][0].replace("**ตัวเลขจาก LAB นี้** ", "").replace(" · ", " และ ")]))
    t3 = {r[0]: r for r in table("3 · ทำไม Scaling", "ค่าที่วัด")["rows"]}
    add(explain("ทฤษฎี 3 · 2 GPU ไม่เร็วขึ้น 2 เท่า เพราะการ Sync แบ่งให้ GPU ทำพร้อมกันไม่ได้", "image/t2-bottleneck.png", [
        "ส่วนที่แบ่งทำพร้อมกันไม่ได้เป็น **เพดานของ Speedup** ตามหลักเดียวกับ Amdahl's law",
        "เวลาที่เพิ่ม 41 ms ต่อ step ราวครึ่งหนึ่งคือ All-reduce (21.4 ms) ที่เหลือคือเวลาที่ GPU ใบหนึ่งรออีกใบ",
        "**CPU ไม่ใช่คอขวด** 1 GPU ใช้ CPU เพียง %s และ 2 GPU ใช้ %s ส่วน GPU util เฉลี่ยเป็น %s (1 GPU) และ %s (2 GPU)" % (
            t3["CPU ที่ใช้จริง"][1], re.sub(r"\s*\(เครื่องให้ ([^)]*)\)", r" จาก \1 ที่เครื่องให้", t3["CPU ที่ใช้จริง"][2]),
            t3["GPU util เฉลี่ย"][1], t3["GPU util เฉลี่ย"][2])]))
    add(explain("Gradient ราว 80 MB ต้องข้าม GPU ทุก step ความเร็วจึงขึ้นกับทางเชื่อม", "image/t2-topology.png", [
        "เครื่องใน LAB นี้เป็น `PHB` ข้อมูลผ่าน PCIe 3.0 x8 ลงไปที่ CPU และ RAM แล้วจึงขึ้นไป GPU อีกใบ",
        "วัดได้ %.1f GB/s และส่ง 80 MB ใช้เวลา %.1f ms" % (R2["allreduce_busbw_GBps"], R2["allreduce_80mb_ms"]),
        "เครื่องที่มี **NVLink** มีทางตรงระหว่าง GPU จึงส่งได้เร็วกว่า"]))
    add(nfig("n03-topology"))
    cost_pts = ["**เงินต่อ Epoch** = ราคาต่อชั่วโมง × วินาทีต่อ Epoch ÷ 3600",
                "1 GPU: $%.3f/ชม. × %s วินาที ได้ **$%.4f** ต่อ Epoch" % (R1["market_usd_per_hour"], f1(R1["sec_per_epoch"]), R1["market_usd_per_epoch"]),
                "2 GPU: $%.3f/ชม. × %s วินาที ได้ **$%.4f** ต่อ Epoch" % (R2["market_usd_per_hour"], f1(R2["sec_per_epoch"]), R2["market_usd_per_epoch"]),
                "ราคาเพิ่ม %s เท่า แต่เร็วขึ้น %.2f เท่า เมื่อราคาเพิ่มเร็วกว่า Speedup เงินต่อ Epoch จึงแพงขึ้น" % (ratio, R2["speedup"])]
    if have("img/n23-costmeter.jpg"):
        add(picside("ทฤษฎี 4 · Cost per Epoch: เร็วขึ้นไม่ได้แปลว่าถูกลง", "img/n23-costmeter.jpg", cost_pts))
    else:
        add(explain("ทฤษฎี 4 · Cost per Epoch: เร็วขึ้นไม่ได้แปลว่าถูกลง", "image/t2-cost.png", cost_pts))
    when = ul_after("4 · Cost per Epoch", "**ควรใช้หลาย GPU เมื่อไร**")
    add(nfig2("n24-when", "ควรใช้หลาย GPU เมื่องานใหญ่ ราคาไม่เกิน N เท่า และทางเชื่อมดี",
              "ถ้างานเล็กหรือต้องการประหยัด ใช้ 1 GPU · ดูทางเชื่อมด้วย `nvidia-smi topo -m` ทุกครั้ง",
              lambda: points("ควรใช้หลาย GPU เมื่องานใหญ่ ราคาไม่เกิน N เท่า และทางเชื่อมดี", when)))

    # ===== 3 · ภาค LAB
    CTX.update(kicker="ภาค LAB · ภาพรวม", group="ภาค LAB · ภาพรวม")
    add(part_divider(2, "ภาค LAB", "6 ขั้นบนเครื่องเช่าเครื่องเดียวกัน", "<p>ทุกขั้นคือ 1 พรอมต์ และโค้ดทุกไฟล์ AI เขียนให้จากพรอมต์ โดยเริ่มจากโฟลเดอร์ว่าง</p>"
                                                                       "<p>%s</p>" % md(exp["เวลาและค่าเช่าจริง"]), "img/s01-lab.jpg"))
    add(fig("แผนที่ของ LAB: เช่าเครื่อง เตรียม Dataset เทรน 1 GPU เทรน 2 GPU สรุปผล แล้วลบเครื่อง", "image/lab4-overview.png",
            "ทำขั้นที่ 1 ถึง 6 ให้ครบในรอบเดียว แล้วปิดท้ายด้วยขั้นที่ 7–8 ซึ่งเก็บงานเป็นสกิลเวอร์ชัน 0"))
    add(nfig("n02-experiment"))
    before = [
        "ขั้นที่ 2 ใช้ `ROBOFLOW_API_KEY` จาก `.env` ซึ่งเตรียมไว้ใน [LAB 0](../README.md#lab-0--เตรียม-key-3-ตัว)",
        "\"โฟลเดอร์ปัจจุบัน\" ในพรอมต์คือ `02_VastAi_Application` และงานทำผ่าน container `multi-account` ด้วยสกิล `vastai`",
        "โค้ดของคุณอยู่ใน `lab4_multigpu/code` ส่วนตัวอย่างจากรอบจริงอยู่ใน `code_reference/`",
        "เพดานราคาคือ $0.60/ชม. ทำ 6 ขั้นให้ครบในรอบเดียว และ **ลบเครื่องในขั้นที่ 6 เสมอ**"]
    if have("img/n25-before.jpg"):
        add(picside("ก่อนเริ่ม ต้องเตรียม 4 อย่างนี้ให้พร้อม", "img/n25-before.jpg", before))
    else:
        add(points("ก่อนเริ่ม ต้องเตรียม 4 อย่างนี้ให้พร้อม", before))

    # --- ขั้นที่ 1
    p = "ขั้นที่ 1"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 1 จาก 8", group="ขั้นที่ 1 · เช่าเครื่อง")
    rented = M["prices"]["rented"]
    add(step_divider(1, sec_name(p), "RTX 3090 2 ใบ $%.3f/ชม. ทางเชื่อม `PHB`" % rented["usd_per_hour"]))
    step_core(1, p, "AI ค้นหาเครื่อง เช่า รอจนพร้อม แล้วรายงานว่า GPU ต่อถึงกันแบบไหน")
    add(answer(1, "ได้ RTX 3090 2 ใบที่ %s ราคา $%.3f ต่อชั่วโมง และ GPU ต่อกันแบบ PHB ไม่มี NVLink" % (
        rented["geolocation"].split(",")[0], rented["usd_per_hour"]), [
        "เครื่องนี้เป็น `PHB` และไม่มี NVLink จึงคาดได้ตั้งแต่ขั้นนี้ว่า 2 GPU จะเร็วขึ้นไม่ถึง 2 เท่า (ทฤษฎีข้อ 3)",
        "GPU 2 ใบอยู่ CPU socket เดียวกัน ซึ่งดีกว่าแบบข้าม socket",
        "**เงินเริ่มเดินตั้งแต่ขั้นนี้** ชั่วโมงละ $%.3f จนกว่าจะลบเครื่องในขั้นที่ 6" % rented["usd_per_hour"]],
        extra=" · เครื่องให้ CPU 32 cores และราคาอยู่ใต้เพดาน $0.60"))

    # --- ขั้นที่ 2
    p = "ขั้นที่ 2"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 2 จาก 8", group="ขั้นที่ 2 · เตรียม Dataset")
    add(step_divider(2, sec_name(p), "%s / %s / %s ภาพ · 2 คลาส" % tuple(r[1] for r in split)))
    STEP[2]["check"] = ["Training Set %s · Validation Set %s · Test Set %s ภาพ · 2 คลาส" % tuple(r[1] for r in split),
                        "มีไฟล์ `lab4_multigpu/results/dataset_samples.jpg` และกรอบตรงกับศีรษะคน",
                        "มี `lab4_multigpu/code/show_samples.py` พร้อมสคริปต์ดาวน์โหลดและสคริปต์นับจำนวน",
                        "ตารางมีจำนวนกรอบของแต่ละคลาสในแต่ละชุด และขนาด Dataset",
                        "AI ยก label จริง 1 บรรทัด พร้อมอธิบายว่าแต่ละช่องคืออะไร",
                        "ไม่มีค่า key ในคำตอบ และไม่มี key ค้างบนเครื่องเช่า"]
    STEP[2]["ref"] = "ผลของผู้สอน: %s ภาพ · %s" % (" / ".join(r[1] for r in split), md(ds["ขนาด"]))
    step_core(2, p, "AI ดาวน์โหลด Dataset แล้วเขียนสคริปต์ทำภาพตัวอย่างจาก label จริง")
    add(answer(2, "ได้ %s / %s / %s ภาพ ครบ 2 คลาส รวม %s และไม่มี key ค้างบนเครื่องเช่า" % (
        tuple(r[1] for r in split) + (ds["ขนาด"].split(" · ")[1],)), [
        "จำนวนภาพต้องตรงกับนี้ เพราะเป็น Dataset รุ่นเดียวกัน แล้วเปิด `results/dataset_samples.jpg` ดูว่ากรอบตรงกับศีรษะคน",
        "กรอบ `helmet` มีมากกว่า `head` ราว 3 เท่า หมายความว่าข้อมูลไม่สมดุล",
        "AI ส่ง key ให้เครื่องเช่าโดยไม่เขียนลงไฟล์ แล้วตรวจซ้ำว่าไม่มี key ค้าง"],
        extra=" · Dataset ใช้พื้นที่ %s" % ds["ขนาด"].split(" · ")[3]))

    # --- ขั้นที่ 3
    p = "ขั้นที่ 3"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 3 จาก 8", group="ขั้นที่ 3 · เทรน 1 GPU")
    add(step_divider(3, sec_name(p), "1 GPU %s วินาทีต่อ Epoch" % f1(R1["sec_per_epoch"])))
    step_core(3, p, "AI เขียนสคริปต์วัดความเร็วสคริปต์เดียวที่ใช้ได้ทั้ง 1 และ 2 GPU")
    add(answer(3, "1 GPU ใช้ %s วินาทีต่อ Epoch และ %.3f วินาทีต่อ step ได้ mAP50 %.3f" % (f1(R1["sec_per_epoch"]), R1["sec_per_step"], R1["map50"]), [
        "1 Epoch มี %d step" % R1["steps_per_epoch"],
        "GPU util %s%% และใช้ CPU เพียง %s core แสดงว่า GPU คือส่วนที่ทำงานหนัก ไม่ได้รอ CPU" % (f1(R1["gpu_util_avg_pct"]), f1(R1["cpu_cores_used"])),
        "รอบลองสั้นได้ mAP50 เป็น 0 เพราะเทรนเพียง 48 step ถือว่าปกติ รอบนี้มีไว้ตรวจว่าสคริปต์รันได้ก่อนเสียเวลารอบจริง"]))
    ep = R1["epoch_seconds_all"]
    whyep = {0: "ช่วงเริ่มต้น · ไม่นับ", len(ep) - 1: "รวมการวัด Validation · ไม่นับ"}
    add(S("Epoch 1 และ 5 ช้ากว่า จึงเฉลี่ยเฉพาะ Epoch 2–4 ได้ %s วินาทีต่อ Epoch" % f1(R1["sec_per_epoch"]), bars(
        [("Epoch %d" % (k + 1), whyep.get(k, "ใช้เฉลี่ย"), v, max(ep) * 1.05, "%s วินาที" % f1(v)) for k, v in enumerate(ep)]) +
        note("Epoch 2–4 ต่างกันไม่ถึง 0.5 วินาที การวัดจึงนิ่งพอที่จะเชื่อถือได้"), tag="results/metrics.json", cls="mid"))

    # --- ขั้นที่ 4
    p = "ขั้นที่ 4"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 4 จาก 8", group="ขั้นที่ 4 · เทรน 2 GPU")
    add(step_divider(4, sec_name(p), "2 GPU %s วินาทีต่อ Epoch · เร็วขึ้น %.2f เท่า" % (f1(R2["sec_per_epoch"]), R2["speedup"])))
    step_core(4, p, "รันสคริปต์เดิมโดยไม่แก้ เปลี่ยนเพียงจำนวน GPU เป็น 2")
    add(answer(4, "2 GPU ใช้ %s วินาทีต่อ Epoch เร็วขึ้น %.2f เท่า โดย mAP50 ไม่ลดลง" % (f1(R2["sec_per_epoch"]), R2["speedup"]), [
        "mAP50 เท่าเดิม (%.3f กับ %.3f) แสดงว่า DDP ทำให้เร็วขึ้นโดยคุณภาพโมเดลไม่ลด" % (R1["map50"], R2["map50"]),
        "ข้อ 3 ของพรอมต์สำคัญ ถ้าสคริปต์ถูกแก้ ต้องวัด 1 GPU ใหม่ด้วย มิฉะนั้นสองรอบเทียบกันไม่ได้"]))
    mp = t4["mAP50 / mAP50-95"]
    add(S("step ต่อ Epoch เหลือครึ่ง แต่แต่ละ step ช้าลงราว 15%% ผลจึงเป็น %.2f เท่า ไม่ใช่ 2 เท่า" % R2["speedup"], pairs([
        ("วินาทีต่อ Epoch", "เฉลี่ย Epoch 2–4", R1["sec_per_epoch"], f1(R1["sec_per_epoch"]), R2["sec_per_epoch"], f1(R2["sec_per_epoch"])),
        ("step ต่อ Epoch", "", R1["steps_per_epoch"], "%d" % R1["steps_per_epoch"], R2["steps_per_epoch"], "%d" % R2["steps_per_epoch"]),
        ("วินาทีต่อ step", "", R1["sec_per_step"], "%.3f" % R1["sec_per_step"], R2["sec_per_step"], "%.3f" % R2["sec_per_step"]),
        ("mAP50", "", R1["map50"], "%.3f" % R1["map50"], R2["map50"], "%.3f" % R2["map50"]),
        ("mAP50-95", "", float(mp[1].split(" / ")[1]), mp[1].split(" / ")[1], float(mp[2].split(" / ")[1]), mp[2].split(" / ")[1])]) +
        note("เร็วขึ้น **%.2f×** เทียบกับ Ideal 2.00× · แท่งยาวขึ้นในแถววินาทีต่อ step คือราคาของการ Sync" % R2["speedup"]),
        tag="results/metrics.json", cls="mid"))

    # --- ขั้นที่ 5
    p = "ขั้นที่ 5"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 5 จาก 8", group="ขั้นที่ 5 · สรุปและเงินต่อ Epoch")
    add(step_divider(5, sec_name(p), "Efficiency %s%% · ราคาตลาด 1 GPU ถูกกว่าต่อ Epoch" % f1(R2["efficiency_pct"])))
    step_core(5, p, "AI ค้นราคาตลาด นำผลดิบกลับมา แล้วคำนวณทุกตัวเลขด้วยสคริปต์")
    add(answer(5, "Speedup %.2f เท่า Efficiency %s%% และในราคาตลาด 1 GPU ถูกกว่าต่อ Epoch" % (R2["speedup"], f1(R2["efficiency_pct"])), [
        "ราคาตลาด 1 GPU ถูกกว่าราว 5%% ต่อ Epoch เพราะเครื่อง 2 ใบแพงขึ้น %s เท่า แต่เร็วขึ้น %.2f เท่า โดย 2 GPU เสร็จเร็วกว่า 42%%" % (ratio, R2["speedup"]),
        "**เช่าเครื่อง 2 ใบแล้วใช้ใบเดียวแพงที่สุด** ($%.4f) เพราะจ่ายค่าเครื่องเต็มแต่ได้งานครึ่งเดียว" % R1["rented_usd_per_epoch"],
        "ราคาตลาดเปลี่ยนตลอด คำตอบเรื่องความคุ้มจึงต้องคิดจากราคา ณ วันที่เช่า และควรดูค่า reliability ประกอบ"]))
    add(figrow("2 GPU ใช้ %s วินาทีต่อ Epoch ช้ากว่า Ideal %s วินาที" % (f1(R2["sec_per_epoch"]), f1(R2["ideal_sec_per_epoch"])),
               ["results/images/1_epoch_time.png", "results/images/2_speedup.png"],
               "ดูแท่งสีส้มเทียบจุดสีเขียว (ideal) ทางซ้าย และเส้นสีส้มที่อยู่ใต้เส้น ideal ทางขวา · Speedup **%.2f×** · Efficiency **%s%%**" % (
                   R2["speedup"], f1(R2["efficiency_pct"]))))
    add(figrow("ช่องว่างจาก Ideal คือเวลา Sync %d ms ต่อ step ส่วน CPU ใช้งานน้อย" % round(R2["step_extra_sec"] * 1000),
               ["results/images/4_bottleneck.png"],
               "ดูส่วนสีส้มบนแท่ง 2 GPU ทางซ้าย และเส้นสีเทาของ CPU ที่อยู่ต่ำทางขวา"))
    add(S("เงินต่อ Epoch: ในราคาตลาด 1 GPU ถูกกว่า แต่บนเครื่อง 2 ใบที่เช่าอยู่ การใช้ 2 GPU ถูกกว่า", tiles([
        ("ราคาตลาด · 1 GPU", "$%.4f" % R1["market_usd_per_epoch"], "$%.3f/ชม." % R1["market_usd_per_hour"], "ok"),
        ("ราคาตลาด · 2 GPU", "$%.4f" % R2["market_usd_per_epoch"], "$%.3f/ชม." % R2["market_usd_per_hour"], ""),
        ("เครื่องที่เช่า · 1 GPU", "$%.4f" % R1["rented_usd_per_epoch"], "จ่ายเต็มเครื่อง $%.3f/ชม. ได้งานครึ่งเดียว" % R1["rented_usd_per_hour"], "bad"),
        ("เครื่องที่เช่า · 2 GPU", "$%.4f" % R2["rented_usd_per_epoch"], "$%.3f/ชม." % R2["rented_usd_per_hour"], "ok")]) +
        '<div class="fig" style="--figmin:300px">%s</div>' % E.img_tag({"src": "results/images/3_cost_per_epoch.png", "alt": plain_alt("results/images/3_cost_per_epoch.png")}),
        tag="results/metrics.json"))

    # --- ขั้นที่ 6
    p = "ขั้นที่ 6"
    CTX.update(kicker="ภาค LAB · ขั้นที่ 6 จาก 8", group="ขั้นที่ 6 · ลบเครื่อง")
    add(step_divider(6, sec_name(p), "ลบเครื่องแล้ว · ค่าเช่าจริง %s" % invoice))
    step_core(6, p, "AI ลบเครื่อง ตรวจว่าไม่มีเครื่องค้าง แล้วอ่านยอดที่ถูกคิดเงินจริง")
    add(answer(6, "เครื่องเปิด %s นาที AI อ่านยอดได้ %s และยอดสุดท้ายในใบแจ้งหนี้คือ %s" % (opened, ai_read, invoice), [
        "ราคา %s ต่อชั่วโมงของเครื่อง 2 ใบ ถูกคิดตลอดอายุเครื่อง" % price,
        "ยอดในใบแจ้งหนี้สูงกว่าที่ AI อ่านได้ทันทีหลังลบเล็กน้อย",
        "ต้องเห็นว่า **ไม่มีเครื่องป้ายนี้เหลือ** แล้วเปิดหน้า [Instances](https://cloud.vast.ai/instances/) ดูอีกครั้ง"]))
    add(nfig("n04-meter", steps=reading(p)[1:]))

    # ===== ปิดท้าย · สกิล v0
    CTX.update(kicker="ปิดท้าย · สกิลเวอร์ชัน 0", group="ปิดท้าย · สกิล v0")
    add(part_divider(3, "ปิดท้าย", "เก็บงานทั้ง LAB เป็นสกิลเวอร์ชัน 0", "<p>%s</p>" % md(first_p("ปิดท้าย")), "img/p31-recipe.jpg"))
    add(fig("สกิลเก็บวิธีทำงานที่สำเร็จแล้วพร้อมโค้ด ให้ทำซ้ำได้ในคำสั่งเดียว", "image/skill-v0.png",
            "ขั้นที่ 7 ให้ AI เขียนสกิลจากงาน 6 ขั้น และขั้นที่ 8 ลองใช้สกิลนั้นทำซ้ำทั้ง LAB"))
    p = "ขั้นที่ 7"
    CTX.update(kicker="ปิดท้าย · ขั้นที่ 7 จาก 8", group="ขั้นที่ 7 · สร้างสกิล v0")
    add(step_divider(7, sec_name(p), "สกิล `multigpu-speedup`"))
    step_core(7, p, "AI อ่านพรอมต์ โค้ด และผลของ LAB แล้วเขียนสกิล v0")
    alert = next(b for b in sec(p) if b["t"] == "alert")
    add(answer(7, "ได้สกิล multigpu-speedup ที่สั่ง LAB 4 ครบ 6 ขั้นได้ในคำสั่งเดียว", [
        "สกิลอยู่ที่ [skill_v0/SKILL.md](skill_v0/SKILL.md) มีค่าที่ปรับได้ คือ รุ่น GPU จำนวน GPU เพดานราคา Epoch และป้ายเครื่อง",
        "โค้ดใน `scripts/` คัดลอกจาก `code` สกิลจึงใช้โค้ดที่ใช้ได้แล้ว ไม่เขียนใหม่",
        "**สำคัญ** " + " ".join(alert["blocks"][0]["lines"]).replace("⚠️", "").strip()]))

    p = "ขั้นที่ 8"
    CTX.update(kicker="ปิดท้าย · ขั้นที่ 8 จาก 8", group="ขั้นที่ 8 · ใช้สกิลทำซ้ำ")
    sp = c8["Speedup / Efficiency"][2]
    add(step_divider(8, sec_name(p), "1 พรอมต์ · Speedup %s · ค่าเช่า %s" % (sp.split(" / ")[0], c8["ค่าเช่า"][2])))
    STEP[8]["ref"] = "ผลของผู้สอน: %s · %s วินาทีต่อ Epoch · Speedup / Efficiency %s · เครื่องเปิด %s · ใบแจ้งหนี้ %s" % (
        c8["เครื่อง (RTX 3090 2 ใบ)"][2], c8["วินาทีต่อ Epoch (1 → 2 GPU)"][2], sp, c8["เครื่องเปิด"][2],
        rx(r"ยอดสุดท้ายในใบแจ้งหนี้คือ \*\*(\$[\d.]+)\*\*"))
    step_core(8, p, "AI ตัวใหม่ทำทั้ง LAB เองด้วยสกิล ตั้งแต่เช่าเครื่องจนลบเครื่อง")
    r8 = reading(p)
    add(answer(8, "สกิล v0 ผ่านในรอบแรก: %s วินาทีต่อ Epoch เร็วขึ้น %s" % (c8["วินาทีต่อ Epoch (1 → 2 GPU)"][2], sp.split(" / ")[0]), [
        "ไม่ต้องเขียนโค้ดใหม่ และไม่มีช่วงรอคนวางพรอมต์ถัดไป เครื่องจึงเปิดสั้นกว่ามาก",
        "เครื่องคนละเครื่อง แต่ทางเชื่อมแบบเดียวกัน (`PHB`) ได้ผลใกล้กัน คือ **1.74 กับ 1.79 เท่า** และ All-reduce 21–23 ms ข้อสรุปจึงทำซ้ำได้"],
        extra=" · Efficiency %s" % sp.split(" / ")[1]))
    num = lambda s: float(re.sub(r"[^\d.]", "", E.plain(s).split()[0]))
    rows8 = [("จำนวนพรอมต์", "", num(c8["จำนวนพรอมต์"][1]), E.plain(c8["จำนวนพรอมต์"][1]), num(c8["จำนวนพรอมต์"][2]), E.plain(c8["จำนวนพรอมต์"][2])),
             ("Speedup", "", num(c8["Speedup / Efficiency"][1]), c8["Speedup / Efficiency"][1].split(" / ")[0], num(sp), sp.split(" / ")[0]),
             ("เครื่องเปิด", "", num(c8["เครื่องเปิด"][1]), c8["เครื่องเปิด"][1], num(c8["เครื่องเปิด"][2]), c8["เครื่องเปิด"][2]),
             ("ค่าเช่า", "", num(c8["ค่าเช่า"][1]), c8["ค่าเช่า"][1], num(c8["ค่าเช่า"][2]), c8["ค่าเช่า"][2])]
    add(S("สกิลได้ Speedup ใกล้เดิม แต่ใช้พรอมต์เดียว และเครื่องเปิดสั้นลงจาก %s เหลือ %s" % (c8["เครื่องเปิด"][1], c8["เครื่องเปิด"][2]),
          pairs(rows8, names=("สั่งทีละขั้น (ขั้นที่ 1–6)", "สกิล v0")) +
          note(r8[2].replace(" · ", " และ "), label="เรื่องเงิน") +
          note(r8[3], label="ข้อควรระวัง") +
          '<p class="cap">ผลของรอบสกิลอยู่ที่ <a href="results/skill_v0_run/metrics.json" target="_blank">results/skill_v0_run/</a> · เทรน %s Epoch ต่อรอบ</p>' % (
              c8["Epoch ต่อรอบ"][2]),
          tag="README · ขั้นที่ 8", cls="mid"))

    # ===== สรุป
    CTX.update(kicker="สรุป", group="สรุป")
    add(part_divider(4, "สรุป", "เพิ่ม GPU จาก 1 เป็น 2 ใบ เร็วขึ้น %.2f เท่า แต่ไม่ได้ถูกลงเสมอ" % R2["speedup"],
                     "<p>ผลรวม ตารางสรุป บทเรียน และสิ่งที่ยังไม่ผ่าน</p>", "img/p30-summary.jpg"))
    add(fig("ผลรวม: %s → %s วินาทีต่อ Epoch ใกล้ Ideal %s แต่ไม่ถึง" % (f1(R1["sec_per_epoch"]), f1(R2["sec_per_epoch"]), f1(R2["ideal_sec_per_epoch"])),
            "results/images/1_epoch_time.png", "ดูแท่งสีส้มที่สูงกว่าจุด ideal · Speedup **%.2f×** · Efficiency **%s%%** · mAP50 %.3f กับ %.3f" % (
                R2["speedup"], f1(R2["efficiency_pct"]), R1["map50"], R2["map50"]), tag="results/metrics.json"))
    add(tbl("สั่งทีละขั้นกับสกิล v0 ได้ข้อสรุปเดียวกัน: Speedup %s กับ %s" % (
        c8["Speedup / Efficiency"][1].split(" / ")[0], sp.split(" / ")[0]), cmp8))
    lessons_fb = lambda: S("บทเรียนของ LAB 4", cards([
        (("1", "วัดจริง ไม่เดา"), "เครื่องเดียวกัน ค่าการเทรนเดียวกัน เปลี่ยนแค่จำนวน GPU", "navy"),
        (("2", "การ Sync คือเพดานของ Speedup"), "step เหลือครึ่ง แต่แต่ละ step ช้าลง", ""),
        (("3", "ดูทางเชื่อมก่อนเช่า"), "`nvidia-smi topo -m`", ""),
        (("4", "เร็วขึ้นไม่ได้แปลว่าถูกลง"), "คิดจากราคา ณ วันที่เช่า", "warn"),
        (("5", "เงินเดินตลอดเวลาที่เครื่องเปิด"), "ลบเครื่องเสมอ", "bad"),
        (("6", "สกิลทำซ้ำได้ในคำสั่งเดียว"), "ดีขึ้นทีละเวอร์ชันจากหลักฐาน", "ok")], 3), cls="mid")
    add(nfig2("n34-lessons", "บทเรียนของ LAB 4: วัดจริง ดูทางเชื่อม คิดเงินต่อ Epoch และลบเครื่องเสมอ",
              "สกิลดีขึ้นทีละเวอร์ชันจากหลักฐานของการรันจริง", lessons_fb))
    fails = table("ขั้นที่ 8", "จุดที่พลาด")
    add(S("v0 ยังไม่สมบูรณ์: มี %d จุดที่ AI ต้องแก้หรือเดาเอง และควรแก้ใน v1" % len(fails["rows"]), cards(
        [((k + 1, r[1]), r[0], "warn") for k, r in enumerate(fails["rows"])], 3) +
        note(" ".join(para("ขั้นที่ 8", "วิธีปรับคือ")["lines"]), label="ถัดไป"), tag="README · ขั้นที่ 8"))
    add(E.divider("จบ LAB 4", "ถัดไป: ปรับสกิลเป็น v1 ตามจุดที่พลาด",
                  '<p>รายละเอียดเต็มของ LAB นี้: <a href="README.md" target="_blank">README.md</a> · พรอมต์ทุกขั้น: '
                  '<a href="PROMPTS.md" target="_blank">PROMPTS.md</a> · <a href="../README.md" target="_blank">กลับหน้ารวมของบท</a></p>'))
    return E.SL


def sec_name(prefix):
    return next(s["text"] for s in SECS if s["text"].startswith(prefix))


# ------------------------------------------------------------------ ตรวจตัวเลข: ทุกตัวเลขในสไลด์ต้องมีใน README หรือไฟล์ผล
def check_numbers(slides):
    src = README + E.read("results/metrics.json") + E.read("PROMPTS.md")
    src_n = set(re.findall(r"\d+(?:[.,]\d+)*", src))
    src_n |= {x.replace(",", "") for x in src_n}
    bad = set()
    for s in slides:
        txt = s.get("raw", "") + s.get("title", "") + s.get("body", "")
        txt = re.sub(r"<style>.*?</style>|<svg.*?</svg>", " ", txt, flags=re.S)
        txt = re.sub(r"<[^>]+>", " ", txt)
        txt = re.sub(r"พรอมต์ทั้งหมด \d+ บรรทัด|ส่วนที่ \d+/\d+ · บรรทัด \d+–\d+ จาก \d+", "", txt)
        txt = re.sub(r"(?:src|href)=\"[^\"]*\"", "", txt)
        txt = re.sub(r"\b(?:img|image|results)/\S+", "", txt)
        for n in re.findall(r"\d+(?:[.,]\d+)*", txt):
            if n not in src_n and n.replace(",", "") not in src_n:
                bad.add(n)
    return sorted(bad)


if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    sl = build()
    E.write(sl, out=OUT, title=TITLE)
    print("ตัวเลขที่ไม่พบใน README/ไฟล์ผล:", check_numbers(sl) or "ไม่มี")
