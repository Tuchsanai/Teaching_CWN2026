"""benchmark_plugin.py : โครงเปล่า · คัดลอกไฟล์นี้เป็น benchmark_plugin.py แล้วเติมให้ครบ

ดูรูปแบบของ Task และกติกาของ plug-in ใน plugin_api.py (วางอยู่ข้างไฟล์นี้)
"""
import json
import os

from plugin_api import Task

# การแบ่งชุดของโจทย์ทุกข้อ เขียนไว้ที่นี่ (ต้องตรงกับการแบ่งชุดที่ผู้ใช้ให้มา)
SPLIT = {
    # "<task id>": "train" | "validation" | "test",
}


def list_tasks(root):
    """คืน list ของ Task ทุกข้อ · root = path ของ data root (อ่านได้เฉพาะไฟล์ใต้ root)"""
    tasks = []
    for task_id, split in SPLIT.items():
        # TODO อ่านไฟล์ของโจทย์ใต้ root แล้วเติมฟิลด์ให้ครบ
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction="",        # ข้อความโจทย์ที่ Solver ได้รับ
            inputs=[],             # ไฟล์ตั้งต้น (path เทียบกับ root)
            answer_files=[],       # ไฟล์เฉลย (path เทียบกับ root)
            grading={},            # ค่าที่ตัวตรวจอ่าน
            category="",
        ))
    return tasks
