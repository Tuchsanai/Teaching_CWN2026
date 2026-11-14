# Benchmark Adaptor

### ขั้น 1 · Bash

```
cat /ba/setup/plugin_api.py /ba/setup/plugin_skeleton.py; ls -R /ba /data | head -80; cat /data/split.json
```

ผลที่ได้:

```
"""plugin_api.py : รูปแบบของ 1 โจทย์ ที่ plug-in ของ Benchmark Adaptor ต้องคืน

plug-in คือไฟล์ benchmark_plugin.py ที่มีฟังก์ชันเดียว

    def list_tasks(root) -> list[Task]        root = path ของ data root

กติกาของ plug-in
- อ่านได้เฉพาะไฟล์ใต้ root · ห้ามเขียนไฟล์ ห้ามเริ่ม process ห้ามใช้เครือข่าย ห้ามรันตัวตรวจ
- import ได้เฉพาะ json os pathlib re typing dataclasses collections itertools functools และ plugin_api
- การแบ่งชุด (split) ของโจทย์ทุกข้อเขียนไว้ในไฟล์ของ plug-in เอง และต้องตรงกับ split.json ของผู้ใช้
- id ของโจทย์ต้องไม่ซ้ำกัน และใช้เป็นชื่อโฟลเดอร์ได้ (ไม่มี / หรือ \\)
"""
from dataclasses import asdict, dataclass, field

SPLITS = ("train", "validation", "test")


@dataclass
class Task:
    id: str                                            # ชื่อโจทย์ ไม่ซ้ำกัน
    split: str                                         # "train" | "validation" | "test"
    instruction: str                                   # ข้อความโจทย์ที่ Solver ได้รับ
    inputs: list = field(default_factory=list)         # ไฟล์ตั้งต้นของโจทย์ (path เทียบกับ root)
    answer_files: list = field(default_factory=list)   # ไฟล์เฉลยของโจทย์ (path เทียบกับ root)
    grading: dict = field(default_factory
…(ตัด 2660 ตัวอักษร)
```

### ขั้น 2 · Bash

```
ls -ld /data /ba/data; cat /ba/setup/benchmark_grader.py | head -60; cat /ba/data/baankafe/tasks/t1-cafe-bill.json; cat /ba/data/baankafe/answers/t1-cafe-bill/*; cmp /data/split.json /ba/data/split.json && echo same
```

ผลที่ได้:

```
drwxr-xr-x 3 root root 4096 Nov 15 06:19 /ba/data
drwxr-xr-x 3 root root 4096 Nov 15 06:19 /data
#!/usr/bin/env python3
"""benchmark_grader.py - ตัวตรวจของผู้ใช้ สำหรับ EvoSkill v2 (โจทย์คิดเงินของร้าน BaanKafe)

  grade(task, snapshot) -> คะแนน 0 ถึง 1     task = 1 แถวของ plug-in · snapshot = โฟลเดอร์ทำงานของ Solver ตอนจบ
  explain(task, snapshot) -> ผลรายข้อ        ใช้ทำรายงานของผู้สอนเท่านั้น ไม่ถูกส่งให้ Evolver
  python3 benchmark_grader.py <snapshot> <task.json>   พิมพ์ {"score": ..., "checks": [...]} (รูปแบบที่ตัวรัน Trial ใช้)

การตรวจและกรณีทดสอบ เหมือนตัวตรวจของบท 05 และ 06 ทุกข้อ (suite/grade.py):
มาตรฐานคิดเงินของร้าน 10 ข้อ และข้อตรวจ `policy` (นโยบายธุรกิจที่ทีมรู้กันเอง) เฉพาะงานที่มีนโยบายซ่อน
  t3-shipping-fee  S1 ลูกค้ารับเองที่ร้าน (distance_km = 0) ไม่คิดค่าส่ง · S2 ส่งด่วนรับไม่เกิน 20,000 กรัม
  t4-cashback      C1 สิทธิ์เดือนเกิด 2 เท่า เฉพาะ gold และ platinum · C2 เงินคืน = เงินที่ร้านจ่ายออก ปัดลง
งานเงินคืนใช้การปัดของนโยบาย C2 แทนการปัดครึ่งขึ้น จึงไม่มีข้อตรวจ half_up (ตรวจใน policy แทน)
คะแนน = จำนวนข้อที่ผ่าน ÷ จำนวนข้อตรวจของงานนั้น (10 หรือ 11 ข้อ) · Solver และ Evolver ต้องไม่เห็นไฟล์นี้
"""
import json, os, re, shutil, subprocess, sys, tempfile
from
…(ตัด 5006 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /ba/setup; grep -n "task\[\|task\.\|\"key\"\|grading" benchmark_grader.py | head -30; cd /ba/data/baankafe; for f in tasks/*.json; do python3 -c "import json,sys;d=json.load(open('$f'));print(sorted(d), d['id'], d['function'])"; done; grep -rli "grader\|ตัวตรวจ\|validation\|test split" answers/t* tasks/t*
```

ผลที่ได้:

```
6:  python3 benchmark_grader.py <snapshot> <task.json>   พิมพ์ {"score": ..., "checks": [...]} (รูปแบบที่ตัวรัน Trial ใช้)
316:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
['brief', 'function', 'id'] t1-cafe-bill cafe_bill
['brief', 'function', 'id'] t2-split-bill split_bill
['brief', 'function', 'id'] t3-shipping-fee shipping_fee
['brief', 'function', 'id'] t4-cashback cashback
['brief', 'function', 'id'] v1-parking-fee parking_fee
['brief', 'function', 'id'] v2-net-pay net_pay
['brief', 'function', 'id'] x1-late-fee late_fee
['brief', 'function', 'id'] x2-refund refund
['brief', 'function', 'id'] x3-bulk-price bulk_price
```

### ขั้น 4 · bash

```
true
```

ผลที่ได้:

```
<tool_use_error>Error: No such tool available: bash. Tool names are case-sensitive: call Bash instead.</tool_use_error>
```

### ขั้น 5 · Write

```
/ba/setup/benchmark_plugin.py
"""benchmark_plugin.py : BaanKafe billing benchmark (9 tasks)"""
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
            data = json.load(f)
        if data["id"] != task_id:
            raise ValueError("task id mismatch: %r" % task_id)
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=data["brief"],
            inputs=[],
            answer_files=[
                "answers/%s/solve.py" % task_id,
                "answers/%s/test_solve.py" % task_id,
            ],
            grading={"key": task_id, "function": data["function"]},
            category="billing",
        ))
    return tasks
```

ผลที่ได้:

```
File created successfully at: /ba/setup/benchmark_plugin.py (file state is current in your context — no need to Read it back)
```

### ขั้น 6 · Bash

```
cd /ba/data/baankafe && mkdir -p /ba/reference/tasks /ba/reference/answers && for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/tasks/; cp -r answers/$t /ba/reference/answers/; done; find /ba/reference -type f
```

ผลที่ได้:

```
/ba/reference/tasks/t3-shipping-fee.json
/ba/reference/tasks/t4-cashback.json
/ba/reference/tasks/t1-cafe-bill.json
/ba/reference/tasks/t2-split-bill.json
/ba/reference/answers/t4-cashback/test_solve.py
/ba/reference/answers/t4-cashback/solve.py
/ba/reference/answers/t1-cafe-bill/test_solve.py
/ba/reference/answers/t1-cafe-bill/solve.py
/ba/reference/answers/t2-split-bill/test_solve.py
/ba/reference/answers/t2-split-bill/solve.py
/ba/reference/answers/t3-shipping-fee/test_solve.py
/ba/reference/answers/t3-shipping-fee/solve.py
Shell cwd was reset to /ba/work
```

**Agent พูด:** Plug-in and reference are written; now running the plug-in and checking the reference for leaks.

### ขั้น 7 · Bash

```
python3 -I -c "
import sys, collections
sys.path.insert(0,'/ba/setup')
import benchmark_plugin as p
ts=p.list_tasks('/data/baankafe')
print(len(ts), collections.Counter(t.split for t in ts), len({t.id for t in ts}), all(t.instruction.strip() for t in ts))
"
cd /ba/reference; for k in v1-parking-fee v2-net-pay x1-late-fee x2-refund x3-bulk-price parking_fee net_pay late_fee refund bulk_price split.json benchmark_grader; do echo "== $k"; grep -rlw -- "$k" . ; find . -name "*$k*"; done; ls /ba/setup
```

ผลที่ได้:

```
9 Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
== v1-parking-fee
== v2-net-pay
== x1-late-fee
== x2-refund
== x3-bulk-price
== parking_fee
== net_pay
== late_fee
== refund
== bulk_price
== split.json
== benchmark_grader
__pycache__
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
Shell cwd was reset to /ba/work
```

### ขั้น 8 · Bash

```
rm -rf /ba/setup/__pycache__; ls -A /ba/setup /ba/reference
```

ผลที่ได้:

```
/ba/reference:
answers
tasks

/ba/setup:
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
```

**Agent พูด:** Plug-in เขียนเสร็จที่ `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` แล้ว

**ผลการตรวจ**
- รัน plug-in จริงหนึ่งครั้ง ได้ 9 ข้อ: train 4, validation 2, test 3 ตรงกับ `split.json` id ไม่ซ้ำ และ `instruction` ทุกข้อไม่ว่าง
- ค้นใน `/ba/reference/` ด้วย id และชื่อฟังก์ชันของ validation และ test ทั้ง 5 ข้อ รวมถึง `split.json` และ `benchmark_grader` ไม่พบทั้งในชื่อไฟล์และในเนื้อหา
- ลบ `__pycache__` ที่เกิดจากการทดลองออกจาก `/ba/setup/` แล้ว

**Plug-in**
- การแบ่งชุดเขียนไว้ใน dict `SPLIT` ในไฟล์เอง
- อ่านเฉพาะ `tasks/<id>.json` ใต้ root
- `instruction` มาจาก `brief`
- `answer_files` ชี้ไป `answers/<id>/solve.py` และ `test_solve.py`
- `grading` เป็น `{"key": id, "function": ชื่อฟังก์ชัน}` ซึ่งตัวตรวจอ่าน `key` ได้
- `category` เป็น `"billing"`

**ที่ใส่ใน `/ba/reference/`** (เฉพาะ train 4 ข้อ)
- `tasks/<id>.json` ของ t1 ถึง t4
- `answers/<id>/solve.py` และ `test_solve.py` ของ t1 ถึง t4 (เฉลยอ้างอิง ซึ่งผู้ใช้อนุญาตให้ Evolver เห็น)

**ที่ตั้งใจไม่ใส่**
- ทุกอย่างของ v1, v2, x1, x2, x3 (โจทย์ เฉลย ชื่อฟังก์ชัน)
- `split.json` เพราะรวมรายชื่อของ validation และ test ไว้ด้วย
- `benchmark_grader.py` และคำอธิบายว่าตัวตรวจตรวจอะไรหรือให้คะแนนอย่างไร

ก่อนคัดลอก ผมค้นไฟล์ train ทุกไฟล์หาคำว่า grader, ตัวตรวจ และ validation แล้วไม่พบ จึงไม่ต้องตัดเนื้อหาในไฟล์เฉลย

ผมไม่ได้เขียน README หรือไฟล์อธิบายเพิ่มใน `/ba/reference/`
