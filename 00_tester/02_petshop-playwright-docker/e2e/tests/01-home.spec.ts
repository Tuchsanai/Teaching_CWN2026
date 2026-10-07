import { test, expect, open } from './fixtures';

test.describe('หน้าแรก', () => {
  test('TC-HOME-01 หน้าแรกแสดง Hero หมวดหมู่ และสินค้ายอดนิยม', {
    tag: ['@home', '@P2'],
    annotation: { type: 'expected', description: 'เห็น Hero, การ์ดหมวดแมว/หมา, สินค้ายอดนิยม 8 รายการ และโค้ด PAW10' },
  }, async ({ page }) => {
    await open(page, '/');
    await expect(page).toHaveTitle(/PawPantry/);
    await expect(page.getByTestId('hero')).toBeVisible();
    await expect(page.getByTestId('category-cat')).toBeVisible();
    await expect(page.getByTestId('category-dog')).toBeVisible();

    const popular = page.getByTestId('popular-products');
    await popular.scrollIntoViewIfNeeded();
    await expect(popular.getByTestId('product-card')).toHaveCount(8);
    await expect(page.getByTestId('promo-banner')).toContainText('PAW10');
  });

  test('TC-HOME-02 กดปุ่ม "ช้อปอาหารแมว" แล้วไปหน้าสินค้าแมว', {
    tag: ['@home', '@P2'],
    annotation: { type: 'expected', description: 'URL มี pet=cat และทุกการ์ดเป็นสินค้าแมว (14 รายการ)' },
  }, async ({ page }) => {
    await open(page, '/');
    await page.getByTestId('hero-cta-cat').click();
    await expect(page).toHaveURL(/pet=cat/);
    await expect(page.getByTestId('result-count')).toHaveText('พบ 14 รายการ');
  });
});
