# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; cat plugin_api.py plugin_skeleton.py; echo ----; cat benchmark_grader.py; echo ----; cat /data/split.json; ls -R /data/baankafe | head -50; ls -la /ba/reference
```

ผลที่ได้:

```
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
"""benchmark_plugin.py (โครงเปล่า) - Benchmark Adaptor เติมไฟล์นี้ แล้วบันทึกเป็น benchmark_
…(ตัด 19906 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data; ls -la . baankafe/tasks; cat baankafe/tasks/t1-cafe-bill.json; ls /ba /ba/setup
```

ผลที่ได้:

```
.:
total 16
drwxr-xr-x 3 root root 4096 Nov 13 10:20 .
drwxr-xr-x 1 root root 4096 Nov 13 08:52 ..
drwxr-xr-x 4 root root 4096 Nov 13 08:46 baankafe
-rw-r--r-- 1 root root  213 Nov 13 10:20 split.json

baankafe/tasks:
total 44
drwxr-xr-x 2 root root 4096 Nov 13 08:46 .
drwxr-xr-x 4 root root 4096 Nov 13 08:46 ..
-rw-r--r-- 1 root root  753 Nov 13 08:46 t1-cafe-bill.json
-rw-r--r-- 1 root root  972 Nov 13 08:46 t2-split-bill.json
-rw-r--r-- 1 root root 1083 Nov 13 08:46 t3-shipping-fee.json
-rw-r--r-- 1 root root  914 Nov 13 08:46 t4-cashback.json
-rw-r--r-- 1 root root  997 Nov 13 08:46 v1-parking-fee.json
-rw-r--r-- 1 root root 1132 Nov 13 08:46 v2-net-pay.json
-rw-r--r-- 1 root root 1008 Nov 13 08:46 x1-late-fee.json
-rw-r--r-- 1 root root 1049 Nov 13 08:46 x2-refund.json
-rw-r--r-- 1 root root  894 Nov 13 08:46 x3-bulk-price.json
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n
…(ตัด 175 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe billing-code tasks (9 tasks)."""
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
        path = os.path.join(root, "tasks", tid + ".json")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        answers = [
            "answers/%s/solve.py" % tid,
            "answers/%s/test_solve.py" % tid,
        ]
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[a for a in answers if os.path.isfile(os.path.join(root, a))],
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do
 cp /data/baankafe/tasks/$t.json /ba/reference/baankafe/tasks/
 cp -r /data/baankafe/answers/$t /ba/reference/baankafe/answers/
done
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files,len(t.instruction))
"
find /ba/reference -type f; grep -rl "v1-\|v2-\|x1-\|x2-\|x3-\|parking\|net_pay\|late_fee\|refund\|bulk" /ba/reference
```

ผลที่ได้:

```
t1-cafe-bill train ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] 329
t2-split-bill train ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] 405
t3-shipping-fee train ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] 485
t4-cashback train ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] 417
v1-parking-fee validation ['answers/v1-parking-fee/solve.py', 'answers/v1-parking-fee/test_solve.py'] 408
v2-net-pay validation ['answers/v2-net-pay/solve.py', 'answers/v2-net-pay/test_solve.py'] 458
x1-late-fee test ['answers/x1-late-fee/solve.py', 'answers/x1-late-fee/test_solve.py'] 405
x2-refund test ['answers/x2-refund/solve.py', 'answers/x2-refund/test_solve.py'] 429
x3-bulk-price test ['answers/x3-bulk-price/solve.py', 'answers/x3-bulk-price/test_solve.py'] 391
/ba/reference/baankafe/tasks/t3-shipping-fee.json
/ba/reference/baankafe/tasks/t4-cashback.json
/ba/reference/baankafe/tasks/t1-cafe-bill.json
/ba/reference/baankafe/tasks/t2-split-bill.json
/ba/reference/baankafe/answers/t4-cashback/test_solve.py
/ba/reference/baankafe/answers/t4-cashback/solve.py
/ba/reference/baankafe/answers/t1-cafe
…(ตัด 302 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -rn "v1-\|v2-\|x1-\|x2-\|x3-\|parking\|net_pay\|late_fee\|refund\|bulk" /ba/reference | head
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน plug-in กับเติมโฟลเดอร์ reference เสร็จแล้ว ทดสอบ `list_tasks('/data/baankafe')` แล้วได้ 9 โจทย์ ตามการแบ่งชุดที่ให้มา ผมไม่ได้รันตัวตรวจ

**`/ba/setup/benchmark_plugin.py`**
- การแบ่งชุดเขียนไว้ในไฟล์ตามที่ `/data/split.json` ให้มา: train 4 ข้อ, validation 2 ข้อ, test 3 ข้อ
- `list_tasks(root)` อ่านเฉพาะ `root/tasks/<id>.json` และ `root/answers/<id>/...`
- แต่ละ `Task` ใช้ `brief` เป็น `instruction` และใส่ path ของ `solve.py` กับ `test_solve.py` ไว้ใน `answer_files`
- ตั้ง `grading={"key": id, "function": ...}` ซึ่งตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ
- `inputs` เป็นลิสต์ว่าง เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- import เฉพาะ standard library กับ `plugin_api`

**`/ba/reference/baankafe/`**
- มี `tasks/<id>.json` และ `answers/<id>/` (`solve.py`, `test_solve.py`) ของโจทย์ train 4 ข้อ: `t1-cafe-bill`, `t2-split-bill`, `t3-shipping-fee`, `t4-cashback` โครงโฟลเดอร์เหมือนใน data root
- ไม่มีไฟล์ของ validation และ test และไม่มี `benchmark_grader.py` หรือคำอธิบายตัวตรวจ
- ผมไม่ได้คัดลอก `/data/split.json` เพราะมีชื่อโจทย์ validation และ test
- ผมค้นหาชื่อโจทย์และคำเฉพาะของโจทย์ชุดอื่นในโฟลเดอร์นี้ ไม่พบเลย
