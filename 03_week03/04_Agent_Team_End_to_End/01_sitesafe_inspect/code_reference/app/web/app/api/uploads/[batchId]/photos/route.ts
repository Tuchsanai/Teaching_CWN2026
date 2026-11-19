// 6 · POST /api/uploads/{batchId}/photos — supervisor who owns the batch: receive 1 file
//     (multipart/form-data, one file part). FR-02, FR-03, FR-04, BR-05, NFR-04 (D-01)
import { randomUUID } from 'node:crypto';
import type { NextRequest } from 'next/server';
import { canAccess, deny, requireAccess, siteScope } from '@/lib/access';
import { todayBangkok } from '@/lib/clock';
import { pool } from '@/lib/db';
import { apiError, isUuid, json, serverError } from '@/lib/http';
import { receiveSingleImage, removePhotoFile, storagePathFor, writePhotoFile } from '@/lib/photo-store';
import { FILE_TOO_LARGE_MESSAGE, STATUS_LABELS } from '@/lib/rules';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type BatchRow = { id: string; site_id: number; site_code: string; declared_count: number; received: number };

const BATCH_FULL = 'จำนวนรูปเกินจำนวนที่แจ้งไว้ตอนเริ่มอัปโหลด';

export async function POST(req: NextRequest, ctx: { params: Promise<{ batchId: string }> }) {
  try {
    const a = await requireAccess(req, 'upload.add_photo');
    if (a.res) return a.res;
    const user = a.user;
    const { batchId } = await ctx.params;
    if (!isUuid(batchId)) return deny(404);

    // upload.add_photo is supervisor-only, so the scope is always the user's own site.
    const scope = siteScope(user);
    if (scope === null) return deny(403);
    const found = await pool().query<BatchRow>(
      `SELECT b.id, b.site_id, s.code AS site_code, b.declared_count,
              (SELECT count(*)::int FROM photos p
                WHERE p.batch_id = b.id AND p.site_id = b.site_id) AS received
         FROM upload_batches b JOIN sites s ON s.id = b.site_id
        WHERE b.id = $1 AND b.site_id = $2 AND b.uploaded_by = $3`,
      [batchId, scope, user.id],
    );
    const batch = found.rows[0];
    if (!batch) return deny(404);
    const d = canAccess(user, 'upload.add_photo', batch.site_id);
    if (!d.ok) return deny(d.status);
    if (batch.received >= batch.declared_count) return apiError(422, 'BATCH_FULL', BATCH_FULL);

    // Type and size are checked on the bytes actually received; nothing is stored yet.
    const got = await receiveSingleImage(req.body, req.headers.get('content-type'));
    if (!got.ok) {
      switch (got.reason) {
        case 'TOO_LARGE':
          return apiError(413, 'FILE_TOO_LARGE', FILE_TOO_LARGE_MESSAGE);
        case 'UNSUPPORTED_TYPE':
          return apiError(415, 'UNSUPPORTED_TYPE', 'รับเฉพาะไฟล์ JPG และ PNG');
        case 'NO_FILE':
          return apiError(400, 'NO_FILE', 'ไม่พบไฟล์รูปในคำขอ');
        case 'MULTIPLE_FILES':
          return apiError(400, 'ONE_FILE_PER_REQUEST', 'ส่งได้คำขอละ 1 ไฟล์ ไม่มีไฟล์ใดในคำขอนี้ถูกเก็บ');
        default:
          return apiError(400, 'BAD_REQUEST', 'รูปแบบคำขอไม่ถูกต้อง (ใช้ multipart/form-data)');
      }
    }
    const file = got.file;

    const photoId = randomUUID();
    const uploadDate = todayBangkok(); // server clock, Asia/Bangkok (FR-04)
    const storagePath = storagePathFor(batch.site_code, uploadDate, photoId, file.kind.ext);

    const client = await pool().connect();
    let fileWritten = false;
    let committed = false;
    try {
      await client.query('BEGIN');
      const locked = await client.query<{ declared_count: number }>(
        `SELECT declared_count FROM upload_batches
          WHERE id = $1 AND site_id = $2 AND uploaded_by = $3 FOR UPDATE`,
        [batch.id, scope, user.id],
      );
      if (!locked.rows[0]) {
        await client.query('ROLLBACK');
        return deny(404);
      }
      const cnt = await client.query<{ n: number }>(
        `SELECT count(*)::int AS n FROM photos WHERE batch_id = $1 AND site_id = $2`,
        [batch.id, scope],
      );
      if (cnt.rows[0].n >= locked.rows[0].declared_count) {
        await client.query('ROLLBACK');
        return apiError(422, 'BATCH_FULL', BATCH_FULL);
      }
      // D-01: the original is stored durably, then the row is inserted, then 201.
      await writePhotoFile(storagePath, file.data);
      fileWritten = true;
      await client.query(
        `INSERT INTO photos (id, batch_id, site_id, uploaded_by, upload_date, original_filename,
                             mime, size_bytes, sha256, storage_path, status, dispatch_state)
         VALUES ($1, $2, $3, $4, $5::date, $6, $7, $8, $9, $10, 'QUEUED', 'PENDING')`,
        [
          photoId,
          batch.id,
          batch.site_id,
          user.id,
          uploadDate,
          file.filename,
          file.kind.mime,
          file.size,
          file.sha256,
          storagePath,
        ],
      );
      await client.query('COMMIT');
      committed = true;
    } catch (e) {
      try {
        await client.query('ROLLBACK');
      } catch {
        /* ignore */
      }
      throw e;
    } finally {
      client.release();
      if (fileWritten && !committed) await removePhotoFile(storagePath);
    }

    return json(
      {
        id: photoId,
        batch_id: batch.id,
        original_filename: file.filename,
        mime: file.kind.mime,
        size_bytes: file.size,
        sha256: file.sha256,
        upload_date: uploadDate,
        status: 'QUEUED',
        status_label: STATUS_LABELS.QUEUED,
      },
      201,
    );
  } catch (e) {
    return serverError('uploads/photos POST', e);
  }
}
