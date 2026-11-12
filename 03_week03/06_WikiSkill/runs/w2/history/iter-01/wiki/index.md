# Wiki Index

- [input-validation-missing](wiki/patterns/input-validation-missing.md): ฟังก์ชันไม่ตรวจอินพุต จึงคืนค่าปกติหรือ raise ZeroDivisionError เมื่อได้ค่านอกช่วง/float/bool (reject_value, reject_type) เพราะโจทย์บอกแค่ช่วงที่ถูก ให้ตรวจทุกพารามิเตอร์เป็นอย่างแรก (ปฏิเสธ bool และ float) แล้ว raise ValueError
- [cli-json-wrapper-missing](wiki/patterns/cli-json-wrapper-missing.md): cli_ok/cli_error ล้มเพราะ solve.py มีแต่ฟังก์ชัน ไม่อ่าน stdin ซึ่งโจทย์ไม่ได้บอก ให้เพิ่ม main ที่อ่าน JSON จาก stdin พิมพ์ {"ok":true,"result":..} exit 0 และเมื่อผิดพิมพ์ {"ok":false,"error":..} exit 2
- [missing-test-file](wiki/patterns/missing-test-file.md): ข้อ tests ล้มเพราะไม่มี test_solve.py ข้าง solve.py (โจทย์ไม่ได้ขอ) ให้สร้างไฟล์ unittest ครอบคลุมกรณีปกติ ค่าขอบ ปัดเศษ และ ValueError แล้วรันให้ผ่าน
- [rounding-exact-half-up](wiki/patterns/rounding-exact-half-up.md): half_up/no_drift ล้มเมื่อเลือกปัดลง (//) เองตอนโจทย์ไม่ระบุ ส่วนข้อที่ผ่านใช้จำนวนเต็ม/Fraction แล้วปัด half up ครั้งเดียวท้ายสุด ใช้ (num*2+den)//(den*2) ห้าม float และ round()
- [happy-path-only-self-check](wiki/patterns/happy-path-only-self-check.md): Agent ทดสอบเองแค่ตัวอย่างปกติ 3–5 ตัวแล้วจบ จึงพลาดทุกข้อนอกเหนือจากกรณีปกติ (ได้ 0.30–0.50) ให้ใช้ checklist 5 ข้อ: ค่าขอบ ปัดเศษ ValueError CLI และ test_solve.py ก่อนส่งงาน
