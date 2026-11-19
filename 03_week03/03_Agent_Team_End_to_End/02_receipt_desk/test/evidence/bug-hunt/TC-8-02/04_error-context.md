# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 58-portal.spec.ts >> 5.8 ลูกค้าภายนอก >> TC-8-02 ไม่มีตัวเลขของใบที่ยังไม่ยืนยัน
- Location: tests\58-portal.spec.ts:329:3

# Error details

```
Error: portal-summary-total พ.ย. = 1,340.00 (ไม่ใช่ 1,840.00)

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

```
Error: ยอดแยกหมวดบนหน้ารวม = 1,340.00

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
Error: W19 ยอดแยกหมวดรวม = 1,340.00

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

# Page snapshot

```yaml
- generic [active] [ref=f2e1]:
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
        - textbox "เดือน" [ref=f2e88]: 2026-11
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
  320 |       expect.soft(w13s02.ct, '⑥ W13 S-02 ได้รูป').toMatch(/^image\/|application\/pdf/);
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
> 376 |       expect.soft((w19.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0), 'W19 ยอดแยกหมวดรวม = 1,340.00').toBe(134000);
      |                                                                                                                                 ^ Error: W19 ยอดแยกหมวดรวม = 1,340.00
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
  421 |       await evidence(testInfo, '① W12 __001 หลังยืนยัน (U-01)', c1[0]);
  422 |       await shot(testInfo, s.st.page, '① U-01 ยืนยัน __001');
  423 | 
  424 |       let st = await portalState(s.cust.page);
  425 |       let rows = await portalRows(s.cust.page, s.ids);
  426 |       await shot(testInfo, s.cust.page, '① U-05 /portal หลังยืนยัน __001');
  427 |       await evidence(testInfo, '① /portal หลังยืนยัน', { summary: st.summary, cats: st.cats, rows });
  428 |       expect.soft(rows[id1].totalCount, '① __001 มี portal-receipt-total').toBeGreaterThan(0);
  429 |       expect.soft(satang(rows[id1].total), '① __001 แสดงยอด 100.00').toBe(10000);
  430 |       expect.soft(rows[id2].totalCount, '① __002 ยังไม่มีตัวเลข (portal-receipt-total)').toBe(0);
  431 |       expect.soft(rowExtraDigits(rows[id2].row, s.files[1]), '① แถว __002 ยังไม่มีตัวเลข').toBeNull();
  432 |       expect.soft(satang(st.summary), '① สรุป พ.ย. = 1,340.00 + 100.00 = 1,440.00').toBe(144000);
  433 |       expect.soft(satang(st.cats.find(c => c.id === cat01)?.text), '① CAT-01 = 1,200.50 + 100.00 = 1,300.50').toBe(130050);
  434 |       expect.soft(st.cats.reduce((a, c) => a + satang(c.text), 0), '① รวมหมวด = 1,440.00').toBe(144000);
  435 |       const w19a = await (await s.client.get('/api/reports/categories?month=2026-11')).json();
  436 |       await evidence(testInfo, '① W19 ของลูกค้า', w19a);
  437 |       expect.soft(satang(w19a.total), '① W19 total = 1,440.00').toBe(144000);
  438 |       expect.soft(satang((w19a.categories ?? []).find((c: any) => c.id === cat01)?.total), '① W19 CAT-01 = 1,300.50').toBe(130050);
  439 |       expect.soft((w19a.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0), '① W19 รวมหมวด = 1,440.00').toBe(144000);
  440 | 
  441 |       // ② U-03 reopens __001
  442 |       lead.page.on('dialog', d => d.accept().catch(() => undefined));
  443 |       await lead.page.goto(`/receipts/${id1}`);
  444 |       const reason = lead.page.getByTestId('reopen-reason-input');
  445 |       if (await reason.isVisible().catch(() => false)) await reason.fill('ทดสอบ TC-8-04 เปิดใบกลับ');
  446 |       await lead.page.getByTestId('reopen-button').click();
  447 |       const r2 = await waitStatus(s.staff, [id1], ['review'], 30_000).catch(e => { throw new Error('② U-03 เปิดใบกลับไม่สำเร็จ: ' + e); });
  448 |       await evidence(testInfo, '② W12 __001 หลังเปิดกลับ (office)', r2[0]);
  449 |       await shot(testInfo, lead.page, '② U-03 เปิด __001 กลับ');
  450 | 
  451 |       st = await portalState(s.cust.page);
  452 |       await shot(testInfo, s.cust.page, '② U-05 /portal หลังเปิดกลับ');
  453 |       await evidence(testInfo, '② /portal หลังเปิดกลับ', { summary: st.summary, cats: st.cats });
  454 |       await expectNoNumbersForCustomer(s.cust.page, s.client, [id1], [s.files[0]], testInfo, '② __001');
  455 |       expect.soft(satang(st.summary), '② สรุป พ.ย. กลับเป็น 1,340.00').toBe(134000);
  456 |       expect.soft(satang(st.cats.find(c => c.id === cat01)?.text), '② CAT-01 = 1,200.50').toBe(120050);
  457 |       const w19b = await (await s.client.get('/api/reports/categories?month=2026-11')).json();
  458 |       await evidence(testInfo, '② W19 ของลูกค้า', w19b);
  459 |       expect.soft(satang(w19b.total), '② W19 total = 1,340.00').toBe(134000);
  460 |       expect.soft(satang((w19b.categories ?? []).find((c: any) => c.id === cat01)?.total), '② W19 CAT-01 = 1,200.50').toBe(120050);
  461 |     } finally {
  462 |       await lead.context.close(); await s.cust.context.close(); await s.st.context.close();
  463 |       await s.office.dispose(); await s.staff.dispose(); await s.client.dispose();
  464 |     }
  465 |   });
  466 | 
  467 |   test('TC-8-05 ลูกค้าส่งใบเข้าร้านอื่นไม่ได้ และคิวเต็มจากหน้าลูกค้า', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  468 |     test.setTimeout(15 * 60_000);
  469 |     // ①
  470 |     await reset(M_URL);
  471 |     let office = await apiAs(M_URL, 'U04');
  472 |     const client5 = await apiAs(M_URL, 'U05');
  473 |     const cl01 = await clientId(office, 'CL-01');
  474 |     const cl02 = await clientId(office, 'CL-02');
  475 |     const count = async (o: APIRequestContext, cl: string) => (await officeReceipts(o, `&client_id=${cl}`)).length;
  476 |     const before = { cl01: await count(office, cl01), cl02: await count(office, cl02) };
```