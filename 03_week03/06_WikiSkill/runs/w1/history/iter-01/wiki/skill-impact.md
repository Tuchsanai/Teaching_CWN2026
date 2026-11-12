# Skill Impact

บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ

## Iteration 1 · create `baankafe_solve_checklist` · ACCEPTED

- Validation ของสกิลที่เสนอ: 100.0% · R_best ก่อนหน้า: 43.3% -> รับ (R_best ใหม่ 100.0%)
- เหตุผลของข้อเสนอ: ทุก Trace ใน iteration 1 ไม่มีสกิล และล้มข้อ cli/validation/tests เหมือนกันหมด และ half_up ในงานที่ใช้ floor จึงสร้างสกิล checklist เดียวพร้อมโค้ดแม่แบบ

Diff ของ SKILL.md ที่เสนอ:

```diff
--- a/skills/baankafe_solve_checklist/SKILL.md
+++ b/skills/baankafe_solve_checklist/SKILL.md
@@ -0,0 +1,69 @@
+---
+name: baankafe_solve_checklist
+description: ขั้นตอนบังคับเมื่อเขียน solve.py คิดเงินของร้านกาแฟ BaanKafe (ฟังก์ชันเงินสตางค์ + validation + CLI + test_solve.py) เพื่อให้ผ่านตัวตรวจทั้ง 10 ข้อ
+---
+
+# BaanKafe solve.py checklist
+
+## When to Apply
+- โจทย์ให้เขียนฟังก์ชันคิดเงิน/ค่าส่ง/หารบิล/เงินคืน ในไฟล์ `solve.py` (หน่วยเงินเป็นสตางค์ จำนวนเต็ม)
+
+## When NOT to Apply
+- งานที่ไม่เกี่ยวกับ `solve.py` หรือไม่เกี่ยวกับเงินสตางค์
+
+## Instructions
+ตัวตรวจทดสอบ 10 ข้อ: contract, basic, half_up, no_drift, boundary, reject_value, reject_type, cli_ok, cli_error, tests โจทย์จะไม่บอกข้อตกลงเหล่านี้ ต้องทำให้ครบทุกครั้ง แม้โจทย์ไม่ได้สั่ง
+
+### 1. ปัดเศษ half-up (โจทย์ไม่ระบุ = ให้ใช้ half-up ห้ามเลือกปัดลง)
+- ห้าม float และห้าม `//` กับค่าที่มีเศษ คำนวณด้วยจำนวนเต็มหรือ `Fraction`
+- เก็บผลเป็น `num/den` คูณต่อกันทุกขั้น (ส่วนลด, VAT, ทิป, อัตรา, ตัวคูณ) แล้วปัด **ครั้งเดียวตอนท้าย**: `(2*num + den) // (2*den)`
+- ถ้ามีเพดาน (min/cap) ให้เทียบหลังปัดได้ แต่ห้ามปัดกลางทางก่อนคูณขั้นถัดไป
+- กรณีแจกเศษหาร (หารเท่า ๆ กัน): ปัดยอดรวมก่อน แล้ว `divmod(grand, n)` แจกคนแรก ๆ คนละ 1
+
+### 2. Validation (raise ValueError เสมอ ตรวจก่อนคำนวณและก่อนหารทุกครั้ง)
+```python
+def _int(x, name, lo=None, hi=None):
+    if isinstance(x, bool) or not isinstance(x, int):
+        raise ValueError(f'{name} must be int')
+    if (lo is not None and x < lo) or (hi is not None and x > hi):
+        raise ValueError(f'{name} out of range')
+    return x
+
+def _bool(x, name):
+    if not isinstance(x, bool):
+        raise ValueError(f'{name} must be bool')
+    return x
+```
+- ทุกพารามิเตอร์ตัวเลขต้องผ่าน `_int` (ปฏิเสธ float เช่น `100.0`, str, None, bool) และกำหนด lo/hi ตามช่วงที่โจทย์เขียน ("ตั้งแต่ 1", "0–100", "1–30,000", "ตั้งแต่ 0")
+- enum (เช่น tier) ตรวจ `isinstance(x, str) and x in TABLE` ไม่เช่นนั้น ValueError (ห้ามปล่อย KeyError)
+- flag (bool) ตรวจด้วย `_bool`
+- list/dict: ตรวจว่าเป็น list, แต่ละตัวเป็น dict, มี key ครบ, แล้วตรวจแต่ละค่าด้วย `_int` ห้ามให้ KeyError/TypeError/ZeroDivisionError หลุด
+- ค่า 0 หรือค่าติดลบที่นอกช่วงต้องถูกปฏิเสธ ห้ามคืน 0
+
+### 3. CLI ต่อท้าย solve.py (ตัวตรวจรัน `python3 solve.py` ส่ง JSON ทาง stdin key = ชื่อพารามิเตอร์)
+```python
+import json, sys
+
+def main():
+    try:
+        data = json.loads(sys.stdin.read())
+        result = FUNC(data['p1'], data['p2'])  # แทนด้วยชื่อฟังก์ชัน/พารามิเตอร์จริงทุกตัว
+    except (ValueError, KeyError, TypeError) as e:
+        print(json.dumps({'ok': False, 'error': str(e)}))
+        return 2
+    print(json.dumps({'ok': True, 'result': result}))
+    return 0
+
+if __name__ == '__main__':
+    sys.exit(main())
+```
+- สำเร็จ: stdout `{"ok": true, "result": ...}` exit 0 · ผิด: `{"ok": false, "error": "..."}` exit 2 ไม่มี traceback
+
+### 4. เขียน test_solve.py ไว้ข้าง solve.py (ต้องเหลือเป็นไฟล์จริง ห้ามใช้ `python3 -c` อย่างเดียว)
+- `unittest` ครอบ: ค่าปกติ, ขอบของทุกเงื่อนไข (พอดี/ต่ำกว่า/สูงกว่า), เศษลงที่ .5 พอดีและ .6 (ยืนยัน half-up), ValueError (นอกช่วง, float, bool, enum ผิด, ศูนย์ที่ใช้หาร), และ CLI ผ่าน `subprocess.run([sys.executable, 'solve.py'], input=..., capture_output=True, text=True)` ทั้ง ok (exit 0) และ error (exit 2)
+
+### 5. รันตรวจจริงก่อนจบ
+- `python3 -m unittest -v test_solve` ต้องผ่านทั้งหมด
+- `echo '{...ปกติ...}' | python3 solve.py; echo $?` ต้องได้ `{"ok": true...}` และ 0
+- `echo '{...ค่าผิด...}' | python3 solve.py; echo $?` ต้องได้ `{"ok": false...}` และ 2
+- หากข้อใดล้ม แก้แล้วรันซ้ำ ห้ามบอกว่าถูกต้องโดยไม่ได้รันทั้งสามข้อ
```
