# LAB 4 RESULT · CLAUDE.md + รั้ว (บท 06 สบายใจ สปา)

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 10:14:52 |
| เวลาจบ (งานตามพรอมต์ ส่วน 1+2) | 10:17:25 · เขียน result เสร็จ ~10:20 |
| เวลาที่ใช้ | ~3 นาทีตามนาฬิกา (ส่วน 1: อ่าน 3 ไฟล์ + ตรวจคำสั่ง/สคริปต์ + เขียน 4 ไฟล์ + commit · ส่วน 2: เซสชันใหม่ 15.2 วิ 4 turn) — runner เขียนเอง ไม่ได้รอ build/test (LAB นี้ไม่รันชุดทดสอบ) · ผู้เรียนจริงน่าจะ 10–15 นาทีเพราะต้องอ่านทวนไฟล์ |
| ไฟล์ที่สร้าง/แก้ใน w/ | สร้าง `CLAUDE.md` (45 บรรทัด) · `.claude/settings.json` (5) · `docs/IMPACT-TEMPLATE.md` (60) · `docs/ORACLE-CHANGES.md` (11) · **ไม่แก้โค้ด** ใน `web/` `db/` `e2e-legacy/` |
| git | commit `8e2ffc6` `docs: CLAUDE.md + รั้ว` · **8 ไฟล์ 553 บรรทัด** (4 ไฟล์ของ LAB นี้ + `SYSTEM-MAP.md` `docs/SPEC-GAPS.md` `docs/REA-INVENTORY.md` `HANDOVER-CHECK.md` ที่ค้างไม่ได้ commit จาก LAB 1–3 · ดูข้อ 6) · `git status --short` หลัง commit = ว่าง |
| สคริปต์ชั่วคราว / log | `tools/lab4/`: `prompt-part2.txt` (พรอมต์ส่วน 2 ตรงตัว) · `part2-stream.jsonl` (stream-json ของเซสชันใหม่ 24.6 KB) · `part2-stderr.txt` (ว่าง) · `cfg-before.sha` (SHA-256 ของ `e2e-legacy/playwright.config.ts` ก่อนทดสอบ) |
| ภาพ / ไฟล์ส่ง | `design/shots/lab4-deny-test.txt` (ข้อความปฏิเสธจริง + โหมดสิทธิ์จริง) |
| สถานะเว็บตอนจบ | `sabai06-web` + `sabai06-db` เปิดค้าง healthy · `GET http://localhost:4100/api/health` → `{"ok":true,"db":true}` |
| ข้อมูลทดสอบ | **reset 1 ครั้ง** (ตรวจว่าคำสั่ง reset ที่เขียนใน CLAUDE.md ใช้ได้จริง) → `{"ok":true,"now":"2026-10-10T10:00:00+07:00"}` · DB กลับเป็น seed (B14 ของ LAB 2 หาย · B05 กลับเป็น confirmed) |
| พอร์ตที่ใช้จริง | เว็บ **4100** · db **5533** (D10) · CLAUDE.md เขียนค่าผู้เรียน **4000** + บรรทัดวิธีตั้ง `$env:WEB_PORT`/`$env:BASE_URL` เมื่อพอร์ตไม่ว่าง (ไม่ต้องแปลงตอนทำ README) |
| เซสชัน / โหมดสิทธิ์ | ส่วน 1: runner (Agent tool) แทนเซสชันผู้เรียน โหมด A · ส่วน 2: **เซสชันใหม่จริง** `cat tools/lab4/prompt-part2.txt \| yolo.cmd -p --permission-mode acceptEdits --model opus --effort medium --output-format stream-json --verbose` (cwd `w/`) · session `d5fa0120-…` · **โหมดที่มีผลจริง = `bypassPermissions`** (event `init`) เพราะ `yolo.cmd` ใส่ `--dangerously-skip-permissions` เองและทับ `--permission-mode acceptEdits` · เรียก yolo 1 ครั้ง (พรอมต์ไม่มีการทดสอบ "สร้างไฟล์ได้" จึงไม่ใช้ครั้งที่ 2) |

## 2. ข้อห้ามที่ทำตาม และจุดที่ทำต่างจากพรอมต์

- ไม่แก้โค้ดใน `web/` `db/` · ไม่เปิด `_solution/` (ไม่มีใน w/) · ไม่เปิด `CHANGE-REQUESTS/answers/`
- "รันคำสั่งด้วย PowerShell": คำสั่งที่เขียนลง CLAUDE.md ตรวจด้วยเครื่องมือ PowerShell (health · reset ด้วย `-Body '{}'` · นับบรรทัด) · การอ่าน/นับ/สร้างโฟลเดอร์ `.claude/` ใช้ Git Bash (ไม่เปลี่ยนสถานะ repo) · ไฟล์เขียนด้วย Write (UTF-8 ไม่มี BOM) · `settings.json` ตรวจด้วย `JSON.parse` ผ่าน
- git: ใช้ git จริงตาม D11 เพราะพรอมต์สั่ง `git add` + `commit` เอง (ไม่ใช้ snapshot ของ RUNNER §4)
- รั้วใน `w/CLAUDE.md` / `.claude/settings.json` ของ LAB นี้: runner (ส่วน 1) self-enforce — ไม่แตะ `e2e-legacy/**` ด้วย Edit/Write · ส่วน 2 รั้วถูกบังคับโดย Claude Code จริงในเซสชันใหม่
- ⚠️ **ต่างจาก RUNNER §2**: RUNNER กำหนดให้ทดสอบ deny ใน `default`/`acceptEdits` ห้าม bypass · แต่ orchestrator อนุญาตเฉพาะ `yolo.cmd` ซึ่งบังคับ `--dangerously-skip-permissions` → ได้ `bypassPermissions` แม้ใส่ `--permission-mode acceptEdits` · ผล: deny **ยังปฏิเสธจริง** ในโหมด bypass (เงื่อนไขเข้มกว่า default) · ยังไม่ได้ยืนยันซ้ำในโหมด default ด้วย `claude` ตรง (ถ้าต้องการ ให้ orchestrator สั่งเพิ่ม)
- ⚠️ ความบริสุทธิ์ของการเทียบผล: ตอนเปิด LAB 4 runner อ่าน PROMPTS.md บรรทัด 141–179 ทีเดียว จึง**เห็นบรรทัด "ผลที่คาด" (บรรทัด 175) ก่อนลงมือ** โดยไม่ตั้งใจ · ตัวเลขทุกตัวด้านล่างนับจากไฟล์/ผลจริง ไม่ได้ปรับตามผลที่คาด และข้อความปฏิเสธคัดจาก stream-json ของเซสชันใหม่ (ไม่ได้พิมพ์เอง)
- ไม่แตะ `pawpantry05` (4000) และ `exref-*` (4200/5633)

## 3. คำตอบสรุปที่แสดงในแชท

**ส่วนที่ 1** (runner แทนผู้เรียน)

> commit `8e2ffc6` `docs: CLAUDE.md + รั้ว` · 8 ไฟล์ (+553)
>
> | ไฟล์ | หัวข้อ | จำนวนบรรทัด |
> |---|---|---|
> | `CLAUDE.md` | รันยังไง (เปิดระบบ · พอร์ต · reset · check-rules · e2e api+chromium · test:all · ผลอ้างอิงตอนรับมอบ) · แผนที่ `@SYSTEM-MAP.md` · ห้ามแตะ · กติกาการแก้ (9 ข้อ) · กับดัก (T1–T13 ย่อ 9 บรรทัด) · เอกสารเก่า `@docs/SPEC-GAPS.md` | 45 |
> | `.claude/settings.json` | `permissions.deny = ["Edit(e2e-legacy/**)"]` | 5 |
> | `docs/IMPACT-TEMPLATE.md` | หัวตาราง CR · 1 คำถามถึงร้าน · 2 ตารางผลกระทบ (ไฟล์ \| เหตุผล (CR) \| ใครเรียกใช้ grep \| หน้าจอ/API/แชท \| ตาราง DB \| เทสต์ที่ต้องรันซ้ำ \| ความเสี่ยง) + เช็กลิสต์กับดัก · 3 ค่าที่คาดหวังใหม่ + วิธีคิด + แหล่ง · 4 เทสต์ใหม่ (ต้องแดง) · 5 วิธีถอยกลับ · 6 ผลหลังแก้ | 60 |
> | `docs/ORACLE-CHANGES.md` | กติกา 3 บรรทัด · ตาราง วันที่ \| ไฟล์เทสต์ \| เคส \| ค่าเดิม → ใหม่ \| CR ที่อนุญาต \| ผู้อนุมัติ (ว่าง) | 11 |

**ส่วนที่ 2** (คัดจากเซสชันใหม่ตรงตัว)

> Edit ถูกรั้วปฏิเสธ ไฟล์จึงไม่เปลี่ยน ไม่ต้องลบบรรทัดคืน และผมไม่ได้ลองใช้ PowerShell หรือ shell แก้แทน
>
> | ทดสอบ | ผล | ข้อความจริง | git status |
> |---|---|---|---|
> | ใช้ Edit เพิ่ม `// test fence` ที่บรรทัด 1 ของ `e2e-legacy/playwright.config.ts` | ❌ ถูกปฏิเสธ (รั้วทำงาน) | `File is in a directory that is denied by your permission settings.` | `git status --porcelain -- e2e-legacy/` ไม่มีผลลัพธ์ (exit 0) · `git status --short` ทั้ง repo ก็ว่าง |
>
> - รั้ว deny ใน `.claude/settings.json` กันเครื่องมือแก้ไฟล์ปกติ (Edit) ได้จริง
> - แต่การอ่านไฟล์ไม่ถูกกัน: ผมอ่านไฟล์นี้ได้ (บรรทัด 1 = `import { defineConfig, devices } from '@playwright/test';`)
> - รั้วนี้ไม่ได้ทดสอบว่ากันคำสั่ง PowerShell หรือ shell ด้วยหรือเปล่า

ลำดับเครื่องมือในเซสชันใหม่: `Read` (3 บรรทัดแรก · ผ่าน) → `Edit` (**error** `<tool_use_error>File is in a directory that is denied by your permission settings.</tool_use_error>`) → `PowerShell` `git status --porcelain -- e2e-legacy/; git status --short` (ว่าง) · `permission_denials` ใน result = 1 รายการ (Edit)

## 4. ตัวเลขสำคัญ

| ตัวเลข | ค่า | คำสั่งที่ใช้นับ |
|---|---|---|
| บรรทัด `CLAUDE.md` | **45** (≤ ~60) · หัวข้อ `##` 6 | `wc -l CLAUDE.md` · `grep -c "^## " CLAUDE.md` |
| กติกาการแก้ใน CLAUDE.md | 9 ข้อ (impact · แดงก่อน · ป้าย [D]/[E] · migration · docker cp + psql -f · ไทย/PowerShell · งานนาน > 2 นาที · 3 ภาษา + แชท · เอกสารเก่าขัดโค้ด) + ห้ามแตะ 4 บรรทัด (down -v/volume · _solution/answers · oracle · clock()) | อ่านไฟล์ |
| import ใน CLAUDE.md | 2 (`@SYSTEM-MAP.md` 262 บรรทัด · `@docs/SPEC-GAPS.md` 35 บรรทัด) | `grep -n "^@" CLAUDE.md` |
| กฎ deny | **1** `Edit(e2e-legacy/**)` | `cat .claude/settings.json` |
| แม่แบบ | 2 ไฟล์: IMPACT-TEMPLATE 60 บรรทัด 6 หัวข้อ · ORACLE-CHANGES 11 บรรทัด ตาราง 6 คอลัมน์ 0 แถวข้อมูล | `wc -l` · `grep -n "^## "` |
| commit | `8e2ffc6` · 8 ไฟล์ · +553 | `git show --stat HEAD` |
| เซสชันทดสอบรั้ว | 15,219 ms · 4 turn · denial 1 · โหมด `bypassPermissions` · model `claude-opus-5-5` | `part2-stream.jsonl` (event `init` + `result`) |
| `playwright.config.ts` หลังทดสอบ | SHA-256 เท่าเดิม `595e9f56…` (`sha256sum -c` → OK) · `git status --short` ว่าง | `sha256sum -c tools/lab4/cfg-before.sha` |
| คำสั่ง reset ใน CLAUDE.md | ใช้ได้จริง: `{"ok":true,"now":"2026-10-10T10:00:00+07:00"}` (รันที่ :4100) | PowerShell `Invoke-RestMethod -Method Post … -ContentType 'application/json' -Body '{}'` |

## 5. ตัวอย่างแถวเด่นสำหรับ README

- รั้วจริง: `Edit e2e-legacy/playwright.config.ts` → *"File is in a directory that is denied by your permission settings."* · `git status` ว่าง
- กติกาป้ายแหล่ง (CLAUDE.md ข้อ 3): `[D:CR-0N]` = คำตอบร้าน · `[E ev_xxxxxxxx]` = หลักฐานระบบ ใช้ล็อกพฤติกรรมเดิมเท่านั้น · `[E]` ขัด `[D]` = ผู้ต้องสงสัยบั๊ก
- กติกา migration (ข้อ 4–5): `db/migrations/` ทางเดียว · รันซ้ำได้ · มีไฟล์ถอย · `docker cp` + `psql -v ON_ERROR_STOP=1 -f`
- กับดักย่อใน CLAUDE.md: T2 `TABLES` ใน `web/lib/server/testmode.ts:11-15` (ตารางใหม่ไม่ถูก reset) · T1 `room_id = 1` `booking.ts:290` `:376`
- IMPACT-TEMPLATE ตาราง 7 คอลัมน์ ตามพรอมต์ + เช็กลิสต์กับดัก T1–T13 + แถวผลก่อนแก้ 90/90 · 38/1/3

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบที่เลือก | เหตุผล |
|---|---|---|
| `git add` อะไรบ้าง (พรอมต์ไม่ระบุ) | `git add -A` → รวม `SYSTEM-MAP.md` `docs/SPEC-GAPS.md` `docs/REA-INVENTORY.md` และ `HANDOVER-CHECK.md` (modified) ที่ LAB 1–3 ไม่ได้ commit | CLAUDE.md import `@SYSTEM-MAP.md` `@docs/SPEC-GAPS.md` · ถ้า commit แค่ 4 ไฟล์ commit จะอ้างไฟล์ที่ไม่อยู่ใน repo · ไฟล์ผลรัน (`rea-out/` `test-report/` `node_modules/`) ถูก exclude ตั้งแต่ LAB 1 จึงไม่หลุดเข้า |
| CLAUDE.md เขียนพอร์ตไหน | 4000/5433 (ค่า compose) + 1 บรรทัดวิธีใช้ `$env:WEB_PORT` `$env:DB_PORT` `$env:BASE_URL` | ไฟล์นี้เป็นของโปรเจกต์ ใช้ได้ทุกเครื่อง · เครื่อง runner ใช้ 4100 ผ่าน env |
| `tests/golden/` ยังไม่มี (LAB 5 สร้าง) จะใส่ในกติกาไหม | ใส่ตามพรอมต์ | พรอมต์สั่งตรง ๆ · เป็นกติกาล่วงหน้า · ไม่ได้ใส่ใน deny (พรอมต์กำหนด deny 1 กฎ) |
| `settings.json` หรือ `settings.local.json` | `.claude/settings.json` (commit) | พรอมต์ระบุ · รั้วต้องตามไปกับ repo ให้ทุกคนในทีม |
| คำสั่ง e2e ใน CLAUDE.md ใส่ `--reporter=list` ไหม | ใส่ในชั้น 2 | LAB 1 พบว่าบรรทัดสรุปต้องแยก passed / test.fail เอง · list อ่านง่ายใน log · `test:all` ใช้ reporter ตาม config |
| คำสั่ง reset ใน PowerShell | `Invoke-RestMethod -Method Post -Uri … -ContentType 'application/json' -Body '{}'` | body เป็น ASCII ล้วน (ไม่ผิดกติกาภาษาไทย) · ตรวจแล้วได้ 200 |
| ไม่มีข้อไหนต้อง "ถามผมก่อน" | ไม่ได้หยุดถาม | ทุกข้อในพรอมต์ชัดพอ · ข้อที่ไม่ระบุจดในตารางนี้ |

## 7. ข้อสังเกต 👀

- **deny มีผลแม้โหมด bypass**: `yolo.cmd` (`--dangerously-skip-permissions`) ทับ `--permission-mode acceptEdits` จนได้ `bypassPermissions` แต่ `Edit(e2e-legacy/**)` ยังปฏิเสธ → สอนได้ว่า deny = รั้วแข็ง ไม่ขึ้นกับโหมด (แต่ RUNNER ต้องการพิสูจน์ในโหมด default — ยังไม่ได้ทำ)
- รั้วกันแค่เครื่องมือแก้ไฟล์: Agent **อ่าน** ไฟล์ใน `e2e-legacy/` ได้ปกติ และ Agent เองชี้ว่า "ไม่ได้ทดสอบว่ากัน PowerShell/shell" → PowerShell `Set-Content` ยังแก้ไฟล์ได้ถ้า Agent ฝ่าฝืน · ต้องพึ่งกติกาใน CLAUDE.md ("ห้ามใช้ shell แก้แทน") ควบคู่
- Agent ในเซสชันใหม่ทำตามพรอมต์ดี: ลอง Edit ครั้งเดียว ไม่พยายามอ้อมด้วย shell · ไม่มีอะไรต้องลบคืน
- `@SYSTEM-MAP.md` (~46 KB) ถูกโหลดเข้า context ทุกเซสชัน → เซสชันสั้น ๆ ก็มีต้นทุน token · ทางเลือก: อ้างเป็นชื่อไฟล์ "อ่านเมื่อจำเป็น" แทน @import
- กติกา oracle ครอบคลุม `check-rules.mjs` และ `tests/golden/` ด้วย แต่ deny กันแค่ `e2e-legacy/**` → 2 ที่นั้นอาศัยกติกาในข้อความอย่างเดียว
- ข้อความในพรอมต์ "Write(...) ใช้กับไฟล์ไม่ได้" ชวนสับสน (ฟังเหมือน Write ไม่ถูกกัน) · runner ไม่ได้ทดสอบ Write ในเซสชันใหม่ (ไม่อยู่ในพรอมต์)
- git เตือน `LF will be replaced by CRLF` ทุกไฟล์ตอน commit (core.autocrlf) — ไม่มีผลกับเนื้อหา แต่ผู้เรียนอาจตกใจ

## 8. เจอระหว่างทาง (นอก CR)

- ไม่มีบั๊กใหม่ของระบบเดิม (LAB นี้ไม่ได้ทดสอบระบบ) · ยืนยันซ้ำว่า `POST /api/test/reset` ไม่ต้องล็อกอินและตอบ 200 (= SPEC-GAPS G7 / HANDOVER H6 ที่จดไว้แล้ว)

## 9. ปัญหาที่เจอ / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| `yolo.cmd` บังคับ bypass ทำให้ทดสอบในโหมด default/acceptEdits ตาม RUNNER ไม่ได้ | ใส่ `--permission-mode acceptEdits` เพิ่มแล้วอ่านโหมดจริงจาก event `init` ของ `--output-format stream-json` → บันทึกตามจริง (`bypassPermissions`) · deny ยังมีผล |
| ส่งพรอมต์ภาษาไทยผ่าน `cmd.exe %*` อาจเพี้ยน | ส่งพรอมต์ทาง stdin (`cat prompt-part2.txt \| yolo.cmd -p …`) · เซสชันใหม่อ่านภาษาไทยถูก (ตอบตรงพรอมต์) |
| `Measure-Object -Line` ไม่นับบรรทัดว่าง (ได้ 39 แทน 45) | ใช้ `wc -l` เป็นตัวเลขทางการ |
| LAB 1–3 ทิ้งไฟล์ไม่ได้ commit | รวมเข้า commit นี้ (ข้อ 6) |

## 10. ข้อเสนอแก้พรอมต์

1. **ส่วน 1 ท้าย:** ระบุขอบเขต commit ชัด เช่น "git add -A (รวม SYSTEM-MAP.md และ docs/ ของ LAB 2–3 ที่ยังไม่ commit) แล้ว commit …" — หรือให้ LAB 3 commit แผนที่เอง · ไม่งั้น Agent อาจ add แค่ 4 ไฟล์ แล้ว CLAUDE.md อ้าง `@SYSTEM-MAP.md` ที่ไม่อยู่ใน repo
2. **ข้อ 3:** เปลี่ยน "(ใช้ Edit(...) เท่านั้น Write(...) ใช้กับไฟล์ไม่ได้)" เป็น "(กฎ Edit(...) กันทุกเครื่องมือแก้ไฟล์ของ Claude Code · อย่าเขียน Write(...)/Read(...))" ให้ไม่ตีความว่า Write ไม่ถูกกัน
3. **ส่วน 2:** เพิ่มบรรทัด "เปิดด้วย `claude` (โหมดปกติ) ห้ามใช้ `--dangerously-skip-permissions`" สำหรับผู้เรียน · และอาจเพิ่มแถวทดสอบ "อ่านไฟล์เดียวกันได้" + หมายเหตุว่ารั้วไม่กัน shell (Agent ในรอบนี้ชี้เองแล้ว)
4. **ข้อ 1:** พิจารณาบอกว่า `@SYSTEM-MAP.md` จะถูกโหลดทุกเซสชัน (ไฟล์ใหญ่) หรือให้อ้างเป็นลิงก์ธรรมดา
5. **RUNNER/orchestrator:** ถ้าต้องพิสูจน์ deny ในโหมด default ให้อนุญาตเรียก `claude.exe -p --permission-mode default` ตรง (ไม่ผ่าน yolo)

## 11. ภาพที่ควรใช้ + เทียบกับผลที่คาด

- `design/shots/lab4-deny-test.txt` — ข้อความปฏิเสธจริง + โหมดสิทธิ์จริง + git status (ใช้ทำภาพ/กล่องข้อความใน README)

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| `CLAUDE.md` ≤ ~60 บรรทัด | 45 บรรทัด · 6 หัวข้อ | ✅ |
| มีกติกาภาษาไทย/PowerShell | ข้อ 6 (node / `curl.exe --data-binary '@ไฟล์.json'` · ห้าม `Invoke-RestMethod -Body '<ไทย>'` · ตรวจด้วย SQL · ห้ามแก้ข้อมูลเพราะจอเพี้ยน) | ✅ |
| migration = ทางเดียว | ข้อ 4–5 (`db/migrations/` ทางเดียว · รันซ้ำได้ · ถอยได้ · db/init ไม่ใช่วิธี deploy · docker cp + psql -f) | ✅ |
| ป้าย [E]/[D] | ข้อ 3 | ✅ |
| `.claude/settings.json` 1 กฎ | `deny: ["Edit(e2e-legacy/**)"]` | ✅ |
| แม่แบบ 2 ไฟล์ | IMPACT-TEMPLATE (60) · ORACLE-CHANGES (11) | ✅ |
| ส่วน 2: แก้ไม่ได้ ข้อความ *"File is in a directory that is denied by your permission settings."* | ข้อความเดียวกันตรงตัว (ใน `<tool_use_error>`) | ✅ (แต่ได้ในโหมด `bypassPermissions` ไม่ใช่ default) |
| `git status` สะอาดใน `e2e-legacy/` | `git status --porcelain -- e2e-legacy/` ว่าง · SHA-256 เท่าเดิม | ✅ |
| ไปต่อได้: รั้วปฏิเสธจริงในเซสชันใหม่ · CLAUDE.md มีคำสั่งรันทุกชุด + ห้าม `down -v` + กติกาค่าคาดหวัง | ครบ (check-rules · e2e api+chromium · test:all · reset · health · ห้าม down -v · oracle rule + ORACLE-CHANGES) | ✅ |

## ภาคผนวก (orchestrator) · ทดสอบรั้วในโหมดของผู้เรียน
- `claude -p ... --permission-mode acceptEdits` (ไม่ใช่ yolo/bypass) จาก `w/` สั่ง Edit `e2e-legacy/playwright.config.ts` → **ถูกปฏิเสธ** agent ไม่พยายามเลี่ยงผ่าน Bash · SHA-256 ก่อน/หลัง = `595e9f566fbc032b` เท่ากัน · git status สะอาด
- สรุป: deny `Edit(e2e-legacy/**)` กันได้ทั้งโหมด acceptEdits (ผู้เรียน) และ bypassPermissions (yolo)
