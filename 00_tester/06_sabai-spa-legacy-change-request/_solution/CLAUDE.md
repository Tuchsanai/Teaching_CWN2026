# สบายใจ สปา · ระบบเดิมที่รับมอบ (legacy) — งานของเราคือแก้ตาม Change Request

## รันยังไง (PowerShell · จากโฟลเดอร์บท)
- เปิดระบบ (ครั้งแรกสร้าง network ก่อน): `docker network create sabai06-net` → `docker compose -f db/compose.yaml up -d --wait` → `docker compose -f web/compose.yaml up -d --build --wait` → http://localhost:4000 · ตรวจ `Invoke-RestMethod http://localhost:4000/api/health` ต้องได้ `db: True`
- พอร์ตไม่ว่าง: ตั้ง `$env:WEB_PORT` `$env:DB_PORT` ก่อน `up` และ `$env:BASE_URL="http://localhost:<พอร์ต>"` ก่อนรันเทสต์ทุกชุด
- reset ข้อมูลทดสอบ (วันนี้ = 10 ต.ค. 2026 10:00): `Invoke-RestMethod -Method Post -Uri http://localhost:4000/api/test/reset -ContentType 'application/json' -Body '{}'`
- ชั้น 1 กฎร้าน (~20 วิ · ต้อง 90/90): `node web/scripts/check-rules.mjs`
- ชั้น 2 e2e (ค่าเริ่ม api + chromium ~4 นาที): `Push-Location e2e-legacy; npx playwright test --reporter=list; Pop-Location`
- ครบ 3 เบราว์เซอร์ (~13 นาที · รัน background): `Push-Location e2e-legacy; npm run test:all; Pop-Location`
- ผลอ้างอิงตอนรับมอบ (HANDOVER-CHECK.md): check-rules 90/90 · e2e api+chromium ผ่านจริง 38 · ล้ม 1 (TC-SEC-05) · `test.fail` 3 (TC-SEC-04 TC-GC-04 TC-TRN-03) — บรรทัดสรุป Playwright นับ `test.fail` รวมใน passed ต้องแยกเอง

## แผนที่
@SYSTEM-MAP.md

## ห้ามแตะ
- ห้าม `docker compose down -v` และห้ามลบ volume `sabai06-pgdata` (มีข้อมูลลูกค้าจริง) · ปิดระบบใช้ `down` เฉย ๆ
- ห้ามเปิด `README.md` ของบท `fast_track/` และ `_solution/` (กันใน .claude/settings.json ด้วย) · เปิด `CHANGE-REQUESTS/answers/` เฉพาะเมื่อผมสั่ง
- ห้ามแก้ค่าที่คาดหวังเดิมใน `web/scripts/check-rules.mjs`, `e2e-legacy/` และ `tests/golden/` ถ้าไม่มี CR อนุญาต · จำเป็นต้องแก้ → หยุดถามผมก่อน แล้วจดใน `docs/ORACLE-CHANGES.md` (`e2e-legacy/**` มีรั้ว deny ใน `.claude/settings.json`)
- โค้ดใหม่ใช้ "วันนี้" จาก `clock()` (`web/lib/clock.ts`) เท่านั้น ห้าม `new Date()` ตรง

## กติกาการแก้
1. ก่อนแก้ทุกครั้ง: อธิบายและทำ impact ตาม `docs/IMPACT-TEMPLATE.md` (หลักฐาน grep ไฟล์:บรรทัด) แล้วรอผมอนุมัติ
2. เทสต์ใหม่ต้อง**แดงก่อนแก้** (เก็บผลแดงไว้) · แก้ให้เล็กที่สุด · หลังแก้รันชั้น 1 + ชั้น 2 ซ้ำ
3. ค่าที่คาดหวังติดป้ายแหล่งเสมอ: `[D:CR-0N]` = คำตอบร้าน · `[E ev_xxxxxxxx]` = หลักฐานระบบ (ใช้ได้เฉพาะล็อกพฤติกรรมเดิม) · `[E]` ขัด `[D]` = ผู้ต้องสงสัยบั๊ก → รายงาน ห้ามใช้ `[E]` นั้นเป็นค่าคาดหวัง
4. เปลี่ยนโครง DB = ไฟล์ migration แยกใน `db/migrations/` เท่านั้น (ทางเดียวสำหรับฐานที่มีข้อมูลอยู่แล้ว) · รันซ้ำได้ (`IF NOT EXISTS`/ตรวจก่อนทำ) · มีไฟล์ถอยกลับ · แก้ `db/init` ได้เฉพาะให้เครื่องติดตั้งใหม่และ reset ตรงกับ migration ห้ามใช้ `db/init` เป็นวิธี deploy
5. รัน SQL: `docker cp <ไฟล์>.sql sabai06-db:/tmp/` → `docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/<ไฟล์>.sql` · ห้าม pipe ไฟล์ภาษาไทยผ่าน PowerShell
6. ภาษาไทย/จีนกับ PowerShell 5.1: ยิง API ที่มีข้อความไทย/จีนด้วยสคริปต์ node หรือ `curl.exe --data-binary '@ไฟล์.json'` · ห้าม `Invoke-RestMethod -Body '<ไทย>'` · `curl` เฉย ๆ = Invoke-WebRequest · ตรวจข้อความไทยใน DB ด้วยการเทียบใน SQL (`SELECT name_th = '<ข้อความ>'`) หรืออ่านผ่าน API ด้วย node · ห้ามตัดสินจากตัวอักษรที่ PowerShell แสดง และห้ามแก้ข้อมูลเพราะเห็นตัวอักษรเพี้ยนบนจอ
7. build หรือชุดทดสอบที่นานเกิน 2 นาที (`up --build` ครั้งแรก · e2e 3 เบราว์เซอร์) → รัน background หรือ timeout ยาว แล้วรอผลจริง ห้ามตัดจบ
8. ข้อความใหม่ต้องครบ 3 ภาษา th/en/zh (`web/lib/i18n.ts`) · error ใหม่ต้องตรวจผลในแชทบอท (`/api/chat` · `web/lib/bot/chat.ts`) ด้วย
9. เอกสารเก่าขัดกับโค้ด → รายงานแล้วถามผม ห้ามเลือกเอง

## กับดัก (รายละเอียด SYSTEM-MAP §6)
- T1 `room_id = 1` ตายตัว `web/lib/server/booking.ts:290` `:376`
- T2 ตารางใหม่ต้องเติม `TABLES` ใน `web/lib/server/testmode.ts:11-15` ไม่งั้น reset ไม่ล้าง
- T3/T4 `db/init` รันเฉพาะ volume ว่าง · seed ถูก COPY เข้า image → แก้ seed แล้วต้อง `up --build` เว็บใหม่
- T5/T6 ราคาแพ็กเกจและกฎจำนวนคนคิดซ้ำในเบราว์เซอร์ (`PackageCalc.tsx:24` · `BookingWizard.tsx:125`)
- T7/T8 ค่ากฎซ้ำในข้อความ i18n/แชท และใน DB CHECK → เปลี่ยนกฎต้องแก้ครบทุกที่ (CHECK แก้ด้วย migration)
- T9 `ALLOW_TEST_RESET=1` ล็อกนาฬิกาที่ `app_setting.test_today`
- T10 หน้า server component เรียก `lib/server/*` ตรง ไม่ผ่าน API → แก้ที่ lib
- T11 `23P01` ทุกตัว → 409 `SLOT_TAKEN` (`web/lib/server/http.ts:42`)
- T13 URL ต่อ string (`` `/api/slots?${q}` ``) → grep ทั้ง `"/api/` และ `` `/api/ ``

## เอกสารเก่า
`web/SPEC.md` (ฉบับ 1.0) ไม่ตรงโค้ดหลายจุด · ใช้โค้ด + คำตอบร้านเป็นหลัก · ข้อขัดแย้งที่รู้แล้ว:
@docs/SPEC-GAPS.md
