# Iteration 1

Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): 46.7%

## wiki/index.md

# Wiki Index

- [input-validation-missing](wiki/patterns/input-validation-missing.md): ฟังก์ชันไม่ตรวจ input จึงคืนค่าแทน raise `ValueError` สำหรับค่านอกช่วง/ชนิดผิด (float, bool, qty=0, people=0, ค่าติดลบ) เพราะโจทย์ไม่สั่งตรง ๆ แก้โดยตรวจชนิด (`type(x) is int`) และช่วงที่ต้นฟังก์ชันก่อน early-return แล้ว raise `ValueError` เสมอ (`reject_value`, `reject_type`)
- [cli-entrypoint-missing](wiki/patterns/cli-entrypoint-missing.md): solve.py ไม่มี `__main__` อ่าน JSON จาก stdin จึงได้ exit 0 stdout ว่าง (`cli_ok`, `cli_error`) เพราะโจทย์ไม่ได้พูดถึง CLI แก้โดยต่อท้ายไฟล์ด้วยโค้ดที่พิมพ์ `{"ok": true, "result": ...}` exit 0 หรือ `{"ok": false, "error": ...}` exit 2 ไม่มี traceback
- [test-file-missing](wiki/patterns/test-file-missing.md): ไม่มี `test_solve.py` ข้าง solve.py (ข้อ `tests` ตก) เพราะ Agent ทดสอบด้วย `python3 -c` แล้วทิ้ง แก้โดยสร้างไฟล์ test ครอบคลุมปกติ ขอบ เศษ .5 และ `ValueError` แล้วรันให้ผ่านก่อนตอบ
- [half-up-integer-rounding](wiki/patterns/half-up-integer-rounding.md): ปัดเศษสตางค์ผิดวิธี (ปัดลงด้วย `//`) ทำให้ `half_up`/`no_drift` ตก เพราะโจทย์ไม่ระบุวิธีปัดแต่ตัวตรวจคาด half-up แก้โดยใช้เลขจำนวนเต็มหรือ Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย `(2*n+d)//(2*d)` (pattern ที่ทำให้สำเร็จอยู่ในหน้านี้)
- [happy-path-only-verification](wiki/patterns/happy-path-only-verification.md): Agent ทดสอบแค่ตัวอย่างปกติรอบเดียวแล้วรายงานว่าเสร็จ (บางรายไม่รันเลย) ทำให้พลาดข้อ validation/CLI/tests/rounding ซ้ำทุก Trace แก้โดยทำรายการตรวจ 5 ข้อก่อนส่งงานและรันจริง

## wiki/skill-impact.md

# Skill Impact

บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ

## summary.md

# ผลของ Training rollouts · iteration 1

คะแนนเฉลี่ย 46.7% · ผ่านครบทุกข้อ 0/12 Trace

| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |
|---|---|---|---|
| t1-cafe-bill-r1 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t1-cafe-bill-r2 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t1-cafe-bill-r3 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r1 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r2 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r3 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t3-shipping-fee-r1 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t3-shipping-fee-r2 | FAIL | 0.60 | reject_type cli_ok cli_error tests |
| t3-shipping-fee-r3 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t4-cashback-r1 | FAIL | 0.30 | half_up no_drift reject_value reject_type cli_ok cli_error tests |
| t4-cashback-r2 | FAIL | 0.30 | half_up no_drift reject_value reject_type cli_ok cli_error tests |
| t4-cashback-r3 | FAIL | 0.40 | half_up no_drift reject_type cli_ok cli_error tests |

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
- t4-cashback-r1 · `reject_value`: cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 1 จาก 3 กรณี
- t4-cashback-r1 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 4 จาก 5 กรณี
- t4-cashback-r1 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r1 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r2 · `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- t4-cashback-r2 · `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 2 จาก 3 กรณี
- t4-cashback-r2 · `reject_value`: cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 1 จาก 3 กรณี
- t4-cashback-r2 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 4 จาก 5 กรณี
- t4-cashback-r2 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r2 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r3 · `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- t4-cashback-r3 · `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 2 จาก 3 กรณี
- t4-cashback-r3 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 4 จาก 5 กรณี
- t4-cashback-r3 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r3 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py

## Active skills

(ยังไม่มีสกิล)

สำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย