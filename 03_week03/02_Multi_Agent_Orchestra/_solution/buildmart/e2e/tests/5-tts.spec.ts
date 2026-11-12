// 🔊 อ่านออกเสียง T01–T03 (v3: VoxCPM2 เสียง "น้องช่าง") — tts-worker เปิดเสมอ · BM_TTS=0 ปิดกลุ่มนี้
// engine: ai = 'voxcpm2' (ai-box GPU-3) · mock = 'mock' (เสียง VoxCPM2 ที่อัดไว้ใน voice-fixtures/tts-cache หรือ generic/tone)
// บันทึกเวลาเริ่มเล่นเทียบเวลาเริ่มวิดีโอ → attach 'audio' {audioId, offsetMs, durationMs, engine} ให้ make-media.mjs รวมเสียงเข้า MP4
import type { Page, TestInfo } from '@playwright/test';
import { test, bmCase, expect, intro, ask, expectAnswer, say, show, hold, highlight, openChat, attachJson, TTS, MODE, ANSWER_TIMEOUT } from './_bm';
import { waitAudio, audioLogLen, nextTtsEngine, expectEngine } from './_voice';

const skip = () => (TTS ? false : 'BM_TTS=0 (ปิดกลุ่ม T)');

/** tts-worker ต้องต่ออยู่ (มี consumer ที่ tts.request) — ไม่งั้นข้ามพร้อมเหตุผล */
async function requireTts(page: Page) {
  const st = await page.request.get('/api/tts/status').then((r) => r.json()).catch(() => ({}));
  test.skip(!st.enabled, 'tts-worker ไม่ได้ต่อคิว tts.request (/api/tts/status enabled=false)');
}

async function playAndCheck(page: Page, info: TestInfo, click: () => Promise<void>) {
  const before = await audioLogLen(page);
  const eng = nextTtsEngine(page);
  await click();
  const audio = await waitAudio(page, info, before);
  const e = await Promise.race([eng, new Promise<{ engine: null; cached: boolean; status: number }>((r) => setTimeout(() => r({ engine: null, cached: false, status: 0 }), 1000))]);
  await attachJson(info, 'checked', { audioId: audio.audioId, durationMs: audio.durationMs, engine: e.engine ?? (e.cached ? '(cache)' : null), mode: MODE });
  expectEngine(e);
  return audio;
}

async function askAndPlay(page: Page, info: TestInfo, q: string) {
  const ans = await ask(page, info, q, { holdMs: 2500 });
  const btn = page.getByTestId('tts-play').last();
  await expect(btn).toBeVisible();
  await say(page, 'กด 🔊 ฟังคำตอบ (เสียง VoxCPM2 “น้องช่าง”)');
  await highlight(btn, 2000);
  await hold(page, 1200);
  await playAndCheck(page, info, () => btn.click());
  return ans;
}

bmCase(
  'T01',
  async ({ page, item }, info) => {
    await requireTts(page);
    await page.goto('/');
    await intro(page, item);
    const ans = await askAndPlay(page, info, 'ร้านเปิดกี่โมงครับ');
    expect(ans.text).toMatch(/[฀-๿]/); // คำตอบไทย → VoxCPM2 พูดไทย
  },
  { skip, timeout: 6 * 60_000 },
);

bmCase(
  'T02',
  async ({ page, item }, info) => {
    await requireTts(page);
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
    await requireTts(page);
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
    const before = await audioLogLen(page);
    const eng = nextTtsEngine(page);
    const ans = await ask(page, info, 'มีโค้ดส่วนลดไหม', { holdMs: 300, timeout: ANSWER_TIMEOUT });
    await say(page, 'ไม่ต้องกด 🔊 — ระบบสร้างเสียงแล้วเล่นเอง');
    const audio = await waitAudio(page, info, before);
    const e = await Promise.race([eng, new Promise<{ engine: null; cached: boolean; status: number }>((r) => setTimeout(() => r({ engine: null, cached: false, status: 0 }), 1000))]);
    await attachJson(info, 'checked', { audioId: audio.audioId, durationMs: audio.durationMs, engine: e.engine ?? (e.cached ? '(cache)' : null), mode: MODE });
    expectEngine(e);
    expectAnswer(ans.text, [/BUILD5/i]);
    await show(page, page.getByTestId('chat-msg-bot').last(), 1000);
  },
  { skip, timeout: 6 * 60_000 },
);
