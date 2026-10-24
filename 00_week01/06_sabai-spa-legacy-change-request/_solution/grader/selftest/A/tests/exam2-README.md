# golden master ของ POST /api/price (ข้อ 2)

| | |
|---|---|
| รัน | `node tests/exam2/run.mjs` (อ่าน `BASE_URL` ค่าเริ่ม `http://localhost:4000` · reset ข้อมูลเองก่อนทุกเคส) · exit 0 = ตรงทั้งหมด |
| ที่มาของค่า | `node tests/exam2/run.mjs --record` กับระบบตั้งต้นที่ commit `EX0` (now = 2026-10-10 10:00) |
| ฟิลด์ที่ตัด | ไม่มี · `/api/price` ไม่คืน id/เวลาสร้าง/cookie (ถ้ามีจะตัดเพราะเปลี่ยนทุกครั้ง) |
