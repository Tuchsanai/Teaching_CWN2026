# ขั้น 6.3 — รวม Test Scenarios และ Traceability
## บริบทและเป้าหมาย
คุณเป็นผู้รวมงานหลัง fan-in ให้ Developer/QA ตามรอยได้โดยไม่กลบช่องว่าง
## Input
อ่าน ../step-02-coverage/selected-set.md ที่ระบุ manifest และรายงาน coverage รอบที่เลือก
อ่านไฟล์ตาม manifest, ../step-00-input/fr-nfr-v2.md, ../step-00-input/flow-v2.md,
../step-00-input/ui-mockup-v2.html, ../../input/ui-scenarios.json และ ../../../docs/case-study-source.md
## งาน
รวม scenario สามบทบาท รักษารหัสและ AC เดิม ห้ามถือเสียงส่วนใหญ่แทนหลักฐาน
เชื่อม fixture TS-<US>-101 ขึ้นไปกับ scenario เชิงออกแบบ ไม่อ้างว่า fixture ครบ AC
ตรวจทุก US อย่างน้อยหนึ่งแถว และทุก TestID เชื่อม FR/Flow/Screen ที่มีจริง
หาก mapping ไม่มี ให้ใช้ MISSING พร้อมข้อบกพร่องในรายงาน ห้ามแต่ง FR ID
หนึ่งความสัมพันธ์ต่อแถว; กรณีหลาย FR/Flow ให้เพิ่มแถวด้วย TestID เดิม ไม่ยัด CSV ผิดรูปแบบ
## Output
สร้าง test-scenarios.md และ traceability.csv แบบ UTF-8 ผ่าน csv writer
CSV header ต้องเป็น US,FR,Flow,Screen,TestID,Scenario,Status ตามลำดับ
Status เริ่ม NOT_RUN, MANUAL_PENDING หรือ MOCK_NOT_TESTABLE ตาม automation
เพิ่ม traceability-notes.md บอกข้อขัดแย้ง จุดขาด และความหมาย Status
ผล COVERED คือเอกสารออกแบบครบ ไม่ใช่ PASS; ผล UI จะผูกจาก JSON ในขั้น 6.5

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
รวมเนื้อหา scenario ฉบับเต็มลง test-scenarios.md ไม่ใช่แค่ลิงก์ออกไป; ทุก US ต้องมี >=2 scenario เชิงออกแบบโดยรักษา ID เดิมและมีสำเร็จ+ผิดพลาด/ข้อยกเว้น ห้ามแก้เนื้อหา source เอง; เก็บข้อค้างตามผู้ตรวจ Coverage; CSV ต้องผ่าน csv.DictReader; ให้ summary ใช้ path relative เท่านั้น
ใช้การอ่านไฟล์และรวมด้วยสคริปต์ในหน่วยความจำเพื่อรักษาบล็อก scenario เดิมโดยครบถ้วน ไม่ต้องพิมพ์เนื้อหาเดิมทั้งไฟล์ซ้ำในคำตอบ; ห้ามสร้างไฟล์สคริปต์เครื่องมือในโฟลเดอร์
ปรับลิงก์และฐาน path ของเอกสารรวมให้ใช้ได้จาก step-03-merge/ และ final/ ซึ่งอยู่ระดับเดียวกัน โดยคงเนื้อหา AC/ID/ขั้น/expected/ข้อค้างเดิม; อ้าง source ต่อบทบาทชัดเจน ใช้ csv writer และตรวจ fieldnames/ทุกUS/ทุกID ก่อนจบ
