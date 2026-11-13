# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; find /data -type f | head -100; cat /data/split.json
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 09:12 .
drwxr-xr-x 6 root root  4096 Nov 13 09:12 ..
-rwxr-xr-x 1 root root 20223 Nov 13 09:12 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 09:12 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 09:12 plugin_skeleton.py
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
cd /data/baankafe/tasks; cat t1-cafe-bill.json; echo; cat v1-parking-fee.json; echo; python3 -c "
import json,glob
for f in sorted(glob.glob('*.json')): print(f, list(json.load(open(f))))"; ls /ba /ba/reference
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
t1-cafe-bill.json ['id', 'function', 'brief']
t2-split-bill.json ['id', 'function', 'brief']
t3-shipping-fee.json ['id', 'function', 'brief']
t4-cashback.json ['id', 'function', 'brief']
v1-parking-fee.json ['id', 'function', 'brief']
v2-net-pay.json ['id', 'function', 'brief']
x1-late-fee.json ['id', 'functio
…(ตัด 181 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe: โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ"""
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
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[
                "answers/%s/solve.py" % tid,
                "answers/%s/test_solve.py" % tid,
            ],
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do
 cp /data/baankafe/tasks/$t.json /ba/reference/baankafe/tasks/
 cp -r /data/baankafe/answers/$t /ba/reference/baankafe/answers/
done
cd /ba/setup && python3 -c "
import benchmark_plugin as b, collections
t=b.list_tasks('/data/baankafe'); print(collections.Counter(x.split for x in t)); print(t[0])
import os
print(all(os.path.isfile(os.path.join('/data/baankafe',p)) for x in t for p in x.answer_files))"
find /ba/reference -type f; grep -rlE "parking|net-pay|late|refund|bulk" /ba/reference
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2})
Task(id='t1-cafe-bill', split='train', instruction='ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์', inputs=[], answer_files=['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'], grading={'key': 't1-cafe-bill', 'function': 'cafe_bill'}, category='coding')
True
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
/ba/reference/baankafe/answers/t3-shipping-fee/test_solve.
…(ตัด 58 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -rnoE "parking|net-pay|net_pay|late.fee|refund|bulk|x[123]-|v[12]-" /ba/reference | head; grep -rnoiE ".{15}late.{10}" /ba/reference | head -3
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน `benchmark_plugin.py` เสร็จแล้ว และเติม `/ba/reference/` แล้ว

**`/ba/setup/benchmark_plugin.py`**
- `list_tasks(root)` อ่าน `tasks/<id>.json` ใต้ `root` แล้วคืน `Task` 9 ตัว การแบ่งชุดตามที่ให้มา: train 4, validation 2, test 3 ตารางแบ่งชุดเขียนไว้ใน `SPLIT` ในไฟล์ plug-in เอง
- แต่ละ `Task` มี `instruction` เป็นข้อความ `brief` และ `answer_files` ชี้ไป `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py` ส่วน `inputs` ว่างเพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- `grading` เป็น `{"key": <task id>, "function": <ชื่อฟังก์ชัน>}` โดย `key` ตรงกับคีย์ใน `TASKS` ของ `benchmark_grader.py`
- ผมไม่ได้รันตัวตรวจ ตามที่กำหนด
- ผมทดสอบกับ `/data/baankafe` แล้ว ได้ 4/2/3 ตามชุด และ `answer_files` ทุกไฟล์มีอยู่จริง

**`/ba/reference/`**
- คัดลอกเฉพาะ `baankafe/tasks/` กับ `baankafe/answers/` ของ 4 โจทย์ train (t1–t4) โดยคงโครงโฟลเดอร์เดิม
- ไม่มีไฟล์ของ validation หรือ test และไม่มีโค้ดตัวตรวจ ผมไม่ได้คัดลอก `split.json` เพราะมี id ของโจทย์ validation และ test
- ผมค้นหา id และชื่อฟังก์ชันของโจทย์ validation และ test ในโฟลเดอร์นี้ ไม่พบ
