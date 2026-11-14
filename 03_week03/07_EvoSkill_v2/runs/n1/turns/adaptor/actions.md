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
cat /ba/setup/benchmark_grader.py | head -80; cat /data/baankafe/tasks/t1-cafe-bill.json; cat /data/baankafe/answers/t1-cafe-bill/*; ls -la /ba/data /data
```

ผลที่ได้:

```
#!/usr/bin/env python3
"""benchmark_grader.py - ตัวตรวจของผู้ใช้ สำหรับ EvoSkill v2 (โจทย์คิดเงินของร้าน BaanKafe)

  grade(task, snapshot) -> คะแนน 0 ถึง 1     task = 1 แถวของ plug-in · snapshot = โฟลเดอร์ทำงานของ Solver ตอนจบ
  explain(task, snapshot) -> ผลรายข้อ        ใช้ทำรายงานของผู้สอนเท่านั้น ไม่ถูกส่งให้ Evolver
  python3 benchmark_grader.py <snapshot> <task.json>   พิมพ์ {"score": ..., "checks": [...]} (รูปแบบที่ตัวรัน Trial ใช้)

การตรวจและกรณีทดสอบ เหมือนตัวตรวจของบท 05 และ 06 ทุกข้อ (suite/grade.py):
มาตรฐานคิดเงินของร้าน 10 ข้อ และข้อตรวจ `policy` (นโยบายธุรกิจที่ทีมรู้กันเอง) เฉพาะงานที่มีนโยบายซ่อน
  t3-shipping-fee  S1 ลูกค้ารับเองที่ร้าน (distance_km = 0) ไม่คิดค่าส่ง · S2 ส่งด่วนรับไม่เกิน 20,000 กรัม
  t4-cashback      C1 สิทธิ์เดือนเกิด 2 เท่า เฉพาะ gold และ platinum · C2 เงินคืน = เงินที่ร้านจ่ายออก ปัดลง
งานเงินคืนใช้การปัดของนโยบาย C2 แทนการปัดครึ่งขึ้น จึงไม่มีข้อตรวจ half_up (ตรวจใน policy แทน)
คะแนน = จำนวนข้อที่ผ่าน ÷ จำนวนข้อตรวจของงานนั้น (10 หรือ 11 ข้อ) · Solver และ Evolver ต้องไม่เห็นไฟล์นี้
"""
import json, os, re, shutil, subprocess, sys, tempfile
from fractions import Fraction as F


def half_up(x):
    return int((F(x) * 2 + 1) // 2)


# -------
…(ตัด 5922 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /data/baankafe; sed -n 80,400p /ba/setup/benchmark_grader.py | grep -n "task\|key\|grading" ; for t in t2-split-bill t3-shipping-fee t4-cashback; do cat tasks/$t.json; done; grep -rniE "v1|v2|x1|x2|x3|parking|net.pay|late.fee|refund|bulk|grader|policy|นโยบาย|ตัวตรวจ|validation|test" answers/t* tasks/t* | grep -v "unittest\|test_solve\|def test_\|^answers/t./test_solve" | head -30; grep -rniE "parking|net_pay|late_fee|refund|bulk_price" answers/t* tasks/t*
```

ผลที่ได้:

```
221:def explain(task, snapshot):
225:        return _checks(task, sb, rdir)
230:def grade(task, snapshot):
232:    checks = explain(task, snapshot)
236:def _checks(task, sb, rdir):
237:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน\n- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)\n- ระยะทางเกิน 100 กม. ค
…(ตัด 1057 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py : โจทย์คิดเงินของร้าน BaanKafe (9 ข้อ)"""
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
            grading={"key": task_id, "function": data.get("function", "")},
            category="billing",
        ))
    return tasks
EOF
cd /ba/work && python3 -I -c "
import sys; sys.path.insert(0,'/ba/setup')
import benchmark_plugin as b, collections
t=b.list_tasks('/data/baankafe')
print(collections.Counter(x.split for x in t), len({x.id for x in t}), all(x.instruction.strip() for x in t))
import os
print(all(os.path.exists('/data/baankafe/'+p) for x in t for p in x.answer_files))
"
rm -rf /ba/setup/__pycache__
R=/ba/reference; mkdir -p $R/tasks $R/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json $R/tasks/; cp -r /data/baankafe/answers/$t $R/answers/; done
printf '%s\n' 'โฟลเดอร์ `answers/<task id>/` คือผลงานของโจทย์นั้นที่ได้คะแนนเต็ม ประกอบด้วย 2 ไฟล์ คือ `solve.py` และ `test_solve.py`' > $R/README.md
find $R -name __pycache__ -exec rm -rf {} +; find $R -type f
grep -rliE "v1-parking|v2-net|x1-late|x2-refund|x3-bulk|parking_fee|net_pay|late_fee|refund|bulk_price|grader" $R; echo "grep rc=$?"; ls /ba/setup
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
True
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
grep rc=1
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
```

**Agent พูด:** Plug-in เสร็จแล้วและรันผ่านจริง 1 ครั้ง โฟลเดอร์ `/ba/reference/` ก็เติมแล้ว ค้น id และชื่อฟังก์ชันของ validation กับ test รวมถึงคำว่า grader ในโฟลเดอร์นั้น ไม่พบ

**Plug-in** (`/ba/setup/benchmark_plugin.py`)
- การแบ่งชุดเขียนไว้ในไฟล์เอง ตรงกับ `split.json`: train 4 ข้อ, validation 2 ข้อ, test 3 ข้อ
- id ไม่ซ้ำ ทุกข้อมี `instruction` ไม่ว่าง และ `answer_files` ชี้ไปยังไฟล์ที่มีอยู่จริง
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ส่วน `category` เป็น `"billing"` ทุกข้อ

**สิ่งที่ใส่ใน `/ba/reference/`**
- `README.md` มีข้อความที่ระบุทุกตัวอักษร
- `tasks/<id>.json` ของโจทย์ train ทั้ง 4 ข้อ ซึ่งเป็นข้อความโจทย์ที่ Evolver อ่านได้
- `answers/<id>/solve.py` และ `test_solve.py` ของโจทย์ train ทั้ง 4 ข้อ

**สิ่งที่ตั้งใจไม่ใส่**
- โจทย์ validation (`v1-parking-fee`, `v2-net-pay`) และ test (`x1-late-fee`, `x2-refund`, `x3-bulk-price`) ทั้งหมด ทั้งไฟล์โจทย์และเฉลย
- `split.json` เพราะรวมรายชื่อทุกชุดไว้ด้วยกัน
- `benchmark_grader.py` และคำอธิบายเรื่องการให้คะแนน

เฉลย train สองข้อมีคอมเมนต์ในโค้ดที่เขียนว่า "นโยบาย S1/S2/C1/C2" (`t3-shipping-fee`, `t4-cashback`) ฉันคัดลอกไว้ตามเดิม เพราะคุณอนุญาตให้ Evolver เห็นเฉลยของ train และคอมเมนต์เหล่านี้อธิบายกติกาธุรกิจที่เฉลยทำตาม ไม่ได้อธิบายว่าตัวตรวจตรวจอะไร
