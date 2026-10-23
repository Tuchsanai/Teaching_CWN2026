import Link from 'next/link';
import { CATEGORIES } from '@/lib/categories';

export default function HomePage() {
  return (
    <>
      <section className="hero">
        <h1>วัสดุก่อสร้างครบ จบที่บ้านช่าง</h1>
        <p>
          ปูน เหล็ก อิฐ กระเบื้อง สี ประปา ไฟฟ้า — ซื้อเยอะยิ่งถูก (50 ชิ้นขึ้นไปลด 5% · 200 ชิ้นขึ้นไปลด 10%)
          ส่งจาก 3 สาขา ลาดกระบัง · บางนา · รังสิต
        </p>
        <div className="actions">
          <Link href="/products" className="btn">
            ดูสินค้าทั้งหมด
          </Link>
          <Link href="/calculator" className="btn secondary">
            คำนวณวัสดุ
          </Link>
        </div>
      </section>

      <h2 className="section-title">หมวดสินค้า</h2>
      <div className="cat-grid">
        {CATEGORIES.map((c) => (
          <Link
            key={c.name}
            href={`/products?category=${encodeURIComponent(c.name)}`}
            className="cat-tile"
            data-testid="category-tile"
            data-category={c.name}
          >
            <span className="icon" aria-hidden>
              {c.icon}
            </span>
            <span className="label">{c.name}</span>
          </Link>
        ))}
      </div>
    </>
  );
}
