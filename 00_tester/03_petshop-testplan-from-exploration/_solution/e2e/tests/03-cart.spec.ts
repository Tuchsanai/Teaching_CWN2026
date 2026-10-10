import { test, expect, step, check, open, plan, addToCart, baht, checkSummary, summary, P } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.3 ตะกร้า (TC-CART-01 … 06)

test('TC-CART-01 ลูกแมว 400 g × 2 ยอดและแถบส่งฟรี', plan('TC-CART-01', '@cart'), async ({ page }) => {
  await step('1. ใส่ลูกแมว สูตรแซลมอน 400 g จำนวน 2 ลงตะกร้า', async () => {
    await addToCart(page, P.kitten400, 2);
  });
  await step('2. เปิดตะกร้า ตรวจยอด (189×2 = 378 < 999 → ส่ง 50 · 378+50 = 428)', async () => {
    await open(page, '/cart');
    await checkSummary(page, 'ตะกร้า:', { subtotal: 378, discount: 0, shipping: 50, total: 428 });
    await check(page, '🛒 = 2', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('2'));
    await check(page, 'แถบ "ซื้อเพิ่มอีก ฿621 เพื่อส่งฟรี" (999−378)', page.getByTestId('free-shipping-progress'),
      () => expect.soft(page.getByTestId('free-shipping-progress')).toHaveText(/ซื้อเพิ่มอีก ฿621 เพื่อส่งฟรี/));
  });
});

test('TC-CART-02 ตะกร้าสูตรลดก้อนขน 3 ชิ้น กด + และพิมพ์ 10', plan('TC-CART-02', '@cart'), async ({ page }) => {
  const qty = page.getByTestId('item-qty');
  await step('1. ใส่สูตรลดก้อนขน 3 ชิ้น แล้วเปิดตะกร้า', async () => {
    await addToCart(page, P.hairball, 3);
    await open(page, '/cart');
  });
  await step('2. กด + 1 ครั้ง', async () => {
    await page.getByTestId('item-plus').click();
    await page.waitForTimeout(300);
    await check(page, 'กด + แล้วจำนวนค้างที่ 3', qty, () => expect.soft(qty).toHaveValue('3'));
  });
  await step('3. พิมพ์จำนวน 10', async () => {
    await qty.fill('10');
    await qty.blur();
    await page.waitForTimeout(300);
    await check(page, 'พิมพ์ 10 แล้วจำนวนค้างที่ 3', qty, () => expect.soft(qty).toHaveValue('3'));
    await checkSummary(page, '', { subtotal: 1560, shipping: 0, total: 1560 });
  });
});

test('TC-CART-03 ลบสินค้าทีละรายการ', plan('TC-CART-03', '@cart'), async ({ page }) => {
  await step('1. ใส่ลูกแมว 400 g ×1 และไม้ตกแมว ×1 แล้วเปิดตะกร้า', async () => {
    await addToCart(page, P.kitten400);
    await addToCart(page, P.featherWand);
    await open(page, '/cart');
  });
  await step('2. กด ✕ ลบไม้ตกแมว', async () => {
    await page.locator(`[data-testid="cart-item"][data-slug="${P.featherWand.slug}"]`).getByTestId('item-remove').click();
    await expect(page.getByTestId('cart-item')).toHaveCount(1);
    await check(page, '🛒 = 1', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('1'));
    await checkSummary(page, '', { subtotal: 189, total: 239 });
  });
  await step('3. กด ✕ ลบรายการที่เหลือ', async () => {
    await page.getByTestId('item-remove').click();
    await check(page, 'ตะกร้าว่าง', page.getByTestId('empty-cart'), () => expect.soft(page.getByTestId('empty-cart')).toBeVisible());
    await check(page, '🛒 = 0', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('0'));
    await check(page, 'ไม่มีปุ่มชำระเงิน', page.getByTestId('checkout-button'), () => expect.soft(page.getByTestId('checkout-button')).toHaveCount(0));
  });
});

test('TC-CART-04 รีโหลดแล้วตะกร้าและรายการโปรดยังอยู่', plan('TC-CART-04', '@cart'), async ({ page }) => {
  let before = 0;
  await step('1. ใส่ลูกแมว 400 g 2 ชิ้น และกด ♥ 1 สินค้า', async () => {
    await addToCart(page, P.kitten400, 2);
    await page.getByTestId('wishlist-toggle').first().click();
    await expect(page.getByTestId('wishlist-count')).toHaveText('1');
    await open(page, '/cart');
    before = baht(await summary(page).total.innerText());
  });
  await step('2. รีโหลดหน้า', async () => {
    await page.reload();
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    await check(page, '🛒 = 2', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('2'));
    await check(page, '♥ = 1', page.getByTestId('wishlist-count'), () => expect.soft(page.getByTestId('wishlist-count')).toHaveText('1'));
    await check(page, `ยอดชำระเท่าเดิม (฿${before})`, summary(page).total, async () => expect.soft(baht(await summary(page).total.innerText())).toBe(before));
  });
});

test('TC-CART-05 ใส่เกินสต็อก ข้อความต้องบอกตามจริง', plan('TC-CART-05', '@cart'), async ({ page }) => {
  await step('1. หน้าสูตรลดก้อนขน ใส่ 2 ชิ้น', async () => {
    await addToCart(page, P.hairball, 2);
    await page.getByTestId('toast').waitFor({ state: 'hidden', timeout: 10_000 }).catch(() => {});
  });
  await step('2. ใส่อีก 2 ชิ้น (รวม 4 > สต็อก 3)', async () => {
    await page.getByTestId('qty-input').fill('2');
    await page.getByTestId('add-to-cart').click();
    // toast อยู่บนจอแค่ ~3 วินาที → อ่านข้อความทันทีที่ขึ้น แล้วค่อยตรวจ
    const toast = page.getByTestId('toast').last();
    await toast.waitFor({ state: 'visible' });
    const said = (await toast.innerText()).replace(/\s+/g, ' ').trim();
    await check(page, 'ข้อความครั้งที่ 2 บอกว่าเพิ่มได้แค่ 1 / ครบจำนวนสต็อกแล้ว', toast,
      () => expect.soft(said).toMatch(/สต็อก|ครบ|สูงสุด|ได้แค่|ได้เพียง|เหลือ|จำกัด/),
      { expected: 'ข้อความบอกว่าเพิ่มได้แค่ 1 / ครบจำนวนสต็อกแล้ว', near: page.getByTestId('add-to-cart') });
  });
  await step('3. เปิดตะกร้า', async () => {
    await open(page, '/cart');
    await check(page, 'ตะกร้ามี 3 ชิ้น (ไม่เกินสต็อก)', page.getByTestId('item-qty'), () => expect.soft(page.getByTestId('item-qty')).toHaveValue('3'));
    await check(page, 'ยอด ฿1,560', summary(page).subtotal, async () => expect.soft(baht(await summary(page).subtotal.innerText())).toBe(1560));
  });
});

test('TC-CART-06 ซื้อคู่กัน "เพิ่มทั้งชุดลงตะกร้า"', plan('TC-CART-06', '@cart'), async ({ page }) => {
  const box: { slug: string; name: string; price: number }[] = [];
  await step('1. เปิด "ลูกแมว สูตรแซลมอน" จดชื่อและราคาทุกชิ้นในกล่อง "มักซื้อคู่กัน"', async () => {
    await open(page, `/products/${P.kitten400.slug}`);
    await page.getByTestId('bought-together').scrollIntoViewIfNeeded();
    // ชิ้นหลักของกล่อง = สินค้าหน้านี้ ขนาดเล็กสุด (ปุ่มขนาดแรก)
    const first = page.getByTestId('size-option').first();
    box.push({ slug: P.kitten400.slug, name: await page.getByTestId('product-title').innerText(), price: baht((await first.innerText()).split('\n').pop()!) });
    for (const card of await page.getByTestId('bought-together').getByTestId('product-card').all()) {
      box.push({ slug: (await card.getAttribute('data-slug'))!, name: await card.getByTestId('product-name').innerText(), price: baht((await card.innerText()).match(/฿[\d,]+/)?.[0] ?? '') });
    }
    test.info().annotations.push({ type: 'ข้อมูลนำเข้า (จดจากกล่อง)', description: box.map((b) => `${b.name} ฿${b.price}`).join(' + ') });
  });
  const sum = () => box.reduce((n, b) => n + b.price, 0);
  await step('2. กด "เพิ่มทั้งชุดลงตะกร้า"', async () => {
    await page.getByTestId('add-bundle').click();
    await expect(page.getByTestId('toast')).toBeVisible();
    await check(page, `🛒 = จำนวนชิ้นในกล่อง (${box.length})`, page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText(String(box.length)));
  });
  await step('3. เปิดตะกร้า', async () => {
    await open(page, '/cart');
    const slugs = await page.getByTestId('cart-item').evaluateAll((els) => els.map((e) => e.getAttribute('data-slug')));
    await check(page, 'ตะกร้ามีทุกชิ้นในกล่อง ไม่มีชิ้นอื่น', page.getByTestId('cart-item').first(),
      () => expect.soft([...slugs].sort()).toEqual(box.map((b) => b.slug).sort()));
    const qtys = await page.getByTestId('item-qty').evaluateAll((els) => els.map((e) => (e as HTMLInputElement).value));
    await check(page, 'ชิ้นละ 1', page.getByTestId('item-qty').first(), () => expect.soft(qtys.every((q) => q === '1')).toBe(true));
    await checkSummary(page, '', { subtotal: sum(), total: sum() < 999 ? sum() + 50 : sum() });
  });
});
