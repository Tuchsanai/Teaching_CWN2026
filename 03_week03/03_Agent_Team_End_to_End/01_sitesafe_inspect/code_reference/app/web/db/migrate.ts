/**
 * Apply web/db/schema.sql (idempotent: CREATE … IF NOT EXISTS / CREATE OR REPLACE),
 * then bring databases created by an older schema up to date without touching data.
 * Must run with the table-owner account (DATABASE_OWNER_URL or DATABASE_URL).
 *
 * Used by resetAndSeed() (POST /api/test/reset, `npm run seed`) and by
 * `npm run migrate` (non-destructive: keeps every photo and result).
 */
import { promises as fs } from 'node:fs';
import path from 'node:path';
import type { Pool, PoolClient } from 'pg';

export function schemaPath(): string {
  return process.env.SCHEMA_SQL_PATH || path.join(process.cwd(), 'db', 'schema.sql');
}

/**
 * Older schemas repeated the upload limits of BR-05 / BR-06 inside CHECK constraints.
 * Those limits belong to web/lib/rules.ts only; a database CHECK that disagrees with
 * the rules turns an accepted upload into a 500. Replace such constraints by the
 * plain positive-value checks of the current schema.sql. Idempotent.
 */
const POSITIVE_CHECKS: readonly { table: string; column: string; constraint: string }[] = [
  { table: 'upload_batches', column: 'declared_count', constraint: 'upload_batches_declared_count_check' },
  { table: 'photos', column: 'size_bytes', constraint: 'photos_size_bytes_check' },
];

export async function relaxLegacyChecks(db: Pool | PoolClient): Promise<string[]> {
  const changed: string[] = [];
  for (const c of POSITIVE_CHECKS) {
    const wanted = `CHECK ((${c.column} >= 1))`;
    // Every CHECK on this single column (whatever its name) other than the wanted one.
    const r = await db.query<{ conname: string; def: string }>(
      `SELECT con.conname, pg_get_constraintdef(con.oid) AS def
         FROM pg_constraint con
         JOIN pg_attribute att ON att.attrelid = con.conrelid AND att.attnum = ANY (con.conkey)
        WHERE con.conrelid = to_regclass($1) AND con.contype = 'c'
          AND cardinality(con.conkey) = 1 AND att.attname = $2`,
      [`public.${c.table}`, c.column],
    );
    const stale = r.rows.filter((x) => x.def !== wanted);
    const hasWanted = r.rows.some((x) => x.def === wanted);
    if (stale.length === 0 && hasWanted) continue;
    for (const s of stale) {
      await db.query(`ALTER TABLE ${c.table} DROP CONSTRAINT ${quoteIdent(s.conname)}`);
    }
    if (!hasWanted) {
      await db.query(`ALTER TABLE ${c.table} ADD CONSTRAINT ${quoteIdent(c.constraint)} ${wanted}`);
    }
    changed.push(`${c.table}.${c.column}`);
  }
  return changed;
}

function quoteIdent(name: string): string {
  return `"${name.replace(/"/g, '""')}"`;
}

export async function applySchema(db: Pool | PoolClient): Promise<void> {
  const sql = await fs.readFile(schemaPath(), 'utf8');
  await db.query(sql);
  await relaxLegacyChecks(db);
}
