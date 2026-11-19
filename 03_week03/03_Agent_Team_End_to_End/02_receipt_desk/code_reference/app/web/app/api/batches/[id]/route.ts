/**
 * W9 · GET /api/batches/{id} — สถานะทุกใบและจำนวนต่อสถานะ · พนักงาน · หัวหน้า · เจ้าของ (ลูกค้า → 403)
 * ยอดตรวจนับของชุด (FR-08): accepted = batches.receipt_count · sum = ผลรวมทุกสถานะ · diff = accepted − sum
 */
import { OFFICE, requireUser } from '../../_lib/auth';
import { dbNow, isUuid, query, queryOne } from '../../_lib/db';
import { handle, json, notFound, paramId } from '../../_lib/http';
import type { IdContext } from '../../_lib/http';
import { RECEIPT_SELECT, STATUSES, officeListView } from '../../_lib/receipts';
import type { ReceiptRow } from '../../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request, ctx: IdContext) => {
  const user = await requireUser(request, OFFICE);
  const id = await paramId(ctx);
  if (!isUuid(id)) throw notFound();
  const batch = await queryOne<{
    id: string; client_id: string; client_code: string; client_name: string; uploaded_by_name: string;
    priority: 'normal' | 'urgent'; urgent_set_at: Date | null; urgent_set_by_name: string | null;
    receipt_count: number; accepted_at: Date;
  }>(
    `SELECT b.id, b.client_id, c.code AS client_code, c.name AS client_name, u.display_name AS uploaded_by_name,
            b.priority, b.urgent_set_at, us.display_name AS urgent_set_by_name, b.receipt_count, b.accepted_at
       FROM batches b
       JOIN clients c ON c.id = b.client_id
       JOIN users u ON u.id = b.uploaded_by
       LEFT JOIN users us ON us.id = b.urgent_set_by
      WHERE b.id = $1`,
    [id],
  );
  if (!batch) throw notFound();
  const rows = await query<ReceiptRow>(`${RECEIPT_SELECT} WHERE r.batch_id = $1 ORDER BY r.accepted_at, r.file_name, r.id`, [id]);
  const now = await dbNow();
  const counts = Object.fromEntries(STATUSES.map((s) => [s, 0])) as Record<string, number>;
  for (const r of rows) counts[r.status]++;
  const sum = rows.length;
  return json({
    batch: {
      id: batch.id,
      clientId: batch.client_id,
      clientCode: batch.client_code,
      clientName: batch.client_name,
      uploadedBy: batch.uploaded_by_name,
      priority: batch.priority,
      urgentSetAt: batch.urgent_set_at ? new Date(batch.urgent_set_at).toISOString() : null,
      urgentSetBy: batch.urgent_set_by_name,
      acceptedAt: new Date(batch.accepted_at).toISOString(),
      accepted: batch.receipt_count,
      counts,
      sum,
      diff: batch.receipt_count - sum,
      canSetUrgent: user.role === 'lead' && batch.priority === 'normal',
    },
    receipts: rows.map((r) => officeListView(r, now)),
  });
});
