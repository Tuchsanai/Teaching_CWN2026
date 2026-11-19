# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 54-urgent.spec.ts >> TC-4-08 ลำดับอ่าน 4:1 ครบ 4 รูปคิว
- Location: tests\54-urgent.spec.ts:402:1

# Error details

```
Error: a ⑤ ลำดับอ่าน (รูปแบบด่วน/ปกติ ตาม BR-10)

expect(received).toBe(expected) // Object.is equality

Expected: "U U U N N"
Received: "U N U U N"
```

# Page snapshot

```yaml
- generic [active] [ref=f5e1]:
  - banner [ref=f5e2]:
    - link "ReceiptDesk" [ref=f5e3] [cursor=pointer]:
      - /url: /
    - navigation [ref=f5e5]:
      - link "อัปโหลดชุด" [ref=f5e6] [cursor=pointer]:
        - /url: /upload
      - link "ชุดใบเสร็จ" [ref=f5e7] [cursor=pointer]:
        - /url: /batches
      - link "รายการใบ" [ref=f5e8] [cursor=pointer]:
        - /url: /receipts
      - link "อ่านไม่ได้" [ref=f5e9] [cursor=pointer]:
        - /url: /unreadable
      - link "ค้างเกินกำหนด" [ref=f5e10] [cursor=pointer]:
        - /url: /overdue
      - link "สรุปรายเดือน" [ref=f5e11] [cursor=pointer]:
        - /url: /reports
      - link "เวลาตรวจ · GPU" [ref=f5e12] [cursor=pointer]:
        - /url: /insights
    - generic [ref=f5e13]:
      - generic [ref=f5e14]: คุณกิตติ
      - generic [ref=f5e15]: หัวหน้าทีมบัญชี
      - button "ออกจากระบบ" [ref=f5e16] [cursor=pointer]
  - main [ref=f5e17]:
    - paragraph [ref=f5e18]:
      - link "← ชุดใบเสร็จทั้งหมด" [ref=f5e19] [cursor=pointer]:
        - /url: /batches
    - heading "ชุดของ CL-02 · ร้านกาแฟมะลิ" [level=1] [ref=f5e20]
    - paragraph [ref=f5e21]:
      - text: รับเมื่อ 19/11/2569 17:25 · อัปโหลดโดย คุณกิตติ · ประเภท
      - generic [ref=f5e22]: ด่วน
      - text: (ตั้งด่วนโดย คุณกิตติ เมื่อ 19/11/2569 17:25)
    - generic [ref=f5e23]:
      - generic [ref=f5e24]:
        - generic [ref=f5e25]: รับเข้า
        - generic [ref=f5e26]: "5"
      - generic [ref=f5e27]:
        - generic [ref=f5e28]: รออ่าน
        - generic [ref=f5e29]: "0"
      - generic [ref=f5e30]:
        - generic [ref=f5e31]: กำลังอ่าน
        - generic [ref=f5e32]: "0"
      - generic [ref=f5e33]:
        - generic [ref=f5e34]: รอตรวจ
        - generic [ref=f5e35]: "5"
      - generic [ref=f5e36]:
        - generic [ref=f5e37]: ยืนยันแล้ว
        - generic [ref=f5e38]: "0"
      - generic [ref=f5e39]:
        - generic [ref=f5e40]: อ่านไม่ได้
        - generic [ref=f5e41]: "0"
      - generic [ref=f5e42]:
        - generic [ref=f5e43]: ผลต่าง (รับเข้า − รวมทุกสถานะ)
        - generic [ref=f5e44]: "0"
    - generic [ref=f5e45]:
      - button "เป็นงานด่วนแล้ว" [disabled]
      - text: ไม่เกิน 10 ใบต่อชุด · ไม่เกิน 5 งานต่อวัน
    - table [ref=f5e46]:
      - rowgroup [ref=f5e47]:
        - row [ref=f5e48]:
          - columnheader "ไฟล์" [ref=f5e49]
          - columnheader "สถานะ" [ref=f5e50]
          - columnheader "ธง" [ref=f5e51]
          - columnheader "ร้านที่อ่านได้" [ref=f5e52]
          - columnheader "ยอดรวม" [ref=f5e53]
          - columnheader [ref=f5e54]
      - rowgroup [ref=f5e55]:
        - row [ref=f5e56]:
          - cell "te0006__4-08d-U1.jpg" [ref=f5e57]
          - cell "รอตรวจ" [ref=f5e58]
          - cell [ref=f5e60]
          - cell "UNKNOWN" [ref=f5e61]
          - cell "46000.00" [ref=f5e62]
          - cell [ref=f5e63]:
            - link "เปิดใบ" [ref=f5e64] [cursor=pointer]:
              - /url: /receipts/2a3d1584-f6f3-4ffa-9397-925f293dbfc9
        - row [ref=f5e65]:
          - cell "te0007__4-08d-U2.jpg" [ref=f5e66]
          - cell "รอตรวจ" [ref=f5e67]
          - 'cell "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f5e69]':
            - 'generic "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f5e70]': "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)"
          - cell "UNKNOWN" [ref=f5e71]
          - cell "111000.00" [ref=f5e72]
          - cell [ref=f5e73]:
            - link "เปิดใบ" [ref=f5e74] [cursor=pointer]:
              - /url: /receipts/8cbccda6-0bb6-4bda-80e5-86511bba0db1
        - row [ref=f5e75]:
          - cell "te0008__4-08d-U3.jpg" [ref=f5e76]
          - cell "รอตรวจ" [ref=f5e77]
          - 'cell "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f5e79]':
            - 'generic "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f5e80]': "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)"
          - cell "UNKNOWN" [ref=f5e81]
          - cell "50000.00" [ref=f5e82]
          - cell [ref=f5e83]:
            - link "เปิดใบ" [ref=f5e84] [cursor=pointer]:
              - /url: /receipts/0be351b1-ab98-4572-9a86-232e2aed2ad0
        - row [ref=f5e85]:
          - cell "te0010__4-08d-U4.jpg" [ref=f5e86]
          - cell "รอตรวจ" [ref=f5e87]
          - cell [ref=f5e89]
          - cell "UNKNOWN" [ref=f5e90]
          - cell "17000.00" [ref=f5e91]
          - cell [ref=f5e92]:
            - link "เปิดใบ" [ref=f5e93] [cursor=pointer]:
              - /url: /receipts/634436a2-cf95-4071-a8be-99aad2d9950a
        - row [ref=f5e94]:
          - cell "te0011__4-08d-U5.jpg" [ref=f5e95]
          - cell "รอตรวจ" [ref=f5e96]
          - cell [ref=f5e98]
          - cell "UNKNOWN" [ref=f5e99]
          - cell "230000.00" [ref=f5e100]
          - cell [ref=f5e101]:
            - link "เปิดใบ" [ref=f5e102] [cursor=pointer]:
              - /url: /receipts/22e9b167-0751-406d-8723-e038d3b08064
  - alert [ref=f5e103]
```

# Test source

```ts
  403 |   test.setTimeout(40 * 60_000);
  404 | 
  405 |   // ---- E6: real images · reset :3420 · W23 · workers
  406 |   const gt: { file: string }[] = JSON.parse(fs.readFileSync(path.join(REAL_IMAGES, 'ground_truth.json'), 'utf8'));
  407 |   const pool = gt.map(g => g.file);
  408 |   expect(pool.length, 'E6 ground_truth 12 ใบ').toBe(12);
  409 |   for (const f of pool) expect(fs.existsSync(path.join(REAL_IMAGES, f)), `E6 มีไฟล์ ${f}`).toBe(true);
  410 |   await reset(R_URL);
  411 |   const lead = await apiAs(R_URL, 'U03');
  412 |   const q0 = await queue(lead);
  413 |   await evidence(testInfo, 'E6 W23 หลังรีเซ็ต', q0);
  414 |   expect(q0.normal.pending, 'E6 ใบงานปกติค้าง 0').toBe(0);
  415 |   expect(q0.urgent.usedToday, 'E6 งานด่วนวันนี้ 0').toBe(0);
  416 |   expect(q0.urgent.limitPerDay, 'E6 / 5').toBe(5);
  417 |   expect(q0.workers.alive, 'E6 W23 workers alive 2').toBe(2);
  418 |   expect(await healthWorkers(R_URL), 'E6 /api/health workersAlive 2').toBe(2);
  419 |   testInfo.annotations.push({ type: 'note', description: 'E6: คิวที่ gateway (GET /v1/queue) เรียกจากเครื่องทดสอบไม่ได้ จึงไม่ได้ตรวจในสเปกนี้' });
  420 | 
  421 |   const cl2 = await clientId(lead, 'CL-02');
  422 |   const dir = testInfo.outputPath('real-4-08'); fs.mkdirSync(dir, { recursive: true });
  423 |   let k = 0;
  424 |   const realCopy = (shape: string, label: string) => {
  425 |     const src = pool[k++ % pool.length];
  426 |     const dst = path.join(dir, `${path.parse(src).name}__4-08${shape}-${label}.jpg`);
  427 |     fs.copyFileSync(path.join(REAL_IMAGES, src), dst);
  428 |     return dst;
  429 |   };
  430 | 
  431 |   const { context, page } = await pageAs(browser, R_URL, 'U03');
  432 |   const summary: Record<string, unknown> = {};
  433 |   try {
  434 |     for (const s of SHAPES) {
  435 |       // ① stop both workers (the web still accepts)
  436 |       await evidence(testInfo, `${s.key} ① stop`, gpu('stop worker0 worker1'));
  437 | 
  438 |       // ② normal batch first, then urgent batch (ticked at upload)
  439 |       const label: Record<string, string> = {};
  440 |       let normal: any = null;
  441 |       if (s.n > 0) {
  442 |         const files = Array.from({ length: s.n }, (_, i) => realCopy(s.key, `N${i + 1}`));
  443 |         const r = await upload(lead, { clientId: cl2, files, real: true });
  444 |         expect(r.status, `${s.key} ② ชุดปกติ ${s.n} ใบ`).toBe(201);
  445 |         expect(r.json.accepted).toBe(s.n);
  446 |         normal = r.json;
  447 |         for (let i = 0; i < s.n; i++) {
  448 |           const rec = r.json.receipts.find((x: any) => x.fileName === path.basename(files[i]));
  449 |           expect(rec, `${s.key} หา N${i + 1} จากชื่อไฟล์`).toBeTruthy();
  450 |           label[rec.id] = `N${i + 1}`;
  451 |         }
  452 |       }
  453 |       const ufiles = Array.from({ length: s.u }, (_, i) => realCopy(s.key, `U${i + 1}`));
  454 |       const ur = await upload(lead, { clientId: cl2, files: ufiles, urgent: true, real: true });
  455 |       await evidence(testInfo, `${s.key} ② W7 ชุดด่วน`, ur);
  456 |       expect(ur.status, `${s.key} ② ชุดด่วน ${s.u} ใบ`).toBe(201);
  457 |       expect(ur.json.priority, `${s.key} ② ชุดเป็นงานด่วน`).toBe('urgent');
  458 |       for (let i = 0; i < s.u; i++) {
  459 |         const rec = ur.json.receipts.find((x: any) => x.fileName === path.basename(ufiles[i]));
  460 |         expect(rec, `${s.key} หา U${i + 1} จากชื่อไฟล์`).toBeTruthy();
  461 |         label[rec.id] = `U${i + 1}`;
  462 |       }
  463 |       const ids = Object.keys(label);
  464 | 
  465 |       // ③ give the dispatcher time to hand them to the gateway, then check W23 / W9 that all are waiting
  466 |       await new Promise(r => setTimeout(r, 20_000));
  467 |       const q = await queue(lead);
  468 |       const w9u = await batchOf(lead, ur.json.batchId);
  469 |       const w9n = normal ? await batchOf(lead, normal.batchId) : null;
  470 |       await evidence(testInfo, `${s.key} ③ W23 + W9 ก่อนเปิด worker0`, { w23: q, urgentBatch: w9u.batch, normalBatch: w9n?.batch ?? null });
  471 |       expect.soft(q.urgent.pending, `${s.key} ③ W23 ใบด่วนรออ่าน ${s.u}`).toBe(s.u);
  472 |       expect.soft(q.normal.pending, `${s.key} ③ W23 ใบปกติรออ่าน ${s.n}`).toBe(s.n);
  473 |       expect.soft(w9u.batch.counts.queued, `${s.key} ③ หน้าชุดด่วน รออ่าน ${s.u}`).toBe(s.u);
  474 |       if (w9n) expect.soft(w9n.batch.counts.queued, `${s.key} ③ หน้าชุดปกติ รออ่าน ${s.n}`).toBe(s.n);
  475 |       await page.goto(`/batches/${ur.json.batchId}`);
  476 |       await expect.soft(page.getByTestId('batch-count-queued'), `${s.key} ③ batch-count-queued`).toHaveText(String(s.u));
  477 |       await shot(testInfo, page, `${s.key} ③ ชุดด่วนรออ่านก่อนเปิด worker0`);
  478 | 
  479 |       // ④ start worker0 only, wait until every receipt of the shape has a result
  480 |       await evidence(testInfo, `${s.key} ④ start worker0`, gpu('start worker0'));
  481 |       await waitStatus(lead, ids, ['review', 'unreadable'], 10 * 60_000);
  482 | 
  483 |       // ⑤ order of "go" events per id from the worker0 log (receipt=<id> is the web receipt id: DESIGN 5.3 receipt_ref = receipts.id)
  484 |       const log = gpu('log worker0');
  485 |       const { goOrder, reads } = parseWorkerLog(log);
  486 |       const mine = goOrder.filter(g => label[g.id]);
  487 |       const order = mine.map(g => label[g.id]);
  488 |       const perId = ids.map(id => ({
  489 |         label: label[id], id,
  490 |         go: goOrder.filter(g => g.id === id).length,
  491 |         read: reads.filter(r => r.id === id).length,
  492 |         queues: [...new Set(goOrder.filter(g => g.id === id).map(g => g.queue))],
  493 |       }));
  494 |       summary[s.key] = { expected: s.expected, observed: order, perId };
  495 |       await evidence(testInfo, `${s.key} ⑤ ลำดับหยิบงานจาก log worker0`, { expected: s.expected, observed: order, events: mine.map(g => ({ ...g, label: label[g.id] })), perId });
  496 |       await evidence(testInfo, `${s.key} ⑤ log worker0 (tail 40)`, log);
  497 |       expect.soft(perId.filter(p => p.go === 0).map(p => p.label), `${s.key} ⑤ ทุก ID ต้องมีเหตุการณ์หยิบใน log (tail 40)`).toEqual([]);
  498 |       // Uk/Nk in the plan = order of entering the queue at the gateway; the dispatcher does not enter receipts in
  499 |       // upload order, so upload labels cannot give the queue position. BR-10 is decided on the U/N sequence.
  500 |       const pattern = order.map(l => l[0]).join(' ');
  501 |       const expectedPattern = s.expected.map((l: string) => l[0]).join(' ');
  502 |       testInfo.annotations.push({ type: 'info', description: `${s.key}: ลำดับหยิบ (ป้ายตามลำดับอัปโหลด) ${order.join(' ')} · รูปแบบ ${pattern} · คาด ${expectedPattern}` });
> 503 |       expect.soft(pattern, `${s.key} ⑤ ลำดับอ่าน (รูปแบบด่วน/ปกติ ตาม BR-10)`).toBe(expectedPattern);
      |                                                                                ^ Error: a ⑤ ลำดับอ่าน (รูปแบบด่วน/ปกติ ตาม BR-10)
  504 |       expect.soft(perId.filter(p => p.go !== 1 || p.read !== 1).map(p => `${p.label}: go=${p.go} read=${p.read}`), `${s.key} ทุก ID หยิบ 1 ครั้งและผล 1 ครั้ง`).toEqual([]);
  505 |       expect.soft(perId.filter(p => p.queues.some(qq => qq !== (p.label.startsWith('U') ? 'urgent' : 'normal'))).map(p => `${p.label}: ${p.queues}`), `${s.key} ใบ U มาจาก queue=urgent · ใบ N มาจาก queue=normal`).toEqual([]);
  506 |     }
  507 |   } finally {
  508 |     await evidence(testInfo, 'สรุปลำดับทุกรูปคิว', summary);
  509 |     let startOut = '';
  510 |     try { startOut = gpu('start worker0 worker1'); } catch (e) { startOut = `start failed: ${e}`; }
  511 |     await evidence(testInfo, 'จบ: start worker0 worker1', startOut);
  512 |     const alive = await waitWorkersAlive(R_URL, 2, 120_000);
  513 |     expect.soft(alive, 'จบด้วย workersAlive = 2').toBe(2);
  514 |     await context.close();
  515 |     await lead.dispose();
  516 |   }
  517 | });
  518 | 
```