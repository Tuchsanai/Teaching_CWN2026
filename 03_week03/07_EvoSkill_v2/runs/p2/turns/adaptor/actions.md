# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; find /data -type f | head -100; cat /data/split.json
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
    tdir = os.path.join(root, "baankafe", "tasks")
    for tid, split in SPLIT.items():
        with open(os.path.join(tdir, tid + ".json"), encoding="utf-8") as f:
            d = json.load(f)
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[
                os.path.join("baankafe", "answers", tid, "solve.py"),
                os.path.join("baankafe", "answers", tid, "test_solve.py"),
            ],
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
mkdir -p /ba/reference/baankafe/tasks
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json /ba/reference/baankafe/tasks/; done
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
for t in b.list_tasks('/data'): print(t.id,t.split,t.answer_files[0],len(t.instruction))
"; find /ba/reference -type f
```

ผลที่ได้:

```
t1-cafe-bill train baankafe/answers/t1-cafe-bill/solve.py 329
t2-split-bill train baankafe/answers/t2-split-bill/solve.py 405
t3-shipping-fee train baankafe/answers/t3-shipping-fee/solve.py 485
t4-cashback train baankafe/answers/t4-cashback/solve.py 417
v1-parking-fee validation baankafe/answers/v1-parking-fee/solve.py 408
v2-net-pay validation baankafe/answers/v2-net-pay/solve.py 458
x1-late-fee test baankafe/answers/x1-late-fee/solve.py 405
x2-refund test baankafe/answers/x2-refund/solve.py 429
x3-bulk-price test baankafe/answers/x3-bulk-price/solve.py 391
/ba/reference/baankafe/tasks/t3-shipping-fee.json
/ba/reference/baankafe/tasks/t4-cashback.json
/ba/reference/baankafe/tasks/t1-cafe-bill.json
/ba/reference/baankafe/tasks/t2-split-bill.json
Shell cwd was reset to /ba/work
```

**Agent พูด:** ผมใช้ path ของ root ผิด เพราะ data root คือ `/data/baankafe` ไม่ใช่ `/data` ผมจะแก้ให้ตรง

### ขั้น 4 · Bash

```
cd /ba/setup && sed -i 's|os.path.join(root, "baankafe", "tasks")|os.path.join(root, "tasks")|; s|os.path.join("baankafe", "answers"|os.path.join("answers"|' benchmark_plugin.py && python3 -I -c "
import sys,os; sys.path.insert(0,'.')
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'):
    assert all(os.path.isfile(os.path.join('/data/baankafe',p)) for p in t.answer_files)
    print(t.id,t.split,t.answer_files[0])
"; grep -rl "answers\|validation\|test" /ba/reference || echo clean
```

ผลที่ได้:

```
t1-cafe-bill train answers/t1-cafe-bill/solve.py
t2-split-bill train answers/t2-split-bill/solve.py
t3-shipping-fee train answers/t3-shipping-fee/solve.py
t4-cashback train answers/t4-cashback/solve.py
v1-parking-fee validation answers/v1-parking-fee/solve.py
v2-net-pay validation answers/v2-net-pay/solve.py
x1-late-fee test answers/x1-late-fee/solve.py
x2-refund test answers/x2-refund/solve.py
x3-bulk-price test answers/x3-bulk-price/solve.py
clean
Shell cwd was reset to /ba/work
```

**Agent พูด:** ผมเขียน plug-in เสร็จแล้ว และทดสอบกับ `/data/baankafe` ได้ครบ 9 โจทย์ โดยไฟล์เฉลยทุกไฟล์ที่ plug-in ระบุมีอยู่จริง ผมยังไม่ได้รันตัวตรวจ เพราะ loop เป็นผู้รัน

**`/ba/setup/benchmark_plugin.py`**
- `list_tasks(root)` อ่าน `tasks/<id>.json` ใต้ root ที่ได้รับ และคืน `Task` 9 ตัว
- การแบ่งชุดเป็นไปตาม `/data/split.json` และเขียนไว้ในไฟล์ plug-in เอง:
  - train: t1-cafe-bill, t2-split-bill, t3-shipping-fee, t4-cashback
  - validation: v1-parking-fee, v2-net-pay
  - test: x1-late-fee, x2-refund, x3-bulk-price
- แต่ละ `Task` มีค่าดังนี้:
  - `instruction` คือ `brief`
  - `inputs` เป็นรายการว่าง เพราะโจทย์ไม่มีไฟล์ตั้งต้น
  - `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `answers/<id>/test_solve.py`
  - `grading` เป็น `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ
- plug-in ใช้เฉพาะ standard library กับ `plugin_api` และไม่รัน process หรือใช้เครือข่าย

**`/ba/reference/`**
- ใส่เฉพาะ `baankafe/tasks/<id>.json` ของโจทย์ train 4 ข้อ ตามโครงโฟลเดอร์เดิม
- ไม่ใส่โจทย์ validation และ test ไม่ใส่ `answers/` ของโจทย์ใดเลย ไม่ใส่โค้ดตัวตรวจ และไม่ใส่ `split.json`
- `split.json` มีชื่อโจทย์ validation และ test จึงไม่ถูกคัดลอกเข้าไป
- ผมค้นในโฟลเดอร์นี้ด้วย grep หาคำว่า answers, validation และ test แล้วไม่พบ
