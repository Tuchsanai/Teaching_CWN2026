#!/usr/bin/env python3
"""ตัดภาพบางส่วนจากภาพหน้าจอคำตอบจริงและภาพผลของบท ไปไว้ที่ img/cNN-*.jpg สำหรับสไลด์

  python tools/make_crops.py            (รันจากโฟลเดอร์ lab2_vlm)

ทุกภาพเป็นการตัด (crop) สำเนาของภาพเดิมเท่านั้น ไม่แก้พิกเซลในบริเวณที่ตัด · ภาพเดิมไม่ถูกแก้
c09 c10 = ชิ้นที่ตัดจาก results/eval/images/examples.jpg หลายชิ้น (ชื่อใบ เฉลย Base Fine-tuned) วางเรียงกันบนพื้นขาว
"""
from PIL import Image

CROPS = [
    # (ไฟล์ปลายทาง, ภาพต้นทาง, (x0, y0, x1, y1))
    ("c01-step1-table", "image/lab2-step1.png", (60, 780, 1710, 1250)),
    ("c02-step2-split", "image/lab2-step2.png", (60, 1545, 1700, 2160)),
    ("c03-step3-table", "image/lab2-step3.png", (60, 900, 1710, 1475)),
    ("c04-step4-tests", "image/lab2-step4.png", (60, 890, 1710, 1470)),
    ("c06-step6-table", "image/lab2-step6.png", (60, 1030, 1700, 1650)),
    ("c07-step7-cost", "image/lab2-step7.png", (60, 1545, 1710, 2190)),
    ("c08-step8-params", "image/lab2-step8.png", (60, 1510, 1710, 2092)),
    ("c11-step9-cost", "image/lab2-step9.png", (60, 2150, 1710, 2490)),
    ("c13-train234", "results/dataset_samples.jpg", (972, 255, 1395, 1025)),
]

# examples.jpg (2520 x 2340): แต่ละแถว = 1 ใบ · คอลัมน์ข้อความ เฉลย / Base / Fine-tuned
EX = "results/eval/images/examples.jpg"
S = 2520 / 1990.0
ROWS = {"test_040": (80, 280), "test_051": (520, 770), "test_086": (960, 1160), "test_091": (1400, 1675)}
COLS = [(425, 735), (945, 1255), (1465, 1775)]
NAME_X = (165, 265)


def px(v):
    return int(round(v * S))


def example_strip(im, name):
    top, bot = ROWS[name]
    pieces = [im.crop((px(NAME_X[0]), px(top), px(NAME_X[1]), px(top + 22)))]
    pieces += [im.crop((px(a), px(top), px(b), px(bot))) for a, b in COLS]
    gap = 24
    w = sum(p.width for p in pieces) + gap * (len(pieces) - 1)
    h = max(p.height for p in pieces)
    out = Image.new("RGB", (w, h), "white")
    x = 0
    for p in pieces:
        out.paste(p, (x, 0))
        x += p.width + gap
    return out


def stack(strips, gap=40):
    w = max(s.width for s in strips)
    h = sum(s.height for s in strips) + gap * (len(strips) - 1)
    out = Image.new("RGB", (w, h), "white")
    y = 0
    for s in strips:
        out.paste(s, (0, y))
        y += s.height + gap
    return out


if __name__ == "__main__":
    for name, src, box in CROPS:
        Image.open(src).convert("RGB").crop(box).save("img/%s.jpg" % name, quality=92)
        print("img/%s.jpg" % name, box)
    im = Image.open(EX).convert("RGB")
    stack([example_strip(im, "test_040"), example_strip(im, "test_051")]).save("img/c09-examples-a.jpg", quality=92)
    stack([example_strip(im, "test_086"), example_strip(im, "test_091")]).save("img/c10-examples-b.jpg", quality=92)
    print("img/c09-examples-a.jpg img/c10-examples-b.jpg")
