#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์บทนี้ (ReceiptDesk · บริการอ่านใบเสร็จสำหรับสำนักงานบัญชี)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล)
  title  หัวข้อของสไลด์ และข้อความบนป้ายชื่อของภาพ
  labels ข้อความสั้นบนภาพ
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ
  steps  ขั้นตอนข้างภาพ 3-5 ขั้น · เรียบเรียงจาก README.md ของบท
PHOTOS = ภาพถ่ายสมจริงของหน้าคั่น (ไม่มีตัวอักษรในภาพ · ฝั่งซ้ายมืดไว้วางหัวข้อ)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
"""
import os, sys

SETTING = ('a small Thai accounting office called "ใส่ใจการบัญชี" (desks with stacks of paper receipts, laptops, '
           'a document scanner, filing cabinets) that sends receipt photos to a rented GPU server with 2 GPUs')

FIGS = [
    {"img": "n01-four-phases", "title": "ส่งมอบระบบใน 4 ระยะ จากบันทึกสัมภาษณ์ถึงรายงานส่งมอบ",
     "labels": ["1 Requirement", "2 Planning", "3 Build · Train · Deploy", "4 Verification",
                "INTERVIEW.md", "DELIVERY.md", "คนอนุมัติ"],
     "scene": "Four numbered stations from left to right connected by thick arrows. At the far left a sheet of interview notes "
              "(label INTERVIEW.md). Station 1: a desk with three stacked documents and a pen. Station 2: a whiteboard with "
              "connected boxes (a dependency graph) and horizontal schedule bars. Station 3: a team of small AI robots building a "
              "web page on a big screen next to a server box with two graphics cards. Station 4: two testers with a checklist and a "
              "magnifying glass. At the far right a finished report (label DELIVERY.md). Between station 2 and station 3 a person "
              "holds up an approval stamp (label คนอนุมัติ).",
     "steps": ["**Requirement** (ขั้นที่ 1–3): User Story · Requirement · System Design และข้อมูลทดสอบ จากบันทึกการสัมภาษณ์",
               "**Planning** (ขั้นที่ 4–5): แตกงานเป็นบล็อก วาด DAG และ Gantt แล้วทำ What-if ก่อนตัดสินใจรัน",
               "**Build · Train · Deploy** (ขั้นที่ 6–12): Agent Team สร้างระบบ · เทรน 1 GPU เทียบ 2 GPU · Deployment · Capacity Test ตาม SLO",
               "**Verification** (ขั้นที่ 13–17): Test Charter · Test Plan · Playwright Test · Bug Hunt · รายงานส่งมอบ · ลบเครื่อง",
               "คนตัดสินใจ **ก่อนรันทีมจริง** และ **ก่อนเช่าเครื่อง** · ขั้นที่ 18–19 เก็บทั้งหมดเป็นสกิลเวอร์ชัน 1"]},
    {"img": "n02-model-metrics", "title": "\"ยอดรวมต้องถูก\" กลายเป็นตัวชี้วัด 4 ตัว",
     "labels": ["M1 อ่านยอดรวมถูก", "M2 ยอดผิดและไม่ติดธง", "M3 ใบผิดถูกติดธง", "M4 สัดส่วนใบที่ติดธง", "ติดธง", "Test Set"],
     "scene": "A 2 x 2 grid of four panels. Top-left (M1): a stack of receipts where most receipts have a green check mark and "
              "very few have a red cross. Top-right (M2): one receipt with a wrong total slipping past a reviewer unnoticed, with no "
              "flag on it, shown as a danger. Bottom-left (M3): receipts with wrong totals each carrying a small yellow flag, caught by "
              "an accountant. Bottom-right (M4): an accountant at a desk with only a small pile of flagged receipts to check, next to "
              "a large pile that needs no check. A small tray in the middle labelled Test Set.",
     "steps": ["**M1 Total Accuracy ≥ 95.0%** แปลงจาก \"100 ใบ ยอดรวมผิดได้ไม่เกิน 5 ใบ\"",
               "**M2 Silent Error Rate ≤ 1.0%** (ยอดผิดและไม่ติดธง) แปลงจาก \"5 ใบนั้นคนต้องตรวจเจอ\" + \"อย่าเดา\"",
               "**M3 Flag Recall ≥ 80.0%** แปลงจาก \"ถ้าไม่แน่ใจต้องบอก\"",
               "**M4 Flag Rate ≤ 20.0%** แปลงจาก \"ตรวจทุกช่องทุกใบก็ไม่ได้ประหยัดเวลา\"",
               "M1 วัดว่าอ่านถูกแค่ไหน ส่วน M2–M4 วัดว่าโมเดล **รู้ตัวว่าไม่แน่ใจ** ดีแค่ไหน"]},
    {"img": "n03-queue-design", "title": "คิว 2 ระดับ: งานด่วนแซงได้ งานปกติไม่ค้าง ใบเสร็จไม่หาย",
     "labels": ["receipts.urgent", "receipts.normal", "receipts.dlq", "1 ด่วนติดกันไม่เกิน 4 ใบ", "2 คิวเต็ม ตอบ 429",
                "3 ล้มเหลวครบ 3 ครั้ง", "4 ack หลังบันทึกผล", "GPU Worker"],
     "scene": "Two conveyor belts coming from the left carrying paper receipts: the upper belt is orange (label receipts.urgent), "
              "the lower belt is blue (label receipts.normal). Both belts lead to two small robots on the right (label GPU Worker), "
              "each picking up one receipt at a time. Badge 1: above the merge point a small sign showing four orange receipts then "
              "one blue receipt. Badge 2: at the entrance on the left a gate keeper holds up a sign 429 and turns away an overflowing "
              "pile of receipts. Badge 3: below the robots a bin for torn, unreadable receipts (label receipts.dlq). Badge 4: a robot "
              "stamps a result into a ledger and then sends a check mark back.",
     "steps": ["**Priority Queue**: 2 คิว `receipts.urgent` และ `receipts.normal` · Worker หยิบใบด่วนก่อน แต่ไม่เกิน 4 ใบติดกัน",
               "**Backpressure** 2 ด่าน: เว็บไม่รับทั้งชุดเมื่องานปกติค้างเกิน 400 ใบ พร้อมบอกนาทีที่ให้ลองใหม่ · gateway ตอบ `429`",
               "**Dead-letter Queue**: ใบที่ล้มเหลวครบ 3 ครั้งไปที่ `receipts.dlq` แล้วไปอยู่หน้า \"อ่านไม่ได้ ให้คนพิมพ์เอง\"",
               "**งานไม่หายเมื่อ Worker ล่ม**: Worker หยิบทีละ 1 ใบ และ ack หลังบันทึกผล · Worker ที่เหลือหยิบงานต่อเอง"]},
    {"img": "n04-review-scope", "title": "ผู้ตรวจพบกรณีขอบใหม่ทุกรอบ คนต้องกำหนดขอบเขตการตรวจ",
     "labels": ["1 ผู้ทำแก้ตามที่ขอ", "2 ผู้ตรวจพบกรณีใหม่", "3 คนกำหนดขอบเขต", "4 ผ่าน · จดงานตามหลัง", "FOLLOW-UPS.md"],
     "scene": "Left half: a circular loop of arrows between two small robots of different colours: a white-and-teal robot (the maker) "
              "hands a code document to a white-and-orange robot (the reviewer), who hands it back with a new small PDF icon and a "
              "question mark each round; three small round markers on the loop show repeated rounds. Middle: a human team lead steps "
              "in and draws a clear rectangular boundary around a checklist of test cases. Right: a green approval stamp on the "
              "document, and next to it an open notebook (label FOLLOW-UPS.md) collecting the PDF items that fall outside the boundary.",
     "steps": ["รอบแรกและรอบรันต่อ: ผู้ทำแก้ครบทุกข้อที่ผู้ตรวจขอ เทสต์เพิ่มจาก 82 เป็น 89 ข้อ",
               "ผู้ตรวจ (Codex) พบกรณีขอบของไฟล์ PDF ใหม่ทุกรอบ และกรณีเหล่านั้น **ไม่มีใน Requirement**",
               "คนกำหนดขอบเขตใหม่: ผ่านเมื่อกรณีทดสอบของ Business Rule ในข้อมูลทดสอบผ่านครบ และไม่ขัดกับ Requirement",
               "ข้อที่อยู่นอกขอบเขตจดไว้ที่ `plan/FOLLOW-UPS.md` · โค้ดของ B03 ไม่ได้แก้ แต่ผ่านในรอบแรกด้วยเทสต์ 89/89"]},
    {"img": "n05-test-types", "title": "แยก Test Case ตามสิ่งที่ใช้รัน: ตัวอ่านจำลอง หรือโมเดลจริง",
     "labels": ["M ตัวอ่านจำลอง", "A ไม่ขึ้นกับผลอ่าน", "R โมเดลจริง", "พอร์ต 3421", "พอร์ต 3420", "0.89 / 0.90 / 0.91", "GPU"],
     "scene": "Two web app windows side by side. The left window (label พอร์ต 3421) is connected by a cable to a simple mock "
              "reader machine that prints a preset answer card with confidence values (label 0.89 / 0.90 / 0.91). The right window "
              "(label พอร์ต 3420) is connected to a server box with two graphics cards (label GPU) that reads a real receipt photo. "
              "In front, three groups of test cards: a group marked with a big letter M (label M ตัวอ่านจำลอง) and a group marked A "
              "(label A ไม่ขึ้นกับผลอ่าน) both walk to the left window; a small group marked R (label R โมเดลจริง) walks to the right window.",
     "steps": ["**M** 21 ข้อ: ต้องกำหนดผลอ่านให้แน่นอน เช่น ความมั่นใจ 0.89 / 0.90 / 0.91 จึงรันกับตัวอ่านจำลอง (พอร์ต 3421)",
               "**A** 32 ข้อ: ไม่ขึ้นกับผลอ่าน เช่น ชุด 99 / 100 / 101 ไฟล์ จึงรันกับตัวอ่านจำลองเพื่อไม่ใช้ GPU",
               "**R** 6 ข้อ: รันกับโมเดลจริง (พอร์ต 3420) เช่น อ่านครบ 5 ช่องจากใบเสร็จจริง 12 ใบ",
               "ตัวอ่านจำลองทำให้ 53 จาก 59 ข้อรันได้โดยไม่ใช้ GPU และไม่มีข้อใดถูกบล็อกเพราะกำหนดคำตอบของโมเดลไม่ได้"]},
    {"img": "n06-boundary-bugs", "title": "บั๊กซ่อนอยู่ที่เส้นแบ่งของ Business Rule",
     "labels": ["ต่ำกว่า", "เท่ากับ", "สูงกว่า", "1.00 บาท", "วันที่ 1", "งานที่ 5", "BUG_MODE=1"],
     "scene": "Three short horizontal rulers stacked one above the other. Each ruler has one bold vertical boundary line in its "
              "middle and a small boundary tag on that line: top ruler tag 1.00 บาท, middle ruler tag วันที่ 1, bottom ruler tag "
              "งานที่ 5. On every ruler one small cartoon beetle hides exactly on the boundary line. Above the top ruler three column "
              "captions, each written once: ต่ำกว่า over the left of the line, เท่ากับ over the line, สูงกว่า over the right of the "
              "line. A tester holds a magnifying glass over the beetles. In the top-right corner a toggle switch turned on "
              "(label BUG_MODE=1). No other numbers.",
     "steps": ["ทุก **Business Rule** เป็นตัวเลขที่ตรวจได้ พร้อมค่าตัวอย่าง ต่ำกว่า · เท่ากับ · สูงกว่า เส้นแบ่ง (เช่น BR-01: 99 · 100 · 101 ไฟล์)",
               "เว็บมีโหมด `BUG_MODE=1` ที่ทำให้ Business Rule ผิด 3 ข้อ รายชื่ออยู่ใน `docs/BUGS-SECRET.md` ที่เดียว",
               "รัน Playwright Test ชุดเดิมกับ `BUG_MODE=1` แล้วเทียบข้อที่ล้มเพิ่มกับรอบปกติ",
               "บั๊กทั้ง 3 ตัวอยู่ที่เส้นแบ่ง (1.00 บาท · วันที่ 1 · งานที่ 5) Test Case ที่ลองค่า \"ต่ำกว่า · เท่ากับ · เกิน\" จึงจับได้ครบ"]},
]

PHOTOS = [
    {"img": "s01-gpu-build", "scene": "Evening in the accounting office. A young developer sits at a desk on the right side of the frame "
                                      "watching a laptop and a second monitor with abstract blurred progress bars, while a compact server "
                                      "with two large graphics cards and glowing fans stands on a side table next to the desk. Stacks of "
                                      "paper receipts in folders in the background. Mood: the system is being built and trained."},
    {"img": "s02-verify", "scene": "Daytime in the accounting office. A quality assurance tester and an accounting team lead sit side by side "
                                   "on the right side of the frame, comparing a paper receipt in hand with a laptop screen showing an abstract "
                                   "blurred form, a printed checklist with tick marks on the desk. Mood: careful verification before delivery."},
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
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, queue names, port numbers) use a monospace font.
- Characters: a friendly team of adult office workers and small white-and-teal robots that represent the AI. Fictional cartoon characters only. No emoji.

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

# ------------------------------------------------------------------ รอบที่ 2: ภาพอธิบายแบบตำรา (n2x/n3x/n4x) และภาพถ่าย (p2x)
# ข้อความในภาพเรียบเรียงจาก README.md · ภาพที่มีตัวเลข: ตัวเลขทุกตัวมาจาก README (บัญชีตัวเลขอยู่ในโฟลเดอร์งาน numbers.md)
FIGS2 = [
    {"img": "n21-conflicts", "ratio": "4:3",
     "labels": ["คุณกิตติ", "คุณอรทัย", "งานด่วนแซงคิว", "งานปกติไม่ค้างข้ามวัน", "คนตรวจเจอยอดผิดทุกใบ", "ไม่ตรวจทุกช่องทุกใบ"],
     "scene": "Two balance scales side by side. Each scale has one pan on the left and one pan on the right, and the beam is level. "
              "On top of the picture, over the left pans, a small portrait badge of a man in a white shirt (label คุณกิตติ); over the "
              "right pans a small portrait badge of a woman in a cream blouse (label คุณอรทัย). Upper scale: the left pan holds a "
              "small orange stack of receipts with a fast-forward arrow (label งานด่วนแซงคิว), the right pan holds a blue stack of "
              "receipts with a calendar (label งานปกติไม่ค้างข้ามวัน). Lower scale: the left pan holds a magnifying glass over a "
              "receipt with a red circle on the total (label คนตรวจเจอยอดผิดทุกใบ), the right pan holds a receipt where only one "
              "line is highlighted and the other lines are greyed out (label ไม่ตรวจทุกช่องทุกใบ)."},
    {"img": "n22-doc-chain", "ratio": "16:9",
     "labels": ["INTERVIEW.md", "USER-STORIES.md", "REQUIREMENTS.md", "DESIGN.md",
                "ลูกค้าพูดว่าอะไร", "ใครต้องการอะไร เพื่ออะไร", "ระบบต้องทำอะไร ต้องดีแค่ไหน", "ระบบมีส่วนใดบ้าง"],
     "scene": "Four document sheets in a row from left to right, connected by thick arrows. Each sheet has a distinct simple icon: "
              "sheet 1 a speech bubble (file name INTERVIEW.md), sheet 2 a person silhouette with a target (USER-STORIES.md), sheet 3 "
              "a checklist with a ruler (REQUIREMENTS.md), sheet 4 a block diagram of connected boxes (DESIGN.md). Under each sheet "
              "its question in a light caption box: ลูกค้าพูดว่าอะไร / ใครต้องการอะไร เพื่ออะไร / ระบบต้องทำอะไร ต้องดีแค่ไหน / "
              "ระบบมีส่วนใดบ้าง. No people."},
    {"img": "n23-model-io", "ratio": "16:9",
     "labels": ["รูปใบเสร็จ", "คำสั่ง", "Qwen3-VL-2B-Instruct", "LoRA", "JSON", "total.total_price"],
     "scene": "A left-to-right flow. Left: a photo of a crumpled shop receipt (label รูปใบเสร็จ) and below it a short text instruction "
              "card drawn as grey lines (label คำสั่ง). Both arrows go into a rounded box in the centre representing a vision-language "
              "model with a small eye icon and a text icon (label Qwen3-VL-2B-Instruct); a thin adapter strip attached to the box "
              "(label LoRA). Right: a code card with curly braces (label JSON), one line of it highlighted in orange "
              "(label total.total_price)."},
    {"img": "n25-setup", "ratio": "4:3",
     "labels": ["Claude Code", "container multi-account", "yolo1", "yolo2", "yolo3", "cyolo1", "Vast.ai", ".env"],
     "scene": "A laptop on the left showing a terminal window (label Claude Code). An arrow goes to a large rounded container box in "
              "the middle (label container multi-account) holding four small account cards in a 2 x 2 grid (labels yolo1, yolo2, "
              "yolo3, cyolo1). An arrow from the container goes up-right to a cloud with a server rack with graphics cards (label "
              "Vast.ai). A small padlock-and-key file icon sits next to the laptop (label .env)."},
    {"img": "n26-quote-to-story", "ratio": "4:3",
     "labels": ["คำพูดในบันทึกสัมภาษณ์", "User Story", "ในฐานะ… ฉันต้องการ… เพื่อ…", "US-01", "Must / Should / Could",
                "เกณฑ์ยอมรับ", "อ้างที่มา", "นอกขอบเขต"],
     "scene": "Left: a page of interview notes with one sentence highlighted in yellow and a speech bubble (label คำพูดในบันทึกสัมภาษณ์). "
              "Right: a large index card titled User Story with a code tag (US-01), a sentence template line "
              "(ในฐานะ… ฉันต้องการ… เพื่อ…), a priority tag (Must / Should / Could) and a small checklist area (label เกณฑ์ยอมรับ). "
              "A dashed arrow runs from the card back to the highlighted sentence (label อ้างที่มา). At the bottom right a separate "
              "grey tray holding two greyed cards (label นอกขอบเขต)."},
    {"img": "n27-unanswered", "ratio": "4:3",
     "labels": ["คำถามที่ไม่มีใครตอบ", "US-24", "เก็บเป็นความต้องการ"],
     "scene": "A meeting table seen from the side. At one end a restaurant owner in a green apron raises a hand with a speech bubble "
              "that contains only a large question mark (label คำถามที่ไม่มีใครตอบ). The other people at the table look at their "
              "laptops and do not respond. On the right a small white-and-teal assistant robot catches the speech bubble and pins it "
              "onto a requirement board as a new card (label US-24), with a green tick (label เก็บเป็นความต้องการ)."},
    {"img": "n28-slo-lanes", "ratio": "4:3",
     "labels": ["งานปกติ", "ชุด 100 ใบ ≤ 30 นาที", "งานด่วน", "≤ 5 นาที", "ด่วนติดกันไม่เกิน 4 ใบ", "หัวหน้าทีม"],
     "scene": "Two horizontal lanes like a race track leading to a finish line on the right with a stopwatch. Upper lane, blue, wide: "
              "a long row of blue receipt cards (lane label งานปกติ, time label ชุด 100 ใบ ≤ 30 นาที). Lower lane, orange, narrow: a "
              "short row of orange receipt cards (lane label งานด่วน, time label ≤ 5 นาที). At the merge gate before the finish, a "
              "sign shows four orange cards followed by one blue card (label ด่วนติดกันไม่เกิน 4 ใบ). At the start of the orange "
              "lane a team lead holds the only key that opens it (label หัวหน้าทีม)."},
    {"img": "n29-assumption", "ratio": "4:3",
     "labels": ["ลูกค้าไม่ได้ให้ตัวเลข", "ข้อสมมติ", "ลูกค้ายืนยัน", "0.90", "400 ใบ", "4 ใบต่อนาทีต่อ Worker"],
     "scene": "Left: a requirement sheet with three empty blanks (label ลูกค้าไม่ได้ให้ตัวเลข). Middle: an analyst fills the three blanks "
              "with three yellow sticky notes, each showing one value: 0.90 / 400 ใบ / 4 ใบต่อนาทีต่อ Worker, and the stack of notes is "
              "marked with a stamp (label ข้อสมมติ). Right: the sheet is handed to a customer who signs it with a pen "
              "(label ลูกค้ายืนยัน)."},
    {"img": "n30-two-queues", "ratio": "4:3",
     "labels": ["คิวเดียว", "งานปกติรอไม่สิ้นสุด", "แยก 2 คิว", "ด่วน 4 ใบ แล้วปกติ 1 ใบ", "receipts.urgent", "receipts.normal"],
     "scene": "Top half (label คิวเดียว): one single conveyor where orange receipts keep jumping to the front and a blue receipt at the "
              "back has a clock and cobwebs (label งานปกติรอไม่สิ้นสุด), marked with a red cross. Bottom half (label แยก 2 คิว): two "
              "parallel conveyors, orange (label receipts.urgent) and blue (label receipts.normal), merging through a counter gate "
              "into a worker robot; the output sequence shows four orange cards then one blue card (label ด่วน 4 ใบ แล้วปกติ 1 ใบ), "
              "marked with a green tick."},
    {"img": "n32-train-gate", "ratio": "16:9",
     "labels": ["Training Set", "1 GPU", "2 GPU", "LoRA", "Test Set", "Acceptance Gate"],
     "scene": "Left: a stack of receipts (label Training Set) feeds two parallel training tracks. Upper track: one graphics card "
              "(label 1 GPU) with a long progress bar. Lower track: two graphics cards (label 2 GPU) with a progress bar half as long. "
              "Both tracks produce the same small adapter chip (label LoRA). Right: the chip is tested on a separate small stack of "
              "receipts (label Test Set) in front of a CLOSED checkpoint barrier with a sign (label Acceptance Gate). The gate shows NO tick mark and NO cross: its verdict is not decided yet. Both progress bars are drawn completely full (finished), the upper one long and the lower one about half as long. No office background."},
    {"img": "n33-gate-stop", "ratio": "4:3",
     "labels": ["Acceptance Gate", "ไม่ผ่าน", "M5", "M4", "M1, M2"],
     "scene": "A road with a closed red-and-white barrier and a sign (label Acceptance Gate) with a red stop light (label ไม่ผ่าน). A "
              "friendly model robot holding a report card with mostly rising green bars waits in front of the closed barrier. Three "
              "red tags hang from the barrier, each a different short code: M5, M4, M1, M2 (the third tag reads M1, M2). Calm, factual "
              "mood, not dramatic."},
    {"img": "n34-deploy-path", "ratio": "16:9",
     "labels": ["เครื่องนี้", "เครื่อง GPU ที่เช่า", "เว็บ", "dispatcher", "API gateway", "X-API-Key", "RabbitMQ",
                "GPU Worker", "NGINX least_conn", "vLLM"],
     "scene": "Two large zones side by side. Left zone with a light green background (label เครื่องนี้) contains a browser window "
              "(label เว็บ) and a small box (label dispatcher). Right zone with a light orange background (label เครื่อง GPU ที่เช่า) "
              "contains, from left to right: a gate box (label API gateway), a queue drawn as stacked trays (label RabbitMQ), two "
              "small robot boxes (one label GPU Worker for both), a load balancer box (label NGINX least_conn), and two server boxes "
              "each with one graphics card (one label vLLM for both). A receipt icon travels along arrows: dispatcher to API gateway "
              "carrying a key tag (label X-API-Key), then through the queue, worker, load balancer to vLLM."},
    {"img": "n35-wait-time", "ratio": "16:9",
     "labels": ["ผู้ใช้รอ 7.2 วินาที", "โมเดลอ่าน 0.88 วินาที", "รอบ poll 5 วินาที"],
     "scene": "One long horizontal time bar across the picture with an hourglass at its left end and a person waiting at a screen "
              "(label ผู้ใช้รอ 7.2 วินาที above the whole bar). Inside the bar, a very short teal segment (label โมเดลอ่าน 0.88 วินาที) "
              "and a long grey segment drawn with a circular refresh arrow icon (label รอบ poll 5 วินาที). The rest of the bar is "
              "plain light grey without any label. Clean flat chart-like style."},
    {"img": "n36-human-bottleneck", "ratio": "4:3",
     "labels": ["GPU Worker", "100 ใบใน 1 นาที", "SLO 30 นาที", "ใบที่ติดธง", "คนตรวจ"],
     "scene": "Left: two fast robot workers next to a server with graphics cards (label GPU Worker) finishing a stack of receipts with "
              "speed lines (label 100 ใบใน 1 นาที); a large stopwatch far to the right of them shows lots of spare time "
              "(label SLO 30 นาที). Right: an accountant at a desk with a growing pile of receipts that carry small yellow flags "
              "(label ใบที่ติดธง), carefully checking them one by one (label คนตรวจ). The narrow point of the flow is the accountant."},
    {"img": "n37-six-testers", "ratio": "4:3",
     "labels": ["Test Charter", "C1", "C2", "C3", "C4", "C5", "C6", "playwright-cli"],
     "scene": "A large browser window of a receipt web app in the centre. Around it six small tester robots, each holding one card with "
              "its own code (C1, C2, C3, C4, C5, C6), each working on a different part of the page at the same time with a "
              "magnifying glass and a notebook. A stack of the six cards at the top left (label Test Charter). A small terminal icon "
              "in the corner (label playwright-cli)."},
    {"img": "n38-warnings", "ratio": "4:3",
     "labels": ["ผ่าน", "ข้อสังเกต", "ไม่ผ่าน 0", "ความเสี่ยงระดับ P1"],
     "scene": "A results board with many rows. Most rows have a green tick (legend label ผ่าน), a few rows have an amber warning "
              "triangle (legend label ข้อสังเกต), and the red cross column is empty (legend label ไม่ผ่าน 0). A large magnifying "
              "glass held by a tester enlarges two of the amber rows, revealing a red risk tag (label ความเสี่ยงระดับ P1)."},
    {"img": "n39-expected-from-req", "ratio": "4:3",
     "labels": ["Requirement", "ผลที่คาดหวัง", "คำนวณจากกติกา", "หน้าเว็บ", "ไม่ใช้เป็นเฉลย"],
     "scene": "Left: a requirement document (label Requirement). A solid arrow goes to a calculator and an answer card "
              "(labels คำนวณจากกติกา and ผลที่คาดหวัง). Right: a browser window showing a result (label หน้าเว็บ) with a dashed arrow "
              "towards the answer card that is blocked by a red stop sign (label ไม่ใช้เป็นเฉลย)."},
    {"img": "n40-triage", "ratio": "4:3",
     "labels": ["Test Case ที่ล้ม", "เว็บผิด", "แผนผิด", "เทสต์ผิด", "ผลที่คาดหวังคงเดิม"],
     "scene": "A pile of red test cards at the top (label Test Case ที่ล้ม) being sorted by a tester into three labelled bins below: "
              "a bin with a broken browser icon (label เว็บผิด), a bin with a document icon (label แผนผิด), a bin with a wrench and "
              "a code icon (label เทสต์ผิด). On the side, an answer card locked in a glass case with a padlock "
              "(label ผลที่คาดหวังคงเดิม)."},
    {"img": "n41-delivery", "ratio": "4:3",
     "labels": ["DELIVERY.md", "ยังไม่พร้อมใช้งานจริง", "Acceptance Gate ไม่ผ่าน", "ข้อบกพร่อง 9 ข้อยังเปิดอยู่",
                "Capacity Test ผ่านทุกข้อ"],
     "scene": "A delivery report on a desk (label DELIVERY.md) with an amber stamp on it (label ยังไม่พร้อมใช้งานจริง). To its right "
              "a short checklist of three lines with icons: a red cross (label Acceptance Gate ไม่ผ่าน), an amber triangle "
              "(label ข้อบกพร่อง 9 ข้อยังเปิดอยู่), a green tick (label Capacity Test ผ่านทุกข้อ). A developer hands the report to "
              "the office owner across the desk; both look serious and calm."},
    {"img": "n42-machine-time", "ratio": "16:9",
     "labels": ["เปิดเครื่อง 4 ชั่วโมง 48 นาที", "เทรน ประมาณ 5 นาที", "Capacity Test 25 นาที", "เครื่องเปิดรอ"],
     "scene": "Left: a rented GPU server next to a large wall clock (label เปิดเครื่อง 4 ชั่วโมง 48 นาที). Right of it two small "
              "equal-size task cards side by side: one with a training icon (label เทรน ประมาณ 5 นาที) and one with a load-test "
              "gauge icon (label Capacity Test 25 นาที). Right: the same server sitting idle with a coffee cup and a waiting "
              "hourglass (label เครื่องเปิดรอ). NO bars, NO timeline, NO chart, NO pie and no shape whose length or size stands "
              "for an amount of time."},
    {"img": "n43-skill-v1", "ratio": "4:3",
     "labels": ["เวอร์ชัน 0", "เวอร์ชัน 1", "What-if ก่อนรันทีม", "รันต่อเมื่อมีบล็อกไม่เสร็จ", "เทรนเทียบจำนวน GPU",
                "Capacity Test ตาม SLO", "แยก Test Case ตามสิ่งที่ใช้รัน"],
     "scene": "Left: a thin binder (label เวอร์ชัน 0). An arrow to the right: the same binder, thicker, with five new coloured index "
              "tabs sticking out (label เวอร์ชัน 1). Each tab has its own label in a list beside the binder: What-if ก่อนรันทีม / "
              "รันต่อเมื่อมีบล็อกไม่เสร็จ / เทรนเทียบจำนวน GPU / Capacity Test ตาม SLO / แยก Test Case ตามสิ่งที่ใช้รัน."},
    {"img": "n44-phase-gates", "ratio": "16:9",
     "labels": ["A Requirement", "B Planning", "C Build · Train · Deploy", "D Verification", "ถามคน", "ก่อนรันทีมจริง",
                "ก่อนเช่าเครื่อง"],
     "scene": "A path with four stations from left to right (labels A Requirement, B Planning, C Build · Train · Deploy, "
              "D Verification). Between stations there are small checkpoint gates. At the gate between B and C a person icon with a "
              "speech bubble (label ถามคน) and a sign (label ก่อนรันทีมจริง). Inside station C a second person icon at a gate in "
              "front of a cloud server (label ก่อนเช่าเครื่อง)."},
]

PHOTOS2 = [
    {"img": "p21-planning", "scene": "A development team of three adults stands at a whiteboard covered with sticky notes connected by "
                                     "drawn arrows and horizontal bars like a schedule, on the right side of the frame; one points at the "
                                     "board, another holds a laptop. The accounting office is visible softly in the background."},
    {"img": "p22-skill", "scene": "Late afternoon. A developer on the right side of the frame writes notes into a thick ring binder full of "
                                  "coloured index tabs on a desk, next to a closed laptop and a cup of tea, looking satisfied and calm."},
    {"img": "p23-delivery", "scene": "A small meeting table in the accounting office. On the right side of the frame a developer hands a "
                                     "printed report to the office owner, a woman in her early forties in a cream blouse; both look "
                                     "serious and attentive, a laptop and a small stack of receipts on the table."},
]

CLEAN = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

Style: a clean, modern, flat explanatory figure like one from a well-made university textbook or a technical report.
White or very light grey background, generous whitespace, thin dark-grey outlines, simple geometric icons, a restrained
palette (navy #12305e, teal #0f8f8c, orange #e07b1a, green #1e8a4c, red #c0392b, light greys). Not childish, no cartoon
faces with big eyes, no decorative clutter, no title banner. People, if any, are simple flat adult figures.

Canvas: landscape {ratio}. Setting of the story: {setting}.

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, digits, decimal
  points, symbols (≤ · … / , . -) and spacing stay exactly as they are. Each label appears exactly once.
- Do NOT add any other words, digits, numbers, captions, titles, axis values, watermarks or logos beyond the labels above.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, queue names,
  headers) use a monospace font.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""


if __name__ == "__main__" and "--pass2" in sys.argv:
    out = os.path.abspath(sys.argv[1]).replace("\\", "/")
    only = [a for a in sys.argv[2:] if a != "--pass2"]
    os.makedirs(out, exist_ok=True)
    n = 0
    for f in FIGS2:
        if only and f["img"] not in only:
            continue
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(CLEAN.format(
            out=out, img=f["img"], ratio=f["ratio"], setting=SETTING, scene=f["scene"], labels="\n".join(f["labels"])))
        n += 1
    for f in PHOTOS2:
        if only and f["img"] not in only:
            continue
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=SETTING, scene=f["scene"]))
        n += 1
    print("%d พรอมต์ -> %s" % (n, out))
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
