/**
 * W21 · GET /api/reports/review-time[?clientId=&from=YYYY-MM-DD&to=YYYY-MM-DD] — เวลาตรวจเฉลี่ยต่อใบ · หัวหน้า · เจ้าของ
 * FR-31 · NFR-09: review_seconds = เปิดใบ (GET /api/receipts/{id}) จนกดยืนยัน · เฉลี่ยต่อชุดและรวม
 */
import { requireUser } from '../../_lib/auth';
import { isUuid, query } from '../../_lib/db';
import { badRequest, handle, json, notFound } from '../../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const TARGET_SECONDS = 120; // NFR-09: ต้องน้อยกว่า 120 วินาที
const TEAM_GOAL_SECONDS = 40;

function round1(n: number | null): number | null {
  return n === null ? null : Math.round(n * 10) / 10;
}

export const GET = handle(async (request: Request) => {
  await requireUser(request, ['lead', 'owner']);
  const sp = new URL(request.url).searchParams;
  const where = [`r.status = 'confirmed'`, 'r.review_seconds IS NOT NULL'];
  const params: unknown[] = [];
  const clientId = sp.get('clientId');
  if (clientId) {
    if (!isUuid(clientId)) throw notFound();
    params.push(clientId);
    where.push(`r.client_id = $${params.length}`);
  }
  for (const [key, op] of [['from', '>='], ['to', '<']] as const) {
    const v = sp.get(key);
    if (!v) continue;
    if (!/^\d{4}-\d{2}-\d{2}$/.test(v)) throw badRequest(`${key} ต้องเป็น YYYY-MM-DD`);
    params.push(v);
    // ขอบวันตามเวลาไทย · to เป็นวันสุดท้ายที่นับ (รวม)
    where.push(
      key === 'from'
        ? `r.confirmed_at ${op} ($${params.length}::date)::timestamp AT TIME ZONE 'Asia/Bangkok'`
        : `r.confirmed_at ${op} ($${params.length}::date + 1)::timestamp AT TIME ZONE 'Asia/Bangkok'`,
    );
  }
  const whereSql = where.join(' AND ');
  const batches = await query<{
    batch_id: string; client_name: string; accepted_at: Date; receipts: number; avg: string | null; flagged_avg: string | null; normal_avg: string | null;
  }>(
    `SELECT r.batch_id, c.name AS client_name, b.accepted_at, count(*)::int AS receipts,
            avg(r.review_seconds) AS avg,
            avg(r.review_seconds) FILTER (WHERE r.flag_low_confidence OR r.flag_mismatch) AS flagged_avg,
            avg(r.review_seconds) FILTER (WHERE NOT (r.flag_low_confidence OR r.flag_mismatch)) AS normal_avg
       FROM receipts r JOIN batches b ON b.id = r.batch_id JOIN clients c ON c.id = r.client_id
      WHERE ${whereSql}
      GROUP BY r.batch_id, c.name, b.accepted_at
      ORDER BY b.accepted_at DESC`,
    params,
  );
  const [overall] = await query<{ receipts: number; avg: string | null }>(
    `SELECT count(*)::int AS receipts, avg(r.review_seconds) AS avg FROM receipts r WHERE ${whereSql}`,
    params,
  );
  const avg = overall?.avg != null ? Number(overall.avg) : null;
  return json({
    averageSeconds: round1(avg),
    receipts: overall?.receipts ?? 0,
    targetSeconds: TARGET_SECONDS,
    teamGoalSeconds: TEAM_GOAL_SECONDS,
    meetsTarget: avg === null ? null : avg < TARGET_SECONDS,
    batches: batches.map((b) => ({
      batchId: b.batch_id,
      clientName: b.client_name,
      acceptedAt: new Date(b.accepted_at).toISOString(),
      receipts: b.receipts,
      averageSeconds: round1(b.avg != null ? Number(b.avg) : null),
      flaggedAverageSeconds: round1(b.flagged_avg != null ? Number(b.flagged_avg) : null),
      normalAverageSeconds: round1(b.normal_avg != null ? Number(b.normal_avg) : null),
    })),
  });
});
