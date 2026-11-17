-- รายจ่าย 1 แถว = ใบเสร็จ 1 ใบที่ผู้ใช้กดบันทึก
CREATE TABLE IF NOT EXISTS expenses (
  id          SERIAL PRIMARY KEY,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  model       TEXT NOT NULL,            -- โมเดลที่อ่านใบนี้ (base / ft)
  source      TEXT NOT NULL DEFAULT '', -- ชื่อไฟล์หรือชื่อตัวอย่าง
  items       JSONB NOT NULL,           -- [{name, qty, price}]
  subtotal    BIGINT,
  tax         BIGINT,
  total       BIGINT,
  thumb       TEXT NOT NULL DEFAULT ''  -- ภาพย่อของใบเสร็จ (data URL)
);
