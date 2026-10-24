# 🧩 CR-DESIGN — งานแก้ระบบเดิม PawPantry (บท 05)

> งาน A5 · 2026-10-12 · อ่านคู่กับ `CODEBASE-NOTES.md` (เลขบรรทัดอ้างอิงที่นั่น)
> ตัวเลขทุกตัวที่เขียนว่า **"รันจริง"** มาจาก build ของสำเนา `C:/t/work/a5/petshop` + Playwright 1.64 (Chromium) · ตัวเลขที่เขียนว่า **"คำนวณ"** มาจากกฎ ยังไม่ได้รัน

## 0. สรุปการตัดสินใจ

| เรื่อง | ข้อเสนอ | เหตุผลสั้น ๆ |
|---|---|---|
| **CR-01** ฟีเจอร์ใหม่ | 🎁 **บริการห่อของขวัญ** ฿30/คำสั่งซื้อ · ฟรีเมื่อยอดสินค้า ≥ ฿1,500 | ผ่าน 3 ชั้นครบ (UI checkout + API `/api/orders` + กฎราคา `computeTotals`) · มีขอบ 1,499/1,500 · ทำ prototype แล้ว: 6 ไฟล์, +60/−9 บรรทัด, suite บท 03 ยัง 46/48 เท่าเดิม |
| **BUG-01** บั๊กจากลูกค้า | 💸 **ยอด ฿999 พอดี: หน้าเว็บบอกส่งฟรี แต่คำสั่งซื้อจริงเก็บค่าส่ง ฿50** (server คำนวณค่าส่งซ้ำด้วย `>` แทน `>=`) | บั๊กเงินที่ลูกค้าเห็นเอง · **suite บท 03 จับไม่ได้** (46/48 เท่าเดิม รันจริง) → สอน "เทสต์เขียวไม่ได้แปลว่าไม่มีบั๊ก" · ถ้าแก้แค่ปลายเหตุ จะทำให้ CR-01 พังต่อ (รันจริง) |
| BUG_MODE | **เอาออกจากบท 05** (ล็อกพฤติกรรมเท่ากับ `BUG_MODE=0`) | ระบบเดิมจริงไม่มีสวิตช์บอกตำแหน่งบั๊ก · `grep bugMode` เฉลยบั๊กใน 10 วินาที |
| ลำดับในบท | เข้าใจระบบ → **BUG-01 ก่อน** → CR-01 | CR-01 แตะ `lib/orders.ts` ไฟล์เดียวกับต้นเหตุ BUG-01 |

---

## 1. CR-01 — ฟีเจอร์ใหม่

### 1.1 ตัวเลือก 3 แบบ และการจัดอันดับ

| เกณฑ์ (น้ำหนัก) | **A. ห่อของขวัญ +฿30 (ฟรี ≥ ฿1,500)** | B. ส่งด่วนฟรีเมื่อซื้อครบ ฿2,000 | C. คูปอง `DOG15` (อาหารสุนัข 15% ขั้นต่ำ ฿600 ลดสูงสุด ฿200) |
|---|---|---|---|
| แตะหลายชั้น (×3) | ✅✅ UI (checkbox + แถวสรุป 2 หน้า) · API (field ใหม่ใน POST `/api/orders` + response) · กฎราคา · โมเดล `Order` | ✅ กฎราคา `shippingCost` · ข้อความฮาร์ดโค้ด 4 จุด · API ไม่เปลี่ยนสัญญา | ⚠️ กฎราคาเกือบทั้งหมด · UI แทบไม่เปลี่ยน (แค่ข้อความ) |
| ทดสอบชัด มีขอบ (×3) | ✅ 1,499/1,500 ทำได้ด้วยสินค้า 3 ชิ้น · มีกรณีผสมคูปอง/ด่วน | ✅ 1,999 (4 ชิ้น) / 2,000 (3 ชิ้น) | ✅ 599/600 · เพดาน 1,333/1,334 (ตะกร้า 4–5 ชิ้น ยุ่งกว่า) |
| ฝึก impact analysis (×2) | ✅✅ กับดัก: หน้า `/orders/[id]` ไม่ใช้ `SummaryRows` · server ต้องไม่เชื่อค่าจาก client · ชนกับ BUG-01 | ✅ กับดัก: "฿120" ฮาร์ดโค้ดใน `CheckoutForm.tsx:230`, `ProductDetail.tsx:251` | ⚠️ น้อย: ทุกอย่างผ่าน `evaluateCoupon` |
| ความเสี่ยงทำ test เดิมพัง (×1, ต่ำ = ดี) | ต่ำ (ค่าเริ่มต้น = ไม่ห่อ) · รันจริง 46/48 เท่าเดิม | ต่ำ (test เดิมใช้ด่วนที่ ≤ ฿999) | ต่ำ |
| ขนาดงาน (×1, เล็ก = ดี) | กลาง (6 ไฟล์) | เล็ก (1 ไฟล์ตรรกะ + 4 ข้อความ) | เล็กมาก (1–2 ไฟล์) |
| **อันดับ** | 🥇 **เลือก** | 🥈 → ใช้เป็นแบบฝึก PR-2 | 🥉 → ใช้เป็นแบบฝึก PR-3 |

### 1.2 ใบ Change Request (ให้ผู้เรียน)

> **CR-01 · บริการห่อของขวัญ** — ลูกค้าขอให้ห่อเป็นของขวัญได้ตอนชำระเงิน คิด ฿30 ต่อคำสั่งซื้อ ถ้ายอดสินค้าครบ ฿1,500 ห่อฟรี

**Acceptance criteria**

| AC | เงื่อนไข |
|---|---|
| AC1 | หน้า `/checkout` มี checkbox "ห่อของขวัญ" (`data-testid="gift-wrap"`) **ค่าเริ่มต้นไม่ติ๊ก** |
| AC2 | ติ๊กแล้ว สรุปยอดมีแถว "ห่อของขวัญ" (`summary-giftwrap`) แสดง `฿30` หรือ `ฟรี` และ `summary-total` + ปุ่ม `place-order` รวมค่าห่อทันที · ไม่ติ๊ก = ไม่มีแถวนี้ |
| AC3 | ค่าห่อ = ฿30 ถ้า **ยอดสินค้าก่อนหักส่วนลด** < ฿1,500 · = ฿0 ถ้า ≥ ฿1,500 |
| AC4 | ค่าห่อ **ไม่นับ** เข้ายอดส่งฟรี ฿999 / ขั้นต่ำ NEWCAT50 · PAW10 ไม่ลดค่าห่อ · FREESHIP ไม่ยกเว้นค่าห่อ |
| AC5 | ยอดชำระ = ยอดสินค้า − ส่วนลด + ค่าส่ง + ค่าห่อ (คำนวณใหม่ที่ server เสมอ) |
| AC6 | POST `/api/orders` รับ `giftWrap: true` (boolean เท่านั้น ค่าอื่นถือว่าไม่ห่อ) · response และ GET `/api/orders/[id]` มี `giftWrap` (bool) และ `giftWrapFee` (number) |
| AC7 | หน้า `/orders/[id]` แสดงแถว "ห่อของขวัญ" ตรงกับที่สั่ง · ยอดใน `/account` ตรงกับหน้าคำสั่งซื้อ |
| AC8 | ไม่ทำให้ test เดิมของบท 03 ที่ผ่านอยู่ล้ม (ต้อง 46/48 เหมือนก่อนแก้) |

> 💡 จุดที่ตั้งใจให้ผู้เรียน **ถามเจ้าของงานก่อนเขียนโค้ด**: ฿1,500 ดูก่อนหรือหลังหักส่วนลด (AC3) · FREESHIP/PAW10 เกี่ยวกับค่าห่อไหม (AC4) · ค่าห่อต่อคำสั่งซื้อหรือต่อชิ้น — เฉลยตอบตามตารางด้านบน (ยึดแบบเดียวกับกฎส่งฟรีเดิม = ก่อนหักส่วนลด)

### 1.3 ค่าขอบและผลที่คาดหวัง (รันจริงบน prototype ผ่าน API + UI)

| # | ตะกร้า (ส่งธรรมดา เว้นแต่ระบุ) | ห่อ | คูปอง | ยอดสินค้า | ส่วนลด | ค่าส่ง | ค่าห่อ | **ยอดชำระ** | หมายเหตุ |
|---|---|---|---|---|---|---|---|---|---|
| W1 | ลูกแมว 400 g ×1 | ไม่ | — | 189 | 0 | 50 | — | **239** | ค่าเริ่มต้นไม่เปลี่ยน |
| W2 | ลูกแมว 400 g ×1 | ✅ | — | 189 | 0 | 50 | 30 | **269** | UI: ตะกร้า/ปุ่ม/หน้าคำสั่งซื้อ = 269 ✅ |
| W3 | ไม้ตกแมว + ชามกินช้า ×3 (฿999) | ✅ | — | 999 | 0 | ฟรี | 30 | **1,029** | ค่าห่อไม่ทำให้เสียสิทธิ์ส่งฟรี |
| W4 | ลูกแมว 400 g + น้ำพุแมว + สุนัขพันธุ์เล็ก (฿1,499) | ✅ | — | 1,499 | 0 | ฟรี | 30 | **1,529** | **ขอบล่าง** · UI ✅ |
| W5 | ชามกินช้า + สุนัขโต แกะ 3 kg + สุนัขพันธุ์เล็ก (฿1,500) | ✅ | — | 1,500 | 0 | ฟรี | ฟรี | **1,500** | **ขอบ** · UI ✅ |
| W6 | เหมือน W5 | ✅ | PAW10 | 1,500 | 150 | ฟรี | ฟรี | **1,350** | ดูยอดก่อนหักส่วนลด (AC3) |
| W7 | ลูกแมว 400 g | ✅ | FREESHIP | 189 | 0 | ฟรี | 30 | **219** | FREESHIP ไม่ยกเว้นค่าห่อ (AC4) |
| W8 | ลูกแมว 1.5 kg ส่งด่วน | ✅ | — | 590 | 0 | 120 | 30 | **740** | |
| W9 | ลูกแมว 400 g · API ส่ง `giftWrap: "true"` | (สตริง) | — | 189 | 0 | 50 | — | **239** | AC6 ต้องเป็น boolean |
| W10 | ลูกแมว 400 g · API ส่ง `giftWrap: 1` | (ตัวเลข) | — | 189 | 0 | 50 | — | **239** | AC6 |

ไม่มีตะกร้าที่ได้ ฿1,501 ด้วยสินค้า ≤ 3 ชิ้น (ค้นด้วยสคริปต์) → ใช้คู่ 1,499/1,500 + ค่าไกล (189, 999) แทน

### 1.4 ไฟล์ที่คาดว่าต้องแก้ (จาก prototype จริง)

| ไฟล์ | แก้อะไร | ชั้น | กับดัก |
|---|---|---|---|
| `lib/pricing.ts` | ค่าคงที่ `GIFT_WRAP_FEE` `GIFT_WRAP_FREE_MIN` · `giftWrapCost()` · `computeTotals({giftWrap})` · `Totals.giftWrap` `giftWrapSelected` | กฎราคา (ใช้ทั้ง client/server) | ต้องเพิ่มที่ **ฟังก์ชันเดียว** ไม่คำนวณซ้ำใน component |
| `lib/orders.ts` | รับ `input.giftWrap === true` ส่งเข้า `computeTotals` · เก็บลง order | API/server | ห้ามรับ "ยอด/ค่าห่อ" จาก client · ⚠️ ถ้า BUG-01 ถูกแก้แบบปลายเหตุ บล็อกคำนวณค่าส่งซ้ำจะเขียนทับ `total` → ค่าห่อหาย (หัวข้อ 2.6) |
| `lib/store.ts` | `Order.giftWrap: boolean` · `giftWrapFee: number` | โมเดลข้อมูล | — |
| `components/OrderSummary.tsx` | `useCartTotals(shipping, giftWrap)` · แถว `summary-giftwrap` ใน `SummaryRows` | UI (ตะกร้า + checkout) | — |
| `components/CheckoutForm.tsx` | state + checkbox `gift-wrap` · ส่ง `giftWrap` ใน body | UI | ปุ่ม `ยืนยันสั่งซื้อ ฿…` ใช้ `totals.total` อยู่แล้ว → ได้ฟรี |
| `app/orders/[id]/page.tsx` | แถว `summary-giftwrap` | UI | ⚠️ หน้านี้ **เขียน summary เอง** ไม่ใช้ `SummaryRows` → ลืมง่ายที่สุด |
| (ไม่ต้องแก้) `app/api/orders/route.ts` · `app/account/page.tsx` | route ส่ง body ทั้งก้อนเข้า `createOrder` · บัญชีใช้ `o.total` | — | ผู้เรียนควร "ยืนยันว่าไม่ต้องแก้" ไม่ใช่เดา |

ขนาด prototype: 6 ไฟล์ +60/−9 · `next build` (มี typecheck) ผ่าน · diff เต็มอยู่ในภาคผนวก A

### 1.5 เทสต์ที่ต้องเพิ่ม

| ID | สิ่งที่ทดสอบ | เทคนิค | ระดับ | ผลที่คาดหวัง |
|---|---|---|---|---|
| TC-GIFT-01 | W1 → ติ๊ก → W2 แล้วสั่งซื้อ | Happy / State | P1 | ไม่ติ๊ก: ไม่มีแถว ยอด ฿239 · ติ๊ก: แถว ฿30 ยอด/ปุ่ม ฿269 · หน้าคำสั่งซื้อ ฿30 / ฿269 |
| TC-GIFT-02 | W4 vs W5 | Boundary | P1 | ฿1,499 → ค่าห่อ ฿30 ยอด ฿1,529 · ฿1,500 → ฟรี ยอด ฿1,500 |
| TC-GIFT-03 | W6 (PAW10) และ W7 (FREESHIP) | Partition | P1 | ฿1,350 · ฿219 |
| TC-GIFT-04 | ติ๊ก → เอาติ๊กออก ก่อนสั่ง | State | P2 | แถวหาย ยอดกลับ ฿239 · คำสั่งซื้อ `giftWrap=false` |
| TC-GIFT-05 | API: `giftWrap` เป็น `"true"`, `1`, ไม่ส่ง (W9/W10) | Negative / API | P2 | ไม่คิดค่าห่อ ยอด ฿239 |
| TC-GIFT-06 | ยอดใน `/account` = หน้าคำสั่งซื้อ (W2) | State | P2 | ฿269 ทั้ง 2 หน้า |

Playwright ตัวอย่างที่รันผ่านแล้วบน prototype: TC-GIFT-01/02 (3 กรณี W2/W4/W5 · `C:/t/work/a5/e2e/tests/a5-cr01.spec.ts` → 3 passed)

### 1.6 test เดิมที่เสี่ยง (และผลจริง)

| test เดิม | ทำไมเสี่ยง | ผลบน prototype (รันจริง) |
|---|---|---|
| TC-CHK-01, CHK-06, SHIP-03, SHIP-04 | ตรวจตัวเลขในปุ่ม `place-order` / `summary-total` ของหน้า checkout | ✅ ผ่าน (ค่าเริ่มต้นไม่ห่อ) |
| TC-ACC-01, CHK-07 | ยอดในหน้าคำสั่งซื้อ/บัญชี | ✅ ผ่าน |
| TC-SEC-03 | ส่งข้อมูลปลอมจาก localStorage → server ต้องคำนวณใหม่ | ✅ ผ่าน |
| TC-UI-01 (จอ 390 px) | section ใหม่ในฟอร์มทำให้หน้ายาวขึ้น/ล้นจอ | ✅ ผ่าน |
| `checkSummary()` ใน `fixtures.ts` | อ่านตาม `data-testid` ไม่ใช่ลำดับแถว → แถวใหม่ไม่กระทบ | ✅ |
| **รวม suite บท 03** | | **46/48** = เท่าก่อนแก้ (ล้ม SRCH-01, CART-05 เดิม) |

---

## 2. BUG-01 — บั๊กที่ลูกค้าแจ้ง (ต้องมีอยู่จริงโดยไม่พึ่ง BUG_MODE)

### 2.1 ตัวเลือกบั๊กที่จะฝัง

| ตัวเลือก | สมจริง | ลูกค้าเห็นเอง | suite บท 03 จับได้? | สอนอะไร | เลือก |
|---|---|---|---|---|---|
| ทำ PAW10 = 1% ถาวร (`pricing.ts:115`) | ต่ำ (ใครก็เห็นตอน QA) | ✅ | ✅ COUP-01..03 | น้อย — ซ้ำบท 03 | ❌ |
| ทำเบอร์ 9 หลักผ่านถาวร (`validation.ts:82`) | กลาง | ❌ ลูกค้าไม่บ่น (ร้านเดือดร้อน) | ✅ CHK-03 | ซ้ำบท 03 | ❌ |
| `shippingCost` ใช้ `>` แทน `>=` (`pricing.ts:135`) | กลาง | ✅ | ✅ SHIP-02 | "รัน regression ก่อน" | สำรอง |
| อีเมลตัวพิมพ์ใหญ่ login ไม่ได้ (`store.ts:110-111` ไม่ lowercase) | สูง (คีย์บอร์ดมือถือ) | ✅ | ✅ REG-03 ล้ม | auth / data | สำรอง |
| **server คำนวณค่าส่งซ้ำด้วย `>` (`orders.ts`)** | **สูง** — โค้ด "กันโกง" ที่มี comment อ้าง ticket แต่ตรรกะซ้ำ | ✅ เห็นยอดไม่ตรงกับปุ่มที่กด | ❌ **ไม่ได้** (รันจริง) | client/server divergence · เทสต์เขียว ≠ ไม่มีบั๊ก · แก้ที่ต้นเหตุ · หลักฐานจาก network/HAR (มุม REA) | ✅ |

### 2.2 diff ที่ต้องใส่ (ให้ผู้สร้างบทใส่ใน `05_rea-reverse-engineer-legacy-petshop/petshop/` — A5 **ไม่ได้แก้** ไฟล์บท)

```diff
diff --git a/lib/orders.ts b/lib/orders.ts
--- a/lib/orders.ts
+++ b/lib/orders.ts
@@ -1,6 +1,13 @@
 import "server-only";
 import { getProduct } from "./products";
-import { computeTotals, priceLines, type CartLine, type ShippingMethod } from "./pricing";
+import {
+  FREE_SHIPPING_MIN,
+  STANDARD_SHIPPING,
+  computeTotals,
+  priceLines,
+  type CartLine,
+  type ShippingMethod,
+} from "./pricing";
 import { db, nextOrderId, type Order, type User } from "./store";
 import { PROVINCES, validateShipping, type ShipInput } from "./validation";
 
@@ -53,6 +60,11 @@ export function createOrder(user: User, input: CreateOrderInput, bugMode: boolea
   const payment = input.payment === "promptpay" ? "promptpay" : "cod";
   const couponCode = typeof input.coupon === "string" && input.coupon.trim() ? input.coupon : null;
   const totals = computeTotals({ lines, couponCode, shipping, bugMode });
+  // PP-231: server must not trust the shipping fee shown in the browser — recompute it here.
+  if (shipping === "standard" && !totals.coupon?.freeShipping) {
+    totals.shipping = totals.subtotal > FREE_SHIPPING_MIN ? 0 : STANDARD_SHIPPING;
+    totals.total = Math.max(0, totals.subtotal - totals.discount + totals.shipping);
+  }
 
   for (const [slug, qty] of qtyBySlug) store.stock[slug] -= qty;
 
```

ทดสอบ diff แล้ว: apply บนสำเนา → `next build` ผ่าน · ไฟล์ในบทเป็น **CRLF** (git autocrlf) → ใช้ `git apply --ignore-whitespace` หรือแก้มือ · ตรรกะไม่ขึ้นกับ BUG_MODE (รันคู่กับ `BUG_MODE=0` เท่านั้น) · ถ้าเอา BUG_MODE ออกตามหัวข้อ 3 ให้ใส่ diff นี้ **หลัง** เอาออก บรรทัด `computeTotals({ ..., bugMode })` จะเป็น `computeTotals({ lines, couponCode, shipping })`

### 2.3 ข้อความจากลูกค้า (ไม่บอกสาเหตุ)

> **เรื่อง: โดนเก็บเงินเกินจากที่หน้าเว็บบอก**
> สวัสดีค่ะ เมื่อวานสั่งของในร้าน ไม้ตกแมว 1 อัน กับชามกินช้า 3 ใบ ในตะกร้าขึ้นว่า "ได้ส่งฟรีแล้ว!" ตอนกดปุ่มก็เขียนว่า "ยืนยันสั่งซื้อ ฿999" แต่พอสั่งเสร็จ หน้าคำสั่งซื้อกับในประวัติบัญชีกลับเป็น ฿1,049 ค่ะ เก็บเงินปลายทางด้วย กลัวไรเดอร์เก็บเกิน ฝากตรวจสอบให้หน่อยนะคะ ก่อนหน้านี้สั่งยอดพันกว่าบาทไม่เคยเป็นแบบนี้
> — คุณนุ่น (เลขที่คำสั่งซื้อ PP-100001)

### 2.4 ขั้นตอนทำซ้ำ + หลักฐาน (รันจริง หลังใส่ diff, `BUG_MODE=0`)

| ขั้น | ทำ | เห็น |
|---|---|---|
| 1 | `POST /api/test/reset` · login `demo@pawpantry.test` / `Paw12345` | — |
| 2 | ใส่ ไม้ตกแมว ×1 (฿129) + ชามกินช้า ×3 (฿290) → `/cart` | ยอดสินค้า ฿999 · ค่าส่ง **ฟรี** · ยอดชำระ **฿999** · แถบ "ได้ส่งฟรีแล้ว!" |
| 3 | `/checkout` กรอกที่อยู่มาตรฐาน ส่งธรรมดา COD | ปุ่ม **"ยืนยันสั่งซื้อ ฿999"** · การ์ดส่งธรรมดาเขียน "ฟรี" |
| 4 | กดยืนยัน | response `POST /api/orders` → `subtotal 999, shipping 50, total 1049` |
| 5 | หน้า `/orders/PP-100001` และ `/account` | ยอดชำระ **฿1,049** · แถว `PP-100001 4 ชิ้น รับคำสั่งซื้อ ฿1,049` |

ตารางขอบ (API รันจริง):

| ตะกร้า | ก่อนใส่บั๊ก (ยอดชำระ) | หลังใส่บั๊ก | ถูก? |
|---|---|---|---|
| ฿998 ส่งธรรมดา | ส่ง 50 → 1,048 | ส่ง 50 → 1,048 | ✅ เหมือนกัน |
| **฿999 ส่งธรรมดา** | ส่งฟรี → 999 | **ส่ง 50 → 1,049** | ❌ |
| **฿999 + PAW10** | −99 ส่งฟรี → 900 | **−99 ส่ง 50 → 950** | ❌ |
| ฿999 + FREESHIP | ส่งฟรี → 999 | ส่งฟรี → 999 | ✅ |
| ฿999 ส่งด่วน | 120 → 1,119 | 120 → 1,119 | ✅ |
| ฿1,560 / ฿1,590 ส่งธรรมดา | ส่งฟรี | ส่งฟรี | ✅ |

→ ผิดเฉพาะ **ยอดสินค้าก่อนหักส่วนลด = ฿999 พอดี + ส่งธรรมดา + ไม่ใช้ FREESHIP** และผิดเฉพาะ **ฝั่ง server** (ตะกร้า/checkout แสดงถูก)

**suite บท 03 กับบั๊กนี้ (รันจริง Chromium):** ก่อนใส่ 46/48 · หลังใส่ **46/48 เท่าเดิม** (ล้มแค่ SRCH-01, CART-05 เดิม) → TC-SHIP-02 ผ่านเพราะตรวจแค่หน้าตะกร้า · test repro ใหม่ (`a5-bug01.spec.ts`) ล้มก่อนแก้ ✅ ผ่านหลังแก้

### 2.5 สาเหตุ (root cause)

- `lib/orders.ts` มี **กฎค่าส่งชุดที่ 2** ที่คำนวณทับผลของ `computeTotals()` (กฎชุดจริงใน `lib/pricing.ts:133-136` ใช้ `>=`)
- ชุดที่ 2 ใช้ `>` → ฿999 ไม่ถือว่า "ครบ" · และเขียนทับ `totals.total` เอง
- ฝั่ง browser ใช้ `computeTotals()` ตัวจริง → หน้าเว็บกับคำสั่งซื้อคิดคนละสูตร (client/server divergence)
- comment `PP-231 … must not trust the shipping fee shown in the browser` ฟังดูมีเหตุผล แต่ไม่จริง — client ไม่เคยส่งค่าส่งมาเลย (`CheckoutForm.tsx:77` ส่งแค่ `shipping: "standard"|"express"`) → ตัวอย่าง "comment ในระบบเดิมเชื่อไม่ได้"

### 2.6 วิธีแก้ที่ถูก + ทำไมไม่ใช่แค่เปลี่ยน `>` เป็น `>=`

| วิธีแก้ | ผล BUG-01 | ผลต่อ CR-01 (รันจริง) | ข้อสรุป |
|---|---|---|---|
| ✅ **ลบบล็อกคำนวณซ้ำ + import ที่ไม่ใช้** (= reverse diff ข้อ 2.2) ให้ `computeTotals()` เป็นแหล่งเดียว | ฿999 → 999 ✅ (repro ผ่าน) · suite 46/48 | prototype ห่อของขวัญถูกทุกกรณี W1–W10 | **แนะนำ** — แก้ที่ต้นเหตุ |
| ⚠️ เปลี่ยน `>` เป็น `>=` อย่างเดียว | ฿999 → 999 ✅ (repro ผ่าน) | ❌ **W2: หน้า checkout/ปุ่ม ฿269 แต่คำสั่งซื้อ ฿239** · W3 1,029 → 999 · W4 1,529 → 1,499 (บล็อกซ้ำเขียนทับ `total` โดยไม่รู้จักค่าห่อ) · TC-GIFT แบบ UI ล้ม 2/3 | ปิดอาการ แต่ทิ้งกับดักไว้ให้ CR ถัดไป |

diff แก้ที่ถูก:

```diff
--- a/lib/orders.ts
+++ b/lib/orders.ts
@@ -1,13 +1,6 @@
 import "server-only";
 import { getProduct } from "./products";
-import {
-  FREE_SHIPPING_MIN,
-  STANDARD_SHIPPING,
-  computeTotals,
-  priceLines,
-  type CartLine,
-  type ShippingMethod,
-} from "./pricing";
+import { computeTotals, priceLines, type CartLine, type ShippingMethod } from "./pricing";
 import { db, nextOrderId, type Order, type User } from "./store";
 import { PROVINCES, validateShipping, type ShipInput } from "./validation";
 
@@ -60,11 +53,6 @@
   const totals = computeTotals({ lines, couponCode, shipping, bugMode });
-  // PP-231: server must not trust the shipping fee shown in the browser — recompute it here.
-  if (shipping === "standard" && !totals.coupon?.freeShipping) {
-    totals.shipping = totals.subtotal > FREE_SHIPPING_MIN ? 0 : STANDARD_SHIPPING;
-    totals.total = Math.max(0, totals.subtotal - totals.discount + totals.shipping);
-  }
 
   for (const [slug, qty] of qtyBySlug) store.stock[slug] -= qty;
```

เทสต์ที่ผู้เรียนต้องเพิ่ม (regression ของ BUG-01):

| ID | สิ่งที่ทดสอบ | ผลที่คาดหวัง (ที่มา) |
|---|---|---|
| TC-SHIP-05 | ฿999 ส่งธรรมดา **สั่งซื้อจนจบ** ตรวจปุ่ม + หน้าคำสั่งซื้อ + `/account` + response API | ฿999 ทุกจุด · `shipping: 0` — [D] TEST-DATA "ฟรีเมื่อซื้อครบ ฿999" |
| TC-SHIP-06 | ฿998 ส่งธรรมดา สั่งจนจบ | ฿1,048 ทุกจุด (คู่ขอบ) |
| TC-SHIP-07 | ฿999 + PAW10 สั่งจนจบ | ส่วนลด ฿99 · ส่งฟรี · ฿900 (ยึดกฎเดิม: ส่งฟรีดูยอดก่อนหักส่วนลด) |
| (หลัก) | "ตัวเลขบนปุ่มยืนยัน = ยอดในคำสั่งซื้อ" สำหรับทุก test ที่สั่งซื้อจนจบ | oracle ใหม่: [R] เงินที่แสดงก่อนกดต้องเท่ากับเงินที่เก็บ |

---

## 3. BUG_MODE — เก็บไว้ไหมในบท 05

| | เก็บไว้ (เหมือนบท 03) | **เอาออก (ล็อกเป็นพฤติกรรม BUG_MODE=0)** |
|---|---|---|
| ข้อดี | คัดลอกบท 03 ได้เลย · ใช้ BUG-HUNT บท 03 อ้างอิงได้ · ให้ REA `compare-application-versions` เทียบ 2 โหมดได้ | **สมจริง**: ระบบที่ทีมเก่าทิ้งไว้ไม่มีสวิตช์บอกบั๊ก · ไม่มี `data-bug-mode` ใน HTML/bundle ให้ REA/ผู้เรียนเห็นเฉลย · BUG-01 เป็นบั๊กเดียวที่ต้องหาเอง · โค้ดอ่านง่ายขึ้น (−1 พารามิเตอร์ใน 11 ไฟล์) |
| ข้อเสีย | `grep -rn bugMode` เจอ 3 บั๊กทันที → ทำลายแบบฝึก "เข้าใจระบบ" · ผู้เรียนสับสนว่าบั๊กไหน "ของจริง" · Agent อาจ "แก้" BUG_MODE แทนงานจริง | ต้องแก้ ~11 ไฟล์ (เสี่ยงพลาดถ้าทำมือ) · บท 05 แยกจากบท 03 (ต้องบอกในบทว่าเป็นคนละ build) |
| ผลต่อ test บท 03 | 46/48 (โหมด 0, รันจริง) | คาดว่า 46/48 เท่าโหมด 0 (suite บท 03 ไม่ได้อ่าน BUG_MODE) — ยังไม่ได้รันกับ build ที่เอาออกจริง |

**ข้อเสนอ: เอาออก** และใช้ BUG-01 + บั๊กเดิม CART-05 (มีอยู่แล้วในโค้ด) เป็นบั๊ก "ของจริง" ของบท · ถ้าอยากใช้มุม REA เทียบเวอร์ชัน ให้เทียบ build "ก่อน/หลังแก้ BUG-01" หรือ "ก่อน/หลัง CR-01" แทน (มีความหมายกว่าเทียบโหมดบั๊ก)

เช็กลิสต์การเอาออก (ผลต้องเท่ากับ `BUG_MODE=0` ทุกจุด):

| ไฟล์ | แก้เป็น |
|---|---|
| `lib/bugmode.ts` | ลบทั้งไฟล์ |
| `lib/pricing.ts:91-95,115,142-146` | ลบพารามิเตอร์ `bugMode` · `PAW10` → `Math.floor((subtotal * 10) / 100)` |
| `lib/validation.ts:81-82,86,89` | `isValidPhone(phone)` ใช้ `/^0\d{9}$/` อย่างเดียว · `validateShipping(input)` |
| `lib/orders.ts:19,34,55` | ลบพารามิเตอร์ `bugMode` |
| `app/api/orders/route.ts:3,25` · `app/api/coupons/validate/route.ts:2,16` | ลบ import + อาร์กิวเมนต์ |
| `app/layout.tsx:16,19,37,42,44` | ลบ `serverBugMode` · ลบ `data-bug-mode` · ไม่ส่ง prop `bugMode` |
| `components/ShopProvider.tsx:27,108,113,225-227,238-241,288,314` | ลบ `bugMode` · `setWishlistBadge(next.length)` ทั้ง 2 จุด (หรือแทน `wishlistBadge` ด้วย `wishlist.length`) |
| `components/OrderSummary.tsx:4,9,12-13` · `CheckoutForm.tsx:5,43,69` · `CartView.tsx:137,168` | ลบ `bugMode`/`clientBugMode` |
| `docker-compose.yml` · `Dockerfile` (comment) · `petshop/README.md` | ลบ `BUG_MODE` |
| ตรวจรับ | `grep -rni bug_\?mode petshop/` = 0 · `npm run typecheck` · suite บท 03 = 46/48 |

---

## 4. แบบฝึกท้ายบท (Practice CR) 3 ข้อ

| ID | ประเภท | โจทย์ (ข้อความถึงผู้เรียน) | จุดในโค้ด | ค่าขอบ / ผลที่คาดหวัง | เกณฑ์ผ่าน |
|---|---|---|---|---|---|
| **PR-1** | บั๊ก (มีอยู่แล้วในระบบ) | "ลูกค้ากดเพิ่มสูตรลดก้อนขน 2 ชิ้น 2 รอบ ระบบบอก 'เพิ่ม…ลงตะกร้าแล้ว' แต่ตะกร้ามีแค่ 3 ชิ้น" | `components/ProductCard.tsx:62-65` (`useAddToCart` เช็กแค่ `added > 0`) · ใช้ทั้งหน้าสินค้า/การ์ด/Finder | ใส่ 2 → "เพิ่ม…แล้ว" · ใส่อีก 2 → เพิ่มได้ 1 ข้อความต้องบอกว่าได้แค่ 1 / ครบสต็อก (ร่างข้อความ: `เพิ่มได้อีกเพียง 1 ชิ้น (สินค้าเหลือ 3 ชิ้น)`) · ตะกร้า 3 ชิ้น ฿1,560 | TC-CART-05 ที่ล้มอยู่ (ทุกการรันใน A5) เปลี่ยนเป็นผ่าน · คาดว่า suite = 47/48 (ยังไม่ได้ implement/รัน) |
| **PR-2** | ฟีเจอร์ (ตัวเลือก B) | "ส่งด่วนฟรีเมื่อซื้อครบ ฿2,000" | `lib/pricing.ts:133-136` + ข้อความ "฿120" ฮาร์ดโค้ด `CheckoutForm.tsx:230`, `ProductDetail.tsx:251` | (คำนวณ) ฿1,999 ด่วน = ไม้ตกแมว + ชามกินช้า + ลูกแมว 1.5 kg + สุนัขสูงวัย แซลมอน → ฿2,119 · ฿2,000 ด่วน = ลูกแมว 1.5 kg + สุนัขสูงวัย แซลมอน + สุนัขพันธุ์เล็ก → ฿2,000 · ฿999 ด่วนยังเป็น ฿1,119 | การ์ดส่งด่วนบอกฟรีเมื่อครบ · TC-SHIP-03 ยังผ่าน · คำสั่งซื้อจริงตรงกับปุ่ม |
| **PR-3** | ฟีเจอร์ (ตัวเลือก C) | "คูปอง `DOG15` ลด 15% เฉพาะอาหารสุนัข (เม็ด/เปียก/ขนม) ยอดอาหารสุนัข ≥ ฿600 ลดสูงสุด ฿200 ปัดลง" | `lib/pricing.ts:91-131` (`evaluateCoupon` + `COUPON_MESSAGES`) | (คำนวณ) ฿599 (สตูว์แพ็ค 6 + ขนมขัดฟัน 7 ชิ้น) → ไม่ผ่าน · ฿600 (แกะบด ×4 + สุนัขพันธุ์เล็ก) → −฿90 · ฿1,333 (สุนัขสูงวัย + แกะบด + ขนมขัดฟัน 7 ชิ้น ×2) → −฿199 · ฿1,334 (สุนัขโต แกะ 3 kg + แกะบด + ขนมขัดฟัน 28 ชิ้น) → −฿200 · ของเล่นสุนัขไม่นับ | coupon API + คำสั่งซื้อได้ส่วนลดเท่ากัน · test เดิมของคูปองยังผ่าน |

> PR-2/PR-3 ตัวเลขเป็น **คำนวณจากกฎ** (ค้นตะกร้าด้วยสคริปต์ `C:/t/work/a5/combos*.py`) ยังไม่ได้ implement/รัน — ผู้สร้างบทควรรันยืนยันก่อนใช้เป็นเฉลย

---

## 5. ข้อควรระวังสำหรับผู้สร้างบท

1. ใส่ BUG-01 **หลัง** ตัดสินใจเรื่อง BUG_MODE (บรรทัด `computeTotals(...)` ต่างกัน) แล้วรัน repro ยืนยันว่า ฿999 → ฿1,049
2. **ห้าม** ใส่คำใบ้ใน README/TEST-DATA ของบท 05 · TEST-DATA ยังเขียน "ฟรีเมื่อซื้อครบ ฿999" ตามเดิม (นี่คือ oracle [D] ที่ผู้เรียนต้องใช้)
3. `petshop/README.md` บท 05 ยังลิงก์ `../TEST-DATA.md` ที่ไม่มีในโฟลเดอร์บท 05 → ต้องคัดลอก TEST-DATA มา
4. suite บท 03 ต้องมี `TEST-PLAN.md` อยู่ `../` ของโฟลเดอร์ e2e ถึงจะรันได้ (fixtures `:193`)
5. บนเครื่องนี้ `next dev -p 3055` ใช้ไม่ได้ (Windows สงวนพอร์ต 2970–3169 → EACCES) · ให้ผู้เรียนรันผ่าน Docker พอร์ต 3000 ตามบท 03

---

## ภาคผนวก A — diff อ้างอิงของ CR-01 (prototype ที่รันผ่านแล้ว, ฐาน = โค้ดบท 05 ปัจจุบันที่ยังมี BUG_MODE)

<details><summary>เปิดดู diff (6 ไฟล์ +60/−9)</summary>

```diff
diff --git a/lib/pricing.ts b/lib/pricing.ts
@@ -32,6 +32,9 @@ export interface Totals {
   subtotal: number;
   discount: number;
   shipping: number;
+  /** Gift-wrap fee actually charged (0 when not selected or free). */
+  giftWrap: number;
+  giftWrapSelected: boolean;
   total: number;
   coupon: CouponResult | null;
 }
@@ -39,6 +42,8 @@
 export const FREE_SHIPPING_MIN = 999;
 export const STANDARD_SHIPPING = 50;
 export const EXPRESS_SHIPPING = 120;
+export const GIFT_WRAP_FEE = 30;
+export const GIFT_WRAP_FREE_MIN = 1500;
@@ -135,20 +140,29 @@ export function shippingCost(subtotal: number, method: ShippingMethod): number {
   return subtotal >= FREE_SHIPPING_MIN ? 0 : STANDARD_SHIPPING;
 }
 
+/** Gift wrap: ฿30 per order, free when the goods subtotal (before discount) is ≥ ฿1,500. */
+export function giftWrapCost(subtotal: number, selected: boolean): number {
+  if (!selected) return 0;
+  return subtotal >= GIFT_WRAP_FREE_MIN ? 0 : GIFT_WRAP_FEE;
+}
+
 export function computeTotals(opts: {
   lines: PricedLine[];
   couponCode?: string | null;
   shipping?: ShippingMethod;
   bugMode?: boolean;
+  giftWrap?: boolean;
 }): Totals {
-  const { lines, couponCode, shipping = "standard", bugMode = false } = opts;
+  const { lines, couponCode, shipping = "standard", bugMode = false, giftWrap = false } = opts;
   const subtotal = subtotalOf(lines);
   const coupon = couponCode ? evaluateCoupon(couponCode, lines, bugMode) : null;
   const discount = coupon?.ok ? Math.min(coupon.discount, subtotal) : 0;
   let ship = lines.length === 0 ? 0 : shippingCost(subtotal, shipping);
   if (coupon?.ok && coupon.freeShipping) ship = 0;
-  const total = Math.max(0, subtotal - discount + ship);
-  return { subtotal, discount, shipping: ship, total, coupon };
+  const wrapSelected = giftWrap && lines.length > 0;
+  const wrap = giftWrapCost(subtotal, wrapSelected);
+  const total = Math.max(0, subtotal - discount + ship + wrap);
+  return { subtotal, discount, shipping: ship, giftWrap: wrap, giftWrapSelected: wrapSelected, total, coupon };
 }
diff --git a/lib/store.ts b/lib/store.ts
@@ -36,6 +36,8 @@ export interface Order {
   subtotal: number;
   discount: number;
   shipping: number;
+  giftWrap: boolean;
+  giftWrapFee: number;
   total: number;
diff --git a/lib/orders.ts b/lib/orders.ts
@@ -14,6 +14,7 @@ export interface CreateOrderInput {
   shipping?: unknown;
   payment?: unknown;
   address?: unknown;
+  giftWrap?: unknown;
 }
@@ -52,7 +53,8 @@
   const couponCode = typeof input.coupon === "string" && input.coupon.trim() ? input.coupon : null;
-  const totals = computeTotals({ lines, couponCode, shipping, bugMode });
+  const giftWrap = input.giftWrap === true;
+  const totals = computeTotals({ lines, couponCode, shipping, bugMode, giftWrap });
@@ -70,6 +72,8 @@
     shipping: totals.shipping,
+    giftWrap: totals.giftWrapSelected,
+    giftWrapFee: totals.giftWrap,
     total: totals.total,
diff --git a/components/OrderSummary.tsx b/components/OrderSummary.tsx
-export function useCartTotals(shipping: ShippingMethod = "standard") {
+export function useCartTotals(shipping: ShippingMethod = "standard", giftWrap = false) {
   const { cart, coupon, bugMode } = useShop();
   const lines = useMemo(() => priceLines(cart), [cart]);
   const totals = useMemo(
-    () => computeTotals({ lines, couponCode: coupon, shipping, bugMode: bugMode || clientBugMode() }),
-    [lines, coupon, shipping, bugMode],
+    () => computeTotals({ lines, couponCode: coupon, shipping, bugMode: bugMode || clientBugMode(), giftWrap }),
+    [lines, coupon, shipping, bugMode, giftWrap],
   );
@@ -34,6 +34,14 @@ export function SummaryRows(...)
       </div>
+      {totals.giftWrapSelected ? (
+        <div>
+          <dt>ห่อของขวัญ</dt>
+          <dd data-testid="summary-giftwrap" className={totals.giftWrap === 0 ? "free" : ""}>
+            {totals.giftWrap === 0 ? "ฟรี" : formatBaht(totals.giftWrap)}
+          </dd>
+        </div>
+      ) : null}
       {children}
diff --git a/components/CheckoutForm.tsx b/components/CheckoutForm.tsx
   const [payment, setPayment] = useState<"cod" | "promptpay">("cod");
+  const [giftWrap, setGiftWrap] = useState(false);
-  const { lines, totals } = useCartTotals(shipping);
+  const { lines, totals } = useCartTotals(shipping, giftWrap);
-        body: JSON.stringify({ items: cart, coupon, shipping, payment, address: form }),
+        body: JSON.stringify({ items: cart, coupon, shipping, payment, address: form, giftWrap }),
@@ (ก่อน section "💳 วิธีชำระเงิน")
+          <section className="card-panel">
+            <h2>🎁 ห่อของขวัญ</h2>
+            <label className="check" htmlFor="gift-wrap">
+              <input
+                type="checkbox"
+                id="gift-wrap"
+                data-testid="gift-wrap"
+                checked={giftWrap}
+                onChange={(e) => setGiftWrap(e.target.checked)}
+              />
+              ห่อของขวัญ (+฿30 · ฟรีเมื่อซื้อครบ ฿1,500)
+            </label>
+          </section>
diff --git a/app/orders/[id]/page.tsx b/app/orders/[id]/page.tsx
@@ -116,6 +116,14 @@ (หลังแถวค่าจัดส่ง ก่อน summary-total-row)
+            {order.giftWrap ? (
+              <div>
+                <dt>ห่อของขวัญ</dt>
+                <dd data-testid="summary-giftwrap" className={order.giftWrapFee === 0 ? "free" : ""}>
+                  {order.giftWrapFee === 0 ? "ฟรี" : formatBaht(order.giftWrapFee)}
+                </dd>
+              </div>
+            ) : null}
```

</details>

## ภาคผนวก B — บันทึกการรัน (Chromium, Playwright 1.64, ใน docker network ภายใน)

| build | BUG_MODE | suite บท 03 (48) | test เพิ่มของ A5 | เวลา |
|---|---|---|---|---|
| ต้นฉบับบท 05 | 0 | 46 ผ่าน / 2 ล้ม (SRCH-01, CART-05) | — | 2.4 นาที |
| ต้นฉบับบท 05 | 1 | 41 / 7 (+WISH-01, COUP-01/02/03, CHK-03) | — | 5.3 นาที |
| + BUG-01 | 0 | 46 / 2 (เท่าเดิม) | A5-BUG01 ❌ (999/999/1,049) | 2.4 นาที |
| แก้ BUG-01 ที่ต้นเหตุ (= ต้นฉบับ) | 0 | 46 / 2 | A5-BUG01 ✅ | — |
| + CR-01 | 0 | 46 / 2 | A5-CR01 a/b/c ✅ 3/3 | 2.4 นาที |
| + CR-01 บนการแก้แบบ `>=` | 0 | (ไม่ได้รัน suite) | A5-BUG01 ✅ · A5-CR01 ❌ 2/3 (ค่าห่อหายในคำสั่งซื้อ) | — |

log: `C:/t/work/a5/test-{base,bugmode1,bug,bug-repro,fix-repro,cr01,cr01-ui,trap-ui}.log`
