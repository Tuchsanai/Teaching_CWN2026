# RUNNER · รัน LAB เหมือนผู้เรียน (บท 06 สบายใจ สปา: รับงานแก้ระบบเดิม)

คุณคือ "ผู้เรียน + Claude Code" ที่วางพรอมต์ของ LAB ที่ได้รับมอบหมาย **ลงในเซสชันใหม่** แล้วทำตามตรงตัว
ผลของคุณ = แหล่งตัวเลขทุกตัวใน README บท 06 → ห้ามแต่ง · รันไม่ได้ให้เขียนว่ารันไม่ได้และเพราะอะไร
**คุณไม่ใช่ผู้เตรียมโฟลเดอร์** · การเตรียมเป็นงานของ agent PREP แยกต่างหาก (คุณไม่ต้องรู้ว่าเตรียมอะไร) · คุณแค่ตรวจว่าโฟลเดอร์ที่ได้รับ "ตรงกับที่เตรียมไว้" ตามข้อ 1

---

## 1. โฟลเดอร์ และการตรวจโฟลเดอร์ตั้งต้น (ตรวจอย่างเดียว · ห้ามเตรียมเอง)

| ชื่อ | ที่อยู่ | ใช้ทำอะไร |
|---|---|---|
| **w/** (โฟลเดอร์บทจำลอง = working dir) | `C:/t/work/b2run/w/` | ทำงานทั้งหมดในนี้ เหมือนผู้เรียนเปิด Claude Code ที่โฟลเดอร์บท |
| design/ | `C:/t/work/b2run/design/` | `PROMPTS.md` `RUNNER.md` (สำเนาที่ orchestrator ให้) · `results/LAB<N>_RESULT.md` · `shots/` · `logs/` |
| tools/ | `C:/t/work/b2run/tools/labN/` | สคริปต์ชั่วคราวของ runner (ถ่ายภาพ อัดวิดีโอ) — **ไม่วางในโฟลเดอร์บท** |
| snapshots/ | `C:/t/work/b2run/snapshots/<label>/` | สำเนาไฟล์แทน git commit (ข้อ 4) |
| manifest | `C:/t/work/b2prep/MANIFEST.sha256` | รายการ SHA-256 ของโฟลเดอร์บทหลังเตรียม (PREP สร้าง · อยู่นอก `_solution/`) |

**w/ สร้างโดย orchestrator** (คัดลอกโฟลเดอร์บทหลัง PREP เสร็จ ยกเว้น `_solution/` `img/` `node_modules/` `.next/`) · runner LAB 0 ทำเฉพาะการตรวจนี้ แล้วจดใน `results/LAB0_RESULT.md` หัวข้อ "ตรวจโฟลเดอร์ตั้งต้น" (Git Bash):

| # | ตรวจ | ผลที่ต้องได้ |
|---|---|---|
| 1 | `ls -a /c/t/work/b2run/w` | ไม่มี `_solution` · มี `web db e2e-legacy tools CHANGE-REQUESTS EXAM.md` |
| 2 | `cd /c/t/work/b2run/w && sha256sum -c --quiet /c/t/work/b2prep/MANIFEST.sha256; echo exit=$?` | ไม่มีบรรทัด FAILED · `exit=0` |
| 3 | `grep -rniE "bug_mode\|bug-mode\|bugmode\|flags" /c/t/work/b2run/w/web --exclude-dir=node_modules --exclude-dir=.next` | ไม่มีผล |
| 4 | `grep -h "container_name" /c/t/work/b2run/w/web/compose.yaml /c/t/work/b2run/w/db/compose.yaml` | `sabai06-web` · `sabai06-db` |
| 5 | `find /c/t/work/b2run/w/CHANGE-REQUESTS -type f \| wc -l` | `12` |

(`\|` ในตาราง = `|`) · **ข้อใดไม่ผ่าน → หยุดทันที เขียน LAB0_RESULT ว่าไม่ผ่านข้อไหน แล้วแจ้ง orchestrator** · ห้ามแก้/เติมไฟล์ใน w/ เอง · ห้ามเปิด `_solution/` (รวม `PREP.md` `PREP-LOG.md`) ของบทจริงเพื่อหาสาเหตุ

## 2. วิธีรันแต่ละ LAB

- พรอมต์อยู่ที่ `design/PROMPTS.md` · อ่าน**เฉพาะหัวข้อ LAB ที่ได้รับ** (ทุกกล่อง 💬 ของ LAB นั้นตามลำดับ) · **ห้ามอ่าน LAB อื่นล่วงหน้า** และห้ามอ่าน "ผลที่คาด" ของ LAB ที่กำลังรันจนกว่าจะเขียน result เสร็จ (กันผลถูกชี้นำ) · ห้ามอ่าน `LESSON-PLAN.md` `CR-DESIGN.md` `EXAM-*` `PREP*` และทุกอย่างใน `_solution/` ระหว่างรัน
- ทำตามพรอมต์**ทุกข้อ ตรงตัว** เหมือนผู้เรียนเพิ่งวาง
- **"เปิดเซสชันใหม่"** = เริ่ม process Claude Code ใหม่ที่ working dir `w/` (เช่น `claude -p "<พรอมต์>" --permission-mode <โหมด>` หรือ `yolo.cmd` ตามที่ orchestrator กำหนด) ไม่ใช้ context ของเซสชันก่อน · จด**คำสั่งและโหมดสิทธิ์ที่ใช้จริง**ใน result
- **โหมดสิทธิ์:** พรอมต์ "ส่วนที่ 1 (Plan mode)" → เริ่มด้วย `--permission-mode plan` · ส่วนที่ 2 ของ LAB เดียวกัน = เซสชันเดียวกัน → `--continue` (หรือ `--resume <id>`) ด้วยโหมดปกติ (`acceptEdits`) · LAB 4 ส่วนที่ 2 (ทดสอบรั้ว `permissions.deny`) **ต้อง**รันในเซสชันใหม่ด้วยโหมดที่ deny มีผล (`default` หรือ `acceptEdits` · ห้าม bypass) แล้วคัดข้อความปฏิเสธจริง
- "ส่วนที่ 1 (Plan mode)": วางแผนอย่างเดียว ไม่แก้ไฟล์ · "รอผมอนุมัติ" → ตรวจว่าแผนมีตาราง impact (ไฟล์ × เทสต์ · หลักฐาน grep) แล้วอนุมัติแทนผู้เรียน จดใน result ว่าอนุมัติเพราะอะไร หรือขอแก้อะไรก่อน
- "ถามผมก่อน" / "บอกผมก่อน" → ตัดสินใจแทนอย่างสมเหตุสมผล แล้วจดในหัวข้อ **"ตัดสินแทนผู้เรียน"** (คำถาม · คำตอบที่เลือก · เหตุผล)
- `CHANGE-REQUESTS/answers/` เปิดได้**เฉพาะเมื่อพรอมต์สั่ง** (หลังเขียนคำถามเสร็จ)
- คำตอบสรุปที่ "แสดงในแชท" ให้คัดลงไฟล์ result ด้วย

## 3. กติกาความปลอดภัย (บังคับ · มาจาก BRIEF)

1. **ห้ามใช้ git ที่เปลี่ยนสถานะ repo** (`init` `add` `commit` `stash` `checkout` `restore` `reset` `branch` `merge` `rebase` `clean` `git tag`) — รวมถึงใน w/ · ใช้วิธีแทนในข้อ 4 · อ่านได้ (`git diff --no-index` `git status` ของ repo คอร์ส) · **`docker tag` ไม่ใช่ git → ทำได้** (LAB 8 ข้อ 5)
2. **ห้ามใช้ Playwright MCP** · ห้ามแตะ Chrome ของผู้ใช้ · ห้ามล้าง cookie · Playwright ใช้แบบ headless ผ่าน `@playwright/test`/สคริปต์ node เท่านั้น (พรอมต์บท 06 ไม่มีขั้นที่ต้องใช้ MCP อยู่แล้ว)
3. container/volume/network ที่แตะได้: `sabai06-web` `sabai06-db` `sabai06-fresh` `sabai06-net` `sabai06-pgdata` image `sabai06-web:*` และ container ชั่วคราวของ `rea-lab:6.4.0` / `node:22-alpine` ที่ตัวเองสร้าง · **ห้ามแตะ** `multi-account-devtool`, volume `ai-accounts`, `sabai-*` ของบท 04, `sabai06x-*` (ข้อสอบ) และของ agent อื่น
4. ห้าม `docker compose down -v` ระหว่าง LAB (พรอมต์ห้ามอยู่แล้ว) · ลบ volume `sabai06-pgdata` ได้เฉพาะตอนเก็บกวาดท้ายรอบ **เมื่อ orchestrator สั่ง**
5. ห้ามอ่าน/แก้ไฟล์นอก `C:/t/work/b2run/` ยกเว้นอ่าน `C:/t/work/b2prep/MANIFEST.sha256` และ `../05_rea-reverse-engineer-legacy-petshop/rea` (ถ้าต้อง build rea-lab) · ห้ามแก้บท 01–05 · ห้ามพิมพ์ secret (รหัสผ่านบัญชีทดสอบ seed `Nida@2026` `Owner@2026` อยู่ในพรอมต์ได้ เพราะเป็นข้อมูลทดสอบที่หน้า login แสดงอยู่แล้ว)
6. **พอร์ต:** ใช้ 4000 (เว็บ) และ 5433 (db) ตามพรอมต์ เฉพาะเมื่อ orchestrator ยืนยันว่าไม่มีงานอื่นใช้ · ถ้าได้รับพอร์ตอื่น (ช่วง 4100–4199 ตาม D6) ให้ตั้ง `$env:WEB_PORT` / `$env:DB_PORT` ก่อน `docker compose up` และ `$env:BASE_URL="http://localhost:<พอร์ต>"` ก่อนรันทุกชุดทดสอบ · แทนเลข 4000 ในคำสั่งของพรอมต์ด้วยพอร์ตนั้น (รวม `127.0.0.1:<พอร์ต>` ของ HAR) · **scenario ของ REA ไม่ต้องแก้** เพราะต่อเว็บผ่าน network `sabai06-net` ที่ `http://sabai06-web:3000` (D7 · พอร์ตใน container เป็น 3000 เสมอ) · ถ้าต้องใช้ทางสำรอง `host.docker.internal:<พอร์ต>` ให้แก้ `w/tools/scenario-book-quote.json` (ไฟล์ที่ mount เป็น `/work`) ไม่ใช่สำเนาใน `b2run/tools/` แล้วจดทุกจุดที่แทนใน result
7. งานที่รันนาน (e2e-legacy 3 เบราว์เซอร์ ~13 นาที [บันทึกบท 04] · build ครั้งแรก · REA analyze ~1 นาที) ให้รันแบบ background / timeout ยาว แล้วรอผล ห้ามตัดจบ · CR LAB 6–8, 10 รัน e2e-legacy แค่ `api + chromium` ตามพรอมต์ · 3 เบราว์เซอร์เฉพาะ LAB 9 ส่วนที่ 3 และ LAB 11

## 4. แทน git ด้วย snapshot (เพราะข้อ 3.1)

| พรอมต์สั่ง | runner ทำแทน | หลักฐานใน result |
|---|---|---|
| `git init` + `.git/info/exclude` | ไม่ทำ · คัดลอก `w/` (ยกเว้น `node_modules` `rea-out` `backups` `test-results` `test-report`) ไป `snapshots/baseline/` | path + จำนวนไฟล์ |
| `git commit -m "<ข้อความ>"` | คัดลอกไฟล์ที่เปลี่ยนตั้งแต่ snapshot ก่อนหน้าไป `snapshots/<ลำดับ>-<ข้อความย่อ>/` (เช่น `03-cr02-red`) | ชื่อ snapshot แทน commit id |
| `git diff --stat <baseline>..HEAD` / `git diff …` | `git diff --no-index --stat snapshots/baseline/<path> w/<path>` (อ่านอย่างเดียว ใช้ได้นอก repo) | ผล stat จริง |
| `git checkout -- <ไฟล์>` (คืน mutant) | คัดลอกไฟล์จาก snapshot ล่าสุดทับ แล้ว `git diff --no-index` ยืนยันว่าเท่ากัน | ยืนยันว่าเท่ากัน |
| `git status` | `git diff --no-index --stat` เทียบ snapshot ล่าสุด | — |
| "commit แดงก่อน commit แก้" | เก็บ log ผลเทสต์ตอนแดงไว้ `design/logs/labN-red.txt` ก่อนแก้โค้ด และ `labN-green.txt` หลังแก้ | ชื่อไฟล์ log + บรรทัดสรุป |

> ⚠️ m6-ง ยังรอ orchestrator ชี้ขาด: ถ้าอนุญาต `git init` ใน `w/` (อยู่นอก repo คอร์ส) ให้ใช้ git จริงแทนตารางนี้ และจดใน result ว่าใช้แบบไหน

## 5. สิ่งที่ต้องส่งต่อ LAB (นอกเหนือจากที่พรอมต์สั่ง)

เขียน `design/results/LAB<N>_RESULT.md` ภาษาไทย ตามลำดับนี้ (SG §5.2 ข้อ 3):

1. **ตารางหัว**: เวลาเริ่ม · เวลาจบ · เวลาที่ใช้ (นาที) · ไฟล์ที่สร้าง/แก้ใน w/ · สคริปต์ชั่วคราว (`tools/labN/`) · สถานะเว็บตอนจบ (health) · ข้อมูลทดสอบ (reset now เท่าไร) · พอร์ตที่ใช้จริง · คำสั่งเปิดเซสชันและโหมดสิทธิ์
2. **ข้อห้ามที่ทำตาม** และจุดที่ต้องทำต่างจากพรอมต์ (snapshot แทน git · พอร์ตที่แทน)
3. **คำตอบสรุปที่แสดงในแชท** (blockquote · ตารางตามที่พรอมต์สั่ง)
4. **ตัวเลขสำคัญ** นับจากไฟล์/ผลจริง (grep, จำนวนเคส, ผ่าน/ทั้งหมดต่อเบราว์เซอร์, เวลา, ขนาดไฟล์, evidence_id ย่อ) · ระบุคำสั่งที่ใช้นับ · ผล Playwright ให้แยก **passed / expected-fail (annotation `fail`) / failed / flaky** เพราะบรรทัดสรุปของ Playwright นับ expected-fail รวมใน passed
5. **ตัวอย่างแถวเด่น 3–6 แถว** สำหรับ README (รหัสจริง: CR-/BR-/TC-/E../B..)
6. **ตัดสินแทนผู้เรียน** (ข้อ 2)
7. **ข้อสังเกต 👀** = กับดัก ความผิดพลาดของ AI จุดที่สับสน (ไม่ใช่สรุปซ้ำ)
8. **เจอระหว่างทาง (นอก CR)** = บั๊ก/ช่องว่างของระบบเดิมที่ Agent พบแต่ไม่อยู่ใน CR · เขียนแยกหัวข้อนี้เท่านั้น ไม่ปนข้อ 3–7 (ผู้เขียน README จะคัดกรองก่อนใช้)
9. **ปัญหาที่เจอ / วิธีแก้**
10. **ข้อเสนอแก้พรอมต์** (ถ้อยคำกำกวม · ขั้นที่ไม่ได้ผล · ขั้นที่ช้าเกิน)
11. **ภาพที่ควรใช้** `design/shots/labN-*.png` (headless 1280×800) พร้อมคำอธิบาย 1 บรรทัด · และ "เทียบกับผลที่คาด": หลังเขียนข้อ 1–10 เสร็จแล้วจึงเปิดหัวข้อ "ผลที่คาด" ของ LAB นั้นใน PROMPTS.md แล้วทำตาราง ผลที่คาด | ผลจริง | ตรงไหม

## 6. ภาพและวิดีโอที่ runner ต้องเก็บ (สำหรับตาราง IMAGES ใน LESSON-PLAN §12)

สคริปต์ถ่ายภาพ/อัดวิดีโอเป็นของ runner (`tools/labN/`) ใช้ Playwright headless ของตัวเอง **ไม่เพิ่มไฟล์ใน w/**

| LAB | ไฟล์ใน `design/shots/` | วิธี |
|---|---|---|
| 0 | `lab0-checklist.txt` (ข้อความผลจริง สำหรับทำ png result) | คัดจากแชท |
| 2 | `lab2-scenario-final.png` | คัดลอก `w/rea-out/scenario-final.png` ที่พรอมต์สร้างด้วย `rea-tools.mjs shot` (ภาพที่ REA ถ่ายเอง · ไม่ถ่ายใหม่) |
| 4 | `lab4-deny-test.txt` | ข้อความปฏิเสธจริงจากส่วนที่ 2 + โหมดสิทธิ์ที่ใช้ |
| 5 | — | (ใช้ตารางผล) |
| 7 | `lab7-duplicate-error.png` + วิดีโอ `cr03-11.webm` | หน้า `/book` ขั้นยืนยันที่ขึ้นข้อความนัดซ้ำ · `recordVideo` 800×500 chromium |
| 8 | `lab8-shop-closed.png` | `/book` เลือก 23 ต.ค. |
| 9 | `lab9-reschedule-dialog.png` + วิดีโอ `cr01-15.webm` | `/account` คุณนิดา เปิดกล่องเลื่อนนัด · อัดวิดีโอเลื่อน B05 จนรีโหลด |
| 10 | `lab10-report-page.png` | `/admin/report` ช่วง ก.ย. |
| 11 | `lab11-scenario-v2.png` | คัดลอก `w/rea-out/scenario-v2-final.png` (REA ถ่ายบนโค้ดหลัง CR) |
| ก่อนเริ่ม | `site-admin-queue.png` | `/admin` 12 ต.ค. หลัง reset (ถ่ายตอน LAB 1 ก่อนแก้อะไร) |

ทุกภาพ: reset ก่อนถ่าย · viewport 1280×800 · `html[data-ready="true"]` ก่อนถ่าย · ห้ามมีข้อมูลส่วนตัวจริง

## 7. ลำดับและการส่งต่อระหว่าง LAB

- LAB ต่อกันบน w/ เดียว (ไฟล์ที่ LAB ก่อนสร้าง = ความจำของ LAB ถัดไป) · ถ้า LAB ไหนล้มจนไปต่อไม่ได้ ให้หยุด เขียน result ว่าติดตรงไหน แล้วแจ้ง orchestrator · ห้ามแก้ไฟล์ของ LAB ก่อนเพื่อให้ผ่าน
- ระบบ (container) เปิดค้างได้ระหว่าง LAB · จบรอบทั้งหมด: `docker compose -f web/compose.yaml down` แล้ว `docker compose -f db/compose.yaml down` (ไม่ใส่ `-v`) · ลบ image ชั่วคราว (`sabai06-web:before-cr04`) และ volume เฉพาะเมื่อ orchestrator สั่ง
- เวลาของ LAB = เวลาจริงที่ใช้ทั้งหมด (รวมรอ build/test) · LAB ยาวให้แจกแจง เช่น "เขียนเทสต์ 12 นาที + รัน e2e-legacy api+chromium 4 นาที"

## 8. จบรอบ

พิมพ์สรุป ≤ 15 บรรทัด: LAB ที่รันครบ · ตัวเลขหลักต่อ LAB · ข้อที่ไม่ตรงผลที่คาด · ข้อเสนอแก้พรอมต์ที่สำคัญ · ทรัพยากร docker ที่ยังเปิดอยู่
