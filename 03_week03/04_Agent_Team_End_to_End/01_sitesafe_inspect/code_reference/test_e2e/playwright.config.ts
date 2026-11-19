import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 20 * 60 * 1000,
  expect: { timeout: 15000 },
  reporter: [['list'], ['json', { outputFile: 'results/results.json' }], ['html', { outputFolder: 'playwright-report', open: 'never' }]],
  outputDir: 'test-results',
  use: {
    baseURL: 'http://localhost:3410',
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    locale: 'th-TH',
    timezoneId: 'Asia/Bangkok',
    navigationTimeout: 30000,
    actionTimeout: 15000,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
