"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, useApp, useReady } from "@/components/AppProvider";
import { Reveal } from "@/components/Reveal";
import { Icon, KranokCorner, Stars, ThaiDivider, PrajamYam } from "@/components/Ornament";
import { HERB_IMG, HERBS, ServiceCard, svcName, useServices } from "@/components/Shared";
import { MOODS, MOOD_IMAGES, recommendForMood, type Mood } from "@/lib/recommend";
import { pick, type DictKey } from "@/lib/i18n";
import { formatBaht } from "@/lib/time";

type Ther = { id: number; image: string; name_th: string; name_en: string; name_zh: string; title_th: string; title_en: string; title_zh: string; rating: number | null; review_count: number };

export default function HomePage() {
  const { t, lang } = useApp();
  const services = useServices();
  const [ther, setTher] = useState<Ther[] | null>(null);
  const [mood, setMood] = useState<Mood | null>(null);

  useEffect(() => {
    api<{ ok: boolean; therapists: Ther[] }>("/api/therapists").then((r) => r.ok && setTher(r.therapists));
  }, []);
  useReady(!!services && !!ther);

  const bySlug = (slug: string) => services?.find((s) => s.slug === slug);
  const signature = (services ?? []).filter((s) => !s.is_package).slice(0, 6);
  const pkg = bySlug("bangkok-relax");

  return (
    <>
      {/* ---------- HERO ---------- */}
      <section className="hero" data-testid="hero" aria-labelledby="hero-title">
        <div className="hero__img">
          <img src="/assets/brand/hero.jpg" alt={t("brandSub")} fetchPriority="high" />
        </div>
        <div className="hero__frame" aria-hidden="true">
          <KranokCorner className="kc kc--tl" />
          <KranokCorner className="kc kc--tr" />
          <KranokCorner className="kc kc--bl" />
          <KranokCorner className="kc kc--br" />
        </div>
        <div className="container hero__content">
          <p className="hero__eyebrow anim-up">
            <PrajamYam size={16} /> {t("home_eyebrow")}
          </p>
          <h1 id="hero-title" className="anim-up d1">
            {t("home_title_1")}
            <span className="gold">{t("home_title_2")}</span>
          </h1>
          <p className="hero__lead anim-up d2">{t("home_lead")}</p>
          <div className="hero__ctas anim-up d3">
            <Link href="/book" className="btn btn--gold btn--lg" data-testid="hero-book">
              {t("home_cta_book")} <Icon name="arrow" />
            </Link>
            <Link href="/services" className="btn btn--light btn--lg" data-testid="hero-explore">
              {t("home_cta_explore")}
            </Link>
          </div>
          <div className="hero__stats anim-up d4">
            <div className="hero__stat"><b>6</b><span>{t("home_stat_therapists")}</span></div>
            <div className="hero__stat"><b>6</b><span>{t("home_stat_herbs")}</span></div>
            <div className="hero__stat"><b>5.0</b><span>{t("home_stat_rating")}</span></div>
            <div className="hero__stat"><b>12</b><span>{t("home_stat_hours")}</span></div>
          </div>
        </div>
        <div className="hero__scroll" aria-hidden="true">
          <span>{t("home_scroll")}</span>
          <i />
        </div>
      </section>

      {/* ---------- SIGNATURE ---------- */}
      <section className="section" aria-labelledby="sig-title">
        <div className="container">
          <Reveal className="section-head">
            <p className="eyebrow">{t("home_sig_eyebrow")}</p>
            <h2 id="sig-title">{t("home_sig_title")}</h2>
            <ThaiDivider />
            <p>{t("home_sig_lead")}</p>
          </Reveal>
          <div className="grid grid--3">
            {signature.map((s, i) => (
              <Reveal key={s.slug} delay={(i % 3) * 80}>
                <ServiceCard s={s} />
              </Reveal>
            ))}
          </div>
          <div className="center mt-3">
            <Link href="/services" className="btn btn--ghost" data-testid="home-all-services">
              {t("view_all")} <Icon name="arrow" />
            </Link>
          </div>
        </div>
      </section>

      {/* ---------- MOOD ---------- */}
      <section className="section section--paper" aria-labelledby="mood-title">
        <div className="container">
          <Reveal className="section-head">
            <p className="eyebrow">{t("home_mood_eyebrow")}</p>
            <h2 id="mood-title">{t("home_mood_title")}</h2>
            <ThaiDivider />
            <p>{t("home_mood_lead")}</p>
          </Reveal>
          <Reveal className="mood-grid" role="group" aria-label={t("mood_title")}>
            {MOODS.map((m) => (
              <button key={m} type="button" className={`mood-btn ${mood === m ? "is-active" : ""}`} aria-pressed={mood === m} onClick={() => setMood(m)} data-testid={`home-mood-${m}`}>
                <img src={MOOD_IMAGES[m]} alt={t(`mood_${m}` as DictKey)} width={120} height={120} loading="lazy" />
                {t(`mood_${m}` as DictKey)}
              </button>
            ))}
          </Reveal>
          {mood && services && (
            <div className="result-panel" data-testid="home-mood-result" key={mood}>
              <h3>{t("mood_result")}</h3>
              <p className="muted">{t(`mood_reason_${mood}` as DictKey)}</p>
              <div className="rec-list">
                {recommendForMood(mood).map((slug) => {
                  const s = bySlug(slug);
                  if (!s) return null;
                  return (
                    <div className="rec" key={slug}>
                      <img src={s.image} alt={svcName(s, lang)} loading="lazy" />
                      <div>
                        <h3>{svcName(s, lang)}</h3>
                        <p>{t("minutes", { n: s.duration })} · {formatBaht(s.price)}</p>
                        <Link href={`/book?service=${s.slug}`} className="btn btn--green btn--sm" data-testid={`home-mood-book-${s.slug}`}>
                          {t("book_now")}
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ---------- PACKAGE ---------- */}
      <section className="section section--green on-dark" aria-labelledby="pkg-title">
        <div className="container split">
          <Reveal className="split__media">
            <img src="/assets/packages/hotel-transfer.jpg" alt={pkg ? svcName(pkg, lang) : "Bangkok Relax"} loading="lazy" />
            <div className="split__badge">
              <b>฿2,900</b>
              <span className="small">{t("per_person")}</span>
            </div>
          </Reveal>
          <Reveal delay={120}>
            <p className="eyebrow">{t("home_pkg_eyebrow")}</p>
            <h2 id="pkg-title">{pkg ? svcName(pkg, lang) : "Bangkok Relax"}</h2>
            <p>{t("home_pkg_lead")}</p>
            <ul className="check-list">
              <li><Icon name="check" /> {t("pkg_inc_1")}</li>
              <li><Icon name="check" /> {t("pkg_inc_2")}</li>
              <li><Icon name="check" /> {t("pkg_inc_3")} — {t("pkg_inc_3_sub")}</li>
            </ul>
            <div className="row">
              <Link href="/packages/bangkok-relax" className="btn btn--gold" data-testid="home-package">
                {t("details")} <Icon name="arrow" />
              </Link>
              <Link href="/book?service=bangkok-relax" className="btn btn--light">{t("book_now")}</Link>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ---------- COUPLE SUITE ---------- */}
      <section className="section" aria-labelledby="couple-title">
        <div className="container split split--rev">
          <Reveal className="split__media">
            <img src="/assets/packages/couple-package.jpg" alt={t("home_couple_title")} loading="lazy" />
            <div className="split__badge">
              <b>360°</b>
              <span className="small">Couple Suite</span>
            </div>
          </Reveal>
          <Reveal delay={120}>
            <p className="eyebrow">{t("home_couple_eyebrow")}</p>
            <h2 id="couple-title">{t("home_couple_title")}</h2>
            <p className="muted">{t("home_couple_lead")}</p>
            <Link href="/rooms/couple-suite" className="btn btn--green" data-testid="home-tour">
              {t("home_couple_cta")} <Icon name="arrow" />
            </Link>
          </Reveal>
        </div>
      </section>

      {/* ---------- HERBS ---------- */}
      <section className="section section--paper" aria-labelledby="herbs-title">
        <div className="container">
          <Reveal className="section-head">
            <p className="eyebrow">{t("home_herbs_eyebrow")}</p>
            <h2 id="herbs-title">{t("home_herbs_title")}</h2>
            <ThaiDivider />
            <p>{t("allergy_warning")}</p>
          </Reveal>
          <div className="herb-grid">
            {HERBS.map((h, i) => (
              <Reveal key={h} className="herb-card" delay={i * 60}>
                <img src={HERB_IMG[h]} alt={t(`herb_${h}` as DictKey)} width={96} height={96} loading="lazy" />
                <h3>{t(`herb_${h}` as DictKey)}</h3>
                <p>{t(`herbdesc_${h}` as DictKey)}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ---------- THERAPISTS ---------- */}
      <section className="section" aria-labelledby="ther-title">
        <div className="container">
          <Reveal className="section-head">
            <p className="eyebrow">{t("home_ther_eyebrow")}</p>
            <h2 id="ther-title">{t("home_ther_title")}</h2>
            <ThaiDivider />
          </Reveal>
          <div className="grid grid--3">
            {(ther ?? []).filter((x) => x.rating !== null).sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0)).slice(0, 3).map((x, i) => (
              <Reveal key={x.id} delay={i * 80}>
                <article className="card card--hover ther-card">
                  <div className="ther-card__media">
                    <img src={x.image} alt={pick(x, "name", lang)} loading="lazy" />
                    <span className="ther-card__score"><Icon name="star" size={16} /> {x.rating?.toFixed(1)}</span>
                  </div>
                  <div className="ther-card__body">
                    <h3>{pick(x, "name", lang)}</h3>
                    <p className="muted small">{pick(x, "title", lang)}</p>
                    <Stars value={x.rating} /> <span className="small muted">{t("ther_reviews", { n: x.review_count })}</span>
                  </div>
                </article>
              </Reveal>
            ))}
          </div>
          <div className="center mt-3">
            <Link href="/therapists" className="btn btn--ghost" data-testid="home-therapists">
              {t("home_ther_cta")} <Icon name="arrow" />
            </Link>
          </div>
        </div>
      </section>

      {/* ---------- TOOLS ---------- */}
      <section className="section section--green on-dark" aria-labelledby="tools-title">
        <div className="container">
          <Reveal className="section-head">
            <p className="eyebrow">{t("home_tools_eyebrow")}</p>
            <h2 id="tools-title">{t("home_tools_title")}</h2>
            <ThaiDivider />
          </Reveal>
          <div className="tools-grid">
            <Reveal><Link href="/quiz" className="tool" data-testid="home-tool-quiz"><span className="tool__icon"><Icon name="spark" /></span><h3>{t("nav_quiz")}</h3><p>{t("home_tool_quiz")}</p><span className="tool__go">{t("next")} <Icon name="arrow" size={18} /></span></Link></Reveal>
            <Reveal delay={80}><Link href="/skin" className="tool" data-testid="home-tool-skin"><span className="tool__icon"><Icon name="shield" /></span><h3>{t("nav_skin")}</h3><p>{t("home_tool_skin")}</p><span className="tool__go">{t("next")} <Icon name="arrow" size={18} /></span></Link></Reveal>
            <Reveal delay={160}><Link href="/mood" className="tool" data-testid="home-tool-mood"><span className="tool__icon"><Icon name="leaf" /></span><h3>{t("nav_mood")}</h3><p>{t("home_mood_lead")}</p><span className="tool__go">{t("next")} <Icon name="arrow" size={18} /></span></Link></Reveal>
            <Reveal delay={240}><div className="tool"><span className="tool__icon"><Icon name="chat" /></span><h3>{t("chat_title")}</h3><p>{t("home_tool_chat")}</p></div></Reveal>
          </div>
        </div>
      </section>

      {/* ---------- GIFT ---------- */}
      <section className="section" aria-labelledby="gift-title">
        <div className="container split">
          <Reveal>
            <div className="giftcard giftcard--gold">
              <img src="/assets/gift/giftcard-gold.jpg" alt={t("design_gold")} loading="lazy" />
              <div className="giftcard__body">
                <span className="giftcard__brand">Sabai Jai Wellness Spa</span>
                <span className="giftcard__amount">฿2,000</span>
                <span className="giftcard__foot"><span>GIFT CARD</span><span>365 days</span></span>
              </div>
            </div>
          </Reveal>
          <Reveal delay={120}>
            <p className="eyebrow">{t("home_gift_eyebrow")}</p>
            <h2 id="gift-title">{t("home_gift_title")}</h2>
            <p className="muted">{t("home_gift_lead")}</p>
            <Link href="/gift-cards" className="btn btn--gold" data-testid="home-gift">
              <Icon name="gift" /> {t("home_gift_cta")}
            </Link>
          </Reveal>
        </div>
      </section>

      {/* ---------- MEMBERSHIP ---------- */}
      <section className="section section--green on-dark" aria-labelledby="member-title">
        <div className="container">
          <Reveal className="section-head">
            <p className="eyebrow">{t("home_member_eyebrow")}</p>
            <h2 id="member-title">{t("home_member_title")}</h2>
            <ThaiDivider />
            <p>{t("home_member_lead")}</p>
          </Reveal>
          <div className="tier-cards">
            {(["silver", "gold", "platinum"] as const).map((tier, i) => (
              <Reveal key={tier} className="tier-card" delay={i * 80}>
                <span className={`tier-badge tier-badge--${tier}`}>{t(`tier_${tier}` as DictKey)}</span>
                <p>{t(`tier_rule_${tier}` as DictKey)}</p>
              </Reveal>
            ))}
          </div>
          <div className="center mt-3">
            <Link href="/login" className="btn btn--gold" data-testid="home-member">{t("home_member_cta")}</Link>
          </div>
        </div>
      </section>
    </>
  );
}

