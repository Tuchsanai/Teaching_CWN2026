# Iteration 2

คะแนน Training ของรอบนี้: 91.3% (ผ่านครบ 3/24 Trace)

## Active skills (ชุดสกิลที่ Agent ใช้ในรอบนี้)

### skills/cafe_solve_checklist/SKILL.md

---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด return 0)
ทุกอินพุตผิดช่วง/ผิดชนิดต้อง `raise ValueError` (ห้ามปล่อยให้เป็น ZeroDivisionError/TypeError/KeyError)
```python
def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):   # ปฏิเสธ bool และ float เช่น 20000.0
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x

def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x
```
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์ ("ตั้งแต่ 0" → lo=0, "ตั้งแต่ 1" → lo=1, "1–30,000" → lo=1, hi=30000)
- ใช้ `_flag` กับพารามิเตอร์ True/False, ตรวจ enum (เช่น tier) ว่าอยู่ในรายการที่โจทย์ให้
- list/dict: ตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ, และค่าในนั้นผ่าน `_int` (ห้ามคืน KeyError)
- ตรวจ `-1` ก่อนเงื่อนไข "ต่ำกว่าเกณฑ์ → 0" เสมอ

## 2. ปัดเศษ: half up ครั้งเดียวตอนท้าย ด้วยจำนวนเต็ม
- โจทย์ไม่ระบุวิธีปัด = half up เสมอ ห้ามเลือกปัดลง (`//` ตรง ๆ) ห้าม `round()` ห้าม float
- คิดเป็นเศษส่วน `num/den` ด้วย int (หรือ `Fraction`) ทุกขั้น ไม่ปัดระหว่างทาง แล้วปัดครั้งเดียว: `(num*2 + den) // (den*2)` (ค่าไม่ติดลบ)
- ลำดับคูณ (ส่วนลด/ค่าธรรมเนียม/VAT) ตามลำดับในโจทย์ ส่วนเพดาน (`min`) ทำหลังปัดตามที่โจทย์เรียง
- คืนค่าเป็น `int` เสมอ

## 3. ต่อท้าย solve.py ให้รันเป็น CLI ได้ (key ของ JSON = ชื่อพารามิเตอร์ของฟังก์ชัน)
```python
import json, sys

def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = FUNC(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))

if __name__ == "__main__":
    _main()
```
แทน `FUNC` ด้วยชื่อฟังก์ชันของโจทย์ ผิดปกติต้อง exit 2 พร้อม JSON ไม่มี traceback

## 4. สร้าง test_solve.py ข้าง solve.py (unittest) แล้วรันให้ผ่าน
ต้องมีอย่างน้อย: กรณีปกติ 2–3 ตัว · ค่าขอบทุกเกณฑ์ (พอดี, ต่ำกว่า 1, สูงกว่า 1) · เคสปัดเศษที่เศษ = .5 พอดี · `assertRaises(ValueError)` สำหรับค่านอกช่วง, float (`1000.0`), bool, ชนิดผิด
```python
import unittest
from solve import FUNC

class T(unittest.TestCase):
    def test_basic(self): ...
    def test_reject(self):
        with self.assertRaises(ValueError):
            FUNC(...)

if __name__ == "__main__":
    unittest.main()
```
รัน `python3 -m unittest -v test_solve` และ `echo '{...}' | python3 solve.py; echo $?` ทั้งกรณีปกติ (exit 0) และกรณีผิด (exit 2) ก่อนจบงาน

## Current wiki

### wiki/index.md

# Wiki Index

- [input-validation-missing](wiki/patterns/input-validation-missing.md): ฟังก์ชันไม่ตรวจอินพุต จึงคืนค่าปกติหรือ raise ZeroDivisionError เมื่อได้ค่านอกช่วง/float/bool (reject_value, reject_type) เพราะโจทย์บอกแค่ช่วงที่ถูก ให้ตรวจทุกพารามิเตอร์เป็นอย่างแรก (ปฏิเสธ bool และ float) แล้ว raise ValueError
- [cli-json-wrapper-missing](wiki/patterns/cli-json-wrapper-missing.md): cli_ok/cli_error ล้มเพราะ solve.py มีแต่ฟังก์ชัน ไม่อ่าน stdin ซึ่งโจทย์ไม่ได้บอก ให้เพิ่ม main ที่อ่าน JSON จาก stdin พิมพ์ {"ok":true,"result":..} exit 0 และเมื่อผิดพิมพ์ {"ok":false,"error":..} exit 2
- [missing-test-file](wiki/patterns/missing-test-file.md): ข้อ tests ล้มเพราะไม่มี test_solve.py ข้าง solve.py (โจทย์ไม่ได้ขอ) ให้สร้างไฟล์ unittest ครอบคลุมกรณีปกติ ค่าขอบ ปัดเศษ และ ValueError แล้วรันให้ผ่าน
- [rounding-exact-half-up](wiki/patterns/rounding-exact-half-up.md): half_up/no_drift ล้มเมื่อเลือกปัดลง (//) เองตอนโจทย์ไม่ระบุ ส่วนข้อที่ผ่านใช้จำนวนเต็ม/Fraction แล้วปัด half up ครั้งเดียวท้ายสุด ใช้ (num*2+den)//(den*2) ห้าม float และ round()
- [happy-path-only-self-check](wiki/patterns/happy-path-only-self-check.md): Agent ทดสอบเองแค่ตัวอย่างปกติ 3–5 ตัวแล้วจบ จึงพลาดทุกข้อนอกเหนือจากกรณีปกติ (ได้ 0.30–0.50) ให้ใช้ checklist 5 ข้อ: ค่าขอบ ปัดเศษ ValueError CLI และ test_solve.py ก่อนส่งงาน

### wiki/log.md

# Evolution Log

## Iteration 1 · Training 45.4%

ไม่มีสกิล และ skill-impact ยังว่าง จึงเป็นรอบฐานเริ่มต้น Trace 5 ตัว (t1 cafe_bill, t2 split_bill, t3 shipping_fee, t4 cashback x2) ได้ 0.30–0.50

สิ่งที่พบ:
- ผ่านเหมือนกันทุก trace: `contract`, `basic`, `boundary` ตรรกะธุรกิจหลักถูก
- ล้มเหมือนกัน 5/5 ในสี่ข้อที่โจทย์ไม่ได้บอกตรง ๆ: `reject_value`+`reject_type` (ไม่ตรวจอินพุต), `cli_ok`+`cli_error` (ไม่มี CLI), `tests` (ไม่มี test_solve.py)
- ล้มเฉพาะ cashback: `half_up`+`no_drift` เพราะเลือกปัดลง ส่วน cafe_bill/split_bill/shipping_fee ใช้ integer/Fraction แล้วปัด half up ผ่าน
- Agent เช็ค `./skills` แล้วไม่พบ จึงเขียนตามโจทย์ตรง ๆ ด้วยคำสั่ง 2 ครั้ง และทดสอบแค่กรณีปกติ

หน้าที่เพิ่ม: input-validation-missing, cli-json-wrapper-missing, missing-test-file, rounding-exact-half-up (มีทั้งแบบพลาดและสำเร็จ), happy-path-only-self-check

ข้อสังเกตสำหรับ Skill Proposer: สาเหตุหลักมาจากข้อกำหนดที่อยู่ในตัวตรวจแต่ไม่อยู่ในโจทย์ จึงควรเขียนสกิลเป็น checklist ส่งมอบที่ใช้ได้กับทุกฟังก์ชันของ BaanKafe รอบนี้ยังไม่มีสกิลให้ประเมินว่าได้ผลหรือไม่

### wiki/skill-impact.md

# Skill Impact

บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ

## Iteration 1 · create `cafe_solve_checklist` · ACCEPTED

- Validation ของสกิลที่เสนอ: 92.5% · R_best ก่อนหน้า: 45.0% -> รับ (R_best ใหม่ 92.5%)
- เหตุผลของข้อเสนอ: ทุก Trace ใน iter 1 พลาด reject_value, reject_type, cli_ok, cli_error, tests เหมือนกัน (และ half_up/no_drift ใน cashback) เพราะไม่มีสกิล จึงรวมเช็กลิสต์จาก pattern ทั้งหมดไว้ในสกิลเดียว

Diff ของ SKILL.md ที่เสนอ:

```diff
--- a/skills/cafe_solve_checklist/SKILL.md
+++ b/skills/cafe_solve_checklist/SKILL.md
@@ -0,0 +1,76 @@
+---
+name: cafe_solve_checklist
+description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
+---
+
+# When to Apply
+- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน
+
+# When NOT to Apply
+- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน
+
+# Instructions
+ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:
+
+## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด return 0)
+ทุกอินพุตผิดช่วง/ผิดชนิดต้อง `raise ValueError` (ห้ามปล่อยให้เป็น ZeroDivisionError/TypeError/KeyError)
+```python
+def _int(x, lo=None, hi=None):
+    if isinstance(x, bool) or not isinstance(x, int):   # ปฏิเสธ bool และ float เช่น 20000.0
+        raise ValueError(f"expected int, got {x!r}")
+    if (lo is not None and x < lo) or (hi is not None and x > hi):
+        raise ValueError(f"out of range: {x!r}")
+    return x
+
+def _flag(x):
+    if not isinstance(x, bool):
+        raise ValueError(f"expected bool, got {x!r}")
+    return x
+```
+- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์ ("ตั้งแต่ 0" → lo=0, "ตั้งแต่ 1" → lo=1, "1–30,000" → lo=1, hi=30000)
+- ใช้ `_flag` กับพารามิเตอร์ True/False, ตรวจ enum (เช่น tier) ว่าอยู่ในรายการที่โจทย์ให้
+- list/dict: ตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ, และค่าในนั้นผ่าน `_int` (ห้ามคืน KeyError)
+- ตรวจ `-1` ก่อนเงื่อนไข "ต่ำกว่าเกณฑ์ → 0" เสมอ
+
+## 2. ปัดเศษ: half up ครั้งเดียวตอนท้าย ด้วยจำนวนเต็ม
+- โจทย์ไม่ระบุวิธีปัด = half up เสมอ ห้ามเลือกปัดลง (`//` ตรง ๆ) ห้าม `round()` ห้าม float
+- คิดเป็นเศษส่วน `num/den` ด้วย int (หรือ `Fraction`) ทุกขั้น ไม่ปัดระหว่างทาง แล้วปัดครั้งเดียว: `(num*2 + den) // (den*2)` (ค่าไม่ติดลบ)
+- ลำดับคูณ (ส่วนลด/ค่าธรรมเนียม/VAT) ตามลำดับในโจทย์ ส่วนเพดาน (`min`) ทำหลังปัดตามที่โจทย์เรียง
+- คืนค่าเป็น `int` เสมอ
+
+## 3. ต่อท้าย solve.py ให้รันเป็น CLI ได้ (key ของ JSON = ชื่อพารามิเตอร์ของฟังก์ชัน)
+```python
+import json, sys
+
+def _main():
+    try:
+        data = json.loads(sys.stdin.read())
+        if not isinstance(data, dict):
+            raise ValueError("input must be a JSON object")
+        result = FUNC(**data)
+    except (ValueError, TypeError, KeyError) as e:
+        print(json.dumps({"ok": False, "error": str(e)}))
+        sys.exit(2)
+    print(json.dumps({"ok": True, "result": result}))
+
+if __name__ == "__main__":
+    _main()
+```
+แทน `FUNC` ด้วยชื่อฟังก์ชันของโจทย์ ผิดปกติต้อง exit 2 พร้อม JSON ไม่มี traceback
+
+## 4. สร้าง test_solve.py ข้าง solve.py (unittest) แล้วรันให้ผ่าน
+ต้องมีอย่างน้อย: กรณีปกติ 2–3 ตัว · ค่าขอบทุกเกณฑ์ (พอดี, ต่ำกว่า 1, สูงกว่า 1) · เคสปัดเศษที่เศษ = .5 พอดี · `assertRaises(ValueError)` สำหรับค่านอกช่วง, float (`1000.0`), bool, ชนิดผิด
+```python
+import unittest
+from solve import FUNC
+
+class T(unittest.TestCase):
+    def test_basic(self): ...
+    def test_reject(self):
+        with self.assertRaises(ValueError):
+            FUNC(...)
+
+if __name__ == "__main__":
+    unittest.main()
+```
+รัน `python3 -m unittest -v test_solve` และ `echo '{...}' | python3 solve.py; echo $?` ทั้งกรณีปกติ (exit 0) และกรณีผิด (exit 2) ก่อนจบงาน
```

### wiki/patterns/cli-json-wrapper-missing.md

# cli-json-wrapper-missing

## อาการ
- `cli_ok` และ `cli_error` ล้มทุก trace: ส่ง JSON ทาง stdin แล้วได้ exit 0 และ stdout ว่าง
- `solve.py` มีแต่ฟังก์ชัน ไม่มีโค้ดที่อ่าน stdin เลย

## สาเหตุ
- โจทย์เขียนแค่ "ฟังก์ชัน `xxx(...)` ในไฟล์ `solve.py`" ไม่ได้บอกว่าต้องรันเป็น CLI ได้ด้วย ข้อกำหนดนี้อยู่ในตัวตรวจเท่านั้น
- Agent ทำตามตัวอักษรของโจทย์และไม่ได้คิดถึงวิธีที่ตัวตรวจจะเรียกใช้
- ไม่มีสกิลบอกข้อกำหนดนี้ (รอบ 1 ไม่มีสกิล และ `./skills` ไม่มีอยู่)

## หลักฐาน
- iter 1 · t4-cashback-r3, t4-cashback-r2, t3-shipping-fee-r2, t2-split-bill-r4, t1-cafe-bill-r1: ล้มครบ 5/5
- ตัวอย่างข้อความตัวตรวจ: stdin `{"amount": 20000, "tier": "gold", "birthday": false}` ต้องได้ `{"ok": true, "result": 500}` exit 0
- error: stdin มี `tier` เป็น `bronze` หรือ `people: 0` ต้องได้ `{"ok": false, "error": "..."}` exit 2 และไม่มี traceback

## วิธีแก้
ต่อท้าย `solve.py` ทุกครั้ง โดยใช้ชื่อพารามิเตอร์เดียวกับ key ของ JSON ในโจทย์
```python
import json, sys

def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = FUNC(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))

if __name__ == "__main__":
    _main()
```
- แทน `FUNC` ด้วยชื่อฟังก์ชันของโจทย์ (JSON ที่พังก็ต้องได้ exit 2 ไม่ใช่ traceback)
- ทดสอบเอง: `echo '{...}' | python3 solve.py; echo $?` ทั้งกรณีปกติ (ต้อง exit 0) และกรณีผิด (ต้อง exit 2 และ stdout เป็น JSON)

### wiki/patterns/happy-path-only-self-check.md

# happy-path-only-self-check

## อาการ
- Agent รันตัวอย่าง 3–5 กรณี ผลตรงกับที่คิดไว้ แล้วประกาศว่า "ผลตรงกับกติกา" และจบงาน
- คะแนนจริงแค่ 0.30–0.50: ผ่าน `contract`, `basic`, `boundary` แต่ล้มทุกข้อที่เกี่ยวกับ CLI, การปฏิเสธอินพุต และไฟล์ทดสอบ
- ทั้ง 5 trace ใช้คำสั่งแค่ 2 ครั้ง

## สาเหตุ
- Agent ตีความว่า "เสร็จ" คือฟังก์ชันให้ค่าถูกในตัวอย่างที่เลือกเอง ไม่ได้ตั้งรายการสิ่งที่ต้องส่งมอบ
- Agent ไม่ได้ลองอินพุตผิด ไม่ได้รัน `python3 solve.py` ผ่าน stdin และไม่ได้ทบทวนข้อที่โจทย์ปล่อยให้เลือกเอง (การปัดเศษ) ว่าควรเป็นแบบไหน
- `./skills` ไม่มี จึงไม่มีใครบอกเกณฑ์ที่ตัวตรวจใช้

## หลักฐาน
- iter 1 · t1-cafe-bill-r1: ตอบว่า "ผมไม่ได้เขียนชุดทดสอบเต็มรูปแบบ" ได้ 0.50
- iter 1 · t3-shipping-fee-r2: ตรวจ 4 กรณีปกติแล้วสรุปว่าตรงกับที่คำนวณด้วยมือ ได้ 0.50
- iter 1 · t2-split-bill-r4, t4-cashback-r2, t4-cashback-r3: รันตัวอย่างปกติ 2–5 ตัว ได้ 0.50, 0.30, 0.30

## วิธีแก้
ก่อนจบงาน ตรวจ checklist ทั้ง 5 ข้อ และรันจริงทุกข้อ
1. ฟังก์ชันให้ค่าถูกในกรณีปกติและค่าขอบ
2. ปัดเศษแบบ half up ปัดครั้งเดียวท้ายสุด (ดู rounding-exact-half-up)
3. อินพุตผิดช่วงหรือผิดชนิดทุกแบบ raise `ValueError` (ดู input-validation-missing)
4. `echo '<json>' | python3 solve.py` ได้ `{"ok": true, ...}` exit 0 และอินพุตผิดได้ exit 2 (ดู cli-json-wrapper-missing)
5. มี `test_solve.py` และรันผ่าน (ดู missing-test-file)

### wiki/patterns/input-validation-missing.md

# input-validation-missing

## อาการ
- `reject_value`: ส่งค่านอกช่วง (`weight_g=0`, `qty=0`, `people=0`, `amount=-1`) แล้วฟังก์ชันคืนค่าปกติ (0, 4000) หรือ raise `ZeroDivisionError` แทน `ValueError`
- `reject_type`: ส่ง float ที่ค่าเป็นจำนวนเต็ม (`20000.0`, `1000.0`, `4500.0`) แล้วฟังก์ชันคืนค่าปกติ เช่น `4815.0` หรือ `[5000.0, 5000.0]`
- ตัวตรวจทั้งสองข้อนี้ล้มทั้ง 5 trace

## สาเหตุ
- โจทย์บอกแค่ช่วงค่าที่ถูกต้อง ("ตั้งแต่ 1", "1–30,000", "จำนวนเต็ม 0–100") ไม่ได้เขียนว่าต้อง `raise ValueError` Agent จึงถือว่าอินพุตถูกเสมอ
- ตัวตรวจคาดว่าอินพุตที่ผิดช่วงหรือผิดชนิดทุกแบบต้องได้ `ValueError` ไม่ใช่ `TypeError` หรือ `ZeroDivisionError`
- ใน cashback Agent ตรวจแค่ `tier` ที่ไม่รู้จัก ไม่ตรวจ `amount` กับ `birthday`
- ลำดับผิด: เช็ค `amount < 10000 → return 0` ก่อนตรวจ `amount < 0` ทำให้ `-1` ได้ 0

## หลักฐาน
- iter 1 · t4-cashback-r3, t4-cashback-r2: `cashback(-1, "gold", false)` ต้อง raise แต่คืน 0 · `cashback(20000.0, ...)` คืน 500 หรือ 500.0
- iter 1 · t3-shipping-fee-r2: `shipping_fee(0, 10, false)` คืน 4000 · พลาด 4/4 กรณี และ reject_type พลาด 5/5
- iter 1 · t2-split-bill-r4: `split_bill(10000, 0, 0)` raise `ZeroDivisionError` · `split_bill(10000.0, 2, 0)` คืน `[5000.0, 5000.0]`
- iter 1 · t1-cafe-bill-r1: `qty: 0` คืน 0 · `price: 4500.0` คืน 4815.0

## วิธีแก้
ตรวจอินพุตทุกตัวเป็นอย่างแรกของฟังก์ชัน ก่อนกติกาธุรกิจใด ๆ (รวมทั้งทางลัดที่ return 0)
```python
def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x
```
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข โดยเอาช่วงจากโจทย์ ("ตั้งแต่ 0" → `lo=0`, "ตั้งแต่ 1" → `lo=1`)
- ปฏิเสธ `bool` ในช่องตัวเลข (เพราะ `True` เป็น `int`) และปฏิเสธค่าที่ไม่ใช่ `bool` ในช่อง flag เช่น `birthday`, `member`, `express` (ข้อนี้ยังไม่ยืนยันจากตัวตรวจ ทำไว้กันพลาด)
- ตรวจ enum (`tier`) และโครงสร้าง list/dict (ต้องมี key `price`, `qty`) ด้วย โดยให้ raise `ValueError` ทั้งหมด
- กรณีหารด้วยตัวแปร ตรวจช่วงก่อนหาร จะได้ไม่เจอ `ZeroDivisionError`

### wiki/patterns/missing-test-file.md

# missing-test-file

## อาการ
- `tests` ล้มทุก trace: "ไม่มีไฟล์ test_solve.py ข้าง solve.py"

## สาเหตุ
- โจทย์ไม่ได้ขอไฟล์ทดสอบ Agent ส่งมอบแค่ `solve.py` และตรวจด้วย `python3 -c` ชั่วคราวที่ไม่ได้เก็บไว้
- Agent บางตัวยอมรับตรง ๆ ว่า "ไม่ได้เขียนชุดทดสอบเต็มรูปแบบ" แต่ถือเป็นเรื่องปกติ ไม่ใช่ข้อบกพร่อง

## หลักฐาน
- iter 1 · ล้ม 5/5: t1-cafe-bill-r1, t2-split-bill-r4, t3-shipping-fee-r2, t4-cashback-r2, t4-cashback-r3
- ทุก trace ใช้คำสั่งแค่ 2 ครั้ง (ls skills กับเขียนไฟล์พร้อมรัน) ไม่มีขั้นสร้างหรือรันไฟล์ทดสอบ

## วิธีแก้
สร้าง `test_solve.py` ไว้ในโฟลเดอร์เดียวกับ `solve.py` แล้วรันให้ผ่านก่อนจบงาน
```python
import unittest
from solve import FUNC

class T(unittest.TestCase):
    def test_basic(self): self.assertEqual(FUNC(...), EXPECTED)
    def test_boundary(self): ...   # ค่าขอบทุกเกณฑ์ในโจทย์ (เท่ากับ, น้อยกว่า 1)
    def test_half_up(self): ...    # ค่าที่เศษลงตัวที่ .5 พอดี
    def test_reject(self):
        for bad in [...]:          # ค่านอกช่วง, float, bool, enum ผิด
            with self.assertRaises(ValueError): FUNC(*bad)
```
- ครอบคลุมอย่างน้อย: ปกติ · ขอบของแต่ละเกณฑ์ · ปัดเศษ · ปฏิเสธอินพุต
- รัน `python3 -m unittest -q` (หรือ `pytest -q`) แล้วแก้จนผ่าน

### wiki/patterns/rounding-exact-half-up.md

# rounding-exact-half-up

มีทั้งแบบที่พลาดและแบบที่สำเร็จ

## อาการ
- พลาด: `half_up` และ `no_drift` ล้มใน cashback `cashback(10020, "gold", false)` คาด 251 ได้ 250 · `cashback(10020, "silver", true)` คาด 301 ได้ 300
- สำเร็จ: cafe_bill, split_bill, shipping_fee ผ่านทั้ง `half_up`, `no_drift`, `boundary`

## สาเหตุ
- โจทย์ไม่ได้บอกวิธีปัดเศษสตางค์ แต่ตัวตรวจคาดว่าเป็น half up (ปัดครึ่งขึ้น) และปัดครั้งเดียวตอนท้าย
- cashback: Agent เลือก `amount * rate // 1000` (ปัดลง) แล้วเขียนว่า "โจทย์ไม่ได้ระบุ จึงเลือกปัดลง" โดยไม่ได้เทียบกับ trace ข้ออื่น
- ข้อที่ผ่านใช้เลขจำนวนเต็มหรือ `Fraction` คำนวณทุกขั้นแบบเป๊ะ แล้วปัด half up ครั้งเดียวตอนท้าย ไม่ใช้ float

## หลักฐาน
- iter 1 · t4-cashback-r3, t4-cashback-r2: ใช้ `//` ปัดลง · half_up พลาด 3/3, no_drift พลาด 2/3
- iter 1 · t1-cafe-bill-r1: `(total*num*2 + den) // (den*2)` ผ่านครบ
- iter 1 · t3-shipping-fee-r2: `Fraction` แล้ว `math.floor(fee + Fraction(1, 2))` ผ่านครบ
- iter 1 · t2-split-bill-r4: `(total*tip_percent + 50) // 100` ผ่านครบ

## วิธีแก้
เมื่อโจทย์ไม่ระบุการปัด ให้ใช้ half up เสมอ ห้ามเลือกปัดลงเอง
- คิดเป็นเศษส่วน `num/den` ด้วยจำนวนเต็มทุกขั้น (ส่วนลดคูณ `95/100` ไม่ปัดระหว่างทาง) แล้วปัดครั้งเดียวสุดท้าย
- สำหรับค่าไม่ติดลบ: `(num * 2 + den) // (den * 2)`
- ตัวอย่าง cashback: `(amount * rate + 500) // 1000` แล้วค่อย `min(..., CAP)` ตรวจ 10020 gold → 251 ✓
- ห้ามใช้ `round()` (ปัดแบบ banker's) และห้ามใช้ float


## Execution traces (sampled: 5 failing + 3 passing)

<trace id="t4-cashback-r6">
# Trace t4-cashback-r6 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก
- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = "silver" "gold" หรือ "platinum" · `birthday` = True คือซื้อในเดือนเกิด
- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%
- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
- เดือนเกิด ได้เงินคืน 2 เท่า
- เงินคืนสูงสุด 200 บาทต่อบิล
- คืนเงินคืน เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✗ `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && cat ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
cafe_solve_checklist
```

### ขั้น 2 · Bash

```
ls -R ./skills; cat ./skills/*/* 2>/dev/null | head -100
```

ผลที่ได้:

```
./skills:
cafe_solve_checklist

./skills/cafe_solve_checklist:
PURPOSE.md
SKILL.md
# PURPOSE

## Origin
สร้างใน iteration 1 จาก Trace ทั้ง 24 ไฟล์ (t1–t4) ที่ได้ 0.30–0.50 เพราะ Agent ทำตามตัวอักษรของโจทย์ แล้วทดสอบเองแค่กรณีปกติ จึงพลาดข้อตรวจที่ไม่ได้เขียนในโจทย์

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-json-wrapper-missing.md (cli_ok, cli_error)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/rounding-exact-half-up.md (half_up, no_drift)
- wiki/patterns/happy-path-only-self-check.md (เช็กลิสต์ก่อนส่งงาน)

## Evolution History
- iter 1: สร้างสกิลครั้งแรก รวม 4 ข้อบังคับ (validation, half up, CLI wrapper, test_solve.py)
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย
…(ตัด 2662 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys

_RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per 1000
_MIN_AMOUNT = 10000  # 100 baht in satang
_CAP = 20000         # 200 baht in satang


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def cashback(amount, tier, birthday):
    amount = _int(amount, lo=0)
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"invalid tier: {tier!r}")
    birthday = _flag(birthday)
    if amount < _MIN_AMOUNT:
        return 0
    num = amount * _RATES[tier] * (2 if birthday else 1)
    den = 1000
    result = (num * 2 + den) // (den * 2)  # half up, once
    return min(result, _CAP)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(0, "gold", True), 0)
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)  # exactly 20000
        self.assertEqual(cashback(499999, "platinum", False), 20000)  # 19999.96 -> 20000
        self.assertEqual(cashback(499900, "platinum", False), 19996)
        self.assertEqual(cashback(600000, "platinum", True), 20000)

    def test_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10050, "silver", False), 151)  # 150.75
        self.assertEqual(cashback(10030, "gold", False), 251)   # 250.75
        self.assertEqual(cashback(10020, "silver", False), 150)  # 150.3
        self.assertEqual(cashback(10100, "silver", False), 152)  # 151.5 -> 152
        self.assertEqual(cashback(10300, "silver", False), 155)  # 154.5 -> 155

    def test_reject(self):
        for args in [(-1, "gold", False), (10000.0, "gold", False),
                     (True, "gold", False), ("100", "gold", False),
                     (10000, "bronze", False), (10000, None, False),
                     (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":-1,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
{"ok": true, "result": 1000}
0
{"ok": false, "error": "out of range: -1"}
2
```

**Agent พูด:** เขียน `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว unittest ผ่านทั้ง 5 ชุด และรันผ่าน CLI ได้ทั้งกรณีปกติ (exit 0) และกรณีอินพุตผิด (exit 2)

ผมทำตามสกิล `cafe_solve_checklist` ที่อยู่ใน `./skills` ด้วย:
- **ตรวจอินพุต:** ถ้า `amount` ติดลบ เป็น float หรือ bool, `tier` ไม่ใช่ silver/gold/platinum หรือ `birthday` ไม่ใช่ bool จะ raise `ValueError`
- **ยอดต่ำกว่า 100 บาท (10,000 สตางค์):** คืน 0
- **การคิดเงินคืน:** คิดเป็นจำนวนเต็มโดยไม่ใช้ float ปัดเศษแบบ half up ครั้งเดียว แล้วจึงจำกัดเพดาน 20,000 สตางค์ (200 บาท)
- **เดือนเกิด:** คูณ 2 ก่อนปัดเศษ ผลต่างจากการปัดก่อนแล้วคูณ 2 เกิดได้เพียง 1 สตางค์
- **CLI:** อ่าน JSON จาก stdin และพิมพ์ผลเป็น `{"ok": ..., ...}`

โจทย์ไม่ได้ระบุวิธีปัดเศษ ผมจึงใช้ half up ตามที่สกิลกำหนด

## คำตอบสุดท้ายของ Agent

เขียน `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว unittest ผ่านทั้ง 5 ชุด และรันผ่าน CLI ได้ทั้งกรณีปกติ (exit 0) และกรณีอินพุตผิด (exit 2)

ผมทำตามสกิล `cafe_solve_checklist` ที่อยู่ใน `./skills` ด้วย:
- **ตรวจอินพุต:** ถ้า `amount` ติดลบ เป็น float หรือ bool, `tier` ไม่ใช่ silver/gold/platinum หรือ `birthday` ไม่ใช่ bool จะ raise `ValueError`
- **ยอดต่ำกว่า 100 บาท (10,000 สตางค์):** คืน 0
- **การคิดเงินคืน:** คิดเป็นจำนวนเต็มโดยไม่ใช้ float ปัดเศษแบบ half up ครั้งเดียว แล้วจึงจำกัดเพดาน 20,000 สตางค์ (200 บาท)
- **เดือนเกิด:** คูณ 2 ก่อนปัดเศษ ผลต่างจากการปัดก่อนแล้วคูณ 2 เกิดได้เพียง 1 สตางค์
- **CLI:** อ่าน JSON จาก stdin และพิมพ์ผลเป็น `{"ok": ..., ...}`

โจทย์ไม่ได้ระบุวิธีปัดเศษ ผมจึงใช้ half up ตามที่สกิลกำหนด

</trace>

<trace id="t1-cafe-bill-r5">
# Trace t1-cafe-bill-r5 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน
- `items` = list ของ dict `{"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (ตั้งแต่ 1)}`
- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%
- `member` = True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✗ `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls -R ./skills 2>/dev/null | head -50
```

ผลที่ได้:

```
./skills:
cafe_solve_checklist

./skills/cafe_solve_checklist:
PURPOSE.md
SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_solve_checklist/*.md
```

ผลที่ได้:

```
# PURPOSE

## Origin
สร้างใน iteration 1 จาก Trace ทั้ง 24 ไฟล์ (t1–t4) ที่ได้ 0.30–0.50 เพราะ Agent ทำตามตัวอักษรของโจทย์ แล้วทดสอบเองแค่กรณีปกติ จึงพลาดข้อตรวจที่ไม่ได้เขียนในโจทย์

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-json-wrapper-missing.md (cli_ok, cli_error)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/rounding-exact-half-up.md (half_up, no_drift)
- wiki/patterns/happy-path-only-self-check.md (เช็กลิสต์ก่อนส่งงาน)

## Evolution History
- iter 1: สร้างสกิลครั้งแรก รวม 4 ข้อบังคับ (validation, half up, CLI wrapper, test_solve.py)
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด ret
…(ตัด 2579 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    member = _flag(member)
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("each item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item needs price and qty")
        total += _int(it["price"], lo=0) * _int(it["qty"], lo=1)

    num, den = total, 1
    if total >= 50000:          # 500 baht in satang
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (num * 2 + den) // (den * 2)   # half up, once


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], True), 19260)

    def test_threshold(self):
        # 49999 -> no discount: 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000 -> 5%: 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)
        # 50000 member: *0.95*0.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], True), 0)

    def test_reject(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": True}], False),
            ([{"price": 100}], False),
            (["x"], False),
            ("x", False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": "100", "qty": 1}], False),
        ]
        for items, m in bad:
            with self.subTest(items=items, m=m):
                with self.assertRaises(ValueError):
                    cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"items":[{"price":10000,"qty":2}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":10000,"qty":0}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
{"ok": true, "result": 19260}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว ชุดทดสอบ 5 ชุดใน `test_solve.py` ผ่านหมด และรันผ่าน CLI ได้ทั้งกรณีปกติ (exit 0) กับกรณีอินพุตผิด (exit 2)

ฉันอ่านสกิล `cafe_solve_checklist` ก่อนเริ่มและทำตามนั้น จึงมีส่วนที่เกินโจทย์: การตรวจอินพุต, CLI ที่รับ JSON ทาง stdin และไฟล์ทดสอบ

**การคิดเงิน**
- ยอดรวม = ผลรวมของ `price × qty` หน่วยสตางค์
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยจำนวนเต็มล้วน ไม่ใช้ float และปัดเศษแบบ half up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`

**ตัวอย่างที่ตรวจแล้ว**
- สินค้า 10,000 สตางค์ 2 ชิ้น ไม่เป็นสมาชิก ได้ 21,400
- ชุดเดียวกันแต่เป็นสมาชิก ได้ 19,260
- ยอด 49,999 ไม่ลด ได้ 53,499 ส่วนยอด 50,000 ลด 5% ได้ 50,825
- ยอด 50 บวก VAT ได้ 53.5 ปัดเป็น 54

**การตรวจอินพ
…(ตัด 428 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว ชุดทดสอบ 5 ชุดใน `test_solve.py` ผ่านหมด และรันผ่าน CLI ได้ทั้งกรณีปกติ (exit 0) กับกรณีอินพุตผิด (exit 2)

ฉันอ่านสกิล `cafe_solve_checklist` ก่อนเริ่มและทำตามนั้น จึงมีส่วนที่เกินโจทย์: การตรวจอินพุต, CLI ที่รับ JSON ทาง stdin และไฟล์ทดสอบ

**การคิดเงิน**
- ยอดรวม = ผลรวมของ `price × qty` หน่วยสตางค์
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยจำนวนเต็มล้วน ไม่ใช้ float และปัดเศษแบบ half up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`

**ตัวอย่างที่ตรวจแล้ว**
- สินค้า 10,000 สตางค์ 2 ชิ้น ไม่เป็นสมาชิก ได้ 21,400
- ชุดเดียวกันแต่เป็นสมาชิก ได้ 19,260
- ยอด 49,999 ไม่ลด ได้ 53,499 ส่วนยอด 50,000 ลด 5% ได้ 50,825
- ยอด 50 บวก VAT ได้ 53.5 ปัดเป็น 54

**การตรวจอินพุต** ค่าที่ผิดจะ `raise ValueError`:
- `price` ต้องเป็น int ตั้งแต่ 0
- `qty` ต้องเป็น int ตั้งแต่ 1
- float, bool, string และ item ที่ขาด key เช่น `price` หรือ `qty` ถูกปฏิเสธ
- `member` ต้องเป็น bool

ข้อกำหนดบางอย่างโจทย์ไม่ได้ระบุ ฉันจึงตั้งเองดังนี้:
- `price` เป็น 0 ได้
- `items` เป็น list ว่างได้ และคืน 0

ถ้าต้องการให้ list ว่างหรือราคา 0 ถูกปฏิเสธ บอกได้เลย

ไฟล์อยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`

</trace>

<trace id="t3-shipping-fee-r2">
# Trace t3-shipping-fee-r2 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `shipping_fee(weight_g, distance_km, express)` ในไฟล์ `solve.py` สำหรับคิดค่าส่งเมล็ดกาแฟ
- `weight_g` = น้ำหนัก 1–30,000 กรัม · `distance_km` = ระยะทาง (ตั้งแต่ 0) · `express` = True คือส่งด่วน
- ไม่เกิน 1,000 กรัม 40 บาท · ไม่เกิน 5,000 กรัม 80 บาท · เกิน 5,000 กรัม 80 บาท บวกส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
- คืนค่าส่ง เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✗ `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && find ./skills -type f | head -50
```

ผลที่ได้:

```
cafe_solve_checklist
./skills/cafe_solve_checklist/PURPOSE.md
./skills/cafe_solve_checklist/SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_solve_checklist/SKILL.md ./skills/cafe_solve_checklist/PURPOSE.md
```

ผลที่ได้:

```
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด return 0)
ทุกอินพุตผิดช่วง/ผิดชนิดต้อง `raise ValueError` (ห้ามปล่อยให้เป็น ZeroDivisionError/TypeError/KeyError)
```python
def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):   # ปฏิเสธ bool และ float เช่น 20000.0
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x

def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x
```
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์ ("ตั้งแต่ 0" → lo=0, "ตั้งแต่ 1" → lo=
…(ตัด 2579 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys
from fractions import Fraction


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def shipping_fee(weight_g, distance_km, express):
    weight_g = _int(weight_g, 1, 30000)
    distance_km = _int(distance_km, 0)
    express = _flag(express)

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return (fee.numerator * 2 + fee.denominator) // (fee.denominator * 2)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)
        self.assertEqual(f(10000, 200, True), 27900)

    def test_edges(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> half up
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)
        self.assertEqual(f(1, 0, True), 6000)
        self.assertEqual(f(30000, 0, False), 45500)

    def test_half(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5003, 0, False), 8005)

    def test_reject(self):
        for args in [(0, 1, False), (30001, 1, False), (-1, 1, False),
                     (1, -1, False), (1000.0, 1, False), (True, 1, False),
                     ("5", 1, False), (1, 1.0, False), (1, 1, 1),
                     (1, 1, None), (None, 1, False)]:
            with self.assertRaises(ValueError):
                f(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"weight_g":10000,"distance_km":200,"express":true}' | python3 solve.py; echo $?
echo '{"weight_g":0,"distance_km":2,"express":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 27900}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** เขียน `solve.py` และ `test_solve.py` เสร็จแล้ว unittest 4 ตัวผ่านทั้งหมด และ CLI ทำงานตามที่คาด ตัวอย่าง 10,000 กรัม, 200 กม., ส่งด่วน ได้ 27900 สตางค์ (exit 0) ส่วนน้ำหนัก 0 กรัมได้ error JSON และ exit 2

ผมทำตามสกิล `cafe_solve_checklist` ใน `./skills` ซึ่งเพิ่มข้อที่โจทย์ไม่ได้เขียนไว้:

- **ตรวจอินพุต:** ถ้าอินพุตผิดช่วงหรือผิดชนิด ฟังก์ชันจะ `raise ValueError`
  - `weight_g` ต้องเป็นจำนวนเต็ม 1–30,000
  - `distance_km` ต้องเป็นจำนวนเต็มตั้งแต่ 0
  - `express` ต้องเป็น bool
  - ค่า float เช่น `1000.0` และ bool ที่ส่งมาแทนตัวเลขจะถูกปฏิเสธ
- **ปัดเศษ:** คิดเป็นเศษส่วนด้วย `Fraction` ตลอด แล้วปัดแบบ half up ครั้งเดียวตอนท้าย เช่น 5,001 กรัมได้ 8001.5 สตางค์ ปัดเป็น 8002
- **ลำดับคิด:** ค่าส่งตามน้ำหนัก แล้วคูณ 1.2 ถ้าเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **CLI:** `solve.py` อ่าน JSON จาก
…(ตัด 171 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `solve.py` และ `test_solve.py` เสร็จแล้ว unittest 4 ตัวผ่านทั้งหมด และ CLI ทำงานตามที่คาด ตัวอย่าง 10,000 กรัม, 200 กม., ส่งด่วน ได้ 27900 สตางค์ (exit 0) ส่วนน้ำหนัก 0 กรัมได้ error JSON และ exit 2

ผมทำตามสกิล `cafe_solve_checklist` ใน `./skills` ซึ่งเพิ่มข้อที่โจทย์ไม่ได้เขียนไว้:

- **ตรวจอินพุต:** ถ้าอินพุตผิดช่วงหรือผิดชนิด ฟังก์ชันจะ `raise ValueError`
  - `weight_g` ต้องเป็นจำนวนเต็ม 1–30,000
  - `distance_km` ต้องเป็นจำนวนเต็มตั้งแต่ 0
  - `express` ต้องเป็น bool
  - ค่า float เช่น `1000.0` และ bool ที่ส่งมาแทนตัวเลขจะถูกปฏิเสธ
- **ปัดเศษ:** คิดเป็นเศษส่วนด้วย `Fraction` ตลอด แล้วปัดแบบ half up ครั้งเดียวตอนท้าย เช่น 5,001 กรัมได้ 8001.5 สตางค์ ปัดเป็น 8002
- **ลำดับคิด:** ค่าส่งตามน้ำหนัก แล้วคูณ 1.2 ถ้าเกิน 100 กม. แล้วคูณ 1.5 ถ้าส่งด่วน
- **CLI:** `solve.py` อ่าน JSON จาก stdin ได้ ถ้าผิดพลาดจะพิมพ์ error JSON และ exit 2

เพราะสกิลกำหนดให้ตรวจเป็นจำนวนเต็ม ระยะทางที่เป็นทศนิยม เช่น `100.5` จึงถูกปฏิเสธ ถ้าต้องการรับระยะทางทศนิยม บอกได้ครับ

</trace>

<trace id="t2-split-bill-r4">
# Trace t2-split-bill-r4 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `split_bill(total, people, tip_percent)` ในไฟล์ `solve.py` สำหรับหารบิล
- `total` = ยอดบิล (สตางค์ ตั้งแต่ 0) · `people` = จำนวนคน (ตั้งแต่ 1) · `tip_percent` = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0–100)
- ยอดที่ต้องหาร = ยอดบิลบวกทิป
- หารเท่ากันทุกคน ถ้าหารไม่ลงตัว ให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ
- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✗ `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
cafe_solve_checklist
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/cafe_solve_checklist/* 2>/dev/null
```

ผลที่ได้:

```
./skills/cafe_solve_checklist/PURPOSE.md
./skills/cafe_solve_checklist/SKILL.md
# PURPOSE

## Origin
สร้างใน iteration 1 จาก Trace ทั้ง 24 ไฟล์ (t1–t4) ที่ได้ 0.30–0.50 เพราะ Agent ทำตามตัวอักษรของโจทย์ แล้วทดสอบเองแค่กรณีปกติ จึงพลาดข้อตรวจที่ไม่ได้เขียนในโจทย์

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-json-wrapper-missing.md (cli_ok, cli_error)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/rounding-exact-half-up.md (half_up, no_drift)
- wiki/patterns/happy-path-only-self-check.md (เช็กลิสต์ก่อนส่งงาน)

## Evolution History
- iter 1: สร้างสกิลครั้งแรก รวม 4 ข้อบังคับ (validation, half up, CLI wrapper, test_solve.py)
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม
…(ตัด 2659 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def split_bill(total, people, tip_percent):
    total = _int(total, 0)
    people = _int(people, 1)
    tip_percent = _int(tip_percent, 0, 100)
    num = total * (100 + tip_percent)
    grand = (num * 2 + 100) // 200  # half up, once
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = split_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_half_up(self):
        self.assertEqual(split_bill(10, 1, 5), [11])   # 10.5 -> 11
        self.assertEqual(split_bill(30, 1, 5), [32])   # 31.5 -> 32
        self.assertEqual(split_bill(9, 1, 5), [9])     # 9.45 -> 9

    def test_reject(self):
        for args in [(-1, 1, 0), (100, 0, 0), (100, 1, -1), (100, 1, 101),
                     (100.0, 1, 0), (100, 1.0, 0), (100, 1, 10.0),
                     (True, 1, 0), (100, True, 0), ("100", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"total":10000,"people":3,"tip_percent":10}' | python3 solve.py; echo $?
echo '{"total":10000,"people":0,"tip_percent":10}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 4 tests in 0.000s

OK
{"ok": true, "result": [3667, 3667, 3666]}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว unittest 4 ชุดผ่านทั้งหมด และ CLI ให้ผลตามที่คาด (ข้อมูลปกติ exit 0, `people` เป็น 0 แล้ว exit 2 พร้อม JSON แจ้ง error)

ฉันอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตามนั้น ส่วนที่เกินจากโจทย์คือการตรวจอินพุต การปัดเศษ และการรันเป็น CLI

- **ยอดที่ต้องหาร:** คิดเป็น `total × (100 + tip_percent) / 100` ด้วยจำนวนเต็ม แล้วปัดเศษแบบ half up ครั้งเดียว เช่น 10 สตางค์ + ทิป 5% = 10.5 ปัดเป็น 11 โจทย์ไม่ได้บอกวิธีปัด ฉันเลือก half up ตามที่สกิลกำหนด
- **การหาร:** ใช้ `divmod` แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ เช่น 10000 สตางค์ หาร 3 คน ได้ `[3334, 3333, 3333]`
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError` ได้แก่ ค่านอกช่วง, float, bool และชนิดข้อมูลผิด
- **CLI:** รับ JSON จาก stdin แล้วพิมพ์ `{"ok": true
…(ตัด 69 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว unittest 4 ชุดผ่านทั้งหมด และ CLI ให้ผลตามที่คาด (ข้อมูลปกติ exit 0, `people` เป็น 0 แล้ว exit 2 พร้อม JSON แจ้ง error)

ฉันอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตามนั้น ส่วนที่เกินจากโจทย์คือการตรวจอินพุต การปัดเศษ และการรันเป็น CLI

- **ยอดที่ต้องหาร:** คิดเป็น `total × (100 + tip_percent) / 100` ด้วยจำนวนเต็ม แล้วปัดเศษแบบ half up ครั้งเดียว เช่น 10 สตางค์ + ทิป 5% = 10.5 ปัดเป็น 11 โจทย์ไม่ได้บอกวิธีปัด ฉันเลือก half up ตามที่สกิลกำหนด
- **การหาร:** ใช้ `divmod` แล้วให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ เช่น 10000 สตางค์ หาร 3 คน ได้ `[3334, 3333, 3333]`
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError` ได้แก่ ค่านอกช่วง, float, bool และชนิดข้อมูลผิด
- **CLI:** รับ JSON จาก stdin แล้วพิมพ์ `{"ok": true, "result": [...]}` ถ้าผิดพลาดจะพิมพ์ `{"ok": false, ...}` และ exit 2

</trace>

<trace id="t4-cashback-r4">
# Trace t4-cashback-r4 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 2 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก
- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = "silver" "gold" หรือ "platinum" · `birthday` = True คือซื้อในเดือนเกิด
- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%
- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
- เดือนเกิด ได้เงินคืน 2 เท่า
- เงินคืนสูงสุด 200 บาทต่อบิล
- คืนเงินคืน เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✗ `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
cafe_solve_checklist
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด return 0)
ทุกอินพุตผิดช่วง/ผิดชนิดต้อง `raise ValueError` (ห้ามปล่อยให้เป็น ZeroDivisionError/TypeError/KeyError)
```python
def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):   # ปฏิเสธ bool และ float เช่น 20000.0
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x

def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x
```
- ใช้ `_int` กับทุกพารามิเตอร์ตัวเลข ช่วงตามโจทย์ ("ตั้งแต่ 0" → lo
…(ตัด 1967 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
import json
import sys
from fractions import Fraction

_RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}
_MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
_CAP = 20000          # 200 บาท (สตางค์)


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def cashback(amount, tier, birthday):
    _int(amount, lo=0)
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"invalid tier: {tier!r}")
    _flag(birthday)
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier] * (2 if birthday else 1)
    num, den = value.numerator, value.denominator
    rounded = (num * 2 + den) // (den * 2)  # half up ครั้งเดียว
    return int(min(rounded, _CAP))


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(10001, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(1000000, "gold", False), 20000 if False else 25000 and 20000)

    def test_rounding_half(self):
        # 10100*0.015 = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        # 10020*0.025 = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_reject(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False), (True, "gold", False),
                     ("100", "gold", False), (20000, "bronze", False), (20000, None, False),
                     (20000, "gold", 1), (20000, "gold", None), (-1, "x", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
sed -i 's/20000 if False else 25000 and 20000/20000/' test_solve.py
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":-1,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
{"ok": true, "result": 1000}
0
{"ok": false, "error": "out of range: -1"}
2
```

**Agent พูด:** เขียน `solve.py` และ `test_solve.py` เสร็จแล้ว ทดสอบผ่านทั้ง 5 เคสและลองรันแบบ CLI แล้ว ตามเช็กลิสต์ใน `./skills/cafe_solve_checklist`

- **ตรวจอินพุตก่อนทุกอย่าง:**
  - `amount` ต้องเป็น int ตั้งแต่ 0 ขึ้นไป (ไม่รับ float หรือ bool)
  - `tier` ต้องเป็น silver, gold หรือ platinum
  - `birthday` ต้องเป็น bool
  - ถ้าผิดจะ `raise ValueError`
- **ยอดต่ำกว่า 10,000 สตางค์ (100 บาท):** คืน 0 ส่วนยอดพอดี 10,000 ได้เงินคืน
- **การคิดเงินคืน:** คิดด้วย `Fraction` (silver 3/200, gold 1/40, platinum 1/25) คูณ 2 ถ้าเป็นเดือนเกิด แล้วปัดครึ่งขึ้นครั้งเดียว
- **เพดาน:** จำกัดไม่เกิน 20,000 สตางค์ (200 บาท) หลังปัดเศษ
- **CLI:** รับ JSON ทาง stdin ถ้าสำเร็จจะพิมพ์ `{"ok": true, "result": ...}` และ exit 0 ถ้าผิดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2
  - ตัวอย่างที่ลอง: gold ยอด 20,000 เดือนเกิด
…(ตัด 193 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `solve.py` และ `test_solve.py` เสร็จแล้ว ทดสอบผ่านทั้ง 5 เคสและลองรันแบบ CLI แล้ว ตามเช็กลิสต์ใน `./skills/cafe_solve_checklist`

- **ตรวจอินพุตก่อนทุกอย่าง:**
  - `amount` ต้องเป็น int ตั้งแต่ 0 ขึ้นไป (ไม่รับ float หรือ bool)
  - `tier` ต้องเป็น silver, gold หรือ platinum
  - `birthday` ต้องเป็น bool
  - ถ้าผิดจะ `raise ValueError`
- **ยอดต่ำกว่า 10,000 สตางค์ (100 บาท):** คืน 0 ส่วนยอดพอดี 10,000 ได้เงินคืน
- **การคิดเงินคืน:** คิดด้วย `Fraction` (silver 3/200, gold 1/40, platinum 1/25) คูณ 2 ถ้าเป็นเดือนเกิด แล้วปัดครึ่งขึ้นครั้งเดียว
- **เพดาน:** จำกัดไม่เกิน 20,000 สตางค์ (200 บาท) หลังปัดเศษ
- **CLI:** รับ JSON ทาง stdin ถ้าสำเร็จจะพิมพ์ `{"ok": true, "result": ...}` และ exit 0 ถ้าผิดจะพิมพ์ `{"ok": false, "error": ...}` และ exit 2
  - ตัวอย่างที่ลอง: gold ยอด 20,000 เดือนเกิด ได้ 1000
  - ยอด -1 ได้ error และ exit 2

เคสทดสอบครอบคลุมค่าขอบที่ 9,999 / 10,000 / 10,001 เพดาน เคสปัดเศษที่เศษ .5 พอดี (10,100 silver ได้ 152, 10,020 gold ได้ 251) และอินพุตที่ต้องถูกปฏิเสธ

</trace>

<trace id="t1-cafe-bill-r1">
# Trace t1-cafe-bill-r1 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน
- `items` = list ของ dict `{"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (ตั้งแต่ 1)}`
- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%
- `member` = True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls -R ./skills 2>/dev/null | head -50
```

ผลที่ได้:

```
./skills:
cafe_solve_checklist

./skills/cafe_solve_checklist:
PURPOSE.md
SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_solve_checklist/*.md
```

ผลที่ได้:

```
# PURPOSE

## Origin
สร้างใน iteration 1 จาก Trace ทั้ง 24 ไฟล์ (t1–t4) ที่ได้ 0.30–0.50 เพราะ Agent ทำตามตัวอักษรของโจทย์ แล้วทดสอบเองแค่กรณีปกติ จึงพลาดข้อตรวจที่ไม่ได้เขียนในโจทย์

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-json-wrapper-missing.md (cli_ok, cli_error)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/rounding-exact-half-up.md (half_up, no_drift)
- wiki/patterns/happy-path-only-self-check.md (เช็กลิสต์ก่อนส่งงาน)

## Evolution History
- iter 1: สร้างสกิลครั้งแรก รวม 4 ข้อบังคับ (validation, half up, CLI wrapper, test_solve.py)
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด ret
…(ตัด 2579 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    member = _flag(member)
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item needs price and qty")
        total += _int(it["price"], lo=0) * _int(it["qty"], lo=1)

    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (num * 2 + den) // (den * 2)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(6000), it(4000, 2)], False), 14980)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 53498.93
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50825
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 50825.95

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)
        self.assertEqual(cafe_bill([it(50000)], True), 45742.5 and 45743)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_reject(self):
        bad = [
            ([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
            ([it(100, 1.0)], False), ([it(True)], False), ([{"price": 1}], False),
            ("x", False), ([5], False), ([it(100)], 1), ([it(100)], None),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -5
echo '{"items":[{"price":10000,"qty":2}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":10000,"qty":0}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
......
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
{"ok": true, "result": 19260}
0
{"ok": false, "error": "out of range: 0"}
2
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และมี `test_solve.py` ข้างกัน unittest ผ่านทั้ง 6 เคส ส่วนการรันเป็น CLI ก็ทดสอบแล้ว: อินพุตปกติ exit 0 และอินพุตผิด exit 2 พร้อม JSON

ก่อนเริ่มผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตาม ซึ่งเป็นที่มาของการตรวจอินพุต CLI และไฟล์ทดสอบ ที่โจทย์ไม่ได้ขอ

- **ลำดับการคิด:** รวมยอด (`price × qty`) → ลด 5% ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป → ลดอีก 10% ถ้าเป็นสมาชิก → บวก VAT 7%
- **การปัดเศษ:** คิดเป็นเศษส่วนด้วยจำนวนเต็มทุกขั้น แล้วปัดครั้งเดียวตอนท้ายแบบ half up คืนค่าเป็น `int` สตางค์
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError` ได้แก่
  - `price` ต่ำกว่า 0 (ผมตั้งช่วงนี้เอง เพราะโจทย์ไม่ได้ระบุราคาขั้นต่ำ)
  - `qty` ต่ำกว่า 1
  - ค่าที่เป็น float หรือ bool
  - item ที่ขาด key
  - `items` ที่ไม่ใช
…(ตัด 159 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และมี `test_solve.py` ข้างกัน unittest ผ่านทั้ง 6 เคส ส่วนการรันเป็น CLI ก็ทดสอบแล้ว: อินพุตปกติ exit 0 และอินพุตผิด exit 2 พร้อม JSON

ก่อนเริ่มผมอ่านสกิล `cafe_solve_checklist` ใน `./skills` แล้วทำตาม ซึ่งเป็นที่มาของการตรวจอินพุต CLI และไฟล์ทดสอบ ที่โจทย์ไม่ได้ขอ

- **ลำดับการคิด:** รวมยอด (`price × qty`) → ลด 5% ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป → ลดอีก 10% ถ้าเป็นสมาชิก → บวก VAT 7%
- **การปัดเศษ:** คิดเป็นเศษส่วนด้วยจำนวนเต็มทุกขั้น แล้วปัดครั้งเดียวตอนท้ายแบบ half up คืนค่าเป็น `int` สตางค์
- **การตรวจอินพุต:** ถ้าอินพุตผิดจะ raise `ValueError` ได้แก่
  - `price` ต่ำกว่า 0 (ผมตั้งช่วงนี้เอง เพราะโจทย์ไม่ได้ระบุราคาขั้นต่ำ)
  - `qty` ต่ำกว่า 1
  - ค่าที่เป็น float หรือ bool
  - item ที่ขาด key
  - `items` ที่ไม่ใช่ list
  - `member` ที่ไม่ใช่ bool
- **รายการว่าง:** `items=[]` ให้ผลเป็น 0

ตัวอย่างที่รันดู: สินค้าราคา 10000 สตางค์ จำนวน 2 ชิ้น เป็นสมาชิก ได้ 19260 สตางค์

</trace>

<trace id="t4-cashback-r5">
# Trace t4-cashback-r5 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ไม่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cashback(amount, tier, birthday)` ในไฟล์ `solve.py` สำหรับคิดเงินคืนสมาชิก
- `amount` = ยอดซื้อ (สตางค์ ตั้งแต่ 0) · `tier` = "silver" "gold" หรือ "platinum" · `birthday` = True คือซื้อในเดือนเกิด
- อัตราเงินคืน: silver 1.5% · gold 2.5% · platinum 4%
- ยอดซื้อต่ำกว่า 100 บาท ไม่ได้เงินคืน
- เดือนเกิด ได้เงินคืน 2 เท่า
- เงินคืนสูงสุด 200 บาทต่อบิล
- คืนเงินคืน เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
cafe_solve_checklist
```

### ขั้น 2 · Bash

```
find ./skills -type f | xargs -I{} sh -c 'echo "== {}"; cat {}'
```

ผลที่ได้:

```
== ./skills/cafe_solve_checklist/PURPOSE.md
# PURPOSE

## Origin
สร้างใน iteration 1 จาก Trace ทั้ง 24 ไฟล์ (t1–t4) ที่ได้ 0.30–0.50 เพราะ Agent ทำตามตัวอักษรของโจทย์ แล้วทดสอบเองแค่กรณีปกติ จึงพลาดข้อตรวจที่ไม่ได้เขียนในโจทย์

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-json-wrapper-missing.md (cli_ok, cli_error)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/rounding-exact-half-up.md (half_up, no_drift)
- wiki/patterns/happy-path-only-self-check.md (เช็กลิสต์ก่อนส่งงาน)

## Evolution History
- iter 1: สร้างสกิลครั้งแรก รวม 4 ข้อบังคับ (validation, half up, CLI wrapper, test_solve.py)
== ./skills/cafe_solve_checklist/SKILL.md
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โ
…(ตัด 2665 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys
from fractions import Fraction


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


_RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
_MIN_AMOUNT = 10000  # 100 baht in satang
_CAP = 20000         # 200 baht in satang


def cashback(amount, tier, birthday):
    amount = _int(amount, lo=0)
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"invalid tier: {tier!r}")
    birthday = _flag(birthday)

    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier]
    if birthday:
        value *= 2
    num, den = value.numerator, value.denominator
    result = (num * 2 + den) // (den * 2)  # half up
    return int(min(result, _CAP))


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_half_up(self):
        # 10010 * 0.015 = 150.15 -> 150 ; 10100*0.015=151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        self.assertEqual(cashback(10010, "silver", False), 150)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(10**9, "platinum", True), 20000)

    def test_reject(self):
        bad = [(-1, "gold", False), (20000.0, "gold", False),
               (True, "gold", False), ("100", "gold", False),
               (None, "gold", False), (20000, "bronze", False),
               (20000, None, False), (20000, "gold", 1),
               (20000, "gold", None)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -3
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
echo '{"amount":-1,"tier":"gold","birthday":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
Ran 6 tests in 0.000s

OK
{"ok": true, "result": 1000}
0
{"ok": false, "error": "out of range: -1"}
2
```

**Agent พูด:** สร้างไฟล์ `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ทำตามเช็กลิสต์ใน `./skills/cafe_solve_checklist` ครบทุกข้อ รัน unittest ผ่านทั้ง 6 เทสต์ และลองรันเป็น CLI แล้ว ได้ exit 0 กรณีปกติ และ exit 2 กรณีอินพุตผิด

`cashback(amount, tier, birthday)` ทำงานตามลำดับนี้:
1. **ตรวจอินพุต:**
   - `amount` ต้องเป็น int ตั้งแต่ 0 (ไม่รับ float, bool หรือค่าติดลบ)
   - `tier` ต้องเป็น silver, gold หรือ platinum
   - `birthday` ต้องเป็น bool
   - ถ้าผิดจะ `raise ValueError`
2. **ยอดต่ำกว่า 10,000 สตางค์ (100 บาท):** คืน 0
3. **คำนวณ:** ใช้ `Fraction` คูณอัตรา (1.5%, 2.5% หรือ 4%) แล้วคูณ 2 ถ้าเป็นเดือนเกิด
4. **ปัดเศษ:** half up ครั้งเดียวเป็นจำนวนเต็มสตางค์
5. **เพดาน:** ไม่เกิน 20,000 สตางค์ (200 บาท)

ผ่าน CLI ด้วย JSON ที่ใช้ชื่อพารามิเตอร์เป็น key ผลลัพธ์จะเป็น `{"ok": true, "result": ..
…(ตัด 197 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้างไฟล์ `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว ทำตามเช็กลิสต์ใน `./skills/cafe_solve_checklist` ครบทุกข้อ รัน unittest ผ่านทั้ง 6 เทสต์ และลองรันเป็น CLI แล้ว ได้ exit 0 กรณีปกติ และ exit 2 กรณีอินพุตผิด

`cashback(amount, tier, birthday)` ทำงานตามลำดับนี้:
1. **ตรวจอินพุต:**
   - `amount` ต้องเป็น int ตั้งแต่ 0 (ไม่รับ float, bool หรือค่าติดลบ)
   - `tier` ต้องเป็น silver, gold หรือ platinum
   - `birthday` ต้องเป็น bool
   - ถ้าผิดจะ `raise ValueError`
2. **ยอดต่ำกว่า 10,000 สตางค์ (100 บาท):** คืน 0
3. **คำนวณ:** ใช้ `Fraction` คูณอัตรา (1.5%, 2.5% หรือ 4%) แล้วคูณ 2 ถ้าเป็นเดือนเกิด
4. **ปัดเศษ:** half up ครั้งเดียวเป็นจำนวนเต็มสตางค์
5. **เพดาน:** ไม่เกิน 20,000 สตางค์ (200 บาท)

ผ่าน CLI ด้วย JSON ที่ใช้ชื่อพารามิเตอร์เป็น key ผลลัพธ์จะเป็น `{"ok": true, "result": ...}` ถ้าอินพุตผิดจะได้ `{"ok": false, "error": ...}` และ exit 2

เทสต์ครอบคลุมกรณีปกติ เดือนเกิด ค่าขอบ 9,999 และ 10,000 เศษ .5 พอดี (10,100 สตางค์ของ silver ได้ 152) เพดาน และอินพุตที่ต้องถูกปฏิเสธ

</trace>

<trace id="t1-cafe-bill-r3">
# Trace t1-cafe-bill-r3 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 5 ครั้ง · คำสั่งล้ม 0 ครั้ง · อ่านสกิล: ใช่

## โจทย์

ร้านกาแฟ BaanKafe ต้องการฟังก์ชัน `cafe_bill(items, member)` ในไฟล์ `solve.py` สำหรับคิดเงินหน้าร้าน
- `items` = list ของ dict `{"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (ตั้งแต่ 1)}`
- ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%
- `member` = True ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

## ผลของตัวตรวจ (Grader)

- ✓ `contract`
- ✓ `basic`
- ✓ `half_up`
- ✓ `no_drift`
- ✓ `boundary`
- ✓ `reject_value`
- ✓ `reject_type`
- ✓ `cli_ok`
- ✓ `cli_error`
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls -R ./skills 2>/dev/null | head -50
```

ผลที่ได้:

```
./skills:
cafe_solve_checklist

./skills/cafe_solve_checklist:
PURPOSE.md
SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_solve_checklist/*.md
```

ผลที่ได้:

```
# PURPOSE

## Origin
สร้างใน iteration 1 จาก Trace ทั้ง 24 ไฟล์ (t1–t4) ที่ได้ 0.30–0.50 เพราะ Agent ทำตามตัวอักษรของโจทย์ แล้วทดสอบเองแค่กรณีปกติ จึงพลาดข้อตรวจที่ไม่ได้เขียนในโจทย์

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-json-wrapper-missing.md (cli_ok, cli_error)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/rounding-exact-half-up.md (half_up, no_drift)
- wiki/patterns/happy-path-only-self-check.md (เช็กลิสต์ก่อนส่งงาน)

## Evolution History
- iter 1: สร้างสกิลครั้งแรก รวม 4 ข้อบังคับ (validation, half up, CLI wrapper, test_solve.py)
---
name: cafe_solve_checklist
description: เช็กลิสต์เขียน solve.py สำหรับโจทย์ฟังก์ชันคิดเงินร้าน BaanKafe (คิดบิล หารบิล ค่าส่ง เงินคืน) ให้ผ่านตัวตรวจทุกข้อ ทั้งอินพุตผิด CLI JSON การปัดเศษ และ test_solve.py
---

# When to Apply
- โจทย์ให้เขียนฟังก์ชัน Python ใน `solve.py` เกี่ยวกับเงิน/ราคา/สตางค์ ใช้ทุกครั้งก่อนส่งงาน

# When NOT to Apply
- งานที่ไม่ใช่การเขียน `solve.py` ตามโจทย์คิดเงิน

# Instructions
ตัวตรวจเช็กสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบ 4 ข้อนี้เสมอ แม้โจทย์ไม่ขอ:

## 1. ตรวจอินพุตเป็นอย่างแรกของฟังก์ชัน (ก่อนกติกาธุรกิจ และก่อนทางลัด ret
…(ตัด 2579 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys


def _int(x, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"expected int, got {x!r}")
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f"out of range: {x!r}")
    return x


def _flag(x):
    if not isinstance(x, bool):
        raise ValueError(f"expected bool, got {x!r}")
    return x


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    member = _flag(member)
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item needs price and qty")
        total += _int(it["price"], lo=0) * _int(it["qty"], lo=1)

    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return (num * 2 + den) // (den * 2)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    _main()
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(50001)], False), 50826)

    def test_member_discount_threshold(self):
        # 50000*.95*.9*1.07 = 45732.5 -> half up 45733
        self.assertEqual(cafe_bill([it(50000)], True), 45733)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_reject(self):
        bad = [
            ([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
            ([it(100, True)], False), ([it(100)], 1), ([it(100)], None),
            ("x", False), ([1], False), ([{"price": 1}], False),
            ([it("1")], False),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest test_solve 2>&1 | tail -4
echo '{"items":[{"price":10000,"qty":2}],"member":true}' | python3 solve.py; echo $?
echo '{"items":[{"price":10000,"qty":0}],"member":true}' | python3 solve.py; echo $?
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 6 tests in 0.001s

FAILED (failures=1)
{"ok": true, "result": 19260}
0
{"ok": false, "error": "out of range: 0"}
2
```

### ขั้น 4 · Bash

```
python3 -m unittest test_solve 2>&1 | head -15
```

ผลที่ได้:

```
...F..
======================================================================
FAIL: test_member_discount_threshold (test_solve.T.test_member_discount_threshold)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/w2-k02-train/t1-cafe-bill-r3/sandbox/test_solve.py", line 21, in test_member_discount_threshold
    self.assertEqual(cafe_bill([it(50000)], True), 45733)
AssertionError: 45743 != 45733

----------------------------------------------------------------------
Ran 6 tests in 0.000s

FAILED (failures=1)
```

**Agent พูด:** My test's arithmetic was wrong: 50000×0.95×0.9×1.07 = 45742.5, which rounds to 45743, so the code is right. I'll fix the test.

### ขั้น 5 · Bash

```
sed -i 's/45732.5 -> half up 45733/45742.5 -> half up 45743/; s/True), 45733)/True), 45743)/' test_solve.py && python3 -m unittest test_solve 2>&1 | tail -3
```

ผลที่ได้:

```
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และ unittest ทั้ง 6 ข้อใน `test_solve.py` ผ่านหมด ผมรัน CLI ทดสอบด้วย: อินพุตปกติได้ exit 0 และอินพุตผิดได้ exit 2

**วิธีคิดเงิน**
- ยอดรวม 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- `member=True` ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยเศษส่วนจำนวนเต็มตลอด แล้วปัดครั้งเดียวตอนท้ายแบบ half up (ปัดครึ่งขึ้น)

**ตามสกิล `cafe_solve_checklist`**
- ตรวจอินพุตก่อนคิดเงิน ถ้าผิดจะ raise `ValueError`
  - `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty`
  - `qty` ต้องเป็นจำนวนเต็มตั้งแต่ 1 ขึ้นไป
  - `price` ต้องเป็นจำนวนเต็มตั้งแต่ 0 ขึ้นไป โจทย์ไม่ได้กำหนดช่วงของราคา ผมจึงตั้งขั้นต่ำเป็น 0 เอง
  - ปฏิเสธ float และ bool
  - `member` ต้องเป็น bool เท่านั้น
- `items` เป็น list ว่างได้ และคืน 0
- `solve.py` รันเป็น CLI ได้ โดยอ่าน
…(ตัด 251 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และ unittest ทั้ง 6 ข้อใน `test_solve.py` ผ่านหมด ผมรัน CLI ทดสอบด้วย: อินพุตปกติได้ exit 0 และอินพุตผิดได้ exit 2

**วิธีคิดเงิน**
- ยอดรวม 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- `member=True` ลดอีก 10%
- บวก VAT 7% เป็นขั้นสุดท้าย
- คำนวณด้วยเศษส่วนจำนวนเต็มตลอด แล้วปัดครั้งเดียวตอนท้ายแบบ half up (ปัดครึ่งขึ้น)

**ตามสกิล `cafe_solve_checklist`**
- ตรวจอินพุตก่อนคิดเงิน ถ้าผิดจะ raise `ValueError`
  - `items` ต้องเป็น list ของ dict ที่มี `price` และ `qty`
  - `qty` ต้องเป็นจำนวนเต็มตั้งแต่ 1 ขึ้นไป
  - `price` ต้องเป็นจำนวนเต็มตั้งแต่ 0 ขึ้นไป โจทย์ไม่ได้กำหนดช่วงของราคา ผมจึงตั้งขั้นต่ำเป็น 0 เอง
  - ปฏิเสธ float และ bool
  - `member` ต้องเป็น bool เท่านั้น
- `items` เป็น list ว่างได้ และคืน 0
- `solve.py` รันเป็น CLI ได้ โดยอ่าน JSON จาก stdin แล้วคืน `{"ok": true, "result": ...}` ถ้าผิดจะคืน `{"ok": false, "error": ...}` และ exit 2

ตอนเขียนเทส ผมคำนวณค่าคาดหวังของเคสสมาชิกที่ยอด 50,000 พอดีผิดไปก่อน (ควรเป็น 45,743 ไม่ใช่ 45,733) ผมแก้ที่เทสแล้ว โค้ดใน `solve.py` ไม่ได้แก้

</trace>

ตอบเป็น JSON object ตามรูปแบบที่กำหนด