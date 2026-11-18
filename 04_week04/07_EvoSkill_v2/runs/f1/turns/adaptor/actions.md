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
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; cat tasks/v1-parking-fee.json; echo; for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do echo "== $t"; cat answers/$t/*; done; echo ======; cat /ba/setup/benchmark_grader.py | head -80; diff -r /ba/data /data && echo same
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
== t1-cafe-bill
"""คิดเงินหน้าร้าน · เฉลยอ้างอิงตามมาตรฐานคิดเงินของร้าน BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if
…(ตัด 15699 ตัวอักษร)
```

### ขั้น 3 · Bash

```
sed -n 80,400p /ba/setup/benchmark_grader.py | grep -n -i -E "key|grading|task\b|task\[|task\.|function" | head -40
```

ผลที่ได้:

```
221:def explain(task, snapshot):
225:        return _checks(task, sb, rdir)
230:def grade(task, snapshot):
232:    checks = explain(task, snapshot)
236:def _checks(task, sb, rdir):
237:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
```

### ขั้น 4 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py : BaanKafe (9 โจทย์ เขียนฟังก์ชัน Python คิดเงิน)"""
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
            meta = json.load(f)
        answers = []
        for name in ("solve.py", "test_solve.py"):
            rel = "answers/%s/%s" % (task_id, name)
            if os.path.isfile(os.path.join(root, rel)):
                answers.append(rel)
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=meta["brief"],
            inputs=[],
            answer_files=answers,
            grading={"key": task_id, "function": meta.get("function", "")},
            category="billing",
        ))
    return tasks
EOF
mkdir -p /ba/reference/tasks /ba/reference/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json /ba/reference/tasks/; cp -r /data/baankafe/answers/$t /ba/reference/answers/; done
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as p, collections
ts=p.list_tasks('/data/baankafe')
print(collections.Counter(t.split for t in ts), len({t.id for t in ts}), all(t.instruction.strip() for t in ts))
json=__import__('json'); s=json.load(open('/data/split.json'))
print(all(p.SPLIT[i]==k for k,v in s.items() for i in v), len(p.SPLIT))
"
ls /ba/setup; find /ba/setup -name __pycache__ -exec rm -rf {} +; ls /ba/setup
cd /ba/reference; grep -rE "v1-|v2-|x1-|x2-|x3-|parking|net_pay|late_fee|refund|bulk|grader" . ; echo grep-rc=$?; find .
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
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
grep-rc=1
.
./answers
./tasks
./answers/t4-cashback
./answers/t1-cafe-bill
./answers/t2-split-bill
./answers/t3-shipping-fee
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
Shell cwd was reset to /ba/work
```

**Agent พูด:** Plug-in เขียนเสร็จและ `/ba/reference/` เติมแล้ว ตรวจผ่านทั้งสองเรื่องที่ต้องตรวจก่อนจบ

**Plug-in** (`/ba/setup/benchmark_plugin.py`)
- รันจริง 1 ครั้งกับ `/data/baankafe` ได้ train 4 ข้อ, validation 2 ข้อ และ test 3 ข้อ ตรงกับ `/data/split.json`
- id ไม่ซ้ำ ทั้ง 9 ข้อ และ `instruction` ของทุกข้อไม่ว่าง
- การแบ่งชุดเขียนไว้ในตัวไฟล์เป็น dict `SPLIT`
- แต่ละ Task ใช้ `brief` เป็น `instruction` และใส่ `solve.py` กับ `test_solve.py` ใน `answer_files`
- `grading` คือ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจเลือกชุดกรณีทดสอบจาก `key` หรือ `id` อยู่แล้ว
- `inputs` เป็น list ว่าง เพราะ benchmark นี้ไม่มีไฟล์ตั้งต้น
- ลบ `__pycache__` ที่เกิดจากการทดลองออกจาก `/ba/setup/` แล้ว

**ที่ใส่ใน `/ba/reference/`** (เฉพาะ train)
- `tasks/<id>.json` ของ t1–t4
- `answers/<id>/solve.py` และ `answers/<id>/test_solve.py` ของ t1–t4

**ที่ตั้งใจไม่ใส่**
- ทุกอย่างของ validation (v1, v2) และ test (x1–x3) เพื่อกันข้อมูลหลุดถึง Evolver
- `split.json` เพราะรวมรายชื่อทุกชุดไว้ในไฟล์เดียว
- `benchmark_grader.py` และคำอธิบายว่าตัวตรวจให้คะแนนอย่างไร
- ค้นใน `/ba/reference/` ด้วย id ของ v1, v2, x1, x2, x3, ชื่อฟังก์ชันของข้อเหล่านี้ (parking, net_pay, late_fee, refund, bulk) และคำว่า `grader` ไม่พบเลย

`test_solve.py` ของ t1–t4 มีหมวด Normal, Boundary, NoDrift และ Reject ซึ่งตรงกับหมวดที่ตัวตรวจใช้ ผมถือว่าเป็นส่วนของ `answers/` ที่ผู้ใช้อนุญาตให้ Evolver เห็น จึงคัดลอกมาด้วย ถ้าไม่ต้องการให้ Evolver เห็น ให้ลบไฟล์เหล่านี้ออกจาก `/ba/reference/answers/`
