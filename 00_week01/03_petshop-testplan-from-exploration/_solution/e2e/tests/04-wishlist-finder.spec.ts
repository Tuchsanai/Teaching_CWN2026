import { test, expect, step, check, open, plan } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.3 รายการโปรด · ตัวช่วยเลือกอาหาร

test('TC-WISH-01 รายการโปรด: เพิ่ม ลบ ย้ายไปตะกร้า', plan('TC-WISH-01', '@wishlist'), async ({ page }) => {
  const heart = page.getByTestId('wishlist-count');
  const items = page.getByTestId('wishlist-item');
  let moved = '';
  await step('1. แคตตาล็อก กด ♥ 2 สินค้า', async () => {
    await open(page, '/products');
    await page.getByTestId('wishlist-toggle').nth(0).click();
    await page.getByTestId('wishlist-toggle').nth(1).click();
    await check(page, '♥ = 2', heart, () => expect.soft(heart).toHaveText('2'));
  });
  await step('2. ไปหน้า /wishlist', async () => {
    await open(page, '/wishlist');
    await check(page, '/wishlist มี 2 รายการ', items.first(), () => expect.soft(items).toHaveCount(2));
    await check(page, '♥ = จำนวนรายการในหน้า (2)', heart, () => expect.soft(heart).toHaveText('2'));
  });
  await step('3. กด "ลบ" 1 รายการ (ไม่รีโหลด)', async () => {
    await page.getByTestId('wishlist-remove').first().click();
    await check(page, '/wishlist เหลือ 1 รายการ', items.first(), () => expect.soft(items).toHaveCount(1));
    await check(page, 'ทันที (ไม่รีโหลด) ♥ บนหัวเว็บ = 1', heart, () => expect.soft(heart).toHaveText('1'));
  });
  await step('4. รีโหลดหน้า', async () => {
    await page.reload();
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    await check(page, 'หลังรีโหลด /wishlist ยังมี 1 รายการ', items.first(), () => expect.soft(items).toHaveCount(1));
    await check(page, 'หลังรีโหลด ♥ = 1', heart, () => expect.soft(heart).toHaveText('1'));
  });
  await step('5. กด "ย้ายไปตะกร้า" รายการที่เหลือ', async () => {
    moved = (await items.first().getAttribute('data-slug')) ?? '';
    await page.getByTestId('move-to-cart').first().click();
    await page.waitForTimeout(500);
    await check(page, '🛒 = 1', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('1'));
    const shown = await items.count();
    await check(page, `♥ = จำนวนรายการในหน้า (${shown})`, heart, () => expect.soft(heart).toHaveText(String(shown)));
  });
  await step('6. เปิดตะกร้า', async () => {
    await open(page, '/cart');
    const line = page.locator(`[data-testid="cart-item"][data-slug="${moved}"]`);
    await check(page, 'สินค้าที่ย้ายอยู่ในตะกร้า', page.getByTestId('cart-item').first(), () => expect.soft(line).toHaveCount(1));
  });
});

test('TC-FIND-01 ตัวช่วยเลือกอาหาร: แมว วัยโต ไม่เอาสูตรไก่', plan('TC-FIND-01', '@finder'), async ({ page }) => {
  await step('1. เปิด /finder เลือก แมว → ถัดไป', async () => {
    await open(page, '/finder');
    await page.getByTestId('finder-pet-cat').click();
    await page.getByTestId('finder-next').click();
  });
  await step('2. เลือก วัยโต (แมวโต) → ถัดไป', async () => {
    await page.getByTestId('finder-life-adult').click();
    await page.getByTestId('finder-next').click();
  });
  await step('3. ติ๊ก "ไม่เอาสูตรไก่" แล้วกด "ดูผลลัพธ์"', async () => {
    await page.getByTestId('finder-no-chicken').check();
    await page.getByTestId('finder-submit').click();
    await expect(page.getByTestId('finder-results')).toBeVisible();
  });
  const results = page.getByTestId('finder-result');
  const slugs = await results.evaluateAll((els) => els.map((e) => e.getAttribute('data-slug')!));
  await step('4. ตรวจผลลัพธ์', async () => {
    await check(page, `มีผล ≥ 1 รายการ (ได้ ${slugs.length})`, page.getByTestId('finder-results'), () => expect.soft(slugs.length).toBeGreaterThanOrEqual(1));
    const names = await results.evaluateAll((els) => els.map((e) => e.textContent ?? ''));
    const chickenByName = names.filter((t) => /ไก่|chicken/i.test(t.replace(/ไม่มีไก่/g, '')));
    await check(page, 'ชื่อผลลัพธ์ไม่มีสูตรไก่', results.filter({ hasText: /chicken/i }).first(),
      () => expect.soft(chickenByName.join(', ') || 'ไม่มี').toBe('ไม่มี'), { expected: 'ไม่มีผลที่เป็นสูตรไก่' });
  });
  await step('5. เปิดหน้ารายละเอียดของผลแต่ละรายการ ดู "โปรตีนหลัก"', async () => {
    const notCat: string[] = [];
    const chicken: string[] = [];
    for (const slug of slugs) {
      await open(page, `/products/${slug}`);
      const text = await page.locator('main').innerText();
      const title = await page.getByTestId('product-title').innerText();
      const protein = text.match(/โปรตีนหลัก\s*\n\s*(.+)/)?.[1]?.trim() ?? '';
      const head = text.slice(0, 150); // breadcrumb + ป้ายสัตว์ด้านบนหน้า (ก่อนส่วนสินค้าแนะนำ)
      if (!head.includes('🐱') || head.includes('🐶')) notCat.push(title);
      if (/ไก่|chicken/i.test(title + ' ' + protein)) chicken.push(`${title} (โปรตีนหลัก: ${protein})`);
    }
    await check(page, 'ผลทุกรายการเป็นของแมว', page.getByTestId('product-title'), () => expect.soft(notCat.join(', ') || 'ไม่มี').toBe('ไม่มี'), { expected: 'ทุกผลเป็นของแมว' });
    await check(page, 'ไม่มีสินค้าโปรตีนไก่ (ชื่อ/โปรตีนหลัก)', page.getByTestId('product-title'),
      () => expect.soft(chicken.join(', ') || 'ไม่มี').toBe('ไม่มี'), { expected: 'ไม่มีสูตรไก่' });
  });
});
