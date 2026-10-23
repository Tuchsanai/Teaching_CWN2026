'use client';
// app/quote/[no]/QuoteActions.tsx (B2) — ปุ่มพิมพ์ + แปลงเป็นคำสั่งซื้อ (เติมตะกร้าจากใบเสนอราคา แล้วไป /checkout)
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { api, notifyCart } from '../../cart/Summary';

export default function QuoteActions({ quoteNo, expired }: { quoteNo: string; expired: boolean }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  const toOrder = async () => {
    setBusy(true);
    setErr('');
    try {
      const r = await api<{ redirect: string; count: number }>(`/api/quotes/${quoteNo}/order`, { method: 'POST' });
      notifyCart(r.count);
      router.push(r.redirect || '/checkout');
    } catch (e: any) {
      setErr(e.message);
      setBusy(false);
    }
  };

  return (
    <>
      <div className="b2-toolbar no-print">
        <button className="btn secondary" type="button" onClick={() => window.print()} data-testid="quote-print">
          🖨 พิมพ์ / บันทึก PDF
        </button>
        <button className="btn" type="button" onClick={toOrder} disabled={busy || expired} data-testid="quote-to-order">
          {busy ? 'กำลังแปลง…' : '🛒 แปลงเป็นคำสั่งซื้อ'}
        </button>
        <Link href="/cart" className="btn secondary">
          กลับตะกร้า
        </Link>
      </div>
      {err && (
        <div className="b2-msg err no-print" style={{ maxWidth: 900, margin: '10px auto' }}>
          {err}
        </div>
      )}
    </>
  );
}
