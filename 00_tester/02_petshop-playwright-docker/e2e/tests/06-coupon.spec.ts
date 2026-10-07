import { test, expect, open } from './fixtures';

test.describe('คูปองส่วนลด', () => {
  test('TC-CPN-01 ใช้คูปอง PAW10 ลด 10%', {
    tag: ['@coupon', '@P1'],
    annotation: { type: 'expected', description: 'แมวโต สูตรไก่ 3 kg ฿799 ลด ฿79 → ยอดสุทธิ ฿770 (รวมค่าส่ง ฿50)' },
  }, async ({ page }) => {
    await open(page, '/products/adult-chicken-dry');
    await page.locator('[data-testid="size-option"][data-size="3 kg"]').click();
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');

    await page.getByTestId('coupon-input').fill('paw10');
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('coupon-message')).toHaveText('ใช้คูปอง PAW10 แล้ว');
    await expect(page.getByTestId('summary-discount')).toContainText('฿79');
    await expect(page.getByTestId('summary-total')).toHaveText('฿770');
  });

  test('TC-CPN-02 คูปองไม่ถูกต้อง และคูปองหมดอายุ', {
    tag: ['@coupon', '@P2'],
    annotation: { type: 'expected', description: 'XYZ → "ไม่พบคูปองนี้", SUMMER20 → "คูปองนี้หมดอายุแล้ว" ยอดไม่เปลี่ยน' },
  }, async ({ page }) => {
    await open(page, '/products/tuna-pouch');
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');

    await page.getByTestId('coupon-input').fill('XYZ');
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('coupon-message')).toHaveText('ไม่พบคูปองนี้');

    await page.getByTestId('coupon-input').fill('SUMMER20');
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('coupon-message')).toHaveText('คูปองนี้หมดอายุแล้ว');
    await expect(page.getByTestId('summary-total')).toHaveText('฿85');
  });

  test('TC-CPN-03 NEWCAT50 ต้องซื้ออาหารแมวขั้นต่ำ ฿500', {
    tag: ['@coupon', '@P2'],
    annotation: { type: 'expected', description: 'มีแต่อาหารหมา → ใช้ไม่ได้; เพิ่มอาหารแมว ฿590 → ลด ฿50' },
  }, async ({ page }) => {
    await open(page, '/products/dental-chew-treat');
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');
    await page.getByTestId('coupon-input').fill('NEWCAT50');
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('coupon-message')).toHaveText('ต้องซื้ออาหารแมวขั้นต่ำ ฿500');

    await open(page, '/products/kitten-salmon-dry');
    await page.locator('[data-testid="size-option"][data-size="1.5 kg"]').click();
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');
    await page.getByTestId('coupon-input').fill('NEWCAT50');
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('summary-discount')).toContainText('฿50');
    // 149 + 590 = 739 − 50 + 50 shipping = 739
    await expect(page.getByTestId('summary-total')).toHaveText('฿739');
  });
});
