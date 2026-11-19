/**
 * TEST-PLAN 5.7 สิทธิ์ของแต่ละบทบาท (TC-7-01 … TC-7-04) · all environment A (runs on the mock stack :3421).
 * Expected values come only from the plan's "ผลที่คาดหวัง" column.
 * Every account uses its own session (apiAs / pageAs) and its W5 is checked first.
 */
import * as fs from 'fs';
import type { APIRequestContext, Page, TestInfo } from '@playwright/test';
import {
  test, expect, apiAs, reset, clientId, categoryId, upload, queue, pageAs,
  pauseReader, resumeReader, evidence, shot, okFiles, M_URL, U, PASSWORD, UserKey,
} from './lib/rd';

// ---------------------------------------------------------------- local helpers
const ROLE: Record<UserKey, { role: string; label: string }> = {
  U01: { role: 'staff', label: 'พนักงานบัญชี' },
  U02: { role: 'staff', label: 'พนักงานบัญชี' },
  U03: { role: 'lead', label: 'หัวหน้าทีมบัญชี' },
  U04: { role: 'owner', label: 'เจ้าของสำนักงาน' },
  U05: { role: 'client', label: 'ลูกค้า' },
  U06: { role: 'client', label: 'ลูกค้า' },
};

/** apiAs + W5 check (plan 5.7: "เริ่มจาก session ว่างและตรวจ W5 ก่อน"). */
async function session(user: UserKey, testInfo: TestInfo): Promise<APIRequestContext> {
  const ctx = await apiAs(M_URL, user);
  const r = await ctx.get('/api/me');
  const j = await r.json().catch(() => ({}));
  await evidence(testInfo, `W5 ${user}`, { status: r.status(), user: j.user, permissions: j.permissions });
  expect(r.status(), `W5 ${user}`).toBe(200);
  expect(j.user?.role, `W5 ${user} role`).toBe(ROLE[user].role);
  return ctx;
}

/** All seeded receipts S-01..S-08 by short code (needs an office session). */
async function seeded(office: APIRequestContext): Promise<Record<string, any>> {
  const j = await (await office.get('/api/receipts?limit=500')).json();
  const out: Record<string, any> = {};
  for (const r of j.receipts ?? []) {
    const m = /^(S-0\d)\.jpg$/.exec(r.fileName ?? '');
    if (m) out[m[1]] = r;
  }
  for (const k of ['S-01', 'S-02', 'S-03', 'S-04', 'S-05', 'S-06', 'S-07', 'S-08']) if (!out[k]) throw new Error(`seed ${k} not found`);
  return out;
}

async function call(ctx: APIRequestContext, method: 'GET' | 'POST' | 'PATCH', url: string, data?: unknown) {
  const r = method === 'GET' ? await ctx.get(url) : method === 'POST' ? await ctx.post(url, data === undefined ? {} : { data }) : await ctx.patch(url, { data });
  const text = await r.text().catch(() => '');
  let json: any = null;
  try { json = JSON.parse(text); } catch { /* CSV / image / html */ }
  return { status: r.status(), json, text, contentType: r.headers()['content-type'] ?? '' };
}

/** Money string -> satang (integer). */
function satang(s: string | number | null | undefined): number {
  const t = String(s ?? '').replace(/[,\s฿บาท]/g, '');
  const m = t.match(/-?\d+(\.\d+)?/);
  return m ? Math.round(Number(m[0]) * 100) : NaN;
}

/** Minimal CSV parser (handles quotes and BOM). */
function parseCsv(text: string): string[][] {
  const s = text.replace(/^﻿/, '');
  const rows: string[][] = []; let row: string[] = []; let f = ''; let q = false;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (q) {
      if (c === '"' && s[i + 1] === '"') { f += '"'; i++; } else if (c === '"') q = false; else f += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(f); f = ''; }
    else if (c === '\n' || c === '\r') { if (c === '\r' && s[i + 1] === '\n') i++; row.push(f); f = ''; if (row.some(x => x !== '')) rows.push(row); row = []; }
    else f += c;
  }
  if (f !== '' || row.length) { row.push(f); if (row.some(x => x !== '')) rows.push(row); }
  return rows;
}

/** Sum of the `total` column of a W18 CSV (satang) + row count (excluding a possible summary row without receipt_date). */
function csvTotal(text: string): { header: string[]; rows: number; sum: number } {
  const rows = parseCsv(text);
  const header = (rows[0] ?? []).map(h => h.trim());
  const ti = header.indexOf('total');
  const di = header.indexOf('receipt_date');
  const data = rows.slice(1).filter(r => di < 0 || /^\d{4}-\d{2}-\d{2}/.test(r[di] ?? ''));
  return { header, rows: data.length, sum: data.reduce((a, r) => a + satang(r[ti]), 0) };
}

/** Pick an option of a <select> by UUID value, else by label text. */
async function pickOption(page: Page, testId: string, uuid: string, labels: string[]) {
  const sel = page.getByTestId(testId);
  await sel.waitFor({ state: 'visible' });
  const opts = await sel.locator('option').evaluateAll(os => os.map(o => ({ v: (o as HTMLOptionElement).value, t: o.textContent || '' })));
  const hit = opts.find(o => o.v === uuid) || opts.find(o => labels.some(l => o.t.includes(l)));
  if (!hit) throw new Error(`${labels[0]} not in ${testId}: ` + JSON.stringify(opts));
  await sel.selectOption(hit.v);
}

// ---------------------------------------------------------------- tests
test.describe('5.7 สิทธิ์ของแต่ละบทบาท', () => {

  test('TC-7-01 ใครตั้งงานด่วนได้ ทั้ง W10 และ W7', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const lead = await session('U03', testInfo);
    const staff = await session('U01', testInfo);
    const owner = await session('U04', testInfo);
    const client = await session('U05', testInfo);
    const cl01 = await clientId(lead, 'CL-01');
    pauseReader();
    try {
      // U-03 uploads a CL-01 batch of 5 files, not urgent
      const up = await upload(lead, { clientId: cl01, files: okFiles(5, 1, 'ok-100') });
      await evidence(testInfo, 'U-03 W7 5 files (not urgent)', up);
      expect(up.status, 'U-03 อัปโหลดชุด CL-01 5 ไฟล์').toBe(201);
      const batchId: string = up.json.batchId ?? up.json.batch?.id ?? up.json.id;
      expect(batchId, 'batchId').toBeTruthy();
      const countBefore = (await (await lead.get('/api/receipts?limit=1')).json()).count;

      // ① W10 from U-01 · U-04 · U-05
      const table: any[] = [];
      for (const [who, ctx] of [['U-01', staff], ['U-04', owner], ['U-05', client]] as const) {
        const r = await call(ctx, 'POST', `/api/batches/${batchId}/urgent`);
        table.push({ step: '①', who, req: `POST /api/batches/{id}/urgent`, status: r.status, error: r.json?.error });
        expect.soft(r.status, `① W10 ${who} -> 403`).toBe(403);
        expect.soft(r.json?.error, `① W10 ${who} error`).toBe('forbidden');
      }
      // ② W7 urgent=true 5 files from U-01 (CL-01) · U-05 (own shop) · U-04
      const tries: [string, APIRequestContext, number][] = [['U-01', staff, 101], ['U-05', client, 111], ['U-04', owner, 121]];
      for (const [who, ctx, from] of tries) {
        const r = await upload(ctx, { clientId: cl01, files: okFiles(5, from, 'ok-100'), urgent: true });
        table.push({ step: '②', who, req: 'POST /api/batches urgent=true 5 files', status: r.status, error: r.json?.error, accepted: r.json?.accepted });
        expect.soft(r.status, `② W7 urgent ${who} -> 403`).toBe(403);
        expect.soft(r.json?.error, `② W7 urgent ${who} error`).toBe('forbidden');
      }
      await evidence(testInfo, '①② requests -> status', table);

      // no new receipt from ②, nothing urgent, counter still 0
      const recs = await (await lead.get('/api/receipts?limit=500')).json();
      const batches = await (await lead.get('/api/batches')).json();
      const q1 = await queue(lead);
      await evidence(testInfo, 'after ①② W11/W8/W23', { count: recs.count, countBefore, batches: batches.batches?.map((b: any) => ({ id: b.id, priority: b.priority, accepted: b.accepted, urgentSetAt: b.urgentSetAt })), urgent: q1.urgent });
      expect.soft(recs.count, 'ไม่มีใบใหม่ถูกรับจากคำขอ ② (8 ตั้งต้น + 5 ของ U-03 = 13)').toBe(13);
      expect.soft(recs.count, 'จำนวนใบก่อนและหลัง ② เท่ากัน').toBe(countBefore);
      const urgentRecs = (recs.receipts ?? []).filter((r: any) => r.priority === 'urgent');
      const urgentBatches = (batches.batches ?? []).filter((b: any) => b.priority === 'urgent' || b.urgentSetAt);
      expect.soft(urgentRecs.length, 'ไม่มีใบใดเป็นงานด่วน').toBe(0);
      expect.soft(urgentBatches.length, 'ไม่มีชุดใดเป็นงานด่วน').toBe(0);
      expect.soft(q1.urgent?.usedToday, 'ตัวนับงานด่วนวันนี้ยังเป็น 0').toBe(0);

      // U-01 pages: no batch-urgent-button, no upload-urgent-checkbox
      const { context, page } = await pageAs(browser, M_URL, 'U01');
      try {
        await page.goto(`/batches/${batchId}`);
        await page.getByTestId('batch-count-accepted').waitFor({ state: 'visible' });
        await expect.soft(page.getByTestId('batch-urgent-button'), 'หน้าชุดของ U-01 ไม่มี batch-urgent-button').toHaveCount(0);
        await shot(testInfo, page, 'U-01 /batches/[id] no urgent button');
        await page.goto('/upload');
        await page.getByTestId('upload-submit-button').waitFor({ state: 'visible' });
        await expect.soft(page.getByTestId('upload-urgent-checkbox'), 'หน้าอัปโหลดของ U-01 ไม่มี upload-urgent-checkbox').toHaveCount(0);
        await shot(testInfo, page, 'U-01 /upload no urgent checkbox');
      } finally { await context.close(); }

      // ③ W10 from U-03
      const r3 = await call(lead, 'POST', `/api/batches/${batchId}/urgent`);
      const q2 = await queue(lead);
      const b3 = await (await lead.get(`/api/batches/${batchId}`)).json().catch(() => ({}));
      await evidence(testInfo, '③ U-03 W10', { status: r3.status, json: r3.json, urgent: q2.urgent, batch: b3.batch ?? b3 });
      expect.soft(r3.status, '③ U-03 ตั้งงานด่วนได้ (2xx)').toBeGreaterThanOrEqual(200);
      expect.soft(r3.status, '③ U-03 ตั้งงานด่วนได้ (2xx)').toBeLessThan(300);
      expect.soft(q2.urgent?.usedToday, '③ ตัวนับ 0 + 1 = 1').toBe(1);
    } finally {
      resumeReader();
      for (const c of [lead, staff, owner, client]) await c.dispose();
    }
  });

  test('TC-7-02 ผู้ไม่เข้าสู่ระบบ และการเข้าสู่ระบบ', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    // real ids taken from an office session beforehand
    const office = await session('U04', testInfo);
    const s = await seeded(office);
    const cl01 = await clientId(office, 'CL-01');
    const cl02 = await clientId(office, 'CL-02');
    const s01 = s['S-01'];

    // ① empty session: pages -> /login
    const anonCtx = await browser.newContext({ baseURL: M_URL, locale: 'th-TH', timezoneId: 'Asia/Bangkok' });
    const pageRows: any[] = [];
    try {
      const page = await anonCtx.newPage();
      for (const p of ['/upload', '/batches', '/receipts', '/unreadable', '/overdue', '/reports', '/insights', '/portal']) {
        await page.goto(p);
        await page.waitForLoadState('domcontentloaded');
        const final = new URL(page.url());
        pageRows.push({ page: p, finalUrl: final.pathname + final.search });
        expect.soft(final.pathname, `① หน้า ${p} พาไป /login`).toBe('/login');
      }
      await shot(testInfo, page, '① anonymous -> /login');
    } finally { await anonCtx.close(); }
    await evidence(testInfo, '① pages (anonymous) -> final URL', pageRows);

    // ① empty session: APIs -> 401 unauthenticated
    const anon = await apiAs(M_URL, null);
    const apis: [string, string][] = [
      ['W5', '/api/me'],
      ['W6', '/api/clients'],
      ['W8', '/api/batches'],
      ['W9', `/api/batches/${s01.batchId}`],
      ['W11', '/api/receipts'],
      ['W12', `/api/receipts/${s01.id}`],
      ['W13', `/api/receipts/${s01.id}/image`],
      ['W17', `/api/receipts/${s01.id}/history`],
      ['W18', `/api/reports/monthly?clientId=${cl01}&month=2026-11`],
      ['W19', `/api/reports/categories?month=2026-11&clientId=${cl01}`],
      ['W20', '/api/reports/reconcile'],
      ['W21', '/api/reports/review-time'],
      ['W22', '/api/reports/gpu'],
      ['W23', '/api/queue'],
    ];
    const apiRows: any[] = [];
    let opened = 0;
    for (const [w, url] of apis) {
      const r = await call(anon, 'GET', url);
      apiRows.push({ w, request: `GET ${url}`, status: r.status, error: r.json?.error });
      if (r.status < 400) opened++;
      expect.soft(r.status, `① ${w} GET ${url} -> 401`).toBe(401);
      expect.soft(r.json?.error, `① ${w} error`).toBe('unauthenticated');
    }
    const h = await call(anon, 'GET', '/api/health');
    apiRows.push({ w: 'W1', request: 'GET /api/health', status: h.status, body: h.json });
    await evidence(testInfo, '① API (anonymous) request -> status', apiRows);
    expect.soft(opened, '① เปิดได้ 0 รายการ').toBe(0);
    expect.soft(h.status, '① /api/health 200').toBe(200);
    expect.soft(h.text, '① /api/health ไม่มีข้อมูลใบเสร็จ').not.toMatch(/S-0\d|\.jpg|receipts?"\s*:\s*\[|"total"|merchant|fileName/i);
    await anon.dispose();

    // ② log in all 6 accounts, each in its own context
    const roleRows: any[] = [];
    for (const user of ['U01', 'U02', 'U03', 'U04', 'U05', 'U06'] as UserKey[]) {
      const { context, page } = await pageAs(browser, M_URL, user);
      try {
        const role = page.getByTestId('nav-user-role');
        await role.waitFor({ state: 'visible' });
        const text = (await role.innerText()).trim();
        const dataRole = await role.getAttribute('data-role');
        const me = await (await context.request.get('/api/me')).json().catch(() => ({}));
        roleRows.push({ user, email: U[user], navUserRole: text, dataRole, me: me.user });
        expect.soft(dataRole, `② ${user} nav-user-role data-role`).toBe(ROLE[user].role);
        expect.soft(text, `② ${user} nav-user-role text`).toContain(ROLE[user].label);
        expect.soft(me.user?.role, `② ${user} W5 role`).toBe(ROLE[user].role);
        if (user === 'U05') {
          expect.soft(me.user?.clientId, '② U-05 ผูก CL-01 (clientId)').toBe(cl01);
          expect.soft(me.user?.clientName, '② U-05 ผูก CL-01 (clientName)').toBe('ร้านข้าวแกงสมชาย');
        } else if (user === 'U06') {
          expect.soft(me.user?.clientId, '② U-06 ผูก CL-02 (clientId)').toBe(cl02);
          expect.soft(me.user?.clientName, '② U-06 ผูก CL-02 (clientName)').toBe('ร้านกาแฟมะลิ');
        } else {
          expect.soft(me.user?.clientId ?? null, `② ${user} ไม่ผูกร้าน`).toBeNull();
        }
        await shot(testInfo, page, `② ${user} logged in`);
      } finally { await context.close(); }
    }
    await evidence(testInfo, '② roles', roleRows);

    // ③ new empty session, wrong password for U-01, then W5
    const ctx3 = await browser.newContext({ baseURL: M_URL, locale: 'th-TH', timezoneId: 'Asia/Bangkok' });
    try {
      const page = await ctx3.newPage();
      await page.goto('/login');
      await page.getByTestId('login-email-input').fill(U.U01);
      await page.getByTestId('login-password-input').fill(PASSWORD + '-wrong');
      await page.getByTestId('login-submit-button').click();
      await expect.soft(page.getByTestId('login-error'), '③ login-error แสดง').toBeVisible();
      await shot(testInfo, page, '③ wrong password');
      const me = await ctx3.request.get('/api/me');
      const body = await me.json().catch(() => ({}));
      await evidence(testInfo, '③ W5 after wrong password', { status: me.status(), body, url: page.url() });
      expect.soft(me.status(), '③ W5 ได้ 401').toBe(401);
    } finally { await ctx3.close(); }
    await office.dispose();
  });

  test('TC-7-03 แก้ ยืนยัน เปิดกลับ ตามบทบาท', { tag: ['@P1', '@A'] }, async ({}, testInfo) => {
    await reset(M_URL);
    const lead = await session('U03', testInfo);
    const owner = await session('U04', testInfo);
    const client = await session('U05', testInfo);
    try {
      const s = await seeded(lead);
      const s06 = s['S-06'].id; const s02 = s['S-02'].id;
      const cat = await categoryId(lead, 'CAT-04');
      const hist = async (id: string) => (await (await lead.get(`/api/receipts/${id}/history`)).json());
      const h06a = await hist(s06); const h02a = await hist(s02);

      const rows: any[] = [];
      const reqs: [string, APIRequestContext, 'POST' | 'PATCH', string, unknown][] = [
        ['U-04', owner, 'PATCH', `/api/receipts/${s06}`, { total: '600.00' }],
        ['U-04', owner, 'POST', `/api/receipts/${s06}/confirm`, { totalChecked: true, categoryId: cat }],
        ['U-05', client, 'PATCH', `/api/receipts/${s06}`, { total: '600.00' }],
        ['U-05', client, 'POST', `/api/receipts/${s06}/confirm`, { totalChecked: true, categoryId: cat }],
        ['U-04', owner, 'POST', `/api/receipts/${s02}/reopen`, undefined],
      ];
      for (const [who, ctx, m, url, data] of reqs) {
        const r = await call(ctx, m, url, data);
        rows.push({ who, request: `${m} ${url.replace(s06, '{S-06}').replace(s02, '{S-02}')}`, status: r.status, error: r.json?.error });
        expect.soft(r.status >= 400 && r.status < 500, `${who} ${m} ${url.replace(s06, 'S-06').replace(s02, 'S-02')} ถูกปฏิเสธ (got ${r.status})`).toBe(true);
      }
      await evidence(testInfo, 'requests -> status', rows);

      const r06 = (await (await lead.get(`/api/receipts/${s06}`)).json()).receipt;
      const r02 = (await (await lead.get(`/api/receipts/${s02}`)).json()).receipt;
      const h06b = await hist(s06); const h02b = await hist(s02);
      await evidence(testInfo, 'after', { S06: r06, S02: r02, h06a, h06b, h02a, h02b });
      expect.soft(r06?.status, 'S-06 ยังเป็นรอตรวจ').toBe('review');
      expect.soft(satang(r06?.total), 'S-06 ยอด 500.00 ไม่เปลี่ยน').toBe(50000);
      expect.soft(r02?.status, 'S-02 ยังยืนยันแล้ว').toBe('confirmed');
      expect.soft((h06b.edits ?? []).length, 'S-06 ประวัติการแก้ไม่มีแถวใหม่').toBe((h06a.edits ?? []).length);
      expect.soft((h06b.events ?? []).length, 'S-06 ประวัติเหตุการณ์ไม่มีแถวใหม่').toBe((h06a.events ?? []).length);
      expect.soft((h02b.edits ?? []).length, 'S-02 ประวัติการแก้ไม่มีแถวใหม่').toBe((h02a.edits ?? []).length);
      expect.soft((h02b.events ?? []).length, 'S-02 ประวัติเหตุการณ์ไม่มีแถวใหม่').toBe((h02a.events ?? []).length);
    } finally {
      for (const c of [lead, owner, client]) await c.dispose();
    }
  });

  test('TC-7-04 ไฟล์สรุปตามบทบาท', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const owner = await session('U04', testInfo);
    const client = await session('U05', testInfo);
    const cl01 = await clientId(owner, 'CL-01');
    const cl02 = await clientId(owner, 'CL-02');
    try {
      // reference of U-04 (TC-6-01: 1,340.00)
      const ref = await call(owner, 'GET', `/api/reports/monthly?clientId=${cl01}&month=2026-11`);
      const refT = csvTotal(ref.text);
      await evidence(testInfo, 'U-04 W18 CL-01 2026-11 (reference)', ref.text);

      for (const user of ['U01', 'U03'] as UserKey[]) {
        await (await session(user, testInfo)).dispose();
        const { context, page } = await pageAs(browser, M_URL, user);
        try {
          await page.goto('/reports');
          await pickOption(page, 'report-client-select', cl01, ['CL-01', 'ร้านข้าวแกงสมชาย']);
          await page.getByTestId('report-month-input').fill('2026-11');
          await page.getByTestId('report-preview-button').click();
          await page.getByTestId('report-total').waitFor({ state: 'visible' });
          await expect.soft(page.getByTestId('report-total'), `${user} report-total 1,340.00`).toContainText(/1,?340\.00/);
          const shown = await page.getByTestId('report-total').innerText();
          await shot(testInfo, page, `${user} /reports CL-01 2026-11`);
          const [dl] = await Promise.all([page.waitForEvent('download'), page.getByTestId('report-export-button').click()]);
          const fp = await dl.path();
          const text = fp ? fs.readFileSync(fp, 'utf8') : '';
          const t = csvTotal(text);
          await evidence(testInfo, `${user} CSV CL-01 2026-11 (${dl.suggestedFilename()})`, text);
          await evidence(testInfo, `${user} totals`, { shown, csvSumSatang: t.sum, rows: t.rows, refSumSatang: refT.sum });
          expect.soft(t.sum, `${user} CSV ยอดรวม 1,340.00`).toBe(134000);
          expect.soft(t.sum, `${user} CSV ยอดเท่ากับของ U-04`).toBe(refT.sum);
        } finally { await context.close(); }
      }

      // U-05 W18 for CL-02
      const rows: any[] = [];
      for (const q of [`clientId=${cl02}&month=2026-11`, `clientId=CL-02&month=2026-11`]) {
        const r = await call(client, 'GET', `/api/reports/monthly?${q}`);
        rows.push({ request: `GET /api/reports/monthly?${q.replace(cl02, '{CL-02 uuid}')}`, status: r.status, contentType: r.contentType, body: r.text.slice(0, 500) });
        expect.soft(r.status >= 400 && r.status < 500, `U-05 W18 ${q.replace(cl02, 'CL-02')} ถูกปฏิเสธ (got ${r.status})`).toBe(true);
        expect.soft(r.text, `U-05 W18 ${q.replace(cl02, 'CL-02')} ไม่มีตัวเลข 999.00`).not.toMatch(/999(\.00)?/);
      }
      await evidence(testInfo, 'U-05 W18 requests -> status', rows);
    } finally {
      await owner.dispose(); await client.dispose();
    }
  });
});
