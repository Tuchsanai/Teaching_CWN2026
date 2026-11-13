# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; cat /data/split.json; find /data/baankafe | head -100
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 09:31 .
drwxr-xr-x 6 root root  4096 Nov 13 09:31 ..
-rwxr-xr-x 1 root root 20223 Nov 13 09:31 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 09:31 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 09:31 plugin_skeleton.py
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
…(ตัด 20946 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe/tasks; for f in *.json; do echo "== $f"; python3 -c "import json,sys;d=json.load(open('$f'));print(d['id'],d['function']);print(d['brief'][:300])"; done; ls -la /data /ba /ba/reference
```

ผลที่ได้:

```
== t1-cafe-bill.json
t1-cafe-bill cafe_bill
ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน
- `items` = list ของ dict `{"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (ตั้งแต่ 1)}`
- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%
- `member` = True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คืนยอดที่ลูกค้
== t2-split-bill.json
t2-split-bill split_bill
ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล
- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)
- ยอดที่ต้องหาร = ยอดบิลบวกทิป
- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้ค
== t3-shipping-fee.json
t3-shipping-fee shipping_fee
ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ
- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน
- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กร
== t4-cashback.json
t4-cashback cashback
ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก
- 
…(ตัด 2544 ตัวอักษร)
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
    for tid, split in SPLIT.items():
        path = os.path.join(root, "tasks", tid + ".json")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        answer_files = []
        adir = os.path.join(root, "answers", tid)
        if os.path.isdir(adir):
            answer_files = ["answers/%s/%s" % (tid, n) for n in sorted(os.listdir(adir))
                            if os.path.isfile(os.path.join(adir, n))]
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
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/baankafe/tasks/; cp -r answers/$t /ba/reference/baankafe/answers/; done
find /ba/reference -type f
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'/ba/setup')
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files,t.grading)
"
grep -rl -i -E "x1-|x2-|x3-|v1-|v2-|parking|net_pay|late_fee|refund|bulk" /ba/reference || echo clean
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

**Agent พูด:** ผมเขียน `benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ทดสอบ plug-in กับ `/data/baankafe` แล้ว ได้โจทย์ครบ 9 ข้อ แบ่งเป็น train 4, validation 2 และ test 3 ตรงกับ `/data/split.json` ผมไม่ได้รันตัวตรวจ

**`/ba/setup/benchmark_plugin.py`**
- `list_tasks(root)` อ่าน `tasks/<id>.json` ใต้ `root` และสร้าง `Task` ให้ทั้ง 9 ข้อ
- การแบ่งชุดเขียนไว้ใน dict `SPLIT` ในไฟล์เอง
- `instruction` ใช้ข้อความ `brief`
- `answer_files` เป็น `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py`
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ซึ่งตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ
- `inputs` เป็นลิสต์ว่าง เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น

**`/ba/reference/baankafe/`**
- ตามที่ผู้ใช้จำกัดไว้ ผมคัดลอกเฉพาะ `brief` ของโจทย์ train ทั้ง 4 ข้อ (`tasks/`) กับเฉลยของข้อเหล่านั้น (`answers/`) โดยคงโครงโฟลเดอร์เดิม
- ไม่มีอะไรของ validation หรือ test อยู่ในโฟลเดอร์นี้ ผมไม่ได้คัดลอก `split.json` เพราะไฟล์นั้นระบุชื่อโจทย์ของสองชุดนั้น
- ไม่มีโค้ดหรือคำอธิบายของตัวตรวจในโฟลเดอร์นี้ และผม grep หาชื่อ validation/test แล้วไม่พบ
