import { test, expect } from '@playwright/test';

test('หน้าแรกมีปุ่ม Get started', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('link', { name: 'Get started' })).toBeVisible();
});

test('ค้นหา locator แล้วเปิดหน้า Locators', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Search' }).click();
  await page.getByRole('searchbox').fill('locator');
  await page.getByRole('option', { name: /^Locators/ }).first().click();
  await expect(page.getByRole('heading', { name: 'Locators', level: 1 })).toBeVisible();
});

test('จับภาพหน้าแรก', async ({ page }, testInfo) => {
  await page.goto('/');
  await page.screenshot({
    path: `screenshots/home-${testInfo.project.name.replace(/\s+/g, '-')}.png`,
    fullPage: true,
  });
});
