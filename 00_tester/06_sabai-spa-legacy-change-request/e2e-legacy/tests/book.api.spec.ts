import { tc, test, expect } from './fixtures';

const S = test.step;

// ยิง API อย่างเดียว (แผน 6.2 ข้อ 3) — log อยู่ที่ test-report/logs/TC-BOOK-06.log
tc('TC-BOOK-06', async ({ api }) => {
  const [u03, u04] = await Promise.all([api.as('U03'), api.as('U04')]);
  const input = { type: 'single', serviceCode: 'S01', people: 1, date: '2026-10-15', time: '11:00', therapists: ['T04'], quotedTotal: 1000 };
  let results: { status: number; json: any }[] = [];
  await S('U03 + U04 ส่งจอง T04 15 ต.ค. 11:00 พร้อมกัน 2 คำขอ', async () => {
    results = await Promise.all([u03.post('/api/bookings', input), u04.post('/api/bookings', input)]);
  });
  await S('สำเร็จ 1 พอดี (201) อีก 1 ได้ 409 "เวลานี้ถูกจองแล้ว" (ทันที)', async () => {
    expect.soft(results.map((r) => r.status).sort()).toEqual([201, 409]);
    const lost = results.find((r) => r.status === 409);
    expect.soft(lost?.json?.message).toBe('เวลานี้ถูกจองแล้ว');
  });
  await S('หลังรีโหลด: ตารางคิว 15 ต.ค. 11:00 ของ T04 มี 1 นัด', async () => {
    const rows = (await api.adminBookings('2026-10-15'))
      .filter((b) => b.time.startsWith('11:00') && b.status !== 'cancelled' && b.therapists.some((x: string) => x.startsWith('T04')));
    expect.soft(rows.length).toBe(1);
  });
});
