// shared/pricing.js — กติกาคิดเงินของร้าน (BUILDMART ข้อ 1) · ESM ล้วน ไม่มี dependency
// ใช้ทั้ง web (import จาก '@/shared/pricing.js') และ workers (import จาก '../shared/pricing.js')

export const VAT_RATE = 0.07;

/** คูปองของร้าน (ต้องตรงกับตาราง coupons ใน db/init/02_seed.sql) */
export const COUPONS = {
  BUILD5: { code: 'BUILD5', percent: 5, min_subtotal: 5000 },
  CONTRACTOR10: { code: 'CONTRACTOR10', percent: 10, min_subtotal: 30000 },
};

export const VEHICLES = {
  pickup: { label: 'กระบะ', fee: 500, maxKg: 1000 },
  '6wheel': { label: 'รถ 6 ล้อ', fee: 1500, maxKg: 6000 },
  '10wheel': { label: 'รถ 10 ล้อ', fee: 3500, maxKg: Infinity },
};
export const FREE_PICKUP_MIN = 20000;

/** ปัดเศษ 2 ตำแหน่งแบบไม่เพี้ยนจาก floating point (1021.0375 → 1021.04) */
export function round2(n) {
  const x = Number(n) || 0;
  const sign = x < 0 ? -1 : 1;
  return sign * Number(Math.round(Number(Math.abs(x) + 'e2')) + 'e-2');
}

/** ระดับราคาส่ง: 1 = 1–49 · 2 = 50–199 · 3 = ≥200 */
export function tierOf(qty) {
  const q = Number(qty) || 0;
  return q >= 200 ? 3 : q >= 50 ? 2 : 1;
}

/** ราคาต่อหน่วยหลังราคาส่ง (คิดต่อรายการ) */
export function tierPrice(price, qty) {
  const t = tierOf(qty);
  const f = t === 3 ? 0.9 : t === 2 ? 0.95 : 1;
  return round2(Number(price) * f);
}

/** ตารางราคาส่ง 3 ขั้น สำหรับหน้าสินค้า */
export function tierTable(price) {
  return [
    { tier: 1, minQty: 1, maxQty: 49, price: tierPrice(price, 1) },
    { tier: 2, minQty: 50, maxQty: 199, price: tierPrice(price, 50) },
    { tier: 3, minQty: 200, maxQty: null, price: tierPrice(price, 200) },
  ];
}

/** เลือกรถตามน้ำหนักรวม (กก.) */
export function vehicleFor(weightKg) {
  const w = Number(weightKg) || 0;
  if (w <= 1000) return 'pickup';
  if (w <= 6000) return '6wheel';
  return '10wheel';
}

/** ค่าส่ง: กระบะฟรีถ้ายอดหลังส่วนลด ≥ 20,000 · ตะกร้าว่าง (น้ำหนัก 0) = 0 */
export function shippingFor(weightKg, afterDiscount = 0) {
  const vehicle = vehicleFor(weightKg);
  let fee = VEHICLES[vehicle].fee;
  if (vehicle === 'pickup' && Number(afterDiscount) >= FREE_PICKUP_MIN) fee = 0;
  if (!(Number(weightKg) > 0)) fee = 0;
  return { vehicle, vehicleLabel: VEHICLES[vehicle].label, shipping: fee };
}

function resolveCoupon(coupon) {
  if (!coupon) return null;
  if (typeof coupon === 'string') return COUPONS[coupon.trim().toUpperCase()] || { code: coupon.trim().toUpperCase(), invalid: true };
  return { code: String(coupon.code).toUpperCase(), percent: Number(coupon.percent), min_subtotal: Number(coupon.min_subtotal) };
}

/**
 * คิดยอดตะกร้าตามลำดับข้อ 1:
 * ยอดสินค้า (หลังราคาส่ง) → หักคูปอง → + ค่าส่ง → + VAT 7% ของ (ยอดหลังคูปอง + ค่าส่ง) → ปัด 2 ตำแหน่ง
 * @param {{items:{sku:string,qty:number,price:number,weight_kg:number}[], coupon?:string|{code,percent,min_subtotal}|null}} p
 */
export function computeTotals({ items = [], coupon = null } = {}) {
  const lines = items.map((it) => {
    const qty = Number(it.qty) || 0;
    const unitPrice = tierPrice(it.price, qty);
    return {
      sku: it.sku,
      qty,
      unitPrice,
      lineTotal: round2(unitPrice * qty),
      weight: round2(Number(it.weight_kg || 0) * qty),
    };
  });
  const subtotal = round2(lines.reduce((s, l) => s + l.lineTotal, 0));
  const weight = round2(lines.reduce((s, l) => s + Number(items.find((i) => i.sku === l.sku)?.weight_kg || 0) * l.qty, 0));

  let discount = 0;
  let couponError;
  let couponCode = null;
  const c = resolveCoupon(coupon);
  if (c) {
    if (c.invalid) couponError = `ไม่พบคูปอง ${c.code}`;
    else if (subtotal < c.min_subtotal) couponError = `คูปอง ${c.code} ใช้ได้เมื่อยอดก่อน VAT ≥ ${formatBaht(c.min_subtotal)} บาท`;
    else {
      discount = round2((subtotal * c.percent) / 100);
      couponCode = c.code;
    }
  }
  const afterDiscount = round2(subtotal - discount);
  const { vehicle, vehicleLabel, shipping } = shippingFor(weight, afterDiscount);
  const vat = round2((afterDiscount + shipping) * VAT_RATE);
  const total = round2(afterDiscount + shipping + vat);
  const out = { lines, subtotal, discount, coupon: couponCode, afterDiscount, weight, vehicle, vehicleLabel, shipping, vat, total };
  if (couponError) out.couponError = couponError;
  return out;
}

/** 15607.29 → "15,607.29" (ทศนิยม 2 ตำแหน่งเสมอ) */
export function formatBaht(n) {
  return round2(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
