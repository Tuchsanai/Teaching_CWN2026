# PURPOSE: cafe_solve_contract

## Origin
Iteration 1: ยังไม่มีสกิล Agent ทั้ง 12 Trace (t1–t4) ได้ 0.40–0.60 ไม่ผ่านครบสักงาน เพราะพลาดข้อที่โจทย์ไม่ได้เขียนไว้ตรง ๆ: CLI stdin JSON, ไฟล์ test_solve.py, validate ชนิด, ปัดเศษ half up ครั้งเดียว

## Patterns Addressed
- wiki/patterns/hidden-cli-contract-stdin-json.md (cli_ok, cli_error)
- wiki/patterns/missing-test-solve-py.md (tests)
- wiki/patterns/reject-non-int-inputs-as-valueerror.md (reject_type)
- wiki/patterns/validate-spec-ranges-with-valueerror.md (reject_value)
- wiki/patterns/floor-instead-of-half-up.md (half_up)
- wiki/patterns/intermediate-rounding-drift.md (no_drift)
- wiki/patterns/self-check-confirms-own-assumptions.md (เช็กลิสต์ก่อนจบ)

## Evolution History
- v1 (iteration 1): สร้างสกิลรวมเป็นแม่แบบโค้ดและเช็กลิสต์เดียว
