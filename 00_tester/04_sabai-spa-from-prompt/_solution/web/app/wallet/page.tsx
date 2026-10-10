import Link from "next/link";
import { BuyCourseButton } from "@/components/BuyCourseButton.tsx";
import { GoldDivider, Lotus } from "@/components/ThaiOrnament.tsx";
import { WaistChart } from "@/components/WaistChart.tsx";
import { clock } from "@/lib/clock.ts";
import { getPool } from "@/lib/db.ts";
import { t } from "@/lib/i18n.ts";
import { wallet } from "@/lib/server/customer.ts";
import { getLang } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** Wallet (FR-15) · กราฟรอบเอว (FR-16) · รูป before/after เฉพาะเจ้าของ (FR-18) · ซื้อคอร์ส (FR-13) */
export default async function WalletPage() {
  const lang = await getLang();
  const session = await getSession();
  if (!session) {
    return (
      <div className="card">
        <p>{t(lang, "common.loginFirst")}</p>
        <Link className="btn" href="/login?next=/wallet" data-testid="wallet-login">
          {t(lang, "nav.login")}
        </Link>
      </div>
    );
  }
  const { today } = await clock();
  const w = await wallet(getPool(), session.uid, today, lang);

  return (
    <>
      <div className="page-head">
        <Lotus className="orn" size={40} />
        <h1>{t(lang, "wallet.title")}</h1>
      </div>
      {w.courses.length === 0 && <p className="muted" data-testid="wallet-empty">{t(lang, "wallet.none")}</p>}
      <div className="grid">
        {w.courses.map((c) => (
          <article key={c.id} className="card" data-testid={`course-${c.code}`} data-remaining={c.remaining} data-expired={c.expired}>
            <h2 style={{ fontSize: "1.2rem" }}>
              {c.code} · {t(lang, "services.course")}
            </h2>
            <p className="price" data-testid={`course-remaining-${c.code}`}>
              {c.remainingLabel}
            </p>
            <p data-testid={`course-expires-${c.code}`}>{t(lang, "wallet.expires", { d: c.expiresLabel })}</p>
            {c.expired ? (
              <p className="badge bad" data-testid={`course-expired-${c.code}`}>
                {t(lang, "wallet.expired")}
              </p>
            ) : (
              <p className="badge ok" data-testid={`course-days-${c.code}`} data-days={c.daysLeft}>
                {t(lang, "wallet.daysLeft", { n: c.daysLeft })}
              </p>
            )}
            <div style={{ marginTop: 10 }}>
              {c.usable ? (
                <Link className="btn btn-sm" href={`/book?type=course&service=K01`} data-testid={`course-book-${c.code}`}>
                  {t(lang, "wallet.book")}
                </Link>
              ) : (
                <button type="button" className="btn btn-sm" disabled data-testid={`course-book-${c.code}`}>
                  {t(lang, "wallet.book")}
                </button>
              )}
            </div>
          </article>
        ))}
      </div>

      <GoldDivider />
      <h2>{t(lang, "wallet.waist")}</h2>
      {w.waist.length ? (
        <div className="card">
          <WaistChart points={w.waist} lang={lang} title={t(lang, "wallet.waist")} />
          <p className="price" data-testid="waist-reduced" data-cm={w.waistReducedCm.toFixed(1)}>
            {t(lang, "wallet.reduced", { x: w.waistReducedCm.toFixed(1) })}
          </p>
        </div>
      ) : (
        <p className="muted" data-testid="waist-empty">{t(lang, "wallet.noWaist")}</p>
      )}

      {w.photos.length > 0 && (
        <>
          <GoldDivider />
          <h2>{t(lang, "wallet.photos")}</h2>
          <div className="card photo-pair" data-testid="body-photos">
            {w.photos.map((p) => (
              <figure key={p.id}>
                <img src={p.url} alt={p.phase === "before" ? t(lang, "wallet.before") : t(lang, "wallet.after")} data-testid={`body-photo-${p.phase}`} />
                <figcaption>{p.phase === "before" ? t(lang, "wallet.before") : t(lang, "wallet.after")}</figcaption>
              </figure>
            ))}
          </div>
        </>
      )}

      <GoldDivider />
      <BuyCourseButton />
    </>
  );
}
