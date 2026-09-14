# ขั้น 6.5 — ตรวจผลรัน UI v2
## บริบทและเป้าหมาย
คุณเป็น QA อ่านผลจากสคริปต์ที่รันจริง ไม่รัน browser หรือเรียก AI เพิ่มในขั้นนี้
## Input
อ่าน work/ui-results-round-0.json, input/ui-scenarios.json, work/traceability.csv,
work/test-scenarios.md, work/nfr-split.md และ work/input-source.md
## งานและ Output
ตรวจจำนวน passed/failed/skipped ให้ตรง results และผูกด้วย TestID ไม่ใช้ตำแหน่งแถว
สร้าง work/ui-run-review.md แยก assertion failure, setup/infrastructure, fixture mismatch และ skip
สร้าง work/traceability-after-ui.csv header เดิม โดยอัปเดตเฉพาะ TestID ที่มีผลจริง
ใช้ Status UI_PASS/UI_FAIL/SKIP สำหรับ fixture; scenario อื่นคงสถานะเดิม
UI_PASS เป็นผล Mock-up เท่านั้น ไม่เปลี่ยนสถานะ NFR ระบบจริงเป็น PASS
อ้าง screenshot path ตาม JSON เฉพาะไฟล์ที่มีจริง; null คือไม่มีภาพพร้อม reason
อย่าสรุปภาพสวยหรือ layout ถูกต้องจากชื่อไฟล์ ต้องมีผู้เปิดตรวจภาพจริงแยกไว้
สร้างรายการข้อบกพร่องและคำแนะนำตรวจซ้ำรุ่นใหม่; ผลล้มเหลวต้องคงอยู่ในรายงาน

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
