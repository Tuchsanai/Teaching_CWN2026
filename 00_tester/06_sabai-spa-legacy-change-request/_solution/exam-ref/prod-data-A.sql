-- EXREF · ฐาน "ใช้งานจริง" ชุด A = seed + ลูกค้าใหม่ 1 คน + นัดใหม่ 5 นัด (มีนัด S03 วันที่ 20 ต.ค.)
-- ใช้เป็น db/init/03-prod-data.sql ต่อจาก 01-schema.sql + 02-seed.sql ของ EX0
INSERT INTO customer (id, name, phone, email, birth_date, lang, lifetime_spend, points_balance, role, created_on) VALUES
 (10, 'คุณใหม่ ใช้งานจริง', '081-222-0010', 'prod10@sabai.test', '1991-06-01', 'th', 2400.00, 0, 'customer', '2026-10-08');
INSERT INTO booking (id, code, customer_id, guest_name, guest_phone, contact_name, contact_phone, service_id, room_id, course_purchase_id,
  booking_type, party_size, start_at, end_at, status, gross_amount, discount_kind, discount_pct, discount_amount,
  points_redeemed, points_discount, distance_km, vehicles, transport_fee, total_amount, giftcard_paid, other_paid, points_earned, created_at) VALUES
 (14, 'B14', 10, NULL, NULL, 'คุณใหม่ ใช้งานจริง', '081-222-0010', 3, NULL, NULL, 'single', 1, '2026-10-20 10:00+07', '2026-10-20 11:00+07', 'confirmed', 1200, 'none', 0, 0, 0, 0, NULL, 0, 0, 1200, 0, 1200, 0, '2026-10-08 09:00+07'),
 (15, 'B15', NULL, 'คุณพร', '081-000-0015', 'คุณพร', '081-000-0015', 1, NULL, NULL, 'single', 1, '2026-10-18 11:00+07', '2026-10-18 12:00+07', 'confirmed', 1000, 'none', 0, 0, 0, 0, NULL, 0, 0, 1000, 0, 1000, 0, '2026-10-08 10:00+07'),
 (16, 'B16', 3, NULL, NULL, 'คุณเมย์', '081-111-0003', 5, NULL, NULL, 'single', 1, '2026-10-19 13:00+07', '2026-10-19 14:00+07', 'confirmed', 800, 'none', 0, 0, 0, 0, NULL, 0, 0, 800, 0, 800, 0, '2026-10-09 11:00+07'),
 (17, 'B17', 10, NULL, NULL, 'คุณใหม่ ใช้งานจริง', '081-222-0010', 2, NULL, NULL, 'single', 1, '2026-10-21 15:00+07', '2026-10-21 16:30+07', 'confirmed', 1400, 'none', 0, 0, 0, 0, NULL, 0, 0, 1400, 0, 1400, 0, '2026-10-09 12:00+07'),
 (18, 'B18', 7, NULL, NULL, 'คุณกานต์', '081-111-0007', 3, NULL, NULL, 'single', 1, '2026-10-03 10:00+07', '2026-10-03 11:00+07', 'completed', 1200, 'tier', 5, 60, 0, 0, NULL, 0, 0, 1140, 0, 1140, 11, '2026-09-28 12:00+07');
INSERT INTO booking_slot (id, booking_id, therapist_id, period, active) VALUES
 (19, 14, 1, '[2026-10-20 10:00+07, 2026-10-20 11:00+07)', TRUE),
 (20, 15, 2, '[2026-10-18 11:00+07, 2026-10-18 12:00+07)', TRUE),
 (21, 16, 4, '[2026-10-19 13:00+07, 2026-10-19 14:00+07)', TRUE),
 (22, 17, 5, '[2026-10-21 15:00+07, 2026-10-21 16:30+07)', TRUE),
 (23, 18, 6, '[2026-10-03 10:00+07, 2026-10-03 11:00+07)', TRUE);
SELECT setval(pg_get_serial_sequence('customer', 'id'), 10);
SELECT setval(pg_get_serial_sequence('booking', 'id'), 18);
SELECT setval(pg_get_serial_sequence('booking_slot', 'id'), 23);
