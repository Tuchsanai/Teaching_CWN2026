import { test, expect, step, check, open, plan, addToCart, applyCoupon, checkSummary, P, type Page } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.4 คูปอง (TC-COUP-01 … 10) · ตัวเลขเงินคำนวณจาก [D] + คณิตศาสตร์ (วงเล็บในชื่อจุดตรวจ)

type Line = [{ slug: string; size?: string }, number];

async function cartWith(page: Page, lines: Line[]) {
  for (const [item, qty] of lines) await addToCart(page, item, qty);
  await open(page, '/cart');
}

const message = (page: Page) => page.getByTestId('coupon-message');

test('TC-COUP-01 PAW10 กับลูกแมว 1.5 kg ฿590', plan('TC-COUP-01', '@coupon'), async ({ page }) => {
  await step('1. ใส่ลูกแมว 1.5 kg ×1 แล้วเปิดตะกร้า', async () => cartWith(page, [[P.kitten15, 1]]));
  await step('2. ใช้คูปอง PAW10 (590×10% = 59 · 590 < 999 ส่ง 50 · 590−59+50 = 581)', async () => {
    await applyCoupon(page, 'PAW10');
    await checkSummary(page, '', { subtotal: 590, discount: 59, shipping: 50, total: 581 });
    await check(page, 'ข้อความยืนยันว่าใช้คูปอง PAW10 แล้ว', message(page), () => expect.soft(message(page)).toHaveText(/ใช้คูปอง PAW10 แล้ว/));
  });
});

test('TC-COUP-02 PAW10 กับสุนัขพันธุ์ใหญ่ ฿1,590', plan('TC-COUP-02', '@coupon'), async ({ page }) => {
  await step('1. ใส่สุนัขพันธุ์ใหญ่ สูตรเนื้อ ×1 แล้วเปิดตะกร้า', async () => cartWith(page, [[P.largeBreedBeef, 1]]));
  await step('2. ใช้คูปอง PAW10 (1,590×10% = 159 · ≥ 999 ส่งฟรี · 1,590−159 = 1,431)', async () => {
    await applyCoupon(page, 'PAW10');
    await checkSummary(page, '', { subtotal: 1590, discount: 159, shipping: 0, total: 1431 });
  });
});

test('TC-COUP-03 PAW10 กับ ฿799 (10% มีเศษ)', plan('TC-COUP-03', '@coupon'), async ({ page }) => {
  await step('1. ใส่แมวโต สูตรไก่ 3 kg ×1 แล้วเปิดตะกร้า', async () => cartWith(page, [[P.adultChicken3kg, 1]]));
  await step('2. ใช้คูปอง PAW10 (79.9 → ปัดลง ฿79 ตามสมมติฐาน Q1/E1 · 799−79+50 = 770)', async () => {
    await applyCoupon(page, 'PAW10');
    await checkSummary(page, '', { subtotal: 799, discount: 79, shipping: 50, total: 770 });
  });
});

test('TC-COUP-04 FREESHIP กับ ฿189', plan('TC-COUP-04', '@coupon'), async ({ page }) => {
  await step('1. ใส่ลูกแมว 400 g ×1 แล้วเปิดตะกร้า', async () => cartWith(page, [[P.kitten400, 1]]));
  await step('2. ใช้คูปอง FREESHIP (ส่วนลด 0 · ส่งฟรี · ยอด 189)', async () => {
    await applyCoupon(page, 'FREESHIP');
    await checkSummary(page, '', { discount: 0, shipping: 0, total: 189 });
  });
});

test('TC-COUP-05 NEWCAT50 อาหารแมว ฿499 → ฿534', plan('TC-COUP-05', '@coupon'), async ({ page }) => {
  await step('1. ใส่เพาช์ทูน่า ×2 + แมวสูงวัย สูตรทูน่า ×1 (35×2+429 = 499) แล้วเปิดตะกร้า', async () =>
    cartWith(page, [[P.tunaPouch, 2], [P.seniorTuna, 1]]));
  await step('2. ใช้ NEWCAT50 ที่ ฿499 (< 500 ไม่ได้ส่วนลด · 499+50 = 549)', async () => {
    await applyCoupon(page, 'NEWCAT50');
    await check(page, 'ข้อความ "ต้องซื้ออาหารแมวขั้นต่ำ ฿500"', message(page), () => expect.soft(message(page)).toHaveText(/ต้องซื้ออาหารแมวขั้นต่ำ ฿500/));
    await checkSummary(page, '฿499:', { subtotal: 499, discount: 0, total: 549 });
  });
  await step('3. เพิ่มเพาช์อีก 1 ซอง (= ฿534) แล้วใส่โค้ด NEWCAT50 ใหม่ (534−50+50 = 534)', async () => {
    await page.locator(`[data-testid="cart-item"][data-slug="${P.tunaPouch.slug}"]`).getByTestId('item-plus').click();
    await applyCoupon(page, 'NEWCAT50');
    await checkSummary(page, '฿534:', { subtotal: 534, discount: 50, shipping: 50, total: 534 });
  });
});

test('TC-COUP-06 NEWCAT50 กับอาหารสุนัข ฿790', plan('TC-COUP-06', '@coupon'), async ({ page }) => {
  await step('1. ใส่สุนัขโต สูตรแกะ 3 kg ×1 แล้วเปิดตะกร้า', async () => cartWith(page, [[P.adultLamb3kg, 1]]));
  await step('2. ใช้ NEWCAT50 (ไม่ใช่อาหารแมว · 790+50 = 840)', async () => {
    await applyCoupon(page, 'NEWCAT50');
    await check(page, 'ข้อความ "ต้องซื้ออาหารแมวขั้นต่ำ ฿500"', message(page), () => expect.soft(message(page)).toHaveText(/ต้องซื้ออาหารแมวขั้นต่ำ ฿500/));
    await checkSummary(page, '', { discount: 0, total: 840 });
  });
});

test('TC-COUP-07 NEWCAT50 กับของเล่นแมว ฿519', plan('TC-COUP-07', '@coupon'), async ({ page }) => {
  await step('1. ใส่อุโมงค์แมว ×1 + ไม้ตกแมว ×1 (390+129 = 519) แล้วเปิดตะกร้า', async () =>
    cartWith(page, [[P.catTunnel, 1], [P.featherWand, 1]]));
  await step('2. ใช้ NEWCAT50 (ของเล่นไม่ใช่อาหาร · 519+50 = 569)', async () => {
    await applyCoupon(page, 'NEWCAT50');
    await checkSummary(page, '', { subtotal: 519, discount: 0, total: 569 });
  });
});

test('TC-COUP-08 SUMMER20 หมดอายุ', plan('TC-COUP-08', '@coupon'), async ({ page }) => {
  await step('1. ใส่แมวโต สูตรไก่ 3 kg (฿799) แล้วเปิดตะกร้า', async () => cartWith(page, [[P.adultChicken3kg, 1]]));
  await step('2. ใช้ SUMMER20 (799+50 = 849)', async () => {
    await applyCoupon(page, 'SUMMER20');
    await check(page, 'ข้อความ "คูปองนี้หมดอายุแล้ว"', message(page), () => expect.soft(message(page)).toHaveText('คูปองนี้หมดอายุแล้ว'));
    await checkSummary(page, '', { discount: 0, total: 849 });
  });
});

test('TC-COUP-09 โค้ดที่ไม่มี ABC', plan('TC-COUP-09', '@coupon'), async ({ page }) => {
  await step('1. ใส่แมวโต สูตรไก่ 3 kg (฿799) แล้วเปิดตะกร้า', async () => cartWith(page, [[P.adultChicken3kg, 1]]));
  await step('2. ใช้โค้ด ABC (799+50 = 849)', async () => {
    await applyCoupon(page, 'ABC');
    await check(page, 'ข้อความ "ไม่พบคูปองนี้"', message(page), () => expect.soft(message(page)).toHaveText('ไม่พบคูปองนี้'));
    await checkSummary(page, '', { discount: 0, total: 849 });
  });
});

test('TC-COUP-10 FREESHIP แล้วนำคูปองออก', plan('TC-COUP-10', '@coupon'), async ({ page }) => {
  await step('1. ใส่แมวโต สูตรไก่ 3 kg (฿799) แล้วเปิดตะกร้า', async () => cartWith(page, [[P.adultChicken3kg, 1]]));
  await step('2. ใช้ FREESHIP (ส่งฟรี ยอด 799)', async () => {
    await applyCoupon(page, 'FREESHIP');
    await checkSummary(page, 'ก่อนนำออก:', { shipping: 0, total: 799 });
  });
  await step('3. กด "นำคูปองออก" (799+50 = 849)', async () => {
    await page.getByTestId('coupon-remove').click();
    await checkSummary(page, 'หลังนำออก:', { discount: 0, shipping: 50, total: 849 });
  });
});
