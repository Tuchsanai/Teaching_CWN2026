สร้าง [scenarios-kitchen-front.md](scenarios-kitchen-front.md) แล้ว มี 40 scenarios ครอบคลุม US-10–US-18 พร้อม AC ต้นฉบับครบ ดัชนี TestID และข้อค้าง

- `auto` 19 / `manual` 1 / `mock-not-testable` 20
- ตรวจ AC ตรงต้นฉบับทั้ง 40 scenarios และ ID ไม่ซ้ำ
- ข้อค้าง: US-17/18 ไม่มี FR/Flow/UI, selector บางชื่อไม่ตรงสัญญา และกฎกรณีผิดปกติยังรอยืนยัน
- ยังไม่ได้รัน Mock-up หรือระบบจริง สถานะเป็น `NOT_RUN`/`NOT_TESTABLE` ทั้งหมด

เขียนเฉพาะไฟล์ Output ที่ระบุ ไม่แก้ Input หรือผลเดิมครับ