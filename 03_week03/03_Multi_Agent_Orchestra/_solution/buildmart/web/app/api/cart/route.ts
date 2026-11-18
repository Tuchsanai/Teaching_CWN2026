// /api/cart (B2) — ตะกร้าใน DB ผูก cookie bm_sid
//   GET                         → { items, totals, count, coupon }
//   POST   {sku, qty}           → เพิ่ม (บวกจำนวนเดิม) · หรือ {items:[{sku,qty}]} เพิ่มหลายรายการทีเดียว (เครื่องคำนวณ "เพิ่มทั้งหมด")
//   PATCH  {sku, qty}           → ตั้งจำนวนใหม่ (qty ≤ 0 = ลบ)
//   DELETE {sku} หรือ ?sku=     → ลบรายการ · ไม่ระบุ sku = ล้างตะกร้า
import { tx } from '@/lib/db';
import { getSessionId } from '@/lib/session';
import { addItem, clearCart, errorJson, loadCart, readJson, removeItem, setItem } from './_lib';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    return Response.json(await tx((c) => loadCart(c, getSessionId())));
  } catch (e) {
    return errorJson(e);
  }
}

export async function POST(req: Request) {
  const sid = getSessionId();
  const body = await readJson(req);
  try {
    const cart = await tx(async (c) => {
      const list = Array.isArray(body.items) ? body.items : [body];
      for (const it of list) await addItem(c, sid, it.sku, it.qty ?? 1);
      return loadCart(c, sid);
    });
    return Response.json(cart);
  } catch (e) {
    return errorJson(e);
  }
}

export async function PATCH(req: Request) {
  const sid = getSessionId();
  const body = await readJson(req);
  try {
    const cart = await tx(async (c) => {
      await setItem(c, sid, body.sku, body.qty);
      return loadCart(c, sid);
    });
    return Response.json(cart);
  } catch (e) {
    return errorJson(e);
  }
}

export async function DELETE(req: Request) {
  const sid = getSessionId();
  const body = await readJson(req);
  const sku = body.sku ?? new URL(req.url).searchParams.get('sku');
  try {
    const cart = await tx(async (c) => {
      if (sku) await removeItem(c, sid, sku);
      else await clearCart(c, sid);
      return loadCart(c, sid);
    });
    return Response.json(cart);
  } catch (e) {
    return errorJson(e);
  }
}
