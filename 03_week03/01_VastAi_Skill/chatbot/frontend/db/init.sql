-- สบายใจ นวดแผนไทย : schema + ข้อมูลตัวอย่าง
-- ไฟล์นี้ถูกรันอัตโนมัติครั้งแรกที่สร้าง volume ของ Postgres
-- (ถ้าแก้ไฟล์นี้ ต้องลบ volume ก่อน: docker compose down -v)

SET client_encoding = 'UTF8';

CREATE TABLE IF NOT EXISTS services (
  id             SERIAL PRIMARY KEY,
  name_th        TEXT    NOT NULL UNIQUE,
  duration_min   INTEGER NOT NULL,
  price_thb      INTEGER NOT NULL,
  description_th TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS shop_info (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
  id            SERIAL PRIMARY KEY,
  customer_name TEXT        NOT NULL,
  phone         TEXT        NOT NULL,
  service_id    INTEGER     REFERENCES services(id),
  booking_time  TIMESTAMP   NOT NULL,
  status        TEXT        NOT NULL DEFAULT 'pending',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chat_messages (
  id         SERIAL PRIMARY KEY,
  session_id TEXT        NOT NULL,
  role       TEXT        NOT NULL CHECK (role IN ('user','assistant','system')),
  content    TEXT        NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, id);

INSERT INTO services (name_th, duration_min, price_thb, description_th) VALUES
  ('นวดไทยแผนโบราณ',        60, 350, 'นวดกดจุดและยืดเส้นตามแบบแผนไทยดั้งเดิม ช่วยคลายกล้ามเนื้อและเพิ่มการไหลเวียนโลหิต'),
  ('นวดไทยแผนโบราณ 2 ชั่วโมง', 120, 600, 'นวดไทยเต็มรูปแบบทั่วร่างกาย เหมาะกับผู้ที่ปวดเมื่อยสะสมหรือต้องการผ่อนคลายเต็มที่'),
  ('นวดน้ำมันอโรมา',          60, 600, 'นวดด้วยน้ำมันหอมระเหย (ลาเวนเดอร์ / ตะไคร้ / มะลิ) ช่วยผ่อนคลายความเครียด หลับสบาย'),
  ('นวดเท้าสะท้อนจุด',         45, 300, 'กดจุดสะท้อนที่ฝ่าเท้า ช่วยบรรเทาอาการเมื่อยล้าจากการยืนหรือเดินนาน'),
  ('นวดคอบ่าไหล่',            30, 250, 'เน้นคอ บ่า ไหล่ เหมาะกับคนทำงานออฟฟิศ นั่งหน้าคอมพิวเตอร์นาน'),
  ('นวดแก้ปวดหลัง',           60, 450, 'เน้นกล้ามเนื้อหลังส่วนบนและส่วนล่าง ผสมการกดจุดและยืดเส้น บรรเทาอาการปวดหลัง'),
  ('ประคบสมุนไพร',            60, 500, 'นวดไทยร่วมกับลูกประคบสมุนไพรอุ่น (ไพล ขมิ้น ตะไคร้) ลดการอักเสบและอาการตึง'),
  ('นวดหน้าและศีรษะ',          30, 300, 'นวดผ่อนคลายใบหน้า ขมับ และหนังศีรษะ ช่วยลดอาการปวดศีรษะจากความเครียด')
ON CONFLICT (name_th) DO NOTHING;

INSERT INTO shop_info (key, value) VALUES
  ('shop_name',  'สบายใจ นวดแผนไทย (Sabaijai Thai Massage)'),
  ('hours',      'เปิดทุกวัน 10:00 - 22:00 น. (รับลูกค้ารอบสุดท้าย 21:00 น.)'),
  ('address',    '99/9 ถนนนิมมานเหมินท์ ซอย 7 ต.สุเทพ อ.เมือง จ.เชียงใหม่ 50200'),
  ('phone',      '053-123-456 / Line: @sabaijai'),
  ('promotions', 'ลด 10% ทุกบริการ วันจันทร์-พฤหัสบดี ก่อน 14:00 น. | ซื้อแพ็กเกจ 5 ครั้ง แถมนวดเท้าฟรี 1 ครั้ง | นักศึกษาลด 15% เมื่อแสดงบัตรนักศึกษา'),
  ('policies',   'กรุณามาก่อนเวลานัด 10 นาที | ยกเลิกหรือเลื่อนนัดได้ล่วงหน้าอย่างน้อย 3 ชั่วโมง | ไม่แนะนำให้นวดสำหรับผู้ตั้งครรภ์ไตรมาสแรกหรือผู้มีไข้ | ชำระเงินสด โอนพร้อมเพย์ หรือบัตรเครดิต'),
  ('parking',    'มีที่จอดรถหน้าร้าน 4 คัน')
ON CONFLICT (key) DO NOTHING;
