"""benchmark_plugin.py - BaanKafe (โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ)

data root: tasks/<id>.json (id, function, brief) และ answers/<id>/{solve.py,test_solve.py}
"""
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
        # เฉลยอ้างอิงเปิดให้เฉพาะชุด train
        answers = []
        if split == "train":
            answers = ["answers/%s/solve.py" % tid, "answers/%s/test_solve.py" % tid]
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=answers,
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
