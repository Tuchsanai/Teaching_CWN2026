# BUGS.md — เฉลยบั๊กสำหรับฝึกหา (สำหรับผู้สอนเท่านั้น)

บั๊กทั้ง 3 ตัวจะเกิด **เฉพาะเมื่อ** รัน web ด้วย `BUG_MODE=1` เท่านั้น (ค่าเริ่มต้น `0` = ระบบถูกต้องทุกข้อ)
ตรวจโหมดได้จาก `<html data-bug-mode="1">`

```powershell
# เปิดโหมดบั๊ก
cd spa
$env:BUG_MODE = "1"; docker compose up -d --force-recreate web
# กลับเป็นโหมดปกติ
$env:BUG_MODE = "0"; docker compose up -d --force-recreate web
Remove-Item Env:BUG_MODE
```

| # | บั๊ก | กฎที่ผิด | ไฟล์ / ฟังก์ชัน | โหมดปกติ | โหมดบั๊ก |
|---|---|---|---|---|---|
| 1 | ยอดสะสม ฿10,000 พอดี ยังเป็น Silver | BR-13 | `lib/server/auth.ts` → `tierOf()` | `spent >= 10000` → Gold | `spent > 10000` → ฿10,000 พอดียังเป็น Silver (฿10,001 ขึ้นไปจึงเป็น Gold) |
| 2 | จองนักบำบัดเวลาทับกันได้ | BR-04, FR-02, NFR-06 | `lib/server/booking.ts` → `assign()` (ฟังก์ชัน `taken`) | นักบำบัดที่มีคิวทับเวลา → "เวลานี้ถูกจองแล้ว" | ไม่ตรวจคิวของนักบำบัดเลย จองคนเดิมเวลาเดิมซ้ำได้ (หน้าจองก็แสดงรอบว่าง) · ห้อง Couple Suite ยังตรวจตามปกติ |
| 3 | จองด้วยคอร์สแล้วจำนวนครั้งไม่ลด | BR-16, FR-13 | `lib/server/booking.ts` → `createBooking()` (`courseStep`) | จองด้วยคอร์ส → `used_sessions + 1` | `used_sessions + 0` → Wallet ยังแสดง "เหลือ 7 จาก 11 ครั้ง" หลังจอง |

## วิธีทดสอบให้เจอ (ตัวอย่าง)

1. **บั๊ก 1** — `POST /api/test/reset` แล้ว `POST /api/test/user {"email":"new@sabai.test","totalSpent":10000}` → login `new@sabai.test` → หน้า `/account` ควรเป็น `Gold` (`data-testid="member-tier"` มี `data-tier="gold"`) แต่โหมดบั๊กได้ `silver`
2. **บั๊ก 2** — จอง `thai-massage` นักบำบัด 1 วันที่ +2 เวลา 14:30 (seed มีคิว 14:00–15:00 อยู่แล้ว) → ควรได้ `booking-error` = "เวลานี้ถูกจองแล้ว" แต่โหมดบั๊กจองสำเร็จ
3. **บั๊ก 3** — login `nida@sabai.test` → `/wallet` เห็น "เหลือ 7 จาก 11 ครั้ง" → จอง `body-contouring` แบบ "จองด้วยคอร์ส" → กลับมาที่ `/wallet` ควรเป็น "เหลือ 6 จาก 11 ครั้ง" แต่โหมดบั๊กยังเป็น 7
