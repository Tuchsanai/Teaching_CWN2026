/**
 * W12 · GET   /api/receipts/{id} — รายละเอียดใบ · ทุกบทบาท (ลูกค้า: ร้านตัวเอง · ไม่มีตัวเลขก่อนยืนยัน · ร้านอื่น 404)
 * W14 · PATCH /api/receipts/{id} — แก้ค่า / พิมพ์เองสำหรับใบอ่านไม่ได้ · พนักงาน · หัวหน้า (เจ้าของ · ลูกค้า → 403)
 *
 * GET โดยพนักงาน/หัวหน้ากับใบ review · unreadable บันทึก review_opened_at = เวลาเปิด (FR-31 เริ่มจับเวลาตรวจ ·
 *   และเป็นหลักฐานว่าเปิดดูรายละเอียดแล้วก่อนยืนยันใบติดธง FR-12)
 * PATCH body: { merchant?, receiptDate?, total?, categoryId?, items?: [{ lineNo?, name?, price?, removed? }] }
 *   แก้ได้เมื่อสถานะ review หรือ unreadable · ยืนยันแล้ว → 409 not_editable (A-15 ต้องให้หัวหน้าเปิดกลับ)
 *   ค่า ai_* ไม่ถูกแตะ · ทุกช่องที่เปลี่ยนมี 1 แถวใน receipt_edits (NFR-10)
 */
import { EDITORS, requireUser } from '../../_lib/auth';
import { dbNow, query, transaction } from '../../_lib/db';
import { applyEdits, assertEditable } from '../../_lib/edits';
import { handle, json, paramId, readJson } from '../../_lib/http';
import type { IdContext } from '../../_lib/http';
import { clientView, loadItems, loadReceipt, officeDetailView } from '../../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request, ctx: IdContext) => {
  const user = await requireUser(request);
  const id = await paramId(ctx);
  const row = await loadReceipt(user, id);
  if (user.role === 'client') {
    const items = row.status === 'confirmed' ? await loadItems(row.id) : null;
    return json({ receipt: clientView(row, items) });
  }
  if ((user.role === 'staff' || user.role === 'lead') && (row.status === 'review' || row.status === 'unreadable')) {
    const [opened] = await query<{ review_opened_at: Date }>(
      `UPDATE receipts SET review_opened_at = clock_timestamp()
        WHERE id = $1 AND status IN ('review', 'unreadable') RETURNING review_opened_at`,
      [row.id],
    );
    if (opened) row.review_opened_at = opened.review_opened_at;
  }
  const items = await loadItems(row.id);
  return json({ receipt: officeDetailView(row, items, user, await dbNow()) });
});

export const PATCH = handle(async (request: Request, ctx: IdContext) => {
  const user = await requireUser(request, EDITORS);
  const id = await paramId(ctx);
  const body = await readJson(request);
  const changes = await transaction(async (client) => {
    const row = await loadReceipt(user, id, { client, forUpdate: true });
    assertEditable(row);
    const items = await loadItems(row.id, client);
    return (await applyEdits(client, row, items, body, user)).changes;
  });
  const row = await loadReceipt(user, id);
  const items = await loadItems(row.id);
  return json({ changed: changes.map((c) => c.field), receipt: officeDetailView(row, items, user, await dbNow()) });
});
