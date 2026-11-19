# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 52-flags.spec.ts >> TC-2-07 โมเดลจริงอ่านใบเสร็จจริง 12 ใบ (smoke)
- Location: tests\52-flags.spec.ts:251:1

# Error details

```
Error: te0000.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0000.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0001.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0001.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0002.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0002.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0003.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0003.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0004.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0004.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0005.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0005.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0006.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0006.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0007.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0007.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0008.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0008.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0010.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0010.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0011.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0011.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

```
Error: te0012.jpg: ชื่อร้านไม่ใช่ UNKNOWN

expect(received).not.toBe(expected) // Object.is equality

Expected: not "UNKNOWN"
```

```
Error: te0012.jpg: วันที่ไม่ใช่ 1900-01-01

expect(received).not.toBe(expected) // Object.is equality

Expected: not "1900-01-01"
```

# Page snapshot

```yaml
- generic [active] [ref=f3e1]:
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
      - generic [ref=f3e12]: คุณแนน
      - generic [ref=f3e13]: พนักงานบัญชี
      - button "ออกจากระบบ" [ref=f3e14] [cursor=pointer]
  - main [ref=f3e15]:
    - paragraph [ref=f3e16]:
      - link "← ชุดใบเสร็จทั้งหมด" [ref=f3e17] [cursor=pointer]:
        - /url: /batches
    - heading "ชุดของ CL-03 · ร้านวัสดุทวีทรัพย์" [level=1] [ref=f3e18]
    - paragraph [ref=f3e19]:
      - text: รับเมื่อ 19/11/2569 17:11 · อัปโหลดโดย คุณแนน · ประเภท
      - generic [ref=f3e20]: ปกติ
    - generic [ref=f3e21]:
      - generic [ref=f3e22]:
        - generic [ref=f3e23]: รับเข้า
        - generic [ref=f3e24]: "12"
      - generic [ref=f3e25]:
        - generic [ref=f3e26]: รออ่าน
        - generic [ref=f3e27]: "0"
      - generic [ref=f3e28]:
        - generic [ref=f3e29]: กำลังอ่าน
        - generic [ref=f3e30]: "0"
      - generic [ref=f3e31]:
        - generic [ref=f3e32]: รอตรวจ
        - generic [ref=f3e33]: "12"
      - generic [ref=f3e34]:
        - generic [ref=f3e35]: ยืนยันแล้ว
        - generic [ref=f3e36]: "0"
      - generic [ref=f3e37]:
        - generic [ref=f3e38]: อ่านไม่ได้
        - generic [ref=f3e39]: "0"
      - generic [ref=f3e40]:
        - generic [ref=f3e41]: ผลต่าง (รับเข้า − รวมทุกสถานะ)
        - generic [ref=f3e42]: "0"
    - table [ref=f3e43]:
      - rowgroup [ref=f3e44]:
        - row [ref=f3e45]:
          - columnheader "ไฟล์" [ref=f3e46]
          - columnheader "สถานะ" [ref=f3e47]
          - columnheader "ธง" [ref=f3e48]
          - columnheader "ร้านที่อ่านได้" [ref=f3e49]
          - columnheader "ยอดรวม" [ref=f3e50]
          - columnheader [ref=f3e51]
      - rowgroup [ref=f3e52]:
        - row [ref=f3e53]:
          - cell "te0000.jpg" [ref=f3e54]
          - cell "รอตรวจ" [ref=f3e55]
          - cell [ref=f3e57]
          - cell "UNKNOWN" [ref=f3e58]
          - cell "60000.00" [ref=f3e59]
          - cell [ref=f3e60]:
            - link "เปิดใบ" [ref=f3e61] [cursor=pointer]:
              - /url: /receipts/eabe2902-aa3c-48b9-b4d3-ef01f8eb9860
        - row [ref=f3e62]:
          - cell "te0001.jpg" [ref=f3e63]
          - cell "รอตรวจ" [ref=f3e64]
          - cell [ref=f3e66]
          - cell "UNKNOWN" [ref=f3e67]
          - cell "91000.00" [ref=f3e68]
          - cell [ref=f3e69]:
            - link "เปิดใบ" [ref=f3e70] [cursor=pointer]:
              - /url: /receipts/264b5758-2b0e-49a2-ab7a-871bf48710e4
        - row [ref=f3e71]:
          - cell "te0002.jpg" [ref=f3e72]
          - cell "รอตรวจ" [ref=f3e73]
          - cell [ref=f3e75]
          - cell "UNKNOWN" [ref=f3e76]
          - cell "28000.00" [ref=f3e77]
          - cell [ref=f3e78]:
            - link "เปิดใบ" [ref=f3e79] [cursor=pointer]:
              - /url: /receipts/a35ec2ad-f4a0-49cd-bb02-14a01e889601
        - row [ref=f3e80]:
          - cell "te0003.jpg" [ref=f3e81]
          - cell "รอตรวจ" [ref=f3e82]
          - cell [ref=f3e84]
          - cell "UNKNOWN" [ref=f3e85]
          - cell "11000.00" [ref=f3e86]
          - cell [ref=f3e87]:
            - link "เปิดใบ" [ref=f3e88] [cursor=pointer]:
              - /url: /receipts/8ee9f7e0-ffd9-4b97-9da0-3bab87e158d6
        - row [ref=f3e89]:
          - cell "te0004.jpg" [ref=f3e90]
          - cell "รอตรวจ" [ref=f3e91]
          - 'cell "ระบบไม่แน่ใจ: ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90 · ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f3e93]':
            - 'generic "ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90 · ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f3e94]': "ระบบไม่แน่ใจ: ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90 · ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)"
          - cell "UNKNOWN" [ref=f3e95]
          - cell "174000.00" [ref=f3e96]
          - cell [ref=f3e97]:
            - link "เปิดใบ" [ref=f3e98] [cursor=pointer]:
              - /url: /receipts/84b3b1db-1f21-4ce4-9809-a7bd732e8980
        - row [ref=f3e99]:
          - cell "te0005.jpg" [ref=f3e100]
          - cell "รอตรวจ" [ref=f3e101]
          - 'cell "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f3e103]':
            - 'generic "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f3e104]': "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)"
          - cell "UNKNOWN" [ref=f3e105]
          - cell "31000.00" [ref=f3e106]
          - cell [ref=f3e107]:
            - link "เปิดใบ" [ref=f3e108] [cursor=pointer]:
              - /url: /receipts/8287de9b-47a7-4d89-916d-f6891e2aff47
        - row [ref=f3e109]:
          - cell "te0006.jpg" [ref=f3e110]
          - cell "รอตรวจ" [ref=f3e111]
          - cell [ref=f3e113]
          - cell "UNKNOWN" [ref=f3e114]
          - cell "46000.00" [ref=f3e115]
          - cell [ref=f3e116]:
            - link "เปิดใบ" [ref=f3e117] [cursor=pointer]:
              - /url: /receipts/7627dfcb-4df8-4a68-bac4-50fd453f3779
        - row [ref=f3e118]:
          - cell "te0007.jpg" [ref=f3e119]
          - cell "รอตรวจ" [ref=f3e120]
          - 'cell "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f3e122]':
            - 'generic "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f3e123]': "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)"
          - cell "UNKNOWN" [ref=f3e124]
          - cell "111000.00" [ref=f3e125]
          - cell [ref=f3e126]:
            - link "เปิดใบ" [ref=f3e127] [cursor=pointer]:
              - /url: /receipts/c9c57981-598d-4290-83d4-6e2afb3efda7
        - row [ref=f3e128]:
          - cell "te0008.jpg" [ref=f3e129]
          - cell "รอตรวจ" [ref=f3e130]
          - 'cell "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f3e132]':
            - 'generic "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)" [ref=f3e133]': "ระบบไม่แน่ใจ: ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม (เกิน 1.00 บาท)"
          - cell "UNKNOWN" [ref=f3e134]
          - cell "50000.00" [ref=f3e135]
          - cell [ref=f3e136]:
            - link "เปิดใบ" [ref=f3e137] [cursor=pointer]:
              - /url: /receipts/821efc01-25c0-43af-bfcd-85a45aff0eeb
        - row [ref=f3e138]:
          - cell "te0010.jpg" [ref=f3e139]
          - cell "รอตรวจ" [ref=f3e140]
          - cell [ref=f3e142]
          - cell "UNKNOWN" [ref=f3e143]
          - cell "17000.00" [ref=f3e144]
          - cell [ref=f3e145]:
            - link "เปิดใบ" [ref=f3e146] [cursor=pointer]:
              - /url: /receipts/12aabf3d-4f08-4a43-85c3-0f7579b6f8d8
        - row [ref=f3e147]:
          - cell "te0011.jpg" [ref=f3e148]
          - cell "รอตรวจ" [ref=f3e149]
          - cell [ref=f3e151]
          - cell "UNKNOWN" [ref=f3e152]
          - cell "230000.00" [ref=f3e153]
          - cell [ref=f3e154]:
            - link "เปิดใบ" [ref=f3e155] [cursor=pointer]:
              - /url: /receipts/e42e30a4-1f55-4b34-9e7a-47a154173a0f
        - row [ref=f3e156]:
          - cell "te0012.jpg" [ref=f3e157]
          - cell "รอตรวจ" [ref=f3e158]
          - cell [ref=f3e160]
          - cell "UNKNOWN" [ref=f3e161]
          - cell "120000.00" [ref=f3e162]
          - cell [ref=f3e163]:
            - link "เปิดใบ" [ref=f3e164] [cursor=pointer]:
              - /url: /receipts/4299a8d9-22e2-4ddb-b436-4f2e754cdb41
  - alert [ref=f3e165]
```

# Test source

```ts
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
  239 |     expect.soft(inFilter.length, 'ในบรรดา 5 ID ผลกรองมี 3 ใบพอดี (ใบติด 2 ธงนับ 1)').toBe(3);
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
> 299 |       expect.soft(d.slice(0, 10), `${g.file}: วันที่ไม่ใช่ 1900-01-01`).not.toBe('1900-01-01');
      |                                                                             ^ Error: te0012.jpg: วันที่ไม่ใช่ 1900-01-01
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
  348 |     expect.soft(guessed, 'ใบที่มียอดรวมโดยไม่ติดธง = 0 (M5 อย่าเดา)').toBe(0);
  349 | 
  350 |     const qEnd = await queue(api);
  351 |     await evidence(testInfo, 'W23 at end', qEnd);
  352 |     expect.soft(qEnd?.workers?.alive, 'workersAlive = 2 at end').toBe(2);
  353 |   } finally { await context.close(); await api.dispose(); }
  354 | });
  355 | 
```