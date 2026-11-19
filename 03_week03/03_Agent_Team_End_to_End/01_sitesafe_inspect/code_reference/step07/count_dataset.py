"""Count images per split and bounding boxes per class (from the real label files)."""
import glob, json, os, sys, yaml
from collections import Counter

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/workspace/e2e_sitesafe/dataset"
names = yaml.safe_load(open(os.path.join(ROOT, "data.yaml")))["names"]
if isinstance(names, dict):
    names = [names[k] for k in sorted(names)]
out = {"names": names, "splits": {}}
for split, title in (("train", "Training"), ("valid", "Validation"), ("test", "Test")):
    imgs = [f for f in glob.glob(os.path.join(ROOT, split, "images", "*")) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    labels = glob.glob(os.path.join(ROOT, split, "labels", "*.txt"))
    boxes, empty, bad = Counter(), 0, 0
    for lf in labels:
        lines = [l.split() for l in open(lf).read().splitlines() if l.strip()]
        if not lines:
            empty += 1
        for p in lines:
            if len(p) != 5:
                bad += 1  # polygon/segment style line
            boxes[names[int(p[0])]] += 1
    out["splits"][title] = {"images": len(imgs), "label_files": len(labels), "empty_label_files": empty,
                            "non_bbox_lines": bad, "boxes_total": sum(boxes.values()),
                            "boxes_per_class": {n: boxes.get(n, 0) for n in names}}
json.dump(out, open(os.path.join(os.path.dirname(ROOT), "dataset_counts.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
