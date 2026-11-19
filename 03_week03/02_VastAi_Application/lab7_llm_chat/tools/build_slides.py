#!/usr/bin/env python3
"""สร้างสไลด์ LAB7_LLM_Chat_Slides.html ของ LAB 7 (แชทบอท LLM: GPU 1 ใบคุยพร้อมกันได้กี่คน)

  python tools/build_slides.py            (รันจากโฟลเดอร์ของบท)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · อธิบายด้วยภาพที่มีป้ายในภาพ · ผลจริงแสดงด้วยกราฟจริงและส่วนที่ตัดจากหน้าจอจริง
รายละเอียดเต็มของทุกหัวข้ออยู่ใน README.md (สไลด์ไม่ได้ยกทุกตารางมา)

ที่มาของเนื้อหา
- ตาราง พรอมต์ และ "อ่านผลอย่างไร": อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร) หรือเรียบเรียงจาก README โดยคงตัวเลขเดิม
- ตัวเลขผล: จากตารางของ README.md (ซึ่งมาจาก results/ ของรอบจริง)
- ภาพอธิบายใหม่: tools/slides_figures.py (FIGS, FIGS2) · ภาพ c*.jpg = ส่วนที่ตัดจากหน้าจอจริงใน image/ (ไม่แก้พิกเซล)
- เครื่องมือเรนเดอร์: tools/slides_engine.py
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, para, CTX, add, note, fig, explain, tiles, cards, versus, tbl, bars)
from slides_figures import FIGS

S = E.slide
SECS = E.load("README.md")
FIG = {f["img"]: f for f in FIGS}
OUT, TITLE = "LAB7_LLM_Chat_Slides.html", "LAB 7 · แชทบอท LLM · Slides"


# ------------------------------------------------------------------ ตัวช่วยอ่าน README
def quote(prefix, k=0):
    """ข้อความในกล่อง > ลำดับ k ของหัวข้อ (ไม่ใช่พรอมต์)"""
    qs = [b for b in sec(prefix) if b["t"] == "alert"]
    return " ".join(" ".join(x["lines"]) for x in qs[k]["blocks"] if x["t"] == "p")


def took(prefix):
    """บรรทัด *ใช้เวลา ...* ของขั้นนั้น"""
    for b in sec(prefix):
        if b["t"] == "p" and b["lines"][0].startswith("*ใช้เวลา"):
            return b["lines"][0].strip("*").split("·")[0].replace("ใช้เวลา", "").strip()
    return ""


def bullets(prefix, start):
    for b in sec(prefix):
        if b["t"] == "ul" and b["items"][0].startswith(start):
            return b["items"]
    raise KeyError(start)


def theory(prefix, key):
    """ข้อ "คืออะไร/ทำไม/ทำงานอย่างไร/ตัวเลข" ของทฤษฎีข้อนั้น"""
    for b in sec(prefix):
        if b["t"] == "ul":
            for it in b["items"]:
                if it.startswith("**%s" % key):
                    return re.sub(r"^\*\*[^*]+\*\*:\s*", "", it)
    raise KeyError((prefix, key))


# ------------------------------------------------------------------ รูปแบบสไลด์ของเด็คนี้
def side(points):
    return "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(points))


def pic(title, src, points, post="", tag=""):
    """ภาพใหญ่ราว 2 ใน 3 ของสไลด์ + ประเด็นที่พูด 2-4 ข้อด้านขวา"""
    img = E.img_tag({"t": "img", "src": src, "alt": E.plain(title)})
    return S(title, '<div class="ex pic"><div class="fig">%s</div><div class="side fitbox">%s%s</div></div>' % (img, side(points), post),
             tag=tag, maxfs=1.25)


def nfig(key, title):
    f = FIG[key]
    return pic(title, "img/%s.jpg" % key, f["steps"])


def shot(title, crop, full, body, cap="ส่วนหนึ่งของคำตอบจริง", tag="ผลจริงของผู้สอน"):
    """ส่วนที่ตัดจากหน้าจอจริงของ Claude Code (ขยายได้) ด้านบน + ตัวเลขใหญ่ด้านล่าง"""
    img = E.img_tag({"t": "img", "src": crop, "alt": "ส่วนหนึ่งของคำตอบจริงของ Claude Code"})
    capt = '<p class="cap">%s · ภาพเต็ม: <a href="%s" target="_blank">%s</a></p>' % (md(cap), full, full)
    return S(title, '<div class="sr"><div class="fig">%s</div>%s<div class="srb">%s</div></div>' % (img, capt, body), tag=tag, maxfs=1.2)


def chartside(title, chart_html, points, tag=""):
    """แผนภูมิที่เรียงพิมพ์จากตัวเลขของ README (ค่าตรงตามจริงเสมอ) + ประเด็นด้านขวา"""
    return S(title, '<div class="ex"><div class="chartbox">%s</div><div class="side fitbox">%s</div></div>' % (chart_html, side(points)),
             tag=tag, maxfs=1.25)


def band(title, src, sentence):
    """ภาพถ่ายเต็มสไลด์ + ข้อความ 1 ประโยคบนแถบ"""
    raw = ('<div class="bd"><div class="bk">%s</div><div class="bs">%s</div></div><div class="imgnote">ภาพจำลอง</div>'
           % (E.esc(CTX["kicker"]), md(sentence)))
    return {"raw": raw, "cls": "bandsl", "style": ' style="background-image:url(%s)"' % src, "title": title, "kicker": "", "tag": "", "lead": ""}


def cover(title, sub, img, small):
    """หน้าปก: ชื่อบทด้านซ้าย ภาพปกของบท (ภาพการ์ตูน "ทำไปเพื่ออะไร") ด้านขวา"""
    hint = ('กด <span class="kbd">→</span> หรือ <span class="kbd">Space</span> เพื่อไปต่อ · <span class="kbd">O</span> สารบัญ · '
            '<span class="kbd">F</span> เต็มจอ · คลิกภาพเพื่อขยาย')
    raw = ('<img class="covimg" src="%s" alt="LAB 7 ทำไปเพื่ออะไร"><div class="inner"><div class="small">%s</div><h1>%s</h1>'
           '<div class="sub">%s</div><div class="hint">%s</div></div>') % (img, E.esc(small), E.esc(title), E.esc(sub), hint)
    return {"raw": raw, "cls": "cover cx", "style": "", "title": "ปก", "kicker": "", "tag": "", "lead": ""}


def divider(n, title, what, time, res):
    sub = ('<p>%s</p><div class="facts"><div><span class="fl">เวลาจริง</span>%s</div><div><span class="fl">ผลจริง</span>%s</div></div>'
           % (md(what), md(time), md(res)))
    return E.divider("ขั้นที่ %d" % n, title, sub, small="ภาค LAB · ขั้นที่ %d จาก 9" % n)


VARY = ("ตัวเลขของคุณอาจต่างจากของผู้สอน เพราะเครื่องที่เช่าได้ คำถามและคำตอบที่ AI เขียน และโค้ดที่ AI เขียนไม่เหมือนกันทุกครั้ง "
        "สิ่งที่ต้องเหมือนกันคือไฟล์และรูปแบบของผล")

CHECKS = {
    1: (["มีเครื่องป้าย `vapp-lab7` ที่มี RTX 3090 **2 ใบ** และราคารวมไม่เกิน $0.60 ต่อชั่วโมง",
         "เข้าเครื่องได้และเห็น GPU ครบ 2 ใบ",
         "อุณหภูมิ GPU ทุกใบตอนว่างไม่เกิน 60°C",
         "AI สรุปเป็นตาราง: GPU · ราคา · ที่ตั้ง · CPU cores · RAM · อุณหภูมิ · เวลารอ และบอกว่าเครื่องยังเปิดอยู่"],
        "ผลของผู้สอน: RTX 3090 2 ใบ $0.369 ต่อชั่วโมง ที่ Missouri สหรัฐฯ 16 cores อุณหภูมิ GPU 0 48°C และ GPU 1 54°C ใช้เวลา 2 นาที"),
    2: (["มีไฟล์ `lab7_llm_chat/code/cluster.sh` บนเครื่องเรา (นอก container)",
         "แชทบอทตอบคำถามทดสอบ 2 ข้อพร้อม key ได้ และบอกจำนวน token กับเวลา",
         "เรียกแบบไม่มี key ถูกปฏิเสธ",
         "สรุปไม่แสดงค่า key และ `HF_TOKEN` และไม่มี token ค้างบนเครื่องเช่า",
         "AI บอกเวอร์ชัน vLLM และเวลาติดตั้ง ดาวน์โหลดโมเดล และเปิด server"],
        "ผลของผู้สอน: vLLM 0.34.0 ดาวน์โหลดโมเดล 7.6 GB ใน 67 วินาที เปิด server 145 วินาที ได้ 84.3 และ 84.9 token/วินาที ไม่มี key ได้ HTTP 401 ใช้เวลา 10 นาที"),
    3: (["มีไฟล์ `lab7_llm_chat/code/loadtest.py` และผล JSON ใน `lab7_llm_chat/results`",
         "มีภาพ `lab7_llm_chat/results/dataset_samples.png` (คำถาม 8 ข้อคู่กับคำตอบจริง)",
         "ตารางมีทุกระดับ N: TTFT p50 / p95 · ความเร็วต่อผู้ใช้ · token/วินาทีรวม · รอคิว · ผ่าน SLO ไหม",
         "ตัวยิงหยุดเองเมื่อไม่ผ่าน SLO 2 ระดับติดกัน",
         "มีประโยค \"GPU 1 ใบ แบบทีละคำถาม รองรับผู้ใช้พร้อมกันได้ N คน\""],
        "ผลของผู้สอน: รองรับได้ **2 คน** TTFT p95 ที่ N=2 เท่ากับ 1.60 วินาที ส่วน N=3 ไม่ผ่าน (2.92 วินาที) ใช้เวลา 9 นาที"),
    4: (["มีผลตรวจก่อนวัด: อุณหภูมิ · clock · ความเร็วตอบผู้ใช้ 1 คน",
         "ตารางมีทุกระดับ N = 1 ถึง 256 ทีละ 32 พร้อม GPU utilization และ CPU% ของตัวยิงโหลด",
         "ถ้ามีระดับก้ำกึ่ง: มีค่าทั้ง 3 ครั้งและค่ากลาง",
         "มีการเทียบกับแบบทีละคำถาม: รองรับผู้ใช้กี่เท่า และ token/วินาทีรวมสูงสุดกี่เท่า",
         "มีประโยค \"GPU 1 ใบ ด้วย Continuous Batching รองรับผู้ใช้พร้อมกันได้ N คน\""],
        "ผลของผู้สอน: รองรับได้ **192 คน** (96 เท่า) token/วินาทีรวมสูงสุด 3,097 (37.6 เท่า) ไม่มีระดับไหนต้องวัดซ้ำ ใช้เวลา 9 นาที"),
    5: (["มีผลตรวจ GPU 2 ใบก่อนวัด และบอกถ้าเร็วต่างกันเกิน 10%",
         "ตาราง N = 128 ถึง 512 ทีละ 64 ระบุว่าระดับไหนวัดซ้ำ",
         "มีไฟล์ `lab7_llm_chat/code/report.py` · `results/metrics.json` และกราฟ (TTFT p95 · token/วินาทีรวม · ความจุเทียบจำนวน GPU)",
         "มีประโยค \"1 ใบ N₁ คน → 2 ใบ N₂ คน (x เท่า, efficiency y%)\"",
         "ค่าประมาณของ 3 ใบระบุว่า **เป็นการคำนวณ ไม่ใช่ผลวัด**"],
        "ผลของผู้สอน: 1 ใบ 192 คน → 2 ใบ 384 คน (2.00 เท่า, Efficiency 100%) GPU 2 ใบเร็ว 84.0 และ 84.4 token/วินาที ใช้เวลา 8 นาที"),
    6: (["`loadtest.py` มีตัวเลือกให้ 20% ของคำถามขอคำตอบยาวได้ถึง 600 token",
         "ยิง 2 รอบที่ผู้ใช้ 448 คน: Round Robin แล้ว least_conn",
         "`report.py` มีตารางและกราฟเทียบ 2 วิธี (TTFT p95 และจำนวนคำถามที่ GPU แต่ละใบกำลังทำ)",
         "AI อธิบายว่าทำไมผลต่างกัน (หรือไม่ต่าง)"],
        "ผลของผู้สอน: Round Robin ได้ TTFT p95 1.55 วินาที least_conn ได้ 0.36 วินาที ทั้งสองวิธีไม่ผ่าน SLO ข้อความเร็ว ใช้เวลา 10 นาที"),
    7: (["โค้ดทุกไฟล์อยู่ใน `lab7_llm_chat/code` และ `metrics.json` กับกราฟอยู่ใน `lab7_llm_chat/results`",
         "ไม่มีเครื่องป้าย `vapp-lab7` ค้างในบัญชี และไม่มีเครื่องป้ายอื่นถูกแตะ",
         "มีสรุปค่าใช้จ่ายจริง: อายุเครื่อง · ราคาต่อชั่วโมง · GPU · disk · รับส่งข้อมูล"],
        "ผลของผู้สอน: อายุเครื่อง 0.80 ชั่วโมง ราคา $0.369 ต่อชั่วโมง รวม $0.597 ใช้เวลา 2 นาที"),
    8: (["มีไฟล์ `lab7_llm_chat/skill_v0/SKILL.md` ที่มี name และ description",
         "SKILL.md มีค่าที่ปรับได้พร้อมค่าเริ่มต้น · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน (ลบเครื่องเสมอ)",
         "มีโค้ดที่ใช้ได้แล้วใน `lab7_llm_chat/skill_v0/scripts`",
         "สกิลถูกติดตั้งที่ `.claude/skills/llm-chat-capacity` ของโฟลเดอร์ปัจจุบัน",
         "ปิดแล้วเปิด Claude Code ใหม่ 1 ครั้งก่อนขั้นที่ 9"],
        "ผลของผู้สอน: สกิล `llm-chat-capacity` และสคริปต์ 8 ไฟล์ใน `scripts/` ไม่ต้องเช่าเครื่อง ใช้เวลา 3 นาที"),
    9: (["AI ใช้สกิล `llm-chat-capacity` และโค้ดใน `scripts/` ไม่เขียนใหม่",
         "ผลอยู่ใน `lab7_llm_chat/results/skill_v0_run` และผลเดิมใน `lab7_llm_chat/results` ไม่ถูกเขียนทับ",
         "มีตารางความจุ 2 แบบ · เวลาแต่ละขั้น · ค่าใช้จ่ายจริง",
         "เครื่องป้าย `vapp-lab7-skill` ถูกลบแล้ว"],
        "ผลของผู้สอน: RTX 3090 1 ใบ $0.196 ต่อชั่วโมง ทีละคำถาม 2 คน Continuous Batching 160 คน ยอดในบิล $0.093 ใช้เวลา 24 นาที"),
}

TITLES = {1: "เช่าเครื่อง RTX 3090 2 ใบ", 2: "เปิดแชทบอทบน GPU 1 ใบ", 3: "ตัวยิงโหลด และ Baseline: ตอบทีละคำถาม",
          4: "Continuous Batching บน GPU 1 ใบ", 5: "เพิ่มเป็น 2 GPU หลัง Load Balancer", 6: "ทดลองเสริม: Round Robin เทียบ least_conn",
          7: "ลบเครื่องและสรุปค่าใช้จ่าย (ห้ามข้าม)", 8: "สร้างสกิลเวอร์ชัน 0", 9: "ลองใช้สกิลทำซ้ำในพรอมต์เดียว"}


def start(n):
    """ตั้ง kicker และกลุ่มของขั้น n ก่อนสร้างสไลด์ของขั้นนั้น · คืนคำค้นหัวข้อของ README"""
    CTX.update(kicker="ภาค LAB · ขั้นที่ %d จาก 9 · %s" % (n, TITLES[n]), group="ขั้นที่ %d" % n)
    return "ขั้นที่ %d ·" % n


def lab_step(n, what, res, picture, result_slides):
    """ลำดับคงที่ของ 1 ขั้น: หน้าคั่น → ภาพ + ขั้นตอน → พรอมต์ → ตรวจผล → ผลจริง → อ่านผล"""
    prefix = start(n)
    st = "ขั้นที่ %d · %s" % (n, TITLES[n])
    for s in [picture] + result_slides:      # สไลด์ถูกสร้างก่อนเรียก start() จึงตั้ง kicker ของขั้นให้ใหม่
        if "raw" not in s:
            s["kicker"] = CTX["kicker"]
    add(divider(n, TITLES[n], what, took(prefix), res))
    add(picture)
    add(E.prompt_slides(E.prompt_code(prefix), CTX["kicker"], st))
    items, ref = CHECKS[n]
    add(E.check_slide("step%d" % n, items, ref, VARY, st))
    for s in result_slides:
        add(s)


RD = "README · อ่านผลอย่างไร"


# ------------------------------------------------------------------ โครงเรื่อง
def build():
    h1 = SECS[0]["text"]
    summary = table("การทดลอง", "จำนวน GPU")

    # ===== 1 · เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    head, sub = h1.split(":", 1)
    add(cover(head.strip(), sub.strip(), "image/why6-chat.png", "03_week03 · 02_VastAi_Application · LAB 7"))
    CTX["kicker"] = "ภาพรวมของบท"
    add(fig("ทั้งเรื่องในภาพเดียว: GPU 1 ใบรับได้ 192 คน และ 2 ใบหลัง Load Balancer รับได้ 384 คน", "results/capacity_vs_gpus.png",
            "จุดทึบคือผลวัดจริง อยู่บนเส้นประ ideal พอดี (**2.00 เท่า, Efficiency 100%**) ส่วนจุดโปร่งที่ 3 ใบเป็นการคำนวณ ไม่ใช่ผลวัด"))
    add(fig("บทนี้มี 4 ส่วน เริ่มจากโจทย์ของร้าน และจบที่สกิลที่ใช้วัดซ้ำได้ในคำสั่งเดียว", "img/n21-roadmap.jpg",
            "ส่วนที่ 3 คืองานหลักของ LAB (ขั้นที่ 1–7) และส่วนที่ 4 คือขั้นที่ 8–9 กับบทสรุป รายละเอียดเต็มอยู่ใน [`README.md`](README.md)"))
    add(fig("วิธีใช้สไลด์: ใช้แป้นลูกศรเปลี่ยนหน้า และใช้ปุ่มคัดลอกพรอมต์ของแต่ละขั้น", "img/n22-howto.jpg",
            "ปุ่มคัดลอกให้ข้อความเดียวกับ `README.md` ทุกตัวอักษร ช่องติ๊กของสไลด์ตรวจผลจำค่าไว้ในเบราว์เซอร์นี้ ควรเปิดสไลด์จากโฟลเดอร์ `lab7_llm_chat` เพื่อให้ลิงก์ไฟล์ทำงาน"))

    # ===== 2 · โจทย์ ข้อมูล และโมเดล
    CTX.update(kicker="", group="โจทย์ ข้อมูล และโมเดล")
    add(E.divider("ส่วนที่ 1", "โจทย์ ข้อมูล และโมเดล", "<p>คำถามของร้าน ชุดคำขอที่ใช้ทดสอบ และโมเดลกับโปรแกรมเสิร์ฟ</p>", "img/s01-theory.jpg",
                  small="ส่วนที่ 1 จาก 4"))
    CTX.update(kicker="ส่วนที่ 1 · โจทย์ ข้อมูล และโมเดล")
    add(fig("โจทย์ของร้าน: GPU 1 ใบ รองรับผู้ใช้พร้อมกันได้กี่คน", "image/why6-chat.png",
            "ร้านขายของใช้ในบ้านต้องการเปิดแชทบอทตอบลูกค้าด้วยงบเช่า GPU ที่จำกัด คำตอบในบทนี้ได้จากการวัดจริงบนเครื่องเช่า"))
    arch = [re.sub(r"^\d+\.\s*", "", x) for x in para("ทำไปเพื่ออะไร", "1. **Baseline**")["lines"]]
    add(pic("วัดจริง 3 แบบ บนเครื่องเดียวกัน ด้วยเกณฑ์เดียวกัน", "img/n23-abc.jpg",
            ["**%s** %s" % ("ABC"[k], it) for k, it in enumerate(arch)] +
            ["ขั้นที่ 1–7 คืองานหลัก ขั้นที่ 8–9 เก็บงานทั้งหมดเป็น **สกิลเวอร์ชัน 0**"]))
    ds = {E.plain(r[0]): r[1] for r in table("รู้จักข้อมูลที่ใช้ทดสอบ", "หัวข้อ")["rows"]}
    add(pic("ข้อมูลที่ใช้ทดสอบคือชุดคำขอ 40 ข้อ ไม่ใช่ Dataset สาธารณะ", "img/n24-workload.jpg", [
        "LAB นี้ไม่ได้เทรนโมเดล ข้อมูลจึงเป็นคำถามสั้น ๆ ภาษาไทยของลูกค้าร้านขายของใช้ในบ้าน",
        "AI เขียนคำถามขึ้นเองตามพรอมต์ขั้นที่ 3 และฝังไว้ในตัวยิงโหลด รอบของคุณจะได้คำถามชุดใหม่",
        "ขาเข้า 71–91 token ต่อคำขอ (system prompt + คำถาม) และคำตอบจริง 57–121 token เฉลี่ยราว 84 token"]))
    add(fig("ตัวอย่างคำขอจริง: คำถามของลูกค้าคู่กับคำตอบของแชทบอท", "img/c10-samples-top3.jpg",
            "ส่วนหนึ่งของภาพจริง 3 ข้อจาก 8 ข้อ (คอลัมน์คำถามและคำตอบ) · token ขาเข้า / คำตอบ: 71 / 68, 86 / 69, 83 / 98 · "
            "TTFT 0.05 วินาที · เวลารวม 0.86, 0.85, 1.20 วินาที · ภาพเต็ม: [results/dataset_samples.png](results/dataset_samples.png) "
            "ข้อมูลดิบ: [results/dataset_samples.json](results/dataset_samples.json)"))
    add(pic("คำขอ 1 รายการคือ POST /v1/chat/completions ที่ส่งไปยัง NGINX พอร์ต 8000", "img/n25-request.jpg", [
        "`messages` มี 2 ส่วน: `system` กำหนดบทบาทพนักงานร้านให้ตอบภาษาไทย สุภาพ กระชับ ไม่เกิน 3 ประโยค และ `user` คือคำถาม 1 ข้อ",
        "`stream: true` ส่งคำตอบกลับทีละ token จึงจับเวลา token แรกได้",
        "`stream_options.include_usage: true` ส่งจำนวน token มาตอนจบ ใช้คำนวณความเร็ว"]))
    obs = bullets("รู้จักข้อมูลที่ใช้ทดสอบ", "**ความจุขึ้นกับ")
    add(pic("ตัวเลขความจุขึ้นกับความยาวคำตอบ", "img/n26-length.jpg", [
        obs[0].split("**:", 1)[1].strip(), obs[1], obs[2]]))
    add(fig("โมเดล Qwen3-4B-Instruct-2507 รับข้อความแชทและตอบออกมาทีละ token", "image/model-qwen3-4b.png",
            "โมเดลมีขนาด 4 พันล้าน parameter ไฟล์โมเดล 7.6 GB ใช้ความยาวบริบท 4,096 token และใช้ตอบอย่างเดียว (Inference) โดยไม่เทรนเพิ่ม"))
    add(fig("โมเดลอย่างเดียวให้บริการหลายคนไม่ได้ จึงต้องมีโปรแกรมเสิร์ฟ vLLM", "image/model-vllm.png",
            "vLLM รับคำขอแบบ OpenAI-compatible API และทำ Continuous Batching ได้สูงสุด 256 คำถามพร้อมกัน โดยเปิด 1 ตัวต่อ 1 GPU"))

    # ===== 3 · ทฤษฎี
    CTX.update(kicker="", group="ทฤษฎีที่ต้องรู้")
    add(E.divider("ส่วนที่ 2", "ทฤษฎีที่ต้องรู้ 8 ข้อ",
                  "<p>วัดอะไร ตัดสินอย่างไร และทำไม Continuous Batching กับ Load Balancer จึงรับผู้ใช้ได้มากขึ้น</p>", small="ส่วนที่ 2 จาก 4"))
    CTX.update(kicker="ทฤษฎี · 1 จาก 8 · Concurrent Users, Throughput และ Latency", group="ทฤษฎี · 1–2 · ตัวชี้วัด")
    add(fig("จำนวนผู้ใช้ (N) แปลงเป็น Throughput ได้ด้วยเวลาต่อคำถาม", "image/t6-users-throughput.png",
            "Throughput = N ÷ เวลาต่อคำถาม เพราะผู้ใช้จำลองแต่ละคนถาม รอจนจบ แล้วถามข้อใหม่ทันที (closed-loop)"))
    add(fig("ทีละคำถาม Throughput แบนที่ราว 82 ส่วน Continuous Batching อิ่มตัวที่ราว 3,000 token/วินาที", "results/throughput_vs_n.png",
            theory("1 ·", "ตัวเลขจาก LAB นี้")))
    CTX.update(kicker="ทฤษฎี · 2 จาก 8 · TTFT และ token ต่อวินาที")
    add(fig("ผู้ใช้รู้สึกช้าจาก 2 อย่าง คือรอ token แรก (TTFT) และความเร็วต่อผู้ใช้", "image/t6-ttft.png",
            theory("2 ·", "ตัวเลขจาก LAB นี้")))
    CTX.update(kicker="ทฤษฎี · 3 จาก 8 · SLO และนิยาม \"รองรับได้ N คน\"", group="ทฤษฎี · 3–5 · SLO และการวัด")
    add(fig("SLO มี 3 ข้อ ต้องผ่านครบทุกข้อ และทุกระดับที่ต่ำกว่าก็ต้องผ่าน", "image/t6-slo.png",
            theory("3 ·", "ตัวเลขจาก LAB นี้")))
    add(fig("ความเร็วต่อผู้ใช้ p5 ตัดเส้น 15 token/วินาทีหลังจุดความจุ", "results/speed_p5_vs_n.png",
            "ดูเส้นสีส้มและสีเขียวที่ลดลงตาม N แล้วตัดเส้นประ 15 token/วินาที " + quote("3 ·")))
    CTX.update(kicker="ทฤษฎี · 4 จาก 8 · วัดความจุอย่างไรให้เชื่อได้")
    add(fig("ตัวเลขความจุเชื่อได้เมื่อตรวจ GPU ก่อนวัด ไล่ N ละเอียด และวัดซ้ำในระดับที่ก้ำกึ่ง", "image/t6-measure.png",
            quote("4 ·")))
    CTX.update(kicker="ทฤษฎี · 5 จาก 8 · จุดอิ่มตัว (Saturation Knee)")
    add(fig("ทีละคำถามหักศอกทันทีที่มีคนที่ 2 ส่วน Continuous Batching ไม่มีคิวจนถึง N=256", "results/knee_ttft.png",
            "กฎของ Little: เวลาต่อคำถาม = N ÷ จำนวนคำถามที่เสร็จต่อวินาที"))
    add(pic("ใน Continuous Batching มีเพดาน 2 ชั้นซ้อนกัน", "img/n27-ceilings.jpg", [
        "**เพดานที่ 1** ความเร็วต่อผู้ใช้ตกเกณฑ์ 15 token/วินาทีหลัง N=192 เพราะ GPU ต้องแบ่งกำลังให้ทุกคน",
        "**เพดานที่ 2** เมื่อเกิน 256 ช่องต่อ GPU คำถามใหม่ต้องรอคิว ในขั้นที่ 6 GPU ใบหนึ่งชน 256 ช่อง TTFT p95 จึงกระโดดเป็น 1.55 วินาที",
        theory("5 ·", "ทำไมต้องรู้")]))
    CTX.update(kicker="ทฤษฎี · 6 จาก 8 · Continuous Batching", group="ทฤษฎี · 6 · Continuous Batching")
    add(fig("ปัญหาของการตอบทีละคำถาม: GPU ทำงานเต็ม แต่รับได้ 2 คน", "image/cb-problem.png",
            "คนที่มาทีหลังต้องรอให้คนก่อนหน้าได้คำตอบครบก่อน TTFT จึงเพิ่มตาม N"))
    add(fig("Continuous Batching รับคำถามใหม่เข้าแทรกได้ทุกรอบ ไม่ต้องรอทั้งชุดจบ", "image/cb-how.png",
            theory("6 ·", "ทำไมต้องใช้")))
    add(fig("GPU ใบเดิมรองรับผู้ใช้จาก 2 เป็น 192 คน (96 เท่า)", "image/cb-result.png", quote("6 ·")))
    CTX.update(kicker="ทฤษฎี · 7 จาก 8 · Load Balancer", group="ทฤษฎี · 7–8 · Load Balancer และ Scaling")
    add(fig("Load Balancer เป็นทางเข้าเดียวที่แจกงานให้หลาย GPU", "image/lb-what.png", theory("7 ·", "ทำไมต้องใช้")))
    add(fig("Round Robin แจกจำนวนคำขอเท่ากัน ส่วน least_conn แจกงานค้างเท่ากัน", "image/lb-rr-vs-lc.png",
            "ผู้ใช้ 448 คน โดย 20% ขอคำตอบยาว ได้ TTFT p95 **1.55 วินาที** เทียบกับ **0.36 วินาที**"))
    add(fig("Streaming ต้องปิด Proxy Buffering เพื่อให้ token ไหลผ่าน NGINX ทันที", "image/lb-buffering.png", quote("7 ·")))
    CTX.update(kicker="ทฤษฎี · 8 จาก 8 · Scaling Efficiency")
    add(fig("Efficiency = ความจุ k ใบ ÷ (k × ความจุ 1 ใบ) และ LAB นี้ได้ 100%", "image/t6-efficiency.png", quote("8 ·")))

    # ===== 4 · ภาค LAB
    CTX.update(kicker="", group="ภาค LAB")
    add(E.divider("ส่วนที่ 3", "ภาค LAB: 9 ขั้น ขั้นละ 1 พรอมต์",
                  "<p>ขั้นที่ 1–7 ใช้เครื่องเดียวกัน ต่างกันเพียงวิธีเสิร์ฟและจำนวน GPU ส่วนขั้นที่ 8–9 เก็บงานเป็นสกิล v0</p>", "img/s02-lab.jpg",
                  small="ส่วนที่ 3 จาก 4"))
    CTX.update(kicker="ภาค LAB · แผนที่และการเตรียม")
    add(fig("แผนที่ของ LAB: 9 ขั้น ทุกขั้นคือ 1 พรอมต์", "image/lab7-overview.png",
            "AI เขียนโค้ดทุกไฟล์จากพรอมต์ลงในโฟลเดอร์ `lab7_llm_chat/code/` ซึ่งตอนเริ่มยังไม่มี"))
    add(pic("ระบบที่จะสร้าง: GPU 1 ใบในขั้นที่ 2–4 และ GPU 2 ใบหลัง NGINX ในขั้นที่ 5–6", "image/lab7-system.png", [
        "ผู้ใช้จำลอง N คนแบบ closed-loop สุ่มถามจาก 40 คำถาม คำตอบไม่เกิน 150 token ตัวยิงโหลดอยู่บนเครื่องเช่าเดียวกับแชทบอท",
        "ไล่ N ทีละ 32 คน (1 ใบ) และทีละ 64 คน (2 ใบ) วัดระดับละ 30 วินาที ด้วย SLO ชุดเดียวกันทุกแบบ: TTFT p95 ≤ 2 วินาที, 95% ของคำถาม ≥ 15 token/วินาที และ error < 1%",
        "ขั้นที่ 1–7 ใช้เวลารวมราว 49 นาที เครื่องเปิด 0.80 ชั่วโมง ค่าเช่า **$0.597** ส่วนขั้นที่ 9 ใช้อีก 24 นาที **$0.093**"]))
    add(pic("ก่อนเริ่ม: เตรียม key เปิดโฟลเดอร์ให้ถูก และทำทุกขั้นให้ครบในรอบเดียว", "img/n28-before.jpg", [
        "ทำ LAB 0 ก่อน เพื่อเตรียม key 3 ตัวตามหน้ารวมของบท [../README.md](../README.md)",
        "เปิด Claude Code ที่ `02_VastAi_Application` เพราะ \"โฟลเดอร์ปัจจุบัน\" ในพรอมต์หมายถึงโฟลเดอร์นั้น",
        "เครื่องคิดเงินตั้งแต่ขั้นที่ 1 ถึงขั้นที่ 7 จึงต้องทำขั้นที่ 1 → 9 ให้ครบในรอบเดียว และห้ามข้ามขั้นที่ 7"]))

    # ----- ขั้นที่ 1
    lab_step(1, "AI ค้นหาเครื่องตามเกณฑ์ เช่า รอจนพร้อม แล้วตรวจว่าเห็น GPU ครบ 2 ใบและ GPU ไม่ร้อน",
             "RTX 3090 2 ใบ ราคา $0.369 ต่อชั่วโมง",
             nfig("n01-step1-rent", "AI กรองเครื่องตามเกณฑ์ เลือกเครื่องที่ถูกที่สุด แล้วตรวจอุณหภูมิ GPU"), [
                 shot("ผลจริง: ได้เครื่องที่ถูกที่สุดจาก 15 เครื่องที่ผ่านเงื่อนไข", "img/c01-step1-table.jpg", "image/lab7-step1.png", tiles([
                     ("RTX 3090", "2 ใบ", "เข้าเครื่องแล้วเห็นครบทั้ง 2 ใบ", ""),
                     ("ราคา", "$0.369", "ต่อชั่วโมง (เพดาน $0.60)", "ok"),
                     ("อุณหภูมิตอนว่าง", "48 / 54°C", "GPU 0 / GPU 1 (เกณฑ์ไม่เกิน 60°C)", "ok")]),
                     cap="ส่วนหนึ่งของคำตอบจริง ที่ Missouri สหรัฐฯ 16 cores เข้า SSH ได้ใน 34 วินาที"),
                 pic("อ่านผล: เงื่อนไขในพรอมต์มีผลกับราคาจริง", "img/n29-step1-read.jpg", [
                     "เช่า **2 ใบตั้งแต่แรก** แม้ขั้นที่ 2–4 ใช้ใบเดียว ทุกแบบจึงวัดบนเครื่องเดียวกัน",
                     "เครื่องในจีนราคา $0.326 ถูกกว่า แต่ถูกตัดออกตามข้อ 3 ของพรอมต์",
                     "เครื่องนี้ได้ 48°C และ 54°C จึงผ่านเกณฑ์อุณหภูมิตอนว่างไม่เกิน 60°C",
                     "**ตั้งแต่ขั้นนี้เครื่องคิดเงิน** ชั่วโมงละ $0.37 จนกว่าจะลบเครื่องในขั้นที่ 7"], tag=RD)])

    # ----- ขั้นที่ 2
    t2 = table("ขั้นที่ 2 ·", "คำถามทดสอบ")
    lab_step(2, "AI ติดตั้ง vLLM กับ NGINX ดาวน์โหลดโมเดล แล้วเขียน `cluster.sh` และ `test_chat.py`",
             "vLLM 0.34.0 ผู้ใช้ 1 คนได้ราว 84 token/วินาที",
             nfig("n02-step2-serve", "AI ติดตั้ง vLLM และ NGINX เขียน cluster.sh แล้วทดสอบด้วยคำถาม 2 ข้อ"), [
                 shot("ผลจริง: ผู้ใช้ 1 คนได้ราว 84 token/วินาที และคำขอที่ไม่มี key ถูกปฏิเสธ", "img/c02-step2-test.jpg", "image/lab7-step2.png",
                      cap="ส่วนหนึ่งของคำตอบจริง token ขาเข้า/คำตอบของ 2 ข้อคือ %s และ %s" % (t2["rows"][0][1], t2["rows"][1][1]),
                      body=tiles([("vLLM", "0.34.0", "ติดตั้งรวม 256 วินาที", ""),
                             ("โมเดล 7.6 GB", "67 วินาที", "ดาวน์โหลด และเปิด server 145 วินาที", ""),
                             ("คำถามทดสอบ 2 ข้อ", "%s / %s" % (t2["rows"][0][4].split()[0], t2["rows"][1][4].split()[0]),
                              "token/วินาที (TTFT %s และ %s)" % (t2["rows"][0][2], t2["rows"][1][2]), "ok"),
                             ("ไม่มี key", "401", "ถูกปฏิเสธ", "ok")])),
                 pic("อ่านผล: 84 token/วินาทีคือความเร็วตั้งต้นของ RTX 3090 ใบนี้", "img/n30-step2-read.jpg", [
                     "ผู้ใช้ 1 คนได้ราว 84 token/วินาที ค่านี้จะเห็นซ้ำในทุกขั้นต่อจากนี้",
                     "คำตอบทดสอบทั้ง 2 ข้อชนเพดาน 150 token และถูกตัดกลางประโยค ขั้นที่ 3 จึงขอคำตอบไม่เกิน 3 ประโยค",
                     "NGINX ใส่ header `X-Served-By` ในทุกคำตอบ ใช้ตรวจการแจกงานในขั้นที่ 5–6",
                     "`HF_TOKEN` ใช้เฉพาะตอนดาวน์โหลด และ API key ของแชทบอทอยู่บนเครื่องเช่าเท่านั้น"], tag=RD)])

    # ----- ขั้นที่ 3
    t3 = table("ขั้นที่ 3 ·", "N")
    lab_step(3, "AI เขียน `loadtest.py` เปิดแชทบอทแบบตอบทีละคำถาม ยิงโหลดไล่ N และทำภาพตัวอย่างชุดคำขอ",
             "รองรับผู้ใช้พร้อมกันได้ **2 คน**",
             nfig("n03-step3-loadtest", "ตัวยิงโหลดจำลองผู้ใช้ N คนที่ถาม รอคำตอบจนจบ แล้วถามข้อใหม่ทันที"), [
                 shot("ผลจริง: GPU 1 ใบ แบบทีละคำถาม รองรับผู้ใช้พร้อมกันได้ 2 คน", "img/c03-step3-levels.jpg", "image/lab7-step3.png", tiles([
                     ("N = %s" % E.plain(r[0]), r[1].split("/")[1].strip() + " วินาที",
                      "TTFT p95 รอคิว %s %s" % (r[4], "ผ่าน" if "✅" in r[5] else "เกิน 2 วินาที"),
                      "ok" if "✅" in r[5] else "bad") for r in t3["rows"]]),
                     cap="ส่วนหนึ่งของคำตอบจริง ตัวยิงหยุดเองหลังไม่ผ่าน 2 ระดับติดกัน จึงไม่ได้วัด N=6 และ 8"),
                 pic("อ่านผล: สิ่งเดียวที่เพิ่มตาม N คือเวลารอคิว", "image/cb-problem.png", [
                     "ความเร็วต่อผู้ใช้คงที่ราว 84 และ token/วินาทีรวมคงที่ราว 82 ทุกระดับ จำนวนที่รอคิวเท่ากับ N − 1 พอดี",
                     "เกณฑ์ที่ไม่ผ่านคือ TTFT อย่างเดียว ที่ N=2 ได้ 1.60 วินาที ห่างเส้น 2 วินาทีอยู่ 20% จึงไม่ต้องวัดซ้ำ",
                     "GPU utilization 97–100% ทั้งที่รับได้ 2 คน และตัวยิงใช้ CPU รวมราว 1.4% จึงไม่ใช่คอขวด"], tag=RD)])

    # ----- ขั้นที่ 4
    p = "ขั้นที่ 4 ·"
    cmp4 = next(b for b in walk(sec(p)) if b["t"] == "table" and len(b["head"]) > 1 and E.plain(b["head"][1]).startswith("ทีละคำถาม"))
    lab_step(4, "AI เปิดแชทบอทใหม่ในโหมด Continuous Batching เขียน `precheck.py` แล้วยิงโหลดด้วยตัวยิงเดิม",
             "รองรับผู้ใช้พร้อมกันได้ **192 คน** (96 เท่า)",
             pic("GPU ใบเดิม เปลี่ยนเพียงวิธีเสิร์ฟเป็น Continuous Batching แล้ววัดด้วยเกณฑ์เดิม", "image/cb-how.png", [
                 "**เปิดแชทบอท 1 GPU แบบ Continuous Batching** ด้วย `cluster.sh` ที่เขียนไว้ในขั้นก่อน",
                 "**ตรวจก่อนวัด** อุณหภูมิและ clock ของ GPU และความเร็วตอบผู้ใช้ 1 คน",
                 "**ยิงโหลดด้วยตัวยิงเดิม** N = 1 ถึง 256 ละเอียดทีละ 32 คน",
                 "**ใช้เกณฑ์ SLO เดิม** ระดับที่ก้ำกึ่งวัดซ้ำ 2 ครั้งแล้วใช้ค่ากลาง"]), [
                 shot("ผลจริง: GPU 1 ใบ ด้วย Continuous Batching รองรับผู้ใช้พร้อมกันได้ 192 คน", "img/c04-step4-compare.jpg", "image/lab7-step4.png", tiles([
                     ("รองรับผู้ใช้", "%s → %s" % (E.plain(cmp4["rows"][0][1]).split()[0], E.plain(cmp4["rows"][0][2]).split()[0]),
                      "คน (**%s**)" % E.plain(cmp4["rows"][0][3]), "ok"),
                     ("token/วินาทีรวมสูงสุด", "%s → %s" % (cmp4["rows"][1][1], cmp4["rows"][1][2]), "**%s**" % E.plain(cmp4["rows"][1][3]), "ok"),
                     ("ความเร็ว p5 ที่ N=192", "16.3", "token/วินาที ส่วน N=224 ได้ 13.3 จึงไม่ผ่าน", "warn")])),
                 tbl("ทุกระดับ N: ไม่มีคิวเลยจนถึง N=256 แต่ความเร็วต่อผู้ใช้ตกเกณฑ์หลัง N=192", table(p, "N"),
                     post=note("N=192 สูงกว่าเส้น 8.7% และ N=224 ต่ำกว่าเส้น 11% ทั้งคู่ห่างเกิน 5% จึงไม่มีระดับไหนต้องวัดซ้ำ")),
                 pic("อ่านผล: สองโหมดตกเกณฑ์คนละข้อ", "results/speed_p5_vs_n.png", [
                     "ทีละคำถามตกเพราะ TTFT (รอคิว) ส่วน Continuous Batching ไม่มีคิวแม้ที่ N=256 แต่ตกเพราะความเร็วต่อผู้ใช้",
                     "Throughput อิ่มตัวที่ราว 3,000 token/วินาทีตั้งแต่ N=96 เกินจุดนี้การเพิ่มผู้ใช้ทำให้ทุกคนช้าลงเท่านั้น",
                     "บันไดทีละ 32 คนบอกว่าความจุอยู่ระหว่าง 192–223 คน",
                     "GPU ร้อนสูงสุด 68°C และ clock อยู่ที่ราว 1,790–1,890 MHz ตลอดการวัด จึงไม่ลดความเร็วตัวเอง"], tag=RD)])

    # ----- ขั้นที่ 5
    p = "ขั้นที่ 5 ·"
    pre5 = table(p, "vLLM")
    lab_step(5, "AI เปิด vLLM 2 ตัวหลัง NGINX แบบ least_conn เขียน `precheck2.py` ยิงโหลด แล้วเขียน `report.py`",
             "1 ใบ 192 คน → 2 ใบ **384 คน** (2.00 เท่า)",
             pic("เปิด vLLM 2 ตัว ตัวละ 1 GPU หลัง NGINX แบบ least_conn แล้ววัดด้วยเกณฑ์เดิม", "image/lab7-system.png", [
                 "**เปิด vLLM 2 ตัว** แล้วตรวจ GPU ทั้ง 2 ใบก่อนวัด: อุณหภูมิ clock และความเร็วผู้ใช้ 1 คน",
                 "**ยิงโหลด** N = 128 ถึง 512 ละเอียดทีละ 64 คน ด้วยเกณฑ์ SLO เดิม",
                 "**เขียน `report.py`** สร้าง `metrics.json` และกราฟบนเครื่องเรานอก container",
                 "**สรุป** 1 ใบ → 2 ใบ กี่เท่า Efficiency เท่าไร และค่าประมาณ 3 ใบ (เป็นการคำนวณ)"]), [
                 shot("ผลจริง: 2 GPU ผ่านถึง N=384 และ Throughput ที่ความจุคือ 6,157 token/วินาที", "img/c05-step5-levels.jpg", "image/lab7-step5.png", tiles([
                     ("ตรวจก่อนวัด", "%s / %s" % (pre5["rows"][0][4].split()[0], pre5["rows"][1][4].split()[0]),
                      "token/วินาที ของ vllm-1 / vllm-2 ต่างกัน 0.5%", ""),
                     ("N = 384", "16.0", "ความเร็ว p5 ผ่าน", "ok"),
                     ("N = 448", "13.4", "ความเร็ว p5 ไม่ผ่าน", "bad"),
                     ("เท่าของ 1 ใบ", "2.00×", "192 → 384 คน", "ok"),
                     ("Efficiency", "100%", "Throughput 1.99 เท่า", "ok")])),
                 pic("อ่านผล: GPU 2 ใบได้งานเกือบเท่ากัน จึงได้ 2.00 เท่า", "results/capacity_vs_gpus.png", [
                     "**1 ใบ 192 คน → 2 ใบ 384 คน (2.00 เท่า, Efficiency 100%)** และ Throughput ที่ความจุเพิ่ม 1.99 เท่า (3,097 → 6,157)",
                     "least_conn แบ่งคำถามให้ 2 ใบต่างกันไม่เกิน 3% GPU 1 ร้อนกว่าราว 13°C แต่ช้ากว่าเพียงราว 2%",
                     "ความละเอียดของผล: ความจุจริงของ 1 ใบอยู่ระหว่าง 192–223 คน และของ 2 ใบอยู่ระหว่าง 384–447 คน",
                     "ถ้าเพิ่มเป็น 3 ใบ: 192 × 3 × 100% ≈ 576 คน **เป็นการคำนวณ ไม่ใช่ผลวัด**"],
                     post='<p class="cap">AI เพิ่มกราฟ <code>speed_p5_vs_n.png</code> ให้เอง เพราะเกณฑ์ที่ทำให้ไม่ผ่านคือความเร็ว</p>', tag=RD)])

    # ----- ขั้นที่ 6
    p = "ขั้นที่ 6 ·"
    t6 = table(p, "วิธีแจกงาน")
    rr, lc = t6["rows"]
    lab_step(6, "AI เพิ่มตัวเลือก \"คำตอบยาว\" ใน `loadtest.py` ยิง 2 รอบโดยสลับวิธีแจกงานของ NGINX แล้วเพิ่มตารางและกราฟใน `report.py`",
             "least_conn TTFT p95 **0.36 วินาที** เทียบกับ Round Robin **1.55 วินาที**",
             pic("ผู้ใช้ 448 คน โดย 20% ขอคำตอบยาว ยิง 2 รอบโดยสลับวิธีแจกงานของ NGINX", "image/lb-rr-vs-lc.png", [
                 "**เพิ่มตัวเลือกคำตอบยาว**: 20% ของคำถามขอคำตอบได้ถึง 600 token",
                 "**ผู้ใช้ระดับเดียว 448 คน** วัด 90 วินาที ไม่นับ 30 วินาทีแรก",
                 "**ยิง 2 รอบ**: NGINX แบบ round robin แล้วแบบ least_conn",
                 "**เพิ่มใน `report.py`**: ตารางและกราฟ TTFT p95 และจำนวนคำถามที่ GPU แต่ละใบกำลังทำ"]), [
                 shot("ผลจริง: least_conn ได้ TTFT p95 ดีกว่าราว 4 เท่า", "img/c06-step6-table.jpg", "image/lab7-step6.png", versus("",
                     ("Round Robin", "GPU 0 / GPU 1 กำลังทำเฉลี่ย 197 / 243 (สูงสุด 256 เต็ม)", E.plain(rr[1]),
                      "ความเร็ว p5 %s และรวม %s token/วินาที" % (rr[2], rr[3])),
                     ("least_conn", "GPU 0 / GPU 1 กำลังทำเฉลี่ย 220 / 222", E.plain(lc[1]),
                      "ความเร็ว p5 %s และรวม %s token/วินาที" % (lc[2], lc[3])))),
                 pic("Round Robin: GPU 1 สะสมงานจนชนเพดาน 256 ส่วน least_conn สองเส้นทับกันที่ราว 220", "results/lb_running_per_gpu.png", [
                     "Round Robin แจกจำนวนคำขอเท่ากันพอดี (1,201 / 1,201 ข้อ) แต่ไม่ดูว่าแต่ละใบยังค้างอยู่กี่ข้อ",
                     "ใบที่บังเอิญได้งานค้างมากกว่าจะตอบแต่ละข้อช้าลง งานจึงสะสมจนชน 256 ช่อง ขณะที่อีกใบยังมีที่ว่าง",
                     "least_conn แจกตามงานค้าง ทั้ง 2 ใบจึงอยู่ที่ราว 220 ข้อตลอด 90 วินาที"], tag=RD),
                 pic("TTFT p95 ต่ำกว่าเส้น SLO 2 วินาทีทั้งสองวิธี แต่ทั้งสองวิธีไม่ผ่าน SLO ข้อความเร็ว", "results/lb_ttft_p95.png", [
                     "least_conn ได้ TTFT p95 ดีกว่าราว 4 เท่า และ token/วินาทีรวมสูงกว่า 5%",
                     "ทั้งสองวิธี **ไม่ผ่าน SLO** ข้อความเร็ว (9.3 และ 11.2) เพราะคำตอบยาวใช้ GPU นานกว่าคำตอบสั้นราว 7 เท่า 448 คนจึงเกินความจุ",
                     "ขั้นนี้ตั้งใจดูพฤติกรรมตอนโหลดหนัก ไม่ได้หาความจุ และแต่ละวิธีวัดรอบเดียว (มีคิวพุ่งสั้น ๆ ช่วงวินาทีที่ 12–17 ทั้ง 2 รอบ)"], tag=RD)])

    # ----- ขั้นที่ 7
    p = "ขั้นที่ 7 ·"
    bill = table(p, "รายการ")

    def bt(r):
        lab = E.plain(r[0])
        return (lab.split("(")[0].strip(), E.plain(r[1]), lab.split("(")[1].rstrip(")") if "(" in lab else "",
                "warn" if lab.startswith("ดาวน์โหลด") else "")
    lab_step(7, "AI ตรวจว่าโค้ดและผลกลับมาครบ ลบเครื่อง แล้วอ่านยอดจากใบแจ้งหนี้", "ค่าเช่าทั้งเครื่อง **$0.597**",
             nfig("n04-step7-destroy", "ตรวจว่าโค้ดและผลกลับมาครบ ลบเครื่อง แล้วอ่านยอดจากใบแจ้งหนี้"), [
                 shot("ผลจริง: ค่าเช่าทั้งเครื่อง $0.597 และค่าดาวน์โหลดสูงกว่าค่า GPU", "img/c07-step7-bill.jpg", "image/lab7-step7.png",
                      tiles([bt(r) for r in bill["rows"][:4]] +
                            [("รวม", E.plain(bill["rows"][4][1]), "อายุเครื่อง 0.80 ชั่วโมง ที่ $0.369 ต่อชั่วโมง", "ok")])),
                 chartside("อ่านผล: ค่ารับส่งข้อมูลต้องดูด้วย ไม่ใช่ดูเพียงราคาต่อชั่วโมง", bars([
                     ("รับส่งข้อมูล", "ดาวน์โหลด $0.299 + อัปโหลด $0.003", 0.302, 0.302, "$0.302"),
                     ("GPU", "0.799 ชั่วโมง × $0.347", 0.277, 0.302, "$0.277"),
                     ("Disk", "0.799 ชั่วโมง × $0.022", 0.018, 0.302, "$0.018")]), [
                     "**ค่ารับส่งข้อมูล ($0.302) สูงกว่าค่า GPU ($0.277)** เพราะต้องดาวน์โหลด vLLM และโมเดลราว 11.5 GB",
                     "ตอนเลือกเครื่องควรดูราคาต่อ GB ของ host ด้วย",
                     "ข้อ 1 ของพรอมต์กันไฟล์หาย ในรอบจริง AI ต้องคัดลอกโค้ดบางไฟล์กลับมาที่ `lab7_llm_chat/code` ก่อนลบเครื่อง",
                     "ทั้ง LAB ตอบคำถามเรื่องความจุได้ด้วยเงินราว $0.60"], tag=RD)])

    # ----- ขั้นที่ 8
    lab_step(8, "AI อ่านพรอมต์ โค้ด และผลของ LAB แล้วเขียนเป็นสกิล `llm-chat-capacity` พร้อมคัดลอกโค้ด 8 ไฟล์เข้า `scripts/`",
             "สกิล `llm-chat-capacity` ไม่ต้องเช่าเครื่อง",
             fig("สกิลคือโฟลเดอร์ที่เก็บวิธีทำงานที่สำเร็จแล้ว พร้อมโค้ดที่ใช้ได้แล้ว", "image/skill-v0.png",
                 "`SKILL.md` บอกว่าใช้เมื่อไร ค่าที่ปรับได้ ขั้นตอน และกติกาเรื่องเงิน ส่วน `scripts/` เก็บโค้ดที่ใช้ได้แล้ว AI จึงทำซ้ำได้ในคำสั่งเดียว"), [
                 shot("ผลจริง: ได้สกิล llm-chat-capacity พร้อมสคริปต์ 8 ไฟล์ ใช้เวลา 3 นาที", "img/c08-step8-files.jpg", "image/lab7-step8.png",
                      tiles([("เวลา", "3 นาที", "ไม่ต้องเช่าเครื่อง", ""),
                             ("scripts/", "8 ไฟล์", "โค้ดที่ใช้ได้แล้วจาก `code/`", "ok")]) +
                      note("สกิลที่ได้: [skill_v0/SKILL.md](skill_v0/SKILL.md) " + quote("ขั้นที่ 8").replace("⚠️", "").strip(), "warn"))])

    # ----- ขั้นที่ 9
    p = "ขั้นที่ 9 ·"
    t9 = table(p, "ระดับที่ก้ำกึ่ง")
    lab_step(9, "AI ตัวใหม่ทำตามสกิล: เช่าเครื่อง ติดตั้ง เปิดแชทบอท ตรวจ GPU ยิงโหลด 2 แบบ สรุปผล ลบเครื่อง และอ่านบิล",
             "ทีละคำถาม 2 คน Continuous Batching 160 คน ค่าใช้จ่าย $0.093",
             nfig("n05-step9-skill", "สกิล v0 ทำงานทั้ง LAB ในพรอมต์เดียว โดยใช้โค้ดใน scripts/"), [
                 shot("ผลจริง: สกิล v0 ผ่านในรอบแรก แต่ความจุต่ำกว่ารอบหลัก", "img/c09-step9-capacity.jpg", "image/lab7-step9.png", tiles([
                     ("ทีละคำถาม", "2 คน", "วัดซ้ำ 3 ครั้ง", "ok"),
                     ("Continuous Batching", "160 คน", "80 เท่า วัดซ้ำ 3 ครั้ง", "warn"),
                     ("ค่าใช้จ่ายจริง", "$0.093", "RTX 3090 1 ใบ $0.196 ต่อชั่วโมง ใช้เวลา 24 นาที", "")])),
                 S("กติกาวัดซ้ำได้ใช้จริง: 2 ระดับห่างเส้นเกณฑ์ไม่ถึง 5%", '<div class="ex"><div class="fig">%s</div><div class="side fitbox">%s</div></div>' % (
                     E.img_tag({"t": "img", "src": "img/c11-measure-repeat.jpg", "alt": "ค่าที่วัดซ้ำ 3 ครั้งและค่ากลาง"}),
                     cards([(E.plain(r[0]), "<p>3 ครั้ง: <code>%s</code></p><p>ค่ากลาง <b>%s</b> %s</p>" % (r[1], r[2], E.plain(r[3])), "ok")
                            for r in t9["rows"]], 1) + note("ตัวยิงวัดซ้ำเองอีก 2 ครั้ง แล้วตัดสินด้วยค่ากลางของ 3 ครั้ง ทั้งคู่ผ่าน")),
                   tag="results/skill_v0_run", maxfs=1.25),
                 tbl("สั่งทีละขั้น 5 พรอมต์ เทียบกับสกิล v0 พรอมต์เดียว",
                     next(b for b in walk(sec(p)) if b["t"] == "table" and len(b["head"]) > 1 and E.plain(b["head"][1]).startswith("สั่งทีละขั้น"))),
                 pic("อ่านผล: RTX 3090 รุ่นเดียวกัน แต่เครื่องที่ถูกจำกัดกำลังไฟรับได้ 160 แทน 192 คน", "img/n31-step9-read.jpg", [
                     "สกิล v0 **ผ่านในรอบแรก**: AI ตัวใหม่ได้คำสั่ง 5 บรรทัด แล้วเช่า ติดตั้ง วัด 2 แบบ ลบเครื่อง และสรุปบิลเองทั้งหมด",
                     "เครื่องนี้ถูกจำกัดกำลังไฟ GPU ไว้ที่ 213 W (ปกติ 350 W) clock จึงอยู่ที่ราว 1,300–1,450 MHz และผู้ใช้ 1 คนได้ 71 แทน 84 token/วินาที",
                     "GPU ไม่ร้อน (ว่าง 29°C สูงสุด 62°C) จึงผ่านการตรวจก่อนวัด อุณหภูมิอย่างเดียวจึงยังไม่พอ ความจุต้องวัดบนเครื่องที่จะใช้จริง"], tag=RD)])

    # ===== 5 · สรุป
    CTX.update(kicker="", group="สรุป")
    add(E.divider("ส่วนที่ 4", "สรุปผลของทั้ง LAB", "<p>ผลรวม บทเรียน ข้อจำกัด และสิ่งที่ยังไม่ผ่าน</p>", small="ส่วนที่ 4 จาก 4"))
    CTX.update(kicker="สรุป")
    add(fig("ผลรวม: Throughput เพิ่มจากราว 82 เป็น 3,097 บน GPU ใบเดิม และ 2 ใบได้สูงสุด 6,261 token/วินาที", "results/throughput_vs_n.png",
            "เส้นสีน้ำเงินด้านล่างคือแบบทีละคำถาม เส้นสีส้มคือ Continuous Batching 1 ใบ และเส้นสีเขียวคือ 2 ใบหลัง NGINX"))
    add(tbl("ผลสรุปของทั้ง LAB: 2 → 192 → 384 คน", summary,
            post=note(para("การทดลอง", "**1 ใบ 192 คน")["lines"][0], "info")))
    add(band("GPU ใบเดิม ราคาเดิม รับผู้ใช้ได้มากขึ้น", "img/p21-result.jpg",
             "GPU ใบเดิมราคาเดิมรองรับผู้ใช้ได้จาก 2 เป็น 192 คนเมื่อเปลี่ยนวิธีเสิร์ฟ และเป็น 384 คนเมื่อเพิ่มเป็น 2 ใบหลัง Load Balancer"))
    add(pic("บทเรียนจากผลจริง (1): วิธีเสิร์ฟสำคัญกว่าตัวเลข GPU utilization", "img/n32-lessons-a.jpg", [
        "GPU ใบเดิม ราคาเดิม เปลี่ยนเป็น Continuous Batching รองรับผู้ใช้ 2 → 192 คน (96 เท่า)",
        "GPU utilization 97–100% ทั้งสองโหมด จึงต้องดู Throughput ประกอบ",
        "ทีละคำถามตกเพราะ TTFT (รอคิว) ส่วน Continuous Batching ตกเพราะความเร็วต่อผู้ใช้"]))
    add(pic("บทเรียนจากผลจริง (2): วิธีแจกงาน ค่ารับส่งข้อมูล และเครื่องที่ใช้จริงมีผลกับคำตอบ", "img/n33-lessons-b.jpg", [
        "least_conn แจกงานค้างเท่ากัน TTFT p95 ดีกว่า Round Robin ราว 4 เท่า",
        "ค่ารับส่งข้อมูล $0.302 สูงกว่าค่า GPU $0.277 จึงต้องดูราคาต่อ GB ของ host ด้วย",
        "RTX 3090 รุ่นเดียวกัน แต่เครื่องที่จำกัดกำลังไฟได้ 160 แทน 192 คน"]))
    v0 = table("ขั้นที่ 9 ·", "จุดที่ v0")
    add(pic("ข้อจำกัด และสิ่งที่ยังไม่ผ่าน", "img/n34-limits.jpg", [
        "ขั้นที่ 6 **ไม่ผ่าน SLO** ข้อความเร็วทั้ง Round Robin และ least_conn (9.3 และ 11.2)",
        "3 ใบ ≈ 576 คนเป็นการคำนวณ ไม่ใช่ผลวัด และความจุจริงอยู่ระหว่าง 192–223 คน (1 ใบ) และ 384–447 คน (2 ใบ)",
        "ทุกส่วนอยู่บนเครื่องเดียว คำถามเป็นข้อความสั้น และสกิล v0 ยังพลาด %d จุด (สไลด์ถัดไป)" % len(v0["rows"])]))
    add(tbl("สกิล v0 ยังพลาด %d จุด และควรแก้ใน v1" % len(v0["rows"]), v0,
            post=note("วิธีปรับคือสั่ง AI ด้วยพรอมต์อีก 1 อันให้แก้สกิลตามตารางนี้ แล้วลองใช้ซ้ำ", "info"), tag="README"))
    CTX.update(kicker="", group="จบบท")
    add(E.divider("จบ", "LAB 7 · แชทบอท LLM",
                  '<p>รายละเอียดเต็มของ LAB นี้: <a href="README.md" target="_blank">README.md</a> · พรอมต์ทั้ง 9 ขั้น: '
                  '<a href="PROMPTS.md" target="_blank">PROMPTS.md</a> · หน้ารวมของบท: <a href="../README.md" target="_blank">../README.md</a></p>'))
    return E.SL


E.CSS += """
.inner .small{margin-bottom:26px}
.cover.cx .inner{max-width:830px}
.cover.cx .inner h1{margin-top:150px}
.covimg{position:absolute;right:56px;top:50%;transform:translateY(-50%);width:640px;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,.35)}
.ex.pic .fig{flex:2.1 1 0}
.sr{flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:12px}
.sr .fig{flex:1 1 0;min-height:0}
.sr .cap{margin:0}
.sr .srb{flex:none;font-size:.8em}
.sr .srb .vs .bigv{font-size:2.1em}
.sr .srb .vs .sidebox{padding:.5em .9em}
.sr .srb .tiles,.sr .srb .vs{margin:0}
.chartbox{flex:1.3 1 0;min-width:0;display:flex;flex-direction:column;justify-content:center}
.bandsl{background-size:cover;background-position:center;padding:0!important}
.bandsl .bd{position:absolute;left:0;right:0;bottom:90px;background:rgba(14,32,62,.82);color:#fff;padding:30px 72px}
.bandsl .bk{font-size:15px;letter-spacing:.04em;color:#9fd6e8;margin-bottom:8px}
.bandsl .bs{font-size:40px;font-weight:700;line-height:1.45}
.bandsl .imgnote{position:absolute;right:26px;top:18px;font-size:13px;color:rgba(255,255,255,.75)}
"""

if __name__ == "__main__":
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
