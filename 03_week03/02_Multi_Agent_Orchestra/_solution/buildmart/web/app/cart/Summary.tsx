'use client';
// app/cart/Summary.tsx (B2) — ส่วนที่ใช้ร่วมกันของหน้า ตะกร้า / ชำระเงิน / ใบเสนอราคา
import { formatBaht } from '@/shared/pricing.js';

export type CartItem = {
  sku: string;
  name: string;
  unit: string;
  price: number;
  qty: number;
  unitPrice: number;
  lineTotal: number;
  weight: number;
  weightPerUnit: number;
  tier: 1 | 2 | 3;
  stock: Record<string, number>;
};

export type Totals = {
  subtotal: number;
  discount: number;
  coupon: string | null;
  afterDiscount: number;
  weight: number;
  vehicle: 'pickup' | '6wheel' | '10wheel';
  vehicleLabel: string;
  shipping: number;
  vat: number;
  total: number;
  couponError?: string;
};

export type Cart = { cartId: string | null; coupon: string | null; items: CartItem[]; totals: Totals; count: number };

export const baht = (n: number) => formatBaht(n);
export const kg = (n: number) => Number(n || 0).toLocaleString('en-US', { maximumFractionDigits: 2 });

/** แจ้ง header ให้อัปเดตตัวเลขตะกร้า (ไม่ส่ง count = ให้ header ดึงใหม่เอง) */
export function notifyCart(count?: number) {
  window.dispatchEvent(new CustomEvent('bm:cart', typeof count === 'number' ? { detail: { count } } : undefined));
}

export async function api<T = any>(url: string, init?: RequestInit & { json?: unknown }): Promise<T> {
  const { json, ...rest } = init || {};
  const res = await fetch(url, {
    cache: 'no-store',
    ...rest,
    headers: { 'content-type': 'application/json', accept: 'application/json', ...(rest.headers || {}) },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error(body?.message || body?.error || `HTTP ${res.status}`), { status: res.status, body });
  return body as T;
}

const VEHICLE_ICON: Record<string, string> = { pickup: '🛻', '6wheel': '🚚', '10wheel': '🚛' };

/** สรุปยอดตามลำดับข้อ 1: ยอดสินค้า → คูปอง → ค่าส่ง → VAT 7% → ยอดสุทธิ */
export function TotalsBox({ t, count }: { t: Totals; count?: number }) {
  const freeShip = t.vehicle === 'pickup' && t.weight > 0 && t.shipping === 0;
  return (
    <div className="b2-sum">
      <div className="row">
        <span>ยอดสินค้า{typeof count === 'number' ? ` (${count.toLocaleString()} ชิ้น)` : ''}</span>
        <span data-testid="cart-subtotal">{baht(t.subtotal)}</span>
      </div>
      <div className="row disc">
        <span>ส่วนลดคูปอง{t.coupon ? ` ${t.coupon}` : ''}</span>
        <span>
          −<span data-testid="cart-discount">{baht(t.discount)}</span>
        </span>
      </div>
      <div className="row">
        <span>ยอดหลังส่วนลด</span>
        <span data-testid="cart-after-discount">{baht(t.afterDiscount)}</span>
      </div>
      <div className="b2-truck">
        <span className="ico" aria-hidden>
          {VEHICLE_ICON[t.vehicle] || '🚚'}
        </span>
        <span>
          <b data-testid="cart-vehicle">{t.vehicleLabel}</b>
          <small>
            น้ำหนักรวม <span data-testid="cart-weight">{kg(t.weight)} กก.</span>
          </small>
        </span>
      </div>
      <div className="row">
        <span>ค่าส่ง</span>
        <span>
          {freeShip && <span className="b2-free">ส่งฟรี · </span>}
          <span data-testid="cart-shipping">{baht(t.shipping)}</span>
        </span>
      </div>
      <div className="row">
        <span>VAT 7%</span>
        <span data-testid="cart-vat">{baht(t.vat)}</span>
      </div>
      <div className="row total">
        <span>ยอดสุทธิ</span>
        <span>
          ฿<span data-testid="cart-total">{baht(t.total)}</span>
        </span>
      </div>
      {t.vehicle === 'pickup' && t.weight > 0 && !freeShip && (
        <div className="muted" style={{ fontSize: 13 }}>
          ซื้อเพิ่มอีก {baht(20000 - t.afterDiscount)} บาท (ก่อน VAT) ส่งฟรีด้วยกระบะ
        </div>
      )}
    </div>
  );
}
