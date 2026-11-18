#!/usr/bin/env node
// loadtest/run_load.mjs — ทดสอบโหลด BuildMart ผ่าน web API จริง (CONTRACT_V3 §8) · Node 22 ไม่มี dependency
//
// ใช้:
//   node loadtest/run_load.mjs --mode chat|stt|tts|voice|rerank [--users 1,2,4,8,16,32] [--stage-sec 120] [--label ชื่อ]
//        [--url http://localhost:3400] [--mq http://localhost:15672] [--config loadtest/config.json] [--no-post]
//        [--drain-sec 60] [--post-also http://localhost:3500,...] [--aibox-env .env.aibox]
//   ผู้ใช้จำลองแต่ละคน = session (cookie bm_sid) ของตัวเอง ยิงคำขอวนต่อเนื่องจนหมดเวลาขั้น (ไม่มีเวลาคิด = โหลดสูงสุด)
//   ขั้นถัดไปเริ่มเมื่อคิวว่าง (รอ ≤ --drain-sec)
//
// โหมด + metric ต่อขั้น (นอกจาก n · errors · p50 · p95 · queue_max · rps · ok):
//   chat   POST /api/chat (SSE) · ttft_p50/p95 (ถึง delta แรก)
//          tok_s_per_user_p50 = token ขาออก ÷ (เวลารวม − TTFT) ต่อคำขอ · tok_s_total = token ขาออกทั้งขั้น ÷ เวลาขั้น
//          token_count_method = 'llm_usage' (done.usage จาก LLM จริง) | 'approx_chars/<chars_per_token>' (ไม่มี usage)
//   stt    POST /api/voice (ไฟล์ใน e2e/voice-fixtures/index.json · ไม่มี → WAV สังเคราะห์)
//          x_realtime_p50 = วินาทีเสียง ÷ วินาทีประมวลผล · audio_s_per_s_total · clips_per_s
//   tts    POST /api/tts (ข้อความไม่ซ้ำทุกครั้ง กัน cache) + GET /api/tts/<id> ถึง byte แรก
//          rtf_p50 = เวลาสร้าง ÷ ความยาวเสียง · audio_s_per_s_total · ttfa_p50/p95 (time to first audio byte)
//   rerank POST ${RERANK_URL}/v1/rerank ตรง (key จาก .env.aibox · ไม่พิมพ์ค่า) query 1 ข้อ + 20 ย่อหน้า
//          passages_per_s_total · p50/p95
//   voice  /api/voice → /api/chat → /api/tts → byte แรกของเสียง (หยุดพูด → ได้ยินคำตอบ)
//          first_audio_p50/p95 + breakdown_p50 {stt, chat_ttft, chat, tts, audio_fetch}
//
// ผล: loadtest/results/<label>.json = {label, config, summary:{mode, max_users_ok, ...}, stages:[...]}
//   แล้ว POST เข้า /api/admin/load (header x-eval-token: $EVAL_TOKEN หรือ bm-eval) ของ --url และ --post-also
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
const MODES = ['chat', 'stt', 'tts', 'voice', 'rerank'];
const MODE = arg('--mode', 'chat');
if (!MODES.includes(MODE)) {
  console.error(`--mode ต้องเป็น ${MODES.join(' | ')}`);
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
// --post-also http://localhost:3400,... = ส่งผลไป dashboard อื่นด้วย (เช่น stack mock + stack AI)
const POST_TO = [BASE, ...arg('--post-also', '').split(',').map((x) => x.trim().replace(/\/+$/, '')).filter(Boolean)];
const TOKEN = process.env.EVAL_TOKEN || 'bm-eval';

const CFG = JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
const TH = CFG.thresholds?.[MODE] || {};
const CPT = Number(CFG.chars_per_token || 2.5);
const QUESTIONS = CFG.questions || ['ปูนซีเมนต์ถุงละเท่าไร'];
const TTS_TEXTS = CFG.tts_texts || ['สวัสดีครับ'];
const QUEUES = { chat: ['chat.request'], stt: ['stt.request'], tts: ['tts.request'], voice: ['stt.request', 'chat.request', 'tts.request'], rerank: [] }[MODE];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const pct = (a, p) => {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y);
  return s[Math.min(s.length - 1, Math.max(0, Math.ceil((p / 100) * s.length) - 1))];
};
const r0 = (v) => (v == null ? null : Math.round(v));
const r2 = (v) => (v == null || !Number.isFinite(v) ? null : +v.toFixed(2));
const r3 = (v) => (v == null || !Number.isFinite(v) ? null : +v.toFixed(3));
const sum = (a) => a.reduce((s, v) => s + v, 0);

// ---------------------------------------------------------------- rerank (ตรงไป ai-box · อ่าน .env.aibox แต่ไม่พิมพ์ค่า)
function readEnvFile(p) {
  const out = {};
  try {
    for (const line of readFileSync(p, 'utf8').split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
      if (m) out[m[1]] = m[2].replace(/^["']|["']$/g, '');
    }
  } catch {}
  return out;
}
const AIBOX = MODE === 'rerank' ? { ...readEnvFile(arg('--aibox-env', path.join(ROOT, '.env.aibox'))), ...process.env } : {};
const RERANK_URL = (AIBOX.RERANK_URL || AIBOX.AIBOX_URL || 'http://localhost:8000').replace(/\/+$/, '');
const RERANK_DOCS = Number(CFG.rerank_passages || 20);
const PASSAGES = (() => {
  const base = [...(CFG.tts_texts || []), ...(CFG.questions || [])];
  const out = [];
  for (let i = 0; out.length < RERANK_DOCS; i++) out.push(`${base[i % base.length]} (ย่อหน้าที่ ${i + 1}: รายละเอียดสินค้า การใช้งาน การเก็บรักษา และเงื่อนไขของร้าน)`);
  return out;
})();

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
    // chat-worker ตอบข้อความขอโทษสำเร็จรูปเมื่อ LLM ล่ม (type done) → นับเป็น error ไม่ใช่คำตอบเร็ว
    if (/ระบบผู้ช่วยตอบกลับไม่ได้ชั่วคราว|assistant is temporarily unavailable/.test(done.text || '')) throw new Error('chat: LLM unavailable (fallback answer)');
    const ms = performance.now() - t0;
    if (ttft == null) ttft = ms;
    const u = done.usage;
    const tokens = u?.completion_tokens > 0 ? u.completion_tokens : String(done.text || '').length / CPT;
    const method = u?.completion_tokens > 0 ? 'llm_usage' : `approx_chars/${CPT}`;
    const gen = Math.max(1, ms - ttft);
    return { ms, ttft, text: done.text || '', tokens, method, tps: tokens / (gen / 1000) };
  }
  async stt(a) {
    const t0 = performance.now();
    const fd = new FormData();
    fd.append('audio', new Blob([a.buf], { type: a.mime }), a.name);
    const r = await this.fetch('/api/voice', { method: 'POST', body: fd });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(`voice HTTP ${r.status} ${j.error || ''}`);
    const ms = performance.now() - t0;
    const audioMs = j.durationMs || a.durationMs || null;
    return { ms, text: j.text || '', audioMs, xrt: audioMs ? audioMs / ms : null };
  }
  async tts(text) {
    const t0 = performance.now();
    const r = await this.fetch('/api/tts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || !j.audioId) throw new Error(`tts HTTP ${r.status} ${j.error || ''}`);
    const gen = performance.now() - t0;
    const a = await this.fetch('/api/tts/' + j.audioId);
    const rd = a.body.getReader();
    await rd.read();
    const ttfa = performance.now() - t0;
    rd.cancel().catch(() => {});
    return { ms: ttfa, gen, ttfa, audioMs: j.durationMs || null, rtf: j.durationMs ? gen / j.durationMs : null, cached: !!j.cached };
  }
  async rerank(q) {
    const t0 = performance.now();
    const r = await fetch(RERANK_URL + '/v1/rerank', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(AIBOX.AIBOX_API_KEY ? { Authorization: `Bearer ${AIBOX.AIBOX_API_KEY}` } : {}) },
      body: JSON.stringify({ query: q, documents: PASSAGES, top_n: 4 }),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || !Array.isArray(j.results)) throw new Error(`rerank HTTP ${r.status}`);
    return { ms: performance.now() - t0, passages: PASSAGES.length };
  }
  /** คำขอ 1 ครั้งตามโหมด */
  async once() {
    const k = this.n++;
    const uniq = `${this.id}-${k}-${Date.now() % 100000}`;
    if (MODE === 'chat') return this.chat(QUESTIONS[(this.id + k) % QUESTIONS.length]);
    if (MODE === 'stt') return this.stt(AUDIO[(this.id + k) % AUDIO.length]);
    if (MODE === 'tts') return this.tts(`${TTS_TEXTS[(this.id + k) % TTS_TEXTS.length]} รหัส ${uniq}`);
    if (MODE === 'rerank') return this.rerank(QUESTIONS[(this.id + k) % QUESTIONS.length]);
    // voice: หยุดพูด → STT → แชท → TTS → byte แรกของเสียงคำตอบ
    const t0 = performance.now();
    const a = AUDIO[(this.id + k) % AUDIO.length];
    const s = await this.stt(a);
    const q = s.text || a.text || QUESTIONS[(this.id + k) % QUESTIONS.length];
    const c = await this.chat(q);
    const t = await this.tts(`${c.text}`.slice(0, 600) || 'ครับ');
    const ms = performance.now() - t0;
    return { ms, ttft: s.ms + c.ttft, tps: c.tps, tokens: c.tokens, method: c.method, parts: { stt: s.ms, chat_ttft: c.ttft, chat: c.ms, tts: t.gen, audio_fetch: t.ttfa - t.gen } };
  }
}

// ---------------------------------------------------------------- RabbitMQ queue depth
async function queueDepth() {
  let total = 0;
  for (const q of QUEUES) {
    try {
      const r = await fetch(`${MQ}/api/queues/%2F/${encodeURIComponent(q)}`, { headers: { authorization: MQ_AUTH } });
      if (r.ok) total += Number((await r.json()).messages ?? 0);
    } catch {}
  }
  return total;
}
async function drain() {
  if (!QUEUES.length) return true;
  const until = Date.now() + DRAIN_SEC * 1000;
  while (Date.now() < until) {
    if ((await queueDepth()) === 0) return true;
    await sleep(1000);
  }
  return false;
}

// ---------------------------------------------------------------- stage
async function runStage(users) {
  const res = [];
  const errs = [];
  let queueMax = 0;
  const end = Date.now() + STAGE_SEC * 1000;
  let polling = !!QUEUES.length;
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
      await sleep(Math.round((i * 1000) / Math.max(1, users)));
      while (Date.now() < end) {
        try {
          res.push(await c.once());
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
  const lat = res.map((r) => r.ms);
  const col = (k) => res.map((r) => r[k]).filter((v) => v != null && Number.isFinite(v));
  const n = res.length + errs.length;
  const st = {
    users,
    n,
    ok_n: res.length,
    errors: errs.length,
    error_rate: n ? +(errs.length / n).toFixed(4) : 0,
    p50: r0(pct(lat, 50)),
    p95: r0(pct(lat, 95)),
    queue_max: queueMax,
    rps: r3(res.length / wall),
    wall_s: r2(wall),
  };
  if (MODE === 'chat' || MODE === 'voice') {
    const ttft = col('ttft');
    const tps = col('tps');
    Object.assign(st, {
      ttft_p50: r0(pct(ttft, 50)),
      ttft_p95: r0(pct(ttft, 95)),
      tok_s_per_user_p50: r2(pct(tps, 50)),
      tok_s_total: r2(sum(col('tokens')) / wall),
      token_count_method: [...new Set(res.map((r) => r.method).filter(Boolean))].join(',') || null,
      tokens_per_s: r2(pct(tps, 50)), // (เดิม) = tok_s_per_user_p50
    });
  }
  if (MODE === 'stt') {
    const xrt = col('xrt');
    Object.assign(st, {
      x_realtime_p50: r2(pct(xrt, 50)),
      audio_s_per_s_total: r2(sum(col('audioMs')) / 1000 / wall),
      clips_per_s: r3(res.length / wall),
      rtf: xrt.length ? r3(1 / pct(xrt, 50)) : null,
    });
  }
  if (MODE === 'tts') {
    const ttfa = col('ttfa');
    Object.assign(st, {
      rtf_p50: r3(pct(col('rtf'), 50)),
      audio_s_per_s_total: r2(sum(col('audioMs')) / 1000 / wall),
      ttfa_p50: r0(pct(ttfa, 50)),
      ttfa_p95: r0(pct(ttfa, 95)),
      rtf: r3(pct(col('rtf'), 50)),
    });
  }
  if (MODE === 'rerank') {
    Object.assign(st, { passages_per_s_total: r2(sum(col('passages')) / wall), requests_per_s: r3(res.length / wall) });
  }
  if (MODE === 'voice') {
    const part = (k) => res.map((r) => r.parts?.[k]).filter((v) => v != null);
    Object.assign(st, {
      first_audio_p50: st.p50,
      first_audio_p95: st.p95,
      breakdown_p50: Object.fromEntries(['stt', 'chat_ttft', 'chat', 'tts', 'audio_fetch'].map((k) => [k, r0(pct(part(k), 50))])),
      breakdown_p95: Object.fromEntries(['stt', 'chat_ttft', 'chat', 'tts', 'audio_fetch'].map((k) => [k, r0(pct(part(k), 95))])),
    });
  }
  st.error_samples = [...new Set(errs)].slice(0, 3);
  const fail = [];
  if (!lat.length) fail.push('no successful request');
  if (TH.p95_ms != null && st.p95 != null && st.p95 > TH.p95_ms) fail.push(`p95 ${st.p95} > ${TH.p95_ms} ms`);
  if (TH.ttft_p95_ms != null && st.ttft_p95 != null && st.ttft_p95 > TH.ttft_p95_ms) fail.push(`ttft_p95 ${st.ttft_p95} > ${TH.ttft_p95_ms} ms`);
  if (TH.error_rate != null && st.error_rate > TH.error_rate) fail.push(`error_rate ${st.error_rate} > ${TH.error_rate}`);
  st.ok = fail.length === 0;
  st.fail_reasons = fail;
  return st;
}

function line(st) {
  const extra = {
    chat: () => ` ttft=${st.ttft_p50}/${st.ttft_p95}ms tok/s/user=${st.tok_s_per_user_p50} tok/s total=${st.tok_s_total} (${st.token_count_method})`,
    stt: () => ` x_rt=${st.x_realtime_p50} audio_s/s=${st.audio_s_per_s_total} clips/s=${st.clips_per_s}`,
    tts: () => ` rtf=${st.rtf_p50} audio_s/s=${st.audio_s_per_s_total} ttfa=${st.ttfa_p50}/${st.ttfa_p95}ms`,
    rerank: () => ` passages/s=${st.passages_per_s_total}`,
    voice: () => ` first_audio=${st.first_audio_p50}/${st.first_audio_p95}ms breakdown_p50=${JSON.stringify(st.breakdown_p50)}`,
  }[MODE]();
  return `users=${String(st.users).padStart(3)} n=${String(st.n).padStart(4)} err=${st.errors} p50=${st.p50}ms p95=${st.p95}ms${extra} queue_max=${st.queue_max} rps=${st.rps} ${st.ok ? 'OK' : 'FAIL ' + st.fail_reasons.join('; ')}`;
}

// ---------------------------------------------------------------- main
async function main() {
  const h = await fetch(BASE + '/api/health').catch(() => null);
  if (!h?.ok) throw new Error(`web ไม่พร้อม: ${BASE}/api/health`);
  console.log(`load test mode=${MODE} users=${USERS.join(',')} stage=${STAGE_SEC}s url=${MODE === 'rerank' ? '(ai-box rerank)' : BASE} label=${LABEL}`);
  console.log(`thresholds ${JSON.stringify(TH)}`);
  const stages = [];
  for (const u of USERS) {
    if (!(await drain())) console.warn(`  (คิวยังไม่ว่างหลังรอ ${DRAIN_SEC}s — เริ่มขั้นต่อไปเลย)`);
    const st = await runStage(u);
    stages.push(st);
    console.log(line(st));
  }
  let maxOk = 0;
  for (const s of stages) {
    if (!s.ok) break;
    maxOk = s.users;
  }
  const best = stages.filter((s) => s.ok).pop() || null;
  const result = {
    label: LABEL,
    config: {
      mode: MODE, users: USERS, stage_sec: STAGE_SEC, url: BASE, thresholds: TH, chars_per_token: CPT,
      audio_files: AUDIO.map((a) => a.name), rerank_passages: MODE === 'rerank' ? RERANK_DOCS : undefined,
      prefetch: { chat: process.env.CHAT_PREFETCH || null, stt: process.env.STT_PREFETCH || null, tts: process.env.TTS_PREFETCH || null },
      note: arg('--note', undefined),
    },
    summary: {
      mode: MODE,
      max_users_ok: maxOk,
      thresholds: TH,
      stages_ok: stages.filter((s) => s.ok).length,
      stages_total: stages.length,
      best_rps: Math.max(0, ...stages.map((s) => s.rps)),
      at_max_users_ok: best ? { users: best.users, p50: best.p50, p95: best.p95 } : null,
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
    for (const base of POST_TO) {
      try {
        const r = await fetch(base + '/api/admin/load', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-eval-token': TOKEN }, body: JSON.stringify(result) });
        const j = await r.json().catch(() => ({}));
        console.log(r.ok ? `POST ${base}/api/admin/load → id ${j.id}` : `POST ${base}/api/admin/load ไม่สำเร็จ (${r.status} ${j.error || ''})`);
      } catch (e) {
        console.log(`POST ${base}/api/admin/load ไม่สำเร็จ (${e.message})`);
      }
    }
  }
}

main().catch((e) => {
  console.error('load test failed:', e.message);
  process.exit(1);
});
