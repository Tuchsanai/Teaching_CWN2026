"""Make a 4x2 grid of 8 Training Set images with boxes + class names drawn from the real YOLO labels.
Usage: python show_samples.py [dataset_dir] [out.jpg]"""
import sys, random
from pathlib import Path
import cv2, numpy as np, yaml

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/hardhat")
out = sys.argv[2] if len(sys.argv) > 2 else "/workspace/dataset_samples.jpg"
names = yaml.safe_load(open(root / "data.yaml"))["names"]
COLORS = {"head": (0, 0, 255), "helmet": (0, 200, 0)}          # BGR: no helmet = red, helmet = green
CELL = 416

imgs = sorted((root / "train/images").glob("*.jpg"))
random.seed(13)
picked = []
for p in random.sample(imgs, len(imgs)):                       # prefer images that show both classes
    lab = root / "train/labels" / (p.stem + ".txt")
    cls = {int(l.split()[0]) for l in open(lab) if l.strip()}
    if len(cls) == 2 or (len(picked) >= 4 and cls):
        picked.append((p, lab))
    if len(picked) == 8:
        break

tiles = []
for p, lab in picked:
    im = cv2.imread(str(p)); h, w = im.shape[:2]
    for line in open(lab):
        if not line.strip():
            continue
        c, xc, yc, bw, bh = line.split()
        c = int(c); xc, yc, bw, bh = float(xc) * w, float(yc) * h, float(bw) * w, float(bh) * h
        x1, y1, x2, y2 = int(xc - bw / 2), int(yc - bh / 2), int(xc + bw / 2), int(yc + bh / 2)
        col = COLORS.get(names[c], (255, 0, 0))
        cv2.rectangle(im, (x1, y1), (x2, y2), col, 2)
        (tw, th), _ = cv2.getTextSize(names[c], cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        ty = max(y1, th + 4)
        cv2.rectangle(im, (x1, ty - th - 4), (x1 + tw + 4, ty), col, -1)
        cv2.putText(im, names[c], (x1 + 2, ty - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
    tiles.append(cv2.resize(im, (CELL, CELL)))

grid = np.vstack([np.hstack(tiles[i:i + 4]) for i in (0, 4)])
cv2.imwrite(out, grid, [cv2.IMWRITE_JPEG_QUALITY, 90])
print("saved", out, grid.shape, "from", [p.name for p, _ in picked])
