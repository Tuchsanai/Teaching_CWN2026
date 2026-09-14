# ขั้น 6.4 — แยก NFR ที่ Mock-up ตรวจได้และระบบจริง
## บริบทและเป้าหมาย
คุณเป็น QA ป้องกันการนำผลคลิกแทนหลักฐาน AC ระบบจริง
## Input
อ่าน ../docs/case-study-source.md, ../docs/data-issues.md, work/source/fr-nfr-v2.md,
work/test-scenarios.md, work/traceability.csv และ work/traceability-notes.md
## งานและ Output
สร้าง work/nfr-split.md ตาราง US/AC เดิม | ส่วน functional ใน Mock-up | ข้อจำกัด | วิธีตรวจระบบจริง | environment/data | เกณฑ์/จำนวนตัวอย่าง | automation | หลักฐานที่ต้องเก็บ | สถานะ
คัดตัวเลข หน่วย สูตร ช่วงเวลา และสัดส่วนเดิม ห้ามลดจำนวนตัวอย่างให้เท่าชุด smoke
รวมเวลา Wi-Fi/LAN, ความแม่นเวลารอ, timestamp/concurrency, security/PIN/สิทธิ์,
รายงาน/ข้อมูลคงทน, Ubuntu/install/offline และการยืนยันชำระเงินด้วยมือ
แยกตรวจซ่อนหน้าจอได้จากยืนยันสิทธิ์ฝั่ง server ได้; file:// ไม่พิสูจน์การติดตั้ง 30 นาที
แยกนาฬิกาจำลองจาก wall time; ไม่ใช้ timeout ของ Playwright เป็นเกณฑ์ธุรกิจ
ให้แผนเก็บ log/เครื่อง/ผู้ตรวจ/จำนวนตัวอย่างครบ แต่สถานะระบบจริงเริ่ม NOT_TESTED
กรณี AC เดียวมีสองประเภทให้แยกแถวโดยคง AC เต็มและขอบเขตแต่ละแถว

## กติกาและขอบเขต
Working directory: AI_Workflow_Engineering_for_SA/006_LAB_Test_Scenarios_Traceability/
เริ่ม session ใหม่ทุกการเรียก อ่าน Input จากไฟล์ ไม่พึ่งประวัติสนทนา ไม่เรียกผู้ช่วยเพิ่ม
เขียนเฉพาะ work/ ไม่แก้ต้นทาง input/, prompts/, reference/, img/ หรือ LAB อื่น
หาก output มีแล้วให้หยุดและขอ path รุ่นใหม่ในบันทึก ไม่เขียนทับหลักฐาน
รักษาข้อความ US/AC ตัวเลข หน่วย สูตร และจำนวนตัวอย่างต้นฉบับทุกข้อ
ใช้ข้อมูลจำลองเท่านั้น; สมมติฐาน fixture ไม่ใช่ข้อกำหนดร้าน
ข้อมูลขาดให้ระบุ BLOCKED/ไม่มีข้อมูล ไม่แต่ง FR, Flow, selector หรือผลผ่าน
ผลคลิก Mock-up ไม่ยืนยัน LAN, Security, Load, Availability หรือการชำระเงินจริง
สรุปไฟล์ที่สร้างจริง ข้อบกพร่อง ข้อค้าง และสิ่งที่ยังไม่ได้ทดสอบ
