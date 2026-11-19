// Test Plan section 5.3 · สถานะงานในคิว · คิวเต็ม · รูปห้ามหาย (TC-3-01 – TC-3-10)
// Expected values come only from ./test/TEST-PLAN.md (5.3) · TEST-DATA (5, 10) · DESIGN (4, 5.1, 6).
// This machine: ai_mode=real, gateway on a rented GPU machine that we may not touch
// (no MAX_QUEUE_DEPTH change, no Worker stop) → TC-3-03–06, 3-09, 3-10 are recorded as "บล็อก".
import { test, expect, type TestInfo, type BrowserContext } from '@playwright/test';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as https from 'node:https';
import * as net from 'node:net';
import * as crypto from 'node:crypto';
import {
  UI, ROOT, reset, login, cookieToContext, fixture, testImage, allTestImages,
  upload, openBatch, sendFile, batchStatus, http, useRealBudget,
  gatewayKey, gatewayUrl, jobForm, evidence, shot, blockedIfClean,
} from './helpers';

// ---------------- extra helpers (this file only) ----------------
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));
const TERMINAL = new Set(['DONE', 'FAILED']);
const STATUSES = ['QUEUED', 'PROCESSING', 'DONE', 'FAILED'];
const STUCK_LIMIT_S = 900;        // NFR-04 · 15 นาที
const WATCHDOG_GRACE_S = 30;      // รอบตรวจของ dispatcher

/**
 * Gateway call. Same contract as helpers.gateway, but sets the TLS servername only for a host NAME:
 * GATEWAY_URL here is an IP address, and Node refuses `servername` = IP (ERR_INVALID_ARG_VALUE).
 * Never logs the key.
 */
function gw(method: string, p: string, key: 'good' | 'none' | 'wrong', body?: { form: Buffer; boundary: string }): Promise<{ status: number; json: any; headers: any }> {
  const u = new URL(gatewayUrl() + p);
  const ca = fs.readFileSync(path.join(ROOT, 'results', 'deploy', 'gateway_ca.crt'));
  const headers: any = {};
  if (key === 'good') headers['X-API-Key'] = gatewayKey();
  if (key === 'wrong') headers['X-API-Key'] = 'wrong-key-0000000000';
  if (body) { headers['content-type'] = 'multipart/form-data; boundary=' + body.boundary; headers['content-length'] = body.form.length; }
  const opts: any = { method, hostname: u.hostname, port: u.port, path: u.pathname + u.search, headers, ca, rejectUnauthorized: true, timeout: 30000 };
  if (!net.isIP(u.hostname)) opts.servername = u.hostname;
  return new Promise((resolve, reject) => {
    const req = https.request(opts, res => {
      const chunks: Buffer[] = []; res.on('data', c => chunks.push(c)); res.on('end', () => {
        const t = Buffer.concat(chunks).toString('utf8'); let j: any = null; try { j = JSON.parse(t); } catch { }
        resolve({ status: res.statusCode || 0, json: j, headers: res.headers });
      });
    });
    req.on('error', reject); req.on('timeout', () => req.destroy(new Error('gateway timeout')));
    if (body) req.write(body.form); req.end();
  });
}

/** Good-key GET /v1/health, never throws (evidence only). */
async function gwHealth() {
  const at = new Date().toISOString();
  try { const r = await gw('GET', '/v1/health', 'good'); return { at, status: r.status, body: r.json }; }
  catch (e: any) { return { at, status: 0, error: String(e?.message || e) }; }
}

/** Wait until the gateway reports queue_depth == 0 (good key). */
async function waitGatewayQueueEmpty(maxMs: number) {
  const t0 = Date.now(); let last: any = null;
  while (Date.now() - t0 < maxMs) {
    last = await gwHealth();
    if (last.status === 200 && last.body?.queue_depth === 0) return { empty: true, waitedS: Math.round((Date.now() - t0) / 1000), health: last };
    await sleep(10000);
  }
  return { empty: false, waitedS: Math.round((Date.now() - t0) / 1000), health: last };
}

/** GET /api/photos/{id} → the photo object (response is {photo:{...}}). */
async function getPhoto(cookie: string, id: string) {
  const r = await http('GET', `/api/photos/${id}`, { cookie });
  return { status: r.status, photo: (r.json?.photo ?? r.json) as any };
}
const hasResult = (p: any) => !!p && (p.current_result != null || p.model_result != null || TERMINAL.has(p.status));

/** Sum of the 4 status counters in a batch `counts` object, whatever the key case. null if none found. */
function countsSum(c: any): { sum: number | null; raw: any } {
  if (!c || typeof c !== 'object') return { sum: null, raw: c };
  let sum = 0, found = 0;
  for (const [k, v] of Object.entries(c)) if (STATUSES.includes(k.toUpperCase()) && typeof v === 'number') { sum += v; found++; }
  return { sum: found ? sum : null, raw: c };
}

async function openBatchPage(ctx: BrowserContext, cookie: string, batchId: string) {
  await cookieToContext(ctx, cookie);
  const page = await ctx.newPage();
  await page.goto(`${UI}/uploads/${batchId}`);
  await page.waitForLoadState('networkidle').catch(() => { });
  return page;
}

async function blockedTC(testInfo: TestInfo, tc: string, needs: string[], reason: string) {
  await reset();
  await login('U2');
  const health = await gwHealth();
  await evidence(testInfo, 'evidence', {
    tc, run: 'blocked · ไม่ได้ส่งงานหรือรูปใดเลย',
    needs, gateway_health_now: health,
    note: 'เครื่อง GPU เป็นเครื่องเช่า ห้ามหยุด Worker / ห้ามแก้ MAX_QUEUE_DEPTH / ไม่มี shell และไม่มีสิทธิ์อ่าน jobs.db',
  });
  blockedIfClean(testInfo, reason);
}

// ---------------- TC-3-01 ----------------
test('TC-3-01 [P1] ปิดหน้าแล้วรูปไม่หาย สถานะ 4 ค่ารวม 10 จบเสร็จแล้ว 10', async ({ context }, testInfo) => {
  await reset();
  const cookie = await login('U2');
  useRealBudget(10, 'TC-3-01');
  const files = Array.from({ length: 10 }, (_, i) => ({ path: fixture('h0_v0.jpg'), name: `h0_v0_${String(i + 1).padStart(2, '0')}.jpg` }));
  const { batchId, items } = await upload(cookie, files);
  items.forEach((it, i) => expect.soft(it.status, `ไฟล์ที่ ${i + 1} ต้องได้ 201`).toBe(201));
  const stored = items.map(i => i.photoId).filter(Boolean) as string[];
  expect.soft(stored.length, 'เก็บ photoId ได้ครบ 10').toBe(10);
  const storedSet = new Set(stored);

  // เปิดหน้าสถานะแล้วปิดทันที
  const p1 = await openBatchPage(context, cookie, batchId);
  await p1.close();

  const t0 = Date.now(); const polls: any[] = []; const prev = new Map<string, string>();
  let regressions: any[] = []; let last: any = null; let allDone = false;
  while (Date.now() - t0 < 10 * 60 * 1000) {
    const r = await batchStatus(cookie, batchId);
    last = r.json;
    const ph: any[] = last?.photos || [];
    const ids = ph.map(p => p.id);
    const sameSet = ids.length === storedSet.size && new Set(ids).size === ids.length && ids.every(id => storedSet.has(id));
    const byStatus: Record<string, number> = { QUEUED: 0, PROCESSING: 0, DONE: 0, FAILED: 0 };
    for (const p of ph) if (p.status in byStatus) byStatus[p.status]++;
    const sumPhotos = Object.values(byStatus).reduce((a, b) => a + b, 0);
    const cs = countsSum(last?.counts);
    for (const p of ph) {
      if (prev.get(p.id) === 'DONE' && p.status !== 'DONE') regressions.push({ t: (Date.now() - t0) / 1000, id: p.id, to: p.status });
      prev.set(p.id, p.status);
    }
    polls.push({ t_s: Math.round((Date.now() - t0) / 100) / 10, http: r.status, sameSet, byStatus, sumPhotos, counts: cs.raw, countsSum: cs.sum });
    expect.soft(r.status, 'GET /api/uploads/{batchId} ต้องได้ 200').toBe(200);
    expect.soft(sameSet, `ทุกครั้งที่ถาม ชุด photoId = 10 รหัสที่เก็บไว้ (poll ${polls.length})`).toBe(true);
    expect.soft(sumPhotos, `รอคิว+กำลังตรวจ+เสร็จแล้ว+ตรวจไม่สำเร็จ = 10 จากรายการรูป (poll ${polls.length})`).toBe(10);
    if (cs.sum !== null) expect.soft(cs.sum, `ตัวนับ 4 สถานะใน counts รวม = 10 (poll ${polls.length})`).toBe(10);
    if (ph.length && ph.every(p => TERMINAL.has(p.status))) { allDone = true; break; }
    await sleep(2000);
  }
  const final = (last?.photos || []) as any[];
  expect.soft(regressions, 'ไม่มีรูปใดย้อนจาก "เสร็จแล้ว" ไปสถานะอื่น').toEqual([]);
  expect.soft(allDone, 'ทุกรูปถึงสถานะปลายทางภายใน 10 นาที').toBe(true);
  expect.soft(final.filter(p => p.status === 'DONE').length, 'จบที่ เสร็จแล้ว 10 แม้ปิดหน้า').toBe(10);
  expect.soft(countsSum(last?.counts).sum === null, 'ตัวนับ 4 สถานะใน counts อ่านได้').toBe(false);

  const page = await openBatchPage(context, cookie, batchId);
  await sleep(3000);
  await shot(testInfo, page, 'uploads-batch-end');
  await evidence(testInfo, 'evidence', {
    tc: 'TC-3-01', note: 'แผนเขียน mock แต่เครื่องนี้ ai_mode=real จึงรันกับโมเดลจริง (งบ 10 รูป)',
    batchId, upload_status: items.map((it, i) => ({ name: files[i].name, status: it.status, photoId: it.photoId })),
    stored_ids: stored, elapsed_s: (Date.now() - t0) / 1000, polls_count: polls.length, regressions,
    final: final.map(p => ({ id: p.id, status: p.status, fail_reason: p.fail_reason })), last_counts: last?.counts, polls,
  });
});

// ---------------- TC-3-02 ----------------
test('TC-3-02 [P1] gateway ไม่มี key หรือ key ผิด ปฏิเสธ 401 ทั้ง 8 คำขอ', async ({ }, testInfo) => {
  await reset();
  await login('U2');
  const before = await gwHealth();
  const jobId = crypto.randomUUID();
  const routes: { method: string; path: string; form: boolean }[] = [
    { method: 'POST', path: '/v1/jobs', form: true },
    { method: 'GET', path: `/v1/jobs/${jobId}`, form: false },
    { method: 'GET', path: `/v1/jobs?ids=${jobId}`, form: false },
    { method: 'GET', path: '/v1/health', form: false },
  ];
  const results: any[] = [];
  for (const key of ['none', 'wrong'] as const) {
    for (const r of routes) {
      const res = await gw(r.method, r.path, key, r.form ? jobForm(jobId, fixture('h0_v0.jpg')) : undefined);
      results.push({ key, method: r.method, path: r.path.replace(jobId, '{uuid}'), status: res.status, error: res.json?.error });
      expect.soft(res.status, `${r.method} ${r.path.replace(jobId, '{uuid}')} key=${key} ต้องได้ 401`).toBe(401);
      expect.soft(res.json?.error, `${r.method} ${r.path.replace(jobId, '{uuid}')} key=${key} เนื้อคำตอบ error = UNAUTHORIZED`).toBe('UNAUTHORIZED');
    }
  }
  const rejected = results.filter(r => r.status === 401).length;
  expect.soft(rejected, '8 / 8 คำขอถูกปฏิเสธ (100%)').toBe(8);
  // "ไม่มีงานใหม่": งาน UUID ที่ส่งไปไม่อยู่ใน gateway
  const check = await gw('GET', `/v1/jobs/${jobId}`, 'good');
  expect.soft(check.status, 'GET /v1/jobs/{uuid} ด้วย key ถูก ต้องได้ 404 (ไม่มีงานถูกสร้าง)').toBe(404);
  const after = await gwHealth();
  const control = after;
  expect.soft(control.status, 'ตัวควบคุม GET /v1/health ด้วย key ถูก ต้องได้ 200').toBe(200);
  expect.soft((after as any).body?.queue_depth, 'queue_depth ก่อน = หลัง (แทนการนับ jobs.db)').toBe((before as any).body?.queue_depth);
  await evidence(testInfo, 'evidence', {
    tc: 'TC-3-02', requests: results, rejected_401: `${rejected}/8`,
    job_lookup_with_good_key: { status: check.status, error: check.json?.error },
    queue_depth_before: (before as any).body?.queue_depth, queue_depth_after: (after as any).body?.queue_depth,
    control_health: { status: control.status, body: (control as any).body },
    note: 'ไม่มีสิทธิ์อ่าน jobs.db บนเครื่อง GPU จึงใช้ (1) GET /v1/jobs/{uuid} ด้วย key ถูก → 404 และ (2) queue_depth จาก /v1/health ก่อน/หลัง แทนการนับแถว jobs.db · queue_depth อาจขยับได้ถ้าผู้ทดสอบคนอื่นส่งรูปพร้อมกัน · ไม่ใช้รูปเข้า GPU',
  });
});

// ---------------- blocked: need MAX_QUEUE_DEPTH / Worker control on the rented machine ----------------
test('TC-3-03 [P1] คิวเต็มที่ 5 งาน งานที่ 6 ได้ 429 QUEUE_FULL', async ({ }, testInfo) => {
  await blockedTC(testInfo, 'TC-3-03', ['MAX_QUEUE_DEPTH=5', 'หยุด Worker', 'นับงานใน jobs.db'],
    'ต้องตั้ง MAX_QUEUE_DEPTH=5 และหยุด Worker บนเครื่อง GPU ที่เช่า ซึ่งห้ามแตะ และอ่าน jobs.db ไม่ได้');
});
test('TC-3-04 [P2] งานที่ถูกปฏิเสธเพราะคิวเต็มส่งใหม่ด้วย job_id เดิมได้', async ({ }, testInfo) => {
  await blockedTC(testInfo, 'TC-3-04', ['ต่อจาก TC-3-03', 'เปิด/หยุด Worker', 'MAX_QUEUE_DEPTH=5'],
    'ต่อจาก TC-3-03 ต้องหยุดและเปิด Worker และตั้ง MAX_QUEUE_DEPTH=5 บนเครื่อง GPU ที่ห้ามแตะ');
});
test('TC-3-05 [P2] ส่ง job_id ซ้ำได้ 200 สถานะเดิม ไม่สร้างงานซ้ำ', async ({ }, testInfo) => {
  await blockedTC(testInfo, 'TC-3-05', ['หยุด Worker ให้งานค้างคงที่ 3', 'นับแถว jobs ของ X ใน jobs.db'],
    'ต้องหยุด Worker ให้งานค้างคงที่ 3 งาน และนับแถวใน jobs.db บนเครื่อง GPU ที่ห้ามแตะ');
});
test('TC-3-06 [P1] Worker ล่มกลางคัน 100 รูปไม่หาย ผลชุดเดียว (รอบ B)', async ({ }, testInfo) => {
  await blockedTC(testInfo, 'TC-3-06', ['รอบ B งบ GPU 100 รูป', 'หยุด Worker 30 วินาที'],
    'เป็นรอบ B ต้องอนุมัติงบ GPU 100 รูปแยก และต้องหยุด/เปิด Worker บนเครื่อง GPU ที่ห้ามแตะ');
});

// ---------------- TC-3-07 ----------------
test('TC-3-07 [P1] ทำซ้ำ D-1 ไฟล์ใหญ่/ไฟล์เสีย/ไซต์ ถึงสถานะปลายทางภายใน 900 วินาที', async ({ context }, testInfo) => {
  test.setTimeout(55 * 60 * 1000);
  await reset();
  await login('U3');
  const rounds = [
    { round: 1, user: 'U3' as const, site: 'SITE-B', files: [{ key: 'F-1', path: fixture('h0_v0_14_9mb.jpg') }, { key: 'F-2', path: fixture('h0_v0_15_0mb.jpg') }, { key: 'F-10', path: fixture('corrupt_half.jpg') }] },
    { round: 2, user: 'U2' as const, site: 'SITE-A', files: [{ key: 'F-1', path: fixture('h0_v0_14_9mb.jpg') }, { key: 'F-2', path: fixture('h0_v0_15_0mb.jpg') }, { key: 'F-10', path: fixture('corrupt_half.jpg') }] },
    { round: 3, user: 'U3' as const, site: 'SITE-B', files: [{ key: 'normal', path: testImage('000005') }] },
  ];
  const expected: Record<string, { status: string; label?: string; reason?: string }> = {
    'F-1': { status: 'DONE', label: 'เสร็จแล้ว' }, 'F-2': { status: 'DONE', label: 'เสร็จแล้ว' },
    'F-10': { status: 'FAILED', label: 'ตรวจไม่สำเร็จ', reason: 'เปิดไฟล์รูปไม่ได้' }, 'normal': { status: 'DONE', label: 'เสร็จแล้ว' },
  };
  const out: any[] = [];
  for (const rd of rounds) {
    const pre = await waitGatewayQueueEmpty(5 * 60 * 1000);
    await reset();
    const cookie = await login(rd.user);
    useRealBudget(rd.files.length, `TC-3-07 round ${rd.round}`);
    const { batchId, items } = await upload(cookie, rd.files.map(f => ({ path: f.path })));
    const photos = rd.files.map((f, i) => ({
      key: f.key, file: path.basename(f.path), bytes: fs.statSync(f.path).size, http: items[i].status, id: items[i].photoId,
      acceptedAt: items[i].acceptedAt, everProcessing: false, terminalS: null as number | null, status: null as string | null,
      label: null as string | null, fail_reason: null as string | null,
    }));
    photos.forEach(p => expect.soft(p.http, `รอบ ${rd.round} ${p.key} (${p.file}) ต้องได้ 201`).toBe(201));
    const t0 = Date.now(); const timeline: any[] = []; let lastSig = '';
    while (Date.now() - t0 < (STUCK_LIMIT_S + WATCHDOG_GRACE_S) * 1000) {
      for (const p of photos) {
        if (!p.id || (p.status && TERMINAL.has(p.status))) continue;
        const g = await getPhoto(cookie, p.id);
        p.status = g.photo?.status ?? `HTTP ${g.status}`; p.label = g.photo?.status_label ?? null; p.fail_reason = g.photo?.fail_reason ?? null;
        if (p.status === 'PROCESSING') p.everProcessing = true;
        if (TERMINAL.has(p.status!) && p.terminalS === null) p.terminalS = Math.round((Date.now() - p.acceptedAt) / 100) / 10;
      }
      const sig = photos.map(p => `${p.key}:${p.status}`).join(' ');
      if (sig !== lastSig) { timeline.push({ t_s: Math.round((Date.now() - t0) / 1000), statuses: sig }); lastSig = sig; }
      if (photos.every(p => !p.id || (p.status && TERMINAL.has(p.status)))) break;
      await sleep(5000);
    }
    for (const p of photos) {
      const e = expected[p.key];
      expect.soft(p.terminalS !== null && p.terminalS <= STUCK_LIMIT_S, `รอบ ${rd.round} ${p.key} ถึงสถานะปลายทางภายใน 900 วินาที (ได้ ${p.terminalS ?? 'ไม่ถึง'} วินาที)`).toBe(true);
      expect.soft(p.status, `รอบ ${rd.round} ${p.key} สถานะปลายทาง = ${e.status}`).toBe(e.status);
      if (e.label) expect.soft(p.label, `รอบ ${rd.round} ${p.key} ป้ายสถานะ = "${e.label}"`).toBe(e.label);
      if (e.reason) expect.soft(p.fail_reason, `รอบ ${rd.round} ${p.key} เหตุผล = "${e.reason}"`).toBe(e.reason);
    }
    const page = await openBatchPage(context, cookie, batchId);
    await sleep(3000);
    await shot(testInfo, page, `round${rd.round}-uploads-batch`);
    await page.close();
    const stalled = photos.some(p => p.terminalS === null || p.terminalS > 30 || p.fail_reason === 'เกินเวลา 15 นาที');
    out.push({
      round: rd.round, user: rd.user, site: rd.site, batchId, queue_before: { empty: pre.empty, waited_s: pre.waitedS, depth: pre.health?.body?.queue_depth },
      stalled_over_30s_or_timeout: stalled,
      photos: photos.map(({ acceptedAt, ...p }) => ({ ...p, accepted_at: new Date(acceptedAt).toISOString() })),
      timeline,
    });
  }
  const [r1, r2, r3] = out.map(o => o.stalled_over_30s_or_timeout);
  const diagnosis = !r1 && !r2 && !r3 ? 'ไม่ค้างทุกรอบ (D-1 ไม่เกิดซ้ำ)'
    : r1 && r2 && r3 ? 'ค้างทุกรอบ รวมรูปปกติ → ไม่ผูกกับไซต์หรือขนาดไฟล์ (ทั้งหมด)'
      : r1 && r2 && !r3 ? 'ค้างรอบ 1 และ 2 แต่รูปปกติไม่ค้าง → ผูกกับขนาดไฟล์ / ไฟล์เสีย'
        : r1 && !r2 ? 'ค้างรอบ 1 (SITE-B) แต่รอบ 2 (SITE-A) ไม่ค้าง → ผูกกับไซต์' + (r3 ? ' (รอบ 3 SITE-B ก็ค้าง)' : '')
          : `รูปแบบอื่น r1=${r1} r2=${r2} r3=${r3}`;
  await evidence(testInfo, 'evidence', { tc: 'TC-3-07', poll_every_s: 5, cap_s: STUCK_LIMIT_S, grace_s: WATCHDOG_GRACE_S, diagnosis, rounds: out });
});

// ---------------- TC-3-08 ----------------
test('TC-3-08 [P1] ภาระปกติ 20 รูป p95 เวลารอผล ≤ 30 วินาที ผลขึ้นทีละรูป', async ({ context }, testInfo) => {
  test.setTimeout(25 * 60 * 1000);
  await reset();
  const cookie = await login('U2');
  const files = allTestImages();
  expect.soft(files.length, 'โฟลเดอร์ test_images มี 20 รูป').toBe(20);
  const health = await gwHealth();
  useRealBudget(files.length, 'TC-3-08');
  const b = await openBatch(cookie, files.length);
  expect(b.status, 'เปิด batch ต้องได้ 201').toBe(201);
  const batchId = b.json.batch_id as string;

  type Row = { file: string; http?: number; id?: string; start?: number; endS: number | null; status?: string };
  const rows: Row[] = files.map(f => ({ file: path.basename(f), endS: null }));
  let uploading = true; let interleaved: any = null; let polls = 0; let lastAccepted = Date.now();
  // ส่งทีละไฟล์ และถามสถานะทุก 1 วินาทีไปพร้อมกัน เวลาเริ่ม = เวลาได้ 201 ของแต่ละรูป
  const uploader = (async () => {
    for (let i = 0; i < files.length; i++) {
      const r = await sendFile(cookie, batchId, files[i]);
      rows[i].http = r.status; rows[i].id = r.photoId; rows[i].start = r.acceptedAt; lastAccepted = r.acceptedAt;
    }
    uploading = false;
  })();
  const poller = (async () => {
    while (true) {
      const pending = rows.filter(r => r.id && r.endS === null);
      const now0 = Date.now();
      if (!uploading && pending.length === 0) break;
      if (!uploading && now0 - lastAccepted > STUCK_LIMIT_S * 1000) break;
      const snap = await Promise.all(rows.filter(r => r.id).map(async r => ({ r, g: await getPhoto(cookie, r.id!) })));
      polls++;
      const tNow = Date.now();
      for (const { r, g } of snap) {
        r.status = g.photo?.status;
        if (r.endS === null && hasResult(g.photo)) r.endS = Math.round((tNow - r.start!) / 100) / 10;
      }
      const withResult = snap.filter(s => hasResult(s.g.photo)).length;
      const waiting = snap.filter(s => s.g.photo?.status === 'QUEUED' || s.g.photo?.status === 'PROCESSING').length;
      if (!interleaved && withResult >= 1 && waiting >= 1) interleaved = { poll: polls, with_result: withResult, queued_or_processing: waiting };
      await sleep(Math.max(0, 1000 - (Date.now() - now0)));
    }
  })();
  await uploader; await poller;

  rows.forEach(r => expect.soft(r.http, `${r.file} ต้องได้ 201`).toBe(201));
  const times = rows.map(r => r.endS === null ? STUCK_LIMIT_S : Math.min(r.endS, STUCK_LIMIT_S));
  const sorted = [...times].sort((a, b) => a - b);
  const rank = Math.ceil(0.95 * sorted.length);           // 20 รูป → ลำดับที่ 19
  const p95 = sorted[rank - 1];
  expect.soft(rank, 'p95 nearest-rank ของ 20 ค่า = ลำดับที่ 19').toBe(19);
  expect.soft(p95, `p95 เวลารอผล ≤ 30 วินาที (ได้ ${p95} วินาที)`).toBeLessThanOrEqual(30);
  expect.soft(interleaved !== null, 'มีอย่างน้อย 1 ครั้งที่บางรูปมีผลขณะที่รูปอื่นยัง รอคิว/กำลังตรวจ (ผลขึ้นทีละรูป)').toBe(true);
  expect.soft(health.status, 'GET /v1/health ด้วย key ถูก ต้องได้ 200').toBe(200);
  const gpu = (health as any).body?.gpu;
  expect.soft(typeof gpu === 'string' && gpu.length > 0, 'gateway รายงานรุ่น GPU').toBe(true);
  expect.soft(typeof gpu === 'string' && !/[,;]/.test(gpu), 'gateway รายงาน GPU 1 ใบ (ชื่อเดียว)').toBe(true);
  expect.soft((health as any).body?.workers, 'workers = 1 (เครื่องมี GPU 1 ใบ)').toBe(1);

  const page = await openBatchPage(context, cookie, batchId);
  await sleep(3000);
  await shot(testInfo, page, 'uploads-batch-end');
  await evidence(testInfo, 'evidence', {
    tc: 'TC-3-08', batchId, poll_every_s: 1, cap_s: STUCK_LIMIT_S, polls,
    gpu, workers: (health as any).body?.workers, gateway_health: health,
    per_photo: rows.map(r => ({ file: r.file, http: r.http, photoId: r.id, accepted_at: r.start ? new Date(r.start).toISOString() : null, wait_s: r.endS, counted_s: r.endS === null ? STUCK_LIMIT_S : r.endS, final_status: r.status })),
    times_sorted_s: sorted, p95_rank: rank, p95_s: p95, interleaved,
  });
});

// ---------------- blocked ----------------
test('TC-3-09 [P1] รูปค้างเกิน 15 นาทีเป็นตรวจไม่สำเร็จ ผลที่มาช้าไม่เปลี่ยนสถานะ', async ({ }, testInfo) => {
  await blockedTC(testInfo, 'TC-3-09', ['หยุด Worker 15 นาที แล้วเปิดใหม่', 'นับแถว detections'],
    'ต้องหยุด Worker บนเครื่อง GPU ที่เช่า 15 นาทีแล้วเปิดใหม่ ซึ่งห้ามแตะเครื่องนั้น');
});
test('TC-3-10 [P1] คิว gateway เต็ม เว็บยังรับรูป 201 และส่งใหม่เองจนเสร็จแล้ว', async ({ }, testInfo) => {
  await blockedTC(testInfo, 'TC-3-10', ['MAX_QUEUE_DEPTH=5', 'หยุด Worker แล้วเติมงานให้ค้าง 5', 'นับแถว jobs'],
    'ต้องตั้ง MAX_QUEUE_DEPTH=5 และหยุด Worker บนเครื่อง GPU ที่เช่า ซึ่งห้ามแตะ');
});
