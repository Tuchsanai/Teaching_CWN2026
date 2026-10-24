// e2e/fixtures/fake-mic.ts — ไมค์ปลอมแบบ deterministic (BUILDMART ข้อ 6 · CONTRACT_V3 §9)
// ห่อ navigator.mediaDevices.getUserMedia ให้คืน MediaStream จาก WebAudio (AudioBufferSource → MediaStreamDestination)
// ที่เล่นไฟล์ fixture ที่เลือกด้วย window.__setMicFile('V02.wav') — เปลี่ยนไฟล์ได้ทุกรอบในหน้าเดียว/วิดีโอเดียว
// ไฟล์ WAV เสิร์ฟผ่าน page.route('/__e2e_mic/<file>') จาก e2e/voice-fixtures/ (ไม่ต้องแก้เว็บ)
// ทุกครั้งที่เริ่มเล่น บันทึก window.__bmMicLog.push({file, startedAt, durationMs}) (performance.now()) ไว้ทำ MP4 ที่มีเสียงคำถาม
import type { Page } from '@playwright/test';
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';

export type MicRec = { file: string; startedAt: number; durationMs: number };

export async function installFakeMic(page: Page, fixturesDir: string) {
  await page.route('**/__e2e_mic/**', async (route) => {
    const name = decodeURIComponent(new URL(route.request().url()).pathname.split('/').pop() || '');
    const f = path.join(fixturesDir, path.basename(name));
    if (!existsSync(f)) return route.fulfill({ status: 404, body: 'no fixture' });
    await route.fulfill({ status: 200, contentType: 'audio/wav', body: readFileSync(f) });
  });
  await page.addInitScript(() => {
    const w = window as any;
    const md = navigator.mediaDevices as any;
    w.__bmMicLog = w.__bmMicLog || [];
    let file: string | null = null;
    const cache: Record<string, ArrayBuffer> = {};
    w.__setMicFile = (f: string | null) => {
      file = f;
    };
    if (!md || !md.getUserMedia) return;
    const orig = md.getUserMedia.bind(md);
    md.getUserMedia = async (c: MediaStreamConstraints) => {
      if (!c || !c.audio || !file) return orig(c);
      const name = file;
      const AC = (window as any).AudioContext || (window as any).webkitAudioContext;
      const ctx: AudioContext = new AC({ sampleRate: 48000 });
      try {
        await ctx.resume();
      } catch {}
      if (!cache[name]) cache[name] = await fetch(`/__e2e_mic/${encodeURIComponent(name)}`).then((r) => {
        if (!r.ok) throw new Error(`fake-mic: ไม่มีไฟล์ ${name}`);
        return r.arrayBuffer();
      });
      const buf = await ctx.decodeAudioData(cache[name].slice(0));
      const src = ctx.createBufferSource();
      src.buffer = buf;
      const dest = ctx.createMediaStreamDestination();
      src.connect(dest);
      // เริ่มเล่นช้ากว่าคืน stream 150 ms ให้ MediaRecorder เริ่มอัดทันก่อน (fixture มีความเงียบหน้า 0.3 วิอยู่แล้ว)
      const LEAD = 0.15;
      src.start(ctx.currentTime + LEAD);
      w.__bmMicLog.push({ file: name, startedAt: performance.now() + LEAD * 1000, durationMs: buf.duration * 1000 });
      const stream = dest.stream;
      for (const t of stream.getAudioTracks()) {
        const stop = t.stop.bind(t);
        t.stop = () => {
          stop();
          try {
            src.stop();
          } catch {}
          ctx.close().catch(() => {});
        };
      }
      return stream;
    };
  });
}
