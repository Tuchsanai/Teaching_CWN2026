"""benchmark_plugin.py (โครงเปล่า) - Benchmark Adaptor เติมไฟล์นี้ แล้วบันทึกเป็น benchmark_plugin.py

ดูรูปแบบของ Task ใน plugin_api.py
"""
import json
import os

from plugin_api import Task

SPLIT = {
    # "<task id>": "train" | "validation" | "test"
}


def list_tasks(root):
    tasks = []
    # อ่านไฟล์ใต้ root แล้วสร้าง Task ของทุกโจทย์ที่ใช้ในการรัน
    return tasks
