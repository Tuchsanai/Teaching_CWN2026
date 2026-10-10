import { defineConfig, devices } from '@playwright/test';

// GIF=1 → record every test slowly on Chromium so the videos can become GIFs.
const GIF = !!process.env.GIF;
const viewport = { width: 1280, height: 800 };

export default defineConfig({
  testDir: './tests',
  globalSetup: './global-setup.ts',
  fullyParallel: true,
  workers: GIF ? 3 : 4,
  retries: 0,
  timeout: GIF ? 180_000 : 45_000,
  expect: { timeout: 8_000 },
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['./reporters/tester-report.ts'],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    locale: 'th-TH',
    viewport,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: GIF ? { mode: 'on', size: viewport } : 'retain-on-failure',
    launchOptions: GIF ? { slowMo: 650 } : {},
  },
  projects: GIF
    ? [{ name: 'chromium', use: { ...devices['Desktop Chrome'], viewport } }]
    : [
        { name: 'chromium', use: { ...devices['Desktop Chrome'], viewport } },
        { name: 'firefox', use: { ...devices['Desktop Firefox'], viewport } },
        { name: 'webkit', use: { ...devices['Desktop Safari'], viewport } },
      ],
});
