// Test Plan 5.5 · สิทธิ์ของแต่ละบทบาท (FR-18–FR-22 · NFR-05 · NFR-06) · TC-5-01 … TC-5-09
// ค่าที่คาดหวังมาจาก test/TEST-PLAN.md 5.5 และ docs/TEST-DATA.md หัวข้อ 1–3, 8 เท่านั้น
// กลุ่มนี้ต้องการเพียงให้เว็บ "เก็บ" รูป {batchB} ไม่ต้องตรวจ → หยุด dispatcher ตลอดไฟล์ (noGpuForThisFile)
// ไม่แตะฐานข้อมูล: "result_overrides +0" / "upload_batches +0" ตรวจทางอ้อมผ่าน API (ประวัติการแก้ผล ผลล่าสุด ไม่มี batch_id)
import { test, expect, type Browser, type BrowserContext, type Page } from '@playwright/test';
import { execSync, execFileSync } from 'node:child_process';
import {
  UI, USERS, WEB_CONTAINER, DISPATCHER_CONTAINER, http, reset, login, cookieToContext, fixture, upload,
  noGpuForThisFile, gatewayKey, evidence, shot, type Res, type UserKey,
} from './helpers';

const D1 = '2026-11-16';

// ---------------- helpers เฉพาะไฟล์นี้ ----------------

/** ขั้นเตรียม "ก่อนเริ่ม" ของ 5.5: {photoB} จาก U-1 (ยืนยัน SITE-B) และ {batchB} จาก U-3 อัปโหลด h0_v0.jpg */
async function prep(opts: { batch: boolean }) {
  const c1 = await login('U1');
  const list = await http('GET', `/api/photos?date=${D1}&site=SITE-B`, { cookie: c1 });
  expect(list.status, 'เตรียม: U-1 ดึงรายการรูป SITE-B วันที่ 2026-11-16 ต้องได้ 200').toBe(200);
  const p = list.json?.photos?.[0];
  expect(p?.site?.code, 'เตรียม: {photoB} ต้องเป็นรูปของ SITE-B').toBe('SITE-B');
  const photoB = p.id as string;
  let batchB = '';
  let batchUpload: any = null;
  if (opts.batch) {
    const c3 = await login('U3');
    const up = await upload(c3, [{ path: fixture('h0_v0.jpg') }]);
    batchB = up.batchId;
    batchUpload = { batchStatus: 201, fileStatus: up.items[0].status };
    expect(up.items[0].status, 'เตรียม: U-3 ส่ง h0_v0.jpg ต้องได้ 201').toBe(201);
  }
  return { c1, photoB, batchB, prepEvidence: { photoB, photoB_site: p.site.code, batchB: batchB || null, batchUpload } };
}

/** สรุปว่าคำตอบมีข้อมูลรูป ผล หรือไบต์รูปหรือไม่ (ไม่เก็บเนื้อหาคำตอบ) */
const DATA_KEYS = ['photos', 'photo', 'overrides', 'detections', 'current_result', 'model_result', 'image_url', 'original_filename', 'batch_id', 'email', 'sites'];
function leak(r: Res) {
  const ct = r.headers.get('content-type') || '';
  const b = r.bytes;
  const isImage = ct.startsWith('image/')
    || (b.length >= 3 && b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff)
    || (b.length >= 4 && b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47);
  const dataKeys = DATA_KEYS.filter(k => r.text.includes(`"${k}"`));
  return { status: r.status, contentType: ct, bytes: b.length, isImage, dataKeys, error: r.json?.error ?? null };
}

async function ctxAs(browser: Browser, user?: UserKey, cookie?: string): Promise<{ ctx: BrowserContext; page: Page; cookie?: string }> {
  const ctx = await browser.newContext({ baseURL: UI });
  let c = cookie;
  if (user && !c) c = await login(user);
  if (c) await cookieToContext(ctx, c);
  const page = await ctx.newPage();
  return { ctx, page, cookie: c };
}

/** อ่านประวัติการแก้ผลและผลล่าสุดของรูปด้วย U-1 (ใช้แทนการนับแถว result_overrides) */
async function photoState(c1: string, id: string) {
  const ov = await http('GET', `/api/photos/${id}/overrides`, { cookie: c1 });
  const d = await http('GET', `/api/photos/${id}`, { cookie: c1 });
  return {
    overridesStatus: ov.status, overrides: (ov.json?.overrides || []).length as number,
    detailStatus: d.status, current_result: d.json?.photo?.current_result ?? null, is_overridden: d.json?.photo?.is_overridden ?? null,
  };
}

function siteRows(r: Res): any[] { return (r.json?.sites || []) as any[]; }

/** ค่าตาม TC-4-01 (P-1, P-2, P-3): taken / fail / H รวม / อัตราผ่าน / แดง / ถูกแก้ผล / ตรวจไม่สำเร็จ */
const D1_EXPECT: Record<string, { taken: number; fail: number; h: number; rate: string; red: boolean; edited: number; failed: number }> = {
  'SITE-A': { taken: 300, fail: 20, h: 15, rate: '89.67', red: true, edited: 0, failed: 0 },
  'SITE-B': { taken: 300, fail: 20, h: 20, rate: '90.00', red: false, edited: 0, failed: 0 },
  'SITE-C': { taken: 300, fail: 20, h: 20, rate: '90.33', red: false, edited: 0, failed: 0 },
};
function checkRow(who: string, row: any, code: string) {
  const e = D1_EXPECT[code];
  expect.soft(row?.taken, `${who} ${code}: รูปที่ถ่ายต้องเป็น ${e.taken}`).toBe(e.taken);
  expect.soft(row?.fail, `${who} ${code}: รูปไม่ผ่านต้องเป็น ${e.fail}`).toBe(e.fail);
  expect.soft(row?.h_total, `${who} ${code}: คนไม่ใส่หมวก (H รวม) ต้องเป็น ${e.h}`).toBe(e.h);
  expect.soft(row?.pass_rate_text, `${who} ${code}: อัตราผ่านต้องเป็น ${e.rate}%`).toBe(e.rate);
  expect.soft(row?.red, `${who} ${code}: สีแดงต้องเป็น ${e.red}`).toBe(e.red);
  expect.soft(row?.edited, `${who} ${code}: ถูกแก้ผลต้องเป็น ${e.edited}`).toBe(e.edited);
  expect.soft(row?.failed, `${who} ${code}: ตรวจไม่สำเร็จต้องเป็น ${e.failed}`).toBe(e.failed);
}

function countIn(text: string, key: string) { return key ? text.split(key).length - 1 : 0; }

test.describe('5.5 สิทธิ์ของแต่ละบทบาท', () => {
  noGpuForThisFile();

  test('TC-5-01 [P1] ไม่ล็อกอิน เปิดหน้าและเรียก API ไม่ได้', async ({ browser }, testInfo) => {
    await reset();
    const { photoB, batchB, prepEvidence } = await prep({ batch: true });

    const { ctx, page } = await ctxAs(browser); // บริบทใหม่ ไม่มี cookie
    const pages = ['/upload', `/uploads/${batchB}`, '/photos', '/photos/problems', `/photos/${photoB}`, '/reports/daily'];
    const pageRes: any[] = [];
    for (const p of pages) {
      await page.goto(UI + p);
      await page.waitForLoadState('domcontentloaded');
      const landed = new URL(page.url()).pathname;
      const imgShown = await page.getByTestId('photo-image').count();
      pageRes.push({ page: p, landed, photoImage: imgShown });
      expect.soft(landed, `หน้า ${p} เมื่อไม่ล็อกอินต้องถูกส่งไป /login`).toBe('/login');
      expect.soft(imgShown, `หน้า ${p} เมื่อไม่ล็อกอินต้องไม่แสดงรูป`).toBe(0);
    }
    const openWithoutLogin = pageRes.filter(r => r.landed !== '/login').length;
    expect.soft(openWithoutLogin, 'หน้าที่เปิดได้โดยไม่ล็อกอิน (นอกจาก /login) ต้องเป็น 0').toBe(0);
    await shot(testInfo, page, 'TC-5-01 หน้าที่ถูกส่งไป login');
    await ctx.close();

    const apis = ['/api/photos', `/api/photos/${photoB}`, `/api/photos/${photoB}/image`, `/api/uploads/${batchB}`, `/api/reports/daily?date=${D1}`, '/api/auth/me'];
    const apiRes: any[] = [];
    for (const a of apis) {
      const r = await http('GET', a);
      const l = leak(r);
      apiRes.push({ api: a, ...l });
      expect.soft(r.status, `GET ${a} ไม่มี cookie ต้องได้ 401`).toBe(401);
      expect.soft(l.isImage, `GET ${a} ไม่มี cookie ต้องไม่มีไบต์รูป`).toBe(false);
      expect.soft(l.dataKeys, `GET ${a} ไม่มี cookie ต้องไม่มีข้อมูลรูป ผล หรือผู้ใช้`).toEqual([]);
    }
    await evidence(testInfo, 'evidence', {
      prep: prepEvidence,
      statuses: Object.fromEntries(apiRes.map(r => [r.api.replace(photoB, '{photoB}').replace(batchB, '{batchB}'), r.status])),
      pages: pageRes.map(r => ({ ...r, page: r.page.replace(photoB, '{photoB}').replace(batchB, '{batchB}') })),
      pagesRedirectedToLogin: `${pageRes.length - openWithoutLogin} / ${pageRes.length}`,
      api401: `${apiRes.filter(r => r.status === 401).length} / ${apiRes.length}`,
      apiLeak: apiRes.map(r => ({ api: r.api.replace(photoB, '{photoB}').replace(batchB, '{batchB}'), isImage: r.isImage, dataKeys: r.dataKeys, contentType: r.contentType })),
    });
  });

  test('TC-5-02 [P2] ล็อกอินผิด ข้อความเดียวกัน ไม่มี session cookie', async ({ browser }, testInfo) => {
    await reset();
    const cases = [
      { name: '(ก) อีเมล U-2 + wrong-password', email: USERS.U2.email, password: 'wrong-password' },
      { name: '(ข) nobody@sitesafe.test + Test-SupA-01', email: 'nobody@sitesafe.test', password: 'Test-SupA-01' },
    ];
    const out: any[] = [];
    for (const [i, c] of cases.entries()) {
      // API
      const r = await http('POST', '/api/auth/login', { json: { email: c.email, password: c.password } });
      const sc = r.headers.get('set-cookie') || '';
      // UI (บริบทใหม่ ไม่มี session)
      const { ctx, page } = await ctxAs(browser);
      await page.goto(UI + '/login');
      await page.getByTestId('login-email').fill(c.email);
      await page.getByTestId('login-password').fill(c.password);
      const respP = page.waitForResponse(x => x.url().includes('/api/auth/login'), { timeout: 15000 }).catch(() => null);
      await page.getByTestId('login-submit').click();
      const resp = await respP;
      const uiStatus = resp ? resp.status() : null;
      const uiSetCookie = resp ? ((await resp.headerValue('set-cookie')) || '') : '';
      await expect.soft(page.getByTestId('login-error'), `${c.name}: ต้องแสดง login-error`).toBeVisible();
      const errText = ((await page.getByTestId('login-error').textContent().catch(() => '')) || '').trim();
      const ctxCookies = (await ctx.cookies()).filter(k => k.name === 'sitesafe_session').length;
      const landed = new URL(page.url()).pathname;
      await shot(testInfo, page, `TC-5-02 ${i === 0 ? 'ก' : 'ข'} login-error`);
      await ctx.close();

      expect.soft(r.status, `${c.name}: API ต้องได้ 401`).toBe(401);
      expect.soft(/sitesafe_session=/.test(sc), `${c.name}: API ต้องไม่มี Set-Cookie ของ session`).toBe(false);
      if (uiStatus !== null) expect.soft(uiStatus, `${c.name}: คำขอล็อกอินจากหน้าเว็บต้องได้ 401`).toBe(401);
      expect.soft(/sitesafe_session=/.test(uiSetCookie), `${c.name}: หน้าเว็บต้องไม่ได้ Set-Cookie ของ session`).toBe(false);
      expect.soft(ctxCookies, `${c.name}: เบราว์เซอร์ต้องไม่มี cookie sitesafe_session`).toBe(0);
      expect.soft(landed, `${c.name}: ต้องยังอยู่ที่ /login`).toBe('/login');
      out.push({ case: c.name, apiStatus: r.status, apiSessionSetCookie: /sitesafe_session=/.test(sc), apiMessage: r.json?.message ?? null, uiLoginStatus: uiStatus, uiSessionSetCookie: /sitesafe_session=/.test(uiSetCookie), browserSessionCookies: ctxCookies, loginError: errText, landed });
    }
    expect.soft(out[0].loginError.length > 0, 'ข้อความ login-error ต้องไม่ว่าง').toBe(true);
    expect.soft(out[1].loginError, 'ข้อความ login-error ต้องเหมือนกันทั้งสองกรณี').toBe(out[0].loginError);
    expect.soft(out[1].apiMessage, 'ข้อความจาก API ต้องเหมือนกันทั้งสองกรณี').toBe(out[0].apiMessage);
    await evidence(testInfo, 'evidence', {
      statuses: { 'ก API': out[0].apiStatus, 'ข API': out[1].apiStatus, 'ก UI': out[0].uiLoginStatus, 'ข UI': out[1].uiLoginStatus },
      cases: out, sameLoginError: out[0].loginError === out[1].loginError,
    });
  });

  test('TC-5-03 [P1] หัวหน้างานไซต์ ก เปิดรูปและงานของไซต์ ข ไม่ได้', async ({ browser }, testInfo) => {
    await reset();
    const { photoB, batchB, prepEvidence } = await prep({ batch: true });
    const { ctx, page, cookie: c2 } = await ctxAs(browser, 'U2');

    const pr = await page.goto(UI + `/photos/${photoB}`);
    await page.waitForLoadState('domcontentloaded');
    const pageStatus = pr ? pr.status() : null;
    const pageImg = await page.getByTestId('photo-image').count();
    await shot(testInfo, page, 'TC-5-03 U-2 เปิด /photos/{photoB}');
    await ctx.close();

    const single: Record<string, Res> = {
      'GET /api/photos/{photoB}': await http('GET', `/api/photos/${photoB}`, { cookie: c2 }),
      'GET /api/photos/{photoB}/image': await http('GET', `/api/photos/${photoB}/image`, { cookie: c2 }),
      'GET /api/photos/{photoB}/overrides': await http('GET', `/api/photos/${photoB}/overrides`, { cookie: c2 }),
      'GET /api/uploads/{batchB}': await http('GET', `/api/uploads/${batchB}`, { cookie: c2 }),
    };
    const statuses: Record<string, number | null> = { 'page /photos/{photoB}': pageStatus };
    expect.soft(pageStatus, 'U-2 เปิดหน้า /photos/{photoB} ต้องได้ 404').toBe(404);
    expect.soft(pageImg, 'U-2 หน้า /photos/{photoB} ต้องไม่แสดงรูป').toBe(0);
    const leaks: any = {};
    for (const [k, r] of Object.entries(single)) {
      statuses[k] = r.status; leaks[k] = leak(r);
      expect.soft(r.status, `U-2 ${k} ต้องได้ 404`).toBe(404);
      expect.soft(leaks[k].isImage, `U-2 ${k} ต้องไม่มีไบต์รูป`).toBe(false);
      expect.soft(leaks[k].dataKeys, `U-2 ${k} ต้องไม่มีข้อมูลรูปหรือผล`).toEqual([]);
    }
    const successes = Object.values(statuses).filter(s => s !== null && s >= 200 && s < 300).length;
    expect.soft(successes, 'คำขอรายตัว 5 รายการต้องสำเร็จ 0 ครั้ง').toBe(0);

    const lists = {
      'GET /api/photos?site=SITE-B&date=2026-11-16': await http('GET', `/api/photos?site=SITE-B&date=${D1}`, { cookie: c2 }),
      'GET /api/photos?problems=1&site=SITE-B&date=2026-11-16': await http('GET', `/api/photos?problems=1&site=SITE-B&date=${D1}`, { cookie: c2 }),
    };
    const listOut: any = {};
    for (const [k, r] of Object.entries(lists)) {
      const ph = (r.json?.photos || []) as any[];
      const notA = ph.filter(p => p?.site?.code !== 'SITE-A').length;
      const ofB = ph.filter(p => p?.site?.code === 'SITE-B').length;
      statuses[k] = r.status;
      listOut[k] = { status: r.status, returned: ph.length, total: r.json?.total ?? null, notSiteA: notA, siteB: ofB, mentionsPhotoB: r.text.includes(photoB) };
      expect.soft(r.status === 401 || r.status >= 500, `U-2 ${k} ต้องตอบโดยไม่ผิดพลาด (ได้ ${r.status})`).toBe(false);
      expect.soft(notA, `U-2 ${k}: รูปที่ไซต์ไม่ใช่ SITE-A ต้องเป็น 0`).toBe(0);
      expect.soft(ofB, `U-2 ${k}: รูปของ SITE-B ต้องเป็น 0`).toBe(0);
      expect.soft(listOut[k].mentionsPhotoB, `U-2 ${k}: ต้องไม่มีรหัส {photoB}`).toBe(false);
    }
    await evidence(testInfo, 'evidence', { prep: prepEvidence, statuses, singleSuccesses: successes, leaks, lists: listOut, pagePhotoImage: pageImg });
  });

  test('TC-5-04 [P1] หัวหน้างานไซต์ ก แก้ผลรูปไซต์ ข ไม่ได้', async ({ browser }, testInfo) => {
    await reset();
    const { c1, photoB, prepEvidence } = await prep({ batch: false });
    const before = await photoState(c1, photoB);
    const c2 = await login('U2');
    const r = await http('POST', `/api/photos/${photoB}/overrides`, { cookie: c2, json: { result: 'PASS', reason: 'ทดสอบสิทธิ์' } });
    const after = await photoState(c1, photoB);
    const rep = await http('GET', `/api/reports/daily?date=${D1}`, { cookie: c1 });
    const rowB = siteRows(rep).find(s => s?.site?.code === 'SITE-B');

    expect.soft(r.status, 'U-2 POST overrides ของ {photoB} ต้องได้ 404').toBe(404);
    expect.soft(leak(r).dataKeys, 'คำตอบ 404 ต้องไม่มีข้อมูลรูปหรือผล').toEqual([]);
    expect.soft(after.overrides, 'ประวัติการแก้ผลของ {photoB} ต้องไม่เพิ่ม (result_overrides +0 ทางอ้อม)').toBe(before.overrides);
    expect.soft(after.current_result, 'ผลล่าสุดของ {photoB} ต้องไม่เปลี่ยน').toBe(before.current_result);
    expect.soft(after.is_overridden, 'สถานะ "แก้ผลโดยคน" ของ {photoB} ต้องไม่เปลี่ยน').toBe(before.is_overridden);
    expect.soft(rowB?.edited, 'รายงาน D1 SITE-B ถูกแก้ผลต้องยังเป็น 0 (P-2)').toBe(0);

    const { ctx, page } = await ctxAs(browser, undefined, c1);
    await page.goto(UI + `/photos/${photoB}`);
    await page.getByTestId('photo-current-result').waitFor({ timeout: 15000 }).catch(() => { });
    await shot(testInfo, page, 'TC-5-04 U-1 เห็นผลล่าสุดของ {photoB} หลังคำขอของ U-2');
    await ctx.close();
    await evidence(testInfo, 'evidence', {
      prep: prepEvidence,
      statuses: { 'U-2 POST /api/photos/{photoB}/overrides': r.status, 'U-1 GET overrides (หลัง)': after.overridesStatus, 'U-1 GET report D1': rep.status },
      response: leak(r),
      indirect: 'ไม่เข้าถึงฐานข้อมูล: ใช้ประวัติ GET /api/photos/{photoB}/overrides ของ U-1 ก่อน/หลัง + current_result + is_overridden + รายงาน D1 SITE-B edited แทนการนับ result_overrides',
      before, after, reportSiteB_edited: rowB?.edited ?? null,
    });
  });

  test('TC-5-05 [P1] รายงานตามบทบาท และผู้จัดการเปิดรูปได้ทุกไซต์', async ({ browser }, testInfo) => {
    await reset();
    const { prepEvidence } = await prep({ batch: false });
    const c2 = await login('U2');
    const c1 = await login('U1');
    const statuses: Record<string, number> = {};
    const reports: any = {};

    for (const [who, c] of [['U-2', c2], ['U-1', c1]] as const) {
      for (const q of [`date=${D1}`, `date=${D1}&site=SITE-B`]) {
        const r = await http('GET', `/api/reports/daily?${q}`, { cookie: c });
        const rows = siteRows(r);
        const key = `${who} GET /api/reports/daily?${q}`;
        statuses[key] = r.status;
        reports[key] = rows.map(s => ({ code: s?.site?.code, taken: s.taken, fail: s.fail, h_total: s.h_total, pass_rate_text: s.pass_rate_text, red: s.red, edited: s.edited, failed: s.failed }));
        expect.soft(r.status, `${key} ต้องได้ 200`).toBe(200);
        if (who === 'U-2') {
          expect.soft(rows.length, `${key}: ต้องมี 1 แถว`).toBe(1);
          expect.soft(rows.map(s => s?.site?.code), `${key}: แถวเดียวต้องเป็น SITE-A`).toEqual(['SITE-A']);
          checkRow(key, rows.find(s => s?.site?.code === 'SITE-A'), 'SITE-A');
        } else {
          expect.soft(rows.length, `${key}: ต้องมี 3 แถว`).toBe(3);
          expect.soft(rows.map(s => s?.site?.code).sort(), `${key}: ต้องมี SITE-A, SITE-B, SITE-C`).toEqual(['SITE-A', 'SITE-B', 'SITE-C']);
          for (const code of ['SITE-A', 'SITE-B', 'SITE-C']) checkRow(key, rows.find(s => s?.site?.code === code), code);
        }
      }
    }

    // หน้ารายงานของ U-2 (เห็นเฉพาะ SITE-A) และของ U-1
    const u2 = await ctxAs(browser, undefined, c2);
    await u2.page.goto(UI + `/reports/daily?date=${D1}`);
    await u2.page.getByTestId('report-row-SITE-A').waitFor({ timeout: 15000 }).catch(() => { });
    const u2Rows = { A: await u2.page.getByTestId('report-row-SITE-A').count(), B: await u2.page.getByTestId('report-row-SITE-B').count(), C: await u2.page.getByTestId('report-row-SITE-C').count() };
    expect.soft(u2Rows.A, 'หน้ารายงาน U-2: ต้องมีแถว SITE-A').toBe(1);
    expect.soft(u2Rows.B + u2Rows.C, 'หน้ารายงาน U-2: ต้องไม่มีแถว SITE-B / SITE-C').toBe(0);
    await shot(testInfo, u2.page, 'TC-5-05 หน้ารายงาน D1 ของ U-2');
    await u2.ctx.close();

    const u1 = await ctxAs(browser, undefined, c1);
    await u1.page.goto(UI + `/reports/daily?date=${D1}`);
    await u1.page.getByTestId('report-row-SITE-C').waitFor({ timeout: 15000 }).catch(() => { });
    const u1Red: any = {};
    for (const code of ['SITE-A', 'SITE-B', 'SITE-C']) {
      u1Red[code] = await u1.page.getByTestId(`report-red-${code}`).getAttribute('data-red').catch(() => null);
      expect.soft(u1Red[code], `หน้ารายงาน U-1 ${code}: data-red ต้องเป็น ${D1_EXPECT[code].red}`).toBe(String(D1_EXPECT[code].red));
    }
    await shot(testInfo, u1.page, 'TC-5-05 หน้ารายงาน D1 ของ U-1');

    // U-1 เปิดรูปและไฟล์รูป 1 รูปจากแต่ละไซต์
    const photoOpen: any[] = [];
    for (const code of ['SITE-A', 'SITE-B', 'SITE-C']) {
      const l = await http('GET', `/api/photos?date=${D1}&site=${code}`, { cookie: c1 });
      const p = l.json?.photos?.[0];
      expect.soft(p?.site?.code, `U-1 รายการ ${code}: รูปแรกต้องเป็นของ ${code}`).toBe(code);
      const id = p?.id as string;
      const pr = await u1.page.goto(UI + `/photos/${id}`);
      await u1.page.getByTestId('photo-image').waitFor({ timeout: 15000 }).catch(() => { });
      const pageStatus = pr ? pr.status() : null;
      const img = await http('GET', `/api/photos/${id}/image`, { cookie: c1 });
      const ok = pageStatus === 200 && img.status === 200 && leak(img).isImage;
      photoOpen.push({ site: code, id, pageStatus, photoImage: await u1.page.getByTestId('photo-image').count(), imageStatus: img.status, imageType: img.headers.get('content-type'), imageBytes: img.bytes.length, ok });
      statuses[`U-1 page /photos/{${code}}`] = pageStatus ?? 0;
      statuses[`U-1 GET /api/photos/{${code}}/image`] = img.status;
      expect.soft(pageStatus, `U-1 เปิดหน้ารูปของ ${code} ต้องได้ 200`).toBe(200);
      expect.soft(img.status, `U-1 GET /image ของ ${code} ต้องได้ 200`).toBe(200);
      expect.soft(leak(img).isImage, `U-1 GET /image ของ ${code} ต้องได้ไบต์รูป`).toBe(true);
      if (code === 'SITE-B') await shot(testInfo, u1.page, 'TC-5-05 U-1 เปิดรูปของ SITE-B');
    }
    const okCount = photoOpen.filter(p => p.ok).length;
    expect.soft(okCount, 'U-1 เปิดรูปและไฟล์รูปได้ 3 / 3 ไซต์').toBe(3);
    await u1.ctx.close();
    await evidence(testInfo, 'evidence', { prep: prepEvidence, statuses, reports, u2PageRows: u2Rows, u1PageDataRed: u1Red, photoOpen, managerOpened: `${okCount} / 3` });
  });

  test('TC-5-06 [P1] ผู้บริหารอัปโหลดและแก้ผลไม่ได้ แต่เปิดรายงานได้', async ({ browser }, testInfo) => {
    await reset();
    const { c1, photoB, prepEvidence } = await prep({ batch: false });
    const before = await photoState(c1, photoB);
    const c5 = await login('U5');

    const up = await http('POST', '/api/uploads', { cookie: c5, json: { count: 1 } });
    const ov = await http('POST', `/api/photos/${photoB}/overrides`, { cookie: c5, json: { result: 'PASS', reason: 'x' } });
    const after = await photoState(c1, photoB);
    const rep = await http('GET', `/api/reports/daily?date=${D1}`, { cookie: c5 });

    expect.soft(up.status, 'U-5 POST /api/uploads ต้องได้ 403').toBe(403);
    expect.soft(up.json?.batch_id ?? up.json?.batchId ?? null, 'U-5 POST /api/uploads ต้องไม่ได้ batch_id (upload_batches +0 ทางอ้อม)').toBeNull();
    expect.soft(ov.status, 'U-5 POST overrides ต้องได้ 403').toBe(403);
    expect.soft(after.overrides, 'ประวัติการแก้ผลของ {photoB} ต้องไม่เพิ่ม (result_overrides +0 ทางอ้อม)').toBe(before.overrides);
    expect.soft(after.current_result, 'ผลล่าสุดของ {photoB} ต้องไม่เปลี่ยน').toBe(before.current_result);
    expect.soft(rep.status, 'U-5 GET รายงาน D1 (ตัวควบคุม) ต้องได้ 200').toBe(200);
    expect.soft(siteRows(rep).length, 'U-5 รายงาน D1 ต้องมี 3 แถว').toBe(3);

    const { ctx, page } = await ctxAs(browser, undefined, c5);
    await page.goto(UI + '/upload');
    await page.waitForLoadState('domcontentloaded');
    await page.getByTestId('page-forbidden').waitFor({ timeout: 15000 }).catch(() => { });
    const bodyText = await page.locator('body').innerText();
    const navUpload = await page.getByTestId('nav-upload').count();
    const fileInput = await page.getByTestId('upload-file-input').count();
    expect.soft(bodyText.includes('ไม่มีสิทธิ์'), 'U-5 เปิด /upload ต้องเห็นหน้า "ไม่มีสิทธิ์"').toBe(true);
    expect.soft(navUpload, 'U-5 หน้า /upload ต้องไม่มี nav-upload').toBe(0);
    expect.soft(fileInput, 'U-5 หน้า /upload ต้องไม่มีช่องเลือกไฟล์').toBe(0);
    await shot(testInfo, page, 'TC-5-06 U-5 เปิด /upload');
    await ctx.close();

    await evidence(testInfo, 'evidence', {
      prep: prepEvidence,
      statuses: { 'U-5 POST /api/uploads': up.status, 'U-5 POST /api/photos/{photoB}/overrides': ov.status, 'U-5 GET /api/reports/daily?date=2026-11-16': rep.status },
      uploadResponse: leak(up), overrideResponse: leak(ov),
      indirect: 'ไม่เข้าถึงฐานข้อมูล: upload_batches +0 = คำตอบไม่มี batch_id · result_overrides +0 = ประวัติการแก้ผลและผลล่าสุดของ {photoB} (อ่านโดย U-1) ก่อน/หลังเท่ากัน',
      before, after, reportRows: siteRows(rep).map(s => s?.site?.code),
      uploadPage: { forbiddenText: bodyText.includes('ไม่มีสิทธิ์'), navUpload, uploadFileInput: fileInput },
    });
  });

  test('TC-5-07 [P1] ผู้บริหารดูรูป ผลรายรูป และประวัติไม่ได้', async ({ browser }, testInfo) => {
    await reset();
    const { photoB, prepEvidence } = await prep({ batch: false });
    const c5 = await login('U5');
    const apis: Record<string, string> = {
      'GET /api/photos?date=2026-11-16': `/api/photos?date=${D1}`,
      'GET /api/photos/{photoB}': `/api/photos/${photoB}`,
      'GET /api/photos/{photoB}/image': `/api/photos/${photoB}/image`,
      'GET /api/photos/{photoB}/overrides': `/api/photos/${photoB}/overrides`,
    };
    const statuses: Record<string, number> = {};
    const leaks: any = {};
    for (const [k, p] of Object.entries(apis)) {
      const r = await http('GET', p, { cookie: c5 });
      statuses[k] = r.status; leaks[k] = leak(r);
      expect.soft(r.status, `U-5 ${k} ต้องได้ 403`).toBe(403);
      expect.soft(leaks[k].isImage, `U-5 ${k} ต้องไม่มีไบต์รูป`).toBe(false);
      expect.soft(leaks[k].dataKeys, `U-5 ${k} ต้องไม่มีข้อมูลรูปหรือผล`).toEqual([]);
    }
    const { ctx, page } = await ctxAs(browser, undefined, c5);
    const pageOut: any = {};
    for (const [label, p] of [['/photos', '/photos'], ['/photos/{photoB}', `/photos/${photoB}`]] as const) {
      await page.goto(UI + p);
      await page.waitForLoadState('domcontentloaded');
      await page.getByTestId('page-forbidden').waitFor({ timeout: 15000 }).catch(() => { });
      const txt = await page.locator('body').innerText();
      pageOut[label] = { forbiddenText: txt.includes('ไม่มีสิทธิ์'), photoImage: await page.getByTestId('photo-image').count(), photoRows: await page.locator('[data-testid^="photo-row-"]').count(), currentResult: await page.getByTestId('photo-current-result').count() };
      expect.soft(pageOut[label].forbiddenText, `U-5 เปิด ${label} ต้องเห็น "ไม่มีสิทธิ์"`).toBe(true);
      expect.soft(pageOut[label].photoImage + pageOut[label].photoRows + pageOut[label].currentResult, `U-5 หน้า ${label} ต้องไม่แสดงรูปหรือผล`).toBe(0);
      await shot(testInfo, page, `TC-5-07 U-5 เปิด ${label}`);
    }
    await ctx.close();
    await evidence(testInfo, 'evidence', { prep: prepEvidence, statuses, leaks, pages: pageOut });
  });

  test('TC-5-08 [P1] ไม่พบ API key ของ gateway ในทุกแหล่ง', async ({ browser }, testInfo) => {
    await reset();
    const { photoB, batchB, prepEvidence } = await prep({ batch: true });
    const key = gatewayKey(); // ห้ามพิมพ์หรือแนบค่านี้
    expect(key.length, 'ต้องอ่าน GATEWAY_API_KEY จาก .env ได้ (ยาวพอสำหรับการค้น)').toBeGreaterThan(8);

    const found: Record<string, number> = {};
    const respSeen: { type: string; n: number }[] = [];
    let respHits = 0;
    const scanContext = async (label: string, ctx: BrowserContext, page: Page, paths: string[]) => {
      const pending: Promise<void>[] = [];
      page.on('response', resp => {
        const t = resp.request().resourceType();
        if (!['document', 'script', 'stylesheet', 'fetch', 'xhr'].includes(t)) return;
        // streaming responses (e.g. long-poll / RSC streams) may never end: bound each body read to 5 s
        const timeout = new Promise<null>(r => setTimeout(() => r(null), 5000));
        pending.push(Promise.race([resp.body().catch(() => null), timeout]).then(b => {
          if (!b) { respSeen.push({ type: t + ' (อ่านเนื้อไม่จบใน 5 วินาที)', n: 0 }); return; }
          const n = countIn(b.toString('utf8'), key); respHits += n; respSeen.push({ type: t, n });
        }));
      });
      for (const p of paths) {
        await page.goto(UI + p);
        await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => { });
        const n = countIn(await page.content(), key);
        found[`HTML ${label} ${p.replace(photoB, '{photoB}').replace(batchB, '{batchB}')}`] = n;
      }
      await Promise.all(pending);
    };

    const anon = await ctxAs(browser);
    await scanContext('ไม่ล็อกอิน', anon.ctx, anon.page, ['/login']);
    await shot(testInfo, anon.page, 'TC-5-08 หน้า login');
    await anon.ctx.close();

    const c2 = await login('U2');
    const ownA = (await http('GET', `/api/photos?date=${D1}&site=SITE-A`, { cookie: c2 })).json?.photos?.[0]?.id as string | undefined;
    const pagesFor = (extra: string[]) => ['/upload', `/uploads/${batchB}`, '/photos', '/photos/problems', `/photos/${photoB}`, '/reports/daily', ...extra];
    const u1 = await ctxAs(browser, 'U1');
    await scanContext('U-1', u1.ctx, u1.page, pagesFor([]));
    await shot(testInfo, u1.page, 'TC-5-08 หน้ารายงานของ U-1');
    await u1.ctx.close();
    const u2 = await ctxAs(browser, undefined, c2);
    await scanContext('U-2', u2.ctx, u2.page, pagesFor(ownA ? [`/photos/${ownA}`] : []));
    await u2.ctx.close();
    found['JS/CSS/เอกสาร/fetch ที่หน้าโหลด (รวม)'] = respHits;

    const health = await http('GET', '/api/health');
    found['/api/health'] = countIn(health.text, key);

    const logs: Record<string, number> = {};
    for (const c of [WEB_CONTAINER, DISPATCHER_CONTAINER]) {
      const out = execSync(`docker logs ${c} 2>&1`, { encoding: 'utf8', maxBuffer: 1024 * 1024 * 1024, stdio: ['ignore', 'pipe', 'pipe'] });
      found[`docker logs ${c}`] = countIn(out, key);
      logs[c] = out.length;
    }

    // ซอร์สของ web ในคอนเทนเนอร์ (ยกเว้น .env และ node_modules) · ส่ง key ทาง env var ไม่อยู่ในบรรทัดคำสั่ง
    const grepScript = 'n=$(grep -rlF -- "$K" /app --exclude=.env --exclude-dir=node_modules 2>/dev/null | wc -l); echo "$n"';
    const srcFiles = Number(execFileSync('docker', ['exec', '-e', 'K', WEB_CONTAINER, 'sh', '-c', grepScript], { encoding: 'utf8', env: { ...process.env, K: key } }).trim());
    found['ซอร์ส web /app (ไฟล์ที่มี key)'] = srcFiles;
    // ตัวควบคุม: คำสั่งค้นเดียวกันต้องเจอคำที่รู้ว่ามี เพื่อยืนยันว่าการค้นทำงาน
    const control = Number(execFileSync('docker', ['exec', '-e', 'K', WEB_CONTAINER, 'sh', '-c', grepScript], { encoding: 'utf8', env: { ...process.env, K: 'sitesafe' } }).trim());
    expect.soft(control > 0, 'ตัวควบคุม: grep ในซอร์ส web ต้องเจอคำว่า sitesafe อย่างน้อย 1 ไฟล์').toBe(true);

    for (const [src, n] of Object.entries(found)) expect.soft(n, `พบ API key ใน ${src} ต้องเป็น 0 ครั้ง`).toBe(0);
    const total = Object.values(found).reduce((s, n) => s + n, 0);
    await evidence(testInfo, 'evidence', {
      prep: prepEvidence,
      statuses: { 'GET /api/health': health.status },
      keyLoaded: true, note: 'ไม่แนบค่า key · รายงานเฉพาะจำนวนครั้งที่พบ',
      foundCounts: found, totalFound: total,
      responsesScanned: respSeen.length, responsesByType: respSeen.reduce((m: any, r) => { m[r.type] = (m[r.type] || 0) + 1; return m; }, {}),
      logChars: logs, sourceGrepControlFiles: control,
    });
  });

  test('TC-5-09 [P1] ออกจากระบบแล้ว cookie เดิมใช้ไม่ได้', async ({ browser }, testInfo) => {
    await reset();
    const c2 = await login('U2');
    const before = await http('GET', '/api/photos', { cookie: c2 });
    const out = await http('POST', '/api/auth/logout', { cookie: c2 });
    const after = await http('GET', '/api/photos', { cookie: c2 });
    expect.soft(before.status, 'ก่อน logout GET /api/photos ต้องได้ 200').toBe(200);
    expect.soft(out.status >= 200 && out.status < 300, 'POST /api/auth/logout ต้องสำเร็จ').toBe(true);
    expect.soft(after.status, 'หลัง logout ใช้ cookie เดิม GET /api/photos ต้องได้ 401').toBe(401);
    expect.soft(leak(after).dataKeys, 'หลัง logout คำตอบต้องไม่มีข้อมูลรูป').toEqual([]);

    const { ctx, page } = await ctxAs(browser, undefined, c2); // ใส่ cookie เดิมลงเบราว์เซอร์
    await page.goto(UI + '/photos');
    await page.waitForLoadState('domcontentloaded');
    const landed = new URL(page.url()).pathname;
    expect.soft(landed, 'หลัง logout เปิด /photos ด้วย cookie เดิมต้องถูกส่งไป /login').toBe('/login');
    await shot(testInfo, page, 'TC-5-09 cookie เดิมหลัง logout');
    await ctx.close();
    await evidence(testInfo, 'evidence', {
      statuses: { 'GET /api/photos ก่อน logout': before.status, 'POST /api/auth/logout': out.status, 'GET /api/photos cookie เดิมหลัง logout': after.status },
      beforeTotal: before.json?.total ?? null, afterResponse: leak(after), pageWithOldCookie: landed,
    });
  });
});
