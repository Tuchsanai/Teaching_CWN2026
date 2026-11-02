# บทเรียน 02 · ทดสอบเว็บร้านอาหารสัตว์ PawPantry ด้วย Playwright

ผู้เรียนเป็น tester / BA ที่ไม่ได้เขียนโปรแกรม ตอบเป็นภาษาไทยง่าย ๆ และสรุปผลเป็นตารางเสมอ

## โครงสร้าง
- `petshop/` เว็บ Next.js + `Dockerfile` + `docker-compose.yml` (พร้อมใช้ **ห้ามแก้โค้ดเว็บ** เว้นแต่ผู้เรียนสั่ง)
  - ข้อกำหนดทั้งหมด (หน้า, ราคา, ข้อความ error, `data-testid`) อยู่ใน `petshop/SPEC.md`
  - เปิดเว็บ: `docker compose up -d --build` ใน `petshop/` → http://localhost:3000
  - โหมดฝังบั๊ก: ตั้ง env `BUG_MODE=1` ก่อน `docker compose up -d` (PowerShell: `$env:BUG_MODE=1`)
- `e2e/` ชุดทดสอบ Playwright (รันบน Windows)
  - `npx playwright test` = ทดสอบบน Chromium · `npm run test:gif` = Chromium อัด GIF + MP4 (ใช้เบราว์เซอร์ที่ติดตั้งไว้แล้วในบท 01 ไม่ต้อง `npx playwright install`)
  - รายงาน: `e2e/test-report/TEST-REPORT.md`, GIF: `test-report/gifs/`, MP4: `test-report/videos/`
- `TEST-PLAN.md` แผนการทดสอบ

## เมื่อผู้เรียนขอให้เขียน test ใหม่จากประโยคธรรมดา
1. อ่าน `petshop/SPEC.md` หา `data-testid` และข้อความที่ต้องตรวจ (ห้ามเดา selector)
2. เขียนไฟล์ใหม่ `e2e/tests/11-my-tests.spec.ts` (ถ้ามีแล้วให้เพิ่มต่อท้าย) ตามแบบไฟล์เดิม:
   - `import { test, expect, open } from './fixtures'`
   - ชื่อ test ขึ้นต้นด้วยรหัส `TC-MY-01`, `TC-MY-02` … ตามด้วยคำอธิบายภาษาไทย
   - ใส่ `tag: ['@my', '@P1|@P2|@P3']` และ `annotation: { type: 'expected', description: '<ผลที่คาดหวัง>' }`
   - เปิดหน้าด้วย `await open(page, '/path')` และหา element ด้วย `page.getByTestId(...)`
3. รันเฉพาะ test ใหม่ด้วย `npx playwright test tests/11-my-tests.spec.ts --project=chromium`
   แล้วรันแบบอัด GIF: `npx cross-env GIF=1 playwright test tests/11-my-tests.spec.ts`
4. ถ้า test ล้ม ให้ดูภาพ/วิดีโอตอนล้มก่อน แล้วบอกว่าเป็น **บั๊กของเว็บ** หรือ **test เขียนผิด** ห้ามแก้ test ให้ผ่านโดยไม่บอก
5. สรุปเป็นตาราง: รหัส | สิ่งที่ทดสอบ | ผลที่คาดหวัง | ผล | ลิงก์ GIF/MP4
