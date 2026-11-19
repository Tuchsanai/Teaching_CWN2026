"""Example detections on the test split at the frozen threshold: TP / FN / FP / TN image-level cases of NO_HARDHAT."""
import argparse, json, sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--team", required=True)
p.add_argument("--data", type=Path, required=True)
p.add_argument("--model", required=True)
p.add_argument("--threshold", type=Path, required=True)
p.add_argument("--out", type=Path, required=True)
p.add_argument("--per-case", type=int, default=4)
a = p.parse_args()
sys.path.insert(0, a.team)
import evaluate as ev
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

thr = ev.read_threshold(a.threshold)
aliases = ev.read_class_aliases(Path(a.team, "classes.json"))
images, actual = ev.load_test_set(a.data, aliases, enforce_size=False)
model = YOLO(a.model, task="detect")
ids, _ = ev.class_ids(model.names, aliases, a.model)
target = sorted(set().union(*ids.values()))
colors = {"NO_HARDHAT": (230, 30, 30), "NO_VEST": (255, 150, 0)}
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
except OSError:
    font = ImageFont.load_default()
cases = {"TP": [], "FN": [], "FP": [], "TN": []}
listing = []
for path, present in zip(images, actual["NO_HARDHAT"]):
    with Image.open(path) as src:
        im = src.convert("RGB")
    (r,) = model.predict(source=im, conf=max(0.0, thr - 1e-7), classes=target, imgsz=640, device=0, verbose=False)
    boxes = [(int(k), c, b) for k, c, b in
             zip(r.boxes.cls.tolist(), r.boxes.conf.tolist(), r.boxes.xyxy.tolist()) if c >= thr]
    h = sum(1 for k, _, _ in boxes if k in ids["NO_HARDHAT"])
    v = sum(1 for k, _, _ in boxes if k in ids["NO_VEST"])
    case = ("TP" if h else "FN") if present else ("FP" if h else "TN")
    listing.append({"image": path.name, "case": case, "H": h, "V": v})
    if len(cases[case]) >= a.per_case:
        continue
    d = ImageDraw.Draw(im)
    for k, c, b in boxes:
        n = "NO_HARDHAT" if k in ids["NO_HARDHAT"] else "NO_VEST"
        d.rectangle(b, outline=colors[n], width=3)
        d.text((b[0] + 3, max(0, b[1] - 20)), f"{n} {c:.2f}", fill=colors[n], font=font)
    im = im.resize((480, 480))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 480, 26), fill=(0, 0, 0))
    d.text((5, 3), f"{case} | GT no-hardhat: {'yes' if present else 'no'} | H={h} V={v}",
           fill=(255, 255, 255), font=font)
    cases[case].append(im)
a.out.mkdir(parents=True, exist_ok=True)
rows = [(c, ims) for c, ims in cases.items() if ims]
sheet = Image.new("RGB", (480 * a.per_case, 480 * len(rows)), (255, 255, 255))
for y, (c, ims) in enumerate(rows):
    for x, im in enumerate(ims):
        sheet.paste(im, (480 * x, 480 * y))
sheet.save(a.out / "examples_test_predictions.jpg", quality=88)
(a.out / "test_image_results.json").write_text(
    json.dumps({"conf_threshold": thr, "images": listing}, indent=1), encoding="utf-8")
print("EXAMPLES", {c: sum(1 for item in listing if item["case"] == c) for c in cases})
