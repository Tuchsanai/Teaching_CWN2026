# Benchmark Adaptor

### ขั้น 1 · Bash

```
cd /ba/setup; ls -la; cat plugin_api.py plugin_skeleton.py benchmark_grader.py; echo ----; cat /data/split.json; find /data -type f | head -100
```

ผลที่ได้:

```
total 36
drwxr-xr-x 2 root root  4096 Nov 13 10:31 .
drwxr-xr-x 6 root root  4096 Nov 13 10:31 ..
-rwxr-xr-x 1 root root 20223 Nov 13 10:31 benchmark_grader.py
-rw-r--r-- 1 root root  1667 Nov 13 10:31 plugin_api.py
-rw-r--r-- 1 root root   560 Nov 13 10:31 plugin_skeleton.py
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
…(ตัด 20585 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /data/baankafe; cat tasks/t1-cafe-bill.json; echo; python3 -c "
import json,glob
for f in sorted(glob.glob('tasks/*.json')):
    d=json.load(open(f)); print(f,list(d), d['id'], d['function'])
"; ls -la /ba /ba/reference 2>&1
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
tasks/t1-cafe-bill.json ['id', 'function', 'brief'] t1-cafe-bill cafe_bill
tasks/t2-split-bill.json ['id', 'function', 'brief'] t2-split-bill split_bill
tasks/t3-shipping-fee.json ['id', 'function', 'brief'] t3-shipping-fee shipping_fee
tasks/t4-cashback.json ['id', 'function', 'brief'] t4-cashback cashback
tasks/v1-parking-fee.json ['id', 'function', 'brief'] v1-parking-fee parking_fee
tasks/v2-net-pay.json ['id', 'function', 'brief'] v2-net-pay net_pay
tasks/x1-late-fee.json ['id', 'function', 'brief'] x1-late-fee late_fee
tasks/x2-refund.json ['id', 'function', 'brief'] x2-refund refund
tasks/x3-bulk-price.json ['id', 'function', 'brief'] x3-bulk-price bulk_price
/ba:
total 24
drwxr-xr-x 6 root root 4096 Nov 13 10:31 .
drwxr-xr-x 1 root root 4096 Nov 13 08:52 ..
drwxr-xr-x 3 root ro
…(ตัด 312 ตัวอักษร)
```

### ขั้น 3 · Bash

```
mkdir -p /ba/reference/baankafe/tasks /ba/reference/baankafe/answers
cd /data/baankafe
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp tasks/$t.json /ba/reference/baankafe/tasks/; cp -r answers/$t /ba/reference/baankafe/answers/; done
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py - BaanKafe (โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ)

data root: tasks/<id>.json (id, function, brief) และ answers/<id>/{solve.py,test_solve.py}
"""
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
        # เฉลยอ้างอิงเปิดให้เฉพาะชุด train
        answers = []
        if split == "train":
            answers = ["answers/%s/solve.py" % tid, "answers/%s/test_solve.py" % tid]
        tasks.append(Task(
            id=d["id"],
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=answers,
            grading={"key": d["id"], "function": d["function"]},
            category="coding",
        ))
    return tasks
EOF
cd /ba/setup && python3 -I -c "
import sys; sys.path.insert(0,'.')
import benchmark_plugin as b
ts=b.list_tasks('/data/baankafe')
import os
for t in ts: print(t.id,t.split,t.answer_files, all(os.path.isfile('/data/baankafe/'+a) for a in t.answer_files))
"
# grader sanity: reference answers should score 1.0
python3 - <<'EOF'
import sys,json,shutil,tempfile
sys.path.insert(0,'/ba/setup')
import benchmark_grader as g
for t in ['t1-cafe-bill','v1-parking-fee','x3-bulk-price']:
    task=json.load(open(f'/data/baankafe/tasks/{t}.json')); task['grading']={'key':t}
    print(t,g.grade(task,f'/data/baankafe/answers/{t}'))
EOF
find /ba/reference -type f; grep -rl -E "parking|net-pay|late|refund|bulk" /ba/reference
```

ผลที่ได้:

```
t1-cafe-bill train ['answers/t1-cafe-bill/solve.py', 'answers/t1-cafe-bill/test_solve.py'] True
t2-split-bill train ['answers/t2-split-bill/solve.py', 'answers/t2-split-bill/test_solve.py'] True
t3-shipping-fee train ['answers/t3-shipping-fee/solve.py', 'answers/t3-shipping-fee/test_solve.py'] True
t4-cashback train ['answers/t4-cashback/solve.py', 'answers/t4-cashback/test_solve.py'] True
v1-parking-fee validation [] True
v2-net-pay validation [] True
x1-late-fee test [] True
x2-refund test [] True
x3-bulk-price test [] True
t1-cafe-bill 1.0
v1-parking-fee 1.0
x3-bulk-price 1.0
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
/ba/reference/baankafe/answer
…(ตัด 26 ตัวอักษร)
```

### ขั้น 4 · Bash

```
grep -rn -E "parking|net-pay|late|refund|bulk" /ba/reference | head
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน `/ba/setup/benchmark_plugin.py` และเติม `/ba/reference/` เสร็จแล้ว ทดสอบแล้วทำงานได้

- **plug-in:** `list_tasks(root)` คืน `Task` 9 ตัวตามการแบ่งชุดที่ให้มา คือ train 4 ข้อ, validation 2 ข้อ และ test 3 ข้อ
  - ผมอ่านข้อความโจทย์จาก `tasks/<id>.json`
  - `grading` เป็น `{"key": id, "function": ...}` ตรงกับที่ตัวตรวจอ่าน
  - `answer_files` ใส่ให้เฉพาะโจทย์ train (`solve.py` กับ `test_solve.py`) ส่วนโจทย์ validation และ test เว้นว่างไว้
- **ที่ทดสอบ:** รัน plug-in กับ `/data/baankafe` แล้ว path ของเฉลยทุกไฟล์มีอยู่จริง ส่วนตัวตรวจ ผมลองให้คะแนนเฉลยอ้างอิงของ `t1-cafe-bill`, `v1-parking-fee` และ `x3-bulk-price` ได้ 1.0 ทั้งสามข้อ
- **`/ba/reference/`:** มีเฉพาะ `baankafe/tasks/` กับ `baankafe/answers/` ของโจทย์ train 4 ข้อ (`t1`–`t4`) โดยคงโครงเดิมไว้
  - ผมไม่ได้คัดลอก `split.json` เพราะมันบอกว่าข้อไหนเป็น validation หรือ test
  - ผมไม่ได้คัดลอกตัวตรวจ และไม่มีไฟล์ของโจทย์ validation หรือ test อยู่ในโฟลเดอร์นี้เลย (ตรวจด้วย `find` แล้ว)
