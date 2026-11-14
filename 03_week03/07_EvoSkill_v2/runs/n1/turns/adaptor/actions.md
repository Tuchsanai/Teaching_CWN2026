# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; find /data -maxdepth 3 | head -80; cat /data/split.json
```

ผลที่ได้:

```
total 40
drwxr-xr-x 2 root root  4096 Nov 15 03:52 .
drwxr-xr-x 6 root root  4096 Nov 15 03:52 ..
-rwxr-xr-x 1 root root 24093 Nov 15 03:52 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 15 03:52 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 15 03:52 plugin_skeleton.py
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
cd /data/baankafe; cat tasks/t3-shipping-fee.json; ls answers/*; ls -la /ba /ba/reference 2>&1 | head -20; python3 -c "
import json,glob
for f in sorted(glob.glob('tasks/*.json')): print(f, list(json.load(open(f)).keys()))"
```

ผลที่ได้:

```
{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน\n- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)\n- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%\n- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)\n- คืนค่าส่ง เป็นจำนวนเต็มสตางค์"
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
solve.py
test_solve.py

answers/x2-refund:
solve.py
test_solve.py

answers/x3-bulk-price:
solve.py
test_solve.py
/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 15 03:52 .
drwxr-xr-x 1 root root 4096 Nov 14 23:46 ..
drwxr-xr-x 3 root root 4096 Nov 15 03:52 data
drwxr-xr-x 2 root root 4096 Nov 15 03:52 reference
drwxr-xr-x 2 root root 4096 
…(ตัด 675 ตัวอักษร)
```

### ขั้น 3 · Bash

```
find /ba/data | head; cd /data/baankafe; cat answers/t3-shipping-fee/solve.py | head -50
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
…(ตัด 650 ตัวอักษร)
```

### ขั้น 4 · Bash

```
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
            spec = json.load(f)
        answers = [os.path.join("answers", tid, n) for n in ("solve.py", "test_solve.py")]
        tasks.append(Task(
            id=tid,
            split=split,
            instruction=spec["brief"],
            inputs=[],
            answer_files=answers,
            grading={"key": tid, "function": spec["function"]},
            category="coding",
        ))
    return tasks
EOF
R=/ba/reference; mkdir -p $R/tasks $R/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json $R/tasks/; cp -r /data/baankafe/answers/$t $R/answers/; done
printf '%s\n' 'โฟลเดอร์ `answers/<task id>/` คือผลงานของโจทย์นั้นที่ได้คะแนนเต็ม ประกอบด้วย 2 ไฟล์ คือ `solve.py` และ `test_solve.py`' > $R/README.md
find $R -type f | sort
cd /ba/setup && python3 -c "
import benchmark_plugin as b,os
ts=b.list_tasks('/data/baankafe')
for t in ts:
    print(t.id,t.split,t.grading,[os.path.isfile('/data/baankafe/'+a) for a in t.answer_files])
"; rm -rf /ba/setup/__pycache__; grep -rl -e x1-late -e v1-park -e v2-net -e x2-ref -e x3-bulk $R || echo clean
```

ผลที่ได้:

```
/ba/reference/README.md
/ba/reference/answers/t1-cafe-bill/solve.py
/ba/reference/answers/t1-cafe-bill/test_solve.py
/ba/reference/answers/t2-split-bill/solve.py
/ba/reference/answers/t2-split-bill/test_solve.py
/ba/reference/answers/t3-shipping-fee/solve.py
/ba/reference/answers/t3-shipping-fee/test_solve.py
/ba/reference/answers/t4-cashback/solve.py
/ba/reference/answers/t4-cashback/test_solve.py
/ba/reference/tasks/t1-cafe-bill.json
/ba/reference/tasks/t2-split-bill.json
/ba/reference/tasks/t3-shipping-fee.json
/ba/reference/tasks/t4-cashback.json
t1-cafe-bill train {'key': 't1-cafe-bill', 'function': 'cafe_bill'} [True, True]
t2-split-bill train {'key': 't2-split-bill', 'function': 'split_bill'} [True, True]
t3-shipping-fee train {'key': 't3-shipping-fee', 'function': 'shipping_fee'} [True, True]
t4-cashback train {'key': 't4-cashback', 'function': 'cashback'} [True, True]
v1-parking-fee validation {'key': 'v1-parking-fee', 'function': 'parking_fee'} [True, True]
v2-net-pay validation {'key': 'v2-net-pay', 'function': 'net_pay'} [True, True]
x1-late-fee test {'key': 'x1-late-fee', 'function': 'late_fee'} [True, True]
x2-refund test {'key': 'x2-refund', 'function': 'refund'} [Tr
…(ตัด 130 ตัวอักษร)
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ทดสอบ `list_tasks('/data/baankafe')` แล้ว คืนครบ 9 โจทย์ ไฟล์เฉลยทุกไฟล์มีอยู่จริง ผมไม่ได้รันตัวตรวจ ตามที่คำสั่งกำหนด

**`benchmark_plugin.py`**
- การแบ่งชุดตาม `/data/split.json` ผมเขียนไว้ใน dict `SPLIT` ในไฟล์ plug-in เอง: train 4 ข้อ, validation 2 ข้อ, test 3 ข้อ
- แต่ละ `Task` อ่านข้อความโจทย์จาก `tasks/<id>.json` ใต้ `root` และใส่ `answer_files` เป็น `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py`
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่านเฉพาะ `key` ส่วน `function` ผมใส่เพิ่มเอง
- `inputs` เป็นรายการว่าง เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น และ `category` ผมตั้งเป็น `"coding"`
- import เฉพาะ `json`, `os` และ `plugin_api`

**`/ba/reference/`** มี 13 ไฟล์
- `README.md` มีข้อความเดียวตามที่ผู้ใช้กำหนด
- `tasks/` มีไฟล์โจทย์ของ train 4 ข้อ
- `answers/<id>/` มี `solve.py` และ `test_solve.py` ของ train 4 ข้อ
- ผมไม่ได้คัดลอก `split.json` เพราะมีรายชื่อโจทย์ validation และ test ไม่ได้คัดลอกโค้ดตัวตรวจด้วย
- ผมค้นหา id ของโจทย์ validation และ test ทั้ง 5 ข้อในโฟลเดอร์นี้ ไม่พบเลย

เฉลยของ `t3-shipping-fee` และ `t4-cashback` มีนโยบายซ่อน (S1, S2, C1, C2) เป็นคอมเมนต์ในโค้ด Evolver จึงเห็นนโยบายเหล่านี้จากเฉลยของ train ผมเก็บไว้ครบ เพราะผู้ใช้ระบุว่า Evolver อ่านเฉลยของ train ได้ทั้งหมด
