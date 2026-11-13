# ตาที่ 2 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-13 03:32 UTC คุณมีเวลาถึง 2026-11-13 04:02 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 2 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v2` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; cat scores/epoch_1.json; ls skills; for d in solver_workspaces/epoch_1/*; do echo "=== $d"; cat $d/solve.py; done
```

ผลที่ได้:

```
{
 "t1-cafe-bill_s1": 0.7,
 "t1-cafe-bill_s2": 0.5,
 "t1-cafe-bill_s3": 0.3,
 "t2-split-bill_s1": 0.7,
 "t2-split-bill_s2": 0.7,
 "t2-split-bill_s3": 0.6,
 "t3-shipping-fee_s1": 0.6,
 "t3-shipping-fee_s2": 0.5,
 "t3-shipping-fee_s3": 0.5,
 "t4-cashback_s1": 0.7,
 "t4-cashback_s2": 0.6,
 "t4-cashback_s3": 0.5
}epoch_0
epoch_1
=== solver_workspaces/epoch_1/t1-cafe-bill_s1
from fractions import Fraction

# นโยบายปัดเศษ r1: คำนวณแม่นยำด้วย Fraction แล้วปัดครึ่งขึ้น (half-up) ครั้งเดียวตอนท้าย


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(items, (list, tuple)) or len(items) == 0:
        raise ValueError("items must be a non-empty list")
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        try:
            price, qty = it["price"], it["qty"]
        except (KeyError, TypeError):
            raise ValueError("each item needs price and qty")
        if not _is_int(price) or price < 0:
            raise ValueError("price must be int >= 0")
        if not _is_int(qty) or qty < 1:
            raise ValueError("qty must be int >= 1")
  
…(ตัด 10802 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /evo/traces/epoch_1; python3 - <<'E'
import json
for f in ['t1-cafe-bill_s1','t3-shipping-fee_s1']:
  print('=====',f)
  for l in open(f+'.jsonl'):
    d=json.loads(l)
    if d.get('type')=='assistant':
        for c in d['message']['content']:
            if c['type']=='text': print(c['text'][:2500])
            if c['type']=='tool_use': print('TOOL',json.dumps(c['input'],ensure_ascii=False)[:700])
    if d.get('type')=='user':
        for c in d['message']['content']:
            if isinstance(c,dict) and c.get('type')=='tool_result': print('RES',str(c['content'])[:600])
E
```

ผลที่ได้:

```
===== t1-cafe-bill_s1
TOOL {"command": "ls ./skills 2>&1 | head"}
RES baankafe-money-fn
TOOL {"command": "cd skills/baankafe-money-fn; ls -R; cat SKILL.md *.md 2>/dev/null"}
RES .:
SKILL.md
---
name: baankafe-money-fn
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชัน Python ใน solve.py จากโจทย์ภาษาไทยของ BaanKafe ที่คำนวณเงิน (ส่วนลด VAT ทิป หารบิล ค่าส่ง เงินคืน) เป็นจำนวนเต็มสตางค์ — มีขั้นตอนอ่านเงื่อนไข ขอบเขต การปัดเศษ การตรวจ input และการทดสอบก่อนส่ง
---

# เขียนฟังก์ชันคิดเงินจากโจทย์ BaanKafe

ผลจาก epoch 0: โค้ดตามตัวอักษรของโจทย์ได้คะแนนแค่ 0.3–0.6 จุดที่พลาดคือสิ่งที่โจทย์ไม่ได้เขียนตรง ๆ
(วิธีปัดเศษ, input ผิดโดเมน) และ Solver หลายครั้งไม่ได้รันทดสอบเลย ทำตามขั้นตอนนี้ให้ครบ

## 1) อ่านโจทย์เป็นเงื่อนไขทีละข้อ
- เขียนรายการเงื่อนไขทุกบรรทัดของโจทย์ แล้วแปลงเป็น
TOOL {"command": "cd /workspace/evlab/ws/p2/legs/runs/v1_train/t1-cafe-bill-r1/sandbox && cat > solve.py <<'EOF'\nfrom fractions import Fraction\n\n# นโยบายปัดเศษ r1: คำนวณแม่นยำด้วย Fraction แล้วปัดครึ่งขึ้น (half-up) ครั้งเดียวตอนท้าย\n\n\ndef _is_int(v):\n    return isinstance(v, int) and not isinstance(v, bool)\n\n\ndef cafe_bill(items, member):\n    if not isinstance(items, (list, tuple)) or len(items) == 0:\n   
…(ตัด 4099 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cd /evo/staging/baankafe-money-fn; python3 - <<'E'
s=open('SKILL.md').read()
a=s.index('## 3)'); b=s.index('## 5)')
new='''## 3) นโยบายปัดเศษ (ตัดสินแล้ว ห้ามเปลี่ยน)
ผลทดลอง epoch 1: คำนวณแม่นยำ (Fraction/จำนวนเต็ม) ตลอดทาง แล้วปัด **half-up ครั้งเดียวตอนท้าย** ได้คะแนนสูงสุดทุกข้อ
(t1 0.7, t2 0.7, t3 0.6, t4 0.7) ส่วนปัดทุกขั้นหรือปัดลง (floor) ได้ต่ำกว่า → ใช้ half-up ครั้งเดียวตอนท้ายเสมอ
- สูตร: `(2*num + den) // (2*den)` หรือ `(Fraction*2 + 1)//2`
- ข้อยกเว้นเดียว: split_bill — ยอดที่หาร = `total*(100+tip)/100` ปัด half-up เป็นสตางค์ แล้ว `divmod(grand, people)` ให้คนแรก ๆ เพิ่มคนละ 1
- cashback: คำนวณ `amount*rate*(2 ถ้า birthday)` แบบแม่นยำ → ใช้ cap 20000 → ปัด half-up ท้ายสุด
- ยังเหลือคะแนนที่หายไปราว 0.3 ต่อข้อ สาเหตุที่เหลือคาดว่าเป็นการตรวจ input (ดูข้อ 4) จึงทดลองต่อ

## 4) ตรวจ input (กำลังทดลองความเข้มงวด — เลือกตามเลขท้ายโฟลเดอร์ `-rN` จาก `pwd`)
หลักร่วม: ตรวจช่วงค่าตามโดเมนที่โจทย์ระบุเสมอ (qty ≥ 1, people ≥ 1, tip 0–100, น้ำหนัก 1–30000,
ระยะทาง ≥ 0, total/amount ≥ 0, price ≥ 0, tier ต้องเป็นค่าที่ระบุ) ถ้านอกช่วง `raise ValueError(...)`
ห้ามให้หลุดเป็น `ZeroDivisionError`/`KeyError` (epoch 1: เพิ่มการตรวจช่วงทำให้ได้คะแนนเพิ่มประมาณ +0.2)
แล้วแยกตาม rollout:
- **r1** (เข้มสุด ตามที่ทำใน epoch 1): ตรวจชนิดด้วย (int ไม่รับ bool, ธง True/False ต้องเป็น `bool`) ชนิดผิด → `ValueError` และ `items` ว่าง → `ValueError`
- **r2** (ตรวจเฉพาะช่วงค่า/enum): ไม่ตรวจชนิดเลย (ยอมรับตัวเลขชนิดใดก็ได้ที่เปรียบเทียบได้ และธงเป็นค่า truthy/falsy ใดก็ได้เช่น 0/1) `items` ว่างให้คิดเป็นยอด 0 ไม่ raise (ยังต้องตรวจ qty ≥ 1, price ≥ 0 ของแต่ละชิ้นที่มี)
- **r3** (ชนิดผิดเป็น TypeError): ค่าที่ชนิดผิด (ไม่ใช่ตัวเลข/ไม่ใช่ bool/เป็น bool ที่ใส่ในช่องตัวเลข/tier ไม่ใช่ str) → `raise TypeError(...)`, ค่านอกช่วง → `raise ValueError(...)`, `items` ว่าง → `ValueError`
- ถ้าหา `-rN` ไม่เจอ ใช้ r1
ใส่คอมเมนต์บนสุดของโค้ดว่า "validation policy rN" และบอกในคำตอบสุดท้าย ห้ามเปลี่ยนเอง

'''
open('SKILL.md','w').write(s[:a]+new+s[b:])
E
sed -i 's/^ผลจาก epoch 0:.*/ผลจากรอบก่อน: คะแนนขึ้นจาก 0.3–0.6 เป็น 0.3–0.7 เมื่อปัดครึ่งขึ้นตอนท้ายและตรวจช่วง input — ทำตามขั้นตอนนี้ให้ครบ/; /^(วิธีปัดเศษ, input ผิดโดเมน)/d' SKILL.md
head -12 SKILL.md
cat >> /evo/evolver_workspace/notes.md <<'E'
# epoch1 results
r1(half-up end): t1 .7 t2 .7 t3 .6 t4 .7; r2(round each step): .5 .7 .5 .6; r3(floor): .3 .6 .5 .5. => half-up once at end fixed in v2.
validation added gave ~+0.2 (e0 vs e1 r1). Remaining ~0.3 unknown. v2 explores validation strictness: r1 strict ValueError+empty err; r2 range
…(ตัด 57 ตัวอักษร)
```

ผลที่ได้:

```
---
name: baankafe-money-fn
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชัน Python ใน solve.py จากโจทย์ภาษาไทยของ BaanKafe ที่คำนวณเงิน (ส่วนลด VAT ทิป หารบิล ค่าส่ง เงินคืน) เป็นจำนวนเต็มสตางค์ — มีขั้นตอนอ่านเงื่อนไข ขอบเขต การปัดเศษ การตรวจ input และการทดสอบก่อนส่ง
---

# เขียนฟังก์ชันคิดเงินจากโจทย์ BaanKafe

ผลจากรอบก่อน: คะแนนขึ้นจาก 0.3–0.6 เป็น 0.3–0.7 เมื่อปัดครึ่งขึ้นตอนท้ายและตรวจช่วง input — ทำตามขั้นตอนนี้ให้ครบ

## 1) อ่านโจทย์เป็นเงื่อนไขทีละข้อ
- เขียนรายการเงื่อนไขทุกบรรทัดของโจทย์ แล้วแปลงเป็นโค้ดทีละข้อ ห้ามข้ามหรือรวมข้อ
- คำไทยกับเครื่องหมาย: "ตั้งแต่ X" = `>= X` · "เกิน X" = `> X` · "ไม่เกิน X" = `<= X` · "ต่ำกว่า X" = `< X`
```

**Agent พูด:** `skills_v2` อยู่ใน `/evo/staging/baankafe-money-fn/SKILL.md` แล้ว ผมยังไม่ได้ทดสอบว่ามันช่วยให้ Solver ได้คะแนนสูงขึ้นจริงหรือไม่

**ผล epoch 1 แยกตามวิธีปัดเศษ**

| วิธีปัดเศษ | t1 | t2 | t3 | t4 |
|---|---|---|---|---|
| r1: ปัดครึ่งขึ้นครั้งเดียวตอนท้าย | 0.7 | 0.7 | 0.6 | 0.7 |
| r2: ปัดครึ่งขึ้นทุกขั้น | 0.5 | 0.7 | 0.5 | 0.6 |
| r3: ปัดลงตอนท้าย | 0.3 | 0.6 | 0.5 | 0.5 |

r1 ได้คะแนนสูงสุดหรือเท่ากับสูงสุดทุกข้อ ส่วนการตรวจช่วงของ input (ขึ้นเป็น `ValueError`) น่าจะเพิ่มคะแนนได้ราว 0.2 เทียบกับ epoch 0

**สิ่งที่เปลี่ยนใน v2**
- ข้อ 3: ตัดสินให้ใช้ "คำนวณแม่นยำแล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย" และไม่ต้องทดลองเรื่องนี้ต่อ
- ข้อ 4: ทดลองเรื่องความเข้มงวดของการตรวจ input โดยดูเลข `-rN` จากชื่อโฟลเดอร์ทำงาน (ใช้ `pwd`)
  - r1: เข้มเหมือนเดิม ตรวจชนิดด้วย ชนิดผิดหรือ `items` ว่างให้ขึ้น `ValueError`
  - r2: ตรวจเฉพาะช่วงค่ากับ enum ไม่ตรวจชนิด และถ้า `items` ว่างให้คืนยอด 0 ไม่ raise
  - r3: ชนิดผิดให้ขึ้น `TypeError` ส่วนค่านอกช่วงขึ้น `ValueError`

คะแนนที่หายไปราว 0.3 ต่อข้อยังไม่มีคำอธิบายที่ยืนยันได้ ผมเดาว่าอยู่ที่การตรวจ input เพราะตัวตรวจไม่แจ้งรายละเอียด ถ้าคะแนนของ r1, r2 และ r3 ใน epoch 2 ต่างกัน ผมจะเลือกแบบที่ได้คะแนนสูงสุดมาเป็นกติกาตายตัวใน v3 ข้อเสียคือ r2 กับ r3 อาจได้คะแนนต่ำกว่า r1 ใน epoch นี้ ผมจดผลวิเคราะห์และแผนไว้ที่ `/evo/evolver_workspace/notes.md`
