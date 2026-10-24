// /cart (B2) — ตะกร้าสินค้า (เก็บใน DB ผูกกับ cookie bm_sid)
import type { Metadata } from 'next';
import CartView from './CartView';
import './shop.css';

export const metadata: Metadata = { title: 'ตะกร้าสินค้า — บ้านช่าง BuildMart' };
export const dynamic = 'force-dynamic';

export default function CartPage() {
  return (
    <div className="b2-page">
      <h1>🛒 ตะกร้าสินค้า</h1>
      <p className="b2-sub">ราคาส่งคิดอัตโนมัติตามจำนวน · เลือกสาขาและวันส่งในขั้นตอนชำระเงิน</p>
      <CartView />
    </div>
  );
}
