"use client";

import Link from "next/link";
import { useState } from "react";
import { useApp, useReady } from "@/components/AppProvider";
import { Icon } from "@/components/Ornament";
import { HerbPills, Loader, PageHead, svcName, useServices } from "@/components/Shared";
import { QUIZ, quizResult, type QuizAnswers } from "@/lib/recommend";
import type { DictKey } from "@/lib/i18n";
import { formatBaht } from "@/lib/time";

export default function QuizPage() {
  const { t, lang } = useApp();
  const services = useServices();
  const [answers, setAnswers] = useState<QuizAnswers>({});
  const [idx, setIdx] = useState(0);
  useReady(!!services);

  const answered = QUIZ.filter((q) => answers[q.id as keyof QuizAnswers]).length;
  const result = quizResult(answers); // BR-24: null until all 4 are answered
  const finished = idx >= QUIZ.length && !!result;
  const q = QUIZ[Math.min(idx, QUIZ.length - 1)];

  const choose = (value: string) => {
    setAnswers((a) => ({ ...a, [q.id]: value }));
    setIdx((i) => i + 1);
  };
  const restart = () => {
    setAnswers({});
    setIdx(0);
  };
  const svc = result ? services?.find((s) => s.slug === result.service) : undefined;

  return (
    <>
      <PageHead eyebrow={t("nav_helpers")} title={t("quiz_title")} lead={t("quiz_lead")} image="/assets/treatments/herbal-compress.jpg" />
      <section className="section">
        <div className="container--narrow">
          {!finished ? (
            <div className="card card--pad quiz-card" key={idx} data-testid="quiz-card">
              <div className="quiz-progress">
                <div className="quiz-progress__bar" aria-hidden="true"><i style={{ width: `${(Math.min(idx + 1, 4) / 4) * 100}%` }} /></div>
                <b data-testid="quiz-progress" aria-live="polite">{t("quiz_progress", { i: Math.min(idx + 1, 4) })}</b>
              </div>
              <h2 data-testid="quiz-question" data-question={q.id}>{t(`quiz_q_${q.id}` as DictKey)}</h2>
              <div className="quiz-opts mt-2" role="radiogroup" aria-label={t(`quiz_q_${q.id}` as DictKey)}>
                {q.options.map((o) => (
                  <button key={o} type="button" role="radio" aria-checked={answers[q.id as keyof QuizAnswers] === o} className={`quiz-opt ${answers[q.id as keyof QuizAnswers] === o ? "is-active" : ""}`} onClick={() => choose(o)} data-testid={`quiz-option-${o}`}>
                    {t(`quiz_${q.id}_${o}` as DictKey)}
                  </button>
                ))}
              </div>
              <div className="row row--between mt-2">
                <button type="button" className="btn btn--ghost btn--sm" disabled={idx === 0} onClick={() => setIdx((i) => Math.max(0, i - 1))} data-testid="quiz-back">
                  <Icon name="left" size={18} /> {t("back")}
                </button>
                <span className="small muted" data-testid="quiz-answered">{answered}/4</span>
              </div>
            </div>
          ) : !services ? (
            <Loader />
          ) : (
            svc && result && (
              <div className="card result-panel" data-testid="quiz-result" data-service={svc.slug} style={{ padding: 0, overflow: "hidden" }}>
                <div className="svc-card__media" style={{ aspectRatio: "21/9" }}>
                  <img src={svc.image} alt={svcName(svc, lang)} />
                  <span className="svc-card__tag">{t("quiz_result")}</span>
                  <span className="svc-card__price">{formatBaht(svc.price)}{svc.is_package ? t("per_person") : ""}</span>
                </div>
                <div className="card--pad">
                  <h2 data-testid="quiz-result-service">{svcName(svc, lang)}</h2>
                  <p className="label">{t("quiz_reason")}</p>
                  <p data-testid="quiz-reason">{t(`quiz_reason_${result.reason}` as DictKey)}</p>
                  <HerbPills herbs={svc.herbs} />
                  <div className="row mt-2">
                    <Link href={`/book?service=${svc.slug}`} className="btn btn--gold btn--lg" data-testid="quiz-book">
                      {t("book_now")} <Icon name="arrow" />
                    </Link>
                    <button type="button" className="btn btn--ghost" onClick={restart} data-testid="quiz-restart">{t("quiz_restart")}</button>
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      </section>
    </>
  );
}
