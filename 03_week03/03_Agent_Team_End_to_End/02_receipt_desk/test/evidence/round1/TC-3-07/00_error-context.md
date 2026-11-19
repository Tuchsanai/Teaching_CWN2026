# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 53-review.spec.ts >> TC-3-07 ธงยอดไม่ตรงคิดจากค่าหลังแก้
- Location: tests\53-review.spec.ts:384:1

# Error details

```
Error: apiRequestContext._wrapApiCall: ENOENT: no such file or directory, open 'C:\Users\oishi\Documents\GitHub\CWN\Teaching\03_week03\04_Agent_Team_End_to_End\02_receipt_desk\test\runs\round1\artifacts-shard-2\.playwright-artifacts-1\traces\1ab129298d31bbfbcc69-83f26df589a6dd605ef6.network'
```

# Test source

```ts
  1   | /**
  2   |  * Shared helpers for the ReceiptDesk Playwright suite (one spec file per Test Plan group 5.x).
  3   |  *
  4   |  * Stacks
  5   |  *   M  = http://localhost:3421  compose project receiptdesk-mock (AI_MODE=mock)  -> tests tagged @M or @A
  6   |  *   R  = http://localhost:3420  compose project receiptdesk-e2e  (real model)     -> tests tagged @R
  7   |  * Every test MUST carry exactly one of the tags @M / @A / @R and one of @P1 / @P2 / @P3.
  8   |  * The `test` exported here takes a cross-process lock on the stack the test uses, so the 4 shards can
  9   |  * run at the same time without one test's reset wiping another's data.
  10  |  */
  11  | import { test as base, expect, APIRequestContext, Browser, BrowserContext, Page, request as pwRequest, TestInfo } from '@playwright/test';
  12  | import { execFileSync } from 'child_process';
  13  | import * as fs from 'fs';
  14  | import * as path from 'path';
  15  | import { ROOT, loadTokens } from './env';
  16  | 
  17  | loadTokens();
  18  | 
  19  | export const M_URL = 'http://localhost:3421';
  20  | export const R_URL = 'http://localhost:3420';
  21  | export const DATA = path.join(ROOT, 'test', 'data');                        // test files (make_files.py)
  22  | export const REAL_IMAGES = path.join(ROOT, 'results', 'deploy', 'test_images'); // 12 real receipts + ground_truth.json
  23  | export const PASSWORD = 'receiptdesk-test';
  24  | 
  25  | export const U = {
  26  |   U01: 'pim@receiptdesk.test',      // คุณพิมพ์  staff
  27  |   U02: 'nan@receiptdesk.test',      // คุณแนน   staff
  28  |   U03: 'kitti@receiptdesk.test',    // คุณกิตติ  lead
  29  |   U04: 'orathai@receiptdesk.test',  // คุณอรทัย  owner
  30  |   U05: 'somchai@receiptdesk.test',  // คุณสมชาย client CL-01
  31  |   U06: 'malee@receiptdesk.test',    // คุณมาลี  client CL-02
  32  | } as const;
  33  | export type UserKey = keyof typeof U;
  34  | 
  35  | /** Category codes of TEST-DATA -> names shown by the web (ids are UUIDs that change on every reset). */
  36  | export const CATEGORY_NAME: Record<string, string> = { 'CAT-01': 'วัตถุดิบ', 'CAT-02': 'ค่าแก๊ส', 'CAT-03': 'ค่าน้ำแข็ง', 'CAT-04': 'อื่น ๆ' };
  37  | 
  38  | // ---------------------------------------------------------------- stack lock (auto fixture)
  39  | const LOCK_DIR = path.join(ROOT, 'test', 'e2e', '.locks');
  40  | function lockName(tags: string[]) { return tags.includes('@R') ? 'stack-3420' : 'stack-3421'; }
  41  | async function acquire(name: string, owner: string) {
  42  |   fs.mkdirSync(LOCK_DIR, { recursive: true });
  43  |   const dir = path.join(LOCK_DIR, name);
  44  |   for (;;) {
  45  |     try { fs.mkdirSync(dir); fs.writeFileSync(path.join(dir, 'owner'), `${owner}\n${new Date().toISOString()}\n${process.pid}`); return dir; }
  46  |     catch {
  47  |       try { // stale lock (> 30 min) -> break it
  48  |         const age = Date.now() - fs.statSync(dir).mtimeMs;
  49  |         if (age > 30 * 60_000) fs.rmSync(dir, { recursive: true, force: true });
  50  |       } catch { /* gone */ }
  51  |       await new Promise(r => setTimeout(r, 1000));
  52  |     }
  53  |   }
  54  | }
  55  | 
  56  | export const test = base.extend<{ stackLock: void }>({
  57  |   stackLock: [async ({}, use, testInfo) => {
  58  |     const dir = await acquire(lockName(testInfo.tags), testInfo.title);
  59  |     try { await use(); } finally { fs.rmSync(dir, { recursive: true, force: true }); }
  60  |   }, { auto: true }],
  61  | });
  62  | export { expect };
  63  | 
  64  | // ---------------------------------------------------------------- API sessions
  65  | /** New API session for `user` on `baseURL` (own cookie jar). Pass null for an empty (not logged in) session. */
  66  | export async function apiAs(baseURL: string, user: UserKey | null, password = PASSWORD): Promise<APIRequestContext> {
  67  |   const ctx = await pwRequest.newContext({ baseURL });
  68  |   if (user) {
  69  |     const r = await ctx.post('/api/auth/login', { data: { email: U[user], password } });
  70  |     expect(r.status(), `login ${user}`).toBe(200);
  71  |   }
  72  |   return ctx;
  73  | }
  74  | 
  75  | /** Reset test data (W2). body e.g. {pendingNormal:301,workersAlive:2}. Returns the JSON. */
  76  | export async function reset(baseURL: string, body?: Record<string, unknown>) {
  77  |   const token = baseURL === R_URL ? process.env.REAL_RESET_TOKEN : process.env.MOCK_RESET_TOKEN;
  78  |   const ctx = await pwRequest.newContext({ baseURL });
  79  |   const r = await ctx.post('/api/test/reset', { headers: { 'X-Test-Token': token || '' }, data: body ?? {} });
  80  |   const j = await r.json().catch(() => ({}));
  81  |   expect(r.status(), 'reset').toBe(200);
  82  |   expect(j.ok).toBe(true);
> 83  |   await ctx.dispose();
      |             ^ Error: apiRequestContext._wrapApiCall: ENOENT: no such file or directory, open 'C:\Users\oishi\Documents\GitHub\CWN\Teaching\03_week03\04_Agent_Team_End_to_End\02_receipt_desk\test\runs\round1\artifacts-shard-2\.playwright-artifacts-1\traces\1ab129298d31bbfbcc69-83f26df589a6dd605ef6.network'
  84  |   return j;
  85  | }
  86  | 
  87  | /** UUID of client CL-0x (needs an office session: staff/lead/owner). */
  88  | export async function clientId(office: APIRequestContext, code: 'CL-01' | 'CL-02' | 'CL-03'): Promise<string> {
  89  |   const j = await (await office.get('/api/clients')).json();
  90  |   const c = j.clients.find((x: any) => x.code === code);
  91  |   if (!c) throw new Error(`client ${code} not found`);
  92  |   return c.id;
  93  | }
  94  | 
  95  | /** UUID of category CAT-0x (looked up by name through W19 of CL-01; needs an office session). */
  96  | export async function categoryId(office: APIRequestContext, code: string): Promise<string> {
  97  |   const cl = await clientId(office, 'CL-01');
  98  |   const j = await (await office.get(`/api/reports/categories?month=2026-11&clientId=${cl}`)).json();
  99  |   const c = j.categories.find((x: any) => x.name === CATEGORY_NAME[code]);
  100 |   if (!c) throw new Error(`category ${code} not found`);
  101 |   return c.id;
  102 | }
  103 | 
  104 | /** Path of a test file. Names under test/data; any name 'x__NNN.jpg' not on disk is created as a copy of 'x.jpg' or ok-100.jpg. */
  105 | export function dataFile(name: string): string {
  106 |   const p = path.join(DATA, name);
  107 |   if (fs.existsSync(p)) return p;
  108 |   const tmpDir = path.join(DATA, '_gen'); fs.mkdirSync(tmpDir, { recursive: true });
  109 |   const q = path.join(tmpDir, name);
  110 |   if (!fs.existsSync(q)) {
  111 |     const stem = name.split('__')[0];
  112 |     const src = [path.join(DATA, `${stem}.jpg`), path.join(DATA, 'ok-100.jpg')].find(fs.existsSync)!;
  113 |     fs.copyFileSync(src, q);
  114 |   }
  115 |   return q;
  116 | }
  117 | /** ['ok-100__001.jpg', ...] for n files starting at `from`. */
  118 | export function okFiles(n: number, from = 1, stem = 'ok-100'): string[] {
  119 |   return Array.from({ length: n }, (_, i) => `${stem}__${String(from + i).padStart(3, '0')}.jpg`);
  120 | }
  121 | 
  122 | /**
  123 |  * W7 upload through the API. `files` are names under test/data (see dataFile) or absolute paths.
  124 |  * Returns { status, json, headers }. Multipart fields: clientId, files (repeated), urgent ('true').
  125 |  */
  126 | export async function upload(ctx: APIRequestContext, opts: { clientId?: string; files: string[]; urgent?: boolean; real?: boolean }) {
  127 |   const fd = new FormData();
  128 |   if (opts.clientId) fd.append('clientId', opts.clientId);
  129 |   if (opts.urgent) fd.append('urgent', 'true');
  130 |   for (const f of opts.files) {
  131 |     const p = path.isAbsolute(f) ? f : dataFile(f);
  132 |     fd.append('files', new Blob([fs.readFileSync(p)]), path.basename(p));
  133 |   }
  134 |   if (opts.real) countGpuFiles(opts.files.length);
  135 |   const r = await ctx.post('/api/batches', { multipart: fd, timeout: 120_000 });
  136 |   const json = await r.json().catch(() => ({}));
  137 |   return { status: r.status(), json, headers: r.headers() };
  138 | }
  139 | 
  140 | /** Poll W12 until every id has one of `statuses` (e.g. ['review','unreadable']). Returns the receipts. */
  141 | export async function waitStatus(ctx: APIRequestContext, ids: string[], statuses: string[], timeoutMs = 180_000) {
  142 |   const end = Date.now() + timeoutMs; let last: any[] = [];
  143 |   for (;;) {
  144 |     last = await Promise.all(ids.map(async id => (await (await ctx.get(`/api/receipts/${id}`)).json()).receipt));
  145 |     if (last.every(r => r && statuses.includes(r.status))) return last;
  146 |     if (Date.now() > end) throw new Error(`timeout waiting for ${statuses.join('/')}: ` + last.map(r => `${r?.fileName}=${r?.status}`).join(', '));
  147 |     await new Promise(r => setTimeout(r, 2000));
  148 |   }
  149 | }
  150 | 
  151 | /** W15 confirm with CAT-04 (or given category) and totalChecked=true. Returns {status,json}. */
  152 | export async function confirm(ctx: APIRequestContext, id: string, body?: Record<string, unknown>) {
  153 |   let data = body;
  154 |   if (!data) data = { totalChecked: true, categoryId: await categoryId(ctx, 'CAT-04') };
  155 |   const r = await ctx.post(`/api/receipts/${id}/confirm`, { data });
  156 |   return { status: r.status(), json: await r.json().catch(() => ({})) };
  157 | }
  158 | 
  159 | /** W20 reconcile (office) -> {accepted,sum,diff,counts} */
  160 | export async function reconcile(ctx: APIRequestContext) { return (await ctx.get('/api/reports/reconcile')).json(); }
  161 | /** W23 queue (office) -> {normal:{pending,...}, urgent:{usedToday,...}, workers:{alive}} */
  162 | export async function queue(ctx: APIRequestContext) { return (await ctx.get('/api/queue')).json(); }
  163 | 
  164 | // ---------------------------------------------------------------- browser sessions
  165 | /** New browser context logged in through the /login page (one context per account). */
  166 | export async function pageAs(browser: Browser, baseURL: string, user: UserKey): Promise<{ context: BrowserContext; page: Page }> {
  167 |   const context = await browser.newContext({ baseURL, locale: 'th-TH', timezoneId: 'Asia/Bangkok' });
  168 |   const page = await context.newPage();
  169 |   await page.goto('/login');
  170 |   await page.getByTestId('login-email-input').fill(U[user]);
  171 |   await page.getByTestId('login-password-input').fill(PASSWORD);
  172 |   await page.getByTestId('login-submit-button').click();
  173 |   await page.waitForURL(u => !u.pathname.startsWith('/login'));
  174 |   return { context, page };
  175 | }
  176 | 
  177 | // ---------------------------------------------------------------- mock stack control ("พักการอ่าน")
  178 | const MOCK_SH = path.join(ROOT, 'code_step15', 'mock.sh');
  179 | const GPU_SH = path.join(ROOT, 'code_step11', 'gpu.sh');
  180 | const GIT_BASH = process.env.GIT_BASH || 'C:/Program Files/Git/bin/bash.exe';
  181 | function bash(cmd: string, timeout = 180_000) {
  182 |   return execFileSync(GIT_BASH, ['-c', cmd], { cwd: ROOT, encoding: 'utf8', timeout, env: { ...process.env } });
  183 | }
```