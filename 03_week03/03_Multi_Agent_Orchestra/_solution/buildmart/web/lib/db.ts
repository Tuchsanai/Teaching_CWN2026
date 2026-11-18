// lib/db.ts — pg Pool ตัวเดียวทั้งแอป (เก็บบน globalThis กัน hot-reload สร้างซ้ำ)
// numeric → number, int8 (count) → number อัตโนมัติ (ตั้ง type parser ไว้ที่นี่)
import { Pool, types, type PoolClient, type QueryResultRow } from 'pg';

types.setTypeParser(1700, (v: string) => parseFloat(v)); // numeric
types.setTypeParser(20, (v: string) => parseInt(v, 10)); // int8 / count(*)

const g = globalThis as unknown as { __bmPool?: Pool };

export const pool: Pool =
  g.__bmPool ??
  (g.__bmPool = new Pool({
    connectionString: process.env.DATABASE_URL || 'postgres://bm:bm@localhost:5432/buildmart',
    max: 10,
  }));

export async function query<T extends QueryResultRow = any>(text: string, params: unknown[] = []) {
  return pool.query<T>(text, params as any[]);
}

/** ทำงานใน transaction: await tx(async (c) => { await c.query(...) }) */
export async function tx<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const out = await fn(client);
    await client.query('COMMIT');
    return out;
  } catch (e) {
    await client.query('ROLLBACK').catch(() => {});
    throw e;
  } finally {
    client.release();
  }
}
