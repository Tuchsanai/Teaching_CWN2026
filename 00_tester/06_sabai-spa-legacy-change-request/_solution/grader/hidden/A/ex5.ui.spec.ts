// ข้อ 5 ชุด A · หน้าจอ (3 คะแนน) · ชื่อ test ขึ้นต้น [w=น้ำหนัก] · รันใน e2e-legacy ฉบับตั้งต้นของเครื่องตรวจ (fixtures เดิม)
import { test, expect, loginUI, bookToStep3, amount } from '../fixtures';

const MSG: Record<string, string> = { th: 'กรุณาเลือกโรงแรมหรือใส่ระยะทาง', en: 'Please choose a hotel or enter the distance', zh: '请选择酒店或输入距离' };
const settle = (page: any) => page.waitForTimeout(900);

async function toStep3Transport(page: any) {
  await loginUI(page, 'U08');
  await bookToStep3(page, { type: 'package', service: 'P01', people: 2, date: '2026-10-16', time: '10:00' });
  await page.getByTestId('book-transport').check();
  await settle(page);
  await page.getByTestId('book-next-3').click({ timeout: 5000 }).catch(() => {});
  await settle(page);
}

test('[w=1.5] A5-u1 ติ๊กรถไม่เลือกโรงแรม → ค้างขั้น 3 + book-transport-error (th)', async ({ page }) => {
  await toStep3Transport(page);
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
  await expect(page.getByTestId('book-transport-error')).toHaveText(MSG.th);
});

test('[w=0.5] A5-u2 ข้อความ en / zh และยังอยู่ขั้น 3', async ({ page }) => {
  await toStep3Transport(page);
  for (const l of ['en', 'zh']) {
    await page.getByTestId(`lang-${l}`).click();
    await settle(page);
    await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '3');
    await expect(page.getByTestId('book-transport-error')).toHaveText(MSG[l]);
  }
});

test('[w=0.5] A5-u3 เลือก H04 แล้วไปขั้น 4 (รถรวมในแพ็กเกจ ฿0)', async ({ page }) => {
  await toStep3Transport(page);
  await page.getByTestId('book-hotel').selectOption('H04');
  await settle(page);
  await page.getByTestId('book-next-3').click();
  await expect(page.getByTestId('book-step-indicator')).toHaveAttribute('data-step', '4');
  expect(await amount(page, 'summary-amount-transport')).toBe(0);
});

test('[w=0.5] A5-u4 ไม่ติ๊กรถ → จองสำเร็จ', async ({ page }) => {
  await loginUI(page, 'U08');
  await bookToStep3(page, { type: 'package', service: 'P01', people: 2, date: '2026-10-16', time: '10:00' });
  await settle(page);
  await page.getByTestId('book-next-3').click();
  await page.getByTestId('book-confirm').click();
  await expect(page.getByTestId('booking-confirmation')).toBeVisible();
});
