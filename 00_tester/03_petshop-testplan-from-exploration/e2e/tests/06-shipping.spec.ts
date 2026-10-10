import { test, expect, step, check, open, plan, addToCart, checkSummary, toCheckout, placeOrder, baht, P } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.4 ค่าส่ง (TC-SHIP-01 … 04) · [D] ปกติ ฿50 ฟรีเมื่อครบ ฿999 · ด่วน ฿120

const bar = (page: import('@playwright/test').Page) => page.getByTestId('free-shipping-progress');

test('TC-SHIP-01 ยอด ฿998 ส่งธรรมดา', plan('TC-SHIP-01', '@shipping'), async ({ page }) => {
  await step('1. ใส่ลูกบอลมีเสียง ×1 + แมวโต สูตรไก่ 3 kg ×1 (199+799 = 998) แล้วเปิดตะกร้า', async () => {
    await addToCart(page, P.squeakyBall);
    await addToCart(page, P.adultChicken3kg);
    await open(page, '/cart');
  });
  await step('2. ตรวจค่าส่ง (998 < 999 → ฿50 · 998+50 = 1,048)', async () => {
    await checkSummary(page, '', { subtotal: 998, shipping: 50, total: 1048 });
    await check(page, 'แถบ "ซื้อเพิ่มอีก ฿1 เพื่อส่งฟรี" (999−998)', bar(page), () => expect.soft(bar(page)).toHaveText(/ซื้อเพิ่มอีก ฿1 เพื่อส่งฟรี/));
  });
});

test('TC-SHIP-02 ยอด ฿999 พอดี ส่งธรรมดา', plan('TC-SHIP-02', '@shipping'), async ({ page }) => {
  await step('1. ใส่ไม้ตกแมว ×1 + ชามกินช้า ×3 (129+290×3 = 999) แล้วเปิดตะกร้า', async () => {
    await addToCart(page, P.featherWand);
    await addToCart(page, P.slowBowl, 3);
    await open(page, '/cart');
  });
  await step('2. ตรวจค่าส่ง ("ครบ ฿999" = ≥ 999 → ฟรี · ยอด 999)', async () => {
    await checkSummary(page, '', { subtotal: 999, shipping: 0, total: 999 });
    await check(page, 'แถบบอกว่าได้ส่งฟรีแล้ว', bar(page), async () => {
      await expect.soft(bar(page)).toHaveText(/ส่งฟรี/);
      await expect.soft(bar(page)).not.toHaveText(/ซื้อเพิ่มอีก/);
    });
  });
});

test('TC-SHIP-03 ส่งด่วน ยอด ฿189 และ ฿999', plan('TC-SHIP-03', '@shipping'), async ({ page }) => {
  await step('1. login · ลูกแมว 400 g ×1 (฿189) · หน้าชำระเงิน เลือก "ส่งด่วน"', async () => {
    await toCheckout(page, [[P.kitten400, 1]]);
    await page.getByTestId('shipping-express').check();
    await checkSummary(page, '฿189 ด่วน:', { shipping: 120, total: 309 });
  });
  await step('2. เปลี่ยนตะกร้าเป็น ไม้ตกแมว ×1 + ชามกินช้า ×3 (฿999)', async () => {
    await open(page, '/cart');
    await page.getByTestId('item-remove').click();
    await addToCart(page, P.featherWand);
    await addToCart(page, P.slowBowl, 3);
  });
  await step('3. หน้าชำระเงิน เลือก "ส่งด่วน" (สมมติฐาน Q3: ด่วน ฿120 เสมอ · 999+120 = 1,119)', async () => {
    await open(page, '/checkout');
    await page.getByTestId('shipping-express').check();
    await checkSummary(page, '฿999 ด่วน:', { subtotal: 999, shipping: 120, total: 1119 });
  });
});

test('TC-SHIP-04 เลือกส่งด่วนแล้วเปลี่ยนกลับส่งธรรมดา', plan('TC-SHIP-04', '@shipping'), async ({ page }) => {
  const btn = page.getByTestId('place-order');
  await step('1. login · ลูกแมว 400 g ×1 (฿189) · หน้าชำระเงิน กรอกที่อยู่มาตรฐาน', async () => {
    await toCheckout(page, [[P.kitten400, 1]]);
  });
  await step('2. เลือก "ส่งด่วน" (189+120 = 309)', async () => {
    await page.getByTestId('shipping-express').check();
    await check(page, 'ค่าส่ง ฿120', page.getByTestId('summary-shipping'), () => expect.soft(page.getByTestId('summary-shipping')).toHaveText('฿120'));
    await check(page, 'ปุ่ม "ยืนยันสั่งซื้อ ฿309"', btn, () => expect.soft(btn).toHaveText(/ยืนยันสั่งซื้อ ฿309/));
  });
  await step('3. เปลี่ยนกลับ "ส่งธรรมดา" (189+50 = 239)', async () => {
    await page.getByTestId('shipping-standard').check();
    await check(page, 'ค่าส่ง ฿50', page.getByTestId('summary-shipping'), () => expect.soft(page.getByTestId('summary-shipping')).toHaveText('฿50'));
    await check(page, 'ปุ่ม "ยืนยันสั่งซื้อ ฿239"', btn, () => expect.soft(btn).toHaveText(/ยืนยันสั่งซื้อ ฿239/));
  });
  await step('4. กดยืนยันสั่งซื้อ', async () => {
    await placeOrder(page);
    await check(page, 'หน้าคำสั่งซื้อยอด ฿239', page.getByTestId('summary-total'),
      async () => expect.soft(baht(await page.getByTestId('summary-total').innerText())).toBe(239));
    await check(page, 'หน้าคำสั่งซื้อระบุส่งธรรมดา', page.locator('main'), () => expect.soft(page.locator('main')).toContainText('ธรรมดา'));
  });
});
