| # | สถานะก่อนทำ | action (คำสั่ง) | ผลที่เห็นจริง | ไฟล์หลักฐาน | elapsed (s) |
|---|---|---|---|---|---|
| 0 | - | คำนวณวันที่ | RUN_DATE=2026-09-24 DEPART=2026-09-27 RETURN_SEARCH=2026-10-01 | dates.env | 0 |
| 1 | ไม่มี session | `open https://www.trip.com/ --idle-timeout=0` | redirect ไป verify.trip.com (CAPTCHA) | 01-home.png/.yml | see commands.log |
| 1a | CAPTCHA | รอ ~8 s แล้ว snapshot 1 ครั้ง | ยังเป็นหน้า verification → WAITING_FOR_HUMAN | 02-verify-recheck.png/.yml | see commands.log |
