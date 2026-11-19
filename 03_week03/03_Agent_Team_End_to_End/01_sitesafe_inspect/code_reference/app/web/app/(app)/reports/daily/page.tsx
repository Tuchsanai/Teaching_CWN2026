// /reports/daily — daily report per site, computed live (FR-15–FR-17, BR-04, BR-07).
// Server Component: the values, red flag, pass-rate text and ready label all come
// from lib/report + lib/rules (the same code as GET /api/reports/daily); this page
// holds no threshold of its own.
import Link from 'next/link';
import Forbidden from '@/components/Forbidden';
import { can, requireUser } from '@/components/server/session';
import { siteScope } from '@/lib/access';
import { now, todayBangkok } from '@/lib/clock';
import { dailyReport } from '@/lib/report';
import { addDays, isValidDateString } from '@/lib/rules';

export const dynamic = 'force-dynamic';

export default async function DailyReportPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const user = await requireUser();
  if (!can(user, 'report.view') || !can(user, 'report.view', siteScope(user))) return <Forbidden />;

  const sp = await searchParams;
  const asked = typeof sp.date === 'string' ? sp.date : '';
  const badDate = asked !== '' && !isValidDateString(asked);
  const date = asked !== '' && !badDate ? asked : todayBangkok();
  const report = await dailyReport(user, date, now());

  return (
    <>
      <h1>รายงานรายวัน</h1>
      <form className="card filters" method="get" action="/reports/daily">
        <Link className="button secondary" href={`/reports/daily?date=${addDays(date, -1)}`} data-testid="report-prev-day">
          ← วันก่อนหน้า
        </Link>
        <label>
          วันที่
          <input type="date" name="date" defaultValue={date} data-testid="report-date" key={date} />
        </label>
        <button type="submit" data-testid="report-apply">
          ดูรายงาน
        </button>
        <Link className="button secondary" href={`/reports/daily?date=${addDays(date, 1)}`} data-testid="report-next-day">
          วันถัดไป →
        </Link>
        <span
          className={`badge ${report.ready ? 'ready' : 'intraday'}`}
          data-testid="report-ready-badge"
          data-ready={report.ready ? 'true' : 'false'}
          style={{ marginLeft: 'auto', fontSize: 15 }}
        >
          {report.ready_label}
        </span>
      </form>
      {badDate && (
        <p className="error" role="alert" data-testid="report-error">
          วันที่ต้องอยู่ในรูปแบบ YYYY-MM-DD จึงแสดงรายงานของวันนี้แทน
        </p>
      )}

      <p className="muted">
        รายงานของวันที่ <strong data-testid="report-shown-date">{report.date}</strong> คำนวณจากข้อมูลล่าสุดทุกครั้งที่เปิดหน้า
      </p>

      <table className="data">
        <thead>
          <tr>
            <th>ไซต์</th>
            <th className="num">จำนวนรูปที่ถ่าย</th>
            <th className="num">จำนวนรูปไม่ผ่าน</th>
            <th className="num">จำนวนคนไม่ใส่หมวก</th>
            <th className="num">อัตราผ่าน (%)</th>
            <th>สถานะไซต์</th>
            <th className="num">รูปที่ถูกแก้ผล</th>
            <th className="num">รูปที่ตรวจไม่สำเร็จ</th>
          </tr>
        </thead>
        <tbody>
          {report.sites.map((s) => {
            const code = s.site.code;
            return (
              <tr
                key={code}
                className={s.red ? 'red' : undefined}
                data-testid={`report-row-${code}`}
                data-red={s.red ? 'true' : 'false'}
              >
                <td>
                  <strong>{s.site.name}</strong> <span className="muted">({code})</span>
                </td>
                <td className="num" data-testid={`report-taken-${code}`}>{s.taken}</td>
                <td className="num" data-testid={`report-fail-${code}`}>{s.fail}</td>
                <td className="num" data-testid={`report-h-${code}`}>{s.h_total}</td>
                <td className="num" data-testid={`report-rate-${code}`} data-rate={s.pass_rate === null ? '' : String(s.pass_rate)}>
                  {s.pass_rate_text}
                </td>
                <td data-testid={`report-red-${code}`} data-red={s.red ? 'true' : 'false'}>
                  {s.red ? <span className="badge red">ต่ำกว่าเกณฑ์</span> : <span className="muted">ปกติ</span>}
                </td>
                <td className="num" data-testid={`report-edited-${code}`}>{s.edited}</td>
                <td className="num" data-testid={`report-failed-${code}`}>{s.failed}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}
