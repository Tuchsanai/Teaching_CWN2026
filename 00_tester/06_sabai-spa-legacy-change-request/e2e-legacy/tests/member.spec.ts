import { tc, test, expect, open, loginUI, logoutUI, bookToStep3, quoteTotal, settle, type UserKey } from './fixtures';

const S = test.step;

tc('TC-MEM-01', async ({ page }) => {
  const rows: [UserKey, string, string, string][] = [
    ['U04', '฿9,999', 'Silver', '0%'],
    ['U07', '฿10,000', 'Gold', '5%'],
    ['U05', '฿29,999', 'Gold', '5%'],
    ['U02', '฿30,000', 'Platinum', '10%'],
  ];
  for (const [u, spend, tier, pct] of rows) {
    await S(`${u} ยอดสะสม ${spend} → ${tier} ${pct}`, async () => {
      await logoutUI(page);
      await loginUI(page, u);
      await open(page, '/account');
      await expect.soft(page.getByTestId('account-tier')).toContainText(tier);
      await expect.soft(page.getByTestId('account-tier-pct')).toContainText(pct);
    });
  }
});

tc('TC-MEM-02', async ({ page }) => {
  const rows: [UserKey, string][] = [
    ['U04', 'อีก ฿1 ถึง Gold'],
    ['U07', 'อีก ฿20,000 ถึง Platinum'],
    ['U06', 'อยู่ระดับสูงสุดแล้ว'],
  ];
  for (const [u, msg] of rows) {
    await S(`${u} → "${msg}"`, async () => {
      await logoutUI(page);
      await loginUI(page, u);
      await open(page, '/account');
      await expect.soft(page.getByTestId('account-tier-message')).toContainText(msg);
      if (u === 'U06') await expect.soft(page.locator('main')).not.toContainText(/[−-]\s*฿\s*15,000/);
    });
  }
});

tc('TC-MEM-03', async ({ page, api }) => {
  const s01 = { service: 'S01', type: 'single' as const, date: '2026-10-20', time: '10:00' };
  await S('U01 (99 แต้ม) → ช่องแลกแต้มกดไม่ได้', async () => {
    await loginUI(page, 'U01');
    await bookToStep3(page, s01);
    await settle(page, () => page.getByTestId('book-points-info').innerText().catch(() => ''));
    await expect.soft(page.getByTestId('book-points')).toBeDisabled();
  });
  await S('U05 (100 แต้ม) แลก 1 ก้อน → ฿1,000 − 5% − ฿50 = ฿900', async () => {
    await logoutUI(page); await loginUI(page, 'U05');
    await bookToStep3(page, s01);
    await page.getByTestId('book-points').selectOption('1');
    expect.soft(await quoteTotal(page)).toBe(900);
  });
  await S('U06 (199 แต้ม) แลก 2 ก้อน → ❌', async () => {
    await logoutUI(page); await loginUI(page, 'U06');
    await bookToStep3(page, s01);
    await settle(page, () => page.getByTestId('book-points-info').innerText().catch(() => ''));
    const opts = await page.getByTestId('book-points').locator('option').evaluateAll((o) => o.map((x) => (x as HTMLOptionElement).value));
    expect.soft(opts, 'ตัวเลือกแลกแต้มของ U06').not.toContain('2');
    const u06 = await api.as('U06');
    const r = await u06.post('/api/price', { type: 'single', serviceCode: 'S01', people: 1, date: '2026-10-20', time: '10:00', redeemBlocks: 2 });
    expect.soft(r.status >= 400 && r.status < 500, `API แลก 2 ก้อน ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  });
  await S('U04 (250 แต้ม) ตัวเลือกสูงสุด 2 ครั้ง · แลก 3 ก้อน → ❌', async () => {
    await logoutUI(page); await loginUI(page, 'U04');
    await bookToStep3(page, s01);
    await settle(page, () => page.getByTestId('book-points-info').innerText().catch(() => ''));
    const opts = (await page.getByTestId('book-points').locator('option').evaluateAll((o) => o.map((x) => (x as HTMLOptionElement).value)))
      .map(Number).filter((n) => !Number.isNaN(n));
    expect.soft(Math.max(...opts), 'ตัวเลือกสูงสุดของ U04').toBe(2);
    const u04 = await api.as('U04');
    const r = await u04.post('/api/price', { type: 'single', serviceCode: 'S01', people: 1, date: '2026-10-20', time: '10:00', redeemBlocks: 3 });
    expect.soft(r.status >= 400 && r.status < 500, `API แลก 3 ก้อน ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  });
});

tc('TC-MEM-04', async ({ page, api }) => {
  await S('ก่อนกด: แต้ม U01 = 99', async () => {
    const u01 = await api.as('U01');
    expect.soft((await u01.get('/api/me')).json.points).toBe(99);
  });
  await S('owner เปิด /admin แล้วกด "ใช้บริการเสร็จ" ที่ B06 (วันนี้ 15:00)', async () => {
    await loginUI(page, 'owner');
    await open(page, '/admin');
    // 👀 ช่องวันที่ของ /admin เปิดมาเป็น 11 ต.ค. ทั้งที่ "วันนี้ของระบบ" = 10 ต.ค. → เลือกวันที่เองให้ตรงกับ B06
    await page.getByTestId('admin-date').fill('2026-10-10');
    await page.getByTestId('admin-complete-B06').click();
    await expect.soft(page.getByTestId('admin-result-B06')).toBeVisible();
  });
  await S('หลังรีโหลด /account ของ U01: แต้ม 99 + floor(950 ÷ 100) = 108', async () => {
    await logoutUI(page);
    await loginUI(page, 'U01');
    await open(page, '/account');
    await expect.soft(page.getByTestId('account-points')).toHaveAttribute('data-points', '108');
  });
});
