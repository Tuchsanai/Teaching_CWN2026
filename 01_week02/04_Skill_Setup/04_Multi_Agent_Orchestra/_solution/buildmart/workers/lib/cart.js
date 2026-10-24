// workers/lib/cart.js — ตะกร้าของ session (ตาราง carts / cart_items) ใช้จาก chat-worker ([ADD_TO_CART])
// web (B2) ใช้ตารางเดียวกันด้วย SQL แบบเดียวกัน · count = ผลรวมจำนวนชิ้น (เหมือน GET /api/cart/count)
import { computeTotals } from '../../shared/pricing.js';

/** คืน cart id ของ session (สร้างถ้ายังไม่มี) */
export async function getOrCreateCartId(db, sessionId) {
  const r = await db.query(
    `INSERT INTO carts (session_id) VALUES ($1)
     ON CONFLICT (session_id) DO UPDATE SET session_id = EXCLUDED.session_id
     RETURNING id`,
    [sessionId],
  );
  return r.rows[0].id;
}

/** เพิ่มสินค้าลงตะกร้า (บวกจำนวนเดิม) → คืน count ใหม่ */
export async function addToCart(db, sessionId, sku, qty) {
  const q = Math.max(1, Math.floor(Number(qty) || 1));
  const p = await db.query('SELECT sku FROM products WHERE sku = $1', [String(sku).toUpperCase()]);
  if (!p.rowCount) throw new Error(`ไม่พบสินค้า ${sku}`);
  const cartId = await getOrCreateCartId(db, sessionId);
  await db.query(
    `INSERT INTO cart_items (cart_id, sku, qty) VALUES ($1, $2, $3)
     ON CONFLICT (cart_id, sku) DO UPDATE SET qty = cart_items.qty + EXCLUDED.qty`,
    [cartId, p.rows[0].sku, q],
  );
  return cartCount(db, sessionId);
}

export async function cartCount(db, sessionId) {
  const r = await db.query(
    `SELECT COALESCE(SUM(ci.qty), 0)::int AS count
       FROM carts c JOIN cart_items ci ON ci.cart_id = c.id WHERE c.session_id = $1`,
    [sessionId],
  );
  return r.rows[0].count;
}

/** รายการในตะกร้า + ยอด (ใช้ shared/pricing) → { cartId, coupon, items, totals } */
export async function loadCart(db, sessionId) {
  const c = await db.query('SELECT id, coupon FROM carts WHERE session_id = $1', [sessionId]);
  if (!c.rowCount) return { cartId: null, coupon: null, items: [], totals: computeTotals({ items: [] }) };
  const { id: cartId, coupon } = c.rows[0];
  const r = await db.query(
    `SELECT ci.sku, ci.qty, p.name, p.unit, p.price, p.weight_kg
       FROM cart_items ci JOIN products p ON p.sku = ci.sku
      WHERE ci.cart_id = $1 ORDER BY ci.sku`,
    [cartId],
  );
  const items = r.rows;
  const totals = computeTotals({ items, coupon });
  return { cartId, coupon, items, totals };
}
