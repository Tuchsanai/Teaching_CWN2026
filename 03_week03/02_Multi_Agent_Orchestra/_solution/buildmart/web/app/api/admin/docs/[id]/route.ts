// DELETE /api/admin/docs/[id] → ลบเอกสาร (doc_chunks ลบตาม ON DELETE CASCADE)
// POST /api/admin/docs/[id] → เข้าคิวทำ RAG ใหม่ (reindex) จากไฟล์เดิมใน DB
import { NextResponse } from 'next/server';
import { query, tx } from '@/lib/db';
import { sendToQueue, Q } from '@/lib/amqp';
import { requireAdmin } from '../../_auth';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type Ctx = { params: { id: string } };

export async function DELETE(_req: Request, { params }: Ctx) {
  const deny = requireAdmin();
  if (deny) return deny;
  const id = Number(params.id);
  if (!Number.isInteger(id)) return NextResponse.json({ error: 'id ไม่ถูกต้อง' }, { status: 400 });
  const r = await query('DELETE FROM docs WHERE id = $1 RETURNING filename', [id]);
  if (!r.rowCount) return NextResponse.json({ error: 'ไม่พบเอกสาร' }, { status: 404 });
  return NextResponse.json({ deleted: r.rows[0].filename });
}

export async function POST(_req: Request, { params }: Ctx) {
  const deny = requireAdmin();
  if (deny) return deny;
  const id = Number(params.id);
  if (!Number.isInteger(id)) return NextResponse.json({ error: 'id ไม่ถูกต้อง' }, { status: 400 });
  const doc = await tx(async (c) => {
    const r = await c.query(
      `UPDATE docs SET status = 'queued', chunks = 0, error = NULL, updated_at = now() WHERE id = $1 RETURNING id, filename`,
      [id],
    );
    if (r.rowCount) await c.query('DELETE FROM doc_chunks WHERE doc_id = $1', [id]);
    return r.rows[0];
  });
  if (!doc) return NextResponse.json({ error: 'ไม่พบเอกสาร' }, { status: 404 });
  await sendToQueue(Q.RAG_INGEST, { docId: doc.id, filename: doc.filename });
  return NextResponse.json({ id: doc.id, filename: doc.filename, status: 'queued' });
}
