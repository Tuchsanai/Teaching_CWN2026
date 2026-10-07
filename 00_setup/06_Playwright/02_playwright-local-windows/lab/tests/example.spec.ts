import { test, expect } from '@playwright/test';

// 1) เปิดเว็บ แล้วตรวจ title + ข้อความบนหน้า
test('example.com shows Example Domain', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle(/Example Domain/);
  // หน้า example.com ปัจจุบันไม่มี <h1> แล้ว มีแค่ย่อหน้า <p> (ดู log/test-failure-h1.txt)
  await expect(page.getByText('This domain is for use in documentation examples')).toBeVisible();
});

// 2) คลิกลิงก์ แล้วตรวจว่าไปหน้าใหม่ถูกต้อง
test('playwright.dev Get started opens Installation', async ({ page }) => {
  await page.goto('https://playwright.dev/');
  await page.getByRole('link', { name: 'Get started' }).click();
  await expect(page).toHaveURL(/.*intro/);
  await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
});

// 3) จับภาพหน้าจอเก็บเป็นหลักฐาน แยกไฟล์ตามเบราว์เซอร์
test('save screenshot of example.com', async ({ page }, testInfo) => {
  await page.goto('https://example.com');
  await page.screenshot({ path: `screenshots/example-${testInfo.project.name.replace(/\s+/g, '-')}.png` });
});
