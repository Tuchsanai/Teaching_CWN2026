// 8 · GET /api/photos?date=&site=&result=&status=&problems=1&page=
//     manager: all sites · supervisor: own site only (FR-11, FR-12, FR-20, FR-21)
import type { NextRequest } from 'next/server';
import { canAccess, deny, requireAccess, siteScope } from '@/lib/access';
import { pool } from '@/lib/db';
import { apiError, json, serverError } from '@/lib/http';
import { PHOTO_STATUSES, RESULTS, isValidDateString, type PhotoStatus, type Result } from '@/lib/rules';
import { PHOTO_COLUMNS, photoView, type PhotoRow } from '@/lib/views';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const PAGE_SIZE = 24;

export async function GET(req: NextRequest) {
  try {
    const a = await requireAccess(req, 'photo.view');
    if (a.res) return a.res;
    const user = a.user;
    const q = req.nextUrl.searchParams;

    const date = q.get('date') || null;
    if (date !== null && !isValidDateString(date)) return apiError(400, 'BAD_REQUEST', 'วันที่ต้องอยู่ในรูปแบบ YYYY-MM-DD');
    const result = (q.get('result') || '').toUpperCase() || null;
    if (result !== null && !RESULTS.includes(result as Result)) return apiError(400, 'BAD_REQUEST', 'ผลต้องเป็น PASS, WARN หรือ FAIL');
    const status = (q.get('status') || '').toUpperCase() || null;
    if (status !== null && !PHOTO_STATUSES.includes(status as PhotoStatus)) {
      return apiError(400, 'BAD_REQUEST', 'สถานะไม่ถูกต้อง');
    }
    const problems = q.get('problems') === '1' || q.get('problems') === 'true';
    const pageRaw = q.get('page');
    const page = pageRaw === null || pageRaw === '' ? 1 : Number(pageRaw);
    if (!Number.isSafeInteger(page) || page < 1) return apiError(400, 'BAD_REQUEST', 'หน้าไม่ถูกต้อง');

    // Optional site filter (code such as SITE-A, or numeric id)
    let siteFilter: number | null = null;
    const siteParam = q.get('site');
    if (siteParam) {
      const sr = await pool().query<{ id: number }>(
        `SELECT id FROM sites WHERE code = $1 OR id::text = $1`,
        [siteParam],
      );
      if (!sr.rows[0]) return deny(404);
      siteFilter = sr.rows[0].id;
    }
    const d = canAccess(user, 'photo.view', siteFilter);
    if (!d.ok) return deny(d.status);

    const params: unknown[] = [];
    const where: string[] = [];
    const add = (sql: string, v: unknown) => {
      params.push(v);
      where.push(sql.replace('?', `$${params.length}`));
    };
    const scope = siteScope(user);
    if (scope !== null) add('p.site_id = ?', scope); // supervisor: always own site
    if (siteFilter !== null) add('p.site_id = ?', siteFilter);
    if (date !== null) add('p.upload_date = ?::date', date);
    if (status !== null) add('p.status = ?', status);
    if (result !== null) add('p.current_result = ?', result);
    if (problems) where.push(`p.status = 'DONE' AND p.current_result IN ('FAIL', 'WARN')`);
    const whereSql = where.length ? `WHERE ${where.join(' AND ')}` : '';

    const totals = await pool().query<{ total: number; pass: number; warn: number; fail: number }>(
      `SELECT count(*)::int AS total,
              (count(*) FILTER (WHERE p.current_result = 'PASS'))::int AS pass,
              (count(*) FILTER (WHERE p.current_result = 'WARN'))::int AS warn,
              (count(*) FILTER (WHERE p.current_result = 'FAIL'))::int AS fail
         FROM photos p ${whereSql}`,
      params,
    );
    const rows = await pool().query<PhotoRow>(
      `SELECT ${PHOTO_COLUMNS}
         FROM photos p JOIN sites s ON s.id = p.site_id
         ${whereSql}
        ORDER BY p.upload_date DESC, p.accepted_at DESC, p.id
        LIMIT ${PAGE_SIZE} OFFSET ${(page - 1) * PAGE_SIZE}`,
      params,
    );
    const t = totals.rows[0];
    return json({
      page,
      page_size: PAGE_SIZE,
      total: t.total,
      pages: Math.max(1, Math.ceil(t.total / PAGE_SIZE)),
      counts: { pass: t.pass, warn: t.warn, fail: t.fail },
      filters: { date, site: siteParam || null, result, status, problems },
      photos: rows.rows.map(photoView),
    });
  } catch (e) {
    return serverError('photos GET', e);
  }
}
