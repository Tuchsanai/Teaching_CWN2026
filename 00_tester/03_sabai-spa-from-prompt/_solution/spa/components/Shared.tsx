"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, useApp } from "./AppProvider";
import { Icon } from "./Ornament";
import { pick, type DictKey, type Lang } from "@/lib/i18n";
import { addDays, formatBaht, formatMonthYear, weekdayShort } from "@/lib/time";
import type { Quote } from "@/lib/rules";

export type Service = {
  slug: string; sort: number; category: string; duration: number; price: number; herbs: string[]; image: string; is_package: boolean;
  name_th: string; name_en: string; name_zh: string; desc_th: string; desc_en: string; desc_zh: string;
};

export const HERB_IMG: Record<string, string> = {
  plai: "/assets/herbs/plai.png",
  turmeric: "/assets/herbs/turmeric.png",
  lemongrass: "/assets/herbs/lemongrass.png",
  "kaffir-lime": "/assets/herbs/kaffir-lime.png",
  thanaka: "/assets/herbs/thanaka.png",
  "aloe-vera": "/assets/herbs/aloe-vera.png",
};
export const HERBS = Object.keys(HERB_IMG);

let servicesCache: Service[] | null = null;
export function useServices() {
  const [list, setList] = useState<Service[] | null>(servicesCache);
  useEffect(() => {
    let alive = true;
    api<{ ok: boolean; services: Service[] }>("/api/services").then((r) => {
      if (alive && r.ok) {
        servicesCache = r.services;
        setList(r.services);
      }
    });
    return () => {
      alive = false;
    };
  }, []);
  return list;
}

export function svcName(s: Service, lang: Lang) {
  return pick(s, "name", lang);
}

export function HerbPills({ herbs, testid }: { herbs: string[]; testid?: string }) {
  const { t } = useApp();
  return (
    <ul className="herb-list" data-testid={testid} aria-label={t("herbs_used")}>
      {herbs.map((h) => (
        <li key={h} className="herb-pill" data-herb={h}>
          <img src={HERB_IMG[h]} alt={t(`herb_${h}` as DictKey)} width={26} height={26} loading="lazy" />
          {t(`herb_${h}` as DictKey)}
        </li>
      ))}
    </ul>
  );
}

export function ServiceCard({ s, showHerbs = true }: { s: Service; showHerbs?: boolean }) {
  const { t, lang } = useApp();
  return (
    <article className="card card--hover svc-card" data-testid={`service-card-${s.slug}`}>
      <div className="svc-card__media">
        <img src={s.image} alt={svcName(s, lang)} loading="lazy" width={600} height={400} />
        <span className="svc-card__tag">{t(`cat_${s.category}` as DictKey)}</span>
        <span className="svc-card__price" data-testid={`service-price-${s.slug}`}>
          {formatBaht(s.price)}
          {s.is_package ? t("per_person") : ""}
        </span>
      </div>
      <div className="svc-card__body">
        <h3>{svcName(s, lang)}</h3>
        <div className="svc-card__meta">
          <span data-testid={`service-duration-${s.slug}`}>
            <Icon name="clock" size={16} /> {t("minutes", { n: s.duration })}
          </span>
        </div>
        <p>{pick(s, "desc", lang)}</p>
        {showHerbs && <HerbPills herbs={s.herbs} testid={`service-herbs-${s.slug}`} />}
        <div className="svc-card__actions">
          <Link href={`/book?service=${s.slug}`} className="btn btn--green btn--sm" data-testid={`service-book-${s.slug}`}>
            {t("book_now")}
          </Link>
          <Link href={s.is_package ? "/packages/bangkok-relax" : `/services/${s.slug}`} className="btn btn--ghost btn--sm" data-testid={`service-detail-${s.slug}`}>
            {t("details")}
          </Link>
        </div>
      </div>
    </article>
  );
}

export function AllergyWarning({ testid = "allergy-warning" }: { testid?: string }) {
  const { t } = useApp();
  return (
    <p className="allergy" role="note" data-testid={testid}>
      <Icon name="leaf" size={18} />
      <span>{t("allergy_warning")}</span>
    </p>
  );
}

/** FR-03: only tomorrow … +30 days can be picked (BR-05) */
export function Calendar({ today, min, max, value, onChange }: { today: string; min: string; max: string; value: string | null; onChange: (d: string) => void }) {
  const { lang, t } = useApp();
  const start = value ?? min;
  const [ym, setYm] = useState<[number, number]>([Number(start.slice(0, 4)), Number(start.slice(5, 7))]);
  useEffect(() => {
    setYm([Number(start.slice(0, 4)), Number(start.slice(5, 7))]);
    // reset the visible month when the bookable range changes (e.g. "now" was locked)
  }, [min]);
  const [y, m] = ym;
  const first = `${y}-${String(m).padStart(2, "0")}-01`;
  const firstDow = new Date(first + "T00:00:00Z").getUTCDay();
  const daysInMonth = new Date(Date.UTC(y, m, 0)).getUTCDate();
  const cells: (string | null)[] = [];
  for (let i = 0; i < firstDow; i++) cells.push(null);
  for (let d = 0; d < daysInMonth; d++) cells.push(addDays(first, d));
  const prevMonthLast = addDays(first, -1);
  const nextMonthFirst = addDays(first, daysInMonth);
  const move = (dir: -1 | 1) => {
    const d = dir === -1 ? prevMonthLast : nextMonthFirst;
    setYm([Number(d.slice(0, 4)), Number(d.slice(5, 7))]);
  };
  return (
    <div className="calendar" data-testid="calendar">
      <div className="calendar__head">
        <button type="button" className="icon-btn" onClick={() => move(-1)} disabled={prevMonthLast < min} aria-label="previous month" data-testid="cal-prev">
          <Icon name="left" />
        </button>
        <span className="calendar__title" data-testid="cal-month" aria-live="polite">{formatMonthYear(y, m, lang)}</span>
        <button type="button" className="icon-btn" onClick={() => move(1)} disabled={nextMonthFirst > max} aria-label="next month" data-testid="cal-next">
          <Icon name="right" />
        </button>
      </div>
      <div className="calendar__grid" role="grid" aria-label={t("step_2")}>
        {weekdayShort(lang).map((d, i) => (
          <span key={i} className="calendar__dow" aria-hidden="true">{d}</span>
        ))}
        {cells.map((d, i) =>
          d === null ? (
            <span key={`e${i}`} className="calendar__day is-empty" />
          ) : (
            <button
              key={d}
              type="button"
              className={`calendar__day ${d === value ? "is-selected" : ""} ${d === today ? "is-today" : ""}`}
              disabled={d < min || d > max}
              aria-pressed={d === value}
              aria-label={d}
              onClick={() => onChange(d)}
              data-testid={`cal-day-${d}`}
              data-date={d}
            >
              {Number(d.slice(8))}
            </button>
          ),
        )}
      </div>
    </div>
  );
}

export function PriceSummary({ q, member, loading }: { q: Quote | null; member: boolean; loading?: boolean }) {
  const { t } = useApp();
  if (!q) return null;
  const neg = (n: number) => (n > 0 ? formatBaht(-n) : formatBaht(0));
  const tierLabel = q.tier ? `${t("price_tier")} (${t(`tier_${q.tier}` as DictKey)} ${q.tierPct}%)` : t("price_tier");
  return (
    <section className="card price-box" aria-busy={loading} data-testid="price-summary">
      <h2>{t("price_title")}</h2>
      <ul className="price-lines">
        <li>
          <span>{t("price_subtotal")} ({formatBaht(q.unitPrice)} × {q.people})</span>
          <b data-testid="price-subtotal">{formatBaht(q.subtotal)}</b>
        </li>
        <li className={q.groupDiscount ? "discount" : "is-zero"}>
          <span>{t("price_group")}</span>
          <b data-testid="price-group-discount">{neg(q.groupDiscount)}</b>
        </li>
        <li className={q.tierDiscount ? "discount" : "is-zero"}>
          <span>{tierLabel}</span>
          <b data-testid="price-tier-discount">{neg(q.tierDiscount)}</b>
        </li>
        <li className={q.birthdayDiscount ? "discount" : "is-zero"}>
          <span>{t("price_birthday")}</span>
          <b data-testid="price-birthday-discount">{neg(q.birthdayDiscount)}</b>
        </li>
        <li className={q.pointsDiscount ? "discount" : "is-zero"}>
          <span>
            {t("price_points")} ({t("price_points_detail", { n: q.pointsUsed })})
          </span>
          <b data-testid="price-points-discount">{neg(q.pointsDiscount)}</b>
        </li>
        {q.courseCovered > 0 && (
          <li className="discount">
            <span>{t("price_course")}</span>
            <b data-testid="price-course">{neg(q.courseCovered)}</b>
          </li>
        )}
        <li className={q.transportFee ? "" : "is-zero"}>
          <span>
            {t("price_transport")}
            {q.transportRequested && q.distanceKm !== null ? ` (${t("km_n", { n: q.distanceKm.toFixed(1) })} · ${t("cars_n", { n: q.cars })})` : ""}
          </span>
          <b data-testid="price-transport">
            {!q.transportRequested ? t("price_transport_none") : q.transportOk ? (q.transportFee === 0 ? t("free") : formatBaht(q.transportFee)) : "—"}
          </b>
        </li>
        <li className="total">
          <span>{t("price_total")}</span>
          <b data-testid="price-total">{formatBaht(q.total)}</b>
        </li>
        {q.giftUsed > 0 && (
          <li className="discount">
            <span>{t("price_gift")}</span>
            <b data-testid="price-gift">{neg(q.giftUsed)}</b>
          </li>
        )}
        <li className="due">
          <span>{t("price_due")}</span>
          <b data-testid="price-due">{formatBaht(q.due)}</b>
        </li>
        <li className="earn">
          <span>{member ? t("price_earn") : t("price_earn_guest")}</span>
          <b data-testid="price-points-earn">{member ? `+${q.pointsEarned}` : "0"}</b>
        </li>
      </ul>
    </section>
  );
}

export function PageHead({ eyebrow, title, lead, image }: { eyebrow?: string; title: string; lead?: string; image?: string }) {
  return (
    <header className="page-head">
      {image && (
        <div className="page-head__img" aria-hidden="true">
          <img src={image} alt={title} />
        </div>
      )}
      <div className="container">
        {eyebrow && <p className="eyebrow anim-up">{eyebrow}</p>}
        <h1 className="anim-up d1">{title}</h1>
        {lead && <p className="anim-up d2">{lead}</p>}
      </div>
    </header>
  );
}

export function Loader() {
  const { t } = useApp();
  return <div className="loader" role="status">{t("loading")}</div>;
}
