"use client";

import Link from "next/link";
import { useState } from "react";
import { formatBaht } from "@/lib/money.ts";
import { useI18n } from "./I18nProvider.tsx";

const MOODS = [
  { key: "stressed", icon: "😣" },
  { key: "tired", icon: "😮‍💨" },
  { key: "aches", icon: "💆" },
  { key: "insomnia", icon: "🌙" },
];

interface Rec {
  mood: string;
  reason: string;
  services: { code: string; name: string; priceSatang: number; durationMin: number }[];
}

/** FR-27 เลือก 1 อารมณ์ → บริการแนะนำ 1–3 รายการ + ปุ่มจองต่อ */
export function MoodPicker() {
  const { t } = useI18n();
  const [mood, setMood] = useState<string | null>(null);
  const [rec, setRec] = useState<Rec | null>(null);

  const pick = async (m: string) => {
    setMood(m);
    const r = await fetch(`/api/mood?mood=${m}`);
    if (r.ok) setRec(await r.json());
  };

  return (
    <section className="card" aria-labelledby="mood-title" data-testid="mood-section">
      <h2 id="mood-title">{t("home.moodTitle")}</h2>
      <p className="muted">{t("home.moodHint")}</p>
      <div className="choice-grid" role="radiogroup" aria-labelledby="mood-title">
        {MOODS.map((m) => (
          <button
            key={m.key}
            type="button"
            role="radio"
            aria-checked={mood === m.key}
            className={`choice${mood === m.key ? " selected" : ""}`}
            onClick={() => pick(m.key)}
            data-testid={`mood-${m.key}`}
          >
            <span aria-hidden="true">{m.icon}</span> {t(`mood.${m.key}`)}
          </button>
        ))}
      </div>
      {rec && (
        <div className="thai-band" data-testid="mood-result" aria-live="polite">
          <h3>{t("mood.result")}</h3>
          <p data-testid="mood-reason">{rec.reason}</p>
          <ul className="booking-list">
            {rec.services.map((s) => (
              <li key={s.code} className="btn-row" data-testid={`mood-rec-${s.code}`}>
                <strong>{s.name}</strong>
                <span className="muted">
                  {s.durationMin} {t("common.minutes")} · {formatBaht(s.priceSatang)}
                </span>
                <Link className="btn btn-sm" href={`/book?service=${s.code}`} data-testid={`mood-book-${s.code}`}>
                  {t("common.bookNow")}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
