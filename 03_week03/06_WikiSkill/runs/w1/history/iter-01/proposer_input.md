# Iteration 1

Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): 43.3%

## wiki/index.md

# Wiki Index

- [missing-cli-entrypoint](wiki/patterns/missing-cli-entrypoint.md): `cli_ok`/`cli_error` ล้มเพราะ solve.py มีแต่ฟังก์ชัน ไม่อ่าน stdin JSON ไม่พิมพ์ `{"ok":...}` ให้เพิ่ม `main()` + `__main__` ที่ exit 0 เมื่อสำเร็จ และ exit 2 พร้อม JSON error เมื่อ ValueError/KeyError/TypeError
- [missing-input-validation](wiki/patterns/missing-input-validation.md): `reject_value`/`reject_type` ล้มเพราะช่วงค่าและชนิดในโจทย์ไม่ถูกบังคับ (ค่า 0/ติดลบ/float/tier ผิดผ่านเข้าไป หรือเกิด ZeroDivisionError) ให้ตรวจทุกพารามิเตอร์ก่อนคำนวณ และ raise ValueError เสมอ รวมปฏิเสธ float และ bool
- [money-rounding-half-up](wiki/patterns/money-rounding-half-up.md): `half_up`/`no_drift` ล้มเพราะใช้ floor (`//`) กับผลที่มีเศษสตางค์ (เช่น 250.5 ได้ 250) ให้คำนวณด้วยจำนวนเต็ม/Fraction เก็บเป็น num/den แล้วปัด half-up ครั้งเดียวตอนท้าย `(2*num+den)//(2*den)` (วิธีนี้ผ่านใน cafe_bill และ shipping_fee)
- [missing-test-file](wiki/patterns/missing-test-file.md): ข้อ `tests` ล้มเพราะไม่มี test_solve.py ข้าง solve.py (Agent ทดสอบด้วย `python3 -c` ที่ไม่เหลือไฟล์) ให้เขียนและรัน unittest/pytest ครอบกรณีปกติ ขอบ half-up ValueError และ CLI
- [happy-path-only-verification](wiki/patterns/happy-path-only-verification.md): Agent ตรวจงานแค่ค่าปกติที่คำนวณวนจากตรรกะของตัวเอง จบใน 2–3 คำสั่ง แล้วบอกว่าถูกต้อง ทั้งที่ล้ม 5–7 จาก 10 ข้อ ให้ไล่ checklist 5 ข้อ (ฟังก์ชัน, half-up, validation, CLI, tests) และรันจริงก่อนจบ

## wiki/skill-impact.md

# Skill Impact

บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ

## summary.md

# ผลของ Training rollouts · iteration 1

คะแนนเฉลี่ย 44.2% · ผ่านครบทุกข้อ 0/12 Trace

| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |
|---|---|---|---|
| t1-cafe-bill-r1 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t1-cafe-bill-r2 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t1-cafe-bill-r3 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r1 | FAIL | 0.40 | half_up reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r2 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r3 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t3-shipping-fee-r1 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t3-shipping-fee-r2 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t3-shipping-fee-r3 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t4-cashback-r1 | FAIL | 0.30 | half_up no_drift reject_value reject_type cli_ok cli_error tests |
| t4-cashback-r2 | FAIL | 0.30 | half_up no_drift reject_value reject_type cli_ok cli_error tests |
| t4-cashback-r3 | FAIL | 0.30 | half_up no_drift reject_value reject_type cli_ok cli_error tests |

## รายละเอียดของข้อตรวจที่ไม่ผ่าน (คาดว่าอะไร · ได้อะไร)

- t1-cafe-bill-r1 · `reject_value`: cafe_bill([{"price": 4500, "qty": 0}], false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t1-cafe-bill-r1 · `reject_type`: cafe_bill([{"price": 4500.0, "qty": 1}], false) ต้อง raise ValueError แต่คืนค่า 4815.0 · พลาด 5 จาก 5 กรณี
- t1-cafe-bill-r1 · `cli_ok`: stdin {"items": [{"price": 4500, "qty": 2}], "member": false} ต้องได้ {"ok": true, "result": 9630} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t1-cafe-bill-r1 · `cli_error`: stdin {"items": [{"price": 4500, "qty": 0}], "member": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t1-cafe-bill-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t1-cafe-bill-r2 · `reject_value`: cafe_bill([{"price": 4500, "qty": 0}], false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t1-cafe-bill-r2 · `reject_type`: cafe_bill([{"price": 4500.0, "qty": 1}], false) ต้อง raise ValueError แต่คืนค่า 4815.0 · พลาด 5 จาก 5 กรณี
- t1-cafe-bill-r2 · `cli_ok`: stdin {"items": [{"price": 4500, "qty": 2}], "member": false} ต้องได้ {"ok": true, "result": 9630} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t1-cafe-bill-r2 · `cli_error`: stdin {"items": [{"price": 4500, "qty": 0}], "member": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t1-cafe-bill-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t1-cafe-bill-r3 · `reject_value`: cafe_bill([{"price": 4500, "qty": 0}], false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t1-cafe-bill-r3 · `reject_type`: cafe_bill([{"price": 4500.0, "qty": 1}], false) ต้อง raise ValueError แต่คืนค่า 4815.0 · พลาด 5 จาก 5 กรณี
- t1-cafe-bill-r3 · `cli_ok`: stdin {"items": [{"price": 4500, "qty": 2}], "member": false} ต้องได้ {"ok": true, "result": 9630} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t1-cafe-bill-r3 · `cli_error`: stdin {"items": [{"price": 4500, "qty": 0}], "member": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t1-cafe-bill-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t2-split-bill-r1 · `half_up`: split_bill(1010, 1, 5) คาด [1061] ได้ [1060] · พลาด 3 จาก 3 กรณี
- t2-split-bill-r1 · `reject_value`: split_bill(10000, 0, 0) ต้อง raise ValueError แต่ raise ZeroDivisionError · พลาด 5 จาก 5 กรณี
- t2-split-bill-r1 · `reject_type`: split_bill(10000.0, 2, 0) ต้อง raise ValueError แต่คืนค่า [5000.0, 5000.0] · พลาด 4 จาก 4 กรณี
- t2-split-bill-r1 · `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t2-split-bill-r1 · `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t2-split-bill-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t2-split-bill-r2 · `reject_value`: split_bill(10000, 0, 0) ต้อง raise ValueError แต่ raise ZeroDivisionError · พลาด 5 จาก 5 กรณี
- t2-split-bill-r2 · `reject_type`: split_bill(10000.0, 2, 0) ต้อง raise ValueError แต่คืนค่า [5000.0, 5000.0] · พลาด 4 จาก 4 กรณี
- t2-split-bill-r2 · `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t2-split-bill-r2 · `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t2-split-bill-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t2-split-bill-r3 · `reject_value`: split_bill(10000, 0, 0) ต้อง raise ValueError แต่ raise ZeroDivisionError · พลาด 5 จาก 5 กรณี
- t2-split-bill-r3 · `reject_type`: split_bill(10000.0, 2, 0) ต้อง raise ValueError แต่คืนค่า [5000.0, 5000.0] · พลาด 4 จาก 4 กรณี
- t2-split-bill-r3 · `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t2-split-bill-r3 · `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t2-split-bill-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t3-shipping-fee-r1 · `reject_value`: shipping_fee(0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 4 จาก 4 กรณี
- t3-shipping-fee-r1 · `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 5 จาก 5 กรณี
- t3-shipping-fee-r1 · `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r1 · `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t3-shipping-fee-r2 · `reject_value`: shipping_fee(0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 4 จาก 4 กรณี
- t3-shipping-fee-r2 · `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 5 จาก 5 กรณี
- t3-shipping-fee-r2 · `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r2 · `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t3-shipping-fee-r3 · `reject_value`: shipping_fee(0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 4 จาก 4 กรณี
- t3-shipping-fee-r3 · `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 5 จาก 5 กรณี
- t3-shipping-fee-r3 · `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r3 · `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r1 · `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- t4-cashback-r1 · `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 2 จาก 3 กรณี
- t4-cashback-r1 · `reject_value`: cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t4-cashback-r1 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 5 จาก 5 กรณี
- t4-cashback-r1 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r1 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r2 · `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- t4-cashback-r2 · `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 2 จาก 3 กรณี
- t4-cashback-r2 · `reject_value`: cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t4-cashback-r2 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 5 จาก 5 กรณี
- t4-cashback-r2 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r2 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r3 · `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- t4-cashback-r3 · `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 2 จาก 3 กรณี
- t4-cashback-r3 · `reject_value`: cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t4-cashback-r3 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 5 จาก 5 กรณี
- t4-cashback-r3 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r3 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py

## Active skills

(ยังไม่มีสกิล)

สำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย