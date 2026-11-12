# Iteration 1

Validation score ที่ดีที่สุดจนถึงตอนนี้ (R_best): 50.0%

## wiki/index.md

# Wiki Index

- [floor-instead-of-half-up](wiki/patterns/floor-instead-of-half-up.md): ผลลัพธ์สตางค์ต่ำไป 1 (ข้อ half_up) เพราะ Agent ปัดด้วย `//` (floor) ตามที่โจทย์ไม่ได้บอก ให้ใช้ half up `(2*n + d)//(2*d)` เสมอ ห้ามใช้ `round()`
- [intermediate-rounding-drift](wiki/patterns/intermediate-rounding-drift.md): ผลเพี้ยน 1 สตางค์ (ข้อ no_drift) เพราะปัดเศษทุกขั้นหรือปัดก่อนคูณ 2 ให้ใช้ `Fraction` หรือจำนวนเต็มที่ยังไม่หาร แล้วปัดครั้งเดียวตอนท้าย (ก่อนเทียบเพดาน)
- [reject-non-int-inputs-as-valueerror](wiki/patterns/reject-non-int-inputs-as-valueerror.md): ข้อ reject_type พลาดเพราะฟังก์ชันรับ float/bool/str แล้วคำนวณต่อ หรือ raise TypeError ให้ validate ทุกพารามิเตอร์ (int จริงที่ไม่ใช่ bool, flag เป็น bool, tier เป็น str ในชุดที่กำหนด) แล้ว raise ValueError อย่างเดียว
- [validate-spec-ranges-with-valueerror](wiki/patterns/validate-spec-ranges-with-valueerror.md): ข้อ reject_value พลาดเพราะไม่ตรวจช่วงที่โจทย์เขียนไว้ เช่น qty ตั้งแต่ 1 คืน 0 แทน raise ให้ไล่ทุกพารามิเตอร์รวมสมาชิกใน list แล้ว raise ValueError ให้ตรงขอบเขต
- [hidden-cli-contract-stdin-json](wiki/patterns/hidden-cli-contract-stdin-json.md): ข้อ cli_ok/cli_error พลาดทั้ง 5 trace เพราะโจทย์ไม่พูดถึง CLI แต่ตัวตรวจรัน `python solve.py` ส่ง JSON ทาง stdin ให้เขียน main() พิมพ์ `{"ok":true,"result":...}` exit 0 หรือ `{"ok":false,"error":...}` exit 2 และไม่มี demo print
- [missing-test-solve-py](wiki/patterns/missing-test-solve-py.md): ข้อ tests พลาดทุก trace เพราะ Agent ทดสอบด้วย `python3 -c` แล้วไม่เหลือไฟล์ ให้สร้าง test_solve.py ข้าง solve.py (unittest/pytest) แล้วรัน `python3 -m unittest` จากโฟลเดอร์งาน ไม่ใช้ `python3 -I`
- [self-check-confirms-own-assumptions](wiki/patterns/self-check-confirms-own-assumptions.md): Agent ทดสอบเองผ่านหมดแต่ได้ 0.4–0.6 เพราะค่าคาดมาจากสมมติฐานเดียวกับโค้ด ให้ไล่เช็กลิสต์ตามข้อตัวตรวจ (เศษ .5, หลายขั้นตอน, ชนิดผิด, qty=0, CLI, test file) ก่อนจบ

## wiki/skill-impact.md

# Skill Impact

บันทึกโดยโปรแกรมหลัง Validation ทุกรอบ: เสนออะไร · คะแนนเท่าไร · รับหรือไม่รับ

## summary.md

# ผลของ Training rollouts · iteration 1

คะแนนเฉลี่ย 50.8% · ผ่านครบทุกข้อ 0/12 Trace

| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |
|---|---|---|---|
| t1-cafe-bill-r1 | FAIL | 0.60 | reject_type cli_ok cli_error tests |
| t1-cafe-bill-r2 | FAIL | 0.40 | no_drift reject_value reject_type cli_ok cli_error tests |
| t1-cafe-bill-r3 | FAIL | 0.50 | no_drift reject_type cli_ok cli_error tests |
| t2-split-bill-r1 | FAIL | 0.50 | half_up reject_type cli_ok cli_error tests |
| t2-split-bill-r2 | FAIL | 0.60 | reject_type cli_ok cli_error tests |
| t2-split-bill-r3 | FAIL | 0.50 | half_up reject_type cli_ok cli_error tests |
| t3-shipping-fee-r1 | FAIL | 0.60 | reject_type cli_ok cli_error tests |
| t3-shipping-fee-r2 | FAIL | 0.60 | reject_type cli_ok cli_error tests |
| t3-shipping-fee-r3 | FAIL | 0.60 | reject_type cli_ok cli_error tests |
| t4-cashback-r1 | FAIL | 0.40 | half_up no_drift reject_type cli_ok cli_error tests |
| t4-cashback-r2 | FAIL | 0.40 | half_up no_drift reject_type cli_ok cli_error tests |
| t4-cashback-r3 | FAIL | 0.40 | half_up no_drift reject_type cli_ok cli_error tests |

## รายละเอียดของข้อตรวจที่ไม่ผ่าน (คาดว่าอะไร · ได้อะไร)

- t1-cafe-bill-r1 · `reject_type`: cafe_bill([{"price": 4500.0, "qty": 1}], false) ต้อง raise ValueError แต่คืนค่า 4815 · พลาด 5 จาก 5 กรณี
- t1-cafe-bill-r1 · `cli_ok`: stdin {"items": [{"price": 4500, "qty": 2}], "member": false} ต้องได้ {"ok": true, "result": 9630} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t1-cafe-bill-r1 · `cli_error`: stdin {"items": [{"price": 4500, "qty": 0}], "member": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t1-cafe-bill-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t1-cafe-bill-r2 · `no_drift`: cafe_bill([{"price": 4505, "qty": 1}], true) คาด 4338 ได้ 4339 · พลาด 3 จาก 3 กรณี
- t1-cafe-bill-r2 · `reject_value`: cafe_bill([{"price": 4500, "qty": 0}], false) ต้อง raise ValueError แต่คืนค่า 0 · พลาด 3 จาก 3 กรณี
- t1-cafe-bill-r2 · `reject_type`: cafe_bill([{"price": 4500.0, "qty": 1}], false) ต้อง raise ValueError แต่คืนค่า 4815 · พลาด 5 จาก 5 กรณี
- t1-cafe-bill-r2 · `cli_ok`: stdin {"items": [{"price": 4500, "qty": 2}], "member": false} ต้องได้ {"ok": true, "result": 9630} exit 0 แต่ได้ exit 0 stdout 47572
- t1-cafe-bill-r2 · `cli_error`: stdin {"items": [{"price": 4500, "qty": 0}], "member": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout 47572
- t1-cafe-bill-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t1-cafe-bill-r3 · `no_drift`: cafe_bill([{"price": 4505, "qty": 1}], true) คาด 4338 ได้ 4339 · พลาด 3 จาก 3 กรณี
- t1-cafe-bill-r3 · `reject_type`: cafe_bill([{"price": 4500.0, "qty": 1}], false) ต้อง raise ValueError แต่คืนค่า 4815 · พลาด 5 จาก 5 กรณี
- t1-cafe-bill-r3 · `cli_ok`: stdin {"items": [{"price": 4500, "qty": 2}], "member": false} ต้องได้ {"ok": true, "result": 9630} exit 0 แต่ได้ exit 0 stdout ไม่ใช่สมาชิก: 64040
สมาชิก: 57636
- t1-cafe-bill-r3 · `cli_error`: stdin {"items": [{"price": 4500, "qty": 0}], "member": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout ไม่ใช่สมาชิก: 64040
สมาชิก: 57636
- t1-cafe-bill-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t2-split-bill-r1 · `half_up`: split_bill(1010, 1, 5) คาด [1061] ได้ [1060] · พลาด 3 จาก 3 กรณี
- t2-split-bill-r1 · `reject_type`: split_bill(10000.0, 2, 0) ต้อง raise ValueError แต่คืนค่า [5000.0, 5000.0] · พลาด 4 จาก 4 กรณี
- t2-split-bill-r1 · `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout [3667, 3667, 3666]
[0, 0, 0, 0]
[1998]
- t2-split-bill-r1 · `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout [3667, 3667, 3666]
[0, 0, 0, 0]
[1998]
- t2-split-bill-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t2-split-bill-r2 · `reject_type`: split_bill(10000, true, 0) ต้อง raise ValueError แต่คืนค่า [10000] · พลาด 1 จาก 4 กรณี
- t2-split-bill-r2 · `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout [3667, 3667, 3666]
- t2-split-bill-r2 · `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout [3667, 3667, 3666]
- t2-split-bill-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t2-split-bill-r3 · `half_up`: split_bill(1010, 1, 5) คาด [1061] ได้ [1060] · พลาด 3 จาก 3 กรณี
- t2-split-bill-r3 · `reject_type`: split_bill(10000.0, 2, 0) ต้อง raise ValueError แต่คืนค่า [5000.0, 5000.0] · พลาด 4 จาก 4 กรณี
- t2-split-bill-r3 · `cli_ok`: stdin {"total": 10000, "people": 3, "tip_percent": 0} ต้องได้ {"ok": true, "result": [3334, 3333, 3333]} exit 0 แต่ได้ exit 0 stdout [3667, 3667, 3666]
[0, 0, 0, 0]
- t2-split-bill-r3 · `cli_error`: stdin {"total": 10000, "people": 0, "tip_percent": 0} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout [3667, 3667, 3666]
[0, 0, 0, 0]
- t2-split-bill-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t3-shipping-fee-r1 · `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่ raise TypeError · พลาด 5 จาก 5 กรณี
- t3-shipping-fee-r1 · `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout 4000
12000
13200
19800
- t3-shipping-fee-r1 · `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout 4000
12000
13200
19800
- t3-shipping-fee-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t3-shipping-fee-r2 · `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 5 จาก 5 กรณี
- t3-shipping-fee-r2 · `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r2 · `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t3-shipping-fee-r3 · `reject_type`: shipping_fee(1000.0, 10, false) ต้อง raise ValueError แต่คืนค่า 4000 · พลาด 3 จาก 5 กรณี
- t3-shipping-fee-r3 · `cli_ok`: stdin {"weight_g": 3000, "distance_km": 150, "express": false} ต้องได้ {"ok": true, "result": 9600} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r3 · `cli_error`: stdin {"weight_g": 0, "distance_km": 10, "express": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t3-shipping-fee-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r1 · `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- t4-cashback-r1 · `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 3 จาก 3 กรณี
- t4-cashback-r1 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่ raise TypeError · พลาด 4 จาก 5 กรณี
- t4-cashback-r1 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout 0
150
300
20000
20000
0
250
- t4-cashback-r1 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout 0
150
300
20000
20000
0
250
- t4-cashback-r1 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r2 · `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- t4-cashback-r2 · `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 3 จาก 3 กรณี
- t4-cashback-r2 · `reject_type`: cashback(20000.0, "gold", false) ต้อง raise ValueError แต่ raise TypeError · พลาด 4 จาก 5 กรณี
- t4-cashback-r2 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r2 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout (ว่าง)
- t4-cashback-r2 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py
- t4-cashback-r3 · `half_up`: cashback(10020, "gold", false) คาด 251 ได้ 250 · พลาด 3 จาก 3 กรณี
- t4-cashback-r3 · `no_drift`: cashback(10020, "silver", true) คาด 301 ได้ 300 · พลาด 2 จาก 3 กรณี
- t4-cashback-r3 · `reject_type`: cashback(20000, "gold", "yes") ต้อง raise ValueError แต่คืนค่า 1000 · พลาด 1 จาก 5 กรณี
- t4-cashback-r3 · `cli_ok`: stdin {"amount": 20000, "tier": "gold", "birthday": false} ต้องได้ {"ok": true, "result": 500} exit 0 แต่ได้ exit 0 stdout OK  cashback(9999, 'platinum', False) = 0 (expected 0)
OK  cashback(10000, 'silver', False) = 150 (expected 150)
OK  cas
- t4-cashback-r3 · `cli_error`: stdin {"amount": 20000, "tier": "bronze", "birthday": false} ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit 0 stdout OK  cashback(9999, 'platinum', False) = 0 (expected 0)
OK  cashback(10000, 'silver', False) = 150 (e
- t4-cashback-r3 · `tests`: ไม่มีไฟล์ test_solve.py ข้าง solve.py

## Active skills

(ยังไม่มีสกิล)

สำรวจด้วยเครื่องมือ Read แล้วตอบข้อเสนอเป็น JSON object ในข้อความสุดท้าย