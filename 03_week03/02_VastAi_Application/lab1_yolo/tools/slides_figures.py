#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์บทนี้ (คัดลอกไฟล์นี้เป็น <บท>/tools/slides_figures.py แล้วแก้ FIGS และ PHOTOS)

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

SETTING = ('construction-site safety work in Thailand: a building site with cranes and scaffolding, workers in yellow hardhats '
           'and orange safety vests, a small site office with a laptop, and one rented GPU server (RTX 4090) in a cloud data center')   # ฉากของบท

FIGS = [
    {"img": "n01-label", "title": "label 1 บรรทัด = กรอบ 1 กรอบ",
     "labels": ["5 0.52 0.48 0.21 0.67", "คลาส", "x_กลาง y_กลาง", "กว้าง", "สูง", "Person", "ค่า 0–1 เทียบกับขนาดภาพ"],
     "scene": "Left: a square construction-site photo frame with one cartoon worker inside a colored bounding box; a dot marks the "
              "center of the box, a horizontal arrow shows the box width and a vertical arrow shows the box height; the tag 'Person' "
              "sits on top of the box. Right: a paper sheet like a .txt file showing one monospace line '5 0.52 0.48 0.21 0.67'; "
              "under its parts, brackets point to the small labels 'คลาส' (under 5), 'x_กลาง y_กลาง' (under 0.52 0.48), "
              "'กว้าง' (under 0.21) and 'สูง' (under 0.67). A ribbon at the bottom with 'ค่า 0–1 เทียบกับขนาดภาพ'.",
     "steps": ["ไฟล์ `.txt` 1 ไฟล์ต่อภาพ มี **บรรทัดละ 1 กรอบ**",
               "รูปแบบ `คลาส x_กลาง y_กลาง กว้าง สูง` · ค่า 0–1 เทียบกับขนาดภาพ",
               "`5 0.52 0.48 0.21 0.67` = คลาสหมายเลข 5 (**Person**) จุดกลางกรอบอยู่กลางภาพ",
               "กรอบกว้าง 21% และสูง 67% ของภาพ · ภาพ 1 ภาพมีได้หลายสิบกรอบ"]},
    {"img": "n02-experiment", "title": "การทดลอง: เทียบก่อนเทรนกับหลังเทรน บน Test Set เดียวกัน",
     "labels": ["ก่อนเทรน: yolo11s (COCO)", "หลังเทรน: เทรนต่อ 50 Epoch", "Test Set 82 ภาพ", "สคริปต์วัดผลเดียวกัน",
                "mAP50 · mAP50-95 · เวลาต่อรูป", "RTX 4090"],
     "scene": "Two robot models side by side at the top: left a plain robot labelled 'ก่อนเทรน: yolo11s (COCO)', right the same robot "
              "wearing a small yellow hardhat labelled 'หลังเทรน: เทรนต่อ 50 Epoch'. Both send arrows down into ONE shared exam desk "
              "in the middle with a stack of construction-site photos labelled 'Test Set 82 ภาพ' and a single clipboard script "
              "labelled 'สคริปต์วัดผลเดียวกัน'. Below the desk, one scoreboard card labelled 'mAP50 · mAP50-95 · เวลาต่อรูป' "
              "(no numbers on it). A small GPU card icon labelled 'RTX 4090' in a corner.",
     "steps": ["**ก่อนเทรน** = `yolo11s` ที่เทรนบน COCO",
               "**หลังเทรน** = โมเดลเดิมเทรนต่อ 50 Epoch (ภาพ 640 · batch 32 · seed 0)",
               "วัดด้วย **Test Set 82 ภาพ** ด้วยสคริปต์เดียวกันทั้งสองโมเดล",
               "ตัวชี้วัด: mAP50 · mAP50-95 · AP50 รายคลาส · เวลาต่อรูป",
               "เครื่อง RTX 4090 1 ใบ · เพดาน $0.70 ต่อชั่วโมง (ได้จริง $0.408)"]},
    {"img": "n03-rent", "title": "ขั้นที่ 1: เช่าเครื่องตามเกณฑ์ แล้วตรวจว่าเห็น GPU จริง",
     "labels": ["1 ค้นหาตามเกณฑ์", "2 เช่าเครื่องที่ถูกที่สุด", "3 รอจนเครื่องพร้อม", "4 เข้าไปเห็น GPU จริง",
                "เกิน 10 นาที: ลบแล้วเช่าใหม่", "RTX 4090 · ไม่เกิน $0.70/ชม.", "vapp-lab1"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a person at a laptop filtering a list of GPU offers "
              "with a funnel, tag 'RTX 4090 · ไม่เกิน $0.70/ชม.'; (2) choosing the cheapest server card and putting a name tag "
              "'vapp-lab1' on it; (3) a server rack with an hourglass and a loading bar; (4) the small robot looking at a green "
              "glowing GPU card on a terminal screen with a check mark. A red detour arrow from panel 3 goes to a trash bin and back "
              "to panel 2, labelled 'เกิน 10 นาที: ลบแล้วเช่าใหม่'.",
     "steps": ["**ค้นหา** RTX 4090 1 ใบ ราคารวมไม่เกิน $0.70 ต่อชั่วโมง เครื่อง verified เน็ต 500 Mbps ขึ้นไป CPU 12 cores ขึ้นไป",
               "**เช่าเครื่องที่ถูกที่สุด** ตั้งป้าย `vapp-lab1` · image PyTorch 2.8 กับ CUDA 12.8 · disk 40 GB · เปิดพอร์ต 8080",
               "**รอจนเครื่องพร้อม** · ถ้าเกิน 10 นาทียังไม่พร้อม ให้ลบแล้วเช่าเครื่องอื่น",
               "**เข้าไปเห็น GPU จริง** แล้วสรุปเป็นตาราง · ตั้งแต่ขั้นนี้เงินเริ่มเดิน"]},
    {"img": "n04-dataset", "title": "ขั้นที่ 2: Dataset ลงเครื่องเช่าโดยตรง กลับมาเฉพาะภาพตัวอย่าง",
     "labels": ["1 ติดตั้ง ultralytics · roboflow", "2 ดาวน์โหลดจาก Roboflow", "3 key ไม่ทิ้งไว้บนเครื่องเช่า",
                "4 ภาพตัวอย่าง 8 รูป", "เครื่องเช่า", "เครื่องของเรา", "dataset_samples.jpg"],
     "scene": "Three places left to right: a cloud labelled with a dataset box icon (Roboflow) on the left; in the middle a big "
              "server rack labelled 'เครื่องเช่า' with a toolbox (step 1) and a fat download arrow coming from the cloud (step 2); "
              "a key icon crossed out next to the server (step 3). On the right a laptop on a desk labelled 'เครื่องของเรา' "
              "receiving only one small picture card showing a 2x4 grid of photos with colored boxes, the card labelled "
              "'dataset_samples.jpg' (step 4). The fat arrow does not reach the laptop; only a thin arrow carries the picture card.",
     "steps": ["**ติดตั้ง** ultralytics และ roboflow บนเครื่องเช่า",
               "**ดาวน์โหลด** construction-site-safety รุ่น 28 จาก Roboflow ในรูปแบบ YOLO ลงเครื่องเช่าโดยตรง",
               "ใช้ `ROBOFLOW_API_KEY` จาก `.env` · **ห้ามแสดงค่า key และห้ามทิ้ง key ไว้บนเครื่องเช่า**",
               "ทำ **ภาพตัวอย่าง 8 รูป** จาก Training Set พร้อมกรอบเฉลย แล้วเก็บกลับมาที่ `results/dataset_samples.jpg`"]},
    {"img": "n05-eval", "title": "ขั้นที่ 4: วัด 2 โมเดลด้วยวิธีเดียวกัน แล้วเก็บผลกลับมา",
     "labels": ["ก่อนเทรน (COCO)", "หลังเทรน (best.pt)", "1 eval.py วิธีเดียวกัน", "2 metrics.json", "3 กราฟและภาพเทียบ",
                "4 รูปตัวอย่าง 6 รูป", "Test Set"],
     "scene": "Top left: two robot models labelled 'ก่อนเทรน (COCO)' and 'หลังเทรน (best.pt)' (the second wears a yellow "
              "hardhat). Both feed into one machine/funnel labelled '1 eval.py วิธีเดียวกัน' that takes a photo stack labelled "
              "'Test Set'. Out of the machine come three outputs to the right, each a card: '2 metrics.json' (a document icon "
              "with curly braces), '3 กราฟและภาพเทียบ' (a small bar chart and a before/after photo pair), and "
              "'4 รูปตัวอย่าง 6 รูป' (six small thumbnails, three with a red mark and three with a green mark). An arrow carries "
              "all cards to a folder on a laptop. No numbers on the charts.",
     "steps": ["**eval.py** วัดโมเดลก่อนเทรนกับหลังเทรน ด้วยวิธีเดียวกัน บน Test Set ที่ไม่ได้ใช้เทรน",
               "โมเดล COCO นับเฉพาะคลาสที่ตรงกัน: person เป็น Person · car, bus, truck เป็น vehicle · คลาสอื่นได้ 0",
               "บันทึกตัวเลขลง **metrics.json** · ทำภาพเทียบก่อน/หลัง 5 ภาพ · กราฟ AP50 รายคลาส · กราฟ loss และ mAP",
               "เลือก **รูปตัวอย่าง 6 รูป** ตามผลของโมเดลหลังเทรน: 3 รูปที่พบคนไม่สวมหมวก 3 รูปที่ทุกคนสวมหมวก",
               "เก็บผลทั้งหมดพร้อม `best.pt` กลับมาที่ `lab1_yolo/results`"]},
    {"img": "n06-api", "title": "ขั้นที่ 5: สัญญา API ระหว่าง AI server กับเว็บ",
     "labels": ["/health · ไม่ต้องใช้ key", "/v1/detect · ช่อง file", "Authorization: Bearer", "ไม่มี key → 401",
                "detections", "confidence ≥ 0.35", "พอร์ต 8080"],
     "scene": "Right: a server rack with a robot inside, a sign 'พอร์ต 8080'. Two doors on the server: a green open door labelled "
              "'/health · ไม่ต้องใช้ key' and a blue door labelled '/v1/detect · ช่อง file' guarded by a key lock with the tag "
              "'Authorization: Bearer'. Left: a web browser window sending a photo envelope with a key to the blue door. A second "
              "envelope without a key bounces off with a red stamp 'ไม่มี key → 401'. From the blue door a JSON card returns to the "
              "browser, the card titled 'detections' showing small boxes, with a filter tag 'confidence ≥ 0.35'.",
     "steps": ["**/health** ตอบว่าพร้อมไหม ชื่อโมเดล `ppe-yolo11s` และรายชื่อคลาส โดยไม่ต้องใช้ key",
               "**/v1/detect** รับรูป 1 รูปในช่อง `file` พร้อม key แบบ `Authorization: Bearer`",
               "ไม่มี key หรือ key ผิด ตอบ **401**",
               "คำตอบเป็น JSON: `model` `width` `height` `inference_ms` `detections` (class · confidence · box x1 y1 x2 y2)",
               "ส่งเฉพาะกรอบที่ confidence **0.35 ขึ้นไป** · server เปิดที่พอร์ต 8080"]},
]

PHOTOS = [
    {"img": "s01-site", "scene": "A real construction site in Thailand at golden hour: several workers in yellow hardhats and orange "
                                 "safety vests work on concrete and scaffolding on the right side; one site supervisor holding a "
                                 "tablet looks at them. Cranes in the soft background."},
    {"img": "s02-gpu", "setting": "a cloud data center where GPU servers are rented by the hour", "scene": "Inside a modern cloud data center: rows of server racks with small blue and green status lights, "
                                "one open rack on the right showing a large graphics card server; cool blue light, depth into the aisle."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, warm cream background, decorations of the setting, dark-brown rounded title banner, thick outlines, rounded cards,
numbered circle badges, palette of teal, orange, green, red and brown, bold rounded Thai lettering):
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

# ===== รอบที่ 2: ภาพอธิบายแบบตำรา (n2x-*) และภาพถ่ายสมจริง (p2x-*)
#   python tools/slides_figures.py --pass2 <โฟลเดอร์ปลายทาง นอกรีโป>
ILLUS2 = [
    {"img": "n21-roadmap", "ratio": "16:9", "title": "LAB 1 มี 4 ส่วน",
     "labels": ["1 ภาคพื้นฐาน", "Dataset · โมเดล · ทฤษฎี", "2 งานหลัก ขั้นที่ 1–8", "เช่า GPU → เทรน → เว็บ → ลบเครื่อง",
                "3 สกิล v0 ขั้นที่ 9–10", "ทำซ้ำในคำสั่งเดียว", "4 สรุป", "ผลรวม · ข้อจำกัด"],
     "scene": "A horizontal road from left to right with four stations, each a rounded signpost with a numbered circle badge (1 to 4) "
              "and a small icon above it: station 1 an open book with a photo of a construction site and a small box diagram; "
              "station 2 a GPU server, a learning curve and a browser window in a row; station 3 a folder with a document and a "
              "repeat arrow; station 4 a flag with a small bar chart. Under each badge the short label for that station, and "
              "under it the smaller sub-label: 'Dataset · โมเดล · ทฤษฎี' under station 1, 'เช่า GPU → เทรน → เว็บ → ลบเครื่อง' "
              "under station 2, 'ทำซ้ำในคำสั่งเดียว' under station 3, 'ผลรวม · ข้อจำกัด' under station 4. Station 2 is the widest."},
    {"img": "n24-setup", "ratio": "4:3", "title": "ก่อนเริ่ม LAB 1",
     "labels": ["1 ทำ LAB 0: key 3 ตัว", "2 Claude Code ที่โฟลเดอร์ 02_VastAi_Application", "3 container multi-account · สกิล vastai",
                "4 Docker Desktop สำหรับเว็บ", "5 โฟลเดอร์ code/ ยังไม่มี AI สร้างให้"],
     "scene": "One laptop in the center of a desk. Around it five items connected to the laptop by thin lines, each with a numbered "
              "circle badge: (1) three keys on a key ring; (2) the laptop screen itself showing a terminal window and a folder icon; "
              "(3) a container box shape with a small robot inside; (4) a second box shape with a small browser window on it; "
              "(5) an empty dashed folder outline with a small robot hand about to fill it. Each label sits next to its item."},
    {"img": "n26-key", "ratio": "16:9", "title": "ค่า key ต้องไม่ปรากฏในผลคำสั่ง",
     "labels": ["1 AI สั่งตรวจไฟล์ .env", "2 ค่า key ปรากฏในผลคำสั่ง", "3 สร้าง key ใหม่ที่ Roboflow ทันที", "ROBOFLOW_API_KEY"],
     "scene": "Three panels left to right connected by arrows. Panel 1: a small white-and-teal robot points at a document icon "
              "named '.env'. Panel 2: a dark terminal window where one line is highlighted in red; the line shows the word "
              "'ROBOFLOW_API_KEY' followed by a row of grey dots (the key value is NOT readable, only dots); a red warning triangle "
              "beside it. Panel 3: a person at a laptop replaces an old crossed-out key with a new shining key. Each panel has its "
              "numbered badge and label underneath."},
    {"img": "n27-train", "ratio": "16:9", "title": "ขั้นที่ 3: train.py เทรนบนเครื่องเช่า",
     "labels": ["1 AI เขียน train.py", "2 เริ่มจาก yolo11s (COCO)", "3 50 Epoch · ภาพ 640 · batch 32 · seed 0",
                "4 รายงานทุก 2 นาที: Epoch · mAP50", "เทรนต่อได้แม้การเชื่อมต่อหลุด", "เครื่องเช่า RTX 4090"],
     "scene": "Left: a laptop with a code file icon (badge 1). An arrow goes right to a large rented GPU server in a cloud (tag "
              "'เครื่องเช่า RTX 4090'). On the server: a small model block (badge 2) and a settings panel with sliders (badge 3, "
              "with its label). Above the server a rising learning curve that flattens (no axis numbers). From the server a dotted "
              "arrow back to the laptop carrying a small status card (badge 4). The connection line between laptop and server has a "
              "visible break, while the server keeps running with a green play symbol, tag 'เทรนต่อได้แม้การเชื่อมต่อหลุด'."},
    {"img": "n28-crash", "ratio": "16:9", "title": "รันครั้งแรกล้ม แล้ว AI แก้เอง",
     "labels": ["1 รันครั้งแรก หยุดหลัง Epoch 1", "2 สาเหตุ: อ่านค่า loss ผิดชนิด", "3 AI แก้โค้ดส่วนพิมพ์ความคืบหน้า",
                "4 เทรนใหม่จนครบ 50 Epoch"],
     "scene": "A loop of four stages drawn as a circular path with arrows: (1) a progress bar that stops very early with a red X; "
              "(2) a magnifying glass over a code line with a red underline; (3) the small robot holding a wrench fixing a code block; "
              "(4) a full green progress bar with a check mark. Each stage has its numbered badge and label next to it."},
    {"img": "n29-sitesafe", "ratio": "16:9", "title": "เว็บ SiteSafe ที่ AI ต้องสร้าง",
     "labels": ["1 หน้าแรก: อัปโหลด หรือกดรูปตัวอย่าง", "2 ป้ายผล ผ่าน / ไม่ผ่าน", "3 หน้าประวัติ · PostgreSQL",
                "4 key อยู่ฝั่ง server เท่านั้น", "AI server บน Vast.ai", "http://localhost:3401"],
     "scene": "A large browser window in front (address bar shows 'http://localhost:3401'). Inside it: on the left an upload box with "
              "an upward arrow and a grid of six small construction-site thumbnails (badge 1); on the right a photo of workers with "
              "colored rectangles and a red result badge (badge 2). Behind it to the right a second browser window with a simple "
              "table and a database cylinder icon (badge 3). Below the windows a server box with a padlock and a key (badge 4) "
              "connected by an arrow to a cloud on the far right labelled 'AI server บน Vast.ai'. No digits on any counter or table."},
    {"img": "n31-shutdown", "ratio": "4:3", "title": "ขั้นที่ 8: ปิดทุกอย่างของ LAB 1",
     "labels": ["1 ลบเครื่อง vapp-lab1", "2 ตรวจว่าไม่มีเครื่องค้าง", "3 ปิดเว็บ เก็บประวัติไว้",
                "4 สรุปบิลจริง: GPU · disk · รับส่งข้อมูล", "ห้ามแตะเครื่องป้ายอื่น", "best.pt อยู่บนเครื่องเราแล้ว"],
     "scene": "Four numbered steps in a 2x2 arrangement with arrows: (1) a server card with the tag 'vapp-lab1' going into a trash "
              "bin; (2) an empty list with a magnifying glass and a green check; (3) a browser window with a power symbol and a "
              "database cylinder kept safe; (4) a paper receipt with three lines of grey bars (no digits). Beside step 1 another "
              "server card with a different colored tag and a shield, label 'ห้ามแตะเครื่องป้ายอื่น'. In a corner a laptop with a "
              "small model file icon, label 'best.pt อยู่บนเครื่องเราแล้ว'."},
    {"img": "n32-skill", "ratio": "16:9", "title": "สกิล yolo-ppe-train",
     "labels": ["SKILL.md", "name · description", "ค่าที่ปรับได้", "ขั้นตอน", "เกณฑ์ตรวจผ่าน", "กติกาเรื่องเงิน: ลบเครื่องเสมอ",
                "scripts/", "train.py · eval.py · serve.py", "เรียกใช้สกิล vastai", ".claude/skills/yolo-ppe-train"],
     "scene": "One big open folder in the center. Left inside the folder: a document titled 'SKILL.md' with five short lines, each "
              "line is one of the labels 'name · description', 'ค่าที่ปรับได้', 'ขั้นตอน', 'เกณฑ์ตรวจผ่าน', "
              "'กติกาเรื่องเงิน: ลบเครื่องเสมอ', each with a small check icon. Right inside the folder: a sub-folder 'scripts/' with "
              "three code file icons and the label 'train.py · eval.py · serve.py'. An arrow from the folder to a second small "
              "folder icon labelled 'เรียกใช้สกิล vastai'. The folder sits on a shelf whose tag reads '.claude/skills/yolo-ppe-train'."},
    {"img": "n33-lessons", "ratio": "16:9", "title": "บทเรียนของ LAB 1",
     "labels": ["1 Fine-tuning ใช้ข้อมูลไม่มาก ได้ผลมาก", "2 ค่าเฉลี่ยสูง ไม่ได้แปลว่าดีทุกคลาส", "3 เงินเดินตลอดเวลาที่เครื่องเปิด",
                "4 ผู้ใช้รอเครือข่าย ไม่ใช่รอโมเดล", "5 AI ต้องรันจริงและแก้จนผ่าน", "6 สกิลทำให้ทำซ้ำได้"],
     "scene": "Six illustrated panels in two rows of three, each with a large clear icon and its numbered badge and label below: "
              "(1) a small stack of photos turning into a big upward arrow; (2) NO bar chart and NO bars: a report card with one big "
              "green check badge at the top, and below it a list of five plain grey rows where exactly one row carries a small red "
              "warning triangle;(3) a server with a running taxi-style meter beside it; (4) a long cable from a laptop to a far "
              "away server with an hourglass in the middle, and a tiny chip with a lightning bolt; (5) the small robot fixing a code "
              "block with a wrench next to a green check; (6) a folder with a circular repeat arrow."},
]

PHOTOS2 = [
    {"img": "p21-monitor", "scene": "A site office at a construction site in the evening: a fictional Thai site supervisor wearing a "
                                    "yellow hardhat sits in front of a wall of many small CCTV monitors that show blurred views of "
                                    "the site, rubbing tired eyes with one hand."},
    {"img": "p22-study", "scene": "A site engineer at a desk in a site office studying photographs of workers on a large monitor (the "
                                  "screen content is blurred), rolled building plans and a hardhat on the desk, a window shows the "
                                  "construction site outside."},
    {"img": "p23-rack", "setting": "a cloud data center where GPU servers are rented by the hour",
     "scene": "A technician's hands sliding a heavy GPU server into a rack, blue and green status lights, cool light, depth of field."},
    {"img": "p24-photos", "scene": "A wooden table covered with many printed photographs of construction sites; on some photos a "
                                   "colored marker has drawn rectangles around workers' heads; a hand holds one more photo; no text."},
    {"img": "p25-gpu", "setting": "a cloud data center where GPU servers are rented by the hour",
     "scene": "Close-up of a large graphics card inside an open server chassis, cooling fans, small glowing status lights, warm and "
              "blue light, shallow depth of field."},
    {"img": "p26-compare", "scene": "Two fictional Thai engineers in a site office comparing two monitors side by side; one points at "
                                    "the right screen; the screens show blurred photos with colored rectangles."},
    {"img": "p27-cables", "setting": "a cloud data center where GPU servers are rented by the hour",
     "scene": "A network switch with many glowing ethernet cables plugged in, in a dim server room, light trails of blue and orange."},
    {"img": "p28-tablet", "scene": "A fictional Thai site supervisor in a hardhat and safety vest stands on a construction site holding "
                                   "a tablet; the tablet screen shows a blurred photo of workers with colored rectangles."},
    {"img": "p29-phone", "scene": "A worker at a construction site photographs two colleagues in yellow hardhats with a smartphone; "
                                  "scaffolding behind them; daytime."},
    {"img": "p30-off", "scene": "End of the day in a dim site office: a person closes a laptop; a desk lamp is the only light; the "
                                "construction site is dark outside the window."},
    {"img": "p31-binder", "scene": "A desk with an open procedure binder with colored tabs, a laptop beside it and a cup of coffee, soft "
                                   "morning light; the pages show only grey abstract lines, no readable text."},
    {"img": "p32-sunset", "scene": "A group of construction workers, all wearing yellow hardhats and orange safety vests, walk together "
                                   "across a construction site at sunset, seen from behind, cranes in the background."},
]

ILLUS = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

Style: a clean explanatory figure from a well-made modern textbook. Flat vector illustration, white to very light warm-grey
background, generous white space, thin dark-navy outlines, rounded shapes, soft shadows only. Palette: navy #12305e, teal #0f8f8c,
orange #e87f1c, green #15803d, red #c92a2a, light greys. People are simple flat adults (not chibi, not childish), a small
white-and-teal robot represents the AI. No decorative clutter, no confetti, no sparkles. Numbered circle badges in navy with white
numbers mark the order.

Canvas: landscape {ratio}. Setting: {setting}.

Title at the top (exact, bold, dark navy, no banner decorations): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above. Screens, tables and papers inside the picture show only grey lines, no readable text and no digits.
- When a label starts with a number (for example "3 gate"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Text must be large, bold and easy to read from the back of a classroom. Use a clean Thai sans-serif font. Code-like labels (file names, paths, URLs) use a monospace font.
- Fictional characters only.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

if __name__ == "__main__" and sys.argv[1:2] == ["--pass2"]:
    out = os.path.abspath(sys.argv[2]).replace("\\", "/")
    os.makedirs(out, exist_ok=True)
    for f in ILLUS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(ILLUS.format(
            out=out, img=f["img"], ratio=f["ratio"], setting=SETTING, title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
    for f in PHOTOS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=f.get("setting", SETTING), scene=f["scene"]))
    print("%d พรอมต์ -> %s" % (len(ILLUS2) + len(PHOTOS2), out))
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
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=f.get("setting", SETTING), scene=f["scene"]))
    print("%d พรอมต์ -> %s" % (len(FIGS) + len(PHOTOS), out))
