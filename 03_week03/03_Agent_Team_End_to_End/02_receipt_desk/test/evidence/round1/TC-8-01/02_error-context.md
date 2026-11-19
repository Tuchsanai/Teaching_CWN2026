# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 58-portal.spec.ts >> 5.8 ลูกค้าภายนอก >> TC-8-01 ลูกค้า CL-01 ขอข้อมูลร้าน CL-02 ทุกช่องทาง
- Location: tests\58-portal.spec.ts:240:3

# Error details

```
Error: ③ W11 client_id=CL-02: คืนรายการ (เฉพาะใบ CL-01)

expect(received).toBe(expected) // Object.is equality

Expected: 200
Received: 404
```

```
Error: ⑥ W13 S-02 (ร้านตัวเอง): HTTP

expect(received).toBe(expected) // Object.is equality

Expected: 200
Received: 404
```

```
Error: ⑥ W13 S-02 ได้รูป

expect(received).toMatch(expected)

Expected pattern: /^image\/|application\/pdf/
Received string:  "application/json"
```

# Test source

```ts
  220 |     expect.soft(r.totalCount, `${label}: ${files[i]} ไม่มี portal-receipt-total`).toBe(0);
  221 |     expect.soft(r.row, `${label}: แถว ${files[i]} ไม่มี 100.00`).not.toMatch(RE_100);
  222 |     expect.soft(rowExtraDigits(r.row, files[i]), `${label}: แถว ${files[i]} ไม่มีตัวเลขอื่นนอกจากเวลา (รายการ/ราคา)`).toBeNull();
  223 |     expect.soft(r.row, `${label}: แถว ${files[i]} ไม่มีสถานะภายใน`).not.toMatch(/queued|review|processing/);
  224 |     const w11 = list.find(x => x.id === ids[i]);
  225 |     const w12r = await client.get(`/api/receipts/${ids[i]}`);
  226 |     const w12 = await w12r.json().catch(() => ({}));
  227 |     await evidence(testInfo, `${label} JSON ${files[i]} (W11 + W12 ของลูกค้า)`, { w11, w12status: w12r.status(), w12 });
  228 |     expect.soft(w12r.status(), `${label}: W12 ${files[i]} ของร้านตัวเอง`).toBe(200);
  229 |     expect.soft(numberFields(w11), `${label}: W11 ${files[i]} ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ`).toEqual([]);
  230 |     expect.soft(numberFields(w12), `${label}: W12 ${files[i]} ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ`).toEqual([]);
  231 |     expect.soft(leakedValues({ w11, w12 }, RE_100), `${label}: JSON ${files[i]} ไม่มี 100.00`).toEqual([]);
  232 |     expect.soft(JSON.stringify({ w11, w12 }), `${label}: JSON ${files[i]} ไม่มีสถานะภายใน`).not.toMatch(/"(queued|review|processing)"/);
  233 |   }
  234 |   const body = await page.locator('body').innerText();
  235 |   expect.soft(body, `${label}: หน้าไม่มีสถานะภายใน queued/review`).not.toMatch(/\b(queued|review)\b/);
  236 | }
  237 | 
  238 | // ---------------------------------------------------------------- tests
  239 | test.describe('5.8 ลูกค้าภายนอก', () => {
  240 |   test('TC-8-01 ลูกค้า CL-01 ขอข้อมูลร้าน CL-02 ทุกช่องทาง', { tag: ['@P1', '@A'] }, async ({}, testInfo) => {
  241 |     await reset(M_URL);
  242 |     const office = await apiAs(M_URL, 'U04');
  243 |     const client = await apiAs(M_URL, 'U05');
  244 |     try {
  245 |       const s08 = await byFile(office, 'S-08.jpg');
  246 |       const s02 = await byFile(office, 'S-02.jpg');
  247 |       const cl02 = await clientId(office, 'CL-02');
  248 |       const ghost = '0f1e2d3c-4b5a-4978-8a6b-5c4d3e2f1a0b';
  249 |       await evidence(testInfo, 'U-04 จด id', { s08: { id: s08.id, batchId: s08.batchId }, s02: s02.id, cl02, ghost });
  250 | 
  251 |       const call = async (path: string) => {
  252 |         const r = await client.get(path);
  253 |         const text = await r.text();
  254 |         let json: any = null; try { json = JSON.parse(text); } catch { /* binary */ }
  255 |         return { path, status: r.status(), ct: r.headers()['content-type'] || '', text: json ? text : `<${text.length} bytes>`, json };
  256 |       };
  257 |       const leaksCL02 = (x: { text: string }) =>
  258 |         [s08.id, 'S-08.jpg', cl02, 'ร้านกาแฟมะลิ', s08.batchId].filter(v => x.text.includes(v)).concat(RE_999.test(x.text) ? ['999.00'] : []);
  259 | 
  260 |       // ① S-08 via W12 / W13
  261 |       const w12s08 = await call(`/api/receipts/${s08.id}`);
  262 |       const w13s08 = await call(`/api/receipts/${s08.id}/image`);
  263 |       // ② id that does not exist
  264 |       const w12ghost = await call(`/api/receipts/${ghost}`);
  265 |       const w13ghost = await call(`/api/receipts/${ghost}/image`);
  266 |       // ③ W11 client_id=CL-02
  267 |       const w11 = await call(`/api/receipts?client_id=${cl02}`);
  268 |       // ④ W19 clientId=CL-02
  269 |       const w19 = await call(`/api/reports/categories?clientId=${cl02}&month=2026-11`);
  270 |       // ⑤ W9 batch of S-08 · W17 S-08 · W20 · W23
  271 |       const w9 = await call(`/api/batches/${s08.batchId}`);
  272 |       const w17 = await call(`/api/receipts/${s08.id}/history`);
  273 |       const w20 = await call('/api/reports/reconcile');
  274 |       const w23 = await call('/api/queue');
  275 |       // ⑥ control: own S-02
  276 |       const w12s02 = await call(`/api/receipts/${s02.id}`);
  277 |       const w13s02 = await call(`/api/receipts/${s02.id}/image`);
  278 |       const all = { w12s08, w13s08, w12ghost, w13ghost, w11, w19, w9, w17, w20, w23, w12s02, w13s02 };
  279 |       await evidence(testInfo, 'คำตอบทุกคำขอของ U-05', Object.fromEntries(Object.entries(all).map(([k, v]) => [k, { path: v.path, status: v.status, ct: v.ct, body: v.text }])));
  280 | 
  281 |       // ①
  282 |       for (const [n, x] of [['W12 S-08', w12s08], ['W13 S-08', w13s08]] as const) {
  283 |         expect.soft(x.status, `① ${n}: HTTP`).toBe(404);
  284 |         expect.soft(x.json?.error, `① ${n}: error`).toBe('not_found');
  285 |       }
  286 |       // ① vs ② pairwise identical
  287 |       expect.soft(w12s08.status, '①/② W12 S-08 กับ id ที่ไม่มีอยู่: สถานะเดียวกัน').toBe(w12ghost.status);
  288 |       expect.soft(w12s08.text, '①/② W12: body เหมือนกัน').toBe(w12ghost.text);
  289 |       expect.soft(w13s08.status, '①/② W13 S-08 กับ id ที่ไม่มีอยู่: สถานะเดียวกัน').toBe(w13ghost.status);
  290 |       expect.soft(w13s08.text, '①/② W13: body เหมือนกัน').toBe(w13ghost.text);
  291 |       expect.soft(w13s08.text, '① W13 S-08 ไม่มี image_missing').not.toContain('image_missing');
  292 | 
  293 |       // ③ only CL-01 receipts
  294 |       const cl01Ids = new Set((await officeReceipts(office, `&client_id=${await clientId(office, 'CL-01')}`)).map(r => r.id));
  295 |       expect.soft(w11.status, '③ W11 client_id=CL-02: คืนรายการ (เฉพาะใบ CL-01)').toBe(200);
  296 |       const w11ids: string[] = (w11.json?.receipts ?? []).map((r: any) => r.id);
  297 |       expect.soft(w11ids.filter(id => !cl01Ids.has(id)), '③ W11: ทุกใบเป็นของ CL-01').toEqual([]);
  298 |       expect.soft(w11ids, '③ W11: ไม่มี S-08').not.toContain(s08.id);
  299 |       expect.soft(leaksCL02(w11), '③ W11: ไม่มีข้อมูล CL-02 / 999.00').toEqual([]);
  300 | 
  301 |       // ④ CL-01 totals or refused, never CL-02
  302 |       expect.soft(leaksCL02(w19), '④ W19 clientId=CL-02: ไม่มีข้อมูล CL-02').toEqual([]);
  303 |       if (w19.status === 200) {
  304 |         testInfo.annotations.push({ type: '④ W19', description: `200 total=${w19.json?.total}` });
  305 |         expect.soft(satang(w19.json?.total), '④ W19 ได้ยอดของ CL-01 (1,340.00)').toBe(134000);
  306 |       } else {
  307 |         testInfo.annotations.push({ type: '④ W19', description: `ถูกปฏิเสธ ${w19.status}` });
  308 |         expect.soft([403, 404], '④ W19 ถูกปฏิเสธ').toContain(w19.status);
  309 |       }
  310 | 
  311 |       // ⑤ all refused (403 or 404)
  312 |       for (const [n, x] of [['W9 ชุดของ S-08', w9], ['W17 S-08', w17], ['W20', w20], ['W23', w23]] as const) {
  313 |         expect.soft([403, 404], `⑤ ${n}: ถูกปฏิเสธ (ได้ ${x.status})`).toContain(x.status);
  314 |       }
  315 | 
  316 |       // ⑥ control
  317 |       expect.soft(w12s02.status, '⑥ W12 S-02 (ร้านตัวเอง): HTTP').toBe(200);
  318 |       expect.soft(w12s02.json?.receipt?.id ?? w12s02.json?.id, '⑥ W12 S-02 ได้ข้อมูล').toBe(s02.id);
  319 |       expect.soft(w13s02.status, '⑥ W13 S-02 (ร้านตัวเอง): HTTP').toBe(200);
> 320 |       expect.soft(w13s02.ct, '⑥ W13 S-02 ได้รูป').toMatch(/^image\/|application\/pdf/);
      |                                                   ^ Error: ⑥ W13 S-02 ได้รูป
  321 | 
  322 |       // no request returns CL-02 data
  323 |       for (const [k, v] of Object.entries(all)) expect.soft(leaksCL02(v), `ไม่มีข้อมูลของ CL-02 ใน ${k}`).toEqual([]);
  324 |     } finally {
  325 |       await office.dispose(); await client.dispose();
  326 |     }
  327 |   });
  328 | 
  329 |   test('TC-8-02 ไม่มีตัวเลขของใบที่ยังไม่ยืนยัน', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  330 |     await reset(M_URL);
  331 |     const office = await apiAs(M_URL, 'U04');
  332 |     const client = await apiAs(M_URL, 'U05');
  333 |     const { context, page } = await pageAs(browser, M_URL, 'U05');
  334 |     try {
  335 |       const s06 = await byFile(office, 'S-06.jpg');
  336 |       const st = await portalState(page);
  337 |       await shot(testInfo, page, 'U-05 /portal เดือน 2026-11');
  338 |       const rows = await portalRows(page, [s06.id]);
  339 |       const row = rows[s06.id];
  340 |       await evidence(testInfo, 'แถว S-06 + สรุปบน /portal', { row, summary: st.summary, cats: st.cats });
  341 | 
  342 |       // row S-06 (by ID): only file name, accepted time, status
  343 |       expect.soft(row.visible, 'แถว S-06 (ตาม ID) อยู่บนหน้า').toBe(true);
  344 |       expect.soft(row.row, 'แถว S-06 มีชื่อไฟล์').toContain('S-06.jpg');
  345 |       expect.soft(row.row, 'แถว S-06 มีเวลาที่รับ').toMatch(/\d{1,2}\/\d{1,2}\/\d{4}\s+\d{1,2}:\d{2}/);
  346 |       expect.soft(row.status, 'แถว S-06 สถานะ').toBe(STATUS_WAITING);
  347 |       expect.soft(rowExtraDigits(row.row, 'S-06.jpg'), 'แถว S-06 ไม่มีตัวเลขอื่นนอกจากเวลาที่รับ').toBeNull();
  348 |       expect.soft(row.row, 'แถว S-06 ไม่มีร้าน/วันที่บนใบ/หมวด').not.toMatch(/ร้านตัวอย่าง|2026-11-15|วัตถุดิบ|ค่าแก๊ส|ค่าน้ำแข็ง|อื่น ๆ/);
  349 |       expect.soft(row.totalCount, 'ไม่มี portal-receipt-total ของ S-06').toBe(0);
  350 |       expect.soft(st.text, 'หน้า /portal ไม่มี 500.00 / 500 / 50000').not.toMatch(RE_500);
  351 | 
  352 |       // JSON W11 / W12 / W19
  353 |       const w11r = await client.get('/api/receipts?limit=1000');
  354 |       const w11 = await w11r.json();
  355 |       const w11s06 = (w11.receipts ?? []).find((r: any) => r.id === s06.id);
  356 |       const w12r = await client.get(`/api/receipts/${s06.id}`);
  357 |       const w12 = await w12r.json().catch(() => ({}));
  358 |       const w19r = await client.get('/api/reports/categories?month=2026-11');
  359 |       const w19 = await w19r.json().catch(() => ({}));
  360 |       await evidence(testInfo, 'U-05 W11 (S-06) · W12 S-06 · W19 2026-11', { w11status: w11r.status(), w11s06, w12status: w12r.status(), w12, w19status: w19r.status(), w19 });
  361 |       expect.soft(w11s06, 'W11 ของลูกค้ามี S-06').toBeTruthy();
  362 |       expect.soft(w12r.status(), 'W12 S-06 (ร้านตัวเอง)').toBe(200);
  363 |       expect.soft(numberFields(w11s06), 'W11 S-06 ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ').toEqual([]);
  364 |       expect.soft(numberFields(w12), 'W12 S-06 ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ').toEqual([]);
  365 |       expect.soft(leakedValues(w11s06, RE_500), 'W11 S-06 ไม่มี 500.00 / 500 / 50000').toEqual([]);
  366 |       expect.soft(leakedValues(w12, RE_500), 'W12 S-06 ไม่มี 500.00 / 500 / 50000').toEqual([]);
  367 |       expect.soft(leakedValues(w11, RE_500), 'W11 ทั้งคำตอบไม่มี 500.00 / 500 / 50000').toEqual([]);
  368 |       expect.soft(leakedValues(w19, RE_500), 'W19 ไม่มี 500.00 / 500 / 50000').toEqual([]);
  369 | 
  370 |       // summary 1,340.00 (not 1,840.00) · categories 1,340.00
  371 |       expect.soft(satang(st.summary), 'portal-summary-total พ.ย. = 1,340.00 (ไม่ใช่ 1,840.00)').toBe(134000);
  372 |       const catSum = st.cats.reduce((a, c) => a + satang(c.text), 0);
  373 |       expect.soft(catSum, 'ยอดแยกหมวดบนหน้ารวม = 1,340.00').toBe(134000);
  374 |       expect.soft(w19r.status(), 'W19 ของลูกค้า').toBe(200);
  375 |       expect.soft(satang(w19.total), 'W19 total = 1,340.00').toBe(134000);
  376 |       expect.soft((w19.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0), 'W19 ยอดแยกหมวดรวม = 1,340.00').toBe(134000);
  377 |     } finally {
  378 |       await context.close(); await office.dispose(); await client.dispose();
  379 |     }
  380 |   });
  381 | 
  382 |   test('TC-8-03 ลูกค้าส่งใบเอง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  383 |     test.setTimeout(20 * 60_000);
  384 |     const s = await customerUploadsTwo(browser, testInfo);
  385 |     try {
  386 |       expect.soft(s.readTimeout, '② ทั้ง 2 ID เป็นรอตรวจภายใน 5 นาที (ถ้าไม่ = หมดเวลาอ่าน)').toBe(false);
  387 |       const reviewCL01 = (await officeReceipts(s.office, `&client_id=${s.cl01}`)).filter(r => r.status === 'review');
  388 |       await evidence(testInfo, '② ใบรอตรวจของ CL-01 (office)', reviewCL01.map(r => ({ id: r.id, fileName: r.fileName, status: r.status })));
  389 |       for (const id of s.ids) expect.soft(reviewCL01.map(r => r.id), `② ${id} เป็นรอตรวจ`).toContain(id);
  390 |       expect.soft(reviewCL01.length, '② รวมกับ S-06 = 3 ใบรอตรวจของ CL-01').toBe(3);
  391 | 
  392 |       // customer refreshes /portal
  393 |       await s.cust.page.goto('/portal');
  394 |       await s.cust.page.getByTestId('portal-month-input').waitFor({ state: 'visible' });
  395 |       await shot(testInfo, s.cust.page, '② U-05 รีเฟรช /portal หลังอ่านเสร็จ');
  396 |       await expectNoNumbersForCustomer(s.cust.page, s.client, s.ids, s.files, testInfo, '②');
  397 |       const rows = await portalRows(s.cust.page, s.ids);
  398 |       s.ids.forEach((id, i) => expect.soft(rows[id].status, `② แถว ${s.files[i]} สถานะ`).toBe(STATUS_WAITING));
  399 |     } finally {
  400 |       await s.cust.context.close(); await s.st.context.close();
  401 |       await s.office.dispose(); await s.staff.dispose(); await s.client.dispose();
  402 |     }
  403 |   });
  404 | 
  405 |   test('TC-8-04 ตัวเลขขึ้นเมื่อยืนยัน และหายเมื่อเปิดกลับ', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  406 |     test.setTimeout(20 * 60_000);
  407 |     // ต่อจาก TC-8-03: repeat its setup so this test runs on its own
  408 |     const s = await customerUploadsTwo(browser, testInfo);
  409 |     const lead = await pageAs(browser, M_URL, 'U03');
  410 |     try {
  411 |       expect(s.readTimeout, 'ขั้นตั้งต้น (TC-8-03): ทั้ง 2 ใบเป็นรอตรวจภายใน 5 นาที').toBe(false);
  412 |       const [id1, id2] = s.ids;
  413 |       const cat01 = await categoryId(s.office, 'CAT-01');
  414 | 
  415 |       // ① U-01 confirms __001 with CAT-01 through /receipts/[id]
  416 |       await s.st.page.goto(`/receipts/${id1}`);
  417 |       await s.st.page.getByTestId('category-select').selectOption(cat01);
  418 |       await s.st.page.getByTestId('total-checked-checkbox').check();
  419 |       await s.st.page.getByTestId('confirm-button').click();
  420 |       const c1 = await waitStatus(s.staff, [id1], ['confirmed'], 30_000).catch(e => { throw new Error('① U-01 ยืนยันไม่สำเร็จ: ' + e); });
```