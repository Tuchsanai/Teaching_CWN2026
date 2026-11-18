"""Download construction-site-safety v28 (YOLO format) from Roboflow.
The API key is read from the ROBOFLOW_API_KEY environment variable only (never saved to disk)."""
import os
from roboflow import Roboflow

key = os.environ.pop("ROBOFLOW_API_KEY")
rf = Roboflow(api_key=key)
project = rf.workspace("roboflow-universe-projects").project("construction-site-safety")
ds = project.version(28).download("yolov8", location="/workspace/datasets/construction-site-safety-28")
print("dataset at:", ds.location)
