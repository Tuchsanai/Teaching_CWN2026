// Shared helpers for the SiteSafe Inspect e2e suite (Test Plan ./test/TEST-PLAN.md).
// Reset ONLY via POST /api/test/reset. Never touch the database.
import { test, expect, type TestInfo, type BrowserContext, type Page } from '@playwright/test';
import { execSync } from 'node:child_process';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as https from 'node:https';
import * as nodeHttp from 'node:http';
import * as crypto from 'node:crypto';

export const API = 'http://127.0.0.1:3410';      // plain HTTP scripts
export const UI = 'http://localhost:3410';       // browser
export const RESET_KEY = 'sitesafe-test-reset-key';
export const ROOT = path.resolve(__dirname, '..', '..', '..');           // project folder
export const FIXTURES = path.resolve(__dirname, '..', 'fixtures');
export const TEST_IMAGES = path.join(ROOT, 'results', 'deploy', 'test_images');
export const WEB_CONTAINER = 'sitesafe-e2e-web-1';
export const DISPATCHER_CONTAINER = 'sitesafe-e2e-dispatcher-1';

export const USERS = {
  U1: { email: 'manager@sitesafe.test', password: 'Test-Manager-01', role: 'manager', site: null },
  U2: { email: 'sup.a@sitesafe.test', password: 'Test-SupA-01', role: 'supervisor', site: 'SITE-A' },
  U3: { email: 'sup.b@sitesafe.test', password: 'Test-SupB-01', role: 'supervisor', site: 'SITE-B' },
  U4: { email: 'sup.c@sitesafe.test', password: 'Test-SupC-01', role: 'supervisor', site: 'SITE-C' },
  U5: { email: 'exec@sitesafe.test', password: 'Test-Exec-01', role: 'executive', site: null },
} as const;
export type UserKey = keyof typeof USERS;

export const RESULT_TH: Record<string, string> = { PASS: 'ผ่าน', WARN: 'เตือน', FAIL: 'ไม่ผ่าน' };

/** Result of an HTTP call. json is null when the body is not JSON. */
export interface Res { status: number; headers: Headers; text: string; json: any; bytes: Buffer }

export async function http(method: string, p: string, opts: { cookie?: string; json?: any; form?: FormData; headers?: Record<string, string> } = {}): Promise<Res> {
  const headers: Record<string, string> = { ...(opts.headers || {}) };
  if (opts.cookie) headers['Cookie'] = opts.cookie;
  let body: any;
  if (opts.json !== undefined) { headers['content-type'] = 'application/json'; body = JSON.stringify(opts.json); }
  if (opts.form) {
    // serialise multipart once so we can send it over a plain node:http request
    const enc = new Response(opts.form);
    headers['content-type'] = enc.headers.get('content-type')!;
    body = Buffer.from(await enc.arrayBuffer());
  }
  // node:http with a NEW connection per request (agent:false). The site answers 413/415 early and closes
  // the socket while the body is still being sent; fetch() then fails or reuses the dead keep-alive socket.
  // Here we keep the early response and ignore the write error that follows it.
  const buf: Buffer | undefined = body === undefined ? undefined : Buffer.isBuffer(body) ? body : Buffer.from(body);
  if (buf) headers['content-length'] = String(buf.length);
  const u = new URL(API + p);
  return await new Promise<Res>((resolve, reject) => {
    let answered = false;
    const req = nodeHttp.request({ method, hostname: u.hostname, port: u.port, path: u.pathname + u.search, headers, agent: false }, res => {
      answered = true;
      const chunks: Buffer[] = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        const bytes = Buffer.concat(chunks); const text = bytes.toString('utf8');
        let json: any = null; try { json = JSON.parse(text); } catch { }
        const h = new Headers();
        for (const [k, v] of Object.entries(res.headers)) if (v !== undefined) (Array.isArray(v) ? v : [v]).forEach(x => h.append(k, String(x)));
        resolve({ status: res.statusCode || 0, headers: h, text, json, bytes });
      });
      res.on('error', e => reject(e));
    });
    req.on('error', e => { if (!answered) reject(e); });
    if (buf) req.write(buf);
    req.end();
  });
}

/** Common step 1: reset. Expects 200 and the seed counts; throws otherwise (stop). */
export async function reset(now?: string) {
  const r = await http('POST', '/api/test/reset', { headers: { 'X-Test-Key': RESET_KEY }, json: now ? { now } : {} });
  expect(r.status, 'reset must return 200').toBe(200);
  expect(r.json).toMatchObject({ reset: true, sites: 3, users: 5, photos: 1233, overrides: 1 });
  return r.json;
}

/** Login through the API, returns the Cookie header value "sitesafe_session=...". */
export async function login(user: UserKey): Promise<string> {
  const u = USERS[user];
  const r = await http('POST', '/api/auth/login', { json: { email: u.email, password: u.password } });
  expect(r.status, `login ${user}`).toBe(200);
  const sc = r.headers.get('set-cookie') || '';
  const m = sc.match(/sitesafe_session=[^;]+/);
  if (!m) throw new Error('no session cookie for ' + user);
  return m[0];
}

/** Put an API session cookie into a browser context (localhost is a secure context in Chromium). */
export async function cookieToContext(ctx: BrowserContext, cookie: string) {
  const [name, value] = cookie.split('=');
  await ctx.addCookies([{ name, value: cookie.slice(name.length + 1), domain: 'localhost', path: '/', httpOnly: true, secure: true, sameSite: 'Lax' }]);
}

/** Login through the UI form (data-testid login-*). */
export async function uiLogin(page: Page, user: UserKey) {
  const u = USERS[user];
  await page.goto(UI + '/login');
  await page.getByTestId('login-email').fill(u.email);
  await page.getByTestId('login-password').fill(u.password);
  await page.getByTestId('login-submit').click();
  await page.waitForURL(url => !url.pathname.startsWith('/login'), { timeout: 15000 });
}

export function fixture(name: string) { return path.join(FIXTURES, name); }
export function testImage(prefix: string) {
  const f = fs.readdirSync(TEST_IMAGES).find(n => n.startsWith(prefix));
  if (!f) throw new Error('no test image ' + prefix);
  return path.join(TEST_IMAGES, f);
}
export function allTestImages() { return fs.readdirSync(TEST_IMAGES).filter(n => /\.(jpe?g|png)$/i.test(n)).sort().map(n => path.join(TEST_IMAGES, n)); }
export function sha256(buf: Buffer) { return crypto.createHash('sha256').update(buf).digest('hex'); }

/** Open a batch: POST /api/uploads {count}. */
export async function openBatch(cookie: string, count: number) {
  return http('POST', '/api/uploads', { cookie, json: { count } });
}
/** Send one file to a batch (multipart field "file"). uploadName lets you rename the file on the wire. */
export async function sendFile(cookie: string, batchId: string, filePath: string, uploadName?: string) {
  const buf = fs.readFileSync(filePath);
  const name = uploadName || path.basename(filePath);
  const type = /\.png$/i.test(name) ? 'image/png' : /\.gif$/i.test(name) ? 'image/gif' : /\.pdf$/i.test(name) ? 'application/pdf' : 'image/jpeg';
  const form = new FormData();
  form.append('file', new Blob([buf], { type }), name);
  const r = await http('POST', `/api/uploads/${batchId}/photos`, { cookie, form });
  return { ...r, photoId: r.json?.id as string | undefined, acceptedAt: Date.now() };
}
/** Common step 2: open a batch of files.length and send each file. Returns per-file status + photoId. */
export async function upload(cookie: string, files: { path: string; name?: string }[], count = files.length) {
  const b = await openBatch(cookie, count);
  expect(b.status, 'open batch').toBe(201);
  const batchId = b.json.batch_id as string;
  const items = [] as Awaited<ReturnType<typeof sendFile>>[];
  for (const f of files) items.push(await sendFile(cookie, batchId, f.path, f.name));
  return { batchId, items };
}

/** GET /api/uploads/{batchId} */
export async function batchStatus(cookie: string, batchId: string) { return http('GET', `/api/uploads/${batchId}`, { cookie }); }

/** Poll a batch until every photo is DONE or FAILED (or timeout). Returns last batch JSON and history. */
export async function waitBatchTerminal(cookie: string, batchId: string, timeoutMs: number, everyMs = 2000) {
  const t0 = Date.now(); const history: any[] = [];
  let last: any = null;
  while (Date.now() - t0 < timeoutMs) {
    const r = await batchStatus(cookie, batchId);
    last = r.json; history.push({ t: Date.now() - t0, status: r.status, counts: last?.counts, photos: (last?.photos || []).map((p: any) => ({ id: p.id, status: p.status })) });
    const ph = last?.photos || [];
    if (ph.length && ph.every((p: any) => p.status === 'DONE' || p.status === 'FAILED')) break;
    await new Promise(r => setTimeout(r, everyMs));
  }
  return { last, history, elapsedMs: Date.now() - t0 };
}

/** Count photos in a filtered list (uses `total`). */
export async function countPhotos(cookie: string, q: string) {
  const r = await http('GET', '/api/photos?' + q, { cookie });
  return { status: r.status, total: r.json?.total as number, json: r.json };
}

/** All pages of /api/photos for a query. */
export async function allPhotos(cookie: string, q: string) {
  const first = await http('GET', `/api/photos?${q}&page=1`, { cookie });
  const out = [...(first.json?.photos || [])];
  for (let p = 2; p <= (first.json?.pages || 1); p++) out.push(...((await http('GET', `/api/photos?${q}&page=${p}`, { cookie })).json?.photos || []));
  return { status: first.status, total: first.json?.total, counts: first.json?.counts, photos: out };
}

// ---------------- docker (only containers of this app) ----------------
export function docker(args: string) { return execSync('docker ' + args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }); }
export function stopDispatcher() { docker(`stop ${DISPATCHER_CONTAINER}`); }
export function startDispatcher() { docker(`start ${DISPATCHER_CONTAINER}`); }
export async function waitHealthy(timeoutMs = 60000) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    try { const r = await http('GET', '/api/health'); if (r.status === 200 && r.json?.db === 'ok') return r.json; } catch { }
    await new Promise(r => setTimeout(r, 1000));
  }
  throw new Error('web not healthy');
}
/**
 * No mock-gateway runs on this machine (ai_mode real). Groups that only need the web to ACCEPT/STORE files
 * (not an AI result) stop the dispatcher so no photo reaches the rented GPU. Call inside test.describe.
 * afterAll resets first (wipes the uploaded rows) and only then starts the dispatcher again.
 */
export function noGpuForThisFile() {
  test.beforeAll(() => { stopDispatcher(); });
  test.afterAll(async () => { await reset(); startDispatcher(); });
}

// ---------------- real-GPU upload budget (< 80 per step) ----------------
const LEDGER = path.resolve(__dirname, '..', 'real-uploads.log');
/** Record n photos that will reach the GPU. Throws (stop condition) if the total would reach 80. */
export function useRealBudget(n: number, why: string) {
  const used = fs.existsSync(LEDGER) ? fs.readFileSync(LEDGER, 'utf8').split('\n').filter(Boolean).reduce((s, l) => s + Number(l.split('\t')[1] || 0), 0) : 0;
  if (used + n > 79) throw new Error(`GPU budget: ${used} used + ${n} > 79 (stop condition)`);
  fs.appendFileSync(LEDGER, `${new Date().toISOString()}\t${n}\t${why}\n`);
  return used + n;
}

// ---------------- gateway (rented GPU machine) ----------------
function readEnvKey(): string {
  const env = fs.readFileSync(path.join(ROOT, '.env'), 'utf8');
  const m = env.match(/^GATEWAY_API_KEY=(.*)$/m); if (!m) throw new Error('no GATEWAY_API_KEY');
  return m[1].trim().replace(/^"|"$/g, '');
}
export function gatewayKey() { return readEnvKey(); }
export function gatewayUrl() { return docker(`inspect ${WEB_CONTAINER} --format "{{range .Config.Env}}{{println .}}{{end}}"`).split('\n').find(l => l.startsWith('GATEWAY_URL='))!.slice(12).trim(); }
/** Request to the gateway. key: 'good' | 'none' | 'wrong'. Never logs the key. */
export function gateway(method: string, p: string, key: 'good' | 'none' | 'wrong', body?: { form: Buffer; boundary: string }): Promise<{ status: number; json: any; headers: any }> {
  const u = new URL(gatewayUrl() + p);
  const ca = fs.readFileSync(path.join(ROOT, 'results', 'deploy', 'gateway_ca.crt'));
  const headers: any = {};
  if (key === 'good') headers['X-API-Key'] = readEnvKey();
  if (key === 'wrong') headers['X-API-Key'] = 'wrong-key-0000000000';
  if (body) { headers['content-type'] = 'multipart/form-data; boundary=' + body.boundary; headers['content-length'] = body.form.length; }
  return new Promise((resolve, reject) => {
    const req = https.request({ method, hostname: u.hostname, port: u.port, path: u.pathname + u.search, headers, ca, rejectUnauthorized: true, ...(/^[0-9.]+$/.test(u.hostname) ? {} : { servername: u.hostname }), timeout: 30000 }, res => {
      const chunks: Buffer[] = []; res.on('data', c => chunks.push(c)); res.on('end', () => {
        const t = Buffer.concat(chunks).toString('utf8'); let j: any = null; try { j = JSON.parse(t); } catch { }
        resolve({ status: res.statusCode || 0, json: j, headers: res.headers });
      });
    });
    req.on('error', reject); req.on('timeout', () => req.destroy(new Error('gateway timeout')));
    if (body) req.write(body.form); req.end();
  });
}
/** Build a multipart body for POST /v1/jobs. */
export function jobForm(jobId: string, filePath: string) {
  const boundary = '----e2e' + crypto.randomBytes(8).toString('hex');
  const img = fs.readFileSync(filePath);
  const parts: Buffer[] = [];
  const field = (n: string, v: string) => Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="${n}"\r\n\r\n${v}\r\n`);
  parts.push(field('job_id', jobId), field('sha256', sha256(img)));
  parts.push(Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="image"; filename="${path.basename(filePath)}"\r\nContent-Type: image/jpeg\r\n\r\n`), img, Buffer.from(`\r\n--${boundary}--\r\n`));
  return { form: Buffer.concat(parts), boundary };
}

// ---------------- evidence ----------------
/** Attach JSON evidence to the test (shown in ./test/index.html). */
export async function evidence(testInfo: TestInfo, name: string, data: any) {
  await testInfo.attach(name, { body: JSON.stringify(data, null, 2), contentType: 'application/json' });
}
/** Attach a screenshot of the page as evidence (every TC that uses a page should call this). */
export async function shot(testInfo: TestInfo, page: Page, name: string) {
  await testInfo.attach(name, { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' });
}
/**
 * Call at the END of a TC whose plan needs something this machine cannot provide
 * (mock-gateway, stopping the GPU Worker, MAX_QUEUE_DEPTH on the rented machine, round B budget).
 * If the runnable parts produced no failure, the TC is marked skipped = "บล็อก" with the reason.
 * If a runnable part failed, the failure stays (the test is "ล้ม").
 */
export function blockedIfClean(testInfo: TestInfo, reason: string) {
  testInfo.annotations.push({ type: 'blocked', description: reason });
  if (testInfo.errors.length === 0) test.skip(true, 'บล็อก: ' + reason);
}
