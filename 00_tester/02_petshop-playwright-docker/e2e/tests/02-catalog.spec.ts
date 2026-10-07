import { test, expect, open, baht } from './fixtures';

test.describe('ค้นหาและกรองสินค้า', () => {
  test('TC-CAT-01 ค้นหาคำว่า "แซลมอน" เจอเฉพาะสินค้าแซลมอน', {
    tag: ['@catalog', '@P1'],
    annotation: { type: 'expected', description: 'พบ 5 รายการ: ทุกตัวทำจากแซลมอน (รวมสูตรที่ชื่อไม่มีคำว่าแซลมอน)' },
  }, async ({ page }) => {
    await open(page, '/');
    await page.getByTestId('search-input').fill('แซลมอน');
    await page.getByTestId('search-submit').click();

    await expect(page).toHaveURL(/q=/);
    await expect(page.getByTestId('result-count')).toHaveText('พบ 5 รายการ');
    const slugs = await page.getByTestId('product-card').evaluateAll((els) => els.map((e) => e.getAttribute('data-slug')));
    expect(slugs.sort()).toEqual([
      'hairball-control-dry', 'kitten-salmon-dry', 'lickable-salmon-treat', 'salmon-skin-treat', 'senior-salmon-dry',
    ]);
  });

  test('TC-CAT-02 กรองแมว + อาหารเปียก', {
    tag: ['@catalog', '@P1'],
    annotation: { type: 'expected', description: 'เหลือ 2 รายการ (เพาช์ทูน่า, มูสไก่ลูกแมว) และ URL จำค่าตัวกรอง' },
  }, async ({ page }) => {
    await open(page, '/products');
    await expect(page.getByTestId('result-count')).toHaveText('พบ 28 รายการ');
    await page.getByTestId('filter-pet-cat').click();
    await page.getByTestId('filter-type').selectOption('wet');

    await expect(page.getByTestId('result-count')).toHaveText('พบ 2 รายการ');
    await expect(page).toHaveURL(/pet=cat/);
    await expect(page).toHaveURL(/type=wet/);
    await expect(page.getByTestId('product-name')).toHaveText([/ทูน่า|มูส/, /ทูน่า|มูส/]);

    // reload: filters come back from the URL
    await page.reload();
    await expect(page.getByTestId('result-count')).toHaveText('พบ 2 รายการ');
  });

  test('TC-CAT-03 เรียงราคาจากน้อยไปมาก', {
    tag: ['@catalog', '@P2'],
    annotation: { type: 'expected', description: 'ราคาทุกการ์ดเรียงจากน้อยไปมาก เริ่มที่ ฿35' },
  }, async ({ page }) => {
    await open(page, '/products');
    await page.getByTestId('sort-select').selectOption('price-asc');
    await expect(page).toHaveURL(/sort=price-asc/);
    await expect(page.getByTestId('product-price').first()).toHaveText('฿35');

    const prices = (await page.getByTestId('product-price').allTextContents()).map(baht);
    expect(prices).toEqual([...prices].sort((a, b) => a - b));
  });

  test('TC-CAT-04 กรองเฉพาะเกรนฟรี', {
    tag: ['@catalog', '@P3'],
    annotation: { type: 'expected', description: 'พบ 9 รายการที่เป็นเกรนฟรี' },
  }, async ({ page }) => {
    await open(page, '/products');
    await page.getByTestId('filter-grainfree').check();
    await expect(page.getByTestId('result-count')).toHaveText('พบ 9 รายการ');
  });

  test('TC-CAT-05 ค้นหาไม่เจอ แสดงหน้าว่าง และล้างตัวกรองได้', {
    tag: ['@catalog', '@P3'],
    annotation: { type: 'expected', description: 'ข้อความ "ไม่พบสินค้าที่ตรงกับการค้นหา" แล้วกดล้างตัวกรองกลับมา 28 รายการ' },
  }, async ({ page }) => {
    await open(page, '/products?q=pizza');
    await expect(page.getByTestId('empty-results')).toContainText('ไม่พบสินค้าที่ตรงกับการค้นหา');
    await page.getByTestId('clear-filters').click();
    await expect(page.getByTestId('result-count')).toHaveText('พบ 28 รายการ');
  });

  test('TC-CAT-06 เมนู "ของเล่น" แสดงเฉพาะของเล่นแมวและหมา', {
    tag: ['@catalog', '@P2'],
    annotation: { type: 'expected', description: 'พบ 4 รายการ: ไม้ตกแมว, อุโมงค์แมว, เชือกกัด, ลูกบอลมีเสียง' },
  }, async ({ page }) => {
    await open(page, '/');
    await page.getByTestId('nav-toys').click();
    await expect(page).toHaveURL(/type=toy/);
    await expect(page.getByTestId('result-count')).toHaveText('พบ 4 รายการ');
    const slugs = await page.getByTestId('product-card').evaluateAll((els) => els.map((e) => e.getAttribute('data-slug')));
    expect(slugs.sort()).toEqual(['cat-feather-wand', 'cat-tunnel', 'dog-rope-toy', 'dog-squeaky-ball']);
  });
});
