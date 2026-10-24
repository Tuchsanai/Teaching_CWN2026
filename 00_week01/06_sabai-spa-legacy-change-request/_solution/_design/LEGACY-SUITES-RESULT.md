# LEGACY-SUITES-RESULT · สร้างและรันชุดเทสต์เดิม (e2e-legacy) ของบท 05–06

> งาน C1 · รันจริงวันที่ 12 ต.ค. 2026 บนเครื่องผู้สร้างบท (Windows 11, Docker Desktop, Node v26.7.0, Playwright 1.63.0)
> รันทีละแอปบน host port **4000** · ตัวเลขทุกตัวในเอกสารนี้มาจากการรันจริง ยกเว้นที่เขียนว่า "คาดว่า"
> ฐานการตัดสินใจ: `LEGACY-TESTSUITES.md` (A7) ข้อ 4.1 และ 4.2

## 0. สรุป

| บท | โฟลเดอร์ | ที่มา | ค่าเริ่มต้น | ผล (ค่าเริ่มต้น) | ผล (ครบ 3 เบราว์เซอร์) |
|---|---|---|---|---|---|
| 05 | `05_rea-reverse-engineer-legacy-petshop/e2e-legacy/` | `02_petshop-test-from-plan/e2e` | chromium | **40/40 passed · 12.4 วินาที** | **120/120 passed · 57.3 วินาที** |
| 06 | `06_sabai-spa-legacy-change-request/e2e-legacy/` | `04_…/_solution/e2e` | api + chromium | **41 passed · 1 failed (TC-SEC-05) · 4.0 นาที** | **113 passed · 1 failed · 12.8 นาที** |
| 06 | `06_…/web/scripts/check-rules.mjs` | มีอยู่แล้ว (แก้แค่ค่าเริ่มต้นพอร์ต) | — | **90/90 · 20.3 วินาที** | — |

สถานะแอปตอนรัน: บท 05 และ 06 **ยังมี `BUG_MODE` อยู่ (ค่า 0)** และบท 05 **ยังไม่ได้ใส่ BUG-01** → ต้องรันซ้ำหลังผู้สร้างบทถอด BUG_MODE/ใส่บั๊ก (ดูข้อ 5)

---

## 1. บท 05 · สิ่งที่คัดลอก/ตัด

| ไฟล์ใน `e2e-legacy/` | ที่มา | ทำอะไร |
|---|---|---|
| `package.json` | 02/e2e | name `pawpantry-legacy-e2e` · ลบ `test:gif` และ `cross-env` · pin `@playwright/test` **1.63.0** (เดิม `^1.63.0`) · เพิ่ม `test:all` · คง `test` `test:ui` `report` |
| `package-lock.json` | สร้างใหม่ | `npm install` ใน `C:/t/work/c1/e5` แล้วคัดลอกกลับ (ไม่มี cross-env แล้ว) |
| `playwright.config.ts` | 02/e2e | ลบ GIF/slowMo/video GIF ทั้งหมด · reporter `list` + `html` (ลบ `./reporters/tester-report.ts`) · baseURL `http://localhost:4000` · project ค่าเริ่มต้น **chromium** · firefox/webkit เปิดเมื่อมี `--project` หรือ `ALL_BROWSERS=1` · คง `fullyParallel`, `workers: 4`, `timeout: 45_000` |
| `global-setup.ts` | 02/e2e | แก้แค่ค่าเริ่มต้น 3000 → 4000 (ยังเช็ก `/api/health` + `POST /api/test/reset`) |
| `tests/fixtures.ts` | 02/e2e | ลบ `overlayScript` + override `page` ของโหมด GIF → `export const test = base` |
| `tests/01…10-*.spec.ts` | 02/e2e | คัดลอกตรง ไม่แก้ (40 test) · **คง TC-CPN-01, TC-WISH-02, TC-CHK-02** เป็น regression ธรรมดา เพราะ CR-DESIGN บท 05 ให้ถอด BUG_MODE |
| `tsconfig.json`, `.gitignore` | 02/e2e | คัดลอกตรง |
| `README-LEGACY.md` | ใหม่ | บันทึกส่งมอบสั้น ๆ: วิธีรัน, ผลรันล่าสุด, ข้อผูกกับ seed/testid · ไม่พูดถึงบั๊ก |
| ~~`reporters/tester-report.ts`~~, ~~`node_modules/`~~ | — | ไม่คัดลอก |

## 2. บท 06 · สิ่งที่คัดลอก/ตัด

| ไฟล์ใน `e2e-legacy/` | ที่มา | ทำอะไร |
|---|---|---|
| `package.json` | 04/e2e | name `sabai-legacy-e2e` · scripts `test`, `test:p1`, `test:all`, `report` (`playwright show-report test-report/html`) · ลบ `test:gif`, `plan`, report แบบเดิม |
| `package-lock.json` | 04/e2e | dependency เดิม · อัปเดตแค่ชื่อแพ็กเกจหลัง `npm install` |
| `playwright.config.ts` | 04/e2e | ลบ GIF/slowMo/video · reporter `list` + `html` (ลบ `json` และ **`./scripts/index-reporter.mjs`**) · baseURL 4000 · project ค่าเริ่มต้น **api + chromium** · firefox/webkit แบบเดียวกับบท 05 · คง `workers: 1`, `timeout: 90_000`, `timezoneId: Asia/Bangkok`, `outputDir: test-report/artifacts` |
| `global-setup.ts` | 04/e2e | ค่าเริ่มต้น 4000 · **ลบส่วนอ่าน `data-bug-mode` + เขียน `test-report/meta.json`** (ไม่ให้ suite ผูกกับ BUG_MODE ที่จะถูกถอด) · ลบคำว่า "EN-3" ในข้อความ error |
| `tests/fixtures.ts` | 04/e2e | ลบ `overlayScript`, `convertVideo`, `spawnSync`, `GIF`, `existsSync` · `page` เหลือ `trackPrice(page)` · คง `Api` log (`test-report/logs/`) และ `tc()` |
| `tests/*.spec.ts` (12 ไฟล์) | 04/e2e | คัดลอกตรง + ติด `test.fail` 3 ข้อ (ข้อ 3) |
| `plan-cases.json`, `fixtures/selfie-test.png`, `tsconfig.json` | 04/e2e | คัดลอกตรง (`tc()` และ TC-UI-02 ต้องใช้) |
| `.gitignore` | ใหม่ | `node_modules/` `test-report/` `test-results/` |
| `README-LEGACY.md` | ใหม่ | บันทึกส่งมอบสั้น ๆ (วิธีรัน, ผลล่าสุด, "TC-SEC-05 แดงค้าง ยังไม่ได้ดู") |
| ~~`scripts/*`, `triage.json`, `index.html`, `normal-mode/`, `test-report/`, `node_modules/`~~ | — | ไม่คัดลอก |

และแก้ `06/web/scripts/check-rules.mjs` **3 บรรทัด** (บรรทัด 2, 3, 8): `localhost:3000` → `localhost:4000` (คอมเมนต์วิธีใช้ + ค่าเริ่มต้น `BASE`) · ไม่แตะส่วนอื่น

## 3. ยืนยัน known failures ของบท 06 (รันจริง ก่อนติดป้าย)

รอบแรก (ยังไม่ติด `test.fail`, api + chromium): **38 passed · 4 failed · 4.0 นาที** ล้มตรงกับที่ A7 ระบุทุกข้อ

| TC | project | ขั้นที่ล้ม | การจัดการ |
|---|---|---|---|
| TC-TRN-03 | chromium | ติ๊กรถรับส่งไม่ใส่ระยะ กดถัดไปแล้วไปขั้น 4 ได้ | `test.fail(true, 'KNOWN-ISSUE: ยังไม่บังคับกรอกระยะทาง/โรงแรมเมื่อติ๊กรถรับส่ง')` |
| TC-GC-04 | chromium | ใส่ `XXXX` แล้วไม่มี `book-giftcard-error` | `test.fail(true, 'KNOWN-ISSUE: ใส่รหัสบัตรที่ไม่มีจริงแล้วไม่มีข้อความเตือน')` |
| TC-SEC-04 | api | logout แล้ว `GET /api/me` ด้วย cookie เดิมไม่ได้ 401 | `test.fail(true, 'KNOWN-ISSUE: logout แล้ว cookie เดิมยังใช้ได้ (session ไม่ถูกเพิกถอน)')` |
| TC-SEC-05 | api | U04 จองด้วยคอร์ส C01 ของ U01 → **422** `COURSE_UNAVAILABLE` (คาด 403/404) · ส่วนยกเลิก B05 ของคนอื่นได้ 403 ถูกแล้ว | **ไม่ติดป้าย** ปล่อยแดง (ข้อสอบ "บั๊กหรือเทสต์ล้าสมัย") |

แต่ละข้อมีคอมเมนต์ `// KNOWN-ISSUE (ส.ค. 69): ล้มตั้งแต่ส่งมอบ ยังไม่ได้แก้ · แก้แล้วให้ลบบรรทัด test.fail ออก` อยู่บรรทัดแรกของ body

## 4. คำสั่งรันสำหรับผู้เรียน (PowerShell) + ผลจริง

### 4.1 บท 05

```powershell
cd 05_rea-reverse-engineer-legacy-petshop\petshop
docker compose up -d --build
cd ..\e2e-legacy
npm install
npx playwright install chromium          # ครบ 3 เบราว์เซอร์: npx playwright install
npx playwright test                      # chromium
npm run test:all                         # chromium + firefox + webkit
```

| คำสั่ง | ผล | เวลา (Playwright) |
|---|---|---|
| `npx playwright test` | 40 passed (2 รอบ: 12.9 / 12.4 วินาที) | ~13 วินาที |
| `npx playwright test --project=firefox` | 40 passed | 18.1 วินาที |
| `npm run test:all` | 120 passed (chromium 40 · firefox 40 · webkit 40) | 57.3 วินาที |

(ตอนรันจริงใช้ `docker compose -p c1pet -f docker-compose.yml -f <override>` เปลี่ยน image เป็น `c1-pawpantry:verify` และ container เป็น `c1-petshop` เพื่อไม่ทับ `pawpantry:latest` ของบท 02/03 · build ใช้ cache ~3.6 วินาที · ลบ image แล้ว)

### 4.2 บท 06

```powershell
cd 06_sabai-spa-legacy-change-request
docker network create sabai-net           # ครั้งแรก (ใช้ชื่อตาม db/compose.yaml ปัจจุบัน)
docker compose -f db/compose.yaml up -d
docker compose -f web/compose.yaml up -d --build
cd web
node scripts/check-rules.mjs              # 90 / 90
cd ..\e2e-legacy
npm install
npx playwright install chromium
npx playwright test                       # api + chromium
npm run test:all                          # api + chromium + firefox + webkit
npm run report
```

| คำสั่ง | ผล | เวลา |
|---|---|---|
| `node scripts/check-rules.mjs` | **ผ่าน 90 / 90** (exit 0) · หัวรายงานพิมพ์ `http://localhost:4000 (BUG_MODE=0)` | 20.3 วินาที (`time`) |
| `npx playwright test` (ก่อนติดป้าย) | 38 passed · 4 failed | 4.0 นาที |
| `npx playwright test` (หลังติดป้าย) | **41 passed · 1 failed** (TC-SEC-05) | 4.0 นาที |
| `npm run test:all` (หลังติดป้าย) | **113 passed · 1 failed** (TC-SEC-05) | 12.8 นาที |

เวลารวมต่อ project (บวกเวลาของแต่ละ test จาก `list` reporter รอบ `test:all`): api 6 ข้อ ~2 วินาที · chromium 36 ข้อ 3.95 นาที · firefox 36 ข้อ 3.94 นาที · webkit 36 ข้อ 4.77 นาที

(ตอนรันจริงใช้ override เปลี่ยน image เป็น `c1-sabai-web:verify` เพื่อไม่ทับ `sabai-web:latest` ของบท 04 · ตอนรันไม่มี container `sabai-db`/`sabai-web` ของบท 04 ค้างอยู่ จึงไม่ต้องหยุดอะไร · จบแล้ว `down` ทั้งสอง project, ลบ volume `sabai06-pgdata` และ image `c1-sabai-web:verify` · network `sabai-net` มีอยู่ก่อนแล้ว ไม่ได้ลบ)

## 5. ข้อสังเกต / สิ่งที่ต้องทำต่อ

| เรื่อง | รายละเอียด | ต้องทำ |
|---|---|---|
| เลือก project ด้วย `process.argv` อย่างเดียวไม่ได้ | รอบแรก `npm run test:all` ได้ 80 failed: `Project "firefox" not found in the worker process` เพราะ worker ไม่เห็น argv เดียวกัน | แก้แล้ว: ถ้ามี `--project` ให้ตั้ง `process.env.ALL_BROWSERS='1'` ใน config (worker สืบทอด env) → ผ่าน |
| ชื่อ compose/image ยังซ้ำบท 02–04 (D8) | ตอนรัน `05/petshop` ยังเป็น container `petshop` image `pawpantry:latest` · `06` ยังเป็น `sabai-db`/`sabai-web`/`sabai-net` image `sabai-web:latest` | ผู้แก้ compose ตาม D8 ต้องแก้คำสั่งใน `e2e-legacy/README-LEGACY.md` บท 06 บรรทัด `docker network create` (ตอนนี้เขียนกลาง ๆ ว่า "ตามชื่อใน db/compose.yaml") · suite ไม่ผูกกับชื่อ container ผูกแค่ `localhost:4000` |
| BUG_MODE ยังอยู่ในทั้งสองแอปตอนรัน | ผลข้างบน = พฤติกรรม `BUG_MODE=0` | หลังถอด BUG_MODE ให้รันซ้ำ: **คาดว่า** บท 05 ยัง 40/40 และบท 06 ยัง 41+1 / check-rules 90/90 (CR-DESIGN ทั้งสองบทบอกว่าการถอดเป็น refactor ที่ผลเท่า `BUG_MODE=0`) · check-rules จะไม่พิมพ์ `(BUG_MODE=…)` อีกเมื่อใส่ diff §2.3 ของ CR-DESIGN บท 06 |
| BUG-01 บท 05 (server คิดค่าส่งด้วย `>`) | ยังไม่ได้ใส่ในแอปตอนรัน · จากการอ่าน spec: TC-CHK-03 ใช้คูปอง FREESHIP และ TC-CART-03 ตรวจแค่หน้าตะกร้า → **คาดว่า** suite นี้ยังเขียว 40/40 หลังใส่บั๊ก (ตรงกับเจตนา "เทสต์เขียว ≠ ไม่มีบั๊ก") | รันยืนยันหลังใส่ diff BUG-01 |
| ชื่อไฟล์ในรายงานเป็น `tests\fixtures.ts:124` | บท 06 ทุก test ประกาศผ่าน `tc()` ใน fixtures จึงขึ้นตำแหน่งนั้นแทนไฟล์ spec | ไม่แก้ (พฤติกรรมเดิมของ suite บท 04) · ใช้ชื่อ TC ค้นแทน |
| `test.fail` กับ CR ที่แก้บั๊ก | ถ้าผู้เรียนแก้ TRN-03 / GC-04 / SEC-04 test จะขึ้น "Expected to fail, but passed" (นับเป็น failed) | ใส่ในเฉลย LAB: ต้องลบ `test.fail` พร้อมการแก้ |
| ผูกกับ seed | บท 06 ใช้ U01–U08, owner, B05/B06, C01, SABAI-GC-* · บท 05 ใช้ demo account, ราคา/สต็อก seed | CR ที่แก้ seed (เช่น CR-04 วันหยุดร้าน) ต้องรัน suite และอธิบายเคสที่เปลี่ยน |
| เอกสารอ้างอิงที่ไม่มี | `plan-cases.json`, คอมเมนต์ fixtures และ check-rules อ้าง TEST-PLAN / TEST-DATA / BR-xx ที่ไม่ได้ส่งมอบ | คงไว้ (สมจริงแบบ legacy ตาม D4) |
