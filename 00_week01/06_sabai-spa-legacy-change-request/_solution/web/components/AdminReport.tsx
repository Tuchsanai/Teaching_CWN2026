"use client";

import { useCallback, useEffect, useState } from "react";
import { formatBaht } from "@/lib/money.ts";
import { useI18n } from "./I18nProvider.tsx";

/** CR-05 รายงานยอด (ตรงกับ GET /api/admin/report · เงินเป็นบาท) */
interface Report {
  from: string;
  to: string;
  counts: { confirmed: number; completed: number; cancelled: number };
  revenue: number;
  giftcardPaid: number;
  otherPaid: number;
  transportFee: number;
  discounts: { group: number; tier: number; birthday: number };
  pointsEarned: number;
  courseSessions: number;
  pendingValue: number;
  byTherapist: { code: string; completed: number }[];
}

const baht = (v: number) => formatBaht(Math.round(v * 100));

export function AdminReport({ initialFrom, initialTo }: { initialFrom: string; initialTo: string }) {
  const { t } = useI18n();
  const [from, setFrom] = useState(initialFrom);
  const [to, setTo] = useState(initialTo);
  const [data, setData] = useState<Report | null>(null);
  const [error, setError] = useState<{ code: string; message: string } | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (f: string, tt: string) => {
    setBusy(true);
    try {
      const q = new URLSearchParams({ from: f, to: tt });
      const r = await fetch(`/api/admin/report?${q}`);
      const j = await r.json();
      if (r.ok) {
        setData(j);
        setError(null);
      } else {
        setData(null);
        setError({ code: j.error, message: j.message });
      }
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    void load(initialFrom, initialTo);
  }, [initialFrom, initialTo, load]);

  const money = (key: string, testid: string, v: number) => (
    <tr>
      <th scope="row">{t(key)}</th>
      <td data-testid={testid} data-amount={v}>
        {baht(v)}
      </td>
    </tr>
  );
  const num = (key: string, testid: string, v: number) => (
    <tr>
      <th scope="row">{t(key)}</th>
      <td data-testid={testid} data-value={v}>
        {v.toLocaleString("en-US")}
      </td>
    </tr>
  );

  return (
    <>
      <p className="muted small">{t("report.hint")}</p>
      <form
        className="card"
        style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "flex-end" }}
        onSubmit={(e) => {
          e.preventDefault();
          void load(from, to);
        }}
      >
        <div className="field" style={{ maxWidth: 220 }}>
          <label htmlFor="rfrom">{t("report.from")}</label>
          <input id="rfrom" type="date" value={from} onChange={(e) => setFrom(e.target.value)} data-testid="report-from" />
        </div>
        <div className="field" style={{ maxWidth: 220 }}>
          <label htmlFor="rto">{t("report.to")}</label>
          <input id="rto" type="date" value={to} onChange={(e) => setTo(e.target.value)} data-testid="report-to" />
        </div>
        <button type="submit" className="btn" disabled={busy} data-testid="report-run">
          {t("report.run")}
        </button>
      </form>

      {error && (
        <p className="alert alert-error" role="alert" data-testid="report-error" data-error-code={error.code}>
          {error.message}
        </p>
      )}

      {data && (
        <div data-testid="report-result" data-from={data.from} data-to={data.to}>
          <p>
            <a
              className="btn btn-ghost"
              href={`/api/admin/report?${new URLSearchParams({ from: data.from, to: data.to, format: "csv" })}`}
              download={`sabai-report-${data.from}_${data.to}.csv`}
              data-testid="report-csv"
            >
              {t("report.csv")}
            </a>
          </p>
          <div className="table-wrap card">
            <table className="data" data-testid="report-table">
              <thead>
                <tr>
                  <th scope="col">{t("report.item")}</th>
                  <th scope="col">{t("report.value")}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th colSpan={2}>{t("report.counts")}</th>
                </tr>
                {num("status.confirmed", "report-count-confirmed", data.counts.confirmed)}
                {num("status.completed", "report-count-completed", data.counts.completed)}
                {num("status.cancelled", "report-count-cancelled", data.counts.cancelled)}
                <tr>
                  <th colSpan={2}>{t("report.money")}</th>
                </tr>
                {money("report.revenue", "report-revenue", data.revenue)}
                {money("report.giftcardPaid", "report-giftcard", data.giftcardPaid)}
                {money("report.otherPaid", "report-other", data.otherPaid)}
                {money("report.transportFee", "report-transport", data.transportFee)}
                {money("report.discGroup", "report-disc-group", data.discounts.group)}
                {money("report.discTier", "report-disc-tier", data.discounts.tier)}
                {money("report.discBirthday", "report-disc-birthday", data.discounts.birthday)}
                <tr>
                  <th colSpan={2}>{t("report.other")}</th>
                </tr>
                {num("report.points", "report-points", data.pointsEarned)}
                {num("report.course", "report-course", data.courseSessions)}
                {money("report.pending", "report-pending", data.pendingValue)}
              </tbody>
            </table>
          </div>
          <h2>{t("report.byTherapist")}</h2>
          <div className="table-wrap card">
            <table className="data" data-testid="report-therapists">
              <thead>
                <tr>
                  <th scope="col">{t("book.therapist")}</th>
                  <th scope="col">{t("report.queues")}</th>
                </tr>
              </thead>
              <tbody>
                {data.byTherapist.map((x) => (
                  <tr key={x.code}>
                    <td>{x.code}</td>
                    <td data-testid={`report-therapist-${x.code}`}>{x.completed}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}
