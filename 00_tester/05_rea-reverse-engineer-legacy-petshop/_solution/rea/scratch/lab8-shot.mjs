// LAB 8 step 6: headless 1280x800 screenshot of /checkout with gift wrap ticked (basket ฿1,499 → ค่าห่อ ฿30 · ยอด ฿1,529)
// usage (from chapter root): node rea\scratch\lab8-shot.mjs
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';

const B = 'http://localhost:4000';
const LINES = [['kitten-salmon-dry', '400 g'], ['cat-fountain', '2 ลิตร'], ['small-breed-chicken-dry', '1.5 kg']];
const OUT = 'out/shots/lab8-checkout-giftwrap.png';

const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1280, height: 800 }, baseURL: B })).newPage();
const ready = () => page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
const reg = await page.request.post('/api/auth/register', {
  data: { name: 'ลูกค้า ห่อของขวัญ', email: `lab8-shot-${Date.now()}@example.test`, password: 'Test1234', confirm: 'Test1234', pet: 'cat', terms: true },
});
if (!reg.ok()) throw new Error(`register ${reg.status()}`);
for (const [slug, size] of LINES) {
  await page.goto(`/products/${slug}`); await ready();
  const opt = page.locator(`[data-testid="size-option"][data-size="${size}"]`);
  if (await opt.count()) await opt.click();
  await page.getByTestId('add-to-cart').click();
  await page.getByTestId('toast').waitFor();
}
await page.goto('/checkout'); await ready();
await page.getByTestId('ship-phone').fill('0812345678');
await page.getByTestId('ship-address').fill('99/9 ถนนสุขุมวิท แขวงคลองเตย');
await page.getByTestId('ship-postcode').fill('10110');
await page.getByTestId('gift-wrap').check();
await page.getByTestId('summary-giftwrap').waitFor();
await page.getByTestId('gift-wrap').evaluate((el) => el.scrollIntoView({ block: 'center' }));
await page.waitForTimeout(300);
mkdirSync('out/shots', { recursive: true });
await page.screenshot({ path: OUT });
const read = async (id) => ((await page.getByTestId(id).textContent()) ?? '').trim();
console.log(JSON.stringify({ shot: OUT, subtotal: await read('summary-subtotal'), shipping: await read('summary-shipping'), giftwrap: await read('summary-giftwrap'), total: await read('summary-total'), button: await read('place-order') }));
await browser.close();
