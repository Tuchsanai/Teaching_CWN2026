/**
 * Shared helpers for the ReceiptDesk Playwright suite (one spec file per Test Plan group 5.x).
 *
 * Stacks
 *   M  = http://localhost:3421  compose project receiptdesk-mock (AI_MODE=mock)  -> tests tagged @M or @A
 *   R  = http://localhost:3420  compose project receiptdesk-e2e  (real model)     -> tests tagged @R
 * Every test MUST carry exactly one of the tags @M / @A / @R and one of @P1 / @P2 / @P3.
 * The `test` exported here takes a cross-process lock on the stack the test uses, so the 4 shards can
 * run at the same time without one test's reset wiping another's data.
 */
import { test as base, expect, APIRequestContext, Browser, BrowserContext, Page, request as pwRequest, TestInfo } from '@playwright/test';
import { execFileSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { ROOT, loadTokens } from './env';

loadTokens();

export const M_URL = 'http://localhost:3421';
export const R_URL = 'http://localhost:3420';
export const DATA = path.join(ROOT, 'test', 'data');                        // test files (make_files.py)
export const REAL_IMAGES = path.join(ROOT, 'results', 'deploy', 'test_images'); // 12 real receipts + ground_truth.json
export const PASSWORD = 'receiptdesk-test';

export const U = {
  U01: 'pim@receiptdesk.test',      // คุณพิมพ์  staff
  U02: 'nan@receiptdesk.test',      // คุณแนน   staff
  U03: 'kitti@receiptdesk.test',    // คุณกิตติ  lead
  U04: 'orathai@receiptdesk.test',  // คุณอรทัย  owner
  U05: 'somchai@receiptdesk.test',  // คุณสมชาย client CL-01
  U06: 'malee@receiptdesk.test',    // คุณมาลี  client CL-02
} as const;
export type UserKey = keyof typeof U;

/** Category codes of TEST-DATA -> names shown by the web (ids are UUIDs that change on every reset). */
export const CATEGORY_NAME: Record<string, string> = { 'CAT-01': 'วัตถุดิบ', 'CAT-02': 'ค่าแก๊ส', 'CAT-03': 'ค่าน้ำแข็ง', 'CAT-04': 'อื่น ๆ' };

// ---------------------------------------------------------------- stack lock (auto fixture)
const LOCK_DIR = path.join(ROOT, 'test', 'e2e', '.locks');
function lockName(tags: string[]) { return tags.includes('@R') ? 'stack-3420' : 'stack-3421'; }
async function acquire(name: string, owner: string) {
  fs.mkdirSync(LOCK_DIR, { recursive: true });
  const dir = path.join(LOCK_DIR, name);
  for (;;) {
    try { fs.mkdirSync(dir); fs.writeFileSync(path.join(dir, 'owner'), `${owner}\n${new Date().toISOString()}\n${process.pid}`); return dir; }
    catch {
      try { // stale lock (> 30 min) -> break it
        const age = Date.now() - fs.statSync(dir).mtimeMs;
        if (age > 30 * 60_000) fs.rmSync(dir, { recursive: true, force: true });
      } catch { /* gone */ }
      await new Promise(r => setTimeout(r, 1000));
    }
  }
}

export const test = base.extend<{ stackLock: void }>({
  stackLock: [async ({}, use, testInfo) => {
    const dir = await acquire(lockName(testInfo.tags), testInfo.title);
    try { await use(); } finally { fs.rmSync(dir, { recursive: true, force: true }); }
  }, { auto: true }],
});
export { expect };

// ---------------------------------------------------------------- API sessions
/** New API session for `user` on `baseURL` (own cookie jar). Pass null for an empty (not logged in) session. */
export async function apiAs(baseURL: string, user: UserKey | null, password = PASSWORD): Promise<APIRequestContext> {
  const ctx = await pwRequest.newContext({ baseURL });
  if (user) {
    const r = await ctx.post('/api/auth/login', { data: { email: U[user], password } });
    expect(r.status(), `login ${user}`).toBe(200);
  }
  return ctx;
}

/** Reset test data (W2). body e.g. {pendingNormal:301,workersAlive:2}. Returns the JSON. */
export async function reset(baseURL: string, body?: Record<string, unknown>) {
  const token = baseURL === R_URL ? process.env.REAL_RESET_TOKEN : process.env.MOCK_RESET_TOKEN;
  const ctx = await pwRequest.newContext({ baseURL });
  const r = await ctx.post('/api/test/reset', { headers: { 'X-Test-Token': token || '' }, data: body ?? {} });
  const j = await r.json().catch(() => ({}));
  expect(r.status(), 'reset').toBe(200);
  expect(j.ok).toBe(true);
  await ctx.dispose();
  return j;
}

/** UUID of client CL-0x (needs an office session: staff/lead/owner). */
export async function clientId(office: APIRequestContext, code: 'CL-01' | 'CL-02' | 'CL-03'): Promise<string> {
  const j = await (await office.get('/api/clients')).json();
  const c = j.clients.find((x: any) => x.code === code);
  if (!c) throw new Error(`client ${code} not found`);
  return c.id;
}

/** UUID of category CAT-0x (looked up by name through W19 of CL-01; needs an office session). */
export async function categoryId(office: APIRequestContext, code: string): Promise<string> {
  const cl = await clientId(office, 'CL-01');
  const j = await (await office.get(`/api/reports/categories?month=2026-11&clientId=${cl}`)).json();
  const c = j.categories.find((x: any) => x.name === CATEGORY_NAME[code]);
  if (!c) throw new Error(`category ${code} not found`);
  return c.id;
}

/** Path of a test file. Names under test/data; any name 'x__NNN.jpg' not on disk is created as a copy of 'x.jpg' or ok-100.jpg. */
export function dataFile(name: string): string {
  const p = path.join(DATA, name);
  if (fs.existsSync(p)) return p;
  const tmpDir = path.join(DATA, '_gen'); fs.mkdirSync(tmpDir, { recursive: true });
  const q = path.join(tmpDir, name);
  if (!fs.existsSync(q)) {
    const stem = name.split('__')[0];
    const src = [path.join(DATA, `${stem}.jpg`), path.join(DATA, 'ok-100.jpg')].find(fs.existsSync)!;
    fs.copyFileSync(src, q);
  }
  return q;
}
/** ['ok-100__001.jpg', ...] for n files starting at `from`. */
export function okFiles(n: number, from = 1, stem = 'ok-100'): string[] {
  return Array.from({ length: n }, (_, i) => `${stem}__${String(from + i).padStart(3, '0')}.jpg`);
}

/**
 * W7 upload through the API. `files` are names under test/data (see dataFile) or absolute paths.
 * Returns { status, json, headers }. Multipart fields: clientId, files (repeated), urgent ('true').
 */
export async function upload(ctx: APIRequestContext, opts: { clientId?: string; files: string[]; urgent?: boolean; real?: boolean }) {
  const fd = new FormData();
  if (opts.clientId) fd.append('clientId', opts.clientId);
  if (opts.urgent) fd.append('urgent', 'true');
  for (const f of opts.files) {
    const p = path.isAbsolute(f) ? f : dataFile(f);
    fd.append('files', new Blob([fs.readFileSync(p)]), path.basename(p));
  }
  if (opts.real) countGpuFiles(opts.files.length);
  const r = await ctx.post('/api/batches', { multipart: fd, timeout: 120_000 });
  const json = await r.json().catch(() => ({}));
  return { status: r.status(), json, headers: r.headers() };
}

/** Poll W12 until every id has one of `statuses` (e.g. ['review','unreadable']). Returns the receipts. */
export async function waitStatus(ctx: APIRequestContext, ids: string[], statuses: string[], timeoutMs = 180_000) {
  const end = Date.now() + timeoutMs; let last: any[] = [];
  for (;;) {
    last = await Promise.all(ids.map(async id => (await (await ctx.get(`/api/receipts/${id}`)).json()).receipt));
    if (last.every(r => r && statuses.includes(r.status))) return last;
    if (Date.now() > end) throw new Error(`timeout waiting for ${statuses.join('/')}: ` + last.map(r => `${r?.fileName}=${r?.status}`).join(', '));
    await new Promise(r => setTimeout(r, 2000));
  }
}

/** W15 confirm with CAT-04 (or given category) and totalChecked=true. Returns {status,json}. */
export async function confirm(ctx: APIRequestContext, id: string, body?: Record<string, unknown>) {
  let data = body;
  if (!data) data = { totalChecked: true, categoryId: await categoryId(ctx, 'CAT-04') };
  const r = await ctx.post(`/api/receipts/${id}/confirm`, { data });
  return { status: r.status(), json: await r.json().catch(() => ({})) };
}

/** W20 reconcile (office) -> {accepted,sum,diff,counts} */
export async function reconcile(ctx: APIRequestContext) { return (await ctx.get('/api/reports/reconcile')).json(); }
/** W23 queue (office) -> {normal:{pending,...}, urgent:{usedToday,...}, workers:{alive}} */
export async function queue(ctx: APIRequestContext) { return (await ctx.get('/api/queue')).json(); }

// ---------------------------------------------------------------- browser sessions
/** New browser context logged in through the /login page (one context per account). */
export async function pageAs(browser: Browser, baseURL: string, user: UserKey): Promise<{ context: BrowserContext; page: Page }> {
  const context = await browser.newContext({ baseURL, locale: 'th-TH', timezoneId: 'Asia/Bangkok' });
  const page = await context.newPage();
  await page.goto('/login');
  await page.getByTestId('login-email-input').fill(U[user]);
  await page.getByTestId('login-password-input').fill(PASSWORD);
  await page.getByTestId('login-submit-button').click();
  await page.waitForURL(u => !u.pathname.startsWith('/login'));
  return { context, page };
}

// ---------------------------------------------------------------- mock stack control ("พักการอ่าน")
const MOCK_SH = path.join(ROOT, 'code_step15', 'mock.sh');
const GPU_SH = path.join(ROOT, 'code_step11', 'gpu.sh');
const GIT_BASH = process.env.GIT_BASH || 'C:/Program Files/Git/bin/bash.exe';
function bash(cmd: string, timeout = 180_000) {
  return execFileSync(GIT_BASH, ['-c', cmd], { cwd: ROOT, encoding: 'utf8', timeout, env: { ...process.env } });
}
/** Stop the dispatcher of the :3421 stack -> new receipts stay 'queued'. */
export function pauseReader() { bash(`bash '${MOCK_SH.replace(/\\/g, '/')}' stop-reader`); }
/** Start the dispatcher of the :3421 stack again. */
export function resumeReader() { bash(`bash '${MOCK_SH.replace(/\\/g, '/')}' start-reader`); }
/** Restart db then dispatcher of the :3421 stack (TC-5-10). */
export function restartDbAndQueue() { bash(`bash '${MOCK_SH.replace(/\\/g, '/')}' restart-dbq`, 300_000); }
/** code_step11/gpu.sh <args>  e.g. gpu('stop worker0 worker1'), gpu('log worker0'), gpu('status all'). R tests only. */
export function gpu(args: string, timeout = 240_000): string { return bash(`bash '${GPU_SH.replace(/\\/g, '/')}' ${args}`, timeout); }

// ---------------------------------------------------------------- GPU budget + evidence
const GPU_LOG = path.join(ROOT, 'test', 'e2e', '.gpu-files.log');
export const GPU_CAP = Number(process.env.GPU_CAP || 120);
/** Called by upload(..., real:true). Throws before sending if the step budget would be exceeded. */
export function countGpuFiles(n: number) {
  const used = fs.existsSync(GPU_LOG) ? fs.readFileSync(GPU_LOG, 'utf8').split('\n').filter(Boolean).reduce((a, l) => a + Number(l.split(' ')[1] || 0), 0) : 0;
  if (used + n > GPU_CAP) throw new Error(`GPU budget: ${used} + ${n} > ${GPU_CAP}`);
  fs.appendFileSync(GPU_LOG, `${new Date().toISOString()} ${n} ${process.env.RUN || 'dev'}\n`);
}

/** Attach evidence to the test (shown in the report and in test/index.html). */
export async function evidence(testInfo: TestInfo, name: string, data: unknown) {
  await testInfo.attach(name, { body: typeof data === 'string' ? data : JSON.stringify(data, null, 2), contentType: typeof data === 'string' ? 'text/plain' : 'application/json' });
}
/** Screenshot of a page as evidence (use at the key moment of every UI test). */
export async function shot(testInfo: TestInfo, page: Page, name: string) {
  await testInfo.attach(name, { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' });
}
/** Mark a check whose verdict depends on a customer question AP-xx (recorded, not used for pass/fail). */
export function pendingAP(testInfo: TestInfo, ap: string, note: string) {
  testInfo.annotations.push({ type: 'AP', description: `${ap}: ${note}` });
}
