import { defineConfig, devices } from '@playwright/test';

// GIF=1 → อัดวิดีโอทุก test (แปลงเป็น GIF + MP4 ใน reporters/tester-report.ts) และ slowMo 650 เฉพาะ chromium
const GIF = !!process.env.GIF;
const viewport = { width: 1280, height: 800 };
const slow = GIF ? { slowMo: 650 } : {};

/**
 * ลำดับการรัน
 *   global-setup.ts      → เช็กเว็บ + reset R0 (2026-10-08 10:00) ครั้งเดียว
 *   setup                → เช็กว่าเว็บพร้อม (ไม่ reset)
 *   chromium / firefox / webkit (ขนานกัน) → tests/*.spec.ts ทุกไฟล์ ยกเว้น *.serial.spec.ts
 *   time-travel (teardown ของ setup) → tests/*.serial.spec.ts รันทีละข้อบน chromium
 *       หลังทั้ง 3 เบราว์เซอร์รันจบแล้วเท่านั้น — TC ที่ต้อง "ย้ายเวลาเว็บ" (reset ด้วยเวลาอื่น) อยู่ที่นี่
 *       เพราะ reset ระหว่างที่เบราว์เซอร์อื่นยังรันอยู่จะล้างข้อมูลของเขา · ข้อสุดท้าย reset กลับเป็น R0
 */
export default defineConfig({
  testDir: './tests',
  globalSetup: './global-setup.ts',
  fullyParallel: true,
  workers: GIF ? 2 : 3,
  retries: 0,
  timeout: GIF ? 240_000 : 90_000,
  expect: { timeout: 8_000 },
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['./reporters/tester-report.ts'],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    locale: 'th-TH',
    timezoneId: 'Asia/Bangkok',
    viewport,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: GIF ? { mode: 'on', size: viewport } : 'retain-on-failure',
  },
  projects: [
    { name: 'setup', testMatch: /ready\.setup\.ts/, teardown: 'time-travel' },
    {
      name: 'chromium',
      dependencies: ['setup'],
      testIgnore: /\.serial\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], viewport, launchOptions: slow },
    },
    { name: 'firefox', dependencies: ['setup'], testIgnore: /\.serial\.spec\.ts/, use: { ...devices['Desktop Firefox'], viewport } },
    { name: 'webkit', dependencies: ['setup'], testIgnore: /\.serial\.spec\.ts/, use: { ...devices['Desktop Safari'], viewport } },
    {
      name: 'time-travel',
      testMatch: /\.serial\.spec\.ts/,
      fullyParallel: false,
      use: { ...devices['Desktop Chrome'], viewport, launchOptions: slow },
    },
  ],
});
