// 9 · GET /api/photos/{id} — H, V, boxes, model result, latest result (FR-07, FR-08)
import type { NextRequest } from 'next/server';
import { canAccess, deny, requireAccess, siteCondition } from '@/lib/access';
import { pool } from '@/lib/db';
import { json, serverError } from '@/lib/http';
import { findPhotoInScope } from '@/lib/photo-query';
import { DETECTION_LABELS, photoView } from '@/lib/views';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  try {
    const a = await requireAccess(req, 'photo.view');
    if (a.res) return a.res;
    const user = a.user;
    const { id } = await ctx.params;

    const photo = await findPhotoInScope(user, id);
    if (!photo) return deny(404);
    const d = canAccess(user, 'photo.view', photo.site_id);
    if (!d.ok) return deny(d.status);

    const detParams: unknown[] = [photo.id];
    const detSite = siteCondition(user, 'p.site_id', detParams);
    const det = await pool().query<{
      id: string; cls: string; confidence: string; x1: number; y1: number; x2: number; y2: number;
    }>(
      `SELECT d.id, d.cls, d.confidence, d.x1, d.y1, d.x2, d.y2
         FROM detections d JOIN photos p ON p.id = d.photo_id
        WHERE d.photo_id = $1${detSite}
        ORDER BY d.id`,
      detParams,
    );
    const ovParams: unknown[] = [photo.id];
    const ovSite = siteCondition(user, 'p.site_id', ovParams);
    const ov = await pool().query<{ n: number }>(
      `SELECT count(*)::int AS n
         FROM result_overrides o JOIN photos p ON p.id = o.photo_id
        WHERE o.photo_id = $1${ovSite}`,
      ovParams,
    );
    return json({
      photo: {
        ...photoView(photo),
        detections: det.rows.map((r) => ({
          id: Number(r.id),
          cls: r.cls,
          label: DETECTION_LABELS[r.cls] ?? r.cls,
          confidence: Number(r.confidence),
          box: [r.x1, r.y1, r.x2, r.y2],
        })),
        override_count: ov.rows[0].n,
        can_override: canAccess(user, 'photo.override', photo.site_id).ok && photo.status === 'DONE',
        can_view_history: canAccess(user, 'override.history', photo.site_id).ok,
      },
    });
  } catch (e) {
    return serverError('photos/{id} GET', e);
  }
}
