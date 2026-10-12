# LAB 0_RESULT · เช็กเครื่อง + เตรียม REA

| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 09:19 · 09:23 · ~4 นาที (เครื่อง ~0.3 นาที: doctor 2 วิ · compose build 3.3 วิ (cache) · npm install 2.3+1.5 วิ · playwright install 1.3 วิ · REA hdi 3.5 วิ · ที่เหลือ = agent) |
| cwd ของเซสชัน / settings มีผลไหม | runner cwd = worktree คอร์ส (ไม่ใช่ `w/`) · ทุกคำสั่งรันด้วย `Set-Location C:\t\work\run05\w` · ❌ settings ไม่ได้ถูกบังคับโดย harness → **ทำตามกติกาเอง** · หมายเหตุ: ตอนนี้ `w/` ยังไม่มี `CLAUDE.md` และ `.claude/settings.json` (ตามคาด LAB 1 สร้าง) |
| ไฟล์ที่สร้าง/แก้ | ไม่มีไฟล์ใน git ถูกแก้ (`git status --short` ว่าง) · สร้าง `out/scenario-hdi.json` (คัดจาก scenario-coupon + เปลี่ยน start_url) · `out/scenario-hdi.json.out` (4,530,542 bytes) · `e2e-legacy/node_modules` `rea/node_modules` (ignored) |
| สคริปต์ชั่วคราว | ไม่มีสคริปต์ · `../tools/lab0/doctor.txt` (สำเนาผล doctor เต็ม 2,829 บรรทัด) |
| โหมดการรัน · shell ที่ agent ใช้จริง | A · PowerShell tool (Windows PowerShell 5.1) สำหรับทุกคำสั่งของพรอมต์ · Git Bash ใช้เฉพาะ checklist ตั้งต้นของ RUNNER (ซึ่งกำหนดให้เป็น Git Bash) |
| timeout / รันซ้ำ | compose up/npm install/playwright install ตั้ง timeout 10 นาที (foreground) · ไม่มีการสั่งซ้ำระหว่างรอ · `rea.ps1 doctor` รัน 3 ครั้ง (ครั้งที่ 2 เพื่อวัดขนาด/เวลา output ครั้งที่ 3 ทดสอบ `--filter-output` เพื่อเสนอแก้พรอมต์ ไม่ใช่เพราะ timeout) |
| สถานะเว็บ | `pawpantry05` Up (healthy) `0.0.0.0:4000->3000` · container สร้าง 09:21:02 · image `pawpantry05:latest` build 09:00:25 (prep) — รอบนี้ cache ทั้งหมด · **เปิดค้างไว้** |
| ข้อมูลทดสอบ | ไม่ reset · ไม่ล็อกอิน (scenario REA เป็น guest ตะกร้าใน localStorage) |

## ตรวจโฟลเดอร์ตั้งต้น (RUNNER · ครั้งเดียวก่อน LAB 0)

| ตรวจ | ต้องได้ | ได้จริง | ผ่าน |
|---|---|---|---|
| `grep -rniE "bug_?mode" petshop --exclude-dir=node_modules --exclude-dir=.next \| wc -l` | 0 | `0` | ✅ |
| `grep -c "PP-231" petshop/lib/orders.ts` | 1 | `1` | ✅ |
| `docker compose -f petshop/docker-compose.yml config \| head -1` | `name: pawpantry05` | `name: pawpantry05` | ✅ |
| `e2e-legacy/tests/` 10 spec + `fixtures.ts` + `new/.gitkeep` | ครบ | `01-home … 10-mobile-api` (10 ไฟล์ `*.spec.ts`) + `fixtures.ts` + `new/.gitkeep` | ✅ |
| `rea/` 8 ไฟล์ · `grep -c "petshop:3000" rea/scenario-coupon.json` = 1 | ครบ · 1 | ครบ 8 ไฟล์ (+ `package-lock.json` เกินมา 1 ไฟล์) · `1` | ✅ |
| `TEST-DATA.md` `.gitignore` (มี `rea/scratch/`) `petshop/HANDOVER-NOTES.md` | มี | มีครบ · `.gitignore` มี `rea/scratch/` | ✅ |
| `docker image inspect rea-lab:6.4.0` | มี | `sha256:2012d907…` size 2,654,494,021 | ✅ (ไม่ได้ build) |
| `PS> Get-NetTCPConnection -LocalPort 4000` + คิวพอร์ต | ว่าง | ว่าง (ไม่มี connection) · `docker ps` เห็น `sabai06-web` ที่ **4100** และ `sabai06-db` ที่ **5533** เท่านั้น (ตาม D10) ไม่มีใครถือ 4000 | ✅ |
| ไม่มี container `pawpantry05` ของงานอื่น | ไม่มี | `docker ps -a` ไม่มี `pawpantry05` | ✅ |
| (เพิ่ม) `w/` เป็น git repo | — | commit `e872ff8 starting folder (chapter 05)` · status ว่าง | ✅ |

## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)
- ไม่ใช้ git ที่เปลี่ยนสถานะ (ใช้แค่ `status` `log` `diff --stat`) · `git diff --stat -- e2e-legacy TEST-DATA.md` = ว่าง → ไม่มีการเลี่ยง deny เขียนไฟล์ต้องห้ามผ่าน shell
- ไม่ปิด/ไม่แตะ container ของบทอื่น (`sabai06-*` `multi-account-devtool` `deep_vision_5090_vllm`) · พรอมต์ข้อ 2 "ยังไม่ต้องปิดอะไร" ทำตาม
- ไม่ build image `rea-lab` เอง (ข้อ 3) · ไม่เปลี่ยน ExecutionPolicy ของเครื่อง
- ไม่แปลงคำสั่ง PowerShell เป็น bash (ยกเว้น checklist ของ RUNNER ที่กำหนดเป็น Git Bash)
- ไม่ใช้ Playwright MCP · ไม่อ่าน LAB อื่น / LESSON-PLAN / _solution
- พลาด: ไม่มี

## คำตอบสรุปที่แสดงในแชท

> | รายการ | ผล | พร้อมไหม | ถ้าไม่พร้อมต้องทำอะไร |
> |---|---|---|---|
> | Docker | Client/Server 29.5.2 · Docker Desktop 4.75.0 · context `desktop-linux` | ✅ | – |
> | Docker Compose | v5.1.4 | ✅ | – |
> | Node | v26.7.0 (≥ 20) | ✅ | – |
> | npm | 12.2.0 | ✅ | – |
> | ExecutionPolicy | MachinePolicy Undefined · UserPolicy Undefined · Process **Bypass** · CurrentUser **RemoteSigned** · LocalMachine Undefined | ✅ | ไม่ต้องเปลี่ยน · เรียก `.ps1` ด้วย `powershell -NoProfile -ExecutionPolicy Bypass -File …` เสมอ |
> | พอร์ตที่ Windows จอง | 3000 **อยู่ใน** ช่วง `2970–3069` (ติดกับ `3070–3169`) · 4000 **ไม่อยู่** ในช่วงใด | ✅ (4000) | – |
> | พอร์ต 4000 ว่างไหม | `Get-NetTCPConnection` ไม่พบ · `docker ps` ไม่มีใครถือ 4000 (มี sabai06-web :4100 · sabai06-db :5533 ซึ่งไม่ชน) | ✅ | – |
> | ทำไมใช้ 4000 | Windows/WinNAT จองช่วง 2970–3069 ไว้ (รวม 3000) Docker จึง bind host port 3000 ไม่ได้ · compose ของบทนี้แมป `4000:3000` (ในคอนเทนเนอร์ยังเป็น 3000) | – | – |
> | image `rea-lab:6.4.0` | มี · Size 2,654,494,021 bytes (~2.65 GB) | ✅ | – |
> | `rea.ps1 doctor` | exit **1** · `healthy: false` · ผ่าน: `node` 24.20.0, `host` ubuntu 24.04 · ไม่ผ่าน: `hopper` `ghidra` `ida-registration` = `missing_analysis_engine`, `skill:identity` = `config_drift` | ✅ สำหรับงานเว็บ | ไม่ต้องทำ · ข้อที่ไม่ผ่านเป็นเครื่องมือแกะไบนารี (Hopper/Ghidra/IDA) และ skill ของ agent ซึ่งงานเว็บ (`analyze-javascript-application` `capture-browser-scenario` `inspect-web-network-capture`) ไม่ใช้ |
> | เว็บ `pawpantry05` | `docker compose up -d --build` exit 0 · container `Up (healthy)` `0.0.0.0:4000->3000` · `http://localhost:4000/api/health` → 200 `{"ok":true}` | ✅ | – |
> | docker network | `pawpantry05_default` มี | ✅ | – |
> | REA เห็นเว็บใน network | `docker run --rm --network pawpantry05_default … fetch('http://petshop:3000/api/health')` → `{"ok":true}` exit 0 | ✅ | – |
> | npm install `e2e-legacy` | added 7 packages · 0 vulnerabilities | ✅ | – |
> | npm install `rea` | added 2 packages · 0 vulnerabilities | ✅ | – |
> | Playwright browsers | `npx playwright install chromium firefox webkit` exit 0 (มีอยู่แล้ว: chromium-1248 firefox-1555 webkit-2370) · `playwright --version` 1.63.0 | ✅ | – |
>
> สรุป: พร้อมทุกข้อ · จำไว้ว่าเว็บเดียวกันมี 2 ที่อยู่ — เบราว์เซอร์/Playwright บนเครื่องใช้ `http://localhost:4000` ส่วน REA ใน container ใช้ `http://petshop:3000` ผ่าน network `pawpantry05_default`

## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)

| ค่า | ตัวเลข | คำสั่ง |
|---|---|---|
| ขนาด image rea-lab | 2,654,494,021 bytes | `docker image inspect rea-lab:6.4.0 --format "{{.Size}}"` |
| ความยาว output `doctor` | 2,829 บรรทัด · 82,965 ตัวอักษร | `$o = … doctor; $o.Count; ($o -join "`n").Length` |
| doctor checks | 6 ข้อ · ผ่าน 2 (node, host) · ไม่ผ่าน 4 | `doctor --filter-output healthy,checks` |
| doctor catalog | cli_commands 127 · mcp_tools 170 · mcp_prompts 6 · cli 6.4.0 · expected_skill_version 37 | อ่านจาก output doctor |
| ช่วงพอร์ตที่จอง | 23 ช่วง (รวม 3 ช่วง administered: 8650, 8888, 50000–50059) | `netsh interface ipv4 show excludedportrange protocol=tcp` |
| spec ใน e2e-legacy | 10 | `ls e2e-legacy/tests/*.spec.ts \| wc -l` |
| ทางสำรอง hdi scenario | steps_completed **11/11** · ไฟล์ผล 4,530,542 bytes · evidence `ev_0d023efd` | `node rea\rea-summarize.mjs out\scenario-hdi.json.out` |

## คำสั่งที่รัน (REA/docker/playwright: คำสั่ง | exit | เวลา | ขนาดผล)

| คำสั่ง (จาก `w/` · PowerShell) | exit | เวลา | ผล |
|---|---|---|---|
| `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 doctor` | 1 | 2.0 วิ | stdout 2,829 บรรทัด (`healthy: false`) |
| `cd petshop; docker compose up -d --build` | 0 | 3.3 วิ (ทุก layer CACHED · ผู้เรียนครั้งแรกจะ ~3 นาที) | network `pawpantry05_default` + container `pawpantry05` Created/Started |
| รอ healthy (`docker inspect -f {{.State.Health.Status}}`) | – | 0.2 วิ (healthy ทันที) | healthy |
| `Invoke-WebRequest http://localhost:4000/api/health` | – | – | 200 `{"ok":true}` |
| `docker network ls` | 0 | – | มี `pawpantry05_default` (และ `sabai06-net` `sabai-net` ของบทอื่น) |
| `docker run --rm --network pawpantry05_default --entrypoint node rea-lab:6.4.0 -e "fetch('http://petshop:3000/api/health')…"` | 0 | 0.7 วิ | `{"ok":true}` |
| `npm install` (e2e-legacy) | 0 | 2.3 วิ | added 7 |
| `npm install` (rea) | 0 | 1.5 วิ | added 2 |
| `npx playwright install chromium firefox webkit` (e2e-legacy) | 0 | 1.3 วิ (ติดตั้งไว้แล้ว) | – |
| **RUNNER (ข)①** `docker run --rm --entrypoint node rea-lab:6.4.0 -e "fetch('http://host.docker.internal:4000/api/health')…"` (ไม่มี `--network`) | 0 | 0.7 วิ | `{"ok":true}` |
| **RUNNER (ข)②** `rea.ps1 -Out out\scenario-hdi.json.out capture-browser-scenario /work/out/scenario-hdi.json --json` (ไม่ใส่ `-Network`) | 0 | 3.5 วิ | 4,530,542 bytes · `steps_completed: 11/11` · `completeness: incomplete (missing_sections: events)` · evidence `ev_0d023efd` · duration_ms 1325 |
| `node rea\rea-summarize.mjs out\scenario-hdi.json.out` | 0 | – | สรุปปกติ (ดูแถวเด่น) |
| **RUNNER (ค)** `Get-ExecutionPolicy -List` | – | – | Machine/User Undefined · Process Bypass · CurrentUser RemoteSigned · LocalMachine Undefined |
| **RUNNER (ง)** build image | ไม่ได้ build (ผู้สั่งงานแจ้งว่ามีแล้ว) | – | – |

`out/scenario-hdi.json` สร้างด้วย .NET `UTF8Encoding($false)` (ReadAllText/Replace/WriteAllText) → ไบต์แรก `{` ไม่มี BOM · ตรวจด้วย node ว่า `start_url.url = http://host.docker.internal:4000/` และคำค้น `แซลมอน` ยังอยู่ครบ

## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)

| แหล่ง | แถว |
|---|---|
| netsh | `2970  3069` ← 3000 อยู่ในช่วงนี้ · ไม่มีช่วงไหนครอบ 4000 |
| doctor | `- name: ghidra · ok: false · classification: missing_analysis_engine · detail: GHIDRA_INSTALL_DIR is not set` |
| doctor | `- name: node · ok: true · classification: healthy · detail: 24.20.0` |
| docker ps | `pawpantry05 Up 7 seconds (healthy) 0.0.0.0:4000->3000/tcp` |
| probe ใน network | `fetch('http://petshop:3000/api/health')` → `{"ok":true}` |
| hdi scenario (api_calls) | `POST /api/coupons/validate 200` request `{"code":"PAW10","items":[{"slug":"lickable-salmon-treat","size":"4 ซอง","qty":1}]}` → `{"ok":true,"code":"PAW10","discount":6,"freeShipping":false,"message":"ใช้คูปอง PAW10 แล้ว"}` |

## ตัดสินแทนผู้เรียน (คำถาม | คำตอบ | ที่มา 🧑/ตัดสินเอง | เหตุผล)

| คำถาม | คำตอบ | ที่มา | เหตุผล |
|---|---|---|---|
| doctor exit 1 → หยุดไหม | ไปต่อ | ตัดสินเอง (พรอมต์ข้อ 3 บอกให้อ่านผลก่อน) | ข้อที่ไม่ผ่านเป็น engine แกะไบนารี/skill ไม่เกี่ยวกับคำสั่งเว็บ · node/host ผ่าน |
| เห็น `sabai06-*` ใน docker ps → หยุดไหม | ไปต่อ | ตัดสินเอง (RUNNER คิวพอร์ต + D10) | sabai06 ถือ 4100/5533 ไม่ใช่ 4000 · พรอมต์บอก "ยังไม่ต้องปิดอะไร" |
| Playwright browsers มีอยู่แล้ว ต้องลงซ้ำไหม | รันคำสั่งตามพรอมต์ 1 ครั้ง (จบใน 1.3 วิ) | ตัดสินเอง | ทำตามพรอมต์ตรงตัว ไม่ข้าม |

(LAB 0 ไม่มีจุด "ถามผมก่อน" และไม่มีหัวข้อ 🧑)

## ข้อสังเกต 👀 (บทเรียนจากรอบจริง ไม่ใช่สรุปผลซ้ำ)
- **output ของ `doctor` ยาวมาก** (2,829 บรรทัด ~83 KB เพราะพ่น catalog ของ MCP tools 170 ตัว) · ใน Claude Code จะถูกตัดกลางเหลือหัว/ท้าย ส่วนที่สำคัญ (`checks[6]`) อยู่ต้น ๆ จึงยังอ่านได้ แต่กิน context มาก · `doctor --filter-output healthy,checks` ได้ผลเหลือ ~30 บรรทัด exit 1 เท่าเดิม (ทดสอบแล้ว)
- ExecutionPolicy ของเครื่องนี้ **ไม่ใช่** Restricted/Undefined ตาม 🎯: `CurrentUser = RemoteSigned` และ `Process = Bypass` (Process เป็น Bypass เพราะ PowerShell tool ของ Claude Code เปิด process ด้วย Bypass เอง — ผู้เรียนที่เปิด PowerShell เองจะไม่เห็นบรรทัดนี้เป็น Bypass) → README ควรบอกว่า "ค่าอาจต่างกันได้ ไม่ต้องเปลี่ยน เพราะเราเรียกผ่าน `-ExecutionPolicy Bypass -File` เสมอ"
- `Get-Content` ของ PowerShell 5.1 แสดงภาษาไทยใน `scenario-coupon.json` (UTF-8 ไม่มี BOM) เป็นอักษรเพี้ยน (`เนเธเธฅ…`) — เป็นแค่การแสดงผล แต่ถ้า agent แก้ไฟล์ด้วย `Get-Content | Set-Content` จะทำให้คำค้นภาษาไทยในไฟล์พังจริง · ใน LAB 0 ใช้ .NET `UTF8Encoding($false)` แทนแล้วปลอดภัย
- ทางสำรอง `host.docker.internal:4000` ใช้ได้ทั้ง 2 ชั้นบนเครื่องนี้ (fetch จาก node + Chromium ใน REA 11/11 steps) → ไม่พบปัญหา IPv6 · URL ใน evidence จะเป็น `host.docker.internal:4000` แทน `petshop:3000`
- capture-browser-scenario ได้ `completeness: incomplete` (`missing_sections: events`) แม้ทุก step ผ่าน — ควรอธิบายใน LAB 3 ว่า "incomplete" ไม่ได้แปลว่า scenario ล้ม
- `docker compose up --build` รอบนี้ใช้ cache ทั้งหมด (3.3 วิ) เพราะ prep build ไว้แล้ว — เวลาที่ผู้เรียนเจอจริงรอบแรก (~3 นาที) วัดจากรอบนี้ไม่ได้
- npm 12 พิมพ์ `npm notice run npx` / `npm notice run playwright …` ทุกครั้งที่เรียก npx — ไม่ใช่ error

## ปัญหา / วิธีแก้
- ไม่มีปัญหาที่ทำให้หยุด
- doctor output ยาวจนถูกตัดในหน้าต่างผล → วัดขนาดด้วยการรันซ้ำแบบเก็บในตัวแปร (ดูข้อเสนอ M ด้านล่าง)

## ข้อเสนอแก้พรอมต์ (ระดับ H = ทำต่อไม่ได้/ผลผิด · M = ได้ผลแต่สับสน · m = ถ้อยคำ)
- **H:** ไม่มี
- **M (LAB 0 ข้อ 3):** เปลี่ยนเป็น `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 doctor --filter-output healthy,checks` เพื่อลด output จาก 2,829 บรรทัดเหลือ ~30 บรรทัด (exit code และข้อมูลที่ต้องใช้เหมือนเดิม)
- **M (🎯 LAB 0):** ExecutionPolicy "ส่วนใหญ่ Restricted/Undefined" → เพิ่ม "บางเครื่องเป็น RemoteSigned และถ้ารันผ่าน Claude Code จะเห็น Process = Bypass ก็ปกติ"
- **m (RUNNER LAB 0 (ข)② / LAB 3):** ระบุวิธีคัด+แก้ scenario JSON ที่ไม่ทำให้ภาษาไทยพัง (เช่น `node -e` หรือ .NET `UTF8Encoding($false)`) และห้าม `Get-Content | Set-Content` ใน PowerShell 5.1
- **m (🎯 LAB 0):** ระบุว่า `docker compose up --build` ครั้งที่ 2 ขึ้นไปใช้ cache เร็วมาก — ไม่ต้องตกใจถ้าไม่ถึง 3 นาที

## ภาพที่ควรใช้ใน README (../design/shots/lab0-*.png 1280×800 + คำอธิบาย 1 บรรทัด)
- ไม่ได้ถ่ายใน LAB 0 (ผลเป็นตาราง/terminal ล้วน ผู้ทำรูปทำจาก result ได้) · ถ้าต้องการ: หน้า `http://localhost:4000/` หลัง compose up = "เว็บ PawPantry ขึ้นที่พอร์ต 4000" · และไดอะแกรม "1 เว็บ 2 ที่อยู่" (`localhost:4000` ↔ `petshop:3000`)
