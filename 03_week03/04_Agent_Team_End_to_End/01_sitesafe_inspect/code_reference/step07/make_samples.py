"""Make a 2x4 grid of 8 training images with the real label boxes and class names drawn on."""
import glob, json, os, random, sys, yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/workspace/e2e_sitesafe/dataset"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/workspace/e2e_sitesafe/dataset_samples.jpg"
names = yaml.safe_load(open(os.path.join(ROOT, "data.yaml")))["names"]
if isinstance(names, dict):
    names = [names[k] for k in sorted(names)]
COLORS = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe"]
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
except OSError:
    font = ImageFont.load_default()

def read(lf):
    rows = []
    for l in open(lf).read().splitlines():
        p = l.split()
        if len(p) >= 5:
            c = int(p[0]); v = list(map(float, p[1:]))
            if len(v) == 4:
                x, y, w, h = v
            else:  # polygon -> enclosing box
                xs, ys = v[0::2], v[1::2]; x, y, w, h = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, max(xs)-min(xs), max(ys)-min(ys)
            rows.append((c, x, y, w, h))
    return rows

random.seed(28)
imgs = sorted(glob.glob(os.path.join(ROOT, "train", "images", "*.jpg")))
random.shuffle(imgs)
picked = []
for im in imgs:  # prefer images with 3-12 boxes and several classes so the labels are readable
    lf = os.path.join(ROOT, "train", "labels", os.path.splitext(os.path.basename(im))[0] + ".txt")
    rows = read(lf) if os.path.exists(lf) else []
    if 3 <= len(rows) <= 12 and len({r[0] for r in rows}) >= 3:
        picked.append((im, lf, rows))
    if len(picked) == 8:
        break

T = 480
grid = Image.new("RGB", (4 * T, 2 * T), "white")
for k, (im, lf, rows) in enumerate(picked):
    img = Image.open(im).convert("RGB").resize((T, T))
    d = ImageDraw.Draw(img)
    for c, x, y, w, h in rows:
        x1, y1, x2, y2 = (x - w / 2) * T, (y - h / 2) * T, (x + w / 2) * T, (y + h / 2) * T
        col = COLORS[c % len(COLORS)]
        d.rectangle([x1, y1, x2, y2], outline=col, width=3)
        tb = d.textbbox((0, 0), names[c], font=font)
        ty = max(0, y1 - (tb[3] + 4))
        d.rectangle([x1, ty, x1 + tb[2] + 6, ty + tb[3] + 4], fill=col)
        d.text((x1 + 3, ty + 1), names[c], fill="black", font=font)
    d.rectangle([0, T - 22, 30, T], fill="black"); d.text((8, T - 20), str(k + 1), fill="white", font=font)
    grid.paste(img, ((k % 4) * T, (k // 4) * T))
grid.save(OUT, quality=90)
first = picked[0]
json.dump({"samples": [os.path.basename(p[0]) for p in picked], "first_image": os.path.basename(first[0]),
           "first_image_size": Image.open(first[0]).size, "first_label_lines": open(first[1]).read().splitlines()},
          open(os.path.join(os.path.dirname(OUT), "samples_info.json"), "w"), indent=1)
print("saved", OUT, grid.size)
print("first image:", os.path.basename(first[0]), Image.open(first[0]).size)
print(open(first[1]).read())
