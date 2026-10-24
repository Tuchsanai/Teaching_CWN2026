// GET /api/orders (B2) → คำสั่งซื้อของ session นี้ (ล่าสุดก่อน)
import { query } from '@/lib/db';
import { getSessionId } from '@/lib/session';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const r = await query(
    `SELECT order_no AS "orderNo", status, branch, delivery_date::text AS "deliveryDate", delivery_slot AS "deliverySlot",
            (totals->>'total')::numeric AS total, created_at AS "createdAt"
       FROM orders WHERE session_id = $1 ORDER BY created_at DESC LIMIT 50`,
    [getSessionId()],
  );
  return Response.json({ items: r.rows });
}
