# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: giftcard.spec.ts >> TC-GC-04 รหัสบัตรที่ไม่มีจริงในหน้าจอง
- Location: tests\fixtures.ts:169:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByTestId('book-giftcard-error')
Expected: visible
Timeout: 7000ms
Error: element(s) not found

Call log:
  - Expect "soft toBeVisible" getByTestId('book-giftcard-error') with timeout 7000ms
  - waiting for getByTestId('book-giftcard-error')

```

```yaml
- link "ข้ามไปที่เนื้อหา":
  - /url: "#main"
- banner:
  - link "สบายใจ สปา":
    - /url: /
  - button "เปิดเพลงสปา"
  - group "เลือกภาษา":
    - button "ไทย" [pressed]
    - button "English"
    - button "中文"
  - link "เข้าสู่ระบบ":
    - /url: /login
  - navigation "เมนู":
    - link "หน้าแรก":
      - /url: /
    - link "บริการ":
      - /url: /services
    - link "จองคิว":
      - /url: /book
    - link "แพ็กเกจ":
      - /url: /package
    - link "นักบำบัด":
      - /url: /therapists
    - link "Gift Card":
      - /url: /giftcard
    - link "รถรับส่ง":
      - /url: /transport
    - link "ผู้ช่วยแชท":
      - /url: /chat
    - link "แบบทดสอบ":
      - /url: /quiz
    - link "วิเคราะห์ผิว":
      - /url: /skin
- main:
  - heading "จองคิว" [level=1]
  - list "จองคิว":
    - listitem: 1. บริการ
    - listitem: 2. วัน/เวลา
    - listitem: 3. ข้อมูลติดต่อ
    - listitem: 4. ยืนยัน
  - paragraph: ขั้นที่ 3 จาก 4
  - region "3. ข้อมูลติดต่อ":
    - heading "3. ข้อมูลติดต่อ" [level=2]
    - text: ชื่อผู้จอง
    - textbox "ชื่อผู้จอง": ทดสอบบัตรมั่ว
    - text: เบอร์โทร
    - textbox "เบอร์โทร": "0812345678"
    - paragraph: "ไม่ได้เข้าสู่ระบบ: จองด้วยชื่อ+เบอร์ได้ แต่ไม่ได้สะสมแต้ม"
    - heading "ส่วนลดและการชำระ" [level=3]
    - text: รหัส Gift Card
    - textbox "รหัส Gift Card":
      - /placeholder: SABAI-GC-XXXX
      - text: XXXX
    - button "ใช้บัตรนี้"
    - checkbox "ต้องการรถรับส่งจากโรงแรม"
    - text: ต้องการรถรับส่งจากโรงแรม
    - paragraph: "ยอดสุทธิ: ฿1,000"
    - button "ย้อนกลับ"
    - button "ถัดไป"
- contentinfo:
  - strong: สบายใจ สปา
  - text: เปิดทุกวัน 10:00–22:00 โทร
  - link "02-123-4567":
    - /url: tel:02-123-4567
- link "ผู้ช่วยแชท":
  - /url: /chat
- text: TC-GC-04 รหัสบัตรที่ไม่มีจริงในหน้าจอง · chromium
- alert
```

```
Error: expect(locator).not.toHaveText(expected) failed

Locator: getByTestId('book-giftcard-error')
Expected pattern: not /^\s*$/
Timeout: 7000ms
Error: element(s) not found

Call log:
  - Expect "soft not toHaveText" getByTestId('book-giftcard-error') with timeout 7000ms
  - waiting for getByTestId('book-giftcard-error')

```

```yaml
- link "ข้ามไปที่เนื้อหา":
  - /url: "#main"
- banner:
  - link "สบายใจ สปา":
    - /url: /
  - button "เปิดเพลงสปา"
  - group "เลือกภาษา":
    - button "ไทย" [pressed]
    - button "English"
    - button "中文"
  - link "เข้าสู่ระบบ":
    - /url: /login
  - navigation "เมนู":
    - link "หน้าแรก":
      - /url: /
    - link "บริการ":
      - /url: /services
    - link "จองคิว":
      - /url: /book
    - link "แพ็กเกจ":
      - /url: /package
    - link "นักบำบัด":
      - /url: /therapists
    - link "Gift Card":
      - /url: /giftcard
    - link "รถรับส่ง":
      - /url: /transport
    - link "ผู้ช่วยแชท":
      - /url: /chat
    - link "แบบทดสอบ":
      - /url: /quiz
    - link "วิเคราะห์ผิว":
      - /url: /skin
- main:
  - heading "จองคิว" [level=1]
  - list "จองคิว":
    - listitem: 1. บริการ
    - listitem: 2. วัน/เวลา
    - listitem: 3. ข้อมูลติดต่อ
    - listitem: 4. ยืนยัน
  - paragraph: ขั้นที่ 3 จาก 4
  - region "3. ข้อมูลติดต่อ":
    - heading "3. ข้อมูลติดต่อ" [level=2]
    - text: ชื่อผู้จอง
    - textbox "ชื่อผู้จอง": ทดสอบบัตรมั่ว
    - text: เบอร์โทร
    - textbox "เบอร์โทร": "0812345678"
    - paragraph: "ไม่ได้เข้าสู่ระบบ: จองด้วยชื่อ+เบอร์ได้ แต่ไม่ได้สะสมแต้ม"
    - heading "ส่วนลดและการชำระ" [level=3]
    - text: รหัส Gift Card
    - textbox "รหัส Gift Card":
      - /placeholder: SABAI-GC-XXXX
      - text: XXXX
    - button "ใช้บัตรนี้"
    - checkbox "ต้องการรถรับส่งจากโรงแรม"
    - text: ต้องการรถรับส่งจากโรงแรม
    - paragraph: "ยอดสุทธิ: ฿1,000"
    - button "ย้อนกลับ"
    - button "ถัดไป"
- contentinfo:
  - strong: สบายใจ สปา
  - text: เปิดทุกวัน 10:00–22:00 โทร
  - link "02-123-4567":
    - /url: tel:02-123-4567
- link "ผู้ช่วยแชท":
  - /url: /chat
- text: TC-GC-04 รหัสบัตรที่ไม่มีจริงในหน้าจอง · chromium
- alert
```

# Test source

```ts
  1   | import { tc, test, expect, open, loginUI, bookToStep3, fillContact, toSummary, amount, quoteTotal, settle } from './fixtures';
  2   | import type { Page } from '@playwright/test';
  3   | 
  4   | const S = test.step;
  5   | 
  6   | async function applyCard(page: Page, code: string) {
  7   |   await page.getByTestId('book-giftcard').fill(code);
  8   |   await page.getByTestId('book-giftcard-apply').click();
  9   |   await settle(page);
  10  | }
  11  | const backTo3 = async (page: Page) => {
  12  |   await page.getByTestId('book-back-4').click();
  13  |   await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
  14  | };
  15  | 
  16  | tc('TC-GC-01', async ({ page }) => {
  17  |   const buy = async (value: string) => {
  18  |     await open(page, '/giftcard');
  19  |     await page.getByTestId('gc-value').fill(value);
  20  |     await page.getByTestId('gc-design-label-lotus').click();
  21  |     await page.getByTestId('gc-channel-label-line').click();
  22  |     await page.getByTestId('gc-recipient').fill('แม่');
  23  |     await page.getByTestId('gc-submit').click();
  24  |   };
  25  |   for (const [v, ok] of [['499', false], ['500', true], ['10000', true], ['10001', false]] as const) {
  26  |     await S(`มูลค่า ฿${Number(v).toLocaleString('en-US')} ลายบัว LINE ถึง "แม่" → ${ok ? '✅' : '❌'}`, async () => {
  27  |       await buy(v);
  28  |       if (ok) {
  29  |         await expect.soft(page.getByTestId('gc-result')).toBeVisible();
  30  |         // ซื้อวันนี้ 10 ต.ค. 2026 + 365 วัน = 10 ต.ค. 2027
  31  |         await expect.soft(page.getByTestId('gc-expires')).toHaveText(/10 ต\.ค\. 2027|2027-10-10/);
  32  |       } else {
  33  |         await expect.soft(page.getByTestId('gc-error')).toBeVisible();
  34  |         await expect.soft(page.getByTestId('gc-result')).toHaveCount(0);
  35  |       }
  36  |     });
  37  |   }
  38  | });
  39  | 
  40  | tc('TC-GC-02', async ({ page }) => {
  41  |   await S('ไม่ล็อกอิน S01 ฿1,000 ถึงขั้น 3', async () => {
  42  |     await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
  43  |     await fillContact(page, 'ทดสอบบัตร', '0812345678');
  44  |   });
  45  |   await S('GC04 SABAI-GC-EXP (หมด 9 ต.ค.) → "บัตรหมดอายุแล้ว" ยอดสุทธิยัง ฿1,000', async () => {
  46  |     await applyCard(page, 'SABAI-GC-EXP');
  47  |     await expect.soft(page.getByTestId('book-giftcard-error')).toContainText('บัตรหมดอายุแล้ว');
  48  |     expect.soft(await quoteTotal(page)).toBe(1000);
  49  |     await toSummary(page);
  50  |     expect.soft(await amount(page, 'summary-total')).toBe(1000);
  51  |     await expect.soft(page.getByTestId('summary-line-giftcard')).toHaveCount(0);
  52  |     await backTo3(page);
  53  |   });
  54  |   await S('GC03 SABAI-GC-LAST (วันสุดท้าย ยอด ฿500) → จ่ายด้วยบัตร ฿500 + จ่ายเพิ่ม ฿500', async () => {
  55  |     await applyCard(page, 'SABAI-GC-LAST');
  56  |     await toSummary(page);
  57  |     expect.soft(Math.abs(await amount(page, 'summary-amount-giftcard'))).toBe(500);
  58  |     expect.soft(await amount(page, 'summary-amount-other')).toBe(500);
  59  |     await backTo3(page);
  60  |   });
  61  |   await S('GC05 SABAI-GC-ZERO (ยอด ฿0) → หักไม่ได้ มีข้อความแจ้ง ยอดที่ต้องจ่ายยัง ฿1,000', async () => {
  62  |     await applyCard(page, 'SABAI-GC-ZERO');
  63  |     await expect.soft(page.getByTestId('book-giftcard-error')).toBeVisible();
  64  |     await toSummary(page);
  65  |     await expect.soft(page.getByTestId('summary-line-giftcard')).toHaveCount(0);
  66  |     expect.soft(await amount(page, 'summary-amount-other')).toBe(1000);
  67  |   });
  68  | });
  69  | 
  70  | tc('TC-GC-03', async ({ page }) => {
  71  |   await loginUI(page, 'U04');
  72  |   await S('U04 (Silver) S06 ฿1,500 ใช้ GC01 SABAI-GC-2000 → จ่ายด้วยบัตร ฿1,500 จ่ายเพิ่ม ฿0 (ทันที)', async () => {
  73  |     await bookToStep3(page, { service: 'S06', type: 'single', date: '2026-10-20', time: '10:00' });
  74  |     await applyCard(page, 'SABAI-GC-2000');
  75  |     await toSummary(page);
  76  |     expect.soft(Math.abs(await amount(page, 'summary-amount-giftcard'))).toBe(1500);
  77  |     expect.soft(await amount(page, 'summary-amount-other')).toBe(0);
  78  |     await page.getByTestId('book-confirm').click();
  79  |     await expect.soft(page.getByTestId('booking-confirmation')).toContainText('จองสำเร็จ');
  80  |   });
  81  |   await S('หลังรีโหลด หน้าตรวจยอด /giftcard: SABAI-GC-2000 เหลือ ฿500', async () => {
  82  |     await open(page, '/giftcard');
  83  |     await page.getByTestId('gc-check-code').fill('SABAI-GC-2000');
  84  |     await page.getByTestId('gc-check-submit').click();
  85  |     await expect.soft(page.getByTestId('gc-check-balance')).toHaveText(/฿\s?500(\.00)?(?![\d,])/);
  86  |   });
  87  | });
  88  | 
  89  | tc('TC-GC-04', async ({ page }) => {
  90  |   await S('ไม่ล็อกอิน S01 ขั้น 3: ใส่รหัส XXXX แล้วกด "ใช้บัตรนี้"', async () => {
  91  |     await bookToStep3(page, { service: 'S01', type: 'single', date: '2026-10-20', time: '10:00' });
  92  |     await fillContact(page, 'ทดสอบบัตรมั่ว', '0812345678');
  93  |     await applyCard(page, 'XXXX');
  94  |   });
  95  |   await S('มีข้อความแจ้งว่าใช้บัตรไม่ได้ ก่อนไปขั้น 4', async () => {
  96  |     await expect.soft(page.getByTestId('book-giftcard-error')).toBeVisible();
> 97  |     await expect.soft(page.getByTestId('book-giftcard-error')).not.toHaveText(/^\s*$/);
      |                                                                    ^ Error: expect(locator).not.toHaveText(expected) failed
  98  |   });
  99  |   await S('ใบสรุปไม่มีบรรทัด Gift Card และยอด ฿1,000', async () => {
  100 |     await toSummary(page);
  101 |     await expect.soft(page.getByTestId('summary-line-giftcard')).toHaveCount(0);
  102 |     expect.soft(await amount(page, 'summary-total')).toBe(1000);
  103 |   });
  104 | });
  105 | 
```