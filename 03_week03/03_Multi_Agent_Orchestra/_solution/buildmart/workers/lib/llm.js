// workers/lib/llm.js — เรียก LLM แบบ OpenAI-compatible (NInfer/Qwen บน Vast.ai หรือ mock-llm)
//
//   import { chatLLM, stripThink } from './lib/llm.js';
//   const raw = await chatLLM(messages, { onDelta: (rawSoFar) => ... });
//
// - ลอง stream (SSE) ก่อน ถ้า server ไม่ stream / ล้ม จะ fallback เป็น non-stream
// - ส่ง enable_thinking:false + chat_template_kwargs.enable_thinking:false (ปิดโหมดคิดของ Qwen3)
// - timeout รวม 90 วิ (LLM_TIMEOUT_MS) · error → throw (ผู้เรียกตอบขอโทษเอง)
import { getLlmConfig } from './config.js';

export const llmConfig = getLlmConfig();

function endpoint(base) {
  const b = String(base || '').trim().replace(/\/+$/, '');
  return b.endsWith('/v1') ? `${b}/chat/completions` : `${b}/v1/chat/completions`;
}

function headers(cfg) {
  const h = { 'Content-Type': 'application/json' };
  if (cfg.apiKey) h.Authorization = `Bearer ${cfg.apiKey}`;
  return h;
}

function payload(cfg, messages, stream) {
  return JSON.stringify({
    model: cfg.model || 'mock-buildmart',
    messages,
    stream,
    temperature: 0.2,
    top_p: 0.9,
    max_tokens: 1024,
    enable_thinking: false,
    chat_template_kwargs: { enable_thinking: false },
    // v3: ขอจำนวน token จริงใน chunk สุดท้าย (OpenAI stream_options) → วัด tokens/s ใน load test
    ...(stream ? { stream_options: { include_usage: true } } : {}),
  });
}

/** ตัดส่วนความคิด <think>…</think> (รวมกรณีมีแค่ </think> หรือยังคิดไม่จบระหว่าง stream) */
export function stripThink(raw) {
  let s = String(raw || '');
  const lastClose = s.lastIndexOf('</think>');
  if (lastClose !== -1 && s.slice(0, lastClose).indexOf('<think>') === -1) s = s.slice(lastClose + 8);
  s = s.replace(/<think>[\s\S]*?<\/think>/g, '');
  const open = s.indexOf('<think>');
  if (open !== -1) s = s.slice(0, open);
  const tail = s.match(/<\/?t?h?i?n?k?$/);
  if (tail && tail[0].length > 0 && '<think>'.startsWith(tail[0].replace('/', ''))) s = s.slice(0, tail.index);
  return s.replace(/^\s+/, '');
}

/**
 * @param {{role:string, content:string}[]} messages
 * @param {{onDelta?:(rawSoFar:string)=>void, cfg?:object, timeoutMs?:number}} opt
 * @returns {Promise<string>} ข้อความดิบทั้งหมด (ยังไม่ตัด think/tag)
 */
export async function chatLLM(messages, { onDelta, onUsage, cfg = llmConfig, timeoutMs } = {}) {
  const url = endpoint(cfg.baseUrl);
  const ms = timeoutMs || cfg.timeoutMs || 90000;
  const deadline = Date.now() + ms;
  const left = () => Math.max(1000, deadline - Date.now());

  // ---- 1) stream ----
  let raw = '';
  try {
    const res = await fetch(url, { method: 'POST', headers: headers(cfg), body: payload(cfg, messages, true), signal: AbortSignal.timeout(left()) });
    const ctype = res.headers.get('content-type') || '';
    if (res.ok && res.body && ctype.includes('text/event-stream')) {
      const dec = new TextDecoder();
      let buf = '';
      outer: for await (const chunk of res.body) {
        buf += dec.decode(chunk, { stream: true });
        let nl;
        while ((nl = buf.indexOf('\n')) !== -1) {
          const line = buf.slice(0, nl).trim();
          buf = buf.slice(nl + 1);
          if (!line.startsWith('data:')) continue;
          const data = line.slice(5).trim();
          if (data === '[DONE]') break outer;
          try {
            const j = JSON.parse(data);
            if (j?.usage || j?.timings) onUsage?.({ ...(j.usage || {}), timings: j.timings || null });
            const piece = j?.choices?.[0]?.delta?.content ?? j?.choices?.[0]?.message?.content ?? '';
            if (piece) {
              raw += piece;
              onDelta?.(raw);
            }
          } catch {
            /* ข้ามบรรทัดที่ parse ไม่ได้ */
          }
        }
      }
      if (raw.trim()) return raw;
    } else if (res.ok && ctype.includes('application/json')) {
      const j = await res.json();
      const text = j?.choices?.[0]?.message?.content ?? '';
      if (j?.usage) onUsage?.({ ...j.usage, timings: j.timings || null });
      if (text) {
        onDelta?.(text);
        return text;
      }
    } else {
      const t = await res.text().catch(() => '');
      console.warn(`[llm] stream HTTP ${res.status}: ${t.slice(0, 160)}`);
      if (res.status === 401 || res.status === 403 || res.status === 404) throw new Error(`LLM HTTP ${res.status}`);
    }
  } catch (e) {
    if (raw.trim()) return raw; // ได้มาบางส่วนแล้ว ใช้ส่วนนั้น
    if (/LLM HTTP 40[134]/.test(e.message) || Date.now() >= deadline - 1000) throw e;
    console.warn('[llm] stream error → non-stream:', e.message);
  }

  // ---- 2) non-stream ----
  const res = await fetch(url, { method: 'POST', headers: headers(cfg), body: payload(cfg, messages, false), signal: AbortSignal.timeout(left()) });
  if (!res.ok) {
    const t = await res.text().catch(() => '');
    throw new Error(`LLM HTTP ${res.status}: ${t.slice(0, 160)}`);
  }
  const j = await res.json();
  const text = j?.choices?.[0]?.message?.content ?? '';
  if (j?.usage) onUsage?.({ ...j.usage, timings: j.timings || null });
  if (!text) throw new Error('LLM empty response');
  onDelta?.(text);
  return text;
}
