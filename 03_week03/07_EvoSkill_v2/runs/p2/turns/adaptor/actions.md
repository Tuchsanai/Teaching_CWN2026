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
ls -la /data 2>&1 | head; cd /ba/data/baankafe/tasks; for f in *.json; do echo "== $f"; cat $f; echo; done; echo; cat /ba/setup/benchmark_grader.py
```

ผลที่ได้:

```
<persisted-output>
Output too large (32.5KB). Full output saved to: /root/ai-accounts/.Claude/yolo1/projects/-ba-work/d4cac8ab-93eb-4f29-bce6-a31f6556ef69/tool-results/bp44i66jb.txt

Preview (first 2KB):
total 16
drwxr-xr-x 3 root root 4096 Nov 15 06:12 .
drwxr-xr-x 1 root root 4096 Nov 15 06:11 ..
drwxr-xr-x 4 root root 4096 Nov 13 08:46 baankafe
-rw-r--r-- 1 root root  213 Nov 15 06:12 split.json
== t1-cafe-bill.json
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
== t2-split-bill.json
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้า
…(ตัด 836 ตัวอักษร)
```

### ขั้น 3 · Bash

```
ls -la /ba /data/baankafe; diff -r /data/baankafe /ba/data/baankafe && echo same; diff /data/split.json /ba/data/split.json && echo same; cat /ba/setup/benchmark_grader.py | head -60; cat /ba/data/baankafe/tasks/t4-cashback.json
```

ผลที่ได้:

```
/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 15 06:12 .
drwxr-xr-x 1 root root 4096 Nov 15 06:11 ..
drwxr-xr-x 3 root root 4096 Nov 15 06:12 data
drwxr-xr-x 2 root root 4096 Nov 15 06:12 reference
drwxr-xr-x 2 root root 4096 Nov 15 06:12 setup
drwxr-xr-x 2 root root 4096 Nov 15 06:12 work

/data/baankafe:
total 16
drwxr-xr-x  4 root root 4096 Nov 13 08:46 .
drwxr-xr-x  3 root root 4096 Nov 15 06:12 ..
drwxr-xr-x 11 root root 4096 Nov 13 08:46 answers
drwxr-xr-x  2 root root 4096 Nov 13 08:46 tasks
same
same
#!/usr/bin/env python3
"""benchmark_grader.py - ตัวตรวจของผู้ใช้ สำหรับ EvoSkill v2 (โจทย์คิดเงินของร้าน BaanKafe)

  grade(task, snapshot) -> คะแนน 0 ถึง 1     task = 1 แถวของ plug-in · snapshot = โฟลเดอร์ทำงานของ Solver ตอนจบ
  explain(task, snapshot) -> ผลรายข้อ        ใช้ทำรายงานของผู้สอนเท่านั้น ไม่ถูกส่งให้ Evolver
  python3 benchmark_grader.py <snapshot> <task.json>   พิมพ์ {"score": ..., "checks": [...]} (รูปแบบที่ตัวรัน Trial ใช้)

การตรวจและกรณีทดสอบ เหมือนตัวตรวจของบท 05 และ 06 ทุกข้อ (suite/grade.py):
มาตรฐานคิดเงินของร้าน 10 ข้อ และข้อตรวจ `policy` (นโยบายธุรกิจที่ทีมรู้กันเอง) เฉพาะงานที่มีนโยบายซ่อน
  t3-shipping-fee  S1 ลูกค้ารับเองที่ร้าน (distance_km = 0) ไม่ค
…(ตัด 2054 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -n "task\b\|task\[\|task\.\|grading\|\"key\"" /ba/setup/benchmark_grader.py | head -40
```

ผลที่ได้:

```
4:  grade(task, snapshot) -> คะแนน 0 ถึง 1     task = 1 แถวของ plug-in · snapshot = โฟลเดอร์ทำงานของ Solver ตอนจบ
5:  explain(task, snapshot) -> ผลรายข้อ        ใช้ทำรายงานของผู้สอนเท่านั้น ไม่ถูกส่งให้ Evolver
6:  python3 benchmark_grader.py <snapshot> <task.json>   พิมพ์ {"score": ..., "checks": [...]} (รูปแบบที่ตัวรัน Trial ใช้)
300:def explain(task, snapshot):
304:        return _checks(task, sb, rdir)
309:def grade(task, snapshot):
311:    checks = explain(task, snapshot)
315:def _checks(task, sb, rdir):
316:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
447:    task = json.load(open(sys.argv[2], encoding="utf-8"))
448:    checks = explain(task, sys.argv[1])
```

### ขั้น 5 · bash

```
true
```

ผลที่ได้:

```
<tool_use_error>Error: No such tool available: bash. Tool names are case-sensitive: call Bash instead.</tool_use_error>
```

### ขั้น 6 · Write

```
/ba/setup/benchmark_plugin.py
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
```

ผลที่ได้:

```
File created successfully at: /ba/setup/benchmark_plugin.py (file state is current in your context — no need to Read it back)
```

### ขั้น 7 · Bash

```
python3 -I -c "
import sys,collections
sys.path.insert(0,'/ba/setup')
import benchmark_plugin as b
for root in ('/data/baankafe','/ba/data/baankafe'):
    t=b.list_tasks(root)
    print(root,len(t),collections.Counter(x.split for x in t),len({x.id for x in t}),all(x.instruction.strip() for x in t))
"
mkdir -p /ba/reference/train_tasks
for id in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$id.json /ba/reference/train_tasks/; done
cat > /ba/reference/README.md <<'EOF'
# BaanKafe benchmark (ข้อมูลสำหรับ Evolver)

โจทย์เขียนโค้ดคิดเงินของร้านกาแฟ BaanKafe: ต่อ 1 โจทย์ Solver ต้องเขียนฟังก์ชัน Python 1 ฟังก์ชัน
ตามข้อความโจทย์ (`brief`) ลงในไฟล์ `solve.py` โดย Solver เริ่มจากโฟลเดอร์ทำงานว่าง ๆ
และบันทึกไฟล์ผลงานไว้ในโฟลเดอร์ทำงานนั้น

โจทย์ชุด train อยู่ใน `train_tasks/<task id>.json` แต่ละไฟล์มี `id`, `function` (ชื่อฟังก์ชัน)
และ `brief` (ข้อความโจทย์ที่ Solver ได้รับ)
EOF
ls -R /ba/reference; grep -rE "v1-parking|v2-net|x1-late|x2-refund|x3-bulk|parking_fee|net_pay|late_fee|refund|bulk_price|grader|split.json" /ba/reference && echo FOUND || echo clean
```

ผลที่ได้:

```
/data/baankafe 9 Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
/ba/data/baankafe 9 Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
/ba/reference:
README.md
train_tasks

/ba/reference/train_tasks:
t1-cafe-bill.json
t2-split-bill.json
t3-shipping-fee.json
t4-cashback.json
clean
```

**Agent พูด:** ทำครบทั้งสองอย่างแล้ว และตรวจผ่านทั้งสองเรื่อง

**plug-in** (`/ba/setup/benchmark_plugin.py`)
- รันจริงกับ `/data/baankafe` ได้ 9 ข้อ แบ่งเป็น train 4, validation 2, test 3 ตรงกับ `split.json`
- id ไม่ซ้ำกัน และ `instruction` ของทุกข้อไม่ว่าง
- การแบ่งชุดเขียนไว้ในไฟล์ plug-in เอง
- ทุกข้อใส่ `answer_files` เป็น `answers/<id>/solve.py` กับ `test_solve.py`
- `grading` มี `key` (เท่ากับ id ของโจทย์) กับ `function` ซึ่งตัวตรวจอ่านได้ ตัวตรวจไม่ได้ถูกแก้หรือรัน

**ที่ใส่ใน `/ba/reference/`**
- `README.md` อธิบายรูปแบบของ benchmark อย่างกว้าง ๆ: Solver ได้อะไร ต้องเขียน `solve.py` ลงโฟลเดอร์ทำงาน
- `train_tasks/` มี JSON ของโจทย์ train 4 ข้อ (`id`, `function`, `brief`) คือ t1 ถึง t4

**ที่ตั้งใจไม่ใส่**
- โจทย์ชุด validation และ test ทั้งหมด (v1, v2, x1, x2, x3)
- `split.json` เพราะรวมรายชื่อทุกชุดไว้ในไฟล์เดียว
- `answers/` ทั้งหมด รวมเฉลยของ train ตามที่ผู้ใช้สั่ง
- ตัวตรวจ `benchmark_grader.py` และคำอธิบายว่าตรวจหรือให้คะแนนอย่างไร

เมื่อค้นใน `/ba/reference/` ด้วย id และชื่อฟังก์ชันของโจทย์ validation และ test รวมถึงคำว่า grader กับ split.json ไม่พบเลย ผมไม่ทิ้งไฟล์ทดลองไว้ใน `/ba/setup/` หรือ `/ba/reference/`

ขนาดการรัน (3 epochs, 3 samples ต่อโจทย์) ไม่ต้องตั้งค่าใน plug-in
