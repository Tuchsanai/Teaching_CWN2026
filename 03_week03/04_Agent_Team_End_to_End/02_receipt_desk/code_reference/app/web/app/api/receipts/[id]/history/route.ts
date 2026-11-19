/**
 * W17 · GET /api/receipts/{id}/history — ค่าเดิมที่ระบบอ่านและประวัติการแก้ · พนักงาน · หัวหน้า · เจ้าของ (ลูกค้า → 403)
 * FR-14 · FR-15 · NFR-10: ค่า ai_* (ไม่เคยถูกเขียนทับ) + ทุกแถวของ receipt_edits (ผู้แก้ + เวลา) + receipt_events
 */
import { OFFICE, requireUser } from '../../../_lib/auth';
import { query } from '../../../_lib/db';
import { handle, json, paramId } from '../../../_lib/http';
import type { IdContext } from '../../../_lib/http';
import { STATUS_LABEL, loadItems, loadReceipt } from '../../../_lib/receipts';
import type { ReceiptStatus } from '../../../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request, ctx: IdContext) => {
  const user = await requireUser(request, OFFICE);
  const id = await paramId(ctx);
  const row = await loadReceipt(user, id);
  const items = await loadItems(row.id);
  const edits = await query<{ field: string; old_value: string | null; new_value: string | null; edited_by: string; edited_at: Date }>(
    `SELECT e.field, e.old_value, e.new_value, u.display_name AS edited_by, e.edited_at
       FROM receipt_edits e JOIN users u ON u.id = e.edited_by
      WHERE e.receipt_id = $1 ORDER BY e.edited_at, e.id`,
    [row.id],
  );
  const events = await query<{ from_status: ReceiptStatus | null; to_status: ReceiptStatus; actor: string | null; created_at: Date }>(
    `SELECT ev.from_status, ev.to_status, u.display_name AS actor, ev.created_at
       FROM receipt_events ev LEFT JOIN users u ON u.id = ev.actor_id
      WHERE ev.receipt_id = $1 ORDER BY ev.created_at, ev.id`,
    [row.id],
  );
  return json({
    receiptId: row.id,
    original: {
      merchant: row.ai_merchant,
      receiptDate: row.ai_receipt_date,
      total: row.ai_total,
      totalConfidence: row.total_confidence,
      items: items.filter((i) => i.ai_name !== null || i.ai_price !== null).map((i) => ({ lineNo: i.line_no, name: i.ai_name, price: i.ai_price })),
    },
    current: {
      merchant: row.merchant,
      receiptDate: row.receipt_date,
      total: row.total,
      categoryId: row.category_id,
      categoryName: row.category_name,
      items: items.map((i) => ({ lineNo: i.line_no, name: i.name, price: i.price, removed: i.removed })),
    },
    enteredManually: row.entered_manually,
    edits: edits.map((e, idx) => ({
      seq: idx + 1,
      field: e.field,
      oldValue: e.old_value,
      newValue: e.new_value,
      editedBy: e.edited_by,
      editedAt: new Date(e.edited_at).toISOString(),
    })),
    events: events.map((e) => ({
      from: e.from_status,
      to: e.to_status,
      toLabel: STATUS_LABEL[e.to_status],
      actor: e.actor ?? 'ระบบ',
      at: new Date(e.created_at).toISOString(),
    })),
    confirmedBy: row.confirmed_by_name,
    confirmedAt: row.confirmed_at ? new Date(row.confirmed_at).toISOString() : null,
  });
});
