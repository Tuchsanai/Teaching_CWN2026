# Iteration 2

Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): 92.5%

## wiki/index.md

# Wiki Index

- [test-count-below-minimum](wiki/patterns/test-count-below-minimum.md): [ยังเกิดอยู่ iter 2: ข้อเดียวที่ล้ม 5/8 trace] ข้อ tests ล้มเพราะ test_solve.py มี method test_* แค่ 4–5 ตัว (ต้อง ≥ 6) เนื่องจากสกิลไม่ระบุจำนวนขั้นต่ำและตัวอย่างโครงมีแค่ 2 method ให้เขียนอย่างน้อย 8 method แยกหมวด (basic, ขอบ 3 แบบ, half_up, reject_value, reject_type, zero/cap) แล้วดู `Ran N tests` ก่อนจบ ตัวที่ผ่านทุกตัวมี 6 method
- [input-validation-missing](wiki/patterns/input-validation-missing.md): ฟังก์ชันไม่ตรวจอินพุต จึงคืนค่าปกติหรือ raise ZeroDivisionError เมื่อได้ค่านอกช่วง/float/bool (reject_value, reject_type) เพราะโจทย์บอกแค่ช่วงที่ถูก ให้ตรวจทุกพารามิเตอร์เป็นอย่างแรก (ปฏิเสธ bool และ float) แล้ว raise ValueError [แก้ได้แล้ว iter 2 ด้วย _int/_flag ในสกิล]
- [cli-json-wrapper-missing](wiki/patterns/cli-json-wrapper-missing.md): cli_ok/cli_error ล้มเพราะ solve.py มีแต่ฟังก์ชัน ไม่อ่าน stdin ซึ่งโจทย์ไม่ได้บอก ให้เพิ่ม main ที่อ่าน JSON จาก stdin พิมพ์ {"ok":true,"result":..} exit 0 และเมื่อผิดพิมพ์ {"ok":false,"error":..} exit 2 [แก้ได้แล้ว iter 2]
- [missing-test-file](wiki/patterns/missing-test-file.md): ข้อ tests ล้มเพราะไม่มี test_solve.py ข้าง solve.py (โจทย์ไม่ได้ขอ) ให้สร้างไฟล์ unittest ครอบคลุมกรณีปกติ ค่าขอบ ปัดเศษ และ ValueError แล้วรันให้ผ่าน [เรื่องไฟล์หายแก้ได้แล้ว iter 2 ส่วนจำนวนเทสต์ไม่พอดู test-count-below-minimum]
- [rounding-exact-half-up](wiki/patterns/rounding-exact-half-up.md): half_up/no_drift ล้มเมื่อเลือกปัดลง (//) เองตอนโจทย์ไม่ระบุ ส่วนข้อที่ผ่านใช้จำนวนเต็ม/Fraction แล้วปัด half up ครั้งเดียวท้ายสุด ใช้ (num*2+den)//(den*2) ห้าม float และ round() [แก้ได้แล้ว iter 2]
- [happy-path-only-self-check](wiki/patterns/happy-path-only-self-check.md): Agent ทดสอบเองแค่ตัวอย่างปกติ 3–5 ตัวแล้วจบ จึงพลาดทุกข้อนอกเหนือจากกรณีปกติ (ได้ 0.30–0.50) ให้ใช้ checklist 5 ข้อ: ค่าขอบ ปัดเศษ ValueError CLI และ test_solve.py ก่อนส่งงาน [iter 2 ดีขึ้นแล้ว เหลือแค่ต้องเทียบผลกับตัวเลขเกณฑ์ เช่น จำนวนเทสต์]

## wiki/skill-impact.md

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

## summary.md

# ผลของ Training rollouts · iteration 2

คะแนนเฉลี่ย 91.3% · ผ่านครบทุกข้อ 3/24 Trace

| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |
|---|---|---|---|
| t1-cafe-bill-r1 | PASS | 1.00 | - |
| t1-cafe-bill-r2 | FAIL | 0.90 | tests |
| t1-cafe-bill-r3 | PASS | 1.00 | - |
| t1-cafe-bill-r4 | FAIL | 0.90 | tests |
| t1-cafe-bill-r5 | FAIL | 0.90 | tests |
| t1-cafe-bill-r6 | FAIL | 0.90 | tests |
| t2-split-bill-r1 | FAIL | 0.90 | tests |
| t2-split-bill-r2 | FAIL | 0.90 | tests |
| t2-split-bill-r3 | FAIL | 0.90 | tests |
| t2-split-bill-r4 | FAIL | 0.90 | tests |
| t2-split-bill-r5 | FAIL | 0.90 | tests |
| t2-split-bill-r6 | FAIL | 0.90 | tests |
| t3-shipping-fee-r1 | FAIL | 0.90 | tests |
| t3-shipping-fee-r2 | FAIL | 0.90 | tests |
| t3-shipping-fee-r3 | FAIL | 0.90 | tests |
| t3-shipping-fee-r4 | FAIL | 0.90 | tests |
| t3-shipping-fee-r5 | FAIL | 0.90 | tests |
| t3-shipping-fee-r6 | FAIL | 0.90 | tests |
| t4-cashback-r1 | FAIL | 0.90 | tests |
| t4-cashback-r2 | FAIL | 0.90 | tests |
| t4-cashback-r3 | FAIL | 0.90 | tests |
| t4-cashback-r4 | FAIL | 0.90 | tests |
| t4-cashback-r5 | PASS | 1.00 | - |
| t4-cashback-r6 | FAIL | 0.90 | tests |

## รายละเอียดของข้อตรวจที่ไม่ผ่าน (คาดว่าอะไร · ได้อะไร)

- t1-cafe-bill-r2 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t1-cafe-bill-r4 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t1-cafe-bill-r5 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t1-cafe-bill-r6 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t2-split-bill-r1 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t2-split-bill-r2 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t2-split-bill-r3 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t2-split-bill-r4 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t2-split-bill-r5 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t2-split-bill-r6 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r1 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r2 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r3 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r4 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r5 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r6 · `tests`: unittest พบ 3 เทสต์ (ต้องมีอย่างน้อย 6)
- t4-cashback-r1 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t4-cashback-r2 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t4-cashback-r3 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t4-cashback-r4 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t4-cashback-r6 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

## Active skills

- skills/cafe_solve_checklist/SKILL.md

สำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย