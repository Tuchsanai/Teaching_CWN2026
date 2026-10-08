"use client";

import Link from "next/link";
import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, useApp, useReady } from "@/components/AppProvider";
import { Icon } from "@/components/Ornament";
import { AllergyWarning, Calendar, HerbPills, Loader, PageHead, PriceSummary, svcName, useServices } from "@/components/Shared";
import { COURSE_SERVICE, GROUP_MAX, kindForPeople, type Quote } from "@/lib/rules";
import { errorText, pick } from "@/lib/i18n";
import { formatBaht, formatDate, hhmmToMin, minToHHMM } from "@/lib/time";

type Slot = { time: string; status: "free" | "booked" | "closed" };
type Ther = { id: number; name_th: string; name_en: string; name_zh: string; rating: number | null };
type Wallet = { canBookWithCourse: boolean; courseProblem: string | null; courses: { left: number; expired: boolean; expiresOn: string }[] };
type Booked = { code: string; date: string; time: string; endTime: string; people: number; therapists: number[]; room: string | null; quote: Quote };

export default function BookPage() {
  return (
    <Suspense fallback={<Loader />}>
      <BookInner />
    </Suspense>
  );
}

function BookInner() {
  const { t, lang, config, refreshConfig, user, userLoaded, refreshUser } = useApp();
  const sp = useSearchParams();
  const services = useServices();

  const [service, setService] = useState<string | null>(sp.get("service"));
  const [people, setPeople] = useState<number>(Math.max(1, Number(sp.get("people")) || 1));
  const [therapistId, setTherapistId] = useState<number | null>(Number(sp.get("therapist")) || null);
  const [date, setDate] = useState<string | null>(null);
  const [time, setTime] = useState<string | null>(null);
  const [transport, setTransport] = useState(sp.get("service") === "bangkok-relax");
  const [hotelId, setHotelId] = useState<number | null>(null);
  const [redeemSets, setRedeemSets] = useState(0);
  const [useBirthday, setUseBirthday] = useState(true);
  const [payWith, setPayWith] = useState<"cash" | "course">(sp.get("pay") === "course" ? "course" : "cash");
  const [giftInput, setGiftInput] = useState("");
  const [gift, setGift] = useState<{ code: string; balance: number; expiresOn: string } | null>(null);
  const [giftError, setGiftError] = useState<string | null>(null);
  const [guestName, setGuestName] = useState("");
  const [guestPhone, setGuestPhone] = useState("");

  const [slots, setSlots] = useState<Slot[] | null>(null);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [slotError, setSlotError] = useState<string | null>(null);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [issues, setIssues] = useState<{ code: string; message: string }[]>([]);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [therapists, setTherapists] = useState<Ther[] | null>(null);
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<Booked | null>(null);
  const [cfgReady, setCfgReady] = useState(false);

  const svc = useMemo(() => services?.find((s) => s.slug === service) ?? null, [services, service]);
  const kind = kindForPeople(people);
  const peopleOk = kind !== null && kind !== "call";

  useEffect(() => {
    refreshConfig().then(() => setCfgReady(true));
    api<{ ok: boolean; therapists: Ther[] }>("/api/therapists").then((r) => r.ok && setTherapists(r.therapists));
  }, [refreshConfig]);

  useEffect(() => {
    if (user) api<Wallet & { ok: boolean }>("/api/wallet").then((r) => r.ok && setWallet(r));
    else setWallet(null);
  }, [user]);

  // reset dependent choices
  useEffect(() => {
    setTime(null);
    setSlotError(null);
  }, [service, date, people, therapistId]);

  // FR-01: open slots for the chosen date
  const loadSlots = useCallback(async () => {
    if (!service || !date || !peopleOk) {
      setSlots(null);
      return;
    }
    setSlotsLoading(true);
    const qs = new URLSearchParams({ service, date, people: String(people) });
    if (therapistId) qs.set("therapistId", String(therapistId));
    const r = await api<{ ok: boolean; slots: Slot[]; error?: string }>(`/api/availability?${qs}`);
    setSlots(r.ok ? r.slots : []);
    if (!r.ok && r.error) setSlotError(errorText(lang, r.error));
    setSlotsLoading(false);
  }, [service, date, people, therapistId, peopleOk, lang]);
  useEffect(() => {
    loadSlots();
  }, [loadSlots]);

  // FR-06: live price breakdown
  const qSeq = useRef(0);
  useEffect(() => {
    if (!service || !peopleOk) {
      setQuote(null);
      setIssues([]);
      return;
    }
    const seq = ++qSeq.current;
    setQuoteLoading(true);
    const timer = setTimeout(async () => {
      const r = await api<{ ok: boolean; quote: Quote; issues: { code: string; message: string }[] }>("/api/quote", {
        method: "POST",
        json: { service, people, transport, hotelId, redeemSets, useBirthday: useBirthday && user?.birthday === "eligible", payWith, giftCode: gift?.code ?? null },
      });
      if (seq !== qSeq.current) return;
      if (r.ok) {
        setQuote(r.quote);
        setIssues(r.issues);
      }
      setQuoteLoading(false);
    }, 120);
    return () => clearTimeout(timer);
  }, [service, people, peopleOk, transport, hotelId, redeemSets, useBirthday, payWith, gift, user]);

  useEffect(() => {
    if (payWith === "course" && (service !== COURSE_SERVICE || people !== 1)) setPayWith("cash");
  }, [service, people, payWith]);

  useReady(!!services && cfgReady && userLoaded && !!therapists);

  if (!services || !config) return <Loader />;

  const applyGift = async () => {
    setGiftError(null);
    const code = giftInput.trim().toUpperCase();
    if (!code) return;
    const r = await api<{ ok: boolean; usable?: boolean; error?: string; giftCard?: { code: string; balance: number; expiresOn: string } }>(`/api/giftcards/${encodeURIComponent(code)}`);
    if (r.ok && r.usable && r.giftCard) setGift({ code: r.giftCard.code, balance: r.giftCard.balance, expiresOn: r.giftCard.expiresOn });
    else {
      setGift(null);
      setGiftError(errorText(lang, r.error ?? "GIFT_NOT_FOUND"));
    }
  };

  const pickSlot = (s: Slot) => {
    setTime(s.time);
    setError(null);
    setSlotError(s.status === "booked" ? errorText(lang, "SLOT_TAKEN") : null);
  };

  const submit = async () => {
    setError(null);
    setSubmitting(true);
    const r = await api<{ ok: boolean; booking?: Booked; error?: string }>("/api/bookings", {
      method: "POST",
      json: {
        service, date, time, people, kind, therapistId, transport, hotelId, redeemSets,
        useBirthday: useBirthday && user?.birthday === "eligible", payWith, giftCode: gift?.code ?? null,
        guestName: user ? undefined : guestName, guestPhone: user ? undefined : guestPhone,
      },
    });
    setSubmitting(false);
    if (r.ok && r.booking) {
      setDone(r.booking);
      refreshUser();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      setError(errorText(lang, r.error ?? "SERVER"));
      if (r.error === "SLOT_TAKEN") loadSlots();
    }
  };

  const therName = (id: number) => {
    const x = therapists?.find((z) => z.id === id);
    return x ? pick(x, "name", lang) : `#${id}`;
  };

  if (done) {
    return (
      <>
        <PageHead eyebrow={t("book_eyebrow")} title={t("book_success")} />
        <section className="section">
          <div className="container--narrow">
            <div className="card success-card" data-testid="booking-success">
              <div className="tick"><Icon name="check" size={40} /></div>
              <h2>{t("book_success")}</h2>
              <p className="muted">{t("book_success_lead")}</p>
              <p className="small muted">{t("book_code")}</p>
              <p><span className="code-badge" data-testid="booking-code">{done.code}</span></p>
              <dl className="summary-list mt-2" style={{ maxWidth: 440, margin: "24px auto 0", textAlign: "left" }}>
                <div><dt>{t("service_col")}</dt><dd>{svc ? svcName(svc, lang) : service}</dd></div>
                <div><dt>{t("book_when")}</dt><dd data-testid="booking-success-when">{formatDate(done.date, lang, true)} · {done.time}–{done.endTime}</dd></div>
                <div><dt>{t("book_people")}</dt><dd>{t("people_n", { n: done.people })}</dd></div>
                <div><dt>{t("book_therapists_assigned")}</dt><dd data-testid="booking-success-therapists">{done.therapists.map(therName).join(", ")}</dd></div>
                {done.room && <div><dt>{t("book_room")}</dt><dd>Couple Suite</dd></div>}
                <div><dt>{t("price_total")}</dt><dd data-testid="booking-success-total">{formatBaht(done.quote.total)}</dd></div>
              </dl>
              <div className="row mt-3" style={{ justifyContent: "center" }}>
                <button type="button" className="btn btn--gold" onClick={() => { setDone(null); setTime(null); loadSlots(); }} data-testid="booking-another">{t("book_another")}</button>
                {user && <Link href="/account" className="btn btn--ghost" data-testid="booking-view-mine">{t("book_view_mine")}</Link>}
              </div>
            </div>
          </div>
        </section>
      </>
    );
  }

  const step1 = !!svc && peopleOk;
  const step2 = step1 && !!date;
  const step3 = step2 && !!time;
  const transportIssue = issues.find((i) => i.code === "TRANSPORT_TOO_FAR" || i.code === "HOTEL_REQUIRED");
  const maxSets = quote?.maxRedeemSets ?? 0;
  const courseLeft = wallet?.courses.find((c) => !c.expired)?.left ?? 0;
  const courseUsable = !!wallet?.canBookWithCourse && people === 1;
  const blocking = issues.filter((i) => i.code !== "HOTEL_REQUIRED" || transport);
  const canSubmit = step3 && !submitting && (!!user || (guestName.trim() && guestPhone.trim()));
  const endTime = time && svc ? minToHHMM((hhmmToMin(time) ?? 0) + svc.duration) : null;

  return (
    <>
      <PageHead eyebrow={t("book_eyebrow")} title={t("book_title")} lead={t("book_lead")} image="/assets/rooms/room-thai-massage.jpg" />
      <section className="section" style={{ paddingTop: 40 }}>
        <div className="container">
          <div className="steps-bar" aria-hidden="true">
            <span className={step1 ? "is-on" : ""} />
            <span className={step2 ? "is-on" : ""} />
            <span className={step3 ? "is-on" : ""} />
            <span className={step3 && blocking.length === 0 ? "is-on" : ""} />
          </div>
          <div className="book-layout">
            <div>
              {/* STEP 1 — service & guests */}
              <section className={`card step ${step1 ? "is-done" : ""}`} aria-labelledby="s1">
                <div className="step__head">
                  <span className="step__num">1</span>
                  <h2 id="s1">{t("step_1")}</h2>
                </div>
                <div className="svc-pick" role="radiogroup" aria-label={t("step_1")}>
                  {services.map((s) => (
                    <button key={s.slug} type="button" role="radio" aria-checked={service === s.slug} className={`svc-opt ${service === s.slug ? "is-active" : ""}`} onClick={() => setService(s.slug)} data-testid={`service-option-${s.slug}`}>
                      <img src={s.image} alt={svcName(s, lang)} loading="lazy" />
                      <span>
                        <b>{svcName(s, lang)}</b>
                        <small>{t("minutes", { n: s.duration })} · {formatBaht(s.price)}{s.is_package ? t("per_person") : ""}</small>
                      </span>
                    </button>
                  ))}
                </div>
                {svc && (
                  <div className="mt-2">
                    <HerbPills herbs={svc.herbs} testid="booking-herbs" />
                    <div className="mt-1"><AllergyWarning testid="booking-allergy" /></div>
                  </div>
                )}

                <div className="mt-2 row row--between">
                  <label className="label" htmlFor="people">{t("book_people")}</label>
                  <div className="stepper">
                    <button type="button" onClick={() => setPeople((p) => Math.max(1, p - 1))} disabled={people <= 1} aria-label={t("book_people_minus")} data-testid="booking-people-minus">−</button>
                    <input
                      id="people"
                      type="number"
                      min={1}
                      inputMode="numeric"
                      value={people}
                      onChange={(e) => setPeople(Math.max(1, Math.floor(Number(e.target.value) || 1)))}
                      data-testid="booking-people"
                    />
                    <button type="button" onClick={() => setPeople((p) => p + 1)} aria-label={t("book_people_plus")} data-testid="booking-people-plus">+</button>
                  </div>
                </div>
                <div className="kind-row" role="radiogroup" aria-label={t("book_people")}>
                  <button type="button" role="radio" aria-checked={kind === "single"} disabled={people !== 1} className={`kind-opt ${kind === "single" ? "is-active" : ""}`} onClick={() => setPeople(1)} data-testid="booking-kind-single">
                    <b>{t("kind_single")}</b><small>{t("kind_single_sub")}</small>
                  </button>
                  <button type="button" role="radio" aria-checked={kind === "couple"} disabled={people !== 2} className={`kind-opt ${kind === "couple" ? "is-active" : ""}`} onClick={() => setPeople(2)} data-testid="booking-kind-couple">
                    <b>{t("kind_couple")}</b><small>{t("kind_couple_sub")}</small>
                  </button>
                  <button type="button" role="radio" aria-checked={kind === "group"} disabled={people < 3 || people > GROUP_MAX} className={`kind-opt ${kind === "group" ? "is-active" : ""}`} onClick={() => undefined} data-testid="booking-kind-group">
                    <b>{t("kind_group")}</b><small>{t("kind_group_sub")}</small>
                  </button>
                </div>
                {kind === "call" && (
                  <p className="alert alert--error mt-1" role="alert" data-testid="booking-group-error">
                    <Icon name="phone" /> {errorText(lang, "GROUP_TOO_LARGE")}
                  </p>
                )}

                <div className="field mt-2">
                  <label htmlFor="ther">{t("book_therapist")}</label>
                  <select id="ther" className="select" value={therapistId ?? ""} onChange={(e) => setTherapistId(Number(e.target.value) || null)} data-testid="booking-therapist">
                    <option value="">{t("book_any_therapist")}</option>
                    {(therapists ?? []).map((x) => (
                      <option key={x.id} value={x.id}>
                        {pick(x, "name", lang)} {x.rating !== null ? `★ ${x.rating.toFixed(1)}` : ""}
                      </option>
                    ))}
                  </select>
                  {people > 1 && <span className="hint">{t("book_therapist_hint")}</span>}
                </div>
              </section>

              {/* STEP 2 — date */}
              <section className={`card step ${step2 ? "is-done" : ""}`} aria-labelledby="s2">
                <div className="step__head">
                  <span className="step__num">2</span>
                  <h2 id="s2">{t("step_2")}</h2>
                </div>
                <p className="hint" data-testid="booking-date-range">
                  {t("book_date_range", { min: formatDate(config.bookable.from, lang), max: formatDate(config.bookable.to, lang) })}
                </p>
                <Calendar today={config.today} min={config.bookable.from} max={config.bookable.to} value={date} onChange={setDate} />
              </section>

              {/* STEP 3 — time */}
              <section className={`card step ${step3 ? "is-done" : ""}`} aria-labelledby="s3">
                <div className="step__head">
                  <span className="step__num">3</span>
                  <h2 id="s3">{t("step_3")}</h2>
                </div>
                {!svc ? (
                  <p className="muted">{t("book_pick_service")}</p>
                ) : !date || !peopleOk ? (
                  <p className="muted">{t("book_pick_date_first")}</p>
                ) : slotsLoading && !slots ? (
                  <Loader />
                ) : (
                  <>
                    <div className="slots" role="radiogroup" aria-label={t("step_3")} data-testid="slot-list">
                      {(slots ?? []).map((s) => (
                        <button
                          key={s.time}
                          type="button"
                          role="radio"
                          aria-checked={time === s.time}
                          className={`slot ${s.status === "booked" ? "is-booked" : ""} ${time === s.time ? "is-selected" : ""}`}
                          disabled={s.status === "closed"}
                          title={s.status === "closed" ? t("slot_closed") : s.status === "booked" ? t("slot_booked") : t("slot_legend_free")}
                          onClick={() => pickSlot(s)}
                          data-testid={`slot-${s.time.replace(":", "-")}`}
                          data-status={s.status}
                        >
                          {s.time}
                          {s.status !== "free" && <small>{s.status === "booked" ? t("slot_booked") : t("slot_closed")}</small>}
                        </button>
                      ))}
                    </div>
                    <div className="slot-legend" aria-hidden="true">
                      <span><i />{t("slot_legend_free")}</span>
                      <span><i className="b" />{t("slot_booked")}</span>
                    </div>
                    {time && endTime && <p className="hint mt-1" data-testid="booking-end-time">{t("book_ends_at", { t: endTime })}</p>}
                    {slotError && (
                      <p className="alert alert--error mt-1" role="alert" data-testid="slot-error">{slotError}</p>
                    )}
                  </>
                )}
              </section>

              {/* STEP 4 — extras & confirm */}
              <section className="card step" aria-labelledby="s4">
                <div className="step__head">
                  <span className="step__num">4</span>
                  <h2 id="s4">{t("step_4")}</h2>
                </div>

                {/* transport (FR-19) */}
                <label className="check">
                  <input type="checkbox" checked={transport} onChange={(e) => setTransport(e.target.checked)} data-testid="booking-transport" />
                  <span>
                    <b>{t("book_transport")}</b>
                    <br />
                    <span className="hint">{t("transport_rules")}</span>
                  </span>
                </label>
                {transport && (
                  <div className="field">
                    <label htmlFor="hotel">{t("book_hotel")}</label>
                    <select id="hotel" className="select" value={hotelId ?? ""} onChange={(e) => setHotelId(Number(e.target.value) || null)} data-testid="booking-hotel">
                      <option value="">{t("book_hotel_pick")}</option>
                      {config.hotels.map((h) => (
                        <option key={h.id} value={h.id}>
                          {lang === "zh" ? h.nameZh : h.name} — {t("km_n", { n: h.distanceKm.toFixed(1) })}
                        </option>
                      ))}
                    </select>
                    {quote && hotelId && quote.distanceKm !== null && (
                      <p className="hint" data-testid="transport-info">
                        {t("book_distance")}: <b data-testid="transport-distance">{t("km_n", { n: quote.distanceKm.toFixed(1) })}</b> · {t("book_cars")}:{" "}
                        <b data-testid="transport-cars">{t("cars_n", { n: quote.cars })}</b> · {t("price_transport")}:{" "}
                        <b data-testid="transport-fee">{quote.transportOk ? (quote.transportFee === 0 ? t("free") : formatBaht(quote.transportFee)) : "—"}</b>
                      </p>
                    )}
                    {transportIssue && transportIssue.code === "TRANSPORT_TOO_FAR" && (
                      <p className="alert alert--error" role="alert" data-testid="transport-error">{errorText(lang, "TRANSPORT_TOO_FAR")}</p>
                    )}
                  </div>
                )}

                {/* member benefits (FR-09 … FR-13) */}
                <h3 className="mt-2">{t("book_member_box")}</h3>
                {!user ? (
                  <>
                    <p className="alert alert--info" data-testid="booking-login-hint">
                      <Icon name="user" /> <span>{t("book_login_hint")} <Link href="/login?next=/book">{t("nav_login")}</Link></span>
                    </p>
                    <div className="grid grid--2" style={{ gap: 12 }}>
                      <div className="field">
                        <label htmlFor="gname">{t("book_guest_name")}</label>
                        <input id="gname" className="input" value={guestName} onChange={(e) => setGuestName(e.target.value)} autoComplete="name" data-testid="booking-guest-name" />
                      </div>
                      <div className="field">
                        <label htmlFor="gphone">{t("book_guest_phone")}</label>
                        <input id="gphone" className="input" type="tel" value={guestPhone} onChange={(e) => setGuestPhone(e.target.value)} autoComplete="tel" placeholder="08x-xxx-xxxx" data-testid="booking-guest-phone" />
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <p className="row" data-testid="booking-member">
                      <span className={`tier-badge tier-badge--${user.tier}`} data-testid="booking-member-tier">{t(`tier_${user.tier}`)}</span>
                      <span data-testid="booking-points-balance">{t("book_points_have", { n: user.points })}</span>
                    </p>
                    <div className="field">
                      <label htmlFor="redeem">{t("book_redeem")}</label>
                      <div className="row">
                        <select id="redeem" className="select" style={{ maxWidth: 220 }} value={Math.min(redeemSets, maxSets)} disabled={maxSets === 0} onChange={(e) => setRedeemSets(Number(e.target.value))} data-testid="booking-redeem">
                          {Array.from({ length: maxSets + 1 }, (_, i) => (
                            <option key={i} value={i}>
                              {t("book_redeem_sets", { n: i })} (−{formatBaht(i * 50)})
                            </option>
                          ))}
                        </select>
                        <button type="button" className="btn btn--ghost btn--sm" disabled={maxSets === 0} onClick={() => setRedeemSets(maxSets)} data-testid="booking-redeem-max">
                          {t("book_redeem_max")}
                        </button>
                      </div>
                      {user.points < 100 && <span className="hint" data-testid="booking-redeem-hint">{t("book_redeem_min")}</span>}
                    </div>
                    {user.birthday === "eligible" && (
                      <label className="check">
                        <input type="checkbox" checked={useBirthday} onChange={(e) => setUseBirthday(e.target.checked)} data-testid="booking-birthday" />
                        <span>{t("book_use_birthday")}</span>
                      </label>
                    )}
                  </>
                )}

                {/* payment */}
                <h3 className="mt-2">{t("book_pay")}</h3>
                <div className="row" role="radiogroup" aria-label={t("book_pay")}>
                  <button type="button" role="radio" aria-checked={payWith === "cash"} className={`chip ${payWith === "cash" ? "is-active" : ""}`} onClick={() => setPayWith("cash")} data-testid="booking-pay-cash">
                    {t("pay_cash")}
                  </button>
                  {user && service === COURSE_SERVICE && (
                    <button type="button" role="radio" aria-checked={payWith === "course"} className={`chip ${payWith === "course" ? "is-active" : ""}`} disabled={!courseUsable} onClick={() => setPayWith("course")} data-testid="booking-pay-course">
                      {t("pay_course")} · {t("pay_course_left", { n: courseLeft })}
                    </button>
                  )}
                </div>
                {user && service === COURSE_SERVICE && !courseUsable && wallet && (
                  <p className="hint" data-testid="booking-course-hint">{wallet.courseProblem ? errorText(lang, wallet.courseProblem) : t("pay_course_na")}</p>
                )}

                <div className="field mt-2">
                  <label htmlFor="gift">{t("book_gift_code")}</label>
                  <div className="row">
                    <input id="gift" className="input" style={{ maxWidth: 260, textTransform: "uppercase" }} value={giftInput} onChange={(e) => setGiftInput(e.target.value)} placeholder="GIFT-XXXX" data-testid="booking-gift-code" />
                    {gift ? (
                      <button type="button" className="btn btn--ghost btn--sm" onClick={() => { setGift(null); setGiftInput(""); }} data-testid="booking-gift-remove">{t("book_gift_remove")}</button>
                    ) : (
                      <button type="button" className="btn btn--green btn--sm" onClick={applyGift} data-testid="booking-gift-apply">{t("book_gift_apply")}</button>
                    )}
                  </div>
                  {gift && <p className="alert alert--ok" data-testid="booking-gift-status">{t("book_gift_ok", { amount: formatBaht(gift.balance), date: formatDate(gift.expiresOn, lang) })}</p>}
                  {giftError && <p className="alert alert--error" role="alert" data-testid="booking-gift-error">{giftError}</p>}
                </div>

                {issues.filter((i) => !["TRANSPORT_TOO_FAR", "HOTEL_REQUIRED"].includes(i.code)).map((i) => (
                  <p key={i.code} className="alert alert--error" role="alert" data-testid={`booking-issue-${i.code}`}>{errorText(lang, i.code)}</p>
                ))}

                {error && (
                  <p className="alert alert--error mt-1" role="alert" data-testid="booking-error">
                    {error}
                  </p>
                )}
                <button type="button" className="btn btn--gold btn--lg btn--block mt-2" onClick={submit} disabled={!canSubmit} data-testid="booking-submit">
                  {submitting ? t("book_submitting") : t("book_submit")} <Icon name="check" />
                </button>
              </section>
            </div>

            {/* aside — summary + price */}
            <aside className="book-aside" aria-label={t("book_summary")}>
              <section className="card card--pad">
                <h2 style={{ fontSize: "1.2rem" }}>{t("book_summary")}</h2>
                <dl className="summary-list" data-testid="booking-summary">
                  <div><dt>{t("service_col")}</dt><dd data-testid="summary-service">{svc ? svcName(svc, lang) : "—"}</dd></div>
                  <div><dt>{t("book_people")}</dt><dd data-testid="summary-people">{t("people_n", { n: people })}</dd></div>
                  <div><dt>{t("date_col")}</dt><dd data-testid="summary-date">{date ? formatDate(date, lang, true) : "—"}</dd></div>
                  <div><dt>{t("step_3")}</dt><dd data-testid="summary-time">{time ? `${time}${endTime ? `–${endTime}` : ""}` : "—"}</dd></div>
                </dl>
              </section>
              <PriceSummary q={quote} member={!!user} loading={quoteLoading} />
            </aside>
          </div>
        </div>
      </section>
    </>
  );
}

