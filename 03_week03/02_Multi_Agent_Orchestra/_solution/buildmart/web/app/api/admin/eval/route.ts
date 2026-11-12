// GET /api/admin/eval → {runs:[{id,label,createdAt,config,summary}], latest:{...,items}|null} (?id=N เลือก run)
// POST /api/admin/eval (cookie admin หรือ header x-eval-token) body = eval/results.json → {id} · ตาราง eval_runs (v3 · CONTRACT_V3 §5–§6)
import { runRoutes } from '@/lib/runs';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const r = runRoutes('eval_runs');
export const GET = r.GET;
export const POST = r.POST;
