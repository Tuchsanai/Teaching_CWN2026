import { tc, test, expect, open, loginUI, bookToStep3, toSummary, amount, TODAY } from './fixtures';

const S = test.step;

tc('TC-CXL-01', async ({ page, api }) => {
  await loginUI(page, 'U01');
  await S('B05 (11 ต.ค. 10:00 เหลือ 24:00 ชม. พอดี) → ปุ่มยกเลิกกดได้ (ทันที)', async () => {
    await open(page, '/account');
    await expect.soft(page.getByTestId('cancel-B05')).toBeEnabled();
    await page.getByTestId('cancel-B05').click();
    await page.getByTestId('cancel-confirm-B05').click();
    await expect.soft(page.getByTestId('cancel-result-B05')).toBeVisible();
  });
  await S('หลังรีโหลด /account: สถานะ B05 = "ยกเลิก"', async () => {
    await open(page, '/account');
    await expect.soft(page.getByTestId('booking-status-B05')).toHaveText(/ยกเลิก/);
  });
  await S('หลังรีโหลด GET /api/slots: รอบ S05 11 ต.ค. 10:00 มี T04 ว่างกลับมา', async () => {
    const anon = await api.anon();
    const r = await anon.get('/api/slots?service=S05&date=2026-10-11&type=single&people=1');
    const slot = (r.json?.slots as any[] | undefined)?.find((s) => s.time === '10:00');
    expect.soft(slot?.therapists?.map((t: any) => t.code) ?? []).toContain('T04');
  });
});

tc('TC-CXL-02', async ({ page, api }) => {
  await S('เลื่อน TODAY เป็น 2026-10-10 10:01 (B05 เหลือ 23:59 ชม.)', async () => {
    await api.reset('2026-10-10T10:01:00+07:00');
  });
  try {
    await S('B05 ปุ่มยกเลิกกดไม่ได้ + ข้อความให้โทรหาร้านพร้อมเบอร์', async () => {
      await loginUI(page, 'U01');
      await open(page, '/account');
      await expect.soft(page.getByTestId('cancel-B05')).toBeDisabled();
      await expect.soft(page.getByTestId('cancel-blocked-B05')).toContainText('โทรหาร้าน');
      await expect.soft(page.getByTestId('cancel-phone-B05')).toHaveText(/\d{2,3}-?\d{3}-?\d{4}/);
    });
    await S('ยิง API ยกเลิก B05 → 4xx (ทันที) · หลังรีโหลดสถานะยัง "ยืนยัน"', async () => {
      const u01 = await api.as('U01');
      const r = await u01.post('/api/bookings/B05/cancel');
      expect.soft(r.status >= 400 && r.status < 500, `ต้อง 4xx (ได้ ${r.status})`).toBe(true);
      await open(page, '/account');
      await expect.soft(page.getByTestId('booking-status-B05')).toHaveText(/ยืนยัน/);
    });
    await S('B06 (นัดวันนี้ 15:00) ปุ่มยกเลิกกดไม่ได้', async () => {
      await expect.soft(page.getByTestId('cancel-B06')).toBeDisabled();
    });
  } finally {
    await S('จบเคส: รีเซ็ตกลับ 10:00', async () => { await api.reset(TODAY); });
  }
});

tc('TC-CXL-03', async ({ page, api }) => {
  let code = '';
  const gc = async () => (await (await api.anon()).get('/api/giftcards/SABAI-GC-2000')).json?.balance;
  const points = async () => {
    await open(page, '/account');
    return page.getByTestId('account-points').getAttribute('data-points');
  };
  await S('U04 จอง S01 20 ต.ค. แลก 2 ก้อน จ่ายด้วย Gift Card SABAI-GC-2000 → ยอด ฿900 จ่ายด้วยบัตรทั้งหมด', async () => {
    await loginUI(page, 'U04');
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
    await page.getByTestId('book-points').selectOption('2');
    await page.getByTestId('book-giftcard').fill('SABAI-GC-2000');
    await page.getByTestId('book-giftcard-apply').click();
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(900);
    // บรรทัด Gift Card แสดงเป็นยอดหัก (data-amount ติดลบ) → เทียบขนาดเงินที่จ่ายด้วยบัตร
    expect.soft(Math.abs(await amount(page, 'summary-amount-giftcard'))).toBe(900);
    await page.getByTestId('book-confirm').click();
    code = (await page.getByTestId('booking-confirmation').innerText()).match(/B\d+/)?.[0] ?? '';
    expect(code, 'ได้รหัสการจอง').not.toBe('');
  });
  await S('หลังรีโหลด: แต้ม 50 · บัตรเหลือ ฿1,100', async () => {
    expect.soft(await points()).toBe('50');
    expect.soft(await gc()).toBe(1100);
  });
  await S(`ยกเลิกนัดที่ /account`, async () => {
    await open(page, '/account');
    await page.getByTestId(`cancel-${code}`).click();
    await page.getByTestId(`cancel-confirm-${code}`).click();
    await expect.soft(page.getByTestId(`booking-status-${code}`)).toContainText('ยกเลิก');
  });
  await S('หลังรีโหลด: แต้มกลับเป็น 250 · บัตรกลับเป็น ฿2,000', async () => {
    expect.soft(await points()).toBe('250');
    expect.soft(await gc()).toBe(2000);
  });
});
