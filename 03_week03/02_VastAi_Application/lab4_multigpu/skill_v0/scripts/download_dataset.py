"""Download hard-hat-workers v13 (YOLO format) from Roboflow.
The API key is read from stdin (never written to disk on the rented machine)."""
import sys, os
from roboflow import Roboflow

key = sys.stdin.readline().strip()
os.chdir("/workspace")
rf = Roboflow(api_key=key)
ds = rf.workspace("joseph-nelson").project("hard-hat-workers").version(13).download(
    "yolov11", location="/workspace/hardhat")
print("saved to", ds.location)
