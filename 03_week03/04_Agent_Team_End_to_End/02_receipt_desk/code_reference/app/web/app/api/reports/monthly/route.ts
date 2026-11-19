/**
 * W18 · GET /api/reports/monthly?clientId=&month=YYYY-MM — ไฟล์สรุปรายเดือน CSV · พนักงาน · หัวหน้า · เจ้าของ (ลูกค้า → 403)
 * FR-28 · BR-14: เฉพาะใบที่ยืนยันแล้ว นับเดือนตามวันที่บนใบ (rules.monthBounds + rules.summarizeMonth)
 * - CSV UTF-8 มี BOM (เปิดใน Excel ภาษาไทยได้) · ไม่มีใบ → มีแต่หัวตาราง (E-06)
 * - ยอดรวมและจำนวนใบอยู่ใน header X-Report-Total · X-Report-Count
 * - ?format=json → ตัวอย่างก่อนดาวน์โหลด { total, count, byCategory, receipts }
 */
import { OFFICE, clientExists, requireUser } from '../../_lib/auth';
import { isUuid, queryOne } from '../../_lib/db';
import { badRequest, handle, json, notFound } from '../../_lib/http';
import { confirmedInMonth, parseMonth, summarize } from '../_month';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const HEADER = ['receipt_date', 'merchant', 'category', 'total', 'file_name', 'confirmed_by', 'confirmed_at', 'receipt_id'];

function csvCell(value: string | null, text = true): string {
  let v = value ?? '';
  // กันสูตรใน Excel (CSV injection) เฉพาะช่องข้อความ
  if (text && /^[=+\-@\t\r]/.test(v)) v = `'${v}`;
  return /[",\r\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
}

export const GET = handle(async (request: Request) => {
  await requireUser(request, OFFICE);
  const sp = new URL(request.url).searchParams;
  const clientId = sp.get('clientId') || sp.get('client_id');
  if (!clientId) throw badRequest('ต้องระบุ clientId');
  if (!isUuid(clientId) || !(await clientExists(clientId))) throw notFound();
  const month = parseMonth(sp.get('month'));

  const rows = await confirmedInMonth(clientId, month);
  const summary = summarize(rows, month);

  if (sp.get('format') === 'json') {
    return json({
      clientId,
      month,
      count: summary.count,
      total: summary.total,
      byCategory: summary.byCategory,
      receipts: rows.map((r) => ({
        id: r.id,
        receiptDate: r.receipt_date,
        merchant: r.merchant,
        categoryName: r.category_name,
        total: r.total,
        fileName: r.file_name,
        confirmedBy: r.confirmed_by_name,
        confirmedAt: r.confirmed_at ? new Date(r.confirmed_at).toISOString() : null,
      })),
    });
  }

  const client = await queryOne<{ code: string }>('SELECT code FROM clients WHERE id = $1', [clientId]);
  const lines = [HEADER.join(',')];
  for (const r of rows) {
    lines.push(
      [
        csvCell(r.receipt_date, false),
        csvCell(r.merchant),
        csvCell(r.category_name),
        csvCell(r.total, false),
        csvCell(r.file_name),
        csvCell(r.confirmed_by_name),
        csvCell(r.confirmed_at ? new Date(r.confirmed_at).toISOString() : null, false),
        csvCell(r.id, false),
      ].join(','),
    );
  }
  const body = '﻿' + lines.join('\r\n') + '\r\n';
  const fileName = `receiptdesk-${client?.code ?? 'client'}-${month}.csv`;
  return new Response(body, {
    status: 200,
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': `attachment; filename="${fileName}"`,
      'Cache-Control': 'no-store',
      'X-Report-Month': month,
      'X-Report-Count': String(summary.count),
      'X-Report-Total': summary.total,
    },
  });
});
