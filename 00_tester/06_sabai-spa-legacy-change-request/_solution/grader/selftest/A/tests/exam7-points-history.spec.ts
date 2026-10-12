// EX7 (ชุด A) เทสต์ของผู้สอบ (Playwright): หน้า /account แสดงประวัติแต้ม
import { test, expect } from '@playwright/test';

test('EX7 U01 เห็นประวัติแต้ม 2 แถว', async ({ page, request }) => {
  expect((await request.post('/api/test/reset', { data: {} })).ok()).toBeTruthy();
  await page.goto('/login');
  await page.getByTestId('login-email').fill('nida@sabai.test');
  await page.getByTestId('login-password').fill('Nida@2026');
  await page.getByTestId('login-submit').click();
  await page.waitForURL((u) => !u.pathname.startsWith('/login'));
  await page.goto('/account');
  await expect(page.getByTestId('points-history')).toBeVisible();
  await expect(page.getByTestId('points-row-0')).toContainText('B13');
  await expect(page.getByTestId('points-row-1')).toContainText('80');
});
