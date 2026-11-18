"""ภาพตาราง 6 รูปที่ใช้ยิงโหลด: วาดกรอบ+คลาสจากคำตอบ API จริง กำกับขนาดไฟล์/ขนาดภาพ"""
import json, os
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

# python make_grid.py [โฟลเดอร์ผลที่มี test_single.json] [โฟลเดอร์รูป]  (ค่าเริ่ม ../results ../samples)
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "results")
SAMPLES = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "samples")
rep = json.load(open(os.path.join(RES, "test_single.json"), encoding="utf-8"))

COLORS = {"Hardhat": (46, 160, 67), "Safety Vest": (31, 119, 180), "Mask": (23, 190, 207),
          "NO-Hardhat": (214, 39, 40), "NO-Safety Vest": (255, 127, 14), "NO-Mask": (227, 119, 194),
          "Person": (148, 103, 189), "Safety Cone": (188, 189, 34), "machinery": (140, 86, 75),
          "vehicle": (127, 127, 127)}


def font(sz, bold=False):
    for p in [f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


F_LBL, F_CAP, F_SUB = font(13, True), font(20, True), font(16)
TILE, CAP_H, PAD, COLS = 640, 92, 16, 3
items = rep["detect"]
rows = (len(items) + COLS - 1) // COLS
W = COLS * TILE + (COLS + 1) * PAD
H = rows * (TILE + CAP_H) + (rows + 1) * PAD
canvas = Image.new("RGB", (W, H), "white")
summary = []
for i, it in enumerate(items):
    path = os.path.join(SAMPLES, it["file"])
    img = Image.open(path).convert("RGB")
    w0, h0 = img.size
    d = ImageDraw.Draw(img)
    for det in it["response"]["detections"]:
        x1, y1, x2, y2 = det["box"]
        c = COLORS.get(det["class"], (0, 0, 0))
        d.rectangle([x1, y1, x2, y2], outline=c, width=3)
        t = f'{det["class"]} {det["confidence"]:.2f}'
        tw, th = d.textbbox((0, 0), t, font=F_LBL)[2:]
        ty = y1 - th - 4 if y1 - th - 4 > 0 else y1
        d.rectangle([x1, ty, x1 + tw + 6, ty + th + 4], fill=c)
        d.text((x1 + 3, ty + 1), t, fill="white", font=F_LBL)
    img = img.resize((TILE, round(TILE * h0 / w0))) if w0 != TILE else img
    r, c = divmod(i, COLS)
    x = PAD + c * (TILE + PAD)
    y = PAD + r * (TILE + CAP_H + PAD)
    canvas.paste(img, (x, y))
    kb = os.path.getsize(path) / 1024
    cnt = Counter(det["class"] for det in it["response"]["detections"])
    dc = ImageDraw.Draw(canvas)
    dc.text((x, y + TILE + 8), f'{it["file"]}  ·  {kb:.1f} KB  ·  {w0}x{h0} px  ·  {sum(cnt.values())} objects',
            fill="black", font=F_CAP)
    line = ", ".join(f"{k} {v}" for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]))
    # ตัดเป็น 2 บรรทัดถ้ายาว
    words, l1, l2 = line.split(", "), "", ""
    for wd in words:
        if dc.textlength(l1 + wd, font=F_SUB) < TILE - 10 and not l2:
            l1 += ("" if not l1 else ", ") + wd
        else:
            l2 += ("" if not l2 else ", ") + wd
    dc.text((x, y + TILE + 38), l1, fill=(60, 60, 60), font=F_SUB)
    dc.text((x, y + TILE + 60), l2, fill=(60, 60, 60), font=F_SUB)
    summary.append({"file": it["file"], "kb": round(kb, 1), "size": f"{w0}x{h0}", "counts": dict(cnt)})

out = os.path.join(RES, "dataset_samples.jpg")
canvas.save(out, quality=90)
print(out, canvas.size)
print(json.dumps(summary, ensure_ascii=False, indent=1))
