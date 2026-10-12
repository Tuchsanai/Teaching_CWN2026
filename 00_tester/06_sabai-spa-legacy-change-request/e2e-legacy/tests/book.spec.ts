import { tc, test, expect, open, bookStep1, bookStep2, bookToStep3, fillContact, toSummary, amount, loginUI, quoteTotal } from './fixtures';

const S = test.step;

// ตัวช่วย: จองแบบไม่ล็อกอินผ่าน API (ใช้กับจุดตรวจ ❌/4xx ที่หน้าเว็บสร้างไม่ได้ — แผน 2.3 ข้อ 4)
const anonBooking = (date: string, time: string, extra: Record<string, unknown> = {}) => ({
  type: 'single', serviceCode: 'S01', people: 1, date, time,
  contactName: 'ทดสอบ API', contactPhone: '0812345678', quotedTotal: 1000, ...extra,
});

tc('TC-BOOK-01', async ({ page, api }) => {
  await S('ขั้น 1: เปิดหน้าจองนวดไทย 60 นาที แบบไม่ล็อกอิน', async () => {
    await bookStep1(page, { service: 'S01', type: 'single' });
  });
  await S('แถบขั้นตอนมี 4 ขั้น', async () => {
    await expect.soft(page.getByTestId('book-step-indicator')).toContainText('จาก 4');
    for (const label of ['1. บริการ', '2. วัน/เวลา', '3. ข้อมูลติดต่อ', '4. ยืนยัน']) {
      await expect.soft(page.getByText(label, { exact: true }).first()).toBeVisible();
    }
  });
  await S('ขั้น 2: เลือก 20 ต.ค. 14:00 พี่สมศรี (T01)', async () => {
    await bookStep2(page, { date: '2026-10-20', time: '14:00', therapist: 'T01' });
  });
  await S('ขั้น 3: กรอกชื่อ "ทดสอบ E2E" เบอร์ 0812345678', async () => {
    await fillContact(page, 'ทดสอบ E2E', '0812345678');
    await toSummary(page);
  });
  await S('ขั้น 4: ใบสรุปมีสมุนไพร "ไพล, ตะไคร้" และยอดสุทธิ ฿1,000', async () => {
    // ใบสรุปแสดงสมุนไพรเป็นชิป <li> ทีละตัว → เทียบเป็นรายการ "ไพล, ตะไคร้"
    expect.soft((await page.getByTestId('book-herbs').locator('li').allInnerTexts()).map((t) => t.trim()).join(', ')).toBe('ไพล, ตะไคร้');
    expect.soft(await amount(page, 'summary-total')).toBe(1000);
  });
  await S('กดยืนยัน → ข้อความยืนยันพร้อมรหัสการจอง B + ตัวเลข (ทันที)', async () => {
    await page.getByTestId('book-confirm').click();
    await expect.soft(page.getByTestId('booking-confirmation')).toHaveText(/B\d+/);
  });
  await S('หลังรีโหลด: ตารางคิว 20 ต.ค. มีนัด 14:00 ของ T01 1 รายการ', async () => {
    const rows = (await api.adminBookings('2026-10-20'))
      .filter((b) => b.time.startsWith('14:00') && b.status !== 'cancelled' && b.therapists.some((t: string) => t.startsWith('T01')));
    expect.soft(rows.length).toBe(1);
  });
});

tc('TC-BOOK-02', async ({ page, api }) => {
  await S('ขั้น 2: ช่องวันมี min = 2026-10-11 และ max = 2026-11-09', async () => {
    await bookStep1(page, { service: 'S01', type: 'single' });
    const d = page.getByTestId('book-date');
    await expect.soft(d).toHaveAttribute('min', '2026-10-11');
    await expect.soft(d).toHaveAttribute('max', '2026-11-09');
  });
  const anon = await api.anon();
  for (const [date, ok, label] of [
    ['2026-10-10', false, '10 ต.ค. (+0) ❌'],
    ['2026-10-11', true, '11 ต.ค. (+1) ✅'],
    ['2026-11-09', true, '9 พ.ย. (+30) ✅'],
    ['2026-11-10', false, '10 พ.ย. (+31) ❌'],
  ] as const) {
    await S(`จอง S01 วันที่ ${label}`, async () => {
      const r = await anon.post('/api/bookings', anonBooking(date, '14:00'));
      if (ok) expect.soft(r.status, `${date} ต้องจองได้`).toBe(201);
      else expect.soft(r.status >= 400 && r.status < 500, `${date} ต้องได้ 4xx (ได้ ${r.status})`).toBe(true);
    });
  }
});

tc('TC-BOOK-03', async ({ page, api }) => {
  const slotsOnPage = async () => (await page.locator('[data-testid^="book-slot-"]').evaluateAll(
    (es) => es.map((e) => e.getAttribute('data-testid')!.replace('book-slot-', ''))));
  await S('S01 (60 นาที) วันที่ 21 ต.ค.: 23 รอบ 10:00–21:00 ไม่มี 09:30 / 21:30', async () => {
    await bookStep1(page, { service: 'S01', type: 'single' });
    await page.getByTestId('book-date').fill('2026-10-21');
    await expect(page.getByTestId('book-slot-10:00')).toBeVisible();
    const s = await slotsOnPage();
    expect.soft(s.length, 'จำนวนรอบ S01').toBe(23);
    expect.soft(s[0]).toBe('10:00');
    expect.soft(s[s.length - 1]).toBe('21:00');
    expect.soft(s).not.toContain('09:30');
    expect.soft(s).not.toContain('21:30');
  });
  await S('S02 (90 นาที) วันที่ 21 ต.ค.: 22 รอบ สุดท้าย 20:30', async () => {
    await bookStep1(page, { service: 'S02', type: 'single' });
    await page.getByTestId('book-date').fill('2026-10-21');
    await expect(page.getByTestId('book-slot-10:00')).toBeVisible();
    const s = await slotsOnPage();
    expect.soft(s.length, 'จำนวนรอบ S02').toBe(22);
    expect.soft(s[s.length - 1]).toBe('20:30');
  });
  await S('ยิงจอง S01 เวลา 10:15 → 4xx และไม่บันทึก (หลังรีโหลด)', async () => {
    const anon = await api.anon();
    const r = await anon.post('/api/bookings', anonBooking('2026-10-21', '10:15'));
    expect.soft(r.status >= 400 && r.status < 500, `10:15 ต้องได้ 4xx (ได้ ${r.status})`).toBe(true);
    const rows = (await api.adminBookings('2026-10-21')).filter((b) => b.time.startsWith('10:15'));
    expect.soft(rows.length).toBe(0);
  });
});

tc('TC-BOOK-04', async ({ page, api }) => {
  const anon = await api.anon();
  for (const t of ['13:30', '14:30']) {
    await S(`T03 วันที่ 12 ต.ค. เริ่ม ${t} (ทับ B01 14:00–15:00) → ❌ "เวลานี้ถูกจองแล้ว"`, async () => {
      const r = await anon.post('/api/bookings', anonBooking('2026-10-12', t, { therapists: ['T03'] }));
      expect.soft(r.status, `${t} ต้องถูกปฏิเสธ`).toBe(409);
      expect.soft(r.json?.message).toBe('เวลานี้ถูกจองแล้ว');
    });
  }
  await S('หลังรีโหลด: ตารางคิว 12 ต.ค. ของ T03 มีแค่ B01', async () => {
    const rows = (await api.adminBookings('2026-10-12')).filter((b) => b.status !== 'cancelled' && b.therapists.some((x: string) => x.startsWith('T03')));
    expect.soft(rows.map((b) => b.code)).toEqual(['B01']);
  });
  await S('หน้าเว็บ: จอง T03 เวลา 15:00 (จบเดิม = เริ่มใหม่) → ✅', async () => {
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-12', time: '15:00', therapist: 'T03' });
    await fillContact(page, 'ทดสอบต่อคิว', '0812345678');
    await toSummary(page);
    await page.getByTestId('book-confirm').click();
    await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  });
});

tc('TC-BOOK-05', async ({ page, api }) => {
  await S('จอง S01 22 ต.ค. 13:00 นักบำบัด "ใครก็ได้" ชื่อ "ทดสอบกดซ้ำ"', async () => {
    await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-22', time: '13:00' });
    await fillContact(page, 'ทดสอบกดซ้ำ', '0812345678');
    await toSummary(page);
  });
  await S('ดับเบิลแตะปุ่ม "ยืนยันการจอง" → เห็นรหัสการจอง 1 รหัส (ทันที)', async () => {
    await page.getByTestId('book-confirm').dblclick();
    const msg = page.getByTestId('booking-confirmation');
    await expect(msg).toBeVisible();
    await expect.soft(msg).toHaveCount(1);
    expect.soft((await msg.innerText()).match(/B\d+/g)?.length ?? 0).toBe(1);
  });
  await S('หลังรีโหลด: ตารางคิว 22 ต.ค. มีชื่อ "ทดสอบกดซ้ำ" 1 แถว', async () => {
    const rows = (await api.adminBookings('2026-10-22')).filter((b) => String(b.customer).startsWith('ทดสอบกดซ้ำ'));
    expect.soft(rows.length).toBe(1);
  });
});

tc('TC-BOOK-07', async ({ page, api }) => {
  await loginUI(page, 'U02');
  const u02 = await api.as('U02');
  const couple = (people: number, time: string, quotedTotal = 2520) => ({ type: 'couple', serviceCode: 'S02', people, date: '2026-10-17', time, quotedTotal });
  for (const n of [1, 3]) {
    await S(`จองคู่ ${n} คน → ❌`, async () => {
      const r = await u02.post('/api/bookings', couple(n, '20:30'));
      expect.soft(r.status >= 400 && r.status < 500, `คู่ ${n} คน ต้อง 4xx (ได้ ${r.status})`).toBe(true);
    });
  }
  await S('จองคู่ 2 คน 19:30 (ทับ B02 19:00–20:30) → ❌ "เวลานี้ถูกจองแล้ว"', async () => {
    const r = await u02.post('/api/bookings', couple(2, '19:30'));
    expect.soft(r.status).toBe(409);
    expect.soft(r.json?.message).toBe('เวลานี้ถูกจองแล้ว');
  });
  await S('หน้าเว็บ: จองคู่ 2 คน 20:30 → ✅ ราคา ฿2,520', async () => {
    await bookToStep3(page, { service: 'S02', type: 'couple', people: 2, date: '2026-10-17', time: '20:30' });
    expect.soft(await quoteTotal(page)).toBe(2520);
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(2520);
    await page.getByTestId('book-confirm').click();
    await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  });
});

tc('TC-BOOK-08', async ({ page, api }) => {
  await loginUI(page, 'U08');
  const u08 = await api.as('U08');
  const group = (people: number) => ({ type: 'group', serviceCode: 'S01', people, date: '2026-10-20', time: '10:00' });
  await S('กลุ่ม 2 คน → ❌ (ไม่ใช่กลุ่ม)', async () => {
    const r = await u08.post('/api/price', group(2));
    expect.soft(r.status >= 400 && r.status < 500, `2 คน ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  });
  await S('กลุ่ม 3 คน → ✅', async () => {
    const r = await u08.post('/api/price', group(3));
    expect.soft(r.status).toBe(200);
  });
  await S('กลุ่ม 6 คน → ✅ (จองได้จริง)', async () => {
    const q = await u08.post('/api/price', group(6));
    expect.soft(q.status).toBe(200);
    const r = await u08.post('/api/bookings', { ...group(6), quotedTotal: q.json?.total });
    expect.soft(r.status).toBe(201);
  });
  await S('หน้าเว็บ: กลุ่ม 7 คน → ข้อความ "กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน" และมีเบอร์โทรร้าน', async () => {
    await bookStep1(page, { service: 'S01', type: 'group', people: 7 });
    await expect.soft(page.getByTestId('book-error-message')).toContainText('กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน');
    await expect.soft(page.getByTestId('shop-phone')).toHaveText(/\d{2,3}-?\d{3}-?\d{4}/);
  });
});

tc('TC-BOOK-09', async ({ page, api }) => {
  await loginUI(page, 'U08');
  const u08 = await api.as('U08');
  const group = (people: number, time: string, quotedTotal: number) => ({ type: 'group', serviceCode: 'S01', people, date: '2026-10-13', time, quotedTotal });
  await S('6 คน 13 ต.ค. 10:00 → ❌ (นักบำบัดว่าง 5 คน)', async () => {
    const r = await u08.post('/api/bookings', group(6, '10:00', 5400));
    expect.soft(r.status >= 400 && r.status < 500, `ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  });
  await S('หน้าเว็บ: 5 คน 10:00 → ✅ ฿4,500', async () => {
    await bookToStep3(page, { service: 'S01', type: 'group', people: 5, date: '2026-10-13', time: '10:00' });
    expect.soft(await quoteTotal(page)).toBe(4500);
    await toSummary(page);
    expect.soft(await amount(page, 'summary-total')).toBe(4500);
    await page.getByTestId('book-confirm').click();
    await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  });
  await S('6 คน 11:30 → ✅ ฿5,400', async () => {
    const r = await u08.post('/api/bookings', group(6, '11:30', 5400));
    expect.soft(r.status).toBe(201);
    expect.soft(r.json?.total).toBe(5400);
  });
});

tc('TC-BOOK-10', async ({ page, api }) => {
  const variants: [string, string, string][] = [
    ['ชื่อ+เบอร์ว่าง', '', ''],
    ['มีแค่ชื่อ "ทดสอบ"', 'ทดสอบ', ''],
    ['มีแค่เบอร์ 0812345678', '', '0812345678'],
    ['ชื่อเป็นเว้นวรรคล้วน', '   ', '0812345678'],
  ];
  for (const [label, name, phone] of variants) {
    await S(`ขั้น 3: ${label} → ไปขั้น 4 ไม่ได้ และมีข้อความให้กรอกชื่อและเบอร์`, async () => {
      await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '15:00' });
      await fillContact(page, name, phone);
      await page.getByTestId('book-next-3').click();
      await expect.soft(page.getByTestId('book-error-message')).toHaveText(/กรอกชื่อ.*เบอร์/);
      await expect.soft(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
      await expect.soft(page.getByTestId('book-summary')).toHaveCount(0);
    });
  }
  await S('หลังรีโหลด: ไม่มีนัดใหม่ 20 ต.ค. 15:00', async () => {
    const rows = (await api.adminBookings('2026-10-20')).filter((b) => b.time.startsWith('15:00'));
    expect.soft(rows.length).toBe(0);
  });
});
