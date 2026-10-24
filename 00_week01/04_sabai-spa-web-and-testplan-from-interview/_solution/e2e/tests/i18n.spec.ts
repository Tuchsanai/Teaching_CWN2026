import { tc, test, expect, open, settle } from './fixtures';

const S = test.step;

// อักษรไทย ก–๛ (U+0E01–U+0E5B) แต่ไม่นับ "฿" (U+0E3F) — แผน 7.2: regex ของ NFR-06 นับ ฿ ด้วย
// 👀 ช่วง [ก-๛] ที่เขียนในแผนจริง ๆ ครอบ ฿ อยู่ จึงต้องตัด U+0E3F ออกเองให้ตรงเจตนาของแผน
const THAI = /[ก-฾เ-๛]/g;

tc('TC-I18N-01', async ({ page }) => {
  await S('เปิด /services แล้วกด 中文', async () => {
    await open(page, '/services');
    await page.getByTestId('lang-zh').click();
    await expect(page.locator('html')).toHaveAttribute('lang', /^zh/);
    await page.locator('html[data-ready="true"]').waitFor();
    // WebKit เปลี่ยน <html lang> ก่อนวาดข้อความใหม่ → รอให้ข้อความใน <main> หยุดเปลี่ยนก่อนนับ
    await settle(page, () => page.locator('main').innerText());
  });
  await S('อักษรไทยใน <main> และเมนู = 0 ตัว (ไม่นับ ฿)', async () => {
    const text = await page.evaluate(() => {
      const main = document.querySelector('main')?.innerText ?? '';
      const nav = Array.from(document.querySelectorAll('header nav, [data-testid^="nav-"]')).map((e) => (e as HTMLElement).innerText).join('\n');
      return main + '\n' + nav;
    });
    const found = text.match(THAI) ?? [];
    expect.soft(found.length, `อักษรไทยที่เจอ: ${[...new Set(found)].join('')}`).toBe(0);
  });
  await S('ไป /book แล้วยังเป็น 中文 (<html lang> = zh)', async () => {
    await page.getByTestId('nav-book').click();
    await page.waitForURL('**/book**');
    await page.locator('html[data-ready="true"]').waitFor();
    await expect.soft(page.locator('html')).toHaveAttribute('lang', /^zh/);
  });
});
