import { tc, test, expect, bookToStep3, toSummary, amount, loginUI, logoutUI, quoteTotal, open } from './fixtures';

const S = test.step;

tc('TC-PRICE-01', async ({ page }) => {
  await loginUI(page, 'U08');
  for (const [n, want, how] of [[3, 3000, 'ไม่ลด'], [4, 3600, '฿4,000 − ฿400'], [5, 4500, '฿5,000 − ฿500']] as const) {
    await S(`กลุ่ม ${n} คน S01 → ฿${want.toLocaleString('en-US')} (${how})`, async () => {
      await bookToStep3(page, { service: 'S01', type: 'group', people: n, date: '2026-10-20', time: '10:00' });
      expect.soft(await quoteTotal(page), `กลุ่ม ${n} คน`).toBe(want);
      await toSummary(page);
      expect.soft(await amount(page, 'summary-total'), `ใบสรุปกลุ่ม ${n} คน`).toBe(want);
    });
  }
});

tc('TC-PRICE-02', async ({ page }) => {
  await S('U01 (Gold 5%) กลุ่ม 4 คน → max(10%, 5%) = ฿3,600', async () => {
    await loginUI(page, 'U01');
    await bookToStep3(page, { service: 'S01', type: 'group', people: 4, date: '2026-10-20', time: '10:00' });
    expect.soft(await quoteTotal(page)).toBe(3600);
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(3600);
  });
  await S('U02 (Platinum + เดือนเกิด) กลุ่ม 4 คน 31 ต.ค. เลือกเดือนเกิด → 20% = ฿3,200', async () => {
    await logoutUI(page);
    await loginUI(page, 'U02');
    await bookToStep3(page, { service: 'S01', type: 'group', people: 4, date: '2026-10-31', time: '10:00' });
    await page.getByTestId('book-birthday').check();
    expect.soft(await quoteTotal(page)).toBe(3200);
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(3200);
  });
});

tc('TC-PRICE-03', async ({ page }) => {
  await loginUI(page, 'U02');
  await S('U02 นัด 20 ต.ค. ใช้เดือนเกิด → ฿1,000 − 20% = ฿800', async () => {
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
    await page.getByTestId('book-birthday').check();
    expect.soft(await quoteTotal(page)).toBe(800);
  });
  await S('U02 นัด 1 พ.ย. → ใช้เดือนเกิดไม่ได้ ราคา ฿900', async () => {
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-11-01', time: '10:00' });
    await expect.soft(page.getByTestId('book-birthday')).toHaveCount(0);
    expect.soft(await quoteTotal(page)).toBe(900);
  });
  await S('U05 (ใช้สิทธิ์ ต.ค. แล้ว) S07 นัด 20 ต.ค. → ไม่มีตัวเลือกเดือนเกิด ราคา ฿1,710', async () => {
    await logoutUI(page);
    await loginUI(page, 'U05');
    await bookToStep3(page, { service: 'S07', type: 'single', date: '2026-10-20', time: '10:00' });
    await expect.soft(page.getByTestId('book-birthday')).toHaveCount(0);
    expect.soft(await quoteTotal(page)).toBe(1710);
  });
});

tc('TC-PRICE-04', async ({ page }) => {
  await loginUI(page, 'U04');
  await S('U04 กลุ่ม 4 คน S01 · แลก 2 ก้อน · รถจาก H04 (12 กม.)', async () => {
    await bookToStep3(page, { service: 'S01', type: 'group', people: 4, date: '2026-10-20', time: '10:00' });
    await page.getByTestId('book-points').selectOption('2');
    await page.getByTestId('book-transport').check();
    await page.getByTestId('book-hotel').selectOption('H04');
  });
  await S('ยอด ฿4,000 − ฿400 − ฿100 + ฿300 = ฿3,800 · บรรทัดค่ารถ "1 คัน" (ทันที)', async () => {
    expect.soft(await quoteTotal(page)).toBe(3800);
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(3800);
    await expect.soft(page.getByTestId('summary-line-transport')).toContainText('1 คัน');
  });
  await S('ยืนยัน → หลังรีโหลด /account แต้มเหลือ 50', async () => {
    await page.getByTestId('book-confirm').click();
    await expect(page.getByTestId('booking-confirmation')).toBeVisible();
    await open(page, '/account');
    await expect.soft(page.getByTestId('account-points')).toHaveAttribute('data-points', '50');
  });
});

tc('TC-PRICE-05', async ({ page, api }) => {
  await loginUI(page, 'U01');
  let code = '';
  await S('U01 (Gold) S04 22 ต.ค. 13:00 + รถ H04 → ใบสรุป ฿2,200', async () => {
    await bookToStep3(page, { service: 'S04', type: 'single', date: '2026-10-22', time: '13:00' });
    await page.getByTestId('book-transport').check();
    await page.getByTestId('book-hotel').selectOption('H04');
    expect.soft(await quoteTotal(page)).toBe(2200);
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(2200);
  });
  await S('ยืนยัน → นัดที่บันทึก = ฿2,200 (หลังรีโหลด /api/me/bookings)', async () => {
    await page.getByTestId('book-confirm').click();
    code = (await page.getByTestId('booking-confirmation').innerText()).match(/B\d+/)?.[0] ?? '';
    const u01 = await api.as('U01');
    const list = (await u01.get('/api/me/bookings')).json.bookings as any[];
    expect.soft(list.find((b) => b.code === code)?.total, `นัด ${code}`).toBe(2200);
  });
  await S('ยิง /api/bookings ด้วย quotedTotal = 1 → 409 (ทันที) และไม่มีนัดใหม่ (หลังรีโหลด)', async () => {
    const u01 = await api.as('U01');
    const before = ((await u01.get('/api/me/bookings')).json.bookings as any[]).length;
    const r = await u01.post('/api/bookings', { type: 'single', serviceCode: 'S04', people: 1, date: '2026-10-22', time: '13:00', hotelCode: 'H04', quotedTotal: 1 });
    expect.soft(r.status).toBe(409);
    const after = ((await u01.get('/api/me/bookings')).json.bookings as any[]).length;
    expect.soft(after).toBe(before);
  });
});

tc('TC-PRICE-06', async ({ page }) => {
  await loginUI(page, 'U02');
  const pkg = (people: number) => bookToStep3(page, { type: 'package', service: 'P01', people, date: '2026-10-20', time: '10:00' });
  await S('1 คน → ฿2,900 และไม่มีตัวเลือกเดือนเกิด', async () => {
    await pkg(1);
    await expect.soft(page.getByTestId('book-birthday')).toHaveCount(0);
    expect.soft(await quoteTotal(page)).toBe(2900);
  });
  await S('2 คน + รถ H04 → ฿5,800 (รถรวมแล้ว ฿0)', async () => {
    await pkg(2);
    await page.getByTestId('book-transport').check();
    await page.getByTestId('book-hotel').selectOption('H04');
    expect.soft(await quoteTotal(page)).toBe(5800);
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(5800);
  });
  await S('4 คน → ฿11,600 (ไม่ลดกลุ่ม) — ดูราคาที่หน้า /package และ /api/price', async () => {
    // P01 ทำได้แค่ T01 T02 T06 (3 คน) หน้า /book จึงไม่มีรอบว่างสำหรับ 4 คน → ดูราคาจากเครื่องคิดเงินของหน้าแพ็กเกจแทน
    await open(page, '/package');
    const ppl = page.getByTestId('package-people');
    if (await ppl.evaluate((e) => e.tagName === 'SELECT')) await ppl.selectOption('4'); else await ppl.fill('4');
    await expect.soft(page.getByTestId('package-total')).toHaveAttribute('data-amount', '11600');
    const r = await page.request.post('/api/price', { data: { type: 'package', serviceCode: 'P01', people: 4, date: '2026-10-20', time: '10:00' } });
    expect.soft((await r.json()).total, 'POST /api/price แพ็กเกจ 4 คน (U02)').toBe(11600);
  });
  await S('2 คน + รถ H06 (15.1 กม.) → ❌ "อยู่นอกพื้นที่รับส่ง"', async () => {
    await pkg(2);
    await page.getByTestId('book-transport').check();
    await page.getByTestId('book-hotel').selectOption('H06');
    await expect.soft(page.getByTestId('book-quote-error-message')).toContainText('อยู่นอกพื้นที่รับส่ง');
  });
});
