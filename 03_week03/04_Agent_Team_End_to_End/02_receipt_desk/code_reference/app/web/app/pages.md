# หน้าเว็บตามบทบาท ReceiptDesk (บล็อก B11)

หน้าเว็บทุกหน้าใน DESIGN 9.1 **ยกเว้นหน้าตรวจแก้ใบ `/receipts/[id]`** (ของ B12) · Next.js App Router (`page.tsx`) · ข้อมูลทุกอย่างมาจาก API 23 เส้นของ B04 (`web/app/api/README.md`)
หน้าไม่ตัดสิน Business Rule เอง กฎ BR-01 – BR-14 ตัดสินที่ server (`web/lib/rules.ts`) แล้วหน้าแสดงผลตามคำตอบเท่านั้น `BUG_MODE` จึงมีผลกับหน้าเว็บแบบเดียวกับ API และไม่มีข้อความบนหน้าที่บอกโหมดนี้ (DESIGN 9.6)

## 1. หน้า → บทบาท (DESIGN 9.1)

✓ = เปิดได้ · ✗ = เห็นกล่อง `page-forbidden` ("บัญชี… ไม่มีสิทธิ์เปิดหน้า…") และไม่โหลดข้อมูลของหน้านั้น · ผู้ที่ไม่ได้เข้าสู่ระบบเปิดหน้าใดก็ได้ `307` ไป `/login?next=<path>` (ยกเว้น `/login`)

| หน้า | Path | ไฟล์ | พนักงาน `staff` | หัวหน้า `lead` | เจ้าของ `owner` | ลูกค้า `client` | API ที่เรียก |
|---|---|---|---|---|---|---|---|
| เข้าสู่ระบบ | `/login` | `login/page.tsx` · `LoginForm.tsx` | ✓ | ✓ | ✓ | ✓ | W3 |
| อัปโหลดชุด | `/upload` | `upload/page.tsx` · `UploadForm.tsx` | ✓ | ✓ + ช่องงานด่วน | ✗ | ✗ | W6 · W7 · W23 |
| รายการชุด + ยอดตรวจนับ (สถานะงาน) | `/batches` | `batches/page.tsx` · `BatchesView.tsx` | ✓ | ✓ | ✓ | ✗ | W8 · W20 |
| ชุด 1 ชุด (สถานะทีละใบ · งานด่วน) | `/batches/[id]` | `batches/[id]/page.tsx` · `BatchView.tsx` | ✓ | ✓ + ปุ่มงานด่วน | ✓ | ✗ | W9 · W10 |
| รายการใบ (กรองสถานะ · ธง · ลูกค้า) | `/receipts` | `receipts/page.tsx` · `ReceiptsView.tsx` | ✓ | ✓ | ✓ | ✗ | W6 · W11 |
| ตรวจและยืนยันใบ | `/receipts/[id]` | **B12** (ไม่อยู่ในบล็อกนี้) | ✓ | ✓ | ดูอย่างเดียว | ✗ | — |
| อ่านไม่ได้ ให้คนพิมพ์เอง | `/unreadable` | `unreadable/page.tsx` · `UnreadableView.tsx` | ✓ | ✓ | ✓ | ✗ | W11 `?status=unreadable` |
| ค้างเกินกำหนด | `/overdue` | `overdue/page.tsx` · `OverdueView.tsx` | ✗ | ✓ | ✓ | ✗ | W11 `?overdue=true` |
| ไฟล์สรุปรายเดือน CSV | `/reports` | `reports/page.tsx` · `ReportsView.tsx` | ✓ | ✓ | ✓ | ✗ | W6 · W18 |
| เวลาตรวจ · GPU 1 เทียบ 2 ใบ | `/insights` | `insights/page.tsx` · `InsightsView.tsx` | ✗ | ✓ (เวลาตรวจเท่านั้น) | ✓ (เวลาตรวจ + GPU) | ✗ | W21 · W22 (เจ้าของ) |
| หน้าลูกค้า: ส่งใบ · ใบของร้าน · สรุปแยกหมวด | `/portal` | `portal/page.tsx` · `PortalView.tsx` | ✗ | ✗ | ✗ | ✓ | W7 · W11 · W19 |
| หน้าแรก | `/` | `page.tsx` | → `/upload` | → `/upload` | → `/batches` | → `/portal` | — |

- หลังเข้าสู่ระบบไปที่ `next` ถ้าเป็น path ภายในเว็บที่บทบาทนั้นเปิดได้ ไม่เช่นนั้นไปหน้าแรกของบทบาท (กัน open redirect)
- เมนูแสดงเฉพาะลิงก์ของหน้าที่บทบาทนั้นเปิดได้ (ตารางเดียวกัน `_ui/roles.ts` `PAGE_ROLES`)
- ตารางนี้กันแค่หน้าเว็บ สิทธิ์จริงตรวจซ้ำที่ API ทุกเส้น (B04) เช่น พนักงานยิง W10 ตรงได้ `403`

## 2. โครงไฟล์

```
web/app/
├── layout.tsx            # root layout: อ่าน session → <Nav/> ทุกหน้า (ไม่มี session = ไม่มีเมนู) · lang="th"
├── page.tsx              # `/` → หน้าแรกของบทบาท
├── globals.css
├── pages.md              # ไฟล์นี้
├── _ui/                  # ไม่ใช่ route (โฟลเดอร์ขึ้นต้นด้วย _)
│   ├── roles.ts          # Role · PAGE_ROLES (ตาราง 9.1) · canOpen() · homeFor() · ROLE_LABEL  ← ใช้ได้ทั้ง server/client
│   ├── session.ts        # server: getPageUser() · requirePageUser(roles, path) ใช้ currentUser() ของ B04
│   ├── Nav.tsx · LogoutButton.tsx · OverdueBadge.tsx · Forbidden.tsx
│   ├── api.ts            # client fetch: 401 → /login?next= · คืน {ok,status,data|error}
│   ├── format.ts         # money() · dateTime() (เวลาไทย) · currentBangkokMonth() · STATUS_OPTIONS
│   ├── ReceiptBits.tsx   # StatusCell (receipt-status-{id}) · FlagCell (receipt-flag-{id})
│   ├── QueueFull.tsx     # ข้อความคิวเต็ม FR-22
│   └── useClients.ts     # W6
├── login/ upload/ batches/ batches/[id]/ receipts/ unreadable/ overdue/ reports/ insights/ portal/
└── api/                  # B04 (ไม่แก้)
```

แต่ละหน้า: `page.tsx` เป็น server component ที่เรียก `requirePageUser(PAGE_ROLES[...])` แล้วส่งต่อให้ client component (`*View.tsx`/`*Form.tsx`) ที่ดึงข้อมูลจาก API ด้วย cookie `rd_session` ของ browser

**สำหรับ B12** (หน้า `/receipts/[id]`): ใช้ตัวกันหน้าเดียวกันได้
`const { user, allowed } = await requirePageUser(['staff','lead','owner'], '/receipts/' + id)` จาก `../../_ui/session` · ถ้า `!allowed` ให้แสดง `<Forbidden user={user} page="ตรวจใบ" />` · ใช้ `api()` จาก `_ui/api.ts` · เมนูมาจาก root layout แล้ว
ทุกลิงก์ "เปิดใบ" ในบล็อกนี้ชี้ไป `/receipts/{id}` ตาม DESIGN 9.1 (แผนระบุผลของ B12 เป็น `web/app/review/page.tsx` ถ้า B12 ใช้ path นั้น ต้องย้ายเป็น `web/app/receipts/[id]/page.tsx` หรือเพิ่ม redirect)

## 3. `data-testid` (DESIGN 9.5)

ใช้ชื่อตาม 9.5 ทุกตัว ไม่เปลี่ยนชื่อ · `{id}` = UUID ของแถว · `{ลำดับ}` ของ `upload-file-error-` = ลำดับไฟล์ในชุด **เริ่มที่ 0** (`index` จาก rules.ts)

| หน้า | `data-testid` | หมายเหตุ |
|---|---|---|
| ทุกหน้า (มี session) | `nav-upload` · `nav-batches` · `nav-receipts` · `nav-unreadable` · `nav-overdue` · `nav-reports` · `nav-insights` · `nav-portal` · `nav-user-name` · `nav-user-role` · `logout-button` | ลิงก์ `nav-*` มีเฉพาะหน้าที่บทบาทเปิดได้ (ตาราง §1) · `nav-user-role` ข้อความไทย + `data-role` = รหัสบทบาท |
| `/login` | `login-email-input` · `login-password-input` · `login-submit-button` · `login-error` | `login-error` มีเมื่อผิดเท่านั้น ("อีเมลหรือรหัสผ่านไม่ถูกต้อง") |
| `/upload` | `upload-client-select` · `upload-file-input` · `upload-urgent-checkbox` · `upload-submit-button` · `upload-accepted-count` · `upload-error` · `upload-file-error-{ลำดับ}` · `upload-full-message` · `upload-retry-minutes` · `upload-queue-pending` | `upload-urgent-checkbox` มีเฉพาะหัวหน้า · `upload-accepted-count` = จำนวนที่รับ (ชุดถูกปฏิเสธแสดง `0` · FR-23) · `upload-full-message` = ประโยค "ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก N นาที" เท่านั้น · `upload-retry-minutes` = N (ตัวเลขล้วน) · `upload-queue-pending` = ใบงานปกติที่ค้าง (W23 `normal.pending`) |
| `/batches` | `batches-table` · `batch-row-{id}` · `batch-open-link-{id}` · `reconcile-accepted` · `reconcile-sum` · `reconcile-diff` | ยอดตรวจนับทั้งสำนักงานจาก W20 · ตารางมีจำนวนต่อสถานะและผลต่างรายชุด |
| `/batches/[id]` | `batch-priority` · `batch-count-accepted` · `batch-count-queued` · `batch-count-processing` · `batch-count-review` · `batch-count-confirmed` · `batch-count-unreadable` · `batch-urgent-button` · `batch-urgent-error` · `receipt-row-{id}` · `receipt-status-{id}` · `receipt-flag-{id}` · `receipt-open-link-{id}` | `batch-priority` ข้อความ "ปกติ"/"ด่วน" + `data-priority` = `normal`/`urgent` · `batch-urgent-button` มีเฉพาะหัวหน้า (FR-19) ปิดเมื่อชุดเป็นด่วนแล้ว · `batch-urgent-error` = `message` ของ BR-08/BR-09 · รีเฟรชทุก 5 วินาทีขณะยังมีใบรออ่าน/กำลังอ่าน |
| `/receipts` | `filter-status-select` · `filter-flagged-checkbox` · `filter-client-select` · `filter-apply-button` · `receipts-table` · `receipts-count` · `receipt-row-{id}` · `receipt-status-{id}` · `receipt-flag-{id}` | ตัวกรองมีผลเมื่อกด `filter-apply-button` และเก็บใน URL (`?status=&flagged=true&clientId=`) · ค่า `filter-status-select`: `""` (ทุกสถานะ) · `queued` · `processing` · `review` · `confirmed` · `unreadable` · มี `receipt-open-link-{id}` เพิ่มเหมือนหน้าชุด |
| `/unreadable` | `unreadable-table` · `unreadable-count` · `unreadable-row-{id}` · `unreadable-reason-{id}` · `unreadable-open-link-{id}` | ลิงก์ไป `/receipts/{id}` (พิมพ์เอง · B12) |
| `/overdue` | `overdue-table` · `overdue-count` · `overdue-row-{id}` · `overdue-minutes-{id}` | เรียงจากรอนานสุด · `overdue-minutes-{id}` = นาทีที่รอ (ตัวเลขล้วน) |
| `/reports` | `report-client-select` · `report-month-input` · `report-preview-button` · `report-total` · `report-receipt-count` · `report-export-button` | `report-month-input` เป็น `<input type="month">` ค่า `YYYY-MM` (ตั้งเดือนปัจจุบันตามเวลาไทย) · `report-total`/`report-receipt-count` มีหลังกดดูตัวอย่าง · `report-export-button` เป็น `<a download>` ไป W18 (CSV) |
| `/insights` | `review-time-average` · `review-time-table` · `gpu-table` · `gpu-speedup` · `gpu-efficiency` · `gpu-cost-per-100` · `gpu-verdict` | `gpu-*` มีเฉพาะเจ้าของ · `review-time-average` = วินาทีต่อใบ · `gpu-speedup` = เท่า · `gpu-efficiency` = ร้อยละ (1 ตำแหน่ง) · `gpu-cost-per-100` = บาทต่อ 100 ใบของ 2 GPU · `gpu-verdict` มี `data-worth` = `true`/`false` |
| `/portal` | `portal-file-input` · `portal-upload-button` · `portal-accepted-count` · `portal-upload-error` · `portal-receipt-row-{id}` · `portal-receipt-status-{id}` · `portal-receipt-total-{id}` · `portal-month-input` · `portal-summary-total` · `portal-category-total-{id}` | `portal-receipt-status-{id}` = "รับแล้ว รอสำนักงานตรวจ" หรือ "ยืนยันแล้ว" (`data-status` = `received`/`confirmed`) · `portal-receipt-total-{id}` **มีเฉพาะใบที่ยืนยันแล้ว** (FR-25) · `portal-category-total-{id}` ใช้ id ของหมวด แสดงครบ 4 หมวดแม้เป็น `0.00` · สรุปโหลดใหม่ทันทีที่เปลี่ยนเดือน · คิวเต็มแสดงใน `portal-upload-error` |

รูปแบบค่าในองค์ประกอบที่มี testid:
- เงิน = ค่าจาก server ทศนิยม 2 ตำแหน่ง ไม่มีจุลภาค ไม่มีหน่วย เช่น `1340.00` (คำว่า "บาท" อยู่นอกองค์ประกอบ)
- จำนวน = ตัวเลขล้วน
- `receipt-status-{id}` = ข้อความไทย (รออ่าน · กำลังอ่าน · รอตรวจ · ยืนยันแล้ว · อ่านไม่ได้) + `data-status` = รหัสสถานะ
- `receipt-flag-{id}` มีเฉพาะใบติดธง ข้อความ = "ระบบไม่แน่ใจ: <เหตุผล>" + `data-flags` = `low-confidence` และ/หรือ `mismatch` (FR-09)

testid ที่เพิ่มนอก 9.5 (ไม่ชนกับของเดิม): `page-forbidden` (บทบาทเปิดหน้าไม่ได้) · `receipt-open-link-{id}` บน `/receipts` · `review-time-row-{batchId}` · `gpu-row-{1|2}`

## 4. พฤติกรรมตาม Requirement

| เรื่อง | ทำอย่างไร |
|---|---|
| FR-02 / DESIGN 8 | ทุกหน้ายกเว้น `/login` ตรวจ session ที่ server ก่อน render · ไม่มี → `/login?next=` · client ได้ `401` ระหว่างใช้งาน → `/login?next=` |
| FR-04 · FR-05 · FR-23 | แสดง `accepted` จาก W7 · ไฟล์ไม่ผ่านแสดงทุกไฟล์พร้อมชื่อและเหตุผล (`upload-file-error-{ลำดับ}`) และ `upload-accepted-count` = 0 |
| FR-06 | หลังรับแล้วบอกว่าออกจากหน้าได้ทันที และมีลิงก์ไปสถานะชุด |
| FR-07 · FR-08 | `/batches/[id]` จำนวนต่อสถานะ + รีเฟรชเอง · `/batches` ยอดตรวจนับทั้งสำนักงาน (รับเข้า · รวมทุกสถานะ · ผลต่าง) และรายชุด |
| FR-09 · FR-10 | ธงพร้อมเหตุผลในตาราง · กรอง `flagged=true` |
| FR-16 | `/unreadable` แยกรายการพร้อมเหตุผล |
| FR-18 · FR-19 | ช่องงานด่วนตอนอัปโหลดและปุ่มบนหน้าชุด มีเฉพาะหัวหน้า (API ตรวจซ้ำ) |
| FR-21 | ตัวเลขเตือนข้างเมนู "ค้างเกินกำหนด" (W23 `overdue` ทุก 60 วินาที) + หน้า `/overdue` |
| FR-22 | `429 queue_full` → "ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก N นาที" โดย N = `retryAfterMinutes` จาก server |
| FR-24 · FR-25 · FR-27 | หน้าลูกค้าใช้ W11/W19 ที่กรองร้านที่ server · ใบยังไม่ยืนยันแสดงแค่ชื่อไฟล์ เวลารับ สถานะ |
| FR-26 | ลูกค้าอัปโหลดโดยไม่ส่ง `clientId` (server ผูกร้านเอง) |
| FR-28 · BR-14 | `/reports` ดูตัวอย่าง (W18 `format=json`) และดาวน์โหลด CSV จาก W18 ตรง ยอดในหน้าตรงกับไฟล์ |
| FR-29 | `/portal` เลือกเดือน → ยอดแยกหมวด (W19) |
| FR-30 · FR-31 | `/insights` เวลาตรวจเฉลี่ย (เป้า < 120 วินาที) · GPU 1 vs 2 (Speedup · Efficiency · บาท/100 ใบ · คุ้มเมื่อ ≥ 1.6) |

## 5. ผลการตรวจ (2026-11-19)

ตรวจในโฟลเดอร์ชั่วคราว `/tmp/b11chk` (สำเนา `web/app` + `web/lib` + `web/public`) ด้วย Next.js 16.4.6 + React 19 + TypeScript 5 (`strict`) + PostgreSQL 16 (docker) ที่โหลด `web/db/schema.sql` แล้วเรียก `reset_test_data`

- `tsc --noEmit` ไม่มี error · `next build` ผ่าน · ตาราง route มีหน้า `/` `/login` `/upload` `/batches` `/batches/[id]` `/receipts` `/unreadable` `/overdue` `/reports` `/insights` `/portal` + API 21 path ของ B04
- ไม่มี session: `GET /upload` → `307 /login?next=%2Fupload`
- Playwright เข้าสู่ระบบจริงด้วย U-01 (staff) · U-03 (lead) · U-04 (owner) · U-05 (client) แล้วเปิดทั้ง 8 หน้า ได้ผลตรงตาราง §1 ทุกช่อง (เมนูก็ตรง) และ:
  - รหัสผ่านผิด → `login-error` "อีเมลหรือรหัสผ่านไม่ถูกต้อง"
  - อัปโหลด `a.jpg` + `b.gif` → `upload-error` + `upload-file-error-1` ("ไฟล์ที่ 2 “b.gif” …") + `upload-accepted-count` = 0
  - หัวหน้าอัปโหลด 2 ไฟล์แบบด่วน → `upload-accepted-count` = 2 · หน้าชุด `batch-priority` = ด่วน · `batch-count-accepted` = 2
  - หัวหน้ากด `batch-urgent-button` กับชุดปกติ → `data-priority` เปลี่ยนเป็น `urgent`
  - พนักงานไม่มี `upload-urgent-checkbox` และไม่มี `batch-urgent-button`
  - รีเซ็ต `pendingNormal: 400` → `upload-queue-pending` = 400 · ส่ง 1 ไฟล์ → `upload-full-message` "ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก 1 นาที" · `upload-retry-minutes` = 1 · ลูกค้าได้ข้อความเดียวกันใน `portal-upload-error` และ `portal-accepted-count` = 0
  - `/reports` CL-01 เดือน 2026-11 → `report-total` = `1340.00` · `report-receipt-count` = 4 (ตรง E-02) · `report-export-button` ดาวน์โหลด `receiptdesk-CL-01-2026-11.csv`
  - `/portal` (U-05) 2026-11 → `portal-summary-total` = `1340.00` · หมวด `1200.50` · `40.00` · `99.50` · `0.00` (ผลรวม = ยอดรวม) · `portal-receipt-total-*` มีเฉพาะใบที่ยืนยันแล้ว
  - `/overdue` (รีเซ็ต `overdue: true`) แสดง 3 ใบ นาที 122 · 121 · 120 เพราะทดสอบหลังรีเซ็ตไปไม่กี่นาที ตรงกับข้อควรระวัง TD-BR13-b ของ B03/B04 ที่ใบ 119 นาทีจะเกินกำหนดตามเวลาที่ผ่านไป
  - ตัวกรอง `flagged` เปลี่ยน URL เป็น `?flagged=true` และ `receipts-count` เปลี่ยนตาม
- ข้อผิดพลาดใน console ของ browser มีแค่ 404 ของ `favicon.ico` · 401 ตอนตั้งใจใส่รหัสผ่านผิด · prefetch ของ `/receipts/{id}` (หน้าของ B12 ที่ยังไม่มี)

## 6. สิ่งที่บล็อกอื่นต้องรู้

1. **B12** หน้าตรวจต้องอยู่ที่ `web/app/receipts/[id]/page.tsx` เพราะลิงก์ "เปิดใบ" ทุกจุดชี้ไป path นี้ตาม DESIGN 9.1 · ใช้ `requirePageUser` / `Forbidden` / `api()` จาก `web/app/_ui/` ได้ · root layout มีเมนูให้แล้ว อย่าสร้าง `layout.tsx` ซ้ำที่ root
2. **B14** `web/package.json` ต้องมี `next` (16.x) `react` `react-dom` (19) `pg` และ dev `typescript` `@types/react` `@types/react-dom` `@types/node` `@types/pg` · `next.config` ใส่ `serverExternalPackages: ['pg']` · หน้าไม่ใช้แพ็กเกจเพิ่ม (ไม่มี `server-only`)
3. ทุกหน้าเป็น `dynamic = 'force-dynamic'` (อ่าน cookie) และไม่มีหน้า static ที่ต้องต่อฐานข้อมูลตอน build
