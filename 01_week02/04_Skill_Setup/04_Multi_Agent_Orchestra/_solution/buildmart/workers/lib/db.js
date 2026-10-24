// workers/lib/db.js — pg Pool + รอ DB พร้อม · numeric/int8 → number
import pg from 'pg';

pg.types.setTypeParser(1700, (v) => parseFloat(v)); // numeric
pg.types.setTypeParser(20, (v) => parseInt(v, 10)); // int8 / count(*)

export const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://bm:bm@localhost:5432/buildmart',
  max: Number(process.env.PG_POOL_MAX || 10),
});
pool.on('error', (e) => console.error('[db] idle client error', e.message));

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** รอจน SELECT 1 ผ่าน (ลองซ้ำ) แล้วคืน pool */
export async function waitForDb({ retries = 60, delayMs = 1000 } = {}) {
  for (let i = 0; ; i++) {
    try {
      await pool.query('SELECT 1');
      return pool;
    } catch (e) {
      if (i >= retries) throw e;
      console.warn(`[db] not ready (${e.message}) retry ${i + 1}`);
      await sleep(delayMs);
    }
  }
}

/** ทำงานใน transaction: await tx(async (c) => { ... }) */
export async function tx(fn) {
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
