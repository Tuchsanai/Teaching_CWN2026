import { test, expect, open, registerByApi, loginByUi, baht } from './fixtures';

test.describe('สั่งซื้อและชำระเงิน', () => {
  test('TC-CHK-01 ยังไม่เข้าสู่ระบบ กดสั่งซื้อต้องไปหน้าเข้าสู่ระบบก่อน', {
    tag: ['@checkout', '@P1'],
    annotation: { type: 'expected', description: 'ถูกพาไปหน้า login แล้วเข้าสู่ระบบเสร็จกลับมาหน้า checkout พร้อมชื่อผู้รับ' },
  }, async ({ page, request }) => {
    const user = await registerByApi(request); // separate API context: the browser stays logged out
    await open(page, '/products/tuna-pouch');
    await page.getByTestId('add-to-cart').click();
    await open(page, '/cart');
    await page.getByTestId('checkout-button').click();

    await expect(page).toHaveURL(/\/login\?next=/);
    await loginByUi(page, user.email, user.password);
    await expect(page).toHaveURL(/\/checkout$/);
    await expect(page.getByTestId('ship-name')).toHaveValue(user.name);
  });

  test('TC-CHK-02 ตรวจฟอร์มที่อยู่จัดส่ง', {
    tag: ['@checkout', '@P1'],
    annotation: { type: 'expected', description: 'เบอร์ 9 หลัก, ที่อยู่สั้นเกิน, รหัสไปรษณีย์ 4 หลัก → ขึ้น error และยังไม่สร้างคำสั่งซื้อ' },
  }, async ({ page }) => {
    await registerByApi(page.request);
    await open(page, '/products/tuna-pouch');
    await page.getByTestId('add-to-cart').click();
    await open(page, '/checkout');

    await page.getByTestId('ship-phone').fill('081234567');
    await page.getByTestId('ship-address').fill('สั้นไป');
    await page.getByTestId('ship-postcode').fill('1050');
    await page.getByTestId('place-order').click();

    await expect(page.getByTestId('error-ship-phone')).toHaveText('เบอร์โทรต้องเป็นตัวเลข 10 หลัก ขึ้นต้นด้วย 0');
    await expect(page.getByTestId('error-ship-address')).toHaveText('กรุณากรอกที่อยู่ (อย่างน้อย 10 ตัวอักษร)');
    await expect(page.getByTestId('error-ship-postcode')).toHaveText('รหัสไปรษณีย์ต้องเป็นตัวเลข 5 หลัก');
    await expect(page).toHaveURL(/\/checkout$/);
  });

  test('TC-CHK-03 ลูกค้าซื้อของจนจบ (End-to-End)', {
    tag: ['@checkout', '@e2e', '@P1'],
    annotation: { type: 'expected', description: 'เลือกสินค้า → ใส่ตะกร้า → คูปอง FREESHIP → เข้าสู่ระบบ → กรอกที่อยู่ → สั่งซื้อ → เห็นเลขคำสั่งซื้อ และอยู่ในประวัติ' },
  }, async ({ page, request }) => {
    const user = await registerByApi(request);

    // 1) shop like a customer
    await open(page, '/');
    await page.getByTestId('category-dog').click();
    await page.locator('[data-testid="product-card"][data-slug="duck-jerky-treat"]').getByTestId('product-name').click();
    await expect(page.getByTestId('product-title')).toContainText('เป็ดอบแห้ง');
    await page.getByTestId('qty-plus').click();
    await page.getByTestId('add-to-cart').click();
    await expect(page.getByTestId('cart-count')).toHaveText('2');

    // 2) cart + coupon
    await page.getByTestId('cart-link').click();
    await page.getByTestId('coupon-input').fill('FREESHIP');
    await page.getByTestId('coupon-apply').click();
    await expect(page.getByTestId('summary-shipping')).toHaveText('ฟรี');
    await expect(page.getByTestId('summary-total')).toHaveText('฿378');
    await page.getByTestId('checkout-button').click();

    // 3) log in, then fill the address
    await loginByUi(page, user.email, user.password);
    await expect(page).toHaveURL(/\/checkout$/);
    await page.getByTestId('ship-phone').fill('0812345678');
    await page.getByTestId('ship-address').fill('99/9 ถนนสุขุมวิท แขวงคลองเตย');
    await page.getByTestId('ship-province').selectOption('กรุงเทพมหานคร');
    await page.getByTestId('ship-postcode').fill('10110');
    await page.getByTestId('pay-promptpay').check();
    await expect(page.getByTestId('promptpay-qr')).toBeVisible();
    await page.getByTestId('place-order').click();

    // 4) confirmation
    await expect(page.getByTestId('order-success')).toContainText('สั่งซื้อสำเร็จ!');
    const orderId = (await page.getByTestId('order-id').textContent())!.trim();
    expect(orderId).toMatch(/^PP-\d{6}$/);
    await expect(page.getByTestId('order-item')).toHaveCount(1);
    await expect(page.getByTestId('summary-total')).toHaveText('฿378');
    await expect(page.getByTestId('cart-count')).toHaveText('0');

    // 5) order history
    await open(page, '/account');
    await expect(page.locator(`[data-testid="order-row"][data-order-id="${orderId}"]`)).toBeVisible();
  });

  test('TC-CHK-04 สั่งซื้อแล้วสต็อกลดลง', {
    tag: ['@checkout', '@api', '@P2'],
    annotation: { type: 'expected', description: 'สต็อกหลังสั่งซื้อ = สต็อกก่อนสั่ง − 2' },
  }, async ({ page }, testInfo) => {
    // each browser buys a different product so parallel runs never share stock
    const slug = ({ chromium: 'senior-tuna-dry', firefox: 'urinary-care-dry', webkit: 'large-breed-beef-dry' } as Record<string, string>)[testInfo.project.name] ?? 'senior-tuna-dry';
    const stockOf = async () => (await (await page.request.get(`/api/products/${slug}`)).json()).stock as number;

    await registerByApi(page.request);
    const before = await stockOf();
    await open(page, `/products/${slug}`);
    await page.getByTestId('qty-plus').click();
    await page.getByTestId('add-to-cart').click();
    await open(page, '/checkout');
    await page.getByTestId('ship-phone').fill('0899999999');
    await page.getByTestId('ship-address').fill('1 หมู่ 2 ตำบลสุเทพ อำเภอเมือง');
    await page.getByTestId('ship-province').selectOption('เชียงใหม่');
    await page.getByTestId('ship-postcode').fill('50200');
    await page.getByTestId('place-order').click();
    await expect(page.getByTestId('order-success')).toBeVisible();

    expect(await stockOf()).toBe(before - 2);
    expect(baht(await page.getByTestId('summary-total').textContent())).toBeGreaterThan(0);
  });
});
