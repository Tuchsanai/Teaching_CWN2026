# LAB 10 RESULT · CR-05 รายงานยอด + CSV (2 ส่วน)

> รอบจริงรันที่ 4100/5533 · ผู้เรียนใช้ 4000/5433

## 1. ตารางหัว

| รายการ | ค่า |
|---|---|
| เวลาเริ่ม | 2026-10-12 12:21 (นาฬิกาเครื่อง) |
| เวลาจบ | 2026-10-12 ~12:40 |
| เวลาที่ใช้ | **~19 นาที** · ส่วน 1 (อ่าน CLAUDE.md/SYSTEM-MAP/CR-05 + คำถาม Q1–Q12 + เปิดคำตอบ + อ่านโค้ดหลังร้าน + reset + SQL 3 ช่วง+ขอบ + impact) ≈ 7 นาที · ส่วน 2 ≈ 12 นาที (เขียน `tests/cr05.mjs` 12 เคส · แดง **3.1 วิ** · โค้ด · rebuild **39 วิ** · เขียว 12/12 **3.1 วิ** (ผ่านรอบแรก) · cr05.spec 3 เบราว์เซอร์ **15 วิ** · ตรวจไขว้คิวหลังร้าน ~5 วิ · regression: check-rules **19.5** · golden 1.3 · cr01 5.5 · cr02 4.4 · cr03 4.0 · cr04 3.0 · cr05 3.2 · e2e-cr chromium **33 วิ** · e2e-legacy api+chromium **245 วิ (4.1 นาที)** · ภาพ ~10 วิ · เอกสาร + commit ≈ 3 นาที) |
| ไฟล์ที่สร้าง/แก้ใน w/ | สร้าง `docs/impact/CR-05.md` · `tests/cr05.mjs` (12 เคส R1–R12) · `e2e-cr/tests/cr05.spec.ts` (2 เทสต์) · `web/app/api/admin/report/route.ts` · `web/app/admin/report/page.tsx` · `web/components/AdminReport.tsx` · แก้ `web/lib/server/admin.ts` (+113/−3) · `web/lib/i18n.ts` (+27) · `web/app/layout.tsx` (+6/−1) · `web/SPEC.md` (1.5) · `docs/TRACEABILITY.md` (+4 แถว CR-05) · `CHANGE-REPORT.md` (+ส่วน CR-05) · `CHANGE-REQUESTS/REGISTER.md` (แถว CR-05) · รวม `git diff --stat f4edf7b HEAD` = **13 ไฟล์ +944/−7** · ไม่แตะ `db/` `web/lib/bot/chat.ts` `check-rules.mjs` `tests/golden/` `e2e-legacy/` (`git diff --stat f4edf7b HEAD -- web/scripts/check-rules.mjs tests/golden e2e-legacy db` = 0 บรรทัด) |
| git (w/) | 2 commit: `15fb782` "CR-05 test: แดงก่อนแก้" (impact + cr05.mjs) → `ef47d72` "CR-05: รายงานยอด + CSV" (12 ไฟล์) · `git status --short` = 0 บรรทัด · มี `Co-Authored-By` |
| สคริปต์ชั่วคราว / log | `tools/lab10/`: `questions.md` `explore.sql` `expected.sql` `expected-out.txt` (ผล psql) `cr05-red.log` `cr05-green.log` `cr05-spec.log` `crosscheck.mjs/.log` (รายงาน vs ตารางคิว) `regress.ps1` `regress-summary.txt` `count.mjs` `check-rules.log` `golden.log` `cr01..05.log` `e2e-cr.log/.json` `e2e-legacy.log/.json` `build-1.log` `shot.mjs` · `design/logs/lab10-red.txt` `lab10-green.txt` (UTF-8) |
| สถานะเว็บตอนจบ | `sabai06-web` image `sabai06-web:latest` `27c39a2eb077` (โค้ด `ef47d72`) · `/api/health` → `{"ok":true,"db":true}` · เปิดค้างไว้ |
| ข้อมูลทดสอบ | ทุกชุด reset ท้ายรอบ · reset ซ้ำตอนจบ → `now` = `2026-10-10T10:00:00+07:00` |
| พอร์ตที่ใช้จริง | เว็บ **4100** · db **5533** (`$env:WEB_PORT/DB_PORT` ก่อน `up --build` · `$env:BASE_URL="http://localhost:4100"` ก่อนทุกชุดทดสอบ) · ไฟล์ใน w/ ใช้ค่าเริ่ม 4000 (README แปลงเป็น 4000) |
| คำสั่งเปิดเซสชันและโหมดสิทธิ์ | runner (Agent tool) ทำเองในเซสชันเดียว ไม่ได้เปิด `claude -p` · ส่วน 1 แบบ plan (ไม่แตะโค้ด · เสนอแผน/impact แล้ว "ออกจาก plan mode" จึงบันทึก `docs/impact/CR-05.md` เพราะ Plan mode เขียนไฟล์ไม่ได้) · ส่วน 2 เทียบเท่า `acceptEdits` · กติกา `w/CLAUDE.md` + deny `Edit(e2e-legacy/**)` **บังคับเอง** |

## 2. ข้อห้ามที่ทำตาม / จุดที่ทำต่างจากพรอมต์

- ไม่เปิด `_solution/` README fast_track · เปิด `CHANGE-REQUESTS/answers/CR-05-ANSWERS.md` **หลัง**เขียนคำถาม Q1–Q12 (`tools/lab10/questions.md`)
- ไม่แก้ `e2e-legacy/` `check-rules.mjs` `tests/golden/` · ไม่มีรายการใหม่ใน `docs/ORACLE-CHANGES.md` · ไม่มี `docker compose down -v` · ไม่แตะ pawpantry05 / exref-* / sabai-* บท 04
- **ส่วน 1 ข้อ 2:** พรอมต์ให้รัน `docker exec sabai06-db psql -U sabai -d sabai -c "<SQL>"` แต่ `w/CLAUDE.md` ข้อ 5 (+ คำสั่ง orchestrator) ให้ใช้ `docker cp` + `psql -v ON_ERROR_STOP=1 -f` → ใช้แบบไฟล์ (`expected.sql` · exit 0 · ตรวจ `$LASTEXITCODE`) · SQL อยู่ใน `tools/lab10/` และคัดลงใน impact §3
- **ค่าคาดหวังมาจาก SQL ก่อนเขียนโค้ด:** `tests/cr05.mjs` ใช้ตัวเลขจาก `expected-out.txt` ทั้งหมด ไม่เคยเปิดหน้ารายงานก่อนเทสต์เขียว · ตัวเลขในข้อ R10 (1440+1000 · 11130−1000) คิดจาก SQL + `total_amount` ของ B01 จาก SQL
- **ส่วน 2 ข้อ 4 (test seam):** R10 reset ด้วย `now = 2026-10-12T14:00:00+07:00` (เวลานัด B01) ก่อน owner กดเสร็จ B01
- **ส่วน 2 ข้อ 5:** e2e-cr `--project=chromium` และ e2e-legacy ค่าเริ่ม (api+chromium) รันด้วย `--reporter=list,json` + `PLAYWRIGHT_JSON_OUTPUT_NAME` เพื่อแยก expected-fail
- e2e-cr/tests/cr05.spec.ts เขียน**หลัง**ทำหน้า (พรอมต์ข้อ 3 ไม่ได้สั่งแดงก่อน · ไม่มี log แดงของ UI)
- ไม่ได้อ่านเกินกล่อง ```text ของ LAB 10 (สกัดด้วย awk หยุดที่ fence ปิด) → §11 ตาบอดจริง (ต่างจาก LAB 8–9)
- ใช้ `git add -N` (intent-to-add) ก่อน `git diff --stat` ไฟล์ใหม่ 1 ครั้ง ระหว่างเตรียม commit ที่พรอมต์สั่ง

## 3. คำตอบสรุปที่แสดงในแชท

**ส่วนที่ 1 (วิเคราะห์ · Plan mode)**

> คำถาม Q1–Q12 → คำตอบร้านตอบตรง Q1 (วันนัดเวลาไทย · รวมหัวท้าย) Q3 (ส่วนลด 3 แบบ) Q6 (ยอดนัดยืนยัน) Q8 (92 วัน · from ≤ to) Q9 (หัว CSV 12 คอลัมน์ + BOM) Q12 (③ 2 ตัวอย่าง) · ตัดสินแทน Q2 Q4 Q5 Q7 Q9 (รูปแบบเงิน/ชื่อบริการ) Q10 Q11
>
> **ของเดิมที่ต่อยอด:** API `admin/bookings/route.ts:10-19` → `queueForDate()` `lib/server/admin.ts:8-40` (ตัดวันด้วย `toInstant(date,"00:00")` = เที่ยงคืนไทย `:20`) · สิทธิ์ owner: ไม่มี session 401 `route.ts:12-13` · `role !== "owner"` 403 `:14` · หน้า `app/admin/page.tsx:15-27` (`admin-forbidden`) · เมนู `app/layout.tsx:47` → `components/NavMenu.tsx:14-40` · ตารางคิว `components/AdminQueue.tsx:24-140` (fetch ต่อ string `:33` T13) · เงิน: DB `NUMERIC(10,2)` → pg สตริง → `toSatang()` `lib/db.ts:43` (สตางค์ integer) → JSON บาท `toSatang()/100` (`admin.ts:35`) / `toBaht()` `lib/money.ts:13` · แสดง `formatBaht()` `money.ts:3` · **ใช้ซ้ำ:** ตรวจสิทธิ์ · `toInstant/addDays/isDateString/diffDays/bangkokDate` · `toSatang/fromSatang/toBaht/formatBaht` · class ตาราง · **เขียนใหม่:** คิวรีรายงาน (รวมหลายวัน) · CSV (ยังไม่มีในระบบ: `grep "text/csv"` = 0) · หน้า/คอมโพเนนต์
>
> **โซนเวลา/เงิน:** ตัดช่วงด้วย `[from 00:00+07, to+1 00:00+07)` · seed ไม่มีนัดที่วัน UTC ≠ วันไทย (`q_tz` = 0) → เทสต์ seed จับบั๊กโซนเวลาได้ไม่หมด · รวมเงินเป็นสตางค์ ไม่บวก float

| ช่วงวัน | ตัวเลข | ค่าจาก SQL | SQL ที่ใช้ (ย่อ) |
|---|---|---|---|
| 1–30 ก.ย. | ยืนยัน / ใช้บริการแล้ว / ยกเลิก | 0 / 3 / 1 | `q_counts`: `count FILTER (status=…)` บน `(start_at AT TIME ZONE 'Asia/Bangkok')::date BETWEEN` |
| 1–30 ก.ย. | ยอดขาย · บัตรของขวัญ · ช่องทางอื่น · ค่ารถ | 1900 · 0 · 1900 · 0 | `q_money`: `sum(total_amount/giftcard_paid/other_paid/transport_fee)` WHERE completed |
| 1–30 ก.ย. | ส่วนลด กลุ่ม/ระดับ/เดือนเกิด | 0 / 100 / 0 | `q_money`: `sum(discount_amount) FILTER (discount_kind=…)` |
| 1–30 ก.ย. | แต้ม · ครั้งคอร์ส · ยอดนัดยืนยัน | 19 · 2 · 0 | `q_money` `sum(points_earned)` (ไขว้ `q_points_txn` 19) · `count FILTER (course_purchase_id NOT NULL)` (ไขว้ `q_course_txn` 2) · `q_pending` |
| 1–30 ก.ย. | คิวต่อนักบำบัด | T01 1 · T03 1 · T05 1 · อื่น 0 | `q_therapist`: therapist LEFT JOIN booking_slot → completed `count(DISTINCT)` |
| 1–30 ก.ย. | แถว CSV | 4 (B10 B11 B12 B13) | `q_counts.csv_rows` · `q_csv_sep` |
| 1–31 ต.ค. | ยืนยัน / ใช้บริการแล้ว / ยกเลิก | 6 / 1 / 0 | `q_counts` |
| 1–31 ต.ค. | ยอดขาย · บัตร · อื่น · ค่ารถ | 1440 · 0 · 1440 · 0 | `q_money` |
| 1–31 ต.ค. | ส่วนลด ก/ร/ด | 0 / 0 / 360 | `q_money` |
| 1–31 ต.ค. | แต้ม · คอร์ส · ยอดนัดยืนยัน | 14 · 0 · 11130 | `q_money` (ไขว้ 14) · `q_pending` |
| 1–31 ต.ค. | คิวต่อนักบำบัด | T05 1 · อื่น 0 | `q_therapist` |
| 6–9 ต.ค. | ทุกตัวเลข | 0 ทั้งหมด (= ③1 ✅) | ทุกคิวรี |
| 1 ส.ค.–31 ต.ค. | วัน · counts · ยอดขาย · แต้ม · คอร์ส | 92 · 6/6/1 · 3340 · 33 · 4 | `q_days` `q_counts` `q_money` |
| 1 ส.ค.–1 พ.ย. | วัน | 93 → ต้อง 422 (= ③2 ✅) | `q_days` |

> ค่าจาก SQL ตรงตัวอย่างคำตอบร้านทั้ง 2 ข้อ → ไม่ต้องหยุดถาม · เสนอแผน (impact §2 ตารางไฟล์ × เทสต์ × หลักฐาน grep) → รออนุมัติ

**ส่วนที่ 2 (ลงมือ)**

| ช่วงวัน | ตัวเลข | SQL | API | หน้าเว็บ | ตรงไหม |
|---|---|---|---|---|---|
| 1–30 ก.ย. | ยืนยัน/ใช้บริการแล้ว/ยกเลิก | 0/3/1 | 0/3/1 (R1) | 0/3/1 (CR05-UI-1) | ✅ |
| 1–30 ก.ย. | ยอดขาย | 1900 | 1900 | ฿1,900 (`data-amount` 1900) | ✅ |
| 1–30 ก.ย. | บัตร · อื่น · ค่ารถ | 0 · 1900 · 0 | 0 · 1900 · 0 | (R1 ครบทุกช่อง) | ✅ |
| 1–30 ก.ย. | ส่วนลด ก/ร/ด | 0/100/0 | 0/100/0 | ระดับ ฿100 | ✅ |
| 1–30 ก.ย. | แต้ม · คอร์ส · ยืนยัน | 19 · 2 · 0 | 19 · 2 · 0 | 19 · 2 | ✅ |
| 1–30 ก.ย. | คิวต่อนักบำบัด | T01 1 T03 1 T05 1 | ตรง 6 คน | ตาราง 6 แถว | ✅ |
| 1–30 ก.ย. | CSV | 4 แถว · B13 `นวดน้ำมันอโรมา` 1900.00 | BOM EF BB BF · หัว 12 คอลัมน์ · 4 แถว (R7) | ไฟล์ดาวน์โหลด `sabai-report-2026-09-01_2026-09-30.csv` ตรวจด้วย Node 3 เบราว์เซอร์ | ✅ |
| 1–31 ต.ค. | counts · ยอดขาย · ส่วนลดเดือนเกิด · แต้ม · ยืนยัน | 6/1/0 · 1440 · 360 · 14 · 11130 | ตรง (R2) | — | ✅ |
| 6–9 ต.ค. | ทุกตัวเลข · CSV | 0 · 0 แถว | 200 ทุกค่า 0 (R3) · CSV หัวอย่างเดียว (R8) | — | ✅ |
| 1 ส.ค.–31 ต.ค. / 1 ส.ค.–1 พ.ย. | 92 / 93 วัน | 92 · 93 | 200 (3340 · 33 · 4) / 422 `REPORT_RANGE` (R4) | 93 วัน → `report-error` `REPORT_RANGE` (UI-2) | ✅ |
| 1–31 ต.ค. หลังกดเสร็จ B01 (clock 12 ต.ค. 14:00) | ยอดขาย · ยืนยัน · completed | 1440+1000 · 11130−1000 · 2 | 2440 · 10130 · 2 = Σ ตารางคิวหลังร้าน (R10) | — | ✅ |

## 4. ตัวเลขสำคัญ

| เรื่อง | ค่า | นับจาก |
|---|---|---|
| คำถามถึงร้าน | 12 ข้อ · ตอบตรง 6 · ตัดสินแทน 7 (Q9 บางส่วน) | `tools/lab10/questions.md` |
| SQL ค่าคาดหวัง | 9 คิวรีชื่อ (`q_counts q_money q_points_txn q_course_txn q_pending q_therapist q_csv_sep q_tz q_days`) × 4 ช่วง · exit 0 | `expected.sql` `expected-out.txt` |
| `tests/cr05.mjs` | ก่อนแก้ **1/12** (R12 แชทผ่านอยู่แล้ว · อื่น 404) · หลังแก้ **12/12** (3.1 วิ · ผ่านรอบแรกหลัง rebuild) | `design/logs/lab10-red.txt` `lab10-green.txt` |
| `e2e-cr/tests/cr05.spec.ts` | **6/6** (2 เทสต์ × chromium/firefox/webkit · 13.9 วิ) | `cr05-spec.log` |
| ตรวจไขว้ รายงาน = Σ ตารางคิว | ก.ย. 1900/3 · ต.ค. 1440/1/11130 · ส.ค.–ต.ค. 3340/6/11130 → ตรง 3/3 | `crosscheck.log` |
| check-rules | **90/90** | `check-rules.log` |
| golden · cr01 · cr02 · cr03 · cr04 | **62/62 · 22/22 · 19/19 · 18/18 · 14/14** | `golden.log` `cr0N.log` |
| e2e-cr chromium | passed **11** · expected-fail **2** (KI-01 KI-02) · failed 0 · flaky 0 (เดิม 9 + 2) | `node count.mjs e2e-cr.json` |
| e2e-legacy api+chromium | api: passed 4 · expected-fail 1 (TC-SEC-04) · **failed 1 (TC-SEC-05 เดิม)** · chromium: passed 34 · expected-fail 2 (TC-GC-04 TC-TRN-03) · failed 0 → รวม **38 / 1 / 3 = baseline** · บรรทัดสรุป Playwright: expected 41 unexpected 1 | `node count.mjs e2e-legacy.json` |
| rebuild | 1 ครั้ง **39 วิ** | `build-1.log` |
| diff | 13 ไฟล์ +944/−7 (`git diff --stat f4edf7b HEAD`) · โค้ดเว็บ 6 ไฟล์ | git |
| i18n ใหม่ | `nav.adminReport` + `report.*` 22 + `err.REPORT_RANGE` = 24 key × 3 ภาษา | `web/lib/i18n.ts` |

## 5. ตัวอย่างแถวเด่น (สำหรับ README)

- **CR-05 R1** owner 1–30 ก.ย. → `counts {0,3,1}` · `revenue 1900` · `discounts.tier 100` · `pointsEarned 19` · `courseSessions 2` · `byTherapist T01/T03/T05 = 1` — ค่ามาจาก `[E sql:q_money]` ไม่ใช่จากหน้า
- **CR-05 R4** 1 ส.ค.–31 ต.ค. (92 วัน) 200 · 1 ส.ค.–1 พ.ย. (93 วัน) 422 `REPORT_RANGE` "เลือกช่วงวันได้ไม่เกิน 92 วัน และวันเริ่มต้องไม่เกินวันสิ้นสุด" `[D:CR-05] ③2`
- **CR-05 R7** CSV ก.ย. → 3 ไบต์แรก `EF BB BF` · `text/csv; charset=utf-8` · แถว `2026-09-30,B13,completed,single,1,นวดน้ำมันอโรมา,1900.00,0.00,1900.00,tier,100.00,19`
- **CR-05 R10** ตั้งเวลา 12 ต.ค. 14:00 → owner กดเสร็จ B01 → ต.ค. ยอดขาย 2440 = Σ ยอดตารางคิวหลังร้าน · ยอดนัดยืนยัน 10130
- **CR05-UI-1** owner เมนู "รายงานยอด" → เลือก ก.ย. → ฿1,900 → กดโหลด CSV → Node อ่านไฟล์ดาวน์โหลด BOM + ไทยตรงตัว (3 เบราว์เซอร์)
- **CR-05 R6** ไม่ล็อกอิน 401 · U01 403 ทั้ง JSON และ CSV · U01 ไม่เห็น `nav-admin-report`

## 6. ตัดสินแทนผู้เรียน

| คำถาม | คำตอบที่เลือก | เหตุผล |
|---|---|---|
| อนุมัติแผน (ส่วน 1 ข้อ 4)? | อนุมัติ | impact มีตารางไฟล์ × เทสต์ × หลักฐาน grep · SQL 3 ช่วง + ขอบ 92/93 พร้อมผล · ตรง ③ ทั้ง 2 ข้อ (ไม่ต้องหยุดถาม) · ไม่มี migration · ไม่แตะ oracle |
| Q2 ยอดขายรวมค่ารถ? | รวม (`revenue` = Σ `total_amount` = giftcard + other) · `transportFee` แยกแสดง | ② ให้ giftcardPaid + otherPaid ซึ่งรวมกันเป็น total_amount ตาม `booking_check6` |
| Q4 แต้มที่ให้ | Σ `booking.points_earned` ของนัดใช้บริการแล้ว | ตรงกับ `point_txn` earn (ไขว้แล้ว 19/14/33) · ผูกกับวันนัดได้ตรง |
| Q5 ครั้งคอร์ส | นัดใช้บริการแล้วที่มี `course_purchase_id` | `completeBooking` ตัด `used_sessions +1` ต่อ 1 นัด |
| Q7 หมอนวด 0 คิว | แสดงทุกคน เรียงรหัส | นักบัญชี/เจ้าของเห็นครบ · ทดสอบง่าย |
| Q9 รูปแบบ CSV | เงิน `1900.00` · ชื่อบริการไทย · ทุกสถานะ · CRLF · RFC 4180 quote · ชื่อไฟล์ `sabai-report-<from>_<to>.csv` | Excel อ่านเป็นตัวเลขได้ · ร้านเป็นคนไทย · ② มีคอลัมน์ status แปลว่ารวมทุกสถานะ |
| Q10 ภาษา | 3 ภาษา | CLAUDE.md ข้อ 8 |
| Q11 ช่วงเริ่มต้น | วันที่ 1 ถึงสิ้นเดือนของ `clock()` | งานสิ้นเดือน · ใช้ clock() ตาม CLAUDE.md |
| error code ช่วงผิด | `REPORT_RANGE` (ใหม่) สำหรับ from > to และ > 92 วัน · วันที่ผิดรูป/ไม่ส่ง = `BAD_REQUEST` | ② บอกแค่ 422 |
| แชทบอท (CLAUDE.md ข้อ 8) | ไม่เพิ่มทางเข้ารายงาน · เพิ่มเคส R12 ล็อกว่าไม่รั่ว | ไม่อยู่ใน CR · รายงานเป็นของ owner |

## 7. ข้อสังเกต 👀

- **seed จับบั๊กโซนเวลาไม่ได้:** `q_tz` = 0 (ทุกนัดอยู่ 10:00–22:00 ไทย = 03:00–15:00 UTC → วัน UTC = วันไทยเสมอ) · การตัดวันด้วย UTC จะเลื่อนขอบ 7 ชม. แต่ไม่มีข้อมูลตกขอบ → ถ้าผู้เรียนเขียน `new Date("2026-09-01")` เทสต์ seed ก็ยังเขียว · พรอมต์ย้ำ "นับตามวันนัดเวลาไทย" ถูกแล้ว แต่ผลที่ seed พิสูจน์ได้จำกัด (เคสขอบที่ดีที่สุดคือ B13 30 ก.ย. 18:00)
- นัดคอร์ส (B10 B12) มียอด ฿0 แต่นับเป็น "ใช้บริการแล้ว" และ "ครั้งคอร์ส" → ก.ย. completed 3 แต่ยอดขายมาจาก B13 นัดเดียว · ถ้าตีความยอดขายคอร์สผิด (ขายแพ็กคอร์ส) จะต้องไปดู `course_purchase` ซึ่ง CR ไม่ได้ขอ
- ยอดนัดยืนยันของ ต.ค. (11130) รวม B06 (10 ต.ค. 15:00) และ B05 (11 ต.ค.) ที่ "วันนี้" ใกล้/เลยเวลาแล้ว → คำตอบร้าน "สถานะยืนยัน" ไม่ดูเวลา · ระวังผู้เรียนตัด `start_at > now`
- R12 (แชท) ผ่านตั้งแต่ก่อนแก้ → เทสต์แดง 11/12 ไม่ใช่ 12/12 · เป็นเคสล็อก "ไม่รั่ว" ไม่ใช่พฤติกรรมใหม่
- พรอมต์ส่วน 1 ใช้ `psql -c "<SQL>"` ขัดกับ CLAUDE.md ข้อ 5 (`docker cp` + `-f`) และ SQL ยาวหลายคิวรีส่งผ่าน `-c` ใน PowerShell ลำบาก (quote/`$`)
- เขียน heredoc ยาว (คอมโพเนนต์ + หน้า + python) ใน bash เดียวแล้ว shell parse พัง ("unexpected EOF") ไม่มีไฟล์ถูกสร้าง → เปลี่ยนไปใช้เครื่องมือ Write (ไม่กระทบผล)
- `/admin/report` เป็น path ซ้อนใต้ `/admin` → `NavMenu` เทียบ `path === href` จึงไฮไลต์เฉพาะลิงก์ที่ตรง (ไม่ไฮไลต์ "หลังร้าน" ซ้อน) ✅

## 8. เจอระหว่างทาง (นอก CR)

- `completeBooking()` (`web/lib/server/booking.ts:534-581`) ไม่ตรวจเวลา: owner กด "ใช้บริการเสร็จ" นัดล่วงหน้าได้ทุกนัด (ตามเอกสาร D12 ของ orchestrator ไม่เขียนเพิ่มว่าอนุญาต/ห้าม) — R10 ตั้งเวลาให้ถึงนัดก่อนกดตามพรอมต์
- ไม่มีวิธีบันทึกยอดขายบัตรของขวัญ/แพ็กคอร์สในรายงาน (`gift_card` `course_purchase` ไม่อยู่ใน booking) → นักบัญชีอาจต้องการรายได้ส่วนนี้ (ไม่อยู่ใน CR-05)

## 9. ปัญหาที่เจอ / วิธีแก้

| ปัญหา | วิธีแก้ |
|---|---|
| log PowerShell `*>` เป็น UTF-8 BOM (ไม่ใช่ UTF-16 อย่าง LAB 9) ใน `node` แต่ `check-rules.log` เป็น UTF-16 | อ่านด้วย `tr -d '\r'` / `iconv -f UTF-16LE` ตามชนิดไฟล์ (`file`) |
| bash heredoc หลายก้อนใน 1 คำสั่ง parse พัง | ใช้เครื่องมือ Write สร้างไฟล์ |
| ไม่มี (เทสต์เขียวรอบแรก · regression = baseline) | — |

## 10. ข้อเสนอแก้พรอมต์

- **H** ส่วน 1 ข้อ 2: เปลี่ยน `docker exec sabai06-db psql -U sabai -d sabai -c "<SQL>"` เป็น "เขียน SQL ลงไฟล์ แล้ว `docker cp` + `psql -v ON_ERROR_STOP=1 -f` (CLAUDE.md ข้อ 5) · ตรวจ `$LASTEXITCODE`" — ตรงกับรั้วที่ผู้เรียนสร้างเอง และ SQL หลายคิวรี + `FILTER`/`$` ผ่าน `-c` ใน PowerShell พังง่าย
- **H** ส่วน 1 ข้อ 3/4 (Plan mode เขียนไฟล์ไม่ได้): เพิ่ม "เสนอเนื้อหา impact ในแชท · หลังผมอนุมัติและออก Plan mode แล้วจึงบันทึก `docs/impact/CR-05.md`"
- **M** ส่วน 1: บอกว่า seed ไม่มีนัดที่ข้ามวัน UTC/ไทย (ให้ผู้เรียนรัน `q_tz` เอง) เพื่อให้เห็นว่าเทสต์ seed พิสูจน์เรื่องโซนเวลาได้จำกัด · หรือเพิ่มขั้น "สร้างนัด 21:30 วันสุดท้ายของเดือนแล้วดูว่าอยู่เดือนไหน" (21:30 ไทย = 14:30 UTC ยังวันเดียวกัน → ต้องเป็นขอบต้นช่วงแทน; seed ร้านเปิด 10:00 จึงทำไม่ได้จริง)
- **M** ส่วน 2 ข้อ 1: บอกว่าเคสแชทที่ล็อก "ไม่รั่ว" อาจผ่านตั้งแต่ก่อนแก้ (แดงไม่ครบทุกเคสเป็นเรื่องปกติ)
- **L** ส่วน 2 ข้อ 3: e2e-cr ใช้ `--reporter=list,json` เพื่อแยก expected-fail (เหมือนข้อเสนอ LAB 9)

## 11. ภาพที่ควรใช้

| ไฟล์ | คำอธิบาย |
|---|---|
| `design/shots/lab10-report-page.png` | `/admin/report` (owner · 1280×800 · reset แล้ว) ช่วง 1–30 ก.ย. 2569: ฟอร์มช่วงวัน + ปุ่มโหลด CSV + จำนวนนัด 0/3/1 (เมนูมี "รายงานยอด") |
| `design/shots/lab10-report-page-full.png` | หน้าเต็ม: ยอดขาย ฿1,900 · ส่วนลดระดับ ฿100 · แต้ม 19 · คอร์ส 2 · คิวต่อนักบำบัด |

### เทียบกับผลที่คาด (เปิดหัวข้อ "ผลที่คาด" หลังเขียนข้อ 1–10 เสร็จ · ตาบอดจริง)

| ผลที่คาด | ผลจริง | ตรงไหม |
|---|---|---|
| ก.ย. completed 3 · cancelled 1 · confirmed 0 | SQL/API/หน้า 3 · 1 · 0 | ✅ |
| ก.ย. revenue 1,900 · otherPaid 1,900 · tier 100 | 1900 · 1900 · 100 | ✅ |
| ก.ย. แต้ม 19 · ครั้งคอร์ส 2 | 19 · 2 | ✅ |
| ก.ย. T01 1 T03 1 T05 1 | T01 1 T03 1 T05 1 (T02 T04 T06 = 0 แสดงด้วย) | ✅ |
| ต.ค. completed 1 · confirmed 6 · revenue 1,440 · birthday 360 · แต้ม 14 · pending 11,130 | 1 · 6 · 1440 · 360 · 14 · 11130 | ✅ |
| 6–9 ต.ค. ทุกค่า 0 | 200 ทุกค่า 0 | ✅ |
| 92 วัน 200 / 93 วัน 422 | 200 / 422 `REPORT_RANGE` | ✅ |
| CSV ก.ย. 4 แถว (B10 B11 B12 B13) มี BOM | 4 แถว ลำดับ B10 B11 B12 B13 · `EF BB BF` | ✅ |
| U01 403 · ไม่ล็อกอิน 401 | 403 / 401 (JSON + CSV) | ✅ |
| ไปต่อได้เมื่อ: ค่าคาดหวังทุกตัวมี SQL + ผลจริงใน impact ก่อน commit แก้ | impact §3 อยู่ใน commit `15fb782` (ก่อน `ef47d72`) | ✅ |
| cr05 เขียว | 12/12 | ✅ |
| CSV เปิดแล้วภาษาไทยไม่เพี้ยน | ตรวจไบต์ด้วย Node: "นวดน้ำมันอโรมา" ตรงตัว + BOM (3 เบราว์เซอร์) · ไม่ได้เปิดใน Excel จริง (ไม่มี Excel ใน sandbox) | ✅ (ด้วย Node) |
