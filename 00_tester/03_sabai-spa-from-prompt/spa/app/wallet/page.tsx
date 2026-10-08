"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, useApp, useReady } from "@/components/AppProvider";
import { Icon } from "@/components/Ornament";
import { Loader, PageHead } from "@/components/Shared";
import { errorText, type DictKey } from "@/lib/i18n";
import { formatBaht, formatDate } from "@/lib/time";

type Course = { id: number; total: number; used: number; left: number; purchasedOn: string; expiresOn: string; expired: boolean };
type Gift = { code: string; amount: number; balance: number; design: string; channel: string; recipient: string; purchased_on: string; expires_on: string; expired: boolean };
type Wallet = { courses: Course[]; canBookWithCourse: boolean; courseProblem: string | null; giftCards: Gift[] };

export default function WalletPage() {
  const { t, lang, user, userLoaded } = useApp();
  const [w, setW] = useState<Wallet | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const r = await api<Wallet & { ok: boolean }>("/api/wallet");
    if (r.ok) setW(r);
  }, []);
  useEffect(() => {
    if (user) load();
  }, [user, load]);
  useReady(userLoaded && (!user || !!w));

  if (!userLoaded) return <Loader />;
  if (!user) {
    return (
      <>
        <PageHead title={t("wallet_title")} />
        <section className="section">
          <div className="container--narrow center">
            <p className="alert alert--info" data-testid="wallet-need-login">{t("need_login")}</p>
            <Link href="/login?next=/wallet" className="btn btn--gold mt-1">{t("nav_login")}</Link>
          </div>
        </section>
      </>
    );
  }
  if (!w) return <Loader />;

  const buy = async () => {
    setBusy(true);
    setMsg(null);
    const r = await api<{ ok: boolean; course?: Course; error?: string }>("/api/courses", { method: "POST" });
    setBusy(false);
    if (r.ok && r.course) {
      setMsg(t("wallet_buy_ok", { date: formatDate(r.course.expiresOn, lang) }));
      load();
    } else setMsg(errorText(lang, r.error ?? "SERVER"));
  };

  const active = w.courses.find((c) => !c.expired && c.left > 0) ?? w.courses.find((c) => !c.expired) ?? w.courses[0];

  return (
    <>
      <PageHead eyebrow={t("nav_wallet")} title={t("wallet_title")} image="/assets/treatments/body-contouring.jpg" />
      <section className="section" style={{ paddingTop: 40 }}>
        <div className="container">
          <div className="split" style={{ alignItems: "start" }}>
            <div className="card card--pad" data-testid="course-card">
              <p className="eyebrow">{t("wallet_course")}</p>
              {active ? (
                <>
                  <p className="stat__value" data-testid="course-remaining" data-left={active.left} data-total={active.total}>
                    {t("wallet_remaining", { left: active.left, total: active.total })}
                  </p>
                  <div className="progress" aria-hidden="true"><i style={{ width: `${(active.left / active.total) * 100}%` }} /></div>
                  <p className="muted" style={{ margin: 0 }}>
                    {t("wallet_purchased", { date: formatDate(active.purchasedOn, lang) })} ·{" "}
                    <b data-testid="course-expires" data-date={active.expiresOn}>{t("wallet_expires", { date: formatDate(active.expiresOn, lang) })}</b>
                  </p>
                  {active.expired && <p className="alert alert--error mt-1" data-testid="course-expired">{t("wallet_expired")}</p>}
                </>
              ) : (
                <p className="muted" data-testid="course-none">{t("wallet_no_course")}</p>
              )}
              <div className="row mt-2">
                {w.canBookWithCourse ? (
                  <Link href="/book?service=body-contouring&pay=course" className="btn btn--gold" data-testid="course-book">
                    {t("wallet_book_course")} <Icon name="arrow" />
                  </Link>
                ) : (
                  <button type="button" className="btn btn--gold" disabled data-testid="course-book">{t("wallet_book_course")}</button>
                )}
              </div>
              {!w.canBookWithCourse && w.courseProblem && <p className="hint mt-1" data-testid="course-problem">{errorText(lang, w.courseProblem)}</p>}
              <hr style={{ border: 0, borderTop: "1px dashed var(--line)", margin: "24px 0" }} />
              <p className="small muted">{t("wallet_course_rule")}</p>
              <button type="button" className="btn btn--ghost" onClick={buy} disabled={busy} data-testid="course-buy">{t("wallet_buy_course")}</button>
              {msg && <p className="alert alert--ok mt-1" data-testid="course-buy-result">{msg}</p>}
            </div>

            <div>
              <h2>{t("wallet_gifts")}</h2>
              {w.giftCards.length === 0 ? (
                <p className="muted">{t("wallet_no_gifts")}</p>
              ) : (
                <div className="grid" style={{ gap: 12 }} data-testid="wallet-gifts">
                  {w.giftCards.map((g) => (
                    <div key={g.code} className="appt" data-testid={`wallet-gift-${g.code}`}>
                      <img src={`/assets/gift/giftcard-${g.design}.jpg`} alt={t(`design_${g.design}` as DictKey)} />
                      <div>
                        <h3>{g.code}</h3>
                        <p className="appt__meta" style={{ margin: 0 }}>{t("gift_balance")} {formatBaht(g.balance)} / {formatBaht(g.amount)}</p>
                        <p className="appt__meta" style={{ margin: 0 }}>{g.expired ? errorText(lang, "GIFT_EXPIRED") : t("gift_valid_until", { date: formatDate(g.expires_on, lang) })}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <Link href="/gift-cards" className="btn btn--green mt-2"><Icon name="gift" /> {t("home_gift_cta")}</Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
