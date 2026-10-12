# PROMPTS · บท 06 สบายใจ สปา: รับงานแก้ระบบเดิมด้วย Change Request

ทุก LAB วางใน Claude Code ที่**โฟลเดอร์บท** (แนะนำเปิดเซสชันใหม่ทุก LAB) · ฉบับ v3 (PF6 · 12 ต.ค. 2026) = v2 + แก้ตามผลรอบ RUNNER LAB 0–9 (รายการใน `PROMPT-FIX-LOG.md`) · LAB 10–12 = v3 ตามผลรอบ RUNNER LAB 10–12 (PF6b)
พรอมต์ในบล็อก `text` = ข้อความที่ผู้เรียนคัดลอกตรงตัว · ใต้แต่ละ LAB มี **ผลที่คาด** (ใช้ตรวจรอบ RUNNER · ป้ายแหล่งตาม LESSON-PLAN · **[รันจริง:PREP]** = ผลที่ PREP ต้องยืนยันใน `PREP-LOG.md`) และ **ไปต่อได้เมื่อ** · ทุก LAB (0–12) มีบรรทัดคั่น `<!-- ✂ … -->` ระหว่างกล่องพรอมต์กับผลที่คาด (runner อ่านเฉพาะกล่อง `text` ก่อน · อ่านผลที่คาดหลังรันเสร็จ)
โฟลเดอร์ตั้งต้นเตรียมตาม `PREP.md` (ไม่ใช่งานของ runner)

กติการ่วมของทุกพรอมต์
- **ทุกพรอมต์บอกว่า "รันคำสั่งด้วย PowerShell"** (D9) · เว็บ `http://localhost:4000` · ฐานข้อมูล container `sabai06-db` (host 5433) · เว็บ container `sabai06-web` · network `sabai06-net` (D7–D8)
- **path ตั้งจากโฟลเดอร์บทเสมอ** (m2): `node web/scripts/check-rules.mjs` (สคริปต์ import `../lib/rules` แบบ relative กับไฟล์ จึงรันจากรากได้ · PREP V4 ยืนยัน) · ชุด Playwright ใช้ `Push-Location <ชุด>; …; Pop-Location` ไม่ใช้ `cd` ต่อกัน
- สคริปต์ `.ps1` เรียกด้วย `powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 …` เสมอ (M8 · ไม่แก้ execution policy ของเครื่อง)
- build/ชุดทดสอบที่นานเกิน 2 นาที (build ครั้งแรก · e2e-legacy 3 เบราว์เซอร์ ~13 นาที) → บอก Agent ให้รันแบบ background หรือ timeout ยาว (D9) · กติกานี้อยู่ใน CLAUDE.md ตั้งแต่ LAB 4
- **ขอบเขตเบราว์เซอร์ (M6 · v3):** CR LAB 6, 7, 8 รัน e2e-legacy ค่าเริ่ม (`api + chromium`) และ e2e-cr ทั้งชุด **รวม spec ใหม่ของ CR** ด้วย `--project=chromium` เท่านั้น · **3 เบราว์เซอร์เฉพาะ LAB 5 ส่วนที่ 2 (ตาข่ายตั้งต้น) · LAB 9 ส่วนที่ 3 · LAB 11** · LAB 10 รัน cr05.spec ไฟล์เดียว 3 เบราว์เซอร์ (การดาวน์โหลด CSV ต่างตามเบราว์เซอร์ · รอบ RUNNER 15 วิ) ส่วน e2e-cr ทั้งชุดยัง chromium
- **แยก expected-fail (v3):** บรรทัดสรุปของ Playwright นับ `test.fail()` ที่ล้มตามคาดรวมใน passed และผลรายข้อแสดง ✘ เหมือนข้อที่ล้มจริง · LAB 1 ใช้รายชื่อ failed ท้ายผล + `Select-String … test.fail(` (ไม่ใส่ `--reporter` เพื่อให้ config เขียนรายงาน html ของ `npm run report` ตามเดิม · `--reporter=html` จาก CLI ใช้ค่าเริ่ม `open: on-failure` ซึ่งเปิดเซิร์ฟเวอร์ค้าง) · รอบ 3 เบราว์เซอร์ใช้ `$env:PLAYWRIGHT_JSON_OUTPUT_NAME` + `npx playwright test --project=… --reporter=list,json` (ไม่ผ่าน `npm run … --` เพราะ npm.ps1 ใน PowerShell อาจกิน `--`)
- **กันเฉลยรั่ว (D15/D15a):** ทุกพรอมต์ที่ห้าม `_solution/` ห้าม `README.md` ของบทและ `fast_track/` ด้วย · LAB 4 สร้าง deny `Read(/README.md)` `Read(./fast_track/**)` `Read(./_solution/**)` คู่กับ `Edit(e2e-legacy/**)` และเขียนห้ามใน CLAUDE.md
- **ป้ายแหล่งของค่าคาดหวัง (M3):** `[E ev_xxxxxxxx]` = หลักฐานจากระบบ (REA Evidence 8 ตัวแรก หรือชื่อไฟล์ HAR/golden + SHA-256 ย่อ) ใช้ได้เฉพาะ characterization/regression · `[D:CR-0N]` = ค่าที่ร้านยืนยันในคำตอบ CR · กฎธุรกิจต้องมี [D] · **[E] ขัด [D] = ผู้ต้องสงสัยบั๊ก ไม่ใช่ค่าคาดหวัง** (RT §4.2)
- พรอมต์ไม่อ้าง "LAB x" (เซสชันใหม่ไม่รู้จัก) อ้างชื่อไฟล์แทน · ข้อห้ามซ้ำในทุกพรอมต์ที่เกี่ยว
- LAB 6–10 มี 💬 2–3 กล่อง: **ส่วนที่ 1 วางใน Plan mode** (กด `Shift+Tab` จนขึ้น plan mode ก่อนวาง) · อ่านแผนแล้วสลับกลับโหมดปกติก่อนวางส่วนที่ 2 (เซสชันเดียวกัน)
- **Plan mode เขียนไฟล์ไม่ได้ (v3 · LAB 6–10):** ส่วนที่ 1 ให้แสดงคำถามในแชทก่อนเปิดคำตอบร้าน และใส่เนื้อหา impact ทั้งหมดในแผน · อนุมัติแผน = ออกจาก Plan mode → Claude บันทึก `docs/impact/CR-0N.md` อย่างเดียวแล้วหยุด · ส่วนที่ 2 ข้อ 0 ตรวจซ้ำว่ามีไฟล์ · commit ทุกตัว: อัปเดต `REGISTER.md` ก่อน แล้ว `git add -A` → `git status` → `git commit` (ไม่มี commit ที่ 3 แค่เพื่อ REGISTER)
- ไม่มีพรอมต์ไหนต้องใช้ Playwright MCP · ทุกอย่างผ่าน `@playwright/test` / สคริปต์ node แบบ headless
- ภาษาไทย/จีนกับ PowerShell 5.1 (M7): ยิง API ที่มี body ภาษาไทย/จีนด้วยสคริปต์ node (หรือ `curl.exe --data-binary '@file.json'`) ไม่ใช้ `Invoke-RestMethod -Body '<สตริงไทย>'` · `curl` ใน PowerShell 5.1 = alias ของ `Invoke-WebRequest` · ตรวจข้อความไทยใน DB ด้วยการเทียบใน SQL หรืออ่านผ่าน API ด้วย node ไม่ตัดสินจากตัวอักษรที่ PowerShell แสดง

---

## LAB 0 · เช็กเครื่อง + พอร์ตที่ Windows จอง

```text
ตรวจเครื่องให้พร้อมสำหรับงานแก้ระบบเดิม "สบายใจ สปา" (อ่านอย่างเดียว ห้ามติดตั้ง ห้ามแก้ไฟล์ ห้ามหยุด container ใด ๆ) ทุกค่าต้องมาจากคำสั่งที่รันจริงใน PowerShell
1. Docker Desktop: docker version และ docker compose version
2. Node.js: node -v (ต้อง 22.18 ขึ้นไป เพราะชุดตรวจ web/scripts/check-rules.mjs import ไฟล์ .ts ตรง) · npm -v · git --version
3. ช่วงพอร์ตที่ Windows จองไว้: netsh interface ipv4 show excludedportrange protocol=tcp
   - บอกว่าพอร์ต 3000, 4000, 5433 อยู่ในช่วงที่จองไหม (ถ้าอยู่ให้บอกช่วงที่ครอบ)
   - อธิบายสั้น ๆ ภาษาง่าย ๆ ว่าทำไมบทนี้เปิดเว็บที่พอร์ต 4000 แทน 3000
4. พอร์ต 4000 และ 5433 มีโปรแกรมใช้อยู่ไหม: Get-NetTCPConnection -LocalPort 4000,5433 -State Listen -ErrorAction SilentlyContinue (ไม่มีผล = ว่าง) และ docker ps --format "{{.Names}} {{.Ports}}" · ถ้าไม่ว่าง บอกด้วยว่าเป็น container ไหน (เช่น เว็บบท 05 ที่เปิดค้างไว้ที่ 4000)
5. มี container หรือ volume ชื่อขึ้นต้นด้วย sabai จากบทก่อนไหม: docker ps -a --filter name=sabai และ docker volume ls --filter name=sabai (บอกอย่างเดียว ยังไม่ต้องปิด)
6. REA: docker image inspect rea-lab:6.4.0 --format "{{.Id}}" · ถ้ามีให้รัน docker run --rm rea-lab:6.4.0 mcp doctor แล้วบอก exit code (0 = พร้อม) · ถ้าไม่มี image ให้บอกคำสั่ง build จากโฟลเดอร์ 05_rea-reverse-engineer-legacy-petshop\rea ใน repo คอร์สที่ clone ไว้ (ยังไม่ต้อง build · build นานหลายนาที)
7. สิทธิ์รันสคริปต์ PowerShell: Get-ExecutionPolicy -List (บอกอย่างเดียว ห้ามแก้ · บทนี้เรียก .ps1 ด้วย powershell -ExecutionPolicy Bypass -File จึงไม่ต้องเปลี่ยนค่าเครื่อง · แถว Process อาจเป็น Bypass เพราะเครื่องมือที่เปิด PowerShell ตั้งให้ชั่วคราว ไม่ใช่ค่าถาวรของเครื่อง)
8. โฟลเดอร์นี้มี web/ db/ e2e-legacy/ tools/ CHANGE-REQUESTS/ ครบไหม · และอยู่ข้างใน git repo อื่นหรือเปล่า: git rev-parse --show-toplevel · error = ยังไม่เป็น repo · ได้ path ของโฟลเดอร์นี้เอง = โฟลเดอร์บทเป็น repo ของตัวเองอยู่แล้ว (ใช้ได้) · ได้ path อื่นที่ไม่ใช่โฟลเดอร์นี้ = อยู่ใน repo อื่น
สรุปเป็นตาราง: รายการ | ผล | พร้อมไหม | ถ้าไม่พร้อมต้องทำอะไร
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** ตารางในแชท 10–11 แถว · บนเครื่องผู้สอน: ช่วงจอง 2970–3069 ครอบ 3000 · 4000 และ 5433 ไม่อยู่ในช่วง [รันจริง:A2 · RF §2.1] · Node v26 · rea-lab 6.4.0 [BRIEF] · `mcp doctor` exit 0 [RF บท 05] · execution policy เครื่องผู้สอน `CurrentUser RemoteSigned` (เครื่องผู้เรียนส่วนใหญ่ `Restricted`/Undefined — ไม่เป็นไรเพราะใช้ Bypass) · ไม่มีการแก้ไฟล์ใด ๆ
**ไปต่อได้เมื่อ** Docker ✅ · Node ≥ 22.18 ✅ · git ✅ · 4000/5433 ว่างและไม่อยู่ในช่วงจอง · มี `rea-lab:6.4.0` · โฟลเดอร์ไม่อยู่ใน repo อื่น (ถ้าอยู่ ให้คัดลอกโฟลเดอร์บทไป `C:\work\sabai06` แล้วเปิด Claude Code ที่นั่น · toplevel = โฟลเดอร์บทเอง = ใช้ได้) · รอบ RUNNER: 4000 ไม่ว่างเพราะเว็บบท 05 (`pawpantry05`) เปิดค้าง → ผู้เรียนใช้ `docker stop pawpantry05` (ไม่ลบอะไร) หรือย้ายพอร์ตด้วย `$env:WEB_PORT` + `$env:BASE_URL`

---

## LAB 1 · รับมอบระบบ

```text
รับมอบระบบเดิม "สบายใจ สปา" จากผู้รับเหมาเดิม แล้วเขียน HANDOVER-CHECK.md (รันคำสั่งด้วย PowerShell จากโฟลเดอร์นี้ · ห้ามแก้ไฟล์ใน web/ db/ e2e-legacy/ · ห้ามเปิด README.md ของบท fast_track/ _solution/ และ CHANGE-REQUESTS/answers/)
0. อ่าน CHANGE-REQUESTS/00-HANDOVER-MEMO.md ก่อน แล้วแยกคำอ้างของผู้รับเหมาเป็นข้อ ๆ (H1, H2, …) · อ่าน e2e-legacy/README-LEGACY.md ด้วย (เป็นคำอ้างของผู้รับเหมาเหมือนกัน ใช้เลข H ต่อจากบันทึกส่งมอบ)
1. เปิดระบบ: docker network create sabai06-net (ถ้ามีแล้วข้ามได้) → docker compose -f db/compose.yaml up -d --wait → docker compose -f web/compose.yaml up -d --build --wait (build ครั้งแรกอาจนานเกิน 2 นาที ให้รันแบบ background หรือตั้ง timeout ยาว แล้วรอจนเสร็จ) · จดเวลาที่ใช้ (เสร็จเร็วและขึ้น CACHED = เคย build แล้ว ไม่ใช่ปัญหา)
2. ตรวจ: GET http://localhost:4000/api/health ต้องได้ {"ok":true,"db":true} · POST http://localhost:4000/api/test/reset · จดเวอร์ชัน Next.js (web/package.json) PostgreSQL (SELECT version()) และ Node ใน container
3. ชุดตรวจที่ส่งมอบ ชั้น 1: node web/scripts/check-rules.mjs → ผ่านกี่ข้อจากกี่ข้อ ใช้เวลาเท่าไร
4. ชุดตรวจที่ส่งมอบ ชั้น 2: Push-Location e2e-legacy; npm install; npx playwright install chromium firefox webkit; npx playwright test; Pop-Location (ค่าเริ่ม = api + chromium · ไม่ต้องใส่ --reporter เพราะ config พิมพ์ผลรายข้อและเขียนรายงาน html ให้ npm run report ตามที่ README-LEGACY อ้างอยู่แล้ว) → แยก ผ่านจริง / คาดว่าล้ม (test.fail) / ล้ม / เวลา · Playwright นับข้อ "คาดว่าล้มแล้วล้มจริง" รวมไว้ใน passed ของบรรทัดสรุป และผลรายข้อแสดง ✘ เหมือนข้อที่ล้มจริง → ข้อ ✘ ที่ไม่อยู่ในรายชื่อ failed ท้ายผล = คาดว่าล้ม · ยืนยันด้วย Select-String -Path e2e-legacy\tests\*.ts -SimpleMatch -Pattern "test.fail("
5. ทุกข้อที่ล้มหรือติด test.fail: เปิดอ่านเทสต์ข้อนั้น (อ่านได้ ห้ามแก้) แล้วจำแนกเป็น บั๊กของระบบ / เทสต์ล้าสมัย / ยังไม่รู้ พร้อมหลักฐาน
6. เทียบคำอ้างทุกข้อในบันทึกส่งมอบกับผลที่รันได้จริง: ตรง ✅ / ไม่ตรง ❌ / ตรวจไม่ได้ตอนนี้ ⚠️ (ข้อไหนตรวจไม่ได้ให้บอกว่าต้องใช้วิธีไหนตรวจ)
7. ตั้ง baseline ด้วย git (เขียน HANDOVER-CHECK.md ให้เสร็จก่อน แล้วค่อย commit · commit id บอกในแชทแล้วเติมลงไฟล์ทีหลังได้):
   - ถ้า git rev-parse --show-toplevel ชี้ไปโฟลเดอร์อื่นที่ไม่ใช่โฟลเดอร์นี้ ให้หยุดแล้วบอกผมก่อน
   - ยังไม่เป็น repo → git init · เป็น repo ของโฟลเดอร์นี้อยู่แล้ว → ข้าม init
   - เพิ่มบรรทัดที่ยังไม่มีใน .git/info/exclude: /_solution/ /img/ /README.md /EXAM.md /fast_track/ rea-out/ backups/ tmp/ node_modules/ test-results/ test-report/ playwright-report/ (มี / นำหน้า = เฉพาะที่รากโฟลเดอร์บท ไม่กัน README.md ในโฟลเดอร์ย่อย)
   - git add -A → git status ต้องไม่เห็นไฟล์ที่ exclude → git commit -m "baseline: ระบบที่รับมอบ" (repo ที่มี commit อยู่แล้วและเปลี่ยนแค่ HANDOVER-CHECK.md ก็ commit ไฟล์นั้นเป็น baseline) → บอก commit id และจำนวนไฟล์
HANDOVER-CHECK.md มี: เวอร์ชัน · container และพอร์ต · เวลาเปิดระบบ · ผลชุดตรวจ 2 ชั้น · ตารางข้อที่ล้ม · ตารางคำอ้าง vs ผลจริง · commit baseline
ทุกตัวเลขต้องมาจากคำสั่งที่รันจริง ถ้าขั้นไหนไม่ผ่านให้หยุดแล้วบอกสาเหตุ ห้ามแก้เทสต์ให้ผ่าน
สรุปเป็นตาราง: ชุดตรวจ | ผ่าน | ล้ม | คาดว่าล้ม | เวลา
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** `HANDOVER-CHECK.md` · check-rules **90/90** ~20 วิ [รันจริง:A6 · รันจากรากต้องยืนยัน: รันจริง:PREP V4] · e2e-legacy api + chromium = 42 รายการ (api 6 + chromium 36): บรรทัดสรุป Playwright **"41 passed · 1 failed"** · ใน 41 มี expected-fail 3 (TC-TRN-03 TC-GC-04 TC-SEC-04) → ผ่านจริง 38 · ล้ม 1 (TC-SEC-05) [บันทึกบท 04 + รันจริง:PREP V5] · build ~42 วิ (ครั้งแรกนานกว่า) [รันจริง:A2] · คำอ้าง H1 ✅ · H2 ❌ (README-LEGACY เองก็บอกว่า TC-SEC-05 แดงค้าง = เอกสารผู้รับเหมาขัดกันเอง) · H3 ⚠️ (ตรวจได้เมื่ออ่านโค้ด) · H4 ❌ (reset ตอบ 200) · H5 ⚠️ · H6 ⚠️ · commit baseline 1 ตัว · **เลข H ขึ้นกับการแตกข้อ** (รอบ RUNNER แตกได้ 12 ข้อ + README-LEGACY ต่อเลข: reset เปิด = H6 ❌ · TC-SEC-05/เอกสารขัดกัน = H9 ❌) → ตรวจด้วยเนื้อหาของคำอ้าง ไม่ใช่เลข · ภาพ `/admin` ใช้ `?date=2026-10-12` (ค่าเริ่มเปิดคิวพรุ่งนี้)
**ไปต่อได้เมื่อ** health `db:true` · มีตัวเลขผ่าน/ทั้งหมดของ 2 ชั้นใน `HANDOVER-CHECK.md` · TC-SEC-05 ถูกจำแนก (คาด: เทสต์ล้าสมัย — ระบบปฏิเสธแล้ว แค่ status 422 ไม่ใช่ 403/404) · มี commit baseline

---

## LAB 2 · มองแบบ black-box ด้วย REA

```text
มองระบบที่รันอยู่แบบ black-box ด้วย REA แล้วเขียน docs/REA-INVENTORY.md (รันคำสั่งด้วย PowerShell · ขั้นนี้ห้ามเปิดอ่านโค้ดใน web/ db/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · ใช้เฉพาะคำสั่งข้างล่าง)
ทุกคำสั่งรันจากโฟลเดอร์บทใน PowerShell · เรียก REA ผ่าน powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 (ไม่ต้องแก้ execution policy ของเครื่อง) · ผลของ REA ใหญ่มาก ห้ามเปิดไฟล์ JSON ทั้งไฟล์ ให้ใช้ tools\rea-tools.mjs สรุป · REA พิมพ์ความคืบหน้าทาง stderr หลายร้อยบรรทัด จึงต่อท้ายคำสั่ง rea.ps1 ด้วย 2> rea-out\<ชื่อ>.log ตามข้างล่าง (เปิด log เฉพาะเมื่อคำสั่ง error)
0. เตรียม: Push-Location tools; npm install; Pop-Location · ระบบต้องเปิดอยู่ (GET http://localhost:4000/api/health ได้ db:true)
1. Static bundle = ของที่ส่งถึงเบราว์เซอร์:
   - ถ้า rea-out\v1\.next\static มีอยู่แล้ว ให้บอกผมก่อนลบแล้วคัดลอกใหม่ (คัดลอกทับจะได้ static\static)
   - New-Item -ItemType Directory -Force rea-out\v1\.next | Out-Null
   - docker cp sabai06-web:/app/.next/static rea-out\v1\.next\static
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\static-v1.json analyze-javascript-application /work/rea-out/v1/.next/static --json 2> rea-out\static-v1.log
   - node tools\rea-tools.mjs endpoints rea-out\static-v1.json
   - node tools\rea-tools.mjs summary rea-out\static-v1.json (node ตามชนิด · endpoint · statistics · coverage · limitations)
   - node tools\rea-tools.mjs pages rea-out\static-v1.json (หน้า/route จากชื่อไฟล์ใน bundle)
   - node tools\rea-tools.mjs view rea-out\static-v1.json rea-out\view-v1.json แล้ว powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\summary-v1.json inspect-analysis-view /work/rea-out/view-v1.json --format json 2> rea-out\summary-v1.log · node tools\rea-tools.mjs summary rea-out\summary-v1.json (summary ที่ REA ทำเอง: statistics และ coverage ต้องตรงกับบรรทัดก่อน)
2. HAR ของเส้นทางใช้งานจริง (ต้องใช้ 127.0.0.1 ไม่ใช่ localhost):
   - ⚠️ record-har.mjs reset ข้อมูลก่อนเดิน แล้วจองนัดใหม่ (รอบรับมอบได้ B14) และยกเลิก B05 → ข้อมูลในระบบเปลี่ยน ถ้างานถัดไปต้องการข้อมูลตั้งต้นให้ reset ใหม่ (POST /api/test/reset)
   - node tools\record-har.mjs http://127.0.0.1:4000 rea-out\journeys.har
   - node tools\rea-tools.mjs har-records rea-out\journeys.har (ได้รายการ --record ของคำขอ /api/*)
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\har-api.json inspect-web-network-capture /work/rea-out/journeys.har har <วาง --record ทั้งหมดที่ได้> --sensitive-value Nida@2026 --sensitive-value Owner@2026 --json 2> rea-out\har-api.log (body ของคำขอ login จะว่างเพราะ --sensitive-value = ตั้งใจ)
   - node tools\rea-tools.mjs har-api rea-out\har-api.json
3. ขับเบราว์เซอร์ด้วย REA (REA อยู่ใน docker network เดียวกับเว็บ จึงเปิด http://sabai06-web:3000 ได้): powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Network sabai06-net -Out rea-out\scenario.json capture-browser-scenario /work/tools/scenario-book-quote.json --json 2> rea-out\scenario.log · node tools\rea-tools.mjs scenario-sum rea-out\scenario.json (step completed x/y · URL สุดท้าย · API ที่เรียก · ยอดในหน้าสรุป) · ดึงภาพหน้าจอที่ REA ถ่าย: node tools\rea-tools.mjs shot rea-out\scenario.json rea-out\scenario-final.png
4. เขียน docs/REA-INVENTORY.md:
   - ตาราง endpoint | เห็นจาก static | เห็นจาก HAR (method, query, body keys, status) | ป้าย static / runtime / inference / unknown | แหล่ง [E ev_xxxxxxxx] (evidence_id 8 ตัวแรกของ Evidence ที่เห็นแถวนั้น · ได้จาก node tools\rea-tools.mjs ids rea-out)
   - ตาราง หน้า (route) ที่เห็นจากชื่อไฟล์ใน bundle (ผลของ pages)
   - หัวข้อ "สิ่งที่ REA ไม่เห็น": ห้ามเขียนว่า "ระบบไม่มี X" ถ้า coverage เป็น partial ให้เขียน "ไม่พบในหลักฐานนี้ เพราะ…"
   - หัวข้อ "คำถามที่ต้องไปหาคำตอบจากโค้ดหรือฐานข้อมูล" อย่างน้อย 5 ข้อ
   - ขนาดไฟล์ เวลา และ evidence_id ย่อ 8 ตัวแรกของ Evidence แต่ละก้อน (ขนาดและป้ายจาก node tools\rea-tools.mjs ids rea-out)
   - หัวข้อ "ค่าที่ล็อกได้เป็น [E]": ยอดหน้าสรุปจาก scenario และสถานะ/คีย์ของ API จาก HAR พร้อมป้าย [E ev_xxxxxxxx] · เขียนกำกับว่า [E] = "ระบบทำอยู่" ใช้ล็อกพฤติกรรมเดิมได้ แต่ไม่ใช่ "ควรทำ"
ถ้าคำสั่งไหน error ให้หยุดแล้วบอกข้อความ error จริง ห้ามเดาผล
สรุปเป็นตาราง: แหล่ง | endpoint ที่เห็น | เวลา | coverage | evidence_id ย่อ
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** `docs/REA-INVENTORY.md` + `rea-out/` (static ~34 MB · summary ~16 KB · HAR ~4 MB · `scenario-final.png` ~100 KB) · static: endpoint จริง **9** (+ เศษจาก minified `[[...]]` `[]` `[...]` และ `/_next/image` = ไม่ใช่ endpoint ของแอป) · route stub **25/25** · หน้า 14 · coverage `partial` · analyze ~53 วิ · HAR: **7 endpoint / 10 ครั้ง** · scenario 12/12 step ยอด **฿1,000** [รันจริง:A2 พอร์ต 3261 · ผ่าน network `sabai06-net` ต้องยืนยัน: รันจริง:PREP V7] · มีหัวข้อ "สิ่งที่ REA ไม่เห็น" ที่อธิบาย `/api/me` `/api/services` (Server Component อ่าน DB ตรง) และ `/cancel` (template literal) · ทุกแถว endpoint มี `[E ev_…]` · `rea-out\*.log` 4 ไฟล์ (stderr ของ REA) · ตัวเลขทั้งหมดได้จาก `ids` `summary` `pages` `scenario-sum` ไม่ต้องใช้ `node -e` · หลัง record-har ข้อมูลเปลี่ยน (B14 · B05 ยกเลิก) → LAB ถัดไป reset ก่อนเสมอ [รันจริง:FIX6T กับผลรอบ RUNNER LAB 2: ids 6 ไฟล์ · summary `/api/*` 9 + อื่น 5 จุด · pages 14 หน้า + `/_not-found` + layout · scenario-sum 12/12 ยอด ฿1,000]
**ไปต่อได้เมื่อ** มีตาราง endpoint ที่ติดป้ายครบ (static/runtime/… + [E]) · ไม่มีประโยค "ระบบไม่มี…" · มีคำถาม ≥ 5 ข้อ · `rea-out/` ไม่ถูก commit (`git status` ไม่เห็น)

---

## LAB 3 · Agent อ่าน repo + DB → แผนที่ระบบ

### ส่วนที่ 1

```text
อ่าน repo นี้แล้วเขียน SYSTEM-MAP.md = แผนที่ระบบเดิมสำหรับทีมใหม่ และ docs/SPEC-GAPS.md (รันคำสั่งด้วย PowerShell · ห้ามแก้โค้ด · ห้ามเปิด README.md ของบท fast_track/ _solution/ และ CHANGE-REQUESTS/answers/)
ใช้ Explore subagent ช่วยค้นได้ แต่ทุกแถวในไฟล์ต้องอ้าง ไฟล์:บรรทัด หรือชื่อฟังก์ชัน/ชื่อ constraint ที่เปิดดูจริง
1. สถาปัตยกรรม: compose 2 project · network · container · พอร์ต · env ที่มีผล (web/compose.yaml, db/compose.yaml, web/Dockerfile)
2. ชั้นของโค้ด หน้า → API route → lib/server → lib/rules · ตาราง route ทุกตัวใน web/app/api: method | path | ฟังก์ชันที่เรียก | component ไหนเรียก (หรือไม่มี) · นับ 2 แบบแล้วรายงานทั้งคู่: จำนวนไฟล์ route.ts และจำนวน handler (method + path)
3. กฎร้าน: ไล่ web/lib/rules ทุกไฟล์ → ตาราง กฎ (ภาษาคน) | ค่าคงที่ | ฟังก์ชัน | ถูกเรียกจาก | ข้อความที่พูดกฎเดียวกันซ้ำ (i18n, แชท, หน้าเว็บ)
4. ฐานข้อมูล: docker exec sabai06-db psql -U sabai -d sabai -c "\dt" แล้ว -c "\d booking" และ -c "\d booking_slot" → ตาราง: ตาราง | กฎที่ DB บังคับ (CHECK / EXCLUDE / UNIQUE) | กฎเดียวกันในโค้ดอยู่ไหน
   นับ constraint ทั้งระบบด้วยคำสั่ง (ไม่นับด้วยตา): docker exec sabai06-db psql -U sabai -d sabai -c "SELECT contype, count(*) FROM pg_constraint WHERE connamespace = 'public'::regnamespace GROUP BY 1 ORDER BY 1" (c = CHECK · f = FK · x = EXCLUDE · p = PK · u = UNIQUE) และแยกต่อตารางด้วย SELECT conrelid::regclass, contype, count(*) … GROUP BY 1, 2
5. Test hooks และ "วันนี้" ของระบบ: /api/test/* ทำอะไร · นาฬิกาอ่านจากไหน · reset ล้างตารางไหนและเอา seed มาจากไหน
6. กับดักถ้าจะแก้: ค่าที่เขียนตายตัว · กฎที่คิดซ้ำทั้งเซิร์ฟเวอร์และเบราว์เซอร์ · ไฟล์ db/init รันตอนไหน
7. Triangulation: เทียบกับ docs/REA-INVENTORY.md → ตาราง endpoint/กฎ | REA เห็น [E ev_xxxxxxxx] | source บอก [source ไฟล์:บรรทัด] | DB บอก [DB ชื่อ constraint] | SPEC บอก [SPEC §] | ตรงไหม ✅/⚠️/❌ | ถ้า REA ไม่เห็น เพราะอะไร · ทุกช่องต้องมีป้ายแหล่ง (ช่องที่ REA ไม่เห็นให้เขียน "REA ไม่เห็น" + เหตุผล ห้ามแต่ง ev_) · แถวที่ [E] หรือ [source] ขัดกับ [SPEC] ให้ส่งต่อเป็นคำถามใน SPEC-GAPS (ห้ามตัดสินเอง)
8. เอกสารเก่า: เทียบ web/SPEC.md กับโค้ดจริงแล้วเขียน docs/SPEC-GAPS.md: SPEC บอก | โค้ดทำ | หลักฐาน | คำถามถึงร้าน (ห้ามตัดสินเองว่าฝั่งไหนถูก)
ท้าย SYSTEM-MAP.md ใส่วันที่และ commit ที่ใช้ทำแผนที่ (git rev-parse --short HEAD) · ไม่แน่ใจข้อไหนให้เขียนในหัวข้อ "ยังไม่รู้" อย่าเดา
สรุปเป็นตาราง: หัวข้อ | จำนวนแถว | ข้อที่ยังไม่รู้
```

### ส่วนที่ 2 (เซสชันเดียวกัน · เราตรวจทานเอง)

```text
(รันคำสั่งด้วย PowerShell) ผมจะตรวจทาน SYSTEM-MAP.md ด้วยตาตัวเอง สุ่มมา 5 แถว: กฎร้าน 2 แถว · route 1 แถว · ฐานข้อมูล 1 แถว · กับดัก 1 แถว (สุ่มเลขแถวในแต่ละหัวข้อด้วย Get-Random ไม่เลือกแถวเอง)
แต่ละแถว เปิดไฟล์ตามที่อ้างแล้วคัดบรรทัดจริงมาให้ผมดู (ไม่เกิน 5 บรรทัดต่อข้อ) ฐานข้อมูลให้รัน psql ให้ดูผลจริง
ถ้าแถวไหนอ้างผิดหรือไม่ครบ ให้แก้ SYSTEM-MAP.md แถวนั้น แล้วบอกว่าผิดเพราะอะไร
เพิ่มหัวข้อ "ตรวจทานโดยคน" ท้าย SYSTEM-MAP.md
สรุปเป็นตาราง: แถวที่สุ่ม | ที่อ้าง | บรรทัดจริง | ตรงไหม ✅/❌ | แก้อะไร
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** `SYSTEM-MAP.md` (route 25 ไฟล์ / 26 handler · BR-01–20 ครบ · 19 ตาราง · CHECK 51 · FK 25 · EXCLUDE 2 (+ PK 19 · UNIQUE 10) จากคิวรี pg_constraint ในข้อ 4 [รันจริง:A2 RF §2.6 · ยืนยันรอบ RUNNER]) · กับดักที่ควรเจอ: `room_id = 1` 2 ที่ · `TABLES` ใน `lib/server/testmode.ts` · init รันเฉพาะ volume ว่าง · `PackageCalc` คิดราคาซ้ำฝั่งเบราว์เซอร์ · ข้อความเวลาเปิดซ้ำใน i18n/แชท [CN §7] · `docs/SPEC-GAPS.md` ≥ 7 แถว: **S2 S3 S5–S9** + พอร์ต 3000/ชื่อ `sabai-*` ในเอกสารเก่า [CN §8 + P4] · ตรวจทาน 5 แถว · triangulation ทุกช่องมีป้าย [E]/[source]/[DB]/[SPEC]
> 🔒 ผู้ตรวจรอบ RUNNER/ผู้เขียน README: ถ้า SPEC-GAPS ของรอบจริงมีแถวเรื่อง "กดใช้บริการเสร็จได้ก่อนถึงเวลานัด" (S4 = L2 = ข้อสอบชุด B ข้อ 5) **ห้ามคัดลง README และภาพ `lab3-*`** · เก็บไว้ใน `_solution` เท่านั้น (M10)
**ไปต่อได้เมื่อ** ทุกแถวมี `file:line` หรือชื่อ constraint · มีตาราง triangulation 3 ตา (+SPEC) พร้อมป้ายแหล่ง · SPEC-GAPS เป็นคำถาม ไม่ใช่คำตัดสิน · ตรวจทานครบ 5 แถว

---

## LAB 4 · CLAUDE.md + รั้ว

### ส่วนที่ 1

```text
เขียน CLAUDE.md สำหรับระบบเดิมนี้ + .claude/settings.json + docs/IMPACT-TEMPLATE.md + docs/ORACLE-CHANGES.md (รันคำสั่งด้วย PowerShell · ห้ามแก้โค้ดใน web/ db/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
อ่าน SYSTEM-MAP.md, docs/SPEC-GAPS.md และ HANDOVER-CHECK.md ก่อน
1. CLAUDE.md ไม่เกิน ~60 บรรทัด หัวข้อ: รันยังไง (PowerShell จากโฟลเดอร์บท: เปิดระบบ · reset · node web/scripts/check-rules.mjs · e2e ด้วย Push-Location/Pop-Location · ค่าเริ่ม api+chromium และคำสั่งครบ 3 เบราว์เซอร์ npm run test:all) · แผนที่: ลิงก์ไป SYSTEM-MAP.md แบบธรรมดา (ไม่ใช้ @ เพราะไฟล์ใหญ่ จะถูกโหลดเข้าทุกเซสชัน) · ห้ามแตะ · กติกาการแก้ · กับดัก (จาก SYSTEM-MAP) · เอกสารเก่า (@docs/SPEC-GAPS.md)
2. กติกาที่ต้องมี:
   - อธิบายและทำ impact ตาม docs/IMPACT-TEMPLATE.md ก่อนแก้ทุกครั้ง · เทสต์ใหม่ต้องแดงก่อนแก้ · แก้ให้เล็กที่สุด
   - ห้ามแก้ค่าที่คาดหวังเดิมใน web/scripts/check-rules.mjs, e2e-legacy/ และ tests/golden/ ถ้าไม่มี CR อนุญาต (ถ้าจำเป็นให้หยุดถาม แล้วจดใน docs/ORACLE-CHANGES.md)
   - ค่าที่คาดหวังติดป้ายแหล่งเสมอ: [D:CR-0N] จากคำตอบร้าน · [E ev_xxxxxxxx] จากหลักฐานระบบ (ใช้ได้เฉพาะล็อกพฤติกรรมเดิม) · [E] ขัด [D] = ผู้ต้องสงสัยบั๊ก ให้รายงาน ห้ามใช้ [E] นั้นเป็นค่าคาดหวัง
   - ห้าม docker compose down -v และห้ามลบ volume sabai06-pgdata (มีข้อมูลลูกค้าจริง)
   - เปลี่ยนโครงฐานข้อมูลด้วยไฟล์ migration แยก (db/migrations/) = ทางเดียวสำหรับฐานที่มีข้อมูลอยู่แล้ว · รันซ้ำได้ มีวิธีถอยกลับ · แก้ db/init ได้เฉพาะเพื่อให้เครื่องติดตั้งใหม่และ reset ตรงกับ migration ห้ามใช้ db/init เป็นวิธี deploy · รัน SQL ด้วย docker cp + psql -f (ห้าม pipe ไฟล์ภาษาไทยผ่าน PowerShell) · SQL ที่มีภาษาไทยหรือ quote ให้เขียนลงไฟล์แล้ว psql -f (ไม่ใช้ psql -c "<SQL>" ใน PowerShell)
   - ภาษาไทย/จีนกับ PowerShell 5.1: ยิง API ที่มีข้อความไทย/จีนด้วยสคริปต์ node หรือ curl.exe --data-binary '@ไฟล์.json' (ห้าม Invoke-RestMethod -Body '<ไทย>' · curl เฉย ๆ = Invoke-WebRequest) · ตรวจข้อความไทยใน DB ด้วยการเทียบใน SQL (เช่น SELECT name_th = '<ข้อความ>') หรืออ่านผ่าน API ด้วย node · ห้ามตัดสินจากตัวอักษรที่ PowerShell แสดง (อาจเพี้ยนทั้งที่ข้อมูลถูก) และห้ามแก้ข้อมูลเพราะเห็นตัวอักษรเพี้ยนบนจอ
   - build หรือชุดทดสอบที่นานเกิน 2 นาที (เช่น docker compose up --build ครั้งแรก · e2e 3 เบราว์เซอร์) ให้รันแบบ background หรือ timeout ยาว แล้วรอผลจริง
   - ข้อความใหม่ต้องครบ 3 ภาษา (th/en/zh) · error ใหม่ต้องตรวจผลในแชทบอทด้วย
   - เอกสารเก่าขัดกับโค้ด ให้รายงานแล้วถาม ห้ามเลือกเอง
   - ห้ามเปิดอ่าน README.md ที่รากโฟลเดอร์บท fast_track/ และ _solution/ (เอกสารผู้สอนและเฉลย) ทั้งด้วยเครื่องมืออ่านไฟล์และคำสั่ง shell
3. .claude/settings.json: permissions.deny = ["Edit(e2e-legacy/**)", "Read(/README.md)", "Read(./fast_track/**)", "Read(./_solution/**)"] (กฎ Edit(...) กันเครื่องมือแก้/เขียนไฟล์ของ Claude Code ทุกตัว · Read(/README.md) ขึ้นต้นด้วย / = เฉพาะ README.md ที่รากโฟลเดอร์บท ไม่กัน README ในโฟลเดอร์ย่อย · deny ไม่กันคำสั่ง shell จึงต้องเขียนห้ามใน CLAUDE.md ด้วย)
4. docs/IMPACT-TEMPLATE.md (แม่แบบของ docs/impact/CR-0N.md ทุก CR): คำถามถึงร้าน · ตาราง ไฟล์ที่จะแตะ | เหตุผล (CR) | ใครเรียกใช้ (หลักฐาน grep ไฟล์:บรรทัด) | หน้าจอ/API/แชทที่กระทบ | ตาราง DB | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง · ค่าที่คาดหวังใหม่พร้อมวิธีคิด · เทสต์ใหม่ที่จะเขียนก่อน (ต้องแดง) · วิธีถอยกลับ · หัวข้อ "ค้นแล้วไม่เจอ": คำค้นที่ใช้ + ที่อาจหลุด (ชื่อประกอบจาก string · key i18n แบบ template · SQL ใน string) · grep ไม่เจอ ≠ ไม่มีผู้เรียก ให้ยืนยันด้วยการรันเทสต์ หรือเขียนเป็นความเสี่ยง
5. docs/ORACLE-CHANGES.md: ตาราง วันที่ | ไฟล์เทสต์ | เคส | ค่าเดิม → ใหม่ | CR ที่อนุญาต | ผู้อนุมัติ (ตอนนี้ยังว่าง)
ไม่แน่ใจข้อไหนให้ถามผมก่อน · เสร็จแล้ว git add -A (รวม HANDOVER-CHECK.md docs/REA-INVENTORY.md SYSTEM-MAP.md docs/SPEC-GAPS.md ที่ยังไม่ได้ commit · rea-out/ ถูก exclude แล้ว) → git status ตรวจว่าไม่มีไฟล์ที่ไม่ควรเข้า → commit "docs: CLAUDE.md + รั้ว"
สรุปเป็นตาราง: ไฟล์ | หัวข้อ | จำนวนบรรทัด
```

### ส่วนที่ 2 (**เปิดเซสชันใหม่** เพื่อให้ settings ใหม่มีผล · เปิดด้วย `claude` ธรรมดา ห้ามใส่ `--dangerously-skip-permissions`)

```text
(รันคำสั่งด้วย PowerShell) ทดสอบรั้วของโปรเจกต์นี้: ลองเพิ่มคอมเมนต์ 1 บรรทัด "// test fence" ที่บรรทัดแรกของ e2e-legacy/playwright.config.ts ด้วยเครื่องมือแก้ไฟล์ปกติ
ห้ามใช้ PowerShell หรือคำสั่ง shell แก้แทน · ถ้าแก้ได้ ให้ลบบรรทัดนั้นคืนทันทีแล้วบอกผมว่ารั้วไม่ทำงาน
รายงานข้อความที่ได้รับจริง แล้วตรวจ git status ว่า e2e-legacy/ ไม่มีไฟล์เปลี่ยน
จากนั้นลองเปิดอ่าน README.md ที่รากโฟลเดอร์นี้ด้วยเครื่องมืออ่านไฟล์ปกติ (ห้ามใช้ shell) · ถ้าอ่านได้ ห้ามสรุปเนื้อหา ให้บอกแค่ว่า "อ่านได้ = รั้วอ่านไม่ทำงาน"
สรุปเป็นตาราง: ทดสอบ | ผล | ข้อความจริง | git status
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** `CLAUDE.md` ≤ ~60 บรรทัด (มีกติกาภาษาไทย/PowerShell · migration = ทางเดียว · ป้าย [E]/[D]) · `.claude/settings.json` 4 กฎ (`Edit(e2e-legacy/**)` + `Read` README รากบท / fast_track / _solution · D15a) · แม่แบบ 2 ไฟล์ (IMPACT-TEMPLATE ชี้ `docs/impact/CR-0N.md`) · ส่วนที่ 2: แก้ไม่ได้ ข้อความแบบ *"File is in a directory that is denied by your permission settings."* [MT §M1 ตรวจแล้ว · รอบ RUNNER ตรงตัว · orchestrator ยืนยันว่า acceptEdits ก็ถูกปฏิเสธ] · อ่าน README.md รากบทถูกปฏิเสธ [D15a ทดสอบกฎด้วย claude -p · ข้อความจริงรอรอบ RUNNER ถัดไป] · `git status` สะอาดใน `e2e-legacy/` · commit รวมไฟล์ของ LAB 1–3
**ไปต่อได้เมื่อ** รั้วปฏิเสธจริงในเซสชันใหม่ · CLAUDE.md มีคำสั่งรันทุกชุด + ห้าม `down -v` + กติกาค่าคาดหวัง

---

## LAB 5 · ตาข่ายกันพลาด

### ส่วนที่ 1 · seam + golden master

```text
สร้างตาข่ายกันพลาดก่อนรับ Change Request (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ไฟล์ใน web/lib/rules/ และ web/lib/server/booking.ts · ห้ามแก้ e2e-legacy/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. อธิบายของเดิมก่อนแก้ (อ้างไฟล์:บรรทัด · ใช้หัวข้อ test hooks ใน SYSTEM-MAP.md ประกอบ): /api/test/reset และ /api/test/today อยู่ไฟล์ไหน · ตรวจ ALLOW_TEST_RESET ที่ไหน · "วันนี้" ของระบบเก็บที่ตาราง/คอลัมน์ไหน · ไฟล์ที่จะเพิ่ม/แก้มีอะไรบ้าง → แสดงในแชทก่อน แล้วจึงทำส่วน A
ส่วน A · test seam: เพิ่ม POST /api/test/clock {"now":"<ISO>"} = เปลี่ยน "วันนี้" ของระบบโดยไม่ล้างข้อมูล
   - ใช้เงื่อนไขเปิด/ปิดเดียวกับ /api/test/reset (ALLOW_TEST_RESET=0 → 404) · แก้แค่ค่า test_today ไม่แตะตารางอื่น
   - rebuild: docker compose -f web/compose.yaml up -d --build --wait (ถ้านานเกิน 2 นาทีให้รันแบบ background แล้วรอ)
   - พิสูจน์: reset → จองนัดใหม่ 1 นัดผ่าน API → เลื่อนนาฬิกา → GET /api/test/today เปลี่ยน · นัดยังอยู่ในตารางคิว
   - พิสูจน์ปิดได้: $env:ALLOW_TEST_RESET="0"; docker compose -f web/compose.yaml up -d --wait → clock ได้ 404 → ตั้งกลับ "1" แล้ว up อีกครั้ง
ส่วน B · golden master ของ API ที่ tests/golden/run.mjs (Node ≥ 22.18 ไม่ใช้ dependency · BASE_URL ค่าเริ่ม http://localhost:4000)
   - reset {"now":"2026-10-10T10:00:00+07:00"} ก่อนทุกกลุ่ม
   - POST /api/price: ผู้ใช้ seed (ไม่ล็อกอิน + U01–U08) × แบบจอง (เดี่ยว คู่ กลุ่ม 3–6 แพ็กเกจ คอร์ส) × แลกแต้ม/ไม่แลก × Gift Card/ไม่ใช้ × รถ (ไม่ใช้ H01 H04 H05) เลือกชุดที่ถูกกฎราว 40–60 เคส (นับเฉพาะ /api/price · slots และตารางคิวนับแยก)
   - GET /api/slots: S01 S02 P01 วันที่ 2026-10-22 และ 2026-10-24
   - ตารางคิวหลังร้าน (ล็อกอิน owner) วันที่ 2026-10-12 ถึง 2026-10-17
   - node tests/golden/run.mjs --update เขียน tests/golden/*.json · ไม่ใส่ --update = เทียบ แล้ว exit 1 ถ้าต่าง พร้อมบอกเคสและฟิลด์ที่ต่าง
   - ตัดฟิลด์ที่เปลี่ยนเองทุกรอบ (id ที่รัน, เวลาสร้าง, cookie) ก่อนเทียบ แล้วเขียนเหตุผลใน tests/golden/README.md
   - รัน --update 1 ครั้ง แล้วรันเทียบอีก 2 ครั้ง ต้องผ่านทั้ง 2 ครั้ง (นิ่ง)
   - tests/golden/README.md ระบุว่าค่าทั้งหมดเป็นป้าย [E] (หลักฐานจากระบบที่รับมอบ = ล็อกพฤติกรรมเดิม ไม่ใช่ตัดสินว่าถูก) พร้อมตาราง ไฟล์ golden | SHA-256 ย่อ 8 ตัว (Get-FileHash) | จำนวนเคส | เวลาที่รัน --update · ใน README อ้างค่าใดให้เขียน [E golden/<ไฟล์>:<sha8>]
ทุกค่าใน golden มาจากการรันระบบที่รับมอบ ห้ามเดาหรือแก้ให้ "ถูก" · เจอค่าที่ดูแปลกให้จดไว้ใน README อย่าแก้
สรุปเป็นตาราง: ส่วน | ไฟล์ | จำนวนเคส | ผล
```

### ส่วนที่ 2 · ล็อกหน้าจอ + known issue

```text
ล็อกหน้าจอสำคัญ และบันทึกพฤติกรรมแปลกเป็น known issue (รันคำสั่งด้วย PowerShell · ห้ามแก้โค้ดใน web/ · ห้ามแก้ e2e-legacy/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
1. สร้างโฟลเดอร์ e2e-cr/ ข้าง web/ (ห้ามสร้างข้างใน web/) = ชุด Playwright ใหม่ของทีม: @playwright/test 1.63.0 · baseURL จาก BASE_URL ค่าเริ่ม http://localhost:4000 · chromium firefox webkit · workers 1 · locale th-TH · timezone Asia/Bangkok · reset ก่อนทุก test · รอ html[data-ready="true"]
   (ดูแนวทางจาก e2e-legacy/playwright.config.ts และ global-setup.ts ได้ แต่ห้ามแก้ของเดิม)
2. e2e-cr/tests/char-booking.spec.ts: ไม่ล็อกอิน จอง S01 วันที่ 12 ต.ค. 15:00 จนถึงหน้าสรุป → ล็อกยอดจาก data-amount และโครงหน้าสรุปด้วย toMatchAriaSnapshot ที่มี /children: equal · ใส่ annotation ป้ายแหล่งของยอด: [E ev_xxxxxxxx] จาก rea-out\scenario.json (ยอดหน้าสรุปที่ REA บันทึกไว้ใน docs/REA-INVENTORY.md) ถ้ายอดที่ล็อกได้ไม่ตรงกับ [E] นั้นให้หยุดบอกผม · เขียน template ของ aria snapshot เองเป็นข้อความตรง (เช่น ยอด "฿1,000") ห้ามใช้ regex ที่ Playwright สร้างให้ (ตัวเลขที่กลายเป็น regex = ไม่ได้ล็อกยอด)
3. ลองของแปลก 3 เรื่อง แล้วเขียน KNOWN-ISSUES.md (อาการ | วิธีทำซ้ำ | หลักฐาน | ผลกระทบ | สถานะ "ยังไม่แก้" | ต้องถามร้านไหม)
   - หน้าจอง: ใส่รหัส Gift Card ที่ไม่มีอยู่ ดูว่ามีข้อความเตือนไหม (เทียบกับคำตอบของ GET /api/giftcards/<รหัส>)
   - จองแบบไม่ล็อกอินด้วยเบอร์โทร "abc"
   - เจ้าของร้าน (owner) ยกเลิกนัดของลูกค้าผ่าน API
   ก่อนตัดสินว่าเป็นบั๊ก ให้เทียบกับ docs/SPEC-GAPS.md (ถ้าเรื่องนั้นยังเป็นคำถามค้างถึงร้าน = "ต้องถามร้าน" ล็อกพฤติกรรมอย่างเดียว ไม่ต้องมี test.fail)
   ข้อที่คิดว่าเป็นบั๊ก: เขียนเทสต์คู่ใน e2e-cr ① ล็อกพฤติกรรมปัจจุบัน ② test.fail() ที่ assert พฤติกรรมที่ควรเป็น + annotation อ้าง KNOWN-ISSUES.md
4. Push-Location e2e-cr; npm install; npx playwright test; Pop-Location (3 เบราว์เซอร์) รัน 2 รอบ ต้องได้ผลเท่ากันทั้ง 2 รอบ (บรรทัดสรุปนับ test.fail ที่ล้มตามคาดรวมใน passed ให้แยกนับในตาราง)
ห้ามแก้บั๊กที่เจอ (ยังไม่มี CR สั่ง) · ไม่แน่ใจว่าบั๊กหรือตั้งใจ ให้เขียน "ต้องถามร้าน"
สรุปเป็นตาราง: test | chromium | firefox | webkit | รอบ 1 = รอบ 2 ไหม | known issue
```

### ส่วนที่ 3 · ทำพังเองเพื่อวัดตาข่าย

```text
วัดว่าตาข่ายจับการพังได้จริงไหม (mutation testing แบบมือ · รันคำสั่งด้วย PowerShell จากโฟลเดอร์บท) · ทำทีละตัว และต้องคืนไฟล์ทุกครั้ง (ห้าม commit โค้ดที่ทำพัง · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
ตัวทำพัง 3 ตัว แก้ตัวละ 1 บรรทัด:
  X1 web/lib/rules/tier.ts: spend >= GOLD_MIN → spend > GOLD_MIN
  X2 web/lib/rules/transport.ts: SEATS_PER_VEHICLE = 4 → 5
  X3 web/lib/rules/pricing.ts: GROUP_PCT = 10 → 15
ต่อ 1 ตัว: แก้ → docker compose -f web/compose.yaml up -d --build --wait (golden ยิง API จึงต้อง rebuild ทุกตัว) → node tests/golden/run.mjs → node web/scripts/check-rules.mjs → Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location (chromium อย่างเดียวพอ) → จดว่าชุดไหนจับได้ → คืนไฟล์ด้วย git checkout -- <ไฟล์> → git status ต้องสะอาดในไฟล์นั้น
จบครบ 3 ตัวแล้ว rebuild โค้ดปกติ แล้วรัน golden ต้องผ่าน
ตัวที่ไม่มีชุดไหนจับได้ (รอด): อธิบายว่าตาข่ายมีรูตรงไหน แล้วเสนอเคสที่จะอุดรู (ยังไม่ต้องเขียน) ลง tests/golden/README.md
ถ้าคืนไฟล์ไม่ได้หรือ rebuild ล้ม ให้หยุดแล้วบอกผม
เสร็จแล้ว git add tests e2e-cr KNOWN-ISSUES.md web → git status ตรวจว่าไฟล์ครบ (tests/golden/README.md และ tests/golden/*.json ต้องอยู่ในรายการที่จะ commit) → commit "safety-net: seam + golden + characterization"
สรุปเป็นตาราง: ตัวทำพัง | golden | check-rules | e2e-cr | ถูกจับ / รอด
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** ส่วนที่ 1: route ใหม่ `web/app/api/test/clock/route.ts` (+ ฟังก์ชันใน `lib/server/testmode.ts`) · clock 404 เมื่อปิด · golden ราคา 40–60 เคส (รอบ RUNNER: price 50 + slots 6 + คิว 6 = 62) นิ่ง 2/2 รอบ · `tests/golden/README.md` มีตาราง SHA-256 ย่อ + ป้าย [E] · char-booking ยอดตรง [E] ของ scenario (฿1,000) · ส่วนที่ 2: `e2e-cr/` · char-booking ยอด ฿1,000 (ราคา S01 [seed]) · aria snapshot เป็นข้อความตรง (ที่ Playwright สร้างให้เป็น regex `/฿\d+,\d+/` = ไม่ล็อกยอด) · known issue 3 เรื่อง: บัตรปลอม API 422 `GC_NOT_FOUND` แต่หน้าจอไม่เตือน · เบอร์ "abc" → 201 · owner ยกเลิก → 200 = "ต้องถามร้าน" (ล็อกอย่างเดียว ไม่มี test.fail) [รันจริง:A6 CN §7 L5 L6 L7] · ส่วนที่ 3: X1 X2 X3 ถูกจับครบ โดย golden (2 · 3 · 10 จาก 62 เคส) และ check-rules (88 · 88 · 83/90) · e2e-cr ไม่จับเลย = ตาข่ายหน้าจอบาง [รันจริง:RUNNER LAB 5] · commit 1 ตัว (มี tests/golden/README.md)
**ไปต่อได้เมื่อ** golden ผ่าน 2 รอบติด · e2e-cr ผ่านเท่ากัน 2 รอบ × 3 เบราว์เซอร์ · `git status` สะอาดหลังคืน mutant · มี KNOWN-ISSUES.md 3 เรื่อง

---

## LAB 6 · CR-02 เปลี่ยนกฎ (วันมีผล)

### ส่วนที่ 1 · วิเคราะห์ (Plan mode)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-02.md ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · Plan mode เขียนไฟล์ไม่ได้ ทุกอย่างให้อยู่ในแชทและแผน)
1. สรุปคำขอเป็นภาษาคน 3–5 ข้อ แล้วแสดง "คำถามถึงร้าน" ทุกเรื่องที่ยังไม่ชัดในแชท
1.5 อธิบายของเดิมก่อนแก้ (อ้างไฟล์:บรรทัด): ระบบคิดส่วนลดกลุ่มและเลือกส่วนลดที่มากที่สุดอย่างไร (bestPercent / calcPrice / buildQuote) · ใครเรียกฟังก์ชันเหล่านี้บ้าง · "วันนี้ของระบบ" ที่ใช้ตอนคิดราคามาจากไหน
2. แสดงคำถามเสร็จแล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-02-ANSWERS.md · บอกว่าคำถามไหนได้คำตอบ ข้อไหนยังค้าง (ข้อค้างให้ใช้สมมติฐานที่ระบุชัด ติด ⚠️)
3. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-02.md) ตาม docs/IMPACT-TEMPLATE.md · ทุกแถวมีหลักฐาน grep (ไฟล์:บรรทัด) · ต้องครอบ: ฟังก์ชันราคา · ผู้เรียกทุกตัว (รวมแชท) · unit test ใน web/scripts/check-rules.mjs ที่เรียกฟังก์ชันราคาตรง · ข้อความ i18n · หน้าจอ
4. คำนวณค่าที่คาดหวังเองจากกฎใหม่ (แสดงวิธีคิด ฿ − % =) อย่างน้อย 8 เคส: กลุ่ม 2/3/4/5/6/7 คน · ขอบวันมีผล (31 ต.ค. 23:59 กับ 1 พ.ย. 00:00) · ส่วนลดกลุ่มเท่ากับส่วนลดสมาชิก · แพ็กเกจ · นัดที่จองก่อนวันมีผลแต่วันนัดอยู่หลัง · เคสที่ยอดเท่าเดิมแต่ชนิดส่วนลดเปลี่ยน (เช่น Gold กลุ่ม 3) ต้องตรวจ discountKind ด้วย ไม่ใช่แค่ยอด · ทุกแถวติดป้ายแหล่ง: [D:CR-02] = ตรงกับตัวอย่าง/กฎที่ร้านยืนยัน · [E golden/<ไฟล์>:<sha8>] = ค่าเดิมที่ต้องไม่เปลี่ยน (ก่อนวันมีผล) · ถ้า [E] ขัดกับ [D:CR-02] ให้เขียนว่า "ผู้ต้องสงสัยบั๊ก" แล้วถามผม ห้ามใช้ [E] นั้นเป็นค่าคาดหวัง
5. เสนอแผนแก้ทีละขั้น + รายการเทสต์ใหม่ที่จะเขียนก่อน (ต้องแดงบนโค้ดเดิม) แล้วรอผมอนุมัติ · หลังผมอนุมัติ (ออกจาก Plan mode) ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-02.md อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ไฟล์ที่จะแตะ | เหตุผล | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง
```

### ส่วนที่ 2 · ลงมือ (โหมดปกติ)

```text
ทำ CR-02 ตามแผนใน docs/impact/CR-02.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิมใน web/scripts/check-rules.mjs และ tests/golden/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-02.md: ถ้าแผนที่ผมอนุมัติยังอยู่ในแชทนี้ ให้บันทึกจากแผนนั้น · ถ้าไม่มี (เซสชันใหม่) ให้หยุดแล้วบอกผมให้วางส่วนที่ 1 ใหม่ ห้ามเขียนแผนเองแล้วลงมือ
1. เทสต์ก่อน: tests/cr02.mjs (Node ไม่ใช้ dependency · reset เอง · คุม "วันที่จอง" ด้วย reset {now} หรือ POST /api/test/clock) ใส่ทุกเคสจากข้อ 4 ของ impact
   รันบนโค้ดเดิม → เคสอัตราใหม่ต้องแดง · บันทึกผลแดงลง docs/impact/CR-02.md → git add tests/cr02.mjs docs/impact/CR-02.md → git commit "CR-02 test: แดงก่อนแก้"
2. แก้โค้ดให้เล็กที่สุดตามแผน · อัตราส่วนลดอยู่จุดเดียว ไม่ hardcode ซ้ำ · ค่าเริ่มของพารามิเตอร์ใหม่ต้องให้ผลเหมือนเดิม · rebuild web
3. เขียว: node tests/cr02.mjs ผ่านทุกเคส
4. Regression (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs (ต้องผ่านเท่าเดิม และ git diff web/scripts/check-rules.mjs ต้องว่าง) · node tests/golden/run.mjs · Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location · Push-Location e2e-legacy; npx playwright test; Pop-Location (ค่าเริ่ม api + chromium · 3 เบราว์เซอร์รอบเต็มทำตอนส่งมอบ)
5. ข้อไหนแดงที่ไม่ได้ตั้งใจ ให้หยุดแล้วบอกผมว่าเป็น เว็บผิด / เทสต์เก่าล้าสมัย / เทสต์ใหม่เขียนผิด · ห้ามแก้เทสต์ให้ผ่านเฉย ๆ
6. เอกสาร: อัปเดต web/SPEC.md เฉพาะกฎส่วนลดกลุ่ม + บรรทัดประวัติแก้ไข · docs/TRACEABILITY.md (สร้างถ้ายังไม่มี) แถว CR-02 → BR-06 (ข้อความกฎใหม่) → TC ทุกตัวที่พิสูจน์ (ใหม่ + regression) → ผล · CHANGE-REPORT.md ส่วน CR-02: ไฟล์ที่แก้ (git diff --stat) · แดง→เขียว · regression · พฤติกรรมที่เปลี่ยนโดยตั้งใจ · ความเสี่ยงคงค้าง · วิธีถอยกลับ
7. อัปเดตสถานะใน CHANGE-REQUESTS/REGISTER.md ก่อน (สถานะ + hash ของ commit แดง) → git add -A → git status ตรวจไฟล์ → git commit "CR-02: ส่วนลดกลุ่มขั้นบันได มีผล 1 พ.ย. 2026"
สรุปเป็นตาราง: ชุดทดสอบ | ก่อนแก้ | หลังแก้ | หมายเหตุ
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** [CRD §1 คาด] กลุ่ม S01 นัด 5 พ.ย. จองวันที่ 1 พ.ย. (Silver): 2 → 422 `GROUP_TOO_SMALL` · 3 → ฿2,850 · 4 → ฿3,600 · 5 → ฿4,250 · 6 → ฿5,100 · 7 → 422 `GROUP_CALL_SHOP` · 31 ต.ค. 23:59 กลุ่ม 3 → ฿3,000 · Gold กลุ่ม 3 → ฿2,850 `group` (ยอดเท่าเดิม ต้องตรวจ discountKind ไม่งั้นเขียวตั้งแต่ก่อนแก้) · แพ็กเกจ 4 คน ฿11,600 · B04 ยัง ฿4,500 · quote ข้ามเที่ยงคืน → 409 `PRICE_CHANGED` · check-rules เท่าเดิม (E26 ฿3,000 · E28 ฿4,500 · E79 ฿6,000) และ **diff ว่าง** · golden ผ่าน (ล็อก 10 ต.ค.) · e2e-legacy api+chromium "41 passed · 1 failed" เท่า baseline · impact (บันทึกหลังออกจาก Plan mode) มีหัวข้อ "อธิบายของเดิม" (1.5) และทุกค่าคาดหวังมีป้าย [D:CR-02]/[E] · commit 2 ตัว (แดง · แก้ที่รวม REGISTER)
**ไปต่อได้เมื่อ** tests/cr02 เขียวทุกเคส · `git diff web/scripts/check-rules.mjs` ว่าง · regression ไม่มีแดงใหม่ · มีแถว CR-02 ใน TRACEABILITY และ REGISTER

---

## LAB 7 · CR-03 แก้บั๊กจากเรื่องร้องเรียน

### ส่วนที่ 1 · วิเคราะห์ (โหมดปกติ · ยังไม่แตะโค้ด)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-03.md (เรื่องร้องเรียน) ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · วางในโหมดปกติ: รันคำสั่งได้ แต่ห้ามแก้ไฟล์ใน web/ db/ e2e-legacy/ · สคริปต์และไฟล์ SQL ชั่วคราวเขียนใน tmp/ เท่านั้น)
1. ทำซ้ำเรื่องร้องเรียนก่อน: reset แล้วยิง POST /api/bookings แบบไม่ล็อกอินด้วยข้อมูลเดียวกับนัดของคุณสมชาย (เบอร์ 081-000-0003 · 13 ต.ค. 10:00 · บริการเดียวกับนัดเดิม) ด้วยสคริปต์ node (ชื่อภาษาไทยใน body) · ลองเขียนเบอร์แบบไม่มีขีดด้วย · จดสถานะและรหัสนัดที่ได้
2. แสดง "คำถามถึงร้าน" ในแชทก่อน แล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-03-ANSWERS.md · บอกข้อที่ได้คำตอบ/ยังค้าง
3. หาต้นเหตุ: ไล่การสร้างนัดตั้งแต่ API → service → DB constraint · อธิบายว่าทำไมชุดตรวจที่ส่งมอบไม่จับเรื่องนี้ และทำไมหน้าเว็บกดสองครั้งไม่ซ้ำแต่ API/แชทซ้ำได้ (อ้างไฟล์:บรรทัด)
4. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-03.md) ตาม docs/IMPACT-TEMPLATE.md · ต้องครอบ: ทุกช่องทางที่สร้างนัด (หน้าเว็บ แชท) · การกดพร้อมกัน 2 คำขอ (สมาชิก และไม่ล็อกอิน) · เทสต์เดิมที่ยิงคำขอพร้อมกันคนละคนต้องยังได้ผลเดิม · เทสต์เดิมที่จองทับนัด seed ด้วยบัญชีหรือเบอร์ของเจ้าของนัดเอง (ไล่ใน e2e-legacy/tests และ web/scripts/check-rules.mjs) → กำหนดลำดับ error เมื่อคำขอเข้าทั้ง "คิวเต็ม" และ "นัดซ้ำ" พร้อมกัน ให้เทสต์เดิมได้ผลเดิม · ข้อความ 3 ภาษา
5. ค่าที่คาดหวังใหม่อย่างน้อย 8 เคส (ซ้ำ · ต่อกันพอดี · คนละเบอร์ · สมาชิก · ยกเลิกแล้วจองใหม่ · คู่ทับเดี่ยว · พร้อมกัน · แชท) · ทุกแถวติดป้าย [D:CR-03] หรือ [E …] · ผลที่ได้จากข้อ 1 (201 ซ้ำได้) คือ [E] ที่ขัด [D:CR-03] = หลักฐานบั๊ก ห้ามนำไปเป็นค่าคาดหวัง · เสนอแผนแล้วรอผมอนุมัติ · หลังผมพิมพ์ "อนุมัติ" ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-03.md อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ไฟล์ที่จะแตะ | เหตุผล | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง
```

### ส่วนที่ 2 · ลงมือ

```text
แก้ CR-03 ตาม docs/impact/CR-03.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิมใน web/scripts/check-rules.mjs และ tests/golden/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-03.md: ถ้าแผนที่ผมอนุมัติยังอยู่ในแชทนี้ ให้บันทึกจากแผนนั้น · ถ้าไม่มี (เซสชันใหม่) ให้หยุดแล้วบอกผมให้วางส่วนที่ 1 ใหม่ ห้ามเขียนแผนเองแล้วลงมือ
1. เทสต์ที่ทำซ้ำเรื่องร้องเรียนก่อน: tests/cr03.mjs ทุกเคสจาก impact (กดพร้อมกันใช้ Promise.all 2 คำขอ) + e2e-cr/tests/cr03.spec.ts (ขั้นยืนยันในหน้าจองแสดง book-error ที่มี data-error-code="DUPLICATE_BOOKING" และรหัสนัดเดิม)
   รันบนโค้ดเดิม → ต้องแดง (เคสเรื่องร้องเรียนได้ 201) · เก็บ log ผลแดง → git add tests/cr03.mjs e2e-cr/tests/cr03.spec.ts docs/impact/CR-03.md → git commit "CR-03 test: ทำซ้ำเรื่องร้องเรียน (แดง)"
2. แก้ฝั่งเซิร์ฟเวอร์ให้เล็กที่สุด: ตรวจตอนสร้างนัด (ไม่ใช่แค่ปิดปุ่ม) · normalize เบอร์เหลือตัวเลข · กันคำขอพร้อมกันทั้งสมาชิกและไม่ล็อกอิน · ลำดับล็อกคงที่ (กัน deadlock) · ข้อความ 3 ภาษา · rebuild web
3. เขียว: node tests/cr03.mjs และ Push-Location e2e-cr; npx playwright test tests/cr03.spec.ts --project=chromium; Pop-Location (ระหว่างทำ CR รัน chromium อย่างเดียว · 3 เบราว์เซอร์รอบเต็มทำตอนส่งมอบ) · ถามแชทจองซ้ำด้วยภาษาไทยและจีนด้วยสคริปต์ node (POST /api/chat · ห้ามส่งข้อความไทย/จีนผ่าน Invoke-RestMethod · แชทต้องคุยครบ 5 ข้อความ ขอจอง → วัน → เวลา → ชื่อ+เบอร์ → ยืนยัน และส่ง state ที่ได้กลับไปทุกครั้ง) แล้วตรวจว่าคำตอบมีข้อความตามภาษาและรหัสนัดเดิม · ภาษาของ error จาก API มาจาก cookie lang ไม่ใช่ lang ใน body (เทสต์ข้อความ en/zh ของ API ต้องส่ง cookie)
4. Regression (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs (diff ว่าง) · node tests/golden/run.mjs · node tests/cr02.mjs · Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location · Push-Location e2e-legacy; npx playwright test; Pop-Location (api + chromium) · ดูให้แน่ว่าเทสต์จองพร้อมกันคนละคนยังได้ SLOT_TAKEN
5. แดงที่ไม่ได้ตั้งใจ → หยุดบอกผม (เว็บผิด / เทสต์เก่าล้าสมัย / เทสต์ใหม่เขียนผิด) ห้ามแก้เทสต์ให้ผ่าน
6. เอกสาร: web/SPEC.md (กฎใหม่ BR-21 + error ใหม่) · docs/TRACEABILITY.md แถว CR-03 → BR-21 → TC → ผล · CHANGE-REPORT.md ส่วน CR-03 (ต้นเหตุ ไฟล์:บรรทัด · ทำไมชุดเดิมไม่จับ) · อัปเดต REGISTER.md (สถานะ + hash commit แดง) → git add -A → git status → git commit "CR-03: กันจองซ้ำของคนเดียวกัน"
สรุปเป็นตาราง: เคส | ก่อนแก้ | หลังแก้ | ช่องทาง
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** ก่อนแก้: guest ส่งซ้ำได้ 201 หลายครั้ง (เคยได้ B14 B15 B16 จาก 3 ครั้ง) [รันจริง:A6 CN §7 L1] · หลังแก้ [CRD §1 คาด]: เรื่องร้องเรียน 409 `DUPLICATE_BOOKING` `existing:"B03"` · 11:30 ต่อกันพอดี 201 · เบอร์อื่น 201 · U04 14:30 → 409 · 15:00 → 201 · guest ใช้เบอร์ของ U04 → 201 · U02 เดี่ยว 20:00 ทับคู่ B02 → 409 · ยกเลิก B05 แล้วจองใหม่ (now 09:59) → 201 · พร้อมกัน `[201, 409]` ทั้งสมาชิกและ guest · แชทได้ข้อความภาษาเดียวกับที่ถาม · BOOK-06 ยัง `SLOT_TAKEN` · check-rules เท่าเดิม (ต้องยืนยันด้วยการรัน) · **กับดัก TC-BOOK-07** (U02 จองทับ B02 ของตัวเอง): ถ้าตรวจนัดซ้ำก่อนตรวจคิวเต็ม e2e-legacy แดง (ได้ "คุณมีนัดในช่วงเวลานี้อยู่แล้ว (รหัส B02)" แทน "เวลานี้ถูกจองแล้ว") → แก้ลำดับการตรวจในโค้ด ไม่แก้เทสต์ = ชุดเทสต์เดิมจับ regression ได้จริง [รันจริง:RUNNER LAB 7] · error en/zh ของ API ต้องส่ง cookie `lang` · รอบ RUNNER ใช้ข้อมูลต่างจากรายการนี้แต่หลักเดียวกัน (U01/B05 ทับบางส่วน · guest/B03 ต่อกันพอดี · guest ใช้เบอร์ U01 · U02 เดี่ยว 19:30 · ยกเลิกแล้วจองใหม่บนนัดที่สร้างเอง)
**ไปต่อได้เมื่อ** commit แดงมาก่อน commit แก้ · cr03 เขียวทั้ง API และ cr03.spec (chromium) · ไม่มี regression ใหม่ (e2e-legacy api+chromium เท่า baseline)

---

## LAB 8 · CR-04 migration วันหยุดร้าน

### ส่วนที่ 1 · วิเคราะห์ (Plan mode)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-04.md ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · Plan mode เขียนไฟล์ไม่ได้ ทุกอย่างให้อยู่ในแชทและแผน)
หนังสือบอกว่าระบบใช้งานจริงอยู่ ข้อมูลลูกค้าและนัดห้ามหาย
1. แสดง "คำถามถึงร้าน" ในแชทก่อน แล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-04-ANSWERS.md · ตัดสินว่ารอบนี้ทำส่วน ข (หลังร้าน) ไหม ให้ถามผมก่อน
2. ตอบด้วยหลักฐานจาก repo (ไฟล์:บรรทัด): ถ้าเพิ่มตารางใน db/init/01-schema.sql อย่างเดียว ฐานข้อมูลที่รันอยู่จะได้ตารางไหม เพราะอะไร · ข้อมูลทดสอบของ reset มาจากไฟล์ไหน เข้าไปใน image ตอนไหน · reset ล้างตารางอะไรบ้าง ถ้ามีตารางใหม่ต้องแก้ที่ไหน
3. ออกแบบ: ตารางใหม่ · migration ไฟล์แยก db/migrations/001_shop_holiday.sql ที่รันซ้ำได้ + 001_shop_holiday.down.sql · สิ่งที่ต้องแก้สำหรับเครื่องที่ติดตั้งใหม่ · สิ่งที่ต้องแก้ให้ reset ยังผ่าน · ทุกช่องทางที่จองได้ (หน้าเว็บ ราคา จอง คอร์ส แชท) · ลำดับ error เมื่อวันที่เกินช่วงจองและเป็นวันหยุดพร้อมกัน
4. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-04.md) ตาม docs/IMPACT-TEMPLATE.md + ค่าที่คาดหวังใหม่อย่างน้อย 8 เคส (ติดป้าย [D:CR-04] หรือ [E …] ทุกแถว) + ขั้นตอนซ้อมบนฐานที่มีข้อมูล + ลำดับ deploy (migration ก่อน rebuild เว็บ) และลำดับถอย (เว็บก่อน down.sql) พร้อมเหตุผล + วิธีถอยกลับ (ข้อมูลอะไรหายบ้างถ้าถอย)
5. เสนอแผนแล้วรอผมอนุมัติ · หลังผมอนุมัติ (ออกจาก Plan mode) ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-04.md อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ไฟล์/ตารางที่จะแตะ | เหตุผล | เทสต์ที่ต้องรันซ้ำ | ความเสี่ยง
```

### ส่วนที่ 2 · ลงมือ (ส่วน ก)

```text
ทำ CR-04 ส่วน ก ตาม docs/impact/CR-04.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้าม docker compose down -v · ห้ามลบ volume · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิม · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-04.md: ถ้าแผนที่ผมอนุมัติยังอยู่ในแชทนี้ ให้บันทึกจากแผนนั้น · ถ้าไม่มี (เซสชันใหม่) ให้หยุดแล้วบอกผมให้วางส่วนที่ 1 ใหม่ ห้ามเขียนแผนเองแล้วลงมือ
1. เทสต์ก่อน: tests/cr04.mjs (ทุกเคสใน impact) → รันบนโค้ดเดิมต้องแดง → git add tests/cr04.mjs docs/impact/CR-04.md (+ e2e-cr/tests/cr04.spec.ts ถ้าเขียนแล้ว) → git commit "CR-04 test: แดงก่อนแก้"
2. เขียน db/migrations/001_shop_holiday.sql (รันซ้ำได้: บรรทัดแรก SET client_min_messages = warning; · CREATE TABLE IF NOT EXISTS · INSERT … ON CONFLICT DO NOTHING) และ 001_shop_holiday.down.sql
3. ซ้อมบนฐานที่มีข้อมูลแบบระบบจริง (เว็บตัวเดิมยังรันอยู่):
   - สำรอง: New-Item -ItemType Directory -Force backups | Out-Null · docker exec sabai06-db pg_dump -U sabai -d sabai -f /tmp/before-cr04.sql แล้ว docker cp sabai06-db:/tmp/before-cr04.sql backups\before-cr04.sql
   - reset แล้วจองนัดใหม่ 1 นัดผ่าน API ด้วยสคริปต์ node (ไม่ล็อกอิน S01 2026-10-20 14:00) จดรหัสนัด
   - รัน migration 2 ครั้ง: docker cp db\migrations\001_shop_holiday.sql sabai06-db:/tmp/001.sql แล้ว docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001.sql (ห้าม pipe ไฟล์ผ่าน PowerShell เพราะภาษาไทยจะเพี้ยน) · ตัดสินผลจาก $LASTEXITCODE (ต้องเป็น 0) และบรรทัดผลของ psql (ครั้งแรก INSERT 0 3 · ครั้งที่ 2 INSERT 0 0) · ถ้าเห็น NOTICE "already exists, skipping" ที่ PowerShell 5.1 แสดงเป็นตัวแดง (NativeCommandError) = ข้อความแจ้ง ไม่ใช่ error
   - ตรวจ: ไม่ error ทั้ง 2 ครั้ง · นัดใหม่ยังอยู่ · SELECT count(*) FROM shop_holiday = 3 · ชื่อไทยถูกต้องตรวจด้วย SQL ไม่ใช่ด้วยตา: SELECT holiday_date, name_th = 'วันปิยมหาราช' AS th_ok FROM shop_holiday WHERE holiday_date = '2026-10-23' ต้องได้ t (ตัวอักษรไทยที่ PowerShell แสดงอาจเพี้ยนทั้งที่ข้อมูลถูก ห้ามแก้ข้อมูลเพราะเห็นบนจอ · ถ้าได้ f ให้รันคำสั่งเดียวกันจากไฟล์ .sql ด้วย docker cp + psql -f ก่อนสรุป)
4. แก้ให้เครื่องติดตั้งใหม่และ reset ใช้ได้ + โค้ดทุกช่องทาง + ข้อความ 3 ภาษา + แชท ตามแผน
5. ลำดับ deploy: migration (ข้อ 3) ต้องรันก่อน rebuild เว็บเสมอ (เว็บใหม่บน schema เก่า → reset/slots/price/bookings ตอบ 500) · เก็บ image เดิมไว้ถอยกลับ: docker tag sabai06-web:latest sabai06-web:before-cr04 · แล้ว rebuild web
6. พิสูจน์: node tests/cr04.mjs เขียว · reset 2 ครั้งติดได้ 200 ทั้งคู่ · หน้า /book เลือกวันที่ 23 ต.ค. เห็นข้อความร้านหยุด (เพิ่มเทสต์ใน e2e-cr/tests/cr04.spec.ts รัน --project=chromium) · ติดตั้งใหม่: docker run --rm -d --name sabai06-fresh -e POSTGRES_USER=sabai -e POSTGRES_PASSWORD=sabai -e POSTGRES_DB=sabai -v "${PWD}\db\init:/docker-entrypoint-initdb.d:ro" postgres:16-alpine → รอ init เสร็จก่อนตรวจ (pg_isready ผ่านได้ระหว่าง init ยังไม่จบ: วนถาม docker exec sabai06-fresh psql -U sabai -d sabai -tAc "SELECT count(*) FROM shop_holiday" ทุก 1 วินาที สูงสุด ~60 วินาที จนได้ตัวเลข) แล้วตรวจว่าได้ 3 แถว จากนั้น docker stop sabai06-fresh
7. Regression (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs (diff ว่าง) · node tests/golden/run.mjs · node tests/cr02.mjs · node tests/cr03.mjs · Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location · Push-Location e2e-legacy; npx playwright test; Pop-Location (api + chromium) · แดงที่ไม่ได้ตั้งใจ → หยุดบอกผม
8. docs/MIGRATION-RUNBOOK.md (สำรอง · คำสั่งรัน · ตรวจ ($LASTEXITCODE + INSERT 0 n) · หัวข้อ "ลำดับ": deploy = สำรอง → migration → rebuild เว็บ · ถอย = เว็บกลับ image before-cr04 ก่อน แล้วค่อย down.sql (เว็บใหม่อ่าน/TRUNCATE ตารางนี้ ถ้า down ก่อน = 500) · ข้อมูลที่จะหาย) · TRACEABILITY แถว CR-04 → BR-01/BR-03 → TC · CHANGE-REPORT ส่วน CR-04 · SPEC.md · อัปเดต REGISTER.md (สถานะ + hash commit แดง) → git add -A (backups/ ถูก exclude) → git status → git commit "CR-04: วันหยุดร้าน + migration 001"
สรุปเป็นตาราง: ขั้น | คำสั่ง | ผล | เวลา
```

### ส่วนที่ 3 · (ทางเลือก) ส่วน ข หลังร้าน

```text
ทำ CR-04 ส่วน ข: เจ้าของร้านเพิ่ม/ลบวันหยุดเองในหน้าหลังร้าน ตามที่ตกลงใน CHANGE-REQUESTS/answers/CR-04-ANSWERS.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ค่าที่คาดหวังเดิม · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. อธิบายของเดิมก่อนแก้ (ไฟล์:บรรทัด): หน้าและ API หลังร้านเดิม (AdminQueue · lib/server/admin.ts) ตรวจสิทธิ์ owner ที่ไหน · อัปเดต docs/impact/CR-04.md หัวข้อ "ส่วน ข" (ไฟล์ที่จะแตะ · เทสต์ที่ต้องรันซ้ำ · ความเสี่ยง) แล้วรอผมอนุมัติ
1. เพิ่มเคสใน tests/cr04.mjs ก่อน (เพิ่มวันที่มีนัดยืนยัน · วันว่าง · วันนี้ · อดีต · ลบ · สมาชิกเรียก · ไม่ล็อกอิน · ชื่อวันหยุดภาษาไทยส่งด้วย node แล้วอ่านกลับจาก GET /api/holidays ต้องตรงตัว) → แดง → commit
2. API + ส่วนหน้าหลังร้าน + ข้อความ 3 ภาษา → rebuild → เขียว
3. Regression ชุดเดียวกับส่วน ก · อัปเดต TRACEABILITY / CHANGE-REPORT / REGISTER · commit "CR-04b: หลังร้านจัดการวันหยุด"
แดงที่ไม่ได้ตั้งใจหรือไม่แน่ใจ ให้หยุดบอกผม ห้ามแก้เทสต์ให้ผ่าน
สรุปเป็นตาราง: เคส | ก่อนแก้ | หลังแก้
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** [CRD §1 คาด] `GET /api/holidays` 3 แถว · slots S01 23 ต.ค. → 422 `SHOP_CLOSED` มี "วันปิยมหาราช" · 22 และ 24 ต.ค. → 200 · 23 รอบ [รันจริง:A6 ค่าปกติ] · price/bookings 23 ต.ค. ทุกแบบ 422 · 5 ธ.ค. ตอนนี้ → `DATE_OUT_OF_RANGE` · ที่ now 10 พ.ย. → `SHOP_CLOSED` · migration 2 ครั้ง exit 0 (`INSERT 0 3` → `INSERT 0 0` · ครั้งที่ 2 มี NOTICE ถ้าไม่ได้ SET client_min_messages) นัดใหม่อยู่ [รันจริง:RUNNER LAB 8 · 0.28/0.27 วิ] · `th_ok = t` · reset 2 ครั้ง 200 · check-rules 90/90 (ไม่มีเคสวันหยุดทั้ง 3) [CN §6.1] · ติดตั้งใหม่มีตาราง (รอ init ~6 วิ) · กับดักที่ควรเห็นถ้าพลาด: ลืมรายชื่อตารางที่ reset ล้าง → reset 500 · rebuild เว็บก่อน migrate → slots/price/bookings/reset 500 [รันจริง:RUNNER LAB 8 ทดสอบลำดับกลับแล้ว] · ส่วน ข: 14 ต.ค. → 409 `HAS_BOOKINGS` · 15 ต.ค. → 201 แล้ว slots 422
**ไปต่อได้เมื่อ** migration รัน 2 ครั้งบนฐานที่มีนัดใหม่ผ่าน · reset ผ่าน 2 ครั้ง · cr04 เขียว · มี MIGRATION-RUNBOOK + `backups/before-cr04.sql` (ไม่ commit) + image `sabai06-web:before-cr04`

---

## LAB 9 · CR-01 ฟีเจอร์ใหม่ เลื่อนนัด

### ส่วนที่ 1 · วิเคราะห์ + แตกงาน (Plan mode)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-01.md (ฟีเจอร์ใหม่ ใหญ่ที่สุด) ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · Plan mode เขียนไฟล์ไม่ได้ ทุกอย่างให้อยู่ในแชทและแผน)
1. แสดง "คำถามถึงร้าน" ในแชทก่อน แล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-01-ANSWERS.md · บอกข้อที่ได้คำตอบ/ยังค้าง
2. อธิบายด้วยหลักฐาน (ไฟล์:บรรทัด): เวลาของนัดเก็บที่ตารางไหนบ้าง คอลัมน์ไหนคำนวณเอง คอลัมน์ไหนต้องอัปเดตเอง · กฎห้ามซ้อนของนักบำบัดและห้องอยู่ที่ไหน (โค้ดและ DB) · ถ้าเลื่อนไปเวลาที่ทับเวลาเดิมของนัดตัวเองจะชนอะไร
3. ทำไมใช้ /api/slots เดิมหาเวลาว่างให้การเลื่อนไม่ได้ · ทำไม "ยกเลิกแล้วจองใหม่" ข้างในโค้ดอาจทำให้คอร์สหรือสิทธิ์เดือนเกิดเพี้ยน
4. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-01.md) ตาม docs/IMPACT-TEMPLATE.md · แตกงาน 3 ขั้น: ขั้น A API เลื่อนนัด · ขั้น B รอบที่เลื่อนได้ (เฉพาะนักบำบัด/ห้องเดิม ไม่นับนัดตัวเอง) · ขั้น C หน้า /account
5. ค่าที่คาดหวังอย่างน้อย 12 เคส ครอบ: ขอบ 24 ชม. · ช่วงวัน +30/+31 · รอบสุดท้าย · เวลาเดิม · คนเดิมไม่ว่าง · ทับเวลาเดิมของตัวเอง (นัดคู่) · สิทธิ์ (คนอื่น/ไม่ล็อกอิน/owner) · นัดที่ใช้บริการแล้ว · เดือนเกิด · คอร์สหมดอายุ · ราคาและแต้มไม่เปลี่ยน · รอบเดิมว่างให้คนอื่น · ทุกแถวติดป้าย [D:CR-01] (คำตอบร้าน) หรือ [E …] (ค่าเดิมที่ต้องคงไว้ เช่น ยอด/แต้มของนัดก่อนเลื่อน)
6. เสนอแผนทีละขั้น แล้วรอผมอนุมัติ · หลังผมอนุมัติ (ออกจาก Plan mode) ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-01.md อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ขั้น | ไฟล์ที่จะแตะ | เทสต์ที่พิสูจน์ | ความเสี่ยง
```

### ส่วนที่ 2 · ขั้น A + B (API)

```text
ทำ CR-01 ขั้น A และ B ตาม docs/impact/CR-01.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิม · ยังไม่ทำหน้าเว็บ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-01.md: ถ้าแผนที่ผมอนุมัติยังอยู่ในแชทนี้ ให้บันทึกจากแผนนั้น · ถ้าไม่มี (เซสชันใหม่) ให้หยุดแล้วบอกผมให้วางส่วนที่ 1 ใหม่ ห้ามเขียนแผนเองแล้วลงมือ
1. เทสต์ก่อน: tests/cr01.mjs ทุกเคส API จาก impact (reset {now} คุมเวลา) → รันบนโค้ดเดิมต้องแดง (endpoint ยังไม่มี) → git add tests/cr01.mjs docs/impact/CR-01.md → git commit "CR-01 test: แดงก่อนแก้"
2. ขั้น A: POST /api/bookings/:id/reschedule ตามที่ตกลง · อัปเดตเวลาทุกตารางที่เก็บเวลา ใน transaction เดียว · ไม่คิดราคา/แต้ม/บัตร/คอร์สใหม่ · error ใหม่ครบ 3 ภาษา · rebuild → รันเฉพาะเคสขั้น A
3. ขั้น B: GET /api/bookings/:id/reschedule-slots?date= · ใช้กฎรอบเวลาเดิม แต่ตรวจเฉพาะนักบำบัด (และห้อง) เดิม และไม่นับนัดตัวเอง · rebuild → node tests/cr01.mjs ต้องเขียวทุกเคส (ถ้าเขียน A และ B เสร็จพร้อมกัน rebuild ครั้งเดียวได้ แต่รันเคสขั้น A ให้เขียวก่อน แล้วจึงรันทั้งหมด)
4. Regression ระหว่างทาง (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs (diff ว่าง) · node tests/golden/run.mjs · node tests/cr02.mjs · node tests/cr03.mjs · node tests/cr04.mjs
5. แดงที่ไม่ได้ตั้งใจ → หยุดบอกผม ห้ามแก้เทสต์ให้ผ่าน · อัปเดต REGISTER.md (ขั้น A+B เสร็จ) → git add -A → git status → git commit "CR-01 A+B: API เลื่อนนัด"
สรุปเป็นตาราง: เคส | ก่อนแก้ | หลังแก้
```

### ส่วนที่ 3 · ขั้น C (หน้าเว็บ) + regression เต็ม

```text
ทำ CR-01 ขั้น C หน้า /account ตาม testid ใน CHANGE-REQUESTS/answers/CR-01-ANSWERS.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิม · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
1. เทสต์ก่อน: e2e-cr/tests/cr01.spec.ts = คุณนิดา (nida@sabai.test) เลื่อนนัด B05 ไป 12 ต.ค. 10:00 ผ่านหน้าเว็บ → รีโหลดแล้วเห็นเวลาใหม่ · ปุ่มเลื่อนของนัดวันนี้ (B06) กดไม่ได้ → รันต้องแดง → git add e2e-cr/tests/cr01.spec.ts → git commit -m "CR-01 C test: แดงก่อนแก้"
2. ทำปุ่ม กล่องเลือกวัน รอบ ยืนยัน ข้อความสำเร็จ/ผิดพลาด 3 ภาษา · rebuild → cr01.spec.ts เขียวทั้ง chromium firefox webkit
3. Regression เต็ม (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs · node tests/golden/run.mjs · node tests/cr01.mjs ถึง cr04.mjs · Push-Location e2e-cr; npx playwright test; Pop-Location (3 เบราว์เซอร์) · Push-Location e2e-legacy; $env:PLAYWRIGHT_JSON_OUTPUT_NAME="test-report\legacy-all.json"; npx playwright test --project=api --project=chromium --project=firefox --project=webkit --reporter=list,json; Pop-Location (= npm run test:all + ไฟล์ JSON · 3 เบราว์เซอร์ ~13 นาที → รันแบบ background แล้วรอผล)
   แยก passed / expected-fail / failed ต่อ project จาก JSON ด้วยสคริปต์ node (tests[].status = expected และ expectedStatus = failed คือ expected-fail · status = unexpected คือ failed · flaky แยกไว้) · e2e-cr ก็แยกแบบเดียวกัน (บรรทัดสรุปนับ test.fail รวมใน passed)
   ข้อที่ล้มแต่ไม่เกี่ยวกับไฟล์ที่ CR แตะ (เช่น TC-UI-02 หน้า /skin บน webkit) ให้รันซ้ำเฉพาะข้อ (--project=webkit -g TC-UI-02 --repeat-each=3) · ถ้ายังผ่านบ้างล้มบ้าง ให้พิสูจน์บน image เดิม sabai06-web:before-cr04 (container ชั่วคราว sabai06-old พอร์ต 4001 ต่อ sabai06-net env เดียวกับ web/compose.yaml แล้วรันข้อนั้นด้วย BASE_URL พอร์ตนั้น · เสร็จแล้ว docker stop) ว่าล้มแบบเดียวกัน = flaky เดิม ไม่ใช่ regression · ห้ามแก้เทสต์
4. เอกสาร: web/SPEC.md (API และหน้าใหม่) · TRACEABILITY แถว CR-01 → BR-01/02/03/04/07/13/14 (+ กฎใหม่ "เลื่อนนัดเอง") → TC · CHANGE-REPORT ส่วน CR-01 · อัปเดต REGISTER.md → git add -A → git status → git commit "CR-01 C: หน้าเลื่อนนัด" · แดงที่ไม่ได้ตั้งใจหรือไม่แน่ใจ → หยุดบอกผม
สรุปเป็นตาราง: ชุดทดสอบ | chromium | firefox | webkit | หมายเหตุ
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** [CRD §1 คาด] B05 → 12 ต.ค. 10:00 = 200 `total` 760 · ทำตอน 10:01 → 422 `RESCHEDULE_TOO_LATE` · B06 → 422 · B02 19:00 → 19:30 = **200** (ไม่นับชนตัวเอง) · B01 → 14 ต.ค. 16:00 = 409 (T03 ติด B04) · reschedule-slots ของ B01 วันที่ 14 ต.ค. ไม่มี 16:00 ขณะ `/api/slots` มี · 9 พ.ย. 200 / 10 พ.ย. 422 · 21:00 200 / 21:30 422 · เวลาเดิม 422 `RESCHEDULE_SAME` · คนอื่น 403 · ไม่ล็อกอิน 401 · owner 403 · B07 422 `RESCHEDULE_NOT_ALLOWED` · เดือนเกิด 31 ต.ค. → 1 พ.ย. 422 · คอร์ส C02 19 → 21 ต.ค. 422 และ `reserved` = 1 · แต้มไม่เปลี่ยน · UI ผ่าน 3 เบราว์เซอร์ · e2e-legacy `test:all` = 114 รายการ "113 passed · 1 failed" (expected-fail 7 · failed TC-SEC-05) เท่า baseline [รันจริง:PREP V5b] · รอบ RUNNER ได้ "112 passed · 2 failed" = เพิ่ม TC-UI-02 webkit (`/skin`) ซึ่ง flaky มาก่อน CR: `--repeat-each=3` image ปัจจุบันล้ม 2/3 · image `before-cr04` ล้ม 1/3 → ไม่ใช่ regression ของ CR-01 [รันจริง:RUNNER LAB 9] · commit 4–5 ตัว
**ไปต่อได้เมื่อ** cr01 API เขียวทุกเคส · cr01.spec.ts เขียว 3 เบราว์เซอร์ · regression ไม่มีแดงใหม่

---

## LAB 10 · CR-05 รายงาน + CSV

### ส่วนที่ 1 · วิเคราะห์ + ค่าคาดหวังจาก SQL (โหมดปกติ · ยังไม่แตะโค้ด)

```text
วิเคราะห์ CHANGE-REQUESTS/CR-05.md ก่อนแก้ (รันคำสั่งด้วย PowerShell · ยังห้ามแก้โค้ด · อ่าน CLAUDE.md และ SYSTEM-MAP.md ก่อน · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · วางในโหมดปกติ: รันคำสั่งได้ แต่ห้ามแก้ไฟล์ใน web/ db/ e2e-legacy/ · สคริปต์และไฟล์ SQL ชั่วคราวเขียนใน tmp/ เท่านั้น)
1. แสดง "คำถามถึงร้าน" ในแชทก่อน แล้วค่อยเปิด CHANGE-REQUESTS/answers/CR-05-ANSWERS.md · บอกข้อที่ได้คำตอบ/ยังค้าง
1.5 อธิบายของเดิมที่จะต่อยอด (อ้างไฟล์:บรรทัด): หน้าและ API หลังร้านเดิม (lib/server/admin.ts · component ตารางคิว AdminQueue · เมนู NavMenu) · ตรวจสิทธิ์ owner ที่ไหนและอย่างไร · เงินเก็บเป็นหน่วยอะไรในโค้ดและแปลงจาก NUMERIC ที่ไหน · ส่วนไหนใช้ซ้ำได้ ส่วนไหนต้องเขียนใหม่
2. ค่าที่คาดหวังต้องมาจากทางอื่น ไม่ใช่จากหน้ารายงานที่กำลังจะสร้าง: reset แล้วเขียน SQL ตรงกับตาราง booking / booking_slot / point_txn ฯลฯ (นับตามวันนัดเวลาไทย) สำหรับช่วง 2026-09-01 ถึง 2026-09-30 · 2026-10-01 ถึง 2026-10-31 · 2026-10-06 ถึง 2026-10-09
   รัน SQL จากไฟล์ตามกฎ CLAUDE.md (ไม่ใช้ psql -c "<SQL>" ใน PowerShell): เขียนคิวรีลงไฟล์ .sql ใน tmp/ → docker cp <ไฟล์> sabai06-db:/tmp/q.sql → docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/q.sql · ตรวจ $LASTEXITCODE = 0
   ทุกตัวเลขในรายงาน (จำนวนแยกสถานะ · ยอดขาย · บัตรของขวัญ · ช่องทางอื่น · ค่ารถ · ส่วนลด 3 แบบ · แต้ม · ครั้งคอร์ส · ยอดนัดที่ยังไม่มา · คิวต่อนักบำบัด) ต้องมี SQL และผลจริง · ป้าย: นิยามตัวเลขมาจาก [D:CR-05] · ค่ามาจาก [E sql:<ชื่อคิวรี>] · ถ้าค่าจาก SQL ไม่ตรงตัวอย่างในคำตอบร้าน = หยุดถามผม (ห้ามปรับ SQL ให้ตรง)
   โซนเวลา: นับด้วย SQL ว่าข้อมูลตั้งต้นมีนัดที่วันตามเวลา UTC ≠ วันตามเวลาไทยกี่นัด · ถ้าเป็น 0 ให้เขียนใน impact ว่า "ข้อมูลตั้งต้นพิสูจน์เรื่องโซนเวลาไม่ได้" (ข้อจำกัด) และเสนอว่าจะพิสูจน์ทางอื่นอย่างไร
3. เนื้อหา impact (จะบันทึกเป็น docs/impact/CR-05.md) ตาม docs/IMPACT-TEMPLATE.md + SQL ทั้งหมดพร้อมผล + เคสขอบ (92/93 วัน · from > to · สิทธิ์) + เรื่องโซนเวลาและหน่วยเงิน
4. เสนอแผนแล้วรอผมอนุมัติ · หลังผมพิมพ์ "อนุมัติ" ให้บันทึกเนื้อหา impact ทั้งหมดเป็น docs/impact/CR-05.md (รวม SQL และผล) อย่างเดียวแล้วหยุด รอพรอมต์ถัดไป
สรุปเป็นตาราง: ช่วงวัน | ตัวเลข | ค่าจาก SQL | SQL ที่ใช้ (ย่อ)
```

### ส่วนที่ 2 · ลงมือ

```text
ทำ CR-05 ตาม docs/impact/CR-05.md (รันคำสั่งด้วย PowerShell · อ่าน CLAUDE.md ก่อน · ห้ามแก้ e2e-legacy/ · ห้ามแก้ค่าที่คาดหวังเดิม · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. ถ้ายังไม่มี docs/impact/CR-05.md: ถ้าแผนที่ผมอนุมัติยังอยู่ในแชทนี้ ให้บันทึกจากแผนนั้น · ถ้าไม่มี (เซสชันใหม่) ให้หยุดแล้วบอกผมให้วางส่วนที่ 1 ใหม่ ห้ามเขียนแผนเองแล้วลงมือ
1. เทสต์ก่อน: tests/cr05.mjs ใช้ค่าจาก SQL ใน impact เป็นค่าที่คาดหวัง (ห้ามรันหน้ารายงานแล้วลอกค่า) + เคส CSV (หัวคอลัมน์ · จำนวนแถว · ขึ้นต้นด้วย BOM) + สิทธิ์ → แดง (เคสที่ล็อกว่า "ไม่รั่ว" เช่นแชทไม่ตอบยอดขาย อาจผ่านตั้งแต่ก่อนแก้ = ปกติ ไม่ต้องทำให้แดง) → git add tests/cr05.mjs docs/impact/CR-05.md → git commit "CR-05 test: แดงก่อนแก้"
2. API + หน้า /admin/report + ลิงก์เมนู + CSV + ข้อความ 3 ภาษา · rebuild → node tests/cr05.mjs เขียว
3. e2e-cr/tests/cr05.spec.ts: owner เปิดหน้า เลือกช่วง ก.ย. กดดู ยอดตรงกับ SQL · กดโหลด CSV แล้วตรวจไฟล์ที่ดาวน์โหลดใน test ด้วย Node (3 ไบต์แรก EF BB BF + ชื่อบริการภาษาไทยตรงตัว · ไม่ตัดสินจากหน้าจอ PowerShell) · รันเฉพาะไฟล์นี้ 3 เบราว์เซอร์: Push-Location e2e-cr; npx playwright test tests/cr05.spec.ts --project=chromium --project=firefox --project=webkit --reporter=list,json; Pop-Location (การดาวน์โหลดไฟล์ต่างกันตามเบราว์เซอร์)
4. ตรวจเพิ่ม: ยอดขายในรายงาน = ผลรวมยอดในตารางคิวหลังร้านของนัดที่ใช้บริการแล้วทุกวันในช่วง · ถ้าเทสต์ต้อง "กดใช้บริการเสร็จ" นัดใด ให้ตั้งเวลาระบบ (reset {now} หรือ /api/test/clock) ให้ถึงเวลานัดนั้นก่อนกด
5. Regression (จากโฟลเดอร์บท): node web/scripts/check-rules.mjs · node tests/golden/run.mjs · node tests/cr01.mjs ถึง cr05.mjs · Push-Location e2e-cr; npx playwright test --project=chromium; Pop-Location · Push-Location e2e-legacy; npx playwright test; Pop-Location (api + chromium) · แดงที่ไม่ได้ตั้งใจ → หยุดบอกผม
6. เอกสาร: web/SPEC.md (API และหน้าใหม่) · TRACEABILITY แถว CR-05 · CHANGE-REPORT ส่วน CR-05 · อัปเดต REGISTER.md (สถานะ + hash commit แดง) → git add -A → git status → git commit "CR-05: รายงานยอด + CSV"
สรุปเป็นตาราง: ช่วงวัน | ตัวเลข | SQL | API | หน้าเว็บ | ตรงไหม
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** [รันจริง:A6 SQL บน seed CN §2 · CRD §1] ก.ย.: completed 3 · cancelled 1 · confirmed 0 · revenue 1,900 · otherPaid 1,900 · tier 100 · แต้ม 19 · ครั้งคอร์ส 2 · T01 1 T03 1 T05 1 · ต.ค.: completed 1 · confirmed 6 · revenue 1,440 · birthday 360 · แต้ม 14 · pending 11,130 · 6–9 ต.ค. ทุกค่า 0 · 92 วัน 200 / 93 วัน 422 · CSV ก.ย. 4 แถว (B10 B11 B12 B13) มี BOM · U01 403 · ไม่ล็อกอิน 401 · รอบ RUNNER (ตาบอด) ตรงทุกค่า · cr05 แดง 11/12 (เคสแชท "ไม่รั่ว" ผ่านก่อนแก้) → เขียว 12/12 · seed ไม่มีนัดที่วัน UTC ≠ วันไทย → จดเป็นข้อจำกัด [รันจริง:RUNNER LAB 10]
**ไปต่อได้เมื่อ** ค่าคาดหวังทุกตัวมี SQL + ผลจริงใน impact ก่อน commit แก้ · cr05 เขียว · CSV เปิดแล้วภาษาไทยไม่เพี้ยน

---

## LAB 11 · Regression เต็ม + REA เทียบเวอร์ชัน

```text
พิสูจน์ว่าทุก CR "ทำตามที่ขอ" และ "ของเดิมไม่พัง" แล้วเขียน REGRESSION-REPORT.md (รันคำสั่งด้วย PowerShell จากโฟลเดอร์บท · ห้ามแก้โค้ด · ห้ามแก้เทสต์ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
ลำดับ: ข้อ 2 (REA static ใช้ CPU หนัก) ห้ามรันขนานกับ e2e 3 เบราว์เซอร์ · ข้อ 2b/2c (reset ข้อมูล) ทำหลัง regression ข้อ 1 เสร็จ
1. reset แล้วรันทุกชุดบนโค้ดล่าสุด จดผ่าน/ทั้งหมด/เวลา: node web/scripts/check-rules.mjs · node tests/golden/run.mjs · node tests/cr01.mjs ถึง cr05.mjs · Push-Location e2e-cr; $env:PLAYWRIGHT_JSON_OUTPUT_NAME="test-results\cr-all.json"; npx playwright test --reporter=list,json; Pop-Location (3 เบราว์เซอร์) · Push-Location e2e-legacy; $env:PLAYWRIGHT_JSON_OUTPUT_NAME="test-report\legacy-all.json"; npx playwright test --project=api --project=chromium --project=firefox --project=webkit --reporter=list,json; Pop-Location (= npm run test:all + ไฟล์ JSON · 3 เบราว์เซอร์ ~13 นาที → รันแบบ background แล้วรอผล)
   แยก passed / expected-fail / failed ต่อ project จาก JSON ด้วยสคริปต์ node (status = expected และ expectedStatus = failed คือ expected-fail · status = unexpected คือ failed · flaky แยกไว้) เพราะบรรทัดสรุปนับ expected-fail รวมใน passed
   เทียบกับ HANDOVER-CHECK.md: ข้อที่ล้มตั้งแต่รับมอบ (เช่น TC-SEC-05) ไม่ใช่แดงใหม่ · ข้อที่ล้มแต่ไม่เกี่ยวกับไฟล์ที่ CR แตะ (เช่น TC-UI-02 /skin บน webkit) ให้รันซ้ำเฉพาะข้อ --repeat-each=3 ก่อนสรุป
2. REA เทียบของที่ส่งมอบ (bundle) ก่อน/หลัง: ใช้ rea-out\v1 เดิมเป็นฝั่งซ้าย
   - ถ้า rea-out\v2\.next\static มีอยู่แล้ว ให้บอกผมก่อนลบแล้วคัดลอกใหม่
   - New-Item -ItemType Directory -Force rea-out\v2\.next | Out-Null; docker cp sabai06-web:/app/.next/static rea-out\v2\.next\static
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\static-v2.json analyze-javascript-application /work/rea-out/v2/.next/static --json 2> rea-out\static-v2.log
   - node tools\rea-tools.mjs pages rea-out\static-v1.json rea-out\static-v2.json (หน้าไหนไฟล์เปลี่ยน/ใหม่ จาก hash ในชื่อไฟล์ · hash ต่าง = ไฟล์ใน bundle เปลี่ยน แต่ไม่บอกว่าเปลี่ยนตรงไหน)
   - node tools\rea-tools.mjs cmp-input rea-out\static-v1.json rea-out\static-v2.json rea-out\cmp.json
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\cmp-out.json compare-application-versions /work/rea-out/cmp.json --json 2> rea-out\cmp-out.log
   - node tools\rea-tools.mjs cmp-sum rea-out\cmp-out.json (หน้าใหม่ใน v2 มักขึ้นเป็น unknown ไม่ใช่ added เพราะ REA นับ added เฉพาะเมื่อ coverage ครบ · added 0 ≠ ไม่มีหน้าใหม่)
   - node tools\rea-tools.mjs endpoints rea-out\static-v1.json แล้ว node tools\rea-tools.mjs endpoints rea-out\static-v2.json → เทียบรายชื่อไฟล์ route API (route ใหม่ที่ compare ไม่บอก)
2b. REA ดูสัญญา API ของเส้นทางเดิมหลังแก้ (HAR ชุดเดียวกับตอนรับมอบ · ต้องใช้ 127.0.0.1):
   - ⚠️ record-har.mjs reset ข้อมูลก่อนเดิน แล้วจองนัดใหม่ (รอบรับมอบได้ B14) และยกเลิก B05 → ข้อมูลในระบบเปลี่ยน ถ้างานถัดไปต้องการข้อมูลตั้งต้นให้ reset ใหม่ (POST /api/test/reset)
   - node tools\record-har.mjs http://127.0.0.1:4000 rea-out\journeys-v2.har
   - node tools\rea-tools.mjs har-records rea-out\journeys-v2.har
   - powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out rea-out\har-api-v2.json inspect-web-network-capture /work/rea-out/journeys-v2.har har <วาง --record ทั้งหมดที่ได้> --sensitive-value Nida@2026 --sensitive-value Owner@2026 --json 2> rea-out\har-api-v2.log
   - node tools\rea-tools.mjs har-api rea-out\har-api-v2.json แล้วเทียบกับ node tools\rea-tools.mjs har-api rea-out\har-api.json (ของตอนรับมอบ) → ตาราง endpoint | v1 (status · คีย์) [E ev_…] | v2 [E ev_…] | เหมือนเดิม/เปลี่ยน | CR ที่อนุญาตให้เปลี่ยน (ป้าย [E] ได้จาก node tools\rea-tools.mjs ids rea-out)
2c. REA ขับหน้าจองเดิมซ้ำบนโค้ดใหม่: powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Network sabai06-net -Out rea-out\scenario-v2.json capture-browser-scenario /work/tools/scenario-book-quote.json --json 2> rea-out\scenario-v2.log · node tools\rea-tools.mjs scenario-sum rea-out\scenario-v2.json · node tools\rea-tools.mjs shot rea-out\scenario-v2.json rea-out\scenario-v2-final.png · เทียบจำนวน step และยอดหน้าสรุป (จาก scenario-sum) กับ docs/REA-INVENTORY.md (ยอดเดิมคือ [E] ของตอนรับมอบ · ต่างได้เฉพาะเมื่อมี CR อนุญาต)
3. ตาราง: CR | ส่วนที่ควรเปลี่ยนใน bundle (หน้าไหน) | REA static เห็นไหม (changed / unknown / ไม่เห็น) | HAR/scenario เห็นไหม | ถ้าไม่เห็นเพราะอะไร | เทสต์ไหนพิสูจน์แทน · อ่านเฉพาะ changed ที่เป็นโค้ดหน้าเว็บ (chunks/app/...) ส่วน unknown ห้ามสรุปว่าไม่เปลี่ยน · "REA ไม่เห็น" ≠ "ไม่ได้เปลี่ยน"
4. หา commit baseline: git log --oneline --grep "baseline: ระบบที่รับมอบ" (ถ้าไม่เจอใช้ commit id ใน HANDOVER-CHECK.md) · git diff --stat <baseline>..HEAD → ทุกไฟล์ที่เปลี่ยนต้องโยงกับ CR ได้ (ตาราง ไฟล์ | CR) ไฟล์ที่โยงไม่ได้ติด ⚠️ พร้อมเหตุผล (เช่น เครื่องมือ/เอกสารของทีม ไม่อยู่ในระบบที่ส่งมอบ)
5. ค่าที่คาดหวังเดิม: git diff <baseline>..HEAD -- web/scripts/check-rules.mjs e2e-legacy ต้องว่าง หรือทุกจุดมีแถวใน docs/ORACLE-CHANGES.md · tests/golden สร้างหลัง baseline → หา commit ที่สร้าง (git log --diff-filter=A --oneline -- tests/golden) แล้ว git diff <commit นั้น>..HEAD -- tests/golden ต้องว่าง
6. docs/TRACEABILITY.md ฉบับสมบูรณ์: ทุก CR มี BR และ TC ที่ผ่าน · ทุก TC ใหม่มี CR
ตัวเลขทุกตัวต้องมาจากการรันรอบนี้ · แดงใหม่ที่ baseline ไม่มีให้หยุดแล้วบอกผม ห้ามแก้ให้ผ่าน
สรุปเป็นตาราง: ชุด | ผ่าน/ทั้งหมด | เบราว์เซอร์ | เวลา | หมายเหตุ
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** `REGRESSION-REPORT.md` · ทุกชุดใหม่เขียว · e2e-legacy `test:all` = **114 รายการ** (api 6 + UI 36 × 3): บรรทัดสรุป Playwright **"113 passed · 1 failed"** = ผ่านจริง 106 · expected-fail 7 (TC-TRN-03 ×3 · TC-GC-04 ×3 · TC-SEC-04 ×1) · failed 1 (TC-SEC-05 · project `api` รันครั้งเดียว) = เท่า baseline [คาด · ยืนยันด้วย PREP V5b] · REA static: `changed` ที่ `chunks/app/account/page` (CR-01) และหน้าใหม่ของรายงาน (CR-05 · อาจเป็น `unknown` ไม่ใช่ `added` ถ้า coverage partial) · CR-02 CR-03 (กฎฝั่งเซิร์ฟเวอร์) ไม่เห็น · `unknown` หลายร้อย [อิงรูปแบบจริง RF §2.7 v1→v2/v3 · ค่าจริงรอรอบ RUNNER] · HAR v2: endpoint ชุดเดิม 7 ตัว status เดิม (เส้นทางใน `record-har.mjs` ไม่ชน CR: จองคนละเบอร์ · 12 ต.ค. ไม่ใช่วันหยุด · ไม่เปิดกล่องเลื่อนนัด) · อาจมี endpoint เพิ่มถ้าหน้าจองเรียก `/api/holidays` [คาด] → ใช้เป็นหลักฐาน [E] ว่า "สัญญา API เส้นทางเดิมไม่เปลี่ยน" · scenario v2: 12/12 step ยอด ฿1,000 เท่าเดิม (นัดเดี่ยว ไม่โดน CR-02) [คาด] · `pages` v1↔v2: `/account` "ไฟล์เปลี่ยน" (CR-01) · หน้าใหม่ของ CR-05 "ใหม่ใน v2" [คาด · FIX6T ทดสอบ logic ด้วย v2 จำลองเท่านั้น] · ไฟล์ทุกไฟล์โยง CR ได้ · diff ค่าคาดหวังเดิมว่าง · รอบ RUNNER: test:all ตรงทุกตัว (106 · ef 7 · failed TC-SEC-05 · 12.8 นาที) · e2e-cr 39 = 33 + ef 6 · compare `changed 12 · unknown 711 · added 0` · `/admin/report` = unknown · route ไฟล์ 25 → 30 · CR-02 ไม่เห็นเลย · CR-03/04 เห็นทางอ้อมผ่าน chunk i18n · HAR v2 7 endpoint เท่า v1 (ไม่มี `/api/holidays`) · scenario v2 12/12 ฿1,000 · ⚠️ ไฟล์เครื่องมือคอร์สใน diff อธิบายได้ [รันจริง:RUNNER LAB 11]
**ไปต่อได้เมื่อ** ตัวเลขทุกชุดในรายงานมาจากรอบนี้ · ตาราง CR × REA ครบ 5 แถว (static + HAR/scenario) · ตาราง HAR v1↔v2 ติดป้าย [E] ครบ · ไม่มีไฟล์ ⚠️ ที่อธิบายไม่ได้

---

## LAB 12 · ส่งมอบ + ซ้อมถอยกลับ

### ส่วนที่ 1 · ซ้อมถอยกลับ + runbook

```text
ซ้อมถอยกลับ migration บนฐานที่มีข้อมูลจริง เขียน smoke test ให้ทีมใช้วันขึ้นระบบ แล้วเขียน docs/DEPLOY-RUNBOOK.md (รันคำสั่งด้วย PowerShell จากโฟลเดอร์บท · ห้าม docker compose down -v · ห้ามลบ volume · ห้ามแก้โค้ดระบบใน web/ db/ · ห้ามเปิด README.md ของบท fast_track/ และ _solution/)
0. เขียน tests/smoke.mjs (Node ≥ 22.18 ไม่ใช้ dependency · BASE_URL ค่าเริ่ม http://localhost:4000) = ตรวจหลังขึ้นระบบจริงแบบ **อ่านอย่างเดียว** (ห้าม reset · ห้ามสร้างหรือแก้ข้อมูล): health db:true · /api/services ตอบ 200 · /api/holidays มีวันหยุดที่ร้านแจ้ง · หน้า /book ตอบ 200 · API ใหม่ของ CR-01 และ CR-05 เมื่อไม่ล็อกอินต้องตอบ 401 (ไม่ใช่ 404 = มี endpoint จริง · POST แบบไม่ล็อกอินที่ถูกปฏิเสธก่อนแตะข้อมูลนับเป็นอ่านอย่างเดียว) · พิมพ์ตาราง ข้อ | ผล แล้ว exit 0 เมื่อผ่านทุกข้อ ไม่งั้น exit 1 · รันตอนนี้ต้อง exit 0
1. สำรอง: New-Item -ItemType Directory -Force backups | Out-Null · docker exec sabai06-db pg_dump -U sabai -d sabai -f /tmp/before-rollback.sql แล้ว docker cp sabai06-db:/tmp/before-rollback.sql backups\before-rollback.sql
2. reset แล้วจองนัดใหม่ 1 นัดผ่าน API ด้วยสคริปต์ node (ไม่ล็อกอิน S05 2026-10-21 11:00) จดรหัสนัด
3. หยุดเว็บชั่วคราว: docker compose -f web/compose.yaml stop → node tests/smoke.mjs ต้อง exit 1 (พิสูจน์ว่า smoke จับระบบล่มได้)
4. ถอย DB: docker cp db\migrations\001_shop_holiday.down.sql sabai06-db:/tmp/001down.sql แล้ว docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001down.sql → ตรวจว่าตารางวันหยุดหายและนัดใหม่ยังอยู่
4b. ถอยเว็บ (ซ้อมสลับ image): เปิด image เดิม sabai06-web:before-cr04 เป็น container ชั่วคราว sabai06-old พอร์ต 4001 ต่อ sabai06-net env เดียวกับ web/compose.yaml → /api/health db:true · /book 200 · /api/holidays 404 (= เว็บรุ่นก่อน CR-04 ทำงานได้บนฐานที่ถอยแล้ว) · จดเวลา → docker stop sabai06-old
5. ไปข้างหน้าอีกครั้ง: รัน 001_shop_holiday.sql ด้วยวิธีเดียวกับข้อ 4 → วันหยุดกลับมา 3 แถว · นัดใหม่ยังอยู่
6. เปิดเว็บ: docker compose -f web/compose.yaml start → health db:true → node tests/smoke.mjs exit 0 → จดหลักฐานนัดใหม่ (รหัส · สถานะ) ให้ครบก่อน แล้วค่อย node tests/cr04.mjs เขียว (cr04 reset ข้อมูลทุกเคส นัดใหม่จะหายเพราะ reset ไม่ใช่เพราะถอย)
7. docs/DEPLOY-RUNBOOK.md ลำดับวันขึ้นระบบจริง: สำรอง → tag image เดิม → รัน migration → build/up เว็บ → node tests/smoke.mjs (ผลที่ต้องเห็น) → เงื่อนไขที่ต้องถอย → ขั้นถอย (เว็บกลับ image เดิมก่อน แล้วค่อย down.sql) · ใส่เวลาที่วัดได้จริงจากการซ้อม และข้อมูลที่จะหายถ้าถอย
8. เพิ่มแถว smoke ใน docs/TRACEABILITY.md (โยงทุก CR) → git add tests/smoke.mjs docs/DEPLOY-RUNBOOK.md docs/TRACEABILITY.md → git status → git commit "release: smoke test + deploy runbook" (ไฟล์อื่นที่ค้างจากงานก่อนเข้า commit ของส่วนที่ 2)
ทุกขั้นจดคำสั่งและผลจริง ขั้นไหนไม่ผ่านให้หยุดบอกผม
สรุปเป็นตาราง: ขั้น | คำสั่ง | ผล | เวลา
```

### ส่วนที่ 2 · เอกสารส่งมอบ

```text
เขียนเอกสารส่งมอบให้คุณจันทร์และคณะกรรมการตรวจรับ (รันคำสั่งด้วย PowerShell · ห้ามแก้โค้ด · ห้ามเปิด README.md ของบท fast_track/ และ _solution/ · อ่าน CHANGE-REPORT.md, REGRESSION-REPORT.md, docs/TRACEABILITY.md, KNOWN-ISSUES.md, docs/SPEC-GAPS.md ก่อน)
1. RELEASE-NOTES.md ภาษาคน ไม่มีศัพท์โปรแกรม: ต่อ CR บอก อะไรเปลี่ยน · ลูกค้าเห็นอะไร · ร้านต้องทำอะไร · มีผลเมื่อไร · หัวข้อ "เรื่องที่ยังไม่ได้แก้" (จาก KNOWN-ISSUES.md และสิ่งที่เจอระหว่างทางแต่ไม่อยู่ใน CR) พร้อมผลกระทบและข้อเสนอ
2. UAT-CHECKLIST.md: ต่อ CR 3–6 ขั้นที่ร้านกดเองได้บนหน้าเว็บ · ผลที่ต้องเห็น (ตัวเลข/ข้อความ) · ช่อง ผ่าน/ไม่ผ่าน · ลงชื่อ · วันที่ · ผลที่ต้องเห็นทุกข้อให้ตรวจบนหน้าเว็บจริงก่อนส่ง (สคริปต์ Playwright headless · reset ก่อนและหลัง) ห้ามลอกจากเทสต์อย่างเดียว · ถ้าเจอพฤติกรรมแปลก ห้ามแก้โค้ด ให้จดไว้ · ข้อที่ร้านกดเองไม่ได้ เช่น ตรวจ CR-02 หลัง 1 พ.ย. ต้องให้ทีมเปลี่ยนวันที่ของเครื่องทดสอบก่อน ให้เขียนขั้นนั้นไว้ในใบ · ผลที่ต้องเห็นทุกแถวติดป้ายที่มา [D:CR-0N] (หนังสือหรือคำตอบร้าน) · ถ้าหน้าเว็บจริงไม่ตรง [D:CR-0N] ห้ามเขียนตามหน้าจอ ให้ติด ⚠️ ผู้ต้องสงสัยบั๊ก และใส่ใน RELEASE-NOTES หัวข้อเรื่องที่ยังไม่ได้แก้
3. CHANGE-REPORT.md ส่วนสรุปรวม: ตาราง CR | commit แดง | commit แก้ | ไฟล์ที่แก้ | เทสต์ใหม่ | regression | ความเสี่ยงคงค้าง | วิธีถอยกลับ
4. ตรวจความครบ: ทุกคำขอในหนังสือ CR-01–05 มีแถวใน UAT · ทุกแถว UAT โยงกับ TC ใน TRACEABILITY · ข้อไหนขาดให้บอก
5. อัปเดต CHANGE-REQUESTS/REGISTER.md เป็น "รอตรวจรับ (UAT)" → git add -A (รวมเอกสารที่ค้างจากงานก่อน เช่น REGRESSION-REPORT.md docs/TRACEABILITY.md docs/ORACLE-CHANGES.md) → git status ตรวจไฟล์ → git commit "release: พร้อมตรวจรับ CR-01–05"
ไม่แน่ใจว่าร้านจะเข้าใจคำไหน ให้เขียนแบบง่ายกว่า · สรุปเป็นตาราง: เอกสาร | ส่วน | จำนวนรายการ
```

<!-- ✂ จบพรอมต์ · ข้างล่างคือผลที่คาดสำหรับผู้ตรวจ (runner อ่านหลังรันเสร็จเท่านั้น) -->
**ผลที่คาด** `tests/smoke.mjs` exit 0 ตอนระบบปกติ · exit 1 ตอนหยุดเว็บ · ซ้อมถอยกลับ: down → ตารางวันหยุดหาย นัดใหม่อยู่ · up → 3 วันหยุด นัดใหม่อยู่ · cr04 เขียว [คาด] · commit smoke + runbook 1 ตัว · `docs/DEPLOY-RUNBOOK.md` มีเวลาจริง · `RELEASE-NOTES.md` มีเรื่องที่ยังไม่แก้อย่างน้อย: cookie ใช้ได้หลังออกจากระบบ (TC-SEC-04) · บัตรปลอมไม่เตือน · เบอร์ไม่ตรวจรูปแบบ · owner ยกเลิกแทนลูกค้า · reset เปิดในโหมดใช้งานจริง · ติ๊กรถไม่ใส่ระยะ [CN §7] · UAT ครบ 5 CR · รอบ RUNNER: smoke 7 ข้อ 7/7 → 0/7 exit 1 (`ECONNREFUSED`) → 7/7 · down.sql/up ซ้ำ นัดใหม่ B14 อยู่ทุกจุด · cr04 14/14 · ซ้อมทั้งก้อน ~17 วิ · UAT 31 แถว โยง TC 30/31 · ตรวจ UAT บนหน้าจริงพบรายงานแสดงรหัสนักบำบัด (T01…) และ race ในกล่องเลื่อนนัด (เปลี่ยนวันเร็ว → ปุ่มรอบของวันก่อนค้าง · เซิร์ฟเวอร์ปฏิเสธ · ไม่แก้ จดเป็นเรื่องที่ยังไม่ได้แก้) [รันจริง:RUNNER LAB 12 · ขั้น 4b เพิ่มใน v3 ยังไม่ได้รัน]
> 🔒 ผู้เขียน README: ภาพ `lab12-release-notes.png` และข้อความที่คัดจาก RELEASE-NOTES ของรอบจริง **ห้ามมีแถวเรื่อง "กดใช้บริการเสร็จก่อนถึงเวลานัด"** (L2 = ข้อสอบชุด B ข้อ 5) · ถ้ามีให้ครอปหรือตัดแถวนั้นออก (M10)
**ไปต่อได้เมื่อ** ซ้อมถอยกลับผ่านทุกขั้นโดยข้อมูลนัดไม่หาย · RELEASE-NOTES ไม่มีศัพท์โปรแกรม · REGISTER เป็น "รอตรวจรับ" ครบ 5 CR

---

## ภาคผนวก · พรอมต์ "รันซ้ำ" และ "ถ้าเจอปัญหา" (ร่างสำหรับ README)

| อยากทำ | 💬 พรอมต์ |
|---|---|
| ล้างข้อมูลทดสอบ | `(รันคำสั่งด้วย PowerShell) เรียก POST http://localhost:4000/api/test/reset แล้วเช็กว่าได้ {"ok":true}` |
| รันตาข่ายทั้งหมด | `(รันคำสั่งด้วย PowerShell) รันทุกชุดตามหัวข้อ "รันยังไง" ใน CLAUDE.md (e2e ครบ 3 เบราว์เซอร์ รันแบบ background แล้วรอ · แยก passed / expected-fail / failed) แล้วสรุปเป็นตาราง ชุด \| ผ่าน/ทั้งหมด \| เวลา ห้ามแก้อะไร` |
| ดูข้อมูลในฐานข้อมูล | `(รันคำสั่งด้วย PowerShell) ใช้ docker exec sabai06-db psql -U sabai -d sabai ดูจำนวนนัดแยกสถานะ (อ่านอย่างเดียว ห้ามแก้)` |
| ปิดระบบ (เก็บข้อมูล) | `(รันคำสั่งด้วย PowerShell) ปิดระบบ: docker compose -f web/compose.yaml down แล้ว docker compose -f db/compose.yaml down ห้ามใส่ -v` |
| เทียบงานกับเฉลย (หลังจบ LAB 12 · ลบ 3 กฎ `Read(...)` ออกจาก `.claude/settings.json` เองก่อน แล้วเปิดเซสชันใหม่) | `เทียบ docs/impact/CR-0N.md และ tests/ ของผมกับ _solution/ บอกเคสหรือไฟล์ที่ผมยังขาด และข้อที่ของผมดีกว่า` |

| อาการ | 💬 พรอมต์ |
|---|---|
| `docker version` ไม่มี Server / `error during connect` | `Docker Desktop ยังไม่พร้อม ช่วยเช็กด้วย PowerShell ว่า docker version เห็น Server ไหม ถ้าไม่เห็นให้บอกผมเปิด Docker Desktop แล้วรอไอคอนวาฬหยุดหมุน ห้ามรีสตาร์ตบริการเอง` |
| `bind: An attempt was made to access a socket…` (Windows/WinNAT จองพอร์ต) | `เปิดเว็บไม่ได้ error bind forbidden ช่วยรัน netsh interface ipv4 show excludedportrange protocol=tcp ดูว่า 4000 หรือ 5433 อยู่ในช่วงจองไหม ถ้าอยู่ให้เสนอพอร์ตว่างนอกช่วง และบอกวิธีตั้ง $env:WEB_PORT / $env:DB_PORT / $env:BASE_URL ก่อนทำ` |
| container ชื่อชน / พอร์ต 4000 · 5433 ถูกใช้ (บท 04–05 เปิดค้าง) | `docker compose ขึ้นว่าชื่อ container ซ้ำหรือพอร์ตถูกใช้ ช่วยดู docker ps ว่าตัวไหนชน (เช่น pawpantry05 ที่ 4000 · sabai-db ที่ 5433) บอกผมก่อนแล้วหยุดด้วย docker stop (ห้ามลบ volume) หรือเสนอพอร์ตว่างผ่าน $env:WEB_PORT / $env:DB_PORT / $env:BASE_URL` |
| `running scripts is disabled` / `UnauthorizedAccess` ตอนเรียก `.ps1` | `PowerShell ไม่ยอมรัน tools\rea.ps1 ช่วยรันใหม่ด้วย powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 … (ไม่แก้ค่าเครื่อง) ถ้ายังติดเพราะไฟล์มาจาก zip ให้บอกผมก่อนรัน Unblock-File -Path tools\*` |
| Claude รันด้วย bash แล้วพัง (`/c/...` · `$env:` ไม่รู้จัก) | `คำสั่งในงานนี้ต้องรันด้วย PowerShell ห้ามแปลงเป็น bash · ถ้าเครื่องมือ PowerShell ใช้ไม่ได้ ให้เขียนคำสั่งเดิมลง tmp\run.ps1 แล้วรัน powershell -NoProfile -ExecutionPolicy Bypass -File tmp\run.ps1 · บอกสาเหตุก่อนรันใหม่` |
| check-rules error import `.ts` | `node web/scripts/check-rules.mjs error ตอน import .ts ช่วยเช็ก node -v ถ้าต่ำกว่า 22.18 ให้บอกวิธีอัปเดต หรือรันใน container node:22-alpine ใน network sabai06-net` |
| REA อ่าน JSON ไม่ได้ (BOM) / HAR schema validation failed | `REA อ่านไฟล์ input ไม่ได้ ช่วยบอกสาเหตุก่อน: JSON มี BOM = สร้างด้วย > ของ PowerShell ให้รันใหม่ด้วย powershell -NoProfile -ExecutionPolicy Bypass -File tools\rea.ps1 -Out <ไฟล์> · HAR ไม่ผ่าน = บันทึกจาก localhost ให้บันทึกใหม่ผ่าน http://127.0.0.1:4000 · ห้ามแก้ HAR ด้วยมือ` |
| คำสั่งถูกตัดเพราะ timeout (build · e2e 3 เบราว์เซอร์) | `คำสั่งนี้นานเกิน 2 นาทีแล้วถูกตัด ช่วยรันใหม่แบบ background หรือตั้ง timeout ยาว แล้วรอจนจบ รายงานผลจริงจาก log อย่าสรุปจากผลที่ยังไม่จบ` |
| ไทย/จีนเป็น `?` (หลัง migration หรือยิง API) | `ข้อความไทย/จีนในฐานข้อมูลเป็น ??? ช่วยเช็กก่อนด้วย SQL SELECT name_th = '<ข้อความไทย>' (จอ PowerShell อาจเพี้ยนทั้งที่ข้อมูลถูก) ถ้าเพี้ยนจริง ให้เช็กว่ารัน SQL ด้วย docker cp + psql -f และยิง API ด้วยสคริปต์ node หรือ curl.exe --data-binary '@ไฟล์.json' ไม่ใช่ Invoke-RestMethod -Body · แก้ข้อมูลด้วย migration ที่รันซ้ำได้` |
| migration รอบ 2 ตัวแดง `NOTICE … already exists` หรือ error | `migration รอบ 2 ขึ้นตัวแดง ช่วยเช็ก $LASTEXITCODE และบรรทัด INSERT 0 n ก่อน · exit 0 = แค่ NOTICE (อยากให้เงียบใส่ SET client_min_messages = warning;) · exit ไม่ใช่ 0 ให้บอกบรรทัดและสาเหตุ แก้ให้รันซ้ำได้ (IF NOT EXISTS · ON CONFLICT DO NOTHING) โดยไม่ลบข้อมูล แล้วซ้อม 2 ครั้งใหม่ ห้าม down -v` |
| reset ไม่ได้ 200 | `POST /api/test/reset ไม่ได้ 200 ช่วยอ่าน docker logs sabai06-web ช่วงนั้นแล้วบอกสาเหตุจาก error จริงก่อนแก้ ห้ามลบ volume ห้ามแก้ค่าที่คาดหวัง` |
| เทสต์เดิมแดงหลังแก้ | `เทสต์เดิมข้อนี้แดงหลังแก้ CR ช่วยบอกว่าเว็บผิด เทสต์เก่าล้าสมัย หรือเทสต์ใหม่เขียนผิด พร้อมหลักฐาน ห้ามแก้เทสต์ให้ผ่าน ถ้าต้องเปลี่ยนค่าที่คาดหวังให้บอกผมก่อนและจดใน docs/ORACLE-CHANGES.md` |
| Claude จะแก้ e2e-legacy หรือใช้ `down -v` | `หยุดก่อน e2e-legacy เป็นชุดที่ส่งมอบ ห้ามแก้ และห้าม docker compose down -v เพราะข้อมูลลูกค้าจะหาย เทสต์ข้อไหนล้าสมัยให้เขียนเหตุผลแล้วถามผม งานฐานข้อมูลให้หาวิธีที่ไม่ลบ volume` |
| e2e ผ่านบ้างล้มบ้าง (รอบ 1 ≠ รอบ 2) | `เทสต์ข้อนี้ผ่านบ้างล้มบ้าง ช่วยรันซ้ำ --repeat-each=5 บอกสาเหตุ (เช่น นาฬิกาหรือข้อมูลไม่ได้ reset) ถ้าเป็นเทสต์ที่ส่งมอบและไม่เกี่ยวกับไฟล์ที่ CR แตะ ให้พิสูจน์บน image เดิมก่อนสรุปว่า regression ห้ามแก้ e2e-legacy · เทสต์ของเราแก้ได้โดยไม่เปลี่ยนค่าที่คาดหวัง` |
| mutant ค้างอยู่ในโค้ด | `เช็ก git status และ git diff ใน web/lib/rules ว่ามีโค้ดที่ทำพังค้างไหม ถ้ามีให้คืนด้วย git checkout -- <ไฟล์> แล้ว rebuild และรัน golden` |
