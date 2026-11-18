// workers/rag-worker.js — ingest เอกสาร PDF เข้า RAG (คิว rag.ingest · prefetch 1)
//
// ตอนเริ่ม: PDF ทุกไฟล์ใน /app/docs (COPY มากับ image) ต้องมีในตาราง docs
//   - ยังไม่มี → INSERT (bytes, status 'queued') · มีแล้วแต่ไฟล์เปลี่ยน (md5 ไม่ตรง) → อัปเดต bytes + 'queued'
//   - เอกสารที่ยังไม่ 'ready' → publish rag.ingest {docId}
// consumer rag.ingest {docId}:
//   status 'processing' → ดึงเนื้อหา (lib/pdf.js: Tagged PDF → หัวข้อ/ย่อหน้า/ตาราง · ไม่มีโครงสร้าง → พิกัดบรรทัด)
//   → chunk ~500 ตัวอักษร ซ้อน 80 (ตาราง: กลุ่มแถว + ชื่อตาราง + หัวคอลัมน์)
//   → embed (TEI, "passage: ", ทีละ ≤32) → ลบ chunk เก่า + INSERT doc_chunks ใหม่ (ใน transaction)
//   → status 'ready', chunks=N, pages=P · ผิดพลาด → status 'failed' + error · ack ทุกกรณี (ไม่วนซ้ำไม่รู้จบ)
// เอกสารที่อัปโหลดจากหลังร้าน (/admin/docs) ใช้เส้นทางเดียวกัน: web INSERT docs แล้ว publish rag.ingest
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { waitForDb, pool, tx } from './lib/db.js';
import { connectAmqp, parseJson, publishJson, Q } from './lib/amqp.js';
import { markReady, idleForever } from './lib/ready.js';
import { extractDocument, buildChunks } from './lib/pdf.js';
import { embedPassages, toPgVector } from './lib/embed.js';

const DOCS_DIR = process.env.DOCS_DIR || '/app/docs';
const CHUNK_SIZE = Number(process.env.CHUNK_SIZE || 500);
const CHUNK_OVERLAP = Number(process.env.CHUNK_OVERLAP || 80);
const log = (...a) => console.log('[rag-worker]', ...a);

/** ingest เอกสาร 1 ไฟล์ → { pages, chunks } */
export async function ingestDoc(docId) {
  const r = await pool.query('SELECT id, filename, bytes FROM docs WHERE id = $1', [docId]);
  if (!r.rowCount) throw new Error(`ไม่พบเอกสาร id=${docId}`);
  const { filename, bytes } = r.rows[0];
  await pool.query(`UPDATE docs SET status = 'processing', error = NULL, updated_at = now() WHERE id = $1`, [docId]);

  const t0 = Date.now();
  // Tagged PDF → หัวข้อ/ย่อหน้า/ตาราง (แถวตารางมีหัวคอลัมน์ติดไปด้วย) · PDF ทั่วไป → ย่อหน้าจากพิกัด
  const { pages, title, tagged, units } = await extractDocument(bytes);
  const rows = buildChunks(units, { size: CHUNK_SIZE, overlap: CHUNK_OVERLAP }).map((c, i) => ({
    page: Math.min(Math.max(1, c.page), pages),
    chunk_no: i,
    content: c.content,
  }));
  if (!rows.length) throw new Error('ไม่พบข้อความใน PDF (อาจเป็นไฟล์สแกนภาพ)');

  // ใส่ชื่อเอกสารนำหน้าตอน embed (ช่วยให้ค้นตามความหมายรู้ว่า chunk นี้มาจากเอกสารเรื่องอะไร) — content ที่เก็บไม่มีหัวนี้
  const head = (title || filename.replace(/\.pdf$/i, '')).trim();
  const vectors = await embedPassages(rows.map((x) => `${head}\n${x.content}`));

  await tx(async (c) => {
    await c.query('DELETE FROM doc_chunks WHERE doc_id = $1', [docId]);
    for (let i = 0; i < rows.length; i++) {
      const x = rows[i];
      await c.query(
        `INSERT INTO doc_chunks (doc_id, filename, page, chunk_no, content, embedding)
         VALUES ($1, $2, $3, $4, $5, $6::vector)`,
        [docId, filename, x.page, x.chunk_no, x.content, toPgVector(vectors[i])],
      );
    }
    await c.query(
      `UPDATE docs SET status = 'ready', pages = $2, chunks = $3, error = NULL, updated_at = now() WHERE id = $1`,
      [docId, pages, rows.length],
    );
  });
  log(`ready ${filename}: ${pages} หน้า ${rows.length} chunks · ${tagged ? 'tagged' : 'plain'} (${Date.now() - t0} ms)`);
  return { pages, chunks: rows.length };
}

/** sync PDF ใน image → ตาราง docs แล้วคืน id ของเอกสารที่ยังไม่ ready */
async function syncBundledDocs() {
  let files = [];
  try {
    files = (await readdir(DOCS_DIR)).filter((f) => f.toLowerCase().endsWith('.pdf')).sort();
  } catch {
    log(`ไม่พบโฟลเดอร์ ${DOCS_DIR} — ข้ามการ sync เอกสารตั้งต้น`);
  }
  for (const f of files) {
    const bytes = await readFile(path.join(DOCS_DIR, f));
    await pool.query(
      `INSERT INTO docs (filename, bytes, status) VALUES ($1, $2, 'queued')
       ON CONFLICT (filename) DO UPDATE
         SET bytes = EXCLUDED.bytes, status = 'queued', error = NULL, updated_at = now()
       WHERE md5(docs.bytes) <> md5(EXCLUDED.bytes)`,
      [f, bytes],
    );
  }
  const r = await pool.query(`SELECT id, filename, status FROM docs WHERE status <> 'ready' ORDER BY id`);
  log(`เอกสารตั้งต้น ${files.length} ไฟล์ · ยังไม่ ready ${r.rowCount} ไฟล์`);
  return r.rows;
}

async function consume({ ch }) {
  await ch.consume(Q.RAG_INGEST, async (msg) => {
    if (!msg) return;
    const body = parseJson(msg);
    const docId = Number(body?.docId);
    try {
      if (!docId) throw new Error('message ไม่มี docId');
      await ingestDoc(docId);
    } catch (e) {
      console.error('[rag-worker] ingest failed', docId, e.message);
      if (docId) {
        await pool
          .query(`UPDATE docs SET status = 'failed', error = $2, updated_at = now() WHERE id = $1`, [
            docId,
            String(e.message).slice(0, 1000),
          ])
          .catch(() => {});
      }
    } finally {
      ch.ack(msg);
    }
  });
  log(`consuming ${Q.RAG_INGEST} (prefetch 1)`);
}

await waitForDb();
const pending = await syncBundledDocs();
const conn0 = await connectAmqp({ prefetch: 1, onReconnect: consume });
for (const d of pending) publishJson(conn0.ch, '', Q.RAG_INGEST, { docId: d.id });
await consume(conn0);
markReady('rag-worker');
idleForever(async () => {
  await conn0.conn.close().catch(() => {});
  await pool.end().catch(() => {});
});
