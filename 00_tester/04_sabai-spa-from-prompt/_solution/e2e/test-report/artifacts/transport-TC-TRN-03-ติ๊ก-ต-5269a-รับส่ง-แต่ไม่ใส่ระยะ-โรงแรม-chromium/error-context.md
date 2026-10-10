# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: transport.spec.ts >> TC-TRN-03 ติ๊ก "ต้องการรถรับส่ง" แต่ไม่ใส่ระยะ/โรงแรม
- Location: tests\fixtures.ts:169:3

# Error details

```
Error: ต้องไปขั้น 4 ไม่ได้

expect(locator).toHaveCount(expected) failed

Locator:  getByTestId('book-summary')
Expected: 0
Received: 1
Timeout:  7000ms

Call log:
  - ต้องไปขั้น 4 ไม่ได้ getByTestId('book-summary') with timeout 7000ms
  - waiting for getByTestId('book-summary')
    18 × locator resolved to 1 element
       - unexpected value "1"

```

```
Error: expect(locator).toHaveAttribute(expected) failed

Locator:  getByTestId('book-step-indicator')
Expected: "3"
Received: "4"
Timeout:  7000ms

Call log:
  - Expect "soft toHaveAttribute" getByTestId('book-step-indicator') with timeout 7000ms
  - waiting for getByTestId('book-step-indicator')
    18 × locator resolved to <p data-step="4" class="muted small" data-testid="book-step-indicator">ขั้นที่ 4 จาก 4</p>
       - unexpected value "4"

```

```yaml
- paragraph: ขั้นที่ 4 จาก 4
```

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  locator('[data-testid="book-error-message"], [data-testid="book-quote-error-message"]').filter({ hasText: /ระยะ|โรงแรม/ })
Expected: 1
Received: 0
Timeout:  7000ms

Call log:
  - Expect "soft toHaveCount" locator('[data-testid="book-error-message"], [data-testid="book-quote-error-message"]').filter({ hasText: /ระยะ|โรงแรม/ }) with timeout 7000ms
  - waiting for locator('[data-testid="book-error-message"], [data-testid="book-quote-error-message"]').filter({ hasText: /ระยะ|โรงแรม/ })
    18 × locator resolved to 0 elements
       - unexpected value "0"

```

# Test source

```ts
  1  | import { tc, test, expect, open, bookToStep3, fillContact } from './fixtures';
  2  | 
  3  | const S = test.step;
  4  | 
  5  | async function calc(page: import('@playwright/test').Page, o: { distance?: string; hotel?: string; people: number }) {
  6  |   if (o.hotel) await page.getByTestId('transport-hotel').selectOption(o.hotel);
  7  |   if (o.distance !== undefined) {
  8  |     await page.getByTestId('transport-hotel').selectOption('');
  9  |     await page.getByTestId('transport-distance').fill(o.distance);
  10 |   }
  11 |   await page.getByTestId('transport-people').selectOption(String(o.people));
  12 |   await page.getByTestId('transport-calc').click();
  13 | }
  14 | 
  15 | tc('TC-TRN-01', async ({ page }) => {
  16 |   await open(page, '/transport');
  17 |   for (const [d, fee] of [['5.0', 0], ['5.1', 300], ['15.0', 300]] as const) {
  18 |     await S(`ระยะ ${d} กม. 1 คน → ฿${fee}`, async () => {
  19 |       await calc(page, { distance: d, people: 1 });
  20 |       await expect.soft(page.getByTestId('transport-fee')).toHaveAttribute('data-amount', String(fee));
  21 |     });
  22 |   }
  23 |   await S('ระยะ 15.1 กม. → "อยู่นอกพื้นที่รับส่ง"', async () => {
  24 |     await calc(page, { distance: '15.1', people: 1 });
  25 |     await expect.soft(page.getByTestId('transport-error')).toContainText('อยู่นอกพื้นที่รับส่ง');
  26 |   });
  27 | });
  28 | 
  29 | tc('TC-TRN-02', async ({ page }) => {
  30 |   await open(page, '/transport');
  31 |   for (const [n, cars, fee] of [[4, 1, 300], [5, 2, 600]] as const) {
  32 |     await S(`H04 12 กม. ${n} คน → ${cars} คัน ฿${fee}`, async () => {
  33 |       await calc(page, { hotel: 'H04', people: n });
  34 |       await expect.soft(page.getByTestId('transport-vehicles')).toContainText(String(cars));
  35 |       await expect.soft(page.getByTestId('transport-fee')).toHaveAttribute('data-amount', String(fee));
  36 |     });
  37 |   }
  38 | });
  39 | 
  40 | tc('TC-TRN-03', async ({ page }) => {
  41 |   await S('ขั้น 3 (ไม่ล็อกอิน S01) ติ๊กรถรับส่ง ไม่เลือกโรงแรม ไม่ใส่ระยะ', async () => {
  42 |     await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
  43 |     await fillContact(page, 'ทดสอบรถ', '0812345678');
  44 |     await page.getByTestId('book-transport').check();
  45 |   });
  46 |   await S('กด "ถัดไป" → ยังอยู่ขั้น 3 และมีข้อความให้ใส่ระยะทาง/เลือกโรงแรม (ทันที)', async () => {
  47 |     await page.getByTestId('book-next-3').click();
  48 |     await expect.soft(page.getByTestId('book-summary'), 'ต้องไปขั้น 4 ไม่ได้').toHaveCount(0);
  49 |     await expect.soft(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
  50 |     const msg = page.locator('[data-testid="book-error-message"], [data-testid="book-quote-error-message"]');
> 51 |     await expect.soft(msg.filter({ hasText: /ระยะ|โรงแรม/ })).toHaveCount(1);
     |                                                               ^ Error: expect(locator).toHaveCount(expected) failed
  52 |   });
  53 | });
  54 | 
```