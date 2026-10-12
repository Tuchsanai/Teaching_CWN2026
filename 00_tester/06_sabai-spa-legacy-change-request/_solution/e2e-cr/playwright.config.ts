import { defineConfig, devices } from '@playwright/test';

// ชุดทดสอบของทีม (ไม่แก้ e2e-legacy/) · baseURL จาก BASE_URL ค่าเริ่ม http://localhost:4000
export const BASE_URL = process.env.BASE_URL ?? 'http://localhost:4000';

const common = {
  baseURL: BASE_URL,
  locale: 'th-TH',
  timezoneId: 'Asia/Bangkok',
  viewport: { width: 1280, height: 800 },
  screenshot: 'only-on-failure' as const,
  trace: 'retain-on-failure' as const,
};

export default defineConfig({
  testDir: './tests',
  globalSetup: './global-setup.ts',
  // ข้อมูลอยู่ฐานเดียวกัน และทุก test reset ก่อน → รันทีละ test
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 90_000,
  expect: { timeout: 7_000 },
  outputDir: 'test-report/artifacts',
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'test-report/html' }]],
  use: common,
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], ...common } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'], ...common } },
    { name: 'webkit', use: { ...devices['Desktop Safari'], ...common } },
  ],
});
