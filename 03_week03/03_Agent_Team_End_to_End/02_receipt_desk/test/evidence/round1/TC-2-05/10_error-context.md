# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 52-flags.spec.ts >> TC-2-05 ผลต่างเกิน 1.00 บาท ทั้งขาดและเกิน ติดธง
- Location: tests\52-flags.spec.ts:190:1

# Error details

```
Error: diff-101.jpg: เหตุผลแสดงยอดรวมที่อ่าน 100 — text "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม 1.01 บาท (เกิน 1.00 บาท)"

expect(received).toContain(expected) // indexOf

Expected value: 10000
Received array: [101, 100]
```

```
Error: diff-101.jpg: เหตุผลแสดงผลรวมรายการ 98.99 — text "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม 1.01 บาท (เกิน 1.00 บาท)"

expect(received).toContain(expected) // indexOf

Expected value: 9899
Received array: [101, 100]
```

```
Error: diff-over-101.jpg: เหตุผลแสดงยอดรวมที่อ่าน 100 — text "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม 1.01 บาท (เกิน 1.00 บาท)"

expect(received).toContain(expected) // indexOf

Expected value: 10000
Received array: [101, 100]
```

```
Error: diff-over-101.jpg: เหตุผลแสดงผลรวมรายการ 101.01 — text "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม 1.01 บาท (เกิน 1.00 บาท)"

expect(received).toContain(expected) // indexOf

Expected value: 10101
Received array: [101, 100]
```

```
Error: diff-149.jpg: เหตุผลแสดงยอดรวมที่อ่าน 100 — text "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม 1.49 บาท (เกิน 1.00 บาท)"

expect(received).toContain(expected) // indexOf

Expected value: 10000
Received array: [149, 100]
```

```
Error: diff-149.jpg: เหตุผลแสดงผลรวมรายการ 98.51 — text "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม 1.49 บาท (เกิน 1.00 บาท)"

expect(received).toContain(expected) // indexOf

Expected value: 9851
Received array: [149, 100]
```

# Page snapshot

```yaml
- generic [ref=f6e1]:
  - banner [ref=f6e2]:
    - link "ReceiptDesk" [ref=f6e3] [cursor=pointer]:
      - /url: /
    - navigation [ref=f6e5]:
      - link "อัปโหลดชุด" [ref=f6e6] [cursor=pointer]:
        - /url: /upload
      - link "ชุดใบเสร็จ" [ref=f6e7] [cursor=pointer]:
        - /url: /batches
      - link "รายการใบ" [ref=f6e8] [cursor=pointer]:
        - /url: /receipts
      - link "อ่านไม่ได้" [ref=f6e9] [cursor=pointer]:
        - /url: /unreadable
      - link "สรุปรายเดือน" [ref=f6e10] [cursor=pointer]:
        - /url: /reports
    - generic [ref=f6e11]:
      - generic [ref=f6e12]: คุณแนน
      - generic [ref=f6e13]: พนักงานบัญชี
      - button "ออกจากระบบ" [ref=f6e14] [cursor=pointer]
  - main [ref=f6e15]:
    - generic [ref=f6e16]:
      - generic [ref=f6e17]:
        - generic [ref=f6e18]:
          - link "← คิวรอตรวจ" [ref=f6e19] [cursor=pointer]:
            - /url: /review
          - heading "ตรวจใบเสร็จ diff-149.jpg" [level=1] [ref=f6e20]
          - paragraph [ref=f6e21]:
            - text: ร้านข้าวแกงสมชาย · รับเมื่อ 19 พ.ย. 2569 17:10 · สถานะ
            - strong [ref=f6e22]: รอตรวจ
        - 'generic "NFR-09: เฉลี่ยต้องน้อยกว่า 120 วินาทีต่อใบ · เป้าหมายทีม ≤ 40 วินาที" [ref=f6e23]': เวลาตรวจ 0:00
      - note [ref=f6e25]:
        - strong [ref=f6e26]: ⚑ ใบติดธง ระบบไม่แน่ใจ — ตรวจทุกช่องเทียบกับรูป
        - list [ref=f6e27]:
          - listitem [ref=f6e28]: "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม 1.49 บาท (เกิน 1.00 บาท)"
        - paragraph [ref=f6e29]:
          - text: "ดูแล้ว:"
          - generic [ref=f6e30]: ✓ ชื่อร้าน
          - generic [ref=f6e31]: ○ วันที่
          - generic [ref=f6e32]: ○ รายการสินค้า
          - generic [ref=f6e33]: ○ ราคาแต่ละรายการ
          - generic [ref=f6e34]: ○ ยอดรวม
      - generic [ref=f6e35]:
        - generic [ref=f6e36]:
          - generic [ref=f6e37]:
            - button "ย่อรูป" [ref=f6e38] [cursor=pointer]: −
            - generic [ref=f6e39]: 100%
            - button "ขยายรูป" [ref=f6e40] [cursor=pointer]: +
            - button "พอดี" [ref=f6e41] [cursor=pointer]
            - button "หมุนรูป" [ref=f6e42] [cursor=pointer]: ⟳
            - link "เปิดรูปในแท็บใหม่ ↗" [ref=f6e43] [cursor=pointer]:
              - /url: /api/receipts/c8fbacef-a3a2-4de9-8f1c-13ce951176ee/image
          - img "รูปใบเสร็จ diff-149.jpg" [ref=f6e45]
        - generic [ref=f6e46]:
          - generic [ref=f6e47]:
            - generic [ref=f6e48]:
              - generic [ref=f6e49]: ชื่อร้าน
              - generic [ref=f6e50]: "ระบบอ่าน: ร้านตัวอย่าง"
            - textbox "ชื่อร้าน" [active] [ref=f6e51]: ร้านตัวอย่าง
          - generic [ref=f6e52]:
            - generic [ref=f6e53]:
              - generic [ref=f6e54]: วันที่บนใบ
              - generic [ref=f6e55]: "ระบบอ่าน: 18 พ.ย. 2569 (2026-11-18)"
            - textbox "วันที่บนใบ" [ref=f6e56]: 2026-11-18
          - generic [ref=f6e57]:
            - generic [ref=f6e58]:
              - generic [ref=f6e59]: รายการสินค้าและราคา
              - generic [ref=f6e60]:
                - text: ผลรวมรายการ
                - strong [ref=f6e61]: "98.51"
                - text: บาท
                - generic [ref=f6e62]: · ต่างจากยอดรวม -1.49 (เกิน 1.00 บาท)
            - table [ref=f6e63]:
              - rowgroup [ref=f6e64]:
                - row [ref=f6e65]:
                  - columnheader "#" [ref=f6e66]
                  - columnheader "รายการ" [ref=f6e67]
                  - columnheader "ราคา" [ref=f6e68]
                  - columnheader [ref=f6e69]
              - rowgroup [ref=f6e70]:
                - row [ref=f6e71]:
                  - cell "1" [ref=f6e72]
                  - cell [ref=f6e73]:
                    - textbox "ชื่อรายการบรรทัด 1" [ref=f6e74]: ข้าวสาร
                  - cell [ref=f6e75]:
                    - textbox "ราคาบรรทัด 1" [ref=f6e76]: "50.00"
                  - cell [ref=f6e77]:
                    - button "ลบ" [ref=f6e78] [cursor=pointer]
                - row [ref=f6e79]:
                  - cell "2" [ref=f6e80]
                  - cell [ref=f6e81]:
                    - textbox "ชื่อรายการบรรทัด 2" [ref=f6e82]: น้ำมันพืช
                  - cell [ref=f6e83]:
                    - textbox "ราคาบรรทัด 2" [ref=f6e84]: "48.51"
                  - cell [ref=f6e85]:
                    - button "ลบ" [ref=f6e86] [cursor=pointer]
            - button "+ เพิ่มรายการ" [ref=f6e87] [cursor=pointer]
          - generic [ref=f6e88]:
            - generic [ref=f6e89]:
              - generic [ref=f6e90]: ยอดรวม (บาท)
              - generic [ref=f6e91]: "ระบบอ่าน: 100.00"
            - textbox "ยอดรวม" [ref=f6e92]: "100.00"
          - generic [ref=f6e93]:
            - generic [ref=f6e94]: หมวดรายจ่าย
            - combobox "หมวดรายจ่าย" [ref=f6e96]:
              - option "— เลือกหมวด —" [selected]
              - option "วัตถุดิบ"
              - option "ค่าแก๊ส"
              - option "ค่าน้ำแข็ง"
              - option "อื่น ๆ"
          - generic [ref=f6e97]:
            - generic [ref=f6e98] [cursor=pointer]:
              - checkbox "เทียบยอดรวมกับรูปแล้ว" [ref=f6e99]
              - text: เทียบยอดรวมกับรูปแล้ว
            - generic [ref=f6e100]:
              - button "บันทึก" [disabled]
              - button "ยืนยัน" [disabled]
              - button "ข้าม → ใบถัดไป" [ref=f6e101] [cursor=pointer]
            - list [ref=f6e102]:
              - listitem [ref=f6e103]: ติ๊ก "เทียบยอดรวมกับรูปแล้ว"
              - listitem [ref=f6e104]: "ใบติดธง: เปิดดูให้ครบทุกช่อง (ยังไม่ได้ดู: วันที่ · รายการสินค้า · ราคาแต่ละรายการ · ยอดรวม)"
              - listitem [ref=f6e105]: เลือกหมวดรายจ่าย
            - paragraph [ref=f6e106]: Enter = ช่องถัดไป · Ctrl/⌘+Enter = ยืนยัน · Ctrl/⌘+S = บันทึก · Alt+→ = ใบถัดไป
          - button "ดูค่าเดิมและประวัติการแก้" [ref=f6e108] [cursor=pointer]
  - alert [ref=f6e109]
```

# Test source

```ts
  105 |   await evidence(testInfo, 'E6 W23 queue after reset', q);
  106 |   expect(q?.normal?.pending, 'E6: ใบงานปกติค้าง 0').toBe(0);
  107 |   expect(q?.urgent?.usedToday, 'E6: งานด่วนวันนี้ 0 / 5').toBe(0);
  108 |   expect(q?.workers?.alive, 'E6: workersAlive 2').toBe(2);
  109 |   testInfo.annotations.push({ type: 'E6', description: 'gateway queue (GET /v1/queue) not checked from the test (API key of the gateway is not used by the suite); W23 pending 0 · urgent 0 · workers 2 checked' });
  110 |   return api;
  111 | }
  112 | 
  113 | const isFlagged = (r: any) => !!(r?.flags && (r.flags.flagged || r.flags.lowConfidence || r.flags.mismatch));
  114 | 
  115 | // ---------------------------------------------------------------- tests
  116 | 
  117 | test('TC-2-01 อ่านครบ 5 ช่อง ใบปกติ', { tag: ['@P1', '@M'] }, async ({ browser }, testInfo) => {
  118 |   const f = 'ok-100__001.jpg';
  119 |   const p = await prepareM(browser, testInfo, [f]);
  120 |   try {
  121 |     const v = await openReview(p.page, p.ids[f]);
  122 |     await shot(testInfo, p.page, 'review page ok-100__001');
  123 |     await evidence(testInfo, 'review page values', v);
  124 | 
  125 |     expect.soft(v.merchant, 'ชื่อร้าน').toBe('ร้านตัวอย่าง');
  126 |     expect.soft(v.date, 'วันที่').toBe('2026-11-18');
  127 |     expect.soft(v.items.length, 'รายการ 3 บรรทัด').toBe(3);
  128 |     const want = [4500, 3000, 2500];
  129 |     want.forEach((sat, i) => {
  130 |       expect.soft(v.items[i]?.name?.trim() ?? '', `ชื่อรายการบรรทัด ${i + 1} ไม่ว่าง`).not.toBe('');
  131 |       expect.soft(toSatang(v.items[i]?.price), `ราคาบรรทัด ${i + 1}`).toBe(sat);
  132 |     });
  133 |     expect.soft(toSatang(v.total), 'ยอดรวม 100.00').toBe(10000);
  134 |     expect.soft(toSatang(v.itemsSum), 'items-sum = 45.00 + 30.00 + 25.00 = 100.00').toBe(4500 + 3000 + 2500);
  135 |     expect.soft(v.low.present, 'ไม่ติดธง "ไม่แน่ใจยอดรวม"').toBe(false);
  136 |     expect.soft(v.mismatch.present, 'ไม่ติดธง "ยอดไม่ตรงรายการ"').toBe(false);
  137 |     pendingAP(testInfo, 'AP-06', `ชื่อรายการที่ได้: ${v.items.map(i => `"${i.name}" ${i.price}`).join(' · ')}`);
  138 |   } finally { await p.context.close(); await p.api.dispose(); }
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
> 205 |       expect.soft(nums, `${c.f}: เหตุผลแสดงผลรวมรายการ ${(c.sum / 100).toFixed(2)} — text "${v.mismatch.text}"`).toContain(c.sum);
      |                                                                                                                  ^ Error: diff-149.jpg: เหตุผลแสดงผลรวมรายการ 98.51 — text "ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม 1.49 บาท (เกิน 1.00 บาท)"
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
  299 |       expect.soft(d.slice(0, 10), `${g.file}: วันที่ไม่ใช่ 1900-01-01`).not.toBe('1900-01-01');
  300 |       // ③ wrong total must be flagged
  301 |       if (!ok) expect.soft(flagged, `${g.file}: ยอดอ่าน ${r?.total} ≠ เฉลย ${g.total} ต้องติดธง`).toBe(true);
  302 |     }
  303 |     rows.push('', `ยอดถูก ${correct} / 12 = ${(correct / 12 * 100).toFixed(1)}% (M1 trend, not used to judge) · จำนวนรายการตรง n_items ${itemsMatch} / 12 (M7 trend) · ยอดผิดและไม่ติดธง ${wrongUnflagged}`);
  304 |     await evidence(testInfo, 'per-receipt comparison (satang)', rows.join('\n'));
  305 |     testInfo.annotations.push({ type: 'trend', description: `total correct ${correct}/12 · items count match ${itemsMatch}/12 · wrong & unflagged ${wrongUnflagged}` });
```