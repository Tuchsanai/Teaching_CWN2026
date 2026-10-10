"use client";

import { useState } from "react";
import { useApp, useReady } from "@/components/AppProvider";
import { Reveal } from "@/components/Reveal";
import { AllergyWarning, Loader, PageHead, ServiceCard, useServices } from "@/components/Shared";
import type { DictKey } from "@/lib/i18n";

const CATS = ["all", "massage", "body", "facial", "package"] as const;

export default function ServicesPage() {
  const { t } = useApp();
  const services = useServices();
  const [cat, setCat] = useState<(typeof CATS)[number]>("all");
  useReady(!!services);
  const list = (services ?? []).filter((s) => cat === "all" || s.category === cat);

  return (
    <>
      <PageHead eyebrow={t("services_eyebrow")} title={t("services_title")} lead={t("services_lead")} image="/assets/treatments/aroma-oil.jpg" />
      <section className="section">
        <div className="container">
          <div className="filter-bar" role="group" aria-label={t("services_title")}>
            {CATS.map((c) => (
              <button key={c} type="button" className={`chip ${cat === c ? "is-active" : ""}`} aria-pressed={cat === c} onClick={() => setCat(c)} data-testid={`cat-${c}`}>
                {t(`cat_${c}` as DictKey)}
              </button>
            ))}
          </div>
          <AllergyWarning />
          {!services ? (
            <Loader />
          ) : (
            <div className="grid grid--3 mt-2" data-testid="service-list">
              {list.map((s, i) => (
                <Reveal key={s.slug} delay={(i % 3) * 70}>
                  <ServiceCard s={s} />
                </Reveal>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
