# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; cat /data/split.json; find /data -maxdepth 3 | head -80
```

ผลที่ได้:

```
benchmark_grader.py
plugin_api.py
plugin_skeleton.py
"""plugin_api.py - รูปแบบของ 1 โจทย์ ที่ plug-in ของ Benchmark Adaptor ต้องคืน

plug-in (benchmark_plugin.py) มีฟังก์ชันเดียว:

    def list_tasks(root) -> list[Task]      root = path ของ data root

กติกาของ plug-in: อ่านเฉพาะไฟล์ใต้ root · import ได้เฉพาะ Python standard library และ plugin_api
ห้ามรันตัวตรวจ ห้ามเริ่ม process ห้ามใช้เครือข่าย · การแบ่งชุด (split) เขียนไว้ในไฟล์ของ plug-in เอง
"""
from dataclasses import dataclass, field, asdict

SPLITS = ("train", "validation", "test")


@dataclass
class Task:
    id: str                                   # ชื่อโจทย์ ไม่ซ้ำกัน
    split: str                                # "train" | "validation" | "test"
    instruction: str                          # ข้อความโจทย์ที่ Solver ได้รับ
    inputs: list = field(default_factory=list)        # ไฟล์ตั้งต้นของโจทย์ (path เทียบกับ root) · โจทย์นี้ไม่มี
    answer_files: list = field(default_factory=list)  # ไฟล์เฉลยของโจทย์ (path เทียบกับ root)
    grading: dict = field(default_factory=dict)       # ค่าที่ตัวตรวจของผู้ใช้อ่าน
    category: str = ""

    def to_dict(self):
        return asdict(self)
"""benchmark_plugin.py (โครงเปล่า) - Be
…(ตัด 19895 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json; ls answers/t1-cafe-bill; ls -la /ba /ba/reference 2>&1; python3 -c "
import json,glob
for f in sorted(glob.glob('tasks/*.json')): d=json.load(open(f)); print(f, list(d))"
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}solve.py
test_solve.py
/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 13 09:02 .
drwxr-xr-x 1 root root 4096 Nov 13 08:52 ..
drwxr-xr-x 3 root root 4096 Nov 13 09:02 data
drwxr-xr-x 2 root root 4096 Nov 13 09:02 reference
drwxr-xr-x 2 root root 4096 Nov 13 09:02 setup
drwxr-xr-x 2 root root 4096 Nov 13 09:02 work

/ba/reference:
total 8
drwxr-xr-x 2 root root 4096 Nov 13 09:02 .
drwxr-xr-x 6 root root 4096 Nov 13 09:02 ..
tasks/t1-cafe-bill.json ['id', 'function', 'brief']
tasks/t2-split-bill.json ['id', 'function', 'brief']
tasks/t3-shipping-fee.json ['id', 'function', 'brief']
tasks/t4-cashback.json ['id', 'function', 'brief']
tasks/v1-parking-fee.json ['id', 'function', 'brief']
tasks/v2-net-pay.json ['id', 'function', 'brief']
tasks/x1-late-fee.json ['id', 'function', 'brief']
tasks/
…(ตัด 127 ตัวอักษร)
```

### ขั้น 3 · Bash

```
find /ba/data | head; mkdir -p /ba/reference/tasks /ba/reference/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/tasks/; cp -r answers/$t /ba/reference/answers/; done
cat > /ba/reference/split.json <<'E'
{
 "train": [
  "t1-cafe-bill",
  "t2-split-bill",
  "t3-shipping-fee",
  "t4-cashback"
 ]
}
E
cat > /ba/setup/benchmark_plugin.py <<'E'
"""benchmark_plugin.py - BaanKafe: โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ"""
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
        ans_dir = os.path.join(root, "answers", tid)
        answers = []
        if os.path.isdir(ans_dir):
            answers = ["answers/%s/%s" % (tid, n) for n in sorted(os.listdir(ans_dir))
                       if os.path.isfile(os.path.join(ans_dir, n))]
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=answers,
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
E
cd /ba/setup && python3 -c "
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files,t.grading)"
grep -rIl -e v1-parking -e x1-late -e net-pay -e refund -e bulk /ba/reference; find /ba/reference -type f
```

ผลที่ได้:

```
/ba/data
/ba/data/baankafe
/ba/data/split.json
/ba/data/baankafe/answers
/ba/data/baankafe/tasks
/ba/data/baankafe/answers/t4-cashback
/ba/data/baankafe/answers/v2-net-pay
/ba/data/baankafe/answers/t1-cafe-bill
/ba/data/baankafe/answers/x3-bulk-price
/ba/data/baankafe/answers/x2-refund
t1-cafe-bill train ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] {'key': 't1-cafe-bill', 'function': 'cafe_bill'}
t2-split-bill train ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] {'key': 't2-split-bill', 'function': 'split_bill'}
t3-shipping-fee train ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] {'key': 't3-shipping-fee', 'function': 'shipping_fee'}
t4-cashback train ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] {'key': 't4-cashback', 'function': 'cashback'}
v1-parking-fee validation ['answers/v1-parking-fee/solve.py', 'answers/v1-parking-fee/test_solve.py'] {'key': 'v1-parking-fee', 'function': 'parking_fee'}
v2-net-pay validation ['answers/v2-net-pay/solve.py', 'answers/v2-net-pay/test_solve.py'] {'key': 'v2-net-pay', 'function': 'net_pay'}
x1-late-fee test ['answers/x1-late-fee/solve.py'
…(ตัด 943 ตัวอักษร)
```

**Agent พูด:** ผมเขียน plug-in และเติมโฟลเดอร์ reference เสร็จแล้ว ทดสอบ `list_tasks('/data/baankafe')` ได้ครบ 9 โจทย์ แบ่งเป็น train 4, validation 2 และ test 3 ตามที่ให้มา ผมไม่ได้รันตัวตรวจ เพราะ loop เป็นผู้รัน

- **`/ba/setup/benchmark_plugin.py`:** อ่านเฉพาะ `tasks/<id>.json` ใต้ root และเก็บการแบ่งชุดไว้ในตัวไฟล์
  - แต่ละ `Task` มี `instruction` จาก `brief` และ `answer_files` เป็น `solve.py` กับ `test_solve.py` ของโจทย์นั้น
  - ช่อง `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่านเฉพาะ `key`
  - `inputs` ว่างเพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- **`/ba/reference/`:** มีเฉพาะส่วนที่ Evolver เห็นได้
  - `tasks/` กับ `answers/` ของโจทย์ train ทั้ง 4 ข้อ (`t1-cafe-bill`, `t2-split-bill`, `t3-shipping-fee`, `t4-cashback`)
  - `split.json` ที่ตัดให้เหลือเฉพาะรายชื่อ train เพราะไฟล์ต้นฉบับมีชื่อโจทย์ validation และ test อยู่ด้วย
  - ไม่มีโค้ดตัวตรวจ และค้นแล้วไม่พบชื่อโจทย์ validation หรือ test ในโฟลเดอร์นี้
