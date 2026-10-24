"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
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
  canReschedule?: boolean;
  date?: string;
  cancelBlockedReason: string | null;
}

interface ReschedSlot {
  time: string;
  endTime: string;
  available: boolean;
  current: boolean;
}

/** CR-01 กล่องเลื่อนนัด: เลือกวัน → รอบที่นักบำบัดคนเดิมว่าง (GET reschedule-slots) → ยืนยัน (POST reschedule) */
function RescheduleDialog({ b, onClose, onDone }: { b: MyBooking; onClose: () => void; onDone: (text: string) => void }) {
  const { t } = useI18n();
  const [date, setDate] = useState(b.date ?? "");
  const [range, setRange] = useState<{ min?: string; max?: string }>({});
  const [slots, setSlots] = useState<ReschedSlot[] | null>(null);
  const [time, setTime] = useState<string | null>(null);
  const [error, setError] = useState<{ code: string; text: string } | null>(null);
  const [busy, setBusy] = useState(false);

  const load = async (d: string) => {
    setDate(d);
    setTime(null);
    setSlots(null);
    setError(null);
    if (!d) return;
    const r = await fetch(`/api/bookings/${b.id}/reschedule-slots?date=${encodeURIComponent(d)}`);
    const j = await r.json();
    if (j.min || j.max) setRange({ min: j.min, max: j.max });
    if (r.ok) setSlots(j.slots);
    else setError({ code: j.error, text: j.message + (j.phone ? ` ${j.phone}` : "") });
  };

  useEffect(() => {
    if (b.date) void load(b.date);
  }, [b.id]);

  const confirm = async () => {
    if (!time) return;
    setBusy(true);
    const r = await fetch(`/api/bookings/${b.id}/reschedule`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date, time }),
    });
    const j = await r.json();
    setBusy(false);
    if (r.ok) onDone(j.message);
    else setError({ code: j.error, text: j.message + (j.phone ? ` ${j.phone}` : "") });
  };

  const open = slots?.filter((s) => s.available) ?? [];
  return (
    <div className="card" role="dialog" aria-modal="false" aria-label={t("account.rescheduleTitle", { code: b.code })} data-testid="reschedule-dialog">
      <strong>{t("account.rescheduleTitle", { code: b.code })}</strong>
      <div>
        <label htmlFor={`reschedule-date-${b.code}`}>{t("account.rescheduleDate")}</label>{" "}
        <input
          id={`reschedule-date-${b.code}`}
          type="date"
          min={range.min}
          max={range.max}
          value={date}
          onChange={(e) => load(e.target.value)}
          data-testid="reschedule-date"
        />
      </div>
      {slots && (
        <div>
          <div className="small muted">{t("account.rescheduleSlots")}</div>
          {open.length ? (
            <div className="btn-row" data-testid="reschedule-slots">
              {slots.map((s) =>
                s.available ? (
                  <button
                    key={s.time}
                    type="button"
                    className={`btn btn-sm ${time === s.time ? "" : "btn-ghost"}`}
                    aria-pressed={time === s.time}
                    onClick={() => setTime(s.time)}
                    data-testid={`reschedule-slot-${s.time}`}
                  >
                    {s.time}
                  </button>
                ) : null,
              )}
            </div>
          ) : (
            <p className="small muted" data-testid="reschedule-no-slots">
              {t("account.rescheduleNoSlots")}
            </p>
          )}
        </div>
      )}
      {error && (
        <div className="alert alert-error" role="alert" data-testid="reschedule-error" data-error-code={error.code}>
          {error.text}
        </div>
      )}
      <div className="btn-row">
        <button type="button" className="btn btn-sm" disabled={!time || busy} onClick={confirm} data-testid="reschedule-confirm">
          {t("account.rescheduleConfirm")}
        </button>
        <button type="button" className="btn btn-sm btn-ghost" onClick={onClose} data-testid="reschedule-close">
          {t("account.rescheduleClose")}
        </button>
      </div>
    </div>
  );
}

/** FR-07 ยกเลิกนัด (BR-07) · FR-17 ประวัติ วันที่ บริการ นักบำบัด ราคาที่จ่าย เรียงล่าสุด → เก่าสุด */
export function MyBookings({ items }: { items: MyBooking[] }) {
  const { t } = useI18n();
  const router = useRouter();
  const [confirming, setConfirming] = useState<number | null>(null);
  const [msg, setMsg] = useState<{ id: number; ok: boolean; text: string } | null>(null);
  const [rescheduling, setRescheduling] = useState<number | null>(null);
  const [done, setDone] = useState<{ id: number; text: string } | null>(null);

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
                <>
                  <button
                    type="button"
                    className="btn btn-sm btn-ghost"
                    disabled={!b.canCancel}
                    onClick={() => setConfirming(b.id)}
                    data-testid={`cancel-${b.code}`}
                  >
                    {t("account.cancel")}
                  </button>
                  <button
                    type="button"
                    className="btn btn-sm btn-ghost"
                    disabled={!b.canReschedule}
                    onClick={() => {
                      setDone(null);
                      setRescheduling(b.id);
                    }}
                    data-testid={`reschedule-${b.code}`}
                  >
                    {t("account.reschedule")}
                  </button>
                </>
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
          {rescheduling === b.id && b.status === "confirmed" && (
            <RescheduleDialog
              b={b}
              onClose={() => setRescheduling(null)}
              onDone={(text) => {
                setRescheduling(null);
                setDone({ id: b.id, text });
                router.refresh();
              }}
            />
          )}
          {done?.id === b.id && (
            <div className="alert alert-ok" role="status" data-testid="reschedule-done">
              {done.text}
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
