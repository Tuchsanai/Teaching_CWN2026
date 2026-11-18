// GET /api/admin/notifications?limit=30 → { items:[{id,kind,message,ref,createdAt,read}], unread }
// PATCH /api/admin/notifications { ids?:number[] } → ทำเครื่องหมายว่าอ่านแล้ว (ไม่ส่ง ids = ทั้งหมด)
// ข้อมูลเขียนโดย notify-worker (คิว notify.orders ผูก exchange order.events)
import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { requireAdmin } from '../_auth';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  const deny = requireAdmin();
  if (deny) return deny;
  const limit = Math.min(Math.max(Number(new URL(req.url).searchParams.get('limit')) || 30, 1), 200);
  const [list, unread] = await Promise.all([
    query(
      `SELECT id, kind, message, ref, created_at, read FROM notifications ORDER BY created_at DESC, id DESC LIMIT $1`,
      [limit],
    ),
    query(`SELECT COUNT(*)::int AS n FROM notifications WHERE NOT read`),
  ]);
  return NextResponse.json({
    items: list.rows.map((n: any) => ({
      id: n.id,
      kind: n.kind,
      message: n.message,
      ref: n.ref,
      createdAt: n.created_at,
      read: n.read,
    })),
    unread: unread.rows[0]?.n ?? 0,
  });
}

export async function PATCH(req: Request) {
  const deny = requireAdmin();
  if (deny) return deny;
  const body = await req.json().catch(() => ({}));
  const ids = Array.isArray(body?.ids) ? body.ids.map(Number).filter(Number.isInteger) : null;
  const r = ids
    ? await query('UPDATE notifications SET read = true WHERE id = ANY($1::int[]) AND NOT read', [ids])
    : await query('UPDATE notifications SET read = true WHERE NOT read');
  return NextResponse.json({ updated: r.rowCount });
}
