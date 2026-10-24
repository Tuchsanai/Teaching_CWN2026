# FT-RESULT · บท 06 fast_track 🅰️ (บอกใบ้) รันจริงแบบผู้เรียน

> คัดจาก C:/t/work/ft06/notes/FT-RESULT.md (รอบ fast track 🅰️ จริง 12 ต.ค. 2026 · รันที่ 4000/5433 ตรงกับผู้เรียน · ไม่มีรหัสผ่าน seed ในไฟล์) · ข้อแก้พรอมต์ P1–P4 ใส่ใน fast_track/README.md ทั้ง 🅰️/🅱️ แล้วโดย FINISHER (ยังไม่ได้รันซ้ำ)

| รายการ | ค่า |
|---|---|
| sandbox | `C:/t/work/ft06/w` (git repo ตั้งต้น `69c4c97`) · พอร์ต 4000/5433 · ชื่อ sabai06-* |
| เริ่ม | 12 ต.ค. 2569 13:23 |
| จบ | 14:58 (**หยุดกลางขั้น 11** — ดูปัญหา H1) |
| เวลา | **95 นาที** (ขั้น 0–10 ครบ + ขั้น 11 ①② บางส่วน · ขั้น 11 ③④ และขั้น 12 ไม่ได้ทำ) |
| วิธีรัน | วางพรอมต์ 🅰️ ทั้งก้อนในเซสชันนี้ ทำตามตัวอักษร (PowerShell สำหรับคำสั่งของพรอมต์) ไม่อ่าน README.md บท / EXAM.md / _solution · อ่าน fast_track/README.md เฉพาะส่วนวิธีใช้+พรอมต์ (ไม่อ่านพรอมต์ 🅱️) |

## เหตุที่หยุด (H1)

≈14:52–14:53 น. ระหว่างรัน e2e 3 เบราว์เซอร์ของขั้น 11 **Docker Engine ทั้งเครื่องถูกล้างจากภายนอก**: containers 0 · images 0 (รวม `rea-lab:6.4.0`) · volumes 0 (รวม `sabai06-pgdata` และ volume ของงานอื่นทั้งหมด เช่น `sabai-pgdata` `spa_sabai-db-data`) · network `sabai06-net` หาย · เห็น container ชื่อ `k8s-lab` สร้าง 14:53:10 แล้วหาย · Docker Desktop process ไม่ได้รีสตาร์ต (เริ่ม 10 ต.ค.)
หลักฐานในผล e2e-cr JSON: chromium ครบ 10 ข้อปกติ (14:51:38–14:52:07) · firefox 4 ข้อแรกผ่าน → CR05-UI-01 timeout (เริ่ม 14:52:22) → ข้อถัดไป ECONNREFUSED 127.0.0.1:4000 ตั้งแต่ 14:53:53 · e2e-legacy global-setup ล้มใน 1 วิ
คำสั่งของงานนี้ในช่วงนั้น: check-rules / golden / cr0N / Playwright / `docker cp` / `docker run --rm rea-lab` (analyze + compare) — **ไม่มี down -v, prune, rm volume** → เป็นเหตุจากภายนอก (น่าจะเป็น agent/lab อื่นที่สร้าง k8s-lab)
ตัดสินตามกติกาข้อ 8 ของพรอมต์ ("ข้อมูลนัดหาย/ระบบไม่ขึ้น → หยุดแล้วบอกผม"): **หยุด ไม่สร้างระบบใหม่เอง ไม่ build rea-lab ใหม่** · ⚠️ orchestrator ควรตรวจว่าใครล้าง Docker (volume `ai-accounts` ถ้าเคยมี ก็หายด้วย — ตอนนี้ `docker volume ls` ว่างทั้งเครื่อง)

## ไฟล์ที่ได้ (บรรทัด)

| ไฟล์ | บรรทัด | | ไฟล์ | บรรทัด |
|---|---|---|---|---|
| HANDOVER-CHECK.md | 82 | | tests/golden/run.mjs + README.md + 3 json | 197 + 50 (+ price 3,365 · slots 3,662 · queue 123) |
| docs/REA-INVENTORY.md | 118 | | tests/lib.mjs | 72 |
| SYSTEM-MAP.md | 161 | | tests/cr01–cr05.mjs | 143 · 83 · 117 · 94 · 81 |
| docs/SPEC-GAPS.md | 20 (14 แถว) | | tests/sql/cr05-report.sql | 31 |
| CLAUDE.md | 36 | | tests/smoke.mjs | 36 |
| .claude/settings.json | 10 | | e2e-cr/ (config + helpers + 6 spec) | helpers 64 · char 37 · KI 55 · cr01 18 · cr03 16 · cr04 16 · cr05 27 |
| docs/IMPACT-TEMPLATE.md · ORACLE-CHANGES.md | 30 · 7 | | db/migrations/001_shop_holiday(.down).sql | 18 · 4 |
| KNOWN-ISSUES.md | 14 | | web: reschedule.ts 108 · report.ts 85 · holidays.ts 26 · ReportView.tsx 101 · +route ใหม่ 5 · แก้ 10 ไฟล์ | `git diff --stat e2d816f..HEAD -- web db` |
| docs/impact/CR-01..05.md | 110 · 98 · 110 · 100 · 89 | | REGRESSION-REPORT.md (บางส่วน) | 68 |
| docs/TRACEABILITY.md | 38 | | CHANGE-REPORT.md | 82 |
| docs/MIGRATION-RUNBOOK.md | 34 | | **ไม่ได้ทำ**: docs/DEPLOY-RUNBOOK.md · RELEASE-NOTES.md · UAT-CHECKLIST.md · REGISTER "รอตรวจรับ" | - |

รวม `git diff --stat e2d816f..HEAD` = 66 ไฟล์ +10,128 −16 · commit 19 ตัว (baseline → regression report) · CR-02/03/04/05 สถานะ REGISTER = "ทดสอบผ่าน" · CR-01 "ทดสอบผ่าน"

## ตัวเลขสำคัญรายขั้น

| ขั้น | ผลจริง |
|---|---|
| 0 | ทุกอย่างพร้อม · 2970–3069 ถูกจอง (ครอบ 3000) · 4000/5433 ว่าง · rea doctor exit 0 · repo = โฟลเดอร์นี้ |
| 1 | db up 6.3 วิ · web build 9.7 วิ (layer cache) · Next 15.5.27 · Node 22.23.3 · PG 16.15 · check-rules 90/90 20.7 วิ · e2e-legacy api+chromium "41 passed · 1 failed" 4.0 นาที = **ผ่านจริง 38 · คาดว่าล้ม 3 · ล้ม 1 (TC-SEC-05: ได้ 422 COURSE_UNAVAILABLE แทน 403/404 — ระบบปฏิเสธจริง เทสต์คาดรหัสต่าง)** · คำอ้าง 16 ข้อ ✅ 9 · ❌ 2 (H6 reset "ปิดแล้ว" แต่ compose ค่าเริ่ม 1 · H8 "ผ่านทั้งหมดยกเว้น 3") · ⚠️ 5 · baseline `e2d816f` |
| 2 | static 53 วิ [E ev_31d69578] /api 9 + ชื่อ route 25 · coverage partial · unknown 7 · HAR 7 endpoint [E ev_f3f3a316] (B14 จอง · B05 ยกเลิก) · scenario 12/12 ฿1,000 [E ev_8ca541e9] · ตาราง endpoint 25 แถวติดป้าย runtime/static/inference |
| 3 | route.ts 25 ไฟล์ / 26 handler · 19 ตาราง · CHECK 51 · FK 25 · PK 19 · UNIQUE 10 · EXCLUDE 2 (ตรงพรอมต์) · เจอรายการตายตัว `TABLES` ใน testmode.ts · SPEC-GAPS 14 แถว เป็นคำถาม · ตรวจทาน 5 แถว (แก้เลขบรรทัดผิด 3 จุดจริง) |
| 4 | CLAUDE.md 36 บรรทัด · `claude -p` 14 วิ → "File is in a directory that is denied by your permission settings." · git status ไม่เปลี่ยน |
| 5 | seam `/api/test/clock` (reset→จอง B14→เลื่อน today 10→15 ต.ค. นัดยังอยู่ · ALLOW_TEST_RESET=0 → clock/reset/today 404 + หน้า login ไม่โชว์บัญชีทดสอบ) · golden 51+6+6 เคส ผ่าน 2/2 รอบ (1.2 วิ) · e2e-cr 15 passed (12 + คาดว่าล้ม 3) × 2 รอบ เท่ากัน (50.6/49.7 วิ) · KI 3 เรื่อง (KI-01 บั๊ก=คู่ lock+test.fail · KI-02/03 คำถามค้าง=lock อย่างเดียว) · X1/X2/X3: golden ❌(1/1/13 เคส) · check-rules ❌(E46 E51 / E78 E80 / 7 ข้อ) · e2e-cr ✅ไม่จับ → **ถูกจับ 3 รอด 0 (e2e-cr จับ 0)** |
| 6–10 | ดูตารางถัดไป |
| 11 | ① ก่อน Docker หาย: check-rules 90/90 · golden 51/6/6 · cr01–05 19/14/16/13/12 ครบ · e2e-cr chromium 9+1 · firefox/webkit ⚠️ ECONNREFUSED (เหตุภายนอก) · legacy ไม่ได้ผล ② REA v2 [E ev_fee38aad] + compare [E ev_5213fa32] changed 11 · /account เปลี่ยน · /admin/report ใหม่ (compare จัดเป็น unknown) ③④ ไม่ได้ทำ ⑥⑦ diff ครบ · oracle diff ว่าง |
| 12 | ไม่ได้ทำ (smoke.mjs เขียนแล้ว · รันหลังเหตุได้ 0/6 exit 1 เพราะเว็บหาย — ตรงพฤติกรรม "เว็บหยุด → exit 1" แต่ไม่ใช่การซ้อมตามขั้น) |

## ต่อ CR

| CR | คำถาม (ตอบ/ค้าง) | impact (แถว) | ค่าที่คาดหวัง | แดง → เขียว | regression | migration / อื่น |
|---|---|---|---|---|---|---|
| CR-02 | 7 (6/1) | 4 | 15 | cr02 7/14 → 14/14 | check-rules 90/90 diff 0 · golden ✅ · e2e-cr ✅ · legacy = รับมอบ | - |
| CR-03 | 9 (6+1/2) | 6 | 17 | cr03 6/16 → 16/16 · UI fail → pass (ครั้งแรกเขียวเลย เพราะวางตรวจซ้ำหลัง SLOT_TAKEN ตามใบ้ TC-BOOK-07) · ทำซ้ำเรื่องร้องเรียนได้ 201 B14 ซ้ำ B03 · U03 พร้อมกัน [201,201] | ✅ = รับมอบ (legacy) | - |
| CR-04 ก | 8 (5/3) | 10 | 15 | cr04 2/13 → 13/13 · UI fail → pass | ✅ = รับมอบ (⚠️ มีเทสต์แทรกระหว่าง legacy รอบนี้ ผลยังเท่าเดิม) | pg_dump 52,535 B · migration 2 รอบ exit 0 `INSERT 0 3` → `INSERT 0 0` · นัด B14 อยู่ · th_ok t · rebuild 38 วิ · reset 200/200 · fresh install 3 แถว 3.1 วิ · init ไม่รันซ้ำพิสูจน์ด้วย log "Skipping initialization" |
| CR-01 | 11 (7+1/3) | 7 | 20 | A 1/16 → 16/16 · B 0/3 → 3/3 · C UI fail → pass 3 เบราว์เซอร์ | **เต็ม 3 เบราว์เซอร์: legacy "113 passed · 1 failed" (106 + คาดว่าล้ม 7) 778 วิ = README-LEGACY** · e2e-cr 7+1 ×3 · ไม่เจอ webkit TC-UI-02 flaky | ตัวอย่าง B05→12 ต.ค. ฿760 · 10:01 TOO_LATE · B02 19:30 200 · B01 16:00 409 + slots ต่างกัน · คอร์ส reserved 1 |
| CR-05 | 10 (5+2/3) | 7 | 13 กลุ่ม (SQL ก่อนโค้ด) | cr05 0/12 → 12/12 · UI 2 fail → 6 pass (3 เบราว์เซอร์) | ✅ = รับมอบ | SQL: ก.ย. 0/3/1 ฿1,900 · ต.ค. ค้าง ฿11,130 · 6–9 ต.ค. 0 · 92/93 วัน · CSV BOM EF BB BF + ไทย · กดเสร็จ B01 → ฿2,440 = ผลรวมตารางคิว |

REA เทียบเวอร์ชัน (ขั้น 11 ②): CR-01 เห็น (account page changed) · CR-02 ไม่เห็น · CR-03/04 เห็นแค่ chunk ร่วม 8561 เปลี่ยน · CR-05 หน้าใหม่เห็นใน pages แต่ compare = unknown → 5 แถวในตาราง REGRESSION-REPORT ⑤ (HAR/scenario ไม่ได้ทำ)

## เรื่องที่ตัดสินแทนผู้เรียน

| # | เรื่อง | ตัดสิน |
|---|---|---|
| D1 | อนุมัติแผนทุก CR | อนุมัติเองเมื่อ impact ครบ 5 อย่าง (จดใน impact §8) |
| D2 | image `sabai06-web:before-cr04` ค้างจากรอบ LAB (สร้าง 2 ชม. ก่อน) | ไม่ลบ · ขั้น 8 tag ทับด้วย image ก่อน CR-04 ของรอบนี้ (id d1423b7b) |
| D3 | คำถามที่ร้านไม่ตอบ | CR-02 Q6 อัตราตามวันที่จอง · CR-03 Q5 เบอร์ต่างประเทศเหลือตัวเลขล้วน · Q9 owner โดนกฎเดียวกัน · CR-04 Q3 ตรวจนัดในวันหยุดด้วย SQL (=0) · Q4 ไม่แก้ปฏิทิน · Q6 ไม่แก้ "เปิดทุกวัน" · CR-01 Q3 วันหยุดเลื่อนไปไม่ได้ · Q6 กันทับนัดตัวเอง · Q10 ไม่เก็บประวัติ · CR-05 Q3 revenue รวมค่ารถ แสดงค่ารถแยก · Q5/Q6/Q8 นิยามแต้ม/คอร์ส/คิวต่อหมอนวด (ทั้งหมดติด ⚠️) |
| D4 | CR-04 ส่วน ข | ไม่ทำ (ตามพรอมต์) |
| D5 | KI-02 KI-03 | ล็อกอย่างเดียว (คำถามค้างใน SPEC-GAPS) · KI-01 = คู่ lock + test.fail |
| D6 | Docker ถูกล้างกลางขั้น 11 | หยุดตามกติกาข้อ 8 ไม่สร้างใหม่ |

## ปัญหา + ข้อเสนอแก้พรอมต์ (H = สูง · M = กลาง · m = ต่ำ)

| # | ระดับ | ปัญหา | ข้อเสนอ |
|---|---|---|---|
| P1 | H | Docker ทั้งเครื่องถูกล้างจากภายนอก (k8s-lab) กลางขั้น 11 → ขั้น 11 ③④ และ 12 ไม่ได้ทำ · volume ของงานอื่นหายด้วย | orchestrator: อย่ารันงานที่ reset Docker Desktop / prune ขนานกับ runner · พรอมต์: ตาราง 🆘 เพิ่มแถว "container/volume/image หายหมด" → บอกให้หยุด แล้วเริ่มใหม่ (db จาก init ที่แก้แล้ว + build rea-lab จากบท 05) และทำต่อจากขั้น 11 |
| P2 | M | agent (ผม) รันเทสต์ที่ reset DB ขณะ e2e-legacy รันอยู่เบื้องหลัง 1 ครั้ง (ฐานเดียวกัน) — ผลยังเท่าเดิมแต่เสี่ยง flaky ปลอม | กติกาข้อ 1: "ระหว่างชุดทดสอบรันแบบ background ห้ามรันสคริปต์/เทสต์ที่ reset หรือเขียนฐานข้อมูล ให้ทำงานเอกสารแทน" |
| P3 | M | agent ใช้ `git reset -q` (ยกเลิก stage) 2 ครั้งเพื่อแยกไฟล์ CR ถัดไปออกจาก commit — ผิดกติกาข้อ 6 (ไม่มีข้อมูลเสีย) · และ commit แก้ CR-02 พาแผน/เทสต์ CR-03 ติดไปเพราะ `git add -A` | วงจร ⑨: "git add เฉพาะไฟล์ของ CR นี้ (หรือเริ่มไฟล์ของ CR ถัดไปหลัง commit)" · อนุญาต `git restore --staged <ไฟล์>` ในรายการ git ที่ใช้ได้ |
| P4 | M | ขั้น 0 ไม่ตรวจ image `sabai06-web:before-cr04` ค้างจากรอบก่อน (หมายเหตุ 🔁 มีแต่ใน README) | ขั้น 0 เพิ่ม `docker images sabai06-web` (บอกอย่างเดียว) และกติกาข้อ 8: "มี before-cr04 ค้าง → tag ทับตอนขั้น 8" |
| P5 | m | โฟลเดอร์ตั้งต้นของ runner commit README.md/EXAM.md/fast_track ไว้แล้ว → `.git/info/exclude` ไม่มีผล (ผู้เรียนจริงที่ `git init` เองไม่เจอ) | ไม่ต้องแก้พรอมต์ (เป็นการตั้ง sandbox) |
| P6 | m | CR-04 ใบ้ "reset 2 ครั้งติดต้อง 200" — เทสต์ของผมนับวันหยุดผ่าน /api/holidays จึงแดงบนโค้ดเดิมด้วย (ต่างจากที่คาดใน impact 1 ข้อ) | ไม่ต้องแก้ · ดีที่บังคับบันทึกผลแดงจริง |
| P7 | m | ใบ้ CR-03 เรื่อง TC-BOOK-07 ทำให้วางลำดับถูกตั้งแต่แรก (เขียวรอบเดียว) · ใบ้ตัวเลขทุก CR ตรงผลจริง (CR-02 ฿2,850/4,250/5,100/3,000 · CR-05 ฿1,900/11,130) | คงไว้ |
| P8 | m | `compare-application-versions` จัดหน้าใหม่ /admin/report เป็น unknown ไม่ใช่ added (ใบ้ "อาจเป็น unknown" ถูก) | คงไว้ |

## ค่าสำหรับ placeholder ใน fast_track/README.md (รอบ 🅰️ นี้ · URL พอร์ต 4000 ตรงแล้ว)

| placeholder | ค่า |
|---|---|
| `<!-- RESULT:FT:time -->` | ~1 ชม. 35 นาที ถึงขั้น 11 (รอบนี้หยุดกลางขั้น 11 เพราะ Docker บนเครื่องถูกล้างจากภายนอก · ขั้น 12 ยังไม่มีผล) |
| `<!-- RESULT:FT:step0-1 -->` | healthy · check-rules 90/90 (21 วิ) · api+chromium "41 passed · 1 failed" = ผ่านจริง 38 · คาดว่าล้ม 3 · ล้ม 1 (TC-SEC-05 ได้ 422 แทน 403/404) · คำอ้าง 16 ข้อ ✅ 9 ❌ 2 ⚠️ 5 · baseline commit |
| `<!-- RESULT:FT:step2-3 -->` | static /api 9 (+ชื่อ route 25) · HAR 7 · scenario 12/12 ฿1,000 · endpoint 25 แถวติดป้าย · 25 route.ts/26 handler · 19 ตาราง CHECK 51 FK 25 EXCLUDE 2 · SPEC-GAPS 14 คำถาม · ตรวจทานแก้เลขบรรทัด 3 จุด |
| `<!-- RESULT:FT:step4 -->` | CLAUDE.md 36 บรรทัด · `claude -p` ถูกปฏิเสธ "File is in a directory that is denied by your permission settings." · e2e-legacy ไม่เปลี่ยน |
| `<!-- RESULT:FT:step5 -->` | golden 63 เคส (ราคา 51) นิ่ง 2/2 · e2e-cr 15 passed (12 + คาดว่าล้ม 3) เท่ากัน 2 รอบ × 3 เบราว์เซอร์ · known issue 3 · X1–X3 ถูก golden+check-rules จับครบ 3/3 · e2e-cr ไม่จับเลย |
| `<!-- RESULT:FT:step6-10 -->` | CR-02 7/14→14/14 · CR-03 6/16→16/16 (+UI) · CR-04 2/13→13/13 (+UI · migration 2 รอบ INSERT 0 3→0 0 นัดไม่หาย) · CR-01 A 1/16→16/16 · B 0/3→3/3 · C UI→เขียว 3 เบราว์เซอร์ · CR-05 0/12→12/12 (+UI · ค่าจาก SQL ก่อนโค้ด) · regression ทุก CR ไม่มีแดงใหม่ · check-rules diff ว่างทุกครั้ง |
| `<!-- RESULT:FT:step11 -->` | (รอบนี้ไม่ครบ) จบ CR-01 รัน test:all ได้ "113 passed · 1 failed" (106 + คาดว่าล้ม 7) 13 นาที = ตอนรับมอบ · cr01–05 + golden + check-rules เขียวบนโค้ดล่าสุด · REA v2 เห็น /account เปลี่ยน + /admin/report ใหม่ (compare = unknown) · CR-02 CR-03 CR-04 static ไม่เห็น (เห็นแค่ chunk ร่วม) · HAR/scenario v2 ไม่ได้ทำ |
| `<!-- RESULT:FT:step12 -->` | (รอบนี้ไม่ได้ทำ) smoke.mjs เขียนแล้ว: เว็บไม่ตอบ → 0/6 exit 1 · ซ้อมถอยกลับ/RELEASE-NOTES/UAT ยังไม่มีผล |
| `<!-- RESULT:FT:A-vs-B -->` | 🅰️ รอบนี้: impact 34 แถว (CR-01 7 · 02 4 · 03 6 · 04 10 · 05 7) · เคสใหม่ API 74 (19+14+16+13+12) + e2e-cr 6 spec UI · 🅱️ ยังไม่ได้รันในงานนี้ (ข้อที่ 🅱️ พลาดยังเทียบไม่ได้) |

⚠️ แนะนำ: placeholder step11/step12/time ควรรอรอบที่รันครบก่อนเติมลง README (ค่าข้างบนเป็นของรอบที่หยุดกลางทาง)
