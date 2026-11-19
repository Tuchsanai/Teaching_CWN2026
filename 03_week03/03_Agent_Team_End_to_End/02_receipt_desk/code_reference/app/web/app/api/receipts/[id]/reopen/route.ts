/**
 * W16 · POST /api/receipts/{id}/reopen — เปิดใบที่ยืนยันแล้วกลับเป็นรอตรวจ · หัวหน้าทีมเท่านั้น (คนอื่น → 403)
 * body (ไม่ใส่ก็ได้): { reason?: string }
 * ใบต้องเป็น confirmed (ไม่ใช่ → 409 not_confirmed) · เก็บประวัติใน receipt_events และ receipt_edits (A-15)
 */
import { LEAD_ONLY, requireUser } from '../../../_lib/auth';
import { dbNow, transaction } from '../../../_lib/db';
import { ApiError, handle, json, paramId, readJson } from '../../../_lib/http';
import type { IdContext } from '../../../_lib/http';
import { addEvent, loadItems, loadReceipt, officeDetailView } from '../../../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const POST = handle(async (request: Request, ctx: IdContext) => {
  const user = await requireUser(request, LEAD_ONLY);
  const id = await paramId(ctx);
  const body = await readJson(request, true);
  const reason = typeof body.reason === 'string' ? body.reason.trim().slice(0, 500) : '';

  await transaction(async (client) => {
    const row = await loadReceipt(user, id, { client, forUpdate: true });
    if (row.status !== 'confirmed') {
      throw new ApiError(409, 'not_confirmed', 'เปิดกลับได้เฉพาะใบที่ยืนยันแล้ว', { status: row.status });
    }
    await client.query(
      `UPDATE receipts
          SET status = 'review', confirmed_by = NULL, confirmed_at = NULL,
              review_opened_at = NULL, review_seconds = NULL
        WHERE id = $1`,
      [row.id],
    );
    await addEvent(client, row.id, 'confirmed', 'review', user.id);
    await client.query(
      `INSERT INTO receipt_edits (receipt_id, field, old_value, new_value, edited_by, edited_at)
       VALUES ($1, 'status', 'confirmed', $2, $3, clock_timestamp())`,
      [row.id, reason ? `review (${reason})` : 'review', user.id],
    );
  });

  const row = await loadReceipt(user, id);
  const items = await loadItems(row.id);
  return json({ ok: true, receipt: officeDetailView(row, items, user, await dbNow()) });
});
