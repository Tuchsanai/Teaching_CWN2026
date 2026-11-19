/**
 * W15 · POST /api/receipts/{id}/confirm — ยืนยันใบ · พนักงาน · หัวหน้า (เจ้าของ · ลูกค้า → 403)
 *
 * body: { totalChecked: true, categoryId: "<uuid>", ...ช่องแก้แบบเดียวกับ PATCH (ไม่ใส่ก็ได้) }
 * ทั้งหมดในธุรกรรมเดียว (ไม่ผ่านข้อใด → ไม่มีอะไรถูกบันทึก ค่าที่แก้ใน body นี้ก็ไม่ถูกบันทึก ให้ PATCH ก่อนถ้าต้องการเก็บ)
 *   สถานะต้องเป็น review หรือ unreadable (FR-12 · FR-17)        → 409 not_editable
 *   totalChecked ต้องเป็น true ("เทียบยอดรวมกับรูปแล้ว")          → 422 total_not_checked
 *   ต้องมีหมวดรายจ่าย (FR-29)                                  → 422 category_required
 *   BR-06 rules.checkConfirmTotal(total)                       → 422 total_invalid
 *   ต้องมีวันที่บนใบ (ใช้นับเดือน BR-14)                          → 422 date_required
 *   ใบติดธงต้องถูกเปิดดูรายละเอียดก่อน (GET /api/receipts/{id})   → 409 review_not_opened
 * ผ่าน → status = confirmed · confirmed_by · confirmed_at · review_seconds (FR-13 · FR-31) + receipt_events
 */
import rules from '../../../../../lib/rules';
import { EDITORS, requireUser } from '../../../_lib/auth';
import { dbNow, isUuid, transaction } from '../../../_lib/db';
import { applyEdits, assertEditable, hasEditFields } from '../../../_lib/edits';
import { ApiError, handle, json, paramId, readJson, ruleError } from '../../../_lib/http';
import type { IdContext } from '../../../_lib/http';
import { addEvent, loadItems, loadReceipt, officeDetailView } from '../../../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const POST = handle(async (request: Request, ctx: IdContext) => {
  const user = await requireUser(request, EDITORS);
  const id = await paramId(ctx);
  const body = await readJson(request, true);

  await transaction(async (client) => {
    let row = await loadReceipt(user, id, { client, forUpdate: true });
    if (row.status === 'confirmed') {
      throw new ApiError(409, 'not_editable', 'ใบนี้ยืนยันแล้ว', { status: row.status });
    }
    assertEditable(row);

    if (hasEditFields(body)) {
      const items = await loadItems(row.id, client);
      await applyEdits(client, row, items, body, user);
      row = await loadReceipt(user, id, { client });
    }

    if (body.totalChecked !== true) {
      throw new ApiError(422, 'total_not_checked', 'กรุณาติ๊ก "เทียบยอดรวมกับรูปแล้ว" ก่อนยืนยัน');
    }

    const categoryId = row.category_id;
    if (!categoryId || !isUuid(categoryId)) {
      throw new ApiError(422, 'category_required', 'กรุณาเลือกหมวดรายจ่ายก่อนยืนยัน');
    }

    // BR-06
    const totalRule = rules.checkConfirmTotal(row.total);
    if (!totalRule.ok) throw ruleError(totalRule, { status: row.status });

    if (!row.receipt_date) {
      throw new ApiError(422, 'date_required', 'กรุณากรอกวันที่บนใบเสร็จก่อนยืนยัน');
    }

    // FR-12: ใบติดธงต้องเปิดดูรายละเอียดทุกช่องก่อน
    if ((row.flag_low_confidence || row.flag_mismatch) && !row.review_opened_at) {
      throw new ApiError(409, 'review_not_opened', 'ใบติดธงต้องเปิดดูรายละเอียดทุกช่องก่อนยืนยัน');
    }

    await client.query(
      `UPDATE receipts
          SET status = 'confirmed', confirmed_by = $2, confirmed_at = clock_timestamp(),
              review_seconds = CASE WHEN review_opened_at IS NULL THEN NULL
                                    ELSE greatest(0, round(extract(epoch FROM clock_timestamp() - review_opened_at)))::int END
        WHERE id = $1`,
      [row.id, user.id],
    );
    await addEvent(client, row.id, row.status, 'confirmed', user.id);
  });

  const row = await loadReceipt(user, id);
  const items = await loadItems(row.id);
  return json({ ok: true, receipt: officeDetailView(row, items, user, await dbNow()) });
});
