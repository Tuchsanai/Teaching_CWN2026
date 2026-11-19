/**
 * PostgreSQL connection pools (DESIGN §2).
 * - pool():      runtime account (DATABASE_URL), used by every API route.
 * - ownerPool(): table-owner account for migrate / reset / seed
 *                (DATABASE_OWNER_URL, falls back to DATABASE_URL).
 * Pools live on globalThis so Next.js route bundles share one pool per process.
 */
import { Pool, type PoolClient, type QueryResultRow } from 'pg';

type Pools = { runtime?: Pool; owner?: Pool };
const KEY = Symbol.for('sitesafe.db.pools');
const g = globalThis as unknown as Record<symbol, Pools | undefined>;
const pools: Pools = (g[KEY] ??= {});

function make(url: string | undefined, applicationName: string): Pool {
  if (!url) throw new Error('DATABASE_URL is not set');
  const p = new Pool({
    connectionString: url,
    max: Number(process.env.DB_POOL_MAX ?? 10),
    application_name: applicationName,
  });
  p.on('error', (err) => {
    console.error('[db] idle client error:', err.message);
  });
  return p;
}

export function pool(): Pool {
  return (pools.runtime ??= make(process.env.DATABASE_URL, process.env.DB_APPLICATION_NAME ?? 'sitesafe-web'));
}

export function ownerPool(): Pool {
  return (pools.owner ??= make(
    process.env.DATABASE_OWNER_URL || process.env.DATABASE_URL,
    'sitesafe-owner',
  ));
}

export async function query<T extends QueryResultRow = QueryResultRow>(
  text: string,
  params: unknown[] = [],
): Promise<T[]> {
  const r = await pool().query<T>(text, params);
  return r.rows;
}

/** Run fn inside BEGIN … COMMIT on the runtime pool (ROLLBACK on error). */
export async function withTransaction<T>(fn: (c: PoolClient) => Promise<T>, p: Pool = pool()): Promise<T> {
  const c = await p.connect();
  try {
    await c.query('BEGIN');
    const out = await fn(c);
    await c.query('COMMIT');
    return out;
  } catch (e) {
    try {
      await c.query('ROLLBACK');
    } catch {
      /* connection already broken */
    }
    throw e;
  } finally {
    c.release();
  }
}
