#!/usr/bin/env python3
"""ภาพการ์ตูนใหม่ของบททฤษฎี SkillOpt (ใช้ทั้งใน README.md และในสไลด์ของบททฤษฎี)

FIGS = ภาพอธิบาย 1 ภาพต่อ 1 ประเด็น
  img     ชื่อไฟล์ใน img/ (.png)
  title   ข้อความพาดหัวบนภาพ
  labels  ข้อความสั้นบนภาพ (ป้ายที่เป็นขั้นขึ้นต้นด้วยเลข)
  caption ข้อความในแถบล่างของภาพ
  scene   คำบรรยายภาพสำหรับตัวสร้างภาพ (ภาษาอังกฤษ)
  steps   ขั้นตอนที่แสดงข้างภาพในสไลด์ · เรียบเรียงจากเปเปอร์ SkillOpt (arXiv:2605.23904v2) และ README.md ของบททฤษฎี

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป>      เขียนพรอมต์สร้างภาพ 1 ไฟล์ต่อภาพ
สไตล์อ้างอิง: img/g06-backward-pass.png และ img/g09-meta-skill.png (ภาพการ์ตูนเดิมของบททฤษฎี)
"""
import os, sys

FIGS = [
    {"img": "g10-overview", "title": "SkillOpt ในภาพเดียว",
     "labels": ["1 ปัญหา", "สกิลเขียนครั้งเดียว ไม่เคยถูกฝึก", "2 แนวคิด", "ล็อกโมเดล ฝึกข้อความของสกิล",
                "3 วงรอบ", "ลองทำ → เสนอแก้ → ตรวจก่อนรับ", "4 ผล", "best_skill.md เล็ก อ่านได้ ย้ายได้"],
     "caption": "ฝึกสกิลด้วยวินัยเดียวกับการเทรนโมเดล",
     "scene": "Four numbered panels left to right connected by arrows: (1) a dusty paper document that nobody edits; (2) the white robot "
              "with a padlock and a snowflake holding a green book, a pencil editing the book; (3) a circular loop of three small icons "
              "(robot working, purple robot proposing an edit tag, a gate with a tick); (4) one small green document with a gold star.",
     "steps": ["**ปัญหา:** สกิลส่วนใหญ่ถูกเขียนครั้งเดียว (คนเขียน หรือ LLM เขียน) หรือถูกแก้ไปเรื่อย ๆ โดยไม่ตรวจ จึงไม่รับประกันว่าดีขึ้น",
               "**แนวคิด:** ล็อกโมเดลไว้ แล้วฝึกข้อความของสกิล เหมือนฝึกน้ำหนักของโมเดล",
               "**วงรอบ 1 ก้าว:** ลองทำงาน (Forward) → เสนอวิธีแก้ (Backward) → ตรวจก่อนรับ (Validation Gate)",
               "**ผล:** ไฟล์ `best_skill.md` ขนาดประมาณ 300–2,000 โทเคน ที่คนอ่านได้ และย้ายไปใช้กับโมเดลหรือ Harness อื่นได้"]},
    {"img": "g11-four-ways", "title": "สกิลสร้างได้ 4 แบบ",
     "labels": ["1 คนเขียนเอง", "ใช้ได้กับงานที่นึกถึง", "2 LLM เขียนครั้งเดียว", "ไม่เคยลองใช้จริง",
                "3 LLM แก้ตัวเอง ไม่ตรวจ", "ผลขึ้น ๆ ลง ๆ", "4 SkillOpt", "แก้ทีละน้อย ตรวจทุกก้าว"],
     "caption": "3 แบบแรกไม่รับประกันว่าดีขึ้นจากจุดเริ่ม",
     "scene": "Four numbered panels in a row. (1) a person writing a document by hand; (2) a robot printing one document from a printer "
              "and walking away; (3) a dizzy grey robot rewriting its own document in a messy spiral with a zig-zag line chart; "
              "(4) the white robot and the purple robot with glasses working together, a small staircase going down steadily with ticks. "
              "Panel 4 is highlighted with a teal border.",
     "steps": ["**คนเขียนเอง:** ใช้ได้กับงานที่คนเขียนนึกถึง พอเปลี่ยนงานหรือเปลี่ยนโมเดลก็พลาด",
               "**LLM เขียนครั้งเดียว:** ไม่ได้ลองใช้จริง จึงไม่รู้ว่าได้ผลหรือไม่",
               "**LLM แก้สกิลตัวเองไปเรื่อย ๆ โดยไม่ตรวจ:** แก้ทีละมาก ๆ ลบกฎที่ดีทิ้ง ผลขึ้น ๆ ลง ๆ",
               "**SkillOpt:** มีหลักฐานต่อก้าว มีขนาดก้าว มีการตรวจบนข้อมูลที่ไม่ได้ใช้ฝึก และมีความจำของก้าวที่ผิด"]},
    {"img": "g12-design-principles", "title": "หลักการออกแบบ 5 ข้อ",
     "labels": ["1 ล็อกโมเดล แก้แค่สกิล", "2 ตรวจก่อนรับทุกครั้ง", "3 เชื่อหลักฐานที่เกิดซ้ำ", "4 จำกัดขนาดของก้าว", "5 สกิลที่ส่งออกต้องเล็ก"],
     "caption": "แต่ละข้อมีไว้กันความผิดพลาด 1 แบบ",
     "scene": "Five numbered cards in a row, one icon each: (1) the white robot with a padlock and snowflake next to a green book and pencil; "
              "(2) a wooden gate with a green tick flag; (3) three identical red-cross papers stacked with a magnifying glass; "
              "(4) a short footstep path with a ruler; (5) one small green document with a star on a tiny scale.",
     "steps": ["**ล็อกโมเดล แก้แค่สกิล:** ถ้าคะแนนเปลี่ยน ต้องมาจากสกิลอย่างเดียว",
               "**ตรวจก่อนรับทุกครั้ง:** สกิลรุ่นใหม่ต้องผ่านชุด Selection ก่อน ข้อเสนอที่ไม่ได้ตรวจจึงไม่สะสม",
               "**เชื่อหลักฐานที่เกิดซ้ำ:** รวมข้อเสนอจากหลายกลุ่มเป็นชั้น ๆ ให้เหลือสิ่งที่พบซ้ำ ไม่ใช่ตัวอย่างเดียว",
               "**จำกัดขนาดของก้าว:** จำนวน Edit ต่อก้าวคือ Learning Rate ช่วงต้นแก้ได้มาก ช่วงท้ายแก้ละเอียด",
               "**สกิลที่ส่งออกต้องเล็ก:** บันทึกของ Optimizer (Meta Skill) แยกไว้ต่างหาก ไม่ส่งให้โมเดลที่ทำงาน"]},
    {"img": "g13-optimizer-inside", "title": "ข้างใน Optimizer: 6 งานย่อย",
     "labels": ["1 วิเคราะห์งานที่ผิด", "2 วิเคราะห์งานที่ถูก", "3 รวมข้อเสนอฝั่งผิด", "4 รวมข้อเสนอฝั่งถูก",
                "5 รวมขั้นสุดท้าย", "ฝั่งผิดมาก่อน", "6 จัดอันดับ เก็บ L ข้อ"],
     "caption": "ข้อเสนอที่หลายกลุ่มเห็นตรงกัน ได้อันดับสูง",
     "scene": "A two-lane pipeline run by the purple robot with glasses. Top lane (red): stack of red-cross papers -> (1) -> (3) a red funnel. "
              "Bottom lane (green): stack of green-tick papers -> (2) -> (4) a green funnel. Both lanes join at (5) one big funnel, then (6) "
              "a podium with three edit tags ranked first, second, third.",
     "steps": ["**วิเคราะห์งานที่ผิด:** อ่านทีละกลุ่ม หาข้อผิดที่เกิดซ้ำ แล้วเสนอ Edit ไม่เกินงบ `L`",
               "**วิเคราะห์งานที่ถูก:** หาพฤติกรรมที่ได้ผลและยังไม่อยู่ในสกิล เพื่อรักษาไว้",
               "**รวมข้อเสนอของแต่ละฝั่ง:** ตัดข้อที่ซ้ำ แก้ข้อที่ขัดกัน และนับว่าแต่ละข้อมีกี่กลุ่มสนับสนุน (support count)",
               "**รวมขั้นสุดท้าย:** ให้การแก้ข้อผิดมาก่อนการเสริมสิ่งที่ถูก",
               "**จัดอันดับ:** เรียงตามผลต่อข้อผิดที่เกิดซ้ำ การเติมช่องว่างของสกิล ความทั่วไป และความชัดเจน แล้วเก็บ `L` ข้อแรก"]},
    {"img": "g14-three-difficulties", "title": "ทำไมการปรับข้อความจึงยาก",
     "labels": ["1 ไม่มี Gradient", "ข้อความหาอนุพันธ์ไม่ได้", "2 วัดแพง และแกว่ง", "ต้องให้โมเดลทำงานจริง", "3 ทางเลือกนับไม่ถ้วน", "เขียนได้ทุกแบบ"],
     "caption": "SkillOpt ตอบทีละข้อ: Reflection · Batch และ Gate · ก้าวสั้น",
     "scene": "Three numbered panels. (1) the purple robot looks at a text document, a crossed-out slope arrow above it; (2) the white robot "
              "runs on a treadmill next to a stopwatch and two score bars of slightly different heights; (3) a huge maze of branching paper paths "
              "fading into fog.",
     "steps": ["**ไม่มี Gradient:** ข้อความหาอนุพันธ์ไม่ได้ จึงให้ Optimizer Model อ่านหลักฐานแล้วเสนอวิธีแก้เป็นภาษาคนแทน (Reflection)",
               "**วัดแพง และแกว่ง:** จะรู้คะแนนของสกิล 1 รุ่น ต้องให้โมเดลทำงานจริงทั้งชุด และผลไม่เท่ากันทุกครั้ง จึงใช้งานเป็นกลุ่ม (Batch) และตัดสินด้วยชุดที่แยกไว้ (Gate)",
               "**ทางเลือกนับไม่ถ้วน:** ข้อความเขียนได้ทุกแบบ จึงเดินจากสกิลปัจจุบันทีละก้าวสั้น ไม่เขียนใหม่ทั้งไฟล์"]},
    {"img": "g15-transfer", "title": "ย้ายสกิลไปใช้ที่อื่น 3 แบบ",
     "labels": ["1 ข้ามโมเดล", "ใหญ่ → เล็ก", "2 ข้าม Harness", "Codex ↔ Claude Code", "3 ข้าม Benchmark", "คณิตศาสตร์ชุดอื่น"],
     "caption": "ไม่เทรนเพิ่ม · ทุกแถวที่วัดดีกว่าไม่มีสกิล",
     "scene": "Three numbered panels, each showing the same small green document with a star being handed over: (1) from a big white robot "
              "to a small white robot; (2) from one computer terminal window to another terminal window of a different colour; "
              "(3) from one math notebook to another math notebook.",
     "steps": ["**ข้ามโมเดล:** สกิลที่เทรนกับโมเดลใหญ่ นำไปใช้กับโมเดลเล็กโดยไม่เทรนเพิ่ม",
               "**ข้าม Harness:** สกิลที่เทรนใน Codex นำไปใช้ใน Claude Code (และกลับกัน)",
               "**ข้าม Benchmark:** สกิลของชุดโจทย์คณิตศาสตร์ชุดหนึ่ง นำไปใช้กับอีกชุดหนึ่ง",
               "ทุกแถวที่วัดดีกว่าไม่มีสกิล แต่ได้มากบ้างน้อยบ้าง ก่อนย้ายไปใช้จริงจึงต้องวัดใหม่"]},
    {"img": "g16-limitations", "title": "ข้อจำกัด 4 ข้อ",
     "labels": ["1 ต้องมีตัวตรวจอัตโนมัติ", "2 การเทรนมีต้นทุน", "3 ปรับสกิลเดียว", "4 ย้ายไกลต้องวัดใหม่"],
     "caption": "เหมาะเมื่อวัดผลได้ และสกิลถูกใช้ซ้ำ",
     "scene": "Four numbered caution cards in a row, each with a small yellow warning triangle and one icon: (1) a robot judge with a "
              "checklist; (2) a pile of coins next to a stopwatch; (3) one single document facing many different tools; "
              "(4) a document travelling far on a map with a measuring ruler at the destination.",
     "steps": ["**ต้องมีตัวตรวจอัตโนมัติที่เชื่อถือได้:** งานที่ตัดสินด้วยความรู้สึก ต้องหาวิธีให้คะแนนก่อน",
               "**การเทรนมีต้นทุน:** ต้องรันโมเดลหลายรอบ และเรียก Optimizer Model คุ้มเมื่อสกิลถูกใช้ซ้ำ",
               "**ปรับสกิลเดียว:** งานที่หลากหลายมากอาจต้องใช้หลายสกิล",
               "**สกิลอาจจำลักษณะของข้อมูลฝึก:** ก่อนย้ายไปใช้กับงานที่ต่างออกไปมาก ต้องวัดใหม่"]},
    {"img": "g17-learned-skill", "title": "สกิลที่เทรนเสร็จหน้าตาอย่างไร",
     "labels": ["1 เล็ก", "379–1,995 โทเคน", "2 แก้ไม่กี่ครั้ง", "รับ 1–4 ก้าว", "3 เป็นวิธีทำงาน", "ไม่ใช่คำตอบของโจทย์"],
     "caption": "ข้อเสนอส่วนใหญ่ถูกประตูปฏิเสธ",
     "scene": "Three numbered panels. (1) one small green document with a star lying on a kitchen scale, a person reading it easily; "
              "(2) a wooden gate where many edit tags are bounced back and only a few pass through; (3) the white robot following a "
              "step-by-step checklist instead of copying an answer sheet.",
     "steps": ["**เล็ก:** สกิลสุดท้ายของ 6 Benchmark ยาว 379–1,995 โทเคน คนอ่านและตรวจได้ในไม่กี่นาที",
               "**แก้ไม่กี่ครั้ง:** ตลอดการเทรนมีก้าวที่ถูกรับเพียง 1–4 ก้าว ข้อเสนอส่วนใหญ่ถูกประตูปฏิเสธ",
               "**เป็นวิธีทำงาน:** กฎที่ได้ไม่เอ่ยถึงโจทย์ ไฟล์ หรือชื่อเฉพาะ จึงใช้กับงานใหม่ได้",
               "**ต้นทุนจ่ายครั้งเดียว:** ตอนใช้งานไม่มีการเรียก Optimizer เพิ่ม มีแค่ข้อความสกิลที่ยาวขึ้น"]},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these two reference images, then match their illustration style exactly (flat kawaii cartoon infographic,
warm cream background, thick dark-brown outlines, rounded panels with coloured pill headers, numbered circle badges, palette of teal,
orange, green, red, purple and dark brown, bold rounded Thai lettering):
{ref}/g06-backward-pass.png
{ref}/g09-meta-skill.png

Canvas: landscape 16:9 (about 1672 x 941).

Headline at the top in large dark-brown bold Thai lettering (exact text): {title}

Scene: {scene}

Characters (same as in the references): the small WHITE robot with teal ears is the frozen target model that does the tasks;
the PURPLE robot with glasses is the optimizer model that edits the skill. Fictional cartoon characters only.

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Caption bar at the bottom: a dark-brown rounded bar with cream text (exact text): {caption}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Do NOT add any other words, numbers, captions, watermarks or logos beyond the headline, the labels and the caption above.
- When a label starts with a number (for example "3 วงรอบ"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names) use a monospace font.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

if __name__ == "__main__":
    out = os.path.abspath(sys.argv[1]).replace("\\", "/")
    ref = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "img").replace("\\", "/")
    os.makedirs(out, exist_ok=True)
    for f in FIGS:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(CARTOON.format(
            out=out, ref=ref, img=f["img"], title=f["title"], scene=f["scene"], caption=f["caption"], labels="\n".join(f["labels"])))
    print("%d พรอมต์ -> %s" % (len(FIGS), out))
