"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { SHOP_PHONE } from "@/lib/i18n.ts";
import { useI18n } from "./I18nProvider.tsx";

export interface MyBooking {
  id: number;
  code: string;
  serviceName: string;
  dateLabel: string;
  time: string;
  endTime: string;
  therapists: string[];
  status: string;
  statusLabel: string;
  totalLabel: string;
  viaCourse: boolean;
  canCancel: boolean;
  cancelBlockedReason: string | null;
}

/** FR-07 ยกเลิกนัด (BR-07) · FR-17 ประวัติ วันที่ บริการ นักบำบัด ราคาที่จ่าย เรียงล่าสุด → เก่าสุด */
export function MyBookings({ items }: { items: MyBooking[] }) {
  const { t } = useI18n();
  const router = useRouter();
  const [confirming, setConfirming] = useState<number | null>(null);
  const [msg, setMsg] = useState<{ id: number; ok: boolean; text: string } | null>(null);

  const cancel = async (id: number) => {
    const r = await fetch(`/api/bookings/${id}/cancel`, { method: "POST" });
    const j = await r.json();
    setConfirming(null);
    if (r.ok) {
      setMsg({ id, ok: true, text: t("account.cancelDone") });
      router.refresh();
    } else {
      setMsg({ id, ok: false, text: j.message + (j.phone ? ` ${j.phone}` : "") });
    }
  };

  if (!items.length) return <p className="muted">{t("account.noBookings")}</p>;

  return (
    <ul className="booking-list" data-testid="history-list">
      {items.map((b) => (
        <li key={b.id} className={`card booking-item ${b.status}`} data-testid={`booking-${b.code}`} data-status={b.status}>
          <div className="btn-row" style={{ justifyContent: "space-between" }}>
            <strong data-testid={`booking-service-${b.code}`}>{b.serviceName}</strong>
            <span className={`badge ${b.status === "cancelled" ? "bad" : b.status === "completed" ? "ok" : ""}`} data-testid={`booking-status-${b.code}`}>
              {b.statusLabel}
            </span>
          </div>
          <div data-testid={`booking-date-${b.code}`}>
            {b.dateLabel} {b.time}–{b.endTime}
          </div>
          <div className="muted small" data-testid={`booking-therapist-${b.code}`}>
            {t("book.therapist")}: {b.therapists.join(", ") || "-"}
          </div>
          <div className="small">
            {t("account.paid")}: <strong data-testid={`booking-paid-${b.code}`}>{b.totalLabel}</strong>
            {b.viaCourse ? ` · ${t("type.course")}` : ""} · <span className="muted">{b.code}</span>
          </div>
          {b.status === "confirmed" && (
            <div className="btn-row">
              {confirming === b.id ? (
                <>
                  <button type="button" className="btn btn-sm" onClick={() => cancel(b.id)} data-testid={`cancel-confirm-${b.code}`}>
                    {t("account.cancelConfirm")}
                  </button>
                  <button type="button" className="btn btn-sm btn-ghost" onClick={() => setConfirming(null)} data-testid={`cancel-abort-${b.code}`}>
                    {t("book.back")}
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  className="btn btn-sm btn-ghost"
                  disabled={!b.canCancel}
                  onClick={() => setConfirming(b.id)}
                  data-testid={`cancel-${b.code}`}
                >
                  {t("account.cancel")}
                </button>
              )}
              {!b.canCancel && b.cancelBlockedReason && (
                <span className="small" style={{ color: "var(--danger)" }} data-testid={`cancel-blocked-${b.code}`}>
                  {b.cancelBlockedReason} ·{" "}
                  <a href={`tel:${SHOP_PHONE}`} data-testid={`cancel-phone-${b.code}`}>
                    {SHOP_PHONE}
                  </a>
                </span>
              )}
            </div>
          )}
          {msg?.id === b.id && (
            <div className={`alert ${msg.ok ? "alert-ok" : "alert-error"}`} role="status" data-testid={`cancel-result-${b.code}`}>
              {msg.text}
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
