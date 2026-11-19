// 13 · GET /api/reports/daily?date= — manager + executive: all 3 sites · supervisor: own site
//      Computed live on every request (FR-15–FR-17, BR-04, BR-07)
import type { NextRequest } from 'next/server';
import { canAccess, deny, requireAccess, siteScope } from '@/lib/access';
import { now, nowIso, todayBangkok } from '@/lib/clock';
import { apiError, json, serverError } from '@/lib/http';
import { dailyReport } from '@/lib/report';
import { isValidDateString } from '@/lib/rules';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    const a = await requireAccess(req, 'report.view');
    if (a.res) return a.res;
    const d = canAccess(a.user, 'report.view', siteScope(a.user));
    if (!d.ok) return deny(d.status);
    const date = req.nextUrl.searchParams.get('date') || todayBangkok();
    if (!isValidDateString(date)) return apiError(400, 'BAD_REQUEST', 'วันที่ต้องอยู่ในรูปแบบ YYYY-MM-DD');
    const report = await dailyReport(a.user, date, now());
    return json({ ...report, now: nowIso() });
  } catch (e) {
    return serverError('reports/daily GET', e);
  }
}
