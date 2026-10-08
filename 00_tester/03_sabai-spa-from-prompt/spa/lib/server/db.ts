import { Pool, type PoolClient, type QueryResultRow } from "pg";
import { SCHEMA_SQL } from "./schema";
import { seedAll } from "./seed";

type G = typeof globalThis & { __sabaiPool?: Pool; __sabaiInit?: Promise<void> | null };
const g = globalThis as G;

export function pool(): Pool {
  if (!g.__sabaiPool) {
    const url = process.env.DATABASE_URL;
    if (!url) throw new Error("DATABASE_URL is not set");
    g.__sabaiPool = new Pool({ connectionString: url, max: 10, connectionTimeoutMillis: 3000 });
    g.__sabaiPool.on("error", (e) => console.error("[db] idle client error", e.message));
  }
  return g.__sabaiPool;
}

export async function q<T extends QueryResultRow = QueryResultRow>(sql: string, params: unknown[] = []): Promise<T[]> {
  await ensureDb();
  const r = await pool().query<T>(sql, params);
  return r.rows;
}

export async function q1<T extends QueryResultRow = QueryResultRow>(sql: string, params: unknown[] = []): Promise<T | null> {
  const rows = await q<T>(sql, params);
  return rows[0] ?? null;
}

export async function tx<T>(fn: (c: PoolClient) => Promise<T>): Promise<T> {
  await ensureDb();
  const c = await pool().connect();
  try {
    await c.query("BEGIN");
    const out = await fn(c);
    await c.query("COMMIT");
    return out;
  } catch (e) {
    await c.query("ROLLBACK").catch(() => undefined);
    throw e;
  } finally {
    c.release();
  }
}

/** Create tables if missing, then seed once if the database is empty (runs on start-up). */
async function init(): Promise<void> {
  const c = await pool().connect();
  try {
    await c.query("SELECT pg_advisory_lock(727001)");
    await c.query(SCHEMA_SQL);
    const r = await c.query<{ n: string }>("SELECT count(*)::text AS n FROM users");
    if (r.rows[0].n === "0") {
      await c.query("BEGIN");
      await seedAll(c, new Date());
      await c.query("COMMIT");
      console.log("[db] seeded initial data");
    }
  } catch (e) {
    await c.query("ROLLBACK").catch(() => undefined);
    throw e;
  } finally {
    await c.query("SELECT pg_advisory_unlock(727001)").catch(() => undefined);
    c.release();
  }
}

export function ensureDb(): Promise<void> {
  if (!g.__sabaiInit) {
    g.__sabaiInit = init().catch((e) => {
      g.__sabaiInit = null; // retry on next call
      throw e;
    });
  }
  return g.__sabaiInit;
}
