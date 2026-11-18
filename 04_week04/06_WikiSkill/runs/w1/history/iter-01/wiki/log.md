# Evolution Log

## Iteration 1 · Training 46.4%

อ่าน Trace 5 งาน (ล้มทั้งหมด ไม่มีงานที่ผ่าน): t1-cafe-bill-r1, t2-split-bill-r1, t3-shipping-fee-r3, t4-cashback-r1, t4-cashback-r3 คะแนน 0.40–0.50 ไม่มีสกิลใช้งานในรอบนี้ (`./skills` ไม่มีอยู่ แม้ Trace ของ t2 ระบุว่า "อ่านสกิล: ใช่" แต่คำสั่ง `ls` exit 2) และ wiki/skill-impact.md ยังไม่มีข้อเสนอรอบก่อนให้เทียบ

พบ: (1) ทุกงานตก `reject_value`/`reject_type` เพราะไม่มีการตรวจอินพุต (t2 หลุดเป็น ZeroDivisionError) (2) ทุกงานตก `cli_ok`/`cli_error` เพราะ solve.py ไม่มี `__main__` อ่าน stdin (3) ทุกงานตก `tests` เพราะไม่มี test_solve.py (4) t3 และ t4 ตก `policy` สาเหตุยังไม่ยืนยัน (ระยะ 0 คาด 0 ได้ 8000; cashback silver เดือนเกิดคาด 300 ได้ 600) (5) ข้อที่ผ่านคือ `contract`/`basic`/`no_drift`/`boundary`/`half_up` เพราะใช้จำนวนเต็มหรือ Fraction แล้วปัดครั้งเดียวตอนท้าย (6) Agent ทดสอบแค่กรณีปกติ และ t2 ไม่ได้รันโค้ดเลย

สิ่งที่ยังเปิดอยู่: สาเหตุของ `policy` ที่ตกใน shipping_fee และ cashback; ยังไม่ทราบว่าตัวตรวจ `reject_type` นับ bool เป็นชนิดผิดหรือไม่; ยังไม่ทราบเกณฑ์ขั้นต่ำของข้อ `tests`

แก้ wiki: สร้าง 6 หน้า ได้แก่ missing-input-validation, missing-cli-entrypoint, missing-test-file, shallow-self-check, policy-ambiguous-edge-cases, integer-money-arithmetic และเขียนสารบัญใหม่ทั้งไฟล์
