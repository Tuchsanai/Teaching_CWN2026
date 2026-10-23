// workers/lib/rag-search.js — Hybrid RAG search (ค้นเอกสาร PDF ที่ ingest แล้วในตาราง doc_chunks)
//
// ┌──────────────────────────── อธิบายอัลกอริทึม (สำหรับนักศึกษา) ────────────────────────────┐
// │ คำถาม เช่น "ทาบเหล็ก DB12 ต้องยาวเท่าไร" ถูกค้น 2 วิธีพร้อมกัน แล้วรวมอันดับด้วย RRF           │
// │                                                                                             │
// │ ① ค้นตามความหมาย (vector search)                                                              │
// │    - แปลงคำถามเป็นเวกเตอร์ 384 มิติด้วยโมเดล multilingual-e5-small (ต้องขึ้นต้น "query: ")      │
// │      ส่วนเอกสารตอน ingest ขึ้นต้น "passage: " (กติกาของโมเดลตระกูล E5)                           │
// │    - pgvector: `embedding <=> q` = cosine distance → vecSim = 1 - distance (ยิ่งใกล้ 1 ยิ่งเหมือน)│
// │    - เก่งเรื่องคำพ้องความหมาย: ถาม "เก็บได้นานแค่ไหน" เจอย่อหน้า "อายุการเก็บรักษา 3 เดือน"         │
// │                                                                                             │
// │ ② ค้นตามคำ (keyword search)                                                                  │
// │    - แยกคำสำคัญจากคำถาม: รหัส/ตัวเลขอังกฤษ (DB12, THW, 2.5, TIL-001, 16A→16) ให้น้ำหนัก 2        │
// │      และคำไทย (ตัดคำฟุ่มเฟือย เช่น ครับ ไหม เท่าไร ออก เหลือชิ้นยาว ≥ 2 ตัวอักษร) น้ำหนัก 1      │
// │    - นับว่า chunk มีคำเหล่านั้นกี่คำ (strpos แบบไม่สนตัวพิมพ์เล็ก/ใหญ่)                            │
// │    - บวกคะแนน pg_trgm `word_similarity(คำถาม, chunk)` (ทดสอบแล้ว: pg_trgm ใน DB นี้ทำ trigram    │
// │      ให้อักษรไทยได้ — ใช้จับคำไทยที่สะกดใกล้เคียงกัน แม้ภาษาไทยไม่มีช่องว่างระหว่างคำ)            │
// │    - เก่งเรื่องรหัสเฉพาะ ที่ vector มักจับไม่แม่น เช่น DB12 กับ DB16 ดูคล้ายกันในเชิงความหมาย      │
// │                                                                                             │
// │ ③ รวมผลด้วย RRF (Reciprocal Rank Fusion)                                                     │
// │    score(chunk) = Σ 1 / (60 + rank)   — rank คืออันดับ (เริ่ม 1) ในแต่ละรายการที่ chunk นั้นอยู่  │
// │    chunk ที่ติดอันดับดีทั้งสองวิธีจะได้คะแนนรวมสูงสุด · ไม่ต้องปรับสเกลคะแนนของสองวิธีให้เท่ากัน    │
// │                                                                                             │
// │ ผลลัพธ์: top k (ค่าเริ่มต้น 4) → [{filename, page, content, score, vecSim, kwScore}]              │
// │ chat-worker ใช้ vecSim ตัดสินว่าควรแสดงป้ายอ้างอิงไหม (คำถามทั่วไป เช่น "ร้านเปิดกี่โมง" vecSim ต่ำ) │
// └─────────────────────────────────────────────────────────────────────────────────────────────┘
import { embedQuery, toPgVector } from './embed.js';

export { embedQuery };

export const RRF_K = 60;
const CANDIDATES = 20; // จำนวนผลจากแต่ละวิธีก่อนนำมารวม
/**
 * เกณฑ์แสดงป้ายอ้างอิง (fallback เมื่อโมเดลไม่ใส่ [n]) — ปรับจากผล workers/rag-selftest.mjs
 *   chunk "ควรอ้างอิง" เมื่อ vecSim ≥ CITE_MIN_VECSIM และ kwScore ≥ CITE_MIN_KW (มีคำสำคัญของคำถามอยู่จริง)
 *   e5-small ให้ cosine กระจุก 0.75–0.93 · คำถามทั่วไปบางข้อ vecSim สูงแต่ไม่มีคำสำคัญตรง → ใช้ 2 เงื่อนไขร่วมกัน
 */
export const CITE_MIN_VECSIM = Number(process.env.RAG_CITE_MIN_VECSIM || 0.865);
export const CITE_MIN_KW = Number(process.env.RAG_CITE_MIN_KW || 1);
/** chunk นี้ควรแสดงเป็นป้ายอ้างอิงไหม (ใช้กับผลอันดับ 1–2 ของ hybridSearch) */
export const isCiteworthy = (r) => !!r && r.vecSim >= CITE_MIN_VECSIM && r.kwScore >= CITE_MIN_KW;

// คำไทยที่ไม่ช่วยในการค้น (คำถาม/คำลงท้าย/คำเชื่อม) — ใช้เป็นตัวแบ่งข้อความไทยออกเป็นชิ้น
const THAI_STOP = [
  'ครับ', 'ค่ะ', 'คะ', 'นะ', 'จ้า', 'แค่ไหน', 'ได้ไหม', 'ได้มั้ย', 'ไหม', 'มั้ย', 'เท่าไหร่', 'เท่าไร', 'อะไร',
  'อย่างไร', 'ยังไง', 'กี่', 'บ้าง', 'หรือเปล่า', 'หรือไม่', 'หรือ', 'แล้ว', 'และ', 'กับ', 'ของ', 'ที่', 'ให้',
  'ต้อง', 'ได้', 'คือ', 'เป็น', 'ช่วย', 'หน่อย', 'ขอ', 'จะ', 'ไป', 'มา', 'มี', 'ใน', 'ว่า', 'ผม', 'ฉัน', 'เรา',
].sort((a, b) => b.length - a.length); // คำยาวก่อน เพื่อไม่ให้ "ไหม" ตัด "ได้ไหม" ผิด

/**
 * แยกคำสำคัญจากคำถาม → [{tok, w}]
 *   ละติน/ตัวเลข: DB12, THW, 2.5, TIL-001, มอก.24 → "24", 16A → "16A" และ "16"  (น้ำหนัก 2)
 *   ไทย: ตัดด้วยคำฟุ่มเฟือย เหลือชิ้นที่ยาว ≥ 2 ตัวอักษร                         (น้ำหนัก 1)
 */
export function extractKeywords(query) {
  const out = new Map();
  const add = (tok, w) => {
    const k = tok.toLowerCase();
    if (k.length >= 2 || /^\d$/.test(k)) out.set(k, Math.max(out.get(k) || 0, w));
  };
  const q = String(query || '');
  for (const m of q.matchAll(/[A-Za-z0-9](?:[A-Za-z0-9.\-\/]*[A-Za-z0-9])?/g)) {
    const tok = m[0];
    add(tok, 2);
    // แยกตัวเลขกับตัวอักษรที่ติดกัน เช่น 16A → 16 (เอกสารเขียน "16 A")
    const parts = tok.split(/(?<=\d)(?=[A-Za-z])|(?<=[A-Za-z])(?=\d)/);
    if (parts.length > 1) parts.forEach((p) => /\d/.test(p) && add(p, 1));
  }
  for (const m of q.matchAll(/[฀-๿]+/g)) {
    let s = m[0];
    for (const w of THAI_STOP) s = s.split(w).join(' ');
    s.split(/\s+/).filter((x) => x.length >= 2).forEach((x) => add(x, 1));
  }
  return [...out].map(([tok, w]) => ({ tok, w }));
}

/**
 * Hybrid search: vector + keyword → RRF
 * @param {import('pg').Pool} pool
 * @param {string} query คำถามผู้ใช้
 * @param {number} k จำนวนผลลัพธ์
 * @returns {Promise<Array<{filename:string, page:number, chunkNo:number, content:string, score:number, vecSim:number, kwScore:number}>>}
 */
export async function hybridSearch(pool, query, k = 4) {
  const q = String(query || '').trim();
  if (!q) return [];
  const qv = toPgVector(await embedQuery(q));
  const kws = extractKeywords(q);

  // ① vector: cosine distance (<=>) ใช้ HNSW index · เฉพาะเอกสารที่ ready
  const vec = await pool.query(
    `SELECT c.id, c.filename, c.page, c.chunk_no, c.content, 1 - (c.embedding <=> $1::vector) AS vec_sim
       FROM doc_chunks c JOIN docs d ON d.id = c.doc_id AND d.status = 'ready'
      ORDER BY c.embedding <=> $1::vector
      LIMIT ${CANDIDATES}`,
    [qv],
  );

  // ② keyword: จำนวนคำที่พบ (ถ่วงน้ำหนัก) + pg_trgm word_similarity
  const kw = await pool.query(
    `SELECT * FROM (
       SELECT c.id, c.filename, c.page, c.chunk_no, c.content,
              1 - (c.embedding <=> $1::vector) AS vec_sim,
              (SELECT COALESCE(SUM(t.w), 0) FROM unnest($2::text[], $3::float8[]) AS t(tok, w)
                WHERE strpos(lower(c.content), t.tok) > 0) AS hits,
              word_similarity($4, c.content) AS wsim
         FROM doc_chunks c JOIN docs d ON d.id = c.doc_id AND d.status = 'ready'
     ) x
     WHERE hits > 0 OR wsim >= 0.3
     ORDER BY hits + wsim DESC, vec_sim DESC
     LIMIT ${CANDIDATES}`,
    [qv, kws.map((x) => x.tok), kws.map((x) => x.w), q],
  );

  // ③ RRF
  const byId = new Map();
  const fuse = (rows, isKw) =>
    rows.forEach((r, i) => {
      const cur = byId.get(r.id) || {
        filename: r.filename,
        page: r.page,
        chunkNo: r.chunk_no,
        content: r.content,
        score: 0,
        vecSim: Number(r.vec_sim),
        kwScore: 0,
      };
      cur.score += 1 / (RRF_K + i + 1);
      if (isKw) cur.kwScore = Number(r.hits) + Number(r.wsim);
      byId.set(r.id, cur);
    });
  fuse(vec.rows, false);
  fuse(kw.rows, true);

  return [...byId.values()]
    .sort((a, b) => b.score - a.score || b.vecSim - a.vecSim)
    .slice(0, k)
    .map((x) => ({ ...x, score: +x.score.toFixed(5), vecSim: +x.vecSim.toFixed(4), kwScore: +x.kwScore.toFixed(3) }));
}
