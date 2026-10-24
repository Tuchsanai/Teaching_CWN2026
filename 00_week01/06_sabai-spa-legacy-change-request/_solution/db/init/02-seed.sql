-- สบายใจ สปา · seed = TEST-DATA.md ทุกค่า
-- ไฟล์นี้เป็นแหล่งเดียวของ seed: db ใช้ตอน init และ web ใช้ซ้ำตอน POST /api/test/reset (หลัง TRUNCATE)
-- เวลาทุกค่าระบุ +07:00 (Asia/Bangkok) · ไม่มีคำสั่ง BEGIN/COMMIT ในไฟล์ (ผู้เรียกคุม transaction เอง)

-- ── ผู้ใช้ U01–U08 + เจ้าของร้าน (รหัสผ่านเก็บเป็น bcrypt) ──────────────────────
INSERT INTO customer (id, name, phone, email, line_id, birth_date, lang, lifetime_spend, points_balance, password_hash, role, created_on) VALUES
 (1, 'คุณนิดา',     '081-111-0001', 'nida@sabai.test',  'nida.line',  '1990-03-08', 'th', 12400.00,  99, '$2b$10$UjQAzM1g6o3y41YW6IrcpeDEyTvRQ2UA7VABSn6Z0GvglVm2h7Y9e', 'customer', '2026-01-15'),
 (2, 'คุณต้น',      '081-111-0002', 'ton@sabai.test',   'ton.line',   '1992-10-15', 'th', 30000.00,   0, '$2b$10$5Rf0kWb0SVGJqz6PgmqDaOZGgJbFZabLJufK2WDHlBHeVvzm4awrC', 'customer', '2025-06-01'),
 (3, 'คุณเมย์',     '081-111-0003', 'may@sabai.test',   NULL,         '1996-05-20', 'th',     0.00,   0, '$2b$10$3lt1L0gDdUCNDGH9K/eZEeoBGR2zp8/3/uZd0aAsWybmN.C3lkJA2', 'customer', '2026-10-09'),
 (4, 'คุณฝน',       '081-111-0004', 'fon@sabai.test',   'fon.line',   '1993-02-14', 'th',  9999.00, 250, '$2b$10$JQq794CzdkUgo0nZMduN1eKq5uKf9Rrfz7RDjmd9ZO4NYQfeb0e7a', 'customer', '2025-11-20'),
 (5, 'น้องแพร',     '081-111-0005', 'prae@sabai.test',  'prae.line',  '2001-10-03', 'th', 29999.00, 100, '$2b$10$FroQ3z4eFYWVVdtlnPO9Cu68d7DkTKs1PPVuNZ2Y.bhsZ4.OTf/za', 'customer', '2025-02-10'),
 (6, 'คุณวิภา',     '081-111-0006', 'vipa@sabai.test',  'vipa.line',  '1985-01-25', 'th', 45000.00, 199, '$2b$10$ozjbDSgDq8ZBZuzpjwR.pO670ZgyAB0w/WrSnV48JV8.ktlABK0hy', 'customer', '2024-12-01'),
 (7, 'คุณกานต์',    '081-111-0007', 'kan@sabai.test',   'kan.line',   '1988-07-07', 'th', 10000.00,   0, '$2b$10$MAl1Rp4j.D4ZhNEcuzzwHOgl9mFxGVfESYej84u4.lwRJF4blt/ge', 'customer', '2026-04-20'),
 (8, 'Mr. Li Wei',  '+86-138-0000-0008', 'liwei@sabai.test', NULL,  '1990-01-12', 'zh',     0.00,   0, '$2b$10$qPzycsoC9PWL8Eck1Iqru.t2J/yo0zgebkveM6qbou1R24Hy7K6Hu', 'customer', '2026-10-01'),
 (9, 'คุณจันทร์ (เจ้าของร้าน)', '02-123-4567', 'owner@sabai.test', NULL, NULL, 'th', 0.00, 0, '$2b$10$WyAoUFf8i3.mw/NDgALy7u47cDNpGd/jmoGObHXt88STMDfThe3bW', 'owner', '2024-01-01');

-- ── บริการ S01–S07 · แพ็กเกจ P01 · คอร์ส K01 ─────────────────────────────────
INSERT INTO service (id, code, name_th, name_en, name_zh, kind, duration_min, price, includes_transport) VALUES
 (1, 'S01', 'นวดไทย 60 นาที',     'Thai Massage 60',        '泰式按摩 60分钟', 'single',  60,  1000.00, FALSE),
 (2, 'S02', 'นวดไทย 90 นาที',     'Thai Massage 90',        '泰式按摩 90分钟', 'single',  90,  1400.00, FALSE),
 (3, 'S03', 'ประคบสมุนไพร',       'Herbal Compress',        '草药热敷',        'single',  60,  1200.00, FALSE),
 (4, 'S04', 'นวดน้ำมันอโรมา',     'Aroma Oil Massage',      '香薰精油按摩',    'single',  90,  2000.00, FALSE),
 (5, 'S05', 'นวดเท้า',            'Foot Massage',           '足部按摩',        'single',  60,   800.00, FALSE),
 (6, 'S06', 'ขัดผิวสมุนไพร',      'Herbal Body Scrub',      '草药身体磨砂',    'single',  60,  1500.00, FALSE),
 (7, 'S07', 'ทรีตเมนต์หน้า',      'Herbal Facial',          '草药面部护理',    'single',  60,  1800.00, FALSE),
 (8, 'P01', 'แพ็กเกจ Bangkok Relax', 'Bangkok Relax Package', '曼谷放松套餐',  'package', 120, 2900.00, TRUE),
 (9, 'K01', 'คอร์สกระชับสัดส่วน 10 แถม 1', 'Body Contouring Course', '塑形疗程', 'course', 60, 15000.00, FALSE);

-- ── สมุนไพร (FR-31 ห้ามว่าง) ────────────────────────────────────────────────
INSERT INTO herb (id, name_th, name_en, name_zh) VALUES
 (1,  'ไพล',           'Plai (Thai ginger)', '泰国姜'),
 (2,  'ตะไคร้',        'Lemongrass',         '香茅'),
 (3,  'ขมิ้น',         'Turmeric',           '姜黄'),
 (4,  'มะกรูด',        'Kaffir lime',        '泰国青柠'),
 (5,  'มะลิ',          'Jasmine',            '茉莉'),
 (6,  'ตะไคร้หอม',     'Citronella',         '亚香茅'),
 (7,  'การบูร',        'Camphor',            '樟脑'),
 (8,  'เกลือสมุนไพร',  'Herbal salt',        '草本盐'),
 (9,  'มะขาม',         'Tamarind',           '罗望子'),
 (10, 'น้ำผึ้ง',       'Honey',              '蜂蜜'),
 (11, 'ว่านหางจระเข้', 'Aloe vera',          '芦荟'),
 (12, 'ทานาคา',        'Thanaka',            '黄香楝'),
 (13, 'ขิง',           'Ginger',             '生姜'),
 (14, 'พริกไทยดำ',     'Black pepper',       '黑胡椒');

INSERT INTO service_herb (service_id, herb_id, sort_order) VALUES
 (1, 1, 1), (1, 2, 2),
 (2, 1, 1), (2, 2, 2),
 (3, 1, 1), (3, 3, 2), (3, 2, 3), (3, 4, 4),
 (4, 5, 1), (4, 6, 2), (4, 4, 3),
 (5, 1, 1), (5, 7, 2), (5, 8, 3),
 (6, 3, 1), (6, 9, 2), (6, 10, 3),
 (7, 11, 1), (7, 3, 2), (7, 12, 3),
 (8, 1, 1), (8, 3, 2), (8, 2, 3), (8, 4, 4),
 (9, 13, 1), (9, 14, 2), (9, 3, 3);

-- ── นักบำบัด T01–T06 + บริการที่ทำได้ ─────────────────────────────────────────
INSERT INTO therapist (id, code, name, name_en, name_zh, active) VALUES
 (1, 'T01', 'พี่สมศรี',     'Somsri',   '颂西',   TRUE),
 (2, 'T02', 'พี่มาลี',      'Malee',    '玛丽',   TRUE),
 (3, 'T03', 'พี่บุญมี',     'Boonmee',  '文米',   TRUE),
 (4, 'T04', 'พี่จันทร์เพ็ญ', 'Janpen',   '占彭',   TRUE),
 (5, 'T05', 'พี่ทองใบ',     'Thongbai', '通拜',   TRUE),
 (6, 'T06', 'พี่ดวงใจ',     'Duangjai', '端再',   TRUE);

INSERT INTO therapist_service (therapist_id, service_id) VALUES
 (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 8), (1, 9),
 (2, 1), (2, 2), (2, 3), (2, 5), (2, 8),
 (3, 1), (3, 2), (3, 4), (3, 5), (3, 6),
 (4, 1), (4, 2), (4, 5), (4, 6), (4, 7),
 (5, 1), (5, 2), (5, 3), (5, 4), (5, 7), (5, 9),
 (6, 1), (6, 2), (6, 3), (6, 5), (6, 8);

-- ── รีวิว 17 รายการ (booking_id NULL = รีวิวก่อนเปิดระบบ T9) ───────────────────
INSERT INTO review (id, therapist_id, customer_id, booking_id, stars, comment) VALUES
 (1,  1, 1, NULL, 5, 'มือหนัก กำลังดี'),
 (2,  1, 2, NULL, 5, 'Excellent massage'),
 (3,  1, 6, NULL, 5, 'ประทับใจมาก'),
 (4,  2, 4, NULL, 5, 'นวดดีมาก'),
 (5,  2, 5, NULL, 4, 'ดี'),
 (6,  3, 1, NULL, 5, 'ผ่อนคลาย'),
 (7,  3, 2, NULL, 5, 'ดีมาก'),
 (8,  3, 4, NULL, 4, 'โอเค'),
 (9,  3, 6, NULL, 4, 'ดี'),
 (10, 3, 7, NULL, 4, 'พอใช้'),
 (11, 5, 1, NULL, 5, 'เชี่ยวชาญ'),
 (12, 5, 2, NULL, 5, 'ดีมาก'),
 (13, 5, 5, NULL, 5, 'หน้าใสขึ้น'),
 (14, 5, 6, NULL, 4, 'ดี'),
 (15, 5, 7, NULL, 4, 'ดี'),
 (16, 6, 4, NULL, 5, 'ใจดี'),
 (17, 6, 7, NULL, 3, 'เฉย ๆ');

-- ── ห้อง Couple Suite ─────────────────────────────────────────────────────────
INSERT INTO room (id, name, capacity) VALUES (1, 'Couple Suite', 2);

-- ── โรงแรม H01–H06 (ชื่อสมมติ) ────────────────────────────────────────────────
INSERT INTO hotel (id, code, name, name_en, name_zh, distance_km) VALUES
 (1, 'H01', 'โรงแรมเรือนไทย ริเวอร์ไซด์', 'Ruen Thai Riverside Hotel', '泰屋河畔酒店',   2.0),
 (2, 'H02', 'โรงแรมบ้านสบาย สุขุมวิท',   'Baan Sabai Sukhumvit Hotel', '舒适之家素坤逸酒店', 5.0),
 (3, 'H03', 'โรงแรมดอกบัว สีลม',         'Dok Bua Silom Hotel',        '莲花是隆酒店',   5.1),
 (4, 'H04', 'โรงแรมกล้วยไม้ พาเลซ',      'Kluai Mai Palace Hotel',     '兰花宫殿酒店',   12.0),
 (5, 'H05', 'โรงแรมทองคำ แกรนด์',        'Thong Kham Grand Hotel',     '黄金大酒店',     15.0),
 (6, 'H06', 'โรงแรมสวนมะลิ บางนา',       'Suan Mali Bangna Hotel',     '茉莉花园邦纳酒店', 15.1);

-- ── คอร์สที่ซื้อแล้ว C01–C04 (ต้องมีก่อน booking ที่อ้างถึง) ──────────────────
INSERT INTO course_purchase (id, code, customer_id, service_id, price, total_sessions, used_sessions, reserved_sessions, purchased_on, expires_on) VALUES
 (1, 'C01', 1, 9, 15000.00, 11,  4, 0, '2026-08-01', '2027-01-28'),
 (2, 'C02', 7, 9, 15000.00, 11, 10, 0, '2026-04-23', '2026-10-20'),
 (3, 'C03', 6, 9, 15000.00, 11, 11, 0, '2026-06-01', '2026-11-28'),
 (4, 'C04', 5, 9, 15000.00, 11,  6, 0, '2026-03-01', '2026-08-28');

-- ── การจองที่มีอยู่ B01–B13 ───────────────────────────────────────────────────
INSERT INTO booking (id, code, customer_id, guest_name, guest_phone, contact_name, contact_phone, service_id, room_id, course_purchase_id,
  booking_type, party_size, start_at, end_at, status,
  gross_amount, discount_kind, discount_pct, discount_amount, points_redeemed, points_discount,
  distance_km, vehicles, transport_fee, total_amount, giftcard_paid, other_paid, points_earned,
  created_at, cancelled_at, completed_at) VALUES
 (1,  'B01', 4, NULL, NULL, 'คุณฝน', '081-111-0004', 1, NULL, NULL, 'single', 1,
      '2026-10-12 14:00+07', '2026-10-12 15:00+07', 'confirmed',
      1000.00, 'none', 0, 0, 0, 0, NULL, 0, 0, 1000.00, 0, 1000.00, 0, '2026-10-05 12:00+07', NULL, NULL),
 (2,  'B02', 2, NULL, NULL, 'คุณต้น', '081-111-0002', 2, 1, NULL, 'couple', 2,
      '2026-10-17 19:00+07', '2026-10-17 20:30+07', 'confirmed',
      2800.00, 'tier', 10, 280.00, 0, 0, NULL, 0, 0, 2520.00, 0, 2520.00, 0, '2026-10-06 20:00+07', NULL, NULL),
 (3,  'B03', NULL, 'คุณสมชาย', '081-000-0003', 'คุณสมชาย', '081-000-0003', 2, NULL, NULL, 'single', 1,
      '2026-10-13 10:00+07', '2026-10-13 11:30+07', 'confirmed',
      1400.00, 'none', 0, 0, 0, 0, NULL, 0, 0, 1400.00, 0, 1400.00, 0, '2026-10-07 09:00+07', NULL, NULL),
 (4,  'B04', 8, NULL, NULL, 'Mr. Li Wei', '+86-138-0000-0008', 1, NULL, NULL, 'group', 5,
      '2026-10-14 16:00+07', '2026-10-14 17:00+07', 'confirmed',
      5000.00, 'group', 10, 500.00, 0, 0, NULL, 0, 0, 4500.00, 0, 4500.00, 0, '2026-10-08 15:00+07', NULL, NULL),
 (5,  'B05', 1, NULL, NULL, 'คุณนิดา', '081-111-0001', 5, NULL, NULL, 'single', 1,
      '2026-10-11 10:00+07', '2026-10-11 11:00+07', 'confirmed',
      800.00, 'tier', 5, 40.00, 0, 0, NULL, 0, 0, 760.00, 0, 760.00, 0, '2026-10-03 18:00+07', NULL, NULL),
 (6,  'B06', 1, NULL, NULL, 'คุณนิดา', '081-111-0001', 1, NULL, NULL, 'single', 1,
      '2026-10-10 15:00+07', '2026-10-10 16:00+07', 'confirmed',
      1000.00, 'tier', 5, 50.00, 0, 0, NULL, 0, 0, 950.00, 0, 950.00, 0, '2026-10-04 18:00+07', NULL, NULL),
 (7,  'B07', 5, NULL, NULL, 'น้องแพร', '081-111-0005', 7, NULL, NULL, 'single', 1,
      '2026-10-05 13:00+07', '2026-10-05 14:00+07', 'completed',
      1800.00, 'birthday', 20, 360.00, 0, 0, NULL, 0, 0, 1440.00, 0, 1440.00, 14, '2026-10-01 10:00+07', NULL, '2026-10-05 14:00+07'),
 (8,  'B08', 1, NULL, NULL, 'คุณนิดา', '081-111-0001', 9, NULL, 1, 'course', 1,
      '2026-08-05 11:00+07', '2026-08-05 12:00+07', 'completed',
      0, 'none', 0, 0, 0, 0, NULL, 0, 0, 0, 0, 0, 0, '2026-08-01 12:00+07', NULL, '2026-08-05 12:00+07'),
 (9,  'B09', 1, NULL, NULL, 'คุณนิดา', '081-111-0001', 9, NULL, 1, 'course', 1,
      '2026-08-19 11:00+07', '2026-08-19 12:00+07', 'completed',
      0, 'none', 0, 0, 0, 0, NULL, 0, 0, 0, 0, 0, 0, '2026-08-06 12:00+07', NULL, '2026-08-19 12:00+07'),
 (10, 'B10', 1, NULL, NULL, 'คุณนิดา', '081-111-0001', 9, NULL, 1, 'course', 1,
      '2026-09-02 11:00+07', '2026-09-02 12:00+07', 'completed',
      0, 'none', 0, 0, 0, 0, NULL, 0, 0, 0, 0, 0, 0, '2026-08-20 12:00+07', NULL, '2026-09-02 12:00+07'),
 (11, 'B11', 1, NULL, NULL, 'คุณนิดา', '081-111-0001', 9, NULL, 1, 'course', 1,
      '2026-09-16 11:00+07', '2026-09-16 12:00+07', 'cancelled',
      0, 'none', 0, 0, 0, 0, NULL, 0, 0, 0, 0, 0, 0, '2026-09-03 12:00+07', '2026-09-10 09:00+07', NULL),
 (12, 'B12', 1, NULL, NULL, 'คุณนิดา', '081-111-0001', 9, NULL, 1, 'course', 1,
      '2026-09-23 11:00+07', '2026-09-23 12:00+07', 'completed',
      0, 'none', 0, 0, 0, 0, NULL, 0, 0, 0, 0, 0, 0, '2026-09-10 12:00+07', NULL, '2026-09-23 12:00+07'),
 (13, 'B13', 1, NULL, NULL, 'คุณนิดา', '081-111-0001', 4, NULL, NULL, 'single', 1,
      '2026-09-30 18:00+07', '2026-09-30 19:30+07', 'completed',
      2000.00, 'tier', 5, 100.00, 0, 0, NULL, 0, 0, 1900.00, 0, 1900.00, 19, '2026-09-25 12:00+07', NULL, '2026-09-30 19:30+07');

INSERT INTO booking_slot (id, booking_id, therapist_id, period, active) VALUES
 (1,  1,  3, '[2026-10-12 14:00+07, 2026-10-12 15:00+07)', TRUE),
 (2,  2,  1, '[2026-10-17 19:00+07, 2026-10-17 20:30+07)', TRUE),
 (3,  2,  2, '[2026-10-17 19:00+07, 2026-10-17 20:30+07)', TRUE),
 (4,  3,  6, '[2026-10-13 10:00+07, 2026-10-13 11:30+07)', TRUE),
 (5,  4,  1, '[2026-10-14 16:00+07, 2026-10-14 17:00+07)', TRUE),
 (6,  4,  2, '[2026-10-14 16:00+07, 2026-10-14 17:00+07)', TRUE),
 (7,  4,  3, '[2026-10-14 16:00+07, 2026-10-14 17:00+07)', TRUE),
 (8,  4,  4, '[2026-10-14 16:00+07, 2026-10-14 17:00+07)', TRUE),
 (9,  4,  5, '[2026-10-14 16:00+07, 2026-10-14 17:00+07)', TRUE),
 (10, 5,  4, '[2026-10-11 10:00+07, 2026-10-11 11:00+07)', TRUE),
 (11, 6,  2, '[2026-10-10 15:00+07, 2026-10-10 16:00+07)', TRUE),
 (12, 7,  5, '[2026-10-05 13:00+07, 2026-10-05 14:00+07)', TRUE),
 (13, 8,  1, '[2026-08-05 11:00+07, 2026-08-05 12:00+07)', TRUE),
 (14, 9,  5, '[2026-08-19 11:00+07, 2026-08-19 12:00+07)', TRUE),
 (15, 10, 1, '[2026-09-02 11:00+07, 2026-09-02 12:00+07)', TRUE),
 (16, 11, 5, '[2026-09-16 11:00+07, 2026-09-16 12:00+07)', FALSE),
 (17, 12, 5, '[2026-09-23 11:00+07, 2026-09-23 12:00+07)', TRUE),
 (18, 13, 3, '[2026-09-30 18:00+07, 2026-09-30 19:30+07)', TRUE);

-- ── รอบเอว 4 จุดของ C01 (FR-16) ───────────────────────────────────────────────
INSERT INTO waist_measurement (id, course_purchase_id, booking_id, measured_on, waist_cm) VALUES
 (1, 1, 8,  '2026-08-05', 82.0),
 (2, 1, 9,  '2026-08-19', 81.0),
 (3, 1, 10, '2026-09-02', 79.5),
 (4, 1, 12, '2026-09-23', 78.0);

-- ── รูป before/after ของ C01 (สัดส่วนร่างกาย ไม่มีใบหน้า · ไฟล์อยู่นอก public/) ──
INSERT INTO body_photo (id, course_purchase_id, phase, storage_key) VALUES
 (1, 1, 'before', 'c01-before.webp'),
 (2, 1, 'after',  'c01-after.webp');

-- ── Gift Card GC01–GC05 + รายการเคลื่อนไหว ───────────────────────────────────
INSERT INTO gift_card (id, code, buyer_id, face_value, balance, design, channel, recipient, message, purchased_on, expires_on) VALUES
 (1, 'SABAI-GC-2000', 4, 2000.00, 2000.00, 'lotus',  'line',  'แม่ของคุณฝน (LINE: mom.fon)', 'สุขสันต์วันแม่ค่ะ', '2026-10-01', '2027-10-01'),
 (2, 'SABAI-GC-PART', 6, 3000.00, 1250.00, 'gold',   'email', 'vipa@sabai.test', NULL, '2026-06-15', '2027-06-15'),
 (3, 'SABAI-GC-LAST', 2, 1000.00,  500.00, 'orchid', 'email', 'ton@sabai.test',  NULL, '2025-10-10', '2026-10-10'),
 (4, 'SABAI-GC-EXP',  5, 1000.00, 1000.00, 'lotus',  'line',  'prae.line',       NULL, '2025-10-09', '2026-10-09'),
 (5, 'SABAI-GC-ZERO', 4,  500.00,    0.00, 'gold',   'line',  'fon.line',        NULL, '2026-09-01', '2027-09-01');

INSERT INTO gift_card_txn (id, gift_card_id, booking_id, amount, created_at) VALUES
 (1, 2, NULL, -1750.00, '2026-08-20 15:00+07'),
 (2, 3, NULL,  -500.00, '2026-03-14 13:00+07'),
 (3, 5, NULL,  -500.00, '2026-09-15 17:00+07');

-- ── แต้ม: point_txn รวมแล้วเท่ากับ points_balance ของแต่ละคน ──────────────────
INSERT INTO point_txn (id, customer_id, booking_id, points, reason, created_at) VALUES
 (1, 1, NULL, 80,  'opening', '2026-01-15 10:00+07'),
 (2, 1, 13,   19,  'earn',    '2026-09-30 19:30+07'),
 (3, 4, NULL, 250, 'opening', '2025-11-20 10:00+07'),
 (4, 5, NULL, 86,  'opening', '2025-02-10 10:00+07'),
 (5, 5, 7,    14,  'earn',    '2026-10-05 14:00+07'),
 (6, 6, NULL, 199, 'opening', '2024-12-01 10:00+07');

-- ── สิทธิ์เดือนเกิดที่ใช้แล้ว: U05 ต.ค. 2026 (นัด B07) ───────────────────────────
INSERT INTO birthday_use (customer_id, year_month, booking_id) VALUES (5, 202610, 7);

-- ── "วันนี้" ของโหมดทดสอบ (NFR-13 · TEST-DATA §1) ─────────────────────────────
INSERT INTO app_setting (key, value) VALUES ('test_today', '2026-10-10T10:00:00+07:00');

-- ── วันหยุดร้าน CR-04 (ตรงกับ db/migrations/001_shop_holiday.sql) ─────────────────
INSERT INTO shop_holiday (holiday_date, name_th, name_en, name_zh) VALUES
 ('2026-10-23', 'วันปิยมหาราช',   'Chulalongkorn Day',     '五世王纪念日'),
 ('2026-12-05', 'วันพ่อแห่งชาติ', 'National Father''s Day', '父亲节'),
 ('2026-12-31', 'วันสิ้นปี',       'New Year''s Eve',       '新年前夕');

-- ── ตั้งลำดับ id ต่อจาก seed ──────────────────────────────────────────────────
SELECT setval(pg_get_serial_sequence('customer', 'id'), 9);
SELECT setval(pg_get_serial_sequence('service', 'id'), 9);
SELECT setval(pg_get_serial_sequence('herb', 'id'), 14);
SELECT setval(pg_get_serial_sequence('therapist', 'id'), 6);
SELECT setval(pg_get_serial_sequence('review', 'id'), 17);
SELECT setval(pg_get_serial_sequence('room', 'id'), 1);
SELECT setval(pg_get_serial_sequence('hotel', 'id'), 6);
SELECT setval(pg_get_serial_sequence('course_purchase', 'id'), 4);
SELECT setval(pg_get_serial_sequence('booking', 'id'), 13);
SELECT setval(pg_get_serial_sequence('booking_slot', 'id'), 18);
SELECT setval(pg_get_serial_sequence('waist_measurement', 'id'), 4);
SELECT setval(pg_get_serial_sequence('body_photo', 'id'), 2);
SELECT setval(pg_get_serial_sequence('gift_card', 'id'), 5);
SELECT setval(pg_get_serial_sequence('gift_card_txn', 'id'), 3);
SELECT setval(pg_get_serial_sequence('point_txn', 'id'), 6);
