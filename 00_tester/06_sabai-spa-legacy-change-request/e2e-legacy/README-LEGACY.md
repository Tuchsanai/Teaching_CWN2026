# e2e-legacy (สบายใจ สปา) — บันทึกส่งมอบ

ชุดเทสต์ Playwright ของระบบจองคิว ส่งมอบพร้อมระบบ · Playwright 1.63.0 · 12 ไฟล์ 42 TC (UI 36 · API 6)
รายการเคสอยู่ใน `plan-cases.json` (ชื่อ test, tag, ผลที่คาดหวัง ดึงจากไฟล์นี้ · ห้ามลบ)

## รัน

```powershell
# 1) เปิด db ก่อน web (ครั้งแรกต้องสร้าง network ตามชื่อใน db/compose.yaml: docker network create <ชื่อ>)
docker compose -f db/compose.yaml up -d
docker compose -f web/compose.yaml up -d --build      # → http://localhost:4000

# 2) ตรวจกฎร้านแบบเร็ว (API + unit, ไม่ใช้เบราว์เซอร์)
cd web
node scripts/check-rules.mjs                          # ต้องได้ 90 / 90

# 3) e2e
cd ..\e2e-legacy
npm install
npx playwright install chromium                       # ครั้งแรกครั้งเดียว
npx playwright test                                   # project api + chromium (ค่าเริ่มต้น)
npm run test:p1                                       # เฉพาะ @P1
npm run test:all                                      # api + chromium + firefox + webkit
npm run report                                        # เปิดรายงาน html (test-report/html)
```

- เว็บอื่น: `$env:BASE_URL="http://localhost:4000"; npx playwright test`
- รันทีละ test (workers 1) เพราะทุก TC `POST /api/test/reset {now}` ฐานเดียวกัน และบาง TC เลื่อนนาฬิการะบบ · วันที่ล็อกไว้ 10 ต.ค. 2569 10:00
- `/api/health` ต้องตอบ `{"ok":true,"db":true}` ไม่งั้น global-setup หยุดทันที
- log การยิง API ของแต่ละ TC อยู่ที่ `test-report/logs/`

## ผลรันล่าสุด

| ชุด | ผล | เวลา |
|---|---|---|
| `node scripts/check-rules.mjs` | 90 / 90 | ~20 วินาที |
| `npx playwright test` (api + chromium) | 41 passed · 1 failed | ~4 นาที |
| `npm run test:all` | 113 passed · 1 failed | ~13 นาที |

- 3 ข้อติด `test.fail` (KNOWN-ISSUE) นับเป็น passed ตราบใดที่ยังล้ม · ถ้าวันไหนขึ้น "expected to fail but passed" แปลว่ามีคนแก้แล้ว ให้ลบบรรทัด `test.fail` ออก
- TC-SEC-05 แดงค้าง ยังไม่ได้ดู

## หมายเหตุ

- ผูกกับ seed (ผู้ใช้ U01–U08, owner, นัด B05/B06, คอร์ส C01, บัตร SABAI-GC-xxxx) และ `data-testid` · แก้ seed แล้วเทสต์แดงได้
- เงินอ่านจาก `data-amount` · หน้าจองรอ `/api/price` นิ่งก่อนอ่านยอด
- เอกสารอ้างอิงในคอมเมนต์ (TEST-PLAN / TEST-DATA / BR-xx) ไม่ได้ส่งมอบมาด้วย
