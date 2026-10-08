Claude สร้างหุ่นยนต์ทดสอบเสร็จใน **ประมาณ 5 นาที** และลอง 2 test ก่อน

| เช็ก | ผล |
|---|---|
| Node · ffmpeg · `/api/health` | ✅ v26.7.0 · 8.0.1 · `{"ok":true,"db":true}` |
| `npx playwright test` (2 test × 3 เบราว์เซอร์) | ✅ **6/6 passed** (chromium 2 · firefox 2 · webkit 2) |
| `npm run test:gif` | ✅ `TC-HOME-01.gif` + `TC-HOME-01.mp4` (TC-API-01 เรียก API อย่างเดียว เก็บเป็นไฟล์ `.log` แทน) |
| `CLAUDE.md` | ✅ คู่มือ: เปิดเว็บ · สลับ BUG_MODE · วิธีเขียน test ใหม่ |

| ไฟล์ | ทำหน้าที่อะไร |
|---|---|
| `e2e/playwright.config.ts` | 3 เบราว์เซอร์ · ภาษาไทย · เวลาไทย · โหมด GIF อัดวิดีโอช้า ๆ |
| `e2e/global-setup.ts` | เช็กว่าเว็บเปิด แล้วรีเซ็ตข้อมูล + ล็อกวันที่ `2026-10-08 10:00` **ครั้งเดียว** |
| `e2e/tests/fixtures.ts` | ตัวช่วย: เปิดหน้า · login · สร้างสมาชิกใหม่ · ป้ายชื่อ test + วงแดงตรงจุดคลิก |
| `e2e/reporters/tester-report.ts` | วิดีโอ → **GIF + MP4** และเขียน **TEST-REPORT.md** แบบ tester |

⚠️ **เจอจริง:** npm ติดตั้ง Playwright รุ่นใหม่กว่าเบราว์เซอร์ในเครื่อง ทำให้ Firefox / WebKit เปิดไม่ขึ้น Claude จึงล็อกรุ่นให้ตรงกัน (`1.63.0`) ถ้าเจอแบบนี้ใช้พรอมต์ในตาราง "ถ้าเจอปัญหา"
