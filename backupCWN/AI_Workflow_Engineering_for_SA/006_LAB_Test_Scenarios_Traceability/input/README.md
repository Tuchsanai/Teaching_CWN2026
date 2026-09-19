# Input สำหรับ LAB 006

## ที่มาและสิ่งที่ต้องเตรียม

ทำงานจากราก LAB 006 และคัด snapshot ไป work/source/ โดยไม่แก้ LAB ก่อนหน้า
ใช้ fr-nfr-v2.md, flow-v2.md, ui-mockup-v2.html จาก work/ ของ LAB 005
หรือจาก ../../005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/
ถ้าใช้ผลอ้างอิง ต้องเขียน “ใช้ผลอ้างอิง ไม่ใช่ผลที่นักศึกษารันเอง” ใน work/input-source.md
บันทึก path, เวอร์ชัน, hash และเหตุผล; หากไฟล์ยังไม่มีให้หยุดขั้นพึ่งพา ไม่สร้างแทน
plan-v3 ไม่ยืนยันว่ารายงาน/ฟีเจอร์ v3 ถูกสร้างแล้วใน UI v2

## ไฟล์ที่จัดให้

- scenario-template.md: แม่แบบเชิงออกแบบสำหรับทุก AC
- coverage-criteria.md: ตารางตรวจ 26 US และเพดานแก้ 2 รอบ
- ui-scenarios.json: ชุด smoke อัตโนมัติที่กำหนดจากสัญญา ยังไม่ใช่ผลรัน
- ui-v2-test-contract.md: สมมติฐาน selector ใหม่ที่ต้องเทียบ HTML v2 จริง

## รูปแบบ JSON

root เป็น object ที่มี scenarios หรือเป็น array ของ scenario ก็ได้
แต่ละ scenario มี id, us, automation และ steps; automation ที่ไม่ระบุถือเป็น auto
แต่ละ step มี action, testid และ value เมื่อจำเป็น
รองรับ click, fill, expect_text, expect_visible, expect_hidden เท่านั้น
fill กับ native select จะใช้ select_option(value); input/textarea ใช้ fill(value)
expect_text ตรวจข้อความย่อยที่มองเห็นและรอได้ ไม่ใช่ regex หรือข้อความทั้งหน้าจอ
expect_hidden ผ่านได้ทั้ง element ซ่อนและไม่มีใน DOM จึงต้องตรวจ precondition ให้ครบ
click ไม่เลือก .first() อัตโนมัติ; selector ที่ซ้ำจะ fail เพื่อไม่ซ่อนความกำกวม
ทุก scenario เปิด context ใหม่และเริ่มด้วย btn-reset; ไม่พึ่งผลของกรณีก่อนหน้า
เมื่อ step ผิดให้หยุด steps ที่พึ่งพากัน แต่รัน scenario ถัดไปจนครบ
ทุกกรณีที่เปิด page ได้จะพยายามถ่ายภาพ; skip/เปิด browser ไม่ได้จะมี screenshot=null พร้อม reason
ผลรันเป็น JSON ที่มี results, passed, failed, skipped; ไม่ให้ skip เป็น pass
--allow-fail ใช้เพื่อเก็บผลครบในกิจกรรมเท่านั้น ต้องอ่าน failed จริงเสมอ
สคริปต์ไม่เขียนทับรายงาน/ภาพเดิม ให้เปลี่ยน --out และ --shots ทุกครั้ง
ค่า timeout 2500 ms เป็นเวลารอเครื่องมือ ไม่ใช่การเปลี่ยน AC

## ขอบเขตและสมมติฐาน

ใช้ fixture สัญญา LAB 004: m01=50, ไข่=10, m02=55 และข้อมูล login จำลอง
สิ่งที่ไม่รองรับด้วยห้า action เช่นอัปโหลดไฟล์/หลายอุปกรณ์ ให้เขียน manual หรือ mock-not-testable
NFR, การติดตั้ง, LAN, สิทธิ์ฝั่ง server และธุรกรรมเงินจริงต้องมีแผนตรวจระบบจริง
US แต่ละข้อใน suite ถูกตรวจเพียงบางส่วน ห้ามสรุปว่าผ่านทั้ง US จาก smoke หนึ่งกรณี
ไม่มีการรัน Prompt นักศึกษาหรือ UI v2 ล่วงหน้าในชุดเนื้อหานี้
