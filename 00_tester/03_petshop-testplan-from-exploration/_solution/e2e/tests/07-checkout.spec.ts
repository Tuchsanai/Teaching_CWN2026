import { test, expect, step, check, open, plan, toCheckout, fillAddress, placeOrder, baht, P, type Page } from './fixtures';

// TEST-PLAN.md หัวข้อ 5.5 ชำระเงิน · ฟอร์มที่อยู่ · สต็อกหลังสั่ง (TC-CHK-01 … 07)

const MSG = {
  name: 'กรุณากรอกชื่อผู้รับ',
  phone: 'เบอร์โทรต้องเป็นตัวเลข 10 หลัก ขึ้นต้นด้วย 0',
  postcode: 'รหัสไปรษณีย์ต้องเป็นตัวเลข 5 หลัก',
  address: 'กรุณากรอกที่อยู่ (อย่างน้อย 10 ตัวอักษร)',
};
const total = (page: Page) => page.getByTestId('summary-total');

/** ลองค่าหนึ่งค่าในฟอร์มที่อยู่ (ช่องอื่นถูกทั้งหมด) แล้วตรวจว่าผ่าน/ไม่ผ่าน */
async function tryValue(page: Page, field: 'phone' | 'postcode' | 'address', value: string, ok: boolean) {
  await open(page, '/checkout');
  await fillAddress(page, { [field]: value });
  await page.getByTestId('place-order').click();
  const error = page.getByTestId(`error-ship-${field}`);
  if (ok) {
    await page.waitForURL(/\/orders\//).catch(() => {});
    await check(page, `"${value}": ผ่าน สั่งซื้อได้`, page.getByTestId(`ship-${field}`), () => expect.soft(page).toHaveURL(/\/orders\/PP-\d+/));
  } else {
    await page.waitForTimeout(800);
    await check(page, `"${value}": ไม่สร้างคำสั่งซื้อ (ยังอยู่ /checkout)`, page.getByTestId(`ship-${field}`), () => expect.soft(page).toHaveURL(/\/checkout$/));
    await check(page, `"${value}": ข้อความ "${MSG[field]}"`, error, () => expect.soft(error).toHaveText(MSG[field]), { near: page.getByTestId(`ship-${field}`) });
  }
}

test('TC-CHK-01 สั่งซื้อจนจบ ลูกแมว 400 g ×2 COD', plan('TC-CHK-01', '@checkout'), async ({ page }) => {
  await step('1. login demo · ลูกแมว 400 g ×2 · หน้าชำระเงิน กรอกที่อยู่มาตรฐาน · ส่งธรรมดา · เก็บเงินปลายทาง', async () => {
    await toCheckout(page, [[P.kitten400, 2]]);
    await page.getByTestId('shipping-standard').check();
    await page.getByTestId('pay-cod').check();
    await check(page, 'ปุ่มแสดง "ยืนยันสั่งซื้อ ฿428" (189×2+50)', page.getByTestId('place-order'),
      () => expect.soft(page.getByTestId('place-order')).toHaveText(/ยืนยันสั่งซื้อ ฿428/));
  });
  await step('2. กด "ยืนยันสั่งซื้อ"', async () => {
    await page.getByTestId('place-order').click();
    await page.waitForURL(/\/orders\//).catch(() => {});
    await check(page, 'ไปหน้า /orders/PP-…', null, () => expect.soft(page).toHaveURL(/\/orders\/PP-\d+$/));
    await check(page, 'บอกว่าสั่งซื้อสำเร็จ', page.getByTestId('order-success'), () => expect.soft(page.getByTestId('order-success')).toContainText('สั่งซื้อสำเร็จ'));
    await check(page, 'ยอด ฿428', total(page), async () => expect.soft(baht(await total(page).innerText())).toBe(428));
    await check(page, '🛒 = 0 หลังสั่ง', page.getByTestId('cart-count'), () => expect.soft(page.getByTestId('cart-count')).toHaveText('0'));
  });
});

test('TC-CHK-02 ล้างทุกช่องแล้วกดยืนยัน', plan('TC-CHK-02', '@checkout'), async ({ page }) => {
  await step('1. login · ลูกแมว 400 g ×1 · หน้าชำระเงิน ล้างทุกช่อง', async () => {
    await toCheckout(page, [[P.kitten400, 1]]);
    for (const f of ['ship-name', 'ship-phone', 'ship-postcode', 'ship-address']) await page.getByTestId(f).fill('');
  });
  await step('2. กด "ยืนยันสั่งซื้อ"', async () => {
    await page.getByTestId('place-order').click();
    await page.waitForTimeout(800);
    await check(page, 'ยังอยู่ /checkout (ไม่สร้างคำสั่งซื้อ)', page.getByTestId('place-order'), () => expect.soft(page).toHaveURL(/\/checkout$/));
    for (const f of ['name', 'phone', 'postcode', 'address'] as const) {
      const e = page.getByTestId(`error-ship-${f}`);
      await check(page, `error: "${MSG[f]}"`, e, () => expect.soft(e).toHaveText(MSG[f]), { near: page.getByTestId(`ship-${f}`) });
    }
  });
});

test('TC-CHK-03 เบอร์โทร 9 / 10 / 11 หลัก และขึ้นต้น 1', plan('TC-CHK-03', '@checkout'), async ({ page }) => {
  await step('1. login · ลูกแมว 400 g ×1', async () => toCheckout(page, [[P.kitten400, 1]]));
  await step('2. เบอร์ 9 หลัก 081234567', async () => tryValue(page, 'phone', '081234567', false));
  await step('3. เบอร์ 11 หลัก 08123456789', async () => tryValue(page, 'phone', '08123456789', false));
  await step('4. เบอร์ 10 หลักขึ้นต้น 1: 1812345678', async () => tryValue(page, 'phone', '1812345678', false));
  await step('5. เบอร์ 10 หลักขึ้นต้น 0: 0812345678', async () => tryValue(page, 'phone', '0812345678', true));
});

test('TC-CHK-04 รหัสไปรษณีย์ 4 / 5 / 6 หลัก', plan('TC-CHK-04', '@checkout'), async ({ page }) => {
  await step('1. login · ลูกแมว 400 g ×1', async () => toCheckout(page, [[P.kitten400, 1]]));
  await step('2. รหัสไปรษณีย์ 4 หลัก 1011', async () => tryValue(page, 'postcode', '1011', false));
  await step('3. รหัสไปรษณีย์ 6 หลัก 101100', async () => tryValue(page, 'postcode', '101100', false));
  await step('4. รหัสไปรษณีย์ 5 หลัก 10110', async () => tryValue(page, 'postcode', '10110', true));
});

test('TC-CHK-05 ที่อยู่ 9 / 10 ตัวอักษร', plan('TC-CHK-05', '@checkout'), async ({ page }) => {
  await step('1. login · ลูกแมว 400 g ×1', async () => toCheckout(page, [[P.kitten400, 1]]));
  await step('2. ที่อยู่ 9 ตัว "123 Sukhu"', async () => tryValue(page, 'address', '123 Sukhu', false));
  await step('3. ที่อยู่ 10 ตัว "123 Sukhum"', async () => tryValue(page, 'address', '123 Sukhum', true));
});

test('TC-CHK-06 ลูกแมว 1.5 kg ส่งด่วน PromptPay', plan('TC-CHK-06', '@checkout'), async ({ page }) => {
  await step('1. login · ลูกแมว 1.5 kg ×1 · หน้าชำระเงิน เลือกส่งด่วน + PromptPay', async () => {
    await toCheckout(page, [[P.kitten15, 1]]);
    await page.getByTestId('shipping-express').check();
    await page.getByTestId('pay-promptpay').check();
    await check(page, 'ปุ่ม "ยืนยันสั่งซื้อ ฿710" (590+120)', page.getByTestId('place-order'),
      () => expect.soft(page.getByTestId('place-order')).toHaveText(/ยืนยันสั่งซื้อ ฿710/));
  });
  await step('2. กดยืนยันสั่งซื้อ', async () => {
    await placeOrder(page);
    await check(page, 'หน้าคำสั่งซื้อยอด ฿710', total(page), async () => expect.soft(baht(await total(page).innerText())).toBe(710));
    await check(page, 'ระบุวิธีชำระ PromptPay', page.locator('main'), () => expect.soft(page.locator('main')).toContainText('PromptPay'));
    await check(page, 'ระบุส่งด่วน', page.locator('main'), () => expect.soft(page.locator('main')).toContainText('ด่วน'));
  });
});

test('TC-CHK-07 สั่งสูตรลดก้อนขน 3 ชิ้น แล้วสต็อกหมด', plan('TC-CHK-07', '@checkout'), async ({ page }) => {
  await step('1. login · สูตรลดก้อนขน ×3 · สั่งซื้อ', async () => {
    await toCheckout(page, [[P.hairball, 3]]);
    await placeOrder(page);
    await check(page, 'คำสั่งซื้อยอด ฿1,560 (520×3 ≥ 999 ส่งฟรี)', total(page), async () => expect.soft(baht(await total(page).innerText())).toBe(1560));
  });
  await step('2. เปิดหน้าสินค้าสูตรลดก้อนขนอีกครั้ง', async () => {
    await open(page, `/products/${P.hairball.slug}`);
    await check(page, 'ป้ายเปลี่ยนเป็น "หมด"', page.getByTestId('stock-info'), () => expect.soft(page.getByTestId('stock-info')).toContainText('หมด'));
    await check(page, 'ปุ่มใส่ตะกร้ากดไม่ได้', page.getByTestId('add-to-cart'), () => expect.soft(page.getByTestId('add-to-cart')).toBeDisabled());
  });
});
