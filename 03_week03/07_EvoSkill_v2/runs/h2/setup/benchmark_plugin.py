"""benchmark_plugin.py - BaanKafe: โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ"""
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
        answer_files = []
        adir = os.path.join(root, "answers", tid)
        if os.path.isdir(adir):
            answer_files = ["answers/%s/%s" % (tid, n) for n in sorted(os.listdir(adir))
                            if os.path.isfile(os.path.join(adir, n))]
        tasks.append(Task(
            id=tid,
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=answer_files,
            grading={"key": tid, "function": d["function"]},
            category="coding",
        ))
    return tasks
