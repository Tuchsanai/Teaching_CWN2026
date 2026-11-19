# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 56-reports.spec.ts >> 5.6 รายงานรายเดือน >> TC-6-05 ยอดแยกหมวด พ.ย. ของ CL-01 · หน้าลูกค้าและ W19 ตรงกัน
- Location: tests\56-reports.spec.ts:236:3

# Error details

```
Error: W19 CAT-01 วัตถุดิบ

expect(received).toBe(expected) // Object.is equality

Expected: 120050
Received: 100000
```

```
Error: W19 รวมทุกหมวด = 1,340.00 (= TC-6-01)

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

```
Error: W19 total = 1,340.00

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

```
Error: หน้าลูกค้า CAT-01 วัตถุดิบ

expect(received).toBe(expected) // Object.is equality

Expected: 120050
Received: 100000
```

```
Error: หน้าลูกค้า รวมทุกหมวด = 1,340.00

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

# Page snapshot

```yaml
- generic [ref=f2e1]:
  - banner [ref=f2e2]:
    - link "ReceiptDesk" [ref=f2e3] [cursor=pointer]:
      - /url: /
    - navigation [ref=f2e5]:
      - link "ใบเสร็จของร้าน" [ref=f2e6] [cursor=pointer]:
        - /url: /portal
    - generic [ref=f2e7]:
      - generic [ref=f2e8]: คุณสมชาย
      - generic [ref=f2e9]: ลูกค้า · ร้านข้าวแกงสมชาย
      - button "ออกจากระบบ" [ref=f2e10] [cursor=pointer]
  - main [ref=f2e11]:
    - heading "ใบเสร็จของ ร้านข้าวแกงสมชาย" [level=1] [ref=f2e12]
    - generic [ref=f2e13]:
      - heading "ส่งใบเสร็จ" [level=2] [ref=f2e14]
      - generic [ref=f2e15]:
        - generic [ref=f2e16]:
          - text: ไฟล์ (JPG · PNG · PDF 1 หน้า · ไม่เกิน 10 MB ต่อไฟล์ · 1–100 ไฟล์)
          - button "ไฟล์ (JPG · PNG · PDF 1 หน้า · ไม่เกิน 10 MB ต่อไฟล์ · 1–100 ไฟล์)" [ref=f2e17]
        - button "ส่งใบเสร็จ" [ref=f2e18] [cursor=pointer]
    - generic [ref=f2e19]:
      - heading "ใบเสร็จของร้าน" [level=2] [ref=f2e20]
      - table [ref=f2e21]:
        - rowgroup [ref=f2e22]:
          - row [ref=f2e23]:
            - columnheader "ไฟล์" [ref=f2e24]
            - columnheader "รับเมื่อ" [ref=f2e25]
            - columnheader "สถานะ" [ref=f2e26]
            - columnheader "ร้านบนใบ" [ref=f2e27]
            - columnheader "วันที่บนใบ" [ref=f2e28]
            - columnheader "หมวด" [ref=f2e29]
            - columnheader "ยอดรวม (บาท)" [ref=f2e30]
        - rowgroup [ref=f2e31]:
          - row [ref=f2e32]:
            - cell "S-07.jpg" [ref=f2e33]
            - cell "02/12/2569 11:00" [ref=f2e34]
            - cell "ยืนยันแล้ว" [ref=f2e35]
            - cell "ร้านตัวอย่าง" [ref=f2e36]
            - cell "2026-11-10" [ref=f2e37]
            - cell "ค่าแก๊ส" [ref=f2e38]
            - cell "40.00" [ref=f2e39]
          - row [ref=f2e40]:
            - cell "S-05.jpg" [ref=f2e41]
            - cell "01/12/2569 08:00" [ref=f2e42]
            - cell "ยืนยันแล้ว" [ref=f2e43]
            - cell "ร้านตัวอย่าง" [ref=f2e44]
            - cell "2026-12-01" [ref=f2e45]
            - cell "ค่าแก๊ส" [ref=f2e46]
            - cell "75.25" [ref=f2e47]
          - row [ref=f2e48]:
            - cell "S-04.jpg" [ref=f2e49]
            - cell "30/11/2569 23:50" [ref=f2e50]
            - cell "ยืนยันแล้ว" [ref=f2e51]
            - cell "ร้านตัวอย่าง" [ref=f2e52]
            - cell "2026-11-30" [ref=f2e53]
            - cell "วัตถุดิบ" [ref=f2e54]
            - cell "1000.00" [ref=f2e55]
          - row [ref=f2e56]:
            - cell "S-06.jpg" [ref=f2e57]
            - cell "15/11/2569 10:00" [ref=f2e58]
            - cell "รับแล้ว รอสำนักงานตรวจ" [ref=f2e59]
            - cell "แสดงตัวเลขเมื่อสำนักงานยืนยันแล้ว" [ref=f2e60]
          - row [ref=f2e61]:
            - cell "S-03.jpg" [ref=f2e62]
            - cell "02/11/2569 09:00" [ref=f2e63]
            - cell "ยืนยันแล้ว" [ref=f2e64]
            - cell "ร้านตัวอย่าง" [ref=f2e65]
            - cell "2026-11-02" [ref=f2e66]
            - cell "ค่าน้ำแข็ง" [ref=f2e67]
            - cell "99.50" [ref=f2e68]
          - row [ref=f2e69]:
            - cell "S-02.jpg" [ref=f2e70]
            - cell "01/11/2569 00:30" [ref=f2e71]
            - cell "ยืนยันแล้ว" [ref=f2e72]
            - cell "ร้านตัวอย่าง" [ref=f2e73]
            - cell "2026-11-01" [ref=f2e74]
            - cell "วัตถุดิบ" [ref=f2e75]
            - cell "200.50" [ref=f2e76]
          - row [ref=f2e77]:
            - cell "S-01.jpg" [ref=f2e78]
            - cell "31/10/2569 18:00" [ref=f2e79]
            - cell "ยืนยันแล้ว" [ref=f2e80]
            - cell "ร้านตัวอย่าง" [ref=f2e81]
            - cell "2026-10-31" [ref=f2e82]
            - cell "วัตถุดิบ" [ref=f2e83]
            - cell "150.00" [ref=f2e84]
    - generic [ref=f2e85]:
      - heading "รายจ่ายแยกหมวด (เฉพาะใบที่ยืนยันแล้ว · ตามวันที่บนใบ)" [level=2] [ref=f2e86]
      - generic [ref=f2e87]:
        - text: เดือน
        - textbox "เดือน" [active] [ref=f2e88]: 2026-11
      - paragraph [ref=f2e89]:
        - text: ยอดรวมทั้งเดือน
        - strong [ref=f2e90]: "1139.50"
        - text: บาท · 3 ใบ
      - table [ref=f2e91]:
        - rowgroup [ref=f2e92]:
          - row [ref=f2e93]:
            - columnheader "หมวด" [ref=f2e94]
            - columnheader "ใบ" [ref=f2e95]
            - columnheader "ยอด (บาท)" [ref=f2e96]
        - rowgroup [ref=f2e97]:
          - row [ref=f2e98]:
            - cell "วัตถุดิบ" [ref=f2e99]
            - cell "1" [ref=f2e100]
            - cell "1000.00" [ref=f2e101]
          - row [ref=f2e102]:
            - cell "ค่าแก๊ส" [ref=f2e103]
            - cell "1" [ref=f2e104]
            - cell "40.00" [ref=f2e105]
          - row [ref=f2e106]:
            - cell "ค่าน้ำแข็ง" [ref=f2e107]
            - cell "1" [ref=f2e108]
            - cell "99.50" [ref=f2e109]
          - row [ref=f2e110]:
            - cell "อื่น ๆ" [ref=f2e111]
            - cell "0" [ref=f2e112]
            - cell "0.00" [ref=f2e113]
  - alert [ref=f2e114]
```

# Test source

```ts
  178 |         expect.soft(csvFiles(r2.csv), 'CL-02 = S-08').toEqual([S('S-08')]);
  179 |         expect.soft(csvFiles(r2.csv).filter(f => CL01_SEED.includes(f)), 'CL-02: ไม่มีใบของ CL-01 ปน').toEqual([]);
  180 |       }
  181 | 
  182 |       const r3 = await runReport(page, testInfo, cl03, '2026-11', 'CL-03 2026-11');
  183 |       expectReport(r3, 'CL-03 2026-11', 0, 0);
  184 |       if (r3.csv) {
  185 |         expect.soft(r3.csv.header.length, 'CL-03: CSV มีหัวตาราง').toBeGreaterThan(0);
  186 |         expect.soft(r3.csv.rows.length, 'CL-03: CSV มีแต่หัวตาราง').toBe(0);
  187 |       }
  188 |       // the same file through W18 directly: must be 200 (not an error)
  189 |       const api = await office.get(`/api/reports/monthly?clientId=${cl03}&month=2026-11`);
  190 |       const body = await api.text();
  191 |       await evidence(testInfo, 'W18 CL-03 2026-11 (API)', { status: api.status(), body });
  192 |       expect.soft(api.status(), 'CL-03: W18 ตอบ 200 ไม่ error').toBe(200);
  193 |       expect.soft(parseCsv(body).rows.length, 'CL-03: W18 มีแต่หัวตาราง').toBe(0);
  194 |     } finally { await context.close(); await office.dispose(); }
  195 |   });
  196 | 
  197 |   test('TC-6-04 ใบที่ยืนยันใหม่เข้าเดือนตามวันที่บนใบ · พ.ย. 1,440.00 ธ.ค. 175.25', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  198 |     await reset(M_URL);
  199 |     const staff = await apiAs(M_URL, 'U01');
  200 |     const owner = await apiAs(M_URL, 'U04');
  201 |     const cl01 = await clientId(staff, 'CL-01');
  202 |     const cat01 = await categoryId(staff, 'CAT-01');
  203 |     const { context, page } = await ownerReports(browser);
  204 |     try {
  205 |       const up = await upload(staff, { clientId: cl01, files: okFiles(2) });
  206 |       await evidence(testInfo, 'W7 upload', up);
  207 |       expect(up.status, 'W7 upload 2 files').toBeLessThan(300);
  208 |       const rs = await waitBatchReview(staff, up.json.batchId, 2);
  209 |       const first = rs.find(r => r.fileName === 'ok-100__001.jpg');
  210 |       const second = rs.find(r => r.fileName === 'ok-100__002.jpg');
  211 |       expect(first && second, 'both receipts in the batch').toBeTruthy();
  212 |       // open each receipt's detail before confirming (FR-12)
  213 |       for (const r of [first, second]) await staff.get(`/api/receipts/${r.id}`);
  214 | 
  215 |       const c1 = await confirm(staff, first.id, { totalChecked: true, categoryId: cat01 });
  216 |       const p2 = await staff.patch(`/api/receipts/${second.id}`, { data: { receiptDate: '2026-12-01' } });
  217 |       const p2j = await p2.json().catch(() => ({}));
  218 |       const c2 = await confirm(staff, second.id, { totalChecked: true, categoryId: cat01 });
  219 |       await evidence(testInfo, 'W15/W14 results', { confirm1: c1, patch2: { status: p2.status(), json: p2j }, confirm2: c2 });
  220 |       expect(c1.status, 'ยืนยันใบแรก').toBe(200);
  221 |       expect(p2.status(), 'แก้วันที่ใบสองเป็น 2026-12-01').toBe(200);
  222 |       expect(c2.status, 'ยืนยันใบสอง').toBe(200);
  223 | 
  224 |       const nov = await runReport(page, testInfo, cl01, '2026-11', 'CL-01 2026-11 after');
  225 |       expectReport(nov, 'CL-01 2026-11 after', 144000, 5);
  226 |       if (nov.csv) {
  227 |         expect.soft(csvFiles(nov.csv), 'พ.ย. มีใบแรก ok-100__001').toContain('ok-100__001.jpg');
  228 |         expect.soft(csvFiles(nov.csv), 'พ.ย. ไม่มีใบสอง (วันที่ที่แก้แล้ว 2026-12-01 ไม่ใช่ 2026-11-18)').not.toContain('ok-100__002.jpg');
  229 |       }
  230 |       const dec = await runReport(page, testInfo, cl01, '2026-12', 'CL-01 2026-12 after');
  231 |       expectReport(dec, 'CL-01 2026-12 after', 17525, 2);
  232 |       if (dec.csv) expect.soft(csvFiles(dec.csv), 'ธ.ค. = S-05 + ใบสอง').toEqual([S('S-05'), 'ok-100__002.jpg'].sort());
  233 |     } finally { await context.close(); await staff.dispose(); await owner.dispose(); }
  234 |   });
  235 | 
  236 |   test('TC-6-05 ยอดแยกหมวด พ.ย. ของ CL-01 · หน้าลูกค้าและ W19 ตรงกัน', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  237 |     await reset(M_URL);
  238 |     const owner = await apiAs(M_URL, 'U04');
  239 |     const cl01 = await clientId(owner, 'CL-01');
  240 |     const expected: Record<string, number> = { 'CAT-01': 120050, 'CAT-02': 4000, 'CAT-03': 9950, 'CAT-04': 0 };
  241 |     const w19r = await owner.get(`/api/reports/categories?month=2026-11&clientId=${cl01}`);
  242 |     const w19 = await w19r.json().catch(() => ({}));
  243 |     await evidence(testInfo, 'W19 CL-01 2026-11 (U-04)', { status: w19r.status(), json: w19 });
  244 |     expect(w19r.status(), 'W19 status').toBe(200);
  245 |     const ids: Record<string, string> = {};
  246 |     for (const code of Object.keys(expected)) {
  247 |       const c = (w19.categories ?? []).find((x: any) => x.name === CATEGORY_NAME[code]);
  248 |       expect.soft(c, `W19 มีหมวด ${code} ${CATEGORY_NAME[code]}`).toBeTruthy();
  249 |       if (!c) continue;
  250 |       ids[code] = c.id;
  251 |       expect.soft(satang(c.total), `W19 ${code} ${CATEGORY_NAME[code]}`).toBe(expected[code]);
  252 |     }
  253 |     const w19Sum = (w19.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0);
  254 |     expect.soft(w19Sum, 'W19 รวมทุกหมวด = 1,340.00 (= TC-6-01)').toBe(134000);
  255 |     expect.soft(satang(w19.total), 'W19 total = 1,340.00').toBe(134000);
  256 | 
  257 |     const { context, page } = await pageAs(browser, M_URL, 'U05');
  258 |     try {
  259 |       await page.goto('/portal');
  260 |       const resp = page.waitForResponse(r => r.url().includes('/api/reports/categories'), { timeout: 10_000 }).catch(() => null);
  261 |       await page.getByTestId('portal-month-input').fill('2026-11');
  262 |       await page.getByTestId('portal-month-input').press('Enter').catch(() => undefined);
  263 |       await resp;
  264 |       await page.waitForTimeout(500);
  265 |       const portal: Record<string, string | null> = {};
  266 |       let portalSum = 0;
  267 |       for (const code of Object.keys(expected)) {
  268 |         const loc = ids[code] ? page.getByTestId(`portal-category-total-${ids[code]}`) : null;
  269 |         const visible = loc ? await loc.isVisible().catch(() => false) : false;
  270 |         portal[code] = visible ? (await loc!.innerText()).trim() : null;
  271 |         expect.soft(portal[code], `portal-category-total-{id} ของ ${code} แสดงบนหน้า`).not.toBeNull();
  272 |         if (portal[code] === null) continue;
  273 |         expect.soft(satang(portal[code]), `หน้าลูกค้า ${code} ${CATEGORY_NAME[code]}`).toBe(expected[code]);
  274 |         const apiCat = (w19.categories ?? []).find((x: any) => x.id === ids[code]);
  275 |         expect.soft(satang(portal[code]), `${code}: หน้าลูกค้า = W19`).toBe(satang(apiCat?.total));
  276 |         portalSum += satang(portal[code]);
  277 |       }
> 278 |       expect.soft(portalSum, 'หน้าลูกค้า รวมทุกหมวด = 1,340.00').toBe(134000);
      |                                                                  ^ Error: หน้าลูกค้า รวมทุกหมวด = 1,340.00
  279 |       await evidence(testInfo, 'portal category totals (U-05)', portal);
  280 |       await shot(testInfo, page, 'portal 2026-11 U-05');
  281 |     } finally { await context.close(); await owner.dispose(); }
  282 |   });
  283 | 
  284 |   test('TC-6-06 เวลาตรวจเฉลี่ยต่อชุด · (30 + 50) ÷ 2 = 40 วินาที', { tag: ['@P3', '@M'] }, async ({ browser }, testInfo) => {
  285 |     test.setTimeout(10 * 60_000);
  286 |     await reset(M_URL);
  287 |     const staff = await apiAs(M_URL, 'U01');
  288 |     const cl01 = await clientId(staff, 'CL-01');
  289 |     const cat04 = await categoryId(staff, 'CAT-04');
  290 |     const up = await upload(staff, { clientId: cl01, files: okFiles(2) });
  291 |     await evidence(testInfo, 'W7 upload', up);
  292 |     expect(up.status, 'W7 upload 2 files as one batch').toBeLessThan(300);
  293 |     const batchId: string = up.json.batchId;
  294 |     const rs = await waitBatchReview(staff, batchId, 2);
  295 |     const order = ['ok-100__001.jpg', 'ok-100__002.jpg'].map(n => rs.find(r => r.fileName === n));
  296 |     expect(order.every(Boolean), 'both receipts in the batch').toBeTruthy();
  297 | 
  298 |     const u01 = await pageAs(browser, M_URL, 'U01');
  299 |     const measured: { file: string; seconds: number; status: number | null }[] = [];
  300 |     try {
  301 |       for (const [i, holdS] of [[0, 30], [1, 50]] as const) {
  302 |         const r = order[i];
  303 |         const t0 = Date.now();
  304 |         await u01.page.goto(`/receipts/${r.id}`);
  305 |         await expect(u01.page.getByTestId('confirm-button')).toBeVisible();
  306 |         await u01.page.getByTestId('category-select').selectOption(cat04);
  307 |         await u01.page.getByTestId('total-checked-checkbox').check();
  308 |         const wait = t0 + holdS * 1000 - Date.now();
  309 |         if (wait > 0) await u01.page.waitForTimeout(wait);
  310 |         if (i === 1) await shot(testInfo, u01.page, 'receipt 2 before confirm (50 s)');
  311 |         const resp = u01.page.waitForResponse(x => x.url().includes(`/api/receipts/${r.id}/confirm`), { timeout: 20_000 }).catch(() => null);
  312 |         await u01.page.getByTestId('confirm-button').click();
  313 |         const res = await resp;
  314 |         measured.push({ file: r.fileName, seconds: (Date.now() - t0) / 1000, status: res ? res.status() : null });
  315 |         expect(res?.status(), `ยืนยัน ${r.fileName} ผ่านหน้าเว็บ`).toBe(200);
  316 |       }
  317 |       await evidence(testInfo, 'held times (open -> confirm click)', measured);
  318 | 
  319 |       // U-01 (staff) calls W21 -> rejected
  320 |       const w21Staff = await staff.get('/api/reports/review-time');
  321 |       await evidence(testInfo, 'W21 as U-01', { status: w21Staff.status(), body: await w21Staff.text() });
  322 |       expect.soft(w21Staff.status(), 'U-01 เรียก W21 ถูกปฏิเสธ (403)').toBe(403);
  323 | 
  324 |       // U-03 and U-04 see the same value on /insights; batch average = 40 s ± 3
  325 |       const seen: Record<string, { page: number; api: number; apiRow: any }> = {};
  326 |       for (const user of ['U03', 'U04'] as const) {
  327 |         const s = await pageAs(browser, M_URL, user);
  328 |         try {
  329 |           await s.page.goto('/insights');
  330 |           const table = s.page.getByTestId('review-time-table');
  331 |           await expect(table).toBeVisible();
  332 |           const row = table.locator('tbody tr', { hasText: 'ร้านข้าวแกงสมชาย' }).first();
  333 |           let pageVal = NaN;
  334 |           if (await row.isVisible().catch(() => false)) {
  335 |             const cells = await row.locator('td').allInnerTexts();
  336 |             pageVal = numOf(cells[3]); // ชุด | ลูกค้า | ใบที่ยืนยัน | เฉลี่ย (วินาที) | ...
  337 |             await evidence(testInfo, `${user} /insights batch row`, cells);
  338 |           }
  339 |           await shot(testInfo, s.page, `${user} /insights review time`);
  340 |           const w21 = await (await s.context.request.get('/api/reports/review-time')).json().catch(() => ({}));
  341 |           await evidence(testInfo, `W21 as ${user}`, w21);
  342 |           const apiRow = (w21.batches ?? []).find((b: any) => b.batchId === batchId || b.id === batchId);
  343 |           const apiVal = numOf(apiRow?.averageSeconds ?? apiRow?.avgSeconds ?? apiRow?.average);
  344 |           seen[user] = { page: pageVal, api: apiVal, apiRow };
  345 |           expect.soft(pageVal, `${user}: /insights แถวของชุดนี้ เฉลี่ย = 40 ± 3 วินาที`).toBeGreaterThanOrEqual(37);
  346 |           expect.soft(pageVal, `${user}: /insights แถวของชุดนี้ เฉลี่ย = 40 ± 3 วินาที`).toBeLessThanOrEqual(43);
  347 |           expect.soft(apiVal, `${user}: W21 batches[ชุดนี้] เฉลี่ย = 40 ± 3 วินาที`).toBeGreaterThanOrEqual(37);
  348 |           expect.soft(apiVal, `${user}: W21 batches[ชุดนี้] เฉลี่ย = 40 ± 3 วินาที`).toBeLessThanOrEqual(43);
  349 |         } finally { await s.context.close(); }
  350 |       }
  351 |       expect.soft(seen.U03?.page, 'U-03 และ U-04 เห็นค่าเดียวกันบน /insights').toBe(seen.U04?.page);
  352 |       expect.soft(seen.U03?.api, 'U-03 และ U-04 ได้ค่าเดียวกันจาก W21').toBe(seen.U04?.api);
  353 |     } finally { await u01.context.close(); await staff.dispose(); }
  354 |   });
  355 | 
  356 |   test('TC-6-07 รายงาน GPU 1 เทียบ 2 ใบ · ต้องมีตารางและสูตรถูก', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  357 |     await reset(M_URL);
  358 |     const step12 = { t1: 116.2, t2: 56.0 }; // results/capacity/summary.json mean_t_1worker_s / mean_t_2workers_s
  359 |     const step12Speedup = step12.t1 / step12.t2; // 2.075 -> shown 2.08 · efficiency 103.75% -> 104% -> คุ้ม
  360 |     const { context, page } = await pageAs(browser, M_URL, 'U04');
  361 |     try {
  362 |       await page.goto('/insights');
  363 |       const table = page.getByTestId('gpu-table');
  364 |       await expect.soft(table, 'gpu-table แสดง').toBeVisible();
  365 |       const w22 = await (await context.request.get('/api/reports/gpu')).json().catch(() => ({}));
  366 |       await evidence(testInfo, 'W22 as U-04', w22);
  367 | 
  368 |       const rows = await table.locator('tbody tr').evaluateAll(trs => trs.map(tr => [...tr.querySelectorAll('td,th')].map(td => (td as HTMLElement).innerText.trim())));
  369 |       const txt = async (id: string) => (await page.getByTestId(id).innerText().catch(() => '')).trim();
  370 |       const shown = { speedup: await txt('gpu-speedup'), efficiency: await txt('gpu-efficiency'), costPer100: await txt('gpu-cost-per-100'), verdict: await txt('gpu-verdict') };
  371 |       await evidence(testInfo, '/insights GPU table + cards', { rows, shown });
  372 |       await shot(testInfo, page, 'U-04 /insights GPU');
  373 | 
  374 |       // must have the table WITH values (empty / "ยังไม่มีข้อมูล" = fail FR-30)
  375 |       const row1 = rows.find(r => r[0] === '1');
  376 |       const row2 = rows.find(r => r[0] === '2');
  377 |       // columns: จำนวน GPU | ใบ | เวลา (นาที) | ใบต่อนาที | ค่าเช่า (บาท) | บาทต่อ 100 ใบ | วัดเมื่อ
  378 |       const hasValues = (r?: string[]) => !!r && r.length >= 6 && !Number.isNaN(numOf(r[1])) && !Number.isNaN(numOf(r[2])) && !Number.isNaN(numOf(r[3])) && !Number.isNaN(numOf(r[4])) && !Number.isNaN(numOf(r[5]));
```