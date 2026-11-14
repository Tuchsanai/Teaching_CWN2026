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

## Iteration 2 · patch `solve-py-contract` · ACCEPTED

- Validation ของสกิลที่เสนอ: 100.0% · R_best ก่อนหน้า: 93.3% -> รับ (R_best ใหม่ 100.0%)
- เหตุผลของข้อเสนอ: ข้อตรวจ `tests` ตกใน 7 จาก 12 Trace ของรอบ 2 (พบ 4–5 เทสต์ ต้องมีอย่างน้อย 6) และเป็นข้อเดียวที่ตกใน t1-cafe-bill-r1/r2/r3 กับ t2-split-bill-r2 ตรงกับ pattern too-few-test-methods ผมเปิด Trace 4 ไฟล์ยืนยัน t1-cafe-bill-r1 ตก (Ran 5 tests, `test_reject` วน `subTest` 13 ชุดแต่นับเป็น 1 เมธอด), t3-shipping-fee-r3 ตก (Ran 4 tests, ค่าขอบทั้งหมดอยู่ใน `test_edges` เมธอดเดียว), t4-cashback-r3 ตก (Ran 5 tests) ส่วน t2-split-bill-r1 ผ่านเต็ม (Ran 9 tests แยกเมธอดละเรื่อง) Agent ทุกตัวอ่านและทำตามสกิล แต่สกิลไม่บอกจำนวนเมธอดขั้นต่ำ จึงเขียนหนึ่งเมธอดต่อหมวด และตอบว่าเทสต์ผ่านโดยไม่เทียบเกณฑ์ ข้อเสนอนี้เพิ่มเกณฑ์ตัวเลข (≥ 8 เมธอด) และแนวแตกเมธอดทั่วไปโดยไม่ใส่ค่าเฉพาะโจทย์ ส่วนปัญหา `policy` ตั้งใจไม่แตะ เพราะ wiki ยังไม่ยืนยันสาเหตุและเป็นกติกาเฉพาะโจทย์ ข้อเสนอนี้เป็นเรื่องใหม่ที่ต่างจากรอบ 1 (create สกิล) และไม่ซ้ำกับข้อเสนอที่ถูกปฏิเสธ

Diff ของ SKILL.md ที่เสนอ:

```diff
--- a/skills/solve-py-contract/SKILL.md
+++ b/skills/solve-py-contract/SKILL.md
@@ -86,11 +86,22 @@
     unittest.main()
 ```
 
-รัน `python3 -m unittest test_solve -v` ในโฟลเดอร์นั้นให้ผ่านทุกเทสต์ก่อนตอบ
+### ต้องมีอย่างน้อย 8 เมธอด `def test_...` แยกกัน
+
+ตัวตรวจนับจำนวนเมธอดที่ unittest รายงาน (บรรทัด `Ran N tests`) และต้องได้อย่างน้อย 6 การวน for หรือ `subTest` หรือ assert หลายตัวในเมธอดเดียวนับเป็น 1 เทสต์ ห้ามรวมทุกอย่างของหนึ่งหมวดไว้ในเมธอดเดียว (เช่น `test_edges` เมธอดเดียวที่ยัดค่าขอบทุกเกณฑ์) ให้เขียนเผื่อให้ได้ N ≥ 8 โดยแตกดังนี้:
+
+- กรณีปกติ: หนึ่งเมธอดต่อหนึ่งสถานการณ์ อย่างน้อย 3 เมธอด (เช่น ไม่มีส่วนลด, มีส่วนลดหรือเงื่อนไขพิเศษ, หลายรายการ)
+- ค่าขอบ: หนึ่งเมธอดต่อหนึ่งเกณฑ์ในโจทย์ (ต่ำกว่า พอดี สูงกว่า)
+- ปัดเศษ: หนึ่งเมธอด และอีกหนึ่งเมธอดเช็กว่าผลเป็น `int` จริงด้วย `assertIs(type(x), int)`
+- อินพุตผิด: หนึ่งเมธอดต่อหนึ่งพารามิเตอร์ ตั้งชื่อ `test_reject_<ชื่อพารามิเตอร์>` ครอบ float, bool, ค่านอกช่วง, ชนิดผิด
+
+แต่ละเมธอดต้องตรวจสิ่งที่ต่างกันจริง ไม่เขียนเมธอดเปล่าหรือซ้ำเพื่อให้ครบจำนวน และต้องคำนวณค่าที่คาดด้วยมือให้ถูกก่อนเขียน
+
+รัน `python3 -m unittest test_solve -v` ในโฟลเดอร์นั้นให้ผ่านทุกเทสต์ แล้วอ่านบรรทัด `Ran N tests` ถ้า N < 8 ให้แตกเมธอดเพิ่มแล้วรันใหม่ก่อนตอบ
 
 ## รายการตรวจก่อนตอบ
 
 - [ ] ทุกพารามิเตอร์มีการตรวจชนิดและช่วง และ float/bool/0/ติดลบ/ค่าไม่อยู่ในรายการ ได้ ValueError
 - [ ] ท้ายไฟล์มีบล็อก CLI และลองรัน stdin ทั้งกรณีสำเร็จและผิดแล้ว (exit 0 / exit 2, ไม่มี traceback)
-- [ ] มี test_solve.py และรันผ่านครบ
+- [ ] มี test_solve.py และรันผ่านครบ และบรรทัด `Ran N tests` ได้ N ≥ 8 (นับเฉพาะเมธอด `def test_...` ไม่นับ `subTest` หรือ assert ในเมธอดเดียวกัน) ถ้าไม่ถึงให้แตกเมธอดเพิ่มก่อนตอบ
 - [ ] ผลลัพธ์เป็น int จริง และคำนวณด้วยจำนวนเต็มหรือ Fraction ปัดครั้งเดียวตอนท้าย
```
