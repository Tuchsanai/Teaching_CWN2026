# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; find /data -type f | head -100; cat /data/split.json
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
…(ตัด 23161 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe/tasks; for f in *.json; do echo "== $f"; cat $f; echo; done; ls -la /ba /ba/reference 2>&1
```

ผลที่ได้:

```
== t1-cafe-bill.json
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
== t2-split-bill.json
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}
== t3-shipping-fee.json
{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะ
…(ตัด 3800 ตัวอักษร)
```

### ขั้น 3 · Bash

```
ls -laR /ba/data | head; cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe: 9 โจทย์เขียนฟังก์ชันคิดเงิน (train 4 · validation 2 · test 3)"""
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
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[],  # เฉลยใน answers/ ไม่ถูกใส่ไว้ เพราะตัวตรวจไม่ใช้ และห้ามให้ Evolver เห็น
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
mkdir -p /ba/reference/tasks && cp /data/baankafe/tasks/t[1-4]-*.json /ba/reference/tasks/
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.grading,len(t.instruction))
"; find /ba/reference -type f; grep -rl -e v1- -e x1- -e answers /ba/reference
```

ผลที่ได้:

```
/ba/data:
total 16
drwxr-xr-x 3 root root 4096 Nov 15 04:05 .
drwxr-xr-x 6 root root 4096 Nov 15 04:05 ..
drwxr-xr-x 4 root root 4096 Nov 13 08:46 baankafe
-rw-r--r-- 1 root root  213 Nov 15 04:05 split.json

/ba/data/baankafe:
total 16
drwxr-xr-x  4 root root 4096 Nov 13 08:46 .
t1-cafe-bill train {'key': 't1-cafe-bill', 'function': 'cafe_bill'} 329
t2-split-bill train {'key': 't2-split-bill', 'function': 'split_bill'} 405
t3-shipping-fee train {'key': 't3-shipping-fee', 'function': 'shipping_fee'} 485
t4-cashback train {'key': 't4-cashback', 'function': 'cashback'} 417
v1-parking-fee validation {'key': 'v1-parking-fee', 'function': 'parking_fee'} 408
v2-net-pay validation {'key': 'v2-net-pay', 'function': 'net_pay'} 458
x1-late-fee test {'key': 'x1-late-fee', 'function': 'late_fee'} 405
x2-refund test {'key': 'x2-refund', 'function': 'refund'} 429
x3-bulk-price test {'key': 'x3-bulk-price', 'function': 'bulk_price'} 391
/ba/reference/tasks/t3-shipping-fee.json
/ba/reference/tasks/t4-cashback.json
/ba/reference/tasks/t1-cafe-bill.json
/ba/reference/tasks/t2-split-bill.json
```

### ขั้น 4 · Bash

```
grep -rnoE -e 'v1-|x1-|answers' /ba/reference | head
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** `/ba/setup/benchmark_plugin.py` และ `/ba/reference/` เสร็จแล้ว ผมรัน `list_tasks('/data/baankafe')` แล้วได้ 9 โจทย์ แบ่งเป็น train 4 · validation 2 · test 3 ตรงกับ `/data/split.json` ผมไม่ได้รันตัวตรวจ เพราะ loop เป็นผู้รัน

- **`benchmark_plugin.py`:** ตาราง `SPLIT` ฝังอยู่ในไฟล์ และอ่านโจทย์จาก `root/tasks/<id>.json` เท่านั้น แต่ละ `Task` ใช้ `brief` เป็น `instruction` และตั้ง `grading = {"key": <id>, "function": <ชื่อฟังก์ชัน>}` ซึ่งตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ `inputs` ว่างเพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- **`answer_files` เว้นว่าง:** ตัวตรวจไม่ใช้เฉลย และคุณสั่งไม่ให้ Evolver เห็น `answers/` ของโจทย์ใดเลย ผมจึงไม่ใส่ path ของเฉลยลงใน `Task`
- **`/ba/reference/`:** มี `tasks/t1-cafe-bill.json`, `t2-split-bill.json`, `t3-shipping-fee.json` และ `t4-cashback.json` ซึ่งเป็นข้อความโจทย์ของชุด train ที่คัดลอกมาตามโครงเดิม

ผมไม่ได้คัดลอก 3 อย่างนี้เข้า reference:
- โจทย์ validation และ test
- `answers/` ทั้งหมด
- `benchmark_grader.py`

ผมไม่ได้คัดลอก `/data/split.json` เพราะมีชื่อโจทย์ validation และ test ผมค้นใน `/ba/reference/` แล้วไม่พบชื่อโจทย์ validation, test หรือคำว่า `answers`
