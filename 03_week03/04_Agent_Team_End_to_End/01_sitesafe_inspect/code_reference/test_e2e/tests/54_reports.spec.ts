// Test Plan 5.4 รายงานและการแก้ผล (BR-04 · BR-07 · FR-13–FR-17 · NFR-07)
// Expected values come ONLY from test/TEST-PLAN.md 5.4 and docs/TEST-DATA.md (P-1–P-9, T-1–T-6, O-1–O-6).
// Machine: ai_mode=real, no mock-gateway -> TC-4-04 (1 photo) and TC-4-06 (3 photos) reach the rented GPU.
import { test, expect, type Page, type Browser } from '@playwright/test';
import {
  API, UI, reset, login, http, uiLogin, cookieToContext, fixture, upload, waitBatchTerminal,
  allPhotos, useRealBudget, evidence, shot, RESULT_TH, type UserKey,
} from './helpers';

// ---------------- local helpers ----------------
const D1 = '2026-11-16', D2 = '2026-11-17', D3 = '2026-11-18';
const SITES = ['SITE-A', 'SITE-B', 'SITE-C'] as const;
type Site = typeof SITES[number];
const BADGE_READY = 'รายงานประจำวันพร้อมแล้ว';
const BADGE_INTRADAY = 'ข้อมูลระหว่างวัน';
const NO_DATA = 'ไม่มีข้อมูล';
const NO_RESULT = 'ยังไม่มีผล';

/** rate: number = percent from the plan (2 decimals) · string = text that must be shown ("ไม่มีข้อมูล" / "ยังไม่มีผล"). */
interface Exp { taken: number; fail: number; h: number; rate: number | string; red: boolean; edited: number; failed: number }

/** true when the site's text/number equals the plan's percent to 2 decimals (accepts "89.67", "89.67%", 89.666…). */
function rateEquals(actual: any, expected: number): boolean {
  if (actual === null || actual === undefined) return false;
  const n = typeof actual === 'number' ? actual : Number(String(actual).replace(/[%\s,]/g, ''));
  return Number.isFinite(n) && n.toFixed(2) === expected.toFixed(2);
}
const num = (t: string | null | undefined) => Number(String(t ?? '').replace(/[^\d.-]/g, ''));

async function reportApi(cookie: string, date: string) {
  const r = await http('GET', `/api/reports/daily?date=${date}`, { cookie });
  return { status: r.status, json: r.json };
}
function siteRow(json: any, site: Site) { return (json?.sites || []).find((s: any) => s?.site?.code === site); }

/** Soft-check one site's row of the API report against the plan. */
function checkApiRow(json: any, site: Site, e: Exp, tag: string) {
  const r = siteRow(json, site);
  expect.soft(r, `${tag} API: ต้องมีแถว ${site}`).toBeTruthy();
  if (!r) return;
  expect.soft(r.taken, `${tag} API ${site}: รูปที่ถ่ายต้องเป็น ${e.taken}`).toBe(e.taken);
  expect.soft(r.fail, `${tag} API ${site}: รูปไม่ผ่านต้องเป็น ${e.fail}`).toBe(e.fail);
  expect.soft(r.h_total, `${tag} API ${site}: คนไม่ใส่หมวก (H รวม) ต้องเป็น ${e.h}`).toBe(e.h);
  if (typeof e.rate === 'number') {
    const v = r.pass_rate_text ?? r.pass_rate;
    expect.soft(rateEquals(v, e.rate), `${tag} API ${site}: อัตราผ่านต้องเป็น ${e.rate.toFixed(2)}% (ได้ ${JSON.stringify(v)})`).toBe(true);
  } else {
    expect.soft(String(r.pass_rate_text ?? ''), `${tag} API ${site}: อัตราผ่านต้องแสดง "${e.rate}"`).toContain(e.rate);
  }
  expect.soft(r.red, `${tag} API ${site}: สีแดงต้องเป็น ${e.red}`).toBe(e.red);
  expect.soft(r.edited, `${tag} API ${site}: ถูกแก้ผลต้องเป็น ${e.edited}`).toBe(e.edited);
  expect.soft(r.failed, `${tag} API ${site}: ตรวจไม่สำเร็จต้องเป็น ${e.failed}`).toBe(e.failed);
}

/** Open /reports/daily, choose the date with report-date + report-apply. */
async function openReportUI(page: Page, date: string) {
  await page.goto(UI + '/reports/daily');
  await page.getByTestId('report-date').fill(date);
  await page.getByTestId('report-apply').click();
  await page.waitForURL(u => u.search.includes(date), { timeout: 15000 }).catch(() => { });
  await page.waitForLoadState('networkidle').catch(() => { });
  await page.getByTestId('report-row-SITE-A').waitFor({ timeout: 15000 }).catch(() => { });
}

/** Read the 6 values + data-red of one site from the UI. */
async function readUiRow(page: Page, site: Site) {
  const t = async (id: string) => { const l = page.getByTestId(id); return (await l.count()) ? (await l.first().textContent())?.trim() ?? '' : null; };
  const redL = page.getByTestId(`report-red-${site}`);
  return {
    row: (await page.getByTestId(`report-row-${site}`).count()) > 0,
    taken: await t(`report-taken-${site}`), fail: await t(`report-fail-${site}`), h: await t(`report-h-${site}`),
    rate: await t(`report-rate-${site}`), edited: await t(`report-edited-${site}`), failed: await t(`report-failed-${site}`),
    red: (await redL.count()) ? await redL.first().getAttribute('data-red') : null,
  };
}

/** Soft-check one site's UI row against the plan. Returns what was read (for evidence). */
async function checkUiRow(page: Page, site: Site, e: Exp, tag: string) {
  const u = await readUiRow(page, site);
  expect.soft(u.row, `${tag} หน้าเว็บ: ต้องมีแถว report-row-${site}`).toBe(true);
  expect.soft(num(u.taken), `${tag} หน้าเว็บ ${site}: รูปที่ถ่ายต้องเป็น ${e.taken} (ได้ "${u.taken}")`).toBe(e.taken);
  expect.soft(num(u.fail), `${tag} หน้าเว็บ ${site}: รูปไม่ผ่านต้องเป็น ${e.fail} (ได้ "${u.fail}")`).toBe(e.fail);
  expect.soft(num(u.h), `${tag} หน้าเว็บ ${site}: คนไม่ใส่หมวกต้องเป็น ${e.h} (ได้ "${u.h}")`).toBe(e.h);
  if (typeof e.rate === 'number') {
    expect.soft(rateEquals(u.rate, e.rate), `${tag} หน้าเว็บ ${site}: อัตราผ่านต้องเป็น ${e.rate.toFixed(2)}% (ได้ "${u.rate}")`).toBe(true);
  } else {
    expect.soft(u.rate ?? '', `${tag} หน้าเว็บ ${site}: อัตราผ่านต้องแสดง "${e.rate}"`).toContain(e.rate);
  }
  expect.soft(u.red, `${tag} หน้าเว็บ ${site}: report-red data-red ต้องเป็น "${e.red}"`).toBe(String(e.red));
  expect.soft(num(u.edited), `${tag} หน้าเว็บ ${site}: ถูกแก้ผลต้องเป็น ${e.edited} (ได้ "${u.edited}")`).toBe(e.edited);
  expect.soft(num(u.failed), `${tag} หน้าเว็บ ${site}: ตรวจไม่สำเร็จต้องเป็น ${e.failed} (ได้ "${u.failed}")`).toBe(e.failed);
  return u;
}

/** Browser page logged in with an API cookie. */
async function pageFor(browser: Browser, cookie: string) {
  const ctx = await browser.newContext({ locale: 'th-TH', timezoneId: 'Asia/Bangkok' });
  await cookieToContext(ctx, cookie);
  return { ctx, page: await ctx.newPage() };
}

async function history(cookie: string, photoId: string) {
  const r = await http('GET', `/api/photos/${photoId}/overrides`, { cookie });
  return { status: r.status, json: r.json, rows: (r.json?.overrides || []) as any[] };
}
async function override(cookie: string, photoId: string, result: string, reason: string) {
  const r = await http('POST', `/api/photos/${photoId}/overrides`, { cookie, json: { result, reason } });
  return { status: r.status, json: r.json };
}
async function photo(cookie: string, id: string) { return (await http('GET', `/api/photos/${id}`, { cookie })).json?.photo; }
/** The 5 audit fields of a history row (for "unchanged" comparisons). */
const five = (r: any) => ({ by: r?.edited_by?.id ?? r?.edited_by, at: r?.edited_at, before: r?.result_before, after: r?.result_after, reason: r?.reason });

/** {failA}: first (by id) D1 SITE-A photo with h=1,v=0 · {passC}: first (by id) D1 SITE-C PASS photo. Seed ids are fixed. */
async function findFailA(cookie: string) {
  const all = (await allPhotos(cookie, `date=${D1}&site=SITE-A`)).photos.sort((a: any, b: any) => (a.id < b.id ? -1 : 1));
  const p = all.find((x: any) => x.h === 1 && x.v === 0); if (!p) throw new Error('no {failA}'); return p.id as string;
}
async function findPassC(cookie: string) {
  const all = (await allPhotos(cookie, `date=${D1}&site=SITE-C`)).photos.sort((a: any, b: any) => (a.id < b.id ? -1 : 1));
  const p = all.find((x: any) => x.current_result === 'PASS' && x.model_result === 'PASS'); if (!p) throw new Error('no {passC}'); return p.id as string;
}

// Seed expectations (TEST-DATA P-1 – P-9)
const P1: Exp = { taken: 300, fail: 20, h: 15, rate: 89.67, red: true, edited: 0, failed: 0 };
const P2: Exp = { taken: 300, fail: 20, h: 20, rate: 90.00, red: false, edited: 0, failed: 0 };
const P3: Exp = { taken: 300, fail: 20, h: 20, rate: 90.33, red: false, edited: 0, failed: 0 };
const P4: Exp = { taken: 0, fail: 0, h: 0, rate: NO_DATA, red: false, edited: 0, failed: 0 };
const P5: Exp = { taken: 10, fail: 0, h: 0, rate: 90.00, red: false, edited: 0, failed: 0 };
const P6: Exp = { taken: 10, fail: 0, h: 0, rate: 100.00, red: false, edited: 0, failed: 1 };
const P7: Exp = { taken: 300, fail: 19, h: 15, rate: 90.00, red: false, edited: 1, failed: 0 };
const P8: Exp = { taken: 12, fail: 1, h: 1, rate: 80.00, red: true, edited: 0, failed: 0 };
const P9: Exp = { taken: 1, fail: 1, h: 2, rate: 0.00, red: true, edited: 0, failed: 0 };

/** Shared body of TC-4-01/02/03: U-1 opens one seed date; check API + UI for 3 sites. */
async function seedReport(browser: Browser, testInfo: any, date: string, exp: Record<Site, Exp>, tag: string) {
  await reset();
  const c1 = await login('U1');
  const api = await reportApi(c1, date);
  expect.soft(api.status, `${tag} API รายงาน ${date} ต้องตอบ 200`).toBe(200);
  expect.soft((api.json?.sites || []).length, `${tag} รายงานต้องมีครบ 3 ไซต์`).toBe(3);
  for (const s of SITES) checkApiRow(api.json, s, exp[s], tag);
  const { ctx, page } = await pageFor(browser, c1);
  await openReportUI(page, date);
  const ui: any = {};
  for (const s of SITES) ui[s] = await checkUiRow(page, s, exp[s], tag);
  await shot(testInfo, page, `report-${date}`);
  await evidence(testInfo, 'evidence', { date, expected: exp, api: api.json, ui });
  await ctx.close();
}

test.describe('5.4 รายงานและการแก้ผล', () => {
  test('TC-4-01 [P1] รายงาน D1 เส้นแบ่งอัตราผ่าน 90% ต่ำกว่า/เท่ากับ/สูงกว่า', async ({ browser }, testInfo) => {
    await seedReport(browser, testInfo, D1, { 'SITE-A': P1, 'SITE-B': P2, 'SITE-C': P3 }, 'TC-4-01');
  });

  test('TC-4-02 [P2] รายงาน D2 วันไม่มีรูป รูปเตือน และรูปตรวจไม่สำเร็จ', async ({ browser }, testInfo) => {
    await seedReport(browser, testInfo, D2, { 'SITE-A': P4, 'SITE-B': P5, 'SITE-C': P6 }, 'TC-4-02');
  });

  test('TC-4-03 [P2] รายงาน D3 ใช้ผลล่าสุดและไม่นับรูปที่ยังไม่เสร็จ', async ({ browser }, testInfo) => {
    await seedReport(browser, testInfo, D3, { 'SITE-A': P7, 'SITE-B': P8, 'SITE-C': P9 }, 'TC-4-03');
  });

  test('TC-4-04 [P1] รายงานวันที่มีรูปแต่ยังไม่มีผล ไม่หารด้วยศูนย์', async ({ browser }, testInfo) => {
    const tag = 'TC-4-04';
    const date = '2026-11-19';
    await reset('2026-11-19T10:00:00+07:00');
    const c4 = await login('U4');
    useRealBudget(1, 'TC-4-04 corrupt_half.jpg');
    const up = await upload(c4, [{ path: fixture('corrupt_half.jpg') }]);
    const item = up.items[0];
    expect.soft(item.status, `${tag} อัปโหลด corrupt_half.jpg ต้องถูกรับ (201)`).toBe(201);
    let wait: any = null;
    if (item.status === 201) {
      wait = await waitBatchTerminal(c4, up.batchId, 16 * 60 * 1000, 5000);
      const st = (wait.last?.photos || []).find((p: any) => p.id === item.photoId)?.status;
      expect.soft(st, `${tag} รูปเสียต้องจบที่ "ตรวจไม่สำเร็จ" (FAILED) ภายใน 16 นาที`).toBe('FAILED');
    }
    const c1 = await login('U1');
    const api = await reportApi(c1, date);
    expect.soft(api.status, `${tag} API รายงาน ${date} ต้องตอบ 200`).toBe(200);
    const expC: Exp = { taken: 1, fail: 0, h: 0, rate: NO_RESULT, red: false, edited: 0, failed: 1 };
    const expEmpty: Exp = { taken: 0, fail: 0, h: 0, rate: NO_DATA, red: false, edited: 0, failed: 0 };
    const exp: Record<Site, Exp> = { 'SITE-A': expEmpty, 'SITE-B': expEmpty, 'SITE-C': expC };
    for (const s of SITES) checkApiRow(api.json, s, exp[s], tag);
    const { ctx, page } = await pageFor(browser, c1);
    await openReportUI(page, date);
    const ui: any = {};
    for (const s of SITES) ui[s] = await checkUiRow(page, s, exp[s], tag);
    await shot(testInfo, page, `report-${date}`);
    await evidence(testInfo, 'evidence', {
      upload: { batchId: up.batchId, status: item.status, photoId: item.photoId, body: item.json },
      wait: wait && { elapsedMs: wait.elapsedMs, last: wait.last, polls: wait.history.length },
      expected: exp, api: api.json, ui,
    });
    await ctx.close();
  });

  test('TC-4-05 [P1] ป้ายความพร้อมของรายงานที่ 17:59 / 18:00 / 18:01', async ({ browser }, testInfo) => {
    const tag = 'TC-4-05';
    const rounds = [
      { now: '2026-11-18T17:59:00+07:00', badge: BADGE_INTRADAY, ready: false },
      { now: '2026-11-18T18:00:00+07:00', badge: BADGE_READY, ready: true },
      { now: '2026-11-18T18:01:00+07:00', badge: BADGE_READY, ready: true },
    ];
    const exp: Record<Site, Exp> = { 'SITE-A': P7, 'SITE-B': P8, 'SITE-C': P9 };
    const ev: any[] = [];
    for (const r of rounds) {
      const t = `${tag} now=${r.now.slice(11, 16)}`;
      await reset(r.now);
      const h = await http('GET', '/api/health');
      const diff = Math.abs(Date.parse(h.json?.time) - Date.parse(r.now));
      expect.soft(Number.isFinite(diff) && diff <= 60_000, `${t} /api/health time ต้องตรงกับเวลาที่ตั้ง ${r.now} (ได้ ${h.json?.time})`).toBe(true);
      // U-5 logs in again (reset logged everyone out) through the login form
      const ctx = await browser.newContext({ locale: 'th-TH', timezoneId: 'Asia/Bangkok' });
      const page = await ctx.newPage();
      await uiLogin(page, 'U5');
      const c5 = await login('U5');
      const api = await reportApi(c5, D3);
      expect.soft(api.status, `${t} API รายงาน D3 ต้องตอบ 200`).toBe(200);
      expect.soft(api.json?.ready, `${t} API ready ต้องเป็น ${r.ready}`).toBe(r.ready);
      expect.soft(String(api.json?.ready_label ?? ''), `${t} API ป้ายต้องเป็น "${r.badge}"`).toContain(r.badge);
      await openReportUI(page, D3);
      const badge = (await page.getByTestId('report-ready-badge').textContent().catch(() => null))?.trim() ?? null;
      expect.soft(badge ?? '', `${t} หน้าเว็บ ป้าย report-ready-badge ต้องเป็น "${r.badge}"`).toContain(r.badge);
      if (r.ready) expect.soft(badge ?? '', `${t} หน้าเว็บ ป้ายต้องไม่ใช่ "${BADGE_INTRADAY}"`).not.toContain(BADGE_INTRADAY);
      const ui: any = {};
      if (r.ready) {
        expect.soft((api.json?.sites || []).length, `${t} รายงานต้องมีครบ 3 ไซต์`).toBe(3);
        for (const s of SITES) { checkApiRow(api.json, s, exp[s], t); ui[s] = await checkUiRow(page, s, exp[s], t); }
      }
      await shot(testInfo, page, `report-D3-${r.now.slice(11, 16).replace(':', '')}`);
      ev.push({ now: r.now, health: h.json, apiReady: api.json?.ready, apiLabel: api.json?.ready_label, badge, api: api.json, ui });
      await ctx.close();
    }
    await evidence(testInfo, 'evidence', { expected: { rounds, values: exp }, rounds: ev });
  });

  test('TC-4-06 [P1] รูปหลัง 18:00 และเส้นแบ่งวันตามเวลาไทย', async ({ browser }, testInfo) => {
    const tag = 'TC-4-06';
    const ev: any = {};

    // (ก) 18:30 upload h0_v0.jpg, wait DONE, U-5 opens D3
    await reset('2026-11-18T18:30:00+07:00');
    let c4 = await login('U4');
    useRealBudget(1, 'TC-4-06 (ก) h0_v0.jpg');
    const upA = await upload(c4, [{ path: fixture('h0_v0.jpg') }]);
    expect.soft(upA.items[0].status, `${tag}(ก) อัปโหลด h0_v0.jpg ต้องได้ 201`).toBe(201);
    const wA = await waitBatchTerminal(c4, upA.batchId, 5 * 60 * 1000, 3000);
    const stA = (wA.last?.photos || [])[0];
    expect.soft(stA?.status, `${tag}(ก) รูปต้องตรวจเสร็จ (DONE) ภายใน ~5 นาที`).toBe('DONE');
    const pA = upA.items[0].photoId ? await photo(c4, upA.items[0].photoId) : null;
    expect.soft(pA?.upload_date, `${tag}(ก) upload_date ของรูปที่ 18:30 ต้องเป็น ${D3}`).toBe(D3);
    let c5 = await login('U5');
    const apiA = await reportApi(c5, D3);
    const rC = siteRow(apiA.json, 'SITE-C');
    expect.soft(rC?.taken, `${tag}(ก) SITE-C D3 รูปที่ถ่ายต้องเป็น 1 + 1 = 2`).toBe(2);
    expect.soft(rC?.pass, `${tag}(ก) SITE-C D3 ผ่านต้องเป็น 0 + 1 = 1`).toBe(1);
    expect.soft(rateEquals(rC?.pass_rate_text ?? rC?.pass_rate, 50), `${tag}(ก) SITE-C D3 อัตราผ่านต้องเป็น 1 ÷ 2 = 50.00% (ได้ ${rC?.pass_rate_text ?? rC?.pass_rate})`).toBe(true);
    expect.soft(rC?.red, `${tag}(ก) SITE-C D3 ต้องแดง (100 < 180)`).toBe(true);
    const { ctx, page } = await pageFor(browser, c5);
    await openReportUI(page, D3);
    const uiA = await readUiRow(page, 'SITE-C');
    expect.soft(num(uiA.taken), `${tag}(ก) หน้าเว็บ SITE-C รูปที่ถ่ายต้องเป็น 2 (ได้ "${uiA.taken}")`).toBe(2);
    expect.soft(rateEquals(uiA.rate, 50), `${tag}(ก) หน้าเว็บ SITE-C อัตราผ่านต้องเป็น 50.00% (ได้ "${uiA.rate}")`).toBe(true);
    expect.soft(uiA.red, `${tag}(ก) หน้าเว็บ SITE-C data-red ต้องเป็น "true"`).toBe('true');
    await shot(testInfo, page, 'ก-report-D3-SITE-C');
    await ctx.close();
    ev.a = { upload: upA.items.map(i => ({ status: i.status, photoId: i.photoId })), waitMs: wA.elapsedMs, photo: pA && { status: pA.status, h: pA.h, v: pA.v, current_result: pA.current_result, upload_date: pA.upload_date, accepted_at: pA.accepted_at }, api: rC, ui: uiA };

    // (ข) 23:59:59 upload 1 photo, read upload_date (do it immediately: the clock keeps running)
    await reset('2026-11-18T23:59:59+07:00');
    c4 = await login('U4');
    useRealBudget(1, 'TC-4-06 (ข) h0_v0.jpg');
    const upB = await upload(c4, [{ path: fixture('h0_v0.jpg') }]);
    const hB = (await http('GET', '/api/health')).json?.time;
    expect.soft(upB.items[0].status, `${tag}(ข) อัปโหลดต้องได้ 201`).toBe(201);
    const pB = upB.items[0].photoId ? await photo(c4, upB.items[0].photoId) : null;
    expect.soft(pB?.upload_date, `${tag}(ข) upload_date ของรูปที่ 23:59:59 ต้องเป็น ${D3}`).toBe(D3);
    ev.b = { upload: upB.items.map(i => ({ status: i.status, photoId: i.photoId, body: i.json })), healthTimeAfterUpload: hB, photo: pB && { upload_date: pB.upload_date, accepted_at: pB.accepted_at } };

    // (ค) 00:00 of the 19th (= 17:00 UTC of the 18th) upload 1 photo, read upload_date, U-5 opens D3
    await reset('2026-11-19T00:00:00+07:00');
    c4 = await login('U4');
    useRealBudget(1, 'TC-4-06 (ค) h0_v0.jpg');
    const upC = await upload(c4, [{ path: fixture('h0_v0.jpg') }]);
    expect.soft(upC.items[0].status, `${tag}(ค) อัปโหลดต้องได้ 201`).toBe(201);
    const pC = upC.items[0].photoId ? await photo(c4, upC.items[0].photoId) : null;
    expect.soft(pC?.upload_date, `${tag}(ค) upload_date ของรูปที่ 00:00 วันที่ 19 ต้องเป็น 2026-11-19`).toBe('2026-11-19');
    c5 = await login('U5');
    const apiC = await reportApi(c5, D3);
    const rC3 = siteRow(apiC.json, 'SITE-C');
    expect.soft(rC3?.taken, `${tag}(ค) รายงาน D3 SITE-C ต้องเป็น seed เดิม รูปที่ถ่าย 1`).toBe(1);
    const p2 = await pageFor(browser, c5);
    await openReportUI(p2.page, D3);
    const uiC = await readUiRow(p2.page, 'SITE-C');
    expect.soft(num(uiC.taken), `${tag}(ค) หน้าเว็บ D3 SITE-C รูปที่ถ่ายต้องเป็น 1 (ได้ "${uiC.taken}")`).toBe(1);
    await shot(testInfo, p2.page, 'ค-report-D3-SITE-C');
    await p2.ctx.close();
    ev.c = { upload: upC.items.map(i => ({ status: i.status, photoId: i.photoId })), photo: pC && { upload_date: pC.upload_date, accepted_at: pC.accepted_at }, api: rC3, ui: uiC };

    await evidence(testInfo, 'evidence', { expected: { a: { taken: 2, pass: 1, rate: '50.00%', red: true }, b: { upload_date: D3 }, c: { upload_date: '2026-11-19', D3_SITE_C_taken: 1 } }, ...ev });
  });

  test('TC-4-07 [P1] หัวหน้างานแก้ผล failA และเหตุผลว่างต้องถูกปฏิเสธ', async ({ browser }, testInfo) => {
    const tag = 'TC-4-07';
    const REASON = 'คนในรูปถือหมวกอยู่นอกเขตก่อสร้าง';
    const P1edited: Exp = { taken: 300, fail: 19, h: 15, rate: 90.00, red: false, edited: 1, failed: 0 };
    await reset();
    const c2 = await login('U2');
    const c1 = await login('U1');
    const me2 = (await http('GET', '/api/auth/me', { cookie: c2 })).json?.user;
    const failA = await findFailA(c1);
    const ev: any = { failA, steps: [] };

    // step 1: FAIL -> PASS with reason
    const o1 = await override(c2, failA, 'PASS', REASON);
    expect.soft(o1.status, `${tag} ครั้งแรก (แก้เป็น "ผ่าน" พร้อมเหตุผล) ต้องได้ 201`).toBe(201);
    let ph = await photo(c2, failA);
    expect.soft(ph?.current_result, `${tag} ผลล่าสุดต้องเป็น "ผ่าน"`).toBe('PASS');
    expect.soft(ph?.model_result, `${tag} ผลของโมเดลต้องยังเป็น "ไม่ผ่าน"`).toBe('FAIL');
    expect.soft(ph?.is_overridden, `${tag} ต้องมีเครื่องหมายว่าแก้ผลโดยคน`).toBe(true);
    let hs = await history(c2, failA);
    expect.soft(hs.rows.length, `${tag} ประวัติต้องมี 1 แถว`).toBe(1);
    const row = hs.rows[0];
    expect.soft(row?.edited_by?.id, `${tag} ประวัติ: ผู้แก้ต้องเป็น U-2`).toBe(me2?.id);
    expect.soft(Number.isFinite(Date.parse(row?.edited_at)), `${tag} ประวัติ: ต้องมีเวลาที่แก้`).toBe(true);
    expect.soft(row?.result_before, `${tag} ประวัติ: ผลก่อนแก้ต้องเป็น "ไม่ผ่าน"`).toBe('FAIL');
    expect.soft(row?.result_after, `${tag} ประวัติ: ผลหลังแก้ต้องเป็น "ผ่าน"`).toBe('PASS');
    expect.soft(row?.reason, `${tag} ประวัติ: เหตุผลต้องตรงกับที่พิมพ์`).toBe(REASON);
    let rep = await reportApi(c1, D1);
    checkApiRow(rep.json, 'SITE-A', P1edited, `${tag} หลังแก้ครั้งแรก`);
    ev.steps.push({ step: 'PASS+reason', status: o1.status, body: o1.json, photo: ph && { current_result: ph.current_result, model_result: ph.model_result, is_overridden: ph.is_overridden }, history: hs.rows, report: siteRow(rep.json, 'SITE-A') });
    const snap = JSON.stringify(hs.rows.map(five));

    // step 2/3: WARN with "" and "   " -> 422, nothing changes
    for (const reason of ['', '   ']) {
      const o = await override(c2, failA, 'WARN', reason);
      const lbl = reason === '' ? 'เหตุผลว่าง ""' : 'เหตุผลช่องว่าง "   "';
      expect.soft(o.status, `${tag} แก้เป็น "เตือน" ด้วย${lbl} ต้องได้ 422`).toBe(422);
      hs = await history(c2, failA);
      expect.soft(hs.rows.length, `${tag} หลัง${lbl} ประวัติต้องยังมี 1 แถว`).toBe(1);
      expect.soft(JSON.stringify(hs.rows.map(five)), `${tag} หลัง${lbl} ประวัติต้องไม่เปลี่ยน`).toBe(snap);
      ph = await photo(c2, failA);
      expect.soft(ph?.current_result, `${tag} หลัง${lbl} ผลล่าสุดต้องยังเป็น "ผ่าน"`).toBe('PASS');
      rep = await reportApi(c1, D1);
      checkApiRow(rep.json, 'SITE-A', P1edited, `${tag} หลัง${lbl}`);
      ev.steps.push({ step: `WARN ${JSON.stringify(reason)}`, status: o.status, body: o.json, historyRows: hs.rows.length, current: ph?.current_result, report: siteRow(rep.json, 'SITE-A') });
    }

    // UI: detail page as U-2 + report D1 as U-1
    const a = await pageFor(browser, c2);
    await a.page.goto(UI + `/photos/${failA}`);
    await expect.soft(a.page.getByTestId('photo-current-result'), `${tag} หน้ารายละเอียด: ผลล่าสุดต้องแสดง "${RESULT_TH.PASS}"`).toHaveText(RESULT_TH.PASS);
    await expect.soft(a.page.getByTestId('photo-model-result'), `${tag} หน้ารายละเอียด: ผลของโมเดลต้องแสดง "${RESULT_TH.FAIL}"`).toHaveText(RESULT_TH.FAIL);
    await expect.soft(a.page.getByTestId('photo-edited-badge'), `${tag} หน้ารายละเอียด: ต้องมีป้าย "แก้ผลโดยคน"`).toContainText('แก้ผลโดยคน');
    await a.page.getByTestId('history-toggle').click().catch(() => { });
    const hrows = a.page.locator('[data-testid^="history-row-"]');
    await expect.soft(hrows, `${tag} หน้ารายละเอียด: ประวัติต้องมี 1 แถว`).toHaveCount(1);
    if (await hrows.count()) {
      const txt = (await hrows.first().textContent()) || '';
      expect.soft(txt, `${tag} แถวประวัติต้องมีชื่อผู้แก้ U-2`).toContain(me2?.full_name ?? 'U-2');
      expect.soft(txt, `${tag} แถวประวัติต้องมีเหตุผลที่พิมพ์`).toContain(REASON);
      expect.soft(txt, `${tag} แถวประวัติต้องมีผลก่อน "ไม่ผ่าน"`).toContain(RESULT_TH.FAIL);
    }
    await shot(testInfo, a.page, 'photo-failA-detail');
    await a.ctx.close();
    const b = await pageFor(browser, c1);
    await openReportUI(b.page, D1);
    const ui = await checkUiRow(b.page, 'SITE-A', P1edited, `${tag} หน้าเว็บรายงาน D1`);
    await shot(testInfo, b.page, 'report-D1');
    await b.ctx.close();
    await evidence(testInfo, 'evidence', { expected: { first: 201, history: 1, report: P1edited, emptyReasons: 422 }, ...ev, uiReport: ui });
  });

  test('TC-4-08 [P2] แก้ผลซ้ำหลายครั้ง ประวัติลบ/แก้ไม่ได้ และผู้จัดการดูประวัติข้ามไซต์', async ({ browser }, testInfo) => {
    const tag = 'TC-4-08';
    const R1 = 'มีคนไม่ใส่หมวกอยู่หลังเสา', R2 = 'ตรวจซ้ำ คนหลังเสาใส่หมวก แต่ไม่ใส่เสื้อ', R3 = 'ยืนยัน';
    await reset();
    const c1 = await login('U1');
    const c2 = await login('U2');
    const c5 = await login('U5');
    const passC = await findPassC(c1);
    const failA = await findFailA(c1);
    const ev: any = { passC, failA, steps: [] };
    const repC = async () => siteRow((await reportApi(c1, D1)).json, 'SITE-C');
    const checkRep = (r: any, t: string, failN: number) => {
      expect.soft(rateEquals(r?.pass_rate_text ?? r?.pass_rate, 90), `${t} รายงาน D1 SITE-C อัตราผ่านต้องเป็น 270 ÷ 300 = 90.00% (ได้ ${r?.pass_rate_text ?? r?.pass_rate})`).toBe(true);
      expect.soft(r?.pass, `${t} รายงาน D1 SITE-C ผ่านต้องเป็น 270`).toBe(270);
      expect.soft(r?.red, `${t} รายงาน D1 SITE-C ต้องไม่แดง`).toBe(false);
      expect.soft(r?.fail, `${t} รายงาน D1 SITE-C ไม่ผ่านต้องเป็น ${failN}`).toBe(failN);
      expect.soft(r?.edited, `${t} รายงาน D1 SITE-C ถูกแก้ผลต้องเป็น 1 (นับเป็นรูป)`).toBe(1);
    };

    // 1) PASS -> FAIL
    const o1 = await override(c1, passC, 'FAIL', R1);
    expect.soft(o1.status, `${tag} ครั้งที่ 1 (เป็น "ไม่ผ่าน") ต้องได้ 201`).toBe(201);
    let r = await repC(); checkRep(r, `${tag} หลังครั้งที่ 1`, 21);
    let hs = await history(c1, passC);
    expect.soft(hs.rows.length, `${tag} หลังครั้งที่ 1 ประวัติต้องมี 1 แถว`).toBe(1);
    ev.steps.push({ step: 1, status: o1.status, report: r, history: hs.rows });

    // 2) FAIL -> WARN
    const o2 = await override(c1, passC, 'WARN', R2);
    expect.soft(o2.status, `${tag} ครั้งที่ 2 (เป็น "เตือน") ต้องได้ 201`).toBe(201);
    r = await repC(); checkRep(r, `${tag} หลังครั้งที่ 2`, 20);
    hs = await history(c1, passC);
    expect.soft(hs.rows.length, `${tag} หลังครั้งที่ 2 ประวัติต้องมี 2 แถว`).toBe(2);
    expect.soft(hs.rows[1]?.result_before, `${tag} แถวที่ 2 "ผลก่อนแก้" ต้องเป็น "ไม่ผ่าน"`).toBe('FAIL');
    expect.soft(hs.rows[1]?.result_after, `${tag} แถวที่ 2 "ผลหลังแก้" ต้องเป็น "เตือน"`).toBe('WARN');
    expect.soft(hs.rows[0]?.reason, `${tag} แถวที่ 1 เหตุผลต้องตรงกับที่พิมพ์`).toBe(R1);
    expect.soft(hs.rows[1]?.reason, `${tag} แถวที่ 2 เหตุผลต้องตรงกับที่พิมพ์`).toBe(R2);
    ev.steps.push({ step: 2, status: o2.status, report: r, history: hs.rows });
    const snap = JSON.stringify(hs.rows.map(five));

    // 3) WARN again -> 422 (same as current result)
    const o3 = await override(c1, passC, 'WARN', R3);
    expect.soft(o3.status, `${tag} ครั้งที่ 3 (เตือนซ้ำ) ต้องได้ 422 เพราะผลซ้ำ`).toBe(422);
    hs = await history(c1, passC);
    expect.soft(hs.rows.length, `${tag} หลังครั้งที่ 3 ประวัติต้องยังมี 2 แถว`).toBe(2);
    expect.soft(JSON.stringify(hs.rows.map(five)), `${tag} หลังครั้งที่ 3 ประวัติต้องไม่เปลี่ยน`).toBe(snap);
    r = await repC(); checkRep(r, `${tag} หลังครั้งที่ 3`, 20);
    ev.steps.push({ step: 3, status: o3.status, body: o3.json, report: r, historyRows: hs.rows.length });

    // 4) DELETE / PUT by U-1, U-2, U-5 -> never succeeds, history unchanged
    const who: [UserKey, string][] = [['U1', c1], ['U2', c2], ['U5', c5]];
    for (const [u, c] of who) {
      for (const m of ['DELETE', 'PUT']) {
        const opts: any = { cookie: c };
        if (m === 'PUT') opts.json = { result: 'PASS', reason: 'ลองแก้ประวัติ' };
        const res = await http(m, `/api/photos/${passC}/overrides`, opts);
        expect.soft([405, 403, 404].includes(res.status), `${tag} ${m} โดย ${u} ต้องไม่สำเร็จ (405 หรือ 403/404) ได้ ${res.status}`).toBe(true);
        hs = await history(c1, passC);
        expect.soft(hs.rows.length, `${tag} หลัง ${m} โดย ${u} ประวัติต้องยังมี 2 แถว`).toBe(2);
        expect.soft(JSON.stringify(hs.rows.map(five)), `${tag} หลัง ${m} โดย ${u} ประวัติ 5 ช่องต้องค่าเดิม`).toBe(snap);
        r = await repC(); checkRep(r, `${tag} หลัง ${m} โดย ${u}`, 20);
        ev.steps.push({ step: `${m} ${u}`, status: res.status, historyRows: hs.rows.length, report: r });
      }
    }

    // 5) Detail page has no delete / edit-history button
    const a = await pageFor(browser, c1);
    await a.page.goto(UI + `/photos/${passC}`);
    await a.page.getByTestId('history-toggle').click().catch(() => { });
    const hrows = a.page.locator('[data-testid^="history-row-"]');
    await expect.soft(hrows, `${tag} หน้ารายละเอียด passC: ประวัติต้องแสดง 2 แถว`).toHaveCount(2);
    const controls = await a.page.evaluate(() => [...document.querySelectorAll('button, a, [role=button], input[type=button], input[type=submit]')]
      .map(e => ({ id: e.getAttribute('data-testid') || '', text: (e.textContent || (e as HTMLInputElement).value || '').trim() })));
    const bad = controls.filter(c => /history-(delete|edit|remove)|override-(delete|edit|remove)/i.test(c.id) || /ลบ|แก้ไขประวัติ|แก้ประวัติ|delete|remove/i.test(c.text));
    expect.soft(bad, `${tag} หน้ารายละเอียดต้องไม่มีปุ่มลบ/แก้ประวัติ`).toEqual([]);
    const inRow = await hrows.locator('button, a, input').count();
    expect.soft(inRow, `${tag} แถวประวัติต้องไม่มีปุ่มหรือลิงก์ใด ๆ`).toBe(0);
    await shot(testInfo, a.page, 'photo-passC-history');

    // 6) U-1 opens the history of {failA} (SITE-A) — cross-site for manager
    const hA = await history(c1, failA);
    expect.soft(hA.status, `${tag} U-1 เปิดประวัติ failA ของ SITE-A ต้องได้ 200`).toBe(200);
    await a.page.goto(UI + `/photos/${failA}`);
    await expect.soft(a.page.getByTestId('history-toggle'), `${tag} U-1 หน้ารายละเอียด failA ต้องมีปุ่มเปิดประวัติ`).toBeVisible();
    await a.page.getByTestId('history-toggle').click().catch(() => { });
    await shot(testInfo, a.page, 'photo-failA-history-U1');
    await a.ctx.close();

    const b = await pageFor(browser, c1);
    await openReportUI(b.page, D1);
    const ui = await checkUiRow(b.page, 'SITE-C', { taken: 300, fail: 20, h: 20, rate: 90.00, red: false, edited: 1, failed: 0 }, `${tag} หน้าเว็บรายงาน D1 สุดท้าย`);
    await shot(testInfo, b.page, 'report-D1');
    await b.ctx.close();
    await evidence(testInfo, 'evidence', { expected: { s1: '201 fail 21 edited 1 rate 90.00', s2: '201 fail 20 history 2 row2 before FAIL', s3: 422, deletePut: '405/403/404 history unchanged' }, ...ev, controls, failAHistory: { status: hA.status, json: hA.json }, uiReport: ui });
  });
});
