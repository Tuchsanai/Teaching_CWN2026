# ตาที่ 1 ของ Evolver

ข้อความที่ได้รับ: เวลาตอนนี้ 2026-11-14 23:13 UTC · เส้นตายของตานี้ 2026-11-14 23:43 UTC เมื่อถึงเส้นตาย สิ่งที่อยู่ใน `/evo/staging/` จะถูกนำไปใช้ทันทีตามสภาพขณะนั้น · นี่คือ epoch 1 · ผลการทำโจทย์รอบล่าสุดของ Solver อยู่ใน `/evo` แล้ว ขอให้วิเคราะห์ rollout เหล่านั้น วินิจฉัยว่า Solver พลาดตรงไหนที่สกิลช่วยแก้ได้ แล้วเขียนชุดสกิล `skills_v1` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; ls; ls reference staging evolver_workspace skills/*; ls traces/epoch_0 | head -50; cat scores/epoch_0.json | head -50
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
evolver_workspace:

reference:
README.md
train_tasks

skills/epoch_0:

staging:
t1-cafe-bill_s1.jsonl
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
{
 "t1-cafe-bill_s1": 0.5,
 "t1-cafe-bill_s2": 0.5,
 "t1-cafe-bill_s3": 0.5,
 "t2-split-bill_s1": 0.5,
 "t2-split-bill_s2": 0.5,
 "t2-split-bill_s3": 0.6,
 "t3-shipping-fee_s1": 0.4545,
 "t3-shipping-fee_s2": 0.4545,
 "t3-shipping-fee_s3": 0.5455,
 "t4-cashback_s1": 0.4,
 "t4-cashback_s2": 0.4,
 "t4-cashback_s3": 0.4
}
```

### ขั้น 2 · Bash

```
cd /evo/reference; cat README.md; find train_tasks | head -50
```

ผลที่ได้:

```
# BaanKafe benchmark (ข้อมูลสำหรับ Evolver)

โจทย์เขียนโค้ดคิดเงินของร้านกาแฟ BaanKafe: ต่อ 1 โจทย์ Solver ต้องเขียนฟังก์ชัน Python 1 ฟังก์ชัน
ตามข้อความโจทย์ (`brief`) ลงในไฟล์ `solve.py` โดย Solver เริ่มจากโฟลเดอร์ทำงานว่าง ๆ
และบันทึกไฟล์ผลงานไว้ในโฟลเดอร์ทำงานนั้น

โจทย์ชุด train อยู่ใน `train_tasks/<task id>.json` แต่ละไฟล์มี `id`, `function` (ชื่อฟังก์ชัน)
และ `brief` (ข้อความโจทย์ที่ Solver ได้รับ)
train_tasks
train_tasks/t3-shipping-fee.json
train_tasks/t4-cashback.json
train_tasks/t1-cafe-bill.json
train_tasks/t2-split-bill.json
```

### ขั้น 3 · Bash

```
cd /evo/reference/train_tasks; for f in *; do cat $f; echo; done; ls /evo/solver_workspaces/epoch_0/*
```

ผลที่ได้:

```
{
 "id": "t1-cafe-bill",
 "function": "cafe_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน\n- `items` = list ของ dict `{\"price\": ราคาต่อชิ้น (สตางค์), \"qty\": จำนวนชิ้น (ตั้งแต่ 1)}`\n- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%\n- `member` = True ลดอีก 10%\n- บวก VAT 7% เป็นขั้นสุดท้าย\n- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์"
}
{
 "id": "t2-split-bill",
 "function": "split_bill",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล\n- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)\n- ยอดที่ต้องหาร = ยอดบิลบวกทิป\n- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ\n- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน"
}
{
 "id": "t3-shipping-fee",
 "function": "shipping_fee",
 "brief": "ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ\n- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน\n- ไม่เกิน 1,000 กรัม
…(ตัด 1439 ตัวอักษร)
```

### ขั้น 4 · Bash

```
cd /evo/solver_workspaces/epoch_0; for d in *; do echo "=== $d"; cat $d/solve.py; done
```

ผลที่ได้:

```
=== t1-cafe-bill_s1
def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = total, 1
    if total >= 50000:  # 500 baht
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (2 * num + den) // (2 * den)  # round half up, exact integer math
=== t1-cafe-bill_s2
def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่าย (สตางค์, int) คำนวณด้วยจำนวนเต็มล้วน ปัดครั้งเดียวตอนท้าย (half up)"""
    total = sum(i["price"] * i["qty"] for i in items)  # สตางค์
    num, den = total, 1
    if total >= 50000:  # 500 บาท
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7%
    return (2 * num + den) // (2 * den)
=== t1-cafe-bill_s3
def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    num, den = 1, 1
    if total >= 50000:      # 500 baht
        num *= 95; den *= 100
    if member:
        num *= 90; den *= 100
    num *= 107; den *= 100  # VAT last
    # exact integer arithmetic, round half up once at the end
    return (total * num *
…(ตัด 4629 ตัวอักษร)
```

### ขั้น 5 · Bash

```
cd /evo/traces/epoch_0; wc -c *; python3 -I -c "
import json
for l in open('t1-cafe-bill_s1.jsonl'):
    d=json.loads(l); print(str(d)[:1500]); print()
"
```

ผลที่ได้:

```
 26707 t1-cafe-bill_s1.jsonl
 30475 t1-cafe-bill_s2.jsonl
 26561 t1-cafe-bill_s3.jsonl
 26551 t2-split-bill_s1.jsonl
 26236 t2-split-bill_s2.jsonl
 27825 t2-split-bill_s3.jsonl
 27208 t3-shipping-fee_s1.jsonl
 26802 t3-shipping-fee_s2.jsonl
 38016 t3-shipping-fee_s3.jsonl
 27267 t4-cashback_s1.jsonl
 26965 t4-cashback_s2.jsonl
 33470 t4-cashback_s3.jsonl
344083 total
{'type': 'system', 'subtype': 'init', 'cwd': '/workspace/evlab/runs/p2/legs/runs/base_train/trials/t1-cafe-bill-r1/sandbox', 'session_id': 'ee0d265a-8202-457b-9160-46f51d834e4b', 'tools': ['Task', 'Bash', 'CronCreate', 'CronDelete', 'CronList', 'DesignSync', 'Edit', 'EnterWorktree', 'ExitWorktree', 'ListAgents', 'Monitor', 'NotebookEdit', 'PushNotification', 'Read', 'RemoteTrigger', 'ReportFindings', 'ScheduleWakeup', 'SendMessage', 'Skill', 'TaskStop', 'ToolSearch', 'WebSearch', 'Workflow', 'Write', 'mcp__playwright__browser_click', 'mcp__playwright__browser_close', 'mcp__playwright__browser_console_messages', 'mcp__playwright__browser_drag', 'mcp__playwright__browser_drop', 'mcp__playwright__browser_emulate_media', 'mcp__playwright__browser_evaluate', 'mcp__playwright__browser_file_upload', 'mcp__playwright__browser_
…(ตัด 9871 ตัวอักษร)
```

### ขั้น 6 · Bash

```
cd /evo/traces/epoch_0; python3 -I -c "
import json,sys
for f in ['t3-shipping-fee_s3','t4-cashback_s3','t2-split-bill_s3']:
  print('#####',f)
  for l in open(f+'.jsonl'):
    d=json.loads(l)
    if d.get('type')=='assistant':
      for c in d['message']['content']:
        if c['type']=='text': print('TEXT:',c['text'][:2500])
        if c['type']=='tool_use': print('TOOL:',json.dumps(c['input'],ensure_ascii=False)[:1500])
    if d.get('type')=='user':
      for c in d['message']['content']:
        if c['type']=='tool_result': print('RES:',str(c['content'])[:800])
"; ls /evo/scores
```

ผลที่ได้:

```
##### t3-shipping-fee_s3
TOOL: {"command": "ls ./skills 2>/dev/null && find ./skills -type f | head"}
RES: Exit code 2
TOOL: {"file_path": "/workspace/evlab/runs/p2/legs/runs/base_train/trials/t3-shipping-fee-r3/sandbox/solve.py", "content": "from fractions import Fraction\n\n\ndef shipping_fee(weight_g, distance_km, express):\n    \"\"\"คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณแบบเศษส่วนตรง ปัดครึ่งขึ้นตอนท้ายสุดครั้งเดียว)\"\"\"\n    if weight_g < 1 or weight_g > 30000:\n        raise ValueError(\"weight_g must be between 1 and 30000\")\n    if distance_km < 0:\n        raise ValueError(\"distance_km must be >= 0\")\n\n    w = Fraction(weight_g)\n    if w <= 1000:\n        fee = Fraction(4000)\n    elif w <= 5000:\n        fee = Fraction(8000)\n    else:\n        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม ตามสัดส่วนกรัม\n        fee = Fraction(8000) + (w - 5000) * 1500 / 1000\n\n    if distance_km > 100:\n        fee *= Fraction(120, 100)\n    if express:\n        fee *= Fraction(150, 100)\n\n    return int(fee + Fraction(1, 2) // 1) if fee.denominator == 1 else int((fee * 2 + 1) // 2)\n"}
RES: File created successfully at: /workspace/evlab/runs/p2/legs/runs/base_train/trials/t3-shipping-fee
…(ตัด 6031 ตัวอักษร)
```

### ขั้น 7 · Bash

```
mkdir -p /evo/staging/billing-function-solver /evo/evolver_workspace
cat > /evo/staging/billing-function-solver/SKILL.md <<'EOF'
---
name: billing-function-solver
description: ขั้นตอนเขียนฟังก์ชันคิดเงิน/ค่าส่ง/ส่วนลด/เงินคืน/หารบิลของร้าน BaanKafe ลง solve.py ให้ผ่านชุดทดสอบลับ — ใช้ทุกครั้งที่โจทย์ให้เขียนฟังก์ชัน Python ตามกติการาคา
---

# แนวทางเขียนฟังก์ชันคิดเงิน (solve.py)

ผลรอบก่อนพบว่าโค้ดที่ "คำนวณถูกตามตัวอย่าง" ยังได้แค่ ~0.5 เพราะชุดทดสอบลับตรวจมากกว่าแค่กรณีปกติ
ให้ทำตามลำดับนี้ทุกครั้ง

## 1. อ่านโจทย์ให้เป็นตารางกติกา (ก่อนเขียนโค้ด)
เขียนคอมเมนต์ลงต้นไฟล์สั้น ๆ ว่า: หน่วยของอินพุต/เอาต์พุต, ลำดับการคิดแต่ละขั้น, เงื่อนไขขอบ
- คำชี้ขอบเขต: "ตั้งแต่ X" = `>= X` · "เกิน X" = `> X` · "ไม่เกิน X" = `<= X` · "ต่ำกว่า X" = `< X`
- หน่วยเงิน: อินพุตเป็นสตางค์ แต่กติกาพูดเป็นบาท → แปลง (1 บาท = 100 สตางค์) ให้ถูกทุกค่าคงที่ (500 บาท = 50000)
- "คูณต่อจากข้อก่อน" = ทบกันตามลำดับ ไม่ใช่บวกเปอร์เซ็นต์รวม
- เงื่อนไข threshold (เช่น ยอดถึง 500 บาท) ให้ใช้ค่าตามที่โจทย์บอก (ยอดก่อนส่วนลดนั้น) อย่าใช้ยอดหลังหักอย่างอื่นเอง
- เพดาน/ขั้นต่ำ (cap/min) ใช้ตามลำดับที่โจทย์เรียง: ขั้นต่ำเช็กที่ยอดซื้อ, เพดานเช็กหลังคูณทุกอย่างแล้ว
- ขั้นตอนที่โจทย์บอกว่า "ขั้นสุดท้าย" (เช่น VAT) ต้องอยู่ท้ายสุดจริง

## 2. เลขต้องแม่นยำ ห้ามใช้ float
- ใช้จำนวนเต็มล้วน หรือ `fractions.Fraction` (เช่น 1.5% = 15/1000, 7% = 107/100) เสมอ
- ปัดเศษเป็นสตางค์ครั้งเดียวตอนท้าย (ผลลัพธ์ต้องเป็น `int` ของ Python ไม่ใช่ float/Fraction/bool)
- ค่าเริ่มต้นเมื่อโจทย์ไม่ระบุวิธีปัด: ปัดครึ่งขึ้น (half-up) ด้วย `(2*num + den) // (2*den)` กับค่าที่ไม่ติดลบ
  ใช้ `round()` ของ Python ไม่ได้ (เป็น banker's rounding)
- ข้อยกเว้น: ถ้าโจทย์พูดชัดเรื่องปัด ("ปัดลง", "ปัดเป็นสตางค์เต็ม", "คนแรก ๆ จ่ายเพิ่ม 1 สตางค์") ให้ทำตามนั้นเป๊ะ
- การหารที่ต้องแจกเศษ (หารบิล): ผลรวมของทุกคนต้องเท่ากับยอดที่ต้องหารพอดี (`divmod`, คนแรก ๆ ได้ +1)

## 3. ตรวจอินพุตตามช่วงที่โจทย์ระบุ (สำคัญ — ชุดทดสอบลับมีเคสอินพุตผิดปกติ)
- ในโจทย์จะมีช่วงที่ระบุไว้ เช่น "ตั้งแต่ 1", "0–100", "1–30,000 กรัม", "ตั้งแต่ 0", ค่าที่เลือกได้ได้แก่ "silver/gold/platinum"
  ถ้าอินพุตอยู่นอกช่วงหรือผิดชนิด ให้ `raise ValueError(...)` อย่าเงียบ ๆ คืนค่า, อย่า clamp, อย่าปล่อยให้เป็น KeyError/ZeroDivisionError
- ตรวจให้ครบทุกพารามิเตอร์ รวมถึงของในลิสต์ (เช่น แต่ละ item มี price ≥ 0 และ qty ≥ 1)
- ตรวจชนิด: ค่าเงิน/จำนวนต้องเป็น `int` (ปฏิเสธ `bool` และ float ที่ไม่ใช่จำนวนเต็มด้วย `ValueError`) ยกเว้นพารามิเตอร์ที่โจทย์ให้เป็นทศนิยมได้ เช่น ระยะทางกิโลเมตร (รับ int/float ที่ไม่ติดลบ)
- พารามิเตอร์ flag (member/express/birthday) ต้องเป็น bo
…(ตัด 1681 ตัวอักษร)
```

ผลที่ได้:

```
(Bash completed with no output)
```

**Agent พูด:** ผมเขียนสกิล `skills_v1` ลง `/evo/staging/billing-function-solver/SKILL.md` แล้ว แต่ยังไม่ได้ทดสอบกับ Solver และไม่รู้ว่าชุดทดสอบลับตรวจอะไรบ้าง

**ที่พบจาก epoch 0**
- ทั้ง 12 ครั้งได้ 0.4–0.6 โค้ดที่ Solver เขียนเกือบเหมือนกันหมด คือใช้เลขแม่นยำ ปัดเศษครั้งเดียวตอนท้าย และ t4 ปัดลง
- สองครั้งที่ได้คะแนนสูงกว่าเพื่อนคือ `t2-split-bill_s3` (0.6 เทียบกับ 0.5) และ `t3-shipping-fee_s3` (0.5455 เทียบกับ 0.4545) สองครั้งนี้เพิ่มการตรวจอินพุตแล้ว `raise ValueError` นี่เป็นเบาะแสเดียวที่ชัดว่าชุดทดสอบลับมีเคสอินพุตผิดปกติ
- `t4-cashback_s3` ตรวจแค่ tier แปลก และคะแนนไม่ขยับ จึงน่าจะมีเคสอื่นที่ยังไม่ครอบคลุม
- Solver ทดสอบเองน้อยมาก บางครั้งไม่ได้รันโค้ดเลย และมีครั้งหนึ่งใช้ `python3 -I` แล้ว import `solve` ไม่เจอ
- ที่ยังไม่รู้คือวิธีปัดเศษที่ชุดทดสอบคาดหวัง เพราะใน trace ไม่มีรายละเอียดว่าเคสไหนตก

**สิ่งที่สกิลสอน**
- อ่านโจทย์เป็นตารางกติกา: คำบอกขอบเขต ("ตั้งแต่", "เกิน", "ต่ำกว่า"), การแปลงบาทเป็นสตางค์ และลำดับการคิด
- ใช้จำนวนเต็มหรือ `Fraction` และคืนค่าเป็น `int` ถ้าโจทย์ไม่ระบุวิธีปัด ให้ปัดครึ่งขึ้น (half-up)
- ตรวจอินพุตตามช่วงที่โจทย์ระบุ แล้ว `raise ValueError` ถ้าผิดช่วงหรือผิดชนิด ส่วนค่าที่โจทย์ไม่ได้ห้าม เช่น รายการสินค้าว่าง ให้รับได้
- ทดสอบก่อนส่งทุกครั้ง: ค่าขอบทุกจุด เทียบกับ oracle อิสระ เคสอินพุตผิด และรันเวอร์ชันสุดท้ายซ้ำ โดยใช้ `PYTHONPATH=.` ไม่ใช้ `-I`

**สิ่งที่ตั้งใจให้ epoch 1 ตอบ**
- สกิลบอกให้ปัดครึ่งขึ้นเมื่อโจทย์ไม่ระบุ ซึ่งต่างจากครั้งก่อนที่ t4 ปัดลง ถ้าคะแนน t4 ขยับ แปลว่าวิธีปัดเป็นตัวแปรสำคัญ
- ผมบันทึกการวิเคราะห์และแผนไว้ใน `/evo/evolver_
…(ตัด 19 ตัวอักษร)
