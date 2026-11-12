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

## Iteration 2 · Training 91.3%

รอบนี้ใช้สกิล `cafe_solve_checklist` (เสนอใน iter 1, รับที่ Validation 92.5%) ขึ้นจากรอบฐาน 45.4% Trace 8 ตัว: ล้ม 5 (t4-cashback-r6, r4, t1-cafe-bill-r5, t3-shipping-fee-r2, t2-split-bill-r4) ผ่าน 3 (t1-cafe-bill-r1, r3, t4-cashback-r5)

สถานะของปัญหาเดิมจาก iter 1:
- input-validation-missing: แก้ได้แล้ว reject_value/reject_type ผ่าน 8/8
- cli-json-wrapper-missing: แก้ได้แล้ว cli_ok/cli_error ผ่าน 8/8
- rounding-exact-half-up: แก้ได้แล้ว cashback ทั้ง 3 trace ใช้ Fraction/int ปัด half up ผ่านครบ
- missing-test-file: เรื่องไฟล์หายแก้ได้แล้ว Agent สร้าง test_solve.py ครบ 8/8
- happy-path-only-self-check: ดีขึ้น Agent รัน unittest และ CLI ทั้งปกติและผิดทุกตัว

สิ่งที่พบใหม่: ทั้ง 5 trace ที่ล้มพลาดข้อเดียวคือ `tests` ที่ `unittest พบ N เทสต์ (ต้องมีอย่างน้อย 6)` (N = 4, 4, 5, 5, 5) ส่วนทั้ง 3 trace ที่ผ่านมี 6 เทสต์พอดี โค้ด solve.py ไม่ต่างกัน ต่างแค่จำนวน method `test_*`
- สาเหตุ: สกิลเขียนว่า "ต้องมีอย่างน้อย" เป็นหมวด ไม่มีตัวเลขจำนวน method และตัวอย่างโครงมีแค่ test_basic กับ test_reject Agent จึงเขียนหมวดละ method ได้ 4–5 ตัว และเห็น `Ran 5 tests` แล้วไม่ได้เอะใจ
- เพิ่มหน้า test-count-below-minimum (มีทั้งแบบพลาดและแบบสำเร็จ) และเพิ่มหมายเหตุสถานะ iter 2 ในอีก 5 หน้า รวมทั้งแก้บรรทัดใน index

ข้อสังเกตอื่น: ตอนเขียนเทสต์ Agent คำนวณค่าคาดหวังผิดหลายครั้ง (t1-r3 ได้ 45733 แทน 45743, t1-r1 ใช้นิพจน์ `45742.5 and 45743`, t4-r4 ใช้ `20000 if False else ...` แล้วแก้ด้วย sed) ไม่กระทบคะแนนแต่เป็นความเสี่ยง

ข้อสังเกตสำหรับ Skill Proposer: แก้สกิลข้อ 4 ให้ระบุ "อย่างน้อย 8 method `test_*` แยกหมวด (เกณฑ์ 6 + เผื่อ)" ปรับตัวอย่างโครงให้มีหลาย method และสั่งให้ดู `Ran N tests` ก่อนจบ ไม่ควรแตะส่วนอื่นของสกิลเพราะผ่านครบแล้ว
