import type { PoolClient } from "pg";
import { q1 } from "./db";

/** NFR-14: "now" of the website. Locked by POST /api/test/reset { now }, otherwise the real clock. */
export async function getNow(c?: PoolClient): Promise<Date> {
  const sql = "SELECT value FROM settings WHERE key = 'fixed_now'";
  const row = c ? (await c.query<{ value: string }>(sql)).rows[0] ?? null : await q1<{ value: string }>(sql);
  if (row?.value) {
    const d = new Date(row.value);
    if (!Number.isNaN(d.getTime())) return d;
  }
  return new Date();
}
