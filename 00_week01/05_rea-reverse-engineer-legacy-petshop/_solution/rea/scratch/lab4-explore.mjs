// LAB 4 explore (headless): buy one boundary cart through the UI and dump every money-ish data-testid on cart / checkout / order page.
// usage: node rea\scratch\lab4-explore.mjs s999|s998 [express]
import { chromium } from 'playwright';
const B = process.env.BASE_URL ?? 'http://localhost:4000';
const carts = {
  s998: [['kitten-salmon-dry', '1.5 kg', 1], ['dental-chew-treat', null, 1], ['cat-scratcher', null, 1]],
  s999: [['cat-feather-wand', null, 1], ['dog-slow-bowl', null, 3]],
  t999: [['cat-feather-wand', null, 1], ['tuna-pouch', 'แพ็ค 12 ซอง', 2], ['puppy-lamb-wet', null, 2]],
};
const name = process.argv[2] ?? 's999';
const express = process.argv.includes('express');
const browser = await chromium.launch();
const ctx = await browser.newContext({ baseURL: B, locale: 'th-TH', viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();
const email = `explore-${Date.now()}-${Math.floor(Math.random() * 1e6)}@test.dev`;
const reg = await page.request.post('/api/auth/register', { data: { name: 'นักทดสอบ ใจเย็น', email, password: 'Test1234', confirm: 'Test1234', pet: 'cat', terms: true } });
console.log('register', reg.status());
const ready = () => page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
const dump = async (label) => {
  const rows = await page.$$eval('[data-testid]', (els) => els
    .filter((e) => /summary|total|shipping|discount|subtotal|place-order|free-shipping|checkout-button|order-id|item-line|order-item|price|ship-method|shipping-/.test(e.dataset.testid))
    .map((e) => `${e.dataset.testid}${e.getAttribute('value') ? '[' + e.getAttribute('value') + ']' : ''} = ${(e.textContent ?? '').replace(/\s+/g, ' ').trim().slice(0, 120)}`));
  console.log(`--- ${label} ${page.url()}\n` + rows.join('\n'));
};
for (const [slug, size, qty] of carts[name]) {
  await page.goto(`/products/${slug}`); await ready();
  if (size) await page.locator(`[data-testid="size-option"][data-size="${size}"]`).click();
  for (let i = 1; i < qty; i++) await page.getByTestId('qty-plus').click();
  await page.getByTestId('add-to-cart').click();
}
await page.goto('/cart'); await ready();
const coupon = process.argv.find((a) => a.startsWith('coupon='))?.slice(7);
if (coupon) { await page.getByTestId('coupon-input').fill(coupon); await page.getByTestId('coupon-apply').click(); await page.getByTestId('coupon-message').waitFor(); }
await dump('cart');
await page.goto('/checkout'); await ready();
await page.getByTestId('ship-phone').fill('0812345678');
await page.getByTestId('ship-address').fill('99/9 ถนนสุขุมวิท แขวงคลองเตย');
await page.getByTestId('ship-province').selectOption('กรุงเทพมหานคร');
await page.getByTestId('ship-postcode').fill('10110');
const radios = await page.$$eval('input[type=radio]', (els) => els.map((e) => `${e.dataset.testid ?? ''} name=${e.name} value=${e.value} checked=${e.checked}`));
console.log('radios:', radios.join(' | '));
if (express) await page.locator('input[type=radio][value="express"]').check();
await dump('checkout');
const respP = page.waitForResponse((r) => r.url().endsWith('/api/orders') && r.request().method() === 'POST');
await page.getByTestId('place-order').click();
const resp = await respP;
const body = await resp.json();
const o = body.order;
console.log('POST /api/orders', resp.status(), 'request', resp.request().postData()?.slice(0, 300));
console.log('response', JSON.stringify({ subtotal: o.subtotal, discount: o.discount, shipping: o.shipping, total: o.total, shippingMethod: o.shippingMethod, items: o.items.map((i) => [i.slug, i.size, i.price, i.qty, i.lineTotal]) }));
await page.getByTestId('order-success').waitFor();
await dump('order');
await browser.close();
