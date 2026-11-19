# FOLLOW-UPS · receiptdesk (B03 โมดูลกติกา Business Rule)

run: `receiptdesk-20261119-115927` · ขอบเขตการตรวจใหม่ของ B03: ผ่านเมื่อกรณีทดสอบ Business Rule ทุกข้อใน `docs/TEST-DATA.md` ผ่านครบ และไม่ขัดกับ Requirement ข้อใด
ข้อด้านล่างผู้ตรวจพบ แต่อยู่นอกขอบเขตนี้ จึงไม่ใช้ตัดสินว่าไม่ผ่าน (จดไว้ทำภายหลัง)

| # | ระดับ | ข้อที่พบ | ไฟล์ | ผู้ตรวจ · รอบ |
|---|---|---|---|---|
| 1 | ต่ำ | BR-03: ตัวอ่าน PDF ยังไม่นับ `\x00` เป็นช่องว่าง (ISO 32000-1 §7.2.2) จึงปฏิเสธ PDF หน้าเดียวรูปแบบ `/Type % comment\n\x00/Page` ด้วย `422 pdf_pages` | `app/web/lib/rules.ts` | cyolo1 · resume 1 r3 และ resume 2 r1 |
| 2 | ต่ำ | BR-03: คำว่า `trailer` ที่อยู่ในสตริงของ PDF เช่น `(trailer << /Encrypt 9 0 R >>)` ถูกตีความเป็น trailer จริง ทำให้ไฟล์ถูกมองว่าเข้ารหัสและถูกปฏิเสธ | `app/web/lib/rules.ts` | cyolo1 · resume 1 r3 และ resume 2 r1 |
| 3 | กลาง | BR-13: ข้อมูลตั้งต้น TD-BR13-b เก็บเป็น `reset_at − 120 นาที` เมื่อเวลาผ่านไปหลังรีเซ็ตเพียง 1 มิลลิวินาที รายการค้างจะเพิ่มจาก 1 เป็น 2 ใบ การรีเซ็ต (B02) และการทดสอบ end-to-end (B14) ควรใช้เวลาอ้างอิงเดียวกัน | `app/web/db/schema.sql` · `TEST.md` | cyolo1 · รอบแรก r3 |
| 4 | ต่ำ | BR-07/BR-10 (7 กรณีใน TEST-DATA §6) ทดสอบผ่านแบบจำลองอ้างอิงใน `rules.ts` เท่านั้น ยังต้องยืนยันกับ gateway และ GPU Worker จริง | `app/ai/gateway/main.py` · `app/ai/worker/worker.py` | cyolo1 · รอบแรก r1 และ resume 1 |
