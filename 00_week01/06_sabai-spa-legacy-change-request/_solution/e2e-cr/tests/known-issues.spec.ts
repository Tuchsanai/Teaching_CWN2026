import { test, expect, guestToStep3, settlePrice } from './fixtures';

// Known issues ของระบบที่รับมอบ (ดู ../KNOWN-ISSUES.md) · ยังไม่แก้ (ยังไม่มี CR สั่ง)
// คู่เทสต์ของข้อที่คิดว่าเป็นบั๊ก: ① ล็อกพฤติกรรมปัจจุบัน [E]  ② test.fail() = พฤติกรรมที่ควรเป็น (รอ CR · ผ่านเมื่อไรให้ถอด test.fail)
const KI = (id: string) => ({ type: 'known-issue', description: `KNOWN-ISSUES.md ${id}` });

/** เดินหน้าจองถึงขั้น 3 แล้วใส่ Gift Card ที่ไม่มีอยู่ · รอ /api/price ตอบ 422 แล้วตอบใหม่อีกรอบ */
async function applyFakeGiftCard(page: import('@playwright/test').Page) {
  await guestToStep3(page, { service: 'S01', date: '2026-10-22', time: '14:00' });
  await page.getByTestId('book-contact-name').fill('ทดสอบบัตร');
  await page.getByTestId('book-contact-phone').fill('0812345678');
  await settlePrice(page);
  const firstErr = page.waitForResponse((r) => r.url().includes('/api/price') && r.status() === 422);
  await page.getByTestId('book-giftcard').fill('SABAI-GC-FAKE');
  await page.getByTestId('book-giftcard-apply').click();
  const err = await (await firstErr).json();
  expect(err.error).toBe('GC_NOT_FOUND');
  await page.waitForResponse((r) => r.url().includes('/api/price') && r.status() === 200);
  await settlePrice(page);
}

test.describe('KI-01 Gift Card ที่ไม่มีอยู่: หน้าจองไม่เตือน', () => {
  test('KI-01a [ล็อกปัจจุบัน] API บอก GC_NOT_FOUND แต่หน้าจองไม่แสดงคำเตือน และคิดยอดเต็มต่อ', async ({ page, request }) => {
    test.info().annotations.push(KI('KI-01'), { type: 'source', description: '[E] รันระบบที่รับมอบ 2026-10-12' });
    const g = await request.get('/api/giftcards/SABAI-GC-FAKE');
    expect(g.status()).toBe(404);
    expect((await g.json()).error).toBe('GC_NOT_FOUND');

    await applyFakeGiftCard(page);
    await expect(page.getByTestId('book-giftcard-error')).toHaveCount(0);
    await expect(page.getByTestId('book-quote-error')).toHaveCount(0);
    await expect(page.getByText('ไม่พบ Gift Card นี้')).toHaveCount(0);
    await expect(page.getByTestId('book-giftcard')).toHaveValue('SABAI-GC-FAKE');
    await expect(page.getByTestId('book-quote-total')).toContainText('฿1,000');
  });

  test('KI-01b [ควรเป็น] หน้าจองเตือน "ไม่พบ Gift Card นี้" ค้างไว้ให้ลูกค้าเห็น', async ({ page }) => {
    test.info().annotations.push(KI('KI-01'));
    test.fail(true, 'KI-01 ยังไม่แก้ · พฤติกรรมที่ควรเป็น (รอ CR/คำตอบร้าน)');
    await applyFakeGiftCard(page);
    await expect(page.getByText('ไม่พบ Gift Card นี้')).toBeVisible({ timeout: 3_000 });
  });
});

const ABC_BOOKING = {
  type: 'single', serviceCode: 'S01', date: '2026-10-22', time: '14:00',
  contactName: 'ทดสอบเบอร์', contactPhone: 'abc', quotedTotal: 1000,
};

test.describe('KI-02 จองแบบไม่ล็อกอินด้วยเบอร์โทร "abc"', () => {
  test('KI-02a [ล็อกปัจจุบัน] POST /api/bookings เบอร์ "abc" → 201 จองสำเร็จ และขึ้นในคิวหลังร้าน', async ({ request, apiAs }) => {
    test.info().annotations.push(KI('KI-02'), { type: 'source', description: '[E] รันระบบที่รับมอบ 2026-10-12' });
    const r = await request.post('/api/bookings', { data: ABC_BOOKING });
    expect(r.status()).toBe(201);
    const b = await r.json();
    expect(b.status).toBe('confirmed');
    const owner = await apiAs('owner');
    const q = await (await owner.get('/api/admin/bookings?date=2026-10-22')).json();
    const row = q.bookings.find((x: { code: string }) => x.code === b.code);
    expect(row?.customer).toBe('ทดสอบเบอร์ (abc)');
  });

  test('KI-02b [ควรเป็น] เบอร์ "abc" ถูกปฏิเสธ (4xx) ไม่สร้างนัด', async ({ request }) => {
    test.info().annotations.push(KI('KI-02'));
    test.fail(true, 'KI-02 ยังไม่แก้ · ต้องถามร้านรูปแบบเบอร์ที่รับ');
    const r = await request.post('/api/bookings', { data: ABC_BOOKING });
    expect(r.status()).toBe(422);
  });
});

test.describe('KI-03 เจ้าของร้านยกเลิกนัดของลูกค้าผ่าน API', () => {
  // ยังไม่ตัดสินว่าเป็นบั๊ก (โค้ดตั้งใจให้ owner ทำได้ `booking.ts` cancelBooking · หน้า /admin ไม่มีปุ่ม) → ต้องถามร้าน · ล็อกอย่างเดียว ไม่มีคู่ test.fail
  test('KI-03a [ล็อกปัจจุบัน] owner POST /api/bookings/B05/cancel (นัดของคุณนิดา) → 200 cancelled', async ({ apiAs }) => {
    test.info().annotations.push(KI('KI-03'), { type: 'source', description: '[E] รันระบบที่รับมอบ 2026-10-12' });
    const owner = await apiAs('owner');
    const r = await owner.post('/api/bookings/B05/cancel');
    expect(r.status()).toBe(200);
    expect(await r.json()).toMatchObject({ ok: true, code: 'B05', status: 'cancelled' });
  });
});
