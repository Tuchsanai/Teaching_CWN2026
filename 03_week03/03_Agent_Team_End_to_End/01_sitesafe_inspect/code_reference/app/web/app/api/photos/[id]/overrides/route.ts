// 11 · POST /api/photos/{id}/overrides — manager: all sites · supervisor: own site (FR-13)
// 12 · GET  /api/photos/{id}/overrides — history ordered by time (FR-14, NFR-07)
// Append-only: adds a result_overrides row and updates current_result / is_overridden.
// model_result is never written here. There is no PUT/PATCH/DELETE (→ 405).
import type { NextRequest } from 'next/server';
import { canAccess, deny, requireAccess, siteCondition } from '@/lib/access';
import { pool, withTransaction } from '@/lib/db';
import { apiError, isRecord, json, readJson, serverError } from '@/lib/http';
import { findPhotoInScope } from '@/lib/photo-query';
import { RESULTS, RESULT_LABELS, type Result } from '@/lib/rules';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const MAX_REASON_LENGTH = 1000;

type OverrideRow = {
  id: string;
  photo_id: string;
  edited_by: number;
  editor_name: string;
  edited_at: Date;
  result_before: Result;
  result_after: Result;
  reason: string;
};

function overrideView(r: OverrideRow) {
  return {
    id: Number(r.id),
    photo_id: r.photo_id,
    edited_by: { id: r.edited_by, full_name: r.editor_name },
    edited_at: r.edited_at,
    result_before: r.result_before,
    result_before_label: RESULT_LABELS[r.result_before],
    result_after: r.result_after,
    result_after_label: RESULT_LABELS[r.result_after],
    reason: r.reason,
  };
}

type Outcome =
  | { kind: 'not_found' }
  | { kind: 'denied'; status: 401 | 403 | 404 }
  | { kind: 'invalid'; error: string; message: string }
  | { kind: 'ok'; row: OverrideRow; current: Result };

export async function POST(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  try {
    const a = await requireAccess(req, 'photo.override');
    if (a.res) return a.res;
    const user = a.user;
    const { id } = await ctx.params;

    // Site check before reading the body: another site's photo is simply "not found".
    const pre = await findPhotoInScope(user, id);
    if (!pre) return deny(404);
    const d = canAccess(user, 'photo.override', pre.site_id);
    if (!d.ok) return deny(d.status);

    const body = await readJson(req);
    if (!isRecord(body)) return apiError(400, 'BAD_REQUEST', 'รูปแบบคำขอไม่ถูกต้อง');
    const result = typeof body.result === 'string' ? body.result.toUpperCase() : '';
    if (!RESULTS.includes(result as Result)) {
      return apiError(422, 'INVALID_RESULT', 'ผลต้องเป็น ผ่าน, เตือน หรือ ไม่ผ่าน');
    }
    const reason = typeof body.reason === 'string' ? body.reason.trim() : '';
    if (reason === '') return apiError(422, 'REASON_REQUIRED', 'ต้องใส่เหตุผลของการแก้ผล');
    if (reason.length > MAX_REASON_LENGTH) {
      return apiError(422, 'REASON_TOO_LONG', `เหตุผลยาวได้ไม่เกิน ${MAX_REASON_LENGTH} ตัวอักษร`);
    }

    const out = await withTransaction<Outcome>(async (c) => {
      const photo = await findPhotoInScope(user, id, { client: c, forUpdate: true });
      if (!photo) return { kind: 'not_found' };
      const dd = canAccess(user, 'photo.override', photo.site_id);
      if (!dd.ok) return { kind: 'denied', status: dd.status };
      if (photo.status !== 'DONE' || photo.current_result === null) {
        return { kind: 'invalid', error: 'NOT_DONE', message: 'แก้ผลได้เฉพาะรูปที่ตรวจเสร็จแล้ว' };
      }
      if (photo.current_result === result) {
        return { kind: 'invalid', error: 'SAME_RESULT', message: 'ผลใหม่ต้องต่างจากผลล่าสุด' };
      }
      // Both statements repeat the site condition: the row is only added / updated
      // when the photo is DONE, still has the result shown as "before", and is in scope.
      const insParams: unknown[] = [photo.id, user.id, photo.current_result, result, reason];
      const insSite = siteCondition(user, 'p.site_id', insParams);
      const ins = await c.query<OverrideRow>(
        `WITH o AS (
           INSERT INTO result_overrides (photo_id, edited_by, result_before, result_after, reason)
           SELECT p.id, $2::int, $3::text, $4::text, $5::text
             FROM photos p
            WHERE p.id = $1::uuid AND p.status = 'DONE' AND p.current_result = $3::text${insSite}
           RETURNING id, photo_id, edited_by, edited_at, result_before, result_after, reason
         )
         SELECT o.*, u.full_name AS editor_name FROM o JOIN users u ON u.id = o.edited_by`,
        insParams,
      );
      if (ins.rowCount !== 1) throw new Error('override insert did not match the photo');
      // model_result is never part of this statement (FR-14).
      const updParams: unknown[] = [photo.id, result, photo.current_result];
      const updSite = siteCondition(user, 'site_id', updParams);
      const upd = await c.query(
        `UPDATE photos SET current_result = $2, is_overridden = true
          WHERE id = $1 AND status = 'DONE' AND current_result = $3${updSite}`,
        updParams,
      );
      if (upd.rowCount !== 1) throw new Error('override update did not match the photo');
      return { kind: 'ok', row: ins.rows[0], current: result as Result };
    });

    if (out.kind === 'not_found') return deny(404);
    if (out.kind === 'denied') return deny(out.status);
    if (out.kind === 'invalid') return apiError(422, out.error, out.message);
    return json(
      {
        override: overrideView(out.row),
        photo: {
          id: pre.id,
          model_result: pre.model_result,
          current_result: out.current,
          current_result_label: RESULT_LABELS[out.current],
          is_overridden: true,
        },
      },
      201,
    );
  } catch (e) {
    return serverError('photos/{id}/overrides POST', e);
  }
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  try {
    const a = await requireAccess(req, 'override.history');
    if (a.res) return a.res;
    const user = a.user;
    const { id } = await ctx.params;

    const photo = await findPhotoInScope(user, id);
    if (!photo) return deny(404);
    const d = canAccess(user, 'override.history', photo.site_id);
    if (!d.ok) return deny(d.status);

    const params: unknown[] = [photo.id];
    const site = siteCondition(user, 'p.site_id', params);
    const r = await pool().query<OverrideRow>(
      `SELECT o.id, o.photo_id, o.edited_by, u.full_name AS editor_name, o.edited_at,
              o.result_before, o.result_after, o.reason
         FROM result_overrides o
         JOIN photos p ON p.id = o.photo_id
         JOIN users u ON u.id = o.edited_by
        WHERE o.photo_id = $1${site}
        ORDER BY o.edited_at, o.id`,
      params,
    );
    return json({
      photo_id: photo.id,
      model_result: photo.model_result,
      current_result: photo.current_result,
      overrides: r.rows.map(overrideView),
    });
  } catch (e) {
    return serverError('photos/{id}/overrides GET', e);
  }
}
