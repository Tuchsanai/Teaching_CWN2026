# FT-RESULT — บท 05 fast_track พรอมต์ 🅰️ (บอกใบ้) รันจริงแบบผู้เรียน

ผู้รัน: Claude Code (Opus 5.5) 1 เซสชัน · cwd `C:/t/work/ft05/w` (สำเนาโฟลเดอร์บทตั้งต้น · git repo) · คัดลอกพรอมต์ 🅰️ จาก `fast_track/README.md` บรรทัด 124–185 แล้วทำตามตัวอักษร · คำสั่ง shell ใช้ PowerShell (อ่านไฟล์ภาษาไทยใช้เครื่องมืออ่านไฟล์ เพราะ `cat` ของ PS 5.1 อ่าน UTF-8 ไม่มี BOM เพี้ยน) · พอร์ต 4000 · ไม่ได้เปิด `_solution/` หรือ `C:/t/work/run05`

## เวลา

| เริ่ม | จบ (ขั้น 9 เสร็จ) | ใช้ |
|---|---|---|
| 11:30:37 | 12:15:39 | **~45 นาที** |

รายขั้นโดยประมาณ (จากเวลาเครื่อง): 0 → 11:33 · 1 → 11:38 (Explore subagent 4 นาที ขนานกับ build out\v1) · 2 → 11:41 · 3 → 11:43 · 4 → 11:47 · 5 (subagent ตาใหม่ 6.5 นาที + white-box) → 11:59 · 6 → 12:01 · 7 → 12:05 · 8 → 12:09 · 9 → 12:15
เวลา build จริง: out\v1 168 วินาที · out\v2 161 วินาที · `docker compose up -d --build` หลังแก้โค้ด 10.7 / 11.2 วินาที (มี cache) · test:all ครบชุด 70–102 วินาที

## ไฟล์ที่พรอมต์สร้าง (นับด้วย `wc -l`)

| ไฟล์ | บรรทัด | ขั้น |
|---|---|---|
| CODEBASE-MAP.md | 187 | 1 |
| CLAUDE.md | 37 (≤ 60 ✅) | 1 |
| .claude/settings.json | 11 | 1 |
| SYSTEM-MAP.md | 164 | 2 |
| API-INVENTORY.md | 102 | 3 |
| BASELINE.md | 120 | 4 |
| e2e-legacy/tests/new/char-money.spec.ts | 155 | 4 (แก้คู่ 02a/02b ในขั้น 6) |
| e2e-legacy/tests/new/money-helpers.ts | 76 | 4 (เพิ่ม opt giftWrap ขั้น 7) |
| e2e-legacy/tests/new/golden/products.json · coupons.json | 1,166 · 267 | 4 |
| BUG-01.md | 237 (subagent 91 + ตัวหลัก 146) | 5–6 |
| e2e-legacy/tests/new/bug01-shipping.spec.ts | 121 | 5 (subagent) · ตัวหลักแก้ตะกร้า |
| CR-01.md | 227 | 7–8 |
| e2e-legacy/tests/new/cr01-giftwrap.spec.ts | 135 | 7 |
| CHANGE-PROOF.md | 105 | 9 |
| CHANGE-REPORT.md | 56 | 9 |
| out\ticket-bug01.txt | 5 | 5 |
| โค้ดที่แก้ใน petshop/ | 6 ไฟล์ +60 −21 | 6, 8 |
| out\ (ไม่ commit) | ~47,600 ไฟล์ 1.35 GB (v1, v2 รวม node_modules 533 MB ต่อชุด) · ไฟล์ผลหลัก: v1-static/v1-server/v2-server.json (~54 MB), har.json, scenario.json + scenario-final.png, bug01.har, bug01-*.json/png, char-run1-3.json, baseline-*.json, lab6-*.json, lab8-all.json, cr01-run1/2.json, cr01-api.json, shots\lab8-checkout-giftwrap.png, s2b-*.json ×4, cmp.json, after\, hash-compare.csv | |
| rea\scratch\ (ไม่ commit) | 19 สคริปต์ (pw-sum.mjs, peek-ev.mjs, grep-build.mjs, har-urls.mjs, find-baskets*.mjs, make-golden.mjs, cr01-api.mjs, shot-giftwrap.mjs, hash-compare.ps1, run-s2b.ps1, bug01-*.mjs ของ subagent) | |

ไฟล์เดิมใน e2e-legacy/ และ TEST-DATA.md: `git diff --stat` ว่าง ✅ · `git status`: M 6 ไฟล์ใน petshop + ไฟล์ใหม่ตามตาราง

## ตัวเลขสำคัญ

### ขั้น 0 (ตารางในแชต · บันทึกไว้ที่นี่)

| รายการ | ผล | พร้อมไหม | ต้องทำอะไร |
|---|---|---|---|
| docker version | client/server 29.5.2 | ✅ | — |
| docker compose version | v5.1.4 | ✅ | — |
| node -v | v26.7.0 (≥ 20) | ✅ | — |
| npm -v | 12.2.0 | ✅ | — |
| Get-ExecutionPolicy -List | CurrentUser RemoteSigned · Process Bypass · อื่น Undefined | ✅ | เรียก rea.ps1 ผ่าน -ExecutionPolicy Bypass |
| excludedportrange | 3000 อยู่ในช่วง 2970–3069 (จอง) · 4000 ไม่อยู่ในช่วง | ✅ | ใช้ 4000 |
| พอร์ต 4000 | Get-NetTCPConnection ว่าง · docker ps ไม่มีใครใช้ (มี sabai06-web 4100 · exref-*) | ✅ | — |
| rea-lab:6.4.0 | 2,654,494,021 bytes (~2.65 GB) | ✅ | — |
| REA doctor | **exit 1** · node ✅ host ubuntu 24.04 ✅ · hopper/ghidra/ida-registration = missing_analysis_engine · skill:identity = config_drift | ✅ (ไม่กระทบงานเว็บ: เป็น engine วิเคราะห์ไบนารี + skill) | — |
| compose up -d --build | 2.6 วินาที (image มี cache) · pawpantry05 healthy | ✅ | — |
| localhost:4000/api/health | 200 `{"ok":true}` | ✅ | — |
| network + probe | `pawpantry05_default` มี · `petshop:3000/api/health` จาก container → `{"ok":true}` | ✅ | — |
| npm install e2e-legacy / rea | 7 / 2 packages | ✅ | — |
| playwright install chromium firefox webkit | มีอยู่แล้ว (1.2 วินาที) · Version 1.63.0 | ✅ | — |

### ขั้น 4 · ชุดเดิมต่อเบราว์เซอร์

| ช่วง | chromium | firefox | webkit |
|---|---|---|---|
| ก่อนแก้ (ชุดเดิม 40) | 40/40 (12.9 วินาที) | 40/40 | 40/40 (test:all 72.6 วินาที) |
| ก่อนแก้ ชุดเดิม + char (49) | 49/49 (expected-fail 1) | 49/49 (1) | 49/49 (1) |
| หลังแก้ทั้งหมด (73 = เดิม 40 + char 9 + bug01 7 + cr01 17) | 73/73 | 73/73 | 73/73 (102.5 วินาที) |

### BUG-01 ก่อน/หลัง

| | ก่อน | หลัง |
|---|---|---|
| ตะกร้าลูกค้า 999 (ไม้ตกแมว + ชามกินช้า 3) | ตะกร้า/ปุ่ม ฿999 · API/หน้าคำสั่งซื้อ/account **฿1,049** | ฿999 ทุกจุด |
| กรณีที่ subagent ลอง | 12 กรณี · ผิด 4 (C01 999 · C04 999+PAW10 900→950 · C06 999+NEWCAT50 · C07 999+SUMMER20) | ผิด 0 |
| bug01-shipping.spec.ts (chromium) | 4 ผ่าน / 3 ล้ม (2 รอบ subagent + 1 รอบหลังแก้ตะกร้า) | 7/7 |
| ต้นเหตุ | `lib/orders.ts:63-67` คิดค่าส่งซ้ำด้วย `>` (browser `pricing.ts:132` ใช้ `>=`) · คอมเมนต์ PP-231 ไม่จริง (HAR: browser ไม่ส่งค่าส่ง) | ลบบล็อก (วิธี B) · lib/orders.ts **+2 −13** |
| CHAR-02a/02b | legacy-quirk 1,049 / test.fail KNOWN-ISSUE | ปรับเป็น bug01-fixed (ข้อยกเว้นขั้น 6) |

### CR-01 ขอบเขต

| ขอบ | ตะกร้าจริง | ผล |
|---|---|---|
| ฿1,499 + ห่อ | ขนมแมวเลีย 20 ซอง + ทูน่า แพ็ค 12 ×2 + มูสไก่ แพ็ค 12 | 1,529 (ห่อ 30) |
| ฿1,500 + ห่อ | ลูกสุนัขไก่ 3 kg + ทูน่า แพ็ค 12 + สุนัขพันธุ์เล็ก | 1,500 (ห่อฟรี · ⚠️ ≥ เป็นสมมติฐาน) |
| ฿1,501 + ห่อ | ขนมแมวเลีย 20 ซอง ×3 + ขนมขัดฟัน 28 + ทูน่าซอง ×3 | 1,501 |
| 1,500 + PAW10 + ห่อ | | 1,350 (ดูยอดก่อนหัก → ฟรี) |
| 998 + ห่อ (ไม่นับเข้าส่งฟรี) | | 1,078 |
| giftWrap "true" / 1 / ไม่ส่ง | T69 | false · 0 · 119 |
| TC-GIFT | 17 ข้อ: แดง 17/17 (ยังไม่มีฟีเจอร์) → เขียว 17/17 · POST ยิงตาราง TC 16 กรณี ✅ ทั้งหมด |

### REA เทียบ

| รายการ | ค่า |
|---|---|
| static v1 | ev_21155440 · files 21 · endpoint 9 (6 จริง + a b c minify) · storage 3 (graph node ตรง) · edges 68 · coverage partial · recovered 0 |
| server v1 | ev_f25e3ba6 · files 445 · endpoint 60 (ส่วนมากเป็น header/query) · electron-renderer 2 (`app/_global-error.html` `pages/500.html`) · recovered_source_files 52 · retained_on_file_nodes 94 |
| trace coupons/validate | ev_b4c560ca · matched 13 · nodes 16 · edges 75 · terminal_paths 0 |
| HAR | ev_f386930c · 97 records · API 4 · scenario ev_856107db 11/11 · storage pp-recent pp-cart pp-coupon · completeness incomplete (missing: events) |
| s2b 4 ทิศ | v1↔v1 / v2↔v2: unchanged 44 · modified 0 · removed 0 · split 0 · merged 0 · duplicated 8 · unknown 3 · ข้ามเวอร์ชัน: 41 · 0 · 0 · 0 · 0 · 5 · 9 · 6 ไฟล์ที่แก้ = unknown ข้ามเวอร์ชัน |
| compare-application-versions | ev_bcaa18ba · changed 234 · unknown 1,459 · items_total 1,693 (source-module changed 6) |
| 3 รายการ CHANGE-PROOF | ตั้งใจ 6 = hash ต่าง 6 = bundle ต่าง 6 ✅ · ส่วนเกิน next-env.d.ts (next build เขียนเองใน v1) |
| HAR หลัง | ev_b4e1daf5 · API เดิม 4/4 status เดิม · เพิ่ม `giftWrap` (req) `giftWrap,giftWrapFee` (res) |

### CHANGE-REPORT สรุป
BUG-01 = re-engineering (ลบกฎซ้ำ เปลี่ยนพฤติกรรมที่ 999) · CR-01 = re-engineering (เพิ่มฟีเจอร์) · 6 ไฟล์ +60 −21 · test ใหม่แดง→เขียว: bug01 3→0 แดง · cr01 17→0 แดง · regression 73/73 ×3 · obligation ledger 16 ข้อ ✅13 ⚪3 (items ว่าง 400 · สต็อกไม่พอ 409 · ที่อยู่ผิดฝั่ง server) · rollback: CR-01 ก่อนแล้ว BUG-01 (ใช้ lib/orders.ts ร่วม) จาก out\v1

## ตารางสรุปตอนจบ (ที่พรอมต์สั่งให้แสดงในแชต)

| ขั้น | ไฟล์ที่ได้ | ตัวเลขสำคัญ | ⚠️ ต้องดู |
|---|---|---|---|
| 0 | (ตารางข้างบน) | 14/14 พร้อม · doctor exit 1 | — |
| 1 | CODEBASE-MAP · CLAUDE.md · settings | 99 แถว · เดา 1 · G ⚠️7 ❌2 · deny ทดสอบแล้ว | H1 สมมติฐาน 999 |
| 2 | SYSTEM-MAP · out\v1 | ✅6 ⚠️7 ❓20 | ❓ เยอะเพราะนิยาม ✅ เคร่ง |
| 3 | API-INVENTORY | API 4 · 🟢 8 แถว | pp-wishlist ยังไม่ยืนยัน |
| 4 | BASELINE · char-money · golden | 40/40 ×3 · char 9 · expected-fail 1 | CHAR-02 [E] ขัด [D] |
| 5 | BUG-01 · bug01-shipping | 12 กรณี ผิด 4 · แดง 3/7 | subagent ใช้สต็อกเกิน → แก้ตะกร้า |
| 6 | แก้ lib/orders.ts | +2 −13 · 7/7 · chromium 56/56 | CheckoutForm.tsx:216 เลข 999 ตรง |
| 7 | CR-01 · cr01-giftwrap | Q 10 · impact 6 ไฟล์ · แดง 17/17 | Q2 Q8 Q9 สมมติฐาน |
| 8 | โค้ด 6 ไฟล์ · ภาพ | 17/17 · 73/73 ×3 | — |
| 9 | CHANGE-PROOF · CHANGE-REPORT | 6=6=6 · ✅13 ⚪3 | modified 0 ต้องอ่านกับ hash |

คำถามถึงร้านที่ยังค้าง: Q2 (≥ หรือ > 1,500) · Q8 (ส่งด่วนกับค่าห่อ) · Q9 (จำ/แสดงค่าห่อในตะกร้า) · SUMMER20 ยังใช้ได้ไหม (HANDOVER ขัด TEST-DATA) · ข้อมูลสินค้าแก้ที่ไหน (HANDOVER ❌) · PP-231 คืออะไร · คำสั่งซื้อจริงของคุณนุ่นคืนเงิน ฿50 หรือยัง

## การตัดสินใจแทนผู้เรียน

| ขั้น | เรื่อง | ตัดสิน |
|---|---|---|
| 1 | บันทึก settings.json | บันทึก · ทดสอบ deny: Edit `tests/01-home.spec.ts` และ Write `TEST-DATA.md` ถูกปฏิเสธ · Write ใน `tests/new/` ได้ |
| 2 | ✅ ต้องอยู่ในรายการ endpoint/storage ของ REA | หน้าเว็บทั้งหมด = ❓ (มีแค่ชื่อไฟล์) · recommendations = ❓ แม้ grep เจอ |
| 3 | scenario completeness incomplete | ถือว่าใช้ได้ (11/11) |
| 4 | ชุดเดิมไม่มีข้อล้ม | ไม่ต้องจดข้อล้มของเดิม · CHAR-02 แยกคู่ legacy-quirk/KNOWN-ISSUE · ใส่ตะกร้าผ่าน localStorage |
| 5 | งาน subagent ผิดกติกาข้อ 9 (ชามกินช้า 18/18 + test.skip firefox/webkit) | ตัวหลักเปลี่ยนตะกร้า 02–07 เป็นสินค้าสต็อกมาก ยอดเท่าเดิม ผลที่คาดหวังเท่าเดิม เอา skip ออก · เก็บต้นฉบับใน out\ |
| 6 | วิธีแก้ BUG-01 | B ลบบล็อกคิดซ้ำ (กฎเงินที่เดียว) ไม่ใช่ A (`>`→`>=`) · ไม่แตะ CheckoutForm.tsx:216 |
| 6 | คู่ CHAR-02 | 02a → bug01-fixed ล็อก 999 · 02b เอา test.fail() ออก |
| 7 | คำถามที่ร้านไม่ตอบ | Q2 ≥ 1,500 · Q8 ด่วนไม่มีผล · Q9 ไม่จำ ไม่แสดงในตะกร้า (⚠️) |
| 8 | อนุมัติแผน CR-01 | อนุมัติ (มี /orders/[id] ที่เขียนแถวเอง · กฎค่าห่อใน pricing.ts ที่เดียว) |

## ปัญหาและข้อเสนอแก้พรอมต์

| ระดับ | ปัญหา | หลักฐาน | ข้อเสนอ |
|---|---|---|---|
| **H** | ข้อความที่ส่งให้ subagent ขั้น 5 ไม่มีกติกาข้อ 9 → subagent ใช้ชามกินช้าครบ 18 ใบใน spec เดียว แล้ว `test.skip` บน firefox/webkit (BUG-01 จะไม่ถูกรันใน regression 3 เบราว์เซอร์ และ test:all อาจได้ 409) | out\bug01-shipping.spec.subagent-original.ts | เติมในข้อความ subagent: "test ที่สั่งซื้อจริง จำนวนชิ้นรวม × 3 เบราว์เซอร์ ≤ สต็อกหลัง reset (ดู GET /api/products) · ห้าม test.skip ตามเบราว์เซอร์ · ตะกร้าลูกค้าใช้แค่ 1 test ที่เหลือใช้ตะกร้ายอดเท่ากันจากสินค้าสต็อกมาก" |
| **M** | README fast_track บอก "ราว 3–4 ชั่วโมง" และ "next build 3–4 รอบ รอบละ ~3 นาที" · รอบนี้ใช้ 45 นาที · `docker compose up -d --build` หลังแก้โค้ด ~11 วินาที (cache) มีแค่ out\v1/out\v2 ที่ ~2.7 นาที | เวลาในตาราง | ปรับเป็น "ราว 45 นาที–1.5 ชั่วโมง (แล้วแต่เครื่อง/รุ่นโมเดล)" และ "build out\v1 out\v2 รอบละ ~3 นาที · rebuild เว็บหลังแก้ไม่กี่วินาทีถึง ~3 นาที" |
| **M** | ขั้น 7 สั่ง "เขียนคำถามให้เสร็จก่อนแล้วค่อยอ่านคำตอบร้าน" แต่คำตอบอยู่ท้ายพรอมต์ตั้งแต่ต้น → บังคับไม่ได้ (Claude เห็นแล้ว) | CR-01.md หมายเหตุความโปร่งใส | ให้ subagent ใหม่เขียนตาราง "ต้องถามร้าน" จากใบ CR + CODEBASE-MAP อย่างเดียว (แบบเดียวกับขั้น 5) แล้วตัวหลักค่อยเติมคำตอบ หรือยอมรับและบอกใน README ว่าเป็นข้อจำกัดของ fast track |
| **M** | เบาะแสขั้น 2 ไม่ตรงรอบนี้: static ได้ endpoint 9 + storage 3 เป็น graph node ตรง (ไม่ใช่ 7 / ไม่มี storage) · ที่ชนเพดานคือฝั่ง server (retained_on_file_nodes 94) · completeness ของ scenario บอก "missing: events" ไม่ใช่เรื่อง prefetch | SYSTEM-MAP ② · API-INVENTORY | เขียนเบาะแสเป็น "อาจ…" และบอกให้ดูคอลัมน์ "ที่มา" ทั้ง static และ server · completeness: "อ่านเหตุผลที่ REA ให้ใน missing" |
| m | ตารางขั้น 0 อยู่แค่ในแชต พอเป็นพรอมต์ยาวจะหลุดจากสรุปตอนจบ | — | ให้เขียนตารางขั้น 0 ไว้ต้น CODEBASE-MAP.md หรือรวมในตารางสรุปตอนจบ |
| m | อยากได้ผลแยกเบราว์เซอร์ต้องใช้ JSON reporter แต่ `>` ของ PS 5.1 ได้ UTF-16 (ต้องเขียนตัวอ่านเอง) | rea\scratch\pw-sum.mjs | แนะนำ `$env:PLAYWRIGHT_JSON_OUTPUT_NAME="..\out\x.json"; npx playwright test --reporter=json` หรือให้ rea-summarize อ่านผล Playwright ได้ |
| m | `node -e "..."` ใน PowerShell ที่มี `$1`/regex ถูก PS แปลงเงียบ ๆ (ชื่อ test หายไปครั้งหนึ่ง แก้แล้ว) | ระหว่างขั้น 5 | กติกาข้อ 4 เติม "สคริปต์ node ที่มี $ หรือ regex ให้เขียนเป็นไฟล์ใน rea\scratch\ ห้ามใช้ node -e" |
| m | `cat`/`Get-Content` ของ PS 5.1 อ่านไฟล์ไทย UTF-8 (ไม่มี BOM) เพี้ยน | ขั้น 0 | กติกาข้อ 4 เติม "อ่านไฟล์ด้วยเครื่องมืออ่านไฟล์ของ Claude ไม่ใช่ Get-Content" |
| m | out\ หลังจบ 1.35 GB (v1/v2 มี node_modules) | — | README ส่วน 🔁 บอกขนาดและให้ลบ out\v1\node_modules out\v2\node_modules ได้หลังจบขั้น 9 |

## ค่าสำหรับ placeholder ใน fast_track/README.md

| placeholder | ค่า |
|---|---|
| `RESULT:FT:duration` | รอบจริง 🅰️ ~45 นาที (Opus 5.5 · 11:30–12:15) → เสนอเปลี่ยนข้อความ "ราว 3–4 ชั่วโมง" เป็น "ราว 45 นาที–1.5 ชั่วโมง" |
| `RESULT:FT:LAB0` | พร้อม 14/14 รายการ · doctor exit 1 (hopper/ghidra/ida + skill identity ไม่กระทบเว็บ) · probe `petshop:3000/api/health` ใน network `pawpantry05_default` = `{"ok":true}` |
| `RESULT:FT:LAB1` | CODEBASE-MAP 99 แถว / เดา 1 · หน้า 12 (+layout) · API 13 · ส่วน G ⚠️7 / ❌2 (HANDOVER: ทุกหน้าดึง /api/products · SUMMER20 ลด 20%) |
| `RESULT:FT:LAB2` | static 21 ไฟล์ / endpoint 9 (6 จริง + a b c) / storage 3 / coverage partial · server recovered_source_files 52 · trace 16 node (75 edge) · ส่วน B ✅6 ⚠️7 ❓20 |
| `RESULT:FT:LAB3` | HAR 97 records · API 4 · scenario 11/11 step · storage keys pp-recent pp-cart pp-coupon |
| `RESULT:FT:LAB4` | ชุดเดิม 40/40 ทุกเบราว์เซอร์ (chromium firefox webkit) · test ใหม่ 9 (char-money: 6 เงิน 4 จุด + 2 golden API + คู่ 999) · expected-fail 1 (CHAR-02b) × 3 เบราว์เซอร์ |
| `RESULT:FT:LAB5-6` | กรณีที่ลอง 12 · ผิด 4 (999 · 999+PAW10 · 999+NEWCAT50 · 999+SUMMER20) · test BUG-01 แดง 3/7 → เขียว 7/7 · lib/orders.ts +2 −13 |
| `RESULT:FT:LAB7-8` | คำถามถึงร้าน 10 (ร้านตอบ 7 · ⚠️ 3) · impact 6 ไฟล์ (+ตรวจแล้วไม่แตะ 6) · TC-GIFT 17 แดง → 17 เขียว · regression 73/73 × 3 เบราว์เซอร์ (ชุดเดิม 40/40 ×3) |
| `RESULT:FT:LAB9` | hash ต่าง 6 (+ next-env.d.ts มีแค่ v1) · s2b เวอร์ชันเดียวกัน 44/0/0/0/0/8/3 · ข้ามเวอร์ชัน 41/0/0/0/0/5/9 (6 ไฟล์ = unknown) · obligation ✅13 / ⚪3 · HAR ใหม่ API เดิมครบ 4/4 status เดิม (+giftWrap, giftWrapFee) |

## ปิดงาน
`docker compose down` ใน `petshop` (project pawpantry05) หลังเขียนไฟล์นี้ — ดูผลในข้อความตอบกลับ
