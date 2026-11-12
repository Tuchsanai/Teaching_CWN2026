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
