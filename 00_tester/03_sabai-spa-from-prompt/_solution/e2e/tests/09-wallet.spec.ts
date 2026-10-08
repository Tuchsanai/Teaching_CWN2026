import { test, expect, open, pause, createMember, setMember, pickDate, slot, expectMoney, money, bookingBody, bookingDate, DAY, NIDA_LIKE } from './fixtures';
import type { Page } from '@playwright/test';

const NOTE_CLONE = {
  type: 'note',
  description:
    'ใช้สมาชิกใหม่อีเมลไม่ซ้ำที่ซื้อคอร์สแล้วตั้งค่าเหมือนนิดา (Gold ฿12,400 · 124 แต้ม · คอร์สใช้ไป 4) ผ่าน POST /api/test/user แทนการแก้ nida ตรง ๆ เพราะ 3 เบราว์เซอร์รันพร้อมกัน · วันจองแยกตามเบราว์เซอร์',
};
const COURSE_EMPTY = 'คอร์สเหลือ 0 ครั้ง จองด้วยคอร์สไม่ได้';
const COURSE_EXPIRED = 'คอร์สหมดอายุแล้ว จองด้วยคอร์สไม่ได้';

/** /wallet → course-book → เลือกวัน/รอบ → ยืนยัน · คืนรหัสจอง */
async function bookWithCourse(page: Page, date: string, time: string) {
  await open(page, '/wallet');
  await page.getByTestId('course-book').click();
  await expect(page).toHaveURL(/\/book\?service=body-contouring&pay=course/);
  await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
  await expect(page.getByTestId('booking-pay-course')).toHaveAttribute('aria-checked', 'true');
  await pickDate(page, date);
  await slot(page, time).click();
}

test.describe('Wallet / คอร์ส', () => {
  test('TC-WAL-01 จองด้วยคอร์สแล้วครั้งลด และยกเลิกแล้วคืนครั้ง', {
    tag: ['@WAL', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'ก่อนจอง course-remaining "เหลือ 7 จาก 11 ครั้ง" (data-left 7) · price-course คอร์สจ่าย ฿1,500 · price-total ฿0 · price-points-earn 0 · จองสำเร็จ → /wallet data-left 6 · ' +
          'member-points ยังเป็น 124 · member-spent ยังเป็น ฿12,400 · ยกเลิกนัดนี้ (เหลือ > 24 ชม.) → data-left กลับเป็น 7',
      },
      NOTE_CLONE,
    ],
  }, async ({ page, browserName }) => {
    await createMember(page.request, { ...NIDA_LIKE, course: { used: 4 } });
    await open(page, '/wallet');
    await expect(page.getByTestId('course-remaining')).toHaveText('เหลือ 7 จาก 11 ครั้ง');
    await expect(page.getByTestId('course-remaining')).toHaveAttribute('data-left', '7');
    await pause(page);

    await bookWithCourse(page, bookingDate(browserName, DAY.WAL), '10:00');
    await expectMoney(page.getByTestId('price-course'), -1500);
    await expectMoney(page.getByTestId('price-total'), 0);
    await expectMoney(page.getByTestId('price-points-earn'), 0);
    await pause(page);
    await page.getByTestId('booking-submit').click();
    await expect(page.getByTestId('booking-success')).toBeVisible();
    const code = (await page.getByTestId('booking-code').textContent())!.trim();

    await open(page, '/wallet');
    await expect(page.getByTestId('course-remaining')).toHaveAttribute('data-left', '6');
    await open(page, '/account');
    await expect.soft(page.getByTestId('member-points')).toHaveText('124');
    expect.soft(money(await page.getByTestId('member-spent').textContent())).toBe(12400);

    await page.getByTestId(`cancel-btn-${code}`).click();
    await expect(page.getByTestId('cancel-success')).toBeVisible();
    await pause(page);
    await open(page, '/wallet');
    await expect(page.getByTestId('course-remaining')).toHaveAttribute('data-left', '7');
  });

  test('TC-WAL-02 คอร์สเหลือ 1 → 0 แล้วจองด้วยคอร์สไม่ได้ และใช้ได้เฉพาะ body-contouring 1 คน', {
    tag: ['@WAL', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'เหลือ 1 → จองได้ แล้ว data-left 0 · เหลือ 0 → course-book disabled · /book booking-pay-course disabled · booking-issue-COURSE_EMPTY "' + COURSE_EMPTY + '" · ' +
          'API payWith:"course" → error COURSE_EMPTY · thai-massage + คอร์ส → COURSE_NOT_APPLICABLE "คอร์สใช้ได้กับบริการกระชับสัดส่วน 1 คนเท่านั้น"',
      },
      NOTE_CLONE,
    ],
  }, async ({ page, browserName, apiLog }) => {
    const date = bookingDate(browserName, DAY.WAL);
    const user = await createMember(page.request, { ...NIDA_LIKE, course: { used: 10 } });

    // คอร์สยังเหลือ 1: ใช้กับนวดไทยไม่ได้ (ตรวจก่อนใช้ครั้งสุดท้าย เพื่อแยกจาก COURSE_EMPTY)
    const na = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ service: 'thai-massage', date, time: '16:00', payWith: 'course', guestName: undefined, guestPhone: undefined }));
    expect.soft(na.body, 'thai-massage + คอร์ส').toMatchObject({ ok: false, error: 'COURSE_NOT_APPLICABLE', message: 'คอร์สใช้ได้กับบริการกระชับสัดส่วน 1 คนเท่านั้น' });

    await open(page, '/wallet');
    await expect(page.getByTestId('course-remaining')).toHaveAttribute('data-left', '1');
    await bookWithCourse(page, date, '13:00');
    await page.getByTestId('booking-submit').click();
    await expect(page.getByTestId('booking-success')).toBeVisible();

    await open(page, '/wallet');
    await expect(page.getByTestId('course-remaining')).toHaveAttribute('data-left', '0');
    await expect(page.getByTestId('course-book')).toBeDisabled();
    await pause(page);

    await setMember(page.request, user.email, { courseUsed: 11 }); // ตามแผน: U{…"courseUsed":11}
    await open(page, '/book?service=body-contouring&pay=course');
    await expect(page.getByTestId('booking-pay-course')).toBeDisabled();
    await expect(page.getByTestId('booking-issue-COURSE_EMPTY')).toHaveText(COURSE_EMPTY);
    await pause(page);
    const empty = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ service: 'body-contouring', date, time: '18:00', payWith: 'course', guestName: undefined, guestPhone: undefined }));
    expect(empty.body).toMatchObject({ ok: false, error: 'COURSE_EMPTY' });
  });

  test('TC-WAL-03 ซื้อคอร์ส ฿15,000 ได้ 11 ครั้ง อายุ 180 วัน (ค่าขอบวันที่ 180 / 181)', {
    tag: ['@WAL', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'ก่อนซื้อ course-none · ซื้อแล้ว course-remaining "เหลือ 11 จาก 11 ครั้ง" · course-expires data-date "2027-04-06" · POST /api/courses → 201 price 15000 left 11 · ' +
          'ซื้อ 2026-04-11 → หมดอายุ 2026-10-08 (วันที่ 180) → course-book กดได้ · ซื้อ 2026-04-10 → หมดอายุ 2026-10-07 (วันที่ 181) → course-expired · course-book disabled · booking-issue-COURSE_EXPIRED "' + COURSE_EXPIRED + '"',
      },
      { type: 'note', description: 'ส่วนซื้อคอร์สใช้สมาชิกใหม่ (เหมือน new@sabai.test) · ส่วนวันหมดอายุใช้สมาชิกใหม่อีกคนที่มีคอร์สเดียว แล้วย้ายวันซื้อด้วย POST /api/test/user แทนการแก้ nida' },
    ],
  }, async ({ page, apiLog }) => {
    await test.step('ซื้อคอร์สที่ /wallet', async () => {
      await createMember(page.request);
      await open(page, '/wallet');
      await expect(page.getByTestId('course-none')).toBeVisible();
      await page.getByTestId('course-buy').click();
      await expect(page.getByTestId('course-buy-result')).toBeVisible();
      await expect(page.getByTestId('course-remaining')).toHaveText('เหลือ 11 จาก 11 ครั้ง');
      await expect(page.getByTestId('course-expires')).toHaveAttribute('data-date', '2027-04-06');
      await pause(page);
    });

    const user = await createMember(page.request);
    await test.step('POST /api/courses → 201', async () => {
      const r = await apiLog.call(page.request, 'POST', '/api/courses');
      expect(r.status).toBe(201);
      expect(r.body.course).toMatchObject({ price: 15000, left: 11 });
    });

    await test.step('ซื้อ 2026-04-11 → วันที่ 180 ยังใช้ได้', async () => {
      const r = await setMember(page.request, user.email, { coursePurchasedOn: '2026-04-11' });
      expect(r.course.expires_on).toBe('2026-10-08');
      await open(page, '/wallet');
      await expect(page.getByTestId('course-expired')).toHaveCount(0);
      await expect(page.getByTestId('course-book')).toBeEnabled();
      await expect(page.getByTestId('course-book')).toHaveAttribute('href', /pay=course/);
      await pause(page);
    });

    await test.step('ซื้อ 2026-04-10 → วันที่ 181 หมดอายุ', async () => {
      const r = await setMember(page.request, user.email, { coursePurchasedOn: '2026-04-10' });
      expect(r.course.expires_on).toBe('2026-10-07');
      await open(page, '/wallet');
      await expect(page.getByTestId('course-expired')).toBeVisible();
      await expect(page.getByTestId('course-book')).toBeDisabled();
      await pause(page);
      await open(page, '/book?service=body-contouring&pay=course');
      await expect(page.getByTestId('booking-issue-COURSE_EXPIRED')).toHaveText(COURSE_EXPIRED);
    });
  });
});
