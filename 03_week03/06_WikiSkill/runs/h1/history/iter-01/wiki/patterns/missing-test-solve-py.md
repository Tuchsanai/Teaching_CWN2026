# ไม่สร้างไฟล์ test_solve.py ข้าง solve.py (tests)

## อาการ
- ข้อตรวจ `tests` พลาดทุกรอบ: "ไม่มีไฟล์ test_solve.py ข้าง solve.py"

## สาเหตุ
- โจทย์ไม่ได้ขอไฟล์ทดสอบ Agent ทดสอบด้วย `python3 -c` หรือ assert ในคำสั่ง shell ที่ใช้ครั้งเดียวทิ้ง (หรือใส่เคสใน `__main__`) ไม่เหลือไฟล์ในโฟลเดอร์งาน
- ผลคือ Agent ทดสอบแล้วแต่ไม่เหลือหลักฐานที่ตัวตรวจเห็น

## หลักฐาน
- iteration 1: ทั้ง 5 trace (t1-cafe-bill-r2, t2-split-bill-r1, t3-shipping-fee-r3, t4-cashback-r1, t4-cashback-r3) พลาดข้อนี้ ทุกตัวมีแต่ solve.py

## วิธีแก้
- เขียน `test_solve.py` ในโฟลเดอร์เดียวกับ solve.py ทุกครั้ง ใช้ `unittest` หรือ `pytest` ที่มี `import solve` หรือ `from solve import FUNC`
- ควรมีอย่างน้อย: เคสปกติ, ขอบเขต (เช่น 9,999 กับ 10,000 สตางค์), เคสเศษ .5 พอดีที่ต้องปัดขึ้น, ค่านอกช่วงและชนิดผิด (`assertRaises(ValueError)`, รวม float, bool, str) และ CLI ผ่าน `subprocess` ทั้งสำเร็จ (exit 0) และผิด (exit 2)
- รันจากโฟลเดอร์งาน: `python3 -m unittest -v` หรือ `python3 -m pytest -q` และแก้ solve.py จนผ่านก่อนจบ
- อย่าใช้ `python3 -I` เพื่อ import solve (ตัด cwd ออกจาก sys.path ทำให้ `ModuleNotFoundError` ซึ่งเกิดใน t1, t2, t3 เสียไป 1 คำสั่ง)
