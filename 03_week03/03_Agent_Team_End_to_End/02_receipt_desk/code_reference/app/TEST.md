# TEST.md · ReceiptDesk: รวมระบบและทดสอบเบื้องต้น (B14)

ทดสอบเมื่อ 2026-11-19 13:20–13:31 (Asia/Bangkok) บนเครื่องเดียว (Linux/WSL2 · Docker 29.9.3 · Compose v5.7.0 · Node 22)
ฝั่งเว็บรันด้วย `AI_MODE=mock` และ `BUG_MODE=0` ส่วนฝั่ง AI ที่ต้องใช้ GPU ยังไม่ได้รัน (ดูหัวข้อ 6)

## สรุปผลตามเกณฑ์เสร็จ

| # | เกณฑ์ | ผล | หลักฐาน |
|---|---|---|---|
| 1 | `docker compose up` ฝั่งเว็บขึ้นครบ 3 service และ `/api/health` ตอบ 200 | ✅ ผ่าน | หัวข้อ 2 · H-01 |
| 2 | ใช้ `logo.png` | ✅ ผ่าน | H-02 · H-03 (ใช้ในเมนู หน้า login และ favicon) |
| 3 | `AI_MODE=mock`: อัปโหลดชุด → อ่าน → ตรวจแก้ → ยืนยัน → CSV ยอดตรงกับ TEST-DATA หัวข้อ 5 | ✅ ผ่าน | หัวข้อ 3 (API 34/34) · หัวข้อ 4 (UI) |
| 4 | `rules.test.ts` ผ่าน | ✅ ผ่าน 89/89 | หัวข้อ 1 |
| 5 | คิวเต็มได้ 429 และบอกจำนวนนาที N | ✅ ผ่าน 7/7 | หัวข้อ 3.3 |

---

## 0. งานรวมระบบที่ B14 เพิ่มหรือแก้

| ไฟล์ | การเปลี่ยนแปลง | เหตุผล |
|---|---|---|
| `web/package.json` (+ `package-lock.json`) | ใหม่: next 16.4.6 · react/react-dom 19 · pg · tsx · dev typescript 7 และ @types/* · script `dispatcher` และ `test` | B01 ยังไม่ได้สร้างไฟล์นี้ (บันทึกบนกระดานโดย B04 และ B11) |
| `web/Dockerfile` · `web/.dockerignore` | ใหม่: build แบบ multi-stage บน node:22-bookworm-slim และใช้อิมเมจเดียวกันทั้ง web และ dispatcher | `docker-compose.yml` ของ B01 อ้างถึงไฟล์นี้ |
| `web/next.config.mjs` · `web/tsconfig.json` | ใหม่: `serverExternalPackages:['pg']` · strict | ตามที่ B04 ทดสอบไว้ |
| `web/app/review/page.tsx` | คัดโค้ดจาก `out/B12.md` (ผลของ B12) มาเป็นไฟล์ | B12 ส่งผลเป็นเอกสาร ยังไม่มีไฟล์ในโปรเจกต์ |
| `web/app/receipts/[id]/page.tsx` | ใหม่: `export { default } from '../../review/page'` | ทำให้ `/receipts/{id}` ตาม DESIGN 9.1 ใช้งานได้ ตามคำแนะนำของ B12 |
| `web/app/login/page.tsx` · `web/app/layout.tsx` | เพิ่มโลโก้ในหน้า login (`login-logo`) และตั้ง favicon เป็น `/logo.png` | เกณฑ์ "ใช้ logo.png" เดิมโลโก้มีแค่ในเมนูหลังเข้าสู่ระบบ |
| `docker-compose.yml` | mount `web/db/schema.sql` เป็น `/docker-entrypoint-initdb.d/01-schema.sql` · เพิ่ม healthcheck ของ web · ส่ง `AI_MODE` ให้ web | ให้ฐานข้อมูลมี schema ตั้งแต่สร้าง และให้ `/api/health` รายงานโหมดได้ถูก |
| `.env.example` · `.env.test` | ใหม่ | `.env.test` ใช้ทดสอบเท่านั้น (เปิด `ENABLE_TEST_RESET=1`) |
| `ai/nginx/nginx.conf` | สร้างด้วย `python -m ai.worker.worker --nginx-conf --upstreams 127.0.0.1:8001,127.0.0.1:8002` | B09 แจ้งบนกระดานว่ายังไม่มีไฟล์นี้ (ต้องแก้ upstream ให้ตรงเครื่อง GPU จริง) |
| `tests/e2e-api.mjs` · `tests/fixtures/*` | ใหม่: สคริปต์ทดสอบ end-to-end และไฟล์ทดสอบ | หลักฐานของหัวข้อ 3 |

ตรวจด้วย: `tsc --noEmit` ไม่มี error และ `next build` ผ่าน ได้ 35 route รวม `/review` และ `/receipts/[id]` · `python -m py_compile` ของ `ai/**/*.py` ผ่าน

## 1. rules.test.ts

```
cd web && npm test        # = node --experimental-strip-types --test lib/rules.test.ts
# tests 89 · suites 17 · pass 89 · fail 0
```
ครอบคลุมครบ 62 รหัสของ TEST-DATA §6 (ผลเต็มอยู่ที่ `tests/rules-test.out.txt`)

## 2. docker compose ฝั่งเว็บ

```
docker compose -p receiptdesk --env-file .env.test up -d --build
docker compose -p receiptdesk ps
  db          Up (healthy)
  dispatcher  Up            # npm run dispatcher → tsx dispatcher/index.ts (AI_MODE=mock)
  web         Up (healthy)  # 0.0.0.0:3000
curl -i localhost:3000/api/health
  HTTP/1.1 200 OK
  {"status":"ok","db":"ok","ai":{"mode":"mock","reachable":true,"workersAlive":null},"version":"1.0.0"}
curl localhost:3000/logo.png → 200 image/png 368,692 ไบต์
```
PostgreSQL 16 โหลด `schema.sql` ตอน init ครั้งแรก และ `POST /api/test/reset` คืน `{"ok":true,"counts":{"users":6,"clients":3,"receipts":8}}`

## 3. End-to-end ผ่าน API (`node tests/e2e-api.mjs` → ผ่าน 34 · ไม่ผ่าน 0)

ผลเต็มอยู่ที่ `tests/e2e-api.out.txt` สคริปต์เรียก reset ก่อนเริ่มและหลังจบทุกครั้ง

### 3.1 ผลรวมจากข้อมูลตั้งต้น (TEST-DATA §5)
ยอดในตารางรวมจากแถวในไฟล์ CSV เอง แล้วเทียบกับ header `X-Report-Total` และ `X-Report-Count` อีกชั้น

| รหัส | คาด | ได้ | ผล |
|---|---|---|---|
| E-01 CL-01 2026-10 | 150.00 · 1 ใบ | 150.00 · 1 แถว | ✅ |
| E-02 CL-01 2026-11 | 1,340.00 · 4 ใบ | 1340.00 · 4 แถว | ✅ |
| E-03 CL-01 2026-12 | 75.25 · 1 ใบ | 75.25 · 1 แถว | ✅ |
| E-04 CL-02 2026-11 | 999.00 · 1 ใบ | 999.00 · 1 แถว | ✅ |
| E-05 หมวด CL-01 2026-11 | 1,200.50 / 40.00 / 99.50 / 0.00 = 1,340.00 | ตรงทุกหมวด | ✅ |
| E-06 CL-03 2026-11 | 0.00 · 0 ใบ · มีแต่หัวตาราง | หัวตาราง `receipt_date,merchant,category,total,file_name,confirmed_by,confirmed_at,receipt_id` · 0 แถว | ✅ |

หลังทดสอบขั้น 3.2 แล้ว E-01 ถึง E-05 ยังตรงเหมือนเดิม (ตรวจซ้ำแล้วผ่าน)

### 3.2 อัปโหลด → อ่าน → ตรวจแก้ → ยืนยัน → CSV
ใช้ U-01 (คุณพิมพ์) อัปโหลดให้ CL-03 ซึ่งเป็นร้านที่ไม่มีใบตั้งต้น เพื่อไม่ให้ E-01 ถึง E-05 เปลี่ยน

| รหัส | ขั้น | ผล |
|---|---|---|
| F-01 | อัปโหลด 5 ไฟล์ `ok-100` `conf-089` `diff-101` `fail3` `total-000` | ✅ 201 · accepted=5 |
| F-02 | dispatcher (mock) อ่านจบ | ✅ review 4 · unreadable 1 (`fail3` อ่านครบ 3 ครั้งแล้วไม่สำเร็จ ตาม BR-07) |
| F-03 | ธง BR-04/BR-05 | ✅ ok-100 ไม่ติดธง · conf-089 ติด "ไม่แน่ใจยอดรวม" · diff-101 ติด "ยอดไม่ตรงรายการ" |
| F-04 | ยืนยันใบติดธงที่ยังไม่เปิดดู | ✅ 409 `review_not_opened` (FR-12) |
| F-05 | เปิดใบ → PATCH → ยืนยัน 4 ใบ | ✅ ok-100 100.00 · conf-089 แก้เป็น 100.50 · diff-101 แก้ราคาบรรทัด 3 แล้วยอดเป็น 100.00 · fail3 กรอกเองเป็น 35.75 (`enteredManually=true`) |
| F-06 | ยืนยันใบยอด 0.00 | ✅ 422 `total_invalid` (BR-06) |
| F-07 | ประวัติการแก้ | ✅ `total 100.00→100.50` และ `category_id` มีชื่อผู้แก้ |
| F-08 | CSV ของ CL-03 2026-11 | ✅ 336.25 · 4 แถว = 100.00 + 100.50 + 100.00 + 35.75 |
| F-09 | กระทบยอดชุด | ✅ accepted 5 = sum 5 · diff 0 |

### 3.3 คิวเต็ม: 429 และบอก N นาที (BR-11/12)
แต่ละแถว reset ใหม่ แล้วอัปโหลด 100 ใบปกติให้ CL-01 ภายใน 30 วินาทีหลัง reset เพื่อให้ `workersAlive` ยังไม่หมดอายุ

| รหัส | ค้าง · Worker | คาด | ได้ |
|---|---|---|---|
| TD-BR11-b | 300 · 2 | รับ 100 · ค้าง 400 | ✅ 201 · ค้าง 400 |
| TD-BR11-c / BR12-a | 301 · 2 | 429 · N=1 | ✅ 429 `queue_full` · N=1 · `Retry-After: 60` · "ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก 1 นาที" · ค้างยังเป็น 301 |
| TD-BR12-d | 309 · 2 | N=2 | ✅ N=2 · Retry-After 120 |
| TD-BR12-e | 380 · 2 | N=10 | ✅ N=10 · Retry-After 600 |
| TD-BR12-f | 400 · 2 | N=13 | ✅ N=13 · Retry-After 780 |
| TD-BR12-g | 309 · 1 | N=3 | ✅ N=3 · Retry-After 180 |
| TD-BR12-h | 380 · 0 (นับเป็น 1 ตัว) | N=20 | ✅ N=20 · Retry-After 1200 |

## 4. ทดสอบผ่านหน้าเว็บจริง (Playwright · Chromium)
หน้าตรวจแก้ของ B12 ยังไม่เคยรันกับ API จริงมาก่อน จึงทดสอบเพิ่มด้วยมือ ภาพหน้าจอผลอยู่ที่ `tests/review-confirmed.png`

1. `/login` แสดง `login-logo` · เข้าสู่ระบบเป็น pim แล้วถูกพาไปหน้าแรกของบทบาท ✅
2. `/upload` เลือก CL-03 แล้วส่ง `tests/fixtures/conf-089__ui1.png` กับ `ok-100__ui2.png` → `upload-accepted-count` = 2 ✅
3. `/review` คิวรอตรวจ 3 แถว ใบติดธงแยกตาราง และแสดงเหตุผล "ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90" ✅
4. `/receipts/{id}` (ใช้หน้า re-export) แสดง `flag-low-confidence` และ `receipt-image` ✅
   - ติ๊ก `total-checked-checkbox` แล้ว ปุ่มยืนยันยังกดไม่ได้จนกว่าจะโฟกัสครบทุกช่อง (FR-12) ✅
   - โฟกัสครบ 5 ช่อง แก้ยอดเป็น 100.50 และเลือกหมวด "ค่าแก๊ส" แล้วปุ่มกดได้ ✅
   - กดยืนยัน → `receipt-status` = "ยืนยันแล้ว" · `confirmed-by` = "ยืนยันโดย คุณพิมพ์ เมื่อ 19 พ.ย. 2569 13:29" · ประวัติ 2 แถว ✅
   - ในฐานข้อมูล `conf-089__ui1.png | confirmed | 100.50` ✅

## 5. วิธีรันซ้ำ

```bash
cd /workspace/plans/receiptdesk/app
docker compose -p receiptdesk --env-file .env.test up -d --build   # AI_MODE=mock · ENABLE_TEST_RESET=1
(cd web && npm ci && npm test)                                     # rules.test.ts
BASE=http://localhost:3000 TOKEN=b14-test-token node tests/e2e-api.mjs
docker compose -p receiptdesk down          # เพิ่ม -v ถ้าต้องการลบฐานข้อมูลและไฟล์อัปโหลด
```
ตอนส่งงาน stack ยังรันอยู่ (project `receiptdesk` · พอร์ต 3000) และข้อมูลถูก reset กลับเป็นข้อมูลตั้งต้นแล้ว

## 6. สิ่งที่ยังไม่ได้ทดสอบหรือต้องระวัง

- **ฝั่ง AI บน GPU ยังไม่ได้รันจริง** ได้แก่ gateway, RabbitMQ, Worker 2 ตัว, NGINX และ vLLM 2 ตัว เพราะเครื่องนี้ไม่มี GPU ที่ตรวจได้คือ `py_compile` ผ่าน และสร้าง `ai/nginx/nginx.conf` ได้ ส่วน NFR-02/03, BR-10 (4:1) แบบ end-to-end, DLQ จริง และ Training/Evaluation ต้องทดสอบบนเครื่อง GPU (B06 กำหนดเกณฑ์ไว้ที่ ≥ 3.8 ใบ/นาทีต่อ Worker)
- **`ai/docker-compose.yml` ยังไม่มี** เพราะ B01 เขียนแค่ compose ฝั่งเว็บ
- **TD-BR13-b**: seed ตั้งเวลารับไว้ที่ `reset − 120 นาที` พอดี หลัง reset เพียงไม่กี่มิลลิวินาที หน้า "ค้างเกินกำหนด" จะแสดง 2 ใบ ไม่ใช่ 1 ใบตาม TEST-DATA (B03/B04 บันทึกไว้แล้ว) จึงไม่ได้นับเป็นเกณฑ์ของ B14
- ใน `AI_MODE=mock` ไม่มีใครอัปเดต `workers_alive` การทดสอบ BR-12 ที่ใช้ Worker 2 ตัวจึงต้องอัปโหลดภายใน 30 วินาทีหลัง reset (สคริปต์ทำตามนี้แล้ว)
- ใบตั้งต้น S-01 ถึง S-08 ไม่มีไฟล์รูป `/image` ของใบเหล่านี้จึงตอบ `404 image_missing` ตามที่ออกแบบไว้
- ตอน `npm install` นอก Docker สคริปต์ postinstall ของ esbuild ถูกบล็อก แต่ `tsx` ยังทำงานได้ และใน Docker ไม่มีปัญหานี้
