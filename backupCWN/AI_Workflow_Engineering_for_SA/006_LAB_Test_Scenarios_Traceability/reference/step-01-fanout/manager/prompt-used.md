# ขั้น 6.1 — สร้าง Scenario บทบาทผู้จัดการร้าน
## บริบทและเป้าหมาย
คุณเป็นผู้ออกแบบการทดสอบบทบาทผู้จัดการร้าน ใน Static Graph; รับผิดชอบ US-19 ถึง US-26
## Input
อ่าน ../../../../docs/case-study-source.md, ../../../../docs/data-issues.md, ../../step-00-input/input-check.md,
../../step-00-input/fr-nfr-v2.md, ../../step-00-input/flow-v2.md, ../../step-00-input/ui-mockup-v2.html,
../../../input/scenario-template.md, ../../../input/coverage-criteria.md, ../../../input/ui-scenarios.json,
../../../input/ui-v2-test-contract.md และ ../../../../004_LAB_Conditional_Graph_UI_Mockup/input/ui-contract.md
## งาน
สร้าง scenario จากแต่ละ clause ของ AC ไม่เริ่มจากการเดาว่าหน้า UI ทำอะไรได้
ทุก US ในขอบเขตต้องมีอย่างน้อย 1 สำเร็จ และ 1 ผิดพลาด/ข้อยกเว้น
ใช้รหัส TS-<US>-<n> เช่น TS-US-01-1; n ไม่ซ้ำภายใน US และห้ามเปลี่ยน ID หลังเผยแพร่
ช่วง n=101 ขึ้นไปสงวนให้ fixture ../../../input/ui-scenarios.json ให้อ้างเชื่อม ไม่สร้างซ้ำ
คัด AC ต้นฉบับครบพร้อมตัวเลขเดิมก่อนแยก functional assertions กับ NFR
ระบุ precondition, test data จำลอง, steps, expected, ประเภท, automation: auto/manual/mock-not-testable
ระบุ data-testid ที่ใช้และ scope; selector ซ้ำต้องชี้รายการโดย order ID หรือใช้ fixture ที่มีใบเดียว
auto หมายถึงรันกับ Mock-up ได้ ไม่หมายความว่า AC ระบบจริงผ่านแล้ว
manual ใช้เมื่อมีขั้นตรวจด้วยคน; mock-not-testable ใช้เมื่อจำเป็นต้องมีระบบจริง
US ที่ UI v2 ยังไม่มีต้องออกแบบ scenario ต่อ แต่ระบุเหตุที่ยังรันไม่ได้
กรณีผิดพลาดที่ต้นฉบับไม่กำหนดผลชัด ให้แยกเป็นสมมติฐานรอยืนยัน ไม่เพิ่มกฎเอง
ข้ามบทบาทได้ใน steps เพื่อ setup แต่เจ้าของ US ยังคงตามขอบเขตนี้
## Output
สร้าง scenarios-manager.md ตาม template พร้อมดัชนี US -> TestID และข้อค้าง
Status เริ่ม NOT_RUN หรือ NOT_TESTABLE ไม่ใส่ PASS โดยไม่มีผลรันจริง

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
ทุก path ภายใน manifest ให้ถือว่า relative จากโฟลเดอร์ LAB ซึ่งอยู่ที่ ../../..
ห้ามเรียก AI เพิ่ม ห้ามแก้ผลเก่าหรือ input; ห้ามใส่ชื่อบัญชีจริง รหัสงานภายใน หรือ path เครื่องในเอกสาร ให้ใช้ relative path เท่านั้น
อ่าน snapshot ui-contract-v2.md และ test-outline-v2.md เพิ่มได้จาก ../../step-00-input/ เพื่อยืนยัน selectors v2; ห้ามนำข้อความเหตุผลภายในหรือชื่อเครื่อง/บัญชีจาก log มาใส่เอกสาร
