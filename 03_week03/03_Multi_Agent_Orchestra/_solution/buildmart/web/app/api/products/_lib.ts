// app/api/products/_lib.ts (B1) — ค้นหา/อ่านสินค้า ใช้ร่วมกันทั้ง route handler และหน้า /products (server component)
import { query } from '@/lib/db';
import { tierTable } from '@/shared/pricing.js';

export const PAGE_SIZE = 12;
export const BRANCH_ORDER = ['LKB', 'BNA', 'RST'] as const;

export type BranchStock = { branch: string; name: string; phone: string; qty: number };
export type ProductItem = {
  sku: string;
  name: string;
  category: string;
  unit: string;
  price: number;
  weight_kg: number;
  reorder_point: number;
  description: string | null;
  totalStock: number;
  stock: Record<string, number>;
};
export type ProductSearch = {
  q?: string;
  category?: string;
  min?: number | null;
  max?: number | null;
  inStock?: boolean;
  sort?: string;
  page?: number;
};

function numOrNull(v: unknown): number | null {
  if (v === undefined || v === null || v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

/** แปลง query string (URLSearchParams หรือ searchParams ของ page) → ProductSearch */
export function parseSearch(sp: URLSearchParams | Record<string, string | string[] | undefined>): ProductSearch {
  const get = (k: string): string | undefined => {
    if (sp instanceof URLSearchParams) return sp.get(k) ?? undefined;
    const v = sp[k];
    return Array.isArray(v) ? v[0] : v;
  };
  const inStockRaw = (get('inStock') || '').toLowerCase();
  return {
    q: (get('q') || '').trim(),
    category: (get('category') || '').trim(),
    min: numOrNull(get('min')),
    max: numOrNull(get('max')),
    inStock: ['1', 'true', 'on', 'yes'].includes(inStockRaw),
    sort: get('sort') || '',
    page: Math.max(1, Math.floor(Number(get('page')) || 1)),
  };
}

const STOCK_JSON = `COALESCE((SELECT jsonb_object_agg(s.branch, s.qty) FROM stock s WHERE s.sku = p.sku), '{}'::jsonb)`;
const STOCK_SUM = `COALESCE((SELECT SUM(s.qty) FROM stock s WHERE s.sku = p.sku), 0)::int`;

/** GET /api/products — ค้นไทยบางส่วน (ILIKE ทั้ง name/sku) · กรองหมวด/ราคา/มีของ · เรียงราคา · 12 ชิ้น/หน้า */
export async function searchProducts(s: ProductSearch) {
  const where: string[] = [];
  const params: unknown[] = [];
  const add = (sql: string, v: unknown) => {
    params.push(v);
    where.push(sql.replace('?', `$${params.length}`));
  };
  if (s.q) {
    // แยกคำด้วยช่องว่าง: ทุกคำต้องเจอในชื่อหรือ SKU (เช่น "ปูน กาว")
    for (const w of s.q.split(/\s+/).filter(Boolean)) {
      const esc = '%' + w.replace(/[\\%_]/g, (m) => '\\' + m) + '%';
      params.push(esc);
      const i = params.length;
      where.push(`(p.name ILIKE $${i} OR p.sku ILIKE $${i})`);
    }
  }
  if (s.category) add('p.category = ?', s.category);
  if (s.min != null) add('p.price >= ?', s.min);
  if (s.max != null) add('p.price <= ?', s.max);
  if (s.inStock) where.push(`${STOCK_SUM} > 0`);
  const whereSql = where.length ? 'WHERE ' + where.join(' AND ') : '';
  const order =
    s.sort === 'price_asc' ? 'p.price ASC, p.sku ASC' : s.sort === 'price_desc' ? 'p.price DESC, p.sku ASC' : 'p.sku ASC';

  const totalR = await query<{ n: number }>(`SELECT COUNT(*)::int AS n FROM products p ${whereSql}`, params);
  const total = totalR.rows[0]?.n ?? 0;
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const page = Math.min(s.page || 1, pages);
  const r = await query<ProductItem>(
    `SELECT p.sku, p.name, p.category, p.unit, p.price, p.weight_kg, p.reorder_point, p.description,
            ${STOCK_SUM} AS "totalStock", ${STOCK_JSON} AS stock
       FROM products p ${whereSql}
      ORDER BY ${order}
      LIMIT ${PAGE_SIZE} OFFSET ${(page - 1) * PAGE_SIZE}`,
    params,
  );
  return { items: r.rows, total, page, pages };
}

/** GET /api/products/[sku] — สินค้า + tiers[3] + stock[3] (เรียง LKB · BNA · RST) */
export async function getProduct(sku: string) {
  const r = await query<Omit<ProductItem, 'totalStock' | 'stock'>>(
    `SELECT sku, name, category, unit, price, weight_kg, reorder_point, description FROM products WHERE upper(sku) = upper($1)`,
    [sku],
  );
  const p = r.rows[0];
  if (!p) return null;
  const st = await query<BranchStock>(
    `SELECT b.code AS branch, b.name, b.phone, COALESCE(s.qty, 0)::int AS qty
       FROM branches b LEFT JOIN stock s ON s.branch = b.code AND s.sku = $1`,
    [p.sku],
  );
  const stock = [...st.rows].sort(
    (a, b) => BRANCH_ORDER.indexOf(a.branch as any) - BRANCH_ORDER.indexOf(b.branch as any),
  );
  const tiers = tierTable(p.price) as { tier: number; minQty: number; maxQty: number | null; price: number }[];
  return { ...p, tiers, stock, totalStock: stock.reduce((s, b) => s + b.qty, 0) };
}

export type ProductDetail = NonNullable<Awaited<ReturnType<typeof getProduct>>>;

/** ราคา/ชื่อของหลาย SKU (ใช้เติมข้อมูลให้ผลเครื่องคำนวณ) */
export async function productsBySku(skus: string[]) {
  if (!skus.length) return {} as Record<string, { sku: string; name: string; unit: string; price: number; weight_kg: number }>;
  const r = await query<{ sku: string; name: string; unit: string; price: number; weight_kg: number }>(
    `SELECT sku, name, unit, price, weight_kg FROM products WHERE sku = ANY($1::text[])`,
    [skus],
  );
  return Object.fromEntries(r.rows.map((x) => [x.sku, x]));
}
