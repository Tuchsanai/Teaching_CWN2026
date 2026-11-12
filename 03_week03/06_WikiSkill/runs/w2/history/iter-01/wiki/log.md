# Evolution Log

## Iteration 1 · Training 45.4%

ไม่มีสกิล และ skill-impact ยังว่าง จึงเป็นรอบฐานเริ่มต้น Trace 5 ตัว (t1 cafe_bill, t2 split_bill, t3 shipping_fee, t4 cashback x2) ได้ 0.30–0.50

สิ่งที่พบ:
- ผ่านเหมือนกันทุก trace: `contract`, `basic`, `boundary` ตรรกะธุรกิจหลักถูก
- ล้มเหมือนกัน 5/5 ในสี่ข้อที่โจทย์ไม่ได้บอกตรง ๆ: `reject_value`+`reject_type` (ไม่ตรวจอินพุต), `cli_ok`+`cli_error` (ไม่มี CLI), `tests` (ไม่มี test_solve.py)
- ล้มเฉพาะ cashback: `half_up`+`no_drift` เพราะเลือกปัดลง ส่วน cafe_bill/split_bill/shipping_fee ใช้ integer/Fraction แล้วปัด half up ผ่าน
- Agent เช็ค `./skills` แล้วไม่พบ จึงเขียนตามโจทย์ตรง ๆ ด้วยคำสั่ง 2 ครั้ง และทดสอบแค่กรณีปกติ

หน้าที่เพิ่ม: input-validation-missing, cli-json-wrapper-missing, missing-test-file, rounding-exact-half-up (มีทั้งแบบพลาดและสำเร็จ), happy-path-only-self-check

ข้อสังเกตสำหรับ Skill Proposer: สาเหตุหลักมาจากข้อกำหนดที่อยู่ในตัวตรวจแต่ไม่อยู่ในโจทย์ จึงควรเขียนสกิลเป็น checklist ส่งมอบที่ใช้ได้กับทุกฟังก์ชันของ BaanKafe รอบนี้ยังไม่มีสกิลให้ประเมินว่าได้ผลหรือไม่
