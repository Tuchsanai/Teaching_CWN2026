# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 54-urgent.spec.ts >> TC-4-01 ชุด 9 และ 10 ใบตั้งด่วนได้ · ชุดที่อ่านเสร็จแล้วตั้งไม่ได้
- Location: tests\54-urgent.spec.ts:66:1

# Error details

```
Error: ชุดที่อ่านเสร็จแล้ว ไม่ถูกตั้งเป็นด่วน (FR-18)

expect(received).toBe(expected) // Object.is equality

Expected: "normal"
Received: "urgent"
```

```
Error: batch-priority ของชุดที่อ่านเสร็จแล้ว ไม่ใช่ด่วน

expect(locator).not.toContainText(expected) failed

Locator: getByTestId('batch-priority')
Expected substring: not "ด่วน"
Received string: "ด่วน"
Timeout: 15000ms

Call log:
  - batch-priority ของชุดที่อ่านเสร็จแล้ว ไม่ใช่ด่วน getByTestId('batch-priority') with timeout 15000ms
  - waiting for getByTestId('batch-priority')
    33 × locator resolved to <span class="badge urgent" data-priority="urgent" data-testid="batch-priority">ด่วน</span>
       - unexpected value "ด่วน"

```

```yaml
- text: ด่วน
```

```
Error: ตัวนับยังเป็น 2

expect(received).toBe(expected) // Object.is equality

Expected: 2
Received: 3
```

# Test source

```ts
  14  | 
  15  | // ---------------------------------------------------------------- local helpers
  16  | type Resp = { status: number; json: any } | null;
  17  | 
  18  | /** W9 of one batch -> {batch, receipts} */
  19  | async function batchOf(ctx: APIRequestContext, id: string) {
  20  |   return (await ctx.get(`/api/batches/${id}`)).json();
  21  | }
  22  | /** W23 urgent.usedToday */
  23  | async function usedToday(ctx: APIRequestContext): Promise<number> {
  24  |   return (await queue(ctx)).urgent.usedToday;
  25  | }
  26  | /** All receipts of the office (W11 · limit 200 is enough after a reset). */
  27  | async function allReceipts(ctx: APIRequestContext): Promise<any[]> {
  28  |   return (await (await ctx.get('/api/receipts?limit=200')).json()).receipts;
  29  | }
  30  | 
  31  | /** Press `batch-urgent-button` on /batches/{id} and return the W10 response the page sent (null = button disabled / no request). */
  32  | async function urgentViaPage(page: Page, batchId: string): Promise<{ disabled: boolean; resp: Resp }> {
  33  |   await page.goto(`/batches/${batchId}`);
  34  |   const btn = page.getByTestId('batch-urgent-button');
  35  |   await expect(btn, 'batch-urgent-button visible').toBeVisible();
  36  |   if (await btn.isDisabled()) return { disabled: true, resp: null };
  37  |   const respP = page.waitForResponse(
  38  |     r => r.request().method() === 'POST' && /^\/api\/batches\/[^/]+\/urgent$/.test(new URL(r.url()).pathname),
  39  |     { timeout: 15_000 },
  40  |   ).catch(() => null);
  41  |   await btn.click();
  42  |   const r = await respP;
  43  |   if (!r) return { disabled: false, resp: null };
  44  |   return { disabled: false, resp: { status: r.status(), json: await r.json().catch(() => ({})) } };
  45  | }
  46  | 
  47  | /** Upload through /upload (client select · files · optional urgent tick). Returns the W7 response, or null if the page blocked before sending. */
  48  | async function uploadViaPage(page: Page, clientUuid: string, files: string[], urgent: boolean): Promise<Resp> {
  49  |   await page.goto('/upload');
  50  |   await page.getByTestId('upload-client-select').selectOption(clientUuid);
  51  |   await page.getByTestId('upload-file-input').setInputFiles(files.map(f => (path.isAbsolute(f) ? f : dataFile(f))));
  52  |   if (urgent) await page.getByTestId('upload-urgent-checkbox').check();
  53  |   const respP = page.waitForResponse(
  54  |     r => r.request().method() === 'POST' && new URL(r.url()).pathname === '/api/batches',
  55  |     { timeout: 60_000 },
  56  |   ).catch(() => null);
  57  |   await page.getByTestId('upload-submit-button').click();
  58  |   const r = await respP;
  59  |   if (!r) return null;
  60  |   return { status: r.status(), json: await r.json().catch(() => ({})) };
  61  | }
  62  | 
  63  | function autoAcceptDialogs(page: Page) { page.on('dialog', d => d.accept().catch(() => {})); }
  64  | 
  65  | // ================================================================= TC-4-01
  66  | test('TC-4-01 ชุด 9 และ 10 ใบตั้งด่วนได้ · ชุดที่อ่านเสร็จแล้วตั้งไม่ได้', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  67  |   await reset(M_URL);
  68  |   const lead = await apiAs(M_URL, 'U03');
  69  |   const { context, page } = await pageAs(browser, M_URL, 'U03');
  70  |   autoAcceptDialogs(page);
  71  |   try {
  72  |     const cl2 = await clientId(lead, 'CL-02');
  73  |     expect.soft(await usedToday(lead), 'ตัวนับงานด่วนวันนี้เริ่มที่ 0').toBe(0);
  74  |     pauseReader();
  75  |     try {
  76  |       // ชุด 9 ไฟล์
  77  |       const b9 = await upload(lead, { clientId: cl2, files: okFiles(9, 1) });
  78  |       expect(b9.status, 'อัปโหลด 9 ไฟล์ (ไม่ติ๊กด่วน)').toBe(201);
  79  |       expect(b9.json.accepted).toBe(9);
  80  |       const u9 = await urgentViaPage(page, b9.json.batchId);
  81  |       await evidence(testInfo, 'W10 ชุด 9 ใบ', u9);
  82  |       expect.soft(u9.resp?.status, 'W10 ชุด 9 ใบ ตั้งได้').toBe(200);
  83  |       await expect.soft(page.getByTestId('batch-priority'), 'ชุด 9 ใบ batch-priority = ด่วน').toContainText('ด่วน');
  84  |       await shot(testInfo, page, 'ชุด 9 ใบ หลังกดงานด่วน');
  85  |       expect.soft((await batchOf(lead, b9.json.batchId)).batch.priority, 'W9 ชุด 9 ใบ priority').toBe('urgent');
  86  |       expect.soft(await usedToday(lead), 'ตัวนับ 0 → 1').toBe(1);
  87  | 
  88  |       // ชุด 10 ไฟล์
  89  |       const b10 = await upload(lead, { clientId: cl2, files: okFiles(10, 10) });
  90  |       expect(b10.status, 'อัปโหลด 10 ไฟล์ (ไม่ติ๊กด่วน)').toBe(201);
  91  |       expect(b10.json.accepted).toBe(10);
  92  |       const u10 = await urgentViaPage(page, b10.json.batchId);
  93  |       await evidence(testInfo, 'W10 ชุด 10 ใบ', u10);
  94  |       expect.soft(u10.resp?.status, 'W10 ชุด 10 ใบ ตั้งได้').toBe(200);
  95  |       await expect.soft(page.getByTestId('batch-priority'), 'ชุด 10 ใบ batch-priority = ด่วน').toContainText('ด่วน');
  96  |       await shot(testInfo, page, 'ชุด 10 ใบ หลังกดงานด่วน');
  97  |       expect.soft((await batchOf(lead, b10.json.batchId)).batch.priority, 'W9 ชุด 10 ใบ priority').toBe('urgent');
  98  |       expect.soft(await usedToday(lead), 'ตัวนับ 1 → 2').toBe(2);
  99  |     } finally {
  100 |       resumeReader();
  101 |     }
  102 | 
  103 |     // ชุดที่อ่านเสร็จแล้ว
  104 |     const b3 = await upload(lead, { clientId: cl2, files: okFiles(3, 20) });
  105 |     expect(b3.status, 'อัปโหลด 3 ไฟล์').toBe(201);
  106 |     await waitStatus(lead, b3.json.receipts.map((r: any) => r.id), ['review', 'unreadable'], 180_000);
  107 |     const u3 = await urgentViaPage(page, b3.json.batchId);
  108 |     await evidence(testInfo, 'W10 ชุดที่อ่านเสร็จแล้ว', u3);
  109 |     await page.reload();
  110 |     await shot(testInfo, page, 'ชุดที่อ่านเสร็จแล้ว หลังกดงานด่วน');
  111 |     const after = await batchOf(lead, b3.json.batchId);
  112 |     expect.soft(after.batch.priority, 'ชุดที่อ่านเสร็จแล้ว ไม่ถูกตั้งเป็นด่วน (FR-18)').toBe('normal');
  113 |     await expect.soft(page.getByTestId('batch-priority'), 'batch-priority ของชุดที่อ่านเสร็จแล้ว ไม่ใช่ด่วน').not.toContainText('ด่วน');
> 114 |     expect.soft(await usedToday(lead), 'ตัวนับยังเป็น 2').toBe(2);
      |                                                           ^ Error: ตัวนับยังเป็น 2
  115 |     await evidence(testInfo, 'W23 ตอนจบ', await queue(lead));
  116 |   } finally {
  117 |     await context.close();
  118 |     await lead.dispose();
  119 |   }
  120 | });
  121 | 
  122 | // ================================================================= TC-4-02
  123 | test('TC-4-02 ชุด 11 ใบตั้งด่วนไม่ได้', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  124 |   await reset(M_URL);
  125 |   const lead = await apiAs(M_URL, 'U03');
  126 |   const { context, page } = await pageAs(browser, M_URL, 'U03');
  127 |   autoAcceptDialogs(page);
  128 |   pauseReader();
  129 |   try {
  130 |     const cl2 = await clientId(lead, 'CL-02');
  131 |     // ① ชุดปกติ 11 ใบ แล้วกดปุ่มด่วน
  132 |     const b11 = await upload(lead, { clientId: cl2, files: okFiles(11, 1) });
  133 |     expect(b11.status, 'อัปโหลด 11 ไฟล์ (ไม่ติ๊กด่วน)').toBe(201);
  134 |     const u = await urgentViaPage(page, b11.json.batchId);
  135 |     await evidence(testInfo, '① W10 ชุด 11 ใบ', u);
  136 |     expect.soft(u.resp?.status, '① W10 → 422').toBe(422);
  137 |     expect.soft(u.resp?.json?.error, '① error = urgent_too_large').toBe('urgent_too_large');
  138 |     await expect.soft(page.getByTestId('batch-urgent-error'), '① batch-urgent-error แสดง').toBeVisible();
  139 |     await shot(testInfo, page, '① ชุด 11 ใบ กดงานด่วน');
  140 |     const w9 = await batchOf(lead, b11.json.batchId);
  141 |     expect.soft(w9.batch.priority, '① ชุดยังเป็นงานปกติ').toBe('normal');
  142 |     expect.soft(w9.batch.accepted, '① รับไว้ 11 ใบ').toBe(11);
  143 |     await expect.soft(page.getByTestId('batch-priority'), '① batch-priority ไม่ใช่ด่วน').not.toContainText('ด่วน');
  144 |     expect.soft(await usedToday(lead), '① ตัวนับด่วนวันนี้ยังเป็น 0').toBe(0);
  145 | 
  146 |     // ② จดจำนวนใบทั้งระบบและ ID แล้วอัปโหลด 11 ไฟล์ติ๊กด่วนตอนอัปโหลด
  147 |     const before = await allReceipts(lead);
  148 |     const beforeIds = new Set(before.map(r => r.id));
  149 |     const recBefore = await reconcile(lead);
  150 |     let resp = await uploadViaPage(page, cl2, okFiles(11, 20), true);
  151 |     await shot(testInfo, page, '② อัปโหลด 11 ไฟล์ติ๊กด่วน');
  152 |     if (!resp) { // the page blocked before sending -> same request via API (plan section 4)
  153 |       testInfo.annotations.push({ type: 'note', description: 'หน้าเว็บกันไว้ก่อนส่ง จึงยิง W7 urgent=true ด้วย API' });
  154 |       resp = await upload(lead, { clientId: cl2, files: okFiles(11, 20), urgent: true });
  155 |     }
  156 |     await evidence(testInfo, '② W7 11 ไฟล์ urgent=true', resp);
  157 |     const afterList = await allReceipts(lead);
  158 |     const newOnes = afterList.filter(r => !beforeIds.has(r.id));
  159 |     const recAfter = await reconcile(lead);
  160 |     await evidence(testInfo, '② ใบใหม่', { before: before.length, after: afterList.length, reconcileBefore: recBefore, reconcileAfter: recAfter, newIds: newOnes.map(r => ({ id: r.id, priority: r.priority, batchId: r.batchId })) });
  161 |     expect.soft([0, 11], `② จำนวนใบใหม่ = 0 หรือ 11 เท่านั้น (ได้ ${newOnes.length})`).toContain(newOnes.length);
  162 |     expect.soft(recAfter.accepted - recBefore.accepted, '② ยอดรับแล้วเพิ่ม = จำนวนใบใหม่').toBe(newOnes.length);
  163 |     if (newOnes.length === 11) {
  164 |       expect.soft(newOnes.filter(r => r.priority !== 'normal').map(r => r.id), '② ถ้ารับ 11 ทุกใบเป็นงานปกติ').toEqual([]);
  165 |     }
  166 |     expect.soft(await usedToday(lead), '② ตัวนับด่วนยังเป็น 0').toBe(0);
  167 |     pendingAP(testInfo, 'AP-02', `W7 11 ไฟล์ urgent=true → HTTP ${resp.status} ${resp.json?.error ?? ''} · ใบใหม่ ${newOnes.length} ใบ (${newOnes.length === 0 ? 'ปฏิเสธทั้งชุด' : newOnes.length === 11 ? 'รับเป็นงานปกติ' : 'รับครึ่งชุด'})`);
  168 |   } finally {
  169 |     resumeReader();
  170 |     await context.close();
  171 |     await lead.dispose();
  172 |   }
  173 | });
  174 | 
  175 | // ================================================================= TC-4-03
  176 | test('TC-4-03 โควตาวันนี้ใช้ไป 4 → งานที่ 5 ได้', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  177 |   await reset(M_URL, { urgentToday: 4 });
  178 |   const lead = await apiAs(M_URL, 'U03');
  179 |   const { context, page } = await pageAs(browser, M_URL, 'U03');
  180 |   try {
  181 |     const cl2 = await clientId(lead, 'CL-02');
  182 |     expect.soft(await usedToday(lead), 'ก่อนเริ่ม ใช้ไป 4').toBe(4);
  183 |     const r = await upload(lead, { clientId: cl2, files: okFiles(5, 1), urgent: true });
  184 |     await evidence(testInfo, 'W7 5 ไฟล์ urgent=true', r);
  185 |     expect.soft(r.status, 'ตั้งได้ (รับชุด)').toBe(201);
  186 |     expect.soft(r.json.accepted, 'รับ 5 ใบ').toBe(5);
  187 |     expect.soft(r.json.priority, 'ชุดเป็นงานด่วน').toBe('urgent');
  188 |     const q = await queue(lead);
  189 |     await evidence(testInfo, 'W23 หลังตั้ง', q);
  190 |     expect.soft(q.urgent.usedToday, 'ตัวนับ 4 + 1 = 5').toBe(5);
  191 |     expect.soft(q.urgent.limitPerDay, '/ 5').toBe(5);
  192 |     if (r.json.batchId) {
  193 |       await page.goto(`/batches/${r.json.batchId}`);
  194 |       await expect.soft(page.getByTestId('batch-priority'), 'batch-priority = ด่วน').toContainText('ด่วน');
  195 |       await shot(testInfo, page, 'หน้าชุดงานด่วนที่ 5');
  196 |     }
  197 |   } finally {
  198 |     await context.close();
  199 |     await lead.dispose();
  200 |   }
  201 | });
  202 | 
  203 | // ================================================================= TC-4-04
  204 | test('TC-4-04 โควตาครบ 5 → งานที่ 6 ไม่ได้ทุกช่องทาง', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  205 |   // reset wipes the users and their sessions -> log in again after every reset
  206 |   let lead!: APIRequestContext; let context!: BrowserContext; let page!: Page;
  207 |   const login = async () => {
  208 |     lead = await apiAs(M_URL, 'U03');
  209 |     ({ context, page } = await pageAs(browser, M_URL, 'U03'));
  210 |     autoAcceptDialogs(page);
  211 |   };
  212 |   const logout = async () => { await context?.close().catch(() => {}); await lead?.dispose().catch(() => {}); };
  213 |   try {
  214 |     // ① รีเซ็ต urgentToday 5
```