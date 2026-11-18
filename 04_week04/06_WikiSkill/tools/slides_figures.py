#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์บท 06_WikiSkill (ใช้โดย tools/build_slides.py)

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

SETTING = 'a small cozy Thai neighborhood coffee shop called "BaanKafe" (wooden counter, espresso machine, plants)'   # ฉากของบท

FIGS = [
    {"img": "n01-what-changed", "title": "สิ่งที่บทนี้เปลี่ยนจากบท 05",
     "labels": ["บท 05 · Skill Optimizer", "คนเขียนสกิลรุ่นแรก", "คนสั่งแก้ทีละรุ่น", "ISSUES.md",
                "บทนี้ · WikiSkill", "เริ่มจากชุดสกิลว่าง", "AI 2 บทบาท ทำเองทั้งวงรอบ", "wiki/", "Test Set 3 ข้อ"],
     "scene": "Two columns side by side, each with a header. Left column (header: the chapter-05 label): a barista writing a paper manual by hand, "
              "the barista giving orders one at a time to the AI robot, and a single sheet of notes. Right column (header: the WikiSkill label): "
              "an empty folder, two small robots working together around a loop arrow, and a thick bound notebook. At the bottom right, three "
              "sealed envelopes with the Test Set label.",
     "steps": ["สกิลรุ่นแรก: บท 05 คนเขียน (`v0`) · บทนี้ **ไม่มี** เริ่มจากชุดสกิลว่าง",
               "ผู้หาสาเหตุและแก้สกิล: บท 05 คือ Claude Code ตามพรอมต์ของคน ทีละรุ่น · บทนี้ AI 2 บทบาท ทำเองทั้งวงรอบ",
               "ความรู้แฝง: บท 05 คนเขียนลงสกิลและตอบคำถามของ Claude · บทนี้ต้อง **ค้นพบเอง** จาก Trace และข้อความของตัวตรวจ",
               "ที่เก็บสิ่งที่เรียนรู้: `ISSUES.md` → สมุดความรู้ `wiki/`",
               "ชุดโจทย์เหมือนเดิม เพิ่ม **Test Set 3 ข้อ** · โมเดล จำนวนรอบ และตัวตรวจเหมือนบท 05 ทุกค่า ผลจึงเทียบกันได้"]},
    {"img": "n02-paper-vs-chapter", "title": "จากเปเปอร์ มาสู่โจทย์ของบทนี้",
     "labels": ["ในเปเปอร์", "5 Benchmark", "8 รอบ", "prompt ในภาคผนวก E",
                "ในบทนี้", "โจทย์คิดเงิน 9 ข้อ", "ไม่เกิน 8 รอบ", "prompt ภาษาไทยที่เขียนใหม่", "Algorithm 1 เหมือนกัน"],
     "scene": "Two columns side by side joined in the middle by one wide bridge ribbon (the Algorithm 1 label). Left column: a research paper "
              "with five small different task icons (a calculator, a globe, a spreadsheet, a long document, a small house), a circular arrow, "
              "and a sheet of paper. Right column: the coffee shop cash register with nine small task cards, a circular arrow, and a sheet "
              "of paper held by the AI robot.",
     "steps": ["เครื่องมือของบทนี้ทำตาม **Algorithm 1** ของเปเปอร์ทุกบรรทัด ต่างกันที่ขนาดของงานและวิธีรัน Agent",
               "งาน: 5 Benchmark → เขียนฟังก์ชันคิดเงิน 9 ข้อของร้าน BaanKafe (Training 4 · Validation 2 · Test 3 · ข้อละ 3 รอบ)",
               "จำนวนรอบ: 8 รอบ → ไม่เกิน 8 รอบ (หยุดเมื่อ Validation = 100%)",
               "Wiki Maintainer และ Skill Proposer: prompt ภาษาไทยที่เขียนใหม่ใน LAB 0 · sonnet (effort high)",
               "การรัน Trial: คำสั่ง `run` ของ `skill-optimizer` ที่สร้างในบท 05 · สกิลวางใน `./skills` ให้ Agent เปิดอ่านเอง"]},
    {"img": "n03-experiment-plan", "title": "แผนการทดลอง",
     "labels": ["9 โจทย์", "Training 4", "Validation 2", "Test 3", "× 3 รอบ", "1 รอบของ WikiSkill = 18 Trial", "วัดชุดสกิล 1 ชุด = 27 Trial"],
     "scene": "A left-to-right counting story. Left: nine task cards in three groups of different colours (a group of four, a group of two, "
              "a group of three sealed envelopes), each group with its label. Middle: three circular repeat arrows. Right: two result badges "
              "stacked vertically, the upper one next to a loop arrow with two small robots, the lower one next to a measuring scale.",
     "steps": ["Input: โจทย์ 9 ข้อใน `suite/suite.json` · 6 ข้อแรกและตัวตรวจเป็นชุดเดียวกับบท 05",
               "**Training Set** 4 ข้อ ใช้สร้าง Trace ให้ Wiki Maintainer อ่าน · **Validation Set** 2 ข้อ ใช้ตัดสินที่ Gate ดูได้แค่คะแนนรวม · **Test Set** 3 ข้อ ใช้วัดตอนจบเท่านั้น",
               "1 Trial = Agent 1 ตัว + โจทย์ 1 ข้อ + ชุดสกิล 1 ชุด → ได้ `solve.py` และ `test_solve.py` · คะแนน = สัดส่วนข้อตรวจที่ผ่าน",
               "1 รอบของ WikiSkill = Training 12 Trial + Validation 6 Trial · วัดชุดสกิล 1 ชุด = 9 โจทย์ × 3 รอบ = **27 Trial**",
               "Inference Agent: `sonnet` effort `medium` · Wiki Maintainer และ Skill Proposer: `sonnet` effort `high`"]},
    {"img": "n04-lab0-setup", "title": "ขั้น 0.2 ทำอะไร",
     "labels": ["1 ติดตั้ง wikiskill", "2 คัดลอกโจทย์ และสกิล v3 ของบท 05", "3 ตรวจตัวตรวจ", "4 รายงาน", "container multi-account"],
     "scene": "A laptop on the left and a large shipping-container-shaped box on the right. Four numbered arrows/cards: a toolbox going "
              "into the container, folders being copied in, the AI robot inspecting a measuring scale, and a clipboard report.",
     "steps": ["ติดตั้ง `my-wikiskill` เป็น global skill ชื่อ `wikiskill` ของบัญชี yolo (ไว้ข้างสกิล `skill-optimizer` ของบท 05)",
               "คัดลอก `suite` ไปไว้ที่ `/workspace/wklab/suite` · สกิล `v3` ของบท 05 ไปไว้ที่ `/workspace/wklab/runs/so-v3/skills`",
               "ตรวจ: มีสกิล `skill-optimizer` อยู่แล้วหรือไม่ · ตัวตรวจด้วย `suite/check_grader.py` · บัญชี `yolo1`–`yolo5` ตัวไหนล็อกอินแล้ว",
               "รายงานเป็นตาราง รายการ | ผล"]},
    {"img": "n05-lab1-steps", "title": "LAB 1 ทำอะไร",
     "labels": ["1 สร้าง workspace w1", "2 รอบที่ 1 ทีละขั้น", "rollout → maintain → propose → gate", "3 loop จนวงรอบหยุด", "4 เก็บผลลงเครื่อง", "5 รายงาน"],
     "scene": "Five numbered stations along a winding road: an empty folder with a small measuring scale; a row of four small connected "
              "boxes that the AI robot inspects one by one with a magnifying glass; a circular loop arrow that ends at a finish flag; folders "
              "moving into a laptop; a clipboard report.",
     "steps": ["สร้าง workspace `w1` (ชุดสกิลว่าง · wiki ว่าง) แล้ววัด baseline",
               "รอบที่ 1 รันทีละขั้น `rollout` → `maintain` → `propose` → `gate` · หลังแต่ละขั้นเปิดไฟล์ที่ขั้นนั้นสร้าง ดูว่าชั้นใด (raw / wiki / skills) เปลี่ยนอย่างไร",
               "รันต่อด้วย `loop` จนวงรอบหยุด (R_best = 100% หรือครบ 8 รอบ) แล้วบันทึกผลของ `status`",
               "เก็บผล: คัดลอก `runs/w1` จาก container มาไว้บนเครื่อง · ไม่เก็บ Trace ดิบ · Validation Set เก็บแค่คะแนนและต้นทุน",
               "รายงาน: ตารางของแต่ละขั้น · เนื้อหาของ `wiki/index.md` · ชื่อสกิลที่ได้ · เหตุผลที่วงรอบหยุด"]},
    {"img": "n06-lab2-steps", "title": "LAB 2 ทำอะไร",
     "labels": ["1 วัด 3 ชุดสกิล", "noskill · so-v3 · w1", "2 สรุปตารางเทียบ", "3 gate ตัดสิน 2 คู่", "4 หาข้อที่ยังผิด", "5 เก็บผลและรายงาน"],
     "scene": "Five numbered stations along a road: three robots writing code side by side (one with no manual, one with a handwritten manual, "
              "one with a printed manual); a score table with three bars; a gate with a traffic light; a robot with a magnifying glass over one "
              "red cross; folders moving into a laptop next to a clipboard.",
     "steps": ["วัด `noskill` · `so-v3` · `w1` กับโจทย์ทั้ง 9 ข้อ · ชุดละ 27 Trial รวม 81 Trial",
               "สรุปตารางเทียบ 3 ชุด (`report`)",
               "`gate` ของ `skill-optimizer` ตัดสิน `noskill` → `w1` และ `so-v3` → `w1` ด้วยกติกาเดียวกับบท 05",
               "หาข้อตรวจที่ `w1` ยังไม่ผ่าน (`failures` ของชุด train และชุด test)",
               "ผลรายข้อของ Test Set เปิดได้หลังวัดครบทั้ง 3 ชุดแล้วเท่านั้น · เก็บผลและรายงาน"]},
    {"img": "n07-lab3-steps", "title": "LAB 3 ทำอะไร",
     "labels": ["1 รัน loop ใหม่ · workspace w2", "ค่าเดิมทุกค่า", "2 วัดสกิลของ w2", "3 เทียบ w1 กับ w2", "4 เก็บผลและรายงาน"],
     "scene": "Four numbered stations along a road: a circular loop arrow with two small robots starting again from an empty folder, with a "
              "small tag showing a lock (same settings); a measuring scale with a row of small score bars; two notebooks side by side being "
              "compared by a barista; folders moving into a laptop next to a clipboard.",
     "steps": ["สร้าง workspace `w2` แล้วรัน `loop` จนวงรอบหยุด · ค่าทุกตัวเหมือน `w1` ใน LAB 1",
               "วัดสกิลของ `w2` กับโจทย์ทั้ง 9 ข้อ ข้อละ 3 รอบ = 27 Trial แล้วสรุปตารางเทียบ `noskill` `so-v3` `w1` `w2`",
               "เทียบ `w1` กับ `w2`: จำนวนรอบ · pattern ใน `wiki/index.md` · ข้อเสนอและผลตัดสินของแต่ละรอบ · คะแนนของสกิลที่ได้",
               "เก็บผลและรายงาน: สิ่งที่เหมือนกันและสิ่งที่ต่างกัน"]},
    {"img": "n08-lab4-steps", "title": "LAB 4 ทำอะไร",
     "labels": ["1 รัน loop แบบไม่ใช้ wiki", "workspace n1", "ไม่มี Wiki Maintainer", "2 วัดสกิลของ n1", "3 เทียบกับ w1 และ w2", "4 เก็บผลและรายงาน"],
     "scene": "Four numbered stations along a road: a circular loop arrow with only ONE small robot, and next to it a thick notebook crossed "
              "out with a red X; a measuring scale with a row of small score bars; three folders side by side being compared by a barista, "
              "two of them with a notebook on top and one without; folders moving into a laptop next to a clipboard.",
     "steps": ["สร้าง workspace `n1` แบบ **ไม่ใช้ wiki** แล้วรัน `loop` จนวงรอบหยุด · ไม่มี Wiki Maintainer · Skill Proposer เห็นเฉพาะ Trace ของรอบล่าสุด",
               "วัดสกิลของ `n1` กับโจทย์ทั้ง 9 ข้อ ข้อละ 3 รอบ = 27 Trial",
               "เทียบ `n1` กับ `w1` และ `w2`: จำนวนรอบ · จำนวน Trial · จำนวนการเรียกโมเดลของผู้ปรับสกิล · คะแนน · สิ่งที่เหลือในโฟลเดอร์เมื่อจบ",
               "เก็บผลและรายงาน: สิ่งที่ `n1` ไม่มีเมื่อจบ"]},
    {"img": "n09-lab5-steps", "title": "LAB 5 ทำอะไร",
     "labels": ["1 ทีมตอบนโยบาย 4 ข้อ", "2 เติมลงสกิล เป็นรุ่น w1p", "3 gate ตัดสิน", "REJECT",
                "4 กำกับขอบเขต เป็นรุ่น w1q", "5 gate ตัดสินอีกครั้ง", "ACCEPT"],
     "scene": "Five numbered stations in two rows. Top row: a barista with four speech bubbles answering questions from an open notebook; a "
              "document receiving new lines from a pencil; a gate with a red traffic light and a red stamp. Bottom row: the same document with "
              "small fences drawn around each new line; a gate with a green traffic light and a green stamp.",
     "steps": ["ผู้เรียนรับบทคนในทีม: ตอบเรื่องที่ Wiki ของ `w1` จดว่ายังไม่ยืนยัน (นโยบายธุรกิจ 4 ข้อ อยู่ในพรอมต์)",
               "ขั้น 5.1: คัดลอกสกิลของ `w1` เป็น `w1p` แก้ไม่เกิน 3 จุด · เขียนเป็นนโยบายของร้าน ห้ามใส่ Input หรือคำตอบของข้อตรวจ",
               "วัด 27 Trial แล้ว `gate` ของบท 05 ตัดสิน `w1` → `w1p`",
               "ขั้น 5.2: รุ่นที่ถูกปฏิเสธไม่ถูกใช้ต่อ · เริ่มจาก `w1` อีกครั้งด้วยความรู้ชุดเดิม แต่ระบุว่านโยบายแต่ละข้อใช้กับฟังก์ชันใด เป็นรุ่น `w1q`",
               "วัด 27 Trial แล้ว `gate` ตัดสิน `w1` → `w1q`"]},
    {"img": "n10-lessons", "title": "สิ่งที่ผลจริงสอน",
     "labels": ["1 ความรู้ที่เกิดซ้ำ ค้นพบได้จาก Trace", "2 สกิลดีได้เท่าที่ Validation วัด", "3 Wiki คือรายการคำถามให้คนตอบ",
                "4 เขียนกว้างเกิน งานอื่นพัง", "5 Gate ไม่คิดความแกว่ง"],
     "scene": "Five numbered lesson cards in a row (three on top, two below), each with one icon: the AI robot finding a pattern in a pile of "
              "paper slips with a magnifying glass; a measuring ruler that is shorter than the object it measures; an open notebook with "
              "question marks next to a barista; a wide paint roller spilling paint over neighbouring cards; a gate with a pair of dice.",
     "steps": ["ไม่มีสกิล 46.9% → `w1` 97.9% โดยไม่มีคนเขียนสกิล: ความรู้แฝงที่เกิดซ้ำทุกงาน ค้นพบได้จาก Trace และข้อความของตัวตรวจ",
               "`policy` 0/6 ทั้ง `w1` `w2` `n1`: Validation ที่ไม่มีข้อตรวจนี้ทำให้วงรอบหยุดที่ 100% · **สกิลดีได้เท่าที่ Validation วัด**",
               "Wiki จดว่า \"ยังไม่ยืนยัน\" พร้อมสมมติฐาน: Wiki ไม่ได้มีไว้ให้ AI อย่างเดียว เป็นรายการคำถามที่คนต้องตอบด้วย",
               "`w1p` REJECT · `w1q` ACCEPT: ความรู้ที่ถูกต้องแต่เขียนกว้างเกิน ทำงานอื่นพัง · ทุกการแก้ต้องผ่านการวัดกับโจทย์ที่ไม่ได้ใช้ตอนแก้",
               "`w1` 2 รอบ · `w2` 1 รอบ: Gate รับเมื่อ \"สูงกว่าเดิม\" และหยุดเมื่อได้ 100% โดยไม่คิดความแกว่ง · Validation 6 Trial ผ่านครบได้โดยบังเอิญ"]},
    {"img": "n11-exercises", "title": "แบบฝึกหัด 6 ข้อ",
     "labels": ["1 อ่านงานของ Wiki Maintainer", "2 รัน workspace w3", "3 ย้าย t4-cashback ไป Validation", "4 วัดโจทย์ละ 6 รอบ",
                "5 ทำรุ่น w1r ลดโทเคน 10%", "6 ใช้กับงานของตัวเอง"],
     "scene": "Six numbered task cards pinned on a cork board in the coffee shop (two rows of three), each with a small icon: an open notebook "
              "with reading glasses; a circular loop arrow; a task card moving from one tray to another; six small repeat arrows; a downward "
              "arrow next to a document; a pencil with a blank document.",
     "steps": ["เปิด `maintainer_input.md` กับ `maintainer_output.json` ของ `w1` รอบที่ 2 แล้วหาว่า Maintainer แก้หน้าเดิมด้วยรายการแก้แบบใดบ้าง (ไม่ใช้โทเคน)",
               "รัน workspace `w3` ด้วยค่าเดิม แล้วเติมแถวที่ 3 ในตารางของ LAB 3",
               "ย้ายโจทย์ `t4-cashback` ไปอยู่ Validation Set แล้วรัน WikiSkill ใหม่ · วงรอบหยุดที่รอบใด และ Wiki จดเรื่อง `policy` อย่างไร",
               "รัน workspace ใหม่โดยตั้งให้วัดโจทย์ละ 6 รอบ แล้วเทียบจำนวนรอบกับ `w1` และ `w2`",
               "ทำรุ่น `w1r` จาก `w1q`: ลดโทเคนขาเข้าอย่างน้อย 10% โดยคะแนนไม่ลด แล้วให้ gate เทียบกับ `so-v3`",
               "ใช้ WikiSkill กับงานของตัวเอง: เขียนโจทย์ 4 + 2 + 2 ข้อและตัวตรวจ แล้วรัน `loop`"]},
    {"img": "n12-limits", "title": "ข้อจำกัดของการทดลองนี้",
     "labels": ["1 โจทย์เล็ก จบใน 1–2 รอบ", "2 รัน 1–2 ครั้งต่อการตั้งค่า", "3 Validation ไม่มีข้อตรวจ policy", "4 สกิลวางใน ./skills",
                "5 เครื่องมือสร้างจากพรอมต์"],
     "scene": "Five numbered caution cards in a row (three on top, two below), each with a small yellow warning triangle and one icon: a very "
              "short race track with a finish flag; a pair of dice; a short checklist with one empty row; a folder with a document inside; "
              "the AI robot assembling a toolbox.",
     "steps": ["โจทย์เล็กและจบใน 1–2 รอบ → ข้อเสนอของวงรอบผ่าน Gate ทั้ง 4 ครั้ง จึงไม่มีการย้อนกลับจริงของ WikiSkill ให้ดู (เห็นได้จากการทดสอบของ LAB 0.1 และจาก gate ของบท 05 ใน LAB 5)",
               "รันแต่ละการตั้งค่า 1–2 ครั้ง → ผลต่าง 1–2 จุดระหว่าง `w1` `w2` `n1` มีส่วนที่เป็นความบังเอิญ",
               "Validation 2 ข้อ ไม่มีข้อตรวจ `policy` → วงรอบหยุดเมื่อ Validation ได้ 100% ทั้งที่ Training ยังไม่เต็ม",
               "สกิลถูกวางใน `./skills` ไม่ได้ใส่ใน prompt แบบเปเปอร์ → Agent ต้องเปิดอ่านเอง ใช้คำสั่งเพิ่ม 1–2 ครั้งต่องาน",
               "เครื่องมือ `wikiskill` และ prompt สร้างจากพรอมต์ของ LAB 0.1 → ฉบับของผู้เรียนอาจต่างจากฉบับที่ใช้วัดผลในบทนี้ สิ่งที่ต้องตรงคือรูปแบบใน `wikiskill_format.md`"]},
]

PHOTOS = [
    {"img": "s01-theory", "scene": "A barista in an apron sits at a wooden table after closing time, reading a thick worn handwritten notebook; "
                                   "a cup of coffee steams beside it. Mood: quiet study, knowledge being read."},
    {"img": "s02-wikiskill", "scene": "On a wooden counter, three things lie in a row from back to front: a messy pile of loose handwritten paper slips, "
                                      "a thick bound notebook, and one clean laminated card. A barista's hand rests on the notebook. "
                                      "Mood: raw notes becoming organised knowledge becoming one short manual."},
    {"img": "s03-lab", "scene": "A young developer sits at a wooden table in the coffee shop typing on an open laptop, focused, while a barista "
                                "colleague stands beside and watches the screen with interest. Mood: hands-on experiment."},
    {"img": "s04-summary", "scene": "Two colleagues in aprons stand at the counter at the end of the day and look together at an open notebook; "
                                    "one points at a page and both smile. Warm evening light. Mood: reviewing what was learned."},
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
