# missing-test-file

## อาการ
- ข้อ `tests` ล้มทุก trace: `ไม่มีไฟล์ test_solve.py ข้าง solve.py`

## สาเหตุ
- โจทย์พูดแต่ `solve.py` Agent เขียนไฟล์เดียวแล้วทดลองรันด้วย `python3 -c` แบบใช้ครั้งเดียวทิ้ง จึงไม่มีไฟล์ test เหลือไว้
- ตัวตรวจคาดว่าต้องมี `test_solve.py` วางไว้ในโฟลเดอร์เดียวกับ `solve.py`

## หลักฐาน
- iteration 1 ทุก trace (t1-cafe-bill-r1, t2-split-bill-r1, t3-shipping-fee-r3, t4-cashback-r1, t4-cashback-r3)
- ทุก trace ใช้คำสั่งแค่ 2–3 ครั้ง และไม่มีการสร้างไฟล์อื่นนอกจาก `solve.py`

## วิธีแก้
สร้าง `test_solve.py` ข้าง `solve.py` (unittest หรือ pytest ก็ได้) แล้วรันให้ผ่านก่อนจบ ให้มีอย่างน้อย:
- กรณีปกติจากตัวอย่างในโจทย์
- ค่าขอบ (เช่น พอดี 100 บาท, พอดี 1,000 กรัม, เพดาน 200 บาท)
- กรณีเศษ .5 เพื่อยืนยัน half-up (ดู money-rounding-half-up)
- `assertRaises(ValueError)` สำหรับค่านอกช่วง, float, ค่า enum ผิด
- CLI ผ่าน `subprocess.run([sys.executable, 'solve.py'], input=..., capture_output=True, text=True)` ทั้งกรณี ok (exit 0) และ error (exit 2)

รันด้วย `python3 -m unittest -v` หรือ `python3 -m pytest` จากโฟลเดอร์ที่มี `solve.py`
