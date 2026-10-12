import { test, expect, open, baht } from '../fixtures';

// PR-1 · ลูกค้า: เพิ่ม "สูตรลดก้อนขน" 2 ชิ้น แล้วเพิ่มอีก 2 ชิ้น → ขึ้น "เพิ่ม…ลงตะกร้าแล้ว" ทั้งสองรอบ แต่ตะกร้ามี 3 ชิ้น
// ที่มาของผลที่คาดหวัง:
//   [D] TEST-DATA.md — สูตรลดก้อนขน สต็อก 3
//   [ร้าน] คำตอบเจ้าของร้าน (LAB 10) — เพิ่มได้ไม่ครบ → แจ้งเตือน (ไม่ใช่ข้อความสำเร็จ)
//          "เพิ่มได้อีกเพียง {จำนวนที่เพิ่มได้} ชิ้น (สินค้าเหลือ {สต็อก} ชิ้น)" · เพิ่มไม่ได้เลย = ข้อความเดิม · เพิ่มได้ครบ = ข้อความเดิม
//   [E] ทำซ้ำแบบ black-box (rea\scratch\pr1-repro.mjs) — ตะกร้าเพิ่มได้แค่ถึงสต็อก (3 ชิ้น ฿1,560) แต่ toast รอบสองยังเป็น toast-success
// ตะกร้าอยู่ใน localStorage ของแต่ละ context → ไม่ต้องล็อกอิน · ไม่สั่งซื้อ → ไม่ตัดสต็อก server

const SLUG = 'hairball-control-dry';
const SUCCESS = 'เพิ่ม สูตรลดก้อนขน (1.5 kg) ลงตะกร้าแล้ว';
const NONE_LEFT = 'ไม่สามารถเพิ่ม สูตรลดก้อนขน ได้ สินค้าในสต็อกไม่พอ';

async function addFromProductPage(page: import('@playwright/test').Page, qty: number) {
  await open(page, `/products/${SLUG}`);
  for (let i = 1; i < qty; i++) await page.getByTestId('qty-plus').click();
  await expect(page.getByTestId('qty-input')).toHaveValue(String(qty));
  await page.getByTestId('add-to-cart').click();
  const toast = page.getByTestId('toast');
  await expect(toast).toBeVisible();
  return toast;
}

async function expectCart(page: import('@playwright/test').Page, qty: number) {
  await open(page, '/cart');
  await expect(page.getByTestId('item-qty')).toHaveValue(String(qty));
  expect(baht(await page.getByTestId('summary-subtotal').textContent())).toBe(520 * qty);
}

test.describe('PR-1 เพิ่มลงตะกร้าเกินสต็อก ต้องบอกจำนวนที่เพิ่มได้จริง', () => {
  test('TC-PR1-01 เพิ่ม 2 แล้วเพิ่มอีก 2 (สต็อก 3) → รอบสองแจ้ง "เพิ่มได้อีกเพียง 1 ชิ้น"', {
    tag: ['@pr1', '@cart'],
    annotation: { type: 'expected', description: '[D] สต็อก 3 · [ร้าน] รอบสองเพิ่มได้ 1 → "เพิ่มได้อีกเพียง 1 ชิ้น (สินค้าเหลือ 3 ชิ้น)" ไม่ใช่ toast-success · ตะกร้า 3 ชิ้น ฿1,560' },
  }, async ({ page }) => {
    const first = await addFromProductPage(page, 2);
    await expect(first).toContainText(SUCCESS);
    await expect(page.getByTestId('cart-count')).toHaveText('2');

    const second = await addFromProductPage(page, 2);
    await expect(second).toContainText('เพิ่มได้อีกเพียง 1 ชิ้น (สินค้าเหลือ 3 ชิ้น)');
    await expect(second).not.toContainText('ลงตะกร้าแล้ว');
    await expect(second).not.toHaveClass(/toast-success/);
    await expect(page.getByTestId('cart-count')).toHaveText('3');

    await expectCart(page, 3);
    expect(baht(await page.getByTestId('summary-total').textContent())).toBe(1560);
  });

  test('TC-PR1-02 เพิ่ม 1 แล้วเพิ่มอีก 3 → แจ้ง "เพิ่มได้อีกเพียง 2 ชิ้น" (ตัวเลขต้องคำนวณ ไม่ใช่ค่าตายตัว)', {
    tag: ['@pr1', '@cart'],
    annotation: { type: 'expected', description: '[D] สต็อก 3 · [ร้าน] ขอ 3 เพิ่มได้ 2 → "เพิ่มได้อีกเพียง 2 ชิ้น (สินค้าเหลือ 3 ชิ้น)"' },
  }, async ({ page }) => {
    await expect(await addFromProductPage(page, 1)).toContainText(SUCCESS);
    const second = await addFromProductPage(page, 3);
    await expect(second).toContainText('เพิ่มได้อีกเพียง 2 ชิ้น (สินค้าเหลือ 3 ชิ้น)');
    await expect(second).not.toHaveClass(/toast-success/);
    await expectCart(page, 3);
  });

  test('TC-PR1-03 (guard) เพิ่ม 3 แล้วเพิ่มอีก 1 → เพิ่มไม่ได้เลย ใช้ข้อความเดิม', {
    tag: ['@pr1', '@cart'],
    annotation: { type: 'expected', description: '[ร้าน] เพิ่มไม่ได้เลย = ข้อความเดิม "ไม่สามารถเพิ่ม … สินค้าในสต็อกไม่พอ" · ตะกร้า 3' },
  }, async ({ page }) => {
    await expect(await addFromProductPage(page, 3)).toContainText(SUCCESS);
    const second = await addFromProductPage(page, 1);
    await expect(second).toContainText(NONE_LEFT);
    await expectCart(page, 3);
  });

  test('TC-PR1-04 (guard) เพิ่มครบตามที่ขอ (1 แล้ว 2 = 3 พอดีสต็อก) → ข้อความสำเร็จเดิมทั้งสองรอบ', {
    tag: ['@pr1', '@cart'],
    annotation: { type: 'expected', description: '[ร้าน] เพิ่มได้ครบ = ข้อความเดิม "เพิ่ม … ลงตะกร้าแล้ว" · ตะกร้า 3' },
  }, async ({ page }) => {
    await expect(await addFromProductPage(page, 1)).toContainText(SUCCESS);
    const second = await addFromProductPage(page, 2);
    await expect(second).toContainText(SUCCESS);
    await expect(second).toHaveClass(/toast-success/);
    await expectCart(page, 3);
  });
});
