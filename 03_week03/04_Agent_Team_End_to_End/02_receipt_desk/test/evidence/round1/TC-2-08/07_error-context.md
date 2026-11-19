# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 52-flags.spec.ts >> TC-2-08 โมเดลจริงไม่เดากับรูปที่อ่านไม่ได้
- Location: tests\52-flags.spec.ts:314:1

# Error details

```
Error: te0000-crop.jpg: ติดธงอย่างน้อย 1 ธง หรืออยู่ "อ่านไม่ได้" (status review, total 0.00)

expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

```
Error: te0000-blur.jpg: ติดธงอย่างน้อย 1 ธง หรืออยู่ "อ่านไม่ได้" (status review, total 0.00)

expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

```
Error: ใบที่มียอดรวมโดยไม่ติดธง = 0 (M5 อย่าเดา)

expect(received).toBe(expected) // Object.is equality

Expected: 0
Received: 2
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
      - link "สรุปรายเดือน" [ref=f2e10] [cursor=pointer]:
        - /url: /reports
    - generic [ref=f2e11]:
      - generic [ref=f2e12]: คุณแนน
      - generic [ref=f2e13]: พนักงานบัญชี
      - button "ออกจากระบบ" [ref=f2e14] [cursor=pointer]
  - main [ref=f2e15]:
    - paragraph [ref=f2e16]:
      - link "← ชุดใบเสร็จทั้งหมด" [ref=f2e17] [cursor=pointer]:
        - /url: /batches
    - heading "ชุดของ CL-03 · ร้านวัสดุทวีทรัพย์" [level=1] [ref=f2e18]
    - paragraph [ref=f2e19]:
      - text: รับเมื่อ 19/11/2569 17:11 · อัปโหลดโดย คุณแนน · ประเภท
      - generic [ref=f2e20]: ปกติ
    - generic [ref=f2e21]:
      - generic [ref=f2e22]:
        - generic [ref=f2e23]: รับเข้า
        - generic [ref=f2e24]: "2"
      - generic [ref=f2e25]:
        - generic [ref=f2e26]: รออ่าน
        - generic [ref=f2e27]: "0"
      - generic [ref=f2e28]:
        - generic [ref=f2e29]: กำลังอ่าน
        - generic [ref=f2e30]: "0"
      - generic [ref=f2e31]:
        - generic [ref=f2e32]: รอตรวจ
        - generic [ref=f2e33]: "2"
      - generic [ref=f2e34]:
        - generic [ref=f2e35]: ยืนยันแล้ว
        - generic [ref=f2e36]: "0"
      - generic [ref=f2e37]:
        - generic [ref=f2e38]: อ่านไม่ได้
        - generic [ref=f2e39]: "0"
      - generic [ref=f2e40]:
        - generic [ref=f2e41]: ผลต่าง (รับเข้า − รวมทุกสถานะ)
        - generic [ref=f2e42]: "0"
    - table [ref=f2e43]:
      - rowgroup [ref=f2e44]:
        - row [ref=f2e45]:
          - columnheader "ไฟล์" [ref=f2e46]
          - columnheader "สถานะ" [ref=f2e47]
          - columnheader "ธง" [ref=f2e48]
          - columnheader "ร้านที่อ่านได้" [ref=f2e49]
          - columnheader "ยอดรวม" [ref=f2e50]
          - columnheader [ref=f2e51]
      - rowgroup [ref=f2e52]:
        - row [ref=f2e53]:
          - cell "te0000-blur.jpg" [ref=f2e54]
          - cell "รอตรวจ" [ref=f2e55]
          - cell [ref=f2e57]
          - cell "UNKNOWN" [ref=f2e58]
          - cell "0.00" [ref=f2e59]
          - cell [ref=f2e60]:
            - link "เปิดใบ" [ref=f2e61] [cursor=pointer]:
              - /url: /receipts/b1bd41ac-ca81-465e-8b66-fc9dc1eec499
        - row [ref=f2e62]:
          - cell "te0000-crop.jpg" [ref=f2e63]
          - cell "รอตรวจ" [ref=f2e64]
          - cell [ref=f2e66]
          - cell "UNKNOWN" [ref=f2e67]
          - cell "0.00" [ref=f2e68]
          - cell [ref=f2e69]:
            - link "เปิดใบ" [ref=f2e70] [cursor=pointer]:
              - /url: /receipts/f7b4bcd1-d0dd-4e92-85d0-a7fbd15d40b7
  - alert [ref=f2e71]
```

# Test source

```ts
  248 |   } finally { await p.context.close(); await p.api.dispose(); }
  249 | });
  250 | 
  251 | test('TC-2-07 โมเดลจริงอ่านใบเสร็จจริง 12 ใบ (smoke)', { tag: ['@P1', '@R'] }, async ({ browser }, testInfo) => {
  252 |   test.setTimeout(30 * 60_000);
  253 |   const gt: { id: string; file: string; total: string; n_items: number }[] =
  254 |     JSON.parse(fs.readFileSync(path.join(REAL_IMAGES, 'ground_truth.json'), 'utf8'));
  255 |   expect(gt.length, 'ground_truth.json has 12 receipts').toBe(12);
  256 |   const files = gt.map(g => path.join(REAL_IMAGES, g.file));
  257 |   const api = await prepareR(testInfo, files);
  258 |   const { context, page } = await pageAs(browser, R_URL, 'U02');
  259 |   try {
  260 |     const cl = await clientId(api, 'CL-03');
  261 |     const up = await upload(api, { clientId: cl, files, real: true });
  262 |     await evidence(testInfo, 'W7 upload 12 real', { status: up.status, json: up.json });
  263 |     expect(up.status, 'W7 upload').toBeLessThan(300);
  264 |     expect(up.json.accepted, 'accepted 12').toBe(12);
  265 |     const ids: Record<string, string> = {};
  266 |     for (const r of up.json.receipts || []) ids[r.fileName] = r.id;
  267 |     for (const g of gt) expect(ids[g.file], `id of ${g.file}`).toBeTruthy();
  268 | 
  269 |     await page.goto(`/batches/${up.json.batchId}`);
  270 |     const got = await waitStatus(api, gt.map(g => ids[g.file]), ['review', 'unreadable', 'confirmed'], 20 * 60_000);
  271 |     await page.reload();
  272 |     await shot(testInfo, page, 'batch page 12 real receipts read');
  273 |     await evidence(testInfo, 'W12 12 real receipts', got);
  274 | 
  275 |     const rows: string[] = ['| file | status | merchant | date | read total | truth total | total ok | flags | items read / n_items |', '|---|---|---|---|---|---|---|---|---|'];
  276 |     let correct = 0, wrongUnflagged = 0, itemsMatch = 0;
  277 |     for (const g of gt) {
  278 |       const r = got.find((x: any) => x.id === ids[g.file]);
  279 |       const readSat = toSatang(r?.total);
  280 |       const truthSat = toSatang(g.total);
  281 |       const ok = readSat !== null && readSat === truthSat;
  282 |       if (ok) correct++;
  283 |       const flagged = isFlagged(r);
  284 |       if (!ok && !flagged) wrongUnflagged++;
  285 |       const nItems = Array.isArray(r?.items) ? r.items.filter((i: any) => !i.removed).length : null;
  286 |       if (nItems === g.n_items) itemsMatch++;
  287 |       rows.push(`| ${g.file} | ${r?.status} | ${r?.merchant ?? ''} | ${r?.receiptDate ?? ''} | ${r?.total ?? ''} | ${g.total} | ${ok ? 'yes' : 'NO'} | ${flagged ? (r.flags.reasons || []).join(' / ') || 'flagged' : '-'} | ${nItems} / ${g.n_items} |`);
  288 | 
  289 |       // ① status รอตรวจ + 5-field structure
  290 |       expect.soft(r?.status, `${g.file}: รอตรวจ (review)`).toBe('review');
  291 |       expect.soft(r && 'merchant' in r && 'receiptDate' in r && 'total' in r && Array.isArray(r.items), `${g.file}: โครงสร้าง 5 ช่องครบ (merchant · date · items[name,price] · total)`).toBe(true);
  292 |       for (const it of (r?.items || [])) expect.soft('name' in it && 'price' in it, `${g.file}: item line ${it.lineNo} has name and price`).toBe(true);
  293 |       expect.soft(r?.total, `${g.file}: มียอดรวม`).not.toBeNull();
  294 |       // ② merchant / date read for real
  295 |       expect.soft((r?.merchant ?? '').trim(), `${g.file}: ชื่อร้านไม่ว่าง`).not.toBe('');
  296 |       expect.soft((r?.merchant ?? '').trim().toUpperCase(), `${g.file}: ชื่อร้านไม่ใช่ UNKNOWN`).not.toBe('UNKNOWN');
  297 |       const d = String(r?.receiptDate ?? '');
  298 |       expect.soft(/^\d{4}-\d{2}-\d{2}/.test(d) && !Number.isNaN(Date.parse(d.slice(0, 10))), `${g.file}: วันที่เป็นวันที่จริง (got "${d}")`).toBe(true);
  299 |       expect.soft(d.slice(0, 10), `${g.file}: วันที่ไม่ใช่ 1900-01-01`).not.toBe('1900-01-01');
  300 |       // ③ wrong total must be flagged
  301 |       if (!ok) expect.soft(flagged, `${g.file}: ยอดอ่าน ${r?.total} ≠ เฉลย ${g.total} ต้องติดธง`).toBe(true);
  302 |     }
  303 |     rows.push('', `ยอดถูก ${correct} / 12 = ${(correct / 12 * 100).toFixed(1)}% (M1 trend, not used to judge) · จำนวนรายการตรง n_items ${itemsMatch} / 12 (M7 trend) · ยอดผิดและไม่ติดธง ${wrongUnflagged}`);
  304 |     await evidence(testInfo, 'per-receipt comparison (satang)', rows.join('\n'));
  305 |     testInfo.annotations.push({ type: 'trend', description: `total correct ${correct}/12 · items count match ${itemsMatch}/12 · wrong & unflagged ${wrongUnflagged}` });
  306 |     expect.soft(wrongUnflagged, '③ ใบที่ยอดผิดและไม่ติดธง = 0').toBe(0);
  307 | 
  308 |     const qEnd = await queue(api);
  309 |     await evidence(testInfo, 'W23 at end', qEnd);
  310 |     expect.soft(qEnd?.workers?.alive, 'workersAlive = 2 at end').toBe(2);
  311 |   } finally { await context.close(); await api.dispose(); }
  312 | });
  313 | 
  314 | test('TC-2-08 โมเดลจริงไม่เดากับรูปที่อ่านไม่ได้', { tag: ['@P2', '@R'] }, async ({ browser }, testInfo) => {
  315 |   test.setTimeout(20 * 60_000);
  316 |   const files = [path.join(DATA, 'te0000-crop.jpg'), path.join(DATA, 'te0000-blur.jpg')];
  317 |   testInfo.annotations.push({ type: 'deviation', description: 'te0000-crop (bottom half cut) และ te0000-blur (Gaussian 25) ตรวจว่าอ่านยอดรวม 60,000.00 ไม่ได้โดยผู้ตรวจ 1 คน (แผนกำหนด 2 คน)' });
  318 |   const api = await prepareR(testInfo, files);
  319 |   const { context, page } = await pageAs(browser, R_URL, 'U02');
  320 |   try {
  321 |     const cl = await clientId(api, 'CL-03');
  322 |     const up = await upload(api, { clientId: cl, files, real: true });
  323 |     await evidence(testInfo, 'W7 upload 2 unreadable images', { status: up.status, json: up.json });
  324 |     expect(up.status, 'W7 upload').toBeLessThan(300);
  325 |     expect(up.json.accepted, 'accepted 2').toBe(2);
  326 |     const ids: Record<string, string> = {};
  327 |     for (const r of up.json.receipts || []) ids[r.fileName] = r.id;
  328 |     const names = files.map(f => path.basename(f));
  329 |     for (const n of names) expect(ids[n], `id of ${n}`).toBeTruthy();
  330 | 
  331 |     const got = await waitStatus(api, names.map(n => ids[n]), ['review', 'unreadable', 'confirmed'], 15 * 60_000);
  332 |     await evidence(testInfo, 'W12 2 receipts', got);
  333 |     await page.goto(`/batches/${up.json.batchId}`);
  334 |     await shot(testInfo, page, 'batch page crop + blur');
  335 | 
  336 |     const rows = ['| file | status | read total | flags | reasons | guessed (total, no flag) |', '|---|---|---|---|---|---|'];
  337 |     let guessed = 0;
  338 |     for (const n of names) {
  339 |       const r = got.find((x: any) => x.id === ids[n]);
  340 |       const flagged = isFlagged(r);
  341 |       const hasTotal = r?.total !== null && r?.total !== undefined && r?.total !== '';
  342 |       const g = r?.status === 'review' && hasTotal && !flagged;
  343 |       if (g) guessed++;
  344 |       rows.push(`| ${n} | ${r?.status} | ${r?.total ?? ''} | ${flagged ? 'yes' : 'no'} | ${(r?.flags?.reasons || []).join(' / ')} | ${g ? 'YES' : 'no'} |`);
  345 |       expect.soft(flagged || r?.status === 'unreadable', `${n}: ติดธงอย่างน้อย 1 ธง หรืออยู่ "อ่านไม่ได้" (status ${r?.status}, total ${r?.total})`).toBe(true);
  346 |     }
  347 |     await evidence(testInfo, 'per-receipt comparison', rows.join('\n'));
> 348 |     expect.soft(guessed, 'ใบที่มียอดรวมโดยไม่ติดธง = 0 (M5 อย่าเดา)').toBe(0);
      |                                                                       ^ Error: ใบที่มียอดรวมโดยไม่ติดธง = 0 (M5 อย่าเดา)
  349 | 
  350 |     const qEnd = await queue(api);
  351 |     await evidence(testInfo, 'W23 at end', qEnd);
  352 |     expect.soft(qEnd?.workers?.alive, 'workersAlive = 2 at end').toBe(2);
  353 |   } finally { await context.close(); await api.dispose(); }
  354 | });
  355 | 
```