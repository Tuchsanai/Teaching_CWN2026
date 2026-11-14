# Evolution Log

## Iteration 1 · Training 46.4%

อ่าน Trace 5 งาน (ล้มทั้งหมด ไม่มีงานที่ผ่าน): t1-cafe-bill-r1, t2-split-bill-r1, t3-shipping-fee-r3, t4-cashback-r1, t4-cashback-r3 คะแนน 0.40–0.50 ไม่มีสกิลใช้งานในรอบนี้ (`./skills` ไม่มีอยู่ แม้ Trace ของ t2 ระบุว่า "อ่านสกิล: ใช่" แต่คำสั่ง `ls` exit 2) และ wiki/skill-impact.md ยังไม่มีข้อเสนอรอบก่อนให้เทียบ

พบ: (1) ทุกงานตก `reject_value`/`reject_type` เพราะไม่มีการตรวจอินพุต (t2 หลุดเป็น ZeroDivisionError) (2) ทุกงานตก `cli_ok`/`cli_error` เพราะ solve.py ไม่มี `__main__` อ่าน stdin (3) ทุกงานตก `tests` เพราะไม่มี test_solve.py (4) t3 และ t4 ตก `policy` สาเหตุยังไม่ยืนยัน (ระยะ 0 คาด 0 ได้ 8000; cashback silver เดือนเกิดคาด 300 ได้ 600) (5) ข้อที่ผ่านคือ `contract`/`basic`/`no_drift`/`boundary`/`half_up` เพราะใช้จำนวนเต็มหรือ Fraction แล้วปัดครั้งเดียวตอนท้าย (6) Agent ทดสอบแค่กรณีปกติ และ t2 ไม่ได้รันโค้ดเลย

สิ่งที่ยังเปิดอยู่: สาเหตุของ `policy` ที่ตกใน shipping_fee และ cashback; ยังไม่ทราบว่าตัวตรวจ `reject_type` นับ bool เป็นชนิดผิดหรือไม่; ยังไม่ทราบเกณฑ์ขั้นต่ำของข้อ `tests`

แก้ wiki: สร้าง 6 หน้า ได้แก่ missing-input-validation, missing-cli-entrypoint, missing-test-file, shallow-self-check, policy-ambiguous-edge-cases, integer-money-arithmetic และเขียนสารบัญใหม่ทั้งไฟล์

## Iteration 2 · Training 89.5%

อ่าน Trace 7 งาน (ล้ม 5: t4-cashback-r3 0.80, t3-shipping-fee-r3 0.82, t1-cafe-bill-r3 0.90, t2-split-bill-r2 0.90, t4-cashback-r1 0.90; ผ่าน 2: t2-split-bill-r3, t2-split-bill-r1) คะแนน Training รอบนี้ 89.5% ทุก Trace อ่านสกิล solve-py-contract ก่อนเริ่มงานและทำตาม

ผลของข้อเสนอรอบก่อน (สกิล solve-py-contract ที่รับในรอบ 1 ตาม skill-impact): ได้ผลกับสามปัญหาเดิม `reject_value`/`reject_type` (missing-input-validation) และ `cli_ok`/`cli_error` (missing-cli-entrypoint) ผ่านครบทั้ง 7 Trace ส่วน missing-test-file แก้ได้เฉพาะส่วนไม่มีไฟล์ (ทุกงานมี test_solve.py) แต่ข้อ `tests` ยังตกใน 4 จาก 7 งาน

พบใหม่: (1) `tests` ตกด้วย `unittest พบ N เทสต์ (ต้องมีอย่างน้อย 6)` ที่ N = 4 หรือ 5 ตัวเลขตรงกับ `Ran N tests` ที่ Agent เห็นเอง subTest นับเป็นเมธอดเดียว งานที่ผ่านมี 6, 7, 9 เมธอด และคู่เทียบ t2-split-bill-r2 (4 เมธอด ตก) กับ t2-split-bill-r3 (7 เมธอด ผ่าน) ต่างกันที่การแตกเมธอดเท่านั้น สาเหตุคือสกิลไม่บอกเกณฑ์จำนวน ไม่ใช่ Agent ไม่ทำตามสกิล สร้างหน้า too-few-test-methods (ถ้าแก้ได้ t1-cafe-bill-r3 และ t2-split-bill-r2 จะได้ 10 จาก 10 ตามการคาดการณ์) (2) ข้อ `policy` ยังตกใน t3 และ t4 ทุกงาน t3 ได้ผลเท่ารอบ 1 (4 จาก 6) t4 ตก 6 จาก 6 จากเดิม 3 จาก 6 เมื่อเปลี่ยนจากปัดลงเป็นปัดครึ่งขึ้น เป็นเบาะแสเรื่องทิศทางการปัดที่ยังไม่ยืนยัน และเคสตัวอย่าง 300 เทียบ 600 ไม่เกี่ยวกับการปัดจึงยังไม่มีสมมติฐานที่อธิบายครบ (3) Agent เรียกเครื่องมือ `bash` ตัวพิมพ์เล็กใน t3-shipping-fee-r3 และ t4-cashback-r1 ได้ error แล้วเรียกซ้ำด้วย `Bash` ไม่กระทบคะแนน

สิ่งที่ยังเปิดอยู่: สาเหตุของ `policy` (ระยะ 0 ในค่าส่ง และ silver เดือนเกิดใน cashback) ยังไม่เห็นข้อความตัวตรวจครบทุกกรณี; ตัวตรวจ `tests` ดูแค่จำนวนหรือดูความครอบคลุมด้วย; ตัวตรวจนับ bool เป็นชนิดผิดหรือไม่ (ทุกงานปฏิเสธ bool และผ่านอยู่แล้ว)

แก้ wiki: สร้าง too-few-test-methods; อัปเดต missing-input-validation และ missing-cli-entrypoint เป็นแก้ได้แล้ว, missing-test-file (ส่วนไม่มีไฟล์แก้ได้แล้ว ชี้ไปหน้าใหม่), shallow-self-check (สถานะรอบ 2), policy-ambiguous-edge-cases (หลักฐานรอบ 2 และเบาะแสเรื่องการปัด), integer-money-arithmetic (ยังได้ผล พร้อมข้อควรระวังเรื่องทิศทางการปัด); เขียนสารบัญใหม่ทั้งไฟล์
