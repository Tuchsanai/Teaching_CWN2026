# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py; echo ----; cat benchmark_grader.py; echo ----; cat /data/split.json; find /data/baankafe | head -100
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 09:30 .
drwxr-xr-x 6 root root  4096 Nov 13 09:30 ..
-rwxr-xr-x 1 root root 20223 Nov 13 09:30 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 09:30 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 09:30 plugin_skeleton.py
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
…(ตัด 20956 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe/tasks; for f in t1* v1*; do cat $f; echo; done; ls -la /ba /ba/reference 2>&1; ls -la /data
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
/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 13 09:30 .
drwxr-xr-x 1 root root 4096 Nov 13 08:52 ..
drwxr-xr-x 3 root root 4096 Nov 13 09:30 data
drwxr-xr-x 2 root root 4096 Nov 13 09:30 reference
drwxr-xr-x 2 root root 4096 Nov 13 09:30 setup
drwxr-xr-x 2 root root 4096 Nov 13 09:30 work

/ba/reference:
tota
…(ตัด 320 ตัวอักษร)
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
        with open(os.path.join(root, "tasks", tid + ".json"), encoding="utf-8") as f:
            d = json.load(f)
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[
                os.path.join("answers", tid, "solve.py"),
                os.path.join("answers", tid, "test_solve.py"),
            ],
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
cd /ba/setup && python3 -c "
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files[0],t.grading)
"
R=/ba/reference/baankafe; mkdir -p $R/tasks $R/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json $R/tasks/; cp -r /data/baankafe/answers/$t $R/answers/; done
echo '{"train": ["t1-cafe-bill","t2-split-bill","t3-shipping-fee","t4-cashback"]}' > /ba/reference/split.json
find /ba/reference -type f; grep -rlE "parking|net-pay|late|refund|bulk" /ba/reference; rm -rf /ba/setup/__pycache__
```

ผลที่ได้:

```
t1-cafe-bill train answers/t1-cafe-bill/solve.py {'key': 't1-cafe-bill', 'function': 'cafe_bill'}
t2-split-bill train answers/t2-split-bill/solve.py {'key': 't2-split-bill', 'function': 'split_bill'}
t3-shipping-fee train answers/t3-shipping-fee/solve.py {'key': 't3-shipping-fee', 'function': 'shipping_fee'}
t4-cashback train answers/t4-cashback/solve.py {'key': 't4-cashback', 'function': 'cashback'}
v1-parking-fee validation answers/v1-parking-fee/solve.py {'key': 'v1-parking-fee', 'function': 'parking_fee'}
v2-net-pay validation answers/v2-net-pay/solve.py {'key': 'v2-net-pay', 'function': 'net_pay'}
x1-late-fee test answers/x1-late-fee/solve.py {'key': 'x1-late-fee', 'function': 'late_fee'}
x2-refund test answers/x2-refund/solve.py {'key': 'x2-refund', 'function': 'refund'}
x3-bulk-price test answers/x3-bulk-price/solve.py {'key': 'x3-bulk-price', 'function': 'bulk_price'}
/ba/reference/split.json
/ba/reference/baankafe/tasks/t3-shipping-fee.json
/ba/reference/baankafe/tasks/t4-cashback.json
/ba/reference/baankafe/tasks/t1-cafe-bill.json
/ba/reference/baankafe/tasks/t2-split-bill.json
/ba/reference/baankafe/answers/t4-cashback/test_solve.py
/ba/reference/baankafe/answers/t4-cash
…(ตัด 386 ตัวอักษร)
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เรียบร้อยแล้ว `list_tasks('/data/baankafe')` คืนโจทย์ครบ 9 ข้อ แบ่งเป็น train 4, validation 2 และ test 3 ตามที่ `/data/split.json` กำหนด ผมยังไม่ได้รันตัวตรวจ เพราะ loop เป็นผู้รัน

**Plug-in**
- การแบ่งชุดเขียนไว้ใน dict `SPLIT` ในไฟล์ plug-in เอง
- plug-in อ่านเฉพาะ `tasks/<id>.json` ใต้ root และ import แค่ `json`, `os` และ `plugin_api`
- แต่ละ `Task` ใช้ `brief` เป็น `instruction` และใส่ `answer_files` เป็น `answers/<id>/solve.py` กับ `answers/<id>/test_solve.py`
- `grading` มี `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่าน `grading["key"]` เพื่อเลือกชุดกรณีทดสอบ
- `inputs` เว้นว่างไว้ เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น

**Reference สำหรับ Evolver**
- `/ba/reference/baankafe/tasks/` และ `answers/` มีเฉพาะโจทย์ train 4 ข้อ โดยคงโครงโฟลเดอร์เดิม
- `/ba/reference/split.json` ผมเขียนใหม่ให้มีเฉพาะรายชื่อ train เพราะไฟล์ต้นฉบับบอกชื่อโจทย์ validation กับ test
- ใน `/ba/reference/` ไม่มีโค้ดตัวตรวจ ไม่มีอะไรของโจทย์ validation หรือ test และไม่มีไฟล์ที่อธิบายวิธีตรวจ
