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
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; cat tasks/t4-cashback.json; echo; ls -la /data /ba/data; cat answers/t1-cafe-bill/*; cat /ba/setup/benchmark_grader.py | head -60; diff -r /data /ba/data && echo same
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
{
 "id": "t4-cashback",
 "function": "cashback",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก\n- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = \"silver\" \"gold\" หรือ \"platinum\" · `birthday` = True คือซื้อในเดือนเกิด\n- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%\n- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน\n- เดือนเกิด ได้เงินคืน 2 เท่า\n- เงินคืนสูงสุด 200 บาทต่อบิล\n- คืนเงินคืน เป็นจำนวนเต็มสตางค์"
}
/ba/data:
total 16
drwxr-xr-x 3 root root 4096 Nov 15 06:02 .
drwxr-xr-x 6 root root 4096 Nov 15 06:02 ..
drwxr-xr-x 4 root root 4096 Nov 13 08:46 baankafe
-rw-r--r-- 1 root root  213 Nov 15 06:02 split.json

/data:
total 16
drwxr-xr-x 3 root root 4096 Nov 15 06:02 .
drwxr-xr-x 1 root root 4096 Nov 15 
…(ตัด 5849 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /data/baankafe; for t in t2-split-bill t3-shipping-fee t4-cashback; do cat tasks/$t.json; echo; cat answers/$t/solve.py | head -50; done; grep -rn -i "grader\|ตัวตรวจ\|policy\|นโยบาย\|v1-\|v2-\|x1-\|x2-\|x3-\|parking\|net_pay\|late_fee\|refund\|bulk" answers/t* tasks/t*
```

ผลที่ได้:

```
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}
"""หารบิล · เฉลยอ้างอิงตามมาตรฐานคิดเงินของร้าน BaanKafe"""
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

def split_bill(total, people, tip_
…(ตัด 5406 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -n "task\b\|task\[\|task\.\|grading\|key" /ba/setup/benchmark_grader.py | head -40
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
```

### ขั้น 5 · Bash

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
        answer_dir = os.path.join(root, "answers", task_id)
        answer_files = ["answers/%s/%s" % (task_id, n) for n in sorted(os.listdir(answer_dir))
                        if os.path.isfile(os.path.join(answer_dir, n))]
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=spec["brief"],
            inputs=[],
            answer_files=answer_files,
            grading={"key": task_id, "function": spec.get("function", "")},
            category="billing",
        ))
    return tasks
EOF
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/baankafe/tasks/; cp -r answers/$t /ba/reference/baankafe/answers/; done
cd /ba/work && python3 -I -c "
import sys,collections;sys.path.insert(0,'/ba/setup')
import benchmark_plugin as b
ts=b.list_tasks('/data/baankafe')
print(collections.Counter(t.split for t in ts),len({t.id for t in ts}),all(t.instruction.strip() for t in ts))
print(ts[0].answer_files)"
find /ba/reference -type f; ls /ba/setup
grep -rniE "v1-|v2-|x1-|x2-|x3-|parking|net.pay|net_pay|late.fee|refund|bulk|grader|split.json" /ba/reference && echo FOUND
```

ผลที่ได้:

```
Exit code 1
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py']
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
__pycache__
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
```

**Agent พูด:** ตอนนี้กำลังล้างไฟล์ทดลอง (`__pycache__` ใน `/ba/setup/`) แล้วตรวจ `/ba/reference/` อีกครั้ง

### ขั้น 6 · Bash

```
rm -rf /ba/setup/__pycache__; find /ba/reference -name __pycache__; ls /ba/setup; grep -rn "grading" /ba/reference | head -2; echo done
```

ผลที่ได้:

```
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
done
```

**Agent พูด:** Plug-in เขียนเสร็จที่ `/ba/setup/benchmark_plugin.py` และ `/ba/reference/` เติมครบแล้ว ผมรัน plug-in จริงหนึ่งครั้งกับ `/data/baankafe` ผลผ่านทุกข้อ

**ผลการตรวจ**
- จำนวนโจทย์ต่อชุดตรงกับ `split.json`: train 4, validation 2, test 3 รวม 9 ข้อ
- id ไม่ซ้ำกัน และ `instruction` ของทุกข้อไม่ว่าง
- ค้นใน `/ba/reference/` ด้วย id ของ validation และ test ทั้ง 5 ข้อ, ชื่อฟังก์ชันที่เกี่ยวกับโจทย์เหล่านั้น, คำว่า `grader` และ `split.json` ไม่พบเลย

**Plug-in**
- การแบ่งชุดเขียนไว้ใน dict `SPLIT` ในไฟล์ plug-in เอง
- แต่ละข้ออ่าน `brief` จาก `tasks/<id>.json` มาเป็น `instruction`
- `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `test_solve.py`
- `inputs` ว่าง เพราะ Solver เริ่มจากโฟลเดอร์ว่าง
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ซึ่งตัวตรวจอ่าน `key` ตามที่ระบุไว้
- `category` ใส่ `"billing"` ทุกข้อ

**สิ่งที่ใส่ใน `/ba/reference/baankafe/`**
- `tasks/` ของ train 4 ข้อ ได้แก่ t1-cafe-bill, t2-split-bill, t3-shipping-fee และ t4-cashback
- `answers/` ของ train 4 ข้อเดียวกัน คือ `solve.py` กับ `test_solve.py` ตามที่ผู้ใช้อนุญาตให้ Evolver เห็น

**สิ่งที่ตั้งใจไม่ใส่**
- ทุกอย่างของ validation (v1, v2) และ test (x1, x2, x3) ทั้งข้อความโจทย์และเฉลย
- `split.json` เพราะรวมรายชื่อ validation และ test ไว้ด้วย
- `benchmark_grader.py` ตัวตรวจ ผมอ่านไฟล์นี้เพื่อดูว่า `grading` ต้องมีค่าอะไร แต่ไม่ได้แก้ และไม่ได้คัดลอกไปไว้ที่ใด

**ข้อสังเกตเรื่องเฉลยชุด train**
- `solve.py` ของ t3 และ t4 มีคอมเมนต์เรื่องนโยบายซ่อน (S1, S2, C1, C2) ผมไม่ได้ตัดออก เพราะเป็นส่วนของเฉลยที
…(ตัด 283 ตัวอักษร)
