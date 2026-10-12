# MIGRATION · EX-A6 ปิด S03 ชั่วคราว (service.active)

| ขั้น | คำสั่ง (PowerShell ที่โฟลเดอร์ระบบ) |
|---|---|
| สำรอง | `docker exec sabai06x-db pg_dump -U sabai sabai > backup-before-001.sql` |
| ขาขึ้น (รันซ้ำได้) | `Get-Content db/migrations/001_service_active.sql -Raw \| docker exec -i sabai06x-db psql -U sabai -d sabai -v ON_ERROR_STOP=1` |
| เปิดเว็บใหม่ | `docker compose -f web/compose.yaml up -d --build --wait` |
| ถอยกลับ | `Get-Content db/migrations/001_service_active.down.sql -Raw \| docker exec -i sabai06x-db psql -U sabai -d sabai -v ON_ERROR_STOP=1` แล้ว build เว็บเวอร์ชันก่อนหน้า |
| ข้อมูลที่หายถ้าถอย | สถานะ active ของทุกบริการ (ถ้าร้านปิดบริการอื่นไว้ จะกลับมาเปิดทั้งหมด) |

ติดตั้งใหม่/reset: `db/init/01-schema.sql` มีคอลัมน์ `active` และ `02-seed.sql` ตั้ง S03 = false
