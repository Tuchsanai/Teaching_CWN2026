// ข้อ 7 ชุด A · หน้าจอประวัติแต้ม (3 คะแนน) · ชื่อ test ขึ้นต้น [w=น้ำหนัก]
import { test, expect, loginUI, open } from '../fixtures';

test('[w=2] A7-u1 U01 /account: points-history 2 แถว · แถว 0 = B13 +19 คงเหลือ 99 · แถว 1 = ยอดยกมา 80', async ({ page }) => {
  await loginUI(page, 'U01');
  await open(page, '/account');
  await expect(page.getByTestId('points-history')).toBeVisible();
  await expect(page.locator('[data-testid^="points-row-"]')).toHaveCount(2);
  const r0 = (await page.getByTestId('points-row-0').innerText()).replace(/,/g, '');
  const r1 = (await page.getByTestId('points-row-1').innerText()).replace(/,/g, '');
  expect(r0).toContain('B13');
  expect(r0).toMatch(/\+?\s*19\b/);
  expect(r0).toMatch(/\b99\b/);
  expect(r1).toMatch(/\b80\b/);
  expect(r1).toContain('ยอดยกมา');
});

test('[w=1] A7-u2 ภาษาอังกฤษแสดง "Opening balance"', async ({ page }) => {
  await loginUI(page, 'U01');
  await open(page, '/account');
  await page.getByTestId('lang-en').click();
  await page.waitForTimeout(800);
  await open(page, '/account');
  await expect(page.getByTestId('points-history')).toContainText('Opening balance');
});
