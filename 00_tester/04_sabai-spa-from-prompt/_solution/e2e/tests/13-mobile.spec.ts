import { test, expect, open, pause, fillBooking, bookingDate, DAY } from './fixtures';
import type { Locator } from '@playwright/test';

const PAGES = ['/', '/services', '/book', '/packages/bangkok-relax', '/therapists', '/rooms/couple-suite', '/gift-cards', '/mood', '/quiz', '/skin', '/account', '/wallet'];

async function size(l: Locator) {
  const b = await l.boundingBox();
  return b ? { w: Math.round(b.width * 10) / 10, h: Math.round(b.height * 10) / 10 } : null;
}

test.describe('มือถือ', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('TC-MOB-01 ใช้งานบนจอ 375 px: ไม่มีแถบเลื่อนแนวนอน ปุ่ม ≥ 44×44 และจองได้', {
    tag: ['@MOB', '@P2'],
    annotation: [
      {
        type: 'expected',
        description:
          'viewport 375×812 ทุกหน้า (/, /services, /book, /packages/bangkok-relax, /therapists, /rooms/couple-suite, /gift-cards, /mood, /quiz, /skin, /account, /wallet) scrollWidth ≤ 375 (NFR-01) · ' +
          'nav-toggle แสดงและเปิดเมนูได้ · nav-toggle, lang-*, chat-toggle, slot-*, booking-submit ขนาด ≥ 44×44 px · ทำ TC-BOOK-01 ซ้ำบนมือถือจนเห็น booking-success',
      },
      { type: 'note', description: 'จองบนวันแยกตามเบราว์เซอร์ รอบ 12:00 (ไม่ชนกับ TC-BOOK-01 รอบ 10:00)' },
    ],
  }, async ({ page, browserName }) => {
    for (const path of PAGES) {
      await test.step(`${path}: ไม่มีแถบเลื่อนแนวนอน`, async () => {
        await open(page, path);
        const w = await page.evaluate(() => document.documentElement.scrollWidth);
        expect.soft(w, `${path} scrollWidth`).toBeLessThanOrEqual(375);
      });
    }

    const small: string[] = [];
    const check = async (name: string, l: Locator) => {
      const s = await size(l);
      if (!s || s.w < 44 || s.h < 44) small.push(`${name} ${s ? `${s.w}×${s.h}` : 'มองไม่เห็น'}`);
    };

    await open(page, '/');
    const toggle = page.getByTestId('nav-toggle');
    await expect(toggle).toBeVisible();
    await check('nav-toggle', toggle);
    await check('chat-toggle', page.getByTestId('chat-toggle'));
    await toggle.click();
    await expect(page.getByTestId('nav-services')).toBeVisible();
    for (const l of ['th', 'en', 'zh']) {
      const btn = page.getByTestId(`lang-${l}`);
      await expect.soft(btn, `lang-${l} ต้องมองเห็นในเมนู`).toBeVisible();
      await check(`lang-${l}`, btn);
    }
    await pause(page);
    await toggle.click();

    await open(page, '/');
    // แตะกลางปุ่ม "จองคิวเลย" แบบนิ้วจริง (page.mouse) — ไม่ใช้ locator.click() เพราะมันรอจนไม่มีอะไรบังแล้วค่อยกด
    const hero = page.getByTestId('hero-book');
    await hero.scrollIntoViewIfNeeded();
    const hb = (await hero.boundingBox())!;
    const onTop = await page.evaluate(([x, y]) => {
      const el = document.elementFromPoint(x, y);
      return el?.closest('[data-testid]')?.getAttribute('data-testid') ?? el?.tagName ?? 'none';
    }, [hb.x + hb.width / 2, hb.y + hb.height / 2]);
    expect.soft(onTop, 'จุดกลางปุ่ม hero-book ต้องเป็นปุ่มนั้นเอง (ไม่มี element อื่นบัง)').toBe('hero-book');
    await page.mouse.click(hb.x + hb.width / 2, hb.y + hb.height / 2);
    await page.waitForURL((u) => u.pathname !== '/', { timeout: 5000 }).catch(() => undefined);
    await pause(page);
    expect.soft(new URL(page.url()).pathname, 'แตะ hero-book แล้วต้องไปหน้า /book').toBe('/book');
    if (new URL(page.url()).pathname !== '/book') await open(page, '/book'); // ไปต่อเพื่อตรวจการจองบนมือถือ
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    await fillBooking(page, { service: 'thai-massage', date: bookingDate(browserName, DAY.MOB01), time: '12:00', guest: true });
    for (const t of ['10-00', '12-00', '21-30']) await check(`slot-${t}`, page.getByTestId(`slot-${t}`));
    const submit = page.getByTestId('booking-submit');
    await submit.scrollIntoViewIfNeeded();
    await check('booking-submit', submit);
    await pause(page);
    await submit.click();
    await expect(page.getByTestId('booking-success')).toBeVisible();
    expect(small, `ปุ่มที่เล็กกว่า 44×44: ${small.join(', ')}`).toEqual([]);
  });
});
