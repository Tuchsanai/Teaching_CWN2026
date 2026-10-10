# BUILD-PROMPT · สร้างเว็บ "สบายใจ สปา · Sabai Jai Wellness Spa"

> วางทั้งไฟล์นี้ให้ Claude Code หน้าต่างใหม่ ในโฟลเดอร์ที่มี REQUIREMENTS.md · DESIGN.md · TEST-DATA.md

สร้างเว็บ "สบายใจ สปา · Sabai Jai Wellness Spa" ใหม่ทั้งหมด ทำทีละขั้นตามเลข จบแต่ละขั้นให้บอก 1 บรรทัดว่าเสร็จอะไร
**ถ้าขั้นไหนไม่ผ่าน ให้หยุดทันทีแล้วบอกสาเหตุ อย่าข้ามไปขั้นถัดไป**

## ขั้น 0 · อ่านก่อนลงมือ
- อ่าน REQUIREMENTS.md (FR-01–35, BR-01–20, NFR-01–18 + สมมติฐาน A1–A20), DESIGN.md (สถาปัตยกรรม, flowchart, ERD, sequence, D1–D15)
  และ TEST-DATA.md (seed + ค่าขอบ E01–E90 + สมมติฐาน T1–T17) ให้ครบทุกบรรทัด
- ข้อไหนเอกสารขัดกัน: TEST-DATA.md > REQUIREMENTS.md > DESIGN.md · คำถาม D1–D15 ใช้ "ข้อเสนอที่ใช้ในแบบนี้" ของ DESIGN.md
- ห้ามเพิ่มฟีเจอร์นอกเอกสาร ยกเว้นที่ขั้นนี้สั่ง

## ขั้น 1 · โครงโปรเจกต์ + ใช้ได้บน Windows
- โครง: `db/` (compose ของฐานข้อมูล) และ `web/` (compose + โค้ด Next.js) เป็น 2 โปรเจกต์ docker compose แยกกัน
- `.gitattributes` ที่ราก: `* text=auto eol=lf` (+ `*.png *.jpg *.webp *.wav binary`)
- **ห้ามมีไฟล์ .sh ที่ต้องรัน** · สคริปต์ช่วยทุกตัวเป็น `node scripts/*.mjs` · คำสั่งทุกตัวที่บอกผมต้องรันใน PowerShell ได้ (ไม่ใช้ `&&`, `export`, `rm -rf`)
- ก่อนเปิด container: `docker ps --format "{{.Names}} {{.Ports}}"` ถ้ามี container อื่นจับพอร์ต 3000 หรือ 5433 (เช่น petshop) ให้ `docker stop <ชื่อ>` (stop อย่างเดียว ห้ามลบ)
- สร้าง network ถ้ายังไม่มี: `docker network inspect sabai-net *> $null; if (-not $?) { docker network create sabai-net }`

## ขั้น 2 · ฐานข้อมูล `db/`
- `db/compose.yaml`: service/container **sabai-db** image `postgres:16-alpine` · volume `sabai-pgdata` · พอร์ต `5433:5432`
  · network `sabai-net` (external) · `TZ=Asia/Bangkok` · healthcheck `pg_isready -U sabai -d sabai` (interval 5s, retries 20)
- `db/init/01-schema.sql` ตาม ERD ใน DESIGN.md §4 ครบ 17 ตาราง + ตาราง `hotel` (H01–H06): เงิน `NUMERIC(10,2)` · แต้ม `INTEGER` · ครั้งคอร์ส `SMALLINT`
  · เวลา `TIMESTAMPTZ` · ทุก CHECK/EXCLUDE ในตาราง "กติกาที่ db ช่วยบังคับ" (ใช้ `btree_gist`, ช่วง `[start,end)`)
  · **ห้ามมีตาราง/คอลัมน์รูปโปรไฟล์หรือรูปหน้า** (NFR-10) · เพิ่มคอลัมน์ `password_hash`, `role` (customer/owner) ได้
- `db/init/02-seed.sql` = TEST-DATA.md **ทุกค่า**: ผู้ใช้ U01–U08, บริการ S01–S07, P01, K01, สมุนไพร, นักบำบัด T01–T06 + บริการที่ทำได้
  + รีวิว 17 รายการ, ห้อง Couple Suite, โรงแรม H01–H06, นัด B01–B13 (+ booking_slot), คอร์ส C01–C04, รอบเอว 4 จุด, รูป before/after 2 รูปของ C01,
  Gift Card GC01–GC05 (+txn), birthday_use ของ U05 (202610), point_txn ที่สอดคล้องแต้ม seed
  · เพิ่มบัญชีเจ้าของร้าน `owner@sabai.test / Owner@2026` (role owner) สำหรับหน้า /admin · รหัสผ่านเก็บเป็น hash (bcrypt)
- ให้ seed อยู่ใน SQL ที่ web เรียกซ้ำได้ด้วย (ใช้ตอน reset ขั้น 8) — ห้ามมีค่าซ้ำ 2 ที่ที่อาจไม่ตรงกัน

## ขั้น 3 · เว็บ `web/` (ตาม DESIGN.md)
- Next.js App Router + TypeScript · ต่อ PostgreSQL 16 ด้วย `pg` (Pool) **เขียน SQL ตรง ๆ ไม่ใช้ ORM**
- กฎร้านทั้งหมดเป็นฟังก์ชันบริสุทธิ์ใน `lib/rules/*` (BR-01–BR-20) ราคา "ที่เก็บจริง" คิดที่เซิร์ฟเวอร์เสมอ
  POST /api/bookings รับ `quotedTotal` ถ้าไม่เท่ายอดที่คิดใหม่ตอบ 409 (NFR-17) · จองใช้ transaction + EXCLUDE → ชนแล้วตอบ 409 "เวลานี้ถูกจองแล้ว" (NFR-12)
- นาฬิกาเดียว `lib/clock.ts`: อ่าน `app_setting.test_today` → env `TODAY` → เวลาจริง · ทุกกฎที่ใช้วันที่ (BR-03/07/13/14/16) ต้องเรียกตัวนี้ 100% (NFR-13)
- ล็อกอินอีเมล+รหัสผ่าน (cookie httpOnly ลงลายเซ็นด้วย `SESSION_SECRET`) · ไม่ล็อกอินจองด้วยชื่อ+เบอร์ได้แต่ไม่ได้แต้ม (T3)
- /admin (role owner): ตารางคิว · กด "ใช้บริการเสร็จ" (ให้แต้ม BR-09 + ตัดครั้งคอร์ส + บันทึกรอบเอว) ตาม D3, D5, D11
- รูป before/after เสิร์ฟผ่าน API ที่ตรวจเจ้าของ (คนอื่น 403 · ไม่ล็อกอิน 401) เก็บนอก `public/` (NFR-11)
- ห้ามต่อฐานข้อมูลตอน build: หน้า/route ที่ใช้ db ตั้ง `export const dynamic = "force-dynamic"` และสร้าง Pool แบบ lazy

## ขั้น 4 · Docker ของ web
- `web/Dockerfile` multi-stage · `next.config` ใช้ `output: "standalone"` · รันด้วย `node server.js`
- `web/compose.yaml`: container **sabai-web** พอร์ต `3000:3000` · network `sabai-net` (external)
  · env: `DATABASE_URL=postgres://sabai:sabai@sabai-db:5432/sabai` · `HOSTNAME=0.0.0.0` · `TZ=Asia/Bangkok`
  `BUG_MODE=${BUG_MODE:-0}` · `ALLOW_TEST_RESET=${ALLOW_TEST_RESET:-1}` · `SESSION_SECRET`
- `GET /api/health` → `{"ok":true,"db":true}` (ทำ `SELECT 1`) · ต่อ db ไม่ได้ → `{"ok":true,"db":false}` (ไม่ throw)
- healthcheck ด้วย node (ไม่ใช้ curl/wget):
  `node -e "fetch('http://127.0.0.1:3000/api/health').then(r=>r.json()).then(j=>process.exit(j.db?0:1)).catch(()=>process.exit(1))"`

## ขั้น 5 · รูปภาพ (ห้ามใช้รูปจากเน็ต · ทุกรูปอยู่ที่ `web/public/assets/`)
- รัน `codex --version` ก่อน
- **ถ้ามี Codex CLI**: สั่ง `codex exec "..."` ให้ใช้เครื่องมือสร้างรูปในตัว โทนไทยร่วมสมัย (เขียวใบตอง ครีม ทอง) ทีละรูป:
  hero · บริการทุกตัว (S01–S07, P01, K01) · นักบำบัดทุกคน (T01–T06 แบบภาพวาด) · Gift Card 3 ลาย (orchid, lotus, gold)
  · panorama ห้อง Couple Suite สัดส่วน 2:1 สำหรับทัวร์ 360° · ใบหน้าตัวอย่าง**แบบภาพวาด (ไม่ใช่คนจริง)** สำหรับวิเคราะห์ผิว/ภาพจำลองก่อน-หลัง
  · รูปสัดส่วนร่างกายไม่มีใบหน้า before/after (ไม่อยู่ใน public/)
  Codex เก็บรูปไว้ใต้ `~/.codex/generated_images` → คัดลอกมาแล้วย่อด้วย `node scripts/resize.mjs` (sharp: กว้าง ≤ 1600px, panorama ≤ 4096px, webp)
  **รูปไหนสร้างไม่สำเร็จ ให้ใช้ SVG/CSS เฉพาะรูปนั้น**
- **ถ้าไม่มี Codex CLI**: Claude สร้างทุกรูปเองเป็น SVG / CSS
- เพลงสปา: ห้ามโหลดจากเน็ต สร้างเองด้วย Web Audio API หรือ `node scripts/make-music.mjs` เขียนไฟล์ .wav
- เขียน `web/ASSETS.md` ตาราง: ไฟล์ | ใช้ที่หน้าไหน | สร้างด้วย Codex หรือ SVG/CSS

## ขั้น 6 · ดีไซน์
- ไทยร่วมสมัย: เขียวใบตอง ครีม ทอง · ลายกล้วยไม้/บัว ที่หน้าแรกและหน้าจอง (FR-32) · การ์ดมีเงา · animation นุ่ม ๆ (เคารพ `prefers-reduced-motion`)
- ฟอนต์ไทยอ่านง่าย self-host (เช่น `@fontsource/sarabun`) เนื้อหา ≥ 16px line-height ≥ 1.5 (NFR-05)
- มือถือ 375px: ไม่มีเลื่อนข้าง ปุ่มหลัก ≥ 44×44px (NFR-01, NFR-04) · เงินแสดงแบบ ฿1,234 (มีสตางค์แสดง ฿1,187.50)

## ขั้น 7 · ฟีเจอร์ (ครบ FR-01–FR-35 · ตัวเลขทุกตัวตรง BR และ TEST-DATA.md)
- จอง 4 ขั้น เดี่ยว/คู่/กลุ่ม/แพ็กเกจ/จองด้วยคอร์ส · หน้ายืนยันแสดงสมุนไพร + ราคาแยกบรรทัด + ค่ารถ (FR-01–06, 14, 21–23, 31)
- ยกเลิกนัด 24 ชม. · นักบำบัด+ตัวกรอง 4.5 · แต้ม/แลกแต้ม · ระดับ+ข้อความ "อีก ฿X" · เดือนเกิด · คอร์ส/Wallet/กราฟรอบเอว/ประวัติ
  · Gift Card ซื้อ/ใช้ · 3 ภาษา (ไทย/English/中文 จำด้วย cookie `lang`) · ทัวร์ 360° (เมาส์+นิ้ว) (FR-07–20, 24, 33 · NFR-06, NFR-18)
- "AI" ทุกตัวเป็น**กฎ/ตารางตายตัว ไม่สุ่ม ไม่เรียก API ภายนอก** (NFR-15): แชทตอบเวลา/ราคา 3 ภาษา + จองผ่านแชทด้วย API เดียวกับเว็บ (FR-25–26)
  · อารมณ์วันนี้ 4 แบบ (FR-27) · แบบทดสอบ 4 ข้อ (FR-28)
- วิเคราะห์ผิว: แจ้งข้อความก่อนเลือกรูป · คำนวณด้วย Canvas **ในเบราว์เซอร์ ไม่อัปโหลดรูป** ไม่เก็บใน localStorage/IndexedDB (FR-29, NFR-09)
  · ภาพจำลองก่อน/หลังมีป้าย "ภาพจำลอง ผลจริงแต่ละคนต่างกัน" ทุกครั้ง (FR-30) · ไม่มีช่องอัปโหลดรูปโปรไฟล์ทุกหน้า (FR-35)
- เพลง: **เปิดด้วยปุ่มเท่านั้น** ไม่มี autoplay (FR-34, NFR-08)
- ส่ง Gift Card ทาง LINE/email **เป็นการจำลอง** ไม่ส่งจริง แสดงข้อความที่ "ส่ง" บนหน้าจอ

## ขั้น 8 · สิ่งที่ใช้ทดสอบ
- `data-testid` ให้**ทุก**ปุ่ม ช่องกรอก ผลลัพธ์ (ราคา แต้ม ระดับ ข้อความยืนยัน ฯลฯ) และข้อความ error · ทุกปุ่ม/ช่องมีชื่อที่ getByRole หาได้ (NFR-16)
- `<html data-ready="true" data-bug-mode="0|1">` (data-ready ตั้งหลัง hydrate เสร็จ)
- `POST /api/test/reset` ทำงานเมื่อ `ALLOW_TEST_RESET=1` เท่านั้น (ไม่งั้น 404): ล้างทุกตารางกลับเป็น seed ใน transaction เดียว ≤ 5 วินาที กด 2 ครั้งผลเท่ากัน (NFR-14)
  รับ body `{"now":"<ISO>"}` เพื่อล็อก "วันนี้" · ไม่ส่ง now = `2026-10-10T10:00:00+07:00` (TEST-DATA.md §1) · ตอบ `{"ok":true,"now":"..."}`

## ขั้น 9 · BUG_MODE (env ของ web ค่าเริ่มต้น 0)
- `BUG_MODE=1` เปิดบั๊กที่ตั้งใจใส่ **3 ตัว** — Claude เลือกเองจาก BR ใน REQUIREMENTS.md:
  1 ตัวเรื่องเงิน · 1 ตัวเรื่องการจอง · 1 ตัวเรื่องตัวเลข/สถานะที่ต้องอัปเดตหลังทำรายการ
- ทุกตัวต้องเป็นแบบ "**ถ้าลอกค่าจากหน้าจอไปเป็นผลที่คาดหวัง จะจับไม่ได้**" (หน้าจอกับ db ผิดตรงกัน จับได้เฉพาะคนที่คิดจาก BR/TEST-DATA เอง)
  และ `BUG_MODE=0` ต้องไม่มีบั๊กเหล่านี้เลย
- เขียนเฉลย (BR ที่ผิด · เคส E ที่จับได้ · ไฟล์/ฟังก์ชัน) ที่ `web/BUGS.md` **เท่านั้น** — ห้ามบอกในแชท ห้ามเขียนใน SPEC.md
  ห้ามคอมเมนต์ที่เดาง่าย (เช่น `// BUG`) และห้ามตั้งชื่อตัวแปรที่บอกใบ้ อ่านค่าผ่าน `lib/flags.ts` จุดเดียว

## ขั้น 10 · `web/SPEC.md`
- หน้าเว็บทุกหน้า (path + ทำอะไร) · กฎโยงรหัส FR/BR → ไฟล์/ฟังก์ชัน · ตาราง `data-testid` ทุกตัว (หน้า | testid | คืออะไร)
- ข้อความ error **คำต่อคำ** ทั้ง 3 ภาษา (เช่น "เวลานี้ถูกจองแล้ว", "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน", "อยู่นอกพื้นที่รับส่ง", "บัตรหมดอายุแล้ว")
- API ทุกเส้น: method | path | body | ตอบกลับ | รหัสสถานะ (200/201/401/403/404/409/422) · ผู้ใช้ seed (อีเมล/รหัสผ่าน/ใช้ทดสอบอะไร) + owner
- วิธีรันบน PowerShell (ขั้น 11) · env ทั้งหมด

## ขั้น 11 · เปิดระบบและตรวจ (หยุดทันทีถ้าข้อไหนไม่ผ่าน แล้วบอกสาเหตุ)
1. หยุด container ที่จับพอร์ต 3000/5433 · สร้าง network `sabai-net`
2. `docker compose -f db/compose.yaml up -d` → รอจน `docker inspect -f "{{.State.Health.Status}}" sabai-db` = healthy
3. `docker compose -f web/compose.yaml up -d --build` → รอจน sabai-web = healthy (build ต้องไม่ต่อ db)
4. `Invoke-RestMethod http://localhost:3000/api/health` ต้องได้ `ok=true, db=true`
5. เขียน `web/scripts/check-rules.mjs` (node + fetch) ยิง API ตรวจกฎร้านตามตาราง E01–E90 ของ TEST-DATA.md ทุกเคสที่ทำผ่าน API ได้
   (reset ก่อนทุกเคส ใช้ now ตามแถว · เคสที่เป็น unit test ให้เรียกฟังก์ชัน `lib/rules` ตรง) → รายงาน "ผ่าน X / Y ข้อ" และรายการที่ล้ม
   ต้องผ่านครบที่ `BUG_MODE=0` ถ้าไม่ครบให้แก้โค้ดแล้วรันใหม่ (ห้ามแก้ค่าที่คาดหวังให้ตรงกับโค้ด)
6. `Start-Process http://localhost:3000` เปิดให้ผมดู
7. สรุปเป็นตาราง: ขั้น | ผล (✅/❌) | หลักฐาน (สถานะ container, ผล /api/health, ผ่าน X/Y, จำนวนรูป Codex/SVG)
   **ห้ามบอกว่าเลือกบั๊กอะไร** บอกแค่ว่า "เขียนเฉลยไว้ที่ web/BUGS.md แล้ว"
