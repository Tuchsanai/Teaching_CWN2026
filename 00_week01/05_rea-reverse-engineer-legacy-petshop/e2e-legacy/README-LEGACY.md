# e2e-legacy (PawPantry) — บันทึกส่งมอบ

ชุดเทสต์ regression ของหน้าร้าน ทีมเดิมใช้รันก่อน deploy ทุกครั้ง · Playwright 1.63.0 · 10 ไฟล์ 40 test

## รัน

```powershell
# 1) เปิดเว็บ (โฟลเดอร์ petshop) → http://localhost:4000
cd petshop
docker compose up -d --build

# 2) รันเทสต์
cd ..\e2e-legacy
npm install
npx playwright install chromium      # ครั้งแรกครั้งเดียว
npx playwright test                  # chromium อย่างเดียว (ค่าเริ่มต้น)
npm run test:all                     # chromium + firefox + webkit (ต้อง install firefox webkit ก่อน)
npx playwright show-report           # ดูรายงาน html
```

- เว็บที่พอร์ตอื่น: `$env:BASE_URL="http://localhost:<พอร์ต>"; npx playwright test` (ค่าเริ่มต้น `http://localhost:4000` · ค่านี้ค้างทั้งหน้าต่าง PowerShell ล้างด้วย `Remove-Item Env:BASE_URL`)
- ก่อนรันทุกรอบ `global-setup.ts` จะเช็ก `/api/health` แล้ว `POST /api/test/reset` (ใช้ได้เพราะ compose ตั้ง `ALLOW_TEST_RESET=1` ไว้ให้แล้ว)
- เลือกรันบางกลุ่ม: `npx playwright test --grep @checkout` · `--grep @P1`
- ข้อมูลแยกกันด้วยอีเมลสุ่ม รันขนานได้ (4 workers)

## ผลรันล่าสุด

| ชุด | ผล | เวลา |
|---|---|---|
| `npx playwright test` (chromium) | 40 passed | ~13 วินาที |
| `npm run test:all` (3 เบราว์เซอร์) | 120 passed | ~1 นาที |

## หมายเหตุ

- ผูกกับ seed data (ชื่อสินค้า ราคา สต็อก บัญชี `demo@pawpantry.test`) และ `data-testid` ในหน้าเว็บ · แก้ seed/ข้อความ/testid แล้วเทสต์แดงได้
- หน้าเว็บต้องตั้ง `html[data-ready="true"]` ก่อน เทสต์ถึงจะเริ่มกด
- ชื่อ test (TC-xxx) อ้างจากแผนทดสอบเดิม · ผลที่คาดหวังเขียนไว้ใน annotation `expected` ของแต่ละ test
