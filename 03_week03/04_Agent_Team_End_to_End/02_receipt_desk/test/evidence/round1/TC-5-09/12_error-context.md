# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 55-queue.spec.ts >> TC-5-09 ฝั่ง AI ล่มทั้งหมด แล้วกลับมา
- Location: tests\55-queue.spec.ts:566:1

# Error details

```
Error: apiRequestContext._wrapApiCall: ENOENT: no such file or directory, open 'C:\Users\oishi\Documents\GitHub\CWN\Teaching\03_week03\04_Agent_Team_End_to_End\02_receipt_desk\test\runs\round1\artifacts-shard-3\.playwright-artifacts-1\traces\ef49f71afe963c1132c4-93e0c79cd7bdcafc7ad6-recording1.trace'
```

# Test source

```ts
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
  635 |       await evidence(testInfo, '③ timeout', String(e));
  636 |       return Promise.all(ids.map(async id => (await receipt(api, id)).receipt));
  637 |     });
  638 |     await evidence(testInfo, '③ results', done.map((r: any) => ({ fileName: r.fileName, status: r.status, attempts: r.attempts, total: r.total })));
  639 |     for (const r of done) expect.soft(r.status, `③ ${r.fileName} ถูกอ่านต่อจนมีผล (รอตรวจ)`).toBe('review');
  640 | 
  641 |     // workersAlive = 2 at the end (give the workers up to 2 min to re-register)
  642 |     let alive: any = null;
  643 |     const endW = Date.now() + 120_000;
  644 |     for (;;) {
  645 |       alive = (await (await api.get('/api/health')).json().catch(() => ({}))).ai?.workersAlive;
  646 |       if (alive === 2 || Date.now() > endW) break;
  647 |       await sleep(10_000);
  648 |     }
  649 |     await evidence(testInfo, '③ /api/health ai.workersAlive', alive);
  650 |     expect.soft(alive, '③ workersAlive = 2').toBe(2);
  651 |     const recEnd = await reconcile(api);
  652 |     await evidence(testInfo, '③ W20', recEnd);
  653 |   } finally {
> 654 |     await api.dispose();
      |               ^ Error: apiRequestContext._wrapApiCall: ENOENT: no such file or directory, open 'C:\Users\oishi\Documents\GitHub\CWN\Teaching\03_week03\04_Agent_Team_End_to_End\02_receipt_desk\test\runs\round1\artifacts-shard-3\.playwright-artifacts-1\traces\ef49f71afe963c1132c4-93e0c79cd7bdcafc7ad6-recording1.trace'
  655 |   }
  656 | });
  657 | 
  658 | // ================================================================= TC-5-10
  659 | test('TC-5-10 ปิดแล้วเปิดคิวและฐานข้อมูลใหม่กลางงาน', { tag: ['@P1', '@A'] }, async ({}, testInfo) => {
  660 |   await reset(M_URL);
  661 |   pauseReader();
  662 |   let resumed = false;
  663 |   let api = await apiAs(M_URL, 'U01');
  664 |   try {
  665 |     const cl = await clientId(api, 'CL-01');
  666 |     const up = await upload(api, { clientId: cl, files: okFiles(20) });
  667 |     await evidence(testInfo, 'W7 response', { status: up.status, accepted: up.json?.accepted, batchId: up.json?.batchId });
  668 |     expect(W7_OK, `อัปโหลด 20 ไฟล์ (HTTP ${up.status})`).toContain(up.status);
  669 |     const ids = Object.values(idsByName(up.json));
  670 |     expect(ids.length, 'จด 20 ID').toBe(20);
  671 | 
  672 |     const batchId: string = up.json.batchId;
  673 |     // start the reader without blocking (resumeReader() is synchronous and the mock reads all 20 before it returns)
  674 |     const started = resumeReaderAsync(); resumed = true;
  675 |     started.catch(() => undefined); // awaited below; avoid an unhandled rejection if an expect fails first
  676 |     // when about 5 have a result -> restart db + queue of the :3421 stack (poll the batch counts: one cheap W9 call)
  677 |     const endA = Date.now() + 300_000;
  678 |     let counts: any = {};
  679 |     let withResult = 0;
  680 |     for (;;) {
  681 |       counts = (await (await api.get(`/api/batches/${batchId}`)).json()).batch?.counts ?? {};
  682 |       withResult = Number(counts.review || 0) + Number(counts.unreadable || 0);
  683 |       if (withResult >= 5 || Date.now() > endA) break;
  684 |       await sleep(150);
  685 |     }
  686 |     await evidence(testInfo, 'batch counts when the restart starts', { withResult, counts });
  687 |     expect(withResult, 'มีผลราว 5 ใบก่อน restart').toBeGreaterThanOrEqual(5);
  688 |     // precondition of "กลางงาน": some receipts must still be unread when the restart starts
  689 |     if (withResult >= 20) {
  690 |       testInfo.annotations.push({ type: 'precondition', description: `ทำ "restart กลางงาน" ไม่ได้: ตัวอ่านจำลองอ่านครบ 20 ใบก่อนการตรวจครั้งแรก (counts=${JSON.stringify(counts)}) · restart เกิดหลังอ่านครบ จึงไม่ได้พิสูจน์ NFR-06 ข้อ 4` });
  691 |     }
  692 |     expect.soft(withResult, 'restart กลางงาน: ยังมีใบที่ยังไม่มีผลตอนเริ่ม restart').toBeLessThan(20);
  693 |     await started;
  694 |     restartDbAndQueue();
  695 | 
  696 |     // wait for the web to answer again, then log in again (the old session may be gone)
  697 |     const endH = Date.now() + 120_000;
  698 |     for (;;) {
  699 |       const ok = await api.get('/api/health').then(r => r.status() === 200).catch(() => false);
  700 |       if (ok || Date.now() > endH) break;
  701 |       await sleep(2000);
  702 |     }
  703 |     await api.dispose();
  704 |     api = await apiAs(M_URL, 'U01');
  705 | 
  706 |     const done = await waitStatus(api, ids, ['review', 'unreadable'], 480_000);
  707 |     await evidence(testInfo, 'final statuses', done.map(r => ({ id: r.id, fileName: r.fileName, status: r.status, attempts: r.attempts })));
  708 |     for (const r of done) expect.soft(r.status, `${r.fileName}: รอตรวจ`).toBe('review');
  709 | 
  710 |     let missing = 0;
  711 |     const reviewEvents: Record<string, number> = {};
  712 |     for (const id of ids) {
  713 |       const g = await receipt(api, id);
  714 |       if (g.status !== 200 || !g.receipt) { missing++; continue; }
  715 |       const h = await history(api, id);
  716 |       reviewEvents[g.receipt.fileName] = (h.events || []).filter((e: any) => e.to === 'review').length;
  717 |     }
  718 |     await evidence(testInfo, 'W17: number of "review" results per receipt', reviewEvents);
  719 |     expect.soft(missing, 'ทั้ง 20 ID มีอยู่ · ใบหาย 0').toBe(0);
  720 |     for (const [f, n] of Object.entries(reviewEvents)) expect.soft(n, `${f}: มีผล "รอตรวจ" 1 ครั้ง`).toBe(1);
  721 | 
  722 |     const rec = await reconcile(api);
  723 |     await evidence(testInfo, 'W20 at the end', rec);
  724 |     const countsSum = Object.values(rec.counts ?? {}).reduce((s: number, v: any) => s + Number(v || 0), 0);
  725 |     expect.soft(rec.accepted, 'รับเข้า 8 + 20 = 28').toBe(28);
  726 |     expect.soft(countsSum, 'ผลรวมทุกสถานะ = 28').toBe(28);
  727 |     expect.soft(Number(rec.diff), 'ผลต่าง 0').toBe(0);
  728 |   } finally {
  729 |     if (!resumed) resumeReader();
  730 |     await api.dispose();
  731 |   }
  732 | });
  733 | 
```