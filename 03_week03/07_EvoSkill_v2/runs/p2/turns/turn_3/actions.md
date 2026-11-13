# ตาที่ 3 ของ Evolver

ข้อความที่ได้รับ: ขณะนี้เวลา 2026-11-13 03:34 UTC คุณมีเวลาถึง 2026-11-13 04:04 UTC สำหรับ epoch นี้ หลังจากนั้น `/evo/staging/` จะถูกนำไปใช้ตามสภาพที่เป็นอยู่ · ตอนนี้คือ epoch 3 · โปรดวิเคราะห์ rollout ของ Solver วินิจฉัยจุดพลาดที่สกิลเฉพาะทางน่าจะแก้ได้ แล้วเขียน `skills_v3` ลงใน `/evo/staging/`

### ขั้น 1 · Bash

```
cd /evo; cat scores/epoch_2.json; for d in solver_workspaces/epoch_2/*; do echo "=== $d"; cat $d/solve.py; done
```

ผลที่ได้:

```
{
 "t1-cafe-bill_s1": 0.7,
 "t1-cafe-bill_s2": 0.6,
 "t1-cafe-bill_s3": 0.6,
 "t2-split-bill_s1": 0.7,
 "t2-split-bill_s2": 0.6,
 "t2-split-bill_s3": 0.6,
 "t3-shipping-fee_s1": 0.6,
 "t3-shipping-fee_s2": 0.6,
 "t3-shipping-fee_s3": 0.6,
 "t4-cashback_s1": 0.7,
 "t4-cashback_s2": 0.6,
 "t4-cashback_s3": 0.6
}=== solver_workspaces/epoch_2/t1-cafe-bill_s1
# validation policy r1
from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    if not isinstance(items, (list, tuple)) or len(items) == 0:
        raise ValueError("items must be a non-empty list")
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("item must be a dict")
        price, qty = it.get("price"), it.get("qty")
        if not _is_int(price) or not _is_int(qty):
            raise ValueError("price and qty must be int")
        if price < 0:
            raise ValueError("price must be >= 0")
        if qty < 1:
            raise ValueError("qty must be >= 1")
        total += price * qty

    amount = Fra
…(ตัด 9880 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cd /evo/staging/baankafe-money-fn; python3 - <<'E'
s=open('SKILL.md').read()
a=s.index('## 3)'); b=s.index('## 5)')
new='''## 3) นโยบายปัดเศษ
คำนวณแม่นยำ (Fraction/จำนวนเต็ม) ตลอดทาง ห้ามปัดกลางทาง แล้วปัดครั้งเดียวตอนท้าย
(ผลที่รู้แล้ว: ปัดทุกขั้นหรือปัดลง ได้คะแนนต่ำกว่าปัด half-up ตอนท้ายทุกข้อ)
เลือกวิธีปัดตอนท้ายตามเลข `-rN` ท้ายโฟลเดอร์ (รัน `pwd`; ไม่เจอให้ใช้ r1) — กำลังทดลองหาแบบที่ถูกต้อง:
- **r1**: half-up `(2*num + den) // (2*den)` (แบบที่ได้คะแนนสูงสุดใน epoch 1–2: t1 0.7, t2 0.7, t3 0.6, t4 0.7)
- **r2**: ceiling ปัดขึ้นเสมอเมื่อมีเศษ `-(-num // den)`
- **r3**: banker's (half-even) แบบแม่นยำ: ถ้าเศษ = .5 พอดีให้ปัดไปหาเลขคู่ มิฉะนั้นปัดใกล้สุด (ใช้ `fractions.Fraction` แล้ว `round(Fraction)` ซึ่งเป็น half-even และคืน int — ไม่ใช้ float)
รูปแบบอื่นคงเดิม: split_bill ปัดยอดที่หาร `total*(100+tip)/100` เป็นสตางค์ด้วยวิธีของ rN แล้ว `divmod(grand, people)` ให้คนแรก ๆ +1;
cashback คำนวณ `amount*rate*(2 ถ้า birthday)` แม่นยำ → ใช้ cap 20000 → ปัดตามวิธีของ rN ท้ายสุด
ใส่คอมเมนต์บนสุดว่า "rounding policy rN" และบอกในคำตอบสุดท้าย ห้ามเปลี่ยนเอง

## 4) ตรวจ input (ตัดสินแล้ว — ใช้แบบเข้มเสมอ ทุก rollout)
ผลทดลอง epoch 2: แบบเข้มที่ raise `ValueError` ได้คะแนนสูงสุด (t1/t2/t4 0.7); ไม่ตรวจชนิด หรือใช้ `TypeError` ได้ต่ำกว่า (0.6)
- ทุกความผิดปกติของ input ให้ `raise ValueError(...)` อย่างเดียว (ห้าม TypeError/ZeroDivisionError/KeyError/AttributeError หลุดออกมา)
- ตรวจช่วงค่าตามโดเมนในโจทย์: qty ≥ 1, price ≥ 0, people ≥ 1, tip 0–100, น้ำหนัก 1–30000, ระยะทาง ≥ 0, total/amount ≥ 0, tier ต้องเป็นค่าที่ระบุ (ตัวพิมพ์เล็กตรงเป๊ะ)
- ตรวจชนิด: จำนวนเงิน/จำนวนชิ้น/จำนวนคน/ทิป ต้องเป็น `int` แท้ (ไม่รับ `bool`, float, str, None); ธง (member/birthday/express) ต้องเป็น `bool`; tier ต้องเป็น `str`
  distance_km รับ int/float/Fraction ที่ไม่ใช่ bool และ finite (ไม่ NaN/inf)
- `items` ต้องเป็น list/tuple ที่ไม่ว่าง ทุกชิ้นเป็น dict ที่มี key `price` และ `qty` ถ้าไม่ใช่ → ValueError
- ลำดับตรวจ: ชนิด → ช่วงค่า (กันเทียบค่าชนิดผิดแล้วเกิด TypeError)

'''
open('SKILL.md','w').write(s[:a]+new+s[b:])
E
sed -i 's/^ผลจากรอบก่อน:.*/ผลจากรอบก่อน: คะแนนสูงสุดตอนนี้ 0.6–0.7 ต่อข้อ ยังขาดอีกราว 0.3 ซึ่งยังไม่รู้สาเหตุ — ทำตามขั้นตอนนี้ให้ครบ/' SKILL.md
grep -n "^## " SKILL.md
cat >> /evo/evolver_workspace/notes.md <<'E'
# epoch2 results
validation r1 strict ValueError: .7 .7 .6 .7 ; r2 no types/empty ok: .6 all; r3 TypeError: .6 all. => strict ValueError fixed in v3.
t3 stuck .6 regardless. v3 explores final rounding: r1 half-up, r2 ceil, r3 banker's. remaining 0.3 unexplained 
…(ตัด 56 ตัวอักษร)
```

ผลที่ได้:

```
10:## 1) อ่านโจทย์เป็นเงื่อนไขทีละข้อ
18:## 2) ใช้เลขจำนวนเต็มหรือ Fraction เท่านั้น
23:## 3) นโยบายปัดเศษ
34:## 4) ตรวจ input (ตัดสินแล้ว — ใช้แบบเข้มเสมอ ทุก rollout)
43:## 5) ต้องรันทดสอบก่อนจบ (ห้ามส่งโดยไม่ได้รัน)
49:## 6) ส่งมอบ
```

**Agent พูด:** `skills_v3` อยู่ใน `/evo/staging/baankafe-money-fn/SKILL.md` แล้ว ผมยังไม่ได้ทดสอบว่ามันช่วยให้ Solver ได้คะแนนสูงขึ้นจริงหรือไม่

**ผลของ epoch 2 (ทดลองความเข้มงวดของการตรวจ input)**

| แบบตรวจ input | t1 | t2 | t3 | t4 |
|---|---|---|---|---|
| r1: เข้ม ชนิดผิดขึ้น `ValueError` | 0.7 | 0.7 | 0.6 | 0.7 |
| r2: ตรวจเฉพาะช่วงค่า ไม่ตรวจชนิด | 0.6 | 0.6 | 0.6 | 0.6 |
| r3: ชนิดผิดขึ้น `TypeError` | 0.6 | 0.6 | 0.6 | 0.6 |

แบบเข้มที่ขึ้น `ValueError` ได้คะแนนสูงสุดหรือเท่ากับสูงสุดทุกข้อ ตัวตรวจน่าจะคาดหวัง `ValueError` เมื่อ input ผิดชนิด

**สิ่งที่เปลี่ยนใน v3**
- ข้อ 4: ใช้แบบเข้มกับทุก rollout และไม่ทดลองเรื่องนี้ต่อ
  - ทุกความผิดปกติของ input ให้ขึ้น `ValueError` อย่างเดียว
  - ตรวจชนิด ช่วงค่า และโครงสร้างของ `items` ตามลำดับ
- ข้อ 3: ปัดเศษครั้งเดียวตอนท้ายเหมือนเดิม แต่ทดลองวิธีปัดตอนท้ายตามเลข `-rN`
  - r1: half-up ซึ่งเป็นแบบที่ได้คะแนนสูงสุดอยู่ตอนนี้
  - r2: ปัดขึ้นเสมอเมื่อมีเศษ (ceiling)
  - r3: banker's (half-even) ด้วย `Fraction` ไม่ใช้ float

เหตุผลที่ทดลองการปัดตอนท้ายต่อคือคะแนนยังขาดอีกราว 0.3 ต่อข้อ และ t3 อยู่ที่ 0.6 ไม่ว่าจะเปลี่ยนวิธีตรวจ input แบบไหน ผมจึงยังไม่รู้สาเหตุของส่วนที่ขาด ผมคาดว่าเป็นเรื่องการปัดเศษเมื่อเศษเป็น .5 พอดีหรือตัวตรวจมีเคสอื่นที่ยังไม่เห็น ผมจดแผนและสิ่งที่ยังไม่ได้ลองไว้ที่ `/evo/evolver_workspace/notes.md` เช่น การไม่รับ weight เป็น float ใน t3 และกรณี `items` ว่าง ข้อเสียของการทดลองนี้คือ r2 กับ r3 อาจได้คะแนนต่ำกว่า r1 ใน epoch 3
