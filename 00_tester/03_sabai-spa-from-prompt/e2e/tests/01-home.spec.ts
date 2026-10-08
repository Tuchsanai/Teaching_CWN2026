import { test, expect, open, money, pause } from './fixtures';

/** SPEC §2.1 — บริการ 9 รายการ: [slug, นาที, ราคา, สมุนไพร] */
const SERVICES: [string, number, number, string[]][] = [
  ['thai-massage', 60, 800, ['plai']],
  ['herbal-compress', 60, 900, ['plai', 'turmeric', 'lemongrass', 'kaffir-lime']],
  ['foot-reflexology', 60, 600, ['lemongrass']],
  ['aroma-oil', 90, 1500, ['lemongrass', 'kaffir-lime']],
  ['coconut-rice-scrub', 90, 1400, ['thanaka', 'turmeric']],
  ['turmeric-facial', 60, 1200, ['turmeric', 'thanaka']],
  ['aloe-hydrating-facial', 60, 1100, ['aloe-vera']],
  ['body-contouring', 90, 1500, ['plai', 'turmeric']],
  ['bangkok-relax', 120, 2900, ['plai', 'turmeric', 'lemongrass']],
];
const ALLERGY = 'ถ้าแพ้สมุนไพรชนิดใด กรุณาแจ้งร้านก่อนรับบริการ';

test.describe('หน้าแรก', () => {
  test('TC-HOME-01 หน้าแรกแสดง hero ลายไทย และพาไปหน้าจองได้', {
    tag: ['@HOME', '@P3'],
    annotation: {
      type: 'expected',
      description:
        'hero แสดงรูป brand/hero.jpg (naturalWidth > 0) · มีส่วน home-package, home-tour, home-therapists, home-gift, home-member · ' +
        'รูปทุกรูปมี alt ไม่ว่าง · กด hero-book ไปที่ /book',
    },
  }, async ({ page }) => {
    await open(page, '/');

    // 1) hero + รูป brand/hero.jpg โหลดสำเร็จ
    const hero = page.getByTestId('hero');
    await expect(hero).toBeVisible();
    const heroImg = hero.locator('img[src*="brand/hero.jpg"]');
    await expect(heroImg).toHaveCount(1);
    await expect.poll(() => heroImg.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth)).toBeGreaterThan(0);

    // 2) ส่วนต่าง ๆ ของหน้าแรก (เลื่อนลงไปให้เห็นในคลิป)
    for (const id of ['home-package', 'home-tour', 'home-therapists', 'home-gift', 'home-member']) {
      const section = page.getByTestId(id);
      await section.scrollIntoViewIfNeeded();
      await expect(section, `ต้องเห็นส่วน ${id}`).toBeVisible();
    }

    // 3) NFR-11: รูปทุกรูปมี alt ไม่ว่าง
    const noAlt = await page.locator('img').evaluateAll((imgs) =>
      imgs.filter((i) => !(i.getAttribute('alt') ?? '').trim()).map((i) => i.getAttribute('src')),
    );
    expect(noAlt, `รูปที่ไม่มี alt: ${noAlt.join(', ')}`).toEqual([]);

    // 4) กด "จองเลย" ใน hero → ไป /book
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.getByTestId('hero-book').click();
    await expect(page).toHaveURL(/\/book(\?|$)/);
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
  });

  test('TC-HOME-02 ทุกบริการแสดงสมุนไพรและคำเตือนการแพ้', {
    tag: ['@HOME', '@P2'],
    annotation: {
      type: 'expected',
      description:
        'service-list มี 9 บริการ ราคาและเวลาตรงตาราง SPEC §2.1 (เช่น thai-massage ฿800 60 นาที) · service-herbs-herbal-compress มี li[data-herb] 4 รายการ (ไพล ขมิ้น ตะไคร้ มะกรูด) · ' +
        'allergy-warning = "ถ้าแพ้สมุนไพรชนิดใด กรุณาแจ้งร้านก่อนรับบริการ" · /book เลือก thai-massage แสดง booking-herbs = ไพล และ booking-allergy',
    },
  }, async ({ page }) => {
    await open(page, '/services');
    const list = page.getByTestId('service-list');
    await expect(list.getByTestId(/^service-card-/)).toHaveCount(9);
    for (const [slug, minutes, price, herbs] of SERVICES) {
      await test.step(`${slug}: ฿${price} · ${minutes} นาที · สมุนไพร ${herbs.join(', ')}`, async () => {
        await page.getByTestId(`service-card-${slug}`).scrollIntoViewIfNeeded();
        expect.soft(money(await page.getByTestId(`service-price-${slug}`).textContent()), `ราคา ${slug}`).toBe(price);
        await expect.soft(page.getByTestId(`service-duration-${slug}`), `เวลา ${slug}`).toHaveText(`${minutes} นาที`);
        const got = await page.getByTestId(`service-herbs-${slug}`).locator('li[data-herb]').evaluateAll((li) => li.map((x) => x.getAttribute('data-herb')));
        expect.soft(got, `สมุนไพร ${slug}`).toEqual(herbs);
      });
    }
    const compress = page.getByTestId('service-herbs-herbal-compress');
    await compress.scrollIntoViewIfNeeded();
    await expect(compress.locator('li[data-herb]')).toHaveText([/ไพล/, /ขมิ้น/, /ตะไคร้/, /มะกรูด/]);
    await expect(page.getByTestId('allergy-warning').first()).toHaveText(ALLERGY);

    await open(page, '/services/herbal-compress');
    await expect(page.getByTestId('service-detail-herbs').locator('[data-herb]')).toHaveCount(4); // หน้ารายละเอียดใช้การ์ดสมุนไพร (ไม่ใช่ li)
    await expect(page.getByTestId('allergy-warning').first()).toHaveText(ALLERGY);

    await open(page, '/book');
    await page.getByTestId('service-option-thai-massage').click();
    await expect(page.getByTestId('booking-herbs').locator('li[data-herb]')).toHaveCount(1);
    await expect(page.getByTestId('booking-herbs').locator('li[data-herb="plai"]')).toHaveText(/ไพล/);
    await expect(page.getByTestId('booking-allergy')).toHaveText(ALLERGY);
    await pause(page);
  });
});
