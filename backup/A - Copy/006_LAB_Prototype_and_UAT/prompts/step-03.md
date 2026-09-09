โฟลเดอร์งานคือ /root/workspace/sa-work/006/ (สร้างถ้ายังไม่มี) เก็บทุกไฟล์ที่นี่ ห้ามแก้ไฟล์ใน /root/workspace/sa-labs/
อ่าน /root/workspace/sa-work/006/requirements.md และ /root/workspace/sa-work/006/index.html จากขั้นก่อน ถ้าไม่มีให้แจ้งชื่อแล้วหยุด ห้ามแต่งเอง
B01 “ออกแบบบริการด้วย AI” 3 ที่/เริ่มว่าง; B02 รหัส `<LEARNER_A>`–`<LEARNER_D>`; B03 ว่าง/ซ้ำไม่รับ จองแล้วรายการเพิ่ม/ที่ลด; B04 ครบ 3 ไม่รับ D/เหลือ 0; B05 ยกเลิก B แล้วรับ D; B06 refresh คงข้อมูล; B07 เริ่มใหม่ล้าง; B08 375px ไม่ล้น ใช้ keyboard/focus; B09 สถานะไทย
ขอบเขต: browser เดียว ไม่มี backend หรือ production

ตรวจเอกสารว่า requirements.md และ index.html ครบ B01–B09 หรือไม่
ทดสอบ http://172.17.0.3:8080/ ของ container ถ้ามี Playwright ให้รัน UAT-01–09 และเก็บ console/page errors; ถ้าไม่มี/เข้าไม่ได้ให้ SKIP พร้อมเหตุผล ห้ามแต่งผล
ยืนยัน UAT-04=A/B/C, 3 รายการ, เหลือ 0; 05 ปฏิเสธ D; 06 ยกเลิก B แล้วได้ A/C/D; 07 refresh แล้วยัง A/C/D; 09 scrollWidth ≤ clientWidth ที่ 375px
สร้าง /root/workspace/sa-work/006/uat-results.md มี ID, ทำจริง, expected, actual, PASS/FAIL/SKIP, หลักฐาน แยกเอกสาร/browser
ห้ามแก้ index.html; ถ้าพบปัญหาให้ FAIL เพื่อส่งกลับผู้สร้าง ห้ามอ่านหรือค้นหาไฟล์ README ของ LAB เพื่อหาเฉลย
ถ้ามีเพียง CLI เดียว ให้ใช้ตัวเดิมและใส่ป้าย `SIMULATION` ในไฟล์ผล
ทำเฉพาะขั้นนี้ เมื่อเสร็จให้แสดงเนื้อหาสำคัญของไฟล์ที่สร้าง (ไม่ใช่แค่ชื่อไฟล์) บนหน้าจอเป็นตาราง/รายการที่ฉันอ่านตรวจได้ แล้วหยุดรอ ห้ามทำขั้นถัดไปเอง
