# Iteration 2

Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): 93.3%

## wiki/index.md

# Wiki Index

- [input-validation-missing](wiki/patterns/input-validation-missing.md): ฟังก์ชันไม่ตรวจ input จึงคืนค่าแทน raise `ValueError` สำหรับค่านอกช่วง/ชนิดผิด (float, bool, qty=0, people=0, ค่าติดลบ) เพราะโจทย์ไม่สั่งตรง ๆ แก้โดยตรวจชนิด (`type(x) is int`) และช่วงที่ต้นฟังก์ชันก่อน early-return แล้ว raise `ValueError` เสมอ (`reject_value`, `reject_type`) [รอบ 2: แก้ได้แล้วด้วยสกิล]
- [cli-entrypoint-missing](wiki/patterns/cli-entrypoint-missing.md): solve.py ไม่มี `__main__` อ่าน JSON จาก stdin จึงได้ exit 0 stdout ว่าง (`cli_ok`, `cli_error`) เพราะโจทย์ไม่ได้พูดถึง CLI แก้โดยต่อท้ายไฟล์ด้วยโค้ดที่พิมพ์ `{"ok": true, "result": ...}` exit 0 หรือ `{"ok": false, "error": ...}` exit 2 ไม่มี traceback [รอบ 2: แก้ได้แล้วด้วยสกิล]
- [test-file-missing](wiki/patterns/test-file-missing.md): ไม่มี `test_solve.py` ข้าง solve.py (ข้อ `tests` ตก) เพราะ Agent ทดสอบด้วย `python3 -c` แล้วทิ้ง แก้โดยสร้างไฟล์ test ครอบคลุมปกติ ขอบ เศษ .5 และ `ValueError` แล้วรันให้ผ่านก่อนตอบ [รอบ 2: ไฟล์ถูกสร้างครบแล้ว ปัญหาที่เหลือดู test-count-below-minimum]
- [test-count-below-minimum](wiki/patterns/test-count-below-minimum.md): มี `test_solve.py` และผ่านหมด แต่ข้อ `tests` ตก "พบ 4/5 เทสต์ ต้องมีอย่างน้อย 6" เพราะตัวตรวจนับจำนวนเมธอด `def test_...` แต่สกิลไม่บอกเกณฑ์ Agent จึงรวม assertion ไว้ 4–5 เมธอด แก้โดยแยก 1 เมธอดต่อ 1 พฤติกรรม ให้ได้ 8 เมธอดขึ้นไป และเช็ก `Ran N tests` ว่า N >= 6 ก่อนตอบ (ข้อที่ตกข้อเดียวของรอบ 2)
- [half-up-integer-rounding](wiki/patterns/half-up-integer-rounding.md): ปัดเศษสตางค์ผิดวิธี (ปัดลงด้วย `//`) ทำให้ `half_up`/`no_drift` ตก เพราะโจทย์ไม่ระบุวิธีปัดแต่ตัวตรวจคาด half-up แก้โดยใช้เลขจำนวนเต็มหรือ Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย `(2*n+d)//(2*d)` (pattern ที่ทำให้สำเร็จอยู่ในหน้านี้) [รอบ 2: แก้ได้แล้วด้วยสกิล]
- [happy-path-only-verification](wiki/patterns/happy-path-only-verification.md): Agent ทดสอบแค่ตัวอย่างปกติรอบเดียวแล้วรายงานว่าเสร็จ (บางรายไม่รันเลย) ทำให้พลาดข้อ validation/CLI/tests/rounding ซ้ำทุก Trace แก้โดยทำรายการตรวจ 5 ข้อก่อนส่งงานและรันจริง [รอบ 2: แก้ได้แล้ว แต่ยังไม่ได้ตรวจจำนวนเทสต์]

## wiki/skill-impact.md

# Skill Impact

บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ

## Iteration 1 · create `cafe_function_checklist` · ACCEPTED

- Validation ของสกิลที่เสนอ: 93.3% · R_best ก่อนหน้า: 46.7% -> รับ (R_best ใหม่ 93.3%)
- เหตุผลของข้อเสนอ: ทุก Trace พลาด cli_ok/cli_error/tests/reject_type ซ้ำกัน และ t4 พลาด half_up/no_drift; ไม่มีสกิลอยู่เลย จึงสร้างสกิล checklist เดียวที่ครอบคลุมทุก pattern ใน wiki

Diff ของ SKILL.md ที่เสนอ:

```diff
--- a/skills/cafe_function_checklist/SKILL.md
+++ b/skills/cafe_function_checklist/SKILL.md
@@ -0,0 +1,76 @@
+---
+name: cafe_function_checklist
+description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
+---
+
+# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ
+
+## When to Apply
+- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
+- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบทั้ง 4 ข้อด้านล่างทุกครั้ง แม้โจทย์ไม่สั่ง
+
+## When NOT to Apply
+- งานที่ไม่ใช่ฟังก์ชันคำนวณใน `solve.py` (เช่น แก้เอกสาร จัดรูปแบบข้อความ)
+- ถ้าโจทย์ระบุวิธีปัด/รูปแบบ CLI/การ reject ไว้ชัดเจนและต่างจากนี้ ให้ทำตามโจทย์
+
+## Instructions
+
+### 1. ตรวจ input ที่ต้นฟังก์ชัน (ก่อนคำนวณ และก่อน early-return ทุกชนิด)
+ตัวตรวจคาดว่าค่าผิดต้อง `raise ValueError` เสมอ ไม่ใช่คืนค่า 0 และไม่ใช่ `ZeroDivisionError`/`TypeError`/`KeyError`
+- ตัวเลขทุกตัว: `type(x) is int` (ปฏิเสธ float เช่น `1000.0` และ `bool`)
+- flag (member/express/birthday ฯลฯ): `type(x) is bool`
+- ช่วงค่า: ตรวจทุกขอบเขตที่โจทย์ระบุ เช่น "ตั้งแต่ 0" -> `x >= 0`, "ตั้งแต่ 1" -> `x >= 1`, "1–30,000" -> `1 <= x <= 30000`, "0–100" -> `0 <= x <= 100`
+- enum (tier ฯลฯ): ต้องอยู่ในชุดที่โจทย์กำหนด
+- list ของ dict: ตรวจว่าเป็น `list`, แต่ละตัวเป็น `dict`, มี key ครบ, แต่ละฟิลด์ตรวจตามข้างบน
+- ค่า 0 ที่ผิดช่วง (qty=0, people=0, weight=0) และค่าติดลบ ต้อง raise
+
+```python
+def _int(name, v, lo=None, hi=None):
+    if type(v) is not int:
+        raise ValueError(f"{name} must be int")
+    if (lo is not None and v < lo) or (hi is not None and v > hi):
+        raise ValueError(f"{name} out of range")
+    return v
+```
+
+### 2. ปัดเศษ half-up ด้วยจำนวนเต็ม ครั้งเดียวตอนท้าย
+- ห้ามใช้ float กับเงิน ห้ามใช้ `round()` ห้ามใช้ `//` ปัดลง (ถ้าโจทย์ไม่ระบุวิธีปัด ให้ถือว่า half-up)
+- เก็บค่าเป็นเศษส่วน `n/d` (จำนวนเต็มบวก) แล้วปัดครั้งเดียว: `(2*n + d) // (2*d)`
+- ขั้นตอนหลายชั้น (ลด %, VAT, คูณ) ให้คูณเศษส่วนต่อกันแล้วปัดทีเดียว ไม่ปัดระหว่างทาง ยกเว้นโจทย์สั่งให้ปัดเป็นขั้น
+- เพดาน/ขั้นต่ำ ให้ดูโจทย์ว่าอยู่ก่อนหรือหลังปัด ถ้าเพดานเป็นจำนวนเต็มอยู่แล้ว ใช้ `min` กับค่าก่อนปัดหรือหลังปัดได้ผลเหมือนกัน
+- ผลลัพธ์ต้องเป็น `int` ไม่ใช่ float
+
+### 3. ต่อท้าย solve.py ด้วย CLI (ตัวตรวจรัน `python solve.py` ส่ง JSON ทาง stdin)
+key ใน JSON ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน แทน `FUNC` ด้วยชื่อฟังก์ชันของโจทย์
+
+```python
+import json, sys
+
+def _main():
+    try:
+        data = json.loads(sys.stdin.read())
+        result = FUNC(**data)
+    except (ValueError, TypeError, KeyError) as e:
+        print(json.dumps({"ok": False, "error": str(e)}))
+        return 2
+    print(json.dumps({"ok": True, "result": result}))
+    return 0
+
+if __name__ == "__main__":
+    sys.exit(_main())
+```
+- สำเร็จ: stdout `{"ok": true, "result": ...}` exit 0
+- input ผิด: stdout `{"ok": false, "error": "..."}` exit 2 และไม่มี traceback
+
+### 4. สร้าง test_solve.py ข้าง solve.py แล้วรันจริง
+- ใช้ `unittest` และ `from solve import FUNC`
+- ครอบคลุม: กรณีปกติ · ค่าขอบพอดี (เช่น พอดีเกณฑ์ขั้นต่ำ/ขั้นบันได) · เศษ .5 พอดีที่ต้องปัดขึ้น · `assertRaises(ValueError)` สำหรับ ค่านอกช่วง, 0, ติดลบ, float, bool, enum ผิด
+- รัน `python3 -m unittest -q` ต้องผ่านทั้งหมด ถ้าล้มให้แก้ solve.py ไม่ใช่แก้ test
+
+### 5. ตรวจก่อนตอบ (ต้องรันจริง)
+```
+echo '<JSON กรณีปกติ>' | python3 solve.py; echo "exit=$?"   # ต้อง exit=0 และมี "ok": true
+echo '<JSON กรณีผิด>'  | python3 solve.py; echo "exit=$?"   # ต้อง exit=2 และมี "ok": false ไม่มี Traceback
+python3 -m unittest -q
+```
+ห้ามรายงานว่าเสร็จถ้ายังไม่ได้รันทั้งสามคำสั่ง
```

## summary.md

# ผลของ Training rollouts · iteration 2

คะแนนเฉลี่ย 95.0% · ผ่านครบทุกข้อ 6/12 Trace

| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |
|---|---|---|---|
| t1-cafe-bill-r1 | PASS | 1.00 | - |
| t1-cafe-bill-r2 | FAIL | 0.90 | tests |
| t1-cafe-bill-r3 | FAIL | 0.90 | tests |
| t2-split-bill-r1 | PASS | 1.00 | - |
| t2-split-bill-r2 | PASS | 1.00 | - |
| t2-split-bill-r3 | PASS | 1.00 | - |
| t3-shipping-fee-r1 | FAIL | 0.90 | tests |
| t3-shipping-fee-r2 | FAIL | 0.90 | tests |
| t3-shipping-fee-r3 | FAIL | 0.90 | tests |
| t4-cashback-r1 | PASS | 1.00 | - |
| t4-cashback-r2 | FAIL | 0.90 | tests |
| t4-cashback-r3 | PASS | 1.00 | - |

## รายละเอียดของข้อตรวจที่ไม่ผ่าน (คาดว่าอะไร · ได้อะไร)

- t1-cafe-bill-r2 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t1-cafe-bill-r3 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r1 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r2 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r3 · `tests`: unittest พบ 3 เทสต์ (ต้องมีอย่างน้อย 6)
- t4-cashback-r2 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)

## Active skills

- skills/cafe_function_checklist/SKILL.md

สำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย