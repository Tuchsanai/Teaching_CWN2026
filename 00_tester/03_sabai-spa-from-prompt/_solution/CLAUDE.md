# CLAUDE.md — สบายใจ สปา + ชุดทดสอบ Playwright

## โครงสร้างโฟลเดอร์

```
03_sabai-spa-from-prompt/
├─ REQUIREMENTS.md, USER-STORIES.md   ความต้องการ (FR / BR / NFR / US)
├─ TEST-PLAN.md                       แผนทดสอบ: รหัส TC-xxx, โมดูล, ระดับ P1–P3, ผลที่คาดหวัง, เกณฑ์ผ่าน
├─ spa/                               เว็บที่ถูกทดสอบ (Next.js + PostgreSQL ใน Docker) — ห้ามแก้โค้ดในนี้
│  └─ SPEC.md                         หน้าเว็บ, data-testid, ข้อความ error, API — แหล่งอ้างอิงเดียวของ selector
└─ e2e/                               โปรเจกต์ Playwright (TypeScript)
   ├─ package.json                    scripts: test, test:gif, report
   ├─ playwright.config.ts            chromium / firefox / webkit · 1280x800 · th-TH · Asia/Bangkok · GIF=1 → อัดวิดีโอ + slowMo 650 (chromium)
   ├─ global-setup.ts                 เช็ก /api/health แล้ว POST /api/test/reset {now: 2026-10-08T10:00:00+07:00} ครั้งเดียว
   ├─ tests/fixtures.ts               test (ป้ายชื่อ + วงแดงตรงจุดคลิก + ค้างเฟรมท้าย ในโหมด GIF), open(), loginByApi(), createUser(), bookingDate(), ApiLog
   ├─ tests/ready.setup.ts            project "setup": เช็กว่าเว็บพร้อม (ไม่ reset) — มีไว้ให้ time-travel รันเป็น teardown
   ├─ tests/NN-<โมดูล>.spec.ts         test case ตาม TEST-PLAN.md (01-home … 13-mobile) รันขนานบน chromium / firefox / webkit
   ├─ tests/90-time-travel.serial.spec.ts  TC ที่ต้องย้ายเวลาเว็บ (TC-BOOK-03, TC-MEM-04, TC-DASH-02) — project "time-travel" รันทีละข้อบน chromium หลัง 3 เบราว์เซอร์จบ แล้ว reset กลับ R0
   ├─ reporters/tester-report.ts      วิดีโอ → test-report/gifs/<TC>.gif + videos/<TC>.mp4 (ffmpeg) และเขียน test-report/TEST-REPORT.md
   └─ test-report/                    ผลลัพธ์: TEST-REPORT.md, gifs/, videos/, logs/, failures/
```

## เปิดเว็บ (PowerShell)

```powershell
cd spa
docker compose up -d --build          # เปิดแบบปกติ (BUG_MODE=0)
curl.exe http://localhost:3000/api/health   # ต้องได้ {"ok":true,"db":true}

# เปิดโหมดฝังบั๊กสำหรับฝึก
$env:BUG_MODE = "1"; docker compose up -d --build
# กลับโหมดปกติ
$env:BUG_MODE = "0"; docker compose up -d --build
Remove-Item Env:BUG_MODE

docker compose down                   # ปิดเว็บ (ข้อมูล DB ยังอยู่ใน volume)
```

ตรวจโหมดที่รันอยู่: `<html data-bug-mode="0|1">` (รายงานใน TEST-REPORT.md แสดงให้อัตโนมัติ)

## รัน test (PowerShell)

```powershell
cd e2e
npm install                           # ครั้งแรก (@playwright/test ล็อกที่ 1.63.0 ให้ตรงกับเบราว์เซอร์ที่ติดตั้งไว้)
npx playwright test                   # 3 เบราว์เซอร์พร้อมกัน
npx playwright test -g "TC-HOME-01"   # รันข้อเดียว
npm run test:gif                      # chromium (+ time-travel) อัดวิดีโอทุก test → GIF + MP4 (ต้องมี ffmpeg ใน PATH) ใช้เวลาราว 8 นาที
npm run report                        # เปิดรายงาน HTML ของ Playwright
```

## วิธีเขียน test ใหม่

1. ชื่อ test ขึ้นต้นด้วยรหัส TC จาก `TEST-PLAN.md` ตามด้วยสิ่งที่ทดสอบ เช่น `'TC-BOOK-01 จองคิวเดี่ยวจนจบ (Guest)'`
2. ใส่ `tag: ['@<โมดูล>', '@P1|@P2|@P3']` ตามคอลัมน์ "โมดูล" และ "ระดับ" เช่น `['@BOOK', '@P1']`
3. ใส่ `annotation: { type: 'expected', description: '<ผลที่คาดหวังจาก TEST-PLAN.md>' }` — reporter เอาไปใส่ในรายงานและ DEF-xxx
4. หา element ด้วย `page.getByTestId('...')` ตามที่เขียนใน `spa/SPEC.md` §3 เท่านั้น ห้ามเดา selector (CSS / XPath / ข้อความ)
5. import จาก `./fixtures` เสมอ (`import { test, expect, open } from './fixtures'`) ไม่ใช่จาก `@playwright/test` — ไม่งั้นจะไม่มีป้ายชื่อ/วงแดงใน GIF
6. เปิดหน้าด้วย `await open(page, '/path')` (รอ `html[data-ready="true"]`)
7. ห้าม reset ใน test — `global-setup.ts` reset ครั้งเดียว เพราะ 3 เบราว์เซอร์รันพร้อมกัน
   - จองคิว: ใช้วันจาก `bookingDate(browserName, DAY.<TC>)` (แต่ละเบราว์เซอร์ได้ช่วงวันของตัวเอง แต่ละ TC ได้วันของตัวเอง) กันจองชนกัน
   - ต้องการสมาชิกที่แก้ข้อมูลได้: `createMember(page.request, { totalSpent, points, course })` (อีเมลไม่ซ้ำ ตั้งค่าด้วย /api/test/user) แทนการแก้ nida / ton / new
   - อ่านผู้ใช้ seed อย่างเดียวได้: `loginByApi(page.request, 'nida')` · อ่านคิว seed 2026-10-09 / 10-10 ได้ แต่ห้ามจองทับวันนั้น
   - TC ที่ต้อง reset ด้วยเวลาอื่น (R(…)) หรือแก้ผู้ใช้ seed ตัวจริง → เขียนใน `tests/90-time-travel.serial.spec.ts` เท่านั้น (รันหลังทุกเบราว์เซอร์จบ)
   - บันทึกข้อมูลที่ปรับจากแผน / ค่าที่ "ต้องถาม" ด้วย `note('…')` หรือ `note('…', 'ต้องถาม')` → ไปอยู่ในรายงาน
8. เรียก API ด้วย fixture `apiLog` (`await apiLog.call(page.request, 'POST', '/api/...', body)`) — บันทึก request / status / body ให้อัตโนมัติ → `test-report/logs/<TC>-<browser>.log`
9. TC ที่เปิดหน้าเว็บต้องได้ทั้ง `test-report/gifs/<TC>.gif` และ `test-report/videos/<TC>.mp4` จาก `npm run test:gif` — ตรวจทุกครั้งหลังเพิ่ม test
10. รัน `npx playwright test` ให้ผ่านทั้ง 3 เบราว์เซอร์ (ถ้าล้มเพราะเว็บมีบั๊กจริง ให้ปล่อยให้ล้มและดู DEF-xxx ใน TEST-REPORT.md อย่าแก้ test ให้ผ่าน)
