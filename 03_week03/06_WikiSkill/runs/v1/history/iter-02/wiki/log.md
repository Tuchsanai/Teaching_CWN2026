# Evolution Log

## Iteration 1 · Training 46.7%

- รอบนี้ไม่มีสกิล (`./skills` ไม่มี) และ skill-impact.md ยังว่าง จึงยังไม่มีผลรอบก่อนให้เทียบ
- ทุก Trace ผ่านเฉพาะ `contract` `basic` `boundary` (บางข้อ `half_up` `no_drift`) ส่วนที่ตกซ้ำทุก Trace คือ 4 เรื่องที่โจทย์ไม่ได้บอกแต่ตัวตรวจคาดหวัง: ตรวจ input แล้ว raise `ValueError`, CLI stdin/stdout JSON, ไฟล์ `test_solve.py`, ปัดเศษ half-up
- Trace ที่ผ่าน half_up/no_drift (t1, t2, t3) ใช้เลขจำนวนเต็มหรือ Fraction ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ส่วน t4 ทั้งสอง Trace ปัดลงด้วย `//` จึงตก
- t2 ไม่ได้รันทดสอบเลย และได้ ZeroDivisionError แทน ValueError
- สร้างหน้าใหม่ 5 หน้า: input-validation-missing, cli-entrypoint-missing, test-file-missing, half-up-integer-rounding, happy-path-only-verification และอัปเดต index

## Iteration 2 · Training 95.0%

- ผลของสกิลรอบก่อน: `cafe_function_checklist` (รับในรอบ 1, Validation 93.3%) ได้ผลชัด ทั้ง 8 Trace ที่สุ่มอ่านสกิลและทำตาม ปัญหาเดิมหายหมด: `reject_value` `reject_type` `cli_ok` `cli_error` `half_up` `no_drift` ผ่านทุก Trace รวมถึง t4-cashback ที่รอบ 1 ปัดลงด้วย `//` และ t2-split-bill ที่รอบ 1 ได้ ZeroDivisionError
- ปัญหาที่เหลือมีข้อเดียวคือ `tests`: Trace ที่ตก 5 ตัว (t3-r1, t3-r2, t1-r2, t4-r2, t1-r3) ได้ 0.90 เพราะมีเทสต์ 4–5 เมธอด ตัวตรวจต้องการอย่างน้อย 6 Trace ที่ผ่าน 3 ตัว (t1-r1 6 เมธอด, t4-r3 6, t2-r1 7) ต่างกันแค่แยกเมธอดละเอียดกว่า โค้ด solve.py ของทุก Trace แทบเหมือนกัน
- สาเหตุ: เกณฑ์ 6 เมธอดไม่อยู่ในโจทย์และไม่อยู่ในสกิล สกิลบอกแค่หมวดที่ต้องครอบคลุม Agent จึงเขียน 1 เมธอดต่อหมวดและรวม assertion ไว้ในเมธอดเดียว และเห็น `Ran 4 tests OK` ก็จบ t1-r2 ยังลบเทสต์ทิ้งจน 5 เหลือ 4
- เปลี่ยน wiki: สร้างหน้า test-count-below-minimum (พร้อมข้อเสนอให้สกิลระบุ >= 6 เมธอด แนะนำ 8 และเช็ก `Ran N tests`), เพิ่มสถานะ "แก้ได้แล้ว" ในหน้า input-validation-missing, cli-entrypoint-missing, half-up-integer-rounding, happy-path-only-verification, เพิ่มสถานะและหมายเหตุเรื่องคำนวณค่าที่คาดซ้ำก่อนแก้เทสต์ใน test-file-missing และอัปเดต index
