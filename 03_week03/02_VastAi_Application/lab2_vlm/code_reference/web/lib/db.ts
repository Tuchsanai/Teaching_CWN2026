import { Pool } from "pg";

const g = globalThis as unknown as { _pool?: Pool; _ready?: Promise<void> };
export const pool = g._pool ?? (g._pool = new Pool({ connectionString: process.env.DATABASE_URL }));

export function ready() {
  return (g._ready ??= pool.query(`
    CREATE TABLE IF NOT EXISTS expenses (
      id         SERIAL PRIMARY KEY,
      title      TEXT NOT NULL,
      model      TEXT NOT NULL,
      items      JSONB NOT NULL,
      subtotal   BIGINT,
      tax        BIGINT,
      total      BIGINT,
      seconds    REAL,
      image      BYTEA,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )`).then(() => undefined));
}
