# PREP-LOG · บท 06 · 12 ต.ค. 2026 09:04–09:30 · agent PREP6 (Claude Code · งาน `C:/t/orch/tasks/P6.md`)

## สรุป: พร้อมให้ RUNNER ✅

P1–P8 ทำครบ · V1–V8 ผ่านทุกข้อตาม "ผลที่ต้องได้" · ตัวเลขทุกตัวด้านล่างมาจากการรันจริงในสำเนา `C:/t/work/b2prep/verify` ที่ `WEB_PORT=4100` `DB_PORT=5533` (D10) · ⚠️ ข้อควรรู้ 2 ข้อ: (1) มี agent อื่นแก้ `EXAM.md` และสร้าง `fast_track/` ระหว่างที่ PREP ทำงาน (ดู "ปัญหาที่เจอ" ข้อ 1) → MANIFEST เป็น snapshot 09:31 · `fast_track/` ยังถูกเขียนอยู่ จึงต้องทำ MANIFEST ใหม่หลัง agent นั้นจบ (2) ตัวอย่าง `doctor` ใน `tools/rea.ps1` เปลี่ยนเป็น `mcp doctor` (ต่างจาก PREP.md P6 · เหตุผลในข้อ 2)

## 0. ก่อนเริ่ม

| ตรวจ | ผลจริง |
|---|---|
| 0.2 agent อื่นจบงานใน `web/ db/ e2e-legacy/ img/` | orchestrator สั่งงานนี้ = ยืนยันโดยปริยาย · ระหว่างทางพบ agent อื่นเขียน `img/` `_solution/_design/README-PART-*.md` `EXAM.md` `fast_track/` (ไม่ใช่ `web/ db/ e2e-legacy/`) |
| 0.6 `docker ps -a --filter name=sabai06` · `docker volume ls --filter name=sabai06` · `docker network ls --filter name=sabai06` | ว่างทั้ง 3 (09:04) → PREP เป็นผู้สร้าง volume `sabai06-pgdata` และ network `sabai06-net` เอง |
| พอร์ตที่ได้รับ | `WEB_PORT=4100` `DB_PORT=5533` (BRIEF D10 · แทนค่าแนะนำ 4140/4141 ในข้อ 0.5) · 4100/5533 ไม่อยู่ใน excludedportrange · ไม่มีโปรเซสฟังอยู่ |
| ของคนอื่นที่ห้ามแตะ | `pawpantry05` (บท 05 · พอร์ต 4000) Up ตลอด · volume `ai-accounts` `sabai-pgdata` อยู่ครบ · network `sabai-net` ไม่แตะ |

## P1–P8

| P | สถานะ | ไฟล์ | ผลตรวจ (คำสั่ง → ผลจริง) |
|---|---|---|---|
| P1 | แก้แล้ว | ใหม่ `web/lib/config.ts` · ลบ `web/lib/flags.ts` · แก้ `lib/rules/slots.ts` `points.ts` `pricing.ts` `lib/clock.ts` `app/layout.tsx` `app/admin/page.tsx` `app/login/page.tsx` `app/api/test/reset/route.ts` `app/api/test/today/route.ts` `scripts/check-rules.mjs` | ข้อความเดิมทั้ง 19 จุดเจอ 1 ครั้งพอดี (สคริปต์ตรวจก่อนเขียน) · `grep -rniE "bug_mode\|bug-mode\|bugmode\|flags" web --exclude-dir=node_modules --exclude-dir=.next` → ไม่มีผล (exit 1) · build ผ่าน (V3) · check-rules 90/90 (V4) |
| P2 | พบว่าทำแล้ว (ตรวจอย่างเดียว) | `web/scripts/check-rules.mjs` | `grep -n "localhost:4000"` → บรรทัด 2, 3, 8 · `grep -c "localhost:3000"` → `0` |
| P3 | แก้แล้ว | `web/compose.yaml` `db/compose.yaml` (เขียนทับทั้งไฟล์ตาม PREP.md) | `grep -rnE "sabai-(web\|db\|net\|pgdata)"` → ไม่มีผล · `grep -c "sabai06-" web/compose.yaml` → `7` · db → `8` · `grep -c BUG_MODE web/compose.yaml` → `0` · `DATABASE_URL` host `sabai06-db` = `container_name` ของ db |
| P4 | แก้แล้ว | `web/SPEC.md` | แทรกบรรทัด "เอกสารส่งมอบ ฉบับ 1.0" · ลบบล็อกโหมดบั๊ก 4 บรรทัด · ลบแถว `BUG_MODE` · แก้ `<html …>` · `grep -niE "bug\|flags" web/SPEC.md` → ไม่มีผล · `grep -c "localhost:3000"` → `3` · `head -3` เห็น "> เอกสารส่งมอบ ฉบับ 1.0 · ก.ย. 2569 · บริษัท โค้ดไว จำกัด" · ส่วนอื่น (พอร์ต 3000, `sabai-net/db/web`, Next.js 15, S2–S9) คงเดิม |
| P5 | พบว่าทำแล้ว (ตรวจอย่างเดียว) | `e2e-legacy/` | `test.fail(true` → `3` (giftcard · security.api · transport) · name `"sabai-legacy-e2e"` · `localhost:4000` ใน config+global-setup → `2` · `bug-mode\|bugmode\|meta\.json\|sabai-net` → ไม่มีผล · `tests/` = 12 spec + `fixtures.ts` · ไม่มี `node_modules/ test-report/ scripts/ triage.json` · `README-LEGACY.md` ไม่ต้องแก้ (ไม่อ้างชื่อ network ตายตัว · ตาราง "ผลรันล่าสุด" คงเป็นคำอ้างผู้รับเหมา) |
| P6 | แก้แล้ว (+ ต่างจาก PREP 1 บรรทัด) | `tools/rea.ps1` `rea-tools.mjs` `record-har.mjs` `scenario-book-quote.json` `package.json` `.gitignore` | `ls -A tools` → 6 รายการ · `127.0.0.1:4000` → `2` · `sabai06-web:3000` → `1` · `host.docker.internal` → `0` · `node --check tools/rea-tools.mjs` exit 0 · `head -c 3 tools/rea.ps1` → `3c 23 0a` (ไม่มี BOM) · บรรทัดตัวอย่างแรกใช้ `mcp doctor` แทน `doctor` (ปัญหาที่เจอ ข้อ 2) |
| P7 | แก้แล้ว | `CHANGE-REQUESTS/` 7 ไฟล์ + `answers/` 5 ไฟล์ | คัดเนื้อในกรอบ `~~~markdown` 12 กรอบตรงตัว (สคริปต์จับคู่หัวข้อ §1 §2 §3.1–3.5 §4.1–4.5 กับชื่อไฟล์) · `find CHANGE-REQUESTS -type f \| wc -l` → `12` · grep คำรั่ว 11 คำ → ไม่มีผล · `sabai06-net` ใน memo → `1` · คุณสมชาย `081-000-0003` (CR-03, seed B03) · คุณนิดา (answers/CR-01 · seed U01, B05 11 ต.ค. 10:00 ฿760) · คุณต้น 17 ต.ค. 19:00 (seed B02) ตรง `db/init/02-seed.sql` · BOM → `0` |
| P8 | แก้แล้ว (ภายหลัง agent อื่นเขียนทับ) | `EXAM.md` | 09:05 คัดภาค 1 ของ `EXAM-DRAFT.md` ตรงตัว (161 บรรทัด) · 09:23 มี agent อื่นเขียน `EXAM.md` ใหม่ (ปัญหาที่เจอ ข้อ 1) · ตรวจ P8 กับไฟล์ปัจจุบัน: `grep -nE "\bM[1-9]\b\|TABLES\|room_id\|EX-B[0-9]\|NOT_STARTED\|therapist_leave"` → ไม่มีผล · `sabai06x-` → `7` · `sabai06-net` → `0` |
| P9 | ข้าม (งานถัดไป) | — | — |
| P10 | ตรวจ | — | `ls -d db/migrations docs tests e2e-cr README.md .gitignore .claude` → ไม่มีสักตัว |
| P11 | ตรวจ | — | ไม่แตะ `web/ASSETS.md` `web/private/` `db/init/*` `web/lib/server/*` `img/` |

## V1–V8

| V | คำสั่ง | ผลจริง | ตรงไหม | เวลา |
|---|---|---|---|---|
| V1 | grep ทุกข้อของ P1–P8 ที่ `$CH` (รันซ้ำหลังแก้ `rea.ps1` ครั้งสุดท้าย 09:28) | ตรงทุกข้อ (ตาราง P) · ทั้งบทนอก `_solution/ img/`: `grep -rniE "bug_mode\|bugmode\|bug-mode\|data-bug-mode\|flags"` → `0` · BOM `0` · CRLF ในไฟล์ที่แก้ `0` | ✅ | — |
| V2 | `robocopy "$CH" C:\t\work\b2prep\verify /E /XD _solution img node_modules .next` | exit `1` · ไฟล์ 176 · `verify/_solution` ไม่มี | ✅ | 09:06 |
| V3 | `docker network create sabai06-net` → db `up -d --wait` → web `up -d --build --wait` (background) → health → `docker ps` | build exit 0 · **41 วิ** (Next.js 15.5.27 · "Compiled successfully" + "checking validity of types" ผ่าน) · health `ok=True db=True` · `sabai06-web 0.0.0.0:4100->3000` · `sabai06-db 0.0.0.0:5533->5432` (healthy) · HTML หน้าแรกไม่มี `data-bug-mode` | ✅ | 09:07–09:09 |
| V4 | ที่ราก `VER`: `$env:BASE_URL="http://localhost:4100"; node web/scripts/check-rules.mjs` | หัว "ตรวจกฎร้าน http://localhost:4100 · 90 เคส" · **ผ่าน 90 / 90 ข้อ** · ไม่มีคำว่า BUG_MODE · exit 0 · **19.7 วิ** | ✅ | 09:09 |
| V5 | `npm ci` · `npx playwright install chromium firefox webkit` · `npx playwright test --reporter=list` | **41 passed · 1 failed (4.0 นาที)** · บรรทัดผล: `ok` 38 · `x` 4 = expected-fail 3 (TC-SEC-04 [api] · TC-GC-04 [chromium] · TC-TRN-03 [chromium]) + failed 1 (TC-SEC-05 [api] ขั้น "U04 จองด้วยคอร์ส C01 ของ U01 → 403/404") · หมายเหตุ: list reporter แสดง `x` ทั้ง expected-fail และ failed ต้องแยกจากชื่อ/บรรทัดสรุป | ✅ | 09:09–09:13 |
| V5b | `npm run test:all -- --reporter=list` (background) | **113 passed · 1 failed (13.1 นาที)** · 114 รายการ: `ok` 106 · expected-fail 7 (TC-SEC-04 api ×1 · TC-GC-04 ×3 · TC-TRN-03 ×3) · failed TC-SEC-05 api ×1 | ✅ | 09:13–09:26 |
| V6 | `$env:ALLOW_TEST_RESET="0"; docker compose -f web/compose.yaml up -d --wait` → `POST /api/test/reset` → `"1"` → up → reset → health | ปิด: reset **404** · `GET /api/test/today` 404 · เปิดกลับ: reset **200** · health `True True` | ✅ | 09:26 |
| V7a | `docker cp sabai06-web:/app/.next/static rea-out\v1\.next\static` → `rea.ps1 -Out rea-out\static-v1.json analyze-javascript-application …` → `rea-tools.mjs endpoints` | exit 0 ทุกคำสั่ง · analyze **55 วิ** · Evidence 34.1 MB · graph: javascript-module 549 · javascript-chunk 26 · javascript-asset 30 · endpoint node 16 · unknown 8 · artifact 1 · edge 1,408 · endpoint `/api/*` จริง **9** (`/api/auth/logout` `/api/price` `/api/auth/login` `/api/bookings` `/api/test/reset` `/api/chat` `/api/courses` `/api/quiz` `/api/giftcards`) + `/_next/image` + ชื่อย่อ minified (`a` `b` `c` `[]` `[...]` `[[...]]`) · route stub **25/25** | ✅ | 09:11 (ขนานกับ V5 · ไม่แตะ DB) |
| V7b | `record-har.mjs http://127.0.0.1:4100 rea-out\journeys.har` → `har-records` → `rea.ps1 -Out rea-out\har-api.json inspect-web-network-capture … har <records> --sensitive-value Nida@2026 --sensitive-value Owner@2026 --json` → `har-api` | HAR **10 วิ** · records `37 39 40 41 69 75 77 126 130 131` · inspect exit 0 **3 วิ** · ตาราง **7 endpoint / 10 ครั้ง** (`GET /api/slots` 1 · `POST /api/price` 2 · `POST /api/bookings` 1 (201) · `POST /api/auth/login` 2 · `POST /api/bookings/{id}/cancel` 1 · `POST /api/auth/logout` 1 · `GET /api/admin/bookings` 2) · `Nida@2026` ไม่อยู่ใน `har-api.json` | ✅ | 09:27 |
| V7c | reset → `rea.ps1 -Network sabai06-net -Out rea-out\scenario.json capture-browser-scenario /work/tools/scenario-book-quote.json --json` → `rea-tools.mjs shot rea-out\scenario.json rea-out\scenario-final.png` | exit 0 · **4 วิ** · 12/12 step `completed` (scenario_start + 11 action) · completeness `complete` · URL `http://sabai06-web:3000` (ผ่าน network · **ไม่ต้องใช้ทางสำรอง host.docker.internal**) · `shot` exit 0 → PNG **107,054 bytes** · เปิดดูแล้ว = หน้า "4. สรุปก่อนจ่าย" นวดไทย 60 นาที · 12 ต.ค. 2026 15:00–16:00 · ยอดสุทธิ **฿1,000** (สำเนาภาพ `C:/t/work/b2prep/scenario-final.png`) · `shot` ไม่ต้องแก้ (Evidence เก็บ PNG เป็น base64) | ✅ | 09:27 |
| V7d | `rea.ps1 doctor` / `rea.ps1 mcp doctor` | `doctor` → exit **1** (`healthy: false` · ขาด Hopper/Ghidra/IDA + skill identity · ไม่เกี่ยวกับงานเว็บ) · `mcp doctor` → exit **0** (ทดสอบซ้ำด้วย `rea.ps1` ฉบับแก้แล้ว) | ⚠️ → แก้ตัวอย่างใน `rea.ps1` | 09:27–09:28 |
| V8 | web `down` · db `down` (ไม่ใส่ `-v`) · `docker volume rm sabai06-pgdata` · `docker network rm sabai06-net` · `docker image rm sabai06-web:latest` · ลบ `VER` | `docker ps -a --filter name=sabai06` ว่าง · volume/network `sabai06*` ว่าง · image ลบแล้ว · `C:/t/work/b2prep/verify` ไม่มีแล้ว · `pawpantry05` ยัง Up · `ai-accounts` `sabai-pgdata` อยู่ครบ | ✅ | 09:28 |

### ตรวจเพิ่ม (งาน P6.md ข้อ 2): บั๊กจริงที่ไม่ผูก flag ยังอยู่หลังถอด BUG_MODE

สคริปต์ `C:/t/work/b2prep/probe-legacy.mjs` (ดัดแปลงจาก `C:/t/work/a6/probe/probe.mjs`) · reset ก่อนแต่ละข้อ · today = 10 ต.ค. 2026 10:00 · ผลดิบ `C:/t/work/b2prep/probe-legacy.out`

| L | ใช้ที่ (CR-DESIGN §2.2) | ผลจริง | ยังอยู่ไหม |
|---|---|---|---|
| **L1** จองเดิมซ้ำได้ | CR-03 | guest ส่ง S01 20 ต.ค. 14:00 เบอร์ 081-000-0003 ซ้ำ 3 ครั้ง → 201 ทั้ง 3 (B14 B15 B16) | ✅ ยังอยู่ |
| **L2** กดเสร็จนัดอนาคต | ข้อสอบชุด B ข้อ 5 | owner complete B02 (17 ต.ค.) วันที่ 10 → 200 `completed` · pointsEarned 25 · U02 แต้ม 0→25 · ยอดสะสม 30,000→32,520 | ✅ ยังอยู่ |
| **L4** ติ๊กรถแต่ไม่ใส่ระยะ/โรงแรม | ข้อสอบชุด A ข้อ 5 | TC-TRN-03 ยังล้มตามคาด (expected-fail) ทั้ง chromium/firefox/webkit (V5, V5b) | ✅ ยังอยู่ |
| **L5** รหัส Gift Card ไม่มีจริงไม่มีข้อความ | LAB 5 known issue | API `/api/price` giftCardCode XXXX → 422 `GC_NOT_FOUND` · หน้าจอ: TC-GC-04 ยังล้มตามคาด 3 เบราว์เซอร์ | ✅ ยังอยู่ |
| L3 cookie หลัง logout | งานเสริม | `/api/me` ด้วย cookie เดิม → 200 "คุณนิดา" · TC-SEC-04 expected-fail | ✅ |
| L6 เบอร์ไม่ตรวจรูปแบบ | CR-03 | `contactPhone:"abc"` → 201 B14 | ✅ |
| L7 owner ยกเลิกนัดลูกค้า | SPEC gap | owner cancel B02 → 200 `cancelled` | ✅ |
| L8 test hooks ไม่ต้องล็อกอิน | release/UAT | `GET /api/test/today` → 200 `{now:"2026-10-10T10:00:00+07:00"}` | ✅ |

### ตรวจเฉลยรั่วในไฟล์ที่ผู้เรียนเห็น

| ไฟล์ | ผล |
|---|---|
| `CHANGE-REQUESTS/` (memo + register + CR + answers) | grep 11 คำของ P7 → 0 |
| `web/SPEC.md` | `bug\|flags` → 0 · ยังมี S2–S9 ตามเจตนา (T4) |
| `e2e-legacy/` | `bug-mode\|bugmode\|meta.json\|sabai-net` → 0 · ข้อความ `test.fail` 3 ข้อ = อาการที่ผู้ใช้เห็น (T5) ไม่บอกไฟล์/ต้นเหตุ |
| `EXAM.md` (ฉบับปัจจุบัน) · `fast_track/README.md` | grep P8 → 0 · `bug_mode\|bugmode\|data-bug-mode\|flags.ts\|self-overlap` → 0 · `\bL[1-8]\b\|S4` ใน fast_track → 0 |
| `tools/` | ไม่มีคำว่า bug/flags · scenario/HAR ใช้ข้อมูล seed เท่านั้น |

## ตัวเลขที่ใช้แทน [คาด] ใน PROMPTS/LESSON-PLAN (รันที่ 4100 → README เขียนเป็น 4000)

| เรื่อง | ค่าจริง |
|---|---|
| build ครั้งแรกของ `sabai06-web` (มี cache ของ base image แล้ว) | 41 วิ (`up -d --build --wait` รวม healthy) |
| check-rules (รันจากราก) | 90 / 90 · 19.7 วิ |
| e2e-legacy default (api + chromium) | "41 passed · 1 failed" · 4.0 นาที · ผ่านจริง 38 · expected-fail 3 · failed TC-SEC-05 |
| e2e-legacy `test:all` | "113 passed · 1 failed" · 13.1 นาที · ผ่านจริง 106 · expected-fail 7 · failed TC-SEC-05 ×1 |
| `npm ci` e2e-legacy / `npm install` tools | 2 วิ / 2 วิ (มี npm cache) |
| REA static | 55 วิ · Evidence 34.1 MB · endpoint `/api/*` 9 · endpoint node 16 · route stub 25/25 · unknown 8 |
| REA HAR | record 10 วิ · inspect 3 วิ · 7 endpoint / 10 ครั้ง |
| REA scenario (network `sabai06-net`) | 4 วิ · 12/12 step · complete · ภาพ 107 KB หน้าสรุป ฿1,000 |
| `rea.ps1 mcp doctor` | exit 0 (`doctor` เฉย ๆ exit 1) |

## MANIFEST

| รายการ | ค่า |
|---|---|
| path | `C:/t/work/b2prep/MANIFEST.sha256` (สร้างด้วยคำสั่ง PREP.md §4 ตรงตัว · ฉบับล่าสุด 09:31:10) |
| จำนวนไฟล์ | 179 (CHANGE-REQUESTS 12 · EXAM.md 1 · db 3 · e2e-legacy 22 · fast_track 3 · tools 6 · web 132) |
| sha256 ของไฟล์ MANIFEST | `5b0c50e648d58ad33332f8e1742d39eb4f5cadd3ab7809f9f6ab842b13c6919d` |
| self-check | `sha256sum -c --quiet` ที่ `$CH` → ไม่มีผล · exit 0 (09:31:10) |
| ⚠️ | ฉบับ 09:29 (177 ไฟล์ · `b023a013…`) ล้าสมัยภายใน 2 นาที เพราะ agent อื่นยังเขียน `fast_track/` อยู่ (`README.md` เปลี่ยน + ไฟล์เพิ่ม 2) · ฉบับ 09:31 รวม `EXAM.md` ฉบับ agent อื่น (09:23) และ `fast_track/` ณ 09:31 · **orchestrator ต้องรันคำสั่ง §4 ใหม่หลัง agent `fast_track/`/EXAM จบ** ก่อนคัดลอกให้ RUNNER · ไฟล์ที่ PREP ทำ (`web/ db/ e2e-legacy/ tools/ CHANGE-REQUESTS/`) ไม่เปลี่ยนแล้ว |

## ปัญหาที่เจอ / สิ่งที่ทำต่างจาก PREP.md

| # | เรื่อง | ทำอย่างไร |
|---|---|---|
| 1 | **มี agent อื่นแก้บทพร้อมกัน**: `EXAM.md` ถูกเขียนใหม่ 09:23 (หัว "(ชุด A · ฝึก)" · เพิ่มตารางเวลา/กติกา · 335 บรรทัด diff กับภาค 1 ของ EXAM-DRAFT) · โฟลเดอร์ใหม่ `fast_track/` (README.md 110 KB + `img/`) 09:24–09:28 · ไฟล์ `_solution/_design/README-PART-*.md` `FT-IMAGES.md` ฯลฯ | ไม่ย้อนกลับ (ถือเป็นงานตั้งใจของ agent อื่น) · ตรวจ P8 กับ `EXAM.md` ปัจจุบันแล้วผ่าน · grep รั่วใน `fast_track/` ผ่าน · ⚠️ orchestrator ควรยืนยันว่า `EXAM.md` ฉบับใหม่คือฉบับจริง และ `fast_track/` ควรอยู่ใน MANIFEST ของ RUNNER หรือไม่ (คำสั่ง §4 รวมไว้เพราะไม่ใช่ `./img/*`) |
| 2 | `tools/rea.ps1 doctor` (ตัวอย่างบรรทัดแรกตาม P6) ตอบ exit 1 `healthy: false` ใน `rea-lab:6.4.0` เพราะไม่มี Hopper/Ghidra/IDA (งานเว็บไม่ใช้) | เปลี่ยนบรรทัดนั้นเป็น `… tools\rea.ps1 mcp doctor      # exit 0 = พร้อม (doctor เฉย ๆ ตอบ exit 1 …)` ให้ตรง LESSON-PLAN T12/m4 และ PROMPTS LAB 0 ที่ใช้ `mcp doctor` · ทดสอบผ่าน `rea.ps1` แล้ว exit 0 · บันทึกใน PREP.md "## PREP notes" |
| 3 | P6.md (คำสั่งงาน) อ้าง `.claude/settings.json` และ `.gitignore` | ไม่สร้าง: PREP.md P10 ห้ามสร้าง root `.gitignore` และ LESSON-PLAN §6/§11 ให้ `.claude/settings.json` เป็นผลงานผู้เรียนใน LAB 4 · `.gitignore` ที่มีอยู่ = `web/.gitignore` `e2e-legacy/.gitignore` + ใหม่ `tools/.gitignore` |
| 4 | P6.md อ้าง "rea/ helpers if specified" | PREP.md ใช้ `tools/` (คัดจาก `rea-probe` ของบท 05/06) ไม่มี `rea/` ในบท 06 → ไม่คัดโฟลเดอร์ `05/rea` |
| 5 | V7 "endpoint static 9" | REA ให้ endpoint node 16 (รวมชื่อย่อ minified + `/_next/image`) · 9 = endpoint `/api/*` จริง (ตรง RF) → README ควรเขียน "9 endpoint จริง" ไม่ใช่จำนวน node |
| 6 | P7 ตรวจ "คุณนิดาใน CR-01/CR-03" | คุณนิดาอยู่ใน `answers/CR-01-ANSWERS.md` (ไม่ใช่ `CR-01.md`) · ข้อมูลตรง seed |
| 7 | list reporter ของ Playwright แสดง `x` ทั้ง expected-fail และ failed | นับแยกจากชื่อ TC + บรรทัดสรุป (`41 passed`/`1 failed`) · README LAB 1 ควรบอกวิธีแยกนี้ |
| 8 | log ของ PowerShell (`*>`) มี BOM | เฉพาะไฟล์ log ใน `C:/t/work/b2prep/` ไม่ใช่ไฟล์บท |

## ทรัพยากร docker ที่ยังเหลือ (ควรว่าง)

| ตรวจ (09:28) | ผล |
|---|---|
| `docker ps -a --filter name=sabai06` | ว่าง |
| `docker volume ls --filter name=sabai06` | ว่าง |
| `docker network ls --filter name=sabai06` | ว่าง |
| image `sabai06-web:latest` | ลบแล้ว (build cache ของ Docker ยังอยู่) |
| `C:/t/work/b2prep/` ที่เหลือ | `MANIFEST.sha256` · log `v3-build.log` `v4-check-rules.log` `v5-e2e.log` `v5b-e2e-all.log` `v7-endpoints.txt` `v7-doctor.txt` · `probe-legacy.mjs/.out` · `scenario-final.png` · `exam-draft-part1.md` (ไม่มี node_modules) |
