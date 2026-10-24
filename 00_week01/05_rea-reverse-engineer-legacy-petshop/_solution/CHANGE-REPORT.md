# CHANGE-REPORT · ปิดงาน BUG-01 + CR-01 (PawPantry)

> ทำเมื่อ 2026-10-12 · อ่านจาก `CHANGE-PROOF.md` · `BUG-01.md` · `CR-01.md` · `BASELINE.md` · ไม่ได้แก้โค้ด · ไฟล์ใหญ่ใน `out\` ย่อด้วย `node rea\rea-summarize.mjs` เท่านั้น
> ทุกตัวเลขมีไฟล์อ้างอิงในวงเล็บ/คอลัมน์ "ที่มา"
> เพิ่ม PR-1 (คอลัมน์ขวาสุดของหัวข้อ 1) ภายหลัง · ผล test/regression ของ PR-1 มาจากรอบรันจริงของ PR-1 · หัวข้อ 2–5 ยังเป็นของ BUG-01 + CR-01

## 1 · ตารางสรุปงาน

| หัวข้อ | BUG-01 · ค่าส่งที่ยอด ฿999 (ปุ่มยืนยัน ฿999 แต่คำสั่งซื้อ ฿1,049) | CR-01 · บริการห่อของขวัญ | PR-1 · เพิ่ม "สูตรลดก้อนขน" เกินสต็อก แต่ขึ้นข้อความสำเร็จ |
|---|---|---|---|
| ชนิดงาน (Chikofsky & Cross) | **re-engineering** (ขนาดเล็ก) ที่ทำด้วยวิธี restructuring · เหตุผล: ตัวโค้ดคือการลบกฎค่าส่งที่เขียนซ้ำใน `createOrder` ให้ใช้ `computeTotals` ตัวเดียวกับหน้าเว็บ (เปลี่ยนโครงสร้าง) แต่ผลที่ server บันทึกเปลี่ยนจริง 2 กรณี (฿999 ส่งปกติ 1,049 → 999 · ฿999 + PAW10 950 → 900) จึงไม่ใช่ "พฤติกรรมเดิม" ตามนิยาม restructuring · ฝั่งหน้าเว็บ/ปุ่มไม่เปลี่ยนเลย (`BUG-01.md` ตารางกรณีเดิมหลังแก้) | **re-engineering** · เพิ่มความสามารถใหม่ (checkbox · ค่าห่อ · field ใหม่ใน API/ออเดอร์) (`CR-01.md` §1 §6) | **re-engineering** (แก้บั๊กขนาดเล็ก) · เปลี่ยนสิ่งที่ผู้ใช้เห็น (toast เมื่อเพิ่มได้ไม่ครบ) จึงไม่ใช่ restructuring · จำนวนที่ลงตะกร้า/ตรรกะสต็อก (`ShopProvider.tsx addToCart`) และ API ไม่เปลี่ยน |
| ไฟล์ที่แก้ (+/−) | `lib/orders.ts` **+1 −7** (ลบ import 2 ตัว + บล็อก PP-231 5 บรรทัด · เพิ่มคอมเมนต์ 1) (`BUG-01.md` "บรรทัดที่เปลี่ยน") | `lib/pricing.ts` +15 −2 · `lib/orders.ts` +5 −1 (ส่วน CR-01) · `lib/store.ts` +2 −0 · `components/OrderSummary.tsx` +11 −3 · `components/CheckoutForm.tsx` +19 −2 · `app/orders/[id]/page.tsx` +8 −0 · รวม CR-01 **+60 −8** (`CR-01.md` §6) · รวมสองงานเทียบ `out\v1` = 6 ไฟล์ **+61 −15** (`git diff --no-index --numstat` ทุกไฟล์ · `git diff --stat -- petshop` · `CHANGE-PROOF.md` §1) | `components/ProductCard.tsx` **+5 −2** (`git diff --no-index --stat out\v1\components\ProductCard.tsx petshop\components\ProductCard.tsx` → 1 file changed, 5 insertions(+), 2 deletions(-)) · แก้ที่ `useAddToCart` ที่เดียว (บรรทัด 60–65) · รวม 3 งาน `git diff --stat -- petshop` = 7 ไฟล์ +66 −17 |
| test ใหม่ (แดงก่อน / เขียวหลัง) | `tests/new/bug01-shipping.spec.ts` 9 test: ก่อนแก้ **3 failed · 6 passed** → หลังแก้ **9 passed** (chromium) · `char-money.spec.ts` SHIP-02/03 ปรับตามพฤติกรรมที่ตั้งใจเปลี่ยน (`BUG-01.md` "ผล test ก่อน/หลัง") | `tests/new/cr01-giftwrap.spec.ts` 21 test: ก่อนทำ **18 failed · 3 passed** (3 ข้อที่เขียวคือ guard TC-GIFT-13/17/18) → หลังทำ **21/21** ทุกเบราว์เซอร์ (`CR-01.md` §5 §6) | `tests/new/pr1-add-to-cart.spec.ts` 4 test: ก่อนแก้ **2 failed · 2 passed** (TC-PR1-01 2+2 · TC-PR1-02 1+3 แดงเพราะ toast ยังเป็น "✅เพิ่ม … ลงตะกร้าแล้ว" · guard TC-PR1-03 3+1 / TC-PR1-04 1+2 เขียว) → หลังแก้ **4 passed** (chromium · `--repeat-each=3` บน firefox 12/12) |
| regression 3 เบราว์เซอร์ | หลังแก้ BUG-01: chromium **56 passed** (เดิม 40 + bug01 9 + char-money 7) (`BUG-01.md`) · 3 เบราว์เซอร์รวมอยู่ในรอบ CR-01 (คอลัมน์ขวา) | รันทีละเบราว์เซอร์ (reset ต้นทุกรอบ): chromium **77/77** 23.7 วิ · firefox **77/77** 36.5 วิ · webkit **77/77** 1.1 นาที (ชุดเดิม 40 + bug01/char 16 + cr01 21) · `npm run test:all` รอบเดียวล้ม 46/231 เพราะสต็อก `kitten-salmon-dry` หมด (409 "สินค้าไม่พอ") ไม่ใช่เว็บผิด (`CR-01.md` §6) | รันทีละเบราว์เซอร์ (global-setup reset ทุกรอบ): chromium **81/81** 27.6 วิ · firefox **81/81** 39.9 วิ · webkit **81/81** 1.2 นาที (ชุดเดิม 40 + bug01/char 16 + cr01 21 + pr1 4) · `npm run test:all` รอบเดียว **196 passed · 47 failed** 4.8 นาที (firefox 15 · webkit 32): 409 "สินค้าไม่พอ" 21 · ปุ่ม `qty-plus`/คลิกถูก disable (สต็อกหมด) 21 · assertion อื่น 5 รวม TC-PR1-03 firefox ไม่เห็น toast 1 ข้อ (รันแยก + repeat ×3 ผ่าน) → อาการเดิมของ CR-01 คือสต็อกร่วมหมดในรอบเดียว ไม่ใช่เว็บผิด |
| หลักฐาน REA (evidence_id) | source→bundle: คู่เวอร์ชันเดียวกัน `ev_23cd4cec` `ev_f47a7dd1` (44/0/0/0/0/8/3) · ข้ามเวอร์ชัน `ev_b034f50f` `ev_ba4bd111` (41/0/0/0/0/5/9) → `lib/orders.ts` duplicated → unknown (`CHANGE-PROOF.md` §3) · build ใหม่ `ev_54c61f33` | s2b ชุดเดียวกัน: 5 ไฟล์ CR-01 + `lib/orders.ts` เป็น unknown ในคู่ข้ามเวอร์ชันเท่านั้น (`CHANGE-PROOF.md` §3) · HAR หลังแก้ `ev_b1e9e721`: `POST /api/orders` 201 request keys มี `giftWrap` เพิ่ม (ข้อ 3) · compare-application-versions `ev_360083db` (ข้อ 2) | ไม่ได้รัน REA ใน PR-1 (พรอมต์ไม่สั่ง) · หลักฐาน = ทำซ้ำ black-box `rea\scratch\pr1-repro.mjs` (2+2 → toast สำเร็จทั้งสองรอบ · ตะกร้า 3 ชิ้น ฿1,560) + test PR-1 |
| พฤติกรรมที่เปลี่ยนโดยตั้งใจ | ยอดสินค้า ฿999 พอดี (ส่งปกติ) server คิดส่งฟรี → คำสั่งซื้อ ฿999 = ปุ่ม (เดิม ฿1,049) · ฿999 + PAW10 → ฿900 (เดิม ฿950) · กฎค่าส่งเหลือที่เดียว `pricing.ts shippingCost()` (`BUG-01.md`) | /checkout มี checkbox `gift-wrap` (ไม่ติ๊ก) · ติ๊กแล้วบวก ฿30 หรือ "ฟรี" เมื่อยอดสินค้า ≥ ฿1,500 (ก่อนหักส่วนลด) · ไม่นับเข้าส่งฟรี/NEWCAT50 · PAW10/FREESHIP ไม่ลดค่าห่อ · ต่อคำสั่งซื้อ · API รับ `giftWrap === true` เท่านั้น · response/GET มี `giftWrap` `giftWrapFee` · /orders/[id] มีแถวห่อ (`CR-01.md` §2 §4 §6) | เพิ่มได้ไม่ครบที่ขอ → toast แจ้งเตือน (`toast-error` ⚠️) "เพิ่มได้อีกเพียง {n} ชิ้น (สินค้าเหลือ {สต็อก} ชิ้น)" แทนข้อความสำเร็จ · เพิ่มไม่ได้เลย/เพิ่มได้ครบ = ข้อความเดิม · [ร้าน] ตอบใน LAB 10 |
| ความเสี่ยงคงค้าง | ① กฎ "ส่งฟรีดูยอดก่อนหรือหลังส่วนลด" ยังไม่ยืนยันกับเจ้าของร้าน (฿999 + PAW10 ได้ ฿900) (`BUG-01.md` ยังไม่รู้ ข้อ 2) · ② ที่มาของบล็อก PP-231 ยังไม่ได้ถามทีมเดิม (ข้อ 1) · ③ คำสั่งซื้อ ฿1,049 ที่บันทึกไปแล้วต้องจัดการทางธุรกิจ (ข้อ 5) · ④ ข้อความค่าส่งที่เขียนเลขตรงยังซ้ำหลายที่ (`CheckoutForm.tsx` `ProductDetail.tsx` `app/page.tsx` `Footer.tsx` · `CR-01.md` §3) | ① Q7 (≥ ฿1,500) และ Q8 (ไม่มีห่อใน /cart) เป็นสมมติฐาน ⚠️ ยังไม่มีคำตอบร้าน (`CR-01.md` §2) · ② ออเดอร์เก่าใน RAM ไม่มี field ใหม่ (หน้าแสดงต้องถือ `undefined` = ไม่ห่อ) (`CR-01.md` §3) · ③ ตะกร้า API ฿189 ใช้สต็อก `kitten-salmon-dry` มาก ทำให้ `test:all` รอบเดียวล้ม (`CR-01.md` §6) · ④ ledger ⚪ O9 O14 (`CHANGE-PROOF.md` §5) | ① การ์ดสินค้า/Finder ส่ง qty 1 เสมอ จึงไม่มีกรณีเพิ่มได้บางส่วน (เห็นผลจริงแค่หน้าสินค้า) · ② "ซื้อคู่กัน" (`ProductDetail.tsx:79`) และหน้าโปรด (`WishlistView.tsx:18`) ไม่ผ่าน helper นี้ (qty 1 · ไม่กระทบ) · ③ "สินค้าเหลือ" ใช้สต็อกฝั่ง browser (`stockOf`) ซึ่งอาจค้างถ้ามีคนซื้อไปแล้ว (CODEBASE-MAP ยังไม่รู้) · ④ toast หาย 2.8 วิ ทำให้ test ที่ตรวจ toast ไวต่อเครื่องช้า |
| วิธี rollback | คืน `lib/orders.ts` เฉพาะ hunk ของ BUG-01 (ใส่ import `FREE_SHIPPING_MIN` `STANDARD_SHIPPING` + บล็อก PP-231 กลับ ตาม diff ใน `BUG-01.md`) **โดยไม่ทับส่วน CR-01** แล้ว `cd petshop; docker compose up -d --build` · ห้ามคัด `out\v1\lib\orders.ts` ทั้งไฟล์ถ้า CR-01 ยังอยู่ (ไฟล์นี้มีทั้งสองงาน) · ต้องรัน `char-money` คืนค่า legacy-quirk/KNOWN-ISSUE ด้วย | คืน 6 ไฟล์ (`CHANGE-PROOF.md` §1) เป็นรุ่นก่อน CR-01: 5 ไฟล์คัดจาก `out\v1\` ได้ตรง ๆ (`pricing.ts` `store.ts` `OrderSummary.tsx` `CheckoutForm.tsx` `app/orders/[id]/page.tsx`) · `lib/orders.ts` ถอดเฉพาะ +5 −1 ของ CR-01 (คง BUG-01) · rebuild · ไม่ต้อง migrate ข้อมูล (ข้อมูลอยู่ใน RAM · restart ล้าง) · client ที่ส่ง `giftWrap` มาจะถูกเมิน (ยอดเท่า TC-GIFT-18) · ตรวจกลับด้วย s2b: ไฟล์ทั้ง 6 ต้องกลับเป็น unchanged/duplicated กับ `out\v1-server.json` | คัด `out\v1\components\ProductCard.tsx` ทับ `petshop\components\ProductCard.tsx` ได้ทั้งไฟล์ (ไฟล์นี้มีแค่ PR-1 · SHA-256 ก่อนแก้ตรงกับ v1) แล้ว `cd petshop; docker compose up -d --build` · TC-PR1-01/02 จะกลับเป็นแดง |

## 2 · compare-application-versions (ดูข้อจำกัดของอีกเครื่องมือ)

`node rea\rea-input.mjs compare out\v1-server.json out\v2-server.json out\cmp.in.json` (exit 0 · 108,102,488 B) → `REA -Out out\cmp.json compare-application-versions /work/out/cmp.in.json --json` (exit 0 · 17.6 วิ · 9,336,638 B · `ev_360083db`)

| summary | unchanged | added | removed | changed | unknown | items_total |
|---|---|---|---|---|---|---|
| `node rea\rea-summarize.mjs out\cmp.json` | 0 | 0 | 0 | 235 | 1,465 | 1,700 |

ทำไมอ่านยากกว่าตาราง 4 ทิศ:
- เทียบ build กับ build ทีละ node (chunk · source map · parse scope · endpoint) ไม่ได้ผูกกลับไปที่ไฟล์ source → ได้ 1,700 รายการปน `node_modules` และ chunk ของ Next ไม่มีรายการ "ไฟล์ที่เราแก้" ให้เทียบกับ BUG-01/CR-01 ตรง ๆ
- ชื่อ chunk มี hash ที่เปลี่ยนทั้งชุดเมื่อ build ใหม่ และ coverage เป็น partial → node ส่วนใหญ่จับคู่ไม่ได้ (unknown 1,465 · unchanged 0) และ changed 235 ปนการเปลี่ยนที่เกิดจาก build เอง จึงแยกของที่ตั้งใจแก้ไม่ออก · ตาราง 4 ทิศมีคู่ควบคุม (v1→v1 · v2→v2) ทำให้เห็นว่าต่างกันแค่ 6 ไฟล์

## 3 · HAR รอบใหม่เทียบ API-INVENTORY.md

`node rea\record-har.mjs --out out\after` (exit 0 · 3.2 วิ · 8/8 ขั้น · `out\after\har-steps.json` total_ms 2,919 · เดิม 3,080 · reset ข้อมูลก่อนบันทึก · คำสั่งซื้อ `PP-100001`) → `REA -Out out\after\har.json inspect-web-network-capture /work/out/after/pawpantry-main.har har --sensitive-value … --sensitive-value … --json` (exit 0 · 2.1 วิ · 1,766,785 B · `ev_b1e9e721` · 97 records = เดิม 97 ใน `ev_4db99f23`)

| method | path | status เดิม (`API-INVENTORY.md` §A · `ev_4db99f23`) | status หลังแก้ (`ev_b1e9e721`) | request keys เพิ่ม | response keys (ชั้นบน) | ผล |
|---|---|---|---|---|---|---|
| POST | `/api/coupons/validate` | 200 | 200 | – (`code` `items`) | เท่าเดิม `ok` `code` `discount` `freeShipping` `message` | ✅ |
| POST | `/api/auth/login` | 200 | 200 | (REA ปิดทั้ง body) | (ปิด) | ✅ |
| POST | `/api/orders` | 201 | 201 | **`giftWrap`** (UI ส่งเสมอ · เส้นทางนี้ไม่ติ๊ก) | เท่าเดิม `order` `id` | ✅ + key ใหม่ตามตั้งใจ |
| GET | `/api/products` | 200 | 200 | – | เท่าเดิม `items` `total` | ✅ |

API เดิม 4 ตัวยังครบ · status เหมือนเดิมทุกตัว · ไม่มี API ใหม่/หาย · key ที่เพิ่มที่มองเห็น = `giftWrap` ใน request ของ `POST /api/orders` · `giftWrap` `giftWrapFee` ใน `response.order` **มองไม่เห็นจาก rea-summarize** (แสดงแค่ key ชั้นบน) → ดูหัวข้อ 4

## 4 · สิ่งที่หลักฐานยังพิสูจน์ไม่ได้

- key ชั้นในของ `response.order` (`giftWrap` `giftWrapFee` ที่เพิ่ม และ key เดิม 13 ตัวว่ายังครบ) — `rea-summarize` แสดงแค่ `order` `id` · ยืนยันได้แค่ทางอ้อมจาก TC-GIFT-10/11/12 ที่ตรวจ field เหล่านี้ (`CR-01.md` §6) · ledger O18 ยัง ⚪ (`CHANGE-PROOF.md` §5)
- ส่วนลดจาก SUMMER20/โค้ดมั่วที่ยิงตรงเข้า `POST /api/orders` (O9) และ body ผิดรูปอื่น ๆ (O14) — ไม่มี test (`CHANGE-PROOF.md` §5)
- กฎที่ยังเป็นสมมติฐาน/รอเจ้าของร้าน: ส่งฟรีก่อน/หลังส่วนลด (BUG-01 · O19) · Q7 `≥ ฿1,500` · Q8 ไม่มีห่อใน /cart (`CR-01.md` §2) — หลักฐานพิสูจน์ได้แค่ว่าโค้ดทำตามสมมติฐาน ไม่ได้พิสูจน์ว่าสมมติฐานถูก
- REA ไม่ได้บอกว่า "แก้อะไร" ในไฟล์: modified = 0 ทุกคู่ · ไฟล์ที่แก้เห็นเป็น unknown (หา digest ไม่เจอ) เท่านั้น · s2b เทียบ 55 ไฟล์ source จาก 154 entries (`inventory_state: partial`) · รูป/Markdown/Docker เชื่อชั้น SHA-256 อย่างเดียว (`CHANGE-PROOF.md` §1 §3)
- ผล regression เป็นผลของ LAB 8 (บันทึกใน `CR-01.md` §6 · ไม่มีไฟล์ผล reporter แบบ JSON เก็บไว้) · LAB นี้ไม่ได้รันเทสต์ซ้ำ · ยืนยันได้ว่า source ไม่เปลี่ยนหลังจากนั้น (แก้ครั้งสุดท้าย 10:27:45 · image build 10:28:03)
- HAR เดินเส้นทางเดียว (PAW10 · ส่งปกติ · ไม่ติ๊กห่อ) → ไม่เห็นเส้นทางห่อของขวัญ ส่งด่วน หรือ API 9 ตัวที่ไม่อยู่ในเส้นทาง (`API-INVENTORY.md` §C)
- ระบบจริงของร้านใช้โค้ดรุ่นเดียวกับเครื่องทดสอบไหม และลูกค้าที่โดนเก็บเกินที่ ฿999 มีกี่ราย (`BUG-01.md` ยังไม่รู้ ข้อ 4) — ต้องใช้ข้อมูลระบบจริง

## 5 · ไฟล์ผลที่อ้าง

| ไฟล์ | evidence | ใช้ในหัวข้อ |
|---|---|---|
| `CHANGE-PROOF.md` | `ev_23cd4cec` `ev_b034f50f` `ev_ba4bd111` `ev_f47a7dd1` `ev_54c61f33` `ev_ac8d9821` | 1 · 4 |
| `out\cmp.json` | `ev_360083db` | 2 |
| `out\after\har.json` · `out\after\har-steps.json` | `ev_b1e9e721` | 3 |
| `API-INVENTORY.md` (`out\har.json`) | `ev_4db99f23` | 3 |
| `BUG-01.md` · `CR-01.md` · `BASELINE.md` | ผลรัน test LAB 4–8 | 1 · 4 |
