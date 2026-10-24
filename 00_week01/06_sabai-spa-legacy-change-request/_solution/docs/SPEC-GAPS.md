# SPEC-GAPS · `web/SPEC.md` (ฉบับ 1.0 ก.ย. 2569) เทียบกับโค้ดจริง

> ตารางนี้ **ไม่ตัดสิน** ว่าฝั่งไหนถูก · ทุกแถวเป็นคำถามที่ต้องให้ร้าน (เจ้าของระบบ) ตอบก่อนแก้อะไร
> หลักฐาน: [source ไฟล์:บรรทัด] · [DB ชื่อ constraint] · [runtime = ผลยิงจริงบนระบบที่รันอยู่ วันที่ 12 ต.ค. 2026 · รอบนี้รันที่ `localhost:4100`]
> แถวที่มาจาก triangulation ใน `SYSTEM-MAP.md` §7 มีป้าย ⚠️ อ้างกลับ

## ก. กฎ / พฤติกรรม

| # | SPEC บอก | โค้ดทำ | หลักฐาน | คำถามถึงร้าน |
|---|---|---|---|---|
| G4 | BR-17 "≤ 5 กม. ฟรี · ≤ 15 กม. ฿300/คัน · > 15 ไม่รับ" [SPEC §4 บรรทัด 111] | ปัดระยะเป็นทศนิยม 1 ตำแหน่งก่อนเทียบ → 15.04 กม. ยังรับ (คิด ฿300) · 5.04 กม. ฟรี | [source `web/lib/rules/transport.ts:19-22`] · [runtime `GET /api/transport?distance=15.04&people=1` → `fee 300` · `15.05` → `OUT_OF_AREA` · `5.04` → `fee 0`] · [DB `booking_distance_km_check` ≤ 15.0 (NUMERIC(4,1))] | ระยะที่เกิน 15 หรือ 5 กม. เพียงเล็กน้อย (เช่น 15.04) ร้านนับเป็น "เกิน" หรือปัดก่อน? ร้านวัดระยะละเอียดแค่ไหน |
| G5 | BR-09 "แต้ม = floor(ยอดจ่าย ÷ 100) หลังส่วนลด ไม่รวมรถ − Gift Card" [SPEC §4 บรรทัด 103] | หักยอดที่จ่ายด้วย Gift Card **ทั้งก้อน** ออกจากฐานแต้ม แม้ส่วนหนึ่งของบัตรจ่ายค่ารถ (ซึ่งไม่อยู่ในฐานอยู่แล้ว) | [source `web/lib/rules/points.ts:29-31` · `web/lib/rules/pricing.ts:88-90`] · [runtime U01 ล็อกอิน · S01 เดี่ยว + โรงแรม H04 (฿300) + `SABAI-GC-LAST` ฿500 → gross 1,000 · ส่วนลด 50 · total 1,250 · GC 500 · `pointsToEarn = 4`] | เมื่อ Gift Card จ่ายครอบคลุมค่ารถด้วย ส่วนที่จ่ายค่ารถควรถูกหักจากฐานแต้มไหม (ตัวอย่างนี้ได้ 4 แต้ม · ถ้านับว่าบัตรจ่ายค่ารถก่อนจะได้ 7) |
| G6 | BR-06 "กลุ่ม ≥ 4 ลด 10% (ไม่ใช้กับแพ็กเกจ)" · BR-11 Silver/Gold/Platinum ไม่ระบุว่าใช้กับแพ็กเกจไหม [SPEC §4 บรรทัด 100, 105] | แพ็กเกจและคอร์ส **ไม่มีส่วนลด % ทุกชนิด** รวมส่วนลดระดับสมาชิก 5%/10% | [source `web/lib/rules/pricing.ts:48`] | สมาชิก Gold/Platinum ซื้อแพ็กเกจ Bangkok Relax ได้ส่วนลดระดับไหม |
| G9 | `/admin` "ใช้บริการเสร็จ" · `POST /api/admin/bookings/:id/complete` ตอบ 422 เฉพาะ `NOT_CONFIRMED` [SPEC §3 บรรทัด 85 · §6 บรรทัด 229] · ไม่ระบุเงื่อนไขเวลา | กดเสร็จได้ทุกนัดที่ `confirmed` ไม่ตรวจว่าถึงเวลานัดแล้วหรือยัง (ให้แต้ม/ตัดครั้งคอร์สทันที) | [source `web/lib/server/booking.ts:493-501` (ตรวจแค่ role + status) · `web/components/AdminQueue.tsx:100` (ปุ่มแสดงเมื่อ `confirmed`)] | ร้านต้องการให้กด "ใช้บริการเสร็จ" ได้ก่อนเวลานัดหรือไม่ <!-- 🔒 ข้อสอบชุด B (ข้อ 5): กด "ใช้บริการเสร็จ" ก่อนถึงเวลานัด — เฉลยเฉพาะผู้สอน ห้ามคัดไปไว้ในส่วนของผู้เรียน --> |
| G13 | ยกเลิก < 24 ชม. "ยกเลิกเองไม่ได้ กรุณาโทรหาร้าน" [SPEC §5 บรรทัด 165 · §3 บรรทัด 83] | เจ้าของร้าน (owner) ยกเลิกผ่าน API ได้ แต่ติดกฎ 24 ชม. เหมือนลูกค้า และหน้า `/admin` ไม่มีปุ่มยกเลิก | [source `web/lib/server/booking.ts:465-467` · `web/components/AdminQueue.tsx:100` (มีแค่ปุ่มเสร็จ)] | เมื่อลูกค้าโทรมายกเลิกช่วง < 24 ชม. ร้านยกเลิกในระบบด้วยวิธีไหน · ต้องการคืนแต้ม/ครั้งคอร์สไหม |
| G11 | BR-04 "Couple Suite 1 คู่/ช่วง" [SPEC §4 บรรทัด 98] | ห้องคู่ล็อก `room_id = 1` ในโค้ด 2 ที่ (DB รองรับหลายห้องได้) | [source `web/lib/server/booking.ts:290` `:376`] · [DB `booking_room_no_overlap` แยกตาม room_id] · seed 1 ห้อง `db/init/02-seed.sql:95` | ร้านมีห้องคู่ 1 ห้องตลอดไปไหม หรือมีแผนเพิ่ม |

## ข. ความปลอดภัย / การตั้งค่าที่ส่งมอบ

| # | SPEC บอก | โค้ดทำ | หลักฐาน | คำถามถึงร้าน |
|---|---|---|---|---|
| G7 | `ALLOW_TEST_RESET` ค่าเริ่มต้น `1` = เปิด `/api/test/*` ใช้ `test_today` เป็นนาฬิกา แสดงบัญชีทดสอบ [SPEC §2 บรรทัด 55] · ไม่บอกว่าเครื่องจริงต้องตั้งเป็น 0 | compose และโค้ดใช้ค่าเริ่มต้น `1` · seed ใส่ `test_today = 2026-10-10T10:00+07` → "วันนี้" ค้าง · ใครก็ `POST /api/test/reset` ล้างข้อมูลได้ (ไม่ต้องล็อกอิน) | [source `web/compose.yaml:19` · `web/lib/config.ts:5` · `web/lib/clock.ts:18-22` · `web/app/api/test/reset/route.ts:8-13`] · [runtime `/api/test/today` → `2026-10-10T10:00:00+07:00`] · `db/init/02-seed.sql:217` | ระบบจริงของร้านรันด้วย `ALLOW_TEST_RESET` เท่าไร · ฐานจริงมีแถว `test_today` ไหม |
| G8 | `POST /api/auth/logout` → `{"ok":true}` [SPEC §6 บรรทัด 208] | logout ลบ cookie ฝั่งเบราว์เซอร์อย่างเดียว · token ลงลายเซ็นแบบ stateless ใช้ต่อได้จนหมดอายุ 7 วัน | [source `web/app/api/auth/logout/route.ts:7-8` · `web/lib/session.ts:6` `:26-41`] | ยอมรับได้ไหมว่า token ที่หลุดยังใช้ได้หลัง logout (ถ้าไม่ได้ ต้องเพิ่มที่เก็บ session) |

## ค. เอกสาร / วิธีรันที่ไม่ตรงระบบจริง

| # | SPEC บอก | โค้ดทำ | หลักฐาน | คำถามถึงร้าน |
|---|---|---|---|---|
| G1 | network `sabai-net` · container `sabai-db` `sabai-web` · เว็บ `http://localhost:3000` [SPEC บรรทัด 6, 14, 19, 23, 27, 30, 34] | network `sabai06-net` · container `sabai06-db` `sabai06-web` · host port `${WEB_PORT:-4000}` | [source `web/compose.yaml:1` `:11` `:14` `:22-23` · `db/compose.yaml:6` `:19-20`] | ระบบจริงของร้านใช้ชื่อ/พอร์ตชุดไหน · เอกสารไหนคือวิธีรันฉบับทางการ |
| G2 | `DATABASE_URL` ค่าเริ่มต้น `postgres://sabai:sabai@sabai-db:5432/sabai` ใน `sabai-net` [SPEC §2 บรรทัด 51] | compose ใช้ `sabai06-db` · ถ้าไม่มี env โค้ดใช้ `localhost:5433` | [source `web/compose.yaml:16` · `web/lib/db.ts:11`] | ยืนยันชื่อ host ของฐานข้อมูลบนเครื่องจริง |
| G3 | check-rules ใช้ `BASE_URL` ค่าเริ่มต้น `http://localhost:3000` [SPEC §1 บรรทัด 44] | สคริปต์ใช้ค่าเริ่มต้น `http://localhost:4000` | [source `web/scripts/check-rules.mjs:2` `:8`] | ใช้ค่าไหนเป็นมาตรฐานของทีมทดสอบ |
| G12 | อ้าง `REQUIREMENTS.md` (FR-01–35, BR-01–20, NFR-01–18) · `DESIGN.md` (D1–D15) · `TEST-DATA.md` (E01–E90, T1–T17) [SPEC บรรทัด 5] · schema อ้าง "DESIGN.md §4 (ERD 17 ตาราง)" | ไม่มีไฟล์เหล่านี้ใน repo · DB จริงมี 19 ตาราง | [source `db/init/01-schema.sql:1`] · [DB `\dt` 19 rows] · `git ls-files` ไม่พบไฟล์ทั้ง 3 | ร้านมีเอกสาร 3 ไฟล์นี้ไหม ขอสำเนาได้ไหม (เป็นแหล่งของรหัส BR/FR/D ที่โค้ดอ้าง) |
| G10 | §6 ระบุ `GET /api/services` `/api/therapists` `/api/hotels` `/api/me` `/api/me/bookings` `/api/wallet` `/api/quiz` เป็น API ของเว็บ [SPEC §6 บรรทัด 209-218, 226] | หน้าเว็บไม่เรียก route เหล่านี้ (หน้า server component เรียก lib ตรง) · ไม่มีผู้เรียกในเว็บ | [source `SYSTEM-MAP.md` §2 ตาราง route #6–8 #13–15 #23 · grep `fetch(` ใน `web/components` ไม่พบ] | มีระบบอื่นเรียก API เหล่านี้อยู่ไหม (แอป, LINE OA, สคริปต์) · ถ้าจะแก้กฎต้องรักษา response เดิมไหม |

รวม **13 แถว** (กฎ 6 · ความปลอดภัย/ตั้งค่า 2 · เอกสาร 5) · ทุกแถวเป็นคำถาม ยังไม่มีคำตอบ
