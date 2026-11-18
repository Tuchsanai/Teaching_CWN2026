// e2e/tests/_shop.ts — ขั้นตอนหน้าร้านที่ใช้ซ้ำ (เพิ่มลงตะกร้า · ชำระเงิน · ติดตาม)
import type { Page } from '@playwright/test';
import { expect, say, show, typeHuman, hold } from './_bm';

export const CUSTOMER = { name: 'สมชาย ทดสอบระบบ', phone: '0812345678', address: '99/9 ถ.ลาดกระบัง แขวงลาดกระบัง กรุงเทพฯ 10520' };

const cartCount = async (page: Page) => Number((await page.getByTestId('nav-cart-count').innerText()).replace(/\D/g, '') || 0);

/** หน้าสินค้า → ใส่จำนวน → เพิ่มลงตะกร้า → รอตัวเลขบนไอคอนตะกร้าเปลี่ยน */
export async function addToCartUI(page: Page, sku: string, qty: number, opts: { holdMs?: number } = {}) {
  await page.goto(`/products/${sku}`);
  await expect(page.getByTestId('product-sku')).toContainText(sku);
  await say(page, `เพิ่ม ${sku} × ${qty.toLocaleString('th-TH')} ลงตะกร้า`);
  // ค่าตั้งต้นจาก API (header โหลดตัวเลขแบบ async — อ่านจาก DOM ทันทีอาจยังเป็น 0)
  const before = Number((await (await page.request.get('/api/cart/count')).json()).count) || 0;
  await expect.poll(() => cartCount(page), { timeout: 10_000 }).toBe(before);
  await typeHuman(page.getByTestId('qty-input'), String(qty));
  await page.getByTestId('add-to-cart').click();
  await expect.poll(() => cartCount(page), { timeout: 15_000 }).toBe(before + qty);
  await show(page, page.getByTestId('nav-cart-count'), opts.holdMs ?? 1500);
}

/** /checkout กรอกฟอร์ม + เลือกสาขา (ไม่กดสั่ง) */
export async function fillCheckout(page: Page, branch: string) {
  await page.goto('/checkout');
  await say(page, `กรอกข้อมูลจัดส่ง · เลือกสาขา ${branch}`);
  await typeHuman(page.getByTestId('checkout-name'), CUSTOMER.name);
  await typeHuman(page.getByTestId('checkout-phone'), CUSTOMER.phone);
  await typeHuman(page.getByTestId('checkout-address'), CUSTOMER.address);
  await page.getByTestId('branch-select').selectOption(branch);
  await page.getByTestId('delivery-slot').selectOption('morning');
  await hold(page, 1200);
}

/** กดสั่งซื้อ → ได้เลข BM-… */
export async function placeOrder(page: Page): Promise<string> {
  await page.getByTestId('place-order').click();
  const no = page.getByTestId('order-no');
  await expect(no).toContainText(/BM-\d{8}-\d{4}/, { timeout: 30_000 });
  const orderNo = (await no.innerText()).match(/BM-\d{8}-\d{4}/)![0];
  await say(page, `สั่งซื้อสำเร็จ ได้เลข ${orderNo}`);
  await show(page, no);
  return orderNo;
}

/** /track กรอกเลขคำสั่งซื้อ + เบอร์ → คืน locator ของสถานะปัจจุบัน */
export async function trackUI(page: Page, orderNo: string, phone = CUSTOMER.phone) {
  await page.goto('/track');
  await say(page, `ติดตามคำสั่งซื้อ ${orderNo}`);
  await typeHuman(page.getByTestId('track-order-no'), orderNo);
  await typeHuman(page.getByTestId('track-phone'), phone);
  await page.getByTestId('track-submit').click();
  const cur = page.getByTestId('track-current');
  await expect(cur).toBeVisible({ timeout: 20_000 });
  return cur;
}
