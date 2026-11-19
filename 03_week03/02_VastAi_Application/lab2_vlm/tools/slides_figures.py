#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ LAB 2 · Fine-tune VLM อ่านใบเสร็จ

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

SETTING = ('a small Indonesian cafe and shop: the owner keeps a big pile of paper receipts (Rupiah, Rp) and an expense notebook '
           'web app on a laptop at the shop counter; the AI model runs on one rented cloud GPU server (RTX 4090) far away, '
           'connected by an internet cable or cloud')

FIGS = [
    {"img": "n01-label-rules", "title": "กติกาของงานที่โมเดลสำเร็จรูปยังไม่รู้",
     "labels": ["1 price = ยอดของบรรทัด", "2 ไม่พิมพ์จำนวน = qty 1", "3 ไม่มีบนใบ = null", "4 total ไม่ใช่ CASH",
                "TOTAL 21,000", "CASH 50,000", "CHANGE 29,000"],
     "scene": "One large printed paper receipt stands in the center. On its lower part three printed lines are visible: "
              "TOTAL 21,000, CASH 50,000 and CHANGE 29,000; the TOTAL line is circled in green and the CASH and CHANGE lines are "
              "crossed out lightly in red. Four numbered callout cards point at the receipt, two on the left and two on the right: "
              "(1) points at an item line, (2) points at an item line without a quantity, (3) points at an empty space where a "
              "tax line would be, (4) points at the TOTAL line. The small robot holds a magnifying glass next to the receipt.",
     "steps": ["**price** คือยอดของบรรทัดนั้น ไม่ใช่ราคาต่อชิ้น · เป็นจำนวนเต็ม (\"12,000\" → 12000)",
               "ใบไม่พิมพ์จำนวน = **qty 1** · รายการย่อย เช่น topping นับเป็นอีกบรรทัด",
               "ใบไม่พิมพ์ subtotal หรือ tax = **null**",
               "**total** คือยอดที่ต้องจ่าย ใบ `train_234` คือ 21,000 ไม่ใช่ CASH 50,000 หรือ CHANGE 29,000",
               "กติกาเหล่านี้คือสิ่งที่โมเดลสำเร็จรูปยังไม่รู้ และเป็นสิ่งที่ LAB นี้จะสอนเพิ่ม"]},
    {"img": "n02-data-split", "title": "ข้อมูล 3 ชุด ทำหน้าที่ต่างกัน",
     "labels": ["1 Training Set 800 ใบ", "2 Validation Set 100 ใบ", "3 Test Set 100 ใบ",
                "ปรับน้ำหนักของ LoRA", "ดู validation loss", "ตัดสินผลครั้งเดียวตอนจบ"],
     "scene": "Three stacks of paper receipts side by side, left to right, each with a numbered badge: (1) a tall stack feeding "
              "into a training machine with gears; (2) a small stack next to a line chart that goes down; (3) a small stack "
              "inside a locked glass box, opened only at the end by a person holding a judge's clipboard. Each stack has its "
              "short description label underneath.",
     "steps": ["**Training Set** 800 ใบ ใช้ปรับน้ำหนักของ LoRA",
               "**Validation Set** 100 ใบ ใช้ดู validation loss ก่อนเทรนและหลังทุก Epoch",
               "**Test Set** 100 ใบ ใช้ตัดสินผล Base เทียบ Fine-tuned ครั้งเดียวตอนจบ",
               "ถ้าวัดผลด้วยใบที่โมเดลเคยเห็น คะแนนจะสูงเกินจริง · validation loss ที่ **กลับขึ้น** คือสัญญาณ Overfitting"]},
    {"img": "n03-ab-setup", "title": "เทียบ Base กับ Fine-tuned อย่างยุติธรรม",
     "labels": ["Base", "Fine-tuned = Base + LoRA", "1 Prompt เดียวกัน", "2 ภาพเดียวกัน", "3 server เดียวกัน",
                "4 Test Set 100 ใบ"],
     "scene": "Two identical robots stand side by side on a stage, the left one labelled Base, the right one wearing a small "
              "extra plug-in module and labelled Fine-tuned = Base + LoRA. Both stand on the same single server box. In front "
              "of them, the same receipt photo and the same instruction card are shown to both. Four numbered cards in a row "
              "at the bottom name what is kept the same.",
     "steps": ["**Base** = Qwen3-VL-2B-Instruct ตามที่โหลดมา · **Fine-tuned** = โมเดลเดิม + LoRA Adapter",
               "ใช้ **Prompt เดียวกัน ภาพเดียวกัน server เดียวกัน** ความต่างจึงมาจาก LoRA เท่านั้น",
               "วัดบน **Test Set 100 ใบ** ส่งทีละใบ temperature 0",
               "ตัวชี้วัด: JSON อ่านได้ · ยอดรวมตรงทุกหลัก · Item F1 · วินาทีต่อใบ"]},
    {"img": "n04-step1-rent", "title": "ขั้นที่ 1: เช่าเครื่องแล้วทดสอบความเร็วก่อนใช้",
     "labels": ["1 ค้นหา RTX 4090", "2 เช่าเครื่องที่ถูกที่สุด", "3 ทดสอบโหลดจาก Hugging Face", "4 ช้ากว่า 20 MB/s = ลบ",
                "vapp-lab2"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a person at a laptop looks through a magnifying "
              "glass at a list of GPU cards; (2) the robot picks the cheapest GPU server box which gets a tag vapp-lab2; "
              "(3) a download progress bar with a speedometer from a cloud with a hugging-face emoji icon (no text) to the "
              "server; (4) a slow speedometer with a snail and a trash can, the slow server going into the trash.",
     "steps": ["**ค้นหา** RTX 4090 1 ใบ ราคารวมไม่เกิน $0.80 ต่อชั่วโมง เครื่อง verified ที่ค่าดาวน์โหลดต่อ GB ถูก",
               "**เช่า** เครื่องที่ถูกที่สุด ตั้งป้ายว่า `vapp-lab2` · image PyTorch CUDA 12.8 · disk 60 GB · พอร์ต 8000",
               "**ทดสอบ** โหลดไฟล์จาก Hugging Face ก่อนใช้จริง",
               "ช้ากว่า **20 MB/s** หรือรอเกิน 10 นาที = ลบแล้วเช่าเครื่องอื่น"]},
    {"img": "n05-step5-eval", "title": "ขั้นที่ 5: วัดผลทีละใบด้วยโปรแกรม",
     "labels": ["1 ส่ง Test Set ทีละใบ", "2 ตอบด้วยสองโมเดล", "receipt-base", "receipt-ft", "3 เทียบกับเฉลย", "4 metrics.json"],
     "scene": "A pipeline left to right: (1) a stack of receipts feeding one receipt at a time into a server box; (2) the "
              "server box has two output slots labelled receipt-base and receipt-ft, each producing a JSON card; (3) a "
              "scoring desk where the robot compares each JSON card with an answer-key card using green check marks and red "
              "crosses; (4) a document icon labelled metrics.json next to a small bar chart.",
     "steps": ["ส่ง **Test Set 100 ใบ** ให้ `receipt-base` และ `receipt-ft` ทีละใบ ด้วยข้อความสั่งเดียวกับตอนเทรน temperature 0",
               "ให้คะแนนด้วยโปรแกรม: **JSON อ่านได้** · **ยอดรวมตรงทุกหลัก** · **Item F1** · วินาทีต่อใบ",
               "รายการถูกเมื่อ **ชื่อและราคา** ตรงเฉลย (เทียบชื่อแบบไม่สนตัวพิมพ์ ช่องว่าง สัญลักษณ์)",
               "เก็บ `metrics.json` คำตอบรายใบ กราฟแท่ง และภาพตัวอย่าง 4 ใบ กลับมาที่ `lab2_vlm/results`"]},
    {"img": "n06-step7-destroy", "title": "ขั้นที่ 7: เงินเดินตลอดเวลาที่เครื่องเปิด",
     "labels": ["1 ตรวจผลใน results", "2 ลบเครื่อง vapp-lab2", "3 ปิดเว็บ เก็บรายจ่าย", "4 อ่านค่าใช้จ่ายจริง",
                "Adapter 34.9 MB"],
     "scene": "Four numbered panels left to right: (1) a person checks a folder with a checklist and a small file card "
              "labelled Adapter 34.9 MB safely on the local laptop; (2) the robot pushes the rented GPU server box into a big "
              "trash can, a running taxi-meter style coin counter above the server stops; (3) a laptop with the expense "
              "notebook web page being closed while a database cylinder stays safe; (4) a paper invoice with coin icons.",
     "steps": ["**ตรวจ** ว่าผลใน `lab2_vlm/results` ครบ: metrics.json กราฟ ภาพตัวอย่าง และ LoRA adapter",
               "**ลบ** เครื่องป้าย `vapp-lab2` แล้วตรวจว่าไม่มีเครื่องป้ายนี้ค้าง (ห้ามแตะเครื่องป้ายอื่น)",
               "**ปิดเว็บ** ใน `lab2_vlm/code/web` โดยเก็บรายจ่ายที่บันทึกไว้",
               "**อ่านค่าใช้จ่ายจริง**: อายุเครื่อง · ราคาต่อชั่วโมง · GPU · disk · รับส่งข้อมูล"]},
]

PHOTOS = [
    {"img": "s01-cover", "scene": "On the wooden counter of a small cafe in the evening, a smartphone held by a hand photographs a "
                                  "crumpled paper receipt; next to it lies a loose pile of many paper receipts and an open laptop. "
                                  "Mood: tedious paperwork about to be automated."},
    {"img": "s02-lab", "scene": "A rack of GPU servers in a dim data center aisle with small blue and green status lights and "
                                "neat cables, a person's hand plugging a network cable on the right side. Mood: rented compute "
                                "power that costs money every hour it runs.", "setting": "a cloud GPU data center"},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, light background, rounded title banner, thick outlines, rounded cards, numbered circle badges, same palette,
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
- People are fictional adults of Southeast Asian appearance; no real person's likeness.
- NO readable text anywhere: no letters, no numbers, no logos, no signs, no watermarks. Screens and papers must be blurred or abstract.
- Keep the left 45% of the frame calm and darker (out-of-focus background), main subject on the right side, because a title will be placed over the left side later.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

# ------------------------------------------------------------------ ภาพชุดที่ 2 (ภาพอธิบายแบบตำรา และภาพถ่ายฉาก)
# ILLUS2  ภาพอธิบายแบบแบน สะอาด 16:9 ป้ายข้อความอยู่ในภาพ (ตัวเลขในป้ายต้องตรงกับ README ทุกตัว ดู numbers.md)
# PHOTOS2 ภาพถ่ายสมจริงของสถานการณ์ ไม่มีตัวอักษรในภาพ ข้อความอยู่บนสไลด์
ILLUS2 = [
    {"img": "n21-plan", "title": "LAB 2 มี 3 ส่วน",
     "labels": ["1 พื้นฐาน", "2 LAB ขั้นที่ 1–7", "3 ขั้นที่ 8–9 และสรุป",
                "ใบเสร็จ · Dataset · โมเดล · ทฤษฎี", "เช่าเครื่อง → เทรน → วัดผล → เว็บ → ลบเครื่อง", "เก็บงานเป็นสกิล"],
     "scene": "A road seen from slightly above runs left to right through three stations, each marked with a numbered circle "
              "badge. Station 1: a desk with a paper receipt, a small dataset box and an open textbook. Station 2: a rented GPU "
              "server box connected to a laptop, with small icons along the road for training, a checklist and a trash can. "
              "Station 3: a folded recipe card with a gear, and a finish flag. Each station has its short description label below it."},
    {"img": "n22-metrics", "title": "ตัวชี้วัด 3 ตัวที่ใช้ตัดสินผล",
     "labels": ["1 JSON Validity", "2 Exact Match ของยอดรวม", "3 Item F1",
                "อ่านเป็น JSON ได้หรือไม่", "เฉลย 334,000", "ตอบ 334,011 = ผิด", "ชื่อและราคาตรงเฉลย"],
     "scene": "Three equal panels side by side, each with a numbered circle badge at the top. Panel 1: a JSON document card "
              "with curly braces passing through a parser gear and getting a green check. Panel 2: two receipt total lines "
              "stacked, the answer-key line 'เฉลย 334,000' in green and the model's line 'ตอบ 334,011 = ผิด' in red, the last "
              "digits of the wrong value circled in red. Panel 3: a list of item rows where each row has a name tag and a price "
              "tag, rows with both tags matching are ticked green, one row with a wrong name is crossed red."},
    {"img": "n23-lora-rules", "title": "LoRA สอนกติกาของงาน ไม่ได้สอนให้อ่านออก",
     "labels": ["อ่านตัวอักษรออกอยู่แล้ว", "LoRA Adapter",
                "1 ยอดรวมไม่ใช่ยอดเงินสด", "2 ราคาคือยอดของบรรทัด", "3 ชื่อต้องคัดลอกครบ", "4 บรรทัดเงินทอนไม่ใช่สินค้า"],
     "scene": "On the left, a large VLM model block with an eye icon looks at a printed paper receipt; a label says it can "
              "already read the letters. A small orange plug-in module labelled LoRA Adapter clicks onto the side of the model "
              "block. From the module, four rule cards fan out to the right, each with a numbered circle badge and a tiny icon: "
              "(1) a cash note crossed out next to a total line, (2) one item line highlighted across the whole row, (3) a "
              "full product name with no letters missing, (4) a change/coins line crossed out from an item list."},
    {"img": "n24-before", "title": "ก่อนเริ่ม LAB",
     "labels": ["1 ทำ LAB 0: key 3 ตัว", "2 เปิด Claude Code ที่ 02_VastAi_Application", "3 container multi-account + สกิล vastai",
                "4 ทำขั้นที่ 1 → 7 ในรอบเดียว", ".env"],
     "scene": "The folder name 02_VastAi_Application starts with the digit zero (0) and the digit two (2), written in a monospace font; it is not the letter o. Four numbered steps arranged left to right with arrows. (1) three keys on a key ring next to a small file card "
              "labelled .env with a closed padlock. (2) a laptop showing a terminal window opened inside a folder icon. "
              "(3) a container box with a small toolbox (the skill) attached. (4) a long arrow passing seven small dots, with a "
              "running coin meter above it."},
    {"img": "n25-step1-cost", "title": "ราคาต่อชั่วโมงไม่ใช่ต้นทุนทั้งหมด",
     "labels": ["1 ความเร็วที่โฆษณา ≠ ความเร็วไป Hugging Face", "2 เครื่องที่ลบทิ้งก็ถูกคิดเงิน", "3 ค่าดาวน์โหลดต่อ GB",
                "4 เงินเริ่มเดินตั้งแต่ขั้นนี้"],
     "scene": "A rented GPU server box in the center with a price tag hanging from it. Four numbered callouts around it: "
              "(1) a fast speedometer on the server's network port but a thin, slow pipe going to a cloud with a hugging-face "
              "emoji icon (no text); (2) a server in a trash can that still has a small coin falling out of it; (3) a download "
              "arrow with coins attached to it; (4) a running coin meter starting to tick."},
    {"img": "n26-step2-data", "title": "ขั้นที่ 2: จาก CORD-v2 สู่ข้อมูลที่พร้อมเทรน",
     "labels": ["1 โหลด CORD-v2 จาก Hugging Face", "2 ย่อภาพด้านยาว ≤ 1280 px", "3 แปลงเฉลยเป็น JSON",
                "4 Prompt ชุดเดียว ใช้ทุกขั้น", "5 dataset_samples.jpg", "receipt_data.py"],
     "scene": "A left-to-right pipeline inside one script file card labelled receipt_data.py. (1) a cloud with a hugging-face "
              "emoji icon (no text) sends a stack of receipt photos; (2) a receipt photo shrinks inside a frame with a "
              "resize arrow; (3) the receipt's printed lines turn into a JSON card with curly braces; (4) one instruction card "
              "with three arrows going to three small icons: a training gear, a scoring checklist and a web page; (5) a small "
              "picture grid of six receipts each paired with a JSON card."},
    {"img": "n27-step3-accum", "title": "ขั้นที่ 3: ป้อนทีละใบ สะสม gradient แล้วจึงปรับน้ำหนัก",
     "labels": ["ป้อนทีละ 1 ใบ", "สะสม gradient 4 ใบ", "ปรับน้ำหนัก 1 ครั้ง", "800 ใบ × 2 Epoch ÷ 4 = 400 step",
                "คิด loss เฉพาะคำตอบ JSON"],
     "scene": "A training machine (GPU box) on the left takes in one receipt at a time from a tall stack. Each receipt produces "
              "a small glowing gradient drop that falls into a measuring cup; the cup shows four drops collected. When the cup "
              "is full, an arrow pours it into a small orange module (the LoRA A and B matrices) with a wrench, meaning one "
              "weight update. Below, a wide formula banner. On the right, an answer card split in two parts: the image and "
              "instruction part greyed out, the JSON answer part highlighted, with the loss label pointing only to the JSON part."},
    {"img": "n28-step4-serve", "title": "ขั้นที่ 4: AI server เดียว ให้บริการสองโมเดล",
     "labels": ["vLLM พอร์ต 8000", "โหลดโมเดลเดิมครั้งเดียว", "receipt-base", "receipt-ft = Base + LoRA",
                "1 เห็นทั้งสองโมเดล", "2 มี key → ได้ JSON", "3 ไม่มี key → 401"],
     "scene": "One GPU server box on the right holds one big model block loaded once. Two doors on the front of the server: "
              "the left door goes straight to the model, the right door passes through a small orange LoRA module first. On the "
              "left side, three numbered test cards come from outside: (1) a list showing two model names with green ticks; "
              "(2) a request with a key icon returns a JSON card with a green tick; (3) a request without a key bounces off a "
              "closed shield with a red cross."},
    {"img": "n29-step6-web", "title": "ขั้นที่ 6: เว็บสมุดรายจ่ายบนเครื่องของเรา",
     "labels": ["localhost:3404", "1 อัปโหลดหรือเลือกใบเสร็จตัวอย่าง", "2 เลือก Base / Fine-tuned / เทียบสองโมเดล",
                "3 ตารางรายการ + ยอดรวม (Rp)", "4 บันทึกเป็นรายจ่าย", "PostgreSQL", "AI server บน Vast.ai"],
     "scene": "A large laptop screen in the center shows a simple web app in four numbered regions: (1) a row of receipt "
              "thumbnails with an upload button; (2) three toggle buttons; (3) a receipt photo next to an item table; (4) a "
              "save button. Under the laptop a database cylinder. A cable from the laptop goes to a GPU server box in a cloud "
              "on the far right."},
    {"img": "n30-step8-skill", "title": "ขั้นที่ 8: สกิลเก็บวิธีทำงานพร้อมโค้ดที่ใช้ได้จริง",
     "labels": ["SKILL.md", "1 ค่าที่ปรับได้", "2 ขั้นตอน", "3 เกณฑ์ตรวจผ่าน", "4 กติกาเรื่องเงิน", "scripts/",
                ".claude/skills/receipt-vlm-finetune", "สกิล vastai"],
     "scene": "An open folder in the center labelled .claude/skills/receipt-vlm-finetune. Inside it a document card SKILL.md "
              "with four numbered sections, each with a small icon (sliders, a numbered list, a checklist, a coin with a trash "
              "can), and next to it a smaller folder card scripts/ containing a few code file icons. An arrow from SKILL.md "
              "points to a separate small toolbox card that is the existing vastai skill."},
    {"img": "n31-v0-issues", "title": "สกิล v0 ยังพลาด 4 จุดในรอบทดสอบ",
     "labels": ["1 $0 ถูกแทนค่า", "2 ไม่ได้กรอง VRAM", "3 ดึงผลกลับช้า", "4 สคริปต์ที่แก้ยังไม่เคยรัน"],
     "scene": "Four equal panels in a 2 x 2 grid, each with a numbered circle badge and a small amber warning triangle. "
              "(1) a blank price tag with only a large dollar sign on it, half rubbed out by an eraser; the tag has NO digits at all; (2) a "
              "small laptop GPU card that is too small next to a big desktop GPU card, the small one being thrown out; "
              "(3) a tiny file moving slowly through a long pipe with a snail and a clock; (4) an edited script page with a "
              "pencil and an untested 'play' button with a question mark."},
    {"img": "n32-lessons", "title": "บทเรียนจาก LAB 2",
     "labels": ["1 LoRA สอนกติกาของงาน", "2 Test Set ตัดสินครั้งเดียวตอนจบ", "3 เงินเดินตลอดเวลาที่เครื่องเปิด",
                "4 เก็บงานเป็นสกิล แล้วปรับทีละเวอร์ชัน"],
     "scene": "Check the Thai spelling of every label carefully, for example เครื่อง is spelled ค-ร-ื่-อ-ง. Four equal panels side by side, each with a numbered circle badge and one clear icon: (1) a small orange "
              "plug-in module attached to a big model block, with a rule card; (2) a locked glass box of receipts opened only "
              "once, with a finish flag; (3) a GPU server with a running coin meter and an hourglass; (4) a recipe card with "
              "version tags v0 and v1 and a circular improvement arrow."},
    {"img": "n33-limits", "title": "ข้อจำกัดที่ยังเหลือ",
     "labels": ["1 ชื่อผิด 1 ตัวอักษร = ผิดทั้งรายการ", "2 Vision Encoder ไม่ได้ถูกเทรน", "3 ใบเสร็จเงินรูเปียห์ (Rp)",
                "4 สกิล v0 ยังไม่สมบูรณ์"],
     "scene": "Four equal panels side by side, each with a numbered circle badge and an amber warning outline: (1) a product "
              "name tag with one wrong letter circled in red and the whole row crossed; (2) an eye-shaped camera block with a "
              "padlock on it, meaning it was frozen and not trained; (3) a paper receipt with Rupiah banknotes beside it; "
              "(4) a recipe card labelled v0 with a small crack and a wrench."},
]

PHOTOS2 = [
    {"img": "p21-shop", "band": True, "scene": "A tired small-shop owner sits at the counter of a cosy Southeast Asian cafe late in the evening, "
                                 "looking at a big messy pile of paper receipts and typing figures into a laptop by hand. Warm "
                                 "lamp light. Mood: slow, tedious manual work."},
    {"img": "p22-receipts", "band": True, "scene": "Close-up of many printed paper receipts from different cafes and shops spread on a wooden table, "
                                     "different lengths and layouts, a few with coffee stains, soft daylight. The print is blurred "
                                     "and unreadable."},
    {"img": "p23-rent", "scene": "A person at a desk at night compares many server offers on a laptop (screen content blurred, only "
                                 "abstract rows of colour), a cup of coffee beside the laptop, a city window behind.",
     "setting": "a home office at night"},
    {"img": "p24-train", "scene": "Close-up inside a server: one large graphics card with glowing fans running under load, faint "
                                  "heat haze, tiny status lights, shallow depth of field.", "setting": "a cloud GPU data center"},
    {"img": "p25-eval", "scene": "An examiner's desk: two printed answer sheets side by side, a red pen and a green pen marking "
                                 "ticks and crosses, a stack of paper receipts next to them. The writing is blurred and "
                                 "unreadable.", "setting": "a quiet office desk"},
    {"img": "p26-web", "scene": "A smartphone photographs a paper receipt on a cafe counter while an open laptop next to it shows "
                                "a clean web app with a table (screen content blurred, abstract shapes only).",
     "setting": "a small Southeast Asian cafe counter in daylight"},
    {"img": "p27-off", "scene": "A finger presses the power button of a rack server in a dim data center aisle; the status "
                                "lights are turning from green to off.", "setting": "a cloud GPU data center"},
    {"img": "p28-skill", "scene": "An open notebook with a neatly written step-by-step procedure (handwriting blurred and "
                                  "unreadable) lies next to a laptop and a cup of tea, a pen resting on the page.",
     "setting": "a tidy desk in a small office"},
    {"img": "p29-meter", "band": True, "scene": "A rented server rack in a dim aisle with an old mechanical coin counter and an hourglass placed "
                                  "on top of the rack; the sand is running. Mood: money keeps running while the machine is on.",
     "setting": "a cloud GPU data center"},
]

ILLUS = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their style: clean flat vector figure, light background,
rounded title banner, thick dark outlines, soft pastel blocks (blue, orange, green, lilac), bold rounded Thai lettering:
{refs}

It must look like a figure in a well-made university textbook: calm, clear, not childish. Few decorations, no sparkles,
no cartoon mascots, no smiling faces on objects. Generous white space so every label can be read at slide size.

Canvas: landscape 16:9 (about 1600 x 900). Setting: {setting}.

Title banner text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above.
- When a label starts with a number followed by a space (for example "3 gate"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Numbers that are inside a label (for example 1280 or 334,011) must appear exactly once, exactly as written, attached to that label.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, JSON, model names) use a monospace font.
- If people appear, they are fictional adults drawn simply; no real person's likeness.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

PHOTO2 = PHOTO.replace("- Keep the left 45% of the frame calm and darker (out-of-focus background), main subject on the right side, because a title will be placed over the left side later.\n",
                       "- Keep the lower third of the frame calm and darker, because one sentence will be placed over it later.\n")


def write_pass2(out, refs):
    os.makedirs(out, exist_ok=True)
    for f in ILLUS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(ILLUS.format(
            out=out, img=f["img"], refs="\n".join(refs), setting=SETTING, title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
    for f in PHOTOS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write((PHOTO2 if f.get("band") else PHOTO).format(out=out, img=f["img"], setting=f.get("setting", SETTING), scene=f["scene"]))
    print("%d พรอมต์ (ชุดที่ 2) -> %s" % (len(ILLUS2) + len(PHOTOS2), out))


if __name__ == "__main__":
    if "--pass2" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--pass2"]
        write_pass2(os.path.abspath(args[0]).replace("\\", "/"), [os.path.abspath(p).replace("\\", "/") for p in args[1:]])
        sys.exit(0)
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
