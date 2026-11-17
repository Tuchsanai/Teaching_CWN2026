#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์ (บท 01_VastAi_Skill): ภาพการ์ตูนอธิบาย 2 ภาพ และภาพถ่ายของหน้าคั่น 4 ภาพ

  python tools/slides_figures.py <work>/gen [ภาพอ้างอิงสไตล์ ...]     เขียนพรอมต์ 1 ไฟล์ต่อ 1 ภาพ ลงใน <work>/gen
  (สร้างภาพจากพรอมต์ ตรวจข้อความในภาพทุกภาพ แล้วย้ายภาพที่ผ่านเข้า image/ : ดูขั้นที่ 3 ของสกิล readme-slides)

ภาพอื่นของสไลด์ใช้ภาพเดิมของบทใน image/ · ขั้นตอนข้างภาพ (steps) ของภาพใหม่อ่านจาก readme.md ใน build_slides.py
ป้ายในภาพไม่มีตัวเลขของผล (ตัวเลขทุกตัวของสไลด์อ่านจาก readme.md ตอนสร้าง)
"""
import os, sys

SETTING = ("a Thai university student renting cloud GPU machines from a laptop: laptop, chat window with a small friendly "
           "white-and-blue robot (the AI), graphics cards, a cloud, price tags, keys")

FIGS = [
    {"img": "n01-scenarios", "title": "ถามตลาดด้วยสถานการณ์จริง 5 แบบ",
     "labels": ["1 หลาย GPU ในเครื่องเดียว", "2 คลัสเตอร์หลายเครื่อง", "3 งานที่ถูกขัดจังหวะได้", "4 แบ่งงานเทรนหลายเครื่อง", "5 เลือกตามงบ"],
     "scene": "Five numbered rounded pastel cards in one row, left to right: (1) one computer case holding four graphics cards; "
              "(2) four separate computer cases joined by network lines; (3) a graphics card with a pause symbol and an hourglass; "
              "(4) one big task block split by arrows into four small blocks, each on its own machine; (5) a wallet with coins next to "
              "a row of graphics cards of different sizes. Below the cards: the student at a laptop asking, and the small robot "
              "holding a magnifying glass over a market stall of graphics cards.",
     "steps": []},
    {"img": "n02-remember", "title": "สิ่งที่ควรจำ 6 ข้อ",
     "labels": ["1 ดูราคารวม ไม่ใช่แค่ค่า GPU", "2 ผลค้นเต็มเพดาน = ผลถูกตัด", "3 เขียนเพดานราคาในพรอมต์", "4 งานเสียเงิน ให้เขียนสูตร",
                "5 คนเทียบกับ baseline", "6 destroy เท่านั้นที่หยุดจ่าย"],
     "scene": "Six numbered rounded pastel cards in a grid of 3 columns and 2 rows: (1) a price tag made of three stacked parts; "
              "(2) a list of machines cut off by scissors at the bottom; (3) a barrier gate with a price tag on a chat message; "
              "(4) a recipe sheet with a checklist held by the small robot; (5) a person comparing two answer sheets side by side; "
              "(6) a trash bin with a green check mark next to a stopped money meter.",
     "steps": []},
]

PHOTOS = [
    {"img": "s01-theory", "scene": "A university lecturer explains to two students at a wooden desk, pointing with a pen at an open laptop; "
                                   "next to the laptop lies a modern graphics card. Mood: understanding the idea before doing."},
    {"img": "s02-model", "scene": "Close view of a hand in an anti-static glove holding a large modern graphics card with three fans in front "
                                  "of an open server rack with soft blue lights. Mood: the machine that runs the language model."},
    {"img": "s03-lab", "scene": "A computer lab classroom in the evening, several university students each typing on their own laptop, one "
                                "student in focus on the right concentrating on the screen. Mood: hands-on practice."},
    {"img": "s04-summary", "scene": "A university student on the right closes a laptop with a relieved smile at a tidy desk, a server room seen "
                                    "through the window behind with its lights dimmed. Mood: work finished, everything switched off."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat cartoon
infographic on a white background, a wide pastel rounded title banner at the top with large bold dark text, soft pastel rounded
cards, coloured numbered circle badges, blue arrows, small yellow sparkle marks, bold rounded Thai lettering, a student in a
blue hoodie and a small white-and-blue robot):
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
- Text must be large, bold and easy to read from the back of a classroom.
- Fictional cartoon characters only.

Rules: create only that one file. Do not modify any other file. Do not run any git command (no add, commit, push).
When the file is saved, reply with the file path and stop.
"""

PHOTO = """Generate ONE photorealistic image with your image generation tool and save it as a JPG file at exactly this path:
{out}/{img}.jpg

Scene: {scene}

Requirements:
- Photorealistic, natural warm light, shallow depth of field, landscape 16:9 (about 1920x1080).
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
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        refs = [os.path.join(here, "image", n).replace("\\", "/") for n in ("lab4-overview.png", "concept-01-three-parts.png")]
    os.makedirs(out, exist_ok=True)
    for f in FIGS:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(CARTOON.format(
            out=out, img=f["img"], refs="\n".join(refs), setting=SETTING, title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
    for f in PHOTOS:
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], scene=f["scene"]))
    print("%d prompts -> %s" % (len(FIGS) + len(PHOTOS), out))
