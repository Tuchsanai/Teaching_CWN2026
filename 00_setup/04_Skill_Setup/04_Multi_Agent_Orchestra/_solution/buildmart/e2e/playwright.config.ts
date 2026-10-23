// e2e/playwright.config.ts — เพลย์ลิสต์ทดสอบ BuildMart (เล่นตามลำดับ playlist.json ทีละเคส)
// BM_URL (ดีฟอลต์ http://localhost:3400) · BM_MODE=mock|ai · BM_TTS=1 เปิดกลุ่ม T
import { defineConfig } from '@playwright/test';

const MODE = process.env.BM_MODE === 'ai' ? 'ai' : 'mock';
// BM_ONLY=R (ทั้งกลุ่ม) หรือ BM_ONLY=W01,C07 (บางเคส) — -g "^R" ใช้ไม่ได้เพราะ grep ของ Playwright มีชื่อไฟล์นำหน้าชื่อ test
const ONLY = (process.env.BM_ONLY || '').split(',').map((s) => s.trim()).filter(Boolean);
const grep = ONLY.length
  ? new RegExp(`(^|\\s)(${ONLY.map((o) => (/^[A-Z]$/i.test(o) ? `${o.toUpperCase()}\\d\\d` : o)).join('|')})\\s`)
  : undefined;

export default defineConfig({
  testDir: './tests',
  // ไฟล์ตั้งชื่อ 1-… 2-… ให้เล่นตามลำดับกลุ่ม W → C → R → Q → T
  fullyParallel: false,
  workers: 1,
  retries: 0,
  grep,
  timeout: 5 * 60_000,
  expect: { timeout: 15_000 },
  outputDir: './test-results',
  globalSetup: './global-setup.ts',
  metadata: { mode: MODE, tts: process.env.BM_TTS === '1', url: process.env.BM_URL || 'http://localhost:3400' },
  reporter: [['list'], ['json', { outputFile: 'results.json' }]],
  use: {
    baseURL: process.env.BM_URL || 'http://localhost:3400',
    viewport: { width: 1280, height: 800 },
    video: { mode: 'on', size: { width: 1280, height: 800 } },
    screenshot: 'only-on-failure',
    trace: 'off',
    locale: 'th-TH',
    timezoneId: 'Asia/Bangkok',
    actionTimeout: 20_000,
    navigationTimeout: 60_000,
    launchOptions: {
      // ให้ <audio> เล่นได้เองในเคส T03 (auto) แม้ไม่มี user gesture ค้างอยู่
      args: ['--autoplay-policy=no-user-gesture-required'],
    },
  },
});
