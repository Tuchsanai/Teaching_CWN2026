# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 53-review.spec.ts >> TC-3-06 แก้ทุกช่องโดยพนักงานและหัวหน้า ค่าเดิมไม่ถูกทับ
- Location: tests\53-review.spec.ts:308:1

# Error details

```
Error: ③ 6 history rows on page

expect(locator).toHaveCount(expected) failed

Locator:  locator('[data-testid^="history-row-"]')
Expected: 6
Received: 5
Timeout:  15000ms

Call log:
  - ③ 6 history rows on page locator('[data-testid^="history-row-"]') with timeout 15000ms
  - waiting for locator('[data-testid^="history-row-"]')
    - locator resolved to 0 elements
    - unexpected value "0"
    32 × locator resolved to 5 elements
       - unexpected value "5"

```

```
Error: 6 edits (5 U-01 + 1 U-03)

expect(received).toBe(expected) // Object.is equality

Expected: 6
Received: 5
```

```
Error: 5 edits by คุณพิมพ์

expect(received).toBe(expected) // Object.is equality

Expected: 5
Received: 4
```

# Page snapshot

```yaml
- generic [ref=f3e1]:
  - banner [ref=f3e2]:
    - link "ReceiptDesk" [ref=f3e3] [cursor=pointer]:
      - /url: /
    - navigation [ref=f3e5]:
      - link "อัปโหลดชุด" [ref=f3e6] [cursor=pointer]:
        - /url: /upload
      - link "ชุดใบเสร็จ" [ref=f3e7] [cursor=pointer]:
        - /url: /batches
      - link "รายการใบ" [ref=f3e8] [cursor=pointer]:
        - /url: /receipts
      - link "อ่านไม่ได้" [ref=f3e9] [cursor=pointer]:
        - /url: /unreadable
      - link "สรุปรายเดือน" [ref=f3e10] [cursor=pointer]:
        - /url: /reports
    - generic [ref=f3e11]:
      - generic [ref=f3e12]: คุณพิมพ์
      - generic [ref=f3e13]: พนักงานบัญชี
      - button "ออกจากระบบ" [ref=f3e14] [cursor=pointer]
  - main [ref=f3e15]:
    - generic [ref=f3e16]:
      - generic [ref=f3e17]:
        - generic [ref=f3e18]:
          - link "← คิวรอตรวจ" [ref=f3e19] [cursor=pointer]:
            - /url: /review
          - heading "ตรวจใบเสร็จ ok-100__001.jpg" [level=1] [ref=f3e20]
          - paragraph [ref=f3e21]:
            - text: ร้านข้าวแกงสมชาย · รับเมื่อ 19 พ.ย. 2569 17:42 · สถานะ
            - strong [ref=f3e22]: รอตรวจ
        - 'generic "NFR-09: เฉลี่ยต้องน้อยกว่า 120 วินาทีต่อใบ · เป้าหมายทีม ≤ 40 วินาที" [ref=f3e23]': เวลาตรวจ 0:15
      - generic [ref=f3e25]:
        - text: ✓ ใบปกติ — ตรวจยอดรวมเทียบกับรูปช่องเดียวแล้วยืนยันได้
        - generic [ref=f3e26]: · ความมั่นใจยอดรวม 0.9900
      - generic [ref=f3e27]:
        - generic [ref=f3e28]:
          - generic [ref=f3e29]:
            - button "ย่อรูป" [ref=f3e30] [cursor=pointer]: −
            - generic [ref=f3e31]: 100%
            - button "ขยายรูป" [ref=f3e32] [cursor=pointer]: +
            - button "พอดี" [ref=f3e33] [cursor=pointer]
            - button "หมุนรูป" [ref=f3e34] [cursor=pointer]: ⟳
            - link "เปิดรูปในแท็บใหม่ ↗" [ref=f3e35] [cursor=pointer]:
              - /url: /api/receipts/848efb9e-9316-4f1c-bee9-bd4d15a4baa7/image
          - img "รูปใบเสร็จ ok-100__001.jpg" [ref=f3e37]
        - generic [ref=f3e38]:
          - generic [ref=f3e39]:
            - generic [ref=f3e40]:
              - generic [ref=f3e41]: ชื่อร้าน แก้แล้ว
              - generic [ref=f3e42]: "ระบบอ่าน: ร้านตัวอย่าง"
            - textbox "ชื่อร้าน" [ref=f3e43]: ร้านแก้ไข
          - generic [ref=f3e44]:
            - generic [ref=f3e45]:
              - generic [ref=f3e46]: วันที่บนใบ แก้แล้ว
              - generic [ref=f3e47]: "ระบบอ่าน: 18 พ.ย. 2569 (2026-11-18)"
            - textbox "วันที่บนใบ" [ref=f3e48]: 2026-11-17
          - generic [ref=f3e49]:
            - generic [ref=f3e50]:
              - generic [ref=f3e51]: รายการสินค้าและราคา
              - generic [ref=f3e52]:
                - text: ผลรวมรายการ
                - strong [ref=f3e53]: "120.00"
                - text: บาท
                - generic [ref=f3e54]: · ต่างจากยอดรวม 0.00
            - table [ref=f3e55]:
              - rowgroup [ref=f3e56]:
                - row [ref=f3e57]:
                  - columnheader "#" [ref=f3e58]
                  - columnheader "รายการ" [ref=f3e59]
                  - columnheader "ราคา" [ref=f3e60]
                  - columnheader [ref=f3e61]
              - rowgroup [ref=f3e62]:
                - row [ref=f3e63]:
                  - cell "1" [ref=f3e64]
                  - cell [ref=f3e65]:
                    - textbox "ชื่อรายการบรรทัด 1" [ref=f3e66]: ข้าวสาร
                  - cell [ref=f3e67]:
                    - textbox "ราคาบรรทัด 1" [ref=f3e68]: "45.00"
                  - cell [ref=f3e69]:
                    - button "ลบ" [ref=f3e70] [cursor=pointer]
                - row [ref=f3e71]:
                  - cell "2" [ref=f3e72]
                  - cell [ref=f3e73]:
                    - textbox "ชื่อรายการบรรทัด 2" [ref=f3e74]: น้ำมันพืช
                  - cell [ref=f3e75]:
                    - textbox "ราคาบรรทัด 2" [ref=f3e76]: "30.00"
                  - cell [ref=f3e77]:
                    - button "ลบ" [ref=f3e78] [cursor=pointer]
                - row [ref=f3e79]:
                  - cell "3" [ref=f3e80]
                  - cell [ref=f3e81]:
                    - textbox "ชื่อรายการบรรทัด 3" [ref=f3e82]: น้ำตาลทราย
                  - 'cell "45.00 ระบบอ่าน: 25.00" [ref=f3e83]':
                    - textbox "ราคาบรรทัด 3" [ref=f3e84]: "45.00"
                    - generic [ref=f3e85]: "ระบบอ่าน: 25.00"
                  - cell [ref=f3e86]:
                    - button "ลบ" [ref=f3e87] [cursor=pointer]
            - button "+ เพิ่มรายการ" [ref=f3e88] [cursor=pointer]
          - generic [ref=f3e89]:
            - generic [ref=f3e90]:
              - generic [ref=f3e91]: ยอดรวม (บาท) แก้แล้ว
              - generic [ref=f3e92]: "ระบบอ่าน: 100.00"
            - textbox "ยอดรวม" [active] [ref=f3e93]: "120.00"
          - generic [ref=f3e94]:
            - generic [ref=f3e95]: หมวดรายจ่าย
            - combobox "หมวดรายจ่าย" [ref=f3e97]:
              - option "— เลือกหมวด —" [selected]
              - option "วัตถุดิบ"
              - option "ค่าแก๊ส"
              - option "ค่าน้ำแข็ง"
              - option "อื่น ๆ"
          - generic [ref=f3e98]:
            - generic [ref=f3e99] [cursor=pointer]:
              - checkbox "เทียบยอดรวมกับรูปแล้ว" [ref=f3e100]
              - text: เทียบยอดรวมกับรูปแล้ว
            - generic [ref=f3e101]:
              - button "บันทึก" [disabled]
              - button "ยืนยัน" [disabled]
              - button "ข้าม → ใบถัดไป" [ref=f3e102] [cursor=pointer]
            - list [ref=f3e103]:
              - listitem [ref=f3e104]: ติ๊ก "เทียบยอดรวมกับรูปแล้ว"
              - listitem [ref=f3e105]: เลือกหมวดรายจ่าย
            - paragraph [ref=f3e106]: Enter = ช่องถัดไป · Ctrl/⌘+Enter = ยืนยัน · Ctrl/⌘+S = บันทึก · Alt+→ = ใบถัดไป
          - button "ดูค่าเดิมและประวัติการแก้" [ref=f3e108] [cursor=pointer]
  - alert [ref=f3e109]
```

# Test source

```ts
  266 |   await up.dispose();
  267 | 
  268 |   const fresh = await apiAs(M_URL, 'U01'); // new U-01 session, never opened anything
  269 |   const { context, page } = await pageAs(browser, M_URL, 'U01');
  270 |   try {
  271 |     const cat4 = await categoryId(fresh, 'CAT-04');
  272 |     const body = { totalChecked: true, categoryId: cat4 };
  273 | 
  274 |     // ① confirm __001 right away: no page, no W12
  275 |     const c1 = await confirm(fresh, id1, body);
  276 |     await evidence(testInfo, '① confirm without opening', c1);
  277 |     expect.soft(c1.status >= 400 && c1.status < 500, `① must be rejected (got ${c1.status})`).toBe(true);
  278 | 
  279 |     // ② W12 on __001, then confirm -> recorded for AP-03
  280 |     const r1 = await getR(fresh, id1);
  281 |     await evidence(testInfo, '② W12 __001 (after ①)', r1);
  282 |     expect.soft(r1.status, '① status stays review').toBe('review');
  283 |     expect.soft(r1.flags?.flagged, 'conf-089 is a flagged receipt').toBe(true);
  284 |     const c2 = await confirm(fresh, id1, body);
  285 |     await evidence(testInfo, '② confirm after W12', c2);
  286 |     const r1b = await getR(fresh, id1);
  287 |     pendingAP(testInfo, 'AP-03', `W12 then W15 on conf-089__001 -> HTTP ${c2.status} ${c2.json.error ?? ''} · status=${r1b.status}`);
  288 | 
  289 |     // ③ __002 through the browser page, then confirm
  290 |     await openReceipt(page, id2);
  291 |     await viewAllFields(page);
  292 |     const c3 = await confirmOnPage(page, id2);
  293 |     expect.soft(c3, '③ confirm-button must be usable').not.toBeNull();
  294 |     if (c3) {
  295 |       await evidence(testInfo, '③ confirm on page', c3);
  296 |       expect.soft(c3.status, '③ confirm must succeed').toBeLessThan(300);
  297 |     }
  298 |     await page.reload();
  299 |     await expect.soft(page.getByTestId('confirmed-by'), '③ confirmed-by คุณพิมพ์').toContainText(PIM);
  300 |     await shot(testInfo, page, '③ confirmed __002');
  301 |     const r2 = await getR(fresh, id2);
  302 |     await evidence(testInfo, '③ W12 __002', r2);
  303 |     expect.soft(r2.status, '③ status confirmed').toBe('confirmed');
  304 |     expect.soft(JSON.stringify(r2.confirmedBy ?? ''), '③ confirmedBy คุณพิมพ์').toContain(PIM);
  305 |   } finally { await context.close(); await fresh.dispose(); }
  306 | });
  307 | 
  308 | test('TC-3-06 แก้ทุกช่องโดยพนักงานและหัวหน้า ค่าเดิมไม่ถูกทับ', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  309 |   await reset(M_URL);
  310 |   const u01 = await apiAs(M_URL, 'U01');
  311 |   const { ids: [id] } = await uploadCL01(u01, ['ok-100__001.jpg']);
  312 |   await waitStatus(u01, [id], ['review']);
  313 | 
  314 |   const s1 = await pageAs(browser, M_URL, 'U01');
  315 |   const s3 = await pageAs(browser, M_URL, 'U03');
  316 |   try {
  317 |     // ① U-01 edits 5 fields
  318 |     const p = s1.page;
  319 |     await openReceipt(p, id);
  320 |     await p.getByTestId('field-merchant-input').fill('ร้านแก้ไข');
  321 |     await p.getByTestId('field-date-input').fill('2026-11-17');
  322 |     await p.getByTestId('item-name-input-1').fill('ข้าวสาร');
  323 |     await p.getByTestId('item-price-input-3').fill('45.00');
  324 |     await p.getByTestId('field-total-input').fill('120.00');
  325 |     const sv1 = await saveOnPage(p, id);
  326 |     await evidence(testInfo, '① W14 U-01', sv1);
  327 |     expect.soft(sv1.status, '① save must succeed').toBeLessThan(300);
  328 |     await p.reload();
  329 |     await expect.soft(p.getByTestId('items-sum'), '① items-sum = 120.00').toContainText('120.00');
  330 |     await expect.soft(p.getByTestId('flag-mismatch'), '① no mismatch flag (|120-120| = 0)').toHaveCount(0);
  331 |     await shot(testInfo, p, '① after U-01 edit');
  332 |     const a = await getR(u01, id);
  333 |     await evidence(testInfo, '① W12', a);
  334 |     expect.soft(money(a.itemsSum), '① itemsSum 120.00').toBe(12000);
  335 |     expect.soft(a.flags?.mismatch, '① flags.mismatch false').toBe(false);
  336 | 
  337 |     // ② U-03 edits merchant
  338 |     const q = s3.page;
  339 |     await openReceipt(q, id);
  340 |     await q.getByTestId('field-merchant-input').fill('ร้านแก้ไข 2');
  341 |     const sv2 = await saveOnPage(q, id);
  342 |     await evidence(testInfo, '② W14 U-03', sv2);
  343 |     expect.soft(sv2.status, '② save must succeed').toBeLessThan(300);
  344 | 
  345 |     // ③ U-03 history
  346 |     await q.reload();
  347 |     await q.getByTestId('history-button').click();
  348 |     await expect.soft(q.locator('[data-testid^="history-row-"]'), '③ 6 history rows on page').toHaveCount(6);
  349 |     const om = (await q.getByTestId('original-merchant').textContent().catch(() => '')) || '';
  350 |     const od = (await q.getByTestId('original-date').textContent().catch(() => '')) || '';
  351 |     const ot = (await q.getByTestId('original-total').textContent().catch(() => '')) || '';
  352 |     await evidence(testInfo, '③ original-* on page', { om, od, ot });
  353 |     expect.soft(om, 'original-merchant ร้านตัวอย่าง').toContain('ร้านตัวอย่าง');
  354 |     expect.soft(/2026-11-18|18\s*พ\.ย\.\s*(2569|69)|18\/11\/(2026|2569)/.test(od), `original-date 2026-11-18 (got "${od}")`).toBe(true);
  355 |     expect.soft(ot, 'original-total 100.00').toContain('100.00');
  356 |     await shot(testInfo, q, '③ history U-03');
  357 | 
  358 |     const u03 = await apiAs(M_URL, 'U03');
  359 |     const h = await history(u03, id);
  360 |     await u03.dispose();
  361 |     await evidence(testInfo, '③ W17', h);
  362 |     const edits = (h.edits || []).map(editParts);
  363 |     if (h.original?.items?.find((x: any) => x.lineNo === 1)?.name === 'ข้าวสาร')
  364 |       pendingAP(testInfo, 'AP-06', 'ok-100 line 1 is already named "ข้าวสาร" by the mock, so step ① renames it to the same value; the plan expects 6 history rows assuming a real change (plan input issue, assertion kept as written)');
  365 |     expect.soft(edits.length, '6 edits (5 U-01 + 1 U-03)').toBe(6);
> 366 |     expect.soft(edits.filter((e: any) => e.actor.includes(PIM)).length, '5 edits by คุณพิมพ์').toBe(5);
      |                                                                                                ^ Error: 5 edits by คุณพิมพ์
  367 |     expect.soft(edits.filter((e: any) => e.actor.includes(KITTI)).length, '1 edit by คุณกิตติ').toBe(1);
  368 |     for (const [i, e] of edits.entries()) {
  369 |       expect.soft(e.old !== undefined && e.neu !== undefined, `edit ${i + 1} has old and new value`).toBe(true);
  370 |       expect.soft(e.actor, `edit ${i + 1} has editor`).not.toBe('');
  371 |       expect.soft(String(e.at ?? ''), `edit ${i + 1} has time`).not.toBe('');
  372 |     }
  373 |     const cur = h.current ?? (await getR(u01, id));
  374 |     expect.soft(cur.merchant, 'current merchant ร้านแก้ไข 2').toBe('ร้านแก้ไข 2');
  375 |     expect.soft(String(cur.receiptDate ?? '').slice(0, 10), 'current date 2026-11-17').toBe('2026-11-17');
  376 |     expect.soft(money(cur.total), 'current total 120.00').toBe(12000);
  377 |     const org = h.original ?? {};
  378 |     expect.soft(org.merchant, 'original merchant ร้านตัวอย่าง').toBe('ร้านตัวอย่าง');
  379 |     expect.soft(String(org.receiptDate ?? '').slice(0, 10), 'original date 2026-11-18').toBe('2026-11-18');
  380 |     expect.soft(money(org.total), 'original total 100.00').toBe(10000);
  381 |   } finally { await s1.context.close(); await s3.context.close(); await u01.dispose(); }
  382 | });
  383 | 
  384 | test('TC-3-07 ธงยอดไม่ตรงคิดจากค่าหลังแก้', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  385 |   await reset(M_URL);
  386 |   const u01 = await apiAs(M_URL, 'U01');
  387 |   const { ids: [id1, id2], batchId } = await uploadCL01(u01, ['ok-100__001.jpg', 'ok-100__002.jpg']);
  388 |   await waitReviewNoOpen(u01, batchId, [id1, id2]);
  389 | 
  390 |   const { context, page } = await pageAs(browser, M_URL, 'U01');
  391 |   const u02 = await apiAs(M_URL, 'U02'); // never opens the receipt
  392 |   try {
  393 |     // ① U-01 opens the review page, line 3 -> 23.99
  394 |     await openReceipt(page, id1);
  395 |     await page.getByTestId('item-price-input-3').fill('23.99');
  396 |     const sv = await saveOnPage(page, id1);
  397 |     await evidence(testInfo, '① W14 line3 23.99', sv);
  398 |     expect.soft(sv.status, '① save must succeed').toBeLessThan(300);
  399 |     await page.reload();
  400 |     await expect.soft(page.getByTestId('items-sum'), '① items-sum 98.99').toContainText('98.99');
  401 |     await expect.soft(page.getByTestId('flag-mismatch'), '① flag ยอดไม่ตรงรายการ shown (|98.99-100.00| = 1.01 > 1.00, AP-01)').toBeVisible();
  402 |     await shot(testInfo, page, '① after edit 23.99');
  403 |     const a = await getR(u01, id1);
  404 |     await evidence(testInfo, '① W12', a);
  405 |     expect.soft(money(a.itemsSum), '① itemsSum 98.99').toBe(9899);
  406 |     expect.soft(a.flags?.mismatch, '① flags.mismatch true (AP-01 provisional: current values)').toBe(true);
  407 |     expect.soft(a.flags?.flagged, '① flags.flagged true').toBe(true);
  408 | 
  409 |     // ② U-02 (never opened) sends a correct W15
  410 |     const c2 = await confirm(u02, id1);
  411 |     await evidence(testInfo, '② W15 by U-02 not opened', c2);
  412 |     expect.soft(c2.status >= 400 && c2.status < 500, `② must be rejected (got ${c2.status})`).toBe(true);
  413 |     const b = await getR(u01, id1);
  414 |     expect.soft(b.status, '② status stays review').toBe('review');
  415 | 
  416 |     // ③ U-01 reloads (opens every field) and confirms
  417 |     await page.reload();
  418 |     await expect(page.getByTestId('receipt-status')).toBeVisible();
  419 |     await viewAllFields(page);
  420 |     const c3 = await confirmOnPage(page, id1);
  421 |     expect.soft(c3, '③ confirm-button usable').not.toBeNull();
  422 |     if (c3) {
  423 |       await evidence(testInfo, '③ W15 by U-01 on page', c3);
  424 |       expect.soft(c3.status, '③ confirm must succeed').toBeLessThan(300);
  425 |     }
  426 |     const c = await getR(u01, id1);
  427 |     await evidence(testInfo, '③ W12', c);
  428 |     expect.soft(c.status, '③ status confirmed').toBe('confirmed');
  429 |     expect.soft(JSON.stringify(c.confirmedBy ?? ''), '③ confirmedBy คุณพิมพ์').toContain(PIM);
  430 |     await page.reload();
  431 |     await shot(testInfo, page, '③ confirmed __001');
  432 | 
  433 |     // ④ __002, line 3 -> 24.00 : 99.00 · diff 1.00 -> no flag
  434 |     await openReceipt(page, id2);
  435 |     await page.getByTestId('item-price-input-3').fill('24.00');
  436 |     const sv4 = await saveOnPage(page, id2);
  437 |     await evidence(testInfo, '④ W14 line3 24.00', sv4);
  438 |     expect.soft(sv4.status, '④ save must succeed').toBeLessThan(300);
  439 |     await page.reload();
  440 |     await expect.soft(page.getByTestId('items-sum'), '④ items-sum 99.00').toContainText('99.00');
  441 |     await expect.soft(page.getByTestId('flag-mismatch'), '④ no mismatch flag (diff 1.00)').toHaveCount(0);
  442 |     await shot(testInfo, page, '④ after edit 24.00');
  443 |     const d = await getR(u01, id2);
  444 |     await evidence(testInfo, '④ W12', d);
  445 |     expect.soft(money(d.itemsSum), '④ itemsSum 99.00').toBe(9900);
  446 |     expect.soft(d.flags?.mismatch, '④ flags.mismatch false').toBe(false);
  447 |   } finally { await context.close(); await u01.dispose(); await u02.dispose(); }
  448 | });
  449 | 
  450 | test('TC-3-08 หลังยืนยัน พนักงานแก้ไม่ได้ หัวหน้าเปิดกลับได้', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  451 |   await reset(M_URL);
  452 |   const u01 = await apiAs(M_URL, 'U01');
  453 |   const { ids: [id] } = await uploadCL01(u01, ['ok-100__001.jpg']);
  454 |   await waitStatus(u01, [id], ['review']);
  455 |   const c0 = await confirm(u01, id);
  456 |   await evidence(testInfo, 'confirm by U-01', c0);
  457 |   expect(c0.status, 'pre-step: U-01 confirms').toBeLessThan(300);
  458 | 
  459 |   const { context, page } = await pageAs(browser, M_URL, 'U03');
  460 |   try {
  461 |     // ① U-01 PATCH total 90.00
  462 |     const p1 = await u01.patch(`/api/receipts/${id}`, { data: { total: '90.00' } });
  463 |     const p1j = await p1.json().catch(() => ({}));
  464 |     await evidence(testInfo, '① PATCH by U-01', { status: p1.status(), json: p1j });
  465 |     expect.soft(p1.status(), '① PATCH after confirm must be 403').toBe(403);
  466 |     let r = await getR(u01, id);
```