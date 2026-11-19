# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 56-reports.spec.ts >> 5.6 รายงานรายเดือน >> TC-6-07 รายงาน GPU 1 เทียบ 2 ใบ · ต้องมีตารางและสูตรถูก
- Location: tests\56-reports.spec.ts:356:3

# Error details

```
Error: แถว GPU 1 ใบ มีค่า ใบ·เวลา·ใบต่อนาที·ค่าเช่า·บาทต่อ 100 ใบ (ได้ ["1","ยังไม่มีผลวัด"])

expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

```
Error: แถว GPU 2 ใบ มีค่า ใบ·เวลา·ใบต่อนาที·ค่าเช่า·บาทต่อ 100 ใบ (ได้ ["2","ยังไม่มีผลวัด"])

expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

```
Error: gpu-verdict ไม่ใช่ "ยังไม่มีข้อมูล/ผลวัด"

expect(received).not.toMatch(expected)

Expected pattern: not /ยังไม่มี/
Received string:      "ยังไม่มีผลวัดครบทั้ง 1 และ 2 GPU"
```

```
Error: gpu-speedup เป็นตัวเลข (ได้ "—")

expect(received).not.toBeNaN()

Received: NaN
```

```
Error: gpu-efficiency เป็นตัวเลข (ได้ "—")

expect(received).not.toBeNaN()

Received: NaN
```

```
Error: gpu-cost-per-100 เป็นตัวเลข (ได้ "—")

expect(received).not.toBeNaN()

Received: NaN
```

```
Error: gpu-speedup = ผลขั้นที่ 12 (แสดง 2.08)

expect(received).toMatch(expected)

Expected pattern: /2\.08/
Received string:  "—"
```

```
Error: gpu-efficiency = ผลขั้นที่ 12 (แสดง 104%)

expect(received).toBe(expected) // Object.is equality

Expected: 104
Received: NaN
```

```
Error: gpu-verdict = คุ้ม (ผลขั้นที่ 12)

expect(received).toMatch(expected)

Expected pattern: /คุ้ม/
Received string:  "ยังไม่มีผลวัดครบทั้ง 1 และ 2 GPU"
```

# Page snapshot

```yaml
- generic [active] [ref=f2e1]:
  - banner [ref=f2e2]:
    - link "ReceiptDesk" [ref=f2e3] [cursor=pointer]:
      - /url: /
    - navigation [ref=f2e5]:
      - link "ชุดใบเสร็จ" [ref=f2e6] [cursor=pointer]:
        - /url: /batches
      - link "รายการใบ" [ref=f2e7] [cursor=pointer]:
        - /url: /receipts
      - link "อ่านไม่ได้" [ref=f2e8] [cursor=pointer]:
        - /url: /unreadable
      - link "ค้างเกินกำหนด" [ref=f2e9] [cursor=pointer]:
        - /url: /overdue
      - link "สรุปรายเดือน" [ref=f2e10] [cursor=pointer]:
        - /url: /reports
      - link "เวลาตรวจ · GPU" [ref=f2e11] [cursor=pointer]:
        - /url: /insights
    - generic [ref=f2e12]:
      - generic [ref=f2e13]: คุณอรทัย
      - generic [ref=f2e14]: เจ้าของสำนักงาน
      - button "ออกจากระบบ" [ref=f2e15] [cursor=pointer]
  - main [ref=f2e16]:
    - heading "เวลาตรวจ · GPU 1 เทียบ 2 ใบ" [level=1] [ref=f2e17]
    - generic [ref=f2e18]:
      - heading "เวลาตรวจต่อใบ (เปิดใบจนกดยืนยัน)" [level=2] [ref=f2e19]
      - generic [ref=f2e20]:
        - generic [ref=f2e21]:
          - generic [ref=f2e22]: เฉลี่ยต่อใบ (วินาที)
          - generic [ref=f2e23]: —
        - generic [ref=f2e24]:
          - generic [ref=f2e25]: จำนวนใบที่นับ
          - generic [ref=f2e26]: "0"
        - generic [ref=f2e27]:
          - generic [ref=f2e28]: เป้าหมาย
          - generic [ref=f2e29]: < 120
      - table [ref=f2e30]:
        - rowgroup [ref=f2e31]:
          - row [ref=f2e32]:
            - columnheader "ชุด (รับเมื่อ)" [ref=f2e33]
            - columnheader "ลูกค้า" [ref=f2e34]
            - columnheader "ใบที่ยืนยัน" [ref=f2e35]
            - columnheader "เฉลี่ย (วินาที)" [ref=f2e36]
            - columnheader "ใบติดธง" [ref=f2e37]
            - columnheader "ใบปกติ" [ref=f2e38]
        - rowgroup [ref=f2e39]:
          - row [ref=f2e40]:
            - cell "ยังไม่มีใบที่ยืนยันพร้อมเวลาตรวจ" [ref=f2e41]
    - generic [ref=f2e42]:
      - heading "GPU 1 ใบ เทียบ 2 ใบ (งานชุดเดียวกัน)" [level=2] [ref=f2e43]
      - table [ref=f2e44]:
        - rowgroup [ref=f2e45]:
          - row [ref=f2e46]:
            - columnheader "จำนวน GPU" [ref=f2e47]
            - columnheader "ใบ" [ref=f2e48]
            - columnheader "เวลา (นาที)" [ref=f2e49]
            - columnheader "ใบต่อนาที" [ref=f2e50]
            - columnheader "ค่าเช่า (บาท)" [ref=f2e51]
            - columnheader "บาทต่อ 100 ใบ" [ref=f2e52]
            - columnheader "วัดเมื่อ" [ref=f2e53]
        - rowgroup [ref=f2e54]:
          - row [ref=f2e55]:
            - cell "1" [ref=f2e56]
            - cell "ยังไม่มีผลวัด" [ref=f2e57]
          - row [ref=f2e58]:
            - cell "2" [ref=f2e59]
            - cell "ยังไม่มีผลวัด" [ref=f2e60]
      - generic [ref=f2e61]:
        - generic [ref=f2e62]:
          - generic [ref=f2e63]: Speedup (เท่า)
          - generic [ref=f2e64]: —
        - generic [ref=f2e65]:
          - generic [ref=f2e66]: Efficiency (%)
          - generic [ref=f2e67]: —
        - generic [ref=f2e68]:
          - generic [ref=f2e69]: บาทต่อ 100 ใบ (2 GPU)
          - generic [ref=f2e70]: —
      - generic [ref=f2e71]: ยังไม่มีผลวัดครบทั้ง 1 และ 2 GPU
  - alert [ref=f2e72]
```

# Test source

```ts
  312 |         await u01.page.getByTestId('confirm-button').click();
  313 |         const res = await resp;
  314 |         measured.push({ file: r.fileName, seconds: (Date.now() - t0) / 1000, status: res ? res.status() : null });
  315 |         expect(res?.status(), `ยืนยัน ${r.fileName} ผ่านหน้าเว็บ`).toBe(200);
  316 |       }
  317 |       await evidence(testInfo, 'held times (open -> confirm click)', measured);
  318 | 
  319 |       // U-01 (staff) calls W21 -> rejected
  320 |       const w21Staff = await staff.get('/api/reports/review-time');
  321 |       await evidence(testInfo, 'W21 as U-01', { status: w21Staff.status(), body: await w21Staff.text() });
  322 |       expect.soft(w21Staff.status(), 'U-01 เรียก W21 ถูกปฏิเสธ (403)').toBe(403);
  323 | 
  324 |       // U-03 and U-04 see the same value on /insights; batch average = 40 s ± 3
  325 |       const seen: Record<string, { page: number; api: number; apiRow: any }> = {};
  326 |       for (const user of ['U03', 'U04'] as const) {
  327 |         const s = await pageAs(browser, M_URL, user);
  328 |         try {
  329 |           await s.page.goto('/insights');
  330 |           const table = s.page.getByTestId('review-time-table');
  331 |           await expect(table).toBeVisible();
  332 |           const row = table.locator('tbody tr', { hasText: 'ร้านข้าวแกงสมชาย' }).first();
  333 |           let pageVal = NaN;
  334 |           if (await row.isVisible().catch(() => false)) {
  335 |             const cells = await row.locator('td').allInnerTexts();
  336 |             pageVal = numOf(cells[3]); // ชุด | ลูกค้า | ใบที่ยืนยัน | เฉลี่ย (วินาที) | ...
  337 |             await evidence(testInfo, `${user} /insights batch row`, cells);
  338 |           }
  339 |           await shot(testInfo, s.page, `${user} /insights review time`);
  340 |           const w21 = await (await s.context.request.get('/api/reports/review-time')).json().catch(() => ({}));
  341 |           await evidence(testInfo, `W21 as ${user}`, w21);
  342 |           const apiRow = (w21.batches ?? []).find((b: any) => b.batchId === batchId || b.id === batchId);
  343 |           const apiVal = numOf(apiRow?.averageSeconds ?? apiRow?.avgSeconds ?? apiRow?.average);
  344 |           seen[user] = { page: pageVal, api: apiVal, apiRow };
  345 |           expect.soft(pageVal, `${user}: /insights แถวของชุดนี้ เฉลี่ย = 40 ± 3 วินาที`).toBeGreaterThanOrEqual(37);
  346 |           expect.soft(pageVal, `${user}: /insights แถวของชุดนี้ เฉลี่ย = 40 ± 3 วินาที`).toBeLessThanOrEqual(43);
  347 |           expect.soft(apiVal, `${user}: W21 batches[ชุดนี้] เฉลี่ย = 40 ± 3 วินาที`).toBeGreaterThanOrEqual(37);
  348 |           expect.soft(apiVal, `${user}: W21 batches[ชุดนี้] เฉลี่ย = 40 ± 3 วินาที`).toBeLessThanOrEqual(43);
  349 |         } finally { await s.context.close(); }
  350 |       }
  351 |       expect.soft(seen.U03?.page, 'U-03 และ U-04 เห็นค่าเดียวกันบน /insights').toBe(seen.U04?.page);
  352 |       expect.soft(seen.U03?.api, 'U-03 และ U-04 ได้ค่าเดียวกันจาก W21').toBe(seen.U04?.api);
  353 |     } finally { await u01.context.close(); await staff.dispose(); }
  354 |   });
  355 | 
  356 |   test('TC-6-07 รายงาน GPU 1 เทียบ 2 ใบ · ต้องมีตารางและสูตรถูก', { tag: ['@P2', '@A'] }, async ({ browser }, testInfo) => {
  357 |     await reset(M_URL);
  358 |     const step12 = { t1: 116.2, t2: 56.0 }; // results/capacity/summary.json mean_t_1worker_s / mean_t_2workers_s
  359 |     const step12Speedup = step12.t1 / step12.t2; // 2.075 -> shown 2.08 · efficiency 103.75% -> 104% -> คุ้ม
  360 |     const { context, page } = await pageAs(browser, M_URL, 'U04');
  361 |     try {
  362 |       await page.goto('/insights');
  363 |       const table = page.getByTestId('gpu-table');
  364 |       await expect.soft(table, 'gpu-table แสดง').toBeVisible();
  365 |       const w22 = await (await context.request.get('/api/reports/gpu')).json().catch(() => ({}));
  366 |       await evidence(testInfo, 'W22 as U-04', w22);
  367 | 
  368 |       const rows = await table.locator('tbody tr').evaluateAll(trs => trs.map(tr => [...tr.querySelectorAll('td,th')].map(td => (td as HTMLElement).innerText.trim())));
  369 |       const txt = async (id: string) => (await page.getByTestId(id).innerText().catch(() => '')).trim();
  370 |       const shown = { speedup: await txt('gpu-speedup'), efficiency: await txt('gpu-efficiency'), costPer100: await txt('gpu-cost-per-100'), verdict: await txt('gpu-verdict') };
  371 |       await evidence(testInfo, '/insights GPU table + cards', { rows, shown });
  372 |       await shot(testInfo, page, 'U-04 /insights GPU');
  373 | 
  374 |       // must have the table WITH values (empty / "ยังไม่มีข้อมูล" = fail FR-30)
  375 |       const row1 = rows.find(r => r[0] === '1');
  376 |       const row2 = rows.find(r => r[0] === '2');
  377 |       // columns: จำนวน GPU | ใบ | เวลา (นาที) | ใบต่อนาที | ค่าเช่า (บาท) | บาทต่อ 100 ใบ | วัดเมื่อ
  378 |       const hasValues = (r?: string[]) => !!r && r.length >= 6 && !Number.isNaN(numOf(r[1])) && !Number.isNaN(numOf(r[2])) && !Number.isNaN(numOf(r[3])) && !Number.isNaN(numOf(r[4])) && !Number.isNaN(numOf(r[5]));
  379 |       expect.soft(hasValues(row1), `แถว GPU 1 ใบ มีค่า ใบ·เวลา·ใบต่อนาที·ค่าเช่า·บาทต่อ 100 ใบ (ได้ ${JSON.stringify(row1)})`).toBe(true);
  380 |       expect.soft(hasValues(row2), `แถว GPU 2 ใบ มีค่า ใบ·เวลา·ใบต่อนาที·ค่าเช่า·บาทต่อ 100 ใบ (ได้ ${JSON.stringify(row2)})`).toBe(true);
  381 |       expect.soft(shown.verdict, 'gpu-verdict ไม่ใช่ "ยังไม่มีข้อมูล/ผลวัด"').not.toMatch(/ยังไม่มี/);
  382 |       expect.soft(numOf(shown.speedup), `gpu-speedup เป็นตัวเลข (ได้ "${shown.speedup}")`).not.toBeNaN();
  383 |       expect.soft(numOf(shown.efficiency), `gpu-efficiency เป็นตัวเลข (ได้ "${shown.efficiency}")`).not.toBeNaN();
  384 |       expect.soft(numOf(shown.costPer100), `gpu-cost-per-100 เป็นตัวเลข (ได้ "${shown.costPer100}")`).not.toBeNaN();
  385 | 
  386 |       // recompute from the rows (only when they exist)
  387 |       if (hasValues(row1) && hasValues(row2)) {
  388 |         const calc = (r: string[]) => ({ n: numOf(r[1]), min: numOf(r[2]), rate: numOf(r[3]), rent: numOf(r[4]), per100: numOf(r[5]) });
  389 |         const a = calc(row1!), b = calc(row2!);
  390 |         const half = (s: string) => 0.5 * Math.pow(10, -decimalsOf(s)) + 1e-9; // display rounding tolerance
  391 |         expect.soft(Math.abs(a.rate - a.n / a.min), 'GPU 1: ใบต่อนาที = ใบ ÷ เวลา').toBeLessThanOrEqual(half(row1![3]) + 0.05);
  392 |         expect.soft(Math.abs(b.rate - b.n / b.min), 'GPU 2: ใบต่อนาที = ใบ ÷ เวลา').toBeLessThanOrEqual(half(row2![3]) + 0.05);
  393 |         expect.soft(Math.abs(a.per100 - a.rent / a.n * 100), 'GPU 1: บาทต่อ 100 ใบ = ค่าเช่า ÷ ใบ × 100').toBeLessThanOrEqual(half(row1![5]) + 0.01);
  394 |         expect.soft(Math.abs(b.per100 - b.rent / b.n * 100), 'GPU 2: บาทต่อ 100 ใบ = ค่าเช่า ÷ ใบ × 100').toBeLessThanOrEqual(half(row2![5]) + 0.01);
  395 |         const speedup = (b.n / b.min) / (a.n / a.min); // value before rounding
  396 |         const eff = speedup / 2 * 100;
  397 |         expect.soft(Math.abs(numOf(shown.speedup) - speedup), `gpu-speedup = อัตรา 2 ÷ อัตรา 1 = ${speedup.toFixed(4)}`).toBeLessThanOrEqual(half(shown.speedup));
  398 |         expect.soft(Math.abs(numOf(shown.efficiency) - eff), `gpu-efficiency = Speedup ÷ 2 = ${eff.toFixed(2)}%`).toBeLessThanOrEqual(half(shown.efficiency));
  399 |         expect.soft(Math.abs(numOf(shown.costPer100) - b.rent / b.n * 100), 'gpu-cost-per-100 (2 GPU) = ค่าเช่า ÷ ใบ × 100').toBeLessThanOrEqual(half(shown.costPer100) + 0.01);
  400 |         if (speedup >= 1.6) {
  401 |           expect.soft(shown.verdict, `Speedup ${speedup.toFixed(4)} ≥ 1.6 → คุ้ม`).toMatch(/คุ้ม/);
  402 |           expect.soft(shown.verdict, `Speedup ${speedup.toFixed(4)} ≥ 1.6 → ไม่ใช่ "ไม่คุ้ม"`).not.toMatch(/ไม่คุ้ม/);
  403 |         } else {
  404 |           testInfo.annotations.push({ type: 'note', description: `Speedup ${speedup.toFixed(4)} < 1.6: verdict depends on SLO of 1 vs 2 GPU (not shown in the row); shown "${shown.verdict}"` });
  405 |         }
  406 |       }
  407 | 
  408 |       // compare with the step-12 measurement (116.2 vs 56.0 -> 2.075 shown 2.08 · 103.75% shown 104% · คุ้ม)
  409 |       await evidence(testInfo, 'step-12 reference', { ...step12, speedup: step12Speedup, efficiencyPct: step12Speedup / 2 * 100 });
  410 |       expect.soft(shown.speedup, 'gpu-speedup = ผลขั้นที่ 12 (แสดง 2.08)').toMatch(/2\.08/);
  411 |       expect.soft(Math.round(numOf(shown.efficiency)), 'gpu-efficiency = ผลขั้นที่ 12 (แสดง 104%)').toBe(104);
> 412 |       expect.soft(shown.verdict, 'gpu-verdict = คุ้ม (ผลขั้นที่ 12)').toMatch(/คุ้ม/);
      |                                                                       ^ Error: gpu-verdict = คุ้ม (ผลขั้นที่ 12)
  413 |       expect.soft(shown.verdict, 'gpu-verdict ไม่ใช่ ไม่คุ้ม').not.toMatch(/ไม่คุ้ม/);
  414 |     } finally { await context.close(); }
  415 |   });
  416 | });
  417 | 
```