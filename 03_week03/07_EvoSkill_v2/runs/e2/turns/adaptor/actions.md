# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py; echo ----; cat benchmark_grader.py; echo ----; find /data -type f | head -100; cat /data/split.json
```

ผลที่ได้:

```
total 40
drwxr-xr-x 2 root root  4096 Nov 15 03:51 .
drwxr-xr-x 6 root root  4096 Nov 15 03:51 ..
-rwxr-xr-x 1 root root 24093 Nov 15 03:51 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 15 03:51 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 15 03:51 plugin_skeleton.py
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
…(ตัด 23166 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json tasks/t3-shipping-fee.json; ls -la /ba /ba/reference; head -30 answers/t4-cashback/solve.py
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน\n- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)\n- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%\n- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)\n- คืนค่าส่ง เป็นจำนวนเต็มสตางค์"
}/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 15 03:51 .
drwxr-xr-x 1 root root 4096 Nov 14 23:46 ..
drwxr-xr-x 3 root root 4096 Nov 15 03:51 data
drwxr-xr-x 2 root root 4096 Nov 15 03:51 reference
drwxr-xr-x 2 root root 4096 Nov 15 03:
…(ตัด 1144 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe billing-code benchmark (9 tasks)"""
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
        rel = "tasks/%s.json" % tid
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
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do
 cp /data/baankafe/tasks/$t.json /ba/reference/baankafe/tasks/
 cp -r /data/baankafe/answers/$t /ba/reference/baankafe/answers/
done
cd /ba/setup && python3 -c "
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,len(t.instruction),t.answer_files)"
find /ba/reference -type f; grep -rl -E "parking|net-pay|late|refund|bulk" /ba/reference
```

ผลที่ได้:

```
t1-cafe-bill train 329 ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py']
t2-split-bill train 405 ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py']
t3-shipping-fee train 485 ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py']
t4-cashback train 417 ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py']
v1-parking-fee validation 408 ['answers/v1-parking-fee/solve.py', 'answers/v1-parking-fee/test_solve.py']
v2-net-pay validation 458 ['answers/v2-net-pay/solve.py', 'answers/v2-net-pay/test_solve.py']
x1-late-fee test 405 ['answers/x1-late-fee/solve.py', 'answers/x1-late-fee/test_solve.py']
x2-refund test 429 ['answers/x2-refund/solve.py', 'answers/x2-refund/test_solve.py']
x3-bulk-price test 391 ['answers/x3-bulk-price/solve.py', 'answers/x3-bulk-price/test_solve.py']
/ba/reference/baankafe/tasks/t3-shipping-fee.json
/ba/reference/baankafe/tasks/t4-cashback.json
/ba/reference/baankafe/tasks/t1-cafe-bill.json
/ba/reference/baankafe/tasks/t2-split-bill.json
/ba/reference/baankafe/answers/t4-cashback/test_solve.py
/ba/reference/baankafe/answers/t4-cashback/solve.py
/ba/reference/baankafe/answers/t1-cafe
…(ตัด 302 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -rn -E "parking|net-pay|net_pay|late_fee|late-fee|refund|bulk|x1-|x2-|x3-|v1-|v2-" /ba/reference | head
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน plug-in และเติมโฟลเดอร์ reference เสร็จแล้ว ทดสอบ `list_tasks('/data/baankafe')` แล้วได้โจทย์ครบ 9 ข้อ แบ่งเป็น train 4, validation 2 และ test 3 ตาม `/data/split.json` ผมไม่ได้รันตัวตรวจ เพราะ loop เป็นผู้รัน

**`/ba/setup/benchmark_plugin.py`**
- การแบ่งชุดเขียนไว้ใน dict `SPLIT` ภายในไฟล์
- โจทย์แต่ละข้อใช้ `brief` เป็น `instruction` และ `answer_files` ชี้ไปที่ `answers/<id>/solve.py` กับ `test_solve.py`
- `inputs` ว่าง เพราะโจทย์นี้ไม่มีไฟล์ตั้งต้น
- `grading` เป็น `{"key": <task id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจเลือกชุดกรณีทดสอบจาก `key` นี้ ส่วน `function` เป็นข้อมูลเสริม
- plug-in ใช้เฉพาะ standard library กับ `plugin_api` และอ่านเฉพาะไฟล์ใต้ `root`

**`/ba/reference/`** (โครงเดิมใต้ `baankafe/`)
- `tasks/<id>.json` และ `answers/<id>/{solve.py,test_solve.py}` ของโจทย์ train 4 ข้อ คือ `t1-cafe-bill`, `t2-split-bill`, `t3-shipping-fee` และ `t4-cashback`
- ผมไม่ได้คัดลอกอะไรของ validation และ test รวมถึง `split.json` ซึ่งมีชื่อโจทย์ของสองชุดนั้น
- ไม่มีโค้ดตัวตรวจหรือคำอธิบายการตรวจ
- ผมค้นไฟล์ในโฟลเดอร์ด้วยชื่อโจทย์และชื่อฟังก์ชันของ validation/test แล้วไม่พบ

เฉลยของ `t3-shipping-fee` และ `t4-cashback` มีนโยบายที่ซ่อนอยู่ (S1, S2, C1, C2) เขียนไว้ในโค้ด ตามคำสั่งว่า Evolver อ่านเฉลยของ train ได้ ผมจึงเก็บไว้ครบ
