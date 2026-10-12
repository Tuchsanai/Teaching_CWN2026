# 🗺️ CODEBASE-NOTES — PawPantry (มุมผู้รับช่วงระบบเดิม)

> งาน A5 · 2026-10-12 · อ่านจาก `05_rea-reverse-engineer-legacy-petshop/petshop/` (สำเนาจากบท 03 ตรงกันทุกไฟล์ ยกเว้น `node_modules`)
> เลขบรรทัดทุกจุดอ้างอิงไฟล์ในบท 05 **ก่อน**ใส่ BUG-01 (ดู `CR-DESIGN.md`) · ตัวเลขผลรันมาจากการรันจริงใน `C:/t/work/a5/` (ดูหัวข้อ 9)

---

## 1. ภาพรวมสถาปัตยกรรม

| ด้าน | ค่า |
|---|---|
| Stack | Next.js 16.4 (App Router, `output: "standalone"`) · React 19.3 · TypeScript · CSS ล้วน (`app/globals.css`) · ไม่มี DB |
| ขนาด | `app/` `components/` `lib/` รวม 8,852 บรรทัด (ในนั้น `globals.css` 3,698) · 11 หน้า (`page.tsx`) + `not-found` · 12 API route · 18 component · 10 ไฟล์ lib |
| รัน | Docker multi-stage (`node:24-alpine`, non-root, `HEALTHCHECK /api/health`) · compose: service/container `petshop` พอร์ต `3000:3000` env `ALLOW_TEST_RESET=1`, `BUG_MODE=${BUG_MODE:-0}` |
| ข้อมูลถาวร | **ไม่มี** — server เก็บใน RAM (`globalThis.__pawpantryStore`) หายเมื่อ restart · client เก็บใน `localStorage` |
| สัญญาสำคัญ | กฎราคาเป็น **pure function ชุดเดียว** (`lib/pricing.ts`) ใช้ทั้ง browser (แสดงยอด) และ server (คิดเงินจริง) |

```
Browser (client components)                       Server (Next.js route handlers / server components)
┌──────────────────────────────┐                   ┌──────────────────────────────────────────────┐
│ ShopProvider (React context) │  fetch JSON       │ app/api/*/route.ts  (thin: parse → lib → JSON)│
│  cart/wishlist/recent/coupon │ ───────────────▶  │ app/**/page.tsx     (server component อ่าน lib│
│  ↕ localStorage pp-*         │  cookie pp_session│                      ตรง ไม่ผ่าน API)          │
│ CartView / CheckoutForm ...  │                   │ lib/orders.ts  lib/auth.ts  lib/store.ts(RAM) │
│   └─ import lib/pricing.ts ◀─┼── โค้ดเดียวกัน ──▶│   └─ import lib/pricing.ts                    │
└──────────────────────────────┘                   └──────────────────────────────────────────────┘
```

**ข้อสังเกตแบบ legacy:** หน้า `/`, `/products`, `/products/[slug]`, `/account`, `/orders/[id]` เป็น server component เรียก `lib/` ตรง ๆ → `GET /api/products*` แทบไม่ได้ใช้ในหน้าเว็บ (ใช้แค่ `refreshStock()` หลังสั่งซื้อ `ShopProvider.tsx:263-274`) แต่ test/REA จะเห็นเป็น endpoint ปกติ

---

## 2. แผนที่ไฟล์สำคัญ

### 2.1 `lib/` (กฎธุรกิจทั้งหมดอยู่ที่นี่)

| ไฟล์ | หน้าที่ | ใช้ฝั่ง | จุดสำคัญ |
|---|---|---|---|
| `lib/products.ts` | ข้อมูลสินค้า 28 ชิ้น (seed) · label ภาษาไทย · `getProduct` `lowestPrice` `smallestSize` `seedStock` `withStock` | ทั้งคู่ | ราคา/สต็อกตั้งต้น `:74-558` · `isFood()` `:5-7` · review สร้างแบบ deterministic `:640-659` |
| `lib/pricing.ts` | **ราคา คูปอง ค่าส่ง ยอดรวม** | ทั้งคู่ | ดูหัวข้อ 3 |
| `lib/orders.ts` | สร้างคำสั่งซื้อ (server-only) | server | `createOrder()` `:19-83` |
| `lib/store.ts` | in-memory store: users, sessions, orders, stock · hash รหัสผ่าน | server | `db()` `:96-99` · `resetStore()` `:101-103` |
| `lib/auth.ts` | cookie `pp_session` (httpOnly, lax, 7 วัน) | server | `currentUser()` `:8-11` · `attachSession()` `:18-27` |
| `lib/validation.ts` | ข้อความ error · ตรวจฟอร์มสมัคร/ที่อยู่ · รายชื่อ 10 จังหวัด | ทั้งคู่ | `MSG` `:3-15` · `validateShipping()` `:86-93` |
| `lib/catalog.ts` | parse query `/products` · กรอง · เรียง · ค้นหา (ชื่อ/ชื่ออังกฤษ/โปรตีน) | ทั้งคู่ | `matchesSearch()` `:51-58` (ค้นโปรตีนด้วย → ต้นเหตุ TC-SRCH-01) |
| `lib/finder.ts` | อัลกอริทึม Pet Food Finder | server+client | `recommend()` `:23-49` คะแนน 50+20+rating×6 สูงสุด 99 |
| `lib/bugmode.ts` | อ่าน `BUG_MODE` | ทั้งคู่ | ดูหัวข้อ 5 |
| `lib/fx.ts` | เอฟเฟกต์ลอยเข้าตะกร้า | client | ไม่มีกฎธุรกิจ |

### 2.2 API (`app/api/**/route.ts`) — ทุกตัว `dynamic = "force-dynamic"`

| method · path | ไฟล์ | ทำอะไร / สถานะ |
|---|---|---|
| GET `/api/health` | `health/route.ts` | `{ok:true}` |
| GET `/api/products` · `/api/products/[slug]` | `products/route.ts` · `products/[slug]/route.ts` | สต็อกสด · 404 `{error:"ไม่พบสินค้า"}` |
| GET `/api/recommendations` | `recommendations/route.ts` | 400 ถ้าไม่มี `pet` |
| POST `/api/coupons/validate` | `coupons/validate/route.ts` | `evaluateCoupon(code, priceLines(items), serverBugMode())` `:16` |
| POST `/api/auth/register` · `login` · `logout` · GET `me` | `auth/*/route.ts` | 400/409/401 ตาม SPEC · ตั้ง/ลบ cookie |
| GET/POST `/api/orders` | `orders/route.ts` | 401 ถ้าไม่ login · POST → `createOrder(user, body, serverBugMode())` `:25` → 201 `{order,id}` |
| GET `/api/orders/[id]` | `orders/[id]/route.ts` | ของตัวเองเท่านั้น (404) |
| POST `/api/test/reset` | `test/reset/route.ts` | ดูหัวข้อ 6 |

### 2.3 หน้า + component

| หน้า | ไฟล์หน้า | component หลัก | ข้อมูลมาจาก |
|---|---|---|---|
| `/` | `app/page.tsx` | `HomePersonal` | `liveProducts()` (server) + `pp-recent`/wishlist (client) |
| `/products` | `app/products/page.tsx` | `CatalogFilters`, `ProductCard` | `filterProducts(parseCatalogQuery(...), liveProducts())` |
| `/products/[slug]` | `app/products/[slug]/page.tsx` | `ProductDetail` | `liveProducts()` |
| `/cart` | `app/cart/page.tsx` | `CartView` + `OrderSummary` | localStorage + `lib/pricing` (client) + `/api/coupons/validate` |
| `/checkout` | `app/checkout/page.tsx` (redirect ถ้าไม่ login) | `CheckoutForm` + `OrderSummary` | client คำนวณแสดง → POST `/api/orders` (server คำนวณใหม่) |
| `/orders/[id]` | `app/orders/[id]/page.tsx` | (เขียน summary เอง `:104-122` **ไม่ได้ใช้ `SummaryRows`**) | `findOrder()` |
| `/account` | `app/account/page.tsx` | — | `ordersFor()` · ยอดสะสม `:23` |
| `/wishlist` `/finder` `/login` `/register` | `app/*/page.tsx` | `WishlistView` `FinderWizard` `LoginForm` `RegisterForm` | — · login กัน open-redirect ด้วย `safeNext()` `app/login/page.tsx:7-10` |
| layout | `app/layout.tsx` | `Header` `Footer` `Toaster` `ShopProvider` | อ่าน BUG_MODE, user, stock ต่อ request `:36-44` |

---

## 3. กฎธุรกิจอยู่ที่ไหน

| กฎ | ที่อยู่หลัก (single source) | ที่ "ก๊อปไว้" อีก (จุดเสี่ยงตอนแก้) |
|---|---|---|
| ราคาต่อบรรทัด · ทิ้งสินค้า/ขนาดที่ไม่มี · qty ≤ 0 | `lib/pricing.ts:57-78` `priceLines()` (server ไม่เชื่อราคาจาก client) | — |
| PAW10 10% ปัดลง | `lib/pricing.ts:114-117` | ข้อความโปรโมชัน `app/page.tsx:72` |
| FREESHIP | `lib/pricing.ts:118-119` + `:149` | — |
| NEWCAT50 (อาหารแมว ≥ ฿500 · ไม่นับของเล่น/ของใช้) | `lib/pricing.ts:120-125` | ข้อความ `COUPON_MESSAGES.catMin` `:46` |
| SUMMER20 หมดอายุ / โค้ดไม่รู้จัก | `lib/pricing.ts:126-129` | — |
| คูปอง: ตัวพิมพ์เล็ก/ช่องว่าง | `normalizeCode()` `:84-86` | `CartView.tsx:172` เก็บโค้ดแบบ normalize |
| ค่าส่ง: ธรรมดา ฿50 ฟรีเมื่อ **ยอดก่อนหักส่วนลด** ≥ ฿999 · ด่วน ฿120 เสมอ | `lib/pricing.ts:39-41` ค่าคงที่ · `shippingCost()` `:133-136` | ⚠️ ฮาร์ดโค้ด: `CheckoutForm.tsx:217` (`>= 999`, "฿50"), `:230` ("฿120"), `CartView.tsx:278`, `ProductDetail.tsx:250-251`, `Footer.tsx:70`, `app/page.tsx:84,104` |
| แถบ "ซื้อเพิ่มอีก ฿N" | `freeShippingRemaining()` `lib/pricing.ts:154-156` | `CartView.tsx:111-133` |
| ยอดรวม = subtotal − discount + ship (≥ 0) · ส่วนลด ≤ subtotal | `computeTotals()` `lib/pricing.ts:138-152` | ⚠️ หน้า `/orders/[id]` แสดงจาก `order.*` ที่ server เก็บไว้ ไม่ได้คำนวณใหม่ |
| สต็อก: ต่อสินค้า (ทุกขนาดใช้ร่วม) | server: `lib/orders.ts:42-50` เช็ก → 409 `สินค้าไม่พอ: <ชื่อ>` · `:57` ตัดสต็อก | client: `ShopProvider.tsx:181-212` จำกัด qty ด้วยสต็อกรวมทุกขนาด · `ProductDetail.tsx:62` clamp · `ProductCard.tsx:58-71` toast (**บั๊กเดิม P3**: เพิ่มได้ไม่ครบก็ยังบอกว่าเพิ่มแล้ว → TC-CART-05) |
| ฟอร์มที่อยู่: ชื่อ · เบอร์ `^0\d{9}$` · ที่อยู่ ≥ 10 · รหัสไปรษณีย์ 5 หลัก | `lib/validation.ts:81-93` | client `CheckoutForm.tsx:69` + server `lib/orders.ts:34` เรียกฟังก์ชันเดียวกัน · จังหวัดที่ไม่รู้จัก → server แก้เป็น `กรุงเทพมหานคร` เงียบ ๆ `orders.ts:38-40` |
| สมัคร: รหัส ≥ 8 + มีตัวเลข · อีเมลซ้ำไม่สนตัวพิมพ์ | `lib/validation.ts:46-58` · `lib/store.ts:109-112` (lowercase) | ความแข็งรหัส `passwordStrength()` `:62-69` (แสดงผลเท่านั้น) |
| Auth: scrypt + salt · session = token สุ่ม 24 byte ใน `Map` | `lib/store.ts:57-69, 127-142` · cookie `lib/auth.ts:6, 18-27` | ไม่มีหมดอายุฝั่ง server (หายเมื่อ reset/restart) |
| สิทธิ์ดูคำสั่งซื้อ | `findOrder(userId, id)` `lib/orders.ts:92-94` | หน้า `app/orders/[id]/page.tsx:17-20` ใช้ตัวเดียวกัน |
| เลขคำสั่งซื้อ `PP-100001…` | `lib/store.ts:153-155` | reset แล้วนับใหม่ |

> **ข้อสรุปสำหรับ Change Request:** แก้ "ตัวเลข" ที่ `lib/pricing.ts` แล้ว server+client ตามพร้อมกัน **แต่ข้อความบนจอ 7 จุดไม่ตาม** และหน้า `/orders/[id]` มี summary ของตัวเอง → ต้องทำ impact analysis ทุกครั้ง

---

## 4. state อยู่ที่ไหน

| state | ที่เก็บ | key / ตัวแปร | อายุ | reset ด้วย `/api/test/reset`? |
|---|---|---|---|---|
| ผู้ใช้ (seed `demo@pawpantry.test` / `Paw12345`) | server RAM | `store.users` (`lib/store.ts:74-92`) | ถึง restart | ✅ |
| session | server RAM + cookie httpOnly | `store.sessions` (Map) · cookie `pp_session` | cookie 7 วัน แต่ Map หายเมื่อ reset | ✅ (cookie เดิมใช้ไม่ได้แล้ว) |
| คำสั่งซื้อ | server RAM | `store.orders` · `nextOrderNo` | ถึง restart | ✅ |
| สต็อกสด | server RAM | `store.stock` (seed จาก `products.ts`) | ถึง restart | ✅ |
| ตะกร้า | browser localStorage | `pp-cart` `[{slug,size,qty}]` (`ShopProvider.tsx:60`) | ถาวรในเบราว์เซอร์ | ❌ |
| รายการโปรด | localStorage | `pp-wishlist` `[slug]` `:61` | ″ | ❌ |
| ดูล่าสุด (6) | localStorage | `pp-recent` `:62` | ″ | ❌ |
| คูปองที่ใช้อยู่ | localStorage | `pp-coupon` (string) `:63` · ล้างหลังสั่งซื้อ `CheckoutForm.tsx:93` | ″ | ❌ |
| ตัวเลข ♥ บนหัวเว็บ | React state แยก | `wishlistBadge` `ShopProvider.tsx:119` (ไม่ได้คำนวณจาก `wishlist.length`! → ช่องให้ BUG_MODE ทำบั๊ก) | ต่อหน้า | — |
| สต็อกฝั่ง client | React state + ref | `stockMap`/`stockRef` (ค่าตั้งต้นจาก layout) | ต่อหน้า | — |
| สัญญาณพร้อมทดสอบ | DOM | `<html data-ready="true">` `ShopProvider.tsx:156-158` (หลังโหลด localStorage) | — | — |

ข้อมูลใน localStorage ถูก sanitize ตอนโหลด (`sanitizeCart` `:82-95` ทิ้งสินค้า/ขนาดที่ไม่มี, qty < 1) และ server คำนวณราคาใหม่เสมอ → แก้ `price` ใน `pp-cart` ไม่มีผล (TC-SEC-03)

---

## 5. ทุกจุดที่ `BUG_MODE` เปลี่ยนพฤติกรรม

กลไก: server อ่าน `process.env.BUG_MODE === "1"` ต่อ request (`lib/bugmode.ts:6-8`) → ส่งให้ client 2 ทาง: attribute `<html data-bug-mode>` (`app/layout.tsx:42`) และ prop `bugMode` ของ `ShopProvider` (`app/layout.tsx:44`) · `isBugMode()` (`lib/bugmode.ts:16-18`) **ไม่มีใครเรียก** (dead code)

| # | บั๊กฝึก | จุดที่ "ทำให้พัง" จริง | เส้นทางที่ส่งค่า bugMode ไปถึง | ผลเมื่อ `BUG_MODE=1` |
|---|---|---|---|---|
| 1 | PAW10 ลด 1% | **`lib/pricing.ts:115`** `const percent = bugMode ? 1 : 10;` | server: `coupons/validate/route.ts:16` · `orders/route.ts:25` → `lib/orders.ts:19,55` → `pricing.ts:142-146` · client: `OrderSummary.tsx:9-13` (`bugMode \|\| clientBugMode()`) · `CartView.tsx:137,168` (fallback ตอน fetch ล้ม) | ฿590 → −฿5 · ฿1,590 → −฿15 · ฿799 → −฿7 (BUG-HUNT บท 03) |
| 2 | ♥ ไม่ลดหลังลบ | **`components/ShopProvider.tsx:225`** `if (!bugMode) setWishlistBadge(...)` และ **`:238`** `bugMode ? b + 1 : next.length` | prop `bugMode` `ShopProvider.tsx:108-113` · ใช้ใน `removeFromWishlist` (`:221-228`, ถูกเรียกจาก ♥ toggle, ปุ่มลบ, ปุ่มย้ายไปตะกร้า) | ♥ ค้างจนรีโหลด |
| 3 | เบอร์ 9 หลักผ่าน | **`lib/validation.ts:82`** `bugMode ? /^0\d{8,9}$/ : /^0\d{9}$/` | client `CheckoutForm.tsx:5,43,69` · server `lib/orders.ts:34` | สั่งซื้อด้วย `081234567` สำเร็จ |
| — | ส่งต่อค่าอย่างเดียว (ไม่เปลี่ยนพฤติกรรมเอง) | `app/layout.tsx:16,37,42,44` · `ShopProvider.tsx:27,288,314` · `lib/pricing.ts:94,142,144,146` · `lib/validation.ts:81,86,89` · `docker-compose.yml` env | | |

รวม: **3 จุดเปลี่ยนพฤติกรรม** (pricing.ts:115, ShopProvider.tsx:225+238, validation.ts:82) · **11 ไฟล์**มีคำว่า bugMode · ผลรันจริงบนสำเนาบท 05: BUG_MODE=0 ผ่าน 46/48, BUG_MODE=1 ผ่าน 41/48 (ล้มเพิ่ม WISH-01, COUP-01/02/03, CHK-03 ตรงกับ BUG-HUNT บท 03)

> ⚠️ ผลต่อบท 05: `grep -rn bugMode` เจอทั้ง 3 บั๊กใน 10 วินาที → ถ้าเก็บ BUG_MODE ไว้ "ระบบเดิม" จะดูไม่สมจริง (ดูข้อเสนอใน `CR-DESIGN.md` หัวข้อ 3)

---

## 6. Test hooks

| hook | ที่อยู่ | พฤติกรรม |
|---|---|---|
| `POST /api/test/reset` | `app/api/test/reset/route.ts:7-13` | ถ้า `ALLOW_TEST_RESET !== "1"` → 404 `{error:"Not found"}` · ไม่งั้น `resetStore()` = seed ใหม่ (users/sessions/orders/stock/เลขคำสั่งซื้อ) · **ไม่ล้าง localStorage** |
| `GET /api/health` | `app/api/health/route.ts` | ใช้ใน Docker HEALTHCHECK และ `global-setup.ts` |
| `<html data-ready="true">` | `ShopProvider.tsx:156-158` | test รอก่อนกด (`fixtures.ts` `open()`) |
| `<html data-bug-mode>` | `app/layout.tsx:42` | บอกโหมดบั๊ก (มองเห็นจาก DOM/HTML/bundle → REA ก็เห็น) |
| `data-testid` | ทุก component ตาม `03/_solution/_design/SPEC-reference.md` | ห้ามเปลี่ยนชื่อ — test บท 03 ผูกอยู่ |
| ข้อมูล deterministic | review/วันที่/QR สร้างจากสูตร (`products.ts:640-659`, `CheckoutForm.tsx:20-40`) | ไม่มีค่าสุ่มบนจอ ยกเว้นเลขคำสั่งซื้อ (เรียงหลัง reset) |

---

## 7. เทสต์ที่มีอยู่แล้ว (บท 03 `_solution/e2e`)

| หัวข้อ | ค่า |
|---|---|
| โครง | `playwright.config.ts` (3 projects: chromium อัด slowMo 300 + วิดีโอ, firefox, webkit · `workers: 1` เพราะ reset เป็น state ร่วม · `BASE_URL` ปรับได้) · `global-setup.ts` (health + reset) · `tests/fixtures.ts` (reset ก่อนทุก test, helper `addToCart` `login` `fillAddress` `checkSummary` `toCheckout` `placeOrder`, อ่าน priority จาก `../TEST-PLAN.md`) · `reporters/html-report.ts` (รายงานไทย + GIF) |
| จำนวน | 48 test ใน 10 ไฟล์ = TC ใน `TEST-PLAN.md` หัวข้อ 5 (P1 30 · P2 13 · P3 5) |
| ครอบคลุมราคา | CART-01..06 · COUP-01..10 · SHIP-01..04 · CHK-01/06/07 · ACC-01 · SEC-03 |
| ผลบนสำเนาบท 05 (Chromium, ไม่ slowMo) | BUG_MODE=0: **46 ผ่าน / 2 ล้ม** (SRCH-01 = แผนตีความแคบ, CART-05 = บั๊กเดิม P3) 2.4 นาที · BUG_MODE=1: **41 / 7** 5.3 นาที |
| **จุดบอดที่สำคัญ** | `TC-SHIP-02` (฿999 พอดี) ตรวจ **แค่หน้าตะกร้า** ไม่ได้สั่งซื้อ · ไม่มี test ไหนตรวจยอดใน **คำสั่งซื้อจริง/API** ที่ ฿999 → BUG-01 ที่เสนอใน `CR-DESIGN.md` ผ่าน suite นี้ครบ 46/48 เท่าเดิม (รันจริงแล้ว) |
| ใช้ซ้ำในบท 05 ได้ | ✅ เป็น regression/characterization suite ได้ทันที: ตั้ง `BASE_URL` แล้วต้องมี `TEST-PLAN.md` อยู่ที่ `../` หรือ `../../` ของโฟลเดอร์ e2e (fixtures `:193` หาไฟล์นี้ ไม่เจอจะ throw "No tests found") |

---

## 8. สิ่งที่ผู้รับช่วงควรรู้ (ข้อเท็จจริงจากโค้ด ไม่ใช่ความเห็น)

1. ไม่มี unit test, ไม่มี CI, ไม่มี git history ในบท 05 → ความรู้เดียวคือโค้ด + SPEC บท 03 + suite บท 03
2. `petshop/README.md` ในบท 05 ยังเป็นข้อความบท 03 และลิงก์ `../TEST-DATA.md` ซึ่ง **ไม่มี** ในโฟลเดอร์บท 05 → ผู้สร้างบทต้องคัดลอก/แก้
3. ส่งฟรีดูยอด **ก่อน** หักส่วนลด (`computeTotals` ส่ง `subtotal` เข้า `shippingCost`) → ฿999 + PAW10 = ยอดชำระ ฿900 ส่งฟรี (รันจริง)
4. Next dev บน Windows: พอร์ต 2970–3169 ถูก Windows สงวนไว้ (Hyper-V) บนเครื่องนี้ → `next dev -p 3055` ได้ `EACCES` · บท 05 ควรให้ผู้เรียนใช้ Docker พอร์ต 3000 ตามเดิม

---

## 9. วิธีที่ได้ตัวเลขในเอกสารนี้

- คัดลอก `petshop/` → `C:/t/work/a5/petshop` (git ภายในโฟลเดอร์งานเท่านั้น) · `e2e/` บท 03 → `C:/t/work/a5/e2e` + `a5.config.ts` (chromium อย่างเดียว ไม่ slowMo)
- `next dev -p 3055` บน host ใช้ไม่ได้ (EACCES ตามข้อ 8.4) → build image จาก `Dockerfile` ของ petshop รันใน docker network ภายใน (`PORT=3055` ใน container, **ไม่ publish พอร์ตบน host**) แล้วรัน Playwright 1.64 (`mcr.microsoft.com/playwright:v1.64.0-noble`) ใน network เดียวกัน · ปิด container/network/image ของงานนี้แล้ว
- log: `C:/t/work/a5/test-*.log` · probe API: `C:/t/work/a5/probe/`
