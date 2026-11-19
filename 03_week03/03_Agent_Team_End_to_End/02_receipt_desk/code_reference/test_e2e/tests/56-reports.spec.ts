/**
 * TEST-PLAN 5.6 รายงานรายเดือน (TC-6-01 … TC-6-07) · runs on the mock stack :3421 (M and A).
 * Expected values come only from the plan's "ผลที่คาดหวัง" column. Money is compared in satang.
 */
import * as fs from 'fs';
import type { APIRequestContext, Browser, Page, TestInfo } from '@playwright/test';
import { test, expect, apiAs, reset, clientId, categoryId, upload, confirm, pageAs, evidence, shot, okFiles, M_URL, CATEGORY_NAME } from './lib/rd';

// ---------------------------------------------------------------- local helpers
/** "1,340.00 บาท" -> 134000 (satang). NaN when no number. */
function satang(s: string | number | null | undefined): number {
  const m = String(s ?? '').replace(/,/g, '').match(/-?\d+(?:\.\d+)?/);
  return m ? Math.round(Number(m[0]) * 100) : NaN;
}
/** First number in a text (commas removed, decimals kept). NaN when none. */
function numOf(s: string | number | null | undefined): number {
  const m = String(s ?? '').replace(/,/g, '').match(/-?\d+(?:\.\d+)?/);
  return m ? Number(m[0]) : NaN;
}
/** Decimals shown in a number text ("2.08" -> 2, "104" -> 0). */
function decimalsOf(s: string): number {
  const m = s.replace(/,/g, '').match(/-?\d+(?:\.(\d+))?/);
  return m && m[1] ? m[1].length : 0;
}

type Csv = { text: string; header: string[]; rows: Record<string, string>[]; bom: boolean };
/** Minimal RFC-4180 CSV parser (quotes, commas and newlines inside quotes, optional BOM). */
function parseCsv(raw: string): Csv {
  const bom = raw.charCodeAt(0) === 0xfeff;
  const text = bom ? raw.slice(1) : raw;
  const out: string[][] = []; let row: string[] = []; let cell = ''; let q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; }
      else cell += ch;
    } else if (ch === '"') q = true;
    else if (ch === ',') { row.push(cell); cell = ''; }
    else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++;
      row.push(cell); cell = '';
      if (row.some(c => c !== '')) out.push(row);
      row = [];
    } else cell += ch;
  }
  row.push(cell); if (row.some(c => c !== '')) out.push(row);
  const header = (out.shift() ?? []).map(h => h.trim());
  const rows = out.map(r => Object.fromEntries(header.map((h, i) => [h, (r[i] ?? '').trim()])));
  return { text: raw, header, rows, bom };
}
function csvSum(csv: Csv): number { return csv.rows.reduce((a, r) => a + satang(r.total), 0); }
function csvFiles(csv: Csv): string[] { return csv.rows.map(r => r.file_name).sort(); }

type Report = { total: string; count: string; csv: Csv | null; csvVia: string };

/**
 * On /reports: choose client + month, click preview, read report-total / report-receipt-count,
 * then export the CSV through report-export-button (download event; falls back to the link's href).
 */
async function runReport(page: Page, testInfo: TestInfo, clientUuid: string, month: string, label: string): Promise<Report> {
  if (!page.url().includes('/reports')) await page.goto('/reports');
  await page.getByTestId('report-client-select').selectOption(clientUuid);
  await page.getByTestId('report-month-input').fill(month);
  const resp = page.waitForResponse(r => r.url().includes('/api/reports'), { timeout: 15_000 }).catch(() => null);
  await page.getByTestId('report-preview-button').click();
  await resp;
  await expect(page.getByTestId('report-total'), `${label}: report-total แสดงหลังกดดูตัวอย่าง`).toBeVisible();
  await page.waitForTimeout(300);
  const total = (await page.getByTestId('report-total').innerText()).trim();
  const count = (await page.getByTestId('report-receipt-count').innerText()).trim();
  await shot(testInfo, page, `${label} preview`);

  let csv: Csv | null = null; let csvVia = 'none';
  const btn = page.getByTestId('report-export-button');
  try {
    const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 15_000 }), btn.click()]);
    const p = await dl.path();
    csv = parseCsv(fs.readFileSync(p!, 'utf8')); csvVia = `download ${dl.suggestedFilename()}`;
  } catch {
    const href = await btn.getAttribute('href').catch(() => null);
    if (href) {
      const r = await page.request.get(href);
      expect.soft(r.status(), `${label}: W18 via export link href`).toBe(200);
      csv = parseCsv(await r.text()); csvVia = `href ${href}`;
      testInfo.annotations.push({ type: 'note', description: `${label}: export button gave no download event; CSV read from its href` });
    }
  }
  expect.soft(csv, `${label}: ได้ไฟล์ CSV จาก report-export-button`).not.toBeNull();
  if (csv) {
    await testInfo.attach(`${label}.csv`, { body: Buffer.from(csv.text, 'utf8'), contentType: 'text/csv' });
    expect.soft(csv.header, `${label}: CSV มีคอลัมน์ total`).toContain('total');
  }
  await evidence(testInfo, `${label} report`, { clientUuid, month, total, count, csvVia, csvRows: csv?.rows ?? null });
  return { total, count, csv, csvVia };
}

/** Soft checks: page total / count and CSV sum / row count equal the plan's expected values. */
function expectReport(r: Report, label: string, expSatang: number, expCount: number) {
  expect.soft(satang(r.total), `${label}: report-total (${r.total})`).toBe(expSatang);
  expect.soft(numOf(r.count), `${label}: report-receipt-count (${r.count})`).toBe(expCount);
  if (r.csv) {
    expect.soft(csvSum(r.csv), `${label}: ผลรวมคอลัมน์ total ใน CSV (สตางค์)`).toBe(expSatang);
    expect.soft(r.csv.rows.length, `${label}: จำนวนแถวใน CSV`).toBe(expCount);
  }
}

async function ownerReports(browser: Browser) {
  const s = await pageAs(browser, M_URL, 'U04');
  await s.page.goto('/reports');
  return s;
}

/** W9 poll (does not open any receipt) until every receipt of the batch is `review`. */
async function waitBatchReview(ctx: APIRequestContext, batchId: string, n: number, timeoutMs = 120_000) {
  const end = Date.now() + timeoutMs;
  for (;;) {
    const j = await (await ctx.get(`/api/batches/${batchId}`)).json();
    const rs: any[] = j.receipts ?? [];
    if (rs.length === n && rs.every(r => r.status === 'review')) return rs;
    if (Date.now() > end) throw new Error('timeout waiting for review: ' + rs.map(r => `${r.fileName}=${r.status}`).join(', '));
    await new Promise(r => setTimeout(r, 1500));
  }
}

const S = (code: string) => `${code}.jpg`; // seed receipts are named S-0x.jpg
const CL01_SEED = ['S-01', 'S-02', 'S-03', 'S-04', 'S-05', 'S-06', 'S-07'].map(S);

// ---------------------------------------------------------------- tests
test.describe('5.6 รายงานรายเดือน', () => {

  test('TC-6-01 สรุป พ.ย. 2026 ของ CL-01 · 1,340.00 บาท 4 ใบ', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U04');
    const cl01 = await clientId(office, 'CL-01');
    const { context, page } = await ownerReports(browser);
    try {
      const r = await runReport(page, testInfo, cl01, '2026-11', 'CL-01 2026-11');
      expectReport(r, 'CL-01 2026-11', 134000, 4);
      if (r.csv) {
        const files = csvFiles(r.csv);
        expect.soft(files, 'CSV = S-02, S-03, S-04, S-07').toEqual([S('S-02'), S('S-03'), S('S-04'), S('S-07')].sort());
        expect.soft(files, 'ไม่มี S-06 (500.00 ยังไม่ยืนยัน)').not.toContain(S('S-06'));
        expect.soft(files, 'มี S-07 (วันที่บนใบ 2026-11-10 แม้อัปโหลด 2026-12-02)').toContain(S('S-07'));
      }
    } finally { await context.close(); await office.dispose(); }
  });

  test('TC-6-02 ใบที่ขอบเดือน ต.ค. / ธ.ค. · 150.00 และ 75.25', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U04');
    const cl01 = await clientId(office, 'CL-01');
    const { context, page } = await ownerReports(browser);
    try {
      const oct = await runReport(page, testInfo, cl01, '2026-10', 'CL-01 2026-10');
      expectReport(oct, 'CL-01 2026-10', 15000, 1);
      if (oct.csv) expect.soft(csvFiles(oct.csv), 'ต.ค. = S-01 (2026-10-31)').toEqual([S('S-01')]);

      const dec = await runReport(page, testInfo, cl01, '2026-12', 'CL-01 2026-12');
      expectReport(dec, 'CL-01 2026-12', 7525, 1);
      if (dec.csv) expect.soft(csvFiles(dec.csv), 'ธ.ค. = S-05 (2026-12-01)').toEqual([S('S-05')]);

      const nov = await runReport(page, testInfo, cl01, '2026-11', 'CL-01 2026-11');
      if (nov.csv) expect.soft(csvFiles(nov.csv), 'S-05 ไม่อยู่ใน พ.ย.').not.toContain(S('S-05'));
      if (nov.csv) expect.soft(csvFiles(nov.csv), 'S-01 ไม่อยู่ใน พ.ย.').not.toContain(S('S-01'));
    } finally { await context.close(); await office.dispose(); }
  });

  test('TC-6-03 ร้านอื่น และร้านที่ไม่มีใบ · CL-02 999.00 · CL-03 0.00', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const office = await apiAs(M_URL, 'U04');
    const cl02 = await clientId(office, 'CL-02');
    const cl03 = await clientId(office, 'CL-03');
    const { context, page } = await ownerReports(browser);
    try {
      const r2 = await runReport(page, testInfo, cl02, '2026-11', 'CL-02 2026-11');
      expectReport(r2, 'CL-02 2026-11', 99900, 1);
      if (r2.csv) {
        expect.soft(csvFiles(r2.csv), 'CL-02 = S-08').toEqual([S('S-08')]);
        expect.soft(csvFiles(r2.csv).filter(f => CL01_SEED.includes(f)), 'CL-02: ไม่มีใบของ CL-01 ปน').toEqual([]);
      }

      const r3 = await runReport(page, testInfo, cl03, '2026-11', 'CL-03 2026-11');
      expectReport(r3, 'CL-03 2026-11', 0, 0);
      if (r3.csv) {
        expect.soft(r3.csv.header.length, 'CL-03: CSV มีหัวตาราง').toBeGreaterThan(0);
        expect.soft(r3.csv.rows.length, 'CL-03: CSV มีแต่หัวตาราง').toBe(0);
      }
      // the same file through W18 directly: must be 200 (not an error)
      const api = await office.get(`/api/reports/monthly?clientId=${cl03}&month=2026-11`);
      const body = await api.text();
      await evidence(testInfo, 'W18 CL-03 2026-11 (API)', { status: api.status(), body });
      expect.soft(api.status(), 'CL-03: W18 ตอบ 200 ไม่ error').toBe(200);
      expect.soft(parseCsv(body).rows.length, 'CL-03: W18 มีแต่หัวตาราง').toBe(0);
    } finally { await context.close(); await office.dispose(); }
  });

  test('TC-6-04 ใบที่ยืนยันใหม่เข้าเดือนตามวันที่บนใบ · พ.ย. 1,440.00 ธ.ค. 175.25', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const staff = await apiAs(M_URL, 'U01');
    const owner = await apiAs(M_URL, 'U04');
    const cl01 = await clientId(staff, 'CL-01');
    const cat01 = await categoryId(staff, 'CAT-01');
    const { context, page } = await ownerReports(browser);
    try {
      const up = await upload(staff, { clientId: cl01, files: okFiles(2) });
      await evidence(testInfo, 'W7 upload', up);
      expect(up.status, 'W7 upload 2 files').toBeLessThan(300);
      const rs = await waitBatchReview(staff, up.json.batchId, 2);
      const first = rs.find(r => r.fileName === 'ok-100__001.jpg');
      const second = rs.find(r => r.fileName === 'ok-100__002.jpg');
      expect(first && second, 'both receipts in the batch').toBeTruthy();
      // open each receipt's detail before confirming (FR-12)
      for (const r of [first, second]) await staff.get(`/api/receipts/${r.id}`);

      const c1 = await confirm(staff, first.id, { totalChecked: true, categoryId: cat01 });
      const p2 = await staff.patch(`/api/receipts/${second.id}`, { data: { receiptDate: '2026-12-01' } });
      const p2j = await p2.json().catch(() => ({}));
      const c2 = await confirm(staff, second.id, { totalChecked: true, categoryId: cat01 });
      await evidence(testInfo, 'W15/W14 results', { confirm1: c1, patch2: { status: p2.status(), json: p2j }, confirm2: c2 });
      expect(c1.status, 'ยืนยันใบแรก').toBe(200);
      expect(p2.status(), 'แก้วันที่ใบสองเป็น 2026-12-01').toBe(200);
      expect(c2.status, 'ยืนยันใบสอง').toBe(200);

      const nov = await runReport(page, testInfo, cl01, '2026-11', 'CL-01 2026-11 after');
      expectReport(nov, 'CL-01 2026-11 after', 144000, 5);
      if (nov.csv) {
        expect.soft(csvFiles(nov.csv), 'พ.ย. มีใบแรก ok-100__001').toContain('ok-100__001.jpg');
        expect.soft(csvFiles(nov.csv), 'พ.ย. ไม่มีใบสอง (วันที่ที่แก้แล้ว 2026-12-01 ไม่ใช่ 2026-11-18)').not.toContain('ok-100__002.jpg');
      }
      const dec = await runReport(page, testInfo, cl01, '2026-12', 'CL-01 2026-12 after');
      expectReport(dec, 'CL-01 2026-12 after', 17525, 2);
      if (dec.csv) expect.soft(csvFiles(dec.csv), 'ธ.ค. = S-05 + ใบสอง').toEqual([S('S-05'), 'ok-100__002.jpg'].sort());
    } finally { await context.close(); await staff.dispose(); await owner.dispose(); }
  });

  test('TC-6-05 ยอดแยกหมวด พ.ย. ของ CL-01 · หน้าลูกค้าและ W19 ตรงกัน', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const owner = await apiAs(M_URL, 'U04');
    const cl01 = await clientId(owner, 'CL-01');
    const expected: Record<string, number> = { 'CAT-01': 120050, 'CAT-02': 4000, 'CAT-03': 9950, 'CAT-04': 0 };
    const w19r = await owner.get(`/api/reports/categories?month=2026-11&clientId=${cl01}`);
    const w19 = await w19r.json().catch(() => ({}));
    await evidence(testInfo, 'W19 CL-01 2026-11 (U-04)', { status: w19r.status(), json: w19 });
    expect(w19r.status(), 'W19 status').toBe(200);
    const ids: Record<string, string> = {};
    for (const code of Object.keys(expected)) {
      const c = (w19.categories ?? []).find((x: any) => x.name === CATEGORY_NAME[code]);
      expect.soft(c, `W19 มีหมวด ${code} ${CATEGORY_NAME[code]}`).toBeTruthy();
      if (!c) continue;
      ids[code] = c.id;
      expect.soft(satang(c.total), `W19 ${code} ${CATEGORY_NAME[code]}`).toBe(expected[code]);
    }
    const w19Sum = (w19.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0);
    expect.soft(w19Sum, 'W19 รวมทุกหมวด = 1,340.00 (= TC-6-01)').toBe(134000);
    expect.soft(satang(w19.total), 'W19 total = 1,340.00').toBe(134000);

    const { context, page } = await pageAs(browser, M_URL, 'U05');
    try {
      await page.goto('/portal');
      const resp = page.waitForResponse(r => r.url().includes('/api/reports/categories'), { timeout: 10_000 }).catch(() => null);
      await page.getByTestId('portal-month-input').fill('2026-11');
      await page.getByTestId('portal-month-input').press('Enter').catch(() => undefined);
      await resp;
      await page.waitForTimeout(500);
      const portal: Record<string, string | null> = {};
      let portalSum = 0;
      for (const code of Object.keys(expected)) {
        const loc = ids[code] ? page.getByTestId(`portal-category-total-${ids[code]}`) : null;
        const visible = loc ? await loc.isVisible().catch(() => false) : false;
        portal[code] = visible ? (await loc!.innerText()).trim() : null;
        expect.soft(portal[code], `portal-category-total-{id} ของ ${code} แสดงบนหน้า`).not.toBeNull();
        if (portal[code] === null) continue;
        expect.soft(satang(portal[code]), `หน้าลูกค้า ${code} ${CATEGORY_NAME[code]}`).toBe(expected[code]);
        const apiCat = (w19.categories ?? []).find((x: any) => x.id === ids[code]);
        expect.soft(satang(portal[code]), `${code}: หน้าลูกค้า = W19`).toBe(satang(apiCat?.total));
        portalSum += satang(portal[code]);
      }
      expect.soft(portalSum, 'หน้าลูกค้า รวมทุกหมวด = 1,340.00').toBe(134000);
      await evidence(testInfo, 'portal category totals (U-05)', portal);
      await shot(testInfo, page, 'portal 2026-11 U-05');
    } finally { await context.close(); await owner.dispose(); }
  });

  test('TC-6-06 เวลาตรวจเฉลี่ยต่อชุด · (30 + 50) ÷ 2 = 40 วินาที', { tag: ['@P3', '@M'] }, async ({ browser }, testInfo) => {
    test.setTimeout(10 * 60_000);
    await reset(M_URL);
    const staff = await apiAs(M_URL, 'U01');
    const cl01 = await clientId(staff, 'CL-01');
    const cat04 = await categoryId(staff, 'CAT-04');
    const up = await upload(staff, { clientId: cl01, files: okFiles(2) });
    await evidence(testInfo, 'W7 upload', up);
    expect(up.status, 'W7 upload 2 files as one batch').toBeLessThan(300);
    const batchId: string = up.json.batchId;
    const rs = await waitBatchReview(staff, batchId, 2);
    const order = ['ok-100__001.jpg', 'ok-100__002.jpg'].map(n => rs.find(r => r.fileName === n));
    expect(order.every(Boolean), 'both receipts in the batch').toBeTruthy();

    const u01 = await pageAs(browser, M_URL, 'U01');
    const measured: { file: string; seconds: number; status: number | null }[] = [];
    try {
      for (const [i, holdS] of [[0, 30], [1, 50]] as const) {
        const r = order[i];
        const t0 = Date.now();
        await u01.page.goto(`/receipts/${r.id}`);
        await expect(u01.page.getByTestId('confirm-button')).toBeVisible();
        await u01.page.getByTestId('category-select').selectOption(cat04);
        await u01.page.getByTestId('total-checked-checkbox').check();
        const wait = t0 + holdS * 1000 - Date.now();
        if (wait > 0) await u01.page.waitForTimeout(wait);
        if (i === 1) await shot(testInfo, u01.page, 'receipt 2 before confirm (50 s)');
        const resp = u01.page.waitForResponse(x => x.url().includes(`/api/receipts/${r.id}/confirm`), { timeout: 20_000 }).catch(() => null);
        await u01.page.getByTestId('confirm-button').click();
        const res = await resp;
        measured.push({ file: r.fileName, seconds: (Date.now() - t0) / 1000, status: res ? res.status() : null });
        expect(res?.status(), `ยืนยัน ${r.fileName} ผ่านหน้าเว็บ`).toBe(200);
      }
      await evidence(testInfo, 'held times (open -> confirm click)', measured);

      // U-01 (staff) calls W21 -> rejected
      const w21Staff = await staff.get('/api/reports/review-time');
      await evidence(testInfo, 'W21 as U-01', { status: w21Staff.status(), body: await w21Staff.text() });
      expect.soft(w21Staff.status(), 'U-01 เรียก W21 ถูกปฏิเสธ (403)').toBe(403);

      // U-03 and U-04 see the same value on /insights; batch average = 40 s ± 3
      const seen: Record<string, { page: number; api: number; apiRow: any }> = {};
      for (const user of ['U03', 'U04'] as const) {
        const s = await pageAs(browser, M_URL, user);
        try {
          await s.page.goto('/insights');
          const table = s.page.getByTestId('review-time-table');
          await expect(table).toBeVisible();
          const row = table.locator('tbody tr', { hasText: 'ร้านข้าวแกงสมชาย' }).first();
          let pageVal = NaN;
          if (await row.isVisible().catch(() => false)) {
            const cells = await row.locator('td').allInnerTexts();
            pageVal = numOf(cells[3]); // ชุด | ลูกค้า | ใบที่ยืนยัน | เฉลี่ย (วินาที) | ...
            await evidence(testInfo, `${user} /insights batch row`, cells);
          }
          await shot(testInfo, s.page, `${user} /insights review time`);
          const w21 = await (await s.context.request.get('/api/reports/review-time')).json().catch(() => ({}));
          await evidence(testInfo, `W21 as ${user}`, w21);
          const apiRow = (w21.batches ?? []).find((b: any) => b.batchId === batchId || b.id === batchId);
          const apiVal = numOf(apiRow?.averageSeconds ?? apiRow?.avgSeconds ?? apiRow?.average);
          seen[user] = { page: pageVal, api: apiVal, apiRow };
          expect.soft(pageVal, `${user}: /insights แถวของชุดนี้ เฉลี่ย = 40 ± 3 วินาที`).toBeGreaterThanOrEqual(37);
          expect.soft(pageVal, `${user}: /insights แถวของชุดนี้ เฉลี่ย = 40 ± 3 วินาที`).toBeLessThanOrEqual(43);
          expect.soft(apiVal, `${user}: W21 batches[ชุดนี้] เฉลี่ย = 40 ± 3 วินาที`).toBeGreaterThanOrEqual(37);
          expect.soft(apiVal, `${user}: W21 batches[ชุดนี้] เฉลี่ย = 40 ± 3 วินาที`).toBeLessThanOrEqual(43);
        } finally { await s.context.close(); }
      }
      expect.soft(seen.U03?.page, 'U-03 และ U-04 เห็นค่าเดียวกันบน /insights').toBe(seen.U04?.page);
      expect.soft(seen.U03?.api, 'U-03 และ U-04 ได้ค่าเดียวกันจาก W21').toBe(seen.U04?.api);
    } finally { await u01.context.close(); await staff.dispose(); }
  });

  test('TC-6-07 รายงาน GPU 1 เทียบ 2 ใบ · ต้องมีตารางและสูตรถูก', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
    await reset(M_URL);
    const step12 = { t1: 116.2, t2: 56.0 }; // results/capacity/summary.json mean_t_1worker_s / mean_t_2workers_s
    const step12Speedup = step12.t1 / step12.t2; // 2.075 -> shown 2.08 · efficiency 103.75% -> 104% -> คุ้ม
    const { context, page } = await pageAs(browser, M_URL, 'U04');
    try {
      await page.goto('/insights');
      const table = page.getByTestId('gpu-table');
      await expect.soft(table, 'gpu-table แสดง').toBeVisible();
      const w22 = await (await context.request.get('/api/reports/gpu')).json().catch(() => ({}));
      await evidence(testInfo, 'W22 as U-04', w22);

      const rows = await table.locator('tbody tr').evaluateAll(trs => trs.map(tr => [...tr.querySelectorAll('td,th')].map(td => (td as HTMLElement).innerText.trim())));
      const txt = async (id: string) => (await page.getByTestId(id).innerText().catch(() => '')).trim();
      const shown = { speedup: await txt('gpu-speedup'), efficiency: await txt('gpu-efficiency'), costPer100: await txt('gpu-cost-per-100'), verdict: await txt('gpu-verdict') };
      await evidence(testInfo, '/insights GPU table + cards', { rows, shown });
      await shot(testInfo, page, 'U-04 /insights GPU');

      // must have the table WITH values (empty / "ยังไม่มีข้อมูล" = fail FR-30)
      const row1 = rows.find(r => r[0] === '1');
      const row2 = rows.find(r => r[0] === '2');
      // columns: จำนวน GPU | ใบ | เวลา (นาที) | ใบต่อนาที | ค่าเช่า (บาท) | บาทต่อ 100 ใบ | วัดเมื่อ
      const hasValues = (r?: string[]) => !!r && r.length >= 6 && !Number.isNaN(numOf(r[1])) && !Number.isNaN(numOf(r[2])) && !Number.isNaN(numOf(r[3])) && !Number.isNaN(numOf(r[4])) && !Number.isNaN(numOf(r[5]));
      expect.soft(hasValues(row1), `แถว GPU 1 ใบ มีค่า ใบ·เวลา·ใบต่อนาที·ค่าเช่า·บาทต่อ 100 ใบ (ได้ ${JSON.stringify(row1)})`).toBe(true);
      expect.soft(hasValues(row2), `แถว GPU 2 ใบ มีค่า ใบ·เวลา·ใบต่อนาที·ค่าเช่า·บาทต่อ 100 ใบ (ได้ ${JSON.stringify(row2)})`).toBe(true);
      expect.soft(shown.verdict, 'gpu-verdict ไม่ใช่ "ยังไม่มีข้อมูล/ผลวัด"').not.toMatch(/ยังไม่มี/);
      expect.soft(numOf(shown.speedup), `gpu-speedup เป็นตัวเลข (ได้ "${shown.speedup}")`).not.toBeNaN();
      expect.soft(numOf(shown.efficiency), `gpu-efficiency เป็นตัวเลข (ได้ "${shown.efficiency}")`).not.toBeNaN();
      expect.soft(numOf(shown.costPer100), `gpu-cost-per-100 เป็นตัวเลข (ได้ "${shown.costPer100}")`).not.toBeNaN();

      // recompute from the rows (only when they exist)
      if (hasValues(row1) && hasValues(row2)) {
        const calc = (r: string[]) => ({ n: numOf(r[1]), min: numOf(r[2]), rate: numOf(r[3]), rent: numOf(r[4]), per100: numOf(r[5]) });
        const a = calc(row1!), b = calc(row2!);
        const half = (s: string) => 0.5 * Math.pow(10, -decimalsOf(s)) + 1e-9; // display rounding tolerance
        expect.soft(Math.abs(a.rate - a.n / a.min), 'GPU 1: ใบต่อนาที = ใบ ÷ เวลา').toBeLessThanOrEqual(half(row1![3]) + 0.05);
        expect.soft(Math.abs(b.rate - b.n / b.min), 'GPU 2: ใบต่อนาที = ใบ ÷ เวลา').toBeLessThanOrEqual(half(row2![3]) + 0.05);
        expect.soft(Math.abs(a.per100 - a.rent / a.n * 100), 'GPU 1: บาทต่อ 100 ใบ = ค่าเช่า ÷ ใบ × 100').toBeLessThanOrEqual(half(row1![5]) + 0.01);
        expect.soft(Math.abs(b.per100 - b.rent / b.n * 100), 'GPU 2: บาทต่อ 100 ใบ = ค่าเช่า ÷ ใบ × 100').toBeLessThanOrEqual(half(row2![5]) + 0.01);
        const speedup = (b.n / b.min) / (a.n / a.min); // value before rounding
        const eff = speedup / 2 * 100;
        expect.soft(Math.abs(numOf(shown.speedup) - speedup), `gpu-speedup = อัตรา 2 ÷ อัตรา 1 = ${speedup.toFixed(4)}`).toBeLessThanOrEqual(half(shown.speedup));
        expect.soft(Math.abs(numOf(shown.efficiency) - eff), `gpu-efficiency = Speedup ÷ 2 = ${eff.toFixed(2)}%`).toBeLessThanOrEqual(half(shown.efficiency));
        expect.soft(Math.abs(numOf(shown.costPer100) - b.rent / b.n * 100), 'gpu-cost-per-100 (2 GPU) = ค่าเช่า ÷ ใบ × 100').toBeLessThanOrEqual(half(shown.costPer100) + 0.01);
        if (speedup >= 1.6) {
          expect.soft(shown.verdict, `Speedup ${speedup.toFixed(4)} ≥ 1.6 → คุ้ม`).toMatch(/คุ้ม/);
          expect.soft(shown.verdict, `Speedup ${speedup.toFixed(4)} ≥ 1.6 → ไม่ใช่ "ไม่คุ้ม"`).not.toMatch(/ไม่คุ้ม/);
        } else {
          testInfo.annotations.push({ type: 'note', description: `Speedup ${speedup.toFixed(4)} < 1.6: verdict depends on SLO of 1 vs 2 GPU (not shown in the row); shown "${shown.verdict}"` });
        }
      }

      // compare with the step-12 measurement (116.2 vs 56.0 -> 2.075 shown 2.08 · 103.75% shown 104% · คุ้ม)
      await evidence(testInfo, 'step-12 reference', { ...step12, speedup: step12Speedup, efficiencyPct: step12Speedup / 2 * 100 });
      expect.soft(shown.speedup, 'gpu-speedup = ผลขั้นที่ 12 (แสดง 2.08)').toMatch(/2\.08/);
      expect.soft(Math.round(numOf(shown.efficiency)), 'gpu-efficiency = ผลขั้นที่ 12 (แสดง 104%)').toBe(104);
      expect.soft(shown.verdict, 'gpu-verdict = คุ้ม (ผลขั้นที่ 12)').toMatch(/คุ้ม/);
      expect.soft(shown.verdict, 'gpu-verdict ไม่ใช่ ไม่คุ้ม').not.toMatch(/ไม่คุ้ม/);
    } finally { await context.close(); }
  });
});
