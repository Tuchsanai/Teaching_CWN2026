// app/api/quotes/_quote.ts (B2) — สร้าง/อ่านใบเสนอราคา (ตรรกะเดียวกับ workers/lib/quote.js ของ chat-worker)
import type { PoolClient } from 'pg';
import { pool } from '@/lib/db';
import { HttpError, loadCart } from '../cart/_lib';

export async function createQuote(c: PoolClient, sid: string, { name = '', company = '', taxId = '' }) {
  const cart = await loadCart(c, sid, true);
  if (!cart.items.length) throw new HttpError(400, 'ตะกร้าว่าง เพิ่มสินค้าก่อนขอใบเสนอราคา');
  const { totals } = cart;
  const no: string = (await c.query(`SELECT next_doc_no('QT') AS no`)).rows[0].no;
  const q = await c.query(
    `INSERT INTO quotes (quote_no, session_id, customer_name, company, tax_id, coupon, totals, expires_at)
     VALUES ($1, $2, $3, $4, $5, $6, $7, now() + interval '7 days') RETURNING id`,
    [no, sid, name || null, company || null, taxId || null, totals.coupon, JSON.stringify(totals)],
  );
  for (const l of totals.lines) {
    await c.query('INSERT INTO quote_items (quote_id, sku, qty, unit_price) VALUES ($1, $2, $3, $4)', [
      q.rows[0].id,
      l.sku,
      l.qty,
      l.unitPrice,
    ]);
  }
  return { quoteNo: no, total: totals.total };
}

export type QuoteItem = {
  sku: string;
  qty: number;
  unitPrice: number;
  name: string;
  unit: string;
  price: number;
  lineTotal: number;
  weight?: number;
};

export async function getQuote(no: string) {
  const q = await pool.query(
    `SELECT id, quote_no, session_id, customer_name, company, tax_id, coupon, totals, created_at, expires_at,
            expires_at < now() AS expired
       FROM quotes WHERE quote_no = $1`,
    [String(no).trim().toUpperCase()],
  );
  if (!q.rowCount) return null;
  const row = q.rows[0];
  const items = await pool.query(
    `SELECT qi.sku, qi.qty, qi.unit_price AS "unitPrice", p.name, p.unit, p.price
       FROM quote_items qi JOIN products p ON p.sku = qi.sku
      WHERE qi.quote_id = $1 ORDER BY qi.sku`,
    [row.id],
  );
  const totals = row.totals || {};
  return {
    quoteNo: row.quote_no as string,
    sessionId: row.session_id as string | null,
    customerName: row.customer_name as string | null,
    company: row.company as string | null,
    taxId: row.tax_id as string | null,
    coupon: row.coupon as string | null,
    createdAt: new Date(row.created_at).toISOString(),
    expiresAt: new Date(row.expires_at).toISOString(),
    expired: row.expired as boolean,
    items: items.rows.map((i: any): QuoteItem => {
      const line = (totals.lines || []).find((l: any) => l.sku === i.sku);
      return { ...i, lineTotal: line?.lineTotal ?? Math.round(i.unitPrice * i.qty * 100) / 100, weight: line?.weight };
    }),
    totals,
  };
}
