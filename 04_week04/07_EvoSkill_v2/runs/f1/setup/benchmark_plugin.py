"""benchmark_plugin.py : BaanKafe (9 โจทย์ เขียนฟังก์ชัน Python คิดเงิน)"""
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
    for task_id, split in SPLIT.items():
        with open(os.path.join(root, "tasks", task_id + ".json"), encoding="utf-8") as f:
            meta = json.load(f)
        answers = []
        for name in ("solve.py", "test_solve.py"):
            rel = "answers/%s/%s" % (task_id, name)
            if os.path.isfile(os.path.join(root, rel)):
                answers.append(rel)
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=meta["brief"],
            inputs=[],
            answer_files=answers,
            grading={"key": task_id, "function": meta.get("function", "")},
            category="billing",
        ))
    return tasks
