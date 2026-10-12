# API-INVENTORY · PawPantry ตอนรันจริง (มุม runtime)

> ทำเมื่อ: **2026-10-12** · เว็บ `pawpantry05` (healthy) ที่ `http://localhost:4000` · petshop/ ไม่ได้แก้
> ไฟล์ผล (อยู่ใน `out\` ซึ่ง .gitignore กันไว้ · ไฟล์ใหญ่ย่อด้วย `node rea\rea-summarize.mjs` และสคริปต์อ่าน key ใน `rea\scratch\` เท่านั้น)

| วิธี | ไฟล์ผล | evidence_id_short | ตัวเลขหลัก |
|---|---|---|---|
| HAR (`node rea\record-har.mjs`) | `out\pawpantry-main.har` (1,629,955 B) · `out\har-steps.json` | – | 8 ขั้น · รวม 3,080 ms |
| REA อ่าน HAR (`inspect-web-network-capture` + ปิดค่าลับ 2 ค่า) | `out\har.json` (1,784,518 B) | `ev_4db99f23` | 97 records · API 4 ตัว · redaction 42 จุด |
| REA ขับเบราว์เซอร์ (`capture-browser-scenario` ใน `pawpantry05_default`) | `out\scenario.json` (4,544,420 B) · `out\scenario-final.png` | `ev_956755da` | 11/11 step · 1,682 ms · events 421 · `completeness: incomplete` |

เวลาแต่ละขั้นของ HAR (`out\har-steps.json`)

| ขั้น | ms | URL หลังจบขั้น |
|---|---|---|
| 01 home | 281 | `/` |
| 02 search 'แซลมอน' | 78 | `/products?q=แซลมอน` |
| 03 open product | 449 | `/products/lickable-salmon-treat` |
| 04 add to cart (x3) | 422 | `/products/lickable-salmon-treat` |
| 05 cart + coupon PAW10 | 122 | `/cart` |
| 06 checkout → redirect login | 63 | `/login?next=/checkout` |
| 07 login (ผู้ใช้ demo) | 994 | `/checkout` |
| 08 fill shipping + place order | 155 | `/orders/PP-100001` |

ชนิดของ 97 records ใน HAR: document 2 (`/` `/cart`) · stylesheet 2 · script 21 · fetch 72 (= API 4 + RSC ของหน้า `?_rsc=` 68 · ส่วนใหญ่เป็น prefetch ของลิงก์ เช่น `/products` 22 ครั้ง)

## A · API ที่เห็นตอนรันจริง

| method | path | status | request keys | response keys | ค่าตัวอย่าง | หน้าที่เรียก (Referer) | หลักฐาน |
|---|---|---|---|---|---|---|---|
| POST | `/api/coupons/validate` | 200 | `code` `items[{slug,size,qty}]` | `ok` `code` `discount` `freeShipping` `message` | HAR: `PAW10` · ขนมแมวเลีย 4 ซอง ×3 (฿69×3 = ฿207) → `discount: 20` `freeShipping: false` `message: "ใช้คูปอง PAW10 แล้ว"` · scenario: ×1 (฿69) → `discount: 6` | `/cart` | `ev_4db99f23` · `ev_956755da` |
| POST | `/api/auth/login` | 200 | (REA ปิดทั้ง body เพราะมีค่าลับ) | (REA ปิดทั้ง body ขนาด 94 B) + `Set-Cookie: pp_session` (HttpOnly · SameSite=Lax · Path=/ · ค่าถูกปิด) | – | `/login?next=/checkout` | `ev_4db99f23` (redaction 4 จุดใน record นี้) |
| POST | `/api/orders` | 201 | `items[{slug,size,qty}]` `coupon` `shipping` `payment` `address{name,phone,address,province,postcode}` · ส่ง cookie `pp_session` | `order{id,userId,items[{slug,name,size,price,qty,lineTotal}],subtotal,discount,shipping,total,coupon,shippingMethod,payment,address,status,createdAt}` `id` | `id: PP-100001` · `subtotal 207` `discount 20` `shipping 50` → `total 237` (= 207 − 20 + 50) · `shippingMethod: standard` `payment: cod` `status: received` | `/checkout` | `ev_4db99f23` |
| GET | `/api/products` | 200 | – (ไม่มี query) | `items[…]` `total` | `total: 28` (items 28 ตัว) · ตัวแรก `lickable-salmon-treat` `sizes [{4 ซอง,69},{20 ซอง,299}]` `stock: 77` | `/checkout` (ยิงหลัง POST `/api/orders` 15 ms) | `ev_4db99f23` |

- scenario เห็น API แค่ตัวเดียว (`POST /api/coupons/validate` 200) เพราะ scenario หยุดที่หน้าตะกร้า
- scenario: localStorage key `pp-recent` `pp-cart` `pp-coupon` · sessionStorage 0 key · cookie 0 · a11y: `alert: ใช้คูปอง PAW10 แล้ว` · `ส่วนลด PAW10 "-฿6"` · `ค่าจัดส่ง ฿50` · `ยอดชำระทั้งหมด ฿113` · `ซื้อเพิ่มอีก ฿930 เพื่อส่งฟรี`
- ทุก URL ใน steps/a11y/screenshot ของ scenario เป็น `http://petshop:3000/...` (REA อยู่ใน network `pawpantry05_default` เรียกเว็บด้วยชื่อ service) · HAR เป็น `http://127.0.0.1:4000/...` = เว็บตัวเดียวกัน คนละประตู
- `completeness: incomplete` (missing `events`): มี `request-failed` 23 ครั้ง ทั้งหมดเป็น `net::ERR_ABORTED` ของ RSC prefetch (`?_rsc=`) ที่ถูกยกเลิกตอนเปลี่ยนหน้า + console error 1 ครั้ง (`/favicon.ico` 404)

## B · เติมช่องว่างจาก SYSTEM-MAP.md

ป้ายเดิมมาจาก SYSTEM-MAP.md (⚪ unknown · ❓ REA ไม่เจอ · ⚠️ เห็นบางส่วน) · 🟢 runtime = เห็นตอนระบบรันจริง · 🟡 = อนุมานจากผลรันจริง

| รายการ (ป้ายเดิม) | runtime ยืนยันได้ไหม | ป้ายใหม่ | ไฟล์หลักฐาน |
|---|---|---|---|
| key ของ localStorage (⚪ `name: null` · ⚠️) | ได้ 3 จาก 4: `pp-recent` `pp-cart` `pp-coupon` · `pp-wishlist` ยังไม่เห็นเพราะ scenario ไม่ได้กดรายการโปรด | 🟢 (3 key) · ⚠️ `pp-wishlist` | `out\scenario.json` `ev_956755da` |
| method ของ `/api/orders` (⚪) | ได้: POST 201 จาก `/checkout` | 🟢 | `out\har.json` `ev_4db99f23` |
| cookie `pp_session` (⚠️ REA จัดเป็น endpoint) | ได้: login ตอบ `Set-Cookie pp_session` HttpOnly SameSite=Lax Path=/ และ POST `/api/orders` ส่ง cookie นี้กลับ | 🟢 | `out\har.json` (redaction `transport-credential`) |
| GET `/api/health` (❓) | ได้ แต่นอกเบราว์เซอร์: `Invoke-RestMethod http://localhost:4000/api/health` → `{"ok":true}` (ไม่อยู่ใน HAR) | 🟢 (คำสั่ง ไม่ใช่ไฟล์) | ผลคำสั่งขั้นที่ 1 |
| ออเดอร์ + เลขรัน RAM (❓) | เห็นผล: order `PP-100001` `status: received` หลัง reset · ตัวที่เก็บใน RAM มองไม่เห็น | 🟢 (ผล) | `out\har.json` · `out\har-steps.json` |
| สต็อก RAM (❓) | เห็นค่า `stock: 77` ของ `lickable-salmon-treat` หลังสั่ง 3 ชิ้น · ไม่มีค่าก่อนสั่งจึงยังพิสูจน์การตัดสต็อกไม่ได้ | 🟢 (ค่า) · การตัดสต็อก ⚪ | `out\har.json` |
| ผู้ใช้ + session RAM (❓) | ทางอ้อม: login 200 → cookie → POST `/api/orders` 201 ได้ `userId: 1` | 🟢 (ทางอ้อม) | `out\har.json` |
| POST `/api/test/reset` (❓) | `record-har.mjs` เรียกด้วย node fetch ก่อนเปิดเบราว์เซอร์ จึงไม่อยู่ใน HAR · เลขออเดอร์เริ่มที่ `PP-100001` ชี้ว่า reset ทำงาน | 🟡 | `out\har.json` |
| container ที่รันอยู่ = build เดียวกับ `out\v1` ไหม (ยังไม่รู้) | ได้: ไฟล์ `/_next/static/...` ที่เว็บส่งมาใน HAR 15 ไฟล์ มีชื่อเดียวกัน (มี hash) ใน `out\v1\.next\static` ครบ 15/15 | 🟢 | `out\har.json` เทียบ `out\v1` |
| GET `/api/orders` (⚠️) | ไม่เห็น (UI ไม่เรียก) | ⚠️ คงเดิม | – |
| GET `/api/auth/me` (❓) | ไม่เห็น | ❓ | – |
| GET `/api/orders/[id]` (❓) | ไม่เห็น API · หน้า `/orders/PP-100001` โหลดผ่าน RSC (server component อ่านข้อมูลเอง) | ❓ | – |
| GET `/api/products/[slug]` (❓) | ไม่เห็น API · หน้า `/products/lickable-salmon-treat` โหลดผ่าน RSC | ❓ | – |
| GET `/api/recommendations` (❓) | ไม่เห็น (เส้นทางวันนี้ไม่เข้า `/finder` เห็นแค่ RSC prefetch ของ `/finder`) | ❓ | – |
| hash รหัส demo (❓) | มองไม่เห็นจากข้างนอก (และไม่ควรเห็น) | ❓ | – |
| state ใน React (❓) | เห็นแค่ผลบนจอ (a11y ยอดเงิน) ไม่เห็นตัว state | ❓ | – |
| node `electron-renderer` · unknown/limitations (⚪) | runtime ไม่เกี่ยว | ⚪ คงเดิม | – |

## C · API ที่มีในโค้ด (CODEBASE-MAP.md ส่วน C) แต่ไม่เห็นในการรันรอบนี้

โค้ดมี 13 แถว (12 route) · เห็นใน HAR 4 · ไม่เห็น 9

| method | path | ทำไมไม่เห็น | เก็บหลักฐานเพิ่มอย่างไร |
|---|---|---|---|
| POST | `/api/auth/logout` | เส้นทางไม่ได้กดออกจากระบบ | เพิ่มขั้น "ออกจากระบบ" ใน scenario/สคริปต์ HAR แล้วดูว่า cookie ถูกล้าง |
| GET | `/api/auth/me` | UI ไม่เรียก (CODEBASE-MAP) | ยิงเองด้วย `Invoke-RestMethod` ทั้งตอนมี/ไม่มี cookie (black box) |
| POST | `/api/auth/register` | เส้นทางใช้ผู้ใช้ demo ที่มีอยู่แล้ว | scenario สมัครสมาชิกด้วยอีเมลทดสอบใหม่ (เกิดผู้ใช้ใหม่ใน RAM → reset หลังทำ) |
| GET | `/api/health` | เรียกนอกเบราว์เซอร์ (Docker HEALTHCHECK · ขั้นที่ 1) | เห็นแล้วด้วย `Invoke-RestMethod` → `{"ok":true}` · ถ้าต้องมีไฟล์ให้บันทึกผลลง `out\` |
| GET | `/api/orders` | UI ไม่เรียก | ยิงเองพร้อม cookie หลัง login (ต้องดูแล cookie ไม่ให้หลุดลงเอกสาร) · ไม่มี cookie ต้องได้ 401 |
| GET | `/api/orders/[id]` | หน้า `/orders/[id]` อ่านข้อมูลฝั่ง server เอง ไม่ผ่าน API | ยิงเอง `/api/orders/PP-100001` ด้วยผู้ใช้เจ้าของ (200) กับผู้ใช้อื่น (404) |
| GET | `/api/products/[slug]` | หน้าสินค้าเป็น server component ไม่ fetch API | ยิงเอง slug ที่มี/ไม่มี (200/404) |
| GET | `/api/recommendations` | เส้นทางไม่เข้า `/finder` | เพิ่ม scenario เดิน `/finder` ครบ wizard แล้วดู query ที่ส่งจริง |
| POST | `/api/test/reset` | `record-har.mjs` เรียกด้วย node fetch นอกเบราว์เซอร์ | ดูโค้ดสคริปต์ (ยืนยันแล้ว) · ห้ามมีในเครื่องจริง (ไม่มี auth) → ตรวจ env `ALLOW_TEST_RESET` ของ container |

## D · 3 วิธีที่ใช้วันนี้

| วิธี | ใครคุมเบราว์เซอร์ | มีผลกับข้อมูลในระบบไหม | หลักฐานบอกอะไร | บอกอะไรไม่ได้ |
|---|---|---|---|---|
| analyze build (LAB 2 · `out\v1`) | ไม่มีเบราว์เซอร์ (อ่านไฟล์ที่ build) | ไม่มี | ไฟล์/endpoint ที่เป็นสตริงคงที่ · path ต้นทางจาก source map · ชนิด storage | method · ค่าจริง · key ที่ส่งผ่านตัวแปร · URL ที่ประกอบตอนรัน · route ที่ UI ไม่เรียก |
| HAR (`record-har.mjs` → REA อ่าน) | สคริปต์ Playwright ของเรา (เราคุม) · REA แค่อ่านไฟล์ ไม่ยิงซ้ำ | **มี**: reset ข้อมูล + login + สร้างออเดอร์ `PP-100001` + ตัดสต็อก (ตอนบันทึก ไม่ใช่ตอน REA อ่าน) | method · status · request/response จริง · ยอดเงิน · cookie (ถูกปิดค่า) · หน้าที่เรียก (Referer) · build ที่รันอยู่ | API ที่เส้นทางไม่ได้เดิน · โค้ดฝั่ง server ทำอะไรข้างใน · body ที่ถูกปิด (login) |
| scenario (`capture-browser-scenario`) | REA คุม Chromium เอง (ใน container · network `pawpantry05_default`) | มีได้ (driven) · รอบนี้ไม่สร้างข้อมูลฝั่ง server (หยุดที่ตะกร้า) เปลี่ยนแค่ localStorage ของเบราว์เซอร์ REA | step ผ่าน/ไม่ผ่าน · URL ทุก step · key ใน storage · a11y/ข้อความบนจอ · ภาพสุดท้าย · API ที่ยิง | ค่าใน storage (เก็บเป็น hash) · ทำไม step เป็นแบบนั้น · ทางอื่นที่ไม่ได้เขียนใน scenario |

## ไฟล์ HAR กับ git

`.gitignore` ของโฟลเดอร์บทมี `out/` (บรรทัด 1) และ `*.har` (บรรทัด 2) แล้ว · `git check-ignore` ยืนยันว่า `out/pawpantry-main.har` และ `out/har.json` ถูกกัน

- ไฟล์ `.har` ต้นฉบับเก็บทุกอย่างตรงตัว: รหัสผ่าน demo ใน body ของ login (ค้นเจอ 1 จุด) · cookie session `pp_session` · ชื่อ/เบอร์/ที่อยู่ในออเดอร์ ใครได้ไฟล์ไปก็ login แทนหรือเห็นข้อมูลส่วนตัวได้
- REA ปิดค่าเหล่านี้ใน `out\har.json` (42 จุด) แต่ไม่ได้แก้ `.har` ต้นฉบับ → ห้าม commit/แนบ/ส่ง `.har` ส่งต่อได้แค่ผลที่ปิดค่าแล้วหรือเอกสารสรุปนี้

## สรุป

| ส่วน | จำนวนแถว | ยืนยันด้วย runtime ได้ | ยังไม่รู้ |
|---|---|---|---|
| A · API ที่เห็นตอนรัน | 4 | 4 | 1 (key ใน body ของ login ถูกปิด) |
| B · เติมช่องว่าง SYSTEM-MAP | 17 | 8 🟢 + 1 🟡 | 8 |
| C · API ในโค้ดที่ไม่เห็น | 9 | 1 (`/api/health` นอกเบราว์เซอร์) · 1 🟡 (`/api/test/reset`) | 7 |
| D · 3 วิธี | 3 | 2 (HAR · scenario) | – |

## ยังไม่รู้

- body ของ login ใช้ key อะไร (REA ปิดทั้ง body เพราะมีค่าลับ) — ต้องอ่านโค้ด `LoginForm` หรือบันทึก HAR ด้วยบัญชีทดสอบที่ไม่ลับ
- การตัดสต็อกตอนสั่งซื้อ (ต้องมีค่าก่อน/หลังในรอบเดียวกัน)
- ส่วนลด PAW10 ปัดเศษแบบไหน: ฿207 → 20 และ ฿69 → 6 ชี้ว่าปัดลง (ถ้า PAW10 = 10%) 🟡
- API 7 ตัวในส่วน C ที่ยังไม่ได้ยิง
