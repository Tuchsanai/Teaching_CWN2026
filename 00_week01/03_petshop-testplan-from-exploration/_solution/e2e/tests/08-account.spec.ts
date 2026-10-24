import { test, expect, step, check, open, plan, addToCart, fillAddress, login, placeOrder, baht, P } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.5 ประวัติการสั่งซื้อ (TC-ACC-01) — สั่งซื้อเอง 2 ครั้งในข้อนี้ ไม่พึ่งผลของข้ออื่น

test('TC-ACC-01 ประวัติการสั่งซื้อ 2 คำสั่งซื้อ ยอดสะสม', plan('TC-ACC-01', '@account'), async ({ page }) => {
  const orders: { id: string; total: number }[] = [];
  await step('1. login demo', async () => login(page));
  await step('2. สั่งซื้อครั้งที่ 1: ลูกแมว 400 g ×2 ส่งธรรมดา COD (189×2+50 = 428)', async () => {
    await addToCart(page, P.kitten400, 2);
    await open(page, '/checkout');
    await fillAddress(page);
    await page.getByTestId('shipping-standard').check();
    await page.getByTestId('pay-cod').check();
    await placeOrder(page);
    orders.push({ id: await page.getByTestId('order-id').innerText(), total: baht(await page.getByTestId('summary-total').innerText()) });
  });
  await step('3. สั่งซื้อครั้งที่ 2: ลูกแมว 1.5 kg ×1 ส่งด่วน PromptPay (590+120 = 710)', async () => {
    await addToCart(page, P.kitten15, 1);
    await open(page, '/checkout');
    await fillAddress(page);
    await page.getByTestId('shipping-express').check();
    await page.getByTestId('pay-promptpay').check();
    await placeOrder(page);
    orders.push({ id: await page.getByTestId('order-id').innerText(), total: baht(await page.getByTestId('summary-total').innerText()) });
  });
  await step('4. เปิด /account', async () => {
    await open(page, '/account');
    const card = page.getByTestId('profile-card');
    const text = await card.innerText();
    const count = Number(text.match(/คำสั่งซื้อ\s*\n\s*(\d+)/)?.[1] ?? -1);
    const spent = baht(text.match(/ยอดซื้อสะสม\s*\n\s*(฿[\d,]+)/)?.[1] ?? '');
    await check(page, 'แสดง 2 คำสั่งซื้อ (ตัวเลข)', card, () => expect.soft(count).toBe(2));
    await check(page, 'แสดง 2 คำสั่งซื้อ (แถวในประวัติ)', page.getByTestId('order-history'), () => expect.soft(page.getByTestId('order-row')).toHaveCount(2));
    await check(page, 'ยอดซื้อสะสม ฿1,138 (428+710)', card, () => expect.soft(spent).toBe(1138));
  });
  for (const [i, want] of [[0, 428], [1, 710]] as const) {
    await step(`${5 + i}. กดคำสั่งซื้อที่ ${i + 1} ในประวัติ`, async () => {
      await open(page, '/account');
      const id = orders[i]?.id ?? '';
      await page.locator(`[data-testid="order-row"][data-order-id="${id}"]`).click();
      await page.waitForURL(/\/orders\//);
      await check(page, `${id}: ยอดตรงกับตอนสั่ง ฿${want}`, page.getByTestId('summary-total'),
        async () => expect.soft(baht(await page.getByTestId('summary-total').innerText())).toBe(want));
    });
  }
});
