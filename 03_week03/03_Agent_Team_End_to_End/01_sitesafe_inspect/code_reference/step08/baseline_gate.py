"""Image-level NFR-01 numbers for the checkpoint BEFORE training (COCO weights).

The COCO model has no NO_HARDHAT / NO_VEST class, so the team's evaluate.py stops with
"no class name matches". The system would report H = 0 and V = 0 for every image; this script
writes that result with the team's own counting function so before/after use one definition.
"""
import argparse, json, sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--team", required=True)
p.add_argument("--data", type=Path, required=True)
p.add_argument("--model", required=True)
p.add_argument("--threshold", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
sys.path.insert(0, a.team)
import evaluate as ev
from ultralytics import YOLO

aliases = ev.read_class_aliases(Path(a.team, "classes.json"))
images, actual = ev.load_test_set(a.data, aliases, enforce_size=False)
model = YOLO(a.model, task="detect")
try:
    ev.class_ids(model.names, aliases, a.model)
except ValueError as e:
    reason = str(e)
else:
    raise SystemExit("this checkpoint has the PPE classes: evaluate it with the team's evaluate.py instead")
classes = {n: ev.image_level_metrics(actual[n], [False] * len(images)) for n in ev.PPE_CLASSES}
pos = sum(actual["NO_HARDHAT"])
neg = len(images) - pos
doc = {"split": "test", "image_count": len(images), "conf_threshold": ev.read_threshold(a.threshold),
       "model_version": "yolo11s-coco-pretrained",
       "note": "model has no NO_HARDHAT/NO_VEST class -> H=0, V=0 on every image (" + reason + ")",
       "positive_images": pos, "negative_images": neg, "min_images_per_group": ev.MIN_TEST_IMAGES_PER_GROUP,
       "test_size_ok": min(pos, neg) >= ev.MIN_TEST_IMAGES_PER_GROUP, "classes": classes,
       "metrics_pass": ev.passes_hardhat_gate(classes["NO_HARDHAT"]), "passed": False, "result": "ไม่ผ่านเกณฑ์"}
a.output.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("BASELINE", classes["NO_HARDHAT"])
