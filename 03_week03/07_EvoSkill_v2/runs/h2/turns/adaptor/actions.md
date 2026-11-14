# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; ls -R /data | head -50; cat /data/split.json
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
…(ตัด 22620 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; ls answers/x3-bulk-price; cat tasks/t1-cafe-bill.json; ls -la /data /ba /ba/reference 2>&1; python3 -c "
import json;d=json.load(open('tasks/t3-shipping-fee.json'));print(d.keys())"
```

ผลที่ได้:

```
solve.py
test_solve.py
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 15 04:15 .
drwxr-xr-x 1 root root 4096 Nov 14 23:46 ..
drwxr-xr-x 3 root root 4096 Nov 15 04:15 data
drwxr-xr-x 2 root root 4096 Nov 15 04:15 reference
drwxr-xr-x 2 root root 4096 Nov 15 04:15 setup
drwxr-xr-x 2 root root 4096 Nov 15 04:15 work

/ba/reference:
total 8
drwxr-xr-x 2 root root 4096 Nov 15 04:15 .
drwxr-xr-x 6 root root 4096 Nov 15 04:15 ..

/data:
total 16
drwxr-xr-x 3 root root 4096 Nov 15 04:15 .
drwxr-xr-x 1 root root 4096 Nov 14 23:46 ..
drwxr-xr-x 4 root root 4096 Nov 13 08:46 baankafe
-rw-r--r-- 1 root root  213 Nov 15 04:15 split.json
dict_keys(['id', 'function', 'brief'])
Shell cwd was reset to /ba/work
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
        answer_files = []
        adir = os.path.join(root, "answers", tid)
        if os.path.isdir(adir):
            answer_files = ["answers/%s/%s" % (tid, n) for n in sorted(os.listdir(adir))
                            if os.path.isfile(os.path.join(adir, n))]
        tasks.append(Task(
            id=tid,
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=answer_files,
            grading={"key": tid, "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
cd /ba/reference && mkdir -p tasks answers
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /data/baankafe/tasks/$t.json tasks/; cp -r /data/baankafe/answers/$t answers/; done
find /ba/reference -type f
cd /ba/setup && python3 -c "
import plugin_benchmark" 2>/dev/null; python3 -c "
import benchmark_plugin as b
for t in b.list_tasks('/data/baankafe'): print(t.id,t.split,t.answer_files,t.grading)"
```

ผลที่ได้:

```
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
t1-cafe-bill train ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] {'key': 't1-cafe-bill', 'function': 'cafe_bill'}
t2-split-bill train ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] {'key': 't2-split-bill', 'function': 'split_bill'}
t3-shipping-fee train ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] {'key': 't3-shipping-fee', 'function': 'shipping_fee'}
t4-cashback train ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] {'key': 't4-cashback', 'function': 'cashback'}
v1-parking-fee validation ['answers/v1-parking-fee/solve.py', 'answers/v1-parking-fee/test_s
…(ตัด 631 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cd /ba/reference; grep -rlE "v1-|v2-|x1-|x2-|x3-|parking|net_pay|late_fee|refund|bulk" . ; echo done
```

ผลที่ได้:

```
done
Shell cwd was reset to /ba/work
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ผมรัน `list_tasks('/data/baankafe')` แล้วได้โจทย์ครบ 9 ข้อ แบ่งเป็น train 4, validation 2 และ test 3 ตรงกับ `/data/split.json` แต่ไม่ได้รัน `benchmark_grader.py` ตามที่ระบุว่า loop เป็นผู้รัน

**`benchmark_plugin.py`**
- การแบ่งชุดฝังอยู่ในไฟล์เอง
- `list_tasks(root)` อ่านเฉพาะ `root/tasks/<id>.json` และ `root/answers/<id>/` แล้วสร้าง `Task` 1 ตัวต่อโจทย์ ใช้เฉพาะ standard library กับ `plugin_api`
- แต่ละ `Task` มี `instruction` เป็น `brief`, `inputs` ว่าง และ `answer_files` เป็น `solve.py` กับ `test_solve.py` ของโจทย์นั้น
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่านแค่ `key` ส่วน `function` ใส่ไว้เฉยๆ

**`/ba/reference/`**
- มี `tasks/*.json` และ `answers/*/` ของโจทย์ train ทั้ง 4 ข้อ (`t1-cafe-bill`, `t2-split-bill`, `t3-shipping-fee`, `t4-cashback`) โครงโฟลเดอร์ตรงกับ data root
- ไม่มีอะไรของ validation หรือ test และไม่มีตัวตรวจ
- ผม grep หาชื่อโจทย์และคำเฉพาะของ validation กับ test แล้วไม่พบ
- ผมไม่ได้คัดลอก `split.json` เพราะมีรายชื่อโจทย์ validation และ test
