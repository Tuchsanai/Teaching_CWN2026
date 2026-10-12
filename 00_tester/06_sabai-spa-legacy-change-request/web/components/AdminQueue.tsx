"use client";

import { useCallback, useEffect, useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

interface Row {
  id: number;
  code: string;
  time: string;
  customer: string;
  member: boolean;
  service: string;
  type: string;
  people: number;
  therapists: string[];
  status: string;
  statusLabel: string;
  totalLabel: string;
  viaCourse: boolean;
  pointsEarned: number;
}

/** หลังร้าน (D3): ตารางคิว · กด "ใช้บริการเสร็จ" ให้แต้ม (BR-09) ตัดครั้งคอร์ส (D5) บันทึกรอบเอว (FR-16) */
export function AdminQueue({ initialDate, today, allowReset }: { initialDate: string; today: string; allowReset: boolean }) {
  const { t } = useI18n();
  const [date, setDate] = useState(initialDate);
  const [rows, setRows] = useState<Row[]>([]);
  const [waist, setWaist] = useState<Record<number, string>>({});
  const [msg, setMsg] = useState<{ id: number; ok: boolean; text: string } | null>(null);
  const [resetMsg, setResetMsg] = useState<string | null>(null);

  const load = useCallback(async (d: string) => {
    const r = await fetch(`/api/admin/bookings?date=${d}`);
    if (r.ok) setRows((await r.json()).bookings);
  }, []);

  useEffect(() => {
    void load(date);
  }, [date, load]);

  const complete = async (row: Row) => {
    const r = await fetch(`/api/admin/bookings/${row.id}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ waistCm: row.viaCourse && waist[row.id] ? Number(waist[row.id]) : null }),
    });
    const j = await r.json();
    setMsg({ id: row.id, ok: r.ok, text: r.ok ? t("admin.done", { p: j.pointsEarned }) : j.message });
    await load(date);
  };

  return (
    <>
      <p className="muted" data-testid="admin-today">
        {t("admin.today", { d: today })}
      </p>
      <div className="field" style={{ maxWidth: 260 }}>
        <label htmlFor="adate">{t("admin.date")}</label>
        <input id="adate" type="date" value={date} onChange={(e) => setDate(e.target.value)} data-testid="admin-date" />
      </div>
      {rows.length === 0 ? (
        <p className="muted" data-testid="admin-empty">
          {t("admin.none")}
        </p>
      ) : (
        <div className="table-wrap card">
          <table className="data" data-testid="admin-table">
            <thead>
              <tr>
                <th scope="col">{t("admin.time")}</th>
                <th scope="col">{t("admin.customer")}</th>
                <th scope="col">{t("book.service")}</th>
                <th scope="col">{t("book.therapist")}</th>
                <th scope="col">{t("line.total")}</th>
                <th scope="col">{t("admin.status")}</th>
                <th scope="col">{t("admin.action")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} data-testid={`admin-row-${r.code}`} data-status={r.status}>
                  <td>
                    {r.time}
                    <div className="muted small">{r.code}</div>
                  </td>
                  <td>{r.customer}</td>
                  <td>
                    {r.service}
                    <div className="muted small">
                      {t(`type.${r.type}`)} · {r.people}
                    </div>
                  </td>
                  <td>{r.therapists.join(", ")}</td>
                  <td>{r.totalLabel}</td>
                  <td data-testid={`admin-status-${r.code}`}>
                    {r.statusLabel}
                    {r.status === "completed" && r.member ? <div className="small muted">+{r.pointsEarned}</div> : null}
                  </td>
                  <td>
                    {r.status === "confirmed" && (
                      <div style={{ display: "grid", gap: 6 }}>
                        {r.viaCourse && (
                          <input
                            type="number"
                            step="0.1"
                            min="1"
                            value={waist[r.id] ?? ""}
                            onChange={(e) => setWaist({ ...waist, [r.id]: e.target.value })}
                            aria-label={`${t("admin.waist")} ${r.code}`}
                            placeholder={t("admin.waist")}
                            data-testid={`admin-waist-${r.code}`}
                          />
                        )}
                        <button type="button" className="btn btn-sm" onClick={() => complete(r)} data-testid={`admin-complete-${r.code}`}>
                          {t("admin.complete")}
                        </button>
                      </div>
                    )}
                    {msg?.id === r.id && (
                      <div className={`small ${msg.ok ? "" : "alert alert-error"}`} role="status" data-testid={`admin-result-${r.code}`}>
                        {msg.text}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {allowReset && (
        <div className="thai-band">
          <button
            type="button"
            className="btn btn-ghost"
            data-testid="admin-reset"
            onClick={async () => {
              const r = await fetch("/api/test/reset", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
              const j = await r.json();
              setResetMsg(r.ok ? `${t("admin.resetDone")} · ${j.now}` : j.message);
              await load(date);
            }}
          >
            {t("admin.reset")}
          </button>
          {resetMsg && (
            <span className="small" data-testid="admin-reset-result" style={{ marginLeft: 10 }}>
              {resetMsg}
            </span>
          )}
        </div>
      )}
    </>
  );
}
