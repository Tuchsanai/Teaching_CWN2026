// Step 11 · send test-set receipts through the real web page (Playwright, headless Chromium).
// usage: node web_upload.mjs <client code e.g. CL-03> <shot.png> file1.jpg file2.jpg ...
// Logs in as คุณพิมพ์ (staff, seed account from schema.sql), opens /upload, picks the client, attaches files, submits.
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const PW = process.env.PW_MODULE || 'C:/Users/oishi/AppData/Roaming/npm/node_modules/@playwright/cli/node_modules/playwright';
const { chromium } = require(PW);
const [client, shot, ...files] = process.argv.slice(2);
const BASE = process.env.BASE || 'http://localhost:3420';
const browser = await chromium.launch({ executablePath: process.env.CHROME || 'C:/Users/oishi/AppData/Local/ms-playwright/chromium-1255/chrome-win64/chrome.exe' });
const page = await browser.newPage();
await page.goto(`${BASE}/login`);
await page.getByTestId('login-email-input').fill('pim@receiptdesk.test');
await page.getByTestId('login-password-input').fill('receiptdesk-test');
await page.getByTestId('login-submit-button').click();
await page.waitForURL((u) => !u.pathname.startsWith('/login'));
await page.goto(`${BASE}/upload`);
const sel = page.getByTestId('upload-client-select');
await sel.locator('option', { hasText: client }).first().waitFor({ state: 'attached' });
const value = await sel.locator('option', { hasText: client }).first().getAttribute('value');
await sel.selectOption(value);
await page.getByTestId('upload-file-input').setInputFiles(files);
const t0 = Date.now();
await page.getByTestId('upload-submit-button').click();
const count = await page.getByTestId('upload-accepted-count').first().textContent({ timeout: 30000 });
await page.screenshot({ path: shot, fullPage: true });
console.log(JSON.stringify({ accepted: Number(count), sent: files.length, submitMs: Date.now() - t0, at: new Date().toISOString() }));
await browser.close();
