import { test, expect, open } from './fixtures';

test.describe('มือถือ', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test('TC-MOB-01 เมนูแฮมเบอร์เกอร์บนมือถือ', {
    tag: ['@mobile', '@P3'],
    annotation: { type: 'expected', description: 'จอกว้าง 390px: กดปุ่มเมนูแล้วเห็นเมนู กด "อาหารหมา" ไปหน้าสินค้าหมา' },
  }, async ({ page }) => {
    await open(page, '/');
    await expect(page.getByTestId('mobile-menu')).toBeHidden();
    await page.getByTestId('menu-toggle').click();
    const menu = page.getByTestId('mobile-menu');
    await expect(menu).toBeVisible();
    await menu.getByTestId('nav-dog').click();
    await expect(page).toHaveURL(/pet=dog/);
    await expect(page.getByTestId('result-count')).toHaveText('พบ 14 รายการ');
  });
});

test.describe('API', () => {
  test('TC-API-01 GET /api/products?pet=dog ได้สินค้าหมา 14 รายการ', {
    tag: ['@api', '@P2'],
    annotation: { type: 'expected', description: 'status 200, total = 14 และทุกชิ้น pet = dog' },
  }, async ({ request }) => {
    const res = await request.get('/api/products?pet=dog');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.total).toBe(14);
    for (const p of body.items) expect(p.pet).toBe('dog');
  });

  test('TC-API-02 สั่งซื้อผ่าน API โดยไม่เข้าสู่ระบบ ต้องถูกปฏิเสธ', {
    tag: ['@api', '@security', '@P1'],
    annotation: { type: 'expected', description: 'POST /api/orders ไม่มี cookie → status 401' },
  }, async ({ request }) => {
    const res = await request.post('/api/orders', {
      data: { items: [{ slug: 'tuna-pouch', size: 'ซอง 85 g', qty: 1 }], shipping: 'standard', payment: 'cod' },
    });
    expect(res.status()).toBe(401);
  });

  test('TC-API-03 ขอสินค้าที่ไม่มีอยู่ ได้ 404', {
    tag: ['@api', '@P3'],
    annotation: { type: 'expected', description: 'GET /api/products/unknown → status 404 พร้อม error' },
  }, async ({ request }) => {
    const res = await request.get('/api/products/unknown');
    expect(res.status()).toBe(404);
    expect((await res.json()).error).toBeTruthy();
  });
});
