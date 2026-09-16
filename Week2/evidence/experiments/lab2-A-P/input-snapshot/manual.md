# คู่มือคำสั่งร้านฝึก — ใช้เหมือนกันทั้ง Prompt และ Skill
บริการคือโปรแกรมที่รอรับคำขอจากหน้าเว็บ; รุ่นคือชุดพฤติกรรมของโปรแกรม; rollback คือกลับรุ่นก่อนที่ตรวจแล้วว่าดี; logs คือบันทึกเหตุการณ์
งาน AI ในการทดลองเป็นการวินิจฉัยจากภาพสถานะ ผู้ใช้เป็นคนเลือกและรันคำสั่ง ไม่ใช่ AI ปฏิบัติเอง
คำสั่งพร้อมใช้จากโฟลเดอร์ Week2:
| คำสั่ง | ใช้เมื่อ / ความหมาย | ผลที่ควรเห็น |
|---|---|---|
| ./shop preflight | ก่อนเริ่ม ตรวจ Python และพอร์ต | PREFLIGHT OK และ URL หรือเหตุขัดข้อง |
| ./shop open | ต้องการเปิดเว็บ คัดลอก URL ที่พิมพ์ไป browser | URL http://127.0.0.1:พอร์ต |
| ./shop status | ดูว่าบริการตอบจริงและรุ่นใด | STOPPED หรือ RUNNING version=v1/v2 |
| ./shop logs | อ่านเหตุการณ์รอบปัจจุบัน | EVENT พร้อม UTC, version, booking หรือ error |
| ./shop start | บริการหยุดและควรใช้รุ่นปัจจุบัน | STARTED version=v1; หากทำซ้ำ ALREADY RUNNING; ไม่แก้ v2 |
| ./shop rollback | v2 ยังเปิดเว็บได้แต่จองไม่ได้ และมี v1 ที่ดี | ROLLED BACK version=v1; บน v1 แจ้ง ALREADY v1 |
| ./shop check | ตรวจทั้งหน้าเว็บและการจองผ่าน endpoint จริง | CHECK PASS booking=... version=v1 หรือ CHECK FAIL; ต้องตรวจ browser เพิ่ม |
| ./shop reset basic-A | เริ่มรอบฝึกบริการหยุดชุด A ล้างเฉพาะรายการฝึก | RESET basic-A STOPPED version=v1 |
| ./shop reset basic-B | เริ่มรอบฝึกบริการหยุดชุด B | RESET basic-B STOPPED version=v1 |
| ./shop reset advanced-A | เริ่มรอบอัปเดตเสียชุด A มีสาเหตุเดียวคือ v2 จองไม่ได้ | RESET advanced-A RUNNING version=v2 |
| ./shop reset advanced-B | เริ่มรอบอัปเดตเสียชุด B | RESET advanced-B RUNNING version=v2 |
| ./shop reset transfer-C | เริ่มรอบถ่ายโอน ร้านใหม่แต่สาเหตุ v2 เดิม | RESET transfer-C RUNNING version=v2 |
| ./shop stop | จบงาน หยุดเฉพาะร้านฝึกนี้ | STOPPED |
ห้าม reset ระหว่างกำลังกู้เพื่อทำให้ผลดูผ่าน ห้ามแก้ไฟล์ภายใน ใช้คำสั่งตามตารางเท่านั้น
หลังเลือกคำสั่งกู้: status → check → open → ปุ่ม จองสินค้า → ต้องเห็นเลขจองและรุ่น v1; จดเลขจริง ไม่ใช้ตัวอย่างในคู่มือ
หากยังไม่ผ่าน: เก็บ logs หยุดและแจ้งผู้สอน อย่าลองหลายคำสั่งที่ไม่เกี่ยว
ข้อมูลสมมติ ไม่มีจ่ายเงินจริง เวลาเครื่อง 240 วินาทีต่อร่าง; ภารกิจกู้คืนของผู้เรียน 30 นาทีแยกจาก setup
