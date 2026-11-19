#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ LAB 3 · QLoRA (ภาพการ์ตูนอธิบาย 6 ภาพ + ภาพถ่ายหน้าปกและหน้าคั่น 2 ภาพ)

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

SETTING = ('the world of "Sabaijai", a small fictional Thai massage shop in Chiang Mai (massage mats, herbal compress balls, '
           'orchids, a reception counter with a tablet showing a customer chat) whose customer chatbot runs on GPU servers '
           'rented by the hour from a cloud marketplace; a developer works on a laptop')

FIGS = [
    {"img": "n01-experiment", "title": "เทียบ 3 แขนด้วยตัววัดชุดเดียวกัน",
     "labels": ["A โมเดลครู 27B", "B Base 4B", "C Fine-tuned 4B + LoRA", "RTX 5090", "RTX 3090",
                "server เดียวกัน · prompt เดียวกัน", "Validation Set 85 คำตอบ", "ชุดทดสอบ 26 เคส"],
     "scene": "Three columns side by side, each with a letter badge A, B, C at the top. Column A: a big robot standing on a large "
              "GPU card labelled RTX 5090, slightly faded to show it is a reference result. Columns B and C: two small robots that "
              "stand together on ONE shared small GPU card labelled RTX 3090; the robot in C wears a small sticky note on its chest "
              "(the LoRA adapter). A bracket under B and C carries the label about the same server and prompt. At the bottom two "
              "measuring tools as signs: a long fine ruler (Validation Set) and a short ruler with a clipboard (26 test cases).",
     "steps": ["**A = โมเดลครู 27B** บน RTX 5090 · ผล 26/26 **อ้างจากบทที่แล้ว ไม่ได้รันซ้ำ**",
               "**B = โมเดลเล็ก Base** ตามที่โหลดมา (`qwen3-4b-base`)",
               "**C = โมเดลเล็ก + LoRA** (Rank 8, Alpha 16, 3 Epoch, learning rate 0.0002, seed 0)",
               "B กับ C อยู่บน **server เดียวกัน เว็บเดียวกัน prompt เดียวกัน**",
               "วัด 2 ชั้น: **Validation Set 85 คำตอบ** (temperature 0) และ **ชุดทดสอบ 26 เคส** ผ่านเว็บจริง + รันซ้ำ 5 รอบผ่าน API"]},
    {"img": "n02-step1-questions", "title": "ขั้นที่ 1: คำถามลูกค้าที่มีเงื่อนไขของคำตอบ",
     "labels": ["1 คัดลอกเว็บและชุดทดสอบเดิม", "2 แม่แบบประโยค + สุ่มชื่อ เบอร์ เวลา", "3 เงื่อนไขของคำตอบ",
                "4 ตรวจไม่ซ้ำชุดทดสอบ", "seed 2026", "questions.jsonl"],
     "scene": "Four numbered stations left to right connected by arrows. (1) Two folders (a web page icon and a checklist icon) "
              "being copied from an old shelf to a new desk. (2) A small machine that takes sentence template cards and random "
              "name/phone/clock tokens and prints customer chat bubbles; a small dice tag reads seed 2026. (3) Each chat bubble "
              "gets a small tag card attached (the answer condition). (4) A magnifying glass comparing the bubbles with a locked "
              "test-case clipboard behind a low wall. The finished bubbles drop into a file box labelled questions.jsonl.",
     "steps": ["**คัดลอกระบบเดิม**: เว็บแชทบอทมาเป็น `code/web` และชุดทดสอบ 26 เคสมาเป็น `code/e2e` โดยไม่แก้ต้นฉบับ",
               "**เขียน `make_questions.py`**: แม่แบบประโยค + สุ่มชื่อ เบอร์ บริการ วันเวลา · seed 2026",
               "**ทุกข้อความมีเงื่อนไขของคำตอบ** เช่น ต้องมีราคา 350 · ต้องมีแท็กจองที่ข้อมูลตรง · ต้องยังไม่มีแท็กจอง",
               "**ตรวจ Data Leakage**: ห้ามซ้ำหรือคล้ายข้อความของชุดทดสอบ (รวมปุ่มลัดบนหน้าแชท)",
               "ได้ไฟล์ `data/questions.jsonl` ซึ่งยังไม่มีคำตอบ · ขั้นนี้ยังไม่เช่าเครื่อง"]},
    {"img": "n03-step5-serve", "title": "ขั้นที่ 5: server เดียว มี 2 ชื่อโมเดล",
     "labels": ["1 vLLM โหลด Base ครั้งเดียว", "2 เสียบ LoRA Adapter", "qwen3-4b-base", "qwen3-4b-sabaijai",
                "3 eval_val.py", "Validation Set 85 คำตอบ", "RTX 3090"],
     "scene": "One server tower on a GPU card labelled RTX 3090 in the middle. Inside the tower, one big base model block is loaded "
              "once (badge 1). A small plug-in card (the LoRA adapter, badge 2) is inserted beside it. From the server two output "
              "doors with name plates: qwen3-4b-base and qwen3-4b-sabaijai. On the right, a robot inspector holding a clipboard "
              "labelled eval_val.py (badge 3) sends the same question cards to both doors and compares the answers, with a stack "
              "of cards labelled Validation Set 85 คำตอบ.",
     "steps": ["**`serve.sh`**: vLLM โหลด Base Model ครั้งเดียว แล้วลงทะเบียน Adapter เป็น **ชื่อโมเดลอีกชื่อ** บน server เดียวกัน",
               "2 ชื่อโมเดล: `qwen3-4b-base` (โมเดลเดิม) และ `qwen3-4b-sabaijai` (โมเดลเดิม + adapter) · พอร์ต 8000 · API key สุ่มใหม่",
               "**`eval_val.py`**: ทั้ง 2 โมเดลตอบทุกข้อความใน Validation Set ด้วยประวัติแชทเดียวกัน (temperature 0)",
               "ตรวจด้วยเงื่อนไขของคำตอบใน Dataset · วัดความเร็ว token ต่อวินาที และ VRAM · เก็บที่ `results/val_eval.json`"]},
    {"img": "n04-step6-web", "title": "ขั้นที่ 6: เว็บแชทบอทเลือกโมเดลได้",
     "labels": ["1 ตัวเลือก Base / Fine-tuned", "2 หน้า /compare", "3 สลับโมเดลเริ่มต้น", "PostgreSQL",
                "Docker · พอร์ต 3403", "เครื่องของเรา"],
     "scene": "A large laptop screen on the left (the developer's own machine, a small house-shaped sign) showing a chat web page "
              "with a two-option toggle at the top (badge 1). Next to it a second browser window split into two answer columns "
              "side by side with small stopwatch icons (badge 2, the compare page). A small switch lever (badge 3) on a control "
              "box changes which robot answers by default. Below, a container-ship style box (Docker) and a "
              "database cylinder labelled PostgreSQL. A cable runs from the laptop to a remote GPU server cloud on the right.",
     "steps": ["**หน้าแชทเดิม** เพิ่มตัวเลือกโมเดล Base / Fine-tuned · ไม่เลือก = ใช้โมเดลเริ่มต้นของเว็บ",
               "**หน้า `/compare`**: พิมพ์คำถาม 1 ข้อ เห็นคำตอบ 2 โมเดลคู่กัน พร้อมเวลา token ต่อวินาที และผลตรวจแท็กจอง",
               "**สลับโมเดลเริ่มต้นได้ขณะเว็บเปิด** (ชุดทดสอบใช้สลับ) โดยไม่เปลี่ยนส่วนที่ชุดทดสอบ 26 เคสใช้อยู่",
               "รันด้วย Docker Compose บน **เครื่องของเรา** project `vapp-lab3` พอร์ต 3403 · เว็บ + PostgreSQL ในคำสั่งเดียว"]},
    {"img": "n05-step7-e2e", "title": "ขั้นที่ 7: ชุดทดสอบ 26 เคสกับทั้ง 2 โมเดล",
     "labels": ["1 สลับโมเดลเริ่มต้น", "2 ล้างตารางจองและประวัติแชท", "3 Playwright รันชุดทดสอบ",
                "4 รันซ้ำ 5 รอบผ่าน API", "compare.json", "repeat.json"],
     "scene": "A loop of four numbered stations around a chat web page in the center. (1) A hand flips a switch between two robots. "
              "(2) A broom sweeping a booking table and old chat bubbles. (3) A robot arm typing on a browser window with a "
              "clipboard checklist of many ticks. (4) A circular repeat arrow drawn five times around a small terminal window "
              "without a browser. At the end two report sheets labelled compare.json and repeat.json.",
     "steps": ["**`run-both.sh`**: รันชุดทดสอบ 26 เคสกับ Base แล้วกับ Fine-tuned · รายงานแยกกัน",
               "ก่อนแต่ละรอบ **สลับโมเดลเริ่มต้นของเว็บ** และ **ล้างตารางจองกับประวัติแชท**",
               "**`compare.mjs`**: ตารางรายเคสว่าแต่ละโมเดลผ่านหรือไม่ พร้อมคำตอบจริงของเคสที่ผลต่างกัน",
               "**`repeat.mjs`**: รันโจทย์ 26 เคสเดิมซ้ำอีก 5 รอบต่อโมเดล ผ่าน API โดยไม่เปิดเบราว์เซอร์ เพื่อดูว่าผลแกว่งไหม"]},
    {"img": "n06-step8-cleanup", "title": "ขั้นที่ 8: ลบเครื่อง ปิดเว็บ เก็บไฟล์ให้ครบ",
     "labels": ["1 จดข้อมูลเครื่อง", "2 ลบเครื่อง vapp-lab3*", "3 ปิดเว็บ", "4 คัดลอกไฟล์กลับ", "ไม่มีเครื่องค้าง"],
     "scene": "Four numbered panels left to right. (1) A person writing on a notepad next to two rented GPU servers with price "
              "tags drawn as coin icons only. (2) The two servers going into a recycle bin. (3) A laptop with a web page being "
              "switched off with a power button. (4) Folders flying from a cloud container back into the laptop. A green ribbon "
              "at the bottom with a check mark and the label about no remaining machines.",
     "steps": ["**จดข้อมูลเครื่อง** ป้าย `vapp-lab3*` ก่อนลบ: GPU · ราคาต่อชั่วโมง · เวลาที่เปิด · ปริมาณดาวน์โหลด",
               "**ลบทุกเครื่อง** ป้ายขึ้นต้นด้วย `vapp-lab3` แล้วตรวจว่าไม่เหลือ · ห้ามแตะเครื่องป้ายอื่น",
               "**ปิดเว็บ** ใน `lab3_qlora/code/web` บนเครื่องของเรา",
               "**ตรวจไฟล์ครบ**: ไฟล์ที่ยังอยู่แค่ใน container ให้คัดลอกกลับมา · สรุปค่าเช่า (ราคาต่อชั่วโมง × ชั่วโมง + ค่าดาวน์โหลด)"]},
]

PHOTOS = [
    {"img": "s01-cover", "scene": "Inside a calm small Thai massage shop in the evening: on the right, a reception counter with a tablet "
                                  "standing on it (screen blurred, soft glow of a chat window) next to rolled towels, herbal compress balls "
                                  "and an orchid; behind it, softly lit massage mats. A laptop on the counter edge glows. Mood: a small "
                                  "business that wants a good chatbot at a low monthly cost."},
    {"img": "s02-lab", "scene": "A developer (fictional adult) at a desk at night seen from the side on the right of the frame, typing on a "
                                "laptop with abstract blurred terminal glow; beside the laptop on the desk sits a bare graphics card with "
                                "two fans, catching the light. The background on the left is a dark out-of-focus room. Mood: hands-on lab work."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, soft pastel rounded panels, thick dark outlines, cute white-and-blue robots for AI models, rounded title banner,
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
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, JSON, model names) use a monospace font.
- Characters: friendly fictional cartoon people and small white-and-blue robots that represent the AI models. Fictional cartoon characters only.

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

# ------------------------------------------------------------------ รอบที่ 2 (ภาพอธิบายแบบตำราเรียน n2x และภาพถ่าย p2x)
# nums = ตัวเลขผลการทดลองที่อยู่ในภาพ (ต้องตรวจย้อนกลับใน numbers.md)
FIGS2 = [
    {"img": "n21-plan", "title": "LAB นี้มี 4 ส่วน",
     "labels": ["1 ภาคพื้นฐาน", "2 ภาค LAB ขั้นที่ 1–8", "3 สกิลเวอร์ชัน 0", "4 สรุป",
                "โจทย์ · Dataset · โมเดล · ทฤษฎี", "เช่าเครื่อง · เทรน · วัดผล · ลบเครื่อง", "ทำซ้ำในคำสั่งเดียว", "ผลและข้อจำกัด"],
     "scene": "A gentle winding road seen from slightly above, with four numbered milestone stations along it from left to right. "
              "Station 1: an open textbook and a small chalkboard. Station 2: a workbench with a rented GPU server, a training "
              "progress chart and a trash bin for deleting the machine. Station 3: a recipe card being filed into a folder. "
              "Station 4: a finish flag beside a results board drawn with abstract bars only (no numbers). Under each station its "
              "short description label."},
    {"img": "n22-dataset-layers", "title": "Dataset สร้างเองใน 2 ชั้น",
     "labels": ["1 make_questions.py สร้างคำถาม", "2 โมเดลครูตอบ", "3 ตรวจด้วยเงื่อนไขของคำตอบ", "4 แบ่ง Training / Validation",
                "ทิ้งบทที่ผิด", "ชุดทดสอบ (Test) ไม่อยู่ใน Dataset"],
     "scene": "A clean left-to-right flow. (1) A script document icon prints customer chat bubbles, each bubble with a small tag "
              "card attached. (2) A large teacher robot writes an answer bubble under each question. (3) A checkpoint gate with a "
              "magnifying glass compares each answer with its tag card; rejected pairs fall into a bin labelled for discarded "
              "dialogs. (4) The accepted pairs split into two stacks, a big stack and a small stack. Separate on the far right, "
              "behind a low glass wall, a locked clipboard of test cases with its label."},
    {"img": "n23-record", "title": "ข้อมูล 1 รายการ",
     "labels": ["messages[0] system", "messages[1] user", "messages[2] assistant", "expects", "now",
                "has · not · lang · booking", "คำสั่งและข้อมูลร้าน", "ข้อความลูกค้า", "คำตอบของครู"],
     "scene": "One large paper card (a data record) shown like an exploded textbook diagram. Inside the card from top to bottom: "
              "a scroll icon for the system message, a customer chat bubble, and a robot answer bubble, each with its code label "
              "and a short Thai caption beside it. Clipped to the right edge of the card is a smaller tag card (expects) listing its "
              "four field names; on the top-right corner a small calendar-clock badge (now). Thin leader lines connect labels to parts."},
    {"img": "n24-before", "title": "ก่อนเริ่ม LAB",
     "labels": ["1 ทำ LAB 0 เตรียม key", "2 Claude Code ที่โฟลเดอร์ 02_VastAi_Application", "3 container multi-account",
                "4 Docker บนเครื่องของเรา", "ใช้กับเครื่องเช่า", "ใช้รันเว็บแชทบอท"],
     "scene": "A desk seen from the front with a laptop in the middle. Around it four numbered items: (1) a small key ring with "
              "three keys; (2) the laptop screen showing a terminal window and a folder icon; (3) a shipping-container shaped box "
              "connected by a cable to a cloud of rented GPU servers, with the label about rented machines; (4) a whale-free plain "
              "box icon for Docker sitting on the laptop side, connected to a small chat web page, with the label about the web chatbot."},
    {"img": "n25-count-check", "title": "ตรวจตัวเลขของ AI กับไฟล์",
     "labels": ["คำตอบของ AI: 993 ข้อความ", "นับจากไฟล์จริง: 998 ข้อความ", "questions.jsonl", "ตรวจเองทุกครั้ง"],
     "scene": "A fictional adult developer at a desk holds a printed report sheet from an AI assistant (a robot icon at its top) "
              "with one line of text, the first label, and looks at a file box labelled questions.jsonl with a counter display "
              "showing the second label. A magnifying glass sits between them and a small amber warning mark shows that the two "
              "values differ. A small badge at the bottom carries the last label.",
     "nums": [("993", "ข้อความ", "จำนวนข้อความลูกค้าที่ AI รายงานในคำตอบขั้นที่ 1", "README ขั้นที่ 1 · อ่านผลอย่างไร: \"คำตอบของรอบนี้รวมข้อความลูกค้าได้ 993\""),
              ("998", "ข้อความ", "จำนวนข้อความลูกค้าที่นับจากไฟล์ data/questions.jsonl", "README ขั้นที่ 1 · อ่านผลอย่างไร: \"นับได้จริง **998 ข้อความ**\" · metrics.json dataset.user_messages_total")]},
    {"img": "n26-step2-teacher", "title": "ขั้นที่ 2: เปิดโมเดลครูบนเครื่องเช่า",
     "labels": ["1 เช่า RTX 5090", "2 ติดตั้ง NInfer", "3 เปิดโมเดลครู 27B", "4 ลองถามจากนอกเครื่อง", "teacher.env"],
     "scene": "Four numbered stations left to right. (1) A cloud marketplace with one powerful GPU card being picked from a shelf. "
              "(2) A toolbox installing software onto that server. (3) A large teacher robot waking up inside the server. (4) A "
              "laptop outside the cloud sends a Thai chat bubble across a dotted line and receives an answer bubble. A small "
              "locked envelope file labelled teacher.env lies beside the laptop."},
    {"img": "n27-step3-dataset", "title": "ขั้นที่ 3: จากคำตอบของครูเป็น Dataset",
     "labels": ["1 ครูตอบทุกข้อความ", "2 ตรวจด้วยเงื่อนไข ผิดให้ตอบใหม่", "3 แบ่ง train.jsonl / val.jsonl", "4 dataset_samples.jpg",
                "5 ลบเครื่องครู"],
     "scene": "Five numbered stations along a conveyor belt. (1) The teacher robot answers a queue of question cards in parallel. "
              "(2) An inspection gate with a tag card checker; one card bounces back for a retry. (3) Two output trays with the file "
              "names. (4) A small framed sample sheet with table rows (no readable numbers). (5) The teacher's GPU server dropped "
              "into a recycle bin."},
    {"img": "n28-step4-train", "title": "ขั้นที่ 4: เทรน QLoRA บนเครื่องราคาถูก",
     "labels": ["1 เช่า RTX 3090", "2 train.py: Base 4-bit + LoRA", "3 วัด Validation loss เก็บ adapter ที่ดีที่สุด",
                "4 run.sh เทรนต่อเมื่อหลุด", "5 คัดลอกผลกลับ results/"],
     "scene": "Five numbered stations. (1) A modest GPU card picked from a cloud shelf. (2) A frozen blue base-model block with a "
              "small padlock and a bright small adapter card plugged on top. (3) A falling curve on a small chart with a circle "
              "marking the lowest point and a trophy-free simple star next to the saved adapter. (4) A broken network cable being "
              "reconnected with a resume arrow. (5) A folder flying from the cloud back to a laptop."},
    {"img": "n29-vram-reserved", "title": "VRAM ที่จองไว้ ไม่ใช่ VRAM ที่ใช้จริง",
     "labels": ["การ์ด 24 GB", "PyTorch จองไว้ 22.9 GB", "ใช้จริง: ไม่ได้วัด", "AI เลือกวิธีวัดเอง"],
     "scene": "A large horizontal memory bar drawn as a long GPU memory strip with the first label at its right end. One uniform "
              "light hatched block fills the bar from the left end to about 95% of its length (22.9 of 24), leaving only a thin "
              "empty sliver at the right end; the second label sits above the hatched block with a bracket. IMPORTANT: there is "
              "NO smaller solid block, NO inner bar and NO second fill level inside the hatched block - the hatched block is one "
              "single even area. Below the bar, separate from it, a small card with a big question mark and the third label, "
              "because the actually used amount was never measured. A small robot holding a measuring tape stands next to the "
              "card with the last label in a speech bubble.",
     "nums": [("24 GB", "GB", "VRAM ของการ์ด RTX 3090", "README ทฤษฎีข้อ 2: \"บนการ์ด 24 GB ที่เช่าได้ถูก\""),
              ("22.9 GB", "GB", "VRAM สูงสุดที่ PyTorch จองไว้ตอนเทรน", "README ขั้นที่ 4 · อ่านผลอย่างไร: \"**VRAM 22.9 GB เป็นค่าที่ PyTorch จองไว้**\" · metrics.json training.peak_vram_gb")]},
    {"img": "n30-booking-early", "title": "แท็กจองที่ออกผิดจังหวะคือการจองปลอม",
     "labels": ["ลูกค้า: ขอจอง 08:00", "ร้านยังไม่เปิด", "Base: รับจองและออกแท็ก", "Fine-tuned: ขอเวลาใหม่", "การจองปลอมในฐานข้อมูล"],
     "scene": "At the top a fictional adult customer, drawn as a PERSON (not a robot), holding a smartphone with a chat bubble (first label). Split picture below it, left and right of that customer bubble next to a shop door sign "
              "drawn as a closed shutter icon (second label). Left half, red accent: a robot stamps a booking card that drops into a "
              "database cylinder, marked with a red cross and the last label. Right half, green accent: a second robot wearing a small "
              "adapter card on its chest politely holds up a clock icon and asks for another time, with a green check.",
     "nums": [("08:00", "เวลา", "เวลาที่ลูกค้าขอจองในตัวอย่างจริง (ก่อนร้านเปิด)", "README ขั้นที่ 5 · อ่านผลอย่างไร: \"ลูกค้าขอจอง 08:00 ก่อนร้านเปิด\"")]},
    {"img": "n31-closed-refusal", "title": "โมเดลที่เทรนแล้วก็ยังผิดได้",
     "labels": ["1 ลูกค้า: จองพรุ่งนี้ 14:00", "2 Fine-tuned: ตอนนี้ร้านปิด", "3 ลูกค้ายืนยันอีกรอบ", "4 จองสำเร็จ"],
     "scene": "A tall smartphone-free chat panel drawn as a large chat window with four numbered message bubbles from top to bottom: "
              "a customer bubble, a robot bubble with a small amber warning triangle (a wrong refusal), a second customer bubble, and "
              "a robot bubble with a green booking card. A small calendar icon next to the first bubble shows tomorrow.",
     "nums": [("14:00", "เวลา", "เวลาที่ลูกค้าขอจองพรุ่งนี้ในการลองจองของขั้นที่ 6", "README ขั้นที่ 6 · อ่านผลอย่างไร: \"ลูกค้าขอจองพรุ่งนี้ 14:00\"")]},
    {"img": "n32-what-ft-taught", "title": "Fine-tune สอนสิ่งที่ Dataset สอน",
     "labels": ["สิ่งที่ Dataset สอน", "ลีลาการตอบ", "รูปแบบคำตอบ", "ระวังเรื่องการจอง", "สิ่งที่ Dataset ไม่ได้เน้น",
                "ตีความคำอ้างอิงข้ามข้อความ"],
     "scene": "Two panels side by side. Left panel (green accent): a small robot wearing an adapter card stands beside a stack of "
              "teacher answer sheets; three items with check marks list the second, third and fourth labels. Right panel (grey-amber "
              "accent): the same robot puzzled in front of three chat bubbles linked by a dotted arrow from the third bubble back to "
              "the first (a reference across messages), with a question mark and the last label."},
    {"img": "n33-same-round", "title": "เทียบ Base กับ Fine-tuned ในรอบเดียวกัน",
     "labels": ["รอบ 3 Epoch", "รอบสกิล v0 · 1 Epoch", "Base 87.1%", "Base 84.7%", "โมเดลเดียวกัน คะแนนต่างกัน"],
     "scene": "Two side-by-side round frames, like two lab sessions on two different days, each with its title label on top. In each "
              "frame the same small base robot stands on a podium with its score label on the podium. Between the frames an "
              "unequal sign and a ruler crossed out, meaning do not compare across rounds. A ribbon at the bottom with the last label.",
     "nums": [("87.1%", "%", "คำตอบที่ถูกของ Base บน Validation Set ในรอบ 3 Epoch (ขั้นที่ 5)", "README ขั้นที่ 10 · อ่านผลอย่างไร: \"Base ของสองรอบได้ไม่เท่ากัน (87.1% กับ 84.7%)\""),
              ("84.7%", "%", "คำตอบที่ถูกของ Base บน Validation Set ในรอบสกิล v0 (ขั้นที่ 10)", "README ขั้นที่ 10 · อ่านผลอย่างไร: \"(87.1% กับ 84.7%)\"")]},
    {"img": "n34-v0-fixes", "title": "สกิล v0 ยังต้องแก้ 5 จุด",
     "labels": ["1 ไม่ตรึงเวอร์ชันไลบรารี", "2 ไฟล์ LICENSE ทำให้โหมด offline ล้ม", "3 เครื่องอัปโหลดช้า",
                "4 ค่าอ้างอิงมาจากรอบเดียว", "5 ผูกกับร้านและโฟลเดอร์นี้"],
     "scene": "A recipe card (the skill file SKILL.md drawn as a card without readable body text) in the center, with five "
              "numbered sticky repair notes around it, each with a small icon: (1) a package box with a loose version tag; (2) a "
              "document with a broken plug icon; (3) a slow snail on an upload arrow; (4) a single measuring point on a small chart; "
              "(5) a chain linking the card to a shop sign and a folder. A small wrench lies beside the card."},
    {"img": "n35-lessons", "title": "สิ่งที่ได้เรียนจาก LAB นี้",
     "labels": ["1 ครูก็ผิดได้", "2 loss ต่ำไม่ได้แปลว่าตอบถูก", "3 ไม้บรรทัดต้องละเอียดพอ", "4 Fine-tune สอนสิ่งที่ Dataset สอน",
                "5 ตรวจตัวเลขของ AI กับไฟล์", "6 เงินเดินตามเวลาที่เครื่องเปิด"],
     "scene": "A tidy grid of six numbered picture tiles, 3 columns by 2 rows, each with one icon and its label: (1) a teacher robot "
              "with one wrong answer sheet in a filter; (2) a falling loss curve next to an answer sheet with a cross; (3) a coarse "
              "ruler next to a fine ruler; (4) a robot learning from a stack of answer sheets; (5) a magnifying glass over a file box; "
              "(6) a GPU server with a running coin meter drawn as coins only."},
]

PHOTOS2 = [
    {"img": "p21-shop", "scene": "Daytime inside a small Thai massage shop: a receptionist (fictional adult) at the counter answers a "
                                 "customer message on a tablet (screen blurred), while in the background a therapist prepares a "
                                 "massage mat. Warm wood, orchids, rolled towels. Mood: the real business the chatbot serves."},
    {"img": "p22-meter", "scene": "A rented GPU server in a dim data-center aisle, its front panel lit by small status lights; in the "
                                  "foreground on a metal shelf a plain analog stopwatch is running. Mood: time on this machine costs money."},
    {"img": "p23-skill", "scene": "A developer (fictional adult) at a tidy desk writes neat notes in a hardbound notebook next to an open "
                                  "laptop with an abstract blurred terminal glow; a cup of tea; calm morning light. Mood: turning finished "
                                  "work into a reusable recipe."},
    {"img": "p24-summary", "scene": "The owner of a small Thai massage shop (fictional adult) and a developer look together at a tablet at "
                                    "the reception counter in the evening (screen blurred), thoughtful and calm. Mood: reviewing the evidence "
                                    "before a decision."},
]

CLEAN = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

Look at these reference images first and keep their colour palette and their friendly white-and-blue robots for AI models:
{refs}
But draw this figure cleaner and more grown-up than the references: a flat, modern explanatory figure like one in a
well-made university textbook. Soft pastel panels, clear thin-to-medium outlines, generous white space, few elements,
numbered circle badges where order matters, no clutter, nothing childish.

Canvas: landscape 4:3 (about 1448 x 1086). Setting: {setting}.

Title banner text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above.
- When a label starts with a number followed by a space (for example "3 gate"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Numbers inside a label that does not start with a badge number (for example "Base 87.1%") must appear exactly once, exactly as written, attached to that label.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, JSON, model names) use a monospace font.
- People, if any, are fictional adults.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

PHOTO2 = PHOTO.replace("- Keep the left 45% of the frame calm and darker (out-of-focus background), main subject on the right side, because a title will be placed over the left side later.\n",
                       "- Keep the left 45% of the frame calm and darker (out-of-focus background), main subject on the right side, because a title will be placed over the left side later.\n"
                       "- Photographic, not illustrated; natural colours.\n")

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--pass2":
    out = os.path.abspath(sys.argv[2]).replace("\\", "/")
    refs = [os.path.abspath(p).replace("\\", "/") for p in sys.argv[3:]]
    os.makedirs(out, exist_ok=True)
    for f in FIGS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(CLEAN.format(
            out=out, img=f["img"], refs="\n".join(refs), setting=SETTING, title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
    for f in PHOTOS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO2.format(out=out, img=f["img"], setting=SETTING, scene=f["scene"]))
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
