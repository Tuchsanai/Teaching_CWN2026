#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์หัวข้อ SiteSafe Inspect (FIGS = ภาพการ์ตูนอธิบาย · PHOTOS = ภาพถ่ายของหน้าคั่น)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล)
  title  หัวข้อของสไลด์ และข้อความบนป้ายชื่อของภาพ
  labels ข้อความสั้นบนภาพ (ป้ายที่เป็นขั้นตอนขึ้นต้นด้วยเลข)
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ
  steps  ขั้นตอนข้างภาพ 3-5 ขั้น · เรียบเรียงจาก README.md ของหัวข้อ
PHOTOS = ภาพถ่ายสมจริงของหน้าคั่น (ไม่มีตัวอักษรในภาพ · ฝั่งซ้ายมืดไว้วางหัวข้อ)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
"""
import os, sys

SETTING = ('a Thai high-rise construction contractor in Bangkok: building sites with cranes and steel frames, workers in hardhats '
           'and reflective safety vests, a site-office container with a meeting table, and a small software team office '
           'connected to one rented GPU server')

FIGS = [
    {"img": "n01-four-phases", "title": "4 ระยะ จากบันทึกสัมภาษณ์ถึงรายงานส่งมอบ",
     "labels": ["1 Requirement", "2 Planning", "3 Build · Train · Deploy", "4 Verification",
                "INTERVIEW.md", "DELIVERY.md", "คนอนุมัติก่อนรันทีม", "คนอนุมัติก่อนเช่าเครื่อง"],
     "scene": "A left-to-right road with four numbered stations connected by arrows. At the far left a single paper sheet "
              "labelled INTERVIEW.md. Station 1: a person writing requirement documents at a desk. Station 2: a whiteboard with "
              "boxes and arrows (a task graph) and a timeline chart. Station 3: three laptops of an AI team plus a GPU server "
              "box with a construction-site photo going into it. Station 4: a tester with a magnifying glass checking a web page "
              "with check marks and one cross mark. At the far right a report sheet labelled DELIVERY.md. Between station 2 and 3 a "
              "small gate with a person holding a stop sign (label: คนอนุมัติก่อนรันทีม); before the GPU server another small gate "
              "with a person (label: คนอนุมัติก่อนเช่าเครื่อง).",
     "steps": ["**Requirement** (ขั้นที่ 1–3): User Story · Requirement · System Design และข้อมูลทดสอบ",
               "**Planning** (ขั้นที่ 4): แตกงานเป็นบล็อก วาด DAG และ Gantt · คนอนุมัติแผนก่อนรันจริง",
               "**Build · Train · Deploy** (ขั้นที่ 5–9): Agent Team สร้างระบบ · เช่า GPU เทรนโมเดล และเปิดบริการ",
               "**Verification** (ขั้นที่ 10–14): Test Charter · Test Plan · Playwright Test · Bug Hunt · ลบเครื่อง",
               "ปิดท้าย (ขั้นที่ 15–16): เก็บทั้งหมดเป็นสกิล `agent-team-delivery` เวอร์ชัน 0"]},

    {"img": "n02-user-story", "title": "User Story 1 ข้อ อ้างคำพูดของลูกค้าเสมอ",
     "labels": ["คำพูดของลูกค้า", "1 ในฐานะ…", "2 ฉันต้องการ…", "3 เพื่อ…", "US-03 · Must",
                "เกณฑ์ยอมรับ", "จุดที่ขัดกัน", "คำถามถึงลูกค้า"],
     "scene": "On the left a customer in a white hardhat and reflective vest speaks; a speech bubble labelled คำพูดของลูกค้า. "
              "An arrow leads to a large index card in the middle with a tag US-03 · Must and three numbered rows "
              "(1 ในฐานะ…, 2 ฉันต้องการ…, 3 เพื่อ…) and a small checklist area labelled เกณฑ์ยอมรับ at the bottom of the card. "
              "On the right two small stacked trays: one with crossed-arrows icon labelled จุดที่ขัดกัน, one with a question mark "
              "labelled คำถามถึงลูกค้า. A small white-and-teal robot holds a pen next to the card.",
     "steps": ["รูปแบบ **ในฐานะ… ฉันต้องการ… เพื่อ…** ทุกข้อมีรหัส US-01… ระดับ Must / Should / Could และเกณฑ์ยอมรับที่ตรวจได้",
               "ทุกข้อ **อ้างคำพูดในบันทึก** ที่เป็นที่มา ห้ามเพิ่มความต้องการที่ลูกค้าไม่ได้พูด",
               "จุดที่ลูกค้าพูดขัดกันเอง และคำถามที่ต้องถามลูกค้าเพิ่ม แยกเป็น **2 ตารางท้ายไฟล์**",
               "สิ่งที่ลูกค้าบอกว่ายังไม่ทำในรุ่นแรก อยู่ในหัวข้อ **นอกขอบเขต**"]},

    {"img": "n03-boundary", "title": "Business Rule ต้องมีเส้นแบ่งที่ตรวจได้",
     "labels": ["BR-02", "V = 1", "V = 2", "V = 3", "เตือน", "ไม่ผ่าน", "ไม่ผ่าน", "ต่ำกว่า", "เท่ากับ", "สูงกว่า"],
     "scene": "A horizontal ruler across the picture with a vertical red boundary line in the middle labelled BR-02. "
              "Three photo frames of construction workers stand on the ruler: left frame shows one worker without a reflective vest "
              "(label V = 1, column caption ต่ำกว่า, yellow badge เตือน); middle frame exactly on the red line shows two workers "
              "without vests (label V = 2, caption เท่ากับ, red badge ไม่ผ่าน); right frame shows three workers without vests "
              "(label V = 3, caption สูงกว่า, red badge ไม่ผ่าน). All workers wear hardhats. A small robot points at the middle frame.",
     "steps": ["เขียนกติกาเป็นตัวเลข: **H** = จำนวนคนไม่ใส่หมวก · **V** = จำนวนคนไม่ใส่เสื้อสะท้อนแสง",
               "ทุก Business Rule มีค่าตัวอย่างที่ **ต่ำกว่า / เท่ากับ / สูงกว่า** เส้นแบ่ง",
               "ลูกค้าไม่ได้บอกว่าพอดี 2 คนเป็นอะไร AI เลือกทางที่เสี่ยงน้อยที่สุด: V = 2 → **ไม่ผ่าน** และจดเป็นข้อสมมติ",
               "ข้อสมมติทุกข้อต้องให้ลูกค้ายืนยัน (เช่น คุณวิชัยยืนยัน BR-02)"]},

    {"img": "n04-acceptance-gate", "title": "Acceptance Gate ต้องมีรูปใน Test Set พอ",
     "labels": ["Validation Set", "Test Set", "1 เลือก Threshold", "2 ตรึงค่า", "3 วัดครั้งเดียว",
                "ต้องการ 100 รูป", "มีจริง 25 รูป", "ยังตัดสินไม่ได้"],
     "scene": "Three numbered stations left to right. Station 1: an engineer turns a dial on a model box while looking at a "
              "folder labelled Validation Set. Station 2: the dial is locked with a padlock. Station 3: the model checks a folder "
              "labelled Test Set. On the right a gate with a scale: one pan shows a tall stack of photos labelled ต้องการ 100 รูป, "
              "the other pan a small stack labelled มีจริง 25 รูป. Above the gate an amber sign labelled ยังตัดสินไม่ได้. "
              "A small robot stands beside the gate looking unsure.",
     "steps": ["เลือก **Confidence Threshold** บน Validation Set แล้วตรึงไว้ก่อนวัดบน Test Set",
               "วัด Image-level Recall และ Precision ของคลาส \"ไม่ใส่หมวก\" บน Test Set เทียบกับเกณฑ์ใน Requirement",
               "เกณฑ์ใน Requirement ต้องการรูปที่มีคนไม่ใส่หมวก **อย่างน้อย 100 รูป** แต่ Test Set จริงมี **25 รูป**",
               "ตัวเลขถึงเกณฑ์ที่ขอบพอดี แต่รูปน้อยเกินกว่าจะยืนยัน ผลจึงเป็น **ยังตัดสินไม่ได้** ไม่ใช่ \"ผ่าน\""]},

    {"img": "n05-deploy-path", "title": "ทดสอบทั้งเส้นทาง และหยุด Worker กลางงาน",
     "labels": ["1 เว็บ", "2 gateway", "3 RabbitMQ", "4 GPU Worker", "X-API-Key", "ack หลังงานเสร็จ", "งานกลับเข้าคิว", "20 งาน หาย 0"],
     "scene": "A pipeline left to right: (1) a web page on a laptop with an uploaded construction photo; arrow with a key icon "
              "labelled X-API-Key to (2) a gateway box on a GPU server; arrow to (3) a queue drawn as a row of envelopes; arrow to "
              "(4) a GPU Worker robot with a graphics card. Below the worker a big red stop button pressed by a person, and a curved "
              "arrow from the worker back to the queue labelled งานกลับเข้าคิว. A small tick tag on the worker labelled "
              "ack หลังงานเสร็จ. At the right end a green counter board labelled 20 งาน หาย 0.",
     "steps": ["บนเครื่อง GPU เปิด **RabbitMQ · API gateway · GPU Worker** โดยใช้โมเดลที่เทรนแล้ว",
               "บนเครื่องนี้เปิดเว็บและฐานข้อมูลด้วย docker compose ที่พอร์ต 3410 ให้เว็บเรียก gateway บนเครื่อง GPU",
               "ส่งรูปจาก Test Set 5 รูปผ่านหน้าเว็บ แล้วตรวจว่าผลในฐานข้อมูลตรงกับที่ gateway ตอบ",
               "ส่ง 20 งาน หยุด Worker กลางงาน เปิดใหม่ แล้วนับว่าเสร็จครบ 20 งาน: Worker **ack หลังงานเสร็จ** งานที่ยังไม่ ack กลับเข้าคิวเอง"]},

    {"img": "n06-cross-review", "title": "ผู้ตรวจ Test Plan ต้องไม่ใช่ผู้เขียน",
     "labels": ["1 Claude เขียนแผน", "2 Codex ตรวจ", "3 แก้ข้อรุนแรงสูง", "TEST-PLAN.md", "PLAN-REVIEW.md", "ผลที่คาดหวังจาก Requirement"],
     "scene": "Three numbered panels left to right. Panel 1: a teal robot writes a document labelled TEST-PLAN.md, with a "
              "Requirement binder open beside it labelled ผลที่คาดหวังจาก Requirement. Panel 2: a different robot in orange with "
              "a magnifying glass reviews the same document and writes a list labelled PLAN-REVIEW.md with red marks. "
              "Panel 3: the teal robot fixes the document while a person watches; the document now has green check marks.",
     "steps": ["เขียน Test Plan 8 หัวข้อ และ Test Case รหัส TC-<กลุ่ม>-<เลข> ทุกข้อมีขั้นตอน ผลที่คาดหวัง ที่มา (FR/BR) และระดับ P1–P3",
               "ผลที่คาดหวังต้อง **คำนวณจาก Requirement** ไม่ใช่จากที่เห็นบนเว็บ",
               "ผู้เขียนแผนคือ Claude ผู้ตรวจคือ Codex (`cyolo1`) ผ่านสกิล agent-team: ตรวจได้จริงไหม ตัวเลขถูกไหม กำกวมไหม ซ้ำไหม",
               "บันทึกผลตรวจไว้ที่ `PLAN-REVIEW.md` แล้วแก้แผนตามข้อที่รุนแรงสูง"]},
]

PHOTOS = [
    {"img": "s01-build", "scene": "A small software team office at dusk: two developers at a desk with several laptops and monitors "
                                  "showing blurred abstract code, a compact server rack with glowing green lights on the right, "
                                  "a white construction hardhat resting on a shelf. Mood: a system being built."},
    {"img": "s02-verify", "scene": "A quality-assurance engineer sits at a desk on the right, looking closely at a laptop with a blurred "
                                   "web page and a tablet showing a blurred construction-site photo, a printed checklist with pen "
                                   "marks beside them. Mood: careful checking before delivery to a customer."},
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

# ------------------------------------------------------------------ รอบที่ 2: ภาพอธิบายแบบตำราและภาพถ่ายฉาก
# FIGS2  = ภาพอธิบายแบบเรียบ (flat) มีป้ายสั้นในภาพ · ใช้กับสไลด์ภาพใหญ่ + ประเด็น 2-3 ข้อ
# PHOTOS2 = ภาพถ่ายฉากเหตุการณ์ (ไม่มีตัวอักษร) · ใช้กับสไลด์ประโยคเดียวบนภาพ
# ภาพที่มีตัวเลข: ตัวเลขทุกตัวมาจาก README.md และถูกตรวจย้อนกลับใน numbers.md ของงานตรวจภาพ

FIGS2 = [
    {"img": "n21-conflict", "ratio": "4:3",
     "labels": ["ผู้จัดการความปลอดภัย", "หัวหน้างานไซต์", "ฝ่ายไอที", "ผลภายในครึ่งนาที", "รอได้ 5 นาที", "GPU ใบเดียว", "ระบบเดียว"],
     "scene": "Three rounded panels across the top, each with a simple flat portrait of one customer: left a man in his late 40s "
              "with a white hardhat and reflective vest (label ผู้จัดการความปลอดภัย), middle a woman about 30 with a yellow hardhat "
              "and reflective vest (label หัวหน้างานไซต์), right a man in his mid 30s with glasses and a light-blue shirt (label ฝ่ายไอที). "
              "Under each portrait one demand with a simple icon: a stopwatch (label ผลภายในครึ่งนาที), a queue of photo cards with a "
              "clock (label รอได้ 5 นาที), a single graphics card (label GPU ใบเดียว). From each demand a thick arrow pulls on one "
              "central box at the bottom (label ระบบเดียว) in a different direction; the box shows small strain lines."},
    {"img": "n22-yolo-io", "ratio": "16:9",
     "labels": ["Input", "ภาพ 640 × 640", "YOLO11s", "Output", "กรอบ + ชื่อคลาส + ค่าความมั่นใจ", "NO-Hardhat", "NO-Safety Vest",
                "H = จำนวน NO-Hardhat", "V = จำนวน NO-Safety Vest"],
     "scene": "Left: a square construction-site photo of three workers (label Input, sub-label ภาพ 640 × 640). A thick arrow to a "
              "central rounded model block (label YOLO11s; spell it as the four capital LETTERS Y, O, L, O followed by the two DIGITS 1, 1 and a lowercase s: both O are the round LETTER O, never a zero; write this label in the same wide bold sans-serif font as the words Input and Output, NOT in a monospace font, so each O is a wide circle). A thick arrow to the right: the same photo with coloured bounding boxes "
              "(label Output, sub-label กรอบ + ชื่อคลาส + ค่าความมั่นใจ): one red box around a worker's bare head tagged NO-Hardhat, "
              "one orange box around a worker's torso without a vest tagged NO-Safety Vest, the other workers with neutral grey boxes "
              "and no tags. Below the output photo a small counter panel with two lines: H = จำนวน NO-Hardhat and V = จำนวน NO-Safety Vest."},
    {"img": "n23-roles", "ratio": "4:3",
     "labels": ["คน: ตัดสินใจ", "Claude Code: หัวหน้าทีม", "Agent Team: เขียนโค้ด", "Claude", "Claude", "Codex", "ตรวจไขว้ข้าม CLI"],
     "scene": "Three horizontal tiers from top to bottom connected by downward arrows. Top tier: a person at a desk pressing a green "
              "approval stamp on a plan sheet (label คน: ตัดสินใจ). Middle tier: one terminal window with a lead icon that sends task "
              "cards downward (label Claude Code: หัวหน้าทีม). Bottom tier: three laptops side by side (label Agent Team: เขียนโค้ด); "
              "small name tags on the laptops: Claude, Claude, Codex. A curved two-way arrow between the second Claude laptop and the "
              "Codex laptop (label ตรวจไขว้ข้าม CLI)."},
    {"img": "n24-setup", "ratio": "16:9",
     "labels": ["1 โฟลเดอร์เริ่มต้น", "INTERVIEW.md", ".env", "2 Claude Code", "3 container multi-account", "yolo2", "yolo3", "cyolo1",
                "4 playwright-cli"],
     "scene": "Four items left to right, each on a light card with a numbered circle badge. Card 1: an open folder with exactly two "
              "file icons named INTERVIEW.md and .env. Card 2: a terminal window with a prompt cursor. Card 3: a container box holding "
              "three small account cards named yolo2, yolo3, cyolo1. Card 4: a browser window with a small automation cursor icon."},
    {"img": "n25-trace", "ratio": "16:9",
     "labels": ["1 INTERVIEW.md", "ลูกค้าพูดว่าอะไร", "2 USER-STORIES.md", "ใครต้องการอะไร", "3 REQUIREMENTS.md", "ระบบต้องทำอะไร",
                "4 DESIGN.md", "ระบบมีส่วนใดบ้าง"],
     "scene": "Four document columns left to right with numbered badges 1 to 4, each column a large document icon with its file name "
              "and a short question underneath. Column 1 shows a speech bubble; column 2 a story card; column 3 a card with a ruler "
              "icon; column 4 a small block diagram. One continuous orange trace line runs from the speech bubble through one card in "
              "each column to the block diagram, showing that every item can be traced back to the customer's words. Thin grey lines "
              "link other items."},
    {"img": "n26-recall", "ratio": "16:9",
     "labels": ["รูปที่มีคนไม่ใส่หมวก 10 รูป", "จับได้ 8 รูป", "จับพลาด", "Recall = 8 ÷ 10 = 0.80", "นับทีละรูป"],
     "scene": "On the left a neat grid of exactly 10 photo thumbnails in 2 rows of 5; every thumbnail shows one worker without a "
              "hardhat. Exactly 8 thumbnails have a red frame and a small red check badge; exactly 2 thumbnails (the last two of the "
              "bottom row) have a grey dashed frame. Group label above the grid: รูปที่มีคนไม่ใส่หมวก 10 รูป. Label beside the red ones: "
              "จับได้ 8 รูป. Label beside the grey ones: จับพลาด. On the right a clean formula card: Recall = 8 ÷ 10 = 0.80, and under "
              "it a small tag นับทีละรูป."},
    {"img": "n27-req-kinds", "ratio": "4:3",
     "labels": ["User Story", "FR · ระบบต้องทำอะไร", "BR · กติกาเป็นตัวเลข", "NFR · ต้องดีแค่ไหน", "ข้อสมมติ · ต้องให้ลูกค้ายืนยัน"],
     "scene": "On the left a stack of story cards (label User Story). Three arrows fan out to three tall containers side by side: "
              "first with an icon of photos being uploaded and a gear (label FR · ระบบต้องทำอะไร), second with a ruler and a red "
              "boundary line (label BR · กติกาเป็นตัวเลข), third with a stopwatch and a shield (label NFR · ต้องดีแค่ไหน). Below the "
              "containers an amber sticky note with a question mark (label ข้อสมมติ · ต้องให้ลูกค้ายืนยัน)."},
    {"img": "n28-mock", "ratio": "16:9",
     "labels": ["dispatcher", "AI_MODE=mock", "mock-gateway", "คืนผลตามชื่อไฟล์", "เครื่อง GPU ที่เช่า", "ไม่ต้องเช่าเครื่องเพื่อทดสอบกติกา"],
     "scene": "On the left a service box (label dispatcher) with a toggle switch (label AI_MODE=mock). Two paths go to the right. "
              "The upper path is bold and leads to a simple test-double box drawn with a dashed outline (label mock-gateway) that "
              "returns a result card immediately; the result card shows a file icon whose name decides the result (label "
              "คืนผลตามชื่อไฟล์). The lower path is faded and leads to a server rack with a graphics card and a coin icon (label "
              "เครื่อง GPU ที่เช่า). A green banner along the bottom (label ไม่ต้องเช่าเครื่องเพื่อทดสอบกติกา)."},
    {"img": "n30-run-team", "ratio": "16:9",
     "labels": ["อนุมัติให้รันจริง", "หัวหน้าทีม", "yolo2", "yolo3", "cyolo1", "./app", "แผนเทียบของจริง", "ห้ามเขียนโค้ดแทนทีม"],
     "scene": "Left: a person presses a green stamp on a plan sheet (label อนุมัติให้รันจริง). Centre: a lead terminal (label หัวหน้าทีม) "
              "sends task block cards along arrows to three laptops named yolo2, yolo3, cyolo1. Right: an output folder (label ./app) "
              "and a report sheet showing a plain two-column table with blank grey rows, NO bars, NO chart and NO numbers "
              "(label แผนเทียบของจริง). Near the lead a small red "
              "prohibition sign over a keyboard (label ห้ามเขียนโค้ดแทนทีม)."},
    {"img": "n33-rent-dataset", "ratio": "16:9",
     "labels": ["1 เช่าเครื่อง GPU", "e2e-sitesafe", "RTX 3090", "2 ดาวน์โหลด Dataset", "construction-site-safety", "3 แบ่ง 3 ชุด",
                "Training Set", "Validation Set", "Test Set"],
     "scene": "Three numbered stages left to right. Stage 1: a rented server rack with a graphics card and a luggage-style tag "
              "(tag text e2e-sitesafe), a small chip label RTX 3090. Stage 2: a cloud with a download arrow into a folder of "
              "construction photos (folder label construction-site-safety). Stage 3: the folder split into three folders of clearly "
              "different sizes, the first much larger than the others: Training Set (large), Validation Set (small), Test Set (small)."},
    {"img": "n34-bottleneck", "ratio": "16:9",
     "labels": ["ผู้ใช้รอ 2.4–8.9 วินาที", "dispatcher ส่งทีละรูป", "คอขวด", "GPU 22 มิลลิวินาทีต่อรูป"],
     "scene": "A left-to-right pipeline. Left: a supervisor at a laptop with an hourglass (label ผู้ใช้รอ 2.4–8.9 วินาที). Middle: a "
              "narrow doorway where a service box passes photo cards one at a time while several cards wait in line (label dispatcher "
              "ส่งทีละรูป); an orange marker on the narrow doorway (label คอขวด). Right: a fast GPU worker with a lightning icon and "
              "an idle waiting gesture (label GPU 22 มิลลิวินาทีต่อรูป)."},
    {"img": "n35-explore", "ratio": "16:9",
     "labels": ["Test Charter", "session ของตัวเอง", "บัญชีทดสอบของตัวเอง", "ผลที่คาดหวัง (เขียนก่อนลอง)", "ผลจริง", "EXPLORATION.md"],
     "scene": "Four identical small AI explorers side by side, each at its own separate browser window and holding its own key card. "
              "Above the four a single label Test Charter pointing to a charter card held by each. One explorer is enlarged in front "
              "with labels: its browser (session ของตัวเอง), its key card (บัญชีทดสอบของตัวเอง), and a notepad with two sections, the "
              "upper section filled first (ผลที่คาดหวัง (เขียนก่อนลอง)) and the lower section with check, warning and cross icons "
              "(ผลจริง). At the bottom arrows from all four notepads merge into one report (label EXPLORATION.md)."},
    {"img": "n37-triage", "ratio": "16:9",
     "labels": ["Test Case ที่ล้ม", "เว็บผิด", "แผนผิด", "เทสต์ผิด", "แก้เทสต์แล้วรันซ้ำ", "ห้ามแก้ผลที่คาดหวังให้ตรงกับเว็บ"],
     "scene": "On the left a pile of red test cards with cross marks (label Test Case ที่ล้ม) entering a sorting funnel. Three bins "
              "on the right: a red bin with a bug icon (label เว็บผิด), an amber bin with a document icon (label แผนผิด), a blue bin "
              "with a wrench icon (label เทสต์ผิด) and an arrow from it looping back (label แก้เทสต์แล้วรันซ้ำ). Along the bottom a "
              "red prohibition sign over a pencil editing an expected-result sheet (label ห้ามแก้ผลที่คาดหวังให้ตรงกับเว็บ)."},
    {"img": "n38-bug-mode", "ratio": "16:9",
     "labels": ["BUG_MODE=1", "บั๊กที่ซ่อนไว้", "Playwright Test ชุดเดิม", "BUGS-SECRET.md", "เปิดหลังเขียนรายงานบั๊กเสร็จ"],
     "scene": "Left: a web server with a toggle switch turned on (label BUG_MODE=1). Behind a half-open curtain on the server three "
              "small beetle icons (label บั๊กที่ซ่อนไว้). Centre: a stack of test cards (label Playwright Test ชุดเดิม) with an arrow "
              "pointing LEFT into the server; the scan beam starts at the test cards and ends at the server. Far right, clearly separate "
              "and NOT connected to anything by lines, arrows or beams: a sealed envelope with a padlock (label BUGS-SECRET.md) and a small "
              "note pinned to it (label เปิดหลังเขียนรายงานบั๊กเสร็จ). Plain white background, no buildings or people."},
    {"img": "n40-skill", "ratio": "16:9",
     "labels": ["agent-team-delivery", "SKILL.md", "references/phases.md", "references/lessons.md", "ถามคนก่อนรันทีมจริง",
                "ถามคนก่อนเช่าเครื่อง"],
     "scene": "Left: one folder (label agent-team-delivery) with three file cards fanned out: SKILL.md (steps icon), "
              "references/phases.md (terminal icon), references/lessons.md (warning-triangle icon). Right: a road with four milestone "
              "flags A, B, C, D; between B and C a stop gate with a raised hand icon (label ถามคนก่อนรันทีมจริง), and in the middle of "
              "C before a server icon a second stop gate (label ถามคนก่อนเช่าเครื่อง)."},
]

PHOTOS2 = [
    {"img": "p21-question", "scene": "Dusk at a Bangkok high-rise construction site seen from inside a site-office container: a safety "
                                     "manager in his late 40s wearing a white hardhat and reflective vest stands at the window holding a "
                                     "tablet, looking out at the steel frame, cranes and small distant workers. Calm, thoughtful mood. "
                                     "Keep the lower third of the frame calm and dark."},
    {"img": "p22-report", "scene": "Inside a site-office meeting room: two software developers present a printed report to two clients "
                                   "from a construction company (one in a white hardhat, one in a reflective vest). The report pages have "
                                   "blurred tables and several red pen marks. The clients read carefully with serious faces. A laptop "
                                   "with a blurred screen on the table. Keep the lower third of the frame calm and dark."},
    {"img": "p23-lessons", "scene": "A small software team office in the evening: a team lead and an engineer stand at a whiteboard "
                                    "covered with blurred sticky notes and hand-drawn boxes and arrows, reviewing a finished project "
                                    "together; a white hardhat on the desk in the foreground. Reflective, honest mood."},
]

ILLUS = """Generate ONE clean explanatory illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

Style: a flat, modern textbook figure. White or very light grey background, clean vector shapes, thin dark-navy outlines,
generous white space, soft shadows only. Colour palette: navy #12305e, teal #0f8f8c, orange #e87f1c, red #c92a2a,
green #15803d, light greys. Numbered circle badges in navy where order matters. Simple flat human figures (adult, fictional)
and objects; NOT childish, no cartoon faces with big eyes, no mascots, no decorative clutter. No title banner.

Canvas: landscape {ratio}. Setting of the story: {setting}.

What the figure shows: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the labels above.
- When a label starts with a number followed by a space (for example "3 gate"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Text must be large, bold and easy to read from the back of a classroom. File names and code-like labels use a monospace font.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

PHOTO2 = """Generate ONE photorealistic image with your image generation tool and save it as a JPG file at exactly this path:
{out}/{img}.jpg

Scene: {scene}

Requirements:
- Photorealistic, natural light, shallow depth of field, landscape 16:9 (about 1920x1080).
- Setting: {setting}.
- People are fictional adults of Thai appearance; no real person's likeness.
- NO readable text anywhere: no letters, no numbers, no logos, no signs, no watermarks. Screens and papers must be blurred or abstract.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""


def write_v2(out, names=None):
    os.makedirs(out, exist_ok=True)
    n = 0
    for f in FIGS2:
        if names and f["img"] not in names:
            continue
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(ILLUS.format(
            out=out, img=f["img"], ratio=f["ratio"], setting=SETTING, scene=f["scene"], labels="\n".join(f["labels"])))
        n += 1
    for f in PHOTOS2:
        if names and f["img"] not in names:
            continue
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO2.format(out=out, img=f["img"], setting=SETTING, scene=f["scene"]))
        n += 1
    print("%d พรอมต์ (รอบที่ 2) -> %s" % (n, out))


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "--v2":
    write_v2(os.path.abspath(sys.argv[1]).replace("\\", "/"), sys.argv[3:])
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
