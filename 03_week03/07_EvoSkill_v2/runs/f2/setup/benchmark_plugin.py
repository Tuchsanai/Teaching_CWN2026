"""benchmark_plugin.py - BaanKafe billing-function benchmark (9 tasks)."""
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
        ans = []
        for name in ("solve.py", "test_solve.py"):
            rel = "answers/%s/%s" % (tid, name)
            if os.path.isfile(os.path.join(root, rel)):
                ans.append(rel)
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=ans,
            grading={"key": d["id"], "function": d["function"]},
            category="billing",
        ))
    return tasks
