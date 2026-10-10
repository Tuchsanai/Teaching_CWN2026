# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: book.spec.ts >> TC-BOOK-07 จองคู่ Couple Suite: จำนวนคน + ห้องเต็ม
- Location: tests\fixtures.ts:169:3

# Error details

```
Test timeout of 240000ms exceeded.
```

```
Error: locator.click: Target page, context or browser has been closed
Call log:
  - waiting for getByTestId('book-slot-20:30')

```

# Test source

```ts
  133 |       adminBookings: async (date) => {
  134 |         owner ??= await as('owner');
  135 |         const r = await owner.get(`/api/admin/bookings?date=${date}`);
  136 |         expect(r.status, 'owner อ่านตารางคิว').toBe(200);
  137 |         return r.json.bookings as any[];
  138 |       },
  139 |     };
  140 |     await use(f);
  141 |     for (const c of ctxs) await c.dispose();
  142 |     if (log.length) {
  143 |       const dir = join(REPORT_DIR, 'logs'); mkdirSync(dir, { recursive: true });
  144 |       const id = tcId(info);
  145 |       const file = join(dir, `${id}${info.project.name === 'api' ? '' : '.' + info.project.name}.log`);
  146 |       writeFileSync(file, `# ${info.title}\n# project: ${info.project.name} · status: ${info.status}\n\n${log.join('\n')}\n`);
  147 |       await info.attach('api-log', { path: file, contentType: 'text/plain' });
  148 |     }
  149 |   },
  150 | 
  151 |   page: async ({ page }, use, info) => {
  152 |     if (GIF) await page.addInitScript(overlayScript(`${info.title} · ${info.project.name}`));
  153 |     trackPrice(page);
  154 |     await use(page);
  155 |     const video = page.video();
  156 |     if (GIF && video && info.project.name === 'chromium') {
  157 |       await page.close();
  158 |       const webm = await video.path();
  159 |       if (existsSync(webm)) convertVideo(webm, tcId(info));
  160 |     }
  161 |   },
  162 | });
  163 | export { expect };
  164 | 
  165 | /** ประกาศ test ตามรหัส TC: ชื่อขึ้นต้นด้วยรหัส · tag โมดูล + ระดับ · annotation ผลที่คาดหวัง/ที่มา */
  166 | export function tc(id: string, body: Parameters<typeof test>[2]) {
  167 |   const c = CASES[id];
  168 |   if (!c) throw new Error(`ไม่มี ${id} ในแผน`);
  169 |   test(`${id} ${c.what}`, {
  170 |     tag: [`@${c.moduleCode}`, `@${c.priority}`],
  171 |     annotation: [
  172 |       { type: 'ผลที่คาดหวัง', description: c.expected },
  173 |       { type: 'ที่มา', description: c.source },
  174 |       { type: 'ข้อมูล', description: c.data },
  175 |     ],
  176 |   }, body);
  177 | }
  178 | 
  179 | // ---------- ตัวช่วยหน้าเว็บ ----------
  180 | export async function open(page: Page, path: string) {
  181 |   await page.goto(path);
  182 |   await page.locator('html[data-ready="true"]').waitFor({ timeout: 15_000 });
  183 | }
  184 | 
  185 | export async function loginUI(page: Page, u: UserKey) {
  186 |   await open(page, '/login');
  187 |   await page.getByTestId('login-email').fill(USERS[u].email);
  188 |   await page.getByTestId('login-password').fill(USERS[u].password);
  189 |   await page.getByTestId('login-submit').click();
  190 |   await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 15_000 });
  191 |   await page.locator('html[data-ready="true"]').waitFor();
  192 | }
  193 | 
  194 | export async function logoutUI(page: Page) {
  195 |   await page.request.post('/api/auth/logout');
  196 |   await page.context().clearCookies({ name: 'sabai_session' });
  197 | }
  198 | 
  199 | /** เงินจาก data-amount (บาท) */
  200 | export async function amount(page: Page, testId: string) {
  201 |   const v = await page.getByTestId(testId).getAttribute('data-amount');
  202 |   return v === null ? NaN : Number(v);
  203 | }
  204 | 
  205 | export type BookOpts = {
  206 |   type?: 'single' | 'couple' | 'group' | 'package' | 'course';
  207 |   service?: string; people?: number; date: string; time: string; therapist?: string;
  208 | };
  209 | 
  210 | /** ขั้น 1 → 2 (เลือกแบบ บริการ จำนวนคน แล้วกดถัดไป) */
  211 | export async function bookStep1(page: Page, o: Omit<BookOpts, 'date' | 'time'>) {
  212 |   const q = new URLSearchParams();
  213 |   if (o.service) q.set('service', o.service);
  214 |   if (o.type) q.set('type', o.type);
  215 |   if (o.people) q.set('people', String(o.people));
  216 |   await open(page, `/book?${q}`);
  217 |   if (o.type) await page.getByTestId(`book-type-label-${o.type}`).click();
  218 |   if (o.service && o.type !== 'package' && o.type !== 'course') {
  219 |     const sel = page.getByTestId('book-service');
  220 |     if (await sel.isVisible()) await sel.selectOption(o.service);
  221 |   }
  222 |   if (o.people) {
  223 |     const ppl = page.getByTestId('book-people');
  224 |     if (await ppl.isVisible() && await ppl.isEditable()) await ppl.fill(String(o.people));
  225 |   }
  226 |   await page.getByTestId('book-next-1').click();
  227 | }
  228 | 
  229 | /** ขั้น 2 → 3 (วัน รอบ นักบำบัด แล้วกดถัดไป) */
  230 | export async function bookStep2(page: Page, o: BookOpts) {
  231 |   await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '2');
  232 |   await page.getByTestId('book-date').fill(o.date);
> 233 |   await page.getByTestId(`book-slot-${o.time}`).click();
      |                                                 ^ Error: locator.click: Target page, context or browser has been closed
  234 |   if (o.therapist) await page.getByTestId('book-therapist').selectOption(o.therapist);
  235 |   await page.getByTestId('book-next-2').click();
  236 |   await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
  237 | }
  238 | 
  239 | /** เปิด /book แล้วเดินถึงขั้น 3 */
  240 | export async function bookToStep3(page: Page, o: BookOpts) {
  241 |   await bookStep1(page, o);
  242 |   await bookStep2(page, o);
  243 | }
  244 | 
  245 | export async function fillContact(page: Page, name: string, phone: string) {
  246 |   await page.getByTestId('book-contact-name').fill(name);
  247 |   await page.getByTestId('book-contact-phone').fill(phone);
  248 | }
  249 | 
  250 | // นับคำขอ /api/price ที่ยังไม่ตอบ — ใช้รอให้ราคาบนหน้าจออัปเดตหลังติ๊ก/เลือกตัวเลือก
  251 | const pending = new WeakMap<Page, number>();
  252 | export function trackPrice(page: Page) {
  253 |   pending.set(page, 0);
  254 |   const isPrice = (u: string) => u.includes('/api/price');
  255 |   page.on('request', (r) => { if (isPrice(r.url())) pending.set(page, (pending.get(page) ?? 0) + 1); });
  256 |   const done = (r: { url(): string }) => { if (isPrice(r.url())) pending.set(page, Math.max(0, (pending.get(page) ?? 1) - 1)); };
  257 |   page.on('requestfinished', done); page.on('requestfailed', done);
  258 | }
  259 | 
  260 | /** รอจนไม่มี /api/price ค้าง และตัวเลขบนจอไม่เปลี่ยน 2 รอบติด (ไม่ได้รอ "ค่าที่อยากได้" — แค่รอให้หน้าเว็บคิดเสร็จ) */
  261 | export async function settle(page: Page, read?: () => Promise<unknown>) {
  262 |   await page.waitForTimeout(250);
  263 |   let prev = read ? await read() : undefined; let stable = 0;
  264 |   for (let i = 0; i < 40 && stable < 2; i++) {
  265 |     await page.waitForTimeout(200);
  266 |     const cur = read ? await read() : undefined;
  267 |     stable = (pending.get(page) ?? 0) === 0 && cur === prev ? stable + 1 : 0;
  268 |     prev = cur;
  269 |   }
  270 | }
  271 | 
  272 | /** ยอดสุทธิขั้น 3 (ราคามาจาก /api/price) เป็นตัวเลขบาท */
  273 | export async function quoteTotal(page: Page) {
  274 |   const el = page.getByTestId('book-quote-total');
  275 |   await expect(el).toBeVisible();
  276 |   const read = async () => {
  277 |     const m = (await el.innerText()).replace(/,/g, '').match(/฿\s*([\d.]+)/);
  278 |     return m ? Number(m[1]) : NaN;
  279 |   };
  280 |   await settle(page, read);
  281 |   return read();
  282 | }
  283 | 
  284 | export async function toSummary(page: Page) {
  285 |   await settle(page);
  286 |   await page.getByTestId('book-next-3').click();
  287 |   await expect(page.getByTestId('book-summary')).toBeVisible();
  288 | }
  289 | 
```