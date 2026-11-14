"""benchmark_plugin.py : BaanKafe (โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ)"""
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
            spec = json.load(f)
        answer_dir = os.path.join(root, "answers", task_id)
        answer_files = ["answers/%s/%s" % (task_id, n) for n in sorted(os.listdir(answer_dir))
                        if os.path.isfile(os.path.join(answer_dir, n))]
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=spec["brief"],
            inputs=[],
            answer_files=answer_files,
            grading={"key": task_id, "function": spec.get("function", "")},
            category="billing",
        ))
    return tasks
