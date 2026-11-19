/**
 * Test Plan section 5.2 · ผลอ่านและธงไม่แน่ใจ (TC-2-01 … TC-2-08)
 *
 * M cases (2-01 … 2-06): reset ตั้งต้น · U-02 uploads the files of the case for CL-01 · note the ids on the
 * batch page · wait for "รอตรวจ" · open /receipts/{id} and read flag-low-confidence / flag-mismatch
 * ("เหตุผลของธง" = the text the user sees in the flag element).
 * R cases (2-07, 2-08): E6 preparation inside the test, then real receipts for CL-03 on :3420.
 * Expected values come only from the plan's "ผลที่คาดหวัง" column. Money is compared in satang (integers).
 */
import * as fs from 'fs';
import * as path from 'path';
import type { APIRequestContext, Browser, BrowserContext, Page, TestInfo } from '@playwright/test';
import {
  test, expect, apiAs, reset, clientId, upload, waitStatus, queue, pageAs, evidence, shot, pendingAP,
  M_URL, R_URL, REAL_IMAGES, DATA,
} from './lib/rd';

// ---------------------------------------------------------------- local helpers

/** '1,234.50' / '100.00 บาท' / 100 -> satang integer (null when there is no number). */
function toSatang(v: unknown): number | null {
  if (v === null || v === undefined) return null;
  const m = String(v).replace(/,/g, '').match(/-?\d+(?:\.\d+)?/);
  return m ? Math.round(Number(m[0]) * 100) : null;
}
/** All numbers with 2 decimals in a text, as satang (e.g. reason "100.00 / 98.99 / 1.01"). */
function moneyInText(t: string): number[] {
  return (t.replace(/,/g, '').match(/-?\d+\.\d{2}\b/g) || []).map(x => Math.round(Number(x) * 100));
}

type Prep = { api: APIRequestContext; context: BrowserContext; page: Page; ids: Record<string, string>; batchId: string; up: any };

/**
 * Common steps of 5.2 (M): reset ตั้งต้น · U-02 uploads `files` for CL-01 · ids noted from the batch page ·
 * wait until every receipt is "รอตรวจ".
 */
async function prepareM(browser: Browser, testInfo: TestInfo, files: string[]): Promise<Prep> {
  await reset(M_URL);
  const api = await apiAs(M_URL, 'U02');
  const cl = await clientId(api, 'CL-01');
  const up = await upload(api, { clientId: cl, files });
  await evidence(testInfo, 'W7 upload', { status: up.status, json: up.json });
  expect(up.status, `W7 upload ${files.join(', ')}`).toBeLessThan(300);
  expect(up.json.accepted, 'accepted count').toBe(files.length);

  const ids: Record<string, string> = {};
  for (const r of up.json.receipts || []) ids[r.fileName] = r.id;
  for (const f of files) expect(ids[f], `receipt id of ${f}`).toBeTruthy();

  const { context, page } = await pageAs(browser, M_URL, 'U02');
  // "จด ID ของใบจากหน้าชุด": every id must be listed on the batch page
  await page.goto(`/batches/${up.json.batchId}`);
  for (const f of files) await expect(page.getByTestId(`receipt-row-${ids[f]}`), `row of ${f} on batch page`).toBeVisible();

  const done = await waitStatus(api, files.map(f => ids[f]), ['review', 'unreadable', 'confirmed'], 300_000);
  await evidence(testInfo, 'W12 receipts after reading', done);
  for (const r of done) expect.soft(r.status, `${r.fileName} status = รอตรวจ (review)`).toBe('review');
  await page.reload();
  await shot(testInfo, page, 'batch page after reading');
  return { api, context, page, ids, batchId: up.json.batchId, up };
}

type ReviewView = {
  merchant: string; date: string; total: string; itemsSum: string;
  items: { name: string; price: string }[];
  low: { present: boolean; text: string }; mismatch: { present: boolean; text: string };
};

/** Open /receipts/{id} (no typing) and read what the user sees. */
async function openReview(page: Page, id: string): Promise<ReviewView> {
  await page.goto(`/receipts/${id}`);
  await expect(page.getByTestId('receipt-status')).toBeVisible();
  await expect(page.getByTestId('field-total-input')).toBeVisible();
  await expect(page.getByTestId('items-sum')).toBeVisible();
  const rows = await page.locator('[data-testid^="item-name-input-"]').count();
  const items: { name: string; price: string }[] = [];
  for (let i = 1; i <= rows; i++) {
    items.push({
      name: await page.getByTestId(`item-name-input-${i}`).inputValue(),
      price: await page.getByTestId(`item-price-input-${i}`).inputValue(),
    });
  }
  const flag = async (tid: string) => {
    const l = page.getByTestId(tid);
    const present = (await l.count()) > 0 && await l.first().isVisible();
    return { present, text: present ? (await l.first().innerText()).trim() : '' };
  };
  return {
    merchant: await page.getByTestId('field-merchant-input').inputValue(),
    date: await page.getByTestId('field-date-input').inputValue(),
    total: await page.getByTestId('field-total-input').inputValue(),
    itemsSum: (await page.getByTestId('items-sum').innerText()).trim(),
    items,
    low: await flag('flag-low-confidence'),
    mismatch: await flag('flag-mismatch'),
  };
}

/** E6 · preparation before every R test (inside the test). Returns an API session of U-02 on :3420. */
async function prepareR(testInfo: TestInfo, files: string[]) {
  for (const f of files) expect(fs.existsSync(f), `file exists: ${path.basename(f)}`).toBe(true);
  await reset(R_URL);
  const api = await apiAs(R_URL, 'U02');
  const q = await queue(api);
  await evidence(testInfo, 'E6 W23 queue after reset', q);
  expect(q?.normal?.pending, 'E6: ใบงานปกติค้าง 0').toBe(0);
  expect(q?.urgent?.usedToday, 'E6: งานด่วนวันนี้ 0 / 5').toBe(0);
  expect(q?.workers?.alive, 'E6: workersAlive 2').toBe(2);
  testInfo.annotations.push({ type: 'E6', description: 'gateway queue (GET /v1/queue) not checked from the test (API key of the gateway is not used by the suite); W23 pending 0 · urgent 0 · workers 2 checked' });
  return api;
}

const isFlagged = (r: any) => !!(r?.flags && (r.flags.flagged || r.flags.lowConfidence || r.flags.mismatch));

// ---------------------------------------------------------------- tests

test('TC-2-01 อ่านครบ 5 ช่อง ใบปกติ', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  const f = 'ok-100__001.jpg';
  const p = await prepareM(browser, testInfo, [f]);
  try {
    const v = await openReview(p.page, p.ids[f]);
    await shot(testInfo, p.page, 'review page ok-100__001');
    await evidence(testInfo, 'review page values', v);

    expect.soft(v.merchant, 'ชื่อร้าน').toBe('ร้านตัวอย่าง');
    expect.soft(v.date, 'วันที่').toBe('2026-11-18');
    expect.soft(v.items.length, 'รายการ 3 บรรทัด').toBe(3);
    const want = [4500, 3000, 2500];
    want.forEach((sat, i) => {
      expect.soft(v.items[i]?.name?.trim() ?? '', `ชื่อรายการบรรทัด ${i + 1} ไม่ว่าง`).not.toBe('');
      expect.soft(toSatang(v.items[i]?.price), `ราคาบรรทัด ${i + 1}`).toBe(sat);
    });
    expect.soft(toSatang(v.total), 'ยอดรวม 100.00').toBe(10000);
    expect.soft(toSatang(v.itemsSum), 'items-sum = 45.00 + 30.00 + 25.00 = 100.00').toBe(4500 + 3000 + 2500);
    expect.soft(v.low.present, 'ไม่ติดธง "ไม่แน่ใจยอดรวม"').toBe(false);
    expect.soft(v.mismatch.present, 'ไม่ติดธง "ยอดไม่ตรงรายการ"').toBe(false);
    pendingAP(testInfo, 'AP-06', `ชื่อรายการที่ได้: ${v.items.map(i => `"${i.name}" ${i.price}`).join(' · ')}`);
  } finally { await p.context.close(); await p.api.dispose(); }
});

test('TC-2-02 ความมั่นใจต่ำกว่า 0.90 ติดธง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  const files = ['conf-089.jpg', 'conf-08999.jpg'];
  const p = await prepareM(browser, testInfo, files);
  try {
    for (const f of files) {
      const v = await openReview(p.page, p.ids[f]);
      await shot(testInfo, p.page, `review page ${f}`);
      await evidence(testInfo, `review page ${f}`, v);
      expect.soft(v.low.present, `${f}: ติดธง "ไม่แน่ใจยอดรวม"`).toBe(true);
      expect.soft(v.low.text, `${f}: ธงชื่อ "ไม่แน่ใจยอดรวม"`).toContain('ไม่แน่ใจยอดรวม');
      expect.soft(v.low.text, `${f}: เหตุผลพูดถึงความมั่นใจของยอดรวม`).toContain('ความมั่นใจ');
      expect.soft(v.low.text, `${f}: เหตุผลบอกว่าต่ำกว่า`).toContain('ต่ำกว่า');
      expect.soft(v.low.text, `${f}: เหตุผลบอกเส้น 0.90`).toContain('0.90');
      expect.soft(v.mismatch.present, `${f}: ไม่ติดธง "ยอดไม่ตรงรายการ" (|100.00 − 100.00| = 0.00)`).toBe(false);
    }
  } finally { await p.context.close(); await p.api.dispose(); }
});

test('TC-2-03 ความมั่นใจเท่ากับและสูงกว่า 0.90 ไม่ติดธง', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  const files = ['conf-090.jpg', 'conf-091.jpg'];
  const p = await prepareM(browser, testInfo, files);
  try {
    for (const f of files) {
      const v = await openReview(p.page, p.ids[f]);
      await shot(testInfo, p.page, `review page ${f}`);
      await evidence(testInfo, `review page ${f}`, v);
      expect.soft(v.low.present, `${f}: ไม่ติดธง "ไม่แน่ใจยอดรวม"`).toBe(false);
      expect.soft(v.mismatch.present, `${f}: ไม่ติดธง "ยอดไม่ตรงรายการ"`).toBe(false);
    }
  } finally { await p.context.close(); await p.api.dispose(); }
});

test('TC-2-04 ผลต่างไม่เกิน 1.00 บาท ไม่ติดธง', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  const cases = [
    { f: 'diff-099.jpg', sum: 4500 + 3000 + 2401 }, // 99.01 · |99.01 − 100.00| = 0.99
    { f: 'diff-100.jpg', sum: 4500 + 3000 + 2400 }, // 99.00 · |99.00 − 100.00| = 1.00
  ];
  const p = await prepareM(browser, testInfo, cases.map(c => c.f));
  try {
    for (const c of cases) {
      const v = await openReview(p.page, p.ids[c.f]);
      await shot(testInfo, p.page, `review page ${c.f}`);
      await evidence(testInfo, `review page ${c.f}`, v);
      expect.soft(toSatang(v.itemsSum), `${c.f}: items-sum`).toBe(c.sum);
      expect.soft(v.mismatch.present, `${c.f}: ไม่ติดธง "ยอดไม่ตรงรายการ" (ผลต่าง ${(10000 - c.sum) / 100} ≤ 1.00)`).toBe(false);
    }
  } finally { await p.context.close(); await p.api.dispose(); }
});

test('TC-2-05 ผลต่างเกิน 1.00 บาท ทั้งขาดและเกิน ติดธง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  const cases = [
    { f: 'diff-101.jpg', total: 10000, sum: 9899, diff: 101 },
    { f: 'diff-over-101.jpg', total: 10000, sum: 10101, diff: 101 },
    { f: 'diff-149.jpg', total: 10000, sum: 9851, diff: 149 },
  ];
  const p = await prepareM(browser, testInfo, cases.map(c => c.f));
  try {
    for (const c of cases) {
      const v = await openReview(p.page, p.ids[c.f]);
      await shot(testInfo, p.page, `review page ${c.f}`);
      await evidence(testInfo, `review page ${c.f}`, v);
      expect.soft(v.mismatch.present, `${c.f}: ติดธง "ยอดไม่ตรงรายการ"`).toBe(true);
      const nums = moneyInText(v.mismatch.text);
      expect.soft(nums, `${c.f}: เหตุผลแสดงยอดรวมที่อ่าน ${c.total / 100} — text "${v.mismatch.text}"`).toContain(c.total);
      expect.soft(nums, `${c.f}: เหตุผลแสดงผลรวมรายการ ${(c.sum / 100).toFixed(2)} — text "${v.mismatch.text}"`).toContain(c.sum);
      expect.soft(nums, `${c.f}: เหตุผลแสดงผลต่าง ${(c.diff / 100).toFixed(2)} — text "${v.mismatch.text}"`).toContain(c.diff);
    }
  } finally { await p.context.close(); await p.api.dispose(); }
});

test('TC-2-06 ติด 2 ธง และตัวกรองเฉพาะใบติดธง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  const files = ['ok-100__001.jpg', 'conf-089.jpg', 'conf-090.jpg', 'diff-101.jpg', 'both-flags.jpg'];
  const p = await prepareM(browser, testInfo, files);
  try {
    // both-flags: 2 flags with both reasons (0.50 < 0.90 · |95.00 − 100.00| = 5.00 > 1.00)
    const v = await openReview(p.page, p.ids['both-flags.jpg']);
    await shot(testInfo, p.page, 'review page both-flags');
    await evidence(testInfo, 'review page both-flags', v);
    expect.soft(v.low.present, 'both-flags: ติดธง "ไม่แน่ใจยอดรวม"').toBe(true);
    expect.soft(v.mismatch.present, 'both-flags: ติดธง "ยอดไม่ตรงรายการ"').toBe(true);
    expect.soft(v.low.text, 'both-flags: เหตุผลความมั่นใจต่ำกว่า 0.90').toContain('0.90');
    expect.soft(moneyInText(v.mismatch.text), `both-flags: เหตุผลแสดงผลต่าง 5.00 — text "${v.mismatch.text}"`).toContain(500);

    // /receipts · tick filter-flagged-checkbox
    await p.page.goto('/receipts');
    await expect(p.page.getByTestId('receipts-table')).toBeVisible();
    await p.page.getByTestId('filter-flagged-checkbox').check();
    await p.page.getByTestId('filter-apply-button').click();
    await p.page.waitForLoadState('networkidle');
    // wait until the unflagged ok-100 row disappears or the filter result settles
    await expect(p.page.getByTestId(`receipt-row-${p.ids['ok-100__001.jpg']}`), 'ok-100 not in flagged filter').toHaveCount(0, { timeout: 15_000 }).catch(() => {});
    await shot(testInfo, p.page, 'receipts filtered flagged');

    const shown: Record<string, number> = {};
    for (const f of files) shown[f] = await p.page.getByTestId(`receipt-row-${p.ids[f]}`).count();
    const inFilter = files.filter(f => shown[f] > 0);
    await evidence(testInfo, 'flagged filter rows of this batch', { shown, receiptsCount: await p.page.getByTestId('receipts-count').innerText().catch(() => '') });
    expect.soft(inFilter.sort(), 'ผลกรองของ 5 ID = conf-089 · diff-101 · both-flags').toEqual(['both-flags.jpg', 'conf-089.jpg', 'diff-101.jpg']);
    expect.soft(inFilter.length, 'ในบรรดา 5 ID ผลกรองมี 3 ใบพอดี (ใบติด 2 ธงนับ 1)').toBe(3);
    expect.soft(shown['both-flags.jpg'], 'both-flags ปรากฏ 1 แถว').toBe(1);
    expect.soft(shown['ok-100__001.jpg'], 'ok-100 ไม่อยู่ในผลกรอง').toBe(0);
    expect.soft(shown['conf-090.jpg'], 'conf-090 ไม่อยู่ในผลกรอง').toBe(0);

    // API view of the same filter (evidence only)
    const w11 = await (await p.api.get('/api/receipts?flagged=true')).json();
    const mine = (w11.receipts || []).filter((r: any) => Object.values(p.ids).includes(r.id)).map((r: any) => r.fileName);
    await evidence(testInfo, 'W11 flagged=true (ids of this batch)', { count: w11.count, ofThisBatch: mine });
  } finally { await p.context.close(); await p.api.dispose(); }
});

test('TC-2-07 โมเดลจริงอ่านใบเสร็จจริง 12 ใบ (smoke)', { tag: ['@P1', '@R'] }, async ({ browser }, testInfo) => {
  test.setTimeout(30 * 60_000);
  const gt: { id: string; file: string; total: string; n_items: number }[] =
    JSON.parse(fs.readFileSync(path.join(REAL_IMAGES, 'ground_truth.json'), 'utf8'));
  expect(gt.length, 'ground_truth.json has 12 receipts').toBe(12);
  const files = gt.map(g => path.join(REAL_IMAGES, g.file));
  const api = await prepareR(testInfo, files);
  const { context, page } = await pageAs(browser, R_URL, 'U02');
  try {
    const cl = await clientId(api, 'CL-03');
    const up = await upload(api, { clientId: cl, files, real: true });
    await evidence(testInfo, 'W7 upload 12 real', { status: up.status, json: up.json });
    expect(up.status, 'W7 upload').toBeLessThan(300);
    expect(up.json.accepted, 'accepted 12').toBe(12);
    const ids: Record<string, string> = {};
    for (const r of up.json.receipts || []) ids[r.fileName] = r.id;
    for (const g of gt) expect(ids[g.file], `id of ${g.file}`).toBeTruthy();

    await page.goto(`/batches/${up.json.batchId}`);
    const got = await waitStatus(api, gt.map(g => ids[g.file]), ['review', 'unreadable', 'confirmed'], 20 * 60_000);
    await page.reload();
    await shot(testInfo, page, 'batch page 12 real receipts read');
    await evidence(testInfo, 'W12 12 real receipts', got);

    const rows: string[] = ['| file | status | merchant | date | read total | truth total | total ok | flags | items read / n_items |', '|---|---|---|---|---|---|---|---|---|'];
    let correct = 0, wrongUnflagged = 0, itemsMatch = 0;
    for (const g of gt) {
      const r = got.find((x: any) => x.id === ids[g.file]);
      const readSat = toSatang(r?.total);
      const truthSat = toSatang(g.total);
      const ok = readSat !== null && readSat === truthSat;
      if (ok) correct++;
      const flagged = isFlagged(r);
      if (!ok && !flagged) wrongUnflagged++;
      const nItems = Array.isArray(r?.items) ? r.items.filter((i: any) => !i.removed).length : null;
      if (nItems === g.n_items) itemsMatch++;
      rows.push(`| ${g.file} | ${r?.status} | ${r?.merchant ?? ''} | ${r?.receiptDate ?? ''} | ${r?.total ?? ''} | ${g.total} | ${ok ? 'yes' : 'NO'} | ${flagged ? (r.flags.reasons || []).join(' / ') || 'flagged' : '-'} | ${nItems} / ${g.n_items} |`);

      // ① status รอตรวจ + 5-field structure
      expect.soft(r?.status, `${g.file}: รอตรวจ (review)`).toBe('review');
      expect.soft(r && 'merchant' in r && 'receiptDate' in r && 'total' in r && Array.isArray(r.items), `${g.file}: โครงสร้าง 5 ช่องครบ (merchant · date · items[name,price] · total)`).toBe(true);
      for (const it of (r?.items || [])) expect.soft('name' in it && 'price' in it, `${g.file}: item line ${it.lineNo} has name and price`).toBe(true);
      expect.soft(r?.total, `${g.file}: มียอดรวม`).not.toBeNull();
      // ② merchant / date read for real
      expect.soft((r?.merchant ?? '').trim(), `${g.file}: ชื่อร้านไม่ว่าง`).not.toBe('');
      expect.soft((r?.merchant ?? '').trim().toUpperCase(), `${g.file}: ชื่อร้านไม่ใช่ UNKNOWN`).not.toBe('UNKNOWN');
      const d = String(r?.receiptDate ?? '');
      expect.soft(/^\d{4}-\d{2}-\d{2}/.test(d) && !Number.isNaN(Date.parse(d.slice(0, 10))), `${g.file}: วันที่เป็นวันที่จริง (got "${d}")`).toBe(true);
      expect.soft(d.slice(0, 10), `${g.file}: วันที่ไม่ใช่ 1900-01-01`).not.toBe('1900-01-01');
      // ③ wrong total must be flagged
      if (!ok) expect.soft(flagged, `${g.file}: ยอดอ่าน ${r?.total} ≠ เฉลย ${g.total} ต้องติดธง`).toBe(true);
    }
    rows.push('', `ยอดถูก ${correct} / 12 = ${(correct / 12 * 100).toFixed(1)}% (M1 trend, not used to judge) · จำนวนรายการตรง n_items ${itemsMatch} / 12 (M7 trend) · ยอดผิดและไม่ติดธง ${wrongUnflagged}`);
    await evidence(testInfo, 'per-receipt comparison (satang)', rows.join('\n'));
    testInfo.annotations.push({ type: 'trend', description: `total correct ${correct}/12 · items count match ${itemsMatch}/12 · wrong & unflagged ${wrongUnflagged}` });
    expect.soft(wrongUnflagged, '③ ใบที่ยอดผิดและไม่ติดธง = 0').toBe(0);

    const qEnd = await queue(api);
    await evidence(testInfo, 'W23 at end', qEnd);
    expect.soft(qEnd?.workers?.alive, 'workersAlive = 2 at end').toBe(2);
  } finally { await context.close(); await api.dispose(); }
});

test('TC-2-08 โมเดลจริงไม่เดากับรูปที่อ่านไม่ได้', { tag: ['@P2', '@R'] }, async ({ browser }, testInfo) => {
  test.setTimeout(20 * 60_000);
  const files = [path.join(DATA, 'te0000-crop.jpg'), path.join(DATA, 'te0000-blur.jpg')];
  testInfo.annotations.push({ type: 'deviation', description: 'te0000-crop (bottom half cut) และ te0000-blur (Gaussian 25) ตรวจว่าอ่านยอดรวม 60,000.00 ไม่ได้โดยผู้ตรวจ 1 คน (แผนกำหนด 2 คน)' });
  const api = await prepareR(testInfo, files);
  const { context, page } = await pageAs(browser, R_URL, 'U02');
  try {
    const cl = await clientId(api, 'CL-03');
    const up = await upload(api, { clientId: cl, files, real: true });
    await evidence(testInfo, 'W7 upload 2 unreadable images', { status: up.status, json: up.json });
    expect(up.status, 'W7 upload').toBeLessThan(300);
    expect(up.json.accepted, 'accepted 2').toBe(2);
    const ids: Record<string, string> = {};
    for (const r of up.json.receipts || []) ids[r.fileName] = r.id;
    const names = files.map(f => path.basename(f));
    for (const n of names) expect(ids[n], `id of ${n}`).toBeTruthy();

    const got = await waitStatus(api, names.map(n => ids[n]), ['review', 'unreadable', 'confirmed'], 15 * 60_000);
    await evidence(testInfo, 'W12 2 receipts', got);
    await page.goto(`/batches/${up.json.batchId}`);
    await shot(testInfo, page, 'batch page crop + blur');

    const rows = ['| file | status | read total | flags | reasons | guessed (total, no flag) |', '|---|---|---|---|---|---|'];
    let guessed = 0;
    for (const n of names) {
      const r = got.find((x: any) => x.id === ids[n]);
      const flagged = isFlagged(r);
      const hasTotal = r?.total !== null && r?.total !== undefined && r?.total !== '';
      const g = r?.status === 'review' && hasTotal && !flagged;
      if (g) guessed++;
      rows.push(`| ${n} | ${r?.status} | ${r?.total ?? ''} | ${flagged ? 'yes' : 'no'} | ${(r?.flags?.reasons || []).join(' / ')} | ${g ? 'YES' : 'no'} |`);
      expect.soft(flagged || r?.status === 'unreadable', `${n}: ติดธงอย่างน้อย 1 ธง หรืออยู่ "อ่านไม่ได้" (status ${r?.status}, total ${r?.total})`).toBe(true);
    }
    await evidence(testInfo, 'per-receipt comparison', rows.join('\n'));
    expect.soft(guessed, 'ใบที่มียอดรวมโดยไม่ติดธง = 0 (M5 อย่าเดา)').toBe(0);

    const qEnd = await queue(api);
    await evidence(testInfo, 'W23 at end', qEnd);
    expect.soft(qEnd?.workers?.alive, 'workersAlive = 2 at end').toBe(2);
  } finally { await context.close(); await api.dispose(); }
});
