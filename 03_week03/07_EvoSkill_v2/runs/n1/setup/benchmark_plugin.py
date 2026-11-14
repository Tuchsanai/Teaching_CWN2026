"""benchmark_plugin.py - BaanKafe: โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ (train 4 · validation 2 · test 3)"""
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
            spec = json.load(f)
        answers = [os.path.join("answers", tid, n) for n in ("solve.py", "test_solve.py")]
        tasks.append(Task(
            id=tid,
            split=split,
            instruction=spec["brief"],
            inputs=[],
            answer_files=answers,
            grading={"key": tid, "function": spec["function"]},
            category="coding",
        ))
    return tasks
