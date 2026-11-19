#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ LAB 7 (แชทบอท LLM: GPU 1 ใบคุยพร้อมกันได้กี่คน)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล)
  title  หัวข้อของสไลด์ และข้อความบนป้ายชื่อของภาพ
  labels ข้อความสั้นบนภาพ (ป้ายที่เป็นขั้นตอนขึ้นต้นด้วยเลข)
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ
  steps  ขั้นตอนข้างภาพ 3-5 ขั้น · เรียบเรียงจาก README.md ของบท
PHOTOS = ภาพถ่ายสมจริงของหน้าคั่น (ไม่มีตัวอักษรในภาพ · ฝั่งซ้ายมืดไว้วางหัวข้อ)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
"""
import os, sys

SETTING = ('a Thai home-goods shop that runs a customer chatbot: the shop owner and a developer in a small back office with a laptop, '
           'customers chatting on smartphones, and a rented remote GPU server with two RTX 3090 graphics cards in a data center')

FIGS = [
    {"img": "n01-step1-rent", "title": "ขั้นที่ 1 · เช่าเครื่อง RTX 3090 2 ใบตามเกณฑ์",
     "labels": ["1 กรองเครื่องตามเกณฑ์", "2 เลือกเครื่องที่ถูกที่สุด", "3 รอจนเครื่องพร้อม", "4 ตรวจอุณหภูมิ GPU",
                "≤ $0.60 ต่อชั่วโมง", "ไม่เกิน 60°C", "vapp-lab7"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a funnel filtering many server cards down to a few, a robot "
              "holding a checklist; (2) a price tag on the cheapest server card with the label '≤ $0.60 ต่อชั่วโมง' and a name tag 'vapp-lab7'; "
              "(3) a server powering on with an hourglass, two GPU cards visible inside; (4) a thermometer next to the two GPU cards "
              "with the label 'ไม่เกิน 60°C'.",
     "steps": ["**กรองเครื่อง**: verified, reliability 0.95 ขึ้นไป, เน็ตขาเข้า 500 Mbps ขึ้นไป, CPU 16 cores ขึ้นไป, CUDA 13 ขึ้นไป และไม่อยู่ในจีน",
               "**เลือกเครื่องที่ถูกที่สุด** ราคารวมไม่เกิน $0.60 ต่อชั่วโมง ตั้งป้าย `vapp-lab7`",
               "**รอจนเครื่องพร้อม** และเห็น GPU ครบ 2 ใบ ถ้าเกิน 10 นาทีให้ลบแล้วเช่าเครื่องอื่น",
               "**ตรวจอุณหภูมิตอนว่าง**: ใบไหนเกิน 60°C ให้เปลี่ยนเครื่อง (GPU ที่ร้อนจะลดความเร็วตัวเองระหว่างวัด)",
               "เช่า **2 ใบตั้งแต่แรก** เพื่อให้ทุกแบบวัดบนเครื่องเดียวกัน"]},
    {"img": "n02-step2-serve", "title": "ขั้นที่ 2 · เปิดแชทบอท shop-bot บน GPU 1 ใบ",
     "labels": ["1 ติดตั้ง vLLM + NGINX", "2 ดาวน์โหลดโมเดล", "3 cluster.sh", "4 ทดสอบ 2 คำถาม", "NGINX :8000", "API key", "401"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a robot installing two boxes labelled vLLM and NGINX onto a server; "
              "(2) a big download arrow bringing a model file into the server; (3) a script document named 'cluster.sh' with start, stop and "
              "status switches; (4) a customer phone sending a chat bubble through a gate labelled 'NGINX :8000' that checks a key card "
              "labelled 'API key', while a second request without a key is blocked with a red sign '401'.",
     "steps": ["**ติดตั้ง** vLLM, NGINX และ C compiler แล้วดาวน์โหลด Qwen3-4B-Instruct-2507 ด้วย `HF_TOKEN` (ห้ามทิ้ง token ไว้บนเครื่องเช่า)",
               "**เขียน `cluster.sh`** สำหรับเปิด ปิด และดูสถานะ vLLM 1 หรือ 2 ตัว ตัวละ 1 GPU ชื่อโมเดล `shop-bot` บริบท 4096 token",
               "**NGINX พอร์ต 8000** ใช้ API key แจกงานแบบ least_conn หรือ round robin และส่ง token ต่อทันทีแบบ streaming",
               "**ทดสอบ** ถาม 2 ข้อพร้อม key และเรียกแบบไม่มี key ต้องถูกปฏิเสธ"]},
    {"img": "n03-step3-loadtest", "title": "ขั้นที่ 3 · ตัวยิงโหลดจำลองผู้ใช้ N คนแบบ closed-loop",
     "labels": ["1 ถาม", "2 รอคำตอบจนจบ", "3 ถามข้อใหม่ทันที", "ผู้ใช้จำลอง N คน", "40 คำถาม", "ระดับละ 30 วินาที", "ผ่าน SLO?"],
     "scene": "Left: a circular loop of three numbered stations around a simulated user with a phone: (1) sending a question bubble, "
              "(2) waiting while answer tokens stream in, (3) immediately sending a new question. Behind it a crowd of identical simulated "
              "users labelled 'ผู้ใช้จำลอง N คน' and a jar of question cards labelled '40 คำถาม'. Right: a staircase of load levels with a stopwatch "
              "labelled 'ระดับละ 30 วินาที' and a judge robot holding a sign 'ผ่าน SLO?'.",
     "steps": ["**ผู้ใช้จำลอง N คน** แต่ละคนถาม รอคำตอบแบบ streaming จนจบ แล้วถามข้อใหม่ทันที",
               "**คำถาม 40 ข้อ** ของลูกค้าร้านขายของใช้ในบ้าน สุ่มถาม ตอบไม่เกิน 150 token",
               "**ไล่ N ทีละระดับ** ระดับละ 30 วินาที ไม่นับ 5 วินาทีแรก และหยุดเองเมื่อไม่ผ่าน SLO 2 ระดับติดกัน",
               "**วัดต่อระดับ**: TTFT p50/p95/p99, ความเร็วต่อผู้ใช้ p50/p5, token/วินาทีรวม, error และสถานะ GPU",
               "**Baseline**: เปิดแชทบอทแบบตอบทีละคำถาม แล้วยิงด้วย N = 1, 2, 3, 4, 6, 8"]},
    {"img": "n04-step7-destroy", "title": "ขั้นที่ 7 · ตรวจไฟล์ ลบเครื่อง แล้วอ่านใบแจ้งหนี้",
     "labels": ["1 ตรวจโค้ดและผล", "2 ลบเครื่อง vapp-lab7", "3 อ่านใบแจ้งหนี้", "code/", "results/", "GPU", "Disk", "รับส่งข้อมูล"],
     "scene": "Three numbered panels left to right connected by arrows: (1) a developer checking two folders labelled 'code/' and 'results/' "
              "on a laptop with a magnifying glass; (2) the robot switching off the GPU server and moving it to a recycle bin; "
              "(3) a paper invoice with three line items labelled 'GPU', 'Disk' and 'รับส่งข้อมูล' (no amounts) being read by the shop owner.",
     "steps": ["**ตรวจไฟล์**: โค้ดทุกไฟล์อยู่ใน `lab7_llm_chat/code` และ `metrics.json` กับกราฟอยู่ใน `lab7_llm_chat/results` ถ้ายังไม่ครบให้คัดลอกมาก่อน",
               "**ลบเครื่องป้าย `vapp-lab7`** แล้วตรวจว่าไม่มีเครื่องป้ายนี้ค้างในบัญชี (ห้ามแตะเครื่องป้ายอื่น)",
               "**สรุปค่าใช้จ่ายจริง**: อายุเครื่อง ราคาต่อชั่วโมง และยอดที่ถูกคิดแยกเป็น GPU, disk และรับส่งข้อมูล"]},
    {"img": "n05-step9-skill", "title": "ขั้นที่ 9 · สกิล v0 ทำงานทั้ง LAB ในพรอมต์เดียว",
     "labels": ["1 เช่า RTX 3090 1 ใบ", "2 ติดตั้งและเปิดแชทบอท", "3 ตรวจ GPU", "4 ยิงโหลด 2 แบบ", "5 ลบเครื่องและอ่านบิล",
                "scripts/", "SKILL.md"],
     "scene": "A developer types one short message into a laptop; a booklet labelled 'SKILL.md' and a toolbox labelled 'scripts/' feed the robot. "
              "From the laptop a path runs through five numbered stations: (1) renting one GPU server card, (2) a server with a chat bubble, "
              "(3) a thermometer and speed gauge on the GPU, (4) two load meters side by side, (5) a recycle bin and a receipt.",
     "steps": ["**เช่า** RTX 3090 1 ใบ ราคาไม่เกิน $0.30 ต่อชั่วโมง ป้าย `vapp-lab7-skill`",
               "**ติดตั้ง เปิดแชทบอท และตรวจ GPU** ด้วยโค้ดใน `scripts/` ไม่ต้องเขียนใหม่",
               "**ยิงโหลด 2 แบบ**: ทีละคำถาม และ Continuous Batching (ไม่ต้องวัด 2 GPU)",
               "**สรุปผล ลบเครื่อง และอ่านบิล** โดยเก็บผลที่ `results/skill_v0_run` ไม่เขียนทับผลเดิม"]},
]

PHOTOS = [
    {"img": "s01-theory", "scene": "The owner of a small Thai home-goods shop stands behind the counter holding a smartphone that shows many "
                                   "incoming chat bubbles (abstract shapes only), shelves of household products softly blurred behind. "
                                   "Mood: many customers asking at the same time."},
    {"img": "s02-lab", "scene": "Close-up inside a data center: an open rack server with two large graphics cards, small status lights, "
                                "cool blue and warm light mixed, a laptop on a cart in the foreground right. Mood: a rented GPU machine ready for a test."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, light pastel background, rounded title banner, thick outlines, rounded cards, numbered circle badges,
same palette, bold rounded Thai lettering):
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
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, ports, status codes) use a monospace font.
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

# ------------------------------------------------------------------ รอบที่ 2: ภาพอธิบายที่มีป้ายในภาพ (แทนสไลด์การ์ดข้อความ)
# label ทุกตัวคัดจาก README.md · ภาพที่มีตัวเลขมีบันทึกตรวจตัวเลขใน C:/t/slides_fanout/lab7/numbers.md
FIGS2 = [
    {"img": "n21-roadmap", "title": "บทนี้มี 4 ส่วน",
     "labels": ["1 โจทย์ ข้อมูล และโมเดล", "2 ทฤษฎีที่ต้องรู้", "3 LAB เช่าเครื่อง วัด และลบเครื่อง", "4 สกิล v0 และสรุป"],
     "scene": "A winding road seen from above with four numbered stations, left to right: (1) a small shop counter with a chatbot phone and a "
              "model chip; (2) an open textbook with a simple graph; (3) a rented GPU server with a stopwatch and a load meter; "
              "(4) a toolbox and a summary chart on a board. A small robot walks along the road."},
    {"img": "n22-howto", "title": "วิธีใช้สไลด์",
     "labels": ["→ หรือ Space หน้าถัดไป", "← หน้าก่อนหน้า", "O สารบัญ", "F เต็มจอ", "คลิกภาพเพื่อขยาย", "คัดลอกพรอมต์", "ติ๊กตรวจผล"],
     "scene": "A large laptop showing a slide. Around it: big keyboard keycaps (right arrow, Space, left arrow, O, F) each with its label; "
              "a mouse pointer clicking a picture that grows larger; an orange button with a copy icon; a checklist with tick boxes."},
    {"img": "n23-abc", "title": "วัด 3 แบบ บนเครื่องเดียวกัน ด้วยเกณฑ์เดียวกัน",
     "labels": ["A ตอบทีละคำถาม", "B Continuous Batching", "C Load Balancer", "GPU 1 ใบ", "GPU 1 ใบ", "NGINX + GPU 2 ใบ"],
     "scene": "Three side-by-side panels with letter badges A, B, C. (A) one GPU card serving one customer while others wait in a line; "
              "(B) the same single GPU card serving many customers at once, their chat bubbles merged into one wide lane; "
              "(C) a gate labelled NGINX splitting customers to two GPU cards. Under each panel a small tag with the GPU count label. "
              "One long ribbon below all three panels showing the same ruler icon (same criteria)."},
    {"img": "n24-workload", "title": "ข้อมูลที่ใช้ทดสอบคือชุดคำขอ (workload)",
     "labels": ["40 คำถาม", "ผู้ใช้จำลองสุ่มถามทีละข้อ", "คำตอบเฉลี่ยราว 84 token", "เพดาน 150 token", "ขั้นที่ 6: 20% ขอคำตอบยาวถึง 600 token"],
     "scene": "Left: a glass jar full of small question cards (Thai household products: dish soap, tissue, mop icons) labelled with the "
              "question count. Middle: simulated users drawing a card at random and sending it to a chatbot phone. Right: an answer "
              "chat bubble with a length bar that stops well before a dashed ceiling line; the ceiling line has its label. Bottom right, a "
              "separate small inset: one in five answer bubbles is much longer, with the step-6 label."},
    {"img": "n25-request", "title": "คำขอ 1 รายการ ส่งไปที่ NGINX",
     "labels": ["POST /v1/chat/completions", "NGINX :8000", "Authorization: Bearer <API key>", "model: shop-bot",
                "messages: system + user", "max_tokens: 150", "stream: true", "ไม่มี key = 401"],
     "scene": "A simulated user on a phone sends one big open envelope towards a gate labelled 'NGINX :8000'. The envelope shows a neat list of "
              "fields as tags, one per line, in monospace: the Authorization line with a key icon, model, messages (two small bubbles: a "
              "shop-staff badge for system and a person for user), max_tokens, stream. On the side a second small envelope without a key "
              "is stopped at the gate by a red sign with its label."},
    {"img": "n26-length", "title": "ความจุขึ้นกับความยาวคำตอบ",
     "labels": ["คำตอบสั้น ราว 84 token", "ความจุสูง", "คำตอบยาวชนเพดาน 150 token", "ความจุต่ำลง", "งานจริงมีเอกสารยาวแนบมา", "ความจุต่ำลงอีก"],
     "scene": "Three rows, each a horizontal comparison. Row 1: a short answer bubble next to one GPU card serving a big crowd of small "
              "customer icons (green). Row 2: a long answer bubble reaching a dashed ceiling line next to the same GPU card serving fewer "
              "customers (orange). Row 3: a question carrying a thick document next to the same GPU card serving very few customers (red)."},
    {"img": "n27-ceilings", "title": "Continuous Batching มีเพดาน 2 ชั้น",
     "labels": ["เพดานที่ 1: ความเร็วต่อผู้ใช้ ≥ 15 token/วินาที", "ตกเกณฑ์หลัง N = 192", "เพดานที่ 2: ช่องของ vLLM 256 ช่องต่อ GPU",
                "เกิน 256 ช่องจึงเกิดคิว"],
     "scene": "A building cross-section with two ceilings stacked. Inside, one GPU card is a shared desk; customer icons fill the room. "
              "Lower ceiling (dashed orange line): a speed gauge for each customer that drops as the room fills, with a marker where it "
              "breaks. Upper ceiling (solid red line): a row of slot boxes that fill up; above the line a waiting queue of customers outside "
              "the door."},
    {"img": "n28-before", "title": "ก่อนเริ่ม LAB",
     "labels": ["1 ทำ LAB 0: เตรียม key 3 ตัว", "2 เปิด Claude Code ที่ 02_VastAi_Application", "3 เครื่องคิดเงินตั้งแต่ขั้นที่ 1 ถึง 7",
                "ห้ามข้ามขั้นที่ 7"],
     "scene": "Three numbered panels left to right: (1) three keys on a key ring on a desk; (2) a laptop with a folder icon open in a code "
              "window (the folder name as its label); (3) a rented GPU server with a running taxi-style meter and a coin stack; a red "
              "stop sign next to it carries the warning label."},
    {"img": "n29-step1-read", "title": "เงื่อนไขในพรอมต์มีผลกับราคาจริง",
     "labels": ["$0.326 ในจีน ตัดออกตามข้อ 3", "$0.369 ต่อชั่วโมง เครื่องที่เลือก", "GPU 0 48°C", "GPU 1 54°C", "เกณฑ์ไม่เกิน 60°C"],
     "scene": "Left: two server price cards side by side; the first card is crossed out with a red X and carries its label; the second card "
              "has a green tick and its label. Right: the chosen server opened, two GPU cards each with a thermometer and its label, and a "
              "dashed limit line on the thermometers with the criterion label."},
    {"img": "n30-step2-read", "title": "สิ่งที่เห็นจากการทดสอบแชทบอท",
     "labels": ["ผู้ใช้ 1 คน: ราว 84 token/วินาที", "คำตอบชนเพดาน 150 token จึงถูกตัด", "X-Served-By", "HF_TOKEN ไม่ค้างบนเครื่องเช่า"],
     "scene": "Four small scenes in a 2x2 grid: (top-left) a speedometer next to a GPU card with its label; (top-right) a long chat bubble cut "
              "off by scissors at a dashed ceiling line; (bottom-left) an answer envelope with a tag showing the header name in monospace "
              "pointing to one of two vLLM boxes; (bottom-right) a key token going back into a safe outside the rented server."},
    {"img": "n31-step9-read", "title": "RTX 3090 รุ่นเดียวกัน แต่ความจุต่างกัน",
     "labels": ["รอบหลัก", "รอบสกิล: จำกัดกำลังไฟ GPU", "84 token/วินาที", "192 คน", "71 token/วินาที", "160 คน"],
     "scene": "Two identical GPU cards side by side on pedestals. Left card: full power plug, a speedometer showing a high reading, a crowd "
              "of customer icons. Right card: a power plug with a limiter clamp on its cable, a speedometer with a lower reading, a "
              "smaller crowd. Each card has its round label above it; under each card the speed label and then the user-count label."},
    {"img": "n32-lessons-a", "title": "บทเรียนจากผลจริง (1)",
     "labels": ["1 GPU ใบเดิม เปลี่ยนแค่วิธีเสิร์ฟ", "2 GPU เต็ม ไม่ได้แปลว่าใช้คุ้ม", "3 สองโหมดตกเกณฑ์คนละข้อ", "TTFT", "ความเร็วต่อผู้ใช้"],
     "scene": "Three numbered panels: (1) a taxi carrying one passenger turning into a bus carrying many passengers, same GPU card on both; "
              "(2) a GPU utilization gauge pointing to full next to a small output pipe with few drops; (3) two gates side by side: one "
              "gate labelled TTFT blocks a long queue (one-at-a-time mode), the other gate labelled with the per-user speed blocks slow "
              "snails (batching mode)."},
    {"img": "n33-lessons-b", "title": "บทเรียนจากผลจริง (2)",
     "labels": ["4 least_conn เหมาะกับ streaming", "5 ค่ารับส่งข้อมูลสำคัญ", "6 วัดบนเครื่องที่จะใช้จริง"],
     "scene": "Three numbered panels: (4) a gate sending a new chat to the GPU card that has the shorter pile of unfinished work; "
              "(5) an invoice where the data-transfer line with a big download arrow is highlighted larger than the GPU line (no amounts); "
              "(6) a developer measuring an actual rented GPU server with a stopwatch and a ruler."},
    {"img": "n34-limits", "title": "ข้อจำกัด และสิ่งที่ยังไม่ผ่าน",
     "labels": ["1 ขั้นที่ 6 ไม่ผ่าน SLO", "2 3 ใบยังไม่ได้วัด", "3 ความละเอียดของขั้นบันได", "4 ทุกส่วนอยู่บนเครื่องเดียว",
                "5 งานจริงอาจหนักกว่า", "6 สกิล v0 ยังไม่สมบูรณ์"],
     "scene": "Six numbered panels in a 3x2 grid, calm and honest mood: (1) a red cross over a speed gauge below its line; (2) a third GPU "
              "card drawn only with a dashed outline; (3) a staircase with wide steps and a question mark between two steps; (4) one "
              "server box containing a gate, two GPU cards and a load generator together; (5) a chat bubble carrying a thick document; "
              "(6) a skill booklet with a small wrench and a list with some unticked boxes."},
]

PHOTOS2 = [
    {"img": "p21-result", "scene": "Evening in the back office of a small Thai home-goods shop: the shop owner and a developer sit together at a "
                                   "laptop, relieved and smiling slightly, the laptop screen is blurred and abstract; behind them shelves of "
                                   "household products and a phone with many abstract chat bubbles on the desk."},
]

CARTOON2 = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style (clean flat infographic with soft pastel
panels, rounded title banner, thick outlines, numbered circle badges, bold rounded Thai lettering, textbook-figure clarity):
{refs}

Canvas: landscape 4:3 (about 1448 x 1086). Setting: {setting}.
The figure must look like a figure from a well-made university textbook: clear, uncluttered, not childish, generous white space.

Title banner text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers, symbols and units stay exactly as they are.
- Each label appears exactly once. Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above.
- When a label starts with a single number or letter followed by a space (for example "3 gate" or "A gate"), draw that number or letter ONLY inside a circle badge and write the rest of the label next to it. Never show the same badge twice.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, ports, headers, fields) use a monospace font.
- People are fictional adults; at most a small white-and-teal robot may appear as the AI.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--v2":
        out = os.path.abspath(sys.argv[2]).replace("\\", "/")
        refs = [os.path.abspath(p).replace("\\", "/") for p in sys.argv[3:]]
        os.makedirs(out, exist_ok=True)
        for f in FIGS2:
            open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(CARTOON2.format(
                out=out, img=f["img"], refs="\n".join(refs), setting=SETTING, title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
        for f in PHOTOS2:
            open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=SETTING, scene=f["scene"]))
        print("%d พรอมต์ -> %s" % (len(FIGS2) + len(PHOTOS2), out))
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
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=SETTING, scene=f["scene"]))
    print("%d พรอมต์ -> %s" % (len(FIGS) + len(PHOTOS), out))
