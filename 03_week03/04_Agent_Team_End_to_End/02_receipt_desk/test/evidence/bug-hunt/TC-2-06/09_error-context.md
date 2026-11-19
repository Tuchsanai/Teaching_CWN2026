# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 52-flags.spec.ts >> TC-2-06 ติด 2 ธง และตัวกรองเฉพาะใบติดธง
- Location: tests\52-flags.spec.ts:211:1

# Error details

```
Error: ผลกรองของ 5 ID = conf-089 · diff-101 · both-flags

expect(received).toEqual(expected) // deep equality

- Expected  - 1
+ Received  + 0

  Array [
    "both-flags.jpg",
    "conf-089.jpg",
-   "diff-101.jpg",
  ]
```

```
Error: ในบรรดา 5 ID ผลกรองมี 3 ใบพอดี (ใบติด 2 ธงนับ 1)

expect(received).toBe(expected) // Object.is equality

Expected: 3
Received: 2
```

# Page snapshot

```yaml
- generic [ref=f5e1]:
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
      - link "สรุปรายเดือน" [ref=f5e10] [cursor=pointer]:
        - /url: /reports
    - generic [ref=f5e11]:
      - generic [ref=f5e12]: คุณแนน
      - generic [ref=f5e13]: พนักงานบัญชี
      - button "ออกจากระบบ" [ref=f5e14] [cursor=pointer]
  - main [ref=f5e15]:
    - heading "รายการใบเสร็จ" [level=1] [ref=f5e16]
    - generic [ref=f5e17]:
      - generic [ref=f5e18]:
        - text: สถานะ
        - combobox "สถานะ" [ref=f5e19]:
          - option "ทุกสถานะ" [selected]
          - option "รออ่าน"
          - option "กำลังอ่าน"
          - option "รอตรวจ"
          - option "ยืนยันแล้ว"
          - option "อ่านไม่ได้"
      - generic [ref=f5e20]:
        - text: ลูกค้า
        - combobox "ลูกค้า" [ref=f5e21]:
          - option "ทุกลูกค้า" [selected]
          - option "CL-01 · ร้านข้าวแกงสมชาย"
          - option "CL-02 · ร้านกาแฟมะลิ"
          - option "CL-03 · ร้านวัสดุทวีทรัพย์"
      - generic [ref=f5e22]:
        - checkbox "เฉพาะใบติดธง “ระบบไม่แน่ใจ”" [checked] [ref=f5e23]
        - text: เฉพาะใบติดธง “ระบบไม่แน่ใจ”
      - button "กรอง" [active] [ref=f5e24] [cursor=pointer]
    - paragraph [ref=f5e25]:
      - text: พบ
      - strong [ref=f5e26]: "2"
      - text: ใบ
    - table [ref=f5e27]:
      - rowgroup [ref=f5e28]:
        - row [ref=f5e29]:
          - columnheader "รับเมื่อ" [ref=f5e30]
          - columnheader "ลูกค้า" [ref=f5e31]
          - columnheader "ไฟล์" [ref=f5e32]
          - columnheader "สถานะ" [ref=f5e33]
          - columnheader "ธง" [ref=f5e34]
          - columnheader "ร้าน" [ref=f5e35]
          - columnheader "วันที่บนใบ" [ref=f5e36]
          - columnheader "ยอดรวม" [ref=f5e37]
          - columnheader "ยืนยันโดย" [ref=f5e38]
          - columnheader [ref=f5e39]
      - rowgroup [ref=f5e40]:
        - row [ref=f5e41]:
          - cell "19/11/2569 17:43" [ref=f5e42]
          - cell "ร้านข้าวแกงสมชาย" [ref=f5e43]
          - cell "both-flags.jpg" [ref=f5e44]
          - cell "รอตรวจ" [ref=f5e45]
          - 'cell "ระบบไม่แน่ใจ: ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90 · ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f5e47]':
            - 'generic "ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90 · ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f5e48]': "ระบบไม่แน่ใจ: ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90 · ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)"
          - cell "ร้านตัวอย่าง" [ref=f5e49]
          - cell "2026-11-18" [ref=f5e50]
          - cell "100.00" [ref=f5e51]
          - cell "—" [ref=f5e52]
          - cell [ref=f5e53]:
            - link "เปิดใบ" [ref=f5e54] [cursor=pointer]:
              - /url: /receipts/242a0969-f9df-4d2f-bf12-569b373a7da2
        - row [ref=f5e55]:
          - cell "19/11/2569 17:43" [ref=f5e56]
          - cell "ร้านข้าวแกงสมชาย" [ref=f5e57]
          - cell "conf-089.jpg" [ref=f5e58]
          - cell "รอตรวจ" [ref=f5e59]
          - 'cell "ระบบไม่แน่ใจ: ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90" [ref=f5e61]':
            - 'generic "ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90" [ref=f5e62]': "ระบบไม่แน่ใจ: ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90"
          - cell "ร้านตัวอย่าง" [ref=f5e63]
          - cell "2026-11-18" [ref=f5e64]
          - cell "100.00" [ref=f5e65]
          - cell "—" [ref=f5e66]
          - cell [ref=f5e67]:
            - link "เปิดใบ" [ref=f5e68] [cursor=pointer]:
              - /url: /receipts/b325ea2a-1474-4588-a4f0-a599450e05e5
  - alert [ref=f5e69]
```

# Test source

```ts
  139 | });
  140 | 
  141 | test('TC-2-02 ความมั่นใจต่ำกว่า 0.90 ติดธง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  142 |   const files = ['conf-089.jpg', 'conf-08999.jpg'];
  143 |   const p = await prepareM(browser, testInfo, files);
  144 |   try {
  145 |     for (const f of files) {
  146 |       const v = await openReview(p.page, p.ids[f]);
  147 |       await shot(testInfo, p.page, `review page ${f}`);
  148 |       await evidence(testInfo, `review page ${f}`, v);
  149 |       expect.soft(v.low.present, `${f}: ติดธง "ไม่แน่ใจยอดรวม"`).toBe(true);
  150 |       expect.soft(v.low.text, `${f}: ธงชื่อ "ไม่แน่ใจยอดรวม"`).toContain('ไม่แน่ใจยอดรวม');
  151 |       expect.soft(v.low.text, `${f}: เหตุผลพูดถึงความมั่นใจของยอดรวม`).toContain('ความมั่นใจ');
  152 |       expect.soft(v.low.text, `${f}: เหตุผลบอกว่าต่ำกว่า`).toContain('ต่ำกว่า');
  153 |       expect.soft(v.low.text, `${f}: เหตุผลบอกเส้น 0.90`).toContain('0.90');
  154 |       expect.soft(v.mismatch.present, `${f}: ไม่ติดธง "ยอดไม่ตรงรายการ" (|100.00 − 100.00| = 0.00)`).toBe(false);
  155 |     }
  156 |   } finally { await p.context.close(); await p.api.dispose(); }
  157 | });
  158 | 
  159 | test('TC-2-03 ความมั่นใจเท่ากับและสูงกว่า 0.90 ไม่ติดธง', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  160 |   const files = ['conf-090.jpg', 'conf-091.jpg'];
  161 |   const p = await prepareM(browser, testInfo, files);
  162 |   try {
  163 |     for (const f of files) {
  164 |       const v = await openReview(p.page, p.ids[f]);
  165 |       await shot(testInfo, p.page, `review page ${f}`);
  166 |       await evidence(testInfo, `review page ${f}`, v);
  167 |       expect.soft(v.low.present, `${f}: ไม่ติดธง "ไม่แน่ใจยอดรวม"`).toBe(false);
  168 |       expect.soft(v.mismatch.present, `${f}: ไม่ติดธง "ยอดไม่ตรงรายการ"`).toBe(false);
  169 |     }
  170 |   } finally { await p.context.close(); await p.api.dispose(); }
  171 | });
  172 | 
  173 | test('TC-2-04 ผลต่างไม่เกิน 1.00 บาท ไม่ติดธง', { tag: ['@P2', '@M'] }, async ({ browser }, testInfo) => {
  174 |   const cases = [
  175 |     { f: 'diff-099.jpg', sum: 4500 + 3000 + 2401 }, // 99.01 · |99.01 − 100.00| = 0.99
  176 |     { f: 'diff-100.jpg', sum: 4500 + 3000 + 2400 }, // 99.00 · |99.00 − 100.00| = 1.00
  177 |   ];
  178 |   const p = await prepareM(browser, testInfo, cases.map(c => c.f));
  179 |   try {
  180 |     for (const c of cases) {
  181 |       const v = await openReview(p.page, p.ids[c.f]);
  182 |       await shot(testInfo, p.page, `review page ${c.f}`);
  183 |       await evidence(testInfo, `review page ${c.f}`, v);
  184 |       expect.soft(toSatang(v.itemsSum), `${c.f}: items-sum`).toBe(c.sum);
  185 |       expect.soft(v.mismatch.present, `${c.f}: ไม่ติดธง "ยอดไม่ตรงรายการ" (ผลต่าง ${(10000 - c.sum) / 100} ≤ 1.00)`).toBe(false);
  186 |     }
  187 |   } finally { await p.context.close(); await p.api.dispose(); }
  188 | });
  189 | 
  190 | test('TC-2-05 ผลต่างเกิน 1.00 บาท ทั้งขาดและเกิน ติดธง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  191 |   const cases = [
  192 |     { f: 'diff-101.jpg', total: 10000, sum: 9899, diff: 101 },
  193 |     { f: 'diff-over-101.jpg', total: 10000, sum: 10101, diff: 101 },
  194 |     { f: 'diff-149.jpg', total: 10000, sum: 9851, diff: 149 },
  195 |   ];
  196 |   const p = await prepareM(browser, testInfo, cases.map(c => c.f));
  197 |   try {
  198 |     for (const c of cases) {
  199 |       const v = await openReview(p.page, p.ids[c.f]);
  200 |       await shot(testInfo, p.page, `review page ${c.f}`);
  201 |       await evidence(testInfo, `review page ${c.f}`, v);
  202 |       expect.soft(v.mismatch.present, `${c.f}: ติดธง "ยอดไม่ตรงรายการ"`).toBe(true);
  203 |       const nums = moneyInText(v.mismatch.text);
  204 |       expect.soft(nums, `${c.f}: เหตุผลแสดงยอดรวมที่อ่าน ${c.total / 100} — text "${v.mismatch.text}"`).toContain(c.total);
  205 |       expect.soft(nums, `${c.f}: เหตุผลแสดงผลรวมรายการ ${(c.sum / 100).toFixed(2)} — text "${v.mismatch.text}"`).toContain(c.sum);
  206 |       expect.soft(nums, `${c.f}: เหตุผลแสดงผลต่าง ${(c.diff / 100).toFixed(2)} — text "${v.mismatch.text}"`).toContain(c.diff);
  207 |     }
  208 |   } finally { await p.context.close(); await p.api.dispose(); }
  209 | });
  210 | 
  211 | test('TC-2-06 ติด 2 ธง และตัวกรองเฉพาะใบติดธง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  212 |   const files = ['ok-100__001.jpg', 'conf-089.jpg', 'conf-090.jpg', 'diff-101.jpg', 'both-flags.jpg'];
  213 |   const p = await prepareM(browser, testInfo, files);
  214 |   try {
  215 |     // both-flags: 2 flags with both reasons (0.50 < 0.90 · |95.00 − 100.00| = 5.00 > 1.00)
  216 |     const v = await openReview(p.page, p.ids['both-flags.jpg']);
  217 |     await shot(testInfo, p.page, 'review page both-flags');
  218 |     await evidence(testInfo, 'review page both-flags', v);
  219 |     expect.soft(v.low.present, 'both-flags: ติดธง "ไม่แน่ใจยอดรวม"').toBe(true);
  220 |     expect.soft(v.mismatch.present, 'both-flags: ติดธง "ยอดไม่ตรงรายการ"').toBe(true);
  221 |     expect.soft(v.low.text, 'both-flags: เหตุผลความมั่นใจต่ำกว่า 0.90').toContain('0.90');
  222 |     expect.soft(moneyInText(v.mismatch.text), `both-flags: เหตุผลแสดงผลต่าง 5.00 — text "${v.mismatch.text}"`).toContain(500);
  223 | 
  224 |     // /receipts · tick filter-flagged-checkbox
  225 |     await p.page.goto('/receipts');
  226 |     await expect(p.page.getByTestId('receipts-table')).toBeVisible();
  227 |     await p.page.getByTestId('filter-flagged-checkbox').check();
  228 |     await p.page.getByTestId('filter-apply-button').click();
  229 |     await p.page.waitForLoadState('networkidle');
  230 |     // wait until the unflagged ok-100 row disappears or the filter result settles
  231 |     await expect(p.page.getByTestId(`receipt-row-${p.ids['ok-100__001.jpg']}`), 'ok-100 not in flagged filter').toHaveCount(0, { timeout: 15_000 }).catch(() => {});
  232 |     await shot(testInfo, p.page, 'receipts filtered flagged');
  233 | 
  234 |     const shown: Record<string, number> = {};
  235 |     for (const f of files) shown[f] = await p.page.getByTestId(`receipt-row-${p.ids[f]}`).count();
  236 |     const inFilter = files.filter(f => shown[f] > 0);
  237 |     await evidence(testInfo, 'flagged filter rows of this batch', { shown, receiptsCount: await p.page.getByTestId('receipts-count').innerText().catch(() => '') });
  238 |     expect.soft(inFilter.sort(), 'ผลกรองของ 5 ID = conf-089 · diff-101 · both-flags').toEqual(['both-flags.jpg', 'conf-089.jpg', 'diff-101.jpg']);
> 239 |     expect.soft(inFilter.length, 'ในบรรดา 5 ID ผลกรองมี 3 ใบพอดี (ใบติด 2 ธงนับ 1)').toBe(3);
      |                                                                                      ^ Error: ในบรรดา 5 ID ผลกรองมี 3 ใบพอดี (ใบติด 2 ธงนับ 1)
  240 |     expect.soft(shown['both-flags.jpg'], 'both-flags ปรากฏ 1 แถว').toBe(1);
  241 |     expect.soft(shown['ok-100__001.jpg'], 'ok-100 ไม่อยู่ในผลกรอง').toBe(0);
  242 |     expect.soft(shown['conf-090.jpg'], 'conf-090 ไม่อยู่ในผลกรอง').toBe(0);
  243 | 
  244 |     // API view of the same filter (evidence only)
  245 |     const w11 = await (await p.api.get('/api/receipts?flagged=true')).json();
  246 |     const mine = (w11.receipts || []).filter((r: any) => Object.values(p.ids).includes(r.id)).map((r: any) => r.fileName);
  247 |     await evidence(testInfo, 'W11 flagged=true (ids of this batch)', { count: w11.count, ofThisBatch: mine });
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
```