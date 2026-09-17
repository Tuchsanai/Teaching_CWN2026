1. ตารางบันทึก Iteration

| Iteration | สิ่งที่เปลี่ยน | C1 | C2 | C3 |
|---|---|---|---|---|
| 1 | สร้างเว็บไซต์ไฟล์เดียว พร้อมข้อมูลสมมติและฟีเจอร์ครบ | PASS — ทดลองครบ 5 ฟีเจอร์ | PASS — Python Playwright ผ่าน ไม่มี console error | PASS — ทุกฟีเจอร์เข้าถึงได้ใน 1–2 คลิก |

หลักฐานจาก CRITIC:

- C1: แสดง 3 ห้อง ดูเวลาว่าง สร้างการจอง ยกเลิกรายการเดียวกัน และเห็นสถานะ “ยืนยันแล้ว → ยกเลิกแล้ว”
- C2: รัน `python critic_test.py` ใน headless Chromium เปิดผ่าน `file://` แบบออฟไลน์ ได้ `console errors=0; page errors=0; network requests=0` และเวลาว่างเปลี่ยน `11 → 10 → 11`
- C3: ทดสอบแต่ละเส้นทางจากหน้าแรกในบริบทเบราว์เซอร์ใหม่ ตามตารางด้านล่าง โดยนับปุ่มยืนยันด้วย

| ฟีเจอร์ | เส้นทางจากหน้าแรก | จำนวนคลิก |
|---|---|---|
| แสดงห้องประชุม | ห้องประชุม → เห็นรายชื่อห้อง | 1 |
| ดูเวลาว่าง | ห้องประชุม → เห็นช่วงว่าง/ไม่ว่าง | 1 |
| สร้างการจอง | ช่วงว่างของห้อง → ยืนยันการจอง | 2 |
| ยกเลิกการจอง | ยกเลิกการจองรายการเริ่มต้น → ยืนยันการยกเลิก | 2 |
| แสดงสถานะ | การจองของฉัน → เห็นสถานะ | 1 |

การนับคลิกไม่นับการเลื่อนหน้า การทดสอบ C2 สร้างแล้วยกเลิกรายการเดียวกันใช้รวม 4 คลิก: จอง 2 และยกเลิก 2

2. ผลงานสุดท้าย

เปิด [output.html](/root/workspace/CWN/Teaching/Basic_AI_WORFLOW/experiments/1_meeting_room/loop/output.html) จากดิสก์เพื่อทดลองได้ทันที มี CSS และ JavaScript ในตัว ไม่ต้องติดตั้งหรือเชื่อมต่อเครือข่าย

หลักฐาน: [critic_test.py](/root/workspace/CWN/Teaching/Basic_AI_WORFLOW/experiments/1_meeting_room/loop/critic_test.py) · [critic-run.log](/root/workspace/CWN/Teaching/Basic_AI_WORFLOW/experiments/1_meeting_room/loop/critic-run.log) · [critic-results.json](/root/workspace/CWN/Teaching/Basic_AI_WORFLOW/experiments/1_meeting_room/loop/critic-results.json) · [trace.md](/root/workspace/CWN/Teaching/Basic_AI_WORFLOW/experiments/1_meeting_room/loop/trace.md)

หยุดที่ Iteration 1 เพราะทุกเกณฑ์ PASS

3. ประเด็นที่ยังเหลือหรือสมมติฐาน

ไม่มีเกณฑ์ค้าง ห้อง ชื่อ ความจุ อุปกรณ์ และรายการเริ่มต้นเป็นข้อมูลสมมติ ผู้ใช้จำลอง 1 คน จองช่วงละ 1 ชั่วโมงระหว่าง 09:00–13:00 น. เริ่มที่วันพรุ่งนี้ตามเวลาเครื่อง ข้อมูลเก็บเฉพาะเบราว์เซอร์ ไม่มีระบบหลังบ้าน