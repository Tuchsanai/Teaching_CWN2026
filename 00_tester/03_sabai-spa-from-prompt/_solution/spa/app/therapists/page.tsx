"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, useApp, useReady } from "@/components/AppProvider";
import { Reveal } from "@/components/Reveal";
import { Icon, Stars } from "@/components/Ornament";
import { Loader, PageHead } from "@/components/Shared";
import { pick } from "@/lib/i18n";
import { formatDate } from "@/lib/time";

type Review = { author: string; rating: number; reviewed_on: string; text_th: string; text_en: string; text_zh: string };
type Ther = {
  id: number; image: string; name_th: string; name_en: string; name_zh: string; title_th: string; title_en: string; title_zh: string;
  rating: number | null; review_count: number; reviews: Review[];
};

export default function TherapistsPage() {
  const { t, lang } = useApp();
  const [min, setMin] = useState<0 | 4.5>(0);
  const [list, setList] = useState<Ther[] | null>(null);
  const [open, setOpen] = useState<Record<number, boolean>>({});

  useEffect(() => {
    setList(null);
    // BR-10: the server applies the ≥ 4.5 filter (therapists without reviews are excluded)
    api<{ ok: boolean; therapists: Ther[] }>(`/api/therapists${min ? `?minRating=${min}` : ""}`).then((r) => r.ok && setList(r.therapists));
  }, [min]);
  useReady(!!list);

  return (
    <>
      <PageHead eyebrow={t("ther_eyebrow")} title={t("ther_title")} lead={t("ther_lead")} image="/assets/rooms/room-herbal-steam.jpg" />
      <section className="section">
        <div className="container">
          <div className="filter-bar" role="group" aria-label={t("ther_title")}>
            <button type="button" className={`chip ${min === 0 ? "is-active" : ""}`} aria-pressed={min === 0} onClick={() => setMin(0)} data-testid="filter-all">
              {t("ther_filter_all")}
            </button>
            <button type="button" className={`chip ${min === 4.5 ? "is-active" : ""}`} aria-pressed={min === 4.5} onClick={() => setMin(4.5)} data-testid="filter-45">
              <Icon name="star" size={16} /> {t("ther_filter_45")}
            </button>
            {list && <span className="muted small" data-testid="therapist-count">{t("ther_showing", { n: list.length })}</span>}
          </div>
          {!list ? (
            <Loader />
          ) : (
            <div className="grid grid--3" data-testid="therapist-list">
              {list.map((x, i) => (
                <Reveal key={x.id} delay={(i % 3) * 70}>
                  <article className="card ther-card" data-testid={`therapist-card-${x.id}`} data-rating={x.rating ?? ""}>
                    <div className="ther-card__media">
                      <img src={x.image} alt={pick(x, "name", lang)} loading="lazy" />
                      <span className="ther-card__score" data-testid={`therapist-rating-${x.id}`}>
                        <Icon name="star" size={16} /> {x.rating !== null ? x.rating.toFixed(1) : "—"}
                      </span>
                    </div>
                    <div className="ther-card__body">
                      <h3>{pick(x, "name", lang)}</h3>
                      <p className="muted small">{pick(x, "title", lang)}</p>
                      <div className="row">
                        <Stars value={x.rating} />
                        <span className="small muted" data-testid={`therapist-review-count-${x.id}`}>
                          {x.review_count > 0 ? t("ther_reviews", { n: x.review_count }) : t("ther_no_reviews")}
                        </span>
                      </div>
                      <div className="row mt-1">
                        <Link href={`/book?therapist=${x.id}`} className="btn btn--green btn--sm" data-testid={`therapist-book-${x.id}`}>
                          {t("ther_book")}
                        </Link>
                        {x.review_count > 0 && (
                          <button type="button" className="btn btn--ghost btn--sm" aria-expanded={!!open[x.id]} onClick={() => setOpen((o) => ({ ...o, [x.id]: !o[x.id] }))} data-testid={`therapist-toggle-reviews-${x.id}`}>
                            {open[x.id] ? t("ther_hide") : t("ther_read")}
                          </button>
                        )}
                      </div>
                      {open[x.id] && (
                        <div className="mt-1" data-testid={`therapist-reviews-${x.id}`}>
                          {x.reviews.map((r, k) => (
                            <div key={k} className="review">
                              <div className="review__head">
                                <span><b>{r.author}</b> · <Stars value={r.rating} size={13} /></span>
                                <span>{formatDate(r.reviewed_on, lang)}</span>
                              </div>
                              <p className="mt-0" style={{ margin: 0 }}>{pick(r, "text", lang)}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </article>
                </Reveal>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
