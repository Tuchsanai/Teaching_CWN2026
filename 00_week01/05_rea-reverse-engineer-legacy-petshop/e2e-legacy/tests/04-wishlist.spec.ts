import { test, expect, open } from './fixtures';

test.describe('รายการโปรด (Wishlist)', () => {
  test('TC-WISH-01 กดหัวใจแล้วสินค้าอยู่ในรายการโปรด แม้รีโหลด', {
    tag: ['@wishlist', '@P2'],
    annotation: { type: 'expected', description: 'ตัวเลขที่หัวใจเป็น 2 และหน้า /wishlist มี 2 รายการ หลังรีโหลดยังอยู่' },
  }, async ({ page }) => {
    await open(page, '/products?pet=dog');
    await page.locator('[data-testid="product-card"][data-slug="duck-jerky-treat"]').getByTestId('wishlist-toggle').click();
    await page.locator('[data-testid="product-card"][data-slug="adult-lamb-dry"]').getByTestId('wishlist-toggle').click();
    await expect(page.getByTestId('wishlist-count')).toHaveText('2');

    await page.getByTestId('wishlist-link').click();
    await expect(page.getByTestId('wishlist-item')).toHaveCount(2);
    await page.reload();
    await expect(page.getByTestId('wishlist-item')).toHaveCount(2);
  });

  test('TC-WISH-02 ลบออกจากรายการโปรด ตัวเลขลดลงทันที', {
    tag: ['@wishlist', '@P2'],
    annotation: { type: 'expected', description: 'ลบ 1 จาก 2 รายการ ตัวเลขที่หัวใจเป็น 1 ทันที (ไม่ต้องรีโหลด)' },
  }, async ({ page }) => {
    await open(page, '/products/senior-salmon-dry');
    await page.getByTestId('wishlist-toggle').click();
    await open(page, '/products/salmon-skin-treat');
    await page.getByTestId('wishlist-toggle').click();
    await expect(page.getByTestId('wishlist-count')).toHaveText('2');

    await page.getByTestId('wishlist-link').click();
    await page.locator('[data-testid="wishlist-item"][data-slug="senior-salmon-dry"]').getByTestId('wishlist-remove').click();
    await expect(page.getByTestId('wishlist-item')).toHaveCount(1);
    await expect(page.getByTestId('wishlist-count')).toHaveText('1');
  });

  test('TC-WISH-03 ย้ายจากรายการโปรดไปตะกร้า', {
    tag: ['@wishlist', '@P2'],
    annotation: { type: 'expected', description: 'สินค้าหายจากรายการโปรด และตะกร้าเพิ่มเป็น 1' },
  }, async ({ page }) => {
    await open(page, '/products/duck-grainfree-dry');
    await page.getByTestId('wishlist-toggle').click();
    await page.getByTestId('wishlist-link').click();
    await page.getByTestId('move-to-cart').click();

    await expect(page.getByTestId('empty-wishlist')).toBeVisible();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
    await page.getByTestId('cart-link').click();
    await expect(page.locator('[data-testid="cart-item"][data-slug="duck-grainfree-dry"]')).toBeVisible();
  });
});
