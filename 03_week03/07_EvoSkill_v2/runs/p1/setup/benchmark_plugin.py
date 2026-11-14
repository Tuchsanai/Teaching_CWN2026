"""benchmark_plugin.py - BaanKafe: 9 โจทย์เขียนฟังก์ชันคิดเงิน (train 4 · validation 2 · test 3)"""
import json
import os

from plugin_api import Task

SPLIT = {
    "t1-cafe-bill": "train",
    "t2-split-bill": "train",
    "t3-shipping-fee": "train",
    "t4-cashback": "train",
    "v1-parking-fee": "validation",
    "v2-net-pay": "validation",
    "x1-late-fee": "test",
    "x2-refund": "test",
    "x3-bulk-price": "test",
}


def list_tasks(root):
    tasks = []
    for tid, split in SPLIT.items():
        with open(os.path.join(root, "tasks", tid + ".json"), encoding="utf-8") as f:
            d = json.load(f)
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[],  # เฉลยใน answers/ ไม่ถูกใส่ไว้ เพราะตัวตรวจไม่ใช้ และห้ามให้ Evolver เห็น
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
