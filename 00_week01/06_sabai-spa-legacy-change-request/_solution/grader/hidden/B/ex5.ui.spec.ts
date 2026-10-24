// ข้อ 5 ชุด B · ปุ่ม "ใช้บริการเสร็จ" ในตารางคิว (1.5 คะแนน) · ชื่อ test ขึ้นต้น [w=น้ำหนัก]
import { test, expect, loginUI, open } from '../fixtures';

const V = JSON.parse(process.env.VARIANT_JSON ?? '{}');
const X = Number(V.completeAfterMin ?? 0);
const iso = (min: number) => {
  const t = 15 * 60 + X + min;
  return `2026-10-10T${String(Math.floor(t / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}:00+07:00`;
};

for (const [label, off, enabled] of [['T-1 ปุ่ม B06 กดไม่ได้', -1, false], ['T ปุ่ม B06 กดได้', 0, true]] as const) {
  test(`[w=0.75] B5-u ${label}`, async ({ page, api }) => {
    await api.reset(iso(off));
    await loginUI(page, 'owner');
    await open(page, '/admin?date=2026-10-10');
    await page.getByTestId('admin-date').fill('2026-10-10');
    const btn = page.getByTestId('admin-complete-B06');
    await btn.waitFor();
    await page.waitForTimeout(500);
    if (enabled) await expect(btn).toBeEnabled();
    else await expect(btn).toBeDisabled();
  });
}
