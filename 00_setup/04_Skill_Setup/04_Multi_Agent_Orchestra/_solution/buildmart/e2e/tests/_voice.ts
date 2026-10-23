// e2e/tests/_voice.ts — ตัวช่วยกลุ่มเสียง (V) · 3D/มาสคอต (D) · อ่านออกเสียง (T)
// - fixtures เสียงคำถาม: e2e/voice-fixtures/{V01..V10.wav, index.json, questions.json} (สร้างบน GPU จริง · ยังไม่มี → เคสเสียงข้าม ไม่ fail)
// - ไมค์ปลอม: fixtures/fake-mic.ts (WebAudio → getUserMedia) · บันทึกเวลาเริ่มพูดลง attachment 'mic' ให้ make-media รวมเสียงคำถามเข้า MP4
// - มาสคอต: MutationObserver จด data-state / data-mouth ทุกครั้งที่เปลี่ยน → window.__bmMascotLog
import type { APIRequestContext, Page, TestInfo } from '@playwright/test';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { E2E_DIR, MODE, expect, say, hold, highlight, attachJson, norm, ANSWER_TIMEOUT, readAnswer, type Answer } from './_bm';
import { installFakeMic, type MicRec } from '../fixtures/fake-mic';

export const VOICE_DIR = path.join(E2E_DIR, 'voice-fixtures');
export type VoiceQ = { id: string; text: string; lang: string; accept?: string[]; file?: string };
export const QUESTIONS: VoiceQ[] = existsSync(path.join(VOICE_DIR, 'questions.json'))
  ? JSON.parse(readFileSync(path.join(VOICE_DIR, 'questions.json'), 'utf8'))
  : [];
export const question = (file: string) => QUESTIONS.find((q) => q.id === file.replace(/\.wav$/i, '') || q.file === file);

/** fixture พร้อมไหม (ไฟล์ในเครื่อง) — ไม่พร้อม → คืนเหตุผลให้ test.skip */
export function voiceFixturesMissing(files: string[]): string | false {
  const miss = files.filter((f) => !existsSync(path.join(VOICE_DIR, f)));
  if (!existsSync(path.join(VOICE_DIR, 'index.json'))) miss.unshift('index.json');
  return miss.length ? `รอไฟล์เสียง fixture: voice-fixtures/${miss.join(', ')} (สร้างบน GPU จริงก่อน แล้ว rebuild mock-llm)` : false;
}

/** โหมด mock: mock-llm ต้องรู้จัก fixture (index.json ถูก COPY เข้า image ตอน build) — ยังไม่ rebuild → ข้ามพร้อมบอกวิธีแก้ */
export async function mockSttNotReady(req: APIRequestContext, file: string): Promise<string | false> {
  if (MODE !== 'mock') return false;
  try {
    const r = await req.post('/api/voice', {
      multipart: { audio: { name: file, mimeType: 'audio/wav', buffer: readFileSync(path.join(VOICE_DIR, file)) } },
      timeout: 60_000,
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok()) return `/api/voice ตอบ ${r.status()} ${j.error || ''}`;
    if (!String(j.text || '').trim()) return 'mock-llm ยังไม่รู้จักไฟล์เสียง fixture → docker compose -p buildmart --profile mock up -d --build mock-llm';
    return false;
  } catch (e: any) {
    return `/api/voice ใช้ไม่ได้: ${e.message}`;
  }
}

// ---------------- มาสคอต ----------------
export type MascotEv = { t: number; state: string; mouth: number };

export async function installMascotRecorder(page: Page) {
  await page.addInitScript(() => {
    const w = window as any;
    w.__bmMascotLog = [] as { t: number; state: string; mouth: number }[];
    let lastState = '';
    let lastMouth = -1;
    const rec = (el: Element) => {
      const state = el.getAttribute('data-state') || '';
      const mouth = Number(el.getAttribute('data-mouth') || 0);
      if (state === lastState && mouth === lastMouth) return;
      lastState = state;
      lastMouth = mouth;
      w.__bmMascotLog.push({ t: performance.now(), state, mouth });
    };
    const start = () => {
      const cur = document.querySelector('[data-testid="mascot"]');
      if (cur) rec(cur);
      new MutationObserver((muts) => {
        for (const m of muts) {
          if (m.type === 'attributes') {
            const el = m.target as Element;
            if (el.getAttribute?.('data-testid') === 'mascot') rec(el);
          } else
            for (const n of Array.from(m.addedNodes)) {
              if (!(n instanceof Element)) continue;
              const el = n.matches('[data-testid="mascot"]') ? n : n.querySelector('[data-testid="mascot"]');
              if (el) rec(el);
            }
        }
      }).observe(document.documentElement, { subtree: true, childList: true, attributes: true, attributeFilter: ['data-state', 'data-mouth'] });
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
  });
}

export const mascotLen = (page: Page) => page.evaluate(() => ((window as any).__bmMascotLog || []).length as number);

/** ลำดับ state (ตัดซ้ำติดกัน) + ค่า data-mouth ระหว่าง talking ตั้งแต่ index `from` */
export async function mascotSince(page: Page, from = 0) {
  const log: MascotEv[] = await page.evaluate((f) => ((window as any).__bmMascotLog || []).slice(f), from);
  const states: string[] = [];
  for (const e of log) if (states[states.length - 1] !== e.state) states.push(e.state);
  const talkMouth = log.filter((e) => e.state === 'talking').map((e) => e.mouth);
  return { states, talkMouth, mouthChanges: talkMouth.length, maxMouth: Math.max(0, ...talkMouth), last: log[log.length - 1] };
}

/** seq เป็น subsequence ของ states (ตามลำดับ) ไหม */
export const hasSeq = (states: string[], seq: string[]) => {
  let i = 0;
  for (const s of states) if (s === seq[i]) i++;
  return i === seq.length;
};

// ---------------- เสียงตอบ (TTS) ----------------
export type AudioRec = { audioId: string; offsetMs: number; durationMs: number; engine?: string | null };
export const audioLogLen = (page: Page) => page.evaluate(() => (window as any).__bmAudioLog?.length ?? 0);

/** รอเสียงใหม่ใน window.__bmAudioLog → attach 'audio' {audioId, offsetMs, durationMs} → ค้างจนเสียงจบ + 1.5 วิ */
export async function waitAudio(page: Page, info: TestInfo, before: number, opts: { engine?: string | null; caption?: boolean } = {}): Promise<AudioRec & { startedAtPerf: number }> {
  await expect.poll(() => audioLogLen(page), { timeout: 120_000, message: 'รอ window.__bmAudioLog (เสียงเริ่มเล่น)' }).toBeGreaterThan(before);
  const rec = await page.evaluate(() => {
    const log = (window as any).__bmAudioLog;
    const r = log[log.length - 1];
    const a = document.querySelector('[data-testid="chat-audio"]') as HTMLAudioElement | null;
    return { ...r, timeOrigin: performance.timeOrigin, elDuration: a && isFinite(a.duration) ? a.duration * 1000 : null };
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
  const audio: AudioRec = { audioId: rec.audioId as string, offsetMs, durationMs: Math.round(durationMs), engine: opts.engine ?? null };
  await attachJson(info, 'audio', audio);

  // ไฟล์ WAV จริงจาก /api/tts/<id>
  const wav = await page.request.get(`/api/tts/${audio.audioId}`);
  expect(wav.ok()).toBe(true);
  expect(wav.headers()['content-type'] || '').toContain('audio');
  expect((await wav.body()).subarray(0, 4).toString('latin1')).toBe('RIFF');

  if (opts.caption !== false) await say(page, `🔊 น้องช่างพูดคำตอบ ${(audio.durationMs / 1000).toFixed(1)} วินาที${audio.engine ? ` (engine ${audio.engine})` : ''}`);
  // รอให้เสียงเล่นจบจริง (onEnded → playingKey null) แล้วค้างภาพต่อ 1.5 วิ
  await page
    .waitForFunction(() => {
      const a = document.querySelector('[data-testid="chat-audio"]') as HTMLAudioElement | null;
      return !a || a.ended || a.paused;
    }, null, { timeout: audio.durationMs + 20_000, polling: 200 })
    .catch(() => {});
  await hold(page, 1500);
  expect(audio.durationMs, 'เสียงตอบยาว > 1 วินาที').toBeGreaterThan(1000);
  return { ...audio, startedAtPerf: rec.startedAt };
}

/** ฟัง response ของ POST /api/tts ถัดไป → engine ('voxcpm2' | 'mock' | null ถ้าได้จาก cache) */
export function nextTtsEngine(page: Page) {
  return page
    .waitForResponse((r) => r.url().endsWith('/api/tts') && r.request().method() === 'POST', { timeout: 120_000 })
    .then(async (r) => {
      const j = await r.json().catch(() => ({}));
      return { engine: (j.engine as string) ?? null, cached: !!j.cached, status: r.status() };
    })
    .catch(() => ({ engine: null, cached: false, status: 0 }));
}

export function expectEngine(e: { engine: string | null; cached: boolean }) {
  // engine มาเฉพาะตอนสร้างใหม่ (ข้อความเดิม → ได้จาก cache ใน tts_audio ไม่มี engine)
  if (!e.engine) return;
  expect(e.engine, 'engine ของเสียงตอบ').toBe(MODE === 'ai' ? 'voxcpm2' : 'mock');
}

// ---------------- CER (BUILDMART ข้อ 8.2) ----------------
const cerNorm = (s: string) =>
  norm(s)
    .toLowerCase()
    .replace(/[\s\p{P}\p{S}]/gu, '');
export function cer(ref: string, hyp: string) {
  const a = [...cerNorm(ref)];
  const b = [...cerNorm(hyp)];
  if (!a.length) return b.length ? 1 : 0;
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    prev = cur;
  }
  return prev[b.length] / a.length;
}

// ---------------- 1 รอบถามด้วยเสียง ----------------
export async function setupVoice(page: Page) {
  await installFakeMic(page, VOICE_DIR);
  await installMascotRecorder(page);
}

/** เปิด voice-mode (คุยด้วยเสียง → ตอบแล้วเล่นเสียงเอง) */
export async function enableVoiceMode(page: Page) {
  const sw = page.getByTestId('voice-mode');
  await expect(sw).toBeAttached({ timeout: 15_000 });
  await say(page, 'เปิดสวิตช์ “คุยด้วยเสียง” — ถามด้วยไมค์ แล้วน้องช่างพูดตอบเอง');
  await highlight(sw.locator('xpath=..'), 2500);
  if (!(await sw.isChecked())) await sw.check({ force: true });
  await expect(sw).toBeChecked();
  await hold(page, 1500);
}

export type VoiceTurn = {
  n: number;
  file: string;
  expectedText: string;
  transcript: string;
  cer: number;
  answer: Answer;
  audio: AudioRec | null;
  engine: string | null;
  stopToAudioMs: number | null;
  mascot: { states: string[]; mouthChanges: number; maxMouth: number };
  ok: { transcript: boolean; audio: boolean; mascot: boolean };
};

/** กดไมค์ → เล่นไฟล์ fixture เข้าไมค์ปลอม → กดหยุด → รอฟองถอดเสียง 🎙 → คำตอบบอท → เสียงตอบเล่นเอง (voice-mode) → มาสคอตกลับ idle
 *  ตรวจ ①③④ ด้วย expect.soft (ไปต่อทุกรอบ ให้วิดีโอ/รายงานครบ) · ② ให้ผู้เรียกตรวจคำตอบ */
export async function voiceTurn(page: Page, info: TestInfo, n: number, file: string): Promise<VoiceTurn> {
  const q = question(file);
  const expectedText = q?.text || '';
  const voiceRows = page.getByTestId('chat-msg-voice');
  const bots = page.getByTestId('chat-msg-bot');
  const vBefore = await voiceRows.count();
  const bBefore = await bots.count();
  const aBefore = await audioLogLen(page);
  const mBefore = await mascotLen(page);
  const micBefore = await page.evaluate(() => (window as any).__bmMicLog?.length ?? 0);

  await page.evaluate((f) => (window as any).__setMicFile(f), file);
  const ttsEngine = nextTtsEngine(page);
  const mic = page.getByTestId('voice-mic');
  await expect(mic).toBeEnabled({ timeout: 30_000 });
  await say(page, `🎙 รอบ ${n}: กดไมค์แล้วพูด “${expectedText || file}”`);
  await highlight(mic, 1500);
  await mic.click();
  await expect(mic).toHaveAttribute('data-recording', 'true', { timeout: 15_000 });
  await expect.poll(() => page.evaluate(() => (window as any).__bmMicLog?.length ?? 0), { timeout: 15_000 }).toBeGreaterThan(micBefore);
  const micRec: MicRec & { timeOrigin: number } = await page.evaluate(() => {
    const l = (window as any).__bmMicLog;
    return { ...l[l.length - 1], timeOrigin: performance.timeOrigin };
  });
  const videoStart = (page as any).__bmVideoStart as number;
  const micAtt = { file, offsetMs: Math.max(0, Math.round(micRec.timeOrigin + micRec.startedAt - videoStart)), durationMs: Math.round(micRec.durationMs) };
  await attachJson(info, 'mic', micAtt);
  // พูดจนจบไฟล์ + 0.4 วิ แล้วกดหยุด
  await page.waitForTimeout(Math.round(micRec.durationMs) + 400);
  await mic.click();
  const stopAt: number = await page.evaluate(() => performance.now());
  await say(page, '⏹ หยุดอัด → ส่งเสียงไปถอดความ (POST /api/voice → stt.request)');

  // ① ฟองผู้ใช้ 🎙 ข้อความที่ถอดได้
  let transcript = '';
  const gotVoice = await expect
    .poll(() => voiceRows.count(), { timeout: 90_000, message: 'รอฟองข้อความจากเสียง (chat-msg-voice)' })
    .toBeGreaterThan(vBefore)
    .then(() => true)
    .catch(async () => {
      const note = (await page.getByTestId('voice-note').innerText().catch(() => '')).trim();
      expect.soft(false, `รอบ ${n}: ไม่ได้ฟองข้อความจากเสียง ${note ? `(${note})` : ''}`).toBe(true);
      return false;
    });
  const empty = { n, file, expectedText, transcript: '', cer: 1, answer: { text: '', cites: [], citeLabels: [] }, audio: null, engine: null, stopToAudioMs: null, mascot: { states: [], mouthChanges: 0, maxMouth: 0 }, ok: { transcript: false, audio: false, mascot: false } };
  if (!gotVoice) return empty;
  const vrow = voiceRows.nth(vBefore);
  transcript = (await vrow.getByTestId('chat-msg-user').innerText()).trim();
  await highlight(vrow, 3000);
  const c = Math.min(cer(expectedText, transcript), ...(q?.accept || []).map((a) => cer(a, transcript)));
  const transcriptOk = MODE === 'mock' ? norm(transcript) === norm(expectedText) : c <= 0.25;
  expect.soft(transcriptOk, `รอบ ${n}: ข้อความถอดเสียง “${transcript}” ${MODE === 'mock' ? `ควรตรง “${expectedText}”` : `CER ${c.toFixed(2)} ควร ≤ 0.25`}`).toBe(true);

  // ② คำตอบบอท
  const bot = bots.nth(bBefore);
  await expect(bot).toHaveAttribute('data-done', 'true', { timeout: ANSWER_TIMEOUT });
  const answer = await readAnswer(page, bot);
  await info.attach(`answer-${n}`, { body: answer.text, contentType: 'text/plain' });
  await highlight(bot, 4000);

  // ③ เสียงตอบเล่นเอง (voice-mode)
  let audio: (AudioRec & { startedAtPerf: number }) | null = null;
  try {
    audio = await waitAudio(page, info, aBefore, { engine: null, caption: true });
  } catch (e: any) {
    expect.soft(false, `รอบ ${n}: เสียงตอบไม่เล่นเอง (${e.message.split('\n')[0]})`).toBe(true);
  }
  const eng = await Promise.race([ttsEngine, new Promise<{ engine: null; cached: boolean }>((r) => setTimeout(() => r({ engine: null, cached: false }), 1000))]);
  if (audio) {
    audio.engine = eng.engine;
    if (eng.engine) expect.soft(eng.engine, `รอบ ${n}: engine`).toBe(MODE === 'ai' ? 'voxcpm2' : 'mock');
  }

  // ④ มาสคอต listening → thinking → talking (data-mouth > 0) → idle
  await expect.poll(async () => (await mascotSince(page, mBefore)).last?.state, { timeout: 15_000 }).toBe('idle').catch(() => {});
  const m = await mascotSince(page, mBefore);
  const mascotOk = hasSeq(m.states, ['listening', 'thinking', 'talking']) && m.states[m.states.length - 1] === 'idle' && m.maxMouth > 0;
  expect.soft(mascotOk, `รอบ ${n}: มาสคอต ${m.states.join('→')} · mouth สูงสุด ${m.maxMouth}`).toBe(true);

  const turn: VoiceTurn = {
    n,
    file,
    expectedText,
    transcript,
    cer: Math.round(c * 1000) / 1000,
    answer,
    audio: audio ? { audioId: audio.audioId, offsetMs: audio.offsetMs, durationMs: audio.durationMs, engine: audio.engine } : null,
    engine: eng.engine,
    stopToAudioMs: audio ? Math.round(audio.startedAtPerf - stopAt) : null,
    mascot: { states: m.states, mouthChanges: m.mouthChanges, maxMouth: m.maxMouth },
    ok: { transcript: transcriptOk, audio: !!audio && audio.durationMs > 1000, mascot: mascotOk },
  };
  await attachJson(info, 'voice-turn', { ...turn, answer: answer.text, cites: answer.cites });
  await say(page, `รอบ ${n} · ถอดได้ “${transcript}” · หยุดพูด→ได้ยินคำตอบ ${turn.stopToAudioMs != null ? (turn.stopToAudioMs / 1000).toFixed(1) + ' วิ' : '–'}`);
  await hold(page, 2000);
  return turn;
}
