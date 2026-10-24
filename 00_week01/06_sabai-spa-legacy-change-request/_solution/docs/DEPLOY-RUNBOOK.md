# DEPLOY-RUNBOOK · สบายใจ สปา · ขึ้นระบบ CR-01–05

> ทุกคำสั่งรันด้วย **PowerShell จากโฟลเดอร์บท** · ห้าม `docker compose down -v` · ห้ามลบ volume `sabai06-pgdata` (ข้อมูลลูกค้าจริง) · ห้าม pipe ไฟล์ SQL ภาษาไทยผ่าน PowerShell (ใช้ `docker cp` + `psql -f`)
> พอร์ตไม่ใช่ค่าเริ่ม: ตั้ง `$env:WEB_PORT` `$env:DB_PORT` ก่อน `up` และ `$env:BASE_URL="http://localhost:<พอร์ต>"` ก่อน `node tests/smoke.mjs` · รายละเอียด migration: `docs/MIGRATION-RUNBOOK.md`
> **เครื่องจริงห้าม `/api/test/reset`** (ล้างข้อมูลทดสอบ) · ตั้ง `ALLOW_TEST_RESET=0` ในเครื่องจริง · เวลาในเอกสารนี้วัดจากการซ้อมบนเครื่องทดสอบ 2026-10-12

## สิ่งที่เปลี่ยนในรอบนี้

| CR | เปลี่ยน DB? | ถอยกลับ |
|---|---|---|
| CR-01 เลื่อนนัด | ไม่ (ใช้ตารางเดิม) | image เดิม |
| CR-02 ส่วนลดกลุ่มขั้นบันได (มีผล 1 พ.ย. 2026) | ไม่ | image เดิม |
| CR-03 กันจองซ้ำคนเดียวกัน | ไม่ | image เดิม |
| CR-04 วันหยุดร้าน | **ใช่** · migration `001_shop_holiday` (ตารางใหม่ 1 ตาราง + 3 แถว) | image เดิม + `001_shop_holiday.down.sql` |
| CR-05 รายงานยอด + CSV | ไม่ | image เดิม |

## ลำดับวันขึ้นระบบ (ต้องตามลำดับ)

| # | ขั้น | คำสั่ง | ผลที่ต้องเห็น | เวลาซ้อม |
|---|---|---|---|---|
| 0 | ตรวจระบบเดิมก่อนเริ่ม | `Invoke-RestMethod http://localhost:4000/api/health` | `ok True` `db True` | < 1 วิ |
| 1 | **สำรอง** | `New-Item -ItemType Directory -Force backups \| Out-Null` · `docker exec sabai06-db pg_dump -U sabai -d sabai -f /tmp/before-release.sql` · `docker cp sabai06-db:/tmp/before-release.sql backups\before-release.sql` | exit 0 · ไฟล์ ~53 KB (ซ้อมได้ 53,469 ไบต์) | 0.5 วิ |
| 2 | นับข้อมูลก่อน | `docker exec sabai06-db psql -U sabai -d sabai -At -c "SELECT (SELECT count(*) FROM booking), (SELECT count(*) FROM customer)"` | จดตัวเลขไว้เทียบ | < 1 วิ |
| 3 | **tag image เดิม** | `docker tag sabai06-web:latest sabai06-web:before-release` | `docker images sabai06-web` เห็น tag `before-release` | < 1 วิ |
| 4 | **รัน migration** (ก่อน build เว็บ) | `docker cp db\migrations\001_shop_holiday.sql sabai06-db:/tmp/001.sql` · `docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001.sql` · `$LASTEXITCODE` | `CREATE TABLE` · `INSERT 0 3` · exit 0 (รันซ้ำได้: `INSERT 0 0`) · นับ booking/customer เท่าขั้น 2 | 0.3–1.3 วิ |
| 5 | **build/up เว็บ** | `docker compose -f web/compose.yaml up -d --build --wait` | container `sabai06-web` healthy | 39–41 วิ (ซ้อม 3 ครั้ง) |
| 6 | **smoke test** | `node tests/smoke.mjs` | ตาราง 7 ข้อ "ผ่าน" ทุกข้อ · `สรุป 7/7 ผ่าน` · `$LASTEXITCODE` = 0 | 0.2 วิ |
| 7 | ตรวจด้วยตาร้าน | เปิด `/book` เลือก 23 ต.ค. → ขึ้น "วันนี้ร้านหยุด" · เจ้าของเข้า `/admin/report` ได้ | ตาม `UAT-CHECKLIST.md` | ~5 นาที |

ผลที่ต้องเห็นจาก smoke (ขั้น 6):

```text
| 1 health db:true | ผ่าน | 200 db=true |
| 2 GET /api/services 200 | ผ่าน | 200 |
| 3 /api/holidays มีวันหยุดที่ร้านแจ้ง (CR-04) | ผ่าน | 200 พบ 3 วัน |
| 4 หน้า /book 200 | ผ่าน | 200 |
| 5 CR-01 GET reschedule-slots ไม่ล็อกอิน = 401 | ผ่าน | 401 |
| 6 CR-01 POST reschedule ไม่ล็อกอิน = 401 | ผ่าน | 401 |
| 7 CR-05 GET /api/admin/report ไม่ล็อกอิน = 401 | ผ่าน | 401 |
สรุป 7/7 ผ่าน
```

smoke อ่านอย่างเดียว (ไม่ reset ไม่จอง ไม่ล็อกอิน) จึงรันบนเครื่องจริงได้ · เว็บล่มแล้ว smoke ต้องได้ `0/7` และ exit 1 (ซ้อมแล้ว: ทุกข้อ `ECONNREFUSED`)

## เงื่อนไขที่ต้องถอย

ถอยทันทีเมื่อข้อใดข้อหนึ่งเกิด (ภายในวันขึ้นระบบ):

1. ขั้น 4 migration exit ≠ 0 → หยุด **ไม่ต้อง build เว็บ** (transaction ถูกยกเลิกทั้งก้อน ระบบเดิมยังทำงาน) · ถ้าตารางถูกสร้างครึ่งทางให้รัน down.sql
2. ขั้น 5 build ล้มหรือ container ไม่ healthy ภายใน 2 นาที
3. ขั้น 6 smoke exit 1 (ข้อใดข้อหนึ่ง "ไม่ผ่าน") และแก้ไม่ได้ภายใน 15 นาที
4. หลังเปิดใช้: ลูกค้าจองไม่ได้ / ยอดเงินผิด / หน้าเว็บ 500 ที่ไม่เคยเกิด

ไม่ต้องถอย: smoke ผ่านแต่มีเรื่องใน "เรื่องที่ยังไม่ได้แก้" ของ `RELEASE-NOTES.md` (เป็นของเดิมก่อนรอบนี้)

## ขั้นถอย (เว็บก่อน แล้วค่อย DB)

| # | ขั้น | คำสั่ง | ผลที่ต้องเห็น | เวลาซ้อม |
|---|---|---|---|---|
| R1 | เว็บกลับ image เดิม | `docker tag sabai06-web:before-release sabai06-web:latest` · `docker compose -f web/compose.yaml up -d --no-build --force-recreate --wait` | healthy · `/api/health` `db True` | ไม่ได้วัดในการซ้อมนี้ (ซ้อม stop/start container เดิม: health ผ่านในรอบตรวจแรก) |
| R2 | DB ถอย migration (เฉพาะเมื่อจำเป็น · เว็บเดิมไม่ต้องใช้ตารางนี้) | `docker cp db\migrations\001_shop_holiday.down.sql sabai06-db:/tmp/001down.sql` · `docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001down.sql` | `DROP TABLE` · exit 0 · `SELECT to_regclass('shop_holiday')` ว่าง | 1.1 วิ |
| R3 | ตรวจ | `docker exec sabai06-db psql -U sabai -d sabai -At -c "SELECT count(*) FROM booking"` · `Invoke-RestMethod http://localhost:4000/api/health` | นัดเท่าเดิม (หรือมากขึ้นจากที่ลูกค้าจองหลังขึ้นระบบ) · `db True` | < 1 วิ |
| R4 | ขึ้นใหม่ภายหลัง | รันขั้น 4–6 ซ้ำ | `INSERT 0 3` · smoke 7/7 | 1.3 วิ + build |

**ห้ามใช้ `backups\before-release.sql` เป็นวิธีถอยปกติ** · ย้อนจากไฟล์สำรอง = นัด/ลูกค้า/การเลื่อนนัดที่เกิดหลังขึ้นระบบหายหมด → ใช้เมื่อข้อมูลเสียหายเท่านั้น

### ข้อมูลที่จะหายถ้าถอย

| ถอยแบบ | หาย | ไม่หาย |
|---|---|---|
| R1 เว็บอย่างเดียว | ไม่มีข้อมูลหาย · ความสามารถใหม่หายจากหน้าเว็บ (เลื่อนนัดเอง · ปิดจองวันหยุด · กันจองซ้ำ · ส่วนลดขั้นบันได · รายงาน/CSV) | ทุกตาราง |
| R1 + R2 down.sql | ทุกแถวใน `shop_holiday` (3 วันหยุดของ CR-04 + วันที่ร้านเพิ่มภายหลังถ้ามี) | ลูกค้า นัด (รวมนัดใหม่หลังขึ้นระบบ) คอร์ส บัตรของขวัญ แต้ม · นัดที่ลูกค้าเลื่อนผ่าน CR-01 ไปแล้วคงเวลาใหม่ไว้ |
| ย้อนจาก backup (ทางสุดท้าย) | ทุกอย่างที่เกิดหลังเวลาสำรองในขั้น 1 | ข้อมูลก่อนขั้น 1 |

## ผลซ้อมถอยกลับ 2026-10-12 (ฐานที่มีข้อมูล · เว็บรุ่น CR-01–05 `ef47d72` · พอร์ตซ้อม WEB 4100 DB 5533)

| ขั้น | คำสั่ง | ผล | เวลา |
|---|---|---|---|
| 0 smoke ก่อนเริ่ม | `node tests/smoke.mjs` | 7/7 ผ่าน · exit 0 | 0.2 วิ |
| 1 สำรอง | `pg_dump` → `docker cp` | `backups\before-rollback.sql` 53,469 ไบต์ · exit 0 | 0.5 วิ |
| 2 reset + จองใหม่ | reset · node จอง (ไม่ล็อกอิน S05 2026-10-21 11:00) | now `2026-10-10T10:00:00+07:00` · **B14** 201 ฿800 confirmed · booking 14 แถว | 0.9 วิ |
| 3 หยุดเว็บ + smoke | `docker compose -f web/compose.yaml stop` · smoke | `Exited (0)` · smoke **0/7** `ECONNREFUSED` · **exit 1** | 1.0 วิ |
| 4 ถอย migration | `001_shop_holiday.down.sql` | `DROP TABLE` exit 0 · `to_regclass` ว่าง · **B14 confirmed ยังอยู่** · booking 14 | 1.1 วิ |
| 5 ขึ้น migration อีกครั้ง | `001_shop_holiday.sql` | `CREATE TABLE` `INSERT 0 3` exit 0 · 3 แถว (23 ต.ค. · 5 ธ.ค. · 31 ธ.ค.) ชื่อไทยตรง · **B14 ยังอยู่** · booking 14 | 1.3 วิ |
| 5b (เพิ่มเติม) DB `down` ไม่ใส่ `-v` → `up` | `docker compose -f db/compose.yaml down` · `up -d --wait` | volume `sabai06-pgdata` ยังอยู่ · **B14 ยังอยู่** · holiday 3 · booking 14 | 7.8 วิ |
| 6 เปิดเว็บ | `docker compose -f web/compose.yaml start` · health · smoke · `node tests/cr04.mjs` | health `db true` รอบแรก · smoke 7/7 exit 0 · CR-04 **14/14** (3.0 วิ) | 4.4 วิ |
