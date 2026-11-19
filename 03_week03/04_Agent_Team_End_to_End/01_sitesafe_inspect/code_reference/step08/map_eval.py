"""Box-level mAP on the test split (Ultralytics val) for one checkpoint; saves plots in --out."""
import argparse, json
from pathlib import Path
from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("--model", required=True)
p.add_argument("--data", required=True)
p.add_argument("--out", required=True)
p.add_argument("--tag", required=True)
a = p.parse_args()
model = YOLO(a.model)
r = model.val(data=a.data, split="test", imgsz=640, device=0, project=a.out, name=f"val_{a.tag}",
              exist_ok=True, plots=True, verbose=False)
names = r.names
per = {names[c]: {"precision": float(r.box.p[i]), "recall": float(r.box.r[i]),
                  "mAP50": float(r.box.ap50[i]), "mAP50_95": float(r.box.ap[i])}
       for i, c in enumerate(r.box.ap_class_index)}
out = {"model": a.model, "split": "test", "model_class_count": len(model.names),
       "mAP50": float(r.box.map50), "mAP50_95": float(r.box.map),
       "precision": float(r.box.mp), "recall": float(r.box.mr), "per_class": per}
Path(a.out, f"map_{a.tag}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
print(a.tag, "mAP50", out["mAP50"], "mAP50-95", out["mAP50_95"])
