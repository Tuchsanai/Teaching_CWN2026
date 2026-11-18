"""Count images/boxes per split and draw an 8-image grid of ground-truth boxes from the training set."""
import json, random, sys
from collections import Counter
from pathlib import Path
import cv2, numpy as np, yaml

root = Path(sys.argv[1]); out = sys.argv[2]
names = yaml.safe_load(open(root / "data.yaml"))["names"]
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def labels_of(img):
    lp = img.parent.parent / "labels" / (img.stem + ".txt")
    rows = []
    if lp.exists():
        for line in lp.read_text().split("\n"):
            p = line.split()
            if len(p) >= 5:
                c = int(p[0]); xs = list(map(float, p[1:]))
                if len(xs) == 4: cx, cy, w, h = xs
                else:  # polygon -> bbox
                    px, py = xs[0::2], xs[1::2]
                    cx, cy, w, h = (min(px)+max(px))/2, (min(py)+max(py))/2, max(px)-min(px), max(py)-min(py)
                rows.append((c, cx, cy, w, h))
    return rows

stats = {"splits": {}, "classes": names}
train_imgs, train_labels = [], {}
for split in ["train", "valid", "test"]:
    imgs = sorted(p for p in (root / split / "images").glob("*") if p.suffix.lower() in IMG_EXT)
    cnt = Counter()
    for im in imgs:
        lab = labels_of(im); cnt.update(c for c, *_ in lab)
        if split == "train": train_labels[im] = lab
    stats["splits"][split] = {"images": len(imgs), "boxes": sum(cnt.values()),
                              "boxes_per_class": {names[k]: cnt.get(k, 0) for k in range(len(names))}}
print(json.dumps(stats, ensure_ascii=False, indent=1))

# greedy pick: 8 images that together cover the most classes (rare classes weighted higher)
freq = Counter(c for lab in train_labels.values() for c, *_ in lab)
random.seed(0)
cands = [im for im, lab in train_labels.items() if 2 <= len(lab) <= 25]
random.shuffle(cands)
chosen, covered = [], Counter()
for _ in range(8):
    def score(im):
        cls = {c for c, *_ in train_labels[im]}
        return sum(1.0 / (1 + covered[c]) / np.log(2 + freq[c]) for c in cls)
    best = max((im for im in cands if im not in chosen), key=score)
    chosen.append(best); covered.update({c for c, *_ in train_labels[best]})

rng = np.random.RandomState(3)
colors = {k: tuple(int(v) for v in rng.randint(40, 255, 3)) for k in range(len(names))}
T = 480; tiles = []
for im in chosen:
    img = cv2.imread(str(im)); H, W = img.shape[:2]; s = T / max(H, W)
    img = cv2.resize(img, (int(W * s), int(H * s)))
    canvas = np.full((T, T, 3), 30, np.uint8); canvas[:img.shape[0], :img.shape[1]] = img
    h, w = img.shape[:2]
    for c, cx, cy, bw, bh in train_labels[im]:
        x1, y1 = int((cx - bw/2) * w), int((cy - bh/2) * h); x2, y2 = int((cx + bw/2) * w), int((cy + bh/2) * h)
        col = colors[c]; cv2.rectangle(canvas, (x1, y1), (x2, y2), col, 2)
        txt = names[c]; (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        ty = max(y1, th + 4); cv2.rectangle(canvas, (x1, ty - th - 4), (x1 + tw + 4, ty), col, -1)
        cv2.putText(canvas, txt, (x1 + 2, ty - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
    tiles.append(cv2.copyMakeBorder(canvas, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=(255, 255, 255)))
grid = np.vstack([np.hstack(tiles[:4]), np.hstack(tiles[4:])])
cv2.imwrite(out, grid, [cv2.IMWRITE_JPEG_QUALITY, 90])
print("classes shown:", sorted(names[c] for c in covered), f"({len(covered)}/{len(names)})")
