# RUNNER · รัน LAB เหมือนผู้เรียน (บท 05 รับช่วงระบบเดิม PawPantry)

คุณคือ "ผู้เรียน + Claude Code" ที่วางพรอมต์ของ LAB ที่ได้รับมอบหมาย ลงในเซสชันใหม่ แล้วทำตามพรอมต์นั้นทุกข้อ **ตรงตัว**

## ผังโฟลเดอร์ sandbox (ผู้สั่งงานเตรียมให้ · ห้ามรันในโฟลเดอร์บทจริง)

```text
C:/t/work/<ชื่องาน>/
├─ w/        = สำเนาโฟลเดอร์บท 05 หลังทำ LESSON-PLAN ข้อ 7 แล้ว (ไม่มี _solution/) ← working dir ของทุก LAB
├─ design/   = PROMPTS.md · RUNNER.md (สำเนา) · results/ · shots/
└─ tools/    = สคริปต์ชั่วคราวของ runner (Playwright headless, ffmpeg) + node_modules ของ tools
```

- พรอมต์อยู่ใน `../design/PROMPTS.md` อ่าน **เฉพาะหัวข้อ LAB ที่ได้รับ** (บล็อก ```` ```text ```` ) · ส่วน 🎯 ผลที่คาดหวัง / 🧑 คำตอบ ในหัวข้อเดียวกันอ่านได้ แต่ **ห้ามใช้ 🎯 เป็นคำตอบ** ต้องรันจริงแล้วเทียบทีหลัง
- ห้ามอ่าน LAB อื่นล่วงหน้า · ห้ามอ่าน `LESSON-PLAN.md` `CR-DESIGN.md` `CODEBASE-NOTES.md` หรือไฟล์อื่นใน `_solution/` ของบทจริง (จะรู้เฉลยก่อนผู้เรียน)
- **1 LAB = 1 เซสชันใหม่** ที่มี cwd = `w/` เพื่อให้ `w/CLAUDE.md` และ `w/.claude/settings.json` มีผลเหมือนเครื่องผู้เรียน (วิธีรัน 2 แบบ ดู "โหมดการรัน") · ถ้า runner เป็นเซสชันที่ cwd ไม่ใช่ `w/` ให้จดใน result ว่า settings ไม่ได้ถูกบังคับ และทำตามกติกาเองอย่างเคร่งครัด
- ผู้สั่งงานจะบอกว่ารัน LAB ไหน · LAB ถัดไปใช้ไฟล์ที่ LAB ก่อนสร้างไว้ใน `w/` (ห้ามสร้างแทนถ้าไม่มี ให้หยุดรายงาน)

## คิวพอร์ต 4000 (บท 05 กับบท 06)

- บท 05 และบท 06 ใช้ host port **4000** ทั้งคู่ → **runner บท 05 กับ runner บท 06 ห้ามรันพร้อมกัน** ถ้าทั้งคู่ใช้ 4000 · ผู้สั่งงาน (orchestrator) เป็นคนจัดคิว
- ก่อนเริ่มทุก LAB: `docker ps --format "{{.Names}} {{.Ports}}"` ถ้าเห็น `sabai06-*` หรือ container อื่นถือ `0.0.0.0:4000` → **หยุด ถามผู้สั่งงาน** (ห้าม stop container ของบทอื่นเอง)
- ทางเดียวที่รันคู่กันได้: runner **บท 06** ย้ายไป `WEB_PORT=41xx` ใน sandbox ของตัวเอง (บท 06 รองรับตาม 06 LESSON-PLAN P3) · runner บท 05 คง 4000 เพราะพรอมต์บท 05 ฮาร์ดโค้ด 4000 (`WEB_PORT` ของบท 05 มีไว้แก้ปัญหาผู้เรียนเท่านั้น)

## ก่อนเริ่ม LAB 0 (ครั้งเดียว) · ตรวจโฟลเดอร์ตั้งต้น

| ตรวจ (Git Bash จาก `w/` เว้นแต่ขึ้นต้น `PS>`) | ต้องได้ | ถ้าไม่ได้ |
|---|---|---|
| `grep -rniE "bug_?mode" petshop --exclude-dir=node_modules --exclude-dir=.next \| wc -l` | `0` | หยุด · รายงานว่ายังไม่ได้ทำ LESSON-PLAN §7 #1 |
| `grep -c "PP-231" petshop/lib/orders.ts` | `1` | หยุด (ยังไม่อบ BUG-01 · §7 #2) |
| `docker compose -f petshop/docker-compose.yml config \| head -1` | `name: pawpantry05` | หยุด · ระดับ H (จะไปลบ/recreate container บท 02/03 · §7 #3) |
| `e2e-legacy/tests/` มี 10 spec + `fixtures.ts` + `new/.gitkeep` | ครบ | หยุด |
| `rea/` มี `Dockerfile rea.ps1 rea-input.mjs rea-summarize.mjs record-har.mjs scenario-coupon.json package.json README.md` · `grep -c "petshop:3000" rea/scenario-coupon.json` = 1 | ครบ | หยุด |
| `TEST-DATA.md` `.gitignore` (มี `rea/scratch/`) `petshop/HANDOVER-NOTES.md` | มี | หยุด |
| `docker image inspect rea-lab:6.4.0` | มี | หยุด (ต้อง build ก่อน = 🧰 ของผู้เรียน · จดเวลาถ้าผู้สั่งงานให้ build) |
| `PS> Get-NetTCPConnection -LocalPort 4000 -ErrorAction SilentlyContinue` + "คิวพอร์ต 4000" | ว่าง | หยุด · **ห้ามเปลี่ยนพอร์ตเอง** ถามผู้สั่งงาน |
| ไม่มี container ชื่อ `pawpantry05` ของงานอื่นรันอยู่ | ไม่มี | ถามผู้สั่งงาน |

## โหมดการรัน

**แบบ A (แนะนำ) · runner ทำเองในเซสชันนี้:** ตั้ง cwd = `w/` แล้วทำตามพรอมต์ทีละข้อเหมือนเป็น Claude Code ของผู้เรียน · จุด "ถามผมก่อน" = runner ตัดสินเอง (ข้อ 3 ด้านล่าง) แล้วทำต่อทันที

**แบบ B · `claude -p` (ใช้เมื่อต้องการให้ CLAUDE.md/settings ของ `w/` มีผลจริง):**
1. ใน `w/` (PowerShell): `yolo.cmd -p "<พรอมต์ทั้งก้อน>" > ..\design\results\LAB<N>_t1.txt` (ตั้ง timeout ยาว · LAB ที่มี build/regression ใช้ ≥ 30 นาที หรือรันเบื้องหลัง)
2. `claude -p` **จบเซสชันทันที**ที่พรอมต์หยุดถาม (LAB 1 5 6 7 8 10 มีจุดถาม) → runner อ่านคำถามท้าย transcript แล้ว**ตัดสินคำตอบเอง** (ข้อ 3) จากนั้นต่อเซสชันเดิมด้วย `yolo.cmd -p --continue "<คำตอบ>" > ..\design\results\LAB<N>_t2.txt` จาก cwd เดิม (`w/`) · ทำซ้ำจนพรอมต์ครบทุกข้อ
3. จดทุกคู่คำถาม/คำตอบในหัวข้อ "ตัดสินแทนผู้เรียน" และเก็บ transcript ทุกช่วง (`LAB<N>_t*.txt`) ไว้ใน `../design/results/`
4. ถ้า `--continue` ไปต่อผิดเซสชัน (เช่นมีเซสชันอื่นใน cwd เดียวกัน) ให้จดแล้วสลับไปแบบ A

## วิธี "รันพรอมต์ตรงตัว"

1. คัดพรอมต์จากบล็อก ```` ```text ```` ของ LAB นั้นทั้งก้อน (รวมข้อความลูกค้า/ใบ CR ท้ายพรอมต์) ทำตามทุกข้อตามลำดับ
2. คำสั่ง shell ในพรอมต์เป็น **PowerShell** → รันด้วย PowerShell (Windows PowerShell 5.1) จาก `w/` · `.ps1` เรียกด้วย `powershell -NoProfile -ExecutionPolicy Bypass -File …` ตามพรอมต์ · ห้ามแปลงเป็น bash เอง ถ้าคำสั่งพังให้จดข้อความ error ตรงตัวแล้วค่อยหาทางแก้ที่ใกล้ที่สุด และจดใน "ข้อเสนอแก้พรอมต์" · จดว่า agent ใช้ shell ไหนจริง (PowerShell tool / Git Bash ห่อ powershell)
3. ทุกจุด "ถามผมก่อน / รอผมอนุมัติ / ไม่แน่ใจให้ถาม" → **runner เป็นผู้ตัดสิน ไม่ต้องรอใคร**: ใช้หัวข้อ 🧑 ของ LAB นั้นใน `PROMPTS.md` ถ้าไม่มี ให้ตัดสินใจอย่างที่ผู้เรียนที่ระวังตัวจะทำ แล้วจดในหัวข้อ **"ตัดสินแทนผู้เรียน"** (คำถาม | คำตอบที่ใช้ | ที่มา 🧑/ตัดสินเอง | เหตุผล) · ห้ามถามผู้สั่งงานเรื่องที่ 🧑 ตอบไว้แล้ว
4. "Explore subagent" → ใช้ Agent ชนิด Explore จริงถ้ามี ถ้าไม่มีให้อ่านเองแล้วจดว่าไม่ได้ใช้
5. คำตอบสรุปที่ "จะแสดงให้ผู้เรียนเห็นในแชท" (ตารางท้ายพรอมต์) ต้องคัดลงไฟล์ result ด้วย
6. **timeout:** คำสั่งที่พรอมต์เขียนว่า "นาน" (docker build · `npm ci && npm run build` · `compose up --build` · `npm run test:all` · `playwright install`) ให้ตั้ง timeout ≥ 10 นาที หรือรันเบื้องหลังแล้วรอจนจบ · ห้ามสั่งซ้ำระหว่างรอ · ถ้า agent (แบบ B) รันซ้ำเพราะ timeout ให้จดเป็นข้อเสนอแก้พรอมต์

## กติกาความปลอดภัย (บังคับ)

1. **ห้าม git ที่เปลี่ยนสถานะ** (commit, stash, checkout, reset, branch, merge, rebase, clean, apply) · อ่านได้ (`git status` `git log` `git diff` และ `git diff --no-index` ที่พรอมต์สั่ง)
2. **ห้าม Playwright MCP** (ตั้งเป็นโหมด `--extension` เกาะ Chrome ตัวจริงของผู้ใช้) · ทุกงานเบราว์เซอร์ใช้ Playwright **headless** ในสคริปต์ node หรือ `@playwright/test` · สคริปต์ที่พรอมต์ไม่ได้สั่งให้อยู่ใน `w/` (เช่นอัดวิดีโอ/ถ่ายภาพเพิ่มเพื่อทำรูป) ให้อยู่ใน `../tools/labN/` (ติดตั้ง `playwright@1.63.0` ใน `../tools/` เอง) · สคริปต์ที่พรอมต์สั่งอยู่ใน `w/rea/scratch/` ตามพรอมต์ (ใช้ `w/rea/node_modules`)
3. ห้ามลบ cookie · ห้ามแตะ Chrome/โปรไฟล์ของผู้ใช้ · ห้ามแตะ container `multi-account-devtool` และ volume `ai-accounts` · ห้ามพิมพ์ secret
4. container ที่แตะได้: `pawpantry05` (compose project `pawpantry05` ของ `w/petshop`) และ container `--rm` ของ `rea-lab:6.4.0` / `node:24-alpine` ที่พรอมต์สั่ง · **ห้ามแตะ container/project ของบทอื่น** (`petshop` บท 02/03 · `sabai-*` บท 04 · `sabai06-*` บท 06) ถ้าขวางพอร์ตให้ถามผู้สั่งงาน
5. ห้ามอ่านไฟล์นอก `w/` ยกเว้น `../design/PROMPTS.md` (เฉพาะ LAB ที่ได้รับ) · `../design/RUNNER.md` · `../tools/`
6. ปฏิบัติตามข้อห้ามในวงเล็บของพรอมต์เคร่งครัด (เช่น LAB 5 ขั้นที่ 1 ห้ามเปิดโค้ดใน `petshop/` · ไฟล์ใหญ่ใน `out/` ห้ามเปิดตรง ๆ) · ถ้าเผลอละเมิด ให้จดใน result ตามจริง
7. **ห้ามแต่งตัวเลข** ทุกค่าใน result ต้องมาจากคำสั่งที่รันจริงหรือนับจากไฟล์ (grep/Measure-Object) · รันไม่ได้ให้เขียนว่ารันไม่ได้เพราะอะไร
8. จบ LAB: เว็บ `pawpantry05` **เปิดค้างไว้** (LAB ถัดไปใช้) · จบ LAB 10 หรือเมื่อผู้สั่งงานบอก (เช่นต้องคืนพอร์ต 4000 ให้บท 06): `docker compose down` ใน `w/petshop` (ลบเฉพาะ project `pawpantry05`) · ไม่ลบ image `rea-lab:6.4.0`
9. ทุก LAB จดว่า agent **เลี่ยง deny ไปเขียนไฟล์ต้องห้ามผ่าน shell** ไหม (`Set-Content` `Out-File` `>` `sed -i` กับไฟล์เดิมใน `e2e-legacy/` หรือ `TEST-DATA.md`) · ตรวจด้วย `git diff --stat -- e2e-legacy TEST-DATA.md` (อ่านอย่างเดียว · ถ้า `w/` ไม่ใช่ git repo ให้เทียบ SHA-256 กับตอนเริ่ม LAB)

## งานเพิ่มเฉพาะบทนี้

| LAB | ต้องทำ/จดเพิ่ม |
|---|---|
| 0 | (ก) ทางหลัก D7 อยู่ในพรอมต์แล้ว (probe `http://petshop:3000` ใน `pawpantry05_default`) · (ข) **ทางสำรอง `host.docker.internal:4000` ทดสอบ 2 ชั้น** แล้วจดผลทั้งคู่: ① `docker run --rm --entrypoint node rea-lab:6.4.0 -e "fetch('http://host.docker.internal:4000/api/health').then(r=>r.text()).then(console.log)"` ② คัด `w/rea/scenario-coupon.json` ไป `w/out/scenario-hdi.json` แก้ `start_url.url` เป็น `http://host.docker.internal:4000/` แล้ว `powershell -NoProfile -ExecutionPolicy Bypass -File .\rea\rea.ps1 -Out out\scenario-hdi.json.out capture-browser-scenario /work/out/scenario-hdi.json --json` (**ไม่ใส่** `-Network`) → `node rea\rea-summarize.mjs out\scenario-hdi.json.out` จด `steps_completed` (ถ้า Chromium ต่อ IPv6 ไม่ได้จะเห็นที่นี่) · (ค) `Get-ExecutionPolicy -List` ของเครื่อง runner · (ง) ถ้าผู้สั่งงานให้ build image: จดเวลาและขนาด (`docker image ls rea-lab`) |
| 1 | เปิดเซสชันใหม่ใน `w/` แล้วสั่งแก้ 1 บรรทัดใน `e2e-legacy/tests/01-home.spec.ts` (ต้องถูกปฏิเสธ) และสร้าง `e2e-legacy/tests/new/_probe.spec.ts` (ต้องสร้างได้ แล้วลบทิ้ง) จดข้อความที่ได้ · ตรวจว่า `CLAUDE.md` ไม่มี `@CODEBASE-MAP.md` |
| 2, 9 | ทุกคำสั่ง REA: exit code · เวลา wall-clock · ขนาดไฟล์ผล (`(Get-Item x).Length`) · evidence_id 8 ตัวแรก · ถ้า `rea-input.mjs`/`rea-summarize.mjs` ทำงานผิดให้จด input/ผลที่ได้ (ห้ามแก้ helper ใน `w/rea/` เอง ให้เขียนใน "ข้อเสนอแก้พรอมต์") |
| 3 | `docker network ls` จดชื่อ network ของเว็บ · ถ้าไม่ใช่ `pawpantry05_default` คือข้อเสนอแก้ระดับ H · จด URL ที่ REA เห็นใน scenario (`petshop:3000`) |
| 5 | จดว่า agent รู้ต้นเหตุ (ไฟล์:บรรทัด) ก่อนขั้นที่ 3 ไหม และรู้จากอะไร (CODEBASE-MAP · CLAUDE.md · เปิดโค้ดเอง) |
| 4, 8, 10 | ผล Playwright แยกเบราว์เซอร์ (passed / failed / expected-fail / flaky) + เวลา จาก reporter `list` · ถ้ามี flaky ให้รันซ้ำ `--repeat-each=3` เฉพาะข้อนั้น |
| 5, 8 | อัดวิดีโอ headless (`recordVideo` 1280×800) ของ test BUG-01 ข้อหลัก (ตอนแดง) และ TC ค่าขอบห่อของขวัญ (ตอนเขียว) เก็บ `../design/shots/lab5-bug01.webm` `lab8-gift-boundary.webm` (ผู้ทำรูปแปลงเป็น GIF ทีหลัง) |
| 6 | จดว่า BUG-01.md แนะนำวิธีไหน และผู้เรียนตอบอะไร (ตามหัวข้อ 🧑) · ถ้า agent แก้แบบเปลี่ยนเครื่องหมายอย่างเดียว **ไม่ต้องแก้ให้** ปล่อยไปแล้วจดผลใน LAB 8 ตามจริง |
| 9 | เทียบตาราง 4 ทิศกับ `REA-FEASIBILITY` ไม่ได้ (ห้ามอ่าน) → จดตัวเลขดิบทุกคู่ให้ผู้ตรวจเทียบเอง |
| ทุก LAB | เวลาที่ใช้ทั้ง LAB (นาที) แยก "เวลาเครื่อง" (build/test/REA) กับ "เวลา agent" ถ้าแยกได้ |

## สิ่งที่ต้องส่ง: `../design/results/LAB<N>_RESULT.md` (ภาษาไทย)

```markdown
# LAB N_RESULT · <ชื่อ LAB>
| หัวข้อ | ค่า |
|---|---|
| เวลาเริ่ม · จบ · ใช้ไป | 2026-10-12 14:02 · 14:19 · 17 นาที (เครื่อง ~9 · agent ~8) |
| cwd ของเซสชัน / settings มีผลไหม | w/ · ✅ |
| ไฟล์ที่สร้าง/แก้ | … (นับบรรทัด) |
| สคริปต์ชั่วคราว | rea\scratch\… · ../tools/labN/… |
| โหมดการรัน · shell ที่ agent ใช้จริง | A หรือ B (`LAB<N>_t*.txt`) · PowerShell tool / Git Bash ห่อ powershell |
| timeout / รันซ้ำ | คำสั่งยาวที่ตั้ง timeout หรือรันเบื้องหลัง · มีการสั่งซ้ำไหม |
| สถานะเว็บ | pawpantry05 healthy · build ล่าสุดเวลา … |
| ข้อมูลทดสอบ | reset กี่ครั้ง · ผู้ใช้ที่ใช้ |
## ข้อห้ามที่ทำตาม (และที่พลาด ถ้ามี)
## คำตอบสรุปที่แสดงในแชท      ← blockquote ตารางท้ายพรอมต์ตรงตัว
## ตัวเลขสำคัญ (นับจากไฟล์จริง พร้อมคำสั่งที่ใช้นับ)
## คำสั่งที่รัน (REA/docker/playwright: คำสั่ง | exit | เวลา | ขนาดผล)
## ตัวอย่างแถวเด่น 3–6 แถว (สำหรับ README)
## ตัดสินแทนผู้เรียน (คำถาม | คำตอบ | ที่มา 🧑/ตัดสินเอง | เหตุผล)
## ข้อสังเกต 👀 (บทเรียนจากรอบจริง ไม่ใช่สรุปผลซ้ำ)
## ปัญหา / วิธีแก้
## ข้อเสนอแก้พรอมต์ (ระดับ H = ทำต่อไม่ได้/ผลผิด · M = ได้ผลแต่สับสน · m = ถ้อยคำ)
## ภาพที่ควรใช้ใน README (../design/shots/labN-*.png 1280×800 + คำอธิบาย 1 บรรทัด)
```

- ภาพ: ถ่ายด้วย Playwright headless 1280×800 เก็บ `../design/shots/labN-<slug>.png` (ถ้าพรอมต์ให้เก็บใน `out\shots\` ให้คัดลอกมาด้วย) · ภาพตารางผลไม่ต้องทำ (ผู้ทำรูปทำจาก result)
- ห้ามใส่รหัสผ่าน/cookie/อีเมลจริงใน result และภาพ (บัญชี demo ใน TEST-DATA.md เขียนชื่อได้ แต่ไม่ใส่รหัสในตารางผล)

## จบงานแต่ละ LAB

พิมพ์สรุป ≤ 15 บรรทัด: LAB · เวลา · ไฟล์ที่ได้ · ตัวเลขหลัก · ปัญหา · ข้อเสนอแก้พรอมต์ระดับ H (ถ้ามี) · สถานะเว็บ
