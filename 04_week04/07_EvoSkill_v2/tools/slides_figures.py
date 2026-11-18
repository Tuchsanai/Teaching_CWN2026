#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์บท 07_EvoSkill_v2 (ใช้โดย tools/build_slides.py)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล · ใช้เลขนำหน้าเรียงตามลำดับในสไลด์ เช่น n01-...)
  title  หัวข้อของสไลด์ และข้อความบนหัวของภาพ
  labels ข้อความสั้นบนภาพ (3-10 ป้าย · ป้ายที่เป็นขั้นตอนขึ้นต้นด้วยเลข เช่น "1 สร้างการรัน e1")
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ: มีอะไรอยู่ตรงไหน เรียงอย่างไร (ไม่ต้องบรรยายสไตล์)
  steps  ขั้นตอนข้างภาพ 3-5 ขั้น · เรียบเรียงจาก README.md ของบท ห้ามมีตัวเลขหรือข้อเท็จจริงที่ไม่อยู่ใน README
         ภาพที่ไม่มี steps = build_slides.py อ่านขั้นตอนจากตารางของ README.md ตอนสร้าง
PHOTOS = ภาพถ่ายสมจริงของหน้าคั่น (ไม่มีตัวอักษรในภาพ · ฝั่งซ้ายมืดไว้วางหัวข้อ) · หน้าปกใช้ img/g01-cover.jpg เดิม

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
      เขียนพรอมต์ 1 ไฟล์ต่อภาพ (<img>.txt) · ภาพอ้างอิงสไตล์ของบทนี้ =
      01_theory/img/g02-three-agents.png และ 01_theory/img/g09-adaptor.png
"""
import os, sys

SETTING = 'a small cozy Thai neighborhood coffee shop called "BaanKafe" (wooden counter, espresso machine, hanging plants, jars of coffee beans)'

FIGS = [
    {"img": "n01-problem", "title": "โจทย์เดิม: ความรู้แฝงของทีมไม่อยู่ในโจทย์",
     "labels": ["โจทย์: เขียนฟังก์ชันคิดเงิน", "ข้อกำหนดที่ระบุชัด", "ความรู้แฝงของทีม", "ตัวตรวจ", "สิ่งเดียวที่ปรับได้: สกิล"],
     "scene": "One wide scene with three areas from left to right. Left: the barista hands one task card to the robot who sits at a laptop "
              "(the task label), the card shows a short checklist (the explicit-requirements label). Middle: a thought cloud above the "
              "barista's head holds a stack of handwritten notes that the robot cannot see, a dotted line separates the cloud from the "
              "robot (the tacit-knowledge label). Right: a grading machine with a round gauge receives the robot's work (the grader label). "
              "Bottom center: one small booklet with a pencil on the counter (the skill label)."},
    {"img": "n02-what-changed", "title": "สิ่งที่บทนี้เปลี่ยนจากบท 05 และ 06",
     "labels": ["บท 05 · Skill Optimizer", "คนเขียนสกิลรุ่นแรก", "มีประตูรับ",
                "บท 06 · WikiSkill", "AI 2 บทบาท + wiki/",
                "บทนี้ · EvoSkill v2", "AI ตัวเดียว มี bash", "เห็นแค่คะแนน", "ไม่มีประตูรับ"],
     "scene": "Three tall rounded panels side by side, each with its header label on top. Panel 1 (chapter 05): the barista writes a booklet "
              "by hand; below it a small gate with a traffic light. Panel 2 (chapter 06): two small robots work together next to a thick "
              "bound notebook. Panel 3 (this chapter): ONE robot with a teal scarf sits at a laptop that shows a dark terminal window; "
              "next to it a round gauge dial; below it an open doorway with no gate and no guard."},
    {"img": "n00-how-to-lab", "title": "วิธีทำ LAB ทุกขั้น",
     "labels": ["1 คัดลอกกล่องพรอมต์", "2 วางใน Claude Code Desktop", "3 รอ AI ทำงานใน container", "4 เทียบกับผลจริงในบท"],
     "scene": "Four numbered stations from left to right along a path: the barista copying a framed note card from an open textbook; "
              "the barista pasting the card into a chat window on a laptop; a robot with an orange scarf working inside a large "
              "shipping-container-shaped box while an hourglass runs; the barista holding two score sheets side by side and nodding."},
    {"img": "n03-lab0-steps", "title": "LAB 0 ทำอะไร",
     "labels": ["ขั้น 0.1 สร้างสกิล evoskill", "1 ศึกษาเปเปอร์", "2 ออกแบบ", "3 สร้างโปรแกรม", "4 เขียน prompt", "5 ทดสอบ", "6 รายงาน",
                "ขั้น 0.2 ติดตั้งใน container", "ตรวจตัวตรวจ"],
     "scene": "Two wide rows. Top row (the step 0.1 label on its left): six numbered small stations in a line: the robot reading a "
              "research paper with glasses; a blueprint sheet on a table; the robot assembling a small machine with a wrench; the robot "
              "writing three note cards; the machine on a test bench with green check lights; a clipboard with a table. The row ends at a "
              "gift-box-shaped folder. Bottom row (the step 0.2 label on its left): the barista carrying that folder into a large "
              "shipping-container-shaped box, and next to it the robot inspecting a grading machine with a round gauge using a magnifying "
              "glass (the grader-check label)."},
    {"img": "n04-lab1-steps", "title": "LAB 1 ทำอะไร",
     "labels": ["1 สร้างการรัน e1", "2 รันขั้น adapt", "3 เปิดไฟล์ใน setup/", "4 ดูไฟล์ใน reference/", "5 เทียบสิ่งที่สั่งกับสิ่งที่ทำ"],
     "scene": "Five numbered stations along a winding path: an empty folder with a name tag; the barista giving a one-page note and a box "
              "to a robot with a green scarf; three documents with a padlock on them; a small shelf of binders and task cards; two sheets "
              "of paper side by side being compared by the robot with a magnifying glass."},
    {"img": "n05-lab2-steps", "title": "LAB 2 ทำอะไร",
     "labels": ["1 base → turn → rollout", "epoch 1 ทีละขั้น", "2 เปิด actions.md และ skills_v1/", "3 run จนจบ",
                "4 เก็บผลด้วย export", "5 รายงาน"],
     "scene": "Five numbered stations along a winding path: a row of three small connected boxes that the barista opens one by one "
              "(the step-by-step label below it); the barista reading a log sheet and a small booklet with a magnifying glass; a circular "
              "loop arrow with three laps that ends at a finish flag, with a robot in an orange scarf and a robot in a teal scarf on the "
              "loop; folders moving into a laptop; a clipboard with a table."},
    {"img": "n06-too-broad", "title": "นโยบายถูกเขียนกว้างกว่าที่เฉลยบอก",
     "labels": ["1 เฉลยของ Training", "เงินคืนสมาชิก: ปัดลง", "2 สกิลที่ Evolver เขียน", "เงินที่ร้านจ่ายออก: ปัดลง",
                "3 Test Set · x2-refund", "งานคืนเงินคอร์ส: ผิด", "ไม่มีประตูรับ"],
     "scene": "Three panels from left to right. Panel 1: the robot with a teal scarf reads ONE answer sheet that shows a single small "
              "member card with a coin and a down arrow. Panel 2: the same robot paints a booklet with a very wide paint roller, the "
              "paint covers many different coins, banknotes and tickets at once. Panel 3: a different task card with a graduation cap "
              "gets a red cross from a grading machine; next to it an open doorway with no gate and no guard (the no-gate label)."},
    {"img": "n07-blind-guess", "title": "Evolver เห็นแค่คะแนน จึงต้องเดา",
     "labels": ["ตัวตรวจ", "ข้อ tests ไม่ผ่าน", "Evolver ไม่เห็น", "Evolver เห็น: 0.9", "1 เดาสาเหตุ", "2 ย้ายไฟล์เทสต์ไป /tmp",
                "3 คะแนนยัง 0.9 เท่าเดิม"],
     "scene": "Left third: a grading machine stands behind a brick wall and prints a detailed slip with one red cross (the grader label, "
              "the failed-check label, the cannot-see label). A small window in the wall shows only a round gauge (the 0.9 label). "
              "Right two thirds, three numbered small scenes in a row: the robot with a teal scarf scratches its head with a question mark; "
              "the robot carries one sheet of paper out of a work folder into a separate box; the robot looks at the same gauge again, "
              "the needle has not moved."},
    {"img": "n08-lab3-steps", "title": "LAB 3 ทำอะไร",
     "labels": ["1 สร้างการรัน n1 ค่าเหมือน e1", "2 ใช้ instruction_with_note.md", "reference/README.md 1 ประโยค", "3 run จนจบ",
                "4 เทียบ n1 กับ e1"],
     "scene": "Four numbered stations from left to right: an empty folder with a name tag; the barista sticking ONE small note onto the "
              "top of a shelf of binders (the one-sentence label next to the note); a circular loop arrow that ends at a finish flag; "
              "two score sheets side by side being compared by the barista."},
    {"img": "n09-lab4-steps", "title": "LAB 4 ทำอะไร",
     "labels": ["1 สร้างการรัน p1 เหมือน e1", "2 ใช้ instruction_score_only.md", "reference/ ไม่มีเฉลย", "3 run จนจบ",
                "4 เปิด evo/evolver_workspace/", "5 เทียบ p1 กับ e1"],
     "scene": "Five numbered stations along a winding path: an empty folder with a name tag; a shelf where the answer binders have been "
              "taken away and only four task cards remain, the robot with a teal scarf looks at a round gauge only (the no-answers label); "
              "a circular loop arrow that ends at a finish flag; the robot's own small private notebook lying open; two score sheets "
              "side by side being compared by the barista."},
    {"img": "n10-lab5-steps", "title": "LAB 5 ทำอะไร",
     "labels": ["1 สร้างการรัน f1 เหมือน e1", "2 เพิ่ม --fresh-session", "เซสชันใหม่ทุก epoch", "ไฟล์ยังอยู่ ความจำหาย", "3 run จนจบ",
                "4 เทียบ f1 กับ e1"],
     "scene": "Four numbered stations from left to right: an empty folder with a name tag; three identical robots with teal scarves, each "
              "stepping out of its own new cardboard box one after another (the new-session label), while one shelf of binders behind them "
              "stays the same (the files-stay label); a circular loop arrow that ends at a finish flag; two score sheets side by side "
              "being compared by the barista."},
    {"img": "n11-lab6-steps", "title": "LAB 6 ทำอะไร",
     "labels": ["1 สร้างการรัน h1 เหมือน e1", "2 Solver = haiku", "Evolver = haiku", "3 run จนจบ", "4 เทียบ h1 กับ e1",
                "5 ดูสกิลใน skills_v3 และต้นทุน"],
     "scene": "Five numbered stations along a winding path: an empty folder with a name tag; two noticeably SMALLER robots, one with an "
              "orange scarf typing on a laptop and one with a teal scarf writing in a notebook, each with its own label; a circular loop "
              "arrow that ends at a finish flag; two score sheets side by side being compared by the barista; a booklet next to a small "
              "stack of coins."},
    {"img": "n12-lab7-steps", "title": "LAB 7 ทำอะไร",
     "labels": ["1 รัน noise ของ e1 n1 p1 f1 h1", "ไม่รัน rollout ใหม่", "2 บันทึก noise.txt", "3 หา leg ที่คะแนนต่างกันระหว่างครั้ง",
                "4 ดูช่อง รับ ที่ไม่ใช่ 0/9 หรือ 9/9"],
     "scene": "Four numbered stations from left to right: the barista pulling five existing folders from a shelf while a robot with an "
              "orange scarf sleeps beside a closed laptop (the no-new-rollout label); sheets of paper being filed into a drawer; a board "
              "with rows of three small score cards where the cards in some rows differ; a gate with a traffic light next to a pair of dice."},
    {"img": "n13-lessons", "title": "สิ่งที่ผลจริงสอน",
     "labels": ["1 เห็นเฉลย จึงพบนโยบายธุรกิจ", "2 ขยายเกินหลักฐาน ไม่มีอะไรจับ", "3 คะแนนตัวเดียว บอกทิศไม่ได้",
                "4 คนปรับได้ที่สิ่งที่ Evolver เห็น", "5 รัน 1 ครั้ง ไม่ใช่ข้อสรุป"],
     "scene": "Five numbered lesson cards (three on top, two below), each with one icon: the robot reading an answer sheet with a light "
              "bulb above its head; a wide paint roller spilling paint over neighbouring cards; a round gauge with one needle next to a "
              "compass with a question mark; the barista placing one note into a folder for the robot; a pair of dice next to three score "
              "bars of different heights."},
    {"img": "n14-exercises", "title": "แบบฝึกหัด 7 ข้อ",
     "labels": ["1 อ่าน status และ actions.md", "2 เพิ่มเป็น 5 epochs", "3 บอกว่าเป็น epoch สุดท้าย", "4 วัดชุดสกิลของทุก epoch",
                "5 วัดสกิลของบท 05", "6 กำกับขอบเขตของนโยบาย", "7 ใช้กับงานของตัวเอง"],
     "scene": "Seven numbered task cards pinned on a cork board in the coffee shop (four on top, three below), each with a small icon: "
              "an open log sheet with reading glasses; five small circular arrows; a finish flag; three booklets in a row on a measuring "
              "scale; one booklet with a pencil next to a round gauge; a fence drawn around one small coin; a pencil with a blank document."},
]

# ขั้นตอนข้างภาพ · เรียบเรียงจากพรอมต์และข้อความของ LAB นั้นใน README.md (ไม่มีตัวเลขผล: ตัวเลขผลอ่านจากไฟล์ผลตอนสร้าง)
# ภาพที่ไม่อยู่ในรายการนี้ (n02 n07 n13 n14) build_slides.py อ่านขั้นตอนจากตารางของ README.md
STEPS = {
    "n00-how-to-lab": [
        "**คัดลอก** กล่องพรอมต์ของ LAB (กล่อง IMPORTANT)",
        "**วาง** ใน Claude Code Desktop แล้วกด Enter",
        "**รอ** AI ทำงานใน container",
        "**เทียบ** ผลของคุณกับผลจริงในบท"],
    "n03-lab0-steps": [
        "ขั้น 0.1 · **ศึกษา** อ่านเปเปอร์ สรุปวงรอบของ EvoSkill v2 · **ออกแบบ** จด `references/source.md`",
        "ขั้น 0.1 · **สร้าง** `scripts/evoskill.py` 12 คำสั่ง พร้อม `plugin_api.py` และ `plugin_skeleton.py`",
        "ขั้น 0.1 · **เขียน** `prompts/` 3 ไฟล์ · `SKILL.md` · `references/workspace.md`",
        "ขั้น 0.1 · **ทดสอบ** 3 ข้อโดยไม่เรียกโมเดล แล้วรายงาน ไฟล์ | หน้าที่",
        "ขั้น 0.2 · **ติดตั้ง** `my-evoskill` เป็น global skill `evoskill` · คัดลอก `bench` ไป `/workspace/evlab/bench`",
        "ขั้น 0.2 · **ตรวจตัวตรวจ** ด้วย `bench/check_grader.py` · ดูว่าบัญชี `yolo` ใดล็อกอินแล้ว"],
    "n04-lab1-steps": [
        "สร้างการรันชื่อ `e1`",
        "รันขั้น `adapt` อย่างเดียว: Benchmark Adaptor อ่านคำสั่งของเรา แล้วเขียนรายการโจทย์ (plug-in) กับโฟลเดอร์ `reference/` จากนั้นโปรแกรมล็อกด้วย hash และตรวจการรั่ว",
        "เปิด `setup/benchmark_plugin.py` · `setup/freeze.json` · `setup/audit.md`",
        "ดูรายการไฟล์ใน `reference/` · `turns/adaptor/message.md` และ `actions.md`",
        "รายงานเป็นตาราง รายการ | ผล และสิ่งที่ Adaptor ทำเองโดยไม่ได้สั่ง"],
    "n05-lab2-steps": [
        "**epoch 0** รันขั้น `base`",
        "**epoch 1** รันขั้น `turn` แล้วเปิด `turns/turn_1/actions.md` และ `skills_v1/` · จากนั้นรันขั้น `rollout`",
        "**รันต่อ** ด้วย `run` จนจบ: epoch 2 และ 3 แล้ววัด `skills_v3` กับ Test Set",
        "**เก็บผล** ด้วย `export` แล้วคัดลอกโฟลเดอร์ `e1` มาแทน `runs/e1` บนเครื่อง",
        "**รายงาน** ตาราง ขั้น | ไฟล์ที่เกิด | สรุป 1 บรรทัด · สรุป 3 ตาของ Evolver · ตาราง status · ข้อตรวจที่ไม่ผ่านใน Test Set"],
    "n06-too-broad": [
        "เฉลยของ Training บอกเพียงว่า **เงินคืนสมาชิก** ปัดลง",
        "Evolver ขยายเป็นกติกาของ \"เงินที่ร้านจ่ายออก\" ทุกชนิด (เงินคืน cashback · คืนเงิน · ส่วนลดที่ให้ · แต้ม · รางวัล)",
        "งานคืนเงินคอร์ส `x2-refund` ของ Test Set จึงผิดทั้ง 3 rollout",
        "ไม่มีประตูรับ และ Validation 2 โจทย์ไม่มีงานแบบนี้ ชุดสกิลจึงถูกใช้ต่อจนถึง Test"],
    "n08-lab3-steps": [
        "สร้างการรันชื่อ `n1` เหมือน `e1` ทุกค่า ต่างจุดเดียว: ใช้ `bench/instruction_with_note.md`",
        "คำสั่งนี้ให้ Benchmark Adaptor เขียน `README.md` 1 ประโยคไว้ที่ชั้นบนสุดของ `reference/`",
        "รัน `run` จนจบ แล้ว `export` และคัดลอกโฟลเดอร์ `n1` มาแทน `runs/n1`",
        "รายงาน: เนื้อหาของ `reference/README.md` · ตาราง status ของ `n1` เทียบ `e1` · สรุป 3 ตาของ Evolver · ข้อตรวจที่ไม่ผ่านใน Test Set"],
    "n09-lab4-steps": [
        "สร้างการรันชื่อ `p1` เหมือน `e1` ต่างจุดเดียว: ใช้ `bench/instruction_score_only.md`",
        "ไม่มีเฉลยของชุดใดเลย: Evolver อ่านได้เฉพาะข้อความโจทย์ของ Training",
        "รัน `run` จนจบ แล้ว `export` และคัดลอกโฟลเดอร์ `p1` มาแทน `runs/p1`",
        "เปิด `evo/evolver_workspace/` ดูบันทึกที่ Evolver เขียนให้ตัวเอง",
        "รายงาน: รายการไฟล์ใน `reference/` · ตาราง status ของ `p1` เทียบ `e1` · สรุป 3 ตาของ Evolver · ข้อตรวจที่ไม่ผ่านใน Test Set"],
    "n10-lab5-steps": [
        "สร้างการรันชื่อ `f1` เหมือน `e1` ต่างจุดเดียว: Evolver เริ่มเซสชันใหม่ทุก epoch (`--fresh-session`)",
        "ไฟล์ทุกอย่างใน `evo/` ยังอยู่ข้าม epoch หายเฉพาะความจำในเซสชัน",
        "รัน `run` จนจบ แล้ว `export` และคัดลอกโฟลเดอร์ `f1` มาแทน `runs/f1`",
        "รายงาน: ตาราง status ของ `f1` เทียบ `e1` · สรุป 3 ตาของ Evolver (ตานั้นรู้เรื่องของตาก่อนจากที่ใด) · ไฟล์ใน `evo/evolver_workspace/`"],
    "n11-lab6-steps": [
        "สร้างการรันชื่อ `h1` เหมือน `e1` ต่างจุดเดียว: Solver และ Evolver เป็น `haiku` (`--solver-model haiku --evolver-model haiku`)",
        "รัน `run` จนจบ แล้ว `export` และคัดลอกโฟลเดอร์ `h1` มาแทน `runs/h1`",
        "เทียบตาราง status ของ `h1` กับ `e1`",
        "รายงาน: ชื่อและ description ของสกิลใน `skills_v3` · ไฟล์ใน `evo/evolver_workspace/` · ต้นทุนรวมของ Evolver 3 ตา และของ Solver"],
    "n12-lab7-steps": [
        "รัน `noise` ของการรัน `e1` `n1` `p1` `f1` `h1` · ไม่รัน rollout ใหม่ (ไม่ใช้โทเคน)",
        "บันทึกผลของแต่ละการรันไว้ที่ `runs/<ชื่อ>/noise.txt` บนเครื่อง",
        "ตอบข้อ 1: leg ใดบ้างที่มีโจทย์ผ่านบางครั้ง หรือคะแนนต่างกันระหว่างครั้ง",
        "ตอบข้อ 2: การเทียบบน Validation ใดที่ช่อง \"รับ\" ไม่ใช่ 0/9 หรือ 9/9 และถ้าใช้ประตูรับนั้นจะทิ้งชุดสกิลใด"],
}
for _f in FIGS:
    _f["steps"] = STEPS.get(_f["img"])

PHOTOS = [
    {"img": "s01-theory", "scene": "After closing time, a barista in an apron sits at a wooden table and looks thoughtfully at three small "
                                   "identical white toy robots standing in a row next to a closed notebook and a steaming cup of coffee. "
                                   "Mood: quiet planning, three helpers with three different jobs."},
    {"img": "s02-lab", "scene": "A young developer sits at the wooden counter typing on an open laptop, focused; one small white toy robot "
                                "stands next to the laptop, and a barista colleague leans in to watch the screen with interest. "
                                "Mood: hands-on experiment."},
    {"img": "s03-summary", "scene": "Two colleagues in aprons stand at the counter in warm evening light and look together at three notebooks "
                                    "laid out side by side; one of them points at the third notebook and both smile. "
                                    "Mood: comparing three approaches, reviewing what was learned."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same cute hand-drawn flat cartoon,
warm cream background, big dark-brown rounded Thai title lettering at the top with small orange sparkle marks beside it,
rounded-corner panels with thick brown outlines, cozy coffee shop interior with hanging plants and coffee jars, coloured rounded
pill-shaped labels with bold white lettering, palette of teal, orange, green, red and brown). Use the same characters as the
references: the cheerful barista woman with a brown hair bun and an orange ribbon, and the small white robot with a dark face
screen, teal headphones and an orange ball antenna (the robot represents the AI agent):
{refs}

Canvas: landscape 4:3 (about 1448 x 1086). Setting: {setting}.

Title text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above. Papers, screens and signs in the scene show only abstract lines or icons, never readable text.
- When a label starts with a number (for example "3 run"), draw that number ONLY inside a circle badge and write the rest of the label next to it. Never show the same number twice.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, folder names, command names) use a monospace font.
- Fictional cartoon characters only.

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
