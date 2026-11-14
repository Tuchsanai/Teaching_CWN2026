# Benchmark Adaptor

### ขั้น 1 · Bash

```
cat /ba/setup/plugin_api.py /ba/setup/plugin_skeleton.py; ls -R /ba/setup /ba/reference /data | head -80; cat /data/split.json
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
…(ตัด 2578 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; head -c 1500 /ba/setup/benchmark_grader.py; echo; grep -n "key\|grading" /ba/setup/benchmark_grader.py | head -20; cat tasks/t1-cafe-bill.json; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do echo "== $t"; cat answers/$t/solve.py; head -20 answers/$t/test_solve.py; done; grep -rl "v1-\|v2-\|x1-\|x2-\|x3-\|parking\|net-pay\|late\|refund\|bulk" tasks/t* answers/t*
```

ผลที่ได้:

```
#!/usr/bin/env python3
"""benchmark_grader.py - ตัวตรวจของผู้ใช้ สำหรับ EvoSkill v2 (โจทย์คิดเงินของร้าน BaanKafe)

  grade(task, snapshot) -> คะแนน 0 ถึง 1     task = 1 แถวของ plug-in · snapshot = โฟลเดอร์ทำงานของ Solver ตอนจบ
  explain(task, snapshot) -> ผลรายข้อ        ใช้ทำรายงานของผู้สอนเท่านั้น ไม่ถูกส่งให้ Evolver
  python3 benchmark_grader.py <snapshot> <task.json>   พิมพ์ {"score": ..., "checks": [...]} (รูปแบบที่ตัวรัน Trial ใช้)

การตรวจและกรณีทดสอบ เหมือนตัวตรวจของบท 05 และ 06 ทุกข้อ (suite/grade.py):
มาตรฐานคิดเงินของร้าน 10 ข้อ และข้อตรวจ `policy` (นโยบายธุรกิจที่ทีมรู้กันเอง) เฉพาะงานที่มีนโยบายซ่อน
  t3-shipping-fee  S1 ลูกค้ารับเองที่ร้าน (distance_km = 0) ไม่คิดค่าส่ง · S2 ส่งด่วนรับไม่เกิน 20,000 กรัม
  t4-cashback      C1 สิทธิ์เดือนเกิด 2 เท่า เฉพาะ gold แล
316:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เ
…(ตัด 9157 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
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
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=data["brief"],
            inputs=[],
            answer_files=["answers/%s/solve.py" % task_id,
                          "answers/%s/test_solve.py" % task_id],
            grading={},
            category="billing",
        ))
    return tasks
EOF
mkdir -p /ba/reference/tasks /ba/reference/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/tasks/; cp -r answers/$t /ba/reference/answers/; done
cd /ba/work && python3 -I - <<'EOF'
import sys,collections
sys.path.insert(0,'/ba/setup')
import benchmark_plugin as p
ts=p.list_tasks('/data/baankafe')
print(collections.Counter(t.split for t in ts), len({t.id for t in ts}), all(t.instruction.strip() for t in ts))
EOF
cd /ba/reference; for k in v1-parking v2-net x1-late x2-refund x3-bulk parking_fee net_pay late_fee refund bulk_price v1 v2 x1 x2 x3 grader benchmark_grader; do grep -rli -- "$k" . ; done; find . -type f; ls /ba/setup; find /ba/setup /ba/reference -name __pycache__
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
./tasks/t3-shipping-fee.json
./tasks/t4-cashback.json
./tasks/t1-cafe-bill.json
./tasks/t2-split-bill.json
./answers/t4-cashback/test_solve.py
./answers/t4-cashback/solve.py
./answers/t1-cafe-bill/test_solve.py
./answers/t1-cafe-bill/solve.py
./answers/t2-split-bill/test_solve.py
./answers/t2-split-bill/solve.py
./answers/t3-shipping-fee/test_solve.py
./answers/t3-shipping-fee/solve.py
__pycache__
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
/ba/setup/__pycache__
Shell cwd was reset to /ba/work
```

### ขั้น 4 · Bash

```
cd /ba/reference; for k in v1-parking v2-net x1-late x2-refund x3-bulk parking_fee net_pay late_fee refund bulk_price v1 v2 x1 x2 x3 grader benchmark_grader; do echo "$k: $(grep -rli -- "$k" . | wc -l)"; done; grep -rn -i "x1\|v1\|grader" . | head -5; rm -rf /ba/setup/__pycache__
```

ผลที่ได้:

```
v1-parking: 0
v2-net: 0
x1-late: 0
x2-refund: 0
x3-bulk: 0
parking_fee: 0
net_pay: 0
late_fee: 0
refund: 0
bulk_price: 0
v1: 0
v2: 0
x1: 0
x2: 0
x3: 0
grader: 0
benchmark_grader: 0
Shell cwd was reset to /ba/work
```

**Agent พูด:** plug-in เขียนเสร็จที่ `/ba/setup/benchmark_plugin.py` และ `/ba/reference/` เติมแล้ว

ผลการตรวจ:
- **plug-in:** รันจริง 1 ครั้งได้ train 4 · validation 2 · test 3 ข้อ ตรงกับ `split.json` id ไม่ซ้ำ 9 ข้อ และ `instruction` ของทุกข้อไม่ว่าง
- **การกันข้อมูล:** ค้นใน `/ba/reference/` ด้วย id ชื่อฟังก์ชัน และคำที่เกี่ยวกับ validation/test ทุกข้อ ไม่พบเลย และไม่พบคำว่า grader
- **ความสะอาด:** ลบ `__pycache__` ที่เกิดจากการทดลองใน `/ba/setup/` ออกแล้ว

**plug-in**
- ตารางแบ่งชุดเขียนไว้ในไฟล์เองครบ 9 ข้อ
- อ่านข้อความโจทย์จาก `tasks/<id>.json` ใต้ root
- `answer_files` ชี้ไป `solve.py` และ `test_solve.py` ของแต่ละข้อ
- `grading` เว้นว่าง เพราะตัวตรวจเลือกชุดกรณีทดสอบจาก `id` อยู่แล้ว
- `category` ใส่ `"billing"` ทุกข้อ

**สิ่งที่ใส่ใน `/ba/reference/`** (เฉพาะ train 4 ข้อ: t1-cafe-bill, t2-split-bill, t3-shipping-fee, t4-cashback)
- `tasks/<id>.json`: id ชื่อฟังก์ชัน และข้อความโจทย์
- `answers/<id>/solve.py` และ `test_solve.py`: เฉลยอ้างอิง ตามที่ผู้ใช้ให้ Evolver อ่านได้

**สิ่งที่ตั้งใจไม่ใส่**
- ทุกอย่างของ v1-parking-fee, v2-net-pay (validation) และ x1-late-fee, x2-refund, x3-bulk-price (test)
- `split.json` เพราะรวมรายชื่อทุกชุดไว้ในไฟล์เดียว
- `benchmark_grader.py` และคำอธิบายว่าตัวตรวจตรวจอะไรหรือให้คะแนนอย่างไร

`test_solve.py` ของเฉลยชุด train ที่คัดลอกไปมีค่าทดสอบเป็นตัวเลขอยู่ด้วย ถือเป็นส่วนของเฉลยที่ผู้ใช้อนุญาตให้ Evolver เห็น ไม่ใช่ตัวตรวจ
