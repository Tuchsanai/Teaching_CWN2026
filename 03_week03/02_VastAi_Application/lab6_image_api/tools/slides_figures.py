#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ LAB 6 (API ตรวจภาพ YOLO · วัดความจุผู้ใช้พร้อมกัน)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล)
  title  หัวข้อของสไลด์ และข้อความบนป้ายชื่อของภาพ
  labels ข้อความสั้นบนภาพ
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ
  steps  ขั้นตอนข้างภาพ 3-5 ขั้น · เรียบเรียงจาก README.md ของบท
PHOTOS = ภาพถ่ายสมจริงของหน้าปกและหน้าคั่น (ไม่มีตัวอักษรในภาพ)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
"""
import os, sys

SETTING = ('a construction company whose site workers send photos of the construction site from their phones to an '
           'image-inspection API (safety equipment detection) running on one rented GPU server with two RTX 3090 cards')

FIGS = [
    {"img": "n01-step1-rent", "title": "ขั้นที่ 1: เช่าเครื่อง RTX 3090 2 ใบ ตามเกณฑ์",
     "labels": ["1 RTX 3090 2 ใบ", "≤ $0.60 ต่อชั่วโมง", "2 verified · CPU 24 cores ขึ้นไป", "3 PyTorch 2.8 · CUDA 12.8",
                "disk 40 GB · พอร์ต 8080", "4 เห็น GPU ครบ 2 ใบ", "vapp-lab6"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a person browsing a catalogue of GPU servers and "
              "picking one server with two GPU cards and a price tag; (2) a checklist board with a verified shield and a CPU chip; "
              "(3) a container box being loaded onto the server with a disk and a port socket; (4) the robot inspecting the "
              "server and seeing two GPU cards. A small name tag 'vapp-lab6' hangs on the server.",
     "steps": ["**เช่า RTX 3090 2 ใบในเครื่องเดียว** ราคารวมไม่เกิน $0.60 ต่อชั่วโมง ตั้งป้าย `vapp-lab6`",
               "**คัดเครื่อง**: verified · เน็ตเร็ว · CPU 24 cores ขึ้นไป · ไม่อยู่ในจีน · เอาเครื่องที่ถูกที่สุด",
               "**image** PyTorch 2.8 + CUDA 12.8 · disk 40 GB · เปิดพอร์ต 8080 ให้ผู้ใช้เรียก API",
               "**รอจนพร้อม** แล้วเข้าไปเห็น GPU ครบ 2 ใบ · เกิน 10 นาทีให้ลบแล้วเช่าเครื่องอื่น"]},
    {"img": "n02-step2-server", "title": "ขั้นที่ 2: AI server รับรูป แล้วตอบเป็น JSON",
     "labels": ["1 POST /v1/detect", "Bearer API key", "2 FastAPI server", "คิว", "3 YOLO best.pt", "GPU 0",
                "4 JSON", "ไม่มี key → 401"],
     "scene": "A left-to-right flow: (1) a site worker's phone sends a construction photo with a key card; (2) a server box with "
              "a small waiting queue of photos; (3) the server calls a GPU card that draws boxes around helmets and vests on the "
              "photo; (4) a JSON document returns to the phone. Below, a second phone without a key is stopped by a red barrier.",
     "steps": ["ผู้ใช้ส่งรูปที่ **`POST /v1/detect`** (ช่อง `file`) พร้อม API key แบบ Bearer · ไม่มีหรือผิดได้ **401**",
               "server 1 process เรียกโมเดลได้ทีละครั้ง คำขอที่มาระหว่างนั้น **เข้าคิวรอ**",
               "โมเดล YOLO `best.pt` ตรวจที่ขนาด 640 ความมั่นใจขั้นต่ำ 0.35 บน **GPU ใบแรก**",
               "ตอบ JSON: `detections` · `replica` · `timing_ms` · `batch_size` · มี `GET /health` ไว้เช็กว่าพร้อม"]},
    {"img": "n03-step3-cluster", "title": "ขั้นที่ 3: ผู้ใช้เข้าทาง NGINX พอร์ต 8080 จุดเดียว",
     "labels": ["cluster.sh", "1 replica", "2 process", "3 batch", "NGINX :8080", "round-robin", "127.0.0.1", "up · status · down"],
     "scene": "On the left a control panel labelled cluster.sh with three numbered dials. In the middle a single gate (load "
              "balancer) that all users pass through, handing requests in turn to server processes. On the right the server "
              "processes sit inside a fenced area marked as local-only, connected to GPU cards. Three buttons under the panel.",
     "steps": ["`cluster.sh` เปิดระบบใหม่ได้ด้วย **ค่า 3 ตัว**: จำนวน replica · process ต่อ replica · ขนาด batch สูงสุด",
               "**NGINX พอร์ต 8080** แจกคำขอให้ server ทุก process แบบ round-robin",
               "server ฟัง **ภายในเครื่องเท่านั้น** (`127.0.0.1`) ยิงตรงจากนอกเครื่องไม่ได้",
               "มีคำสั่งเปิด · ดูสถานะ · ปิดทั้งระบบ · API key สุ่มครั้งแรกแล้วใช้ค่าเดิม"]},
    {"img": "n04-step9-close", "title": "ขั้นที่ 9: ทำกราฟ เก็บผล แล้วลบเครื่อง",
     "labels": ["1 report.py", "metrics.json", "2 กราฟ 5 ภาพ", "3 results · code", "4 ลบ vapp-lab6", "5 ค่าใช้จ่ายจริง"],
     "scene": "Five numbered scenes left to right connected by arrows: (1) a script reads many result files; (2) it produces a "
              "summary file and a stack of charts; (3) a box of result files and code is carried back from the rented server to "
              "a laptop; (4) the rented server is switched off and removed; (5) a person checks a bill receipt.",
     "steps": ["เขียน **`report.py`** อ่านผลทุกชุด (base1 batch1 gpu1 gpu2 lc2 rr_slow lc_slow fo_noretry fo_retry) รวมเป็น `metrics.json`",
               "วาด **กราฟ PNG** ชุดหลักและชุดเสริม แล้วเปิดดูว่าอ่านออก",
               "เก็บ **ผลทั้งหมดและโค้ดทุกไฟล์** กลับมาไว้ในโฟลเดอร์ของบท",
               "**ลบเครื่องป้าย `vapp-lab6`** ตรวจว่าไม่มีค้าง แล้วสรุป **ค่าใช้จ่ายจริง**"]},
    {"img": "n05-step11-reuse", "title": "ขั้นที่ 11: สกิล v0 ทำซ้ำได้ในคำสั่งเดียว",
     "labels": ["1 พรอมต์", "gpu-api-capacity", "scripts/", "2 เช่า", "3 วัด 2 แบบ", "4 ลบเครื่อง", "results_skill"],
     "scene": "On the left a single prompt card goes into a skill folder that contains a manual and a box of ready-made scripts. "
              "From the folder the robot follows a numbered track: rent a GPU server, measure two set-ups with a gauge, then "
              "switch off and remove the server. At the end the results land in a folder.",
     "steps": ["วาง **พรอมต์เดียว**: ใช้สกิล `gpu-api-capacity` บน RTX 3090 2 ใบ ป้าย `vapp-lab6-skill`",
               "AI ตัวใหม่ **ใช้โค้ดใน `scripts/`** ไม่ต้องเขียนใหม่: เช่า ติดตั้ง ทดสอบ API",
               "วัดแค่ **2 แบบ**: GPU 1 ใบทีละคำขอ · GPU 2 ใบ Micro-batching + 4 process · N = 16, 64, 128, 256, 512",
               "เก็บผลที่ `results_skill` **ลบเครื่อง** แล้วเทียบกับผลรอบหลักและค่าใช้จ่ายจริง"]},
]

# ภาพรอบที่ 2 (ปรับสไลด์ให้อธิบายด้วยภาพ) · n20-n22 แทน n02 n04 n05 ซึ่งมีจุดที่อาจทำให้เข้าใจผิด
FIGS2 = [
    {"img": "n20-step2-server", "title": "ขั้นที่ 2: AI server รับรูป แล้วตอบเป็น JSON",
     "labels": ["1 POST /v1/detect", "Bearer API key", "2 FastAPI server", "คิว", "3 YOLO best.pt", "GPU 0", "4 JSON",
                "ไม่มี key", "401"],
     "scene": "Two lanes separated by a thin dashed line. UPPER LANE (the normal path), four numbered panels left to right joined "
              "by blue arrows: (1) a site worker's phone sends a construction photo together with a key card; (2) a server box "
              "with a short queue of three waiting photos in front of it; (3) a GPU card inside the server draws green boxes "
              "around helmets and vests on the photo; (4) a JSON document. One blue return arrow runs ABOVE the four panels from "
              "the JSON document back to the SAME worker's phone. LOWER LANE: a second worker's phone WITHOUT any key sends a "
              "request (red arrow pointing right) that is stopped by a red barrier standing in front of a small server door; "
              "from the barrier exactly ONE red arrow points back LEFT to the second phone, with a small red tag reading 401 on "
              "that arrow. Nothing crosses the barrier: no arrow goes from the barrier to the server, the GPU or the upper lane.",
     "steps": ["ผู้ใช้ส่งรูปที่ **`POST /v1/detect`** (ช่อง `file`) พร้อม API key แบบ Bearer · ไม่มีหรือผิดได้ **401**",
               "server 1 process เรียกโมเดลได้ทีละครั้ง คำขอที่มาระหว่างนั้น **เข้าคิวรอ**",
               "โมเดล YOLO `best.pt` ตรวจที่ขนาด 640 ความมั่นใจขั้นต่ำ 0.35 บน **GPU ใบแรก**",
               "ตอบ JSON: `detections` · `replica` · `timing_ms` · `batch_size` · มี `GET /health` ไว้เช็กว่าพร้อม"]},
    {"img": "n21-step9-close", "title": "ขั้นที่ 9: ทำกราฟ เก็บผล แล้วลบเครื่อง",
     "labels": ["1 report.py", "metrics.json", "2 กราฟ PNG", "3 results · code", "4 ลบ vapp-lab6", "5 ค่าใช้จ่ายจริง"],
     "scene": "Five numbered panels left to right joined by arrows. Panel 1: a script window reads a stack of result files and "
              "writes ONE summary document; the label metrics.json is written directly under that summary document, inside "
              "panel 1. Panel 2: a few paper sheets with line charts and bar charts only (no pie chart, no donut chart). "
              "Panel 3: a person and the robot carry a box of result files and one code file from the rented GPU server down to "
              "a laptop. Panel 4: the rented GPU server is switched off with a red power button and dropped into a bin. "
              "Panel 5: a person checks a bill receipt next to a calculator.",
     "steps": ["เขียน **`report.py`** อ่านผลทุกชุด (base1 batch1 gpu1 gpu2 lc2 rr_slow lc_slow fo_noretry fo_retry) รวมเป็น `metrics.json`",
               "วาด **กราฟ PNG** ชุดหลักและชุดเสริม แล้วเปิดดูว่าอ่านออก",
               "เก็บ **ผลทั้งหมดและโค้ดทุกไฟล์** กลับมาไว้ในโฟลเดอร์ของบท",
               "**ลบเครื่องป้าย `vapp-lab6`** ตรวจว่าไม่มีค้าง แล้วสรุป **ค่าใช้จ่ายจริง**"]},
    {"img": "n22-step11-reuse", "title": "ขั้นที่ 11: สกิล v0 ทำซ้ำได้ในคำสั่งเดียว",
     "labels": ["1 พรอมต์เดียว", "gpu-api-capacity", "SKILL.md", "scripts/", "2 เช่าเครื่อง", "3 วัด 2 แบบ", "4 ลบเครื่อง",
                "results_skill"],
     "scene": "One numbered track, left to right on the top row and continuing left to right on the bottom row. (1) A person "
              "hands the robot a single paper card that shows three short lines of text (text lines only, no picture or photo "
              "icon on the card); the card goes into a folder that holds a manual and a code box. (2) The robot rents one GPU "
              "server with two GPU cards. (3) Two set-ups measured with one gauge: a server with one GPU card lit and a server "
              "with two GPU cards lit. (4) The server is switched off and put into a bin. At the end a results folder holding "
              "table sheets. No crowd of workers and no construction scene.",
     "steps": ["วาง **พรอมต์เดียว**: ใช้สกิล `gpu-api-capacity` บน RTX 3090 2 ใบ ป้าย `vapp-lab6-skill`",
               "AI ตัวใหม่ **ใช้โค้ดใน `scripts/`** ไม่ต้องเขียนใหม่: เช่า ติดตั้ง ทดสอบ API",
               "วัดแค่ **2 แบบ**: GPU 1 ใบทีละคำขอ · GPU 2 ใบ Micro-batching + 4 process · N = 16, 64, 128, 256, 512",
               "เก็บผลที่ `results_skill` **ลบเครื่อง** แล้วเทียบกับผลรอบหลักและค่าใช้จ่ายจริง"]},
    {"img": "n23-plan", "title": "บทนี้มี 3 ภาค",
     "labels": ["1 ภาคพื้นฐาน", "ข้อมูล · โมเดล · ทฤษฎี", "2 ภาค LAB ขั้นที่ 1–9", "วัด 4 แบบ · ทดลองเสริม 2 เรื่อง",
                "3 ปิดท้าย ขั้นที่ 10–11", "สกิลเวอร์ชัน 0"],
     "scene": "A road with three large numbered stations from left to right joined by arrows. Station 1: an open textbook with a "
              "small latency chart and a construction-site photo beside it. Station 2: a rented GPU server with two GPU cards, a "
              "speed gauge and four small test tokens in a row. Station 3: a folder holding a manual and a code box, with a "
              "circular repeat arrow around it. A small team of people and the robot walk along the road."},
    {"img": "n24-request", "title": "คำขอ 1 ครั้ง: ส่งรูปพร้อม key แล้วได้ JSON กลับ",
     "labels": ["POST /v1/detect", "Authorization: Bearer <API key>", "file = รูป JPEG", "NGINX :8080",
                "detections", "replica", "timing_ms", "batch_size"],
     "scene": "Left: a site worker's phone sends one envelope (the request) with two tags attached to it, one tag for the "
              "Authorization header and one tag for the attached photo file. Middle: the envelope passes one gate (NGINX :8080) "
              "and reaches a server with a GPU card. Right: a large JSON card comes back to the phone; the card has four rows, "
              "each row with a small icon and its label: boxes drawn on a construction photo (detections), a small server name "
              "tag (replica), a stopwatch (timing_ms), a stack of photos (batch_size)."},
    {"img": "n25-remeasure", "title": "วัดครั้งเดียวเชื่อไม่ได้: วัดซ้ำก่อนสรุป",
     "labels": ["1 สะดุดครั้งเดียวที่ N=64", "ครั้งแรก 32 คน → วัดซ้ำ 176 คน", "2 ก่อนแก้บั๊ก 18 คน", "server ฉบับแก้แล้ว 22 คน"],
     "scene": "Two horizontal rows. Row 1: a server with two GPU cards; beside it a small latency chart with one single tall "
              "spike; a person with a magnifying glass repeats the measurement three times (three small green check marks), "
              "and an arrow leads from a small grey result card to a larger green result card. Row 2: a server with one GPU "
              "card; the robot removes a small bug (a beetle) from the server code with a wrench; an arrow leads from a small "
              "grey result card to a larger green result card. Each label goes on the matching card or row."},
    {"img": "n26-prereq", "title": "ก่อนเริ่ม LAB: เตรียม 5 อย่าง",
     "labels": ["1 LAB 0: key 3 ตัว", "2 Claude Code ที่ 02_VastAi_Application", "3 best.pt · samples/",
                "4 ราว 2.5 ชั่วโมง · ราว $1", "5 ตอบเป็นภาษาไทย"],
     "scene": "Five numbered items laid out in a row on a long desk, each in its own pastel card: (1) three key cards on a key "
              "ring; (2) a laptop with a terminal window and a folder; (3) a model file icon next to a folder of six "
              "construction photos; (4) a clock next to a small stack of coins; (5) a chat speech bubble from a person to the "
              "robot."},
    {"img": "n27-step5-configs", "title": "ขั้นที่ 5: เปิดระบบใหม่ 2 แบบบน GPU ใบเดิม",
     "labels": ["cluster.sh", "1 batch1", "replica 1 · process 1 · batch 32", "2 gpu1", "replica 1 · process 4 · batch 32",
                "GPU 0", "loadgen.py · SLO เดิม"],
     "scene": "Left: a control panel with three dials (the cluster.sh launcher). Two arrows lead right to two set-ups stacked "
              "vertically. Top set-up (1): ONE server process that collects many photos into one batch (like a bus) and feeds "
              "a single GPU card. Bottom set-up (2): FOUR server processes side by side, each collecting its own small batch, "
              "all feeding the SAME single GPU card. On the far right one load generator gauge measures both set-ups with the "
              "same rule."},
    {"img": "n28-twovars", "title": "replica เท่ากัน: 2 ตัวแปรเปลี่ยนพร้อมกัน จึงยังสรุปไม่ได้",
     "labels": ["round-robin · gpu2", "176 คน", "least_conn · lc2", "256 คน", "1 วิธีแจกงาน", "2 ค่า zone ของ NGINX",
                "ยังสรุปไม่ได้"],
     "scene": "Two set-ups side by side, each a load balancer gate with two equal GPU servers behind it: in BOTH set-ups the "
              "gate sends exactly ONE photo card to each of its two servers (the split is equal, about half and half, on both "
              "sides; never draw a stack or more cards going to one server). Each set-up shows one result card under it. Between the two set-ups, two control knobs are both turned and highlighted in orange "
              "(badges 1 and 2). Above them a balance scale with a question mark, and an orange stamp with the last label."},
    {"img": "n29-lessons", "title": "บทเรียนของ LAB นี้",
     "labels": ["1 ปรับใบเดิมก่อน แล้วค่อยเพิ่มใบ", "2 หาคอขวดก่อนเพิ่ม GPU", "3 วัดซ้ำก่อนสรุป", "4 เปลี่ยนทีละตัวแปร",
                "5 ผลแย่ลงผิดปกติ ให้หาบั๊ก", "6 นับเฉพาะคำขอที่สำเร็จ"],
     "scene": "A 3 x 2 grid of six numbered panels, one lesson each: (1) one GPU card being filled to the top before a second "
              "card is added; (2) four small gauges with one gauge in the red, a magnifying glass on it; (3) a person repeating "
              "a measurement three times with check marks; (4) a control panel where only one dial is turned while the others "
              "are locked; (5) the robot finding a small bug (beetle) under a falling chart; (6) a stack of requests where "
              "green successful ones are counted and red failed ones are set aside."},
]

PHOTOS2 = [
    {"img": "p20-owner", "scene": "Inside a site office container at a busy construction site, a project engineer in a hard hat sits "
                                  "at a laptop with a thoughtful expression; through the large window behind, several workers "
                                  "in high-visibility vests hold up phones to photograph scaffolding. Mood: many inspection "
                                  "photos arriving at the same moment, and one person wondering how much the system can take."},
]

PHOTOS = [
    {"img": "s01-cover", "scene": "On an active construction site at golden hour, a site safety officer wearing a hard hat and a "
                                  "high-visibility vest holds up a smartphone to photograph workers on scaffolding. Mood: many "
                                  "photos being sent for inspection at the same time."},
    {"img": "s02-lab", "scene": "Inside a dim server room, an engineer in a hoodie checks an open rack server with two large "
                                "graphics cards glowing softly, a laptop on a cart beside the rack. Mood: preparing a GPU "
                                "server for a load test."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, light pastel background, rounded title banner, thick outlines, rounded pastel cards, numbered circle badges,
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
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, JSON, exit codes) use a monospace font.
- Characters: a friendly team of people and one small white-and-teal robot that represents the AI. Fictional cartoon characters only.

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

CLEAN = ("\nLook: a clean, well-made textbook figure in that same style. Few elements, generous white space, arrows that "
         "show exactly one reading direction, every arrow means what the scene says and nothing more. Not childish.\n")

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--pass2":           # ภาพรอบที่ 2 เท่านั้น
        FIGS, PHOTOS, args = FIGS2, PHOTOS2, args[1:]
        CARTOON = CARTOON.replace("\nCanvas:", CLEAN + "\nCanvas:")
    sys.argv = [sys.argv[0]] + args
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
