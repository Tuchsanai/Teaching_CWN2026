import { test, expect, step, check, open, plan, addToCart, baht, summary, P } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.2 ค้นหา · กรอง · สินค้า

const cards = (page: import('@playwright/test').Page) => page.getByTestId('product-card');

async function search(page: import('@playwright/test').Page, q: string) {
  await page.getByTestId('search-input').fill(q);
  await page.getByTestId('search-submit').click();
  await page.waitForURL(/\/products\?q=/);
  await expect(page.getByTestId('result-count')).toBeVisible();
}

test('TC-SRCH-01 ค้น แซลมอน / salmon / SALMON', plan('TC-SRCH-01', '@search'), async ({ page }) => {
  const counts: number[] = [];
  await open(page, '/');
  for (const [n, q] of [['1', 'แซลมอน'], ['2', 'salmon'], ['3', 'SALMON']] as const) {
    await step(`${n}. ค้นหา "${q}"`, async () => {
      await search(page, q);
      const found = baht(await page.getByTestId('result-count').innerText());
      const shown = await cards(page).count();
      counts.push(shown);
      await check(page, `"${q}": พบ N ≥ 1`, page.getByTestId('result-count'), () => expect.soft(shown).toBeGreaterThanOrEqual(1));
      await check(page, `"${q}": "พบ N รายการ" = จำนวนการ์ด (${shown})`, page.getByTestId('result-count'), () => expect.soft(found).toBe(shown));
      // ชื่อบนการ์ด = ชื่อไทย (product-name) + ชื่ออังกฤษใต้ชื่อไทย → ใช้ข้อความทั้งการ์ด
      const pairs = await cards(page).evaluateAll((els) => els.map((e) => [e.querySelector('[data-testid="product-name"]')?.textContent ?? '', e.textContent ?? '']));
      const missing = pairs.filter(([, text]) => !/แซลมอน|salmon/i.test(text)).map(([name]) => name);
      const bad = missing.length ? cards(page).filter({ hasNotText: /แซลมอน|salmon/i }).first() : null;
      await check(page, `"${q}": ทุกการ์ดมีคำว่า แซลมอน/Salmon ในชื่อ`, bad,
        () => expect.soft(missing.join(', ') || 'ไม่มี').toBe('ไม่มี'), { expected: 'ไม่มีการ์ดที่ชื่อไม่มีคำค้น' });
    });
  }
  await step('4. เทียบจำนวนผลของ 3 คำ', async () => {
    await check(page, `ทั้ง 3 คำได้จำนวนผลเท่ากัน (${counts.join(' / ')})`, null, () => expect.soft(new Set(counts).size).toBe(1));
  });
});

test('TC-SRCH-02 ค้นคำที่ไม่มี xyz', plan('TC-SRCH-02', '@search'), async ({ page }) => {
  await step('1. ค้นหา "xyz"', async () => {
    await open(page, '/');
    await search(page, 'xyz');
    await check(page, '0 การ์ด', page.getByTestId('result-count'), () => expect.soft(cards(page)).toHaveCount(0));
    await check(page, 'ข้อความ "ไม่พบสินค้าที่ตรงกับการค้นหา"', page.getByTestId('empty-results'),
      () => expect.soft(page.getByTestId('empty-results')).toContainText('ไม่พบสินค้าที่ตรงกับการค้นหา'), { near: page.getByTestId('result-count') });
  });
});

test('TC-CAT-01 กรอง แมว + ของเล่น เรียงราคาต่ำ → สูง', plan('TC-CAT-01', '@catalog'), async ({ page }) => {
  await step('1. เปิดสินค้าทั้งหมด กด "แมว" เลือกประเภท "ของเล่น" และเรียง "ราคา: ต่ำ → สูง"', async () => {
    await open(page, '/products');
    await page.getByTestId('filter-pet-cat').click();
    await page.getByTestId('filter-type').selectOption({ label: 'ของเล่น' });
    await page.getByTestId('sort-select').selectOption({ label: 'ราคา: ต่ำ → สูง' });
    await page.waitForURL(/sort=/);
    await page.waitForTimeout(500);
  });
  await step('2. ตรวจการ์ดทุกใบ', async () => {
    const texts = await cards(page).allInnerTexts();
    const notCatToy = texts.filter((t) => !(t.includes('🐱') && t.includes('ของเล่น')) || t.includes('🐶') || /อาหาร|ขนม/.test(t));
    await check(page, 'ทุกการ์ดเป็นของเล่นแมว (ไม่มีอาหาร ไม่มีของสุนัข)', cards(page).first(),
      () => expect.soft(notCatToy.join(', ') || 'ไม่มี').toBe('ไม่มี'), { expected: 'ไม่มีการ์ดอื่นนอกจากของเล่นแมว' });
    const prices = (await page.getByTestId('product-price').allInnerTexts()).map(baht);
    const sorted = [...prices].sort((a, b) => a - b);
    await check(page, `ราคาเรียงไม่ลดลง (${prices.join(' → ')})`, page.getByTestId('product-price').first(), () => expect.soft(prices).toEqual(sorted));
    const found = baht(await page.getByTestId('result-count').innerText());
    await check(page, `"พบ N รายการ" = จำนวนการ์ด (${texts.length})`, page.getByTestId('result-count'), () => expect.soft(found).toBe(texts.length));
  });
});

test('TC-PROD-01 ราคาตามขนาด 1.5 kg', plan('TC-PROD-01', '@product'), async ({ page }) => {
  let btnPrice = 0;
  await step('1. เปิด "ลูกแมว สูตรแซลมอน" แล้วเลือก 1.5 kg', async () => {
    await open(page, `/products/${P.kitten15.slug}`);
    const btn = page.locator('[data-testid="size-option"][data-size="1.5 kg"]');
    btnPrice = baht((await btn.innerText()).replace(/1\.5 kg/, ''));
    await btn.click();
    await check(page, `ราคาบนหน้าเปลี่ยนเป็นราคาบนปุ่ม 1.5 kg (฿${btnPrice})`, page.getByTestId('product-price'),
      async () => expect.soft(baht(await page.getByTestId('product-price').innerText())).toBe(btnPrice));
    await check(page, 'ราคาบนปุ่ม 1.5 kg = ฿590', btn, () => expect.soft(btnPrice).toBe(590));
  });
  await step('2. กด "เพิ่มลงตะกร้า"', async () => {
    await page.getByTestId('add-to-cart').click();
    const toast = page.getByTestId('toast');
    await check(page, 'toast มีชื่อสินค้าและขนาด "(1.5 kg)"', toast, async () => {
      await expect.soft(toast).toContainText('ลูกแมว สูตรแซลมอน');
      await expect.soft(toast).toContainText('(1.5 kg)');
    });
    await check(page, '🛒 = 1', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('1'));
  });
  await step('3. เปิดตะกร้า', async () => {
    await open(page, '/cart');
    const line = page.getByTestId('cart-item');
    await check(page, 'ตะกร้ามีบรรทัดขนาด 1.5 kg', line, () => expect.soft(page.getByTestId('item-size')).toHaveText(['1.5 kg']));
    await check(page, 'ยอดบรรทัด ฿590 (ไม่ใช่ ฿189)', page.getByTestId('item-line-total'),
      async () => expect.soft(baht(await page.getByTestId('item-line-total').innerText())).toBe(590));
    await check(page, 'ยอดสินค้า ฿590', summary(page).subtotal, async () => expect.soft(baht(await summary(page).subtotal.innerText())).toBe(590));
  });
});

test('TC-PROD-02 สต็อก 3 ชิ้น: จำนวนสูงสุด/ต่ำสุด', plan('TC-PROD-02', '@product'), async ({ page }) => {
  const qty = page.getByTestId('qty-input');
  await step('1. เปิด "สูตรลดก้อนขน"', async () => {
    await open(page, `/products/${P.hairball.slug}`);
    await check(page, 'ป้าย "เหลือ 3 ชิ้น"', page.getByTestId('stock-info'), () => expect.soft(page.getByTestId('stock-info')).toContainText('เหลือ 3 ชิ้น'));
  });
  await step('2. พิมพ์จำนวน 4', async () => {
    await qty.fill('4');
    await qty.blur();
    await check(page, 'พิมพ์ 4 → ไม่เกิน 3', qty, async () => expect.soft(Number(await qty.inputValue())).toBeLessThanOrEqual(3));
  });
  await step('3. พิมพ์จำนวน 0 และ −1', async () => {
    for (const v of ['0', '-1']) {
      await qty.fill(v);
      await qty.blur();
      await check(page, `พิมพ์ ${v} → ไม่ต่ำกว่า 1`, qty, async () => expect.soft(Number(await qty.inputValue())).toBeGreaterThanOrEqual(1));
    }
  });
  await step('4. กด + จนสุด (กด 5 ครั้ง)', async () => {
    await qty.fill('1');
    for (let i = 0; i < 5; i++) await page.getByTestId('qty-plus').click();
    await check(page, 'กด + เกิน → จำนวนสูงสุด = 3', qty, async () => expect.soft(Number(await qty.inputValue())).toBe(3));
  });
  await step('5. ใส่ตะกร้าที่ 3 ชิ้น แล้วเปิดตะกร้า', async () => {
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');
    await check(page, 'จำนวนในตะกร้า = 3', page.getByTestId('item-qty'), () => expect.soft(page.getByTestId('item-qty')).toHaveValue('3'));
    await check(page, 'ยอด ฿1,560 (520×3)', summary(page).subtotal, async () => expect.soft(baht(await summary(page).subtotal.innerText())).toBe(1560));
  });
});

test('TC-PROD-03 สินค้าหมด ไก่ฟรีซดราย', plan('TC-PROD-03', '@product'), async ({ page }) => {
  await step('1. เปิดหน้ารายละเอียด "ไก่ฟรีซดราย"', async () => {
    await open(page, `/products/${P.freezeDriedChicken.slug}`);
    await check(page, 'ป้าย "หมด"', page.getByTestId('stock-info'), () => expect.soft(page.getByTestId('stock-info')).toContainText('หมด'));
    await check(page, 'ปุ่มใส่ตะกร้ากดไม่ได้ (หน้ารายละเอียด)', page.getByTestId('add-to-cart'), () => expect.soft(page.getByTestId('add-to-cart')).toBeDisabled());
  });
  await step('2. เปิดแคตตาล็อกแมว ดูการ์ด "ไก่ฟรีซดราย"', async () => {
    await open(page, '/products?pet=cat');
    const card = page.locator(`[data-testid="product-card"][data-slug="${P.freezeDriedChicken.slug}"]`);
    await card.scrollIntoViewIfNeeded();
    await check(page, 'การ์ดมีป้าย "หมด"', card, () => expect.soft(card).toContainText('หมด'));
    await check(page, 'ปุ่มใส่ตะกร้าบนการ์ดกดไม่ได้', card.getByTestId('quick-add'), () => expect.soft(card.getByTestId('quick-add')).toBeDisabled());
    await check(page, '🛒 ยังเป็น 0', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('0'));
  });
});
