#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์บททฤษฎี EvoSkill v2 (ใช้โดย tools/build_slides.py)

FIGS   = ภาพอธิบายแบบการ์ตูน 1 ภาพต่อ 1 สไลด์ "ภาพ + ขั้นตอน" (ภาพด้านซ้าย ขั้นตอนเรียงเลขด้านขวา)
  img    ชื่อไฟล์ใน img/ (ไม่ใส่นามสกุล)
  title  ข้อความพาดหัวบนภาพ
  labels ข้อความสั้นบนภาพ (ป้ายที่เป็นขั้นตอนขึ้นต้นด้วยเลข)
  scene  คำบรรยายภาพเป็นภาษาอังกฤษ: มีอะไรอยู่ตรงไหน เรียงอย่างไร
  from   หัวข้อของ README.md ที่ภาพนี้อธิบาย · ขั้นตอนข้างภาพในสไลด์อ่านจากตารางของหัวข้อนั้นตอนสร้าง
         (build_slides.py) จึงไม่พิมพ์ซ้ำที่นี่ และตัวเลขตรงกับ README เสมอ
PHOTOS = ภาพถ่ายสมจริงของหน้าปกและหน้าคั่น (ไม่มีตัวอักษรในภาพ · ฝั่งซ้ายมืดไว้วางหัวข้อ)

  python tools/slides_figures.py <โฟลเดอร์ปลายทาง นอกรีโป> [ภาพอ้างอิงสไตล์ ...]
      เขียนพรอมต์ 1 ไฟล์ต่อภาพ (<img>.txt)
      ภาพอ้างอิงสไตล์ของบทนี้: img/g02-three-agents.png และ img/g09-adaptor.png (ภาพการ์ตูนเดิมของบททฤษฎี)
      ONLY=n02-broad-policy,s03-run = เขียนเฉพาะภาพที่ระบุ
"""
import os, sys

SETTING = 'a small cozy Thai neighborhood coffee shop called "BaanKafe" (wooden counter, espresso machine, plants)'   # ฉากของบท

FIGS = [
    {"img": "n01-tune-skill", "title": "ปรับสกิล ไม่แตะโมเดล", "from": "ขั้น 2",
     "labels": ["เทรนโมเดล: แก้น้ำหนักของโมเดล", "ปรับสกิล: แก้ข้อความที่โมเดลอ่าน", "SKILL.md"],
     "scene": "Two panels side by side. Left panel: a grey mechanical arm holding a screwdriver reaches into the opened head panel of "
              "the white robot, where small gears and dials are visible; the robot looks dizzy with swirl eyes. Pill label under the "
              "left panel (orange): 'เทรนโมเดล: แก้น้ำหนักของโมเดล'. Right panel: the head of the white robot with an orange scarf "
              "stays closed and untouched; a second white robot with a teal scarf hands it a single one-page checklist card; the card "
              "has a small monospace tag 'SKILL.md'; the barista stands behind them, reads the card too and gives a thumbs up. "
              "Pill label under the right panel (teal): 'ปรับสกิล: แก้ข้อความที่โมเดลอ่าน'."},
    {"img": "n02-broad-policy", "title": "กฎที่กว้างเกินหลักฐาน", "from": "9.4",
     "labels": ["1 หลักฐาน: เงินคืนสมาชิก ปัดลง", "2 กฎที่เขียน: เงินจ่ายออกทุกชนิด ปัดลง", "3 งานคืนเงินคอร์สใน Test: ผิด"],
     "scene": "Three numbered scenes left to right connected by arrows. (1) The white robot with a teal scarf studies ONE small answer "
              "sheet through a magnifying glass; the sheet shows a single coin with one arrow pointing down. (2) The same robot "
              "paints one big rule poster on the wall; the poster shows four different money icons (a coin, a banknote, a gift "
              "voucher, a piggy bank), every one with an arrow pointing down. (3) The white robot with an orange scarf stands at "
              "the cash register and hands some coins to a customer while following the poster; next to it a simple grey checking "
              "machine with a dial shows a big red cross. Each scene has its numbered label below it."},
    {"img": "n03-separate-adaptor", "title": "ผู้ถูกวัดต้องไม่เป็นผู้กำหนดการวัด", "from": "11.5",
     "labels": ["Agent เดียว: กำหนดการวัดและถูกวัด", "แยก Agent: ล็อกการวัดก่อนมีสกิลตัวแรก", "Benchmark Adaptor", "Evolver"],
     "scene": "Two panels side by side. Left panel: one white robot (no scarf) holds a ruler in one hand and with the other hand "
              "sneakily pulls two exam sheets marked with red crosses off a cork board and drops them into a bin, a gold star "
              "sticker on its own chest. Pill label under the left panel (red): 'Agent เดียว: กำหนดการวัดและถูกวัด'. Right panel: "
              "on the left side a white robot with a green scarf closes a glass cabinet with a padlock; inside the cabinet are a "
              "ruler and a neat stack of exam sheets; a small tag under this robot: 'Benchmark Adaptor'. On the right side, at a "
              "separate desk, a white robot with a teal scarf writes on a checklist card and cannot reach the cabinet; a small tag "
              "under this robot: 'Evolver'. Pill label under the right panel (green): 'แยก Agent: ล็อกการวัดก่อนมีสกิลตัวแรก'."},
    {"img": "n04-score-only", "title": "ผู้ใช้ให้ตัวตรวจ Evolver ได้แต่คะแนน", "from": "11.6",
     "labels": ["1 ผู้ใช้เขียนตัวตรวจ", "2 ตัวตรวจให้คะแนน 0 ถึง 1", "3 Evolver เห็นแค่ตัวเลข", "0.9"],
     "scene": "Three numbered scenes left to right connected by arrows. (1) The barista tightens a bolt on a simple grey checking "
              "machine with a dial (a machine, not a character) using a wrench, a clipboard with ticks beside her. (2) The checking "
              "machine examines a work folder and prints a long paper strip with several small ticks and one red cross; the strip "
              "drops into a glass box closed with a padlock. (3) Through a small hatch in a brick wall only one small card comes "
              "out; the card shows the text '0.9' in large monospace digits; the white robot with a teal scarf holds the card and "
              "looks puzzled, a small question mark above its head. Each scene has its numbered label below it."},
    {"img": "n05-validation-meter", "title": "Validation คือมาตรวัดสำหรับคน", "from": "11.7",
     "labels": ["1 Solver ทำโจทย์ Validation ทุก epoch", "2 คะแนนถูกบันทึกให้คนดู", "3 Evolver ไม่เห็น"],
     "scene": "Three numbered scenes left to right. (1) The white robot with an orange scarf works on a small stack of exam sheets "
              "at a laptop. (2) A wall chart with a simple rising line made of four dots (no numbers, no axis text); the barista "
              "stands in front of the chart holding a clipboard and studies it. (3) Behind a low brick wall, with its back to the "
              "chart, the white robot with a teal scarf writes on a checklist card at a desk; it cannot see the chart. Each scene "
              "has its numbered label below it."},
    {"img": "n06-short-prompt", "title": "prompt สั้น กติกาอยู่ที่โครงของเครื่อง", "from": "11.8",
     "labels": ["prompt ยาว: กำหนดวิธีทำทุกขั้น", "prompt สั้น: บอกแค่ 3 เรื่อง", "อ่านอย่างเดียว", "เขียนได้"],
     "scene": "Two panels side by side. Left panel: the white robot with a teal scarf is wrapped in one very long paper scroll full "
              "of tiny unreadable squiggle lines that unrolls across the floor; the robot looks overwhelmed. Pill label under the "
              "left panel (orange): 'prompt ยาว: กำหนดวิธีทำทุกขั้น'. Right panel: the same robot looks relaxed and holds one tiny "
              "note card; behind it stands a wooden shelf unit: the upper shelves hold ring binders behind a glass door closed "
              "with a padlock, with a small tag 'อ่านอย่างเดียว'; below is one open drawer with a pencil and blank cards, with a "
              "small tag 'เขียนได้'. Pill label under the right panel (teal): 'prompt สั้น: บอกแค่ 3 เรื่อง'."},
]

PHOTOS = [
    {"img": "s01-cover", "scene": "Close view of a wooden cafe counter: a young developer's hands type on a laptop whose screen is "
                                  "blurred; beside the laptop stand three slim ring binders in green, orange and teal, and a cup "
                                  "of latte. In the soft background a barista works at the espresso machine. Mood: a small team "
                                  "of assistants improving a playbook together."},
    {"img": "s02-concept", "scene": "On a wooden cafe table, three things in a row: a small cardboard box of neatly sorted blank "
                                    "paper cards closed with a little brass padlock, an open laptop with a blurred screen, and an "
                                    "open notebook with a pencil lying on it. A hand rests on the notebook. Mood: preparing, "
                                    "doing and reviewing, in that order."},
    {"img": "s03-run", "scene": "A software engineer sits at a small cafe table in the evening and follows a long printed paper "
                                "strip of results with one finger; the marks on the strip are blurred and abstract; an open "
                                "laptop beside the strip shows only blurred abstract coloured bars; the other hand holds a "
                                "pencil over a paper pad with abstract boxes and arrows. Mood: walking through one real run "
                                "and weighing design choices."},
    {"img": "s04-evidence", "scene": "Two colleagues sit side by side at a cafe table and compare two printed sheets with blurred "
                                     "abstract bar charts lying next to each other; one of them points at a sheet with a pen "
                                     "while the other holds a coffee cup and looks closely; a closed laptop at the edge of the "
                                     "table. Mood: comparing evidence from two sources."},
]

CARTOON = """Generate ONE illustration with your image generation tool and save it as a PNG file at exactly this path:
{out}/{img}.png

First open and look at these reference images, then match their illustration style exactly (same kind of flat kawaii cartoon
infographic, warm cream background, decorations of the setting, large bold dark-brown Thai title lettering at the top, thick
dark-brown outlines, rounded panels, coloured rounded pill labels, numbered circle badges, palette of teal, orange, green, red and
brown, bold rounded Thai lettering):
{refs}

Canvas: landscape 4:3 (about 1448 x 1086). Setting: {setting}.

Title text at the top (exact): {title}

Scene: {scene}

Text labels to place in the picture, each next to the element it names (exact text, one label per line below):
{labels}

Strict text rules:
- Write every label EXACTLY as given, character by character. Thai stays Thai, English stays English, numbers and symbols stay as they are.
- Each label appears exactly once. Do NOT add any other words, numbers, captions, watermarks or logos beyond the title and the labels above.
- When a label starts with a number (for example "3 gate"), draw that number ONLY inside the circle badge and write the rest of the label next to it. Never show the same number twice.
- Text must be large, bold and easy to read from the back of a classroom. Code-like labels (file names, JSON, exit codes) use a monospace font.
- Characters (same as in the references): a small white robot with teal ear pieces and an orange antenna ball represents an AI agent. When a scene has more than one robot they look the same and differ only by scarf colour: green scarf = Benchmark Adaptor, orange scarf = Solver, teal scarf = Evolver. The barista is a young woman with a brown hair bun, an orange ribbon and a brown apron; she represents the user. Fictional cartoon characters only.

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
        img = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "img")
        refs = [os.path.join(img, n).replace("\\", "/") for n in ("g02-three-agents.png", "g09-adaptor.png")]
    only = set(os.environ.get("ONLY", "").split(",")) - {""}       # ONLY=n03-separate-adaptor,s02-concept = เขียนเฉพาะภาพที่ระบุ
    os.makedirs(out, exist_ok=True)
    n = 0
    for f in FIGS:
        if only and f["img"] not in only:
            continue
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(CARTOON.format(
            out=out, img=f["img"], refs="\n".join(refs), setting=SETTING, title=f["title"], scene=f["scene"], labels="\n".join(f["labels"])))
        n += 1
    for f in PHOTOS:
        if only and f["img"] not in only:
            continue
        open(os.path.join(out, f["img"] + ".txt"), "w", encoding="utf-8").write(PHOTO.format(out=out, img=f["img"], setting=SETTING, scene=f["scene"]))
        n += 1
    print("%d พรอมต์ -> %s" % (n, out))
