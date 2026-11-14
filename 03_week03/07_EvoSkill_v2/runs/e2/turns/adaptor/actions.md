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
cd /data/baankafe; cat tasks/t1-cafe-bill.json tasks/x1-late-fee.json; echo; cat answers/t1-cafe-bill/*; cat /ba/setup/benchmark_grader.py | head -60; diff -r /data /ba/data && echo same; grep -il "baankafe\|cafe" /data/baankafe/tasks/*
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}{
 "id": "x1-late-fee",
 "function": "late_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `late_fee(amount, days_late)` ในไฟล์ `solve.py` สำหรับคิดค่าปรับของลูกค้าขายส่งที่ชำระเงินช้า\n- `amount` = ยอดค้างชำระ (สตางค์ ตั้งแต่ 0) · `days_late` = จำนวนวันที่ช้า (จำนวนเต็ม 0–365)\n- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ\n- ช้าเกิน 3 วัน คิดค่าปรับวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)\n- ค่าปรับสูงสุด 15% ของยอดค้างชำระ\n- คืนค่าปรับ เป็นจำนวนเต็มสตางค์"
}
"""คิดเงินหน้าร้าน · เฉลยอ้างอิงตามมาตรฐานคิดเงินของร้าน BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # 
…(ตัด 5766 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /ba/setup; grep -n "task\b\|task\[\|task\.\|grading\|key" benchmark_grader.py | head -40; cd /data/baankafe; grep -rniE "v1|v2|x1|x2|x3|parking|net-pay|late|refund|bulk|grader|grade|ตรวจ|policy|นโยบาย" answers/t* tasks/t*
```

ผลที่ได้:

```
4:  grade(task, snapshot) -> คะแนน 0 ถึง 1     task = 1 แถวของ plug-in · snapshot = โฟลเดอร์ทำงานของ Solver ตอนจบ
5:  explain(task, snapshot) -> ผลรายข้อ        ใช้ทำรายงานของผู้สอนเท่านั้น ไม่ถูกส่งให้ Evolver
6:  python3 benchmark_grader.py <snapshot> <task.json>   พิมพ์ {"score": ..., "checks": [...]} (รูปแบบที่ตัวรัน Trial ใช้)
300:def explain(task, snapshot):
304:        return _checks(task, sb, rdir)
309:def grade(task, snapshot):
311:    checks = explain(task, snapshot)
315:def _checks(task, sb, rdir):
316:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
447:    task = json.load(open(sys.argv[2], encoding="utf-8"))
448:    checks = explain(task, sys.argv[1])
answers/t3-shipping-fee/solve.py:29:    if express and weight_g > 20000:  # นโยบาย S2: ส่งด่วนรับน้ำหนักไม่เกิน 20,000 กรัม
answers/t3-shipping-fee/solve.py:31:    if distance_km == 0:  # นโยบาย S1: ลูกค้ารับเองที่ร้าน ไม่คิดค่าส่ง
answers/t4-cashback/solve.py:8:    """นโยบาย C2: เงินคืน = เงินที่ร้านจ่ายออก ปัดลงเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
answers/t4-cashback/solve.py:36:    if birthday and tier in ("gold", "platinum"):  # นโยบาย C1: silver ไม่ได้สิทธิ์เดือนเกิด
Shell cwd was reset to /ba/work
```

### ขั้น 4 · Bash

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
            spec = json.load(f)
        ans_dir = os.path.join("answers", task_id)
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=spec["brief"],
            inputs=[],
            answer_files=[ans_dir + "/solve.py", ans_dir + "/test_solve.py"],
            grading={"key": task_id, "function": spec.get("function", "")},
            category="",
        ))
    return tasks
EOF
mkdir -p /ba/reference/tasks /ba/reference/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/tasks/; cp -r answers/$t /ba/reference/answers/; done
find /ba/reference -name __pycache__ -exec rm -rf {} +
cd /ba/work && python3 -I - <<'EOF'
import sys, json, collections
sys.path.insert(0,'/ba/setup')
import benchmark_plugin as p
ts=p.list_tasks('/data/baankafe')
print(collections.Counter(t.split for t in ts), len({t.id for t in ts}), all(t.instruction.strip() for t in ts))
sp=json.load(open('/data/split.json'))
print(all(p.SPLIT[i]==s for s,l in sp.items() for i in l), len(p.SPLIT))
EOF
find /ba/setup /ba/reference -name __pycache__ -exec rm -rf {} + ; ls /ba/setup; find /ba/reference
grep -rniE "v1-|v2-|x1-|x2-|x3-|parking|net.pay|late.fee|refund|bulk|grader|v1|v2" /ba/reference; echo grep-rc=$?
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
True 9
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
/ba/reference
/ba/reference/answers
/ba/reference/tasks
/ba/reference/answers/t4-cashback
/ba/reference/answers/t1-cafe-bill
/ba/reference/answers/t2-split-bill
/ba/reference/answers/t3-shipping-fee
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
grep-rc=1
```

**Agent พูด:** Plug-in เขียนเสร็จและรันตรวจแล้ว ส่วน `/ba/reference/` เติมเฉพาะของชุด train และค้น id ของ validation กับ test ไม่พบเลย

**Plug-in** (`/ba/setup/benchmark_plugin.py`)
- การแบ่งชุดเขียนไว้ในไฟล์เอง ตรงกับ `/data/split.json` ทุกข้อ
- ผลรันจริง 1 ครั้ง: train 4 · validation 2 · test 3 รวม 9 ข้อ id ไม่ซ้ำ และ `instruction` ไม่ว่างทุกข้อ
- `instruction` มาจาก `brief` ของแต่ละโจทย์
- `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `test_solve.py`
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่าน `grading["key"]` แล้วเลือกชุดกรณีทดสอบจาก key นั้น
- `inputs` เว้นว่าง เพราะโจทย์เหล่านี้ไม่มีไฟล์ตั้งต้น

**สิ่งที่ใส่ใน `/ba/reference/`** (ตามข้อ 4 ที่ Evolver เห็นได้)
- `tasks/<id>.json` ของ train 4 ข้อ: t1-cafe-bill, t2-split-bill, t3-shipping-fee, t4-cashback
- `answers/<id>/solve.py` และ `test_solve.py` ของ train 4 ข้อเดียวกัน
- ล้าง `__pycache__` แล้ว

**สิ่งที่ตั้งใจไม่ใส่**
- โจทย์และเฉลยของ validation (v1, v2) และ test (x1, x2, x3) รวมถึง id และชื่อฟังก์ชัน
- `split.json` เพราะมีรายชื่อของทุกชุด
- `benchmark_grader.py` และคำอธิบายว่ามันตรวจอะไร
- ในไฟล์เฉลย train มีคอมเมนต์เรื่องนโยบาย S1, S2, C1, C2 ของ t3 และ t4 ซึ่งเป็นเนื้อหาของเฉลย ไม่ใช่คำอธิบายของตัวตรวจ จึงคัดลอกไว้ตามที่อนุญาตให้ Evolver เห็นเฉลย train

ค้น `/ba/reference/` ด้วย id ของ validation และ test ทุกข้อ ชื่อฟังก์ชัน และคำว่า grader ไม่พบสักรายการ ผมไม่ได้ทิ้งไฟล์ทดลองไว้ใน `/ba/setup/` หรือ `/ba/reference/` ส่วน `benchmark_grader.py` ไม่ได้แก้ แต่ผมเปิดอ่านบางส่วนเพื่อดูว่า `grading` ต
…(ตัด 12 ตัวอักษร)
