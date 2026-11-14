# Benchmark Adaptor

### ขั้น 1 · Bash

```
cat /ba/setup/plugin_api.py /ba/setup/plugin_skeleton.py; ls -R /ba /data | head -80; cat /data/split.json
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
…(ตัด 2660 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /ba/data/baankafe/tasks; for f in *.json; do echo "== $f"; cat $f; echo; done; echo; cat /ba/setup/benchmark_grader.py | head -60; ls -la /data /ba/data
```

ผลที่ได้:

```
== t1-cafe-bill.json
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
== t2-split-bill.json
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}
== t3-shipping-fee.json
{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะ
…(ตัด 6061 ตัวอักษร)
```

### ขั้น 3 · Bash

```
sed -n 60,400p /ba/setup/benchmark_grader.py | grep -n -E "task|key|grading|def " | head -60
```

ผลที่ได้:

```
9:def o_parking_fee(minutes, member):
19:def o_net_pay(hours, rate, has_sso):
26:def o_late_fee(amount, days_late):
32:def o_refund(paid, used_percent, restock):
41:def o_bulk_price(unit_price, qty, coupon):
52:def it(*pq):
187:def is_int(v):
207:def run_cases(sb, rdir, func, cases):
229:def show(args):
233:def cli(sb, payload):
241:def explain(task, snapshot):
245:        return _checks(task, sb, rdir)
250:def grade(task, snapshot):
252:    checks = explain(task, snapshot)
256:def _checks(task, sb, rdir):
257:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
260:    def add(cid, ok, note=""):
```

### ขั้น 4 · Bash

```
sed -n 295,420p /ba/setup/benchmark_grader.py | grep -n "task\[" ; grep -n 'task\[\|task.get\|T\[' /ba/setup/benchmark_grader.py | head -20
```

ผลที่ได้:

```
22:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
316:    T = TASKS[(task.get("grading") or {}).get("key") or task["id"]]
328:                c["exp"] = T["oracle"](*a)
336:    res = run_cases(sb, rdir, T["func"], cases) if have else {"import_error": "ไม่มีไฟล์ solve.py", "results": []}
341:        add("contract", False, "ใช้ฟังก์ชัน %s ไม่ได้: %s" % (T["func"], err))
355:            T["func"], show(bad[0][0]["args"])[1:-1], bad[0][0]["exp"], bad[0][1].get("value") or bad[0][1].get("exc"),
365:            T["func"], show(bad[0][0]["args"])[1:-1],
371:    for a in T["cli_ok"] if have else []:
372:        exp = T["oracle"](*a)
373:        rc, out, _ = cli(sb, json.dumps(dict(zip(T["args"], a))))
380:                show(dict(zip(T["args"], a))), json.dumps(exp), rc, out[:120] or "(ว่าง)")
386:    for payload in ([json.dumps(dict(zip(T["args"], T["cli_err"]))), "{bad json"] if have else []):
429:            for (a, exp), i in zip(T["policy"], index["policy"]):
439:                    T["func"], show(a)[1:-1], want, got, len(bad), len(T["policy"])))
```

### ขั้น 5 · Bash

```
cat > /ba/setup/benchmark_plugin.py <<'EOF'
"""benchmark_plugin.py : BaanKafe (โจทย์เขียนฟังก์ชันคิดเงิน 9 ข้อ)"""
import json
import os

from plugin_api import Task

# การแบ่งชุด ตรงกับ split.json ของผู้ใช้ (train 4 · validation 2 · test 3)
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
            d = json.load(f)
        tasks.append(Task(
            id=task_id,
            split=split,
            instruction=d["brief"],
            inputs=[],
            answer_files=[
                "answers/%s/solve.py" % task_id,
                "answers/%s/test_solve.py" % task_id,
            ],
            grading={"key": task_id, "function": d.get("function", "")},
            category="billing",
        ))
    return tasks
EOF
mkdir -p /ba/reference/tasks
for t in t1-cafe-bill t2-split-bill t3-shipping-fee t4-cashback; do cp /ba/data/baankafe/tasks/$t.json /ba/reference/tasks/; done
cat > /ba/reference/README.md <<'EOF'
# BaanKafe benchmark

โจทย์เขียนโค้ดคิดเงินของร้านกาแฟ BaanKafe · 1 โจทย์ให้ Solver เขียนฟังก์ชัน Python 1 ฟังก์ชันตามข้อความโจทย์ (`brief`)

- Solver ได้เฉพาะข้อความ `brief` ของโจทย์นั้น และเริ่มจากโฟลเดอร์ทำงานว่าง ๆ
- Solver บันทึกไฟล์ผลงาน (เช่น `solve.py`) ไว้ในโฟลเดอร์ทำงานนั้น
- `tasks/<task id>.json` = โจทย์ชุด train ที่ Evolver ใช้เป็นหลักฐาน มี `id` · `function` (ชื่อฟังก์ชันที่ต้องเขียน) · `brief` (ข้อความโจทย์ที่ Solver ได้รับ)

สกิลที่เขียนควรเป็นแนวทางทั่วไปสำหรับโจทย์คิดเงินแบบนี้ ไม่ผูกกับโจทย์ข้อใดข้อหนึ่ง
EOF
cd /ba/work && cp /ba/setup/plugin_api.py . && python3 -I - <<'EOF'
import sys; sys.path.insert(0,'/ba/setup')
import benchmark_plugin as b, collections
ts=b.list_tasks('/ba/data/baankafe')
print(collections.Counter(t.split for t in ts), len({t.id for t in ts}), all(t.instruction.strip() for t in ts))
import json; sp=json.load(open('/ba/data/split.json'))
print(all(sp[t.split].count(t.id)==1 for t in ts), sum(map(len,sp.values())))
EOF
rm -f /ba/work/plugin_api.py; rm -rf /ba/setup/__pycache__
grep -rniE "v1|v2|x1|x2|x3|parking|net-pay|net_pay|late|refund|bulk|grader" /ba/reference; ls -R /ba/reference /ba/setup
```

ผลที่ได้:

```
Counter({'train': 4, 'test': 3, 'validation': 2}) 9 True
True 9
/ba/reference:
README.md
tasks

/ba/reference/tasks:
t1-cafe-bill.json
t2-split-bill.json
t3-shipping-fee.json
t4-cashback.json

/ba/setup:
benchmark_grader.py
benchmark_plugin.py
plugin_api.py
plugin_skeleton.py
```

**Agent พูด:** Plug-in และ `/ba/reference/` เสร็จแล้ว ตรวจผ่านทั้งหมด

**Plug-in** (`/ba/setup/benchmark_plugin.py`)
- รันจริงแล้ว 1 ครั้ง ได้ train 4 · validation 2 · test 3 รวม 9 ข้อ ตรงกับ `split.json` ทุกข้อ
- id ไม่ซ้ำ และ `instruction` ของทุกข้อไม่ว่าง
- ตารางการแบ่งชุดเขียนไว้ในไฟล์เอง
- `grading` ใส่ `{"key": <id>, "function": <ชื่อฟังก์ชัน>}` ตัวตรวจอ่าน `grading["key"]` หรือ `id` อยู่แล้ว
- `answer_files` ชี้ไปที่ `answers/<id>/solve.py` และ `test_solve.py`
- ไม่ได้แก้ตัวตรวจ และลบไฟล์ทดลองใน `/ba/setup/` ออกแล้ว

**ใน `/ba/reference/`**
- `tasks/` มี JSON ของโจทย์ชุด train 4 ข้อ (id, ชื่อฟังก์ชัน, brief)
- `README.md` อธิบายภาพรวมของ benchmark สั้น ๆ โดยไม่เอ่ยถึงชุด validation, test หรือตัวตรวจ
- ค้นหา id ของ validation และ test รวมถึงชื่อฟังก์ชัน คำว่า grader และคำอธิบายการตรวจ ไม่พบเลย

**ตั้งใจไม่ใส่**
- `answers/` ทั้งหมด รวมของ train ตามที่คุณสั่ง
- โจทย์ validation และ test ทุกส่วน
- `split.json` เพราะรวมรายชื่อทุกชุด
- `benchmark_grader.py` และคำอธิบายว่าตัวตรวจให้คะแนนอย่างไร

**หมายเหตุ**
- คุณระบุ data root เป็น `/data/baankafe` แต่ในเครื่องมีสำเนาอยู่ที่ `/ba/data/baankafe` ด้วย ผมอ่านจาก `/ba/data/baankafe`
- plug-in รับ `root` เป็นพารามิเตอร์ จึงใช้ได้กับทั้งสอง path
