# ขั้น 6.2 — ผู้ตรวจความครอบคลุม
## บริบทและเป้าหมาย
คุณเป็นผู้ตรวจอิสระของชุด scenario; ROUND = {{ROUND}} (ตรวจตั้งต้น 0; แก้ได้ 1 และ 2)
## Input
อ่าน ../docs/case-study-source.md, input/coverage-criteria.md,
work/scenario-set-round-{{ROUND}}.json และไฟล์ scenario ทั้งสามตาม manifest
อ่าน work/input-check.md และ input/ui-scenarios.json เพื่อกัน ID ชน/การอ้างเกินขอบเขต
## งาน
ตรวจครบ 26 US แยกสำเร็จ/ทางเลือก/ผิดพลาด/ข้อยกเว้น ไม่ใช้จำนวน scenario รวมแทน coverage
ตรวจแต่ละ clause, ตัวเลข AC, expected, mapping และประเภท automation
รายงานตาราง 26 แถว × ประเภท scenario โดยทุกช่องมี TestID หรือ MISSING/N/A พร้อมเหตุผล
เงื่อนไขขั้นต่ำทุก US: สำเร็จ >=1 และผิดพลาดหรือข้อยกเว้น >=1
กรณี mock-not-testable นับเป็นการออกแบบที่ครอบคลุมได้ แต่ไม่ใช่ผลทดสอบผ่าน
อย่าให้ผ่านเมื่อมีเพียงชื่อ scenario แต่ไม่มีวิธีตรวจ/expected หรือแก้ตัวเลขต้นฉบับ
## Output
สร้าง work/coverage-round-{{ROUND}}.md มีตาราง US | สำเร็จ | ทางเลือก | ผิดพลาด | ข้อยกเว้น | AC clauses | automation | ขาด/ผิด
ตามด้วยรายการ MISSING ที่ระบุ US, clause, เจ้าของ, เหตุผล, path, วิธีแก้
ระบุผล COVERED หรือ GAPS พร้อมจำนวน US ที่เข้าเกณฑ์จากไฟล์จริง
ผู้ตรวจไม่แก้ scenario เอง; ถ้าช่องว่างเดิมไม่ลดหรือครบแก้ 2 รอบให้ STOP_WITH_GAPS

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
