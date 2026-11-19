/**
 * W10 · POST /api/batches/{id}/urgent — ตั้งงานด่วน · หัวหน้าทีมเท่านั้น (คนอื่น → 403 forbidden · FR-19)
 *
 * ธุรกรรมเดียว + LOCK TABLE batches (SHARE ROW EXCLUSIVE) เพื่อให้โควตาต่อวันนับถูกเมื่อกดพร้อมกัน
 *   BR-08  rules.checkUrgentSize(receipt_count)  → 422 urgent_too_large (ชุดยังเป็นงานปกติ)
 *   BR-09  rules.checkUrgentQuota(ใช้ไปวันนี้)     → 409 urgent_quota  (นับในวันปฏิทินไทยจาก rules.bangkokDayRange)
 * ชุดที่เป็นงานด่วนอยู่แล้ว → 200 (เรียกซ้ำได้ ไม่กินโควตา)
 * dispatcher (B05) เห็น priority = urgent แล้วส่ง G5 / ส่งใบที่ยังรอก่อนเอง
 */
import rules, { LIMITS, bangkokDayRange } from '../../../../../lib/rules';
import { LEAD_ONLY, requireUser } from '../../../_lib/auth';
import { isUuid, transaction } from '../../../_lib/db';
import { handle, json, notFound, paramId, ruleError } from '../../../_lib/http';
import type { IdContext } from '../../../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const POST = handle(async (request: Request, ctx: IdContext) => {
  const user = await requireUser(request, LEAD_ONLY);
  const id = await paramId(ctx);
  if (!isUuid(id)) throw notFound();

  const result = await transaction(async (client) => {
    await client.query(`SET LOCAL lock_timeout = '30s'`);
    await client.query('LOCK TABLE batches IN SHARE ROW EXCLUSIVE MODE');
    const { rows: [batch] } = await client.query<{
      id: string; priority: string; receipt_count: number; urgent_set_at: Date | null;
    }>('SELECT id, priority, receipt_count, urgent_set_at FROM batches WHERE id = $1 FOR UPDATE', [id]);
    if (!batch) throw notFound();

    const { rows: [clock] } = await client.query<{ now: Date }>('SELECT clock_timestamp() AS now');
    const now = new Date(clock.now);
    const { start, end } = bangkokDayRange(now);
    const countToday = async () => {
      const { rows: [u] } = await client.query<{ n: number }>(
        `SELECT count(*)::int AS n FROM batches
          WHERE priority = 'urgent' AND urgent_set_at >= $1 AND urgent_set_at < $2`,
        [start, end],
      );
      return u.n;
    };

    if (batch.priority === 'urgent') {
      return { already: true, urgentSetAt: batch.urgent_set_at, usedToday: await countToday(), receiptCount: batch.receipt_count };
    }

    // BR-08
    const size = rules.checkUrgentSize(batch.receipt_count);
    if (!size.ok) throw ruleError(size, { priority: 'normal' });

    // BR-09
    const used = await countToday();
    const quota = rules.checkUrgentQuota(used);
    if (!quota.ok) throw ruleError(quota, { priority: 'normal', usedToday: used });

    await client.query(
      `UPDATE batches SET priority = 'urgent', urgent_set_by = $2, urgent_set_at = $3 WHERE id = $1`,
      [id, user.id, now],
    );
    return { already: false, urgentSetAt: now, usedToday: used + 1, receiptCount: batch.receipt_count };
  });

  return json({
    batchId: id,
    priority: 'urgent',
    alreadyUrgent: result.already,
    urgentSetAt: result.urgentSetAt ? new Date(result.urgentSetAt).toISOString() : null,
    receiptCount: result.receiptCount,
    usedToday: result.usedToday,
    limitPerDay: LIMITS.URGENT_MAX_PER_DAY,
    message: result.already ? 'ชุดนี้เป็นงานด่วนอยู่แล้ว' : 'ตั้งเป็นงานด่วนแล้ว',
  });
});
