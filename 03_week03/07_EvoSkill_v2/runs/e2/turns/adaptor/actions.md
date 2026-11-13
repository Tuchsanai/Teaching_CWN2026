# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; cat /data/split.json; find /data/baankafe | head -100
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 09:21 .
drwxr-xr-x 6 root root  4096 Nov 13 09:21 ..
-rwxr-xr-x 1 root root 20223 Nov 13 09:21 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 09:21 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 09:21 plugin_skeleton.py
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
…(ตัด 20946 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json tasks/x1-late-fee.json; ls /data /ba /ba/reference; head -30 answers/t1-cafe-bill/solve.py
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}{
 "id": "x1-late-fee",
 "function": "late_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `late_fee(amount, days_late)` ในไฟล์ `solve.py` สำหรับคิดค่าปรับของลูกค้าขายส่งที่ชำระเงินช้า\n- `amount` = ยอดค้างชำระ (สตางค์ ตั้งแต่ 0) · `days_late` = จำนวนวันที่ช้า (จำนวนเต็ม 0–365)\n- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ\n- ช้าเกิน 3 วัน คิดค่าปรับวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)\n- ค่าปรับสูงสุด 15% ของยอดค้างชำระ\n- คืนค่าปรับ เป็นจำนวนเต็มสตางค์"
}/ba:
data
reference
setup
work

/ba/reference:

/data:
baankafe
split.json
"""คิดเงินหน้าร้าน · เฉลยอ้างอิงตามมาตรฐานคิดเงินของร้าน BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need
…(ตัด 662 ตัวอักษร)
```

### ขั้น 3 · Bash

```
mkdir -p /ba/reference/tasks /ba/reference/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/tasks/; cp -r answers/$t /ba/reference/answers/; done
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe: โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ (train 4 · validation 2 · test 3)"""
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
        answer_files = []
        for name in ("solve.py", "test_solve.py"):
            rel = "answers/%s/%s" % (tid, name)
            if os.path.isfile(os.path.join(root, "answers", tid, name)):
                answer_files.append(rel)
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=answer_files,
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files,t.grading)
"; find /ba/reference -type f; grep -rl "validation\|v1-\|x1-" /ba/reference
```

ผลที่ได้:

```
t1-cafe-bill train ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] {'key': 't1-cafe-bill', 'function': 'cafe_bill'}
t2-split-bill train ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] {'key': 't2-split-bill', 'function': 'split_bill'}
t3-shipping-fee train ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] {'key': 't3-shipping-fee', 'function': 'shipping_fee'}
t4-cashback train ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] {'key': 't4-cashback', 'function': 'cashback'}
v1-parking-fee validation ['answers/v1-parking-fee/solve.py', 'answers/v1-parking-fee/test_solve.py'] {'key': 'v1-parking-fee', 'function': 'parking_fee'}
v2-net-pay validation ['answers/v2-net-pay/solve.py', 'answers/v2-net-pay/test_solve.py'] {'key': 'v2-net-pay', 'function': 'net_pay'}
x1-late-fee test ['answers/x1-late-fee/solve.py', 'answers/x1-late-fee/test_solve.py'] {'key': 'x1-late-fee', 'function': 'late_fee'}
x2-refund test ['answers/x2-refund/solve.py', 'answers/x2-refund/test_solve.py'] {'key': 'x2-refund', 'function': 'refund'}
x3-bulk-price test ['answers/x3-bulk-price/solve.py', 'answers/x3-bulk-price/
…(ตัด 599 ตัวอักษร)
```

**Agent พูด:** ผมเขียน plug-in และเติมโฟลเดอร์ reference ให้ Evolver เสร็จแล้ว ทดสอบ `list_tasks('/data/baankafe')` แล้วคืนครบ 9 โจทย์ ตัวตรวจไม่ได้ถูกรัน

**`/ba/setup/benchmark_plugin.py`**
- การแบ่งชุดเป็นไปตาม `/data/split.json` เขียนไว้ใน `SPLIT` ของไฟล์ plug-in เอง
  - train: t1-cafe-bill, t2-split-bill, t3-shipping-fee, t4-cashback
  - validation: v1-parking-fee, v2-net-pay
  - test: x1-late-fee, x2-refund, x3-bulk-price
- `list_tasks(root)` อ่านเฉพาะ `root/tasks/<id>.json` และสร้าง `Task` ต่อโจทย์ โดย `instruction` คือ `brief` ส่วน `inputs` ว่างเพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- `answer_files` คือ `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py` และ `category` ตั้งเป็น `"coding"`
- `grading` มี `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ซึ่ง `key` คือค่าที่ตัวตรวจใช้เลือกชุดกรณีทดสอบ

**`/ba/reference/`** มีเฉพาะของโจทย์ชุด train โดยคงโครงโฟลเดอร์เดิม
- `tasks/<id>.json` 4 ไฟล์
- `answers/<id>/solve.py` และ `test_solve.py` ของโจทย์ train ทั้ง 4 ข้อ
- ไม่ได้คัดลอก `split.json` เพราะมีชื่อโจทย์ validation กับ test อยู่ข้างใน
- ไม่มีโค้ดตัวตรวจ และค้นหาชื่อโจทย์ validation กับ test ในโฟลเดอร์นี้แล้วไม่พบ

ขนาดการรัน (3 epochs, 3 samples ต่อโจทย์) ไม่มีที่ให้ตั้งใน plug-in ผมจึงไม่ได้ใส่ไว้ที่ไหน
