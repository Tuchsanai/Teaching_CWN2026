// workers/lib/quote.js — สร้างใบเสนอราคาจากตะกร้า (ใช้โดย chat-worker tag [QUOTE])
// เลขเอกสารมาจาก SQL `next_doc_no('QT')` ตัวเดียวกับที่ web (B2 /api/quotes) ใช้ → ไม่ชนกัน
// ยอดคิดด้วย shared/pricing.js · quotes.totals เก็บผลของ computeTotals() ทั้งก้อน · อายุ 7 วัน
import { tx } from './db.js';
import { loadCart } from './cart.js';

/**
 * @param {import('pg').Pool} pool
 * @param {string} sessionId
 * @param {{name?:string, company?:string, taxId?:string}} customer
 * @returns {Promise<{quoteNo:string, quoteId:number, totals:object, items:object[], expiresAt:string}>}
 * throws Error('cart_empty') ถ้าตะกร้าว่าง
 */
export async function createQuoteFromCart(pool, sessionId, { name = '', company = '', taxId = '' } = {}) {
  return tx(async (c) => {
    const cart = await loadCart(c, sessionId);
    if (!cart.items.length) throw new Error('cart_empty');
    const { totals } = cart;
    const no = (await c.query(`SELECT next_doc_no('QT') AS no`)).rows[0].no;
    const q = await c.query(
      `INSERT INTO quotes (quote_no, session_id, customer_name, company, tax_id, coupon, totals, expires_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, now() + interval '7 days')
       RETURNING id, expires_at`,
      [no, sessionId, name || null, company || null, taxId || null, totals.coupon, JSON.stringify(totals)],
    );
    const quoteId = q.rows[0].id;
    for (const l of totals.lines) {
      await c.query('INSERT INTO quote_items (quote_id, sku, qty, unit_price) VALUES ($1, $2, $3, $4)', [
        quoteId,
        l.sku,
        l.qty,
        l.unitPrice,
      ]);
    }
    return { quoteNo: no, quoteId, totals, items: cart.items, expiresAt: q.rows[0].expires_at };
  });
}
