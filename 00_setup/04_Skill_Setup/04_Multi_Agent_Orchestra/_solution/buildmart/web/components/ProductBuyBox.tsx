'use client';
// components/ProductBuyBox.tsx (B1) — เลือกจำนวน → แสดงราคาส่งที่ได้ → เพิ่มลงตะกร้า (POST /api/cart)
import Link from 'next/link';
import { useState } from 'react';
import { formatBaht, round2, tierOf, tierPrice } from '@/shared/pricing.js';
import { addToCart, notifyCart } from './ProductCart';

export default function ProductBuyBox({
  sku,
  price,
  unit,
  totalStock,
}: {
  sku: string;
  price: number;
  unit: string;
  totalStock: number;
}) {
  const [qty, setQty] = useState('1');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const n = Math.max(0, Math.floor(Number(qty) || 0));
  const unitPrice = tierPrice(price, n || 1);
  const tier = tierOf(n || 1);
  const out = totalStock <= 0;

  async function onAdd() {
    if (n < 1) {
      setMsg({ ok: false, text: 'กรุณาใส่จำนวนอย่างน้อย 1' });
      return;
    }
    setBusy(true);
    setMsg(null);
    try {
      const { count } = await addToCart(sku, n);
      notifyCart(count);
      setMsg({ ok: true, text: `เพิ่ม ${sku} × ${n.toLocaleString('th-TH')} ${unit} ลงตะกร้าแล้ว` });
    } catch (e: any) {
      setMsg({ ok: false, text: e?.message || 'เพิ่มลงตะกร้าไม่สำเร็จ' });
    } finally {
      setBusy(false);
    }
  }

  const step = (d: number) => setQty(String(Math.max(1, n + d)));

  return (
    <div className="buy-box card">
      <div className="buy-price">
        <span className="price big">฿{formatBaht(unitPrice)}</span>
        <span className="muted"> / {unit}</span>
        {tier > 1 && <span className="tier-chip">ราคาส่งขั้น {tier} (ลด {tier === 2 ? 5 : 10}%)</span>}
      </div>
      <div className="buy-row">
        <div className="qty">
          <button type="button" aria-label="ลดจำนวน" onClick={() => step(-1)}>
            −
          </button>
          <input
            data-testid="qty-input"
            type="number"
            min={1}
            inputMode="numeric"
            value={qty}
            onChange={(e) => setQty(e.target.value)}
            aria-label="จำนวน"
          />
          <button type="button" aria-label="เพิ่มจำนวน" onClick={() => step(1)}>
            +
          </button>
        </div>
        <button type="button" className="btn add" data-testid="add-to-cart" onClick={onAdd} disabled={busy || out}>
          {busy ? 'กำลังเพิ่ม…' : out ? 'สินค้าหมด' : '🛒 เพิ่มลงตะกร้า'}
        </button>
      </div>
      <div className="muted small">
        รวม {n.toLocaleString('th-TH')} {unit} ≈ <b>฿{formatBaht(round2(unitPrice * n))}</b> (ยังไม่รวม VAT 7%)
      </div>
      {msg && (
        <div className={`buy-msg ${msg.ok ? 'ok' : 'err'}`} role="status">
          {msg.text}
          {msg.ok && (
            <>
              {' '}
              · <Link href="/cart">ไปที่ตะกร้า →</Link>
            </>
          )}
        </div>
      )}
    </div>
  );
}
