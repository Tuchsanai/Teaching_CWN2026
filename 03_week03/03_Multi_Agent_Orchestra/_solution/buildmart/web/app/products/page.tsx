// /products (B1) — รายการสินค้า: ค้นไทยบางส่วน · กรองหมวด/ราคา/มีของ · เรียงราคา · 12 ชิ้น/หน้า
import Link from 'next/link';
import { Suspense } from 'react';
import ProductCard from '@/components/ProductCard';
import ProductFilters from '@/components/ProductFilters';
import { parseSearch, searchProducts } from '../api/products/_lib';
import './products.css';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'สินค้าทั้งหมด — บ้านช่าง BuildMart' };

type SP = Record<string, string | string[] | undefined>;

function pageHref(sp: SP, page: number) {
  const u = new URLSearchParams();
  for (const [k, v] of Object.entries(sp)) {
    const val = Array.isArray(v) ? v[0] : v;
    if (val && k !== 'page') u.set(k, val);
  }
  if (page > 1) u.set('page', String(page));
  const qs = u.toString();
  return qs ? `/products?${qs}` : '/products';
}

export default async function ProductsPage({ searchParams }: { searchParams: SP }) {
  const s = parseSearch(searchParams);
  const { items, total, page, pages } = await searchProducts(s);
  const heading = s.category ? `หมวด${s.category}` : 'สินค้าทั้งหมด';

  return (
    <div className="products-page">
      <nav className="crumbs" aria-label="breadcrumb">
        <Link href="/">หน้าแรก</Link> › <span>สินค้า</span>
      </nav>
      <div className="pl-head">
        <h1>{heading}</h1>
        <p className="muted" data-testid="product-total">
          {s.q ? (
            <>
              ผลการค้นหา “<b>{s.q}</b>” ·{' '}
            </>
          ) : null}
          พบ {total.toLocaleString('th-TH')} รายการ{pages > 1 ? ` · หน้า ${page}/${pages}` : ''}
        </p>
      </div>

      <Suspense fallback={<div className="pf-bar card" />}>
        <ProductFilters />
      </Suspense>

      {items.length === 0 ? (
        <div className="empty card">
          <div className="big-ico">🔎</div>
          <p>ไม่พบสินค้าที่ตรงกับเงื่อนไข ลองเปลี่ยนคำค้นหรือล้างตัวกรอง</p>
          <Link className="btn secondary" href="/products">
            ดูสินค้าทั้งหมด
          </Link>
        </div>
      ) : (
        <div className="p-grid">
          {items.map((p) => (
            <ProductCard key={p.sku} p={p} />
          ))}
        </div>
      )}

      {pages > 1 && (
        <nav className="pager" aria-label="แบ่งหน้า">
          {page > 1 ? (
            <Link className="btn secondary" href={pageHref(searchParams, page - 1)} data-testid="pagination-prev">
              ‹ ก่อนหน้า
            </Link>
          ) : (
            <button className="btn secondary" disabled data-testid="pagination-prev">
              ‹ ก่อนหน้า
            </button>
          )}
          {Array.from({ length: pages }, (_, i) => i + 1).map((n) => (
            <Link
              key={n}
              href={pageHref(searchParams, n)}
              className={`pg-num${n === page ? ' active' : ''}`}
              aria-current={n === page ? 'page' : undefined}
              data-testid="pagination-page"
            >
              {n}
            </Link>
          ))}
          {page < pages ? (
            <Link className="btn secondary" href={pageHref(searchParams, page + 1)} data-testid="pagination-next">
              ถัดไป ›
            </Link>
          ) : (
            <button className="btn secondary" disabled data-testid="pagination-next">
              ถัดไป ›
            </button>
          )}
        </nav>
      )}
    </div>
  );
}
