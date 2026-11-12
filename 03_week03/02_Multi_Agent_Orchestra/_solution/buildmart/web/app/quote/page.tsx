// /quote (B2) — ฟอร์มขอใบเสนอราคาจากตะกร้า
import type { Metadata } from 'next';
import QuoteForm from './QuoteForm';
import '../cart/shop.css';

export const metadata: Metadata = { title: 'ขอใบเสนอราคา — บ้านช่าง BuildMart' };
export const dynamic = 'force-dynamic';

export default function QuoteRequestPage() {
  return (
    <div className="b2-page">
      <h1>📄 ขอใบเสนอราคา</h1>
      <p className="b2-sub">ออกใบเสนอราคาจากสินค้าในตะกร้า ราคาส่ง คูปอง และค่าส่งคิดให้ครบ</p>
      <QuoteForm />
    </div>
  );
}
