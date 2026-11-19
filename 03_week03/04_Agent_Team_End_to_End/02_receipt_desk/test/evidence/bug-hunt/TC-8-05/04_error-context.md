# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 58-portal.spec.ts >> 5.8 ลูกค้าภายนอก >> TC-8-05 ลูกค้าส่งใบเข้าร้านอื่นไม่ได้ และคิวเต็มจากหน้าลูกค้า
- Location: tests\58-portal.spec.ts:467:3

# Error details

```
Error: ② คำตอบไม่มีฟิลด์จำนวนใบค้างหรือเพดานของสำนักงาน [ข้อสมมติของแผน]

expect(received).toEqual(expected) // deep equality

- Expected  - 1
+ Received  + 4

- Array []
+ Array [
+   "pending=309",
+   "limit=400",
+ ]
```

# Page snapshot

```yaml
- generic [active] [ref=f2e1]:
  - banner [ref=f2e2]:
    - link "ReceiptDesk" [ref=f2e3] [cursor=pointer]:
      - /url: /
    - navigation [ref=f2e5]:
      - link "ใบเสร็จของร้าน" [ref=f2e6] [cursor=pointer]:
        - /url: /portal
    - generic [ref=f2e7]:
      - generic [ref=f2e8]: คุณมาลี
      - generic [ref=f2e9]: ลูกค้า · ร้านกาแฟมะลิ
      - button "ออกจากระบบ" [ref=f2e10] [cursor=pointer]
  - main [ref=f2e11]:
    - heading "ใบเสร็จของ ร้านกาแฟมะลิ" [level=1] [ref=f2e12]
    - generic [ref=f2e13]:
      - heading "ส่งใบเสร็จ" [level=2] [ref=f2e14]
      - generic [ref=f2e15]:
        - generic [ref=f2e16]:
          - text: ไฟล์ (JPG · PNG · PDF 1 หน้า · ไม่เกิน 10 MB ต่อไฟล์ · 1–100 ไฟล์)
          - button "ไฟล์ (JPG · PNG · PDF 1 หน้า · ไม่เกิน 10 MB ต่อไฟล์ · 1–100 ไฟล์)" [ref=f2e17]
        - button "ส่งใบเสร็จ" [ref=f2e18] [cursor=pointer]
      - paragraph [ref=f2e19]:
        - text: รับแล้ว
        - strong [ref=f2e20]: "0"
        - text: ใบ
      - alert [ref=f2e21]: ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก 2 นาที
    - generic [ref=f2e22]:
      - heading "ใบเสร็จของร้าน" [level=2] [ref=f2e23]
      - table [ref=f2e24]:
        - rowgroup [ref=f2e25]:
          - row [ref=f2e26]:
            - columnheader "ไฟล์" [ref=f2e27]
            - columnheader "รับเมื่อ" [ref=f2e28]
            - columnheader "สถานะ" [ref=f2e29]
            - columnheader "ร้านบนใบ" [ref=f2e30]
            - columnheader "วันที่บนใบ" [ref=f2e31]
            - columnheader "หมวด" [ref=f2e32]
            - columnheader "ยอดรวม (บาท)" [ref=f2e33]
        - rowgroup [ref=f2e34]:
          - row [ref=f2e35]:
            - cell "S-08.jpg" [ref=f2e36]
            - cell "05/11/2569 14:00" [ref=f2e37]
            - cell "ยืนยันแล้ว" [ref=f2e38]
            - cell "ร้านตัวอย่าง" [ref=f2e39]
            - cell "2026-11-05" [ref=f2e40]
            - cell "วัตถุดิบ" [ref=f2e41]
            - cell "999.00" [ref=f2e42]
    - generic [ref=f2e43]:
      - heading "รายจ่ายแยกหมวด (เฉพาะใบที่ยืนยันแล้ว · ตามวันที่บนใบ)" [level=2] [ref=f2e44]
      - generic [ref=f2e45]:
        - text: เดือน
        - textbox "เดือน" [ref=f2e46]: 2026-11
      - paragraph [ref=f2e47]:
        - text: ยอดรวมทั้งเดือน
        - strong [ref=f2e48]: "999.00"
        - text: บาท · 1 ใบ
      - table [ref=f2e49]:
        - rowgroup [ref=f2e50]:
          - row [ref=f2e51]:
            - columnheader "หมวด" [ref=f2e52]
            - columnheader "ใบ" [ref=f2e53]
            - columnheader "ยอด (บาท)" [ref=f2e54]
        - rowgroup [ref=f2e55]:
          - row [ref=f2e56]:
            - cell "วัตถุดิบ" [ref=f2e57]
            - cell "1" [ref=f2e58]
            - cell "999.00" [ref=f2e59]
          - row [ref=f2e60]:
            - cell "ค่าแก๊ส" [ref=f2e61]
            - cell "0" [ref=f2e62]
            - cell "0.00" [ref=f2e63]
          - row [ref=f2e64]:
            - cell "ค่าน้ำแข็ง" [ref=f2e65]
            - cell "0" [ref=f2e66]
            - cell "0.00" [ref=f2e67]
          - row [ref=f2e68]:
            - cell "อื่น ๆ" [ref=f2e69]
            - cell "0" [ref=f2e70]
            - cell "0.00" [ref=f2e71]
  - alert [ref=f2e72]
```

# Test source

```ts
  409 |     const lead = await pageAs(browser, M_URL, 'U03');
  410 |     try {
  411 |       expect(s.readTimeout, 'ขั้นตั้งต้น (TC-8-03): ทั้ง 2 ใบเป็นรอตรวจภายใน 5 นาที').toBe(false);
  412 |       const [id1, id2] = s.ids;
  413 |       const cat01 = await categoryId(s.office, 'CAT-01');
  414 | 
  415 |       // ① U-01 confirms __001 with CAT-01 through /receipts/[id]
  416 |       await s.st.page.goto(`/receipts/${id1}`);
  417 |       await s.st.page.getByTestId('category-select').selectOption(cat01);
  418 |       await s.st.page.getByTestId('total-checked-checkbox').check();
  419 |       await s.st.page.getByTestId('confirm-button').click();
  420 |       const c1 = await waitStatus(s.staff, [id1], ['confirmed'], 30_000).catch(e => { throw new Error('① U-01 ยืนยันไม่สำเร็จ: ' + e); });
  421 |       await evidence(testInfo, '① W12 __001 หลังยืนยัน (U-01)', c1[0]);
  422 |       await shot(testInfo, s.st.page, '① U-01 ยืนยัน __001');
  423 | 
  424 |       let st = await portalState(s.cust.page);
  425 |       let rows = await portalRows(s.cust.page, s.ids);
  426 |       await shot(testInfo, s.cust.page, '① U-05 /portal หลังยืนยัน __001');
  427 |       await evidence(testInfo, '① /portal หลังยืนยัน', { summary: st.summary, cats: st.cats, rows });
  428 |       expect.soft(rows[id1].totalCount, '① __001 มี portal-receipt-total').toBeGreaterThan(0);
  429 |       expect.soft(satang(rows[id1].total), '① __001 แสดงยอด 100.00').toBe(10000);
  430 |       expect.soft(rows[id2].totalCount, '① __002 ยังไม่มีตัวเลข (portal-receipt-total)').toBe(0);
  431 |       expect.soft(rowExtraDigits(rows[id2].row, s.files[1]), '① แถว __002 ยังไม่มีตัวเลข').toBeNull();
  432 |       expect.soft(satang(st.summary), '① สรุป พ.ย. = 1,340.00 + 100.00 = 1,440.00').toBe(144000);
  433 |       expect.soft(satang(st.cats.find(c => c.id === cat01)?.text), '① CAT-01 = 1,200.50 + 100.00 = 1,300.50').toBe(130050);
  434 |       expect.soft(st.cats.reduce((a, c) => a + satang(c.text), 0), '① รวมหมวด = 1,440.00').toBe(144000);
  435 |       const w19a = await (await s.client.get('/api/reports/categories?month=2026-11')).json();
  436 |       await evidence(testInfo, '① W19 ของลูกค้า', w19a);
  437 |       expect.soft(satang(w19a.total), '① W19 total = 1,440.00').toBe(144000);
  438 |       expect.soft(satang((w19a.categories ?? []).find((c: any) => c.id === cat01)?.total), '① W19 CAT-01 = 1,300.50').toBe(130050);
  439 |       expect.soft((w19a.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0), '① W19 รวมหมวด = 1,440.00').toBe(144000);
  440 | 
  441 |       // ② U-03 reopens __001
  442 |       lead.page.on('dialog', d => d.accept().catch(() => undefined));
  443 |       await lead.page.goto(`/receipts/${id1}`);
  444 |       const reason = lead.page.getByTestId('reopen-reason-input');
  445 |       if (await reason.isVisible().catch(() => false)) await reason.fill('ทดสอบ TC-8-04 เปิดใบกลับ');
  446 |       await lead.page.getByTestId('reopen-button').click();
  447 |       const r2 = await waitStatus(s.staff, [id1], ['review'], 30_000).catch(e => { throw new Error('② U-03 เปิดใบกลับไม่สำเร็จ: ' + e); });
  448 |       await evidence(testInfo, '② W12 __001 หลังเปิดกลับ (office)', r2[0]);
  449 |       await shot(testInfo, lead.page, '② U-03 เปิด __001 กลับ');
  450 | 
  451 |       st = await portalState(s.cust.page);
  452 |       await shot(testInfo, s.cust.page, '② U-05 /portal หลังเปิดกลับ');
  453 |       await evidence(testInfo, '② /portal หลังเปิดกลับ', { summary: st.summary, cats: st.cats });
  454 |       await expectNoNumbersForCustomer(s.cust.page, s.client, [id1], [s.files[0]], testInfo, '② __001');
  455 |       expect.soft(satang(st.summary), '② สรุป พ.ย. กลับเป็น 1,340.00').toBe(134000);
  456 |       expect.soft(satang(st.cats.find(c => c.id === cat01)?.text), '② CAT-01 = 1,200.50').toBe(120050);
  457 |       const w19b = await (await s.client.get('/api/reports/categories?month=2026-11')).json();
  458 |       await evidence(testInfo, '② W19 ของลูกค้า', w19b);
  459 |       expect.soft(satang(w19b.total), '② W19 total = 1,340.00').toBe(134000);
  460 |       expect.soft(satang((w19b.categories ?? []).find((c: any) => c.id === cat01)?.total), '② W19 CAT-01 = 1,200.50').toBe(120050);
  461 |     } finally {
  462 |       await lead.context.close(); await s.cust.context.close(); await s.st.context.close();
  463 |       await s.office.dispose(); await s.staff.dispose(); await s.client.dispose();
  464 |     }
  465 |   });
  466 | 
  467 |   test('TC-8-05 ลูกค้าส่งใบเข้าร้านอื่นไม่ได้ และคิวเต็มจากหน้าลูกค้า', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  468 |     test.setTimeout(15 * 60_000);
  469 |     // ①
  470 |     await reset(M_URL);
  471 |     let office = await apiAs(M_URL, 'U04');
  472 |     const client5 = await apiAs(M_URL, 'U05');
  473 |     const cl01 = await clientId(office, 'CL-01');
  474 |     const cl02 = await clientId(office, 'CL-02');
  475 |     const count = async (o: APIRequestContext, cl: string) => (await officeReceipts(o, `&client_id=${cl}`)).length;
  476 |     const before = { cl01: await count(office, cl01), cl02: await count(office, cl02) };
  477 |     expect.soft(before, '① จำนวนใบตั้งต้น CL-01 = 7 · CL-02 = 1').toEqual({ cl01: 7, cl02: 1 });
  478 |     const up = await upload(client5, { clientId: cl02, files: ['ok-100__001.jpg'] });
  479 |     const after = { cl01: await count(office, cl01), cl02: await count(office, cl02) };
  480 |     const acceptedPath = up.status >= 200 && up.status < 300;
  481 |     await evidence(testInfo, '① U-05 W7 clientId=CL-02', { status: up.status, json: up.json, before, after, outcome: acceptedPath ? 'รับแล้วผูกร้านของบัญชี' : 'ปฏิเสธ' });
  482 |     testInfo.annotations.push({ type: '① ทางที่เกิด', description: acceptedPath ? `รับ (${up.status}) แล้วผูกร้านของบัญชี` : `ปฏิเสธ (${up.status})` });
  483 |     expect.soft(after.cl02, '① ทั้ง 2 ทาง CL-02 ต้องคงเป็น 1').toBe(1);
  484 |     if (acceptedPath) expect.soft(after.cl01, '① รับแล้วผูกร้านของบัญชี → CL-01 = 7 + 1 = 8').toBe(8);
  485 |     else expect.soft(after.cl01, '① ปฏิเสธ → CL-01 = 7').toBe(7);
  486 |     expect.soft([7, 8], '① ผลอยู่ในชุดที่ยอมรับ').toContain(after.cl01);
  487 |     await office.dispose(); await client5.dispose();
  488 | 
  489 |     // ② queue full from the portal
  490 |     await reset(M_URL, { pendingNormal: 309, workersAlive: 2 });
  491 |     office = await apiAs(M_URL, 'U04');
  492 |     const { context, page } = await pageAs(browser, M_URL, 'U06');
  493 |     try {
  494 |       const cl02before = await count(office, cl02);
  495 |       const r = await portalUpload(page, okFiles(100, 1));
  496 |       await shot(testInfo, page, '② U-06 /portal ส่ง 100 ไฟล์');
  497 |       const cl02after = await count(office, cl02);
  498 |       await evidence(testInfo, '② W7 จาก /portal (U-06 · 100 ไฟล์)', { ...r, cl02before, cl02after });
  499 |       expect.soft(r.status, '② 309 + 100 = 409 เกิน 9 → HTTP').toBe(429);
  500 |       expect.soft(r.json?.error, '② error').toBe('queue_full');
  501 |       expect.soft(r.json?.retryAfterMinutes, '② ปัดขึ้น 9 ÷ 8 = 2 นาที').toBe(2);
  502 |       expect.soft(r.errorText ?? '', '② ข้อความบนหน้า "ลองใหม่ในอีก 2 นาที"').toContain('ลองใหม่ในอีก 2 นาที');
  503 |       expect.soft(Number(r.json?.accepted ?? 0), '② รับ 0 ใบ (คำตอบ)').toBe(0);
  504 |       if (r.acceptedText !== null) expect.soft(int(r.acceptedText), '② portal-accepted-count = 0').toBe(0);
  505 |       expect.soft(cl02after - cl02before, '② รับ 0 ใบ (ไม่มีใบใหม่ของ CL-02)').toBe(0);
  506 |       const queueKeys: string[] = [];
  507 |       const walk = (o: any, p: string) => { if (o && typeof o === 'object') for (const [k, v] of Object.entries(o)) { const kp = p ? `${p}.${k}` : k; if (/pending|limit|queue|capacity|workers/i.test(k)) queueKeys.push(`${kp}=${JSON.stringify(v)}`); walk(v, kp); } };
  508 |       walk(r.json, '');
> 509 |       expect.soft(queueKeys, '② คำตอบไม่มีฟิลด์จำนวนใบค้างหรือเพดานของสำนักงาน [ข้อสมมติของแผน]').toEqual([]);
      |                                                                                                   ^ Error: ② คำตอบไม่มีฟิลด์จำนวนใบค้างหรือเพดานของสำนักงาน [ข้อสมมติของแผน]
  510 |     } finally {
  511 |       await context.close(); await office.dispose();
  512 |     }
  513 |   });
  514 | });
  515 | 
```