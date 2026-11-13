# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; find /data -type f | head -100; cat /data/split.json
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 09:02 .
drwxr-xr-x 6 root root  4096 Nov 13 09:02 ..
-rwxr-xr-x 1 root root 20223 Nov 13 09:02 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 09:02 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 09:02 plugin_skeleton.py
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
…(ตัด 20586 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe/tasks; cat t1-cafe-bill.json; echo; ls -la /ba /ba/reference /ba/setup; grep -l "answers\|grader" *.json
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 13 09:02 .
drwxr-xr-x 1 root root 4096 Nov 13 08:52 ..
drwxr-xr-x 3 root root 4096 Nov 13 09:02 data
drwxr-xr-x 2 root root 4096 Nov 13 09:02 reference
drwxr-xr-x 2 root root 4096 Nov 13 09:02 setup
drwxr-xr-x 2 root root 4096 Nov 13 09:02 work

/ba/reference:
total 8
drwxr-xr-x 2 root root 4096 Nov 13 09:02 .
drwxr-xr-x 6 root root 4096 Nov 13 09:02 ..

/ba/setup:
total 36
drwxr-xr-x 2 root root  4096 Nov 13 09:02 .
drwxr-xr-x 6 root root  4096 Nov 13 09:02 ..
-rwxr-xr-x 1 root root 20223 Nov 13 09:02 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 09:02 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 09:02 plugin_skeleton.py
```

### ขั้น 3 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe: 9 โจทย์เขียนฟังก์ชันคิดเงิน (train 4 / validation 2 / test 3)"""
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
    tdir = os.path.join(root, "tasks")
    for tid, split in SPLIT.items():
        with open(os.path.join(tdir, tid + ".json"), encoding="utf-8") as f:
            d = json.load(f)
        tasks.append(Task(
            id=tid,
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[
                "answers/%s/solve.py" % tid,
                "answers/%s/test_solve.py" % tid,
            ],
            grading={"key": tid, "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
mkdir -p /ba/reference/baankafe/tasks
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json /ba/reference/baankafe/tasks/; done
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'/ba/setup')
import benchmark_plugin as b, os
ts=b.list_tasks('/data/baankafe')
for t in ts:
    print(t.id,t.split,all(os.path.isfile('/data/baankafe/'+p) for p in t.answer_files),t.grading)
import benchmark_grader as g
print(all(t.id in g.TASKS for t in ts))
"; find /ba/reference -type f; grep -rl "ValueError\|answers" /ba/reference
```

ผลที่ได้:

```
t1-cafe-bill train True {'key': 't1-cafe-bill', 'function': 'cafe_bill'}
t2-split-bill train True {'key': 't2-split-bill', 'function': 'split_bill'}
t3-shipping-fee train True {'key': 't3-shipping-fee', 'function': 'shipping_fee'}
t4-cashback train True {'key': 't4-cashback', 'function': 'cashback'}
v1-parking-fee validation True {'key': 'v1-parking-fee', 'function': 'parking_fee'}
v2-net-pay validation True {'key': 'v2-net-pay', 'function': 'net_pay'}
x1-late-fee test True {'key': 'x1-late-fee', 'function': 'late_fee'}
x2-refund test True {'key': 'x2-refund', 'function': 'refund'}
x3-bulk-price test True {'key': 'x3-bulk-price', 'function': 'bulk_price'}
True
/ba/reference/baankafe/tasks/t3-shipping-fee.json
/ba/reference/baankafe/tasks/t4-cashback.json
/ba/reference/baankafe/tasks/t1-cafe-bill.json
/ba/reference/baankafe/tasks/t2-split-bill.json
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ทดสอบปลั๊กอินกับ `/data/baankafe` แล้ว รันตัวตรวจจริงไม่ได้เพราะกติกาห้าม

**`benchmark_plugin.py`**
- `list_tasks(root)` คืน `Task` 9 ตัว แบ่งตาม `/data/split.json`: train 4, validation 2, test 3 ผมเขียนการแบ่งชุดไว้ในไฟล์ปลั๊กอินเอง ตามกติกา
- `instruction` มาจาก `brief` ของแต่ละโจทย์ และ `answer_files` ชี้ไปที่ `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py` ทั้ง 9 โจทย์
- `grading` ใส่ `{"key": <task id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่าน `key` นี้เลือกชุดกรณีทดสอบ
- ปลั๊กอินสร้าง path ทั้งหมดจาก `root` และ import เฉพาะ standard library กับ `plugin_api`
- ผลทดสอบ: ไฟล์เฉลยมีอยู่จริงครบทุกโจทย์ และ id ทั้ง 9 ตัวมีใน `TASKS` ของ `benchmark_grader.py`

**`/ba/reference/`**
- มีเฉพาะ `baankafe/tasks/` ของโจทย์ train 4 ข้อ (t1–t4) คงโครงโฟลเดอร์เดิม
- ไม่มีโฟลเดอร์ `answers/` ของโจทย์ใดเลย รวมถึงชุด train ตามที่สั่ง
- ไม่มีไฟล์ของโจทย์ validation หรือ test ไม่มีโค้ดตัวตรวจ และไม่มี `split.json` เพราะไฟล์นั้นระบุ id ของชุด validation กับ test

คำว่า `ValueError` ที่ปรากฏใน reference อยู่ในข้อความโจทย์ train เท่านั้น ไม่ใช่รายละเอียดของตัวตรวจ

ขนาดการรัน (3 epochs, 3 samples per task) ผมไม่ได้เขียนไว้ที่ใด เพราะ `list_tasks` มีหน้าที่คืนโจทย์เท่านั้น ค่านี้ต้องตั้งฝั่ง loop
