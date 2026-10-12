# LEGACY-TESTSUITES · ชุดเทสต์เดิมของบท 02–04 ใช้เป็น "legacy regression suite" ของบท 05–06 ได้ไหม

> งาน A7 · ตรวจแบบอ่านไฟล์อย่างเดียว (static) ไม่ได้เปิด server และไม่ได้รันเทสต์
> - **จำนวน test / ไฟล์ / selector** = นับจากโค้ดจริงด้วย grep/diff ในงานนี้
> - **เวลาที่ใช้ / ผลผ่าน-ล้ม** = อ้างจากผลที่ผู้สร้างบทรันไว้แล้ว (README บท 02–03, `history.json` `summary.json` `bug-run1.txt` ของบท 04, `BUGS.md`) **ไม่ได้รันใหม่ในงานนี้**

## 0. สรุปสั้น

| บท | คำแนะนำ | เหตุผลหลัก |
|---|---|---|
| **05** PawPantry | **(b) ใช้ suite บท 02 ที่ตัดแล้ว** → `05/e2e-legacy/` (40 test) | แอปของบท 02, 03 และ 05 **ทำงานเหมือนกันทุกอย่าง** (ต่างกันแค่คอมเมนต์) · suite บท 02 แยกเป็นอิสระ ไม่ต้องใช้ TEST-PLAN.md · เมื่อ `BUG_MODE=0` ผ่านครบ 120/120 ใน 1.1 นาที · ไม่ใช้ suite `_solution` ของบท 03 เพราะ fixture ต้องอ่าน TEST-PLAN.md, reporter ต้องใช้ ffmpeg และรันช้า 8.7 นาที |
| **06** Sabai Spa | **(c) ใช้ 2 ชั้น**: ① `web/scripts/check-rules.mjs` (มีอยู่ใน 06 แล้ว · 90 เคส API+unit) ② suite บท 04 ที่ตัดแล้ว → `06/e2e-legacy/` (42 TC · ค่าเริ่มต้น api + chromium) และติดป้าย **known failures 4 ข้อ** ที่ล้มอยู่แล้วแม้ `BUG_MODE=0` | ตรงกับ legacy จริง คือ "มีเทสต์อยู่แล้ว แต่บางข้อแดงค้าง" · ถ้าผู้เรียนแก้ CR แล้วข้อที่ติด `test.fail` เปลี่ยนเป็นผ่าน จะเห็นทันทีว่าต้องอัปเดต suite ตาม |

---

## 1. ภาพรวม 4 ชุดที่ตรวจ

| | **บท 02 `e2e/`** (ผู้เรียนใช้) | **บท 03 `_solution/e2e/`** | **บท 04 `_solution/e2e/`** | **`web/scripts/check-rules.mjs`** (04 = 06) |
|---|---|---|---|---|
| ระบบที่ทดสอบ | PawPantry | PawPantry | Sabai Spa | Sabai Spa |
| จำนวน | **40 test** · 10 spec | **48 test** · 10 spec | **42 TC** · 12 spec (UI 36 · API 6) | **90 เคส** E01–E90 (unit 7 · API 83) |
| จำนวนรอบเต็มชุด | 120 (40 × 3 เบราว์เซอร์) | 144 (48 × 3) | 114 (36 × 3 + API 6 × 1) | 90 (ไม่ใช้เบราว์เซอร์) |
| workers / parallel | 4 · `fullyParallel: true` | 1 · serial | 1 · serial | serial (ลูปใน node) |
| reset ข้อมูล | globalSetup `POST /api/test/reset` ครั้งเดียว · แยกข้อมูลกันด้วยอีเมลสุ่มและสินค้าคนละตัวต่อเบราว์เซอร์ | globalSetup + fixture `_cleanState` (auto) reset ก่อน**ทุก** test | globalSetup + fixture `resetDb` (auto) `POST /api/test/reset {now: 2026-10-10T10:00+07:00}` ก่อนทุก test | `reset(now)` ก่อนทุกเคส (ยกเว้น unit) + reset ท้ายรอบ |
| health check | `/api/health` ok | `/api/health` → `{"ok":true}` | `/api/health` ต้องเป็น `{"ok":true,"db":true}` ตรงตัว | `/api/health` `db:true` (ไม่ผ่าน = exit 2) |
| BUG_MODE | ไม่อ่าน (สลับที่ container) | ไม่อ่าน | อ่าน `<html data-bug-mode>` แล้วเขียนลง `test-report/meta.json` | อ่าน `data-bug-mode` แล้วตั้ง `process.env.BUG_MODE` ให้ unit test |
| ต้องใช้ไฟล์เฉพาะบท | ไม่ต้อง (tag/annotation เขียนในไฟล์ spec) | **ต้องมี `TEST-PLAN.md`** (`plan()` throw ถ้าหาไม่เจอ) · `triage.json` · ต้องใช้ `ffmpeg-static` (postinstall ดาวน์โหลด binary) | **ต้องมี `plan-cases.json`** (`tc()` throw ถ้าไม่มี id) · `fixtures/selfie-test.png` · `scripts/index-reporter.mjs` → `build-report.mjs` | `../lib/rules/index.ts` (import ตรง) · ต้องใช้ Node ≥ 22.18 |
| reporter/GIF | `list` + `html` + `tester-report.ts` (ทำ GIF ถ้า `GIF=1` · ใช้ ffmpeg จาก PATH) | `list` + `html-report.ts` (**chromium อัดวิดีโอทุก test + slowMo 300** → GIF/MP4) | `list` + `json` + `html` + `index-reporter.mjs` · GIF ถ้า `GIF=1` (`run-gif.mjs`) | console |
| `BUG_MODE=0` (ผลที่บันทึกไว้) | **120 passed · 1.1 นาที** | 46/48 ผ่าน (ล้ม TC-SRCH-01, TC-CART-05) · 8.7 นาที | 38/42 ผ่าน (ล้ม TC-TRN-03, TC-GC-04, TC-SEC-04, TC-SEC-05) · ~13 นาที (3 เบราว์เซอร์) | **90/90** |
| `BUG_MODE=1` (ผลที่บันทึกไว้) | ผ่าน 37 · ล้ม 3 (จับบั๊กได้ครบ 3) | 41/48 · 16.8 นาที | 91/114 passed · 17.8 นาที (TC-BOOK-07 timeout 90 วิ) | 80/90 |

---

## 2. PawPantry: แอปบท 02, 03 และ 05 เป็นตัวเดียวกันไหม

ใช้ `diff -rq -x node_modules -x .next` เทียบทีละไฟล์

| เทียบ | ผล |
|---|---|
| **03 ↔ 05** | **เหมือนกันทุกไฟล์** (diff ไม่มีผลต่าง) |
| **02 ↔ 03** `app/` | เหมือนกันทุกไฟล์ |
| **02 ↔ 03** `lib/` | ต่างกัน 3 ไฟล์ แต่**ต่างแค่คอมเมนต์**: `pricing.ts` (02 มีบรรทัด `bugMode (training bug #1): PAW10 gives 1%…`) · `validation.ts` (`Training bug #3…`) · `finder.ts` (`(see SPEC)`) |
| **02 ↔ 03** `components/` | ต่างกัน 1 ไฟล์: `ShopProvider.tsx` ต่างแค่คอมเมนต์ `Training bug #2…` |
| อื่น ๆ | 02 มี `SPEC.md` (03 และ 05 ไม่มี) · `.dockerignore` ของ 02 มีบรรทัด `SPEC.md` เพิ่ม · `README.md` ของ 02 อธิบาย BUG_MODE, บั๊ก 3 ตัว และบัญชี demo แต่ของ 03 ไม่มี |

**สรุป:** โค้ดที่รันจริงเหมือนกันทั้งหมด บท 03 แค่ลบคำใบ้เรื่องบั๊กออก → **suite บท 02 รันกับ `05/petshop` ได้เลยโดยไม่ต้องแก้ selector**

---

## 3. รายละเอียดแต่ละชุด

### 3.1 บท 02 `02_petshop-test-from-plan/e2e/` (แนะนำให้ใช้กับบท 05)

**วิธีรัน:** `cd petshop; docker compose up -d --build` → `cd ../e2e; npm install; npx playwright test` · `BASE_URL` (ค่าเริ่มต้น `http://localhost:3000`) · ต้องตั้ง `ALLOW_TEST_RESET=1` ไว้ใน `docker-compose.yml` (ตั้งไว้แล้ว) · ถ้าจะสลับ BUG_MODE ต้องสั่ง `BUG_MODE=1 docker compose up -d` ที่ฝั่ง container

| ไฟล์ | test | ครอบคลุม |
|---|---|---|
| 01-home | 2 | หน้าแรก, ปุ่ม "ช้อปอาหารแมว" |
| 02-catalog | 6 | ค้นหา, กรอง, เรียงราคา, เกรนฟรี, ค้นไม่เจอ, เมนูของเล่น |
| 03-product | 4 | ราคาตามขนาด, สินค้าหมด, จำนวนไม่เกินสต็อก, 404 |
| 04-wishlist | 3 | เพิ่ม/รีโหลด, **ลบแล้วตัวเลขลดทันที**, ย้ายไปตะกร้า |
| 05-cart | 4 | ยอดรวม, เพิ่ม/ลด/ลบ, ส่งฟรี ฿999, ตะกร้ายังอยู่หลังรีโหลด |
| 06-coupon | 3 | **PAW10 ลด 10%**, คูปองผิด/หมดอายุ, NEWCAT50 ขั้นต่ำ |
| 07-auth | 6 | สมัคร, ส่งฟอร์มเปล่า, รหัสอ่อน, อีเมลซ้ำ, รหัสผิด, login/logout |
| 08-checkout | 4 | ต้อง login ก่อน, **ตรวจฟอร์มที่อยู่ (เบอร์ 9 หลัก)**, ซื้อจนจบ E2E, สต็อกลดลง |
| 09-recommend | 4 | finder 2 แบบ, แนะนำตามที่เคยดู, "ซื้อคู่กันบ่อย" |
| 10-mobile-api | 4 | เมนูมือถือ 390px · API `GET /api/products?pet=dog` · `POST /api/orders` ต้องได้ 401 · 404 |

- **ผูกกับ selector แค่ไหน:** `getByTestId`/`data-testid` 235 จุด · assert ข้อความ (`toHaveText`/`getByText`/`getByRole`) 69 จุด ส่วนมากเป็น**ข้อความภาษาไทยแบบตรงตัว** เช่น `'ใช้คูปอง PAW10 แล้ว'` และ `'พบ 14 รายการ'` · มี `data-slug` และยอดเงินตรงตัว เช่น `฿770` และ `฿378` · ทุกหน้ารอ `html[data-ready="true"]` (ตั้งใน `components/ShopProvider.tsx`) → ถ้าแก้ชื่อ testid, ข้อความ, ราคาหรือ seed data เทสต์จะแดงทันที (เป็น characterization ที่ดี)
- **test.fail / skip:** ไม่มีเลย ทุกข้อ assert พฤติกรรมที่ถูกต้อง
- **ข้อที่จับบั๊ก BUG_MODE=1:** TC-CPN-01 (PAW10 1%) · TC-WISH-02 (ตัวเลขหัวใจ) · TC-CHK-02 (เบอร์ 9 หลัก)
- **ความเร็ว:** บันทึกไว้ 120 รอบใน 1.1 นาที (4 workers) → ถ้ารัน chromium อย่างเดียวน่าจะไม่ถึง 1 นาที (ยังไม่ได้วัด)

### 3.2 บท 03 `_solution/e2e/` (ไม่แนะนำให้คัดลอก)

**วิธีรัน:** เหมือนบท 02 แต่ `npm install` จะรัน `postinstall` เพื่อดาวน์โหลด ffmpeg-static · `workers: 1` · timeout 120 วินาที · chromium อัดวิดีโอทุกข้อพร้อม `slowMo: 300` · reporter `html-report.ts` (545 บรรทัด) สร้าง `index.html` + GIF/MP4 และตัดสิน Exit criteria จาก TEST-PLAN หัวข้อ 6.2 + `triage.json`

| ไฟล์ | test | | ไฟล์ | test |
|---|---|---|---|---|
| 01-auth (login 4 + สมัคร 3) | 7 | | 06-shipping | 4 |
| 02-catalog (ค้นหา 2, กรอง 1, สินค้า 3) | 6 | | 07-checkout (BVA เบอร์/ไปรษณีย์/ที่อยู่) | 7 |
| 03-cart | 6 | | 08-account | 1 |
| 04-wishlist-finder | 2 | | 09-security (IDOR, XSS, แก้ localStorage) | 3 |
| 05-coupon | 10 | | 10-mobile-404 | 2 |

- **ต้องใช้ไฟล์ของบท:** `fixtures.ts` จะอ่าน `../TEST-PLAN.md` หรือ `../../TEST-PLAN.md` และ `plan(id)` จะ **throw ตอนโหลดไฟล์** ถ้าไม่มี id นั้น → ถ้าไม่มีแผน ทุก spec จะพังตั้งแต่ตอน collect
- **ผูกกับ selector:** testid 288 จุด · assert ข้อความ 61 จุด · ใช้ `expect.soft` + `check()` (นับเป็น checkpoint) และวงแดงบนจอเมื่อล้ม
- **ล้มอยู่แล้วแม้ `BUG_MODE=0`:** TC-SRCH-01 (ความคาดหวังในแผนน่าจะแคบไป) และ TC-CART-05 (ข้อความ toast) · TC-CHK-03 ออกแบบไม่ดี เพราะพอข้อย่อยแรกล้ม ข้อย่อยที่เหลือจะ timeout (มีบันทึกใน `triage.json`)
- **ความเร็ว:** 8.7 นาที (`BUG_MODE=0`) และ 16.8 นาที (`BUG_MODE=1`) · ช้าเพราะใช้ worker เดียว, reset ทุกข้อ และ chromium ใช้ slowMo + วิดีโอ
- **เหตุผลที่ไม่ใช้:** ต้องพึ่งไฟล์ของบทเยอะ (TEST-PLAN, triage, ffmpeg) ช้ากว่าบท 02 ราว 8 เท่า และเป็น**เฉลยของบท 03** (คัดลอกไปเท่ากับแจกแผนของบท 03 ไปด้วย) · ชุดนี้เหมาะเป็นแหล่งไอเดีย "เทสต์ที่ล้าสมัย" มากกว่า (ดู 4.1 ข้อเลือกเสริม)

### 3.3 บท 04 `_solution/e2e/` (แนะนำให้ใช้กับบท 06 หลังตัดแล้ว)

**วิธีรัน:** ต้องรัน db ก่อน web (`docker network create sabai-net` → `db/compose.yaml` → `web/compose.yaml`) → `cd e2e; npm install; npx playwright test` · `BASE_URL` (ค่าเริ่มต้น `http://localhost:3000`) · `timezoneId: Asia/Bangkok` · วันที่ล็อกไว้ `TODAY=2026-10-10T10:00:00+07:00` ส่งผ่าน `reset {now}` และ TC-CXL-02 เลื่อนนาฬิกาของทั้งระบบ จึงต้องรัน serial · project `api` รัน `*.api.spec.ts` ครั้งเดียว · `npm run test:p1` = `--grep @P1`

| โมดูล (ไฟล์) | TC | หมายเหตุ |
|---|---|---|
| BOOK (`book.spec` 9 + `book.api.spec` 1) | 10 | E2E จอง 4 ขั้น · ช่วงวัน · รอบ/เวลาปิด · จองซ้อน · ดับเบิลคลิก · คู่ · กลุ่ม · จองพร้อมกัน (API) |
| PRICE (`price.spec`) | 6 | ลำดับคิดราคา (BR-20) |
| MEM (`member.spec`) | 4 | tier · แลกแต้ม · แต้มหลังใช้บริการ |
| GC (`giftcard.spec`) | 4 | มูลค่า · หมดอายุ · ใช้บางส่วน · รหัสปลอม |
| CXL / CRS / TRN | 3 / 3 / 3 | ยกเลิก 24 ชม. · คอร์ส · รถรับส่ง |
| SEC (`security.api.spec`) | 5 | ไม่ login · รูปของคนอื่น · API หลังร้าน · logout แล้วใช้ cookie เดิม · ใช้ของคนอื่น |
| TH / I18N / UI | 1 / 1 / 2 | รีวิวนักบำบัด · ภาษา · UI (อัปโหลด `fixtures/selfie-test.png`) |
| **รวม** | **42** | P1 33 · P2 8 · P3 1 (จาก `plan-cases.json`) |

- **ต้องใช้ไฟล์ของบท:** `plan-cases.json` (ชื่อ test, tag และ annotation มาจากไฟล์นี้ · `tc()` throw ถ้าไม่มี id) · `scripts/index-reporter.mjs` ถูกอ้างใน config (และ import `build-report.mjs`) · `scripts/extract-plan.mjs` อ่าน `../TEST-PLAN.md` (ใช้เฉพาะตอน `npm run plan`) · `fixtures/selfie-test.png`
- **ผูกกับ selector:** testid 172 จุด · assert ข้อความ 38 จุด · เงินอ่านจาก `data-amount` · ราคารอให้ `/api/price` นิ่งก่อน (`settle`) · มี API call 30 จุด · ใช้ผู้ใช้ seed U01–U08 + owner และรหัสนัด/คอร์ส (B05, B06, C01) แบบ hard-code → ถ้า CR แก้ seed เทสต์จะแดง
- **test.fail / skip:** ไม่มี `test.fail` · ถ้า reset ไม่สำเร็จจะ `info.skip` (นับเป็น "ไม่ได้รัน")
- **ล้มอยู่แล้วแม้ `BUG_MODE=0`** (รันเต็มชุด 2 รอบหลังสุดใน `normal-mode/test-report/history.json` ได้ผลตรงกัน · รอบก่อนหน้านั้น webkit ล้ม 3 ข้อ):

| TC | ประเภท (จาก `triage.json`) | อาการ |
|---|---|---|
| TC-TRN-03 | เว็บผิด | ติ๊กรถรับส่งแต่ไม่ใส่ระยะ ก็ยังไปขั้น 4 ได้ |
| TC-GC-04 | เว็บผิด | ใส่รหัสบัตรปลอมแล้วไม่มีข้อความเตือน |
| TC-SEC-04 | เว็บผิด | logout แล้วใช้ cookie เดิมยังได้ 200 (ไม่เพิกถอน session) |
| TC-SEC-05 | แผนผิด | จองด้วยคอร์สของคนอื่นได้ 422 แทน 403/404 ที่คาดไว้ (ความคาดหวังเก่า) |

- **ล้มเพิ่มเมื่อ `BUG_MODE=1`:** TC-BOOK-03, TC-BOOK-07 (timeout 90 วิ), TC-MEM-03, TC-PRICE-04, TC-MEM-04
- **ความเร็ว (ผลที่บันทึกไว้):** api 6 ข้อรวม ~2 วินาที · chromium 36 ข้อ 5.9 นาที (รอบนั้นเป็นโหมด GIF ที่มี slowMo) · firefox 4.0 นาที · webkit 4.9 นาที · เต็มชุด ~13 นาที (`BUG_MODE=0`) และ 17.8 นาที (`BUG_MODE=1`) → **api + chromium แบบไม่อัด GIF น่าจะใช้ราว 4–5 นาที** (ประมาณจาก firefox และ webkit ยังไม่ได้วัด)

### 3.4 `web/scripts/check-rules.mjs` (มีอยู่ใน `06/web/scripts/` แล้ว)

- **วิธีรัน:** `cd web; node scripts/check-rules.mjs` · `BASE_URL` (ค่าเริ่มต้น `http://localhost:3000`) · Node ≥ 22.18 (unit test import ไฟล์ `.ts` ตรง ๆ) · `npm run check-rules` ก็ได้ · exit 1 ถ้ามีข้อล้ม และ exit 2 ถ้าเว็บหรือ db ไม่พร้อม
- **ครอบคลุม:** BR-01–BR-20 ตามตาราง E01–E90 · ยิงผ่าน `/api/slots` `/api/price` `/api/bookings` `/api/admin/bookings` · unit 7 เคสเรียกฟังก์ชันใน `lib/rules` · E90 ตรวจว่ายอดหน้าสรุป = ยอดใน db สำหรับทุกการจองใน E26–E89
- **ผูกกับ UI:** ไม่ผูกเลย (ไม่ใช้ DOM/testid) · ผูกกับ API contract, ข้อความ error (`MSG`), ผู้ใช้ seed และชื่อ export ใน `lib/rules/index.ts`
- **ผลที่บันทึกไว้:** `BUG_MODE=0` ได้ 90/90 · `BUG_MODE=1` ได้ 80/90 (ล้ม E05 E07 E09 E20 E39 E40 E50 E87 E88 E89) · ยังไม่มีการบันทึกเวลาที่ใช้ (ไม่ใช้เบราว์เซอร์ จึงน่าจะเร็ว แต่ยังไม่ได้วัด)
- **ข้อสังเกต:** คอมเมนต์หัวไฟล์อ้าง `TEST-DATA.md` / `REQUIREMENTS.md` ซึ่งไม่มีในบท 06 (ตรงกับ legacy จริง คือมีเอกสารอ้างอิงที่หายไปแล้ว) · `tsconfig.json` ของ web exclude `scripts` ไว้แล้ว จึงไม่กระทบ `next build`

---

## 4. คำแนะนำพร้อมรายการไฟล์

> **ตำแหน่งต้องเป็นโฟลเดอร์คู่กัน ห้ามวางข้างในโฟลเดอร์แอป** เพราะ `tsconfig.json` ของ `petshop/` include `**/*.ts` และของ `web/` exclude แค่ `scripts` → ถ้าวาง e2e ไว้ข้างใน `next build` (และ Docker build context) จะดึงไฟล์เทสต์เข้าไปด้วยและ type-check ไม่ผ่าน (ไม่มี `@playwright/test` ในแอป) · รูปแบบนี้ตรงกับบท 02 (`e2e/` อยู่ข้าง `petshop/`) และบท 04 (`e2e/` อยู่ข้าง `web/`)

### 4.1 บท 05 → `05_rea-reverse-engineer-legacy-petshop/e2e-legacy/`

| คัดลอกจาก `02_petshop-test-from-plan/e2e/` | สิ่งที่ต้องทำ |
|---|---|
| `package.json` | ลบสคริปต์ `test:gif` และ devDependency `cross-env` · เปลี่ยน name เป็น `pawpantry-legacy-e2e` · เหลือ `test`, `test:ui`, `report` |
| `package-lock.json` | คัดลอกมา แล้วผู้สร้างบทรัน `npm install` 1 ครั้งให้ lock ตรงกับ package.json ที่แก้ |
| `playwright.config.ts` | ลบ `GIF` และทุก branch ที่เกี่ยว · reporter เหลือ `[['list'], ['html', { open: 'never' }]]` (ลบ `./reporters/tester-report.ts`) · projects: ค่าเริ่มต้น `chromium` อย่างเดียว และเปิด firefox+webkit เมื่อ `ALL_BROWSERS=1` · คง `fullyParallel: true`, `workers: 4`, `timeout: 45_000` |
| `global-setup.ts` | ใช้ได้เลย (ข้อความ error บอกให้ไปรัน docker ในโฟลเดอร์ `petshop` ซึ่งตรงกับ layout ของบท 05) |
| `tsconfig.json`, `.gitignore` | ใช้ได้เลย |
| `tests/fixtures.ts` | ลบ `overlayScript` และ override `page` ของโหมด GIF → `export const test = base` · ส่วนอื่นคงไว้ |
| `tests/01-home … 10-mobile-api.spec.ts` (10 ไฟล์) | ใช้ได้เลย (40 test) |
| ~~`reporters/tester-report.ts`~~ | **ไม่คัดลอก** (ต้องใช้ ffmpeg/GIF และตาราง MODULES ที่ผูกกับแผนบท 02) |

**คำสั่งรันในบท 05:** `cd petshop; docker compose up -d --build` → `cd ..\e2e-legacy; npm install; npx playwright install chromium; npx playwright test`

**ต้องตัดสินใจเรื่อง BUG_MODE:**
- ถ้าบท 05 ให้ผู้เรียนล่าบั๊กด้วย REA เมื่อ `BUG_MODE=1` → suite นี้จะเฉลยทันที (TC-CPN-01, TC-WISH-02, TC-CHK-02 แดง) · ทางเลือกคือ (ก) บอกว่า "ล็อก baseline ที่ `BUG_MODE=0`" แล้วใช้ suite เป็นแค่ตาข่ายกันพังตอนแก้โค้ด หรือ (ข) ลบ 3 ข้อนี้ออก แล้วบอกว่า "legacy suite ไม่ได้ครอบคลุมเรื่องนี้" (ตรงกับระบบจริงที่ coverage มีรู)
- **annotation `expected`** ในไฟล์ spec คือ "spec ที่รันได้" → ถ้าบท 05 อยากให้กู้ spec ด้วย REA หรือ black-box อย่างเดียว ให้ซ่อน suite ไว้จนกว่าจะถึง LAB "เปลี่ยนแปลงอย่างปลอดภัย" หรือใช้เป็นแหล่งหลักฐานอีกทาง (เทียบว่า "อ่านจากเทสต์" กับ "กู้จาก bundle" ได้อะไรต่างกัน)

**ข้อเลือกเสริม (ทำให้ legacy สมจริง):** ถ้าอยากมี "เทสต์เก่าที่แดงแม้ระบบไม่ได้พัง" ให้เขียน TC-SRCH-01 ของบท 03 ใหม่ (ทุกการ์ดต้องมีคำค้นในชื่อ ซึ่งล้มที่ `BUG_MODE=0` เพราะ "สูตรลดก้อนขน" ค้นเจอจากส่วนผสม) ด้วยสไตล์บท 02 เป็น `tests/11-search-legacy.spec.ts` · แต่บท 05 เป็นบทพื้นฐาน จึงแนะนำให้เริ่มจาก **baseline เขียวทั้งชุด** ก่อน แล้วไปสอนเรื่องเทสต์แดงค้างในบท 06

### 4.2 บท 06 → ชั้น ① `web/scripts/check-rules.mjs` (ไม่ต้องคัดลอก) + ชั้น ② `06_sabai-spa-legacy-change-request/e2e-legacy/`

**ชั้น ①:** ใช้ตามที่มี · ถ้าจะทำให้เป็น gate ให้บอกผู้เรียนว่า "ก่อนและหลังแก้ CR ต้องรัน `node scripts/check-rules.mjs` ให้ได้ 90/90 (หรือได้ตามที่ CR ตั้งใจเปลี่ยน)" · ถ้า CR เปลี่ยนกฎธุรกิจ (เช่น BR-20) ผู้เรียนต้อง**แก้ค่าคาดหวังของเคส E ที่เกี่ยวข้องอย่างมีเหตุผล** ซึ่งเป็นจุดสอน "regression ที่ตั้งใจ" กับ "regression ที่ไม่ตั้งใจ"

**ชั้น ②:**

| คัดลอกจาก `04_…/_solution/e2e/` | สิ่งที่ต้องทำ |
|---|---|
| `package.json` | scripts เหลือ `test`, `test:p1` · ลบ `test:gif`, `report`, `plan` · name `sabai-legacy-e2e` |
| `package-lock.json` | คัดลอกมา (dependency ไม่เปลี่ยน ใช้ได้เลย) |
| `playwright.config.ts` | reporter เหลือ `[['list'], ['html', { open: 'never', outputFolder: 'test-report/html' }]]` (**ต้องลบ** `./scripts/index-reporter.mjs` ไม่งั้นหาไฟล์ไม่เจอ) · ลบ GIF/slowMo/video · projects ค่าเริ่มต้น `api` + `chromium` และเพิ่ม firefox+webkit เมื่อ `ALL_BROWSERS=1` · คง `workers: 1` (reset ฐานเดียวกันและเลื่อนนาฬิกา) |
| `global-setup.ts` | ใช้ได้เลย (ใช้ `config.projects[1]` หา baseURL ซึ่งยังมีอยู่ใน config แม้รันแค่บาง project) · จะเก็บหรือลบส่วนเขียน `test-report/meta.json` ก็ได้ |
| `tsconfig.json` | ใช้ได้เลย |
| `.gitignore` | เขียนใหม่สั้น ๆ: `node_modules/` `test-report/` `test-results/` |
| `plan-cases.json` | **ต้องมี** (`tc()` ใช้) · ข้อความ expected ในไฟล์อ้าง BR/FR/TEST-DATA ที่ไม่มีในบท 06 (ตรงกับ legacy จริง) · จะเปลี่ยนชื่อเป็น `cases.json` ก็ได้ แต่ต้องแก้ path ใน `fixtures.ts` บรรทัด 13 ด้วย |
| `fixtures/selfie-test.png` | **ต้องมี** (`ui.spec.ts` TC-UI-02 ใช้) |
| `tests/fixtures.ts` | ลบ `overlayScript`, `convertVideo`, `spawnSync` และส่วน GIF ใน `page` · คง `api` log ไว้ได้ (เขียน `test-report/logs/`) |
| `tests/*.spec.ts` (12 ไฟล์) | ใช้ได้เลย + ติดป้าย known failures ตามตารางล่าง |
| ~~`scripts/*`, `triage.json`, `index.html`, `normal-mode/`, `test-report/`~~ | **ไม่คัดลอก** (เป็นเครื่องมือรายงานและเฉลยของบท 04) |

**Known failures (`BUG_MODE=0`):** ใส่ไว้บรรทัดแรกของ body ของ `tc()` · Playwright ยอมให้เรียก `test.fail()` ข้างใน test

| TC | แนะนำ | เหตุผล |
|---|---|---|
| TC-TRN-03 | `test.fail(true, 'KNOWN-ISSUE ไม่บังคับระยะรถรับส่ง')` | บั๊กจริงของระบบเดิม เหมาะเป็นโจทย์แก้บั๊ก · ถ้าแก้แล้ว test จะขึ้น "expected to fail but passed" → ผู้เรียนต้องเอา `test.fail` ออก |
| TC-GC-04 | `test.fail(true, 'KNOWN-ISSUE ไม่เตือนรหัสบัตรปลอม')` | เหมือนข้อบน |
| TC-SEC-04 | `test.fail(true, 'KNOWN-ISSUE session ไม่ถูกเพิกถอน')` | เหมือนข้อบน (เป็นโจทย์ security ที่ดี) |
| TC-SEC-05 | **ไม่ติดป้าย** ปล่อยแดงไว้ (หรือ `test.fixme` พร้อมเขียนว่า "ความคาดหวังเก่า: เว็บตอบ 422") | ใช้เป็นข้อสอบ "เทสต์แดงนี้คือบั๊ก หรือเทสต์ที่ล้าสมัย" · ระบบปฏิเสธถูกแล้ว แค่ status code ไม่ตรงกับที่แผนเดิมคาด |

→ หลังติดป้าย baseline ที่ `BUG_MODE=0` จะเป็น **เขียว 41 + แดงที่รู้สาเหตุ 1** (ประมาณจากผลที่บันทึกไว้ ยังไม่ได้รันยืนยัน)

**คำสั่งรันในบท 06:** `docker network create sabai-net` (ครั้งแรก) → `docker compose -f db/compose.yaml up -d` → `docker compose -f web/compose.yaml up -d --build` → `cd e2e-legacy; npm install; npx playwright install chromium; npx playwright test` (~4–5 นาที, ประมาณ) · ลัด `npm run test:p1` · ตาข่ายแบบเร็ว `cd ..\web; node scripts/check-rules.mjs`

---

## 5. ความเสี่ยงที่เจอระหว่างตรวจ (ควรแก้ตอนออกแบบบท 05–06)

| เรื่อง | รายละเอียด | ข้อเสนอ |
|---|---|---|
| พอร์ตและชื่อ container ชนกัน | `petshop` (บท 02/03/05) และ `sabai-web` (บท 04/06) ใช้พอร์ต **3000** และ `container_name` ตายตัว · suite ทุกชุดมีค่าเริ่มต้น `BASE_URL=http://localhost:3000` | ให้ README บอกว่า "ปิดบทเก่าก่อน" หรือเปลี่ยนพอร์ตของบทใหม่ (เช่น 3005/3006) แล้วตั้ง `BASE_URL` ใน config ของ `e2e-legacy` |
| image tag ใช้ร่วมกัน | `pawpantry:latest` และ `sabai-web:latest` เป็นชื่อเดียวกับบทเก่า → พอ build บทที่แก้แล้ว image ของบทเก่าจะถูกทับ | ตั้ง `image:` ใหม่ในบท 05/06 (เช่น `pawpantry-legacy:latest`, `sabai-web-legacy:latest`) |
| **volume ของ db ใช้ร่วมกัน** | `06/db/compose.yaml` ใช้ volume ชื่อ `sabai-pgdata` เดียวกับบท 04 · `docker-entrypoint-initdb.d` จะรันเฉพาะตอน volume ยังว่าง → ถ้า CR ของบท 06 แก้ `db/init` (เช่นเพิ่มคอลัมน์) แต่เครื่องผู้เรียนมี volume จากบท 04 อยู่แล้ว **schema ใหม่จะไม่ถูกสร้าง** | เปลี่ยนชื่อ volume/project ในบท 06 หรือให้ LAB 0 สั่ง `docker compose down -v` ของบท 06 ก่อน |
| เปิดเผย BUG_MODE | Sabai มี `<html data-bug-mode>` (global-setup และ check-rules อ่านค่านี้) · `06/web/SPEC.md` (49 KB) ยังอยู่ใน 06 | ถ้าอยากให้บท 06 เป็น "ระบบรัฐที่เอกสารไม่ครบ" ให้พิจารณาว่าจะเก็บ SPEC.md ไว้หรือย้ายไป `_solution` |
| เทสต์ผูกกับ seed | ทั้งสอง suite ใช้ผู้ใช้/สินค้า/รหัสนัดจาก seed แบบ hard-code | CR ที่แก้ seed ต้องแก้เทสต์ด้วย → ใช้เป็นจุดสอน impact analysis ได้ |
