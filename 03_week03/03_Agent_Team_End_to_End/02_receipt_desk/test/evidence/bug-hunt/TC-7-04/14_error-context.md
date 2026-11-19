# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 57-roles.spec.ts >> 5.7 สิทธิ์ของแต่ละบทบาท >> TC-7-04 ไฟล์สรุปตามบทบาท
- Location: tests\57-roles.spec.ts:325:3

# Error details

```
Error: U01 report-total 1,340.00

expect(locator).toContainText(expected) failed

Locator: getByTestId('report-total')
Expected pattern: /1,?340\.00/
Received string:  "1139.50"
Timeout: 15000ms

Call log:
  - U01 report-total 1,340.00 getByTestId('report-total') with timeout 15000ms
  - waiting for getByTestId('report-total')
    33 × locator resolved to <span data-testid="report-total">1139.50</span>
       - unexpected value "1139.50"

```

```yaml
- text: "1139.50"
```

```
Error: U01 CSV ยอดรวม 1,340.00

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

```
Error: U03 report-total 1,340.00

expect(locator).toContainText(expected) failed

Locator: getByTestId('report-total')
Expected pattern: /1,?340\.00/
Received string:  "1139.50"
Timeout: 15000ms

Call log:
  - U03 report-total 1,340.00 getByTestId('report-total') with timeout 15000ms
  - waiting for getByTestId('report-total')
    33 × locator resolved to <span data-testid="report-total">1139.50</span>
       - unexpected value "1139.50"

```

```yaml
- text: "1139.50"
```

```
Error: U03 CSV ยอดรวม 1,340.00

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

# Test source

```ts
  255 |           expect.soft(me.user?.clientName, '② U-06 ผูก CL-02 (clientName)').toBe('ร้านกาแฟมะลิ');
  256 |         } else {
  257 |           expect.soft(me.user?.clientId ?? null, `② ${user} ไม่ผูกร้าน`).toBeNull();
  258 |         }
  259 |         await shot(testInfo, page, `② ${user} logged in`);
  260 |       } finally { await context.close(); }
  261 |     }
  262 |     await evidence(testInfo, '② roles', roleRows);
  263 | 
  264 |     // ③ new empty session, wrong password for U-01, then W5
  265 |     const ctx3 = await browser.newContext({ baseURL: M_URL, locale: 'th-TH', timezoneId: 'Asia/Bangkok' });
  266 |     try {
  267 |       const page = await ctx3.newPage();
  268 |       await page.goto('/login');
  269 |       await page.getByTestId('login-email-input').fill(U.U01);
  270 |       await page.getByTestId('login-password-input').fill(PASSWORD + '-wrong');
  271 |       await page.getByTestId('login-submit-button').click();
  272 |       await expect.soft(page.getByTestId('login-error'), '③ login-error แสดง').toBeVisible();
  273 |       await shot(testInfo, page, '③ wrong password');
  274 |       const me = await ctx3.request.get('/api/me');
  275 |       const body = await me.json().catch(() => ({}));
  276 |       await evidence(testInfo, '③ W5 after wrong password', { status: me.status(), body, url: page.url() });
  277 |       expect.soft(me.status(), '③ W5 ได้ 401').toBe(401);
  278 |     } finally { await ctx3.close(); }
  279 |     await office.dispose();
  280 |   });
  281 | 
  282 |   test('TC-7-03 แก้ ยืนยัน เปิดกลับ ตามบทบาท', { tag: ['@P1', '@A'] }, async ({}, testInfo) => {
  283 |     await reset(M_URL);
  284 |     const lead = await session('U03', testInfo);
  285 |     const owner = await session('U04', testInfo);
  286 |     const client = await session('U05', testInfo);
  287 |     try {
  288 |       const s = await seeded(lead);
  289 |       const s06 = s['S-06'].id; const s02 = s['S-02'].id;
  290 |       const cat = await categoryId(lead, 'CAT-04');
  291 |       const hist = async (id: string) => (await (await lead.get(`/api/receipts/${id}/history`)).json());
  292 |       const h06a = await hist(s06); const h02a = await hist(s02);
  293 | 
  294 |       const rows: any[] = [];
  295 |       const reqs: [string, APIRequestContext, 'POST' | 'PATCH', string, unknown][] = [
  296 |         ['U-04', owner, 'PATCH', `/api/receipts/${s06}`, { total: '600.00' }],
  297 |         ['U-04', owner, 'POST', `/api/receipts/${s06}/confirm`, { totalChecked: true, categoryId: cat }],
  298 |         ['U-05', client, 'PATCH', `/api/receipts/${s06}`, { total: '600.00' }],
  299 |         ['U-05', client, 'POST', `/api/receipts/${s06}/confirm`, { totalChecked: true, categoryId: cat }],
  300 |         ['U-04', owner, 'POST', `/api/receipts/${s02}/reopen`, undefined],
  301 |       ];
  302 |       for (const [who, ctx, m, url, data] of reqs) {
  303 |         const r = await call(ctx, m, url, data);
  304 |         rows.push({ who, request: `${m} ${url.replace(s06, '{S-06}').replace(s02, '{S-02}')}`, status: r.status, error: r.json?.error });
  305 |         expect.soft(r.status >= 400 && r.status < 500, `${who} ${m} ${url.replace(s06, 'S-06').replace(s02, 'S-02')} ถูกปฏิเสธ (got ${r.status})`).toBe(true);
  306 |       }
  307 |       await evidence(testInfo, 'requests -> status', rows);
  308 | 
  309 |       const r06 = (await (await lead.get(`/api/receipts/${s06}`)).json()).receipt;
  310 |       const r02 = (await (await lead.get(`/api/receipts/${s02}`)).json()).receipt;
  311 |       const h06b = await hist(s06); const h02b = await hist(s02);
  312 |       await evidence(testInfo, 'after', { S06: r06, S02: r02, h06a, h06b, h02a, h02b });
  313 |       expect.soft(r06?.status, 'S-06 ยังเป็นรอตรวจ').toBe('review');
  314 |       expect.soft(satang(r06?.total), 'S-06 ยอด 500.00 ไม่เปลี่ยน').toBe(50000);
  315 |       expect.soft(r02?.status, 'S-02 ยังยืนยันแล้ว').toBe('confirmed');
  316 |       expect.soft((h06b.edits ?? []).length, 'S-06 ประวัติการแก้ไม่มีแถวใหม่').toBe((h06a.edits ?? []).length);
  317 |       expect.soft((h06b.events ?? []).length, 'S-06 ประวัติเหตุการณ์ไม่มีแถวใหม่').toBe((h06a.events ?? []).length);
  318 |       expect.soft((h02b.edits ?? []).length, 'S-02 ประวัติการแก้ไม่มีแถวใหม่').toBe((h02a.edits ?? []).length);
  319 |       expect.soft((h02b.events ?? []).length, 'S-02 ประวัติเหตุการณ์ไม่มีแถวใหม่').toBe((h02a.events ?? []).length);
  320 |     } finally {
  321 |       for (const c of [lead, owner, client]) await c.dispose();
  322 |     }
  323 |   });
  324 | 
  325 |   test('TC-7-04 ไฟล์สรุปตามบทบาท', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  326 |     await reset(M_URL);
  327 |     const owner = await session('U04', testInfo);
  328 |     const client = await session('U05', testInfo);
  329 |     const cl01 = await clientId(owner, 'CL-01');
  330 |     const cl02 = await clientId(owner, 'CL-02');
  331 |     try {
  332 |       // reference of U-04 (TC-6-01: 1,340.00)
  333 |       const ref = await call(owner, 'GET', `/api/reports/monthly?clientId=${cl01}&month=2026-11`);
  334 |       const refT = csvTotal(ref.text);
  335 |       await evidence(testInfo, 'U-04 W18 CL-01 2026-11 (reference)', ref.text);
  336 | 
  337 |       for (const user of ['U01', 'U03'] as UserKey[]) {
  338 |         await (await session(user, testInfo)).dispose();
  339 |         const { context, page } = await pageAs(browser, M_URL, user);
  340 |         try {
  341 |           await page.goto('/reports');
  342 |           await pickOption(page, 'report-client-select', cl01, ['CL-01', 'ร้านข้าวแกงสมชาย']);
  343 |           await page.getByTestId('report-month-input').fill('2026-11');
  344 |           await page.getByTestId('report-preview-button').click();
  345 |           await page.getByTestId('report-total').waitFor({ state: 'visible' });
  346 |           await expect.soft(page.getByTestId('report-total'), `${user} report-total 1,340.00`).toContainText(/1,?340\.00/);
  347 |           const shown = await page.getByTestId('report-total').innerText();
  348 |           await shot(testInfo, page, `${user} /reports CL-01 2026-11`);
  349 |           const [dl] = await Promise.all([page.waitForEvent('download'), page.getByTestId('report-export-button').click()]);
  350 |           const fp = await dl.path();
  351 |           const text = fp ? fs.readFileSync(fp, 'utf8') : '';
  352 |           const t = csvTotal(text);
  353 |           await evidence(testInfo, `${user} CSV CL-01 2026-11 (${dl.suggestedFilename()})`, text);
  354 |           await evidence(testInfo, `${user} totals`, { shown, csvSumSatang: t.sum, rows: t.rows, refSumSatang: refT.sum });
> 355 |           expect.soft(t.sum, `${user} CSV ยอดรวม 1,340.00`).toBe(134000);
      |                                                             ^ Error: U03 CSV ยอดรวม 1,340.00
  356 |           expect.soft(t.sum, `${user} CSV ยอดเท่ากับของ U-04`).toBe(refT.sum);
  357 |         } finally { await context.close(); }
  358 |       }
  359 | 
  360 |       // U-05 W18 for CL-02
  361 |       const rows: any[] = [];
  362 |       for (const q of [`clientId=${cl02}&month=2026-11`, `clientId=CL-02&month=2026-11`]) {
  363 |         const r = await call(client, 'GET', `/api/reports/monthly?${q}`);
  364 |         rows.push({ request: `GET /api/reports/monthly?${q.replace(cl02, '{CL-02 uuid}')}`, status: r.status, contentType: r.contentType, body: r.text.slice(0, 500) });
  365 |         expect.soft(r.status >= 400 && r.status < 500, `U-05 W18 ${q.replace(cl02, 'CL-02')} ถูกปฏิเสธ (got ${r.status})`).toBe(true);
  366 |         expect.soft(r.text, `U-05 W18 ${q.replace(cl02, 'CL-02')} ไม่มีตัวเลข 999.00`).not.toMatch(/999(\.00)?/);
  367 |       }
  368 |       await evidence(testInfo, 'U-05 W18 requests -> status', rows);
  369 |     } finally {
  370 |       await owner.dispose(); await client.dispose();
  371 |     }
  372 |   });
  373 | });
  374 | 
```