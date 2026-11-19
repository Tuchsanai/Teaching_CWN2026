# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 56-reports.spec.ts >> 5.6 รายงานรายเดือน >> TC-6-04 ใบที่ยืนยันใหม่เข้าเดือนตามวันที่บนใบ · พ.ย. 1,440.00 ธ.ค. 175.25
- Location: tests\56-reports.spec.ts:197:3

# Error details

```
Error: CL-01 2026-11 after: report-total (1239.50)

expect(received).toBe(expected) // Object.is equality

Expected: 144000
Received: 123950
```

```
Error: CL-01 2026-11 after: report-receipt-count (4)

expect(received).toBe(expected) // Object.is equality

Expected: 5
Received: 4
```

```
Error: CL-01 2026-11 after: ผลรวมคอลัมน์ total ใน CSV (สตางค์)

expect(received).toBe(expected) // Object.is equality

Expected: 144000
Received: 123950
```

```
Error: CL-01 2026-11 after: จำนวนแถวใน CSV

expect(received).toBe(expected) // Object.is equality

Expected: 5
Received: 4
```

```
Error: CL-01 2026-12 after: report-total (0.00)

expect(received).toBe(expected) // Object.is equality

Expected: 17525
Received: 0
```

```
Error: CL-01 2026-12 after: report-receipt-count (0)

expect(received).toBe(expected) // Object.is equality

Expected: 2
Received: 0
```

```
Error: CL-01 2026-12 after: ผลรวมคอลัมน์ total ใน CSV (สตางค์)

expect(received).toBe(expected) // Object.is equality

Expected: 17525
Received: 0
```

```
Error: CL-01 2026-12 after: จำนวนแถวใน CSV

expect(received).toBe(expected) // Object.is equality

Expected: 2
Received: 0
```

```
Error: ธ.ค. = S-05 + ใบสอง

expect(received).toEqual(expected) // deep equality

- Expected  - 4
+ Received  + 1

- Array [
-   "S-05.jpg",
-   "ok-100__002.jpg",
- ]
+ Array []
```

# Page snapshot

```yaml
- generic [ref=f2e1]:
  - banner [ref=f2e2]:
    - link "ReceiptDesk" [ref=f2e3] [cursor=pointer]:
      - /url: /
    - navigation [ref=f2e5]:
      - link "ชุดใบเสร็จ" [ref=f2e6] [cursor=pointer]:
        - /url: /batches
      - link "รายการใบ" [ref=f2e7] [cursor=pointer]:
        - /url: /receipts
      - link "อ่านไม่ได้" [ref=f2e8] [cursor=pointer]:
        - /url: /unreadable
      - link "ค้างเกินกำหนด" [ref=f2e9] [cursor=pointer]:
        - /url: /overdue
      - link "สรุปรายเดือน" [ref=f2e10] [cursor=pointer]:
        - /url: /reports
      - link "เวลาตรวจ · GPU" [ref=f2e11] [cursor=pointer]:
        - /url: /insights
    - generic [ref=f2e12]:
      - generic [ref=f2e13]: คุณอรทัย
      - generic [ref=f2e14]: เจ้าของสำนักงาน
      - button "ออกจากระบบ" [ref=f2e15] [cursor=pointer]
  - main [ref=f2e16]:
    - heading "ไฟล์สรุปรายเดือน" [level=1] [ref=f2e17]
    - paragraph [ref=f2e18]: นับเฉพาะใบที่ยืนยันแล้ว และนับเดือนตามวันที่บนใบเสร็จ (ไม่ใช่วันที่อัปโหลด) · ไฟล์ CSV เข้ารหัส UTF-8 เปิดใน Excel ได้
    - generic [ref=f2e19]:
      - generic [ref=f2e20]:
        - text: ลูกค้า
        - combobox "ลูกค้า" [ref=f2e21]:
          - option "— เลือกลูกค้า —"
          - option "CL-01 · ร้านข้าวแกงสมชาย" [selected]
          - option "CL-02 · ร้านกาแฟมะลิ"
          - option "CL-03 · ร้านวัสดุทวีทรัพย์"
      - generic [ref=f2e22]:
        - text: เดือน
        - textbox "เดือน" [ref=f2e23]: 2026-12
      - button "ดูตัวอย่าง" [ref=f2e24] [cursor=pointer]
      - link "ออกไฟล์ CSV" [active] [ref=f2e25] [cursor=pointer]:
        - /url: /api/reports/monthly?clientId=a1b0be0b-79b1-4158-8d04-e30a246d9af3&month=2026-12
    - generic [ref=f2e26]:
      - generic [ref=f2e27]:
        - generic [ref=f2e28]:
          - generic [ref=f2e29]: ยอดรวมของเดือน 2026-12
          - generic [ref=f2e30]: 0.00 บาท
        - generic [ref=f2e31]:
          - generic [ref=f2e32]: จำนวนใบที่ยืนยันแล้ว
          - generic [ref=f2e33]: "0"
      - paragraph [ref=f2e34]: เดือนนี้ไม่มีใบที่ยืนยันแล้ว ไฟล์ CSV จะมีเฉพาะหัวตาราง
  - alert [ref=f2e35]
```

# Test source

```ts
  132 |     await reset(M_URL);
  133 |     const office = await apiAs(M_URL, 'U04');
  134 |     const cl01 = await clientId(office, 'CL-01');
  135 |     const { context, page } = await ownerReports(browser);
  136 |     try {
  137 |       const r = await runReport(page, testInfo, cl01, '2026-11', 'CL-01 2026-11');
  138 |       expectReport(r, 'CL-01 2026-11', 134000, 4);
  139 |       if (r.csv) {
  140 |         const files = csvFiles(r.csv);
  141 |         expect.soft(files, 'CSV = S-02, S-03, S-04, S-07').toEqual([S('S-02'), S('S-03'), S('S-04'), S('S-07')].sort());
  142 |         expect.soft(files, 'ไม่มี S-06 (500.00 ยังไม่ยืนยัน)').not.toContain(S('S-06'));
  143 |         expect.soft(files, 'มี S-07 (วันที่บนใบ 2026-11-10 แม้อัปโหลด 2026-12-02)').toContain(S('S-07'));
  144 |       }
  145 |     } finally { await context.close(); await office.dispose(); }
  146 |   });
  147 | 
  148 |   test('TC-6-02 ใบที่ขอบเดือน ต.ค. / ธ.ค. · 150.00 และ 75.25', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  149 |     await reset(M_URL);
  150 |     const office = await apiAs(M_URL, 'U04');
  151 |     const cl01 = await clientId(office, 'CL-01');
  152 |     const { context, page } = await ownerReports(browser);
  153 |     try {
  154 |       const oct = await runReport(page, testInfo, cl01, '2026-10', 'CL-01 2026-10');
  155 |       expectReport(oct, 'CL-01 2026-10', 15000, 1);
  156 |       if (oct.csv) expect.soft(csvFiles(oct.csv), 'ต.ค. = S-01 (2026-10-31)').toEqual([S('S-01')]);
  157 | 
  158 |       const dec = await runReport(page, testInfo, cl01, '2026-12', 'CL-01 2026-12');
  159 |       expectReport(dec, 'CL-01 2026-12', 7525, 1);
  160 |       if (dec.csv) expect.soft(csvFiles(dec.csv), 'ธ.ค. = S-05 (2026-12-01)').toEqual([S('S-05')]);
  161 | 
  162 |       const nov = await runReport(page, testInfo, cl01, '2026-11', 'CL-01 2026-11');
  163 |       if (nov.csv) expect.soft(csvFiles(nov.csv), 'S-05 ไม่อยู่ใน พ.ย.').not.toContain(S('S-05'));
  164 |       if (nov.csv) expect.soft(csvFiles(nov.csv), 'S-01 ไม่อยู่ใน พ.ย.').not.toContain(S('S-01'));
  165 |     } finally { await context.close(); await office.dispose(); }
  166 |   });
  167 | 
  168 |   test('TC-6-03 ร้านอื่น และร้านที่ไม่มีใบ · CL-02 999.00 · CL-03 0.00', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  169 |     await reset(M_URL);
  170 |     const office = await apiAs(M_URL, 'U04');
  171 |     const cl02 = await clientId(office, 'CL-02');
  172 |     const cl03 = await clientId(office, 'CL-03');
  173 |     const { context, page } = await ownerReports(browser);
  174 |     try {
  175 |       const r2 = await runReport(page, testInfo, cl02, '2026-11', 'CL-02 2026-11');
  176 |       expectReport(r2, 'CL-02 2026-11', 99900, 1);
  177 |       if (r2.csv) {
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
> 232 |       if (dec.csv) expect.soft(csvFiles(dec.csv), 'ธ.ค. = S-05 + ใบสอง').toEqual([S('S-05'), 'ok-100__002.jpg'].sort());
      |                                                                          ^ Error: ธ.ค. = S-05 + ใบสอง
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
  278 |       expect.soft(portalSum, 'หน้าลูกค้า รวมทุกหมวด = 1,340.00').toBe(134000);
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
```