import { defineConfig, devices } from '@playwright/test';
import * as path from 'path';
import { loadTokens } from './tests/lib/env';

loadTokens(); // reads TEST_RESET_TOKEN of both stacks into process.env (never printed)

const RUN = process.env.RUN || 'dev';                 // e.g. round1, round2
const SHARD = process.env.SHARD_ID || '0';
const OUT = path.resolve(__dirname, '..', 'runs', RUN);

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 45 * 60_000,                // includes waiting for the stack lock of another shard
  expect: { timeout: 15_000 },
  outputDir: path.join(OUT, `artifacts-shard-${SHARD}`),
  reporter: [
    ['list'],
    ['json', { outputFile: path.join(OUT, `shard-${SHARD}.json`) }],
    ['blob', { outputDir: path.join(OUT, 'blob'), fileName: `shard-${SHARD}.zip` }],
  ],
  use: {
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    actionTimeout: 20_000,
    navigationTimeout: 30_000,
    locale: 'th-TH',
    timezoneId: 'Asia/Bangkok',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
