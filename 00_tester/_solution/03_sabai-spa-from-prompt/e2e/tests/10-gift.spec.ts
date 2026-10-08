import { test, expect, open, pause, fillBooking, expectMoney, bookingDate, DAY } from './fixtures';
import type { Page } from '@playwright/test';

const AMOUNT_ERR = 'มูลค่า Gift Card ต้องอยู่ระหว่าง ฿500–฿10,000';

async function fillGift(page: Page, o: { amount?: string; design?: string; channel?: 'line' | 'email'; recipient?: string }) {
  if (o.amount !== undefined) await page.getByTestId('gift-amount').fill(o.amount);
  if (o.design) await page.getByTestId(`gift-design-${o.design}`).click();
  if (o.channel) await page.getByTestId(`gift-channel-${o.channel}`).click();
  if (o.recipient !== undefined) await page.getByTestId('gift-recipient').fill(o.recipient);
  await page.getByTestId('gift-submit').click();
}

async function checkCard(page: Page, code: string) {
  await page.getByTestId('gift-check-code').fill(code);
  await page.getByTestId('gift-check-submit').click();
  await page.getByTestId('gift-check-form').scrollIntoViewIfNeeded();
}

test.describe('Gift Card', () => {
  test('TC-GIFT-01 ซื้อ Gift Card: ค่าขอบมูลค่า ลาย และช่องทาง', {
    tag: ['@GIFT', '@P2'],
    annotation: {
      type: 'expected',
      description:
        '499 / 10001 / 500.5 → gift-error "' + AMOUNT_ERR + '" · 500 และ 10000 ผ่าน · ไม่เลือกลาย → "กรุณาเลือกลาย Gift Card" · ไม่เลือกช่องทาง → "กรุณาเลือกช่องทางส่ง (LINE หรืออีเมล)" · ' +
        'email ผิด "abc" → "กรุณากรอก LINE ID หรืออีเมลผู้รับให้ถูกต้อง" · มีลาย 3 แบบ orchid / lotus / gold · ชุดที่ถูกต้อง 2000, orchid, line, "mom-line" → gift-success · gift-code ขึ้นต้น "GC-" · ' +
        'gift-expiry data-date "2027-10-08" · gift-simulated-note แสดง · API delivery = {"simulated":true,"sent":false}',
    },
  }, async ({ page, apiLog }) => {
    await open(page, '/gift-cards');
    await expect(page.getByTestId('gift-form').getByTestId(/^gift-design-/)).toHaveCount(3);
    for (const d of ['orchid', 'lotus', 'gold']) await expect.soft(page.getByTestId(`gift-design-${d}`)).toBeVisible();

    await test.step('ไม่เลือกลาย', async () => {
      await fillGift(page, { amount: '2000' });
      await expect(page.getByTestId('gift-error')).toHaveText('กรุณาเลือกลาย Gift Card');
    });
    await test.step('ไม่เลือกช่องทาง', async () => {
      await fillGift(page, { design: 'orchid' });
      await expect(page.getByTestId('gift-error')).toHaveText('กรุณาเลือกช่องทางส่ง (LINE หรืออีเมล)');
    });
    for (const amount of ['499', '10001', '500.5']) {
      await test.step(`มูลค่า ${amount} → error`, async () => {
        await fillGift(page, { amount, channel: 'line', recipient: 'mom-line' });
        await expect.soft(page.getByTestId('gift-error'), `มูลค่า ${amount}`).toHaveText(AMOUNT_ERR);
        await expect.soft(page.getByTestId('gift-success')).toHaveCount(0);
      });
    }
    for (const amount of ['500', '10000']) {
      await test.step(`มูลค่า ${amount} → ผ่าน`, async () => {
        await fillGift(page, { amount, channel: 'line', recipient: 'mom-line' });
        await expect.soft(page.getByTestId('gift-success'), `มูลค่า ${amount}`).toBeVisible();
        if (await page.getByTestId('gift-again').isVisible()) {
          // กด 'ซื้ออีกใบ' แล้วกล่องผลลัพธ์หายไป หน้าจะขยับ — รอให้นิ่งก่อนกรอกใบถัดไป (กันคลิกปุ่มส่งพลาดตอนหน้ากำลังขยับ)
          await page.getByTestId('gift-again').click();
          await expect(page.getByTestId('gift-success')).toHaveCount(0);
          await page.waitForTimeout(500);
        }
      });
    }
    await test.step('อีเมลผู้รับ "abc"', async () => {
      await fillGift(page, { amount: '2000', channel: 'email', recipient: 'abc' });
      await expect(page.getByTestId('gift-error')).toHaveText('กรุณากรอก LINE ID หรืออีเมลผู้รับให้ถูกต้อง');
    });

    await test.step('ชุดที่ถูกต้อง: 2000 · orchid · LINE · mom-line', async () => {
      await page.getByTestId('gift-quick-2000').click();
      await fillGift(page, { design: 'orchid', channel: 'line', recipient: 'mom-line' });
      await expect(page.getByTestId('gift-success')).toBeVisible();
      await expect(page.getByTestId('gift-code')).toHaveText(/^GC-/);
      await expect(page.getByTestId('gift-expiry')).toHaveAttribute('data-date', '2027-10-08');
      await expect(page.getByTestId('gift-simulated-note')).toBeVisible();
      await pause(page);
    });

    const r = await apiLog.call(page.request, 'POST', '/api/giftcards', {
      amount: 2000, design: 'orchid', channel: 'line', recipient: 'mom-line', recipientName: 'Mom', senderName: 'Fon', message: 'สุขสันต์วันเกิด',
    });
    expect(r.body.delivery).toMatchObject({ simulated: true, sent: false });
  });

  test('TC-GIFT-02 ใช้ Gift Card จ่ายค่าบริการ และวันหมดอายุ 365 / 366', {
    tag: ['@GIFT', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'บัตร ฿2,000: aroma-oil ฿1,500 → price-total ฿1,500 · price-gift −฿1,500 · price-due ฿0 · ตรวจบัตรเหลือ gift-check-balance ฿500 · ครั้งที่ 2 thai-massage ฿800 → price-gift −฿500 · price-due ฿300 · ' +
          'บัตรเหลือ ฿0 → data-status "empty" "Gift Card นี้ใช้ยอดหมดแล้ว" · GIFT-DAY365 → data-status "valid" · gift-check-expiry 2026-10-08 · GIFT-DAY366 → "expired" "Gift Card หมดอายุแล้ว" · ' +
          'ใช้ DAY366 ที่ /book → booking-gift-error "Gift Card หมดอายุแล้ว" และ price-due ไม่ลด',
      },
      {
        type: 'note',
        description: 'ใช้บัตร ฿2,000 ลาย orchid ที่ซื้อใหม่ผ่าน POST /api/giftcards แทน GIFT-2000-ORCHID (บัตรเดียวกันถูก 3 เบราว์เซอร์ใช้พร้อมกันไม่ได้) · วันจองแยกตามเบราว์เซอร์',
      },
    ],
  }, async ({ page, browserName, apiLog }) => {
    const date = bookingDate(browserName, DAY.GIFT);
    const bought = await apiLog.call(page.request, 'POST', '/api/giftcards', { amount: 2000, design: 'orchid', channel: 'line', recipient: 'mom-line' });
    expect(bought.status).toBe(201);
    const code = bought.body.giftCard.code as string;

    await test.step(`ครั้งที่ 1: aroma-oil ฿1,500 ด้วยบัตร ${code}`, async () => {
      await open(page, '/book');
      await fillBooking(page, { service: 'aroma-oil', date, time: '12:00', guest: true });
      await page.getByTestId('booking-gift-code').fill(code);
      await page.getByTestId('booking-gift-apply').click();
      await expect(page.getByTestId('booking-gift-status')).toBeVisible();
      await expectMoney(page.getByTestId('price-total'), 1500);
      await expectMoney(page.getByTestId('price-gift'), -1500);
      await expectMoney(page.getByTestId('price-due'), 0);
      await pause(page);
      await page.getByTestId('booking-submit').click();
      await expect(page.getByTestId('booking-success')).toBeVisible();
    });

    await open(page, '/gift-cards');
    await checkCard(page, code);
    await expectMoney(page.getByTestId('gift-check-balance'), 500);
    await pause(page);

    await test.step('ครั้งที่ 2: thai-massage ฿800 ด้วยบัตรเดิม (เหลือ ฿500)', async () => {
      await open(page, '/book');
      await fillBooking(page, { service: 'thai-massage', date, time: '15:00', guest: true });
      await page.getByTestId('booking-gift-code').fill(code);
      await page.getByTestId('booking-gift-apply').click();
      await expectMoney(page.getByTestId('price-gift'), -500);
      await expectMoney(page.getByTestId('price-due'), 300);
      await pause(page);
      await page.getByTestId('booking-submit').click();
      await expect(page.getByTestId('booking-success')).toBeVisible();
    });

    await open(page, '/gift-cards');
    await checkCard(page, code);
    await expect(page.getByTestId('gift-check-result')).toHaveAttribute('data-status', 'empty');
    await expect(page.getByTestId('gift-check-error')).toHaveText('Gift Card นี้ใช้ยอดหมดแล้ว');
    await pause(page);

    await checkCard(page, 'GIFT-DAY365');
    await expect(page.getByTestId('gift-check-result')).toHaveAttribute('data-status', 'valid');
    await expect(page.getByTestId('gift-check-expiry')).toHaveAttribute('data-date', '2026-10-08');
    await pause(page);
    await checkCard(page, 'GIFT-DAY366');
    await expect(page.getByTestId('gift-check-result')).toHaveAttribute('data-status', 'expired');
    await expect(page.getByTestId('gift-check-error')).toHaveText('Gift Card หมดอายุแล้ว');
    await pause(page);

    await test.step('ใช้ GIFT-DAY366 ที่ /book', async () => {
      await open(page, '/book');
      await page.getByTestId('service-option-thai-massage').click();
      await expectMoney(page.getByTestId('price-due'), 800);
      await page.getByTestId('booking-gift-code').fill('GIFT-DAY366');
      await page.getByTestId('booking-gift-apply').click();
      await expect(page.getByTestId('booking-gift-error')).toHaveText('Gift Card หมดอายุแล้ว');
      await page.waitForTimeout(500);
      await expectMoney(page.getByTestId('price-due'), 800);
      await expect(page.getByTestId('price-gift')).toHaveCount(0);
    });
  });
});
