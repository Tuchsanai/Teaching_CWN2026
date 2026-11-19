/**
 * W23 · GET /api/queue — ใบงานปกติที่ค้าง · เพดาน · งานด่วนที่ใช้ไปวันนี้ · จำนวน Worker · พนักงาน · หัวหน้า · เจ้าของ
 * ตัวเลขทุกตัวคิดด้วย rules.ts: BR-09 (rules.bangkokDayRange + canSetUrgent) · BR-11/12 (hasQueueRoom · effectiveWorkers ·
 * retryAfterMinutes) · BR-13 (overdueCutoff)
 */
import rules, { LIMITS, bangkokDayRange } from '../../../lib/rules';
import { OFFICE, requireUser } from '../_lib/auth';
import { dbNow, queryOne } from '../_lib/db';
import { handle, json } from '../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request) => {
  await requireUser(request, OFFICE);
  const now = await dbNow();
  const { start, end } = bangkokDayRange(now);
  const row = await queryOne<{
    pending_normal: number; queued_normal: number; processing_normal: number; pending_urgent: number;
    urgent_today: number; overdue: number; workers_value: string | null; workers_updated_at: Date | null;
  }>(
    `SELECT
       (SELECT count(*)::int FROM receipts r JOIN batches b ON b.id = r.batch_id
          WHERE b.priority = 'normal' AND r.status IN ('queued', 'processing')) AS pending_normal,
       (SELECT count(*)::int FROM receipts r JOIN batches b ON b.id = r.batch_id
          WHERE b.priority = 'normal' AND r.status = 'queued') AS queued_normal,
       (SELECT count(*)::int FROM receipts r JOIN batches b ON b.id = r.batch_id
          WHERE b.priority = 'normal' AND r.status = 'processing') AS processing_normal,
       (SELECT count(*)::int FROM receipts r JOIN batches b ON b.id = r.batch_id
          WHERE b.priority = 'urgent' AND r.status IN ('queued', 'processing')) AS pending_urgent,
       (SELECT count(*)::int FROM batches
          WHERE priority = 'urgent' AND urgent_set_at >= $1 AND urgent_set_at < $2) AS urgent_today,
       (SELECT count(*)::int FROM receipts r JOIN batches b ON b.id = r.batch_id
          WHERE b.priority = 'normal' AND r.status IN ('queued', 'processing') AND r.accepted_at < $3) AS overdue,
       (SELECT value FROM system_state WHERE key = 'workers_alive') AS workers_value,
       (SELECT updated_at FROM system_state WHERE key = 'workers_alive') AS workers_updated_at`,
    [start, end, rules.overdueCutoff(now)],
  );
  const pending = row?.pending_normal ?? 0;
  const raw = row?.workers_value != null && Number.isFinite(Number(row.workers_value)) ? Number(row.workers_value) : null;
  const workers = rules.effectiveWorkers(raw, row?.workers_updated_at ?? null, now);
  const urgentToday = row?.urgent_today ?? 0;
  const room = Math.max(0, LIMITS.NORMAL_QUEUE_CAP - pending);
  return json({
    normal: {
      pending,
      queued: row?.queued_normal ?? 0,
      processing: row?.processing_normal ?? 0,
      limit: LIMITS.NORMAL_QUEUE_CAP,
      room,
      acceptsBatchOf: room,
      full: !rules.hasQueueRoom(pending, 1),
      retryAfterMinutesIfFull: rules.hasQueueRoom(pending, 1) ? null : rules.retryAfterMinutes(pending, 1, workers),
    },
    urgent: {
      pending: row?.pending_urgent ?? 0,
      usedToday: urgentToday,
      limitPerDay: LIMITS.URGENT_MAX_PER_DAY,
      remainingToday: Math.max(0, LIMITS.URGENT_MAX_PER_DAY - urgentToday),
      canSetMore: rules.canSetUrgent(urgentToday),
      maxReceipts: LIMITS.URGENT_MAX_RECEIPTS,
    },
    workers: {
      alive: raw,
      updatedAt: row?.workers_updated_at ? new Date(row.workers_updated_at).toISOString() : null,
      usedForEstimate: workers,
      minRatePerMinute: LIMITS.READS_PER_MINUTE_PER_WORKER * workers,
    },
    overdue: row?.overdue ?? 0,
    now: now.toISOString(),
  });
});
