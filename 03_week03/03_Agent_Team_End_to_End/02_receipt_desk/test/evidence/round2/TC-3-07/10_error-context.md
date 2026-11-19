# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 53-review.spec.ts >> TC-3-07 ธงยอดไม่ตรงคิดจากค่าหลังแก้
- Location: tests\53-review.spec.ts:384:1

# Error details

```
Error: ① flag ยอดไม่ตรงรายการ shown (|98.99-100.00| = 1.01 > 1.00, AP-01)

expect(locator).toBeVisible() failed

Locator: getByTestId('flag-mismatch')
Expected: visible
Timeout: 15000ms
Error: element(s) not found

Call log:
  - ① flag ยอดไม่ตรงรายการ shown (|98.99-100.00| = 1.01 > 1.00, AP-01) getByTestId('flag-mismatch') with timeout 15000ms
  - waiting for getByTestId('flag-mismatch')

```

```yaml
- banner:
  - link "ReceiptDesk":
    - /url: /
  - navigation:
    - link "อัปโหลดชุด":
      - /url: /upload
    - link "ชุดใบเสร็จ":
      - /url: /batches
    - link "รายการใบ":
      - /url: /receipts
    - link "อ่านไม่ได้":
      - /url: /unreadable
    - link "สรุปรายเดือน":
      - /url: /reports
  - text: คุณพิมพ์ พนักงานบัญชี
  - button "ออกจากระบบ"
- main:
  - link "← คิวรอตรวจ":
    - /url: /review
  - heading "ตรวจใบเสร็จ ok-100__001.jpg" [level=1]
  - paragraph:
    - text: ร้านข้าวแกงสมชาย · รับเมื่อ 19 พ.ย. 2569 17:23 · สถานะ
    - strong: รอตรวจ
  - text: เวลาตรวจ 0:14 ✓ ใบปกติ — ตรวจยอดรวมเทียบกับรูปช่องเดียวแล้วยืนยันได้ · ความมั่นใจยอดรวม 0.9900
  - button "ย่อรูป": −
  - text: 100%
  - button "ขยายรูป": +
  - button "พอดี"
  - button "หมุนรูป": ⟳
  - link "เปิดรูปในแท็บใหม่ ↗":
    - /url: /api/receipts/f3bf87c1-4286-4ba6-bec4-0062806b775f/image
  - img "รูปใบเสร็จ ok-100__001.jpg"
  - text: "ชื่อร้าน ระบบอ่าน: ร้านตัวอย่าง"
  - textbox "ชื่อร้าน": ร้านตัวอย่าง
  - text: "วันที่บนใบ ระบบอ่าน: 18 พ.ย. 2569 (2026-11-18)"
  - textbox "วันที่บนใบ": 2026-11-18
  - text: รายการสินค้าและราคา ผลรวมรายการ
  - strong: "98.99"
  - text: บาท · ต่างจากยอดรวม -1.01 (เกิน 1.00 บาท)
  - table:
    - rowgroup:
      - row "# รายการ ราคา":
        - columnheader "#"
        - columnheader "รายการ"
        - columnheader "ราคา"
        - columnheader
    - rowgroup:
      - row "1 ข้าวสาร 45.00 ลบ":
        - cell "1"
        - cell "ข้าวสาร":
          - textbox "ชื่อรายการบรรทัด 1": ข้าวสาร
        - cell "45.00":
          - textbox "ราคาบรรทัด 1": "45.00"
        - cell "ลบ":
          - button "ลบ"
      - row "2 น้ำมันพืช 30.00 ลบ":
        - cell "2"
        - cell "น้ำมันพืช":
          - textbox "ชื่อรายการบรรทัด 2": น้ำมันพืช
        - cell "30.00":
          - textbox "ราคาบรรทัด 2": "30.00"
        - cell "ลบ":
          - button "ลบ"
      - 'row "3 น้ำตาลทราย 23.99 ระบบอ่าน: 25.00 ลบ"':
        - cell "3"
        - cell "น้ำตาลทราย":
          - textbox "ชื่อรายการบรรทัด 3": น้ำตาลทราย
        - 'cell "23.99 ระบบอ่าน: 25.00"':
          - textbox "ราคาบรรทัด 3": "23.99"
          - text: "ระบบอ่าน: 25.00"
        - cell "ลบ":
          - button "ลบ"
  - button "+ เพิ่มรายการ"
  - text: "ยอดรวม (บาท) ระบบอ่าน: 100.00"
  - textbox "ยอดรวม": "100.00"
  - text: หมวดรายจ่าย
  - combobox "หมวดรายจ่าย":
    - option "— เลือกหมวด —" [selected]
    - option "วัตถุดิบ"
    - option "ค่าแก๊ส"
    - option "ค่าน้ำแข็ง"
    - option "อื่น ๆ"
  - checkbox "เทียบยอดรวมกับรูปแล้ว"
  - text: เทียบยอดรวมกับรูปแล้ว
  - button "บันทึก" [disabled]
  - button "ยืนยัน" [disabled]
  - button "ข้าม → ใบถัดไป"
  - list:
    - listitem: ติ๊ก "เทียบยอดรวมกับรูปแล้ว"
    - listitem: เลือกหมวดรายจ่าย
  - paragraph: Enter = ช่องถัดไป · Ctrl/⌘+Enter = ยืนยัน · Ctrl/⌘+S = บันทึก · Alt+→ = ใบถัดไป
  - button "ดูค่าเดิมและประวัติการแก้"
- alert
```

```
Error: ① flags.mismatch true (AP-01 provisional: current values)

expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

```
Error: ① flags.flagged true

expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

```
Error: ② must be rejected (got 200)

expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

```
Error: ② status stays review

expect(received).toBe(expected) // Object.is equality

Expected: "review"
Received: "confirmed"
```

```
Error: ③ confirm-button usable

expect(received).not.toBeNull()

Received: null
```

```
Error: ③ confirmedBy คุณพิมพ์

expect(received).toContain(expected) // indexOf

Expected substring: "พิมพ์"
Received string:    "\"คุณแนน\""
```

# Test source

```ts
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
  366 |     expect.soft(edits.filter((e: any) => e.actor.includes(PIM)).length, '5 edits by คุณพิมพ์').toBe(5);
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
> 429 |     expect.soft(JSON.stringify(c.confirmedBy ?? ''), '③ confirmedBy คุณพิมพ์').toContain(PIM);
      |                                                                                ^ Error: ③ confirmedBy คุณพิมพ์
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
  467 |     expect.soft(money(r.total), '① total stays 100.00').toBe(10000);
  468 | 
  469 |     // ② U-01 reopen
  470 |     const p2 = await u01.post(`/api/receipts/${id}/reopen`);
  471 |     const p2j = await p2.json().catch(() => ({}));
  472 |     await evidence(testInfo, '② reopen by U-01', { status: p2.status(), json: p2j });
  473 |     expect.soft(p2.status(), '② reopen by staff must be 403').toBe(403);
  474 |     r = await getR(u01, id);
  475 |     expect.soft(r.status, '② status stays confirmed').toBe('confirmed');
  476 |     expect.soft(money(r.total), '② total stays 100.00').toBe(10000);
  477 | 
  478 |     // ③ U-03 presses reopen-button
  479 |     await openReceipt(page, id);
  480 |     const respP = page.waitForResponse(x => x.url().includes(`/api/receipts/${id}/reopen`) && x.request().method() === 'POST', { timeout: 20_000 });
  481 |     await page.getByTestId('reopen-button').click();
  482 |     const resp = await respP;
  483 |     await evidence(testInfo, '③ reopen by U-03', { status: resp.status(), json: await resp.json().catch(() => ({})) });
  484 |     expect.soft(resp.status(), '③ reopen must succeed').toBeLessThan(300);
  485 |     await page.reload();
  486 |     await page.getByTestId('history-button').click().catch(() => {});
  487 |     await shot(testInfo, page, '③ after reopen');
  488 | 
  489 |     r = await getR(u01, id);
  490 |     expect.soft(r.status, '③ status back to review (รอตรวจ)').toBe('review');
  491 |     const h = await history(u01, id);
  492 |     await evidence(testInfo, '③ W17', h);
  493 |     const ev: any[] = h.events || [];
  494 |     const conf = ev.find(e => e.to === 'confirmed');
  495 |     const reo = ev.find(e => e.from === 'confirmed' && e.to === 'review');
  496 |     expect.soft(conf, 'history has the confirm event').toBeTruthy();
  497 |     expect.soft(JSON.stringify(conf?.actor ?? ''), 'confirm by คุณพิมพ์').toContain(PIM);
  498 |     expect.soft(String(conf?.at ?? ''), 'confirm time').not.toBe('');
  499 |     expect.soft(reo, 'history has the reopen event').toBeTruthy();
  500 |     expect.soft(JSON.stringify(reo?.actor ?? ''), 'reopen by คุณกิตติ').toContain(KITTI);
  501 |     expect.soft(String(reo?.at ?? ''), 'reopen time').not.toBe('');
  502 |   } finally { await context.close(); await u01.dispose(); }
  503 | });
  504 | 
```