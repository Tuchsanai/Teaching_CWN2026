import Link from "next/link";
import { MyBookings } from "@/components/MyBookings.tsx";
import { Lotus } from "@/components/ThaiOrnament.tsx";
import { clock } from "@/lib/clock.ts";
import { getPool } from "@/lib/db.ts";
import { t } from "@/lib/i18n.ts";
import { formatBaht } from "@/lib/money.ts";
import { accountSummary, myBookings } from "@/lib/server/customer.ts";
import { getLang } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** บัญชี: ระดับ (FR-11) แต้ม (FR-09) เดือนเกิด (FR-12) นัด/ยกเลิก/ประวัติ (FR-07, FR-17) · ไม่มีช่องอัปโหลดรูป (FR-35) */
export default async function AccountPage() {
  const lang = await getLang();
  const session = await getSession();
  if (!session) {
    return (
      <div className="card">
        <p>{t(lang, "common.loginFirst")}</p>
        <Link className="btn" href="/login?next=/account" data-testid="account-login">
          {t(lang, "nav.login")}
        </Link>
      </div>
    );
  }
  const { now, today } = await clock();
  const me = await accountSummary(getPool(), session.uid, today, lang);
  if (!me) return <p>{t(lang, "err.NOT_FOUND")}</p>;
  const bookings = await myBookings(getPool(), session.uid, now, lang);

  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1 data-testid="account-hello">{t(lang, "account.hello", { name: me.name })}</h1>
      </div>
      <div className="stat-row">
        <div className="stat" data-testid="account-tier-card">
          <div className="muted">{t(lang, "account.tier")}</div>
          <div className="value" data-testid="account-tier" data-tier={me.tier}>
            {me.tierLabel}
          </div>
          <div className="small" data-testid="account-tier-pct">
            {t(lang, "account.tierPct", { p: me.tierPct })}
          </div>
          <div className="small muted" data-testid="account-spend" data-amount={me.lifetimeSpend}>
            {t(lang, "account.spend", { s: formatBaht(Math.round(me.lifetimeSpend * 100)) })}
          </div>
          <div className="small" data-testid="account-tier-message">
            {me.tierMessage}
          </div>
        </div>
        <div className="stat">
          <div className="muted">{t(lang, "account.points")}</div>
          <div className="value" data-testid="account-points" data-points={me.points}>
            {t(lang, "account.pointsUnit", { p: me.points })}
          </div>
        </div>
        <div className="stat">
          <div className="muted">{t(lang, "nav.wallet")}</div>
          <Link className="btn btn-sm" href="/wallet" data-testid="account-wallet-link">
            {t(lang, "account.wallet")}
          </Link>
        </div>
      </div>
      {me.birthdayThisMonth !== "none" && (
        <p className={`alert ${me.birthdayThisMonth === "available" ? "alert-ok" : "alert-info"}`} data-testid="account-birthday" data-state={me.birthdayThisMonth}>
          {me.birthdayThisMonth === "available" ? t(lang, "account.birthdayOn") : t(lang, "account.birthdayUsed")}
        </p>
      )}
      <h2 style={{ marginTop: 24 }}>{t(lang, "account.bookings")}</h2>
      <MyBookings items={bookings} />
    </>
  );
}
