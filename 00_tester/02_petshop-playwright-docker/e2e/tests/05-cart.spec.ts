import { test, expect, open, baht } from './fixtures';

test.describe('ตะกร้าสินค้า', () => {
  test('TC-CART-01 เพิ่มสินค้า 2 ชิ้น ยอดรวมถูกต้อง', {
    tag: ['@cart', '@P1'],
    annotation: { type: 'expected', description: '฿189 × 2 = ฿378 + ค่าส่ง ฿50 = ฿428 และตัวเลขตะกร้าเป็น 2' },
  }, async ({ page }) => {
    await open(page, '/products/kitten-salmon-dry');
    await page.getByTestId('qty-plus').click();
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('toast')).toBeVisible();
    await expect(page.getByTestId('cart-count')).toHaveText('2');

    await page.getByTestId('cart-link').click();
    await expect(page.getByTestId('item-line-total')).toHaveText('฿378');
    await expect(page.getByTestId('summary-subtotal')).toHaveText('฿378');
    await expect(page.getByTestId('summary-shipping')).toHaveText('฿50');
    await expect(page.getByTestId('summary-total')).toHaveText('฿428');
  });

  test('TC-CART-02 เพิ่ม ลด และลบสินค้าในตะกร้า', {
    tag: ['@cart', '@P1'],
    annotation: { type: 'expected', description: 'กด + แล้วยอดเพิ่ม, กด − แล้วยอดลด, ลบรายการสุดท้ายแล้วเห็นตะกร้าว่าง' },
  }, async ({ page }) => {
    await open(page, '/products/beef-stew-can');
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');

    const row = page.locator('[data-testid="cart-item"][data-slug="beef-stew-can"]');
    await row.getByTestId('item-plus').click();
    await row.getByTestId('item-plus').click();
    await expect(row.getByTestId('item-qty')).toHaveValue('3');
    await expect(page.getByTestId('summary-subtotal')).toHaveText('฿237');

    await row.getByTestId('item-minus').click();
    await expect(page.getByTestId('summary-subtotal')).toHaveText('฿158');
    await expect(page.getByTestId('cart-count')).toHaveText('2');

    await row.getByTestId('item-remove').click();
    await expect(page.getByTestId('empty-cart')).toBeVisible();
    await expect(page.getByTestId('cart-count')).toHaveText('0');
  });

  test('TC-CART-03 ซื้อครบ ฿999 ได้ส่งฟรี', {
    tag: ['@cart', '@P2'],
    annotation: { type: 'expected', description: 'ยอด ฿790 ยังเสียค่าส่ง; เปลี่ยนเป็น 8 kg (฿1,890) ได้ส่งฟรี' },
  }, async ({ page }) => {
    await open(page, '/products/adult-lamb-dry');
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');
    await expect(page.getByTestId('free-shipping-progress')).toContainText('ซื้อเพิ่มอีก ฿209 เพื่อส่งฟรี');
    await expect(page.getByTestId('summary-shipping')).toHaveText('฿50');

    await open(page, '/products/adult-lamb-dry');
    await page.locator('[data-testid="size-option"][data-size="8 kg"]').click();
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');
    await expect(page.getByTestId('free-shipping-progress')).toContainText('ได้ส่งฟรีแล้ว!');
    await expect(page.getByTestId('summary-shipping')).toHaveText('ฟรี');
    expect(baht(await page.getByTestId('summary-total').textContent())).toBe(790 + 1890);
  });

  test('TC-CART-04 ตะกร้ายังอยู่หลังรีโหลด และมีสินค้าแนะนำ', {
    tag: ['@cart', '@P2'],
    annotation: { type: 'expected', description: 'รีโหลดแล้วสินค้ายังอยู่ และแถบ "ซื้อคู่กัน" แนะนำสินค้าที่เกี่ยวข้อง' },
  }, async ({ page }) => {
    await open(page, '/products/puppy-chicken-dry');
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');
    await page.reload();
    await expect(page.locator('[data-testid="cart-item"][data-slug="puppy-chicken-dry"]')).toBeVisible();
    await expect(page.getByTestId('cart-recommendations').locator('[data-slug="puppy-lamb-wet"]').first()).toBeVisible();
  });
});
