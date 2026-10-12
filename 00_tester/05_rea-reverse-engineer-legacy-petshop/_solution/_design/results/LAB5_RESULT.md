# LAB 5_RESULT · BUG-01: ทำซ้ำ → test แดง → หาต้นเหตุ

| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 10:03 · 10:13 · ~10 นาที (เครื่อง ~2.5: สคริปต์ black-box 84 s · spec 8 s · วิดีโอ ~10 s · agent ~7.5) |
| cwd ของเซสชัน / settings มีผลไหม | runner (Agent tool) cwd ไม่ใช่ `w/` → `w/CLAUDE.md` + `.claude/settings.json` **ไม่ได้ถูกบังคับโดย harness · runner ทำตามเอง** (เขียนเฉพาะไฟล์ใหม่ใน `tests/new/` `rea\scratch\` `out\` และ `BUG-01.md`) |
| ไฟล์ที่สร้าง/แก้ | `BUG-01.md` (102 บรรทัด · 7 หัวข้อ `##` = 6 หัวข้อที่สั่ง + ยังไม่รู้) · `e2e-legacy/tests/new/bug01-shipping.spec.ts` (147 บรรทัด · 9 test) · `out\bug01.har` (40,452,170 B · 2,447 entries) · `out\bug01-blackbox.json` (7,856 B) · `out\bug01-<กรณี>-{cart,checkout,order}.png` 21 ไฟล์ |
| สคริปต์ชั่วคราว | `rea\scratch\bug01.mjs` (105 บรรทัด · 7 กรณี + HAR) · `rea\scratch\bug01-har.mjs` (12 บรรทัด · อ่าน body POST /api/orders จาก HAR) · `../tools/lab5/video.config.ts` (runner เท่านั้น · อัดวิดีโอ) · log `../tools/lab5/{bug01-run,spec-red,video-run}.txt` |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · PowerShell tool สำหรับ node/npx ตามพรอมต์ · Git Bash สำหรับ grep/อ่านไฟล์/ffprobe (อ่านอย่างเดียว) |
| timeout / รันซ้ำ | ไม่มีคำสั่งยาว · ไม่มีการสั่งซ้ำเพราะ timeout · spec รัน 1 รอบ (+1 รอบเฉพาะข้อหลักเพื่ออัดวิดีโอ) |
| สถานะเว็บ | pawpantry05 Up 49 min (healthy) · `/api/health` → `{"ok":true}` · ไม่ได้ rebuild (LAB นี้ห้ามแก้ petshop/) |
| ข้อมูลทดสอบ | reset 3 ครั้ง (bug01.mjs 1 · global-setup ของ Playwright 2) · ผู้ใช้สุ่มใหม่ทุกครั้ง (`bug01-…@test.dev` / `buyer-…@test.dev`) · ไม่ใช้บัญชี demo |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)

- ✅ ไม่แก้ `petshop/` · ไม่แก้ไฟล์เดิมใน `e2e-legacy/` · ไม่เปิด `_solution/` · `git diff --stat -- e2e-legacy TEST-DATA.md petshop` = ว่าง · ไม่มีการเลี่ยง deny ผ่าน shell
- ✅ **ขั้นที่ 1–2 black-box จริง**: ไม่เปิดไฟล์ใน `petshop/` และไม่อ่าน CODEBASE-MAP ส่วน D จนจบขั้นที่ 2 (เปิด CODEBASE-MAP แค่ `grep "^#"` ดูชื่อหัวข้อ) · ราคาสินค้าหาจาก `GET /api/products` (black-box) · locator ยืมจาก `tests/fixtures.ts` + `tests/new/char-money.spec.ts` (ไม่ใช่โค้ดเว็บ)
- ⚠️ **รู้ต้นเหตุก่อนขั้นที่ 3 ไหม (หน้าที่ RUNNER)** — **runner รู้แล้ว** ไม่ใช่จากการเปิดโค้ด แต่จาก:
  1. `RUNNER.md` ตารางตรวจก่อน LAB 0 มี `grep -c "PP-231" petshop/lib/orders.ts` = 1 ("อบ BUG-01") → รู้ไฟล์ + ชื่อตั๋วตั้งแต่ก่อนเริ่ม
  2. หัวข้อ 🎯 ของ LAB 5 ใน PROMPTS.md (RUNNER อนุญาตให้อ่าน) บอกต้นเหตุครบ: บล็อก PP-231 ใน `lib/orders.ts` ใช้ `>` vs `shippingCost()` `>=` + วิธี A/B
  3. ไฟล์จาก LAB ก่อนใน `w/`: `BASELINE.md` S1 + `char-money.spec.ts` TC-CHAR-SHIP-02/03 ให้**อาการ**ครบ (฿999 → server ค่าส่ง 50 ยอด 1049) แต่ไม่มีไฟล์:บรรทัด · `CLAUDE.md` ใบ้ว่า "กฎหลายข้อถูกเขียนซ้ำหลายที่ ดูส่วน D"
  4. **CODEBASE-MAP ส่วน D (เขียนใน LAB 1) มีต้นเหตุตรงตัว** — `lib/orders.ts:63-67` ใช้ `subtotal > FREE_SHIPPING_MIN` + คอมเมนต์ PP-231 + "server เขียนกฎซ้ำ" (ยืนยันหลังเปิดในขั้นที่ 3) → Agent ของผู้เรียนที่โหลด D หรือจำจากเซสชัน LAB 1 จะรู้ไฟล์:บรรทัดก่อนขั้นที่ 3 แน่นอน ข้อห้าม "ยังไม่ใช้ส่วน D" จึงสำคัญจริง
  - ผลต่อการรัน: ตาราง black-box ทำจากการรันจริงทั้งหมด (ไม่ได้ใช้ 🎯 เป็นคำตอบ) · ค่าที่ได้ตรง 🎯 ทุกแถว
- ✅ HAR อัดที่ `http://127.0.0.1:4000` (ตามคำสั่งผู้สั่งงาน/D7 เพราะ REA ไม่รับ HAR ที่อัดผ่าน localhost) ต่างจากพรอมต์ที่เขียน localhost → ดูข้อเสนอแก้พรอมต์
- ✅ ไม่ไปหาเลขคำสั่งซื้อของลูกค้าในเครื่องทดสอบ

## คำตอบสรุปที่แสดงในแชท

> | กรณี | ตะกร้า | ปุ่ม | คำสั่งซื้อ (response · หน้าคำสั่งซื้อ · /account) | ถูกไหม |
> |---|---|---|---|---|
> | ฿999 ส่งธรรมดา (ตะกร้าคุณนุ่น: ไม้ตกแมว 1 + ชามกินช้า 3) | ฟรี · ฿999 | ฿999 | ค่าส่ง ฿50 · **฿1,049** | ❌ |
> | ฿998 ส่งธรรมดา | ฿50 · ฿1,048 | ฿1,048 | ฿50 · ฿1,048 | ✅ |
> | ฿1,000 ส่งธรรมดา | ฟรี · ฿1,000 | ฿1,000 | ฟรี · ฿1,000 | ✅ |
> | ฿999 + PAW10 | ลด ฿99 · ฟรี · ฿900 | ฿900 | ฿50 · **฿950** | ❌ |
> | ฿999 + FREESHIP | ฟรี · ฿999 | ฿999 | ฟรี · ฿999 | ✅ |
> | ฿999 ส่งด่วน | ฟรี · ฿999 (ตะกร้ายังเลือกด่วนไม่ได้) | ฿1,119 | ฿120 · ฿1,119 | ✅ |
> | ฿998 + PAW10 | ลด ฿99 · ฿50 · ฿949 | ฿949 | ฿50 · ฿949 | ✅ |
>
> ต้นเหตุ: `petshop/lib/orders.ts:63-67` (บล็อก `// PP-231`) คำนวณค่าส่งซ้ำด้วย `subtotal > 999` แล้วเขียนทับ `totals.shipping`/`totals.total` ขณะที่กฎจริง `lib/pricing.ts:130-133 shippingCost()` ใช้ `>=` · HAR: POST /api/orders ส่งแค่ `items{slug,size,qty} coupon shipping payment address` ไม่มีค่าส่ง/ราคา → คอมเมนต์ "must not trust the shipping fee shown in the browser" ไม่จริง · แนะนำวิธี A ลบบล็อกซ้ำ (+ import ที่ไม่ใช้) · test BUG-01 แดง 3 / เขียว 6 · `char-money` TC-CHAR-SHIP-02 (legacy-quirk) ล็อกค่าผิดไว้แล้ว + SHIP-03 (KNOWN-ISSUE `test.fail()`)

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)

| ค่า | ผล | คำสั่ง |
|---|---|---|
| กรณีที่ทดสอบ black-box | 7 (ผิด 2: ฿999 ส่งธรรมดา · ฿999+PAW10) | `node rea\scratch\bug01.mjs` → `out\bug01-blackbox.json` |
| HAR | 40,452,170 B · 2,447 entries · POST /api/orders 7 ครั้ง (status 201 ทุกครั้ง) | `node rea\scratch\bug01-har.mjs out\bug01.har` |
| field ใน body POST /api/orders | `items,coupon,shipping,payment,address` · items = `{slug,size,qty}` เท่านั้น (ไม่มีราคา/ค่าส่ง/ยอด) | เหมือนบน |
| spec chromium | **3 failed · 6 passed · 7.2 s** (reporter list) | `npx playwright test tests/new/bug01-shipping.spec.ts --project=chromium --reporter=list` |
| เหตุผลที่แดง | ข้อหลัก: server `{shipping:50,total:1049}` ≠ `{0,999}` · หน้าคำสั่งซื้อ ฿50/1049 · /account 1049 ≠ 999 · ปุ่ม=คำสั่งซื้อ ฿999: 1049 ≠ 999 · ปุ่ม=คำสั่งซื้อ PAW10: 950 ≠ 900 (เงินทั้งหมด · ไม่มี timeout/locator) | `../tools/lab5/spec-red.txt` |
| วิดีโอข้อหลัก (แดง) | 1280×800 · 143 เฟรม @25 fps = 5.72 s · 690,061 B | `ffprobe -count_packets …` |

## คำสั่งที่รัน

| คำสั่ง (จาก `w/`) | exit | เวลา | ขนาดผล |
|---|---|---|---|
| `node rea\scratch\bug01.mjs` (reset → 7 กรณี · recordHar) | 0 | 84 s | HAR 40.5 MB · json 7.9 KB · png 21 ไฟล์ |
| `node rea\scratch\bug01-har.mjs out\bug01.har` | 0 | <2 s | stdout 7 แถว |
| `cd e2e-legacy; npx playwright test tests/new/bug01-shipping.spec.ts --project=chromium --reporter=list` | 1 (แดงตามตั้งใจ) | 8 s (test 7.2 s) | – |
| (runner) `npx playwright test -c ..\..\tools\lab5\video.config.ts --grep "ลูกค้าคุณนุ่น"` | 1 (แดงตามตั้งใจ) | ~10 s | `../design/shots/lab5-bug01.webm` 690 KB |
| REA / docker | ไม่ได้ใช้ (LAB นี้ไม่สั่ง) | – | – |

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)

- ตะกร้าคุณนุ่น ฿999: ตะกร้า "ได้ส่งฟรีแล้ว!" ฿999 · ปุ่ม "ยืนยันสั่งซื้อ ฿999" · response `{subtotal 999, discount 0, shipping 50, total 1049}` · /account แถว ฿1,049
- ฿999 + PAW10: ปุ่ม ฿900 → คำสั่งซื้อ ฿950 (บั๊กเดียวกัน ส่วนลดไม่ช่วย)
- ฿998 → ฿1,048 ทุกจุด · ฿1,000 → ฟรีทุกจุด (ผิดเฉพาะ ฿999 พอดี = ค่าขอบ `>` vs `>=`)
- HAR body: `{"coupon":null,"shipping":"standard","payment":"cod"}` + items `{slug,size,qty}` — ไม่มีค่าส่งให้ "ไม่เชื่อ"
- `orders.ts:65` `totals.subtotal > FREE_SHIPPING_MIN ? 0 : STANDARD_SHIPPING` vs `pricing.ts:132` `subtotal >= FREE_SHIPPING_MIN ? 0 : STANDARD_SHIPPING`

## ตัดสินแทนผู้เรียน

| คำถาม | คำตอบ | ที่มา | เหตุผล |
|---|---|---|---|
| (LAB 5 ไม่มีหัวข้อ 🧑 · ไม่มีจุดถาม) | – | – | – |
| ค่าที่ถูกของ ฿999 + PAW10 ตาม [D] | ไม่ล็อกตัวเลข · ใช้กฎ "ปุ่ม = คำสั่งซื้อ" แทน และเขียนใน "ยังไม่รู้" (ส่งฟรีนับก่อน/หลังส่วนลด · ปัด 99.90) | ตัดสินเอง | TEST-DATA ไม่บอก · พรอมต์ห้ามเดาและห้ามลอกจากเว็บ |
| ตะกร้า "สูงกว่า 1 บาท" | ฿1,000 = ลูกสุนัขแกะบด 1 + สตูว์เนื้อ 400 g × 2 + เชือกกัด 1 + หนังแซลมอน 2 + ทูน่าแพ็ค 12 × 1 | ตัดสินเอง (หาจาก /api/products) | ไม่มีสินค้า ฿1 ให้เติม |
| ตะกร้าข้างเคียงใน spec ใช้ของอะไร | ข้อหลักใช้ตะกร้าลูกค้าตรงตัว · ข้ออื่นใช้ ฿999 ชุดอื่น (ทูน่า/ลูกสุนัข) | ตัดสินเอง | ชามกินช้ามีสต็อก 18 หลัง reset (3 ใบ/คำสั่งซื้อ) · ชุด legacy+char-money รันขนานไม่ reset ระหว่างกัน |
| ที่วาง BUG-01.md | รากบท `w/BUG-01.md` | ตัดสินเอง | พรอมต์ไม่ระบุ · ข้าง CODEBASE-MAP/BASELINE |
| HAR ใช้ host ไหน | `http://127.0.0.1:4000` | ผู้สั่งงาน + BRIEF D7 | REA ไม่รับ HAR ที่อัดผ่าน localhost |

## ข้อสังเกต 👀

- ชุดไฟล์ที่ผู้เรียนสร้างใน LAB 1/4 ทำให้ "black-box" ของ LAB 5 แทบเป็นพิธีกรรม: BASELINE S1 + TC-CHAR-SHIP-02 บอกอาการครบ และ CODEBASE-MAP D บอกไฟล์:บรรทัด — คุณค่าของขั้นที่ 1 จึงอยู่ที่ **หลักฐานใหม่** (ตะกร้าลูกค้าตรงตัว · /account · ค่าขอบ ฿1,000 · PAW10 · HAR) ไม่ใช่การค้นพบ
- กรณี PAW10 ที่ ฿999 เผยว่า [D] กำกวม (ส่งฟรีนับก่อน/หลังส่วนลด) → test แบบ invariant "ปุ่ม = คำสั่งซื้อ" แดงได้โดยไม่ต้องเดากฎ เป็นเทคนิคที่ดีสำหรับ README
- ข้อ "ปุ่ม = คำสั่งซื้อ · ฿999 ส่งด่วน" เขียวเพราะบล็อก PP-231 ถูกข้ามเมื่อส่งด่วน — ตรงกับโค้ด `orders.ts:64` ทุกจุด
- หลังแก้ใน LAB 6 จะมี 2 สัญญาณจาก LAB 4: TC-CHAR-SHIP-02 (legacy-quirk) แดง และ TC-CHAR-SHIP-03 รายงาน "expected to fail but passed" → ผู้เรียนต้องปลด/แก้ test ใหม่ของตัวเอง (ไม่ใช่ test เดิม) เป็นจุดสอนที่ดี
- HAR มีรหัสผ่านของผู้ใช้ทดสอบ (register ผ่าน `page.request`) — `.gitignore` กัน `out/` และ `*.har` อยู่แล้ว

## ปัญหา / วิธีแก้

- ไม่มีปัญหาที่ขวางงาน · ชามกินช้าเหลือสต็อก 9 ก่อนเริ่ม (LAB 4 ใช้ไป) → สคริปต์ reset ก่อนรัน
- วิดีโอสั้น 5.7 s แม้ตั้ง `slowMo: 250` ใน `launchOptions` ของ project (ดูทันแต่เร็ว · ถ้าผู้ทำ GIF ต้องการช้าลงให้ชะลอตอนแปลง)

## ข้อเสนอแก้พรอมต์

| ระดับ | ข้อเสนอ |
|---|---|
| M | ขั้นที่ 1 เขียน "บน http://localhost:4000 … บันทึก HAR" แต่ D7 ให้ HAR อัดที่ `127.0.0.1:4000` (REA ไม่รับ localhost) → ถ้า LAB ถัดไปจะเอา `out\bug01.har` เข้า REA ให้ระบุ `http://127.0.0.1:4000` ในพรอมต์ |
| M | HAR ทั้ง run ใหญ่ 40 MB (2,447 entries ส่วนใหญ่เป็น static/RSC) → แนะนำ `recordHar: { path, urlFilter: /\/api\// }` หรือ `mode: 'minimal'` ในพรอมต์ |
| m | ระบุที่วาง `BUG-01.md` (รากบท) |
| m | กรณี PAW10 ที่ ฿999: TEST-DATA ไม่บอกว่าส่งฟรีนับก่อน/หลังส่วนลดและปัดเศษอย่างไร → พรอมต์อาจใบ้ให้ใช้ invariant "ปุ่ม = คำสั่งซื้อ" สำหรับกรณีที่ [D] ไม่พอ (ตอนนี้ agent ต้องคิดเอง) |
| m | เตือนเรื่องสต็อกชามกินช้า 18 ใบ (3 ใบ/คำสั่งซื้อ) ถ้าผู้เรียนรันตะกร้าลูกค้าหลายรอบโดยไม่ reset จะได้ 409 "สินค้าไม่พอ" |
| m | ถ้าอยากให้ black-box มีความหมาย ควรบอกตรง ๆ ว่า "BASELINE/char-money รู้อาการแล้ว — ขั้นนี้ต้องหาหลักฐานเพิ่ม (ตะกร้าลูกค้า · /account · HAR)" |

## ภาพที่ควรใช้ใน README

- `../design/shots/lab5-cart-free.png` (1280×800) — ตะกร้าคุณนุ่น ฿999 "ได้ส่งฟรีแล้ว!"
- `../design/shots/lab5-button-999.png` (1280×800) — checkout ปุ่ม "ยืนยันสั่งซื้อ ฿999"
- `../design/shots/lab5-order-1049.png` (1280×800) — หน้าคำสั่งซื้อ ค่าส่ง ฿50 ยอด ฿1,049
- `../design/shots/lab5-bug01.webm` (1280×800 · 5.7 s) — test BUG-01 ข้อหลักตอนแดง (แปลงเป็น GIF ทีหลัง)
