// Group 5.2 of ./test/TEST-PLAN.md · ผลตรวจของโมเดลกับกติกา ผ่าน / เตือน / ไม่ผ่าน
// (BR-01–BR-03 · FR-07–FR-09 · FR-11 · FR-12 · NFR-01)
// Expected values come ONLY from TEST-PLAN.md / docs/TEST-DATA.md, never from what the site shows.
import { test, expect, type Page, type TestInfo } from '@playwright/test';
import {
  UI, reset, login, cookieToContext, http, upload, waitBatchTerminal, allPhotos, fixture, testImage,
  useRealBudget, gateway, evidence, shot, blockedIfClean, RESULT_TH,
} from './helpers';
import * as path from 'node:path';
import * as fs from 'node:fs';

// ---------------- helpers local to this file ----------------

/** DESIGN 9.1: BR-01 → BR-02 → BR-03 in this order. */
function rule(h: number, v: number): 'PASS' | 'WARN' | 'FAIL' {
  if (h >= 1) return 'FAIL';   // BR-01 HELMET_FAIL_MIN = 1
  if (v >= 2) return 'FAIL';   // BR-02 VEST_FAIL_MIN = 2
  if (v >= 1) return 'WARN';   // BR-03 VEST_WARN_MIN = 1
  return 'PASS';
}

async function aiMode() {
  const r = await http('GET', '/api/health');
  return { status: r.status, mode: r.json?.ai_mode as string | undefined, health: r.json };
}

const MOCK_REASON = 'ต้องใช้ AI_MODE=mock (mock-gateway) ซึ่งเครื่องนี้ไม่มี';

/** R-1 – R-8 of TEST-DATA section 4 with the expected values (computed in the plan). */
const R_ROWS = [
  { id: 'R-1', file: 'h0_v0.jpg', h: 0, v: 0, exp: 'PASS', boxes: 0 },
  { id: 'R-2', file: 'h1_v0.jpg', h: 1, v: 0, exp: 'FAIL', boxes: 1 },
  { id: 'R-3', file: 'h2_v0.jpg', h: 2, v: 0, exp: 'FAIL', boxes: 2 },
  { id: 'R-4', file: 'h0_v1.jpg', h: 0, v: 1, exp: 'WARN', boxes: 1 },
  { id: 'R-5', file: 'h0_v2.jpg', h: 0, v: 2, exp: 'FAIL', boxes: 2 },
  { id: 'R-6', file: 'h0_v3.jpg', h: 0, v: 3, exp: 'FAIL', boxes: 3 },
  { id: 'R-7', file: 'h1_v1.jpg', h: 1, v: 1, exp: 'FAIL', boxes: 2 },
  { id: 'R-8', file: 'h1_v3.jpg', h: 1, v: 3, exp: 'FAIL', boxes: 4 },
] as const;

/** Mock only: U-2 uploads R-1..R-8 in one batch and waits until all are terminal. */
async function uploadRRows(cookie: string) {
  const up = await upload(cookie, R_ROWS.map(r => ({ path: fixture(r.file) })));
  for (const [i, it] of up.items.entries()) expect.soft(it.status, `${R_ROWS[i].id} ${R_ROWS[i].file} ต้องได้ 201`).toBe(201);
  const wait = await waitBatchTerminal(cookie, up.batchId, 3 * 60 * 1000);
  return { ...up, wait };
}

/** Wait until the photo detail page shows its image (natural size known). */
async function openDetail(page: Page, photoId: string) {
  await page.goto(`${UI}/photos/${photoId}`);
  const img = page.getByTestId('photo-image');
  await expect(img).toBeVisible();
  await page.waitForFunction(() => {
    const i = document.querySelector('[data-testid="photo-image"]') as HTMLImageElement | null;
    return !!i && i.complete && i.naturalWidth > 0;
  }, null, { timeout: 30000 });
}

/** Count rows over every page of a list (/photos or /photos/problems) by clicking "next" until disabled. */
async function uiRowsAllPages(page: Page, pagePrefix: 'photos' | 'problems') {
  const results: string[] = [];
  const seen = new Set<string>();
  for (let guard = 0; guard < 100; guard++) {
    await page.waitForTimeout(300);
    const rows = page.locator('tr[data-testid^="photo-row-"]');
    const n = await rows.count();
    for (let i = 0; i < n; i++) {
      const tid = (await rows.nth(i).getAttribute('data-testid')) || '';
      if (seen.has(tid)) continue;
      seen.add(tid);
      results.push((await rows.nth(i).getAttribute('data-result')) || '');
    }
    const next = page.getByTestId(`${pagePrefix}-page-next`);
    if (!(await next.count()) || (await next.isDisabled())) break;
    const before = page.url();
    await next.click();
    await page.waitForURL(u => u.toString() !== before, { timeout: 15000 }).catch(() => { });
    await page.waitForLoadState('networkidle').catch(() => { });
  }
  return { rows: results.length, results };
}

// =====================================================================

test.describe('5.2 ผลตรวจของโมเดลกับกติกา', () => {

  test('TC-2-01 [P1] ตัดสินผล 8 กรณี R-1–R-8 ตามลำดับ BR-01→BR-03', async ({ page }, testInfo) => {
    await reset();
    const cookie = await login('U2');
    const m = await aiMode();
    await evidence(testInfo, 'evidence', { tc: 'TC-2-01', health_status: m.status, ai_mode: m.mode, health: m.health, needs: 'ai_mode = mock' });
    await cookieToContext(page.context(), cookie);
    await page.goto(`${UI}/upload`);
    await shot(testInfo, page, 'upload-page');
    if (m.mode !== 'mock') { blockedIfClean(testInfo, MOCK_REASON); return; } // before any upload: no GPU spent

    // ---- runs only with AI_MODE=mock ----
    const up = await uploadRRows(cookie);
    const photos: any[] = up.wait.last?.photos || [];
    const got: any[] = [];
    for (const [i, r] of R_ROWS.entries()) {
      const id = up.items[i].photoId!;
      const p = photos.find(x => x.id === id);
      got.push({ ...r, photoId: id, status: p?.status, h: p?.h, v: p?.v, model_result: p?.model_result, current_result: p?.current_result });
      expect.soft(p?.status, `${r.id} ต้องถึง "เสร็จแล้ว" (DONE)`).toBe('DONE');
      expect.soft(p?.current_result, `${r.id} (${r.h},${r.v}) ต้องได้ ${RESULT_TH[r.exp]} (${r.exp})`).toBe(r.exp);
    }
    const sum = (x: string) => got.filter(g => g.current_result === x).length;
    expect.soft(sum('PASS'), 'รวมผ่านต้อง = 1').toBe(1);
    expect.soft(sum('WARN'), 'รวมเตือนต้อง = 1').toBe(1);
    expect.soft(sum('FAIL'), 'รวมไม่ผ่านต้อง = 6').toBe(6);
    // the batch status page (where the plan says to read the result)
    await page.goto(`${UI}/uploads/${up.batchId}`);
    for (const g of got) {
      const ui = await page.getByTestId(`batch-row-result-${g.photoId}`).getAttribute('data-result').catch(() => null);
      expect.soft(ui, `หน้าสถานะ ${g.id} ต้องแสดง ${g.exp}`).toBe(g.exp);
    }
    await shot(testInfo, page, 'batch-status');
    await evidence(testInfo, 'results', { batchId: up.batchId, elapsedMs: up.wait.elapsedMs, got });
  });

  test('TC-2-02 [P1] H, V และจำนวนกรอบของ 8 รูปตรงชื่อไฟล์', async ({ page }, testInfo) => {
    await reset();
    const cookie = await login('U2');
    const m = await aiMode();
    await evidence(testInfo, 'evidence', { tc: 'TC-2-02', health_status: m.status, ai_mode: m.mode, health: m.health, needs: 'ai_mode = mock' });
    await cookieToContext(page.context(), cookie);
    await page.goto(`${UI}/photos`);
    await shot(testInfo, page, 'photos-page');
    if (m.mode !== 'mock') { blockedIfClean(testInfo, MOCK_REASON); return; }

    // ---- runs only with AI_MODE=mock ----
    const up = await uploadRRows(cookie);
    const got: any[] = [];
    let totalBoxes = 0;
    for (const [i, r] of R_ROWS.entries()) {
      const id = up.items[i].photoId!;
      await openDetail(page, id);
      const h = (await page.getByTestId('photo-h').textContent())?.trim();
      const v = (await page.getByTestId('photo-v').textContent())?.trim();
      const boxes = page.locator('[data-testid^="photo-box-"]:not([data-testid^="photo-box-label-"])');
      const nBox = await boxes.count();
      const labels: string[] = [];
      for (let k = 0; k < nBox; k++) labels.push(((await page.getByTestId(`photo-box-label-${k}`).textContent()) || '').trim());
      totalBoxes += nBox;
      got.push({ ...r, photoId: id, h, v, nBox, labels });
      expect.soft(h, `${r.id} H ต้อง = ${r.h}`).toBe(String(r.h));
      expect.soft(v, `${r.id} V ต้อง = ${r.v}`).toBe(String(r.v));
      expect.soft(nBox, `${r.id} จำนวนกรอบต้อง = H + V = ${r.boxes}`).toBe(r.boxes);
      expect.soft(labels.filter(l => l === 'ไม่ใส่หมวก').length, `${r.id} ป้าย "ไม่ใส่หมวก" ต้อง = ${r.h} กรอบ`).toBe(r.h);
      expect.soft(labels.filter(l => l === 'ไม่ใส่เสื้อสะท้อนแสง').length, `${r.id} ป้าย "ไม่ใส่เสื้อสะท้อนแสง" ต้อง = ${r.v} กรอบ`).toBe(r.v);
      await shot(testInfo, page, `detail-${r.id}`);
    }
    expect.soft(totalBoxes, 'กรอบรวมต้อง = 15 (H รวม 5 + V รวม 10)').toBe(15);
    await evidence(testInfo, 'results', { batchId: up.batchId, got, totalBoxes });
  });

  test('TC-2-03 [P1] โมเดลจริง 6 รูป ค่า H, V ผล และตำแหน่งกรอบตรงกับ gateway', async ({ page }, testInfo) => {
    test.setTimeout(15 * 60 * 1000);
    await reset();
    const cookie = await login('U2');
    const m = await aiMode();
    expect.soft(m.mode, 'TC นี้ต้องรันด้วย ai_mode = real (gateway และโมเดลจริงบน GPU)').toBe('real');
    if (m.mode !== 'real') { await evidence(testInfo, 'evidence', { tc: 'TC-2-03', ai_mode: m.mode }); return; }

    const PREFIXES = ['-4405-_png_jpg', '000005_jpg', '002551_jpg', '003357_jpg', '004063_jpg', '004763_jpg'];
    const files = PREFIXES.map(p => testImage(p));
    const refJson = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', '..', '..', 'results', 'model', 'test_image_results.json'), 'utf8'));
    const ref: Record<string, { H: number; V: number }> = Object.fromEntries((refJson.images || []).map((x: any) => [x.image, { H: x.H, V: x.V }]));

    const budget = useRealBudget(6, 'TC-2-03');
    const up = await upload(cookie, files.map(f => ({ path: f })));
    for (const [i, it] of up.items.entries()) expect.soft(it.status, `${path.basename(files[i])} ต้องได้ 201`).toBe(201);
    const wait = await waitBatchTerminal(cookie, up.batchId, 5 * 60 * 1000, 3000);

    await cookieToContext(page.context(), cookie);
    const rows: any[] = [];
    const observations: string[] = [];
    let zeroZeroSeen = 0;
    for (const [i, it] of up.items.entries()) {
      const name = path.basename(files[i]);
      const id = it.photoId!;
      const row: any = { name, photoId: id };
      rows.push(row);
      const bp = (wait.last?.photos || []).find((x: any) => x.id === id);
      row.batch_status = bp?.status;
      expect.soft(bp?.status, `${name} ต้องถึง "เสร็จแล้ว" (DONE) ภายใน 5 นาที`).toBe('DONE');
      if (!id) continue;

      // gateway (job_id = photo id)
      const g = await gateway('GET', `/v1/jobs/${id}`, 'good');
      const gr = g.json?.result;
      row.gateway = { status: g.status, job_status: g.json?.status, h: gr?.h, v: gr?.v, image_w: gr?.image_w, image_h: gr?.image_h, conf_threshold: gr?.conf_threshold, model_version: gr?.model_version, detections: gr?.detections };
      expect.soft(g.status, `${name} gateway GET /v1/jobs/{id} ต้องได้ 200`).toBe(200);
      expect.soft(g.json?.status, `${name} งานบน gateway ต้องเป็น DONE`).toBe('DONE');
      if (!gr) continue;
      const gh = Number(gr.h), gv = Number(gr.v);
      const expResult = rule(gh, gv);
      row.expected_result = expResult;

      // web API
      const w = await http('GET', `/api/photos/${id}`, { cookie });
      const wp = w.json?.photo || w.json;
      row.web = { status: w.status, h: wp?.h, v: wp?.v, model_result: wp?.model_result, current_result: wp?.current_result, image_w: wp?.image_w, image_h: wp?.image_h, detections: wp?.detections };
      expect.soft(wp?.h, `${name} H บนเว็บต้อง = result.h ของ gateway (${gh})`).toBe(gh);
      expect.soft(wp?.v, `${name} V บนเว็บต้อง = result.v ของ gateway (${gv})`).toBe(gv);
      expect.soft(wp?.model_result, `${name} ผลของโมเดลบนเว็บต้อง = BR-01→BR-03 จาก (${gh},${gv}) = ${expResult}`).toBe(expResult);
      expect.soft(wp?.current_result, `${name} ผลล่าสุด (ยังไม่มีการแก้) ต้อง = ${expResult}`).toBe(expResult);

      // gateway boxes that count (confidence ≥ conf_threshold) – DESIGN 5.1: h/v are those boxes
      const thr = typeof gr.conf_threshold === 'number' ? gr.conf_threshold : 0;
      const gBoxes = (gr.detections || []).filter((d: any) => d.confidence >= thr && (d.cls === 'NO_HARDHAT' || d.cls === 'NO_VEST'));
      expect.soft(gBoxes.length, `${name} กรอบของ gateway (conf ≥ ${thr}) ต้อง = H + V = ${gh + gv}`).toBe(gh + gv);

      // UI detail page
      await openDetail(page, id);
      const uiH = (await page.getByTestId('photo-h').textContent())?.trim();
      const uiV = (await page.getByTestId('photo-v').textContent())?.trim();
      const uiModel = await page.getByTestId('photo-model-result').getAttribute('data-result');
      const uiCur = await page.getByTestId('photo-current-result').getAttribute('data-result');
      expect.soft(uiH, `${name} หน้ารายละเอียด H ต้อง = ${gh}`).toBe(String(gh));
      expect.soft(uiV, `${name} หน้ารายละเอียด V ต้อง = ${gv}`).toBe(String(gv));
      expect.soft(uiModel, `${name} หน้ารายละเอียด ผลของโมเดลต้อง = ${expResult}`).toBe(expResult);
      expect.soft(uiCur, `${name} หน้ารายละเอียด ผลล่าสุดต้อง = ${expResult}`).toBe(expResult);

      const imgBox = await page.getByTestId('photo-image').boundingBox();
      const boxLoc = page.locator('[data-testid^="photo-box-"]:not([data-testid^="photo-box-label-"])');
      const nUi = await boxLoc.count();
      const uiBoxes: { i: number; cls: string | null; bb: any }[] = [];
      for (let k = 0; k < nUi; k++) {
        const el = page.getByTestId(`photo-box-${k}`);
        uiBoxes.push({ i: k, cls: await el.getAttribute('data-cls'), bb: await el.boundingBox() });
      }
      row.ui = { h: uiH, v: uiV, model: uiModel, current: uiCur, image_box: imgBox, boxes: uiBoxes };
      expect.soft(nUi, `${name} จำนวนกรอบที่วาดต้อง = H + V = ${gh + gv}`).toBe(gh + gv);
      if (gh === 0 && gv === 0) { zeroZeroSeen++; expect.soft(nUi, `${name} รูป (0,0) ต้องไม่มีกรอบ`).toBe(0); }

      // position: gateway box × (displayed width ÷ image_w), within 2 px
      if (imgBox && gr.image_w && gr.image_h) {
        const sx = imgBox.width / gr.image_w;
        const sy = imgBox.height / gr.image_h;
        row.scale = { sx, sy };
        const used = new Set<number>();
        row.box_compare = [];
        for (const d of gBoxes) {
          const [x1, y1, x2, y2] = d.box;
          const exp = { x1: imgBox.x + x1 * sx, y1: imgBox.y + y1 * sy, x2: imgBox.x + x2 * sx, y2: imgBox.y + y2 * sy };
          let best: any = null; let bestErr = Infinity;
          for (const u of uiBoxes) {
            if (used.has(u.i) || !u.bb || (u.cls && u.cls !== d.cls)) continue;
            const err = Math.max(Math.abs(u.bb.x - exp.x1), Math.abs(u.bb.y - exp.y1), Math.abs(u.bb.x + u.bb.width - exp.x2), Math.abs(u.bb.y + u.bb.height - exp.y2));
            if (err < bestErr) { bestErr = err; best = u; }
          }
          if (best) used.add(best.i);
          row.box_compare.push({ cls: d.cls, gateway_box: d.box, expected_px: exp, ui_index: best?.i ?? null, max_err_px: best ? Number(bestErr.toFixed(2)) : null });
          expect.soft(best, `${name} กรอบ ${d.cls} ${JSON.stringify(d.box)} ต้องมีกรอบคลาสเดียวกันบนหน้าเว็บ`).not.toBeNull();
          if (best) expect.soft(bestErr, `${name} กรอบ ${d.cls} ${JSON.stringify(d.box)} คลาดจาก box × อัตราย่อ ต้องไม่เกิน 2 px`).toBeLessThanOrEqual(2);
        }
      }
      await shot(testInfo, page, `detail-${PREFIXES[i]}`);

      // reference values: an observation only, not a failure
      const r = ref[name];
      row.reference = r || null;
      if (r && (r.H !== gh || r.V !== gv)) {
        const note = `${name}: test_image_results.json (H=${r.H},V=${r.V}) ≠ gateway (H=${gh},V=${gv}) – ข้อสังเกตรุ่นโมเดล`;
        observations.push(note);
        testInfo.annotations.push({ type: 'observation', description: note });
      }
    }
    if (zeroZeroSeen === 0) {
      const note = 'ไม่มีรูปที่ gateway ให้ (0,0) ใน 6 รูป จึงตรวจข้อ "รูป (0,0) ไม่มีกรอบ" ไม่ได้ในรอบนี้';
      observations.push(note);
      testInfo.annotations.push({ type: 'observation', description: note });
    }
    await evidence(testInfo, 'evidence', { tc: 'TC-2-03', ai_mode: m.mode, gpu_budget_total_after: budget, batchId: up.batchId, elapsedMs: wait.elapsedMs, upload_status: up.items.map(x => x.status), rows, observations });
  });

  test('TC-2-04 [P1] รูปที่มีปัญหา มีเฉพาะไม่ผ่านและเตือน (ผลล่าสุด)', async ({ page }, testInfo) => {
    await reset();
    const u1 = await login('U1');
    const cases = [
      { date: '2026-11-16', site: 'SITE-A', total: 31, fail: 20, warn: 11, label: 'D1 · SITE-A' },
      { date: '2026-11-18', site: 'SITE-A', total: 30, fail: 19, warn: 11, label: 'D3 · SITE-A' },
    ];
    const ev: any[] = [];
    for (const c of cases) {
      const a = await allPhotos(u1, `date=${c.date}&site=${c.site}&problems=1`);
      const passIn = a.photos.filter((p: any) => p.current_result === 'PASS').length;
      const failN = a.photos.filter((p: any) => p.current_result === 'FAIL').length;
      const warnN = a.photos.filter((p: any) => p.current_result === 'WARN').length;
      expect.soft(a.status, `${c.label} API ต้องได้ 200`).toBe(200);
      expect.soft(a.total, `${c.label} API total ต้อง = ${c.fail} + ${c.warn} = ${c.total}`).toBe(c.total);
      expect.soft(a.photos.length, `${c.label} นับทุกหน้าต้อง = ${c.total}`).toBe(c.total);
      expect.soft(failN, `${c.label} ไม่ผ่าน (ผลล่าสุด) ต้อง = ${c.fail}`).toBe(c.fail);
      expect.soft(warnN, `${c.label} เตือน ต้อง = ${c.warn}`).toBe(c.warn);
      expect.soft(passIn, `${c.label} ต้องไม่มีรูปที่ผลล่าสุด "ผ่าน" ปน`).toBe(0);

      // UI as U-1
      const ctx = page.context();
      await cookieToContext(ctx, u1);
      await page.goto(`${UI}/photos/problems`);
      await page.getByTestId('problems-filter-date').fill(c.date);
      await page.getByTestId('problems-filter-site').selectOption(c.site);
      await page.getByTestId('problems-filter-apply').click();
      await page.waitForURL(u => u.search.includes(c.date), { timeout: 15000 }).catch(() => { });
      await page.waitForLoadState('networkidle').catch(() => { });
      const uiTotal = (await page.getByTestId('problems-total-count').textContent())?.trim();
      const uiFail = (await page.getByTestId('problems-count-fail').textContent())?.trim();
      const uiWarn = (await page.getByTestId('problems-count-warn').textContent())?.trim();
      await shot(testInfo, page, `problems-${c.date}-${c.site}`);
      const rowsAll = await uiRowsAllPages(page, 'problems');
      expect.soft(uiTotal, `${c.label} หน้าเว็บ problems-total-count ต้อง = ${c.total}`).toBe(String(c.total));
      expect.soft(uiFail, `${c.label} หน้าเว็บ ไม่ผ่าน ต้อง = ${c.fail}`).toBe(String(c.fail));
      expect.soft(uiWarn, `${c.label} หน้าเว็บ เตือน ต้อง = ${c.warn}`).toBe(String(c.warn));
      expect.soft(rowsAll.rows, `${c.label} แถวบนหน้าเว็บ (ทุกหน้า) ต้อง = ${c.total}`).toBe(c.total);
      expect.soft(rowsAll.results.filter(r => r === 'PASS').length, `${c.label} แถวบนหน้าเว็บต้องไม่มี "ผ่าน"`).toBe(0);
      ev.push({ ...c, api: { status: a.status, total: a.total, counts: a.counts, listed: a.photos.length, fail: failN, warn: warnN, pass: passIn }, ui: { total: uiTotal, fail: uiFail, warn: uiWarn, rows: rowsAll.rows, pass_rows: rowsAll.results.filter(r => r === 'PASS').length } });
    }
    const m = await aiMode();
    await evidence(testInfo, 'evidence', { tc: 'TC-2-04', ai_mode: m.mode, seed_views: ev, today_part: 'ต้องใช้ผลของ TC-2-01 (mock): วันนี้ ไม่ผ่าน 6 + เตือน 1 = 7' });

    // "today" part = continues from TC-2-01 (R-1..R-8 via mock-gateway)
    if (m.mode !== 'mock') { blockedIfClean(testInfo, 'ส่วน "วันนี้ = 7 รูป" ต่อจาก TC-2-01 ' + MOCK_REASON); return; }
    const u2 = await login('U2');
    const up = await uploadRRows(u2);
    const today = String(m.health?.time || '').slice(0, 10) || '2026-11-19';
    const a = await allPhotos(u2, `date=${today}&site=SITE-A&problems=1`);
    expect.soft(a.total, `วันนี้ (${today}) SITE-A ต้อง = ไม่ผ่าน 6 + เตือน 1 = 7`).toBe(7);
    expect.soft(a.photos.filter((p: any) => p.current_result === 'PASS').length, 'วันนี้ต้องไม่มีรูป "ผ่าน" ปน').toBe(0);
    await evidence(testInfo, 'today', { batchId: up.batchId, today, total: a.total, counts: a.counts });
  });

  test('TC-2-05 [P1] รอบ B วัด Recall และ Precision บน Test Set', async ({ page }, testInfo) => {
    await reset();
    const cookie = await login('U1');
    const thr = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', '..', '..', 'results', 'model', 'threshold.json'), 'utf8'));
    await cookieToContext(page.context(), cookie);
    await page.goto(`${UI}/reports/daily`);
    await shot(testInfo, page, 'report-page');
    await evidence(testInfo, 'evidence', {
      tc: 'TC-2-05', round: 'B', threshold_json: thr,
      needs: ['อนุมัติงบ GPU แยก (Entry E-6)', 'Test Set แยกจากชุดเทรน/Validation: Positive ≥ 100 · Negative ≥ 100 เฉลยโดยคน (AS-14)'],
      pass_rule: 'Recall = TP ÷ (TP + FN) ≥ 0.80 และ Precision = TP ÷ (TP + FP) ≥ 0.80 ที่ conf_threshold 0.32',
    });
    blockedIfClean(testInfo, 'รอบ B: ต้องได้อนุมัติงบ GPU แยก และ Test Set ที่มี Positive ≥ 100 · Negative ≥ 100 (เฉลยโดยคน) ซึ่งยังไม่มี');
  });

  test('TC-2-06 [P2] กรองรูปทั้งหมดตามผล ผ่าน 269 · เตือน 11 · ไม่กรอง 300', async ({ page }, testInfo) => {
    test.setTimeout(10 * 60 * 1000);
    await reset();
    const cookie = await login('U2');
    await cookieToContext(page.context(), cookie);
    const cases = [
      { result: 'PASS', total: 269 },
      { result: 'WARN', total: 11 },
      { result: '', total: 300 },
    ];
    const ev: any[] = [];
    for (const c of cases) {
      const label = c.result ? `กรอง "${RESULT_TH[c.result]}"` : 'ไม่กรองผล';
      const q = `date=2026-11-16&site=SITE-A${c.result ? `&result=${c.result}` : ''}`;
      const a = await allPhotos(cookie, q);
      const wrong = c.result ? a.photos.filter((p: any) => p.current_result !== c.result).length : 0;
      expect.soft(a.status, `${label} API ต้องได้ 200`).toBe(200);
      expect.soft(a.total, `${label} API total ต้อง = ${c.total}`).toBe(c.total);
      expect.soft(a.photos.length, `${label} นับทุกหน้าใน API ต้อง = ${c.total}`).toBe(c.total);
      if (c.result) expect.soft(wrong, `${label} ทุกรูปต้องมีผลล่าสุด ${c.result}`).toBe(0);
      else expect.soft(a.photos.every((p: any) => p.site?.code === 'SITE-A' && p.upload_date === '2026-11-16'), 'ไม่กรองผล: ทุกรูปเป็น D1 · SITE-A').toBe(true);

      // UI
      await page.goto(`${UI}/photos`);
      await page.getByTestId('photos-filter-date').fill('2026-11-16');
      await page.getByTestId('photos-filter-result').selectOption(c.result);
      await page.getByTestId('photos-filter-apply').click();
      await page.waitForURL(u => u.search.includes('2026-11-16'), { timeout: 15000 }).catch(() => { });
      await page.waitForLoadState('networkidle').catch(() => { });
      const uiTotal = (await page.getByTestId('photos-total-count').textContent())?.trim();
      await shot(testInfo, page, `photos-${c.result || 'ALL'}`);
      const rowsAll = await uiRowsAllPages(page, 'photos');
      const uiWrong = c.result ? rowsAll.results.filter(r => r !== c.result).length : 0;
      expect.soft(uiTotal, `${label} หน้าเว็บ photos-total-count ต้อง = ${c.total}`).toBe(String(c.total));
      expect.soft(rowsAll.rows, `${label} แถวบนหน้าเว็บ (ทุกหน้า) ต้อง = ${c.total}`).toBe(c.total);
      if (c.result) expect.soft(uiWrong, `${label} ทุกแถวบนหน้าเว็บต้องเป็น ${c.result}`).toBe(0);
      ev.push({ ...c, api: { status: a.status, total: a.total, counts: a.counts, listed: a.photos.length, wrong }, ui: { total: uiTotal, rows: rowsAll.rows, wrong: uiWrong } });
    }
    await evidence(testInfo, 'evidence', { tc: 'TC-2-06', user: 'U-2', date: '2026-11-16', site: 'SITE-A', cases: ev });
  });
});
