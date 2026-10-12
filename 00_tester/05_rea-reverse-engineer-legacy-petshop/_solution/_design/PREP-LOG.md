# PREP-LOG · เตรียมโฟลเดอร์ตั้งต้นบท 05 ตาม LESSON-PLAN §7 (งาน PREP5 · 12 ต.ค. 2026)

> ทำตาม `C:/t/orch/tasks/P5.md` · พอร์ตที่ได้รับ = **4000** · งานชั่วคราวอยู่ `C:/t/work/prep5/` (`$T`) · ข้อมูลอ้างอิง A1 = `C:/t/work/a1/out` (`$A`)
> ทุกผลในไฟล์นี้มาจากการรันจริงบนเครื่องนี้ (Windows 11 · Docker Desktop · Node 26.7.0 · Playwright 1.63.0 · image `rea-lab:6.4.0`)
> ไม่ได้ทำ: §7 #15 (README.md ราก · ผู้เขียน README ทำ) · §7 #17 (diagram/img · agent อื่นทำ) · ไม่แตะ `img/` · ไม่ใช้ git ที่เปลี่ยนสถานะ repo

## 1. รายการงาน §7 (#1–#16)

| # | ทำอะไร | คำสั่งตรวจรับ | ผล |
|---|---|---|---|
| 1 | เอา BUG_MODE ออก 12 ไฟล์ตามตาราง 7.2 ด้วยสคริปต์ `$T/apply-7.2.mjs` (แทนที่แบบ exact-match ต้องเจอครบตามจำนวน ไม่งั้นหยุด · คง CRLF เดิม) · ลบ `lib/bugmode.ts` · ลองบนสำเนาก่อน (`$T/dryrun`) แล้ว diff ตรงกัน 100% ค่อยใช้กับบท · **เพิ่ม (D4):** ลบ `<p className="made-for">สร้างไว้สำหรับฝึก Playwright</p>` ใน `components/Footer.tsx` และตัด " · ร้านจำลองเพื่อการเรียนรู้" ออกจาก `© 2026 PawPantry` (ดูข้อ 3.6) | `grep -rniE "bug_?mode" petshop … \| wc -l` · `npm ci && npm run typecheck` (รันบนสำเนา `$T/tc` เพื่อไม่ทิ้ง node_modules ในบท) · `grep -c "ฝึกเขียนเทสต์" petshop/app/layout.tsx` | `0` · typecheck exit 0 (+ `npm run lint` ไม่มี error) · `0` ✅ · แก้ 40 จุด |
| 2 | อบ BUG-01 ตาม diff 7.3 (= CR-DESIGN §2.2 หลังเอา `bugMode` ออก) ในสคริปต์เดียวกัน · คอมเมนต์ `// PP-231 …` คงไว้ตามแบบ (เป็นคอมเมนต์ที่ "เชื่อไม่ได้" ซึ่งเป็นจุดสอน ไม่ใช่คำใบ้) | `grep -c "PP-231" petshop/lib/orders.ts` · `node $T/verify-bug01.mjs` (7.4 ตามตัว · หลัง reset) | `1` · `999-standard total=1049 shipping=50` · `999-PAW10 total=950` · `999-FREESHIP total=999` · `999-express total=1119` → **ALL OK** ✅ |
| 3 | เขียนทับ `petshop/docker-compose.yml` ด้วย 7.5-A | `docker compose -f petshop/docker-compose.yml config \| head -1` · `docker compose -f petshop/docker-compose.yml up -d --build` · `docker ps --filter name=pawpantry05` · network · probe ใน network · `curl -s localhost:4000/api/health` | `name: pawpantry05` · up exit 0 (14 วินาที เพราะ layer `npm ci` cache อยู่ · `next build` 7.3 s) · `Up 25 seconds (healthy)` · `pawpantry05_default` = 1 · probe `{"ok":true}` · curl `{"ok":true}` · HTML ไม่มี `data-bug-mode` ✅ |
| 4 | เขียนทับ `petshop/README.md` ด้วย 7.5-B | `grep -ciE "bug_?mode\|ฝึก" petshop/README.md` · `test -f TEST-DATA.md` | `0` · มี ✅ |
| 5 | สร้าง `petshop/HANDOVER-NOTES.md` ตาม 7.5-C ตามตัว | `wc -l` · `grep -ciE "ค่าส่ง\|ส่งฟรี\|shipping\|999\|PP-231\|orders.ts"` | `9` บรรทัด · `0` ✅ |
| 6 | `cp ../03_petshop-testplan-from-exploration/TEST-DATA.md TEST-DATA.md` | `cmp` | exit 0 ✅ |
| 7 | `mkdir e2e-legacy/tests/new` + `.gitkeep` · รัน suite บน build #1–#3 | `ls e2e-legacy/tests/*.spec.ts \| wc -l` · `npm ci && npx playwright test` · `npm run test:all` | `10` · **chromium 40 passed (12.9 s)** · รอบ 2 = 40 passed (13.6 s) · **3 เบราว์เซอร์ 120 passed (58.2 s)** ✅ · ตาราง "ผลรันล่าสุด" ใน `README-LEGACY.md` เขียนไว้ "40 passed ~13 วินาที / 120 passed ~1 นาที" = ตรงผลจริงแล้ว **จึงไม่แก้ไฟล์** |
| 8 | `rea/rea.ps1` = สำเนา `rea-probe/rea.ps1` แทนบรรทัด 6–11 ด้วย 7.5-D (ส่วน `param(...)` ลงไปไม่แก้) · บันทึกเป็น **UTF-8 มี BOM** (ดู 3.7) | `PS> powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 doctor` · `… -Out out\doctor.json doctor --json; Format-Hex out\doctor.json \| Select -First 1` | doctor แสดงผล 2,829 บรรทัด `healthy: false` exit 1 (ปกติ) · ไบต์แรก `7B` (`{"healthy":false…`) · 61,460 bytes ✅ |
| 9 | เขียน `rea/rea-summarize.mjs` ใหม่ตามสัญญา 7.6 ทุกโหมด (A B C D D′ E F G + อื่น ๆ) | ทุกแถวคอลัมน์ "ตรวจรับกับข้อมูล A1" | ผ่านทุกแถว ยกเว้น B ที่สเปกเป็นไปไม่ได้ (ดู 3.1) · รายละเอียดตาราง 2 ✅ |
| 10 | เขียน `rea/rea-input.mjs` ตามสัญญา 7.7 | 5 คำสั่ง `jsoneq` ใน 7.7 + `head -c3 \| od` | `true` ×5 (trace · s2b v1 · s2b v1src-v2server · compare · view) · ไบต์แรก `7b` ทุกไฟล์ · usage ผิด/seedKind ผิด/reference ไม่ใช่ HistoricalSourceGraph → exit 2 ✅ |
| 11 | `rea/record-har.mjs` คัดจาก probe + `--base` `--out` · `OUT` เริ่มต้น `<รากบท>/out` · ล้มแล้ว `✗ <step>: <msg>` exit 1 · หัวไฟล์ตาม 7.8 · **ค่าเริ่มต้น base = `http://127.0.0.1:4000` + แปลง `localhost`→`127.0.0.1` อัตโนมัติ** (ดู 3.2) | `PS> node rea\record-har.mjs` · `--out out\after` · จาก `petshop\`: `node ..\rea\record-har.mjs` · `--base http://localhost:4199` (ไม่มีเว็บ) · `--out` ไม่มีค่า | 8 step · `out\pawpantry-main.har` 1.60 MB + `har-steps.json` (total 2,420 ms) · `out\after\` ได้ · จาก `petshop\` เขียนลง `<รากบท>\out\` และไม่มี `petshop\out` · `✗ 01 home: page.goto: net::ERR_CONNECTION_REFUSED` exit 1 · exit 2 ✅ |
| 12 | `rea/package.json` = 7.5-E ตามตัว · `rea/scenario-coupon.json` = probe แก้ `start_url` → `http://petshop:3000/` | `cd rea && npm install` · `node -e "import('playwright')…"` · `rea/scratch/t.mjs` · `PS> … rea.ps1 -Network pawpantry05_default -Out out\scenario.json capture-browser-scenario /work/rea/scenario-coupon.json --json` · `node rea\rea-summarize.mjs out\scenario.json` | `ok` · `ok` (ลบ t.mjs แล้ว) · exit 0 (4 วินาที · 4.5 MB) · `steps_completed` = **`"11/11"`** ✅ · `npm install` สร้าง `rea/package-lock.json` (เก็บไว้ ดู 3.8) |
| 13 | `rea/README.md` = 7.5-F ตามตัว | `wc -l < rea/README.md` | `15` ✅ |
| 14 | `.gitignore` ราก = 7.5-G ตามตัว | คำสั่งในสเปก `git check-ignore -q out/x.json rea/scratch/a.mjs x.har` **ใช้ไม่ได้** (`fatal: --quiet is only valid with a single pathname`, exit 128) → ตรวจทีละ path `git check-ignore -q <p>` + `-v` | ทั้ง 3 path exit 0 (ignored โดย `.gitignore` บรรทัด 1 7 2) · `e2e-legacy/node_modules` `rea/node_modules` ก็ ignored ✅ (ดู 3.4) |
| 15 | — ไม่ทำ (README.md ราก ยังไม่มี · คำสั่งงานห้ามแก้) | — | — |
| 16 | สร้าง `_solution/QUIZ.md` (ตาราง §3.1 ทั้ง 2 คอลัมน์ คัดตามตัว) · `_solution/GRADING.md` (รูบริก §4 + ตาราง §4.1 คัดตามตัว) | `grep -c "^\| [0-9]" _solution/QUIZ.md` · `grep -c "1,049" _solution/GRADING.md` | `10` · `1` ✅ |
| 17 | — ไม่ทำ (agent อื่น) | — | — |

## 2. ตรวจจริงบนพอร์ต 4000 + ตัวช่วย rea/ ทุกโหมด (รันแบบเดียวกับ PROMPTS.md · PowerShell 5.1 จากรากบท)

### 2.1 BUG-01 (API + หน้าเว็บ)

| จุด | ผล (ตะกร้า ไม้ตกแมว ×1 + ชามกินช้า ×3 = ฿999 · ส่งธรรมดา · COD · login demo) |
|---|---|
| `/cart` | ยอดสินค้า ฿999 · ค่าส่ง **ฟรี** · ยอดชำระ ฿999 · แถบ "ได้ส่งฟรีแล้ว!" |
| `/checkout` | ปุ่ม **"ยืนยันสั่งซื้อ ฿999"** |
| `POST /api/orders` | `subtotal 999 · shipping 50 · total 1049` |
| `/orders/PP-100001` | ค่าส่ง ฿50 · ยอดชำระ **฿1,049** |
| `/account` | `PP-100001 4 ชิ้น รับคำสั่งซื้อ ฿1,049` |
| `verify-bug01.mjs` (7.4) | ALL OK (4 กรณี) |

→ **ทำซ้ำได้ครบ** (สคริปต์ Playwright ชั่วคราวรันจาก `rea/scratch/` แล้วลบทิ้ง)

### 2.2 grep กันเฉลยรั่ว (หลังเก็บกวาด · ทั้งบท ยกเว้น `_solution/`)

| คำสั่ง | ผล |
|---|---|
| `grep -rniE "bug_?mode\|data-bug-mode\|training bug" . --exclude-dir=_solution \| wc -l` | **0** |
| `grep -rnE "1,049\|1049\|lib/orders\.ts\|orders\.ts\|PP-231" petshop/HANDOVER-NOTES.md petshop/README.md TEST-DATA.md e2e-legacy rea` (ไม่รวม node_modules) | **0** |

### 2.3 rea-summarize.mjs เทียบข้อมูล A1 (`$A`)

| โหมด | ไฟล์ A1 | ผลเรา | ตรงสเปก |
|---|---|---|---|
| A static | `v1-static.json` | `ev_ca3bd308` · digest `7ab17795d9f1` · files 21 · edges 68 · endpoint 9 / javascript-asset 21 / javascript-module 19 / unknown 10 / storage 3 / artifact 1 · endpoints 9 (มี `a` `b` `c`) · storage 3 แถว `name: null` | ✅ |
| A server | `v1-server.json` | files 449 · `recovered_source_files` 53 = รายชื่อใน `rea-probe/evidence/02` ตรงทุกตัว (diff ว่าง) | ✅ |
| B | `har-inspect-redacted.json --md` | 4 แถว · แถว login = `(redacted) \| (redacted)` (สเปกคาด `email, password \| user`) · ไฟล์ไม่ปิดค่าลับ `har-inspect.json --md` = ตรง `04-har-api-table.md` ทุกไบต์ | ⚠️ ดู 3.1 |
| C | `trace-s1.json` | matched_seeds 13 · traced_nodes 16 · nodes 16 · `source_files ["app/api/coupons/validate/route.ts"]` · มี `chunks/ssr/components_CartView_tsx_12yx7o-868btn._.js` | ✅ |
| D | `s2b-server.json` | summary `{"unchanged":44,"modified":0,"removed":0,"split":0,"merged":0,"duplicated":9,"unknown":3}` · items 12 แถว = รายการ `s2b-server` ใน `07-source-to-bundle.summary.json` | ✅ |
| D′ | `--s2b-table` 4 ไฟล์ | 2 แถว `app/api/coupons/active/route.ts` `lib/pricing.ts` + 4 บรรทัดตัวนับ = `07-s2b-diff-table.md` (หัวคอลัมน์ = ชื่อไฟล์ตามสเปก) | ✅ |
| E | `scenario-capture.json --png` | `11/11` · completeness `incomplete` (missing `events`) · keys `pp-recent pp-cart pp-coupon` · a11y มี `ใช้คูปอง PAW10 แล้ว` `-฿6` `฿113` · api_calls POST `/api/coupons/validate` 200 (body ถอดได้) · `cmp` PNG = เท่ากัน 182,349 bytes | ✅ |
| F | `cmp-server.json` | summary `{"unchanged":0,"added":0,"removed":0,"changed":273,"unknown":1479}` · items_total 1752 · sample 20 | ✅ |
| G | `v1-source-graph.json` | `HistoricalSourceGraph` · `038405ccb558` · entries 154 · `partial` | ✅ |
| BOM / error | ไฟล์มี BOM · ไฟล์ไม่ใช่ JSON · usage ผิด | อ่านได้ · exit 1 พร้อมข้อความ · exit 2 | ✅ |

### 2.4 รันทุกโหมดแบบที่ PROMPTS เรียก (บนเว็บ/บิลด์จริงของบทนี้ · ไฟล์ผลใน `out\` ลบแล้วตอนจบ)

| LAB | คำสั่ง (ย่อ `REA` = `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1`) | exit · เวลา | ขนาด / ผลย่อ |
|---|---|---|---|
| 0 | `REA doctor` · `REA -Out out\doctor.json doctor --json` | 1 · 1 (ปกติ) | 2,829 บรรทัด · 61,460 B |
| 2 | `robocopy petshop out\v1 …` + `docker run … node:24-alpine "npm ci && npm run build"` | robocopy 1 (สำเร็จ) · build 0 · **160 s** | — |
| 2 | `REA -Out out\v1-static.json analyze-javascript-application /work/out/v1/.next/static --json` | 0 · 39 s | 54.4 MB · `ev_209e3dcd` · digest `4b9555209cfa` · files 21 · edges 61 · node: javascript-asset 21 · javascript-module 18 · unknown 11 · **endpoint 7 · ไม่มี node storage** · สรุปรวม fact จาก file node แล้ว = endpoints 9 (`/api/auth/login|logout|register` `/api/coupons/validate` `/api/orders` `/api/products` `a` `b` `c`) · storage 3 (ดู 3.3) |
| 2 | `REA -Out out\v1-server.json … /work/out/v1/.next/server --json` | 0 · 24 s | 54.0 MB · `ev_f1e43793` · files 445 · edges 1,859 · endpoints 37 · storage 3 · **recovered_source_files 52** (= 53 ของ A1 ลบ `lib/bugmode.ts`) · มี `electron-renderer` 2 |
| 2 | `node rea\rea-input.mjs trace out\v1-server.json string coupons/validate incoming out\trace-coupon.in.json` → `REA -Out out\trace-coupon.json trace-application-feature …` | 0 · 10 s | in 54.0 MB · out 265 KB · `ev_662c485e` · matched 13 · nodes 16 · `source_files = app/api/coupons/validate/route.ts` |
| 3 | `node rea\record-har.mjs` | 0 · 2.4 s | HAR 1.60 MB · 8 step |
| 3 | `REA -Out out\har.json inspect-web-network-capture /work/out/pawpantry-main.har har --sensitive-value Paw12345 --sensitive-value demo@pawpantry.test --json` | 0 · 2 s | 1.76 MB · `ev_d21c167e` · records 97 · API 4 แถว · `Select-String Paw12345`: har.json = False · .har = True ✅ · (**ก่อนแก้ข้อ 3.2 = exit 1** HAR schema error) |
| 3 | `REA -Network pawpantry05_default -Out out\scenario.json capture-browser-scenario /work/rea/scenario-coupon.json --json` + `rea-summarize --png out\scenario-final.png` | 0 · 4 s | 4.5 MB · `ev_c8f246ce` · 11/11 · 1,836 ms · keys `pp-recent pp-cart pp-coupon` · a11y 14 บรรทัด · PNG 182,349 B |
| 9 | robocopy → `out\v2` + แก้ BUG-01 แบบต้นเหตุ **ในสำเนา v2 เท่านั้น** (CR-DESIGN §2.6) + build | build 0 · **165 s** | `git diff --no-index --stat`: `lib/orders.ts` +1 −13 |
| 9 | `REA -Out out\v2-server.json analyze-javascript-application /work/out/v2/.next/server --json` | 0 · 23 s | 54.1 MB · `ev_fb2d55a7` · files 445 · recovered 52 |
| 9 | `REA -Out out\v1-src.json import-reference-source /work/out/v1 --json` (และ v2) | 0 · 3 s ×2 | 58 KB · entries 154 · `partial` · root `ae1f32c6afb8` / `2a732efc90e0` |
| 9 | `node rea\rea-input.mjs s2b …` ×4 → `REA -Out out\s2b-<คู่>.json compare-source-to-bundle /work/out/s2b.in.json --json` | 0 · 10 s ต่อคู่ | in 54.1 MB · out 266–269 KB · v1src-v1build `44/0/0/0/0/8/3` · v1src-v2build `44/0/0/0/0/7/4` · v2src-v1build `44/0/0/0/0/7/4` · v2src-v2build `44/0/0/0/0/8/3` |
| 9 | `node rea\rea-summarize.mjs --s2b-table …4 ไฟล์` | 0 | **1 แถว: `lib/orders.ts` duplicated · unknown · unknown · duplicated** = ไฟล์ที่แก้จริงไฟล์เดียว ✅ |
| 9-2 | `node rea\rea-input.mjs compare out\v1-server.json out\v2-server.json out\cmp.in.json` → `REA -Out out\cmp.json compare-application-versions …` | 0 · 19 s | in 108 MB · out 9.1 MB · `ev_10b3dac6` · changed 222 · unknown 1,447 · items_total 1,669 |
| 9-2 | `node rea\record-har.mjs --out out\after` → `REA -Out out\after\har.json inspect-web-network-capture /work/out/after/pawpantry-main.har har --sensitive-value … --json` | 0 · 0 | HAR 1.61 MB · har.json 1.78 MB · API 4 แถวเหมือนเดิม (ทดสอบพร้อม `$env:BASE_URL="http://localhost:4000"` → แปลงเป็น 127.0.0.1 อัตโนมัติ) |
| (ไม่อยู่ใน PROMPTS) | `node rea\rea-input.mjs view out\v1-static.json out\view.in.json` → `REA -Out out\view.json inspect-analysis-view …` | 0 · 10 s | 18 KB · `operation inspect_analysis_view` (โหมด "อื่น ๆ" แสดง keys) |

## 3. สิ่งที่ §7 ผิด/กำกวม และวิธีที่ตัดสิน

| # | เรื่อง | พบอะไร (รันจริง) | ตัดสิน / ให้แก้ที่ไหน |
|---|---|---|---|
| 3.1 | §7.6-B ตรวจรับ `har-inspect-redacted.json --md` = ตาราง `04-har-api-table.md` | **เป็นไปไม่ได้**: `--sensitive-value` ทำให้ REA ตั้ง `request.postData.text` และ `response.content.text` ของ login เป็น `null` ทั้งก้อน (`redactions: explicit-sensitive-value`) → ไม่มี key ให้แสดง · ตาราง 04 ทำจาก `har-inspect.json` (ไม่ปิดค่าลับ) | `rea-summarize` แสดง `(redacted)` เมื่อ REA ปิด body (แทน `-` ที่ชวนเข้าใจผิดว่า "ไม่มี body") · ไฟล์ไม่ปิดค่าลับยังตรง 04 ทุกไบต์ · **PROMPTS LAB 3 🎯**: แถว `POST /api/auth/login` = `(redacted)` ทั้ง 2 คอลัมน์ |
| 3.2 | §7.8 base เริ่มต้น `http://localhost:4000` (และ PROMPTS ข้อแก้ปัญหา `--base http://localhost:4100`) | บนเครื่องนี้ Playwright ต่อ `localhost` ทาง IPv6 → HAR มี `serverIPAddress: "[::1]"` 51 รายการ → `inspect-web-network-capture` **exit 1** `HAR schema validation failed: format` ที่ `/log/entries/0/serverIPAddress` · ใช้ `127.0.0.1` → exit 0 (ตรง BRIEF D7 "HAR ใช้ `127.0.0.1:4000`") | ค่าเริ่มต้น = `http://127.0.0.1:4000` และถ้า `--base`/`BASE_URL` เป็น `localhost` สคริปต์แปลงเป็น `127.0.0.1` เอง (พิมพ์บอก 1 บรรทัด) → คำสั่งใน PROMPTS ใช้ได้ตามเดิมทุกตัว · **ควรแก้ LESSON-PLAN §7.8 แถว base URL** ให้ตรง |
| 3.3 | PROMPTS LAB 2 🎯 "static: endpoint ~9 · storage 3 แบบ `local-storage` `name: null`" | build ใหม่ (ไม่มี BUG_MODE) แบ่ง chunk ต่างจาก A1 · REA ชนเพดานผลลัพธ์ที่ `chunks/34-265z4ykszx.js` (มี `/api/products` `/api/auth/logout` และ localStorage ทั้งหมด) → **ไม่แตกเป็น node** (graph มี endpoint 7 · ไม่มี node storage) แต่เก็บ fact ไว้ที่ `javascript-asset` node (`static_analysis.endpoints/storage` + `application_projection_failure`) | `rea-summarize` โหมด A รวม fact จาก file node เข้ามา โดยติด `file_node: <ไฟล์>` (คอลัมน์ "ที่มา" ใน `--md`) + ตัวนับ `retained_on_file_nodes` · ผลรวม = endpoints 9 · storage 3 ตามที่ 🎯 คาด · A1 ไม่มีไฟล์ชนเพดาน → ผลกับ A1 เท่าเดิม · **PROMPTS LAB 2 🎯 ควรเพิ่ม**: "node_kinds อาจมี endpoint 7 ไม่มี storage · ที่เหลืออยู่ในแถว file node = REA ชนเพดาน ≠ ไม่มี" (ตัวอย่างดีของ "หาไม่เจอ ≠ ไม่มี") · server: files 445 (A1 449) · recovered 52 (A1 53 รวม `lib/bugmode.ts`) |
| 3.4 | §7 #14 คำสั่งตรวจรับ | `git check-ignore -q` รับ path เดียว → exit 128 | ตรวจทีละ path (ผ่านทั้ง 3) · **แก้ §7 #14** เป็น `for p in out/x.json rea/scratch/a.mjs x.har; do git check-ignore -q $p \|\| echo FAIL $p; done` |
| 3.5 | คำสั่งงาน P5 บอกให้ทำ ".claude/settings.json deny rules" แต่ §7 แถว ✖ บอก **ไม่ให้** `.claude/settings.json` (ผู้เรียนให้ agent เขียนใน LAB 1 ข้อ 6 · rubric ข้อ 3) | ถ้าใส่ไว้ก่อน LAB 1 จะเฉลยงานของ LAB 1 | **ไม่สร้าง** ตาม LESSON-PLAN/PROMPTS · ความเสี่ยง glob `tests/*.ts` vs `tests/new/` ยังอยู่ใน §9 ให้ RUNNER ทดสอบ LAB 1 |
| 3.6 | ร่องรอย "ของฝึก" ที่ §7.2 ไม่ได้ระบุ | `components/Footer.tsx:14` "สร้างไว้สำหรับฝึก Playwright" และ `:68` "ร้านจำลองเพื่อการเรียนรู้" (เห็นใน a11y ของ REA scenario ด้วย) | ลบตามเหตุผลเดียวกับ §7.2 แถว `layout.tsx:27` (D4: ระบบจริงไม่บอกว่าเป็นของฝึก) · CSS `.made-for` ทิ้งไว้ (ไม่มีผล) · suite 40/40 · 120/120 หลังแก้ |
| 3.7 | §7 #8 "คัดจาก probe" | probe `rea.ps1` เป็น UTF-8 ไม่มี BOM · PowerShell 5.1 อ่านไฟล์ไม่มี BOM เป็น ANSI → คอมเมนต์ไทยเพี้ยน (ในบล็อกคอมเมนต์จึงยังรันได้) | บันทึกเป็น UTF-8 **มี BOM** กันพลาดถ้าวันหน้ามีข้อความไทยในโค้ด · รันจริงผ่านทั้ง doctor และ `-Out` |
| 3.8 | §6 ผังไฟล์ไม่มี `rea/package-lock.json` | `npm install` สร้างให้ | เก็บไว้ (ล็อกเวอร์ชันเหมือน `e2e-legacy/package-lock.json`) |
| 3.9 | §7 #1 ให้ `cd petshop && npm ci` | จะทิ้ง `petshop/node_modules` ไว้ในบท | รัน typecheck/lint บนสำเนา `$T/tc` (โค้ดเดียวกัน) |
| 3.10 | §7 #7 "แก้ตัวเลขใน README-LEGACY" | ตัวเลขเดิมตรงผลจริงอยู่แล้ว | ไม่แก้ |
| 3.11 | §7 #12 scenario "ที่เหลือตามตัว" | ไฟล์ probe เป็น CRLF · ไฟล์ใหม่เป็น LF (เนื้อหาเหมือนกันทุกตัวอักษรยกเว้น `start_url`) | ไม่มีผล (JSON) |

## 4. เก็บกวาด (ข้อ 4 ของคำสั่งงาน)

| รายการ | ผล |
|---|---|
| `docker compose -f petshop/docker-compose.yml down` | container `pawpantry05` + network `pawpantry05_default` ถูกลบ · เว็บ **ปิดแล้ว** · `docker ps -a --filter name=pawpantry05` ว่าง |
| image | เก็บ `pawpantry05:latest` (215 MB) ไว้ใช้ต่อ · dangling image ทั้งหมดบนเครื่องเก่ากว่างานนี้ (≥ 2 ชม.) → **ไม่ได้ลบอะไร** (ไม่ใช่ของงานนี้) · `node:24-alpine` มีอยู่ก่อนแล้ว |
| ไฟล์ในบท | ลบ `out/` (v1 v2 json har png) · `e2e-legacy/node_modules` `test-results` `playwright-report` · `rea/node_modules` · `rea/scratch/` → ผู้เรียนเริ่มจาก `npm install` ใน LAB 0 ตาม PROMPTS |
| สิ่งที่เพิ่มในบท | `.gitignore` `TEST-DATA.md` `petshop/HANDOVER-NOTES.md` `e2e-legacy/tests/new/.gitkeep` `rea/{rea.ps1,rea-input.mjs,rea-summarize.mjs,record-har.mjs,scenario-coupon.json,package.json,package-lock.json,README.md}` `_solution/QUIZ.md` `_solution/GRADING.md` · ลบ `petshop/lib/bugmode.ts` · แก้ 14 ไฟล์ใน `petshop/` (11 ตาม 7.2 + `components/Footer.tsx` + `docker-compose.yml` และ `README.md` เขียนทับ) |
| งานชั่วคราว | อยู่ `C:/t/work/prep5/` (สคริปต์ `apply-7.2.mjs` `verify-bug01.mjs` `jsoneq.mjs` · log build/e2e · สำเนา petshop ก่อนแก้ `petshop-orig-backup/`) |
