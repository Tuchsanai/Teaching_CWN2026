import { tc, test, expect, open, loginUI, logoutUI, bookStep2, toSummary, amount, type Api } from './fixtures';
import type { Page } from '@playwright/test';

const S = test.step;

/** จาก /wallet กด "จองด้วยคอร์ส" แล้วเดินถึงใบสรุป */
async function bookWithCourse(page: Page, course: string, date: string, time: string) {
  await open(page, '/wallet');
  await page.getByTestId(`course-book-${course}`).click();
  await page.locator('html[data-ready="true"]').waitFor();
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '1');
  await page.getByTestId('book-next-1').click();
  await bookStep2(page, { date, time });
  await toSummary(page);
}

const courseBooking = (date: string, time: string, extra: Record<string, unknown> = {}) =>
  ({ type: 'course', serviceCode: 'K01', people: 1, date, time, quotedTotal: 0, ...extra });

tc('TC-CRS-01', async ({ page }) => {
  await loginUI(page, 'U01');
  await S('Wallet ก่อนจอง: "เหลือ 7 จาก 11 ครั้ง"', async () => {
    await open(page, '/wallet');
    await expect.soft(page.getByTestId('course-remaining-C01')).toContainText('เหลือ 7 จาก 11 ครั้ง');
  });
  await S('จองด้วยคอร์ส C01 (K01) 20 ต.ค. 11:00 → ใบสรุปราคา ฿0 (ทันที)', async () => {
    await bookWithCourse(page, 'C01', '2026-10-20', '11:00');
    expect.soft(await amount(page, 'summary-total')).toBe(0);
    await page.getByTestId('book-confirm').click();
    await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  });
  await S('หลังรีโหลด /wallet: "เหลือ 6 จาก 11 ครั้ง"', async () => {
    await open(page, '/wallet');
    await expect.soft(page.getByTestId('course-remaining-C01')).toContainText('เหลือ 6 จาก 11 ครั้ง');
  });
});

tc('TC-CRS-02', async ({ page, api }) => {
  let code = '';
  await S('เตรียม: U01 จองด้วยคอร์ส C01 20 ต.ค. 11:00 (เหมือน TC-CRS-01) → Wallet เหลือ 6', async () => {
    const u01 = await api.as('U01');
    const r = await u01.post('/api/bookings', courseBooking('2026-10-20', '11:00'));
    expect(r.status, 'จองด้วยคอร์ส (เตรียมข้อมูล)').toBe(201);
    code = r.json.code;
    await loginUI(page, 'U01');
    await open(page, '/wallet');
    await expect.soft(page.getByTestId('course-remaining-C01')).toContainText('เหลือ 6 จาก 11 ครั้ง');
  });
  await S('ยกเลิกนัดคอร์สที่ /account (เหลือ 10 วัน) → ยกเลิกได้ (ทันที)', async () => {
    await open(page, '/account');
    await page.getByTestId(`cancel-${code}`).click();
    await page.getByTestId(`cancel-confirm-${code}`).click();
    await expect.soft(page.getByTestId(`booking-status-${code}`)).toContainText('ยกเลิก');
  });
  await S('หลังรีโหลด /wallet: กลับเป็น "เหลือ 7 จาก 11 ครั้ง"', async () => {
    await open(page, '/wallet');
    await expect.soft(page.getByTestId('course-remaining-C01')).toContainText('เหลือ 7 จาก 11 ครั้ง');
  });
});

tc('TC-CRS-03', async ({ page, api }) => {
  await S('U06 C03 (เหลือ 0) → ปุ่ม "จองด้วยคอร์ส" กดไม่ได้', async () => {
    await loginUI(page, 'U06');
    await open(page, '/wallet');
    await expect.soft(page.getByTestId('course-book-C03')).toBeDisabled();
  });
  await S('U05 C04 (หมดอายุ 28 ส.ค.) → ปุ่มกดไม่ได้ + Wallet บอกหมดอายุ', async () => {
    await logoutUI(page); await loginUI(page, 'U05');
    await open(page, '/wallet');
    await expect.soft(page.getByTestId('course-book-C04')).toBeDisabled();
    await expect.soft(page.getByTestId('course-expired-C04')).toBeVisible();
  });
  let u07: Api;
  await S('U07 C02 นัด 21 ต.ค. (หลังหมดอายุ 20 ต.ค.) → ❌', async () => {
    u07 = await api.as('U07');
    const r = await u07.post('/api/bookings', courseBooking('2026-10-21', '11:00'));
    expect.soft(r.status >= 400 && r.status < 500, `21 ต.ค. ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  });
  await S('U07 C02 นัด 20 ต.ค. (วันสุดท้าย) → ✅ ฿0', async () => {
    await logoutUI(page); await loginUI(page, 'U07');
    await bookWithCourse(page, 'C02', '2026-10-20', '11:00');
    expect.soft(await amount(page, 'summary-total')).toBe(0);
    await page.getByTestId('book-confirm').click();
    await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  });
});
