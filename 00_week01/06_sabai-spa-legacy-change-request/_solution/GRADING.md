# 🔑 เกณฑ์ตรวจผู้สอน · บท 06 สบายใจ สปา: รับงานแก้ระบบเดิมด้วย Change Request

> ⚠️ **สำหรับผู้สอนเท่านั้น · ห้ามคัดลง README** · README ของบทแสดงเฉพาะรูบริก 20 ข้อ (ข้อความเดียวกับข้อ 2) · หมายเหตุผู้ตรวจ ค่าอ้างอิง และคำตอบผิดที่พบบ่อยอยู่ที่นี่ที่เดียว
> ที่มา: `_design/LESSON-PLAN.md` §6 §7 §9 · `_design/PROMPTS.md` · `_design/CR-DESIGN.md` · `_design/CODEBASE-NOTES.md` · **ผลรันจริง** `_design/results/LAB0–12_RESULT.md` (12 ต.ค. 2026 · รันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433)
> ค่าในคอลัมน์ "รอบจริง" = สิ่งที่ runner ได้ · ใช้เทียบงานผู้เรียน · LAB 11–12 เติมผลรอบจริงแล้ว · ข้อสอบตรวจด้วย [EXAM-KEY.md](EXAM-KEY.md) + [grader/README.md](grader/README.md)

## สารบัญ

1. [วิธีให้คะแนน](#1-วิธีให้คะแนน)
2. [รูบริก 20 ข้อ + วิธีตรวจ](#2-รูบริก-20-ข้อ--วิธีตรวจ)
3. [ตรวจทีละ LAB](#3-ตรวจทีละ-lab)
4. [คำตอบผิดที่พบบ่อย (จากรอบจริง)](#4-คำตอบผิดที่พบบ่อย-จากรอบจริง)
5. [ค่าที่ต้องตรงเป๊ะต่อ CR](#5-ค่าที่ต้องตรงเป๊ะต่อ-cr)

---

## 1. วิธีให้คะแนน

| เรื่อง | กติกา |
|---|---|
| คะแนนเต็ม | 20 ข้อ ข้อละ 1 · **ดีมาก ≥ 18 · ใช้ได้ 14–17 · ต้องแก้ < 14** |
| หลักฐาน | ให้คะแนนจาก **ไฟล์และ git log ใน repo ของผู้เรียน** ไม่ใช่คำพูดในแชท · ไม่มีในไฟล์ = 0 |
| ครึ่งคะแนน | ไม่มี · ก้ำกึ่งให้ดูคอลัมน์ "ได้ 0 ถ้า" ถ้าไม่เกิดให้ 1 |
| LAB 0 | ไม่มีคะแนน · เป็นเงื่อนไขก่อนตรวจ (ไม่มี `rea-lab:6.4.0` = ข้อ 2 18 ไม่มีหลักฐาน REA) |
| ธงแดง (ตัดทันที) | แก้ไฟล์ใน `e2e-legacy/` · เปลี่ยนค่าคาดหวังใน `check-rules.mjs` / `tests/golden/` โดยไม่มีแถวใน `ORACLE-CHANGES.md` → ข้อ 11 = 0 และผล regression ข้อ 17 ใช้ไม่ได้ · รัน `golden --update` หลังแก้โค้ด → ข้อ 6 11 = 0 · `docker compose down -v` / ลบ volume → ข้อ 14 20 = 0 · รหัสผ่าน/cookie ในไฟล์ `.md` หรือ commit `.har` → ข้อ 2 = 0 |
| AI ไม่ deterministic | ตัวเลขนับ (endpoint · แถวตาราง · เวลา) ต่างจากรอบจริงได้ · ที่ **ต้องตรงเป๊ะ** คือค่าใน [ข้อ 5](#5-ค่าที่ต้องตรงเป๊ะต่อ-cr) (ร้านยืนยันใน ③ หรือมาจาก SQL บน seed) และตัวนับ baseline 90/90 · 38/1/3 · 62/62 |
| expected-fail | Playwright นับ `test.fail()` ที่ล้มตามคาดรวมใน "passed" · ผู้เรียนต้องแยก **ผ่านจริง / ล้ม / expected-fail** ได้ (ดูข้อ 4.1) |

ตรวจเร็วจากรากบทของผู้เรียน (Git Bash):

```bash
git log --oneline                                   # ทุก CR: "CR-0N test: …" มาก่อน "CR-0N: …"
git diff <baseline> -- web/scripts/check-rules.mjs tests/golden e2e-legacy | wc -l   # ต้อง 0 (หรือทุกจุดมีแถวใน ORACLE-CHANGES)
grep -rln "@2026\|sabai_session=" --include=*.md .  # ต้องว่าง (ไม่มีรหัสผ่าน/cookie)
git ls-files "*.har" "rea-out/*" "backups/*"        # ต้องว่าง
grep -c "\[D:CR-0" docs/impact/CR-0*.md             # ทุกฉบับ > 0
```

---

## 2. รูบริก 20 ข้อ + วิธีตรวจ

**A. รับมอบและเข้าใจ (LAB 1–3)** · **B. รั้วและตาข่าย (LAB 4–5)** · **C. Change Request (LAB 6–10)** · **D. Regression (LAB 11)** · **E. ส่งมอบ (LAB 12)** (ข้อความเต็มเหมือน `LESSON-PLAN.md` §9)

| ข้อ | เกณฑ์ (ย่อ) | ไฟล์หลักฐาน | ได้ 1 เมื่อ | ได้ 0 ถ้า | รอบจริง |
|---|---|---|---|---|---|
| 1 | HANDOVER-CHECK ตัวเลขจริง · คำอ้าง ✅/❌/⚠️ · ข้อแดงจำแนกโดยไม่แก้เทสต์ | `HANDOVER-CHECK.md` | 90/90 · 38/1/3 · TC-SEC-05 = เทสต์ล้าสมัย · คำอ้าง "reset ปิดใน production" = ❌ · "ผ่านหมดยกเว้น 3" = ❌ | นับ `x` เป็นล้ม 4 · TC-SEC-05 = บั๊ก/แก้เทสต์ · คัดคำอ้างมาเป็นผล | 19 คำอ้าง ✅ 12 ❌ 2 ⚠️ 5 |
| 2 | REA-INVENTORY แยก static/runtime/inference/unknown · `[E ev_…]` ทุกแถว · ไม่มี "ไม่มี X" | `docs/REA-INVENTORY.md` | ทุกแถว endpoint มี ev_ · `/api/me` `/api/services` เขียนเป็น inference/unknown | ประโยค "ระบบไม่มี…" / "route นี้ไม่ได้ใช้" · มีรหัสผ่านในไฟล์ | 25/25 แถวมี ev_ · `grep "ระบบไม่มี"` = 0 |
| 3 | SYSTEM-MAP อ้าง file:line · ตรวจทาน 5 ข้อด้วยตาตัวเอง | `SYSTEM-MAP.md` หัวข้อ "ตรวจทานโดยคน" | 5 แถวสุ่ม (ไม่ cherry-pick) · จดแถวที่อ้างไม่ครบและแก้แล้ว | ไม่มีส่วนตรวจทาน · ตรวจทานด้วย AI อีกตัว | ตรง 3 · ไม่ครบ 2 · บรรทัดผิด 0 |
| 4 | triangulation REA/source/DB · SPEC-GAPS เป็นคำถาม | `SYSTEM-MAP.md` · `docs/SPEC-GAPS.md` | มีคอลัมน์ DB (constraint) · ⚠️ มีคำถามคู่ใน SPEC-GAPS · ไม่ตัดสินเองว่า SPEC หรือโค้ดถูก | SPEC-GAPS เขียนว่า "แก้ SPEC แล้ว" | 23 แถว ✅ 17 ⚠️ 6 ❌ 0 · SPEC-GAPS 13 |
| 5 | CLAUDE.md สั้น · ทดสอบรั้วในเซสชันใหม่ | `CLAUDE.md` · `.claude/settings.json` | ≤ ~60 บรรทัด · ห้าม `down -v` · กติกา migration · `Edit(e2e-legacy/**)` ถูกปฏิเสธใน **เซสชันใหม่** | ทดสอบในเซสชันเดิม · ใช้ `Write(...)` อย่างเดียว · ไม่มีข้อความปฏิเสธจริง | 45 บรรทัด · ปฏิเสธจริง · SHA-256 เท่าเดิม |
| 6 | golden นิ่ง 2 รอบ · ตัดฟิลด์ที่เปลี่ยนเอง | `tests/golden/README.md` | 2 รอบติดผ่าน · ตัด `id` `bookingId` `createdAt` + เหตุผล · SHA-256 ย่อ | รอบสองไม่ผ่าน · ไม่ตัด id → ล้มทุกครั้ง | 62/62 ×2 |
| 7 | known issue ล็อกคู่ · seam ปิดได้ | `e2e-cr/tests/known-issues.spec.ts` · `KNOWN-ISSUES.md` · clock route | บั๊กมีคู่ ① ล็อก ② `test.fail` · ข้อไม่แน่ใจ (owner ยกเลิก) = ล็อกอย่างเดียว + ถามร้าน · clock 404 เมื่อ `ALLOW_TEST_RESET=0` | แอบแก้บั๊ก · `test.fail` ที่ "ผ่านโดยไม่คาด" (จับข้อความวูบ KI-01) | KI-01 KI-02 คู่ · KI-03 ล็อกเดียว · 404 |
| 8 | mutant 3 ตัว คืนไฟล์ครบ · ตัวรอดอธิบายรูได้ | `tests/golden/README.md` · `git status` | ตาราง mutant × ชุด · `git diff -- web/lib/rules/` = 0 · อธิบายว่า e2e-cr จับ 0/3 เพราะล็อกแค่เดี่ยวไม่ล็อกอิน | ไม่คืนไฟล์ · สรุป "ตาข่ายดีครบ" โดยไม่พูดถึงชั้นที่จับไม่ได้ | golden 3/3 · check-rules 3/3 · e2e-cr 0/3 |
| 9 | ทุก CR มีคำถาม + อธิบายของเดิม + impact ก่อน diff · ป้ายครบ | `docs/impact/CR-0N.md` (อยู่ใน commit แดง) | คำถามเขียนก่อนเปิด answers · ตาราง ไฟล์ × เทสต์ × grep · แชท/i18n/DB · ทุกค่ามี `[D:CR-0N]` หรือ `[E]` | impact หลังแก้ · ค่าคาดหวังไม่มีป้าย · ใช้ [E] ที่ขัด [D] เป็นค่าคาดหวัง | ครบ 5 ฉบับ |
| 10 | commit แดงก่อน commit แก้ทุก CR | `git log` | ลำดับ test → fix ทุก CR · log แดงอ้างเหตุผลเรื่องพฤติกรรม (ไม่ใช่ syntax) | commit เดียว · แดงเพราะเทสต์เขียนผิด | 5/5 CR |
| 11 | oracle เดิมไม่เปลี่ยน หรือมีแถว ORACLE-CHANGES | `git diff` · `docs/ORACLE-CHANGES.md` | diff ว่าง และตารางว่างพร้อมเหตุผล | แก้ e2e-legacy (เช่น TC-BOOK-07) ให้ผ่าน | diff ว่างทุก LAB · ตารางว่าง |
| 12 | CR-02 ทั้ง 2 ฝั่งวันมีผล · นัดเก่าไม่เปลี่ยนยอด | `tests/cr02.mjs` | 31 ต.ค. 23:59 / 1 พ.ย. 00:00 · จองก่อน-นัดหลัง · B04 ฿4,500 · `discountKind` ของ Gold กลุ่ม 3 | ใช้วันนัด (`input.date`) เป็นวันมีผล · ตรวจแค่ยอด | 19/19 · C7 C8 C9 C15–C17 |
| 13 | CR-03 พร้อมกัน (สมาชิก + ไม่ล็อกอิน) + แชท · BOOK-06 ยัง `SLOT_TAKEN` | `tests/cr03.mjs` · `cr03.spec.ts` | `[201, 409]` ทั้ง 2 แบบ · แชท ≥ 1 ภาษา · คนละคนพร้อมกันยัง `SLOT_TAKEN` | กันแค่ปุ่มหน้าเว็บ · ไม่มีเคสพร้อมกัน | C10 C11 C12 C15 C16 |
| 14 | CR-04 migration 2 ครั้งบนฐานที่มีนัดใหม่ · reset 2 ครั้ง · ไม่ `down -v` | `db/migrations/001_*.sql` · `docs/MIGRATION-RUNBOOK.md` | log `INSERT 0 3` → `INSERT 0 0` exit 0 · นัดใหม่อยู่ · reset 200 ×2 · มี `.down.sql` + สำรอง | แก้แค่ `db/init` · ลืม `TABLES` → reset 500 · ลบ volume | ครบ |
| 15 | CR-01 self-overlap + นักบำบัดคนเดิมไม่ว่าง + Playwright 3 เบราว์เซอร์ | `tests/cr01.mjs` · `cr01.spec.ts` | B02 19:00→19:30 = 200 · B01 14 ต.ค. 16:00 = 409 + `reschedule-slots` ไม่ว่าง · spec 3 เบราว์เซอร์ | ใช้ `/api/slots` เดิม · ยกเลิก+จองใหม่ | 22/22 · 6/6 |
| 16 | CR-05 SQL ก่อนโค้ด · CSV BOM | `docs/impact/CR-05.md` (ใน commit แดง) · `tests/cr05.mjs` | SQL + ผลอยู่ใน commit ก่อน commit แก้ · BOM `EF BB BF` · ภาษาไทยตรงตัว | ลอกตัวเลขจากหน้ารายงานที่เพิ่งทำ | 12/12 · BOM ✓ |
| 17 | REGRESSION-REPORT ตัวเลขตรงการรันซ้ำ · 3 เบราว์เซอร์ | `REGRESSION-REPORT.md` | แยกผ่านจริง/ล้ม/ef · TC-UI-02 webkit จำแนกพร้อมหลักฐาน | นับ "passed" ของ Playwright ตรง ๆ | `test:all` 106 / 1 / 7 (Playwright "113 passed · 1 failed") · TC-UI-02 webkit rerun ×3 ล้ม 2 → flaky เดิม (ไฟล์ `/skin` ไม่มี CR แตะ) |
| 18 | CR × REA เห็นไหม · ไฟล์ทุกไฟล์โยง CR · TRACEABILITY ครบ | `REGRESSION-REPORT.md` · `docs/TRACEABILITY.md` | CR ที่ REA ไม่เห็น (กฎฝั่งเซิร์ฟเวอร์) มีเทสต์ที่พิสูจน์แทน · HAR v2 + scenario v2 | "REA ไม่เห็น = ไม่ได้เปลี่ยน" | CR × REA 5 แถว (CR-02 ไม่เห็น → cr02 19/19 + golden) · diff `4a7908f..HEAD` 66 ไฟล์โยงได้ (⚠️ 3 ไฟล์คอร์ส) · HAR v2 `ev_ba70ee00` · scenario v2 `ev_d627ab35` |
| 19 | RELEASE-NOTES ภาษาคน + known issues · UAT ต่อ CR | `RELEASE-NOTES.md` · `UAT-CHECKLIST.md` | คุณจันทร์อ่านเข้าใจ · known issue ข้อ 6 ของ README เฉลย · ช่องลงชื่อ | ศัพท์เทคนิคล้วน · ไม่มี known issue | ยังไม่แก้ 16 ข้อ (ครบ 6 ที่คาด) · รอยืนยัน 7 · UAT 31 แถว 5 CR · ลงชื่อ 4 ช่อง · ไม่มี API/รหัส error ใน RELEASE-NOTES |
| 20 | ซ้อมถอยกลับจริง · smoke exit 1/0 · runbook ไม่มี `down -v` | `docs/DEPLOY-RUNBOOK.md` · `tests/smoke.mjs` | ผลซ้อมจริง: นัดอยู่ครบหลัง down→up · smoke อ่านอย่างเดียว | smoke reset/สร้างข้อมูล · ไม่ได้ซ้อมจริง | smoke 7/7 → 0/7 exit 1 → 7/7 · B14 รอด down.sql → up และ DB down→up · cr04 14/14 · runbook มี `down -v` เฉพาะในคำเตือนห้าม |

---

## 3. ตรวจทีละ LAB

### LAB 0 · เช็กเครื่อง (ไม่มีคะแนน)

| ตรวจ | ต้องได้ | ผิดบ่อย / รอบจริง |
|---|---|---|
| พอร์ต | อธิบายว่า 3000 อยู่ในช่วงที่ Windows จอง (`netsh … excludedportrange`) จึงใช้ 4000 | รอบจริง: 23 ช่วง · 2970–3069 ครอบ 3000 · ช่วงต่างกันแต่ละเครื่อง/หลังรีบูต |
| 4000 ไม่ว่าง | บอกว่าเป็น container ไหน (`docker ps`) · ปิดเว็บบท 05 หรือใช้ `$env:WEB_PORT` | `Get-NetTCPConnection` เห็นแค่ `com.docker.backend`/`wslrelay` ไม่บอกชื่อ container |
| REA | `mcp doctor` exit 0 | รอบจริง: tools 170/170 · 3.4 วิ |
| execution policy | ไม่ต้องแก้ (เรียก `-ExecutionPolicy Bypass -File`) | Process = Bypass มาจากเครื่องมือของ agent ไม่ใช่ค่าถาวรของเครื่อง |
| อยู่ใน repo อื่นไหม | เทียบ `git rev-parse --show-toplevel` กับโฟลเดอร์ปัจจุบัน | ถ้าบทเป็น repo ของตัวเอง toplevel = โฟลเดอร์นี้ = ไม่ใช่ "repo อื่น" |

### LAB 1 · รับมอบ (รูบริก 1)

- **หลักฐาน:** `HANDOVER-CHECK.md` · commit baseline · log ของ check-rules และ e2e-legacy
- **ค่าอ้างอิง:** check-rules 90/90 (~20 วิ) · e2e-legacy 42 รายการ (api 6 + chromium 36) · Playwright "41 passed · 1 failed" = ผ่านจริง 38 + expected-fail 3 (TC-SEC-04 · TC-GC-04 · TC-TRN-03) + ล้ม 1 (TC-SEC-05)
- **จำแนกที่ถูก:** TC-SEC-05 = **เทสต์ล้าสมัย** (U04 ใช้คอร์สของ U01 ได้ 422 `COURSE_UNAVAILABLE` ไม่ใช่ 403/404 · ไม่สร้างนัด คอร์สไม่ลด) · TC-SEC-04 / TC-GC-04 / TC-TRN-03 = บั๊กที่ผู้รับเหมาติดป้าย KNOWN-ISSUE
- **คำอ้างที่ต้องได้ ❌:** "ปิด reset ใน production" (compose `${ALLOW_TEST_RESET:-1}` + `config.ts` ค่าเริ่ม "1" + reset 200) · "ผ่านหมดยกเว้น 3" (TC-SEC-05 ล้มเพิ่ม · README-LEGACY เขียนเองว่าแดงค้าง) · เลข H ของผู้เรียนต่างจากเฉลยได้ ให้ตรวจที่ **เนื้อหา**
- **ผิดบ่อย:** นับ `x` ใน list reporter เป็น "ล้ม 4" · แก้ TC-SEC-05 ให้เขียว · ไม่ได้ commit baseline เพราะเจอ "nothing to commit" (ต้องเขียน HANDOVER-CHECK ก่อนแล้ว commit)

### LAB 2 · REA black-box (รูบริก 2)

- **ค่าอ้างอิง:** static endpoint 9 (`/api/price` `/api/bookings` `/api/auth/login` `/api/auth/logout` `/api/test/reset` `/api/chat` `/api/courses` `/api/quiz` `/api/giftcards`) · route file 25 · หน้า 14 · coverage partial · HAR 7 endpoint / 10 ครั้ง · scenario 12/12 ฿1,000 ผ่าน `sabai06-net`
- **ต้องอธิบาย:** `/api/slots` `/cancel` `/admin/bookings?date=` เห็นจาก HAR แต่ static ไม่เห็น (URL ประกอบตอนรัน) · `/api/me` `/api/me/bookings` `/api/services` ไม่อยู่ใน HAR (อ่านฝั่งเซิร์ฟเวอร์) → inference/unknown ไม่ใช่ "ไม่ได้ใช้" · body ของ login ว่างเพราะ `--sensitive-value`
- **ผิดบ่อย:** สรุป "route ที่ไม่เห็น = ไม่ได้ใช้" · ใช้ [E] เป็น "ควรทำ" · เปิดไฟล์ JSON 34 MB ทั้งไฟล์ · commit `rea-out/` · ไม่รู้ว่า `record-har.mjs` จอง + ยกเลิกนัด (ข้อมูลเปลี่ยน ต้อง reset ก่อน LAB ที่ต้องการ seed)

### LAB 3 · แผนที่ระบบ (รูบริก 3 4)

- **ค่าอ้างอิง:** 25 ไฟล์ / 26 handler (`/api/quiz` มี GET + POST) · BR-01–20 · 19 ตาราง · CHECK 51 · FK 25 · EXCLUDE 2 (`booking_room_no_overlap` · `booking_slot_no_overlap`) · `room_id = 1` 2 ที่ · `TABLES` ใน `testmode.ts:11-15` · init รันเฉพาะ volume ว่าง · `PackageCalc.tsx:24` คิดราคาซ้ำ · ข้อความเวลาเปิดซ้ำ `i18n.ts` + `chat.ts`
- **SPEC-GAPS ที่ควรมี:** พอร์ต/ชื่อ container เก่า (`sabai-*` · 3000) · ระยะรถปัดทศนิยม · ฐานแต้มหัก Gift Card · แพ็กเกจไม่ได้ส่วนลดระดับ · reset เปิดค่าเริ่ม · logout ไม่ revoke · owner ยกเลิก (≥ 7 แถว · รอบจริง 13)
- 🔒 ถ้าผู้เรียนเจอ "กดใช้บริการเสร็จได้ก่อนเวลานัด" (G9) = ให้คะแนนตามปกติ แต่ **ห้ามนำไปเป็นตัวอย่างในห้อง** (ข้อสอบชุด B ข้อ 5)
- **ผิดบ่อย:** นับ constraint จาก `\d booking` + `\d booking_slot` อย่างเดียว (ได้ CHECK 23 / FK 6) · คัด "ERD 17 ตาราง" จากหัวไฟล์ schema (จริง 19) · grep `"/api/` พลาด template literal 4 จุด · ตรวจทานแบบเลือกแถวที่มั่นใจ (ให้สุ่มด้วยคำสั่ง)

### LAB 4 · CLAUDE.md + รั้ว (รูบริก 5)

- **ต้องเห็น:** คำสั่งรันทุกชุด (check-rules · e2e api+chromium · test:all · reset · health) · ห้าม `down -v` · ป้าย [D:CR-0N]/[E] · migration = `db/migrations/` ทางเดียว + `docker cp` + `psql -v ON_ERROR_STOP=1 -f` · กติกาภาษาไทยใน PowerShell · ห้ามแก้ oracle
- **ทดสอบรั้ว:** เซสชันใหม่ (`claude` โหมดปกติ หรือ `acceptEdits`) → ข้อความ *"File is in a directory that is denied by your permission settings."* · `git status` ว่าง
- **ผิดบ่อย:** ทดสอบในเซสชันเดิม (settings ยังไม่โหลด) · ใช้ `Write(...)`/`Read(...)` แทน `Edit(...)` · เชื่อว่ารั้วกัน shell ได้ (ไม่กัน → ต้องเขียนห้ามใน CLAUDE.md) · commit แค่ 4 ไฟล์แล้ว CLAUDE.md อ้าง `@SYSTEM-MAP.md` ที่ไม่อยู่ใน repo · `@SYSTEM-MAP.md` ~46 KB โหลดทุกเซสชัน (รับได้ แต่ควรรู้ต้นทุน)

### LAB 5 · ตาข่าย (รูบริก 6 7 8)

- **seam:** clock เปลี่ยน "วันนี้" โดยนัดยังอยู่ (ต่างจาก reset ที่ล้างข้อมูล) · 404 เมื่อปิด · 422 ค่าไม่ถูก · ไม่แตะ `web/lib/rules/` `booking.ts`
- **golden:** 40–60 เคสราคา (รอบจริง 50 + slots 6 + คิว 6 = 62) · ต้องมี U07 ยอดสะสม ฿10,000 พอดี ไม่งั้น X1 รอด
- **characterization:** ยอด ฿1,000 = [E ev_8dc23d9f] ของ LAB 2 · aria snapshot เป็นข้อความตรง (`row "ยอดสุทธิ ฿1,000"`) ไม่ใช่ regex ที่ Playwright สร้าง
- **mutant:** X1 `tier.ts` `>=`→`>` · X2 `transport.ts` ที่นั่ง 4→5 · X3 `pricing.ts` กลุ่ม 10→15 · คืนด้วย `git checkout -- <ไฟล์>` · รอบจริง: ถูกจับทุกตัวโดย golden + check-rules · e2e-cr 0/3
- **ผิดบ่อย:** `tests/golden/README.md` ไม่อยู่ใน commit (exclude `README.md` ไม่ anchor) · KI-01b `test.fail` "ผ่านโดยไม่คาด" เพราะ `toBeVisible` จับข้อความวูบ ~250 ms (ต้องรอ 422 แล้วรอ 200 รอบถัดไปก่อน assert) · เขียน test.fail ให้ KI-03 ทั้งที่ยังไม่รู้ว่าบั๊ก · นับ "18 passed" โดยไม่แยก expected-fail 6

### LAB 6 · CR-02 ส่วนลดกลุ่มขั้นบันได (รูบริก 9 10 11 12)

- **อธิบายของเดิม (ต้องมี file:line):** `bestPercent()` `pricing.ts:47-57` (กลุ่ม `people >= 4 ? 10 : 0` · เลือก `>` เท่ากันได้ตัวแรก = กลุ่ม) → `calcPrice()` → `buildQuote()` `booking.ts:178-188` · "วันนี้" = `clock()` ส่งเป็น `today` · calcPrice ไม่รู้วันที่จอง
- **ออกแบบที่ดี:** ตารางอัตราตามวันมีผลจุดเดียว · พารามิเตอร์ใหม่ไม่ส่ง = กฎเดิม (unit test ใน check-rules เรียก `calcPrice` ตรง) · ส่ง `today` (วันที่จอง) ไม่ใช่ `input.date` (วันนัด)
- **รอบจริง:** แดง 10/19 (ล้ม C2 C4 C5 C8 C9 C11 C13 C14 C17) → 19/19 · check-rules 90/90 diff ว่าง · golden 62/62 · e2e-legacy 38/1/3
- **ผิดบ่อย:** ดูข้อ 4.3 (วันที่จอง ≠ วันนัด) · ข้อ 4.2 (Plan mode) · เปลี่ยนค่าคงที่ตรง ๆ → E26/E28/E79 + golden แดง แล้วแก้ oracle ให้ผ่าน (ธงแดงข้อ 11) · เคส Gold กลุ่ม 3 ตรวจแค่ยอด (เขียวตั้งแต่ก่อนแก้)

### LAB 7 · CR-03 จองซ้ำ (รูบริก 9 10 11 13)

- **ทำซ้ำก่อน:** ไม่ล็อกอิน S02 13 ต.ค. 10:00 คุณสมชาย → 201 ทุกครั้ง (รอบจริง B14 B15 B16 · พร้อมกัน B17 B18) = [E] ขัด [D:CR-03] → **หลักฐานบั๊ก ไม่ใช่ค่าคาดหวัง**
- **ต้นเหตุ:** `createBooking` ตรวจราคา/นักบำบัด/ห้องแล้วจัดนักบำบัดว่างคนถัดไป · DB EXCLUDE ผูกนักบำบัด/ห้อง ไม่ผูกคน · หน้าเว็บกันได้แค่ `disabled={busy}` (แท็บเดียว) · API ตรง/แชทไม่มีปุ่ม
- **ออกแบบที่ดี:** ตรวจในฝั่งเซิร์ฟเวอร์ใน transaction เดิม + กันพร้อมกัน (รอบจริง `pg_advisory_xact_lock` ต่อคน · ไม่มี migration เพราะฐานจริงมีนัดซ้ำอยู่แล้ว constraint สร้างไม่ผ่าน) · normalize เบอร์ตอนเทียบ ไม่เปลี่ยนค่าที่บันทึก · ข้อความ 3 ภาษาใน API + แชท
- **ผิดบ่อย:** ดูข้อ 4.1 (TC-BOOK-07) · แก้แค่ปุ่มหน้าเว็บ · ส่ง `lang` ใน body แล้วคาด error ภาษานั้น (error ใช้ cookie) · ล็อกด้วย FOR UPDATE ของลูกค้าอย่างเดียว (ไม่ล็อกอินไม่มีแถวให้ล็อก)

### LAB 8 · CR-04 migration วันหยุดร้าน (รูบริก 9 10 11 14)

- **ต้องตอบได้ก่อนแก้:** ทำไม init ไม่พอ (`db/compose.yaml` mount `./init` → รันเฉพาะ volume ว่าง) · seed ของ reset มาจาก `02-seed.sql` ที่ COPY เข้า image ตอน build · reset `TRUNCATE` ตามรายการ `TABLES` → ตารางใหม่ต้องเติม TABLES + seed + rebuild
- **รอบจริง:** ดูข้อ 4.4 · `cr04` 3/14 → 14/14 · ลำดับ error: SERVICE → คน → `DATE_OUT_OF_RANGE` → `SHOP_CLOSED` → `SLOT_INVALID` · ติดตั้งใหม่ 20 ตาราง · image ถอย `before-cr04`
- **ผิดบ่อย:** แก้ `db/init` อย่างเดียว · rebuild เว็บก่อนรัน migration (slots/price/bookings/reset 500) · ถอยด้วย `down.sql` ก่อนถอยเว็บ · `Get-Content | docker exec -i` ทำภาษาไทยเป็น `?` · เห็น psql ภาษาไทยเพี้ยนบนจอแล้วไปแก้ข้อมูล (ตรวจด้วย `SELECT name_th = 'วันปิยมหาราช'` → `t`) · แชทได้ 422 แทนคำตอบบอท (ต้องเช็กวันหยุดในขั้นเลือกวัน) · ไม่ทำส่วน ข = **ไม่หักคะแนน** ถ้าถามก่อนและบันทึกใน REGISTER

### LAB 9 · CR-01 เลื่อนนัด (รูบริก 9 10 11 15)

- **ต้องตอบได้:** เวลาเก็บที่ `booking.start_at/end_at` + `booking_slot.period` (ต้อง UPDATE เอง) · `booking.period` GENERATED · ทำไม `/api/slots` ใช้ไม่ได้ (นับนัดตัวเองเป็นไม่ว่าง · ตอบว่างถ้า "ใครก็ได้" ว่าง) · ทำไม "ยกเลิก + จองใหม่" เพี้ยน (คอร์ส · เดือนเกิด · ราคาใหม่ · รหัสเปลี่ยน · รอบเดิมหลุด)
- **รอบจริง:** 0/22 → 22/22 · spec 0/6 → 6/6 · `test:all` 105/2/7 (TC-UI-02 webkit = flaky เดิม ดูข้อ 4.6)
- **ผิดบ่อย:** แก้แค่ `busySlots` → R10 ได้ `DUPLICATE_BOOKING` ปลอมจาก CR-03 (นับนัดตัวเอง 3 จุด) · ใช้ `canUseCourse()` เดิมกับนัดที่กันครั้งแล้ว (422 ทุกครั้งสำหรับคอร์สที่เหลือ 1) · ลืม `booking_slot.period` (R17 จับ) · INSERT slot ใหม่ก่อนปิดเก่า → 23P01 → 409

### LAB 10 · CR-05 รายงาน + CSV (รูบริก 9 10 11 16)

- **ต้องตอบได้:** ต่อยอดจาก `queueForDate()` `admin.ts` · สิทธิ์ owner (401/403) · เงิน `NUMERIC` → สตางค์ (`toSatang`) → บาท · ตัดวันตามเวลาไทย `[from 00:00+07, to+1 00:00+07)`
- **รอบจริง:** ดูข้อ 4.5 และข้อ 5 · แดง 1/12 (R12 แชทไม่รั่ว ผ่านตั้งแต่ก่อนแก้ = ปกติ) → 12/12 · ตรวจไขว้รายงาน = Σ ตารางคิวหลังร้าน 3/3 · R10 ตั้งนาฬิกา 12 ต.ค. 14:00 ก่อน owner กดเสร็จ B01 (D12)
- **ผิดบ่อย:** ใช้ `new Date("2026-09-01")` (UTC) — seed ไม่มีนัดตกขอบ (`q_tz` = 0) จึงยังเขียว → ถามผู้เรียนให้อธิบาย ไม่ใช่ดูแค่เทสต์ · บวกเงินเป็น float · CSV ไม่มี BOM · ตัด `start_at > now` ออกจากยอดนัดยืนยัน (ร้านนับตามสถานะ)

### LAB 11 · regression เต็ม + REA เทียบเวอร์ชัน (รูบริก 17 18)

**รอบจริง (ค่าอ้างอิง · รันที่ 4100/5533):**

| ชุด | ผล | เวลา |
|---|---|---|
| check-rules · golden | 90/90 · 62/62 | 19.0 · 1.2 วิ |
| cr01–cr05 | 22 · 19 · 18 · 14 · 12 (เขียวทั้งหมด) | 2.9–5.3 วิ/ชุด |
| e2e-cr 3 เบราว์เซอร์ | 39: ผ่าน 33 · ef 6 (KI-01b KI-02b ×3) · ล้ม 0 | 104 วิ |
| e2e-legacy `test:all` | 114: ผ่าน 106 · ef 7 · ล้ม 1 (TC-SEC-05) · Playwright "113 passed · 1 failed" | 12.8 นาที |
| TC-UI-02 webkit `--repeat-each=3` | 1/3 (flaky เดิม) | 38 วิ |
| REA compare v1↔v2 | `changed 12 · unknown 711 · added 0` · `ev_ea036036` | 12 วิ (+ analyze v2 49.1 วิ) |
| HAR v2 | 7 endpoint status/คีย์เท่า v1 · `ev_ba70ee00` | 10 วิ |
| scenario v2 | 12/12 ฿1,000 · `ev_d627ab35` | 4.1 วิ |

- **CR × REA:** CR-01 เห็น (`account/page` changed + route ใหม่) · CR-03/04 เห็นทางอ้อม (chunk i18n `8561` changed · route `/api/holidays`) แต่ตัวกฎไม่เห็น · CR-05 หน้าใหม่เป็น `unknown` ไม่ใช่ `added` · CR-02 ไม่เห็นเลย → ผู้เรียนต้องชี้ cr02 + golden
- **ผิดบ่อย:** อ่านแค่ `added 0` แล้วสรุปว่าไม่มีหน้าใหม่ · หยุดเพราะ TC-SEC-05 แดง (เป็น baseline) · รัน REA analyze ขนานกับ e2e 3 เบราว์เซอร์ (webkit flaky) · เก็บ HAR แล้วไม่ reset (มี B14 ค้าง)

- **คาด (ยืนยันแล้วในรอบจริง ตามตารางบน):** REA static เห็นเฉพาะ chunk ฝั่งเบราว์เซอร์ที่เปลี่ยน (CR-01 `/account` · CR-05 หน้าใหม่) · CR-02 CR-03 (กฎฝั่งเซิร์ฟเวอร์) ไม่เห็น → ต้องชี้เทสต์ที่พิสูจน์แทน · "REA ไม่เห็น ≠ ไม่ได้เปลี่ยน"

### LAB 12 · ส่งมอบ + ซ้อมถอยกลับ (รูบริก 19 20)

**รอบจริง:** smoke 7 ข้อ (health · services · วันหยุด 3 วัน · `/book` · CR-01 GET+POST ไม่ล็อกอิน 401 · CR-05 401) → 7/7 exit 0 · หยุดเว็บ 0/7 exit 1 · หลังถอย/ขึ้น 7/7 exit 0 · สำรอง 53,469 B · B14 รอด `down.sql` (`to_regclass` ว่าง) → up ซ้ำ `INSERT 0 3` → DB down→up (ไม่มี `-v`) · cr04 14/14 · RELEASE-NOTES ยังไม่แก้ 16 / รอยืนยัน 7 · UAT 31 แถว โยง TC 30/31 · REGISTER "รอตรวจรับ (UAT)" ×5 · commit `e768ef9` + `ab04036`

- **ข้อสังเกตตอนตรวจ:** ขั้น 6 `node tests/cr04.mjs` reset ข้อมูล → B14 หาย **หลัง**พิสูจน์แล้ว (ไม่ใช่ถอยทำหาย) — ผู้เรียนต้องจดหลักฐาน B14 ก่อนรัน · การซ้อมถอยใน LAB นี้ถอยแค่ DB ขณะเว็บหยุด (R1 สลับ image "ไม่ได้วัด" = ยอมรับได้ถ้าเขียนตรง ๆ) · smoke อ่านอย่างเดียวพิสูจน์ CR-02/03 ไม่ได้ → ต้องโยงไป UAT
- **ได้คะแนนเพิ่ม (ไม่บังคับ):** ตรวจ UAT บนหน้าเว็บจริงแล้วเจอ race กล่องเลื่อนนัด (2/4 รอบ) หรือรายงานแสดงรหัสนักบำบัดแทนชื่อ

- **ต้องเห็น:** smoke อ่านอย่างเดียว (ห้าม reset/สร้างข้อมูล) · runbook: สำรอง → tag image → migration → up → smoke → ถอยกลับ · ไม่มี `down -v` · known issues ที่ยังเหลือ (logout · owner ยกเลิก · reset เปิดค่าเริ่ม ฯลฯ) · 🔒 ถ้า RELEASE-NOTES มีเรื่อง "กดเสร็จก่อนเวลานัด" ห้ามนำไปทำภาพ/README

---

## 4. คำตอบผิดที่พบบ่อย (จากรอบจริง)

### 4.1 TC-BOOK-07 แดงหลังทำ CR-03 = ลำดับ error ไม่ใช่เทสต์ผิด

| | |
|---|---|
| อาการ | e2e-legacy รอบแรกหลังแก้ "40 passed · 2 failed" → ผ่านจริง 37 · ล้ม TC-SEC-05 (เดิม) + **TC-BOOK-07 (ใหม่)** · เทสต์คาด "เวลานี้ถูกจองแล้ว" แต่ได้ "คุณมีนัดในช่วงเวลานี้อยู่แล้ว (รหัส B02)" |
| ทำไม | TC-BOOK-07 ใช้ U02 จองคู่ทับ B02 **ซึ่งเป็นนัดของ U02 เอง** → เข้าทั้ง 2 เงื่อนไข (ห้องเต็ม และนัดซ้ำคนเดิม) · โค้ดใหม่ตรวจ BR-21 ก่อนตรวจคิว |
| ที่ถูก (รอบจริง) | จัดเป็น "ลำดับ error ที่ CR ไม่ได้กำหนด" · **ไม่แก้ e2e-legacy** · ย้าย `assertNoOverlapForPerson` ไปหลังตรวจนักบำบัด/ห้อง (ยังก่อน insert ใน transaction เดียว) · เพิ่ม C17 (U02 คู่ทับ B02 → `SLOT_TAKEN`) C18 (U02 เดี่ยวทับ B02 → `DUPLICATE_BOOKING`) · บันทึกใน impact §7 · รันชั้น 1+2 ซ้ำ → 38/1/3 |
| ให้ 0 ถ้า | แก้ข้อความคาดหวังใน `e2e-legacy` ให้ผ่าน (ข้อ 11) · ปิด/ข้ามเทสต์ · สรุปว่า "เทสต์เก่าผิด" โดยไม่มี CR |
| ให้เต็มถ้า | อธิบาย precedence ได้ และ impact ระบุลำดับ error ไว้ (หรือจับได้ตอน regression แล้วแก้ที่โค้ด) |

### 4.2 Plan mode เขียนไฟล์ไม่ได้

พรอมต์ส่วนที่ 1 ของ LAB 6–10 อยู่ใน Plan mode แต่สั่งให้ "ทำ `docs/impact/CR-0N.md`" · Plan mode ของจริงเขียนไฟล์ไม่ได้ → ที่ถูก: เสนอคำถาม + เนื้อหา impact **ในแผน** · หลังอนุมัติ (ออก Plan mode) บันทึก impact เป็นขั้นแรก แล้วจึงเขียนเทสต์ · รอบจริง LAB 7–10 ทำแบบนี้ (LAB 6 เขียนไฟล์ระหว่าง "plan" เพราะยังไม่รู้ปัญหา)
- **ตรวจ:** impact ต้องอยู่ใน commit แดง (`git show --stat <commit แดง>` มี `docs/impact/CR-0N.md`) · คำถามถึงร้านต้องเกิดก่อนเปิด answers (มีในแผน/แชท หรือไฟล์คำถามแยก)
- **อย่าหักคะแนน** ผู้เรียนที่ Agent ขอออกจาก Plan mode เพื่อบันทึกไฟล์ · **หักข้อ 9** ถ้าไม่มีไฟล์ impact เลย หรือ impact เกิดหลัง commit แก้

### 4.3 CR-02: "วันที่จอง" ≠ "วันนัด"

- CR-02 มีผลตาม **วันกดยืนยันการจอง** (Q1: 1 พ.ย. 2569 00:00 เวลาไทย) · "วันนี้" ของระบบ = `clock()` (test_today → TODAY → เวลาจริง) ส่งเข้า `buildQuote` เป็น `today`
- **กับดัก:** `buildQuote` มีทั้ง `today` และ `input.date` · ใช้ `input.date` ก็ผ่าน C2–C5 (นัด 5 พ.ย.) แต่ **C7 C15 C17 แดง** → เคสขอบต้องมี "จองก่อนวันมีผล นัดหลังวันมีผล" เสมอ
- **ตาข่ายเดิมช่วยไม่ได้:** check-rules / golden / e2e-legacy ล็อกวันที่ 10 ต.ค. → เขียวทั้งใช้วันที่ถูกและผิด · มีแค่ `tests/cr02.mjs` ที่จับได้
- **ค่าอ้างอิง:** จอง 31 ต.ค. 23:59 กลุ่ม 3 → ฿3,000 · 1 พ.ย. 00:00 → ฿2,850 · จอง 31 ต.ค. กลุ่ม 5 นัด 5 พ.ย. ฿4,500 → นาฬิกา 1 พ.ย. คิวยัง ฿4,500 · ใบสรุป 23:59 ฿3,000 → เลื่อนนาฬิกา 00:00 → ยืนยัน → 409 `PRICE_CHANGED` total ฿2,850 (กลไก `quotedTotal` เดิมทำงานเอง ไม่ต้องแก้โค้ดเพิ่ม)
- **กับดักข้างเคียง:** ระบบที่ส่งมอบ "วันนี้" ค้าง 10 ต.ค. ถ้าขึ้นจริงด้วย `ALLOW_TEST_RESET=1` → อัตราใหม่ไม่มีผลเอง · ควรอยู่ในความเสี่ยงของ CHANGE-REPORT

### 4.4 Migration idempotent: `INSERT 0 3` → `INSERT 0 0`

| ครั้ง | ผลที่ต้องเห็น (รอบจริง) |
|---|---|
| 1 | `CREATE TABLE` · `INSERT 0 3` · exit 0 (0.28 วิ) |
| 2 | `NOTICE: relation "shop_holiday" already exists, skipping` · `INSERT 0 0` · exit 0 (0.27 วิ) |
| ตรวจ | count 3 · `th_ok = t` · `zh_ok = t` · นัดใหม่ (B14) confirmed อยู่ · booking 14 ก่อน = 14 หลัง · customer 9 |

- ไฟล์ต้องมี `BEGIN` · `CREATE TABLE IF NOT EXISTS` · `INSERT … ON CONFLICT DO NOTHING` · `COMMIT` + `.down.sql` แยก
- **ผิดบ่อย:** เห็น NOTICE ครั้งที่ 2 เป็นตัวแดง `NativeCommandError` ใน PowerShell 5.1 แล้วสรุปว่า "รันซ้ำพัง" (ต้องดู `$LASTEXITCODE` = 0 และ `INSERT 0 0`) · ครั้งที่ 2 ได้ `INSERT 0 3` อีก (ไม่มี unique/ON CONFLICT → ข้อมูลซ้ำ) · ครั้งที่ 2 error `already exists` (ไม่มี `IF NOT EXISTS`) · ซ้อมบนฐานว่างแทนฐานที่มีนัดใหม่ · สำรองหลัง reset (ต้องสำรองก่อน)

### 4.5 CR-05: oracle จาก SQL ก่อนเขียนโค้ด

- ค่าคาดหวังทุกตัวต้องมาจาก **SQL บน seed ที่รันก่อนเขียนโค้ด** (ป้าย `[D:CR-05]` = นิยาม + `[E sql:q_…]` = ค่า) และอยู่ใน impact ของ **commit แดง** · ห้ามลอกจากหน้ารายงานที่เพิ่งทำ (จะอบบั๊กของตัวเองเป็นค่าคาดหวัง)
- รอบจริง: 9 คิวรี (`q_counts q_money q_points_txn q_course_txn q_pending q_therapist q_csv_sep q_tz q_days`) × 4 ช่วง · ไขว้แต้มกับ `point_txn` (19/14/33) · ไขว้คอร์สกับ `course_txn` · หลังทำ ตรวจไขว้รายงาน = Σ ตารางคิวหลังร้าน 3/3
- **ตรวจ:** `git show <commit แดง>:docs/impact/CR-05.md` มีตาราง SQL + ผล · ตัวเลขใน `tests/cr05.mjs` = ตัวเลขในตารางนั้น
- รอบจริงใช้ไฟล์ SQL + `docker cp` + `psql -v ON_ERROR_STOP=1 -f` แทน `psql -c` ของพรอมต์ (ตาม CLAUDE.md ข้อ 5) = **ถูก**

### 4.6 TC-UI-02 webkit แดงใน `test:all` = flaky เดิม (พิสูจน์ด้วย image เก่า)

- LAB 9 `test:all` 114 รายการ "112 passed · 2 failed" → ล้ม TC-SEC-05 (เดิม) + TC-UI-02 webkit (`/skin` อัปโหลดรูป → `skin-recs` ไม่ขึ้นใน 15 วิ) · ไฟล์ที่ CR-01 แตะไม่เกี่ยว `/skin`
- **วิธีพิสูจน์ที่ถูก (รอบจริง):** รันซ้ำเฉพาะตัว `--project=webkit -g TC-UI-02 --repeat-each=3` บน image ปัจจุบัน → ล้ม 2/3 · บน image `sabai06-web:before-cr04` (ก่อน CR-04 และ CR-01) ที่พอร์ตแยก → ล้ม 1/3 → ล้มบนโค้ดก่อน CR ด้วย = flaky ของเดิม · จดไว้ ไม่แก้เทสต์
- **ให้ 0 ถ้า:** แก้/ข้าม TC-UI-02 · เพิ่ม retries ใน config ของ e2e-legacy · สรุป "flaky" โดยไม่มีหลักฐานรันซ้ำบนโค้ดก่อน CR · หรือกลับกัน ไปย้อนแก้ CR-01 เพราะคิดว่าทำพัง

### 4.7 อื่น ๆ ที่เจอในรอบจริง

| เรื่อง | LAB | ที่ถูก |
|---|---|---|
| expected-fail แสดง `x` เหมือนล้ม · Playwright นับรวมใน "passed" | 1 5 6 9 | แยกด้วย `test.fail` ในไฟล์ / บรรทัด `N failed` / `--reporter=list,json` |
| `tests/golden/README.md` หายจาก commit | 5 | `git check-ignore -v` → `git add -f` · ตรวจ `git status` ก่อน commit |
| aria snapshot ที่สร้างอัตโนมัติเป็น regex | 5 | เขียนข้อความตรง + `/children: equal` หรือใช้ `data-amount` |
| e2e-cr จับ mutant 0/3 | 5 | สรุปว่า "snapshot หน้าจอ ≠ ตาข่ายของกฎ" ไม่ใช่ "ตาข่ายดี" |
| C9 Gold กลุ่ม 3 ยอดเท่าเดิม | 6 | ตรวจ `discountKind` (tier → group) ด้วย |
| error ภาษาไม่ตาม `body.lang` | 7 | ส่ง cookie `lang` ในเทสต์ · ไม่ลดความเข้มของเทสต์ |
| ลำดับ deploy / ถอยกลับ | 8 | migrate ก่อน rebuild · ถอย: เว็บก่อน `down.sql` |
| ติดตั้งใหม่ตรวจเร็วเกิน (`relation does not exist`) | 8 | รอ init เสร็จก่อนตรวจ (`pg_isready` อาจผ่านระหว่าง init) |
| คอร์สที่เหลือ 0 หลังกันครั้ง | 9 | ตรวจแค่วันหมดอายุ ไม่ใช้ `canUseCourse()` |
| เทสต์แดงไม่ครบทุกเคส | 6 7 8 10 | ปกติ: เคสล็อกของเดิม (cr02 10/19 · cr03 5/16 · cr04 3/14 · cr05 1/12) ต้องเขียวตั้งแต่ก่อนแก้ · ที่ต้องแดง = เคสพฤติกรรมใหม่ตาม impact §4 |

---

## 5. ค่าที่ต้องตรงเป๊ะต่อ CR

ค่าจาก `_design/results/LAB6–10_RESULT.md` (รันจริง · ตรงกับคำตอบร้าน ③ ทุกตัวที่ร้านให้ตัวอย่าง) · "วันนี้" = 10 ต.ค. 2026 10:00 หลัง reset

| CR | กรณี | ค่าที่ต้องได้ |
|---|---|---|
| CR-02 | S01 นัด 5 พ.ย. จอง 1 พ.ย. Silver (U08) กลุ่ม 2 / 3 / 4 / 5 / 6 / 7 | 422 `GROUP_TOO_SMALL` / ฿2,850 (5%) / ฿3,600 (10%) / ฿4,250 (15%) / ฿5,100 (15%) / 422 `GROUP_CALL_SHOP` |
| | จอง 31 ต.ค. 23:59 กลุ่ม 3 / 1 พ.ย. 00:00 | ฿3,000 none / ฿2,850 |
| | U07 Gold กลุ่ม 3 จอง 1 พ.ย. | ฿2,850 · `discountKind` = group |
| | แพ็กเกจ 4 คน · กลุ่ม 6 + H04 12 กม. | ฿11,600 none · ฿6,000 − 15% + รถ 2 × ฿300 = ฿5,700 |
| | B04 หลังเลื่อนนาฬิกา 1 พ.ย. · ใบสรุปข้ามเที่ยงคืน | ฿4,500 · 409 `PRICE_CHANGED` total ฿2,850 |
| | check-rules เดิม | E26 ฿3,000 · E28 ฿4,500 · E79 ฿6,000 (ไม่ต้องแก้) |
| CR-03 | ไม่ล็อกอิน `081-000-0003` / `0810000003` / `(081) 000 0003` ทับ B03 | 409 `DUPLICATE_BOOKING` existing B03 |
| | ต่อกันพอดี 11:30 · คนละเบอร์ · แขกใช้เบอร์ตรงบัญชีสมาชิก · ยกเลิกแล้วจองใหม่ | 201 |
| | พร้อมกัน 2 คำขอ (ไม่ล็อกอิน / สมาชิก U01) | `[201, 409 DUPLICATE_BOOKING]` · ฐาน 1 นัด |
| | คนละคนแย่ง T04 (U03 + U04) · TC-BOOK-06 | 201 + 409 `SLOT_TAKEN` (เดิม) |
| | U02 คู่ทับ B02 ห้องเต็ม / U02 เดี่ยวทับ B02 | 409 `SLOT_TAKEN` / 409 `DUPLICATE_BOOKING` B02 |
| | en / zh | "You already have a booking at this time (code B03)" / "您在该时段已有预约（预约号 B03）" |
| CR-04 | `GET /api/holidays` | 200 · 3 แถวเรียงวันที่ · ชื่อ 3 ภาษา |
| | slots S01 23 ต.ค. / 22 และ 24 ต.ค. | 422 `SHOP_CLOSED` "วันนี้ร้านหยุด (วันปิยมหาราช) กรุณาเลือกวันอื่น" / 200 · 23 รอบ |
| | price/bookings 23 ต.ค. ทุกแบบ (เดี่ยว คู่ กลุ่ม แพ็กเกจ คอร์ส) | 422 `SHOP_CLOSED` |
| | 5 ธ.ค. ตอนวันนี้ 10 ต.ค. / ตอนวันนี้ 10 พ.ย. | `DATE_OUT_OF_RANGE` / `SHOP_CLOSED` (วันพ่อแห่งชาติ) |
| CR-01 | B05 (นิดา 11 ต.ค. 10:00) → 12 ต.ค. 10:00 ตอน 10:00 / ตอน 10:01 | 200 · ฿760 · รหัส B05 เดิม · T04 / 422 `RESCHEDULE_TOO_LATE` |
| | B06 (วันนี้) · เวลาเดิม · 9 พ.ย. / 10 พ.ย. · 21:00 / 21:30 | `RESCHEDULE_TOO_LATE` · `RESCHEDULE_SAME` · 200 / `DATE_OUT_OF_RANGE` · 200 / `SLOT_INVALID` |
| | B01 → 14 ต.ค. 16:00 · `reschedule-slots` B01 14 ต.ค. | 409 `SLOT_TAKEN` (T03 ติด B04) · 16:00 `available:false` ขณะ `/api/slots` 16:00 true (T06) |
| | B02 คู่ 19:00 → 19:30 | 200 · T01 + T02 |
| | คนอื่น / ไม่ล็อกอิน / owner · B07 completed / B11 cancelled | 403 / 401 / 403 · 422 `RESCHEDULE_NOT_ALLOWED` |
| | เดือนเกิด 31 ต.ค. → 1 พ.ย. / 30 ต.ค. · คอร์ส C02 19 → 21 / 20 ต.ค. | 422 `RESCHEDULE_BIRTHDAY` / 200 · 422 `COURSE_UNAVAILABLE` reserved 1 / 200 reserved 1 |
| | ทับนัดอื่นของตัวเอง · 23 ต.ค. | 409 `DUPLICATE_BOOKING` · 422 `SHOP_CLOSED` |
| CR-05 | 1–30 ก.ย. | ยืนยัน/เสร็จ/ยกเลิก 0/3/1 · ยอดขาย 1,900 (บัตร 0 · อื่น 1,900 · ค่ารถ 0) · ส่วนลด กลุ่ม/ระดับ/เดือนเกิด 0/100/0 · แต้ม 19 · ครั้งคอร์ส 2 · ยอดนัดยืนยัน 0 · T01 T03 T05 = 1 · CSV 4 แถว (B10 B11 B12 B13) |
| | 1–31 ต.ค. | 6/1/0 · ยอดขาย 1,440 · เดือนเกิด 360 · แต้ม 14 · คอร์ส 0 · ยอดนัดยืนยัน 11,130 · T05 = 1 |
| | 6–9 ต.ค. · 1 ส.ค.–31 ต.ค. · 1 ส.ค.–1 พ.ย. | ทุกค่า 0 (CSV หัวอย่างเดียว) · 92 วัน 200 (3,340 · แต้ม 33 · คอร์ส 4) · 93 วัน 422 `REPORT_RANGE` |
| | CSV | `EF BB BF` · `text/csv; charset=utf-8` · แถว `2026-09-30,B13,completed,single,1,นวดน้ำมันอโรมา,1900.00,0.00,1900.00,tier,100.00,19` |
| | สิทธิ์ | ไม่ล็อกอิน 401 · U01 403 (JSON + CSV) · U01 ไม่เห็นเมนูรายงาน |
| | ตั้งนาฬิกา 12 ต.ค. 14:00 → owner กดเสร็จ B01 → ต.ค. | ยอดขาย 2,440 · ยอดนัดยืนยัน 10,130 · เสร็จ 2 |

> รูปแบบ CSV (เงิน `1900.00` · ชื่อบริการไทย · ทุกสถานะ · CRLF) และชื่อ error `REPORT_RANGE` เป็นการตัดสินแทนร้านของรอบจริง · ผู้เรียนเลือกต่างได้ถ้ามีในคำถาม/impact และ ③ ของร้านยังผ่าน
