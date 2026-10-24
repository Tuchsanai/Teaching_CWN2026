import { readFileSync } from 'node:fs';
import type { Page } from '@playwright/test';
import { test, expect, open, registerByApi, baht } from '../fixtures';

/*
 * Characterization (golden master) of the money rules — LAB 4.
 * Locks what the running web does TODAY so later changes can be compared.
 *   [E] = value seen by running the web (source file/run named in the annotation)
 *   [D] = value stated by TEST-DATA.md (the old team's test data)
 * When [E] ≠ [D]: one test locks today's value (legacy-quirk) and one test.fail() expects [D] (KNOWN-ISSUE).
 * Rules: no /api/test/reset here (legacy suite runs in parallel) · fresh random user per test · never lock order id or stock.
 */

type Line = { slug: string; size?: string; qty: number };
const CART = {
  // ฿590 + ฿149 + ฿259 = ฿998 (฿1 under the free-shipping line)
  mixed998: [{ slug: 'kitten-salmon-dry', size: '1.5 kg', qty: 1 }, { slug: 'dental-chew-treat', qty: 1 }, { slug: 'cat-scratcher', qty: 1 }],
  // ฿129 + ฿390×2 + ฿45×2 = ฿999 (exactly on the line)
  mixed999: [{ slug: 'cat-feather-wand', qty: 1 }, { slug: 'tuna-pouch', size: 'แพ็ค 12 ซอง', qty: 2 }, { slug: 'puppy-lamb-wet', qty: 2 }],
  // ฿129 + ฿290×3 = ฿999 (exactly on the line · used for express)
  bowl999: [{ slug: 'cat-feather-wand', qty: 1 }, { slug: 'dog-slow-bowl', qty: 3 }],
} satisfies Record<string, Line[]>;

type Money = { subtotal: number; discount: number; shipping: string; total: number };

/** Buy one cart through the UI and read the money at 4 points: cart page · place-order button · POST /api/orders response · order page. */
async function buyAndRead(page: Page, lines: Line[], opts: { express?: boolean; coupon?: string } = {}) {
  await registerByApi(page.request); // logs this browser context in
  for (const l of lines) {
    await open(page, `/products/${l.slug}`);
    if (l.size) await page.locator(`[data-testid="size-option"][data-size="${l.size}"]`).click();
    for (let i = 1; i < l.qty; i++) await page.getByTestId('qty-plus').click();
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('toast')).toBeVisible();
  }

  const readSummary = async (): Promise<Money> => ({
    subtotal: baht(await page.getByTestId('summary-subtotal').textContent()),
    discount: baht(await page.getByTestId('summary-discount').textContent()),
    shipping: ((await page.getByTestId('summary-shipping').textContent()) ?? '').trim(),
    total: baht(await page.getByTestId('summary-total').textContent()),
  });

  // 1) cart page
  await open(page, '/cart');
  if (opts.coupon) {
    await page.getByTestId('coupon-input').fill(opts.coupon);
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('coupon-message')).toHaveText(`ใช้คูปอง ${opts.coupon} แล้ว`);
  }
  const cart = await readSummary();

  // 2) checkout: place-order button
  await open(page, '/checkout');
  await page.getByTestId('ship-phone').fill('0812345678');
  await page.getByTestId('ship-address').fill('99/9 ถนนสุขุมวิท แขวงคลองเตย');
  await page.getByTestId('ship-province').selectOption('กรุงเทพมหานคร');
  await page.getByTestId('ship-postcode').fill('10110');
  if (opts.express) await page.getByTestId('shipping-express').check();
  const button = baht(await page.getByTestId('place-order').textContent());

  // 3) server response
  const respP = page.waitForResponse((r) => r.url().endsWith('/api/orders') && r.request().method() === 'POST');
  await page.getByTestId('place-order').click();
  const resp = await respP;
  expect(resp.status()).toBe(201);
  const o = (await resp.json()).order;
  const server = { subtotal: o.subtotal as number, discount: o.discount as number, shipping: o.shipping as number, total: o.total as number };

  // 4) order page (the order the server saved)
  await expect(page.getByTestId('order-success')).toBeVisible();
  await expect(page.getByTestId('order-id')).toHaveText(/^PP-\d{6}$/); // format only — never the number
  const order = await readSummary();
  return { cart, button, server, order };
}

const src = (e: string, d?: string) => [
  { type: '[E]', description: e },
  ...(d ? [{ type: '[D]', description: d }] : []),
];

test.describe('char-money · ค่าส่งที่ค่าขอบ ฿999 (4 จุด)', () => {
  test('TC-CHAR-SHIP-01 ตะกร้า ฿998 ส่งปกติ → ค่าส่ง ฿50 ทุกจุด', {
    tag: ['@char', '@money'],
    annotation: src(
      'cart/checkout/order: ฿998 · ฿50 · ฿1,048 · POST /api/orders {subtotal 998, shipping 50, total 1048} — rea\\scratch\\lab4-explore.mjs s998',
      'ค่าส่งปกติ ฿50 (ยังไม่ครบ ฿999)',
    ),
  }, async ({ page }) => {
    const m = await buyAndRead(page, CART.mixed998);
    expect(m.cart).toEqual({ subtotal: 998, discount: 0, shipping: '฿50', total: 1048 });
    expect(m.button).toBe(1048);
    expect(m.server).toEqual({ subtotal: 998, discount: 0, shipping: 50, total: 1048 });
    expect(m.order).toEqual({ subtotal: 998, discount: 0, shipping: '฿50', total: 1048 });
  });

  test('TC-CHAR-SHIP-02 ตะกร้า ฿999 ส่งปกติ → ค่าหลังแก้ BUG-01 (server คิดเท่าหน้าเว็บ: ฟรี ฿999)', {
    tag: ['@char', '@money', '@bug01-fixed'],
    annotation: [
      ...src('LAB 6 หลังแก้ BUG-01 (ลบบล็อก PP-231 ใน petshop/lib/orders.ts) · cart/button ฿999 ฟรี · POST /api/orders {subtotal 999, shipping 0, total 999} · order page ฟรี ฿999'),
      { type: 'changed-by-BUG-01', description: 'เดิมเป็น legacy-quirk ล็อก server {shipping 50, total 1049} · พฤติกรรมเปลี่ยนโดยตั้งใจตาม BUG-01.md "แก้แล้ว" (วิธี A) จึงปรับค่าที่ล็อกเป็นค่าหลังแก้' },
    ],
  }, async ({ page }) => {
    const m = await buyAndRead(page, CART.mixed999);
    expect(m.cart).toEqual({ subtotal: 999, discount: 0, shipping: 'ฟรี', total: 999 });
    expect(m.button).toBe(999);
    expect(m.server).toEqual({ subtotal: 999, discount: 0, shipping: 0, total: 999 });
    expect(m.order).toEqual({ subtotal: 999, discount: 0, shipping: 'ฟรี', total: 999 });
  });

  test('TC-CHAR-SHIP-03 ตะกร้า ฿999 ส่งปกติ → ตาม TEST-DATA ต้องส่งฟรีทุกจุด', {
    tag: ['@char', '@money', '@bug01-fixed'],
    annotation: [
      ...src('LAB 6 หลังแก้ BUG-01: server/order page ฟรี ฿999 (เดิม ฿50 ฿1,049)', 'ค่าส่งปกติ ฿50 (ฟรีเมื่อซื้อครบ ฿999) → ที่ ฿999 ค่าส่ง 0 ยอด ฿999'),
      { type: 'changed-by-BUG-01', description: 'เดิมเป็น KNOWN-ISSUE (test.fail()) · BUG-01 แก้แล้ว (BUG-01.md "แก้แล้ว") จึงเอา test.fail() ออก ให้เป็น test ปกติที่ต้องผ่าน' },
    ],
  }, async ({ page }) => {
    const m = await buyAndRead(page, CART.mixed999);
    expect(m.cart).toEqual({ subtotal: 999, discount: 0, shipping: 'ฟรี', total: 999 });
    expect(m.button).toBe(999);
    expect(m.server).toEqual({ subtotal: 999, discount: 0, shipping: 0, total: 999 });
    expect(m.order).toEqual({ subtotal: 999, discount: 0, shipping: 'ฟรี', total: 999 });
  });

  test('TC-CHAR-SHIP-04 ตะกร้า ฿999 ส่งด่วน → ค่าส่ง ฿120 ทุกจุด', {
    tag: ['@char', '@money'],
    annotation: src(
      'cart (ยังเป็นส่งปกติ) ฟรี ฿999 · button ฿1,119 · POST /api/orders {shipping 120, total 1119, shippingMethod express} · order page ฿120 ฿1,119 — rea\\scratch\\lab4-explore.mjs s999 express',
      'ด่วน ฿120',
    ),
  }, async ({ page }) => {
    const m = await buyAndRead(page, CART.bowl999, { express: true });
    expect(m.cart).toEqual({ subtotal: 999, discount: 0, shipping: 'ฟรี', total: 999 }); // cart has no express choice yet
    expect(m.button).toBe(1119);
    expect(m.server).toEqual({ subtotal: 999, discount: 0, shipping: 120, total: 1119 });
    expect(m.order).toEqual({ subtotal: 999, discount: 0, shipping: '฿120', total: 1119 });
  });
});

test.describe('char-money · คูปองบนตะกร้าเดียวกัน (4 จุด)', () => {
  test('TC-CHAR-CPN-01 NEWCAT50 บนตะกร้า ฿998 (อาหารแมว ฿590) → ลด ฿50 ค่าส่ง ฿50 ยอด ฿998 ทุกจุด', {
    tag: ['@char', '@money', '@coupon'],
    annotation: src(
      'cart/checkout/order: ฿998 −฿50 ฿50 = ฿998 · POST /api/orders {discount 50, shipping 50, total 998} — rea\\scratch\\lab4-explore.mjs s998 coupon=NEWCAT50',
      'NEWCAT50 ลด ฿50 (อาหารแมว ≥ ฿500) · ค่าส่งปกติ ฿50',
    ),
  }, async ({ page }) => {
    const m = await buyAndRead(page, CART.mixed998, { coupon: 'NEWCAT50' });
    expect(m.cart).toEqual({ subtotal: 998, discount: 50, shipping: '฿50', total: 998 });
    expect(m.button).toBe(998);
    expect(m.server).toEqual({ subtotal: 998, discount: 50, shipping: 50, total: 998 });
    expect(m.order).toEqual({ subtotal: 998, discount: 50, shipping: '฿50', total: 998 });
  });
});

const golden = (name: string) => JSON.parse(readFileSync(new URL(`./golden/${name}`, import.meta.url), 'utf8'));

test.describe('char-money · API golden', () => {
  test('TC-CHAR-API-01 GET /api/products ตรงกับ golden (ตัด stock)', {
    tag: ['@char', '@api'],
    annotation: src('golden/products.json (บันทึกด้วย rea\\scratch\\lab4-golden.mjs · 28 รายการ · ตัด stock)'),
  }, async ({ request }) => {
    const res = await request.get('/api/products');
    expect(res.status()).toBe(200);
    const body = await res.json();
    const g = golden('products.json');
    expect(body.total).toBe(g.total);
    expect(body.items.map(({ stock, ...rest }: { stock: number }) => rest)).toEqual(g.items);
  });

  test('TC-CHAR-API-02 POST /api/coupons/validate 5 ตะกร้า × 6 โค้ด ตรงกับ golden', {
    tag: ['@char', '@api', '@coupon'],
    annotation: src(
      'golden/coupons-validate.json (30 กรณี · rea\\scratch\\lab4-golden.mjs) · PAW10 ปัดลง: ฿69→6 ฿499→49 ฿520→52 ฿998/999→99 · NEWCAT50 ฿499 ไม่ผ่าน ฿520 ผ่าน',
      'PAW10 ลด 10% · FREESHIP ส่งฟรี · NEWCAT50 ลด ฿50 (อาหารแมว ≥ ฿500) · SUMMER20 หมดอายุ',
    ),
  }, async ({ request }) => {
    const g = golden('coupons-validate.json');
    expect(g.cases.length).toBe(30);
    for (const c of g.cases) {
      const res = await request.post('/api/coupons/validate', { data: { code: c.code, items: c.items } });
      expect(res.status(), `${c.cart} ${c.code}`).toBe(c.status);
      expect(await res.json(), `${c.cart} ${c.code}`).toEqual(c.response);
    }
  });
});
