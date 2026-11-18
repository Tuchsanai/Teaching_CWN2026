// GET /api/admin/docs → { items:[{id, filename, pages, chunks, status, error, size, createdAt, updatedAt}] }
// POST /api/admin/docs (multipart field `file`, .pdf ≤ 10MB) → บันทึก docs.bytes status queued → publish rag.ingest {docId, filename}
//   ชื่อไฟล์ซ้ำ = แทนที่ไฟล์เดิม (ลบ chunk เก่า แล้วเข้าคิวทำใหม่)
import { NextResponse } from 'next/server';
import { query, tx } from '@/lib/db';
import { sendToQueue, Q } from '@/lib/amqp';
import { requireAdmin } from '../_auth';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const MAX_BYTES = 10 * 1024 * 1024;

export async function GET() {
  const deny = requireAdmin();
  if (deny) return deny;
  const r = await query(
    `SELECT id, filename, pages, chunks, status, error, octet_length(bytes) AS size, created_at, updated_at
       FROM docs ORDER BY filename`,
  );
  return NextResponse.json({
    items: r.rows.map((d: any) => ({
      id: d.id,
      filename: d.filename,
      pages: d.pages,
      chunks: d.chunks,
      status: d.status,
      error: d.error,
      size: Number(d.size) || 0,
      createdAt: d.created_at,
      updatedAt: d.updated_at,
    })),
  });
}

/** เหลือแค่ชื่อไฟล์ (ตัด path) และตัวอักษรที่ปลอดภัยต่อ URL */
function cleanName(name: string) {
  const base = name.split(/[\\/]/).pop() || '';
  return base.replace(/[^\p{L}\p{N}._-]+/gu, '_').replace(/^[._]+/, '').slice(0, 120);
}

export async function POST(req: Request) {
  const deny = requireAdmin();
  if (deny) return deny;
  const form = await req.formData().catch(() => null);
  const file = form?.get('file');
  if (!file || typeof file === 'string') {
    return NextResponse.json({ error: 'กรุณาเลือกไฟล์ PDF (field file)' }, { status: 400 });
  }
  const filename = cleanName(file.name);
  if (!/\.pdf$/i.test(filename) || filename.length < 5) {
    return NextResponse.json({ error: 'รับเฉพาะไฟล์ .pdf' }, { status: 400 });
  }
  if (file.size > MAX_BYTES) {
    return NextResponse.json({ error: 'ไฟล์ใหญ่เกิน 10MB' }, { status: 413 });
  }
  const bytes = Buffer.from(await file.arrayBuffer());
  if (bytes.subarray(0, 5).toString('latin1') !== '%PDF-') {
    return NextResponse.json({ error: 'ไฟล์นี้ไม่ใช่ PDF ที่ถูกต้อง' }, { status: 400 });
  }

  const doc = await tx(async (c) => {
    const r = await c.query(
      `INSERT INTO docs (filename, bytes, status, chunks, pages, error)
       VALUES ($1, $2, 'queued', 0, NULL, NULL)
       ON CONFLICT (filename) DO UPDATE
         SET bytes = EXCLUDED.bytes, status = 'queued', chunks = 0, pages = NULL, error = NULL, updated_at = now()
       RETURNING id, filename, status, (xmax <> 0) AS replaced`,
      [filename, bytes],
    );
    await c.query('DELETE FROM doc_chunks WHERE doc_id = $1', [r.rows[0].id]);
    return r.rows[0];
  });

  try {
    await sendToQueue(Q.RAG_INGEST, { docId: doc.id, filename: doc.filename });
  } catch (e: any) {
    await query(`UPDATE docs SET status = 'failed', error = $2, updated_at = now() WHERE id = $1`, [
      doc.id,
      `ส่งเข้าคิวไม่สำเร็จ: ${e?.message || e}`,
    ]);
    return NextResponse.json({ error: 'บันทึกไฟล์แล้ว แต่ส่งเข้าคิว rag.ingest ไม่สำเร็จ' }, { status: 503 });
  }
  return NextResponse.json({ id: doc.id, filename: doc.filename, status: doc.status, replaced: doc.replaced, size: bytes.length });
}
