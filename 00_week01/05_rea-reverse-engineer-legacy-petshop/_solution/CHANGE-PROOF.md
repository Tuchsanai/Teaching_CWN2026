# CHANGE-PROOF · ของที่จะส่งมอบเปลี่ยนเฉพาะที่ตั้งใจ (BUG-01 + CR-01)

> ทำเมื่อ 2026-10-12 · เทียบ `out\v1` (สำเนาโค้ดตอนรับช่วง + build เดิม) กับ `petshop\` (หลังแก้ BUG-01 และทำ CR-01) · ไม่ได้แก้โค้ด
> ไฟล์ผล REA ใหญ่ทั้งหมดอ่านผ่าน `node rea\rea-summarize.mjs` เท่านั้น · คำสั่งทุกตัวรันด้วย PowerShell จากโฟลเดอร์บท

## 0 · ไฟล์ผลและ evidence_id_short

| ผล | คำสั่ง | exit | เวลา | ขนาด (B) | evidence_id_short |
|---|---|---|---|---|---|
| `out\v1-server.json` (ของเดิม · ไม่ได้รันใหม่) | `REA analyze-javascript-application /work/out/v1/.next/server` | – | – | 54,029,530 | `ev_ac8d9821` |
| `out\v2` (build ใหม่) | `robocopy petshop out\v2 /E /XD node_modules .next …` | 1 (= คัดลอกสำเร็จ) | 0.1 วิ | 120 ไฟล์ | – |
| `out\v2\.next` | `docker run … node:24-alpine sh -c "npm ci … && npm run build"` | 0 | 155.2 วิ | `✓ Compiled successfully` · added 348 packages | – |
| `out\v2-server.json` | `REA -Out out\v2-server.json analyze-javascript-application /work/out/v2/.next/server --json` | 0 | 21.8 วิ | 54,072,942 | `ev_54c61f33` (files 445 · edges 1,859 · coverage partial/partial · limitations 213) |
| `out\v1-src.json` | `REA -Out out\v1-src.json import-reference-source /work/out/v1 --json` | 0 | 2.7 วิ | 58,226 | ไม่มี evidence_id (schema `HistoricalSourceGraph`) · root `ae1f32c6afb8` · 154 entries · `inventory_state: partial` |
| `out\v2-src.json` | `REA -Out out\v2-src.json import-reference-source /work/out/v2 --json` | 0 | 2.7 วิ | 58,226 | ไม่มี evidence_id · root `087ee24a43b9` · 154 entries · `partial` |
| `out\s2b-v1src-v1build.json` | `compare-source-to-bundle` (v1-src × v1-server) | 0 | 9.0 วิ | 262,270 | `ev_23cd4cec` |
| `out\s2b-v1src-v2build.json` | (v1-src × v2-server) | 0 | 9.0 วิ | 264,070 | `ev_b034f50f` |
| `out\s2b-v2src-v1build.json` | (v2-src × v1-server) | 0 | 9.2 วิ | 257,300 | `ev_ba4bd111` |
| `out\s2b-v2src-v2build.json` | (v2-src × v2-server) | 0 | 9.1 วิ | 269,040 | `ev_f47a7dd1` |

ทุกคู่สร้าง input ด้วย `node rea\rea-input.mjs s2b out\<src>.json out\<v>-server.json out\s2b.in.json` (exit 0 · ~0.4 วิ · 54.1 MB)

## 1 · ชั้น source: SHA-256 `out\v1` เทียบ `petshop` (ไม่รวม `node_modules` `.next`)

`Get-ChildItem -LiteralPath … -Recurse -File -Force` + `Get-FileHash -LiteralPath … -Algorithm SHA256` · out\v1 = 121 ไฟล์ · petshop = 120 ไฟล์ (= `git ls-files petshop` 120) · รวม 121 ชื่อ

| สถานะ | จำนวน |
|---|---|
| เหมือน | 114 |
| ต่าง | 6 |
| มีแค่ฝั่ง out\v1 | 1 |
| มีแค่ฝั่ง petshop | 0 |

| ไฟล์ | สถานะ | SHA-256 (12 ตัวแรก) out\v1 → petshop | ตั้งใจแก้? |
|---|---|---|---|
| `app/orders/[id]/page.tsx` | ต่าง | `8C832CD3702B` → `8A8EDE89A3DD` | ✅ CR-01 |
| `components/CheckoutForm.tsx` | ต่าง | `C9979CCE19CD` → `A5397DBE3EB2` | ✅ CR-01 |
| `components/OrderSummary.tsx` | ต่าง | `9F75918840BE` → `A8619CC2986C` | ✅ CR-01 |
| `lib/orders.ts` | ต่าง | `7DC5D36B3055` → `FCD5BEE3B883` | ✅ BUG-01 + CR-01 |
| `lib/pricing.ts` | ต่าง | `532235A18E6A` → `D9D2156456B5` | ✅ CR-01 |
| `lib/store.ts` | ต่าง | `7947235EFF28` → `673D7E8BBDB4` | ✅ CR-01 |
| `next-env.d.ts` | มีแค่ out\v1 | `1862AC4BBBC5` → – | ❌ ไม่ได้ตั้งใจ → อธิบายด้านล่าง |

ไฟล์ที่เหมือน 114 ไฟล์: ราก 11 (`Dockerfile` `docker-compose.yml` `package.json` `package-lock.json` `tsconfig.json` `next.config.ts` `eslint.config.mjs` `.gitignore` `.dockerignore` `README.md` `HANDOVER-NOTES.md`) · `app/` 25 (รวม route API 12 ไฟล์) · `components/` 16 · `lib/` 6 (`auth` `catalog` `finder` `fx` `products` `validation`) · `public/images/` 56 (รายการเต็ม `..\tools\lab9\hash-table.csv` ของ runner)

**`next-env.d.ts` ไม่ใช่การแก้ แต่เป็นไฟล์ที่ `next build` สร้างเอง:**
- `petshop/.gitignore` มีบรรทัด `next-env.d.ts` และ `git ls-files petshop` ไม่มีไฟล์นี้ → ไม่เคยอยู่ใน source ที่ส่งมอบ
- `out\v1\next-env.d.ts` เวลาแก้ไข 09:36:33 = ช่วงเดียวกับ `out\v1\node_modules` (09:36) และ `.next` (09:37) ตอน build v1 · ไฟล์อื่นใน out\v1 ส่วนใหญ่ 07:19 / 08:55–08:59
- หลัง build v2 (ข้อ 2) `out\v2\next-env.d.ts` เกิดขึ้นเอง SHA-256 `1862AC4BBBC5…` **เท่ากับของ out\v1 ทุกไบต์** → ยืนยันว่าเป็นผลของ build ไม่ใช่การแก้
- `tsconfig.json` เหมือนกันทั้ง 3 ที่ (`06D0A398B847` · out\v1 = petshop = out\v2 หลัง build) → build ไม่ได้เขียนทับ

👀 `Get-FileHash $_.FullName` (ไม่ใส่ `-LiteralPath`) คืนค่าว่างสำหรับ path ที่มี `[ ]` เช่น `app/orders/[id]/page.tsx` เพราะ PowerShell ตีความ `[id]` เป็น wildcard → รอบแรกตารางนี้ได้ "ต่าง 5" และนับ `app/orders/[id]/page.tsx` เป็น "เหมือน" (ค่าว่าง = ค่าว่าง) · แก้ด้วย `-LiteralPath` แล้วได้ 6 (ตรวจซ้ำ: ไม่มี hash ว่างเลย · `git diff --stat -- petshop` ก็บอก 6 ไฟล์ `61 insertions(+), 15 deletions(-)`)

## 2 · build เวอร์ชันใหม่ (`out\v2`)

- `robocopy petshop out\v2 /E /XD node_modules .next /NFL /NDL /NJH /NJS` → exit **1** (อยู่ในช่วง 0–7 = สำเร็จ · 1 = มีไฟล์ถูกคัดลอก) · out\v2 = 120 ไฟล์
- `docker run --rm -v "${PWD}\out\v2:/app" -w /app -e NEXT_TELEMETRY_DISABLED=1 node:24-alpine sh -c "npm ci --no-audit --no-fund && npm run build"` → exit **0** · **155.2 วิ** · `added 348 packages in 2m` · `✓ Compiled successfully in 3.5s` · `Finished TypeScript in 8.1s`
- `REA analyze-javascript-application /work/out/v2/.next/server` → `ev_54c61f33` · v1 (`ev_ac8d9821`) files 445 · edges 1,868 · limitations 202 / v2 files 445 · edges 1,859 · limitations 213

## 3 · ชั้น bundle: REA เทียบ source กับของที่ build 4 ทิศ

### ตัวนับ 7 คลาสของทุกคู่ (`node rea\rea-summarize.mjs out\s2b-<คู่>.json --md`)

| คู่ (source → build) | evidence | unchanged | modified | removed | split | merged | duplicated | unknown | รวม |
|---|---|---|---|---|---|---|---|---|---|
| v1src → v1build | `ev_23cd4cec` | 44 | 0 | 0 | 0 | 0 | 8 | 3 | 55 |
| v1src → v2build | `ev_b034f50f` | 41 | 0 | 0 | 0 | 0 | 5 | 9 | 55 |
| v2src → v1build | `ev_ba4bd111` | 41 | 0 | 0 | 0 | 0 | 5 | 9 | 55 |
| v2src → v2build | `ev_f47a7dd1` | 44 | 0 | 0 | 0 | 0 | 8 | 3 | 55 |

### ตาราง 4 ทิศ (`node rea\rea-summarize.mjs --s2b-table …` · แสดงเฉพาะไฟล์ที่สถานะไม่เท่ากันระหว่างคู่)

| source file | v1src → v1build | v1src → v2build | v2src → v1build | v2src → v2build |
|---|---|---|---|---|
| `app/orders/[id]/page.tsx` | unchanged | unknown | unknown | unchanged |
| `components/CheckoutForm.tsx` | unchanged | unknown | unknown | unchanged |
| `components/OrderSummary.tsx` | unchanged | unknown | unknown | unchanged |
| `lib/orders.ts` | duplicated | unknown | unknown | duplicated |
| `lib/pricing.ts` | duplicated | unknown | unknown | duplicated |
| `lib/store.ts` | duplicated | unknown | unknown | duplicated |

อ่านอย่างไร
- **คู่เวอร์ชันเดียวกัน** (v1→v1 · v2→v2) ได้ตัวนับเท่ากันทุกคลาส (44/0/0/0/0/8/3) → source แต่ละรุ่นตรงกับ build ของรุ่นตัวเอง
- **คู่ข้ามเวอร์ชัน** ได้ 41/0/0/0/0/5/9 · ส่วนต่าง = 6 ไฟล์พอดี (unchanged −3 · duplicated −3 · unknown +6) และเป็น 6 ไฟล์เดียวกับที่ hash ต่างในข้อ 1
- ไฟล์ที่แก้ขึ้นเป็น **unknown** ในคู่ข้ามเวอร์ชัน = REA หา digest ของ source ไฟล์นั้นใน bundle อีกรุ่นไม่เจอ (ไม่ได้แปลว่าไฟล์หาย) · **modified = 0 ทุกคู่** แม้ REA มีคลาสนี้ → จะใช้ "modified" เป็นตัวบอกว่าไฟล์ไหนถูกแก้ไม่ได้ ต้องดูการเปลี่ยนจาก unchanged/duplicated → unknown แทน
- unknown 3 ตัวที่มีอยู่แล้วในคู่เวอร์ชันเดียวกัน (`app/globals.css` `eslint.config.mjs` `next.config.ts`) = ไฟล์ที่ไม่ได้ถูกรวมเป็น JS ใน `.next/server` (CSS / config ตอน build) ไม่ใช่การเปลี่ยนแปลง · duplicated 8 ตัว (`lib/*` 7 + `components/AuthShell.tsx`) = โค้ดเดียวกันถูกรวมไว้หลาย chunk (ฝั่ง route API และหน้าเว็บ) จับคู่ได้แบบ `exact`
- REA เทียบแค่ 55 ไฟล์ source (TS/TSX/JS/CSS ที่ควรอยู่ใน bundle) จาก 154 entries · รูป/Markdown/Dockerfile ไม่อยู่ใน bundle จึงพิสูจน์ด้วยชั้น source (ข้อ 1) เท่านั้น

## 4 · เทียบ 3 รายการ

| ไฟล์ (`petshop/…`) | ตั้งใจแก้ (BUG-01.md · CR-01.md) | hash ต่าง (ข้อ 1) | REA: bundle ต่าง (ข้อ 3 · unknown ในคู่ข้ามเวอร์ชัน) | ตรงกันไหม |
|---|---|---|---|---|
| `lib/orders.ts` | ✅ BUG-01 (ลบบล็อก PP-231 · BUG-01.md "แก้แล้ว") + CR-01 (CR-01.md §3 · §6) | ✅ | ✅ | ✅ |
| `lib/pricing.ts` | ✅ CR-01 | ✅ | ✅ | ✅ |
| `lib/store.ts` | ✅ CR-01 | ✅ | ✅ | ✅ |
| `components/OrderSummary.tsx` | ✅ CR-01 | ✅ | ✅ | ✅ |
| `components/CheckoutForm.tsx` | ✅ CR-01 | ✅ | ✅ | ✅ |
| `app/orders/[id]/page.tsx` | ✅ CR-01 | ✅ | ✅ | ✅ |
| `next-env.d.ts` | ❌ | มีแค่ out\v1 | ไม่อยู่ใน 55 ไฟล์ที่ REA เทียบ | ⚠️ อธิบายได้: ไฟล์ที่ `next build` สร้าง (gitignore · v2 build สร้างไฟล์เดียวกันทุกไบต์) ไม่ใช่การแก้ |
| ไฟล์ "ไม่ต้องแตะ" ใน CR-01.md §3 (`app/api/orders/route.ts` `app/api/orders/[id]/route.ts` `app/account/page.tsx` `app/api/coupons/validate/route.ts` `components/CartView.tsx` `ProductDetail.tsx` `app/page.tsx` `Footer.tsx`) | ไม่แก้ | เหมือน | `unchanged` (exact) แม้ในคู่ข้ามเวอร์ชัน (`--md --all` ของ `s2b-v2src-v1build` ตรวจทั้ง 8 ไฟล์) · ไม่อยู่ในตาราง 4 ทิศ | ✅ |

**สรุป:** ตั้งใจแก้ 6 = hash ต่าง 6 = REA เห็น bundle ต่าง 6 (ชุดเดียวกัน) · ส่วนเกินมี 1 (`next-env.d.ts`) อธิบายได้ว่าเป็นไฟล์จาก build · ไม่มี ⚠️ ที่อธิบายไม่ได้

## 5 · Obligation ledger "ของใหม่ต้องทำได้เท่าของเดิม"

ที่มาของพฤติกรรมเดิม: `BASELINE.md` §2–3 (กฎเงินใน TEST-DATA + TC เดิม) · `API-INVENTORY.md` §A (API ตอนรันจริง) · เลือกเฉพาะที่ไฟล์ที่แก้แตะถึง (`pricing.ts` = กฎเงิน/คูปอง/ค่าส่ง · `orders.ts` `store.ts` = สั่งซื้อ · `OrderSummary` `CheckoutForm` `/orders/[id]` = ยอดบนจอ)
หลักฐาน = ผลรันจริงที่บันทึกไว้แล้วกับโค้ดชุดนี้ (source แก้ครั้งสุดท้าย 10:27:45 · image `pawpantry05` build 10:28:03 · ผล LAB 8 ใน `CR-01.md` §6 รันหลังจากนั้น) · **LAB นี้ไม่ได้รันเทสต์ใหม่**

| # | ของเดิมที่ต้องยังทำได้ | ชนิด | หลักฐาน (test · ไฟล์ผล) | ผล |
|---|---|---|---|---|
| O1 | ค่าส่งปกติ ฿50 เมื่อยอดสินค้า < ฿999 (ตะกร้า = ปุ่ม = คำสั่งซื้อ) | positive | `TC-CHAR-SHIP-01` (฿998 → ฿1,048) · `bug01-shipping` ข้างเคียง ฿998 · `TC-CART-01` · `TC-GIFT-08` (฿998 ยังเสีย ฿50) · ผล `CR-01.md` §6 (77/77 × 3 เบราว์เซอร์) · `BUG-01.md` ตารางกรณีเดิมหลังแก้ | ✅ |
| O2 | ส่งฟรีเมื่อยอดสินค้าเกินเส้น (฿1,000 · ฿2,680) | positive | `bug01-shipping` ข้างเคียง ฿1,000 · `TC-CART-03` (฿2,680 ฟรี) · `CR-01.md` §6 · `BUG-01.md` ตารางหลังแก้ (0 · 1000) | ✅ |
| O3 | ส่งด่วน ฿120 ไม่ขึ้นกับเกณฑ์ส่งฟรี | positive | `TC-CHAR-SHIP-04` (฿999 ด่วน → ฿1,119) · `bug01-shipping` ฿999 ส่งด่วน · `TC-GIFT-07` (฿590 + 120 + 30 = ฿740) · `CR-01.md` §6 | ✅ |
| O4 | PAW10 ลด 10% ปัดลง (ตะกร้าและ API validate) | positive | `TC-CPN-01` (฿799 → ลด ฿79) · `TC-CHAR-API-02` golden `tests/new/golden/coupons-validate.json` 30 กรณี · `TC-GIFT-15` (฿189 → ลด 18) · `CR-01.md` §6 | ✅ |
| O5 | FREESHIP ส่งฟรีทุกยอด | positive | `TC-CHK-03` (฿378 หน้าคำสั่งซื้อ) · `bug01-shipping` ฿999 + FREESHIP · `TC-GIFT-06` · `CR-01.md` §6 | ✅ |
| O6 | NEWCAT50 ลด ฿50 เมื่ออาหารแมว ≥ ฿500 | positive | `TC-CPN-03` (฿590 → ฿739) · `TC-CHAR-CPN-01` (฿998 → ฿998 ทุกจุด) · golden coupons-validate · `CR-01.md` §6 | ✅ |
| O7 | NEWCAT50 ยังปฏิเสธเมื่ออาหารแมว < ฿500 / ไม่มีอาหารแมว | negative | `TC-CPN-03` (มีแต่ของหมา → ข้อความ) · golden coupons-validate (฿499 → "ต้องซื้ออาหารแมวขั้นต่ำ ฿500") · `TC-GIFT-16` (POST /api/orders ฿489 → `coupon:null discount:0`) · `CR-01.md` §6 | ✅ |
| O8 | SUMMER20 (หมดอายุ) และโค้ดมั่ว (XYZ) ยังถูกปฏิเสธที่ตะกร้าและ `/api/coupons/validate` | negative | `TC-CPN-02` · golden coupons-validate ("คูปองนี้หมดอายุแล้ว" · "ไม่พบคูปองนี้") · `CR-01.md` §6 | ✅ |
| O9 | SUMMER20/โค้ดมั่วที่ส่งตรงเข้า `POST /api/orders` ไม่ได้ส่วนลด | negative | ไม่มี test ที่ยิงคูปองหมดอายุ/มั่วเข้า `/api/orders` โดยตรง (golden ตรวจแค่ `/api/coupons/validate`) | ⚪ ยังไม่มีหลักฐาน |
| O10 | สั่งซื้อผ่าน API โดยไม่ login → 401 | negative | `TC-API-02` (ชุดเดิม 40/40 × 3 เบราว์เซอร์ · `CR-01.md` §6) | ✅ |
| O11 | client เดิมที่ไม่ส่ง `giftWrap` ได้ยอดเท่าเดิม (`POST /api/orders` 201) | positive | `TC-GIFT-18` (฿239) · `lab8-api.mjs` แถว TC-GIFT-18 (201 · false/0/0/50/239) ใน `CR-01.md` §6 | ✅ |
| O12 | ค่า `giftWrap` ผิดชนิด (`"true"` `1` `"yes"` `null`) ถูกจัดการเป็น "ไม่ห่อ" ไม่ทำให้ยอดผิด | malformed | `TC-GIFT-12` ×4 · `TC-GIFT-13` · `lab8-api.mjs` (201 · false/0/0/50/239 ทั้ง 4) · `CR-01.md` §6 | ✅ |
| O13 | server ไม่เชื่อเงินจาก browser (ปลอม `giftWrapFee` `total` `shippingFee` ใน body) | malformed | `lab8-api.mjs` แถว "ปลอม fee/total ใน body" → 201 · true/30/0/50/269 (`CR-01.md` §6) · ไม่มีใน spec | ✅ (หลักฐานจากสคริปต์ ไม่ใช่ test ถาวร) |
| O14 | body ผิดรูปอื่น ๆ (`items` ว่าง · qty ติดลบ/ไม่ใช่ตัวเลข · slug ไม่มีจริง · `shipping` แปลก) ยังถูกปฏิเสธเหมือนเดิม | malformed | ไม่มี test ทั้งก่อนและหลังแก้ | ⚪ ยังไม่มีหลักฐาน |
| O15 | สั่งซื้อแล้วสต็อกลด | positive | `TC-CHK-04` (ชุดเดิม 40/40 × 3 เบราว์เซอร์ · `CR-01.md` §6) | ✅ |
| O16 | ยอดใน `/account` = หน้าคำสั่งซื้อ = response | positive | `TC-GIFT-03` `TC-GIFT-04` (4 จุด) · `bug01-shipping` (ปุ่ม = คำสั่งซื้อ) · `BUG-01.md` ตารางหลังแก้ (คอลัมน์ /account) | ✅ |
| O17 | `GET /api/products` ไม่เปลี่ยน (ราคาที่ใช้คิดเงิน) | positive | `TC-CHAR-API-01` golden `products.json` 28 รายการ · `CR-01.md` §6 | ✅ |
| O18 | `POST /api/orders` ยังคืน key เดิมครบ (`order{id,userId,items,subtotal,discount,shipping,total,coupon,shippingMethod,payment,address,status,createdAt}` `id`) | positive | test ตรวจแค่บาง field (`total` `shipping` `giftWrap*`) · ยังไม่มี HAR หลังแก้ | ⚪ ยังไม่มีหลักฐาน (เก็บได้ด้วย HAR รอบใหม่) |
| O19 | PAW10 + ยอดใกล้เส้น ฿999 คิดส่งฟรีจากยอดก่อน/หลังส่วนลด | positive (เปลี่ยนโดยตั้งใจ) | `BUG-01.md` ตารางหลังแก้: ฿999 + PAW10 เดิม server ฿950 → ตอนนี้ ฿900 (ปุ่ม = คำสั่งซื้อ) · กฎที่ถูกต้องยังรอเจ้าของร้าน (BUG-01.md "ยังไม่รู้" ข้อ 2) | ⚪ ไม่ใช่ "ทำได้เท่าเดิม" — เปลี่ยนโดยตั้งใจ รอยืนยันกฎ |

รวม 19 ข้อ: ✅ 15 · ❌ 0 · ⚪ 4 (O9 O14 O18 O19)

## สรุป

| หลักฐาน | บอกอะไร | ตรงกับที่ตั้งใจไหม |
|---|---|---|
| SHA-256 `out\v1` vs `petshop` (ข้อ 1) | source ต่าง 6 ไฟล์ · มีแค่ v1 1 ไฟล์ (`next-env.d.ts`) · เหมือน 114 | ✅ 6 = ไฟล์ใน BUG-01.md + CR-01.md · ส่วนเกิน 1 = ไฟล์ที่ build สร้าง |
| build v2 (`out\v2` · exit 0 · 155.2 วิ) + `ev_54c61f33` | โค้ดใหม่ build ผ่าน (TypeScript ผ่าน) · build สร้าง `next-env.d.ts` ตัวเดียวกับ v1 | ✅ |
| s2b คู่เวอร์ชันเดียวกัน `ev_23cd4cec` `ev_f47a7dd1` | 44/0/0/0/0/8/3 ทั้งคู่ → source แต่ละรุ่นตรงกับ build ของตัวเอง | ✅ |
| s2b คู่ข้ามเวอร์ชัน `ev_b034f50f` `ev_ba4bd111` | 41/0/0/0/0/5/9 → 6 ไฟล์ที่แก้กลายเป็น unknown (digest ไม่ตรงกับ bundle อีกรุ่น) · modified = 0 | ✅ 6 ไฟล์เดียวกับข้อ 1 · ไม่มีไฟล์อื่นเปลี่ยนใน bundle |
| ตาราง 3 รายการ (ข้อ 4) | ตั้งใจ = hash ต่าง = bundle ต่าง | ✅ (⚠️ 1 ข้อ อธิบายได้) |
| obligation ledger (ข้อ 5) | กฎเงิน/คูปอง/ค่าส่ง/สั่งซื้อเดิม 15 ข้อมีหลักฐานผ่าน · 4 ข้อยังไม่มีหลักฐาน | ✅ เท่าที่มีหลักฐาน · ⚪ 4 ข้อห้ามถือว่าผ่าน |
