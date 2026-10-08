import { test, expect, open, pause, note, bookingBody } from './fixtures';
import type { Page } from '@playwright/test';

/** ทุกหน้าใน SPEC §1 */
const PAGES = [
  '/', '/services', '/services/thai-massage', '/book', '/packages/bangkok-relax', '/therapists', '/rooms/couple-suite', '/gift-cards',
  '/mood', '/quiz', '/skin', '/privacy', '/login', '/register', '/account', '/wallet',
];

/** ตัวอักษรไทยที่มองเห็นบนหน้า ไม่นับชื่อร้าน "สบายใจ สปา" และป้ายปุ่มภาษา "ไทย" (ชื่อภาษาในตัวเลือกภาษา) */
async function thaiOnPage(page: Page) {
  return page.evaluate(() => {
    const skip = (el: Element | null) => !!el?.closest('[data-testid^="lang-"]');
    // ตัวอักษรไทย U+0E01–0E3A และ U+0E40–0E5B (ไม่นับ ฿ U+0E3F ซึ่งใช้ทุกภาษา)
    const thai = new RegExp('[' + String.fromCharCode(0x0e01) + '-' + String.fromCharCode(0x0e3a) + String.fromCharCode(0x0e40) + '-' + String.fromCharCode(0x0e5b) + ']');
    const found: string[] = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      const el = n.parentElement;
      if (!el || skip(el)) continue;
      const style = getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden' || el.closest('script,style,noscript')) continue;
      const text = (n.textContent ?? '').replace(/สบายใจ\s*สปา|สบายใจ/g, '');
      if (thai.test(text)) found.push(text.trim().slice(0, 60));
    }
    // alt / aria-label / placeholder ที่อ่านออกเสียงหรือเห็นได้
    for (const el of Array.from(document.querySelectorAll('[alt],[aria-label],[placeholder],[title]'))) {
      if (skip(el)) continue;
      for (const a of ['alt', 'aria-label', 'placeholder', 'title']) {
        const v = (el.getAttribute(a) ?? '').replace(/สบายใจ\s*สปา|สบายใจ/g, '');
        if (thai.test(v)) found.push(`[${a}] ${v.slice(0, 60)}`);
      }
    }
    return found;
  });
}

test.describe('ประสบการณ์ / หลายภาษา', () => {
  test('TC-EXP-01 เปลี่ยนภาษา 3 ภาษา จำค่าที่เลือกเมื่อเปลี่ยนหน้า และแปลครบ', {
    tag: ['@EXP', '@P2'],
    annotation: [
      {
        type: 'expected',
        description:
          'มีปุ่มภาษาแค่ 3 ปุ่ม (lang-th, lang-en, lang-zh) · lang-en aria-pressed="true" และยังเป็น English หลังเปลี่ยนหน้าและรีโหลด (cookie lang=en) · ' +
          'หน้า 中文 และ English มีตัวอักษรไทย 0 จุด ยกเว้นชื่อร้าน (NFR-04) · API จองรอบเต็มพร้อม cookie lang=en / zh → message "This time is already booked" / "该时间已被预订"',
      },
      { type: 'note', description: 'ไม่นับป้ายปุ่มเลือกภาษา "ไทย" ซึ่งเป็นชื่อภาษาในตัวเลือกภาษา · API ใช้คิว seed ของมาลี 2026-10-10 14:00 (อ่านอย่างเดียว)' },
    ],
  }, async ({ page, context, playwright, baseURL, apiLog }) => {
    await open(page, '/');
    await expect(page.getByTestId('site-header').getByTestId(/^lang-/)).toHaveCount(3);
    for (const l of ['th', 'en', 'zh']) await expect(page.getByTestId(`lang-${l}`)).toBeVisible();

    await page.getByTestId('lang-en').click();
    await expect(page.getByTestId('lang-en')).toHaveAttribute('aria-pressed', 'true');
    await page.getByTestId('nav-book').click();
    await expect(page).toHaveURL(/\/book/);
    await expect(page.getByTestId('lang-en')).toHaveAttribute('aria-pressed', 'true');
    await page.reload();
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    await expect(page.getByTestId('lang-en')).toHaveAttribute('aria-pressed', 'true');
    expect((await context.cookies()).find((c) => c.name === 'lang')?.value).toBe('en');
    await pause(page);

    const leaks: string[] = [];
    for (const lang of ['zh', 'en']) {
      await page.getByTestId(`lang-${lang}`).click();
      await expect(page.getByTestId(`lang-${lang}`)).toHaveAttribute('aria-pressed', 'true');
      for (const path of PAGES) {
        await test.step(`${lang} ${path}: ไม่มีตัวอักษรไทย`, async () => {
          await open(page, path);
          await expect(page.getByTestId(`lang-${lang}`)).toHaveAttribute('aria-pressed', 'true');
          const found = await thaiOnPage(page);
          if (found.length) leaks.push(`${lang} ${path}: ${found.slice(0, 3).join(' | ')}${found.length > 3 ? ` … (${found.length} จุด)` : ''}`);
          expect.soft(found, `${lang} ${path} มีตัวอักษรไทย`).toEqual([]);
        });
      }
    }
    if (leaks.length) note(`จุดที่ยังเป็นภาษาไทย: ${leaks.join(' ; ')}`);

    for (const [lang, msg] of [['en', 'This time is already booked'], ['zh', '该时间已被预订']]) {
      const ctx = await playwright.request.newContext({ baseURL, extraHTTPHeaders: { cookie: `lang=${lang}` } });
      const r = await apiLog.call(ctx, 'POST', '/api/bookings', bookingBody({ date: '2026-10-10', time: '14:00', therapistId: 1 }), `cookie lang=${lang}`);
      expect.soft(r.body, `lang=${lang}`).toMatchObject({ ok: false, error: 'SLOT_TAKEN', message: msg });
      await ctx.dispose();
    }
  });

  test('TC-EXP-02 ปุ่มเพลงสปา: ไม่เล่นเองเมื่อเปิดเว็บ และเปิด/ปิดได้', {
    tag: ['@EXP', '@P3'],
    annotation: {
      type: 'expected',
      description: 'โหลดครั้งแรก music-toggle data-playing="false" และไม่มีเสียงเล่นเอง (NFR-09) · กดครั้งที่ 1 → data-playing="true", aria-pressed="true" · กดครั้งที่ 2 → "false"',
    },
  }, async ({ page }) => {
    // context ใหม่ของทุก test = storage ว่าง · นับ AudioContext ที่หน้าเว็บสร้างเอง
    await page.addInitScript(() => {
      const w = window as unknown as { __audio: number; AudioContext: typeof AudioContext };
      w.__audio = 0;
      const Orig = w.AudioContext;
      if (Orig) {
        w.AudioContext = class extends Orig {
          constructor(...a: ConstructorParameters<typeof AudioContext>) {
            super(...a);
            w.__audio++;
          }
        } as typeof AudioContext;
      }
    });
    await open(page, '/');
    const btn = page.getByTestId('music-toggle');
    await expect(btn).toHaveAttribute('data-playing', 'false');
    await page.waitForTimeout(1500);
    expect(await page.evaluate(() => (window as unknown as { __audio: number }).__audio), 'ต้องไม่สร้างเสียงเองตอนเปิดเว็บ').toBe(0);
    const hasAudio = await page.evaluate(() => typeof (window.AudioContext ?? (window as unknown as { webkitAudioContext?: unknown }).webkitAudioContext) === 'function');
    test.skip(!hasAudio, 'เบราว์เซอร์ทดสอบนี้ไม่มี Web Audio API (Playwright WebKit บน Windows) จึงเปิดเพลงไม่ได้ — ตรวจได้แค่ "ไม่เล่นเองตอนเปิดเว็บ"');
    await btn.click();
    await expect(btn).toHaveAttribute('data-playing', 'true');
    await expect(btn).toHaveAttribute('aria-pressed', 'true');
    await pause(page);
    await btn.click();
    await expect(btn).toHaveAttribute('data-playing', 'false');
    await expect(btn).toHaveAttribute('aria-pressed', 'false');
  });

  test('TC-EXP-03 ทัวร์ 360° ห้อง Couple Suite ลากหมุนได้ และมีปุ่มจอง', {
    tag: ['@EXP', '@P3'],
    annotation: {
      type: 'expected',
      description:
        '/rooms redirect ไป /rooms/couple-suite · tour-360 data-loaded="true" ภายใน 5 วินาที (NFR-10) · กด tour-right / ลาก / ปุ่มลูกศร แล้ว data-angle เปลี่ยน และอยู่ในช่วง 0–359 เสมอ (รวมกรณีหมุนผ่าน 0) · ' +
        'tour-book แสดง "จองห้องนี้" และพาไปหน้าจอง',
    },
  }, async ({ page }) => {
    await page.goto('/rooms');
    await expect(page).toHaveURL(/\/rooms\/couple-suite$/);
    const tour = page.getByTestId('tour-360');
    await expect(tour).toHaveAttribute('data-loaded', 'true', { timeout: 5000 });
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    await tour.scrollIntoViewIfNeeded();
    const angle = async () => Number(await tour.getAttribute('data-angle'));
    const inRange = (a: number) => Number.isInteger(a) && a >= 0 && a <= 359;

    // ปุ่มขวา 13 ครั้ง (หมุนเกิน 360° → ผ่าน 0)
    const seen: number[] = [];
    let prev = await angle();
    let changed = 0;
    for (let i = 0; i < 13; i++) {
      await page.getByTestId('tour-right').click();
      const a = await angle();
      seen.push(a);
      if (a !== prev) changed++;
      prev = a;
    }
    expect.soft(changed, 'กด tour-right แล้วมุมต้องเปลี่ยนทุกครั้ง').toBe(13);
    expect.soft(seen.filter((a) => !inRange(a)), `มุมนอกช่วง 0–359: ${seen.join(', ')}`).toEqual([]);
    note(`ต้องถาม #8: มุมหลังกด tour-right 13 ครั้ง = ${seen.join(', ')}`, 'ต้องถาม');

    // ปุ่มซ้าย (หมุนย้อนผ่าน 0)
    for (let i = 0; i < 13; i++) {
      await page.getByTestId('tour-left').click();
      expect.soft(inRange(await angle()), 'tour-left ต้องอยู่ในช่วง 0–359').toBe(true);
    }

    // ลากเมาส์
    await tour.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    const before = await angle();
    const box = (await tour.boundingBox())!;
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width / 2 - 200, box.y + box.height / 2, { steps: 10 });
    await page.mouse.up();
    await page.waitForTimeout(500);
    const dragged = await angle();
    expect.soft(dragged, 'ลากแล้วมุมต้องเปลี่ยน').not.toBe(before);
    expect.soft(inRange(dragged)).toBe(true);

    // ปุ่มลูกศรบนคีย์บอร์ด
    await page.waitForTimeout(1500); // รอแรงเหวี่ยงหยุด
    await tour.focus();
    const k0 = await angle();
    await page.keyboard.press('ArrowRight');
    const k1 = await angle();
    expect.soft(k1, 'ArrowRight แล้วมุมต้องเปลี่ยน').not.toBe(k0);
    expect.soft(inRange(k1)).toBe(true);
    await pause(page);

    const book = page.getByTestId('tour-book');
    await expect(book).toContainText('จองห้องนี้');
    await book.click();
    await expect(page).toHaveURL(/\/book/);
    await page.locator('html[data-ready="true"]').waitFor({ state: 'attached' });
    note(`ต้องถาม #7: tour-book เลือกแบบคู่ไว้ให้หรือไม่ — booking-kind-couple aria-checked="${await page.getByTestId('booking-kind-couple').getAttribute('aria-checked')}"`, 'ต้องถาม');
  });
});
