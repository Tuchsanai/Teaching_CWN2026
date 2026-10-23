'use client';
// app/quote/QuoteForm.tsx (B2) — ขอใบเสนอราคาจากตะกร้า (ชื่อ/บริษัท/เลขผู้เสียภาษี ไม่บังคับ) → /quote/QT-…
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { api, baht, TotalsBox, type Cart } from '../cart/Summary';

export default function QuoteForm() {
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [f, setF] = useState({ name: '', company: '', taxId: '' });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');

  useEffect(() => {
    api<Cart>('/api/cart')
      .then(setCart)
      .catch(() => setErr('โหลดตะกร้าไม่สำเร็จ'));
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setErr('');
    try {
      const r = await api<{ quoteNo: string }>('/api/quotes', { method: 'POST', json: f });
      router.push(`/quote/${r.quoteNo}`);
    } catch (e: any) {
      setErr(e.message);
      setBusy(false);
    }
  };

  if (!cart) return <div className="b2-card">{err || 'กำลังโหลด…'}</div>;
  if (!cart.items.length) {
    return (
      <div className="b2-card b2-empty">
        <div className="big" aria-hidden>
          📄
        </div>
        <h2>ตะกร้าว่าง</h2>
        <p>เพิ่มสินค้าลงตะกร้าก่อน แล้วจึงขอใบเสนอราคา</p>
        <Link href="/products" className="btn">
          เลือกซื้อสินค้า
        </Link>
      </div>
    );
  }

  return (
    <form className="b2-grid" onSubmit={submit}>
      <section className="b2-card">
        <h2>ข้อมูลผู้ขอใบเสนอราคา</h2>
        <div className="b2-form">
          <label>
            ชื่อผู้ติดต่อ <span className="muted">(ไม่บังคับ)</span>
            <input className="input" data-testid="quote-name" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
          </label>
          <label>
            บริษัท / หน่วยงาน <span className="muted">(ไม่บังคับ)</span>
            <input className="input" data-testid="quote-company" value={f.company} onChange={(e) => setF({ ...f, company: e.target.value })} />
          </label>
          <label>
            เลขประจำตัวผู้เสียภาษี <span className="muted">(ไม่บังคับ · 13 หลัก)</span>
            <input
              className="input"
              data-testid="quote-taxid"
              inputMode="numeric"
              maxLength={20}
              value={f.taxId}
              onChange={(e) => setF({ ...f, taxId: e.target.value })}
            />
          </label>
          {err && <div className="b2-msg err">{err}</div>}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <button className="btn" type="submit" data-testid="quote-submit" disabled={busy}>
              {busy ? 'กำลังออกใบเสนอราคา…' : '📄 ออกใบเสนอราคา'}
            </button>
            <Link href="/cart" className="btn secondary">
              ← กลับตะกร้า
            </Link>
          </div>
          <p className="muted" style={{ fontSize: 13, margin: 0 }}>
            ใบเสนอราคามีอายุ 7 วัน พิมพ์หรือบันทึกเป็น PDF ได้ และแปลงเป็นคำสั่งซื้อได้ทันที
          </p>
        </div>
      </section>
      <aside className="b2-card">
        <h2>รายการในตะกร้า</h2>
        <div className="b2-mini">
          {cart.items.map((i) => (
            <div className="it" key={i.sku}>
              <span>
                {i.name} × {i.qty.toLocaleString()}
              </span>
              <span>{baht(i.lineTotal)}</span>
            </div>
          ))}
        </div>
        <TotalsBox t={cart.totals} count={cart.count} />
      </aside>
    </form>
  );
}
