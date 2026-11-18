import { Pool } from "pg";

const g = globalThis as unknown as { _pool?: Pool; _ready?: Promise<void> };
export const pool = g._pool ?? (g._pool = new Pool({ connectionString: process.env.DATABASE_URL }));

export function ready() {
  return (g._ready ??= pool
    .query(`CREATE TABLE IF NOT EXISTS inspections (
      id SERIAL PRIMARY KEY,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      filename TEXT NOT NULL,
      mime TEXT NOT NULL,
      image BYTEA NOT NULL,
      model TEXT NOT NULL,
      width INT NOT NULL,
      height INT NOT NULL,
      passed BOOLEAN NOT NULL,
      persons INT NOT NULL,
      hardhat INT NOT NULL,
      no_hardhat INT NOT NULL,
      no_vest INT NOT NULL,
      inference_ms REAL NOT NULL,
      roundtrip_ms REAL NOT NULL,
      detections JSONB NOT NULL
    )`)
    .then(() => undefined)
    .catch((e) => { g._ready = undefined; throw e; }));
}
