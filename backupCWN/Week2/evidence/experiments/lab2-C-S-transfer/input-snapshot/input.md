# ชุด C — โจทย์ถ่ายโอนของร้านใหม่ (fixture สมมติ ไม่ใช่ snapshot รัน AI)
[C-U1] ร้านพร้อมขาย RUNNING version=v2
[C-U2] เปิดหน้าร้านได้ แต่กดจองแล้ว จองไม่สำเร็จ UPDATE_V2_BOOKING_BROKEN
[C-U3] คู่มือระบุรุ่น v1 ก่อนหน้าเคยตรวจการจองผ่าน; log ระบุ UPDATE_APPLIED และ BOOKING_ERROR ไม่มีเหตุอื่น
[C-N1] ยังไม่มีผลหลังแก้ ให้คนเริ่มด้วย ./shop reset transfer-C แล้วตรวจหลักฐานสดก่อนเลือกคำสั่ง
