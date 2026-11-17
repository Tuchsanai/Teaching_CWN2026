# ดาวน์โหลด dataset จาก Roboflow Universe ในรูปแบบ YOLO
# ใช้: ROBOFLOW_API_KEY=... python get_data.py [workspace/project] [version] [โฟลเดอร์ปลายทาง]
import os
import sys
from pathlib import Path

import yaml
from roboflow import Roboflow

project = sys.argv[1] if len(sys.argv) > 1 else "roboflow-universe-projects/construction-site-safety"
version = int(sys.argv[2]) if len(sys.argv) > 2 else 28
out = Path(sys.argv[3] if len(sys.argv) > 3 else "/workspace/data/ppe").resolve()

ws, proj = project.split("/")
rf = Roboflow(api_key=os.environ["ROBOFLOW_API_KEY"])
rf.workspace(ws).project(proj).version(version).download("yolov11", location=str(out), overwrite=True)

# เขียน data.yaml ใหม่ให้เป็น path เต็ม (ไฟล์จาก Roboflow ใช้ ../train ซึ่งชี้ผิดที่ได้)
cfg = yaml.safe_load((out / "data.yaml").read_text())
for split, folder in [("train", "train"), ("val", "valid"), ("test", "test")]:
    cfg[split] = str(out / folder / "images")
cfg.pop("path", None)
(out / "data.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))

for folder in ["train", "valid", "test"]:
    n = len(list((out / folder / "images").glob("*")))
    print(f"{folder}: {n} images")
print("classes:", cfg["names"])
