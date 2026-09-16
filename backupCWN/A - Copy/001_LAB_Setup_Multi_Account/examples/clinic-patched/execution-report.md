# ผลรอบล่าสุด: READY

เพิ่ม effort จาก medium เป็น high สำหรับ Fable และ Astra พร้อมนำข้อทักท้วงจริงมาแก้แผน รอบที่ผ่านใช้ Fable high สร้างข้อความแก้ไขเฉพาะจุด และ Astra high ตรวจแผนทั้งฉบับด้วยเกณฑ์เดิม

| รอบ | การตั้งค่า | ผลจริง |
|---|---|---|
| เดิม | Fable medium / Astra medium | NOT READY |
| ปรับทั้งฉบับ 2 รอบ | Fable high / Astra high | NOT READY; เหลือกติกาหน้างานเปิดค้างและการคืนสถานะหลังเวรเปลี่ยน |
| ลอง max | Fable max | ไม่ได้คำตอบภายในเวลารอ 480 วินาที จึงไม่มีผลตรวจรอบนี้ |
| แก้เฉพาะจุด | Fable high / Astra high | READY หลังใช้ข้อความแก้ไข 6 จุด |

## ไฟล์ที่เกิดจริง

- [patch-1.md](patch-1.md): JSON ข้อความเดิม/ข้อความใหม่จาก Fable high
- [plan-v5.md](plan-v5.md): โปรแกรมนำ patch จริงทั้ง 6 จุดไปใช้กับ [แผนฐาน v4](baseline-plan-v4.md) โดยตรวจว่าข้อความเดิมตรงหนึ่งแห่งทุกจุด เนื้อหาชื่อเรื่องของแผนฐานยังคงเดิม
- [review-final.md](review-final.md): คำตัดสิน READY จาก Astra high คัดลอกตรงจาก [ผลตรวจต้นฉบับ](review-patched-1.md)
- [solution.md](solution.md): ข้อเสนอสรุปจาก Astra high หลังผ่านเกณฑ์
- [scenario-results.md](scenario-results.md): ผลประเมินสถานการณ์สมมติจาก Astra high

## วิธีเก็บผล

รัน CLI แยกคำสั่งในคอนเทนเนอร์ Devtools Lab ผ่าน SSH บน 5090 ผู้รันทดสอบนำเนื้อหาไฟล์ต้นทางประกอบเป็นพรอมต์และบันทึกคำตอบ จึงไม่ใช้รอบนี้เป็นหลักฐานว่า Fable เรียก Astra อัตโนมัติตามพรอมต์หลัก

Fable ใช้ --safe-mode, --model fable, --effort high, --tools และค่าว่าง, --output-format json ส่วน Codex ใช้ exec --model gpt-6-astra -c model_reasoning_effort=high พร้อมบันทึก output ผ่าน -o ทุกคำสั่งจบด้วย exit code 0 รายละเอียดไฟล์ input และรายชื่อโมเดลที่ CLI รายงานอยู่ใน [execution.json](execution.json)

เก็บพรอมต์ที่ส่งจริงในไฟล์ *-input.txt ข้อความคำตอบจากโมเดลไม่ถูกแก้ให้ผ่านเกณฑ์ การเพิ่ม effort เกิดพร้อมการแก้แผนและการตรวจเพิ่มเติม จึงไม่ได้พิสูจน์ว่าเพิ่ม effort อย่างเดียวแล้วจะผ่าน

READY หมายถึงพร้อมสรุปข้อเสนอ ไม่ใช่รับรองซอฟต์แวร์หรือผลใช้จริงกับคลินิก คอนเทนเนอร์และสำเนาข้อมูลล็อกอินลบแล้วและตรวจยืนยันว่าไม่ค้าง
