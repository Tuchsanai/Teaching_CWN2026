"use client";

import Link from "next/link";
import { useState } from "react";
import { useApp, useReady } from "@/components/AppProvider";
import { Icon, ThaiDivider } from "@/components/Ornament";
import { AllergyWarning, HerbPills, Loader, PageHead, svcName, useServices } from "@/components/Shared";
import { transportQuote, PACKAGE_SLUG } from "@/lib/rules";
import { errorText, pick } from "@/lib/i18n";
import { formatBaht } from "@/lib/time";

export default function PackagePage() {
  const { t, lang, config } = useApp();
  const services = useServices();
  const [people, setPeople] = useState(1);
  const [hotelId, setHotelId] = useState<number | null>(null);
  useReady(!!services && !!config);
  const pkg = services?.find((s) => s.slug === PACKAGE_SLUG);
  if (!services || !config || !pkg) return <Loader />;

  const hotel = config.hotels.find((h) => h.id === hotelId) ?? null;
  const tq = hotel ? transportQuote(hotel.distanceKm, people) : null;
  const total = pkg.price * people;

  return (
    <>
      <PageHead eyebrow={t("pkg_eyebrow")} title={svcName(pkg, lang)} lead={t("pkg_lead")} image="/assets/packages/hotel-transfer.jpg" />
      <section className="section">
        <div className="container split">
          <div>
            <div className="split__media">
              <img src="/assets/packages/hotel-transfer.jpg" alt={svcName(pkg, lang)} />
              <div className="split__badge">
                <b data-testid="package-price">{formatBaht(pkg.price)}</b>
                <span className="small">{t("per_person")} · {t("minutes", { n: pkg.duration })}</span>
              </div>
            </div>
            <div className="grid grid--3 mt-2" style={{ gridTemplateColumns: "repeat(3, minmax(0,1fr))", gap: 10 }}>
              <img src="/assets/treatments/thai-massage.jpg" alt={t("pkg_inc_1")} style={{ borderRadius: 14, aspectRatio: "1", objectFit: "cover" }} loading="lazy" />
              <img src="/assets/treatments/herbal-compress.jpg" alt={t("pkg_inc_2")} style={{ borderRadius: 14, aspectRatio: "1", objectFit: "cover" }} loading="lazy" />
              <img src="/assets/packages/hotel-transfer.jpg" alt={t("pkg_inc_3")} style={{ borderRadius: 14, aspectRatio: "1", objectFit: "cover" }} loading="lazy" />
            </div>
          </div>
          <div>
            <h2>{t("service_includes")}</h2>
            <ThaiDivider className="mt-0" />
            <ul className="check-list" data-testid="package-includes">
              <li data-testid="package-inc-thai-massage"><Icon name="check" /> {t("pkg_inc_1")}</li>
              <li data-testid="package-inc-herbal-compress"><Icon name="check" /> {t("pkg_inc_2")}</li>
              <li data-testid="package-inc-transfer"><Icon name="check" /> {t("pkg_inc_3")} <span className="muted small">({t("pkg_inc_3_sub")})</span></li>
            </ul>
            <HerbPills herbs={pkg.herbs} testid="package-herbs" />
            <div className="mt-1"><AllergyWarning /></div>

            <div className="card card--pad mt-2">
              <h3>{t("pkg_calc")}</h3>
              <div className="row row--between">
                <label className="label" htmlFor="pk-people">{t("book_people")}</label>
                <div className="stepper">
                  <button type="button" onClick={() => setPeople((p) => Math.max(1, p - 1))} disabled={people <= 1} aria-label={t("book_people_minus")} data-testid="package-people-minus">−</button>
                  <input id="pk-people" type="number" min={1} max={6} value={people} onChange={(e) => setPeople(Math.min(6, Math.max(1, Math.floor(Number(e.target.value) || 1))))} data-testid="package-people" />
                  <button type="button" onClick={() => setPeople((p) => Math.min(6, p + 1))} disabled={people >= 6} aria-label={t("book_people_plus")} data-testid="package-people-plus">+</button>
                </div>
              </div>
              <ul className="price-lines mt-1">
                <li className="total">
                  <span>{t("pkg_total")}</span>
                  <b data-testid="package-total">{formatBaht(total)}</b>
                </li>
              </ul>
              <div className="field mt-1">
                <label htmlFor="pk-hotel">{t("pkg_transport_calc")}</label>
                <select id="pk-hotel" className="select" value={hotelId ?? ""} onChange={(e) => setHotelId(Number(e.target.value) || null)} data-testid="package-hotel">
                  <option value="">{t("book_hotel_pick")}</option>
                  {config.hotels.map((h) => (
                    <option key={h.id} value={h.id}>{lang === "zh" ? h.nameZh : h.name} — {t("km_n", { n: h.distanceKm.toFixed(1) })}</option>
                  ))}
                </select>
                <span className="hint">{t("transport_rules")}</span>
              </div>
              {tq && (
                tq.ok ? (
                  <p className="alert alert--ok" data-testid="package-transport">
                    <Icon name="car" /> <span>{t("book_distance")} <b>{t("km_n", { n: tq.distanceKm.toFixed(1) })}</b> · {t("book_cars")} <b data-testid="package-cars">{t("cars_n", { n: tq.cars })}</b> · {t("price_transport")} <b data-testid="package-transport-fee">{tq.fee === 0 ? t("free") : formatBaht(tq.fee)}</b></span>
                  </p>
                ) : (
                  <p className="alert alert--error" role="alert" data-testid="package-transport-error">{errorText(lang, "TRANSPORT_TOO_FAR")}</p>
                )
              )}
              <Link href={`/book?service=${PACKAGE_SLUG}&people=${people}`} className="btn btn--gold btn--block btn--lg mt-1" data-testid="package-book">
                {t("pkg_book")} <Icon name="arrow" />
              </Link>
            </div>
            <p className="muted small mt-1">{pick(pkg, "desc", lang)}</p>
          </div>
        </div>
      </section>
    </>
  );
}
