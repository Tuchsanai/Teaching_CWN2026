# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; cat /data/split.json; find /data/baankafe | head -100
```

ผลที่ได้:

```
total 40
drwxr-xr-x 2 root root  4096 Nov 15 04:15 .
drwxr-xr-x 6 root root  4096 Nov 15 04:15 ..
-rwxr-xr-x 1 root root 24093 Nov 15 04:15 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 15 04:15 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 15 04:15 plugin_skeleton.py
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
cd /data/baankafe/tasks; for f in t*.json; do cat $f; echo; done; head -c 600 v1-parking-fee.json; ls -la /ba /ba/reference; ls /data
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}
{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน\n- ไม่เกิน 1,000 กรัม
…(ตัด 1513 ตัวอักษร)
```

### ขั้น 3 · Bash

```
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/baankafe/tasks/; cp -r answers/$t /ba/reference/baankafe/answers/; done
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
        ans = []
        for name in ("solve.py", "test_solve.py"):
            rel = "answers/%s/%s" % (tid, name)
            if os.path.isfile(os.path.join(root, rel)):
                ans.append(rel)
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=ans,
            grading={"key": d["id"], "function": d["function"]},
            category="billing",
        ))
    return tasks
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files,t.grading)
"; find /ba/reference -type f; grep -rl "parking\|net-pay\|late-fee\|refund\|bulk" /ba/reference
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
…(ตัด 707 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -rnoi "parking\|net-pay\|late-fee\|refund\|bulk" /ba/reference | head
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน `benchmark_plugin.py` และเติม `/ba/reference/` แล้ว ทดสอบ plug-in กับ `/data/baankafe` แล้ว `list_tasks` คืนโจทย์ครบ 9 ข้อ แบ่งเป็น train 4, validation 2 และ test 3 ตรงกับ `/data/split.json` ผมไม่ได้รันตัวตรวจ

**`/ba/setup/benchmark_plugin.py`**
- ตาราง `SPLIT` อยู่ในไฟล์เอง
- อ่านเฉพาะ `tasks/<id>.json` ใต้ `root`
- `instruction` คือ `brief`
- `answer_files` คือ `answers/<id>/solve.py` และ `answers/<id>/test_solve.py`
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ
- `inputs` ว่าง เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- import เฉพาะ standard library กับ `plugin_api`

**`/ba/reference/baankafe/`**
- มี `tasks/<id>.json` และ `answers/<id>/` (`solve.py`, `test_solve.py`) ของโจทย์ train 4 ข้อ คือ `t1-cafe-bill`, `t2-split-bill`, `t3-shipping-fee`, `t4-cashback`
- โครงโฟลเดอร์เหมือนเดิม
- ไม่ได้คัดลอกโจทย์ validation, โจทย์ test, เฉลยของสองชุดนั้น, `split.json` และ `benchmark_grader.py` เพราะ `split.json` บอกว่าข้อไหนอยู่ชุดไหน
- ค้นข้อความใน `/ba/reference` แล้วไม่พบชื่อโจทย์ validation หรือ test

ไฟล์ `answer_files` ของ validation และ test ถูกระบุไว้ใน plug-in ด้วย ผมสมมติว่า loop ไม่ส่งไฟล์เหล่านี้ให้ Evolver เพราะ Evolver เห็นเฉพาะ `/ba/reference/`
