import { tc, test, expect, open, bookToStep3, fillContact } from './fixtures';

const S = test.step;

async function calc(page: import('@playwright/test').Page, o: { distance?: string; hotel?: string; people: number }) {
  if (o.hotel) await page.getByTestId('transport-hotel').selectOption(o.hotel);
  if (o.distance !== undefined) {
    await page.getByTestId('transport-hotel').selectOption('');
    await page.getByTestId('transport-distance').fill(o.distance);
  }
  await page.getByTestId('transport-people').selectOption(String(o.people));
  await page.getByTestId('transport-calc').click();
}

tc('TC-TRN-01', async ({ page }) => {
  await open(page, '/transport');
  for (const [d, fee] of [['5.0', 0], ['5.1', 300], ['15.0', 300]] as const) {
    await S(`ระยะ ${d} กม. 1 คน → ฿${fee}`, async () => {
      await calc(page, { distance: d, people: 1 });
      await expect.soft(page.getByTestId('transport-fee')).toHaveAttribute('data-amount', String(fee));
    });
  }
  await S('ระยะ 15.1 กม. → "อยู่นอกพื้นที่รับส่ง"', async () => {
    await calc(page, { distance: '15.1', people: 1 });
    await expect.soft(page.getByTestId('transport-error')).toContainText('อยู่นอกพื้นที่รับส่ง');
  });
});

tc('TC-TRN-02', async ({ page }) => {
  await open(page, '/transport');
  for (const [n, cars, fee] of [[4, 1, 300], [5, 2, 600]] as const) {
    await S(`H04 12 กม. ${n} คน → ${cars} คัน ฿${fee}`, async () => {
      await calc(page, { hotel: 'H04', people: n });
      await expect.soft(page.getByTestId('transport-vehicles')).toContainText(String(cars));
      await expect.soft(page.getByTestId('transport-fee')).toHaveAttribute('data-amount', String(fee));
    });
  }
});

tc('TC-TRN-03', async ({ page }) => {
  await S('ขั้น 3 (ไม่ล็อกอิน S01) ติ๊กรถรับส่ง ไม่เลือกโรงแรม ไม่ใส่ระยะ', async () => {
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
    await fillContact(page, 'ทดสอบรถ', '0812345678');
    await page.getByTestId('book-transport').check();
  });
  await S('กด "ถัดไป" → ยังอยู่ขั้น 3 และมีข้อความให้ใส่ระยะทาง/เลือกโรงแรม (ทันที)', async () => {
    await page.getByTestId('book-next-3').click();
    await expect.soft(page.getByTestId('book-summary'), 'ต้องไปขั้น 4 ไม่ได้').toHaveCount(0);
    await expect.soft(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
    const msg = page.locator('[data-testid="book-error-message"], [data-testid="book-quote-error-message"]');
    await expect.soft(msg.filter({ hasText: /ระยะ|โรงแรม/ })).toHaveCount(1);
  });
});
