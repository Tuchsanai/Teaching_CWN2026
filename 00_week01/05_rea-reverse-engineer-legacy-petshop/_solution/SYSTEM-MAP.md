# SYSTEM-MAP · PawPantry ที่ build แล้ว (มุม REA) เทียบกับโค้ด

> ทำเมื่อ: **2026-10-12** · โค้ดจาก commit `13b334b` (petshop/ ไม่ได้แก้) · build สำเนาใน `out\v1` ด้วย `node:24-alpine` (Next.js 16.4.0 Turbopack · 159 วินาทีรวม `npm ci`)
> REA 6.4.0 (`rea-lab:6.4.0`) · ผลดิบใน `out\v1-static.json` `out\v1-server.json` `out\trace-coupon.json` (ย่อด้วย `node rea\rea-summarize.mjs` เท่านั้น ไม่ได้เปิด JSON ตรง)
> `out\v1` = "ของเดิม" ไว้เทียบทีหลัง ห้ามแก้จนจบบท

| ผล REA | evidence_id_short | subject_digest_short | ไฟล์ | node | edge | coverage | limitations |
|---|---|---|---|---|---|---|---|
| static (`/work/out/v1/.next/static` = ของที่ browser โหลด) | `ev_64fa462f` | `8887b53bc4b2` | 21 | 63 | 68 | partial / partial | 16 |
| server (`/work/out/v1/.next/server`) | `ev_ac8d9821` | `dcd04a88daaf` | 445 | 1,528 | 1,868 | partial / partial | 202 |
| trace คูปอง (seed `string:coupons/validate` · incoming · จาก server) | `ev_d404eddd` | – | – | 16 | 75 | partial | – |

node แต่ละชนิด
- static: javascript-asset 21 · javascript-module 19 · unknown 10 · endpoint 9 · artifact 1 · storage 3
- server: source-module 729 · javascript-module 185 · javascript-asset 169 · unknown 196 · artifact 89 · source-map 95 · endpoint 63 (สรุปรวมเป็น 34 แถว) · electron-renderer 2
- server กู้ path ต้นทางจาก source map ได้ **52 ไฟล์** (`app/` 25 = หน้า 11 + layout + not-found + API route 12 · `components/` 18 · `lib/` 9) · static กู้ได้ **0**

ป้าย: 🔵 static = อ่านเจอตรง ๆ ในไฟล์ที่ build · 🟢 runtime = เห็นตอนระบบรันจริง · 🟡 inference = REA/ผมอนุมาน (ชื่อถูกย่อ เดาชนิด เดา URL จาก path) · ⚪ unknown = REA บอกว่ามีแต่ไม่รู้ค่า

## A · REA เห็นอะไร

| สิ่งที่เจอ | ชนิด | มาจาก | ป้าย | evidence_id |
|---|---|---|---|---|
| `/api/auth/login` (`call:fetch`) | endpoint | static + server (`chunks/ssr/components_LoginForm_tsx_…js`) | 🔵 | `ev_64fa462f` · `ev_ac8d9821` |
| `/api/auth/logout` (`call:fetch`) | endpoint | static + server (`chunks/ssr/components_15s-58tum8e8a._.js` ชื่อไม่บอกว่าเป็น component ไหน) | 🔵 (ไฟล์ต้นทาง 🟡) | `ev_64fa462f` · `ev_ac8d9821` |
| `/api/auth/register` (`call:fetch`) | endpoint | static + server (`components_RegisterForm_tsx_…js`) | 🔵 | `ev_64fa462f` · `ev_ac8d9821` |
| `/api/coupons/validate` (`call:fetch`) | endpoint | static + server (`components_CartView_tsx_…js`) | 🔵 | `ev_64fa462f` · `ev_ac8d9821` |
| `/api/orders` (`call:fetch`) | endpoint | static + server (`components_CheckoutForm_tsx_…js`) · สรุปไม่บอก method | 🔵 (method ⚪) | `ev_64fa462f` · `ev_ac8d9821` |
| `/api/products` (`call:fetch`) | endpoint | static + server (`chunks/ssr/_01-bhf61ps_r7._.js` ไฟล์เดียวกับ localStorage → น่าจะ ShopProvider) | 🔵 (ไฟล์ต้นทาง 🟡) | `ev_64fa462f` · `ev_ac8d9821` |
| `a` `b` (`call:Uv.delete`) · `c` (`call:e.get`) | "endpoint" ปลอม | static | 🟡 noise — ชื่อตัวแปรถูกย่อ · grep ไฟล์ build เจอเป็นโค้ดทดสอบความสามารถ `URLSearchParams` ของ polyfill (`"https://a/c%20d?a=1&c=3"`) ไม่ใช่ API ของร้าน | `ev_64fa462f` |
| local-storage `getItem` `setItem` `removeItem` | storage ×3 | static + server (`_01-bhf61ps_r7._.js`) | 🔵 ชนิด · ⚪ key (`name: null`) | `ev_64fa462f` · `ev_ac8d9821` |
| `pp_session` (`call:a.get` · `chunks/ssr/_12axzdy3dcd09._.js`) | ถูกจัดเป็น endpoint แต่จริงคือชื่อ cookie | server | 🔵 ค่า · 🟡 ชนิดผิด | `ev_ac8d9821` |
| `pet` `type` `life` `grainFree` `noChicken` (`call:e.get`) | ถูกจัดเป็น endpoint แต่น่าจะเป็นชื่อ query parameter | server | 🟡 | `ev_ac8d9821` |
| `Cache-Control` `authorization` `cookie` `set-cookie` `user-agent` `next.route` `next.span_type` `/` `static/chunks/3tywpon56yur2.css` | "endpoint" ที่เป็นชื่อ header / attribute ของ Next.js | server (ส่วนใหญ่ `node_modules_next_dist_*`) | 🟡 noise | `ev_ac8d9821` |
| ไฟล์ต้นทาง 52 ไฟล์ (เช่น `app/api/coupons/validate/route.ts` `components/CartView.tsx` `lib/pricing.ts`) | recovered source (source map) | server เท่านั้น | 🔵 path · URL ของหน้า/API 🟡 (เดาจากกติกา App Router) | `ev_ac8d9821` |
| node `electron-renderer` 2 ตัว | ชนิด runtime ที่ REA จัดให้ | server | ⚪ (สรุปไม่บอกว่าไฟล์ไหน) · 🟡 แอปนี้เป็น Next.js ไม่ใช่ Electron → น่าจะเป็นการเดาชนิดจาก global ฝั่ง browser ในโค้ด SSR | `ev_ac8d9821` |
| unknown 10 (static) / 196 (server) · limitations 16 / 202 | node/ข้อจำกัดที่ REA วิเคราะห์ไม่ได้ | ทั้งคู่ | ⚪ | `ev_64fa462f` · `ev_ac8d9821` |
| trace คูปอง: matched seeds 13 · traced nodes 16 · edges 75 · observed facts 149 · inferred facts 3 · terminal paths 0 | trace | server | 🔵 (+ inferred 3 🟡) | `ev_d404eddd` |
| trace → ไฟล์ต้นทาง `app/api/coupons/validate/route.ts` (ผ่าน `chunks/_1q6d1zmza_6h_._.js.map`) + chunk ฝั่งเรียก `chunks/ssr/components_CartView_tsx_12yx7o-868btn._.js` + manifest/nft ของ route | trace node | server | 🔵 | `ev_d404eddd` |
| trace ติด node ที่ไม่เกี่ยว `app/register/page/server-reference-manifest.json` `app/register/page.js.map` `app/api/products/[slug]/route/build-manifest.json` | trace node | server | 🟡 น่าจะเพราะ manifest รวมทุก route ไว้ในไฟล์เดียว | `ev_d404eddd` |

## B · triangulation (หน้า · API · state จาก CODEBASE-MAP ส่วน B C E)

ตาที่ใช้: **white** = อ่านโค้ด · **grey** = REA ส่องของที่ build (หรือ grep ไฟล์ build เอง — เขียนกำกับไว้) · **black** = เปิดเว็บ/HAR/ผลจากข้างนอก
เกณฑ์ ✅ = REA เห็นสิ่งนั้นเองและตรงกับโค้ด · ⚠️ = REA เห็นบางส่วน/ผิดชนิด · ❓ = REA ไม่เจอตัวสิ่งนั้น (**ไม่ได้แปลว่าไม่มี**)

### B1 · หน้าเว็บ (12)

REA ไม่ได้ทำรายการ URL ของหน้า (หน้าไม่มี `fetch` ให้จับ) แต่กู้ไฟล์ `page.tsx` ทุกหน้าจาก source map ของ server bundle (🔵 path · URL 🟡)

| รายการ | REA เห็น | โค้ดบอก (ไฟล์:บรรทัด) | ตรงไหม | ยืนยันด้วยตา |
|---|---|---|---|---|
| `/` | server: `app/page.tsx` | `app/page.tsx:18` | ✅ | white + grey |
| `/products` | server: `app/products/page.tsx` | `app/products/page.tsx:11` | ✅ | white + grey |
| `/products/[slug]` | server: `app/products/[slug]/page.tsx` | `app/products/[slug]/page.tsx:15` | ✅ | white + grey |
| `/cart` | server: `app/cart/page.tsx` + `components/CartView.tsx` (อยู่ใน trace คูปองด้วย) | `app/cart/page.tsx:6` | ✅ | white + grey |
| `/checkout` | server: `app/checkout/page.tsx` | `app/checkout/page.tsx:8` | ✅ | white + grey |
| `/orders/[id]` | server: `app/orders/[id]/page.tsx` | `app/orders/[id]/page.tsx:15` | ✅ | white + grey |
| `/account` | server: `app/account/page.tsx` | `app/account/page.tsx:13` | ✅ | white + grey |
| `/login` | server: `app/login/page.tsx` | `app/login/page.tsx:12` | ✅ | white + grey |
| `/register` | server: `app/register/page.tsx` | `app/register/page.tsx:7` | ✅ | white + grey |
| `/wishlist` | server: `app/wishlist/page.tsx` | `app/wishlist/page.tsx:6` | ✅ | white + grey |
| `/finder` | server: `app/finder/page.tsx` | `app/finder/page.tsx:6` | ✅ | white + grey |
| 404 | server: `app/not-found.tsx` | `app/not-found.tsx:4` | ✅ | white + grey |

### B2 · API (13 แถว = 12 route · `/api/orders` แยก GET/POST)

| รายการ | REA เห็น | โค้ดบอก (ไฟล์:บรรทัด) | ตรงไหม | ยืนยันด้วยตา |
|---|---|---|---|---|
| POST `/api/auth/login` | static+server `call:fetch` (LoginForm chunk) · route.ts กู้ได้ | `app/api/auth/login/route.ts:8` · เรียกที่ `components/LoginForm.tsx:23` | ✅ | white + grey |
| POST `/api/auth/logout` | static+server `call:fetch` · route.ts กู้ได้ | `app/api/auth/logout/route.ts:8` · `components/Header.tsx:55` | ✅ | white + grey |
| GET `/api/auth/me` | ❌ ไม่มีใน endpoint · กู้ได้แค่ชื่อไฟล์ `app/api/auth/me/route.ts` | `app/api/auth/me/route.ts:6` · UI ไม่เรียก | ❓ | white |
| POST `/api/auth/register` | static+server `call:fetch` (RegisterForm chunk) · route.ts กู้ได้ | `app/api/auth/register/route.ts:8` · `components/RegisterForm.tsx:36` | ✅ | white + grey |
| POST `/api/coupons/validate` | static+server `call:fetch` (CartView chunk) · trace เจอ route.ts + CartView | `app/api/coupons/validate/route.ts:6` · `components/CartView.tsx:161` | ✅ | white + grey |
| GET `/api/health` | ❌ ไม่มีใน endpoint · กู้ได้แค่ชื่อไฟล์ route.ts | `app/api/health/route.ts:5` · ใช้โดย Docker HEALTHCHECK | ❓ | white + black (`docker ps` แสดง `pawpantry05 … (healthy)` = HEALTHCHECK เรียกแล้วผ่าน) |
| GET `/api/orders` | เห็นสตริง `/api/orders` แต่ตัวที่เจออยู่ใน CheckoutForm (= POST) · สรุปไม่บอก method | `app/api/orders/route.ts:9` · UI ไม่เรียก | ⚠️ | white |
| POST `/api/orders` | static+server `call:fetch` (CheckoutForm chunk) · method ⚪ | `app/api/orders/route.ts:15` · `components/CheckoutForm.tsx:73` | ✅ | white + grey |
| GET `/api/orders/[id]` | ❌ ไม่มีใน endpoint · กู้ได้แค่ชื่อไฟล์ route.ts | `app/api/orders/[id]/route.ts:7` · UI ไม่เรียก | ❓ | white |
| GET `/api/products` | static+server `call:fetch` (`_01-bhf61ps_r7._.js`) · route.ts กู้ได้ · server เห็นชื่อ query `pet` `type` `life` `grainFree` (🟡) | `app/api/products/route.ts:7` · `components/ShopProvider.tsx:262` | ✅ | white + grey |
| GET `/api/products/[slug]` | ❌ ไม่มีใน endpoint · กู้ได้แค่ชื่อไฟล์ route.ts | `app/api/products/[slug]/route.ts:6` · UI ไม่เรียก | ❓ | white |
| GET `/api/recommendations` | ❌ ไม่มีใน endpoint ทั้ง 2 bundle (ทั้งที่ UI เรียกจริง) · grep ไฟล์ build เองเจอ `` fetch(`/api/recommendations?${e.toString()}` `` ใน `static/chunks/0hsrwulyc6rel.js` | `app/api/recommendations/route.ts:7` · `components/FinderWizard.tsx:95` (template literal) | ❓ | white + grey (grep build เอง ไม่ใช่ REA) |
| POST `/api/test/reset` | ❌ ไม่มีใน endpoint · กู้ได้แค่ชื่อไฟล์ route.ts | `app/api/test/reset/route.ts:7` · UI ไม่เรียก | ❓ | white |

เหตุผลที่เป็นไปได้ที่ REA ไม่เจอ (ไม่ได้แปลว่าไม่มี)
- `auth/me` `orders` (GET) `orders/[id]` `products/[slug]` `test/reset` `health`: ไม่มีโค้ดฝั่ง browser เรียก → ไม่มี `fetch("…")` ให้ static เจอ · ฝั่ง server ตัว route ไม่ได้เขียน URL เป็นสตริง (URL มาจากตำแหน่งโฟลเดอร์ตามกติกา App Router) REA จึงได้แค่ชื่อไฟล์จาก source map · ถ้า build ไม่แนบ source map จะไม่เห็นแม้แต่ชื่อไฟล์
- `recommendations`: URL ประกอบด้วย template literal + query ที่สร้างตอนรัน (`${sp.toString()}`) REA จับเฉพาะสตริงคงที่
- route แบบ `[id]` `[slug]` เป็น URL ที่มีค่าเปลี่ยน ต้องเห็นตอนรัน (HAR) หรืออ่านโค้ด

### B3 · state (8)

| รายการ | REA เห็น | โค้ดบอก (ไฟล์:บรรทัด) | ตรงไหม | ยืนยันด้วยตา |
|---|---|---|---|---|
| ผู้ใช้ (RAM `__pawpantryStore.users`) | ❌ ไม่มี storage node (REA จับ storage ฝั่ง browser) · กู้ได้แค่ไฟล์ `lib/store.ts` | `lib/store.ts:49` | ❓ | white |
| session (RAM `.sessions`) | ❌ เหมือนข้างบน | `lib/store.ts:50,86` | ❓ | white |
| ออเดอร์ + เลขรัน (RAM `.orders` `.nextOrderNo`) | ❌ | `lib/store.ts:51,87` | ❓ | white |
| สต็อก (RAM `.stock`) | ❌ | `lib/store.ts:52` | ❓ | white |
| hash รหัส demo (`demoHash` ตัวแปร module) | ❌ | `lib/store.ts:72,75` | ❓ | white |
| cookie `pp_session` | server เห็นสตริง `pp_session` (`call:a.get`) แต่จัดเป็น endpoint ไม่ใช่ cookie | `lib/auth.ts:6,10,20` | ⚠️ | white + grey |
| localStorage `pp-cart` `pp-wishlist` `pp-recent` `pp-coupon` | static+server: local-storage get/set/remove ×3 · `name: null` (⚪ ไม่รู้ key) · grep ไฟล์ build เองเจอ `i="pp-cart",l="pp-wishlist"` ใน `static/chunks/34-265z4ykszx.js` (key ถูกส่งผ่านตัวแปร REA จึงไม่ผูกชื่อ) | `components/ShopProvider.tsx:59-62,66,75,253-254` | ⚠️ | white + grey |
| state ใน React (`user` `cart` `wishlist` ของ ShopProvider) | ❌ REA ไม่ได้จำลอง state ของ React · กู้ได้แค่ไฟล์ `components/ShopProvider.tsx` | `components/ShopProvider.tsx:112-115` | ❓ | white |

## C · คำตอบ 5 ข้อ

**(1) ผลไหนเป็นแค่ inference หรือชื่อที่ถูกย่อ (minify)**
- ชื่อถูกย่อ: endpoint `a` `b` `c` และ mechanism `Uv.delete` `e.get` `C.get` `G.get` `a.get` `r.get` (ชื่อตัวแปรหลัง minify) · ชื่อ chunk ฝั่ง static เป็น hash ทั้งหมด (`0hsrwulyc6rel.js` `34-265z4ykszx.js`) ส่วน chunk ฝั่ง server บางตัวยังมีชื่อ component (`components_CartView_tsx_…`) แต่บางตัวไม่มี (`components_15s-58tum8e8a._.js` `_01-bhf61ps_r7._.js`)
- inference: การจัดชนิด `electron-renderer` (แอปไม่ใช่ Electron) · `pp_session` และชื่อ query/header ที่ถูกจัดเป็น "endpoint" · URL ของหน้า/API ที่เดาจาก path ไฟล์ (`app/cart/page.tsx` → `/cart`) · `inferred_facts 3` ใน trace · node manifest ที่ติดมาใน trace · ข้อสรุปว่า `_01-bhf61ps_r7._.js` คือ ShopProvider (ผมเดาจากการที่ fetch `/api/products` กับ localStorage อยู่ไฟล์เดียวกัน)
- ⚪ unknown: key ของ localStorage (`name: null`) · method ของ `/api/orders` · node unknown 10/196 · limitations 16/202

**(2) ถ้ามีแต่ build ไม่มี source เราจะรู้อะไรได้และไม่ได้**
- รู้ได้: API ที่ browser เรียกด้วย URL คงที่ (6 ตัว) · ว่ามีการใช้ localStorage (get/set/remove) · ถ้า build แนบ source map (server bundle นี้มี 95 source-map node) จะได้ชื่อไฟล์ต้นทาง 52 ไฟล์ → รู้โครงหน้า/route/component · ชื่อ cookie/query ที่เป็นสตริงตรง ๆ (ต้องคัด noise เอง)
- รู้ไม่ได้ (จาก REA อย่างเดียว): URL ที่ประกอบตอนรัน (`/api/recommendations?…`) · key ของ localStorage · method ของ API · กฎธุรกิจ (เช่น `>=` กับ `>` ที่ ฿999 ใน CODEBASE-MAP ส่วน D) · state ฝั่ง server ใน RAM · API ที่ไม่มีใครเรียกจากหน้าเว็บ ถ้าไม่มี source map (static bundle ที่ browser ได้ กู้ source ได้ **0** ไฟล์)
- ส่วนที่ "รู้ได้แต่ต้องขุดเอง": บางอย่างมีอยู่ในไฟล์ build จริง (key `pp-cart` URL recommendations) แต่ REA ไม่ได้ยกขึ้นมา ต้อง grep ไฟล์ build เองหรือดูตอนรัน

**(3) งานแบบไหนควรใช้ REA งานแบบไหนอ่าน source ก็พอ**
- อ่าน source ก็พอ: ทำแผนที่สถาปัตยกรรมเมื่อมี repo อยู่ในมือ — CODEBASE-MAP (อ่านโค้ด) ได้ครบ 12 route พร้อมบรรทัด method และกฎธุรกิจ ส่วน static REA เห็น endpoint ของร้านแค่ 6 จาก 12 route
- ควรใช้ REA: มีแต่ของที่ deploy/build (ไม่มี source หรือไม่แน่ใจว่า source ตรงกับของที่รัน — CODEBASE-MAP ส่วน H ข้อแรก) · ตรวจว่า browser ได้รับอะไรไปจริง (endpoint ที่เปิดเผย ชื่อไฟล์ใน source map ที่หลุดไป) · เทียบรุ่นก่อน/หลังแก้ด้วย digest · ตามรอยฟีเจอร์ข้ามไฟล์ที่ build แล้ว (trace คูปองเจอ route + CartView) · งาน runtime (HAR/scenario) ในขั้นถัดไป

**(4) subject digest มีไว้ทำอะไรกับงานทดสอบ**
- เป็นลายนิ้วมือของ "ของที่ถูกวิเคราะห์" (static `8887b53bc4b2` · server `dcd04a88daaf`) ต่างจาก evidence_id ที่เป็นรหัสของผลวิเคราะห์ครั้งนั้น
- ใช้ผูกผลทดสอบ/หลักฐานกับ build ที่แน่นอน: ถ้ารายงานบอกว่าทดสอบ build digest X แล้ว build ที่ deploy มี digest Y แปลว่าทดสอบคนละของ ต้องรันใหม่ · ใช้พิสูจน์ว่า `out\v1` (ของเดิม) ไม่ถูกแตะระหว่างบท · ใช้เทียบ v1 กับรุ่นหลังแก้ว่าเปลี่ยนจริง และเปลี่ยนเฉพาะส่วนไหน

**(5) นับแถวในส่วน B**
- ทั้งหมด **33 แถว** (หน้า 12 · API 13 · state 8)
- ยืนยันด้วย 2 ตา **22 แถว**: white + grey 21 (หน้า 12 · API 6 ตัวที่ static เห็น · `/api/recommendations` จาก grep build เอง · cookie `pp_session` · localStorage) · white + black 1 (`/api/health` จาก HEALTHCHECK)
- ตาเดียว (white) **11 แถว**: API `auth/me` · GET `orders` · `orders/[id]` · `products/[slug]` · `test/reset` · state users · sessions · orders · stock · `demoHash` · React state
- ตาที่สองที่ต้องหา (black-box ทั้งหมด เพราะ REA static ยืนยันไม่ได้):
  - API ที่ UI ไม่เรียก: ยิงตรงจากข้างนอก (`Invoke-RestMethod`) ดู status/รูปร่างคำตอบ เช่น `/api/auth/me` ตอนยังไม่ login · GET `/api/orders` ไม่มี cookie ต้องได้ 401 · `orders/[id]` ของคนอื่นต้อง 404 · `products/[slug]` ที่ไม่มีจริงต้อง 404 · `test/reset` (เฉพาะเครื่อง dev)
  - API ที่ UI เรียก (`recommendations`) และตัวที่ static เห็นอยู่แล้ว: HAR / REA ขับเบราว์เซอร์ ดู request จริงพร้อม method
  - state ใน RAM: ดูจากพฤติกรรม — สมัครแล้ว login ได้ (users/sessions) · หลัง reset เลขออเดอร์เริ่ม `PP-100001` (orders) · สั่งซื้อแล้วสต็อกใน `/api/products/[slug]` ลด (stock) · `demoHash` ดูจากข้างนอกได้แค่ "login demo ได้หลัง reset"
  - React state: เปิดเบราว์เซอร์จริง (Playwright) ดูหน้าเปลี่ยนตาม localStorage

## สรุป

| ส่วน | จำนวนแถว | ✅ | ⚠️ | ❓ |
|---|---|---|---|---|
| A · REA เห็นอะไร | 17 | – | – | – |
| B1 · หน้าเว็บ | 12 | 12 | 0 | 0 |
| B2 · API | 13 | 6 | 1 | 6 |
| B3 · state | 8 | 0 | 2 | 6 |
| **B รวม** | **33** | **18** | **3** | **12** |
| C · คำตอบ | 5 ข้อ | – | – | – |

## ยังไม่รู้

- node `electron-renderer` 2 ตัวมาจากไฟล์ไหน (`rea-summarize.mjs` ไม่แสดง และห้ามเปิด JSON ตรง)
- REA เก็บ method ของ endpoint ไว้ใน evidence ไหม (สรุปไม่แสดง)
- `inferred_facts 3` ของ trace คืออะไร
- chunk `components_15s-58tum8e8a._.js` คือ `Header.tsx` จริงไหม (เดาจากโค้ดที่เรียก logout มีที่เดียว)
- container `pawpantry05` ที่รันอยู่ build จากโค้ดชุดเดียวกับ `out\v1` ไหม — ยังไม่ได้เทียบ (ต้องดูตอนรัน/เทียบ bundle)
