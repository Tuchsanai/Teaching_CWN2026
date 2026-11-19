# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 55-queue.spec.ts >> TC-5-07 ค้างเกิน 120 นาที
- Location: tests\55-queue.spec.ts:494:1

# Error details

```
Error: ② รายการมี 1 ใบ (TD-BR13-c)

expect(received).toBe(expected) // Object.is equality

Expected: 1
Received: 2
```

```
Error: ② ใบ 120 นาทีไม่อยู่ (120 ไม่เกิน 120)

expect(received).not.toContain(expected) // indexOf

Expected value: not "1d12727c-6d73-4500-a44f-20d185ab20a9"
Received array:     ["2b8e8bfb-6bed-420b-adbd-503600570bb1", "1d12727c-6d73-4500-a44f-20d185ab20a9"]
```

# Page snapshot

```yaml
- generic [active] [ref=f2e1]:
  - banner [ref=f2e2]:
    - link "ReceiptDesk" [ref=f2e3] [cursor=pointer]:
      - /url: /
    - navigation [ref=f2e5]:
      - link "อัปโหลดชุด" [ref=f2e6] [cursor=pointer]:
        - /url: /upload
      - link "ชุดใบเสร็จ" [ref=f2e7] [cursor=pointer]:
        - /url: /batches
      - link "รายการใบ" [ref=f2e8] [cursor=pointer]:
        - /url: /receipts
      - link "อ่านไม่ได้" [ref=f2e9] [cursor=pointer]:
        - /url: /unreadable
      - link "ค้างเกินกำหนด 2" [ref=f2e10] [cursor=pointer]:
        - /url: /overdue
        - text: ค้างเกินกำหนด
        - generic "งานปกติค้างเกิน 120 นาที 2 ใบ" [ref=f2e11]: "2"
      - link "สรุปรายเดือน" [ref=f2e12] [cursor=pointer]:
        - /url: /reports
      - link "เวลาตรวจ · GPU" [ref=f2e13] [cursor=pointer]:
        - /url: /insights
    - generic [ref=f2e14]:
      - generic [ref=f2e15]: คุณกิตติ
      - generic [ref=f2e16]: หัวหน้าทีมบัญชี
      - button "ออกจากระบบ" [ref=f2e17] [cursor=pointer]
  - main [ref=f2e18]:
    - heading "งานปกติค้างเกินกำหนด" [level=1] [ref=f2e19]
    - paragraph [ref=f2e20]: ใบของงานปกติที่ยังรออ่านหรือกำลังอ่าน และรับมาแล้วเกิน 120 นาที เรียงจากรอนานที่สุด
    - status [ref=f2e21]: มีงานปกติค้างเกินกำหนด 2 ใบ
    - paragraph [ref=f2e22]:
      - text: ค้างเกินกำหนด
      - strong [ref=f2e23]: "2"
      - text: ใบ
    - table [ref=f2e24]:
      - rowgroup [ref=f2e25]:
        - row [ref=f2e26]:
          - columnheader "รับเมื่อ" [ref=f2e27]
          - columnheader "ลูกค้า" [ref=f2e28]
          - columnheader "ไฟล์" [ref=f2e29]
          - columnheader "สถานะ" [ref=f2e30]
          - columnheader "รอมาแล้ว (นาที)" [ref=f2e31]
          - columnheader [ref=f2e32]
      - rowgroup [ref=f2e33]:
        - row [ref=f2e34]:
          - cell "19/11/2569 15:13" [ref=f2e35]
          - cell "ร้านข้าวแกงสมชาย" [ref=f2e36]
          - cell "TD-BR13-c.jpg" [ref=f2e37]
          - cell "รออ่าน" [ref=f2e38]
          - cell "121" [ref=f2e39]
          - cell [ref=f2e40]:
            - link "เปิดชุด" [ref=f2e41] [cursor=pointer]:
              - /url: /batches/8e81ba41-7956-4652-b072-c40e69d16843
        - row [ref=f2e42]:
          - cell "19/11/2569 15:14" [ref=f2e43]
          - cell "ร้านข้าวแกงสมชาย" [ref=f2e44]
          - cell "TD-BR13-b.jpg" [ref=f2e45]
          - cell "รออ่าน" [ref=f2e46]
          - cell "120" [ref=f2e47]
          - cell [ref=f2e48]:
            - link "เปิดชุด" [ref=f2e49] [cursor=pointer]:
              - /url: /batches/37b56bfd-e076-4ee9-8236-3cff57fb8c5b
  - alert [ref=f2e50]
```

# Test source

```ts
  434 |     await evidence(testInfo, '② W14 save total 55.50', save2);
  435 |     expect.soft(save2.status, '② บันทึก 55.50 สำเร็จ').toBe(200);
  436 |     await expect.soft(page.getByTestId('items-sum'), '② ผลรวมรายการ 30.00 + 25.50 = 55.50').toHaveText(/55\.50/);
  437 |     const itemsDiff = await page.getByTestId('items-diff').innerText().catch(() => '');
  438 |     if (itemsDiff) expect.soft(itemsDiff, '② ผลต่าง 0').toMatch(/0\.00/);
  439 |     if (!(await chk.isChecked())) await chk.check();
  440 |     let conf2 = await clickAndCapture(page, 'confirm-button', 'POST', `/api/receipts/${id}/confirm`);
  441 |     if (!conf2.sent) {
  442 |       const blockers = await page.getByTestId('confirm-blockers').innerText().catch(() => '');
  443 |       await evidence(testInfo, '② page blocked confirm (confirm-blockers)', blockers);
  444 |       const api2 = await confirm(api, id);
  445 |       conf2 = { sent: true, status: api2.status, json: api2.json };
  446 |     }
  447 |     await evidence(testInfo, '② W15 confirm', conf2);
  448 |     expect.soft(conf2.status, '② ยืนยันได้').toBe(200);
  449 |     await expect.soft(page.getByTestId('receipt-status'), '② สถานะยืนยันแล้ว (หน้า)').toHaveText(/ยืนยันแล้ว/);
  450 |     await shot(testInfo, page, '② confirmed 55.50');
  451 |     const r2 = (await receipt(api, id)).receipt;
  452 |     expect.soft(r2.status, '② สถานะยืนยันแล้ว').toBe('confirmed');
  453 |     await page.goto('/unreadable');
  454 |     await expect.soft(page.getByTestId('unreadable-count'), '② /unreadable นับ 1 → 0').toHaveText(/^\s*0\s*$/);
  455 |     await expect.soft(page.getByTestId(`unreadable-row-${id}`), '② ใบหายจากรายการ /unreadable').toHaveCount(0);
  456 |     await shot(testInfo, page, '② /unreadable empty');
  457 | 
  458 |     // ③ open the receipt again
  459 |     await page.goto(`/receipts/${id}`);
  460 |     await expect.soft(page.getByTestId('field-merchant-input'), '③ ร้าน').toHaveValue('ร้านทดสอบ');
  461 |     await expect.soft(page.getByTestId('field-date-input'), '③ วันที่').toHaveValue('2026-11-19');
  462 |     await expect.soft(page.getByTestId('item-name-input-1'), '③ รายการ 1').toHaveValue('น้ำแข็ง');
  463 |     await expect.soft(page.getByTestId('item-price-input-1'), '③ ราคา 1').toHaveValue(/^30(\.00)?$/);
  464 |     await expect.soft(page.getByTestId('item-name-input-2'), '③ รายการ 2').toHaveValue('ถ่าน');
  465 |     await expect.soft(page.getByTestId('item-price-input-2'), '③ ราคา 2').toHaveValue(/^25\.50?$/);
  466 |     await expect.soft(page.getByTestId('field-total-input'), '③ ยอดรวม').toHaveValue(/^55\.50?$/);
  467 |     await shot(testInfo, page, '③ reopened receipt');
  468 |     const r3 = (await receipt(api, id)).receipt;
  469 |     await evidence(testInfo, '③ W12', r3);
  470 |     expect.soft(r3.merchant, '③ W12 ร้าน').toBe('ร้านทดสอบ');
  471 |     expect.soft(r3.receiptDate, '③ W12 วันที่').toBe('2026-11-19');
  472 |     expect.soft(Number(r3.total).toFixed(2), '③ W12 ยอด 55.50').toBe('55.50');
  473 |     const items = (r3.items || []).filter((i: any) => !i.removed).map((i: any) => ({ name: i.name, price: Number(i.price).toFixed(2) }));
  474 |     expect.soft(items, '③ W12 2 รายการพร้อมราคา').toEqual([{ name: 'น้ำแข็ง', price: '30.00' }, { name: 'ถ่าน', price: '25.50' }]);
  475 |   } finally {
  476 |     await context.close();
  477 |     await api.dispose();
  478 |   }
  479 | });
  480 | 
  481 | /** Click a button and capture the matching request it sends (sent=false when disabled / nothing sent within 10 s). */
  482 | async function clickAndCapture(page: Page, testid: string, method: string, urlPart: string): Promise<{ sent: boolean; status: number | null; json: any }> {
  483 |   const btn = page.getByTestId(testid);
  484 |   if (!(await btn.isEnabled().catch(() => false))) return { sent: false, status: null, json: null };
  485 |   const respP = page.waitForResponse(r => r.request().method() === method && new URL(r.url()).pathname === urlPart, { timeout: 10_000 }).catch(() => null);
  486 |   await btn.click();
  487 |   const resp = await respP;
  488 |   if (!resp) return { sent: false, status: null, json: null };
  489 |   await page.waitForLoadState('networkidle').catch(() => undefined);
  490 |   return { sent: true, status: resp.status(), json: await resp.json().catch(() => ({})) };
  491 | }
  492 | 
  493 | // ================================================================= TC-5-07
  494 | test('TC-5-07 ค้างเกิน 120 นาที', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  495 |   await reset(M_URL, { overdue: true });
  496 |   const t = Date.now();
  497 |   const lead = await apiAs(M_URL, 'U03');
  498 |   try {
  499 |     // ① W11: the 4 receipts the reset created (TD-BR13-a … d)
  500 |     const j = await (await lead.get('/api/receipts?limit=1000')).json();
  501 |     const now = Date.now();
  502 |     const made = (j.receipts || []).filter((r: any) => !/^S-0[1-8]\./.test(r.fileName))
  503 |       .map((r: any) => ({ id: r.id, fileName: r.fileName, status: r.status, ageMin: Math.floor((now - Date.parse(r.acceptedAt)) / 60_000), overdue: r.overdue }));
  504 |     await evidence(testInfo, '① W11 receipts made by reset {overdue:true}', made);
  505 |     expect(made.length, '① รีเซ็ตสร้าง 4 ใบ (TD-BR13-a – d)').toBe(4);
  506 |     const find = (age: number, status: string) => made.find((r: any) => r.ageMin === age && r.status === status);
  507 |     const a = find(119, 'queued'), b = find(120, 'queued'), c = find(121, 'queued'), d = find(121, 'review');
  508 |     expect.soft(!!a, '① TD-BR13-a อายุ 119 รออ่าน').toBe(true);
  509 |     expect.soft(!!b, '① TD-BR13-b อายุ 120 รออ่าน').toBe(true);
  510 |     expect.soft(!!c, '① TD-BR13-c อายุ 121 รออ่าน').toBe(true);
  511 |     expect.soft(!!d, '① TD-BR13-d อายุ 121 รอตรวจ').toBe(true);
  512 | 
  513 |     // ② within t + 59 s U-03 opens /overdue
  514 |     const { context, page } = await pageAs(browser, M_URL, 'U03');
  515 |     try {
  516 |       await expect.soft(page.getByTestId('nav-overdue'), '② หัวหน้าเห็นการแจ้ง (เมนูค้างเกินกำหนด)').toBeVisible();
  517 |       await evidence(testInfo, '② nav-overdue text (U-03)', await page.getByTestId('nav-overdue').innerText().catch(() => ''));
  518 |       await page.goto('/overdue');
  519 |       await expect(page.getByTestId('overdue-table')).toBeVisible();
  520 |       const countText = await page.getByTestId('overdue-count').innerText();
  521 |       const rowIds = await page.locator('[data-testid^="overdue-row-"]').evaluateAll(es => es.map(e => (e.getAttribute('data-testid') || '').replace('overdue-row-', '')));
  522 |       const minutes: Record<string, string> = {};
  523 |       for (const rid of rowIds) minutes[rid] = await page.getByTestId(`overdue-minutes-${rid}`).innerText().catch(() => '');
  524 |       const elapsed = Date.now() - t;
  525 |       await shot(testInfo, page, '② /overdue (U-03)');
  526 |       await evidence(testInfo, '② /overdue', { elapsedMsSinceReset: elapsed, overdueCount: countText, rows: rowIds, minutes });
  527 |       expect.soft(elapsed, '② ตรวจภายใน t + 59 วินาที (AP-04)').toBeLessThanOrEqual(59_000);
  528 |       expect.soft(num(countText), '② รายการมี 1 ใบ (TD-BR13-c)').toBe(1);
  529 |       if (c) {
  530 |         expect.soft(rowIds, '② ใบ TD-BR13-c อยู่ในรายการ').toContain(c.id);
  531 |         expect.soft(num(minutes[c.id]), '② overdue-minutes = 121').toBe(121);
  532 |       }
  533 |       if (a) expect.soft(rowIds, '② ใบ 119 นาทีไม่อยู่').not.toContain(a.id);
> 534 |       if (b) expect.soft(rowIds, '② ใบ 120 นาทีไม่อยู่ (120 ไม่เกิน 120)').not.toContain(b.id);
      |                                                                                ^ Error: ② ใบ 120 นาทีไม่อยู่ (120 ไม่เกิน 120)
  535 |       if (d) expect.soft(rowIds, '② ใบ 121 นาทีที่มีผลแล้วไม่อยู่').not.toContain(d.id);
  536 |       pendingAP(testInfo, 'AP-04', `ตรวจที่ ${Math.round(elapsed / 1000)} s หลังรีเซ็ต · overdue-count=${countText.trim()} · แถว=${JSON.stringify(minutes)} · ใบ 120 นาที ${b && rowIds.includes(b.id) ? 'อยู่' : 'ไม่อยู่'}ในรายการ`);
  537 |     } finally {
  538 |       await context.close();
  539 |     }
  540 |     pendingAP(testInfo, 'AP-05', 'ไม่มีใบด่วนอายุเกิน 120 นาทีในข้อมูลรีเซ็ต · กรณีใบด่วนรอข้อมูลเพิ่มใน TEST-DATA');
  541 | 
  542 |     // ③ U-01 opens /overdue -> refused
  543 |     const u1 = await pageAs(browser, M_URL, 'U01');
  544 |     try {
  545 |       await u1.page.goto('/overdue');
  546 |       await u1.page.waitForLoadState('networkidle').catch(() => undefined);
  547 |       await shot(testInfo, u1.page, '③ /overdue (U-01)');
  548 |       await evidence(testInfo, '③ U-01 url after /overdue', u1.page.url());
  549 |       await expect.soft(u1.page.getByTestId('overdue-table'), '③ U-01 ถูกปฏิเสธ: ไม่เห็นตารางค้างเกินกำหนด').toHaveCount(0);
  550 |       await expect.soft(u1.page.locator('[data-testid^="overdue-row-"]'), '③ U-01 ไม่เห็นแถวค้าง').toHaveCount(0);
  551 |     } finally {
  552 |       await u1.context.close();
  553 |     }
  554 |   } finally {
  555 |     await lead.dispose();
  556 |   }
  557 | });
  558 | 
  559 | // ================================================================= TC-5-08 ★
  560 | test('TC-5-08 ★ ดับ Worker ที่กำลังถือใบกลางงาน 100 ใบ', { tag: ['@P1', '@R'] }, async ({}, testInfo) => {
  561 |   testInfo.annotations.push({ type: 'blocked', description: 'รอบปล่อยรุ่น ★: ต้องใช้ใบจริง 100 ไฟล์ เกินงบรอบปกติ/งบของขั้นนี้ (120 ใบ) และต้องได้อนุมัติหัวหน้าทีมทดสอบ' });
  562 |   test.skip(true, 'รอบปล่อยรุ่น ★ เท่านั้น (ใบจริง 100 ไฟล์ · ต้องอนุมัติหัวหน้าทีมทดสอบ)');
  563 | });
  564 | 
  565 | // ================================================================= TC-5-09
  566 | test('TC-5-09 ฝั่ง AI ล่มทั้งหมด แล้วกลับมา', { tag: ['@P1', '@R'] }, async ({ browser }, testInfo) => {
  567 |   // E6: real files present · reset :3420 · W23 pending 0 · urgent today 0 · workers alive 2
  568 |   const gt = JSON.parse(fs.readFileSync(path.join(REAL_IMAGES, 'ground_truth.json'), 'utf8'));
  569 |   const gtFiles: string[] = (Array.isArray(gt) ? gt : gt.items || gt.receipts || Object.values(gt)).map((x: any) => x.file).filter(Boolean);
  570 |   const missing = gtFiles.filter(f => !fs.existsSync(path.join(REAL_IMAGES, f)));
  571 |   expect(missing, 'E6: รูปจริงครบตาม ground_truth.json').toEqual([]);
  572 |   await reset(R_URL);
  573 |   const api = await apiAs(R_URL, 'U01');
  574 |   try {
  575 |     const q0 = await queue(api);
  576 |     await evidence(testInfo, 'E6 W23', q0);
  577 |     expect(q0.normal?.pending, 'E6: ใบงานปกติค้าง 0').toBe(0);
  578 |     expect(q0.urgent?.usedToday, 'E6: งานด่วนวันนี้ 0 / 5').toBe(0);
  579 |     expect(q0.workers?.alive, 'E6: workersAlive 2').toBe(2);
  580 |     await evidence(testInfo, 'E6 gpu.sh status all', gpu('status all'));
  581 | 
  582 |     const cl = await clientId(api, 'CL-01');
  583 |     const real = ['te0000.jpg', 'te0001.jpg', 'te0002.jpg'].map(f => path.join(REAL_IMAGES, f));
  584 |     let ids: string[] = [];
  585 |     let batchId = '';
  586 |     try {
  587 |       // ① stop gateway
  588 |       await evidence(testInfo, '① gpu.sh stop gateway', gpu('stop gateway'));
  589 |       // ② U-01 uploads 3 real files
  590 |       const up = await upload(api, { clientId: cl, files: real, real: true });
  591 |       await evidence(testInfo, '② W7 response', up.json);
  592 |       expect(W7_OK, `② รับ 3 ใบ (HTTP ${up.status})`).toContain(up.status);
  593 |       expect.soft(up.json.accepted, '② รับ 3 ใบ').toBe(3);
  594 |       ids = Object.values(idsByName(up.json));
  595 |       batchId = up.json.batchId;
  596 |       expect(ids.length, '② จด 3 ID').toBe(3);
  597 | 
  598 |       // web still opens every page
  599 |       const { context, page } = await pageAs(browser, R_URL, 'U01');
  600 |       try {
  601 |         for (const p of ['/upload', '/batches', `/batches/${batchId}`, '/receipts', `/receipts/${ids[0]}`, '/unreadable', '/reports']) {
  602 |           const resp = await page.goto(p);
  603 |           expect.soft(resp?.status() ?? 0, `② หน้า ${p} เปิดได้`).toBeLessThan(400);
  604 |           await expect.soft(page.getByTestId('nav-user-name'), `② หน้า ${p} แสดงผล`).toBeVisible();
  605 |           if (p === `/batches/${batchId}`) await shot(testInfo, page, '② batch page while gateway is down');
  606 |         }
  607 |       } finally {
  608 |         await context.close();
  609 |       }
  610 |       const h = await api.get('/api/health');
  611 |       const hj = await h.json().catch(() => ({}));
  612 |       await evidence(testInfo, '② /api/health while gateway is down', hj);
  613 |       expect.soft(h.status(), '② /api/health 200 (ai.reachable = false ได้)').toBe(200);
  614 | 
  615 |       // wait 3 minutes; all 3 must stay queued
  616 |       const seen = new Set<string>();
  617 |       const end = Date.now() + 180_000;
  618 |       while (Date.now() < end) {
  619 |         for (const id of ids) seen.add((await receipt(api, id)).receipt?.status);
  620 |         await sleep(15_000);
  621 |       }
  622 |       const after3 = await Promise.all(ids.map(async id => (await receipt(api, id)).receipt));
  623 |       await evidence(testInfo, '② statuses after 3 min', { seen: [...seen], receipts: after3.map(r => ({ fileName: r.fileName, status: r.status, attempts: r.attempts })) });
  624 |       for (const r of after3) expect.soft(r.status, `② ${r.fileName} คงสถานะ "รออ่าน"`).toBe('queued');
  625 |       const rec = await reconcile(api);
  626 |       await evidence(testInfo, '② W20', rec);
  627 |       expect.soft(Number(rec.diff), '② ยอดตรวจนับผลต่าง 0').toBe(0);
  628 |     } finally {
  629 |       // ③ gateway back (always)
  630 |       await evidence(testInfo, '③ gpu.sh start gateway', gpu('start gateway'));
  631 |     }
  632 | 
  633 |     // ③ ≤ 10 min: all 3 are read by themselves (nobody clicks anything)
  634 |     const done = await waitStatus(api, ids, ['review', 'unreadable'], 600_000).catch(async e => {
```