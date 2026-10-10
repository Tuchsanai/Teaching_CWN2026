import { defineConfig, devices } from '@playwright/test';

// GIF=1 → อัดวิดีโอทุก test แบบช้า (เฉพาะ chromium) แล้วแปลงเป็น test-report/gifs/<TC>.gif + videos/<TC>.mp4
const GIF = process.env.GIF === '1';
export const BASE_URL = process.env.BASE_URL ?? 'http://localhost:3000';

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
  // ข้อมูลอยู่ฐานเดียวกัน · ทุก TC ต้อง reset ก่อน (แผนหัวข้อ 5) และ TC-CXL-02 เลื่อนนาฬิกาของทั้งระบบ
  // → แยกวัน/ผู้ใช้ต่อเบราว์เซอร์ไม่ได้ (ค่าคาดหวังผูกกับผู้ใช้ seed + วันที่ในแผน) จึงรันทีละ test
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: GIF ? 240_000 : 90_000,
  expect: { timeout: 7_000 },
  outputDir: 'test-report/artifacts',
  reporter: [
    ['list'],
    ['json', { outputFile: 'test-report/results.json' }],
    ['html', { open: 'never', outputFolder: 'test-report/html' }],
    ['./scripts/index-reporter.mjs'],
  ],
  use: common,
  projects: [
    // TC ที่ยิง API อย่างเดียว (หัวข้อ 6.2 ข้อ 3) รัน 1 ครั้ง/รอบ แล้วนับผลให้ทุกเบราว์เซอร์
    { name: 'api', testMatch: /.*\.api\.spec\.ts/ },
    {
      name: 'chromium',
      testIgnore: /.*\.api\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'], ...common,
        launchOptions: GIF ? { slowMo: 350 } : {},
        video: GIF ? { mode: 'on', size: { width: 1280, height: 800 } } : 'off',
      },
    },
    { name: 'firefox', testIgnore: /.*\.api\.spec\.ts/, use: { ...devices['Desktop Firefox'], ...common } },
    { name: 'webkit', testIgnore: /.*\.api\.spec\.ts/, use: { ...devices['Desktop Safari'], ...common } },
  ],
});
