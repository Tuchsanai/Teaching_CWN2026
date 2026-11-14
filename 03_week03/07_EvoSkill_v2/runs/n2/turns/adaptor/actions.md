# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; find /data -maxdepth 3 | head -100; cat /data/split.json
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
…(ตัด 22695 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json tasks/t4-cashback.json; ls answers/*; ls -la /ba /ba/reference 2>&1 | head -20
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}{
 "id": "t4-cashback",
 "function": "cashback",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก\n- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = \"silver\" \"gold\" หรือ \"platinum\" · `birthday` = True คือซื้อในเดือนเกิด\n- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%\n- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน\n- เดือนเกิด ได้เงินคืน 2 เท่า\n- เงินคืนสูงสุด 200 บาทต่อบิล\n- คืนเงินคืน เป็นจำนวนเต็มสตางค์"
}answers/t1-cafe-bill:
solve.py
test_solve.py

answers/t2-split-bill:
solve.py
test_solve.py

answers/t3-shipping-fee:
solve.py
test_solve.py

answers/t4-cashback:
solve.py
test_solve.py

answers/v1-parking-fee:
solve.py
test_solve.py

answers/v2-net-pay:
solve.py
test_solve.py

answers/x1-late-fee:
solve
…(ตัด 541 ตัวอักษร)
```

### ขั้น 3 · Bash

```
find /ba/data | head; cd /data/baankafe; grep -il "grader\|hidden\|policy" answers/t*/* ; cat answers/t3-shipping-fee/solve.py | head -40
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
"""คิดค่าส่ง · เฉลยอ้างอิงตามมาตรฐานคิดเงินของร้าน BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool และ float ไม่ใช่ int
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value

def shipping_fee(weight_g, distance_km, express):
    need_int(weight_g, "weight_g", 1, 30000)
    need_int(distance_km, "distance_km", 0)
    need_bool(express, "express")
    if express and weight_g > 20000:  # นโยบาย S
…(ตัด 477 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
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
        tasks.append(Task(
            id=tid,
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=["answers/%s/solve.py" % tid, "answers/%s/test_solve.py" % tid],
            grading={"key": tid},
            category="coding",
        ))
    return tasks
EOF
cd /ba/reference && mkdir -p tasks answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json tasks/; cp -r /data/baankafe/answers/$t answers/; done
printf '%s\n' 'โฟลเดอร์ `answers/<task id>/` คือผลงานของโจทย์นั้นที่ได้คะแนนเต็ม ประกอบด้วย 2 ไฟล์ คือ `solve.py` และ `test_solve.py`' > README.md
find . -type f | sort
cd /ba/setup && python3 -c "
import benchmark_plugin as b,os
ts=b.list_tasks('/data/baankafe')
for t in ts:
    print(t.id,t.split,[os.path.isfile('/data/baankafe/'+p) for p in t.answer_files])
"
grep -rn "x1\|x2\|x3\|v1\|v2\|parking\|net-pay\|late\|refund\|bulk" /ba/reference | head
```

ผลที่ได้:

```
./README.md
./answers/t1-cafe-bill/solve.py
./answers/t1-cafe-bill/test_solve.py
./answers/t2-split-bill/solve.py
./answers/t2-split-bill/test_solve.py
./answers/t3-shipping-fee/solve.py
./answers/t3-shipping-fee/test_solve.py
./answers/t4-cashback/solve.py
./answers/t4-cashback/test_solve.py
./tasks/t1-cafe-bill.json
./tasks/t2-split-bill.json
./tasks/t3-shipping-fee.json
./tasks/t4-cashback.json
t1-cafe-bill train [True, True]
t2-split-bill train [True, True]
t3-shipping-fee train [True, True]
t4-cashback train [True, True]
v1-parking-fee validation [True, True]
v2-net-pay validation [True, True]
x1-late-fee test [True, True]
x2-refund test [True, True]
x3-bulk-price test [True, True]
Shell cwd was reset to /ba/work
```

**Agent พูด:** เขียน plug-in กับโฟลเดอร์ reference เสร็จแล้ว `list_tasks('/data/baankafe')` คืนโจทย์ครบ 9 ข้อ และไฟล์เฉลยของทุกข้อมีอยู่จริง ผมไม่ได้รันตัวตรวจ

**`/ba/setup/benchmark_plugin.py`**
- การแบ่งชุดตาม `/data/split.json`: train 4 ข้อ (t1–t4), validation 2 ข้อ (v1, v2) และ test 3 ข้อ (x1–x3)
- `instruction` ของแต่ละข้อมาจาก `brief` ใน `tasks/<id>.json`
- `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `answers/<id>/test_solve.py`
- `grading` เป็น `{"key": <task id>}` เพื่อให้ตัวตรวจเลือกชุดกรณีทดสอบถูกข้อ
- `inputs` ว่าง เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น

**`/ba/reference/`** มีเฉพาะสิ่งที่ Evolver เห็นได้:
- `README.md` มีข้อความที่ผู้ใช้กำหนดข้อความเดียว
- `tasks/` มีไฟล์โจทย์ของ train 4 ข้อ
- `answers/` มีเฉลยของ train 4 ข้อ (`solve.py` และ `test_solve.py`) โครงเดิม
- ไม่มีไฟล์ของ validation หรือ test, `split.json` (เพราะมีชื่อโจทย์ validation กับ test) หรือโค้ดของตัวตรวจ
- ผมค้นหาชื่อโจทย์ validation และ test ใน reference แล้วไม่พบ

เฉลยของ t3 และ t4 มีคอมเมนต์นโยบาย S1, S2 ที่ตัวตรวจใช้ตรวจ ผมคงไว้ตามเดิม เพราะผู้ใช้ระบุว่า Evolver อ่านเฉลยของ train ได้

ขนาดการรัน (3 epochs, 3 samples per task) ไม่ได้อยู่ในไฟล์ที่ผมเขียน ให้ตั้งที่ตัวควบคุม loop
