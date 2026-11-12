// POST /api/quotes/[no]/order (B2) — แปลงใบเสนอราคาเป็นคำสั่งซื้อ:
// แทนที่ตะกร้าของ session ด้วยรายการ + คูปองของใบเสนอราคา แล้วไปหน้า /checkout
//   fetch (JSON) → {ok, redirect:'/checkout', count} · ฟอร์ม HTML ธรรมดา → 303 /checkout
//   ใบเสนอราคาหมดอายุ → 410
import { tx } from '@/lib/db';
import { getSessionId } from '@/lib/session';
import { clearCart, errorJson, getOrCreateCartId, HttpError, setCoupon } from '../../../cart/_lib';
import { getQuote } from '../../_quote';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request, { params }: { params: { no: string } }) {
  const sid = getSessionId();
  try {
    const q = await getQuote(params.no);
    if (!q) throw new HttpError(404, 'ไม่พบใบเสนอราคา');
    if (q.expired) throw new HttpError(410, 'ใบเสนอราคานี้หมดอายุแล้ว (อายุ 7 วัน) กรุณาขอใบใหม่');
    const count = await tx(async (c) => {
      await clearCart(c, sid);
      const cartId = await getOrCreateCartId(c, sid);
      for (const i of q.items) {
        await c.query('INSERT INTO cart_items (cart_id, sku, qty) VALUES ($1, $2, $3)', [cartId, i.sku, i.qty]);
      }
      if (q.coupon) await setCoupon(c, sid, q.coupon);
      return q.items.reduce((s, i) => s + i.qty, 0);
    });
    if ((req.headers.get('accept') || '').includes('text/html')) {
      return Response.redirect(new URL('/checkout', req.url), 303);
    }
    return Response.json({ ok: true, redirect: '/checkout', count });
  } catch (e) {
    return errorJson(e);
  }
}
