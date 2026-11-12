-- BuildMart schema (CONTRACT ข้อ Database) — รันครั้งแรกตอนสร้าง volume bm-db เท่านั้น
-- แก้ schema แล้วต้อง: docker compose -p buildmart down -v (ลบ volume ของ buildmart เอง) แล้ว up ใหม่
SET client_encoding = 'UTF8';
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER DATABASE buildmart SET timezone TO 'Asia/Bangkok';
SET timezone TO 'Asia/Bangkok';

-- ---------- ร้าน / สินค้า ----------
CREATE TABLE products (
  sku           text PRIMARY KEY,
  name          text NOT NULL,
  category      text NOT NULL,
  unit          text NOT NULL,
  price         numeric(12,2) NOT NULL,
  weight_kg     numeric(10,3) NOT NULL,
  reorder_point int NOT NULL DEFAULT 0,
  description   text
);
CREATE INDEX products_category_idx ON products (category);
CREATE INDEX products_name_trgm ON products USING gin (name gin_trgm_ops);

CREATE TABLE branches (
  code  text PRIMARY KEY CHECK (code IN ('LKB','BNA','RST')),
  name  text NOT NULL,
  phone text NOT NULL
);

CREATE TABLE stock (
  sku    text NOT NULL REFERENCES products(sku) ON DELETE CASCADE,
  branch text NOT NULL REFERENCES branches(code),
  qty    int  NOT NULL DEFAULT 0 CHECK (qty >= 0),
  PRIMARY KEY (sku, branch)
);

CREATE TABLE coupons (
  code         text PRIMARY KEY,
  percent      numeric NOT NULL,
  min_subtotal numeric NOT NULL DEFAULT 0
);

-- ---------- ตะกร้า ----------
CREATE TABLE carts (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id text UNIQUE NOT NULL,
  coupon     text,                       -- (A) เพิ่ม: คูปองที่ใส่ไว้ในตะกร้า (POST /api/cart/coupon)
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE cart_items (
  cart_id uuid NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
  sku     text NOT NULL REFERENCES products(sku),
  qty     int  NOT NULL CHECK (qty > 0),
  PRIMARY KEY (cart_id, sku)
);

-- ---------- ใบเสนอราคา ----------
CREATE TABLE quotes (
  id            serial PRIMARY KEY,
  quote_no      text UNIQUE NOT NULL,     -- QT-YYYYMMDD-NNNN
  session_id    text,
  customer_name text,
  company       text,
  tax_id        text,
  coupon        text,
  totals        jsonb NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now(),
  expires_at    timestamptz NOT NULL DEFAULT (now() + interval '7 days')
);
CREATE TABLE quote_items (
  quote_id   int  NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
  sku        text NOT NULL REFERENCES products(sku),
  qty        int  NOT NULL,
  unit_price numeric(12,2) NOT NULL,
  PRIMARY KEY (quote_id, sku)
);

-- ---------- คำสั่งซื้อ ----------
CREATE TABLE orders (
  id            serial PRIMARY KEY,
  order_no      text UNIQUE NOT NULL,     -- BM-YYYYMMDD-NNNN
  session_id    text,
  customer_name text NOT NULL,
  phone         text NOT NULL,
  address       text,
  branch        text REFERENCES branches(code),
  delivery_date date,
  delivery_slot text CHECK (delivery_slot IN ('morning','afternoon')),
  coupon        text,
  totals        jsonb NOT NULL,
  status        text NOT NULL DEFAULT 'received' CHECK (status IN ('received','preparing','shipping','delivered')),
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX orders_created_idx ON orders (created_at);
CREATE TABLE order_items (
  order_id   int  NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  sku        text NOT NULL REFERENCES products(sku),
  qty        int  NOT NULL,
  unit_price numeric(12,2) NOT NULL,
  PRIMARY KEY (order_id, sku)
);
CREATE TABLE order_status_history (
  id         serial PRIMARY KEY,
  order_id   int  NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  status     text NOT NULL,
  changed_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX order_status_history_order_idx ON order_status_history (order_id, changed_at);

-- ---------- แชท ----------
CREATE TABLE chat_sessions (
  id         text PRIMARY KEY,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE chat_messages (
  id         serial PRIMARY KEY,
  session_id text NOT NULL,
  role       text NOT NULL CHECK (role IN ('user','assistant')),
  content    text NOT NULL,
  cites      jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX chat_messages_session_idx ON chat_messages (session_id, id);

-- ---------- เอกสาร RAG ----------
CREATE TABLE docs (
  id         serial PRIMARY KEY,
  filename   text UNIQUE NOT NULL,
  bytes      bytea NOT NULL,
  pages      int,
  chunks     int NOT NULL DEFAULT 0,
  status     text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','processing','ready','failed')),
  error      text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE doc_chunks (
  id        serial PRIMARY KEY,
  doc_id    int NOT NULL REFERENCES docs(id) ON DELETE CASCADE,
  filename  text NOT NULL,
  page      int NOT NULL,
  chunk_no  int NOT NULL,
  content   text NOT NULL,
  embedding vector(384)
);
CREATE INDEX doc_chunks_embedding_hnsw ON doc_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX doc_chunks_content_trgm ON doc_chunks USING gin (content gin_trgm_ops);
CREATE INDEX doc_chunks_doc_idx ON doc_chunks (doc_id);

-- ---------- แจ้งเตือนหลังร้าน ----------
CREATE TABLE notifications (
  id         serial PRIMARY KEY,
  kind       text NOT NULL CHECK (kind IN ('order','low_stock')),
  message    text NOT NULL,
  ref        text,
  created_at timestamptz NOT NULL DEFAULT now(),
  read       boolean NOT NULL DEFAULT false
);

-- ---------- เสียง TTS ----------
CREATE TABLE tts_audio (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lang        text,
  text        text,
  wav         bytea,
  duration_ms int,
  engine      text,                      -- v3: voxcpm2 | kokoro | pythaitts
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- ---------- v3: ผลประเมิน RAG (POST /api/admin/eval · หน้า /admin/eval) ----------
CREATE TABLE eval_runs (
  id         serial PRIMARY KEY,
  label      text,
  created_at timestamptz NOT NULL DEFAULT now(),
  config     jsonb,
  summary    jsonb,
  items      jsonb
);

-- ---------- เลขเอกสาร QT/BM (ใช้ร่วมกันทั้ง web และ workers) ----------
-- SELECT next_doc_no('QT') → 'QT-20261023-0001' · นับแยกตาม prefix และวัน (เวลาไทย)
CREATE TABLE doc_counters (
  prefix text NOT NULL,
  day    date NOT NULL,
  n      int  NOT NULL DEFAULT 0,
  PRIMARY KEY (prefix, day)
);
CREATE OR REPLACE FUNCTION next_doc_no(p_prefix text) RETURNS text
LANGUAGE plpgsql AS $$
DECLARE
  d date := (now() AT TIME ZONE 'Asia/Bangkok')::date;
  v int;
BEGIN
  INSERT INTO doc_counters (prefix, day, n) VALUES (p_prefix, d, 1)
  ON CONFLICT (prefix, day) DO UPDATE SET n = doc_counters.n + 1
  RETURNING n INTO v;
  RETURN p_prefix || '-' || to_char(d, 'YYYYMMDD') || '-' || lpad(v::text, 4, '0');
END $$;

-- ---------- v3: ผล load test (loadtest/run_load.mjs → POST /api/admin/load · หน้า /admin/load) ----------
-- items = ขั้นของ load test [{users, n, errors, p50, p95, ttft_p50, ttft_p95, rtf, tokens_per_s, queue_max, ok}]
CREATE TABLE load_runs (
  id         serial PRIMARY KEY,
  label      text,
  created_at timestamptz NOT NULL DEFAULT now(),
  config     jsonb,
  summary    jsonb,
  items      jsonb
);
