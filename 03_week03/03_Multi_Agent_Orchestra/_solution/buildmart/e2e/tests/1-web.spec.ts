// 🛒 หน้าร้าน W01–W14
import type { Page, TestInfo } from '@playwright/test';
import { bmCase, expect, intro, say, show, hold, typeHuman, highlight, attachText, attachJson, apiJson, getStock, adminLogin } from './_bm';
import { addToCartUI, fillCheckout, placeOrder, trackUI, CUSTOMER } from './_shop';

const skus = (page: Page) => page.getByTestId('product-card').evaluateAll((els) => els.map((e) => e.getAttribute('data-sku') || ''));
const text = async (page: Page, id: string) => (await page.getByTestId(id).first().innerText()).trim();

/** แถวผลคำนวณ → {sku: qty} */
async function calcRows(page: Page) {
  const rows = page.getByTestId('calc-row');
  await expect(rows.first()).toBeVisible();
  const list = await rows.evaluateAll((els) => els.map((e) => [e.getAttribute('data-sku') || '', Number(e.getAttribute('data-qty'))] as const));
  return Object.fromEntries(list) as Record<string, number>;
}

async function calc(page: Page, info: TestInfo, tab: string, fill: () => Promise<void>, expected: Record<string, number>) {
  await page.goto('/calculator');
  await say(page, `เครื่องคำนวณวัสดุ · แท็บ ${tab}`);
  await page.getByTestId(`calc-tab-${tab}`).click();
  await hold(page, 800);
  await fill();
  await page.getByTestId('calc-submit').click();
  const rows = await calcRows(page);
  await attachJson(info, 'checked', rows);
  await say(page, 'ผลคำนวณ (ปัดขึ้นเป็นจำนวนเต็ม)');
  for (const sku of Object.keys(expected)) await highlight(page.locator(`[data-testid="calc-row"][data-sku="${sku}"]`), 5000);
  await hold(page);
  for (const [sku, qty] of Object.entries(expected)) expect(rows[sku], `${sku}`).toBe(qty);
}

bmCase('W01', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  await say(page, 'พิมพ์ “ปูน” ในช่องค้นหา');
  await typeHuman(page.getByTestId('search-input'), 'ปูน');
  await page.getByTestId('search-btn').click();
  await page.waitForURL(/\/products/);
  await expect(page.getByTestId('product-card').first()).toBeVisible();
  const found = await skus(page);
  await attachText(info, 'checked', found.join(', '));
  await say(page, `เจอ ${found.length} รายการ`);
  await show(page, page.locator('[data-testid="product-card"][data-sku^="CEM-"]'));
  for (const s of ['CEM-001', 'CEM-002', 'CEM-003', 'CEM-004']) expect(found).toContain(s);
  expect(found.length).toBeGreaterThanOrEqual(4);
});

bmCase('W02', async ({ page, item }, info) => {
  await page.goto('/products');
  await intro(page, item);
  await say(page, 'เลือกหมวด “เหล็ก”');
  await page.getByTestId('filter-category').selectOption('เหล็ก');
  await expect(page).toHaveURL(/category=/);
  await expect.poll(async () => (await skus(page)).every((s) => s.startsWith('STL-'))).toBe(true);
  await hold(page, 1500);
  await say(page, 'เรียงราคา สูง → ต่ำ');
  await page.getByTestId('sort-select').selectOption('price_desc');
  await expect(page).toHaveURL(/sort=price_desc/);
  await expect.poll(async () => (await skus(page))[0], { timeout: 15_000 }).toBe('STL-004');
  const found = await skus(page);
  await attachText(info, 'checked', found.join(' > '));
  await say(page, `รายการแรกคือ ${found[0]}`);
  await show(page, page.getByTestId('product-card').first());
  expect(found[0]).toBe('STL-004');
});

bmCase('W03', async ({ page, item }, info) => {
  await page.goto('/products/STL-003');
  await intro(page, item);
  const tiers = [await text(page, 'tier-price-1'), await text(page, 'tier-price-2'), await text(page, 'tier-price-3')];
  const stock = { LKB: await text(page, 'stock-LKB'), BNA: await text(page, 'stock-BNA'), RST: await text(page, 'stock-RST') };
  await attachJson(info, 'checked', { tiers, stock });
  await say(page, 'ตารางราคาส่ง 3 ขั้น');
  await show(page, page.locator('[data-testid^="tier-price-"]'));
  await say(page, 'สต็อกแยก 3 สาขา');
  await show(page, page.locator('[data-testid^="stock-"]'));
  expect(tiers[0]).toContain('195');
  expect(tiers[1]).toContain('185.25');
  expect(tiers[2]).toContain('175.50');
  for (const b of ['LKB', 'BNA', 'RST'] as const) expect(stock[b]).toMatch(/\d/);
});

bmCase('W04', async ({ page, item }, info) => {
  await page.goto('/products/CEM-002');
  await intro(page, item);
  const rst = await text(page, 'stock-RST');
  await attachText(info, 'checked', `stock-RST = ${rst}`);
  await say(page, 'สาขารังสิตไม่มีของ → แสดง “หมด”');
  await show(page, page.getByTestId('stock-RST'));
  expect(rst).toContain('หมด');
});

bmCase('W05', async ({ page, item }, info) => {
  await page.goto('/calculator');
  await intro(page, item);
  await calc(page, info, 'concrete', () => typeHuman(page.getByTestId('calc-input-volume'), '3'), { 'CEM-001': 21, 'AGG-001': 2, 'AGG-003': 3 });
  await say(page, 'กด “เพิ่มทั้งหมดลงตะกร้า”');
  await highlight(page.getByTestId('calc-add-all'), 1500);
  await page.getByTestId('calc-add-all').click();
  await expect(page.getByTestId('nav-cart-count')).toHaveText('26', { timeout: 15_000 });
  await show(page, page.getByTestId('nav-cart-count'), 1500);
  await page.goto('/cart');
  const rows = page.getByTestId('cart-row');
  await expect(rows).toHaveCount(3);
  const inCart = await rows.evaluateAll((els) => els.map((e) => e.getAttribute('data-sku')));
  await attachText(info, 'checked', `ตะกร้า: ${inCart.join(', ')}`);
  await say(page, 'ตะกร้ามี 3 รายการ (ปูน · ทราย · หิน)');
  await show(page, rows);
  expect(inCart.sort()).toEqual(['AGG-001', 'AGG-003', 'CEM-001']);
});

bmCase('W06', async ({ page, item }, info) => {
  await page.goto('/calculator');
  await intro(page, item);
  await calc(page, info, 'tile', () => typeHuman(page.getByTestId('calc-input-area'), '50'), { 'TIL-001': 39, 'CEM-004': 13, 'TIL-003': 10 });
});

bmCase('W07', async ({ page, item }, info) => {
  await page.goto('/calculator');
  await intro(page, item);
  await calc(
    page,
    info,
    'paint',
    async () => {
      await page.getByTestId('calc-paint-type').selectOption('exterior');
      await typeHuman(page.getByTestId('calc-input-area'), '120');
      await typeHuman(page.getByTestId('calc-input-coats'), '2');
    },
    { 'PNT-001': 8, 'PNT-003': 3 },
  );
});

bmCase('W08', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  await addToCartUI(page, 'STL-003', 60);
  await page.goto('/cart');
  const row = page.locator('[data-testid="cart-row"][data-sku="STL-003"]');
  const unit = (await row.getByTestId('cart-unit-price').innerText()).trim();
  await attachText(info, 'checked', `ราคาต่อเส้น = ${unit}`);
  await say(page, 'ซื้อ 60 เส้น ได้ราคาส่งขั้น 2 (ลด 5%)');
  await show(page, row.getByTestId('cart-unit-price'));
  expect(unit).toContain('185.25');
});

bmCase('W09', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  await addToCartUI(page, 'CEM-001', 100);
  await page.goto('/cart');
  await say(page, 'ใส่คูปอง BUILD5');
  await typeHuman(page.getByTestId('coupon-input'), 'BUILD5');
  await page.getByTestId('coupon-apply').click();
  await expect(page.getByTestId('cart-total')).toContainText('15,607.29', { timeout: 15_000 });
  const v = {
    unit: await text(page, 'cart-unit-price'),
    subtotal: await text(page, 'cart-subtotal'),
    discount: await text(page, 'cart-discount'),
    weight: await text(page, 'cart-weight'),
    vehicle: await text(page, 'cart-vehicle'),
    shipping: await text(page, 'cart-shipping'),
    vat: await text(page, 'cart-vat'),
    total: await text(page, 'cart-total'),
  };
  await attachJson(info, 'checked', v);
  await say(page, 'ราคาส่ง 137.75 × 100 = 13,775');
  await show(page, page.locator('[data-testid="cart-unit-price"],[data-testid="cart-subtotal"]'), 3000);
  await say(page, 'หักคูปอง 5% → 13,086.25 · น้ำหนัก 5,000 กก. → รถ 6 ล้อ 1,500');
  await show(page, page.locator('[data-testid="cart-discount"],[data-testid="cart-weight"],[data-testid="cart-vehicle"],[data-testid="cart-shipping"]'), 3500);
  await say(page, 'VAT 7% = 1,021.04 · ยอดสุทธิ 15,607.29');
  await show(page, page.locator('[data-testid="cart-vat"],[data-testid="cart-total"]'));
  expect(v.unit).toContain('137.75');
  expect(v.subtotal).toContain('13,775');
  expect(v.discount).toContain('688.75'); // 13,775 − 13,086.25
  expect(v.weight).toMatch(/5,?000/);
  expect(v.vehicle).toContain('6 ล้อ');
  expect(v.shipping).toContain('1,500');
  expect(v.vat).toContain('1,021.04');
  expect(v.total).toContain('15,607.29');
});

bmCase('W10', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  await addToCartUI(page, 'AGG-003', 4);
  await page.goto('/cart');
  const v = { weight: await text(page, 'cart-weight'), vehicle: await text(page, 'cart-vehicle'), shipping: await text(page, 'cart-shipping') };
  await attachJson(info, 'checked', v);
  await say(page, 'หนัก 6,400 กก. (> 6 ตัน) → รถ 10 ล้อ ค่าส่ง 3,500');
  await show(page, page.locator('[data-testid="cart-weight"],[data-testid="cart-vehicle"],[data-testid="cart-shipping"]'));
  expect(v.weight).toMatch(/6,?400/);
  expect(v.vehicle).toContain('10 ล้อ');
  expect(v.shipping).toContain('3,500');
});

bmCase('W11', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  await addToCartUI(page, 'CEM-001', 10);
  await addToCartUI(page, 'TIL-001', 5);
  await page.goto('/cart');
  const cartTotal = await text(page, 'cart-total');
  const cartSkus = await page.getByTestId('cart-row').evaluateAll((els) => els.map((e) => e.getAttribute('data-sku')));
  await say(page, `ตะกร้า ${cartSkus.length} รายการ ยอดสุทธิ ${cartTotal}`);
  await show(page, page.getByTestId('cart-total'), 2500);
  await page.getByTestId('request-quote-btn').click();
  await page.waitForURL(/\/quote/);
  await say(page, 'กรอกชื่อ / บริษัท / เลขผู้เสียภาษี (ไม่บังคับ)');
  await typeHuman(page.getByTestId('quote-name'), 'สมชาย ทดสอบระบบ');
  await typeHuman(page.getByTestId('quote-company'), 'บริษัท ช่างดี จำกัด');
  await typeHuman(page.getByTestId('quote-taxid'), '0105551234567');
  await page.getByTestId('quote-submit').click();
  await page.waitForURL(/\/quote\/QT-/, { timeout: 30_000 });
  const quoteNo = await text(page, 'quote-no');
  const quoteTotal = await text(page, 'quote-total');
  const qSkus = await page.getByTestId('quote-row').evaluateAll((els) => els.map((e) => e.getAttribute('data-sku')));
  await attachJson(info, 'checked', { quoteNo, quoteTotal, cartTotal, quoteRows: qSkus, cartRows: cartSkus });
  await say(page, `ใบเสนอราคา ${quoteNo.match(/QT-\S+/)?.[0] ?? ''}`);
  await show(page, page.getByTestId('quote-no'), 2500);
  await say(page, 'รายการและยอดตรงกับตะกร้า');
  await show(page, page.locator('[data-testid="quote-row"],[data-testid="quote-total"]'));
  expect(quoteNo).toMatch(/QT-\d{8}-\d{4}/);
  expect(qSkus.sort()).toEqual(cartSkus.sort());
  expect(quoteTotal.replace(/[^\d.]/g, '')).toBe(cartTotal.replace(/[^\d.]/g, ''));
});

bmCase('W12', async ({ page, item }, info) => {
  const SKU = 'TIL-003';
  const QTY = 2;
  await page.goto('/');
  await intro(page, item);
  const before = await getStock(page.request, SKU);
  await addToCartUI(page, SKU, QTY);
  await fillCheckout(page, 'LKB');
  const orderNo = await placeOrder(page);
  const after = await getStock(page.request, SKU);
  await page.goto(`/products/${SKU}`);
  await say(page, `สต็อก ${SKU} สาขาลาดกระบัง ${before.LKB} → ${after.LKB}`);
  await show(page, page.getByTestId('stock-LKB'));
  const cur = await trackUI(page, orderNo);
  const curText = (await cur.innerText()).trim();
  await attachJson(info, 'checked', { orderNo, stockLKB: { before: before.LKB, after: after.LKB }, track: curText });
  await say(page, 'timeline แสดง “รับคำสั่งซื้อ”');
  await show(page, page.locator('[data-testid="track-current"],[data-testid="track-step"][data-active="true"]'));
  expect(after.LKB).toBe(before.LKB - QTY);
  expect(curText).toContain('รับคำสั่งซื้อ');
  await expect(page.locator('[data-testid="track-step"][data-status="received"]')).toHaveAttribute('data-active', 'true');
});

bmCase('W13', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  const before = await getStock(page.request, 'BRK-003');
  await addToCartUI(page, 'BRK-003', 10);
  await fillCheckout(page, 'RST');
  const err = page.getByTestId('stock-error');
  await expect(err).toBeVisible();
  await say(page, 'สาขารังสิตไม่มีบล็อกประสาน → แจ้งเตือนของไม่พอ');
  await show(page, err, 2500);
  await say(page, 'ลองกดสั่งซื้อ → ต้องสั่งไม่ได้');
  await page.getByTestId('place-order').click({ force: true }).catch(() => {});
  await hold(page, 3000);
  await expect(page.getByTestId('order-no')).toHaveCount(0);
  await expect(err).toBeVisible();
  const after = await getStock(page.request, 'BRK-003');
  await attachJson(info, 'checked', { stockError: (await err.innerText()).trim(), stockBefore: before, stockAfter: after });
  await show(page, err);
  expect(after).toEqual(before);
});

bmCase('W14', async ({ page, item }, info) => {
  await page.goto('/');
  await intro(page, item);
  // สร้างคำสั่งซื้อผ่าน API (session เดียวกับหน้าเว็บ) ให้วิดีโอโฟกัสที่หลังร้าน
  await say(page, 'สร้างคำสั่งซื้อทดสอบ (TOL-003 × 1)');
  await apiJson(page.request, 'POST', '/api/cart', { sku: 'TOL-003', qty: 1 });
  const d = new Date(Date.now() + 2 * 86400_000);
  if (d.getDay() === 0) d.setDate(d.getDate() + 1);
  const { orderNo } = await apiJson(page.request, 'POST', '/api/checkout', {
    ...CUSTOMER,
    branch: 'BNA',
    deliveryDate: d.toISOString().slice(0, 10),
    slot: 'afternoon',
  });
  expect(orderNo).toMatch(/BM-\d{8}-\d{4}/);
  await adminLogin(page);
  const row = page.locator(`[data-testid="admin-order-row"][data-order="${orderNo}"]`);
  await expect(row).toBeVisible({ timeout: 20_000 });
  await say(page, `หลังร้าน: คำสั่งซื้อ ${orderNo} → เปลี่ยนเป็น “กำลังจัดส่ง”`);
  await show(page, row, 2000);
  await row.getByTestId('admin-status-select').selectOption('shipping');
  await hold(page, 1000);
  await row.getByTestId('admin-status-save').click();
  await expect(row.getByTestId('admin-status-save')).toBeDisabled({ timeout: 15_000 });
  await show(page, row, 2500);
  const cur = await trackUI(page, orderNo);
  await expect(cur).toContainText('กำลังจัดส่ง', { timeout: 15_000 });
  const curText = (await cur.innerText()).trim();
  await attachJson(info, 'checked', { orderNo, track: curText });
  await say(page, '/track แสดงขั้น “กำลังจัดส่ง”');
  await show(page, page.locator('[data-testid="track-current"],[data-testid="track-step"][data-status="shipping"]'));
  await expect(page.locator('[data-testid="track-step"][data-status="shipping"]')).toHaveAttribute('data-active', 'true');
});
