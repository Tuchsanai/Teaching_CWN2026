import Link from "next/link";
import { AdminReport } from "@/components/AdminReport.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { clock } from "@/lib/clock.ts";
import { t } from "@/lib/i18n.ts";
import { addDays, isDateString } from "@/lib/rules/time.ts";
import { getLang } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** CR-05 รายงานยอด (owner เท่านั้น · ตรวจสิทธิ์แบบเดียวกับ /admin) · ช่วงเริ่มต้น = เดือนของ "วันนี้" จาก clock() */
export default async function AdminReportPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const lang = await getLang();
  const session = await getSession();
  if (!session || session.role !== "owner") {
    return (
      <div className="card">
        <p className="alert alert-error" data-testid="admin-forbidden">
          {t(lang, session ? "err.FORBIDDEN" : "err.LOGIN_REQUIRED")}
        </p>
        <Link className="btn" href="/login?next=/admin/report" data-testid="admin-login">
          {t(lang, "nav.login")}
        </Link>
      </div>
    );
  }
  const sp = await searchParams;
  const { today } = await clock();
  const monthStart = `${today.slice(0, 7)}-01`;
  const monthEnd = addDays(`${addDays(monthStart, 31).slice(0, 7)}-01`, -1);
  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "report.title")}</h1>
      </div>
      <AdminReport initialFrom={isDateString(sp.from) ? sp.from : monthStart} initialTo={isDateString(sp.to) ? sp.to : monthEnd} />
    </>
  );
}
