# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: price.spec.ts >> TC-PRICE-04 ลำดับคิดราคาเต็ม: กลุ่ม → แลกแต้ม → ค่ารถ
- Location: tests\fixtures.ts:169:3

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 3800
Received: 3810
```

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 3800
Received: 3810
```

# Test source

```ts
  1   | import { tc, test, expect, bookToStep3, toSummary, amount, loginUI, logoutUI, quoteTotal, open } from './fixtures';
  2   | 
  3   | const S = test.step;
  4   | 
  5   | tc('TC-PRICE-01', async ({ page }) => {
  6   |   await loginUI(page, 'U08');
  7   |   for (const [n, want, how] of [[3, 3000, 'ไม่ลด'], [4, 3600, '฿4,000 − ฿400'], [5, 4500, '฿5,000 − ฿500']] as const) {
  8   |     await S(`กลุ่ม ${n} คน S01 → ฿${want.toLocaleString('en-US')} (${how})`, async () => {
  9   |       await bookToStep3(page, { service: 'S01', type: 'group', people: n, date: '2026-10-20', time: '10:00' });
  10  |       expect.soft(await quoteTotal(page), `กลุ่ม ${n} คน`).toBe(want);
  11  |       await toSummary(page);
  12  |       expect.soft(await amount(page, 'summary-total'), `ใบสรุปกลุ่ม ${n} คน`).toBe(want);
  13  |     });
  14  |   }
  15  | });
  16  | 
  17  | tc('TC-PRICE-02', async ({ page }) => {
  18  |   await S('U01 (Gold 5%) กลุ่ม 4 คน → max(10%, 5%) = ฿3,600', async () => {
  19  |     await loginUI(page, 'U01');
  20  |     await bookToStep3(page, { service: 'S01', type: 'group', people: 4, date: '2026-10-20', time: '10:00' });
  21  |     expect.soft(await quoteTotal(page)).toBe(3600);
  22  |     await toSummary(page);
  23  |     expect.soft(await amount(page, 'summary-total')).toBe(3600);
  24  |   });
  25  |   await S('U02 (Platinum + เดือนเกิด) กลุ่ม 4 คน 31 ต.ค. เลือกเดือนเกิด → 20% = ฿3,200', async () => {
  26  |     await logoutUI(page);
  27  |     await loginUI(page, 'U02');
  28  |     await bookToStep3(page, { service: 'S01', type: 'group', people: 4, date: '2026-10-31', time: '10:00' });
  29  |     await page.getByTestId('book-birthday').check();
  30  |     expect.soft(await quoteTotal(page)).toBe(3200);
  31  |     await toSummary(page);
  32  |     expect.soft(await amount(page, 'summary-total')).toBe(3200);
  33  |   });
  34  | });
  35  | 
  36  | tc('TC-PRICE-03', async ({ page }) => {
  37  |   await loginUI(page, 'U02');
  38  |   await S('U02 นัด 20 ต.ค. ใช้เดือนเกิด → ฿1,000 − 20% = ฿800', async () => {
  39  |     await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
  40  |     await page.getByTestId('book-birthday').check();
  41  |     expect.soft(await quoteTotal(page)).toBe(800);
  42  |   });
  43  |   await S('U02 นัด 1 พ.ย. → ใช้เดือนเกิดไม่ได้ ราคา ฿900', async () => {
  44  |     await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-11-01', time: '10:00' });
  45  |     await expect.soft(page.getByTestId('book-birthday')).toHaveCount(0);
  46  |     expect.soft(await quoteTotal(page)).toBe(900);
  47  |   });
  48  |   await S('U05 (ใช้สิทธิ์ ต.ค. แล้ว) S07 นัด 20 ต.ค. → ไม่มีตัวเลือกเดือนเกิด ราคา ฿1,710', async () => {
  49  |     await logoutUI(page);
  50  |     await loginUI(page, 'U05');
  51  |     await bookToStep3(page, { service: 'S07', type: 'single', date: '2026-10-20', time: '10:00' });
  52  |     await expect.soft(page.getByTestId('book-birthday')).toHaveCount(0);
  53  |     expect.soft(await quoteTotal(page)).toBe(1710);
  54  |   });
  55  | });
  56  | 
  57  | tc('TC-PRICE-04', async ({ page }) => {
  58  |   await loginUI(page, 'U04');
  59  |   await S('U04 กลุ่ม 4 คน S01 · แลก 2 ก้อน · รถจาก H04 (12 กม.)', async () => {
  60  |     await bookToStep3(page, { service: 'S01', type: 'group', people: 4, date: '2026-10-20', time: '10:00' });
  61  |     await page.getByTestId('book-points').selectOption('2');
  62  |     await page.getByTestId('book-transport').check();
  63  |     await page.getByTestId('book-hotel').selectOption('H04');
  64  |   });
  65  |   await S('ยอด ฿4,000 − ฿400 − ฿100 + ฿300 = ฿3,800 · บรรทัดค่ารถ "1 คัน" (ทันที)', async () => {
  66  |     expect.soft(await quoteTotal(page)).toBe(3800);
  67  |     await toSummary(page);
> 68  |     expect.soft(await amount(page, 'summary-total')).toBe(3800);
      |                                                      ^ Error: expect(received).toBe(expected) // Object.is equality
  69  |     await expect.soft(page.getByTestId('summary-line-transport')).toContainText('1 คัน');
  70  |   });
  71  |   await S('ยืนยัน → หลังรีโหลด /account แต้มเหลือ 50', async () => {
  72  |     await page.getByTestId('book-confirm').click();
  73  |     await expect(page.getByTestId('booking-confirmation')).toBeVisible();
  74  |     await open(page, '/account');
  75  |     await expect.soft(page.getByTestId('account-points')).toHaveAttribute('data-points', '50');
  76  |   });
  77  | });
  78  | 
  79  | tc('TC-PRICE-05', async ({ page, api }) => {
  80  |   await loginUI(page, 'U01');
  81  |   let code = '';
  82  |   await S('U01 (Gold) S04 22 ต.ค. 13:00 + รถ H04 → ใบสรุป ฿2,200', async () => {
  83  |     await bookToStep3(page, { service: 'S04', type: 'single', date: '2026-10-22', time: '13:00' });
  84  |     await page.getByTestId('book-transport').check();
  85  |     await page.getByTestId('book-hotel').selectOption('H04');
  86  |     expect.soft(await quoteTotal(page)).toBe(2200);
  87  |     await toSummary(page);
  88  |     expect.soft(await amount(page, 'summary-total')).toBe(2200);
  89  |   });
  90  |   await S('ยืนยัน → นัดที่บันทึก = ฿2,200 (หลังรีโหลด /api/me/bookings)', async () => {
  91  |     await page.getByTestId('book-confirm').click();
  92  |     code = (await page.getByTestId('booking-confirmation').innerText()).match(/B\d+/)?.[0] ?? '';
  93  |     const u01 = await api.as('U01');
  94  |     const list = (await u01.get('/api/me/bookings')).json.bookings as any[];
  95  |     expect.soft(list.find((b) => b.code === code)?.total, `นัด ${code}`).toBe(2200);
  96  |   });
  97  |   await S('ยิง /api/bookings ด้วย quotedTotal = 1 → 409 (ทันที) และไม่มีนัดใหม่ (หลังรีโหลด)', async () => {
  98  |     const u01 = await api.as('U01');
  99  |     const before = ((await u01.get('/api/me/bookings')).json.bookings as any[]).length;
  100 |     const r = await u01.post('/api/bookings', { type: 'single', serviceCode: 'S04', people: 1, date: '2026-10-22', time: '13:00', hotelCode: 'H04', quotedTotal: 1 });
  101 |     expect.soft(r.status).toBe(409);
  102 |     const after = ((await u01.get('/api/me/bookings')).json.bookings as any[]).length;
  103 |     expect.soft(after).toBe(before);
  104 |   });
  105 | });
  106 | 
  107 | tc('TC-PRICE-06', async ({ page }) => {
  108 |   await loginUI(page, 'U02');
  109 |   const pkg = (people: number) => bookToStep3(page, { type: 'package', service: 'P01', people, date: '2026-10-20', time: '10:00' });
  110 |   await S('1 คน → ฿2,900 และไม่มีตัวเลือกเดือนเกิด', async () => {
  111 |     await pkg(1);
  112 |     await expect.soft(page.getByTestId('book-birthday')).toHaveCount(0);
  113 |     expect.soft(await quoteTotal(page)).toBe(2900);
  114 |   });
  115 |   await S('2 คน + รถ H04 → ฿5,800 (รถรวมแล้ว ฿0)', async () => {
  116 |     await pkg(2);
  117 |     await page.getByTestId('book-transport').check();
  118 |     await page.getByTestId('book-hotel').selectOption('H04');
  119 |     expect.soft(await quoteTotal(page)).toBe(5800);
  120 |     await toSummary(page);
  121 |     expect.soft(await amount(page, 'summary-total')).toBe(5800);
  122 |   });
  123 |   await S('4 คน → ฿11,600 (ไม่ลดกลุ่ม) — ดูราคาที่หน้า /package และ /api/price', async () => {
  124 |     // P01 ทำได้แค่ T01 T02 T06 (3 คน) หน้า /book จึงไม่มีรอบว่างสำหรับ 4 คน → ดูราคาจากเครื่องคิดเงินของหน้าแพ็กเกจแทน
  125 |     await open(page, '/package');
  126 |     const ppl = page.getByTestId('package-people');
  127 |     if (await ppl.evaluate((e) => e.tagName === 'SELECT')) await ppl.selectOption('4'); else await ppl.fill('4');
  128 |     await expect.soft(page.getByTestId('package-total')).toHaveAttribute('data-amount', '11600');
  129 |     const r = await page.request.post('/api/price', { data: { type: 'package', serviceCode: 'P01', people: 4, date: '2026-10-20', time: '10:00' } });
  130 |     expect.soft((await r.json()).total, 'POST /api/price แพ็กเกจ 4 คน (U02)').toBe(11600);
  131 |   });
  132 |   await S('2 คน + รถ H06 (15.1 กม.) → ❌ "อยู่นอกพื้นที่รับส่ง"', async () => {
  133 |     await pkg(2);
  134 |     await page.getByTestId('book-transport').check();
  135 |     await page.getByTestId('book-hotel').selectOption('H06');
  136 |     await expect.soft(page.getByTestId('book-quote-error-message')).toContainText('อยู่นอกพื้นที่รับส่ง');
  137 |   });
  138 | });
  139 | 
```