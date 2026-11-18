// /track (B2) — ติดตามคำสั่งซื้อ (เปิดตรงด้วย ?no=BM-…&phone=… จะค้นให้อัตโนมัติ)
import type { Metadata } from 'next';
import TrackView from './TrackView';
import '../cart/shop.css';

export const metadata: Metadata = { title: 'ติดตามคำสั่งซื้อ — บ้านช่าง BuildMart' };
export const dynamic = 'force-dynamic';

export default function TrackPage({ searchParams }: { searchParams: { no?: string; phone?: string } }) {
  return (
    <div className="b2-page">
      <h1>🚚 ติดตามคำสั่งซื้อ</h1>
      <p className="b2-sub">กรอกเลขที่คำสั่งซื้อ (BM-…) และเบอร์โทรที่ใช้สั่งซื้อ</p>
      <TrackView initialNo={searchParams.no || ''} initialPhone={searchParams.phone || ''} />
    </div>
  );
}
