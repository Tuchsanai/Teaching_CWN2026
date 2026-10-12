import { test, expect, open } from './fixtures';

test.describe('หน้ารายละเอียดสินค้า', () => {
  test('TC-PRD-01 เลือกขนาดแล้วราคาเปลี่ยนตาม', {
    tag: ['@product', '@P1'],
    annotation: { type: 'expected', description: 'สุนัขโต สูตรแกะ: 3 kg = ฿790, 8 kg = ฿1,890' },
  }, async ({ page }) => {
    await open(page, '/products/adult-lamb-dry');
    await expect(page.getByTestId('product-title')).toContainText('สุนัขโต สูตรแกะ');
    await expect(page.getByTestId('product-price')).toHaveText('฿790');

    const big = page.locator('[data-testid="size-option"][data-size="8 kg"]');
    await big.click();
    await expect(big).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('product-price')).toHaveText('฿1,890');
  });

  test('TC-PRD-02 สินค้าหมด กดใส่ตะกร้าไม่ได้', {
    tag: ['@product', '@P1'],
    annotation: { type: 'expected', description: 'ปุ่มเป็น "สินค้าหมด" และกดไม่ได้ ตะกร้ายังเป็น 0' },
  }, async ({ page }) => {
    await open(page, '/products/freeze-dried-chicken-cat');
    const add = page.getByTestId('add-to-cart');
    await expect(add).toBeDisabled();
    await expect(add).toHaveText(/สินค้าหมด/);
    await expect(page.getByTestId('cart-count')).toHaveText('0');
  });

  test('TC-PRD-03 เพิ่มจำนวนได้ไม่เกินสต็อก', {
    tag: ['@product', '@P2'],
    annotation: { type: 'expected', description: 'สูตรลดก้อนขน มีสต็อก 3 กด + 5 ครั้ง จำนวนหยุดที่ 3' },
  }, async ({ page }) => {
    await open(page, '/products/hairball-control-dry');
    for (let i = 0; i < 5; i++) await page.getByTestId('qty-plus').click();
    await expect(page.getByTestId('qty-input')).toHaveValue('3');
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-count')).toHaveText('3');
  });

  test('TC-PRD-04 เปิดสินค้าที่ไม่มีอยู่ ได้หน้า 404', {
    tag: ['@product', '@P3'],
    annotation: { type: 'expected', description: 'แสดงหน้า not-found ที่สวย พร้อมลิงก์กลับหน้าแรก' },
  }, async ({ page }) => {
    const res = await page.goto('/products/this-does-not-exist');
    expect(res?.status()).toBe(404);
    await expect(page.getByTestId('not-found')).toBeVisible();
    await page.getByTestId('not-found').getByRole('link').first().click();
    await expect(page).toHaveURL(/\/$/);
  });
});
