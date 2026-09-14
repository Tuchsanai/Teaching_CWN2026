# ขั้น 6.5 — ตรวจผลรัน UI v2
## บริบทและเป้าหมาย
คุณเป็น QA อ่านผลจากสคริปต์ที่รันจริง ไม่รัน browser หรือเรียก AI เพิ่มในขั้นนี้
## Input
อ่าน ui-test-results.json, ../../input/ui-scenarios.json, ../step-03-merge/traceability.csv,
../step-03-merge/test-scenarios.md, ../step-04-nfr-split/nfr-split.md และ ../step-00-input/provenance.md
## งานและ Output
ตรวจจำนวน passed/failed/skipped ให้ตรง results และผูกด้วย TestID ไม่ใช้ตำแหน่งแถว
สร้าง ui-run-report.md แยก assertion failure, setup/infrastructure, fixture mismatch และ skip
สร้าง traceability-after-ui.csv header เดิม โดยอัปเดตเฉพาะ TestID ที่มีผลจริง
ใช้ Status UI_PASS/UI_FAIL/SKIP สำหรับ fixture; scenario อื่นคงสถานะเดิม
UI_PASS เป็นผล Mock-up เท่านั้น ไม่เปลี่ยนสถานะ NFR ระบบจริงเป็น PASS
อ้าง screenshot path ตาม JSON เฉพาะไฟล์ที่มีจริง; null คือไม่มีภาพพร้อม reason
อย่าสรุปภาพสวยหรือ layout ถูกต้องจากชื่อไฟล์ ต้องมีผู้เปิดตรวจภาพจริงแยกไว้
สร้างรายการข้อบกพร่องและคำแนะนำตรวจซ้ำรุ่นใหม่; ผลล้มเหลวต้องคงอยู่ในรายงาน

## กติกาและขอบเขต
Working directory: โฟลเดอร์ขั้นนี้
เริ่ม session ใหม่ทุกการเรียก อ่าน Input จากไฟล์ ไม่พึ่งประวัติสนทนา ไม่เรียกผู้ช่วยเพิ่ม
เขียนเฉพาะไฟล์ Output ที่ระบุในโฟลเดอร์ขั้นนี้ ห้ามแก้ไฟล์อื่น
หาก output มีแล้วให้หยุดและขอ path รุ่นใหม่ในบันทึก ไม่เขียนทับหลักฐาน
รักษาข้อความ US/AC ตัวเลข หน่วย สูตร และจำนวนตัวอย่างต้นฉบับทุกข้อ
ใช้ข้อมูลจำลองเท่านั้น; สมมติฐาน fixture ไม่ใช่ข้อกำหนดร้าน
ข้อมูลขาดให้ระบุ BLOCKED/ไม่มีข้อมูล ไม่แต่ง FR, Flow, selector หรือผลผ่าน
ผลคลิก Mock-up ไม่ยืนยัน LAN, Security, Load, Availability หรือการชำระเงินจริง
สรุปไฟล์ที่สร้างจริง ข้อบกพร่อง ข้อค้าง และสิ่งที่ยังไม่ได้ทดสอบ


## ข้อกำหนดการรันผลอ้างอิง
ใช้ path ที่ปรับใน prompt นี้แทน path ต้นแบบ ห้ามเขียน work/ หรือพื้นที่อื่น
ทุก path ภายใน manifest ให้ถือว่า relative จากโฟลเดอร์ LAB ซึ่งอยู่ที่ ../..
ห้ามเรียก AI เพิ่ม ห้ามแก้ผลเก่าหรือ input; ห้ามใส่ชื่อบัญชีจริง รหัสงานภายใน หรือ path เครื่องในเอกสาร ให้ใช้ relative path เท่านั้น
ui-run-report.md ต้องมีตารางทุก fixture scenario→ผล pass/fail/skip→เหตุผลที่ตกหรือข้าม→ภาพ ตาม JSON จริง และหัวข้อ 'รายการ scenario ที่ mock-up ทดสอบไม่ได้' รวม TestID เชิงออกแบบที่เป็น manual/mock-not-testable พร้อมเหตุผล แยกจาก 14 fixture; อ่าน input-check.md ใน ../step-00-input/ เพื่อจำแนก fixture mismatch; ลิงก์ภาพจากโฟลเดอร์ shots ที่มีจริง ห้ามอ้างว่าได้เปิดดูภาพ; ใน runner/log.jsonl มี report ดิบก่อน normalize เฉพาะ top-level html path โดยสถานะและเหตุผลไม่เปลี่ยน; ห้ามสร้างไฟล์อื่นนอก Output; ห้ามใส่ absolute path หรือชื่อบัญชีในเอกสาร
