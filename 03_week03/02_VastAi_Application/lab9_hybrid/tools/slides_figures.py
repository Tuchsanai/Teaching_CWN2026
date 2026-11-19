#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ LAB 9 (ภาพที่ README ยังไม่มี · ภาพอื่นใช้ภาพเดิมของ README)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล)
  title  หัวข้อของสไลด์ และข้อความบนป้ายชื่อของภาพ
  labels ข้อความสั้นบนภาพ (ป้ายที่เป็นขั้นตอนขึ้นต้นด้วยเลข)
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ
  steps  ขั้นตอนข้างภาพ 3-5 ขั้น · เรียบเรียงจาก README.md ของบท
PHOTOS = ภาพถ่ายสมจริงของหน้าปกและหน้าคั่น (ไม่มีตัวอักษรในภาพ · ฝั่งซ้ายมืดไว้วางหัวข้อ)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
"""
import os, sys

SETTING = ('a small Thai startup that runs a text-to-image web service: an operations desk with monitors showing queue graphs, '
           'and a rented cloud GPU server with two RTX 3090 graphics cards')

FIGS = [
    {"img": "n01-experiment", "title": "การทดลอง: 3 แบบ ตัวยิงโหลดเดียวกัน เกณฑ์เดียวกัน",
     "labels": ["1 ผู้ใช้จำลอง N คน", "2 ดูภาพ เฉลี่ย 5 วินาที", "3 ไล่ระดับ N ระดับละ 30 วินาที",
                "4 SLO: p95 ≤ 10 วินาที · งานล้ม < 1%",
                "A: API Synchronous · GPU 1 ใบ", "B: ระบบผสม · Worker 1 ตัว", "C: ระบบผสม · Worker 2 ตัว"],
     "scene": "Left: a circular loop of small simulated users with phones (send text, wait for image, look at image, send again), "
              "badge 1 near the users and badge 2 near a person looking at a picture with a small clock. "
              "Middle: three stacked system cards marked A, B, C (A: one server with one GPU card, B: gateway + queue + one GPU worker, "
              "C: gateway + queue + two GPU workers). Under them a staircase of increasing user counts with badge 3. "
              "Right: a gate with a stopwatch and a checklist, badge 4. Arrows from the users loop into each system and to the gate.",
     "steps": ['ผู้ใช้จำลองแต่ละคนส่งข้อความ รอจนได้ภาพ ดูภาพ 2.5–7.5 วินาที (เฉลี่ย 5 วินาที) แล้วส่งใหม่ ถ้ารอเกิน 30 วินาทีนับเป็นงานล้ม',
               'ไล่ระดับ N = 1, 8, 16, 24, 32, 48, 64, 96, 128, … ระดับละ 30 วินาที (ไม่นับ 10 วินาทีแรก) หยุดที่ระดับแรกที่ไม่ผ่าน แล้วลองค่ากึ่งกลางอีก 2 ครั้ง',
               'เทียบ 3 แบบ: **A** API Synchronous บน GPU 1 ใบ (Baseline) **B** ระบบผสม Worker 1 ตัวบน GPU ใบเดิม และ **C** ระบบผสม Worker 2 ตัวบน GPU 2 ใบ',
               '**ความจุ** คือ N สูงสุดที่ผ่าน SLO คือ p95 ≤ 10 วินาที และงานล้ม < 1%']},
    {"img": "n02-lb-vs-queue", "title": "Load Balancer ส่งงานให้เครื่อง · Queue ให้ Worker ดึงงานเอง",
     "labels": ["Load Balancer (LAB 6–7)", "Queue (LAB 8–9)", "ส่งงานให้เครื่องปลายทาง", "Worker ดึงงานเอง",
                "คำขอที่ค้างอยู่ล้ม", "งานกลับเข้าคิว", "คิวเต็ม → 429"],
     "scene": "Two halves side by side separated by a vertical line. Left half 'Load Balancer': users holding open phone lines to a "
              "dispatcher box that pushes requests with arrows into two server boxes; one server box is broken with a small red cross and "
              "its pending requests fall down. Right half 'Queue': users drop tickets into a long queue box; two GPU worker robots pull "
              "tickets from the queue themselves; one worker is broken and its tickets go back into the queue with a curved arrow; "
              "at the queue entrance a small gate shows the label for a full queue.",
     "steps": ["**Load Balancer** เหมาะกับคำขอสั้นที่ผู้ใช้ถือสายรอได้ · **Queue** เหมาะกับงานยาว หรืองานที่มาเป็นก้อน",
               "ตอนรอ: งานอยู่ **ใน connection ของผู้ใช้** เทียบกับ **ในคิว** (เขียนลงดิสก์ได้)",
               "Load Balancer **ส่ง** งานให้เครื่องปลายทาง · Worker **ดึง** งานเองตามกำลังของตัวเอง",
               "ปลายทางเต็ม: รอใน connection หรือถูกปฏิเสธ · คิว: รอในคิว จนถึงเพดานแล้วตอบ 429",
               "เครื่องทำงานตาย: คำขอที่ค้างอยู่ล้ม · คิว: งานกลับเข้าคิว ตัวอื่นทำแทน"]},
    {"img": "n03-step1-prepare", "title": "ขั้นที่ 1: เช่าเครื่อง 2 GPU แล้วจับเวลาโมเดล",
     "labels": ["1 เช่า RTX 3090 2 ใบ · vapp-lab9", "2 ติดตั้ง sdxl-turbo + RabbitMQ", "3 จับเวลา ครั้งละ 1, 2, 4, 8 ภาพ",
                "4 prompts.txt 12 ข้อ", "dataset_samples.jpg"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a person picks a cloud GPU server with two graphics cards "
              "from a list on a laptop, a tag hangs on the server; (2) packages and a rabbit-shaped message broker icon being installed "
              "onto the server; (3) a stopwatch next to stacks of 1, 2, 4 and 8 small picture cards coming out of a GPU; "
              "(4) a text file with twelve short lines and a 3 x 2 grid of sample photos (lighthouse, red bicycle, ramen bowl, dog on beach, "
              "latte art, snowy mountain).",
     "steps": ['เช่าเครื่องเดียวที่มี **RTX 3090 2 ใบ** ติดป้าย `vapp-lab9` ราคารวมไม่เกิน $0.60 ต่อชั่วโมง',
               'ติดตั้งสิ่งที่ต้องใช้กับโมเดล `stabilityai/sdxl-turbo` และติดตั้ง RabbitMQ ไว้ล่วงหน้า เพราะเครื่องเช่าไม่มี Docker',
               'จับเวลาสร้างภาพ 512x512 แบบ 4 steps บน GPU ใบแรก เมื่อส่งครั้งละ 1, 2, 4 และ 8 ข้อความ',
               'เขียนคำบรรยายภาพ 12 ข้อลง `prompts.txt` แล้วสร้างภาพจาก 6 ข้อแรกเป็น `dataset_samples.jpg`']},
    {"img": "n04-step2-sync", "title": "ขั้นที่ 2: API แบบ Synchronous ผู้ใช้ถือสายรอจนได้ภาพ",
     "labels": ["1 POST /generate + API key", "2 คำขอยืนรอกันใน server", "3 GPU ใบแรก สร้างทีละ 1 ภาพ",
                "4 ตอบกลับเป็นภาพ JPEG", "ไม่มี key → 401"],
     "scene": "A single server box in the middle with one GPU card inside. On the left a line of users holding phones on an open call "
              "(waiting), badge 1 on the first request arrow, badge 2 on the line of waiting requests inside the server. "
              "Badge 3 on the GPU making one picture at a time. Badge 4 on an arrow returning a picture to the first user. "
              "At the bottom a small stranger without a key is stopped at a door with a red stop sign.",
     "steps": ['API รับข้อความที่ **`POST /generate`** แล้วตอบกลับเป็นภาพ JPEG โดยต้องแนบ **API key** ที่สุ่มและเก็บไว้บนเครื่องเช่า',
               'คำขอที่มาพร้อมกันต่อแถวรอกันเองใน server ซึ่งต้องรับคำขอค้างได้อย่างน้อย 500 คำขอ',
               'โมเดล `stabilityai/sdxl-turbo` สร้างภาพ 512x512 แบบ 4 steps บน GPU ใบแรก **ครั้งละ 1 ภาพ**',
               'ทดสอบจากนอกเครื่อง: ส่งพร้อม key ต้องได้ภาพ และส่งโดยไม่มี key ต้องได้ **401**']},
    {"img": "n05-step3-ramp", "title": "ขั้นที่ 3: ไล่ระดับผู้ใช้จนไม่ผ่าน SLO แล้วหาค่ากึ่งกลาง",
     "labels": ["1 เขียน loadtest.py", "2 ไล่ระดับ N = 1, 8, 16, 24, 32, …", "3 ระดับแรกที่ไม่ผ่าน → หยุด",
                "4 ลองระดับกึ่งกลางอีก 2 ครั้ง", "บันทึกเป็นไฟล์ JSON"],
     "scene": "A staircase rising left to right; each step holds a growing group of simulated users and a small result card. "
              "The early steps have green check marks, the last step has a red cross. A magnifying glass looks between the last green step "
              "and the red step. A person with a laptop at the bottom left writes a script (badge 1). A JSON file icon at the bottom right.",
     "steps": ['ผู้ใช้จำลองแต่ละคนวนใช้คำบรรยาย 12 ข้อ รอจนได้ภาพ พักดูภาพ 2.5–7.5 วินาที แล้วส่งใหม่ และนับงานที่รอเกิน 30 วินาทีเป็นงานล้ม',
               'ไล่ระดับ N = 1, 8, 16, 24, 32, 48, 64, 96, 128, 160, 192, 256, 320 ระดับละ 30 วินาที โดยไม่นับ 10 วินาทีแรก',
               'เมื่อพบระดับแรกที่ไม่ผ่าน SLO ให้หยุด แล้วลองระดับกึ่งกลางอีก 2 ครั้งเพื่อให้ได้ค่าที่ละเอียดขึ้น',
               'ทุกระดับบันทึกภาพต่อวินาที p50 p95 p99 งานล้ม (%) GPU utilization และ CPU ของตัวยิงโหลดเป็นไฟล์ JSON']},
    {"img": "n06-step11-cleanup", "title": "ขั้นที่ 11: ลบเครื่อง แล้วสรุปยอดจากใบแจ้งหนี้",
     "labels": ["1 ลบเครื่อง vapp-lab9", "2 ตรวจว่าไม่มีเครื่องค้าง", "3 ปิด container ของเว็บ", "4 สรุปยอดจากใบแจ้งหนี้",
                "GPU · Disk · รับส่งข้อมูล"],
     "scene": "Four numbered panels left to right: (1) a cloud GPU server with a tag being moved into a large recycle bin; "
              "(2) a person checking an account list with a magnifying glass, the list is empty; (3) a laptop showing a small container box "
              "being switched off; (4) an invoice paper with three line items and a total line (no numbers), a person reading it.",
     "steps": ['ลบเครื่องป้าย `vapp-lab9` แล้วตรวจว่าไม่มีเครื่องป้ายนี้ค้างในบัญชี โดยไม่แตะเครื่องที่มีป้ายอื่น',
               'ปิด container ของเว็บในโฟลเดอร์ `lab9_hybrid/code/web`',
               'สรุปค่าใช้จ่ายจริง ได้แก่ อายุเครื่อง ราคาต่อชั่วโมง และยอดที่ถูกคิดแยกเป็น GPU, disk และรับส่งข้อมูล',
               'ตัวเลขทั้งหมดอ่านจาก **ใบแจ้งหนี้ของบัญชี** ไม่ได้คำนวณเอง']},
]

PHOTOS = [
    {"img": "s01-gpu-service", "scene": "A Thai engineer in a small startup operations room at night watches two monitors with abstract "
                                         "blurred line graphs, next to an open server rack with glowing graphics cards. Calm focused mood."},
    {"img": "s02-many-users", "scene": "Many young Thai adults in a busy co-working cafe all looking at their phones at the same time, "
                                        "waiting for something to load; soft bokeh lights. Mood: many people using one service at once."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, light background, rounded title banner, thick outlines, rounded cards, numbered circle badges, pastel palette,
bold rounded Thai lettering):
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
- Labels that start with a letter and a colon (for example "A: ...") are written in full as plain text, without a circle badge.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, paths, HTTP codes) use a monospace font.
- Characters: friendly fictional cartoon people (neutral, professional). Fictional cartoon characters only.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

PHOTO = """Generate ONE photorealistic image with your image generation tool and save it as a JPG file at exactly this path:
{out}/{img}.jpg

Scene: {scene}

Requirements:
- Photorealistic, natural light, shallow depth of field, landscape 16:9 (about 1920x1080).
- Setting: {setting}.
- People are fictional adults of Thai appearance; no real person's likeness.
- NO readable text anywhere: no letters, no numbers, no logos, no signs, no watermarks. Screens and papers must be blurred or abstract.
- Keep the left 45% of the frame calm and darker (out-of-focus background), main subject on the right side, because a title will be placed over the left side later.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

# ------------------------------------------------------------------ รอบที่ 2: ภาพอธิบายแบบตำรา (n2x) และภาพถ่าย (p2x)
# ตัวเลขทุกตัวในภาพมาจาก README.md (ดูบัญชีตัวเลขของรอบตรวจ) · ป้ายสั้น ภาษาไทยทางการ + ศัพท์อังกฤษตาม README
FIGS2 = [
    {"img": "n21-lesson-path", "title": "LAB 9 แบ่งเป็น 4 ส่วน",
     "labels": ["1 พื้นฐาน", "2 ทฤษฎี", "3 LAB", "4 สกิล v0",
                "คำถามของเจ้าของระบบ", "p95 · SLO · RabbitMQ · Batching", "Baseline → ระบบผสม → GPU 2 ใบ", "ทำซ้ำในคำสั่งเดียว"],
     "scene": "A horizontal path of four connected stations from left to right, like a route on a map, each station a rounded panel "
              "with a numbered badge and a small icon: (1) a business owner with a question mark next to a GPU card; "
              "(2) an open textbook with a small latency chart; (3) a rented cloud server with two graphics cards and a measuring stopwatch; "
              "(4) a document named SKILL with a single play button. Under each station its short description label. "
              "Arrows connect the stations in order."},
    {"img": "n22-p50-p95-loads", "title": "p50 และ p95 ก่อนและหลังอิ่มตัว",
     "labels": ["ก่อนอิ่มตัว", "อิ่มตัวแล้ว", "p50 = 0.47 s", "p95 = 1.12 s", "p50 = 8.42 s", "p95 = 9.19 s",
                "N = 8", "N = 30", "p95 มากกว่า p50 เกิน 2 เท่า", "p50 กับ p95 ใกล้กัน"],
     # รอบตรวจ: ภาพเดิมวาดฮิสโตแกรมที่ไม่ได้วัดจริง (ไม่มีข้อมูลเวลารอรายงาน) และเส้น p50 ไม่แบ่งพื้นที่ครึ่งหนึ่ง จึงตัดกราฟออก
     "scene": "Two side-by-side panels, NO chart, NO histogram, NO bars, NO axis, NO number line. Each panel shows a scene and two "
              "value cards stacked vertically (p50 card on top, p95 card below). Left panel (header label 'ก่อนอิ่มตัว' with a small "
              "tag 'N = 8'): an image-generation service counter where most users already hold their finished picture and are smiling, "
              "and only two users stand waiting with a stopwatch; under the two value cards a note card with the label about p95 being "
              "more than 2 times p50. Right panel (header label 'อิ่มตัวแล้ว' with a small tag 'N = 30'): the same counter with a long "
              "orderly queue where every user waits about equally long, each holding a stopwatch; under the two value cards a note card "
              "with the label that p50 and p95 are close. Both panels are the same size. Value cards are plain rounded boxes of equal size "
              "with the text only (no bars or lengths that suggest a scale)."},
    {"img": "n23-scaling", "title": "Scaling Efficiency ของระบบผสม",
     "labels": ["Worker 1 ตัว · 52 คน", "Worker 2 ตัว · 104 คน", "Efficiency 100%", "คิว jobs เดียวกัน"],
     "scene": "Left: one queue box feeding one GPU worker robot, with a group of user figures above it. Right: the same queue box feeding "
              "two GPU worker robots, with a group of user figures twice as large above them. Between left and right a big arrow. "
              "At the bottom a horizontal gauge filled completely, labelled with the efficiency label. Do not draw any other numbers.",
     },
    {"img": "n24-setup", "title": "ก่อนเริ่ม: งานเกิดขึ้นที่ไหนบ้าง",
     "labels": ["Claude Code บนเครื่องเรา", "container multi-account", "สกิล vastai", "เครื่องเช่า vapp-lab9",
                "RTX 3090 × 2", "เว็บ PixelQueue · พอร์ต 3408", "ไฟล์ .env (ห้ามแสดงค่า)"],
     "scene": "Left: a laptop on a desk showing a chat-style coding assistant window; next to it a box shaped like a shipping container "
              "connected to the laptop, with a small toolbox icon for the skill. A dashed arrow goes from the container through a cloud to "
              "a rented server on the right that has two graphics cards. A small browser window on the laptop shows a web app. "
              "A small locked key file sits next to the container. Each element has its label next to it."},
    {"img": "n25-step4-gateway", "title": "ขั้นที่ 4: gateway รับงานแล้วตอบทันที",
     "labels": ["1 POST /jobs + API key", "2 ส่งงานเข้าคิว jobs", "3 ตอบ 202 + เลขงาน", "4 GET /jobs/{เลขงาน}",
                "ยังไม่มี Worker", "ไม่มี key → 401", "คิวเต็ม → 429"],
     "scene": "Left: a user with a phone sends a ticket (badge 1) to a gateway counter in the middle. The gateway drops the ticket into a "
              "long queue box on the right (badge 2) and immediately hands a numbered receipt back to the user (badge 3). The user later "
              "asks the counter about the receipt (badge 4). To the right of the queue an empty worker chair with a GPU card, labelled as "
              "no worker yet. At the gateway, a small side door shows a stopped person without a key, and the queue entrance has a small "
              "full-sign. Each label placed next to its element."},
    {"img": "n26-step5-worker", "title": "ขั้นที่ 5: Worker ดึงงาน รวมเป็น batch แล้วจึง ack",
     "labels": ["1 ดึงงานจากคิว · prefetch 4", "2 สร้างภาพครั้งละไม่เกิน 4 ภาพ", "3 เก็บภาพ", "4 ack",
                "งานเสีย → jobs.dead", "GPU ใบแรก"],
     "scene": "A left-to-right flow: a queue box with tickets; a GPU worker robot takes a tray of up to four tickets from it (badge 1); "
              "the robot sits on a graphics card and produces four small pictures at once (badge 2); the pictures go into a storage shelf "
              "(badge 3); then a check-mark message arrow goes back to the queue (badge 4). Below the queue, one broken empty ticket slides "
              "down into a separate small box for bad jobs. Labels next to each element."},
    {"img": "n27-step6-measure", "title": "ขั้นที่ 6: ยิงโหลดชุดเดิมใส่ระบบผสม",
     "labels": ["1 loadtest.py · ระดับ N เดิม", "2 gateway + คิว", "3 Worker 1 ตัว · GPU ใบเดิม", "4 เทียบกับ Baseline",
                "ภาพต่อ batch โตตามโหลด"],
     "scene": "Left: a staircase of growing groups of simulated users with a laptop running a load test script (badge 1). Middle: arrows "
              "into a gateway and queue (badge 2), then one GPU worker robot on one graphics card (badge 3); above the robot, trays with "
              "one, two, three and four pictures getting fuller from left to right to show batch growing with load. Right: two result "
              "cards side by side, one grey for the old baseline and one teal for the new system, with a balance scale between them "
              "(badge 4). No numbers other than the badges."},
    {"img": "n28-step7-burst", "title": "ขั้นที่ 7: Burst 200 งานใน 10 วินาที",
     "labels": ["A: API Synchronous · เลิกรอที่ 30 วินาที", "B: ระบบผสม · ได้ 429 แล้วส่งใหม่", "งาน express แซงคิว",
                "งานเข้าพร้อมกันเป็นก้อน"],
     "scene": "Top: a sudden wave of many job tickets arriving at once from the left. The wave splits into two lanes. Lane A (top): users "
              "holding phones on open calls in front of one server, some giving up and walking away. Lane B (bottom): users receive "
              "tickets from a gateway, some get a small 'come back later' card and send again, jobs wait in a queue, and a few tickets "
              "with a lightning mark jump to the front of the queue. Both lanes end at one graphics card each of the same size. "
              "No numbers other than those in the labels."},
    {"img": "n29-step8-second-worker", "title": "ขั้นที่ 8: เปิด Worker ตัวที่สองบน GPU ใบที่สอง",
     "labels": ["gateway เดิม", "คิว jobs เดิม", "Worker gpu0", "Worker gpu1 · ตัวที่สอง", "ไม่แก้โค้ด"],
     "scene": "A gateway counter on the left, a single queue box in the middle, and two GPU worker robots on the right, each on its own "
              "graphics card. The upper robot is already working; the lower robot is just switched on with a small power symbol and a "
              "soft highlight. Both robots pull tickets from the same queue. The gateway and the queue have a small padlock-like "
              "'unchanged' seal. Labels next to each element."},
    {"img": "n30-step9-kill", "title": "ขั้นที่ 9: ปิด Worker กลางงาน แล้วนับงาน",
     "labels": ["1 ส่ง 90 งานใน 3 วินาที", "2 ปิด gpu1 ที่วินาทีที่ 4", "3 งานที่ยังไม่ ack กลับเข้าคิว",
                "4 report.py → metrics.json + กราฟ 6 ภาพ", "งานเสีย → jobs.dead"],
     "scene": "Left: a burst of tickets entering a queue (badge 1). Two GPU worker robots take tickets from the queue; the lower robot "
              "is suddenly switched off with a red power-off symbol while holding a tray of tickets (badge 2); its tickets travel back "
              "into the queue with a curved arrow and the upper robot takes them (badge 3). One broken empty ticket drops into a small "
              "separate box. Right: a report document producing a metrics file and a small grid of six chart thumbnails (badge 4)."},
    {"img": "n31-lessons", "title": "สิ่งที่ได้เรียนจาก LAB 9",
     "labels": ["Batching: 30 → 52 คน", "ack หลังเก็บภาพ: งานหาย 0", "เพิ่ม Worker: 52 → 104 คน",
                "ตรวจกราฟกับข้อมูลดิบ", "ความจุเปลี่ยนตามเครื่อง"],
     "scene": "Five panels arranged as two rows (three on top, two below), each a small clear icon scene with its label: "
              "a GPU card producing four pictures at once; a queue with a check-mark returning to it; two GPU worker robots side by side; "
              "a magnifying glass over a line chart next to a raw data file; two different servers with different speedometers. "
              "No numbers other than those in the labels."},
]

PHOTOS2 = [
    {"img": "p21-owner-question", "scene": "A Thai business owner in their thirties stands in a small server room, one hand on an open rack "
                                           "with a single glowing graphics card, looking thoughtfully at a wall display with abstract blurred "
                                           "rising curves. Quiet evening light, contemplative mood."},
]

ILLUS = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

Look at this reference image only for the colour palette of the course (navy, teal, orange, soft pastel backgrounds):
{refs}

Style: a clean, modern, flat explanatory figure that could appear in a well-made university textbook. Light background,
simple geometric shapes, thin dark outlines, soft shadows, generous white space, rounded panels. Not childish, no cartoon
faces with big eyes; people are simple neutral flat figures. Numbered circle badges (navy circle, white digit) where order matters.
Canvas: landscape 4:3 (about 1448 x 1086). Setting: {setting}.

Title text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers, units and symbols stay exactly as they are.
- Do NOT add any other words, numbers, captions, axis values, watermarks or logos beyond the title and the labels above.
- When a label starts with a number followed by a space (for example "3 gate"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Labels that start with a letter and a colon (for example "A: ...") are written in full as plain text, without a circle badge.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, paths, HTTP codes) use a monospace font.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--pass2":
    out = os.path.abspath(sys.argv[2]).replace("\\", "/")
    refs = [os.path.abspath(p).replace("\\", "/") for p in sys.argv[3:]]
    os.makedirs(out, exist_ok=True)
    for f in FIGS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(ILLUS.format(
            out=out, img=f["img"], refs="\n".join(refs), setting=SETTING, title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
    for f in PHOTOS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=SETTING, scene=f["scene"]))
    print("%d พรอมต์ -> %s" % (len(FIGS2) + len(PHOTOS2), out))
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
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=SETTING, scene=f["scene"]))
    print("%d พรอมต์ -> %s" % (len(FIGS) + len(PHOTOS), out))
