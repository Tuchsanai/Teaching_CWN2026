// workers/lib/embed.js — เรียก embedder (Hugging Face TEI · intfloat/multilingual-e5-small · 384 มิติ)
//
// โมเดลตระกูล E5 ต้องใส่ prefix ให้ถูก:
//   - ข้อความเอกสาร (ตอน ingest)  → "passage: ..."
//   - คำถามของผู้ใช้ (ตอนค้น)     → "query: ..."
// TEI: POST ${EMBED_URL}/embed {"inputs": [...]} → [[...384 float...], ...] (normalize แล้ว → cosine = dot)
// ส่งทีละไม่เกิน 32 ข้อความ (ค่า max-client-batch-size เริ่มต้นของ TEI)
const EMBED_URL = (process.env.EMBED_URL || 'http://localhost:8080').replace(/\/$/, '');
const BATCH = 32;
const MAX_CHARS = 1500; // กันข้อความยาวเกิน (e5-small รับได้ 512 token)

async function postEmbed(inputs, { retries = 3 } = {}) {
  for (let i = 0; ; i++) {
    try {
      const r = await fetch(`${EMBED_URL}/embed`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ inputs, truncate: true }),
        signal: AbortSignal.timeout(60000),
      });
      if (!r.ok) throw new Error(`embedder HTTP ${r.status}: ${(await r.text()).slice(0, 200)}`);
      const out = await r.json();
      if (!Array.isArray(out) || out.length !== inputs.length) throw new Error('embedder ตอบผิดรูปแบบ');
      return out;
    } catch (e) {
      if (i >= retries) throw e;
      await new Promise((res) => setTimeout(res, 1000 * (i + 1)));
    }
  }
}

/** embed หลายข้อความ (ใส่ prefix ให้แล้ว) → array ของ vector */
export async function embedTexts(texts, prefix = 'passage: ') {
  const out = [];
  for (let i = 0; i < texts.length; i += BATCH) {
    const batch = texts.slice(i, i + BATCH).map((t) => prefix + String(t).slice(0, MAX_CHARS));
    out.push(...(await postEmbed(batch)));
  }
  return out;
}

/** embed เอกสาร (passage) */
export const embedPassages = (texts) => embedTexts(texts, 'passage: ');

/** embed คำถาม 1 ข้อ (query) → vector */
export async function embedQuery(text) {
  const [v] = await embedTexts([text], 'query: ');
  return v;
}

/** แปลง vector เป็นรูปแบบ literal ของ pgvector: '[0.1,0.2,...]' */
export const toPgVector = (v) => `[${v.join(',')}]`;
