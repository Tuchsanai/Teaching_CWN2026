// 🧪 ประเมิน RAG E01–E03 + ⚡ Load test L01–L02 (BUILDMART ข้อ 7) — dashboard /admin/eval และ /admin/load
// fixture รู้ค่าแน่นอน: fixtures/eval-run-a.json (rerank on) · eval-run-b.json (rerank off) · load-run-a.json (chat 1→32 · ขั้น 32 ไม่ผ่าน)
// POST ด้วย header x-eval-token (EVAL_TOKEN ดีฟอลต์ bm-eval) · ไม่มี token/cookie → 401
// หมายเหตุ: ทุกรอบที่รันจะเพิ่ม run ป้าย "e2e-…" ลงตาราง eval_runs / load_runs (ไม่มี API ลบ)
import { spawn } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import type { Page } from '@playwright/test';
import { bmCase, expect, intro, say, show, hold, highlight, adminLogin, attachJson, attachText, BM_URL, E2E_DIR, ROOT } from './_bm';

const TOKEN = process.env.EVAL_TOKEN || 'bm-eval';
const fx = (f: string) => JSON.parse(readFileSync(path.join(E2E_DIR, 'fixtures', f), 'utf8'));
const EVAL_A = fx('eval-run-a.json');
const EVAL_B = fx('eval-run-b.json');
const LOAD_A = fx('load-run-a.json');

async function post(kind: 'eval' | 'load', body: unknown, token: string | null = TOKEN) {
  const r = await fetch(`${BM_URL}/api/admin/${kind}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(token ? { 'x-eval-token': token } : {}) },
    body: JSON.stringify(body),
  });
  return { status: r.status, json: (await r.json().catch(() => ({}))) as any };
}

/** ไม่ส่ง token / cookie → 401 ทั้ง POST และ GET */
async function expect401(kind: 'eval' | 'load', body: unknown) {
  const p = await post(kind, body, null);
  const g = await fetch(`${BM_URL}/api/admin/${kind}`).then((r) => r.status);
  const bad = await post(kind, body, 'wrong-token');
  expect(p.status, `POST /api/admin/${kind} ไม่มี token`).toBe(401);
  expect(bad.status, `POST /api/admin/${kind} token ผิด`).toBe(401);
  expect(g, `GET /api/admin/${kind} ไม่มี cookie`).toBe(401);
  return { postNoToken: p.status, postBadToken: bad.status, getNoCookie: g };
}

/** แผ่นป้ายบนจอ: แสดงคำขอ HTTP ที่ยิง (ให้คนดูวิดีโอเห็นว่าเกิดอะไร) */
async function board(page: Page, html: string, ms = 3500) {
  await page.evaluate((h) => {
    const d = document.createElement('div');
    d.id = '__bm_board';
    d.style.cssText =
      'position:fixed;left:50%;top:90px;transform:translateX(-50%);z-index:2147483645;background:#fff;color:#222;border-radius:14px;' +
      'box-shadow:0 20px 60px rgba(0,0,0,.35);border-top:8px solid #F26B1D;padding:16px 22px;max-width:900px;' +
      'font:15px/1.5 Consolas,"Sarabun",monospace;white-space:pre-wrap';
    d.innerHTML = h;
    document.documentElement.appendChild(d);
  }, html);
  await hold(page, ms);
  await page.evaluate(() => document.getElementById('__bm_board')?.remove());
}

const gaugeText = (m: string, v: number) => (m === 'stt_cer' ? `${(v * 100).toFixed(1)}%` : `${Math.round(v * 100)}%`);
const cmpText = (m: string, v: number) => (m === 'stt_cer' ? `${(v * 100).toFixed(1)}%` : `${(v * 100).toFixed(0)}%`);
const metricsOf = (s: any) => Object.entries(s).filter(([k, v]) => k !== 'n' && typeof v === 'number') as [string, number][];
const SET_ORDER: Record<string, string[]> = {
  rag: ['hit_at_4', 'mrr', 'citation_acc', 'faithfulness', 'correctness'],
  qa: ['exact_value', 'sql_correct', 'correctness'],
  conv: ['context_retention', 'correctness', 'stt_cer'],
};

/** เลือก run ใน <select> แล้วรอให้หน้าโหลด run นั้น */
async function pickRun(page: Page, testid: string, id: number) {
  const sel = page.getByTestId(testid);
  await highlight(sel, 2000);
  await sel.selectOption(String(id));
  await expect(sel).toHaveValue(String(id), { timeout: 15_000 });
  await page.waitForLoadState('networkidle').catch(() => {});
  await hold(page, 1200);
}

// run id ที่ E01/E02 สร้าง (E02/E03 ใช้ต่อ · รันเดี่ยวก็สร้างเอง)
let evalA = 0;
let evalB = 0;
async function ensureEvalA() {
  if (!evalA) evalA = (await post('eval', EVAL_A)).json.id;
  return evalA;
}

bmCase('E01', async ({ page, item }, info) => {
  await page.goto('/admin');
  await intro(page, item);
  const deny = await expect401('eval', EVAL_A);
  const r = await post('eval', EVAL_A);
  expect(r.status).toBe(201);
  expect(r.json.id, 'ได้ {id}').toBeGreaterThan(0);
  evalA = r.json.id;
  await attachJson(info, 'checked', { ...deny, postWithToken: r.status, id: evalA, label: EVAL_A.label });
  await board(
    page,
    `<b>POST /api/admin/eval</b>  (ไม่มี token)        → <b style="color:#c62828">${deny.postNoToken}</b>\n` +
      `<b>GET  /api/admin/eval</b>  (ไม่มี cookie)       → <b style="color:#c62828">${deny.getNoCookie}</b>\n` +
      `<b>POST /api/admin/eval</b>  x-eval-token ✓ run A → <b style="color:#1a7f37">${r.status} {id: ${evalA}}</b>\n\n` +
      `label: ${EVAL_A.label} · ${EVAL_A.items.length} ข้อ (rag ${EVAL_A.summary.rag.n} · qa ${EVAL_A.summary.qa.n} · conv ${EVAL_A.summary.conv.n})`,
    4500,
  );
  await adminLogin(page);
  await page.goto('/admin/eval');
  await say(page, `/admin/eval แสดง run #${evalA} — ตรวจการ์ดคะแนนทุกชุด × metric ตรงไฟล์`);
  await expect(page.getByTestId('eval-run-select')).toHaveValue(String(evalA), { timeout: 20_000 });
  const shown: Record<string, string> = {};
  for (const set of ['rag', 'qa', 'conv']) {
    for (const [m, v] of metricsOf(EVAL_A.summary[set])) {
      const card = page.locator(`[data-testid="eval-metric"][data-set="${set}"][data-metric="${m}"]`);
      await expect(card, `การ์ด ${set}.${m}`).toHaveCount(1);
      await expect(card).toHaveAttribute('data-value', String(v));
      await expect(card).toContainText(gaugeText(m, v));
      shown[`${set}.${m}`] = gaugeText(m, v);
    }
    await show(page, page.locator(`[data-testid="eval-metric"][data-set="${set}"]`), 1800);
  }
  const docs = page.getByTestId('eval-by-doc');
  await expect(docs, 'กราฟต่อเอกสาร 6 ไฟล์').toHaveCount(6);
  await say(page, 'กราฟแยกตามเอกสาร 6 ไฟล์ PDF');
  await show(page, docs);
  await attachJson(info, 'metrics-shown', shown);
});

bmCase('E02', async ({ page, item }, info) => {
  await page.goto('/admin');
  await intro(page, item);
  const a = await ensureEvalA();
  const r = await post('eval', EVAL_B);
  expect(r.status).toBe(201);
  evalB = r.json.id;
  await board(page, `<b>POST /api/admin/eval</b>  run B (rerank off) → <b style="color:#1a7f37">${r.status} {id: ${evalB}}</b>`, 3000);
  await adminLogin(page);
  await page.goto('/admin/eval');
  const sel = page.getByTestId('eval-run-select');
  await expect(sel).toHaveValue(String(evalB), { timeout: 20_000 });
  for (const id of [a, evalB]) await expect(sel.locator(`option[value="${id}"]`)).toHaveCount(1);
  await say(page, `เลือก run A (#${a} rerank on) เทียบกับ run B (#${evalB} rerank off)`);
  await pickRun(page, 'eval-run-select', a);

  // ① การ์ดคะแนน: ▲▼ = A − B (เทียบ run ที่ rerank ต่างกัน)
  const deltas: Record<string, string> = {};
  for (const set of ['rag', 'qa', 'conv']) {
    for (const [m, va] of metricsOf(EVAL_A.summary[set])) {
      const vb = EVAL_B.summary[set][m];
      const d = va - vb;
      const card = page.locator(`[data-testid="eval-metric"][data-set="${set}"][data-metric="${m}"]`);
      if (Math.abs(d) >= 0.0005) {
        const txt = `${d > 0 ? '▲' : '▼'} ${Math.abs(d * 100).toFixed(1)} จุด`;
        await expect(card.locator('.ev-delta'), `ผลต่าง ${set}.${m} (A − B)`).toHaveText(txt);
        deltas[`${set}.${m}`] = txt;
      }
    }
  }
  await show(page, page.locator('.ev-delta'), 2500);
  // ② ตารางเทียบ: ทุกแถว metric มีค่าของ A (แท่งแรก) และ B (แท่งที่สอง)
  const cmp = page.getByTestId('eval-compare');
  await expect(cmp).toContainText(EVAL_A.label);
  await expect(cmp).toContainText(EVAL_B.label);
  const rows = cmp.locator('.ev-cmp-row');
  const expected = Object.entries(SET_ORDER).flatMap(([set, ms]) => ms.filter((m) => EVAL_A.summary[set][m] != null).map((m) => ({ set, m })));
  await expect(rows).toHaveCount(expected.length);
  const table: string[] = [];
  for (const [i, { set, m }] of expected.entries()) {
    const vals = rows.nth(i).locator('.ev-cmp-bar > span:last-child');
    await expect(vals.nth(0), `${set}.${m} ค่า run A`).toHaveText(cmpText(m, EVAL_A.summary[set][m]));
    await expect(vals.nth(1), `${set}.${m} ค่า run B`).toHaveText(cmpText(m, EVAL_B.summary[set][m]));
    table.push(`${set}.${m}: A ${cmpText(m, EVAL_A.summary[set][m])} · B ${cmpText(m, EVAL_B.summary[set][m])} · ${deltas[`${set}.${m}`] || '='}`);
  }
  await say(page, 'ตารางเทียบ 2 run: ค่าทั้งสอง run + ผลต่าง (A − B)');
  await show(page, cmp, 4000);
  await attachText(info, 'checked', table.join('\n'));
});

bmCase('E03', async ({ page, item }, info) => {
  await page.goto('/admin');
  await intro(page, item);
  const a = await ensureEvalA();
  await adminLogin(page);
  await page.goto('/admin/eval');
  await expect(page.getByTestId('eval-run-select')).toBeVisible({ timeout: 20_000 });
  await pickRun(page, 'eval-run-select', a);
  const fails = EVAL_A.items.filter((i: any) => !i.pass);
  const items = page.getByTestId('eval-item');
  await expect(items).toHaveCount(EVAL_A.items.length);
  await say(page, `ติ๊ก “เฉพาะข้อที่ตก” — ในไฟล์มี ${fails.length} ข้อ`);
  const cb = page.getByTestId('eval-filter-fail');
  await highlight(cb.locator('xpath=..'), 2000);
  await cb.check();
  await expect(items).toHaveCount(fails.length);
  await expect(page.locator('[data-testid="eval-item"][data-pass="true"]')).toHaveCount(0);
  const ids = await items.evaluateAll((els) => els.map((e) => e.getAttribute('data-id')));
  expect(ids.sort()).toEqual(fails.map((f: any) => f.id).sort());
  await show(page, items, 2500);
  const first = items.first();
  const it = fails.find((f: any) => f.id === ids[0]) || fails[0];
  await say(page, `กดขยายข้อ ${await first.getAttribute('data-id')} ดูคำถาม · คำตอบที่คาด · คำตอบจริง · เหตุผล`);
  await first.click();
  const detail = page.locator('.ev-detail');
  await expect(detail).toBeVisible();
  const firstId = await first.getAttribute('data-id');
  const f = EVAL_A.items.find((x: any) => x.id === firstId);
  await expect(first).toContainText((f.question || f.turns[0].q).slice(0, 12));
  await expect(detail).toContainText(String(f.expected.answer).slice(0, 10));
  if (f.answer) await expect(detail).toContainText(f.answer.slice(0, 10));
  else await expect(detail).toContainText(f.turns[0].q.slice(0, 10));
  await expect(detail).toContainText(f.reason);
  await show(page, detail, 4000);
  await attachJson(info, 'checked', { run: a, failsInFile: fails.length, shown: ids, expanded: firstId, reason: f.reason, _it: it.id });
});

bmCase('L01', async ({ page, item }, info) => {
  await page.goto('/admin');
  await intro(page, item);
  const deny = await expect401('load', LOAD_A);
  const r = await post('load', LOAD_A);
  expect(r.status).toBe(201);
  const id = r.json.id;
  await board(
    page,
    `<b>POST /api/admin/load</b> (ไม่มี token) → <b style="color:#c62828">${deny.postNoToken}</b>\n` +
      `<b>GET  /api/admin/load</b> (ไม่มี cookie) → <b style="color:#c62828">${deny.getNoCookie}</b>\n` +
      `<b>POST /api/admin/load</b> x-eval-token ✓ → <b style="color:#1a7f37">${r.status} {id: ${id}}</b>\n\n` +
      `${LOAD_A.label} · ${LOAD_A.stages.length} ขั้น · max_users_ok = ${LOAD_A.summary.max_users_ok}`,
    4500,
  );
  await adminLogin(page);
  await page.goto('/admin/load');
  await expect(page.getByTestId('load-run-select')).toBeVisible({ timeout: 20_000 });
  await pickRun(page, 'load-run-select', id);
  const chart = page.getByTestId('load-chart');
  await expect(chart).toBeVisible();
  const xs = await chart.locator('circle').evaluateAll((cs) => new Set(cs.map((c) => c.getAttribute('cx'))).size);
  expect(xs, 'load-chart มีจุดครบ 6 ขั้น').toBe(LOAD_A.stages.length);
  await expect(page.getByTestId('load-stage')).toHaveCount(LOAD_A.stages.length);
  await say(page, `กราฟ latency เทียบผู้ใช้ ${LOAD_A.stages.length} ขั้น (1 → 32 คน)`);
  await show(page, chart, 3000);
  const maxCard = page.locator('[data-testid="load-max-users"][data-mode="chat"]');
  await expect(maxCard).toHaveAttribute('data-value', String(LOAD_A.summary.max_users_ok));
  await expect(maxCard).toContainText(String(LOAD_A.summary.max_users_ok));
  await say(page, `รับผู้ใช้พร้อมกันได้สูงสุด ${LOAD_A.summary.max_users_ok} คน (ตรงไฟล์)`);
  await show(page, maxCard, 2500);
  for (const s of LOAD_A.stages) {
    const row = page.locator(`[data-testid="load-stage"][data-users="${s.users}"]`);
    await expect(row).toHaveAttribute('data-ok', s.ok ? 'true' : 'false');
    if (!s.ok) {
      await expect(row.locator('.ev-pass.no')).toBeVisible();
      const color = await row.locator('.ev-pass.no').evaluate((e) => getComputedStyle(e).color);
      const [rr, gg] = (color.match(/\d+/g) || []).map(Number);
      expect(rr, `ขั้น ${s.users} คน ไม่ผ่าน → สีแดง (${color})`).toBeGreaterThan(gg);
      await say(page, `ขั้น ${s.users} คน เกินเกณฑ์ → สีแดง`);
      await show(page, row, 3000);
    }
  }
  await attachJson(info, 'checked', { ...deny, id, points: xs, max_users_ok: LOAD_A.summary.max_users_ok });
});

bmCase(
  'L02',
  async ({ page, item }, info) => {
    await page.goto('/admin');
    await intro(page, item);
    await adminLogin(page);
    await page.goto('/admin/load');
    const label = 'e2e-mini';
    const args = ['loadtest/run_load.mjs', '--mode', 'chat', '--users', '1,2,4', '--stage-sec', '15', '--label', label, '--url', BM_URL, '--drain-sec', '30'];
    await say(page, `รัน: node ${args.join(' ')}`);
    const t0 = Date.now();
    let out = '';
    const code: number = await new Promise((resolve) => {
      const p = spawn(process.execPath, args, { cwd: ROOT, env: { ...process.env, EVAL_TOKEN: TOKEN } });
      let last = 0;
      const onData = (d: Buffer) => {
        out += d.toString();
        const line = out.trim().split('\n').pop() || '';
        if (Date.now() - last > 1500) {
          last = Date.now();
          say(page, `⚡ load test (${Math.round((Date.now() - t0) / 1000)} วิ): ${line.slice(0, 110)}`);
        }
      };
      p.stdout.on('data', onData);
      p.stderr.on('data', onData);
      p.on('close', (c) => resolve(c ?? 1));
    });
    await attachText(info, 'run_load-output', out.slice(-4000));
    expect(code, 'run_load.mjs exit 0').toBe(0);
    const id = Number(out.match(/POST \S*\/api\/admin\/load → id (\d+)/)?.[1]);
    expect(id, 'POST /api/admin/load สำเร็จ (ได้ id)').toBeGreaterThan(0);
    const resFile = path.join(ROOT, 'loadtest', 'results', `${label}.json`);
    const res = existsSync(resFile) ? JSON.parse(readFileSync(resFile, 'utf8')) : null;
    const stages = res?.stages || [];
    expect(stages.length).toBe(3);
    for (const s of stages) expect(s.errors, `ขั้น ${s.users} คน errors`).toBe(0);

    await page.reload();
    const sel = page.getByTestId('load-run-select');
    await expect(sel.locator(`option[value="${id}"]`)).toContainText(label);
    await pickRun(page, 'load-run-select', id);
    await expect(page.getByTestId('load-stage')).toHaveCount(3);
    const xs = await page.getByTestId('load-chart').locator('circle').evaluateAll((cs) => new Set(cs.map((c) => c.getAttribute('cx'))).size);
    expect(xs, 'load-chart 3 ขั้น').toBe(3);
    await say(page, `run ${label}: กราฟ 3 ขั้น (1/2/4 คน) · errors 0 ทุกขั้น`);
    await show(page, page.getByTestId('load-chart'), 3000);
    const maxCard = page.locator('[data-testid="load-max-users"][data-mode="chat"]');
    const v = Number(await maxCard.getAttribute('data-value'));
    expect(v, 'load-max-users ≥ 1').toBeGreaterThanOrEqual(1);
    await say(page, `max_users_ok = ${v} คน (mock)`);
    await show(page, maxCard, 3000);
    await attachJson(info, 'checked', { id, label, exit: code, max_users_ok: res?.summary?.max_users_ok, shown: v, stages: stages.map((s: any) => ({ users: s.users, n: s.n, errors: s.errors, p95: s.p95, ttft_p95: s.ttft_p95 })) });
  },
  { timeout: 8 * 60_000 },
);
