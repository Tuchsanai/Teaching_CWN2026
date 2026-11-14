# PURPOSE: solve-py-contract

## ที่มา
สร้างในรอบ 1 (iteration 1) ตอนยังไม่มีสกิลใช้งานเลย

## หลักฐาน
ทั้ง 12 Trace ในรอบ 1 ตกข้อตรวจ `reject_value`, `reject_type`, `cli_ok`, `cli_error`, `tests` เหมือนกันทุกโจทย์ (คะแนนเฉลี่ย 46.4%) ขณะที่ข้อตรวจเรื่องการคำนวณ (`basic`, `no_drift`, `boundary`, `half_up`) ผ่านหมด เปิดดู `t1-cafe-bill-r1`, `t2-split-bill-r2`, `t3-shipping-fee-r1`, `t4-cashback-r2` แล้วพบว่า Agent เขียนแต่สูตรคำนวณ ไม่มี `raise ValueError`, ไม่มีบล็อก `__main__` อ่าน stdin, ไม่มี test_solve.py และทดสอบด้วย `python3 -c` ทิ้ง (t4-cashback-r2 ไม่ได้รันเลย)

## pattern ใน wiki ที่แก้
- `wiki/patterns/missing-input-validation.md`
- `wiki/patterns/missing-cli-entrypoint.md`
- `wiki/patterns/missing-test-file.md`
- `wiki/patterns/shallow-self-check.md` (ส่วนรายการตรวจก่อนตอบ)

ไม่ได้แตะ `wiki/patterns/policy-ambiguous-edge-cases.md` เพราะยังไม่ยืนยันสาเหตุ และคงแนวทางจำนวนเต็มจาก `wiki/patterns/integer-money-arithmetic.md` ไว้

## ประวัติการแก้
- รอบ 1: สร้างสกิล รวม 3 ส่วนของสัญญาไฟล์ solve.py ที่โจทย์ไม่ได้บอก (ตรวจอินพุต, CLI, test_solve.py) เพราะเป็นกลุ่มข้อตรวจที่ตกพร้อมกันทุก Trace
