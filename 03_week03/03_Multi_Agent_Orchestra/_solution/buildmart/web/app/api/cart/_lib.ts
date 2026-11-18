// app/api/cart/_lib.ts (B2) — ตะกร้า/ใบเสนอราคา/คำสั่งซื้อ ฝั่ง server (ใช้ร่วมกันระหว่าง route ของ B2)
// ตาราง carts / cart_items ผูกกับ cookie bm_sid · ยอดเงินคิดด้วย shared/pricing.js ที่เดียว
// count = SUM(qty) (นิยามเดียวกับ GET /api/cart/count ของ A และ workers/lib/cart.js)
import type { QueryResult } from 'pg';
import { computeTotals } from '@/shared/pricing.js';

type Db = { query(text: string, params?: unknown[]): Promise<QueryResult<any>> };

export const BRANCHES = [
  { code: 'LKB', name: 'ลาดกระบัง', phone: '02-111-0001' },
  { code: 'BNA', name: 'บางนา', phone: '02-111-0002' },
  { code: 'RST', name: 'รังสิต', phone: '02-111-0003' },
] as const;
export const BRANCH_CODES = BRANCHES.map((b) => b.code) as string[];

export const STATUSES = [
  { code: 'received', label: 'รับคำสั่งซื้อ' },
  { code: 'preparing', label: 'เตรียมสินค้า' },
  { code: 'shipping', label: 'กำลังจัดส่ง' },
  { code: 'delivered', label: 'ส่งแล้ว' },
] as const;

export type CartItem = {
  sku: string;
  name: string;
  unit: string;
  price: number;
  qty: number;
  unitPrice: number;
  lineTotal: number;
  weight: number;
  weightPerUnit: number;
  tier: 1 | 2 | 3;
  stock: Record<string, number>;
};

export type Cart = {
  cartId: string | null;
  coupon: string | null;
  items: CartItem[];
  totals: any;
  count: number;
};

export class HttpError extends Error {
  constructor(public status: number, message: string, public extra: Record<string, unknown> = {}) {
    super(message);
  }
}

export function normSku(s: unknown) {
  return String(s ?? '').trim().toUpperCase();
}

export function normQty(q: unknown) {
  const n = Math.floor(Number(q));
  return Number.isFinite(n) ? n : NaN;
}

export async function getOrCreateCartId(db: Db, sid: string): Promise<string> {
  const r = await db.query(
    `INSERT INTO carts (session_id) VALUES ($1)
     ON CONFLICT (session_id) DO UPDATE SET session_id = EXCLUDED.session_id
     RETURNING id`,
    [sid],
  );
  return r.rows[0].id;
}

async function assertProduct(db: Db, sku: string) {
  const r = await db.query('SELECT sku FROM products WHERE sku = $1', [sku]);
  if (!r.rowCount) throw new HttpError(404, `ไม่พบสินค้า ${sku}`);
}

/** เพิ่มสินค้า (บวกจำนวนเดิม) */
export async function addItem(db: Db, sid: string, skuIn: unknown, qtyIn: unknown) {
  const sku = normSku(skuIn);
  const qty = normQty(qtyIn ?? 1);
  if (!sku) throw new HttpError(400, 'ต้องระบุ sku');
  if (!(qty >= 1)) throw new HttpError(400, 'จำนวนต้องเป็นจำนวนเต็มตั้งแต่ 1 ขึ้นไป');
  await assertProduct(db, sku);
  const cartId = await getOrCreateCartId(db, sid);
  await db.query(
    `INSERT INTO cart_items (cart_id, sku, qty) VALUES ($1, $2, $3)
     ON CONFLICT (cart_id, sku) DO UPDATE SET qty = cart_items.qty + EXCLUDED.qty`,
    [cartId, sku, qty],
  );
}

/** ตั้งจำนวน (qty ≤ 0 = ลบรายการ) */
export async function setItem(db: Db, sid: string, skuIn: unknown, qtyIn: unknown) {
  const sku = normSku(skuIn);
  const qty = normQty(qtyIn);
  if (!sku) throw new HttpError(400, 'ต้องระบุ sku');
  if (!Number.isFinite(qty)) throw new HttpError(400, 'จำนวนไม่ถูกต้อง');
  if (qty <= 0) return removeItem(db, sid, sku);
  await assertProduct(db, sku);
  const cartId = await getOrCreateCartId(db, sid);
  await db.query(
    `INSERT INTO cart_items (cart_id, sku, qty) VALUES ($1, $2, $3)
     ON CONFLICT (cart_id, sku) DO UPDATE SET qty = EXCLUDED.qty`,
    [cartId, sku, qty],
  );
}

export async function removeItem(db: Db, sid: string, skuIn: unknown) {
  await db.query(
    `DELETE FROM cart_items ci USING carts c
      WHERE ci.cart_id = c.id AND c.session_id = $1 AND ci.sku = $2`,
    [sid, normSku(skuIn)],
  );
}

/** ล้างตะกร้า (รายการ + คูปอง) */
export async function clearCart(db: Db, sid: string) {
  await db.query(`DELETE FROM cart_items ci USING carts c WHERE ci.cart_id = c.id AND c.session_id = $1`, [sid]);
  await db.query('UPDATE carts SET coupon = NULL WHERE session_id = $1', [sid]);
}

export async function setCoupon(db: Db, sid: string, code: string | null) {
  const cartId = await getOrCreateCartId(db, sid);
  await db.query('UPDATE carts SET coupon = $2 WHERE id = $1', [cartId, code]);
}

/** โหลดตะกร้า + ยอดจาก shared/pricing.js · lock = true ใช้ใน transaction (SELECT ... FOR UPDATE) */
export async function loadCart(db: Db, sid: string, lock = false): Promise<Cart> {
  const c = await db.query(`SELECT id, coupon FROM carts WHERE session_id = $1${lock ? ' FOR UPDATE' : ''}`, [sid]);
  if (!c.rowCount) return { cartId: null, coupon: null, items: [], totals: computeTotals({ items: [] }), count: 0 };
  const { id: cartId, coupon } = c.rows[0];
  const r = await db.query(
    `SELECT ci.sku, ci.qty, p.name, p.unit, p.price, p.weight_kg,
            COALESCE(jsonb_object_agg(s.branch, s.qty) FILTER (WHERE s.branch IS NOT NULL), '{}'::jsonb) AS stock
       FROM cart_items ci
       JOIN products p ON p.sku = ci.sku
       LEFT JOIN stock s ON s.sku = ci.sku
      WHERE ci.cart_id = $1
      GROUP BY ci.sku, ci.qty, p.name, p.unit, p.price, p.weight_kg
      ORDER BY ci.sku`,
    [cartId],
  );
  const rows = r.rows;
  const totals = computeTotals({ items: rows, coupon });
  const items: CartItem[] = rows.map((row: any) => {
    const l = totals.lines.find((x: any) => x.sku === row.sku)!;
    return {
      sku: row.sku,
      name: row.name,
      unit: row.unit,
      price: Number(row.price),
      qty: row.qty,
      unitPrice: l.unitPrice,
      lineTotal: l.lineTotal,
      weight: l.weight,
      weightPerUnit: Number(row.weight_kg),
      tier: row.qty >= 200 ? 3 : row.qty >= 50 ? 2 : 1,
      stock: row.stock || {},
    };
  });
  const count = items.reduce((s, i) => s + i.qty, 0);
  return { cartId, coupon, items, totals, count };
}

/** วันส่งที่เลือกได้: 7 วันถัดไป (พรุ่งนี้ … +7) ไม่รวมวันอาทิตย์ · ใช้วันที่ตามเวลาไทย */
export function deliveryDates(now = new Date()) {
  const bkk = new Date(now.getTime() + 7 * 3600_000); // UTC → เวลาไทย (ใช้ getUTC*)
  const out: { value: string; label: string }[] = [];
  const days = ['อาทิตย์', 'จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'ศุกร์', 'เสาร์'];
  const months = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
  for (let i = 1; i <= 7; i++) {
    const d = new Date(Date.UTC(bkk.getUTCFullYear(), bkk.getUTCMonth(), bkk.getUTCDate() + i));
    if (d.getUTCDay() === 0) continue;
    const value = d.toISOString().slice(0, 10);
    out.push({ value, label: `${days[d.getUTCDay()]} ${d.getUTCDate()} ${months[d.getUTCMonth()]} ${d.getUTCFullYear() + 543}` });
  }
  return out;
}

export function digits(s: unknown) {
  return String(s ?? '').replace(/\D/g, '');
}

/** แปลง error เป็น Response JSON */
export function errorJson(e: unknown) {
  if (e instanceof HttpError) {
    return Response.json({ error: e.message, ...e.extra }, { status: e.status });
  }
  console.error('[b2]', e);
  return Response.json({ error: 'เกิดข้อผิดพลาดในระบบ ลองใหม่อีกครั้ง' }, { status: 500 });
}

export async function readJson(req: Request): Promise<any> {
  try {
    return await req.json();
  } catch {
    return {};
  }
}
