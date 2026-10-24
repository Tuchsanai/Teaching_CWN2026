-- สบายใจ สปา · schema ตาม DESIGN.md §4 (ERD 17 ตาราง) + hotel + therapist_service
-- เงิน NUMERIC(10,2) · แต้ม INTEGER · ครั้งคอร์ส SMALLINT · เวลา TIMESTAMPTZ · ช่วงเวลา [start,end)
-- ไม่มีตาราง/คอลัมน์รูปโปรไฟล์หรือรูปหน้า (NFR-10)

CREATE EXTENSION IF NOT EXISTS btree_gist;

SET TIME ZONE 'Asia/Bangkok';

CREATE TABLE customer (
  id              SERIAL PRIMARY KEY,
  name            VARCHAR(120) NOT NULL,
  phone           VARCHAR(20),
  email           VARCHAR(160) UNIQUE,
  line_id         VARCHAR(60),
  birth_date      DATE,
  lang            VARCHAR(2) NOT NULL DEFAULT 'th' CHECK (lang IN ('th','en','zh')),
  lifetime_spend  NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (lifetime_spend >= 0),
  points_balance  INTEGER NOT NULL DEFAULT 0 CHECK (points_balance >= 0),
  password_hash   VARCHAR(100),
  role            VARCHAR(10) NOT NULL DEFAULT 'customer' CHECK (role IN ('customer','owner')),
  created_on      DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE therapist (
  id      SERIAL PRIMARY KEY,
  code    VARCHAR(4) NOT NULL UNIQUE,
  name    VARCHAR(80) NOT NULL,
  name_en VARCHAR(80) NOT NULL,
  name_zh VARCHAR(80) NOT NULL,
  active  BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE service (
  id                 SERIAL PRIMARY KEY,
  code               VARCHAR(4) NOT NULL UNIQUE,
  name_th            VARCHAR(120) NOT NULL,
  name_en            VARCHAR(120) NOT NULL,
  name_zh            VARCHAR(120) NOT NULL,
  kind               VARCHAR(10) NOT NULL CHECK (kind IN ('single','package','course')),
  duration_min       SMALLINT NOT NULL CHECK (duration_min > 0),
  price              NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  includes_transport BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE herb (
  id      SERIAL PRIMARY KEY,
  name_th VARCHAR(60) NOT NULL UNIQUE,
  name_en VARCHAR(60) NOT NULL,
  name_zh VARCHAR(60) NOT NULL
);

CREATE TABLE service_herb (
  service_id INTEGER NOT NULL REFERENCES service(id) ON DELETE CASCADE,
  herb_id    INTEGER NOT NULL REFERENCES herb(id),
  sort_order SMALLINT NOT NULL DEFAULT 0,
  PRIMARY KEY (service_id, herb_id)
);

-- บริการที่นักบำบัดแต่ละคนทำได้ (TEST-DATA §4)
CREATE TABLE therapist_service (
  therapist_id INTEGER NOT NULL REFERENCES therapist(id) ON DELETE CASCADE,
  service_id   INTEGER NOT NULL REFERENCES service(id) ON DELETE CASCADE,
  PRIMARY KEY (therapist_id, service_id)
);

CREATE TABLE room (
  id       SERIAL PRIMARY KEY,
  name     VARCHAR(60) NOT NULL,
  capacity SMALLINT NOT NULL CHECK (capacity > 0)
);

CREATE TABLE hotel (
  id          SERIAL PRIMARY KEY,
  code        VARCHAR(4) NOT NULL UNIQUE,
  name        VARCHAR(120) NOT NULL,
  name_en     VARCHAR(120) NOT NULL,
  name_zh     VARCHAR(120) NOT NULL,
  distance_km NUMERIC(4,1) NOT NULL CHECK (distance_km >= 0)
);

CREATE TABLE course_purchase (
  id                SERIAL PRIMARY KEY,
  code              VARCHAR(4) UNIQUE,
  customer_id       INTEGER NOT NULL REFERENCES customer(id),
  service_id        INTEGER NOT NULL REFERENCES service(id),
  price             NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  total_sessions    SMALLINT NOT NULL CHECK (total_sessions > 0),
  used_sessions     SMALLINT NOT NULL DEFAULT 0 CHECK (used_sessions >= 0),
  reserved_sessions SMALLINT NOT NULL DEFAULT 0 CHECK (reserved_sessions >= 0),
  purchased_on      DATE NOT NULL,
  expires_on        DATE NOT NULL,
  CHECK (used_sessions + reserved_sessions <= total_sessions),
  CHECK (expires_on >= purchased_on)
);

CREATE TABLE booking (
  id                 SERIAL PRIMARY KEY,
  code               VARCHAR(8) UNIQUE,
  customer_id        INTEGER REFERENCES customer(id),
  guest_name         VARCHAR(120),
  guest_phone        VARCHAR(20),
  contact_name       VARCHAR(120),
  contact_phone      VARCHAR(20),
  service_id         INTEGER NOT NULL REFERENCES service(id),
  room_id            INTEGER REFERENCES room(id),
  course_purchase_id INTEGER REFERENCES course_purchase(id),
  booking_type       VARCHAR(10) NOT NULL CHECK (booking_type IN ('single','couple','group','package','course')),
  party_size         SMALLINT NOT NULL CHECK (party_size BETWEEN 1 AND 6),
  start_at           TIMESTAMPTZ NOT NULL,
  end_at             TIMESTAMPTZ NOT NULL,
  period             TSTZRANGE GENERATED ALWAYS AS (tstzrange(start_at, end_at, '[)')) STORED,
  status             VARCHAR(10) NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed','cancelled','completed')),
  gross_amount       NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (gross_amount >= 0),
  discount_kind      VARCHAR(10) NOT NULL DEFAULT 'none' CHECK (discount_kind IN ('none','group','tier','birthday')),
  discount_pct       NUMERIC(4,2) NOT NULL DEFAULT 0 CHECK (discount_pct >= 0 AND discount_pct <= 100),
  discount_amount    NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
  points_redeemed    INTEGER NOT NULL DEFAULT 0 CHECK (points_redeemed >= 0 AND points_redeemed % 100 = 0),
  points_discount    NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (points_discount >= 0),
  distance_km        NUMERIC(4,1) CHECK (distance_km IS NULL OR (distance_km >= 0 AND distance_km <= 15.0)),
  vehicles           SMALLINT NOT NULL DEFAULT 0 CHECK (vehicles >= 0),
  transport_fee      NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (transport_fee >= 0),
  total_amount       NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
  giftcard_paid      NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (giftcard_paid >= 0),
  other_paid         NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (other_paid >= 0),
  points_earned      INTEGER NOT NULL DEFAULT 0 CHECK (points_earned >= 0),
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  cancelled_at       TIMESTAMPTZ,
  completed_at       TIMESTAMPTZ,
  CHECK (end_at > start_at),
  CHECK (customer_id IS NOT NULL OR guest_name IS NOT NULL),
  CHECK (booking_type <> 'couple' OR (party_size = 2 AND room_id IS NOT NULL)),
  CHECK (booking_type <> 'group' OR party_size BETWEEN 3 AND 6),
  CHECK (booking_type <> 'single' OR party_size = 1),
  CHECK (booking_type <> 'course' OR (party_size = 1 AND course_purchase_id IS NOT NULL)),
  CHECK (giftcard_paid + other_paid = total_amount),
  -- BR-04 Couple Suite 1 คู่ต่อช่วงเวลา (นัดที่ไม่ถูกยกเลิก)
  CONSTRAINT booking_room_no_overlap EXCLUDE USING gist (room_id WITH =, period WITH &&)
    WHERE (room_id IS NOT NULL AND status <> 'cancelled')
);

CREATE INDEX booking_start_idx ON booking (start_at);
CREATE INDEX booking_customer_idx ON booking (customer_id);

CREATE TABLE booking_slot (
  id           SERIAL PRIMARY KEY,
  booking_id   INTEGER NOT NULL REFERENCES booking(id) ON DELETE CASCADE,
  therapist_id INTEGER NOT NULL REFERENCES therapist(id),
  period       TSTZRANGE NOT NULL,
  active       BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (booking_id, therapist_id),
  -- BR-02 นักบำบัด 1 คน 1 คิวต่อเวลา · [start,end) ทำให้ต่อกันพอดีไม่ชน
  CONSTRAINT booking_slot_no_overlap EXCLUDE USING gist (therapist_id WITH =, period WITH &&) WHERE (active)
);

CREATE TABLE review (
  id           SERIAL PRIMARY KEY,
  therapist_id INTEGER NOT NULL REFERENCES therapist(id),
  customer_id  INTEGER REFERENCES customer(id),
  booking_id   INTEGER REFERENCES booking(id),
  stars        SMALLINT NOT NULL CHECK (stars BETWEEN 1 AND 5),
  comment      TEXT
);

CREATE TABLE waist_measurement (
  id                 SERIAL PRIMARY KEY,
  course_purchase_id INTEGER NOT NULL REFERENCES course_purchase(id),
  booking_id         INTEGER UNIQUE REFERENCES booking(id),
  measured_on        DATE NOT NULL,
  waist_cm           NUMERIC(5,1) NOT NULL CHECK (waist_cm > 0)
);

-- รูปสัดส่วนร่างกายไม่มีใบหน้า (FR-18) เก็บไฟล์นอก web root อ้างด้วย storage_key
CREATE TABLE body_photo (
  id                 SERIAL PRIMARY KEY,
  course_purchase_id INTEGER NOT NULL REFERENCES course_purchase(id),
  phase              VARCHAR(6) NOT NULL CHECK (phase IN ('before','after')),
  storage_key        VARCHAR(120) NOT NULL
);

CREATE TABLE gift_card (
  id           SERIAL PRIMARY KEY,
  code         VARCHAR(40) NOT NULL UNIQUE,
  buyer_id     INTEGER REFERENCES customer(id),
  face_value   NUMERIC(10,2) NOT NULL CHECK (face_value BETWEEN 500 AND 10000 AND face_value = trunc(face_value)),
  balance      NUMERIC(10,2) NOT NULL CHECK (balance >= 0),
  design       VARCHAR(8) NOT NULL CHECK (design IN ('orchid','lotus','gold')),
  channel      VARCHAR(6) NOT NULL CHECK (channel IN ('line','email')),
  recipient    VARCHAR(160) NOT NULL,
  message      VARCHAR(300),
  purchased_on DATE NOT NULL,
  expires_on   DATE NOT NULL,
  CHECK (balance <= face_value),
  CHECK (expires_on = purchased_on + 365)
);

CREATE TABLE gift_card_txn (
  id           SERIAL PRIMARY KEY,
  gift_card_id INTEGER NOT NULL REFERENCES gift_card(id),
  booking_id   INTEGER REFERENCES booking(id),
  amount       NUMERIC(10,2) NOT NULL CHECK (amount <> 0),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE point_txn (
  id          SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customer(id),
  booking_id  INTEGER REFERENCES booking(id),
  points      INTEGER NOT NULL CHECK (points <> 0),
  reason      VARCHAR(8) NOT NULL CHECK (reason IN ('earn','redeem','refund','opening')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- BR-13 เดือนเกิด 1 ครั้งต่อเดือน: PK (customer_id, year_month)
CREATE TABLE birthday_use (
  customer_id INTEGER NOT NULL REFERENCES customer(id),
  year_month  INTEGER NOT NULL CHECK (year_month BETWEEN 200001 AND 299912),
  booking_id  INTEGER REFERENCES booking(id),
  PRIMARY KEY (customer_id, year_month)
);

CREATE TABLE app_setting (
  key   VARCHAR(40) PRIMARY KEY,
  value VARCHAR(200) NOT NULL
);
