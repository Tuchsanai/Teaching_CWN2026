// GET /api/cart/count → { count } (ผลรวมจำนวนชิ้นในตะกร้าของ session) — A สร้างไว้ให้ header · B2 เป็นเจ้าของ /api/cart ส่วนอื่น
import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { peekSessionId } from '@/lib/session';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const sid = peekSessionId();
  if (!sid) return NextResponse.json({ count: 0 });
  const r = await query<{ count: number }>(
    `SELECT COALESCE(SUM(ci.qty), 0)::int AS count
       FROM carts c JOIN cart_items ci ON ci.cart_id = c.id
      WHERE c.session_id = $1`,
    [sid],
  );
  return NextResponse.json({ count: r.rows[0]?.count ?? 0 });
}
