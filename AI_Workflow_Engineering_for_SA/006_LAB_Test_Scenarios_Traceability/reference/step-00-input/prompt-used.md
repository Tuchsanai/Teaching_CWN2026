# ขั้น 6.0 — ตรวจ Input และที่มา
## บริบทและเป้าหมาย
คุณเป็น SA เตรียม snapshot สำหรับสร้าง Test Scenarios จาก UI v2 ของครัวคุณยาย
## Input
อ่าน provenance.md, fr-nfr-v2.md, flow-v2.md,
ui-mockup-v2.html, ../../../docs/case-study-source.md, ../../../docs/data-issues.md,
../../input/README.md, ../../input/ui-v2-test-contract.md และ ../../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md
## งานและ Output
ตรวจไฟล์ครบและบันทึก hash/ที่มา/รุ่น/การใช้ผลอ้างอิงใน input-check.md
ตรวจ selector เดิมและส่วนขยาย v2 จาก HTML โดยไม่อ้างว่าคลิกผ่าน
ถ้า selector v2 ต่าง ให้ระบุ mapping ที่พบจริงและรายการยังขาด ไม่เปลี่ยนต้นทาง
แยก plan-v3 จากสิ่งที่ทำจริงใน UI v2; รายงานที่เพียง planned ยัง NOT_TESTED
สร้าง scenario-set-round-0.json เป็น object role -> path:
customer -> ../step-01-fanout/customer/scenarios-customer.md
kitchen-front -> ../step-01-fanout/kitchen-front/scenarios-kitchen-front.md
manager -> ../step-01-fanout/manager/scenarios-manager.md
manifest นี้เป็นรายการ output ที่คาดหวัง ไม่ใช่การรับรองว่าทั้งสามไฟล์มีแล้ว
หยุดขั้นถัดไปถ้า Input จำเป็นขาด; อย่าสร้าง UI หรือผล LAB 005 แทน

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
สร้าง input-check.md จากการอ่านจริงและตรวจ SHA-256 ตรวจ selector ด้วยการอ่าน HTML เท่านั้น ยังไม่รัน browser; manifest ใช้ path relative จาก LAB ตาม provenance
