#!/usr/bin/env node
// B14 · ทดสอบเบื้องต้นแบบ end-to-end ผ่าน HTTP กับเว็บที่รันด้วย docker compose (AI_MODE=mock)
// ใช้: BASE=http://localhost:3000 TOKEN=<TEST_RESET_TOKEN> node tests/e2e-api.mjs
const BASE = process.env.BASE || 'http://localhost:3000';
const TOKEN = process.env.TOKEN || 'b14-test-token';
const PASSWORD = 'receiptdesk-test';
let pass = 0, fail = 0;
const results = [];
function check(id, ok, detail) {
  (ok ? pass++ : fail++);
  results.push({ id, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'} ${id} · ${detail}`);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function reset(options) {
  const r = await fetch(`${BASE}/api/test/reset`, {
    method: 'POST',
    headers: { 'x-test-token': TOKEN, ...(options ? { 'content-type': 'application/json' } : {}) },
    body: options ? JSON.stringify(options) : undefined,
  });
  if (!r.ok) throw new Error(`reset ${r.status} ${await r.text()}`);
  return r.json();
}
async function login(email) {
  const r = await fetch(`${BASE}/api/auth/login`, {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email, password: PASSWORD }),
  });
  if (!r.ok) throw new Error(`login ${email} ${r.status}`);
  const cookie = r.headers.getSetCookie().map((c) => c.split(';')[0]).join('; ');
  return (path, init = {}) => fetch(`${BASE}${path}`, { ...init, headers: { ...(init.headers || {}), cookie } });
}
async function j(res) { const t = await res.text(); try { return JSON.parse(t); } catch { return t; } }

// รูป PNG 1×1 ที่ถูกต้อง (magic bytes ผ่าน BR-03)
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64');
function form(clientId, names, urgent = false) {
  const fd = new FormData();
  fd.set('clientId', clientId);
  if (urgent) fd.set('urgent', 'true');
  for (const n of names) fd.append('files', new Blob([PNG], { type: 'image/png' }), n);
  return fd;
}
const many = (n, prefix = 'ok-100') => Array.from({ length: n }, (_, i) => `${prefix}__${String(i + 1).padStart(3, '0')}.png`);

async function monthly(api, clientId, month) {
  const csv = await api(`/api/reports/monthly?clientId=${clientId}&month=${month}`);
  const text = await csv.text();
  const rows = text.replace(/^﻿/, '').trim().split(/\r?\n/);
  const header = rows[0];
  const totalIdx = header.split(',').indexOf('total');
  // ผลรวมจากเนื้อไฟล์ CSV เอง (ไม่ใช่แค่ header) เทียบเป็นสตางค์
  let satang = 0;
  for (const line of rows.slice(1)) {
    const cells = line.match(/("([^"]|"")*"|[^,]*)(,|$)/g).map((c) => c.replace(/,$/, '').replace(/^"|"$/g, ''));
    satang += Math.round(Number(cells[totalIdx]) * 100);
  }
  return {
    status: csv.status, header, dataRows: rows.length - 1, csvTotal: (satang / 100).toFixed(2),
    hTotal: csv.headers.get('x-report-total'), hCount: csv.headers.get('x-report-count'),
    contentType: csv.headers.get('content-type'),
  };
}

async function main() {
  // ── 0. health + logo ──
  const h = await fetch(`${BASE}/api/health`);
  const hb = await h.json();
  check('H-01', h.status === 200 && hb.status === 'ok' && hb.db === 'ok', `/api/health ${h.status} ${JSON.stringify(hb)}`);
  const logo = await fetch(`${BASE}/logo.png`);
  const lb = Buffer.from(await logo.arrayBuffer());
  check('H-02', logo.status === 200 && lb.subarray(0, 4).equals(PNG.subarray(0, 4)), `/logo.png ${logo.status} ${logo.headers.get('content-type')} ${lb.length} bytes`);
  const loginPage = await (await fetch(`${BASE}/login`)).text();
  check('H-03', loginPage.includes('data-testid="login-logo"') && loginPage.includes('rel="icon" href="/logo.png'), 'หน้า /login แสดง /logo.png และใช้เป็น favicon');

  // ── 1. ข้อมูลตั้งต้น + ผลรวม §5 ──
  await reset();
  const pim = await login('pim@receiptdesk.test');
  const { clients } = await j(await pim('/api/clients'));
  const C = Object.fromEntries(clients.map((c) => [c.code, c.id]));
  const expect5 = [
    ['E-01', 'CL-01', '2026-10', '150.00', 1],
    ['E-02', 'CL-01', '2026-11', '1340.00', 4],
    ['E-03', 'CL-01', '2026-12', '75.25', 1],
    ['E-04', 'CL-02', '2026-11', '999.00', 1],
    ['E-06', 'CL-03', '2026-11', '0.00', 0],
  ];
  const checkSection5 = async (tag) => {
    for (const [id, cl, month, total, count] of expect5) {
      if (tag && id === 'E-06') continue; // CL-03 ถูกใช้ทดสอบในขั้น 2 แล้ว (ดู F-08)
      const m = await monthly(pim, C[cl], month);
      check(`${id}${tag}`, m.status === 200 && m.csvTotal === total && m.dataRows === count && m.hTotal === total && Number(m.hCount) === count,
        `CSV ${cl} ${month}: ยอดจากไฟล์ ${m.csvTotal} · ${m.dataRows} แถว · X-Report-Total ${m.hTotal} · คาด ${total}/${count}`);
    }
    const cat = await j(await pim(`/api/reports/categories?clientId=${C['CL-01']}&month=2026-11`));
    const by = Object.fromEntries(cat.categories.map((c) => [c.name, c.total]));
    const okCat = by['วัตถุดิบ'] === '1200.50' && by['ค่าแก๊ส'] === '40.00' && by['ค่าน้ำแข็ง'] === '99.50' && by['อื่น ๆ'] === '0.00' && cat.total === '1340.00';
    check(`E-05${tag}`, okCat, `หมวด CL-01 2026-11 ${JSON.stringify(by)} รวม ${cat.total}`);
  };
  await checkSection5('');
  const e6 = await monthly(pim, C['CL-03'], '2026-11');
  check('E-06-csv', e6.dataRows === 0 && e6.header.startsWith('receipt_date,merchant'), `CL-03 ได้ไฟล์มีแต่หัวตาราง: "${e6.header}" (${e6.contentType})`);

  // ── 2. อัปโหลดชุด → อ่าน (mock) → ตรวจแก้ → ยืนยัน → CSV ──
  // ใช้ CL-03 เพื่อไม่ให้กระทบ E-01..E-05 แล้วคำนวณยอดที่คาดของ CL-03 จากค่าที่ยืนยันเอง
  const files = ['ok-100__001.png', 'conf-089__002.png', 'diff-101__003.png', 'fail3__004.png', 'total-000__005.png'];
  const up = await pim('/api/batches', { method: 'POST', body: form(C['CL-03'], files) });
  const ub = await j(up);
  check('F-01', up.status === 201 && ub.accepted === files.length, `อัปโหลดชุด 5 ไฟล์ของ CL-03 → ${up.status} accepted=${ub.accepted}`);
  const batchId = ub.batchId;

  let batch;
  for (let i = 0; i < 60; i++) {
    batch = await j(await pim(`/api/batches/${batchId}`));
    const c = batch.batch?.counts ?? {};
    if ((c.queued ?? 0) + (c.processing ?? 0) === 0) break;
    await sleep(2000);
  }
  const counts = batch.batch.counts;
  check('F-02', counts.queued === 0 && counts.processing === 0 && counts.review === 4 && counts.unreadable === 1,
    `ตัวอ่านจำลองอ่านจบ: ${JSON.stringify(counts)} (คาด review 4 · unreadable 1 จาก fail3)`);

  const { receipts } = await j(await pim(`/api/receipts?batchId=${batchId}&limit=50`));
  const byName = Object.fromEntries(receipts.map((r) => [r.fileName.split('__')[0], r]));
  const flagsOf = (k) => byName[k]?.flags ?? {};
  check('F-03', !flagsOf('ok-100').flagged && flagsOf('conf-089').lowConfidence && flagsOf('conf-089').flagged
    && flagsOf('diff-101').mismatch && byName['fail3'].status === 'unreadable',
    `ธง: ok-100=${flagsOf('ok-100').flagged} conf-089=${JSON.stringify(flagsOf('conf-089').reasons)} diff-101=${JSON.stringify(flagsOf('diff-101').reasons)} fail3=${byName['fail3'].status}`);

  const cats = await j(await pim(`/api/reports/categories?clientId=${C['CL-03']}&month=2026-11`));
  const catId = Object.fromEntries(cats.categories.map((c) => [c.name, c.id]));

  // F-04: ยืนยันใบติดธงโดยยังไม่เปิดดู → 409 review_not_opened (FR-12)
  const early = await pim(`/api/receipts/${byName['conf-089'].id}/confirm`, {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ totalChecked: true, categoryId: catId['วัตถุดิบ'] }),
  });
  const eb = await j(early);
  check('F-04', early.status === 409 && eb.error === 'review_not_opened', `ยืนยันใบติดธงก่อนเปิด → ${early.status} ${eb.error}`);

  const plan = [
    // [key, PATCH body, category, ยอดที่ยืนยัน]
    ['ok-100', null, 'วัตถุดิบ', '100.00'],
    ['conf-089', { total: '100.50' }, 'ค่าแก๊ส', '100.50'],
    ['diff-101', { items: [{ lineNo: 3, price: '25.00' }] }, 'วัตถุดิบ', '100.00'],
    ['fail3', { merchant: 'ร้านกรอกเอง', receiptDate: '2026-11-20', total: '35.75', items: [{ name: 'น้ำแข็ง', price: '35.75' }] }, 'ค่าน้ำแข็ง', '35.75'],
  ];
  let expectSatang = 0;
  for (const [key, patch, cat, total] of plan) {
    const id = byName[key].id;
    const open = (await j(await pim(`/api/receipts/${id}`))).receipt; // W12 บันทึก review_opened_at
    let pst = '-';
    if (patch) {
      const p = await pim(`/api/receipts/${id}`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify(patch) });
      pst = p.status;
    }
    const c = await pim(`/api/receipts/${id}/confirm`, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ totalChecked: true, categoryId: catId[cat] }),
    });
    const cb = await j(c);
    const after = (await j(await pim(`/api/receipts/${id}`))).receipt;
    const ok = c.status === 200 && after.status === 'confirmed' && after.total === total && after.confirmedBy;
    if (ok) expectSatang += Math.round(Number(total) * 100);
    check(`F-05:${key}`, ok, `เปิด(${open.status}) → PATCH ${pst} → confirm ${c.status}${cb.error ? ' ' + cb.error : ''} → ${after.status} ยอด ${after.total} โดย ${after.confirmedBy}${key === 'fail3' ? ` · กรอกเอง=${after.enteredManually}` : ''}`);
  }
  // ใบยอด 0.00 ยืนยันไม่ได้ (BR-06)
  {
    const id = byName['total-000'].id;
    await pim(`/api/receipts/${id}`);
    const c = await pim(`/api/receipts/${id}/confirm`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ totalChecked: true, categoryId: catId['อื่น ๆ'] }) });
    const cb = await j(c);
    check('F-06', c.status === 422 && cb.error === 'total_invalid', `ยืนยันใบยอด 0.00 → ${c.status} ${cb.error}`);
  }
  const hist = await j(await pim(`/api/receipts/${byName['conf-089'].id}/history`));
  check('F-07', Array.isArray(hist.edits) && hist.edits.some((e) => e.field === 'total' && e.newValue === '100.50' && e.editedBy),
    `ประวัติการแก้ conf-089: ${JSON.stringify(hist.edits?.map((e) => [e.field, e.oldValue, e.newValue]))}`);

  const expectCl3 = (expectSatang / 100).toFixed(2);
  const m3 = await monthly(pim, C['CL-03'], '2026-11');
  check('F-08', m3.csvTotal === expectCl3 && m3.dataRows === 4 && m3.hTotal === expectCl3,
    `CSV CL-03 2026-11 หลังยืนยัน: ยอดจากไฟล์ ${m3.csvTotal} · ${m3.dataRows} แถว (คาด ${expectCl3} · 4 แถว)`);
  await checkSection5('·หลังยืนยัน');
  const rec = await j(await pim(`/api/reports/reconcile?batchId=${batchId}`));
  check('F-09', rec.diff === 0 && rec.accepted === 5, `กระทบยอดชุด: ${JSON.stringify(rec)}`);

  // ── 3. คิวเต็ม: 429 + N นาที (BR-11/12) ──
  const fullCases = [
    ['TD-BR11-b', { pendingNormal: 300, workersAlive: 2 }, 100, 201, null],
    ['TD-BR11-c', { pendingNormal: 301, workersAlive: 2 }, 100, 429, 1],
    ['TD-BR12-d', { pendingNormal: 309, workersAlive: 2 }, 100, 429, 2],
    ['TD-BR12-e', { pendingNormal: 380, workersAlive: 2 }, 100, 429, 10],
    ['TD-BR12-f', { pendingNormal: 400, workersAlive: 2 }, 100, 429, 13],
    ['TD-BR12-g', { pendingNormal: 309, workersAlive: 1 }, 100, 429, 3],
    ['TD-BR12-h', { pendingNormal: 380, workersAlive: 0 }, 100, 429, 20],
  ];
  for (const [id, opts, n, status, minutes] of fullCases) {
    await reset(opts);
    const api = await login('pim@receiptdesk.test');
    // reset สร้าง UUID ใหม่ทุกครั้ง จึงต้องอ่านรหัสลูกค้าใหม่
    const cl1 = (await j(await api('/api/clients'))).clients.find((c) => c.code === 'CL-01').id;
    const r = await api('/api/batches', { method: 'POST', body: form(cl1, many(n)) });
    const b = await j(r);
    const q = await j(await api('/api/queue'));
    if (status === 429) {
      const ok = r.status === 429 && b.error === 'queue_full' && b.retryAfterMinutes === minutes
        && Number(r.headers.get('retry-after')) === minutes * 60 && String(b.message).includes(`${minutes} นาที`)
        && q.normal.pending === opts.pendingNormal;
      check(id, ok, `ค้าง ${opts.pendingNormal} + ${n} · Worker ${opts.workersAlive} → ${r.status} ${b.error} N=${b.retryAfterMinutes} Retry-After=${r.headers.get('retry-after')}s · "${b.message}" · ค้างหลังปฏิเสธ ${q.normal.pending}`);
    } else {
      check(id, r.status === 201 && b.accepted === n, `ค้าง ${opts.pendingNormal} + ${n} → ${r.status} รับ ${b.accepted} · ค้าง ${q.normal.pending}`);
    }
  }
  // คืนสภาพข้อมูลตั้งต้น
  await reset();

  console.log(`\nสรุป: ผ่าน ${pass} · ไม่ผ่าน ${fail}`);
  process.exitCode = fail ? 1 : 0;
}
main().catch((e) => { console.error(e); process.exitCode = 2; });
