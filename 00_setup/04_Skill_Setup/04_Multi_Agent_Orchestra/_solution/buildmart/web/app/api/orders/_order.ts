// app/api/orders/_order.ts (B2) — อ่านคำสั่งซื้อ + ประวัติสถานะ (ใช้กับ /api/orders/[no] และ /api/track)
import { pool } from '@/lib/db';
import { STATUSES } from '../cart/_lib';

const labelOf = (s: string) => STATUSES.find((x) => x.code === s)?.label ?? s;

export async function getOrder(no: string) {
  const o = await pool.query(
    `SELECT id, order_no, session_id, customer_name, phone, address, branch, delivery_date::text AS delivery_date,
            delivery_slot, coupon, totals, status, created_at
       FROM orders WHERE order_no = $1`,
    [String(no).trim().toUpperCase()],
  );
  if (!o.rowCount) return null;
  const row = o.rows[0];
  const [items, hist] = await Promise.all([
    pool.query(
      `SELECT oi.sku, oi.qty, oi.unit_price AS "unitPrice", p.name, p.unit
         FROM order_items oi JOIN products p ON p.sku = oi.sku WHERE oi.order_id = $1 ORDER BY oi.sku`,
      [row.id],
    ),
    pool.query(
      'SELECT status, changed_at AS "changedAt" FROM order_status_history WHERE order_id = $1 ORDER BY changed_at, id',
      [row.id],
    ),
  ]);
  return {
    orderNo: row.order_no as string,
    sessionId: row.session_id as string | null,
    customerName: row.customer_name as string,
    phone: row.phone as string,
    address: row.address as string | null,
    branch: row.branch as string,
    deliveryDate: row.delivery_date as string,
    deliverySlot: row.delivery_slot as string,
    coupon: row.coupon as string | null,
    totals: row.totals,
    status: row.status as string,
    statusLabel: labelOf(row.status),
    createdAt: row.created_at,
    items: items.rows,
    history: hist.rows.map((h: any) => ({ ...h, label: labelOf(h.status) })),
  };
}
