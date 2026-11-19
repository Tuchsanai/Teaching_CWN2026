#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ LAB 4 (1 GPU เทียบ 2 GPU)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล · ใช้เลขนำหน้าเรียงตามลำดับในสไลด์ เช่น n01-...)
  title  หัวข้อของสไลด์ และข้อความบนป้ายชื่อของภาพ
  labels ข้อความสั้นบนภาพ (3-10 ป้าย · ป้ายที่เป็นขั้นตอนขึ้นต้นด้วยเลข เช่น "1 วัดรุ่นฐาน")
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ: มีอะไรอยู่ตรงไหน เรียงอย่างไร (ไม่ต้องบรรยายสไตล์)
  steps  ขั้นตอนข้างภาพ 3-5 ขั้น · เรียบเรียงจาก README.md ของบท ห้ามมีตัวเลขหรือข้อเท็จจริงที่ไม่อยู่ใน README
PHOTOS = ภาพถ่ายสมจริงของหน้าปกและหน้าคั่น (ไม่มีตัวอักษรในภาพ · ฝั่งซ้ายมืดไว้วางหัวข้อ)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
      เขียนพรอมต์ 1 ไฟล์ต่อภาพ (<img>.txt) · ภาพอ้างอิงสไตล์ = ภาพการ์ตูนเดิมของบท 1-2 ภาพ
      ถ้าไม่ระบุ ใช้ assets/style-cartoon-1.jpg และ -2.jpg ของสกิล readme-slides
"""
import os, sys

SETTING = ('a small Thai university AI lab that rents a cloud GPU server (one machine with two RTX 3090 graphics cards) '
           'to train a hard-hat detection model for construction-site safety (decorations: server rack, GPU cards, '
           'yellow hard hats, stopwatch, coins)')

FIGS = [
    {"img": "n01-label", "title": "label 1 บรรทัด = 1 กรอบ มี 5 ช่อง",
     "labels": ["label: 1 0.5697 0.3029 0.1226 0.1779", "ช่อง 1 = คลาส helmet", "ช่อง 2–3 = จุดกลาง x, y",
                "ช่อง 4–5 = กว้าง, สูง", "ภาพ 416 × 416", "ทุกค่าเป็นสัดส่วนของภาพ 0–1"],
     "scene": "Top: a long monospace text strip showing the label line, split into three colored segments (first number, "
              "next two numbers, last two numbers). Below: a square photo frame of a construction worker wearing a yellow hard hat, "
              "with a green bounding box around the head; a dot marks the box center with dashed lines to the image edges, and "
              "double-headed arrows show the box width and height. Three colored callout cards (matching the three segment colors) "
              "connect each segment to its meaning. A small ruler-like badge shows the image size.",
     "steps": ["**1 กรอบ = 1 บรรทัด** มี 5 ช่อง ทุกค่าเป็นสัดส่วนของภาพ (0–1)",
               "ช่อง 1 คือ **คลาส** · `0 head` = ไม่สวมหมวก · `1 helmet` = สวมหมวกนิรภัย",
               "ช่อง 2–3 คือ **จุดกลางกรอบ** x, y (ราว 237, 126 px)",
               "ช่อง 4–5 คือ **กว้าง, สูง** ของกรอบ (ราว 51 × 74 px)"]},
    {"img": "n02-experiment", "title": "การทดลอง: ตรึงทุกค่า เปลี่ยนแค่จำนวน GPU",
     "labels": ["A = GPU 1 ใบ", "B = GPU 2 ใบ (DDP)", "เครื่องเดียวกัน", "5 Epoch · ภาพ 640", "batch 32 ภาพต่อ GPU · seed 0",
                "วัดวินาทีต่อ Epoch"],
     "scene": "Center: one open server machine with two graphics cards. Left lane labelled A: the same machine with only the left "
              "card glowing (the right card dark). Right lane labelled B: both cards glowing and connected. Between the lanes a "
              "padlocked settings board lists the fixed settings (two label lines). At the bottom a big stopwatch with the "
              "measurement label. A friendly team member compares the two lanes with a clipboard.",
     "steps": ["**A** = เทรนด้วย GPU 1 ใบ · **B** = เทรนงานเดิมด้วย GPU 2 ใบ (DDP) บนเครื่องเดียวกัน",
               "**ค่าที่ตรึงไว้**: 5 Epoch · ภาพ 640 · batch 32 ภาพต่อ GPU · seed 0 · วัด Validation ครั้งเดียวตอนจบ",
               "**วิธีวัด**: วินาทีต่อ Epoch (เฉลี่ย Epoch 2–4) · วินาทีต่อ step · GPU util · CPU ที่ใช้จริง · All-reduce 80 MB · mAP50",
               "**เครื่อง**: RTX 3090 2 ใบในเครื่องเดียว · เพดาน $0.60/ชม. · ได้เครื่อง $0.414/ชม."]},
    {"img": "n03-topology", "title": "ระดับทางเชื่อมระหว่าง GPU จากดีไปแย่",
     "labels": ["NV# · NVLink สายตรง", "PIX / PXB · ใต้ PCIe switch เดียวกัน", "PHB · ผ่าน Host Bridge ของ CPU",
                "NODE / SYS · ข้าม Host Bridge หรือ CPU socket", "เครื่องใน LAB นี้", "nvidia-smi topo -m"],
     "scene": "A vertical ladder of four horizontal rungs from top (best, green) to bottom (worst, red). Each rung shows two small "
              "GPU cards and the data path between them: top rung a short direct cable; second rung both cards under one small "
              "switch chip; third rung the path goes down through a CPU chip and back up; bottom rung the path crosses between two "
              "CPU chips. A big star marker with the label for this lab points at the third rung. A terminal window badge at the "
              "top shows the command label.",
     "steps": ["ดูด้วยคำสั่ง `nvidia-smi topo -m` ทุกครั้ง ก่อนใช้หลาย GPU",
               "`NV#` **NVLink** สายตรงระหว่าง GPU · `PIX` / `PXB` อยู่ใต้ PCIe switch เดียวกัน ไม่ผ่าน CPU",
               "**`PHB`** ผ่าน PCIe Host Bridge ของ CPU · **เครื่องใน LAB นี้**",
               "`NODE` / `SYS` ข้าม Host Bridge หรือข้าม CPU socket"]},
    {"img": "n04-meter", "title": "เงินเดินตลอดเวลาที่เครื่องเปิด ไม่ใช่แค่ตอนเทรน",
     "labels": ["เช่าเครื่อง", "AI เขียนโค้ด", "เทรนจริง", "รอพรอมต์ถัดไป", "ลบเครื่อง",
                "เครื่องเปิด 76.5 นาที", "$0.414 ต่อชั่วโมง"],
     "scene": "A long horizontal timeline bar from left to right with five stops (no number badges on the stops, only their labels). Above the whole bar runs a taxi-style "
              "money meter with coins dropping continuously along the entire length. Only the middle training segments are "
              "highlighted with GPU icons; the coding and waiting segments show a robot typing and a person drinking coffee, but coins "
              "still drop there too. At the right end a trash-can icon stops the meter. A brace under the whole bar carries the "
              "machine-open label.",
     "steps": ["**ตั้งแต่ขั้นที่ 1 เงินเริ่มเดิน** ชั่วโมงละ $0.414 จนกว่าจะลบเครื่องในขั้นที่ 6",
               "เทรนจริงรวมราว 20 นาที แต่ **เครื่องเปิด 76.5 นาที**",
               "เงินเดินรวมช่วงที่ AI เขียนโค้ด และช่วงที่เรายังไม่วางพรอมต์ถัดไป",
               "ลบเครื่องแล้วทุกอย่างบนเครื่องหายหมด · ผลถูกเก็บกลับมาที่ `lab4_multigpu/results` ตั้งแต่ขั้นที่ 5"]},
]

PHOTOS = [
    {"img": "s00-cover", "scene": "Close-up inside an open rack-mounted GPU server in a dim data center: two large graphics cards "
                                  "installed side by side in the same machine, cooling fans and cables, soft teal and amber status "
                                  "lights. Rows of server racks blurred in the background. Mood: computing power, comparison of one "
                                  "card against two."},
    {"img": "s01-lab", "scene": "A university student in a hoodie sits at a desk in a small lab in the evening, looking at a laptop "
                                "whose screen shows abstract, blurred progress charts; a stopwatch and a coffee mug on the desk, a "
                                "yellow hard hat on a shelf, a server rack with glowing lights blurred in the background. Mood: "
                                "focused measurement and waiting for a training run."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, light pastel background, rounded title banner, thick outlines, rounded cards,
numbered circle badges, the same palette, bold rounded Thai lettering):
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

# ------------------------------------------------------------------ ชุดที่ 2 (ปรับสไลด์รอบสอง)
# FIGS2   = ภาพอธิบายแบบแผนภาพในตำรา (flat, modern) ป้ายอยู่ในภาพ
# PHOTOS2 = ภาพถ่ายสมจริงของหน้าคั่นแต่ละส่วนและแต่ละขั้น (ไม่มีตัวอักษร)
FIGS2 = [
    {"img": "n21-roadmap", "title": "LAB 4 มี 4 ส่วน",
     "labels": ["1 พื้นฐาน", "Dataset โมเดล และทฤษฎี", "2 ภาค LAB ขั้นที่ 1–6", "เช่าเครื่อง เทรน แล้วลบเครื่อง",
                "3 ปิดท้าย ขั้นที่ 7–8", "เก็บงานเป็นสกิลเวอร์ชัน 0", "4 สรุป", "ผลรวมและสิ่งที่ยังไม่ผ่าน"],
     "scene": "A winding road seen from slightly above, going from left to right through four stations, each a rounded platform "
              "with a numbered circle badge (1 to 4) and its two labels: station 1 shows an open book with a hard hat and a small "
              "neural-network icon; station 2 shows a server with two graphics cards and a stopwatch; station 3 shows a document "
              "with a gear (a reusable recipe); station 4 shows a podium with a bar chart and a flag. Calm, lots of white space."},
    {"img": "n22-halfsteps", "title": "Batch รวมโตขึ้น 2 เท่า จำนวน step จึงเหลือครึ่งเดียว",
     "labels": ["Training Set ทั้งชุด = 1 Epoch", "1 GPU: batch 32 ภาพต่อ step", "461 step ต่อ Epoch",
                "2 GPU: batch รวม 64 ภาพต่อ step", "231 step ต่อ Epoch"],
     "scene": "Two horizontal tracks of exactly the same total length, one above the other, with a bracket over both carrying the "
              "Training Set label. Top track (one graphics card icon at its left end) is cut into many narrow equal blocks, each a "
              "small stack of photo thumbnails; its two labels sit at the left and at the right end. Bottom track (two graphics "
              "card icons at its left end) is cut into half as many blocks, each block twice as wide with a double stack of "
              "thumbnails; its two labels sit at the left and at the right end. Do not draw individual block numbers."},
    {"img": "n23-costmeter", "title": "เงินต่อ Epoch = ราคาต่อชั่วโมง × วินาทีต่อ Epoch ÷ 3600",
     "labels": ["ราคาต่อชั่วโมง", "วินาทีต่อ Epoch", "เงินต่อ Epoch", "เร็วขึ้น แต่ราคาต่อชั่วโมงสูงขึ้น"],
     "scene": "Left: a price tag on a server with a clock symbol (first label). Middle: a stopwatch over a progress bar of one "
              "training pass (second label). Right: a small stack of coins inside a dashed frame (third label). Multiplication "
              "and division signs between the three objects follow the title. Bottom: a balance scale; on one pan a faster "
              "stopwatch, on the other a taller price tag, with the fourth label under the scale. No numbers except in the title."},
    {"img": "n24-when", "title": "ควรใช้หลาย GPU เมื่อไร",
     "labels": ["งานใหญ่ เทรนนาน เวลาสำคัญกว่าเงินเล็กน้อย", "ราคาเครื่อง N ใบ ไม่เกิน N เท่า",
                "ทางเชื่อมดี: NVLink หรือ PCIe switch เดียวกัน", "ใช้หลาย GPU", "งานเล็กหรือเน้นประหยัด", "ใช้ 1 GPU"],
     "scene": "A clean decision diagram. Left column: three condition cards stacked vertically, each with a green check icon and "
              "an icon (a long timeline, a plain blank price tag with no symbol or letter on it, a short direct cable between two cards); arrows from all three converge "
              "to a large green result card on the right showing two graphics cards (label: use multiple GPUs). Below, separated "
              "by a thin line, one condition card with a small coin icon and an arrow to a blue result card with one graphics card "
              "(label: use one GPU). No currency symbols anywhere."},
    {"img": "n25-before", "title": "ก่อนเริ่ม LAB เตรียม 4 อย่าง",
     "labels": ["1 ทำ LAB 0 เตรียม key ให้ครบ", "2 เปิด Claude Code ที่โฟลเดอร์ของบท", "3 โฟลเดอร์ code เริ่มจากว่าง",
                "4 เงินเดินตั้งแต่เช่าเครื่องจนกว่าจะลบ"],
     "scene": "Four tidy panels in a 2 x 2 grid on a desk-like background, each with a numbered circle badge and its label: "
              "panel 1 a key ring with three keys and a locked file; panel 2 a laptop with a terminal window and a folder icon; "
              "panel 3 an empty open folder; panel 4 a server with a running taxi-style meter and coins, plus a trash can."},
    {"img": "n26-step1", "title": "AI เลือกและเช่าเครื่องที่มี GPU 2 ใบ",
     "labels": ["รายการเครื่องเช่าในตลาด", "RTX 3090 2 ใบในเครื่องเดียว", "เลือกเครื่องที่ถูกที่สุด", "ป้าย vapp-lab4",
                "ตรวจทางเชื่อมระหว่าง GPU"],
     "scene": "Left: a marketplace list of several server offer cards (no prices, only icons), a small white-and-teal robot "
              "(the AI) pointing a magnifier at them. One card is highlighted and pulled out with a check mark: it shows one "
              "server with two graphics cards inside (labels next to it: two cards in one machine, choose the cheapest). Right: "
              "the rented server with a tag hanging on it (label vapp-lab4) and a zoom bubble showing the data path between the "
              "two cards (label: check the link between GPUs)."},
    {"img": "n27-step2", "title": "AI ดาวน์โหลด Dataset แล้วทำภาพตัวอย่างจาก label จริง",
     "labels": ["Roboflow", "hard-hat-workers", "ROBOFLOW_API_KEY", "ไม่ทิ้ง key บนเครื่องเช่า", "show_samples.py",
                "dataset_samples.jpg"],
     "scene": "Left: a cloud labelled Roboflow with a stack of construction-site photos (dataset name label) flowing by an arrow "
              "into a rented server. A key icon with the key-name label passes into the server through a thin pipe and a shield "
              "icon shows the no-key-left label. Right: a script file icon (show_samples.py) producing a grid of eight small "
              "photos of workers with green and red boxes around heads (file name label under the grid)."},
    {"img": "n28-step3", "title": "สคริปต์เดียว ลองรันสั้นก่อน แล้ววัดเส้นฐาน 1 GPU",
     "labels": ["bench.py", "1 ลองรันสั้น ทั้ง 1 และ 2 GPU", "2 รันจริงด้วย GPU 1 ใบ", "3 บันทึกผลเป็นไฟล์ JSON", "วินาทีต่อ Epoch"],
     "scene": "A left-to-right flow of three numbered stations starting from a script file icon (bench.py). Station 1: a short "
              "test lap with a small flag and two tiny GPU icons. Station 2: one graphics card glowing on a long running track with "
              "a big stopwatch (label: seconds per epoch next to the stopwatch). Station 3: a JSON document icon receiving the "
              "result. Numbers appear only inside the three circle badges and in the labels exactly as given."},
    {"img": "n29-step4", "title": "สคริปต์เดิม ค่าเดิม เปลี่ยนแค่จำนวน GPU",
     "labels": ["bench.py เดิม", "ค่าเดิมทุกอย่าง", "GPU 0", "GPU 1", "ถ้าแก้สคริปต์ ต้องรัน 1 GPU ใหม่"],
     "scene": "Center: the same script file icon (bench.py) with a padlocked settings panel beside it (label: same settings). "
              "Right: one server with two graphics cards both glowing, each labelled GPU 0 and GPU 1, connected under the server "
              "by a cable through the CPU. Bottom: a small warning card with a circular arrow and the last label."},
    {"img": "n30-step5", "title": "ผลดิบและราคาตลาด เข้าสคริปต์เดียว ได้ตัวเลขและกราฟ",
     "labels": ["ราคาตลาด 1 ใบ และ 2 ใบ", "results/raw", "report.py", "metrics.json", "กราฟ 4 รูป"],
     "scene": "A funnel diagram. Top left: price tags from a marketplace (first label). Top right: a folder of raw result files "
              "(results/raw). Both flow down into a gear-shaped script (report.py). Out of it come a JSON document (metrics.json) "
              "and a fan of four small chart cards: a bar chart, a line chart, a bar chart with coins, a stacked bar chart."},
    {"img": "n31-step6", "title": "ลบเครื่อง ตรวจว่าไม่มีเครื่องค้าง แล้วอ่านยอดเงิน",
     "labels": ["ลบ vapp-lab4", "ไม่มีเครื่องค้างในบัญชี", "ไม่แตะเครื่องป้ายอื่น", "ยอด GPU · disk · รับส่งข้อมูล"],
     "scene": "Left: the robot moves a server tagged vapp-lab4 into a large trash can. Middle: an account dashboard window with an "
              "empty slot and a green check (second label); next to it two other servers with different blank tags and a "
              "do-not-touch hand sign (third label). Right: a receipt with three rows of icons (a GPU chip, a disk, two arrows "
              "up and down) and the last label; no amounts on the receipt."},
    {"img": "n32-step7", "title": "AI อ่านงานทั้ง LAB แล้วเขียนเป็นสกิล",
     "labels": ["PROMPTS.md", "code", "results", "SKILL.md", "scripts", ".claude/skills/multigpu-speedup"],
     "scene": "Left: three input items in a column, a document (PROMPTS.md), a folder of code files (code), a folder with charts "
              "(results). Arrows lead to the robot in the middle who is writing. Right: a new skill package box containing a "
              "document (SKILL.md) and a folder (scripts). An arrow carries the box into a cabinet drawer labelled with the "
              "install path."},
    {"img": "n33-step8", "title": "พรอมต์เดียว AI ทำทั้ง LAB ด้วยสกิล",
     "labels": ["1 เช่าเครื่อง", "2 เตรียม Dataset", "3 เทรน 1 และ 2 GPU", "4 ทำรายงาน", "5 ลบเครื่อง", "vapp-lab4-skill",
                "results/skill_v0_run"],
     "scene": "Top left: one single prompt card going into the robot. From the robot a continuous conveyor runs left to right "
              "through five numbered stations (icons: server with tag vapp-lab4-skill, photo stack, two graphics cards with "
              "stopwatch, chart document, trash can). The conveyor ends at a folder labelled results/skill_v0_run. A person sits "
              "relaxed at the side with a cup."},
    {"img": "n34-lessons", "title": "บทเรียนของ LAB 4",
     "labels": ["1 วัดจริง ไม่เดา", "2 การ Sync คือเพดานของ Speedup", "3 ดูทางเชื่อมก่อนเช่า", "4 เร็วขึ้นไม่ได้แปลว่าถูกลง",
                "5 เงินเดินตลอดเวลาที่เครื่องเปิด", "6 สกิลทำซ้ำได้ในคำสั่งเดียว"],
     "scene": "Six panels in a 3 x 2 grid, each with a numbered circle badge, one clear icon and its label: 1 a stopwatch over "
              "a clipboard; 2 two graphics cards with a narrow bottleneck between them; 3 a magnifier over a cable between two "
              "cards; 4 a fast running figure next to a stack of coins; 5 a taxi-style meter on a server; 6 a document with a "
              "gear and a single click."},
]

PHOTOS2 = [
    {"img": "p21-site", "scene": "A real construction site in daylight: several workers wearing yellow and white hard hats walk "
                                 "between scaffolding, one worker without a hard hat in the middle distance; a safety camera on a "
                                 "pole in the foreground right. Mood: workplace safety, why we detect hard hats."},
    {"img": "p22-rent", "scene": "A person in a quiet lab at night scrolling a laptop whose screen shows an abstract blurred list of "
                                 "cards; in the background a server rack with blue lights. Mood: choosing a machine to rent."},
    {"img": "p23-data", "scene": "A large monitor shows a blurred grid of small photos of construction workers with thin green and "
                                 "red rectangles around heads (abstract, unreadable); a person points at it. Mood: checking data."},
    {"img": "p24-onegpu", "scene": "Close-up inside an open server: two large graphics cards side by side, only the right card has "
                                   "its fans and lights on, the left card is dark and still. A stopwatch rests on top of the case."},
    {"img": "p25-twogpu", "scene": "Close-up inside an open server: two large graphics cards side by side, both glowing with teal "
                                   "lights and spinning fans, motion blur on fans; a stopwatch rests on top of the case."},
    {"img": "p26-report", "scene": "A desk with printed bar charts (abstract shapes only, no text), a calculator, a few coins and a "
                                   "laptop with a blurred chart on screen; a person's hands compare two printed charts."},
    {"img": "p27-delete", "scene": "A person's hand clicking a laptop trackpad decisively; behind, slightly out of focus, a server "
                                   "rack where the lights of one unit are going dark. Mood: shutting down and stopping the bill."},
    {"img": "p28-skill", "scene": "A person writes a neat procedure in a notebook beside a laptop and a small folder of files on a "
                                  "wooden desk; warm lamp light. Mood: saving a working method so it can be repeated."},
    {"img": "p29-auto", "scene": "A person leans back with a cup of coffee while a laptop on the desk runs a job on its own (blurred "
                                 "progress bars); server rack lights glow in the background. Mood: one command does the whole job."},
    {"img": "p31-recipe", "scene": "A tidy shelf with labelled-looking but blank binders and one open binder on a desk showing neat "
                                   "blank checklists (no readable text), a laptop beside it with a blurred screen. Mood: keeping "
                                   "a proven method for the next time."},
    {"img": "p30-summary", "scene": "On a dark desk: two graphics cards lying side by side, a stopwatch, a small stack of coins and a "
                                    "yellow hard hat, dramatic side light. Mood: weighing time against money."},
]

FIGURE2 = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

Style: a clean, modern, flat explanatory figure like one from a well-made university textbook or a technical report.
White or very light background, generous white space, a restrained palette (navy #12305e, teal #0f8f8c, orange #e87f1c,
soft grey), simple geometric icons with thin outlines, rounded cards, numbered circle badges where order matters.
Not childish: no cartoon faces except the small white-and-teal robot that stands for the AI where the scene mentions it.
Canvas: landscape 16:9 (about 1600 x 900).

Title text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above.
- When a label starts with a number followed by a space (for example "3 gate"), draw that number ONLY inside a circle badge and write the rest of the label next to it. Never show the same number twice.
- Text must be large, bold and easy to read from the back of a classroom. File names and paths use a monospace font.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "--v2":
    out = os.path.abspath(sys.argv[1]).replace("\\", "/")
    os.makedirs(out, exist_ok=True)
    for f in FIGS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(FIGURE2.format(
            out=out, img=f["img"], title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
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
