# บันทึก Epoch 1 (ตา 1)

## คะแนน epoch 0 (ค่าเฉลี่ยต่อโจทย์, 3 ครั้ง)
- t1-cafe-bill: 0.6 / 0.5 / 0.5
- t2-split-bill: 0.6 / 0.6 / 0.6
- t3-shipping-fee: 0.5455 (ทั้ง 3 ครั้ง)
- t4-cashback: 0.4 (ทั้ง 3 ครั้ง)

## ผลรัน test อ้างอิง (reference/baankafe/answers/*/test_solve.py) กับ solve.py ของ Solver
สคริปต์: `evolver_workspace/analysis/runtests.sh`, `detail.sh` (ดึงไฟล์ไปรันในโฟลเดอร์ชั่วคราว)

| Solver | ผลที่ไม่ผ่าน | สาเหตุ |
|---|---|---|
| t1 s1 | reject_3, reject_4 | `int(item["price"])` รับ float/str เงียบ ๆ |
| t1 s2 | no_drift_2 (45879 vs 45880), reject_3, reject_4 | ปัดเศษทุกขั้นตอน (intermediate rounding) + รับ float/str |
| t1 s3 | reject_1..4 | ไม่ตรวจ qty<1 / ช่วง / type เลย |
| t2 s1, s2 | ผ่านทั้งหมด | แต่คะแนน 0.6 → มีการตรวจอื่นที่ไม่เห็น |
| t2 s3 | reject_3, reject_4 (error) | รับ float/str; ทำ TypeError |
| t3 s1..s3 | reject_3, reject_4 | `Fraction(str(x))` / ไม่ตรวจ type → รับ float/str |
| t4 s1..s3 | no_drift_1, no_drift_2 (800 vs 801, 500 vs 501) | floor ก่อนคูณ ×2 (birthday) |
| t4 s1..s3 | reject_3, reject_4 | โยน TypeError แทน ValueError; และ normalize tier (.lower/.strip) |

## ข้อสรุปเชิงกลไก
1. ปัญหาใหญ่ที่สุด: การตรวจ type/ช่วงของ input ไม่เข้มงวด (ใช้ int()/str() แปลงค่าเงียบ, ใช้ TypeError, ไม่ตรวจ bool)
2. ลำดับการปัดเศษ: ต้องคูณทั้งหมดให้เสร็จแล้วปัดครั้งเดียว Python round() เป็น banker's rounding
3. กฎที่โจทย์ไม่ได้เขียนไว้ (เช่น กรณีพิเศษบางค่า, ข้อจำกัดเฉพาะ tier) Solver ไม่มีทางรู้จาก brief → สกิลทั่วไปแก้ไม่ได้ทั้งหมด
4. สิ่งที่ไม่รู้: ทำไม t2 s1/s2 ผ่าน test ทั้งหมดแต่ได้ 0.6 (อาจเป็น hidden test หรือ CLI interface แบบ main()/stdin JSON ที่เฉลยมี)

## การตัดสินใจเรื่อง reference
- ใช้เฉลยเพื่อวินิจฉัยเท่านั้น
- สกิลใน staging ใส่เฉพาะหลักการทั่วไป ไม่ใส่โค้ดเฉลยและไม่ใส่กฎเฉพาะของโจทย์ (เช่น ค่าส่งเมื่อระยะ 0, ข้อจำกัดส่งด่วน, silver ไม่มีโบนัสเดือนเกิด) เพราะจะเป็นการ overfit ต่อ 4 โจทย์นี้และไม่ใช่สิ่งที่ Solver อนุมานได้จากโจทย์
- ถ้าผู้ใช้ต้องการให้ใส่กฎเหล่านี้ ให้ถามก่อน

## ชุดสกิล skills_v1 (ใน staging/)
- strict-input-validation: ปฏิเสธ input ผิด type/ช่วงด้วย ValueError
- integer-money-rounding: เก็บสตางค์เป็นจำนวนเต็ม/Fraction, ปัดครั้งเดียวท้ายสุด, ลำดับตัวคูณ
- solve-task-checklist: ขั้นตอนก่อนส่ง (แตกกฎ, ทดสอบขอบ, รันจริง, สรุปการตีความ)

## สิ่งที่ควรดูใน epoch 2
- คะแนน reject tests ควรขึ้นจากเดิม (ถ้า Solver ทำตามสกิลได้)
- ถ้า t4 ยังได้ 0.4 ให้ดูว่าเป็นเรื่องกฎที่ซ่อนอยู่หรือเรื่องการปัด
- ตรวจว่า Solver ใช้ `python3 -I` import ไม่ได้หรือไม่ (ดู ModuleNotFoundError ใน trace)
