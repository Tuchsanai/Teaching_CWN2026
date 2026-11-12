// /products/[sku] (B1) — สเปก · น้ำหนัก · ตารางราคาส่ง 3 ขั้น · สต็อก 3 สาขา ("หมด" ถ้า 0) · เพิ่มลงตะกร้า
import Link from 'next/link';
import { notFound } from 'next/navigation';
import ProductBuyBox from '@/components/ProductBuyBox';
import { ProductImage } from '@/components/CatImage';
import { formatBaht } from '@/shared/pricing.js';
import { getProduct } from '../../api/products/_lib';
import '../products.css';

export const dynamic = 'force-dynamic';

export async function generateMetadata({ params }: { params: { sku: string } }) {
  const p = await getProduct(decodeURIComponent(params.sku)).catch(() => null);
  return { title: p ? `${p.name} (${p.sku}) — บ้านช่าง BuildMart` : 'ไม่พบสินค้า — บ้านช่าง BuildMart' };
}

const fmtQty = (n: number) => n.toLocaleString('th-TH');
const fmtKg = (n: number) => Number(n).toLocaleString('th-TH', { maximumFractionDigits: 3 });
const DISCOUNT = ['ราคาปกติ', 'ลด 5%', 'ลด 10%'];

export default async function ProductPage({ params }: { params: { sku: string } }) {
  const p = await getProduct(decodeURIComponent(params.sku));
  if (!p) notFound();
  const tierLabel = (t: { minQty: number; maxQty: number | null }) =>
    t.maxQty ? `${fmtQty(t.minQty)}–${fmtQty(t.maxQty)} ${p.unit}` : `${fmtQty(t.minQty)} ${p.unit} ขึ้นไป`;

  return (
    <div className="product-page">
      <nav className="crumbs" aria-label="breadcrumb">
        <Link href="/">หน้าแรก</Link> › <Link href="/products">สินค้า</Link> ›{' '}
        <Link href={`/products?category=${encodeURIComponent(p.category)}`}>{p.category}</Link> › <span>{p.sku}</span>
      </nav>

      <div className="pd-grid">
        <div className="pd-visual card" aria-hidden>
          <ProductImage sku={p.sku} category={p.category} className="pd-visual-img" />
          <span className="pd-visual-sku">{p.sku}</span>
        </div>

        <div className="pd-info">
          <div className="p-meta">
            <span className="p-sku" data-testid="product-sku">
              {p.sku}
            </span>
            <span className="p-cat">{p.category}</span>
          </div>
          <h1 className="pd-name" data-testid="product-name">
            {p.name}
          </h1>
          {p.description && <p className="pd-desc">{p.description}</p>}

          <dl className="pd-spec">
            <div>
              <dt>ราคาปกติ</dt>
              <dd>
                ฿{formatBaht(p.price)} / {p.unit}
              </dd>
            </div>
            <div>
              <dt>หน่วยขาย</dt>
              <dd>{p.unit}</dd>
            </div>
            <div>
              <dt>น้ำหนัก</dt>
              <dd>
                {fmtKg(p.weight_kg)} กก. / {p.unit}
              </dd>
            </div>
            <div>
              <dt>หมวด</dt>
              <dd>{p.category}</dd>
            </div>
          </dl>

          <ProductBuyBox sku={p.sku} price={p.price} unit={p.unit} totalStock={p.totalStock} />
        </div>
      </div>

      <div className="pd-tables">
        <section className="card">
          <h2>ราคาส่งตามจำนวน</h2>
          <table className="tbl">
            <thead>
              <tr>
                <th>จำนวนต่อรายการ</th>
                <th>ส่วนลด</th>
                <th className="r">ราคา / {p.unit}</th>
              </tr>
            </thead>
            <tbody>
              {p.tiers.map((t) => (
                <tr key={t.tier}>
                  <td>{tierLabel(t)}</td>
                  <td>{DISCOUNT[t.tier - 1]}</td>
                  <td className="r">
                    <span className="price" data-testid={`tier-price-${t.tier}`}>
                      {formatBaht(t.price)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="muted small">ราคายังไม่รวม VAT 7% · ราคาส่งคิดแยกต่อรายการสินค้า</p>
        </section>

        <section className="card">
          <h2>สต็อกแต่ละสาขา</h2>
          <table className="tbl">
            <thead>
              <tr>
                <th>สาขา</th>
                <th>โทร</th>
                <th className="r">คงเหลือ</th>
              </tr>
            </thead>
            <tbody>
              {p.stock.map((s) => (
                <tr key={s.branch}>
                  <td>
                    <b>{s.branch}</b> {s.name}
                  </td>
                  <td className="muted">{s.phone}</td>
                  <td className="r">
                    <span className={`stock-pill ${s.qty > 0 ? 'in' : 'out'}`} data-testid={`stock-${s.branch}`}>
                      {s.qty > 0 ? `${fmtQty(s.qty)} ${p.unit}` : 'หมด'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="muted small">เลือกสาขาที่จัดส่งได้ตอนชำระเงิน</p>
        </section>
      </div>
    </div>
  );
}
