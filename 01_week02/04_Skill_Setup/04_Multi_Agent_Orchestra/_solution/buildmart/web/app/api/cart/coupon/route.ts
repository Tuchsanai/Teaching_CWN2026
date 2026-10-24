// POST /api/cart/coupon {code} (B2) — ใส่คูปองในตะกร้า (code ว่าง = เอาคูปองออก)
// คูปองไม่มีจริง / ยอดไม่ถึงขั้นต่ำ → 400 {error} และไม่บันทึก
import { tx } from '@/lib/db';
import { getSessionId } from '@/lib/session';
import { computeTotals } from '@/shared/pricing.js';
import { errorJson, HttpError, loadCart, readJson, setCoupon } from '../_lib';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const sid = getSessionId();
  const code = String((await readJson(req)).code ?? '').trim().toUpperCase();
  try {
    const cart = await tx(async (c) => {
      if (!code) {
        await setCoupon(c, sid, null);
        return loadCart(c, sid);
      }
      const cur = await loadCart(c, sid, true);
      const check: any = computeTotals({
        items: cur.items.map((i) => ({ sku: i.sku, qty: i.qty, price: i.price, weight_kg: i.weightPerUnit })),
        coupon: code,
      });
      if (check.couponError) throw new HttpError(400, check.couponError);
      const r = await c.query('SELECT code FROM coupons WHERE code = $1', [code]);
      if (!r.rowCount) throw new HttpError(400, `ไม่พบคูปอง ${code}`);
      await setCoupon(c, sid, code);
      return loadCart(c, sid);
    });
    return Response.json(cart);
  } catch (e) {
    return errorJson(e);
  }
}
