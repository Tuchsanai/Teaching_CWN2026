// GET /api/quotes/[no] (B2) → ใบเสนอราคา + รายการ + ยอด (เลข QT เป็นเลขอ้างอิงที่ส่งต่อให้ลูกค้าได้ จึงเปิดดูได้ด้วยเลข)
import { getQuote } from '../_quote';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(_req: Request, { params }: { params: { no: string } }) {
  const q = await getQuote(params.no);
  if (!q) return Response.json({ error: 'ไม่พบใบเสนอราคา' }, { status: 404 });
  const { sessionId: _sid, ...pub } = q;
  return Response.json(pub);
}
