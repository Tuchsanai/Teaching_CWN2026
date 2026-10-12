import { test, expect, open } from './fixtures';

// CR-04 วันหยุดร้าน · หน้า /book เลือกวันที่ 23 ต.ค. 2026 (วันปิยมหาราช) → ขั้น 2 ขึ้นข้อความร้านหยุด ไม่มีรอบให้เลือก
// ค่าที่คาดหวัง [D:CR-04] ③1 ② (CHANGE-REQUESTS/answers/CR-04-ANSWERS.md) · docs/impact/CR-04.md §6

test('CR04-UI-1 ไม่ล็อกอิน เลือกวันที่ 23 ต.ค. → ข้อความร้านหยุด (วันปิยมหาราช) · ไม่มีรอบ', async ({ page }) => {
  test.info().annotations.push({ type: 'source', description: '[D:CR-04] ③1 ไม่มีรอบ ขึ้นข้อความร้านหยุด · ② SHOP_CLOSED' });

  await open(page, '/book?service=S01&type=single');
  await page.getByTestId('book-type-label-single').click();
  const sel = page.getByTestId('book-service');
  if (await sel.isVisible()) await sel.selectOption('S01');
  await page.getByTestId('book-next-1').click();
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '2');

  await page.getByTestId('book-date').fill('2026-10-23');

  const err = page.getByTestId('book-error');
  await expect(err).toBeVisible();
  await expect(err).toHaveAttribute('data-error-code', 'SHOP_CLOSED');
  await expect(err).toContainText('วันนี้ร้านหยุด (วันปิยมหาราช) กรุณาเลือกวันอื่น');
  await expect(page.getByTestId('book-slots')).toHaveCount(0);
  await expect(page.getByTestId('book-next-2')).toBeDisabled();
});

test('CR04-UI-2 วันที่ 22 ต.ค. ยังมีรอบตามปกติ', async ({ page }) => {
  test.info().annotations.push({ type: 'source', description: '[D:CR-04] ③2' });
  await open(page, '/book?service=S01&type=single');
  await page.getByTestId('book-type-label-single').click();
  await page.getByTestId('book-next-1').click();
  await page.getByTestId('book-date').fill('2026-10-22');
  await expect(page.getByTestId('book-slot-10:00')).toBeVisible();
  await expect(page.getByTestId('book-error')).toHaveCount(0);
});
