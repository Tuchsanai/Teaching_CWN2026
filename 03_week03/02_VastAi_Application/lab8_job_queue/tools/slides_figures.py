#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ LAB 8 (ระบบคิวอ่านใบเสร็จด้วย VLM)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล)
  title  หัวข้อของสไลด์ และข้อความบนป้ายชื่อของภาพ
  labels ข้อความสั้นบนภาพ (ป้ายที่เป็นขั้นตอนขึ้นต้นด้วยเลข)
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ
  steps  ขั้นตอนข้างภาพ 3-5 ขั้น · เรียบเรียงจาก README.md ของบท
PHOTOS = ภาพถ่ายสมจริงของหน้าปกและหน้าคั่น (ไม่มีตัวอักษรในภาพ)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
"""
import os, sys

SETTING = ('a small receipt-reading service team: a few developers at laptops, a rented GPU server with two RTX 3090 cards, '
           'a message queue drawn as a conveyor of envelopes, and customers holding paper receipts')

PHOTO_SETTING = 'a modern small tech office and server room of a receipt-reading service that runs AI models on rented GPU servers'

FIGS = [
    {"img": "n01-experiment", "title": "การทดลอง: วัด 3 แบบด้วยโหลดและเกณฑ์เดียวกัน",
     "labels": ["1 A: API Synchronous · 1 GPU", "2 B1: คิว 1 Worker · 1 GPU", "3 B2: คิว 2 Worker · 2 GPU",
                "Closed loop: ส่ง → รอผล → คิด 10 วินาที", "N = 1, 2, 4, 6, 8", "งานถล่ม 60 งาน ใน 10 วินาที",
                "SLO: p95 ≤ 20 วินาที · ล้ม < 1%"],
     "scene": "Top half: three numbered boxes side by side, each showing one system under test: (1) one GPU card behind a single "
              "server box with users holding the line; (2) one GPU card with one robot-arm worker taking envelopes from a queue tube; "
              "(3) two GPU cards with two robot-arm workers sharing the same queue tube. Bottom left: a small circular arrow loop of a "
              "user icon (send, wait, think) with a row of user counters. Bottom middle: a burst of many envelopes arriving at once. "
              "Bottom right: a ribbon with the SLO label.",
     "steps": ["**A** = API Synchronous บน GPU 1 ใบ · **B1** = ระบบคิว 1 Worker (GPU 1 ใบ) · **B2** = ระบบคิว 2 Worker (GPU 2 ใบ)",
               "**Closed loop**: ผู้ใช้จำลอง N คน ส่งงาน (ใบเสร็จ 4 ใบ) → รอผล → คิด 10 วินาที → ส่งใหม่ · ระดับละ 75 วินาที",
               "ไล่ **N = 1, 2, 4, 6, 8 …** หยุดเมื่อไม่ผ่าน 2 ระดับติดกัน",
               "**งานถล่ม** (Open loop): 60 งานภายใน 10 วินาที · บันทึกความยาวคิวทุก 1 วินาที",
               "**SLO** = p95 ≤ 20 วินาที และงานล้ม < 1% · แบบ Synchronous ผู้ใช้รอได้ไม่เกิน 30 วินาที"]},
    {"img": "n02-step1-rent", "title": "ขั้นที่ 1: เช่าเครื่อง 2 GPU แล้วดูใบเสร็จตัวอย่าง",
     "labels": ["1 เช่า 2× RTX 3090", "≤ $0.60/ชม.", "vapp-lab8", "2 เห็น GPU ครบ 2 ใบ",
                "3 โหลดโมเดล + Test Set", "4 ภาพตัวอย่าง 6 ใบ + JSON เฉลย"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a developer at a laptop picking one server card from a "
              "marketplace shelf of GPU servers, with a price tag and a name tag on the chosen server; (2) the rented server opened, "
              "showing two GPU cards with green check marks; (3) a download arrow bringing a model box and a stack of receipt "
              "photos onto the server; (4) a grid of six receipt photos, each paired with a small JSON card.",
     "steps": ["**เช่าเครื่องเดียว** ที่มี RTX 3090 2 ใบ ราคารวมไม่เกิน $0.60/ชม. ป้ายเครื่อง `vapp-lab8`",
               "**รอจนเห็น GPU ครบ 2 ใบ** · เกิน 10 นาทียังไม่พร้อม ให้ลบแล้วเช่าเครื่องอื่น",
               "**ดาวน์โหลด** โมเดล `Qwen/Qwen3-VL-2B-Instruct` และ Test Set ของ CORD-v2 ไว้บนเครื่องที่เช่า",
               "**ทำภาพตัวอย่าง** ใบเสร็จ 6 ใบคู่กับ JSON เฉลย เก็บที่ `results/dataset_samples.jpg`"]},
    {"img": "n03-step2-baseline", "title": "ขั้นที่ 2: Baseline คือ API Synchronous บน GPU 1 ใบ",
     "labels": ["1 sync_api.py", "2 loadtest.py", "ผู้ใช้ถือสายรอ", "GPU อ่านทีละงาน", "รอเกิน 30 วินาที = ล้ม",
                "3 ไล่ N + งานถล่ม"],
     "scene": "Left: a row of users each holding a long telephone-like cable connected to one server box (numbered 1) in front of one "
              "GPU card; the server reads one receipt bundle at a time while others wait in a line inside the server. Middle: a "
              "small load generator machine (numbered 2) spawning user icons. A stopwatch near the line shows a time limit, with a "
              "red cross on a user who gave up. Right: a staircase chart of user levels with a burst of envelopes (numbered 3).",
     "steps": ["**sync_api.py**: รับงาน 1 งาน (ใบเสร็จหลายใบ) แล้วตอบผลในการเชื่อมต่อเดิม · GPU อ่านได้ทีละงาน",
               "**loadtest.py**: ผู้ใช้จำลอง N คน ส่งงาน → รอผล → คิด 10 วินาที → ส่งใหม่ · วัดงาน/นาที p50/p95/p99 % ล้ม",
               "ผู้ใช้รอได้ไม่เกิน **30 วินาที** เกินนับเป็นล้ม",
               "ไล่ **N = 1, 2, 4, 6, …** หยุดเมื่อไม่ผ่าน SLO 2 ระดับติดกัน แล้วตามด้วย **งานถล่ม 60 งาน**"]},
    {"img": "n04-step6-web", "title": "ขั้นที่ 6: เว็บดูคิวแบบสดบนเครื่องเรา ต่อกับ gateway บนเครื่องเช่า",
     "labels": ["1 เลือกใบเสร็จ แล้วส่งเป็นชุด", "localhost:3407", "2 Next.js server + API key", "3 gateway พอร์ต 8000",
                "4 Worker GPU0 · GPU1", "อัปเดตทุก 1 วินาที"],
     "scene": "Left: a laptop browser window showing a queue length number, two worker cards and a table of jobs, labelled with the "
              "local address. Middle: a small Next.js server box holding a key icon (the key stays inside this box, a crossed-out "
              "key near the browser). Right: across a cloud arrow, the rented server with the API gateway box and a queue tube "
              "feeding two robot-arm workers, one per GPU card.",
     "steps": ["**เว็บ Next.js ภาษาไทย** เปิดด้วย docker compose ที่ `http://localhost:3407` · เลือกใบเสร็จตัวอย่างหรืออัปโหลด แล้วส่งเป็นชุด",
               "**เว็บเรียก gateway จากฝั่ง server ของ Next.js** อ่านที่อยู่และ API key จาก `.env` · key ไม่ไปถึงเบราว์เซอร์",
               "เห็น **ความยาวคิว · การ์ด Worker แต่ละตัว · ตารางงานล่าสุด** อัปเดตทุก 1 วินาที",
               "**ทดสอบ**: ส่งใบเสร็จตัวอย่างทั้ง 6 ใบเป็น 6 งาน แล้วรอจนเสร็จทุกงาน"]},
    {"img": "n05-step7-cleanup", "title": "ขั้นที่ 7: ตรวจผลครบ ลบเครื่อง ปิดเว็บ แล้วสรุปค่าใช้จ่าย",
     "labels": ["1 ตรวจ results ครบ", "2 ลบเครื่อง vapp-lab8", "ไม่มีเครื่องค้าง", "3 ปิดเว็บ", "4 ค่าใช้จ่ายจริง"],
     "scene": "Four numbered panels left to right: (1) a folder with result files, charts and a check mark; (2) a GPU server being "
              "dropped into a recycle bin, with an empty server rack and a check mark next to it; (3) a browser window being "
              "closed; (4) a bill receipt with three cost rows and a total line, held by a developer.",
     "steps": ["**ตรวจ** ว่า `results/` มีผลครบ (JSON ของทุกการทดลอง · metrics.json · กราฟ) ถ้าขาดให้เก็บจากเครื่องก่อนลบ",
               "**ลบเครื่องป้าย** `vapp-lab8` แล้วตรวจว่าไม่มีเครื่องป้ายนี้ค้างในบัญชี (ห้ามแตะเครื่องป้ายอื่น)",
               "**ปิดเว็บ** ใน `code/web`",
               "**สรุปค่าใช้จ่ายจริง**: อายุเครื่อง · ราคาต่อชั่วโมง · GPU · disk · รับส่งข้อมูล · รวม"]},
]

PHOTOS = [
    {"img": "s01-cover", "scene": "A small office of a receipt-reading service at dusk. On the right, a developer sits at a desk with "
                                  "two monitors showing abstract blurred dashboards; beside the desk lies a neat pile of paper "
                                  "shop receipts and a phone. Mood: a service that must handle many requests at once."},
    {"img": "s02-lab", "scene": "Close-up of a server room aisle: on the right, an open GPU server with two large graphics cards and "
                                "blinking status lights, a technician's hand plugging a network cable. Mood: hands-on measurement work."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, light background, rounded title banner at the top, thick outlines, rounded pastel cards,
numbered circle badges, bold rounded Thai lettering):
{refs}

Canvas: landscape 4:3 (about 1448 x 1086). Setting: {setting}.

Title banner text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above.
- When a label starts with a number (for example "3 gate"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, addresses) use a monospace font.
- Characters: a friendly team of fictional cartoon people. No emoji.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

PHOTO = """Generate ONE photorealistic image with your image generation tool and save it as a JPG file at exactly this path:
{out}/{img}.jpg

Scene: {scene}

Requirements:
- Photorealistic, natural warm light, shallow depth of field, landscape 16:9 (about 1920x1080).
- Setting: {setting}.
- People are fictional adults of Thai appearance; no real person's likeness.
- NO readable text anywhere: no letters, no numbers, no logos, no signs, no watermarks. Screens and papers must be blurred or abstract.
- Keep the left 45% of the frame calm and darker (out-of-focus background), main subject on the right side, because a title will be placed over the left side later.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

# ------------------------------------------------------------------ รอบที่ 2: ภาพอธิบายแบบตำราเรียน (n2x) และภาพถ่าย (p2x)
# ภาพที่มีตัวเลข: ตัวเลขทุกตัวคัดจาก README.md ตรงตัวอักษร และมีบัญชีตรวจย้อนกลับใน <WORK>/numbers.md
FIGS2 = [
    {"img": "n21-roadmap", "ratio": "16:9", "title": "บทนี้มี 4 ส่วน",
     "labels": ["1 พื้นฐาน: ข้อมูล โมเดล ผู้ใช้และ SLO", "2 ทฤษฎี: Latency · Little's Law · Job Queue · RabbitMQ",
                "3 LAB ขั้นที่ 1–7: เช่าเครื่อง วัด ลบเครื่อง", "4 สกิลเวอร์ชัน 0 และสรุป"],
     "scene": "A horizontal road of four numbered stations from left to right, connected by a path with arrows. Station 1: a receipt "
              "photo next to a small model box and a user icon. Station 2: a simple line chart with a bend and a queue tube of "
              "envelopes. Station 3: a rented GPU server with two cards, a stopwatch and a recycle bin at the end. Station 4: a "
              "document card with a gear and a repeat arrow. Each station has its label on a card under it."},
    {"img": "n22-capacity", "ratio": "16:9", "title": "GPU 1 ใบ รับผู้ใช้ได้กี่คน",
     "labels": ["ผู้ใช้ 1 คน ≈ 2.9 งาน/นาที", "GPU 1 ใบ สูงสุด 5.44 งาน/นาที", "5.44 ÷ 2.9 ≈ 1.9 คน", "วัดจริง: 2 คน"],
     "scene": "Left: one user icon with a circular arrow (send, wait, think) and a small flow of job envelopes coming out, with its "
              "label. Middle: one GPU card with a gauge at its maximum, with its label. Right: a clean division card showing the "
              "formula label, and below it a green result badge with the measured label. Arrows connect left and middle into the "
              "formula card."},
    {"img": "n23-percentile", "ratio": "16:9", "title": "p50 และ p95 ของเวลารอผล",
     "labels": ["เวลารอผลของแต่ละงาน เรียงจากเร็วไปช้า", "p50: ครึ่งหนึ่งได้ผลเร็วกว่านี้", "p95: 95% ได้ผลเร็วกว่านี้",
                "ค่าเฉลี่ยซ่อนคนที่รอนาน", "SLO: p95 ≤ 20 วินาที"],
     "scene": "A clean bar figure: about twenty thin vertical bars sorted from short (left) to tall (right), like a sorted histogram "
              "of waiting times, no axis numbers. A vertical marker line at the middle bar with the p50 label, and a vertical marker "
              "line near the right end with the p95 label. A horizontal dashed red line across the chart with the SLO label. A small "
              "callout pointing at the few tallest bars on the right with the label about the average hiding long waits."},
    {"img": "n24-little", "ratio": "16:9", "title": "Little's Law สำหรับ Closed loop",
     "labels": ["N = X × (R + Z)", "N: ผู้ใช้พร้อมกัน", "X: Throughput", "R: เวลารอผล", "Z: Think time"],
     "scene": "A circular loop diagram: user icons travelling around a ring. The top half of the ring passes through a GPU server box "
              "(the waiting part R), the bottom half passes through a thinking zone with a thought bubble (Z). An arrow at the "
              "exit of the server shows the completed jobs rate (X). The ring of users is labelled N. The formula sits large in "
              "the centre of the ring on a white card. Each symbol label sits next to its part of the diagram."},
    {"img": "n25-sync-problems", "ratio": "16:9", "title": "API แบบ Synchronous เมื่อโหลดเกิน",
     "labels": ["1 ผู้ใช้รอจน timeout แล้วเลิก", "2 server ยังอ่านงานที่ไม่มีใครรอ", "3 server ดับ งานที่รอหายหมด",
                "Job Queue: ได้ job_id ทันที งานรอในคิว"],
     "scene": "Top row: three numbered panels of a synchronous server in trouble. Panel 1: a user holding a long cable to the server, "
              "a stopwatch, the user walking away. Panel 2: the server still reading a receipt bundle with an empty chair in front "
              "of it while new users queue behind. Panel 3: the server with a power-off symbol and the waiting bundles fading away. "
              "Bottom band in green: a user receiving a small ticket and walking off, the job envelope resting in a queue tube in "
              "front of a robot-arm worker."},
    {"img": "n27-prereq", "ratio": "16:9", "title": "ก่อนเริ่ม LAB",
     "labels": ["1 LAB 0: key 3 ตัว", "2 Claude Code ที่โฟลเดอร์ 02_VastAi_Application", "3 container multi-account · สกิล vastai",
                "4 งบค่าเช่าเครื่อง 2 GPU"],
     "scene": "Four numbered cards in a row with a check box each: (1) three key icons on a key ring; (2) a laptop with a terminal "
              "window and a folder icon; (3) a container box with a small toolbox inside; (4) a wallet with coins next to a server "
              "with two GPU cards and a running meter."},
    {"img": "n28-step1-read", "ratio": "16:9", "title": "อ่านผลขั้นที่ 1",
     "labels": ["เครื่องถูกกว่า แต่ดาวน์โหลดจาก Hugging Face ไม่ได้", "เครื่องที่เลือก: ดาวน์โหลดได้",
                "ไม่พร้อมใน 10 นาที: ลบแล้วเช่าใหม่", "เครื่องเริ่มคิดเงินแล้ว"],
     "scene": "Left: two rental server cards on a shelf; the cheaper one shows a download arrow blocked by a red cross, the chosen one "
              "shows a green download arrow and a check mark. Middle: a small clock with a loop arrow back to the shelf. Right: a "
              "taxi-style running meter attached to the chosen server."},
    {"img": "n29-chain", "ratio": "16:9", "title": "ทำไม API Synchronous ล้มเป็นลูกโซ่",
     "labels": ["1 ผู้ใช้เลิกรอที่ 30 วินาที", "2 server ยังอ่านงานนั้นต่อ", "3 งานใหม่ต้องรอหลังงานที่ไม่มีใครต้องการ",
                "N = 4: ล้ม 100%"],
     "scene": "A horizontal timeline with one GPU server on the left reading jobs in order. Job blocks wait in a line inside the "
              "server. The first waiting job's user has left (empty outline, a stopwatch). The server still processes that job (badge "
              "2). Newer job blocks behind it turn red one after another like falling dominoes (badge 3). At the right end a red "
              "result card with the last label."},
    {"img": "n31-no-loss", "ratio": "16:9", "title": "3 กลไกที่ทำให้งานไม่หาย",
     "labels": ["1 Durable + Persistent: งานอยู่ใน RabbitMQ", "2 Prefetch = 1: Worker ถือทีละงาน", "3 ack หลังทำเสร็จเท่านั้น",
                "Worker ถูกฆ่า งานในมือกลับเข้าคิว"],
     "scene": "Centre: a queue tube of envelopes resting on a disk drive (mechanism 1). Two robot-arm workers each hold exactly one "
              "envelope (mechanism 2). One worker is unplugged with a red cross; its envelope flies back into the queue tube along a "
              "curved arrow (the last label). The other worker sends a green check-mark message back to the queue (mechanism 3)."},
    {"img": "n33-v0-fixes", "ratio": "16:9", "title": "จุดที่สกิล v0 ยังพลาด และวิธีแก้ใน v1",
     "labels": ["1 จดค่าตายตัวของเครื่องแรก → จดอาการ + วิธีตรวจ", "2 Worker ซ้ำบน GPU ใบเดียว → ตรวจจำนวน Consumer",
                "3 คำสั่งปิด API ฆ่า shell ตัวเอง → วิธีปิดที่ไม่โดน shell", "4 RabbitMQ เขียน log ไม่ได้ → กำหนดที่เก็บ log",
                "5 รายการ N ไม่ตรงตัวยิงโหลด → สคริปต์รับรายการ N"],
     "scene": "Left: a document card titled SKILL.md v0 with five small numbered warning markers. Right: five numbered rows, each "
              "row a small problem icon (wrench, two workers on one card, broken terminal, blocked log file, mismatched list) then an "
              "arrow then a green fix icon. At the far right, a document card for v1 with a check mark."},
    {"img": "n34-lessons", "ratio": "16:9", "title": "สิ่งที่ได้เรียนรู้จาก LAB นี้",
     "labels": ["1 คิวไม่ทำให้ GPU เร็วขึ้น", "2 งานไม่หายเมื่อ Worker ตาย", "3 เพิ่ม Worker = เพิ่มความจุ", "4 ออกแบบด้วย Little's Law"],
     "scene": "Four numbered panels in a 2 x 2 grid: (1) one GPU card with a speedometer that stays the same, a queue tube in front; "
              "(2) an unplugged worker with its envelope returning to the queue, a shield with a check; (3) one worker becoming two "
              "workers next to two GPU cards, an arrow upward; (4) a loop diagram of users with a ruler and pencil."},
    {"img": "n35-limits", "ratio": "16:9", "title": "สิ่งที่ LAB นี้ไม่ได้วัด",
     "labels": ["GPU 3 ใบ: ค่าคำนวณ ไม่ใช่ผลวัด", "ไม่ได้ทดลองรีสตาร์ต RabbitMQ", "ไม่ได้ทดสอบ DLQ ด้วยรูปเสีย",
                "ไม่ได้วัดความแม่นของโมเดล", "ทุกส่วนอยู่บนเครื่องเดียว", "ความจุหยาบ: ไล่ N ทีละ 2"],
     "scene": "Six cards in a 3 x 2 grid, each with a dashed outline (meaning: not measured) and one icon: three GPU cards with a "
              "calculator; a broker box with a restart arrow; a broken image file entering a side queue; a receipt with a "
              "magnifier; one server rack holding all parts; a staircase with big steps. Every card carries one label. No numbers "
              "other than those in the labels."},
]

PHOTOS2 = [
    {"img": "p21-heavy", "scene": "A cashier-like office worker at a desk holding a thick stack of paper shop receipts next to a single "
                                  "compact GPU workstation with its side panel open; a small queue of three colleagues stands "
                                  "waiting with receipts in hand, softly out of focus. Mood: one machine, heavy work."},
    {"img": "p22-receipt", "scene": "Close-up of hands holding a smartphone, photographing a crumpled restaurant receipt on a wooden "
                                    "table with a coffee cup. The receipt print is blurred and unreadable. Mood: the input data."},
    {"img": "p23-theory", "scene": "A lecturer stands beside a large whiteboard covered with abstract diagrams of arrows, boxes and a "
                                   "curved line chart (no letters or numbers), students' backs softly blurred in the foreground. "
                                   "Mood: understanding the ideas before the experiment."},
    {"img": "p24-skill", "scene": "A developer at a tidy desk reviews a printed checklist and a laptop with an abstract blurred "
                                  "document on screen; a sticky note pad and a pen beside. Mood: turning finished work into a "
                                  "reusable procedure."},
]

FIG2 = """Generate ONE explanatory figure with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

Look at these reference images first and keep the same family look (light background, rounded title banner, rounded pastel
cards, thick clean outlines, numbered circle badges, bold rounded Thai lettering):
{refs}

Style: a clean, modern, flat explanatory figure like one from a well-made university textbook. Calm pastel colours with one
accent colour, generous white space, few elements, big shapes. Not childish: no faces with exaggerated expressions, no
sparkles or decorative clutter. Simple human figures are fine (fictional adults, neutral).

Canvas: landscape {ratio} ({size}). Setting: {setting}.

Title banner text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers, decimal points,
  symbols (≈ ÷ × = ≤ → %) stay exactly as they are.
- Do NOT add any other words, numbers, axis values, captions, watermarks or logos beyond the title and the labels above.
- When a label starts with a number followed by a space (for example "3 gate"), draw that number ONLY inside the circle badge
  and write the rest of the label next to it. Never show the same badge number twice.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels use a monospace font.
- No emoji.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

SIZE = {"16:9": "about 1672 x 941", "4:3": "about 1448 x 1086"}


def write_pass2(out, refs):
    os.makedirs(out, exist_ok=True)
    for f in FIGS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(FIG2.format(
            out=out, img=f["img"], refs="\n".join(refs), ratio=f["ratio"], size=SIZE[f["ratio"]], setting=SETTING,
            title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
    for f in PHOTOS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=PHOTO_SETTING, scene=f["scene"]))
    print("%d พรอมต์ (รอบที่ 2) -> %s" % (len(FIGS2) + len(PHOTOS2), out))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--pass2":
    write_pass2(os.path.abspath(sys.argv[2]).replace("\\", "/"), [os.path.abspath(p).replace("\\", "/") for p in sys.argv[3:]])
    sys.exit(0)

if __name__ == "__main__":
    out = os.path.abspath(sys.argv[1]).replace("\\", "/")
    refs = [os.path.abspath(p).replace("\\", "/") for p in sys.argv[2:]]
    if not refs:
        assets = os.path.join(os.path.expanduser("~"), ".claude", "skills", "readme-slides", "assets")
        refs = [os.path.join(assets, n).replace("\\", "/") for n in ("style-cartoon-1.jpg", "style-cartoon-2.jpg")]
    os.makedirs(out, exist_ok=True)
    for f in FIGS:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(CARTOON.format(
            out=out, img=f["img"], refs="\n".join(refs), setting=SETTING, title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
    for f in PHOTOS:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=PHOTO_SETTING, scene=f["scene"]))
    print("%d พรอมต์ -> %s" % (len(FIGS) + len(PHOTOS), out))
