# Iteration 2

คะแนน Training ของรอบนี้: 95.0% (ผ่านครบ 6/12 Trace)

## Active skills (ชุดสกิลที่ Agent ใช้ในรอบนี้)

### skills/cafe_function_checklist/SKILL.md

---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบทั้ง 4 ข้อด้านล่างทุกครั้ง แม้โจทย์ไม่สั่ง

## When NOT to Apply
- งานที่ไม่ใช่ฟังก์ชันคำนวณใน `solve.py` (เช่น แก้เอกสาร จัดรูปแบบข้อความ)
- ถ้าโจทย์ระบุวิธีปัด/รูปแบบ CLI/การ reject ไว้ชัดเจนและต่างจากนี้ ให้ทำตามโจทย์

## Instructions

### 1. ตรวจ input ที่ต้นฟังก์ชัน (ก่อนคำนวณ และก่อน early-return ทุกชนิด)
ตัวตรวจคาดว่าค่าผิดต้อง `raise ValueError` เสมอ ไม่ใช่คืนค่า 0 และไม่ใช่ `ZeroDivisionError`/`TypeError`/`KeyError`
- ตัวเลขทุกตัว: `type(x) is int` (ปฏิเสธ float เช่น `1000.0` และ `bool`)
- flag (member/express/birthday ฯลฯ): `type(x) is bool`
- ช่วงค่า: ตรวจทุกขอบเขตที่โจทย์ระบุ เช่น "ตั้งแต่ 0" -> `x >= 0`, "ตั้งแต่ 1" -> `x >= 1`, "1–30,000" -> `1 <= x <= 30000`, "0–100" -> `0 <= x <= 100`
- enum (tier ฯลฯ): ต้องอยู่ในชุดที่โจทย์กำหนด
- list ของ dict: ตรวจว่าเป็น `list`, แต่ละตัวเป็น `dict`, มี key ครบ, แต่ละฟิลด์ตรวจตามข้างบน
- ค่า 0 ที่ผิดช่วง (qty=0, people=0, weight=0) และค่าติดลบ ต้อง raise

```python
def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v
```

### 2. ปัดเศษ half-up ด้วยจำนวนเต็ม ครั้งเดียวตอนท้าย
- ห้ามใช้ float กับเงิน ห้ามใช้ `round()` ห้ามใช้ `//` ปัดลง (ถ้าโจทย์ไม่ระบุวิธีปัด ให้ถือว่า half-up)
- เก็บค่าเป็นเศษส่วน `n/d` (จำนวนเต็มบวก) แล้วปัดครั้งเดียว: `(2*n + d) // (2*d)`
- ขั้นตอนหลายชั้น (ลด %, VAT, คูณ) ให้คูณเศษส่วนต่อกันแล้วปัดทีเดียว ไม่ปัดระหว่างทาง ยกเว้นโจทย์สั่งให้ปัดเป็นขั้น
- เพดาน/ขั้นต่ำ ให้ดูโจทย์ว่าอยู่ก่อนหรือหลังปัด ถ้าเพดานเป็นจำนวนเต็มอยู่แล้ว ใช้ `min` กับค่าก่อนปัดหรือหลังปัดได้ผลเหมือนกัน
- ผลลัพธ์ต้องเป็น `int` ไม่ใช่ float

### 3. ต่อท้าย solve.py ด้วย CLI (ตัวตรวจรัน `python solve.py` ส่ง JSON ทาง stdin)
key ใน JSON ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน แทน `FUNC` ด้วยชื่อฟังก์ชันของโจทย์

```python
import json, sys

def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = FUNC(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0

if __name__ == "__main__":
    sys.exit(_main())
```
- สำเร็จ: stdout `{"ok": true, "result": ...}` exit 0
- input ผิด: stdout `{"ok": false, "error": "..."}` exit 2 และไม่มี traceback

### 4. สร้าง test_solve.py ข้าง solve.py แล้วรันจริง
- ใช้ `unittest` และ `from solve import FUNC`
- ครอบคลุม: กรณีปกติ · ค่าขอบพอดี (เช่น พอดีเกณฑ์ขั้นต่ำ/ขั้นบันได) · เศษ .5 พอดีที่ต้องปัดขึ้น · `assertRaises(ValueError)` สำหรับ ค่านอกช่วง, 0, ติดลบ, float, bool, enum ผิด
- รัน `python3 -m unittest -q` ต้องผ่านทั้งหมด ถ้าล้มให้แก้ solve.py ไม่ใช่แก้ test

### 5. ตรวจก่อนตอบ (ต้องรันจริง)
```
echo '<JSON กรณีปกติ>' | python3 solve.py; echo "exit=$?"   # ต้อง exit=0 และมี "ok": true
echo '<JSON กรณีผิด>'  | python3 solve.py; echo "exit=$?"   # ต้อง exit=2 และมี "ok": false ไม่มี Traceback
python3 -m unittest -q
```
ห้ามรายงานว่าเสร็จถ้ายังไม่ได้รันทั้งสามคำสั่ง

## Current wiki

### wiki/index.md

# Wiki Index

- [input-validation-missing](wiki/patterns/input-validation-missing.md): ฟังก์ชันไม่ตรวจ input จึงคืนค่าแทน raise `ValueError` สำหรับค่านอกช่วง/ชนิดผิด (float, bool, qty=0, people=0, ค่าติดลบ) เพราะโจทย์ไม่สั่งตรง ๆ แก้โดยตรวจชนิด (`type(x) is int`) และช่วงที่ต้นฟังก์ชันก่อน early-return แล้ว raise `ValueError` เสมอ (`reject_value`, `reject_type`)
- [cli-entrypoint-missing](wiki/patterns/cli-entrypoint-missing.md): solve.py ไม่มี `__main__` อ่าน JSON จาก stdin จึงได้ exit 0 stdout ว่าง (`cli_ok`, `cli_error`) เพราะโจทย์ไม่ได้พูดถึง CLI แก้โดยต่อท้ายไฟล์ด้วยโค้ดที่พิมพ์ `{"ok": true, "result": ...}` exit 0 หรือ `{"ok": false, "error": ...}` exit 2 ไม่มี traceback
- [test-file-missing](wiki/patterns/test-file-missing.md): ไม่มี `test_solve.py` ข้าง solve.py (ข้อ `tests` ตก) เพราะ Agent ทดสอบด้วย `python3 -c` แล้วทิ้ง แก้โดยสร้างไฟล์ test ครอบคลุมปกติ ขอบ เศษ .5 และ `ValueError` แล้วรันให้ผ่านก่อนตอบ
- [half-up-integer-rounding](wiki/patterns/half-up-integer-rounding.md): ปัดเศษสตางค์ผิดวิธี (ปัดลงด้วย `//`) ทำให้ `half_up`/`no_drift` ตก เพราะโจทย์ไม่ระบุวิธีปัดแต่ตัวตรวจคาด half-up แก้โดยใช้เลขจำนวนเต็มหรือ Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย `(2*n+d)//(2*d)` (pattern ที่ทำให้สำเร็จอยู่ในหน้านี้)
- [happy-path-only-verification](wiki/patterns/happy-path-only-verification.md): Agent ทดสอบแค่ตัวอย่างปกติรอบเดียวแล้วรายงานว่าเสร็จ (บางรายไม่รันเลย) ทำให้พลาดข้อ validation/CLI/tests/rounding ซ้ำทุก Trace แก้โดยทำรายการตรวจ 5 ข้อก่อนส่งงานและรันจริง

### wiki/log.md

# Evolution Log

## Iteration 1 · Training 46.7%

- รอบนี้ไม่มีสกิล (`./skills` ไม่มี) และ skill-impact.md ยังว่าง จึงยังไม่มีผลรอบก่อนให้เทียบ
- ทุก Trace ผ่านเฉพาะ `contract` `basic` `boundary` (บางข้อ `half_up` `no_drift`) ส่วนที่ตกซ้ำทุก Trace คือ 4 เรื่องที่โจทย์ไม่ได้บอกแต่ตัวตรวจคาดหวัง: ตรวจ input แล้ว raise `ValueError`, CLI stdin/stdout JSON, ไฟล์ `test_solve.py`, ปัดเศษ half-up
- Trace ที่ผ่าน half_up/no_drift (t1, t2, t3) ใช้เลขจำนวนเต็มหรือ Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ส่วน t4 ทั้งสอง Trace ปัดลงด้วย `//` จึงตก
- t2 ไม่ได้รันทดสอบเลย และได้ ZeroDivisionError แทน ValueError
- สร้างหน้าใหม่ 5 หน้า: input-validation-missing, cli-entrypoint-missing, test-file-missing, half-up-integer-rounding, happy-path-only-verification และอัปเดต index

### wiki/skill-impact.md

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

### wiki/patterns/cli-entrypoint-missing.md

# cli-entrypoint-missing: solve.py ไม่มี CLI อ่าน stdin เป็น JSON

## อาการ
- `cli_ok` และ `cli_error` ตกใน 5 จาก 5 Trace
- ข้อความตัวตรวจ: "ได้ exit 0 stdout (ว่าง)" ทั้งกรณีปกติและกรณี input ผิด

## สาเหตุ
- ตัวตรวจรัน `python solve.py` โดยส่ง JSON ทาง stdin แต่โจทย์พูดถึงแค่ฟังก์ชัน ไม่ได้บอกว่าต้องมี CLI
- Agent เขียนแต่ฟังก์ชัน ไม่มี `if __name__ == "__main__"` สคริปต์จึงจบเงียบ ๆ ด้วย exit 0
- รูปแบบที่ตัวตรวจคาดหวังรู้ได้จากข้อความของตัวตรวจเท่านั้น ไม่ใช่จากโจทย์

## หลักฐาน
- iteration 1: ทุก Trace (t1-cafe-bill-r1, t2-split-bill-r1, t3-shipping-fee-r3, t4-cashback-r1, t4-cashback-r2)
- ตัวอย่างที่คาด: stdin `{"amount": 20000, "tier": "gold", "birthday": false}` ได้ stdout `{"ok": true, "result": 500}` exit 0
- กรณีผิด: stdin `{"amount": 20000, "tier": "bronze", ...}` ได้ `{"ok": false, "error": "..."}` exit 2 และไม่มี traceback

## วิธีแก้
ต่อท้าย solve.py ทุกครั้ง (key ใน JSON ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน):

```python
import json, sys

def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = FUNC(**data)  # แทน FUNC ด้วยชื่อฟังก์ชันของโจทย์
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0

if __name__ == "__main__":
    sys.exit(_main())
```

แล้วรันเองทั้งกรณีปกติและกรณีผิด: `echo '{...}' | python3 solve.py; echo $?` ตรวจว่า exit code เป็น 0 และ 2 ตามลำดับ และไม่มี traceback

### wiki/patterns/half-up-integer-rounding.md

# half-up-integer-rounding: ปัดเศษสตางค์ด้วยเลขจำนวนเต็ม ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย

## อาการ
- `half_up` และ `no_drift` ตกเมื่อ Agent ปัดลง เช่น `cashback(10020, "gold", false)` คาด 251 ได้ 250, `cashback(10020, "silver", true)` คาด 301 ได้ 300
- Trace ที่ปัดครึ่งขึ้นด้วยเลขจำนวนเต็มหรือ Fraction ผ่านทั้ง `half_up` `no_drift` `boundary`

## สาเหตุ
- โจทย์เขียนแค่ "เป็นจำนวนเต็มสตางค์" ไม่บอกวิธีปัด
- ตัวตรวจคาดหวังปัดครึ่งขึ้น (half-up) แต่ t4 เลือกปัดลงด้วย `//` และระบุในคำตอบว่า "โจทย์ไม่ได้ระบุ" จึงเลือกเอง
- ข้อสรุป: เมื่อโจทย์ไม่ระบุ ให้ใช้ half-up เสมอ

## หลักฐาน
- ล้ม: t4-cashback-r1 (`amount*rate*mult // 10_000`), t4-cashback-r2 (`// 1000`)
- ผ่าน: t1-cafe-bill-r1 (`(total*num*2 + den)//(den*2)`), t3-shipping-fee-r3 (`Fraction` แล้ว `floor(fee + Fraction(1,2))`), t2-split-bill-r1 (ปัดทิป half-up ด้วยเลขจำนวนเต็ม)

## วิธีแก้
1. ห้ามใช้ float กับเงิน คำนวณเป็นเศษส่วนหรือจำนวนเต็มล้วน
2. ปัดเพียงครั้งเดียวที่ขั้นสุดท้าย ไม่ปัดระหว่างขั้นตอน
3. สูตร half-up สำหรับค่า `n/d` (n, d เป็นจำนวนเต็มบวก): `(2*n + d) // (2*d)`
   - เช่น cashback: `n = amount * rate_num * mult`, `d = rate_den` ได้ `(2*n + d)//(2*d)`
4. ใช้ `//` ธรรมดาเฉพาะเมื่อโจทย์สั่งปัดลงอย่างชัดเจน
5. ทดสอบเศษที่พอดี .5 อย่างน้อย 1 กรณีใน test_solve.py
6. ลำดับ: ตรวจ input -> คำนวณ -> ใช้เพดาน/เงื่อนไขตามโจทย์ -> ปัดครั้งเดียว (ดูโจทย์ว่าเพดานอยู่ก่อนหรือหลังปัด)

### wiki/patterns/happy-path-only-verification.md

# happy-path-only-verification: ทดสอบแค่ตัวอย่างปกติแล้วรายงานว่า "ผลตามที่คาด"

## อาการ
- ทุก Trace ตกข้อเดิมซ้ำ ๆ (validation · CLI · tests · rounding) ทั้งที่ Agent รายงานว่าเสร็จ
- คะแนนที่ได้มาจาก `contract` `basic` `boundary` เท่านั้น (3–5 จาก 10)
- รอบนี้ไม่มี Trace ผ่านเลย (0/12)

## สาเหตุ
- Agent รัน `python3 -c` 1 ครั้งกับ 4–5 ตัวอย่างที่ตนเลือกเอง ซึ่งเป็นแต่กรณีปกติ จึงมั่นใจเกินจริง
- ไม่มีรายการตรวจก่อนส่งงาน จึงไม่เคยลองกรณี input ผิด, CLI, หรือเศษ .5
- Agent ปล่อยข้อสันนิษฐานไว้ในคำตอบ ("ถ้าต้องการปัดแบบอื่นบอกได้") แทนที่จะเลือกค่าปลอดภัยเอง
- ไม่มีสกิลในรอบนี้ (`./skills` ไม่มี) จึงไม่มีรายการตรวจให้ทำตาม

## หลักฐาน
- iteration 1: t2-split-bill-r1 เขียนไฟล์แล้วจบโดยไม่รันอะไร ("ยังไม่ได้รันทดสอบ") · ที่เหลือรันเพียง 1 คำสั่งทดสอบ
- ทุก Trace จบภายใน 2 คำสั่ง

## วิธีแก้
ก่อนตอบ ให้ทำรายการตรวจนี้ครบและรันจริง:
1. ฟังก์ชันตรงตามโจทย์ (ตัวอย่างปกติ + ค่าขอบ)
2. ปัดครึ่งขึ้นด้วยเลขจำนวนเต็ม (ดู half-up-integer-rounding)
3. input ผิดช่วง/ผิดชนิดต้อง raise `ValueError` (ดู input-validation-missing)
4. มี CLI ที่ตอบ `{"ok":...}` exit 0/2 (ดู cli-entrypoint-missing)
5. มี `test_solve.py` ที่รันผ่าน (ดู test-file-missing)

ถ้าโจทย์ไม่ระบุ ให้เลือกค่าตามรายการนี้ แล้วค่อยบันทึกข้อสันนิษฐานสั้น ๆ

### wiki/patterns/input-validation-missing.md

# input-validation-missing: ไม่ตรวจ input ทำให้ไม่ raise ValueError

## อาการ
- ข้อตรวจ `reject_value` และ `reject_type` ตกเกือบทุกกรณีในทุก Trace (5 จาก 5 Trace)
- ค่าที่ผิดช่วงถูกคำนวณต่อจนได้ตัวเลข เช่น `cafe_bill` qty=0 คืน 0, `shipping_fee(0,...)` คืน 4000, `cashback(-1,...)` คืน 0
- ค่าที่ชนิดผิดผ่านไปได้ เช่น 20000.0 ได้ 500.0 กลับมาเป็น float
- หารด้วยศูนย์ ทำให้เกิด `ZeroDivisionError` แทน `ValueError` (`split_bill` people=0)

## สาเหตุ
- โจทย์บอกแค่ช่วงค่าที่ถูกต้อง (เช่น "น้ำหนัก 1–30,000", "จำนวนคนตั้งแต่ 1") แต่ไม่ได้สั่งให้ reject ตัวตรวจจึงคาดหวังเองว่าค่านอกช่วงต้อง raise `ValueError`
- Agent ทำเฉพาะ happy path และตรวจแค่ tier ที่ไม่รู้จัก (t4) ไม่ตรวจ amount ที่ติดลบหรือชนิดข้อมูล
- ใน t4 การ early-return `amount < MIN_AMOUNT -> 0` มาก่อนการตรวจช่วงค่า จึงกลืนค่า -1

## หลักฐาน
- iteration 1: t1-cafe-bill-r1 (qty=0 คืน 0, price 4500.0 คืน 4815.0), t2-split-bill-r1 (people=0 ได้ ZeroDivisionError), t3-shipping-fee-r3 (weight 0 คืน 4000, 1000.0 คืน 4000), t4-cashback-r1 และ r2 (-1 คืน 0, 20000.0 คืน 500.0)
- ข้อความตัวตรวจ: "ต้อง raise ValueError แต่คืนค่า ..."

## วิธีแก้
1. ตรวจ input ที่ต้นฟังก์ชัน ก่อนคำนวณและก่อน early-return ใด ๆ
2. ชนิด: ใช้ `type(x) is int` สำหรับค่าจำนวนเต็ม (ปฏิเสธ float และ bool ซึ่งเป็น subclass ของ int) ใช้ `type(x) is bool` กับ flag เช่น `member` `express` `birthday`
3. ช่วงค่า: ตรวจตามที่โจทย์ระบุทุกตัว (เช่น weight 1–30000, tip 0–100, people >= 1, amount >= 0, qty >= 1)
4. ค่าเลือก (enum) เช่น tier ต้องอยู่ในชุดที่กำหนด
5. โครงสร้าง: ถ้ารับ list ของ dict ต้องตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ แล้วตรวจแต่ละฟิลด์เหมือนข้อ 2–3
6. ทุกกรณีผิดต้อง `raise ValueError("...")` ไม่ปล่อยให้เป็น `TypeError` `ZeroDivisionError` หรือ `KeyError`

### wiki/patterns/test-file-missing.md

# test-file-missing: ไม่มี test_solve.py ข้าง solve.py

## อาการ
- ข้อตรวจ `tests` ตกใน 5 จาก 5 Trace: "ไม่มีไฟล์ test_solve.py ข้าง solve.py"

## สาเหตุ
- โจทย์ไม่ได้สั่งให้เขียน test แต่ตัวตรวจเช็คว่ามีไฟล์
- Agent ทดสอบด้วย `python3 -c "print(...)"` ครั้งเดียวแล้วทิ้ง ไม่เก็บเป็นไฟล์

## หลักฐาน
- iteration 1: ทุก Trace ไม่มีการสร้างไฟล์อื่นนอกจาก solve.py
- t2-split-bill-r1 ไม่ได้รันทดสอบใดเลย (เขียนไฟล์แล้วจบ)

## วิธีแก้
1. สร้าง `test_solve.py` ในโฟลเดอร์เดียวกับ solve.py (ใช้ `unittest` หรือ `pytest` แบบ `from solve import FUNC`)
2. ครอบคลุมอย่างน้อย: กรณีปกติ · ค่าขอบ (เช่น พอดี 100 บาท, พอดี 1,000 กรัม) · เศษที่ต้องปัดครึ่งขึ้น · input ผิดช่วงและผิดชนิดต้อง `assertRaises(ValueError)`
3. รันจริง (`python3 -m unittest -q` หรือ `pytest -q`) และดูว่าผ่านก่อนตอบ
4. ถ้า test ล้ม ให้แก้ solve.py ไม่ใช่แก้ test ให้ผ่านตามผลเดิม


## Execution traces (sampled: 5 failing + 3 passing)

<trace id="t3-shipping-fee-r1">
# Trace t3-shipping-fee-r1 · iteration 2

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
ls ./skills 2>&1 | head; ls
```

ผลที่ได้:

```
cafe_function_checklist
skills
```

### ขั้น 2 · Bash

```
find skills -type f | head; cat skills/*/* 2>/dev/null | head -100
```

ผลที่ได้:

```
skills/cafe_function_checklist/PURPOSE.md
skills/cafe_function_checklist/SKILL.md
# PURPOSE: cafe_function_checklist

## Origin
สร้างจาก iteration 1 (ยังไม่มีสกิลมาก่อน) ทั้ง 12 Trace (t1–t4) ได้ 0.30–0.60 เพราะ Agent เขียนเฉพาะ happy path ไม่รู้ข้อที่ตัวตรวจคาดแต่โจทย์ไม่ได้เขียน ได้แก่ ValueError, CLI stdin, test_solve.py และ half-up

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-entrypoint-missing.md (cli_ok, cli_error)
- wiki/patterns/test-file-missing.md (tests)
- wiki/patterns/half-up-integer-rounding.md (half_up, no_drift)
- wiki/patterns/happy-path-only-verification.md (ขั้น 5 ตรวจก่อนตอบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวม checklist 4 ข้อ + คำสั่งตรวจก่อนตอบ
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได
…(ตัด 3060 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def shipping_fee(weight_g, distance_km, express):
    _int("weight_g", weight_g, 1, 30000)
    _int("distance_km", distance_km, 0)
    if type(express) is not bool:
        raise ValueError("express must be bool")

    # ค่าฐานเป็นสตางค์ x1000 (ตัวส่วน 1000)
    if weight_g <= 1000:
        n = 4000 * 1000
    elif weight_g <= 5000:
        n = 8000 * 1000
    else:
        n = 8000 * 1000 + (weight_g - 5000) * 1500  # 15 บาท/กก. = 1.5 สตางค์/กรัม
    d = 1000
    if distance_km > 100:
        n, d = n * 6, d * 5
    if express:
        n, d = n * 3, d * 2
    return (2 * n + d) // (2 * d)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import shipping_fee


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)

    def test_fraction_and_half_up(self):
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 8001.5 -> 8002
        self.assertEqual(shipping_fee(5003, 0, False), 8005)  # 8004.5 -> 8005

    def test_distance_express(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (-1, 0, False), (100, -1, False),
                  (100.0, 0, False), (100, 1.5, False), (True, 0, False),
                  (100, 0, 1), (100, 0, None), ("5", 0, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"weight_g":6000,"distance_km":150,"express":true}' | python3 solve.py; echo "exit=$?"
echo '{"weight_g":0,"distance_km":1,"express":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": 17100}
exit=0
{"ok": false, "error": "weight_g out of range"}
exit=2
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

**Agent พูด:** เขียน `shipping_fee(weight_g, distance_km, express)` เสร็จแล้วใน `solve.py` ตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` รัน 3 คำสั่งตรวจตามสกิลแล้วผ่านทั้งหมด

- **ผลที่ตรวจ:** กรณี 6,000 กรัม, 150 กม., ส่งด่วน ได้ 17,100 สตางค์ (exit 0) ส่วนกรณีผิด (น้ำหนัก 0) ได้ `{"ok": false}` (exit 2) และ `python3 -m unittest -q` ผ่าน 4 เทสต์
- **การคำนวณ:** ใช้จำนวนเต็มล้วน คูณ +20% และ +50% ต่อกันแล้วปัดแบบ half-up ครั้งเดียวตอนท้าย เช่น 5,001 กรัม ได้ 8,002 สตางค์
- **การตรวจ input:** ค่าผิดจะ `raise ValueError` คือ น้ำหนักนอก 1–30,000, ระยะทางติดลบ, float, bool ที่ส่งมาแทนตัวเลข, หรือ `express` ที่ไม่ใช่ bool
- **เพิ่มตามสกิล:** ต่อท้าย `solve.py` ด้วย CLI ที่อ่าน JSON จาก stdin และสร้าง `test_solve.py` ไว้ข้างกัน

ระยะทางต้องเป็นจำนวนเต็มกิโลเมตร ถ้าส่งทศนิยมเช่น 100.5 จะถูกปฏิเสธ เพรา
…(ตัด 167 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `shipping_fee(weight_g, distance_km, express)` เสร็จแล้วใน `solve.py` ตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` รัน 3 คำสั่งตรวจตามสกิลแล้วผ่านทั้งหมด

- **ผลที่ตรวจ:** กรณี 6,000 กรัม, 150 กม., ส่งด่วน ได้ 17,100 สตางค์ (exit 0) ส่วนกรณีผิด (น้ำหนัก 0) ได้ `{"ok": false}` (exit 2) และ `python3 -m unittest -q` ผ่าน 4 เทสต์
- **การคำนวณ:** ใช้จำนวนเต็มล้วน คูณ +20% และ +50% ต่อกันแล้วปัดแบบ half-up ครั้งเดียวตอนท้าย เช่น 5,001 กรัม ได้ 8,002 สตางค์
- **การตรวจ input:** ค่าผิดจะ `raise ValueError` คือ น้ำหนักนอก 1–30,000, ระยะทางติดลบ, float, bool ที่ส่งมาแทนตัวเลข, หรือ `express` ที่ไม่ใช่ bool
- **เพิ่มตามสกิล:** ต่อท้าย `solve.py` ด้วย CLI ที่อ่าน JSON จาก stdin และสร้าง `test_solve.py` ไว้ข้างกัน

ระยะทางต้องเป็นจำนวนเต็มกิโลเมตร ถ้าส่งทศนิยมเช่น 100.5 จะถูกปฏิเสธ เพราะสกิลกำหนดให้ปฏิเสธ float โจทย์ไม่ได้ระบุเรื่องนี้ ถ้าต้องการรับทศนิยม ต้องแก้การตรวจ `distance_km`

ไฟล์ที่สร้างอยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`

</trace>

<trace id="t4-cashback-r2">
# Trace t4-cashback-r2 · iteration 2

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
ls ./skills 2>&1; ls
```

ผลที่ได้:

```
cafe_function_checklist
skills
```

### ขั้น 2 · Bash

```
find ./skills -type f | head; cat ./skills/*/* 2>/dev/null | head -100
```

ผลที่ได้:

```
./skills/cafe_function_checklist/PURPOSE.md
./skills/cafe_function_checklist/SKILL.md
# PURPOSE: cafe_function_checklist

## Origin
สร้างจาก iteration 1 (ยังไม่มีสกิลมาก่อน) ทั้ง 12 Trace (t1–t4) ได้ 0.30–0.60 เพราะ Agent เขียนเฉพาะ happy path ไม่รู้ข้อที่ตัวตรวจคาดแต่โจทย์ไม่ได้เขียน ได้แก่ ValueError, CLI stdin, test_solve.py และ half-up

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-entrypoint-missing.md (cli_ok, cli_error)
- wiki/patterns/test-file-missing.md (tests)
- wiki/patterns/half-up-integer-rounding.md (half_up, no_drift)
- wiki/patterns/happy-path-only-verification.md (ขั้น 5 ตรวจก่อนตอบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวม checklist 4 ข้อ + คำสั่งตรวจก่อนตอบ
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไ
…(ตัด 3064 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys

_RATES = {"silver": 15, "gold": 25, "platinum": 40}  # per 1000
_MIN_AMOUNT = 10000   # 100 baht in satang
_CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < _MIN_AMOUNT:
        return 0
    n = amount * _RATES[tier] * (2 if birthday else 1)
    d = 1000
    return min((2 * n + d) // (2 * d), _CAP)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10030, "silver", False), 150)  # 150.45
        self.assertEqual(cashback(10040, "silver", False), 151)  # 150.6
        self.assertEqual(cashback(10100, "gold", False), 253)    # 252.5

    def test_cap(self):
        self.assertEqual(cashback(10**7, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_invalid(self):
        for a in (-1, 1000.0, True, "5", None):
            with self.assertRaises(ValueError):
                cashback(a, "gold", False)
        for t in ("bronze", "", None, 1):
            with self.assertRaises(ValueError):
                cashback(10000, t, False)
        for b in (1, 0, None, "True"):
            with self.assertRaises(ValueError):
                cashback(10000, "gold", b)
        with self.assertRaises(ValueError):
            cashback(-5, "bad", 1)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"amount":100000,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
echo '{"amount":1000.0,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": 5000}
exit=0
{"ok": false, "error": "amount must be int >= 0"}
exit=2
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
```

**Agent พูด:** สร้าง `solve.py` และ `test_solve.py` เสร็จแล้ว ทำตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` ด้วย รัน unittest ผ่านทั้ง 5 เทสต์ และรัน CLI ทดสอบแล้วทั้งกรณีปกติและกรณีผิด

**วิธีคิดเงินคืนใน `cashback(amount, tier, birthday)`**
- **ยอดขั้นต่ำ:** ถ้ายอดซื้อต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
- **อัตรา:** คำนวณด้วยจำนวนเต็มล้วน ไม่ใช้ float โดย silver คิดเป็น 15/1000, gold 25/1000, platinum 40/1000
- **เดือนเกิด:** คูณ 2 ก่อนปัด
- **การปัด:** ปัดแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`
- **เพดาน:** สูงสุด 20,000 สตางค์ (200 บาท) ต่อบิล
- **ตรวจ input:** ถ้า input ผิดจะ raise `ValueError` ได้แก่
  - `amount` ไม่ใช่ `int` (รวม float และ bool) หรือติดลบ
  - `tier` ไม่อยู่ใน silver, gold, platinum
  - `birthday` ไม่ใช่ `bool`

**CLI:** `python solve.py` รับ JSON ทาง stdin
- ส
…(ตัด 302 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

สร้าง `solve.py` และ `test_solve.py` เสร็จแล้ว ทำตามสกิล `cafe_function_checklist` ที่อยู่ใน `./skills` ด้วย รัน unittest ผ่านทั้ง 5 เทสต์ และรัน CLI ทดสอบแล้วทั้งกรณีปกติและกรณีผิด

**วิธีคิดเงินคืนใน `cashback(amount, tier, birthday)`**
- **ยอดขั้นต่ำ:** ถ้ายอดซื้อต่ำกว่า 10,000 สตางค์ (100 บาท) คืน 0
- **อัตรา:** คำนวณด้วยจำนวนเต็มล้วน ไม่ใช้ float โดย silver คิดเป็น 15/1000, gold 25/1000, platinum 40/1000
- **เดือนเกิด:** คูณ 2 ก่อนปัด
- **การปัด:** ปัดแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`
- **เพดาน:** สูงสุด 20,000 สตางค์ (200 บาท) ต่อบิล
- **ตรวจ input:** ถ้า input ผิดจะ raise `ValueError` ได้แก่
  - `amount` ไม่ใช่ `int` (รวม float และ bool) หรือติดลบ
  - `tier` ไม่อยู่ใน silver, gold, platinum
  - `birthday` ไม่ใช่ `bool`

**CLI:** `python solve.py` รับ JSON ทาง stdin
- สำเร็จ: ได้ `{"ok": true, "result": ...}` และ exit 0 เช่น gold, 100000 สตางค์, เดือนเกิด ได้ 5000
- input ผิด: ได้ `{"ok": false, "error": ...}` และ exit 2 โดยไม่มี traceback

**เทสต์:** `test_solve.py` ครอบคลุมกรณีปกติ ขอบ 9,999 กับ 10,000 สตางค์ เศษ .5 ที่ปัดขึ้น เพดาน 200 บาท และ input ที่ไม่ถูกต้อง

</trace>

<trace id="t1-cafe-bill-r3">
# Trace t1-cafe-bill-r3 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 4 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
cafe_function_checklist

./skills/cafe_function_checklist:
PURPOSE.md
SKILL.md
```

### ขั้น 2 · Bash

```
cat ./skills/cafe_function_checklist/*.md
```

ผลที่ได้:

```
# PURPOSE: cafe_function_checklist

## Origin
สร้างจาก iteration 1 (ยังไม่มีสกิลมาก่อน) ทั้ง 12 Trace (t1–t4) ได้ 0.30–0.60 เพราะ Agent เขียนเฉพาะ happy path ไม่รู้ข้อที่ตัวตรวจคาดแต่โจทย์ไม่ได้เขียน ได้แก่ ValueError, CLI stdin, test_solve.py และ half-up

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-entrypoint-missing.md (cli_ok, cli_error)
- wiki/patterns/test-file-missing.md (tests)
- wiki/patterns/half-up-integer-rounding.md (half_up, no_drift)
- wiki/patterns/happy-path-only-verification.md (ขั้น 5 ตรวจก่อนตอบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวม checklist 4 ข้อ + คำสั่งตรวจก่อนตอบ
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบทั้ง 4 ข้อด้านล่างทุกครั้ง แม้โจทย์ไม่สั่ง

## When NOT to 
…(ตัด 2978 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("item must be dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item missing key")
        price = _int("price", it["price"], 0)
        qty = _int("qty", it["qty"], 1)
        total += price * qty

    n, d = total, 1
    if total >= 50000:  # 500 baht
        n *= 95
        d *= 100
    if member:
        n *= 90
        d *= 100
    n *= 107
    d *= 100
    return (2 * n + d) // (2 * d)  # half-up, rounded once


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_exact(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45742)

    def test_half_up(self):
        # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": True}], False),
            ([{"price": 100}], False),
            ([1], False),
            ({}, False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": 100, "qty": 1}], None),
        ]
        for a in bad:
            with self.assertRaises(ValueError):
                cafe_bill(*a)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"items":[{"price":30000,"qty":2}],"member":true}' | python3 solve.py; echo "exit=$?"
echo '{"items":[{"price":300,"qty":0}],"member":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
ERROR Exit code 1
{"ok": true, "result": 54891}
exit=0
{"ok": false, "error": "qty out of range"}
exit=2
======================================================================
FAIL: test_member (test_solve.T.test_member)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/wklab/suite/runs/v1-k02-train/t1-cafe-bill-r3/sandbox/test_solve.py", line 15, in test_member
    self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45742)
AssertionError: 45743 != 45742

----------------------------------------------------------------------
Ran 5 tests in 0.000s

FAILED (failures=1)
```

### ขั้น 4 · Bash

```
sed -i 's/45742)/45743)/' test_solve.py && python3 -m unittest -q
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cafe_bill(items, member)` เสร็จแล้วใน `solve.py` พร้อม `test_solve.py` และรันทดสอบผ่านทั้ง 5 เทสต์

ผมอ่านและทำตามสกิล `cafe_function_checklist` ก่อนเริ่ม ตามที่โจทย์สั่ง

**วิธีคิดเงิน**
- ยอดรวมคือผลรวมของ `price*qty` หน่วยสตางค์
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% โดยคิดต่อจากยอดที่ลด 5% แล้ว (ตีความ "ลดอีก" เป็นการลดซ้อน ไม่ใช่รวมเป็น 15%)
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้จำนวนเต็มล้วนและปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`

**ตรวจ input**
- `items` ต้องเป็น list ของ dict ที่มี key `price` และ `qty` ครบ ส่วน `member` ต้องเป็น `bool`
- `price` ต้องเป็น int และ `>= 0` ส่วน `qty` ต้องเป็น int และ `>= 1`
- float และ bool ถูกปฏิเสธ ค่าผิดทุกกรณี raise `ValueError`
- โจทย์ไม่ได้ระบุว่า `items` ว่างได้หรือไม่ โค้ด
…(ตัด 529 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` เสร็จแล้วใน `solve.py` พร้อม `test_solve.py` และรันทดสอบผ่านทั้ง 5 เทสต์

ผมอ่านและทำตามสกิล `cafe_function_checklist` ก่อนเริ่ม ตามที่โจทย์สั่ง

**วิธีคิดเงิน**
- ยอดรวมคือผลรวมของ `price*qty` หน่วยสตางค์
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% โดยคิดต่อจากยอดที่ลด 5% แล้ว (ตีความ "ลดอีก" เป็นการลดซ้อน ไม่ใช่รวมเป็น 15%)
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้จำนวนเต็มล้วนและปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int`

**ตรวจ input**
- `items` ต้องเป็น list ของ dict ที่มี key `price` และ `qty` ครบ ส่วน `member` ต้องเป็น `bool`
- `price` ต้องเป็น int และ `>= 0` ส่วน `qty` ต้องเป็น int และ `>= 1`
- float และ bool ถูกปฏิเสธ ค่าผิดทุกกรณี raise `ValueError`
- โจทย์ไม่ได้ระบุว่า `items` ว่างได้หรือไม่ โค้ดจึงยอมรับ list ว่างและคืน 0

**CLI**
- `python solve.py` อ่าน JSON จาก stdin แล้วพิมพ์ `{"ok": true, "result": ...}` พร้อม exit 0
- ถ้า input ผิดจะพิมพ์ `{"ok": false, "error": ...}` พร้อม exit 2 และไม่มี traceback

**ผลที่รันจริง**
- ตัวอย่างปกติ (สินค้า 300 บาท 2 ชิ้น เป็นสมาชิก) ได้ 54891 สตางค์ และ exit=0
- ตัวอย่างผิด (`qty` เป็น 0) ได้ `"ok": false` และ exit=2
- เทสต์ครั้งแรกล้ม 1 ข้อ เพราะผมคาดค่าผิดเอง กรณี 50,000 สตางค์ เป็นสมาชิก ได้ 45742.5 ซึ่งปัดขึ้นเป็น 45743 ฟังก์ชันถูกต้อง ผมจึงแก้ค่าที่คาดในเทสต์แล้วรันผ่าน

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
ls ./skills 2>&1; ls
```

ผลที่ได้:

```
cafe_function_checklist
skills
```

### ขั้น 2 · Bash

```
find skills -type f | head; cat skills/*/* 2>/dev/null | head -100
```

ผลที่ได้:

```
skills/cafe_function_checklist/PURPOSE.md
skills/cafe_function_checklist/SKILL.md
# PURPOSE: cafe_function_checklist

## Origin
สร้างจาก iteration 1 (ยังไม่มีสกิลมาก่อน) ทั้ง 12 Trace (t1–t4) ได้ 0.30–0.60 เพราะ Agent เขียนเฉพาะ happy path ไม่รู้ข้อที่ตัวตรวจคาดแต่โจทย์ไม่ได้เขียน ได้แก่ ValueError, CLI stdin, test_solve.py และ half-up

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-entrypoint-missing.md (cli_ok, cli_error)
- wiki/patterns/test-file-missing.md (tests)
- wiki/patterns/half-up-integer-rounding.md (half_up, no_drift)
- wiki/patterns/happy-path-only-verification.md (ขั้น 5 ตรวจก่อนตอบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวม checklist 4 ข้อ + คำสั่งตรวจก่อนตอบ
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได
…(ตัด 3060 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def shipping_fee(weight_g, distance_km, express):
    _int("weight_g", weight_g, 1, 30000)
    _int("distance_km", distance_km, 0)
    if type(express) is not bool:
        raise ValueError("express must be bool")
    # fee in satang as fraction n/d
    if weight_g <= 1000:
        n, d = 4000, 1
    elif weight_g <= 5000:
        n, d = 8000, 1
    else:
        # 15 baht/kg = 1.5 satang/g
        n, d = 16000 + 3 * (weight_g - 5000), 2
    if distance_km > 100:
        n, d = n * 6, d * 5
    if express:
        n, d = n * 3, d * 2
    return (2 * n + d) // (2 * d)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = shipping_fee(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(6000, 0, False), 9500)
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_modifiers(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 101, True), 7200)
        self.assertEqual(f(500, 0, True), 6000)

    def test_half_up(self):
        # 5001 g: 8001.5 satang -> 8002
        self.assertEqual(f(5001, 0, False), 8002)
        # 5001 g express: 12002.25 -> 12002
        self.assertEqual(f(5001, 0, True), 12002)
        # 5003 g: 8004.5 -> 8005
        self.assertEqual(f(5003, 0, False), 8005)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (-1, 0, False), (100, -1, False),
                  (100.0, 0, False), (True, 0, False), (100, 0.0, False),
                  (100, 0, 1), (100, 0, None), ("5", 0, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -m unittest -q 2>&1 | tail -3
echo '{"weight_g":6000,"distance_km":150,"express":true}' | python3 solve.py; echo "exit=$?"
echo '{"weight_g":0,"distance_km":1,"express":true}' | python3 solve.py; echo "exit=$?"
```

ผลที่ได้:

```
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 17100}
exit=0
{"ok": false, "error": "weight_g out of range"}
exit=2
```

**Agent พูด:** ผมเขียน `shipping_fee` ใน `solve.py` เสร็จแล้ว และเขียน `test_solve.py` ไว้คู่กัน ผมทำตามสกิล `cafe_function_checklist` ใน `./skills` ตอนเขียน

ผมรันตรวจแล้ว unittest ผ่านทั้ง 4 ชุด ส่วน CLI ที่รับ JSON ทาง stdin ให้ผลถูกทั้งกรณีปกติและกรณีผิด:
- `{"weight_g":6000,"distance_km":150,"express":true}` ได้ผล `17100` สตางค์ (171 บาท) และ exit 0
- `{"weight_g":0,"distance_km":1,"express":true}` ได้ `{"ok": false, ...}` และ exit 2

การคำนวณและการตรวจ input:
- ค่าส่งคำนวณเป็นสตางค์ด้วยจำนวนเต็มล้วน แล้วปัดครั้งเดียวตอนท้ายแบบ half-up เช่น น้ำหนัก 5003 กรัมคิดได้ 8004.5 สตางค์ จึงปัดเป็น 8005
- ระยะทางเกิน 100 กม. คูณ 6/5 และส่งด่วนคูณ 3/2 ต่อจากนั้น
- ถ้า `weight_g` ไม่อยู่ในช่วง 1–30,000 หรือ `distance_km` ติดลบ จะ raise `ValueError`
- ถ้า `weight_g` หรือ `distance_km` เป็น float หรือ bool หรือ `
…(ตัด 190 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

ผมเขียน `shipping_fee` ใน `solve.py` เสร็จแล้ว และเขียน `test_solve.py` ไว้คู่กัน ผมทำตามสกิล `cafe_function_checklist` ใน `./skills` ตอนเขียน

ผมรันตรวจแล้ว unittest ผ่านทั้ง 4 ชุด ส่วน CLI ที่รับ JSON ทาง stdin ให้ผลถูกทั้งกรณีปกติและกรณีผิด:
- `{"weight_g":6000,"distance_km":150,"express":true}` ได้ผล `17100` สตางค์ (171 บาท) และ exit 0
- `{"weight_g":0,"distance_km":1,"express":true}` ได้ `{"ok": false, ...}` และ exit 2

การคำนวณและการตรวจ input:
- ค่าส่งคำนวณเป็นสตางค์ด้วยจำนวนเต็มล้วน แล้วปัดครั้งเดียวตอนท้ายแบบ half-up เช่น น้ำหนัก 5003 กรัมคิดได้ 8004.5 สตางค์ จึงปัดเป็น 8005
- ระยะทางเกิน 100 กม. คูณ 6/5 และส่งด่วนคูณ 3/2 ต่อจากนั้น
- ถ้า `weight_g` ไม่อยู่ในช่วง 1–30,000 หรือ `distance_km` ติดลบ จะ raise `ValueError`
- ถ้า `weight_g` หรือ `distance_km` เป็น float หรือ bool หรือ `express` ไม่ใช่ bool ก็ raise `ValueError` เช่นกัน

ข้อควรรู้: `distance_km` ต้องเป็นจำนวนเต็มเท่านั้น เพราะสกิลสั่งให้ปฏิเสธ float ถ้าต้องการให้รับระยะทางทศนิยม เช่น 100.5 กม. ต้องแก้ตรงนี้

</trace>

<trace id="t1-cafe-bill-r2">
# Trace t1-cafe-bill-r2 · iteration 2

- ผล: **FAIL** · คะแนน 0.90 (ผ่าน 9 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 4 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
- ✗ `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && head -50 ./skills/* 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
cafe_function_checklist
```

### ขั้น 2 · Bash

```
ls -R ./skills; cat ./skills/cafe_function_checklist/* 2>/dev/null
```

ผลที่ได้:

```
./skills:
cafe_function_checklist

./skills/cafe_function_checklist:
PURPOSE.md
SKILL.md
# PURPOSE: cafe_function_checklist

## Origin
สร้างจาก iteration 1 (ยังไม่มีสกิลมาก่อน) ทั้ง 12 Trace (t1–t4) ได้ 0.30–0.60 เพราะ Agent เขียนเฉพาะ happy path ไม่รู้ข้อที่ตัวตรวจคาดแต่โจทย์ไม่ได้เขียน ได้แก่ ValueError, CLI stdin, test_solve.py และ half-up

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-entrypoint-missing.md (cli_ok, cli_error)
- wiki/patterns/test-file-missing.md (tests)
- wiki/patterns/half-up-integer-rounding.md (half_up, no_drift)
- wiki/patterns/happy-path-only-verification.md (ขั้น 5 ตรวจก่อนตอบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวม checklist 4 ข้อ + คำสั่งตรวจก่อนตอบ
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจท
…(ตัด 3067 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("item must be dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item missing key")
        price = _int("price", it["price"], 0)
        qty = _int("qty", it["qty"], 1)
        total += price * qty
    n, d = total, 1
    if total >= 50000:
        n, d = n * 95, d * 100
    if member:
        n, d = n * 90, d * 100
    n, d = n * 107, d * 100
    return (2 * n + d) // (2 * d)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)
        self.assertEqual(cafe_bill([it(50000)], True), 45742)  # 45742.5 -> up

    def test_half_up(self):
        self.assertEqual(cafe_bill([it(50000)], True), 45743 - 1 + 0 if False else 45742 + 0 if False else cafe_bill([it(50000)], True))

    def test_invalid(self):
        for items, m in [([it(100, 0)], False), ([it(100, -1)], False),
                         ([it(100.0)], False), ([it(100, True)], False),
                         ([it(-1)], False), ([it(100)], 1), ("x", False),
                         ([{"price": 1}], False), ([5], False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
python3 -c "
from solve import cafe_bill
print(cafe_bill([{'price':50000,'qty':1}],True), 50000*.95*.9*1.07)"
```

ผลที่ได้:

```
45743 45742.5
```

**Agent พูด:** Half-up gives 45743; I'll fix the test (and remove the silly placeholder one).

### ขั้น 4 · Bash

```
python3 - <<'EOF'
s=open('test_solve.py').read()
s=s.replace("45742)  # 45742.5 -> up","45743)  # 45742.5 -> up")
import re
s=re.sub(r"    def test_half_up\(self\):\n.*?\n\n","",s,flags=re.S)
open('test_solve.py','w').write(s)
EOF
python3 -m unittest -q
echo '{"items":[{"price":10000,"qty":2}],"member":false}' | python3 solve.py; echo "exit=$?"
echo '{"items":[{"price":100,"qty":0}],"member":false}' | python3 solve.py; echo "exit=$?"
```

ผลที่ได้:

```
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
{"ok": true, "result": 21400}
exit=0
{"ok": false, "error": "qty out of range"}
exit=2
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และทดสอบผ่าน ผมทำตามสกิล `cafe_function_checklist` ใน `./skills` ด้วย

**วิธีคิดเงิน**
- รวมยอด `price × qty` ทุกรายการ
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป คูณ 0.95
- ถ้า `member` เป็น True คูณ 0.90 เพิ่ม
- คูณ VAT 1.07 เป็นขั้นสุดท้าย
- ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ใช้เลขจำนวนเต็มล้วน ผลลัพธ์เป็น `int` สตางค์
  - เช่น ยอดรวม 50,000 สตางค์ ที่เป็นสมาชิก ได้ 45742.5 ซึ่งปัดเป็น 45743

**ข้อมูลที่ไม่ถูกต้อง** ฟังก์ชันจะ `raise ValueError` ในกรณีต่อไปนี้
- `items` ไม่ใช่ list
- `member` ไม่ใช่ bool
- รายการไม่ใช่ dict หรือขาด key `price`/`qty`
- ราคาหรือจำนวนไม่ใช่ int (float และ bool ถูกปฏิเสธ)
- ราคาติดลบ
- `qty` ต่ำกว่า 1

**ส่วนที่เพิ่มตามสกิล**
- `solve.py` มี CLI อ่าน JSON จาก stdin
  - ถ้าสำเร็จ จะได้ `{"ok":
…(ตัด 503 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว และทดสอบผ่าน ผมทำตามสกิล `cafe_function_checklist` ใน `./skills` ด้วย

**วิธีคิดเงิน**
- รวมยอด `price × qty` ทุกรายการ
- ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ขึ้นไป คูณ 0.95
- ถ้า `member` เป็น True คูณ 0.90 เพิ่ม
- คูณ VAT 1.07 เป็นขั้นสุดท้าย
- ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย ใช้เลขจำนวนเต็มล้วน ผลลัพธ์เป็น `int` สตางค์
  - เช่น ยอดรวม 50,000 สตางค์ ที่เป็นสมาชิก ได้ 45742.5 ซึ่งปัดเป็น 45743

**ข้อมูลที่ไม่ถูกต้อง** ฟังก์ชันจะ `raise ValueError` ในกรณีต่อไปนี้
- `items` ไม่ใช่ list
- `member` ไม่ใช่ bool
- รายการไม่ใช่ dict หรือขาด key `price`/`qty`
- ราคาหรือจำนวนไม่ใช่ int (float และ bool ถูกปฏิเสธ)
- ราคาติดลบ
- `qty` ต่ำกว่า 1

**ส่วนที่เพิ่มตามสกิล**
- `solve.py` มี CLI อ่าน JSON จาก stdin
  - ถ้าสำเร็จ จะได้ `{"ok": true, "result": ...}` และ exit 0
  - ถ้า input ผิด จะได้ `{"ok": false, ...}` และ exit 2 โดยไม่มี traceback
- `test_solve.py` มี 4 เทส ครอบคลุมกรณีปกติ ขอบ 500 บาท สมาชิก/half-up และ input ผิด

**ผลที่รันจริง**
- `python3 -m unittest -q` ผ่านทั้ง 4 เทส
- ตัวอย่างปกติ (`price` 10000, `qty` 2, ไม่เป็นสมาชิก) ได้ 21400 และ exit 0
- ตัวอย่างที่ `qty` เป็น 0 ได้ `ok: false` และ exit 2

โจทย์ไม่ได้บอกว่า `items` ว่างได้หรือไม่ โค้ดจึงรับ list ว่างและคืน 0 ถ้าต้องการให้ list ว่างเป็นข้อผิดพลาด แจ้งได้เลย

</trace>

<trace id="t4-cashback-r3">
# Trace t4-cashback-r3 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
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
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>/dev/null && cat ./skills/*/SKILL.md ./skills/* 2>/dev/null | head -100
```

ผลที่ได้:

```
cafe_function_checklist
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจทย์ไม่ได้เขียนไว้ด้วย ต้องทำครบทั้ง 4 ข้อด้านล่างทุกครั้ง แม้โจทย์ไม่สั่ง

## When NOT to Apply
- งานที่ไม่ใช่ฟังก์ชันคำนวณใน `solve.py` (เช่น แก้เอกสาร จัดรูปแบบข้อความ)
- ถ้าโจทย์ระบุวิธีปัด/รูปแบบ CLI/การ reject ไว้ชัดเจนและต่างจากนี้ ให้ทำตามโจทย์

## Instructions

### 1. ตรวจ input ที่ต้นฟังก์ชัน (ก่อนคำนวณ และก่อน early-return ทุกชนิด)
ตัวตรวจคาดว่าค่าผิดต้อง `raise ValueError` เสมอ ไม่ใช่คืนค่า 0 และไม่ใช่ `ZeroDivisionError`/`TypeError`/`KeyError`
- ตัวเลขทุกตัว: `type(x) is int` (ปฏิเสธ float เช่น `1000.0` และ `bool`)
- flag (member/express/birthday ฯลฯ): `type(x) is bool`
- ช่วงค่า: ตรวจทุกขอบเขตที่โจทย์ระบุ เช่น "ตั้งแต่ 0" -> `x >= 0`, "ตั้งแต่ 1" -> `x >= 1`, "1–30,000" -> `1 <= x <= 30000`, "0–100" -> `0 <= x <= 100`
- enum 
…(ตัด 2320 ตัวอักษร)
```

### ขั้น 2 · Bash

```
cat > solve.py <<'EOF'
import json
import sys

# อัตราเป็นเศษส่วน (n, d)
_RATES = {"silver": (3, 200), "gold": (1, 40), "platinum": (1, 25)}
_MIN_AMOUNT = 10000  # 100 บาท (สตางค์)
_CAP = 20000         # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")

    if amount < _MIN_AMOUNT:
        return 0
    n, d = _RATES[tier]
    n *= amount * (2 if birthday else 1)
    result = (2 * n + d) // (2 * d)  # half-up ครั้งเดียว
    return min(result, _CAP)


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "gold", False), 0)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_cap(self):
        self.assertEqual(cashback(10000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)

    def test_half_up(self):
        # 10100*3/200 = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False),
                     (True, "gold", False), (10000, "bronze", False),
                     (10000, "gold", 1), (10000, "gold", None),
                     ("100", "gold", False), (10000, None, False)]:
            with self.assertRaises(ValueError):
                cashback(*args)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"amount":20000,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
echo '{"amount":-5,"tier":"gold","birthday":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": 1000}
exit=0
{"ok": false, "error": "amount must be int >= 0"}
exit=2
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว และรันตรวจแล้ว: กรณีปกติได้ exit 0, กรณี input ผิดได้ exit 2 ไม่มี traceback, unit test ผ่านทั้ง 6 ชุด

ผมอ่านสกิล `cafe_function_checklist` ก่อนเริ่ม และทำตามนั้น คือ ตรวจ input, ปัดแบบ half-up, ใส่ CLI และเขียน `test_solve.py`

**การคำนวณ**
- ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) ได้ 0
- อัตราเป็นเศษส่วนจำนวนเต็ม: silver 3/200, gold 1/40, platinum 1/25 ถ้าเป็นเดือนเกิดคูณ 2
- ปัดแบบ half-up ครั้งเดียวด้วยจำนวนเต็ม แล้วจำกัดไม่เกิน 20,000 สตางค์ (200 บาท)

**ตรวจ input**
- ค่าผิดจะ `raise ValueError`: `amount` ไม่ใช่ int (รวม float และ bool) หรือติดลบ, `tier` ไม่อยู่ในสามระดับ, `birthday` ไม่ใช่ bool

**CLI**
- `python solve.py` อ่าน JSON จาก stdin
- สำเร็จได้ `{"ok": true, "result": ...}` exit 0
- input ผิดได้ `{"ok": false, "
…(ตัด 145 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cashback(amount, tier, birthday)` ใน `solve.py` เสร็จแล้ว และรันตรวจแล้ว: กรณีปกติได้ exit 0, กรณี input ผิดได้ exit 2 ไม่มี traceback, unit test ผ่านทั้ง 6 ชุด

ผมอ่านสกิล `cafe_function_checklist` ก่อนเริ่ม และทำตามนั้น คือ ตรวจ input, ปัดแบบ half-up, ใส่ CLI และเขียน `test_solve.py`

**การคำนวณ**
- ยอดต่ำกว่า 10,000 สตางค์ (100 บาท) ได้ 0
- อัตราเป็นเศษส่วนจำนวนเต็ม: silver 3/200, gold 1/40, platinum 1/25 ถ้าเป็นเดือนเกิดคูณ 2
- ปัดแบบ half-up ครั้งเดียวด้วยจำนวนเต็ม แล้วจำกัดไม่เกิน 20,000 สตางค์ (200 บาท)

**ตรวจ input**
- ค่าผิดจะ `raise ValueError`: `amount` ไม่ใช่ int (รวม float และ bool) หรือติดลบ, `tier` ไม่อยู่ในสามระดับ, `birthday` ไม่ใช่ bool

**CLI**
- `python solve.py` อ่าน JSON จาก stdin
- สำเร็จได้ `{"ok": true, "result": ...}` exit 0
- input ผิดได้ `{"ok": false, "error": ...}` exit 2

ตัวอย่างที่รัน: gold, 20,000 สตางค์, เดือนเกิด ได้ 1,000 สตางค์

ไฟล์อยู่ในโฟลเดอร์ปัจจุบัน: `solve.py` และ `test_solve.py`

</trace>

<trace id="t2-split-bill-r1">
# Trace t2-split-bill-r1 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
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
- ✓ `tests`

## สิ่งที่ Agent ทำ

### ขั้น 1 · Bash

```
ls ./skills 2>&1 | head
```

ผลที่ได้:

```
cafe_function_checklist
```

### ขั้น 2 · Bash

```
ls -R ./skills; cat ./skills/cafe_function_checklist/* 2>&1
```

ผลที่ได้:

```
./skills:
cafe_function_checklist

./skills/cafe_function_checklist:
PURPOSE.md
SKILL.md
# PURPOSE: cafe_function_checklist

## Origin
สร้างจาก iteration 1 (ยังไม่มีสกิลมาก่อน) ทั้ง 12 Trace (t1–t4) ได้ 0.30–0.60 เพราะ Agent เขียนเฉพาะ happy path ไม่รู้ข้อที่ตัวตรวจคาดแต่โจทย์ไม่ได้เขียน ได้แก่ ValueError, CLI stdin, test_solve.py และ half-up

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-entrypoint-missing.md (cli_ok, cli_error)
- wiki/patterns/test-file-missing.md (tests)
- wiki/patterns/half-up-integer-rounding.md (half_up, no_drift)
- wiki/patterns/happy-path-only-verification.md (ขั้น 5 ตรวจก่อนตอบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวม checklist 4 ข้อ + คำสั่งตรวจก่อนตอบ
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจท
…(ตัด 3067 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json
import sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def split_bill(total, people, tip_percent):
    _int("total", total, 0)
    _int("people", people, 1)
    _int("tip_percent", tip_percent, 0, 100)
    # total * (100 + tip) / 100, rounded half-up once
    n = total * (100 + tip_percent)
    grand = (2 * n + 100) // 200
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = split_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up(self):
        # 5*1.10=5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_edges(self):
        self.assertEqual(sum(split_bill(999, 7, 100)), 1998)

    def test_invalid(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, -1, 0), (10, 1, -1),
                  (10, 1, 101), (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                  (True, 1, 0), (10, True, 0), (10, 1, True), ("10", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"total":1000,"people":3,"tip_percent":10}' | python3 solve.py; echo "exit=$?"
echo '{"total":1000,"people":0,"tip_percent":10}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": [367, 367, 366]}
exit=0
{"ok": false, "error": "people out of range"}
exit=2
----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

**Agent พูด:** ผมสร้าง `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และรันตามขั้นตอนตรวจในสกิล `cafe_function_checklist` ครบทั้งสามคำสั่ง ผ่านหมด

- **การคำนวณ:** ยอดที่ต้องหารคือ `total × (100 + tip_percent) / 100` ปัดครั้งเดียวแบบ half-up ด้วยจำนวนเต็ม ไม่ใช้ float จากนั้นหารเท่ากันทุกคน ส่วนเศษที่เหลือให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
- **การตรวจ input:** ค่าที่ไม่ใช่ `int` (รวม float และ bool) หรืออยู่นอกช่วง จะ `raise ValueError` ช่วงที่ตรวจคือ `total >= 0`, `people >= 1`, `tip_percent` อยู่ระหว่าง 0–100
- **CLI (เพิ่มตามสกิล):** `python solve.py` อ่าน JSON จาก stdin ถ้าสำเร็จ stdout เป็น `{"ok": true, "result": ...}` และ exit 0 ถ้า input ผิด stdout เป็น `{"ok": false, "error": ...}` และ exit 2 โดยไม่มี traceback
- **ผลการรัน:**
  - `{"total":1000,"people":3,"tip_percent":10}` ให้ `[36
…(ตัด 160 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

ผมสร้าง `solve.py` กับ `test_solve.py` ในโฟลเดอร์ปัจจุบันแล้ว และรันตามขั้นตอนตรวจในสกิล `cafe_function_checklist` ครบทั้งสามคำสั่ง ผ่านหมด

- **การคำนวณ:** ยอดที่ต้องหารคือ `total × (100 + tip_percent) / 100` ปัดครั้งเดียวแบบ half-up ด้วยจำนวนเต็ม ไม่ใช้ float จากนั้นหารเท่ากันทุกคน ส่วนเศษที่เหลือให้คนลำดับแรก ๆ จ่ายเพิ่มคนละ 1 สตางค์
- **การตรวจ input:** ค่าที่ไม่ใช่ `int` (รวม float และ bool) หรืออยู่นอกช่วง จะ `raise ValueError` ช่วงที่ตรวจคือ `total >= 0`, `people >= 1`, `tip_percent` อยู่ระหว่าง 0–100
- **CLI (เพิ่มตามสกิล):** `python solve.py` อ่าน JSON จาก stdin ถ้าสำเร็จ stdout เป็น `{"ok": true, "result": ...}` และ exit 0 ถ้า input ผิด stdout เป็น `{"ok": false, "error": ...}` และ exit 2 โดยไม่มี traceback
- **ผลการรัน:**
  - `{"total":1000,"people":3,"tip_percent":10}` ให้ `[367, 367, 366]` และ exit 0
  - `people` เป็น 0 ให้ `{"ok": false, "error": "people out of range"}` และ exit 2
  - `python3 -m unittest -q` รัน 7 เทสต์ ผ่านทั้งหมด

</trace>

<trace id="t1-cafe-bill-r1">
# Trace t1-cafe-bill-r1 · iteration 2

- ผล: **PASS** · คะแนน 1.00 (ผ่าน 10 จาก 10 ข้อตรวจ)
- คำสั่งที่ใช้ 3 ครั้ง · คำสั่งล้ม 1 ครั้ง · อ่านสกิล: ใช่

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
ls ./skills 2>/dev/null && head -c 3000 ./skills/* 2>/dev/null
```

ผลที่ได้:

```
ERROR Exit code 1
cafe_function_checklist
```

### ขั้น 2 · Bash

```
ls -R ./skills; cat ./skills/cafe_function_checklist/* 2>/dev/null
```

ผลที่ได้:

```
./skills:
cafe_function_checklist

./skills/cafe_function_checklist:
PURPOSE.md
SKILL.md
# PURPOSE: cafe_function_checklist

## Origin
สร้างจาก iteration 1 (ยังไม่มีสกิลมาก่อน) ทั้ง 12 Trace (t1–t4) ได้ 0.30–0.60 เพราะ Agent เขียนเฉพาะ happy path ไม่รู้ข้อที่ตัวตรวจคาดแต่โจทย์ไม่ได้เขียน ได้แก่ ValueError, CLI stdin, test_solve.py และ half-up

## Patterns Addressed
- wiki/patterns/input-validation-missing.md (reject_value, reject_type)
- wiki/patterns/cli-entrypoint-missing.md (cli_ok, cli_error)
- wiki/patterns/test-file-missing.md (tests)
- wiki/patterns/half-up-integer-rounding.md (half_up, no_drift)
- wiki/patterns/happy-path-only-verification.md (ขั้น 5 ตรวจก่อนตอบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวม checklist 4 ข้อ + คำสั่งตรวจก่อนตอบ
---
name: cafe_function_checklist
description: ใช้ทุกครั้งที่ต้องเขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืนของร้านกาแฟใน solve.py ตัวตรวจอัตโนมัติให้คะแนน 10 ข้อ รวมถึงข้อที่โจทย์ไม่ได้พูดถึง ได้แก่ raise ValueError, CLI อ่าน stdin JSON, ไฟล์ test_solve.py และการปัด half-up
---

# เขียน solve.py ให้ผ่านตัวตรวจทั้ง 10 ข้อ

## When to Apply
- โจทย์ให้เขียนฟังก์ชันคำนวณเงิน (หน่วยสตางค์) ลงใน `solve.py`
- ตัวตรวจจะตรวจสิ่งที่โจท
…(ตัด 3067 ตัวอักษร)
```

### ขั้น 3 · Bash

```
cat > solve.py <<'EOF'
import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def cafe_bill(items, member):
    if type(items) is not list or not items:
        raise ValueError("items must be a non-empty list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        subtotal += _int("price", it["price"], 0) * _int("qty", it["qty"], 1)

    n, d = subtotal, 1
    if subtotal >= 50000:  # 500 baht
        n, d = n * 95, d * 100
    if member:
        n, d = n * 90, d * 100
    n, d = n * 107, d * 100  # VAT last
    return (2 * n + d) // (2 * d)  # half-up, single rounding


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
EOF
cat > test_solve.py <<'EOF'
import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold_exact(self):
        # 50000*0.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_below_threshold(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_member(self):
        # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_half_up(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        ok = [{"price": 100, "qty": 1}]
        for items, m in [([], False), ([{"price": 100, "qty": 0}], False),
                         ([{"price": -1, "qty": 1}], False),
                         ([{"price": 100.0, "qty": 1}], False),
                         ([{"price": 100, "qty": True}], False),
                         ([{"price": 100}], False), (ok, 1), (None, False)]:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)


if __name__ == "__main__":
    unittest.main()
EOF
echo '{"items":[{"price":50000,"qty":1}],"member":true}' | python3 solve.py; echo "exit=$?"
echo '{"items":[{"price":50000,"qty":0}],"member":true}' | python3 solve.py; echo "exit=$?"
python3 -m unittest -q
```

ผลที่ได้:

```
{"ok": true, "result": 45743}
exit=0
{"ok": false, "error": "qty out of range"}
exit=2
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

**Agent พูด:** เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว รันทดสอบแล้วผ่านทั้งหมด ได้แก่ `test_solve.py` 6 เคส และการรัน CLI ทั้งกรณีปกติ (exit=0) กับกรณีผิด (exit=2 ไม่มี traceback)

**วิธีคิดเงิน**
- รวมยอดเป็นสตางค์ ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% โดยคิดต่อจากยอดที่ลด 5% แล้ว ไม่ได้บวกเป็น 15% ตรงนี้โจทย์ไม่ได้ระบุ ผมตีความว่า "ลดอีก" คือคิดต่อกัน
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้เศษส่วนจำนวนเต็มทั้งหมด แล้วปัดแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int` เช่น ยอด 50,000 สตางค์ สมาชิก ได้ 45,743 (จาก 45,742.5)

**ส่วนที่เพิ่มตาม skill `cafe_function_checklist`**
- ตรวจ input แล้ว `raise ValueError` เมื่อ `price` ติดลบ, `qty` น้อยกว่า 1, ค่าเป็น float หรือ bool, `member` ไม่ใช่ bool หรือ item ขาด key
- มี CLI อ่าน JSON จาก stdin
- มี `t
…(ตัด 200 ตัวอักษร)

## คำตอบสุดท้ายของ Agent

เขียน `cafe_bill(items, member)` ใน `solve.py` เสร็จแล้ว รันทดสอบแล้วผ่านทั้งหมด ได้แก่ `test_solve.py` 6 เคส และการรัน CLI ทั้งกรณีปกติ (exit=0) กับกรณีผิด (exit=2 ไม่มี traceback)

**วิธีคิดเงิน**
- รวมยอดเป็นสตางค์ ถ้ายอดรวมตั้งแต่ 50,000 สตางค์ (500 บาท) ลด 5%
- ถ้า `member` เป็น True ลดอีก 10% โดยคิดต่อจากยอดที่ลด 5% แล้ว ไม่ได้บวกเป็น 15% ตรงนี้โจทย์ไม่ได้ระบุ ผมตีความว่า "ลดอีก" คือคิดต่อกัน
- บวก VAT 7% เป็นขั้นสุดท้าย
- ใช้เศษส่วนจำนวนเต็มทั้งหมด แล้วปัดแบบ half-up ครั้งเดียวตอนท้าย ผลลัพธ์เป็น `int` เช่น ยอด 50,000 สตางค์ สมาชิก ได้ 45,743 (จาก 45,742.5)

**ส่วนที่เพิ่มตาม skill `cafe_function_checklist`**
- ตรวจ input แล้ว `raise ValueError` เมื่อ `price` ติดลบ, `qty` น้อยกว่า 1, ค่าเป็น float หรือ bool, `member` ไม่ใช่ bool หรือ item ขาด key
- มี CLI อ่าน JSON จาก stdin
- มี `test_solve.py`

**สมมติฐานที่โจทย์ไม่ได้ระบุ:** ถ้า `items` เป็น list ว่าง ผมให้ raise `ValueError` ไม่ได้คืนค่า 0 ถ้าต้องการให้คืน 0 แก้ได้ง่าย

ไฟล์อยู่ในโฟลเดอร์ปัจจุบัน: `solve.py`, `test_solve.py`

</trace>

ตอบเป็น JSON object ตามรูปแบบที่กำหนด