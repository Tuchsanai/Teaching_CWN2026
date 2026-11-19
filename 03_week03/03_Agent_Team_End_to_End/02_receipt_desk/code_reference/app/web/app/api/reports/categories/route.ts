/**
 * W19 · GET /api/reports/categories?month=YYYY-MM[&clientId=] — ยอดแยกหมวดของร้าน (FR-29 · BR-14)
 * - ลูกค้า: ร้านตัวเองเสมอ (ส่ง clientId ร้านอื่น → 404) · เฉพาะใบที่ยืนยันแล้ว (FR-25)
 * - สำนักงาน (พนักงาน · หัวหน้า · เจ้าของ): ต้องระบุ clientId
 * ทุกหมวดแสดงครบแม้ยอด 0.00 · ผลรวมทุกหมวด = ยอดรวมของเดือน (E-05 = E-02)
 */
import { satangToBaht } from '../../../../lib/rules';
import { clientExists, requireUser } from '../../_lib/auth';
import { isUuid, query } from '../../_lib/db';
import { badRequest, handle, json, notFound } from '../../_lib/http';
import { confirmedInMonth, parseMonth, summarize } from '../_month';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const GET = handle(async (request: Request) => {
  const user = await requireUser(request);
  const sp = new URL(request.url).searchParams;
  const requested = sp.get('clientId') || sp.get('client_id');
  let clientId: string;
  if (user.role === 'client') {
    if (requested && requested !== user.clientId) throw notFound();
    clientId = user.clientId as string;
  } else {
    if (!requested) throw badRequest('ต้องระบุ clientId');
    if (!isUuid(requested) || !(await clientExists(requested))) throw notFound();
    clientId = requested;
  }
  const month = parseMonth(sp.get('month'));

  const rows = await confirmedInMonth(clientId, month);
  const summary = summarize(rows, month);
  const categories = await query<{ id: string; name: string }>('SELECT id, name FROM categories ORDER BY name');
  const order = ['วัตถุดิบ', 'ค่าแก๊ส', 'ค่าน้ำแข็ง', 'อื่น ๆ'];
  categories.sort((a, b) => (order.indexOf(a.name) + 1 || 99) - (order.indexOf(b.name) + 1 || 99));

  const listed = categories.map((c) => {
    const s = summary.byCategory[c.id];
    return { id: c.id, name: c.name, count: s?.count ?? 0, total: s ? s.total : '0.00' };
  });
  const categorizedSatang = Object.values(summary.byCategory).reduce((n, c) => n + c.totalSatang, 0);
  const uncategorizedSatang = summary.totalSatang - categorizedSatang;

  return json({
    clientId,
    month,
    count: summary.count,
    total: summary.total,
    categories: listed,
    ...(uncategorizedSatang !== 0 ? { uncategorized: satangToBaht(uncategorizedSatang) } : {}),
  });
});
