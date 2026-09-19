# แม่แบบ Test Scenario

คัดลอกหนึ่งชุดต่อ TestID; ตัวอย่างช่องว่างไม่ใช่ผลรัน

## TS-<US>-<n> — <ชื่อพฤติกรรม>
- US: <รหัสต้นฉบับ>
- เจ้าของ: customer / kitchen-front / manager
- ประเภท: สำเร็จ / ทางเลือก / ผิดพลาด / ข้อยกเว้น
- AC ต้นฉบับเต็ม: <คัดครบ รวมตัวเลข หน่วย สูตร และจำนวนตัวอย่าง>
- clause ที่ตรวจ: <ส่วนเฉพาะของ AC>
- FR / Flow / Screen: <รหัสจริงและ path/หัวข้อ หรือ MISSING พร้อมเหตุผล>
- automation: auto / manual / mock-not-testable
- เหตุผล automation และขอบเขตที่พิสูจน์ได้: <ระบุ>
- Precondition/reset: <state เริ่มต้นและสิทธิ์>
- Test data: <ค่าจำลองและที่มา ห้ามข้อมูลบัญชีจริง>
- data-testid และ scope: <ตัวจริงในสัญญา; ถ้าซ้ำระบุ container/order ID>
- ขั้นตอน: <ลำดับ action/ค่าที่กรอก/ผลที่ควรเห็นต่อขั้น>
- Expected result: <สังเกตและตัดสินได้ ไม่ใช้คำว่าทำงานถูกต้องเฉย ๆ>
- จำนวนตัวอย่างและเกณฑ์ระบบจริง: <คง AC; ถ้าไม่เกี่ยวข้องระบุเหตุผล>
- สมมติฐาน/ข้อค้าง: <แยกจากต้นฉบับ>
- Status: NOT_RUN / MANUAL_PENDING / MOCK_NOT_TESTABLE
- Actual result: ไม่มีข้อมูล
- หลักฐาน: ไม่มีข้อมูล

รหัสใช้ TS-US-01-1 เป็นต้น; ห้ามใช้ ID ซ้ำกับ scenario คนละเรื่อง
ช่วง n>=101 สงวน fixture ใน ui-scenarios.json; หนึ่ง fixture อาจตรวจเพียงบาง clause
ตาราง coverage ต้องอ้างทั้ง ID เชิงออกแบบและ ID fixture อย่างแยกแยะ
เมื่อรันแล้วเก็บ Actual/Status/หลักฐานในรุ่นใหม่ ห้ามลบประวัติเดิม
