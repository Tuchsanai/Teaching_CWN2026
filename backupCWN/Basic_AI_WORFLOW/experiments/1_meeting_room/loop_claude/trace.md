# trace.md — ระบบจองห้องประชุม (GENERATOR / CRITIC loop)

## Iteration 1 — 2026-09-16
**GENERATOR — สิ่งที่เปลี่ยน:** สร้าง `output.html` ไฟล์เดียว (inline CSS/JS, ไม่มี URL ภายนอก) 3 ส่วน: (1) รายการห้องประชุม 3 ห้อง + ปุ่ม "ดูเวลาว่าง", (2) ตารางช่วงเวลา 7 ช่อง (เขียว=ว่าง/แดง=จองแล้ว) คลิกช่องว่างเปิดฟอร์มจอง, (3) ตารางสถานะการจอง (badge จองแล้ว/ยกเลิกแล้ว) พร้อมปุ่ม "ยกเลิกการจอง"

**CRITIC — คำตัดสิน (หลักฐานจาก `python3 critic_test.py`, headless Chromium):**
- C1: **PASS** — โค้ดมีครบ 5 ฟีเจอร์: renderRooms (แสดงห้อง), renderSlots (เวลาว่าง), confirmBooking (จอง), cancelBooking (ยกเลิก), renderBookings (สถานะ); ผลรัน F1_rooms_visible: 3, F2_free_slots: 7, F3_message: "จองสำเร็จ รหัส BK001", F4_message: "ยกเลิกการจอง BK001 แล้ว", F5_badge_before/after: "จองแล้ว" → "ยกเลิกแล้ว"
- C2: **PASS** — console_errors: [] ; ลำดับคลิกจริง: ดูเวลาว่าง(ห้อง A) → ช่อง 10:00-11:00 → ยืนยันการจอง → slot เป็น busy, แถว BK001 data-status=confirmed → คลิกยกเลิกการจอง → data-status=cancelled, slot กลับเป็น free, ปุ่มยกเลิกหายไป (F4_cancel_button_gone: True); OVERALL: PASS
- C3: **PASS** — F1 แสดงห้อง: 0 คลิก (หน้าแรก) | F2 ดูเวลาว่าง: 1 คลิก (ปุ่ม "ดูเวลาว่าง") | F3 จองห้อง: 2 คลิก (ปุ่ม "ดูเวลาว่าง" → ช่องเวลาสีเขียว เปิดฟอร์ม) | F4 ยกเลิก: 1 คลิก (ปุ่ม "ยกเลิกการจอง" ในตาราง) | F5 สถานะการจอง: 0 คลิก (ตารางในหน้าแรก)

**ผล:** ทุกเกณฑ์ PASS → หยุด
