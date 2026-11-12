# test-file-missing: ไม่มี test_solve.py ข้าง solve.py

## อาการ
- ข้อตรวจ `tests` ตกใน 5 จาก 5 Trace: "ไม่มีไฟล์ test_solve.py ข้าง solve.py"

## สาเหตุ
- โจทย์ไม่ได้สั่งให้เขียน test แต่ตัวตรวจเช็คว่ามีไฟล์
- Agent ทดสอบด้วย `python3 -c "print(...)"` ครั้งเดียวแล้วทิ้ง ไม่เก็บเป็นไฟล์

## หลักฐาน
- iteration 1: ทุก Trace ไม่มีการสร้างไฟล์อื่นนอกจาก solve.py
- t2-split-bill-r1 ไม่ได้รันทดสอบใดเลย (เขียนไฟล์แล้วจบ)

## วิธีแก้
1. สร้าง `test_solve.py` ในโฟลเดอร์เดียวกับ solve.py (ใช้ `unittest` หรือ `pytest` แบบ `from solve import FUNC`)
2. ครอบคลุมอย่างน้อย: กรณีปกติ · ค่าขอบ (เช่น พอดี 100 บาท, พอดี 1,000 กรัม) · เศษที่ต้องปัดครึ่งขึ้น · input ผิดช่วงและผิดชนิดต้อง `assertRaises(ValueError)`
3. รันจริง (`python3 -m unittest -q` หรือ `pytest -q`) และดูว่าผ่านก่อนตอบ
4. ถ้า test ล้ม ให้แก้ solve.py ไม่ใช่แก้ test ให้ผ่านตามผลเดิม
