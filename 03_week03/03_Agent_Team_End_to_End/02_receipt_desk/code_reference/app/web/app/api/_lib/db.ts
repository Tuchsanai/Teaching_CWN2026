/**
 * PostgreSQL pool ของ web (B04) — ใช้ร่วมกันทุก route ใน web/app/api
 * โฟลเดอร์ `_lib` ขึ้นต้นด้วย `_` จึงไม่ถูก Next.js นับเป็น route
 */
import { Pool, types } from 'pg';
import type { PoolClient, QueryResultRow } from 'pg';

// `date` (OID 1082) ให้คงเป็นข้อความ 'YYYY-MM-DD' — ถ้าแปลงเป็น Date จะเลื่อนวันตามเขตเวลา (BR-14)
types.setTypeParser(1082, (value: string) => value);

const globalForPool = globalThis as unknown as { __receiptdeskPool?: Pool };

export function pool(): Pool {
  if (!globalForPool.__receiptdeskPool) {
    const p = new Pool({
      connectionString: process.env.DATABASE_URL,
      max: Number(process.env.DATABASE_POOL_MAX || 10),
      connectionTimeoutMillis: 5_000,
    });
    p.on('error', (error) => {
      console.error('[db] idle client error:', error.message);
    });
    globalForPool.__receiptdeskPool = p;
  }
  return globalForPool.__receiptdeskPool;
}

export async function query<T extends QueryResultRow = QueryResultRow>(
  text: string,
  params: unknown[] = [],
): Promise<T[]> {
  const result = await pool().query<T>(text, params);
  return result.rows;
}

export async function queryOne<T extends QueryResultRow = QueryResultRow>(
  text: string,
  params: unknown[] = [],
): Promise<T | undefined> {
  const rows = await query<T>(text, params);
  return rows[0];
}

/** รัน `fn` ในธุรกรรมเดียว · โยน error → ROLLBACK */
export async function transaction<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool().connect();
  try {
    await client.query('BEGIN');
    const result = await fn(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK').catch(() => {});
    throw error;
  } finally {
    client.release();
  }
}

/** เวลาปัจจุบันจากนาฬิกาของฐานข้อมูล — ใช้เทียบกับ timestamptz ในตาราง (BR-09 · BR-12 · BR-13) */
export async function dbNow(client?: PoolClient): Promise<Date> {
  const sql = 'SELECT clock_timestamp() AS now';
  const row = client ? (await client.query<{ now: Date }>(sql)).rows[0] : await queryOne<{ now: Date }>(sql);
  return row ? new Date(row.now) : new Date();
}

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isUuid(value: unknown): value is string {
  return typeof value === 'string' && UUID_RE.test(value);
}
