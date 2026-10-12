# LAB 3 RESULT · Agent อ่าน repo + DB → แผนที่ระบบ (บท 06 สบายใจ สปา)

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 10:03:23 |
| เวลาจบ (งานตามพรอมต์ ส่วน 1+2) | 10:12:05 · เขียน result เสร็จ ~10:16 |
| เวลาที่ใช้ | ~9 นาที ตามพรอมต์ (อ่านโค้ด/infra ~4 นาที · psql + pg_constraint < 1 วิ/คำสั่ง · ยิง runtime 2 ชุด · เขียน 2 ไฟล์ ~3 นาที · ตรวจทาน 5 แถว ~1 นาที) — runner อ่านเอง ไม่ได้ใช้ Explore subagent |
| ไฟล์ที่สร้าง/แก้ใน w/ | สร้าง `SYSTEM-MAP.md` (~46 KB) · สร้าง `docs/SPEC-GAPS.md` (~10.8 KB) · **ไม่แก้โค้ด** · `git status --short` ตอนจบ: ` M HANDOVER-CHECK.md` (ค้างจาก LAB 1) · `?? SYSTEM-MAP.md` · `?? docs/` |
| สคริปต์ชั่วคราว / log | `tools/lab3/`: `files.txt` (git ls-files) · `routes.txt` (route ทุกไฟล์พร้อมเลขบรรทัด) · `dt.txt` `d_booking.txt` `d_booking_slot.txt` `d_birthday_use.txt` · `constraints.txt` (pg_constraint 107 แถว) · `price-gc-transport.json` |
| ภาพ | ไม่มี (RUNNER §6 ไม่กำหนดภาพของ LAB 3) |
| สถานะเว็บตอนจบ | `sabai06-web` + `sabai06-db` เปิดค้าง healthy · `GET http://localhost:4100/api/health` → `{"ok":true,"db":true}` |
| ข้อมูลทดสอบ | **ไม่ได้ reset** (พรอมต์ไม่ต้องใช้ seed state · อ่าน schema อย่างเดียว) · DB ยังเป็นสถานะหลัง LAB 2 (B14 จองแล้ว · B05 ยกเลิก) · `/api/test/today` → `2026-10-10T10:00:00+07:00` · การยิงทดสอบใน LAB นี้เป็น GET/`POST /api/price` + login (ไม่เขียนข้อมูล) |
| พอร์ตที่ใช้จริง | เว็บ **4100**→3000 · db **5533**→5432 (D10) · psql ผ่าน `docker exec sabai06-db` (ไม่ใช้พอร์ต host) · runtime check ยิง `http://localhost:4100` · **README ต้องแปลงเป็น 4000** (ใน SYSTEM-MAP เขียนค่า compose `${WEB_PORT:-4000}` และระบุว่ารอบนี้รัน 4100 เฉพาะแถว runtime) |
| เซสชัน / โหมดสิทธิ์ | runner (Agent tool) ทำแทนเซสชันใหม่ของผู้เรียน · โหมด A · ส่วนที่ 2 = เซสชันเดียวกัน (ต่อเนื่องใน runner เดียว) · ไม่ได้เปิด `yolo.cmd` · ไม่มี Plan mode ใน LAB นี้ |
| commit ที่ใช้ทำแผนที่ | `3526f06` (= baseline `4a7908f` + 2 commit ของ orchestrator: rea-tools subcommands, fast_track sync — ไม่ใช่งานผู้เรียน) · ผู้เรียนจริงจะเห็น hash อื่น |

## 2. ข้อห้ามที่ทำตาม และจุดที่ทำต่างจากพรอมต์

- **ไม่แก้โค้ด** ใน `web/` `db/` `e2e-legacy/` `tools/` · ไม่เปิด `_solution/` (ไม่มีใน w/) · ไม่เปิด `CHANGE-REQUESTS/answers/` · ไม่รัน `check-rules.mjs` (ไม่ได้สั่ง)
- `w/CLAUDE.md` และ `w/.claude/settings.json` **ยังไม่มี** (LAB 4 สร้าง) → ไม่มีรั้วให้ self-enforce นอกจากข้อห้ามในพรอมต์
- "รันคำสั่งด้วย PowerShell": คำสั่ง psql 3 ตัวของพรอมต์รันซ้ำด้วยเครื่องมือ PowerShell ยืนยันผล (`(19 rows)` · `\d booking` 78 บรรทัด EXCLUDE 1 · `\d booking_slot` EXCLUDE 1 · `git rev-parse --short HEAD` = `3526f06`) · การอ่านไฟล์/grep/นับ ใช้ Git Bash + Read (เครื่องมืออ่าน ไม่เปลี่ยนสถานะ) — ผลเท่ากัน
- เพิ่มคำสั่งนอกพรอมต์ (อ่านอย่างเดียว): `SELECT conrelid::regclass, contype, conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE connamespace='public'::regnamespace` เพื่อนับ CHECK/FK/EXCLUDE ทั้ง 19 ตาราง (พรอมต์สั่งแค่ `\d booking` `\d booking_slot`) · `\d birthday_use` ตอนตรวจทาน
- runtime check นอกพรอมต์ 2 ชุด (เพื่อยืนยันแถว ⚠️ ไม่ใช่เดา): `GET /api/transport?distance=5.04|5.05|15.04|15.05` · login U01 (บัญชีทดสอบที่หน้า login แสดง) + `POST /api/price` (ไม่บันทึก) — cookie ลบทิ้งหลังใช้
- ไม่มี git ที่เปลี่ยนสถานะ (พรอมต์ LAB 3 ไม่สั่ง commit) · ใช้ `git ls-files` / `git status` / `git rev-parse` (อ่านอย่างเดียว)
- ไม่แตะ `pawpantry05` (4000) และ `exref-*` (4200/5633)

## 3. คำตอบสรุปที่แสดงในแชท

### ส่วนที่ 1

> | หัวข้อ | จำนวนแถว | ข้อที่ยังไม่รู้ |
> |---|---|---|
> | 1 สถาปัตยกรรม (compose/network/container/พอร์ต/Dockerfile) + env | 13 + env 9 | ระบบจริงตั้ง `ALLOW_TEST_RESET` เท่าไร (U2) |
> | 2 ชั้นโค้ด + ตาราง route | 26 handler (25 ไฟล์ · GET 15 POST 11) | route ที่ UI ไม่เรียก 8 ตัว มีระบบภายนอกใช้ไหม (U3) |
> | 3 กฎร้าน BR-01–20 | 20 | — |
> | 4 ฐานข้อมูล | 19 ตาราง · CHECK 51 · FK 25 · PK 19 · UNIQUE 10 · EXCLUDE 2 | ห้องคู่จริงกี่ห้อง (U4) |
> | 5 Test hooks + นาฬิกา | 7 | — |
> | 6 กับดัก | 13 (T1–T13) | — |
> | 7 Triangulation | 23 แถว (✅ 17 · ⚠️ 6 · ❌ 0) | — |
> | 8 SPEC-GAPS (`docs/SPEC-GAPS.md`) | 13 คำถาม (กฎ 6 · ความปลอดภัย 2 · เอกสาร 5) | ทุกแถวยังไม่มีคำตอบ |
> | ยังไม่รู้ | 6 (U1–U6) | REQUIREMENTS/DESIGN/TEST-DATA ไม่มีใน repo (U1) · check-rules ยังไม่ได้รัน (U5) |
>
> commit `3526f06` · 2026-10-12

### ส่วนที่ 2 (ตรวจทาน 5 แถว · สุ่มด้วย `Math.random` → กฎ 6, 10 · route 24 · DB 8 · กับดัก 10)

> | แถวที่สุ่ม | ที่อ้าง | บรรทัดจริง | ตรงไหม | แก้อะไร |
> |---|---|---|---|---|
> | กฎ BR-06 | `pricing.ts:9-10` `:47-57` `:65` | `:9` `GROUP_DISCOUNT_MIN_PEOPLE = 4` · `:10` `GROUP_PCT = 10` · `:48` package/course → none · `:65` `bestPercent(input)` | ✅ | — |
> | กฎ BR-10 | `points.ts:3-4` `:10` `:15` · `pricing.ts:69` · `booking.ts:153-156` · `i18n.ts:103` `:106` | `POINT_BLOCK = 100` · `BLOCK_VALUE = 50_00` · `redeemPoints(...)` · POINTS_NOT_ENOUGH | ✅ | — |
> | route #24 POST /api/quiz | `quiz/route.ts:18` · `quizResult()` · `Quiz.tsx:29` | `:18` POST · `:22` validateAnswers · `:23` quizResult · `Quiz.tsx:29` fetch POST | ⚠️ ไม่ครบ | เติม `quiz.ts:104` `:110` (และ `QUIZ` `quiz.ts:12` ในแถว #23) |
> | DB `birthday_use` | PK `birthday_use_pkey` · year_month CHECK | psql: `PRIMARY KEY, btree (customer_id, year_month)` · `CHECK (year_month >= 200001 AND year_month <= 299912)` · FK 2 | ✅ (FK ขาด) | เติม FK 2 ตัว |
> | กับดัก T10 | "ตาราง §2" | `account/page.tsx:29` `:31` · `wallet/page.tsx:29` · `services/page.tsx:14` · `therapists/page.tsx:14` · `transport/page.tsx:17` | ❌ อ้างไม่ครบ | เติมไฟล์:บรรทัด 7 จุด + แก้ §2 ให้อ้าง `account/page.tsx:8` `:29` `:31` |
>
> ผล: ตรง 3/5 · ไม่ครบ 2/5 · ไม่มีแถวที่อ้างบรรทัดผิด · เพิ่มหัวข้อ "ตรวจทานโดยคน" ท้าย SYSTEM-MAP.md แล้ว

## 4. ตัวเลขสำคัญ (นับจากไฟล์/ผลจริง)

| ตัวเลข | ค่า | คำสั่งที่ใช้นับ |
|---|---|---|
| route ไฟล์ | **25** | `find web/app/api -name route.ts \| wc -l` |
| route handler | **26** (GET 15 · POST 11) | `grep -rhoE "export (async )?function (GET\|POST…)" web/app/api \| sort \| uniq -c` |
| handler ที่ component เรียก / `<img>` / healthcheck / ไม่มีผู้เรียกในเว็บ | 16 / 1 / 1 / **8** | grep `fetch(` + `/api/` ใน components, app, lib/bot |
| กฎร้าน | BR-01–BR-20 = **20** แถว · ไฟล์ rules 14 + index | `wc -l web/lib/rules/*.ts` (443 บรรทัดรวม) |
| ตาราง DB | **19** | `psql -c "\dt"` → `(19 rows)` |
| constraint | **CHECK 51 · FK 25 · PK 19 · UNIQUE 10 · EXCLUDE 2** (booking มี CHECK 23) | pg_constraint ของ schema public |
| EXCLUDE | `booking_room_no_overlap` · `booking_slot_no_overlap` | `\d booking` · `\d booking_slot` |
| กับดัก | 13 · `room_id = 1` **2 ที่** (`booking.ts:290` `:376`) | `grep -n "room_id = 1\|roomId = 1"` |
| triangulation | 23 แถว ✅ 17 ⚠️ 6 ❌ 0 · ทุกแถวมีป้าย [E]/[source]/[DB]/[SPEC] | นับในไฟล์ |
| SPEC-GAPS | **13** แถว | `grep -c "^\| G" docs/SPEC-GAPS.md` |
| runtime ค่ารถ | 5.04 กม. → ฟรี · 5.05 → ฿300 · **15.04 → ฿300 (รับ)** · 15.05 → OUT_OF_AREA | `GET /api/transport?distance=…&people=1` |
| runtime ฐานแต้ม | S01 + H04 + GC ฿500 (U01 Gold) → gross 1000 · discount 50 · transport 300 · total 1250 · GC 500 · **pointsToEarn 4** | login + `POST /api/price` |
| ขนาดไฟล์ | SYSTEM-MAP.md 45,931 B (ก่อนเติมส่วนตรวจทาน) · SPEC-GAPS.md 10,798 B | `wc -c` |

## 5. ตัวอย่างแถวเด่นสำหรับ README

1. **route** `GET /api/slots` → `availableSlots()` `booking.ts:308` · เรียกจาก `BookingWizard.tsx:144` ด้วย template literal → อธิบายได้ว่าทำไม REA static ไม่เห็น (ยืนยัน inference ของ LAB 2)
2. **กฎ** BR-01 ค่าคงที่ `OPEN_MIN`/`CLOSE_MIN` `slots.ts:4-5` · ข้อความซ้ำ `i18n.ts:37` `:53` + `chat.ts:64-66` (กับดัก T7)
3. **DB** `booking_slot_no_overlap` EXCLUDE (therapist_id =, period &&) WHERE (active) ↔ `overlap.ts:14` `freeTherapists()` · ชนพร้อมกัน → `23P01` → 409 SLOT_TAKEN `http.ts:42`
4. **กับดัก** T1 `room_id = 1` 2 ที่ · T2 `TABLES` `testmode.ts:11-15` · T3 init รันเฉพาะ volume ว่าง · T5 `PackageCalc.tsx:24` คิดราคาซ้ำ
5. **triangulation ⚠️** BR-17: [source `transport.ts:19-22`] ปัดทศนิยม · [runtime 15.04 กม. รับ ฿300] · [DB `booking_distance_km_check` ≤ 15.0] · [SPEC BR-17 "> 15 ไม่รับ"] → SPEC-GAPS G4
6. **SPEC-GAPS** G1: SPEC ใช้ `sabai-net`/`sabai-db`/`sabai-web`/`localhost:3000` ↔ compose `sabai06-*` + `${WEB_PORT:-4000}`

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบที่เลือก | เหตุผล |
|---|---|---|
| "ตาราง route ทุกตัว" นับต่อไฟล์หรือต่อ method | ต่อ handler (method+path) = 26 แถว และระบุว่า 25 ไฟล์ | `/api/quiz` มีทั้ง GET และ POST ผู้เรียกต่างกัน |
| ใช้ Explore subagent ไหม | ไม่ใช้ (runner อ่านเอง) | repo เล็ก (165 ไฟล์) · ลด context ซ้ำ · ทุกแถวต้องอ้างบรรทัดที่เปิดจริงอยู่แล้ว |
| สุ่ม 5 แถวอย่างไร | `node -e Math.random` ต่อหมวด | กันเลือกแถวที่มั่นใจ (cherry-pick) |
| แถวที่ SPEC เงียบ (เช่น complete ก่อนเวลานัด, owner ยกเลิก < 24 ชม.) | ใส่ใน SPEC-GAPS เป็นคำถาม โดยระบุว่า SPEC "ไม่ระบุ" | พรอมต์ห้ามตัดสินเอง · เป็นช่องว่างของเอกสาร |
| reset ก่อนทำไหม | ไม่ reset | อ่าน schema/โค้ด ไม่ต้องใช้ seed state · ระบุใน "ยังไม่รู้" U6 ว่า DB ไม่ใช่ seed ล้วน |

## 7. ข้อสังเกต 👀

- `\d booking` + `\d booking_slot` อย่างเดียว **ไม่พอ** นับ CHECK/FK ของทั้งระบบ — ต้องใช้ `pg_constraint` (พรอมต์ไม่ได้บอก) · ถ้า agent นับจาก `\d` 2 ตารางจะได้ CHECK 23 / FK 6
- หัวไฟล์ schema เขียน "ERD 17 ตาราง" แต่ DB มี 19 (คอมเมนต์อธิบาย +hotel +therapist_service) — agent อาจคัดเลข 17 ผิด
- grep หา endpoint ด้วย `"/api/` พลาด template literal `` `/api/slots?${q}` `` 4 จุด — บทเรียนเดียวกับที่ REA static พลาด (เชื่อมกับ LAB 2 ได้ดี)
- 8 route ไม่มีผู้เรียกในเว็บเพราะหน้าเป็น server component เรียก lib ตรง — ตอบคำถามข้อ 2 ของ REA-INVENTORY §5 ได้ตรง
- นาฬิกา: `ALLOW_TEST_RESET` ค่าเริ่มต้น 1 ทั้งใน compose และ `config.ts` + seed มี `test_today` → ถ้าส่งขึ้นจริงแบบค่าเริ่มต้น "วันนี้" ค้าง 10 ต.ค. 2026 และใครก็ reset ได้ (กับดัก T9 · G7)
- การตรวจทาน 5 แถวไม่เจอบรรทัดผิดเลย เจอแค่ "อ้างไม่ครบ" (อ้างตารางในไฟล์ตัวเอง / อ้างชื่อฟังก์ชันไม่มีบรรทัด) — ข้อผิดพลาดแบบนี้เกิดจริงเมื่อ agent เขียนเร็ว เหมาะเป็นตัวอย่างใน README

## 8. เจอระหว่างทาง (นอก CR)

> ผู้เขียน README คัดกรองก่อนใช้ · ทุกข้อเป็น "คำถาม" ใน SPEC-GAPS ไม่ได้ตัดสินว่าเป็นบั๊ก

| # | เรื่อง | หลักฐาน |
|---|---|---|
| X1 | ระยะรถปัดทศนิยม 1 ก่อนเทียบ: 15.04 กม. รับ · 5.04 กม. ฟรี (G4) | `transport.ts:19-22` · runtime |
| X2 | ฐานแต้มหัก Gift Card ทั้งก้อนแม้บัตรจ่ายค่ารถ (G5) | `points.ts:29-31` · runtime pointsToEarn 4 |
| X3 | แพ็กเกจไม่ได้ส่วนลดระดับสมาชิก (SPEC เงียบ) (G6) | `pricing.ts:48` |
| X4 | 🔒 **กด "ใช้บริการเสร็จ" ได้ก่อนเวลานัด** (G9) — ตรงกับ S4/L2 = ข้อสอบชุด B ข้อ 5 → **ห้ามคัดลง README/ภาพ lab3-*** เก็บใน `_solution` เท่านั้น | `booking.ts:493-501` |
| X5 | owner ยกเลิก < 24 ชม. ไม่ได้ และ /admin ไม่มีปุ่มยกเลิก (G13) | `booking.ts:465-467` · `AdminQueue.tsx:100` |
| X6 | `/api/test/reset` เปิดเป็นค่าเริ่มต้น ไม่ต้องล็อกอิน + นาฬิกาค้าง (G7) | `compose.yaml:19` · `config.ts:5` · `reset/route.ts:8-13` |
| X7 | logout ไม่ revoke token (stateless 7 วัน) (G8) | `logout/route.ts:7-8` · `session.ts:26-41` |
| X8 | input จำนวนคนในหน้าจอง `max={20}` ขณะที่กฎสูงสุด 6 (เซิร์ฟเวอร์ตอบ GROUP_CALL_SHOP อยู่แล้ว) | `BookingWizard.tsx:331` |
| X9 | คิวหลังร้าน join `booking_slot` ไม่กรอง `active` → นัดที่ยกเลิกยังแสดงชื่อนักบำบัด (ไม่ได้ยืนยัน runtime) | `web/lib/server/admin.ts:15` |

## 9. ปัญหาที่เจอ / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| เผลออ่าน "ผลที่คาด" ของ LAB 3 ก่อนเริ่ม: การ Read PROMPTS.md ช่วงบรรทัด 106–140 ครอบบรรทัด 135–137 (ผลที่คาด + 🔒) ไปด้วย | เปิดเผยไว้ตรงนี้ · ตัวเลขทุกตัวมาจากคำสั่งจริง (ไม่ได้ปรับให้ตรง) · X4/G9 เจอระหว่างอ่าน `completeBooking` แต่ยอมรับว่าเคยเห็นคำว่า S4 ก่อน → ข้อ X4 อาจถูกชี้นำบางส่วน · ข้อเสนอแก้ RUNNER ข้อ 10 |
| `sed -n 213-219p` ผิด syntax (ใช้ `-` แทน `,`) | ไม่กระทบผล (ข้อมูลเดียวกันได้จาก psql `\d birthday_use`) |
| เลขบรรทัดของไฟล์ที่ cat ต่อกันหลายไฟล์เป็นเลขรวม | grep -n ต่อไฟล์ยืนยันใหม่ก่อนเขียน (แก้ `session.ts:186` → `:37` ก่อนตรวจทาน) |

## 10. ข้อเสนอแก้พรอมต์

| ระดับ | ข้อเสนอ |
|---|---|
| H | ข้อ 4 เพิ่มคำสั่งนับ constraint ทั้งระบบ เช่น `docker exec sabai06-db psql -U sabai -d sabai -c "SELECT contype, count(*) FROM pg_constraint WHERE connamespace='public'::regnamespace GROUP BY 1"` — ไม่งั้นผลที่คาด "CHECK 51 · FK 25" ไม่มีขั้นที่ทำให้ได้ตัวเลขนี้ |
| H | ข้อ 2 ระบุหน่วยนับ: "นับเป็น handler (method + path)" — ไฟล์ 25 / handler 26 ทำให้ผลที่คาด "route 25" กำกวม |
| M | ส่วนที่ 2 ให้ "สุ่มด้วยคำสั่ง" (เช่น `Get-Random`) แทนให้ agent เลือกเอง — กันเลือกแถวที่ถูกอยู่แล้ว |
| M | ข้อ 7 บอกว่าแถวที่ REA ไม่เห็นเลย (กฎฝั่งเซิร์ฟเวอร์) ให้ใส่ "REA ไม่เห็น" + เหตุผล ได้ (ไม่ต้องมี ev_) — ตอนนี้ "ทุกช่องต้องมีป้ายแหล่ง" อาจทำให้ agent แต่ง ev_ |
| M | ข้อ 5–6 บอกให้เทียบ `ALLOW_TEST_RESET` ค่าเริ่มต้นกับ "ระบบจริง" — เป็นกับดักสำคัญ (นาฬิกาค้าง/ reset เปิด) ที่ไม่อยู่ในรายการผลที่คาด |
| L (RUNNER) | แยก "ผลที่คาด" ออกจากบล็อกพรอมต์ด้วยหัวข้อหรือไฟล์ต่างหาก · runner ที่อ่านด้วยช่วงบรรทัดจะเห็นผลที่คาดทันที (เกิดใน LAB นี้) |

## 11. ภาพที่ควรใช้ + เทียบกับผลที่คาด

ภาพ: ไม่มี (RUNNER §6 ไม่กำหนด) · ถ้า README ต้องการภาพ ควรเป็นตาราง triangulation หรือตารางตรวจทาน (render จาก md) โดย **ตัดแถว G9/X4 ออก** (🔒)

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| route 25 | 25 ไฟล์ · 26 handler | ✅ (ต่างที่หน่วยนับ) |
| BR-01–20 ครบ | 20 แถว | ✅ |
| 19 ตาราง | 19 | ✅ |
| CHECK 51 · FK 25 · EXCLUDE 2 | CHECK 51 · FK 25 · EXCLUDE 2 (+ PK 19 · UNIQUE 10) | ✅ (ได้จาก pg_constraint ซึ่งพรอมต์ไม่ได้สั่ง) |
| กับดัก `room_id = 1` 2 ที่ | T1 `booking.ts:290` `:376` | ✅ |
| `TABLES` ใน `lib/server/testmode.ts` | T2 `testmode.ts:11-15` | ✅ |
| init รันเฉพาะ volume ว่าง | T3 | ✅ |
| `PackageCalc` คิดราคาซ้ำฝั่งเบราว์เซอร์ | T5 `PackageCalc.tsx:24` | ✅ |
| ข้อความเวลาเปิดซ้ำใน i18n/แชท | T7 `i18n.ts:37` `:53` · `chat.ts:64-66` | ✅ |
| SPEC-GAPS ≥ 7 แถว: S2 S3 S5–S9 + พอร์ต 3000/ชื่อ `sabai-*` | 13 แถว · มีพอร์ต/ชื่อเก่า (G1 G2 G3) · การจับคู่รหัส S2–S9 ทำไม่ได้ (นิยามอยู่ใน CODEBASE-NOTES ซึ่งห้ามเปิด) | ⚠️ จำนวนผ่าน · ต้องให้ผู้ตรวจจับคู่ S-code เอง |
| 🔒 S4 (กดเสร็จก่อนเวลานัด) ถ้ามี ห้ามลง README | มี (G9 / X4) · ทำเครื่องหมาย 🔒 แล้ว | ⚠️ ต้องตัดออกตอนเขียน README |
| ตรวจทาน 5 แถว | 5 แถว (✅ 3 · ไม่ครบ 2 · แก้แล้ว) | ✅ |
| triangulation ทุกช่องมีป้าย [E]/[source]/[DB]/[SPEC] | 23 แถว ทุกแถวมีป้าย · ช่อง REA ที่ไม่เห็นเขียน "REA ไม่เห็น" + เหตุผล | ✅ |

**การแปลงพอร์ตสำหรับ README:** รอบนี้ 4100/5533 → ผู้เรียน 4000/5433 · ใน `SYSTEM-MAP.md` มี 4100 แค่แถว "ตรวจ runtime" §5 และหัว SPEC-GAPS (`localhost:4100`) — ตอนคัดลง `_solution` ให้แทนเป็น 4000
