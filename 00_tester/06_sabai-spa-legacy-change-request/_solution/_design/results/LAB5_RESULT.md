# LAB 5 RESULT · ตาข่ายกันพลาด (บท 06 สบายใจ สปา)

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 10:20:25 |
| เวลาจบ (งานตามพรอมต์ ส่วน 1–3 + commit) | 10:38:21 · เขียน result เสร็จ ~10:45 |
| เวลาที่ใช้ | ~18 นาที: ส่วน 1 ≈ 7 นาที (rebuild seam 51 วิ · up ปิด/เปิด seam 2 ครั้ง · golden --update + เทียบ 2 รอบ ≈ 10 วิ/รอบ) · ส่วน 2 ≈ 6 นาที (npm install 4 วิ · e2e-cr 3 เบราว์เซอร์ 68 วิ + 64 วิ) · ส่วน 3 ≈ 5 นาที (rebuild ต่อ mutant 41/38/43 วิ + golden + check-rules ~20 วิ + e2e-cr chromium ~19 วิ · rebuild คืนโค้ด 42 วิ) |
| ไฟล์ที่สร้าง/แก้ใน w/ | แก้ `web/lib/server/testmode.ts` (+12 บรรทัด `setTestClock()`) · สร้าง `web/app/api/test/clock/route.ts` (14) · `tests/golden/run.mjs` (189) `price.json` `slots.json` `admin-queue.json` `README.md` (77) · `e2e-cr/` (package.json · package-lock.json · playwright.config.ts · global-setup.ts · tsconfig.json · tests/fixtures.ts · tests/char-booking.spec.ts · tests/known-issues.spec.ts) · `KNOWN-ISSUES.md` · **ไม่แก้** `web/lib/rules/` (ยกเว้น mutant ชั่วคราวในส่วน 3 ที่คืนแล้ว) · `web/lib/server/booking.ts` · `e2e-legacy/` |
| git | commit `3bcd8c9` `safety-net: seam + golden + characterization` · **16 ไฟล์ +8,681 บรรทัด** · `git status --short` หลัง commit = ว่าง (0 บรรทัด) · ต้องใช้ `git add -f tests/golden/README.md` (ดูข้อ 9) |
| สคริปต์ชั่วคราว / log | `tools/lab5/`: `mutant.ps1` (1 รอบ mutant) · `seam-proof.txt` · `build-seam.log` `up-off.log` `up-on.log` `rebuild-final.log` · `price-summary.txt` (สรุปทุกเคสราคา) · `char-probe*.log` · `e2e-cr-run1.log` `e2e-cr-run2.log` `e2e-cr-summary.txt` · `X{1,2,3}-{build,golden,rules,e2e}.log` (log ของ PowerShell `*>` เป็น UTF-16) |
| ภาพ | RUNNER §6: LAB 5 ไม่มีภาพ ("ใช้ตารางผล") → ไม่ได้ถ่าย |
| สถานะเว็บตอนจบ | `sabai06-web` (rebuild ด้วยโค้ดปกติ + seam) + `sabai06-db` เปิดค้าง healthy · `GET http://localhost:4100/api/health` → `{"ok":true,"db":true}` · `ALLOW_TEST_RESET=1` |
| ข้อมูลทดสอบ | reset หลายครั้ง (golden 3 ครั้ง/รอบ × 4 รอบ + mutant 3 รอบ + ทุก test ของ e2e-cr) · **ท้าย LAB reset อีกครั้ง** → `{"ok":true,"now":"2026-10-10T10:00:00+07:00"}` (DB = seed) |
| พอร์ตที่ใช้จริง | เว็บ **4100** · db **5533** (`$env:WEB_PORT` `$env:DB_PORT` ก่อนทุก `up` · `$env:BASE_URL="http://localhost:4100"` ก่อน golden และ e2e-cr) · ไฟล์ใน w/ ใช้ค่าเริ่ม 4000 ตามพรอมต์ (ไม่ต้องแปลงตอนเขียน README) |
| เซสชัน / โหมดสิทธิ์ | runner (Agent tool) แทนเซสชันผู้เรียน โหมด A · 3 กล่องพรอมต์ทำต่อกันในเซสชันเดียว · ไม่ได้เรียก `yolo.cmd` (LAB นี้ไม่มีขั้นที่ต้องพิสูจน์ในเซสชันใหม่) |

## 2. ข้อห้ามที่ทำตาม และจุดที่ทำต่างจากพรอมต์

- รั้วจาก `w/CLAUDE.md` และ `w/.claude/settings.json` (`deny Edit(e2e-legacy/**)`) **self-enforce** โดย runner: ไม่แตะ `e2e-legacy/**` (แค่อ่าน config/fixtures เป็นแนวทาง) · ไม่ `down -v` · ไม่เปิด `_solution/` และ `CHANGE-REQUESTS/answers/` · โค้ดใหม่ไม่ใช้ `new Date()` (seam ใช้ `parseClockValue` + `bangkokIso` เดิม)
- ส่วน 1: ไม่แก้ `web/lib/rules/` และ `web/lib/server/booking.ts` · seam แตะแค่ `app_setting.test_today` (UPDATE แถวเดียวใน transaction) ไม่แตะตารางอื่น · ใช้เงื่อนไขเปิด/ปิดเดียวกับ reset (`config.allowTestReset` → 404)
- ส่วน 2: ไม่แก้โค้ดใน `web/` · ไม่แก้บั๊กที่เจอ
- ส่วน 3: แก้ rules ทีละตัว (ตามที่พรอมต์สั่ง) แล้วคืนด้วย `git checkout -- <ไฟล์>` ทุกตัว · ยืนยัน `git status --short <ไฟล์>` ว่าง และ `git diff -- web/lib/rules/` = 0 บรรทัด หลังคืนครบ
- git: ใช้ git จริงตาม D11 เพราะพรอมต์สั่ง `git checkout --` / `git add` / `git commit` เอง (ไม่ใช้ snapshot ของ RUNNER §4)
- CLAUDE.md กติกาข้อ 1 ("ทำ impact แล้วรออนุมัติก่อนแก้"): ถือว่าพรอมต์ส่วน 1 ที่สั่งเพิ่ม seam ชัดเจน = การอนุมัติของผู้เรียน จึงไม่หยุดถาม (บันทึกในข้อ 6)
- "รันคำสั่งด้วย PowerShell": docker compose · golden · check-rules · Playwright · git checkout ใช้เครื่องมือ PowerShell · การอ่าน/grep/สร้างไฟล์ใช้ Git Bash + Write (ไม่เปลี่ยนสถานะ repo)
- ⚠️ ความบริสุทธิ์ของการเทียบผล: ตอนเปิด LAB 5 runner อ่าน PROMPTS.md บรรทัด 180–241 ทีเดียว จึง**เห็นบรรทัด "ผลที่คาด" ก่อนลงมือ**โดยไม่ตั้งใจ (เหมือน LAB 4) · ตัวเลขทุกตัวนับจาก log/ไฟล์จริง ไม่ได้ปรับตามผลที่คาด
- ไม่แตะ `pawpantry05` (4000) และ `exref-*` (4200/5633) · ไม่ใช้ Playwright MCP

## 3. คำตอบสรุปที่แสดงในแชท

**ส่วนที่ 1**

> | ส่วน | ไฟล์ | จำนวนเคส | ผล |
> |---|---|---|---|
> | A seam | `web/app/api/test/clock/route.ts` + `setTestClock()` ใน `web/lib/server/testmode.ts` | พิสูจน์ 3 ข้อ | reset → จอง S01 12 ต.ค. 16:00 ผ่าน API ได้ **B14** (201) → `today` 2026-10-10 → clock `2026-10-12T09:00+07:00` → `today` **2026-10-12** · คิวหลังร้าน 12 ต.ค. = **B01, B14** (นัดยังอยู่) · `now:"garbage"` → 422 · `ALLOW_TEST_RESET=0` → clock **404** (today 404) → ตั้งกลับ 1 → clock 200 |
> | B golden ราคา | `tests/golden/price.json` | 50 | `--update` แล้วเทียบ 2 รอบ ผ่าน 50/50 ทั้งคู่ · ทุกเคส HTTP 200 |
> | B golden ช่วงเวลา | `tests/golden/slots.json` | 6 | ผ่าน 6/6 × 2 รอบ |
> | B golden คิวหลังร้าน | `tests/golden/admin-queue.json` | 6 | ผ่าน 6/6 × 2 รอบ |
> | README | `tests/golden/README.md` | — | ป้าย [E] · ตาราง SHA-256 ย่อ `a485c485` / `b5eb12a8` / `255ee583` · ฟิลด์ที่ตัด (`id` `bookingId` `createdAt`… · ไม่เก็บ header/cookie) · ค่าที่ดูแปลก 8 แถว |

**ส่วนที่ 2**

> | test | chromium | firefox | webkit | รอบ 1 = รอบ 2 ไหม | known issue |
> |---|---|---|---|---|---|
> | CHAR-BOOK-01 จอง S01 12 ต.ค. 15:00 → หน้าสรุป ฿1,000 + aria `/children: equal` | ✅ | ✅ | ✅ | เท่ากัน | — ([E ev_8dc23d9f] ฿1,000 ตรง) |
> | KI-01a [ล็อก] บัตรปลอม: API 404/422 GC_NOT_FOUND แต่หน้าจองไม่เตือน | ✅ | ✅ | ✅ | เท่ากัน | KI-01 |
> | KI-01b [ควรเป็น] เตือน "ไม่พบ Gift Card นี้" (test.fail) | ✅ expected-fail | ✅ expected-fail | ✅ expected-fail | เท่ากัน | KI-01 |
> | KI-02a [ล็อก] เบอร์ "abc" → 201 + ขึ้นคิวหลังร้าน | ✅ | ✅ | ✅ | เท่ากัน | KI-02 |
> | KI-02b [ควรเป็น] เบอร์ "abc" → 422 (test.fail) | ✅ expected-fail | ✅ expected-fail | ✅ expected-fail | เท่ากัน | KI-02 |
> | KI-03a [ล็อก] owner ยกเลิก B05 → 200 cancelled (ต้องถามร้าน · ไม่มี test.fail) | ✅ | ✅ | ✅ | เท่ากัน | KI-03 |

**ส่วนที่ 3**

> | ตัวทำพัง | golden | check-rules | e2e-cr (chromium) | ถูกจับ / รอด |
> |---|---|---|---|---|
> | X1 `tier.ts` `>=` → `>` | ❌ 2/62 ต่าง (single-S01-U07, group3-S01-U07) | ❌ 88/90 (E46 E51) | ✅ 6/6 ไม่จับ | **ถูกจับ** |
> | X2 `transport.ts` ที่นั่ง 4 → 5 | ❌ 3/62 (package5-P01-guest-H05, group5-S01-guest-H04, group5-S01-U06-redeem1-H04-GCPART) | ❌ 88/90 (E78 E80) | ✅ 6/6 ไม่จับ | **ถูกจับ** |
> | X3 `pricing.ts` กลุ่ม 10 → 15 | ❌ 10/62 (ทุกเคสกลุ่ม ≥ 4) | ❌ 83/90 (E27 E28 E79 E84 E85 E87 E88) | ✅ 6/6 ไม่จับ | **ถูกจับ** |
>
> คืนไฟล์ครบ 3 ตัว (git diff ว่าง) → rebuild โค้ดปกติ → golden **62/62** · check-rules **90/90** · ไม่มีตัวรอด แต่เขียนจุดที่ตาข่ายบางพร้อมเคสเสนอไว้ใน `tests/golden/README.md` · commit `3bcd8c9`

## 4. ตัวเลขสำคัญ (นับจากผลจริง)

| ตัวเลข | ค่า | คำสั่ง/แหล่ง |
|---|---|---|
| golden เคสรวม | **62** (price 50 · slots 6 · admin-queue 6) | `node tests/golden/run.mjs --update` → `updated price.json: 50 cases` ฯลฯ |
| golden เทียบหลัง update | รอบ 1 `GOLDEN PASS: 62/62` exit 0 · รอบ 2 `GOLDEN PASS: 62/62` exit 0 | `node tests/golden/run.mjs` ×2 |
| สถานะ HTTP ใน golden | 62/62 = 200 | node นับ `cases[].status` |
| SHA-256 ย่อ / ขนาด | price.json `a485c485` 111,837 B · slots.json `b5eb12a8` 101,001 B · admin-queue.json `255ee583` 4,654 B | `Get-FileHash -Algorithm SHA256` |
| เวลา `--update` | 2026-10-12 10:24:30 | |
| ยอด char-booking | `summary-amount-total` data-amount = **1000** = [E ev_8dc23d9f] ฿1,000 (ตรง · ไม่ต้องหยุดถาม) | spec + `rea-out/scenario.json` |
| e2e-cr รอบ 1 / รอบ 2 | Playwright รายงาน `18 passed (1.1m)` / `18 passed (1.0m)` · แยกจริง: **passed 12 · expected-fail 6 (KI-01b KI-02b × 3 เบราว์เซอร์) · failed 0 · flaky 0** ทั้ง 2 รอบ · ลำดับผลรายเทสต์เท่ากัน (diff ว่าง) | `npx playwright test --reporter=list` (expected-fail แสดงเป็น `x` แต่นับรวมใน passed) |
| e2e-cr ต่อเบราว์เซอร์ | chromium / firefox / webkit = ผ่าน 4 + expected-fail 2 เท่ากันทุกตัว | log `tools/lab5/e2e-cr-run{1,2}.log` |
| seam | clock 200 → today เปลี่ยน 2026-10-10 → 2026-10-12 · ปิด (`ALLOW_TEST_RESET=0`) clock **404** today **404** · ค่าไม่ถูกต้อง 422 | `tools/lab5/seam-proof.txt` |
| mutant จับได้ | golden 3/3 · check-rules 3/3 · e2e-cr 0/3 · รอด 0 | `tools/lab5/X*-*.log` |
| เวลา rebuild | seam 51 วิ · X1 41 · X2 38 · X3 43 · คืนโค้ด 42 วิ | `mutant.ps1` |
| check-rules หลังคืนโค้ด | `ผ่าน 90 / 90 ข้อ` | |
| commit | `3bcd8c9` · 16 ไฟล์ +8,681 | `git show --stat` |

## 5. ตัวอย่างแถวเด่นสำหรับ README

| รหัส | แถว |
|---|---|
| golden `single-S01-U07` | U07 ยอดสะสม ฿10,000 พอดี → Gold 5% ยอด ฿950 [E golden/price.json:a485c485] — เคสเดียวที่ทำให้ X1 (`>=`→`>`) ถูก golden จับ |
| golden `group5-S01-guest-H04` | กลุ่ม 5 คน H04 12 กม. → รถ 2 คัน ฿600 ยอด ฿5,100 — จับ X2 |
| `CHAR-BOOK-01` | หน้าสรุป S01 12 ต.ค. 15:00–16:00 ฿1,000 ตรง [E ev_8dc23d9f] + aria `/children: equal` (3 แถวในตารางราคา) |
| KI-01 | `GET /api/giftcards/SABAI-GC-FAKE` → 404 `GC_NOT_FOUND` · `/api/price` → 422 · หน้าจองล้างข้อความใน ~250 ms (`BookingWizard.tsx:188` `setGcCode("")` → `:182` `setQuoteErr(null)`) → ไม่เตือน |
| KI-02 | เบอร์ `abc` → 201 confirmed · คิวหลังร้านแสดง `ทดสอบเบอร์ (abc)` |
| X3 | กลุ่ม 10 → 15: golden 10/62 ต่าง · check-rules 83/90 · e2e-cr ไม่จับ (ตาข่ายหน้าจอบาง) |

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบที่เลือก | เหตุผล |
|---|---|---|
| CLAUDE.md ข้อ 1 ให้รออนุมัติ impact ก่อนแก้ — ต้องหยุดก่อนเพิ่ม seam ไหม | ไม่หยุด · ถือพรอมต์เป็นการอนุมัติ | พรอมต์ระบุไฟล์/พฤติกรรม/วิธีพิสูจน์ครบ และไม่ใช่ CR ที่เปลี่ยนกฎ · seam แตะแค่โหมดทดสอบ |
| เลือกชุดเคสราคา "ราว 40–60" | 50 เคส (ผู้ใช้ 9 × เดี่ยว · คู่ 3 · กลุ่ม 7 · แพ็กเกจ 5 · คอร์ส 2 · แต้ม 5 · Gift Card 6 · รถ 7 · วันเกิด/ผสม 5 → ตรวจแล้วทุกเคสได้ 200) | ให้ครอบทุกผู้ใช้ seed + ขอบที่กฎน่าจะเปลี่ยน (กลุ่ม 4/5/6 · รถ 5 คน · ยอด 10,000) |
| ตัดฟิลด์ไหน | `id` `bookingId` `createdAt/created_at/updatedAt/updated_at` · ไม่เก็บ header/cookie · คง `today` และ `code` | id เป็น serial · ใช้ code แทน · today ถูก reset ล็อกไว้ |
| ชื่อผู้ติดต่อในเคสจอง (seam proof) | `Seam Test` (ภาษาอังกฤษ) | ยิงด้วย Invoke-RestMethod ใน PS 5.1 → หลีกเลี่ยงข้อความไทยตาม CLAUDE.md ข้อ 6 |
| owner ยกเลิกนัดลูกค้า = บั๊กไหม | **ไม่แน่ใจ → "ต้องถามร้าน"** · เขียนแค่เทสต์ล็อก ไม่มีคู่ test.fail | โค้ด `booking.ts:465` ตั้งใจให้ owner ทำได้ · ตรงกับ SPEC-GAPS G13 ที่ยังรอคำตอบร้าน |
| บัตรปลอม / เบอร์ abc = บั๊กไหม | ใช่ · เขียนคู่ ① ล็อก ② test.fail | บัตรหมดอายุ/ยอด 0 หน้าจอเตือน แต่บัตรไม่มีอยู่ไม่เตือน (ไม่สอดคล้อง) · เบอร์ abc ติดต่อไม่ได้ (ถามร้านรูปแบบเบอร์) |
| เทสต์ ② ของ KI-02 คาดสถานะอะไร | 422 | ตรงกับรูปแบบ error validation อื่น (`CONTACT_REQUIRED` 422) · ยังไม่มีรหัส error จริง |
| `tests/golden/README.md` ถูก `.git/info/exclude` กันไว้ | `git add -f tests/golden/README.md` | พรอมต์ต้องการให้ README อยู่ใน commit · ไม่แก้ exclude ของ repo |
| ภาพ LAB 5 | ไม่ถ่าย | RUNNER §6 กำหนด "—" |

## 7. ข้อสังเกต 👀

- **`.git/info/exclude` บรรทัด `README.md` ไม่มี `/` นำหน้า** → กัน README ทุกระดับ · `git add tests` เงียบ ๆ ไม่ใส่ `tests/golden/README.md` (เอกสารป้าย [E] + ตาราง SHA ที่พรอมต์บังคับ) · ผู้เรียนที่ไม่ดู `git status` จะ commit ไม่ครบโดยไม่รู้ตัว
- **e2e-cr จับ mutant ไม่ได้เลย (0/3)** ทั้งที่ "ล็อกหน้าจองแล้ว" → char-booking ล็อกแค่ลูกค้าไม่ล็อกอินจองเดี่ยว ไม่มีส่วนลด/รถ · เป็นจุดสอนที่ดี: snapshot หน้าจอ ≠ ตาข่ายของกฎ
- X1 รอดได้ง่ายมาก: golden จับเพราะบังเอิญมี U07 ยอด ฿10,000 พอดีใน seed เท่านั้น (2 เคส) · ถ้าเลือกเคสราคาเฉพาะไม่ล็อกอิน X1 จะรอดจาก golden
- KI-01 เป็นบั๊กแบบ "ข้อความวูบ": หน้าจอแสดง error ~250 ms แล้วล้างเอง (`setGcCode("")` ยิงราคาใหม่สำเร็จ → `setQuoteErr(null)`) · เทสต์ ② ต้องรอ response 422 แล้วรอ 200 รอบถัดไปก่อน assert ไม่งั้น `toBeVisible` อาจจับข้อความวูบได้แล้ว test.fail กลายเป็น "ผ่านโดยไม่คาด"
- `toMatchAriaSnapshot` ที่ Playwright สร้างให้ (`--update-snapshots --update-source-method=overwrite`) แปลงตัวเลขเป็น regex (`/฿\d+,\d+/`) → ยอดเงินไม่ถูกล็อกจริง · ต้องเขียน template เองเป็นข้อความตรง (`row "ยอดสุทธิ ฿1,000"`) + `/children: equal`
- Playwright list reporter: expected-fail แสดง `x` แต่บรรทัดสรุปเขียน `18 passed` (นับรวม) → ต้องแยกเองตาม RUNNER
- PowerShell 5.1 `*>` เขียน log เป็น UTF-16 LE → `grep` ใน Git Bash หาไม่เจอ (ต้องอ่านด้วย `Get-Content`)
- `git` เตือน `LF will be replaced by CRLF` (autocrlf เปิด) → ถ้า clone ใหม่บน Windows ไฟล์ golden จะเป็น CRLF และ **SHA-256 ใน README จะไม่ตรง** (run.mjs ยังผ่านเพราะ parse JSON) · ควรมี `.gitattributes` `tests/golden/*.json -text` หรือระบุว่า SHA คำนวณตอน `--update`
- REA บันทึก B14 จาก scenario ของ LAB 2 · seam proof ของ LAB นี้ก็ได้ B14 (เลขซ้ำเพราะ reset RESTART IDENTITY) → ใน README ระวังสับสน

## 8. เจอระหว่างทาง (นอก CR)

- Gift Card หมดอายุ "วันนี้" (`SABAI-GC-LAST` expires 2026-10-10 = วันที่ล็อก) ยังใช้ได้ `status ok` (นับรวมวันหมดอายุ) [E golden/price.json:a485c485 `single-S01-U02-GCLAST`] — ถามร้าน
- แต้มที่จะได้ไม่นับส่วนที่จ่ายด้วย Gift Card ทั้งก้อน (U06 + GCPART ได้ 0 แต้ม) — ตรงกับ SPEC-GAPS G5 ที่มีอยู่แล้ว
- กลุ่ม 4 คนของ Platinum (U06) ได้ส่วนลด 10% แบบ `discountKind: group` (เสมอกับ tier แล้วเลือก group ตามลำดับ) — ผลเงินเท่ากัน แต่ป้ายบรรทัดส่วนลดต่าง
- Gift Card หมดอายุ/ยอด 0 → `/api/price` 200 + `giftCardError` · บัตรไม่มีอยู่ → 422 (รูปแบบ error ไม่สม่ำเสมอ · ต้นเหตุ KI-01)
- `/api/bookings` ต้องมี `quotedTotal` (ไม่ส่ง → 422 `QUOTE_REQUIRED`) — SYSTEM-MAP มีแล้ว แต่ทำให้ยิง API ครั้งแรกล้ม
- แพ็กเกจ 6 คน แสดง "ค่ารถรับส่ง 2 คัน · รวมในแพ็กเกจแล้ว" (ค่ารถ 0) — ตรงกฎ

## 9. ปัญหาที่เจอ / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| ยิง `POST /api/bookings` ครั้งแรก 422 | ดู body = `QUOTE_REQUIRED` → ใส่ `quotedTotal: 1000` |
| heredoc ใน Git Bash ที่มี backtick/`${}` ของ JS พัง (2 ครั้ง) | เขียนไฟล์ด้วยเครื่องมือ Write/Edit แทน |
| aria snapshot ที่สร้างอัตโนมัติเป็น regex | เขียน template เองด้วยข้อความตรง + `/children: equal` แล้วรันผ่าน |
| `tests/golden/README.md` ไม่อยู่ใน `git status` | `git check-ignore -v` → `.git/info/exclude:9 README.md` → `git add -f` |
| log PS5.1 เป็น UTF-16 | อ่านผ่าน `Get-Content` / `Select-String` |
| ไม่มี rebuild ล้ม · คืนไฟล์ได้ทุกตัว | — |

## 10. ข้อเสนอแก้พรอมต์

1. **(H) exclude ไม่ anchor** — ในพรอมต์ที่สร้าง `.git/info/exclude` (LAB ก่อนหน้า) ให้เขียน `/README.md` `/EXAM.md` (มีเครื่องหมาย `/`) หรือใน LAB 5 ส่วนที่ 3 เติม "ตรวจ `git status` ว่ามี `tests/golden/README.md` ก่อน commit" · ไม่งั้น README ของ golden หายจาก commit
2. (M) ส่วนที่ 2 ข้อ 2: เติม "เขียน aria snapshot เป็นข้อความตรง ไม่ใช้ regex ที่ Playwright สร้างให้" — ไม่งั้นยอดเงินในโครงหน้าสรุปไม่ถูกล็อก
3. (M) ส่วนที่ 2 ข้อ 3: owner ยกเลิก — พรอมต์ไม่ได้บอกว่าข้อนี้อาจเป็น "ตั้งใจ" · เพิ่ม "เทียบกับ docs/SPEC-GAPS.md ก่อนตัดสินว่าบั๊ก" ช่วยให้ผลตรงกันระหว่างผู้เรียน
4. (M) ส่วนที่ 1: ระบุว่า "40–60 เคส" นับเฉพาะ `/api/price` (รวมทั้งหมดได้ 62 ซึ่งเกิน 60 ถ้าอ่านว่านับรวม)
5. (L) ส่วนที่ 3: ผลเฉลี่ย rebuild ~40 วิ/ตัว (ไม่ถึง 2 นาที) · ทั้ง LAB ส่วน 3 ≈ 5 นาที
6. (L) README golden: แนะนำ `.gitattributes` (`tests/golden/*.json -text`) เพื่อให้ SHA ย่อคงที่หลัง clone บน Windows
7. (L) ส่วนที่ 2 ข้อ 4: เตือนว่าบรรทัดสรุป Playwright นับ `test.fail` รวมใน passed (ผู้เรียนจะเห็น "18 passed" แล้วงงว่า test.fail อยู่ไหน)

## 11. ภาพที่ควรใช้ + เทียบกับผลที่คาด

ภาพ: ไม่มี (RUNNER §6 LAB 5 = "ใช้ตารางผล") · ถ้า README ต้องการภาพ แนะนำทำ png จากตารางข้อ 3 ส่วนที่ 3 (mutant × ชุดทดสอบ)

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| route ใหม่ `web/app/api/test/clock/route.ts` (+ ฟังก์ชันใน `lib/server/testmode.ts`) | ตรงตัว (`setTestClock()`) | ✅ |
| clock 404 เมื่อปิด | `ALLOW_TEST_RESET=0` → 404 (today ก็ 404) → เปิดกลับ 200 | ✅ |
| golden 40–60 เคส นิ่ง 2/2 รอบ | ราคา 50 (+ slots 6 + คิว 6 = 62) · ผ่าน 62/62 ทั้ง 2 รอบ | ✅ (ถ้านับรวมเป็น 62 > 60 · ดูข้อเสนอ 4) |
| `tests/golden/README.md` มีตาราง SHA-256 ย่อ + ป้าย [E] | มีครบ + ฟิลด์ที่ตัด + ค่าแปลก 8 แถว + ผล mutant | ✅ (แต่ต้อง `git add -f`) |
| char-booking ยอดตรง [E] ของ scenario (฿1,000) | data-amount 1000 = [E ev_8dc23d9f] | ✅ |
| `e2e-cr/` · ยอด ฿1,000 (ราคา S01 [seed]) | ✅ 3 เบราว์เซอร์ × 2 รอบ | ✅ |
| known issue: บัตรปลอม API 422 `GC_NOT_FOUND` แต่หน้าจอไม่เตือน | `/api/price` 422 GC_NOT_FOUND (+ `GET /api/giftcards/:code` 404) · หน้าจอไม่เตือน (วูบ ~250 ms) | ✅ |
| เบอร์ "abc" → 201 | 201 confirmed | ✅ |
| owner ยกเลิก → 200 | 200 cancelled | ✅ |
| X2 X3 ถูกจับโดย golden ราคา/รถ | X2 golden 3 เคส · X3 golden 10 เคส (+ check-rules ทั้งคู่) | ✅ |
| X1 อาจรอดถ้าไม่มีเคสยอดสะสม ฿10,000 พอดี — ใช้ผลจริง | **ถูกจับ** โดย golden (U07 ฿10,000 พอดี 2 เคส) และ check-rules (E46 E51) | ✅ (ผลจริง = ถูกจับ) |
| commit 1 ตัว | `3bcd8c9` 1 ตัว | ✅ |
| ไปต่อได้: golden ผ่าน 2 รอบติด · e2e-cr เท่ากัน 2 รอบ × 3 เบราว์เซอร์ · git status สะอาดหลังคืน mutant · KNOWN-ISSUES 3 เรื่อง | ครบทุกข้อ | ✅ |
