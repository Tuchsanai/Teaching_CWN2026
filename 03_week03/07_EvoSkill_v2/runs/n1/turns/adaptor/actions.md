# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; find /data -maxdepth 3 | head -80; cat /data/split.json
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 09:12 .
drwxr-xr-x 6 root root  4096 Nov 13 09:12 ..
-rwxr-xr-x 1 root root 20223 Nov 13 09:12 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 09:12 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 09:12 plugin_skeleton.py
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
…(ตัด 20120 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; ls answers/*; grep -il "v1-\|v2-\|x1-\|x2-\|x3-\|parking\|net_pay\|late_fee\|refund\|bulk" tasks/t*.json answers/t*/*; ls /ba /ba/reference 2>&1
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
answers/t1-cafe-bill:
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
data
reference
setup
work

/ba/reference:
Shell cwd was reset to /ba/work
```

### ขั้น 3 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - โจทย์คิดเงินของร้านกาแฟ BaanKafe (9 ข้อ)"""
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
            grading={"key": tid, "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
cd /ba/reference && mkdir -p tasks answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json tasks/; cp -r /data/baankafe/answers/$t answers/; done
printf '%s\n' 'โฟลเดอร์ `answers/<task id>/` คือผลงานของโจทย์นั้นที่ได้คะแนนเต็ม ประกอบด้วย 2 ไฟล์ คือ `solve.py` และ `test_solve.py`' > README.md
find . -type f | sort
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
ts=b.list_tasks('/data/baankafe')
for t in ts: print(t.id,t.split,t.answer_files,t.grading)
import os
assert all(os.path.isfile(os.path.join('/data/baankafe',p)) for t in ts for p in t.answer_files)
"
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
t1-cafe-bill train ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] {'key': 't1-cafe-bill', 'function': 'cafe_bill'}
t2-split-bill train ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] {'key': 't2-split-bill', 'function': 'split_bill'}
t3-shipping-fee train ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] {'key': 't3-shipping-fee', 'function': 'shipping_fee'}
t4-cashback train ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] {'key': 't4-cashback', 'function': 'cashback'}
v1-parking-fee validation ['answers/v1-parking-fee/solve.py', 'answers/v1-parking-fee/test_solve.py'] {'key': 'v1-parking-fee', 'function': 'parking_fee'}
v2-net-pay validation ['answers/v2-net-pay/solve.py', 'answers/v2-net
…(ตัด 499 ตัวอักษร)
```

**Agent พูด:** ผมเขียน `benchmark_plugin.py` เสร็จแล้ว และเติมโฟลเดอร์ `/ba/reference/` ให้ Evolver แล้ว ผมรัน `list_tasks('/data/baankafe')` ทดสอบแล้ว ได้โจทย์ครบ 9 ข้อ และไฟล์เฉลยทุก path มีอยู่จริง ผมไม่ได้รันตัวตรวจ ตามที่คำสั่งกำหนด

**`/ba/setup/benchmark_plugin.py`**
- `list_tasks(root)` อ่าน `tasks/<id>.json` ใต้ `root` แล้วคืน `Task` 1 ตัวต่อ 1 โจทย์
- การแบ่งชุดตรงกับ `/data/split.json` และเขียนไว้ในไฟล์ plug-in เอง:
  - train: t1-cafe-bill, t2-split-bill, t3-shipping-fee, t4-cashback
  - validation: v1-parking-fee, v2-net-pay
  - test: x1-late-fee, x2-refund, x3-bulk-price
- `instruction` คือ `brief` ของโจทย์ และ `inputs` ว่างเพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `answers/<id>/test_solve.py`
- `grading` เป็น `{"key": <task id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ

**`/ba/reference/`** มี 3 อย่างนี้ และคงโครงโฟลเดอร์เดิมไว้
- `README.md` มีข้อความที่กำหนดข้อความเดียว
- `tasks/<id>.json` ของโจทย์ train ทั้ง 4 ข้อ
- `answers/<id>/solve.py` และ `test_solve.py` ของโจทย์ train ทั้ง 4 ข้อ

ผมไม่ได้คัดลอกสิ่งต่อไปนี้ไปไว้ในโฟลเดอร์นี้
- โจทย์และเฉลยของชุด validation และ test
- `split.json` เพราะมีรายชื่อโจทย์ของ validation และ test
- โค้ดของตัวตรวจ

ผมค้นข้อความในไฟล์ train ที่คัดลอกไป ไม่พบชื่อโจทย์หรือคำที่เกี่ยวกับโจทย์ validation และ test
