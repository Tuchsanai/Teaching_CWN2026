// lib/runs.ts — เก็บ/อ่านผล "run" (ประเมิน RAG = eval_runs · load test = load_runs) — v3 (CONTRACT_V3 §5–§8)
//   สิทธิ์: cookie admin (bm_admin) หรือ header `x-eval-token: ${EVAL_TOKEN:-bm-eval}` (สคริปต์ score.mjs / run_load.mjs)
//   ตารางสร้างใน db/init/01_schema.sql · volume เก่าจาก v2 ไม่มีตาราง → สร้างให้อัตโนมัติ (CREATE TABLE IF NOT EXISTS)
import { NextResponse } from 'next/server';
import { timingSafeEqual } from 'node:crypto';
import { query } from '@/lib/db';
import { isAdmin } from '@/app/api/admin/_auth';

export type RunTable = 'eval_runs' | 'load_runs';
const TABLES: RunTable[] = ['eval_runs', 'load_runs'];

const ensured = new Set<RunTable>();
async function ensure(table: RunTable) {
  if (ensured.has(table)) return;
  await query(
    `CREATE TABLE IF NOT EXISTS ${table} (
       id serial PRIMARY KEY, label text, created_at timestamptz NOT NULL DEFAULT now(),
       config jsonb, summary jsonb, items jsonb)`,
  );
  ensured.add(table);
}

export const evalToken = () => process.env.EVAL_TOKEN || 'bm-eval';

function tokenOk(req: Request) {
  const got = req.headers.get('x-eval-token') || '';
  const want = evalToken();
  const a = Buffer.from(got);
  const b = Buffer.from(want);
  return a.length === b.length && timingSafeEqual(a, b);
}

/** admin cookie หรือ x-eval-token ถูก → null · ไม่งั้น 401 */
export function requireRunAuth(req: Request): NextResponse | null {
  return isAdmin() || tokenOk(req) ? null : NextResponse.json({ error: 'unauthorized' }, { status: 401 });
}

const toRun = (r: any, withItems: boolean) => ({
  id: r.id,
  label: r.label,
  createdAt: r.created_at,
  config: r.config ?? {},
  summary: r.summary ?? {},
  ...(withItems ? { items: r.items ?? [] } : {}),
});

/**
 * GET: `{ runs:[{id,label,createdAt,config,summary}] (ใหม่→เก่า), latest:{...run, items} | null }`
 * `?id=N` → latest = run นั้น · `?limit=` (ค่าเริ่มต้น 50)
 */
export async function listRuns(table: RunTable, req: Request) {
  if (!TABLES.includes(table)) throw new Error('bad table');
  await ensure(table);
  const u = new URL(req.url);
  const limit = Math.min(200, Math.max(1, Number(u.searchParams.get('limit')) || 50));
  const id = Number(u.searchParams.get('id')) || null;
  const runs = await query(`SELECT id, label, created_at, config, summary FROM ${table} ORDER BY id DESC LIMIT $1`, [limit]);
  const one = id
    ? await query(`SELECT * FROM ${table} WHERE id = $1`, [id])
    : await query(`SELECT * FROM ${table} ORDER BY id DESC LIMIT 1`);
  return {
    runs: runs.rows.map((r) => toRun(r, false)),
    latest: one.rows[0] ? toRun(one.rows[0], true) : null,
  };
}

/** POST body = results JSON `{label, config, summary, items}` → `{id}` */
export async function saveRun(table: RunTable, body: any) {
  if (!TABLES.includes(table)) throw new Error('bad table');
  if (!body || typeof body !== 'object') throw new Error('body must be a JSON object');
  await ensure(table);
  const r = await query<{ id: number; created_at: string }>(
    `INSERT INTO ${table} (label, config, summary, items) VALUES ($1, $2, $3, $4) RETURNING id, created_at`,
    [
      String(body.label || `${table === 'eval_runs' ? 'eval' : 'load'}-${new Date().toISOString()}`).slice(0, 200),
      JSON.stringify(body.config ?? {}),
      JSON.stringify(body.summary ?? {}),
      JSON.stringify(Array.isArray(body.items) ? body.items : body.stages ?? []),
    ],
  );
  return { id: r.rows[0].id, createdAt: r.rows[0].created_at };
}

/** route handler กลางของ /api/admin/eval และ /api/admin/load */
export function runRoutes(table: RunTable) {
  return {
    async GET(req: Request) {
      const deny = requireRunAuth(req);
      if (deny) return deny;
      return NextResponse.json(await listRuns(table, req), { headers: { 'Cache-Control': 'no-store' } });
    },
    async POST(req: Request) {
      const deny = requireRunAuth(req);
      if (deny) return deny;
      let body: any;
      try {
        body = await req.json();
      } catch {
        return NextResponse.json({ error: 'invalid JSON' }, { status: 400 });
      }
      try {
        return NextResponse.json(await saveRun(table, body), { status: 201 });
      } catch (e: any) {
        return NextResponse.json({ error: String(e?.message || e) }, { status: 400 });
      }
    },
  };
}
