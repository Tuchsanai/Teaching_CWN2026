// e2e/tests/_bm.ts — fixture + helper กลางของเพลย์ลิสต์
// - bmCase(id, fn): สร้าง test ชื่อ "<id> <title>" จาก playlist.json + ป้ายมุมจอ + การ์ดเปิดเคส
// - typeHuman / hold / show (ไฮไลต์สีส้ม + ค้างภาพ) / say (คำบรรยายล่างจอ)
// - แชท: openChat / ask (รอคำตอบเสร็จ แล้ว attach คำตอบ + cites)
import { test as base, expect, type Locator, type Page, type TestInfo, type APIRequestContext } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

export { expect };

const here = path.dirname(fileURLToPath(import.meta.url));
export const E2E_DIR = path.resolve(here, '..');
export const ROOT = path.resolve(E2E_DIR, '..');

export type PlayItem = { id: string; group: string; title: string; what: string; expect: string };
export const PLAYLIST: PlayItem[] = JSON.parse(readFileSync(path.join(E2E_DIR, 'playlist.json'), 'utf8'));

export const MODE: 'mock' | 'ai' = process.env.BM_MODE === 'ai' ? 'ai' : 'mock';
export const TTS = process.env.BM_TTS === '1';
export const BM_URL = (process.env.BM_URL || 'http://localhost:3400').replace(/\/$/, '');
export const ADMIN_PASSWORD = process.env.BM_ADMIN_PASSWORD || 'admin1234';
/** ระยะค้างภาพหลังผลแต่ละขั้น (3–5 วิ) */
export const HOLD = Number(process.env.BM_HOLD_MS || 3500);
/** รอคำตอบแชท: mock เร็ว · ai ≤ 120 วิ ต่อคำตอบ (Qwen จริง) */
export const ANSWER_TIMEOUT = MODE === 'ai' ? 120_000 : 90_000;
/** Q01: 8 แชทพร้อมกันหลัง GPU ที่รับได้ทีละ 4 → ai ให้ถึง 240 วิ */
export const BURST_TIMEOUT = MODE === 'ai' ? 240_000 : 90_000;

type Fixtures = { item: PlayItem };

export const test = base.extend<Fixtures>({
  item: async ({}, use, info) => {
    const id = info.title.split(' ')[0];
    const it = PLAYLIST.find((p) => p.id === id);
    if (!it) throw new Error(`ไม่พบเคส ${id} ใน playlist.json`);
    await use(it);
  },
  // จด Date.now() ตอน page ถูกสร้าง ≈ เวลาเริ่มอัดวิดีโอ — ใช้คำนวณ offset เสียงของเคส T
  page: async ({ page, item }, use, info) => {
    const start = Date.now();
    (page as any).__bmVideoStart = start;
    info.annotations.push({ type: 'videoStart', description: String(start) });
    await installOverlay(page, item);
    await use(page);
  },
});

/** ป้ายมุมจอ + คำบรรยาย (sessionStorage ทำให้คงอยู่ข้ามการเปลี่ยนหน้า) */
export async function installOverlay(page: Page, item: PlayItem) {
  await page.addInitScript(
    ({ label, group }) => {
      const mount = () => {
        if (document.getElementById('__bm_badge')) return;
        const b = document.createElement('div');
        b.id = '__bm_badge';
        b.setAttribute('aria-hidden', 'true');
        b.style.cssText =
          'position:fixed;top:2px;left:8px;z-index:2147483646;pointer-events:none;white-space:nowrap;' +
          'background:rgba(28,28,32,.92);color:#fff;border-left:6px solid #F26B1D;border-radius:8px;' +
          'padding:3px 12px;font:600 15px/1.35 Sarabun,"Noto Sans Thai",Tahoma,sans-serif;box-shadow:0 4px 18px rgba(0,0,0,.3)';
        b.innerHTML = `<span style="opacity:.8;font-weight:500">${group} ·</span> ${label}`;
        document.documentElement.appendChild(b);
        const c = document.createElement('div');
        c.id = '__bm_caption';
        c.setAttribute('aria-hidden', 'true');
        c.style.cssText =
          'position:fixed;left:20px;bottom:18px;z-index:2147483646;pointer-events:none;' +
          'background:rgba(28,28,32,.88);color:#fff;border-radius:14px;padding:8px 18px;border-left:6px solid #F26B1D;' +
          'font:500 17px/1.4 Sarabun,"Noto Sans Thai",Tahoma,sans-serif;max-width:790px;display:none';
        document.documentElement.appendChild(c);
        try {
          const t = sessionStorage.getItem('__bm_caption');
          if (t) {
            c.textContent = t;
            c.style.display = 'block';
          }
        } catch {}
      };
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
      else mount();
    },
    { label: `${item.id} · ${item.title}`, group: item.group },
  );
}

/** คำบรรยายล่างจอ บอกคนดูว่ากำลังทำขั้นไหน */
export async function say(page: Page, text: string) {
  await page
    .evaluate((t) => {
      try {
        sessionStorage.setItem('__bm_caption', t);
      } catch {}
      const c = document.getElementById('__bm_caption');
      if (c) {
        c.textContent = t;
        c.style.display = t ? 'block' : 'none';
      }
    }, text)
    .catch(() => {});
}

/** การ์ดเปิดเคส: บอกว่าทำอะไร และผ่านเมื่อไร (ค้าง ~3 วิ) */
export async function intro(page: Page, item: PlayItem, ms = 3000) {
  await page.evaluate(
    ({ it }) => {
      const d = document.createElement('div');
      d.id = '__bm_intro';
      d.style.cssText =
        'position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;' +
        'background:rgba(20,20,24,.78);pointer-events:none;font-family:Sarabun,"Noto Sans Thai",Tahoma,sans-serif';
      const esc = (s: string) => s.replace(/[&<>]/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[ch] as string);
      d.innerHTML = `<div style="background:#fff;border-radius:18px;padding:28px 36px;max-width:820px;box-shadow:0 20px 60px rgba(0,0,0,.4);border-top:8px solid #F26B1D">
        <div style="color:#F26B1D;font-weight:700;font-size:16px">${esc(it.group)}</div>
        <div style="font-size:34px;font-weight:800;color:#222;margin:4px 0 14px">${esc(it.id)} · ${esc(it.title)}</div>
        <div style="font-size:19px;color:#333;margin-bottom:8px"><b>ทำอะไร:</b> ${esc(it.what)}</div>
        <div style="font-size:19px;color:#333"><b>ผ่านเมื่อ:</b> ${esc(it.expect)}</div></div>`;
      document.documentElement.appendChild(d);
    },
    { it: item },
  );
  await page.waitForTimeout(ms);
  await page.evaluate(() => document.getElementById('__bm_intro')?.remove()).catch(() => {});
}

export async function hold(page: Page, ms = HOLD) {
  await page.waitForTimeout(ms);
}

/** พิมพ์ทีละตัว (delay 60 ms) ให้คนดูทัน */
export async function typeHuman(locator: Locator, text: string, opts: { clear?: boolean } = {}) {
  await locator.click();
  if (opts.clear !== false) await locator.fill('');
  await locator.pressSequentially(text, { delay: 60 });
}

/** ใส่ outline สีส้มชั่วคราวให้ element ที่กำลังตรวจ */
export async function highlight(locator: Locator, ms = 4500) {
  await locator.first().scrollIntoViewIfNeeded().catch(() => {});
  await locator
    .evaluateAll((els, ms) => {
      for (const el of els as HTMLElement[]) {
        const prev = [el.style.outline, el.style.outlineOffset, el.style.boxShadow];
        el.style.outline = '4px solid #ff8c00';
        el.style.outlineOffset = '2px';
        el.style.boxShadow = '0 0 0 8px rgba(255,140,0,.25)';
        setTimeout(() => {
          [el.style.outline, el.style.outlineOffset, el.style.boxShadow] = prev;
        }, ms);
      }
    }, ms)
    .catch(() => {});
}

/** ไฮไลต์แล้วค้างภาพ (ใช้หลังได้ผลแต่ละขั้น ก่อน assert ถัดไป) */
export async function show(page: Page, locator: Locator, ms = HOLD) {
  await highlight(locator, ms + 500);
  await hold(page, ms);
}

export async function attachText(info: TestInfo, name: string, body: string) {
  await info.attach(name, { body, contentType: 'text/plain' });
}
export async function attachJson(info: TestInfo, name: string, data: unknown) {
  await info.attach(name, { body: JSON.stringify(data, null, 2), contentType: 'application/json' });
}

// ---------------- ตรวจคำตอบแบบยืดหยุ่น ----------------
/** เลขไทย → อารบิก · ตัด comma คั่นหลักพัน (7,120 → 7120) · ตัด zero-width · ช่องว่างซ้ำ → ช่องเดียว (ใช้ทั้งคำตอบและคำที่ค้น) */
export const norm = (s: string) =>
  s
    .replace(/[๐-๙]/g, (d) => String(d.charCodeAt(0) - 0x0e50))
    .replace(/[\u200b\u200c\u200d\ufeff]/g, '')
    .replace(/(\d),(?=\d{3}(?!\d))/g, '$1')
    .replace(/\s+/g, ' ')
    .trim();

export type Check = string | RegExp | { mock: string | RegExp; ai: string | RegExp };

/** mock: ต้องมีคำนั้นตรงตัว (ยอม comma) · ai: ใช้ regex ยืดหยุ่นถ้าให้มา
 *  ตรวจบนข้อความที่ผ่าน norm() แล้วทุกโหมด → regex ไม่ต้องเผื่อ comma / เลขไทย / ช่องว่างซ้ำ */
export function expectAnswer(answer: string, checks: Check[]) {
  const a = norm(answer);
  for (const c of checks) {
    const pick = typeof c === 'object' && !(c instanceof RegExp) ? (MODE === 'ai' ? c.ai : c.mock) : c;
    if (pick instanceof RegExp) expect(a, `คำตอบควรตรง ${pick}`).toMatch(pick);
    else expect(a, `คำตอบควรมี "${pick}"`).toContain(norm(pick));
  }
}

// ---------------- API helper (ใช้ cookie session เดียวกับหน้าเว็บ) ----------------
export async function apiJson(req: APIRequestContext, method: string, url: string, data?: unknown) {
  const r = await req.fetch(url, { method, data, headers: data ? { 'Content-Type': 'application/json' } : undefined });
  const t = await r.text();
  let j: any = null;
  try {
    j = JSON.parse(t);
  } catch {
    j = { raw: t };
  }
  if (!r.ok()) throw new Error(`${method} ${url} → ${r.status()} ${t.slice(0, 200)}`);
  return j;
}

export async function getStock(req: APIRequestContext, sku: string): Promise<Record<string, number>> {
  const p = await apiJson(req, 'GET', `/api/products/${sku}`);
  return Object.fromEntries((p.stock || []).map((s: any) => [s.branch, Number(s.qty)]));
}

export async function adminLogin(page: Page) {
  await page.goto('/admin');
  const pw = page.getByTestId('admin-password');
  if (await pw.isVisible().catch(() => false)) {
    await say(page, 'ล็อกอินหลังร้าน (รหัส dev)');
    await typeHuman(pw, ADMIN_PASSWORD);
    await page.getByTestId('admin-login').click();
    await expect(page.getByTestId('admin-password')).toHaveCount(0, { timeout: 20_000 });
  }
}

// ---------------- แชท ----------------
export type Answer = { text: string; cites: string[]; citeLabels: string[] };

export async function openChat(page: Page) {
  if (!(await page.getByTestId('chat-panel').isVisible().catch(() => false))) {
    await highlight(page.getByTestId('chat-open'), 1500);
    await page.waitForTimeout(800);
    await page.getByTestId('chat-open').click();
  }
  await expect(page.getByTestId('chat-panel')).toBeVisible();
  await page.waitForTimeout(800); // ให้ประวัติแชทโหลดก่อนนับข้อความ
}

/** พิมพ์คำถาม → ส่ง → รอคำตอบเสร็จ (data-done) → ไฮไลต์ + ค้างภาพ → attach คำตอบ */
export async function ask(
  page: Page,
  info: TestInfo,
  question: string,
  opts: { timeout?: number; holdMs?: number; attachName?: string; waitDone?: boolean } = {},
): Promise<Answer> {
  await openChat(page);
  const bots = page.getByTestId('chat-msg-bot');
  const before = await bots.count();
  await say(page, `พิมพ์ถามน้องช่าง: “${question}”`);
  await typeHuman(page.getByTestId('chat-input'), question);
  await page.getByTestId('chat-send').click();
  const bot = bots.nth(before);
  await expect(bot).toHaveAttribute('data-done', 'true', { timeout: opts.timeout ?? ANSWER_TIMEOUT });
  const ans = await readAnswer(page, bot);
  await info.attach(opts.attachName ?? 'answer', { body: ans.text, contentType: 'text/plain' });
  if (ans.cites.length) await attachJson(info, 'cites', ans.citeLabels);
  await say(page, ans.cites.length ? `ได้คำตอบ + ป้ายอ้างอิง ${ans.cites.join(', ')}` : 'ได้คำตอบแล้ว');
  await highlight(bot, (opts.holdMs ?? HOLD) + 500);
  const citeLoc = page.getByTestId('chat-cite');
  if (ans.cites.length) await highlight(citeLoc, (opts.holdMs ?? HOLD) + 500);
  await hold(page, opts.holdMs ?? HOLD);
  return ans;
}

/** อ่านข้อความ + cites ของ bubble บอท (cites อยู่ใน row เดียวกัน) */
export async function readAnswer(page: Page, bot: Locator): Promise<Answer> {
  const text = (await bot.innerText()).trim();
  const row = bot.locator('xpath=..');
  const cites = row.getByTestId('chat-cite');
  const n = await cites.count();
  const files: string[] = [];
  const labels: string[] = [];
  for (let i = 0; i < n; i++) {
    const href = (await cites.nth(i).getAttribute('href')) || '';
    const m = href.match(/\/api\/docs\/([^#?]+)/);
    if (m) files.push(decodeURIComponent(m[1]));
    labels.push((await cites.nth(i).innerText()).trim());
  }
  return { text, cites: [...new Set(files)], citeLabels: labels };
}

export function expectCite(ans: Answer, filename: string) {
  expect(ans.cites, `ควรมีป้ายอ้างอิง ${filename}`).toContain(filename);
}

/** สร้าง test 1 เคสจาก playlist (ชื่อ test ขึ้นต้นด้วย id) */
export function bmCase(
  id: string,
  fn: (args: { page: Page; item: PlayItem; browser: import('@playwright/test').Browser; context: import('@playwright/test').BrowserContext }, info: TestInfo) => Promise<void>,
  opts: { timeout?: number; skip?: () => string | false } = {},
) {
  const it = PLAYLIST.find((p) => p.id === id);
  if (!it) throw new Error(`ไม่พบเคส ${id} ใน playlist.json`);
  test(`${id} ${it.title}`, async ({ page, item, browser, context }, info) => {
    const why = opts.skip?.();
    test.skip(!!why, why || '');
    if (opts.timeout) test.setTimeout(opts.timeout);
    info.annotations.push({ type: 'group', description: item.group }, { type: 'mode', description: MODE });
    await fn({ page, item, browser, context }, info);
  });
}
