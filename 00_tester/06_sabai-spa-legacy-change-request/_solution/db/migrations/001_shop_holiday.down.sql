-- CR-04 migration 001 (ถอยกลับ) · ลบตาราง shop_holiday
-- ⚠️ ข้อมูลที่หาย: แถววันหยุดทั้งหมดใน shop_holiday (3 วันของ CR-04 + ที่เพิ่มภายหลัง) · ลูกค้า/นัด/คอร์ส ไม่หาย
-- ลำดับถอย: ถอยเว็บเป็น image sabai06-web:before-cr04 ก่อน แล้วค่อยรันไฟล์นี้
--   (เว็บรุ่น CR-04 อ่านตารางนี้ และ reset จะ TRUNCATE ตารางนี้ → ถ้าลบก่อน จอง/reset จะ 500)
-- รัน: docker cp db\migrations\001_shop_holiday.down.sql sabai06-db:/tmp/001down.sql
--      docker exec sabai06-db psql -U sabai -d sabai -v ON_ERROR_STOP=1 -f /tmp/001down.sql
BEGIN;
DROP TABLE IF EXISTS shop_holiday;
COMMIT;
