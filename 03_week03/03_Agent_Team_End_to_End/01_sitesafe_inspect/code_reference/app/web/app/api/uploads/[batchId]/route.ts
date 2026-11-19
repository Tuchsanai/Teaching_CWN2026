// 7 · GET /api/uploads/{batchId} — status and result of every photo in the batch (FR-06, FR-10)
import type { NextRequest } from 'next/server';
import { canAccess, deny, requireAccess, siteCondition } from '@/lib/access';
import { pool } from '@/lib/db';
import { isUuid, json, serverError } from '@/lib/http';
import { PHOTO_COLUMNS, photoView, type PhotoRow } from '@/lib/views';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type BatchRow = {
  id: string;
  site_id: number;
  site_code: string;
  site_name: string;
  declared_count: number;
  created_at: Date;
  uploaded_by: number;
  uploader_name: string;
};

export async function GET(req: NextRequest, ctx: { params: Promise<{ batchId: string }> }) {
  try {
    const a = await requireAccess(req, 'upload.view');
    if (a.res) return a.res;
    const user = a.user;
    const { batchId } = await ctx.params;
    if (!isUuid(batchId)) return deny(404);

    const params: unknown[] = [batchId];
    const where = `b.id = $1${siteCondition(user, 'b.site_id', params)}`;
    const br = await pool().query<BatchRow>(
      `SELECT b.id, b.site_id, s.code AS site_code, s.name AS site_name, b.declared_count, b.created_at,
              b.uploaded_by, u.full_name AS uploader_name
         FROM upload_batches b JOIN sites s ON s.id = b.site_id JOIN users u ON u.id = b.uploaded_by
        WHERE ${where}`,
      params,
    );
    const b = br.rows[0];
    if (!b) return deny(404);
    const d = canAccess(user, 'upload.view', b.site_id);
    if (!d.ok) return deny(d.status);

    const pParams: unknown[] = [b.id, b.site_id];
    const pSite = siteCondition(user, 'p.site_id', pParams);
    const pr = await pool().query<PhotoRow>(
      `SELECT ${PHOTO_COLUMNS}
         FROM photos p JOIN sites s ON s.id = p.site_id
        WHERE p.batch_id = $1 AND p.site_id = $2${pSite}
        ORDER BY p.accepted_at, p.id`,
      pParams,
    );
    const photos = pr.rows.map(photoView);
    const counts = { queued: 0, processing: 0, done: 0, failed: 0 };
    for (const p of photos) {
      if (p.status === 'QUEUED') counts.queued += 1;
      else if (p.status === 'PROCESSING') counts.processing += 1;
      else if (p.status === 'DONE') counts.done += 1;
      else counts.failed += 1;
    }
    return json({
      batch: {
        id: b.id,
        site: { id: b.site_id, code: b.site_code, name: b.site_name },
        declared_count: b.declared_count,
        created_at: b.created_at,
        uploaded_by: { id: b.uploaded_by, full_name: b.uploader_name },
      },
      accepted_count: photos.length,
      counts,
      photos,
    });
  } catch (e) {
    return serverError('uploads GET', e);
  }
}
