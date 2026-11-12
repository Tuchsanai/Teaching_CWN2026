// GET /api/admin/dashboard → ยอดขายวันนี้/7 วัน (รายวัน) · 5 สินค้าขายดี · สถานะคำสั่งซื้อ · จำนวนใน chat.dlq · สต็อกต่ำ
// timezone ของ DB = Asia/Bangkok → current_date / created_at::date เป็นวันไทยแล้ว
import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { checkQueue, Q } from '@/lib/amqp';
import { requireAdmin } from '../_auth';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const deny = requireAdmin();
  if (deny) return deny;

  const [days, top, byStatus, low, unread, dlq] = await Promise.all([
    query(
      `SELECT d::date::text AS day,
              COALESCE(SUM((o.totals->>'total')::numeric), 0) AS total,
              COUNT(o.id)::int AS orders
         FROM generate_series(current_date - 6, current_date, interval '1 day') d
         LEFT JOIN orders o ON o.created_at::date = d::date
        GROUP BY d ORDER BY d`,
    ),
    query(
      `SELECT oi.sku, p.name, p.unit, SUM(oi.qty)::int AS qty, SUM(oi.qty * oi.unit_price) AS revenue
         FROM order_items oi
         JOIN orders o ON o.id = oi.order_id
         JOIN products p ON p.sku = oi.sku
        WHERE o.created_at::date >= current_date - 6
        GROUP BY oi.sku, p.name, p.unit
        ORDER BY qty DESC, revenue DESC
        LIMIT 5`,
    ),
    query(`SELECT status, COUNT(*)::int AS n FROM orders GROUP BY status`),
    query(
      `SELECT COUNT(*)::int AS n FROM stock s JOIN products p ON p.sku = s.sku WHERE s.qty < p.reorder_point`,
    ),
    query(`SELECT COUNT(*)::int AS n FROM notifications WHERE NOT read`),
    checkQueue(Q.CHAT_DLQ).catch(() => null),
  ]);

  const series = days.rows.map((r: any) => ({ day: r.day, total: Number(r.total) || 0, orders: r.orders }));
  const today = series[series.length - 1] ?? { total: 0, orders: 0 };
  const statusCount: Record<string, number> = { received: 0, preparing: 0, shipping: 0, delivered: 0 };
  for (const r of byStatus.rows as any[]) statusCount[r.status] = r.n;

  return NextResponse.json({
    today: { total: today.total, orders: today.orders },
    week: {
      total: Math.round(series.reduce((s, d) => s + d.total, 0) * 100) / 100,
      orders: series.reduce((s, d) => s + d.orders, 0),
      days: series,
    },
    top: top.rows.map((r: any) => ({ sku: r.sku, name: r.name, unit: r.unit, qty: r.qty, revenue: Number(r.revenue) || 0 })),
    statusCount,
    lowStockCount: low.rows[0]?.n ?? 0,
    unreadNotifications: unread.rows[0]?.n ?? 0,
    dlq: dlq ? dlq.messageCount : null,
  });
}
