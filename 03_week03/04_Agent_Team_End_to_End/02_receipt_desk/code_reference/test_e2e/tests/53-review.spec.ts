/**
 * TEST-PLAN.md section 5.3 · การตรวจแก้และยืนยัน (TC-3-01 … TC-3-08) · all on stack M (:3421, mock reader).
 * Common pre-steps of 5.3: reset ตั้งต้น · U-01 uploads the file(s) for CL-01 · wait until "รอตรวจ" (review).
 * Confirm = category CAT-04 + "เทียบยอดรวมกับรูปแล้ว" ticked, unless the TC says otherwise.
 *
 * Note: W12 (GET /api/receipts/{id}) marks a receipt as opened (reviewOpenedAt). TC-3-05 and TC-3-07 need
 * receipts / sessions that never opened the receipt, so they wait for "review" through W9/W11 instead of W12.
 */
import { APIRequestContext, Page } from '@playwright/test';
import {
  test, expect, M_URL, apiAs, reset, clientId, categoryId, upload, waitStatus, confirm,
  pageAs, evidence, shot, pendingAP, CATEGORY_NAME,
} from './lib/rd';

const PIM = 'พิมพ์';     // U-01 คุณพิมพ์
const KITTI = 'กิตติ';   // U-03 คุณกิตติ

// ------------------------------------------------------------------ local helpers
const money = (v: unknown) => Math.round(Number(String(v ?? '').replace(/[^0-9.\-]/g, '')) * 100); // satang

/** Upload `files` for CL-01 as U-01 (API). Returns receipt ids in file order + batch id + upload json. */
async function uploadCL01(u01: APIRequestContext, files: string[]) {
  const cl = await clientId(u01, 'CL-01');
  const up = await upload(u01, { clientId: cl, files });
  expect(up.status, `upload ${files.join(',')} -> ${JSON.stringify(up.json).slice(0, 300)}`).toBeLessThan(300);
  const recs: any[] = up.json.receipts || [];
  const ids = files.map(f => {
    const r = recs.find(x => x.fileName === f);
    if (!r) throw new Error(`receipt of ${f} not in upload response`);
    return r.id as string;
  });
  const batchId = up.json.batch?.id ?? up.json.batchId ?? up.json.id ?? recs[0]?.batchId;
  return { ids, batchId, json: up.json };
}

/** Wait for "review" WITHOUT calling W12 (W9 batch detail, fallback W11 list), so nobody "opens" the receipt. */
async function waitReviewNoOpen(ctx: APIRequestContext, batchId: string | undefined, ids: string[], timeoutMs = 180_000) {
  const end = Date.now() + timeoutMs; let last = '';
  for (;;) {
    let list: any[] | undefined;
    if (batchId) {
      const j = await (await ctx.get(`/api/batches/${batchId}`)).json().catch(() => ({}));
      list = j.receipts ?? j.batch?.receipts;
      last = JSON.stringify(j).slice(0, 400);
    }
    if (!list) {
      const j = await (await ctx.get('/api/receipts')).json().catch(() => ({}));
      list = j.receipts ?? j.items;
      last = JSON.stringify(j).slice(0, 400);
    }
    const st = ids.map(id => list!.find((r: any) => r.id === id)?.status);
    if (st.every(s => s === 'review')) return;
    if (Date.now() > end) throw new Error(`timeout waiting for review (no W12): ${st.join(',')} · last=${last}`);
    await new Promise(r => setTimeout(r, 2000));
  }
}

async function getR(ctx: APIRequestContext, id: string) {
  return (await (await ctx.get(`/api/receipts/${id}`)).json()).receipt;
}
async function history(ctx: APIRequestContext, id: string) {
  return (await ctx.get(`/api/receipts/${id}/history`)).json();
}

/** Pick old/new/actor/time out of an edit row whatever the key names are. */
function editParts(e: any) {
  const keys = Object.keys(e || {});
  const k = (re: RegExp) => keys.find(x => re.test(x));
  const oldK = k(/^(old|before|from|previous|oldValue)/i);
  const newK = k(/^(new|after|to$|value$|newValue)/i);
  const actK = k(/(by|actor|editor|user)/i);
  const atK = k(/(At$|^at$|time|date$)/);
  const actor = actK ? e[actK] : undefined;
  return {
    field: String(e.field ?? e.path ?? e.name ?? ''),
    old: oldK ? e[oldK] : undefined,
    neu: newK ? e[newK] : undefined,
    actor: typeof actor === 'object' ? JSON.stringify(actor) : String(actor ?? ''),
    at: atK ? e[atK] : undefined,
  };
}

/** Page step "ยืนยัน": choose category, tick total-checked, press confirm. Returns the W15 response or null when the page blocked it. */
async function confirmOnPage(page: Page, id: string, cat = 'CAT-04') {
  if (await page.getByTestId('category-select').count() === 0 || await page.getByTestId('confirm-button').count() === 0) return null;
  await page.getByTestId('category-select').selectOption({ label: CATEGORY_NAME[cat] });
  await page.getByTestId('total-checked-checkbox').check();
  const btn = page.getByTestId('confirm-button');
  if (await btn.isDisabled()) return null;
  const respP = page.waitForResponse(r => r.url().includes(`/api/receipts/${id}/confirm`) && r.request().method() === 'POST', { timeout: 20_000 });
  await btn.click();
  const resp = await respP;
  return { status: resp.status(), json: await resp.json().catch(() => ({})) };
}

/** Page step "บันทึก": press save and wait for the W14 PATCH. */
async function saveOnPage(page: Page, id: string) {
  const respP = page.waitForResponse(r => r.url().endsWith(`/api/receipts/${id}`) && r.request().method() === 'PATCH', { timeout: 20_000 });
  await page.getByTestId('save-button').click();
  const resp = await respP;
  return { status: resp.status(), json: await resp.json().catch(() => ({})) };
}

/** "เปิดดูรายละเอียดทุกช่อง" as a reviewer does on the page: visit every field once (merchant, date, every item name/price, total). */
async function viewAllFields(page: Page) {
  const ids = ['field-merchant-input', 'field-date-input'];
  const n = await page.locator('[data-testid^="item-price-input-"]').count();
  for (let i = 1; i <= n; i++) ids.push(`item-name-input-${i}`, `item-price-input-${i}`);
  ids.push('field-total-input');
  for (const t of ids) {
    const l = page.getByTestId(t);
    if (await l.count() && await l.isEditable()) { await l.click(); await l.press('End'); }
  }
}

async function openReceipt(page: Page, id: string) {
  await page.goto(`/receipts/${id}`);
  await expect(page.getByTestId('receipt-status')).toBeVisible();
}

// ------------------------------------------------------------------ tests

test('TC-3-01 ยอดรวม 0.00 ยืนยันไม่ได้', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const u01 = await apiAs(M_URL, 'U01');
  const { ids: [id] } = await uploadCL01(u01, ['total-000.jpg']);
  await waitStatus(u01, [id], ['review']);

  const { context, page } = await pageAs(browser, M_URL, 'U01');
  try {
    await openReceipt(page, id);
    let res = await confirmOnPage(page, id);
    if (res === null) {
      // page blocked the confirm before sending (plan section 4): send the same request through the API to read the code
      testInfo.annotations.push({ type: 'note', description: 'confirm-button disabled on the page for total 0.00 -> same W15 sent by API' });
      await shot(testInfo, page, 'confirm-blocked-on-page');
      res = await confirm(u01, id);
    } else {
      await shot(testInfo, page, 'after-confirm-click');
    }
    await evidence(testInfo, 'W15 confirm total 0.00', res);
    expect.soft(res.status, 'W15 for total 0.00 must be 422').toBe(422);
    expect.soft(res.json.error, 'error code must be total_invalid').toBe('total_invalid');

    const r = await getR(u01, id);
    await evidence(testInfo, 'W12 after confirm', r);
    expect.soft(r.status, 'status must stay review (รอตรวจ)').toBe('review');
    expect.soft(r.confirmedBy ?? null, 'no confirmer').toBeNull();
    expect.soft(r.confirmedAt ?? null, 'no confirm time').toBeNull();
  } finally { await context.close(); await u01.dispose(); }
});

test('TC-3-02 ยอดรวม 0.01 และ 0.02 ยืนยันได้', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const u01 = await apiAs(M_URL, 'U01');
  const { ids } = await uploadCL01(u01, ['total-001.jpg', 'total-002.jpg']);
  await waitStatus(u01, ids, ['review']);

  const { context, page } = await pageAs(browser, M_URL, 'U01');
  try {
    for (const [i, id] of ids.entries()) {
      const name = i === 0 ? 'total 0.01' : 'total 0.02';
      await openReceipt(page, id);
      const res = await confirmOnPage(page, id);
      expect.soft(res, `${name}: confirm-button must be usable`).not.toBeNull();
      if (res) {
        await evidence(testInfo, `W15 ${name}`, res);
        expect.soft(res.status, `${name}: W15 must succeed`).toBeLessThan(300);
      }
      await page.reload();
      await expect.soft(page.getByTestId('confirmed-by'), `${name}: confirmed-by = คุณพิมพ์`).toContainText(PIM);
      await shot(testInfo, page, `confirmed ${name}`);
      const r = await getR(u01, id);
      await evidence(testInfo, `W12 ${name}`, r);
      expect.soft(r.status, `${name}: status confirmed`).toBe('confirmed');
      expect.soft(JSON.stringify(r.confirmedBy ?? ''), `${name}: confirmedBy คุณพิมพ์`).toContain(PIM);
      expect.soft(String(r.confirmedAt ?? ''), `${name}: confirmedAt not empty`).not.toBe('');
    }
  } finally { await context.close(); await u01.dispose(); }
});

test('TC-3-03 แก้ยอดเป็นค่าติดลบ', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const u01 = await apiAs(M_URL, 'U01');
  const { ids: [id] } = await uploadCL01(u01, ['ok-100__001.jpg']);
  await waitStatus(u01, [id], ['review']);

  const { context, page } = await pageAs(browser, M_URL, 'U01');
  try {
    await openReceipt(page, id);
    await page.getByTestId('field-total-input').fill('-5.00');
    const saved = await saveOnPage(page, id);
    await evidence(testInfo, 'W14 total -5.00', saved);
    expect.soft(saved.status, 'saving -5.00 must be accepted (history must show it)').toBeLessThan(300);

    let res = await confirmOnPage(page, id);
    if (res === null) {
      testInfo.annotations.push({ type: 'note', description: 'confirm-button disabled for total -5.00 -> same W15 sent by API' });
      res = await confirm(u01, id);
    }
    await evidence(testInfo, 'W15 confirm total -5.00', res);
    expect.soft(res.status, 'W15 for -5.00 must be 422').toBe(422);
    expect.soft(res.json.error, 'error total_invalid').toBe('total_invalid');

    const r = await getR(u01, id);
    expect.soft(r.status, 'status stays review').toBe('review');

    await page.reload();
    await page.getByTestId('history-button').click();
    await expect.soft(page.locator('[data-testid^="history-row-"]').first(), 'history row visible').toBeVisible();
    await shot(testInfo, page, 'history');

    const h = await history(u01, id);
    await evidence(testInfo, 'W17 history', h);
    const e = (h.edits || []).map(editParts).find((x: any) => /total/i.test(x.field));
    expect.soft(e, 'history has an edit of total').toBeTruthy();
    if (e) {
      expect.soft(money(e.old), 'old value 100.00').toBe(10000);
      expect.soft(money(e.neu), 'new value -5.00').toBe(-500);
      expect.soft(e.actor, 'edited by คุณพิมพ์').toContain(PIM);
      expect.soft(String(e.at ?? ''), 'edit time present').not.toBe('');
    }
  } finally { await context.close(); await u01.dispose(); }
});

test('TC-3-04 ยืนยันโดยไม่ติ๊กเทียบยอด / ไม่เลือกหมวด', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const u01 = await apiAs(M_URL, 'U01');
  const { ids: [id] } = await uploadCL01(u01, ['ok-100__001.jpg']);
  await waitStatus(u01, [id], ['review']);
  const cat4 = await categoryId(u01, 'CAT-04');

  const { context, page } = await pageAs(browser, M_URL, 'U01');
  try {
    await openReceipt(page, id); // เปิดหน้าตรวจ
    await shot(testInfo, page, 'review page');

    const r1 = await confirm(u01, id, { totalChecked: false, categoryId: cat4 });
    await evidence(testInfo, '① totalChecked=false', r1);
    expect.soft(r1.status >= 400 && r1.status < 500, `① must be rejected 4xx (got ${r1.status})`).toBe(true);
    let r = await getR(u01, id);
    expect.soft(r.status, '① status stays review').toBe('review');
    expect.soft(r.confirmedBy ?? null, '① no confirmer').toBeNull();

    const r2 = await confirm(u01, id, { totalChecked: true });
    await evidence(testInfo, '② no categoryId', r2);
    expect.soft(r2.status >= 400 && r2.status < 500, `② must be rejected 4xx (got ${r2.status})`).toBe(true);
    r = await getR(u01, id);
    expect.soft(r.status, '② status stays review').toBe('review');
    expect.soft(r.confirmedBy ?? null, '② no confirmer').toBeNull();

    const r3 = await confirm(u01, id, { totalChecked: true, categoryId: cat4 });
    await evidence(testInfo, '③ control', r3);
    expect.soft(r3.status, '③ control confirm must succeed').toBeLessThan(300);
    r = await getR(u01, id);
    await evidence(testInfo, 'W12 end', r);
    expect.soft(r.status, '③ status confirmed').toBe('confirmed');
  } finally { await context.close(); await u01.dispose(); }
});

test('TC-3-05 ใบติดธงต้องเปิดดูก่อนยืนยัน', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const up = await apiAs(M_URL, 'U01');
  const { ids: [id1, id2], batchId } = await uploadCL01(up, ['conf-089__001.jpg', 'conf-089__002.jpg']);
  await waitReviewNoOpen(up, batchId, [id1, id2]);
  await up.dispose();

  const fresh = await apiAs(M_URL, 'U01'); // new U-01 session, never opened anything
  const { context, page } = await pageAs(browser, M_URL, 'U01');
  try {
    const cat4 = await categoryId(fresh, 'CAT-04');
    const body = { totalChecked: true, categoryId: cat4 };

    // ① confirm __001 right away: no page, no W12
    const c1 = await confirm(fresh, id1, body);
    await evidence(testInfo, '① confirm without opening', c1);
    expect.soft(c1.status >= 400 && c1.status < 500, `① must be rejected (got ${c1.status})`).toBe(true);

    // ② W12 on __001, then confirm -> recorded for AP-03
    const r1 = await getR(fresh, id1);
    await evidence(testInfo, '② W12 __001 (after ①)', r1);
    expect.soft(r1.status, '① status stays review').toBe('review');
    expect.soft(r1.flags?.flagged, 'conf-089 is a flagged receipt').toBe(true);
    const c2 = await confirm(fresh, id1, body);
    await evidence(testInfo, '② confirm after W12', c2);
    const r1b = await getR(fresh, id1);
    pendingAP(testInfo, 'AP-03', `W12 then W15 on conf-089__001 -> HTTP ${c2.status} ${c2.json.error ?? ''} · status=${r1b.status}`);

    // ③ __002 through the browser page, then confirm
    await openReceipt(page, id2);
    await viewAllFields(page);
    const c3 = await confirmOnPage(page, id2);
    expect.soft(c3, '③ confirm-button must be usable').not.toBeNull();
    if (c3) {
      await evidence(testInfo, '③ confirm on page', c3);
      expect.soft(c3.status, '③ confirm must succeed').toBeLessThan(300);
    }
    await page.reload();
    await expect.soft(page.getByTestId('confirmed-by'), '③ confirmed-by คุณพิมพ์').toContainText(PIM);
    await shot(testInfo, page, '③ confirmed __002');
    const r2 = await getR(fresh, id2);
    await evidence(testInfo, '③ W12 __002', r2);
    expect.soft(r2.status, '③ status confirmed').toBe('confirmed');
    expect.soft(JSON.stringify(r2.confirmedBy ?? ''), '③ confirmedBy คุณพิมพ์').toContain(PIM);
  } finally { await context.close(); await fresh.dispose(); }
});

test('TC-3-06 แก้ทุกช่องโดยพนักงานและหัวหน้า ค่าเดิมไม่ถูกทับ', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const u01 = await apiAs(M_URL, 'U01');
  const { ids: [id] } = await uploadCL01(u01, ['ok-100__001.jpg']);
  await waitStatus(u01, [id], ['review']);

  const s1 = await pageAs(browser, M_URL, 'U01');
  const s3 = await pageAs(browser, M_URL, 'U03');
  try {
    // ① U-01 edits 5 fields
    const p = s1.page;
    await openReceipt(p, id);
    await p.getByTestId('field-merchant-input').fill('ร้านแก้ไข');
    await p.getByTestId('field-date-input').fill('2026-11-17');
    await p.getByTestId('item-name-input-1').fill('ข้าวสาร');
    await p.getByTestId('item-price-input-3').fill('45.00');
    await p.getByTestId('field-total-input').fill('120.00');
    const sv1 = await saveOnPage(p, id);
    await evidence(testInfo, '① W14 U-01', sv1);
    expect.soft(sv1.status, '① save must succeed').toBeLessThan(300);
    await p.reload();
    await expect.soft(p.getByTestId('items-sum'), '① items-sum = 120.00').toContainText('120.00');
    await expect.soft(p.getByTestId('flag-mismatch'), '① no mismatch flag (|120-120| = 0)').toHaveCount(0);
    await shot(testInfo, p, '① after U-01 edit');
    const a = await getR(u01, id);
    await evidence(testInfo, '① W12', a);
    expect.soft(money(a.itemsSum), '① itemsSum 120.00').toBe(12000);
    expect.soft(a.flags?.mismatch, '① flags.mismatch false').toBe(false);

    // ② U-03 edits merchant
    const q = s3.page;
    await openReceipt(q, id);
    await q.getByTestId('field-merchant-input').fill('ร้านแก้ไข 2');
    const sv2 = await saveOnPage(q, id);
    await evidence(testInfo, '② W14 U-03', sv2);
    expect.soft(sv2.status, '② save must succeed').toBeLessThan(300);

    // ③ U-03 history
    await q.reload();
    await q.getByTestId('history-button').click();
    await expect.soft(q.locator('[data-testid^="history-row-"]'), '③ 6 history rows on page').toHaveCount(6);
    const om = (await q.getByTestId('original-merchant').textContent().catch(() => '')) || '';
    const od = (await q.getByTestId('original-date').textContent().catch(() => '')) || '';
    const ot = (await q.getByTestId('original-total').textContent().catch(() => '')) || '';
    await evidence(testInfo, '③ original-* on page', { om, od, ot });
    expect.soft(om, 'original-merchant ร้านตัวอย่าง').toContain('ร้านตัวอย่าง');
    expect.soft(/2026-11-18|18\s*พ\.ย\.\s*(2569|69)|18\/11\/(2026|2569)/.test(od), `original-date 2026-11-18 (got "${od}")`).toBe(true);
    expect.soft(ot, 'original-total 100.00').toContain('100.00');
    await shot(testInfo, q, '③ history U-03');

    const u03 = await apiAs(M_URL, 'U03');
    const h = await history(u03, id);
    await u03.dispose();
    await evidence(testInfo, '③ W17', h);
    const edits = (h.edits || []).map(editParts);
    if (h.original?.items?.find((x: any) => x.lineNo === 1)?.name === 'ข้าวสาร')
      pendingAP(testInfo, 'AP-06', 'ok-100 line 1 is already named "ข้าวสาร" by the mock, so step ① renames it to the same value; the plan expects 6 history rows assuming a real change (plan input issue, assertion kept as written)');
    expect.soft(edits.length, '6 edits (5 U-01 + 1 U-03)').toBe(6);
    expect.soft(edits.filter((e: any) => e.actor.includes(PIM)).length, '5 edits by คุณพิมพ์').toBe(5);
    expect.soft(edits.filter((e: any) => e.actor.includes(KITTI)).length, '1 edit by คุณกิตติ').toBe(1);
    for (const [i, e] of edits.entries()) {
      expect.soft(e.old !== undefined && e.neu !== undefined, `edit ${i + 1} has old and new value`).toBe(true);
      expect.soft(e.actor, `edit ${i + 1} has editor`).not.toBe('');
      expect.soft(String(e.at ?? ''), `edit ${i + 1} has time`).not.toBe('');
    }
    const cur = h.current ?? (await getR(u01, id));
    expect.soft(cur.merchant, 'current merchant ร้านแก้ไข 2').toBe('ร้านแก้ไข 2');
    expect.soft(String(cur.receiptDate ?? '').slice(0, 10), 'current date 2026-11-17').toBe('2026-11-17');
    expect.soft(money(cur.total), 'current total 120.00').toBe(12000);
    const org = h.original ?? {};
    expect.soft(org.merchant, 'original merchant ร้านตัวอย่าง').toBe('ร้านตัวอย่าง');
    expect.soft(String(org.receiptDate ?? '').slice(0, 10), 'original date 2026-11-18').toBe('2026-11-18');
    expect.soft(money(org.total), 'original total 100.00').toBe(10000);
  } finally { await s1.context.close(); await s3.context.close(); await u01.dispose(); }
});

test('TC-3-07 ธงยอดไม่ตรงคิดจากค่าหลังแก้', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const u01 = await apiAs(M_URL, 'U01');
  const { ids: [id1, id2], batchId } = await uploadCL01(u01, ['ok-100__001.jpg', 'ok-100__002.jpg']);
  await waitReviewNoOpen(u01, batchId, [id1, id2]);

  const { context, page } = await pageAs(browser, M_URL, 'U01');
  const u02 = await apiAs(M_URL, 'U02'); // never opens the receipt
  try {
    // ① U-01 opens the review page, line 3 -> 23.99
    await openReceipt(page, id1);
    await page.getByTestId('item-price-input-3').fill('23.99');
    const sv = await saveOnPage(page, id1);
    await evidence(testInfo, '① W14 line3 23.99', sv);
    expect.soft(sv.status, '① save must succeed').toBeLessThan(300);
    await page.reload();
    await expect.soft(page.getByTestId('items-sum'), '① items-sum 98.99').toContainText('98.99');
    await expect.soft(page.getByTestId('flag-mismatch'), '① flag ยอดไม่ตรงรายการ shown (|98.99-100.00| = 1.01 > 1.00, AP-01)').toBeVisible();
    await shot(testInfo, page, '① after edit 23.99');
    const a = await getR(u01, id1);
    await evidence(testInfo, '① W12', a);
    expect.soft(money(a.itemsSum), '① itemsSum 98.99').toBe(9899);
    expect.soft(a.flags?.mismatch, '① flags.mismatch true (AP-01 provisional: current values)').toBe(true);
    expect.soft(a.flags?.flagged, '① flags.flagged true').toBe(true);

    // ② U-02 (never opened) sends a correct W15
    const c2 = await confirm(u02, id1);
    await evidence(testInfo, '② W15 by U-02 not opened', c2);
    expect.soft(c2.status >= 400 && c2.status < 500, `② must be rejected (got ${c2.status})`).toBe(true);
    const b = await getR(u01, id1);
    expect.soft(b.status, '② status stays review').toBe('review');

    // ③ U-01 reloads (opens every field) and confirms
    await page.reload();
    await expect(page.getByTestId('receipt-status')).toBeVisible();
    await viewAllFields(page);
    const c3 = await confirmOnPage(page, id1);
    expect.soft(c3, '③ confirm-button usable').not.toBeNull();
    if (c3) {
      await evidence(testInfo, '③ W15 by U-01 on page', c3);
      expect.soft(c3.status, '③ confirm must succeed').toBeLessThan(300);
    }
    const c = await getR(u01, id1);
    await evidence(testInfo, '③ W12', c);
    expect.soft(c.status, '③ status confirmed').toBe('confirmed');
    expect.soft(JSON.stringify(c.confirmedBy ?? ''), '③ confirmedBy คุณพิมพ์').toContain(PIM);
    await page.reload();
    await shot(testInfo, page, '③ confirmed __001');

    // ④ __002, line 3 -> 24.00 : 99.00 · diff 1.00 -> no flag
    await openReceipt(page, id2);
    await page.getByTestId('item-price-input-3').fill('24.00');
    const sv4 = await saveOnPage(page, id2);
    await evidence(testInfo, '④ W14 line3 24.00', sv4);
    expect.soft(sv4.status, '④ save must succeed').toBeLessThan(300);
    await page.reload();
    await expect.soft(page.getByTestId('items-sum'), '④ items-sum 99.00').toContainText('99.00');
    await expect.soft(page.getByTestId('flag-mismatch'), '④ no mismatch flag (diff 1.00)').toHaveCount(0);
    await shot(testInfo, page, '④ after edit 24.00');
    const d = await getR(u01, id2);
    await evidence(testInfo, '④ W12', d);
    expect.soft(money(d.itemsSum), '④ itemsSum 99.00').toBe(9900);
    expect.soft(d.flags?.mismatch, '④ flags.mismatch false').toBe(false);
  } finally { await context.close(); await u01.dispose(); await u02.dispose(); }
});

test('TC-3-08 หลังยืนยัน พนักงานแก้ไม่ได้ หัวหน้าเปิดกลับได้', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const u01 = await apiAs(M_URL, 'U01');
  const { ids: [id] } = await uploadCL01(u01, ['ok-100__001.jpg']);
  await waitStatus(u01, [id], ['review']);
  const c0 = await confirm(u01, id);
  await evidence(testInfo, 'confirm by U-01', c0);
  expect(c0.status, 'pre-step: U-01 confirms').toBeLessThan(300);

  const { context, page } = await pageAs(browser, M_URL, 'U03');
  try {
    // ① U-01 PATCH total 90.00
    const p1 = await u01.patch(`/api/receipts/${id}`, { data: { total: '90.00' } });
    const p1j = await p1.json().catch(() => ({}));
    await evidence(testInfo, '① PATCH by U-01', { status: p1.status(), json: p1j });
    expect.soft(p1.status(), '① PATCH after confirm must be 403').toBe(403);
    let r = await getR(u01, id);
    expect.soft(money(r.total), '① total stays 100.00').toBe(10000);

    // ② U-01 reopen
    const p2 = await u01.post(`/api/receipts/${id}/reopen`);
    const p2j = await p2.json().catch(() => ({}));
    await evidence(testInfo, '② reopen by U-01', { status: p2.status(), json: p2j });
    expect.soft(p2.status(), '② reopen by staff must be 403').toBe(403);
    r = await getR(u01, id);
    expect.soft(r.status, '② status stays confirmed').toBe('confirmed');
    expect.soft(money(r.total), '② total stays 100.00').toBe(10000);

    // ③ U-03 presses reopen-button
    await openReceipt(page, id);
    const respP = page.waitForResponse(x => x.url().includes(`/api/receipts/${id}/reopen`) && x.request().method() === 'POST', { timeout: 20_000 });
    await page.getByTestId('reopen-button').click();
    const resp = await respP;
    await evidence(testInfo, '③ reopen by U-03', { status: resp.status(), json: await resp.json().catch(() => ({})) });
    expect.soft(resp.status(), '③ reopen must succeed').toBeLessThan(300);
    await page.reload();
    await page.getByTestId('history-button').click().catch(() => {});
    await shot(testInfo, page, '③ after reopen');

    r = await getR(u01, id);
    expect.soft(r.status, '③ status back to review (รอตรวจ)').toBe('review');
    const h = await history(u01, id);
    await evidence(testInfo, '③ W17', h);
    const ev: any[] = h.events || [];
    const conf = ev.find(e => e.to === 'confirmed');
    const reo = ev.find(e => e.from === 'confirmed' && e.to === 'review');
    expect.soft(conf, 'history has the confirm event').toBeTruthy();
    expect.soft(JSON.stringify(conf?.actor ?? ''), 'confirm by คุณพิมพ์').toContain(PIM);
    expect.soft(String(conf?.at ?? ''), 'confirm time').not.toBe('');
    expect.soft(reo, 'history has the reopen event').toBeTruthy();
    expect.soft(JSON.stringify(reo?.actor ?? ''), 'reopen by คุณกิตติ').toContain(KITTI);
    expect.soft(String(reo?.at ?? ''), 'reopen time').not.toBe('');
  } finally { await context.close(); await u01.dispose(); }
});
