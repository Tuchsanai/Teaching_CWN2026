// workers/stt-worker.js — เสียงพูด → ข้อความ (v3 · CONTRACT_V3 §4)
//
// คิว stt.request (durable · prefetch STT_PREFETCH=8) body {audioB64, mime, lang?} + reply_to/correlation_id (แบบเดียวกับ tts)
//   → POST ${STT_URL}/v1/audio/transcriptions (Whisper บน ai-box · ไม่มี .env.aibox → mock-llm เทียบ sha256 ไฟล์ทดสอบ)
//   → reply ทาง exchange chat.reply: {type:'stt', text, language, durationMs, tookMs, engine} หรือ {type:'stt', error}
// healthcheck: /tmp/ready (เขียนหลัง consume สำเร็จ)
import { connectAmqp, replyTo, parseJson, Q } from './lib/amqp.js';
import { markReady, markNotReady } from './lib/ready.js';
import { transcribe, aiboxInfo } from './lib/aibox.js';

const PREFETCH = Number(process.env.STT_PREFETCH || 8);
const MAX_BYTES = 15 * 1024 * 1024;
const log = (...a) => console.log(new Date().toISOString(), '[stt-worker]', ...a);

async function onMessage(ch, msg) {
  if (!msg) return;
  const t0 = Date.now();
  const body = parseJson(msg) || {};
  const reply = { type: 'stt' };
  try {
    const buf = Buffer.from(String(body.audioB64 || ''), 'base64');
    if (!buf.length) throw new Error('empty audio');
    if (buf.length > MAX_BYTES) throw new Error('audio too large');
    const lang = ['th', 'en'].includes(body.lang) ? body.lang : '';
    const r = await transcribe(buf, body.mime || 'audio/webm', lang);
    const text = String(r?.text || '').trim();
    Object.assign(reply, {
      text,
      language: r?.language || lang || (/[฀-๿]/.test(text) ? 'th' : 'en'),
      durationMs: r?.duration != null ? Math.round(Number(r.duration) * 1000) : null,
      tookMs: Date.now() - t0,
      engine: r?.mock || aiboxInfo('stt').mock ? 'mock' : 'whisper',
    });
    log(`ok ${msg.properties.correlationId} bytes=${buf.length} ${reply.engine} ${reply.tookMs}ms text=${JSON.stringify(text.slice(0, 60))}`);
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
  await ch.consume(Q.STT_REQUEST, (m) => onMessage(ch, m).catch((e) => console.error('[stt-worker] crash', e)), { noAck: false });
  const ab = aiboxInfo('stt');
  markReady(`stt-worker aibox=${ab.url}`);
  log(`consuming ${Q.STT_REQUEST} prefetch=${PREFETCH} aibox=${ab.url}${ab.mock ? ' (mock)' : ''}`);
}

let current = await connectAmqp({ prefetch: PREFETCH, onReconnect: async (again) => { current = again; await start(again); } });
await start(current);

const stop = async () => {
  markNotReady();
  try { await current.ch.close(); } catch {}
  try { await current.conn.close(); } catch {}
  process.exit(0);
};
process.on('SIGTERM', stop);
process.on('SIGINT', stop);
