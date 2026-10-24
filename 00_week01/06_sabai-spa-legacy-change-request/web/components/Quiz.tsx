"use client";

import Link from "next/link";
import { useState } from "react";
import { formatBaht } from "@/lib/money.ts";
import { useI18n } from "./I18nProvider.tsx";

interface Q {
  id: string;
  text: string;
  options: { value: string; label: string }[];
}

/** FR-28 แบบทดสอบ 4 ข้อพอดี แถบบอกข้อ 1/4 … 4/4 → แพ็กเกจแนะนำ 1 รายการ + เหตุผล + ปุ่มจอง */
export function Quiz({ questions }: { questions: Q[] }) {
  const { t } = useI18n();
  const [i, setI] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<{ code: string; name: string; price: number; reason: string; image: string } | null>(null);

  const q = questions[i];
  const answer = async (v: string) => {
    const next = { ...answers, [q.id]: v };
    setAnswers(next);
    if (i < questions.length - 1) {
      setI(i + 1);
      return;
    }
    const r = await fetch("/api/quiz", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ answers: next }) });
    if (r.ok) setResult(await r.json());
  };

  if (result) {
    const href = result.code === "P01" ? "/book?type=package&service=P01" : result.code === "K01" ? "/wallet" : `/book?service=${result.code}`;
    return (
      <div className="card" data-testid="quiz-result">
        <h2>{t("quiz.result")}</h2>
        <img src={result.image} alt={result.name} style={{ width: "100%", maxWidth: 360, borderRadius: 12 }} />
        <p className="price" data-testid="quiz-package" data-code={result.code}>
          {result.name} · {formatBaht(Math.round(result.price * 100))}
        </p>
        <p>
          <strong>{t("quiz.reason")}:</strong> <span data-testid="quiz-reason">{result.reason}</span>
        </p>
        <div className="btn-row">
          <Link className="btn btn-gold" href={href} data-testid="quiz-book">
            {t("common.bookNow")}
          </Link>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              setResult(null);
              setAnswers({});
              setI(0);
            }}
            data-testid="quiz-restart"
          >
            {t("quiz.restart")}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card" data-testid="quiz">
      <p data-testid="quiz-progress" data-current={i + 1}>
        {t("quiz.progress", { n: i + 1 })}
      </p>
      <div className="progress" role="progressbar" aria-valuemin={1} aria-valuemax={4} aria-valuenow={i + 1} aria-label={t("quiz.progress", { n: i + 1 })}>
        <span style={{ width: `${((i + 1) / 4) * 100}%` }} />
      </div>
      <h2 data-testid="quiz-question">{q.text}</h2>
      <div className="choice-grid">
        {q.options.map((o) => (
          <button key={o.value} type="button" className="choice" onClick={() => answer(o.value)} data-testid={`quiz-option-${o.value}`}>
            {o.label}
          </button>
        ))}
      </div>
      {i > 0 && (
        <button type="button" className="btn btn-ghost btn-sm" style={{ marginTop: 12 }} onClick={() => setI(i - 1)} data-testid="quiz-back">
          {t("book.back")}
        </button>
      )}
    </div>
  );
}
