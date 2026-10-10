import Link from "next/link";
import { MoodPicker } from "@/components/MoodPicker.tsx";
import { GoldDivider, Lotus, Orchid } from "@/components/ThaiOrnament.tsx";
import { asset, serviceImage } from "@/lib/assets.ts";
import { formatBaht } from "@/lib/money.ts";
import { t } from "@/lib/i18n.ts";
import { listServices } from "@/lib/server/catalog.ts";
import { getLang } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

export default async function Home() {
  const lang = await getLang();
  let services: Awaited<ReturnType<typeof listServices>> = [];
  try {
    services = await listServices(lang);
  } catch {
    services = [];
  }
  const featured = services.filter((s) => ["S01", "S04", "P01"].includes(s.code));

  return (
    <>
      <section className="hero" data-testid="home-hero">
        <img className="hero-bg" src={asset("hero")} alt="" />
        <div className="hero-text">
          <div className="ornament-row">
            <Orchid size={40} className="sway" />
            <Lotus size={40} />
            <Orchid size={40} className="sway" />
          </div>
          <h1 data-testid="home-title">{t(lang, "home.title")}</h1>
          <p>{t(lang, "home.subtitle")}</p>
          <div className="btn-row">
            <Link className="btn btn-gold" href="/book" data-testid="home-book">
              {t(lang, "home.ctaBook")}
            </Link>
            <Link className="btn" href="/package" data-testid="home-package">
              {t(lang, "home.ctaPackage")}
            </Link>
          </div>
        </div>
      </section>

      <GoldDivider />
      <MoodPicker />

      <GoldDivider />
      <h2>{t(lang, "home.featured")}</h2>
      <div className="grid">
        {featured.map((s) => (
          <article key={s.code} className="card svc-card" data-testid={`home-svc-${s.code}`}>
            <img src={serviceImage(s.code)} alt={s.name} loading="lazy" />
            <div className="body">
              <h3>{s.name}</h3>
              <div className="price">
                {formatBaht(s.priceSatang)} <span className="muted small">{t(lang, "common.perPerson")}</span>
              </div>
              <ul className="chips" aria-label={t(lang, "common.herbs")}>
                {s.herbs.map((h) => (
                  <li key={h}>{h}</li>
                ))}
              </ul>
              <Link className="btn btn-sm" href={s.code === "P01" ? "/package" : `/book?service=${s.code}`} data-testid={`home-book-${s.code}`}>
                {t(lang, "common.bookNow")}
              </Link>
            </div>
          </article>
        ))}
      </div>

      <section className="thai-band">
        <h2>{t(lang, "home.explore")}</h2>
        <div className="btn-row">
          <Link className="btn btn-ghost" href="/quiz" data-testid="home-quiz">
            {t(lang, "home.quizCta")}
          </Link>
          <Link className="btn btn-ghost" href="/skin" data-testid="home-skin">
            {t(lang, "home.skinCta")}
          </Link>
          <Link className="btn btn-ghost" href="/chat" data-testid="home-chat">
            {t(lang, "home.chatCta")}
          </Link>
        </div>
      </section>
    </>
  );
}
