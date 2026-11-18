// workers/tts-worker.js — ข้อความ → เสียง (v3 · CONTRACT_V3 §4) · เบา ไม่มีโมเดลในตัว (เลิกใช้ Kokoro/PyThaiTTS)
//
// คิว tts.request (durable · prefetch TTS_PREFETCH=2) body {text, lang?} + reply_to/correlation_id
//   → speechText() (shared/speech.js: ตัด tag/[n]/markdown/URL/emoji · ≤ 600 ตัวอักษร)
//   → POST ${TTS_URL}/v1/audio/speech {input, voice:'nongchang', response_format:'wav', language}
//       ai-box จริง = VoxCPM2 (เสียงน้องช่าง) · ไม่มี .env.aibox = mock-llm เล่นไฟล์ที่อัดจาก VoxCPM2 ไว้แล้ว
//       (e2e/voice-fixtures/tts-cache/<sha256(input)>.wav ไม่มี → generic.wav)
//   → INSERT tts_audio (wav, duration_ms, engine) → reply {type:'tts', audioId, durationMs, lang, engine:'voxcpm2'|'mock'}
//   ผิดพลาด → reply {type:'tts', error}
import { pool, waitForDb } from './lib/db.js';
import { connectAmqp, replyTo, parseJson, Q } from './lib/amqp.js';
import { markReady, markNotReady } from './lib/ready.js';
import { aiboxConfig, aiboxInfo } from './lib/aibox.js';
import { speechText, speechLang, wavDurationMs } from '../shared/speech.js';

const PREFETCH = Number(process.env.TTS_PREFETCH || 2);
const VOICE = process.env.TTS_VOICE || 'nongchang';
const TIMEOUT_MS = Number(process.env.TTS_TIMEOUT_MS || 55000);
const log = (...a) => console.log(new Date().toISOString(), '[tts-worker]', ...a);

async function synth(input, lang) {
  const c = aiboxConfig('tts');
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const r = await fetch(`${c.url}/v1/audio/speech`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(c.apiKey ? { Authorization: `Bearer ${c.apiKey}` } : {}) },
      body: JSON.stringify({ input, voice: VOICE, response_format: 'wav', language: lang }),
      signal: ctrl.signal,
    });
    const buf = Buffer.from(await r.arrayBuffer());
    if (!r.ok) throw new Error(`ai-box /v1/audio/speech HTTP ${r.status}: ${buf.toString('utf8').slice(0, 200)}`);
    const engine = r.headers.get('x-tts-engine') === 'mock' || c.mock ? 'mock' : 'voxcpm2';
    return { wav: buf, engine };
  } catch (e) {
    if (e.name === 'AbortError') throw new Error(`tts timeout ${TIMEOUT_MS}ms`);
    throw e;
  } finally {
    clearTimeout(t);
  }
}

async function onMessage(ch, msg) {
  if (!msg) return;
  const t0 = Date.now();
  const body = parseJson(msg) || {};
  const reply = { type: 'tts' };
  try {
    const text = speechText(body.text);
    if (!text) throw new Error('empty text');
    const lang = speechLang(text) === 'th' ? 'th' : ['th', 'en'].includes(body.lang) ? body.lang : 'en';
    // เครือข่ายไป ai-box สะดุดเป็นครั้งคราว ("fetch failed") → ลองซ้ำ 1 ครั้ง
    const { wav, engine } = await synth(text, lang).catch((e) => {
      if (!/fetch failed|ECONNRESET|socket/i.test(e.message)) throw e;
      log(`retry after network error: ${e.message}`);
      return synth(text, lang);
    });
    const durationMs = wavDurationMs(wav);
    if (!durationMs) throw new Error('ai-box returned no WAV audio');
    const r = await pool.query(
      `INSERT INTO tts_audio (lang, text, wav, duration_ms, engine) VALUES ($1, $2, $3, $4, $5) RETURNING id`,
      [lang, text, wav, durationMs, engine],
    );
    Object.assign(reply, { audioId: r.rows[0].id, durationMs, lang, engine });
    log(`ok ${reply.audioId} ${engine} lang=${lang} chars=${text.length} dur=${durationMs}ms took=${Date.now() - t0}ms`);
  } catch (e) {
    reply.error = String(e.message || e).slice(0, 300);
    log(`error ${msg.properties.correlationId}: ${reply.error}`);
  }
  try {
    replyTo(ch, msg, reply);
  } finally {
    ch.ack(msg);
  }
}

async function start({ ch }) {
  await ch.prefetch(PREFETCH);
  await ch.consume(Q.TTS_REQUEST, (m) => onMessage(ch, m).catch((e) => console.error('[tts-worker] crash', e)), { noAck: false });
  const ab = aiboxInfo('tts');
  markReady(`tts-worker aibox=${ab.url}`);
  log(`consuming ${Q.TTS_REQUEST} prefetch=${PREFETCH} aibox=${ab.url}${ab.mock ? ' (mock: pre-recorded VoxCPM2)' : ' (VoxCPM2)'}`);
}

await waitForDb();
// ฐานข้อมูลจาก v2 (volume เดิม) ยังไม่มีคอลัมน์ engine → เพิ่มให้เอง
await pool.query('ALTER TABLE tts_audio ADD COLUMN IF NOT EXISTS engine text').catch((e) => log('migrate engine column:', e.message));
let current = await connectAmqp({ prefetch: PREFETCH, onReconnect: async (again) => { current = again; await start(again); } });
await start(current);

const stop = async () => {
  markNotReady();
  try { await current.ch.close(); } catch {}
  try { await current.conn.close(); } catch {}
  await pool.end().catch(() => {});
  process.exit(0);
};
process.on('SIGTERM', stop);
process.on('SIGINT', stop);
