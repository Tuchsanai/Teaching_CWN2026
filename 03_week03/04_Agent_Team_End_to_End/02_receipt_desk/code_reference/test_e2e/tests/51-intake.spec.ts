/**
 * TEST-PLAN 5.1 การรับชุดใบเสร็จ (TC-1-01 … TC-1-09) · all environment A (runs on the mock stack :3421).
 * Expected values come only from the plan's "ผลที่คาดหวัง" column.
 */
import * as path from 'path';
import type { APIRequestContext, Page, Response, TestInfo } from '@playwright/test';
import { test, expect, apiAs, reset, clientId, upload, reconcile, pageAs, evidence, shot, dataFile, okFiles, M_URL } from './lib/rd';

// ---------------------------------------------------------------- local helpers
/** First (possibly negative) integer in a text, commas removed. NaN when none. */
function num(s: string | null | undefined): number {
  const m = (s ?? '').replace(/,/g, '').match(/-?\d+/);
  return m ? Number(m[0]) : NaN;
}

/** Pick CL-0x in `upload-client-select` (option value = UUID, else label with code / name). */
async function selectClient(page: Page, uuid: string) {
  const sel = page.getByTestId('upload-client-select');
  await expect.poll(() => sel.locator('option').count(), { message: 'client options loaded', timeout: 15_000 }).toBeGreaterThan(1);
  const opts = await sel.locator('option').evaluateAll(os => os.map(o => ({ v: (o as HTMLOptionElement).value, t: o.textContent || '' })));
  const hit = opts.find(o => o.v === uuid) || opts.find(o => o.t.includes('CL-01')) || opts.find(o => o.t.includes('ร้านข้าวแกงสมชาย'));
  if (!hit) throw new Error('CL-01 not in upload-client-select: ' + JSON.stringify(opts));
  await sel.selectOption(hit.v);
}

type PageUpload = { sent: boolean; status: number | null; json: any; ms: number; acceptedText: string | null; errorText: string | null };

/**
 * Upload `files` through /upload as the logged-in user of `page`.
 * Returns the HTTP status/JSON of the W7 request the page actually sent (sent=false if the page blocked it before sending),
 * the time from click to the moment `upload-accepted-count` (or `upload-error`) is visible, and the texts shown.
 */
async function pageUpload(page: Page, clientUuid: string, files: string[]): Promise<PageUpload> {
  await page.goto('/upload');
  await selectClient(page, clientUuid);
  await page.getByTestId('upload-file-input').setInputFiles(files.map(f => (path.isAbsolute(f) ? f : dataFile(f))));
  const respP: Promise<Response | null> = page
    .waitForResponse(r => r.url().includes('/api/batches') && r.request().method() === 'POST', { timeout: 120_000 })
    .catch(() => null);
  const accepted = page.getByTestId('upload-accepted-count');
  const error = page.getByTestId('upload-error');
  const t0 = Date.now();
  await page.getByTestId('upload-submit-button').click();
  // whichever comes first: the request's response, or an error shown without a request
  const first: Response | null | 'ui' = await Promise.race([
    respP,
    error.waitFor({ state: 'visible', timeout: 120_000 }).then(() => 'ui' as const).catch(() => 'ui' as const),
  ]);
  const resp: Response | null = first === 'ui' ? await Promise.race([respP, new Promise<null>(r => setTimeout(() => r(null), 3000))]) : first;
  // wait for the page to show a result (accepted count or error)
  await Promise.race([
    accepted.waitFor({ state: 'visible', timeout: 120_000 }),
    error.waitFor({ state: 'visible', timeout: 120_000 }),
  ]).catch(() => undefined);
  const ms = Date.now() - t0;
  const json = resp ? await resp.json().catch(() => ({})) : null;
  const acceptedText = (await accepted.isVisible().catch(() => false)) ? await accepted.innerText() : null;
  const errorText = (await error.isVisible().catch(() => false)) ? await error.innerText() : null;
  return { sent: !!resp, status: resp ? resp.status() : null, json, ms, acceptedText, errorText };
}

/** All `upload-file-error-{n}` texts plus `upload-error` (for "names the file" checks). */
async function uploadErrorTexts(page: Page): Promise<string> {
  const parts = await page.locator('[data-testid^="upload-file-error-"], [data-testid="upload-error"]').allInnerTexts().catch(() => []);
  return parts.join('\n');
}

/** W20 checks: accepted = expected, sum of all statuses = expected, diff = 0. */
async function expectReconcile(office: APIRequestContext, testInfo: TestInfo, expected: number, label: string, checkDiff = true) {
  const rec = await reconcile(office);
  await evidence(testInfo, `W20 reconcile ${label}`, rec);
  const countsSum = Object.values(rec.counts ?? {}).reduce((a: number, v: any) => a + Number(v || 0), 0);
  expect.soft(rec.accepted, `${label}: ยอดตรวจนับ รับแล้วทั้งสำนักงาน`).toBe(expected);
  expect.soft(countsSum, `${label}: ผลรวมทุกสถานะ (counts)`).toBe(expected);
  expect.soft(Number(rec.sum), `${label}: ผลรวมทุกสถานะ (sum)`).toBe(expected);
  if (checkDiff) expect.soft(Number(rec.diff), `${label}: ผลต่าง`).toBe(0);
  return rec;
}

/** /batches page reconcile cards -> soft checks + screenshot. */
async function expectReconcilePage(page: Page, testInfo: TestInfo, expected: number, label: string) {
  await page.goto('/batches');
  await page.getByTestId('reconcile-accepted').waitFor({ state: 'visible' });
  for (const id of ['reconcile-accepted', 'reconcile-sum', 'reconcile-diff']) {
    await expect(page.getByTestId(id), `${id} loaded`).toHaveText(/\d/, { timeout: 15_000 }).catch(() => undefined);
  }
  const acc = num(await page.getByTestId('reconcile-accepted').innerText());
  const sum = num(await page.getByTestId('reconcile-sum').innerText());
  const diff = num(await page.getByTestId('reconcile-diff').innerText());
  await shot(testInfo, page, `batches reconcile ${label}`);
  expect.soft(acc, `${label}: reconcile-accepted บนหน้า /batches`).toBe(expected);
  expect.soft(sum, `${label}: reconcile-sum บนหน้า /batches`).toBe(expected);
  expect.soft(diff, `${label}: reconcile-diff บนหน้า /batches`).toBe(0);
}

/** Check a rejected W7 answer: status, error code, accepted 0, file name in the answer. */
function expectRejected(r: { status: number | null; json: any }, code: string, label: string, fileName?: string) {
  expect.soft(r.status, `${label}: HTTP`).toBe(422);
  expect.soft(r.json?.error, `${label}: error`).toBe(code);
  expect.soft(Number(r.json?.accepted ?? 0), `${label}: accepted`).toBe(0);
  if (fileName) expect.soft(JSON.stringify(r.json ?? {}), `${label}: คำตอบบอกชื่อไฟล์ ${fileName}`).toContain(fileName);
}

// ---------------------------------------------------------------- tests
test.describe('5.1 การรับชุดใบเสร็จ', () => {

  test('TC-1-01 ชุด 99 ไฟล์ (ต่ำกว่าเส้น)', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    const { context, page } = await pageAs(browser, M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      const r = await pageUpload(page, cl, okFiles(99));
      await evidence(testInfo, 'W7 response (99 files)', { sent: r.sent, status: r.status, json: r.json, ms: r.ms, acceptedText: r.acceptedText, errorText: r.errorText });
      await shot(testInfo, page, 'upload 99 accepted');
      expect.soft(r.sent, 'page sent W7').toBe(true);
      expect.soft([200, 201], `BR-01: HTTP of 99-file batch = ${r.status}`).toContain(r.status);
      expect.soft(Number(r.json?.accepted), 'BR-01: W7 accepted').toBe(99);
      expect.soft(num(r.acceptedText), 'BR-01: upload-accepted-count').toBe(99);
      await expectReconcile(office, testInfo, 8 + 99, 'หลังส่ง 99');
      await expectReconcilePage(page, testInfo, 8 + 99, 'หลังส่ง 99');
    } finally {
      await context.close();
      await office.dispose();
    }
  });

  test('TC-1-02 ชุด 100 ไฟล์ (เท่ากับเส้น) และเวลาตอบ', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    const { context, page } = await pageAs(browser, M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      const files = okFiles(100);
      const r = await pageUpload(page, cl, files);
      await evidence(testInfo, 'W7 response (100 files)', { sent: r.sent, status: r.status, json: r.json, ms: r.ms, acceptedText: r.acceptedText, errorText: r.errorText });
      await shot(testInfo, page, 'upload 100 accepted');
      expect.soft(r.sent, 'page sent W7').toBe(true);
      expect.soft([200, 201], `BR-01: HTTP of 100-file batch = ${r.status}`).toContain(r.status);
      expect.soft(Number(r.json?.accepted), 'BR-01: W7 accepted = files sent').toBe(files.length);
      expect.soft(num(r.acceptedText), 'BR-01: upload-accepted-count = 100').toBe(100);
      expect.soft(r.ms, `NFR-02: click -> accepted count shown (${r.ms} ms) ≤ 60 s`).toBeLessThanOrEqual(60_000);
      await expectReconcile(office, testInfo, 8 + 100, 'หลังส่ง 100');
    } finally {
      await context.close();
      await office.dispose();
    }
  });

  test('TC-1-03 ชุด 101 ไฟล์ และชุด 0 ไฟล์', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    const { context, page } = await pageAs(browser, M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      // ① 101 files through the page
      const files = okFiles(101);
      const r1 = await pageUpload(page, cl, files);
      await evidence(testInfo, '① W7 from page (101 files)', { sent: r1.sent, status: r1.status, json: r1.json, acceptedText: r1.acceptedText, errorText: r1.errorText });
      await shot(testInfo, page, '① upload 101 rejected');
      if (r1.sent) {
        expectRejected(r1, 'batch_size', '① 101 ไฟล์ (หน้าเว็บ)');
      } else {
        // page blocked before sending -> same request through the API for the HTTP code (plan section 4)
        expect.soft(r1.errorText, '① page shows upload-error').toBeTruthy();
        const a1 = await upload(office, { clientId: cl, files });
        await evidence(testInfo, '① W7 API (101 files)', a1.json);
        expectRejected(a1, 'batch_size', '① 101 ไฟล์ (API)');
      }
      if (r1.acceptedText !== null) expect.soft(num(r1.acceptedText), '① upload-accepted-count').toBe(0);
      await expectReconcile(office, testInfo, 8, 'หลัง ① (ใบทั้งระบบยังเป็น 8)');

      // ② request without files through the API
      const r2 = await upload(office, { clientId: cl, files: [] });
      await evidence(testInfo, '② W7 API (0 files)', { status: r2.status, json: r2.json });
      expectRejected(r2, 'batch_size', '② 0 ไฟล์ (API)');
      await expectReconcile(office, testInfo, 8, 'หลัง ② (ใบทั้งระบบยังเป็น 8)');
    } finally {
      await context.close();
      await office.dispose();
    }
  });

  test('TC-1-04 ขนาดต่ำกว่าและเท่ากับ 10.00 MB', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    const { context, page } = await pageAs(browser, M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      for (const f of ['size-under.jpg', 'size-equal.jpg']) {
        const r = await pageUpload(page, cl, [f]);
        await evidence(testInfo, `W7 ${f}`, { sent: r.sent, status: r.status, json: r.json, acceptedText: r.acceptedText, errorText: r.errorText });
        await shot(testInfo, page, `upload ${f}`);
        expect.soft(r.sent, `${f}: page sent W7`).toBe(true);
        expect.soft([200, 201], `BR-02: HTTP of ${f} = ${r.status}`).toContain(r.status);
        expect.soft(Number(r.json?.accepted), `BR-02: ${f} W7 accepted`).toBe(1);
        expect.soft(num(r.acceptedText), `BR-02: ${f} upload-accepted-count`).toBe(1);
      }
      await evidence(testInfo, 'W20 reconcile (after both)', await reconcile(office));
    } finally {
      await context.close();
      await office.dispose();
    }
  });

  test('TC-1-05 ขนาดเกิน 10.00 MB 1 ไบต์', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    const { context, page } = await pageAs(browser, M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      const r = await pageUpload(page, cl, ['size-over.jpg']);
      const shown = await uploadErrorTexts(page);
      await evidence(testInfo, 'W7 size-over.jpg', { sent: r.sent, status: r.status, json: r.json, acceptedText: r.acceptedText, errorText: r.errorText, shown });
      await shot(testInfo, page, 'upload size-over rejected');
      if (r.sent) {
        expectRejected(r, 'file_too_large', 'size-over (หน้าเว็บ)', 'size-over.jpg');
      } else {
        const a = await upload(office, { clientId: cl, files: ['size-over.jpg'] });
        await evidence(testInfo, 'W7 API size-over.jpg', a.json);
        expectRejected(a, 'file_too_large', 'size-over (API)', 'size-over.jpg');
      }
      expect.soft(shown, 'BR-02: ข้อความบนหน้ามีชื่อ size-over.jpg').toContain('size-over.jpg');
      expect.soft(shown.replace(/size-over\.jpg/g, '').replace(/[\s\d.:“”"'·—-]/g, '').length, 'BR-02: ข้อความบนหน้ามีเหตุผล (ไม่ใช่แค่ชื่อไฟล์)').toBeGreaterThan(0);
      if (r.acceptedText !== null) expect.soft(num(r.acceptedText), 'upload-accepted-count').toBe(0);
      await expectReconcile(office, testInfo, 8, 'รับ 0 ใบ (ยังเป็น 8)');
    } finally {
      await context.close();
      await office.dispose();
    }
  });

  test('TC-1-06 ชนิดไฟล์ที่รับ', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    const { context, page } = await pageAs(browser, M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      const files = ['ok-100.jpg', 'ok-100.png', 'page-1.pdf'];
      const r = await pageUpload(page, cl, files);
      await evidence(testInfo, 'W7 jpg+png+pdf', { sent: r.sent, status: r.status, json: r.json, acceptedText: r.acceptedText, errorText: r.errorText });
      await shot(testInfo, page, 'upload 3 types');
      expect.soft(r.sent, 'page sent W7').toBe(true);
      expect.soft([200, 201], `BR-03: HTTP = ${r.status}`).toContain(r.status);
      expect.soft(Number(r.json?.accepted), 'BR-03: W7 accepted').toBe(3);
      expect.soft(num(r.acceptedText), 'BR-03: upload-accepted-count').toBe(3);

      const batchId: string | undefined = r.json?.batchId;
      const receipts: any[] = r.json?.receipts ?? [];
      expect.soft(receipts.map(x => x.fileName).sort(), 'all 3 files listed in the batch').toEqual([...files].sort());
      if (batchId) {
        const b = await office.get(`/api/batches/${batchId}`);
        await evidence(testInfo, 'W9 batch', await b.json().catch(() => ({})));
        await page.goto(`/batches/${batchId}`);
        await page.getByTestId('batch-count-accepted').waitFor({ state: 'visible' });
        await expect(page.getByTestId('batch-count-accepted')).toHaveText(/\d/).catch(() => undefined);
        expect.soft(num(await page.getByTestId('batch-count-accepted').innerText()), 'batch-count-accepted').toBe(3);
        for (const rc of receipts) {
          await expect.soft(page.getByTestId(`receipt-row-${rc.id}`), `${rc.fileName} อยู่ในหน้าชุดเดียวกัน`).toBeVisible();
        }
        await shot(testInfo, page, 'batch page with 3 receipts');
      } else {
        expect.soft(batchId, 'W7 batchId').toBeTruthy();
      }
    } finally {
      await context.close();
      await office.dispose();
    }
  });

  test('TC-1-07 PDF 0 หน้า และ 2 หน้า', { tag: ['@P2', '@A'] }, async ({}, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      for (const f of ['page-0.pdf', 'page-2.pdf']) {
        const r = await upload(office, { clientId: cl, files: [f] });
        await evidence(testInfo, `W7 ${f}`, { status: r.status, json: r.json });
        expectRejected(r, 'pdf_pages', f, f);
      }
      await expectReconcile(office, testInfo, 8, 'รับ 0 ใบ (ยังเป็น 8)');
    } finally {
      await office.dispose();
    }
  });

  test('TC-1-08 ไฟล์ชนิดอื่น และนามสกุลปลอม', { tag: ['@P3', '@A'] }, async ({}, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      for (const f of ['anim.gif', 'fake.jpg']) {
        const r = await upload(office, { clientId: cl, files: [f] });
        await evidence(testInfo, `W7 ${f}`, { status: r.status, json: r.json });
        expectRejected(r, 'file_type', f, f);
      }
      await expectReconcile(office, testInfo, 8, 'รับ 0 ใบ (ยังเป็น 8)');
    } finally {
      await office.dispose();
    }
  });

  test('TC-1-09 ชุดผสม: ไฟล์ดี 3 + ไฟล์เกินขนาด 1 แล้วเอาออก', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U01');
    const { context, page } = await pageAs(browser, M_URL, 'U01');
    try {
      const cl = await clientId(office, 'CL-01');
      const good = okFiles(3);
      // ① 3 good + size-over
      const r1 = await pageUpload(page, cl, [...good, 'size-over.jpg']);
      const shown = await uploadErrorTexts(page);
      await evidence(testInfo, '① W7 3 ok + size-over', { sent: r1.sent, status: r1.status, json: r1.json, acceptedText: r1.acceptedText, errorText: r1.errorText, shown });
      await shot(testInfo, page, '① mixed batch rejected');
      if (r1.sent) {
        expect.soft(r1.status, '① HTTP: ปฏิเสธทั้งชุด').toBe(422);
        expect.soft(Number(r1.json?.accepted ?? 0), '① W7 accepted').toBe(0);
        expect.soft(JSON.stringify(r1.json ?? {}), '① คำตอบบอก size-over.jpg').toContain('size-over.jpg');
      } else {
        const a1 = await upload(office, { clientId: cl, files: [...good, 'size-over.jpg'] });
        await evidence(testInfo, '① W7 API', a1.json);
        expect.soft(a1.status, '① HTTP (API): ปฏิเสธทั้งชุด').toBe(422);
        expect.soft(Number(a1.json?.accepted ?? 0), '① W7 accepted (API)').toBe(0);
        expect.soft(JSON.stringify(a1.json ?? {}), '① คำตอบบอก size-over.jpg').toContain('size-over.jpg');
      }
      expect.soft(shown, '① ข้อความบนหน้าบอก size-over.jpg').toContain('size-over.jpg');
      if (r1.acceptedText !== null) expect.soft(num(r1.acceptedText), '① upload-accepted-count').toBe(0);
      await expectReconcile(office, testInfo, 8, '① ใบทั้งระบบยังเป็น 8');

      // ② size-over removed, send again
      const r2 = await pageUpload(page, cl, good);
      await evidence(testInfo, '② W7 3 ok', { sent: r2.sent, status: r2.status, json: r2.json, acceptedText: r2.acceptedText, errorText: r2.errorText });
      await shot(testInfo, page, '② 3 accepted');
      expect.soft([200, 201], `② HTTP = ${r2.status}`).toContain(r2.status);
      expect.soft(Number(r2.json?.accepted), '② W7 accepted').toBe(3);
      expect.soft(num(r2.acceptedText), '② upload-accepted-count').toBe(3);
      await expectReconcile(office, testInfo, 8 + 3, '② ยอดตรวจนับ 11');
      await expectReconcilePage(page, testInfo, 8 + 3, '② ยอดตรวจนับ 11');
    } finally {
      await context.close();
      await office.dispose();
    }
  });
});
