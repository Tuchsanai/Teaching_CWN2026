import { test, expect, open, USERS } from './fixtures';

// CR-01 ลูกค้าเลื่อนนัดเอง · ขั้น C หน้า /account
// testid ตาม CHANGE-REQUESTS/answers/CR-01-ANSWERS.md ②: reschedule-{code} · reschedule-dialog · reschedule-date · reschedule-slot-{HH:MM} · reschedule-confirm · reschedule-done
// ค่าที่คาดหวัง [D:CR-01] ③1 ① ② · docs/impact/CR-01.md §5 (R1 R3) · วันนี้ = 10 ต.ค. 2026 10:00 (reset ใน fixture)

test('CR01-UI-1 คุณนิดาเลื่อนนัด B05 ไป 12 ต.ค. 10:00 ผ่านหน้าเว็บ → รีโหลดแล้วเห็นเวลาใหม่', async ({ page }) => {
  test.info().annotations.push({ type: 'source', description: '[D:CR-01] ③1 · ② testid + ข้อความสำเร็จ' });
  const r = await page.request.post('/api/auth/login', { data: USERS.U01 });
  expect(r.status()).toBe(200);

  await open(page, '/account');
  await expect(page.getByTestId('booking-date-B05')).toContainText('11 ต.ค. 2026 10:00–11:00');
  await page.getByTestId('reschedule-B05').click();

  const dlg = page.getByTestId('reschedule-dialog');
  await expect(dlg).toBeVisible();
  await page.getByTestId('reschedule-date').fill('2026-10-12');
  await page.getByTestId('reschedule-slot-10:00').click();
  await page.getByTestId('reschedule-confirm').click();
  await expect(page.getByTestId('reschedule-done')).toHaveText('เลื่อนนัด B05 เป็น 12 ต.ค. 2026 10:00 แล้ว');

  await page.reload();
  await page.locator('html[data-ready="true"]').waitFor();
  await expect(page.getByTestId('booking-date-B05')).toContainText('12 ต.ค. 2026 10:00–11:00');
  await expect(page.getByTestId('booking-paid-B05')).toContainText('760');
  await expect(page.getByTestId('booking-status-B05')).toHaveText('ยืนยัน');
});

test('CR01-UI-2 ปุ่มเลื่อนของนัดวันนี้ (B06) กดไม่ได้ · B05 กดได้', async ({ page }) => {
  test.info().annotations.push({ type: 'source', description: '[D:CR-01] ② ปุ่มกดไม่ได้เมื่อเหลือไม่ถึง 24 ชม. · CR ข้อ 1' });
  const r = await page.request.post('/api/auth/login', { data: USERS.U01 });
  expect(r.status()).toBe(200);

  await open(page, '/account');
  await expect(page.getByTestId('reschedule-B06')).toBeVisible();
  await expect(page.getByTestId('reschedule-B06')).toBeDisabled();
  await expect(page.getByTestId('reschedule-B05')).toBeEnabled();
  await expect(page.getByTestId('reschedule-B13')).toHaveCount(0);
});
