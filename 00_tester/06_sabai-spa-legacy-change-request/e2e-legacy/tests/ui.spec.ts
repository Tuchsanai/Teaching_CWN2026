import { tc, test, expect, open } from './fixtures';
import { join } from 'node:path';

const S = test.step;

tc('TC-UI-01', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  const pages = ['/', '/services', '/book', '/package', '/transport', '/giftcard'];
  let ok = 0;
  for (const path of pages) {
    await S(`จอ 375×667 หน้า ${path}: scrollWidth ≤ 375`, async () => {
      await open(page, path);
      const w = await page.evaluate(() => document.documentElement.scrollWidth);
      expect.soft(w, `${path} scrollWidth`).toBeLessThanOrEqual(375);
      if (w <= 375) ok++;
    });
  }
  await S('ผ่านเมื่อ 6/6 หน้า', async () => { expect.soft(ok).toBe(6); });
});

tc('TC-UI-02', async ({ page }) => {
  const suspicious: string[] = [];
  let watching = false;
  page.on('request', (r) => {
    if (!watching) return;
    const size = r.postDataBuffer()?.length ?? 0;
    if (['POST', 'PUT'].includes(r.method()) || size > 50 * 1024) suspicious.push(`${r.method()} ${r.url()} (${size} bytes)`);
  });
  await S('เปิด /skin แล้วกด "รับทราบ"', async () => {
    await open(page, '/skin');
    await page.getByTestId('skin-accept').click();
  });
  await S('อัปโหลดรูป PNG ทดสอบ (> 50 KB) → ได้ทรีตเมนต์แนะนำ 1–3 รายการ', async () => {
    watching = true;
    await page.getByTestId('skin-file').setInputFiles(join(__dirname, '..', 'fixtures', 'selfie-test.png'));
    await expect(page.getByTestId('skin-recs')).toBeVisible({ timeout: 15_000 });
    const n = await page.locator('[data-testid^="skin-rec-"]').count();
    expect.soft(n).toBeGreaterThanOrEqual(1);
    expect.soft(n).toBeLessThanOrEqual(3);
    await page.waitForTimeout(500);
    watching = false;
  });
  await S('ระหว่างอัปโหลด–วิเคราะห์ request ที่มีรูป (POST/PUT หรือ body > 50 KB) = 0', async () => {
    expect.soft(suspicious, suspicious.join('\n')).toHaveLength(0);
  });
  await S('รีโหลดแล้วไม่มีรูปค้าง', async () => {
    await page.reload();
    await page.locator('html[data-ready="true"]').waitFor();
    await expect.soft(page.getByTestId('skin-recs')).toHaveCount(0);
    await expect.soft(page.getByTestId('skin-type')).toHaveCount(0);
    await expect.soft(page.locator('main img[src^="blob:"], main img[src^="data:"]')).toHaveCount(0);
  });
});
