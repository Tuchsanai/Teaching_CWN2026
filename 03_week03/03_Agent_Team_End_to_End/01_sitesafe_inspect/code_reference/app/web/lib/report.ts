/**
 * Daily report per site, computed live from photos on every request (D-09, DESIGN §9.2).
 * Thresholds and formulas come from lib/rules only.
 */
import type { SessionUser } from './auth';
import { siteCondition } from './access';
import { pool } from './db';
import {
  REPORT_INTRADAY_LABEL,
  REPORT_READY_LABEL,
  formatPassRate,
  isRed,
  isReportReady,
  passRate,
} from './rules';

type AggRow = {
  site_id: number;
  site_code: string;
  site_name: string;
  taken: number;
  with_result: number;
  pass: number;
  warn: number;
  fail: number;
  h_total: number;
  edited: number;
  failed: number;
  queued: number;
  processing: number;
};

export const NO_DATA_LABEL = 'ไม่มีข้อมูล';
export const NO_RESULT_LABEL = 'ยังไม่มีผล';

export function siteReport(r: AggRow) {
  const rate = passRate(r.pass, r.with_result);
  const rateText = formatPassRate(r.pass, r.with_result);
  return {
    site: { id: r.site_id, code: r.site_code, name: r.site_name },
    has_data: r.taken > 0,
    taken: r.taken,
    with_result: r.with_result,
    pass: r.pass,
    warn: r.warn,
    fail: r.fail,
    h_total: r.h_total,
    edited: r.edited,
    failed: r.failed,
    pending: r.queued + r.processing,
    pass_rate: rate,
    pass_rate_text: r.taken === 0 ? NO_DATA_LABEL : rateText === null ? NO_RESULT_LABEL : rateText,
    red: isRed(r.pass, r.with_result),
  };
}

export async function dailyReport(user: SessionUser, date: string, now: Date) {
  const params: unknown[] = [date];
  // supervisor: own site only, on both the photos counted and the site rows returned
  const photoSite = siteCondition(user, 'p.site_id', params);
  const siteWhere = photoSite ? `WHERE s.id = $${params.length}` : '';
  const r = await pool().query<AggRow>(
    `SELECT s.id AS site_id, s.code AS site_code, s.name AS site_name,
            count(p.id)::int AS taken,
            (count(p.id) FILTER (WHERE p.status = 'DONE'))::int AS with_result,
            (count(p.id) FILTER (WHERE p.status = 'DONE' AND p.current_result = 'PASS'))::int AS pass,
            (count(p.id) FILTER (WHERE p.status = 'DONE' AND p.current_result = 'WARN'))::int AS warn,
            (count(p.id) FILTER (WHERE p.status = 'DONE' AND p.current_result = 'FAIL'))::int AS fail,
            (COALESCE(sum(p.model_h) FILTER (WHERE p.status = 'DONE'), 0))::int AS h_total,
            (count(p.id) FILTER (WHERE p.is_overridden))::int AS edited,
            (count(p.id) FILTER (WHERE p.status = 'FAILED'))::int AS failed,
            (count(p.id) FILTER (WHERE p.status = 'QUEUED'))::int AS queued,
            (count(p.id) FILTER (WHERE p.status = 'PROCESSING'))::int AS processing
       FROM sites s
       LEFT JOIN photos p ON p.site_id = s.id AND p.upload_date = $1::date${photoSite}
       ${siteWhere}
      GROUP BY s.id, s.code, s.name
      ORDER BY s.code`,
    params,
  );
  const ready = isReportReady(now, date);
  return {
    date,
    ready,
    ready_label: ready ? REPORT_READY_LABEL : REPORT_INTRADAY_LABEL,
    sites: r.rows.map(siteReport),
  };
}
