import { test as base, expect, request, type APIRequestContext, type Page, type TestInfo } from '@playwright/test';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

// ---------- รายการเคส (plan-cases.json) ----------
export type PlanCase = {
  id: string; module: string; moduleCode: string; what: string; refs: string; technique: string;
  priority: 'P1' | 'P2' | 'P3'; data: string; expected: string; source: string; apiOnly: boolean;
};
const ROOT = join(__dirname, '..');
export const CASES: Record<string, PlanCase> = Object.fromEntries(
  (JSON.parse(readFileSync(join(ROOT, 'plan-cases.json'), 'utf8')) as PlanCase[]).map((c) => [c.id, c]),
);
export const REPORT_DIR = join(ROOT, 'test-report');

// วันล็อกจาก TEST-DATA.md
export const TODAY = '2026-10-10T10:00:00+07:00';

// ผู้ใช้ seed (TEST-DATA.md U01–U08 · owner จาก SPEC หัวข้อ 7)
export const USERS = {
  U01: { email: 'nida@sabai.test', password: 'Nida@2026', name: 'คุณนิดา' },
  U02: { email: 'ton@sabai.test', password: 'Ton@2026', name: 'คุณต้น' },
  U03: { email: 'may@sabai.test', password: 'May@2026', name: 'คุณเมย์' },
  U04: { email: 'fon@sabai.test', password: 'Fon@2026', name: 'คุณฝน' },
  U05: { email: 'prae@sabai.test', password: 'Prae@2026', name: 'น้องแพร' },
  U06: { email: 'vipa@sabai.test', password: 'Vipa@2026', name: 'คุณวิภา' },
  U07: { email: 'kan@sabai.test', password: 'Kan@2026', name: 'คุณกานต์' },
  U08: { email: 'liwei@sabai.test', password: 'LiWei@2026', name: 'Mr. Li Wei' },
  owner: { email: 'owner@sabai.test', password: 'Owner@2026', name: 'owner' },
} as const;
export type UserKey = keyof typeof USERS;

// ---------- API client ที่บันทึก log ทุกคำขอ ----------
export class Api {
  constructor(public ctx: APIRequestContext, public who: string, private log: string[]) {}
  private write(method: string, url: string, body: unknown, status: number, res: string) {
    const b = body === undefined ? '' : ' ' + JSON.stringify(body);
    this.log.push(`[${new Date().toISOString()}] (${this.who}) ${method} ${url}${b}\n    → ${status} ${res.slice(0, 600)}`);
  }
  async get(url: string) {
    const r = await this.ctx.get(url);
    const text = await r.text();
    this.write('GET', url, undefined, r.status(), r.headers()['content-type']?.includes('json') ? text : `<${r.headers()['content-type']} ${text.length} bytes>`);
    return { status: r.status(), json: safeJson(text), headers: r.headers() };
  }
  async post(url: string, data?: unknown) {
    const r = await this.ctx.post(url, data === undefined ? {} : { data });
    const text = await r.text();
    this.write('POST', url, data, r.status(), text);
    return { status: r.status(), json: safeJson(text) };
  }
}
function safeJson(t: string) { try { return JSON.parse(t); } catch { return null; } }

type ApiFactory = {
  anon: () => Promise<Api>;
  as: (u: UserKey) => Promise<Api>;
  reset: (now?: string) => Promise<void>;
  /** ตารางคิวของวัน (owner GET /api/admin/bookings) */
  adminBookings: (date: string) => Promise<any[]>;
  log: string[];
};

export function tcId(info: TestInfo) { return info.title.split(' ')[0]; }

export const test = base.extend<{ api: ApiFactory; resetDb: void }>({
  // ทุก TC เริ่มจาก POST /api/test/reset (แผนหัวข้อ 5) · reset ไม่สำเร็จ = "ไม่ได้รัน" (หัวข้อ 6.1)
  resetDb: [async ({ baseURL }, use, info) => {
    const ctx = await request.newContext({ baseURL });
    const r = await ctx.post('/api/test/reset', { data: { now: TODAY } });
    await ctx.dispose();
    if (!r.ok()) info.skip(true, `ไม่ได้รัน: reset ไม่สำเร็จ ${r.status()}`);
    await use();
  }, { auto: true }],

  api: async ({ baseURL }, use, info) => {
    const log: string[] = [];
    const ctxs: APIRequestContext[] = [];
    const make = async (who: string) => {
      const ctx = await request.newContext({ baseURL, extraHTTPHeaders: { 'accept-language': 'th-TH' } });
      ctxs.push(ctx); return new Api(ctx, who, log);
    };
    const as = async (u: UserKey) => {
      const a = await make(u);
      const r = await a.post('/api/auth/login', { email: USERS[u].email, password: USERS[u].password });
      expect(r.status, `login ${u}`).toBe(200);
      return a;
    };
    let owner: Api | undefined;
    const f: ApiFactory = {
      log,
      anon: () => make('ไม่ล็อกอิน'),
      as,
      reset: async (now = TODAY) => { const a = await make('reset'); const r = await a.post('/api/test/reset', { now }); expect(r.status).toBe(200); },
      adminBookings: async (date) => {
        owner ??= await as('owner');
        const r = await owner.get(`/api/admin/bookings?date=${date}`);
        expect(r.status, 'owner อ่านตารางคิว').toBe(200);
        return r.json.bookings as any[];
      },
    };
    await use(f);
    for (const c of ctxs) await c.dispose();
    if (log.length) {
      const dir = join(REPORT_DIR, 'logs'); mkdirSync(dir, { recursive: true });
      const id = tcId(info);
      const file = join(dir, `${id}${info.project.name === 'api' ? '' : '.' + info.project.name}.log`);
      writeFileSync(file, `# ${info.title}\n# project: ${info.project.name} · status: ${info.status}\n\n${log.join('\n')}\n`);
      await info.attach('api-log', { path: file, contentType: 'text/plain' });
    }
  },

  page: async ({ page }, use) => {
    trackPrice(page);
    await use(page);
  },
});
export { expect };

/** ประกาศ test ตามรหัส TC: ชื่อขึ้นต้นด้วยรหัส · tag โมดูล + ระดับ · annotation ผลที่คาดหวัง/ที่มา */
export function tc(id: string, body: Parameters<typeof test>[2]) {
  const c = CASES[id];
  if (!c) throw new Error(`ไม่มี ${id} ในแผน`);
  test(`${id} ${c.what}`, {
    tag: [`@${c.moduleCode}`, `@${c.priority}`],
    annotation: [
      { type: 'ผลที่คาดหวัง', description: c.expected },
      { type: 'ที่มา', description: c.source },
      { type: 'ข้อมูล', description: c.data },
    ],
  }, body);
}

// ---------- ตัวช่วยหน้าเว็บ ----------
export async function open(page: Page, path: string) {
  await page.goto(path);
  await page.locator('html[data-ready="true"]').waitFor({ timeout: 15_000 });
}

export async function loginUI(page: Page, u: UserKey) {
  await open(page, '/login');
  await page.getByTestId('login-email').fill(USERS[u].email);
  await page.getByTestId('login-password').fill(USERS[u].password);
  await page.getByTestId('login-submit').click();
  await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 15_000 });
  await page.locator('html[data-ready="true"]').waitFor();
}

export async function logoutUI(page: Page) {
  await page.request.post('/api/auth/logout');
  await page.context().clearCookies({ name: 'sabai_session' });
}

/** เงินจาก data-amount (บาท) */
export async function amount(page: Page, testId: string) {
  const v = await page.getByTestId(testId).getAttribute('data-amount');
  return v === null ? NaN : Number(v);
}

export type BookOpts = {
  type?: 'single' | 'couple' | 'group' | 'package' | 'course';
  service?: string; people?: number; date: string; time: string; therapist?: string;
};

/** ขั้น 1 → 2 (เลือกแบบ บริการ จำนวนคน แล้วกดถัดไป) */
export async function bookStep1(page: Page, o: Omit<BookOpts, 'date' | 'time'>) {
  const q = new URLSearchParams();
  if (o.service) q.set('service', o.service);
  if (o.type) q.set('type', o.type);
  if (o.people) q.set('people', String(o.people));
  await open(page, `/book?${q}`);
  if (o.type) await page.getByTestId(`book-type-label-${o.type}`).click();
  if (o.service && o.type !== 'package' && o.type !== 'course') {
    const sel = page.getByTestId('book-service');
    if (await sel.isVisible()) await sel.selectOption(o.service);
  }
  if (o.people) {
    const ppl = page.getByTestId('book-people');
    if (await ppl.isVisible() && await ppl.isEditable()) await ppl.fill(String(o.people));
  }
  await page.getByTestId('book-next-1').click();
}

/** ขั้น 2 → 3 (วัน รอบ นักบำบัด แล้วกดถัดไป) */
export async function bookStep2(page: Page, o: BookOpts) {
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '2');
  await page.getByTestId('book-date').fill(o.date);
  await page.getByTestId(`book-slot-${o.time}`).click();
  if (o.therapist) await page.getByTestId('book-therapist').selectOption(o.therapist);
  await page.getByTestId('book-next-2').click();
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
}

/** เปิด /book แล้วเดินถึงขั้น 3 */
export async function bookToStep3(page: Page, o: BookOpts) {
  await bookStep1(page, o);
  await bookStep2(page, o);
}

export async function fillContact(page: Page, name: string, phone: string) {
  await page.getByTestId('book-contact-name').fill(name);
  await page.getByTestId('book-contact-phone').fill(phone);
}

// นับคำขอ /api/price ที่ยังไม่ตอบ — ใช้รอให้ราคาบนหน้าจออัปเดตหลังติ๊ก/เลือกตัวเลือก
const pending = new WeakMap<Page, number>();
export function trackPrice(page: Page) {
  pending.set(page, 0);
  const isPrice = (u: string) => u.includes('/api/price');
  page.on('request', (r) => { if (isPrice(r.url())) pending.set(page, (pending.get(page) ?? 0) + 1); });
  const done = (r: { url(): string }) => { if (isPrice(r.url())) pending.set(page, Math.max(0, (pending.get(page) ?? 1) - 1)); };
  page.on('requestfinished', done); page.on('requestfailed', done);
}

/** รอจนไม่มี /api/price ค้าง และตัวเลขบนจอไม่เปลี่ยน 2 รอบติด (ไม่ได้รอ "ค่าที่อยากได้" — แค่รอให้หน้าเว็บคิดเสร็จ) */
export async function settle(page: Page, read?: () => Promise<unknown>) {
  await page.waitForTimeout(250);
  let prev = read ? await read() : undefined; let stable = 0;
  for (let i = 0; i < 40 && stable < 2; i++) {
    await page.waitForTimeout(200);
    const cur = read ? await read() : undefined;
    stable = (pending.get(page) ?? 0) === 0 && cur === prev ? stable + 1 : 0;
    prev = cur;
  }
}

/** ยอดสุทธิขั้น 3 (ราคามาจาก /api/price) เป็นตัวเลขบาท */
export async function quoteTotal(page: Page) {
  const el = page.getByTestId('book-quote-total');
  await expect(el).toBeVisible();
  const read = async () => {
    const m = (await el.innerText()).replace(/,/g, '').match(/฿\s*([\d.]+)/);
    return m ? Number(m[1]) : NaN;
  };
  await settle(page, read);
  return read();
}

export async function toSummary(page: Page) {
  await settle(page);
  await page.getByTestId('book-next-3').click();
  await expect(page.getByTestId('book-summary')).toBeVisible();
}
