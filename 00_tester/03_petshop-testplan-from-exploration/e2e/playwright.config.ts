import { defineConfig, devices } from '@playwright/test';

// Chromium = the "evidence" browser: every test is recorded slowly so it can become a GIF/MP4.
// Firefox and WebKit run at full speed and only keep a video when a test fails.
const viewport = { width: 1280, height: 800 };

export default defineConfig({
  testDir: './tests',
  globalSetup: './global-setup.ts',
  // ทุก test เริ่มด้วย POST /api/test/reset (สถานะร่วมของเว็บทั้งเครื่อง) → ต้องรันทีละ test
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 120_000,
  expect: { timeout: 6_000 },
  reporter: [
    ['list'],
    ['./reporters/html-report.ts', { outputFolder: 'test-report' }],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    locale: 'th-TH',
    viewport,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], viewport, video: { mode: 'on', size: viewport }, launchOptions: { slowMo: 300 } },
    },
    { name: 'firefox', use: { ...devices['Desktop Firefox'], viewport } },
    { name: 'webkit', use: { ...devices['Desktop Safari'], viewport } },
  ],
});
