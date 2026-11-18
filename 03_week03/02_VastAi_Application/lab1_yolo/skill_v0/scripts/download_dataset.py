"""Download construction-site-safety v28 (YOLO format) from Roboflow.
The API key is read from stdin (preferred: `... | ssh host python code/download_dataset.py`) or from the
ROBOFLOW_API_KEY environment variable. It is never saved to disk or printed."""
import os
import sys
from roboflow import Roboflow

key = os.environ.pop("ROBOFLOW_API_KEY", "") or sys.stdin.readline().strip()
if not key:
    sys.exit("ROBOFLOW_API_KEY missing (send it on stdin)")
rf = Roboflow(api_key=key)
project = rf.workspace("roboflow-universe-projects").project("construction-site-safety")
ds = project.version(28).download("yolov8", location="/workspace/datasets/construction-site-safety-28")
print("dataset at:", ds.location)
