import Link from "next/link";
import { AdminQueue } from "@/components/AdminQueue.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { clock } from "@/lib/clock.ts";
import { flags } from "@/lib/flags.ts";
import { t } from "@/lib/i18n.ts";
import { addDays } from "@/lib/rules/time.ts";
import { getLang } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

export default async function AdminPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const lang = await getLang();
  const session = await getSession();
  if (!session || session.role !== "owner") {
    return (
      <div className="card">
        <p className="alert alert-error" data-testid="admin-forbidden">
          {t(lang, session ? "err.FORBIDDEN" : "err.LOGIN_REQUIRED")}
        </p>
        <Link className="btn" href="/login?next=/admin" data-testid="admin-login">
          {t(lang, "nav.login")}
        </Link>
      </div>
    );
  }
  const sp = await searchParams;
  const { today } = await clock();
  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "admin.title")}</h1>
      </div>
      <AdminQueue initialDate={sp.date ?? addDays(today, 1)} today={today} allowReset={flags.allowTestReset} />
    </>
  );
}
