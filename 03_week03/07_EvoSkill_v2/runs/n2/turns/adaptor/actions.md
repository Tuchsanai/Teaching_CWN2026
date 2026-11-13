# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; cat /data/split.json; find /data -type f | head -100
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 10:20 .
drwxr-xr-x 6 root root  4096 Nov 13 10:20 ..
-rwxr-xr-x 1 root root 20223 Nov 13 10:20 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 10:20 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 10:20 plugin_skeleton.py
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
…(ตัด 20585 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; python3 -c "
import json,glob
for f in sorted(glob.glob('tasks/*.json')):
    d=json.load(open(f)); print(f, list(d), d['id'], d['function'])
"; ls -la /ba /ba/reference; cat answers/t1-cafe-bill/solve.py | head -40; grep -il "grader\|hidden\|oracle" answers/t*/* tasks/t*
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
tasks/t1-cafe-bill.json ['id', 'function', 'brief'] t1-cafe-bill cafe_bill
tasks/t2-split-bill.json ['id', 'function', 'brief'] t2-split-bill split_bill
tasks/t3-shipping-fee.json ['id', 'function', 'brief'] t3-shipping-fee shipping_fee
tasks/t4-cashback.json ['id', 'function', 'brief'] t4-cashback cashback
tasks/v1-parking-fee.json ['id', 'function', 'brief'] v1-parking-fee parking_fee
tasks/v2-net-pay.json ['id', 'function', 'brief'] v2-net-pay net_pay
tasks/x1-late-fee.json ['id', 'function', 'brief'] x1-late-fee late_fee
tasks/x2-refund.json ['id', 'function', 'brief'] x2-refund refund
tasks/x3-bulk-price.json ['id', 'function', 'brief'] x3-bulk-price bulk_price
/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 13 10:20 .
drwxr-xr-x 1 root root 4096 Nov 13 08:52 ..
drwxr-xr-x 3 root ro
…(ตัด 1543 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /ba/setup && cat > benchmark_plugin.py <<'EOF'
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
find . -type f | sort; find answers -name __pycache__
cd /ba/setup && python3 -c "
import plugin_benchmark" 2>/dev/null; python3 -c "
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.grading,t.answer_files,len(t.instruction))
"; rm -rf /ba/setup/__pycache__
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
t1-cafe-bill train {'key': 't1-cafe-bill', 'function': 'cafe_bill'} ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] 329
t2-split-bill train {'key': 't2-split-bill', 'function': 'split_bill'} ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] 405
t3-shipping-fee train {'key': 't3-shipping-fee', 'function': 'shipping_fee'} ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] 485
t4-cashback train {'key': 't4-cashback', 'function': 'cashback'} ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] 417
v1-parking-fee validation {'key': 'v1-parking-fee', 'function': 'parking_fee'} ['answers/v1-parking-fee/solve.py', 'answers/v1-parking-fee/test_solve.py'] 408
v2-net-pay validation {'key': 'v2-net-pay', 'func
…(ตัด 535 ตัวอักษร)
```

**Agent พูด:** เขียน plug-in กับโฟลเดอร์ reference เสร็จแล้ว และทดสอบ `list_tasks('/data/baankafe')` แล้ว คืน `Task` ครบ 9 ข้อ แบ่งเป็น train 4, validation 2, test 3 ตรงกับ `/data/split.json` ผมไม่ได้รันตัวตรวจ

**`/ba/setup/benchmark_plugin.py`**
- อ่าน `tasks/<id>.json` ใต้ root แล้วเติม `instruction` จาก `brief` และตั้ง `category="coding"`
- ตั้ง `answer_files` เป็น `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py`
- ตั้ง `grading={"key": id, "function": ...}` ตัวตรวจอ่าน `key` เพื่อเลือกชุดกรณีทดสอบ
- ตาราง `SPLIT` เขียนไว้ในไฟล์เอง ใช้เฉพาะ standard library กับ `plugin_api`

**`/ba/reference/`**
- `README.md` มีข้อความที่คุณกำหนดข้อความเดียว
- `tasks/` มีไฟล์โจทย์ของ train ทั้ง 4 ข้อ
- `answers/` มีเฉลยของ train ทั้ง 4 ข้อ (`solve.py` กับ `test_solve.py`) โครงโฟลเดอร์เหมือนเดิม
- ไม่ได้ใส่โจทย์หรือเฉลยของ validation กับ test ไม่ได้ใส่ตัวตรวจ และไม่ได้คัดลอก `split.json` เพราะไฟล์นั้นระบุชื่อโจทย์ validation กับ test
