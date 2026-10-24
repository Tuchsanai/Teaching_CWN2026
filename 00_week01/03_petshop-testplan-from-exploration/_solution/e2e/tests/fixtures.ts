import { test as base, expect, type Page, type Locator, type TestInfo } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * Shared helpers for every spec.
 *
 * - step(title, fn)            one Thai step of the test case ("ขั้นตอน")
 * - check(page, name, target, run)   one checkpoint ("จุดตรวจ") using expect.soft, so a wrong value
 *                              does not stop the test: every checkpoint is checked and counted.
 *   When a checkpoint fails, the wrong element is circled in red on screen with
 *   "คาดหวัง … / ได้จริง …", held for the video, and a screenshot is attached.
 * - At the end of every test, steps + checkpoint results are attached as evidence.json
 *   for the HTML report (reporters/html-report.ts).
 */

type CheckResult = { step: string; name: string; ok: boolean; expected?: string; received?: string };
type Evidence = { steps: string[]; checks: CheckResult[]; stoppedAt?: { step: string; message: string } };

const evidence = new WeakMap<TestInfo, Evidence & { step: string; softErrors: number }>();
const state = (info: TestInfo) => {
  let s = evidence.get(info);
  if (!s) evidence.set(info, (s = { steps: [], checks: [], step: '', softErrors: 0 }));
  return s;
};

const isRecorded = (info: TestInfo) => info.project.name === 'chromium';
const stripAnsi = (s = '') => s.replace(/\u001b\[[0-9;]*m/g, '');

/** Pull "Expected: … / Received: …" out of a Playwright assertion message. */
function parseError(message?: string) {
  const msg = stripAnsi(message);
  const pick = (label: string) => msg.match(new RegExp(`^\\s*${label}(?: [a-z ]+)?:\\s*(.+)$`, 'm'))?.[1]?.trim();
  return {
    expected: pick('Expected'),
    received: pick('Received') ?? (/element\(s\) not found/.test(msg) ? 'ไม่พบบนหน้าจอ' : undefined),
    first: msg.split('\n').find((l) => l.trim())?.trim() ?? '',
  };
}

// Recorded runs: caption with the test title + a red ripple wherever Playwright clicks.
const overlayScript = (caption: string) => `
  (() => {
    const add = () => {
      if (document.getElementById('__pw-caption')) return;
      const bar = document.createElement('div');
      bar.id = '__pw-caption';
      bar.textContent = ${JSON.stringify('🎬 ' + caption)};
      bar.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:2147483646;pointer-events:none;' +
        'background:rgba(30,42,58,.92);color:#fff;font:700 20px/1.4 "IBM Plex Sans Thai",sans-serif;' +
        'padding:8px 18px;border-radius:999px;box-shadow:0 6px 20px rgba(0,0,0,.25);max-width:80vw';
      document.documentElement.appendChild(bar);
      const css = document.createElement('style');
      css.textContent = '@keyframes __pwr{from{transform:translate(-50%,-50%) scale(.3);opacity:1}to{transform:translate(-50%,-50%) scale(1.6);opacity:0}}';
      document.documentElement.appendChild(css);
      document.addEventListener('mousedown', (e) => {
        const dot = document.createElement('div');
        dot.style.cssText = 'position:fixed;z-index:2147483646;pointer-events:none;width:56px;height:56px;' +
          'border:4px solid #ff8a00;border-radius:50%;left:' + e.clientX + 'px;top:' + e.clientY + 'px;' +
          'animation:__pwr .7s ease-out forwards';
        document.documentElement.appendChild(dot);
        setTimeout(() => dot.remove(), 800);
      }, true);
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
  })();`;

/** Circle the wrong element in red with a label. Falls back to a banner when the element is not on screen. */
async function markOnScreen(page: Page, targets: (Locator | undefined)[], title: string, detail: string) {
  let box: { x: number; y: number; width: number; height: number } | null = null;
  for (const t of targets) {
    if (!t || box) continue;
    try {
      await t.first().scrollIntoViewIfNeeded({ timeout: 1500 });
      box = await t.first().boundingBox({ timeout: 1500 });
    } catch { /* not on this page */ }
  }
  await page.evaluate(({ box, title, detail }) => {
    document.querySelectorAll('.__pw-fail').forEach((e) => e.remove());
    const add = (css: string, html = '') => {
      const el = document.createElement('div');
      el.className = '__pw-fail';
      el.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;' + css;
      el.innerHTML = html;
      document.documentElement.appendChild(el);
      return el;
    };
    const label = '<b style="font-size:20px">' + title + '</b><br><span style="font-size:17px">' + detail + '</span>';
    const pill = 'background:#d91a1a;color:#fff;font:600 17px/1.45 "IBM Plex Sans Thai",sans-serif;padding:8px 16px;' +
      'border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,.3);max-width:620px;';
    if (box) {
      const pad = 14;
      add(`left:${box.x - pad}px;top:${box.y - pad}px;width:${box.width + pad * 2}px;height:${box.height + pad * 2}px;` +
        'border:5px solid #ff1f1f;border-radius:50%;box-shadow:0 0 0 4px rgba(255,255,255,.85),0 0 24px rgba(255,0,0,.6);');
      const below = box.y + box.height + pad + 12;
      const top = below + 90 < innerHeight ? below : Math.max(8, box.y - pad - 96);
      add(pill + `left:${Math.max(8, Math.min(box.x - pad, innerWidth - 640))}px;top:${top}px;`, label);
    } else {
      add(pill + 'left:50%;top:16px;transform:translateX(-50%);', '⚠️ ' + label);
    }
  }, { box, title, detail }).catch(() => {});
}

export const test = base.extend<{ page: Page; _evidence: void; _cleanState: void }>({
  // TEST-PLAN.md หัวข้อ 5 กติกา: ทุกข้อเริ่มจากสถานะสะอาด → POST /api/test/reset ก่อนทุก test
  // (localStorage ของ localhost:3000 สะอาดอยู่แล้ว เพราะ Playwright เปิด browser context ใหม่ทุก test)
  _cleanState: [async ({ request }, use) => {
    const res = await request.post('/api/test/reset');
    expect(res.ok(), 'POST /api/test/reset ต้องได้ 200').toBeTruthy();
    await use();
  }, { auto: true }],

  // Runs for every test (also API-only tests): attach steps + checkpoints for the report.
  _evidence: [async ({}, use, testInfo) => {
    await use();
    const s = state(testInfo);
    const out: Evidence = { steps: s.steps, checks: s.checks, stoppedAt: s.stoppedAt };
    await testInfo.attach('evidence.json', { body: JSON.stringify(out), contentType: 'application/json' });
  }, { auto: true }],

  page: async ({ page }, use, testInfo) => {
    if (isRecorded(testInfo)) await page.addInitScript(overlayScript(testInfo.title));
    await use(page);

    // A hard failure (timeout, missing element) stopped the test: circle what it was waiting for.
    const s = state(testInfo);
    const hard = testInfo.errors.length > s.softErrors ? testInfo.errors[testInfo.errors.length - 1] : undefined;
    if (hard && !page.isClosed()) {
      const { first } = parseError(hard.message);
      s.stoppedAt = { step: s.step || '-', message: first };
      const testId = stripAnsi(hard.message).match(/getByTestId\('([^']+)'\)/)?.[1];
      await markOnScreen(page, [testId ? page.getByTestId(testId) : undefined], '❌ หยุดกลางทาง: ' + (s.step || 'ขั้นแรก'), first.slice(0, 140));
      await testInfo.attach('วงจุดที่ผิด', { body: await page.screenshot(), contentType: 'image/png' }).catch(() => {});
    }
    if (isRecorded(testInfo)) await page.waitForTimeout(hard ? 2500 : 1500); // end the video on the result
  },
});

export { expect };
export type { Page } from '@playwright/test';

/** One step of the test case, e.g. step('1. เปิดหน้าสินค้า', async () => { … }). */
export async function step(title: string, fn: () => Promise<void>) {
  const s = state(test.info());
  s.step = title;
  s.steps.push(title);
  await test.step(title, fn);
}

/**
 * One checkpoint. `run` must use expect.soft(...) so a wrong value is recorded but the test continues.
 * `target` is the element to circle when it fails; `near` is used when the target itself is missing
 * (e.g. an error message that should have appeared under an input).
 */
export async function check(
  page: Page | null,
  name: string,
  target: Locator | null,
  run: () => unknown,
  opts: { near?: Locator; expected?: string } = {},
) {
  const info = test.info();
  const s = state(info);
  await test.step(`ตรวจ: ${name}`, async () => {
    const before = info.errors.length;
    await run();
    const failed = info.errors.length > before;
    const parsed = failed ? parseError(info.errors[info.errors.length - 1].message) : undefined;
    const expected = opts.expected ?? parsed?.expected;
    const received = parsed?.received ?? parsed?.first;
    s.checks.push({ step: s.step, name, ok: !failed, ...(failed ? { expected, received } : {}) });
    if (!failed) return;
    s.softErrors = info.errors.length;
    if (!page || page.isClosed()) return;
    await markOnScreen(page, [target ?? undefined, opts.near], '❌ ' + name,
      `คาดหวัง: ${expected ?? '-'}  ·  ได้จริง: ${received ?? '-'}`);
    if (isRecorded(info)) await page.waitForTimeout(2200);
    await info.attach(`วงจุดที่ผิด: ${name}`, { body: await page.screenshot(), contentType: 'image/png' });
  });
}

/** Open a page and wait until the app has loaded cart/wishlist from localStorage. */
export async function open(page: Page, path: string) {
  await page.goto(path);
  await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
}


// ---- ข้อมูลจากแผน (TEST-PLAN.md หัวข้อ 5) ----

type PlanRow = { module: string; what: string; technique: string; priority: string; expected: string; source: string };
const PLAN_FILE = ['..', '../..'].map((up) => path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', up, 'TEST-PLAN.md')).find((f) => fs.existsSync(f));
const PLAN = new Map<string, PlanRow>();
if (PLAN_FILE) {
  for (const line of fs.readFileSync(PLAN_FILE, 'utf8').split(/\r?\n/)) {
    if (!/^\| TC-/.test(line)) continue;
    const c = line.split('|').slice(1, -1).map((x) => x.trim().replace(/\*\*/g, ''));
    PLAN.set(c[0], { module: c[1], what: c[2], technique: c[3], priority: c[4], expected: c[5], source: c[6] ?? '' });
  }
}

/**
 * tag + annotation ของ test case จากแผน: test('TC-…', plan('TC-…', '@cart'), async ({ page }) => …)
 * - tag = โมดูล + ระดับ (ระดับอ่านจากแผน จึงตรงกับแผนเสมอ)
 * - annotation "expected" = ผลที่คาดหวังจากแผน (ตัวอักษรเดียวกับในแผน) · "source" = ที่มา [D]/[R]/[O]
 */
export function plan(id: string, moduleTag: string) {
  const row = PLAN.get(id);
  if (!row) throw new Error(`${id} ไม่มีใน TEST-PLAN.md หัวข้อ 5`);
  return {
    tag: [moduleTag, '@' + row.priority],
    annotation: [
      { type: 'expected', description: row.expected },
      { type: 'source', description: row.source },
    ],
  };
}

// ---- ข้อมูลทดสอบ (TEST-PLAN.md หัวข้อ 7) ----
export const DEMO = { email: 'demo@pawpantry.test', password: 'Paw12345' };
export const ADDRESS = {
  name: 'สมใจ ใจดี', phone: '0812345678', postcode: '10110', address: '99 ถนนสุขุมวิท แขวงคลองเตย', province: 'กรุงเทพมหานคร',
};

/** สินค้าที่แผนใช้ (หัวข้อ 5 "ชุดสินค้าที่ใช้") → slug/ขนาด ที่เห็นบนหน้าเว็บ */
export const P = {
  kitten400: { slug: 'kitten-salmon-dry', size: '400 g' },
  kitten15: { slug: 'kitten-salmon-dry', size: '1.5 kg' },
  adultChicken3kg: { slug: 'adult-chicken-dry', size: '3 kg' },
  squeakyBall: { slug: 'dog-squeaky-ball' },
  featherWand: { slug: 'cat-feather-wand' },
  slowBowl: { slug: 'dog-slow-bowl' },
  largeBreedBeef: { slug: 'large-breed-beef-dry' },
  adultLamb3kg: { slug: 'adult-lamb-dry', size: '3 kg' },
  tunaPouch: { slug: 'tuna-pouch', size: 'ซอง 85 g' },
  seniorTuna: { slug: 'senior-tuna-dry' },
  catTunnel: { slug: 'cat-tunnel' },
  hairball: { slug: 'hairball-control-dry' },
  freezeDriedChicken: { slug: 'freeze-dried-chicken-cat' },
} as const;
type Item = { slug: string; size?: string };

// ---- ตัวช่วยกดหน้าเว็บ ----

/** "฿1,234" → 1234 · "-฿59" → 59 · "ฟรี" → 0 */
export function baht(text: string | null) {
  return Number((text ?? '').replace(/[^\d]/g, '') || 0);
}

/** เปิดหน้าสินค้า เลือกขนาด ใส่จำนวน แล้วกด "เพิ่มลงตะกร้า" */
export async function addToCart(page: Page, item: Item, qty = 1) {
  await open(page, `/products/${item.slug}`);
  if (item.size) await page.locator(`[data-testid="size-option"][data-size="${item.size}"]`).click();
  if (qty !== 1) await page.getByTestId('qty-input').fill(String(qty));
  await page.getByTestId('add-to-cart').click();
  await expect(page.getByTestId('toast')).toBeVisible();
}

export async function login(page: Page, email = DEMO.email, password = DEMO.password) {
  if (!/\/login/.test(page.url())) await open(page, '/login');
  await page.getByTestId('login-email').fill(email);
  await page.getByTestId('login-password').fill(password);
  await page.getByTestId('login-submit').click();
  await expect(page.getByTestId('logout-button')).toBeVisible();
}

/** กด "ออกจากระบบ" แล้วรอให้เว็บพากลับหน้าแรกจนเสร็จ (ถ้าสั่ง goto ระหว่างนั้น Firefox จะยกเลิกการเปิดหน้า) */
export async function logout(page: Page) {
  const navigated = page.waitForEvent('framenavigated', { timeout: 5000 }).catch(() => {});
  await page.getByTestId('logout-button').click();
  await navigated;
  await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
  await expect(page.getByTestId('login-link')).toBeVisible();
}

export async function register(page: Page, name: string, email: string, password: string) {
  await open(page, '/register');
  await page.getByTestId('reg-name').fill(name);
  await page.getByTestId('reg-email').fill(email);
  await page.getByTestId('reg-password').fill(password);
  await page.getByTestId('reg-confirm').fill(password);
  await page.getByTestId('reg-terms').check();
  await page.getByTestId('reg-submit').click();
}

export async function applyCoupon(page: Page, code: string) {
  await page.getByTestId('coupon-input').fill(code);
  await page.getByTestId('coupon-apply').click();
  await expect(page.getByTestId('coupon-message')).toBeVisible();
}

/** กรอกที่อยู่มาตรฐาน (หัวข้อ 7.2) — แทนบางช่องด้วย overrides */
export async function fillAddress(page: Page, overrides: Partial<typeof ADDRESS> = {}) {
  const a = { ...ADDRESS, ...overrides };
  await page.getByTestId('ship-name').fill(a.name);
  await page.getByTestId('ship-phone').fill(a.phone);
  await page.getByTestId('ship-postcode').fill(a.postcode);
  await page.getByTestId('ship-address').fill(a.address);
  await page.getByTestId('ship-province').selectOption({ label: a.province });
}

/** ตัวเลขในสรุปยอด (ตะกร้า / ชำระเงิน / คำสั่งซื้อ ใช้ data-testid เดียวกัน) */
export const summary = (page: Page) => ({
  subtotal: page.getByTestId('summary-subtotal'),
  discount: page.getByTestId('summary-discount'),
  shipping: page.getByTestId('summary-shipping'),
  total: page.getByTestId('summary-total'),
});

/** expect.soft ที่รอให้ตัวเลขอัปเดตก่อน (poll) */
const softExpect = expect.configure({ soft: true });

/** ตรวจ 4 ตัวเลขในสรุปยอดทีละจุด (แต่ละจุดเป็น 1 checkpoint) · shipping 0 = "ฟรี" */
export async function checkSummary(page: Page, prefix: string, want: { subtotal?: number; discount?: number; shipping?: number; total: number }) {
  const label = prefix ? prefix + ' ' : '';
  const s = summary(page);
  if (want.subtotal !== undefined)
    await check(page, `${label}ยอดสินค้า = ฿${want.subtotal.toLocaleString()}`, s.subtotal, () => softExpect.poll(async () => baht(await s.subtotal.innerText()), { timeout: 4000 }).toBe(want.subtotal));
  if (want.discount !== undefined)
    await check(page, `${label}ส่วนลด = ฿${want.discount.toLocaleString()}`, s.discount, () => softExpect.poll(async () => baht(await s.discount.innerText()), { timeout: 4000 }).toBe(want.discount));
  if (want.shipping !== undefined) {
    if (want.shipping === 0) await check(page, `${label}ค่าส่ง = ฟรี`, s.shipping, () => expect.soft(s.shipping).toHaveText(/ฟรี/));
    else await check(page, `${label}ค่าส่ง = ฿${want.shipping}`, s.shipping, () => softExpect.poll(async () => baht(await s.shipping.innerText()), { timeout: 4000 }).toBe(want.shipping));
  }
  await check(page, `${label}ยอดชำระ = ฿${want.total.toLocaleString()}`, s.total, () => softExpect.poll(async () => baht(await s.total.innerText()), { timeout: 4000 }).toBe(want.total));
}

/** login demo + ของในตะกร้า → หน้าชำระเงินพร้อมที่อยู่มาตรฐาน */
export async function toCheckout(page: Page, items: [Item, number][]) {
  await open(page, '/login');
  await login(page);
  for (const [item, qty] of items) await addToCart(page, item, qty);
  await open(page, '/checkout');
  await fillAddress(page);
}

export async function placeOrder(page: Page) {
  await page.getByTestId('place-order').click();
  await page.waitForURL(/\/orders\/PP-\d+/);
  await expect(page.getByTestId('order-success')).toBeVisible();
}
