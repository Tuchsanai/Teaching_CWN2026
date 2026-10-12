# CODEBASE-MAP · PawPantry (ระบบเดิมที่รับช่วงมา)

> ทำแผนที่เมื่อ: **2026-10-12** · จาก commit `e872ff8` · วิธี: Explore subagent อ่าน `petshop/` `e2e-legacy/` + เปิดไฟล์ยืนยันเองทีละจุด (white-box ล้วน ยังไม่ได้รันระบบ)
> path ทั้งหมดนับจาก `petshop/` เว้นแต่ขึ้นต้น `e2e-legacy/` หรือ `TEST-DATA.md` · "เดา" = อนุมานจากชื่อ/โครงสร้าง ไม่ได้เปิดยืนยันบรรทัดนั้น

## A · ภาพรวม

| เรื่อง | รายละเอียด | ยืนยันจาก |
|---|---|---|
| stack | Next.js 16.4.0 (App Router) · React 19.3.0 · TypeScript · `output: "standalone"` | `package.json:16-18` · `next.config.ts:4-6` |
| รันยังไง | `docker compose up -d --build` ใน `petshop/` → project/container `pawpantry05` · host `4000` → container `3000` (`WEB_PORT` เปลี่ยนได้) · env `ALLOW_TEST_RESET=1` | `docker-compose.yml:1,6,8,10` |
| image | 3 stage บน `node:24-alpine` · รัน `node server.js` เป็น user `nextjs` · HEALTHCHECK `GET /api/health` | `Dockerfile:4,10,18,25,35-38` |
| ข้อมูลฝั่ง server | ไม่มีฐานข้อมูล · อยู่ใน RAM ที่ `globalThis.__pawpantryStore` = `{users, sessions, orders, stock, nextUserId, nextOrderNo}` · รีสตาร์ต container = กลับ seed | `lib/store.ts:48-55,94-99` |
| seed | ผู้ใช้ 1 คน (demo "สมใจ ใจดี") · ไม่มีออเดอร์ · สต็อกจาก `seedStock()` · เลขออเดอร์เริ่ม `PP-100001` | `lib/store.ts:74-92,153-155` |
| สินค้า | 28 รายการ hard-code ในโค้ด · สต็อกนับต่อสินค้า (ทุกขนาดใช้ร่วมกัน) | `lib/products.ts:74-558,33` |
| session | cookie httpOnly `pp_session` (SameSite lax · 7 วัน) → `sessions` Map ใน RAM | `lib/auth.ts:6,18-26` |
| ข้อมูลฝั่ง browser | localStorage `pp-cart` `pp-wishlist` `pp-recent` `pp-coupon` · ตั้ง `html[data-ready="true"]` หลังโหลดจาก storage | `components/ShopProvider.tsx:59-62,153-155` |
| middleware | ไม่มี `middleware.ts` / `proxy.ts` | ค้นทั้งโฟลเดอร์ (Explore) |

## B · หน้าเว็บ (11 หน้า + not-found)

`app/layout.tsx` เป็น force-dynamic อ่าน `currentPublicUser()` + `liveStock()` บน server แล้วส่งให้ `ShopProvider` (`app/layout.tsx:19,36-37`)

| URL | ไฟล์ | component หลัก | ข้อมูลมาจากไหน | ยืนยันจาก |
|---|---|---|---|---|
| `/` | `app/page.tsx` | `ProductGrid` · `HomePersonal` | server import `liveProducts()` · `HomePersonal` ใช้ `PRODUCTS` (static) + stock จาก provider + localStorage `pp-recent`/`pp-wishlist` | `app/page.tsx:19` · `components/HomePersonal.tsx:31` |
| `/products` | `app/products/page.tsx` | `CatalogFilters` · `ProductGrid` | server `filterProducts(query, liveProducts())` · ตัวกรองอยู่ใน URL | `app/products/page.tsx:13` |
| `/products/[slug]` | `app/products/[slug]/page.tsx` | `ProductDetail` | server `liveProducts()` · ไม่พบ → `notFound()` | `app/products/[slug]/page.tsx:17,19` |
| `/cart` | `app/cart/page.tsx` | `CartView` · `FreeShippingProgress` | client ล้วน: localStorage + ราคา static (`priceLines`) · ใส่คูปอง → `POST /api/coupons/validate` ถ้า fetch พังคำนวณเองใน browser | `components/CartView.tsx:161,168` |
| `/checkout` | `app/checkout/page.tsx` | `CheckoutForm` | ต้อง login (ไม่ login → `/login?next=/checkout`) · สั่งซื้อ `POST /api/orders` แล้ว `refreshStock()` (`GET /api/products`) | `app/checkout/page.tsx:9-10` · `components/CheckoutForm.tsx:73` · `ShopProvider.tsx:262` |
| `/orders/[id]` | `app/orders/[id]/page.tsx` | `Confetti` + สรุปเงิน | server `currentUser()` + `findOrder()` · แสดงค่า **ที่เก็บในออเดอร์** ไม่คำนวณใหม่ | `app/orders/[id]/page.tsx:17-20,107-121` |
| `/account` | `app/account/page.tsx` | โปรไฟล์ · ประวัติออเดอร์ | server `ordersFor()` · คำนวณเองแค่ `totalSpent = Σ order.total` | `app/account/page.tsx:18-23` |
| `/login` | `app/login/page.tsx` | `LoginForm` | `POST /api/auth/login` · `next` รับแค่ path ขึ้นต้น `/` | `app/login/page.tsx:7-10` · `components/LoginForm.tsx:23` |
| `/register` | `app/register/page.tsx` | `RegisterForm` | `POST /api/auth/register` → ไป `/account?welcome=1` เสมอ (ไม่สน `?next`) | `components/RegisterForm.tsx:36,50` |
| `/wishlist` | `app/wishlist/page.tsx` | `WishlistView` | client ล้วน: localStorage + `PRODUCTS` static | `components/WishlistView.tsx:80` (Explore) |
| `/finder` | `app/finder/page.tsx` | `FinderWizard` | `GET /api/recommendations?...` | `components/FinderWizard.tsx:95` (Explore) |
| 404 | `app/not-found.tsx` | – | static | เปิดดู (Explore) |

## C · API (12 route · ทั้งหมด `force-dynamic`)

login ตรวจด้วย `currentUser()` = หา cookie `pp_session` ใน `db().sessions` (`lib/auth.ts:8-11` · `lib/store.ts:137-142`)

| method | path | ไฟล์ (`app/api/…`) | ทำอะไร | login? | ยืนยันจาก |
|---|---|---|---|---|---|
| POST | `/api/auth/login` | `auth/login/route.ts` | ตรวจอีเมล (ไม่สนตัวพิมพ์) + รหัส · 401 หรือ set cookie | ไม่ | `:18-22` |
| POST | `/api/auth/logout` | `auth/logout/route.ts` | ลบ session + ล้าง cookie | ไม่ | `:10-12` |
| GET | `/api/auth/me` | `auth/me/route.ts` | `{user \| null}` · **UI ไม่เรียก** | ไม่ | `:7` |
| POST | `/api/auth/register` | `auth/register/route.ts` | `validateRegister` → 400 · อีเมลซ้ำ 409 · สำเร็จ 201 + cookie | ไม่ | `:19-32` |
| POST | `/api/coupons/validate` | `coupons/validate/route.ts` | `evaluateCoupon(code, priceLines(items))` | ไม่ | `:15-22` |
| GET | `/api/health` | `health/route.ts` | `{ok:true}` (Docker + global-setup ใช้) | ไม่ | Explore |
| GET | `/api/orders` | `orders/route.ts` | ออเดอร์ของผู้ใช้ ใหม่สุดก่อน · **UI ไม่เรียก** | ใช่ (401) | `:9-13` |
| POST | `/api/orders` | `orders/route.ts` → `lib/orders.ts createOrder` | ตรวจที่อยู่ · ตรวจสต็อก · คำนวณยอด · ตัดสต็อก · 201 / 400 / 409 | ใช่ (401) | `:15-27` · `lib/orders.ts:26-69` |
| GET | `/api/orders/[id]` | `orders/[id]/route.ts` | เฉพาะออเดอร์ตัวเอง ไม่ใช่ → 404 · **UI ไม่เรียก** | ใช่ (401) | `:11-12` |
| GET | `/api/products` | `products/route.ts` | `filterProducts(...)` → `{items,total}` (pet type life grainFree q sort) | ไม่ | Explore |
| GET | `/api/products/[slug]` | `products/[slug]/route.ts` | สินค้า + สต็อกจริง · 404 · **UI ไม่เรียก** | ไม่ | Explore |
| GET | `/api/recommendations` | `recommendations/route.ts` | ไม่มี `pet` → 400 · `recommend()` | ไม่ | `:9` |
| POST | `/api/test/reset` | `test/reset/route.ts` | ถ้า `ALLOW_TEST_RESET==="1"` → `resetStore()` ไม่งั้น 404 · **ไม่มี auth** | ไม่ | `:8-11` |

## D · กฎธุรกิจ

| กฎ | ไฟล์:บรรทัด (ต้นฉบับ) | ถูกใช้ / ถูกเขียนซ้ำที่ไหนอีก | ยืนยันจาก |
|---|---|---|---|
| ค่าคงที่ `FREE_SHIPPING_MIN=999` `STANDARD_SHIPPING=50` `EXPRESS_SHIPPING=120` | `lib/pricing.ts:39-41` | import ใน `lib/orders.ts:4-5` · `CartView.tsx:111-118` (แถบ progress) | เปิดดู |
| ค่าส่งปกติ: `subtotal >= 999 ? 0 : 50` · ด่วน 120 เสมอ | `lib/pricing.ts:130-133` | **server เขียนกฎซ้ำ** `lib/orders.ts:63-67` ใช้ `subtotal > FREE_SHIPPING_MIN` (คอมเมนต์ `PP-231: server must not trust the shipping fee shown in the browser — recompute it here.`) · **browser เขียนซ้ำแบบเลขตรง** `CheckoutForm.tsx:216` `totals.subtotal >= 999 ? "ฟรี" : "฿50"` (ไม่สน FREESHIP) · ข้อความบนจอ: `CheckoutForm.tsx:216,229` · `CartView.tsx:278` · `ProductDetail.tsx:250-251` · `app/page.tsx:84,104` · `Footer.tsx:69` | เปิดดูทุกจุด |
| ยอดรวม: ส่วนลดไม่เกิน subtotal · ตะกร้าว่างค่าส่ง 0 · FREESHIP ทำค่าส่ง = 0 (รวมส่งด่วน) · `total = max(0, subtotal − discount + ship)` | `lib/pricing.ts:135-148` | browser: `useCartTotals` (`OrderSummary.tsx:7-15`) · server: `lib/orders.ts:62` แล้วถูกแก้ทับที่ `:63-67` · หน้า `/orders/[id]` แสดงค่าที่เก็บ (`:107-121`) · `/account` รวม `o.total` (`:23`) · หน้า cart คิดแบบ `"standard"` เสมอ (`CartView.tsx:139` Explore) | เปิดดู |
| รหัสคูปอง trim + ตัวพิมพ์ใหญ่ | `lib/pricing.ts:84-86` | ทุกที่ใช้ `evaluateCoupon` ตัวเดียว | เปิดดู |
| PAW10 = `floor(subtotal × 10%)` ไม่มีขั้นต่ำ ไม่ต้อง login | `lib/pricing.ts:113-114` | ข้อความ: `app/page.tsx:72` ("ทุกออเดอร์") · `:218-226` ("สำหรับสมาชิกใหม่") · `ProductDetail.tsx:252` · `CartView.tsx:244` | เปิดดู |
| FREESHIP = ส่วนลด 0 + ส่งฟรี | `lib/pricing.ts:115-116,145` | server ข้ามบล็อก PP-231 เมื่อ freeShipping (`orders.ts:64`) | เปิดดู |
| NEWCAT50 = ลด ฿50 เมื่ออาหารแมว (dry/wet/treat) ≥ ฿500 · ของเล่น/อุปกรณ์แมวไม่นับ | `lib/pricing.ts:117-121` | ข้อความ error `pricing.ts:46` | เปิดดู |
| SUMMER20 = ล้มเสมอ "คูปองนี้หมดอายุแล้ว" | `lib/pricing.ts:123-124` | – | เปิดดู |
| คูปองถูกประเมิน 3 ที่ | `evaluateCoupon` ตัวเดียว | browser (`computeTotals`) · `/api/coupons/validate` · `createOrder` (`orders.ts:61-62`) · ถ้า fetch validate พัง browser ประเมินเอง (`CartView.tsx:167-168`) | เปิดดู |
| ราคาบรรทัด = ราคาขนาด × qty (ตัดบรรทัดที่ slug/size ไม่รู้จัก หรือ qty ≤ 0) | `lib/pricing.ts:57-78` | ราคา bundle หน้าสินค้า `ProductDetail.tsx:73-75` (แสดงผลอย่างเดียว) | Explore |
| สต็อก (server): รวม qty ต่อ slug ทุกขนาด > สต็อก → 409 "สินค้าไม่พอ" แล้วตัดสต็อก | `lib/orders.ts:49-57,69` | browser จำกัดตอนเพิ่มลงตะกร้า `ShopProvider.tsx:178-209` · หน้าสินค้า `ProductDetail.tsx:62,237` · `sanitizeCart` ไม่ clamp สต็อก (`:81-94`) | `orders.ts` เปิดดู · ที่เหลือ Explore |
| ฟอร์มสมัคร: ชื่อไม่ว่าง · อีเมล regex · รหัส ≥ 8 ตัวและมีตัวเลข · ยืนยันตรง · ติ๊กเงื่อนไข | `lib/validation.ts:40-58` | ใช้ทั้ง `RegisterForm` (browser) และ `auth/register/route.ts` · อีเมลซ้ำตรวจที่ server | Explore |
| ฟอร์มที่อยู่: ชื่อ · โทร `^0\d{9}$` · ที่อยู่ ≥ 10 ตัว · ไปรษณีย์ 5 หลัก · จังหวัดไม่อยู่ในรายการ → แทนด้วย "กรุงเทพมหานคร" เงียบ ๆ | `lib/validation.ts:81-93` · `lib/orders.ts:41-47` | `CheckoutForm` (browser) + `createOrder` (server) | `orders.ts` เปิดดู · validation Explore |
| วิธีส่ง/จ่ายที่ server: ไม่ใช่ `express` = `standard` · ไม่ใช่ `promptpay` = `cod` | `lib/orders.ts:59-60` | – | เปิดดู |

## E · state

| อะไร | เก็บที่ไหน | key / ตัวแปร | `/api/test/reset` ล้างได้ไหม | ยืนยันจาก |
|---|---|---|---|---|
| ผู้ใช้ | RAM server | `__pawpantryStore.users` | ✅ เหลือ demo | `lib/store.ts:101-103` |
| session | RAM server | `__pawpantryStore.sessions` | ✅ (cookie เดิมใช้ไม่ได้) | `lib/store.ts:101-103` |
| ออเดอร์ + เลขรัน | RAM server | `.orders` · `.nextOrderNo` | ✅ เลขกลับไป `PP-100001` | `lib/store.ts:74-92` |
| สต็อก | RAM server | `.stock` | ✅ | `lib/store.ts:74-92` |
| hash รหัส demo | ตัวแปร module | `demoHash` | ❌ (ตั้งใจ cache · ค่าเดิม) | `lib/store.ts:71-72` (Explore) |
| cookie login | browser | `pp_session` | ❌ อยู่ต่อแต่ใช้ไม่ได้ | `lib/auth.ts:6` |
| ตะกร้า · โปรด · ดูล่าสุด · คูปอง | browser localStorage | `pp-cart` `pp-wishlist` `pp-recent` `pp-coupon` | ❌ | `ShopProvider.tsx:59-62` |
| user/stock/toast ใน React | state ของ `ShopProvider` | – | ❌ จนกว่าจะ reload | Explore |

## F · ชุดเทสต์เดิม `e2e-legacy/`

- 10 ไฟล์ 40 test (`grep -c "test("` = 2+6+4+3+4+3+6+4+4+4) · `tests/new/` มีแค่ `.gitkeep`
- `playwright.config.ts`: baseURL `http://localhost:4000` (`:22`) · workers 4 · retries 0 · ค่าเริ่มต้น chromium เท่านั้น เพิ่ม firefox/webkit เมื่อมี `--project` หรือ `ALL_BROWSERS` (`:6-7,29-37`)
- `global-setup.ts`: เช็ก `/api/health` แล้ว `POST /api/test/reset` **ครั้งเดียวต่อรอบ** ไม่ใช่ต่อ test (`:7-13`)
- `fixtures.ts`: `open()` รอ `html[data-ready="true"]` (`:7-10`) · `baht()` ตัดทุกอย่างที่ไม่ใช่ตัวเลข (เครื่องหมายลบหาย) (`:33-35`)

| ครอบคลุม | ตรวจเงินที่หน้าไหน | ยืนยันจาก |
|---|---|---|
| หน้าแรก · ค้นหา/กรอง/เรียง · หน้าสินค้า (ขนาด สต็อก 404) · โปรด · ตะกร้า · คูปอง 4 ตัว · สมัคร/ล็อกอิน · checkout · แนะนำสินค้า · มือถือ + API 4 ข้อ | `/products` (CAT-03) · `/products/[slug]` (PRD-01) · `/cart` (CART-01..03, CPN-01..03) · `/orders/[id]` CHK-03 ฿378 (ใช้ FREESHIP) · CHK-04 แค่ `> 0` | `e2e-legacy/tests/*.spec.ts` · `08-checkout.spec.ts:60,79,109` |

**ยังไม่ครอบคลุม (ช่องโหว่)**

| เรื่อง | ทำไมสำคัญ |
|---|---|
| ยอดเงินบน `/checkout` และ `/account` | ไม่มี test ตรวจตัวเลขสองหน้านี้เลย |
| ออเดอร์จริงที่ส่งแบบปกติ **ไม่ใช้ FREESHIP** แล้วตรวจค่าส่ง/ยอดรวม | ออเดอร์ที่ตรวจยอดมีแต่ FREESHIP (CHK-03) · CHK-04 ตรวจแค่ > 0 → บล็อก PP-231 ใน `orders.ts:63-67` ไม่ถูกตรวจ |
| ค่าขอบ ฿999 พอดี | กฎเขียนไว้ 3 ที่ด้วย `>=` / `>` / เลขตรง |
| ส่งด่วน ฿120 · ด่วน + FREESHIP | ไม่มี test |
| ส่วนลด PAW10 / NEWCAT50 บนออเดอร์ที่สั่งจริง (server) | ตรวจแค่ในตะกร้า |
| 409 สต็อกไม่พอ · จังหวัดถูกแทน · register ไม่สน `?next` · ออเดอร์คนอื่น → 404 | ไม่มี test |
| API `coupons/validate` `GET /api/orders` `orders/[id]` `auth/*` `recommendations` 400 | ไม่มี test |

## G · เอกสารบอก ≠ โค้ดทำ

> ไม่ตัดสินว่าฝั่งไหนถูก — คอลัมน์สุดท้ายคือคำถามถึงเจ้าของร้าน

| เรื่อง | เอกสาร/คอมเมนต์บอก | โค้ดทำ (ไฟล์:บรรทัด) | ตรงไหม | คำถามถึงเจ้าของร้าน |
|---|---|---|---|---|
| ข้อมูลอยู่ใน memory | `HANDOVER-NOTES.md:3` · `README.md:3` | `lib/store.ts:94-99` | ✅ | – |
| รันที่ `localhost:4000` | `HANDOVER-NOTES.md:4` · `README.md:7` | `docker-compose.yml:8` | ✅ | – |
| reset ด้วย `ALLOW_TEST_RESET=1` | `README.md:13-15` · `TEST-DATA.md:11` | `docker-compose.yml:10` · `api/test/reset/route.ts:8-11` | ✅ | endpoint นี้ไม่มี auth — ระบบจริง (production) ปิด flag นี้แน่ไหม |
| เก็บใน localStorage แค่ตะกร้า+โปรด | `HANDOVER-NOTES.md:3` | มี `pp-recent` `pp-coupon` ด้วย `ShopProvider.tsx:59-62` | ⚠️ | – (เอกสารไม่ครบ) |
| "ทุกหน้าดึงสินค้าผ่าน `GET /api/products`" | `HANDOVER-NOTES.md:5` | หน้า `/` `/products` `/products/[slug]` import `liveProducts()` ตรงบน server (`app/page.tsx:19` · `products/page.tsx:13` · `products/[slug]/page.tsx:17`) · cart/wishlist ใช้ `PRODUCTS` static · `/api/products` ถูกเรียกแค่ `refreshStock` (`ShopProvider.tsx:262`) | ❌ | ถ้าจะแก้ข้อมูลสินค้า ต้องแก้ที่ `lib/products.ts` ใช่ไหม และมีระบบอื่น (แอปมือถือ?) ที่ใช้ `/api/products` อยู่หรือเปล่า |
| SUMMER20 ลด 20% ใช้ได้ถึงสิ้นปี | `HANDOVER-NOTES.md:6` | ล้มเสมอ "หมดอายุ" `lib/pricing.ts:123-124` | ❌ | SUMMER20 ควรใช้ได้อยู่หรือหมดอายุแล้ว (TEST-DATA บอกหมดอายุ) |
| SUMMER20 หมดอายุ | `TEST-DATA.md:8` | `lib/pricing.ts:123-124` | ✅ | – |
| PAW10 ลด 10% | `HANDOVER-NOTES.md:6` · `TEST-DATA.md:8` | `pricing.ts:113-114` (ปัดลง) | ✅ | ปัดเศษลงตามที่ตั้งใจไหม |
| PAW10 "สำหรับสมาชิกใหม่" vs "ทุกออเดอร์" | `app/page.tsx:218` vs `:72` | ไม่ตรวจผู้ใช้ `pricing.ts:113-114` | ⚠️ | PAW10 จำกัดเฉพาะสมาชิกใหม่ไหม |
| FREESHIP ส่งฟรี | `HANDOVER-NOTES.md:6` · `TEST-DATA.md:8` | `pricing.ts:115-116,145` ทำส่งด่วนเป็น 0 ด้วย | ⚠️ | FREESHIP ใช้กับส่งด่วนด้วยไหม |
| NEWCAT50 ลด ฿50 (อาหารแมว ≥ ฿500) | `TEST-DATA.md:8` | `pricing.ts:117-121` (นับ dry/wet/treat) | ✅ | ขนมแมวนับเป็น "อาหาร" ใช่ไหม |
| ค่าส่งปกติ ฿50 ฟรีเมื่อ "ซื้อครบ" ฿999 | `TEST-DATA.md:9` + ข้อความบนจอ 6 จุด (ดู D) | browser `>=` (`pricing.ts:132` · `CheckoutForm.tsx:216`) · server `>` (`orders.ts:65`) | ⚠️ | ยอด ฿999 พอดี ต้องส่งฟรีหรือเสีย ฿50 · ตั๋ว PP-231 ตั้งใจเปลี่ยนกฎค่าส่งด้วยหรือแค่ให้ server คำนวณเอง |
| ส่งด่วน ฿120 | `TEST-DATA.md:9` | `pricing.ts:41,131` | ✅ | – |
| บัญชี demo | `TEST-DATA.md:7` | `lib/store.ts:75,81` | ✅ | – |
| สินค้าหมด 0 / ใกล้หมด 3 | `TEST-DATA.md:10` | `lib/products.ts:217,233` | ✅ | – |
| regression ผ่านครบก่อน deploy | `HANDOVER-NOTES.md:8` · `e2e-legacy/README-LEGACY.md:28-31` | ค่าที่คาดใน spec สอดคล้องกับโค้ด (อ่านอย่างเดียว ยังไม่ได้รัน) แต่ไม่มี test ครอบ `orders.ts:63-67` | ⚠️ | deploy ล่าสุดรวมตั๋ว PP-231 ด้วยไหม |
| งานค้าง: ไม่มี | `HANDOVER-NOTES.md:9` | มีคอมเมนต์ตั๋ว `PP-231` ที่ `orders.ts:63` | ⚠️ | PP-231 ปิดแล้วจริงไหม มีรายละเอียดตั๋วเหลือไหม |
| ข้อมูลแยกด้วยอีเมลสุ่ม รันขนานได้ | `README-LEGACY.md:24` | สต็อกใช้ร่วมกัน reset ครั้งเดียวต่อรอบ (`global-setup.ts:12`) | ⚠️ | – (คำถามถึงทีมเทสต์ ไม่ใช่ร้าน) |
| 10 ไฟล์ 40 test | `README-LEGACY.md:3` | นับได้ 40 | ✅ | – |
| ตัวเลขหน้าแรก "28 สินค้า" "4.7★" | `app/page.tsx:76,80` (hard-code) | 28 รายการจริง · rating เฉลี่ยคำนวณได้ ≈ 4.68 (Explore) | ✅ | ตัวเลขนี้ควรคำนวณอัตโนมัติไหม |

## H · อ่านโค้ดอย่างเดียวยังพิสูจน์ไม่ได้

| เรื่อง | ทำไมโค้ดตอบไม่ได้ | ต้องดูด้วยวิธีไหน |
|---|---|---|
| ของที่รันอยู่ (container `pawpantry05`) ตรงกับโค้ด commit นี้ไหม | image อาจ build จากโค้ดรุ่นอื่น | ส่อง bundle ที่ build แล้ว / เทียบ source กับ bundle (REA) |
| ระหว่างใช้งานจริง browser เรียก API ไหนบ้าง ตามลำดับไหน | หน้า server component ไม่มี fetch ให้เห็น · บางทางเป็น fallback | HAR / REA ขับเบราว์เซอร์ แล้วนับ request |
| ยอดเงินที่ผู้ใช้เห็นแต่ละหน้า (cart · checkout · order · account) ตรงกันไหมที่ค่าขอบ | ต้องประกอบ client + server + ค่าที่เก็บ | สั่งซื้อจริงที่ยอด ฿998 / ฿999 / ฿1,000 แล้วเทียบ 4 หน้า |
| ข้อความ error/ปุ่ม ที่แสดงจริง (ภาษา ไทย ฟอนต์ มือถือ) | render ขึ้นกับ browser | Playwright 3 เบราว์เซอร์ |
| ชุดเทสต์เดิมยังผ่านครบกับของที่รันอยู่ไหม | README บอกผลรอบเก่า | รัน `npx playwright test` / `npm run test:all` |
| สต็อกฝั่ง browser ค้าง (stale) ระหว่างเปลี่ยนหน้าไหม | ขึ้นกับ React state + การ navigate (เดา) | ลองสั่งซื้อจาก 2 แท็บ / ดู network |
| ค่า env ใน production (`ALLOW_TEST_RESET`) | compose ในนี้เป็นของเครื่อง dev | ถามร้าน / ลอง `POST /api/test/reset` บนระบบจริง (ห้ามทำโดยไม่ได้รับอนุญาต) |

## I · งานนี้คือ reverse engineering แบบไหน (Chikofsky & Cross 1990)

| ส่วน | ชนิดงาน | ได้จากตาไหน | เหตุผล |
|---|---|---|---|
| A ภาพรวม | redocumentation | white-box | เขียน stack/วิธีรัน/ที่เก็บข้อมูล ใหม่จาก config และโค้ด ระดับเดียวกัน |
| B หน้าเว็บ | redocumentation | white-box | ไล่ไฟล์ `app/**/page.tsx` เป็นตาราง |
| C API | redocumentation | white-box | ไล่ `route.ts` เป็นตาราง |
| D กฎธุรกิจ | design recovery | white-box | ประกอบโค้ดหลายไฟล์เป็น "กฎของร้าน" + ชี้ที่เขียนซ้ำ |
| E state | redocumentation | white-box | ไล่ตัวแปร/key ที่เก็บข้อมูลและผลของ reset |
| F เทสต์เดิม | redocumentation | white-box | สรุป spec ที่มีอยู่ (ช่องโหว่ = เริ่มเป็นการตีความ) |
| G เอกสาร ≠ โค้ด | design recovery | white-box (เทียบเอกสาร) | สร้างความเข้าใจระดับเจตนา/กฎ แล้วชี้จุดที่ไม่ตรง |
| H ยังพิสูจน์ไม่ได้ | (รายการงานต่อ) | ต้องใช้ black-box / grey-box | ทุกข้อต้องรันระบบหรือดูของที่ build แล้ว |

- ยังไม่ใช่ re-engineering เพราะยังไม่ได้เปลี่ยนหรือสร้างระบบใหม่เลย — แค่ทำความเข้าใจและเขียนเอกสาร
- ควรยืนยันด้วยตาที่สองก่อนเชื่อ: **D** (กฎค่าส่งที่ขัดกันระหว่าง browser/server) และ **G** (ข้อ ⚠️/❌) — ต้องรันจริง (black-box) และถามเจ้าของร้าน

## ยังไม่รู้

- ตั๋ว PP-231 ต้องการอะไรจริง (มีแค่คอมเมนต์บรรทัดเดียว `lib/orders.ts:63`)
- ยอด ฿999 พอดี ร้านตั้งใจให้ส่งฟรีหรือไม่ (กฎใน browser กับ server ไม่ตรงกัน)
- SUMMER20 สถานะจริง (HANDOVER กับ TEST-DATA ขัดกัน)
- container ที่รันอยู่ build จากโค้ดนี้หรือไม่ · production เปิด `ALLOW_TEST_RESET` ไหม
- มีผู้ใช้ `/api/products` `/api/auth/me` `GET /api/orders` นอกจากหน้าเว็บนี้ไหม (UI ไม่เรียก)
- ไฟล์ที่อ้าง "(Explore)" เป็นบรรทัดที่ subagent เปิดดู แต่ผมไม่ได้เปิดซ้ำเอง
