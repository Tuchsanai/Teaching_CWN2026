// 5 · POST /api/uploads — supervisor: open an upload of {"count": n} (FR-01, BR-06)
import type { NextRequest } from 'next/server';
import { canAccess, deny, requireAccess } from '@/lib/access';
import { pool } from '@/lib/db';
import { apiError, isRecord, json, readJson, serverError } from '@/lib/http';
import {
  TOO_FEW_PHOTOS_MESSAGE,
  TOO_MANY_PHOTOS_MESSAGE,
  checkPhotoCount,
  uploadLimits,
} from '@/lib/rules';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const a = await requireAccess(req, 'upload.create');
    if (a.res) return a.res;
    const user = a.user;
    // site_id comes from the account, never from the request (FR-04)
    const d = canAccess(user, 'upload.create', user.site_id);
    if (!d.ok) return deny(d.status);

    const body = await readJson(req);
    if (!isRecord(body)) return apiError(400, 'BAD_REQUEST', 'รูปแบบคำขอไม่ถูกต้อง');
    const count = body.count;
    if (typeof count !== 'number' || !Number.isSafeInteger(count)) {
      return apiError(422, 'INVALID_COUNT', 'จำนวนรูปต้องเป็นจำนวนเต็ม');
    }
    // BR-06 is decided here, before any file is received
    const check = checkPhotoCount(count);
    if (check === 'TOO_FEW') return apiError(422, 'TOO_FEW_PHOTOS', TOO_FEW_PHOTOS_MESSAGE);
    if (check === 'TOO_MANY') return apiError(422, 'TOO_MANY_PHOTOS', TOO_MANY_PHOTOS_MESSAGE);

    const r = await pool().query<{ id: string; created_at: Date }>(
      `INSERT INTO upload_batches (site_id, uploaded_by, declared_count)
       VALUES ($1, $2, $3) RETURNING id, created_at`,
      [user.site_id, user.id, count],
    );
    const b = r.rows[0];
    return json(
      {
        batch_id: b.id,
        declared_count: count,
        site: { id: user.site_id, code: user.site_code, name: user.site_name },
        created_at: b.created_at,
        upload_url: `/api/uploads/${b.id}/photos`,
        limits: uploadLimits(),
      },
      201,
    );
  } catch (e) {
    return serverError('uploads POST', e);
  }
}
