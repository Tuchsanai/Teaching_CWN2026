import { defineConfig, devices } from '@playwright/test';

// ค่าเริ่มต้นรันแค่ chromium · อยากรันครบ 3 เบราว์เซอร์: npm run test:all (หรือใส่ --project เอง)
const viewport = { width: 1280, height: 800 };
// (ตั้งเป็น env เพื่อให้ worker process เห็น project ชุดเดียวกัน)
if (process.argv.some((a) => a.startsWith('--project'))) process.env.ALL_BROWSERS = '1';
const ALL = !!process.env.ALL_BROWSERS;

export default defineConfig({
  testDir: './tests',
  globalSetup: './global-setup.ts',
  fullyParallel: true,
  workers: 4,
  retries: 0,
  timeout: 45_000,
  expect: { timeout: 8_000 },
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:4000',
    locale: 'th-TH',
    viewport,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], viewport } },
    ...(ALL
      ? [
          { name: 'firefox', use: { ...devices['Desktop Firefox'], viewport } },
          { name: 'webkit', use: { ...devices['Desktop Safari'], viewport } },
        ]
      : []),
  ],
});
