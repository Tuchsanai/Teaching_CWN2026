# ขั้น 6.3 — รวม Test Scenarios และ Traceability
## บริบทและเป้าหมาย
คุณเป็นผู้รวมงานหลัง fan-in ให้ Developer/QA ตามรอยได้โดยไม่กลบช่องว่าง
## Input
อ่าน work/selected-set.md ที่ระบุ manifest และรายงาน coverage รอบที่เลือก
อ่านไฟล์ตาม manifest, work/source/fr-nfr-v2.md, work/source/flow-v2.md,
work/source/ui-mockup-v2.html, input/ui-scenarios.json และ ../docs/case-study-source.md
## งาน
รวม scenario สามบทบาท รักษารหัสและ AC เดิม ห้ามถือเสียงส่วนใหญ่แทนหลักฐาน
เชื่อม fixture TS-<US>-101 ขึ้นไปกับ scenario เชิงออกแบบ ไม่อ้างว่า fixture ครบ AC
ตรวจทุก US อย่างน้อยหนึ่งแถว และทุก TestID เชื่อม FR/Flow/Screen ที่มีจริง
หาก mapping ไม่มี ให้ใช้ MISSING พร้อมข้อบกพร่องในรายงาน ห้ามแต่ง FR ID
หนึ่งความสัมพันธ์ต่อแถว; กรณีหลาย FR/Flow ให้เพิ่มแถวด้วย TestID เดิม ไม่ยัด CSV ผิดรูปแบบ
## Output
สร้าง work/test-scenarios.md และ work/traceability.csv แบบ UTF-8 ผ่าน csv writer
CSV header ต้องเป็น US,FR,Flow,Screen,TestID,Scenario,Status ตามลำดับ
Status เริ่ม NOT_RUN, MANUAL_PENDING หรือ MOCK_NOT_TESTABLE ตาม automation
เพิ่ม work/traceability-notes.md บอกข้อขัดแย้ง จุดขาด และความหมาย Status
ผล COVERED คือเอกสารออกแบบครบ ไม่ใช่ PASS; ผล UI จะผูกจาก JSON ในขั้น 6.5

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
