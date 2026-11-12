# Evolution Log

## Iteration 1 · Training 44.2%

รอบแรก ยังไม่มีสกิลและ skill-impact ว่าง จึงยังไม่มีผลของข้อเสนอเก่าให้ติดตาม

สิ่งที่พบ: ทุก trace ผ่านเฉพาะ `contract`/`basic` (กับ `boundary`/`half_up`/`no_drift` บางตัว) ส่วนที่ล้มซ้ำกันทุกโจทย์ เป็นข้อตกลงแฝงที่โจทย์ไม่ได้เขียน:
- ไม่มี CLI อ่าน stdin JSON (cli_ok/cli_error ล้ม 5/5)
- ไม่ validate ช่วงค่าและชนิด (reject_value/reject_type ล้ม 5/5)
- ไม่มี test_solve.py (tests ล้ม 5/5)
- ปัดเศษด้วย floor แทน half-up ใน t4 (สองรอบ) และ t2 (`half_up` ล้ม, t4 `no_drift` ล้มด้วย) ส่วน t1/t3 ผ่านเพราะใช้เลขจำนวนเต็ม/Fraction ปัด half-up ครั้งเดียวตอนท้าย
- Agent ทดสอบเฉพาะ happy path และรายงานว่าถูกต้อง

เปลี่ยน wiki: สร้าง 5 หน้าใหม่ missing-cli-entrypoint, missing-input-validation, money-rounding-half-up (รวมฝั่งที่ทำสำเร็จ), missing-test-file, happy-path-only-verification และอัปเดต index

ข้อสังเกตเพิ่ม: ข้อตรวจที่ล้มเกือบทุก trace มาจากข้อกำหนดแฝง ไม่ใช่ตรรกะธุรกิจ แก้ 4 เรื่องแรกได้น่าจะเพิ่มคะแนนได้มาก (ประมาณ +0.4 ถึง +0.5 ต่อ trace) ส่วนข้อที่ยังไม่ยืนยัน: ตัวตรวจ reject_type ปฏิเสธ bool หรือ flag ที่ไม่ใช่ bool หรือไม่
