import { readFileSync } from 'node:fs';
import { test, expect, open, amount, USERS } from './fixtures';

// CR-05 รายงานยอด · owner เปิด /admin/report เลือก 1–30 ก.ย. 2026 → ตัวเลขตรง SQL · โหลด CSV แล้วตรวจไฟล์ด้วย Node
// ค่าที่คาดหวังจาก SQL ตรงกับฐาน (docs/impact/CR-05.md §3 · [E sql:q_counts q_money q_csv_sep]) ไม่ได้ลอกจากหน้ารายงาน

const CSV_HEAD = 'date,code,status,type,people,service,total,giftcard_paid,other_paid,discount_kind,discount_amount,points_earned';
const B13 = '2026-09-30,B13,completed,single,1,นวดน้ำมันอโรมา,1900.00,0.00,1900.00,tier,100.00,19';

test('CR05-UI-1 owner เลือกช่วง ก.ย. กดดู → ยอดตรง SQL · โหลด CSV → BOM + ชื่อบริการไทยตรงตัว', async ({ page }) => {
  test.info().annotations.push({ type: 'source', description: '[D:CR-05] ①② · [E sql:q_counts q_money q_csv_sep]' });
  const r = await page.request.post('/api/auth/login', { data: USERS.owner });
  expect(r.status()).toBe(200);

  await open(page, '/admin');
  await page.getByTestId('nav-admin-report').click();
  await page.waitForURL('**/admin/report');
  await page.locator('html[data-ready="true"]').waitFor();

  await page.getByTestId('report-from').fill('2026-09-01');
  await page.getByTestId('report-to').fill('2026-09-30');
  await page.getByTestId('report-run').click();
  await expect(page.getByTestId('report-result')).toHaveAttribute('data-from', '2026-09-01');
  await expect(page.getByTestId('report-result')).toHaveAttribute('data-to', '2026-09-30');

  expect(await amount(page, 'report-revenue')).toBe(1900);
  await expect(page.getByTestId('report-revenue')).toHaveText('฿1,900');
  await expect(page.getByTestId('report-count-confirmed')).toHaveText('0');
  await expect(page.getByTestId('report-count-completed')).toHaveText('3');
  await expect(page.getByTestId('report-count-cancelled')).toHaveText('1');
  expect(await amount(page, 'report-disc-tier')).toBe(100);
  await expect(page.getByTestId('report-points')).toHaveText('19');
  await expect(page.getByTestId('report-course')).toHaveText('2');

  const [dl] = await Promise.all([page.waitForEvent('download'), page.getByTestId('report-csv').click()]);
  expect(dl.suggestedFilename()).toBe('sabai-report-2026-09-01_2026-09-30.csv');
  const file = test.info().outputPath('report.csv');
  await dl.saveAs(file);
  const bytes = readFileSync(file);
  expect([...bytes.subarray(0, 3)]).toEqual([0xef, 0xbb, 0xbf]);
  const lines = bytes.subarray(3).toString('utf8').split(/\r?\n/).filter((l) => l !== '');
  expect(lines[0]).toBe(CSV_HEAD);
  expect(lines.length - 1).toBe(4);
  expect(lines.map((l) => l.split(',')[1])).toEqual(['code', 'B10', 'B11', 'B12', 'B13']);
  expect(lines[4]).toBe(B13);
  expect(lines[4].split(',')[5]).toBe('นวดน้ำมันอโรมา');
});

test('CR05-UI-2 ช่วง 93 วัน → ข้อความ REPORT_RANGE · สมาชิกเปิดหน้าไม่ได้', async ({ page }) => {
  test.info().annotations.push({ type: 'source', description: '[D:CR-05] ③2 · ② สิทธิ์' });
  const r = await page.request.post('/api/auth/login', { data: USERS.owner });
  expect(r.status()).toBe(200);
  await open(page, '/admin/report');
  await page.getByTestId('report-from').fill('2026-08-01');
  await page.getByTestId('report-to').fill('2026-11-01');
  await page.getByTestId('report-run').click();
  await expect(page.getByTestId('report-error')).toHaveAttribute('data-error-code', 'REPORT_RANGE');
  await expect(page.getByTestId('report-result')).toHaveCount(0);

  await page.request.post('/api/auth/logout').catch(() => {});
  await page.context().clearCookies();
  const u = await page.request.post('/api/auth/login', { data: USERS.U01 });
  expect(u.status()).toBe(200);
  await open(page, '/admin/report');
  await expect(page.getByTestId('admin-forbidden')).toBeVisible();
  await expect(page.getByTestId('nav-admin-report')).toHaveCount(0);
});
