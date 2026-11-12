# test-count-below-minimum

มีทั้งแบบที่พลาดและแบบที่สำเร็จ

## อาการ
- ข้อ `tests` เป็นข้อเดียวที่ล้ม (ได้ 0.90 ผ่าน 9/10): `unittest พบ N เทสต์ (ต้องมีอย่างน้อย 6)`
- ส่วนอื่นผ่านครบ: contract, basic, half_up, no_drift, boundary, reject_value, reject_type, cli_ok, cli_error
- ผลของ unittest ที่ Agent เห็นเองคือ `Ran 4 tests` หรือ `Ran 5 tests` และ `OK` แต่ Agent ไม่ได้เทียบกับเกณฑ์ และสรุปว่า "ผ่านทั้งหมด"

## สาเหตุ
- สกิลบอกว่า test_solve.py "ต้องมีอย่างน้อย" แล้วไล่หมวดไว้ (ปกติ · ขอบ · ปัดเศษ · ValueError) แต่ไม่ได้ระบุ **จำนวน test method ขั้นต่ำ** ตัวตรวจนับ method `test_*` ไม่ใช่จำนวน assert
- ตัวอย่างโครงในสกิลมีแค่ `test_basic` กับ `test_reject` Agent จึงจับหมวดมาเป็น method ละหมวด ได้ 4–5 method และเอา assert หลายตัวรวมใน method เดียว
- `for` หรือ `subTest` ใน method เดียวนับเป็น 1 เทสต์ (t4-cashback-r5 ใช้ subTest ใน test_reject แล้วยังนับเป็น 1)
- เกณฑ์ 6 มองไม่เห็นจากโจทย์ มีแต่ในตัวตรวจ

## หลักฐาน
- iter 2 · ล้ม (ได้ 0.90) 5 trace: t4-cashback-r6 (5 เทสต์), t1-cafe-bill-r5 (5), t3-shipping-fee-r2 (4), t2-split-bill-r4 (4), t4-cashback-r4 (5)
- iter 2 · ผ่าน (ได้ 1.00) 3 trace: t1-cafe-bill-r1, t1-cafe-bill-r3, t4-cashback-r5 ทุกตัว `Ran 6 tests`
- ใช้โค้ด solve.py แบบเดียวกัน ต่างกันที่จำนวน method: ตัวที่ผ่านแยก `test_member`, `test_empty`, `test_birthday` หรือ `test_cap` ออกเป็น method ของตัวเอง
- ไม่เกี่ยวกับโจทย์ข้อไหน: t1 และ t4 มีทั้งผ่านและล้ม

## วิธีแก้
- เขียน test_solve.py ให้มี **อย่างน้อย 8 method `test_*`** (เกณฑ์คือ 6 เผื่อไว้ 2) แยกเป็นคนละ method:
  `test_basic` · `test_boundary_exact` · `test_boundary_below` · `test_boundary_above` · `test_half_up` · `test_reject_value` · `test_reject_type` · `test_zero_or_empty` (หรือ `test_cap` ถ้ามีเพดาน)
- ห้ามรวมหลายหมวดไว้ใน method เดียว และห้ามหวังพึ่ง `subTest` ให้นับเพิ่ม
- ก่อนจบงานดูบรรทัด `Ran N tests` จาก `python3 -m unittest -v test_solve 2>&1 | tail -5` ถ้า N < 8 ให้เพิ่ม method
- เขียนค่าคาดหวังจากการคำนวณจริงให้ถูก อย่าเขียนนิพจน์แปลก ๆ เช่น `45742.5 and 45743` (t1-cafe-bill-r1) หรือ `20000 if False else 25000 and 20000` (t4-cashback-r4) ซึ่งต้องแก้ทีหลัง
- ถ้าเทสต์ล้มให้เช็กเลขด้วยมือก่อนว่าผิดที่โค้ดหรือที่ค่าคาดหวัง (t1-cafe-bill-r3 ตรวจแล้วพบว่าผิดที่ค่าคาดหวัง 45733 ควรเป็น 45743 จึงแก้เทสต์ไม่แก้โค้ด)
