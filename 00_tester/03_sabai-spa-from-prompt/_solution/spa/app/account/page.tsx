"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, useApp, useReady, type Member } from "@/components/AppProvider";
import { Icon } from "@/components/Ornament";
import { Loader, PageHead } from "@/components/Shared";
import { errorText, type DictKey, type Lang } from "@/lib/i18n";
import { formatBaht, formatDate } from "@/lib/time";
import { GOLD_MIN, PLATINUM_MIN } from "@/lib/rules";

type Bk = {
  id: number; code: string; service: string; serviceName: Record<Lang, string>; image: string; kind: string; people: number; date: string; time: string; endTime: string;
  status: string; past: boolean; canCancel: boolean; therapists: { id: number; th: string; en: string; zh: string }[]; total: number; due: number; paidByCourse: boolean;
};
type Account = { member: Member; upcoming: Bk[]; history: Bk[]; cancelled: Bk[]; waist: { date: string; cm: number }[]; waistDrop: number; photos: { id: number; date: string; kind: string; image: string }[] };

function WaistChart({ data, lang }: { data: { date: string; cm: number }[]; lang: Lang }) {
  const W = 560, H = 240, P = { l: 44, r: 20, t: 24, b: 40 };
  const min = Math.floor(Math.min(...data.map((d) => d.cm)) - 1);
  const max = Math.ceil(Math.max(...data.map((d) => d.cm)) + 1);
  const x = (i: number) => P.l + (data.length === 1 ? 0 : (i / (data.length - 1)) * (W - P.l - P.r));
  const y = (v: number) => P.t + ((max - v) / (max - min)) * (H - P.t - P.b);
  const path = data.map((d, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(d.cm).toFixed(1)}`).join(" ");
  const area = `${path} L${x(data.length - 1)},${H - P.b} L${x(0)},${H - P.b} Z`;
  const ticks = [min, (min + max) / 2, max];
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={data.map((d) => `${d.date}: ${d.cm} cm`).join(", ")} data-testid="waist-chart">
      <defs>
        <linearGradient id="waistFill" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#2F5D3A" stopOpacity="0.25" />
          <stop offset="100%" stopColor="#2F5D3A" stopOpacity="0" />
        </linearGradient>
      </defs>
      {ticks.map((v) => (
        <g key={v}>
          <line className="grid-line" x1={P.l} x2={W - P.r} y1={y(v)} y2={y(v)} />
          <text className="axis-label" x={P.l - 8} y={y(v) + 4} textAnchor="end">{v.toFixed(0)}</text>
        </g>
      ))}
      <path className="area" d={area} />
      <path className="line" d={path} />
      {data.map((d, i) => (
        <g key={d.date} data-testid={`waist-point-${i}`} data-cm={d.cm} data-date={d.date}>
          <circle className="dot" cx={x(i)} cy={y(d.cm)} r={6} />
          <text className="val" x={x(i)} y={y(d.cm) - 12} textAnchor="middle">{d.cm.toFixed(1)}</text>
          <text className="axis-label" x={x(i)} y={H - 14} textAnchor="middle">{formatDate(d.date, lang).replace(/\s?\d{4}$/, "")}</text>
        </g>
      ))}
    </svg>
  );
}

export default function AccountPage() {
  const { t, lang, user, userLoaded, refreshUser } = useApp();
  const [data, setData] = useState<Account | null>(null);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(async () => {
    const r = await api<Account & { ok: boolean }>("/api/account");
    if (r.ok) setData(r);
  }, []);
  useEffect(() => {
    if (user) load();
  }, [user, load]);
  useReady(userLoaded && (!user || !!data));

  if (!userLoaded) return <Loader />;
  if (!user) {
    return (
      <>
        <PageHead title={t("account_title")} />
        <section className="section">
          <div className="container--narrow center">
            <p className="alert alert--info" data-testid="account-need-login">{t("need_login")}</p>
            <Link href="/login?next=/account" className="btn btn--gold mt-1">{t("nav_login")}</Link>
          </div>
        </section>
      </>
    );
  }
  if (!data) return <Loader />;
  const m = data.member;
  const name = lang === "th" ? m.name : m.nameEn;

  const cancel = async (b: Bk) => {
    setMsg(null);
    setBusyId(b.id);
    const r = await api<{ ok: boolean; error?: string }>(`/api/bookings/${b.id}/cancel`, { method: "POST" });
    setBusyId(null);
    if (r.ok) {
      setMsg({ ok: true, text: t("account_cancel_ok") });
      await load();
      refreshUser();
    } else setMsg({ ok: false, text: errorText(lang, r.error ?? "SERVER") });
  };

  const progressPct = m.tier === "platinum" ? 100 : m.tier === "gold" ? ((m.totalSpent - GOLD_MIN) / (PLATINUM_MIN - GOLD_MIN)) * 100 : (m.totalSpent / GOLD_MIN) * 100;
  const birthMonthName = new Intl.DateTimeFormat(lang === "th" ? "th-TH" : lang === "zh" ? "zh-CN" : "en-GB", { month: "long", timeZone: "UTC" }).format(new Date(Date.UTC(2024, m.birthMonth - 1, 1)));
  const ther = (b: Bk) => b.therapists.map((x) => x[lang]).join(", ");

  return (
    <>
      <PageHead eyebrow={t("account_title")} title={t("account_hello", { name })} />
      <section className="section" style={{ paddingTop: 40 }}>
        <div className="container">
          <div className="stat-grid">
            <div className="stat">
              <div className="stat__label">{t("account_tier")}</div>
              <div className="mt-1"><span className={`tier-badge tier-badge--${m.tier}`} data-testid="member-tier" data-tier={m.tier}>{t(`tier_${m.tier}` as DictKey)}</span></div>
              <p className="small muted mt-1" style={{ marginBottom: 0 }}>{t("account_tier_pct", { pct: m.tierPct })}</p>
            </div>
            <div className="stat">
              <div className="stat__label">{t("account_points")}</div>
              <div className="stat__value" data-testid="member-points">{m.points.toLocaleString("en-US")}</div>
            </div>
            <div className="stat">
              <div className="stat__label">{t("account_spent")}</div>
              <div className="stat__value" data-testid="member-spent">{formatBaht(m.totalSpent)}</div>
            </div>
          </div>

          <div className="card card--pad mt-2">
            <div className="progress" aria-hidden="true"><i style={{ width: `${Math.max(2, Math.min(100, progressPct))}%` }} /></div>
            <p style={{ margin: 0, fontWeight: 600 }} data-testid="member-next-tier">
              {m.nextTier ? t("account_next", { amount: formatBaht(m.nextTierNeed), tier: t(`tier_${m.nextTier}` as DictKey) }) : t("account_top")}
            </p>
            <p className="small muted" style={{ margin: "6px 0 0" }} data-testid="member-birthday" data-status={m.birthday}>
              <Icon name="gift" size={15} /> {m.birthday === "eligible" ? t("account_birthday_yes") : m.birthday === "used" ? t("account_birthday_used") : t("account_birthday_no", { month: birthMonthName })}
            </p>
          </div>

          <h2 className="mt-3">{t("account_upcoming")}</h2>
          {msg && <p className={`alert ${msg.ok ? "alert--ok" : "alert--error"}`} role="alert" data-testid={msg.ok ? "cancel-success" : "cancel-error"}>{msg.text}</p>}
          {data.upcoming.length === 0 ? (
            <p className="muted" data-testid="no-upcoming">{t("account_no_upcoming")}</p>
          ) : (
            <div className="grid" style={{ gap: 12 }} data-testid="upcoming-list">
              {data.upcoming.map((b) => (
                <div key={b.id} className="appt" data-testid={`booking-item-${b.code}`}>
                  <img src={b.image} alt={b.serviceName[lang]} />
                  <div>
                    <h3>{b.serviceName[lang]}</h3>
                    <p className="appt__meta" style={{ margin: 0 }}>
                      <Icon name="calendar" size={15} /> {formatDate(b.date, lang, true)} · {b.time}–{b.endTime} · {t("people_n", { n: b.people })}
                    </p>
                    <p className="appt__meta" style={{ margin: 0 }}>{t("therapist_col")}: {ther(b)} · {b.code}</p>
                  </div>
                  <div className="appt__actions">
                    <button type="button" className="btn btn--ghost btn--sm" disabled={!b.canCancel || busyId === b.id} onClick={() => cancel(b)} data-testid={`cancel-btn-${b.code}`}>
                      {t("account_cancel")}
                    </button>
                    {!b.canCancel && <p className="hint" style={{ margin: "6px 0 0", maxWidth: 260 }} data-testid={`cancel-blocked-${b.code}`}>{t("account_cancel_blocked")}</p>}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="split mt-3" style={{ alignItems: "start" }}>
            <div>
              <h2>{t("account_waist")}</h2>
              {data.waist.length ? (
                <div className="card card--pad">
                  <WaistChart data={data.waist} lang={lang} />
                  <p className="center" style={{ margin: "8px 0 0", fontWeight: 700, color: "var(--ok)" }} data-testid="waist-drop" data-cm={data.waistDrop}>
                    {t("account_waist_drop", { n: data.waistDrop })}
                  </p>
                </div>
              ) : (
                <p className="muted">{t("account_no_waist")}</p>
              )}
            </div>
            <div>
              <h2>{t("account_photos")}</h2>
              {data.photos.length ? (
                <div className="card card--pad">
                  <div className="photo-pair" data-testid="body-photos">
                    {data.photos.map((p) => (
                      <figure key={p.id} data-testid={`photo-${p.kind}`}>
                        <img src={p.image} alt={`${t(p.kind === "before" ? "before" : "after")} — ${formatDate(p.date, lang)}`} style={p.kind === "before" ? { filter: "saturate(0.85) brightness(0.96)" } : undefined} />
                        <figcaption>{t(p.kind === "before" ? "before" : "after")} · {formatDate(p.date, lang)}</figcaption>
                      </figure>
                    ))}
                  </div>
                  <p className="hint mt-1" style={{ marginBottom: 0 }}>{t("account_photos_note")}</p>
                </div>
              ) : (
                <p className="muted">{t("account_photos_note")}</p>
              )}
            </div>
          </div>

          <h2 className="mt-3">{t("account_history")}</h2>
          {data.history.length === 0 ? (
            <p className="muted">{t("account_no_history")}</p>
          ) : (
            <div className="table-wrap">
              <table className="table" data-testid="history-list">
                <thead>
                  <tr><th>{t("date_col")}</th><th>{t("service_col")}</th><th>{t("therapist_col")}</th></tr>
                </thead>
                <tbody>
                  {data.history.map((b, i) => (
                    <tr key={b.id} data-testid={`history-row-${i}`} data-date={b.date}>
                      <td>{formatDate(b.date, lang)}</td>
                      <td>{b.serviceName[lang]}</td>
                      <td>{ther(b)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="row mt-3">
            <Link href="/wallet" className="btn btn--green" data-testid="account-wallet">{t("nav_wallet")}</Link>
            <Link href="/book" className="btn btn--gold">{t("nav_book")}</Link>
          </div>
        </div>
      </section>
    </>
  );
}
