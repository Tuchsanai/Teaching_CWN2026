# Benchmark Adaptor

### ขั้น 1 · Bash

```
cat /ba/setup/plugin_api.py /ba/setup/plugin_skeleton.py; ls -la /ba/setup /ba/reference; cat /data/split.json; find /data/baankafe | head -100
```

ผลที่ได้:

```
"""plugin_api.py : รูปแบบของ 1 โจทย์ ที่ plug-in ของ Benchmark Adaptor ต้องคืน

plug-in คือไฟล์ benchmark_plugin.py ที่มีฟังก์ชันเดียว

    def list_tasks(root) -> list[Task]        root = path ของ data root

กติกาของ plug-in
- อ่านได้เฉพาะไฟล์ใต้ root · ห้ามเขียนไฟล์ ห้ามเริ่ม process ห้ามใช้เครือข่าย ห้ามรันตัวตรวจ
- import ได้เฉพาะ json os pathlib re typing dataclasses collections itertools functools และ plugin_api
- การแบ่งชุด (split) ของโจทย์ทุกข้อเขียนไว้ในไฟล์ของ plug-in เอง และต้องตรงกับ split.json ของผู้ใช้
- id ของโจทย์ต้องไม่ซ้ำกัน และใช้เป็นชื่อโฟลเดอร์ได้ (ไม่มี / หรือ \\)
"""
from dataclasses import asdict, dataclass, field

SPLITS = ("train", "validation", "test")


@dataclass
class Task:
    id: str                                            # ชื่อโจทย์ ไม่ซ้ำกัน
    split: str                                         # "train" | "validation" | "test"
    instruction: str                                   # ข้อความโจทย์ที่ Solver ได้รับ
    inputs: list = field(default_factory=list)         # ไฟล์ตั้งต้นของโจทย์ (path เทียบกับ root)
    answer_files: list = field(default_factory=list)   # ไฟล์เฉลยของโจทย์ (path เทียบกับ root)
    grading: dict = field(default_factory
…(ตัด 3550 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; for f in tasks/*.json; do echo "== $f"; cat $f; echo; done; head -80 /ba/setup/benchmark_grader.py; grep -n "grading\|key" /ba/setup/benchmark_grader.py | head -40
```

ผลที่ได้:

```
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
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}
== tasks/t3-shipping-fee.json
{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `d
…(ตัด 6376 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /data/baankafe/answers; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do for f in $t/*; do echo "== $f"; cat $f; done; done; sed -n 300,340p /ba/setup/benchmark_grader.py
```

ผลที่ได้:

```
== t1-cafe-bill/solve.py
"""คิดเงินหน้าร้าน · เฉลยอ้างอิงตามมาตรฐานคิดเงินของร้าน BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool และ float ไม่ใช่ int
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value

def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    subtotal = 0
    for item in items:
        if type(item) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        subtotal += need_int(item.get("price"), "price", 0) * need_int(item.get("qty"), "qty", 1)
    amount = Fraction(subtotal)
    if subtotal >= 50000:
        amount *= Fraction(95, 100)
    if memb
…(ตัด 13673 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py : BaanKafe (โจทย์คิดเงินของร้านกาแฟ 9 ข้อ)"""
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
    for task_id, split in SPLIT.items():
        with open(os.path.join(root, "tasks", task_id + ".json"), encoding="utf-8") as f:
            data = json.load(f)
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=data["brief"],
            inputs=[],
            answer_files=["answers/%s/solve.py" % task_id,
                          "answers/%s/test_solve.py" % task_id],
            grading={"key": task_id, "function": data["function"]},
            category="",
        ))
    return tasks
EOF
mkdir -p /ba/reference/tasks /ba/reference/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/tasks/; cp -r answers/$t /ba/reference/answers/; done
cat > /ba/reference/README.md <<'EOF'
# BaanKafe (ข้อมูลอ้างอิงสำหรับ Evolver)

โจทย์เขียนโค้ดคิดเงินของร้านกาแฟ BaanKafe: Solver ได้ข้อความโจทย์ (`brief`) แล้วเขียนฟังก์ชัน Python 1 ฟังก์ชัน
ลงในไฟล์ `solve.py` ในโฟลเดอร์ทำงานที่ว่างเปล่า

ในโฟลเดอร์นี้มีเฉพาะโจทย์ชุด train 4 ข้อ:
- `tasks/<task id>.json` : `id`, `function` (ชื่อฟังก์ชัน), `brief` (ข้อความโจทย์ที่ Solver ได้รับ)
- `answers/<task id>/` : เฉลยอ้างอิง `solve.py` และ `test_solve.py`
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'/ba/setup')
import benchmark_plugin as b, collections
t=b.list_tasks('/data/baankafe')
print(collections.Counter(x.split for x in t), len({x.id for x in t}), all(x.instruction.strip() for x in t))
import json; s=json.load(open('/data/split.json'))
print(all(b.SPLIT[i]==k for k,v in s.items() for i in v), len(b.SPLIT))
"
ls /ba/setup; find /ba/reference -type f
grep -rIl -e v1-parking -e v2-net -e x1-late -e x2-refund -e x3-bulk -e parking_fee -e net_pay -e late_fee -e bulk_price /ba/reference; echo grep-done; find /ba/setup -name __pycache__ -exec rm -rf {} +; ls /ba/setup
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
True 9
__pycache__
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
/ba/reference/README.md
/ba/reference/tasks/t3-shipping-fee.json
/ba/reference/tasks/t4-cashback.json
/ba/reference/tasks/t1-cafe-bill.json
/ba/reference/tasks/t2-split-bill.json
/ba/reference/answers/t4-cashback/test_solve.py
/ba/reference/answers/t4-cashback/solve.py
/ba/reference/answers/t1-cafe-bill/test_solve.py
/ba/reference/answers/t1-cafe-bill/solve.py
/ba/reference/answers/t2-split-bill/test_solve.py
/ba/reference/answers/t2-split-bill/solve.py
/ba/reference/answers/t3-shipping-fee/test_solve.py
/ba/reference/answers/t3-shipping-fee/solve.py
grep-done
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
Shell cwd was reset to /ba/work
```

**Agent พูด:** เตรียม plug-in และโฟลเดอร์ reference เสร็จแล้ว และตรวจผ่านทั้งสองเรื่องที่โปรแกรมจะตรวจซ้ำ

**จำนวนโจทย์ต่อชุด**
- train 4 ข้อ, validation 2 ข้อ, test 3 ข้อ รวม 9 ข้อ ตรงกับ `/data/split.json` ทุกข้อ
- id ไม่ซ้ำ และ `instruction` ของทุกข้อไม่ว่าง
- ค้นใน `/ba/reference/` ด้วย id และชื่อฟังก์ชันของ validation กับ test ทุกข้อ ไม่พบ
- ลบ `__pycache__` ที่เกิดตอนทดลองใน `/ba/setup/` แล้ว

**Plug-in (`/ba/setup/benchmark_plugin.py`)**
- การแบ่งชุดเขียนไว้ในไฟล์เอง
- `instruction` อ่านมาจาก `brief` ใน `tasks/<id>.json`
- `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `test_solve.py`
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}`
- ตัวตรวจเลือกชุดกรณีทดสอบจาก `id` หรือ `grading["key"]` ซึ่งตรงกับค่าที่ใส่ไว้
- ไม่ได้แก้ตัวตรวจ

**สิ่งที่ใส่ใน `/ba/reference/`**
- `tasks/<id>.json` ของโจทย์ train 4 ข้อ
- `answers/<id>/solve.py` และ `test_solve.py` ของ train 4 ข้อ
- `README.md` สั้น ๆ ที่อธิบายรูปแบบโจทย์ โดยพูดถึงเฉพาะ train

**สิ่งที่ตั้งใจไม่ใส่**
- ทุกอย่างของ validation และ test เพราะเป็นข้อมูลที่ต้องกันไม่ให้ Evolver เห็น
- `split.json` เพราะรวมรายชื่อโจทย์ของ validation และ test ไว้
- `benchmark_grader.py` และคำอธิบายว่าตัวตรวจตรวจอะไรหรือให้คะแนนอย่างไร

เฉลย train ของ `t3-shipping-fee` และ `t4-cashback` มีคอมเมนต์เรื่องนโยบายธุรกิจ (S1, S2, C1, C2) อยู่ในโค้ด ผมคัดลอกไว้ตามเดิม เพราะคำสั่งผู้ใช้ให้ Evolver เห็นเฉลย train ได้ และคอมเมนต์เหล่านั้นอยู่ในเฉลย ไม่ใช่ในตัวตรวจ
