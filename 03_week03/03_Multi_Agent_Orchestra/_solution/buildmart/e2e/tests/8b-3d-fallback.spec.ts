// 🧊 D03 — ไม่มี WebGL (launch Chromium ด้วย --disable-webgl --disable-3d-apis) → ภาพ fallback แทนฉาก 3D · ฟีเจอร์อื่นทำงานปกติ
// ไฟล์แยกเพราะ launchOptions เป็นค่าระดับ worker (Playwright เปิด browser ใหม่ให้ไฟล์นี้)
import { test, bmCase, expect, intro, ask, expectAnswer, say, show, hold, typeHuman, highlight, attachJson, BASE_ARGS } from './_bm';
import { installMascotRecorder, mascotLen, mascotSince, hasSeq } from './_voice';

test.use({ launchOptions: { args: [...BASE_ARGS, '--disable-webgl', '--disable-3d-apis'] } });

bmCase('D03', async ({ page, item }, info) => {
  const errs: string[] = [];
  page.on('pageerror', (e) => errs.push(e.message));
  await installMascotRecorder(page);
  await page.goto('/');
  await intro(page, item);
  const gl = await page.evaluate(() => !!(document.createElement('canvas').getContext('webgl2') || document.createElement('canvas').getContext('webgl')));
  expect(gl, 'เบราว์เซอร์นี้ไม่มี WebGL').toBe(false);

  // หน้าแรก: ไม่มี <canvas> · แสดงภาพแทนฉาก 3D (ภาพพื้นหลัง hero + มาสคอตภาพนิ่ง)
  const hero = page.getByTestId('hero-3d');
  await expect(hero).toHaveAttribute('data-render', 'flat', { timeout: 20_000 });
  await expect(page.locator('canvas')).toHaveCount(0);
  const fallback = page.locator('[data-testid="banner-hero"], .hero3d-bg, .hero-flat-mascot');
  await expect(fallback.first()).toBeVisible();
  const bg = await page.locator('.hero3d-bg').evaluate((e) => getComputedStyle(e).backgroundImage).catch(() => '');
  const flatImg = page.locator('.hero-flat-mascot');
  await expect(flatImg).toBeVisible();
  expect(await flatImg.evaluate((i: HTMLImageElement) => i.complete && i.naturalWidth > 0), 'รูปมาสคอต fallback โหลดได้').toBe(true);
  await say(page, 'ไม่มี WebGL → หน้าแรกแสดงภาพแบนเนอร์ + มาสคอตภาพนิ่งแทนฉาก 3D (ไม่มี <canvas>)');
  await show(page, hero, 3500);
  // ไม่มีข้อความ error บนจอ
  const body = await page.locator('body').innerText();
  expect(body).not.toMatch(/Application error|Unhandled Runtime Error|WebGL.*(error|not supported)|เกิดข้อผิดพลาด/i);

  // ค้นหา "ปูน" ได้ปกติ
  await say(page, 'ค้นหา “ปูน” — ฟีเจอร์อื่นยังทำงานปกติ');
  await typeHuman(page.getByTestId('search-input'), 'ปูน');
  await page.getByTestId('search-btn').click();
  const cards = page.locator('[data-testid="product-card"][data-sku^="CEM-"]');
  await expect(cards.first()).toBeVisible({ timeout: 20_000 });
  const skus = await cards.evaluateAll((els) => els.map((e) => e.getAttribute('data-sku')));
  await show(page, cards, 3000);

  // แชท: มาสคอตเป็น <img> 2D · state ยังเปลี่ยน thinking → idle · ตอบ 07:00
  const m0 = await mascotLen(page);
  const ans = await ask(page, info, 'ร้านเปิดกี่โมงครับ');
  const mascot = page.getByTestId('mascot');
  await expect(mascot).toHaveAttribute('data-render', 'img');
  await expect(mascot.locator('img')).toHaveCount(1);
  await expect(mascot.locator('canvas')).toHaveCount(0);
  await expect.poll(async () => (await mascotSince(page, m0)).last?.state, { timeout: 15_000 }).toBe('idle');
  const m = await mascotSince(page, m0);
  expect(hasSeq(m.states, ['thinking', 'idle']), `มาสคอต ${m.states.join('→')}`).toBe(true);
  expectAnswer(ans.text, [{ mock: '07:00', ai: /(^|\D)0?7\s*[:.]\s*00|(^|\D)7\s*โมง|เจ็ดโมง/ }]);
  await say(page, `มาสคอต 2D (<img>) · ท่า ${m.states.join(' → ')}`);
  await show(page, mascot, 3000);
  await attachJson(info, 'checked', { webgl: gl, heroRender: 'flat', canvases: 0, heroBg: bg.slice(0, 80), search: skus, mascot: { render: 'img', states: m.states }, pageErrors: errs });
  expect(errs, 'ไม่มี pageerror').toEqual([]);
  await hold(page, 1000);
});
