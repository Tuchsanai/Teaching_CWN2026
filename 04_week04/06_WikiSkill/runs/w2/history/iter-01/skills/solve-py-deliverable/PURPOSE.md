# PURPOSE: solve-py-deliverable

สร้างในรอบที่ 1 (iteration 1) เพราะยังไม่มีสกิลใดเลย และ Training 12 Trace ตกซ้ำชุดเดียวกันทุกงาน (คะแนนเฉลี่ย 46.4% ผ่านครบ 0/12): `reject_value`, `reject_type`, `cli_ok`, `cli_error`, `tests`

## pattern ที่แก้ใน wiki
- `wiki/patterns/missing-input-validation.md` : ตรวจช่วงและชนิดแบบเข้ม แล้ว raise ValueError
- `wiki/patterns/missing-cli-entrypoint.md` : entrypoint อ่าน JSON จาก stdin พิมพ์ ok/result exit 0 หรือ error exit 2
- `wiki/patterns/missing-test-file.md` : สร้าง test_solve.py และรันให้ผ่าน
- `wiki/patterns/no-self-verification.md` : ขั้นตอนตรวจก่อนส่งที่ต้องรันจริง
- `wiki/patterns/integer-math-half-up-works.md` : คงวิธีคำนวณเป็นจำนวนเต็มและปัดครึ่งขึ้นครั้งเดียวไว้ (ได้ผลอยู่แล้ว)

## หลักฐาน
เปิดดู Trace: t1-cafe-bill-r1, t1-cafe-bill-r3, t2-split-bill-r2, t3-shipping-fee-r1, t4-cashback-r3 ทุกงานเขียนแค่ฟังก์ชัน happy path ไม่มี `__main__` ไม่มี test_solve.py และ Agent ไม่เห็นสกิลเพราะ `./skills` ว่าง ส่วนผ่านเฉพาะข้อคำนวณ (`contract`, `basic`, `half_up`, `no_drift`, `boundary`) ยังไม่ได้แตะข้อ `policy` (ยังไม่ยืนยันสาเหตุ ดู `wiki/patterns/policy-mismatch-unconfirmed.md`)

## ประวัติการแก้
- รอบ 1: สร้างสกิล รวมกฎตรวจอินพุต + CLI + test_solve.py + เช็กลิสต์ก่อนส่ง
