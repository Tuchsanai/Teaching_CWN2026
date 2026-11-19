# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 54-urgent.spec.ts >> TC-4-04 โควตาครบ 5 → งานที่ 6 ไม่ได้ทุกช่องทาง
- Location: tests\54-urgent.spec.ts:204:1

# Error details

```
Error: ① (ก) 409

expect(received).toBe(expected) // Object.is equality

Expected: 409
Received: 201
```

```
Error: ① (ก) urgent_quota

expect(received).toBe(expected) // Object.is equality

Expected: "urgent_quota"
Received: undefined
```

```
Error: ① (ก) ตัวนับยังเป็น 5

expect(received).toBe(expected) // Object.is equality

Expected: 5
Received: 6
```

```
Error: ① ตัวนับยังเป็น 5

expect(received).toBe(expected) // Object.is equality

Expected: 5
Received: 6
```

```
Error: ② งานที่ 6 W7 → 409

expect(received).toBe(expected) // Object.is equality

Expected: 409
Received: 201
```

```
Error: ② งานที่ 6 W7 urgent_quota

expect(received).toBe(expected) // Object.is equality

Expected: "urgent_quota"
Received: undefined
```

```
Error: ② ตัวนับ 5 / 5

expect(received).toBe(expected) // Object.is equality

Expected: 5
Received: 6
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
    - paragraph [ref=f3e18]:
      - link "← ชุดใบเสร็จทั้งหมด" [ref=f3e19] [cursor=pointer]:
        - /url: /batches
    - heading "ชุดของ CL-02 · ร้านกาแฟมะลิ" [level=1] [ref=f3e20]
    - paragraph [ref=f3e21]:
      - text: รับเมื่อ 19/11/2569 17:44 · อัปโหลดโดย คุณกิตติ · ประเภท
      - generic [ref=f3e22]: ปกติ
    - generic [ref=f3e23]:
      - generic [ref=f3e24]:
        - generic [ref=f3e25]: รับเข้า
        - generic [ref=f3e26]: "5"
      - generic [ref=f3e27]:
        - generic [ref=f3e28]: รออ่าน
        - generic [ref=f3e29]: "5"
      - generic [ref=f3e30]:
        - generic [ref=f3e31]: กำลังอ่าน
        - generic [ref=f3e32]: "0"
      - generic [ref=f3e33]:
        - generic [ref=f3e34]: รอตรวจ
        - generic [ref=f3e35]: "0"
      - generic [ref=f3e36]:
        - generic [ref=f3e37]: ยืนยันแล้ว
        - generic [ref=f3e38]: "0"
      - generic [ref=f3e39]:
        - generic [ref=f3e40]: อ่านไม่ได้
        - generic [ref=f3e41]: "0"
      - generic [ref=f3e42]:
        - generic [ref=f3e43]: ผลต่าง (รับเข้า − รวมทุกสถานะ)
        - generic [ref=f3e44]: "0"
    - generic [ref=f3e45]:
      - button "ตั้งเป็นงานด่วน" [ref=f3e46] [cursor=pointer]
      - text: ไม่เกิน 10 ใบต่อชุด · ไม่เกิน 5 งานต่อวัน
      - alert [ref=f3e47]: วันนี้ตั้งงานด่วนครบ 5 งานแล้ว ตั้งเพิ่มได้อีกครั้งพรุ่งนี้ (เวลาไทย)
    - table [ref=f3e48]:
      - rowgroup [ref=f3e49]:
        - row [ref=f3e50]:
          - columnheader "ไฟล์" [ref=f3e51]
          - columnheader "สถานะ" [ref=f3e52]
          - columnheader "ธง" [ref=f3e53]
          - columnheader "ร้านที่อ่านได้" [ref=f3e54]
          - columnheader "ยอดรวม" [ref=f3e55]
          - columnheader [ref=f3e56]
      - rowgroup [ref=f3e57]:
        - row [ref=f3e58]:
          - cell "ok-100__010.jpg" [ref=f3e59]
          - cell "รออ่าน" [ref=f3e60]
          - cell [ref=f3e62]
          - cell "—" [ref=f3e63]
          - cell "—" [ref=f3e64]
          - cell [ref=f3e65]:
            - link "เปิดใบ" [ref=f3e66] [cursor=pointer]:
              - /url: /receipts/aafab2ac-14a8-44c1-84e7-7e58d61fe91d
        - row [ref=f3e67]:
          - cell "ok-100__011.jpg" [ref=f3e68]
          - cell "รออ่าน" [ref=f3e69]
          - cell [ref=f3e71]
          - cell "—" [ref=f3e72]
          - cell "—" [ref=f3e73]
          - cell [ref=f3e74]:
            - link "เปิดใบ" [ref=f3e75] [cursor=pointer]:
              - /url: /receipts/cd0ffe65-69f7-42f1-8eb7-c43b09fb4c9d
        - row [ref=f3e76]:
          - cell "ok-100__012.jpg" [ref=f3e77]
          - cell "รออ่าน" [ref=f3e78]
          - cell [ref=f3e80]
          - cell "—" [ref=f3e81]
          - cell "—" [ref=f3e82]
          - cell [ref=f3e83]:
            - link "เปิดใบ" [ref=f3e84] [cursor=pointer]:
              - /url: /receipts/896241ce-75bc-4650-8206-2a744b457f58
        - row [ref=f3e85]:
          - cell "ok-100__013.jpg" [ref=f3e86]
          - cell "รออ่าน" [ref=f3e87]
          - cell [ref=f3e89]
          - cell "—" [ref=f3e90]
          - cell "—" [ref=f3e91]
          - cell [ref=f3e92]:
            - link "เปิดใบ" [ref=f3e93] [cursor=pointer]:
              - /url: /receipts/43368fe6-8114-4c70-933e-35b717c0c02e
        - row [ref=f3e94]:
          - cell "ok-100__014.jpg" [ref=f3e95]
          - cell "รออ่าน" [ref=f3e96]
          - cell [ref=f3e98]
          - cell "—" [ref=f3e99]
          - cell "—" [ref=f3e100]
          - cell [ref=f3e101]:
            - link "เปิดใบ" [ref=f3e102] [cursor=pointer]:
              - /url: /receipts/356e4906-a59e-4b64-93e8-a29d3988ed44
  - alert [ref=f3e103]
```

# Test source

```ts
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
  215 |     await reset(M_URL, { urgentToday: 5 });
  216 |     await login();
  217 |     pauseReader();
  218 |     try {
  219 |       const cl2 = await clientId(lead, 'CL-02');
  220 |       expect.soft(await usedToday(lead), '① ก่อนเริ่ม 5 / 5').toBe(5);
  221 |       // (ก) อัปโหลด 5 ไฟล์ติ๊กด่วน (ผ่านหน้า /upload)
  222 |       let a = await uploadViaPage(page, cl2, okFiles(5, 1), true);
  223 |       await shot(testInfo, page, '① (ก) อัปโหลดติ๊กด่วน งานที่ 6');
  224 |       if (!a) {
  225 |         testInfo.annotations.push({ type: 'note', description: '① (ก) หน้าเว็บกันไว้ก่อนส่ง จึงยิง W7 urgent=true ด้วย API' });
  226 |         a = await upload(lead, { clientId: cl2, files: okFiles(5, 1), urgent: true });
  227 |       }
  228 |       await evidence(testInfo, '① (ก) W7 urgent=true', a);
  229 |       expect.soft(a.status, '① (ก) 409').toBe(409);
  230 |       expect.soft(a.json?.error, '① (ก) urgent_quota').toBe('urgent_quota');
  231 |       expect.soft(await usedToday(lead), '① (ก) ตัวนับยังเป็น 5').toBe(5);
  232 |       // (ข) อัปโหลดปกติแล้วกดปุ่มด่วน
  233 |       const nb = await upload(lead, { clientId: cl2, files: okFiles(5, 10) });
  234 |       expect(nb.status, '① (ข) อัปโหลดปกติ').toBe(201);
  235 |       const b = await urgentViaPage(page, nb.json.batchId);
  236 |       await evidence(testInfo, '① (ข) W10', b);
  237 |       await shot(testInfo, page, '① (ข) กดปุ่มด่วน งานที่ 6');
  238 |       expect.soft(b.resp?.status, '① (ข) 409').toBe(409);
  239 |       expect.soft(b.resp?.json?.error, '① (ข) urgent_quota').toBe('urgent_quota');
  240 |       expect.soft((await batchOf(lead, nb.json.batchId)).batch.priority, '① (ข) ชุดยังเป็นปกติ').toBe('normal');
  241 |       const q1 = await queue(lead);
  242 |       expect.soft(q1.urgent.usedToday, '① ตัวนับยังเป็น 5').toBe(5);
  243 |       expect.soft(q1.urgent.limitPerDay, '① / 5').toBe(5);
  244 |     } finally {
  245 |       resumeReader();
  246 |     }
  247 | 
  248 |     // ② รีเซ็ตตั้งต้น · 3 งานด้วยปุ่ม + 2 งานด้วยการติ๊กตอนอัปโหลด
  249 |     await logout();
  250 |     await reset(M_URL);
  251 |     await login();
  252 |     pauseReader();
  253 |     try {
  254 |       const cl2 = await clientId(lead, 'CL-02');
  255 |       expect.soft(await usedToday(lead), '② ก่อนเริ่ม 0').toBe(0);
  256 |       let from = 30;
  257 |       const log: any[] = [];
  258 |       for (let i = 1; i <= 3; i++) {
  259 |         const nb = await upload(lead, { clientId: cl2, files: okFiles(5, from) }); from += 5;
  260 |         expect(nb.status, `② ชุดปกติที่ ${i}`).toBe(201);
  261 |         const u = await urgentViaPage(page, nb.json.batchId);
  262 |         log.push({ via: 'W10', i, resp: u.resp });
  263 |         expect.soft(u.resp?.status, `② งานที่ ${i} (ปุ่ม) ตั้งได้`).toBe(200);
  264 |         expect.soft(await usedToday(lead), `② ตัวนับ ${i}`).toBe(i);
  265 |       }
  266 |       for (let i = 4; i <= 5; i++) {
  267 |         const r = await upload(lead, { clientId: cl2, files: okFiles(5, from), urgent: true }); from += 5;
  268 |         log.push({ via: 'W7', i, status: r.status, json: r.json });
  269 |         expect.soft(r.status, `② งานที่ ${i} (ติ๊กตอนอัปโหลด) ตั้งได้`).toBe(201);
  270 |         expect.soft(r.json.priority, `② งานที่ ${i} เป็นงานด่วน`).toBe('urgent');
  271 |         expect.soft(await usedToday(lead), `② ตัวนับ ${i}`).toBe(i);
  272 |       }
  273 |       // งานที่ 6 ทั้ง 2 ช่องทาง
  274 |       const w7 = await upload(lead, { clientId: cl2, files: okFiles(5, from), urgent: true }); from += 5;
  275 |       log.push({ via: 'W7', i: 6, status: w7.status, json: w7.json });
  276 |       expect.soft(w7.status, '② งานที่ 6 W7 → 409').toBe(409);
  277 |       expect.soft(w7.json?.error, '② งานที่ 6 W7 urgent_quota').toBe('urgent_quota');
  278 |       const nb6 = await upload(lead, { clientId: cl2, files: okFiles(5, from) });
  279 |       expect(nb6.status, '② ชุดปกติสำหรับงานที่ 6').toBe(201);
  280 |       const w10 = await urgentViaPage(page, nb6.json.batchId);
  281 |       log.push({ via: 'W10', i: 6, resp: w10.resp });
  282 |       await shot(testInfo, page, '② งานที่ 6 กดปุ่มด่วน');
  283 |       expect.soft(w10.resp?.status, '② งานที่ 6 W10 → 409').toBe(409);
  284 |       expect.soft(w10.resp?.json?.error, '② งานที่ 6 W10 urgent_quota').toBe('urgent_quota');
  285 |       const q2 = await queue(lead);
  286 |       await evidence(testInfo, '② ลำดับการตั้งด่วน', { log, w23: q2 });
> 287 |       expect.soft(q2.urgent.usedToday, '② ตัวนับ 5 / 5').toBe(5);
      |                                                          ^ Error: ② ตัวนับ 5 / 5
  288 |       expect.soft(q2.urgent.limitPerDay, '② / 5').toBe(5);
  289 |     } finally {
  290 |       resumeReader();
  291 |     }
  292 |     pendingAP(testInfo, 'AP-05', 'โควตาทั้งสำนักงานทดสอบด้วยหัวหน้าคนเดียว (U-03) ผ่าน 2 ช่องทาง · การทดสอบด้วยหัวหน้า 2 คนรอ U-07');
  293 |   } finally {
  294 |     await logout();
  295 |   }
  296 | });
  297 | 
  298 | // ================================================================= TC-4-05
  299 | test('TC-4-05 วันใหม่เริ่มนับ 0', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  300 |   await reset(M_URL, { urgentYesterday: 5, urgentToday: 0 });
  301 |   const lead = await apiAs(M_URL, 'U03');
  302 |   const { context, page } = await pageAs(browser, M_URL, 'U03');
  303 |   try {
  304 |     const cl2 = await clientId(lead, 'CL-02');
  305 |     const q0 = await queue(lead);
  306 |     await evidence(testInfo, 'W23 ก่อนเริ่ม', q0);
  307 |     expect.soft(q0.urgent.usedToday, 'งานเมื่อวาน 23:59 ไม่ถูกนับในวันนี้ (0)').toBe(0);
  308 |     const r = await upload(lead, { clientId: cl2, files: okFiles(5, 1), urgent: true });
  309 |     await evidence(testInfo, 'W7 5 ไฟล์ urgent=true', r);
  310 |     expect.soft(r.status, 'ตั้งได้').toBe(201);
  311 |     expect.soft(r.json.priority, 'ชุดเป็นงานด่วน').toBe('urgent');
  312 |     expect.soft(await usedToday(lead), 'ตัวนับวันนี้ 0 + 1 = 1').toBe(1);
  313 |     if (r.json.batchId) {
  314 |       await page.goto(`/batches/${r.json.batchId}`);
  315 |       await expect.soft(page.getByTestId('batch-priority'), 'batch-priority = ด่วน').toContainText('ด่วน');
  316 |       await shot(testInfo, page, 'หน้าชุดงานด่วนวันใหม่');
  317 |     }
  318 |   } finally {
  319 |     await context.close();
  320 |     await lead.dispose();
  321 |   }
  322 | });
  323 | 
  324 | // ================================================================= TC-4-06
  325 | test('TC-4-06 งานด่วนไม่ติดเพดานคิว', { tag: ['@P1', '@A'] }, async ({ browser }, testInfo) => {
  326 |   await reset(M_URL, { pendingNormal: 400 });
  327 |   const lead = await apiAs(M_URL, 'U03');
  328 |   const staff = await apiAs(M_URL, 'U01');
  329 |   const { context, page } = await pageAs(browser, M_URL, 'U01');
  330 |   try {
  331 |     const cl2 = await clientId(lead, 'CL-02');
  332 |     const cl1 = await clientId(staff, 'CL-01');
  333 |     // ① U-03 10 ไฟล์ติ๊กด่วน
  334 |     const u = await upload(lead, { clientId: cl2, files: okFiles(10, 1), urgent: true });
  335 |     await evidence(testInfo, '① W7 10 ไฟล์ urgent=true', u);
  336 |     expect.soft(u.status, '① รับชุดด่วน').toBe(201);
  337 |     expect.soft(u.json.accepted, '① รับ 10').toBe(10);
  338 |     const q = await queue(lead);
  339 |     await evidence(testInfo, '① W23', q);
  340 |     expect.soft(q.normal.pending, '① ใบงานปกติค้างยังเป็น 400').toBe(400);
  341 |     // ② U-01 1 ไฟล์ปกติ (ผ่านหน้า /upload)
  342 |     let n = await uploadViaPage(page, cl1, okFiles(1, 50), false);
  343 |     await shot(testInfo, page, '② U-01 ส่ง 1 ไฟล์ขณะคิวเต็ม');
  344 |     if (!n) {
  345 |       testInfo.annotations.push({ type: 'note', description: '② หน้าเว็บกันไว้ก่อนส่ง จึงยิง W7 ด้วย API' });
  346 |       n = await upload(staff, { clientId: cl1, files: okFiles(1, 50) });
  347 |     }
  348 |     await evidence(testInfo, '② W7 1 ไฟล์ปกติ', n);
  349 |     expect.soft(n.status, '② 400 + 1 = 401 > 400 → 429').toBe(429);
  350 |     expect.soft(n.json?.error, '② queue_full').toBe('queue_full');
  351 |     expect.soft(n.json?.retryAfterMinutes, '② N = ปัดขึ้น(1 ÷ 8) = 1 นาที').toBe(1);
  352 |     await expect.soft(page.getByTestId('upload-retry-minutes'), '② upload-retry-minutes = 1').toHaveText(/^\D*1\D*$/);
  353 |   } finally {
  354 |     await context.close();
  355 |     await lead.dispose();
  356 |     await staff.dispose();
  357 |   }
  358 | });
  359 | 
  360 | // ================================================================= TC-4-07 ★
  361 | test('TC-4-07 ★ งานด่วน 10 ใบมีผลภายใน 5 นาที (smoke ของ NFR-03)', { tag: ['@P1', '@R'] }, async ({}, testInfo) => {
  362 |   testInfo.annotations.push({ type: 'blocked', description: 'รอบปล่อยรุ่น ★: ต้องใช้ใบจริง 100 ไฟล์ เกินงบรอบปกติ/งบของขั้นนี้ (120 ใบ) และต้องได้อนุมัติหัวหน้าทีมทดสอบ' });
  363 |   test.skip(true, 'รอบปล่อยรุ่น ★ เท่านั้น (2 × 50 ไฟล์จริง ต้องได้อนุมัติหัวหน้าทีมทดสอบ)');
  364 | });
  365 | 
  366 | // ================================================================= TC-4-08
  367 | type Shape = { key: 'a' | 'b' | 'c' | 'd'; u: number; n: number; expected: string[] };
  368 | const SHAPES: Shape[] = [
  369 |   { key: 'a', u: 3, n: 2, expected: ['U1', 'U2', 'U3', 'N1', 'N2'] },
  370 |   { key: 'b', u: 4, n: 2, expected: ['U1', 'U2', 'U3', 'U4', 'N1', 'N2'] },
  371 |   { key: 'c', u: 5, n: 2, expected: ['U1', 'U2', 'U3', 'U4', 'N1', 'U5', 'N2'] },
  372 |   { key: 'd', u: 5, n: 0, expected: ['U1', 'U2', 'U3', 'U4', 'U5'] },
  373 | ];
  374 | 
  375 | /** Parse `gpu.sh log worker0` -> per receipt id: go events (queue, attempt) and read events, in log order. */
  376 | function parseWorkerLog(log: string) {
  377 |   const goOrder: { id: string; queue: string; attempt: number; time: string }[] = [];
  378 |   const reads: { id: string; ok: string; outcome: string }[] = [];
  379 |   for (const line of log.split(/\r?\n/)) {
  380 |     const g = line.match(/^(\S+ \S+) .*receipt=([0-9a-f-]{36}) go queue=(urgent|normal) attempt=(\d+)/);
  381 |     if (g) { goOrder.push({ time: g[1], id: g[2], queue: g[3], attempt: Number(g[4]) }); continue; }
  382 |     const r = line.match(/receipt=([0-9a-f-]{36}) read ok=(True|False).*-> (\w+)/);
  383 |     if (r) reads.push({ id: r[1], ok: r[2], outcome: r[3] });
  384 |   }
  385 |   return { goOrder, reads };
  386 | }
  387 | 
```