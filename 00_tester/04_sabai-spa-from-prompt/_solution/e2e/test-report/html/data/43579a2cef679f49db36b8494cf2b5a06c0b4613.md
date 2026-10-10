# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: security.api.spec.ts >> TC-SEC-04 ออกจากระบบแล้วใช้ cookie เดิม
- Location: tests\fixtures.ts:169:3

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 401
Received: 200
```

# Test source

```ts
  1   | import { request } from '@playwright/test';
  2   | import { tc, test, expect, Api, USERS } from './fixtures';
  3   | 
  4   | const S = test.step;
  5   | 
  6   | // TC สิทธิ์/API ยิง API อย่างเดียว (แผน 6.2 ข้อ 3) — log ทุกคำขออยู่ที่ test-report/logs/<TC>.log
  7   | const courseBooking = (extra: Record<string, unknown> = {}) =>
  8   |   ({ type: 'course', serviceCode: 'K01', people: 1, date: '2026-10-20', time: '11:00', quotedTotal: 0, ...extra });
  9   | 
  10  | async function statusOf(api: Api, code: string) {
  11  |   const list = (await api.get('/api/me/bookings')).json.bookings as any[];
  12  |   return list.find((b) => b.code === code)?.status;
  13  | }
  14  | 
  15  | tc('TC-SEC-01', async ({ api }) => {
  16  |   const anon = await api.anon();
  17  |   await S('ไม่มี cookie: GET /api/me · /api/me/bookings · /api/wallet → 401', async () => {
  18  |     for (const url of ['/api/me', '/api/me/bookings', '/api/wallet']) {
  19  |       expect.soft((await anon.get(url)).status, url).toBe(401);
  20  |     }
  21  |   });
  22  |   await S('ไม่มี cookie: POST /api/bookings/B05/cancel → 401', async () => {
  23  |     expect.soft((await anon.post('/api/bookings/B05/cancel')).status).toBe(401);
  24  |   });
  25  |   await S('ไม่มี cookie: POST /api/bookings แบบคอร์ส K01 → 401', async () => {
  26  |     expect.soft((await anon.post('/api/bookings', courseBooking({ contactName: 'ไม่ล็อกอิน', contactPhone: '0812345678' }))).status).toBe(401);
  27  |   });
  28  |   await S('หลังรีโหลด: B05 ยัง "ยืนยัน" · ไม่มีนัดคอร์สใหม่', async () => {
  29  |     const u01 = await api.as('U01');
  30  |     expect.soft(await statusOf(u01, 'B05')).toBe('confirmed');
  31  |     const rows = (await api.adminBookings('2026-10-20')).filter((b) => b.viaCourse);
  32  |     expect.soft(rows.length).toBe(0);
  33  |   });
  34  | });
  35  | 
  36  | tc('TC-SEC-02', async ({ api }) => {
  37  |   await S('ไม่ล็อกอิน GET /api/photos/1 → 401', async () => {
  38  |     expect.soft((await (await api.anon()).get('/api/photos/1')).status).toBe(401);
  39  |   });
  40  |   await S('U04 GET /api/photos/1 → 403', async () => {
  41  |     expect.soft((await (await api.as('U04')).get('/api/photos/1')).status).toBe(403);
  42  |   });
  43  |   await S('U01 (เจ้าของ) GET /api/photos/1 → 200 เป็นรูป', async () => {
  44  |     const r = await (await api.as('U01')).get('/api/photos/1');
  45  |     expect.soft(r.status).toBe(200);
  46  |     expect.soft(r.headers['content-type'] ?? '').toMatch(/^image\//);
  47  |   });
  48  | });
  49  | 
  50  | tc('TC-SEC-03', async ({ api }) => {
  51  |   const u01 = await api.as('U01');
  52  |   await S('U01 GET /api/admin/bookings?date=2026-10-12 → 403', async () => {
  53  |     expect.soft((await u01.get('/api/admin/bookings?date=2026-10-12')).status).toBe(403);
  54  |   });
  55  |   await S('U01 POST /api/admin/bookings/B06/complete → 403', async () => {
  56  |     expect.soft((await u01.post('/api/admin/bookings/B06/complete', {})).status).toBe(403);
  57  |   });
  58  |   await S('หลังรีโหลด: B06 ยัง "ยืนยัน" · แต้ม U01 ยัง 99', async () => {
  59  |     expect.soft(await statusOf(u01, 'B06')).toBe('confirmed');
  60  |     expect.soft((await u01.get('/api/me')).json.points).toBe(99);
  61  |   });
  62  | });
  63  | 
  64  | tc('TC-SEC-04', async ({ api, baseURL }) => {
  65  |   const u01 = await api.as('U01');
  66  |   let state: Awaited<ReturnType<typeof u01.ctx.storageState>>;
  67  |   await S('U01 ล็อกอิน → เก็บ cookie ไว้', async () => {
  68  |     state = await u01.ctx.storageState();
  69  |     expect(state.cookies.some((c) => c.name === 'sabai_session')).toBe(true);
  70  |     expect.soft((await u01.get('/api/me')).status, 'ก่อน logout').toBe(200);
  71  |   });
  72  |   await S('POST /api/auth/logout', async () => {
  73  |     expect.soft((await u01.post('/api/auth/logout')).status).toBe(200);
  74  |   });
  75  |   await S('GET /api/me ด้วย cookie เดิม → 401', async () => {
  76  |     const ctx = await request.newContext({ baseURL, storageState: state });
  77  |     const old = new Api(ctx, 'cookie เดิมของ U01', api.log);
> 78  |     expect.soft((await old.get('/api/me')).status).toBe(401);
      |                                                    ^ Error: expect(received).toBe(expected) // Object.is equality
  79  |     await ctx.dispose();
  80  |   });
  81  | });
  82  | 
  83  | tc('TC-SEC-05', async ({ api }) => {
  84  |   const u01 = await api.as('U01');
  85  |   const u04 = await api.as('U04');
  86  |   const c01 = ((await u01.get('/api/wallet')).json.courses as any[]).find((c) => c.code === 'C01');
  87  |   await S('U04 POST /api/bookings/B05/cancel (นัดของ U01) → 403/404', async () => {
  88  |     expect.soft([403, 404]).toContain((await u04.post('/api/bookings/B05/cancel')).status);
  89  |   });
  90  |   await S('U04 POST /api/bookings แบบคอร์สด้วย C01 (ของ U01) 20 ต.ค. 11:00 → 403/404', async () => {
  91  |     expect.soft([403, 404]).toContain((await u04.post('/api/bookings', courseBooking({ coursePurchaseId: c01?.id }))).status);
  92  |   });
  93  |   await S('หลังรีโหลด: B05 ยัง "ยืนยัน" · Wallet U01 ยัง "เหลือ 7 จาก 11 ครั้ง" · ไม่มีนัดใหม่ 20 ต.ค. 11:00', async () => {
  94  |     expect.soft(await statusOf(u01, 'B05')).toBe('confirmed');
  95  |     const after = ((await u01.get('/api/wallet')).json.courses as any[]).find((c) => c.code === 'C01');
  96  |     expect.soft(after?.remainingLabel).toBe('เหลือ 7 จาก 11 ครั้ง');
  97  |     const rows = (await api.adminBookings('2026-10-20')).filter((b) => b.time.startsWith('11:00'));
  98  |     expect.soft(rows.length).toBe(0);
  99  |   });
  100 | });
  101 | 
  102 | void USERS;
  103 | 
```