#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ LAB 5 (เทรน VLM บนคลัสเตอร์ 2 เครื่อง)

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

SETTING = ('a small AI engineering team office that trains a receipt-reading Vision-Language Model on two rented cloud GPU '
           'servers (each server holds two RTX 3090 graphics cards) located in two different data centers and connected over the internet')

FIGS = [
    {"img": "n01-experiment", "title": "การทดลอง: 2 แนวทาง × 1 และ 2 Node × Effective Batch 8 และ 32",
     "labels": ["แนวทาง A", "แนวทาง B", "1 Node", "2 Node", "Effective Batch 8", "Effective Batch 32", "รวม 8 รอบวัด",
                "ค่าที่ตรึงไว้", "Test Set 100 ใบ"],
     "scene": "Left two thirds: a big board with a grid of 8 small cards, 2 rows (row labels 'แนวทาง A' and 'แนวทาง B') and "
              "4 columns grouped as '1 Node' and '2 Node', each group split into 'Effective Batch 8' and 'Effective Batch 32'; every card "
              "shows a small stopwatch icon. A ribbon under the board reads 'รวม 8 รอบวัด'. Right third, top: a padlock panel labelled "
              "'ค่าที่ตรึงไว้' with three small gear icons (no extra text). Right third, bottom: a clipboard with a receipt and a check mark, "
              "labelled 'Test Set 100 ใบ'.",
     "steps": ["**เทียบ A กับ B**: A = โมเดล 1 ชุดแบ่งลง GPU 2 ใบ ปิด Gradient Checkpointing · B = GPU 1 ใบต่อโมเดล 1 ชุด เปิด Gradient Checkpointing ที่ batch 1",
               "**เทียบ 1 กับ 2 Node**: แต่ละแนวทางวัดที่ Effective Batch 8 และ 32 รวม 8 รอบ",
               "**ค่าที่ตรึงไว้**: learning rate 0.0002 · seed 0 · คิด loss เฉพาะส่วนคำตอบ JSON · ป้อนทีละ 1 ใบ",
               "**วัดคุณภาพ**: เทรนจริง 400 ใบ 1 Epoch ด้วยคลัสเตอร์ 2 Node แล้ววัดบน Test Set 100 ใบ"]},
    {"img": "n02-step1-rent", "title": "ขั้นที่ 1: เช่า Node 1 ที่เครื่องอื่นต่อเข้ามาได้",
     "labels": ["1 ค้นหา RTX 3090 2 ใบ", "2 กรองตามเงื่อนไข", "3 เช่าและเปิดพอร์ต 9000", "4 รอจนเห็น GPU ครบ",
                "เกิน 8 นาที: ลบแล้วเช่าใหม่", "vapp-lab5-n1"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a magnifying glass over a list of GPU server offers; "
              "(2) a funnel filtering the offers, with small check marks; (3) one rented server box with a hanging name tag 'vapp-lab5-n1' "
              "and an open network socket on its side; (4) a laptop terminal showing two green GPU card icons. Under panel 4 a small "
              "warning sign with a stopwatch and a trash can carries the label about 8 minutes. A team member at a laptop watches on the left.",
     "steps": ["**ค้นหา** เครื่อง RTX 3090 2 ใบในเครื่องเดียว ราคารวมไม่เกิน $0.60 ต่อชั่วโมง ตั้งป้าย `vapp-lab5-n1`",
               "**กรอง**: verified · SSH ตรง · เน็ต 500 Mbps ขึ้นไป · CPU 12 cores ขึ้นไป · เลือกภูมิภาคที่มีเครื่องผ่านเงื่อนไข 2 เครื่องที่ public IP คนละตัว",
               "**เปิดพอร์ต 9000** 1 พอร์ต ให้เครื่องอื่นในคลัสเตอร์ต่อเข้ามาหาเครื่องนี้",
               "**รอจนเห็น GPU ครบ 2 ใบ** · ถ้าเกิน 8 นาทียังไม่พร้อม ให้ลบแล้วเช่าเครื่องอื่น"]},
    {"img": "n03-step6-train", "title": "ขั้นที่ 6: เทรนจริง 400 ใบ ทีละแนวทาง บนคลัสเตอร์ 2 Node",
     "labels": ["1 รอบแรก แนวทาง A · 2 replica", "2 รอบสอง แนวทาง B · 4 replica", "3 ตรวจ checksum", "4 เก็บ LoRA adapter",
                "Node 1", "Node 2", "Coordinator"],
     "scene": "Center: two server boxes labelled 'Node 1' and 'Node 2' with a small hub box labelled 'Coordinator' between them, "
              "linked by dashed internet lines. Above them, step 1 shows one model block spanning two GPU cards on each node (two replicas). "
              "Below them, step 2 shows four smaller model blocks, one on each GPU card (four replicas). Right side: step 3 a magnifying glass "
              "comparing identical fingerprint icons; step 4 a folder icon flying back to a laptop held by a team member.",
     "steps": ["**รอบแรก แนวทาง A**: 2 replica (Node ละ 1 ตัว โมเดลแบ่งบน GPU 2 ใบ) สะสมตัวละ 4 ใบ",
               "**รอบสอง แนวทาง B**: 4 replica (GPU ละ 1 ตัว) สะสมตัวละ 2 ใบ เริ่มจากโมเดลตั้งต้นใหม่",
               "ใบเสร็จ 400 ใบแรกของ Training Set · 1 Epoch · Effective Batch 8 = **50 ครั้ง** ของการปรับน้ำหนัก",
               "**ตรวจ checksum** ของน้ำหนัก LoRA ของทุก replica แล้วเก็บ adapter ไว้ที่ `results/adapter_A` และ `results/adapter_B`"]},
    {"img": "n04-step7-eval", "title": "ขั้นที่ 7: Evaluation 3 โมเดลบน Test Set 100 ใบ",
     "labels": ["Base", "Fine-tuned A", "Fine-tuned B", "1 อ่าน Test Set ทีละใบ", "2 แบ่งงานไป GPU 4 ใบ", "3 ให้คะแนน",
                "JSON อ่านได้", "ยอดรวมตรง", "Item F1"],
     "scene": "Left: a stack of receipt photos feeding three model badges labelled 'Base', 'Fine-tuned A' and 'Fine-tuned B'. "
              "Middle: four GPU cards in two server boxes working at the same time, each with a few receipts. Right: a score board with "
              "three rows labelled 'JSON อ่านได้', 'ยอดรวมตรง' and 'Item F1'; each row has only one small grey magnifier icon. "
              "NO bars, NO bar lengths, no stars and nothing that ranks or compares the three models (the results are shown elsewhere). Numbered badges 1, 2, 3 "
              "mark the three stages left to right.",
     "steps": ["**วัด 3 โมเดล**: Base (Qwen3-VL-8B-Instruct เดิม) · Fine-tuned A · Fine-tuned B (Base + adapter ของแต่ละแนวทาง)",
               "**อ่าน Test Set ทั้ง 100 ใบ** ด้วยข้อความสั่งเดียวกับตอนเทรน ภาพด้านยาว 1280 px ตอบแบบไม่สุ่ม (temperature 0)",
               "**แบ่งงานไป GPU ทั้ง 4 ใบ** ของสอง Node เพราะโมเดล 1 ชุดพอดี GPU 1 ใบตอนวัดผล",
               "**ให้คะแนน**: JSON อ่านได้ · ยอดรวมตรงทุกหลัก · Item F1 (ชื่อและราคาตรงเฉลย) · วินาทีต่อใบ"]},
    {"img": "n05-step8-delete", "title": "ขั้นที่ 8: ตรวจผลครบ ลบทุกเครื่อง แล้วอ่านยอดจริง",
     "labels": ["1 ตรวจผลใน results", "2 บันทึก nodes.json", "3 ลบ vapp-lab5-n*", "4 อ่านยอดที่ถูกคิด", "ไม่มีเครื่องค้าง"],
     "scene": "Four numbered panels left to right connected by arrows: (1) a laptop with a folder and a checklist with ticks; "
              "(2) a small JSON document card; (3) two server boxes going into a big trash can; (4) a bill/invoice paper with a coin stack "
              "(no numbers). A green ribbon at the bottom carries the label 'ไม่มีเครื่องค้าง'. A team member points at the trash can.",
     "steps": ["**ตรวจผลให้ครบ** ใน `results`: ผลดิบขั้นที่ 3–5 · adapter A และ B · ผล Evaluation ถ้าขาดให้เก็บจากเครื่องก่อน",
               "**บันทึกข้อมูลของแต่ละ Node** (GPU ที่ตั้ง ราคา อายุเครื่อง ยอดที่ถูกคิด) ลง `results/raw/nodes.json` โดยไม่ใส่ IP และเลขเครื่อง",
               "**ลบทุกเครื่องที่ป้ายขึ้นต้นด้วย `vapp-lab5-n`** แล้วตรวจว่าไม่มีเครื่องป้ายนี้ค้าง (ห้ามแตะเครื่องป้ายอื่น)",
               "**สรุปค่าใช้จ่ายจริงแยกเครื่อง**: อายุเครื่อง · ราคาต่อชั่วโมง · GPU · disk · รับส่งข้อมูล"]},
    {"img": "n06-step11-skill", "title": "ขั้นที่ 11: ใช้สกิล cluster-vlm-train ทำซ้ำใน 1 พรอมต์",
     "labels": ["1 พรอมต์", "SKILL.md", "1 เช่า 2 เครื่อง", "2 วัด 1 Node เทียบ 2 Node", "3 เทรน 200 ใบ", "4 วัดผลบน Test Set",
                "5 ลบทุกเครื่อง"],
     "scene": "Left: a team member types one short prompt card labelled '1 พรอมต์' on a laptop; the small robot holds a document labelled "
              "'SKILL.md'. Right: a path of five numbered stations left to right: (1) two server boxes being rented; (2) a stopwatch comparing "
              "one server with two servers; (3) a small stack of receipts feeding one GPU card (no chart, no curve, no graph); (4) a clipboard with a receipt and check mark; (5) a trash can with "
              "the two servers.",
     "steps": ["**สั่งด้วยพรอมต์เดียว**: ใช้สกิล `cluster-vlm-train` แนวทาง B บนคลัสเตอร์ 2 Node แบบย่อ",
               "**เช่า RTX 3090 2 ใบ 2 เครื่อง** ป้าย `vapp-lab5-skill-n1` และ `vapp-lab5-skill-n2`",
               "**วัดความเร็ว** 1 Node เทียบ 2 Node ที่ Effective Batch 32 รอบละ 6 ครั้งของการปรับน้ำหนัก",
               "**เทรนจริง 200 ใบ** 1 Epoch ที่ Effective Batch 8 วัดผลบน Test Set เทียบ Base แล้วลบทุกเครื่อง",
               "เก็บผลไว้ที่ `results/skill_v0_run` ห้ามเขียนทับผลเดิม"]},
]

PHOTOS = [
    {"img": "s01-theory", "scene": "A quiet modern server room with soft light. On the right, an engineer kneels beside an open rack server "
                                   "and looks closely at two large graphics cards installed side by side, thinking about memory limits. "
                                   "Mood: careful investigation before training a large model."},
    {"img": "s02-lab", "scene": "A small team office at dusk. On the right, a developer sits at a desk typing on a laptop, the screen glow "
                                "abstract and unreadable; beside the desk two small rack servers sit on a shelf connected by a network cable, "
                                "status lights glowing. Mood: starting a hands-on experiment on rented machines."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, light pastel background, rounded panels, thick outlines, numbered circle badges, rounded title banner, bold rounded Thai lettering):
{refs}

Canvas: landscape 16:9 (about 1400 x 788). Setting: {setting}.

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

# ------------------------------------------------------------------ รอบที่ 2: ภาพอธิบายแบบตำรา (n2x) และภาพถ่าย (p2x)
# ภาพอธิบาย: ป้ายอยู่ในภาพ ไม่มีแถบหัวข้อ (หัวข้อเป็นของสไลด์) · ภาพถ่าย: ไม่มีตัวอักษร สไลด์เป็นผู้ใส่ข้อความ
FIGS2 = [
    {"img": "n21-roadmap",
     "labels": ["1 ภาคพื้นฐาน", "ปัญหา · Dataset · โมเดล · ทฤษฎี", "2 ภาค LAB", "ขั้นที่ 1–9 บนเครื่องเช่า",
                "3 ปิดท้าย", "สร้างสกิลเวอร์ชัน 0", "4 สรุป", "ผลรวม · บทเรียน · ข้อจำกัด"],
     "scene": "A horizontal road map with four numbered stations from left to right, joined by a gently curving path. "
              "Station 1: an open book with a small GPU card icon. Station 2: two rack servers with a cloud between them. "
              "Station 3: a document with a gear (a reusable skill file). Station 4: a flag with a small bar chart. "
              "Each station has its name label (the label that starts with the number) and, under it, its smaller description label."},
    {"img": "n22-two-approaches",
     "labels": ["แนวทาง A · Model Parallelism", "โมเดล 1 ชุด แบ่ง Layer ลง GPU 2 ใบ", "แนวทาง B · Data Parallelism",
                "GPU 1 ใบ ต่อโมเดล 1 ชุด", "1 Node", "2 Node", "1 replica", "2 replica", "4 replica"],
     "scene": "A 2 x 2 comparison grid. Row headers on the left: the A label (with its description under it) and the B label "
              "(with its description). Column headers on top: '1 Node' and '2 Node'. Each Node is drawn as one rack server box holding "
              "two GPU cards. Row A: one long model block (stack of layers) spans BOTH GPU cards of a server; cell '1 Node' has one "
              "server and the tag '1 replica'; cell '2 Node' has two servers and the tag '2 replica'. Row B: each GPU card holds its own "
              "complete small model block; cell '1 Node' has one server with two model blocks and the tag '2 replica'; cell '2 Node' has "
              "two servers with four model blocks and the tag '4 replica'. Use navy for A and orange for B."},
    {"img": "n23-label-rules",
     "labels": ["items · ทุกบรรทัดที่พิมพ์ รวม topping", "name · คัดลอกตามตัวอักษร", "qty · ไม่พิมพ์จำนวน = 1",
                "price · จำนวนเต็ม", "subtotal · tax · ไม่พิมพ์ = null", "total · ยอดที่ต้องจ่าย"],
     "scene": "Left: a simple drawn paper receipt (no readable words on it, only grey lines for item rows, a small indented line "
              "for a topping, and bold lines at the bottom for the totals). Right: a code card with a JSON skeleton drawn as "
              "coloured key chips only. Six thin leader lines connect parts of the receipt to six rule labels arranged in a column "
              "between them: item rows to the items label, the item name to the name label, a quantity spot to the qty label, the "
              "price column to the price label, the subtotal and tax lines to the subtotal label, the bottom total line to the total label."},
    {"img": "n24-metrics",
     "labels": ["Speedup", "ใบเสร็จต่อวินาที ของ N Node ÷ ของ 1 Node", "เร็วขึ้นกี่เท่า",
                "Efficiency", "Speedup ÷ N", "ได้กี่ % ของ Ideal",
                "เงินต่อ Epoch", "เวลาที่ใช้กับ 800 ใบ × ราคาต่อชั่วโมงรวมทุก Node", "จ่ายเท่าไรต่อการเทรน 1 รอบ"],
     "scene": "Three tall panels side by side, each with one large simple icon at the top: a stopwatch (Speedup), a half-circle "
              "gauge (Efficiency), a stack of coins with a small calendar page (เงินต่อ Epoch). In each panel: the metric name in large "
              "bold type, under it the formula label inside a light rounded box, under that the meaning label in smaller muted type."},
    {"img": "n25-before-start",
     "labels": ["1 ทำ LAB 0 · เตรียม key 3 ตัว", "2 เปิด Claude Code ที่โฟลเดอร์ 02_VastAi_Application",
                "3 ทำขั้นที่ 1 → 9 ให้ครบในรอบเดียว", "4 ต้องลบทุกเครื่องในขั้นที่ 8 เสมอ"],
     "scene": "A vertical checklist of four numbered rows, each row a wide rounded strip with an icon on the left: (1) three keys "
              "on a ring; (2) a laptop with a folder; (3) a straight arrow passing through nine small dots; (4) a running taxi-style "
              "money meter beside a trash can with a server, this row highlighted in soft red as a warning."},
    {"img": "n26-report",
     "labels": ["ผลดิบ results/raw", "ผล Evaluation results/eval", "ราคาต่อชั่วโมงของแต่ละ Node", "code/report.py",
                "results/metrics.json", "กราฟ 4 รูป results/images", "ตารางสรุป + ประมาณการ 3 Node", "ไม่ใช้เครื่องเช่า"],
     "scene": "A left-to-right data flow. Left column: three input cards (folder icon, clipboard icon, price-tag icon) with the three "
              "input labels. Centre: one large navy processing block labelled with the code/report.py label, on a laptop. Right column: "
              "three output cards (JSON file icon, small bar chart icon, table icon) with the three output labels. Arrows from inputs to "
              "the centre and from the centre to outputs. Above the laptop, a small crossed-out cloud server icon with the label "
              "about not using a rented machine."},
    {"img": "n27-v0-bug",
     "labels": ["ลูปของ Node ใช้ตัวนับ i", "ฟังก์ชัน ssh_n ใช้ i โดยไม่ประกาศ local", "ค่า i ของลูปถูกเขียนทับ",
                "worker ได้ที่อยู่ Coordinator ผิด", "เข้าร่วมได้ 2 จาก 4 replica", "การเทรนค้างราว 14 นาที",
                "แก้: local rc i"],
     "scene": "A cause-and-effect chain from left to right in four boxes connected by arrows. Box 1: a loop arrow circling two server "
              "icons, with a small variable chip 'i' (monospace). Box 2: a function card (monospace style) that reaches into the same "
              "chip 'i'. Box 3: the chip 'i' with a red overwrite mark. Box 4: a Coordinator hub with four replica slots, two connected "
              "in green and two disconnected in grey, plus a paused hourglass. Under the chain, a green fix tag with the fix label "
              "pointing at box 2. Code-like labels in monospace."},
    {"img": "n29-step2",
     "labels": ["1 ติดตั้งแพ็กเกจ", "2 โหลดโมเดล Qwen3-VL-8B-Instruct", "3 receipt_data.py แปลงเฉลยเป็น JSON",
                "4 ทำภาพตัวอย่าง dataset_samples.jpg", "HF_TOKEN ห้ามค้างบนเครื่องเช่า"],
     "scene": "One rented rack server in the centre. Four numbered stations around "
              "it in clockwise order with arrows: (1) a package box going into the server; (2) a large model file icon downloading; "
              "(3) a receipt turning into a JSON code card (code label in monospace); (4) a small grid of six receipt thumbnails "
              "paired with code cards. In the lower right corner: a small key icon with a crossed circle and the HF_TOKEN label."},
    {"img": "n30-step3",
     "labels": ["ใบเสร็จที่เฉลยยาวที่สุด", "A · GPU 1 ใบ", "A · GPU 2 ใบ", "B · batch 1", "B · batch 2",
                "Out of Memory", "เทรนได้"],
     "scene": "Left: one long receipt icon with a long JSON tail, labelled with the first label, feeding four horizontal test lanes "
              "stacked vertically. Lane 1 (A, one GPU card): the memory bar of the card overflows above a dashed 24 GB line, red "
              "stamp 'Out of Memory'. Lane 2 (A, two GPU cards): model split over two cards, both bars below the line, green tag "
              "'เทรนได้'. Lane 3 (B batch 1, one card): bar below the line, green tag 'เทรนได้'. Lane 4 (B batch 2, one card with "
              "two receipts): bar overflows, red stamp 'Out of Memory'. Write 'Out of Memory' and 'เทรนได้' once per lane where shown "
              "(they may repeat across lanes; no other text). Do not write numbers on the bars."},
    {"img": "n31-step4",
     "labels": ["Node 1", "Coordinator · CPU · พอร์ต 9000", "worker · replica", "1 คำนวณ Gradient", "2 ส่ง", "3 รอครบแล้วเฉลี่ย",
                "4 รับค่าเฉลี่ย ปรับน้ำหนัก", "เวลาคำนวณ / เวลาสื่อสาร"],
     "scene": "One large rack server box labelled Node 1. Inside: a small CPU hub labelled with the Coordinator label in the centre, "
              "and two GPU cards each running a worker replica (label the worker label once). A circular cycle of four numbered "
              "arrows between the replicas and the hub shows steps 1 to 4. To the right: a plain stopwatch (one colour, the dial is NOT split into "
              "coloured parts and has no wedges or shares) with the label about compute time and communication time under it."},
    {"img": "n32-step5",
     "labels": ["Node 1", "Node 2", "อินเทอร์เน็ต", "1 เช่า Node 2 · public IP คนละตัว", "2 เตรียมให้เหมือน Node 1",
                "3 ทดสอบการต่อ และวัด RTT", "4 วัด 4 รอบเดิมด้วยโค้ดเดิม"],
     "scene": "Two rack server boxes far apart, labelled Node 1 (left) and Node 2 (right), each with two GPU cards, standing on two "
              "separate small map tiles; between them a long dashed internet line with a cloud labelled 'อินเทอร์เน็ต'. Node 2 has "
              "a single arrow pointing toward Node 1 (it connects out to Node 1). Along the bottom, four numbered step cards in a row "
              "with small icons: a rental tag, a copy icon, a ping wave, a stopwatch."},
    {"img": "n33-step10",
     "labels": ["PROMPTS.md", "code", "results", "SKILL.md", "skill_v0/scripts", ".claude/skills/cluster-vlm-train",
                "ค่าที่ปรับได้ · ขั้นตอน · เกณฑ์ตรวจผ่าน · กติกาเรื่องเงิน"],
     "scene": "A left-to-right flow. Left: three stacked document/folder cards labelled PROMPTS.md, code and results (monospace). "
              "Middle: a large funnel that turns them into one document card labelled SKILL.md (monospace), with the four-part "
              "checklist label written beside it as one line. Under SKILL.md a folder labelled skill_v0/scripts. Right: an arrow to "
              "an installed folder icon labelled .claude/skills/cluster-vlm-train (monospace)."},
]

PHOTOS2 = [
    {"img": "p22-two-sites", "comp": "lower",
     "scene": "Wide shot at dusk: two separate small data-centre buildings far apart in a landscape (one near forest and snow hills, "
              "one near red desert rock), a faint glowing line of light arcing across the sky between them, suggesting an internet "
              "link between two rented GPU servers in different places. No people."},
    {"img": "p23-meter", "comp": "lower",
     "scene": "Close view of an open rack server in a dim machine room, its status lights glowing; in the foreground on a desk a "
              "laptop with an abstract unreadable bar chart and a small analog wall clock in soft focus, suggesting that rented "
              "machines cost money every minute they stay switched on."},
    {"img": "p25-closing", "comp": "left",
     "scene": "A tidy engineering desk at night after an experiment: a closed laptop, a printed chart page turned face down, a cup "
              "of tea, and in the background two small rack servers whose lights are switched off. One adult engineer of Thai "
              "appearance on the right side stands up, satisfied, putting on a jacket."},
]

ILLUS = """Generate ONE image with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

Kind of image: a clean explanatory figure for a university lecture slide, like a figure in a well-made textbook or technical report.
Style: modern flat vector illustration, white or very light grey background, restrained palette (navy #12305e, teal #0f8f8c,
orange #e87f1c, soft red for errors, soft green for success, light greys), thin consistent outlines, simple geometric icons
(rack servers, GPU cards, documents, arrows), generous white space, clear left-to-right or top-to-bottom reading order.
No cartoon mascots, no robot, no comic style, nothing childish. No title banner (the slide has its own title).
Canvas: landscape 16:9 (about 1600 x 900).

Context of the lesson: {setting}.

What the figure shows: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Write each label once unless the scene says otherwise. Do NOT add any other words, numbers, captions, units, watermarks or logos.
- When a label starts with a number followed by a space (for example "2 ส่ง"), draw that number ONLY inside a circle badge and write the rest of the label next to it. Never show the same badge number twice.
- Text must be large, bold, clean sans-serif (Thai like IBM Plex Sans Thai or Noto Sans Thai) and easy to read from the back of a classroom. File names, folders and code-like labels use a monospace font.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

PHOTO2 = """Generate ONE photorealistic image with your image generation tool and save it as a JPG file at exactly this path:
{out}/{img}.jpg

Scene: {scene}

Requirements:
- Photorealistic, natural light, cinematic but calm, landscape 16:9 (about 1920x1080).
- Setting of the lesson: {setting}.
- Any people are fictional adults of Thai appearance; no real person's likeness.
- NO readable text anywhere: no letters, no numbers, no logos, no signs, no watermarks. Screens and papers must be blurred or abstract.
- {comp}

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

COMP = {"lower": "Keep the lower third of the frame calm and darker, because one sentence will be placed on a band across the bottom later.",
        "left": "Keep the left 45% of the frame calm and darker (out-of-focus background), main subject on the right side, because a title will be placed over the left side later."}


def pass2(out):
    os.makedirs(out, exist_ok=True)
    for f in FIGS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(ILLUS.format(
            out=out, img=f["img"], setting=SETTING, scene=f["scene"], labels="\n".join(f["labels"])))
    for f in PHOTOS2:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO2.format(
            out=out, img=f["img"], setting=SETTING, scene=f["scene"], comp=COMP[f["comp"]]))
    print("%d พรอมต์ (รอบที่ 2) -> %s" % (len(FIGS2) + len(PHOTOS2), out))


if __name__ == "__main__":
    if sys.argv[1] == "--pass2":
        pass2(os.path.abspath(sys.argv[2]).replace("\\", "/"))
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
