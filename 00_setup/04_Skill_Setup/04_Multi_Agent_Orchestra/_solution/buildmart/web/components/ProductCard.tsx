// components/ProductCard.tsx (B1) — การ์ดสินค้าในหน้ารายการ
import Link from 'next/link';
import { CATEGORIES } from '@/lib/categories';
import { ProductImage } from '@/components/CatImage';
import { formatBaht } from '@/shared/pricing.js';

export type ProductCardData = {
  sku: string;
  name: string;
  category: string;
  unit: string;
  price: number;
  totalStock: number;
};

export function categoryIcon(category: string) {
  return CATEGORIES.find((c) => c.name === category)?.icon || '📦';
}

export default function ProductCard({ p }: { p: ProductCardData }) {
  const out = p.totalStock <= 0;
  return (
    <Link href={`/products/${encodeURIComponent(p.sku)}`} className="p-card tilt" data-testid="product-card" data-sku={p.sku}>
      <div className="p-thumb" aria-hidden>
        <ProductImage sku={p.sku} category={p.category} className="p-thumb-img" />
        <span className={`p-badge ${out ? 'out' : 'in'}`}>{out ? 'หมด' : 'พร้อมส่ง'}</span>
      </div>
      <div className="p-body">
        <div className="p-meta">
          <span className="p-sku">{p.sku}</span>
          <span className="p-cat">{p.category}</span>
        </div>
        <div className="p-name">{p.name}</div>
        <div className="p-foot">
          <span>
            <span className="price">฿{formatBaht(p.price)}</span>
            <span className="muted"> / {p.unit}</span>
          </span>
          <span className={`p-stock ${out ? 'out' : 'in'}`}>{out ? 'หมด' : 'มีของ'}</span>
        </div>
      </div>
    </Link>
  );
}
