import { test, expect, guestToStep3, settlePrice } from './fixtures';

// CR-03 (BR-21) คนเดียวกันห้ามมีนัดเวลาทับกัน · หน้าจองขั้นยืนยันต้องบอกว่ามีนัดอยู่แล้วพร้อมรหัสนัดเดิม
// ค่าที่คาดหวัง [D:CR-03] ② (CHANGE-REQUESTS/answers/CR-03-ANSWERS.md) · docs/impact/CR-03.md §3 UI-1
//   นัดเดิม B03 คุณสมชาย 081-000-0003 · S02 13 ต.ค. 2026 10:00–11:30 (seed)

test('CR03-UI-1 ไม่ล็อกอิน จองซ้ำนัดคุณสมชาย (เบอร์ไม่มีขีด) → ขั้นยืนยันแสดง DUPLICATE_BOOKING + B03', async ({ page }) => {
  test.info().annotations.push({ type: 'source', description: '[D:CR-03] ② error 409 DUPLICATE_BOOKING · หน้าจอ book-error พร้อมรหัสนัดเดิม' });

  await guestToStep3(page, { service: 'S02', date: '2026-10-13', time: '10:00' });
  await page.getByTestId('book-contact-name').fill('คุณสมชาย');
  await page.getByTestId('book-contact-phone').fill('0810000003');
  await settlePrice(page);
  await page.getByTestId('book-next-3').click();
  await expect(page.getByTestId('book-summary')).toBeVisible();

  await page.getByTestId('book-confirm').click();

  const err = page.getByTestId('book-error');
  await expect(err).toBeVisible();
  await expect(err).toHaveAttribute('data-error-code', 'DUPLICATE_BOOKING');
  await expect(page.getByTestId('book-error-message')).toHaveText('คุณมีนัดในช่วงเวลานี้อยู่แล้ว (รหัส B03)');
  // ยังอยู่ขั้นยืนยัน (ไม่ได้หน้าจองสำเร็จ)
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '4');
  await expect(page.getByTestId('book-summary')).toBeVisible();
});
