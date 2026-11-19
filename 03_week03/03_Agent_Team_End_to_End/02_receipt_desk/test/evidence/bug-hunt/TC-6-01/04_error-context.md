# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 56-reports.spec.ts >> 5.6 รายงานรายเดือน >> TC-6-01 สรุป พ.ย. 2026 ของ CL-01 · 1,340.00 บาท 4 ใบ
- Location: tests\56-reports.spec.ts:131:3

# Error details

```
Error: CL-01 2026-11: report-total (1139.50)

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

```
Error: CL-01 2026-11: report-receipt-count (3)

expect(received).toBe(expected) // Object.is equality

Expected: 4
Received: 3
```

```
Error: CL-01 2026-11: ผลรวมคอลัมน์ total ใน CSV (สตางค์)

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

```
Error: CL-01 2026-11: จำนวนแถวใน CSV

expect(received).toBe(expected) // Object.is equality

Expected: 4
Received: 3
```

```
Error: CSV = S-02, S-03, S-04, S-07

expect(received).toEqual(expected) // deep equality

- Expected  - 1
+ Received  + 0

  Array [
-   "S-02.jpg",
    "S-03.jpg",
    "S-04.jpg",
    "S-07.jpg",
  ]
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
        - textbox "เดือน" [ref=f2e23]: 2026-11
      - button "ดูตัวอย่าง" [ref=f2e24] [cursor=pointer]
      - link "ออกไฟล์ CSV" [active] [ref=f2e25] [cursor=pointer]:
        - /url: /api/reports/monthly?clientId=8206f74b-2cf6-4ae5-9928-7c963c071161&month=2026-11
    - generic [ref=f2e26]:
      - generic [ref=f2e27]:
        - generic [ref=f2e28]:
          - generic [ref=f2e29]: ยอดรวมของเดือน 2026-11
          - generic [ref=f2e30]: 1139.50 บาท
        - generic [ref=f2e31]:
          - generic [ref=f2e32]: จำนวนใบที่ยืนยันแล้ว
          - generic [ref=f2e33]: "3"
      - table [ref=f2e34]:
        - rowgroup [ref=f2e35]:
          - row [ref=f2e36]:
            - columnheader "วันที่บนใบ" [ref=f2e37]
            - columnheader "ร้าน" [ref=f2e38]
            - columnheader "หมวด" [ref=f2e39]
            - columnheader "ยอดรวม" [ref=f2e40]
            - columnheader "ไฟล์" [ref=f2e41]
            - columnheader "ยืนยันโดย" [ref=f2e42]
        - rowgroup [ref=f2e43]:
          - row [ref=f2e44]:
            - cell "2026-11-02" [ref=f2e45]
            - cell "ร้านตัวอย่าง" [ref=f2e46]
            - cell "ค่าน้ำแข็ง" [ref=f2e47]
            - cell "99.50" [ref=f2e48]
            - cell "S-03.jpg" [ref=f2e49]
            - cell "คุณพิมพ์" [ref=f2e50]
          - row [ref=f2e51]:
            - cell "2026-11-10" [ref=f2e52]
            - cell "ร้านตัวอย่าง" [ref=f2e53]
            - cell "ค่าแก๊ส" [ref=f2e54]
            - cell "40.00" [ref=f2e55]
            - cell "S-07.jpg" [ref=f2e56]
            - cell "คุณพิมพ์" [ref=f2e57]
          - row [ref=f2e58]:
            - cell "2026-11-30" [ref=f2e59]
            - cell "ร้านตัวอย่าง" [ref=f2e60]
            - cell "วัตถุดิบ" [ref=f2e61]
            - cell "1000.00" [ref=f2e62]
            - cell "S-04.jpg" [ref=f2e63]
            - cell "คุณแนน" [ref=f2e64]
  - alert [ref=f2e65]
```

# Test source

```ts
  41  |       row.push(cell); cell = '';
  42  |       if (row.some(c => c !== '')) out.push(row);
  43  |       row = [];
  44  |     } else cell += ch;
  45  |   }
  46  |   row.push(cell); if (row.some(c => c !== '')) out.push(row);
  47  |   const header = (out.shift() ?? []).map(h => h.trim());
  48  |   const rows = out.map(r => Object.fromEntries(header.map((h, i) => [h, (r[i] ?? '').trim()])));
  49  |   return { text: raw, header, rows, bom };
  50  | }
  51  | function csvSum(csv: Csv): number { return csv.rows.reduce((a, r) => a + satang(r.total), 0); }
  52  | function csvFiles(csv: Csv): string[] { return csv.rows.map(r => r.file_name).sort(); }
  53  | 
  54  | type Report = { total: string; count: string; csv: Csv | null; csvVia: string };
  55  | 
  56  | /**
  57  |  * On /reports: choose client + month, click preview, read report-total / report-receipt-count,
  58  |  * then export the CSV through report-export-button (download event; falls back to the link's href).
  59  |  */
  60  | async function runReport(page: Page, testInfo: TestInfo, clientUuid: string, month: string, label: string): Promise<Report> {
  61  |   if (!page.url().includes('/reports')) await page.goto('/reports');
  62  |   await page.getByTestId('report-client-select').selectOption(clientUuid);
  63  |   await page.getByTestId('report-month-input').fill(month);
  64  |   const resp = page.waitForResponse(r => r.url().includes('/api/reports'), { timeout: 15_000 }).catch(() => null);
  65  |   await page.getByTestId('report-preview-button').click();
  66  |   await resp;
  67  |   await expect(page.getByTestId('report-total'), `${label}: report-total แสดงหลังกดดูตัวอย่าง`).toBeVisible();
  68  |   await page.waitForTimeout(300);
  69  |   const total = (await page.getByTestId('report-total').innerText()).trim();
  70  |   const count = (await page.getByTestId('report-receipt-count').innerText()).trim();
  71  |   await shot(testInfo, page, `${label} preview`);
  72  | 
  73  |   let csv: Csv | null = null; let csvVia = 'none';
  74  |   const btn = page.getByTestId('report-export-button');
  75  |   try {
  76  |     const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 15_000 }), btn.click()]);
  77  |     const p = await dl.path();
  78  |     csv = parseCsv(fs.readFileSync(p!, 'utf8')); csvVia = `download ${dl.suggestedFilename()}`;
  79  |   } catch {
  80  |     const href = await btn.getAttribute('href').catch(() => null);
  81  |     if (href) {
  82  |       const r = await page.request.get(href);
  83  |       expect.soft(r.status(), `${label}: W18 via export link href`).toBe(200);
  84  |       csv = parseCsv(await r.text()); csvVia = `href ${href}`;
  85  |       testInfo.annotations.push({ type: 'note', description: `${label}: export button gave no download event; CSV read from its href` });
  86  |     }
  87  |   }
  88  |   expect.soft(csv, `${label}: ได้ไฟล์ CSV จาก report-export-button`).not.toBeNull();
  89  |   if (csv) {
  90  |     await testInfo.attach(`${label}.csv`, { body: Buffer.from(csv.text, 'utf8'), contentType: 'text/csv' });
  91  |     expect.soft(csv.header, `${label}: CSV มีคอลัมน์ total`).toContain('total');
  92  |   }
  93  |   await evidence(testInfo, `${label} report`, { clientUuid, month, total, count, csvVia, csvRows: csv?.rows ?? null });
  94  |   return { total, count, csv, csvVia };
  95  | }
  96  | 
  97  | /** Soft checks: page total / count and CSV sum / row count equal the plan's expected values. */
  98  | function expectReport(r: Report, label: string, expSatang: number, expCount: number) {
  99  |   expect.soft(satang(r.total), `${label}: report-total (${r.total})`).toBe(expSatang);
  100 |   expect.soft(numOf(r.count), `${label}: report-receipt-count (${r.count})`).toBe(expCount);
  101 |   if (r.csv) {
  102 |     expect.soft(csvSum(r.csv), `${label}: ผลรวมคอลัมน์ total ใน CSV (สตางค์)`).toBe(expSatang);
  103 |     expect.soft(r.csv.rows.length, `${label}: จำนวนแถวใน CSV`).toBe(expCount);
  104 |   }
  105 | }
  106 | 
  107 | async function ownerReports(browser: Browser) {
  108 |   const s = await pageAs(browser, M_URL, 'U04');
  109 |   await s.page.goto('/reports');
  110 |   return s;
  111 | }
  112 | 
  113 | /** W9 poll (does not open any receipt) until every receipt of the batch is `review`. */
  114 | async function waitBatchReview(ctx: APIRequestContext, batchId: string, n: number, timeoutMs = 120_000) {
  115 |   const end = Date.now() + timeoutMs;
  116 |   for (;;) {
  117 |     const j = await (await ctx.get(`/api/batches/${batchId}`)).json();
  118 |     const rs: any[] = j.receipts ?? [];
  119 |     if (rs.length === n && rs.every(r => r.status === 'review')) return rs;
  120 |     if (Date.now() > end) throw new Error('timeout waiting for review: ' + rs.map(r => `${r.fileName}=${r.status}`).join(', '));
  121 |     await new Promise(r => setTimeout(r, 1500));
  122 |   }
  123 | }
  124 | 
  125 | const S = (code: string) => `${code}.jpg`; // seed receipts are named S-0x.jpg
  126 | const CL01_SEED = ['S-01', 'S-02', 'S-03', 'S-04', 'S-05', 'S-06', 'S-07'].map(S);
  127 | 
  128 | // ---------------------------------------------------------------- tests
  129 | test.describe('5.6 รายงานรายเดือน', () => {
  130 | 
  131 |   test('TC-6-01 สรุป พ.ย. 2026 ของ CL-01 · 1,340.00 บาท 4 ใบ', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  132 |     await reset(M_URL);
  133 |     const office = await apiAs(M_URL, 'U04');
  134 |     const cl01 = await clientId(office, 'CL-01');
  135 |     const { context, page } = await ownerReports(browser);
  136 |     try {
  137 |       const r = await runReport(page, testInfo, cl01, '2026-11', 'CL-01 2026-11');
  138 |       expectReport(r, 'CL-01 2026-11', 134000, 4);
  139 |       if (r.csv) {
  140 |         const files = csvFiles(r.csv);
> 141 |         expect.soft(files, 'CSV = S-02, S-03, S-04, S-07').toEqual([S('S-02'), S('S-03'), S('S-04'), S('S-07')].sort());
      |                                                            ^ Error: CSV = S-02, S-03, S-04, S-07
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
```