import { request } from '@playwright/test';
import { tc, test, expect, Api, USERS } from './fixtures';

const S = test.step;

// TC สิทธิ์/API ยิง API อย่างเดียว (แผน 6.2 ข้อ 3) — log ทุกคำขออยู่ที่ test-report/logs/<TC>.log
const courseBooking = (extra: Record<string, unknown> = {}) =>
  ({ type: 'course', serviceCode: 'K01', people: 1, date: '2026-10-20', time: '11:00', quotedTotal: 0, ...extra });

async function statusOf(api: Api, code: string) {
  const list = (await api.get('/api/me/bookings')).json.bookings as any[];
  return list.find((b) => b.code === code)?.status;
}

tc('TC-SEC-01', async ({ api }) => {
  const anon = await api.anon();
  await S('ไม่มี cookie: GET /api/me · /api/me/bookings · /api/wallet → 401', async () => {
    for (const url of ['/api/me', '/api/me/bookings', '/api/wallet']) {
      expect.soft((await anon.get(url)).status, url).toBe(401);
    }
  });
  await S('ไม่มี cookie: POST /api/bookings/B05/cancel → 401', async () => {
    expect.soft((await anon.post('/api/bookings/B05/cancel')).status).toBe(401);
  });
  await S('ไม่มี cookie: POST /api/bookings แบบคอร์ส K01 → 401', async () => {
    expect.soft((await anon.post('/api/bookings', courseBooking({ contactName: 'ไม่ล็อกอิน', contactPhone: '0812345678' }))).status).toBe(401);
  });
  await S('หลังรีโหลด: B05 ยัง "ยืนยัน" · ไม่มีนัดคอร์สใหม่', async () => {
    const u01 = await api.as('U01');
    expect.soft(await statusOf(u01, 'B05')).toBe('confirmed');
    const rows = (await api.adminBookings('2026-10-20')).filter((b) => b.viaCourse);
    expect.soft(rows.length).toBe(0);
  });
});

tc('TC-SEC-02', async ({ api }) => {
  await S('ไม่ล็อกอิน GET /api/photos/1 → 401', async () => {
    expect.soft((await (await api.anon()).get('/api/photos/1')).status).toBe(401);
  });
  await S('U04 GET /api/photos/1 → 403', async () => {
    expect.soft((await (await api.as('U04')).get('/api/photos/1')).status).toBe(403);
  });
  await S('U01 (เจ้าของ) GET /api/photos/1 → 200 เป็นรูป', async () => {
    const r = await (await api.as('U01')).get('/api/photos/1');
    expect.soft(r.status).toBe(200);
    expect.soft(r.headers['content-type'] ?? '').toMatch(/^image\//);
  });
});

tc('TC-SEC-03', async ({ api }) => {
  const u01 = await api.as('U01');
  await S('U01 GET /api/admin/bookings?date=2026-10-12 → 403', async () => {
    expect.soft((await u01.get('/api/admin/bookings?date=2026-10-12')).status).toBe(403);
  });
  await S('U01 POST /api/admin/bookings/B06/complete → 403', async () => {
    expect.soft((await u01.post('/api/admin/bookings/B06/complete', {})).status).toBe(403);
  });
  await S('หลังรีโหลด: B06 ยัง "ยืนยัน" · แต้ม U01 ยัง 99', async () => {
    expect.soft(await statusOf(u01, 'B06')).toBe('confirmed');
    expect.soft((await u01.get('/api/me')).json.points).toBe(99);
  });
});

tc('TC-SEC-04', async ({ api, baseURL }) => {
  // KNOWN-ISSUE (ส.ค. 69): ล้มตั้งแต่ส่งมอบ ยังไม่ได้แก้ · แก้แล้วให้ลบบรรทัด test.fail ออก
  test.fail(true, 'KNOWN-ISSUE: logout แล้ว cookie เดิมยังใช้ได้ (session ไม่ถูกเพิกถอน)');
  const u01 = await api.as('U01');
  let state: Awaited<ReturnType<typeof u01.ctx.storageState>>;
  await S('U01 ล็อกอิน → เก็บ cookie ไว้', async () => {
    state = await u01.ctx.storageState();
    expect(state.cookies.some((c) => c.name === 'sabai_session')).toBe(true);
    expect.soft((await u01.get('/api/me')).status, 'ก่อน logout').toBe(200);
  });
  await S('POST /api/auth/logout', async () => {
    expect.soft((await u01.post('/api/auth/logout')).status).toBe(200);
  });
  await S('GET /api/me ด้วย cookie เดิม → 401', async () => {
    const ctx = await request.newContext({ baseURL, storageState: state });
    const old = new Api(ctx, 'cookie เดิมของ U01', api.log);
    expect.soft((await old.get('/api/me')).status).toBe(401);
    await ctx.dispose();
  });
});

tc('TC-SEC-05', async ({ api }) => {
  const u01 = await api.as('U01');
  const u04 = await api.as('U04');
  const c01 = ((await u01.get('/api/wallet')).json.courses as any[]).find((c) => c.code === 'C01');
  await S('U04 POST /api/bookings/B05/cancel (นัดของ U01) → 403/404', async () => {
    expect.soft([403, 404]).toContain((await u04.post('/api/bookings/B05/cancel')).status);
  });
  await S('U04 POST /api/bookings แบบคอร์สด้วย C01 (ของ U01) 20 ต.ค. 11:00 → 403/404', async () => {
    expect.soft([403, 404]).toContain((await u04.post('/api/bookings', courseBooking({ coursePurchaseId: c01?.id }))).status);
  });
  await S('หลังรีโหลด: B05 ยัง "ยืนยัน" · Wallet U01 ยัง "เหลือ 7 จาก 11 ครั้ง" · ไม่มีนัดใหม่ 20 ต.ค. 11:00', async () => {
    expect.soft(await statusOf(u01, 'B05')).toBe('confirmed');
    const after = ((await u01.get('/api/wallet')).json.courses as any[]).find((c) => c.code === 'C01');
    expect.soft(after?.remainingLabel).toBe('เหลือ 7 จาก 11 ครั้ง');
    const rows = (await api.adminBookings('2026-10-20')).filter((b) => b.time.startsWith('11:00'));
    expect.soft(rows.length).toBe(0);
  });
});

void USERS;
