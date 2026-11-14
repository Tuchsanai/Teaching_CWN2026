# Benchmark Adaptor

### ขั้น 1 · Bash

```
cat /ba/setup/plugin_api.py /ba/setup/plugin_skeleton.py; ls -R /ba /data | head -100; cat /data/split.json
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
…(ตัด 2862 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; cat tasks/v1-parking-fee.json; echo; cat answers/t1-cafe-bill/*; grep -n "grading\|key\|\.get" /ba/setup/benchmark_grader.py | head -30; diff /data/split.json /ba/data/split.json && echo same
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
{
 "id": "v1-parking-fee",
 "function": "parking_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `parking_fee(minutes, member)` ในไฟล์ `solve.py` สำหรับคิดค่าจอดรถ\n- `minutes` = เวลาที่จอด 0–1,440 นาที · `member` = True คือสมาชิก\n- จอดไม่เกิน 30 นาที ไม่คิดเงิน\n- จอดเกิน 30 นาที คิดชั่วโมงละ 25 บาท นับจากเวลาที่จอดทั้งหมด เศษของชั่วโมงนับเป็น 1 ชั่วโมง\n- ค่าจอดก่อนส่วนลดและภาษี สูงสุด 250 บาท\n- สมาชิกลด 15%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนค่าจอด เป็นจำนวนเต็มสตางค์"
}
"""คิดเงินหน้าร้าน · เฉลยอ้างอิงตามมาตรฐานคิดเงินของร้าน BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is 
…(ตัด 4249 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py : BaanKafe (โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ)"""
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
        if data["id"] != task_id:
            raise ValueError("id ไม่ตรงกับชื่อไฟล์: %s" % task_id)
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=data["brief"],
            inputs=[],
            answer_files=["answers/%s/solve.py" % task_id, "answers/%s/test_solve.py" % task_id],
            grading={},
            category="",
        ))
    return tasks
EOF
cd /ba/work && python3 -I - <<'EOF'
import sys; sys.path.insert(0,'/ba/setup')
import benchmark_plugin as b, collections
t=b.list_tasks('/data/baankafe')
print(collections.Counter(x.split for x in t), len({x.id for x in t}), all(x.instruction.strip() for x in t))
EOF
rm -rf /ba/setup/__pycache__
for i in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do mkdir -p /ba/reference/answers/$i; cp /data/baankafe/tasks/$i.json /ba/reference/ 2>/dev/null; done
mkdir -p /ba/reference/tasks; mv /ba/reference/t*.json /ba/reference/tasks/
for i in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/answers/$i/* /ba/reference/answers/$i/; done
cd /ba/reference; find . -type f; grep -rniE "v1-|v2-|x1-|x2-|x3-|parking|net-pay|net_pay|late|refund|bulk|grader|validation|test split" . | grep -v "^./answers/.*test_solve" | head; grep -rliE "parking|net_pay|late_fee|refund|bulk" .
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
./tasks/t3-shipping-fee.json
./tasks/t4-cashback.json
./tasks/t1-cafe-bill.json
./tasks/t2-split-bill.json
./answers/t4-cashback/test_solve.py
./answers/t4-cashback/solve.py
./answers/t1-cafe-bill/test_solve.py
./answers/t1-cafe-bill/solve.py
./answers/t2-split-bill/test_solve.py
./answers/t2-split-bill/solve.py
./answers/t3-shipping-fee/test_solve.py
./answers/t3-shipping-fee/solve.py
```

**Agent พูด:** plug-in เขียนเสร็จที่ `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` แล้ว ผ่านการตรวจทั้งสองข้อ

**ผลการตรวจ**
- plug-in รันจริง 1 ครั้ง ได้ train 4 · validation 2 · test 3 ตรงกับ `split.json` id ไม่ซ้ำ และทุกข้อมี `instruction`
- ค้นใน `/ba/reference/` ด้วย id ของโจทย์ validation และ test ทั้ง 5 ข้อ ไม่พบ ค้นชื่อฟังก์ชันของชุดเหล่านั้นและคำว่า grader ก็ไม่พบ
- ลบ `__pycache__` ที่เกิดตอนทดลองออกจาก `/ba/setup/` แล้ว

**plug-in**
- การแบ่งชุดเขียนไว้ใน dict `SPLIT` ในไฟล์เอง
- `instruction` มาจาก `brief` ใน `tasks/<id>.json`
- `answer_files` ชี้ไปที่ `solve.py` และ `test_solve.py` ของแต่ละข้อ
- `inputs` กับ `category` เว้นว่าง
- `grading` เป็น `{}` เพราะตัวตรวจเลือกชุดกรณีทดสอบจาก `id` อยู่แล้ว

**ที่ใส่ใน `/ba/reference/`** (เฉพาะ train 4 ข้อ: t1-cafe-bill, t2-split-bill, t3-shipping-fee, t4-cashback)
- `tasks/<id>.json` ของ 4 ข้อนั้น
- `answers/<id>/solve.py` และ `test_solve.py` ของ 4 ข้อนั้น

ผมใส่ `test_solve.py` ด้วย เพราะคุณบอกว่า Evolver อ่านเฉลยอ้างอิง (`answers/`) ของ train ได้ ไฟล์นี้เป็นเทสต์ของเฉลยเอง ไม่ใช่โค้ดหรือคำอธิบายของตัวตรวจ

**ที่ตั้งใจไม่ใส่**
- ทุกอย่างของ validation (v1, v2) และ test (x1, x2, x3) ทั้งไฟล์โจทย์และเฉลย
- `split.json` เพราะรวมรายชื่อทุกชุดไว้ด้วยกัน
- `benchmark_grader.py` และคำอธิบายใด ๆ เกี่ยวกับสิ่งที่มันตรวจหรือวิธีให้คะแนน
