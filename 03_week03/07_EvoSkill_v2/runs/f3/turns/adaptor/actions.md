# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; find /data -maxdepth 3 | head -80; cat /data/split.json
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
…(ตัด 22695 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json tasks/t4-cashback.json; ls -R answers/t1-cafe-bill answers/t4-cashback; ls /ba /ba/reference 2>&1; grep -l "grading" tasks/*
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}{
 "id": "t4-cashback",
 "function": "cashback",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก\n- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = \"silver\" \"gold\" หรือ \"platinum\" · `birthday` = True คือซื้อในเดือนเกิด\n- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%\n- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน\n- เดือนเกิด ได้เงินคืน 2 เท่า\n- เงินคืนสูงสุด 200 บาทต่อบิล\n- คืนเงินคืน เป็นจำนวนเต็มสตางค์"
}answers/t1-cafe-bill:
solve.py
test_solve.py

answers/t4-cashback:
solve.py
test_solve.py
/ba:
data
reference
setup
work

/ba/reference:
```

### ขั้น 3 · Bash

```
ls -R /ba/data | head; cd /data; mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp baankafe/tasks/$t.json /ba/reference/baankafe/tasks/; cp -r baankafe/answers/$t /ba/reference/baankafe/answers/; done
echo '{
 "train": [
  "t1-cafe-bill",
  "t2-split-bill",
  "t3-shipping-fee",
  "t4-cashback"
 ]
}' > /ba/reference/split.json
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
        with open(os.path.join(root, "tasks", tid + ".json"), encoding="utf-8") as f:
            d = json.load(f)
        tasks.append(Task(
            id=tid,
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=["answers/%s/solve.py" % tid, "answers/%s/test_solve.py" % tid],
            grading={"key": tid, "function": d["function"]},
            category="billing",
        ))
    return tasks
EOF
cd /ba/setup && python3 -c "
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files,[__import__('os').path.exists('/data/baankafe/'+a) for a in t.answer_files])"
grep -rilE "grader|validation|x1-|v1-" /ba/reference; find /ba/reference
```

ผลที่ได้:

```
/ba/data:
baankafe
split.json

/ba/data/baankafe:
answers
tasks

/ba/data/baankafe/answers:
t1-cafe-bill
t1-cafe-bill train ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] [True, True]
t2-split-bill train ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] [True, True]
t3-shipping-fee train ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] [True, True]
t4-cashback train ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] [True, True]
v1-parking-fee validation ['answers/v1-parking-fee/solve.py', 'answers/v1-parking-fee/test_solve.py'] [True, True]
v2-net-pay validation ['answers/v2-net-pay/solve.py', 'answers/v2-net-pay/test_solve.py'] [True, True]
x1-late-fee test ['answers/x1-late-fee/solve.py', 'answers/x1-late-fee/test_solve.py'] [True, True]
x2-refund test ['answers/x2-refund/solve.py', 'answers/x2-refund/test_solve.py'] [True, True]
x3-bulk-price test ['answers/x3-bulk-price/solve.py', 'answers/x3-bulk-price/test_solve.py'] [True, True]
/ba/reference
/ba/reference/baankafe
/ba/reference/split.json
/ba/reference/baankafe/answers
/ba/reference/baankafe/tasks
/ba/reference/baankafe/answers
…(ตัด 821 ตัวอักษร)
```

**Agent พูด:** เขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ผมทดสอบ `list_tasks` กับ `/data/baankafe` แล้ว ได้โจทย์ครบ 9 ข้อ แต่ละข้อมีไฟล์เฉลยอยู่จริง ผมไม่ได้รัน `benchmark_grader.py` ตามที่คำสั่งกำหนด

**`benchmark_plugin.py`**
- แบ่งชุดตาม `/data/split.json` โดยเขียนการแบ่งไว้ในไฟล์ plug-in เอง: train 4 ข้อ (`t1`–`t4`), validation 2 ข้อ (`v1`, `v2`), test 3 ข้อ (`x1`–`x3`)
- `list_tasks(root)` อ่านเฉพาะ `root/tasks/<id>.json` ใช้ `brief` เป็น `instruction` และใส่ `answer_files` เป็น `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py`
- ตั้ง `grading` เป็น `{"key": <id>, "function": ...}` ตัวตรวจจึงเลือกชุดกรณีทดสอบได้ตรงกับโจทย์
- ใช้เฉพาะ standard library กับ `plugin_api` และไม่รัน process ไม่ใช้เครือข่าย

**`/ba/reference/`**
- มีเฉพาะชุด train: `baankafe/tasks/` กับ `baankafe/answers/` ของ `t1`–`t4` คงโครงโฟลเดอร์เดิม
- มี `split.json` ที่ผมเขียนใหม่ ซึ่งใส่เฉพาะรายชื่อ train ไม่มีรายชื่อ validation หรือ test
- ไม่ได้คัดลอกอะไรของ validation, test หรือ `benchmark_grader.py` เข้าไป และ grep หาคำว่า grader, validation และชื่อโจทย์ `v1-` กับ `x1-` ในโฟลเดอร์นี้ไม่พบ
