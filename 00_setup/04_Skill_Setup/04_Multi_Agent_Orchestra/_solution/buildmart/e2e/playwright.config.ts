// e2e/playwright.config.ts — เพลย์ลิสต์ทดสอบ BuildMart (เล่นตามลำดับ playlist.json ทีละเคส)
// BM_URL (ดีฟอลต์ http://localhost:3400 · ชี้ stack โหมด AI ได้) · BM_MODE=mock|ai · BM_TTS=0 ปิดกลุ่ม T
// v3: กลุ่ม M (หลายรอบ) · V (เสียง · ข้ามถ้ายังไม่มี voice-fixtures) · D (3D) · E (ประเมิน RAG) · L (load test)
import { defineConfig } from '@playwright/test';

const MODE = process.env.BM_MODE === 'ai' ? 'ai' : 'mock';
// BM_ONLY=R (ทั้งกลุ่ม) หรือ BM_ONLY=W01,C07 (บางเคส) — -g "^R" ใช้ไม่ได้เพราะ grep ของ Playwright มีชื่อไฟล์นำหน้าชื่อ test
const ONLY = (process.env.BM_ONLY || '').split(',').map((s) => s.trim()).filter(Boolean);
const grep = ONLY.length
  ? new RegExp(`(^|\\s)(${ONLY.map((o) => (/^[A-Z]$/i.test(o) ? `${o.toUpperCase()}\\d\\d` : o)).join('|')})\\s`)
  : undefined;

/** ให้ <audio> เล่นได้เองในเคส T03/V (auto) แม้ไม่มี user gesture ค้างอยู่ · ไมค์ปลอม (ไม่มีป๊อปอัปขออนุญาต)
 *  เคส D ใช้ test.use เติม SwiftShader (WebGL) หรือปิด WebGL เองในไฟล์ของตัวเอง */
export const BASE_ARGS = ['--autoplay-policy=no-user-gesture-required', '--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'];

export default defineConfig({
  testDir: './tests',
  // ไฟล์ตั้งชื่อ 1-… 9-… ให้เล่นตามลำดับกลุ่ม W → C → R → Q → T → M → V → D → E/L
  fullyParallel: false,
  workers: 1,
  retries: 0,
  grep,
  timeout: 5 * 60_000,
  expect: { timeout: 15_000 },
  // ai/mock แยกโฟลเดอร์วิดีโอดิบ + ไฟล์ผล → รัน 2 โหมดพร้อมกันได้ ไม่ทับกัน
  outputDir: process.env.BM_OUTPUT_DIR || (MODE === 'ai' ? './test-results-ai' : './test-results'),
  globalSetup: './global-setup.ts',
  metadata: { mode: MODE, tts: process.env.BM_TTS !== '0', url: process.env.BM_URL || 'http://localhost:3400' },
  reporter: [['list'], ['json', { outputFile: process.env.BM_RESULTS || (MODE === 'ai' ? 'results.ai.json' : 'results.json') }]],
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
    // ไมค์: อนุญาตอัตโนมัติ (ไม่มีป๊อปอัป) · เสียงจริงใส่ด้วย init script fixtures/fake-mic.ts (เคส V/D02)
    permissions: ['microphone'],
    launchOptions: { args: BASE_ARGS },
  },
});
