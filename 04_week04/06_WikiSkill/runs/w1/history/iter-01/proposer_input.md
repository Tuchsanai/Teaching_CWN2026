# Iteration 1

Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): 45.0%

## wiki/index.md

# Wiki Index

- [missing-input-validation](wiki/patterns/missing-input-validation.md): ยังเกิดอยู่ (ตกทุกโจทย์ `reject_value`/`reject_type`) ค่านอกช่วง ชนิดผิด หรือ float ไม่ถูก raise ValueError (people=0 ได้ ZeroDivisionError) เพราะโค้ดเป็นสูตรคำนวณล้วนและโจทย์ไม่ได้บอกตรง ๆ ให้ตรวจอินพุต ให้ตรวจช่วง ชนิดแบบ `type(x) is int` และค่าที่อนุญาตไว้ต้นฟังก์ชัน แล้ว raise ValueError ก่อนคำนวณ
- [missing-cli-entrypoint](wiki/patterns/missing-cli-entrypoint.md): ยังเกิดอยู่ (ตกทุกโจทย์ `cli_ok`/`cli_error`) รัน solve.py ด้วย stdin แล้วได้ exit 0 และ stdout ว่าง เพราะไฟล์มีแต่ฟังก์ชัน ไม่มี `__main__` ให้อ่าน JSON จาก stdin เรียก `fn(**data)` พิมพ์ `{"ok":true,"result":...}` exit 0 หรือ `{"ok":false,"error":...}` exit 2 โดยไม่มี traceback
- [missing-test-file](wiki/patterns/missing-test-file.md): ยังเกิดอยู่ (ตกทุกโจทย์ `tests`) ไม่มี test_solve.py ข้าง solve.py เพราะ Agent ทดสอบด้วย `python3 -c` ทิ้งและโจทย์ไม่ได้สั่ง ให้สร้าง test_solve.py แบบ unittest ครอบคลุมกรณีปกติ ขอบ การปัดเศษ และอินพุตผิด แล้วรันให้ผ่านก่อนตอบ
- [shallow-self-check](wiki/patterns/shallow-self-check.md): ยังเกิดอยู่ Agent สรุปว่าถูกต้องทั้งที่ตกหลายข้อ เพราะทดสอบแต่กรณีปกติ 3–5 ตัว (t2 ไม่ได้รันเลย) และไม่มีสกิลใช้งานในรอบนี้ (`./skills` ไม่มีอยู่) ให้ทำรายการตรวจก่อนตอบ: ขอบ อินพุตผิด stdin test_solve.py และทบทวนโจทย์ทีละข้อ แล้วรันจริงทุกข้อ
- [policy-ambiguous-edge-cases](wiki/patterns/policy-ambiguous-edge-cases.md): ยังไม่ยืนยันสาเหตุ `policy` ตกใน shipping_fee (ระยะ 0 คาด 0 ได้ 8000) และ cashback (silver เดือนเกิด 20000 คาด 300 ได้ 600) เพราะ Agent ตีความกติกาที่ไม่ชัดตามตัวอักษรโดยไม่บันทึกข้อสมมติ ให้หาเคสที่เงื่อนไขชนกันหรือค่าขอบก่อนเขียน จดข้อสมมติเป็นเทสต์ และรอบหน้าดูข้อความตัวตรวจทุกกรณีที่พลาดเพื่อยืนยัน
- [integer-money-arithmetic](wiki/patterns/integer-money-arithmetic.md): แก้ได้แล้ว/ใช้ได้ผล (ผ่าน `basic`/`no_drift`/`boundary`/`half_up` ทุกโจทย์) ปัญหาทศนิยมและการปัดซ้อนหลายรอบหายไป เพราะ Agent คิดด้วยจำนวนเต็มหรือ Fraction และปัดครั้งเดียวตอนท้าย ให้คงแนวทางนี้ไว้ในสกิล และคืนผลเป็น int จริง

## wiki/skill-impact.md

# Skill Impact

บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ

## summary.md

# ผลของ Training rollouts · iteration 1

คะแนนเฉลี่ย 46.4% · ผ่านครบทุกข้อ 0/12 Trace

| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |
|---|---|---|---|
| t1-cafe-bill-r1 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t1-cafe-bill-r2 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t1-cafe-bill-r3 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r1 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r2 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t2-split-bill-r3 | FAIL | 0.50 | reject_value reject_type cli_ok cli_error tests |
| t3-shipping-fee-r1 | FAIL | 0.45 | reject_value reject_type cli_ok cli_error tests policy |
| t3-shipping-fee-r2 | FAIL | 0.45 | reject_value reject_type cli_ok cli_error tests policy |
| t3-shipping-fee-r3 | FAIL | 0.45 | reject_value reject_type cli_ok cli_error tests policy |
| t4-cashback-r1 | FAIL | 0.40 | reject_value reject_type cli_ok cli_error tests policy |
| t4-cashback-r2 | FAIL | 0.40 | reject_value reject_type cli_ok cli_error tests policy |
| t4-cashback-r3 | FAIL | 0.40 | reject_value reject_type cli_ok cli_error tests policy |

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
- t3-shipping-fee-r1 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t3-shipping-fee-r2 · `reject_value`: shipping_fee(0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 4 จาก 4 กรณี
- t3-shipping-fee-r2 · `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 5 จาก 5 กรณี
- t3-shipping-fee-r2 · `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r2 · `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t3-shipping-fee-r2 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t3-shipping-fee-r3 · `reject_value`: shipping_fee(0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 4 จาก 4 กรณี
- t3-shipping-fee-r3 · `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 5 จาก 5 กรณี
- t3-shipping-fee-r3 · `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r3 · `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t3-shipping-fee-r3 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t4-cashback-r1 · `reject_value`: cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t4-cashback-r1 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 5 จาก 5 กรณี
- t4-cashback-r1 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r1 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r1 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 3 จาก 6 กรณี
- t4-cashback-r2 · `reject_value`: cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 1 จาก 3 กรณี
- t4-cashback-r2 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 4 จาก 5 กรณี
- t4-cashback-r2 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r2 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r2 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 3 จาก 6 กรณี
- t4-cashback-r3 · `reject_value`: cashback(-1, "gold", false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t4-cashback-r3 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่คืนค่า 500.0 · พลาด 5 จาก 5 กรณี
- t4-cashback-r3 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r3 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r3 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 3 จาก 6 กรณี

## Active skills

(ยังไม่มีสกิล)

สำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย