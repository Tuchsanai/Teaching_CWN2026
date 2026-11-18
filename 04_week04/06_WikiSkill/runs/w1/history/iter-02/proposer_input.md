# Iteration 2

Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): 93.3%

## wiki/index.md

# Wiki Index

- [too-few-test-methods](wiki/patterns/too-few-test-methods.md): ยังเกิดอยู่ (ตกข้อ `tests` ใน 4 จาก 7 Trace รอบ 2: พบ 4–5 เทสต์ ต้องมีอย่างน้อย 6; ผ่านที่ 6, 7, 9) มี test_solve.py แล้วแต่นับได้ไม่ถึง 6 เทสต์ เพราะสกิลไม่บอกเกณฑ์จำนวนและ Agent เขียนหนึ่งเมธอดต่อหมวดแล้วยัด assert/subTest หลายตัวไว้ในเมธอดเดียว (subTest นับเป็นเมธอดเดียว) ให้แตกเป็นอย่างน้อย 8 เมธอด (ปกติหลายแบบ ขอบต่อเกณฑ์ ปัดเศษ reject ต่อพารามิเตอร์) และดู `Ran N tests` ให้ N ≥ 8 ก่อนตอบ ถ้าแก้ข้อนี้ 2 จาก 5 งานที่ล้มในรอบนี้จะผ่านเต็ม
- [policy-ambiguous-edge-cases](wiki/patterns/policy-ambiguous-edge-cases.md): ยังเกิดอยู่และยังไม่ยืนยันสาเหตุ (`policy` ตกทุกงาน t3/t4 รอบ 2: shipping_fee ระยะ 0 คาด 0 ได้ 8000 พลาด 4 จาก 6; cashback silver เดือนเกิด 20000 คาด 300 ได้ 600 พลาด 6 จาก 6 เทียบ 3 จาก 6 ตอนปัดลงในรอบ 1) เพราะ Agent ตีความกติกาตามตัวอักษรและจดข้อสมมติแล้วก็ยังพลาด สกิลรอบ 1 ไม่ได้ครอบเรื่องนี้ ให้ยังไม่ใส่กติกาเฉพาะโจทย์ลงสกิล รอบหน้าดูข้อความตัวตรวจครบทุกกรณี และเทียบการปัดลงกับปัดครึ่งขึ้นใน cashback
- [missing-test-file](wiki/patterns/missing-test-file.md): แก้ได้แล้วเฉพาะส่วนไม่มีไฟล์ (ทุก Trace รอบ 2 มี test_solve.py และรันผ่าน) เดิมตกเพราะ Agent ทดสอบด้วย `python3 -c` ทิ้งและไม่มีสกิล ให้คงข้อกำหนดสร้าง test_solve.py แบบ unittest ในสกิล ส่วนเกณฑ์จำนวนเทสต์ที่ยังตกอยู่ดู too-few-test-methods
- [shallow-self-check](wiki/patterns/shallow-self-check.md): ดีขึ้นมากในรอบ 2 (มีสกิลและทุก Trace รัน unittest, stdin สำเร็จ/ผิด, เทสต์อินพุตผิด) แต่ยังเหลือช่องว่าง Agent ตอบว่าเทสต์ผ่านครบโดยไม่เทียบเกณฑ์จำนวนเทสต์ที่ตัวตรวจต้องการ และจดข้อสมมติโดยไม่ได้ยืนยัน เพราะเกณฑ์บางข้อ Agent มองไม่เห็นเอง ให้ใส่เกณฑ์ที่เป็นตัวเลขในรายการตรวจก่อนตอบ และอ่านเทสต์ที่เขียนเองให้ถูกก่อนรัน (ตัวอย่างดี: t1-cafe-bill-r3 แก้ค่าคาดที่ผิดในเทสต์เอง)
- [integer-money-arithmetic](wiki/patterns/integer-money-arithmetic.md): แก้ได้แล้ว/ใช้ได้ผลต่อเนื่อง (ผ่าน `basic`/`no_drift`/`boundary` ทุก Trace และ `half_up` ทุกโจทย์ที่มีข้อนี้ในรอบ 2) ปัญหาทศนิยมและการปัดซ้อนหายไป เพราะ Agent คิดด้วยจำนวนเต็มหรือ Fraction และปัดครั้งเดียวตอนท้าย ให้คงแนวทางนี้และคืนผลเป็น int จริง แต่อย่าถือว่าปัดครึ่งขึ้นปลอดภัยเสมอใน cashback (ยังไม่ยืนยัน)
- [missing-input-validation](wiki/patterns/missing-input-validation.md): แก้ได้แล้ว (`reject_value`/`reject_type` ผ่านทั้ง 7 Trace รอบ 2 หลังมีสกิล solve-py-contract) ปัญหาเดิมคือค่านอกช่วง ชนิดผิด หรือ float ไม่ถูก raise ValueError (people=0 ได้ ZeroDivisionError) เพราะโค้ดเป็นสูตรล้วนและโจทย์ไม่บอกตรง ๆ ให้คงการตรวจ `type(x) is int`/bool/ค่าที่อนุญาตไว้ต้นฟังก์ชันแล้ว raise ValueError ก่อนคำนวณ (ยังไม่ยืนยัน: ตัวตรวจนับ bool หรือไม่)
- [missing-cli-entrypoint](wiki/patterns/missing-cli-entrypoint.md): แก้ได้แล้ว (`cli_ok`/`cli_error` ผ่านทั้ง 7 Trace รอบ 2) ปัญหาเดิมคือรัน solve.py ด้วย stdin แล้วได้ exit 0 และ stdout ว่าง เพราะไม่มี `__main__` ให้คงบล็อกจากสกิล: อ่าน JSON จาก stdin เรียก `fn(**data)` พิมพ์ `{"ok":true,"result":...}` exit 0 หรือ `{"ok":false,"error":...}` exit 2 โดยไม่มี traceback และลองรันทั้งสองกรณี

## wiki/skill-impact.md

# Skill Impact

บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ

## Iteration 1 · create `solve-py-contract` · ACCEPTED

- Validation ของสกิลที่เสนอ: 93.3% · R_best ก่อนหน้า: 45.0% -> รับ (R_best ใหม่ 93.3%)
- เหตุผลของข้อเสนอ: ทั้ง 12 Trace ไม่มีสกิล และตกข้อตรวจ reject_value, reject_type, cli_ok, cli_error, tests เหมือนกันทุกโจทย์ ส่วนข้อตรวจเรื่องการคำนวณผ่านหมด ซึ่งตรงกับ pattern missing-input-validation, missing-cli-entrypoint และ missing-test-file ผมเปิดดู t1-cafe-bill-r1, t2-split-bill-r2, t3-shipping-fee-r1 และ t4-cashback-r2 แล้วพบว่าโค้ดมีแต่สูตร ไม่มี ValueError ไม่มีบล็อก __main__ และไม่มี test_solve.py สกิลนี้รวมเป็นสกิลเดียวเรื่อง 'สัญญาของ solve.py ที่โจทย์ไม่บอก' ไม่ใส่คำตอบเฉพาะโจทย์ และเว้นเรื่อง policy ที่ยังไม่ยืนยันสาเหตุ

Diff ของ SKILL.md ที่เสนอ:

```diff
--- a/skills/solve-py-contract/SKILL.md
+++ b/skills/solve-py-contract/SKILL.md
@@ -0,0 +1,96 @@
+---
+name: solve-py-contract
+description: ข้อกำหนดที่ไม่ได้เขียนในโจทย์ของงานเขียนฟังก์ชันใน solve.py (ตรวจอินพุตแล้ว raise ValueError, โหมด CLI อ่าน JSON จาก stdin, ไฟล์ test_solve.py) ใช้ทุกครั้งที่ต้องสร้างหรือแก้ solve.py ก่อนตอบ
+---
+
+# solve.py ต้องมี 3 ส่วนเสมอ แม้โจทย์ไม่บอก
+
+ตัวตรวจไม่ได้ดูแค่ว่าสูตรถูก แต่ตรวจสัญญาของไฟล์ด้วย ถ้าเขียนแต่สูตรคำนวณจะเสียคะแนนครึ่งหนึ่ง ทำทั้ง 3 ส่วนต่อไปนี้ทุกโจทย์
+
+## 1) ตรวจอินพุตไว้ต้นฟังก์ชัน แล้ว raise ValueError
+
+ช่วงค่าและชนิดที่โจทย์เขียนไว้ (เช่น "ตั้งแต่ 1", "0–100", "1–30,000", รายชื่อค่าที่อนุญาต) คือเงื่อนไขที่ต้องตรวจ ไม่ใช่แค่คำอธิบาย
+
+- ก่อนคำนวณใด ๆ ให้แปลงทุกช่วงเป็น `if ... : raise ValueError("ข้อความที่อ่านรู้เรื่อง")` ทั้งขอบล่างและขอบบน (ตรวจค่า 0, ค่าติดลบ, ค่าเกินขอบ)
+- พารามิเตอร์ที่ควรเป็นจำนวนเต็ม ให้ตรวจด้วย `type(x) is int` ซึ่งปฏิเสธ float (เช่น `4500.0`) และ bool (`True`) ไปพร้อมกัน ห้ามใช้ `isinstance(x, int)` เพราะ bool ผ่าน
+- พารามิเตอร์ที่ควรเป็น bool ให้ตรวจ `type(x) is bool`
+- พารามิเตอร์ที่เป็นข้อความที่มีค่าอนุญาตจำกัด (เช่น ระดับสมาชิก) ให้ตรวจ `type(x) is str and x in ALLOWED`
+- พารามิเตอร์ที่เป็น list ของ dict ให้ตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ, และค่าในแต่ละ key ผ่านกฎชนิด/ช่วงเหมือนกัน (ตรวจทุกรายการ ไม่ใช่แค่รายการแรก)
+- ห้ามปล่อยให้ `ZeroDivisionError`, `KeyError`, `TypeError` หลุดออกมาแทน ValueError ตรวจให้เสร็จก่อนถึงบรรทัดที่หารหรือค้นตาราง
+- ผลที่คืนต้องเป็น `int` จริง (หรือ list ของ int) ตามที่โจทย์สั่ง ไม่ใช่ float
+
+โครงตัวอย่าง:
+
+```python
+def _need_int(name, v, lo=None, hi=None):
+    if type(v) is not int:
+        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
+    if lo is not None and v < lo:
+        raise ValueError(f"{name} ต้องไม่น้อยกว่า {lo}")
+    if hi is not None and v > hi:
+        raise ValueError(f"{name} ต้องไม่เกิน {hi}")
+```
+
+เรียกตัวช่วยนี้ที่ต้นฟังก์ชันหลักกับทุกพารามิเตอร์
+
+## 2) โหมด CLI ท้าย solve.py
+
+ตัวตรวจรัน `python3 solve.py` โดยส่ง JSON object ทาง stdin ที่มี key ตรงกับชื่อพารามิเตอร์ของฟังก์ชัน ถ้าไม่มีบล็อกนี้จะได้ exit 0 และ stdout ว่าง ให้ต่อท้ายไฟล์เสมอ (เปลี่ยน `FUNC` เป็นชื่อฟังก์ชันของโจทย์):
+
+```python
+if __name__ == "__main__":
+    import json, sys
+    try:
+        data = json.loads(sys.stdin.read())
+        if type(data) is not dict:
+            raise ValueError("อินพุตต้องเป็น JSON object")
+        result = FUNC(**data)
+    except Exception as e:  # ValueError, TypeError, KeyError, JSONDecodeError
+        print(json.dumps({"ok": False, "error": str(e) or type(e).__name__}, ensure_ascii=False))
+        sys.exit(2)
+    print(json.dumps({"ok": True, "result": result}))
+    sys.exit(0)
+```
+
+- สำเร็จ: stdout เป็น `{"ok": true, "result": ...}` exit 0
+- ผิดพลาด: stdout เป็น `{"ok": false, "error": "..."}` exit 2 และห้ามมี traceback
+- ต้องอยู่ใน `if __name__ == "__main__":` เพื่อให้ `import solve` จากไฟล์ทดสอบไม่ค้างรอ stdin
+- ลองรันจริงทั้งกรณีสำเร็จและกรณีผิด แล้วดูทั้ง stdout และ exit code:
+
+```bash
+echo '{...อินพุตถูก...}' | python3 solve.py; echo "exit=$?"
+echo '{...อินพุตผิด...}' | python3 solve.py; echo "exit=$?"
+```
+
+## 3) ไฟล์ test_solve.py ข้าง solve.py
+
+ต้องมีไฟล์ `test_solve.py` (unittest) ในโฟลเดอร์เดียวกับ `solve.py` การรันทดสอบด้วย `python3 -c` แล้วทิ้งไม่นับ ให้ครอบคลุม:
+
+- กรณีปกติอย่างน้อย 3 กรณี
+- ค่าขอบของทุกเกณฑ์ในโจทย์ (ค่าที่พอดีเกณฑ์ ต่ำกว่า 1 หน่วย สูงกว่า 1 หน่วย) พร้อมคอมเมนต์ข้อสมมติเมื่อกติกาไม่ชัด
+- เคสปัดเศษ
+- อินพุตผิดอย่างน้อย 1 ตัวต่อ 1 พารามิเตอร์ ด้วย `with self.assertRaises(ValueError):` รวมกรณี float, ค่านอกช่วง, ค่า 0 และชนิดผิด
+
+```python
+import unittest
+from solve import FUNC
+
+class TestSolve(unittest.TestCase):
+    def test_normal(self):
+        self.assertEqual(FUNC(...), ...)
+    def test_reject(self):
+        with self.assertRaises(ValueError):
+            FUNC(...)
+
+if __name__ == "__main__":
+    unittest.main()
+```
+
+รัน `python3 -m unittest test_solve -v` ในโฟลเดอร์นั้นให้ผ่านทุกเทสต์ก่อนตอบ
+
+## รายการตรวจก่อนตอบ
+
+- [ ] ทุกพารามิเตอร์มีการตรวจชนิดและช่วง และ float/bool/0/ติดลบ/ค่าไม่อยู่ในรายการ ได้ ValueError
+- [ ] ท้ายไฟล์มีบล็อก CLI และลองรัน stdin ทั้งกรณีสำเร็จและผิดแล้ว (exit 0 / exit 2, ไม่มี traceback)
+- [ ] มี test_solve.py และรันผ่านครบ
+- [ ] ผลลัพธ์เป็น int จริง และคำนวณด้วยจำนวนเต็มหรือ Fraction ปัดครั้งเดียวตอนท้าย
```

## summary.md

# ผลของ Training rollouts · iteration 2

คะแนนเฉลี่ย 89.5% · ผ่านครบทุกข้อ 2/12 Trace

| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |
|---|---|---|---|
| t1-cafe-bill-r1 | FAIL | 0.90 | tests |
| t1-cafe-bill-r2 | FAIL | 0.90 | tests |
| t1-cafe-bill-r3 | FAIL | 0.90 | tests |
| t2-split-bill-r1 | PASS | 1.00 | - |
| t2-split-bill-r2 | FAIL | 0.90 | tests |
| t2-split-bill-r3 | PASS | 1.00 | - |
| t3-shipping-fee-r1 | FAIL | 0.91 | policy |
| t3-shipping-fee-r2 | FAIL | 0.82 | tests policy |
| t3-shipping-fee-r3 | FAIL | 0.82 | tests policy |
| t4-cashback-r1 | FAIL | 0.90 | policy |
| t4-cashback-r2 | FAIL | 0.90 | policy |
| t4-cashback-r3 | FAIL | 0.80 | tests policy |

## รายละเอียดของข้อตรวจที่ไม่ผ่าน (คาดว่าอะไร · ได้อะไร)

- t1-cafe-bill-r1 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t1-cafe-bill-r2 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t1-cafe-bill-r3 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t2-split-bill-r2 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r1 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t3-shipping-fee-r2 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r2 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t3-shipping-fee-r3 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r3 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t4-cashback-r1 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 6 จาก 6 กรณี
- t4-cashback-r2 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 6 จาก 6 กรณี
- t4-cashback-r3 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t4-cashback-r3 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 6 จาก 6 กรณี

## Active skills

- skills/solve-py-contract/SKILL.md

สำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย