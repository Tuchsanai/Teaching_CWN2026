import { defineConfig, devices } from '@playwright/test';

export const BASE_URL = process.env.BASE_URL ?? 'http://localhost:4000';

const common = {
  baseURL: BASE_URL,
  locale: 'th-TH',
  timezoneId: 'Asia/Bangkok',
  viewport: { width: 1280, height: 800 },
  screenshot: 'only-on-failure' as const,
  trace: 'retain-on-failure' as const,
};

// ค่าเริ่มต้นรัน api + chromium · ครบ 3 เบราว์เซอร์: npm run test:all (หรือใส่ --project เอง)
// (ตั้งเป็น env เพื่อให้ worker process เห็น project ชุดเดียวกัน)
if (process.argv.some((a) => a.startsWith('--project'))) process.env.ALL_BROWSERS = '1';
const ALL = !!process.env.ALL_BROWSERS;

export default defineConfig({
  testDir: './tests',
  globalSetup: './global-setup.ts',
  // ข้อมูลอยู่ฐานเดียวกัน · ทุก TC reset ก่อน และ TC-CXL-02 เลื่อนนาฬิกาของทั้งระบบ → รันทีละ test
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 90_000,
  expect: { timeout: 7_000 },
  outputDir: 'test-report/artifacts',
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'test-report/html' }],
  ],
  use: common,
  projects: [
    // TC ที่ยิง API อย่างเดียว รัน 1 ครั้ง/รอบ
    { name: 'api', testMatch: /.*\.api\.spec\.ts/ },
    { name: 'chromium', testIgnore: /.*\.api\.spec\.ts/, use: { ...devices['Desktop Chrome'], ...common } },
    ...(ALL
      ? [
          { name: 'firefox', testIgnore: /.*\.api\.spec\.ts/, use: { ...devices['Desktop Firefox'], ...common } },
          { name: 'webkit', testIgnore: /.*\.api\.spec\.ts/, use: { ...devices['Desktop Safari'], ...common } },
        ]
      : []),
  ],
});
