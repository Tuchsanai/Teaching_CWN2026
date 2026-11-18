// GET /api/admin/orders?status=&q= → { items:[{orderNo, customerName, phone, branch, deliveryDate, slot, total, status, createdAt, items:[...]}] }
// PATCH /api/admin/orders { orderNo, status } → เปลี่ยนสถานะ + เขียน order_status_history
import { NextResponse } from 'next/server';
import { query, tx } from '@/lib/db';
import { requireAdmin } from '../_auth';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const STATUSES =['received', 'preparing', 'shipping', 'delivered'];

export async function GET(req: Request) {
  const deny = requireAdmin();
  if (deny) return deny;
  const url = new URL(req.url);
  const status = url.searchParams.get('status');
  const q = url.searchParams.get('q')?.trim();
  const r = await query(
    `SELECT o.order_no, o.customer_name, o.phone, o.branch, o.delivery_date::text AS delivery_date, o.delivery_slot,
            (o.totals->>'total')::numeric AS total, o.status, o.created_at,
            COALESCE(json_agg(json_build_object('sku', oi.sku, 'name', p.name, 'qty', oi.qty, 'unit', p.unit)
                     ORDER BY oi.sku) FILTER (WHERE oi.sku IS NOT NULL), '[]') AS items
       FROM orders o
       LEFT JOIN order_items oi ON oi.order_id = o.id
       LEFT JOIN products p ON p.sku = oi.sku
      WHERE ($1::text IS NULL OR o.status = $1)
        AND ($2::text IS NULL OR o.order_no ILIKE '%' || $2 || '%' OR o.customer_name ILIKE '%' || $2 || '%' OR o.phone LIKE '%' || $2 || '%')
      GROUP BY o.id
      ORDER BY o.created_at DESC, o.id DESC
      LIMIT 100`,
    [status && STATUSES.includes(status) ? status : null, q || null],
  );
  const items = r.rows.map((o: any) => ({
    orderNo: o.order_no,
    customerName: o.customer_name,
    phone: o.phone,
    branch: o.branch,
    deliveryDate: o.delivery_date,
    slot: o.delivery_slot,
    total: Number(o.total) || 0,
    status: o.status,
    createdAt: o.created_at,
    items: o.items,
  }));
  return NextResponse.json({ items });
}

export async function PATCH(req: Request) {
  const deny = requireAdmin();
  if (deny) return deny;
  const body = await req.json().catch(() => null);
  const orderNo = typeof body?.orderNo === 'string' ? body.orderNo.trim() : '';
  const status = body?.status;
  if (!orderNo || !STATUSES.includes(status)) {
    return NextResponse.json({ error: 'ข้อมูลไม่ถูกต้อง (orderNo, status)' }, { status: 400 });
  }
  const out = await tx(async (c) => {
    const o = await c.query('SELECT id, status FROM orders WHERE order_no = $1 FOR UPDATE', [orderNo]);
    if (!o.rowCount) return null;
    const { id, status: prev } = o.rows[0];
    if (prev !== status) {
      await c.query('UPDATE orders SET status = $2 WHERE id = $1', [id, status]);
      await c.query('INSERT INTO order_status_history (order_id, status) VALUES ($1, $2)', [id, status]);
    }
    return { orderNo, status, previous: prev, changed: prev !== status };
  });
  if (!out) return NextResponse.json({ error: 'ไม่พบคำสั่งซื้อ' }, { status: 404 });
  return NextResponse.json(out);
}
