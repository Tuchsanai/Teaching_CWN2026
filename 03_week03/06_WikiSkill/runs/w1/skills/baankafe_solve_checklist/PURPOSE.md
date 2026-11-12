# PURPOSE

## Origin
สร้างใน iteration 1 จากการที่ Agent ไม่มีสกิล เขียนแต่ฟังก์ชันแล้วจบใน 2–3 คำสั่ง ทุก Trace (12/12) ล้ม 5–8 จาก 10 ข้อ คะแนนเฉลี่ย 44.2% ดูได้จาก t1-cafe-bill-r1, t2-split-bill-r1, t3-shipping-fee-r1, t4-cashback-r1

## Patterns Addressed
- wiki/patterns/missing-cli-entrypoint.md (cli_ok, cli_error)
- wiki/patterns/missing-input-validation.md (reject_value, reject_type)
- wiki/patterns/money-rounding-half-up.md (half_up, no_drift)
- wiki/patterns/missing-test-file.md (tests)
- wiki/patterns/happy-path-only-verification.md (ตรวจจริงก่อนจบ)

## Evolution History
- iter 1: สร้างสกิลแรก รวม checklist 5 ข้อไว้ในสกิลเดียว
