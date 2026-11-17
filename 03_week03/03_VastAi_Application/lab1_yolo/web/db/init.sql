-- ประวัติการตรวจรูป 1 แถวต่อ 1 รูป
CREATE TABLE IF NOT EXISTS inspections (
  id           SERIAL PRIMARY KEY,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  file_name    TEXT NOT NULL,
  mime         TEXT NOT NULL,
  image        BYTEA NOT NULL,
  width        INT NOT NULL,
  height       INT NOT NULL,
  model        TEXT NOT NULL,
  detections   JSONB NOT NULL,
  persons      INT NOT NULL,
  hardhat      INT NOT NULL,
  no_hardhat   INT NOT NULL,
  no_vest      INT NOT NULL,
  passed       BOOLEAN NOT NULL,
  inference_ms REAL NOT NULL,
  roundtrip_ms REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS inspections_created_idx ON inspections (created_at DESC);
