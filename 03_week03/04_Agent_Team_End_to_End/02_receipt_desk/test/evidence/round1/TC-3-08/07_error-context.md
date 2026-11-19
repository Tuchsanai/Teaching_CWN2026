# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 53-review.spec.ts >> TC-3-08 หลังยืนยัน พนักงานแก้ไม่ได้ หัวหน้าเปิดกลับได้
- Location: tests\53-review.spec.ts:450:1

# Error details

```
Error: ① PATCH after confirm must be 403

expect(received).toBe(expected) // Object.is equality

Expected: 403
Received: 409
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
      - link "ค้างเกินกำหนด" [ref=f3e10] [cursor=pointer]:
        - /url: /overdue
      - link "สรุปรายเดือน" [ref=f3e11] [cursor=pointer]:
        - /url: /reports
      - link "เวลาตรวจ · GPU" [ref=f3e12] [cursor=pointer]:
        - /url: /insights
    - generic [ref=f3e13]:
      - generic [ref=f3e14]: คุณกิตติ
      - generic [ref=f3e15]: หัวหน้าทีมบัญชี
      - button "ออกจากระบบ" [ref=f3e16] [cursor=pointer]
  - main [ref=f3e17]:
    - generic [ref=f3e18]:
      - generic [ref=f3e19]:
        - generic [ref=f3e20]:
          - link "← คิวรอตรวจ" [ref=f3e21] [cursor=pointer]:
            - /url: /review
          - heading "ตรวจใบเสร็จ ok-100__001.jpg" [level=1] [ref=f3e22]
          - paragraph [ref=f3e23]:
            - text: ร้านข้าวแกงสมชาย · รับเมื่อ 19 พ.ย. 2569 17:16 · สถานะ
            - strong [ref=f3e24]: รอตรวจ
        - 'generic "NFR-09: เฉลี่ยต้องน้อยกว่า 120 วินาทีต่อใบ · เป้าหมายทีม ≤ 40 วินาที" [ref=f3e25]': เวลาตรวจ 0:00
      - generic [ref=f3e27]:
        - text: ✓ ใบปกติ — ตรวจยอดรวมเทียบกับรูปช่องเดียวแล้วยืนยันได้
        - generic [ref=f3e28]: · ความมั่นใจยอดรวม 0.9900
      - generic [ref=f3e29]:
        - generic [ref=f3e30]:
          - generic [ref=f3e31]:
            - button "ย่อรูป" [ref=f3e32] [cursor=pointer]: −
            - generic [ref=f3e33]: 100%
            - button "ขยายรูป" [ref=f3e34] [cursor=pointer]: +
            - button "พอดี" [ref=f3e35] [cursor=pointer]
            - button "หมุนรูป" [ref=f3e36] [cursor=pointer]: ⟳
            - link "เปิดรูปในแท็บใหม่ ↗" [ref=f3e37] [cursor=pointer]:
              - /url: /api/receipts/953fc3a0-c416-461f-8200-e8b6f92d1bdf/image
          - img "รูปใบเสร็จ ok-100__001.jpg" [ref=f3e39]
        - generic [ref=f3e40]:
          - generic [ref=f3e41]:
            - generic [ref=f3e42]:
              - generic [ref=f3e43]: ชื่อร้าน
              - generic [ref=f3e44]: "ระบบอ่าน: ร้านตัวอย่าง"
            - textbox "ชื่อร้าน" [ref=f3e45]: ร้านตัวอย่าง
          - generic [ref=f3e46]:
            - generic [ref=f3e47]:
              - generic [ref=f3e48]: วันที่บนใบ
              - generic [ref=f3e49]: "ระบบอ่าน: 18 พ.ย. 2569 (2026-11-18)"
            - textbox "วันที่บนใบ" [ref=f3e50]: 2026-11-18
          - generic [ref=f3e51]:
            - generic [ref=f3e52]:
              - generic [ref=f3e53]: รายการสินค้าและราคา
              - generic [ref=f3e54]:
                - text: ผลรวมรายการ
                - strong [ref=f3e55]: "100.00"
                - text: บาท
                - generic [ref=f3e56]: · ต่างจากยอดรวม 0.00
            - table [ref=f3e57]:
              - rowgroup [ref=f3e58]:
                - row [ref=f3e59]:
                  - columnheader "#" [ref=f3e60]
                  - columnheader "รายการ" [ref=f3e61]
                  - columnheader "ราคา" [ref=f3e62]
                  - columnheader [ref=f3e63]
              - rowgroup [ref=f3e64]:
                - row [ref=f3e65]:
                  - cell "1" [ref=f3e66]
                  - cell [ref=f3e67]:
                    - textbox "ชื่อรายการบรรทัด 1" [ref=f3e68]: ข้าวสาร
                  - cell [ref=f3e69]:
                    - textbox "ราคาบรรทัด 1" [ref=f3e70]: "45.00"
                  - cell [ref=f3e71]:
                    - button "ลบ" [ref=f3e72] [cursor=pointer]
                - row [ref=f3e73]:
                  - cell "2" [ref=f3e74]
                  - cell [ref=f3e75]:
                    - textbox "ชื่อรายการบรรทัด 2" [ref=f3e76]: น้ำมันพืช
                  - cell [ref=f3e77]:
                    - textbox "ราคาบรรทัด 2" [ref=f3e78]: "30.00"
                  - cell [ref=f3e79]:
                    - button "ลบ" [ref=f3e80] [cursor=pointer]
                - row [ref=f3e81]:
                  - cell "3" [ref=f3e82]
                  - cell [ref=f3e83]:
                    - textbox "ชื่อรายการบรรทัด 3" [ref=f3e84]: น้ำตาลทราย
                  - cell [ref=f3e85]:
                    - textbox "ราคาบรรทัด 3" [ref=f3e86]: "25.00"
                  - cell [ref=f3e87]:
                    - button "ลบ" [ref=f3e88] [cursor=pointer]
            - button "+ เพิ่มรายการ" [ref=f3e89] [cursor=pointer]
          - generic [ref=f3e90]:
            - generic [ref=f3e91]:
              - generic [ref=f3e92]: ยอดรวม (บาท)
              - generic [ref=f3e93]: "ระบบอ่าน: 100.00"
            - textbox "ยอดรวม" [ref=f3e94]: "100.00"
          - generic [ref=f3e95]:
            - generic [ref=f3e96]: หมวดรายจ่าย
            - combobox "หมวดรายจ่าย" [ref=f3e98]:
              - option "— เลือกหมวด —"
              - option "วัตถุดิบ"
              - option "ค่าแก๊ส"
              - option "ค่าน้ำแข็ง"
              - option "อื่น ๆ" [selected]
          - generic [ref=f3e99]:
            - generic [ref=f3e100] [cursor=pointer]:
              - checkbox "เทียบยอดรวมกับรูปแล้ว" [ref=f3e101]
              - text: เทียบยอดรวมกับรูปแล้ว
            - generic [ref=f3e102]:
              - button "บันทึก" [disabled]
              - button "ยืนยัน" [disabled]
              - button "ข้าม → ใบถัดไป" [ref=f3e103] [cursor=pointer]
            - list [ref=f3e104]:
              - listitem [ref=f3e105]: ติ๊ก "เทียบยอดรวมกับรูปแล้ว"
            - paragraph [ref=f3e106]: Enter = ช่องถัดไป · Ctrl/⌘+Enter = ยืนยัน · Ctrl/⌘+S = บันทึก · Alt+→ = ใบถัดไป
          - generic [ref=f3e107]:
            - button "ซ่อนประวัติการแก้" [active] [ref=f3e108] [cursor=pointer]
            - generic [ref=f3e109]:
              - paragraph [ref=f3e110]: "ค่าที่ระบบอ่านเดิม: ร้าน ร้านตัวอย่าง · วันที่ 2026-11-18 · ยอดรวม 100.00"
              - table [ref=f3e111]:
                - rowgroup [ref=f3e112]:
                  - row [ref=f3e113]:
                    - columnheader "#" [ref=f3e114]
                    - columnheader "ช่อง" [ref=f3e115]
                    - columnheader "ค่าเดิม" [ref=f3e116]
                    - columnheader "ค่าใหม่" [ref=f3e117]
                    - columnheader "ผู้แก้" [ref=f3e118]
                    - columnheader "เวลา" [ref=f3e119]
                - rowgroup [ref=f3e120]:
                  - row [ref=f3e121]:
                    - cell "1" [ref=f3e122]
                    - cell "หมวดรายจ่าย" [ref=f3e123]
                    - cell "—" [ref=f3e124]
                    - cell "อื่น ๆ" [ref=f3e125]
                    - cell "คุณพิมพ์" [ref=f3e126]
                    - cell "19 พ.ย. 2569 17:16" [ref=f3e127]
                  - row [ref=f3e128]:
                    - cell "2" [ref=f3e129]
                    - cell "สถานะ" [ref=f3e130]
                    - cell "confirmed" [ref=f3e131]
                    - cell "review" [ref=f3e132]
                    - cell "คุณกิตติ" [ref=f3e133]
                    - cell "19 พ.ย. 2569 17:16" [ref=f3e134]
              - group [ref=f3e135]:
                - generic "การเปลี่ยนสถานะ 5 ครั้ง" [ref=f3e136]
  - alert [ref=f3e137]
```

# Test source

```ts
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
> 465 |     expect.soft(p1.status(), '① PATCH after confirm must be 403').toBe(403);
      |                                                                   ^ Error: ① PATCH after confirm must be 403
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