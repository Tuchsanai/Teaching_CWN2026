import {
  test, expect, open, note, pause, pickDate, setPeople, slot, fillBooking, bookingBody, bookingDate, slotStatus, expectMoney, money,
  createMember, DAY,
} from './fixtures';

const SLOT_TAKEN = { ok: false, error: 'SLOT_TAKEN', message: 'เวลานี้ถูกจองแล้ว' };
const TIME_INVALID = 'รอบเวลานี้ไม่เปิดให้จอง (เปิด 10:00–22:00 ทุก 30 นาที และต้องเสร็จไม่เกิน 22:00)';
const GROUP_TOO_LARGE = 'กลุ่ม 7 คนขึ้นไป กรุณาโทรหาร้าน 02-123-4567';
const TOO_FAR = 'ไม่มีบริการรับส่งสำหรับระยะนี้';

async function ready(page: import('@playwright/test').Page) {
  await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
}

test.describe('การจอง', () => {
  test('TC-BOOK-01 E2E จองคิวเดี่ยวจนจบ (Guest)', {
    tag: ['@BOOK', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          '/ → hero-book → thai-massage 1 คน (ร้านจัดให้) → วัน → slot-10-00 → กรอกชื่อ/เบอร์ → booking-submit · booking-end-time 11:00 · price-subtotal ฿800 · price-total ฿800 · price-due ฿800 · ' +
          'เห็น booking-success · booking-code = SB + ตัวเลข 5 หลัก · booking-success-total ฿800 · availability รอบ 10:00 ของนักบำบัดที่ได้ = booked',
      },
      { type: 'note', description: 'วันจองแยกตามเบราว์เซอร์ (chromium 2026-10-14 · firefox 10-22 · webkit 10-30) แทน 2026-10-09 เพื่อไม่ให้ชนกันตอนรันพร้อมกัน' },
    ],
  }, async ({ page, browserName }) => {
    const date = bookingDate(browserName, DAY.BOOK01);
    await open(page, '/');
    await page.getByTestId('hero-book').click();
    await expect(page).toHaveURL(/\/book/);
    await ready(page);

    // ขั้น 1: บริการ + จำนวนคน + นักบำบัด
    await page.getByTestId('service-option-thai-massage').click();
    await expect(page.getByTestId('service-option-thai-massage')).toHaveAttribute('aria-checked', 'true');
    await expect(page.getByTestId('booking-people')).toHaveValue('1');
    await expect(page.getByTestId('booking-therapist')).toHaveValue('');
    // ขั้น 2–3: วัน + รอบ
    await pickDate(page, date);
    await slot(page, '10:00').click();
    await expect(page.getByTestId('booking-end-time')).toContainText('11:00');
    // ขั้น 4: ข้อมูลลูกค้าทั่วไป + ราคา
    await page.getByTestId('booking-guest-name').fill('Mei');
    await page.getByTestId('booking-guest-phone').fill('0812345678');
    await page.getByTestId('price-summary').scrollIntoViewIfNeeded();
    await expectMoney(page.getByTestId('price-subtotal'), 800);
    await expectMoney(page.getByTestId('price-total'), 800);
    await expectMoney(page.getByTestId('price-due'), 800);
    await pause(page);
    await page.getByTestId('booking-submit').click();

    await expect(page.getByTestId('booking-success')).toBeVisible();
    const code = (await page.getByTestId('booking-code').textContent())!.trim();
    expect(code).toMatch(/^SB\d{5}$/);
    await expectMoney(page.getByTestId('booking-success-total'), 800);
    note(`ต้องถาม #3: เลข booking-code ที่ได้จริง = ${code}`, 'ต้องถาม');

    const therName = (await page.getByTestId('booking-success-therapists').textContent())!.trim();
    const all = (await (await page.request.get('/api/therapists')).json()).therapists as { id: number; name_th: string }[];
    const ther = all.find((x) => x.name_th === therName);
    expect(ther, `หา id ของนักบำบัด "${therName}"`).toBeTruthy();
    expect(await slotStatus(page.request, { service: 'thai-massage', date, therapistId: ther!.id }, '10:00')).toBe('booked');
  });

  test('TC-BOOK-02 รอบเวลา: เปิด 10:00 ทุก 30 นาที และต้องจบไม่เกิน 22:00 (รวมวันอาทิตย์และวันหยุด)', {
    tag: ['@BOOK', '@P1'],
    annotation: {
      type: 'expected',
      description:
        '2026-10-11 (อา.) และ 2026-10-13 (วันหยุด): ไม่มี 09:30 · รอบแรก 10:00 · มี 10:30 ไม่มี 10:15 · รอบสุดท้าย 21:30 · 60 นาที slot-21-00 free / slot-21-30 closed (disabled) · ' +
        '90 นาที slot-20-30 free / slot-21-00 closed · 120 นาที slot-20-00 free / slot-20-30 closed · POST /api/bookings 09:30 / 10:15 / thai-massage 21:30 → TIME_INVALID "' + TIME_INVALID + '"',
    },
  }, async ({ page, browserName, apiLog }) => {
    const cases = [
      { service: 'thai-massage', free: '21:00', closed: '21:30' },
      { service: 'aroma-oil', free: '20:30', closed: '21:00' },
      { service: 'bangkok-relax', free: '20:00', closed: '20:30' },
    ];
    for (const date of ['2026-10-11', '2026-10-13']) {
      for (const c of cases) {
        await test.step(`API ${date} ${c.service}`, async () => {
          const { body } = await apiLog.call(page.request, 'GET', `/api/availability?service=${c.service}&date=${date}&people=1`);
          const times = (body.slots as { time: string }[]).map((s) => s.time);
          const st = (t: string) => (body.slots as { time: string; status: string }[]).find((s) => s.time === t)?.status;
          expect.soft(times[0], 'รอบแรก').toBe('10:00');
          expect.soft(times.at(-1), 'รอบสุดท้าย').toBe('21:30');
          expect.soft(times).not.toContain('09:30');
          expect.soft(times).not.toContain('10:15');
          expect.soft(times).toContain('10:30');
          expect.soft(st(c.free), `${c.service} ${c.free}`).toBe('free');
          expect.soft(st(c.closed), `${c.service} ${c.closed}`).toBe('closed');
        });
      }
    }

    await open(page, '/book');
    for (const [date, c] of [['2026-10-11', cases[0]], ['2026-10-11', cases[1]], ['2026-10-13', cases[2]], ['2026-10-13', cases[0]]] as const) {
      await test.step(`UI ${date} ${c.service}: ${c.free} ว่าง · ${c.closed} ปิด`, async () => {
        await page.getByTestId(`service-option-${c.service}`).click();
        await pickDate(page, date);
        const list = page.getByTestId('slot-list');
        await expect(list).toBeVisible();
        await expect.soft(slot(page, '09:30')).toHaveCount(0);
        await expect.soft(slot(page, '10:15')).toHaveCount(0);
        await expect.soft(list.getByTestId(/^slot-/).first()).toHaveAttribute('data-testid', 'slot-10-00');
        await expect.soft(list.getByTestId(/^slot-/).last()).toHaveAttribute('data-testid', 'slot-21-30');
        await expect.soft(slot(page, '10:30')).toBeVisible();
        await slot(page, c.closed).scrollIntoViewIfNeeded();
        await expect.soft(slot(page, c.free)).toHaveAttribute('data-status', 'free');
        await expect.soft(slot(page, c.free)).toBeEnabled();
        await expect.soft(slot(page, c.closed)).toHaveAttribute('data-status', 'closed');
        await expect.soft(slot(page, c.closed)).toBeDisabled();
        await pause(page, 600);
      });
    }

    const date = bookingDate(browserName, DAY.BOOK07);
    for (const [service, time] of [['thai-massage', '09:30'], ['thai-massage', '10:15'], ['thai-massage', '21:30']]) {
      await test.step(`POST /api/bookings ${service} ${time} → TIME_INVALID`, async () => {
        const r = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ service, date, time }));
        expect.soft(r.body, `${service} ${time}`).toMatchObject({ ok: false, error: 'TIME_INVALID', message: TIME_INVALID });
      });
    }
  });

  test('TC-BOOK-04 จองซ้อน: นักบำบัด 1 คนรับ 1 คิว (ขอบชนพอดีจองได้) และกดยืนยันซ้ำ', {
    tag: ['@BOOK', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'มาลี (1) 2026-10-10 มีคิว 14:00–15:00: slot-13-30, slot-14-00, slot-14-30 = booked · slot-13-00, slot-15-00 = free · กดรอบที่เต็ม → slot-error "เวลานี้ถูกจองแล้ว" · ' +
          'API จอง 14:30 → 409 SLOT_TAKEN · จอง 13:00 และ 15:00 → 201 ทั้งคู่ · จอง 15:00 ซ้ำ → 409 SLOT_TAKEN · UI กด booking-submit 2 ครั้งติดกัน → เกิดการจองแค่ 1 รายการ',
      },
      {
        type: 'note',
        description:
          'ส่วนที่อ่านอย่างเดียว (สถานะรอบ, 409 ของ 14:30) ใช้คิว seed 2026-10-10 ตามแผน · ส่วนที่จองสำเร็จจริง (13:00 / 15:00) ทำบนวันแยกตามเบราว์เซอร์ที่สร้างคิว 14:00–15:00 ของมาลีไว้ก่อน · ' +
          'ทดสอบกดยืนยันซ้ำด้วย "ร้านจัดให้" เพื่อให้คำขอที่ 2 จองได้จริงถ้าระบบไม่กันกดซ้ำ',
      },
    ],
  }, async ({ page, browserName, apiLog }) => {
    // 1) คิว seed ของมาลี 2026-10-10 14:00–15:00 (อ่านอย่างเดียว)
    await open(page, '/book');
    await page.getByTestId('service-option-thai-massage').click();
    await page.getByTestId('booking-therapist').selectOption('1');
    await pickDate(page, '2026-10-10');
    for (const t of ['13:30', '14:00', '14:30']) await expect.soft(slot(page, t), `${t} ต้องเต็ม`).toHaveAttribute('data-status', 'booked');
    for (const t of ['13:00', '15:00']) await expect.soft(slot(page, t), `${t} ต้องว่าง`).toHaveAttribute('data-status', 'free');
    await slot(page, '14:00').click();
    await expect(page.getByTestId('slot-error')).toHaveText('เวลานี้ถูกจองแล้ว');
    await pause(page);

    const seed = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ date: '2026-10-10', time: '14:30', therapistId: 1 }));
    expect.soft(seed.status, '14:30 ทับคิว 14:00–15:00').toBe(409);
    expect.soft(seed.body).toEqual(SLOT_TAKEN);

    // 2) วันของเบราว์เซอร์นี้: สร้างคิวมาลี 14:00–15:00 แล้วจองขอบชนพอดี
    const date = bookingDate(browserName, DAY.BOOK04);
    const block = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ date, time: '14:00', therapistId: 1, guestName: 'Block' }));
    expect(block.status, 'เตรียมคิว 14:00–15:00 ของมาลี').toBe(201);
    const r1300 = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ date, time: '13:00', therapistId: 1 }));
    expect.soft(r1300.status, '13:00 (จบชน 14:00 พอดี)').toBe(201);
    const r1500 = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ date, time: '15:00', therapistId: 1 }));
    expect.soft(r1500.status, '15:00 (เริ่มชน 15:00 พอดี)').toBe(201);
    const again = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ date, time: '15:00', therapistId: 1, guestName: 'Again' }));
    expect.soft(again.status, 'จอง 15:00 ซ้ำ').toBe(409);
    expect.soft(again.body).toEqual(SLOT_TAKEN);

    // 3) กด booking-submit 2 ครั้งติดกัน (สมาชิก เพื่อดูรายการจองของตัวเองได้)
    await createMember(page.request);
    await open(page, '/book');
    await fillBooking(page, { service: 'thai-massage', date, time: '17:00' });
    await expectMoney(page.getByTestId('price-total'), 800);
    await page.getByTestId('booking-submit').evaluate((btn: HTMLButtonElement) => {
      btn.click();
      btn.click();
    });
    await expect(page.getByTestId('booking-success')).toBeVisible();
    await page.waitForTimeout(1500); // เผื่อคำขอที่ 2 ยังไม่กลับ
    const mine = (await (await page.request.get('/api/bookings')).json()).bookings as { date: string; time: string; status: string }[];
    expect(mine.filter((b) => b.date === date && b.time === '17:00' && b.status !== 'cancelled'), 'กดยืนยัน 2 ครั้ง ต้องมีการจองแค่ 1 รายการ').toHaveLength(1);
  });

  test('TC-BOOK-05 จองคู่ 2 คนพอดี และ Couple Suite ซ้อน', {
    tag: ['@BOOK', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'aroma-oil (90 นาที) 2026-10-10 Couple Suite มีคิว 18:00–19:30: จำนวนคน 2 → booking-kind-couple กดได้ · 1 และ 3 คน → disabled · slot-17-00, slot-18-00 = booked · slot-16-30, slot-19-30 = free · ' +
          'จอง 18:00 → 409 "เวลานี้ถูกจองแล้ว" · จอง 19:30 → 201 room "couple-suite", therapists 2 คน, เริ่มพร้อมกัน, endTime 21:00 · คู่ที่ 2 จอง 19:30 ซ้ำ → 409 SLOT_TAKEN',
      },
      { type: 'note', description: 'ส่วนที่อ่านอย่างเดียวใช้คิว seed 2026-10-10 · ส่วนที่จองสำเร็จทำบนวันแยกตามเบราว์เซอร์ที่สร้างคิว Couple Suite 18:00–19:30 ไว้ก่อน' },
    ],
  }, async ({ page, browserName, apiLog }) => {
    await open(page, '/book');
    await page.getByTestId('service-option-aroma-oil').click();
    await setPeople(page, 1);
    await expect.soft(page.getByTestId('booking-kind-couple'), '1 คน').toBeDisabled();
    await setPeople(page, 3);
    await expect.soft(page.getByTestId('booking-kind-couple'), '3 คน').toBeDisabled();
    await setPeople(page, 2);
    await expect(page.getByTestId('booking-kind-couple'), '2 คน').toBeEnabled();
    await expect(page.getByTestId('booking-kind-couple')).toHaveAttribute('aria-checked', 'true');
    await pickDate(page, '2026-10-10');
    for (const t of ['17:00', '18:00']) await expect.soft(slot(page, t), `${t} ต้องเต็ม`).toHaveAttribute('data-status', 'booked');
    for (const t of ['16:30', '19:30']) await expect.soft(slot(page, t), `${t} ต้องว่าง`).toHaveAttribute('data-status', 'free');
    await slot(page, '18:00').click();
    await expect(page.getByTestId('slot-error')).toHaveText('เวลานี้ถูกจองแล้ว');
    await pause(page);

    const seed = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ service: 'aroma-oil', people: 2, date: '2026-10-10', time: '18:00' }));
    expect.soft(seed.status).toBe(409);
    expect.soft(seed.body).toEqual(SLOT_TAKEN);

    const date = bookingDate(browserName, DAY.BOOK05);
    const block = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ service: 'aroma-oil', people: 2, date, time: '18:00', guestName: 'Block' }));
    expect(block.status, 'เตรียมคิว Couple Suite 18:00–19:30').toBe(201);
    const blocked = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ service: 'aroma-oil', people: 2, date, time: '18:00' }));
    expect.soft(blocked.status).toBe(409);
    expect.soft(blocked.body).toEqual(SLOT_TAKEN);
    const ok = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ service: 'aroma-oil', people: 2, date, time: '19:30', guestName: 'Couple 1' }));
    expect(ok.status, 'จองคู่ 19:30').toBe(201);
    expect.soft(ok.body.booking.room).toBe('couple-suite');
    expect.soft(ok.body.booking.therapists).toHaveLength(2);
    expect.soft(ok.body.booking.time).toBe('19:30');
    expect.soft(ok.body.booking.endTime).toBe('21:00');
    const second = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ service: 'aroma-oil', people: 2, date, time: '19:30', guestName: 'Couple 2' }));
    expect.soft(second.status, 'คู่ที่ 2 จอง 19:30 ซ้ำ').toBe(409);
    expect.soft(second.body).toEqual(SLOT_TAKEN);
  });

  test('TC-BOOK-06 จำนวนคน: คู่ / กลุ่ม 3–6 / ≥7 โทรร้าน และส่วนลดกลุ่ม 10%', {
    tag: ['@BOOK', '@P1'],
    annotation: {
      type: 'expected',
      description:
        'thai-massage ฿800: 2 คน → booking-kind-group disabled · 3 คน กลุ่มได้ ไม่ลด price-total ฿2,400 · 4 คน price-group-discount −฿320 → ฿2,880 · 6 คน −฿480 → ฿4,320 · ' +
        '7 คน → booking-group-error "' + GROUP_TOO_LARGE + '" และจองไม่ได้ (API → GROUP_TOO_LARGE) · 0 คน → PEOPLE_INVALID "กรุณาระบุจำนวนคนให้ถูกต้อง" · ' +
        'quote ตัวอย่าง SPEC §5 → subtotal 3200, groupDiscount 320, transportFee 300, cars 1, total 3180, due 3180',
    },
  }, async ({ page, browserName, apiLog }) => {
    await open(page, '/book');
    await page.getByTestId('service-option-thai-massage').click();
    await setPeople(page, 2);
    await expect.soft(page.getByTestId('booking-kind-group'), '2 คน').toBeDisabled();
    for (const [n, disc, total] of [[3, 0, 2400], [4, -320, 2880], [6, -480, 4320]]) {
      await test.step(`${n} คน → ส่วนลดกลุ่ม ${disc} · รวม ${total}`, async () => {
        await setPeople(page, n);
        await expect.soft(page.getByTestId('booking-kind-group')).toBeEnabled();
        await expectMoney(page.getByTestId('price-group-discount'), disc);
        await expectMoney(page.getByTestId('price-total'), total);
        await pause(page, 600);
      });
    }
    await setPeople(page, 7);
    await expect(page.getByTestId('booking-group-error')).toContainText(GROUP_TOO_LARGE);
    await expect(page.getByTestId('booking-submit')).toBeDisabled();
    await pause(page);

    const date = bookingDate(browserName, DAY.BOOK07);
    const seven = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ people: 7, date, time: '10:00' }));
    expect.soft(seven.body, '7 คน').toMatchObject({ ok: false, error: 'GROUP_TOO_LARGE', message: GROUP_TOO_LARGE });
    const zero = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ people: 0, date, time: '10:00' }));
    expect.soft(zero.body, '0 คน').toMatchObject({ ok: false, error: 'PEOPLE_INVALID', message: 'กรุณาระบุจำนวนคนให้ถูกต้อง' });
    const q = await apiLog.call(page.request, 'POST', '/api/quote', {
      service: 'thai-massage', people: 4, transport: true, hotelId: 4, redeemSets: 1, useBirthday: false, payWith: 'cash', giftCode: null,
    });
    expect(q.body.quote).toMatchObject({ subtotal: 3200, groupDiscount: 320, transportFee: 300, cars: 1, total: 3180, due: 3180 });
  });

  test('TC-BOOK-07 ค่ารถตามระยะทาง และจำนวนรถ', {
    tag: ['@BOOK', '@P1'],
    annotation: {
      type: 'expected',
      description:
        '1 คน: โรงแรม 2 (5.0) → transport-fee ฿0 · โรงแรม 3 (5.1) → ฿300 price-total ฿1,100 · โรงแรม 5 (15.0) → ฿300 · โรงแรม 6 (15.1), 7 (20.0) → transport-error "' + TOO_FAR + '" และจองไม่ได้ · ' +
        'โรงแรม 4: 4 คน → 1 คัน ฿300 · 5 คน → 2 คัน ฿600 (price-total ฿4,200) · 6 คน → 2 คัน ฿600 · GET /api/transport?hotelId=4&people=5 → {"available":true,"distanceKm":12,"cars":2,"feePerCar":300,"fee":600} · ' +
        'เปิดรถแต่ไม่เลือกโรงแรม → "กรุณาเลือกโรงแรม"',
    },
  }, async ({ page, browserName, apiLog }) => {
    await open(page, '/book');
    await page.getByTestId('service-option-thai-massage').click();
    await page.getByTestId('booking-transport').check();
    const hotel = page.getByTestId('booking-hotel');
    for (const [id, fee, total] of [[2, 0, 800], [3, 300, 1100], [5, 300, 1100]]) {
      await test.step(`1 คน โรงแรม ${id} → ค่ารถ ${fee}`, async () => {
        await hotel.selectOption(String(id));
        await expectMoney(page.getByTestId('transport-fee'), fee, `transport-fee โรงแรม ${id}`);
        await expectMoney(page.getByTestId('price-total'), total, `price-total โรงแรม ${id}`);
        await pause(page, 600);
      });
    }
    await hotel.selectOption('2');
    await expectMoney(page.getByTestId('transport-fee'), 0); // รอให้ราคา/ระยะของโรงแรม 2 อัปเดตก่อนอ่าน
    await expect(page.getByTestId('transport-distance')).toContainText('5');
    note(`ต้องถาม #13: รูปแบบระยะทางบนหน้า — โรงแรม 2 แสดง transport-distance = "${(await page.getByTestId('transport-distance').textContent())?.trim()}"`, 'ต้องถาม');
    for (const id of [6, 7]) {
      await hotel.selectOption(String(id));
      await expect.soft(page.getByTestId('transport-error'), `โรงแรม ${id}`).toHaveText(TOO_FAR);
      await pause(page, 600);
    }
    const date = bookingDate(browserName, DAY.BOOK07);
    const far = await apiLog.call(page.request, 'POST', '/api/bookings', bookingBody({ date, time: '20:00', transport: true, hotelId: 6 }));
    expect.soft(far.body, 'จองโรงแรม 6 ต้องไม่สำเร็จ').toMatchObject({ ok: false, error: 'TRANSPORT_TOO_FAR', message: TOO_FAR });

    await hotel.selectOption('4');
    for (const [n, cars, fee, total] of [[4, 1, 300, null], [5, 2, 600, 4200], [6, 2, 600, null]] as const) {
      await test.step(`โรงแรม 4 · ${n} คน → ${cars} คัน ฿${fee}`, async () => {
        await setPeople(page, n);
        await expect.poll(async () => money(await page.getByTestId('transport-cars').textContent()), { message: `transport-cars ${n} คน` }).toBe(cars);
        await expectMoney(page.getByTestId('transport-fee'), fee, `transport-fee ${n} คน`);
        if (total) await expectMoney(page.getByTestId('price-total'), total, `price-total ${n} คน`);
        await pause(page, 600);
      });
    }
    const tr = await apiLog.call(page.request, 'GET', '/api/transport?hotelId=4&people=5');
    expect.soft(tr.body).toMatchObject({ available: true, distanceKm: 12, cars: 2, feePerCar: 300, fee: 600 });

    await test.step('เปิดรถแต่ไม่เลือกโรงแรม → "กรุณาเลือกโรงแรม"', async () => {
      await open(page, '/book');
      await fillBooking(page, { service: 'thai-massage', date, time: '20:00', guest: true });
      await page.getByTestId('booking-transport').check();
      await expect(page.getByTestId('booking-hotel')).toHaveValue('');
      await page.getByTestId('booking-submit').click();
      await expect(page.getByTestId('booking-error')).toHaveText('กรุณาเลือกโรงแรม');
      await expect(page.getByTestId('booking-success')).toHaveCount(0);
    });
  });

  test('TC-BOOK-08 แพ็กเกจ Bangkok Relax: รายการที่รวม ราคาต่อคน และราคารวม', {
    tag: ['@BOOK', '@P1'],
    annotation: {
      type: 'expected',
      description:
        'package-price ฿2,900 · มี package-inc-thai-massage, package-inc-herbal-compress, package-inc-transfer · package-herbs ไพล ขมิ้น ตะไคร้ · 1 คน package-total ฿2,900 · ' +
        '4 คน package-total ฿11,600 หรือ ฿10,440 (ต้องถาม) · โรงแรม 4 → package-cars 1, package-transport-fee ฿300 · โรงแรม 6 → package-transport-error · ' +
        'ที่ /book 4 คน + โรงแรม 4: price-subtotal ฿11,600, price-group-discount −฿1,160, price-transport ฿300, price-total ฿10,740',
    },
  }, async ({ page }) => {
    await open(page, '/packages/bangkok-relax');
    await expectMoney(page.getByTestId('package-price'), 2900);
    for (const id of ['package-inc-thai-massage', 'package-inc-herbal-compress', 'package-inc-transfer']) await expect.soft(page.getByTestId(id)).toBeVisible();
    const herbs = await page.getByTestId('package-herbs').locator('li[data-herb]').evaluateAll((li) => li.map((x) => x.getAttribute('data-herb')));
    expect.soft(herbs, 'ไพล ขมิ้น ตะไคร้').toEqual(['plai', 'turmeric', 'lemongrass']);
    await page.getByTestId('package-total').scrollIntoViewIfNeeded();
    await expectMoney(page.getByTestId('package-total'), 2900);
    for (let i = 0; i < 3; i++) await page.getByTestId('package-people-plus').click();
    await expect(page.getByTestId('package-people')).toHaveValue('4');
    await expect.poll(async () => money(await page.getByTestId('package-total').textContent())).not.toBe(2900);
    const total4 = money(await page.getByTestId('package-total').textContent());
    note(`ต้องถาม #4: package-total 4 คนที่หน้าแพ็กเกจแสดงจริง = ฿${total4.toLocaleString('en-US')}`, 'ต้องถาม');
    expect.soft([11600, 10440], 'package-total 4 คน ต้องเป็น ฿11,600 หรือ ฿10,440').toContain(total4);

    await page.getByTestId('package-hotel').selectOption('4');
    await expect.poll(async () => money(await page.getByTestId('package-cars').textContent())).toBe(1);
    await expectMoney(page.getByTestId('package-transport-fee'), 300);
    await pause(page, 600);
    await page.getByTestId('package-hotel').selectOption('6');
    await expect(page.getByTestId('package-transport-error')).toHaveText(TOO_FAR);
    await pause(page, 600);

    await page.getByTestId('package-book').click();
    await expect(page).toHaveURL(/\/book\?service=bangkok-relax&people=4/);
    await ready(page);
    await expect(page.getByTestId('service-option-bangkok-relax')).toHaveAttribute('aria-checked', 'true');
    await expect(page.getByTestId('booking-people')).toHaveValue('4');
    await expect(page.getByTestId('booking-transport')).toBeChecked();
    await page.getByTestId('booking-hotel').selectOption('4');
    await page.getByTestId('price-summary').scrollIntoViewIfNeeded();
    await expectMoney(page.getByTestId('price-subtotal'), 11600);
    await expectMoney(page.getByTestId('price-group-discount'), -1160);
    await expectMoney(page.getByTestId('price-transport'), 300);
    await expectMoney(page.getByTestId('price-total'), 10740);
    await pause(page);
  });
});
