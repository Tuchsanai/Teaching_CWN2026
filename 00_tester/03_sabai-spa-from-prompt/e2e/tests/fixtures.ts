import { test as base, expect, type Page, type Locator, type APIRequestContext, type APIResponse, type TestInfo } from '@playwright/test';

const GIF = !!process.env.GIF;

// โหมด GIF: ป้ายชื่อ test มุมซ้ายล่าง + วงแดงตรงจุดคลิก เพื่อให้คนดู GIF ตามขั้นตอนได้
const overlayScript = (caption: string) => `
  (() => {
    const add = () => {
      if (document.getElementById('__pw-caption')) return;
      const bar = document.createElement('div');
      bar.id = '__pw-caption';
      bar.textContent = ${JSON.stringify('🎬 ' + caption)};
      bar.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:2147483647;pointer-events:none;' +
        'background:rgba(46,33,24,.92);color:#fff;font:700 20px/1.4 "Noto Sans Thai","Leelawadee UI",sans-serif;' +
        'padding:10px 20px;border-radius:999px;box-shadow:0 6px 20px rgba(0,0,0,.25);max-width:80vw';
      document.documentElement.appendChild(bar);
      const css = document.createElement('style');
      css.textContent = '@keyframes __pwr{from{transform:translate(-50%,-50%) scale(.3);opacity:1}to{transform:translate(-50%,-50%) scale(1.6);opacity:0}}';
      document.documentElement.appendChild(css);
      document.addEventListener('mousedown', (e) => {
        const dot = document.createElement('div');
        dot.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;width:60px;height:60px;' +
          'border:4px solid #ff2d2d;border-radius:50%;left:' + e.clientX + 'px;top:' + e.clientY + 'px;' +
          'animation:__pwr .7s ease-out forwards';
        document.documentElement.appendChild(dot);
        setTimeout(() => dot.remove(), 800);
      }, true);
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
  })();`;

export const test = base.extend<{ page: Page; apiLog: ApiLog }>({
  page: async ({ page }, use, testInfo) => {
    if (GIF) await page.addInitScript(overlayScript(testInfo.title));
    await use(page);
    if (GIF) await page.waitForTimeout(2500); // ค้างเฟรมสุดท้าย 2.5 วินาที ให้ GIF จบที่ผลลัพธ์
  },
  // log ของ API (request / HTTP status / body) แนบให้อัตโนมัติเมื่อ test จบ แม้ test จะล้ม
  apiLog: async ({}, use, testInfo) => {
    const log = new ApiLog(testInfo);
    await use(log);
    if (log.size) await log.save();
  },
});

/** บันทึกหมายเหตุลงรายงาน (type "note") หรือค่าที่ "ต้องถาม" พร้อมค่าที่เว็บแสดงจริง */
export function note(text: string, kind: 'note' | 'ต้องถาม' = 'note') {
  test.info().annotations.push({ type: kind, description: text });
}

export { expect };

/** เปิดหน้าแล้วรอจนเว็บโหลดข้อมูลเสร็จ (<html data-ready="true">) */
export async function open(page: Page, path: string) {
  await page.goto(path);
  await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
}

/** ผู้ใช้ seed (SPEC §6.1) รหัสผ่านเดียวกันทุกคน */
export const PASSWORD = 'Sabai1234!';
export const USERS = {
  nida: 'nida@sabai.test',
  ton: 'ton@sabai.test',
  new: 'new@sabai.test',
} as const;

/** login ผ่าน API — ส่ง page.request เพื่อให้ cookie sabai_session ใช้กับหน้าเว็บใน browser เดียวกัน */
export async function loginByApi(request: APIRequestContext, who: keyof typeof USERS | string, password = PASSWORD) {
  const email = who in USERS ? USERS[who as keyof typeof USERS] : who;
  const res = await request.post('/api/auth/login', { data: { email, password } });
  expect(res.status(), await res.text()).toBe(200);
  return (await res.json()).user;
}

/** อีเมลไม่ซ้ำ (3 เบราว์เซอร์รันพร้อมกัน จึงห้ามใช้อีเมลตายตัวกับการสมัครใหม่) */
export function uniqueEmail(tag = 'tester') {
  return `${tag}-${Date.now()}-${Math.floor(Math.random() * 1e6)}@sabai.test`;
}

/** สร้างสมาชิกใหม่ผ่าน API (และ login ให้ context นั้นทันที) */
export async function createUser(request: APIRequestContext, opts: { name?: string; birthMonth?: number } = {}) {
  const user = { name: opts.name ?? 'นักทดสอบ', email: uniqueEmail(), password: 'Test12345', birthMonth: opts.birthMonth ?? 5 };
  const res = await request.post('/api/auth/register', { data: user });
  expect(res.status(), await res.text()).toBe(201);
  return user;
}

/** ตั้งค่าสมาชิกด้วย POST /api/test/user (U{…} ใน TEST-PLAN) */
export async function setMember(
  request: APIRequestContext,
  email: string,
  patch: { totalSpent?: number; points?: number; birthMonth?: number; birthdayUsedYear?: number | null; coursePurchasedOn?: string; courseUsed?: number },
) {
  const res = await request.post('/api/test/user', { data: { email, ...patch } });
  expect(res.status(), await res.text()).toBe(200);
  return res.json();
}

/**
 * "ร่างโคลน" ของผู้ใช้ seed: สมัครสมาชิกใหม่อีเมลไม่ซ้ำ (login ให้ context นั้นทันที) แล้วตั้งยอด/แต้ม/คอร์สให้เหมือนผู้ใช้ใน TEST-PLAN
 * ใช้แทนการแก้ nida / ton / new ตรง ๆ เพราะ 3 เบราว์เซอร์รันพร้อมกัน — ถ้าแก้คนเดียวกันผลจะชนกัน
 */
export async function createMember(
  request: APIRequestContext,
  opts: { totalSpent?: number; points?: number; birthMonth?: number; course?: { used?: number; purchasedOn?: string } } = {},
) {
  const user = await createUser(request, { birthMonth: opts.birthMonth ?? 5 });
  if (opts.course) {
    const c = await request.post('/api/courses');
    expect(c.status(), await c.text()).toBe(201);
  }
  await setMember(request, user.email, {
    totalSpent: opts.totalSpent ?? 0,
    points: opts.points ?? 0,
    ...(opts.course?.used !== undefined ? { courseUsed: opts.course.used } : {}),
    ...(opts.course?.purchasedOn ? { coursePurchasedOn: opts.course.purchasedOn } : {}),
  });
  return user;
}

/** ข้อมูลของนิดา (Gold ฿12,400 · 124 แต้ม) / ต้น (Platinum ฿30,000 · 250 แต้ม) ตาม SPEC §6.1 */
export const NIDA_LIKE = { totalSpent: 12400, points: 124 };
export const TON_LIKE = { totalSpent: 30000, points: 250 };

/**
 * วันจองแยกตามเบราว์เซอร์ + ตาม TC กันจองชนกันตอนรันพร้อมกัน (reset ครั้งเดียวใน global-setup)
 * today = 2026-10-08 → จองได้ 2026-10-09 ถึง 2026-11-07
 * 2026-10-09 ถึง 10-13 ไม่ใช้จองจริง (10-09/10-10 มีคิว seed และใช้ตรวจแบบอ่านอย่างเดียว, 10-11/10-13 ใช้ใน TC-BOOK-02)
 * chromium = 10-14…10-21 · firefox = 10-22…10-29 · webkit = 10-30…11-06
 */
export const DAY = { BOOK01: 0, MOB01: 0, BOOK04: 1, BOOK05: 2, API02: 3, MEM: 4, WAL: 5, GIFT: 6, BOOK07: 7 } as const;
const BROWSER_INDEX: Record<string, number> = { chromium: 0, firefox: 1, webkit: 2 };
export function bookingDate(browserName: string, slot = 0) {
  const d = new Date('2026-10-14T00:00:00Z');
  d.setUTCDate(d.getUTCDate() + (BROWSER_INDEX[browserName] ?? 0) * 8 + slot);
  return d.toISOString().slice(0, 10);
}

/** แปลง "฿1,234" / "-฿40" / "−฿40" / "+7" → ตัวเลข (ติดลบได้) · "ฟรี" / "Free" → 0 */
export function money(text: string | null) {
  const s = (text ?? '').trim();
  if (/^(ฟรี|Free|免费)$/.test(s)) return 0;
  const n = Number(s.replace(/[^\d]/g, ''));
  return /^[-−]/.test(s) ? -n : n;
}
/** ตัวเลขในข้อความ (เดิม) */
export function baht(text: string | null) {
  return Number((text ?? '').replace(/[^\d]/g, ''));
}

/** รอให้ข้อความของ element แปลงเป็นตัวเลขได้ตามที่คาด (ราคา/แต้มอัปเดตหลังเรียก /api/quote) */
export async function expectMoney(locator: Locator, value: number, message?: string) {
  await expect.poll(async () => money(await locator.textContent()), { message: message ?? String(locator) }).toBe(value);
}

/* ---------- หน้า /book ---------- */

/** เลือกวันในปฏิทิน (กดเดือนถัดไปจนเจอวันนั้น) */
export async function pickDate(page: Page, date: string) {
  const day = page.getByTestId(`cal-day-${date}`);
  for (let i = 0; i < 3 && !(await day.isVisible()); i++) await page.getByTestId('cal-next').click();
  await day.click();
}

/** ตั้งจำนวนคนในช่อง booking-people */
export async function setPeople(page: Page, n: number) {
  const box = page.getByTestId('booking-people');
  await box.fill(String(n));
  await expect(box).toHaveValue(String(n));
}

/** เลือกรอบเวลา เช่น "10:00" */
export function slot(page: Page, time: string) {
  return page.getByTestId(`slot-${time.replace(':', '-')}`);
}

/** จองผ่าน /book แบบลูกค้าทั่วไปหรือสมาชิก (หน้าต้องเปิด /book อยู่แล้ว) */
export async function fillBooking(page: Page, o: { service?: string; people?: number; date: string; time: string; guest?: boolean }) {
  if (o.service) await page.getByTestId(`service-option-${o.service}`).click();
  if (o.people) await setPeople(page, o.people);
  await pickDate(page, o.date);
  await slot(page, o.time).click();
  if (o.guest) {
    await page.getByTestId('booking-guest-name').fill('Mei');
    await page.getByTestId('booking-guest-phone').fill('0812345678');
  }
}

export const GUEST = { guestName: 'Mei', guestPhone: '0812345678' };

/** body ของ POST /api/bookings (ค่า default ตาม SPEC §5) */
export function bookingBody(o: Record<string, unknown>) {
  return {
    service: 'thai-massage', people: 1, therapistId: null, transport: false, hotelId: null, redeemSets: 0,
    useBirthday: false, payWith: 'cash', giftCode: null, source: 'web', ...GUEST, ...o,
  };
}

/** สถานะของรอบเวลาจาก GET /api/availability */
export async function slotStatus(request: APIRequestContext, q: { service: string; date: string; people?: number; therapistId?: number }, time: string) {
  const qs = new URLSearchParams({ service: q.service, date: q.date, people: String(q.people ?? 1) });
  if (q.therapistId) qs.set('therapistId', String(q.therapistId));
  const r = await (await request.get(`/api/availability?${qs}`)).json();
  return (r.slots as { time: string; status: string }[]).find((s) => s.time === time)?.status;
}

/** หน่วงให้คนดู GIF อ่านผลทัน (ไม่มีผลตอนรันปกติ) */
export async function pause(page: Page, ms = 1200) {
  if (GIF) await page.waitForTimeout(ms);
}

/** ตัวอักษรไทย (ไม่นับเครื่องหมาย ฿ U+0E3F ซึ่งใช้ทุกภาษา) */
export const THAI = /[\u0E01-\u0E3A\u0E40-\u0E5B]/;

/** เปิดแชท — ปุ่ม chat-toggle มีแอนิเมชันลอยขึ้นลงตลอดเวลา (ตั้งใจออกแบบ) จึงกดแบบไม่รอให้นิ่ง */
export async function openChat(page: Page) {
  await page.getByTestId('chat-toggle').click({ force: true });
  await expect(page.getByTestId('chat-panel')).toBeVisible();
}

/**
 * เก็บหลักฐานของ TC ที่เรียก API (TEST-PLAN §7): request, HTTP status และ response body ทุกครั้ง
 * แนบเป็น attachment ชื่อ "api-log" → reporter เขียนเป็น test-report/logs/<TC>-<browser>.log
 */
export class ApiLog {
  private lines: string[] = [];
  constructor(private testInfo: TestInfo) {}
  get size() {
    return this.lines.length;
  }
  async record(method: string, url: string, res: APIResponse, extra = '') {
    const body = await res.text();
    this.lines.push(`${new Date().toISOString()}  ${method} ${url}${extra ? `  [${extra}]` : ''}\n  → HTTP ${res.status()}\n  ${body}\n`);
    return body;
  }
  /** ส่ง request แล้วบันทึกทันที คืน { status, body(JSON) } */
  async call(request: APIRequestContext, method: 'GET' | 'POST', url: string, data?: unknown, extra = '') {
    const res = method === 'GET' ? await request.get(url) : await request.post(url, { data: data ?? {} });
    const text = await this.record(method, `${url}${data ? ` ${JSON.stringify(data)}` : ''}`, res, extra);
    let body: any = null;
    try { body = JSON.parse(text); } catch { /* not JSON */ }
    return { status: res.status(), body };
  }
  async save() {
    await this.testInfo.attach('api-log', { body: this.lines.join('\n'), contentType: 'text/plain' });
  }
}
