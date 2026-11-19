/**
 * W20 · GET /api/reports/reconcile[?batchId=|clientId=] — ยอดตรวจนับ · พนักงาน · หัวหน้า · เจ้าของ (ลูกค้า → 403)
 * FR-08 · NFR-06: accepted = ผลรวม batches.receipt_count (ใบที่ตอบว่ารับแล้ว) · sum = ผลรวมจำนวนใบทุกสถานะ · diff = accepted − sum (ต้องเป็น 0)
 */
import { OFFICE, requireUser } from '../../_lib/auth';
import { isUuid, query, queryOne } from '../../_lib/db';
import { handle, json, notFound } from '../../_lib/http';
import { STATUSES } from '../../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request) => {
  await requireUser(request, OFFICE);
  const sp = new URL(request.url).searchParams;
  const batchId = sp.get('batchId');
  const clientId = sp.get('clientId');
  let filter = '';
  const params: unknown[] = [];
  if (batchId) {
    if (!isUuid(batchId)) throw notFound();
    params.push(batchId);
    filter = 'id = $1';
  } else if (clientId) {
    if (!isUuid(clientId)) throw notFound();
    params.push(clientId);
    filter = 'client_id = $1';
  }
  const accepted = await queryOne<{ n: number; batches: number }>(
    `SELECT coalesce(sum(receipt_count), 0)::int AS n, count(*)::int AS batches FROM batches ${filter ? `WHERE ${filter}` : ''}`,
    params,
  );
  if (batchId && !accepted?.batches) throw notFound();
  const rows = await query<{ status: string; n: number }>(
    `SELECT r.status, count(*)::int AS n FROM receipts r
      ${filter ? `WHERE r.${filter === 'id = $1' ? 'batch_id' : 'client_id'} = $1` : ''}
      GROUP BY r.status`,
    params,
  );
  const counts = Object.fromEntries(STATUSES.map((s) => [s, 0])) as Record<string, number>;
  for (const r of rows) counts[r.status] = r.n;
  const sum = STATUSES.reduce((n, s) => n + counts[s], 0);
  const acceptedCount = accepted?.n ?? 0;
  return json({
    scope: batchId ? { batchId } : clientId ? { clientId } : { office: true },
    batches: accepted?.batches ?? 0,
    accepted: acceptedCount,
    counts,
    sum,
    diff: acceptedCount - sum,
  });
});
