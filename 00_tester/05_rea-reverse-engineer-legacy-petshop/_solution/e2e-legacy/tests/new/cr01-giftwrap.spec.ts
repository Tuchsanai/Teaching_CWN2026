import type { APIRequestContext, Page } from '@playwright/test';
import { test, expect, open, registerByApi, baht } from '../fixtures';

/*
 * CR-01 · บริการห่อของขวัญ (ใบ CR + คำตอบร้าน ดู CR-01.md)
 * กฎที่ใช้คิดผลที่คาดหวัง (ทุกข้อมีที่มา):
 *   [CR]  ค่าห่อ ฿30 · ซื้อครบ ฿1,500 ห่อฟรี · ยอดชำระ = ยอดสินค้า − ส่วนลด + ค่าส่ง + ค่าห่อ (AC3)
 *   [ร้าน] ฿1,500 ดูยอดก่อนหักส่วนลด · ค่าห่อไม่นับเข้ายอดส่งฟรี ฿999 / ขั้นต่ำ NEWCAT50 · PAW10 ไม่ลดค่าห่อ · FREESHIP ไม่ยกเว้นค่าห่อ · ต่อคำสั่งซื้อ
 *   [D]   TEST-DATA.md: ส่งปกติ ฿50 (ฟรีเมื่อครบ ฿999) · ด่วน ฿120 · PAW10 10% · FREESHIP ส่งฟรี · NEWCAT50 ลด ฿50 (อาหารแมว ≥ ฿500)
 *   [⚠️]  สมมติฐาน: "ครบ ฿1,500" = ≥ 1,500 (แบบเดียวกับ ≥ ฿999) · ห่อของขวัญเลือกได้เฉพาะ /checkout (หน้า /cart ไม่มีแถวนี้)
 * ราคาสินค้า: GET /api/products (2026-10-12) ทุกตะกร้าซื้อได้จริงในร้าน
 * ผู้ซื้อสุ่มใหม่ทุก test · ไม่เรียก /api/test/reset เอง · ไม่ล็อกเลขออเดอร์/สต็อก
 */

// ตั้ง timeout สั้น: ตอนนี้ยังไม่มีฟีเจอร์ ข้อ UI จะแดงที่การหา gift-wrap ไม่ต้องรอ 45 วิ
test.use({ actionTimeout: 5_000 });
test.describe.configure({ timeout: 30_000 });

type Line = { slug: string; size: string; qty: number };
const L = (slug: string, size: string, qty = 1): Line => ({ slug, size, qty });

// ฿189 + ฿890 + ฿420 = ฿1,499 (฿1 ต่ำกว่าเส้นห่อฟรี)
const B1499 = [L('kitten-salmon-dry', '400 g'), L('cat-fountain', '2 ลิตร'), L('small-breed-chicken-dry', '1.5 kg')];
// ฿290 + ฿790 + ฿420 = ฿1,500 (ถึงเส้นห่อฟรีพอดี)
const B1500 = [L('dog-slow-bowl', '1 ใบ'), L('adult-lamb-dry', '3 kg'), L('small-breed-chicken-dry', '1.5 kg')];
// ฿189 ตะกร้าเล็ก
const B189 = [L('kitten-salmon-dry', '400 g')];
// ฿189 × 2 = ฿378 (หลายชิ้น)
const B378 = [L('kitten-salmon-dry', '400 g', 2)];
// ฿420 + ฿390 + ฿189 = ฿999 (ครบส่งฟรีพอดี)
const B999 = [L('small-breed-chicken-dry', '1.5 kg'), L('cat-tunnel', '1 ชิ้น'), L('kitten-salmon-dry', '400 g')];
// ฿799 + ฿199 = ฿998 (ขาดส่งฟรี ฿1 · ถ้าเอาค่าห่อไปนับจะกลายเป็นส่งฟรี)
const B998 = [L('adult-chicken-dry', '3 kg'), L('dog-squeaky-ball', 'แพ็ค 3 ลูก')];
// ฿590 ลูกแมว 1.5 kg
const B590 = [L('kitten-salmon-dry', '1.5 kg')];
// ฿420 + ฿69 = ฿489 อาหารแมวล้วน (ขาดขั้นต่ำ NEWCAT50 ฿11 · ถ้านับค่าห่อ ฿30 จะผ่าน)
const B489 = [L('kitten-chicken-mousse', 'แพ็ค 12 ซอง'), L('lickable-salmon-treat', '4 ซอง')];

const ADDRESS = { name: 'นักทดสอบ ห่อของขวัญ', phone: '0812345678', address: '99/9 ถนนสุขุมวิท แขวงคลองเตย', province: 'กรุงเทพมหานคร', postcode: '10110' };

type Summary = { subtotal: number; discount: number; shipping: string; giftwrap: string | null; total: number };

async function readSummary(page: Page): Promise<Summary> {
  const gw = page.getByTestId('summary-giftwrap');
  return {
    subtotal: baht(await page.getByTestId('summary-subtotal').textContent()),
    discount: baht(await page.getByTestId('summary-discount').textContent()),
    shipping: ((await page.getByTestId('summary-shipping').textContent()) ?? '').trim(),
    giftwrap: (await gw.count()) ? ((await gw.textContent()) ?? '').trim() : null,
    total: baht(await page.getByTestId('summary-total').textContent()),
  };
}

async function fillCart(page: Page, lines: Line[], coupon?: string) {
  await registerByApi(page.request);
  for (const l of lines) {
    await open(page, `/products/${l.slug}`);
    const opt = page.locator(`[data-testid="size-option"][data-size="${l.size}"]`);
    if (await opt.count()) await opt.click();
    for (let i = 1; i < l.qty; i++) await page.getByTestId('qty-plus').click();
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('toast')).toBeVisible();
  }
  if (coupon) {
    await open(page, '/cart');
    await page.getByTestId('coupon-input').fill(coupon);
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('coupon-message')).toHaveText(`ใช้คูปอง ${coupon} แล้ว`);
  }
}

async function openCheckout(page: Page, opts: { express?: boolean } = {}) {
  await open(page, '/checkout');
  await page.getByTestId('ship-phone').fill(ADDRESS.phone);
  await page.getByTestId('ship-address').fill(ADDRESS.address);
  await page.getByTestId('ship-province').selectOption(ADDRESS.province);
  await page.getByTestId('ship-postcode').fill(ADDRESS.postcode);
  if (opts.express) await page.getByTestId('shipping-express').check();
}

/** ซื้อผ่าน UI แบบติ๊กห่อของขวัญ แล้วอ่านเงิน 4 จุด: checkout · ปุ่ม · response · หน้าคำสั่งซื้อ + /account */
async function buyWrapped(page: Page, lines: Line[], opts: { express?: boolean; coupon?: string } = {}) {
  await fillCart(page, lines, opts.coupon);
  await openCheckout(page, opts);
  const box = page.getByTestId('gift-wrap');
  await expect(box, 'AC1 ค่าเริ่มต้นไม่ติ๊ก').not.toBeChecked();
  await box.check();
  const checkout = await readSummary(page);
  const button = baht(await page.getByTestId('place-order').textContent());

  const respP = page.waitForResponse((r) => r.url().endsWith('/api/orders') && r.request().method() === 'POST');
  await page.getByTestId('place-order').click();
  const resp = await respP;
  expect(resp.status()).toBe(201);
  const o = (await resp.json()).order;
  const server = { giftWrap: o.giftWrap, giftWrapFee: o.giftWrapFee, shipping: o.shipping, discount: o.discount, total: o.total };

  await expect(page.getByTestId('order-success')).toBeVisible();
  const orderId = ((await page.getByTestId('order-id').textContent()) ?? '').trim();
  const order = await readSummary(page);

  await open(page, '/account');
  const row = page.getByTestId('order-row').filter({ hasText: orderId });
  await expect(row).toHaveCount(1);
  const account = baht(((await row.textContent()) ?? '').split('฿').pop() ?? '');
  return { checkout, button, server, order, account };
}

/** สั่งผ่าน API (ผู้ซื้อใหม่ · cookie อยู่ใน request context) */
async function apiOrder(request: APIRequestContext, lines: Line[], extra: Record<string, unknown> = {}) {
  await registerByApi(request);
  const res = await request.post('/api/orders', { data: { items: lines, shipping: 'standard', payment: 'cod', address: ADDRESS, ...extra } });
  expect(res.status(), await res.text()).toBe(201);
  return (await res.json()).order;
}

const why = (d: string) => ({ type: 'expected', description: d });

test.describe('CR-01 · ห่อของขวัญ (UI /checkout → /orders/[id] → /account)', () => {
  test('TC-GIFT-01 AC1 · /checkout มี checkbox gift-wrap ไม่ติ๊ก และยังไม่มีแถว summary-giftwrap', {
    tag: '@cr01', annotation: why('[CR] AC1 ค่าเริ่มต้นไม่ติ๊ก · AC2 ไม่ติ๊ก = ไม่มีแถว · ฿189 + ส่ง ฿50 = ฿239'),
  }, async ({ page }) => {
    await fillCart(page, B189);
    await openCheckout(page);
    await expect(page.getByTestId('gift-wrap')).toBeVisible();
    await expect(page.getByTestId('gift-wrap')).not.toBeChecked();
    await expect(page.getByTestId('summary-giftwrap')).toHaveCount(0);
    expect(baht(await page.getByTestId('summary-total').textContent())).toBe(239);
  });

  test('TC-GIFT-02 AC2 · ติ๊กแล้วเอาออก: ฿239 → ฿269 (แถว ฿30) → ฿239 (แถวหาย) ทั้งสรุปยอดและปุ่ม', {
    tag: '@cr01', annotation: why('[CR] ฿189 < ฿1,500 → ค่าห่อ ฿30 · ฿189 + ฿50 + ฿30 = ฿269 · เอาออก → ฿189 + ฿50 = ฿239'),
  }, async ({ page }) => {
    await fillCart(page, B189);
    await openCheckout(page);
    const box = page.getByTestId('gift-wrap');
    await box.check();
    await expect(page.getByTestId('summary-giftwrap')).toHaveText('฿30');
    await expect(page.getByTestId('summary-total')).toHaveText('฿269');
    await expect(page.getByTestId('place-order')).toContainText('฿269');
    await box.uncheck();
    await expect(page.getByTestId('summary-giftwrap')).toHaveCount(0);
    await expect(page.getByTestId('summary-total')).toHaveText('฿239');
    await expect(page.getByTestId('place-order')).toContainText('฿239');
  });

  test('TC-GIFT-03 ค่าขอบ ฿1,499 ห่อ → ค่าห่อ ฿30 ยอด ฿1,529 ตรงกัน 4 จุด', {
    tag: '@cr01', annotation: why('[CR] ฿1,499 < ฿1,500 → ฿30 · [D] ฿1,499 ≥ ฿999 ส่งฟรี · ฿1,499 − 0 + 0 + ฿30 = ฿1,529'),
  }, async ({ page }) => {
    const m = await buyWrapped(page, B1499);
    expect.soft(m.checkout, 'checkout').toEqual({ subtotal: 1499, discount: 0, shipping: 'ฟรี', giftwrap: '฿30', total: 1529 });
    expect.soft(m.button, 'ปุ่ม place-order').toBe(1529);
    expect.soft(m.server, 'response POST /api/orders').toEqual({ giftWrap: true, giftWrapFee: 30, shipping: 0, discount: 0, total: 1529 });
    expect.soft(m.order, 'หน้า /orders/[id]').toEqual({ subtotal: 1499, discount: 0, shipping: 'ฟรี', giftwrap: '฿30', total: 1529 });
    expect.soft(m.account, '/account').toBe(1529);
  });

  test('TC-GIFT-04 ค่าขอบ ฿1,500 ห่อ → ห่อฟรี ยอด ฿1,500 ตรงกัน 4 จุด', {
    tag: '@cr01', annotation: why('[CR] ครบ ฿1,500 ห่อฟรี [⚠️ ≥] · [D] ส่งฟรี · ฿1,500 + 0 + 0 = ฿1,500'),
  }, async ({ page }) => {
    const m = await buyWrapped(page, B1500);
    expect.soft(m.checkout, 'checkout').toEqual({ subtotal: 1500, discount: 0, shipping: 'ฟรี', giftwrap: 'ฟรี', total: 1500 });
    expect.soft(m.button, 'ปุ่ม place-order').toBe(1500);
    expect.soft(m.server, 'response POST /api/orders').toEqual({ giftWrap: true, giftWrapFee: 0, shipping: 0, discount: 0, total: 1500 });
    expect.soft(m.order, 'หน้า /orders/[id]').toEqual({ subtotal: 1500, discount: 0, shipping: 'ฟรี', giftwrap: 'ฟรี', total: 1500 });
    expect.soft(m.account, '/account').toBe(1500);
  });

  test('TC-GIFT-05 ฿1,500 + PAW10 ห่อ → ห่อยังฟรี (ดูยอดก่อนหักส่วนลด) ยอด ฿1,350', {
    tag: '@cr01', annotation: why('[ร้าน] ฿1,500 ดูก่อนหักส่วนลด → ห่อฟรี · [D] PAW10 = floor(1500×10%) = ฿150 · ส่งฟรี · 1,500 − 150 + 0 + 0 = ฿1,350'),
  }, async ({ page }) => {
    const m = await buyWrapped(page, B1500, { coupon: 'PAW10' });
    expect.soft(m.checkout, 'checkout').toEqual({ subtotal: 1500, discount: 150, shipping: 'ฟรี', giftwrap: 'ฟรี', total: 1350 });
    expect.soft(m.button, 'ปุ่ม place-order').toBe(1350);
    expect.soft(m.server, 'response POST /api/orders').toEqual({ giftWrap: true, giftWrapFee: 0, shipping: 0, discount: 150, total: 1350 });
    expect.soft(m.order.total, 'หน้า /orders/[id]').toBe(1350);
    expect.soft(m.account, '/account').toBe(1350);
  });

  test('TC-GIFT-06 ฿189 + FREESHIP ห่อ → ส่งฟรีแต่ค่าห่อยัง ฿30 ยอด ฿219', {
    tag: '@cr01', annotation: why('[ร้าน] FREESHIP ไม่ยกเว้นค่าห่อ · [D] FREESHIP ค่าส่ง 0 · 189 − 0 + 0 + 30 = ฿219'),
  }, async ({ page }) => {
    const m = await buyWrapped(page, B189, { coupon: 'FREESHIP' });
    expect.soft(m.checkout, 'checkout').toEqual({ subtotal: 189, discount: 0, shipping: 'ฟรี', giftwrap: '฿30', total: 219 });
    expect.soft(m.button, 'ปุ่ม place-order').toBe(219);
    expect.soft(m.server, 'response POST /api/orders').toEqual({ giftWrap: true, giftWrapFee: 30, shipping: 0, discount: 0, total: 219 });
    expect.soft(m.order.total, 'หน้า /orders/[id]').toBe(219);
    expect.soft(m.account, '/account').toBe(219);
  });

  test('TC-GIFT-07 ลูกแมว 1.5 kg ส่งด่วน ห่อ → ฿590 + ฿120 + ฿30 = ฿740', {
    tag: '@cr01', annotation: why('[D] ด่วน ฿120 · [CR] ฿590 < ฿1,500 → ฿30 · 590 + 120 + 30 = ฿740'),
  }, async ({ page }) => {
    const m = await buyWrapped(page, B590, { express: true });
    expect.soft(m.checkout, 'checkout').toEqual({ subtotal: 590, discount: 0, shipping: '฿120', giftwrap: '฿30', total: 740 });
    expect.soft(m.button, 'ปุ่ม place-order').toBe(740);
    expect.soft(m.server, 'response POST /api/orders').toEqual({ giftWrap: true, giftWrapFee: 30, shipping: 120, discount: 0, total: 740 });
    expect.soft(m.order.total, 'หน้า /orders/[id]').toBe(740);
    expect.soft(m.account, '/account').toBe(740);
  });

  test('TC-GIFT-08 ฿998 ห่อ → ค่าห่อไม่ช่วยให้ส่งฟรี ยอด ฿1,078', {
    tag: '@cr01', annotation: why('[ร้าน] ค่าห่อไม่นับเข้ายอดส่งฟรี · [D] ฿998 < ฿999 → ค่าส่ง ฿50 · 998 + 50 + 30 = ฿1,078 (ถ้านับผิดจะได้ ฿1,028)'),
  }, async ({ page }) => {
    const m = await buyWrapped(page, B998);
    expect.soft(m.checkout, 'checkout').toEqual({ subtotal: 998, discount: 0, shipping: '฿50', giftwrap: '฿30', total: 1078 });
    expect.soft(m.button, 'ปุ่ม place-order').toBe(1078);
    expect.soft(m.server, 'response POST /api/orders').toEqual({ giftWrap: true, giftWrapFee: 30, shipping: 50, discount: 0, total: 1078 });
    expect.soft(m.order.total, 'หน้า /orders/[id]').toBe(1078);
    expect.soft(m.account, '/account').toBe(1078);
  });

  test('TC-GIFT-09 ฿999 ห่อ → ส่งฟรี + ค่าห่อ ฿30 ยอด ฿1,029', {
    tag: '@cr01', annotation: why('[D] ฿999 ≥ ฿999 ส่งฟรี · [CR] ฿999 < ฿1,500 → ฿30 · 999 + 0 + 30 = ฿1,029'),
  }, async ({ page }) => {
    const m = await buyWrapped(page, B999);
    expect.soft(m.checkout, 'checkout').toEqual({ subtotal: 999, discount: 0, shipping: 'ฟรี', giftwrap: '฿30', total: 1029 });
    expect.soft(m.button, 'ปุ่ม place-order').toBe(1029);
    expect.soft(m.server, 'response POST /api/orders').toEqual({ giftWrap: true, giftWrapFee: 30, shipping: 0, discount: 0, total: 1029 });
    expect.soft(m.order.total, 'หน้า /orders/[id]').toBe(1029);
    expect.soft(m.account, '/account').toBe(1029);
  });

  test('TC-GIFT-17 guard · หน้า /cart ไม่มีแถวห่อของขวัญ (เลือกได้ที่ /checkout เท่านั้น)', {
    tag: '@cr01', annotation: why('[⚠️ สมมติฐาน] AC1 พูดถึง /checkout เท่านั้น → /cart ไม่เปลี่ยน · ฿189 + ฿50 = ฿239'),
  }, async ({ page }) => {
    await fillCart(page, B189);
    await open(page, '/cart');
    await expect(page.getByTestId('summary-giftwrap')).toHaveCount(0);
    await expect(page.getByTestId('summary-total')).toHaveText('฿239');
  });
});

test.describe('CR-01 · ห่อของขวัญ (API POST /api/orders · GET /api/orders/[id])', () => {
  test('TC-GIFT-10 API giftWrap: true ฿189 → giftWrap true · giftWrapFee 30 · total 269 (response = GET /api/orders/[id])', {
    tag: '@cr01', annotation: why('[CR] AC3 AC4 · 189 + 50 + 30 = ฿269'),
  }, async ({ request }) => {
    const o = await apiOrder(request, B189, { giftWrap: true });
    expect.soft({ giftWrap: o.giftWrap, giftWrapFee: o.giftWrapFee, total: o.total }).toEqual({ giftWrap: true, giftWrapFee: 30, total: 269 });
    const g = (await (await request.get(`/api/orders/${o.id}`)).json()).order;
    expect.soft({ giftWrap: g.giftWrap, giftWrapFee: g.giftWrapFee, total: g.total }).toEqual({ giftWrap: true, giftWrapFee: 30, total: 269 });
  });

  test('TC-GIFT-11 API giftWrap: false ฿189 → giftWrap false · giftWrapFee 0 · total 239', {
    tag: '@cr01', annotation: why('[CR] AC4 response มี giftWrap/giftWrapFee เสมอ · 189 + 50 = ฿239'),
  }, async ({ request }) => {
    const o = await apiOrder(request, B189, { giftWrap: false });
    expect.soft({ giftWrap: o.giftWrap, giftWrapFee: o.giftWrapFee, total: o.total }).toEqual({ giftWrap: false, giftWrapFee: 0, total: 239 });
  });

  for (const bad of ['true', 1, 'yes', null] as const) {
    test(`TC-GIFT-12 API giftWrap ผิดชนิด (${JSON.stringify(bad)}) → ถือว่าไม่ห่อ giftWrap false · fee 0 · total 239`, {
      tag: '@cr01', annotation: why('[CR] AC4 boolean เท่านั้น ค่าอื่นถือว่าไม่ห่อ · 189 + 50 = ฿239'),
    }, async ({ request }) => {
      const o = await apiOrder(request, B189, { giftWrap: bad });
      expect.soft(o.total, 'ยอดไม่รวมค่าห่อ').toBe(239);
      expect.soft({ giftWrap: o.giftWrap, giftWrapFee: o.giftWrapFee }).toEqual({ giftWrap: false, giftWrapFee: 0 });
    });
  }

  test('TC-GIFT-13 guard · API ส่ง giftWrap ผิดชนิด → ยอดไม่รวมค่าห่อ (฿239) [เขียวตั้งแต่ก่อนมีฟีเจอร์ = guard ห้ามแดงหลังทำ]', {
    tag: '@cr01', annotation: why('[CR] AC4 ค่าอื่นถือว่าไม่ห่อ · 189 + 50 = ฿239 · ตรวจเฉพาะยอด'),
  }, async ({ request }) => {
    for (const bad of ['true', 1]) {
      const o = await apiOrder(request, B189, { giftWrap: bad });
      expect.soft(o.total, `giftWrap=${JSON.stringify(bad)}`).toBe(239);
    }
  });

  test('TC-GIFT-14 API ค่าห่อต่อคำสั่งซื้อ: ลูกแมว 400 g × 2 ห่อ → fee 30 ไม่ใช่ 60 · total 458', {
    tag: '@cr01', annotation: why('[ร้าน] ต่อคำสั่งซื้อ · 189×2 = 378 + 50 + 30 = ฿458 (ต่อชิ้นจะได้ ฿488)'),
  }, async ({ request }) => {
    const o = await apiOrder(request, B378, { giftWrap: true });
    expect.soft({ subtotal: o.subtotal, giftWrapFee: o.giftWrapFee, total: o.total }).toEqual({ subtotal: 378, giftWrapFee: 30, total: 458 });
  });

  test('TC-GIFT-15 API PAW10 ไม่ลดค่าห่อ: ฿189 + PAW10 ห่อ → ส่วนลด 18 · total 251', {
    tag: '@cr01', annotation: why('[ร้าน] PAW10 ไม่ลดค่าห่อ · [D] floor(189×10%) = 18 · 189 − 18 + 50 + 30 = ฿251 (ถ้าลดค่าห่อด้วย = ฿248)'),
  }, async ({ request }) => {
    const o = await apiOrder(request, B189, { giftWrap: true, coupon: 'PAW10' });
    expect.soft({ discount: o.discount, giftWrapFee: o.giftWrapFee, total: o.total }).toEqual({ discount: 18, giftWrapFee: 30, total: 251 });
  });

  test('TC-GIFT-16 API ค่าห่อไม่นับขั้นต่ำ NEWCAT50: อาหารแมว ฿489 + ห่อ → คูปองไม่ผ่าน · total 569', {
    tag: '@cr01', annotation: why('[ร้าน] ไม่นับเข้าขั้นต่ำ NEWCAT50 · [D] อาหารแมว 489 < 500 → ไม่ลด · 489 + 50 + 30 = ฿569 (ถ้านับผิด 519)'),
  }, async ({ request }) => {
    const o = await apiOrder(request, B489, { giftWrap: true, coupon: 'NEWCAT50' });
    expect.soft({ discount: o.discount, coupon: o.coupon, giftWrapFee: o.giftWrapFee, total: o.total }).toEqual({ discount: 0, coupon: null, giftWrapFee: 30, total: 569 });
  });

  test('TC-GIFT-18 guard · API ไม่ส่ง giftWrap เลย (client เดิม) → ยอดเดิม ฿239', {
    tag: '@cr01', annotation: why('[CR] AC6 ของเดิมต้องไม่เปลี่ยน · 189 + 50 = ฿239'),
  }, async ({ request }) => {
    const o = await apiOrder(request, B189);
    expect(o.total).toBe(239);
  });
});
