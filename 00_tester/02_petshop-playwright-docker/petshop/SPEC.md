# PawPantry — Pet Food Shop (spec for builders and testers)

A Thai-language online shop that sells cat and dog food. It is a **test target** for a Playwright course,
so it must be beautiful, multi-page and fully deterministic. Everything a test needs is pinned down here:
routes, data, prices, error messages and `data-testid`s. **Do not rename anything in this file.**

## Stack
- Next.js 16 (App Router, TypeScript, `output: "standalone"`), React 19. No database: an in-memory store on `globalThis`.
- Styling: plain CSS (CSS modules or `app/globals.css`), no Tailwind. Fonts from `@fontsource/prompt` (headings) and `@fontsource/ibm-plex-sans-thai` (body), imported in `app/layout.tsx` (no network fonts at runtime).
- Optional animation library: `framer-motion` (or CSS only). Must respect `prefers-reduced-motion`.
- Runs in Docker: multi-stage `Dockerfile` (node:24-alpine or newer LTS, `npm ci`, `next build`, standalone runner, non-root user, `HEALTHCHECK` hitting `/api/health`), `.dockerignore`, `docker-compose.yml` (service `petshop`, container name `petshop`, port `3000:3000`, env `ALLOW_TEST_RESET=1`, `BUG_MODE=${BUG_MODE:-0}`).

## Look & feel ("wow")
Premium, playful, warm. Cream background `#FFF8EF`, ink `#1E2A3A`, coral primary `#FF6B4A`, teal accent `#14B8A6`, sunshine `#FFC145`, cat purple `#8B5CF6`, dog blue `#3B82F6`.
- Hero with big illustration (`/images/brand/hero.jpg`), animated floating paw prints / blobs, gradient headline, two CTAs (ช้อปอาหารแมว / ช้อปอาหารหมา) and a coupon ribbon `PAW10`.
- Glassy sticky header that shrinks on scroll; badge counters that "pop" when they change; cards lift and tilt on hover; add-to-cart shows a flying-dot animation to the cart icon and a toast.
- Skeleton shimmer while images load. Every product image falls back to a gradient tile with 🐱/🐶 emoji if the file is missing (`onError`).
- Fully responsive. At width < 768px the nav collapses into a hamburger (`menu-toggle`) that opens a drawer (`mobile-menu`).
- Footer with newsletter field (visual only), links, and "สร้างไว้สำหรับฝึก Playwright".

## Images (provided separately — just reference these paths)
- Products: `/images/products/<slug>.jpg`
- Brand: `/images/brand/hero.jpg`, `cat.jpg`, `dog.jpg`, `logo.png`, `empty-cart.jpg`, `empty-wishlist.jpg`, `finder.jpg`, `order-success.jpg`, `not-found.jpg`

## Products (exact data, `lib/products.ts`)
Fields: `slug, name (Thai), nameEn, pet ('cat'|'dog'), type ('dry'|'wet'|'treat'), lifeStage ('baby'|'adult'|'senior'), protein ('chicken'|'salmon'|'tuna'|'beef'|'lamb'|'duck'), grainFree, sizes[{label, price}], stock, rating, reviews, popularity, boughtWith[], description`.
`stock` is per product (shared by all sizes). Prices are THB integers.

| slug | name | nameEn | pet | type | life | protein | grainFree | sizes (label:price) | stock | rating | popularity | boughtWith |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kitten-salmon-dry | ลูกแมว สูตรแซลมอน | Kitten Salmon | cat | dry | baby | salmon | yes | 400 g:189, 1.5 kg:590 | 25 | 4.8 | 95 | kitten-chicken-mousse, lickable-salmon-treat |
| adult-chicken-dry | แมวโต สูตรไก่ | Adult Chicken | cat | dry | adult | chicken | no | 1.2 kg:359, 3 kg:799 | 40 | 4.6 | 90 | tuna-pouch |
| senior-tuna-dry | แมวสูงวัย สูตรทูน่า | Senior Tuna | cat | dry | senior | tuna | no | 1.2 kg:429 | 12 | 4.5 | 60 | urinary-care-dry |
| tuna-pouch | เพาช์ทูน่าในเยลลี่ | Tuna in Jelly | cat | wet | adult | tuna | yes | ซอง 85 g:35, แพ็ค 12 ซอง:390 | 60 | 4.7 | 88 | adult-chicken-dry |
| kitten-chicken-mousse | มูสไก่ลูกแมว | Kitten Chicken Mousse | cat | wet | baby | chicken | no | ซอง 85 g:39, แพ็ค 12 ซอง:420 | 30 | 4.4 | 70 | kitten-salmon-dry |
| duck-grainfree-dry | แมวโต เป็ดเกรนฟรี | Grain-Free Duck | cat | dry | adult | duck | yes | 1.5 kg:690 | 15 | 4.9 | 84 | lickable-salmon-treat |
| lickable-salmon-treat | ขนมแมวเลีย แซลมอน | Lickable Salmon | cat | treat | adult | salmon | yes | 4 ซอง:69, 20 ซอง:299 | 80 | 4.8 | 99 | duck-grainfree-dry |
| freeze-dried-chicken-cat | ไก่ฟรีซดราย สำหรับแมว | Freeze-Dried Chicken | cat | treat | adult | chicken | yes | 50 g:159 | **0** | 4.7 | 75 | adult-chicken-dry |
| hairball-control-dry | สูตรลดก้อนขน | Hairball Control | cat | dry | adult | salmon | no | 1.5 kg:520 | **3** | 4.3 | 55 | lickable-salmon-treat |
| urinary-care-dry | สูตรดูแลทางเดินปัสสาวะ | Urinary Care | cat | dry | senior | chicken | no | 1.5 kg:650 | 8 | 4.6 | 58 | senior-tuna-dry |
| puppy-chicken-dry | ลูกสุนัข สูตรไก่และข้าว | Puppy Chicken & Rice | dog | dry | baby | chicken | no | 1 kg:259, 3 kg:690 | 35 | 4.7 | 92 | puppy-lamb-wet |
| adult-lamb-dry | สุนัขโต สูตรแกะ | Adult Lamb | dog | dry | adult | lamb | no | 3 kg:790, 8 kg:1890 | 20 | 4.6 | 86 | dental-chew-treat |
| senior-salmon-dry | สุนัขสูงวัย สูตรแซลมอน | Senior Salmon | dog | dry | senior | salmon | yes | 3 kg:990 | 10 | 4.8 | 65 | salmon-skin-treat |
| beef-stew-can | สตูว์เนื้อกระป๋อง | Beef Stew | dog | wet | adult | beef | no | 400 g:79, แพ็ค 6 กระป๋อง:450 | 50 | 4.5 | 80 | small-breed-chicken-dry |
| puppy-lamb-wet | ลูกสุนัข แกะบด | Puppy Lamb Pâté | dog | wet | baby | lamb | yes | 100 g:45 | 40 | 4.4 | 62 | puppy-chicken-dry |
| dental-chew-treat | ขนมขัดฟัน | Dental Chew | dog | treat | adult | chicken | no | 7 ชิ้น:149, 28 ชิ้น:499 | 70 | 4.7 | 97 | adult-lamb-dry |
| duck-jerky-treat | เป็ดอบแห้ง | Duck Jerky | dog | treat | adult | duck | yes | 100 g:189 | 25 | 4.9 | 89 | adult-lamb-dry |
| small-breed-chicken-dry | สุนัขพันธุ์เล็ก สูตรไก่ | Small Breed Chicken | dog | dry | adult | chicken | no | 1.5 kg:420 | 30 | 4.5 | 78 | beef-stew-can |
| large-breed-beef-dry | สุนัขพันธุ์ใหญ่ สูตรเนื้อ | Large Breed Beef | dog | dry | adult | beef | no | 10 kg:1590 | 6 | 4.4 | 57 | dental-chew-treat |
| salmon-skin-treat | หนังปลาแซลมอนกรอบ | Crispy Salmon Skin | dog | treat | senior | salmon | yes | 80 g:129 | 14 | 4.6 | 68 | senior-salmon-dry |

### Toys & supplies (8 more rows → 28 products total, 14 cat + 14 dog)
`type` gains two values: `'toy'` (ของเล่น) and `'accessory'` (ของใช้). For these: `lifeStage: 'adult'`, `protein: null`, `grainFree: false`.

| slug | name | nameEn | pet | type | sizes (label:price) | stock | rating | popularity | boughtWith |
|---|---|---|---|---|---|---|---|---|---|
| cat-feather-wand | ไม้ตกแมว ขนนก | Feather Wand | cat | toy | 1 ชิ้น:129 | 45 | 4.8 | 91 | lickable-salmon-treat |
| cat-tunnel | อุโมงค์แมว 3 ทาง | Crinkle Tunnel | cat | toy | 1 ชิ้น:390 | 12 | 4.6 | 64 | cat-feather-wand |
| cat-scratcher | ที่ลับเล็บแมว | Cardboard Scratcher | cat | accessory | 1 ชิ้น:259 | 20 | 4.7 | 73 | cat-feather-wand |
| cat-fountain | น้ำพุแมว | Water Fountain | cat | accessory | 2 ลิตร:890 | 7 | 4.5 | 59 | urinary-care-dry |
| dog-rope-toy | เชือกกัดสำหรับหมา | Rope Tug Toy | dog | toy | 1 ชิ้น:149 | 50 | 4.7 | 87 | dental-chew-treat |
| dog-squeaky-ball | ลูกบอลมีเสียง | Squeaky Ball | dog | toy | แพ็ค 3 ลูก:199 | 35 | 4.8 | 93 | duck-jerky-treat |
| dog-slow-bowl | ชามกินช้า | Slow Feeder Bowl | dog | accessory | 1 ใบ:290 | 18 | 4.6 | 66 | adult-lamb-dry |
| dog-cozy-bed | เบาะนอนนุ่มฟู | Cozy Bed | dog | accessory | M:690, L:990 | 9 | 4.9 | 77 | dental-chew-treat |

Rules for the new types:
- `filter-type` select options: all, dry (อาหารเม็ด), wet (อาหารเปียก), treat (ขนม), toy (ของเล่น), accessory (ของใช้).
- Header gets one more nav link `nav-toys` → `/products?type=toy` (label `ของเล่น`), also inside the mobile drawer.
- Finder (`/finder`, `/api/recommendations`) only ever returns food (`dry|wet|treat`), never toys/accessories.
- `NEWCAT50` counts only cat **food** (dry/wet/treat) toward the ฿500 minimum.
- Search by protein simply never matches toys (protein null). Search still matches name/nameEn.
- Product detail for toys/accessories shows no protein / grain-free info.

Each product has 2–3 Thai reviews (name, stars, text, date) for the detail page, plus a 1–2 sentence Thai description.

## Pricing rules (`lib/pricing.ts`, shared by client and server)
- `subtotal` = Σ price(size) × qty.
- Coupons (case-insensitive, trimmed):
  - `PAW10` → 10% off subtotal, rounded down to integer.
  - `FREESHIP` → shipping becomes 0.
  - `NEWCAT50` → 50 off, only if cat-items subtotal ≥ 500, else error `ต้องซื้ออาหารแมวขั้นต่ำ ฿500`.
  - `SUMMER20` → expired, error `คูปองนี้หมดอายุแล้ว`.
  - anything else → error `ไม่พบคูปองนี้`.
- Shipping: `standard` = 50, free (0) when subtotal ≥ 999; `express` = 120 always.
- `total = subtotal − discount + shipping` (never below 0).
- Money format everywhere: `฿1,234` (no decimals) via one helper `formatBaht`.

## BUG_MODE (training bugs, server reads `process.env.BUG_MODE === "1"`, expose to client via a server-rendered `<html data-bug-mode="1">` attribute or similar so shared code can read it)
When on, exactly these 3 bugs appear, otherwise the app is correct:
1. `PAW10` gives 1% instead of 10% (in `lib/pricing.ts`, on both client and server).
2. Removing an item from the **wishlist** does not decrease the header wishlist badge until reload.
3. Checkout phone validation accepts 9 digits (`0812345678` and `081234567` both pass).

## Client state (localStorage, via one React context provider)
- `pp-cart`: `[{slug, size, qty}]` (same slug+size merges, qty capped at stock).
- `pp-wishlist`: `[slug]`
- `pp-recent`: last 6 viewed slugs, newest first.
- After the provider has loaded localStorage it sets `document.documentElement.dataset.ready = "true"`. Tests wait for `html[data-ready="true"]`.

## Server store (in-memory, `lib/store.ts`)
- users (seed: `demo@pawpantry.test` / `Paw12345`, name `สมใจ ใจดี`, pet `cat`), sessions (httpOnly cookie `pp_session`), orders, product stock.
- Passwords hashed with `crypto.scryptSync`.
- Order ids `PP-` + 6 digits, starting `PP-100001`.

## API routes
| method | path | notes |
|---|---|---|
| GET | `/api/health` | `{ ok: true }` |
| GET | `/api/products?pet=&type=&life=&q=&sort=` | returns `{ items, total }` |
| GET | `/api/products/[slug]` | 404 `{ error }` when unknown |
| GET | `/api/recommendations?pet=&life=&noChicken=1&grainFree=1&type=` | finder results |
| POST | `/api/coupons/validate` | body `{ code, items }` → `{ ok, discount, freeShipping, message }` |
| POST | `/api/auth/register` | 400 with `{ errors: {field: message} }`, 409 duplicate |
| POST | `/api/auth/login` | 401 `{ error: "อีเมลหรือรหัสผ่านไม่ถูกต้อง" }` |
| POST | `/api/auth/logout` | |
| GET | `/api/auth/me` | `{ user }` or `{ user: null }` |
| POST | `/api/orders` | 401 if not logged in; server recomputes prices; 409 `{ error: "สินค้าไม่พอ: <name>" }` if stock short; decrements stock |
| GET | `/api/orders` | current user's orders |
| GET | `/api/orders/[id]` | own order only (404 otherwise) |
| POST | `/api/test/reset` | only if `ALLOW_TEST_RESET=1`; resets store to seed; else 404 |

## Pages and required `data-testid`s
Global header: `logo` (link to `/`), nav links `nav-cat` (`/products?pet=cat`), `nav-dog` (`/products?pet=dog`), `nav-finder` (`/finder`), `search-input` + submit `search-submit` (goes to `/products?q=`), `wishlist-link` with `wishlist-count`, `cart-link` with `cart-count` (count = total qty; badge hidden or shows 0 when empty — always render the element, text `0`), `login-link` (when logged out), `user-menu` showing user name (when logged in), `logout-button`, `menu-toggle`, `mobile-menu`. Toasts: `toast` (role="status").

1. `/` Home: `hero`, `hero-cta-cat`, `hero-cta-dog`, `category-cat`, `category-dog`, section `popular-products` (top 8 by popularity), section `recommended-for-you` (personalised: if `pp-recent` or wishlist non-empty, recommend in-stock products with same pet and protein/type as those, excluding already-viewed; else popular; heading `แนะนำสำหรับคุณ`), section `recently-viewed` (only when non-empty), `promo-banner` showing code `PAW10`.
2. `/products` Catalog: filters synced to URL query: `filter-pet-all|cat|dog` (buttons/chips), `filter-type` (select: all, dry, wet, treat), `filter-life` (select: all, baby, adult, senior), `filter-grainfree` (checkbox), `sort-select` (values `popular` default, `price-asc`, `price-desc`, `rating`), `result-count` text `พบ N รายการ`, grid of `product-card` each with attribute `data-slug`, inside: `product-name`, `product-price` (lowest size price, e.g. `฿189`), `stock-badge` (`หมด` when 0, `เหลือ N ชิ้น` when ≤ 5), `wishlist-toggle` (aria-pressed), `quick-add` (adds smallest size qty 1; disabled when out of stock). Empty state `empty-results` with text `ไม่พบสินค้าที่ตรงกับการค้นหา` and a `clear-filters` button. Search `q` matches name, nameEn, protein (Thai or English: ไก่/chicken, แซลมอน/salmon, ทูน่า/tuna, เนื้อ/beef, แกะ/lamb, เป็ด/duck).
3. `/products/[slug]` Product: `product-title`, `product-image`, `product-price` (price of selected size), `size-option` buttons (`data-size` = label, aria-pressed), `qty-input` (number), `qty-plus`, `qty-minus` (qty clamps 1..stock), `add-to-cart` (disabled + text `สินค้าหมด` when stock 0), `wishlist-toggle`, `stock-info`, `rating`, reviews list `review`, sections `bought-together` (cards for `boughtWith`, with button `add-bundle` that adds this product + all boughtWith products, smallest sizes, qty 1) and `similar-products` (same pet & type, up to 4). Visiting adds to `pp-recent`. Unknown slug → custom 404 page `not-found` with link home.
4. `/wishlist`: rows `wishlist-item` (`data-slug`), `wishlist-remove`, `move-to-cart` (adds smallest size then removes from wishlist). Empty: `empty-wishlist`.
5. `/cart`: rows `cart-item` (`data-slug`, `data-size`), `item-qty` (number input), `item-plus`, `item-minus`, `item-remove`, `item-line-total`; `free-shipping-progress` text `ซื้อเพิ่มอีก ฿N เพื่อส่งฟรี` or `ได้ส่งฟรีแล้ว!`; `coupon-input`, `coupon-apply`, `coupon-message` (success `ใช้คูปอง PAW10 แล้ว` / error text above), `coupon-remove`; `summary-subtotal`, `summary-discount`, `summary-shipping` (`ฟรี` when 0), `summary-total`; `checkout-button`; recommendations strip `cart-recommendations` (boughtWith of cart items, not already in cart). Empty: `empty-cart` + `continue-shopping`. Applied coupon persists in localStorage `pp-coupon`.
6. `/finder` Pet Food Finder (3-step wizard with progress bar `finder-progress`): step 1 `finder-pet-cat` / `finder-pet-dog`; step 2 `finder-life-baby|adult|senior`; step 3 checkboxes `finder-no-chicken`, `finder-grainfree`, select `finder-type` (any/dry/wet/treat); buttons `finder-next`, `finder-back`, `finder-submit`. Results `finder-results` with up to 4 `finder-result` (`data-slug`), each showing a `match-score` (`ตรงใจ N%`) and reason chips `match-reason` (e.g. `เหมาะกับลูกแมว`, `ไม่มีไก่`, `เกรนฟรี`, `รีวิว 4.8★`). Algorithm: same pet only, exclude out-of-stock, exclude chicken if `noChicken`, only grainFree if `grainFree`, filter type if chosen; score = 50 (life match) + 20 (type match or type any) + rating×6, then normalise to max 99%; sort desc then popularity. If nothing matches: `finder-empty`.
7. `/register`: inputs `reg-name`, `reg-email`, `reg-password`, `reg-confirm`, radio `reg-pet-cat|dog|both`, checkbox `reg-terms`, submit `reg-submit`. Field errors `error-<field>` (field = name, email, password, confirm, terms):
   - name empty → `กรุณากรอกชื่อ`
   - email invalid → `อีเมลไม่ถูกต้อง`
   - password < 8 chars or no digit → `รหัสผ่านต้องมีอย่างน้อย 8 ตัว และมีตัวเลข`
   - confirm mismatch → `รหัสผ่านไม่ตรงกัน`
   - terms unchecked → `กรุณายอมรับเงื่อนไข`
   - duplicate email (409) → `error-email`: `อีเมลนี้ถูกใช้แล้ว`
   - Password strength meter `password-strength` (อ่อน / ปานกลาง / แข็งแรง).
   - Success: logs in, redirects to `/account?welcome=1`, shows `welcome-banner` `ยินดีต้อนรับ <name>!`.
8. `/login`: `login-email`, `login-password`, `login-submit`, `login-error` (`อีเมลหรือรหัสผ่านไม่ถูกต้อง`). Supports `?next=/checkout` redirect after login. Link to register.
9. `/checkout` (requires login; otherwise redirect to `/login?next=/checkout`; empty cart → redirect to `/cart`). Stepper look. Fields `ship-name`, `ship-phone`, `ship-address`, `ship-province` (select of 10 provinces incl. กรุงเทพมหานคร, เชียงใหม่, ขอนแก่น, ชลบุรี, ภูเก็ต), `ship-postcode`; radios `shipping-standard`, `shipping-express`; radios `pay-cod`, `pay-promptpay` (shows a fake QR box `promptpay-qr`); errors `error-ship-name` `กรุณากรอกชื่อผู้รับ`, `error-ship-phone` `เบอร์โทรต้องเป็นตัวเลข 10 หลัก ขึ้นต้นด้วย 0`, `error-ship-address` `กรุณากรอกที่อยู่ (อย่างน้อย 10 ตัวอักษร)`, `error-ship-postcode` `รหัสไปรษณีย์ต้องเป็นตัวเลข 5 หลัก`; order summary with same `summary-*` testids; `place-order`. Prefill `ship-name` with user name. On success: clear cart and coupon, go to `/orders/<id>`.
10. `/orders/[id]`: `order-success` heading `สั่งซื้อสำเร็จ!`, `order-id` (e.g. `PP-100001`), list `order-item`, `summary-total`, status timeline (รับคำสั่งซื้อ → แพ็คสินค้า → จัดส่ง → ถึงแล้ว) with first step active; confetti animation once.
11. `/account`: requires login (redirect to `/login?next=/account`); `welcome-banner` when `?welcome=1`; profile card; `order-history` with rows `order-row` (`data-order-id`) linking to the order page; empty `no-orders` `ยังไม่มีคำสั่งซื้อ`.

## Accessibility & test-friendliness
- Every input has a `<label>`. Buttons are real `<button>`s. Images have Thai alt text.
- No random data on screen that changes between runs (except order ids which are sequential after reset).
- Animations ≤ 400 ms; never block clicks.
