import { test, expect, open, CAT_SLUGS, CHICKEN_SLUGS } from './fixtures';

test.describe('ระบบแนะนำสินค้า', () => {
  test('TC-REC-01 ตัวช่วยเลือกอาหาร: ลูกแมว แพ้ไก่', {
    tag: ['@recommend', '@P1'],
    annotation: { type: 'expected', description: 'ผลลัพธ์เป็นอาหารแมว ไม่มีไก่ อันดับ 1 คือ "ลูกแมว สูตรแซลมอน" และมีเหตุผล "ไม่มีไก่"' },
  }, async ({ page }) => {
    await open(page, '/');
    await page.getByTestId('nav-finder').click();
    await page.getByTestId('finder-pet-cat').click();
    await page.getByTestId('finder-next').click();
    await page.getByTestId('finder-life-baby').click();
    await page.getByTestId('finder-next').click();
    await page.getByTestId('finder-no-chicken').check();
    await page.getByTestId('finder-submit').click();

    const results = page.getByTestId('finder-result');
    await expect(results.first()).toHaveAttribute('data-slug', 'kitten-salmon-dry');
    const slugs = await results.evaluateAll((els) => els.map((e) => e.getAttribute('data-slug')!));
    for (const slug of slugs) {
      expect(CAT_SLUGS, `${slug} ต้องเป็นอาหารแมว`).toContain(slug);
      expect(CHICKEN_SLUGS, `${slug} ต้องไม่มีไก่`).not.toContain(slug);
    }
    await expect(results.first().getByTestId('match-reason').filter({ hasText: 'ไม่มีไก่' })).toBeVisible();
    await expect(results.first().getByTestId('match-score')).toContainText('ตรงใจ');
  });

  test('TC-REC-02 ตัวช่วยเลือกอาหาร: หมาสูงวัย เกรนฟรี ขนม', {
    tag: ['@recommend', '@P2'],
    annotation: { type: 'expected', description: 'อันดับ 1 คือ "หนังปลาแซลมอนกรอบ" (สูงวัย + เกรนฟรี + ขนม)' },
  }, async ({ page }) => {
    await open(page, '/finder');
    await page.getByTestId('finder-pet-dog').click();
    await page.getByTestId('finder-next').click();
    await page.getByTestId('finder-life-senior').click();
    await page.getByTestId('finder-next').click();
    await page.getByTestId('finder-grainfree').check();
    await page.getByTestId('finder-type').selectOption('treat');
    await page.getByTestId('finder-submit').click();
    await expect(page.getByTestId('finder-result').first()).toHaveAttribute('data-slug', 'salmon-skin-treat');
  });

  test('TC-REC-03 หน้าแรกแนะนำสินค้าตามที่เคยดู', {
    tag: ['@recommend', '@P2'],
    annotation: { type: 'expected', description: 'หลังดูอาหารลูกแมว หน้าแรกมี "ดูล่าสุด" และ "แนะนำสำหรับคุณ" เป็นอาหารแมวทั้งหมด' },
  }, async ({ page }) => {
    await open(page, '/products/kitten-salmon-dry');
    await open(page, '/');

    const recent = page.getByTestId('recently-viewed');
    await recent.scrollIntoViewIfNeeded();
    await expect(recent.locator('[data-slug="kitten-salmon-dry"]').first()).toBeVisible();

    const recommended = page.getByTestId('recommended-for-you');
    await recommended.scrollIntoViewIfNeeded();
    const slugs = await recommended.getByTestId('product-card').evaluateAll((els) => els.map((e) => e.getAttribute('data-slug')!));
    expect(slugs.length).toBeGreaterThan(0);
    for (const slug of slugs) expect(CAT_SLUGS).toContain(slug);
    expect(slugs).not.toContain('kitten-salmon-dry');
  });

  test('TC-REC-04 "ซื้อคู่กันบ่อย" กดเดียวได้ครบชุด', {
    tag: ['@recommend', '@P2'],
    annotation: { type: 'expected', description: 'กด add-bundle ที่ลูกแมวสูตรแซลมอน ตะกร้าได้ 3 ชิ้น (ตัวมันเอง + 2 ชิ้นที่ซื้อคู่กัน)' },
  }, async ({ page }) => {
    await open(page, '/products/kitten-salmon-dry');
    const bundle = page.getByTestId('bought-together');
    await bundle.scrollIntoViewIfNeeded();
    await expect(bundle.locator('[data-slug="kitten-chicken-mousse"]').first()).toBeVisible();
    await bundle.getByTestId('add-bundle').click();
    await expect(page.getByTestId('cart-count')).toHaveText('3');
  });
});
