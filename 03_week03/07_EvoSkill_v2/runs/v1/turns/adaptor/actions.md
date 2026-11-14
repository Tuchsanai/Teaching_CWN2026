# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; cat /data/split.json; find /data/baankafe | head -50
```

ผลที่ได้:

```
total 40
drwxr-xr-x 2 root root  4096 Nov 15 04:01 .
drwxr-xr-x 6 root root  4096 Nov 15 04:01 ..
-rwxr-xr-x 1 root root 24093 Nov 15 04:01 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 15 04:01 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 15 04:01 plugin_skeleton.py
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
…(ตัด 23521 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe/tasks; cat t1-cafe-bill.json t4-cashback.json; ls /ba /ba/reference; ls /data
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
}/ba:
data
reference
setup
work

/ba/reference:
baankafe
split.json
Shell cwd was reset to /ba/work
```

### ขั้น 3 · Bash

```
find /ba/reference /ba/data | head -60; ls -la /ba/data
```

ผลที่ได้:

```
/ba/reference
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
/ba/data/baankafe/answers/t2-split-bill
/ba/data/baankafe/answers/t3-shipping-fee
/ba/data/baankafe/answers/v1-parking-fee
/ba/data/baankafe/answers/x1-late-fee
/ba/data/baankafe/tasks/x1-late-fee.json
/ba/data/baankafe/tasks/x3-bulk-price.json
/ba/data/baankafe/tasks/x2-refund.json
/ba/data/baankafe/tasks/v2-net-pay.json
/ba/data/baankafe/tasks/t3-shipping-fee.json
/ba/data/baankafe/tasks/t4-cashback.json
/ba/data/baankafe/tasks/v1-parking-fee.json
/ba/data/baankafe/tasks/t1-cafe-bill.json
/ba/data/baankafe/tasks/t2-split-bill.json
/ba/data/baankafe/answers/x1-late-fee/test_solve.py
/ba/data/baankafe/answers/x1-late-fee/solve.py
/ba/data/baankafe/answers/t4-cashback/test_solve.py
/ba/data/baankafe/answers/t4-cashback/solve.py
/ba/data/baankafe/answers/v2-net-pay/test_solve.py
/ba/data/baankafe/answers/v2-net-pay/solve.py
/ba/data/baankafe/answers/t1-cafe-bill/test_solve.py
/ba/data/baa
…(ตัด 746 ตัวอักษร)
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
            d = json.load(f)
        tasks.append(Task(
            id=tid,
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[os.path.join("answers", tid, "solve.py"),
                          os.path.join("answers", tid, "test_solve.py")],
            grading={"key": tid, "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
ts=b.list_tasks('/data/baankafe')
for t in ts: print(t.id,t.split,t.grading,[__import__('os').path.isfile('/data/baankafe/'+a) for a in t.answer_files])
"
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json /ba/reference/baankafe/tasks/; cp -r /data/baankafe/answers/$t /ba/reference/baankafe/answers/; done
find /ba/reference -type f; grep -ril "v1-\|v2-\|x1-\|x2-\|x3-\|grader" /ba/reference || echo clean
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
…(ตัด 214 ตัวอักษร)
```

**Agent พูด:** ผมเขียน `benchmark_plugin.py` ลงใน `/ba/setup/` และเติม `/ba/reference/` ให้แล้ว ทดสอบ plug-in กับ `/data/baankafe` แล้ว `list_tasks` คืนครบ 9 โจทย์ และไฟล์เฉลยของทุกโจทย์มีอยู่จริง ผมไม่ได้รันตัวตรวจ

**`/ba/setup/benchmark_plugin.py`**
- การแบ่งชุดทำตาม `/data/split.json` และเขียนฝังไว้ในไฟล์ plug-in
  - train: `t1-cafe-bill`, `t2-split-bill`, `t3-shipping-fee`, `t4-cashback`
  - validation: `v1-parking-fee`, `v2-net-pay`
  - test: `x1-late-fee`, `x2-refund`, `x3-bulk-price`
- แต่ละ `Task` ใช้ `brief` เป็น `instruction` และใส่ `answer_files` เป็น `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py` (path เทียบกับ root)
- ฟิลด์ `grading` คือ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่าน `key` เพื่อเลือกชุดกรณีทดสอบ
- `inputs` ว่าง เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- plug-in อ่านเฉพาะไฟล์ใต้ `root` และ import เฉพาะ standard library กับ `plugin_api`

**`/ba/reference/`**
- ใส่เฉพาะ `baankafe/tasks/` และ `baankafe/answers/` ของ 4 โจทย์ชุด train โดยคงโครงโฟลเดอร์เดิม
- ไม่ได้คัดลอก `split.json` เพราะมีรายชื่อโจทย์ validation และ test
- ไม่มีไฟล์ของ validation, test หรือตัวตรวจในโฟลเดอร์นี้ ผมใช้ grep หาชื่อโจทย์ `v1-`, `v2-`, `x1-` ถึง `x3-` และคำว่า `grader` แล้วไม่พบ
