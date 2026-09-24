| # | สถานะก่อนทำ | action (คำสั่ง) | ผลที่เห็นจริง | ไฟล์หลักฐาน | elapsed (s) |
|---|---|---|---|---|---|
| 0 | - | คำนวณวันที่ | RUN_DATE=2026-09-24 DEPART=2026-09-27 RETURN_SEARCH=2026-10-01 | dates.env | 0 |
| 1 | ไม่มี session | `open https://www.trip.com/ --idle-timeout=0` | redirect ไป verify.trip.com (CAPTCHA) | 01-home.png/.yml | see commands.log |
| 1a | CAPTCHA | รอ ~8 s แล้ว snapshot 1 ครั้ง | ยังเป็นหน้า verification → WAITING_FOR_HUMAN | 02-verify-recheck.png/.yml | see commands.log |
| 1b | CAPTCHA | human แก้ verification เอง (WAIT_END ใน human-wait.log, รอ 554.33 s) | - | human-wait.log | human_wait |
| 2 | หลัง human แก้ | snapshot + screenshot (ไม่ open/goto/reload) | หน้าแรก th.trip.com ภาษาไทย THB | 03-resume.png/.yml | see commands.log |
| 3 | หน้าแรก | click tab "เที่ยวบิน" (f4e183), click cookie "ปฏิเสธทั้งหมด" (f4e664) | ฟอร์มเที่ยวบิน ไป-กลับ ผู้ใหญ่ 1 คน ชั้นประหยัด (default) | 04-flight-tab.png/.yml, 05-origin-open.yml | see commands.log |
| 4 | ฟอร์มเที่ยวบิน | click origin combobox, fill "Bangkok", click "กรุงเทพ · ทุกสนามบิน" (BKK+DMK) | ต้นทาง กรุงเทพ สนามบินทั้งหมด | 06-origin-typed.png/.yml, 07-origin-set.yml | see commands.log |
| 5 | ต้นทางตั้งแล้ว | click dest combobox, fill "Tokyo", click "โตเกียว · ทุกสนามบิน" (NRT+HND) | ปลายทาง โตเกียว สนามบินทั้งหมด | 08-dest-open.yml, 09-dest-typed.yml, 10-dest-set.png/.yml | see commands.log |
| 6 | ปลายทางตั้งแล้ว | click วันออกเดินทาง, click "วันอาทิตย์ 27 กันยายน 2026", click "วันพฤหัสบดี 1 ตุลาคม 2026" | อา. 27 ก.ย. — พฤ. 1 ต.ค. | 11-calendar.png/.yml, 12-depart-picked.yml, 13-dates-set.png/.yml | see commands.log |
| 7 | ฟอร์มครบ | click "ค้นหา" (f4e749) | URL showfarefirst?dcity=bkk&acity=tyo&ddate=2026-09-27&rdate=2026-10-01&triptype=rt&class=y&quantity=1 → **HTTP 432 "whaleguard block"** → WAITING_FOR_HUMAN | 14-flight-results.png/.yml (yml ว่าง) | see commands.log |
| 8 | whaleguard wait | user asked for a retry (wait closed as not solved), tab-new homepage, redid the UI search | whaleguard block again, WAITING_FOR_HUMAN | retry-watch/steps.md, retry-watch/15-flight-results.* | see retry-watch/commands.log |
