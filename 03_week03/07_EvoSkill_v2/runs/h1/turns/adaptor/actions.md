# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; cat /data/split.json; find /data -type f | head -100
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
…(ตัด 20580 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; cat tasks/v1-parking-fee.json; echo; cat answers/t1-cafe-bill/solve.py; ls /ba /ba/reference
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
…(ตัด 1464 ตัวอักษร)
```

### ขั้น 3 · Bash

```
mkdir -p /ba/reference/tasks /ba/reference/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/tasks/; cp -r answers/$t /ba/reference/answers/; done
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe billing tasks (9 tasks: 4 train / 2 validation / 3 test)"""
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
            answer_files=[
                "answers/%s/solve.py" % tid,
                "answers/%s/test_solve.py" % tid,
            ],
            grading={"key": tid, "function": d["function"]},
            category="billing",
        ))
    return tasks
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.grading,t.answer_files[0])
"
grep -rl -E "parking|net_pay|late_fee|refund|bulk" /ba/reference; find /ba/reference -type f
```

ผลที่ได้:

```
t1-cafe-bill train {'key': 't1-cafe-bill', 'function': 'cafe_bill'} answers/t1-cafe-bill/solve.py
t2-split-bill train {'key': 't2-split-bill', 'function': 'split_bill'} answers/t2-split-bill/solve.py
t3-shipping-fee train {'key': 't3-shipping-fee', 'function': 'shipping_fee'} answers/t3-shipping-fee/solve.py
t4-cashback train {'key': 't4-cashback', 'function': 'cashback'} answers/t4-cashback/solve.py
v1-parking-fee validation {'key': 'v1-parking-fee', 'function': 'parking_fee'} answers/v1-parking-fee/solve.py
v2-net-pay validation {'key': 'v2-net-pay', 'function': 'net_pay'} answers/v2-net-pay/solve.py
x1-late-fee test {'key': 'x1-late-fee', 'function': 'late_fee'} answers/x1-late-fee/solve.py
x2-refund test {'key': 'x2-refund', 'function': 'refund'} answers/x2-refund/solve.py
x3-bulk-price test {'key': 'x3-bulk-price', 'function': 'bulk_price'} answers/x3-bulk-price/solve.py
/ba/reference/tasks/t3-shipping-fee.json
/ba/reference/tasks/t4-cashback.json
/ba/reference/tasks/t1-cafe-bill.json
/ba/reference/tasks/t2-split-bill.json
/ba/reference/answers/t4-cashback/test_solve.py
/ba/reference/answers/t4-cashback/solve.py
/ba/reference/answers/t1-cafe-bill/test_solve.py
/ba/reference/an
…(ตัด 253 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -rn -E "parking|net_pay|late_fee|refund|bulk" /ba/reference | cut -c1-200
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ผมทดสอบ `list_tasks('/data/baankafe')` แล้ว ได้ 9 โจทย์แบ่งเป็น train 4, validation 2 และ test 3 ตรงกับ `/data/split.json` ผมไม่ได้รันตัวตรวจ

**`benchmark_plugin.py`**
- ตาราง `SPLIT` ฝังอยู่ในไฟล์ plug-in เอง ใช้เฉพาะ standard library กับ `plugin_api` และสร้าง path ทั้งหมดจาก `root`
- `Task` แต่ละตัวมีค่าดังนี้:
  - `instruction` คือ `brief` จาก `tasks/<id>.json`
  - `answer_files` คือ `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py`
  - `grading` เป็น `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ซึ่งตัวตรวจอ่าน `key` เพื่อเลือกชุดกรณีทดสอบ
  - `inputs` ว่าง และ `category` เป็น `"billing"`

**`/ba/reference/`**
- มีเฉพาะโจทย์ train 4 ข้อ โดยคงโครงเดิม คือ `tasks/<id>.json` และ `answers/<id>/{solve.py,test_solve.py}` ซึ่งตรงกับสิ่งที่ข้อ 4 ให้ Evolver เห็นได้
- ไม่มีไฟล์ของ validation หรือ test และไม่มีโค้ดตัวตรวจ ผม grep หาชื่อฟังก์ชันของโจทย์ validation และ test แล้วไม่พบ
- ผมไม่ได้คัดลอก `split.json` เพราะมีรายชื่อโจทย์ validation และ test อยู่
