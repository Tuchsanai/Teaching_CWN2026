#!/usr/bin/env node
// loadtest/run_load.mjs — ทดสอบโหลด BuildMart ผ่าน web API จริง (CONTRACT_V3 §8) · Node 22 ไม่มี dependency
//
// ใช้:
//   node loadtest/run_load.mjs --mode chat|stt|tts|voice [--users 1,2,4,8,16,32] [--stage-sec 120] [--label ชื่อ]
//        [--url http://localhost:3400] [--mq http://localhost:15672] [--config loadtest/config.json] [--no-post] [--drain-sec 60]
//   ผู้ใช้จำลองแต่ละคน = session (cookie bm_sid) ของตัวเอง ยิงคำขอวนต่อเนื่องจนหมดเวลาขั้น (ไม่มีเวลาคิด = โหลดสูงสุด)
//   ขั้นถัดไปเริ่มเมื่อคิวว่าง (รอ ≤ --drain-sec)
//
// โหมด:
//   chat  POST /api/chat (SSE) → latency = จนได้ done · TTFT = ถึง delta แรก · tokens/s ≈ ตัวอักษร ÷ chars_per_token ÷ (latency − TTFT)
//   stt   POST /api/voice (ไฟล์ใน e2e/voice-fixtures/index.json · ไม่มี → WAV สังเคราะห์) · rtf = latency ÷ ความยาวเสียง
//   tts   POST /api/tts (ข้อความไม่ซ้ำทุกครั้ง กัน cache) · rtf = latency ÷ ความยาวเสียงที่ได้
//   voice /api/voice → /api/chat → /api/tts ต่อกัน (ถามด้วยเสียง → ได้ยินคำตอบ) · TTFT = STT + token แรกของแชท
//
// ผล: loadtest/results/<label>.json
//   {label, config:{mode, users, stage_sec, url, thresholds}, summary:{mode, max_users_ok, thresholds, stages_ok, ...},
//    stages:[{users, n, errors, error_rate, p50, p95, ttft_p50, ttft_p95, rtf, tokens_per_s, queue_max, rps, ok, fail_reasons}]}
//   แล้ว POST เข้า /api/admin/load (header x-eval-token: $EVAL_TOKEN หรือ bm-eval) → หน้า /admin/load
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(here, '..');

// ---------------------------------------------------------------- args
const argv = process.argv.slice(2);
const arg = (k, d) => {
  const i = argv.indexOf(k);
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : d;
};
const flag = (k) => argv.includes(k);
const MODE = arg('--mode', 'chat');
if (!['chat', 'stt', 'tts', 'voice'].includes(MODE)) {
  console.error('--mode ต้องเป็น chat | stt | tts | voice');
  process.exit(2);
}
const USERS = arg('--users', '1,2,4,8,16,32').split(',').map(Number).filter((n) => n > 0);
const STAGE_SEC = Number(arg('--stage-sec', 120));
const DRAIN_SEC = Number(arg('--drain-sec', 60));
const BASE = arg('--url', process.env.BM_URL || 'http://localhost:3400').replace(/\/+$/, '');
const MQ = arg('--mq', process.env.BM_MQ_URL || 'http://localhost:15672').replace(/\/+$/, '');
const MQ_AUTH = 'Basic ' + Buffer.from(`${process.env.BM_MQ_USER || 'guest'}:${process.env.BM_MQ_PASS || 'guest'}`).toString('base64');
const CONFIG_PATH = arg('--config', path.join(here, 'config.json'));
const LABEL = arg('--label', `${MODE}-${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}`);
const POST = !flag('--no-post');
const TOKEN = process.env.EVAL_TOKEN || 'bm-eval';

const CFG = JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
const TH = CFG.thresholds?.[MODE] || {};
const CPT = Number(CFG.chars_per_token || 2.5);
const QUESTIONS = CFG.questions || ['ปูนซีเมนต์ถุงละเท่าไร'];
const TTS_TEXTS = CFG.tts_texts || ['สวัสดีครับ'];
const QUEUES = { chat: ['chat.request'], stt: ['stt.request'], tts: ['tts.request'], voice: ['stt.request', 'chat.request', 'tts.request'] }[MODE];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const pct = (a, p) => {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y);
  return Math.round(s[Math.min(s.length - 1, Math.max(0, Math.ceil((p / 100) * s.length) - 1))]);
};
const mean = (a) => (a.length ? a.reduce((s, v) => s + v, 0) / a.length : null);

// ---------------------------------------------------------------- เสียงสำหรับ stt/voice
function synthWav(sec = 2.5) {
  const sr = 16000;
  const n = Math.round(sr * sec);
  const b = Buffer.alloc(44 + n * 2);
  b.write('RIFF', 0); b.writeUInt32LE(36 + n * 2, 4); b.write('WAVE', 8); b.write('fmt ', 12);
  b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22); b.writeUInt32LE(sr, 24);
  b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) b.writeInt16LE(Math.round(Math.sin((2 * Math.PI * 200 * i) / sr) * 4000 * (0.5 + 0.5 * Math.sin((2 * Math.PI * 3 * i) / sr))), 44 + i * 2);
  return b;
}
function loadAudio() {
  const dir = path.join(ROOT, 'e2e', 'voice-fixtures');
  const out = [];
  try {
    const idx = JSON.parse(readFileSync(path.join(dir, 'index.json'), 'utf8'));
    for (const v of Object.values(idx)) {
      if (!v?.file || !existsSync(path.join(dir, v.file))) continue;
      const buf = readFileSync(path.join(dir, v.file));
      const ext = path.extname(v.file).slice(1).toLowerCase();
      out.push({ buf, name: v.file, mime: { wav: 'audio/wav', webm: 'audio/webm', ogg: 'audio/ogg', mp3: 'audio/mpeg' }[ext] || 'audio/wav', durationMs: v.durationMs || null, text: v.text });
    }
  } catch {}
  if (!out.length) out.push({ buf: synthWav(), name: 'synth.wav', mime: 'audio/wav', durationMs: 2500, text: '' });
  return out;
}
const AUDIO = MODE === 'stt' || MODE === 'voice' ? loadAudio() : [];

// ---------------------------------------------------------------- client (1 ผู้ใช้จำลอง = 1 session)
class Client {
  constructor(id) {
    this.id = id;
    this.cookie = '';
    this.n = 0;
  }
  async fetch(p, init = {}) {
    const r = await fetch(BASE + p, { ...init, headers: { ...(init.headers || {}), ...(this.cookie ? { cookie: this.cookie } : {}) } });
    const sc = r.headers.get('set-cookie');
    if (sc && !this.cookie) {
      const m = /bm_sid=[^;]+/.exec(sc);
      if (m) this.cookie = m[0];
    }
    return r;
  }
  async chat(text) {
    const t0 = performance.now();
    const r = await this.fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
    if (!r.ok || !r.body) throw new Error(`chat HTTP ${r.status}`);
    const dec = new TextDecoder();
    let buf = '';
    let ttft = null;
    let done = null;
    for await (const chunk of r.body) {
      buf += dec.decode(chunk, { stream: true });
      let i;
      while ((i = buf.indexOf('\n\n')) >= 0) {
        const block = buf.slice(0, i);
        buf = buf.slice(i + 2);
        const ev = /^event: (\w+)/m.exec(block)?.[1];
        const data = /^data: (.*)$/m.exec(block)?.[1];
        if (ev === 'delta' && ttft == null) ttft = performance.now() - t0;
        if (ev === 'done') done = JSON.parse(data || '{}');
        if (ev === 'error') throw new Error('chat error: ' + (data || '').slice(0, 120));
      }
    }
    if (!done) throw new Error('chat: no done event');
    const ms = performance.now() - t0;
    if (ttft == null) ttft = ms;
    const gen = Math.max(1, ms - ttft);
    return { ms, ttft, text: done.text || '', tps: (String(done.text || '').length / CPT) / (gen / 1000) };
  }
  async stt(a) {
    const t0 = performance.now();
    const fd = new FormData();
    fd.append('audio', new Blob([a.buf], { type: a.mime }), a.name);
    const r = await this.fetch('/api/voice', { method: 'POST', body: fd });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(`voice HTTP ${r.status} ${j.error || ''}`);
    const ms = performance.now() - t0;
    const audioMs = j.durationMs || a.durationMs;
    return { ms, text: j.text || '', rtf: audioMs ? ms / audioMs : null };
  }
  async tts(text) {
    const t0 = performance.now();
    const r = await this.fetch('/api/tts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || !j.audioId) throw new Error(`tts HTTP ${r.status} ${j.error || ''}`);
    const ms = performance.now() - t0;
    return { ms, rtf: j.durationMs ? ms / j.durationMs : null, cached: !!j.cached };
  }
  /** คำขอ 1 ครั้งตามโหมด → {ms, ttft?, rtf?, tps?} */
  async once() {
    const k = this.n++;
    const uniq = `${this.id}-${k}-${Date.now() % 100000}`;
    if (MODE === 'chat') return this.chat(QUESTIONS[(this.id + k) % QUESTIONS.length]);
    if (MODE === 'stt') return this.stt(AUDIO[(this.id + k) % AUDIO.length]);
    if (MODE === 'tts') return this.tts(`${TTS_TEXTS[(this.id + k) % TTS_TEXTS.length]} รหัส ${uniq}`);
    // voice: ถามด้วยเสียง → แชท → เสียงตอบ
    const t0 = performance.now();
    const a = AUDIO[(this.id + k) % AUDIO.length];
    const s = await this.stt(a);
    const q = s.text || a.text || QUESTIONS[(this.id + k) % QUESTIONS.length];
    const c = await this.chat(q);
    await this.tts(`${c.text}`.slice(0, 600) || 'ครับ');
    return { ms: performance.now() - t0, ttft: s.ms + c.ttft, tps: c.tps };
  }
}

// ---------------------------------------------------------------- RabbitMQ queue depth
async function queueDepth() {
  let total = 0;
  for (const q of QUEUES) {
    try {
      const r = await fetch(`${MQ}/api/queues/%2F/${encodeURIComponent(q)}`, { headers: { authorization: MQ_AUTH } });
      if (r.ok) {
        const j = await r.json();
        total += Number(j.messages ?? 0);
      }
    } catch {}
  }
  return total;
}
async function drain() {
  const until = Date.now() + DRAIN_SEC * 1000;
  while (Date.now() < until) {
    if ((await queueDepth()) === 0) return true;
    await sleep(1000);
  }
  return false;
}

// ---------------------------------------------------------------- stage
async function runStage(users) {
  const lat = [];
  const ttft = [];
  const rtf = [];
  const tps = [];
  const errs = [];
  let queueMax = 0;
  const end = Date.now() + STAGE_SEC * 1000;
  let polling = true;
  const poller = (async () => {
    while (polling) {
      queueMax = Math.max(queueMax, await queueDepth());
      await sleep(2000);
    }
  })();
  const t0 = Date.now();
  await Promise.all(
    Array.from({ length: users }, async (_, i) => {
      const c = new Client(i);
      await sleep(Math.round((i * 1000) / Math.max(1, users))); // ไม่ให้ทุกคนยิงพร้อมกันเป๊ะในมิลลิวินาทีเดียว
      while (Date.now() < end) {
        try {
          const r = await c.once();
          lat.push(r.ms);
          if (r.ttft != null) ttft.push(r.ttft);
          if (r.rtf != null) rtf.push(r.rtf);
          if (r.tps != null && Number.isFinite(r.tps)) tps.push(r.tps);
        } catch (e) {
          errs.push(String(e.message || e).slice(0, 160));
          await sleep(500);
        }
      }
    }),
  );
  const wall = (Date.now() - t0) / 1000;
  polling = false;
  await poller;
  const n = lat.length + errs.length;
  const st = {
    users,
    n,
    errors: errs.length,
    error_rate: n ? +(errs.length / n).toFixed(4) : 0,
    p50: pct(lat, 50),
    p95: pct(lat, 95),
    ttft_p50: pct(ttft, 50),
    ttft_p95: pct(ttft, 95),
    rtf: rtf.length ? +mean(rtf).toFixed(3) : null,
    tokens_per_s: tps.length ? +mean(tps).toFixed(1) : null,
    queue_max: queueMax,
    rps: +(lat.length / wall).toFixed(3),
    error_samples: [...new Set(errs)].slice(0, 3),
  };
  const fail = [];
  if (!lat.length) fail.push('no successful request');
  if (TH.p95_ms != null && st.p95 != null && st.p95 > TH.p95_ms) fail.push(`p95 ${st.p95} > ${TH.p95_ms} ms`);
  if (TH.ttft_p95_ms != null && st.ttft_p95 != null && st.ttft_p95 > TH.ttft_p95_ms) fail.push(`ttft_p95 ${st.ttft_p95} > ${TH.ttft_p95_ms} ms`);
  if (TH.error_rate != null && st.error_rate > TH.error_rate) fail.push(`error_rate ${st.error_rate} > ${TH.error_rate}`);
  st.ok = fail.length === 0;
  st.fail_reasons = fail;
  return st;
}

// ---------------------------------------------------------------- main
async function main() {
  const h = await fetch(BASE + '/api/health').catch(() => null);
  if (!h?.ok) throw new Error(`web ไม่พร้อม: ${BASE}/api/health`);
  console.log(`load test mode=${MODE} users=${USERS.join(',')} stage=${STAGE_SEC}s url=${BASE} label=${LABEL}`);
  console.log(`thresholds ${JSON.stringify(TH)}`);
  const stages = [];
  for (const u of USERS) {
    const drained = await drain();
    if (!drained) console.warn(`  (คิวยังไม่ว่างหลังรอ ${DRAIN_SEC}s — เริ่มขั้นต่อไปเลย)`);
    const st = await runStage(u);
    stages.push(st);
    console.log(
      `users=${String(u).padStart(3)} n=${String(st.n).padStart(4)} err=${st.errors} p50=${st.p50}ms p95=${st.p95}ms` +
        (st.ttft_p50 != null ? ` ttft p50/p95=${st.ttft_p50}/${st.ttft_p95}ms` : '') +
        (st.rtf != null ? ` rtf=${st.rtf}` : '') +
        (st.tokens_per_s != null ? ` tok/s=${st.tokens_per_s}` : '') +
        ` queue_max=${st.queue_max} rps=${st.rps} ${st.ok ? 'OK' : 'FAIL ' + st.fail_reasons.join('; ')}`,
    );
  }
  let maxOk = 0;
  for (const s of stages) {
    if (!s.ok) break;
    maxOk = s.users;
  }
  const result = {
    label: LABEL,
    config: { mode: MODE, users: USERS, stage_sec: STAGE_SEC, url: BASE, thresholds: TH, chars_per_token: CPT, audio_files: AUDIO.map((a) => a.name) },
    summary: {
      mode: MODE,
      max_users_ok: maxOk,
      thresholds: TH,
      stages_ok: stages.filter((s) => s.ok).length,
      stages_total: stages.length,
      best_rps: Math.max(0, ...stages.map((s) => s.rps)),
      finished_at: new Date().toISOString(),
    },
    stages,
  };
  const outDir = path.join(here, 'results');
  mkdirSync(outDir, { recursive: true });
  const out = path.join(outDir, `${LABEL.replace(/[^\w.-]+/g, '_')}.json`);
  writeFileSync(out, JSON.stringify(result, null, 2));
  console.log(`\nmax_users_ok = ${maxOk} → ${out}`);
  if (POST) {
    const r = await fetch(BASE + '/api/admin/load', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-eval-token': TOKEN }, body: JSON.stringify(result) });
    const j = await r.json().catch(() => ({}));
    console.log(r.ok ? `POST /api/admin/load → id ${j.id}` : `POST /api/admin/load ไม่สำเร็จ (${r.status} ${j.error || ''})`);
  }
}

main().catch((e) => {
  console.error('load test failed:', e.message);
  process.exit(1);
});
