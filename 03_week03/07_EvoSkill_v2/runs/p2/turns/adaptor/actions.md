# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; cat /data/split.json; find /data/baankafe | head -100
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 10:28 .
drwxr-xr-x 6 root root  4096 Nov 13 10:28 ..
-rwxr-xr-x 1 root root 20223 Nov 13 10:28 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 10:28 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 10:28 plugin_skeleton.py
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
…(ตัด 20951 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe/tasks; for f in *.json; do echo "== $f"; cat $f; echo; done; ls -la /data /ba /ba/reference 2>&1
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
…(ตัด 4006 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe billing-function benchmark (9 tasks)

Reads tasks/<id>.json under the data root. Split is hard-coded below (from the given split.json).
"""
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
            answer_files=[
                "answers/%s/solve.py" % tid,
                "answers/%s/test_solve.py" % tid,
            ],
            grading={"key": d["id"], "function": d["function"]},
            category="billing",
        ))
    return tasks
EOF
mkdir -p /ba/reference/baankafe/tasks
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json /ba/reference/baankafe/tasks/; done
cat > /ba/reference/README.md <<'EOF'
# BaanKafe benchmark (training material)

Each task asks the Solver to write one Python function in `solve.py` from a Thai-language brief.
`baankafe/tasks/<task id>.json` holds `id`, `function` (name of the function to write) and `brief`
(the task text the Solver receives). Only the training tasks are included here.
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b, collections
t=b.list_tasks('/data/baankafe'); print(len(t), collections.Counter(x.split for x in t)); print(t[0].to_dict())
import os; print(all(os.path.isfile('/data/baankafe/'+p) for x in t for p in x.answer_files))"
find /ba/reference -type f; grep -rl "answers\|x1-\|v1-" /ba/reference
```

ผลที่ได้:

```
9 Counter({'train': 4, 'test': 3, 'validation': 2})
{'id': 't1-cafe-bill', 'split': 'train', 'instruction': 'ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์', 'inputs': [], 'answer_files': ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'], 'grading': {'key': 't1-cafe-bill', 'function': 'cafe_bill'}, 'category': 'billing'}
True
/ba/reference/README.md
/ba/reference/baankafe/tasks/t3-shipping-fee.json
/ba/reference/baankafe/tasks/t4-cashback.json
/ba/reference/baankafe/tasks/t1-cafe-bill.json
/ba/reference/baankafe/tasks/t2-split-bill.json
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ทดสอบ plug-in กับ `/data/baankafe` แล้ว `list_tasks` คืน 9 โจทย์ แบ่งเป็น train 4, validation 2 และ test 3 ตรงกับ `split.json` ไฟล์เฉลยที่ `answer_files` ชี้ไว้มีอยู่จริงทุกไฟล์ ผมไม่ได้รันตัวตรวจ

**`benchmark_plugin.py`**
- ตารางแบ่งชุดฝังอยู่ในไฟล์เอง
- `list_tasks(root)` อ่านเฉพาะ `root/tasks/<id>.json` โดยใช้ `brief` เป็น `instruction`
- `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `answers/<id>/test_solve.py`
- `grading` มี `key` (ค่าเดียวกับ id ซึ่งตัวตรวจใช้เลือกชุดกรณีทดสอบ) กับ `function`
- ไม่มี `inputs` เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- import เฉพาะ standard library กับ `plugin_api`

**`/ba/reference/`**
- `baankafe/tasks/` มีไฟล์ JSON ของโจทย์ train 4 ข้อ ได้แก่ t1-cafe-bill, t2-split-bill, t3-shipping-fee และ t4-cashback
- `README.md` อธิบายรูปแบบโจทย์สั้น ๆ
- ผมไม่ได้ใส่ `answers/` เลย แม้แต่ของ train ตามข้อ 4 ของคำสั่ง
- ไม่ได้ใส่โจทย์ validation กับ test และไม่ได้ใส่ `split.json` เพราะไฟล์นั้นมีชื่อโจทย์ของสองชุดนี้
- ไม่ได้ใส่ตัวตรวจ ผมตรวจแล้วว่าไม่มีคำว่า answers หรือ id ของ validation และ test ในโฟลเดอร์นี้
