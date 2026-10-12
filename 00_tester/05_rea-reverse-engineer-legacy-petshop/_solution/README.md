# 🔑 เฉลยผู้สอน · บท 05 รับช่วงระบบเดิม PawPantry (REA + legacy)

> ⚠️ **โฟลเดอร์นี้สำหรับผู้สอนเท่านั้น** มีเฉลย BUG-01 (ต้นเหตุ + วิธีแก้) · เฉลย CR-01 และ PR-1 · เกณฑ์ตรวจ ([GRADING.md](GRADING.md)) · เฉลย Quiz ([QUIZ.md](QUIZ.md))
> ถ้าแจกงานให้ผู้เรียน ให้ลบหรือย้าย `_solution/` ออกก่อน (หรืออย่างน้อยห้ามเปิดก่อนจบ LAB 10)

ไฟล์ผลงานในนี้มาจาก **การรันพรอมต์ใน [README.md](../README.md) ของบทจริงครบ LAB 0–10 หนึ่งรอบ** (12 ต.ค. 2026 · 09:19–11:10) โดยให้ Claude สวมบทผู้เรียน ทำทีละ LAB ตามพรอมต์ตรงตัว 1 LAB = 1 เซสชันใหม่ ไม่อ่าน LAB ถัดไปล่วงหน้า และไม่เปิด `_solution/` — กติกาการรันอยู่ใน [_design/RUNNER.md](_design/RUNNER.md)

- **รันใน sandbox แยก** (`C:/t/work/…/w/` = สำเนาโฟลเดอร์บทที่เป็น git repo ของตัวเอง) ไม่ใช่ในโฟลเดอร์บทจริง · โหมดการรัน: **แบบ A** (runner ทำเองใน Agent-tool session ทุก LAB · cwd ของ runner ไม่ใช่ `w/` จึงต้องทำตาม `CLAUDE.md` / `.claude/settings.json` เอง) · มีเซสชันใหม่จริง `yolo.cmd -p` จาก `w/` 2 ครั้งใน LAB 1 เพื่อทดสอบรั้ว deny
- **ใช้ Playwright แบบ headless** ทุกงานเบราว์เซอร์ (ไม่ใช้ Playwright MCP แบบ `--extension`) · REA ผ่าน image `rea-lab:6.4.0` + `rea\rea.ps1` ตามพรอมต์
- **จุด "ถามผมก่อน"** (LAB 1 5 6 7 8 10) runner ตอบตาม 🧑 ใน `_design/PROMPTS.md` แล้วจดใน result หัวข้อ "ตัดสินแทนผู้เรียน"
- พอร์ต: เว็บ `localhost:4000` ตามพรอมต์ · **รันที่ 4000 จริง ไม่ต้องแปลง URL** · ระหว่างรอบนี้บท 06 รันขนานที่ 4100/5533 (D10) ไม่ชน · ช่วงที่ Windows จองมี `2970–3069` (ครอบ 3000) · 4000 ไม่อยู่ในช่วงใด
- ตัวเลขผลจริงทุกตัวในหน้านี้มาจาก `_design/results/LAB*_RESULT.md` และไฟล์ผลในโฟลเดอร์นี้ · ช่องที่ไม่มีข้อมูลจริงเขียนว่า "ไม่ได้วัดในรอบจริง"

---

## สารบัญ

1. [ไฟล์ในโฟลเดอร์นี้ มาจาก LAB ไหน](#1-ไฟล์ในโฟลเดอร์นี้-มาจาก-lab-ไหน)
2. [ผลจริงทีละ LAB](#2-ผลจริงทีละ-lab)
3. [เฉลยบั๊กที่อบไว้ (BUG-01)](#3-เฉลยบั๊กที่อบไว้-bug-01)
4. [บั๊กจริงที่ไม่ได้อบ (PR-1 และที่เจอระหว่างทาง)](#4-บั๊กจริงที่ไม่ได้อบ-pr-1-และที่เจอระหว่างทาง)
5. [ชุดเทสต์เดิมจับได้แค่ไหน (เทสต์เขียว ≠ ไม่มีบั๊ก)](#5-ชุดเทสต์เดิมจับได้แค่ไหน-เทสต์เขียว--ไม่มีบั๊ก)
6. [งานที่ดีควรมีอะไร + คะแนนรูบริกของเฉลย](#6-งานที่ดีควรมีอะไร--คะแนนรูบริกของเฉลย)
7. [ปัญหาที่เจอระหว่างทำจริง / ข้อเสนอแก้พรอมต์](#7-ปัญหาที่เจอระหว่างทำจริง--ข้อเสนอแก้พรอมต์)
8. [เปิดเว็บเฉลยและรันซ้ำ](#8-เปิดเว็บเฉลยและรันซ้ำ)

---

## 1. ไฟล์ในโฟลเดอร์นี้ มาจาก LAB ไหน

| ไฟล์ / โฟลเดอร์ | ได้จาก LAB | เนื้อหา |
|---|---|---|
| [CODEBASE-MAP.md](CODEBASE-MAP.md) | LAB 1 | ส่วน A–I · 176 บรรทัด · แถว: A 9 · B 12 (11 หน้า + 404) · C 13 · D 14 · E 8 · F 1 + ช่องโหว่ 7 · G 20 · H 7 · I 8 · ยังไม่รู้ 6 ข้อ · แถว "เดา" 1 (ส่วน H สต็อกฝั่ง browser ค้าง) · ส่วน G ⚠️ 7 / ❌ 2 |
| [CLAUDE.md](CLAUDE.md) · `.claude/settings.json` | LAB 1 | 46 บรรทัด · deny 5 กฎ (`Edit(...)` ของ `playwright.config.ts` `global-setup.ts` `package.json` `tests/*.ts` `TEST-DATA.md`) · ทดสอบแก้ไฟล์เดิม = **ถูกปฏิเสธ** (`File is in a directory that is denied…`) · สร้างไฟล์ใน `tests/new/` = **ได้** · หลังรอบจริงเพิ่ม deny `Read(/README.md)` `Read(./fast_track/**)` `Read(./_solution/**)` (D15 · ทดสอบแยกด้วย `claude -p`: 3 เป้าถูกปฏิเสธทั้ง Read และ Grep · `petshop/README.md` อ่านได้ · `Read(./README.md)` จะกัน `petshop/README.md` ด้วย) |
| [SYSTEM-MAP.md](SYSTEM-MAP.md) | LAB 2 | REA เห็น / โค้ดบอก / ตรงไหม · ส่วน B 33 แถว: ✅ 18 · ⚠️ 3 · ❓ 12 · 2 ตา 22 แถว (white+grey 21 · white+black 1) · ตาเดียว 11 แถว |
| [API-INVENTORY.md](API-INVENTORY.md) | LAB 3 | API ที่เห็นตอนรัน 4 (coupons/validate · auth/login · orders · products) · เติมช่องว่าง SYSTEM-MAP 17 แถว: 🟢 8 + 🟡 1 · ยังไม่รู้ 8 · API ในโค้ดที่ไม่เห็นตอนรัน 9 แถว |
| [BASELINE.md](BASELINE.md) | LAB 4 | ผลชุดเดิม · ตารางช่องว่าง · test ใหม่ · ผู้ต้องสงสัย **S1**: ตะกร้า ฿999 พอดี ตะกร้า/ปุ่ม ฿999 ส่งฟรี แต่ server บันทึกค่าส่ง ฿50 ยอด ฿1,049 |
| [BUG-01.md](BUG-01.md) | LAB 5 (อาการ → ต้นเหตุ → impact) · LAB 6 (หัวข้อ "แก้แล้ว") | 7 กรณี black-box (ผิด 2: ฿999 ส่งธรรมดา · ฿999+PAW10) · ต้นเหตุ `lib/orders.ts:63-67` (`>` vs `pricing.ts:130-133` `>=`) · แนะนำวิธี A ลบบล็อกซ้ำ · หลังแก้ 162 บรรทัด |
| [CR-01.md](CR-01.md) | LAB 7 (คำถาม · impact · TC · ผลรอบแรก) · LAB 8 (หัวข้อ "ทำแล้ว") | คำถามถึงร้าน 8 ข้อ (Q1–Q6 ร้านตอบ · Q7 Q8 = สมมติฐาน ⚠️) · impact 6 ไฟล์ (มี `app/orders/[id]/page.tsx`) + ตรวจแล้วไม่ต้องแตะ 8 ไฟล์ · TC-GIFT-01…18 = 21 test |
| [CHANGE-PROOF.md](CHANGE-PROOF.md) | LAB 9 ส่วนที่ 1 | SHA-256 · ตาราง 4 ทิศ · 3 รายการ · obligation ledger · source ต่าง 6 / เหมือน 114 / มีแค่ v1 1 · s2b คู่เดียวกัน 44/0/0/0/0/8/3 · ข้ามเวอร์ชัน 41/0/0/0/0/5/9 · ledger 19 ข้อ ✅ 15 · ❌ 0 · ⚪ 4 |
| [CHANGE-REPORT.md](CHANGE-REPORT.md) | LAB 9 ส่วนที่ 2 · LAB 10 (แถว PR-1) | 5 หัวข้อ · ตารางสรุปหัวข้อ 1 = 8 แถว (ชนิดงาน · ไฟล์ +/− · test ใหม่ · regression · REA evidence · พฤติกรรมที่เปลี่ยน · ความเสี่ยง · rollback) × 3 คอลัมน์งาน (BUG-01 · CR-01 · PR-1 ที่เติมใน LAB 10) |
| `e2e-legacy/tests/new/` | LAB 4 (`char-money` + `golden/`) · LAB 5 (`bug01-shipping`) · LAB 7 (`cr01-giftwrap`) · LAB 10 (`pr1-*`) | `char-money.spec.ts` 7 · `bug01-shipping.spec.ts` 9 · `cr01-giftwrap.spec.ts` 21 (18 `test(` + วน 4 ค่า) · `pr1-add-to-cart.spec.ts` 4 = **41 test** · `golden/products.json` (28 รายการ) · `golden/coupons-validate.json` (30 กรณี) |
| `petshop/` (โค้ดหลังแก้) | LAB 6 · 8 · 10 | เก็บ **เฉพาะ 7 ไฟล์ที่แก้** (ตำแหน่งเดิม) + diff เต็ม [petshop-solution.diff](petshop-solution.diff) (เทียบโฟลเดอร์ตั้งต้น · +66 −17): `lib/orders.ts` +6 −8 (BUG-01 +1 −7 · CR-01 +5 −1) · `lib/pricing.ts` +15 −2 · `lib/store.ts` +2 −0 · `components/OrderSummary.tsx` +11 −3 · `components/CheckoutForm.tsx` +19 −2 · `app/orders/[id]/page.tsx` +8 −0 · `components/ProductCard.tsx` +5 −2 (PR-1) |
| `out/` (คัดบางไฟล์) | LAB 2 3 5 8 9 | ไฟล์เล็ก < 300 KB เท่านั้น: `trace-coupon.json` (LAB 2) · `scenario-final.png` (LAB 3) · `bug01-before-fix/bug01-blackbox.json` + `bug01-blackbox.json` (LAB 5 / 6) · `shots/lab8-checkout-giftwrap.png` (LAB 8) · `v1-src.json` `v2-src.json` `s2b-*.json` ×4 (LAB 9) · `scenario-hdi.json` (LAB 0) · **ไม่เก็บ** `.har` · `har.json` · `har-steps.json` (มีค่าลับ demo) · ผล analyze/compare ขนาด 4–108 MB |
| `rea/scratch/*.mjs` | LAB 3 4 5 8 10 | สคริปต์ชั่วคราวที่ผู้เรียนเขียน 11 ไฟล์ (`har-peek` `scn-peek` `lab4-*` ×3 `bug01` `bug01-har` `lab8-api` `lab8-shot` `pr1-repro` `pr1-toast-probe`) |
| [QUIZ.md](QUIZ.md) | ก่อนถ่ายทำ | เฉลย Quiz 10 ข้อ + คำอธิบาย + ฉบับคำตอบจริงของบท + คำถามสำรอง |
| [GRADING.md](GRADING.md) | ก่อนถ่ายทำ | รูบริก 20 ข้อ + วิธีตรวจ · ตรวจทีละ LAB · เฉลย BUG-01 / CR-01 / PR-1 · ผลที่คาดหวังจาก REA |
| `_design/LESSON-PLAN.md` · `PROMPTS.md` · `RUNNER.md` | ก่อนถ่ายทำ | แผนการสอน · พรอมต์ทุก LAB (ฉบับที่ใช้รัน) · กติกาให้ Claude สวมบทผู้เรียน |
| `_design/REA-THEORY.md` · `REA-FEASIBILITY.md` · `METHODS.md` · `rea-probe/` | ก่อนถ่ายทำ | ทฤษฎี · ผลพิสูจน์ว่า REA คำสั่งไหนใช้ได้ (A1 รันจริง) · วิธีอื่นที่เลือกใช้ |
| `_design/CODEBASE-NOTES.md` · `CR-DESIGN.md` | ก่อนถ่ายทำ | แผนที่โค้ด · ออกแบบ BUG-01 / CR-01 / PR-1 (A5 รันจริงบน prototype) |
| `_design/results/LAB0_RESULT.md` … `LAB10_RESULT.md` | ทุก LAB | คำตอบในแชท · ตัวเลข · ข้อสังเกต · ปัญหา · ข้อเสนอแก้พรอมต์ — ที่มาของตัวเลขทุกตัวในหน้านี้ (อีเมล/รหัส demo ถูกแทนด้วย `<อีเมล demo>` `<รหัส demo>`) |

---

## 2. ผลจริงทีละ LAB

| LAB | เวลา | ผลจริง |
|---|---|---|
| 🧰 build image | ไม่ได้วัดในรอบจริง (image มีอยู่แล้ว ไม่ได้ build) | `rea-lab:6.4.0` 2,654,494,021 bytes (~2.65 GB) |
| 0 เช็กเครื่อง | ~4 นาที | ExecutionPolicy: CurrentUser RemoteSigned · Process Bypass (ไม่ต้องเปลี่ยน) · พอร์ตที่จอง 23 ช่วง มี `2970–3069` (ครอบ 3000) · 4000 ว่าง · `doctor` exit 1 `healthy: false` (node/host ผ่าน · hopper/ghidra/ida/skill ไม่ผ่าน = ไม่ใช้กับงานเว็บ) · `pawpantry05` healthy `0.0.0.0:4000->3000` · probe `http://petshop:3000/api/health` ใน `pawpantry05_default` → `{"ok":true}` · ทางสำรอง host.docker.internal ผ่าน 2 ชั้น (node fetch + scenario 11/11) |
| 1 อ่าน repo | ~9 นาที | 11 หน้า + 404 · API 12 route file (13 แถว) · กฎธุรกิจ 14 แถว · ส่วน G 20 เรื่อง (⚠️ 7 · ❌ 2 = SUMMER20 · "ทุกหน้าดึง /api/products") · ส่วน I 8 แถว · กฎค่าส่งเขียน 3 ที่ (`pricing.ts:132` `>=` · `orders.ts:65` `>` · `CheckoutForm.tsx:216`) · Explore subagent เจอค่าขอบ ฿999 (PP-231) ตั้งแต่ LAB นี้ |
| 2 REA ส่อง build | 11 นาที | build v1 159 s · static (`ev_64fa462f`): files 21 · endpoint 9 (ของร้าน 6 + `a` `b` `c`) · storage local-storage ×3 (`name: null`) · coverage partial · server (`ev_ac8d9821`): files 445 · recovered_source_files 52 (static = 0) · trace คูปอง (`ev_d404eddd`): matched_seeds 13 · traced_nodes 16 · traced_edges 75 · REA พลาด `/api/recommendations` (URL เป็น template literal) |
| 3 HAR + scenario | ~8 นาที | HAR 8 ขั้น 3,080 ms · 97 records · API 4 (`ev_4db99f23`) · รหัส demo ใน `out\har.json` = False (ใน `.har` ต้นฉบับ = True) · scenario 11/11 steps · events 421 (`ev_956755da`) · storage `pp-recent` `pp-cart` `pp-coupon` · a11y `alert: ใช้คูปอง PAW10 แล้ว` · ส่วนลด −฿6 · ยอดชำระ ฿113 |
| 4 characterization | 11 นาที | ชุดเดิม chromium 40/40 · 3 เบราว์เซอร์ 120/120 · ช่องว่าง: ไม่มี test ใช้ ฿999 พอดี / ไม่มี test อ่าน response `POST /api/orders` / ส่งด่วนไม่มี test · `char-money` 7 test (6 ผ่าน + 1 expected-fail) เงิน 4 จุด · golden products 28 · คูปอง 30 กรณี · รวม 3 เบราว์เซอร์ 141 passed (expected-fail 3 ถูกนับรวม) · ผู้ต้องสงสัย S1 = ฿999 |
| 5 BUG-01 ทำซ้ำ + ต้นเหตุ | ~10 นาที | 7 กรณี black-box ผิด 2 (฿999 → ฿1,049 · ฿999+PAW10 ปุ่ม ฿900 → ฿950) · `bug01-shipping` 3 failed / 6 passed (แดงเพราะเงินทุกข้อ) · ต้นเหตุ `lib/orders.ts:63-67` · HAR: body `POST /api/orders` มีแค่ `items{slug,size,qty} coupon shipping payment address` → คอมเมนต์ PP-231 ไม่จริง · แนะนำวิธี A ลบบล็อกซ้ำ |
| 6 แก้ BUG-01 | ~6 นาที | วิธี A · `lib/orders.ts` +1 −7 · `bug01-shipping` 3F/6P → 9/9 · `char-money` SHIP-02/03 พลิกตามคาด → ปรับ test ใหม่ของตัวเอง · ชุดเดิม chromium 40/40 · ทั้งชุด chromium 56 passed · ยิงซ้ำ 7 กรณี: ปุ่ม = server total = /account ทุกกรณี |
| 7 CR-01 ถาม + impact + แดง | ~7 นาที | คำถาม 8 ข้อ · impact 6 ไฟล์ **มี** `/orders/[id]` (`page.tsx:104-123` เขียนสรุปเงินเอง) · TC-GIFT 21 test · รอบแรก 18 failed / 3 passed (แดงเพราะหา `gift-wrap` ไม่เจอ 9 · ไม่มี field `giftWrap`/`giftWrapFee` 9) · guard เขียว TC-GIFT-13 17 18 |
| 8 ทำ CR-01 + regression | ~16 นาที | 6 ไฟล์ +61 −15 (เฉพาะ CR-01 +60 −8) · TC-GIFT 21/21 · `test:all` รอบเดียว 185/231 (ล้ม 46 เพราะสต็อกลูกแมวแซลมอนหมด 20×3 > 25) → รันแยกเบราว์เซอร์ 77/77 ×3 · ยิง API ตรง 18/18 (รวมข้อปลอม `giftWrapFee:0,total:1` → server คิด 269) |
| 9 พิสูจน์ + ส่งมอบ | ~11 นาที | SHA-256: ต่าง 6 · เหมือน 114 · มีแค่ v1 1 (`next-env.d.ts`) · s2b คู่เดียวกัน 44/0/0/0/0/8/3 (`ev_23cd4cec` `ev_f47a7dd1`) · ข้ามเวอร์ชัน 41/0/0/0/0/5/9 (`ev_b034f50f` `ev_ba4bd111`) · 3 รายการ ✅ (⚠️ 1 อธิบายได้) · ledger ✅ 15 / ❌ 0 / ⚪ 4 · compare-versions (`ev_360083db`) changed 235 · unknown 1,465 / 1,700 · HAR ใหม่ (`ev_b1e9e721`) 97 records · API 4 status เดิม + key `giftWrap` |
| 10 PR-1 | ~16 นาที | ทำซ้ำ black-box (2+2 → toast สำเร็จทั้งสองรอบ · ตะกร้า 3) → test แดง 2F/2P → ถามข้อความ → ต้นเหตุ `ProductCard.tsx:63` `if (added > 0)` → แก้ +5 −2 → 4/4 · chromium 81/81 · `test:all` รอบเดียว 196/243 (สต็อก) → firefox 81/81 · webkit 81/81 · เติม CHANGE-REPORT คอลัมน์ PR-1 |

### เวลาจริงต่อ LAB

จากหัวตาราง "เวลาเริ่ม · จบ · ใช้ไป" ของแต่ละ `LAB*_RESULT.md` (12 ต.ค. 2026 · "เครื่อง" = เวลาที่คำสั่งรันจริง · ที่เหลือ = agent คิด/อ่าน/เขียน)

| LAB | เริ่ม | จบ | ใช้ไป | เครื่อง | agent |
|---|---|---|---|---|---|
| 0 | 09:19 | 09:23 | ~4 นาที | ~0.3 นาที | ~3.7 |
| 1 | 09:24 | 09:33 | ~9 นาที | ~0.3 นาที | ~8.7 (Explore ~4) |
| 2 | 09:34 | 09:45 | 11 นาที | ~4 | ~7 |
| 3 | 09:44 | 09:52 | ~8 นาที | ~0.5 | ~7.5 |
| 4 | 09:51 | 10:02 | 11 นาที | ~4 | ~7 |
| 5 | 10:03 | 10:13 | ~10 นาที | ~2.5 | ~7.5 |
| 6 | 10:12 | 10:18 | ~6 นาที | ~2.5 | ~3.5 |
| 7 | 10:19 | 10:25 | ~7 นาที | ~0.6 | ~6 |
| 8 | 10:26 | 10:42 | ~16 นาที | ~7.5 | ~8.5 |
| 9 | 10:42 | 10:53 | ~11 นาที | ~4.2 | ~7 |
| 10 | 10:54 | 11:10 | ~16 นาที | ~8 | ~8 |
| **รวม** | 09:19 | 11:10 | **~109 นาที** (ผลรวมแถว) | **~34 นาที** | ~75 |

> เวลา "เครื่อง" ที่ยาวที่สุด: build v1 159 s (LAB 2) · build v2 155.2 s (LAB 9) · `npm run test:all` 244 s (LAB 8) และ 288.7 s (LAB 10) · ทุก `docker compose up --build` ในรอบนี้ใช้ cache (3.3 / 12 / 11 / 9.7 s) — ผู้เรียนครั้งแรกจะนานกว่านี้

### หมายเหตุรายละเอียดสำคัญ

- **LAB 0:** `doctor` พ่น output 2,829 บรรทัด (~83 KB) · `--filter-output healthy,checks` เหลือ ~30 บรรทัด exit เท่าเดิม · `Get-Content | Set-Content` ใน PS 5.1 ทำภาษาไทยในไฟล์ JSON พัง → ใช้ .NET `UTF8Encoding($false)`
- **LAB 1:** รั้ว deny ทำงานจริงในเซสชันใหม่ (`yolo.cmd -p` จาก `w/`): แก้ `01-home.spec.ts` ถูกปฏิเสธ · เซสชันแรกหยุดหลังโดนปฏิเสธจึงต้องทดสอบขั้นสร้าง `tests/new/_probe.spec.ts` อีกเซสชัน → สร้างได้ แล้วลบ · runner ใช้ Git Bash อ่านไฟล์/เขียน settings.json (พรอมต์ขอ PowerShell)
- **LAB 2:** REA ส่ง progress JSON ออก stderr 492 บรรทัด (~88 KB) ต่อการ analyze 2 ครั้ง · runner grep ไฟล์ build เองเพื่อหาที่มาของ `a b c` / `/api/recommendations` (กำกับไว้ใน SYSTEM-MAP ว่าไม่ใช่ REA)
- **LAB 3:** `rea-summarize` ให้แค่ชื่อ key → ค่าตัวอย่างต้องเขียนสคริปต์ `rea\scratch\har-peek.mjs` · REA ปิด body ของ login ทั้งก้อน (เสีย request keys ไปด้วย)
- **LAB 4:** ไม่มี flaky · `test.fail()` ถูก reporter นับรวมใน "passed" (141 = 120 + 21) ต้องดู `x` ใน list / tag `@known-issue`
- **LAB 5:** runner **รู้ต้นเหตุก่อนขั้นที่ 3** (จาก RUNNER.md ที่ grep `PP-231` · 🎯 ของ LAB 5 · และ CODEBASE-MAP ส่วน D ของ LAB 1 ที่ชี้ `lib/orders.ts:63-67`) แต่ไม่เปิดไฟล์ใน `petshop/` และไม่อ่านส่วน D จนจบขั้นที่ 2 · ตาราง black-box มาจากการรันจริงทั้งหมด
- **LAB 6:** BUG-01.md แนะนำ A อยู่แล้ว → คำตอบ 🧑 ("ให้กฎเงินอยู่ที่เดียว") ตรงกัน ไม่มีความขัดแย้ง · สำรองผลก่อนแก้ไป `out\bug01-before-fix\` ก่อนรันสคริปต์ซ้ำ (ไม่งั้นหลักฐานก่อนแก้ถูกเขียนทับ)
- **LAB 7:** runner อ่านบรรทัด 🎯 ติดมาก่อนคิดตัวเลข → ตะกร้า ฿1,499/฿1,500 ตรงกับ 🎯 ทุกชิ้น (ไม่ควรนับว่าหาตะกร้าขอบเองได้) · ตัวเลขทุกค่ายืนยันจาก API + การรัน
- **LAB 8:** `test:all` รอบเดียวล้มเพราะสต็อกร่วมหมด (409 "สินค้าไม่พอ") รวมชุดเดิม webkit 4 ข้อ — ไม่ใช่โค้ดผิด · runner เห็น 🎯 ก่อนรัน (awk เกินบล็อก) · ตัวเลข CR-only ครั้งแรกเขียน −9 ตาม 🎯 แล้วนับใหม่ได้ −8
- **LAB 9:** `Get-FileHash` ไม่ใส่ `-LiteralPath` คืนค่าว่างเงียบ ๆ สำหรับ path ที่มี `[id]` `[slug]` → ได้ "ต่าง 5" ผิด (หลุด `app/orders/[id]/page.tsx`) · จับได้เพราะเทียบกับ `git status`
- **LAB 10:** test แดงรอบแรกแดง "ผิดเหตุ" 2 ข้อ (`item-qty` เป็น `<input>` ต้อง `toHaveValue`) → guard ช่วยจับ spec ผิด · ปิด `pawpantry05` ด้วย `docker compose down` ตอนจบ

---

## 3. เฉลยบั๊กที่อบไว้ (BUG-01)

บทนี้ **ไม่มี BUG_MODE** · บั๊กเดียวที่อบลงโค้ดถาวรคือ BUG-01 (diff `_design/LESSON-PLAN.md` §7.3) · รายละเอียดเต็ม + วิธีตรวจงานผู้เรียน: [GRADING.md ข้อ 4](GRADING.md#4-เฉลย-bug-01-ต้นเหตุ--วิธีแก้ที่ถูก--กับดัก)

| | |
|---|---|
| อาการ | ตะกร้า ฿999 พอดี (ไม้ตกแมว ขนนก ฿129 + ชามกินช้า ฿290 ×3) ส่งธรรมดา: หน้าตะกร้า/ปุ่มบอก ฿999 ส่งฟรี แต่คำสั่งซื้อจริงเก็บ ฿1,049 |
| ต้นเหตุ | `petshop/lib/orders.ts:63-67` บล็อก `// PP-231` คำนวณค่าส่งซ้ำด้วย `>` แล้วเขียนทับ `totals.total` (กฎจริง `lib/pricing.ts:130-133` ใช้ `>=`) · คอมเมนต์อ้างว่า browser ส่งค่าส่งมา แต่ body จริงมีแค่ `shipping: "standard"` |
| แก้ที่ถูก | ลบบล็อกซ้ำ + import `FREE_SHIPPING_MIN` `STANDARD_SHIPPING` ให้ `computeTotals()` เป็นแหล่งเดียว |
| กับดัก | แก้แค่ `>` → `>=` ผ่านทุก test ของ LAB 6 แต่ทำให้ CR-01 ค่าห่อหายในคำสั่งซื้อ (หน้า ฿269 · คำสั่งซื้อ ฿239) |

### 3.1 ตารางกรณี: ค่าที่ต้องได้ vs รอบนี้

| กรณี | ค่าที่ต้องได้ ก่อนแก้ (A5) | รอบนี้ ก่อนแก้ (LAB 5) | ค่าที่ต้องได้ หลังแก้ | รอบนี้ หลังแก้ (LAB 6) |
|---|---|---|---|---|
| ฿999 ส่งธรรมดา | ปุ่ม ฿999 · คำสั่งซื้อ ฿1,049 | ปุ่ม ฿999 · คำสั่งซื้อ ฿1,049 (ค่าส่ง ฿50) ❌ | ฿999 ทุกจุด | ค่าส่ง 0 · ฿999 ✅ |
| ฿999 + PAW10 | ปุ่ม ฿900 · คำสั่งซื้อ ฿950 | ปุ่ม ฿900 · คำสั่งซื้อ ฿950 ❌ | ฿900 | ค่าส่ง 0 · ฿900 ✅ |
| ฿998 ส่งธรรมดา | ฿1,048 ทั้งคู่ | ฿1,048 ทั้งคู่ ✅ | ฿1,048 | ฿1,048 ✅ |
| ฿999 + FREESHIP | ฿999 ทั้งคู่ | ฿999 ทั้งคู่ ✅ | ฿999 | ฿999 ✅ |
| ฿999 ส่งด่วน | ฿1,119 ทั้งคู่ | ฿1,119 ทั้งคู่ ✅ | ฿1,119 | ฿1,119 ✅ |

(รอบนี้ทดสอบเพิ่ม 2 กรณี: ฿1,000 ส่งธรรมดา ฟรี ฿1,000 · ฿998 + PAW10 ฿949 — ถูกทั้งก่อนและหลังแก้)

### 3.2 รอบนี้ agent ทำอะไร

| ประเด็น | รอบนี้ |
|---|---|
| ทำซ้ำ black-box ก่อนเปิดโค้ดจริงไหม · รู้ต้นเหตุจาก CODEBASE-MAP มาก่อนไหม | ทำซ้ำ black-box จริง 7 กรณี (สคริปต์ `bug01.mjs` 84 s · ราคาจาก `GET /api/products` · ไม่เปิด `petshop/` และไม่อ่าน CODEBASE-MAP ส่วน D จนจบขั้นที่ 2) · **แต่รู้ต้นเหตุมาก่อน**: CODEBASE-MAP ส่วน D (LAB 1) ชี้ `lib/orders.ts:63-67` + PP-231 ไว้แล้ว และ BASELINE S1 + TC-CHAR-SHIP-02 บอกอาการครบ |
| test `bug01-shipping` แดงด้วยเหตุผลอะไร | เงินทั้งหมด ไม่มี timeout/locator: server `{shipping:50,total:1049}` ≠ `{0,999}` · หน้าคำสั่งซื้อ ฿50/฿1,049 · /account 1049 ≠ 999 · ปุ่ม = คำสั่งซื้อ 1049 ≠ 999 · PAW10 950 ≠ 900 (3 failed · 6 passed · 7.2 s) |
| ตรวจคอมเมนต์ PP-231 กับ HAR ไหม | ตรวจ: HAR 7 ครั้งของ `POST /api/orders` body มีแค่ `items{slug,size,qty} coupon shipping payment address` (เช่น `{"coupon":null,"shipping":"standard","payment":"cod"}`) → ไม่มีค่าส่งให้ "ไม่เชื่อ" คอมเมนต์ไม่จริง |
| วิธีที่ BUG-01.md แนะนำ / วิธีที่ใช้จริงใน LAB 6 | แนะนำ **A ลบบล็อกซ้ำ** (มี B `>`→`>=` และ C เป็นทางเลือก) / ใช้ **A** จริง: ลบ 7 บรรทัด (import 2 + คอมเมนต์ + if 4) เพิ่มคอมเมนต์อ้าง BUG-01 1 บรรทัด |
| ถ้าใช้ `>=` — LAB 8 พังตามที่ทำนายไหม | ไม่เกิด เพราะ LAB 6 แก้ที่ต้นเหตุ (LAB 8 ยืนยัน: กรณี "UI ฿269 แต่คำสั่งซื้อ ฿239" ไม่เกิด) |

---

## 4. บั๊กจริงที่ไม่ได้อบ (PR-1 และที่เจอระหว่างทาง)

| บั๊ก | อยู่ที่ | เจอครั้งแรก | ชุดเดิมจับได้ไหม | สถานะหลังจบบท |
|---|---|---|---|---|
| **PR-1** toast "เพิ่ม…ลงตะกร้าแล้ว" ทั้งที่เพิ่มได้ไม่ครบ (สูตรลดก้อนขน สต็อก 3: เพิ่ม 2 + 2 → ตะกร้า 3) | `components/ProductCard.tsx:59-70` `useAddToCart` เช็กแค่ `added > 0` | LAB 10 (ข้อความลูกค้า) · LAB 1/4 ไม่เห็นก่อน (CODEBASE-MAP/BASELINE ไม่มีแถวเรื่อง `useAddToCart` หรือ toast) | ไม่ได้ — ชุดเดิม 40/40 ทุกเบราว์เซอร์ใน LAB 4 และ LAB 8 ขณะที่ PR-1 ยังอยู่ | แก้แล้ว (LAB 10): `ProductCard.tsx` +5 −2 → toast `error` "เพิ่มได้อีกเพียง {n} ชิ้น (สินค้าเหลือ {สต็อก} ชิ้น)" · `pr1-add-to-cart` 2F/2P → 4/4 · regression 81/81 ×3 (ทีละเบราว์เซอร์) |
| ตัวเลือกจำนวนบนหน้าสินค้า clamp ที่สต็อกรวม ไม่หักของในตะกร้า · หน้าสินค้ายังขึ้น "เหลือ 3 ชิ้น" หลังของ 3 ชิ้นอยู่ในตะกร้า | หน้า `/products/[slug]` (ต้นทางของอาการ PR-1) | LAB 10 | ไม่มี test | ไม่แก้ (นอกขอบเขต PR-1 · ร้านเลือกแก้ที่ข้อความ) → ควรถามร้าน |
| ชุดทดสอบ `tests/new/` ใช้สต็อกร่วมเกิน seed เมื่อรัน 3 เบราว์เซอร์รอบเดียว (`kitten-salmon-dry` 20/25 ต่อเบราว์เซอร์ · `puppy-lamb-wet` 15/40 · `dog-slow-bowl` 8/18) | `e2e-legacy/tests/new/cr01-giftwrap.spec.ts` + `global-setup.ts` reset ครั้งเดียวต่อรอบ | LAB 8 | – (ทำให้ชุดเดิม webkit ล้ม 4 ข้อใน `test:all` รอบเดียว) | ไม่แก้ · หลบด้วยการรันทีละเบราว์เซอร์ (`--project=`) · บันทึกใน CR-01.md ให้เจ้าของชุดทดสอบตัดสิน |

เรื่องที่ไม่ใช่บั๊กแต่ควรถามร้าน (จาก CODEBASE-MAP ส่วน G / BASELINE): SUMMER20 ยังใช้ได้ไหม (HANDOVER บอกถึงสิ้นปี · โค้ด/TEST-DATA บอกหมดอายุ) · HANDOVER บอก "ทุกหน้าดึง `/api/products`" แต่หน้า `/` `/products` `/products/[slug]` อ่าน `liveProducts()` บน server → แก้ข้อมูลสินค้าต้องแก้ `lib/products.ts` ใช่ไหม · PAW10 "สำหรับสมาชิกใหม่" หรือ "ทุกออเดอร์" (โค้ดไม่ตรวจผู้ใช้) · PAW10 ปัดลงตั้งใจไหม · FREESHIP ใช้กับส่งด่วนด้วยไหม · NEWCAT50 นับขนมแมวเป็นอาหารไหม · PP-231 ปิดแล้วจริงไหม · ฿999 พอดีส่งฟรีไหม · ส่งฟรีนับยอดก่อนหรือหลังส่วนลด (BASELINE: ยังไม่ล็อก) · `/api/test/reset` ไม่มี auth production ปิดไหม · จังหวัดที่ไม่อยู่ในรายการถูกแทนเป็น "กรุงเทพมหานคร" เงียบ ๆ (`lib/orders.ts:41-47`)

---

## 5. ชุดเทสต์เดิมจับได้แค่ไหน (เทสต์เขียว ≠ ไม่มีบั๊ก)

`e2e-legacy/` = ชุดของทีมเดิม 40 test (คัดจากบท 02) · ค่าอ้างอิงใน `e2e-legacy/README-LEGACY.md`: chromium 40 passed · 3 เบราว์เซอร์ 120 passed

| จุดเวลา | ชุดเดิม chromium | ชุดเดิม 3 เบราว์เซอร์ | `tests/new` | หมายเหตุ |
|---|---|---|---|---|
| LAB 4 ก่อนแตะโค้ด (มี BUG-01) | 40/40 (14.4 s) | 120/120 (60.7 s) | `char-money` 6 passed + 1 expected-fail ต่อเบราว์เซอร์ (chromium 2 รอบเท่ากัน) · รวมชุดเดิม 141 passed | ชุดเดิมจับ BUG-01 ได้ไหม: **ไม่ได้** — เขียวครบบน build ที่มีบั๊ก |
| LAB 5 test BUG-01 ก่อนแก้ | — | — | `bug01-shipping` 3 failed · 6 passed (chromium) | |
| LAB 6 หลังแก้ BUG-01 | 40/40 | — | `bug01-shipping` 9/9 · `char-money` 7/7 (หลังปรับ SHIP-02/03 · ก่อนปรับ 2 failed) · ทั้งชุด 56 passed | |
| LAB 7 TC-GIFT รอบแรก | — | — | `cr01-giftwrap` 18 failed · 3 passed | |
| LAB 8 หลัง CR-01 | 40/40 | 40/40 ทุกเบราว์เซอร์ (รันทีละเบราว์เซอร์) · `test:all` รอบเดียว webkit ล้ม 4 ข้อเพราะสต็อก | 37/37 ต่อเบราว์เซอร์ (bug01 + char-money 16 · cr01 21) · รวม 77/77 ×3 | `test:all` รอบเดียว 185/231 |
| LAB 10 หลัง PR-1 | 40/40 (ทั้งชุด 81 passed 27.6 s) | 81/81 ×3 (ทีละเบราว์เซอร์ · firefox 39.9 s · webkit 1.2 นาที) | 41/41 ต่อเบราว์เซอร์ (+ `pr1-add-to-cart` 4) | `test:all` รอบเดียว 196/243 (สต็อก) |

**ทำไมชุดเดิมพลาด BUG-01** (ตรวจได้จากโค้ด test): TC-CART-03 ชื่อ "ซื้อครบ ฿999 ได้ส่งฟรี" แต่ตรวจที่ ฿790 / ฿2,680 บนหน้าตะกร้า · TC-CHK-03 สั่งซื้อจริงแต่ที่ ฿378 + FREESHIP · ไม่มีข้อสั่งซื้อจนจบที่ ฿999 และไม่มีข้อเทียบ "เงินบนปุ่ม = เงินในคำสั่งซื้อ" · ตารางช่องว่างที่ agent ทำได้รอบนี้: TC-CART-03 ชื่อ ≠ สิ่งที่ตรวจ · กฎเงินเกือบทั้งหมดตรวจแค่หน้าตะกร้า · มีแค่ TC-CHK-03 ที่ดูยอดที่ server บันทึก · ไม่มี test อ่าน response `POST /api/orders` · ส่งด่วน ฿120 ไม่มี test เลย

### 5.1 REA ช่วยตรงไหน · ไม่ช่วยตรงไหน (รอบนี้)

| คำถาม | REA ตอบได้ไหม | หลักฐานรอบนี้ |
|---|---|---|
| ของที่ build มี endpoint/storage อะไร | ได้บางส่วน (🔵 · coverage partial) | static `ev_64fa462f`: endpoint 9 (ของร้าน 6 + noise `a` `b` `c` จาก polyfill) · storage local-storage ×3 `name: null` · พลาด `/api/recommendations` (template literal) · server 34 แถว เป็นของร้านแค่ 6 |
| กฎค่าส่งฝั่ง server ผิดตรงไหน | ไม่ได้ (ตรรกะ server ไม่อยู่ใน client bundle · ต้องดูผ่าน API/HAR หรืออ่าน source) | LAB 5 ไม่ได้ใช้ REA · หาได้จากสคริปต์ black-box เทียบเงิน 5 จุด (ตะกร้า · ปุ่ม · response · หน้าคำสั่งซื้อ · /account) แล้วเปิด `lib/orders.ts:63-67` |
| browser ส่งค่าส่งไป server จริงไหม | ได้ (HAR 🟢) | body `POST /api/orders` = `items coupon shipping payment address` · items = `{slug,size,qty}` (ไม่มีราคา/ค่าส่ง/ยอด) · LAB 5 อ่านจาก HAR ด้วย `bug01-har.mjs` · LAB 3/9 ผ่าน REA `inspect-web-network-capture` |
| ของที่ส่งมอบเปลี่ยนเฉพาะที่ตั้งใจไหม | ได้ เมื่อดู 4 ทิศคู่กับ SHA-256 | v1→v1 / v2→v2 = 44/0/0/0/0/8/3 · v1→v2 / v2→v1 = 41/0/0/0/0/5/9 → 6 ไฟล์ที่แก้กลายเป็น unknown = 6 ไฟล์เดียวกับ SHA-256 · modified = 0 ทุกคู่ |

---

## 6. งานที่ดีควรมีอะไร + คะแนนรูบริกของเฉลย

เกณฑ์ละเอียดและคำตอบผิดที่พบบ่อยอยู่ใน [GRADING.md](GRADING.md) · ตารางนี้ให้คะแนน **งานของรอบถ่ายทำ** ตามรูบริก 20 ข้อ (ดีมาก ≥ 18 · ใช้ได้ 14–17 · ต้องแก้ < 14)

> รอบนี้ **ยังไม่ได้ให้คะแนน** (ไม่มีผู้ตรวจให้คะแนนใน result) · คอลัมน์ "หลักฐาน" คัดข้อเท็จจริงจาก `_design/results/` ไว้ให้ผู้ตรวจใช้ให้คะแนน

| ข้อ | เกณฑ์ (ย่อ) | คะแนน | หลักฐาน / เหตุผล |
|---|---|---|---|
| ข้อ 1 | CODEBASE-MAP "ยืนยันจาก" · เดา ≤ 10% | ไม่ได้วัดในรอบจริง | แถว "เดา" 1 แถว (ส่วน H) · แถวที่ยืนยันจาก subagent ชั้นเดียวติดป้าย "(Explore)" · สุ่มตรวจ ~25 จุดด้วย `sed -n`/`grep -n` ตรงทุกจุด |
| ข้อ 2 | เรื่องเก่าใน HANDOVER ครบ 2 · ไม่ตัดสินเอง | ไม่ได้วัดในรอบจริง | ส่วน G มี ❌ ครบ 2 (SUMMER20 · "ทุกหน้าดึง /api/products") · ความขัดของกฎค่าส่งเขียนเป็นคำถามถึงร้าน ไม่ตัดสิน |
| ข้อ 3 | CLAUDE.md ≤ 60 · settings กันได้จริง | ไม่ได้วัดในรอบจริง | CLAUDE.md 46 บรรทัด · ไม่มี `@CODEBASE-MAP` · deny 5 กฎ: แก้ test เดิมถูกปฏิเสธ · สร้างใน `tests/new/` ได้ |
| ข้อ 4 | SYSTEM-MAP ป้ายครบ · ไม่สรุป "ไม่มี" | ไม่ได้วัดในรอบจริง | ✅ 18 · ⚠️ 3 · ❓ 12 · `/api/recommendations` เขียนเป็น ❓ (REA พลาด ≠ ไม่มี) |
| ข้อ 5 | API-INVENTORY ไม่มีความลับ · 3 วิธี | ไม่ได้วัดในรอบจริง | `Select-String` ทุก `*.md` ไม่พบรหัส/อีเมล demo ใน API-INVENTORY · ส่วน D 3 วิธี (ยืนยันด้วย runtime 2: HAR · scenario) |
| ข้อ 6 | suite เดิม 3 เบราว์เซอร์ก่อนแตะโค้ด | ไม่ได้วัดในรอบจริง | LAB 4: 120/120 ก่อนแก้ `petshop/` (`git diff --stat -- petshop` ว่าง) |
| ข้อ 7 | golden master เงิน 4 จุด | ไม่ได้วัดในรอบจริง | `char-money` ตรวจตะกร้า · ปุ่ม · response · หน้าคำสั่งซื้อ · golden products 28 · คูปอง 30 กรณี (`toEqual` ไม่ใช่ snapshot) |
| ข้อ 8 | [E] ขัด [D] ไม่ถูกอบ | ไม่ได้วัดในรอบจริง | ฿999 ล็อกเป็นคู่ TC-CHAR-SHIP-02 (legacy-quirk) + TC-CHAR-SHIP-03 (`test.fail` KNOWN-ISSUE) · PAW10 + ส่งฟรี "ยังไม่ล็อก ต้องถามร้าน" |
| ข้อ 9 | ทำซ้ำ black-box + ขอบเขตอาการ | ไม่ได้วัดในรอบจริง | 7 กรณี (฿998 · ฿999 · ฿1,000 · PAW10 ×2 · FREESHIP · ด่วน) ก่อนเปิดโค้ด · หมายเหตุ: รู้ต้นเหตุมาก่อน (ดู 3.2) |
| ข้อ 10 | test แดงก่อนแก้ด้วย [D] | ไม่ได้วัดในรอบจริง | `bug01-shipping` 3 failed ด้วยค่าเงินตาม TEST-DATA ("ฟรีเมื่อซื้อครบ ฿999") + invariant ปุ่ม = คำสั่งซื้อ |
| ข้อ 11 | ต้นเหตุไฟล์:บรรทัด + คอมเมนต์ vs HAR | ไม่ได้วัดในรอบจริง | `lib/orders.ts:63-67` vs `pricing.ts:130-133` · ตรวจคอมเมนต์ PP-231 กับ body ใน HAR แล้ว |
| ข้อ 12 | แก้ที่ต้นเหตุ + อธิบายได้ | ไม่ได้วัดในรอบจริง | วิธี A ลบบล็อกซ้ำ +1 −7 · `computeTotals` เป็นที่เดียว · ไฟล์ที่แตะ = ตาราง impact แถว A |
| ข้อ 13 | ถามร้าน ≥ 2 เรื่องพร้อมตัวเลข | ไม่ได้วัดในรอบจริง | 8 คำถาม · เช่น Q1 ฿1,500 + PAW10 ก่อนลด ฿1,350 / หลังลด ฿1,380 · Q2 ฿998 ห่อ ฿1,078 / ฿1,028 · Q4 ฿251 / ฿248 |
| ข้อ 14 | impact ครอบจุดคำนวณและแสดงเงิน | ไม่ได้วัดในรอบจริง | 6 ไฟล์ รวม `app/orders/[id]/page.tsx:104-123` (ไม่ใช้ `SummaryRows`) · เตือนกับดัก golden คูปองถ้าใส่ค่าห่อใน `evaluateCoupon` |
| ข้อ 15 | ขอบ ±1 + giftWrap ผิดชนิด | ไม่ได้วัดในรอบจริง | ฿1,499/฿1,500 (TC-GIFT-03/04) · ฿998/฿999 (08/09) · `"true"` `1` `"yes"` `null` (TC-GIFT-12 ×4) + TC-GIFT-13 · หมายเหตุ: ตะกร้าขอบได้รับอิทธิพลจาก 🎯 (ดูหมายเหตุ LAB 7) |
| ข้อ 16 | TC-GIFT แดง → เขียว · regression 3 เบราว์เซอร์ | ไม่ได้วัดในรอบจริง | 18F/3P → 21/21 · 77/77 ×3 (ทีละเบราว์เซอร์) · `test:all` รอบเดียว 185/231 เพราะสต็อก (วินิจฉัยแล้ว ไม่แก้ test/config) |
| ข้อ 17 | ตั้งใจแก้ = hash ต่าง = REA ต่าง | ไม่ได้วัดในรอบจริง | ต่าง 6 = unknown 6 ในคู่ข้ามเวอร์ชัน = ไฟล์ใน BUG-01.md + CR-01.md · `next-env.d.ts` (มีแค่ v1) อธิบายได้ 3 ทาง |
| ข้อ 18 | CHANGE-REPORT อ้างไฟล์ผล + evidence_id + rollback | ไม่ได้วัดในรอบจริง | หัวข้อ 5 อ้าง `CHANGE-PROOF.md` `out\cmp.json` (`ev_360083db`) `out\after\har.json` (`ev_b1e9e721`) ฯลฯ · มีแถว rollback ต่องาน |
| ข้อ 19 | ไม่ `-u` · ไม่แก้ test เดิม | ไม่ได้วัดในรอบจริง | ไม่รัน `-u` · `git diff --stat -- e2e-legacy TEST-DATA.md` ว่างทุก LAB · SHA-256 ของ `cr01-giftwrap.spec.ts` ไม่เปลี่ยนใน LAB 8 · ปรับเฉพาะ test ใหม่ของตัวเอง (`char-money` SHIP-02/03) ใน LAB 6 พร้อมเหตุผล |
| ข้อ 20 | PR-1 ครบวงจรในพรอมต์เดียว | ไม่ได้วัดในรอบจริง | LAB 10 เซสชันเดียว: ทำซ้ำ → test แดง 2F/2P → ถาม → ต้นเหตุ + impact → แก้ +5 −2 → 4/4 → regression 81 ×3 → CHANGE-REPORT |
| **รวม** | | ไม่ได้วัดในรอบจริง | ไม่ได้วัดในรอบจริง |

### 6.1 คำถามดี ๆ ที่ควรเกิด (และเกิดจริงในรอบถ่ายทำไหม)

| คำถาม | LAB | เกิดจริง |
|---|---|---|
| SUMMER20 ยังใช้ได้ไหม (HANDOVER บอกใช้ได้ถึงสิ้นปี แต่โค้ด/TEST-DATA บอกหมดอายุ) | 1 | ✅ CODEBASE-MAP ส่วน G (❌ + คำถามถึงร้าน) และ "ยังไม่รู้" |
| ถ้าจะแก้ข้อมูลสินค้า ต้องแก้ที่ API หรือ `lib/products.ts` | 1 | ✅ ส่วน G: "ต้องแก้ที่ `lib/products.ts` ใช่ไหม และมีระบบอื่น (แอปมือถือ?) ที่ใช้ `/api/products` อยู่หรือเปล่า" |
| ฿999 ส่งฟรีหรือไม่ (หน้าเว็บกับคำสั่งซื้อไม่ตรงกัน) | 4 · 5 | ✅ ตั้งแต่ LAB 1 (ส่วน G ⚠️ + "ยังไม่รู้") · LAB 4 เป็นผู้ต้องสงสัย S1 · LAB 5 ถามต่อเรื่องส่งฟรีนับก่อน/หลังส่วนลด |
| ฿1,500 ดูก่อนหรือหลังหักส่วนลด · FREESHIP/PAW10 เกี่ยวกับค่าห่อไหม · ต่อคำสั่งซื้อหรือต่อชิ้น | 7 | ✅ ครบทั้ง 4 เรื่องใน 8 คำถาม (Q1–Q6 ร้านตอบ: ก่อนหักส่วนลด · ไม่นับเข้าส่งฟรี/NEWCAT50 · PAW10 ไม่ลด · FREESHIP ไม่ยกเว้น · ต่อคำสั่งซื้อ · Q7 "ครบ" = ≥ และ Q8 /cart ไม่มีห่อ = สมมติฐาน ⚠️) |
| ข้อความที่ถูกเมื่อเพิ่มลงตะกร้าได้ไม่ครบ | 10 | ✅ ถามก่อนเขียนผลที่คาดหวัง ([D]/[R] ไม่มี) → ร้านตอบ "เพิ่มได้อีกเพียง {n} ชิ้น (สินค้าเหลือ {สต็อก} ชิ้น)" แบบแจ้งเตือน |

---

## 7. ปัญหาที่เจอระหว่างทำจริง / ข้อเสนอแก้พรอมต์

รวมจากหัวข้อ "ปัญหา / วิธีแก้" และ "ข้อเสนอแก้พรอมต์" ของทุก `_design/results/LAB*_RESULT.md` · สถานะ: ตัวเลขในหน้านี้มาจากพรอมต์ฉบับ `_design/PROMPTS.md` ที่ใช้รัน 12 ต.ค. 2026 · ข้อเสนอด้านล่างยังไม่ได้ยืนยันว่าปรับลง README ของบทแล้ว (ผู้ดูแลบทต้องตรวจทีละข้อ)

### 7.1 ข้อเสนอแก้พรอมต์

| LAB | ระดับ (H/M/m) | ปัญหาของพรอมต์ | ข้อเสนอ |
|---|---|---|---|
| 0 | M | `doctor` พ่น 2,829 บรรทัด | ใช้ `rea.ps1 doctor --filter-output healthy,checks` (~30 บรรทัด) |
| 0 | M | 🎯 บอก ExecutionPolicy "ส่วนใหญ่ Restricted/Undefined" | เพิ่ม "บางเครื่อง RemoteSigned · รันผ่าน Claude Code จะเห็น Process = Bypass ก็ปกติ" |
| 0 | m | คัด/แก้ scenario JSON ด้วย `Get-Content \| Set-Content` ทำภาษาไทยพัง | ระบุให้ใช้ `node -e` หรือ .NET `UTF8Encoding($false)` |
| 0 | m | compose ครั้งที่ 2 ใช้ cache เร็วมาก | บอกว่าไม่ถึง 3 นาทีก็ปกติ |
| 1 | M | agent ที่ถูกปฏิเสธขั้นแรกหยุดทั้งชุด · ข้อความปฏิเสธพูดว่า "directory" | แยกการทดสอบ deny เป็น 2 ข้อความในเซสชันใหม่ · อธิบายข้อความปฏิเสธใน README |
| 1 ↔ 5 | M | CODEBASE-MAP ชี้ต้นเหตุ PP-231 ตั้งแต่ LAB 1 | ผู้สอนตัดสินใจ: ยอมให้ชี้ แล้วเปลี่ยน LAB 5 เป็น "ยืนยันด้วยการรันจริงว่าแผนที่บอกจริง" |
| 1 | m | path ใน deny อาจถูกเขียนเป็น `**` แล้วจับ `tests/new/` | ระบุรูปแบบ `Edit(e2e-legacy/tests/*.ts)` |
| 1 | m | "shell ใช้ PowerShell" | เพิ่ม "(อ่านไฟล์ใช้เครื่องมืออ่านไฟล์ได้)" |
| 2 | M | progress ของ REA analyze 492 บรรทัดท่วม context | เติม `2>$null` หรือให้ `rea.ps1 -Out` ย่อ stderr |
| 2 | M | ไม่นิยาม ✅/⚠️/❓ และ "REA เห็น" นับ static หรือรวม server | นิยาม "❓ = ไม่อยู่ในรายการ endpoint ของ REA (กู้ชื่อไฟล์ได้ก็ยัง ❓)" |
| 2 | M | `rea-summarize` ไม่แสดงไฟล์ของ node `electron-renderer` / method | ปรับ helper (งานผู้ดูแลบท) |
| 2 | m | grep build เอง / HEALTHCHECK นับเป็นตาไหน · ข้อ 6(3) ไม่บอกแหล่งแนวทาง "เมื่อไรไม่ควรใช้ REA" · robocopy exit 1 แสดงเป็น error | ระบุในพรอมต์ |
| 3 | M | ส่วน A ขอ "ค่าตัวอย่าง" แต่ `rea-summarize` ไม่แสดงค่า และห้ามเปิดไฟล์ใหญ่ | เพิ่ม `--samples` ใน helper หรือบอกให้เขียนสคริปต์ใน `rea\scratch\` |
| 3 | M | คำสั่งมีรหัส demo ตรง ๆ แต่ ✔️ ห้ามรหัสใน .md | เพิ่ม "(ถ้าคัดคำสั่งลงเอกสาร ให้เขียน `<รหัส demo>`)" |
| 3 | m | summarize ตัด `term: ยอดชำระทั้งหมด` เหลือแค่ definition | ให้ filter เก็บคู่ term/definition |
| 4 | M | สต็อกร่วมของเทสต์ขนาน 3 เบราว์เซอร์ | เตือน "ชิ้นต่อ test × 3 ≤ สต็อก seed · อย่าใช้สินค้าของ TC-PRD-03/TC-CHK-04" |
| 4 | M | expected-fail ถูกนับรวมใน "passed" | บอกให้ดู `x` ใน list / tag `@known-issue` |
| 4 | m | "ปุ่มยืนยันสั่งซื้อ" / "หน้าคำสั่งซื้อ" · NEWCAT50 ไม่มีตะกร้า ฿500 พอดี | ระบุ testid `place-order` · `/orders/PP-…` · ใช้ค่าใกล้สุดสองฝั่งได้ |
| 5 | M | HAR อัดที่ localhost แต่ REA ไม่รับ | ระบุ `http://127.0.0.1:4000` |
| 5 | M | HAR ทั้ง run 40 MB | แนะนำ `recordHar: { urlFilter: /\/api\// }` หรือ `mode: 'minimal'` |
| 5 | m | ไม่ระบุที่วาง BUG-01.md · [D] กำกวมกรณี PAW10 · สต็อกชามกินช้า 18 · black-box ซ้ำกับ BASELINE | ระบุรากบท · ใบ้ invariant "ปุ่ม = คำสั่งซื้อ" · เตือนสต็อก · บอกให้หาหลักฐานใหม่ (ตะกร้าลูกค้า · /account · HAR) |
| 6 | M | ใช้สคริปต์ LAB 5 ซ้ำจะเขียนทับหลักฐานก่อนแก้ | เพิ่ม "คัดผลเดิมไป `out\bug01-before-fix\` ก่อน" |
| 6 | m | "(นาน ~3 นาที)" · ปรับ test คู่ควรเปลี่ยน tag/annotation ด้วย | "(ครั้งแรก ~3 นาที · แก้ไฟล์เดียวมักไม่ถึงนาที)" · ระบุเรื่อง tag |
| 7 | M | "API ส่ง giftWrap ผิดชนิด" ผลขึ้นกับว่าตรวจ field ไหม | บอก "ตรวจทั้งยอดและ field" หรือแยก guard กับข้อพิสูจน์ฟีเจอร์ |
| 7 | M | "ตั้ง timeout สั้นพอ" แต่ expect ยังรอ 8 วิจาก config | บอก `test.use({ actionTimeout: 5_000 })` + `expect.configure({ timeout: 3_000 })` ในไฟล์ |
| 7 | m | ตะกร้าตัวอย่างควรมีจริงในร้าน · ชื่อไทยจาก `Invoke-RestMethod` เพี้ยน | เติม "ตะกร้าที่มีจริง" · ใช้ `node -e "fetch(...)"` |
| 8 | **H** | `npm run test:all` รอบเดียวล้มแน่ถ้า spec LAB 7 ใช้สินค้าสต็อกน้อยซ้ำ ๆ → ผู้เรียนหยุดที่ "ชุดเดิมแดง" ทั้งที่โค้ดถูก | (ก) LAB 7 เพิ่มกติกาจำนวนชิ้น × 3 ≤ สต็อก · (ข) LAB 8 ข้อ 4 เพิ่ม "ล้มด้วย `สินค้าไม่พอ` / `qty-plus` กดไม่ได้ = สต็อกหมด → รัน `--project=<เบราว์เซอร์>` ทีละรอบ" |
| 8 | m | diff `lib/orders.ts` เทียบ `out\v1` รวม BUG-01 · "~3 นาที" · ไม่ชี้ `--reporter=list` | ระบุให้แยก +/− เอง · "1–3 นาที" · ชี้ reporter |
| 9 | M (เกือบ H) | `Get-FileHash` ไม่ใส่ `-LiteralPath` ได้ผลผิดเงียบ ๆ กับ `[id]` `[slug]` | เขียน `-LiteralPath` และ "ตรวจตัวนับกับ `git status --short petshop`" |
| 9 | M | `import-reference-source` ไม่มี evidence_id | ให้ใช้ `root_sha256_short` |
| 9 | M | `rea-summarize` แสดงแค่ key ชั้นบน (ไม่เห็น `order.giftWrap`) | ให้ helper แสดง key ชั้นที่ 2 หรืออนุญาต `rea\scratch\` |
| 9 | m | หลักฐาน test รันใหม่หรือใช้ผลเดิม · `--s2b-table` แสดงเฉพาะไฟล์ที่ต่าง | "อ้างผลใน CR-01.md/BUG-01.md ได้ · ถ้ารันใหม่ใช้ `--project=`" · อธิบาย `--s2b-table` |
| 10 | M | `test:all` ล้มแน่ในรอบเดียว (สต็อกร่วม) | เพิ่มทางรันทีละเบราว์เซอร์ หรือแก้ reset ต่อ project ก่อนแจกบท |
| 10 | M | "เพิ่มแถว PR-1" แต่ตาราง CHANGE-REPORT เป็นแนวตั้ง | "แถวหรือคอลัมน์ตามรูปแบบเดิม" |
| 10 | m | "แจ้งเตือน" ใช้ toast แบบไหน · ตัวเลือกจำนวนหยุดที่สต็อก · toast หายใน 2.8 วิ | ให้ถามชนิด toast · บอกเรื่อง max · อธิบาย flaky ใน README |

### 7.2 ปัญหาที่เจอระหว่างทำจริง

| ปัญหา | เกิดที่ | วิธีรับมือ |
|---|---|---|
| `doctor` output ยาวจนถูกตัด | LAB 0 | วัดด้วยการเก็บในตัวแปร · เสนอ `--filter-output` |
| PS 5.1 แสดง/เขียนภาษาไทยเพี้ยน (`Get-Content` · `Invoke-RestMethod`) | LAB 0 4 7 | .NET `UTF8Encoding($false)` · อ่าน API ด้วย node `fetch` |
| เซสชันทดสอบ deny หยุดหลังขั้นแรก | LAB 1 | เปิดเซสชันใหม่อีกครั้งเฉพาะขั้นสร้างไฟล์ใน `tests/new/` → ได้ |
| `w/CLAUDE.md` / settings ไม่ถูกบังคับใน session ของ runner (cwd ≠ `w/`) | LAB 0–10 | runner ทำตามเอง · ตรวจ `git diff --stat -- e2e-legacy TEST-DATA.md` ว่างทุก LAB |
| stderr progress ของ REA ท่วม output (88 KB · 173 KB ใน LAB 9) | LAB 2 9 | redirect stderr ไปไฟล์ / `2>$null` |
| robocopy exit 1 ถูกแสดงเป็น error | LAB 2 9 | 0–7 = สำเร็จ (พรอมต์บอกไว้แล้ว) |
| `scenario` ได้ `completeness: incomplete` (`missing_sections: events`) + request-failed 23 (RSC prefetch `ERR_ABORTED`) | LAB 0 3 | ปกติ ไม่ใช่ scenario พัง |
| นับผล list reporter ด้วย `Select-String` ได้ 0 (เลขลำดับ pad ช่องว่าง) | LAB 4 | สคริปต์นับด้วย regex `\s+\d+` |
| ไม่มีชุดอาหารแมวรวม ฿500 พอดี | LAB 4 | golden ใช้ ฿499 / ฿520 |
| สคริปต์ LAB 5 เขียนทับหลักฐานก่อนแก้ | LAB 6 | สำรองไป `out\bug01-before-fix\` ก่อนรัน |
| runner อ่าน 🎯 ก่อนคิดตัวเลข | LAB 7 8 | จดตามจริง · ตัวเลขทุกค่ายืนยันจากการรัน |
| `test:all` รอบเดียวล้ม 46 / 47 ข้อ (409 "สินค้าไม่พอ" · `qty-plus` disabled) | LAB 8 10 | วัดสต็อกยืนยันสาเหตุ → รันทีละเบราว์เซอร์ 77/77 และ 81/81 ×3 · ไม่แก้ test/config |
| Python ต่อท้าย CR-01.md: `out\v1` กลายเป็น `out<VT>1` | LAB 8 | หา control char แล้วแทนกลับ |
| `function H` ชน alias `Get-History` · `Get-FileHash` คืนค่าว่างกับ `[id]` | LAB 9 | เปลี่ยนชื่อฟังก์ชัน · ใช้ `-LiteralPath` · ตรวจ hash ว่าง = 0 |
| `rea-summarize` ไม่แสดง key ชั้นในของ response | LAB 9 | จดเป็น "พิสูจน์ไม่ได้" (ledger O18 ⚪) |
| spec PR-1 รอบแรกแดงผิดเหตุ (`item-qty` เป็น input) | LAB 10 | แก้ spec เป็น `toHaveValue` ก่อนแก้โค้ด → 2F/2P |
| `Out-File` ไปโฟลเดอร์ที่ยังไม่มี | LAB 10 | สร้างโฟลเดอร์แล้วรันใหม่ |

### 7.3 สิ่งที่ต้องยืนยันตอนรันจริง (จาก `LESSON-PLAN` §9)

| เรื่อง | ผลรอบนี้ |
|---|---|
| ทางสำรอง `host.docker.internal:4000` (node fetch + Chromium ใน container) | ✅ ทั้ง 2 ชั้น: node fetch → `{"ok":true}` 0.7 วิ · `capture-browser-scenario` 11/11 steps 3.5 วิ (`ev_0d023efd`) · ไม่พบปัญหา IPv6 |
| compose project `pawpantry05` / network `pawpantry05_default` ไม่ชนบทอื่น | ✅ `docker compose config` → `name: pawpantry05` · network `pawpantry05_default` มี · ไม่มี container ชื่อซ้ำ · บท 06 (`sabai06-*`) อยู่ 4100/5533 |
| ExecutionPolicy / shell ที่ agent ใช้จริง | CurrentUser RemoteSigned · Process Bypass · คำสั่งในพรอมต์รันด้วย PowerShell tool (Windows PowerShell 5.1) ทุก LAB · Git Bash ใช้อ่าน/นับ/grep (และเขียน settings.json ใน LAB 1) |
| คำสั่งนาน > 2 นาที (timeout · agent สั่งซ้ำไหม) | build v1 159 s · build v2 155.2 s (รันเบื้องหลัง) · `test:all` 244 s / 288.7 s · ตั้ง timeout 10–20 นาที · **ไม่มีการสั่งซ้ำเพราะ timeout** |
| suite บท 02 กับ build ที่เอา BUG_MODE ออก + มี BUG-01 | `grep bug_mode` = 0 · ชุดเดิม 40/40 chromium · 120/120 3 เบราว์เซอร์ (เขียวทั้งที่มี BUG-01) |
| `.claude/settings.json` deny · agent เลี่ยงผ่าน shell ไหม | ไม่เลี่ยง · `git diff --stat -- e2e-legacy TEST-DATA.md` ว่างทุก LAB · SHA-256 `01-home.spec.ts` ก่อน/หลังทดสอบเท่ากัน · รั้ว: แก้ test เดิม = ปฏิเสธ · สร้างใน `tests/new/` = ได้ |
| CODEBASE-MAP ทำให้ LAB 5 ไม่ black-box ไหม | **ใช่** · ส่วน D ของ LAB 1 มี `lib/orders.ts:63-67` + `>` + PP-231 · Explore เจอค่าขอบ ฿999 เอง · คุณค่าของขั้น black-box จึงอยู่ที่หลักฐานใหม่ (ตะกร้าลูกค้า · /account · ฿1,000 · PAW10 · HAR) |
| test ใหม่รันขนานกับชุดเดิม นิ่งไหม (รัน 2 รอบ) | LAB 4: `tests/new` 2 รอบเท่ากัน (6 + 1 expected-fail) · ร่วมชุดเดิม 3 เบราว์เซอร์ 141 passed · 0 flaky · **แต่หลัง LAB 7** `test:all` รอบเดียวล้มเพราะสต็อกร่วม (LAB 8 46 ข้อ · LAB 10 47 ข้อ) · TC-PR1-03 firefox ไม่เห็น toast 1 ครั้งในรอบหนัก (`--repeat-each=3` ลำพังผ่าน 12/12) |
| ไฟล์ที่ CR-01 / PR-1 แตะจริง เทียบ `CR-DESIGN` §1.4 | CR-01: 6 ไฟล์ตรง §1.4 ทุกไฟล์ (pricing · orders · store · OrderSummary · CheckoutForm · `app/orders/[id]/page.tsx`) · +60 −8 (prototype +60/−9) · PR-1: `components/ProductCard.tsx` ไฟล์เดียว +5 −2 |
| เวลา build image REA | ไม่ได้วัดในรอบจริง (image มีอยู่แล้ว · 2,654,494,021 bytes) |

---

## 8. เปิดเว็บเฉลยและรันซ้ำ

> พอร์ต 4000 ใช้ร่วมกับบท 06 → ปิดบท 06 ก่อน (`docker compose down` ในโฟลเดอร์ web ของบท 06) · compose project ของบทนี้ชื่อ `pawpantry05` (ไม่ชนบท 02/03)

### 8.1 เปิดเว็บ (PowerShell จากรากบท)

```powershell
# ระบบเดิมตอนเริ่มบท (มี BUG-01) = โฟลเดอร์ petshop ของบท
cd petshop
docker compose up -d --build                          # นาน ~3 นาที · container pawpantry05 · http://localhost:4000
Invoke-RestMethod http://localhost:4000/api/health    # ok = True
Invoke-RestMethod -Method Post http://localhost:4000/api/test/reset
cd ..
```

ระบบหลังแก้ (BUG-01 + CR-01 + PR-1): ทำใน **สำเนา** ของโฟลเดอร์บท (อย่าทับ `petshop/` ของบทจริง) แล้วคัด 7 ไฟล์ใน `_solution/petshop/` ทับตำแหน่งเดิม จากนั้น compose up ตามปกติ

```powershell
# จากรากของสำเนาโฟลเดอร์บท
robocopy _solution\petshop petshop /E      # exit 1 = คัดลอกสำเร็จ · คัด 7 ไฟล์ (ใช้ robocopy เพราะ path มี [id])
cd petshop; docker compose up -d --build; cd ..
```

ดูการเปลี่ยนแปลงทั้งหมดได้ที่ [petshop-solution.diff](petshop-solution.diff) (unified diff เทียบโฟลเดอร์ตั้งต้น · path `a/petshop/…` · ใช้ `git apply` ได้ในสำเนาที่ไม่ใช่ git repo ย่อยของ repo คอร์ส)

### 8.2 รัน test

```powershell
cd e2e-legacy
npm install
npx playwright install chromium firefox webkit   # ครั้งแรกครั้งเดียว · นาน ~3 นาที
npx playwright test                              # chromium · ชุดเดิม + tests/new
npm run test:all                                 # 3 เบราว์เซอร์
```

- ผลที่ควรได้บน **ระบบเดิม**: ชุดเดิมเขียวครบ (120/120 · 3 เบราว์เซอร์) · `bug01-shipping` แดง · `cr01-giftwrap` แดง
- ผลที่ควรได้บน **ระบบหลังแก้**: 81/81 ต่อเบราว์เซอร์ (ชุดเดิม 40 + tests/new 41) เมื่อรันทีละเบราว์เซอร์ `npx playwright test --project=chromium` / `firefox` / `webkit` · `npm run test:all` รอบเดียวได้ 196/243 เพราะสต็อกร่วมหมด (409 "สินค้าไม่พอ") — ไม่ใช่โค้ดผิด
- test ของเฉลยอยู่ที่ `_solution/e2e-legacy/tests/new/` (4 spec + `golden/` 2 ไฟล์ · 41 test) · คัดไป `e2e-legacy/tests/new/` ก่อนรัน

### 8.3 ตรวจ BUG-01 ทาง API อย่างเดียว (ไม่ผ่าน UI)

ใช้สคริปต์ `verify-bug01.mjs` ใน `_design/LESSON-PLAN.md` §7.4 (Node 20+ · ไม่ต้องติดตั้งอะไร) · ระบบเดิมต้องพิมพ์ `999-standard total=1049` … `ALL OK` (ค่าของ "ระบบที่มีบั๊ก") · บนระบบหลังแก้แถวแรกต้องเป็น 999 และแถว PAW10 ต้องเป็น 900 (สคริปต์จะพิมพ์ `MISMATCH` เพราะค่า `want` ในสคริปต์คือค่าของระบบที่มีบั๊ก) · สต็อกลดทุกครั้งที่รัน → `POST /api/test/reset` ก่อนรันซ้ำ

### 8.4 REA

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 doctor
# ที่เหลือดูคำสั่งในพรอมต์ LAB 2 3 9 ของ README
```

ผล REA ที่เก็บไว้ในเฉลย: เฉพาะไฟล์เล็ก — `out/trace-coupon.json` (262,894 B · `ev_d404eddd`) · `out/s2b-v1src-v1build.json` `s2b-v1src-v2build.json` `s2b-v2src-v1build.json` `s2b-v2src-v2build.json` (~257–269 KB · `ev_23cd4cec` `ev_b034f50f` `ev_ba4bd111` `ev_f47a7dd1`) · `out/v1-src.json` `out/v2-src.json` (58,226 B) · `out/scenario-final.png` · ผล analyze (`v1-static` `v1-server` `v2-server` ~54 MB) · `cmp.json` (9.3 MB) · `scenario.json` (4.5 MB) · HAR และ `har.json` **ไม่เก็บ** (ใหญ่ / มีค่าลับ) → สร้างใหม่ด้วยคำสั่งในพรอมต์ LAB 2 3 9 · สรุปตัวเลขของทุกผลอยู่ใน `CHANGE-PROOF.md` §0 และ `_design/results/LAB2_RESULT.md` `LAB3_RESULT.md` `LAB9_RESULT.md`

ปิดงาน: `docker compose down` ในโฟลเดอร์ `petshop` (ลบเฉพาะ project `pawpantry05`) · ไม่ต้องลบ image `rea-lab:6.4.0`
