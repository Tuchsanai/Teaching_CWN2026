import { tc, test, expect, open } from './fixtures';

const S = test.step;

tc('TC-TH-01', async ({ page }) => {
  await S('เปิด /therapists แล้วติ๊ก "4.5 ดาวขึ้นไป"', async () => {
    await open(page, '/therapists');
    await page.getByTestId('filter-45').check();
  });
  await S('เหลือ 3 คน: พี่สมศรี 5.0 · พี่มาลี 4.5 · พี่ทองใบ 4.6', async () => {
    await expect.soft(page.getByTestId('therapist-count')).toContainText('3');
    for (const [code, name, rating] of [['T01', 'พี่สมศรี', '5.0'], ['T02', 'พี่มาลี', '4.5'], ['T05', 'พี่ทองใบ', '4.6']]) {
      await expect.soft(page.getByTestId(`therapist-name-${code}`)).toContainText(name);
      await expect.soft(page.getByTestId(`therapist-rating-${code}`)).toHaveText(new RegExp(`^\\D*${rating.replace('.', '\\.')}\\D*$`));
    }
  });
  await S('ไม่แสดงพี่บุญมี 4.4 · พี่จันทร์เพ็ญ (ไม่มีรีวิว) · พี่ดวงใจ 4.0', async () => {
    for (const code of ['T03', 'T04', 'T06']) await expect.soft(page.getByTestId(`therapist-${code}`)).toBeHidden();
  });
  await S('คะแนนแสดง "5.0" (ไม่ใช่ "5")', async () => {
    await expect.soft(page.getByTestId('therapist-rating-T01')).toContainText('5.0');
  });
});
