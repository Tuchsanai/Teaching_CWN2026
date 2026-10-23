// 🔊 อ่านออกเสียง T01–T03 — รันเมื่อ BM_TTS=1 (ต้องเปิด profile tts)
// บันทึกเวลาเริ่มเล่นเทียบเวลาเริ่มวิดีโอ → attach 'audio' {audioId, offsetMs, durationMs} ให้ make-media.mjs รวมเสียงเข้า MP4
import type { Page, TestInfo } from '@playwright/test';
import { bmCase, expect, intro, ask, expectAnswer, say, show, hold, highlight, openChat, attachJson, TTS, MODE, ANSWER_TIMEOUT } from './_bm';

const skip = () => (TTS ? false : 'ตั้ง BM_TTS=1 และเปิด profile tts ก่อน');

const logLen = (page: Page) => page.evaluate(() => (window as any).__bmAudioLog?.length ?? 0);

/** รอเสียงใหม่ใน window.__bmAudioLog → attach offset/duration → ค้างจนเสียงจบ + 1.5 วิ */
async function waitAudio(page: Page, info: TestInfo, before: number) {
  await expect.poll(() => logLen(page), { timeout: 120_000, message: 'รอ window.__bmAudioLog (เสียงเริ่มเล่น)' }).toBeGreaterThan(before);
  const rec = await page.evaluate(() => {
    const log = (window as any).__bmAudioLog;
    const r = log[log.length - 1];
    const a = document.querySelector('[data-testid="chat-audio"]') as HTMLAudioElement | null;
    return { ...r, timeOrigin: performance.timeOrigin, elDuration: a && isFinite(a.duration) ? a.duration * 1000 : null, paused: a?.paused ?? null };
  });
  let durationMs: number = rec.durationMs ?? rec.elDuration ?? 0;
  if (!durationMs) {
    durationMs = await page
      .waitForFunction(() => {
        const a = document.querySelector('[data-testid="chat-audio"]') as HTMLAudioElement | null;
        return a && isFinite(a.duration) && a.duration > 0 ? a.duration * 1000 : false;
      }, null, { timeout: 15_000 })
      .then((h) => h.jsonValue() as Promise<number>)
      .catch(() => 0);
  }
  const videoStart = (page as any).__bmVideoStart as number;
  const offsetMs = Math.max(0, Math.round(rec.timeOrigin + rec.startedAt - videoStart));
  const audio = { audioId: rec.audioId as string, offsetMs, durationMs: Math.round(durationMs) };
  await attachJson(info, 'audio', audio);

  // ไฟล์ WAV จริงจาก /api/tts/<id>
  const wav = await page.request.get(`/api/tts/${audio.audioId}`);
  expect(wav.ok()).toBe(true);
  const body = await wav.body();
  expect(wav.headers()['content-type'] || '').toContain('audio');
  expect(body.subarray(0, 4).toString('latin1')).toBe('RIFF');

  await say(page, `🔊 กำลังเล่นเสียง ${(audio.durationMs / 1000).toFixed(1)} วินาที (audioId ${audio.audioId.slice(0, 8)}…)`);
  await highlight(page.locator('[data-testid="tts-play"]').last(), audio.durationMs + 1500);
  await hold(page, audio.durationMs + 1500);
  expect(audio.durationMs).toBeGreaterThan(1000);
  return audio;
}

async function askAndPlay(page: Page, info: TestInfo, q: string) {
  const ans = await ask(page, info, q, { holdMs: 2500 });
  const btn = page.getByTestId('tts-play').last();
  await expect(btn).toBeVisible();
  await say(page, 'กด 🔊 ฟังคำตอบ');
  await highlight(btn, 2000);
  await hold(page, 1200);
  const before = await logLen(page);
  await btn.click();
  await waitAudio(page, info, before);
  return ans;
}

bmCase(
  'T01',
  async ({ page, item }, info) => {
    await page.goto('/');
    await intro(page, item);
    const ans = await askAndPlay(page, info, 'ร้านเปิดกี่โมงครับ');
    expect(ans.text).toMatch(/[฀-๿]/); // คำตอบไทย → เสียงไทย (PyThaiTTS)
  },
  { skip, timeout: 6 * 60_000 },
);

bmCase(
  'T02',
  async ({ page, item }, info) => {
    await page.goto('/');
    await intro(page, item);
    const ans = await askAndPlay(page, info, 'How much is Portland cement?');
    if (MODE === 'mock') expect(ans.text, 'ตอบภาษาอังกฤษ (ไม่มีอักษรไทย)').not.toMatch(/[฀-๿]/);
    else {
      // ai: ยอมให้มีชื่อสินค้าภาษาไทยปนได้ แต่เนื้อความต้องเป็นอังกฤษ (อักษรละติน ≥ 70% ของตัวอักษรทั้งหมด)
      const th = (ans.text.match(/[฀-๿]/g) || []).length;
      const en = (ans.text.match(/[A-Za-z]/g) || []).length;
      expect(en / Math.max(1, en + th), `ตอบภาษาอังกฤษ (ละติน ${en} · ไทย ${th})`).toBeGreaterThanOrEqual(0.7);
    }
    expectAnswer(ans.text, [/(^|\D)145(\D|$)/]);
  },
  { skip, timeout: 6 * 60_000 },
);

bmCase(
  'T03',
  async ({ page, item }, info) => {
    await page.goto('/');
    await intro(page, item);
    await openChat(page);
    const sw = page.getByTestId('tts-auto');
    await expect(sw).toBeAttached({ timeout: 15_000 });
    await say(page, 'เปิดสวิตช์ “อ่านออกเสียงอัตโนมัติ”');
    await highlight(sw.locator('xpath=..'), 2500);
    await sw.check({ force: true });
    await expect(sw).toBeChecked();
    await hold(page, 1500);
    const before = await logLen(page);
    const ans = await ask(page, info, 'มีโค้ดส่วนลดไหม', { holdMs: 300, timeout: ANSWER_TIMEOUT });
    await say(page, 'ไม่ต้องกด 🔊 — ระบบสร้างเสียงแล้วเล่นเอง');
    await waitAudio(page, info, before);
    expectAnswer(ans.text, [/BUILD5/i]);
    await show(page, page.getByTestId('chat-msg-bot').last(), 1000);
  },
  { skip, timeout: 6 * 60_000 },
);
