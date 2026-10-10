import { test, expect, open, pause, note, loginByApi, setMember, slot, slotStatus, expectMoney, bookingBody, USERS } from './fixtures';
import { FIXED_NOW } from '../global-setup';
import type { APIRequestContext, Page } from '@playwright/test';

/**
 * TC ที่ต้อง "ย้ายเวลาเว็บ" (R(…) ใน TEST-PLAN) — reset ฐานข้อมูลด้วยเวลาอื่น
 * project "time-travel" รันไฟล์นี้ทีละข้อ หลัง chromium / firefox / webkit รันจบทั้งหมดแล้ว (teardown ของ setup)
 * จึง reset ได้โดยไม่ล้างข้อมูลของเบราว์เซอร์อื่น · จบไฟล์แล้ว reset กลับเป็น R0
 */
test.describe.configure({ mode: 'default' });

async function resetAt(request: APIRequestContext, now: string) {
  const r = await request.post('/api/test/reset', { data: { now } });
  expect(r.status(), await r.text()).toBe(200);
  return r.json();
}

/** แสดงเดือนของวันนั้นในปฏิทิน (ไม่กดวัน) · คืน false ถ้าไปถึงเดือนนั้นไม่ได้เพราะปุ่มเดือนถัดไปถูกปิด */
async function showMonth(page: Page, date: string) {
  const day = page.getByTestId(`cal-day-${date}`);
  for (let i = 0; i < 3 && !(await day.isVisible()); i++) {
    const next = page.getByTestId('cal-next');
    if (await next.isDisabled()) return false;
    await next.click();
  }
  return day.isVisible();
}

test.afterAll(async ({ playwright, baseURL }) => {
  const ctx = await playwright.request.newContext({ baseURL });
  await resetAt(ctx, FIXED_NOW);
  await ctx.dispose();
});

test.describe('ย้ายเวลาเว็บ (รันทีละข้อหลังทุกเบราว์เซอร์)', () => {
  test('TC-BOOK-03 ปฏิทินกดได้เฉพาะ +1 ถึง +30 วัน รวมกรณีข้ามเดือน', {
    tag: ['@BOOK', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'R0: cal-day-2026-10-08 disabled · cal-day-2026-10-09 กดได้ · cal-day-2026-11-07 กดได้ · cal-day-2026-11-08 disabled · GET /api/config → bookable.from "2026-10-09" bookable.to "2026-11-07" · ' +
          'POST /api/bookings date 2026-10-08 และ 2026-11-08 → DATE_OUT_OF_RANGE "จองได้ตั้งแต่พรุ่งนี้ถึง 30 วันข้างหน้าเท่านั้น" · R(2026-10-31T10:00:00+07:00): cal-day-2026-11-30 กดได้ · cal-day-2026-12-01 disabled',
      },
      { type: 'note', description: 'รันใน project time-travel (chromium) หลังทุกเบราว์เซอร์ เพราะต้อง reset ด้วยเวลา 2026-10-31' },
    ],
  }, async ({ page, apiLog }) => {
    await resetAt(page.request, FIXED_NOW);
    await open(page, '/book');
    await page.getByTestId('service-option-thai-massage').click();
    await expect(page.getByTestId('cal-day-2026-10-08')).toBeDisabled();
    await expect(page.getByTestId('cal-day-2026-10-09')).toBeEnabled();
    await pause(page, 800);
    expect(await showMonth(page, '2026-11-07')).toBe(true);
    await expect(page.getByTestId('cal-day-2026-11-07')).toBeEnabled();
    await expect(page.getByTestId('cal-day-2026-11-08')).toBeDisabled();
    await pause(page, 800);

    const cfg = await apiLog.call(page.request, 'GET', '/api/config');
    expect.soft(cfg.body.bookable).toEqual({ from: '2026-10-09', to: '2026-11-07' });
    for (const date of ['2026-10-08', '2026-11-08']) {
      const r = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ date, time: '10:00' }));
      expect.soft(r.body, date).toMatchObject({ ok: false, error: 'DATE_OUT_OF_RANGE', message: 'จองได้ตั้งแต่พรุ่งนี้ถึง 30 วันข้างหน้าเท่านั้น' });
    }

    await resetAt(page.request, '2026-10-31T10:00:00+07:00');
    await open(page, '/book');
    await page.getByTestId('service-option-thai-massage').click();
    expect(await showMonth(page, '2026-11-30')).toBe(true);
    await expect(page.getByTestId('cal-day-2026-11-30')).toBeEnabled();
    await pause(page, 800);
    const dec1 = page.getByTestId('cal-day-2026-12-01');
    const reachable = await showMonth(page, '2026-12-01');
    if (reachable) await expect(dec1, '2026-12-01 ต้องกดไม่ได้').toBeDisabled();
    else note('R(2026-10-31): ปุ่มเดือนถัดไป (cal-next) ถูกปิด จึงไปถึงวันที่ 2026-12-01 ไม่ได้ = เลือกวันนั้นไม่ได้');
    await expect(page.getByTestId('cal-day-2026-11-30')).toBeVisible();
  });

  test('TC-MEM-04 ส่วนลดเดือนเกิด 20% ใช้ได้ 1 ครั้ง ไม่รวมกับส่วนลดระดับ และค่าขอบเดือน', {
    tag: ['@MEM', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'ต้น (Platinum เกิดเดือน ต.ค.) aroma-oil ฿1,500 1 คน 2026-10-09 12:00: มี booking-birthday · ติ๊กแล้ว price-birthday-discount −฿300 · ไม่มีส่วนลดระดับซ้อน · price-total ฿1,200 · price-points-earn 12 · ' +
          'จองแล้วเปิด /book ใหม่ → ไม่มี booking-birthday · quote useBirthday:true → BIRTHDAY_NOT_ELIGIBLE "ใช้ส่วนลดเดือนเกิดไม่ได้ (ไม่ใช่เดือนเกิด หรือใช้ไปแล้วปีนี้)" · ' +
          '30 ก.ย. ไม่มีตัวเลือก · 1 ต.ค. มี · 31 ต.ค. มี · 1 พ.ย. ไม่มี',
      },
      { type: 'note', description: 'รันใน project time-travel (chromium) หลังทุกเบราว์เซอร์ เพราะใช้ ton@sabai.test ตัวจริง และต้อง reset ด้วยเวลา 30 ก.ย. / 1 ต.ค. / 31 ต.ค. / 1 พ.ย.' },
    ],
  }, async ({ page, apiLog }) => {
    await resetAt(page.request, FIXED_NOW);
    await loginByApi(page.request, 'ton');
    await open(page, '/book');
    await page.getByTestId('service-option-aroma-oil').click();
    await page.getByTestId('cal-day-2026-10-09').click();
    await slot(page, '12:00').click();
    const bday = page.getByTestId('booking-birthday');
    await expect(bday).toBeVisible();
    await bday.check();
    await expectMoney(page.getByTestId('price-birthday-discount'), -300);
    await expectMoney(page.getByTestId('price-tier-discount'), 0);
    await expectMoney(page.getByTestId('price-total'), 1200);
    await expectMoney(page.getByTestId('price-points-earn'), 12);
    await pause(page);
    await page.getByTestId('booking-submit').click();
    await expect(page.getByTestId('booking-success')).toBeVisible();

    await open(page, '/book');
    await expect(page.getByTestId('booking-member')).toBeVisible();
    await expect(page.getByTestId('booking-birthday'), 'ใช้แล้วตัวเลือกต้องหายไป').toHaveCount(0);
    const q = await apiLog.call(page.request, 'POST', '/api/quote', {
      service: 'aroma-oil', people: 1, transport: false, hotelId: null, redeemSets: 0, useBirthday: true, payWith: 'cash', giftCode: null,
    });
    expect.soft(q.body.issues).toEqual(expect.arrayContaining([
      expect.objectContaining({ code: 'BIRTHDAY_NOT_ELIGIBLE', message: 'ใช้ส่วนลดเดือนเกิดไม่ได้ (ไม่ใช่เดือนเกิด หรือใช้ไปแล้วปีนี้)' }),
    ]));
    await pause(page);

    for (const [now, shown] of [
      ['2026-09-30T10:00:00+07:00', false], ['2026-10-01T10:00:00+07:00', true], ['2026-10-31T10:00:00+07:00', true], ['2026-11-01T10:00:00+07:00', false],
    ] as const) {
      await test.step(`วันนี้ = ${now.slice(0, 10)} → ${shown ? 'มี' : 'ไม่มี'}ตัวเลือกวันเกิด`, async () => {
        await resetAt(page.request, now);
        await setMember(page.request, USERS.ton, { birthMonth: 10, birthdayUsedYear: null });
        await loginByApi(page.request, 'ton');
        await open(page, '/book');
        await expect(page.getByTestId('booking-member')).toBeVisible();
        await expect.soft(page.getByTestId('booking-birthday'), now.slice(0, 10)).toHaveCount(shown ? 1 : 0);
        await pause(page, 600);
      });
    }
  });

  test('TC-DASH-02 ยกเลิกนัดเองได้เมื่อเหลือ ≥ 24 ชม. (ค่าขอบ 24 ชม. พอดี)', {
    tag: ['@DASH', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'นิดา SB00006 = 2026-10-09 15:00 · R(2026-10-08 14:59) และ R(15:00:00) → cancel-btn-SB00006 กดได้ · กดแล้ว cancel-success · availability thai-massage 2026-10-09 นักบำบัด 1 รอบ 15:00 = free · ' +
          'ยกเลิกซ้ำผ่าน API → ALREADY_CANCELLED "นัดนี้ถูกยกเลิกไปแล้ว" · R(15:01) → ปุ่ม disabled · cancel-blocked-SB00006 "เหลือน้อยกว่า 24 ชั่วโมง ยกเลิกเองไม่ได้ กรุณาติดต่อร้าน 02-123-4567" · API cancel → 409 CANCEL_TOO_LATE',
      },
      { type: 'note', description: 'รันใน project time-travel (chromium) หลังทุกเบราว์เซอร์ เพราะยกเลิก SB00006 ของ nida ตัวจริงและต้อง reset ด้วยเวลา 14:59 / 15:00 / 15:01' },
    ],
  }, async ({ page, apiLog }) => {
    for (const now of ['2026-10-08T14:59:00+07:00', '2026-10-08T15:00:00+07:00']) {
      await test.step(`ตอนนี้ ${now.slice(11, 16)} (เหลือ ≥ 24 ชม.) → ยกเลิกได้`, async () => {
        await resetAt(page.request, now);
        await loginByApi(page.request, 'nida');
        await open(page, '/account');
        const btn = page.getByTestId('cancel-btn-SB00006');
        await btn.scrollIntoViewIfNeeded();
        await expect(btn).toBeEnabled();
        await btn.click();
        await expect(page.getByTestId('cancel-success')).toBeVisible();
        await pause(page);
        expect.soft(await slotStatus(page.request, { service: 'thai-massage', date: '2026-10-09', therapistId: 1 }, '15:00'), 'รอบ 15:00 ต้องว่าง').toBe('free');
        const again = await apiLog.call(page.request, 'POST', '/api/bookings/6/cancel', undefined, `ยกเลิกซ้ำ ${now}`);
        expect.soft(again.body).toMatchObject({ ok: false, error: 'ALREADY_CANCELLED', message: 'นัดนี้ถูกยกเลิกไปแล้ว' });
      });
    }

    await test.step('ตอนนี้ 15:01 (เหลือน้อยกว่า 24 ชม.) → ยกเลิกไม่ได้', async () => {
      await resetAt(page.request, '2026-10-08T15:01:00+07:00');
      await loginByApi(page.request, 'nida');
      await open(page, '/account');
      const btn = page.getByTestId('cancel-btn-SB00006');
      await btn.scrollIntoViewIfNeeded();
      await expect(btn).toBeDisabled();
      await expect(page.getByTestId('cancel-blocked-SB00006')).toHaveText('เหลือน้อยกว่า 24 ชั่วโมง ยกเลิกเองไม่ได้ กรุณาติดต่อร้าน 02-123-4567');
      await pause(page);
      const r = await apiLog.call(page.request, 'POST', '/api/bookings/6/cancel', undefined, 'ตอนนี้ 15:01');
      expect.soft(r.status).toBe(409);
      expect.soft(r.body).toMatchObject({ ok: false, error: 'CANCEL_TOO_LATE' });
    });
  });
});
