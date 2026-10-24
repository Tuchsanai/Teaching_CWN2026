# LAB 8_RESULT · ทำ CR-01 + regression 3 เบราว์เซอร์

| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 10:26 · 10:42 · ~16 นาที (เครื่อง ~7.5: build 11 วิ · test:all 244 วิ · รันแยก 3 เบราว์เซอร์ 25+38+68 วิ · TC-GIFT 2 รอบ ~15 วิ · API/ภาพ/วิดีโอ ~20 วิ · agent ~8.5) |
| cwd ของเซสชัน / settings มีผลไหม | runner cwd ≠ `w/` (โหมด A) → `w/CLAUDE.md` และ `w/.claude/settings.json` **บังคับเอง** · ทุกคำสั่งรันจาก `C:\t\work\run05\w` |
| ไฟล์ที่สร้าง/แก้ | แก้ `petshop/` 6 ไฟล์ (เทียบ out\v1: +61 −15 · ส่วน CR-01 อย่างเดียว +60 −8) · `CR-01.md` เพิ่มหัวข้อ "6 · ทำแล้ว" (168 บรรทัดรวม) · สร้าง `rea/scratch/lab8-api.mjs` `rea/scratch/lab8-shot.mjs` · `out/shots/lab8-checkout-giftwrap.png` |
| สคริปต์ชั่วคราว | `rea\scratch\lab8-api.mjs` · `rea\scratch\lab8-shot.mjs` (ตามพรอมต์) · `../tools/lab8/edit2.py` (สคริปต์แก้โค้ดของ runner แทน Edit tool) · `../tools/lab8/count.py` (นับผล list reporter) · `../tools/lab8/gift-boundary-video.mjs` (วิดีโอ) · log ทั้งหมดใน `../tools/lab8/` |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · คำสั่งของพรอมต์ (docker compose · npx playwright · npm run test:all · node scratch · git diff --no-index) รันด้วย **PowerShell tool** · อ่านไฟล์/grep/นับผลด้วย Git Bash |
| timeout / รันซ้ำ | build และ test:all ตั้ง timeout 15 นาที (foreground) · ไม่มีการสั่งซ้ำระหว่างรอ · test:all รอบเดียวล้ม 46 ข้อ (สต็อกหมด) → รันแยกเบราว์เซอร์ 3 รอบ (ตัดสินเอง ดูด้านล่าง) |
| สถานะเว็บ | pawpantry05 healthy · build ล่าสุด 10:28 (03:28Z) · **เปิดค้างไว้** |
| ข้อมูลทดสอบ | reset 8 ครั้ง (global-setup 6 รอบ · ด้วยมือ 1 ครั้งหลังวัดสต็อก · `lab8-api.mjs` 1 ครั้ง) · ผู้ใช้ใหม่สุ่มทุก test/สคริปต์ ไม่ใช้บัญชี demo |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)

- ไม่แก้ไฟล์เดิมใน `e2e-legacy/` / `TEST-DATA.md`: `git diff --stat -- e2e-legacy TEST-DATA.md` = ว่าง (0 บรรทัด) ทั้งก่อนเริ่มและตอนจบ · ไม่มีการเขียนไฟล์ต้องห้ามผ่าน shell
- ไม่แก้ `tests/new/cr01-giftwrap.spec.ts` เลย (SHA-256 `f5b65690…` ตรงกับตอนเริ่ม · `sha256sum -c` = OK) · ไม่รัน `-u` · ไม่เปิด `_solution/`
- สคริปต์ชั่วคราวที่พรอมต์สั่งอยู่ใน `rea\scratch\` · ของ runner อยู่ `../tools/lab8/` · ไม่ใช้ Playwright MCP (headless ทั้งหมด)
- ไม่มี git ที่เปลี่ยนสถานะ (ใช้แค่ `git diff` / `git diff --no-index` / `git status`)
- **พลาด 1 ข้อ (กติกา runner):** ตอนคัดบล็อก ```text ของ LAB 8 ด้วย awk ผลพิมพ์เกินบล็อกไปถึง 🧑 และ 🎯 จึงเห็น 🎯 ก่อนรัน · ตัวเลขทุกตัวในไฟล์นี้มาจากการรันจริง (ตัวเลขรวมบรรทัด CR-only ครั้งแรกเขียนผิดเป็น −9 ตาม 🎯 แล้วนับใหม่ได้ −8 แก้ใน CR-01.md แล้ว)

## คำตอบสรุปที่แสดงในแชท

> | ชุด | chromium | firefox | webkit |
> |---|---|---|---|
> | ชุดเดิม `tests/*.spec.ts` (40) | 40/40 ✅ | 40/40 ✅ | 40/40 ✅ |
> | `tests/new/` bug01 + char-money (16) | 16/16 ✅ | 16/16 ✅ | 16/16 ✅ |
> | `tests/new/cr01-giftwrap.spec.ts` (21) | 21/21 ✅ | 21/21 ✅ | 21/21 ✅ |
> | รวม (รันทีละเบราว์เซอร์ · reset ต้นทุกรอบ) | 77/77 · 23.7 วิ | 77/77 · 36.5 วิ | 77/77 · 1.1 นาที |
> | `npm run test:all` รอบเดียว 3 เบราว์เซอร์ | 77/77 | 63/77 | 45/77 |
> | ยิง API ตรง (POST + GET /api/orders/[id]) | 18/18 ✅ | – | – |
>
> `test:all` รอบเดียวล้ม 46/231 เพราะ **สต็อกหมด** (`409 สินค้าไม่พอ: ลูกแมว สูตรแซลมอน` · `qty-plus` disabled) ไม่ใช่เว็บผิด: ลูกแมวแซลมอนใช้ 20 ชิ้นต่อเบราว์เซอร์ × 3 = 60 > สต็อก 25 → รันแยกเบราว์เซอร์แล้วเขียวครบ

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)

| รายการ | ค่า | คำสั่ง/ที่มา |
|---|---|---|
| TC-GIFT chromium หลัง build รอบแรก | 21 passed (6.3 s · wall 8 s) | `gift-chromium-1.log` |
| `npm run test:all` รอบเดียว | 185 passed · 46 failed (4.0 m · wall 244 s) | `testall-1.log` บรรทัด "46 failed" "185 passed" |
| แยกตามเบราว์เซอร์ใน test:all | chromium ok 77 · firefox ok 63 / x 14 (cr01 ทั้งหมด) · webkit ok 45 / x 32 (เดิม 4 · bug01 4 · char-money 5 · cr01 19) | `python count.py testall-1.log` + รายการ `N) [browser]` |
| ชุดเดิมที่ล้มใน webkit (รอบเดียว) | TC-CART-01 · TC-CPN-03 · TC-REC-01 · TC-REC-04 (ทุกข้อ timeout ที่ `qty-plus` disabled / สินค้าหมด) | `testall-1.log` |
| รันแยก chromium / firefox / webkit | 77/77 (23.7 s · wall 25) · 77/77 (36.5 s · wall 38) · 77/77 (1.1 m · wall 68) | `all-<browser>.log` |
| passed / failed / expected-fail / flaky (รันแยก) | chromium 77/0/0/0 · firefox 77/0/0/0 · webkit 77/0/0/0 | `count.py` · ไม่มี `test.fail()` เหลือใน tests/new (grep) · `retries: 0` จึงไม่มีป้าย flaky |
| flaky → `--repeat-each=3` | ไม่ต้องรัน (ไม่มี flaky · ข้อล้มในรอบเดียวล้มแบบ deterministic จากสต็อก และเขียวเมื่อ reset) | — |
| สต็อกที่ใช้ต่อ 1 รอบเบราว์เซอร์ (reset → ชุดเต็ม chromium → `/api/products`) | `kitten-salmon-dry` 20/25 (cr01 อย่างเดียว 16) · `puppy-lamb-wet` 15/40 · `dog-slow-bowl` 8/18 → ×3 เกินสต็อกทั้ง 3 ตัว | `stock-seed.json` vs `stock-after-chromium.json` / `stock-after-cr01.json` |
| diff ต่อไฟล์ (vs out\v1) | pricing 15/2 · orders 6/8 · store 2/0 · OrderSummary 11/3 · CheckoutForm 19/2 · orders/[id]/page 8/0 = +61 −15 · ทุกไฟล์ exit 1 | `git diff --no-index --numstat` ทีละไฟล์ |
| ส่วน CR-01 อย่างเดียว | +60 −8 (orders.ts CR = +5 −1 · BUG-01 = +1 −7) | อ่าน diff ของ orders.ts |
| ยิง API ตรง | 18/18 ตรงตาราง ทั้ง response และ GET (รวมข้อปลอม `giftWrapFee:0,total:1` ใน body → server ยังคิด 269) | `node rea\scratch\lab8-api.mjs` → `../tools/lab8/api.md` |
| ภาพ checkout | subtotal ฿1,499 · ค่าส่ง ฟรี · ห่อ ฿30 · total ฿1,529 · ปุ่ม "ยืนยันสั่งซื้อ ฿1,529" | stdout `lab8-shot.mjs` |
| วิดีโอค่าขอบ | TC-GIFT-03 ฿1,499 → ห่อ ฿30 ยอด ฿1,529 (checkout+ปุ่ม+หน้าออเดอร์) ok · TC-GIFT-04 ฿1,500 → ห่อ ฟรี ยอด ฿1,500 ok · 1,422,304 bytes · 13 วิ | stdout `gift-boundary-video.mjs` |

## คำสั่งที่รัน (REA/docker/playwright: คำสั่ง | exit | เวลา | ขนาดผล)

| คำสั่ง (PowerShell จาก `w/`) | exit | เวลา | ผล |
|---|---|---|---|
| `cd petshop; docker compose up -d --build` | 0 | 11 s | `next build` Compiled 1.7 s + TypeScript 2.4 s · ชั้นอื่น CACHED · log 132 บรรทัด `build1.log` |
| `cd e2e-legacy; npx playwright test tests/new/cr01-giftwrap.spec.ts --project=chromium --reporter=list` | 0 | 8 s | 21 passed |
| `cd e2e-legacy; npm run test:all -- --reporter=list` | 1 | 244 s | 185 passed · 46 failed |
| `npx playwright test --project=chromium --reporter=list` (ชุดเต็ม) | 0 | 25 s | 77 passed |
| `npx playwright test tests/new/cr01-giftwrap.spec.ts --project=chromium` (วัดสต็อก) | 0 | ~7 s | 21 passed |
| `npx playwright test --project=firefox --reporter=list` | 0 | 38 s | 77 passed |
| `npx playwright test --project=webkit --reporter=list` | 0 | 68 s | 77 passed |
| `node rea\scratch\lab8-api.mjs` | 0 | ~2 s | 18/18 |
| `node rea\scratch\lab8-shot.mjs` | 0 | ~5 s | `out\shots\lab8-checkout-giftwrap.png` 124,335 B |
| `node ..\tools\lab8\gift-boundary-video.mjs` (runner) | 0 | 13 s | `../design/shots/lab8-gift-boundary.webm` 1,422,304 B |
| `git diff --no-index --numstat out\v1\<ไฟล์> petshop\<ไฟล์>` × 6 | 1 ทุกไฟล์ | – | ตารางบน |
| `git diff --stat -- e2e-legacy TEST-DATA.md` | 0 | – | ว่าง |

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)

| จุด | ค่า |
|---|---|
| TC-GIFT-03 ค่าขอบ ฿1,499 ห่อ | checkout/ปุ่ม/response/หน้าออเดอร์ = ฿1,529 (ห่อ ฿30) |
| TC-GIFT-04 ค่าขอบ ฿1,500 ห่อ | ทุกจุด ฿1,500 (ห่อ "ฟรี" · `giftWrapFee:0`) |
| TC-GIFT-12 `giftWrap:"true"` / `1` / `"yes"` / `null` | `giftWrap:false giftWrapFee:0 total:239` (ไม่แปลงชนิด) |
| ปลอมเงินใน body `{"giftWrap":true,"giftWrapFee":0,"total":1}` | server คืน `giftWrapFee:30 total:269` (ไม่เชื่อ browser) |
| `test:all` รอบเดียว | 185/231 · ล้ม 46 เพราะสต็อกลูกแมวแซลมอนหมด (20 × 3 > 25) |
| รันแยกเบราว์เซอร์ | 77/77 × 3 = 231/231 |

## ตัดสินแทนผู้เรียน (คำถาม | คำตอบ | ที่มา 🧑/ตัดสินเอง | เหตุผล)

| คำถาม | คำตอบที่ใช้ | ที่มา | เหตุผล |
|---|---|---|---|
| ข้อ 1 แผน 6 ไฟล์ (pricing · orders · store · OrderSummary · CheckoutForm · app/orders/[id]/page) ตรงตาราง impact · อนุมัติไหม | อนุมัติ | 🧑 | แผนมี `app/orders/[id]/page.tsx` และกฎค่าห่ออยู่ใน `lib/pricing.ts` ที่เดียว → ไม่เกิดกรณี "หน้า /orders/[id] แสดงเงินจากไหน ตรวจก่อน" |
| ข้อ 3 TC-GIFT ล้มไหม เว็บผิดหรือ test ผิด | ไม่ล้ม (21/21 รอบแรก) → ไม่ต้องตัดสิน | – | – |
| ข้อ 4 `test:all` ล้ม 46 ข้อ "หยุดบอกผม" → ทำอย่างไรต่อ | วินิจฉัยก่อน: **ไม่ใช่เว็บผิด ไม่ใช่ผลคาดหวังผิด** แต่สต็อกที่ reset ครั้งเดียวไม่พอ 3 เบราว์เซอร์ · พิสูจน์ด้วยการวัดสต็อก แล้ว **รันชุดเต็มแยกทีละเบราว์เซอร์** (global-setup reset ทุกรอบ) โดยไม่แก้ไฟล์ test/config | ตัดสินเอง | แก้ตะกร้าใน spec = เปลี่ยนผลที่คาดหวัง (ห้าม) · แก้ config/global-setup = ไฟล์เดิมห้ามแตะ · รันแยกเป็นวิธีที่ไม่แตะอะไรและยังครอบคลุมทุกข้อทุกเบราว์เซอร์ · บันทึกไว้ใน CR-01.md ให้เจ้าของชุดทดสอบตัดสินวิธีแก้ถาวร |
| ภาพข้อ 6 ใช้ตะกร้าไหน | ฿1,499 (ห่อ ฿30 · ส่งฟรี) | ตัดสินเอง | เห็นแถวห่อเป็นเงินและยอดรวมค่าห่อชัด · เป็นค่าขอบเดียวกับวิดีโอ |

## ข้อสังเกต 👀 (บทเรียนจากรอบจริง ไม่ใช่สรุปผลซ้ำ)

- **test ใหม่ที่เขียวบน chromium อาจทำให้ชุดเดิมแดงบนเบราว์เซอร์อื่น:** ชุดเดิม webkit 4 ข้อ (TC-CART-01 · TC-CPN-03 · TC-REC-01/04) ล้มเพราะ test ใหม่ของ CR-01 กินสต็อกลูกแมวแซลมอนไปก่อน ไม่ใช่เพราะโค้ด CR-01 · ถ้าอ่านแค่ "ชุดเดิมแดงหลังแก้" จะเข้าใจผิดว่าแก้โค้ดแล้วพังของเดิม — ต้องอ่านข้อความ error (409 สินค้าไม่พอ) ก่อนตัดสิน
- LAB 7 เขียนใน CR-01.md ว่า "ทุกตะกร้าซื้อได้จริง (สต็อกหลัง reset พอ)" แต่ตรวจแค่ 1 เบราว์เซอร์ · ใน LAB 4 runner เคยคิดเรื่องนี้ (ชามกินช้า 27 > 18) แต่ LAB 7 ใช้ลูกแมวแซลมอน ฿189 เป็นตะกร้าหลักของ API 10 ข้อ (×1–2 ชิ้น) → 16 ชิ้น/เบราว์เซอร์
- `puppy-lamb-wet` (15/40) และ `dog-slow-bowl` (8/18) ก็เกินเมื่อ ×3 แต่ไม่ทำให้ล้มในรอบนี้ (ข้อที่ใช้อาจรันก่อนสต็อกหมด หรือใช้แค่ใส่ตะกร้า) — เป็นระเบิดเวลาของชุด tests/new
- BUG-01 ใน LAB 6 แก้ที่ต้นเหตุ (ลบสูตรค่าส่งซ้ำใน `orders.ts` ให้ `computeTotals` เป็นที่เดียว) ไม่ใช่เปลี่ยนเครื่องหมาย → กรณี "UI ฿269 แต่คำสั่งซื้อ ฿239" **ไม่เกิด** ในรอบนี้
- build ใช้แค่ 11 วิ (Turbopack + cache ชั้น npm ci) ไม่ใช่ ~3 นาทีตามพรอมต์ · หลัง `compose up` เว็บ healthy ทันที
- diff `out\v1` ↔ `petshop` ของ `lib/orders.ts` รวมการแก้ BUG-01 ด้วย (+1 −7) ต้องแยกเองถ้าจะรายงาน "บรรทัดของ CR-01"
- การ map body → server ทำแค่ `input.giftWrap === true` บรรทัดเดียว ทำให้ TC-GIFT-12/13 (ชนิดผิด) และข้อปลอม fee/total ผ่านโดยไม่ต้องมีโค้ดตรวจเพิ่ม

## ปัญหา / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| `npm run test:all` 46 failed (409 สินค้าไม่พอ · `qty-plus` disabled timeout 45 s) | วัดสต็อกต่อรอบ → ยืนยันว่าสต็อกหมด → รัน `npx playwright test --project=<b>` ทีละเบราว์เซอร์ = 77/77 ×3 · บันทึกใน CR-01.md |
| สคริปต์ Python ที่ต่อท้าย CR-01.md: `out\v1` กลายเป็น `out<VT>1` (escape `\v`) | ตรวจหา control char แล้วแทนกลับเป็น `out\v1` (0 ตัวเหลือ) |
| ตัวนับผล regex ไม่ match เพราะ `\\` ใน heredoc ถูกยุบ | เปลี่ยนเป็น `tests.(new.)?` |

## ข้อเสนอแก้พรอมต์ (ระดับ H = ทำต่อไม่ได้/ผลผิด · M = ได้ผลแต่สับสน · m = ถ้อยคำ)

- **H** · ✔️ "ตาราง 3 เบราว์เซอร์ไม่มีข้อล้ม" ทำไม่ได้ด้วยคำสั่งตรงตัวของข้อ 4 (`npm run test:all` รอบเดียว) ถ้า spec ของ LAB 7 ใช้สินค้าสต็อกน้อยซ้ำ ๆ → ผู้เรียนจะหยุดที่ "ชุดเดิมแดง" ทั้งที่โค้ดถูก · เสนอ: (ก) LAB 7 เพิ่มกติกา "จำนวนชิ้นที่ test ใหม่ซื้อ × 3 เบราว์เซอร์ ต้อง ≤ สต็อกหลัง reset (ดู `/api/products`) · ตะกร้า API ใช้สินค้าสต็อกมาก" และ (ข) LAB 8 ข้อ 4 เพิ่ม "ถ้าล้มด้วย `สินค้าไม่พอ` หรือปุ่ม `qty-plus` กดไม่ได้ = สต็อกหมด ไม่ใช่เว็บผิด → รัน `npx playwright test --project=<เบราว์เซอร์>` ทีละรอบ"
- **m** · ข้อ 7: บอกว่า `lib/orders.ts` เทียบ `out\v1` จะรวมการแก้ BUG-01 ด้วย (ให้แยก +/− ของ CR-01 เอง หรือใช้ `git diff --stat -- petshop` เทียบ commit ตั้งต้นซึ่งก็ยังรวม BUG-01)
- **m** · ข้อ 3: "นาน ~3 นาที" จริง 11 วิ (cache) — เขียน "1–3 นาที" ก็พอ
- **m** · ข้อ 4 ชี้ `--reporter=list` ด้วย (config มี reporter อื่นด้วย) เพื่อให้ผู้เรียนเห็นชื่อข้อและเวลา

## ภาพที่ควรใช้ใน README (../design/shots/labN-*.png 1280×800 + คำอธิบาย 1 บรรทัด)

- `../design/shots/lab8-checkout-giftwrap.png` (คัดจาก `w/out/shots/`) · หน้า /checkout ตะกร้า ฿1,499 ติ๊ก "ห่อของขวัญ" → แถวห่อ ฿30 · ยอดชำระและปุ่ม ฿1,529
- `../design/shots/lab8-gift-boundary.webm` (1280×800 · 13 วิ) · ค่าขอบ ฿1,499 (ห่อ ฿30 → ฿1,529) ต่อด้วย ฿1,500 (ห่อฟรี → ฿1,500) จาก checkout → สั่งซื้อ → หน้าคำสั่งซื้อ (ตอนเขียว)
