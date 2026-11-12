// GET /api/admin/load → {runs:[{id,label,createdAt,config,summary}], latest:{...,items}|null} (?id=N เลือก run)
//   latest.items = ขั้นของ load test [{users, n, errors, p50, p95, ttft_p50, ttft_p95, rtf, tokens_per_s, queue_max, ok}]
//   latest.summary = {mode, max_users_ok, thresholds, ...}
// POST /api/admin/load (cookie admin หรือ header x-eval-token) body = loadtest/results/<label>.json → {id} · ตาราง load_runs (CONTRACT_V3 §8)
import { runRoutes } from '@/lib/runs';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const r = runRoutes('load_runs');
export const GET = r.GET;
export const POST = r.POST;
