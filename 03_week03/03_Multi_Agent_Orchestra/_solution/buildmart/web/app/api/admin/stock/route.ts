// GET /api/admin/stock → { items:[{sku,name,category,unit,reorderPoint,stock:{LKB,BNA,RST},low:[branch...]}], lowCount }
// PATCH /api/admin/stock { sku, stock?:{LKB?,BNA?,RST?}, reorderPoint? } → แถวที่อัปเดตแล้ว
import { NextResponse } from 'next/server';
import { query, tx } from '@/lib/db';
import { requireAdmin } from '../_auth';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const BRANCHES = ['LKB', 'BNA', 'RST'] as const;

async function load(sku?: string) {
  const r = await query(
    `SELECT p.sku, p.name, p.category, p.unit, p.reorder_point,
            COALESCE(jsonb_object_agg(s.branch, s.qty) FILTER (WHERE s.branch IS NOT NULL), '{}'::jsonb) AS stock
       FROM products p LEFT JOIN stock s ON s.sku = p.sku
      WHERE ($1::text IS NULL OR p.sku = $1)
      GROUP BY p.sku
      ORDER BY p.category, p.sku`,
    [sku ?? null],
  );
  return r.rows.map((p: any) => {
    const stock: Record<string, number> = {};
    for (const b of BRANCHES) stock[b] = Number(p.stock?.[b] ?? 0);
    return {
      sku: p.sku,
      name: p.name,
      category: p.category,
      unit: p.unit,
      reorderPoint: p.reorder_point,
      stock,
      low: BRANCHES.filter((b) => stock[b] < p.reorder_point),
    };
  });
}

export async function GET() {
  const deny = requireAdmin();
  if (deny) return deny;
  const items = await load();
  return NextResponse.json({ items, lowCount: items.reduce((n, i) => n + i.low.length, 0) });
}

const toInt = (v: unknown) => {
  const n = Number(v);
  return Number.isInteger(n) && n >= 0 && n <= 10_000_000 ? n : null;
};

export async function PATCH(req: Request) {
  const deny = requireAdmin();
  if (deny) return deny;
  const body = await req.json().catch(() => null);
  const sku = typeof body?.sku === 'string' ? body.sku : '';
  if (!sku) return NextResponse.json({ error: 'ต้องระบุ sku' }, { status: 400 });

  const updates: [string, number][] = [];
  for (const b of BRANCHES) {
    if (body?.stock?.[b] === undefined) continue;
    const n = toInt(body.stock[b]);
    if (n === null) return NextResponse.json({ error: `จำนวนสาขา ${b} ต้องเป็นจำนวนเต็ม ≥ 0` }, { status: 400 });
    updates.push([b, n]);
  }
  let reorder: number | null = null;
  if (body?.reorderPoint !== undefined) {
    reorder = toInt(body.reorderPoint);
    if (reorder === null) return NextResponse.json({ error: 'จุดสั่งซื้อซ้ำต้องเป็นจำนวนเต็ม ≥ 0' }, { status: 400 });
  }

  const found = await tx(async (c) => {
    const p = await c.query('SELECT 1 FROM products WHERE sku = $1', [sku]);
    if (!p.rowCount) return false;
    for (const [b, n] of updates) {
      await c.query(
        `INSERT INTO stock (sku, branch, qty) VALUES ($1, $2, $3)
         ON CONFLICT (sku, branch) DO UPDATE SET qty = EXCLUDED.qty`,
        [sku, b, n],
      );
    }
    if (reorder !== null) await c.query('UPDATE products SET reorder_point = $2 WHERE sku = $1', [sku, reorder]);
    return true;
  });
  if (!found) return NextResponse.json({ error: 'ไม่พบสินค้า' }, { status: 404 });
  const [item] = await load(sku);
  return NextResponse.json({ item });
}
