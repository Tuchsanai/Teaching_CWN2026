import { test, expect, step, check, open, plan, login, logout, register, toCheckout, placeOrder, baht, ADDRESS, P, type Page } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.6 ความปลอดภัย (TC-SEC-01 … 03)

test('TC-SEC-01 ผู้ใช้อื่นเปิดคำสั่งซื้อของ demo ไม่ได้', plan('TC-SEC-01', '@security'), async ({ page }) => {
  let orderUrl = '';
  await step('1. demo สั่งซื้อ 1 ครั้ง (ลูกแมว 400 g ×1)', async () => {
    await toCheckout(page, [[P.kitten400, 1]]);
    await placeOrder(page);
    orderUrl = new URL(page.url()).pathname;
  });
  await step('2. ออกจากระบบ แล้วสมัครผู้ใช้ใหม่ other@pawpantry.test', async () => {
    await logout(page);
    await register(page, 'ผู้ใช้ อื่น', 'other@pawpantry.test', 'Abcd1234');
    await page.waitForURL(/\/account/);
  });
  await step('3. ผู้ใช้ใหม่เปิด URL คำสั่งซื้อของ demo', async () => {
    const res = await page.goto(orderUrl);
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    const main = page.locator('main');
    await check(page, `${orderUrl}: ไม่เห็นข้อมูลคำสั่งซื้อ (หน้า 404 / ไม่พบ)`, main, async () => {
      expect.soft(res?.status(), 'HTTP status').toBe(404);
      await expect.soft(page.getByTestId('order-success')).toHaveCount(0);
    });
    await check(page, 'ไม่เห็นชื่อ เบอร์ ที่อยู่ของ demo', main, async () => {
      await expect.soft(main).not.toContainText(ADDRESS.name);
      await expect.soft(main).not.toContainText(ADDRESS.phone);
      await expect.soft(main).not.toContainText(ADDRESS.address);
    });
  });
  await step('4. เปิด /account ของผู้ใช้ใหม่', async () => {
    await open(page, '/account');
    await check(page, '/account ของผู้ใช้ใหม่มี 0 คำสั่งซื้อ', page.getByTestId('profile-card'), () => expect.soft(page.getByTestId('order-row')).toHaveCount(0));
  });
});

test('TC-SEC-02 ฝังสคริปต์ในช่องค้นหาและชื่อผู้ใช้', plan('TC-SEC-02', '@security'), async ({ page }) => {
  const dialogs: string[] = [];
  page.on('dialog', (d) => { dialogs.push(d.message()); d.dismiss().catch(() => {}); });
  const SCRIPT = '<script>alert(1)</script>';
  const IMG = '<img src=x onerror=alert(1)>';
  await step(`1. ค้นหา ${SCRIPT}`, async () => {
    await open(page, '/');
    await page.getByTestId('search-input').fill(SCRIPT);
    await page.getByTestId('search-submit').click();
    await page.waitForURL(/\/products\?q=/);
    await page.waitForTimeout(1000);
    await check(page, 'ไม่มีกล่อง alert เด้ง (ค้นหา)', null, () => expect.soft(dialogs.join(', ') || 'ไม่มี').toBe('ไม่มี'));
    await check(page, 'ข้อความแสดงเป็นตัวอักษรธรรมดา (ช่องค้นหายังเป็นข้อความเดิม)', page.getByTestId('search-input'),
      () => expect.soft(page.getByTestId('search-input')).toHaveValue(SCRIPT));
  });
  await step(`2. สมัครด้วยชื่อ ${IMG}`, async () => {
    await register(page, IMG, 'xss@pawpantry.test', 'Abcd1234');
    await page.waitForURL(/\/account/).catch(() => {});
    await page.waitForTimeout(1000);
    await check(page, 'ไม่มีกล่อง alert เด้ง (ชื่อผู้ใช้)', null, () => expect.soft(dialogs.join(', ') || 'ไม่มี').toBe('ไม่มี'));
    await check(page, 'ชื่อแสดงเป็นตัวอักษรธรรมดา ไม่กลายเป็นรูป', page.getByTestId('user-menu'), async () => {
      await expect.soft(page.getByTestId('user-menu')).toContainText(IMG);
      await expect.soft(page.locator('img[src="x"]')).toHaveCount(0);
    });
  });
});

async function setCart(page: Page, cart: object[]) {
  await page.evaluate((c) => localStorage.setItem('pp-cart', JSON.stringify(c)), cart);
}

test('TC-SEC-03 แก้ตะกร้าใน localStorage (ราคา / สินค้าหมด)', plan('TC-SEC-03', '@security'), async ({ page }) => {
  await step('1. login demo', async () => login(page));
  await step('2. ① แก้ pp-cart: ลูกแมว 400 g ใส่ price: 1 แล้วเปิดตะกร้า', async () => {
    await setCart(page, [{ slug: P.kitten400.slug, size: P.kitten400.size, qty: 1, price: 1 }]);
    await open(page, '/cart');
    await check(page, 'ยอดสินค้าในตะกร้าคิด ฿189 (ราคาจริง) ไม่ใช่ ฿1', page.getByTestId('summary-subtotal'),
      async () => expect.soft(baht(await page.getByTestId('summary-subtotal').innerText())).toBe(189));
  });
  await step('3. ① เปิดหน้าชำระเงิน', async () => {
    await open(page, '/checkout');
    await check(page, 'ปุ่มยืนยันคิด ฿239 (189+50)', page.getByTestId('place-order'), () => expect.soft(page.getByTestId('place-order')).toHaveText(/ยืนยันสั่งซื้อ ฿239/));
    await check(page, 'ยอดชำระ ฿239', page.getByTestId('summary-total'), async () => expect.soft(baht(await page.getByTestId('summary-total').innerText())).toBe(239));
  });
  await step('4. ② แก้ pp-cart: ไก่ฟรีซดราย (หมด) 1 ชิ้น แล้วกดสั่งซื้อ', async () => {
    await setCart(page, [{ slug: P.freezeDriedChicken.slug, size: '50 g', qty: 1 }]);
    await open(page, '/checkout');
    await page.getByTestId('ship-phone').fill(ADDRESS.phone);
    await page.getByTestId('ship-postcode').fill(ADDRESS.postcode);
    await page.getByTestId('ship-address').fill(ADDRESS.address);
    await page.getByTestId('place-order').click();
    await page.waitForTimeout(1500);
    await check(page, 'ยังอยู่ /checkout ไม่สร้างคำสั่งซื้อ', page.getByTestId('place-order'), () => expect.soft(page).toHaveURL(/\/checkout$/));
    const msg = page.getByText(/ไม่พอ/).first();
    await check(page, 'มีข้อความที่มีชื่อ "ไก่ฟรีซดราย" และบอกว่าสินค้าไม่พอ', msg, () => expect.soft(msg).toContainText('ไก่ฟรีซดราย'),
      { near: page.getByTestId('place-order') });
  });
  await step('5. เปิด /account และหน้าสินค้าไก่ฟรีซดราย', async () => {
    await open(page, '/account');
    await check(page, '/account มี 0 คำสั่งซื้อ', page.getByTestId('profile-card'), () => expect.soft(page.getByTestId('order-row')).toHaveCount(0));
    await open(page, `/products/${P.freezeDriedChicken.slug}`);
    await check(page, 'หน้าสินค้ายังเป็น "หมด"', page.getByTestId('stock-info'), () => expect.soft(page.getByTestId('stock-info')).toContainText('หมด'));
  });
});
