// PR-1 black-box repro (headless, no source reading): add "สูตรลดก้อนขน" (hairball-control-dry) 2 + 2 from the product page,
// capture every toast/status message and the cart contents. Also probes 3+1 (none left) and 4-at-once.
// usage: node rea\scratch\pr1-repro.mjs   (resets test data first)
import { chromium } from 'playwright';
const B = process.env.BASE_URL ?? 'http://localhost:4000';
const SLUG = 'hairball-control-dry';
const reset = await fetch(`${B}/api/test/reset`, { method: 'POST' });
console.log('reset', reset.status);
const browser = await chromium.launch();

async function scenario(label, rounds) {
  const ctx = await browser.newContext({ baseURL: B, locale: 'th-TH', viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  const ready = () => page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
  await page.goto(`/products/${SLUG}`); await ready();
  const ids = await page.$$eval('[data-testid]', (els) => [...new Set(els.map((e) => e.dataset.testid))]);
  if (label === 'A') console.log('testids on product page:', ids.join(' '));
  const stockTxt = await page.locator('[data-testid*="stock"]').allTextContents().catch(() => []);
  console.log(`[${label}] stock text:`, JSON.stringify(stockTxt));
  let r = 0;
  for (const qty of rounds) {
    r++;
    // reset qty selector to 1 by reloading the page
    await page.goto(`/products/${SLUG}`); await ready();
    for (let i = 1; i < qty; i++) {
      const plus = page.getByTestId('qty-plus');
      if (await plus.isDisabled()) { console.log(`[${label}] round ${r}: qty-plus disabled at ${i}`); break; }
      await plus.click();
    }
    const qtyVal = await page.locator('[data-testid="qty-value"], [data-testid="qty-input"], [data-testid="qty"]').first().textContent().catch(() => '?');
    await page.getByTestId('add-to-cart').click();
    await page.waitForTimeout(400);
    const msgs = await page.$$eval('[role="status"], [role="alert"], [aria-live], [data-testid*="toast"], [data-testid*="message"], [data-testid*="notice"]',
      (els) => els.map((e) => `${e.dataset.testid ?? e.getAttribute('role') ?? 'aria-live'}: ${(e.textContent ?? '').replace(/\s+/g, ' ').trim()}`).filter((s) => !/:\s*$/.test(s)));
    const badge = await page.locator('[data-testid*="cart-count"], [data-testid*="cart-badge"]').allTextContents().catch(() => []);
    console.log(`[${label}] round ${r}: asked ${qty} (qty shown ${JSON.stringify(qtyVal)}) → messages ${JSON.stringify(msgs)} badge ${JSON.stringify(badge)}`);
  }
  await page.goto('/cart'); await ready();
  const cart = await page.$$eval('[data-testid]', (els) => els
    .filter((e) => /item|qty|line|subtotal|total|summary/.test(e.dataset.testid))
    .map((e) => `${e.dataset.testid} = ${(e.getAttribute('value') ?? '')}${(e.textContent ?? '').replace(/\s+/g, ' ').trim().slice(0, 100)}`));
  const ls = await page.evaluate(() => localStorage.getItem('pp-cart'));
  console.log(`[${label}] cart page:\n  ` + cart.join('\n  ') + `\n  pp-cart=${ls}`);
  await page.screenshot({ path: `out/pr1-${label}-cart.png` });
  await ctx.close();
}

await scenario('A', [2, 2]);   // the customer's report
await scenario('B', [3, 1]);   // full first, then nothing left
await scenario('C', [4]);      // more than stock at once
await browser.close();
