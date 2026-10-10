"use client";

import Link from "next/link";
import { useState } from "react";
import { useApp, useReady } from "@/components/AppProvider";
import { Loader, PageHead, svcName, useServices } from "@/components/Shared";
import { MOODS, MOOD_IMAGES, recommendForMood, type Mood } from "@/lib/recommend";
import type { DictKey } from "@/lib/i18n";
import { formatBaht } from "@/lib/time";

export default function MoodPage() {
  const { t, lang } = useApp();
  const services = useServices();
  const [mood, setMood] = useState<Mood | null>(null);
  useReady(!!services);

  return (
    <>
      <PageHead eyebrow={t("nav_helpers")} title={t("mood_title")} lead={t("mood_lead")} image="/assets/treatments/foot-reflexology.jpg" />
      <section className="section">
        <div className="container">
          <div className="mood-grid" role="group" aria-label={t("mood_title")}>
            {MOODS.map((m) => (
              <button key={m} type="button" className={`mood-btn ${mood === m ? "is-active" : ""}`} aria-pressed={mood === m} onClick={() => setMood(m)} data-testid={`mood-${m}`}>
                <img src={MOOD_IMAGES[m]} alt={t(`mood_${m}` as DictKey)} width={120} height={120} />
                {t(`mood_${m}` as DictKey)}
              </button>
            ))}
          </div>
          {mood && !services && <Loader />}
          {mood && services && (
            <div className="result-panel" data-testid="mood-result" data-mood={mood} key={mood}>
              <h2 style={{ fontSize: "1.4rem" }}>{t("mood_result")}</h2>
              <p className="muted" data-testid="mood-reason">{t(`mood_reason_${mood}` as DictKey)}</p>
              <div className="rec-list">
                {recommendForMood(mood).map((slug) => {
                  const s = services.find((x) => x.slug === slug);
                  if (!s) return null;
                  return (
                    <div className="rec" key={slug} data-testid={`mood-rec-${slug}`}>
                      <img src={s.image} alt={svcName(s, lang)} />
                      <div>
                        <h3>{svcName(s, lang)}</h3>
                        <p>{t("minutes", { n: s.duration })} · {formatBaht(s.price)}{s.is_package ? t("per_person") : ""}</p>
                        <Link href={`/book?service=${slug}`} className="btn btn--green btn--sm" data-testid={`mood-book-${slug}`}>
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
    </>
  );
}
