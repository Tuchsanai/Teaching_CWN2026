# PURPOSE: billing-function-contract

## ที่มา
สร้างในรอบที่ 1 (ยังไม่มีสกิลใดมาก่อน)

## ปัญหาที่พบ
ทั้ง 12 Trace ของรอบที่ 1 (t1-cafe-bill, t2-split-bill, t3-shipping-fee, t4-cashback อย่างละ 3 รอบ) คะแนนเฉลี่ย 46.3% ไม่มี Trace ใดผ่านครบ ข้อตรวจที่ตกซ้ำเกือบทุกงาน:
- `reject_type`: float (เช่น 4500.0) และอื่น ๆ ถูกรับและคืนค่า แทนที่จะ raise ValueError
- `reject_value`: ค่า qty=0, people=0 (เกิด ZeroDivisionError), weight_g=0, amount ติดลบ ไม่ถูก raise ValueError
- `cli_ok` / `cli_error`: ไม่มี CLI เลย (รันแล้ว exit 0 stdout ว่าง)
- `tests`: ไม่มี test_solve.py
- `half_up`: t2-split-bill-r3 ปัดทิปลง (floor) แทนที่จะปัดครึ่งขึ้น

## สาเหตุ
Agent ลงมือเขียนแค่ฟังก์ชันตามสูตรของโจทย์ ไม่ทำส่วนสัญญาที่ตัวตรวจตรวจ (ตรวจอินพุต, CLI JSON, test file) และไม่ได้รันทดสอบ ในรอบนี้ไม่มีสกิลให้อ่าน (`ls ./skills` ล้มทุก Trace) หลักฐาน: t1-cafe-bill-r1, t2-split-bill-r3, t3-shipping-fee-r3, t4-cashback-r1 ใน t3-shipping-fee-r3 ผ่าน reject_value เพราะ Agent ใส่การตรวจช่วงเอง แต่ยังพลาด reject_type

## ที่ยังไม่ได้แก้
ข้อตรวจ `policy` ตกใน t3 และ t4 (เช่น shipping_fee(3000, 0, false) คาด 0 ได้ 8000; cashback(20000, "silver", true) คาด 300 ได้ 600) เป็นเรื่องเฉพาะโจทย์/การตีความกฎ ยังไม่มีหลักฐานพอสำหรับแก้ในสกิลทั่วไป สกิลนี้จึงเพียงเตือนให้ทำตามกฎทุกข้อและคำนวณตัวอย่างด้วยมือ

## ประวัติการแก้
- รอบ 1: สร้างสกิล ครอบคลุมการตรวจอินพุต, half up, CLI, test_solve.py และขั้นตอนรันตรวจก่อนส่ง
