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
cat /ba/setup/benchmark_grader.py; cd /data/baankafe; cat tasks/t1-cafe-bill.json; cat answers/t1-cafe-bill/*; ls -la /data /ba/data
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
…(ตัด 24229 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /data/baankafe; cat tasks/t[234]*.json; cat answers/t3*/solve.py answers/t4*/solve.py; grep -rniE "grader|ตัวตรวจ|validation|test set|v1-|v2-|x1-|x2-|x3-|parking|net_pay|late_fee|refund|bulk" tasks/t* answers/t* ; head -c 300 answers/t2*/solve.py
```

ผลที่ได้:

```
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน\n- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)\n- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%\n- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)\n- คืนค่าส่ง เป็นจำนวนเต็มสตางค์"
}{
 "id": "t4-cashback",
 "function": "cashback",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืน
…(ตัด 4103 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py : BaanKafe (โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ)"""
import json
import os

from plugin_api import Task

# การแบ่งชุด: train 4 · validation 2 · test 3 (ตรงกับ split.json ของผู้ใช้)
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
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=spec["brief"],
            inputs=[],
            answer_files=["answers/%s/solve.py" % task_id,
                          "answers/%s/test_solve.py" % task_id],
            grading={"key": task_id, "function": spec["function"]},
            category="billing",
        ))
    return tasks
EOF
mkdir -p /ba/reference/tasks /ba/reference/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/tasks/; cp -r answers/$t /ba/reference/answers/; done
printf '%s\n' 'โฟลเดอร์ `answers/<task id>/` คือผลงานของโจทย์นั้นที่ได้คะแนนเต็ม ประกอบด้วย 2 ไฟล์ คือ `solve.py` และ `test_solve.py`' > /ba/reference/README.md
cd /ba/setup && python3 -I -c "
import sys,collections;sys.path.insert(0,'.')
import benchmark_plugin as p
t=p.list_tasks('/data/baankafe')
print(collections.Counter(x.split for x in t),len({x.id for x in t}),all(x.instruction.strip() for x in t))
import json;s=json.load(open('/data/split.json'))
print(all(p.SPLIT[i]==k for k,v in s.items() for i in v), len(p.SPLIT))"
rm -rf /ba/setup/__pycache__
cd /ba/reference; find . -type f; grep -rniE "v1-|v2-|x1-|x2-|x3-|parking|net_pay|late_fee|refund|bulk|grader" . ; echo grep-rc=$?; ls /ba/setup
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
True 9
./README.md
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
grep-rc=1
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
Shell cwd was reset to /ba/work
```

**Agent พูด:** เตรียม benchmark เสร็จแล้ว ทั้ง plug-in และโฟลเดอร์ reference

**Plug-in** (`/ba/setup/benchmark_plugin.py`)
- รันจริงแล้วได้ 9 ข้อ: train 4, validation 2, test 3 ตรงกับ `/data/split.json` ทุก id
- id ไม่ซ้ำ และ `instruction` ของทุกข้อไม่ว่าง
- การแบ่งชุดเขียนไว้ในไฟล์ plug-in เอง
- `instruction` อ่านมาจากฟิลด์ `brief` ของแต่ละโจทย์ และ `answer_files` ชี้ไปที่ `solve.py` กับ `test_solve.py` ของข้อนั้น
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ซึ่งตัวตรวจใช้ `key` เลือกชุดกรณีทดสอบ

**`/ba/reference/` มีอะไรบ้าง**
- `README.md` ตามข้อความที่ผู้ใช้กำหนด
- `tasks/` มีไฟล์โจทย์ของชุด train 4 ข้อ (t1 ถึง t4)
- `answers/` มี `solve.py` และ `test_solve.py` ของชุด train 4 ข้อ ตามที่ผู้ใช้อนุญาตให้ Evolver เห็น

**สิ่งที่ตั้งใจไม่ใส่**
- ทุกอย่างของชุด validation (v1, v2) และชุด test (x1, x2, x3) ทั้งข้อความโจทย์ เฉลย และชื่อฟังก์ชัน
- `/data/split.json` เพราะรวมรายชื่อทุกชุดไว้ด้วยกัน
- `benchmark_grader.py` และทุกข้อความที่อธิบายว่าตัวตรวจให้คะแนนอย่างไร

ผมค้นใน `/ba/reference/` ด้วย id และชื่อฟังก์ชันของ validation และ test ทุกข้อ (v1, v2, x1 ถึง x3, parking, net_pay, late_fee, refund, bulk) และคำว่า grader ไม่พบเลย

ไฟล์เฉลย `solve.py` ของ t3 และ t4 มีคอมเมนต์เกี่ยวกับนโยบายธุรกิจ (S1, S2, C1, C2) อยู่ ผมคัดลอกมาตามเดิมเพราะเป็นส่วนของเฉลย train ที่ผู้ใช้อนุญาตให้ Evolver เห็น คอมเมนต์เหล่านี้ไม่ได้อธิบายการทำงานของตัวตรวจ

ผมลบ `__pycache__` ที่เกิดจากการทดสอบออกจาก `/ba/setup/` แล้ว
