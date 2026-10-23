'use client';
// app/cart/CartView.tsx (B2) — ตะกร้า: ราคาส่งต่อรายการ · แก้จำนวน · คูปอง · รถ/ค่าส่ง/VAT/ยอดสุทธิ
import Link from 'next/link';
import { useCallback, useEffect, useRef, useState } from 'react';
import { api, baht, notifyCart, TotalsBox, type Cart, type CartItem } from './Summary';

function nextTierHint(it: CartItem) {
  if (it.qty < 50) return `ซื้อเพิ่มอีก ${50 - it.qty} ${it.unit} ได้ราคาส่ง ลด 5%`;
  if (it.qty < 200) return `ซื้อเพิ่มอีก ${200 - it.qty} ${it.unit} ได้ราคาส่ง ลด 10%`;
  return null;
}

function QtyBox({ item, onSet }: { item: CartItem; onSet: (sku: string, qty: number) => void }) {
  const [v, setV] = useState(String(item.qty));
  const timer = useRef<ReturnType<typeof setTimeout>>();
  useEffect(() => setV(String(item.qty)), [item.qty]);
  const commit = (raw: string) => {
    clearTimeout(timer.current);
    const n = Math.floor(Number(raw));
    if (!Number.isFinite(n) || raw.trim() === '') return setV(String(item.qty));
    if (n !== item.qty) onSet(item.sku, n);
  };
  return (
    <div className="b2-qty">
      <button type="button" aria-label="ลดจำนวน" onClick={() => onSet(item.sku, item.qty - 1)}>
        −
      </button>
      <input
        type="number"
        min={0}
        inputMode="numeric"
        data-testid="cart-qty"
        aria-label={`จำนวน ${item.name}`}
        value={v}
        onChange={(e) => {
          setV(e.target.value);
          clearTimeout(timer.current);
          const raw = e.target.value;
          timer.current = setTimeout(() => commit(raw), 700);
        }}
        onBlur={(e) => commit(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && commit((e.target as HTMLInputElement).value)}
      />
      <button type="button" aria-label="เพิ่มจำนวน" onClick={() => onSet(item.sku, item.qty + 1)}>
        +
      </button>
    </div>
  );
}

export default function CartView() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const [code, setCode] = useState('');
  const [couponMsg, setCouponMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const apply = useCallback((c: Cart) => {
    setCart(c);
    notifyCart(c.count);
  }, []);

  useEffect(() => {
    api<Cart>('/api/cart')
      .then(setCart)
      .catch(() => setErr('โหลดตะกร้าไม่สำเร็จ ลองรีเฟรชหน้า'));
  }, []);

  const run = async (fn: () => Promise<Cart>) => {
    setBusy(true);
    setErr('');
    try {
      apply(await fn());
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  const setQty = (sku: string, qty: number) =>
    run(() => api<Cart>('/api/cart', { method: 'PATCH', json: { sku, qty: Math.max(0, qty) } }));
  const remove = (sku: string) => run(() => api<Cart>('/api/cart', { method: 'DELETE', json: { sku } }));

  const applyCoupon = async (c: string) => {
    setBusy(true);
    setCouponMsg(null);
    try {
      const next = await api<Cart>('/api/cart/coupon', { method: 'POST', json: { code: c } });
      apply(next);
      setCouponMsg(c ? { ok: true, text: `ใช้คูปอง ${next.coupon} แล้ว ลด ${baht(next.totals.discount)} บาท` } : null);
      setCode('');
    } catch (e: any) {
      setCouponMsg({ ok: false, text: e.message });
    } finally {
      setBusy(false);
    }
  };

  if (!cart) {
    return <div className="b2-card">{err || 'กำลังโหลดตะกร้า…'}</div>;
  }

  if (!cart.items.length) {
    return (
      <div className="b2-card b2-empty">
        <div className="big" aria-hidden>
          🛒
        </div>
        <h2>ตะกร้ายังว่างอยู่</h2>
        <p>เลือกสินค้าหรือใช้เครื่องคำนวณวัสดุ แล้วกด “เพิ่มลงตะกร้า”</p>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/products" className="btn">
            เลือกซื้อสินค้า
          </Link>
          <Link href="/calculator" className="btn secondary">
            คำนวณวัสดุ
          </Link>
        </div>
      </div>
    );
  }

  const t = cart.totals;
  return (
    <div className="b2-grid">
      <section className="b2-card" aria-busy={busy}>
        <h2>รายการสินค้า ({cart.items.length} รายการ)</h2>
        <table className="b2-table resp">
          <thead>
            <tr>
              <th>สินค้า</th>
              <th className="num">ราคา/หน่วย</th>
              <th>จำนวน</th>
              <th className="num">รวม</th>
              <th aria-label="ลบ" />
            </tr>
          </thead>
          <tbody>
            {cart.items.map((it) => {
              const hint = nextTierHint(it);
              return (
                <tr key={it.sku} data-testid="cart-row" data-sku={it.sku}>
                  <td className="wide">
                    <Link href={`/products/${it.sku}`} className="b2-name">
                      {it.name}
                    </Link>
                    <span className="b2-sku">
                      {it.sku} · {Number(it.weightPerUnit).toLocaleString()} กก./{it.unit}
                    </span>
                    {hint && <div className="b2-hint">💡 {hint}</div>}
                  </td>
                  <td className="num">
                    {it.tier > 1 && <span className="b2-strike">{baht(it.price)}</span>}
                    <span data-testid="cart-unit-price" className="price">
                      {baht(it.unitPrice)}
                    </span>
                    {it.tier > 1 && <span className="b2-tier">−{it.tier === 2 ? 5 : 10}%</span>}
                    <div className="muted" style={{ fontSize: 12 }}>
                      บาท/{it.unit}
                    </div>
                  </td>
                  <td>
                    <QtyBox item={it} onSet={setQty} />
                  </td>
                  <td className="num">
                    <b data-testid="cart-line-total">{baht(it.lineTotal)}</b>
                  </td>
                  <td>
                    <button className="b2-remove" title="ลบออกจากตะกร้า" aria-label={`ลบ ${it.name}`} onClick={() => remove(it.sku)}>
                      🗑
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {err && <div className="b2-msg err">{err}</div>}
        <p className="muted" style={{ fontSize: 13, marginBottom: 0 }}>
          ราคาส่งคิดต่อรายการ: 1–49 ชิ้น ราคาปกติ · 50–199 ชิ้น ลด 5% · 200 ชิ้นขึ้นไป ลด 10% · ราคายังไม่รวม VAT
        </p>
      </section>

      <aside>
        <div className="b2-card">
          <h2>คูปองส่วนลด</h2>
          {t.coupon ? (
            <div style={{ marginBottom: 8 }}>
              <span className="b2-chip">
                🏷 {t.coupon}
                <button aria-label="เอาคูปองออก" onClick={() => applyCoupon('')}>
                  ✕
                </button>
              </span>
            </div>
          ) : null}
          <form
            className="b2-coupon"
            onSubmit={(e) => {
              e.preventDefault();
              if (code.trim()) applyCoupon(code.trim());
            }}
          >
            <input
              className="input"
              data-testid="coupon-input"
              placeholder="เช่น BUILD5"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              aria-label="รหัสคูปอง"
            />
            <button className="btn secondary" type="submit" data-testid="coupon-apply" disabled={busy}>
              ใช้คูปอง
            </button>
          </form>
          {couponMsg && <div className={`b2-msg ${couponMsg.ok ? 'ok' : 'err'}`}>{couponMsg.text}</div>}
          {t.couponError && <div className="b2-msg warn">{t.couponError}</div>}
          <div className="muted" style={{ fontSize: 12 }}>
            BUILD5 ลด 5% (ยอด ≥ 5,000) · CONTRACTOR10 ลด 10% (ยอด ≥ 30,000) · ใช้ได้ทีละ 1 ใบ
          </div>
        </div>

        <div className="b2-card">
          <h2>สรุปยอด</h2>
          <TotalsBox t={t} count={cart.count} />
          <div className="b2-actions">
            <Link href="/checkout" className="btn" data-testid="checkout-btn">
              ไปชำระเงิน →
            </Link>
            <Link href="/quote" className="btn secondary" data-testid="request-quote-btn">
              📄 ขอใบเสนอราคา
            </Link>
          </div>
        </div>
      </aside>
    </div>
  );
}
