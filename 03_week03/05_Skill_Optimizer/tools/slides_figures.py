#!/usr/bin/env python3
"""ภาพอธิบายที่สไลด์เพิ่มไว้หน้าตาราง (ใช้โดย tools/build_slides.py)

แต่ละรายการ = 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ภาพใน img/ (.jpg · สร้างด้วย cyolo จาก title scene และ labels ด้านล่าง แล้วตรวจข้อความในภาพทุกภาพ)
  title  หัวข้อของสไลด์ และชื่อบนภาพ
  labels ข้อความสั้นที่อยู่บนภาพ (ใช้ตอนสร้างภาพ)
  scene  คำบรรยายภาพสำหรับตัวสร้างภาพ (ภาษาอังกฤษ)
  steps  ขั้นตอนที่แสดงข้างภาพ · เรียบเรียงจาก README.md ของบท ห้ามมีตัวเลขที่ไม่อยู่ใน README
  at     หัวข้อของ README.md ที่ภาพนี้อธิบาย (ใช้อ้างอิงเท่านั้น · ลำดับในสไลด์กำหนดใน tools/build_slides.py)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง>     เขียนพรอมต์สร้างภาพ 1 ไฟล์ต่อภาพ
"""
import os, sys

FIGS = [
    {"img": "n01-glossary", "at": ("details", "คำที่ใช้ตลอดบท"), "title": "คำที่ใช้ตลอดบท",
     "labels": ["1 สกิล", "SKILL.md", "2 Agent", "AI ที่เขียนโค้ด", "3 ตัวตรวจ", "Grader", "4 Trial", "เขียน 1 ครั้ง + ตรวจ 1 ครั้ง", "5 รุ่น", "v0 → v1 → v2"],
     "scene": "Five numbered panels in a row connected by arrows: (1) a paper document; (2) the small AI robot typing on a laptop; "
              "(3) a second robot with a magnifying glass and a checklist; (4) a stopwatch-like badge showing one write plus one check; "
              "(5) three folders in a row.",
     "steps": ["**สกิล** (`SKILL.md`): ไฟล์ข้อความ 1 ไฟล์ เขียนข้อกำหนดของร้านเป็นภาษาคน",
               "**Agent**: AI ที่ได้โจทย์ 1 ข้อกับสกิล แล้วเขียน `solve.py` เอง",
               "**ตัวตรวจ** (Grader): โปรแกรมที่รันโค้ดของ Agent แล้วตรวจทีละข้อ",
               "**Trial**: Agent เขียนโค้ด 1 ครั้ง และตัวตรวจให้คะแนน 1 ครั้ง",
               "**รุ่น**: แก้สกิล 1 ครั้ง ได้สกิลรุ่นใหม่ 1 รุ่น ชื่อ `v0` `v1` `v2` …"]},
    {"img": "n02-rules", "at": ("lead", "กติกาของโจทย์"), "title": "กติกาของโจทย์",
     "labels": ["ทำได้", "แก้ SKILL.md", "ให้ Claude Code ช่วยหาสาเหตุ", "ดูข้อที่ผิดของงาน 1–4",
                "ห้ามทำ", "แก้โค้ดของ Agent", "แก้โจทย์หรือตัวตรวจ", "ดูข้อที่ผิดของงาน 5–6"],
     "scene": "Two columns. Left column with a green header and three green check-mark rows. Right column with a red header and three "
              "red cross rows. A barista points to the left column; the AI robot stands between the columns.",
     "steps": ["แก้ได้อย่างเดียวคือ `SKILL.md` · ให้ Claude Code ช่วยหาสาเหตุและเสนอจุดแก้ได้",
               "ห้ามแก้โค้ดที่ Agent เขียน: แก้โค้ดได้ผลกับงานนั้นงานเดียว · แก้สกิลได้ผลกับทุกงานที่ AI จะเขียนต่อไป",
               "ห้ามแก้โจทย์ หรือแก้ตัวตรวจ",
               "งาน 1–4 เปิดดูข้อที่ผิดได้ · งาน 5–6 ดูได้แค่คะแนนรวม",
               "เป้าหมาย: ทุกงานผ่านครบทุกข้อตรวจ ทุกครั้งที่ให้ Agent เขียน"]},
    {"img": "n03-std1-integer", "at": ("h5", "ข้อ 1"), "title": "ข้อ 1 · ค่าเงินเป็นจำนวนเต็ม",
     "labels": ["ราคา 45.30 บาท", "ถูก", "4530 สตางค์", "int", "ผิด", "45.3", "float", "100 สตางค์ = 1 บาท"],
     "scene": "A latte with a price tag in the centre. An arrow to the left leads to a green card with a neat stack of coins. "
              "An arrow to the right leads to a red card with a cracked, wobbly coin. A small footer ribbon at the bottom.",
     "steps": ["เงินทุกค่าที่รับเข้าและคืนออก เป็นจำนวนเต็มหน่วยสตางค์ (100 สตางค์ = 1 บาท)",
               "ห้ามใช้ `float`: คอมพิวเตอร์เก็บเลขทศนิยมเป็นเลขฐานสอง จึงเก็บค่าอย่าง 45.3 ได้ไม่ตรง",
               "ผลของ `float`: ยอดเงินคลาดทีละสตางค์ เช่น `int(19.99 * 100)` ได้ `1998`"]},
    {"img": "n04-std2-rounding", "at": ("h5", "ข้อ 2"), "title": "ข้อ 2 · ปัดครึ่งขึ้น ครั้งเดียว",
     "labels": ["1230.5 สตางค์", "ถูก", "1231", "ปัดครึ่งขึ้น", "ผิด", "1230", "round() ของ Python", "ลด → VAT → ปัด 1 ครั้งตอนท้าย"],
     "scene": "A number card in the centre. A green upward arrow leads to a green result card. A red arrow leads to a red result card "
              "with a small Python snake icon. At the bottom, a three-stop timeline where only the last stop has a rounding stamp.",
     "steps": ["เศษตั้งแต่ .5 สตางค์ปัดขึ้น: 1230.5 → `1231`",
               "`round(1230.5)` ของ Python ได้ `1230` เพราะปัดเข้าหาเลขคู่ (Banker's Rounding)",
               "ปัดครั้งเดียวที่ผลสุดท้าย ขั้นกลางเก็บค่าเต็มไว้ไม่ปัด",
               "เหตุผล: ทุกสาขาต้องได้ยอดตรงกัน · ปัดหลายครั้งทำให้ความคลาดเคลื่อนสะสม (Rounding Drift)"]},
    {"img": "n05-std3-validation", "at": ("h5", "ข้อ 3"), "title": "ข้อ 3 · ตรวจสอบข้อมูลนำเข้า",
     "labels": ["ยอดซื้อ = -1", "ถูก", "ValueError", "หยุดทันที", "ผิด", "คืน 0", "คำนวณต่อ", "Fail Fast"],
     "scene": "A wrong input ticket arrives at a checkpoint gate guarded by the AI robot. Green path: the robot holds up a stop sign. "
              "Red path: the ticket slips through the gate into the cash register.",
     "steps": ["ข้อมูลผิดชนิด หรืออยู่นอกช่วงที่โจทย์กำหนด ถือเป็นข้อมูลผิด",
               "ต้องหยุดทันทีด้วย `ValueError` เท่านั้น (ไม่คืน `0` · ไม่ใช้ `TypeError`)",
               "เหตุผล: คำนวณต่อจากข้อมูลผิด = เก็บเงินลูกค้าผิด · หยุดทันที (Fail Fast) ปลอดภัยกว่า"]},
    {"img": "n06-std4-cli", "at": ("h5", "ข้อ 4"), "title": "ข้อ 4 · สัญญาการเรียกผ่าน CLI",
     "labels": ["1 JSON ทาง stdin", "2 python3 solve.py", "3 สำเร็จ", '{"ok": true, "result": 500}', "exit 0",
                "3 ข้อมูลผิด", '{"ok": false, "error": "…"}', "exit 2"],
     "scene": "A cash register sends a small data envelope into a terminal window box in the centre. Two arrows leave the terminal: "
              "the upper one to a green card, the lower one to an orange card.",
     "steps": ["เครื่องคิดเงินของร้านรัน `python3 solve.py` แล้วส่ง JSON ทาง stdin",
               "สำเร็จ: ตอบ `{\"ok\": true, \"result\": …}` exit 0",
               "ข้อมูลผิด: ตอบ `{\"ok\": false, \"error\": \"…\"}` exit 2",
               "เหตุผล: เครื่องคิดเงินเรียกทุกโปรแกรมด้วยวิธีเดียวกัน รูปแบบคำตอบจึงต้องตรงกันทุกตัว"]},
    {"img": "n07-std5-tests", "at": ("h5", "ข้อ 5"), "title": "ข้อ 5 · ชุดทดสอบหน่วย",
     "labels": ["test_solve.py", "1 ใช้ unittest", "2 อย่างน้อย 6 เทสต์", "3 มีเทสต์ข้อมูลผิด", "4 รันผ่าน", "Regression Test"],
     "scene": "A file card on the left. Four numbered checklist rows in the middle, each with a green tick. On the right, a developer "
              "character looks relieved at a laptop that shows a big green tick.",
     "steps": ["ส่ง `test_solve.py` คู่กับ `solve.py` ทุกงาน",
               "ใช้ `unittest` อย่างน้อย 6 เทสต์ และมีเทสต์ของข้อมูลผิด",
               "ต้องรันผ่านด้วย `python3 -m unittest`",
               "เหตุผล: คนที่มาแก้โค้ดทีหลังรันเทสต์แล้วรู้ทันทีว่าทำของเดิมพังหรือไม่ (Regression Test)"]},
    {"img": "n08-policies", "at": ("section", "ความรู้แฝงกลุ่ม 2"), "title": "นโยบายธุรกิจ 4 ข้อ",
     "labels": ["เงินคืน", "C1", "เดือนเกิด 2 เท่า เฉพาะ gold และ platinum", "C2", "เงินคืน ปัดลง",
                "ค่าส่ง", "S1", "0 กม. = รับเองที่ร้าน ไม่คิดค่าส่ง", "S2", "ส่งด่วน ไม่เกิน 20,000 กรัม"],
     "scene": "Four cards in a 2x2 grid under two group headers. C1: a birthday cake with gold and platinum member cards. "
              "C2: coins with a downward arrow. S1: a customer picking up a coffee-bean bag at the counter. S2: a delivery scooter with a "
              "parcel on a scale.",
     "steps": ["นโยบายที่พนักงานรู้ แต่ไม่ได้เขียนลงโจทย์ · มีอยู่ในตัวตรวจเท่านั้น",
               "เงินคืน: **C1** สิทธิ์ 2 เท่าในเดือนเกิด เฉพาะ gold และ platinum · **C2** เงินที่ร้านจ่ายออก ปัดลง",
               "ค่าส่ง: **S1** 0 กม. = ลูกค้ารับเองที่ร้าน ไม่คิดค่าส่ง · **S2** ส่งด่วนรับไม่เกิน 20,000 กรัม",
               "โค้ดที่ AI เขียนตอนไม่มีสกิล ทำตามนโยบายครบ 0/6 Trial (ผล LAB 1)"]},
    {"img": "n09-skill-role", "at": ("para", "สกิล `money-coder` มีหน้าที่เดียว"), "title": "หน้าที่ของสกิล",
     "labels": ["1 ความรู้แฝงของทีม", "2 เขียนลง SKILL.md", "3 AI อ่านก่อนเขียนโค้ด", "Externalization"],
     "scene": "Three numbered scenes left to right connected by arrows: (1) two baristas with thought bubbles above their heads; "
              "(2) a hand writing on a paper document; (3) the AI robot reading the document before typing on a laptop. A ribbon at the bottom.",
     "steps": ["ความรู้แฝงของทีมอยู่ในหัวพนักงาน ไม่เคยถูกเขียนลงโจทย์",
               "สกิล `money-coder` เปลี่ยนความรู้แฝงของทีมให้เป็นข้อกำหนดที่ระบุชัด (Externalization)",
               "AI อ่านสกิลก่อนเขียนโค้ดทุกครั้ง",
               "ตัวตรวจแปลงข้อกำหนดทั้ง 2 ประเภทเป็นข้อตรวจ 11 แบบ · ผ่านครบทุกข้อ = โค้ดถูกทั้งสองประเภท"]},
    {"img": "n10-cashback-steps", "at": ("lead", "ค · ลองคิดด้วยมือ"), "title": "cashback คิดอย่างไร",
     "labels": ["1 ยอดซื้อถึง 100 บาท?", "2 × อัตราตามระดับ", "silver 1.5% · gold 2.5% · platinum 4%", "3 เดือนเกิด × 2",
                "เฉพาะ gold และ platinum", "4 ปัดลงเป็นสตางค์", "5 ไม่เกิน 200 บาท", "ความรู้แฝง"],
     "scene": "Five numbered steps along a winding path from a receipt to a coin purse. Steps 3 and 4 each carry a small orange tag "
              "(the tacit-knowledge tag). Step 2 shows three member cards.",
     "steps": ["ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน → `0`",
               "คูณอัตราตามระดับ: silver 1.5% · gold 2.5% · platinum 4%",
               "เดือนเกิดได้ 2 เท่า **เฉพาะ gold และ platinum** (นโยบาย C1 · โจทย์ไม่ได้บอก)",
               "เศษสตางค์ **ปัดลง** เพราะเป็นเงินที่ร้านจ่ายออก (นโยบาย C2 · โจทย์ไม่ได้บอก)",
               "เงินคืนสูงสุด 200 บาทต่อบิล"]},
    {"img": "n11-deliverables", "at": ("section", "1.5 Agent ต้องส่งอะไร"), "title": "Agent ต้องส่งอะไร",
     "labels": ["ส่ง 2 ไฟล์", "solve.py", "test_solve.py", "ใช้ได้ 3 แบบ", "1 เรียกจากโค้ด Python", "2 รันเป็นโปรแกรม",
                "JSON เข้า → JSON ออก", "3 รันเทสต์", "unittest"],
     "scene": "Left: the AI robot hands over two file cards. Right: three numbered cards stacked vertically, each with an icon "
              "(a code editor, a cash register terminal, a checklist).",
     "steps": ["Agent ส่ง 2 ไฟล์ต่องาน: `solve.py` (ฟังก์ชัน) และ `test_solve.py` (เทสต์อย่างน้อย 6 เทสต์)",
               "แบบที่ 1 เรียกจากโค้ด Python: `cashback(20000, \"gold\", False)` → `500` · โปรแกรมเมอร์ของร้านใช้",
               "แบบที่ 2 รันเป็นโปรแกรม: ส่ง JSON เข้า ได้ JSON ออก (ความรู้แฝงข้อ 4) · เครื่องคิดเงินของร้านใช้",
               "แบบที่ 3 รันเทสต์: `python3 -m unittest` (ความรู้แฝงข้อ 5) · คนที่มาแก้โค้ดทีหลังใช้"]},
    {"img": "n12-train-val-cases", "at": ("table", "Training", "2.6"), "title": "อ่านผล Training กับ Validation",
     "labels": ["Training", "Validation", "1 ขึ้น · ขึ้น", "Generalization", "2 ขึ้น · ไม่ขึ้น", "Overfitting",
                "3 เต็ม · ยังไม่เต็ม", "ยังมีปัญหาที่มองไม่เห็น", "4 ลง · ลง", "ของเดิมพัง"],
     "scene": "Four numbered cards in a 2x2 grid. Each card shows two small bars (one teal for Training, one orange for Validation) "
              "with up or down arrows matching its label: both up; one up and one flat; one full and one not full; both down.",
     "steps": ["Training ขึ้น · Validation ขึ้น = สกิลดีขึ้นจริง ใช้กับงานใหม่ได้ (**Generalization**) · เช่น `v0` → `v1`",
               "Training ขึ้น · Validation ไม่ขึ้นหรือลง = สกิลจำโจทย์ของ Training (**Overfitting**) · ไม่เกิดในบทนี้",
               "Training เต็มแล้ว · Validation ยังไม่เต็ม = ยังมีปัญหาที่ Training Set มองไม่เห็น · เช่น `v2`",
               "ลงทั้งคู่ = การแก้ทำของเดิมพัง · เช่น `v3` → `v4`"]},
    {"img": "n13-experiment-plan", "at": ("section", "แผนการทดลอง"), "title": "แผนการทดลอง",
     "labels": ["6 โจทย์", "Training 4 · Validation 2", "× 3 รอบ", "= 18 Trial ต่อรุ่น", "× 6 รุ่น", "= 108 Trial"],
     "scene": "A left-to-right multiplication story: six task cards, then three circular repeat arrows, then a grid of eighteen small "
              "squares, then six folders, then a big total badge.",
     "steps": ["Input: โจทย์ 6 ข้อใน `suite/suite.json` · Training Set 4 ข้อ · Validation Set 2 ข้อ",
               "1 Trial = Agent 1 ตัว + โจทย์ 1 ข้อ + สกิล 1 รุ่น → ได้ `solve.py` และ `test_solve.py`",
               "1 รุ่น = 6 โจทย์ × 3 รอบ = **18 Trial** (Training 12 · Validation 6)",
               "ทั้งบท = 6 รุ่น (`noskill` `v0`–`v4`) × 18 = **108 Trial**",
               "โมเดล `sonnet` · effort `medium` เหมือนกันทุกรุ่น"]},
    {"img": "n14-lab0-setup", "at": ("section", "ขั้น 0.2"), "title": "ขั้น 0.2 ทำอะไร",
     "labels": ["1 ติดตั้ง skill-optimizer", "2 คัดลอกโจทย์และสกิล v0", "3 ตรวจตัวตรวจ", "4 รายงาน", "container multi-account"],
     "scene": "A laptop on the left and a large shipping-container-shaped box on the right. Four numbered arrows/cards: a toolbox going "
              "into the container, folders being copied in, a robot inspecting a measuring scale, and a clipboard report.",
     "steps": ["ติดตั้ง `my-skill-optimizer` เป็น global skill ชื่อ `skill-optimizer` ของบัญชี yolo",
               "คัดลอก `suite` และ `runs/v0/skills` ไปไว้ที่ `/workspace/sklab` (คงโครงโฟลเดอร์เดิม)",
               "ตรวจตัวตรวจด้วย `suite/check_grader.py` · ดูว่าบัญชี `yolo1`–`yolo5` ตัวไหนล็อกอินแล้ว",
               "รายงานเป็นตาราง รายการ | ผล"]},
    {"img": "n15-lab1-steps", "at": ("section", "LAB 1"), "title": "LAB 1 ทำอะไร",
     "labels": ["1 วัด noskill และ v0", "2 สรุปตารางเทียบ", "3 gate ตัดสิน", "4 เก็บผลลงเครื่อง", "5 รายงาน"],
     "scene": "Five numbered stations along a road: two robots writing code side by side (one with a manual, one without); a score table; "
              "a gate with a traffic light; folders moving into a laptop; a clipboard report.",
     "steps": ["วัดรุ่น `noskill` และรุ่น `v0` · รุ่นละ 18 Trial รวม 36 Trial",
               "สรุปตารางเทียบ 2 รุ่น (`report`) และความแกว่งของ `v0` (`null`)",
               "`gate` ตัดสิน `noskill` → `v0` ด้วยต้นทุน `context_tokens`",
               "เก็บผล: คัดลอก `runs/` จาก container มาไว้บนเครื่อง",
               "รายงาน: ตารางเทียบ 2 รุ่น · ความแกว่งของ `v0` · ผล `gate`"]},
    {"img": "n16-lab2-steps", "at": ("section", "LAB 2"), "title": "LAB 2 ทำอะไร",
     "labels": ["1 หาสาเหตุจากข้อที่ผิด", "2 จดลง ISSUES.md", "3 แก้สกิลไม่เกิน 3 จุด", "4 วัด v1", "5 gate ตัดสิน"],
     "scene": "Five numbered stations along a road: a robot with a magnifying glass over red crosses; a notebook; a pencil editing a "
              "document with three highlighted marks; a row of small score bars; a gate with a traffic light.",
     "steps": ["หาสาเหตุ: ดูข้อที่ผิดของ `v0` (เฉพาะ Training Set) เปิด Trace และโค้ดของ Trial ที่ผิด · เก็บเฉพาะสาเหตุที่พบมากกว่า 1 Trial",
               "จด `runs/ISSUES.md`: ปัญหา | พบกี่ Trial | สาเหตุ | ทางแก้",
               "แก้: คัดลอก `runs/v0/skills` เป็น `runs/v1/skills` แล้วแก้ไม่เกิน 3 จุด",
               "วัดรุ่น `v1` ด้วยค่าเดียวกับ `v0` (18 Trial)",
               "`gate` ตัดสิน `v0` → `v1` แล้วเก็บผลและรายงาน"]},
    {"img": "n17-lab3-steps", "at": ("section", "LAB 3"), "title": "LAB 3 ทำอะไร",
     "labels": ["1 ทีมตอบนโยบาย 4 ข้อ", "2 เขียนเป็นนโยบายของร้านลงสกิล", "3 วัด v2", "4 gate ตัดสิน"],
     "scene": "Four numbered stations: a barista speaking with four speech bubbles to the AI robot; a document receiving two new lines; "
              "a row of small score bars; a gate with a traffic light.",
     "steps": ["ผู้เรียนรับบทคนในทีม: ใส่ความรู้จากทีม 4 ข้อ (นโยบายธุรกิจ) ไว้ในพรอมต์",
               "หาจุดแก้จาก 3 อย่าง: ข้อที่ผิดของรุ่นฐาน · ปัญหาที่ยังเปิดใน `runs/ISSUES.md` · ความรู้จากทีม",
               "แก้ไม่เกิน 3 จุด · เขียนเป็นนโยบายของร้าน ห้ามใส่ Input หรือคำตอบของข้อตรวจ",
               "วัดรุ่น `v2` แล้ว `gate` ตัดสิน `v1` → `v2`"]},
    {"img": "n18-lab4-steps", "at": ("section", "LAB 4"), "title": "LAB 4 ทำอะไร",
     "labels": ["1 Training ผ่านครบแล้ว", "2 Validation ยังไม่เต็ม ห้ามเปิดดู", "3 หากติกาที่ยังกว้าง", "4 เขียนให้ตรวจสอบได้", "5 gate ตัดสิน"],
     "scene": "Five numbered stations: a full green bar; an orange bar that is not full next to a locked box; a robot with a magnifying "
              "glass reading a document with vague cloudy lines; the same document with crisp ruler-straight lines; a gate with a traffic light.",
     "steps": ["สถานการณ์: รุ่นฐานผ่านครบทุกข้อใน Training Set แล้ว แต่ Validation Set ยังไม่เต็ม และห้ามเปิดดูว่าผิดข้อไหน",
               "อ่านกติกาทุกข้อในสกิลของรุ่นฐาน หากติกาที่ยังกว้างจน Agent ต้องเดาเอง",
               "แก้ไม่เกิน 3 จุด ให้เป็นกติกาที่ตรวจสอบได้ · ห้ามใส่ Input หรือคำตอบของข้อตรวจ",
               "วัดรุ่น `v3` แล้ว `gate` ตัดสิน `v2` → `v3` · ถ้า REJECT ใช้ `v2` ต่อ ห้ามวัดซ้ำเพื่อให้ผ่าน"]},
    {"img": "n19-lab5-steps", "at": ("section", "LAB 5"), "title": "LAB 5 ทำอะไร",
     "labels": ["สมมติฐาน", "สกิลสั้นลง ต้นทุนลด คะแนนไม่ลด", "1 ย่อกติกาละ 1 บรรทัด", "2 วัด v4", "3 gate ตัดสิน"],
     "scene": "A scientist-style barista holds a hypothesis card at the top. Below, three numbered stations: scissors trimming a long "
              "document into a short one; a row of small score bars; a gate with a traffic light.",
     "steps": ["สมมติฐาน: สกิลที่สั้นกว่าใช้โทเคนน้อยลงโดยคะแนนไม่ลด",
               "ย่อ `SKILL.md` ของ `v3` เป็น `v4`: กติกาละ 1 บรรทัด ไม่เกิน 60 ตัวอักษร (นับเป็น 1 จุด ไม่แก้อย่างอื่น)",
               "วัดรุ่น `v4` ด้วยค่าเดียวกับ `v0`",
               "`gate` ตัดสิน `v3` → `v4` · ถ้า REJECT ใช้ `v3` ต่อ ห้ามแก้ `v4` เพิ่ม ห้ามวัดซ้ำ"]},
    {"img": "n20-lessons", "at": ("section", "4.2"), "title": "สิ่งที่ผลจริงสอน",
     "labels": ["1 เขียนกติกาให้ตรวจสอบได้", "2 ความรู้แฝงต้องมาจากทีม", "3 แก้ที่สาเหตุ", "4 วัดก่อนเชื่อ"],
     "scene": "Four numbered lesson cards in a row, each with one icon: a ruler over a document; a barista handing a note to the robot; "
              "a wrench at the root of a small plant; a measuring scale next to an eye with a question mark.",
     "steps": ["กติกากว้าง (\"ตอบเป็น JSON\") ทำให้ AI เดาต่างกันทุกครั้ง · กติกาที่ตรวจสอบได้แก้ได้ทันที (`v0` → `v1` +25.6 จุด)",
               "เครื่องมือบอกได้ว่าความรู้ขาดตรงไหน แต่ความรู้นั้นต้องมาจากคนในทีม (`policy` ยัง 0/6 ใน `v1`)",
               "Training Set เต็มแล้วไม่ได้แปลว่าสกิลสมบูรณ์ · แก้ที่สาเหตุ โจทย์ที่ไม่เคยเห็นจึงดีขึ้นด้วย (`v3`)",
               "สกิลที่สั้นและดูดี ทำคะแนนลด 19.7 จุด และต้นทุนลดแค่ 5.2% · ถ้าไม่วัดจะไม่รู้ (`v4`)"]},
    {"img": "n21-exercises", "at": ("section", "4.3"), "title": "แบบฝึกหัด 5 ข้อ",
     "labels": ["1 เพิ่มโจทย์ Training", "2 เพิ่ม Test Set", "3 วัดด้วยโมเดล haiku", "4 ทำ v5 ลดโทเคน 10%", "5 เขียนสกิลของตัวเอง"],
     "scene": "Five numbered task cards pinned on a cork board in the coffee shop, each with a small icon: a plus sign on a task card; "
              "a sealed envelope; a small bird; a downward arrow next to a document; a pencil with a blank document.",
     "steps": ["เพิ่มโจทย์ Training ข้อที่ 5 ใน `suite/` พร้อมเฉลยใน `suite/ref/` แล้วรัน `check_grader.py`",
               "เพิ่มโจทย์ `\"split\": \"test\"` 1 ข้อ แล้ววัด `v3` ครั้งเดียว",
               "วัด `v0` และ `v3` ใหม่ด้วยโมเดล `haiku`",
               "ทำ `v5` จาก `v3`: ลดโทเคนขาเข้าอย่างน้อย 10% โดยคะแนนไม่ลด (อ่าน `ISSUES.md` ก่อน)",
               "เขียนสกิลของตัวเอง 1 ตัว พร้อมโจทย์ 4 + 2 ข้อ แล้วปรับ 2 รุ่น"]},
    {"img": "n22-limits", "at": ("section", "4.4"), "title": "ข้อจำกัดของการทดลองนี้",
     "labels": ["1 โจทย์มี 6 ข้อ", "2 Validation ถูกใช้ 5 ครั้ง", "3 ไม่คิดความแกว่งของต้นทุน", "4 ตรวจ 10–11 ข้อ", "5 เครื่องมือสร้างจากพรอมต์"],
     "scene": "Five numbered caution cards in a row, each with a small yellow warning triangle and one icon: six task cards; a worn "
              "answer sheet; a wobbly price tag; a short checklist; a robot assembling a toolbox.",
     "steps": ["โจทย์มี 6 ข้อ และตั้งแต่ `v2` คะแนนของแต่ละโจทย์เท่ากันทุกรอบ → ความแกว่งที่วัดได้เป็น 0 ประตูรับใช้เกณฑ์ขั้นต่ำ 2 จุด",
               "Validation Set ถูกใช้ตัดสิน 5 ครั้ง → คำตอบค่อย ๆ รั่วเข้าการตัดสินใจ ควรยืนยันด้วย Test Set",
               "ประตูรับไม่คิดความแกว่งของต้นทุน → ผลต่างของต้นทุนเล็ก ๆ อาจเป็นความบังเอิญ",
               "ตัวตรวจตรวจเฉพาะ 10–11 ข้อ → คุณภาพด้านอื่น เช่น โค้ดอ่านง่าย ไม่ถูกวัด",
               "เครื่องมือ `skill-optimizer` สร้างจากพรอมต์ → ฉบับของผู้เรียนอาจต่างจากฉบับที่ใช้วัดผลในบทนี้"]},
]

PROMPT = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these two reference images, then match their illustration style exactly (same kind of flat cartoon
infographic, warm cream background, coffee-shop decorations, dark-brown rounded title banner, thick outlines, rounded cards,
numbered circle badges, palette of teal, orange, green, red and brown, bold rounded Thai lettering):
{ref}/g19-problem.png
{ref}/g21-one-round.png

Canvas: landscape 4:3 (about 1448 x 1086).

Title banner text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above.
- When a label starts with a number (for example "3 gate"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, JSON, exit codes) use a monospace font.
- Characters: a friendly barista team and one small white-and-teal robot that represents the AI. Fictional cartoon characters only.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

if __name__ == "__main__":
    out = sys.argv[1].replace("\\", "/")
    ref = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "img").replace("\\", "/")
    os.makedirs(out, exist_ok=True)
    for f in FIGS:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(
            PROMPT.format(out=out, ref=ref, img=f["img"], title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
    print(len(FIGS), "prompts ->", out)
