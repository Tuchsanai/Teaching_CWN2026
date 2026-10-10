import { test, expect, step, check, open, plan, addToCart, fillAddress, placeOrder, baht, DEMO, P } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.6 จอมือถือ · 404 (TC-UI-01, TC-UI-02)

test.describe('จอมือถือ 390×844', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test('TC-UI-01 จอมือถือ: เมนูลิ้นชัก และสั่งซื้อจนจบ', plan('TC-UI-01', '@mobile'), async ({ page }) => {
    const menu = page.getByTestId('mobile-menu');
    await step('1. เปิดหน้าแรกบนจอ 390×844', async () => {
      await open(page, '/');
      const width = await page.evaluate(() => document.documentElement.scrollWidth);
      await check(page, `ไม่มีแถบเลื่อนแนวนอน (ความกว้างหน้า ${width} ≤ 390)`, null, () => expect.soft(width).toBeLessThanOrEqual(390));
    });
    await step('2. กด ☰ เปิดเมนู', async () => {
      await page.getByTestId('menu-toggle').click();
      await check(page, 'เมนูลิ้นชักเปิดได้', menu, () => expect.soft(menu).toBeVisible());
      for (const [label, href] of [['สินค้า', '/products'], ['รายการโปรด', '/wishlist'], ['ตะกร้า', '/cart'], ['เข้าสู่ระบบ', '/login']]) {
        const link = menu.locator(`a[href^="${href}"]`);
        await check(page, `มีลิงก์ไป${label} (${href})`, menu, () => expect.soft(link.first()).toBeVisible());
      }
    });
    await step('3. กด "เข้าสู่ระบบ" ในเมนู แล้ว login demo', async () => {
      await menu.locator('a[href^="/login"]').first().click();
      await page.waitForURL(/\/login/);
      await page.getByTestId('login-email').fill(DEMO.email);
      await page.getByTestId('login-password').fill(DEMO.password);
      await page.getByTestId('login-submit').click();
      await page.waitForURL((u) => !u.pathname.startsWith('/login'));
    });
    await step('4. ใส่ลูกแมว 400 g ×1 แล้วชำระเงินด้วยที่อยู่มาตรฐาน', async () => {
      await addToCart(page, P.kitten400);
      await open(page, '/cart');
      await page.getByTestId('checkout-button').click();
      await page.waitForURL(/\/checkout/);
      await fillAddress(page);
      await placeOrder(page);
      await check(page, 'สั่งซื้อสำเร็จยอด ฿239 (189+50)', page.getByTestId('summary-total'),
        async () => expect.soft(baht(await page.getByTestId('summary-total').innerText())).toBe(239));
    });
  });
});

test('TC-UI-02 หน้า 404', plan('TC-UI-02', '@404'), async ({ page }) => {
  for (const [n, url] of [['1', '/no-such-page'], ['2', '/products/no-such']] as const) {
    await step(`${n}. เปิด ${url}`, async () => {
      const res = await page.goto(url);
      await check(page, `${url}: HTTP status 404`, null, () => expect.soft(res?.status()).toBe(404));
      await check(page, `${url}: มีข้อความว่าไม่พบหน้า`, page.getByTestId('not-found'), () => expect.soft(page.getByTestId('not-found')).toContainText('ไม่พบหน้า'));
    });
  }
  await step('3. กด "กลับหน้าแรก"', async () => {
    await page.getByTestId('not-found-home').click();
    await page.waitForURL((u) => u.pathname === '/').catch(() => {});
    await check(page, 'ไปที่ /', null, () => expect.soft(new URL(page.url()).pathname).toBe('/'));
  });
});
