# LAB 0 RESULT · บท 06 · เช็กเครื่อง + พอร์ตที่ Windows จอง

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 09:33:05 (+07) |
| เวลาจบ | 2026-10-12 09:36 (โดยประมาณ) |
| เวลาที่ใช้ | ~3 นาที (ตรวจโฟลเดอร์ตั้งต้น ~0.5 นาที + คำสั่ง LAB 0 ~1.5 นาที รวม `mcp doctor` 3.4 วินาที + เขียนผล) |
| ไฟล์ที่สร้าง/แก้ใน w/ | **ไม่มี** (`git status --short` ใน w/ = 0 บรรทัด ทั้งก่อนและหลัง) |
| ไฟล์นอก w/ | `design/results/LAB0_RESULT.md` · `design/shots/lab0-checklist.txt` |
| สคริปต์ชั่วคราว (`tools/lab0/`) | ไม่มี |
| สถานะเว็บตอนจบ | ยังไม่เปิด (LAB 0 อ่านอย่างเดียว · ห้ามเริ่ม container) |
| ข้อมูลทดสอบ | — (ยังไม่มี db) |
| พอร์ตที่ใช้จริง | runner บท 06 ใช้ **WEB_PORT=4100 · DB_PORT=5533** (BRIEF D10 · 4000 ถูก container `pawpantry05` ของ runner บท 05 ใช้อยู่) · ค่าที่ผู้เรียนเห็นใน README = **4000 / 5433** · compose รองรับแล้ว: `"${WEB_PORT:-4000}:3000"` และ `"${DB_PORT:-5433}:5432"` |
| คำสั่งเปิดเซสชัน / โหมดสิทธิ์ | mode A: runner (Claude Code agent) ทำตามพรอมต์เองโดยตรง · cwd ของ process ไม่ใช่ w/ จึงรันทุกคำสั่งด้วย `Set-Location C:\t\work\b2run\w` / path เต็ม · ไม่ได้เปิด `yolo.cmd`/`claude -p` (LAB 0 ไม่ต้องทดสอบ fresh session) · ใช้ PowerShell tool สำหรับคำสั่งของพรอมต์ · Git Bash สำหรับการตรวจโฟลเดอร์ตามตาราง RUNNER §1 |

## ตรวจโฟลเดอร์ตั้งต้น (RUNNER §1 · Git Bash)

| # | ตรวจ | ผลจริง | ผ่าน |
|---|---|---|---|
| 1 | `ls -a /c/t/work/b2run/w` | `.git CHANGE-REQUESTS EXAM.md db e2e-legacy fast_track img tools web` · ไม่มี `_solution` | ✅ |
| 2 | `sha256sum -c --quiet /c/t/work/b2prep/MANIFEST.sha256` (manifest 180 บรรทัด) | ไม่มีบรรทัด FAILED · `exit=0` | ✅ |
| 3 | `grep -rniE "bug_mode\|bug-mode\|bugmode\|flags" w/web --exclude-dir=node_modules --exclude-dir=.next` | ไม่มีผล (grep exit=1) | ✅ |
| 4 | `grep -h container_name web/compose.yaml db/compose.yaml` | `sabai06-web` · `sabai06-db` | ✅ |
| 5 | `find w/CHANGE-REQUESTS -type f \| wc -l` | `12` | ✅ |

ผ่านครบ 5/5 → ไปต่อ LAB 0 ได้ · ข้อสังเกต: w/ มี `img/` (ภาพ concept-01…05) และ `fast_track/` ด้วย ทั้งที่ RUNNER §1 บอกว่า orchestrator คัดลอก "ยกเว้น `img/`" · ทั้งสองไม่อยู่ใน MANIFEST (img 0 บรรทัด · fast_track 4 บรรทัดเป็นรายการ manifest จริง) จึงไม่ทำให้ข้อ 2 ล้ม และไม่กระทบ LAB · `.git` มีอยู่ตาม D11 (commit `d617d68 starting folder (chapter 06)`)

## 2. ข้อห้ามที่ทำตาม / จุดที่ทำต่างจากพรอมต์

- อ่านอย่างเดียว: ไม่ติดตั้ง ไม่แก้ไฟล์ ไม่หยุด/เริ่ม container ใด ๆ (ไม่แตะ `pawpantry05`, `multi-account-devtool`, `deep_vision_5090_vllm`) · ไม่แก้ execution policy
- ไม่ใช้ git ที่เปลี่ยนสถานะ (ใช้แค่ `git rev-parse` `git status` `git log`)
- กฎใน `w/CLAUDE.md` / `w/.claude/settings.json`: ยังไม่มีไฟล์เหล่านี้ใน w/ ตอน LAB 0 (สร้างใน LAB 4) · ข้อห้ามของพรอมต์ runner บังคับเอง (self-enforced)
- **พอร์ต:** ข้อ 4 ของพรอมต์ตรวจ 4000,5433 ตรงตัว (เพื่อให้ได้ผลเหมือนผู้เรียน) และตรวจเพิ่ม 4100,5533 ที่ runner จะใช้จริง · ตั้งแต่ LAB 1 runner จะตั้ง `$env:WEB_PORT=4100` `$env:DB_PORT=5533` `$env:BASE_URL="http://localhost:4100"` · README ผู้เรียนให้เขียน 4000/5433
- ข้อ 8 "อยู่ใน git repo อื่นไหม": w/ เป็น repo ของตัวเอง (D11 · toplevel = w/ เอง) ไม่ใช่ repo อื่นที่ครอบ → ถือว่าพร้อม

## 3. คำตอบสรุปที่แสดงในแชท

> | รายการ | ผล | พร้อมไหม | ถ้าไม่พร้อมต้องทำอะไร |
> |---|---|---|---|
> | Docker | Engine 29.5.2 · Docker Desktop 4.75.0 · Compose v5.1.4 | ✅ | — |
> | Node.js | v26.7.0 (≥ 22.18) | ✅ | — |
> | npm / git | npm 12.2.0 · git 2.50.1.windows.1 | ✅ | — |
> | ช่วงพอร์ตที่ Windows จอง | 3000 อยู่ในช่วง **2970–3069** · 4000 และ 5433 ไม่อยู่ในช่วงใด | ✅ | — |
> | ทำไมใช้ 4000 | Windows จองพอร์ตช่วง 2970–3069 ไว้ให้ระบบ (Hyper-V/WinNAT) Docker จึงเปิดพอร์ต 3000 บนเครื่องไม่ได้ · บทนี้เลยให้เว็บออกที่ 4000 (ในคอนเทนเนอร์ยังเป็น 3000) | ℹ️ | — |
> | พอร์ต 4000 | **มีผู้ใช้อยู่**: container `pawpantry05` (บท 05) `0.0.0.0:4000->3000` (Get-NetTCPConnection เห็น `com.docker.backend` และ `wslrelay`) | ⚠️ | ผู้เรียน: ปิดเว็บบท 05 ก่อน · runner: ใช้ 4100/5533 แทน (D10) |
> | พอร์ต 5433 | ว่าง | ✅ | — |
> | พอร์ต 4100 / 5533 (runner) | ว่าง · ไม่อยู่ในช่วงจอง | ✅ | — |
> | container/volume ชื่อ sabai | container: ไม่มี · volume: `sabai-pgdata`, `spa_sabai-db-data` (บทก่อน) | ✅ | ไม่ต้องทำ (บทนี้ใช้ `sabai06-pgdata` ไม่ชน) |
> | REA | `rea-lab:6.4.0` = `sha256:2012d907…5123` · `mcp doctor` healthy: true · **exit 0** · tools 170/170 · prompts 6/6 | ✅ | — |
> | Execution policy | MachinePolicy Undefined · UserPolicy Undefined · Process Bypass · CurrentUser **RemoteSigned** · LocalMachine Undefined | ✅ | ไม่ต้องแก้ · บทนี้เรียก .ps1 ด้วย `-ExecutionPolicy Bypass -File` |
> | โฟลเดอร์บท | web/ db/ e2e-legacy/ tools/ CHANGE-REQUESTS/ ครบ · `git rev-parse --show-toplevel` = `C:/t/work/b2run/w` (repo ของโฟลเดอร์นี้เอง) | ✅ | — |

## 4. ตัวเลขสำคัญ (นับจากผลจริง)

- ช่วงพอร์ตที่จอง (tcp): 23 ช่วง · ช่วงที่ครอบ 3000 = **2970–3069** · ข้างเคียง 2870–2969 และ 3070–3169 ก็จอง (ช่วง 2870–3169 จองต่อเนื่อง) · 4000, 4100, 5433, 5533 ไม่อยู่ในช่วงใด · คำสั่ง `netsh interface ipv4 show excludedportrange protocol=tcp`
- `docker ps`: 3 container ทำงาน (`pawpantry05` 4000, `multi-account-devtool` 2223/8886, `deep_vision_5090_vllm` 22022/8650)
- `mcp doctor`: 3.4 วินาที · exit 0 · tools 170 · prompts 6 · catalog digest `85d80276…7d72a`
- MANIFEST: 180 ไฟล์ ตรงทั้งหมด
- CHANGE-REQUESTS: 12 ไฟล์

## 5. ตัวอย่างแถวเด่นสำหรับ README

- "ช่วงพอร์ตที่ Windows จอง | 3000 อยู่ในช่วง 2970–3069 · 4000/5433 ไม่อยู่ | ✅"
- "REA | rea-lab:6.4.0 · mcp doctor exit 0 (tools 170/170) | ✅"
- "Execution policy | CurrentUser RemoteSigned | ✅ ไม่ต้องแก้ เพราะใช้ Bypass"
- "พอร์ต 4000 | ถูกบท 05 ใช้อยู่ | ⚠️ ปิดเว็บบท 05 ก่อน" (กรณีที่ผู้เรียนเปิดบท 05 ค้างไว้ · น่าใส่เป็นข้อ "ถ้าเจอปัญหา")

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบที่เลือก | เหตุผล |
|---|---|---|
| 4000 ไม่ว่าง (ใช้โดย `pawpantry05`) จะทำอะไร | ไม่ปิด container (พรอมต์ห้าม) · runner ใช้ 4100/5533 | BRIEF D10 · 4000 เป็นของ runner บท 05 |
| โฟลเดอร์อยู่ใน git repo แล้ว (rev-parse ไม่ error) ต้องย้ายไป `C:\work\sabai06` ไหม | ไม่ย้าย | repo นั้นคือ w/ เอง (D11) ไม่ใช่ repo อื่นที่ครอบโฟลเดอร์ |

## 7. ข้อสังเกต 👀

- ข้อ 8 ของพรอมต์ใช้ `git rev-parse --show-toplevel` แยก "อยู่ใน repo อื่น" ไม่ได้ ถ้าผู้เรียน clone บทมาเป็น repo ของตัวเอง (หรือ init เองแล้ว) คำสั่งจะคืน path ของโฟลเดอร์บทเอง · ต้องเทียบว่า toplevel = โฟลเดอร์ปัจจุบันหรือโฟลเดอร์แม่ (ในเครื่องผู้เรียนที่ clone repo คอร์ส จะได้ path ของ repo คอร์ส → ถือว่า "อยู่ใน repo อื่น" ถูกต้อง)
- Execution policy ระดับ `Process` = `Bypass` มาจากวิธีที่ PowerShell tool ของ agent เปิด process · ผู้เรียนที่เปิด PowerShell เองจะเห็น `Undefined` ในแถวนี้ · AI อาจเข้าใจผิดว่าเครื่องตั้ง Bypass ไว้ถาวร
- Get-NetTCPConnection ไม่บอกว่าเป็น container ไหน (เห็นแค่ `com.docker.backend`/`wslrelay`) ต้องใช้ `docker ps` ประกอบจึงรู้ว่าเป็น `pawpantry05`

## 8. เจอระหว่างทาง (นอก CR)

- ไม่มี (LAB 0 ไม่แตะระบบ)

## 9. ปัญหาที่เจอ / วิธีแก้

- พอร์ต 4000 ถูกใช้โดย runner บท 05 (คาดไว้แล้วตาม D10) → ใช้ 4100/5533 ตั้งแต่ LAB 1
- ระหว่างอ่านหัวข้อ LAB 0 ช่วงบรรทัดที่อ่านติดบรรทัด "ผลที่คาด" มาด้วยก่อนเขียน result (ผิด RUNNER §2 เล็กน้อย) · ตัวเลขทุกตัวข้างบนมาจากคำสั่งที่รันจริง ไม่ได้ปรับตามผลที่คาด

## 10. ข้อเสนอแก้พรอมต์

- ข้อ 8: เปลี่ยนเป็น "ถ้า `git rev-parse --show-toplevel` ได้ path ที่**ไม่ใช่**โฟลเดอร์นี้ = อยู่ใน repo อื่น" เพื่อไม่ให้ผู้ที่ได้บทมาเป็น repo เดี่ยวตกใจ
- ข้อ 4: เพิ่ม "ถ้าไม่ว่าง ให้บอกด้วยว่าเป็น container ไหนจาก `docker ps`" และในหัวข้อ "ถ้าเจอปัญหา" ใส่ทางแก้กรณีเว็บบท 05 เปิดค้างที่ 4000 (`docker compose -f ...05.../compose.yaml down` หรือ `$env:WEB_PORT`)
- ข้อ 7: บอกว่าแถว `Process` อาจเป็น Bypass ถ้าเปิดผ่านเครื่องมือ ไม่ใช่ค่าถาวรของเครื่อง

## 11. ภาพที่ควรใช้

- `design/shots/lab0-checklist.txt` = ตารางผลจริง สำหรับทำภาพ result ของ LAB 0 (ไม่มี png ใน LAB นี้)

### เทียบกับผลที่คาด

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| ตารางในแชท 10–11 แถว | 12 แถว (เพิ่มแถว "ทำไมใช้ 4000" และ "พอร์ต 4100/5533 ของ runner") · ถ้าตัดแถว runner = 11 | ✅ (เกิน 1 แถวเพราะ runner) |
| ช่วงจอง 2970–3069 ครอบ 3000 | 2970–3069 ครอบ 3000 | ✅ |
| 4000 และ 5433 ไม่อยู่ในช่วงจอง | ไม่อยู่ | ✅ |
| Node v26 | v26.7.0 | ✅ |
| rea-lab 6.4.0 | มี `sha256:2012d907…` | ✅ |
| `mcp doctor` exit 0 | exit 0 (healthy, 170/170 tools) | ✅ |
| execution policy เครื่องผู้สอน `CurrentUser RemoteSigned` | CurrentUser RemoteSigned (+ Process Bypass จาก tool) | ✅ |
| ไม่มีการแก้ไฟล์ใด ๆ | `git status --short` = 0 บรรทัด | ✅ |
| ไปต่อได้: 4000/5433 ว่าง | 4000 **ไม่ว่าง** (pawpantry05 ของ runner บท 05) · 5433 ว่าง · runner ใช้ 4100/5533 ที่ว่างแทน | ⚠️ ต่างเพราะรันขนานกับบท 05 (ไม่ใช่ปัญหาของบท) |
| โฟลเดอร์ไม่อยู่ใน repo อื่น | toplevel = w/ เอง (D11) | ✅ (ตีความตามข้อ 7) |
