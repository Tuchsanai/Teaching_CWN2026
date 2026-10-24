# BUGFIX · EX-A5 ติ๊กรถแต่ไม่มีโรงแรม/ระยะ

| หัวข้อ | รายละเอียด |
|---|---|
| ต้นเหตุ ชั้น UI | `web/components/BookingWizard.tsx` `body()` ส่ง `hotelCode/distanceKm = null` เมื่อว่าง และ `next3()` ไม่ตรวจว่าเลือกโรงแรม/ใส่ระยะแล้ว |
| ต้นเหตุ ชั้น API | `web/lib/server/booking.ts` `buildQuote` ไม่รู้จัก `wantTransport` → ไม่มีระยะ = ไม่คิดค่ารถ และบันทึกนัดได้ |
| ทำไมไม่มีใครจับ | e2e-legacy TC-TRN-03 รู้ปัญหาแต่ติด `test.fail` KNOWN-ISSUE · check-rules ไม่มีเคส wantTransport ที่ไม่มีระยะ |
| เทสต์เดิมที่เปลี่ยนสถานะ | TC-TRN-03 เอา `test.fail` ออก (แถวใน ORACLE-CHANGES ข้อ 5) |
| เทสต์ทำซ้ำ | `tests/exam5/transport-required.mjs` (แดงที่ EX5-red · เขียวที่ EX5) |
