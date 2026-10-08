import { test, expect, ApiLog, PASSWORD, USERS, bookingBody, bookingDate, slotStatus, DAY } from './fixtures';
import type { APIRequestContext } from '@playwright/test';

const PROTECTED = [
  { method: 'GET', url: '/api/account' },
  { method: 'GET', url: '/api/wallet' },
  { method: 'GET', url: '/api/bookings' },
  { method: 'POST', url: '/api/courses' },
  { method: 'POST', url: '/api/bookings/6/cancel' },
] as const;

const MESSAGE = { th: 'กรุณาเข้าสู่ระบบ', en: 'Please log in' } as const;

/** อ่านสถานะของ nida (เจ้าของ SB00006) ด้วย context แยกที่ login แล้ว */
async function nidaState(newContext: () => Promise<APIRequestContext>) {
  const ctx = await newContext();
  try {
    const login = await ctx.post('/api/auth/login', { data: { email: USERS.nida, password: PASSWORD } });
    expect(login.status()).toBe(200);
    const bookings = (await (await ctx.get('/api/bookings')).json()).bookings as { code: string; status: string }[];
    const courses = (await (await ctx.get('/api/wallet')).json()).courses as unknown[];
    return { sb6: bookings.find((b) => b.code === 'SB00006')?.status, courseCount: courses.length };
  } finally {
    await ctx.dispose();
  }
}

test.describe('API', () => {
  test('TC-API-01 เรียก API ที่ต้อง login โดยไม่ login ต้องได้ 401', {
    tag: ['@API', '@P2'],
    annotation: {
      type: 'expected',
      description:
        'GET /api/account, /api/wallet, /api/bookings, POST /api/courses, POST /api/bookings/6/cancel ที่ไม่มี cookie sabai_session → HTTP 401 ' +
        '{"ok":false,"error":"LOGIN_REQUIRED","message":"กรุณาเข้าสู่ระบบ"} (lang=en → "Please log in") · ไม่มีข้อมูลสมาชิก · SB00006 ยัง confirmed และไม่มีคอร์สใหม่',
    },
  }, async ({ playwright, baseURL }, testInfo) => {
    const log = new ApiLog(testInfo);
    const newContext = () => playwright.request.newContext({ baseURL });
    const before = await nidaState(newContext);
    expect(before.sb6).toBe('confirmed');

    for (const lang of ['th', 'en'] as const) {
      // context ใหม่ ไม่มี sabai_session · lang=en ส่งผ่าน cookie
      const ctx = await playwright.request.newContext({
        baseURL,
        extraHTTPHeaders: lang === 'en' ? { cookie: 'lang=en' } : {},
      });
      for (const { method, url } of PROTECTED) {
        const res = method === 'GET' ? await ctx.get(url) : await ctx.post(url, { data: {} });
        const text = await log.record(method, url, res, `lang=${lang}, ไม่ login`);
        await test.step(`${method} ${url} (lang=${lang}) → 401 LOGIN_REQUIRED`, async () => {
          expect.soft(res.status(), `${method} ${url} lang=${lang}`).toBe(401);
          const body = JSON.parse(text);
          expect.soft(body, `${method} ${url} lang=${lang}`).toEqual({ ok: false, error: 'LOGIN_REQUIRED', message: MESSAGE[lang] });
          expect.soft(text, 'ต้องไม่มีข้อมูลสมาชิกในคำตอบ').not.toMatch(/nida|member|points|courses|bookings/i);
        });
      }
      await ctx.dispose();
    }

    const after = await nidaState(newContext);
    await log.save();
    await testInfo.attach('nida-state', { body: JSON.stringify({ before, after }, null, 2), contentType: 'application/json' });
    expect(after.sb6, 'SB00006 ต้องยัง confirmed').toBe('confirmed');
    expect(after.courseCount, 'ต้องไม่มีคอร์สใหม่เกิดขึ้น').toBe(before.courseCount);
  });

  test('TC-API-02 จองซ้อนพร้อมกัน: 2 คำขอพร้อมกันต้องสำเร็จ 1 คนพอดี', {
    tag: ['@API', '@P1'],
    annotation: [
      {
        type: 'expected',
        description:
          'POST /api/bookings 2 คำขอพร้อมกัน thai-massage therapistId 2 ทำ 10 รอบ (10:00–14:30) → ทุกรอบได้ 201 หนึ่งครั้ง และ 409 {"ok":false,"error":"SLOT_TAKEN","message":"เวลานี้ถูกจองแล้ว"} หนึ่งครั้ง (10/10) · ' +
          'availability ของรอบนั้นเป็น booked และมีการจอง 1 รายการต่อรอบ · Couple Suite aroma-oil 2 คนพร้อมกัน → 201 หนึ่งครั้ง และ 409 หนึ่งครั้ง',
      },
      {
        type: 'note',
        description:
          'นวดไทย 60 นาที ถ้า 10 รอบอยู่วันเดียวกัน รอบ 10:30 จะทับคิว 10:00 ที่เพิ่งจองได้ (BR-04) จึงแบ่งเป็น 2 วัน: 10:00/11:00/12:00/13:00/14:00 กับ 10:30/11:30/12:30/13:30/14:30 · ' +
          'ใช้วันแยกตามเบราว์เซอร์แทน 2026-10-09 / 10-12 และ Couple Suite รอบ 18:00 เพื่อไม่ให้ 3 เบราว์เซอร์ที่รันพร้อมกันชนกันเอง',
      },
    ],
  }, async ({ playwright, baseURL, browserName, apiLog }) => {
    const SLOT_TAKEN = { ok: false, error: 'SLOT_TAKEN', message: 'เวลานี้ถูกจองแล้ว' };
    // 2 context = ลูกค้า 2 คนคนละเครื่อง
    const a = await playwright.request.newContext({ baseURL });
    const b = await playwright.request.newContext({ baseURL });
    const dayA = bookingDate(browserName, DAY.API02);
    const dayB = bookingDate(browserName, DAY.BOOK07);
    const rounds = [
      ...['10:00', '11:00', '12:00', '13:00', '14:00'].map((t) => [dayA, t]),
      ...['10:30', '11:30', '12:30', '13:30', '14:30'].map((t) => [dayB, t]),
    ] as const;

    let ok = 0;
    for (const [i, [date, time]] of rounds.entries()) {
      await test.step(`รอบ ${i + 1}/10: ${date} ${time} therapistId 2 · ยิงพร้อมกัน 2 คำขอ`, async () => {
        const body = (name: string) => bookingBody({ service: 'thai-massage', date, time, therapistId: 2, guestName: name });
        const [r1, r2] = await Promise.all([a.post('/api/bookings', { data: body(`Guest A${i}`) }), b.post('/api/bookings', { data: body(`Guest B${i}`) })]);
        const t1 = await apiLog.record('POST', `/api/bookings ${date} ${time} therapist 2 (A)`, r1);
        const t2 = await apiLog.record('POST', `/api/bookings ${date} ${time} therapist 2 (B)`, r2);
        const statuses = [r1.status(), r2.status()].sort();
        expect.soft(statuses, `รอบ ${i + 1} (${date} ${time}): ต้องได้ 201 หนึ่งครั้ง และ 409 หนึ่งครั้ง`).toEqual([201, 409]);
        if (statuses[1] === 409) expect.soft(JSON.parse(r1.status() === 409 ? t1 : t2), `รอบ ${i + 1}: body ของ 409`).toEqual(SLOT_TAKEN);
        const st = await slotStatus(a, { service: 'thai-massage', date, therapistId: 2 }, time);
        expect.soft(st, `รอบ ${i + 1}: availability ${time} ของนักบำบัด 2 ต้องเป็น booked`).toBe('booked');
        if (statuses.join() === '201,409' && st === 'booked') ok++;
      });
    }
    expect(ok, 'จำนวนรอบที่สำเร็จ 1 คนพอดี').toBe(10);

    await test.step('Couple Suite: aroma-oil 2 คน 18:00 ยิงพร้อมกัน 2 คำขอ', async () => {
      const couple = (name: string) => bookingBody({ service: 'aroma-oil', people: 2, date: dayA, time: '18:00', guestName: name });
      const [r1, r2] = await Promise.all([a.post('/api/bookings', { data: couple('Couple A') }), b.post('/api/bookings', { data: couple('Couple B') })]);
      const t1 = await apiLog.record('POST', `/api/bookings couple ${dayA} 18:00 (A)`, r1);
      const t2 = await apiLog.record('POST', `/api/bookings couple ${dayA} 18:00 (B)`, r2);
      expect([r1.status(), r2.status()].sort(), 'Couple Suite: 201 หนึ่งครั้ง และ 409 หนึ่งครั้ง').toEqual([201, 409]);
      expect(JSON.parse(r1.status() === 409 ? t1 : t2)).toEqual(SLOT_TAKEN);
    });
    await a.dispose();
    await b.dispose();
  });
});
