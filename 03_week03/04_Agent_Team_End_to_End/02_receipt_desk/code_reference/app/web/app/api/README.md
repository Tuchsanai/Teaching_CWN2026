# API ของเว็บ ReceiptDesk (บล็อก B04)

สิทธิ์ 4 บทบาท + API 23 เส้นตาม DESIGN 9.2 (รวม `/api/health` ตาม 9.3) · Next.js App Router (`route.ts`) · PostgreSQL ผ่าน `pg`

ทุกการตัดสินตาม Business Rule เรียก `web/lib/rules.ts` (B03) ไม่มีการเขียนเส้นแบ่งของกฎซ้ำในโค้ด route หรือใน SQL
ช่วงเวลาที่ใช้ใน SQL (วันไทยของ BR-09 · เดือนของ BR-14 · เส้นค้างของ BR-13) ก็มาจาก rules.ts
`BUG_MODE` จึงมีผลกับ API แบบเดียวกับโมดูลกฎ (DESIGN 9.6) โดย route ไม่อ่าน `BUG_MODE` เอง

## 1. โครงไฟล์

```
web/app/api/
├── _lib/                 # ไม่ใช่ route (โฟลเดอร์ขึ้นต้นด้วย _)
│   ├── db.ts             # Pool · transaction() · dbNow() · isUuid() · คอลัมน์ date คืนเป็น 'YYYY-MM-DD'
│   ├── auth.ts           # session · cookie rd_session · requireUser(roles) · กลุ่มบทบาท OFFICE / EDITORS / LEAD_ONLY
│   ├── http.ts           # ApiError · ruleError(RuleViolation) · handle() · json()
│   ├── receipts.ts       # SELECT ใบ + กรองร้าน · มุมมองสำนักงาน / ลูกค้า · เหตุผลของธง
│   └── edits.ts          # แก้ค่า + receipt_edits (W14 · W15)
├── reports/_month.ts     # ตัวช่วย BR-14 ของ W18 · W19
├── health/ test/reset/ auth/login/ auth/logout/ me/ clients/ queue/
├── batches/ batches/[id]/ batches/[id]/urgent/
├── receipts/ receipts/[id]/ receipts/[id]/{image,confirm,reopen,history}/
└── reports/{monthly,categories,reconcile,review-time,gpu}/
```

แพ็กเกจที่ `web/package.json` ต้องมีสำหรับ API ชุดนี้: `next` (15 ขึ้นไป · `params` เป็น Promise) และ `pg` (+ `@types/pg`)
แนะนำ `serverExternalPackages: ['pg']` ใน `next.config` · ไม่ใช้ bcrypt ฝั่ง Node เพราะตรวจรหัสผ่านด้วย `crypt()` ของ pgcrypto (B02)

ตัวแปรสภาพแวดล้อม: `DATABASE_URL` · `UPLOAD_DIR` (ค่าตั้งต้น `/app/uploads`) · `SESSION_SECRET` · `ENABLE_TEST_RESET` · `TEST_RESET_TOKEN` · `BUG_MODE` (อ่านใน rules.ts) · `AI_MODE` (ใช้แค่ในคำตอบของ health ถ้าตั้ง) · `COOKIE_SECURE` (ไม่ต้องตั้ง: `1` บังคับ Secure และ `0` ปิด ถ้าไม่ตั้งจะดูจาก https)

## 2. การเข้าสู่ระบบและสิทธิ์

- `POST /api/auth/login` สร้างแถวใน `sessions` (token สุ่ม 32 ไบต์ อายุ 12 ชั่วโมง) แล้วตั้ง cookie `rd_session` แบบ `HttpOnly; SameSite=Lax`
  ถ้าตั้ง `SESSION_SECRET` ค่า cookie จะมีลายเซ็น HMAC-SHA256 ต่อท้ายและถูกตรวจทุกคำขอ
- ทุกเส้นยกเว้น `/api/health` · `/api/auth/login` · `/api/test/reset` ต้องมี session ถ้าไม่มีจะได้ `401 {"error":"unauthenticated"}` ก่อนตรวจอย่างอื่น
- บทบาทไม่อยู่ในรายชื่อที่เรียกเส้นนั้นได้ → `403 {"error":"forbidden"}` (ตรวจก่อนหาข้อมูล จึงไม่บอกว่าข้อมูลมีอยู่หรือไม่)
- **บัญชีลูกค้า** (DESIGN 8 · FR-24 · FR-25 · FR-27 · NFR-07)
  - คำสั่งอ่านทุกคำสั่งกรอง `r.client_id = <client_id ของ session>` ที่ SQL ถ้าขอใบร้านอื่น หรือส่ง `clientId` ร้านอื่น จะได้ `404 not_found`
  - ใบที่ยังไม่ `confirmed` ส่งออกเฉพาะ `id · fileName · acceptedAt · status:"received" · statusLabel:"รับแล้ว รอสำนักงานตรวจ"` ไม่มีตัวเลข ธง หรือชื่อร้านจากการอ่าน
  - ใบที่ยืนยันแล้วเพิ่ม `merchant · receiptDate · total · categoryId/Name · confirmedAt` และใน W12 มี `items` ด้วย
  - อัปโหลดได้เฉพาะร้านตัวเอง ถ้าส่ง `clientId` มาจะถูกแทนด้วยร้านของ session

### 2.1 ตารางสิทธิ์ของแต่ละเส้น

✓ = เรียกได้ · ✗ = ได้ `403 forbidden` · ผู้ไม่เข้าสู่ระบบได้ `401 unauthenticated` ทุกเส้นยกเว้น W1–W3

| # | Method + Path | ไฟล์ | พนักงาน `staff` | หัวหน้า `lead` | เจ้าของ `owner` | ลูกค้า `client` | กฎที่เรียกจาก rules.ts |
|---|---|---|---|---|---|---|---|
| W1 | `GET /api/health` | `health/route.ts` | ✓ | ✓ | ✓ | ✓ (ไม่ต้องเข้าสู่ระบบ) | `LIMITS.WORKERS_STALE_MS` |
| W2 | `POST /api/test/reset` | `test/reset/route.ts` | ผู้ทดสอบที่มี `X-Test-Token` เท่านั้น (ไม่ดู session) · `ENABLE_TEST_RESET≠1` → `404` · token ผิด → `403` | | | | — |
| W3 | `POST /api/auth/login` | `auth/login/route.ts` | ✓ | ✓ | ✓ | ✓ (ไม่ต้องเข้าสู่ระบบ) | — |
| W4 | `POST /api/auth/logout` | `auth/logout/route.ts` | ✓ | ✓ | ✓ | ✓ | — |
| W5 | `GET /api/me` | `me/route.ts` | ✓ | ✓ | ✓ | ✓ | — |
| W6 | `GET /api/clients` | `clients/route.ts` | ✓ | ✓ | ✓ | ✗ | — |
| W7 | `POST /api/batches` | `batches/route.ts` | ✓ | ✓ (`urgent=true` ได้เฉพาะคนนี้) | ✗ | ✓ ร้านตัวเอง (`urgent` → 403) | `validateUpload` (BR-01–03) · `checkUrgentSize` (BR-08) · `checkUrgentQuota` + `bangkokDayRange` (BR-09) · `checkQueueCapacity` (BR-11/12) · `resolveFileKind` |
| W8 | `GET /api/batches` | `batches/route.ts` | ✓ | ✓ | ✓ | ✗ | — |
| W9 | `GET /api/batches/{id}` | `batches/[id]/route.ts` | ✓ | ✓ (`canSetUrgent`) | ✓ | ✗ | `isOverdue` · `minutesWaiting` (BR-13) |
| W10 | `POST /api/batches/{id}/urgent` | `batches/[id]/urgent/route.ts` | ✗ | ✓ | ✗ | ✗ | `checkUrgentSize` (BR-08) · `checkUrgentQuota` + `bangkokDayRange` (BR-09) |
| W11 | `GET /api/receipts` | `receipts/route.ts` | ✓ | ✓ | ✓ | ✓ ร้านตัวเอง · ไม่มีตัวเลขก่อนยืนยัน | `overdueCutoff` · `listOverdue` · `isOverdue` (BR-13) |
| W12 | `GET /api/receipts/{id}` | `receipts/[id]/route.ts` | ✓ | ✓ | ✓ (ดูอย่างเดียว) | ✓ ร้านตัวเอง · ร้านอื่น 404 | `itemsDiffSatang` (เหตุผลธง BR-05) · `isOverdue` |
| W13 | `GET /api/receipts/{id}/image` | `receipts/[id]/image/route.ts` | ✓ | ✓ | ✓ | ✓ ร้านตัวเอง · ร้านอื่น 404 | — |
| W14 | `PATCH /api/receipts/{id}` | `receipts/[id]/route.ts` | ✓ | ✓ | ✗ | ✗ | `toSatang` · `satangToBaht` |
| W15 | `POST /api/receipts/{id}/confirm` | `receipts/[id]/confirm/route.ts` | ✓ | ✓ | ✗ | ✗ | `checkConfirmTotal` (BR-06) |
| W16 | `POST /api/receipts/{id}/reopen` | `receipts/[id]/reopen/route.ts` | ✗ | ✓ | ✗ | ✗ | — |
| W17 | `GET /api/receipts/{id}/history` | `receipts/[id]/history/route.ts` | ✓ | ✓ | ✓ | ✗ | — |
| W18 | `GET /api/reports/monthly?clientId=&month=YYYY-MM` | `reports/monthly/route.ts` | ✓ | ✓ | ✓ | ✗ | `monthBounds` · `isInMonth` · `summarizeMonth` (BR-14) · `isValidMonth` |
| W19 | `GET /api/reports/categories?month=YYYY-MM[&clientId=]` | `reports/categories/route.ts` | ✓ (ต้องระบุ `clientId`) | ✓ (ต้องระบุ) | ✓ (ต้องระบุ) | ✓ ร้านตัวเอง · ร้านอื่น 404 | `monthBounds` · `isInMonth` · `summarizeMonth` (BR-14) |
| W20 | `GET /api/reports/reconcile[?batchId=\|clientId=]` | `reports/reconcile/route.ts` | ✓ | ✓ | ✓ | ✗ | — |
| W21 | `GET /api/reports/review-time` | `reports/review-time/route.ts` | ✗ | ✓ | ✓ | ✗ | — |
| W22 | `GET /api/reports/gpu` | `reports/gpu/route.ts` | ✗ | ✗ | ✓ | ✗ | — (NFR-08: Speedup ≥ 1.6) |
| W23 | `GET /api/queue` | `queue/route.ts` | ✓ | ✓ | ✓ | ✗ | `hasQueueRoom` · `effectiveWorkers` · `retryAfterMinutes` (BR-11/12) · `canSetUrgent` + `bangkokDayRange` (BR-09) · `overdueCutoff` (BR-13) |

กฎที่ไม่อยู่ใน API: BR-04 และ BR-05 (ติดธง) คิดตอน dispatcher (B05) เขียนผลด้วย `rules.computeFlags` แล้ว API อ่านธงที่บันทึกไว้ ส่วน BR-07 และ BR-10 คิดที่ฝั่ง AI

## 3. รูปแบบคำตอบเมื่อผิด

ผิดกฎใช้ `{"error","rule","message",...}` ตาม DESIGN 9.2 ทั้งรหัส HTTP และเนื้อหามาจาก `RuleViolation` ของ rules.ts ผ่าน `ruleError()`

| สถานการณ์ | HTTP | `error` | ที่มา |
|---|---|---|---|
| ชุดว่าง หรือเกิน 100 ไฟล์ | 422 | `batch_size` (BR-01) | rules |
| ไฟล์เกิน 10 MB | 422 | `file_too_large` (BR-02) + `file` + `files[]{index,name,error,rule,message}` | rules |
| ชนิดไฟล์ไม่รับ / PDF ไม่ใช่ 1 หน้า | 422 | `file_type` / `pdf_pages` (BR-03) + `file` + `files[]` | rules |
| ระบบเต็ม | 429 | `queue_full` (BR-11) + `retryAfterMinutes` (BR-12) + `pending` + `limit` + header `Retry-After` (วินาที) · `message` = "ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก N นาที" | rules |
| ยอดรวมต่ำกว่า 0.01 | 422 | `total_invalid` (BR-06) | rules |
| งานด่วนเกิน 10 ใบ | 422 | `urgent_too_large` (BR-08) | rules |
| งานด่วนครบ 5 งานของวัน | 409 | `urgent_quota` (BR-09) + `usedToday` | rules |
| ไม่มีสิทธิ์ | 403 | `forbidden` | auth |
| ยังไม่เข้าสู่ระบบ | 401 | `unauthenticated` | auth |
| ข้อมูลของร้านอื่น / ไม่พบ / id ผิดรูป | 404 | `not_found` | |
| อีเมลหรือรหัสผ่านผิด | 401 | `invalid_credentials` | W3 |
| เนื้อหาคำขอผิดรูป | 400 | `bad_request` | |
| แก้หรือยืนยันใบที่ไม่ใช่ review/unreadable | 409 | `not_editable` | W14 · W15 |
| ยืนยันโดยไม่ติ๊ก "เทียบยอดรวมกับรูปแล้ว" | 422 | `total_not_checked` | W15 |
| ยืนยันโดยไม่มีหมวด / ไม่มีวันที่บนใบ | 422 | `category_required` / `date_required` | W15 |
| ยืนยันใบติดธงที่ยังไม่เคยเปิดดูรายละเอียด (FR-12) | 409 | `review_not_opened` | W15 |
| เปิดกลับใบที่ยังไม่ยืนยัน | 409 | `not_confirmed` | W16 |
| ไม่พบไฟล์รูปบนดิสก์ | 404 | `image_missing` | W13 |
| รอล็อกตารางนานเกิน 30 วินาที | 503 | `busy` + `Retry-After: 5` | W7 |

## 4. รายละเอียดสำหรับหน้าเว็บ (B11 · B12) และการทดสอบ (B14)

### W7 `POST /api/batches` (อัปโหลดชุด)
- `multipart/form-data` มีช่อง `files` (หลายไฟล์ หรือใช้ชื่อ `file` ก็ได้) · `clientId` (สำนักงานต้องส่ง) · `urgent` = `true`/`1`/`on`
- ลำดับ:
  1. ตรวจสิทธิ์
  2. `validateUpload` (BR-01–03 · คืนทุกไฟล์ที่ไม่ผ่านพร้อม `index` สำหรับ `upload-file-error-{ลำดับ}`)
  3. `checkUrgentSize` (BR-08)
  4. เขียนไฟล์ลง `UPLOAD_DIR/<batchId>/<receiptId>.<ext>` แล้ว fsync
  5. **ธุรกรรมเดียว**:
     - `LOCK TABLE batches IN SHARE ROW EXCLUSIVE MODE` แล้วจึง `LOCK TABLE receipts IN SHARE ROW EXCLUSIVE MODE` (ลำดับนี้เสมอ จึงไม่ deadlock กับ W10)
     - นับใบงานปกติที่ `queued + processing` ภายใต้ล็อก
     - ถ้าเป็นงานด่วน ตรวจ `checkUrgentQuota` (BR-09)
     - `checkQueueCapacity` (BR-11/12) ใช้ `workers_alive` และ `updated_at` จาก `system_state` ส่วน `now` มาจาก `clock_timestamp()`
     - INSERT `batches` + `receipts` (`queued` · `pending`) + `receipt_events` แล้ว COMMIT
- ถ้าไม่ผ่านขั้นใด ระบบ ROLLBACK และลบโฟลเดอร์ของชุด จึงไม่มีแถวหรือไฟล์ค้าง (FR-23) · ชุด 2 ชุดที่ส่งพร้อมกันไม่ทะลุเพดาน 400 (DESIGN 6.2)
- `201`: `{ batchId, accepted, priority, clientId, acceptedAt, receipts:[{id,fileName,status}], queue:{pendingNormal,limit}, urgentUsedToday?, message }`
- `file_path` ที่บันทึกเป็น path สัมพัทธ์จาก `UPLOAD_DIR` ตรงกับที่ dispatcher (B05) ใช้ · `mime_type` มาจาก magic bytes

### W9 / W11 / W12 (มุมมองของสำนักงาน)
- แต่ละใบมี `status` · `statusLabel` · `flags{lowConfidence,mismatch,flagged,reasons[]}` · `overdue` · `minutesWaiting` (เมื่อค้าง) · `merchant/receiptDate/total` · `confirmedBy/At` · `unreadableReason`
- W9 มี `batch{accepted,counts{queued,processing,review,confirmed,unreadable},sum,diff,priority,canSetUrgent}`
- W11 มีตัวกรอง `status=a,b` · `flagged=true` · `clientId` · `overdue=true` (หน้า "ค้างเกินกำหนด" · เรียงจากรอนานสุด) · `batchId` · `limit`/`offset` · คำตอบมี `count` (สำหรับ `receipts-count` · `unreadable-count` · `overdue-count`)
- W12 เพิ่ม:
  - `items[{id,lineNo,name,price,removed}]` · `itemsSum` · `imageUrl` · `totalConfidence`
  - `original{merchant,receiptDate,total,items}` (ค่าที่ระบบอ่าน)
  - `permissions{canEdit,canConfirm,canReopen}`
- **W12 ที่พนักงานหรือหัวหน้าเปิดกับใบ review/unreadable จะบันทึก `review_opened_at`** ค่านี้เป็นจุดเริ่มจับเวลาตรวจ (FR-31) และเป็นหลักฐานว่าเปิดดูแล้วก่อนยืนยันใบติดธง (FR-12) หน้าตรวจจึงต้องเรียก W12 ก่อนยืนยันเสมอ

### W14 `PATCH` และ W15 `confirm`
- body ของ PATCH: `{ merchant?, receiptDate?:"YYYY-MM-DD", total?:"100.00", categoryId?, items?:[{lineNo?, name?, price?, removed?}] }`
  - มี `lineNo` = แก้บรรทัดเดิม · ไม่มี `lineNo` = เพิ่มบรรทัดใหม่ · ลบด้วย `removed:true` (ไม่ลบแถวจริง)
  - ช่องที่เปลี่ยนจริงได้ 1 แถวใน `receipt_edits` (`merchant` · `receipt_date` · `total` · `category_id` · `item[n].name|price|removed` · `item[n]`) · ค่า `ai_*` ไม่ถูกแตะ
  - ใบ unreadable ที่ถูกแก้จะได้ `entered_manually = true` (FR-17)
  - บันทึกยอดติดลบได้ แต่ยืนยันไม่ได้ (TD-BR06-d)
- body ของ confirm: `{ totalChecked: true, categoryId, ...ช่องแก้แบบ PATCH ไม่ใส่ก็ได้ }`
  - ทั้งคำขอเป็นธุรกรรมเดียว ถ้าผิดกฎ ค่าที่แนบมากับคำขอนี้จะไม่ถูกบันทึกด้วย ถ้าต้องการเก็บค่าที่แก้ ให้ PATCH ก่อน
  - ผ่านแล้ว: `status = confirmed` · `confirmed_by` · `confirmed_at` · `review_seconds` · บันทึกแถวใน `receipt_events`
- W16 reopen: `confirmed → review` ล้าง `confirmed_by/at` และบันทึกทั้งใน `receipt_events` และใน `receipt_edits` (`field = status`)
- W17 history: `original{...}` · `current{...}` · `edits[{seq,field,oldValue,newValue,editedBy,editedAt}]` (สำหรับ `history-row-{ลำดับ}`) · `events[]`

### รายงาน
- W18:
  - ไฟล์ CSV เป็น UTF-8 มี BOM คอลัมน์ `receipt_date,merchant,category,total,file_name,confirmed_by,confirmed_at,receipt_id`
  - ไม่มีแถวยอดรวมท้ายไฟล์ เดือนที่ไม่มีใบจึงได้แต่หัวตาราง (E-06)
  - ยอดและจำนวนอยู่ใน header `X-Report-Total` และ `X-Report-Count`
  - `&format=json` คืน `{count,total,byCategory,receipts[]}` ใช้กับปุ่มดูตัวอย่าง (`report-total` · `report-receipt-count`)
- W19: `{count,total,categories:[{id,name,count,total}]}` แสดงครบทุกหมวดแม้ยอดเป็น `0.00` และผลรวมทุกหมวดเท่ากับ `total`
- W20: `{accepted,counts,sum,diff}` เมื่อ `accepted` = ผลรวม `batches.receipt_count` (สำหรับ `reconcile-accepted/sum/diff`)
- W21: `{averageSeconds,receipts,targetSeconds:120,meetsTarget,batches[]}`
- W22: `{oneGpu,twoGpu,speedup,efficiency,worth,verdict,history}` ซึ่ง `oneGpu`/`twoGpu` มี `receiptsPerMinute` และ `costPer100`
- W23: `{normal{pending,limit,room,full,retryAfterMinutesIfFull}, urgent{usedToday,limitPerDay,remainingToday,canSetMore}, workers{alive,updatedAt,usedForEstimate}, overdue}`

### W1 · W2
- W1 ตอบ `{"status":"ok","db":"ok","ai":{"mode","reachable","workersAlive"},"version":"1.0.0"}` และเป็น `503` เฉพาะเมื่อต่อฐานข้อมูลไม่ได้ ไม่บอกโหมดฝึกทดสอบ
- W2 เรียก `SELECT reset_test_data($1::jsonb, $2::text)` ของ B02 ตัวเลือกที่ผิดรูปจะได้ `400 bad_request`

## 5. ผลการตรวจ (2026-11-19)

ตรวจบนเครื่องนี้ในโฟลเดอร์ชั่วคราว (ลบแล้ว) ด้วย Next.js 16.4.6 + `pg` + PostgreSQL 16 ที่โหลด `web/db/schema.sql`

- `tsc --strict` ไม่มี error · `next build` ผ่าน · ตาราง route ของ build แสดงครบ 21 path = 23 เส้น (W7/W8 และ W12/W14 ใช้ path เดียวกันคนละ method)
- สคริปต์ทดสอบ HTTP ผ่าน 123/123 ข้อเมื่อ `BUG_MODE=0` ครอบคลุม:
  - กรณีที่ทดสอบผ่าน API ได้ใน TEST-DATA: BR-01 a–d · BR-02 a–c · BR-03 a–f · BR-06 a, b, d · BR-08 a–c · BR-09 a–c · BR-11 a–e · BR-12 a–h · BR-13 · BR-14 ผ่าน E-01 – E-06
  - P-01 – P-07
  - 401 ของทุกเส้นที่ต้องเข้าสู่ระบบ และ 403 ของลูกค้าทุกเส้นของสำนักงาน
  - อัปโหลด 2 ชุดพร้อมกัน (ค้าง 250 + 100 + 100) ได้ `201` กับ `429` อย่างละชุด และค้างเหลือ 350
- `BUG_MODE=1`: ผลของกรณีขอบเปลี่ยนตามโมดูลกฎ แปลว่า API ใช้กฎจาก rules.ts จริง และ `/api/health` ไม่เปิดเผยโหมดนี้

## 6. ข้อควรรู้และจุดที่ต้องประสานกับบล็อกอื่น

1. **`web/package.json` ยังไม่มี** (ผลของ B01 มีแค่ `docker-compose.yml`) · B14 ต้องเพิ่ม `next` `react` `react-dom` `pg` `@types/pg` `typescript` และ script `dispatcher`
   Next.js 15 ใช้กับ TypeScript 7 ไม่ได้ ให้ใช้ Next 16.2.11 ขึ้นไป หรือ TypeScript 6
2. **TD-BR13-b**: `reset_test_data` ตั้งเวลารับไว้ที่ `reset_at − 120 นาที` พอดี เมื่อเวลาผ่านไปแม้ 1 มิลลิวินาที ใบนี้จะค้างเกิน 120 นาทีตามกฎ BR-13 แล้ว รายการค้างจริงจึงมี 2 ใบ (b และ c) ไม่ใช่ 1 ใบตามที่ TEST-DATA คาด (ดูบันทึกของ B03 บนกระดาน)
3. **BR-12 กับ `workers_alive`**: DESIGN 6.2 ให้ใช้ Worker 1 ตัวเมื่อค่าเก่ากว่า 30 วินาที ถ้ารันด้วย `AI_MODE=mock` จะไม่มีใครอัปเดตค่านี้ การทดสอบ TD-BR12 ที่ `workersAlive=2` จึงต้องอัปโหลดภายใน 30 วินาทีหลังรีเซ็ต
4. ไฟล์ตั้งต้น S-01…S-08 และใบจาก `pendingNormal` ไม่มีรูปจริงใน `UPLOAD_DIR` W13 จึงตอบ `404 image_missing`
5. W10 ยอมตั้งด่วนให้ชุดที่อ่านจบแล้ว (DESIGN ไม่ได้ห้าม และใน `AI_MODE=mock` ใบอาจถูกอ่านเสร็จก่อนกดปุ่ม) การตั้งด่วนซ้ำกับชุดที่ด่วนอยู่แล้วตอบ `200` และไม่นับโควตาเพิ่ม
