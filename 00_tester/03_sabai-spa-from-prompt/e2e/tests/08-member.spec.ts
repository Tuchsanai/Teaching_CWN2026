import {
  test, expect, open, pause, createMember, setMember, fillBooking, expectMoney, money, bookingDate, DAY, NIDA_LIKE, TON_LIKE,
} from './fixtures';
import type { Page } from '@playwright/test';

const NOTE_CLONE = {
  type: 'note',
  description:
    'ใช้สมาชิกใหม่อีเมลไม่ซ้ำที่ตั้งยอด/แต้มให้เท่ากับผู้ใช้ในแผน (POST /api/test/user) แทนการแก้ nida / ton / new ตรง ๆ เพราะ 3 เบราว์เซอร์รันพร้อมกัน · วันจองแยกตามเบราว์เซอร์',
};

/** เปิด /book เลือก thai-massage 1 คน แล้วรอให้กล่องราคาขึ้น */
async function bookThai(page: Page) {
  await open(page, '/book');
  await page.getByTestId('service-option-thai-massage').click();
  await expect(page.getByTestId('price-summary')).toBeVisible();
}

test.describe('สมาชิก / แต้ม', () => {
  test('TC-MEM-01 ค่าขอบระดับสมาชิก ฿9,999 / ฿10,000 / ฿29,999 / ฿30,000 และส่วนลดตามระดับ', {
    tag: ['@MEM', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          '฿9,999 → member-tier "silver" · "อีก ฿1 ถึงระดับ Gold" · /book ไม่มีส่วนลดระดับ price-total ฿800 · ฿10,000 → "gold" · "อีก ฿20,000 ถึงระดับ Platinum" · price-tier-discount −฿40 → ฿760 · ' +
          '฿29,999 → "gold" · "อีก ฿1 ถึงระดับ Platinum" · ฿760 · ฿30,000 → "platinum" · "คุณอยู่ระดับสูงสุดแล้ว" · −฿80 → ฿720',
      },
      NOTE_CLONE,
    ],
  }, async ({ page }) => {
    const user = await createMember(page.request);
    const cases = [
      { spent: 9999, tier: 'silver', next: 'อีก ฿1 ถึงระดับ Gold', disc: 0, total: 800 },
      { spent: 10000, tier: 'gold', next: 'อีก ฿20,000 ถึงระดับ Platinum', disc: -40, total: 760 },
      { spent: 29999, tier: 'gold', next: 'อีก ฿1 ถึงระดับ Platinum', disc: -40, total: 760 },
      { spent: 30000, tier: 'platinum', next: 'คุณอยู่ระดับสูงสุดแล้ว', disc: -80, total: 720 },
    ];
    for (const c of cases) {
      await test.step(`ยอดสะสม ฿${c.spent.toLocaleString('en-US')} → ${c.tier}`, async () => {
        await setMember(page.request, user.email, { totalSpent: c.spent });
        await open(page, '/account');
        await expect.soft(page.getByTestId('member-tier')).toHaveAttribute('data-tier', c.tier);
        await expect.soft(page.getByTestId('member-next-tier')).toHaveText(c.next);
        await pause(page, 600);
        await bookThai(page);
        await expectMoney(page.getByTestId('price-tier-discount'), c.disc, `price-tier-discount ฿${c.spent}`);
        await expectMoney(page.getByTestId('price-total'), c.total, `price-total ฿${c.spent}`);
        await pause(page, 600);
      });
    }
  });

  test('TC-MEM-02 ได้แต้ม floor(ยอดสุทธิ/100) และยอดสะสมเพิ่ม', {
    tag: ['@MEM', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'Gold ฿12,400 · 124 แต้ม · thai-massage 1 คน ไม่แลกแต้ม ไม่ใช้รถ: price-tier-discount −฿40 · price-total ฿760 · price-points-earn 7 (ปัดทิ้ง 7.6 → 7) · หลังจองสำเร็จ member-points 131 · member-spent ฿13,160',
      },
      NOTE_CLONE,
      { type: 'ต้องถาม', description: '#11 ค่าขอบ ฿99 → 0, ฿100 → 1, ฿199 → 1 สร้างจากราคาบริการใน seed ไม่ได้ (บริการถูกสุด ฿600) — ไม่ได้ทดสอบ' },
    ],
  }, async ({ page, browserName }) => {
    await createMember(page.request, NIDA_LIKE);
    await bookThai(page);
    await fillBooking(page, { date: bookingDate(browserName, DAY.MEM), time: '11:00' });
    await expectMoney(page.getByTestId('price-tier-discount'), -40);
    await expectMoney(page.getByTestId('price-total'), 760);
    await expectMoney(page.getByTestId('price-points-earn'), 7);
    await pause(page);
    await page.getByTestId('booking-submit').click();
    await expect(page.getByTestId('booking-success')).toBeVisible();
    await open(page, '/account');
    await expect(page.getByTestId('member-points')).toHaveText('131');
    expect(money(await page.getByTestId('member-spent').textContent())).toBe(13160);
  });

  test('TC-MEM-03 แลกแต้ม 100 แต้ม = ฿50 ค่าขอบ 99 / 100 / 250 แต้ม หักแต้มทันที', {
    tag: ['@MEM', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          '(ก) Gold 124 แต้ม thai-massage แลก 1 ชุด: booking-redeem-max 1 · price-points-discount −฿50 · price-total ฿710 · ได้ 7 แต้ม → member-points 31 · member-spent ฿13,110 · ' +
          '(ข) 99 แต้ม: booking-redeem disabled · POST /api/quote redeemSets:1 → issues มี POINTS_NOT_ENOUGH "แต้มไม่พอสำหรับแลกส่วนลด" · ' +
          '(ค) Platinum 250 แต้ม แลก 2 ชุด: booking-redeem-max 2 · ส่วนลด −฿100 · price-total ฿620 · member-points 56',
      },
      NOTE_CLONE,
    ],
  }, async ({ page, browserName, apiLog }) => {
    const date = bookingDate(browserName, DAY.MEM);

    await test.step('(ก) 124 แต้ม แลกได้สูงสุด 1 ชุด', async () => {
      await createMember(page.request, NIDA_LIKE);
      await bookThai(page);
      await fillBooking(page, { date, time: '13:00' });
      await page.getByTestId('booking-redeem-max').click();
      await expect(page.getByTestId('booking-redeem')).toHaveValue('1');
      await expect(page.getByTestId('booking-redeem').locator('option')).toHaveCount(2); // 0 หรือ 1 ชุด
      await expectMoney(page.getByTestId('price-points-discount'), -50);
      await expectMoney(page.getByTestId('price-total'), 710);
      await expectMoney(page.getByTestId('price-points-earn'), 7);
      await pause(page);
      await page.getByTestId('booking-submit').click();
      await expect(page.getByTestId('booking-success')).toBeVisible();
      await open(page, '/account');
      await expect.soft(page.getByTestId('member-points')).toHaveText('31');
      expect.soft(money(await page.getByTestId('member-spent').textContent())).toBe(13110);
    });

    await test.step('(ข) 99 แต้ม แลกไม่ได้', async () => {
      await createMember(page.request, { ...NIDA_LIKE, points: 99 });
      await bookThai(page);
      await expect.soft(page.getByTestId('booking-redeem')).toBeDisabled();
      const q = await apiLog.call(page.request, 'POST', '/api/quote', {
        service: 'thai-massage', people: 1, transport: false, hotelId: null, redeemSets: 1, useBirthday: false, payWith: 'cash', giftCode: null,
      });
      expect.soft(q.body.issues, 'issues').toEqual(expect.arrayContaining([expect.objectContaining({ code: 'POINTS_NOT_ENOUGH', message: 'แต้มไม่พอสำหรับแลกส่วนลด' })]));
      await pause(page, 600);
    });

    await test.step('(ค) Platinum 250 แต้ม แลกได้สูงสุด 2 ชุด', async () => {
      await createMember(page.request, TON_LIKE);
      await bookThai(page);
      await fillBooking(page, { date, time: '15:00' });
      await page.getByTestId('booking-redeem-max').click();
      await expect(page.getByTestId('booking-redeem')).toHaveValue('2');
      await expectMoney(page.getByTestId('price-tier-discount'), -80);
      await expectMoney(page.getByTestId('price-points-discount'), -100);
      await expectMoney(page.getByTestId('price-total'), 620);
      await pause(page);
      await page.getByTestId('booking-submit').click();
      await expect(page.getByTestId('booking-success')).toBeVisible();
      await open(page, '/account');
      await expect.soft(page.getByTestId('member-points')).toHaveText('56');
    });
  });
});
