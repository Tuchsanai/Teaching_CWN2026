"""benchmark_plugin.py : BaanKafe (โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ)"""
import json
import os

from plugin_api import Task

# การแบ่งชุด ตรงกับ split.json ของผู้ใช้
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
        path = os.path.join(root, "tasks", task_id + ".json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["id"] == task_id, (data["id"], task_id)
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=data["brief"],
            inputs=[],
            answer_files=[
                "answers/%s/solve.py" % task_id,
                "answers/%s/test_solve.py" % task_id,
            ],
            grading={"key": task_id, "function": data.get("function", "")},
            category="billing",
        ))
    return tasks
