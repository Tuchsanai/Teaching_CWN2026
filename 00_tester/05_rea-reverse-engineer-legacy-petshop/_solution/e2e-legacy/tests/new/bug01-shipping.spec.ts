import type { Page } from '@playwright/test';
import { test, expect, open, registerByApi, baht } from '../fixtures';

/*
 * BUG-01 · "โดนเก็บเงินเกินจากที่หน้าเว็บบอก" (คุณนุ่น · ไม้ตกแมว 1 + ชามกินช้า 3 · ปุ่ม ฿999 แต่คำสั่งซื้อ ฿1,049)
 * Expected values come ONLY from TEST-DATA.md [D]: "ค่าส่ง ปกติ ฿50 (ฟรีเมื่อซื้อครบ ฿999) · ด่วน ฿120" · "FREESHIP ส่งฟรี".
 *   ฿999 ≥ ฿999 → ส่งฟรี → ยอด ฿999 · ฿998 → +฿50 = ฿1,048 · ฿1,000 → ส่งฟรี · ด่วน ฿999 + ฿120 = ฿1,119
 * Never copied from the web. Fresh random buyer per test · no /api/test/reset here · never lock order id or stock.
 * Related (LAB 4): char-money.spec.ts TC-CHAR-SHIP-02 (legacy-quirk, locks ฿1,049) · TC-CHAR-SHIP-03 (KNOWN-ISSUE test.fail()).
 */

type Line = { slug: string; size?: string; qty: number };
// ฿129 + ฿290×3 = ฿999 — the customer's own cart
const CUSTOMER_999: Line[] = [{ slug: 'cat-feather-wand', qty: 1 }, { slug: 'dog-slow-bowl', qty: 3 }];
// ฿129 + ฿390×2 + ฿45×2 = ฿999 — same total, other goods (keeps dog-slow-bowl stock for the customer test)
const MIXED_999: Line[] = [{ slug: 'cat-feather-wand', qty: 1 }, { slug: 'tuna-pouch', size: 'แพ็ค 12 ซอง', qty: 2 }, { slug: 'puppy-lamb-wet', qty: 2 }];
// ฿590 + ฿149 + ฿259 = ฿998 — ฿1 under the line
const MIXED_998: Line[] = [{ slug: 'kitten-salmon-dry', size: '1.5 kg', qty: 1 }, { slug: 'dental-chew-treat', qty: 1 }, { slug: 'cat-scratcher', qty: 1 }];
// ฿45 + ฿79×2 + ฿149 + ฿129×2 + ฿390 = ฿1,000 — ฿1 over the line
const MIXED_1000: Line[] = [
  { slug: 'puppy-lamb-wet', qty: 1 }, { slug: 'beef-stew-can', size: '400 g', qty: 2 }, { slug: 'dog-rope-toy', qty: 1 },
  { slug: 'salmon-skin-treat', qty: 2 }, { slug: 'tuna-pouch', size: 'แพ็ค 12 ซอง', qty: 1 },
];

type Money = { subtotal: number; discount: number; shipping: string; total: number };

/** Buy through the UI and read the money at: cart · place-order button · POST /api/orders · order page · /account row. */
async function buy(page: Page, lines: Line[], opts: { express?: boolean; coupon?: string } = {}) {
  await registerByApi(page.request);
  for (const l of lines) {
    await open(page, `/products/${l.slug}`);
    if (l.size) await page.locator(`[data-testid="size-option"][data-size="${l.size}"]`).click();
    for (let i = 1; i < l.qty; i++) await page.getByTestId('qty-plus').click();
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('toast')).toBeVisible();
  }
  const summary = async (): Promise<Money> => ({
    subtotal: baht(await page.getByTestId('summary-subtotal').textContent()),
    discount: baht(await page.getByTestId('summary-discount').textContent()),
    shipping: ((await page.getByTestId('summary-shipping').textContent()) ?? '').trim(),
    total: baht(await page.getByTestId('summary-total').textContent()),
  });

  await open(page, '/cart');
  if (opts.coupon) {
    await page.getByTestId('coupon-input').fill(opts.coupon);
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('coupon-message')).toHaveText(`ใช้คูปอง ${opts.coupon} แล้ว`);
  }
  const cart = await summary();

  await open(page, '/checkout');
  await page.getByTestId('ship-phone').fill('0812345678');
  await page.getByTestId('ship-address').fill('99/9 ถนนสุขุมวิท แขวงคลองเตย');
  await page.getByTestId('ship-province').selectOption('กรุงเทพมหานคร');
  await page.getByTestId('ship-postcode').fill('10110');
  if (opts.express) await page.getByTestId('shipping-express').check();
  const button = baht(await page.getByTestId('place-order').textContent());

  const respP = page.waitForResponse((r) => r.url().endsWith('/api/orders') && r.request().method() === 'POST');
  await page.getByTestId('place-order').click();
  const resp = await respP;
  expect(resp.status()).toBe(201);
  const o = (await resp.json()).order;
  const server = { shipping: o.shipping as number, total: o.total as number };

  await expect(page.getByTestId('order-success')).toBeVisible();
  const orderId = ((await page.getByTestId('order-id').textContent()) ?? '').trim();
  const order = await summary();

  await open(page, '/account');
  const row = page.getByTestId('order-row').filter({ hasText: orderId });
  await expect(row).toHaveCount(1);
  const account = baht(((await row.textContent()) ?? '').split('฿').pop() ?? '');
  return { cart, button, server, order, account };
}

const D = (d: string) => ({ type: '[D] TEST-DATA.md', description: d });

test.describe('BUG-01 · ค่าส่งที่ยอด ฿999 (ปุ่มยืนยันกับคำสั่งซื้อต้องเท่ากัน)', () => {
  test('BUG-01 ลูกค้าคุณนุ่น: ไม้ตกแมว 1 + ชามกินช้า 3 = ฿999 ส่งปกติ → ส่งฟรี ยอด ฿999 ทุกจุด (ตะกร้า·ปุ่ม·server·หน้าคำสั่งซื้อ·บัญชี)', {
    tag: '@bug01',
    annotation: [D('ค่าส่งปกติ ฿50 (ฟรีเมื่อซื้อครบ ฿999) → ฿999 ครบพอดี → ค่าส่ง 0 · ยอด ฿999'), { type: 'issue', description: 'BUG-01.md' }],
  }, async ({ page }) => {
    const m = await buy(page, CUSTOMER_999);
    expect.soft(m.cart, 'ตะกร้า').toEqual({ subtotal: 999, discount: 0, shipping: 'ฟรี', total: 999 });
    expect.soft(m.button, 'ปุ่มยืนยันสั่งซื้อ').toBe(999);
    expect.soft(m.server, 'response ของ POST /api/orders').toEqual({ shipping: 0, total: 999 });
    expect.soft(m.order, 'หน้าคำสั่งซื้อ').toEqual({ subtotal: 999, discount: 0, shipping: 'ฟรี', total: 999 });
    expect.soft(m.account, 'ยอดใน /account').toBe(999);
  });

  for (const c of [
    { name: '฿999 ส่งปกติ', lines: MIXED_999, opts: {} },
    { name: '฿999 + PAW10', lines: MIXED_999, opts: { coupon: 'PAW10' } },
    { name: '฿999 ส่งด่วน', lines: MIXED_999, opts: { express: true } },
    { name: '฿998 ส่งปกติ', lines: MIXED_998, opts: {} },
  ]) {
    test(`BUG-01 เงินบนปุ่มยืนยัน = เงินในคำสั่งซื้อ · ${c.name}`, {
      tag: '@bug01',
      annotation: { type: 'rule', description: 'ลูกค้าต้องจ่ายเท่าที่ปุ่มยืนยันบอก (ไม่ขึ้นกับว่ากฎค่าส่งคิดแบบไหน)' },
    }, async ({ page }) => {
      const m = await buy(page, c.lines, c.opts);
      expect.soft(m.server.total, 'response ของ POST /api/orders').toBe(m.button);
      expect.soft(m.order.total, 'หน้าคำสั่งซื้อ').toBe(m.button);
      expect.soft(m.account, 'ยอดใน /account').toBe(m.button);
    });
  }

  test('BUG-01 ข้างเคียง ฿998 ส่งปกติ → ค่าส่ง ฿50 ยอด ฿1,048 ทุกจุด', {
    tag: '@bug01', annotation: D('ยังไม่ครบ ฿999 → ค่าส่งปกติ ฿50 → ฿998 + ฿50 = ฿1,048'),
  }, async ({ page }) => {
    const m = await buy(page, MIXED_998);
    expect.soft(m.cart).toEqual({ subtotal: 998, discount: 0, shipping: '฿50', total: 1048 });
    expect.soft(m.button).toBe(1048);
    expect.soft(m.server).toEqual({ shipping: 50, total: 1048 });
    expect.soft(m.order).toEqual({ subtotal: 998, discount: 0, shipping: '฿50', total: 1048 });
  });

  test('BUG-01 ข้างเคียง ฿1,000 ส่งปกติ → ส่งฟรี ยอด ฿1,000 ทุกจุด', {
    tag: '@bug01', annotation: D('เกิน ฿999 → ส่งฟรี → ยอด ฿1,000'),
  }, async ({ page }) => {
    const m = await buy(page, MIXED_1000);
    expect.soft(m.cart).toEqual({ subtotal: 1000, discount: 0, shipping: 'ฟรี', total: 1000 });
    expect.soft(m.button).toBe(1000);
    expect.soft(m.server).toEqual({ shipping: 0, total: 1000 });
    expect.soft(m.order).toEqual({ subtotal: 1000, discount: 0, shipping: 'ฟรี', total: 1000 });
  });

  test('BUG-01 ข้างเคียง ฿999 + FREESHIP → ส่งฟรี ยอด ฿999 ทุกจุด', {
    tag: '@bug01', annotation: D('FREESHIP ส่งฟรี → ยอด ฿999'),
  }, async ({ page }) => {
    const m = await buy(page, MIXED_999, { coupon: 'FREESHIP' });
    expect.soft(m.button).toBe(999);
    expect.soft(m.server).toEqual({ shipping: 0, total: 999 });
    expect.soft(m.order.total).toBe(999);
  });

  test('BUG-01 ข้างเคียง ฿999 ส่งด่วน → ค่าส่ง ฿120 ยอด ฿1,119', {
    tag: '@bug01', annotation: D('ด่วน ฿120 (ส่งฟรีเขียนไว้เฉพาะส่งปกติ) → ฿999 + ฿120 = ฿1,119'),
  }, async ({ page }) => {
    const m = await buy(page, MIXED_999, { express: true });
    expect.soft(m.button).toBe(1119);
    expect.soft(m.server).toEqual({ shipping: 120, total: 1119 });
    expect.soft(m.order).toEqual({ subtotal: 999, discount: 0, shipping: '฿120', total: 1119 });
  });
});
