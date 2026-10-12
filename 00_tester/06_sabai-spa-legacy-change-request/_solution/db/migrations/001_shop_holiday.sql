-- CR-04 วันหยุดร้าน · migration 001 (ขึ้น) · รันกับฐานที่มีข้อมูลอยู่แล้วได้ และรันซ้ำได้ (idempotent)
-- รัน (PowerShell จากโฟลเดอร์บท · ห้าม pipe ไฟล์ผ่าน PowerShell):
--   docker cp db\migrations\001_shop_holiday.sql sabai06-db:/tmp/001.sql
--   docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001.sql
-- เพิ่มตารางใหม่อย่างเดียว ไม่แตะตาราง/ข้อมูลเดิม · ถอยกลับ: 001_shop_holiday.down.sql
-- โครงตารางต้องตรงกับ db/init/01-schema.sql (เครื่องติดตั้งใหม่) · แถวตรงกับ db/init/02-seed.sql
BEGIN;

CREATE TABLE IF NOT EXISTS shop_holiday (
  holiday_date DATE PRIMARY KEY,
  name_th      VARCHAR(100) NOT NULL,
  name_en      VARCHAR(100) NOT NULL,
  name_zh      VARCHAR(100) NOT NULL
);

-- วันหยุดปี 2569 ตาม CR-04 + CR-04-ANSWERS ② (มีอยู่แล้ว = ข้าม ไม่ทับชื่อที่ร้านแก้เอง)
INSERT INTO shop_holiday (holiday_date, name_th, name_en, name_zh) VALUES
 ('2026-10-23', 'วันปิยมหาราช',   'Chulalongkorn Day',     '五世王纪念日'),
 ('2026-12-05', 'วันพ่อแห่งชาติ', 'National Father''s Day', '父亲节'),
 ('2026-12-31', 'วันสิ้นปี',       'New Year''s Eve',       '新年前夕')
ON CONFLICT (holiday_date) DO NOTHING;

COMMIT;
