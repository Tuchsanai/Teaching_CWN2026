# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: member.spec.ts >> TC-MEM-03 แลกแต้ม 99 / 100 / 199 / 250
- Location: tests\fixtures.ts:169:3

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 900
Received: 902.5
```

# Test source

```ts
  1  | import { tc, test, expect, open, loginUI, logoutUI, bookToStep3, quoteTotal, settle, type UserKey } from './fixtures';
  2  | 
  3  | const S = test.step;
  4  | 
  5  | tc('TC-MEM-01', async ({ page }) => {
  6  |   const rows: [UserKey, string, string, string][] = [
  7  |     ['U04', '฿9,999', 'Silver', '0%'],
  8  |     ['U07', '฿10,000', 'Gold', '5%'],
  9  |     ['U05', '฿29,999', 'Gold', '5%'],
  10 |     ['U02', '฿30,000', 'Platinum', '10%'],
  11 |   ];
  12 |   for (const [u, spend, tier, pct] of rows) {
  13 |     await S(`${u} ยอดสะสม ${spend} → ${tier} ${pct}`, async () => {
  14 |       await logoutUI(page);
  15 |       await loginUI(page, u);
  16 |       await open(page, '/account');
  17 |       await expect.soft(page.getByTestId('account-tier')).toContainText(tier);
  18 |       await expect.soft(page.getByTestId('account-tier-pct')).toContainText(pct);
  19 |     });
  20 |   }
  21 | });
  22 | 
  23 | tc('TC-MEM-02', async ({ page }) => {
  24 |   const rows: [UserKey, string][] = [
  25 |     ['U04', 'อีก ฿1 ถึง Gold'],
  26 |     ['U07', 'อีก ฿20,000 ถึง Platinum'],
  27 |     ['U06', 'อยู่ระดับสูงสุดแล้ว'],
  28 |   ];
  29 |   for (const [u, msg] of rows) {
  30 |     await S(`${u} → "${msg}"`, async () => {
  31 |       await logoutUI(page);
  32 |       await loginUI(page, u);
  33 |       await open(page, '/account');
  34 |       await expect.soft(page.getByTestId('account-tier-message')).toContainText(msg);
  35 |       if (u === 'U06') await expect.soft(page.locator('main')).not.toContainText(/[−-]\s*฿\s*15,000/);
  36 |     });
  37 |   }
  38 | });
  39 | 
  40 | tc('TC-MEM-03', async ({ page, api }) => {
  41 |   const s01 = { service: 'S01', type: 'single' as const, date: '2026-10-20', time: '10:00' };
  42 |   await S('U01 (99 แต้ม) → ช่องแลกแต้มกดไม่ได้', async () => {
  43 |     await loginUI(page, 'U01');
  44 |     await bookToStep3(page, s01);
  45 |     await settle(page, () => page.getByTestId('book-points-info').innerText().catch(() => ''));
  46 |     await expect.soft(page.getByTestId('book-points')).toBeDisabled();
  47 |   });
  48 |   await S('U05 (100 แต้ม) แลก 1 ก้อน → ฿1,000 − 5% − ฿50 = ฿900', async () => {
  49 |     await logoutUI(page); await loginUI(page, 'U05');
  50 |     await bookToStep3(page, s01);
  51 |     await page.getByTestId('book-points').selectOption('1');
> 52 |     expect.soft(await quoteTotal(page)).toBe(900);
     |                                         ^ Error: expect(received).toBe(expected) // Object.is equality
  53 |   });
  54 |   await S('U06 (199 แต้ม) แลก 2 ก้อน → ❌', async () => {
  55 |     await logoutUI(page); await loginUI(page, 'U06');
  56 |     await bookToStep3(page, s01);
  57 |     await settle(page, () => page.getByTestId('book-points-info').innerText().catch(() => ''));
  58 |     const opts = await page.getByTestId('book-points').locator('option').evaluateAll((o) => o.map((x) => (x as HTMLOptionElement).value));
  59 |     expect.soft(opts, 'ตัวเลือกแลกแต้มของ U06').not.toContain('2');
  60 |     const u06 = await api.as('U06');
  61 |     const r = await u06.post('/api/price', { type: 'single', serviceCode: 'S01', people: 1, date: '2026-10-20', time: '10:00', redeemBlocks: 2 });
  62 |     expect.soft(r.status >= 400 && r.status < 500, `API แลก 2 ก้อน ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  63 |   });
  64 |   await S('U04 (250 แต้ม) ตัวเลือกสูงสุด 2 ครั้ง · แลก 3 ก้อน → ❌', async () => {
  65 |     await logoutUI(page); await loginUI(page, 'U04');
  66 |     await bookToStep3(page, s01);
  67 |     await settle(page, () => page.getByTestId('book-points-info').innerText().catch(() => ''));
  68 |     const opts = (await page.getByTestId('book-points').locator('option').evaluateAll((o) => o.map((x) => (x as HTMLOptionElement).value)))
  69 |       .map(Number).filter((n) => !Number.isNaN(n));
  70 |     expect.soft(Math.max(...opts), 'ตัวเลือกสูงสุดของ U04').toBe(2);
  71 |     const u04 = await api.as('U04');
  72 |     const r = await u04.post('/api/price', { type: 'single', serviceCode: 'S01', people: 1, date: '2026-10-20', time: '10:00', redeemBlocks: 3 });
  73 |     expect.soft(r.status >= 400 && r.status < 500, `API แลก 3 ก้อน ต้อง 4xx (ได้ ${r.status})`).toBe(true);
  74 |   });
  75 | });
  76 | 
  77 | tc('TC-MEM-04', async ({ page, api }) => {
  78 |   await S('ก่อนกด: แต้ม U01 = 99', async () => {
  79 |     const u01 = await api.as('U01');
  80 |     expect.soft((await u01.get('/api/me')).json.points).toBe(99);
  81 |   });
  82 |   await S('owner เปิด /admin แล้วกด "ใช้บริการเสร็จ" ที่ B06 (วันนี้ 15:00)', async () => {
  83 |     await loginUI(page, 'owner');
  84 |     await open(page, '/admin');
  85 |     // 👀 ช่องวันที่ของ /admin เปิดมาเป็น 11 ต.ค. ทั้งที่ "วันนี้ของระบบ" = 10 ต.ค. → เลือกวันที่เองให้ตรงกับ B06
  86 |     await page.getByTestId('admin-date').fill('2026-10-10');
  87 |     await page.getByTestId('admin-complete-B06').click();
  88 |     await expect.soft(page.getByTestId('admin-result-B06')).toBeVisible();
  89 |   });
  90 |   await S('หลังรีโหลด /account ของ U01: แต้ม 99 + floor(950 ÷ 100) = 108', async () => {
  91 |     await logoutUI(page);
  92 |     await loginUI(page, 'U01');
  93 |     await open(page, '/account');
  94 |     await expect.soft(page.getByTestId('account-points')).toHaveAttribute('data-points', '108');
  95 |   });
  96 | });
  97 | 
```