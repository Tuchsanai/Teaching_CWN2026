import { test, expect } from '@playwright/test';

// 1) เปิดเว็บ แล้วตรวจหัวเรื่องของหน้า
test('playwright.dev home page', async ({ page }) => {
  await page.goto('https://playwright.dev/');
  await expect(page).toHaveTitle(/Playwright/);
  await expect(page.getByRole('link', { name: 'Get started' })).toBeVisible();
});

// 2) ค้นหาข้อมูลในเว็บ: พิมพ์ "locator" ในช่องค้นหา แล้วเปิดผลลัพธ์
test('search docs for locator', async ({ page }) => {
  await page.goto('https://playwright.dev/');
  await page.getByRole('button', { name: 'Search' }).click();
  await page.getByPlaceholder('Search docs').fill('locator');
  await page.getByRole('option', { name: /Locators/ }).first().click();
  await expect(page.getByRole('heading', { name: 'Locators', level: 1 })).toBeVisible();
});

// 3) จับภาพหน้าแรกเก็บเป็นหลักฐาน แยกไฟล์ตามเบราว์เซอร์
test('save screenshot of playwright.dev', async ({ page }, testInfo) => {
  await page.goto('https://playwright.dev/');
  await page.screenshot({ path: `screenshots/playwright-dev-${testInfo.project.name.replace(/\s+/g, '-')}.png` });
});
