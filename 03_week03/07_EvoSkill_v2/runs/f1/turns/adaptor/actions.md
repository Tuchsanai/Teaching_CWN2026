# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; cat /data/split.json; find /data -type f | head -100
```

ผลที่ได้:

```
total 40
drwxr-xr-x 2 root root  4096 Nov 15 04:05 .
drwxr-xr-x 6 root root  4096 Nov 15 04:05 ..
-rwxr-xr-x 1 root root 24093 Nov 15 04:05 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 15 04:05 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 15 04:05 plugin_skeleton.py
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
    answer_files: list = field(default_factory=list)  # ไฟล์เฉลยของ
…(ตัด 23160 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; cat tasks/t4-cashback.json; echo; ls -R /ba | head -30; cat answers/t4-cashback/solve.py
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
{
 "id": "t4-cashback",
 "function": "cashback",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก\n- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = \"silver\" \"gold\" หรือ \"platinum\" · `birthday` = True คือซื้อในเดือนเกิด\n- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%\n- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน\n- เดือนเกิด ได้เงินคืน 2 เท่า\n- เงินคืนสูงสุด 200 บาทต่อบิล\n- คืนเงินคืน เป็นจำนวนเต็มสตางค์"
}
/ba:
data
reference
setup
work

/ba/data:
baankafe
split.json

/ba/data/baankafe:
answers
tasks

/ba/data/baankafe/answers:
t1-cafe-bill
t2-split-bill
t3-shipping-fee
t4-cashback
v1-parking-fee
v2-net-pay
x1-late-fee
x2-refund
x3-bulk-price

/ba/data/baankafe/answers/t1-cafe-bill:
solve.py
test_solve.p
…(ตัด 1782 ตัวอักษร)
```

### ขั้น 3 · Bash

```
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/baankafe/tasks/; cp -r answers/$t /ba/reference/baankafe/answers/; done
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe billing-function tasks (9 tasks: 4 train / 2 validation / 3 test)."""
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
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=["answers/%s/solve.py" % tid, "answers/%s/test_solve.py" % tid],
            grading={"key": d["id"], "function": d["function"]},
            category="billing",
        ))
    return tasks
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b, os
ts=b.list_tasks('/data/baankafe')
for t in ts:
    print(t.id,t.split,t.grading,[os.path.isfile('/data/baankafe/'+a) for a in t.answer_files])
"
grep -ril "grader\|validation\|v1-\|x1-" /ba/reference; find /ba/reference -type f
```

ผลที่ได้:

```
t1-cafe-bill train {'key': 't1-cafe-bill', 'function': 'cafe_bill'} [True, True]
t2-split-bill train {'key': 't2-split-bill', 'function': 'split_bill'} [True, True]
t3-shipping-fee train {'key': 't3-shipping-fee', 'function': 'shipping_fee'} [True, True]
t4-cashback train {'key': 't4-cashback', 'function': 'cashback'} [True, True]
v1-parking-fee validation {'key': 'v1-parking-fee', 'function': 'parking_fee'} [True, True]
v2-net-pay validation {'key': 'v2-net-pay', 'function': 'net_pay'} [True, True]
x1-late-fee test {'key': 'x1-late-fee', 'function': 'late_fee'} [True, True]
x2-refund test {'key': 'x2-refund', 'function': 'refund'} [True, True]
x3-bulk-price test {'key': 'x3-bulk-price', 'function': 'bulk_price'} [True, True]
/ba/reference/baankafe/tasks/t3-shipping-fee.json
/ba/reference/baankafe/tasks/t4-cashback.json
/ba/reference/baankafe/tasks/t1-cafe-bill.json
/ba/reference/baankafe/tasks/t2-split-bill.json
/ba/reference/baankafe/answers/t4-cashback/test_solve.py
/ba/reference/baankafe/answers/t4-cashback/solve.py
/ba/reference/baankafe/answers/t1-cafe-bill/test_solve.py
/ba/reference/baankafe/answers/t1-cafe-bill/solve.py
/ba/reference/baankafe/answers/t2-split-bill/test_sol
…(ตัด 208 ตัวอักษร)
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เรียบร้อยแล้ว ทดสอบ plug-in กับ `/data/baankafe` แล้วได้ 9 โจทย์ ไฟล์เฉลยของทุกโจทย์มีอยู่จริง ผมไม่ได้รันตัวตรวจ

**`benchmark_plugin.py`**
- การแบ่งชุดเขียนไว้ในไฟล์เอง ตาม `/data/split.json`: train 4 ข้อ (t1–t4), validation 2 ข้อ (v1, v2), test 3 ข้อ (x1–x3)
- `list_tasks(root)` อ่านเฉพาะ `root/tasks/<id>.json` โดย `instruction` คือ `brief` และ `answer_files` ชี้ไปที่ `answers/<id>/solve.py` กับ `test_solve.py`
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่านเฉพาะ `key` ส่วน `function` ผมใส่เสริมเอง
- ใช้เฉพาะ standard library กับ `plugin_api` และไม่รัน process

**`/ba/reference/`** มีเฉพาะของโจทย์ train ตามที่คำสั่งอนุญาต โดยคงโครงเดิมไว้:
- `baankafe/tasks/` มีไฟล์โจทย์ของ t1–t4
- `baankafe/answers/` มี `solve.py` กับ `test_solve.py` ของ t1–t4
- ผมไม่ได้คัดลอก `split.json` เพราะมีชื่อโจทย์ validation และ test
- ไม่มีโค้ดตัวตรวจ และไม่มีโจทย์หรือเฉลยของ validation หรือ test
- grep หาคำที่เกี่ยวกับตัวตรวจและชื่อโจทย์ validation/test ใน reference แล้วไม่พบ
