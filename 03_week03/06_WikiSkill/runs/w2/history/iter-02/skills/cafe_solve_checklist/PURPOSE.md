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

iter 2: แก้ pattern wiki/patterns/test-count-below-minimum.md (ข้อ tests ล้ม 21/24 trace ได้ 0.90 เพราะ test_solve.py มี method test_* เพียง 3–5 ตัว ต้อง ≥ 6) จึงระบุขั้นต่ำ 8 method แยกหมวด ขยายโครงตัวอย่างเป็น 8 method และบังคับดู `Ran N tests` ก่อนจบ ส่วน wiki/patterns/missing-test-file.md และ happy-path-only-self-check.md ยังเกี่ยวข้องในฐานะเรื่องไฟล์เทสต์และการเทียบผลกับเกณฑ์
