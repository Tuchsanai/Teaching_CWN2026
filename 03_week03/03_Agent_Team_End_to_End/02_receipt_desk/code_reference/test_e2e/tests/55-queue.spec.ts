/**
 * TEST-PLAN 5.5 สถานะงานในคิวและใบที่อ่านไม่ได้ (TC-5-01 … TC-5-10).
 * A / M run on the mock stack :3421 · TC-5-09 (R) on :3420 with the real model · TC-5-08 ★ release round only (skipped).
 * Expected values come only from the plan's "ผลที่คาดหวัง" column.
 */
import * as fs from 'fs';
import { execFile } from 'child_process';
import * as path from 'path';
import type { APIRequestContext, Page, Response, TestInfo } from '@playwright/test';
import {
  test, expect, apiAs, reset, clientId, upload, waitStatus, confirm, reconcile, queue, pageAs,
  pauseReader, resumeReader, restartDbAndQueue, gpu, evidence, shot, pendingAP, okFiles, dataFile,
  M_URL, R_URL, REAL_IMAGES,
} from './lib/rd';

// ---------------------------------------------------------------- local helpers
/** First (possibly negative) number in a text, commas removed. NaN when none. */
function num(s: string | null | undefined): number {
  const m = (s ?? '').replace(/,/g, '').match(/-?\d+(\.\d+)?/);
  return m ? Number(m[0]) : NaN;
}
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

/** Pick a client in `upload-client-select` (option value = UUID, else label with the code). */
async function selectClient(page: Page, uuid: string, code = 'CL-01') {
  const sel = page.getByTestId('upload-client-select');
  await expect.poll(() => sel.locator('option').count(), { message: 'client options loaded', timeout: 15_000 }).toBeGreaterThan(1);
  const opts = await sel.locator('option').evaluateAll(os => os.map(o => ({ v: (o as HTMLOptionElement).value, t: o.textContent || '' })));
  const hit = opts.find(o => o.v === uuid) || opts.find(o => o.t.includes(code));
  if (!hit) throw new Error(`${code} not in upload-client-select: ` + JSON.stringify(opts));
  await sel.selectOption(hit.v);
}

type PageUpload = { sent: boolean; status: number | null; json: any };
/** Upload through /upload; returns the W7 response the page actually sent (sent=false if blocked before sending). */
async function pageUpload(page: Page, clientUuid: string, files: string[]): Promise<PageUpload> {
  await page.goto('/upload');
  await selectClient(page, clientUuid);
  await page.getByTestId('upload-file-input').setInputFiles(files.map(f => (path.isAbsolute(f) ? f : dataFile(f))));
  const respP: Promise<Response | null> = page
    .waitForResponse(r => r.url().includes('/api/batches') && r.request().method() === 'POST', { timeout: 120_000 })
    .catch(() => null);
  await page.getByTestId('upload-submit-button').click();
  const resp = await respP;
  const result = page.locator('[data-testid="upload-accepted-count"], [data-testid="upload-full-message"], [data-testid="upload-error"]');
  await result.first().waitFor({ state: 'visible', timeout: 60_000 }).catch(() => undefined);
  const json = resp ? await resp.json().catch(() => ({})) : null;
  return { sent: !!resp, status: resp ? resp.status() : null, json };
}

/** {fileName: id} from a W7 success JSON. */
function idsByName(json: any): Record<string, string> {
  const ids: Record<string, string> = {};
  for (const r of json?.receipts || []) ids[r.fileName] = r.id;
  return ids;
}

async function receipt(ctx: APIRequestContext, id: string) {
  const r = await ctx.get(`/api/receipts/${id}`);
  return { status: r.status(), receipt: (await r.json().catch(() => ({}))).receipt };
}
async function history(ctx: APIRequestContext, id: string) {
  return (await ctx.get(`/api/receipts/${id}/history`)).json();
}

/** Status of the 8 initial receipts S-01 … S-08 (they are confirmed or review; W11 filtered by status). */
async function initialStatuses(ctx: APIRequestContext): Promise<Record<string, string>> {
  const out: Record<string, string> = {};
  for (const st of ['confirmed', 'review', 'queued', 'processing', 'unreadable']) {
    const j = await (await ctx.get(`/api/receipts?status=${st}&limit=1000`)).json();
    for (const r of j.receipts || []) if (/^S-0[1-8]\./.test(r.fileName)) out[r.fileName.slice(0, 4)] = r.status;
  }
  return out;
}

const W7_OK = [200, 201];

/** Same command as resumeReader() (code_step15/mock.sh start-reader) but asynchronous, so the test can poll while the dispatcher starts. */
function resumeReaderAsync(): Promise<void> {
  const root = path.resolve(__dirname, '..', '..', '..');
  const sh = path.join(root, 'code_step15', 'mock.sh').replace(/\\/g, '/');
  const gitBash = process.env.GIT_BASH || 'C:/Program Files/Git/bin/bash.exe';
  return new Promise((resolve, reject) => {
    execFile(gitBash, ['-c', `bash '${sh}' start-reader`], { cwd: root, timeout: 180_000 }, err => (err ? reject(err) : resolve()));
  });
}


/** docker compose restart db + dispatcher of the :3421 stack, asynchronously (same as restartDbAndQueue()). */
function restartDbAndQueueAsync(): Promise<void> {
  const root = path.resolve(__dirname, '..', '..', '..');
  const sh = path.join(root, 'code_step15', 'mock.sh').split(path.sep).join('/');
  const gitBash = process.env.GIT_BASH || 'C:/Program Files/Git/bin/bash.exe';
  return new Promise((resolve, reject) => {
    execFile(gitBash, ['-c', `bash '${sh}' restart-dbq`], { cwd: root, timeout: 300_000 }, err => (err ? reject(err) : resolve()));
  });
}

// ================================================================= TC-5-01
test('TC-5-01 ค้าง + ใหม่ ≤ 400 รับ', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  const steps = [
    { label: '① 299 + 100', pendingNormal: 299, n: 100, expectPending: 399 },
    { label: '② 300 + 100', pendingNormal: 300, n: 100, expectPending: 400 },
    { label: '③ 395 + 5', pendingNormal: 395, n: 5, expectPending: 400 },
  ];
  pauseReader();
  try {
    for (const s of steps) {
      await reset(M_URL, { pendingNormal: s.pendingNormal });
      const api = await apiAs(M_URL, 'U01');
      const cl = await clientId(api, 'CL-01');
      const { context, page } = await pageAs(browser, M_URL, 'U01');
      try {
        const up = await pageUpload(page, cl, okFiles(s.n));
        await evidence(testInfo, `${s.label} W7 response`, { status: up.status, accepted: up.json?.accepted, batchId: up.json?.batchId, error: up.json?.error });
        expect.soft(up.sent, `${s.label}: หน้าเว็บส่งคำขอ W7`).toBe(true);
        expect.soft(W7_OK, `${s.label}: รับชุด (HTTP ${up.status})`).toContain(up.status);
        expect.soft(up.json?.accepted, `${s.label}: รับ ${s.n}`).toBe(s.n);
        const shown = page.getByTestId('upload-accepted-count');
        await expect.soft(shown, `${s.label}: upload-accepted-count แสดง`).toBeVisible();
        if (await shown.isVisible().catch(() => false)) expect.soft(num(await shown.innerText()), `${s.label}: upload-accepted-count = ${s.n}`).toBe(s.n);
        await shot(testInfo, page, `${s.label} upload result`);
        const q = await queue(api);
        await evidence(testInfo, `${s.label} W23`, q);
        expect.soft(q.normal?.pending, `${s.label}: W23 ค้าง = ${s.expectPending}`).toBe(s.expectPending);
      } finally {
        await context.close();
        await api.dispose();
      }
    }
  } finally {
    resumeReader();
  }
});

// ================================================================= TC-5-02
test('TC-5-02 ค้าง + ใหม่ > 400 ไม่รับทั้งชุด', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  await reset(M_URL, { pendingNormal: 301 });
  const api = await apiAs(M_URL, 'U01');
  const { context, page } = await pageAs(browser, M_URL, 'U01');
  try {
    const cl = await clientId(api, 'CL-01');
    const recBefore = await reconcile(api);
    const initBefore = await initialStatuses(api);
    await evidence(testInfo, 'W20 before', recBefore);
    await evidence(testInfo, 'S-01..S-08 before', initBefore);

    const up = await pageUpload(page, cl, okFiles(100));
    await evidence(testInfo, 'W7 response (page)', up);
    expect.soft(up.status, '429 (301 + 100 = 401 > 400)').toBe(429);
    expect.soft(up.json?.error, 'error = queue_full').toBe('queue_full');
    expect.soft(Number(up.json?.accepted ?? 0), 'รับ 0 ใบ').toBe(0);
    const full = page.getByTestId('upload-full-message');
    await expect.soft(full, 'upload-full-message แสดง').toBeVisible();
    if (await full.isVisible().catch(() => false)) {
      expect.soft((await full.innerText()).replace(/\s+/g, ' ').trim(), 'ข้อความเต็ม (เกิน 1 ÷ 8 → 1)').toContain('ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก 1 นาที');
    }
    await shot(testInfo, page, 'upload refused queue_full');

    const q = await queue(api);
    const recAfter = await reconcile(api);
    const initAfter = await initialStatuses(api);
    await evidence(testInfo, 'W23 after', q);
    await evidence(testInfo, 'W20 after', recAfter);
    await evidence(testInfo, 'S-01..S-08 after', initAfter);
    expect.soft(q.normal?.pending, 'ค้างยังเป็น 301').toBe(301);
    expect.soft(recAfter.accepted, 'ยอดรับเข้าเท่าก่อนส่ง').toBe(recBefore.accepted);
    expect.soft(Number(recAfter.diff), 'ผลต่าง 0').toBe(0);
    expect.soft(Object.keys(initAfter).length, 'ใบตั้งต้นครบ 8 ใบ').toBe(8);
    expect.soft(initAfter, 'ใบตั้งต้น 8 ใบสถานะไม่เปลี่ยน').toEqual(initBefore);
  } finally {
    await context.close();
    await api.dispose();
  }
});

// ================================================================= TC-5-03
test('TC-5-03 นาทีให้ลองใหม่ตามจำนวน Worker', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  const rows = [
    { id: 'TD-BR12-b', pendingNormal: 307, workersAlive: 2, n: 1, page: true },
    { id: 'TD-BR12-c', pendingNormal: 308, workersAlive: 2, n: 1, page: false },
    { id: 'TD-BR12-d', pendingNormal: 309, workersAlive: 2, n: 2, page: false },
    { id: 'TD-BR12-e', pendingNormal: 380, workersAlive: 2, n: 10, page: false },
    { id: 'TD-BR12-f', pendingNormal: 400, workersAlive: 2, n: 13, page: false },
    { id: 'TD-BR12-g', pendingNormal: 309, workersAlive: 1, n: 3, page: true },
    { id: 'TD-BR12-h', pendingNormal: 380, workersAlive: 0, n: 20, page: false },
  ];
  const table: any[] = [];
  for (const row of rows) {
    await reset(M_URL, { pendingNormal: row.pendingNormal, workersAlive: row.workersAlive });
    const api = await apiAs(M_URL, 'U01');
    try {
      const cl = await clientId(api, 'CL-01');
      const q0 = await queue(api);
      const rec0 = await reconcile(api);
      const up = await upload(api, { clientId: cl, files: okFiles(100) });
      const q1 = await queue(api);
      const rec1 = await reconcile(api);
      const line: any = {
        row: row.id, reset: { pendingNormal: row.pendingNormal, workersAlive: row.workersAlive }, w23WorkersAlive: q0.workers?.alive,
        status: up.status, body: up.json, retryAfterHeader: up.headers['retry-after'], pendingAfter: q1.normal?.pending, acceptedBefore: rec0.accepted, acceptedAfter: rec1.accepted,
      };
      expect.soft(up.status, `${row.id}: 429`).toBe(429);
      expect.soft(up.json?.error, `${row.id}: queue_full`).toBe('queue_full');
      expect.soft(up.json?.retryAfterMinutes, `${row.id}: retryAfterMinutes = ${row.n}`).toBe(row.n);
      expect.soft(Number(up.json?.accepted ?? 0), `${row.id}: รับ 0 ใบ`).toBe(0);
      expect.soft(q1.normal?.pending, `${row.id}: ค้างไม่เปลี่ยน`).toBe(row.pendingNormal);
      expect.soft(rec1.accepted, `${row.id}: ยอดรับเข้าไม่เปลี่ยน`).toBe(rec0.accepted);

      if (row.page) {
        const { context, page } = await pageAs(browser, M_URL, 'U01');
        try {
          const pu = await pageUpload(page, cl, okFiles(100));
          const minutes = page.getByTestId('upload-retry-minutes');
          await expect.soft(minutes, `${row.id}: upload-retry-minutes แสดง`).toBeVisible();
          const shown = (await minutes.isVisible().catch(() => false)) ? num(await minutes.innerText()) : NaN;
          line.page = { status: pu.status, retryAfterMinutes: pu.json?.retryAfterMinutes, shownMinutes: shown };
          expect.soft(pu.status, `${row.id} (หน้าเว็บ): 429`).toBe(429);
          expect.soft(shown, `${row.id} (หน้าเว็บ): upload-retry-minutes = ${row.n} เท่ากับ API`).toBe(row.n);
          expect.soft(Number(pu.json?.accepted ?? 0), `${row.id} (หน้าเว็บ): รับ 0 ใบ`).toBe(0);
          await shot(testInfo, page, `${row.id} upload-retry-minutes`);
          const q2 = await queue(api);
          expect.soft(q2.normal?.pending, `${row.id} (หน้าเว็บ): ค้างไม่เปลี่ยน`).toBe(row.pendingNormal);
        } finally {
          await context.close();
        }
      }
      table.push(line);
    } finally {
      await api.dispose();
    }
  }
  await evidence(testInfo, 'TD-BR12-b..h results', table);
});

// ================================================================= TC-5-04
test('TC-5-04 ออกจากหน้าแล้วกลับมาเห็นสถานะ และยอดตรวจนับ', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const files = ['ok-100__001.jpg', 'ok-100__002.jpg', 'ok-100__003.jpg', 'conf-089.jpg', 'fail3.jpg'];
  pauseReader();
  let resumed = false;
  const api = await apiAs(M_URL, 'U01');
  try {
    const cl = await clientId(api, 'CL-01');
    let { context, page } = await pageAs(browser, M_URL, 'U01');
    const up = await pageUpload(page, cl, files);
    await evidence(testInfo, 'W7 response (page)', up);
    expect(W7_OK, `อัปโหลด 5 ไฟล์ (HTTP ${up.status})`).toContain(up.status);
    const ids = idsByName(up.json);
    const batchId: string = up.json.batchId;
    expect(Object.keys(ids).length, 'จด 5 ID').toBe(5);

    // ① batch page + /batches while reading is paused
    await page.goto(`/batches/${batchId}`);
    await expect.soft(page.getByTestId('batch-count-accepted'), '① ชุด: รับเข้า 5').toHaveText(/^\s*5\s*$/);
    await expect.soft(page.getByTestId('batch-count-queued'), '① ชุด: รออ่าน 5').toHaveText(/^\s*5\s*$/);
    await shot(testInfo, page, '① batch page (paused)');
    await page.goto('/batches');
    await expect.soft(page.getByTestId('reconcile-accepted'), '① ทั้งสำนักงาน รับเข้า 8 + 5 = 13').toHaveText(/^\s*13\s*$/);
    await expect.soft(page.getByTestId('reconcile-sum'), '① ผลรวมทุกสถานะ 13').toHaveText(/^\s*13\s*$/);
    await expect.soft(page.getByTestId('reconcile-diff'), '① ผลต่าง 0').toHaveText(/^\s*0\s*$/);
    await shot(testInfo, page, '① /batches (paused)');
    const rec1 = await reconcile(api);
    await evidence(testInfo, '① W20 office', rec1);
    expect.soft(rec1.counts, '① 13 = ยืนยันแล้ว 7 + รอตรวจ 1 + รออ่าน 5').toEqual({ queued: 5, processing: 0, review: 1, confirmed: 7, unreadable: 0 });
    expect.soft(Number(rec1.diff), '① ผลต่าง 0 (W20)').toBe(0);

    // log out
    await page.getByTestId('logout-button').click();
    await page.waitForURL(u => u.pathname.startsWith('/login'), { timeout: 15_000 }).catch(() => undefined);
    await context.close();

    // ② resume reading, wait ≤ 3 min until every receipt has a result
    resumeReader(); resumed = true;
    const done = await waitStatus(api, Object.values(ids), ['review', 'unreadable'], 180_000);
    await evidence(testInfo, '② statuses', done.map(r => ({ fileName: r.fileName, status: r.status, attempts: r.attempts })));

    // ③ log in again
    ({ context, page } = await pageAs(browser, M_URL, 'U01'));
    try {
      await page.goto(`/batches/${batchId}`);
      await expect.soft(page.getByTestId('batch-count-accepted'), '③ ชุด: รับเข้า 5').toHaveText(/^\s*5\s*$/);
      await expect.soft(page.getByTestId('batch-count-review'), '③ ชุด: รอตรวจ 4').toHaveText(/^\s*4\s*$/);
      await expect.soft(page.getByTestId('batch-count-unreadable'), '③ ชุด: อ่านไม่ได้ 1').toHaveText(/^\s*1\s*$/);
      for (const f of ['ok-100__001.jpg', 'ok-100__002.jpg', 'ok-100__003.jpg', 'conf-089.jpg']) {
        await expect.soft(page.getByTestId(`receipt-status-${ids[f]}`), `③ ${f} = รอตรวจ`).toHaveText(/รอตรวจ/);
      }
      await expect.soft(page.getByTestId(`receipt-status-${ids['fail3.jpg']}`), '③ fail3 = อ่านไม่ได้').toHaveText(/อ่านไม่ได้/);
      await shot(testInfo, page, '③ batch page after re-login');
      await page.goto('/batches');
      await expect.soft(page.getByTestId('reconcile-accepted'), '③ ทั้งสำนักงาน 13').toHaveText(/^\s*13\s*$/);
      await expect.soft(page.getByTestId('reconcile-sum'), '③ ผลรวมทุกสถานะ 13').toHaveText(/^\s*13\s*$/);
      await expect.soft(page.getByTestId('reconcile-diff'), '③ reconcile-diff = 0').toHaveText(/^\s*0\s*$/);
      await shot(testInfo, page, '③ /batches after re-login');
    } finally {
      await context.close();
    }
    const rec3 = await reconcile(api);
    const recBatch = await (await api.get(`/api/reports/reconcile?batchId=${batchId}`)).json();
    const w9 = await (await api.get(`/api/batches/${batchId}`)).json();
    await evidence(testInfo, '③ W20 office', rec3);
    await evidence(testInfo, '③ W20 batch', recBatch);
    await evidence(testInfo, '③ W9 batch', w9.batch);
    expect.soft(rec3.counts, '③ 13 = ยืนยันแล้ว 7 + รอตรวจ 5 + อ่านไม่ได้ 1').toEqual({ queued: 0, processing: 0, review: 5, confirmed: 7, unreadable: 1 });
    expect.soft(Number(rec3.diff), '③ ผลต่างทั้งสำนักงาน 0').toBe(0);
    expect.soft(recBatch.accepted, '③ รายชุด รับเข้า 5').toBe(5);
    expect.soft(Number(recBatch.diff), '③ ผลต่างรายชุด 0').toBe(0);
    expect.soft(w9.batch?.counts, '③ W9 ชุด: รอตรวจ 4 + อ่านไม่ได้ 1').toEqual({ queued: 0, processing: 0, review: 4, confirmed: 0, unreadable: 1 });
  } finally {
    if (!resumed) resumeReader();
    await api.dispose();
  }
});

// ================================================================= TC-5-05
test('TC-5-05 อ่านซ้ำไม่เกิน 3 ครั้ง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const api = await apiAs(M_URL, 'U01');
  try {
    const cl = await clientId(api, 'CL-01');
    const up = await upload(api, { clientId: cl, files: ['fail1-then-ok.jpg', 'fail2-then-ok.jpg', 'fail3.jpg'] });
    await evidence(testInfo, 'W7 response', up.json);
    expect(W7_OK, `อัปโหลด 3 ไฟล์ (HTTP ${up.status})`).toContain(up.status);
    const ids = idsByName(up.json);
    expect(Object.keys(ids).length, 'จด 3 ID').toBe(3);

    await waitStatus(api, Object.values(ids), ['review', 'unreadable'], 240_000);
    const first: Record<string, any> = {};
    for (const [f, id] of Object.entries(ids)) first[f] = (await receipt(api, id)).receipt;
    await evidence(testInfo, 'W12 when all have a result', Object.values(first).map(r => ({ fileName: r.fileName, status: r.status, attempts: r.attempts, unreadableReason: r.unreadableReason })));
    await sleep(120_000); // then wait 2 more minutes

    const exp: Record<string, { status: string; attempts: number }> = {
      'fail1-then-ok.jpg': { status: 'review', attempts: 2 },
      'fail2-then-ok.jpg': { status: 'review', attempts: 3 },
      'fail3.jpg': { status: 'unreadable', attempts: 3 },
    };
    const after: Record<string, any> = {};
    for (const [f, id] of Object.entries(ids)) {
      const r = (await receipt(api, id)).receipt;
      after[f] = r;
      expect.soft(r.status, `${f}: สถานะ ${exp[f].status} (หลังรอ 2 นาทีไม่กลับเป็นรออ่าน)`).toBe(exp[f].status);
      expect.soft(r.attempts, `${f}: attempts = ${exp[f].attempts}`).toBe(exp[f].attempts);
    }
    await evidence(testInfo, 'W12 after +2 min', Object.values(after).map(r => ({ fileName: r.fileName, status: r.status, attempts: r.attempts, unreadableReason: r.unreadableReason })));

    // W17 history of fail3: 3 read attempts with time (NFR-10), never back to queued at the end
    const h = await history(api, ids['fail3.jpg']);
    await evidence(testInfo, 'W17 fail3', h);
    const tries = (h.events || []).filter((e: any) => e.to === 'processing');
    expect.soft(tries.length, 'ประวัติ fail3 มีการลองอ่าน 3 ครั้ง (เหตุการณ์ → processing)').toBe(3);
    for (const e of tries) expect.soft(Number.isNaN(Date.parse(e.at)), `เหตุการณ์ลองอ่านมีเวลา (${e.at})`).toBe(false);
    const last = (h.events || []).at(-1);
    expect.soft(last?.to, 'เหตุการณ์ล่าสุดของ fail3 = unreadable (ไม่กลับเป็นรออ่าน)').toBe('unreadable');
    for (const f of ['fail1-then-ok.jpg', 'fail2-then-ok.jpg']) await evidence(testInfo, `W17 ${f}`, await history(api, ids[f]));

    // W13 image of fail3
    const img = await api.get(`/api/receipts/${ids['fail3.jpg']}/image`);
    expect.soft(img.status(), 'W13 รูปของ fail3 = 200').toBe(200);

    // /unreadable page
    const { context, page } = await pageAs(browser, M_URL, 'U01');
    try {
      const id3 = ids['fail3.jpg'];
      await page.goto('/unreadable');
      await expect.soft(page.getByTestId(`unreadable-row-${id3}`), 'fail3 อยู่ใน /unreadable').toBeVisible();
      for (const f of ['fail1-then-ok.jpg', 'fail2-then-ok.jpg']) await expect.soft(page.getByTestId(`unreadable-row-${ids[f]}`), `${f} ไม่อยู่ใน /unreadable`).toHaveCount(0);
      const reason = page.getByTestId(`unreadable-reason-${id3}`);
      const reasonText = (await reason.isVisible().catch(() => false)) ? (await reason.innerText()).trim() : '';
      await evidence(testInfo, 'unreadable-reason text', reasonText);
      expect.soft(reasonText.length, 'มีเหตุผลแสดง').toBeGreaterThan(0);
      expect.soft(reasonText, 'เหตุผลไม่ใช่ "ไม่พบไฟล์รูป" (W13 ส่งรูปได้)').not.toContain('ไม่พบไฟล์รูป');
      await shot(testInfo, page, '/unreadable');
      await page.getByTestId(`unreadable-open-link-${id3}`).click();
      await page.waitForURL(u => u.pathname.includes(id3), { timeout: 15_000 }).catch(() => undefined);
      await expect(page.getByTestId('receipt-status')).toBeVisible();
      const body = await page.locator('body').innerText();
      expect.soft(body, 'หน้าใบ fail3 ไม่บอก "ไม่พบไฟล์รูป" ในเมื่อ W13 = 200').not.toContain('ไม่พบไฟล์รูป');
      await shot(testInfo, page, 'fail3 opened from /unreadable');
    } finally {
      await context.close();
    }
  } finally {
    await api.dispose();
  }
});

// ================================================================= TC-5-06
test('TC-5-06 พิมพ์ 5 ช่องเองให้ใบอ่านไม่ได้', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  // "ต่อจาก TC-5-05": repeat its setup so this test runs standalone (shards may separate them)
  await reset(M_URL);
  const api = await apiAs(M_URL, 'U01');
  const { context, page } = await pageAs(browser, M_URL, 'U01');
  try {
    const cl = await clientId(api, 'CL-01');
    const up = await upload(api, { clientId: cl, files: ['fail3.jpg'] });
    expect(W7_OK, `อัปโหลด fail3 (HTTP ${up.status})`).toContain(up.status);
    const id = idsByName(up.json)['fail3.jpg'];
    await waitStatus(api, [id], ['unreadable'], 120_000);

    await page.goto('/unreadable');
    await expect.soft(page.getByTestId('unreadable-count'), '/unreadable นับ 1 ก่อนพิมพ์').toHaveText(/^\s*1\s*$/);
    await page.getByTestId(`unreadable-open-link-${id}`).click();
    await page.waitForURL(u => u.pathname.includes(id), { timeout: 15_000 });
    await expect(page.getByTestId('field-merchant-input')).toBeVisible();

    // ① type 5 fields with total 0.00, save (W14), then confirm
    await page.getByTestId('field-merchant-input').fill('ร้านทดสอบ');
    await page.getByTestId('field-date-input').fill('2026-11-19');
    for (const line of [1, 2]) {
      if (await page.getByTestId(`item-name-input-${line}`).count() === 0) await page.getByTestId('item-add-button').click();
    }
    await page.getByTestId('item-name-input-1').fill('น้ำแข็ง');
    await page.getByTestId('item-price-input-1').fill('30.00');
    await page.getByTestId('item-name-input-2').fill('ถ่าน');
    await page.getByTestId('item-price-input-2').fill('25.50');
    await page.getByTestId('field-total-input').fill('0.00');
    await page.getByTestId('category-select').selectOption({ label: 'อื่น ๆ' });
    const chk = page.getByTestId('total-checked-checkbox');
    if (!(await chk.isChecked())) await chk.check();

    const save1 = await clickAndCapture(page, 'save-button', 'PATCH', `/api/receipts/${id}`);
    await evidence(testInfo, '① W14 save total 0.00', save1);
    const conf1 = await clickAndCapture(page, 'confirm-button', 'POST', `/api/receipts/${id}/confirm`);
    let confirm1 = conf1;
    if (!conf1.sent) {
      // page blocked the confirm before sending -> same request through the API (plan section 4)
      const blockers = await page.getByTestId('confirm-blockers').innerText().catch(() => '');
      await evidence(testInfo, '① page blocked confirm (confirm-blockers)', blockers);
      const api1 = await confirm(api, id);
      confirm1 = { sent: true, status: api1.status, json: api1.json, via: 'api' } as any;
    }
    await evidence(testInfo, '① W15 confirm with total 0.00', confirm1);
    await shot(testInfo, page, '① total 0.00 refused');
    const got422 = [save1, confirm1].some(r => r.status === 422 && r.json?.error === 'total_invalid');
    expect.soft(got422, `① 422 total_invalid (0.00 < 0.01) · save=${save1.status}/${save1.json?.error} confirm=${confirm1.status}/${confirm1.json?.error}`).toBe(true);
    expect.soft(confirm1.status, '① ยืนยันไม่สำเร็จ').not.toBe(200);
    const r1 = (await receipt(api, id)).receipt;
    expect.soft(r1.status, '① สถานะยังไม่ยืนยัน').not.toBe('confirmed');

    // ② total 55.50, save, confirm
    await page.getByTestId('field-total-input').fill('55.50');
    if (!(await chk.isChecked())) await chk.check();
    const save2 = await clickAndCapture(page, 'save-button', 'PATCH', `/api/receipts/${id}`);
    await evidence(testInfo, '② W14 save total 55.50', save2);
    expect.soft(save2.status, '② บันทึก 55.50 สำเร็จ').toBe(200);
    await expect.soft(page.getByTestId('items-sum'), '② ผลรวมรายการ 30.00 + 25.50 = 55.50').toHaveText(/55\.50/);
    const itemsDiff = await page.getByTestId('items-diff').innerText().catch(() => '');
    if (itemsDiff) expect.soft(itemsDiff, '② ผลต่าง 0').toMatch(/0\.00/);
    if (!(await chk.isChecked())) await chk.check();
    let conf2 = await clickAndCapture(page, 'confirm-button', 'POST', `/api/receipts/${id}/confirm`);
    if (!conf2.sent) {
      const blockers = await page.getByTestId('confirm-blockers').innerText().catch(() => '');
      await evidence(testInfo, '② page blocked confirm (confirm-blockers)', blockers);
      const api2 = await confirm(api, id);
      conf2 = { sent: true, status: api2.status, json: api2.json };
    }
    await evidence(testInfo, '② W15 confirm', conf2);
    expect.soft(conf2.status, '② ยืนยันได้').toBe(200);
    await expect.soft(page.getByTestId('receipt-status'), '② สถานะยืนยันแล้ว (หน้า)').toHaveText(/ยืนยันแล้ว/);
    await shot(testInfo, page, '② confirmed 55.50');
    const r2 = (await receipt(api, id)).receipt;
    expect.soft(r2.status, '② สถานะยืนยันแล้ว').toBe('confirmed');
    await page.goto('/unreadable');
    await expect.soft(page.getByTestId('unreadable-count'), '② /unreadable นับ 1 → 0').toHaveText(/^\s*0\s*$/);
    await expect.soft(page.getByTestId(`unreadable-row-${id}`), '② ใบหายจากรายการ /unreadable').toHaveCount(0);
    await shot(testInfo, page, '② /unreadable empty');

    // ③ open the receipt again
    await page.goto(`/receipts/${id}`);
    await expect.soft(page.getByTestId('field-merchant-input'), '③ ร้าน').toHaveValue('ร้านทดสอบ');
    await expect.soft(page.getByTestId('field-date-input'), '③ วันที่').toHaveValue('2026-11-19');
    await expect.soft(page.getByTestId('item-name-input-1'), '③ รายการ 1').toHaveValue('น้ำแข็ง');
    await expect.soft(page.getByTestId('item-price-input-1'), '③ ราคา 1').toHaveValue(/^30(\.00)?$/);
    await expect.soft(page.getByTestId('item-name-input-2'), '③ รายการ 2').toHaveValue('ถ่าน');
    await expect.soft(page.getByTestId('item-price-input-2'), '③ ราคา 2').toHaveValue(/^25\.50?$/);
    await expect.soft(page.getByTestId('field-total-input'), '③ ยอดรวม').toHaveValue(/^55\.50?$/);
    await shot(testInfo, page, '③ reopened receipt');
    const r3 = (await receipt(api, id)).receipt;
    await evidence(testInfo, '③ W12', r3);
    expect.soft(r3.merchant, '③ W12 ร้าน').toBe('ร้านทดสอบ');
    expect.soft(r3.receiptDate, '③ W12 วันที่').toBe('2026-11-19');
    expect.soft(Number(r3.total).toFixed(2), '③ W12 ยอด 55.50').toBe('55.50');
    const items = (r3.items || []).filter((i: any) => !i.removed).map((i: any) => ({ name: i.name, price: Number(i.price).toFixed(2) }));
    expect.soft(items, '③ W12 2 รายการพร้อมราคา').toEqual([{ name: 'น้ำแข็ง', price: '30.00' }, { name: 'ถ่าน', price: '25.50' }]);
  } finally {
    await context.close();
    await api.dispose();
  }
});

/** Click a button and capture the matching request it sends (sent=false when disabled / nothing sent within 10 s). */
async function clickAndCapture(page: Page, testid: string, method: string, urlPart: string): Promise<{ sent: boolean; status: number | null; json: any }> {
  const btn = page.getByTestId(testid);
  if (!(await btn.isEnabled().catch(() => false))) return { sent: false, status: null, json: null };
  const respP = page.waitForResponse(r => r.request().method() === method && new URL(r.url()).pathname === urlPart, { timeout: 10_000 }).catch(() => null);
  await btn.click();
  const resp = await respP;
  if (!resp) return { sent: false, status: null, json: null };
  await page.waitForLoadState('networkidle').catch(() => undefined);
  return { sent: true, status: resp.status(), json: await resp.json().catch(() => ({})) };
}

// ================================================================= TC-5-07
test('TC-5-07 ค้างเกิน 120 นาที', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  await reset(M_URL, { overdue: true });
  const t = Date.now();
  const lead = await apiAs(M_URL, 'U03');
  try {
    // ① W11: the 4 receipts the reset created (TD-BR13-a … d)
    const j = await (await lead.get('/api/receipts?limit=1000')).json();
    const now = Date.now();
    const made = (j.receipts || []).filter((r: any) => !/^S-0[1-8]\./.test(r.fileName))
      .map((r: any) => ({ id: r.id, fileName: r.fileName, status: r.status, ageMin: Math.floor((now - Date.parse(r.acceptedAt)) / 60_000), overdue: r.overdue }));
    await evidence(testInfo, '① W11 receipts made by reset {overdue:true}', made);
    expect(made.length, '① รีเซ็ตสร้าง 4 ใบ (TD-BR13-a – d)').toBe(4);
    const find = (age: number, status: string) => made.find((r: any) => r.ageMin === age && r.status === status);
    const a = find(119, 'queued'), b = find(120, 'queued'), c = find(121, 'queued'), d = find(121, 'review');
    expect.soft(!!a, '① TD-BR13-a อายุ 119 รออ่าน').toBe(true);
    expect.soft(!!b, '① TD-BR13-b อายุ 120 รออ่าน').toBe(true);
    expect.soft(!!c, '① TD-BR13-c อายุ 121 รออ่าน').toBe(true);
    expect.soft(!!d, '① TD-BR13-d อายุ 121 รอตรวจ').toBe(true);

    // ② within t + 59 s U-03 opens /overdue
    const { context, page } = await pageAs(browser, M_URL, 'U03');
    try {
      await expect.soft(page.getByTestId('nav-overdue'), '② หัวหน้าเห็นการแจ้ง (เมนูค้างเกินกำหนด)').toBeVisible();
      await evidence(testInfo, '② nav-overdue text (U-03)', await page.getByTestId('nav-overdue').innerText().catch(() => ''));
      await page.goto('/overdue');
      await expect(page.getByTestId('overdue-table')).toBeVisible();
      const countText = await page.getByTestId('overdue-count').innerText();
      const rowIds = await page.locator('[data-testid^="overdue-row-"]').evaluateAll(es => es.map(e => (e.getAttribute('data-testid') || '').replace('overdue-row-', '')));
      const minutes: Record<string, string> = {};
      for (const rid of rowIds) minutes[rid] = await page.getByTestId(`overdue-minutes-${rid}`).innerText().catch(() => '');
      const elapsed = Date.now() - t;
      await shot(testInfo, page, '② /overdue (U-03)');
      await evidence(testInfo, '② /overdue', { elapsedMsSinceReset: elapsed, overdueCount: countText, rows: rowIds, minutes });
      expect.soft(elapsed, '② ตรวจภายใน t + 59 วินาที (AP-04)').toBeLessThanOrEqual(59_000);
      // AP-04: ใบ 120 นาที (TD-BR13-b) ที่อายุเกิน 120 เพียงเศษวินาทีตอนตรวจ "บันทึกแยก ไม่ใช้ตัดสิน" ตามแผน 2.4 จึงไม่นับในการตัดสิน
      const decisiveRows = rowIds.filter((id: string) => !(b && id === b.id));
      expect.soft(decisiveRows.length, '② รายการมี 1 ใบ (TD-BR13-c) ไม่นับใบ 120 นาทีที่รอ AP-04').toBe(1);
      if (c) {
        expect.soft(rowIds, '② ใบ TD-BR13-c อยู่ในรายการ').toContain(c.id);
        expect.soft(num(minutes[c.id]), '② overdue-minutes = 121').toBe(121);
      }
      if (a) expect.soft(rowIds, '② ใบ 119 นาทีไม่อยู่').not.toContain(a.id);
      if (b && rowIds.includes(b.id)) testInfo.annotations.push({ type: 'รอตัดสิน', description: `AP-04: ใบ TD-BR13-b (120 นาที + เศษวินาที) อยู่ในรายการ แสดง ${minutes[b.id]} นาที · overdue-count=${countText.trim()}` });
      if (d) expect.soft(rowIds, '② ใบ 121 นาทีที่มีผลแล้วไม่อยู่').not.toContain(d.id);
      pendingAP(testInfo, 'AP-04', `ตรวจที่ ${Math.round(elapsed / 1000)} s หลังรีเซ็ต · overdue-count=${countText.trim()} · แถว=${JSON.stringify(minutes)} · ใบ 120 นาที ${b && rowIds.includes(b.id) ? 'อยู่' : 'ไม่อยู่'}ในรายการ`);
    } finally {
      await context.close();
    }
    pendingAP(testInfo, 'AP-05', 'ไม่มีใบด่วนอายุเกิน 120 นาทีในข้อมูลรีเซ็ต · กรณีใบด่วนรอข้อมูลเพิ่มใน TEST-DATA');

    // ③ U-01 opens /overdue -> refused
    const u1 = await pageAs(browser, M_URL, 'U01');
    try {
      await u1.page.goto('/overdue');
      await u1.page.waitForLoadState('networkidle').catch(() => undefined);
      await shot(testInfo, u1.page, '③ /overdue (U-01)');
      await evidence(testInfo, '③ U-01 url after /overdue', u1.page.url());
      await expect.soft(u1.page.getByTestId('overdue-table'), '③ U-01 ถูกปฏิเสธ: ไม่เห็นตารางค้างเกินกำหนด').toHaveCount(0);
      await expect.soft(u1.page.locator('[data-testid^="overdue-row-"]'), '③ U-01 ไม่เห็นแถวค้าง').toHaveCount(0);
    } finally {
      await u1.context.close();
    }
  } finally {
    await lead.dispose();
  }
});

// ================================================================= TC-5-08 ★
test('TC-5-08 ★ ดับ Worker ที่กำลังถือใบกลางงาน 100 ใบ', { tag: ['@P1', '@R'] }, async ({}, testInfo) => {
  testInfo.annotations.push({ type: 'blocked', description: 'รอบปล่อยรุ่น ★: ต้องใช้ใบจริง 100 ไฟล์ เกินงบรอบปกติ/งบของขั้นนี้ (120 ใบ) และต้องได้อนุมัติหัวหน้าทีมทดสอบ' });
  test.skip(true, 'รอบปล่อยรุ่น ★ เท่านั้น (ใบจริง 100 ไฟล์ · ต้องอนุมัติหัวหน้าทีมทดสอบ)');
});

// ================================================================= TC-5-09
test('TC-5-09 ฝั่ง AI ล่มทั้งหมด แล้วกลับมา', { tag: ['@P1', '@R'] }, async ({ browser }, testInfo) => {
  // E6: real files present · reset :3420 · W23 pending 0 · urgent today 0 · workers alive 2
  const gt = JSON.parse(fs.readFileSync(path.join(REAL_IMAGES, 'ground_truth.json'), 'utf8'));
  const gtFiles: string[] = (Array.isArray(gt) ? gt : gt.items || gt.receipts || Object.values(gt)).map((x: any) => x.file).filter(Boolean);
  const missing = gtFiles.filter(f => !fs.existsSync(path.join(REAL_IMAGES, f)));
  expect(missing, 'E6: รูปจริงครบตาม ground_truth.json').toEqual([]);
  await reset(R_URL);
  const api = await apiAs(R_URL, 'U01');
  try {
    const q0 = await queue(api);
    await evidence(testInfo, 'E6 W23', q0);
    expect(q0.normal?.pending, 'E6: ใบงานปกติค้าง 0').toBe(0);
    expect(q0.urgent?.usedToday, 'E6: งานด่วนวันนี้ 0 / 5').toBe(0);
    expect(q0.workers?.alive, 'E6: workersAlive 2').toBe(2);
    await evidence(testInfo, 'E6 gpu.sh status all', gpu('status all'));

    const cl = await clientId(api, 'CL-01');
    const real = ['te0000.jpg', 'te0001.jpg', 'te0002.jpg'].map(f => path.join(REAL_IMAGES, f));
    let ids: string[] = [];
    let batchId = '';
    try {
      // ① stop gateway
      await evidence(testInfo, '① gpu.sh stop gateway', gpu('stop gateway'));
      // ② U-01 uploads 3 real files
      const up = await upload(api, { clientId: cl, files: real, real: true });
      await evidence(testInfo, '② W7 response', up.json);
      expect(W7_OK, `② รับ 3 ใบ (HTTP ${up.status})`).toContain(up.status);
      expect.soft(up.json.accepted, '② รับ 3 ใบ').toBe(3);
      ids = Object.values(idsByName(up.json));
      batchId = up.json.batchId;
      expect(ids.length, '② จด 3 ID').toBe(3);

      // web still opens every page
      const { context, page } = await pageAs(browser, R_URL, 'U01');
      try {
        for (const p of ['/upload', '/batches', `/batches/${batchId}`, '/receipts', `/receipts/${ids[0]}`, '/unreadable', '/reports']) {
          const resp = await page.goto(p);
          expect.soft(resp?.status() ?? 0, `② หน้า ${p} เปิดได้`).toBeLessThan(400);
          await expect.soft(page.getByTestId('nav-user-name'), `② หน้า ${p} แสดงผล`).toBeVisible();
          if (p === `/batches/${batchId}`) await shot(testInfo, page, '② batch page while gateway is down');
        }
      } finally {
        await context.close();
      }
      const h = await api.get('/api/health');
      const hj = await h.json().catch(() => ({}));
      await evidence(testInfo, '② /api/health while gateway is down', hj);
      expect.soft(h.status(), '② /api/health 200 (ai.reachable = false ได้)').toBe(200);

      // wait 3 minutes; all 3 must stay queued
      const seen = new Set<string>();
      const end = Date.now() + 180_000;
      while (Date.now() < end) {
        for (const id of ids) seen.add((await receipt(api, id)).receipt?.status);
        await sleep(15_000);
      }
      const after3 = await Promise.all(ids.map(async id => (await receipt(api, id)).receipt));
      await evidence(testInfo, '② statuses after 3 min', { seen: [...seen], receipts: after3.map(r => ({ fileName: r.fileName, status: r.status, attempts: r.attempts })) });
      for (const r of after3) expect.soft(r.status, `② ${r.fileName} คงสถานะ "รออ่าน"`).toBe('queued');
      const rec = await reconcile(api);
      await evidence(testInfo, '② W20', rec);
      expect.soft(Number(rec.diff), '② ยอดตรวจนับผลต่าง 0').toBe(0);
    } finally {
      // ③ gateway back (always)
      await evidence(testInfo, '③ gpu.sh start gateway', gpu('start gateway'));
    }

    // ③ ≤ 10 min: all 3 are read by themselves (nobody clicks anything)
    const done = await waitStatus(api, ids, ['review', 'unreadable'], 600_000).catch(async e => {
      await evidence(testInfo, '③ timeout', String(e));
      return Promise.all(ids.map(async id => (await receipt(api, id)).receipt));
    });
    await evidence(testInfo, '③ results', done.map((r: any) => ({ fileName: r.fileName, status: r.status, attempts: r.attempts, total: r.total })));
    for (const r of done) expect.soft(r.status, `③ ${r.fileName} ถูกอ่านต่อจนมีผล (รอตรวจ)`).toBe('review');

    // workersAlive = 2 at the end (give the workers up to 2 min to re-register)
    let alive: any = null;
    const endW = Date.now() + 120_000;
    for (;;) {
      alive = (await (await api.get('/api/health')).json().catch(() => ({}))).ai?.workersAlive;
      if (alive === 2 || Date.now() > endW) break;
      await sleep(10_000);
    }
    await evidence(testInfo, '③ /api/health ai.workersAlive', alive);
    expect.soft(alive, '③ workersAlive = 2').toBe(2);
    const recEnd = await reconcile(api);
    await evidence(testInfo, '③ W20', recEnd);
  } finally {
    await api.dispose();
  }
});

// ================================================================= TC-5-10
test('TC-5-10 ปิดแล้วเปิดคิวและฐานข้อมูลใหม่กลางงาน', { tag: ['@P1', '@A'] }, async ({}, testInfo) => {
  await reset(M_URL);
  pauseReader();
  let resumed = false;
  let api = await apiAs(M_URL, 'U01');
  try {
    const cl = await clientId(api, 'CL-01');
    const up = await upload(api, { clientId: cl, files: okFiles(20) });
    await evidence(testInfo, 'W7 response', { status: up.status, accepted: up.json?.accepted, batchId: up.json?.batchId });
    expect(W7_OK, `อัปโหลด 20 ไฟล์ (HTTP ${up.status})`).toContain(up.status);
    const ids = Object.values(idsByName(up.json));
    expect(ids.length, 'จด 20 ID').toBe(20);

    const batchId: string = up.json.batchId;
    // start the reader without blocking (resumeReader() is synchronous and the mock reads all 20 before it returns)
    const started = resumeReaderAsync(); resumed = true;
    started.catch(() => undefined); // awaited below; avoid an unhandled rejection if an expect fails first
    // restart db + queue as soon as the first results appear (the mock reads ~20 receipts in < 1 s, so "about 5"
    // is approximated by "at least 1 and not all"): fire the restart asynchronously the moment W9 shows a result.
    const endA = Date.now() + 300_000;
    let counts: any = {};
    let withResult = 0;
    let restart: Promise<void> | null = null;
    for (;;) {
      counts = (await (await api.get(`/api/batches/${batchId}`)).json()).batch?.counts ?? {};
      withResult = Number(counts.review || 0) + Number(counts.unreadable || 0);
      if (withResult >= 1 || Date.now() > endA) { restart = restartDbAndQueueAsync(); break; }
      await sleep(25);
    }
    await evidence(testInfo, 'batch counts when the restart starts', { withResult, counts });
    expect(withResult, 'มีผลแล้วบางใบก่อน restart').toBeGreaterThanOrEqual(1);
    if (withResult >= 20) {
      testInfo.annotations.push({ type: 'precondition', description: `ทำ "restart กลางงาน" ไม่ได้: ตัวอ่านจำลองอ่านครบ 20 ใบก่อนเริ่ม restart (counts=${JSON.stringify(counts)})` });
    }
    expect.soft(withResult, 'restart กลางงาน: ยังมีใบที่ยังไม่มีผลตอนเริ่ม restart').toBeLessThan(20);
    await started.catch(() => undefined);
    await restart;

    // wait for the web to answer again, then log in again (the old session may be gone)
    const endH = Date.now() + 120_000;
    for (;;) {
      const ok = await api.get('/api/health').then(r => r.status() === 200).catch(() => false);
      if (ok || Date.now() > endH) break;
      await sleep(2000);
    }
    await api.dispose();
    api = await apiAs(M_URL, 'U01');

    const done = await waitStatus(api, ids, ['review', 'unreadable'], 480_000);
    await evidence(testInfo, 'final statuses', done.map(r => ({ id: r.id, fileName: r.fileName, status: r.status, attempts: r.attempts })));
    for (const r of done) expect.soft(r.status, `${r.fileName}: รอตรวจ`).toBe('review');

    let missing = 0;
    const reviewEvents: Record<string, number> = {};
    for (const id of ids) {
      const g = await receipt(api, id);
      if (g.status !== 200 || !g.receipt) { missing++; continue; }
      const h = await history(api, id);
      reviewEvents[g.receipt.fileName] = (h.events || []).filter((e: any) => e.to === 'review').length;
    }
    await evidence(testInfo, 'W17: number of "review" results per receipt', reviewEvents);
    expect.soft(missing, 'ทั้ง 20 ID มีอยู่ · ใบหาย 0').toBe(0);
    for (const [f, n] of Object.entries(reviewEvents)) expect.soft(n, `${f}: มีผล "รอตรวจ" 1 ครั้ง`).toBe(1);

    const rec = await reconcile(api);
    await evidence(testInfo, 'W20 at the end', rec);
    const countsSum = Object.values(rec.counts ?? {}).reduce((s: number, v: any) => s + Number(v || 0), 0);
    expect.soft(rec.accepted, 'รับเข้า 8 + 20 = 28').toBe(28);
    expect.soft(countsSum, 'ผลรวมทุกสถานะ = 28').toBe(28);
    expect.soft(Number(rec.diff), 'ผลต่าง 0').toBe(0);
  } finally {
    if (!resumed) resumeReader();
    await api.dispose();
  }
});
