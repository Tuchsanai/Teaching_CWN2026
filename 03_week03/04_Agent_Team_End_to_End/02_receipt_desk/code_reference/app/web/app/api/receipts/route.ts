/**
 * W11 · GET /api/receipts — รายการใบ · ทุกบทบาท
 * ตัวกรอง: status (คั่นด้วยจุลภาคได้) · flagged=true · clientId · overdue=true · batchId · limit · offset
 *
 * - ลูกค้า: กรอง r.client_id = ร้านของ session ที่ SQL เสมอ · ส่ง clientId ร้านอื่น → 404 not_found
 *   ได้เฉพาะ ชื่อไฟล์ · เวลาที่รับ · สถานะ ("รับแล้ว รอสำนักงานตรวจ") และตัวเลขเฉพาะใบที่ยืนยันแล้ว
 *   ตัวกรอง flagged / overdue ไม่ใช้กับลูกค้า (ธงมาจากตัวเลขที่ยังไม่ยืนยัน)
 * - overdue=true: SQL ใช้ accepted_at < rules.overdueCutoff(now) แล้วยืนยันซ้ำด้วย rules.listOverdue (BR-13)
 */
import rules from '../../../lib/rules';
import { requireUser } from '../_lib/auth';
import { dbNow, isUuid, query } from '../_lib/db';
import { badRequest, boolParam, handle, json, notFound } from '../_lib/http';
import { RECEIPT_SELECT, STATUSES, clientView, officeListView } from '../_lib/receipts';
import type { ReceiptRow } from '../_lib/receipts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request) => {
  const user = await requireUser(request);
  const isClient = user.role === 'client';
  const sp = new URL(request.url).searchParams;
  const now = await dbNow();

  const where: string[] = [];
  const params: unknown[] = [];
  const add = (sql: string, value: unknown) => {
    params.push(value);
    where.push(sql.replace('$?', `$${params.length}`));
  };

  // ขอบเขตร้าน
  const clientId = sp.get('clientId') || sp.get('client_id');
  if (isClient) {
    if (clientId && clientId !== user.clientId) throw notFound();
    add('r.client_id = $?', user.clientId);
  } else if (clientId) {
    if (!isUuid(clientId)) throw notFound();
    add('r.client_id = $?', clientId);
  }

  const batchId = sp.get('batchId');
  if (batchId) {
    if (!isUuid(batchId)) throw notFound();
    add('r.batch_id = $?', batchId);
  }

  const statusParam = sp.get('status');
  if (statusParam) {
    const wanted = statusParam.split(',').map((s) => s.trim()).filter(Boolean);
    const statuses = new Set<string>();
    for (const s of wanted) {
      if (isClient) {
        if (s === 'received') ['queued', 'processing', 'review', 'unreadable'].forEach((x) => statuses.add(x));
        else if (s === 'confirmed') statuses.add(s);
        else throw badRequest('ลูกค้ากรองได้เฉพาะ status=received หรือ confirmed');
      } else if ((STATUSES as readonly string[]).includes(s)) statuses.add(s);
      else throw badRequest(`status ไม่ถูกต้อง: ${s}`);
    }
    if (statuses.size) add('r.status = ANY($?::text[])', [...statuses]);
  }

  const flagged = isClient ? undefined : boolParam(sp.get('flagged'));
  if (flagged === true) where.push('(r.flag_low_confidence OR r.flag_mismatch)');
  if (flagged === false) where.push('NOT (r.flag_low_confidence OR r.flag_mismatch)');

  const overdue = isClient ? undefined : boolParam(sp.get('overdue'));
  if (overdue === true) {
    where.push(`b.priority = 'normal'`, `r.status IN ('queued', 'processing')`);
    add('r.accepted_at < $?', rules.overdueCutoff(now));
  }

  const limit = Math.min(1000, Math.max(1, Number(sp.get('limit')) || 200));
  const offset = Math.max(0, Number(sp.get('offset')) || 0);
  const whereSql = where.length ? `WHERE ${where.join(' AND ')}` : '';
  const order = overdue === true ? 'r.accepted_at ASC, r.id' : 'r.accepted_at DESC, r.file_name, r.id';

  const [countRow] = await query<{ n: number }>(
    `SELECT count(*)::int AS n FROM receipts r JOIN batches b ON b.id = r.batch_id ${whereSql}`,
    params,
  );
  let rows = await query<ReceiptRow>(
    `${RECEIPT_SELECT} ${whereSql} ORDER BY ${order} LIMIT $${params.length + 1} OFFSET $${params.length + 2}`,
    [...params, limit, offset],
  );
  let total = countRow?.n ?? 0;

  if (overdue === true) {
    // ตัดสินขั้นสุดท้ายด้วยโมดูลกฎ (เรียงจากรอนานที่สุด)
    const listed = rules.listOverdue(rows.map((r) => ({ ...r, acceptedAt: r.accepted_at })), now);
    total -= rows.length - listed.length;
    rows = listed;
  }

  return json({
    count: total,
    limit,
    offset,
    receipts: isClient ? rows.map((r) => clientView(r)) : rows.map((r) => officeListView(r, now)),
  });
});
