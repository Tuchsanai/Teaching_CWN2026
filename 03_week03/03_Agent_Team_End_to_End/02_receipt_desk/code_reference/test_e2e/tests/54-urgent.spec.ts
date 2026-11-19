/**
 * Test Plan 5.4 · งานด่วน (TC-4-01 … TC-4-08)
 * Expected values come only from the column "ผลที่คาดหวัง" of test/TEST-PLAN.md.
 * @A cases run on the mock stack :3421 · TC-4-07 ★ release round only (skipped) · TC-4-08 @R on :3420 (real model, 23 files).
 */
import * as fs from 'fs';
import * as path from 'path';
import type { APIRequestContext, BrowserContext, Page } from '@playwright/test';
import {
  test, expect, apiAs, reset, clientId, upload, waitStatus, queue, reconcile, pageAs,
  pauseReader, resumeReader, gpu, evidence, shot, pendingAP, okFiles, dataFile,
  M_URL, R_URL, REAL_IMAGES,
} from './lib/rd';

// ---------------------------------------------------------------- local helpers
type Resp = { status: number; json: any } | null;

/** W9 of one batch -> {batch, receipts} */
async function batchOf(ctx: APIRequestContext, id: string) {
  return (await ctx.get(`/api/batches/${id}`)).json();
}
/** W23 urgent.usedToday */
async function usedToday(ctx: APIRequestContext): Promise<number> {
  return (await queue(ctx)).urgent.usedToday;
}
/** All receipts of the office (W11 · limit 200 is enough after a reset). */
async function allReceipts(ctx: APIRequestContext): Promise<any[]> {
  return (await (await ctx.get('/api/receipts?limit=200')).json()).receipts;
}

/** Press `batch-urgent-button` on /batches/{id} and return the W10 response the page sent (null = button disabled / no request). */
async function urgentViaPage(page: Page, batchId: string): Promise<{ disabled: boolean; resp: Resp }> {
  await page.goto(`/batches/${batchId}`);
  const btn = page.getByTestId('batch-urgent-button');
  await expect(btn, 'batch-urgent-button visible').toBeVisible();
  if (await btn.isDisabled()) return { disabled: true, resp: null };
  const respP = page.waitForResponse(
    r => r.request().method() === 'POST' && /^\/api\/batches\/[^/]+\/urgent$/.test(new URL(r.url()).pathname),
    { timeout: 15_000 },
  ).catch(() => null);
  await btn.click();
  const r = await respP;
  if (!r) return { disabled: false, resp: null };
  return { disabled: false, resp: { status: r.status(), json: await r.json().catch(() => ({})) } };
}

/** Upload through /upload (client select · files · optional urgent tick). Returns the W7 response, or null if the page blocked before sending. */
async function uploadViaPage(page: Page, clientUuid: string, files: string[], urgent: boolean): Promise<Resp> {
  await page.goto('/upload');
  await page.getByTestId('upload-client-select').selectOption(clientUuid);
  await page.getByTestId('upload-file-input').setInputFiles(files.map(f => (path.isAbsolute(f) ? f : dataFile(f))));
  if (urgent) await page.getByTestId('upload-urgent-checkbox').check();
  const respP = page.waitForResponse(
    r => r.request().method() === 'POST' && new URL(r.url()).pathname === '/api/batches',
    { timeout: 60_000 },
  ).catch(() => null);
  await page.getByTestId('upload-submit-button').click();
  const r = await respP;
  if (!r) return null;
  return { status: r.status(), json: await r.json().catch(() => ({})) };
}

function autoAcceptDialogs(page: Page) { page.on('dialog', d => d.accept().catch(() => {})); }

// ================================================================= TC-4-01
test('TC-4-01 ชุด 9 และ 10 ใบตั้งด่วนได้ · ชุดที่อ่านเสร็จแล้วตั้งไม่ได้', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const lead = await apiAs(M_URL, 'U03');
  const { context, page } = await pageAs(browser, M_URL, 'U03');
  autoAcceptDialogs(page);
  try {
    const cl2 = await clientId(lead, 'CL-02');
    expect.soft(await usedToday(lead), 'ตัวนับงานด่วนวันนี้เริ่มที่ 0').toBe(0);
    pauseReader();
    try {
      // ชุด 9 ไฟล์
      const b9 = await upload(lead, { clientId: cl2, files: okFiles(9, 1) });
      expect(b9.status, 'อัปโหลด 9 ไฟล์ (ไม่ติ๊กด่วน)').toBe(201);
      expect(b9.json.accepted).toBe(9);
      const u9 = await urgentViaPage(page, b9.json.batchId);
      await evidence(testInfo, 'W10 ชุด 9 ใบ', u9);
      expect.soft(u9.resp?.status, 'W10 ชุด 9 ใบ ตั้งได้').toBe(200);
      await expect.soft(page.getByTestId('batch-priority'), 'ชุด 9 ใบ batch-priority = ด่วน').toContainText('ด่วน');
      await shot(testInfo, page, 'ชุด 9 ใบ หลังกดงานด่วน');
      expect.soft((await batchOf(lead, b9.json.batchId)).batch.priority, 'W9 ชุด 9 ใบ priority').toBe('urgent');
      expect.soft(await usedToday(lead), 'ตัวนับ 0 → 1').toBe(1);

      // ชุด 10 ไฟล์
      const b10 = await upload(lead, { clientId: cl2, files: okFiles(10, 10) });
      expect(b10.status, 'อัปโหลด 10 ไฟล์ (ไม่ติ๊กด่วน)').toBe(201);
      expect(b10.json.accepted).toBe(10);
      const u10 = await urgentViaPage(page, b10.json.batchId);
      await evidence(testInfo, 'W10 ชุด 10 ใบ', u10);
      expect.soft(u10.resp?.status, 'W10 ชุด 10 ใบ ตั้งได้').toBe(200);
      await expect.soft(page.getByTestId('batch-priority'), 'ชุด 10 ใบ batch-priority = ด่วน').toContainText('ด่วน');
      await shot(testInfo, page, 'ชุด 10 ใบ หลังกดงานด่วน');
      expect.soft((await batchOf(lead, b10.json.batchId)).batch.priority, 'W9 ชุด 10 ใบ priority').toBe('urgent');
      expect.soft(await usedToday(lead), 'ตัวนับ 1 → 2').toBe(2);
    } finally {
      resumeReader();
    }

    // ชุดที่อ่านเสร็จแล้ว
    const b3 = await upload(lead, { clientId: cl2, files: okFiles(3, 20) });
    expect(b3.status, 'อัปโหลด 3 ไฟล์').toBe(201);
    await waitStatus(lead, b3.json.receipts.map((r: any) => r.id), ['review', 'unreadable'], 180_000);
    const u3 = await urgentViaPage(page, b3.json.batchId);
    await evidence(testInfo, 'W10 ชุดที่อ่านเสร็จแล้ว', u3);
    await page.reload();
    await shot(testInfo, page, 'ชุดที่อ่านเสร็จแล้ว หลังกดงานด่วน');
    const after = await batchOf(lead, b3.json.batchId);
    expect.soft(after.batch.priority, 'ชุดที่อ่านเสร็จแล้ว ไม่ถูกตั้งเป็นด่วน (FR-18)').toBe('normal');
    await expect.soft(page.getByTestId('batch-priority'), 'batch-priority ของชุดที่อ่านเสร็จแล้ว ไม่ใช่ด่วน').not.toContainText('ด่วน');
    expect.soft(await usedToday(lead), 'ตัวนับยังเป็น 2').toBe(2);
    await evidence(testInfo, 'W23 ตอนจบ', await queue(lead));
  } finally {
    await context.close();
    await lead.dispose();
  }
});

// ================================================================= TC-4-02
test('TC-4-02 ชุด 11 ใบตั้งด่วนไม่ได้', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  await reset(M_URL);
  const lead = await apiAs(M_URL, 'U03');
  const { context, page } = await pageAs(browser, M_URL, 'U03');
  autoAcceptDialogs(page);
  pauseReader();
  try {
    const cl2 = await clientId(lead, 'CL-02');
    // ① ชุดปกติ 11 ใบ แล้วกดปุ่มด่วน
    const b11 = await upload(lead, { clientId: cl2, files: okFiles(11, 1) });
    expect(b11.status, 'อัปโหลด 11 ไฟล์ (ไม่ติ๊กด่วน)').toBe(201);
    const u = await urgentViaPage(page, b11.json.batchId);
    await evidence(testInfo, '① W10 ชุด 11 ใบ', u);
    expect.soft(u.resp?.status, '① W10 → 422').toBe(422);
    expect.soft(u.resp?.json?.error, '① error = urgent_too_large').toBe('urgent_too_large');
    await expect.soft(page.getByTestId('batch-urgent-error'), '① batch-urgent-error แสดง').toBeVisible();
    await shot(testInfo, page, '① ชุด 11 ใบ กดงานด่วน');
    const w9 = await batchOf(lead, b11.json.batchId);
    expect.soft(w9.batch.priority, '① ชุดยังเป็นงานปกติ').toBe('normal');
    expect.soft(w9.batch.accepted, '① รับไว้ 11 ใบ').toBe(11);
    await expect.soft(page.getByTestId('batch-priority'), '① batch-priority ไม่ใช่ด่วน').not.toContainText('ด่วน');
    expect.soft(await usedToday(lead), '① ตัวนับด่วนวันนี้ยังเป็น 0').toBe(0);

    // ② จดจำนวนใบทั้งระบบและ ID แล้วอัปโหลด 11 ไฟล์ติ๊กด่วนตอนอัปโหลด
    const before = await allReceipts(lead);
    const beforeIds = new Set(before.map(r => r.id));
    const recBefore = await reconcile(lead);
    let resp = await uploadViaPage(page, cl2, okFiles(11, 20), true);
    await shot(testInfo, page, '② อัปโหลด 11 ไฟล์ติ๊กด่วน');
    if (!resp) { // the page blocked before sending -> same request via API (plan section 4)
      testInfo.annotations.push({ type: 'note', description: 'หน้าเว็บกันไว้ก่อนส่ง จึงยิง W7 urgent=true ด้วย API' });
      resp = await upload(lead, { clientId: cl2, files: okFiles(11, 20), urgent: true });
    }
    await evidence(testInfo, '② W7 11 ไฟล์ urgent=true', resp);
    const afterList = await allReceipts(lead);
    const newOnes = afterList.filter(r => !beforeIds.has(r.id));
    const recAfter = await reconcile(lead);
    await evidence(testInfo, '② ใบใหม่', { before: before.length, after: afterList.length, reconcileBefore: recBefore, reconcileAfter: recAfter, newIds: newOnes.map(r => ({ id: r.id, priority: r.priority, batchId: r.batchId })) });
    expect.soft([0, 11], `② จำนวนใบใหม่ = 0 หรือ 11 เท่านั้น (ได้ ${newOnes.length})`).toContain(newOnes.length);
    expect.soft(recAfter.accepted - recBefore.accepted, '② ยอดรับแล้วเพิ่ม = จำนวนใบใหม่').toBe(newOnes.length);
    if (newOnes.length === 11) {
      expect.soft(newOnes.filter(r => r.priority !== 'normal').map(r => r.id), '② ถ้ารับ 11 ทุกใบเป็นงานปกติ').toEqual([]);
    }
    expect.soft(await usedToday(lead), '② ตัวนับด่วนยังเป็น 0').toBe(0);
    pendingAP(testInfo, 'AP-02', `W7 11 ไฟล์ urgent=true → HTTP ${resp.status} ${resp.json?.error ?? ''} · ใบใหม่ ${newOnes.length} ใบ (${newOnes.length === 0 ? 'ปฏิเสธทั้งชุด' : newOnes.length === 11 ? 'รับเป็นงานปกติ' : 'รับครึ่งชุด'})`);
  } finally {
    resumeReader();
    await context.close();
    await lead.dispose();
  }
});

// ================================================================= TC-4-03
test('TC-4-03 โควตาวันนี้ใช้ไป 4 → งานที่ 5 ได้', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  await reset(M_URL, { urgentToday: 4 });
  const lead = await apiAs(M_URL, 'U03');
  const { context, page } = await pageAs(browser, M_URL, 'U03');
  try {
    const cl2 = await clientId(lead, 'CL-02');
    expect.soft(await usedToday(lead), 'ก่อนเริ่ม ใช้ไป 4').toBe(4);
    const r = await upload(lead, { clientId: cl2, files: okFiles(5, 1), urgent: true });
    await evidence(testInfo, 'W7 5 ไฟล์ urgent=true', r);
    expect.soft(r.status, 'ตั้งได้ (รับชุด)').toBe(201);
    expect.soft(r.json.accepted, 'รับ 5 ใบ').toBe(5);
    expect.soft(r.json.priority, 'ชุดเป็นงานด่วน').toBe('urgent');
    const q = await queue(lead);
    await evidence(testInfo, 'W23 หลังตั้ง', q);
    expect.soft(q.urgent.usedToday, 'ตัวนับ 4 + 1 = 5').toBe(5);
    expect.soft(q.urgent.limitPerDay, '/ 5').toBe(5);
    if (r.json.batchId) {
      await page.goto(`/batches/${r.json.batchId}`);
      await expect.soft(page.getByTestId('batch-priority'), 'batch-priority = ด่วน').toContainText('ด่วน');
      await shot(testInfo, page, 'หน้าชุดงานด่วนที่ 5');
    }
  } finally {
    await context.close();
    await lead.dispose();
  }
});

// ================================================================= TC-4-04
test('TC-4-04 โควตาครบ 5 → งานที่ 6 ไม่ได้ทุกช่องทาง', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  // reset wipes the users and their sessions -> log in again after every reset
  let lead!: APIRequestContext; let context!: BrowserContext; let page!: Page;
  const login = async () => {
    lead = await apiAs(M_URL, 'U03');
    ({ context, page } = await pageAs(browser, M_URL, 'U03'));
    autoAcceptDialogs(page);
  };
  const logout = async () => { await context?.close().catch(() => {}); await lead?.dispose().catch(() => {}); };
  try {
    // ① รีเซ็ต urgentToday 5
    await reset(M_URL, { urgentToday: 5 });
    await login();
    pauseReader();
    try {
      const cl2 = await clientId(lead, 'CL-02');
      expect.soft(await usedToday(lead), '① ก่อนเริ่ม 5 / 5').toBe(5);
      // (ก) อัปโหลด 5 ไฟล์ติ๊กด่วน (ผ่านหน้า /upload)
      let a = await uploadViaPage(page, cl2, okFiles(5, 1), true);
      await shot(testInfo, page, '① (ก) อัปโหลดติ๊กด่วน งานที่ 6');
      if (!a) {
        testInfo.annotations.push({ type: 'note', description: '① (ก) หน้าเว็บกันไว้ก่อนส่ง จึงยิง W7 urgent=true ด้วย API' });
        a = await upload(lead, { clientId: cl2, files: okFiles(5, 1), urgent: true });
      }
      await evidence(testInfo, '① (ก) W7 urgent=true', a);
      expect.soft(a.status, '① (ก) 409').toBe(409);
      expect.soft(a.json?.error, '① (ก) urgent_quota').toBe('urgent_quota');
      expect.soft(await usedToday(lead), '① (ก) ตัวนับยังเป็น 5').toBe(5);
      // (ข) อัปโหลดปกติแล้วกดปุ่มด่วน
      const nb = await upload(lead, { clientId: cl2, files: okFiles(5, 10) });
      expect(nb.status, '① (ข) อัปโหลดปกติ').toBe(201);
      const b = await urgentViaPage(page, nb.json.batchId);
      await evidence(testInfo, '① (ข) W10', b);
      await shot(testInfo, page, '① (ข) กดปุ่มด่วน งานที่ 6');
      expect.soft(b.resp?.status, '① (ข) 409').toBe(409);
      expect.soft(b.resp?.json?.error, '① (ข) urgent_quota').toBe('urgent_quota');
      expect.soft((await batchOf(lead, nb.json.batchId)).batch.priority, '① (ข) ชุดยังเป็นปกติ').toBe('normal');
      const q1 = await queue(lead);
      expect.soft(q1.urgent.usedToday, '① ตัวนับยังเป็น 5').toBe(5);
      expect.soft(q1.urgent.limitPerDay, '① / 5').toBe(5);
    } finally {
      resumeReader();
    }

    // ② รีเซ็ตตั้งต้น · 3 งานด้วยปุ่ม + 2 งานด้วยการติ๊กตอนอัปโหลด
    await logout();
    await reset(M_URL);
    await login();
    pauseReader();
    try {
      const cl2 = await clientId(lead, 'CL-02');
      expect.soft(await usedToday(lead), '② ก่อนเริ่ม 0').toBe(0);
      let from = 30;
      const log: any[] = [];
      for (let i = 1; i <= 3; i++) {
        const nb = await upload(lead, { clientId: cl2, files: okFiles(5, from) }); from += 5;
        expect(nb.status, `② ชุดปกติที่ ${i}`).toBe(201);
        const u = await urgentViaPage(page, nb.json.batchId);
        log.push({ via: 'W10', i, resp: u.resp });
        expect.soft(u.resp?.status, `② งานที่ ${i} (ปุ่ม) ตั้งได้`).toBe(200);
        expect.soft(await usedToday(lead), `② ตัวนับ ${i}`).toBe(i);
      }
      for (let i = 4; i <= 5; i++) {
        const r = await upload(lead, { clientId: cl2, files: okFiles(5, from), urgent: true }); from += 5;
        log.push({ via: 'W7', i, status: r.status, json: r.json });
        expect.soft(r.status, `② งานที่ ${i} (ติ๊กตอนอัปโหลด) ตั้งได้`).toBe(201);
        expect.soft(r.json.priority, `② งานที่ ${i} เป็นงานด่วน`).toBe('urgent');
        expect.soft(await usedToday(lead), `② ตัวนับ ${i}`).toBe(i);
      }
      // งานที่ 6 ทั้ง 2 ช่องทาง
      const w7 = await upload(lead, { clientId: cl2, files: okFiles(5, from), urgent: true }); from += 5;
      log.push({ via: 'W7', i: 6, status: w7.status, json: w7.json });
      expect.soft(w7.status, '② งานที่ 6 W7 → 409').toBe(409);
      expect.soft(w7.json?.error, '② งานที่ 6 W7 urgent_quota').toBe('urgent_quota');
      const nb6 = await upload(lead, { clientId: cl2, files: okFiles(5, from) });
      expect(nb6.status, '② ชุดปกติสำหรับงานที่ 6').toBe(201);
      const w10 = await urgentViaPage(page, nb6.json.batchId);
      log.push({ via: 'W10', i: 6, resp: w10.resp });
      await shot(testInfo, page, '② งานที่ 6 กดปุ่มด่วน');
      expect.soft(w10.resp?.status, '② งานที่ 6 W10 → 409').toBe(409);
      expect.soft(w10.resp?.json?.error, '② งานที่ 6 W10 urgent_quota').toBe('urgent_quota');
      const q2 = await queue(lead);
      await evidence(testInfo, '② ลำดับการตั้งด่วน', { log, w23: q2 });
      expect.soft(q2.urgent.usedToday, '② ตัวนับ 5 / 5').toBe(5);
      expect.soft(q2.urgent.limitPerDay, '② / 5').toBe(5);
    } finally {
      resumeReader();
    }
    pendingAP(testInfo, 'AP-05', 'โควตาทั้งสำนักงานทดสอบด้วยหัวหน้าคนเดียว (U-03) ผ่าน 2 ช่องทาง · การทดสอบด้วยหัวหน้า 2 คนรอ U-07');
  } finally {
    await logout();
  }
});

// ================================================================= TC-4-05
test('TC-4-05 วันใหม่เริ่มนับ 0', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  await reset(M_URL, { urgentYesterday: 5, urgentToday: 0 });
  const lead = await apiAs(M_URL, 'U03');
  const { context, page } = await pageAs(browser, M_URL, 'U03');
  try {
    const cl2 = await clientId(lead, 'CL-02');
    const q0 = await queue(lead);
    await evidence(testInfo, 'W23 ก่อนเริ่ม', q0);
    expect.soft(q0.urgent.usedToday, 'งานเมื่อวาน 23:59 ไม่ถูกนับในวันนี้ (0)').toBe(0);
    const r = await upload(lead, { clientId: cl2, files: okFiles(5, 1), urgent: true });
    await evidence(testInfo, 'W7 5 ไฟล์ urgent=true', r);
    expect.soft(r.status, 'ตั้งได้').toBe(201);
    expect.soft(r.json.priority, 'ชุดเป็นงานด่วน').toBe('urgent');
    expect.soft(await usedToday(lead), 'ตัวนับวันนี้ 0 + 1 = 1').toBe(1);
    if (r.json.batchId) {
      await page.goto(`/batches/${r.json.batchId}`);
      await expect.soft(page.getByTestId('batch-priority'), 'batch-priority = ด่วน').toContainText('ด่วน');
      await shot(testInfo, page, 'หน้าชุดงานด่วนวันใหม่');
    }
  } finally {
    await context.close();
    await lead.dispose();
  }
});

// ================================================================= TC-4-06
test('TC-4-06 งานด่วนไม่ติดเพดานคิว', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  await reset(M_URL, { pendingNormal: 400 });
  const lead = await apiAs(M_URL, 'U03');
  const staff = await apiAs(M_URL, 'U01');
  const { context, page } = await pageAs(browser, M_URL, 'U01');
  try {
    const cl2 = await clientId(lead, 'CL-02');
    const cl1 = await clientId(staff, 'CL-01');
    // ① U-03 10 ไฟล์ติ๊กด่วน
    const u = await upload(lead, { clientId: cl2, files: okFiles(10, 1), urgent: true });
    await evidence(testInfo, '① W7 10 ไฟล์ urgent=true', u);
    expect.soft(u.status, '① รับชุดด่วน').toBe(201);
    expect.soft(u.json.accepted, '① รับ 10').toBe(10);
    const q = await queue(lead);
    await evidence(testInfo, '① W23', q);
    expect.soft(q.normal.pending, '① ใบงานปกติค้างยังเป็น 400').toBe(400);
    // ② U-01 1 ไฟล์ปกติ (ผ่านหน้า /upload)
    let n = await uploadViaPage(page, cl1, okFiles(1, 50), false);
    await shot(testInfo, page, '② U-01 ส่ง 1 ไฟล์ขณะคิวเต็ม');
    if (!n) {
      testInfo.annotations.push({ type: 'note', description: '② หน้าเว็บกันไว้ก่อนส่ง จึงยิง W7 ด้วย API' });
      n = await upload(staff, { clientId: cl1, files: okFiles(1, 50) });
    }
    await evidence(testInfo, '② W7 1 ไฟล์ปกติ', n);
    expect.soft(n.status, '② 400 + 1 = 401 > 400 → 429').toBe(429);
    expect.soft(n.json?.error, '② queue_full').toBe('queue_full');
    expect.soft(n.json?.retryAfterMinutes, '② N = ปัดขึ้น(1 ÷ 8) = 1 นาที').toBe(1);
    await expect.soft(page.getByTestId('upload-retry-minutes'), '② upload-retry-minutes = 1').toHaveText(/^\D*1\D*$/);
  } finally {
    await context.close();
    await lead.dispose();
    await staff.dispose();
  }
});

// ================================================================= TC-4-07 ★
test('TC-4-07 ★ งานด่วน 10 ใบมีผลภายใน 5 นาที (smoke ของ NFR-03)', { tag: ['@P1', '@R'] }, async ({}, testInfo) => {
  testInfo.annotations.push({ type: 'blocked', description: 'รอบปล่อยรุ่น ★: ต้องใช้ใบจริง 100 ไฟล์ เกินงบรอบปกติ/งบของขั้นนี้ (120 ใบ) และต้องได้อนุมัติหัวหน้าทีมทดสอบ' });
  test.skip(true, 'รอบปล่อยรุ่น ★ เท่านั้น (2 × 50 ไฟล์จริง ต้องได้อนุมัติหัวหน้าทีมทดสอบ)');
});

// ================================================================= TC-4-08
type Shape = { key: 'a' | 'b' | 'c' | 'd'; u: number; n: number; expected: string[] };
const SHAPES: Shape[] = [
  { key: 'a', u: 3, n: 2, expected: ['U1', 'U2', 'U3', 'N1', 'N2'] },
  { key: 'b', u: 4, n: 2, expected: ['U1', 'U2', 'U3', 'U4', 'N1', 'N2'] },
  { key: 'c', u: 5, n: 2, expected: ['U1', 'U2', 'U3', 'U4', 'N1', 'U5', 'N2'] },
  { key: 'd', u: 5, n: 0, expected: ['U1', 'U2', 'U3', 'U4', 'U5'] },
];

/** Parse `gpu.sh log worker0` -> per receipt id: go events (queue, attempt) and read events, in log order. */
function parseWorkerLog(log: string) {
  const goOrder: { id: string; queue: string; attempt: number; time: string }[] = [];
  const reads: { id: string; ok: string; outcome: string }[] = [];
  for (const line of log.split(/\r?\n/)) {
    const g = line.match(/^(\S+ \S+) .*receipt=([0-9a-f-]{36}) go queue=(urgent|normal) attempt=(\d+)/);
    if (g) { goOrder.push({ time: g[1], id: g[2], queue: g[3], attempt: Number(g[4]) }); continue; }
    const r = line.match(/receipt=([0-9a-f-]{36}) read ok=(True|False).*-> (\w+)/);
    if (r) reads.push({ id: r[1], ok: r[2], outcome: r[3] });
  }
  return { goOrder, reads };
}

async function healthWorkers(baseURL: string): Promise<number | undefined> {
  const ctx = await apiAs(baseURL, null);
  try { return (await (await ctx.get('/api/health')).json())?.ai?.workersAlive; } finally { await ctx.dispose(); }
}
async function waitWorkersAlive(baseURL: string, n: number, timeoutMs = 120_000) {
  const end = Date.now() + timeoutMs; let last: number | undefined;
  while (Date.now() < end) {
    last = await healthWorkers(baseURL).catch(() => undefined);
    if (last === n) return last;
    await new Promise(r => setTimeout(r, 5000));
  }
  return last;
}

test('TC-4-08 ลำดับอ่าน 4:1 ครบ 4 รูปคิว', { tag: ['@P2', '@R'] }, async ({ browser }, testInfo) => {
  test.setTimeout(40 * 60_000);

  // ---- E6: real images · reset :3420 · W23 · workers
  const gt: { file: string }[] = JSON.parse(fs.readFileSync(path.join(REAL_IMAGES, 'ground_truth.json'), 'utf8'));
  const pool = gt.map(g => g.file);
  expect(pool.length, 'E6 ground_truth 12 ใบ').toBe(12);
  for (const f of pool) expect(fs.existsSync(path.join(REAL_IMAGES, f)), `E6 มีไฟล์ ${f}`).toBe(true);
  await reset(R_URL);
  const lead = await apiAs(R_URL, 'U03');
  const q0 = await queue(lead);
  await evidence(testInfo, 'E6 W23 หลังรีเซ็ต', q0);
  expect(q0.normal.pending, 'E6 ใบงานปกติค้าง 0').toBe(0);
  expect(q0.urgent.usedToday, 'E6 งานด่วนวันนี้ 0').toBe(0);
  expect(q0.urgent.limitPerDay, 'E6 / 5').toBe(5);
  expect(q0.workers.alive, 'E6 W23 workers alive 2').toBe(2);
  expect(await healthWorkers(R_URL), 'E6 /api/health workersAlive 2').toBe(2);
  testInfo.annotations.push({ type: 'note', description: 'E6: คิวที่ gateway (GET /v1/queue) เรียกจากเครื่องทดสอบไม่ได้ จึงไม่ได้ตรวจในสเปกนี้' });

  const cl2 = await clientId(lead, 'CL-02');
  const dir = testInfo.outputPath('real-4-08'); fs.mkdirSync(dir, { recursive: true });
  let k = 0;
  const realCopy = (shape: string, label: string) => {
    const src = pool[k++ % pool.length];
    const dst = path.join(dir, `${path.parse(src).name}__4-08${shape}-${label}.jpg`);
    fs.copyFileSync(path.join(REAL_IMAGES, src), dst);
    return dst;
  };

  const { context, page } = await pageAs(browser, R_URL, 'U03');
  const summary: Record<string, unknown> = {};
  try {
    for (const s of SHAPES) {
      // ① stop both workers (the web still accepts)
      await evidence(testInfo, `${s.key} ① stop`, gpu('stop worker0 worker1'));

      // ② normal batch first, then urgent batch (ticked at upload)
      const label: Record<string, string> = {};
      let normal: any = null;
      if (s.n > 0) {
        const files = Array.from({ length: s.n }, (_, i) => realCopy(s.key, `N${i + 1}`));
        const r = await upload(lead, { clientId: cl2, files, real: true });
        expect(r.status, `${s.key} ② ชุดปกติ ${s.n} ใบ`).toBe(201);
        expect(r.json.accepted).toBe(s.n);
        normal = r.json;
        for (let i = 0; i < s.n; i++) {
          const rec = r.json.receipts.find((x: any) => x.fileName === path.basename(files[i]));
          expect(rec, `${s.key} หา N${i + 1} จากชื่อไฟล์`).toBeTruthy();
          label[rec.id] = `N${i + 1}`;
        }
      }
      const ufiles = Array.from({ length: s.u }, (_, i) => realCopy(s.key, `U${i + 1}`));
      const ur = await upload(lead, { clientId: cl2, files: ufiles, urgent: true, real: true });
      await evidence(testInfo, `${s.key} ② W7 ชุดด่วน`, ur);
      expect(ur.status, `${s.key} ② ชุดด่วน ${s.u} ใบ`).toBe(201);
      expect(ur.json.priority, `${s.key} ② ชุดเป็นงานด่วน`).toBe('urgent');
      for (let i = 0; i < s.u; i++) {
        const rec = ur.json.receipts.find((x: any) => x.fileName === path.basename(ufiles[i]));
        expect(rec, `${s.key} หา U${i + 1} จากชื่อไฟล์`).toBeTruthy();
        label[rec.id] = `U${i + 1}`;
      }
      const ids = Object.keys(label);

      // ③ give the dispatcher time to hand them to the gateway, then check W23 / W9 that all are waiting
      await new Promise(r => setTimeout(r, 20_000));
      const q = await queue(lead);
      const w9u = await batchOf(lead, ur.json.batchId);
      const w9n = normal ? await batchOf(lead, normal.batchId) : null;
      await evidence(testInfo, `${s.key} ③ W23 + W9 ก่อนเปิด worker0`, { w23: q, urgentBatch: w9u.batch, normalBatch: w9n?.batch ?? null });
      expect.soft(q.urgent.pending, `${s.key} ③ W23 ใบด่วนรออ่าน ${s.u}`).toBe(s.u);
      expect.soft(q.normal.pending, `${s.key} ③ W23 ใบปกติรออ่าน ${s.n}`).toBe(s.n);
      expect.soft(w9u.batch.counts.queued, `${s.key} ③ หน้าชุดด่วน รออ่าน ${s.u}`).toBe(s.u);
      if (w9n) expect.soft(w9n.batch.counts.queued, `${s.key} ③ หน้าชุดปกติ รออ่าน ${s.n}`).toBe(s.n);
      await page.goto(`/batches/${ur.json.batchId}`);
      await expect.soft(page.getByTestId('batch-count-queued'), `${s.key} ③ batch-count-queued`).toHaveText(String(s.u));
      await shot(testInfo, page, `${s.key} ③ ชุดด่วนรออ่านก่อนเปิด worker0`);

      // ④ start worker0 only, wait until every receipt of the shape has a result
      await evidence(testInfo, `${s.key} ④ start worker0`, gpu('start worker0'));
      await waitStatus(lead, ids, ['review', 'unreadable'], 10 * 60_000);

      // ⑤ order of "go" events per id from the worker0 log (receipt=<id> is the web receipt id: DESIGN 5.3 receipt_ref = receipts.id)
      const log = gpu('log worker0');
      const { goOrder, reads } = parseWorkerLog(log);
      const mine = goOrder.filter(g => label[g.id]);
      const order = mine.map(g => label[g.id]);
      const perId = ids.map(id => ({
        label: label[id], id,
        go: goOrder.filter(g => g.id === id).length,
        read: reads.filter(r => r.id === id).length,
        queues: [...new Set(goOrder.filter(g => g.id === id).map(g => g.queue))],
      }));
      summary[s.key] = { expected: s.expected, observed: order, perId };
      await evidence(testInfo, `${s.key} ⑤ ลำดับหยิบงานจาก log worker0`, { expected: s.expected, observed: order, events: mine.map(g => ({ ...g, label: label[g.id] })), perId });
      await evidence(testInfo, `${s.key} ⑤ log worker0 (tail 40)`, log);
      expect.soft(perId.filter(p => p.go === 0).map(p => p.label), `${s.key} ⑤ ทุก ID ต้องมีเหตุการณ์หยิบใน log (tail 40)`).toEqual([]);
      // Uk/Nk in the plan = order of entering the queue at the gateway; the dispatcher does not enter receipts in
      // upload order, so upload labels cannot give the queue position. BR-10 is decided on the U/N sequence.
      const pattern = order.map(l => l[0]).join(' ');
      const expectedPattern = s.expected.map((l: string) => l[0]).join(' ');
      testInfo.annotations.push({ type: 'info', description: `${s.key}: ลำดับหยิบ (ป้ายตามลำดับอัปโหลด) ${order.join(' ')} · รูปแบบ ${pattern} · คาด ${expectedPattern}` });
      expect.soft(pattern, `${s.key} ⑤ ลำดับอ่าน (รูปแบบด่วน/ปกติ ตาม BR-10)`).toBe(expectedPattern);
      expect.soft(perId.filter(p => p.go !== 1 || p.read !== 1).map(p => `${p.label}: go=${p.go} read=${p.read}`), `${s.key} ทุก ID หยิบ 1 ครั้งและผล 1 ครั้ง`).toEqual([]);
      expect.soft(perId.filter(p => p.queues.some(qq => qq !== (p.label.startsWith('U') ? 'urgent' : 'normal'))).map(p => `${p.label}: ${p.queues}`), `${s.key} ใบ U มาจาก queue=urgent · ใบ N มาจาก queue=normal`).toEqual([]);
    }
  } finally {
    await evidence(testInfo, 'สรุปลำดับทุกรูปคิว', summary);
    let startOut = '';
    try { startOut = gpu('start worker0 worker1'); } catch (e) { startOut = `start failed: ${e}`; }
    await evidence(testInfo, 'จบ: start worker0 worker1', startOut);
    const alive = await waitWorkersAlive(R_URL, 2, 120_000);
    expect.soft(alive, 'จบด้วย workersAlive = 2').toBe(2);
    await context.close();
    await lead.dispose();
  }
});
