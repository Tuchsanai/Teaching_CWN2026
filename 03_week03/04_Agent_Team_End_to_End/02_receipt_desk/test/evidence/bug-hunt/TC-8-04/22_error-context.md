# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 58-portal.spec.ts >> 5.8 ลูกค้าภายนอก >> TC-8-04 ตัวเลขขึ้นเมื่อยืนยัน และหายเมื่อเปิดกลับ
- Location: tests\58-portal.spec.ts:405:3

# Error details

```
Error: ① สรุป พ.ย. = 1,340.00 + 100.00 = 1,440.00

expect(received).toBe(expected) // Object.is equality

Expected: 144000
Received: 123950
```

```
Error: ① CAT-01 = 1,200.50 + 100.00 = 1,300.50

expect(received).toBe(expected) // Object.is equality

Expected: 130050
Received: 110000
```

```
Error: ① รวมหมวด = 1,440.00

expect(received).toBe(expected) // Object.is equality

Expected: 144000
Received: 123950
```

```
Error: ① W19 total = 1,440.00

expect(received).toBe(expected) // Object.is equality

Expected: 144000
Received: 123950
```

```
Error: ① W19 CAT-01 = 1,300.50

expect(received).toBe(expected) // Object.is equality

Expected: 130050
Received: 110000
```

```
Error: ① W19 รวมหมวด = 1,440.00

expect(received).toBe(expected) // Object.is equality

Expected: 144000
Received: 123950
```

```
Error: ② สรุป พ.ย. กลับเป็น 1,340.00

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

```
Error: ② CAT-01 = 1,200.50

expect(received).toBe(expected) // Object.is equality

Expected: 120050
Received: 100000
```

```
Error: ② W19 total = 1,340.00

expect(received).toBe(expected) // Object.is equality

Expected: 134000
Received: 113950
```

```
Error: ② W19 CAT-01 = 1,200.50

expect(received).toBe(expected) // Object.is equality

Expected: 120050
Received: 100000
```

# Page snapshot

```yaml
- generic [ref=f2e1]:
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
      - link "ค้างเกินกำหนด" [ref=f2e10] [cursor=pointer]:
        - /url: /overdue
      - link "สรุปรายเดือน" [ref=f2e11] [cursor=pointer]:
        - /url: /reports
      - link "เวลาตรวจ · GPU" [ref=f2e12] [cursor=pointer]:
        - /url: /insights
    - generic [ref=f2e13]:
      - generic [ref=f2e14]: คุณกิตติ
      - generic [ref=f2e15]: หัวหน้าทีมบัญชี
      - button "ออกจากระบบ" [ref=f2e16] [cursor=pointer]
  - main [ref=f2e17]:
    - generic [ref=f2e18]:
      - generic [ref=f2e19]:
        - generic [ref=f2e20]:
          - link "← คิวรอตรวจ" [ref=f2e21] [cursor=pointer]:
            - /url: /review
          - heading "ตรวจใบเสร็จ ok-100__001.jpg" [level=1] [ref=f2e22]
          - paragraph [ref=f2e23]:
            - text: ร้านข้าวแกงสมชาย · รับเมื่อ 19 พ.ย. 2569 17:36 · สถานะ
            - strong [ref=f2e24]: รอตรวจ
        - 'generic "NFR-09: เฉลี่ยต้องน้อยกว่า 120 วินาทีต่อใบ · เป้าหมายทีม ≤ 40 วินาที" [ref=f2e25]': เวลาตรวจ 0:02
      - generic [ref=f2e27]:
        - text: ✓ ใบปกติ — ตรวจยอดรวมเทียบกับรูปช่องเดียวแล้วยืนยันได้
        - generic [ref=f2e28]: · ความมั่นใจยอดรวม 0.9900
      - generic [ref=f2e29]:
        - generic [ref=f2e30]:
          - generic [ref=f2e31]:
            - button "ย่อรูป" [ref=f2e32] [cursor=pointer]: −
            - generic [ref=f2e33]: 100%
            - button "ขยายรูป" [ref=f2e34] [cursor=pointer]: +
            - button "พอดี" [ref=f2e35] [cursor=pointer]
            - button "หมุนรูป" [ref=f2e36] [cursor=pointer]: ⟳
            - link "เปิดรูปในแท็บใหม่ ↗" [ref=f2e37] [cursor=pointer]:
              - /url: /api/receipts/60f53e3f-b659-4fa7-b3d1-f83f68655868/image
          - img "รูปใบเสร็จ ok-100__001.jpg" [ref=f2e39]
        - generic [ref=f2e40]:
          - generic [ref=f2e41]:
            - generic [ref=f2e42]:
              - generic [ref=f2e43]: ชื่อร้าน
              - generic [ref=f2e44]: "ระบบอ่าน: ร้านตัวอย่าง"
            - textbox "ชื่อร้าน" [ref=f2e45]: ร้านตัวอย่าง
          - generic [ref=f2e46]:
            - generic [ref=f2e47]:
              - generic [ref=f2e48]: วันที่บนใบ
              - generic [ref=f2e49]: "ระบบอ่าน: 18 พ.ย. 2569 (2026-11-18)"
            - textbox "วันที่บนใบ" [ref=f2e50]: 2026-11-18
          - generic [ref=f2e51]:
            - generic [ref=f2e52]:
              - generic [ref=f2e53]: รายการสินค้าและราคา
              - generic [ref=f2e54]:
                - text: ผลรวมรายการ
                - strong [ref=f2e55]: "100.00"
                - text: บาท
                - generic [ref=f2e56]: · ต่างจากยอดรวม 0.00
            - table [ref=f2e57]:
              - rowgroup [ref=f2e58]:
                - row [ref=f2e59]:
                  - columnheader "#" [ref=f2e60]
                  - columnheader "รายการ" [ref=f2e61]
                  - columnheader "ราคา" [ref=f2e62]
                  - columnheader [ref=f2e63]
              - rowgroup [ref=f2e64]:
                - row [ref=f2e65]:
                  - cell "1" [ref=f2e66]
                  - cell [ref=f2e67]:
                    - textbox "ชื่อรายการบรรทัด 1" [ref=f2e68]: ข้าวสาร
                  - cell [ref=f2e69]:
                    - textbox "ราคาบรรทัด 1" [ref=f2e70]: "45.00"
                  - cell [ref=f2e71]:
                    - button "ลบ" [ref=f2e72] [cursor=pointer]
                - row [ref=f2e73]:
                  - cell "2" [ref=f2e74]
                  - cell [ref=f2e75]:
                    - textbox "ชื่อรายการบรรทัด 2" [ref=f2e76]: น้ำมันพืช
                  - cell [ref=f2e77]:
                    - textbox "ราคาบรรทัด 2" [ref=f2e78]: "30.00"
                  - cell [ref=f2e79]:
                    - button "ลบ" [ref=f2e80] [cursor=pointer]
                - row [ref=f2e81]:
                  - cell "3" [ref=f2e82]
                  - cell [ref=f2e83]:
                    - textbox "ชื่อรายการบรรทัด 3" [ref=f2e84]: น้ำตาลทราย
                  - cell [ref=f2e85]:
                    - textbox "ราคาบรรทัด 3" [ref=f2e86]: "25.00"
                  - cell [ref=f2e87]:
                    - button "ลบ" [ref=f2e88] [cursor=pointer]
            - button "+ เพิ่มรายการ" [ref=f2e89] [cursor=pointer]
          - generic [ref=f2e90]:
            - generic [ref=f2e91]:
              - generic [ref=f2e92]: ยอดรวม (บาท)
              - generic [ref=f2e93]: "ระบบอ่าน: 100.00"
            - textbox "ยอดรวม" [active] [ref=f2e94]: "100.00"
          - generic [ref=f2e95]:
            - generic [ref=f2e96]: หมวดรายจ่าย
            - combobox "หมวดรายจ่าย" [ref=f2e98]:
              - option "— เลือกหมวด —"
              - option "วัตถุดิบ" [selected]
              - option "ค่าแก๊ส"
              - option "ค่าน้ำแข็ง"
              - option "อื่น ๆ"
          - generic [ref=f2e99]:
            - generic [ref=f2e100] [cursor=pointer]:
              - checkbox "เทียบยอดรวมกับรูปแล้ว" [ref=f2e101]
              - text: เทียบยอดรวมกับรูปแล้ว
            - generic [ref=f2e102]:
              - button "บันทึก" [disabled]
              - button "ยืนยัน" [disabled]
              - button "ข้าม → ใบถัดไป" [ref=f2e103] [cursor=pointer]
            - list [ref=f2e104]:
              - listitem [ref=f2e105]: ติ๊ก "เทียบยอดรวมกับรูปแล้ว"
            - paragraph [ref=f2e106]: Enter = ช่องถัดไป · Ctrl/⌘+Enter = ยืนยัน · Ctrl/⌘+S = บันทึก · Alt+→ = ใบถัดไป
          - button "ดูค่าเดิมและประวัติการแก้" [ref=f2e108] [cursor=pointer]
  - alert [ref=f2e109]
```

# Test source

```ts
  360 |       await evidence(testInfo, 'U-05 W11 (S-06) · W12 S-06 · W19 2026-11', { w11status: w11r.status(), w11s06, w12status: w12r.status(), w12, w19status: w19r.status(), w19 });
  361 |       expect.soft(w11s06, 'W11 ของลูกค้ามี S-06').toBeTruthy();
  362 |       expect.soft(w12r.status(), 'W12 S-06 (ร้านตัวเอง)').toBe(200);
  363 |       expect.soft(numberFields(w11s06), 'W11 S-06 ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ').toEqual([]);
  364 |       expect.soft(numberFields(w12), 'W12 S-06 ไม่มียอดรวม/รายการ/ราคา/ความมั่นใจ').toEqual([]);
  365 |       expect.soft(leakedValues(w11s06, RE_500), 'W11 S-06 ไม่มี 500.00 / 500 / 50000').toEqual([]);
  366 |       expect.soft(leakedValues(w12, RE_500), 'W12 S-06 ไม่มี 500.00 / 500 / 50000').toEqual([]);
  367 |       expect.soft(leakedValues(w11, RE_500), 'W11 ทั้งคำตอบไม่มี 500.00 / 500 / 50000').toEqual([]);
  368 |       expect.soft(leakedValues(w19, RE_500), 'W19 ไม่มี 500.00 / 500 / 50000').toEqual([]);
  369 | 
  370 |       // summary 1,340.00 (not 1,840.00) · categories 1,340.00
  371 |       expect.soft(satang(st.summary), 'portal-summary-total พ.ย. = 1,340.00 (ไม่ใช่ 1,840.00)').toBe(134000);
  372 |       const catSum = st.cats.reduce((a, c) => a + satang(c.text), 0);
  373 |       expect.soft(catSum, 'ยอดแยกหมวดบนหน้ารวม = 1,340.00').toBe(134000);
  374 |       expect.soft(w19r.status(), 'W19 ของลูกค้า').toBe(200);
  375 |       expect.soft(satang(w19.total), 'W19 total = 1,340.00').toBe(134000);
  376 |       expect.soft((w19.categories ?? []).reduce((a: number, c: any) => a + satang(c.total), 0), 'W19 ยอดแยกหมวดรวม = 1,340.00').toBe(134000);
  377 |     } finally {
  378 |       await context.close(); await office.dispose(); await client.dispose();
  379 |     }
  380 |   });
  381 | 
  382 |   test('TC-8-03 ลูกค้าส่งใบเอง', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  383 |     test.setTimeout(20 * 60_000);
  384 |     const s = await customerUploadsTwo(browser, testInfo);
  385 |     try {
  386 |       expect.soft(s.readTimeout, '② ทั้ง 2 ID เป็นรอตรวจภายใน 5 นาที (ถ้าไม่ = หมดเวลาอ่าน)').toBe(false);
  387 |       const reviewCL01 = (await officeReceipts(s.office, `&client_id=${s.cl01}`)).filter(r => r.status === 'review');
  388 |       await evidence(testInfo, '② ใบรอตรวจของ CL-01 (office)', reviewCL01.map(r => ({ id: r.id, fileName: r.fileName, status: r.status })));
  389 |       for (const id of s.ids) expect.soft(reviewCL01.map(r => r.id), `② ${id} เป็นรอตรวจ`).toContain(id);
  390 |       expect.soft(reviewCL01.length, '② รวมกับ S-06 = 3 ใบรอตรวจของ CL-01').toBe(3);
  391 | 
  392 |       // customer refreshes /portal
  393 |       await s.cust.page.goto('/portal');
  394 |       await s.cust.page.getByTestId('portal-month-input').waitFor({ state: 'visible' });
  395 |       await shot(testInfo, s.cust.page, '② U-05 รีเฟรช /portal หลังอ่านเสร็จ');
  396 |       await expectNoNumbersForCustomer(s.cust.page, s.client, s.ids, s.files, testInfo, '②');
  397 |       const rows = await portalRows(s.cust.page, s.ids);
  398 |       s.ids.forEach((id, i) => expect.soft(rows[id].status, `② แถว ${s.files[i]} สถานะ`).toBe(STATUS_WAITING));
  399 |     } finally {
  400 |       await s.cust.context.close(); await s.st.context.close();
  401 |       await s.office.dispose(); await s.staff.dispose(); await s.client.dispose();
  402 |     }
  403 |   });
  404 | 
  405 |   test('TC-8-04 ตัวเลขขึ้นเมื่อยืนยัน และหายเมื่อเปิดกลับ', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  406 |     test.setTimeout(20 * 60_000);
  407 |     // ต่อจาก TC-8-03: repeat its setup so this test runs on its own
  408 |     const s = await customerUploadsTwo(browser, testInfo);
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
> 460 |       expect.soft(satang((w19b.categories ?? []).find((c: any) => c.id === cat01)?.total), '② W19 CAT-01 = 1,200.50').toBe(120050);
      |                                                                                                                       ^ Error: ② W19 CAT-01 = 1,200.50
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
  509 |       expect.soft(queueKeys, '② คำตอบไม่มีฟิลด์จำนวนใบค้างหรือเพดานของสำนักงาน [ข้อสมมติของแผน]').toEqual([]);
  510 |     } finally {
  511 |       await context.close(); await office.dispose();
  512 |     }
  513 |   });
  514 | });
  515 | 
```