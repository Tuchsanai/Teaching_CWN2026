# Benchmark Adaptor

### ขั้น 1 · Bash

```
cat /ba/setup/plugin_api.py /ba/setup/plugin_skeleton.py; ls -R /ba /data | head -100; cat /data/split.json
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
…(ตัด 2862 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; cat tasks/v1-parking-fee.json; echo; cat answers/t1-cafe-bill/*; grep -n "grading\|key\|def " /ba/setup/benchmark_grader.py | head -40; diff /data/split.json /ba/data/split.json && echo same
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
{
 "id": "v1-parking-fee",
 "function": "parking_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `parking_fee(minutes, member)` ในไฟล์ `solve.py` สำหรับคิดค่าจอดรถ\n- `minutes` = เวลาที่จอด 0–1,440 นาที · `member` = True คือสมาชิก\n- จอดไม่เกิน 30 นาที ไม่คิดเงิน\n- จอดเกิน 30 นาที คิดชั่วโมงละ 25 บาท นับจากเวลาที่จอดทั้งหมด เศษของชั่วโมงนับเป็น 1 ชั่วโมง\n- ค่าจอดก่อนส่วนลดและภาษี สูงสุด 250 บาท\n- สมาชิกลด 15%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนค่าจอด เป็นจำนวนเต็มสตางค์"
}
"""คิดเงินหน้าร้าน · เฉลยอ้างอิงตามมาตรฐานคิดเงินของร้าน BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is 
…(ตัด 3934 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /ba/setup; grep -n "TASKS" benchmark_grader.py | head; sed -n 300,316p benchmark_grader.py
```

ผลที่ได้:

```
120:TASKS = {
316:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
def explain(task, snapshot):
    """ตรวจทุกข้อของงาน -> [{"id": ..., "pass": True/False, "note": ...}, ...]"""
    sb, rdir = str(snapshot), tempfile.mkdtemp(prefix="grader_")
    try:
        return _checks(task, sb, rdir)
    finally:
        shutil.rmtree(rdir, ignore_errors=True)


def grade(task, snapshot):
    """สัญญาของ EvoSkill v2: คืนคะแนน 0 ถึง 1 (0.999 ขึ้นไป = ผ่าน)"""
    checks = explain(task, snapshot)
    return round(sum(1 for c in checks if c["pass"]) / len(checks), 4)


def _checks(task, sb, rdir):
    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
Shell cwd was reset to /ba/work
```

### ขั้น 4 · Bash

```
cd /data/baankafe/tasks; for f in t*.json; do python3 -c "import json,sys;d=json.load(open('$f'));print(sorted(d))"; done
```

ผลที่ได้:

```
['brief', 'function', 'id']
['brief', 'function', 'id']
['brief', 'function', 'id']
['brief', 'function', 'id']
Shell cwd was reset to /ba/work
```

### ขั้น 5 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
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
            data = json.load(f)
        assert data["id"] == task_id
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=data["brief"],
            inputs=[],
            answer_files=["answers/%s/solve.py" % task_id,
                          "answers/%s/test_solve.py" % task_id],
            grading={"key": task_id, "function": data["function"]},
            category="billing",
        ))
    return tasks
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b, collections, os
t=b.list_tasks('/data/baankafe')
print(collections.Counter(x.split for x in t), len({x.id for x in t}), all(x.instruction.strip() for x in t))
print(all(os.path.exists('/data/baankafe/'+p) for x in t for p in x.answer_files))
import benchmark_grader as g; print(all(x.id in g.TASKS for x in t))
"
rm -rf /ba/setup/__pycache__
mkdir -p /ba/reference/tasks /ba/reference/answers
for i in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$i.json /ba/reference/tasks/; cp -r /data/baankafe/answers/$i /ba/reference/answers/; done
find /ba/reference -name __pycache__ ; find /ba/reference -type f
grep -rilE "v1-parking|v2-net|x1-late|x2-refund|x3-bulk|parking_fee|net_pay|late_fee|bulk_price|grader|validation" /ba/reference; ls /ba/setup
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
True
True
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
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
Shell cwd was reset to /ba/work
```

**Agent พูด:** เตรียมเสร็จแล้ว: plug-in เขียนไว้ที่ `/ba/setup/benchmark_plugin.py` และ `/ba/reference/` เติมเฉพาะของชุด train

**ผลการตรวจก่อนจบ**
- รัน `list_tasks` จริง 1 ครั้ง ได้ 9 โจทย์ แบ่งเป็น train 4, validation 2, test 3 ตรงกับ `/data/split.json`
- id ไม่ซ้ำ และ `instruction` ของทุกข้อไม่ว่าง
- ไฟล์เฉลยที่ plug-in ระบุไว้มีอยู่จริงทุกไฟล์
- ทุก id ตรงกับชื่อชุดกรณีทดสอบในตัวตรวจ (`TASKS` ใน `benchmark_grader.py`)
- ค้นใน `/ba/reference/` ด้วย id ของ validation และ test ทุกข้อ ชื่อฟังก์ชันของโจทย์ชุดนั้น และคำว่า grader กับ validation ไม่พบเลย
- ลบไฟล์ `__pycache__` ที่เกิดจากการทดลองออกแล้ว

**Plug-in**
- ตาราง `SPLIT` เขียนไว้ในไฟล์เอง
- `instruction` มาจาก `brief` ในไฟล์โจทย์
- `answer_files` ชี้ไปที่ `solve.py` และ `test_solve.py` ของแต่ละข้อ
- `grading` เป็น `{"key": <id>, "function": <ชื่อฟังก์ชัน>}`
- `category` คือ `"billing"` และ `inputs` เป็น list ว่าง เพราะ benchmark นี้ไม่มีไฟล์ตั้งต้น

**สิ่งที่ใส่ใน `/ba/reference/`** (ตามที่ผู้ใช้ให้ Evolver เห็นของ train ได้)
- `tasks/` ไฟล์โจทย์ของ t1-cafe-bill, t2-split-bill, t3-shipping-fee และ t4-cashback
- `answers/<id>/` ไฟล์ `solve.py` และ `test_solve.py` ของ 4 ข้อเดียวกัน

**สิ่งที่ตั้งใจไม่ใส่**
- ไฟล์โจทย์และเฉลยของ v1-parking-fee, v2-net-pay, x1-late-fee, x2-refund และ x3-bulk-price เพราะเป็นชุด validation และ test
- `/data/split.json` เพราะมีรายชื่อโจทย์ของทั้งสามชุดรวมกัน
- `benchmark_grader.py` และคำอธิบายว่าตัวตรวจให้คะแนนอย่างไร
- `plugin_api.py` และ `plugin_skeleton.py` เพราะ Evolver ไม่ต้องใช้

`test_solve.py` ของช
…(ตัด 100 ตัวอักษร)
