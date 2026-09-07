const fs = require('fs');
const { chromium } = require('playwright');

const url = process.argv[2];
const outDir = process.argv[3];
const results = [];
const business = [];
const browserErrors = [];

function record(id, pass, detail) {
  results.push({ id, status: pass ? 'PASS' : 'FAIL', detail });
}

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  page.on('console', m => { if (m.type() === 'error') browserErrors.push(`console.error: ${m.text()}`); });
  page.on('pageerror', e => browserErrors.push(`pageerror: ${e.message}`));
  page.on('requestfailed', r => browserErrors.push(`requestfailed: ${r.url()} ${r.failure()?.errorText || ''}`));

  const code = page.locator('#learner-code');
  const book = page.locator('#book-btn');
  const count = page.locator('#seat-booked');
  const left = page.locator('#seat-left');
  const status = page.locator('#status');
  const reset = async () => { await page.locator('#reset-btn').click(); };
  const bookCode = async value => { await code.fill(value); await book.click(); };
  const stateIs = async (c, l) => (await count.textContent()) === String(c) && (await left.textContent()) === String(l);

  await page.goto(url, { waitUntil: 'networkidle' });
  await reset();

  await bookCode('');
  const blank = await stateIs(0, 3) && /กรอก/.test(await status.textContent());
  await bookCode('   ');
  record('UAT-01', blank && await stateIs(0, 3) && /กรอก/.test(await status.textContent()), 'ช่องว่างและ space ล้วนถูกปฏิเสธ; 0 รายการ เหลือ 3');

  await bookCode('<LEARNER_A>');
  record('UAT-02', await stateIs(1, 2) && await page.locator('#booking-list').getByText('<LEARNER_A>', { exact: true }).count() === 1 && /สำเร็จ/.test(await status.textContent()), 'จอง A สำเร็จทันที; 1 รายการ เหลือ 2');

  await bookCode('<LEARNER_A>');
  record('UAT-03', await stateIs(1, 2) && await page.locator('#booking-list').getByText('<LEARNER_A>', { exact: true }).count() === 1 && /จอง.*แล้ว/.test(await status.textContent()), 'รหัส A ซ้ำถูกปฏิเสธ; สถานะไม่เปลี่ยน');

  await bookCode('<LEARNER_B>');
  const afterB = await stateIs(2, 1);
  await bookCode('<LEARNER_C>');
  record('UAT-04', afterB && await stateIs(3, 0) && await page.locator('[data-cancel]').count() === 3, 'จอง A/B/C ครบ; 3 รายการ เหลือ 0');

  await bookCode('<LEARNER_D>');
  record('UAT-05', await stateIs(3, 0) && /เต็ม/.test(await status.textContent()) && /0/.test(await status.textContent()), 'คนที่ 4 ถูกปฏิเสธ; เต็มและเหลือ 0');

  await page.locator('[data-cancel="<LEARNER_B>"]').click();
  const cancelled = await stateIs(2, 1) && /ยกเลิก/.test(await status.textContent());
  await bookCode('<LEARNER_D>');
  const listText = await page.locator('#booking-list').textContent();
  record('UAT-06', cancelled && await stateIs(3, 0) && listText.includes('<LEARNER_A>') && listText.includes('<LEARNER_C>') && listText.includes('<LEARNER_D>') && !listText.includes('<LEARNER_B>'), 'ยกเลิก B แล้ว D จองได้; A/C/D ครบ 3');

  await page.reload({ waitUntil: 'networkidle' });
  const persisted = await stateIs(3, 0) && /<LEARNER_A>/.test(await page.locator('#booking-list').textContent());
  await reset();
  await page.reload({ waitUntil: 'networkidle' });
  record('UAT-07', persisted && await stateIs(0, 3), 'refresh คง A/C/D; เริ่มใหม่แล้ว refresh ยังคง 0/3');

  await page.reload({ waitUntil: 'networkidle' });
  await page.keyboard.press('Tab');
  const focusInput = await page.evaluate(() => document.activeElement?.id === 'learner-code');
  await page.keyboard.type('<LEARNER_A>');
  const inputRing = await page.evaluate(() => getComputedStyle(document.activeElement).outlineStyle !== 'none' || getComputedStyle(document.activeElement).boxShadow !== 'none');
  await page.keyboard.press('Tab');
  const focusBook = await page.evaluate(() => document.activeElement?.id === 'book-btn');
  await page.keyboard.press('Enter');
  await page.keyboard.press('Tab');
  const focusCancel = await page.evaluate(() => document.activeElement?.hasAttribute('data-cancel'));
  await page.keyboard.press('Space');
  await page.keyboard.press('Tab');
  const focusReset = await page.evaluate(() => document.activeElement?.id === 'reset-btn');
  record('UAT-08', focusInput && inputRing && focusBook && focusCancel && focusReset && await stateIs(0, 3), 'Tab ถึง input/book/cancel/reset; Enter จองและ Space ยกเลิก');

  await page.setViewportSize({ width: 375, height: 812 });
  await bookCode('<LEARNER_A>');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  const thaiStatus = /[ก-๙]/.test(await status.textContent());
  record('UAT-09', overflow === 0 && thaiStatus && await stateIs(1, 2), `viewport 375px; horizontal overflow = ${overflow}px; ข้อความเป็นภาษาไทย`);
  await page.screenshot({ path: `${outDir}/mobile-375.png`, fullPage: true });

  await page.setViewportSize({ width: 1440, height: 1000 });
  await reset();
  await bookCode('<LEARNER_A>');
  await bookCode('<LEARNER_B>');
  await page.screenshot({ path: `${outDir}/desktop-1440.png`, fullPage: true });

  await reset();
  await bookCode('<LEARNER_X>');
  business.push({ id: 'B02-X', status: await stateIs(0, 3) && /ไม่ผ่าน/.test(await status.textContent()) ? 'PASS' : 'FAIL', detail: 'รหัสนอกชุด <LEARNER_A>–<LEARNER_D> ต้องไม่ถูกจอง' });

  const output = {
    generated_at: new Date().toISOString(),
    url,
    browser: 'Chromium ผ่าน pw-up CDP 127.0.0.1:9222',
    viewport_evidence: ['desktop-1440.png', 'mobile-375.png'],
    summary: {
      pass: results.filter(x => x.status === 'PASS').length,
      fail: results.filter(x => x.status === 'FAIL').length,
      business_pass: business.filter(x => x.status === 'PASS').length,
      business_fail: business.filter(x => x.status === 'FAIL').length
    },
    results,
    additional_business_checks: business,
    browser_errors: browserErrors
  };
  fs.writeFileSync(`${outDir}/uat-auto.json`, JSON.stringify(output, null, 2) + '\n');
  await context.close();
  process.stdout.write(JSON.stringify(output.summary) + '\n');
  process.exit(output.summary.fail || output.summary.business_fail || browserErrors.length ? 1 : 0);
})().catch(error => {
  process.stderr.write(error.stack + '\n');
  process.exit(2);
});
