import { tc, test, expect, open, loginUI, bookToStep3, fillContact, toSummary, amount, quoteTotal, settle } from './fixtures';
import type { Page } from '@playwright/test';

const S = test.step;

async function applyCard(page: Page, code: string) {
  await page.getByTestId('book-giftcard').fill(code);
  await page.getByTestId('book-giftcard-apply').click();
  await settle(page);
}
const backTo3 = async (page: Page) => {
  await page.getByTestId('book-back-4').click();
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
};

tc('TC-GC-01', async ({ page }) => {
  const buy = async (value: string) => {
    await open(page, '/giftcard');
    await page.getByTestId('gc-value').fill(value);
    await page.getByTestId('gc-design-label-lotus').click();
    await page.getByTestId('gc-channel-label-line').click();
    await page.getByTestId('gc-recipient').fill('แม่');
    await page.getByTestId('gc-submit').click();
  };
  for (const [v, ok] of [['499', false], ['500', true], ['10000', true], ['10001', false]] as const) {
    await S(`มูลค่า ฿${Number(v).toLocaleString('en-US')} ลายบัว LINE ถึง "แม่" → ${ok ? '✅' : '❌'}`, async () => {
      await buy(v);
      if (ok) {
        await expect.soft(page.getByTestId('gc-result')).toBeVisible();
        // ซื้อวันนี้ 10 ต.ค. 2026 + 365 วัน = 10 ต.ค. 2027
        await expect.soft(page.getByTestId('gc-expires')).toHaveText(/10 ต\.ค\. 2027|2027-10-10/);
      } else {
        await expect.soft(page.getByTestId('gc-error')).toBeVisible();
        await expect.soft(page.getByTestId('gc-result')).toHaveCount(0);
      }
    });
  }
});

tc('TC-GC-02', async ({ page }) => {
  await S('ไม่ล็อกอิน S01 ฿1,000 ถึงขั้น 3', async () => {
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
    await fillContact(page, 'ทดสอบบัตร', '0812345678');
  });
  await S('GC04 SABAI-GC-EXP (หมด 9 ต.ค.) → "บัตรหมดอายุแล้ว" ยอดสุทธิยัง ฿1,000', async () => {
    await applyCard(page, 'SABAI-GC-EXP');
    await expect.soft(page.getByTestId('book-giftcard-error')).toContainText('บัตรหมดอายุแล้ว');
    expect.soft(await quoteTotal(page)).toBe(1000);
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(1000);
    await expect.soft(page.getByTestId('summary-line-giftcard')).toHaveCount(0);
    await backTo3(page);
  });
  await S('GC03 SABAI-GC-LAST (วันสุดท้าย ยอด ฿500) → จ่ายด้วยบัตร ฿500 + จ่ายเพิ่ม ฿500', async () => {
    await applyCard(page, 'SABAI-GC-LAST');
    await toSummary(page);
    expect.soft(Math.abs(await amount(page, 'summary-amount-giftcard'))).toBe(500);
    expect.soft(await amount(page, 'summary-amount-other')).toBe(500);
    await backTo3(page);
  });
  await S('GC05 SABAI-GC-ZERO (ยอด ฿0) → หักไม่ได้ มีข้อความแจ้ง ยอดที่ต้องจ่ายยัง ฿1,000', async () => {
    await applyCard(page, 'SABAI-GC-ZERO');
    await expect.soft(page.getByTestId('book-giftcard-error')).toBeVisible();
    await toSummary(page);
    await expect.soft(page.getByTestId('summary-line-giftcard')).toHaveCount(0);
    expect.soft(await amount(page, 'summary-amount-other')).toBe(1000);
  });
});

tc('TC-GC-03', async ({ page }) => {
  await loginUI(page, 'U04');
  await S('U04 (Silver) S06 ฿1,500 ใช้ GC01 SABAI-GC-2000 → จ่ายด้วยบัตร ฿1,500 จ่ายเพิ่ม ฿0 (ทันที)', async () => {
    await bookToStep3(page, { service: 'S06', type: 'single', date: '2026-10-20', time: '10:00' });
    await applyCard(page, 'SABAI-GC-2000');
    await toSummary(page);
    expect.soft(Math.abs(await amount(page, 'summary-amount-giftcard'))).toBe(1500);
    expect.soft(await amount(page, 'summary-amount-other')).toBe(0);
    await page.getByTestId('book-confirm').click();
    await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  });
  await S('หลังรีโหลด หน้าตรวจยอด /giftcard: SABAI-GC-2000 เหลือ ฿500', async () => {
    await open(page, '/giftcard');
    await page.getByTestId('gc-check-code').fill('SABAI-GC-2000');
    await page.getByTestId('gc-check-submit').click();
    await expect.soft(page.getByTestId('gc-check-balance')).toHaveText(/฿\s?500(\.00)?(?![\d,])/);
  });
});

tc('TC-GC-04', async ({ page }) => {
  // KNOWN-ISSUE (ส.ค. 69): ล้มตั้งแต่ส่งมอบ ยังไม่ได้แก้ · แก้แล้วให้ลบบรรทัด test.fail ออก
  test.fail(true, 'KNOWN-ISSUE: ใส่รหัสบัตรที่ไม่มีจริงแล้วไม่มีข้อความเตือน');
  await S('ไม่ล็อกอิน S01 ขั้น 3: ใส่รหัส XXXX แล้วกด "ใช้บัตรนี้"', async () => {
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
    await fillContact(page, 'ทดสอบบัตรมั่ว', '0812345678');
    await applyCard(page, 'XXXX');
  });
  await S('มีข้อความแจ้งว่าใช้บัตรไม่ได้ ก่อนไปขั้น 4', async () => {
    await expect.soft(page.getByTestId('book-giftcard-error')).toBeVisible();
    await expect.soft(page.getByTestId('book-giftcard-error')).not.toHaveText(/^\s*$/);
  });
  await S('ใบสรุปไม่มีบรรทัด Gift Card และยอด ฿1,000', async () => {
    await toSummary(page);
    await expect.soft(page.getByTestId('summary-line-giftcard')).toHaveCount(0);
    expect.soft(await amount(page, 'summary-total')).toBe(1000);
  });
});
