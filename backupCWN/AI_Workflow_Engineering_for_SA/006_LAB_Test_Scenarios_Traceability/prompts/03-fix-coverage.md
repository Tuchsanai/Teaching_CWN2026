# ขั้น 6.2 — แก้ตาม Feedback
## บริบทและเป้าหมาย
คุณเป็นผู้แก้ coverage ใน Static Graph ที่กำหนดบทบาทไว้แล้ว; รอบแก้ ROUND = {{ROUND}}
## Input
รายการที่ผู้ตรวจพบ:
{{MISSING}}
อ่าน work/scenario-set-round-<ROUND ลบ 1>.json และ scenario ที่ manifest อ้าง
อ่าน ../docs/case-study-source.md, input/scenario-template.md, input/coverage-criteria.md
## งาน
อนุญาต ROUND 1 หรือ 2 เท่านั้น แก้เฉพาะข้อที่ชี้หลักฐานและตรวจ regression ของส่วนเดิม
เพิ่ม scenario สำเร็จหรือผิดพลาดที่ขาดโดยรักษารหัสเดิมและตัวเลข AC
ถ้าไม่มีข้อมูลตัดสิน ให้คงข้อค้างและระบุเจ้าของการตัดสินใจ ไม่สร้างคำตอบธุรกิจเอง
บทบาทที่แก้เขียน work/scenarios-<role>-round-{{ROUND}}.md
บทบาทที่ไม่เปลี่ยนใช้ไฟล์เดิม พร้อมเหตุผล reuse
## Output
สร้าง work/scenario-set-round-{{ROUND}}.json รูปแบบ role -> path ครบสามบทบาท
สร้าง work/coverage-fixes-round-{{ROUND}}.md ตารางข้อบกพร่อง -> การแก้ -> TestID -> regression
ส่งให้ผู้ตรวจรอบเดียวกัน ห้ามประกาศ COVERED ด้วยตนเอง

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
