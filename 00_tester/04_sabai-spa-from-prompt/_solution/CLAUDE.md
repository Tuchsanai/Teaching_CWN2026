# CLAUDE.md · บท 04 สบายใจ สปา (ทดสอบเว็บ)

โฟลเดอร์นี้เป็นงาน **ทดสอบ** เว็บ สบายใจ สปา: เอกสารความต้องการ → แผนทดสอบ → ชุดทดสอบ Playwright (`e2e/`)

## ข้อห้าม (สำคัญ)
- **ห้ามแก้โค้ดใน `web/` และ `db/`** — เราเป็นผู้ทดสอบ ถ้าเว็บผิดให้บันทึกเป็นบั๊ก ไม่ใช่แก้เว็บ
- **ห้ามเปิด `web/BUGS.md` และ `_solution/`** (เฉลยบั๊ก) จนกว่าพรอมต์จะอนุญาต
- ห้ามแก้ "ผลที่คาดหวัง" ใน test ให้ตรงกับที่เว็บแสดง — ค่าคาดหวังมาจาก `TEST-PLAN.md` เท่านั้น
- ห้ามแตะ container อื่นนอกจาก `sabai-web`, `sabai-db` (container ที่จับพอร์ตชน เช่น `petshop` ให้ **stop** ได้อย่างเดียว ห้ามลบ)

## โครงสร้างโฟลเดอร์

```
w/
├─ REQUIREMENTS.md  USER-STORIES.md  DESIGN.md   ← ความต้องการของร้าน [D]
├─ TEST-DATA.md      ← seed (U01–U08, S01–S07, B01–B13, GC01–GC05 …) + ค่าขอบ E01–E90 · วันล็อก TODAY=2026-10-10T10:00:00+07:00
├─ EXPLORATION.md    ← ผลสำรวจเว็บ 3 ทาง (ร้าน/AI/เว็บจริง) + คำถามส่วน F · รูปใน exploration/
├─ TEST-PLAN.md      ← แผนทดสอบ 42 TC (หัวข้อ 5) + เกณฑ์ผ่าน (หัวข้อ 6)
├─ PLAN-REVIEW.md    ← รีวิวแผน
├─ db/               ← compose ฐานข้อมูล (ห้ามแก้)
├─ web/              ← โค้ดเว็บ Next.js (ห้ามแก้) · web/SPEC.md = API + data-testid (อ่านได้)
└─ e2e/              ← ชุดทดสอบ Playwright (TypeScript)
   ├─ playwright.config.ts   ← chromium / firefox / webkit + project "api" · th-TH · Asia/Bangkok · workers 1
   ├─ global-setup.ts        ← เช็ก /api/health แล้ว POST /api/test/reset ครั้งเดียว · อ่าน data-bug-mode
   ├─ plan-cases.json        ← 42 TC ที่ดึงจาก TEST-PLAN.md (npm run plan)
   ├─ tests/
   │  ├─ fixtures.ts         ← tc() ตั้งชื่อ/tag/annotation · reset ก่อนทุก test · api log · GIF/MP4 · ตัวช่วยจองคิว
   │  ├─ book.spec.ts  price.spec.ts  transport.spec.ts  member.spec.ts  course.spec.ts
   │  ├─ cancel.spec.ts  giftcard.spec.ts  therapist.spec.ts  i18n.spec.ts  ui.spec.ts
   │  └─ book.api.spec.ts  security.api.spec.ts   ← TC ที่ยิง API อย่างเดียว (รันใน project "api")
   ├─ fixtures/selfie-test.png   ← รูปทดสอบ > 50 KB (TC-UI-02)
   ├─ triage.json            ← การจำแนกข้อที่ล้ม: เว็บผิด / แผนผิด / test เขียนผิด
   ├─ index.html             ← รายงานหน้าเดียว (ดับเบิลคลิกเปิดได้)
   ├─ scripts/               ← build-report.mjs · index-reporter.mjs · run-gif.mjs · extract-plan.mjs
   └─ test-report/           ← gifs/<TC>.gif · videos/<TC>.mp4 · logs/<TC>.log · summary.json · history.json · html/
```

## เปิดฐานข้อมูล + เว็บ (PowerShell, ที่โฟลเดอร์ `w/`)

```powershell
# หยุด container อื่นที่จับพอร์ต 3000 / 5433 (stop อย่างเดียว)
docker ps --format "{{.Names}} {{.Ports}}"
docker stop petshop                                   # ถ้ามี

# network ร่วม + ฐานข้อมูล (รอ healthy)
docker network inspect sabai-net *> $null; if (-not $?) { docker network create sabai-net }
docker compose -f db/compose.yaml up -d
docker inspect -f "{{.State.Health.Status}}" sabai-db

# เว็บ (รอ healthy) แล้วเช็ก
docker compose -f web/compose.yaml up -d --build
docker inspect -f "{{.State.Health.Status}}" sabai-web
Invoke-RestMethod http://localhost:3000/api/health    # ok=True db=True

# รีเซ็ตข้อมูลทดสอบ + ล็อกวันนี้
Invoke-RestMethod -Method Post http://localhost:3000/api/test/reset -ContentType "application/json" -Body '{"now":"2026-10-10T10:00:00+07:00"}'
```

### BUG_MODE (เปิด/ปิดบั๊กที่ตั้งใจใส่)

```powershell
$env:BUG_MODE = "1"; docker compose -f web/compose.yaml up -d --force-recreate   # เปิดโหมดบั๊ก
$env:BUG_MODE = "0"; docker compose -f web/compose.yaml up -d --force-recreate   # ปิด (ปกติ)
# ตรวจโหมด: <html data-bug-mode="0|1"> — รายงาน e2e/index.html แสดงป้ายโหมดให้อัตโนมัติ
(Invoke-WebRequest http://localhost:3000).Content -match 'data-bug-mode="(\d)"' | Out-Null; $Matches[1]
```

## รันชุดทดสอบ (PowerShell, ที่ `w/e2e`)

```powershell
cd e2e
npm install
npx playwright install                 # chromium firefox webkit
npx playwright test                    # 3 เบราว์เซอร์ + project api → สร้าง index.html ใหม่อัตโนมัติ
npm run test:gif                       # chromium แบบช้า + อัดวิดีโอ → test-report/gifs/*.gif, videos/*.mp4 (ต้องมี ffmpeg)
npx playwright test --grep "@P1"       # เฉพาะ P1 · --grep "@BOOK" เฉพาะโมดูล · --grep "TC-GC-02" ข้อเดียว
npx playwright test --project=webkit   # เบราว์เซอร์เดียว
npm run report                         # สร้าง index.html ใหม่หลังแก้ triage.json (ไม่ต้องรัน test ซ้ำ)
npx playwright show-report test-report/html
```

- `GIF=1` ตั้งผ่าน `npm run test:gif` (ใช้ได้ทั้ง PowerShell/bash) · ถ้าจะตั้งเอง: `$env:GIF="1"; npx playwright test --project=chromium; Remove-Item Env:GIF`
- รันทีละ test (`workers: 1`) เพราะทุก TC ต้อง reset ฐานข้อมูลก่อน และ TC-CXL-02 เลื่อนนาฬิกาของทั้งระบบ → 3 เบราว์เซอร์รันพร้อมกันจะชนข้อมูลกัน

## วิธีเขียน test ใหม่

1. เพิ่มแถว TC ใน `TEST-PLAN.md` หัวข้อ 5 (ID · โมดูล · สิ่งที่ทดสอบ · … · ระดับ · ผลที่คาดหวัง · ที่มา) แล้วรัน `npm run plan` → `plan-cases.json`
   - ถ้าเป็น TC ที่ยิง API อย่างเดียว เพิ่ม ID ใน `API_ONLY` ของ `scripts/extract-plan.mjs` และเขียนในไฟล์ `*.api.spec.ts`
2. เขียนในไฟล์ของโมดูล (`tests/<โมดูล>.spec.ts`) ด้วย `tc('<ID>', ...)` — ชื่อ test, tag `@<โมดูล>` `@P1|P2|P3` และ annotation ผลที่คาดหวัง/ที่มา มาจากแผนให้เอง

```ts
import { tc, test, expect, loginUI, bookToStep3, quoteTotal, toSummary, amount } from './fixtures';
const S = test.step;

tc('TC-PRICE-99', async ({ page, api }) => {
  await S('U01 จอง S01 20 ต.ค. 10:00', async () => {
    await loginUI(page, 'U01');
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
  });
  await S('ยอด ฿950 (฿1,000 − 5% Gold)', async () => {
    expect.soft(await quoteTotal(page)).toBe(950);        // ตัวเลขจากแผน ไม่ใช่จากที่เว็บแสดง
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(950);
  });
  await S('หลังรีโหลด: ตรวจที่บันทึกจริง', async () => {
    const rows = await api.adminBookings('2026-10-20');   // owner GET /api/admin/bookings (ถูกบันทึก log)
    expect.soft(rows.length).toBe(1);
  });
});
```

กติกา:
- หา element ด้วย `getByTestId` จาก `web/SPEC.md` หัวข้อ 8 (หรือที่เห็นบนหน้า) · เงินอ่านจาก `data-amount`
- แบ่งขั้นตอนภาษาไทยด้วย `test.step` · ตรวจด้วย `expect.soft` (ล้มจุดเดียวยังตรวจจุดอื่นต่อ)
- ไม่ต้อง reset เอง — fixture `resetDb` reset ให้ทุก test · ถ้าเลื่อนนาฬิกา (`api.reset(now)`) ต้อง reset กลับใน `finally`
- ค่าที่ "ถูกบันทึก" (นัด แต้ม ครั้งคอร์ส ยอดบัตร) ต้องตรวจหลังรีโหลด/GET ใหม่เสมอ
- ราคาบนหน้าจอมาจาก `/api/price` แบบไม่พร้อมกัน → อ่านด้วย `quoteTotal()` / `settle()` ที่รอให้หน้าเว็บคิดเสร็จ (ไม่ได้รอค่าที่อยากได้)
- test ล้ม → ดูภาพ/GIF ก่อน แล้วจำแนกใน `e2e/triage.json` (`เว็บผิด` / `แผนผิด` / `test เขียนผิด`) → `npm run report` · แก้ได้เฉพาะ test ที่เขียนผิดจริง
