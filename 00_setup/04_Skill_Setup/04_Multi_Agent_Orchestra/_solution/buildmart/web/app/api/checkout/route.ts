// POST /api/checkout {name, phone, address, branch, deliveryDate, slot} (B2)
//   200 {orderNo} · 409 {error:'stock', items:[{sku,name,need,available}]} (ไม่ตัดอะไรเลย) · 400 {error} กรอกไม่ครบ/ตะกร้าว่าง
// ขั้นตอน (transaction เดียว): lock ตะกร้า + แถว stock ของสาขา → ไม่พอ = rollback 409
//   → ตัดสต็อก → สร้าง orders/order_items/order_status_history('received') ด้วยเลข next_doc_no('BM') → ล้างตะกร้า
// หลัง commit: publish order.events (fanout) {type:'order.created', orderNo, items:[{sku,qty}], branch} ให้ notify-worker
import { tx } from '@/lib/db';
import { publish, EX } from '@/lib/amqp';
import { getSessionId } from '@/lib/session';
import { BRANCH_CODES, clearCart, deliveryDates, digits, errorJson, HttpError, loadCart, readJson } from '../cart/_lib';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const sid = getSessionId();
  const b = await readJson(req);
  const name = String(b.name ?? '').trim();
  const phone = String(b.phone ?? '').trim();
  const address = String(b.address ?? '').trim();
  const branch = String(b.branch ?? '').trim().toUpperCase();
  const deliveryDate = String(b.deliveryDate ?? '').trim();
  const slot = String(b.slot ?? '').trim();

  try {
    if (!name) throw new HttpError(400, 'กรุณากรอกชื่อผู้สั่งซื้อ');
    if (digits(phone).length < 9) throw new HttpError(400, 'กรุณากรอกเบอร์โทรให้ถูกต้อง');
    if (!address) throw new HttpError(400, 'กรุณากรอกที่อยู่จัดส่ง');
    if (!BRANCH_CODES.includes(branch)) throw new HttpError(400, 'กรุณาเลือกสาขาที่ส่งของ');
    if (!deliveryDates().some((d) => d.value === deliveryDate))
      throw new HttpError(400, 'วันส่งต้องอยู่ใน 7 วันถัดไป และไม่ใช่วันอาทิตย์');
    if (!['morning', 'afternoon'].includes(slot)) throw new HttpError(400, 'กรุณาเลือกช่วงเวลาส่ง (เช้า/บ่าย)');

    const order = await tx(async (c) => {
      const cart = await loadCart(c, sid, true);
      if (!cart.items.length) throw new HttpError(400, 'ตะกร้าว่าง');

      const skus = cart.items.map((i) => i.sku);
      const st = await c.query(
        'SELECT sku, qty FROM stock WHERE branch = $1 AND sku = ANY($2) ORDER BY sku FOR UPDATE',
        [branch, skus],
      );
      const avail = new Map<string, number>(st.rows.map((r: any) => [r.sku, r.qty] as [string, number]));
      const short = cart.items
        .filter((i) => (avail.get(i.sku) ?? 0) < i.qty)
        .map((i) => ({ sku: i.sku, name: i.name, unit: i.unit, need: i.qty, available: avail.get(i.sku) ?? 0 }));
      if (short.length) throw new HttpError(409, 'stock', { items: short, branch });

      for (const i of cart.items) {
        await c.query('UPDATE stock SET qty = qty - $3 WHERE sku = $1 AND branch = $2', [i.sku, branch, i.qty]);
      }
      const orderNo: string = (await c.query(`SELECT next_doc_no('BM') AS no`)).rows[0].no;
      const o = await c.query(
        `INSERT INTO orders (order_no, session_id, customer_name, phone, address, branch, delivery_date, delivery_slot, coupon, totals)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id`,
        [orderNo, sid, name, phone, address, branch, deliveryDate, slot, cart.totals.coupon, JSON.stringify(cart.totals)],
      );
      const orderId = o.rows[0].id;
      for (const i of cart.items) {
        await c.query('INSERT INTO order_items (order_id, sku, qty, unit_price) VALUES ($1, $2, $3, $4)', [
          orderId,
          i.sku,
          i.qty,
          i.unitPrice,
        ]);
      }
      await c.query(`INSERT INTO order_status_history (order_id, status) VALUES ($1, 'received')`, [orderId]);
      await clearCart(c, sid);
      return { orderNo, items: cart.items.map((i) => ({ sku: i.sku, qty: i.qty })), total: cart.totals.total };
    });

    try {
      await publish(EX.ORDER_EVENTS, '', { type: 'order.created', orderNo: order.orderNo, items: order.items, branch });
    } catch (e: any) {
      // คำสั่งซื้อบันทึกแล้ว — แจ้งเตือนหลังร้านพลาดได้ ไม่ทำให้ลูกค้าสั่งไม่สำเร็จ
      console.error('[checkout] publish order.events failed', e?.message);
    }
    return Response.json({ orderNo: order.orderNo, total: order.total, count: 0 });
  } catch (e) {
    if (e instanceof HttpError && e.status === 409) {
      return Response.json({ error: 'stock', message: 'สินค้าในสาขาที่เลือกมีไม่พอ', ...e.extra }, { status: 409 });
    }
    return errorJson(e);
  }
}
