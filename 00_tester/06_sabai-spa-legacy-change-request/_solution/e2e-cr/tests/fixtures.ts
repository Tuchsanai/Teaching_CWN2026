import { test as base, expect, request, type APIRequestContext, type Page } from '@playwright/test';

/** วันล็อกของข้อมูลทดสอบ (เหมือน e2e-legacy) */
export const TODAY = '2026-10-10T10:00:00+07:00';

/** บัญชีทดสอบ seed (แสดงบนหน้า /login เมื่อ ALLOW_TEST_RESET=1) */
export const USERS = {
  U01: { email: 'nida@sabai.test', password: 'Nida@2026' },
  owner: { email: 'owner@sabai.test', password: 'Owner@2026' },
} as const;

/** ทุก test เริ่มจาก reset (auto fixture) · reset ไม่สำเร็จ = ล้มทันที (ไม่ข้าม) */
export const test = base.extend<{ resetDb: void; apiAs: (u?: keyof typeof USERS) => Promise<APIRequestContext> }>({
  resetDb: [async ({ baseURL }, use) => {
    const ctx = await request.newContext({ baseURL });
    const r = await ctx.post('/api/test/reset', { data: { now: TODAY } });
    await ctx.dispose();
    expect(r.ok(), `reset ${r.status()}`).toBeTruthy();
    await use();
  }, { auto: true }],
  apiAs: async ({ baseURL }, use) => {
    const ctxs: APIRequestContext[] = [];
    await use(async (u) => {
      const ctx = await request.newContext({ baseURL });
      ctxs.push(ctx);
      if (u) {
        const r = await ctx.post('/api/auth/login', { data: USERS[u] });
        expect(r.status(), `login ${u}`).toBe(200);
      }
      return ctx;
    });
    for (const c of ctxs) await c.dispose();
  },
});
export { expect };

/** เปิดหน้าแล้วรอ html[data-ready="true"] */
export async function open(page: Page, path: string) {
  await page.goto(path);
  await page.locator('html[data-ready="true"]').waitFor({ timeout: 15_000 });
}

/** เงินจาก data-amount (บาท) */
export async function amount(page: Page, testId: string) {
  const v = await page.getByTestId(testId).getAttribute('data-amount');
  return v === null ? NaN : Number(v);
}

/** หน้าจองแบบไม่ล็อกอิน: เดี่ยว <service> วันที่/เวลา → ขั้น 3 (ข้อมูลติดต่อ) */
export async function guestToStep3(page: Page, o: { service: string; date: string; time: string }) {
  await open(page, `/book?service=${o.service}&type=single`);
  await page.getByTestId('book-type-label-single').click();
  const sel = page.getByTestId('book-service');
  if (await sel.isVisible()) await sel.selectOption(o.service);
  await page.getByTestId('book-next-1').click();
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '2');
  await page.getByTestId('book-date').fill(o.date);
  await page.getByTestId(`book-slot-${o.time}`).click();
  await page.getByTestId('book-next-2').click();
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
}

/** รอให้คำขอ /api/price ที่ค้างตอบครบ และยอดขั้น 3 นิ่ง */
export async function settlePrice(page: Page) {
  const el = page.getByTestId('book-quote-total');
  await expect(el).toBeVisible();
  let prev = ''; let stable = 0;
  for (let i = 0; i < 40 && stable < 2; i++) {
    await page.waitForTimeout(250);
    const cur = await el.innerText();
    stable = cur === prev ? stable + 1 : 0;
    prev = cur;
  }
}
