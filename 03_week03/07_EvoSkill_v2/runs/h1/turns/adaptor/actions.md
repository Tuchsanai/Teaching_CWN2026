# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; cat /data/split.json; find /data -type f | head -100; ls /ba/reference
```

ผลที่ได้:

```
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
    answer_files: list = field(default_factory=list)  # ไฟล์เฉลยของโจทย์ (path เทียบกับ root)
    grading: dict = field(default_factory=dict)       # ค่าที่ตัวตรวจของผู้ใช้อ่าน
    category: str = ""

    def to_dict(self):
        return asdict(self)
"""benchmark_plugin.py (โครงเปล่า) - Benchmark Adaptor เติมไฟล์นี้ แล้วบันทึกเป็น benchmark_
…(ตัด 22883 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cat tasks/$t.json; echo; done; head -c 600 tasks/v1-parking-fee.json; grep -il "v1-\|v2-\|x1-\|x2-\|x3-\|parking\|net_pay\|late_fee\|refund\|bulk" answers/t*/* tasks/t*
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
…(ตัด 1060 ตัวอักษร)
```

### ขั้น 3 · Bash

```
mkdir -p /ba/setup /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/baankafe/tasks/; cp -r answers/$t /ba/reference/baankafe/answers/; done
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe (โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ)"""
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
            answer_files=[
                os.path.join("answers", tid, "solve.py"),
                os.path.join("answers", tid, "test_solve.py"),
            ],
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
cd /ba/setup && python3 -c "
import benchmark_plugin as b,os
for t in b.list_tasks('/data/baankafe'):
    assert all(os.path.isfile(os.path.join('/data/baankafe',p)) for p in t.answer_files)
    print(t.id,t.split,t.grading)
"; find /ba/reference -type f; grep -rl "parking\|net_pay\|late_fee\|refund\|bulk" /ba/reference
```

ผลที่ได้:

```
t1-cafe-bill train {'key': 't1-cafe-bill', 'function': 'cafe_bill'}
t2-split-bill train {'key': 't2-split-bill', 'function': 'split_bill'}
t3-shipping-fee train {'key': 't3-shipping-fee', 'function': 'shipping_fee'}
t4-cashback train {'key': 't4-cashback', 'function': 'cashback'}
v1-parking-fee validation {'key': 'v1-parking-fee', 'function': 'parking_fee'}
v2-net-pay validation {'key': 'v2-net-pay', 'function': 'net_pay'}
x1-late-fee test {'key': 'x1-late-fee', 'function': 'late_fee'}
x2-refund test {'key': 'x2-refund', 'function': 'refund'}
x3-bulk-price test {'key': 'x3-bulk-price', 'function': 'bulk_price'}
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
/ba/reference/baankafe/answers/t3-shipping-fee/test_solve
…(ตัด 59 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -rno "parking\|net_pay\|late_fee\|refund\|bulk" /ba/reference | head
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ส่วนตัวตรวจ `benchmark_grader.py` ผมไม่ได้รัน

ผมทดสอบ `list_tasks('/data/baankafe')` แล้ว คืนครบ 9 โจทย์ตามการแบ่งที่ให้มา และไฟล์เฉลยของทุกโจทย์มีอยู่จริง

- **การแบ่งชุด:** plug-in ฝังการแบ่งไว้ในไฟล์เอง ตรงกับ `/data/split.json` คือ train 4 ข้อ (t1–t4), validation 2 ข้อ (v1, v2) และ test 3 ข้อ (x1–x3)
- **ค่าของแต่ละ `Task`:** `instruction` มาจาก `brief` ส่วน `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `test_solve.py` ทั้งหมดเป็น path เทียบกับ `root` ค่า `grading` เป็น `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ซึ่งตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ ส่วน `inputs` ว่างเพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น และ `category` ตั้งเป็น `coding`
- **`/ba/reference/`:** มีเฉพาะโจทย์ train 4 ข้อ ใต้ `baankafe/tasks/<id>.json` และ `baankafe/answers/<id>/{solve.py,test_solve.py}` โดยคงโครงโฟลเดอร์เดิม
- **ไม่ได้คัดลอก:** โจทย์และเฉลยของ validation กับ test, `split.json` (เพราะมีรายชื่อโจทย์ validation และ test) และโค้ดของตัวตรวจ ผมค้นในโฟลเดอร์ reference แล้วไม่พบคำที่เกี่ยวกับ validation หรือ test อยู่เลย
