// components/ProductCart.ts (B1) — เรียก POST /api/cart ของ B2 แล้วแจ้ง Header ให้อัปเดต nav-cart-count

export async function addToCart(sku: string, qty: number): Promise<{ count?: number }> {
  const r = await fetch('/api/cart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sku, qty }),
  });
  let j: any = {};
  try {
    j = await r.json();
  } catch {
    /* ไม่มี body */
  }
  if (!r.ok) throw new Error(j?.error || `เพิ่มลงตะกร้าไม่สำเร็จ (${r.status})`);
  return { count: typeof j?.count === 'number' ? j.count : undefined };
}

/** แจ้ง Header (มี count → ใช้เลย · ไม่มี → header ดึง /api/cart/count ใหม่) */
export function notifyCart(count?: number) {
  window.dispatchEvent(new CustomEvent('bm:cart', typeof count === 'number' ? { detail: { count } } : undefined));
}
