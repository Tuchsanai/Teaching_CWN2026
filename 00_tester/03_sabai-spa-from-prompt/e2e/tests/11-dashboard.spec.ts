import { test, expect, open, pause, loginByApi, money, note, PASSWORD, USERS } from './fixtures';

test.describe('หน้าบัญชี', () => {
  test('TC-DASH-01 หน้าสมาชิก (/account): ระดับ แต้ม ประวัติ กราฟรอบเอว รูปก่อน/หลัง และข้อมูลข้ามบัญชี', {
    tag: ['@DASH', '@P2'],
    annotation: [
      {
        type: 'expected',
        description:
          'นิดา: member-tier "gold" · member-points 124 · member-spent ฿12,400 · member-next-tier "อีก ฿17,600 ถึงระดับ Platinum" · upcoming-list มี booking-item-SB00006 (2026-10-09 15:00 นวดไทย มาลี) · ' +
          'waist-point-* data-cm 82, 80.5, 79, 78 · waist-drop "ลดลง 4 ซม. จากครั้งแรก" · history-row-0–4 = 5 แถว เรียงจากล่าสุด · มี photo-before, photo-after · logout แล้วเปิด /account → account-need-login · ' +
          'ต้นไม่เห็น SB00006 กราฟรอบเอว หรือรูปของนิดา (NFR-08) · ต้นยกเลิกนัดของนิดาต้องไม่สำเร็จ',
      },
      { type: 'note', description: '"ไม่เห็นใบหน้าในรูป" ต้องตรวจด้วยตา — ดูจาก GIF/MP4 ของ TC นี้' },
    ],
  }, async ({ page, playwright, baseURL, apiLog }) => {
    await loginByApi(page.request, 'nida');
    await open(page, '/account');
    await expect.soft(page.getByTestId('member-tier')).toHaveAttribute('data-tier', 'gold');
    await expect.soft(page.getByTestId('member-points')).toHaveText('124');
    expect.soft(money(await page.getByTestId('member-spent').textContent())).toBe(12400);
    await expect.soft(page.getByTestId('member-next-tier')).toHaveText('อีก ฿17,600 ถึงระดับ Platinum');

    const appt = page.getByTestId('upcoming-list').getByTestId('booking-item-SB00006');
    await appt.scrollIntoViewIfNeeded();
    await expect(appt).toBeVisible();
    await expect.soft(appt).toContainText('15:00');
    await expect.soft(appt).toContainText('นวดไทย');
    await expect.soft(appt).toContainText('มาลี');
    const api = (await (await page.request.get('/api/bookings')).json()).bookings as { code: string; date: string; time: string }[];
    expect.soft(api.find((b) => b.code === 'SB00006'), 'SB00006 = 2026-10-09 15:00').toMatchObject({ date: '2026-10-09', time: '15:00' });
    await pause(page);

    await page.getByTestId('waist-chart').scrollIntoViewIfNeeded();
    const cms = await page.getByTestId('waist-chart').getByTestId(/^waist-point-\d+$/).evaluateAll((g) => g.map((x) => Number(x.getAttribute('data-cm'))));
    expect.soft(cms, 'รอบเอว').toEqual([82, 80.5, 79, 78]);
    await expect.soft(page.getByTestId('waist-drop')).toHaveText('ลดลง 4 ซม. จากครั้งแรก');
    await expect.soft(page.getByTestId('photo-before')).toBeVisible();
    await expect.soft(page.getByTestId('photo-after')).toBeVisible();
    await pause(page);

    const rows = page.getByTestId('history-list').getByTestId(/^history-row-\d+$/);
    await rows.first().scrollIntoViewIfNeeded();
    await expect(rows).toHaveCount(5);
    const dates = await rows.evaluateAll((tr) => tr.map((x) => x.getAttribute('data-date') ?? ''));
    expect.soft(dates, 'ประวัติเรียงจากล่าสุดก่อน').toEqual([...dates].sort().reverse());
    await pause(page);

    // logout → /account ต้องให้ login
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.getByTestId('nav-logout').click();
    await expect(page.getByTestId('nav-login')).toBeVisible();
    await expect(page).toHaveURL(baseURL + '/'); // logout พากลับหน้าแรก (router.push) — รอให้เสร็จก่อนเปิดหน้าใหม่
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    await open(page, '/account');
    await expect(page.getByTestId('account-need-login')).toBeVisible();
    await pause(page);

    // ต้นต้องไม่เห็นข้อมูลของนิดา
    await loginByApi(page.request, 'ton');
    await open(page, '/account');
    await expect(page.getByTestId('member-tier')).toHaveAttribute('data-tier', 'platinum');
    await expect.soft(page.getByTestId('booking-item-SB00006')).toHaveCount(0);
    await expect.soft(page.getByTestId('waist-chart')).toHaveCount(0);
    await expect.soft(page.getByTestId('photo-before')).toHaveCount(0);
    await expect.soft(page.getByTestId('photo-after')).toHaveCount(0);
    await pause(page);
    await open(page, '/wallet');
    await expect.soft(page.getByTestId('course-card')).toBeVisible();
    await expect.soft(page.getByTestId('course-remaining').filter({ hasText: 'เหลือ 7 จาก 11 ครั้ง' }), 'ต้นต้องไม่เห็นคอร์สของนิดา (เหลือ 7 จาก 11)').toHaveCount(0);

    const cancel = await apiLog.call(page.request, 'POST', '/api/bookings/6/cancel', undefined, 'login เป็น ton');
    expect.soft(cancel.body?.ok, 'ต้นยกเลิกนัดของนิดาต้องไม่สำเร็จ').toBe(false);
    note(`ต้องถาม #12: ต้นยกเลิกนัดของนิดา ได้ HTTP ${cancel.status} · ${JSON.stringify(cancel.body)}`, 'ต้องถาม');

    // นัดของนิดายังอยู่
    const nida = await playwright.request.newContext({ baseURL });
    await nida.post('/api/auth/login', { data: { email: USERS.nida, password: PASSWORD } });
    const still = ((await (await nida.get('/api/bookings')).json()).bookings as { code: string; status: string }[]).find((b) => b.code === 'SB00006');
    expect(still?.status, 'SB00006 ต้องยัง confirmed').toBe('confirmed');
    await nida.dispose();
  });
});
