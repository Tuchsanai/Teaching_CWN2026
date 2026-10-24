"use client";

import Link from "next/link";
import { useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

export interface TherapistItem {
  code: string;
  name: string;
  rating: string | null;
  reviewCount: number;
  passes45: boolean;
  services: string[];
  serviceNames: string[];
  image: string;
}

/** FR-08 คะแนนเฉลี่ยทศนิยม 1 ตำแหน่ง + จำนวนรีวิว + ตัวกรอง 4.5 ดาวขึ้นไป (BR-08) */
export function TherapistList({ items, initialFilter }: { items: TherapistItem[]; initialFilter: boolean }) {
  const { t } = useI18n();
  const [only45, setOnly45] = useState(initialFilter);
  const shown = only45 ? items.filter((x) => x.passes45) : items;
  return (
    <>
      <label className="check">
        <input type="checkbox" checked={only45} onChange={(e) => setOnly45(e.target.checked)} data-testid="filter-45" />
        {t("therapists.filter")}
      </label>
      <p className="muted small" data-testid="therapist-count">
        {t("therapists.count", { n: shown.length })}
      </p>
      <div className="grid">
        {shown.map((x) => (
          <article key={x.code} className="card thr-card" data-testid={`therapist-${x.code}`}>
            <img src={x.image} alt={x.name} loading="lazy" />
            <div>
              <h2 style={{ fontSize: "1.2rem", margin: 0 }} data-testid={`therapist-name-${x.code}`}>
                {x.name}
              </h2>
              {x.rating ? (
                <div>
                  <span className="stars" aria-hidden="true">★</span>{" "}
                  <strong data-testid={`therapist-rating-${x.code}`}>{x.rating}</strong>{" "}
                  <span className="muted" data-testid={`therapist-reviews-${x.code}`}>
                    ({t("therapists.reviews", { n: x.reviewCount })})
                  </span>
                </div>
              ) : (
                <div className="muted" data-testid={`therapist-rating-${x.code}`}>
                  {t("therapists.noReviews")}
                </div>
              )}
              <div className="small muted">
                {t("therapists.does")}: {x.serviceNames.join(", ")}
              </div>
              <Link className="btn btn-sm" href={`/book?service=${x.services.find((s) => s.startsWith("S")) ?? "S01"}`} data-testid={`therapist-book-${x.code}`}>
                {t("common.bookNow")}
              </Link>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
