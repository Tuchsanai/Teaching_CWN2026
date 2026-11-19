/**
 * TEST-PLAN 5.8 ลูกค้าภายนอก (TC-8-01 … TC-8-05) · runs on the mock stack :3421.
 * Expected values come only from the plan's "ผลที่คาดหวัง" column.
 */
import type { APIRequestContext, Browser, Page, Response, TestInfo } from '@playwright/test';
import {
  test, expect, apiAs, reset, clientId, categoryId, upload, waitStatus, pageAs, pauseReader, resumeReader,
  evidence, shot, okFiles, dataFile, M_URL,
} from './lib/rd';

// ---------------------------------------------------------------- local helpers
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const ISO_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/;
const STATUS_WAITING = 'รับแล้ว รอสำนักงานตรวจ';
const NUMBER_KEY_RE = /total|item|price|confidence|amount|sum/i;

/** Money text -> satang (commas removed). NaN when none. */
function satang(s: string | number | null | undefined): number {
  const m = String(s ?? '').replace(/,/g, '').match(/-?\d+(?:\.\d+)?/);
  return m ? Math.round(Number(m[0]) * 100) : NaN;
}
/** First integer in a text. */
function int(s: string | null | undefined): number {
  const m = (s ?? '').replace(/,/g, '').match(/-?\d+/);
  return m ? Number(m[0]) : NaN;
}

/** Office lookup of seeded / uploaded receipts by fileName (office W11 has id, batchId, clientId, status, total). */
async function officeReceipts(office: APIRequestContext, query = ''): Promise<any[]> {
  const r = await office.get(`/api/receipts?limit=1000${query}`);
  expect(r.status(), `office W11 ${query}`).toBe(200);
  return (await r.json()).receipts;
}
async function byFile(office: APIRequestContext, fileName: string) {
  const r = (await officeReceipts(office)).find(x => x.fileName === fileName);
  if (!r) throw new Error(`${fileName} not found by office W11`);
  return r;
}

/** Keys holding numbers from reading (total, items, prices, confidence) that are present and not null. */
function numberFields(obj: any): string[] {
  const hits: string[] = [];
  const walk = (o: any, p: string) => {
    if (o === null || typeof o !== 'object') return;
    for (const [k, v] of Object.entries(o)) {
      const kp = p ? `${p}.${k}` : k;
      if (NUMBER_KEY_RE.test(k) && v !== null && v !== undefined && !(Array.isArray(v) && v.length === 0)) hits.push(`${kp}=${JSON.stringify(v)}`);
      else walk(v, kp);
    }
  };
  walk(obj, '');
  return hits;
}

/** Values in a JSON tree (ids and ISO times skipped) that equal / contain one of the forbidden numbers. */
function leakedValues(obj: any, forbidden: RegExp): string[] {
  const hits: string[] = [];
  const walk = (o: any, p: string) => {
    if (o === null || o === undefined) return;
    if (typeof o === 'number') { if (forbidden.test(String(o))) hits.push(`${p}=${o}`); return; }
    if (typeof o === 'string') { if (!UUID_RE.test(o) && !ISO_RE.test(o) && forbidden.test(o)) hits.push(`${p}=${o}`); return; }
    if (typeof o === 'object') for (const [k, v] of Object.entries(o)) walk(v, p ? `${p}.${k}` : k);
  };
  walk(obj, '');
  return hits;
}
/** 500.00 / 500 / 50000 as a whole number (digit boundaries). */
const RE_500 = /(?<![\d.])(500(\.0+)?|50000)(?![\d])/;
const RE_999 = /(?<![\d.])999(\.00)?(?![\d])/;
const RE_100 = /(?<![\d.])100\.00(?![\d])/;

/** Portal: upload files from /portal; returns the W7 response the page sent and the texts shown. */
async function portalUpload(page: Page, files: string[]) {
  await page.goto('/portal');
  await page.getByTestId('portal-file-input').setInputFiles(files.map(f => dataFile(f)));
  const respP: Promise<Response | null> = page
    .waitForResponse(r => r.url().includes('/api/batches') && r.request().method() === 'POST', { timeout: 120_000 })
    .catch(() => null);
  await page.getByTestId('portal-upload-button').click();
  const resp = await respP;
  const accepted = page.getByTestId('portal-accepted-count');
  const error = page.getByTestId('portal-upload-error');
  await Promise.race([
    accepted.waitFor({ state: 'visible', timeout: 30_000 }),
    error.waitFor({ state: 'visible', timeout: 30_000 }),
  ]).catch(() => undefined);
  await page.waitForTimeout(500);
  return {
    status: resp ? resp.status() : null,
    json: resp ? await resp.json().catch(() => ({})) : null,
    acceptedText: (await accepted.isVisible().catch(() => false)) ? await accepted.innerText() : null,
    errorText: (await error.isVisible().catch(() => false)) ? await error.innerText() : null,
  };
}

/** Portal page state for month 2026-11. */
async function portalState(page: Page) {
  await page.goto('/portal');
  const month = page.getByTestId('portal-month-input');
  await month.waitFor({ state: 'visible' });
  if ((await month.inputValue()) !== '2026-11') {
    await month.fill('2026-11');
    await month.press('Enter').catch(() => undefined);
    await page.waitForTimeout(1000);
  }
  await page.getByTestId('portal-summary-total').waitFor({ state: 'visible' });
  await page.waitForTimeout(500);
  const summary = await page.getByTestId('portal-summary-total').innerText();
  const cats = page.locator('[data-testid^="portal-category-total-"]');
  const catList = await cats.evaluateAll(es => es.map(e => ({ id: (e.getAttribute('data-testid') || '').replace('portal-category-total-', ''), text: (e as HTMLElement).innerText })));
  return { summary, cats: catList, text: await page.locator('body').innerText() };
}

/** Rows, statuses and totals of given receipt ids on /portal (already loaded). */
async function portalRows(page: Page, ids: string[]) {
  const out: Record<string, { visible: boolean; row: string; status: string | null; totalCount: number; total: string | null }> = {};
  for (const id of ids) {
    const row = page.getByTestId(`portal-receipt-row-${id}`);
    const visible = await row.isVisible().catch(() => false);
    const totalLoc = page.getByTestId(`portal-receipt-total-${id}`);
    const totalCount = await totalLoc.count();
    out[id] = {
      visible,
      row: visible ? await row.innerText() : '',
      status: (await page.getByTestId(`portal-receipt-status-${id}`).isVisible().catch(() => false)) ? await page.getByTestId(`portal-receipt-status-${id}`).innerText() : null,
      totalCount,
      total: totalCount ? await totalLoc.first().innerText() : null,
    };
  }
  return out;
}

/** Text of a portal row after removing file name and accepted time -> must have no digits. */
function rowExtraDigits(row: string, fileName: string): string | null {
  const rest = row.replace(fileName, '').replace(/\d{1,2}\/\d{1,2}\/\d{4}(\s+\d{1,2}:\d{2}(:\d{2})?)?/g, '');
  const m = rest.match(/\d[\d.,]*/g);
  return m ? m.join(' ') : null;
}

/** Setup shared by TC-8-03 and TC-8-04: reset, pause, U-05 uploads 2 files from /portal, checks while paused, resume, wait review. */
async function customerUploadsTwo(browser: Browser, testInfo: TestInfo) {
  await reset(M_URL);
  const office = await apiAs(M_URL, 'U04');
  const staff = await apiAs(M_URL, 'U01');
  const client = await apiAs(M_URL, 'U05');
  const cl01 = await clientId(office, 'CL-01');
  const files = okFiles(2, 1); // ok-100__001.jpg, ok-100__002.jpg
  const cust = await pageAs(browser, M_URL, 'U05');
  const st = await pageAs(browser, M_URL, 'U01');
  let ids: string[] = [];
  let readTimeout = false;
  pauseReader();
  try {
    // ① customer sends 2 files from /portal
    const up = await portalUpload(cust.page, files);
    await evidence(testInfo, '① W7 จาก /portal (U-05)', up);
    await shot(testInfo, cust.page, '① U-05 /portal หลังส่ง 2 ไฟล์');
    expect.soft(up.status, '① W7 จาก /portal: HTTP').toBe(201);
    expect.soft(int(up.acceptedText), '① portal-accepted-count = 2').toBe(2);

    // note the 2 IDs (office lookup by file name, bound shop checked separately)
    const all = await officeReceipts(office);
    const mine = files.map(f => all.find(r => r.fileName === f));
    expect(mine.every(Boolean), '① ทั้ง 2 ไฟล์ถูกรับและมี ID').toBe(true);
    ids = mine.map(r => r.id);
    await evidence(testInfo, '① 2 IDs (office W11)', mine);

    // customer sees 2 rows: file name, time, status "รับแล้ว รอสำนักงานตรวจ"
    await cust.page.goto('/portal');
    await cust.page.getByTestId('portal-month-input').waitFor({ state: 'visible' });
    const rows1 = await portalRows(cust.page, ids);
    await evidence(testInfo, '① แถวบน /portal ขณะพักการอ่าน', rows1);
    await shot(testInfo, cust.page, '① U-05 เห็น 2 แถว');
    ids.forEach((id, i) => {
      const r = rows1[id];
      expect.soft(r.visible, `① ลูกค้าเห็นแถว ${files[i]}`).toBe(true);
      expect.soft(r.row, `① แถว ${files[i]} มีชื่อไฟล์`).toContain(files[i]);
      expect.soft(r.row, `① แถว ${files[i]} มีเวลาที่รับ`).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}\s+\d{1,2}:\d{2}/);
      expect.soft(r.status, `① แถว ${files[i]} สถานะ`).toBe(STATUS_WAITING);
      expect.soft(r.totalCount, `① แถว ${files[i]} ไม่มี portal-receipt-total`).toBe(0);
    });

    // U-01 opens /receipts filtered by CL-01 immediately -> both IDs bound to CL-01
    await st.page.goto('/receipts');
    await st.page.getByTestId('filter-client-select').selectOption(cl01);
    await st.page.getByTestId('filter-apply-button').click();
    await st.page.waitForTimeout(1500);
    for (let i = 0; i < ids.length; i++) {
      await expect.soft(st.page.getByTestId(`receipt-row-${ids[i]}`), `① U-01 /receipts กรอง CL-01 เห็น ${files[i]}`).toBeVisible();
    }
    await shot(testInfo, st.page, '① U-01 /receipts กรอง CL-01');
    const staffList = await officeReceipts(staff, `&client_id=${cl01}`);
    const bound = ids.map(id => staffList.find(r => r.id === id));
    await evidence(testInfo, '① U-01 W11 client_id=CL-01', bound);
    ids.forEach((id, i) => expect.soft(bound[i]?.clientId, `① ${files[i]} ผูก CL-01`).toBe(cl01));
  } finally {
    resumeReader();
  }

  // ② wait up to 5 minutes for review
  if (ids.length === 2) {
    try {
      await waitStatus(staff, ids, ['review'], 5 * 60_000);
    } catch (e) {
      readTimeout = true;
      testInfo.annotations.push({ type: 'หมดเวลาอ่าน', description: String(e) });
    }
  }
  return { office, staff, client, cl01, files, ids, cust, st, readTimeout };
}

/** Customer-side checks: no number/internal status of `ids` on /portal and in W11/W12 JSON. */
async function expectNoNumbersForCustomer(page: Page, client: APIRequestContext, ids: string[], files: string[], testInfo: TestInfo, label: string) {
  const rows = await portalRows(page, ids);
  await evidence(testInfo, `${label} แถวบน /portal`, rows);
  const list = (await (await client.get('/api/receipts?limit=1000')).json()).receipts as any[];
  for (let i = 0; i < ids.length; i++) {
    const r = rows[ids[i]];
    expect.soft(r.visible, `${label}: ลูกค้าเห็นแถว ${files[i]}`).toBe(true);
    expect.soft(r.totalCount, `${label}: ${files[i]} ไม่มี portal-receipt-total`).toBe(0);
    expect.soft(r.row, `${label}: แถว ${files[i]} ไม่มี 100.00`).not.toMatch(RE_100);
    expect.soft(rowExtraDigits(r.row, files[i]), `${label}: แถว ${files[i]} ไม่มีตัวเลขอื่นนอกจากเวลา (รายการ/ราคา)`).toBeNull();
    expect.soft(r.row, `${label}: แถว ${files[i]} ไม่มีสถานะภายใน`).not.toMatch(/queued|review|processing/);
    const w11 = list.find(x => x.id === ids[i]);
    const w12r = await client.get(`/api/receipts/${ids[i]}`);
    const w12 = await w12r.json().catch(() => ({}));
    await evidence(testInfo, `${label} JSON ${files[i]} (W11 + W12 ของลูกค้า)`, { w11, w12status: w12r.status(), w12 });
    expect.soft(w12r.status(), `${label}: W12 ${files[i]} ของร้านตัวเอง`).toBe(200);
    expect.soft(numberFields(w11), `${label}: W11 ${files[i]} ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ`).toEqual([]);
    expect.soft(numberFields(w12), `${label}: W12 ${files[i]} ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ`).toEqual([]);
    expect.soft(leakedValues({ w11, w12 }, RE_100), `${label}: JSON ${files[i]} ไม่มี 100.00`).toEqual([]);
    expect.soft(JSON.stringify({ w11, w12 }), `${label}: JSON ${files[i]} ไม่มีสถานะภายใน`).not.toMatch(/"(queued|review|processing)"/);
  }
  const body = await page.locator('body').innerText();
  expect.soft(body, `${label}: หน้าไม่มีสถานะภายใน queued/review`).not.toMatch(/\b(queued|review)\b/);
}

// ---------------------------------------------------------------- tests
test.describe('5.8 ลูกค้าภายนอก', () => {
  test('TC-8-01 ลูกค้า CL-01 ขอข้อมูลร้าน CL-02 ทุกช่องทาง', { tag: ['@P1', '@A'] }, async ({}, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U04');
    const client = await apiAs(M_URL, 'U05');
    try {
      const s08 = await byFile(office, 'S-08.jpg');
      const s02 = await byFile(office, 'S-02.jpg');
      const cl02 = await clientId(office, 'CL-02');
      const ghost = '0f1e2d3c-4b5a-4978-8a6b-5c4d3e2f1a0b';
      await evidence(testInfo, 'U-04 จด id', { s08: { id: s08.id, batchId: s08.batchId }, s02: s02.id, cl02, ghost });

      const call = async (path: string) => {
        const r = await client.get(path);
        const text = await r.text();
        let json: any = null; try { json = JSON.parse(text); } catch { /* binary */ }
        return { path, status: r.status(), ct: r.headers()['content-type'] || '', text: json ? text : `<${text.length} bytes>`, json };
      };
      const leaksCL02 = (x: { text: string }) =>
        [s08.id, 'S-08.jpg', cl02, 'ร้านกาแฟมะลิ', s08.batchId].filter(v => x.text.includes(v)).concat(RE_999.test(x.text) ? ['999.00'] : []);

      // ① S-08 via W12 / W13
      const w12s08 = await call(`/api/receipts/${s08.id}`);
      const w13s08 = await call(`/api/receipts/${s08.id}/image`);
      // ② id that does not exist
      const w12ghost = await call(`/api/receipts/${ghost}`);
      const w13ghost = await call(`/api/receipts/${ghost}/image`);
      // ③ W11 client_id=CL-02
      const w11 = await call(`/api/receipts?client_id=${cl02}`);
      // ④ W19 clientId=CL-02
      const w19 = await call(`/api/reports/categories?clientId=${cl02}&month=2026-11`);
      // ⑤ W9 batch of S-08 · W17 S-08 · W20 · W23
      const w9 = await call(`/api/batches/${s08.batchId}`);
      const w17 = await call(`/api/receipts/${s08.id}/history`);
      const w20 = await call('/api/reports/reconcile');
      const w23 = await call('/api/queue');
      // ⑥ control: own S-02
      const w12s02 = await call(`/api/receipts/${s02.id}`);
      const w13s02 = await call(`/api/receipts/${s02.id}/image`);
      const all = { w12s08, w13s08, w12ghost, w13ghost, w11, w19, w9, w17, w20, w23, w12s02, w13s02 };
      await evidence(testInfo, 'คำตอบทุกคำขอของ U-05', Object.fromEntries(Object.entries(all).map(([k, v]) => [k, { path: v.path, status: v.status, ct: v.ct, body: v.text }])));

      // ①
      for (const [n, x] of [['W12 S-08', w12s08], ['W13 S-08', w13s08]] as const) {
        expect.soft(x.status, `① ${n}: HTTP`).toBe(404);
        expect.soft(x.json?.error, `① ${n}: error`).toBe('not_found');
      }
      // ① vs ② pairwise identical
      expect.soft(w12s08.status, '①/② W12 S-08 กับ id ที่ไม่มีอยู่: สถานะเดียวกัน').toBe(w12ghost.status);
      expect.soft(w12s08.text, '①/② W12: body เหมือนกัน').toBe(w12ghost.text);
      expect.soft(w13s08.status, '①/② W13 S-08 กับ id ที่ไม่มีอยู่: สถานะเดียวกัน').toBe(w13ghost.status);
      expect.soft(w13s08.text, '①/② W13: body เหมือนกัน').toBe(w13ghost.text);
      expect.soft(w13s08.text, '① W13 S-08 ไม่มี image_missing').not.toContain('image_missing');

      // ③ only CL-01 receipts
      const cl01Ids = new Set((await officeReceipts(office, `&client_id=${await clientId(office, 'CL-01')}`)).map(r => r.id));
      expect.soft(w11.status, '③ W11 client_id=CL-02: คืนรายการ (เฉพาะใบ CL-01)').toBe(200);
      const w11ids: string[] = (w11.json?.receipts ?? []).map((r: any) => r.id);
      expect.soft(w11ids.filter(id => !cl01Ids.has(id)), '③ W11: ทุกใบเป็นของ CL-01').toEqual([]);
      expect.soft(w11ids, '③ W11: ไม่มี S-08').not.toContain(s08.id);
      expect.soft(leaksCL02(w11), '③ W11: ไม่มีข้อมูล CL-02 / 999.00').toEqual([]);

      // ④ CL-01 totals or refused, never CL-02
      expect.soft(leaksCL02(w19), '④ W19 clientId=CL-02: ไม่มีข้อมูล CL-02').toEqual([]);
      if (w19.status === 200) {
        testInfo.annotations.push({ type: '④ W19', description: `200 total=${w19.json?.total}` });
        expect.soft(satang(w19.json?.total), '④ W19 ได้ยอดของ CL-01 (1,340.00)').toBe(134000);
      } else {
        testInfo.annotations.push({ type: '④ W19', description: `ถูกปฏิเสธ ${w19.status}` });
        expect.soft([403, 404], '④ W19 ถูกปฏิเสธ').toContain(w19.status);
      }

      // ⑤ all refused (403 or 404)
      for (const [n, x] of [['W9 ชุดของ S-08', w9], ['W17 S-08', w17], ['W20', w20], ['W23', w23]] as const) {
        expect.soft([403, 404], `⑤ ${n}: ถูกปฏิเสธ (ได้ ${x.status})`).toContain(x.status);
      }

      // ⑥ control
      expect.soft(w12s02.status, '⑥ W12 S-02 (ร้านตัวเอง): HTTP').toBe(200);
      expect.soft(w12s02.json?.receipt?.id ?? w12s02.json?.id, '⑥ W12 S-02 ได้ข้อมูล').toBe(s02.id);
      expect.soft(w13s02.status, '⑥ W13 S-02 (ร้านตัวเอง): HTTP').toBe(200);
      expect.soft(w13s02.ct, '⑥ W13 S-02 ได้รูป').toMatch(/^image\/|application\/pdf/);

      // no request returns CL-02 data
      for (const [k, v] of Object.entries(all)) expect.soft(leaksCL02(v), `ไม่มีข้อมูลของ CL-02 ใน ${k}`).toEqual([]);
    } finally {
      await office.dispose(); await client.dispose();
    }
  });

  test('TC-8-02 ไม่มีตัวเลขของใบที่ยังไม่ยืนยัน', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U04');
    const client = await apiAs(M_URL, 'U05');
    const { context, page } = await pageAs(browser, M_URL, 'U05');
    try {
      const s06 = await byFile(office, 'S-06.jpg');
      const st = await portalState(page);
      await shot(testInfo, page, 'U-05 /portal เดือน 2026-11');
      const rows = await portalRows(page, [s06.id]);
      const row = rows[s06.id];
      await evidence(testInfo, 'แถว S-06 + สรุปบน /portal', { row, summary: st.summary, cats: st.cats });

      // row S-06 (by ID): only file name, accepted time, status
      expect.soft(row.visible, 'แถว S-06 (ตาม ID) อยู่บนหน้า').toBe(true);
      expect.soft(row.row, 'แถว S-06 มีชื่อไฟล์').toContain('S-06.jpg');
      expect.soft(row.row, 'แถว S-06 มีเวลาที่รับ').toMatch(/\d{1,2}\/\d{1,2}\/\d{4}\s+\d{1,2}:\d{2}/);
      expect.soft(row.status, 'แถว S-06 สถานะ').toBe(STATUS_WAITING);
      expect.soft(rowExtraDigits(row.row, 'S-06.jpg'), 'แถว S-06 ไม่มีตัวเลขอื่นนอกจากเวลาที่รับ').toBeNull();
      expect.soft(row.row, 'แถว S-06 ไม่มีร้าน/วันที่บนใบ/หมวด').not.toMatch(/ร้านตัวอย่าง|2026-11-15|วัตถุดิบ|ค่าแก๊ส|ค่าน้ำแข็ง|อื่น ๆ/);
      expect.soft(row.totalCount, 'ไม่มี portal-receipt-total ของ S-06').toBe(0);
      expect.soft(st.text, 'หน้า /portal ไม่มี 500.00 / 500 / 50000').not.toMatch(RE_500);

      // JSON W11 / W12 / W19
      const w11r = await client.get('/api/receipts?limit=1000');
      const w11 = await w11r.json();
      const w11s06 = (w11.receipts ?? []).find((r: any) => r.id === s06.id);
      const w12r = await client.get(`/api/receipts/${s06.id}`);
      const w12 = await w12r.json().catch(() => ({}));
      const w19r = await client.get('/api/reports/categories?month=2026-11');
      const w19 = await w19r.json().catch(() => ({}));
      await evidence(testInfo, 'U-05 W11 (S-06) · W12 S-06 · W19 2026-11', { w11status: w11r.status(), w11s06, w12status: w12r.status(), w12, w19status: w19r.status(), w19 });
      expect.soft(w11s06, 'W11 ของลูกค้ามี S-06').toBeTruthy();
      expect.soft(w12r.status(), 'W12 S-06 (ร้านตัวเอง)').toBe(200);
      expect.soft(numberFields(w11s06), 'W11 S-06 ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ').toEqual([]);
      expect.soft(numberFields(w12), 'W12 S-06 ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ').toEqual([]);
      expect.soft(leakedValues(w11s06, RE_500), 'W11 S-06 ไม่มี 500.00 / 500 / 50000').toEqual([]);
      expect.soft(leakedValues(w12, RE_500), 'W12 S-06 ไม่มี 500.00 / 500 / 50000').toEqual([]);
      expect.soft(leakedValues(w11, RE_500), 'W11 ทั้งคำตอบไม่มี 500.00 / 500 / 50000').toEqual([]);
      expect.soft(leakedValues(w19, RE_500), 'W19 ไม่มี 500.00 / 500 / 50000').toEqual([]);

      // summary 1,340.00 (not 1,840.00) · categories 1,340.00
      expect.soft(satang(st.summary), 'portal-summary-total พ.ย. = 1,340.00 (ไม่ใช่ 1,840.00)').toBe(134000);
      const catSum = st.cats.reduce((a, c) => a + satang(c.text), 0);
      expect.soft(catSum, 'ยอดแยกหมวดบนหน้ารวม = 1,340.00').toBe(134000);
      expect.soft(w19r.status(), 'W19 ของลูกค้า').toBe(200);
      expect.soft(satang(w19.total), 'W19 total = 1,340.00').toBe(134000);
      expect.soft((w19.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0), 'W19 ยอดแยกหมวดรวม = 1,340.00').toBe(134000);
    } finally {
      await context.close(); await office.dispose(); await client.dispose();
    }
  });

  test('TC-8-03 ลูกค้าส่งใบเอง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
    test.setTimeout(20 * 60_000);
    const s = await customerUploadsTwo(browser, testInfo);
    try {
      expect.soft(s.readTimeout, '② ทั้ง 2 ID เป็นรอตรวจภายใน 5 นาที (ถ้าไม่ = หมดเวลาอ่าน)').toBe(false);
      const reviewCL01 = (await officeReceipts(s.office, `&client_id=${s.cl01}`)).filter(r => r.status === 'review');
      await evidence(testInfo, '② ใบรอตรวจของ CL-01 (office)', reviewCL01.map(r => ({ id: r.id, fileName: r.fileName, status: r.status })));
      for (const id of s.ids) expect.soft(reviewCL01.map(r => r.id), `② ${id} เป็นรอตรวจ`).toContain(id);
      expect.soft(reviewCL01.length, '② รวมกับ S-06 = 3 ใบรอตรวจของ CL-01').toBe(3);

      // customer refreshes /portal
      await s.cust.page.goto('/portal');
      await s.cust.page.getByTestId('portal-month-input').waitFor({ state: 'visible' });
      await shot(testInfo, s.cust.page, '② U-05 รีเฟรช /portal หลังอ่านเสร็จ');
      await expectNoNumbersForCustomer(s.cust.page, s.client, s.ids, s.files, testInfo, '②');
      const rows = await portalRows(s.cust.page, s.ids);
      s.ids.forEach((id, i) => expect.soft(rows[id].status, `② แถว ${s.files[i]} สถานะ`).toBe(STATUS_WAITING));
    } finally {
      await s.cust.context.close(); await s.st.context.close();
      await s.office.dispose(); await s.staff.dispose(); await s.client.dispose();
    }
  });

  test('TC-8-04 ตัวเลขขึ้นเมื่อยืนยัน และหายเมื่อเปิดกลับ', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
    test.setTimeout(20 * 60_000);
    // ต่อจาก TC-8-03: repeat its setup so this test runs on its own
    const s = await customerUploadsTwo(browser, testInfo);
    const lead = await pageAs(browser, M_URL, 'U03');
    try {
      expect(s.readTimeout, 'ขั้นตั้งต้น (TC-8-03): ทั้ง 2 ใบเป็นรอตรวจภายใน 5 นาที').toBe(false);
      const [id1, id2] = s.ids;
      const cat01 = await categoryId(s.office, 'CAT-01');

      // ① U-01 confirms __001 with CAT-01 through /receipts/[id]
      await s.st.page.goto(`/receipts/${id1}`);
      await s.st.page.getByTestId('category-select').selectOption(cat01);
      await s.st.page.getByTestId('total-checked-checkbox').check();
      await s.st.page.getByTestId('confirm-button').click();
      const c1 = await waitStatus(s.staff, [id1], ['confirmed'], 30_000).catch(e => { throw new Error('① U-01 ยืนยันไม่สำเร็จ: ' + e); });
      await evidence(testInfo, '① W12 __001 หลังยืนยัน (U-01)', c1[0]);
      await shot(testInfo, s.st.page, '① U-01 ยืนยัน __001');

      let st = await portalState(s.cust.page);
      let rows = await portalRows(s.cust.page, s.ids);
      await shot(testInfo, s.cust.page, '① U-05 /portal หลังยืนยัน __001');
      await evidence(testInfo, '① /portal หลังยืนยัน', { summary: st.summary, cats: st.cats, rows });
      expect.soft(rows[id1].totalCount, '① __001 มี portal-receipt-total').toBeGreaterThan(0);
      expect.soft(satang(rows[id1].total), '① __001 แสดงยอด 100.00').toBe(10000);
      expect.soft(rows[id2].totalCount, '① __002 ยังไม่มีตัวเลข (portal-receipt-total)').toBe(0);
      expect.soft(rowExtraDigits(rows[id2].row, s.files[1]), '① แถว __002 ยังไม่มีตัวเลข').toBeNull();
      expect.soft(satang(st.summary), '① สรุป พ.ย. = 1,340.00 + 100.00 = 1,440.00').toBe(144000);
      expect.soft(satang(st.cats.find(c => c.id === cat01)?.text), '① CAT-01 = 1,200.50 + 100.00 = 1,300.50').toBe(130050);
      expect.soft(st.cats.reduce((a, c) => a + satang(c.text), 0), '① รวมหมวด = 1,440.00').toBe(144000);
      const w19a = await (await s.client.get('/api/reports/categories?month=2026-11')).json();
      await evidence(testInfo, '① W19 ของลูกค้า', w19a);
      expect.soft(satang(w19a.total), '① W19 total = 1,440.00').toBe(144000);
      expect.soft(satang((w19a.categories ?? []).find((c: any) => c.id === cat01)?.total), '① W19 CAT-01 = 1,300.50').toBe(130050);
      expect.soft((w19a.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0), '① W19 รวมหมวด = 1,440.00').toBe(144000);

      // ② U-03 reopens __001
      lead.page.on('dialog', d => d.accept().catch(() => undefined));
      await lead.page.goto(`/receipts/${id1}`);
      const reason = lead.page.getByTestId('reopen-reason-input');
      if (await reason.isVisible().catch(() => false)) await reason.fill('ทดสอบ TC-8-04 เปิดใบกลับ');
      await lead.page.getByTestId('reopen-button').click();
      const r2 = await waitStatus(s.staff, [id1], ['review'], 30_000).catch(e => { throw new Error('② U-03 เปิดใบกลับไม่สำเร็จ: ' + e); });
      await evidence(testInfo, '② W12 __001 หลังเปิดกลับ (office)', r2[0]);
      await shot(testInfo, lead.page, '② U-03 เปิด __001 กลับ');

      st = await portalState(s.cust.page);
      await shot(testInfo, s.cust.page, '② U-05 /portal หลังเปิดกลับ');
      await evidence(testInfo, '② /portal หลังเปิดกลับ', { summary: st.summary, cats: st.cats });
      await expectNoNumbersForCustomer(s.cust.page, s.client, [id1], [s.files[0]], testInfo, '② __001');
      expect.soft(satang(st.summary), '② สรุป พ.ย. กลับเป็น 1,340.00').toBe(134000);
      expect.soft(satang(st.cats.find(c => c.id === cat01)?.text), '② CAT-01 = 1,200.50').toBe(120050);
      const w19b = await (await s.client.get('/api/reports/categories?month=2026-11')).json();
      await evidence(testInfo, '② W19 ของลูกค้า', w19b);
      expect.soft(satang(w19b.total), '② W19 total = 1,340.00').toBe(134000);
      expect.soft(satang((w19b.categories ?? []).find((c: any) => c.id === cat01)?.total), '② W19 CAT-01 = 1,200.50').toBe(120050);
    } finally {
      await lead.context.close(); await s.cust.context.close(); await s.st.context.close();
      await s.office.dispose(); await s.staff.dispose(); await s.client.dispose();
    }
  });

  test('TC-8-05 ลูกค้าส่งใบเข้าร้านอื่นไม่ได้ และคิวเต็มจากหน้าลูกค้า', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
    test.setTimeout(15 * 60_000);
    // ①
    await reset(M_URL);
    let office = await apiAs(M_URL, 'U04');
    const client5 = await apiAs(M_URL, 'U05');
    const cl01 = await clientId(office, 'CL-01');
    const cl02 = await clientId(office, 'CL-02');
    const count = async (o: APIRequestContext, cl: string) => (await officeReceipts(o, `&client_id=${cl}`)).length;
    const before = { cl01: await count(office, cl01), cl02: await count(office, cl02) };
    expect.soft(before, '① จำนวนใบตั้งต้น CL-01 = 7 · CL-02 = 1').toEqual({ cl01: 7, cl02: 1 });
    const up = await upload(client5, { clientId: cl02, files: ['ok-100__001.jpg'] });
    const after = { cl01: await count(office, cl01), cl02: await count(office, cl02) };
    const acceptedPath = up.status >= 200 && up.status < 300;
    await evidence(testInfo, '① U-05 W7 clientId=CL-02', { status: up.status, json: up.json, before, after, outcome: acceptedPath ? 'รับแล้วผูกร้านของบัญชี' : 'ปฏิเสธ' });
    testInfo.annotations.push({ type: '① ทางที่เกิด', description: acceptedPath ? `รับ (${up.status}) แล้วผูกร้านของบัญชี` : `ปฏิเสธ (${up.status})` });
    expect.soft(after.cl02, '① ทั้ง 2 ทาง CL-02 ต้องคงเป็น 1').toBe(1);
    if (acceptedPath) expect.soft(after.cl01, '① รับแล้วผูกร้านของบัญชี → CL-01 = 7 + 1 = 8').toBe(8);
    else expect.soft(after.cl01, '① ปฏิเสธ → CL-01 = 7').toBe(7);
    expect.soft([7, 8], '① ผลอยู่ในชุดที่ยอมรับ').toContain(after.cl01);
    await office.dispose(); await client5.dispose();

    // ② queue full from the portal
    await reset(M_URL, { pendingNormal: 309, workersAlive: 2 });
    office = await apiAs(M_URL, 'U04');
    const { context, page } = await pageAs(browser, M_URL, 'U06');
    try {
      const cl02before = await count(office, cl02);
      const r = await portalUpload(page, okFiles(100, 1));
      await shot(testInfo, page, '② U-06 /portal ส่ง 100 ไฟล์');
      const cl02after = await count(office, cl02);
      await evidence(testInfo, '② W7 จาก /portal (U-06 · 100 ไฟล์)', { ...r, cl02before, cl02after });
      expect.soft(r.status, '② 309 + 100 = 409 เกิน 9 → HTTP').toBe(429);
      expect.soft(r.json?.error, '② error').toBe('queue_full');
      expect.soft(r.json?.retryAfterMinutes, '② ปัดขึ้น 9 ÷ 8 = 2 นาที').toBe(2);
      expect.soft(r.errorText ?? '', '② ข้อความบนหน้า "ลองใหม่ในอีก 2 นาที"').toContain('ลองใหม่ในอีก 2 นาที');
      expect.soft(Number(r.json?.accepted ?? 0), '② รับ 0 ใบ (คำตอบ)').toBe(0);
      if (r.acceptedText !== null) expect.soft(int(r.acceptedText), '② portal-accepted-count = 0').toBe(0);
      expect.soft(cl02after - cl02before, '② รับ 0 ใบ (ไม่มีใบใหม่ของ CL-02)').toBe(0);
      const queueKeys: string[] = [];
      const walk = (o: any, p: string) => { if (o && typeof o === 'object') for (const [k, v] of Object.entries(o)) { const kp = p ? `${p}.${k}` : k; if (/pending|limit|queue|capacity|workers/i.test(k)) queueKeys.push(`${kp}=${JSON.stringify(v)}`); walk(v, kp); } };
      walk(r.json, '');
      expect.soft(queueKeys, '② คำตอบไม่มีฟิลด์จำนวนใบค้างหรือเพดานของสำนักงาน [ข้อสมมติของแผน]').toEqual([]);
    } finally {
      await context.close(); await office.dispose();
    }
  });
});
