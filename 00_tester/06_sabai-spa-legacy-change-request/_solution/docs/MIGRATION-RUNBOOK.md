# MIGRATION-RUNBOOK · สบายใจ สปา

> ทุกคำสั่งรันด้วย **PowerShell จากโฟลเดอร์บท** · ห้าม `docker compose down -v` · ห้ามลบ volume `sabai06-pgdata` · ห้าม pipe ไฟล์ SQL ภาษาไทยผ่าน PowerShell (ใช้ `docker cp` + `psql -f` เท่านั้น)
> พอร์ตไม่ใช่ค่าเริ่ม: ตั้ง `$env:WEB_PORT` `$env:DB_PORT` ก่อน `up` และแทน `4000` ในคำสั่งด้านล่าง

## 001 · `shop_holiday` วันหยุดร้าน (CR-04)

| รายการ | ค่า |
|---|---|
| ไฟล์ขึ้น | `db/migrations/001_shop_holiday.sql` (`CREATE TABLE IF NOT EXISTS` + `INSERT … ON CONFLICT DO NOTHING` ใน transaction เดียว · รันซ้ำได้) |
| ไฟล์ถอย | `db/migrations/001_shop_holiday.down.sql` (`DROP TABLE IF EXISTS shop_holiday`) |
| ผลกับข้อมูลเดิม | เพิ่มตารางใหม่ 1 ตาราง + 3 แถว · ไม่แตะตาราง/แถวเดิม · เว็บรุ่นก่อน CR-04 ทำงานต่อได้ระหว่างนั้น (ไม่รู้จักตารางนี้ · reset รุ่นเก่าไม่ล้างตารางนี้) |
| เครื่องติดตั้งใหม่ | ไม่ต้องรัน migration: `db/init/01-schema.sql` + `db/init/02-seed.sql` มีตารางและ 3 แถวแล้ว (รันเองตอน volume ว่าง) |
| image ถอยกลับ | `sabai06-web:before-cr04` |

### ลำดับ deploy (ต้องตามนี้)

**migration ก่อน แล้วค่อย rebuild เว็บ** · ถ้าเว็บรุ่นใหม่ขึ้นก่อน ตารางยังไม่มี → `/api/slots` `/api/price` `/api/bookings` `/api/test/reset` ตอบ 500

1. สำรอง (ไม่ commit · `backups/` อยู่ใน `.git/info/exclude`)
   ```powershell
   New-Item -ItemType Directory -Force backups | Out-Null
   docker exec sabai06-db pg_dump -U sabai -d sabai -f /tmp/before-cr04.sql
   docker cp sabai06-db:/tmp/before-cr04.sql backups\before-cr04.sql
   ```
2. นับก่อน: `docker exec sabai06-db psql -U sabai -d sabai -c "SELECT (SELECT count(*) FROM booking) b, (SELECT count(*) FROM customer) c"`
3. รัน migration (ซ้ำได้ · ครั้งที่ 2 ขึ้น NOTICE `already exists, skipping` และ `INSERT 0 0` = ปกติ · PowerShell อาจห่อ NOTICE เป็นตัวแดง `NativeCommandError` ให้ดู exit code)
   ```powershell
   docker cp db\migrations\001_shop_holiday.sql sabai06-db:/tmp/001.sql
   docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001.sql
   $LASTEXITCODE   # ต้อง 0
   ```
4. ตรวจด้วย SQL (ไม่ตัดสินจากตัวอักษรไทยบนจอ) · เขียนลงไฟล์ .sql แล้ว `docker cp` + `psql -f`:
   ```sql
   SELECT count(*) FROM shop_holiday;                                              -- 3
   SELECT holiday_date, name_th = 'วันปิยมหาราช' AS th_ok FROM shop_holiday
    WHERE holiday_date = '2026-10-23';                                              -- t
   SELECT (SELECT count(*) FROM booking) b, (SELECT count(*) FROM customer) c;      -- เท่าข้อ 2
   ```
5. เก็บ image เดิม แล้ว rebuild เว็บ (~1 นาที)
   ```powershell
   docker tag sabai06-web:latest sabai06-web:before-cr04
   docker compose -f web/compose.yaml up -d --build --wait
   Invoke-RestMethod http://localhost:4000/api/health            # ok True · db True
   Invoke-RestMethod http://localhost:4000/api/holidays          # 3 แถว
   ```
6. ทดสอบ: `node tests/cr04.mjs` (14/14) · reset 2 ครั้งได้ 200 · ชั้น 1 + ชั้น 2 ตาม `CLAUDE.md`

### ถอยกลับ (ลำดับกลับกัน: เว็บก่อน แล้วค่อย DB)

1. เว็บกลับรุ่นเดิม
   ```powershell
   docker tag sabai06-web:before-cr04 sabai06-web:latest
   docker compose -f web/compose.yaml up -d --no-build --force-recreate --wait
   ```
   (หรือ `git revert <commit CR-04>` แล้ว `up -d --build --wait`)
2. DB (ถ้าต้องลบตารางจริง · ไม่จำเป็นต่อการให้เว็บเดิมทำงาน)
   ```powershell
   docker cp db\migrations\001_shop_holiday.down.sql sabai06-db:/tmp/001down.sql
   docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001down.sql
   ```
3. ตรวจ: `/api/health` · `/api/holidays` → 404 · `\dt shop_holiday` ไม่พบ · นับ booking/customer เท่าก่อนถอย · check-rules 90/90

**ข้อมูลที่หายเมื่อถอย DB:** ทุกแถวใน `shop_holiday` (3 วันของ CR-04 + วันที่ร้านเพิ่มเองในอนาคตถ้ามีส่วน ข) · ลูกค้า นัด คอร์ส บัตรของขวัญ แต้ม **ไม่หาย** · นัดที่ลูกค้าจองหลัง deploy ยังอยู่ (ถ้าย้อนด้วย `backups/before-cr04.sql` แทน down.sql จะ**ทำนัดหลัง deploy หาย** → ใช้เป็นทางสุดท้ายเท่านั้น)

### ผลซ้อม 2026-10-12 (ฐานที่มีข้อมูล · เว็บรุ่นเดิม `fe187aa` ยังรัน)

| ขั้น | ผล |
|---|---|
| สำรอง | `backups/before-cr04.sql` 52,535 ไบต์ |
| นัดใหม่ก่อน migrate | reset → จอง B14 (ไม่ล็อกอิน S01 2026-10-20 14:00) · booking 14 แถว |
| migrate ครั้งที่ 1 | `CREATE TABLE` · `INSERT 0 3` · exit 0 · 0.28 วิ |
| migrate ครั้งที่ 2 | NOTICE `already exists, skipping` · `INSERT 0 0` · exit 0 · 0.27 วิ |
| ตรวจ | `count = 3` · `th_ok = t` · `zh_ok = t` · B14 ยังอยู่ (confirmed) · booking 14 · customer 9 |
| เว็บรุ่นเดิมหลัง migrate | `/api/test/reset` 200 · `shop_holiday` ยัง 3 แถว |
| rebuild เว็บ | 41 วิ · health ok · reset ×2 → 200 · 200 |
| ติดตั้งใหม่ (`sabai06-fresh`) | 20 ตาราง · `shop_holiday` 3 แถว · `th_ok = t` |
