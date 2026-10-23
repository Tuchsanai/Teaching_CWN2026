// 📨 RabbitMQ Q01–Q03
import { execSync } from 'node:child_process';
import type { Page } from '@playwright/test';
import {
  bmCase, expect, intro, ask, expectAnswer, say, show, hold, highlight, typeHuman, attachJson, attachText,
  openChat, readAnswer, adminLogin, apiJson, getStock, BM_URL, ROOT, BURST_TIMEOUT,
} from './_bm';
import { addToCartUI, fillCheckout, placeOrder } from './_shop';

const MQ_URL = (process.env.BM_MQ_URL || 'http://localhost:15672').replace(/\/$/, '');
// guest/guest = ค่า dev ของ RabbitMQ ในเครื่อง (ผูก 127.0.0.1 เท่านั้น)
const MQ_AUTH = 'Basic ' + Buffer.from(`${process.env.BM_MQ_USER || 'guest'}:${process.env.BM_MQ_PASS || 'guest'}`).toString('base64');

async function queueInfo(name = 'chat.request') {
  try {
    const r = await fetch(`${MQ_URL}/api/queues/%2F/${encodeURIComponent(name)}`, { headers: { Authorization: MQ_AUTH } });
    if (!r.ok) return null;
    const j: any = await r.json();
    return { messages: Number(j.messages ?? 0), ready: Number(j.messages_ready ?? 0), unacked: Number(j.messages_unacknowledged ?? 0), consumers: Number(j.consumers ?? 0) };
  } catch {
    return null;
  }
}

const compose = (args: string) =>
  execSync(`docker compose -p buildmart ${args}`, { cwd: ROOT, stdio: 'pipe', timeout: 120_000 }).toString();

const Q01_QUESTIONS = [
  'ร้านเปิดกี่โมงครับ',
  'ปูนซีเมนต์ถุงละเท่าไร',
  'มีโค้ดส่วนลดไหม',
  'สาขาบางนาเบอร์อะไร',
  'วันอาทิตย์เปิดไหม',
  'ส่งของน้ำหนัก 5 ตันใช้รถอะไร ค่าส่งเท่าไร',
  'ปูนซีเมนต์เก็บได้นานแค่ไหนครับ',
  'สีทาภายนอกรับประกันกี่ปี',
];

/** ตารางสรุปบนหน้าหลัก (อัปเดตสดระหว่างรอ 8 หน้าต่าง) */
async function renderBoard(page: Page, rows: { q: string; state: string; text: string; ms: number | null }[], mq: string) {
  await page.evaluate(
    ({ rows, mq }) => {
      let d = document.getElementById('__bm_board');
      if (!d) {
        d = document.createElement('div');
        d.id = '__bm_board';
        d.style.cssText =
          'position:fixed;inset:70px 40px 70px 40px;z-index:2147483645;background:#fff;border-radius:16px;' +
          'box-shadow:0 20px 60px rgba(0,0,0,.35);border-top:8px solid #F26B1D;padding:18px 24px;overflow:hidden;' +
          'font:15px/1.45 Sarabun,"Noto Sans Thai",Tahoma,sans-serif;color:#222';
        document.documentElement.appendChild(d);
      }
      const esc = (s: string) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c] as string);
      const color = (s: string) => (s === 'เสร็จ' ? '#1a7f37' : s === 'error' ? '#c62828' : s.startsWith('รอคิว') ? '#b26a00' : '#1565c0');
      d.innerHTML =
        `<div style="display:flex;justify-content:space-between;align-items:baseline"><b style="font-size:22px">💬 × 8 หน้าต่างถามพร้อมกัน</b>` +
        `<span style="font-family:Consolas,monospace;background:#fff4ec;border:1px solid #F26B1D;border-radius:8px;padding:2px 10px">${esc(mq)}</span></div>` +
        `<table style="width:100%;border-collapse:collapse;margin-top:10px">` +
        `<tr style="text-align:left;background:#f4f4f6"><th style="padding:6px">#</th><th>คำถาม</th><th>สถานะ</th><th>เวลา</th><th>คำตอบ (ย่อ)</th></tr>` +
        rows
          .map(
            (r, i) =>
              `<tr style="border-top:1px solid #eee"><td style="padding:6px">${i + 1}</td><td style="width:26%">${esc(r.q)}</td>` +
              `<td style="color:${color(r.state)};font-weight:700;white-space:nowrap">${esc(r.state)}</td>` +
              `<td style="white-space:nowrap">${r.ms == null ? '' : (r.ms / 1000).toFixed(1) + ' วิ'}</td>` +
              `<td style="color:#444">${esc(r.text.replace(/\s+/g, ' ').slice(0, 90))}</td></tr>`,
          )
          .join('') +
        `</table>`;
    },
    { rows, mq },
  );
}

bmCase(
  'Q01',
  async ({ page, item, browser }, info) => {
    await page.goto('/');
    await intro(page, item);
    await say(page, 'เปิด 8 หน้าต่าง (8 session) แล้วกดส่งคำถามพร้อมกัน');
    const rows = Q01_QUESTIONS.map((q) => ({ q, state: 'เตรียม…', text: '', ms: null as number | null }));
    await renderBoard(page, rows, 'chat.request: –');
    const ctxs = await Promise.all(Q01_QUESTIONS.map(() => browser.newContext({ baseURL: BM_URL, viewport: { width: 1000, height: 760 }, locale: 'th-TH' })));
    try {
      const pages = await Promise.all(
        ctxs.map(async (c, i) => {
          const p = await c.newPage();
          await p.goto('/');
          await openChat(p);
          await p.getByTestId('chat-input').fill(Q01_QUESTIONS[i]);
          return p;
        }),
      );
      rows.forEach((r) => (r.state = 'พร้อมส่ง'));
      await renderBoard(page, rows, 'chat.request: –');
      await hold(page, 1500);
      const t0 = Date.now();
      await Promise.all(pages.map((p) => p.getByTestId('chat-send').click()));
      let peak = { ready: 0, unacked: 0, consumers: 0 };
      const deadline = Date.now() + BURST_TIMEOUT; // ai: 8 แชท / GPU ทีละ 4 → ถึง 240 วิ
      for (;;) {
        const states = await Promise.all(
          pages.map(async (p, i) => {
            const bot = p.getByTestId('chat-msg-bot').first();
            if ((await bot.getAttribute('data-done').catch(() => null)) === 'true') {
              const isErr = ((await bot.getAttribute('class')) || '').includes('error');
              if (rows[i].ms == null) rows[i].ms = Date.now() - t0;
              return { state: isErr ? 'error' : 'เสร็จ', text: (await bot.innerText()).trim() };
            }
            const st = await p.getByTestId('chat-status').first().innerText().catch(() => '');
            const partial = await bot.innerText().catch(() => '');
            return { state: st.trim() || (partial ? 'กำลังพิมพ์…' : 'ส่งแล้ว'), text: partial };
          }),
        );
        states.forEach((s, i) => Object.assign(rows[i], s));
        const q = await queueInfo();
        if (q) peak = { ready: Math.max(peak.ready, q.ready), unacked: Math.max(peak.unacked, q.unacked), consumers: Math.max(peak.consumers, q.consumers) };
        await renderBoard(page, rows, q ? `chat.request · รอ ${q.ready} · กำลังทำ ${q.unacked} · consumer ${q.consumers}` : 'chat.request: –');
        if (rows.every((r) => r.state === 'เสร็จ' || r.state === 'error') || Date.now() > deadline) break;
        await page.waitForTimeout(400);
      }
      const answers = await Promise.all(pages.map(async (p) => readAnswer(p, p.getByTestId('chat-msg-bot').first())));
      await info.attach('answer', {
        body: answers.map((a, i) => `${i + 1}. ${Q01_QUESTIONS[i]} → ${a.text.replace(/\s+/g, ' ')}`).join('\n'),
        contentType: 'text/plain',
      });
      await attachJson(info, 'checked', { totalMs: Date.now() - t0, peakQueue: peak, states: rows.map((r) => r.state), ms: rows.map((r) => r.ms) });
      await say(page, `ได้คำตอบครบ ${rows.filter((r) => r.state === 'เสร็จ').length}/8 · ไม่มี error`);
      await show(page, page.locator('#__bm_board'), 5000);
      expect(rows.map((r) => r.state)).toEqual(Array(8).fill('เสร็จ'));
      for (const a of answers) expect(a.text.length).toBeGreaterThan(5);
    } finally {
      await Promise.all(ctxs.map((c) => c.close().catch(() => {})));
    }

    // หน้า RabbitMQ UI → คิว chat.request มี consumer
    await say(page, 'เปิด RabbitMQ Management UI (:15672) ดูคิว chat.request');
    await page.goto(`${MQ_URL}/`);
    const user = page.locator('input[name="username"]');
    if (await user.isVisible({ timeout: 10_000 }).catch(() => false)) {
      await typeHuman(user, 'guest');
      await typeHuman(page.locator('input[name="password"]'), 'guest');
      await page.locator('input[type="submit"], button[type="submit"]').first().click();
    }
    await page.goto(`${MQ_URL}/#/queues`);
    const link = page.locator('a', { hasText: /^chat\.request$/ }).first();
    await expect(link).toBeVisible({ timeout: 20_000 });
    await show(page, link.locator('xpath=ancestor::tr[1]'), 3000);
    await link.click();
    const consumersH = page.locator('h2', { hasText: /Consumers/ }).first();
    await expect(consumersH).toBeVisible({ timeout: 20_000 });
    await consumersH.click().catch(() => {}); // ส่วน Consumers อาจพับอยู่
    const q = await queueInfo();
    await say(page, `คิว chat.request (durable) มี consumer ${q?.consumers ?? '?'} ตัว (chat-worker)`);
    await page.waitForTimeout(800);
    await highlight(page.locator('#main h1, #main table.facts').first(), 5000);
    await highlight(consumersH.locator('xpath=..'), 5000);
    await hold(page, 4500);
    await info.attach('rabbitmq-queues', { body: await page.screenshot(), contentType: 'image/png' });
    await attachText(info, 'mq', JSON.stringify(q));
    expect(q?.consumers ?? 0).toBeGreaterThanOrEqual(1);
  },
  { timeout: 8 * 60_000 },
);

bmCase(
  'Q02',
  async ({ page, item }, info) => {
    await page.goto('/');
    await intro(page, item);
    await openChat(page);
    let started = false;
    try {
      await say(page, 'หยุด chat-worker (docker compose stop chat-worker)');
      compose('stop chat-worker');
      await hold(page, 1500);
      const q = 'ปูนซีเมนต์ถุงละเท่าไร';
      await say(page, `chat-worker หยุดอยู่ → ถาม “${q}”`);
      await typeHuman(page.getByTestId('chat-input'), q);
      await page.getByTestId('chat-send').click();
      const status = page.getByTestId('chat-status');
      await expect(status).toContainText('รอคิว', { timeout: 15_000 });
      await say(page, 'ข้อความค้างอยู่ในคิว chat.request (durable) — สถานะ “รอคิว…”');
      await highlight(status, 7000);
      await hold(page, 6000); // ค้าง ≥ 5 วิ
      // สถิติของ management API หน่วง ~5 วิ → poll จน consumer = 0 และมีข้อความค้างในคิว
      let mqWhileStopped = await queueInfo();
      await expect
        .poll(async () => ((mqWhileStopped = await queueInfo()), `${mqWhileStopped?.consumers}/${(mqWhileStopped?.messages ?? 0) > 0}`), { timeout: 15_000 })
        .toBe('0/true');
      await expect(status).toContainText('รอคิว');
      await expect(page.locator('[data-testid="chat-msg-bot"][data-done="true"]')).toHaveCount(0);
      await say(page, 'เปิด chat-worker กลับ (docker compose start chat-worker)');
      compose('start chat-worker');
      started = true;
      const bot = page.getByTestId('chat-msg-bot').last();
      await expect(bot).toHaveAttribute('data-done', 'true', { timeout: 180_000 });
      const ans = await readAnswer(page, bot);
      await info.attach('answer', { body: ans.text, contentType: 'text/plain' });
      await attachJson(info, 'checked', { queueWhileWorkerStopped: mqWhileStopped, queueAfter: await queueInfo() });
      await say(page, 'worker กลับมา → ดึงข้อความเดิมจากคิว → ได้คำตอบ ไม่หาย');
      await show(page, bot, 4500);
      expectAnswer(ans.text, [/(^|\D)145(\D|$)/]);
    } finally {
      if (!started) {
        try {
          compose('start chat-worker');
        } catch {}
      }
    }
  },
  { timeout: 6 * 60_000 },
);

/** หา (sku, สาขา, จำนวน) ที่สั่งแล้วสต็อกต่ำกว่าจุดสั่งซื้อซ้ำ โดยสั่งน้อยที่สุด */
async function pickLowStockOrder(page: Page) {
  const candidates = ['TOL-002', 'ELC-003', 'TOL-001', 'ELC-001', 'PNT-003', 'AGG-002', 'AGG-001', 'TOL-003'];
  let best: { sku: string; branch: string; qty: number; stock: number; reorder: number } | null = null;
  for (const sku of candidates) {
    const p = await apiJson(page.request, 'GET', `/api/products/${sku}`);
    const reorder = Number(p.reorder_point);
    for (const s of p.stock) {
      const qty = Math.max(1, s.qty - reorder + 1);
      if (s.qty >= 1 && qty <= s.qty && qty <= 30 && (!best || qty < best.qty)) best = { sku, branch: s.branch, qty, stock: s.qty, reorder };
    }
    if (best && best.qty <= 10) break;
  }
  if (!best) throw new Error('หา SKU ที่ทำให้สต็อกต่ำกว่าจุดสั่งซื้อซ้ำไม่ได้');
  return best;
}

bmCase(
  'Q03',
  async ({ page, item }, info) => {
    await page.goto('/');
    await intro(page, item);
    const pick = await pickLowStockOrder(page);
    await say(page, `${pick.sku} สาขา ${pick.branch} เหลือ ${pick.stock} (จุดสั่งซื้อซ้ำ ${pick.reorder}) → สั่ง ${pick.qty}`);
    await hold(page, 2500);
    await addToCartUI(page, pick.sku, pick.qty);
    await fillCheckout(page, pick.branch);
    const orderNo = await placeOrder(page);
    const after = await getStock(page.request, pick.sku);
    await adminLogin(page);
    await say(page, 'หลังร้าน: แจ้งเตือนจากคิว order.events (notify-worker)');
    const notes = page.getByTestId('admin-notifications');
    const orderNote = notes.locator('[data-testid="admin-notification"][data-kind="order"]', { hasText: orderNo });
    const lowNote = notes.locator('[data-testid="admin-notification"][data-kind="low_stock"]', { hasText: pick.sku });
    await expect(async () => {
      if (!(await orderNote.count()) || !(await lowNote.count())) {
        await page.reload();
        throw new Error('ยังไม่มีแจ้งเตือน');
      }
    }).toPass({ timeout: 60_000, intervals: [2000, 3000, 5000] });
    await attachJson(info, 'checked', {
      pick,
      orderNo,
      stockAfter: after[pick.branch],
      order: (await orderNote.first().innerText()).trim(),
      lowStock: (await lowNote.first().innerText()).trim(),
    });
    await show(page, orderNote.first(), 3000);
    await say(page, `สต็อกต่ำ: ${pick.sku} สาขา ${pick.branch} เหลือ ${after[pick.branch]} < ${pick.reorder}`);
    await show(page, lowNote.first(), 4000);
    expect(after[pick.branch]).toBeLessThan(pick.reorder);
  },
  { timeout: 6 * 60_000 },
);
