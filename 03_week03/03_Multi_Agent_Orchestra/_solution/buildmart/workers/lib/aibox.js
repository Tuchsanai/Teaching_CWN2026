// workers/lib/aibox.js — เรียก "ai-box" (Whisper · VoxCPM2 · bge-reranker) (CONTRACT_V3 §2–§3)
// ai-box แยก 2 เครื่องได้ (GPU-2 stt · GPU-3 tts+rerank) → URL แยกต่อบริการ:
//   STT_URL · TTS_URL · RERANK_URL  จาก .env.aibox (env_file ใน compose) · ไม่มี → AIBOX_URL (ถ้ามี) → mock-llm (http://mock-llm:8000)
//   AIBOX_API_KEY  key เดียวกันทุกเครื่อง ส่งเป็น Authorization: Bearer <key> (ทุก endpoint ยกเว้น /health) · ห้าม log ค่านี้
//
//   rerank(query, documents, topN)  → [{index, relevance_score}] เรียงมาก→น้อย · ล่ม → null (ผู้เรียกใช้ลำดับเดิม)
//   transcribe(buffer, mime, lang)  → {text, language, duration}
//   aiboxConfig(service)            → {url, apiKey, mock} · aiboxInfo(service) → {url, mock} (ไว้ log · ไม่มี key)

const trimSlash = (s) => String(s || '').trim().replace(/\/+$/, '');
const VAR = { stt: 'STT_URL', tts: 'TTS_URL', rerank: 'RERANK_URL' };

/** @param {'stt'|'tts'|'rerank'} service */
export function aiboxConfig(service, env = process.env) {
  const own = trimSlash(env[VAR[service]]) || trimSlash(env.AIBOX_URL);
  const url = own || trimSlash(env.MOCK_LLM_URL || 'http://mock-llm:8000');
  return {
    url,
    apiKey: (env.AIBOX_API_KEY || '').trim(),
    mock: !own || /mock-llm/i.test(url),
  };
}

export const aiboxInfo = (service) => {
  const c = aiboxConfig(service);
  return { url: c.url, mock: c.mock, hasKey: !!c.apiKey };
};

function headers(service, extra = {}) {
  const c = aiboxConfig(service);
  return c.apiKey ? { Authorization: `Bearer ${c.apiKey}`, ...extra } : extra;
}

async function call(service, path, init, timeoutMs) {
  const c = aiboxConfig(service);
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const r = await fetch(c.url + path, { ...init, signal: ctrl.signal });
    const body = await r.text();
    if (!r.ok) throw new Error(`ai-box ${path} HTTP ${r.status}: ${body.slice(0, 200)}`);
    return JSON.parse(body);
  } catch (e) {
    if (e.name === 'AbortError') throw new Error(`ai-box ${path} timeout ${timeoutMs}ms`);
    throw e;
  } finally {
    clearTimeout(t);
  }
}

// reranker ล่ม/ไม่มี → พักไม่เรียกซ้ำ 30 วิ (ไม่ให้ทุกคำถามช้าเพราะรอ timeout)
let rerankDownUntil = 0;

/**
 * จัดอันดับย่อหน้าใหม่ด้วย cross-encoder (bge-reranker-v2-m3 บน ai-box · mock = ลำดับเดิม)
 * @returns {Promise<{index:number, relevance_score:number}[] | null>}
 */
export async function rerank(query, documents, topN = 4, { timeoutMs = Number(process.env.RERANK_TIMEOUT_MS || 15000) } = {}) {
  if (!documents.length) return [];
  if (Date.now() < rerankDownUntil) return null;
  try {
    const j = await call(
      'rerank',
      '/v1/rerank',
      { method: 'POST', headers: headers('rerank', { 'Content-Type': 'application/json' }), body: JSON.stringify({ query, documents, top_n: topN }) },
      timeoutMs,
    );
    const res = Array.isArray(j?.results) ? j.results : null;
    if (!res) throw new Error('bad rerank response');
    return res
      .filter((x) => Number.isInteger(x.index) && x.index >= 0 && x.index < documents.length)
      .sort((a, b) => b.relevance_score - a.relevance_score);
  } catch (e) {
    rerankDownUntil = Date.now() + 30_000;
    console.warn('[aibox] rerank unavailable → hybrid order:', e.message);
    return null;
  }
}

const EXT = { 'audio/webm': 'webm', 'audio/ogg': 'ogg', 'audio/wav': 'wav', 'audio/x-wav': 'wav', 'audio/wave': 'wav', 'audio/mpeg': 'mp3', 'audio/mp3': 'mp3', 'audio/mp4': 'm4a', 'audio/x-m4a': 'm4a' };

/** ถอดเสียง → ข้อความ (Whisper บน ai-box · mock = เทียบ sha256 ของไฟล์ทดสอบ) */
export async function transcribe(buf, mime = 'audio/webm', lang = '', { timeoutMs = Number(process.env.STT_TIMEOUT_MS || 55000) } = {}) {
  const base = String(mime || '').split(';')[0].trim().toLowerCase();
  const fd = new FormData();
  fd.append('file', new Blob([buf], { type: base || 'application/octet-stream' }), `speech.${EXT[base] || 'webm'}`);
  if (lang) fd.append('language', lang);
  fd.append('response_format', 'json');
  return call('stt', '/v1/audio/transcriptions', { method: 'POST', headers: headers('stt'), body: fd }, timeoutMs);
}
