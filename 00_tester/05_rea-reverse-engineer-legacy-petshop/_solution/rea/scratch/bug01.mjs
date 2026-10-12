// LAB 5 · BUG-01 black-box (headless): replay the customer's story + neighbour carts.
// Reads money at 4 points (cart · place-order button · POST /api/orders response · order page) + /account.
// HAR of the whole run → out\bug01.har (127.0.0.1 so REA can read it later).
// Usage (from chapter root): node rea\scratch\bug01.mjs [caseName ...]
import { chromium } from 'playwright';
import { writeFileSync } from 'node:fs';

const B = 'http://127.0.0.1:4000';
const CASES = {
  // customer's cart: ไม้ตกแมว 1 + ชามกินช้า 3 = ฿129 + ฿290×3 = ฿999
  'c999': { lines: [['cat-feather-wand', null, 1], ['dog-slow-bowl', null, 3]] },
  // ฿1 under: ฿590 + ฿149 + ฿259 = ฿998
  'c998': { lines: [['kitten-salmon-dry', '1.5 kg', 1], ['dental-chew-treat', null, 1], ['cat-scratcher', null, 1]] },
  // ฿1 over: ฿45 + ฿79×2 + ฿149 + ฿129×2 + ฿390 = ฿1,000
  'c1000': { lines: [['puppy-lamb-wet', null, 1], ['beef-stew-can', '400 g', 2], ['dog-rope-toy', null, 1], ['salmon-skin-treat', null, 2], ['tuna-pouch', 'แพ็ค 12 ซอง', 1]] },
  'c999-PAW10': { lines: [['cat-feather-wand', null, 1], ['dog-slow-bowl', null, 3]], coupon: 'PAW10' },
  'c999-FREESHIP': { lines: [['cat-feather-wand', null, 1], ['dog-slow-bowl', null, 3]], coupon: 'FREESHIP' },
  'c999-express': { lines: [['cat-feather-wand', null, 1], ['dog-slow-bowl', null, 3]], express: true },
  'c998-PAW10': { lines: [['kitten-salmon-dry', '1.5 kg', 1], ['dental-chew-treat', null, 1], ['cat-scratcher', null, 1]], coupon: 'PAW10' },
};
const pick = process.argv.slice(2);
const names = pick.length ? pick : Object.keys(CASES);

const baht = (t) => Number((t ?? '').replace(/[^\d]/g, ''));
const txt = async (loc) => ((await loc.textContent()) ?? '').replace(/\s+/g, ' ').trim();

await fetch(`${B}/api/test/reset`, { method: 'POST' }).then((r) => console.log('reset', r.status));

const browser = await chromium.launch();
const ctx = await browser.newContext({ baseURL: B, locale: 'th-TH', viewport: { width: 1280, height: 800 }, recordHar: { path: 'out/bug01.har' } });
const page = await ctx.newPage();
const open = async (p) => { await page.goto(p); await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' }); };

// one fresh buyer for the whole run (customer's order number is from the real shop — never looked up here)
const email = `bug01-${Date.now()}@test.dev`;
const reg = await page.request.post('/api/auth/register', { data: { name: 'ลูกค้า ทดสอบ', email, password: 'Test1234', confirm: 'Test1234', pet: 'cat', terms: true } });
console.log('register', reg.status());

const summary = async () => ({
  subtotal: baht(await page.getByTestId('summary-subtotal').textContent()),
  discount: baht(await page.getByTestId('summary-discount').textContent()),
  shipping: await txt(page.getByTestId('summary-shipping')),
  total: baht(await page.getByTestId('summary-total').textContent()),
});

const results = {};
for (const name of names) {
  const c = CASES[name];
  await open('/');
  await page.evaluate(() => Object.keys(localStorage).filter((k) => k.startsWith('pp-') && k !== 'pp-wishlist').forEach((k) => localStorage.removeItem(k)));
  for (const [slug, size, qty] of c.lines) {
    await open(`/products/${slug}`);
    if (size) await page.locator(`[data-testid="size-option"][data-size="${size}"]`).click();
    for (let i = 1; i < qty; i++) await page.getByTestId('qty-plus').click();
    await page.getByTestId('add-to-cart').click();
    await page.getByTestId('toast').waitFor();
  }
  await open('/cart');
  if (c.coupon) {
    await page.getByTestId('coupon-input').fill(c.coupon);
    await page.getByTestId('coupon-apply').click();
    await page.getByTestId('coupon-message').waitFor();
  }
  const cart = await summary();
  const freeBanner = await page.locator('[data-testid*="free-shipping"]').allTextContents().then((a) => a.map((s) => s.trim()).join(' | '));
  await page.screenshot({ path: `out/bug01-${name}-cart.png` });

  await open('/checkout');
  await page.getByTestId('ship-phone').fill('0812345678');
  await page.getByTestId('ship-address').fill('99/9 ถนนสุขุมวิท แขวงคลองเตย');
  await page.getByTestId('ship-province').selectOption('กรุงเทพมหานคร');
  await page.getByTestId('ship-postcode').fill('10110');
  if (c.express) await page.getByTestId('shipping-express').check();
  const checkout = await summary().catch(() => null);
  const buttonText = await txt(page.getByTestId('place-order'));
  await page.screenshot({ path: `out/bug01-${name}-checkout.png` });

  const respP = page.waitForResponse((r) => r.url().endsWith('/api/orders') && r.request().method() === 'POST');
  await page.getByTestId('place-order').click();
  const resp = await respP;
  const reqBody = resp.request().postDataJSON();
  const o = (await resp.json()).order ?? {};
  await page.getByTestId('order-success').waitFor();
  const order = await summary();
  const orderId = await txt(page.getByTestId('order-id'));
  await page.screenshot({ path: `out/bug01-${name}-order.png` });

  await open('/account');
  const acct = await page.locator('[data-testid]').evaluateAll((els, id) => els
    .filter((e) => (e.textContent ?? '').includes(id) && /order/.test(e.dataset.testid) && e.children.length > 0)
    .map((e) => `${e.dataset.testid} = ${(e.textContent ?? '').replace(/\s+/g, ' ').trim().slice(0, 160)}`), orderId);

  results[name] = {
    cart, freeBanner, checkout, button: baht(buttonText), buttonText,
    request: { keys: Object.keys(reqBody ?? {}), shipping: reqBody?.shipping, coupon: reqBody?.coupon ?? reqBody?.couponCode ?? null, hasFeeOrTotal: /fee|total|cost|price/i.test(JSON.stringify(reqBody ?? {}).replace(/"items".*?\]/s, '')) },
    status: resp.status(),
    server: { subtotal: o.subtotal, discount: o.discount, shipping: o.shipping, total: o.total, shippingMethod: o.shippingMethod },
    order, account: acct.slice(-1)[0] ?? '(not found)',
  };
  console.log(name, JSON.stringify({ cart, button: results[name].button, server: results[name].server, order, account: results[name].account }));
}
await ctx.close(); // flushes HAR
await browser.close();
writeFileSync('out/bug01-blackbox.json', JSON.stringify({ base: B, at: new Date().toISOString(), results }, null, 2), 'utf8');
console.log('saved out/bug01-blackbox.json + out/bug01.har');
