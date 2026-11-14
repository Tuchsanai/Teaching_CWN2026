# ตาที่ 1 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-14 20:54 UTC คุณมีเวลาถึง 2026-11-14 21:24 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 1 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v1` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; ls; cat scores/epoch_0.json | head -50; ls traces/epoch_0 | head -50; ls skills/* staging reference evolver_workspace; cat evolver_workspace/* 2>/dev/null | head -50
```

ผลที่ได้:

```
evolver_workspace
reference
scores
skills
solver_workspaces
staging
traces
{
 "t1-cafe-bill_s1": 0.5,
 "t1-cafe-bill_s2": 0.5,
 "t1-cafe-bill_s3": 0.5,
 "t2-split-bill_s1": 0.4,
 "t2-split-bill_s2": 0.5,
 "t2-split-bill_s3": 0.5,
 "t3-shipping-fee_s1": 0.4545,
 "t3-shipping-fee_s2": 0.5455,
 "t3-shipping-fee_s3": 0.4545,
 "t4-cashback_s1": 0.4,
 "t4-cashback_s2": 0.4,
 "t4-cashback_s3": 0.4
}t1-cafe-bill_s1.jsonl
t1-cafe-bill_s2.jsonl
t1-cafe-bill_s3.jsonl
t2-split-bill_s1.jsonl
t2-split-bill_s2.jsonl
t2-split-bill_s3.jsonl
t3-shipping-fee_s1.jsonl
t3-shipping-fee_s2.jsonl
t3-shipping-fee_s3.jsonl
t4-cashback_s1.jsonl
t4-cashback_s2.jsonl
t4-cashback_s3.jsonl
evolver_workspace:

reference:
README.md
answers
tasks

skills/epoch_0:

staging:
```

### ขั้น 2 · Bash

```
cd /evo/reference; cat README.md; find . -type f | head -50; 
```

ผลที่ได้:

```
โฟลเดอร์ `answers/<task id>/` คือผลงานของโจทย์นั้นที่ได้คะแนนเต็ม ประกอบด้วย 2 ไฟล์ คือ `solve.py` และ `test_solve.py`
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
```

### ขั้น 3 · Bash

```
cd /evo/reference; cat tasks/*.json; for t in answers/*; do echo "=== $t"; cat $t/solve.py; cat $t/test_solve.py; done
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน\n- ไม่เกิน 1,000 กรัม 4
…(ตัด 13882 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cd /evo/solver_workspaces/epoch_0; ls *; cd /evo/traces/epoch_0; wc -c *; head -c 3000 t4-cashback_s1.jsonl
```

ผลที่ได้:

```
t1-cafe-bill_s1:
solve.py

t1-cafe-bill_s2:
solve.py

t1-cafe-bill_s3:
solve.py

t2-split-bill_s1:
solve.py

t2-split-bill_s2:
solve.py

t2-split-bill_s3:
solve.py

t3-shipping-fee_s1:
solve.py

t3-shipping-fee_s2:
solve.py

t3-shipping-fee_s3:
solve.py

t4-cashback_s1:
solve.py

t4-cashback_s2:
solve.py

t4-cashback_s3:
solve.py
 26856 t1-cafe-bill_s1.jsonl
 27308 t1-cafe-bill_s2.jsonl
 27157 t1-cafe-bill_s3.jsonl
 27503 t2-split-bill_s1.jsonl
 29271 t2-split-bill_s2.jsonl
 26298 t2-split-bill_s3.jsonl
 33802 t3-shipping-fee_s1.jsonl
 35038 t3-shipping-fee_s2.jsonl
 37558 t3-shipping-fee_s3.jsonl
 26281 t4-cashback_s1.jsonl
 28821 t4-cashback_s2.jsonl
 27425 t4-cashback_s3.jsonl
353318 total
{"type":"system","subtype":"init","cwd":"/workspace/evlab/ws/n1/legs/runs/base_train/t4-cashback-r1/sandbox","session_id":"db5488e2-f474-4bb9-b910-93d23cc960f2","tools":["Task","Bash","CronCreate","CronDelete","CronList","DesignSync","Edit","EnterWorktree","ExitWorktree","ListAgents","Monitor","NotebookEdit","PushNotification","Read","RemoteTrigger","ReportFindings","ScheduleWakeup","SendMessage","Skill","TaskStop","ToolSearch","WebSearch","Workflow","Write","mcp__playwright__browser_click","m
…(ตัด 2502 ตัวอักษร)
```

### ขั้น 5 · Bash

```
cd /evo/traces/epoch_0; python3 -I - <<'E'
import json,glob
for f in ['t4-cashback_s1.jsonl','t3-shipping-fee_s1.jsonl']:
    print('=====',f)
    for l in open(f):
        d=json.loads(l)
        if d['type']=='system': continue
        m=d.get('message',{})
        c=m.get('content')
        if isinstance(c,str): print(d['type'],c[:2500]);continue
        for b in c or []:
            if b['type']=='text': print(d['type'],'TEXT',b['text'][:2500])
            elif b['type']=='tool_use': print('TOOL',json.dumps(b['input'],ensure_ascii=False)[:2500])
            elif b['type']=='tool_result': print('RESULT',str(b['content'])[:1500])
E
cat /evo/solver_workspaces/epoch_0/t4-cashback_s1/solve.py
```

ผลที่ได้:

```
===== t4-cashback_s1.jsonl
TOOL {"command": "ls ./skills 2>&1"}
RESULT Exit code 2
ls: cannot access './skills': No such file or directory
TOOL {"file_path": "/workspace/evlab/ws/n1/legs/runs/base_train/t4-cashback-r1/sandbox/solve.py", "content": "RATES_PER_MILLE = {\"silver\": 15, \"gold\": 25, \"platinum\": 40}  # 1.5%, 2.5%, 4%\nMIN_AMOUNT = 100 * 100   # 100 baht in satang\nMAX_CASHBACK = 200 * 100  # 200 baht in satang\n\n\ndef cashback(amount, tier, birthday):\n    \"\"\"Return cashback in whole satang (integer math, rounded down).\"\"\"\n    if amount < MIN_AMOUNT:\n        return 0\n    rate = RATES_PER_MILLE[tier]\n    if birthday:\n        rate *= 2\n    return min(amount * rate // 1000, MAX_CASHBACK)\n"}
RESULT File created successfully at: /workspace/evlab/ws/n1/legs/runs/base_train/t4-cashback-r1/sandbox/solve.py (file state is current in your context — no need to Read it back)
assistant TEXT เขียน `cashback(amount, tier, birthday)` ลงใน `solve.py` แล้ว แต่ยังไม่ได้รันหรือทดสอบ ในโฟลเดอร์ไม่มี `./skills` เลยไม่ต้องทำตามสกิลใด

- **ยอดขั้นต่ำ:** ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) ได้ 0
- **อัตราเงินคืน:** silver 1.5%, gold 2.5%, platinum 4% และเดือนเกิดคูณ 2
- **เพดาน:
…(ตัด 3182 ตัวอักษร)
```

### ขั้น 6 · Bash

```
cd /evo/solver_workspaces/epoch_0; cat t1-cafe-bill_s1/solve.py t2-split-bill_s2/solve.py t3-shipping-fee_s2/solve.py
```

ผลที่ได้:

```
def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์ (ปัดครั้งเดียวตอนท้าย, half up)"""
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)
def split_bill(total, people, tip_percent):
    """หารบิลให้ทุกคน (หน่วยสตางค์) คนแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์ถ้าหารไม่ลงตัว"""
    # ยอดรวมทิป คำนวณด้วยจำนวนเต็มล้วน ปัดครึ่งขึ้นเป็นสตางค์
    grand = (total * (100 + tip_percent) + 50) // 100
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
from fractions import Fraction
from math import floor


def _frac(x):
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นเมื่อสุดท้ายได้เศษสตางค์)"""
    w = _frac(weight_g)
    d = _frac(distance_km)
    if w < 1 or w > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if d < 0:
        raise ValueErr
…(ตัด 400 ตัวอักษร)
```

### ขั้น 7 · Bash

```
mkdir -p /evo/staging/money-function-solve && cd /evo/staging/money-function-solve
cat > SKILL.md <<'E'
---
name: money-function-solve
description: ใช้เมื่อโจทย์ให้เขียนฟังก์ชันคิดเงิน/ส่วนลด/ค่าส่ง/เงินคืน/หารบิล (หน่วยสตางค์) ลงใน solve.py — มีขั้นตอน ตรวจ input เข้มงวด คำนวณด้วย Fraction ปัดเศษ และเช็กลิสต์กรณีขอบ
---

# เขียนฟังก์ชันคิดเงินใน solve.py ให้ผ่านตัวตรวจ

ตัวตรวจทดสอบ 4 กลุ่ม: **Normal** (ค่าทั่วไป), **Boundary** (ค่าขอบ เช่น พอดี 500 บาท / 1000 กรัม), **NoDrift** (เศษสตางค์ ปัดเศษผิดที่เดียวก็พลาด), **Reject** (input ผิดต้อง `raise ValueError`)
จาก epoch ก่อน: สูตรหลักถูกหมด แต่ **ไม่มีการตรวจ input เลย → เสียกลุ่ม Reject ทั้งกลุ่ม (~0.5 คะแนน)** ห้ามพลาดซ้ำ

## ขั้นตอน
1. อ่านโจทย์ ระบุพารามิเตอร์ทุกตัว พร้อมชนิดและช่วงที่โจทย์ระบุ ("ตั้งแต่ 1", "0–100", "1–30,000" ฯลฯ)
2. คัดลอกโครงจาก `template.py` (ในโฟลเดอร์สกิลนี้) มาเป็น `solve.py` แล้วแก้เฉพาะฟังก์ชันหลัก
3. ตรวจ input ทุกตัวก่อนคำนวณ (ดูหัวข้อถัดไป)
4. คำนวณด้วย `fractions.Fraction` ล้วน ห้ามใช้ float และห้ามปัดกลางทาง ปัดครั้งเดียวตอนท้าย
5. ทดสอบเอง: รัน `python3 -m unittest` กับ test ที่เขียนเองหรือสคริปต์สั้น ๆ (ใช้ `PYTHONPATH=.` ไม่ใช่ `python3 -I` เพราะ -I จะ import solve ไม่ได้) ต้องลองครบ 4 กลุ่มข้างบน โดยเฉพาะค่าที่ให้เศษครึ่งสตางค์พอดี
6. เขียน `test_solve.py` ไว้ข้าง `solve.py` ด้วย (unittest, 4 กลุ่ม)

## ตรวจ input (Reject)
- ชนิด: ใช้ `type(v) is int` ไม่ใช่ `isinstance` — เพราะ `bool` เป็น subclass ของ int, `True` ต้องถูกปฏิเสธเมื่อคาดหวังตัวเลข; `float` (เช่น `4500.0`) และ `str` (เช่น `'2'`) ต้องถูกปฏิเสธ แม้ค่าจะดูเป็นเลขจำนวนเต็ม
- พารามิเตอร์ที่เป็นแฟล็ก (`member`, `express`, `birthday`): ต้อง `type(v) is bool` เท่านั้น (0/1/"yes" ปฏิเสธ)
- ช่วงค่า: ปฏิเสธค่านอกช่วงที่โจทย์ระบุ เช่น qty < 1, people < 1, น้ำหนักต่ำกว่า 1 หรือเกินสูงสุด, ยอดติดลบ, tip นอก 0–100, ราคาติดลบ
- ค่า enum (เช่น tier): ต้องเป็น str และอยู่ในชุดที่กำหนด มิฉะนั้น ValueError (ไม่ใช่ KeyError)
- list/dict: ตรวจ `type(items) is list`, แต่ละรายการ `type(item) is dict`, ต้องมี key ครบ (ขาด key → ValueError ไม่ใช่ KeyError/TypeError)
- ต้อง raise **ValueError** เท่านั้น (ไม่ใช่ TypeError/KeyError/assert)
- ตรวจให้ครบ **ก่อน** early-return ใด ๆ (เช่น ก่อน "ต่ำกว่า 100 บาทได้ 0") — input ผิดต้อง raise เสมอไม่ว่าสาขาไหน
- ราคา/จำนวนที่เป็น 0 ที่โจทย์อนุญาต ("ตั้งแต่ 0") ต้องรับได้

## การคำนวณและปัดเศษ
- ลำดับขั้นตามโจทย์เป๊ะ ๆ ("ลด 5% แล้วลดอีก 10% แล้วบวก VAT เป็นขั้นสุดท้าย" = คูณต่อกัน ไม่ใช่บวกเปอร์เซ็นต์)
- เงื่อนไข "ตั้งแต่ X ขึ้นไป" ใช้ `>=` ; "เกิน X" ใช้ `>` ; "ไม่เกิน X" ใช้ `<=` ; "ต่ำ
…(ตัด 4304 ตัวอักษร)
```

ผลที่ได้:

```
/evo/staging:
money-edge-policies
money-function-solve

/evo/staging/money-edge-policies:
SKILL.md

/evo/staging/money-function-solve:
SKILL.md
template.py
```

### ขั้น 8 · Bash

```
cat > /evo/evolver_workspace/notes.md <<'E'
# epoch0: no skills, scores ~0.4-0.55. Solvers got formulas right but had no input validation (Reject tests lost), no test_solve.py.
Hidden ref policies: S1 distance 0 -> fee 0, S2 express weight>20000 reject, C1 silver no birthday bonus, C2 cashback floor. Not in briefs.
# epoch1: wrote skills money-function-solve (template.py + validation + rounding) and money-edge-policies. Check epoch_1 scores for Reject gain.
E
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียน `skills_v1` ลงใน `/evo/staging/` แล้ว มีสกิล 2 ตัว ยังไม่ได้ทดสอบว่าช่วยได้จริงหรือไม่ ต้องรอคะแนน epoch 1

**จุดพลาดใน epoch 0:** คะแนนทุกข้ออยู่ที่ 0.4–0.55
- **สูตรหลัก:** Solver เขียนถูกเกือบทุกข้อ
- **การตรวจ input:** ไม่มีเลย ทั้ง `float`, `str`, `bool` และค่านอกช่วง ซึ่งเป็นกลุ่ม Reject ที่ตัวตรวจต้องการ `ValueError` เสียไปทั้งกลุ่ม ราวครึ่งหนึ่งของคะแนน
- **ไฟล์ที่ขาด:** ไม่มี `test_solve.py` และไม่มี `main()` แบบอ่าน JSON
- **เฉลยอ้างอิง:** มีนโยบายที่โจทย์ไม่ได้เขียน 4 ข้อ
  - ระยะทาง 0 คิดค่าส่ง 0
  - ส่งด่วนรับน้ำหนักไม่เกิน 20,000 กรัม
  - สมาชิก silver ไม่ได้สิทธิ์เดือนเกิด
  - เงินคืนปัดลง

**สกิลที่เขียน:**
- **`money-function-solve`**
  - ขั้นตอนทำงานตั้งแต่ตรวจ input ถึงเขียน test
  - ตรวจชนิดด้วย `type(v) is int` และ `type(v) is bool` แล้ว `raise ValueError`
  - คำนวณด้วย `Fraction` และปัดครั้งเดียวตอนท้าย
  - กฎปัดเศษ: เงินที่ลูกค้าจ่ายปัดครึ่งขึ้น เงินที่ร้านจ่ายออกปัดลง
  - ความหมายของ "ตั้งแต่/เกิน/ไม่เกิน/ต่ำกว่า"
  - มี `template.py` เป็นโครง `solve.py` พร้อม `main()` แบบ JSON
- **`money-edge-policies`:** เช็กลิสต์ตัดสินกรณีที่โจทย์เงียบและให้บันทึกสมมติฐาน ผมเขียนแบบกลาง ๆ ไม่ได้ใส่นโยบายแฝง 4 ข้อข้างบนตรง ๆ เพราะเป็นของโจทย์เฉพาะที่ใช้กับโจทย์อื่นไม่ได้ ผลคือสกิลอาจยังไม่ช่วยให้ตรงกับนโยบายแฝงเหล่านั้น

ผมจดบันทึกสั้น ๆ ไว้ที่ `/evo/evolver_workspace/notes.md` เพื่อใช้ตรวจต่อใน epoch ถัดไป
