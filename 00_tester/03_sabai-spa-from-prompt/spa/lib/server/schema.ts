export const SCHEMA_SQL = `
CREATE TABLE IF NOT EXISTS settings (
  key   text PRIMARY KEY,
  value text
);

CREATE TABLE IF NOT EXISTS users (
  id                 serial PRIMARY KEY,
  email              text UNIQUE NOT NULL,
  password_hash      text NOT NULL,
  name               text NOT NULL,
  name_en            text,
  birth_month        int NOT NULL CHECK (birth_month BETWEEN 1 AND 12),
  birth_day          int,
  total_spent        int NOT NULL DEFAULT 0,
  points             int NOT NULL DEFAULT 0,
  birthday_used_year int,
  created_at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
  token      text PRIMARY KEY,
  user_id    int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS services (
  slug       text PRIMARY KEY,
  sort       int NOT NULL,
  category   text NOT NULL,
  duration   int NOT NULL,
  price      int NOT NULL,
  herbs      text[] NOT NULL,
  image      text NOT NULL,
  is_package boolean NOT NULL DEFAULT false,
  name_th text NOT NULL, name_en text NOT NULL, name_zh text NOT NULL,
  desc_th text NOT NULL, desc_en text NOT NULL, desc_zh text NOT NULL
);

CREATE TABLE IF NOT EXISTS therapists (
  id    int PRIMARY KEY,
  image text NOT NULL,
  name_th text NOT NULL, name_en text NOT NULL, name_zh text NOT NULL,
  title_th text NOT NULL, title_en text NOT NULL, title_zh text NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
  id           serial PRIMARY KEY,
  therapist_id int NOT NULL REFERENCES therapists(id) ON DELETE CASCADE,
  author       text NOT NULL,
  rating       int NOT NULL CHECK (rating BETWEEN 1 AND 5),
  reviewed_on  date NOT NULL,
  text_th text NOT NULL, text_en text NOT NULL, text_zh text NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms (
  slug     text PRIMARY KEY,
  sort     int NOT NULL,
  image    text NOT NULL,
  capacity int NOT NULL,
  name_th text NOT NULL, name_en text NOT NULL, name_zh text NOT NULL,
  desc_th text NOT NULL, desc_en text NOT NULL, desc_zh text NOT NULL
);

CREATE TABLE IF NOT EXISTS hotels (
  id          int PRIMARY KEY,
  name        text NOT NULL,
  name_zh     text NOT NULL,
  distance_km numeric(5,1) NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
  id             serial PRIMARY KEY,
  user_id        int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  service_slug   text NOT NULL,
  total_sessions int NOT NULL,
  used_sessions  int NOT NULL DEFAULT 0,
  price          int NOT NULL,
  purchased_on   date NOT NULL,
  expires_on     date NOT NULL
);

CREATE TABLE IF NOT EXISTS waist_measurements (
  id          serial PRIMARY KEY,
  user_id     int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  measured_on date NOT NULL,
  cm          numeric(5,1) NOT NULL
);

CREATE TABLE IF NOT EXISTS body_photos (
  id       serial PRIMARY KEY,
  user_id  int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  taken_on date NOT NULL,
  kind     text NOT NULL,
  image    text NOT NULL
);

CREATE TABLE IF NOT EXISTS gift_cards (
  code           text PRIMARY KEY,
  amount         int NOT NULL,
  balance        int NOT NULL,
  design         text NOT NULL,
  channel        text NOT NULL,
  recipient      text NOT NULL,
  recipient_name text,
  sender_name    text,
  message        text,
  buyer_user_id  int REFERENCES users(id) ON DELETE SET NULL,
  purchased_on   date NOT NULL,
  expires_on     date NOT NULL,
  created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bookings (
  id                serial PRIMARY KEY,
  code              text UNIQUE,
  user_id           int REFERENCES users(id) ON DELETE SET NULL,
  guest_name        text,
  guest_phone       text,
  service_slug      text NOT NULL,
  kind              text NOT NULL,
  people            int NOT NULL,
  start_at          timestamptz NOT NULL,
  end_at            timestamptz NOT NULL,
  status            text NOT NULL DEFAULT 'confirmed',
  therapist_ids     int[] NOT NULL,
  room_slug         text,
  hotel_id          int,
  cars              int NOT NULL DEFAULT 0,
  subtotal          int NOT NULL DEFAULT 0,
  group_discount    int NOT NULL DEFAULT 0,
  tier_discount     int NOT NULL DEFAULT 0,
  birthday_discount int NOT NULL DEFAULT 0,
  points_used       int NOT NULL DEFAULT 0,
  points_discount   int NOT NULL DEFAULT 0,
  course_id         int,
  course_covered    int NOT NULL DEFAULT 0,
  course_step       int NOT NULL DEFAULT 0,
  transport_fee     int NOT NULL DEFAULT 0,
  total             int NOT NULL DEFAULT 0,
  gift_code         text,
  gift_used         int NOT NULL DEFAULT 0,
  due               int NOT NULL DEFAULT 0,
  points_earned     int NOT NULL DEFAULT 0,
  spent_added       int NOT NULL DEFAULT 0,
  birthday_used     boolean NOT NULL DEFAULT false,
  source            text NOT NULL DEFAULT 'web',
  created_at        timestamptz NOT NULL DEFAULT now(),
  cancelled_at      timestamptz
);

CREATE TABLE IF NOT EXISTS booking_resources (
  id         serial PRIMARY KEY,
  booking_id int NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
  resource   text NOT NULL,
  start_at   timestamptz NOT NULL,
  end_at     timestamptz NOT NULL
);
CREATE INDEX IF NOT EXISTS booking_resources_res_idx ON booking_resources (resource, start_at);
`;

export const ALL_TABLES = [
  "booking_resources",
  "bookings",
  "gift_cards",
  "body_photos",
  "waist_measurements",
  "courses",
  "sessions",
  "reviews",
  "therapists",
  "rooms",
  "hotels",
  "services",
  "users",
  "settings",
];
