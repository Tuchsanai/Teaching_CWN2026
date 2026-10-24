# PROMPT-FIX-LOG · บท 06 · แก้พรอมต์ LAB 0–9 ตามผลรอบ RUNNER (PF6 · 12 ต.ค. 2026)

แหล่ง: `C:/t/orch/PROMPT-FIXES-06.md` + หัวข้อ "ข้อเสนอแก้พรอมต์" ใน `LAB0..9_RESULT.md` ของ runner (อ่านอย่างเดียว) · ไม่ได้เปิดเซิร์ฟเวอร์หรือรันระบบในงานนี้ ตัวเลขที่เติมลง "ผลที่คาด" มาจากผลรอบ RUNNER เท่านั้น

## ไฟล์ที่แก้

| ไฟล์ | แก้อะไร |
|---|---|
| `_solution/_design/PROMPTS.md` | v2 → v3: กล่องพรอมต์ LAB 0–9 · ผลที่คาด LAB 0–9 · กติการ่วม 4 ข้อใหม่ · บรรทัดคั่น `<!-- ✂ … -->` ก่อนผลที่คาด LAB 0–9 · LAB 10–12 แก้แค่ถ้อยคำ D15 · ภาคผนวกเพิ่ม 2 แถว แก้ 2 แถว |
| `_solution/_design/README-PART-B.md` | คัดกล่อง `text` ทั้ง 25 กล่องจาก PROMPTS.md · ปรับ 👀 / 🎯 / ✔️ / หัวกล่อง LAB 4 ส่วนที่ 2 · ตาราง 🔁 และถ้าเจอปัญหา · ผังไฟล์ |
| `fast_track/README.md` | พรอมต์ 🅰️ และ 🅱️ ตรงที่ใช้คำสั่ง/กติกาเดียวกัน · ตาราง 🆘 เพิ่ม 2 แถว · ข้อ 2 ของ "จุดที่ต่าง" |

**ตรวจ byte-identical (สคริปต์ Python เทียบ UTF-8 bytes):** กล่อง `text` 25 กล่องก่อนหัวข้อรูบริกใน README-PART-B = 25 กล่องใน PROMPTS.md → `IDENTICAL` · ทั้ง 3 ไฟล์ยังเป็น LF เหมือนเดิม

## รายการแก้ต่อ LAB

ระดับ H/M/m ตาม PROMPT-FIXES-06 · ✅ = แก้ · ➖ = ไม่แก้ (เหตุผลในช่องหมายเหตุ) · FT = fast_track (A = บอกใบ้ · B = ไม่บอกใบ้)

| LAB | ระดับ | เรื่อง | PROMPTS / README-B | FT | หมายเหตุ |
|---|---|---|---|---|---|
| 0 | m | ข้อ 8: toplevel = โฟลเดอร์นี้ = ใช้ได้ · path อื่น = อยู่ใน repo อื่น | ✅ | ✅ A B | 👀 เพิ่มประโยคเดียวกัน |
| 0 | m | ข้อ 4: ไม่ว่าง → บอก container · แถวแก้ปัญหา "เว็บบท 05 ค้างที่ 4000" | ✅ + แถวใหม่ในภาคผนวก/ถ้าเจอปัญหา | ✅ A B + 🆘 | ใช้ `docker stop pawpantry05` (ชื่อ container ใน compose บท 05) แทน path compose ซึ่งใช้ไม่ได้ถ้าคัดลอกบทไป `C:\work\sabai06` |
| 0 | m | ข้อ 7: แถว Process = Bypass จากเครื่องมือ | ✅ | ✅ A B | |
| 1 | M | ข้อ 7: repo อยู่แล้ว / tree สะอาด · เขียน HANDOVER-CHECK ก่อน commit | ✅ | ✅ A B | |
| 1 | M | `--reporter=list` ทับ html → `npm run report` เสีย | ✅ **ต่างจากที่เสนอ** | ✅ A B | ไม่ใช้ `--reporter=list,html` เพราะ html จาก CLI ใช้ค่าเริ่ม `open: 'on-failure'` + โฟลเดอร์ `playwright-report/` (config ใช้ `open: 'never'` + `test-report/html`) → มีข้อล้ม 1 ข้อจะเปิดเซิร์ฟเวอร์ค้าง · ใช้ `npx playwright test` เฉย ๆ (config มี list + html อยู่แล้ว) |
| 1 | M | ✘ เหมือนกันทั้ง expected-fail/failed | ✅ รายชื่อ failed ท้ายผล + `Select-String … -SimpleMatch "test.fail("` | ✅ A B | e2e-legacy มี `test.fail(` 3 จุด (giftcard · security.api · transport) ตรงกับ expected-fail 3 ข้อ |
| 1 | m | เลข H ต่อเนื่อง (บันทึก → README-LEGACY) | ✅ + ผลที่คาดบอกว่าตรวจด้วยเนื้อหา | — | FT มี H1, H2 … อยู่แล้ว |
| 1 | — | exclude ไม่ anchor (`README.md` กิน `tests/golden/README.md`) | ✅ `/_solution/ /img/ /README.md /EXAM.md /fast_track/` | ✅ A B | PROMPT-FIXES บอกว่าเป็นของ runner แต่พรอมต์ LAB 1 เดิมสั่งบรรทัด `README.md` แบบไม่ anchor เอง → ผู้เรียนโดนด้วย · เพิ่ม `/fast_track/` ที่ PROMPTS เดิมขาด |
| 1 | note | `/admin` เปิดคิวพรุ่งนี้ → ภาพใช้ `?date=` | ✅ ผลที่คาด | — | |
| 2 | H | rea-tools `ids summary scenario-sum pages` | ➖ ทำแล้วโดย FIX6T | ➖ | กล่อง LAB 2/11 มีครบแล้ว |
| 2 | M | stderr ของ REA ลง log | ➖ มีแล้ว (`2> rea-out\*.log`) | ➖ มีแล้ว | |
| 2 | M | record-har เปลี่ยนข้อมูล · body login ว่าง | ✅ เพิ่มเรื่อง body login (คำเตือนข้อมูลมีแล้ว) + 👀 | ➖ คำเตือนมีแล้ว | |
| 2 | m | `tools/.gitignore` + package-lock.json | ➖ | ➖ | มีอยู่แล้ว (`node_modules/` `package-lock.json`) |
| 2 | m | ผลที่คาด: เศษ `[[...]] [] [...]` ไม่ใช่ `a b c` · static ~34 MB | ✅ | — | |
| 3 | H | คิวรี `pg_constraint` นับ c/f/x/p/u | ✅ รวม + ต่อตาราง | ✅ A B | A ใส่ FK 25 ในตัวเลขตรวจทวน |
| 3 | H | route นับทั้งไฟล์ (25) และ handler (26) | ✅ + ผลที่คาด | ✅ A B | |
| 3 | M* | ช่องที่ REA ไม่เห็น → "REA ไม่เห็น" + เหตุผล ห้ามแต่ง ev_ · สุ่มด้วย `Get-Random` | ✅ | ✅ A B (ข้อแรก) | *ข้อเสนอ M ของ runner ที่ไม่อยู่ในรายการรวม แต่ถูกและสั้น |
| 3 | 🔒 | G9/S4 "กดเสร็จก่อนเวลานัด" | ➖ ไม่แตะ | ➖ | ไม่มีอยู่ใน README-B/ภาพจากงานนี้ (D12) |
| 3 | note | runner อ่านผลที่คาดตามช่วงบรรทัด | ✅ บรรทัดคั่น `<!-- ✂ … -->` LAB 0–9 + บรรทัดอธิบายหัวไฟล์ | — | |
| 4 | M | บอกว่า git add อะไร (ไฟล์ LAB 1–3 ยังไม่ commit) | ✅ `git add -A` + `git status` + 👀 | ✅ A B | |
| 4 | m | ถ้อยคำ `Edit(...)` กันเครื่องมือแก้/เขียนไฟล์ทุกตัว | ✅ + 👀 | ✅ A | |
| 4 | M | ส่วน 2 เปิด `claude` ธรรมดา ไม่ใช้ skip-permissions · รั้วไม่กัน shell/การอ่าน | ✅ หัวส่วน 2 (PROMPTS + README-B) + 👀 | ➖ | FT ใช้ `claude -p` อยู่แล้ว |
| 4 | m | `@SYSTEM-MAP.md` (~46 KB) โหลดทุกเซสชัน → ลิงก์ธรรมดา | ✅ + 👀 | ✅ A B | พรอมต์ CR สั่ง "อ่าน SYSTEM-MAP.md ก่อน" อยู่แล้ว |
| 4 | D15/D15a | deny `Read(/README.md)` `Read(./fast_track/**)` `Read(./_solution/**)` + Edit เดิม · CLAUDE.md เขียนห้ามอ่าน | ✅ ข้อ 2–3 + ผลที่คาด 4 กฎ + 🎯 + ผังไฟล์ | ✅ A B | **เพิ่มเอง:** ส่วนที่ 2 ทดสอบอ่าน README.md รากบทต้องถูกปฏิเสธ (ห้ามสรุปเนื้อหาถ้าอ่านได้) · ข้อความปฏิเสธจริงยังไม่มีรอบรัน |
| 4 | D15 | ภาคผนวก "เทียบงานกับเฉลย" อ่าน `_solution/` ไม่ได้แล้ว | ✅ บอกให้ลบ 3 กฎ `Read` เองก่อน + เปิดเซสชันใหม่ | — | ผลข้างเคียงของ D15 ที่ต้องบอกผู้เรียน |
| 4/6 | M | path แม่แบบ `docs/IMPACT-CR-0N.md` vs `docs/impact/CR-0N.md` | ✅ LAB 4 ข้อ 4 ระบุว่าแม่แบบของ `docs/impact/CR-0N.md` | ✅ A B | |
| 5 | M | ตรวจ `git status` ก่อน commit ว่าไฟล์ครบ | ✅ + 👀 | ✅ A B | |
| 5 | M | aria snapshot เขียนข้อความตรง ไม่ใช้ regex | ✅ + ผลที่คาด + 👀 | ✅ A B | |
| 5 | M | "40–60 เคส" = เฉพาะ `/api/price` | ✅ + ผลที่คาด (50 + 6 + 6 = 62) | ✅ A B | |
| 5 | M | เทียบ SPEC-GAPS ก่อนเรียก owner-cancel ว่าบั๊ก | ✅ ถ้อยคำทั่วไป (ไม่ชี้ G13) | ✅ A B | |
| 5 | L | บรรทัดสรุปนับ test.fail ใน passed (e2e-cr) | ✅ | ✅ A B | |
| 5 | — | ผลที่คาด X1 "อาจรอด" → ผลจริงจับครบ 3 ตัว · e2e-cr ไม่จับ | ✅ + 👀 | ✅ A (ตัวเลขตรวจทวน) | |
| 5 | L | `.gitattributes` ให้ SHA golden คงที่ | ➖ | ➖ | ไม่ใช่เรื่องพรอมต์ · เสนอให้ PREP พิจารณา |
| 6–9 | H | Plan mode เขียนไฟล์ไม่ได้ → แสดงคำถามในแชท · impact อยู่ในแผน · อนุมัติแล้วบันทึกไฟล์อย่างเดียวแล้วหยุด · ส่วน 2 ข้อ 0 ตรวจซ้ำ | ✅ ทุกส่วนที่ 1–2 ของ LAB 6–9 + กติการ่วม + บทนำ LAB 6–10 ใน README-B | ➖ | FT ไม่ใช้ Plan mode (เขียน impact ลงไฟล์ตรง) · LAB 10 ยังไม่แก้ (คำสั่งงาน) |
| 6–9 | M | อัปเดต REGISTER ก่อน commit (ไม่มี commit ที่ 3) + `git add` ชัดเจน | ✅ ทุก commit แดง/แก้ | ✅ A B (วงจร CR ⑨) | |
| 6 | m | ตรวจ `discountKind` (Gold กลุ่ม 3 ยอดเท่ากัน) | ✅ + ผลที่คาด + 👀 | ➖ | A มีตัวอย่างตรวจทวน ฿2,850 อยู่แล้ว |
| 7 | H | ส่วน 2 ข้อ 3 "3 เบราว์เซอร์" ขัด M6 → `--project=chromium` | ✅ + ✔️ README-B เปลี่ยนเป็น chromium | ✅ A B (วงจร ⑧) | กติการ่วม M6 v3: spec ใหม่ของ CR ก็ chromium |
| 7 | M | เทสต์เดิมจองทับนัด seed ด้วยบัญชีเจ้าของ + ลำดับ error | ✅ ส่วน 1 ข้อ 4 (ไม่ระบุชื่อ TC) + ผลที่คาด (TC-BOOK-07) + 👀 "ชุดเทสต์เดิมจับ regression ได้" | ✅ A ระบุ TC-BOOK-07 · A B วงจร ④ แบบทั่วไป | |
| 7 | M | แชทครบ 5 ข้อความ + state · ภาษา error จาก cookie `lang` | ✅ + 👀 | ✅ A | B ไม่ใส่ (เป็นเบาะแสเฉพาะระบบ) |
| 7 | note | ข้อมูลเคสในผลที่คาดต่างจากที่ runner ใช้ | ✅ เติมบรรทัด "หลักเดียวกัน คนละข้อมูล" | — | ไม่ได้เปลี่ยนค่าเดิม (ยังไม่มีการรันยืนยันว่าเคสเดิมผิด) |
| 7 | L | ระบุบริการ S02 ในข้อ 1 | ➖ | ➖ | ให้ผู้เรียนหาเองจาก seed (ทักษะทำซ้ำเรื่องร้องเรียน) |
| 8 | H | NOTICE รอบ 2 = ตัวแดงใน PS 5.1 → `$LASTEXITCODE` / `SET client_min_messages = warning;` | ✅ ทั้งสองทาง + แถวแก้ปัญหาใหม่ + 👀 + ผลที่คาด `INSERT 0 3 / 0 0` | ✅ A (ทั้งสองทาง) · B (`$LASTEXITCODE`) + 🆘 | |
| 8 | H | ข้อ 6 "3 เบราว์เซอร์" → `--project=chromium` | ✅ | ✅ (วงจร ⑧) | |
| 8 | M | ลำดับ: migrate → rebuild · ถอย: เว็บ → down.sql (+ runbook หัวข้อ "ลำดับ") | ✅ ส่วน 1 ข้อ 4 · ส่วน 2 ข้อ 5 และ 8 + 👀 + ผลที่คาด | ✅ A B (ขั้น 8 และ 12 ⑧) | LAB 12 ไม่แก้ (คำสั่งงาน) · ลำดับใน LAB 12 ถูกอยู่แล้วเพราะหยุดเว็บก่อน down |
| 8 | M | ติดตั้งใหม่ต้องรอ init จบ | ✅ วนถาม `SELECT count(*) FROM shop_holiday` สูงสุด ~60 วิ | ✅ A B | |
| 8 | L | คำใบ้แชท `freeTimes` / ถ้อยคำร้าน "วันนี้ร้านหยุด" | ➖ | ➖ | ข้อแรกจะเฉลยกับดัก · ข้อสองอยู่ใน answers ไม่ใช่พรอมต์ |
| 9 | M | ข้อความ commit ของ UI test แดง | ✅ `CR-01 C test: แดงก่อนแก้` | ➖ | FT ใช้รูปแบบวงจร ⑥ อยู่แล้ว |
| 9 | M | แยก expected-fail ด้วย JSON | ✅ `$env:PLAYWRIGHT_JSON_OUTPUT_NAME` + `npx playwright test --project=api --project=chromium --project=firefox --project=webkit --reporter=list,json` + วิธีนับจาก `status`/`expectedStatus` | ✅ A B (ขั้น 9 · 11) | ไม่ใช้ `npm run test:all -- …` เพราะ `--` อาจหายเมื่อเรียก npm.ps1 จาก PowerShell · ยังไม่ได้รันรูปนี้ตรงตัว (runner รันด้วย `-- --reporter=list,json`) |
| 9 | M | TC-UI-02 webkit flaky → รันซ้ำ + พิสูจน์บน image `before-cr04` | ✅ + ผลที่คาด (112/2) + 👀 "flaky ≠ regression" + แถวแก้ปัญหา | ✅ A (ระบุชื่อ) · A B กติกาข้อ 6 | |
| 9 | m | rebuild ครั้งเดียวสำหรับ A+B ได้ | ✅ | ➖ | |
| 10–12 | D15 | ห้ามเปิด README.md ของบท + fast_track/ + _solution/ | ✅ ถ้อยคำเท่านั้น | — | ไม่แตะส่วนอื่นของ LAB 10–12 (runner กำลังรัน) |

## สิ่งที่ยังไม่ได้ยืนยันด้วยการรัน (ให้รอบ RUNNER ถัดไปดู)

| เรื่อง | ทำไมเสี่ยง |
|---|---|
| ข้อความปฏิเสธของ `Read(/README.md)` ใน LAB 4 ส่วนที่ 2 | กฎทดสอบแล้วโดย orchestrator (D15a) แต่ยังไม่มีข้อความจริงของรอบผู้เรียน |
| `npx playwright test --project=… --reporter=list,json` + `PLAYWRIGHT_JSON_OUTPUT_NAME` ใน PowerShell | runner LAB 9 ใช้รูป `npm run test:all -- --reporter=list,json` · รูป npx ยังไม่ได้รันตรงตัว |
| `Select-String … -SimpleMatch -Pattern "test.fail("` | ยังไม่ได้รัน (คาดได้ 3 บรรทัดตาม grep ของงานนี้) |
| `SET client_min_messages = warning;` บรรทัดแรกของ migration | runner LAB 8 ใช้ `$LASTEXITCODE` · ยังไม่ได้รัน migration ที่มี SET |
| คิวรี `pg_constraint` แบบแยกต่อตาราง | runner ใช้แบบรวม (ได้ CHECK 51 · FK 25 · EXCLUDE 2 · PK 19 · UNIQUE 10) |
| image `before-cr04` เป็น container ชั่วคราว `sabai06-old` พอร์ต 4001 | runner ใช้ชื่อ `sabai06-fresh` พอร์ต 4101 (sandbox) · ผู้เรียนต้องดู env จาก `web/compose.yaml` เอง |

## ที่ไม่ได้แตะ

- LAB 10: ยังมี "3 เบราว์เซอร์" ให้ `cr05.spec` และ Plan mode ยังสั่งเขียน `docs/impact/CR-05.md` ในส่วนที่ 1 → แก้หลังได้ผลรอบ RUNNER LAB 10 (กติการ่วมใน PROMPTS.md จดไว้แล้ว) · ระหว่างทำงานนี้ PROMPT-FIXES-06 มีหัวข้อ LAB 10 เพิ่ม (H: `psql -c "<SQL>"` ขัดกติกาภาษาไทย → `docker cp` + `psql -f` · H: Plan mode · M: seed ไม่มีนัดที่วัน UTC ≠ วันไทย) → **ยังไม่ได้ใช้** ตามคำสั่งงานที่ห้ามแก้ LAB 10–12 นอกจาก D15
- 👀 ของ LAB 10–12 ใน README-B · `README.md` หลักของบท · ภาพ

---

# PF6b · แก้พรอมต์ LAB 10–12 ตามผลรอบ RUNNER + เติมผล LAB 11–12 ใน README (12 ต.ค. 2026)

แหล่ง: `C:/t/orch/PROMPT-FIXES-06.md` (หัวข้อ LAB 10 · LAB 11) + "ข้อเสนอแก้พรอมต์" ใน `LAB10/11/12_RESULT.md` (อ่านอย่างเดียว) · ไม่ได้เปิดเซิร์ฟเวอร์ ไม่ได้รันระบบ · ไม่แตะ `C:/t/work/ft06` · ไม่ใช้ git ที่เปลี่ยนสถานะ

## ไฟล์ที่แก้

| ไฟล์ | แก้อะไร |
|---|---|
| `_solution/_design/PROMPTS.md` | LAB 10–12 → v3 (ตารางด้านล่าง) · บรรทัดคั่น `<!-- ✂ … -->` ก่อนผลที่คาด LAB 10 · 11 · 12 (ครบ 13 จุด LAB 0–12) · ผลที่คาด LAB 10–12 เติมผลรอบ RUNNER · หัวไฟล์ + กติการ่วม (Plan mode LAB 6–10 · ขอบเขตเบราว์เซอร์ LAB 10) |
| `README.md` (บท) | กล่อง `text` LAB 10 (2) · LAB 11 (1) · LAB 12 (2) คัดจาก PROMPTS.md ตรงตัว · ตรวจด้วยสคริปต์: ทุกกล่อง LAB 0–12 (25 กล่อง) **byte-identical** |

## รายการแก้

| LAB | ระดับ | เรื่อง | แก้ |
|---|---|---|---|
| 10 | H | `psql -c "<SQL>"` ขัดกฎ CLAUDE.md (ภาษาไทย/ PowerShell) | ส่วน 1 ข้อ 2: เขียน SQL ลงไฟล์ → `docker cp` → `psql -v ON_ERROR_STOP=1 -f` · ตรวจ `$LASTEXITCODE` |
| 10 | H | Plan mode เขียนไฟล์ไม่ได้ | ส่วน 1 หัวพรอมต์ + ข้อ 1 (คำถามในแชท) · ข้อ 3 "เนื้อหา impact (จะบันทึกเป็น…)" · ข้อ 4 บันทึก `docs/impact/CR-05.md` หลังอนุมัติแล้วหยุด · ส่วน 2 ข้อ 0 ตรวจซ้ำ |
| 10 | M | seed พิสูจน์โซนเวลาไม่ได้ | ส่วน 1 ข้อ 2: นับนัดที่วัน UTC ≠ วันไทย · ถ้า 0 → จดข้อจำกัด + เสนอวิธีพิสูจน์อื่น |
| 10 | M | เคสแชท "ไม่รั่ว" ผ่านก่อนแก้ | ส่วน 2 ข้อ 1 บอกว่าเป็นเรื่องปกติ |
| 10 | m | cr05.spec 3 เบราว์เซอร์ vs กติกา CR LAB | คงไว้เฉพาะไฟล์ `cr05.spec.ts` (การดาวน์โหลด CSV ต่างตามเบราว์เซอร์ · รอบจริง 15 วิ) + `--reporter=list,json` · e2e-cr ทั้งชุดยัง chromium |
| 10 | m | ลำดับ commit / REGISTER | ส่วน 2 ข้อ 1 `git add` ระบุไฟล์ · ข้อ 6 REGISTER ก่อน → `git add -A` → `git status` → commit (แบบ LAB 6–9) |
| 11 | H | "ข้อไหนแดงให้หยุด" (TC-SEC-05 แดงเสมอ) | "แดงใหม่ที่ baseline ไม่มีให้หยุด" + เทียบ HANDOVER-CHECK.md + TC-UI-02 รันซ้ำ `--repeat-each=3` ก่อนสรุป |
| 11 | H | นับผลต้องใช้ JSON | ข้อ 1 ใช้ `$env:PLAYWRIGHT_JSON_OUTPUT_NAME` + `--reporter=list,json` ทั้ง e2e-cr และ e2e-legacy (รูปเดียวกับ LAB 9) + วิธีนับ |
| 11 | H | REA หน้าใหม่ = `unknown` ไม่ใช่ `added` · route ใหม่ compare ไม่บอก | ข้อ 2 หมายเหตุหลัง `cmp-sum` + `rea-tools endpoints` v1/v2 |
| 11 | H | ชื่อ commit baseline · golden สร้างหลัง baseline | ข้อ 4 `git log --oneline --grep "baseline: ระบบที่รับมอบ"` (สำรอง: id ใน HANDOVER-CHECK) + ไฟล์คอร์สติด ⚠️ พร้อมเหตุผล · ข้อ 5 golden เทียบจาก commit ที่สร้าง (`--diff-filter=A`) |
| 11 | m | REA ขนานกับ e2e / HAR reset | บรรทัดลำดับต้นพรอมต์ |
| 12 | H | ขั้น 6 `cr04.mjs` reset → นัดใหม่หาย | ขั้น 6 จดหลักฐานนัดใหม่ก่อน แล้วค่อย cr04 (+ เหตุผล) |
| 12 | H | ซ้อมถอยไม่ได้ถอยเว็บ | ขั้น 4b ใหม่: เปิด `sabai06-web:before-cr04` เป็น `sabai06-old` พอร์ต 4001 (แบบ LAB 9) → health · /book 200 · /api/holidays 404 → stop · ขั้น 7 ระบุลำดับถอย เว็บก่อน down.sql |
| 12 | M | ไฟล์ไหนเข้า commit ไหน | ขั้น 8: TRACEABILITY เข้า commit เดียวกับ smoke+runbook · ส่วน 2 ข้อ 5 `git add -A` รวมเอกสารค้างจาก LAB 11 (REGRESSION-REPORT ORACLE-CHANGES) + `git status` |
| 12 | M | UAT ต้องตรวจบนหน้าจริง | ส่วน 2 ข้อ 2: ตรวจผลที่ต้องเห็นบนหน้าเว็บจริงด้วย Playwright headless (reset ก่อน/หลัง) · เจอแปลกห้ามแก้โค้ด ให้จด |
| 12 | M | CR-02 หลัง 1 พ.ย. ร้านกดเองไม่ได้ | ส่วน 2 ข้อ 2: เขียนขั้น "ทีมเปลี่ยนวันที่ของเครื่องทดสอบ" ในใบ |
| 12 | m | POST ไม่ล็อกอินนับเป็นอ่านอย่างเดียวไหม | ขั้น 0: นับได้ถ้าถูกปฏิเสธก่อนแตะข้อมูล |

## ไม่ได้ทำ / ยังไม่ยืนยันด้วยการรัน

| เรื่อง | หมายเหตุ |
|---|---|
| ขั้น 4b (สลับ image `before-cr04`) | ยังไม่ได้รัน · README จดว่า "ยังไม่มีเวลาวัด" · `before-cr04` = ก่อน CR-04/01/05 → smoke ทั้งชุดจะไม่ผ่าน จึงตรวจแค่ health · /book · holidays 404 |
| `--reporter=list,json` ผ่าน `npx` ใน LAB 10–11 | runner LAB 11 ใช้ `npm run test:all -- --reporter=list,json` · รูป npx ยังไม่ได้รันตรงตัว (เหมือนข้อค้างของ LAB 9) |
| `git log --grep "baseline: ระบบที่รับมอบ"` จาก PowerShell | ภาษาไทยใน argument ของ git บน PS 5.1 ยังไม่ได้ทดสอบ · มีทางสำรองเป็น id ใน HANDOVER-CHECK.md |
| `fast_track/README.md` · `README-PART-B.md` | ไม่อยู่ในขอบเขตงานนี้ → พรอมต์ LAB 10–12 ในสองไฟล์นี้ยังเป็นฉบับก่อน PF6b |
