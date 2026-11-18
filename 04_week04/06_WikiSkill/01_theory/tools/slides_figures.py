#!/usr/bin/env python3
"""ภาพใหม่ของสไลด์บททฤษฎี WikiSkill (ใช้โดย tools/build_slides.py)

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
      ภาพอ้างอิงสไตล์ของบทนี้: img/g01-three-layers.png และ img/g05-two-roles.png (ภาพการ์ตูนเดิมของบททฤษฎี)
"""
import os, sys

SETTING = 'a small cozy Thai neighborhood coffee shop called "BaanKafe" (wooden counter, espresso machine, plants)'   # ฉากของบท

FIGS = [
    {"img": "n01-compile", "title": "คอมไพล์ประสบการณ์เป็นความรู้", "from": "ขั้น 3",
     "labels": ["ของดิบ", "สิ่งที่เรียบเรียงแล้ว", "สิ่งที่ใช้ทำงาน", "เขียนโปรแกรม", "ร้านกาแฟ", "นักเรียน", "Trace", "Wiki", "สกิล"],
     "scene": "A tidy grid with three columns and three picture rows. Three column header pills across the top, left to right: the label "
              "'ของดิบ' (brown), 'สิ่งที่เรียบเรียงแล้ว' (teal), 'สิ่งที่ใช้ทำงาน' (orange). Each row has a small row tag on the far left and "
              "three small pictures joined by orange arrows pointing right. Row 'เขียนโปรแกรม': a sheet of source code with angle brackets, "
              "then a closed package box with a gear on it, then a small app window with a play button. Row 'ร้านกาแฟ': a pile of loose "
              "daily paper slips, then a thick bound notebook, then a single one-page checklist card held by the barista. Row 'นักเรียน': "
              "old exam papers with red crosses, then a neat summary notebook, then a tiny formula card. Under the three columns, a bottom "
              "row of three big pills aligned with the columns: 'Trace' (brown), 'Wiki' (teal), 'สกิล' (orange). The white robot stands "
              "at the right edge pointing at the grid."},
    {"img": "n02-skill-short", "title": "ทำไมไม่ให้สกิลเก็บความรู้เอง", "from": "8.1",
     "labels": ["เขียนทุกอย่างลงสกิล", "แยกชั้นความรู้ออกมา", "SKILL.md", "Wiki"],
     "scene": "Two panels side by side. Left panel: the barista is buried behind one enormous thick manual that unrolls onto the floor, "
              "looking tired, while coffee cups wait on the counter. Pill label under the left panel (red): 'เขียนทุกอย่างลงสกิล'. "
              "Right panel: the barista happily makes coffee while glancing at one short single-page checklist card pinned next to her, "
              "the card has a small tag 'SKILL.md'; behind her on a shelf the white robot keeps a thick bound notebook with a small tag "
              "'Wiki'. Pill label under the right panel (teal): 'แยกชั้นความรู้ออกมา'."},
    {"img": "n03-raw-immutable", "title": "Raw Layer ห้ามแก้", "from": "8.2",
     "labels": ["1 เก็บ Trace ดิบไว้ครบ", "2 Wiki คือการตีความ", "3 กลับไปดูของจริงก่อนเสนอ", "ไม่แก้ ไม่ลบ"],
     "scene": "Three numbered scenes left to right connected by arrows. (1) A glass display cabinet with a padlock, full of original "
              "paper slips, a small sign pill on the glass 'ไม่แก้ ไม่ลบ'. (2) The white robot wearing a teal scarf writes a summary into "
              "an open notebook. (3) The white robot wearing an orange scarf holds a photocopy of one paper slip and compares it with the "
              "notebook using a magnifying glass. Each scene has its numbered label below it."},
    {"img": "n04-program-record", "title": "skill-impact.md เขียนโดยโปรแกรม", "from": "8.6",
     "labels": ["โมเดลเล่าเอง: อาจจำคลาด", "โปรแกรมจด: ข้อเท็จจริงจากการวัด", "diff", "คะแนน", "รับ / ไม่รับ"],
     "scene": "Two panels side by side. Left panel: the white robot proudly tells a story with a speech bubble that contains only a "
              "wobbly star and a question mark, holding a medal it drew for itself. Pill label under the left panel (red): "
              "'โมเดลเล่าเอง: อาจจำคลาด'. Right panel: a simple grey measuring machine with a dial and gears (a machine, not a character) "
              "prints a long paper strip that feeds into an open notebook; the strip has three rows, each with a small icon and a tag: "
              "plus and minus lines with the tag 'diff', a gauge with the tag 'คะแนน', a tick and a cross with the tag 'รับ / ไม่รับ'. "
              "Pill label under the right panel (green): 'โปรแกรมจด: ข้อเท็จจริงจากการวัด'."},
    {"img": "n05-small-patch", "title": "ข้อเสนอต้องเล็ก: แก้ทีละจุด", "from": "8.9",
     "labels": ["เขียนทับทั้งไฟล์: กฎเดิมตกหล่น", "patch: แตะเฉพาะจุดที่ระบุ", "ข้อเสนอ 1 ข้อต่อรอบ"],
     "scene": "Two panels side by side. Left panel: the white robot wearing an orange scarf swaps a whole checklist page for a brand new "
              "page, and several green-ticked rule lines fall off the old page onto the floor. Pill label under the left panel (red): "
              "'เขียนทับทั้งไฟล์: กฎเดิมตกหล่น'. Right panel: the same robot carefully sticks one small orange patch sticker onto a single "
              "line of the checklist page, every other green-ticked line stays in place. Pill label under the right panel (green): "
              "'patch: แตะเฉพาะจุดที่ระบุ'. A small yellow rounded tag (plain text, no circle badge) at the top right corner of the right "
              "panel: 'ข้อเสนอ 1 ข้อต่อรอบ'."},
    {"img": "n06-strict-gate", "title": "Gate รับเฉพาะเมื่อดีกว่า", "from": "8.10",
     "labels": ["1 มากกว่า R_best: รับ", "2 เท่ากัน: ไม่รับ", "3 R_best = 100%: หยุด"],
     "scene": "Three numbered scenes left to right. Each scene shows the same wooden garden gate and a vertical score bar with a "
              "horizontal dashed line marking the best score so far. (1) A checklist page whose score bar is clearly above the dashed "
              "line walks through the open gate, a green tick flag on the gate. (2) A checklist page whose score bar is exactly level with "
              "the dashed line is stopped in front of the closed gate, a red cross flag on the gate. (3) The score bar is completely "
              "full and the white robot raises a small finish flag next to a trophy. Each scene has its numbered label below it."},
]

PHOTOS = [
    {"img": "s01-cover", "scene": "Close view of a wooden counter: a thick worn hardcover notebook lies open next to a laptop and a cup of "
                                  "latte; a young developer's hands write in the notebook with a pencil. In the soft background a barista "
                                  "works at the espresso machine. Mood: experience being written down as lasting knowledge."},
    {"img": "s02-how", "scene": "On a wooden table: a messy pile of loose handwritten order slips and receipts, next to it a neat thick "
                                "bound notebook, and next to that one single laminated card. A hand moves one slip from the pile toward "
                                "the notebook. Mood: raw notes being organised step by step."},
    {"img": "s03-design", "scene": "A thoughtful software engineer sits at a small table and sketches abstract boxes and arrows on a "
                                   "paper pad with a pencil, chin resting on the other hand, a closed laptop and a coffee cup beside the "
                                   "pad. Mood: careful design thinking, weighing options."},
    {"img": "s04-evidence", "scene": "Two colleagues sit side by side at a table and review results on a laptop; the screen shows only "
                                     "blurred abstract coloured bars; one of them points at the screen while the other takes notes in a "
                                     "notebook. Mood: checking evidence together."},
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
- Characters (same as in the references): a small white robot with teal ear pieces and an orange antenna ball represents the AI; the barista is a young woman with a brown hair bun, an orange ribbon and a brown apron. Fictional cartoon characters only.

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
        refs = [os.path.join(img, n).replace("\\", "/") for n in ("g01-three-layers.png", "g05-two-roles.png")]
    only = set(os.environ.get("ONLY", "").split(",")) - {""}       # ONLY=n03-raw-immutable,s02-how = เขียนเฉพาะภาพที่ระบุ
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
