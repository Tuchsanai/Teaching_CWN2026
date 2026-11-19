"""Train YOLO11s on the prepared dataset. Re-running continues from last.pt if the run was interrupted."""
import argparse, json, time
from pathlib import Path
from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("--data", required=True)
p.add_argument("--project", required=True)
p.add_argument("--name", default="train")
p.add_argument("--model", default="yolo11s.pt")
p.add_argument("--epochs", type=int, default=30)
p.add_argument("--imgsz", type=int, default=640)
p.add_argument("--seed", type=int, default=0)
p.add_argument("--batch", type=int, default=16)
p.add_argument("--workers", type=int, default=8)
a = p.parse_args()

run = Path(a.project) / a.name
last = run / "weights" / "last.pt"
t0 = time.time()
if last.is_file():
    YOLO(str(last)).train(resume=True)
else:
    YOLO(a.model).train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, seed=a.seed, batch=a.batch,
                        workers=a.workers, device=0, project=a.project, name=a.name, exist_ok=True)
secs = time.time() - t0
log = run / "train_time.json"
prev = json.loads(log.read_text()) if log.is_file() else {"segments": []}
prev["segments"].append(round(secs, 1))
prev["train_seconds"] = round(sum(prev["segments"]), 1)
prev.update(epochs=a.epochs, imgsz=a.imgsz, seed=a.seed, batch=a.batch, model=a.model)
log.write_text(json.dumps(prev, indent=2))
print("TRAIN_DONE", prev)
