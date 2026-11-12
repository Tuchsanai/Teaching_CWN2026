// 🧊 3D + มาสคอต D01–D02 (BUILDMART ข้อ 7) — headless ใช้ SwiftShader ทำ WebGL (--enable-unsafe-swiftshader --use-angle=swiftshader)
// D01: ฉาก 3D หน้าแรก (canvas WebGL · ภาพหลายสี · เลื่อนแล้วกล้องเคลื่อน) + มาสคอตในแชท idle · ไม่มี error ใน console
// D02: จด data-state/data-mouth ด้วย MutationObserver → พิมพ์+tts-auto แล้วถามด้วยเสียง V01 (voice-mode)
import type { Page, TestInfo } from '@playwright/test';
import { test, bmCase, expect, intro, ask, openChat, expectAnswer, say, show, hold, highlight, attachJson, BASE_ARGS } from './_bm';
import { setupVoice, installMascotRecorder, enableVoiceMode, voiceTurn, voiceFixturesMissing, mockSttNotReady, mascotLen, mascotSince, hasSeq, waitAudio, audioLogLen } from './_voice';

test.use({ launchOptions: { args: [...BASE_ARGS, '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist'] } });

/** สัดส่วนพิกเซลที่ต่างจากสีที่พบมากที่สุด (quantize 4 bit/ช่อง) + diff ระหว่าง 2 ภาพ — คำนวณใน browser (ไม่ต้องลง lib ถอด PNG) */
async function imageStats(page: Page, a: Buffer, b?: Buffer, offY = 0) {
  return page.evaluate(
    async ({ a, b, offY }) => {
      let wa = 0;
      let wb = 0;
      const load = async (b64: string, set: (w: number) => void) => {
        const img = new Image();
        img.src = `data:image/png;base64,${b64}`;
        await img.decode();
        const c = document.createElement('canvas');
        c.width = img.width;
        c.height = img.height;
        const g = c.getContext('2d')!;
        g.drawImage(img, 0, 0);
        set(c.width);
        return g.getImageData(0, 0, c.width, c.height).data;
      };
      const da = await load(a, (w) => (wa = w));
      const hist = new Map<number, number>();
      for (let i = 0; i < da.length; i += 4) {
        const k = ((da[i] >> 4) << 8) | ((da[i + 1] >> 4) << 4) | (da[i + 2] >> 4);
        hist.set(k, (hist.get(k) || 0) + 1);
      }
      const total = da.length / 4;
      const top = Math.max(...hist.values());
      let diff = null as number | null;
      if (b) {
        // b = ส่วนของ canvas ที่ยังเห็นหลังเลื่อน (แถวที่ offY ของ a ขึ้นไป) → เทียบพิกเซลตำแหน่งเดียวกันบน canvas
        const db = await load(b, (w) => (wb = w));
        const w = Math.min(wa, wb);
        const hb = db.length / 4 / wb;
        let n = 0;
        let cnt = 0;
        for (let y = 0; y < hb; y++)
          for (let x = 0; x < w; x++) {
            const ia = ((y + offY) * wa + x) * 4;
            const ib = (y * wb + x) * 4;
            if (ia + 2 >= da.length) continue;
            cnt++;
            if (Math.abs(da[ia] - db[ib]) + Math.abs(da[ia + 1] - db[ib + 1]) + Math.abs(da[ia + 2] - db[ib + 2]) > 30) n++;
          }
        diff = cnt ? n / cnt : 0;
      }
      return { colors: hist.size, nonDominant: 1 - top / total, diff };
    },
    { a: a.toString('base64'), b: b?.toString('base64'), offY },
  );
}

/** เก็บ error ใน console / pageerror ตั้งแต่เปิดหน้า (ไม่นับ 404 ของรูป .webp→.png fallback) */
function collectErrors(page: Page) {
  const errs: string[] = [];
  page.on('pageerror', (e) => errs.push(`pageerror: ${e.message}`));
  page.on('console', (m) => {
    if (m.type() !== 'error') return;
    const t = m.text();
    if (/Failed to load resource.*(404|net::ERR_ABORTED)/i.test(t)) return;
    errs.push(t);
  });
  return errs;
}

bmCase('D01', async ({ page, item }, info) => {
  const errs = collectErrors(page);
  await page.goto('/');
  await intro(page, item);
  const hero = page.getByTestId('hero-3d');
  await expect(hero, 'ฉาก 3D โหลดเสร็จ (data-render=3d)').toHaveAttribute('data-render', '3d', { timeout: 60_000 });
  const canvas = hero.locator('canvas').first();
  await expect(canvas).toBeVisible();
  const gl = await canvas.evaluate((c: HTMLCanvasElement) => {
    const ctx = (c.getContext('webgl2') || c.getContext('webgl')) as WebGLRenderingContext | null;
    return ctx ? { ok: true, version: ctx.getParameter(ctx.VERSION), renderer: ctx.getParameter(ctx.RENDERER) } : { ok: false };
  });
  expect(gl.ok, '<canvas> ได้ WebGL context').toBe(true);
  await say(page, `ฉาก 3D (WebGL: ${gl.renderer || '?'}) — กล่องวัสดุลอย + มาสคอต`);
  await highlight(hero, 3000);
  await hold(page, 2500);
  const shot1 = await canvas.screenshot();
  const s1 = await imageStats(page, shot1);
  expect(s1.nonDominant, `ภาพในฉากไม่ใช่สีเดียว (พิกเซลที่ต่างจากสีหลัก ${(s1.nonDominant * 100).toFixed(1)}%)`).toBeGreaterThan(0.05);

  await say(page, 'เลื่อนหน้าลง 600 px → กล้องเคลื่อนตาม');
  const box = (await canvas.boundingBox())!; // ตอน scrollY = 0
  await page.mouse.move(640, 400);
  await page.mouse.wheel(0, 600);
  await expect.poll(() => page.evaluate(() => window.scrollY), { timeout: 5000 }).toBeGreaterThan(300);
  await page.waitForTimeout(1800);
  const sy = await page.evaluate(() => window.scrollY);
  // ส่วนของ canvas ที่ยังอยู่ในจอหลังเลื่อน → เทียบกับภาพก่อนเลื่อนที่ตำแหน่งเดียวกันบน canvas
  const top = Math.max(0, box.y - sy);
  const bottom = Math.min(800, box.y + box.height - sy);
  expect(bottom - top, 'หลังเลื่อนยังเห็นฉาก 3D บางส่วน').toBeGreaterThan(40);
  const shot2 = await page.screenshot({ clip: { x: box.x, y: top, width: box.width, height: bottom - top } });
  const s2 = await imageStats(page, shot1, shot2, Math.round(top + sy - box.y));
  expect(s2.diff!, `ก่อน/หลังเลื่อนต่างกัน (${((s2.diff || 0) * 100).toFixed(1)}% ของพิกเซล)`).toBeGreaterThan(0.01);
  await hold(page, 2000);
  await page.evaluate(() => window.scrollTo(0, 0));

  await openChat(page);
  const mascot = page.getByTestId('mascot');
  await expect(mascot).toHaveAttribute('data-render', '3d', { timeout: 60_000 });
  await expect(mascot.locator('canvas')).toHaveCount(1);
  await expect(mascot).toHaveAttribute('data-state', 'idle');
  await say(page, 'มาสคอต “น้องช่าง” 3D ในหน้าต่างแชท · data-state = idle');
  await show(page, mascot, 3500);
  await attachJson(info, 'checked', { webgl: gl, colors: s1.colors, nonDominant: s1.nonDominant, scrollDiff: s2.diff, mascot: 'canvas idle', consoleErrors: errs });
  expect(errs, 'ไม่มี error ใน console').toEqual([]);
});

bmCase(
  'D02',
  async ({ page, item }, info) => {
    const voiceMiss = voiceFixturesMissing(['V01.wav']) || (await mockSttNotReady(page.request, 'V01.wav'));
    if (voiceMiss) await installMascotRecorder(page);
    else await setupVoice(page);
    await page.goto('/');
    await intro(page, item);
    await openChat(page);
    const mascot = page.getByTestId('mascot');
    await expect(mascot).toHaveAttribute('data-state', 'idle');

    // ① พิมพ์ + อ่านออกเสียงอัตโนมัติ: idle → thinking → talking → idle
    const sw = page.getByTestId('tts-auto');
    await expect(sw).toBeAttached({ timeout: 15_000 });
    await say(page, 'เปิด “อ่านออกเสียงอัตโนมัติ” แล้วพิมพ์ถาม — ดูท่ามาสคอต');
    await highlight(sw.locator('xpath=..'), 2000);
    await sw.check({ force: true });
    await hold(page, 1000);
    const m0 = await mascotLen(page);
    const a0 = await audioLogLen(page);
    const ans = await ask(page, info, 'ร้านเปิดกี่โมงครับ', { holdMs: 300, attachName: 'answer-1' });
    expectAnswer(ans.text, [{ mock: '07:00', ai: /(^|\D)0?7\s*[:.]\s*00|(^|\D)7\s*โมง|เจ็ดโมง/ }]);
    await highlight(mascot, 6000);
    await waitAudio(page, info, a0);
    await expect.poll(async () => (await mascotSince(page, m0)).last?.state, { timeout: 15_000 }).toBe('idle');
    await expect(mascot).toHaveAttribute('data-mouth', '0.00', { timeout: 5000 });
    const typed = await mascotSince(page, m0 > 0 ? m0 - 1 : 0);
    await say(page, `ท่าที่จดได้ (พิมพ์): ${typed.states.join(' → ')} · ปากขยับ ${typed.mouthChanges} ครั้ง สูงสุด ${typed.maxMouth.toFixed(2)}`);
    await hold(page, 3000);
    expect(typed.states[0], 'เริ่มที่ idle').toBe('idle');
    expect(hasSeq(typed.states, ['idle', 'thinking', 'talking', 'idle']), `ลำดับ ${typed.states.join('→')}`).toBe(true);
    expect(typed.states.includes('listening'), 'พิมพ์ไม่ต้องมี listening').toBe(false);
    expect(typed.mouthChanges, 'data-mouth เปลี่ยน ≥ 5 ครั้งระหว่าง talking').toBeGreaterThanOrEqual(5);
    expect(typed.maxMouth, 'data-mouth สูงสุด > 0.1').toBeGreaterThan(0.1);
    const result: any = { typed: { states: typed.states, mouthChanges: typed.mouthChanges, maxMouth: typed.maxMouth } };

    // ② ถามด้วยเสียง V01 (voice-mode): idle → listening → thinking → talking → idle
    if (voiceMiss) {
      result.voice = `ข้าม: ${voiceMiss}`;
      info.annotations.push({ type: 'pending', description: `D02 ส่วนเสียง: ${voiceMiss}` });
    } else {
      await sw.uncheck({ force: true });
      await enableVoiceMode(page);
      const m1 = await mascotLen(page);
      const t = await voiceTurn(page, info, 2, 'V01.wav');
      await expect(mascot).toHaveAttribute('data-mouth', '0.00', { timeout: 5000 });
      const v = await mascotSince(page, m1 > 0 ? m1 - 1 : 0);
      await say(page, `ท่าที่จดได้ (เสียง): ${v.states.join(' → ')} · ปากขยับ ${v.mouthChanges} ครั้ง สูงสุด ${v.maxMouth.toFixed(2)}`);
      await hold(page, 3000);
      expect(v.states[0]).toBe('idle');
      expect(hasSeq(v.states, ['idle', 'listening', 'thinking', 'talking', 'idle']), `ลำดับ ${v.states.join('→')}`).toBe(true);
      expect(v.mouthChanges).toBeGreaterThanOrEqual(5);
      expect(v.maxMouth).toBeGreaterThan(0.1);
      expectAnswer(t.answer.text, [{ mock: /3\s*เดือน/, ai: /(^|\D)3\s*เดือน|สามเดือน|90\s*วัน/ }]);
      result.voice = { states: v.states, mouthChanges: v.mouthChanges, maxMouth: v.maxMouth, transcript: t.transcript };
    }
    await attachJson(info, 'checked', result);
  },
  { timeout: 8 * 60_000 },
);
