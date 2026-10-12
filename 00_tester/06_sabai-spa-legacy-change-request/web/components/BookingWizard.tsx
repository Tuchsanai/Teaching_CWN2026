"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { SHOP_PHONE } from "@/lib/i18n.ts";
import { formatBaht } from "@/lib/money.ts";
import { checkParty, type BookingType } from "@/lib/rules/party.ts";
import { useI18n } from "./I18nProvider.tsx";
import { Lotus, Orchid } from "./ThaiOrnament.tsx";
import { Tour360 } from "./Tour360.tsx";

export interface WizardService {
  code: string;
  name: string;
  kind: "single" | "package" | "course";
  durationMin: number;
  priceSatang: number;
  herbs: string[];
}

interface Slot {
  time: string;
  endTime: string;
  available: boolean;
  therapists: { code: string; name: string }[];
}

interface QuoteLine {
  key: string;
  label: string;
  amount: number;
  display: string;
}

interface Quote {
  service: { code: string; name: string; herbs: string[] };
  whenLabel: string;
  total: number;
  totalLabel: string;
  lines: QuoteLine[];
  pointsToEarn: number;
  birthdayAvailable: boolean;
  maxRedeemBlocks: number;
  pointsBalance: number;
  loggedIn: boolean;
  vehicles: number;
  transportFee: number;
  course: { remainingAfter: number } | null;
  giftCard: { code: string; status: string; balance: number; balanceAfter: number; expiresOn: string } | null;
  giftCardError: { code: string; message: string } | null;
}

interface ApiErr {
  error: string;
  message: string;
  phone?: string;
}

export interface WizardProps {
  services: WizardService[];
  hotels: { code: string; name: string; distanceKm: number }[];
  user: { name: string; phone: string } | null;
  courses: { id: number; code: string; label: string; usable: boolean }[];
  range: { min: string; max: string };
  initial: { type: BookingType; service: string; people: number };
  panorama: string;
}

const TYPES: BookingType[] = ["single", "couple", "group", "package", "course"];

function defaultPeople(type: BookingType) {
  return type === "couple" ? 2 : type === "group" ? 3 : 1;
}

export function BookingWizard(props: WizardProps) {
  const { t } = useI18n();
  const [step, setStep] = useState(1);
  const [type, setType] = useState<BookingType>(props.initial.type);
  const [serviceCode, setServiceCode] = useState(props.initial.service);
  const [people, setPeople] = useState(String(props.initial.people));
  const [date, setDate] = useState("");
  const [slots, setSlots] = useState<Slot[] | null>(null);
  const [time, setTime] = useState("");
  const [therapist, setTherapist] = useState("");
  const [contactName, setContactName] = useState(props.user?.name ?? "");
  const [contactPhone, setContactPhone] = useState(props.user?.phone ?? "");
  const [redeemBlocks, setRedeemBlocks] = useState(0);
  const [useBirthday, setUseBirthday] = useState(false);
  const [gcInput, setGcInput] = useState("");
  const [gcCode, setGcCode] = useState("");
  const [wantTransport, setWantTransport] = useState(false);
  const [hotelCode, setHotelCode] = useState("");
  const [distance, setDistance] = useState("");
  const [courseId, setCourseId] = useState<number | "">(props.courses.find((c) => c.usable)?.id ?? "");
  const [quote, setQuote] = useState<Quote | null>(null);
  const [quoteErr, setQuoteErr] = useState<ApiErr | null>(null);
  const [error, setError] = useState<ApiErr | null>(null);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState<{ code: string; message: string; detail: string; therapistNames: string[] } | null>(null);
  const [tour, setTour] = useState(false);
  const topRef = useRef<HTMLDivElement>(null);

  const forType = useMemo(
    () => props.services.filter((s) => (type === "package" ? s.kind === "package" : type === "course" ? s.kind === "course" : s.kind === "single")),
    [props.services, type],
  );
  const service = props.services.find((s) => s.code === serviceCode);
  const peopleN = Number(people);

  useEffect(() => {
    if (!forType.some((s) => s.code === serviceCode)) setServiceCode(forType[0]?.code ?? "");
  }, [forType, serviceCode]);

  useEffect(() => {
    topRef.current?.scrollIntoView({ block: "start", behavior: "smooth" });
  }, [step]);

  const chooseType = (tp: BookingType) => {
    setType(tp);
    setPeople(String(defaultPeople(tp)));
    setError(null);
  };

  // ── ขั้น 1 → 2: ตรวจจำนวนคน (BR-04, BR-05) ──
  const next1 = () => {
    const pe = checkParty(type, peopleN);
    if (pe) {
      setError({ error: pe, message: t(`err.${pe}`), phone: pe === "GROUP_CALL_SHOP" ? SHOP_PHONE : undefined });
      return;
    }
    if (!service) return;
    setError(null);
    setStep(2);
  };

  // ── ขั้น 2: รอบว่างจากเซิร์ฟเวอร์ ──
  const loadSlots = async (d: string) => {
    setDate(d);
    setTime("");
    setTherapist("");
    setSlots(null);
    setError(null);
    if (!d) return;
    const q = new URLSearchParams({ service: serviceCode, date: d, type, people: String(peopleN) });
    const r = await fetch(`/api/slots?${q}`);
    const j = await r.json();
    if (!r.ok) {
      setError(j);
      return;
    }
    setSlots(j.slots);
  };
  const freeSlots = (slots ?? []).filter((s) => s.available);
  const chosenSlot = freeSlots.find((s) => s.time === time);

  // ── ขั้น 3: ใบเสนอราคาจากเซิร์ฟเวอร์ (ไม่คิดเองในเบราว์เซอร์) ──
  const body = () => ({
    type,
    serviceCode,
    people: peopleN,
    date,
    time,
    therapists: therapist ? [therapist] : [],
    contactName,
    contactPhone,
    redeemBlocks,
    useBirthday,
    giftCardCode: gcCode || null,
    hotelCode: wantTransport && hotelCode ? hotelCode : null,
    distanceKm: wantTransport && !hotelCode && distance !== "" ? Number(distance) : null,
    coursePurchaseId: type === "course" && courseId !== "" ? courseId : null,
  });

  useEffect(() => {
    if (step < 3) return;
    let cancelled = false;
    const timer = setTimeout(async () => {
      const r = await fetch("/api/price", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body()) });
      const j = await r.json();
      if (cancelled) return;
      if (r.ok) {
        setQuote(j);
        setQuoteErr(null);
        if (!j.birthdayAvailable && useBirthday) setUseBirthday(false);
      } else {
        setQuote(null);
        setQuoteErr(j);
        if (j.error === "BIRTHDAY_UNAVAILABLE") setUseBirthday(false);
        if (j.error === "GC_NOT_FOUND") setGcCode("");
      }
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step, redeemBlocks, useBirthday, gcCode, wantTransport, hotelCode, distance, courseId]);

  const contactOk = !!props.user || (contactName.trim() !== "" && contactPhone.trim() !== "");
  const next3 = () => {
    if (!contactOk) {
      setError({ error: "CONTACT_REQUIRED", message: t("err.CONTACT_REQUIRED") });
      return;
    }
    if (!quote) return;
    setError(null);
    setStep(4);
  };

  // ── ขั้น 4: ยืนยัน → POST /api/bookings พร้อม quotedTotal (NFR-17) ──
  const confirm = async () => {
    if (!quote) return;
    setBusy(true);
    setError(null);
    try {
      const r = await fetch("/api/bookings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...body(), quotedTotal: quote.total }),
      });
      const j = await r.json();
      if (r.status === 201) {
        setDone(j);
        return;
      }
      setError(j);
      if (j.error === "PRICE_CHANGED" && j.quote) setQuote(j.quote);
      if (j.error === "SLOT_TAKEN") {
        await loadSlots(date);
        setError(j);
        setStep(2);
      }
    } finally {
      setBusy(false);
    }
  };

  const reset = () => {
    setDone(null);
    setStep(1);
    setDate("");
    setSlots(null);
    setTime("");
    setQuote(null);
    setRedeemBlocks(0);
    setUseBirthday(false);
    setGcCode("");
    setGcInput("");
  };

  const ErrorBox = ({ e, testid = "book-error" }: { e: ApiErr | null; testid?: string }) =>
    e ? (
      <div className="alert alert-error" role="alert" data-testid={testid} data-error-code={e.error}>
        <span data-testid={`${testid}-message`}>{e.message}</span>
        {e.phone && (
          <>
            {" "}
            · {t("book.callShop")}{" "}
            <a href={`tel:${e.phone}`} data-testid="shop-phone">
              {e.phone}
            </a>
          </>
        )}
      </div>
    ) : null;

  if (done) {
    return (
      <div className="card confirm-box" data-testid="booking-done">
        <div className="ornament-row">
          <Orchid size={46} />
          <Lotus size={46} />
          <Orchid size={46} />
        </div>
        <h2 data-testid="booking-confirmation">{done.message}</h2>
        <p data-testid="booking-detail">{done.detail}</p>
        <p className="muted" data-testid="booking-therapists">
          {t("book.therapist")}: {done.therapistNames.join(", ")}
        </p>
        <span hidden data-testid="booking-code">
          {done.code}
        </span>
        <button type="button" className="btn" onClick={reset} data-testid="book-again">
          {t("book.again")}
        </button>
      </div>
    );
  }

  return (
    <div ref={topRef}>
      <ol className="stepper" aria-label={t("book.title")}>
        {[1, 2, 3, 4].map((n) => (
          <li key={n} className={n === step ? "current" : n < step ? "done" : ""} aria-current={n === step ? "step" : undefined}>
            {n}. {t(`book.step${n}`)}
          </li>
        ))}
      </ol>
      <p className="muted small" data-testid="book-step-indicator" data-step={step}>
        {t("book.stepOf", { n: step })}
      </p>

      {step === 1 && (
        <section className="card" aria-labelledby="s1">
          <h2 id="s1">
            1. {t("book.step1")}
          </h2>
          <fieldset style={{ border: 0, padding: 0, margin: "0 0 14px" }}>
            <legend style={{ fontWeight: 600, marginBottom: 6 }}>{t("book.type")}</legend>
            <div className="choice-grid">
              {TYPES.map((tp) => (
                <label key={tp} className="choice" data-testid={`book-type-label-${tp}`}>
                  <input type="radio" name="btype" value={tp} checked={type === tp} onChange={() => chooseType(tp)} data-testid={`book-type-${tp}`} />
                  {t(`type.${tp}`)}
                </label>
              ))}
            </div>
          </fieldset>
          <div className="field">
            <label htmlFor="svc">{t("book.service")}</label>
            <select id="svc" value={serviceCode} onChange={(e) => setServiceCode(e.target.value)} data-testid="book-service">
              {forType.map((s) => (
                <option key={s.code} value={s.code}>
                  {s.name} · {s.durationMin} {t("common.minutes")} · {formatBaht(s.priceSatang)}
                </option>
              ))}
            </select>
          </div>
          {type !== "single" && type !== "course" && (
            <div className="field">
              <label htmlFor="people">{t("book.people")}</label>
              <input id="people" type="number" inputMode="numeric" min={1} max={20} value={people} onChange={(e) => setPeople(e.target.value)} data-testid="book-people" />
            </div>
          )}
          {type === "couple" && (
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setTour(true)} data-testid="book-tour-open">
              {t("book.tour")}
            </button>
          )}
          {type === "course" && !props.user && <p className="alert alert-info">{t("book.courseLogin")}</p>}
          {service && (
            <div className="thai-band small" data-testid="book-service-herbs">
              <strong>{t("common.herbs")}:</strong> {service.herbs.join(", ")}
            </div>
          )}
          <ErrorBox e={error} />
          <div className="btn-row">
            <button type="button" className="btn" onClick={next1} disabled={type === "course" && !props.user} data-testid="book-next-1">
              {t("book.next")}
            </button>
          </div>
        </section>
      )}

      {step === 2 && (
        <section className="card" aria-labelledby="s2">
          <h2 id="s2">
            2. {t("book.step2")}
          </h2>
          <p className="muted">
            {service?.name} · {t(`type.${type}`)} · {peopleN} {t("common.people")}
          </p>
          {type === "couple" && (
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setTour(true)} data-testid="book-tour-open-2">
              {t("book.tour")}
            </button>
          )}
          <div className="field">
            <label htmlFor="date">{t("book.date")}</label>
            <input id="date" type="date" min={props.range.min} max={props.range.max} value={date} onChange={(e) => loadSlots(e.target.value)} data-testid="book-date" />
            <div className="small muted">{t("book.dateHint", { min: props.range.min, max: props.range.max })}</div>
          </div>
          <ErrorBox e={error} />
          {slots && (
            <div className="field">
              <div style={{ fontWeight: 600, marginBottom: 6 }} id="slots-label">
                {t("book.time")}
              </div>
              {freeSlots.length === 0 ? (
                <p className="alert alert-info" data-testid="book-no-slots">
                  {t("book.noSlots")}
                </p>
              ) : (
                <div className="slot-grid" role="group" aria-labelledby="slots-label" data-testid="book-slots">
                  {freeSlots.map((s) => (
                    <button
                      key={s.time}
                      type="button"
                      aria-pressed={time === s.time}
                      onClick={() => {
                        setTime(s.time);
                        setTherapist("");
                        setError(null);
                      }}
                      data-testid={`book-slot-${s.time}`}
                    >
                      {s.time}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
          {chosenSlot && type === "single" && (
            <div className="field">
              <label htmlFor="thr">{t("book.therapist")}</label>
              <select id="thr" value={therapist} onChange={(e) => setTherapist(e.target.value)} data-testid="book-therapist">
                <option value="">{t("book.anyTherapist")}</option>
                {chosenSlot.therapists.map((th) => (
                  <option key={th.code} value={th.code}>
                    {th.name}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="btn-row">
            <button type="button" className="btn btn-ghost" onClick={() => setStep(1)} data-testid="book-back-2">
              {t("book.back")}
            </button>
            <button type="button" className="btn" disabled={!chosenSlot} onClick={() => { setError(null); setStep(3); }} data-testid="book-next-2">
              {t("book.next")}
            </button>
          </div>
        </section>
      )}

      {step === 3 && (
        <section className="card" aria-labelledby="s3">
          <h2 id="s3">
            3. {t("book.step3")}
          </h2>
          <div className="field">
            <label htmlFor="cname">{t("book.contactName")}</label>
            <input id="cname" type="text" autoComplete="name" value={contactName} onChange={(e) => setContactName(e.target.value)} data-testid="book-contact-name" />
          </div>
          <div className="field">
            <label htmlFor="cphone">{t("book.contactPhone")}</label>
            <input id="cphone" type="tel" autoComplete="tel" value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} data-testid="book-contact-phone" />
          </div>
          {!props.user && <p className="alert alert-info small">{t("book.guestHint")}</p>}

          <h3>{t("book.options")}</h3>
          {type === "course" && (
            <div className="field">
              <label htmlFor="course">{t("book.course")}</label>
              {props.courses.some((c) => c.usable) ? (
                <select id="course" value={courseId} onChange={(e) => setCourseId(Number(e.target.value))} data-testid="book-course">
                  {props.courses.map((c) => (
                    <option key={c.id} value={c.id} disabled={!c.usable}>
                      {c.code} · {c.label}
                    </option>
                  ))}
                </select>
              ) : (
                <p className="alert alert-info" data-testid="book-course-none">
                  {t("book.courseNone")}
                </p>
              )}
            </div>
          )}

          {props.user && type !== "course" && (
            <div className="field">
              <label htmlFor="pts">{t("book.points")}</label>
              <div className="small muted" data-testid="book-points-info">
                {t("book.pointsHave", { p: quote?.pointsBalance ?? 0, b: quote?.maxRedeemBlocks ?? 0 })}
              </div>
              <select
                id="pts"
                value={redeemBlocks}
                disabled={!quote || quote.maxRedeemBlocks < 1}
                onChange={(e) => setRedeemBlocks(Number(e.target.value))}
                data-testid="book-points"
              >
                {Array.from({ length: (quote?.maxRedeemBlocks ?? 0) + 1 }, (_, i) => (
                  <option key={i} value={i}>
                    {i} × 100 = -{formatBaht(i * 5000)}
                  </option>
                ))}
              </select>
              {quote && quote.maxRedeemBlocks < 1 && (
                <div className="small muted" data-testid="book-points-none">
                  {t("book.redeemNone")}
                </div>
              )}
            </div>
          )}

          {quote?.birthdayAvailable && (
            <label className="check" data-testid="book-birthday-label">
              <input type="checkbox" checked={useBirthday} onChange={(e) => setUseBirthday(e.target.checked)} data-testid="book-birthday" />
              {t("book.birthday")}
            </label>
          )}

          {type !== "course" && (
            <div className="field">
              <label htmlFor="gc">{t("book.giftcard")}</label>
              <div className="btn-row" style={{ flexWrap: "nowrap" }}>
                <input id="gc" type="text" value={gcInput} onChange={(e) => setGcInput(e.target.value.toUpperCase())} placeholder="SABAI-GC-XXXX" data-testid="book-giftcard" />
                <button type="button" className="btn btn-sm btn-gold" onClick={() => setGcCode(gcInput.trim())} data-testid="book-giftcard-apply">
                  {t("book.giftcardCheck")}
                </button>
              </div>
              {quote?.giftCard && quote.giftCard.status === "ok" && (
                <div className="small" data-testid="book-giftcard-info">
                  {t("book.giftcardBalance", { b: formatBaht(Math.round(quote.giftCard.balance * 100)) })} ·{" "}
                  <span data-testid="book-giftcard-after">{t("book.giftcardAfter", { b: formatBaht(Math.round(quote.giftCard.balanceAfter * 100)) })}</span>
                </div>
              )}
              {quote?.giftCardError && (
                <div className="alert alert-error" role="alert" data-testid="book-giftcard-error" data-error-code={quote.giftCardError.code}>
                  {quote.giftCardError.message}
                </div>
              )}
            </div>
          )}

          {type !== "course" && (
            <>
              <label className="check">
                <input type="checkbox" checked={wantTransport} onChange={(e) => setWantTransport(e.target.checked)} data-testid="book-transport" />
                {t("book.transport")}
              </label>
              {wantTransport && (
                <div className="thai-band">
                  <div className="field">
                    <label htmlFor="hotel">{t("book.hotel")}</label>
                    <select id="hotel" value={hotelCode} onChange={(e) => setHotelCode(e.target.value)} data-testid="book-hotel">
                      <option value="">{t("book.hotelOther")}</option>
                      {props.hotels.map((h) => (
                        <option key={h.code} value={h.code}>
                          {h.name} · {h.distanceKm.toFixed(1)} {t("common.km")}
                        </option>
                      ))}
                    </select>
                  </div>
                  {!hotelCode && (
                    <div className="field">
                      <label htmlFor="dist">{t("book.distance")}</label>
                      <input id="dist" type="number" inputMode="decimal" step="0.1" min="0" value={distance} onChange={(e) => setDistance(e.target.value)} data-testid="book-distance" />
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          <ErrorBox e={quoteErr} testid="book-quote-error" />
          {quote && (
            <p className="price" data-testid="book-quote-total" aria-live="polite">
              {t("line.total")}: {quote.totalLabel}
            </p>
          )}
          <ErrorBox e={error} />
          <div className="btn-row">
            <button type="button" className="btn btn-ghost" onClick={() => setStep(2)} data-testid="book-back-3">
              {t("book.back")}
            </button>
            <button type="button" className="btn" disabled={!quote} onClick={next3} data-testid="book-next-3">
              {t("book.next")}
            </button>
          </div>
        </section>
      )}

      {step === 4 && quote && (
        <section className="card" aria-labelledby="s4" data-testid="book-summary">
          <h2 id="s4">
            4. {t("book.summary")}
          </h2>
          <p>
            <strong data-testid="summary-service">{quote.service.name}</strong> · {t(`type.${type}`)} · {peopleN} {t("common.people")}
          </p>
          <p data-testid="summary-when">
            {t("book.when")}: {quote.whenLabel}
          </p>
          <div className="thai-band">
            <strong>{t("book.herbsConfirm")}</strong>
            <ul className="chips" data-testid="book-herbs" style={{ marginTop: 6 }}>
              {quote.service.herbs.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>
          </div>
          <table className="summary-lines" data-testid="summary-lines">
            <tbody>
              {quote.lines.map((l) => (
                <tr key={l.key} className={l.key === "total" ? "total" : ""} data-testid={`summary-line-${l.key}`}>
                  <td>{l.label}</td>
                  <td data-testid={`summary-amount-${l.key}`} data-amount={l.amount}>
                    {l.display}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {quote.loggedIn && type !== "course" && (
            <p className="small muted" data-testid="book-earn-points">
              {t("line.earn")}: {quote.pointsToEarn}
            </p>
          )}
          {quote.course && (
            <p className="small muted" data-testid="book-course-after">
              {t("wallet.remaining", { r: quote.course.remainingAfter, t: 11 })}
            </p>
          )}
          <p className="price" data-testid="summary-total" data-amount={quote.total}>
            {t("line.total")}: {quote.totalLabel}
          </p>
          <ErrorBox e={error} />
          <div className="btn-row">
            <button type="button" className="btn btn-ghost" onClick={() => setStep(3)} data-testid="book-back-4">
              {t("book.back")}
            </button>
            <button type="button" className="btn btn-gold" onClick={confirm} disabled={busy} data-testid="book-confirm">
              {t("book.confirm")}
            </button>
          </div>
        </section>
      )}

      {tour && <Tour360 src={props.panorama} onClose={() => setTour(false)} />}
    </div>
  );
}
