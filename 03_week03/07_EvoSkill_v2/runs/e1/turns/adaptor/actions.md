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
cd /data/baankafe; ls answers/*; for f in tasks/t*.json; do echo "== $f"; cat $f; echo; done; head -c 600 tasks/x1-late-fee.json; ls /ba /ba/reference
```

ผลที่ได้:

```
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
== tasks/t1-cafe-bill.json
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
== tasks/t2-split-bill.json
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป
…(ตัด 1649 ตัวอักษร)
```

### ขั้น 3 · Bash

```
mkdir -p /ba/setup /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe billing-function benchmark (9 tasks)."""
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
        answer_files = [
            os.path.join("answers", tid, n)
            for n in ("solve.py", "test_solve.py")
            if os.path.isfile(os.path.join(ans_dir, n))
        ]
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=answer_files,
            grading={"key": d["id"], "function": d["function"]},
            category="billing",
        ))
    return tasks
EOF
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/baankafe/tasks/; cp -r answers/$t /ba/reference/baankafe/answers/; done
find /ba/reference -type f
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files,t.grading)
"
grep -rl "x1\|x2\|x3\|v1-\|v2-\|late\|refund\|parking" /ba/reference || echo clean
```

ผลที่ได้:

```
/ba/reference/baankafe/tasks/t3-shipping-fee.json
/ba/reference/baankafe/tasks/t4-cashback.json
/ba/reference/baankafe/tasks/t1-cafe-bill.json
/ba/reference/baankafe/tasks/t2-split-bill.json
/ba/reference/baankafe/answers/t4-cashback/test_solve.py
/ba/reference/baankafe/answers/t4-cashback/solve.py
/ba/reference/baankafe/answers/t1-cafe-bill/test_solve.py
/ba/reference/baankafe/answers/t1-cafe-bill/solve.py
/ba/reference/baankafe/answers/t2-split-bill/test_solve.py
/ba/reference/baankafe/answers/t2-split-bill/solve.py
/ba/reference/baankafe/answers/t3-shipping-fee/test_solve.py
/ba/reference/baankafe/answers/t3-shipping-fee/solve.py
t1-cafe-bill train ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] {'key': 't1-cafe-bill', 'function': 'cafe_bill'}
t2-split-bill train ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] {'key': 't2-split-bill', 'function': 'split_bill'}
t3-shipping-fee train ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] {'key': 't3-shipping-fee', 'function': 'shipping_fee'}
t4-cashback train ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] {'key': 't4-cashback', 'functio
…(ตัด 745 ตัวอักษร)
```

**Agent พูด:** ผมเขียน `benchmark_plugin.py` และเติม `/ba/reference/` แล้ว ทดสอบ plug-in กับ `/data/baankafe` ด้วย `python3 -I` ได้ผลดี แต่ยังไม่ได้รันตัวตรวจ

**`/ba/setup/benchmark_plugin.py`**
- `list_tasks(root)` คืน `Task` 9 ตัว อ่านเฉพาะ `root/tasks/<id>.json` และ `root/answers/<id>/` ใช้ import จาก standard library กับ `plugin_api` เท่านั้น
- การแบ่งชุดตรงกับ `/data/split.json` และฝังไว้ในไฟล์ plug-in:
  - train: t1-cafe-bill, t2-split-bill, t3-shipping-fee, t4-cashback
  - validation: v1-parking-fee, v2-net-pay
  - test: x1-late-fee, x2-refund, x3-bulk-price
- แต่ละ `Task` มีค่าดังนี้:
  - `instruction` = `brief`
  - `inputs` ว่าง
  - `answer_files` = `answers/<id>/solve.py` กับ `test_solve.py`
  - `grading` = `{"key": id, "function": ...}` ซึ่งตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ
  - `category` = `"billing"`

**`/ba/reference/`**
- คัดลอกเฉพาะโจทย์ train 4 ข้อ ได้แก่ `baankafe/tasks/<id>.json` และ `baankafe/answers/<id>/{solve.py,test_solve.py}` โดยคงโครงโฟลเดอร์เดิม
- ไม่ได้ใส่ `split.json` เพราะมีรายชื่อโจทย์ validation กับ test
- ไม่ได้ใส่ตัวตรวจหรือคำอธิบายของตัวตรวจ
- ค้นหา id และคำสำคัญของโจทย์ validation กับ test ในโฟลเดอร์นี้แล้ว ไม่พบ
