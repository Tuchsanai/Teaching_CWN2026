// GET /api/orders/[no] (B2) → รายละเอียดคำสั่งซื้อ (เฉพาะ session ที่สั่ง · คนอื่นใช้ /api/track ด้วยเบอร์โทร)
import { getSessionId } from '@/lib/session';
import { getOrder } from '../_order';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(_req: Request, { params }: { params: { no: string } }) {
  const o = await getOrder(params.no);
  if (!o || o.sessionId !== getSessionId()) return Response.json({ error: 'ไม่พบคำสั่งซื้อ' }, { status: 404 });
  const { sessionId: _sid, ...pub } = o;
  return Response.json(pub);
}
