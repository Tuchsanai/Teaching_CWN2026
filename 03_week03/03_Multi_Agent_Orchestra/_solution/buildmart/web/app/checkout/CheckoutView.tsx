'use client';
// app/checkout/CheckoutView.tsx (B2) — กรอกข้อมูลจัดส่ง · เลือกสาขา/วันส่ง/ช่วงเวลา · สั่งซื้อ → เลข BM-…
import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { api, baht, notifyCart, TotalsBox, type Cart } from '../cart/Summary';

type Branch = { code: string; name: string; phone: string };
type Short = { sku: string; name: string; unit: string; need: number; available: number };

export default function CheckoutView({ branches, dates }: { branches: Branch[]; dates: { value: string; label: string }[] }) {
  const [cart, setCart] = useState<Cart | null>(null);
  const [form, setForm] = useState({
    name: '',
    phone: '',
    address: '',
    branch: branches[0].code,
    deliveryDate: dates[0]?.value ?? '',
    slot: 'morning',
  });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const [serverShort, setServerShort] = useState<{ branch: string; items: Short[] } | null>(null);
  const [done, setDone] = useState<{ orderNo: string; total: number; phone: string } | null>(null);

  useEffect(() => {
    api<Cart>('/api/cart')
      .then(setCart)
      .catch(() => setErr('โหลดตะกร้าไม่สำเร็จ'));
  }, []);

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm((f) => ({ ...f, [k]: e.target.value }));
    if (k === 'branch') setServerShort(null);
  };

  /** รายการที่สาขานั้นมีไม่พอ (เช็คล่วงหน้าจากข้อมูลตะกร้า · server เช็คซ้ำตอนสั่งจริง) */
  const shortOf = (code: string): Short[] =>
    (cart?.items || [])
      .filter((i) => (i.stock?.[code] ?? 0) < i.qty)
      .map((i) => ({ sku: i.sku, name: i.name, unit: i.unit, need: i.qty, available: i.stock?.[code] ?? 0 }));

  const short = useMemo(
    () => (serverShort && serverShort.branch === form.branch ? serverShort.items : shortOf(form.branch)),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [cart, form.branch, serverShort],
  );
  const branchName = branches.find((b) => b.code === form.branch)?.name ?? form.branch;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setErr('');
    setServerShort(null);
    try {
      const r = await api<{ orderNo: string; total: number }>('/api/checkout', { method: 'POST', json: form });
      setDone({ orderNo: r.orderNo, total: r.total, phone: form.phone });
      notifyCart(0);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (e: any) {
      if (e.status === 409 && e.body?.items) setServerShort({ branch: form.branch, items: e.body.items });
      else setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    const trackUrl = `/track?no=${encodeURIComponent(done.orderNo)}&phone=${encodeURIComponent(done.phone)}`;
    return (
      <div className="b2-card b2-success">
        <div className="big" aria-hidden>
          ✅
        </div>
        <h2>สั่งซื้อสำเร็จ ขอบคุณที่ใช้บริการบ้านช่าง</h2>
        <div>เลขที่คำสั่งซื้อ</div>
        <div className="b2-docno" data-testid="order-no">
          {done.orderNo}
        </div>
        <p className="muted">
          ยอดสุทธิ {baht(done.total)} บาท · ส่งจากสาขา{branchName} · เก็บเลขนี้ไว้ใช้ติดตามสถานะพร้อมเบอร์โทร
        </p>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href={trackUrl} className="btn" data-testid="go-track">
            ติดตามคำสั่งซื้อ
          </Link>
          <Link href="/products" className="btn secondary">
            เลือกซื้อสินค้าต่อ
          </Link>
        </div>
      </div>
    );
  }

  if (!cart) return <div className="b2-card">{err || 'กำลังโหลด…'}</div>;

  if (!cart.items.length) {
    return (
      <div className="b2-card b2-empty">
        <div className="big" aria-hidden>
          🛒
        </div>
        <h2>ยังไม่มีสินค้าในตะกร้า</h2>
        <p>เพิ่มสินค้าลงตะกร้าก่อนชำระเงิน</p>
        <Link href="/products" className="btn">
          เลือกซื้อสินค้า
        </Link>
      </div>
    );
  }

  return (
    <form className="b2-grid" onSubmit={submit}>
      <section>
        <div className="b2-card">
          <h2>1. ข้อมูลผู้สั่งซื้อ</h2>
          <div className="b2-form">
            <div className="two">
              <label>
                ชื่อ-นามสกุล
                <input className="input" data-testid="checkout-name" value={form.name} onChange={set('name')} required autoComplete="name" />
              </label>
              <label>
                เบอร์โทร
                <input
                  className="input"
                  data-testid="checkout-phone"
                  value={form.phone}
                  onChange={set('phone')}
                  required
                  inputMode="tel"
                  autoComplete="tel"
                  placeholder="08x-xxx-xxxx"
                />
              </label>
            </div>
            <label>
              ที่อยู่จัดส่ง / หน้างาน
              <textarea data-testid="checkout-address" value={form.address} onChange={set('address')} required autoComplete="street-address" />
            </label>
          </div>
        </div>

        <div className="b2-card">
          <h2>2. สาขาที่ส่งของ และวันส่ง</h2>
          <div className="b2-form">
            <label>
              สาขา (คลังสินค้า)
              <select className="select" data-testid="branch-select" value={form.branch} onChange={set('branch')}>
                {branches.map((b) => {
                  const n = shortOf(b.code).length;
                  return (
                    <option key={b.code} value={b.code}>
                      {b.code} {b.name} — {n ? `ของไม่พอ ${n} รายการ` : 'ของครบ'}
                    </option>
                  );
                })}
              </select>
            </label>
            <div className="b2-branches" aria-hidden>
              {branches.map((b) => {
                const n = shortOf(b.code).length;
                return (
                  <button
                    type="button"
                    key={b.code}
                    tabIndex={-1}
                    className={`b2-branch${form.branch === b.code ? ' sel' : ''}`}
                    onClick={() => {
                      setForm((f) => ({ ...f, branch: b.code }));
                      setServerShort(null);
                    }}
                  >
                    <b>
                      {b.name} ({b.code})
                    </b>
                    <span className={n ? 'no' : 'ok'}>{n ? `✗ ของไม่พอ ${n} รายการ` : '✓ มีของครบ'}</span>
                    <div className="muted">โทร {b.phone}</div>
                  </button>
                );
              })}
            </div>
            {short.length > 0 && (
              <div className="b2-msg err" data-testid="stock-error" role="alert">
                <b>⚠ สินค้าที่สาขา{branchName}มีไม่พอ — สั่งซื้อไม่ได้</b> กรุณาเลือกสาขาอื่นหรือลดจำนวน
                <ul>
                  {short.map((s) => (
                    <li key={s.sku}>
                      {s.sku} {s.name}: ต้องการ {s.need.toLocaleString()} {s.unit} · คงเหลือ {s.available.toLocaleString()} {s.unit}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="two">
              <label>
                วันส่ง <span className="muted">(ภายใน 7 วัน · ไม่ส่งวันอาทิตย์)</span>
                <select className="select" data-testid="delivery-date" value={form.deliveryDate} onChange={set('deliveryDate')}>
                  {dates.map((d) => (
                    <option key={d.value} value={d.value}>
                      {d.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                ช่วงเวลา
                <select className="select" data-testid="delivery-slot" value={form.slot} onChange={set('slot')}>
                  <option value="morning">ช่วงเช้า 08:00–12:00</option>
                  <option value="afternoon">ช่วงบ่าย 13:00–17:00</option>
                </select>
              </label>
            </div>
          </div>
        </div>
      </section>

      <aside>
        <div className="b2-card">
          <h2>3. สรุปคำสั่งซื้อ</h2>
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
          {err && <div className="b2-msg err">{err}</div>}
          <div className="b2-actions">
            <button className="btn" type="submit" data-testid="place-order" disabled={busy}>
              {busy ? 'กำลังสั่งซื้อ…' : `ยืนยันสั่งซื้อ ฿${baht(cart.totals.total)}`}
            </button>
            <Link href="/cart" className="btn secondary">
              ← กลับไปแก้ตะกร้า
            </Link>
          </div>
          <p className="muted" style={{ fontSize: 12, marginBottom: 0 }}>
            ชำระเงินปลายทางเมื่อรับสินค้า · ระบบตัดสต็อกจากสาขาที่เลือกทันทีที่ยืนยัน
          </p>
        </div>
      </aside>
    </form>
  );
}
