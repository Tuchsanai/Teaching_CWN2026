"use client";

import { useState } from "react";
import { api, useApp, useReady } from "@/components/AppProvider";
import { Icon } from "@/components/Ornament";
import { PageHead } from "@/components/Shared";
import { GIFT_DESIGNS, GIFT_MAX, GIFT_MIN } from "@/lib/rules";
import { errorText, type DictKey } from "@/lib/i18n";
import { formatBaht, formatDate } from "@/lib/time";

type Card = { code: string; amount: number; balance?: number; design: string; channel?: string; recipient?: string; recipientName?: string; senderName?: string; message?: string; purchasedOn: string; expiresOn: string };
const IMG: Record<string, string> = { orchid: "/assets/gift/giftcard-orchid.jpg", lotus: "/assets/gift/giftcard-lotus.jpg", gold: "/assets/gift/giftcard-gold.jpg" };

function GiftVisual({ design, amount, code, expires }: { design: string; amount: number; code?: string; expires?: string }) {
  const { t, lang } = useApp();
  return (
    <div className={`giftcard giftcard--${design}`} data-testid="gift-preview">
      <img src={IMG[design] ?? IMG.gold} alt={t(`design_${design}` as DictKey)} />
      <div className="giftcard__body">
        <span className="giftcard__brand">Sabai Jai Wellness Spa</span>
        <span className="giftcard__amount">{formatBaht(amount || 0)}</span>
        <span className="giftcard__foot">
          <span>{code ?? "GIFT CARD"}</span>
          <span data-testid={code ? "gift-card-expiry" : undefined}>{expires ? t("gift_valid_until", { date: formatDate(expires, lang) }) : "365"}</span>
        </span>
      </div>
    </div>
  );
}

export default function GiftCardsPage() {
  const { t, lang, user } = useApp();
  const [amount, setAmount] = useState<string>("2000");
  const [design, setDesign] = useState<string | null>(null);
  const [channel, setChannel] = useState<"line" | "email" | null>(null);
  const [recipient, setRecipient] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [sender, setSender] = useState(user ? (lang === "th" ? user.name : user.nameEn) : "");
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<Card | null>(null);

  const [checkCode, setCheckCode] = useState("");
  const [check, setCheck] = useState<{ card: Card; status: string } | null>(null);
  const [checkError, setCheckError] = useState<string | null>(null);
  useReady(true);

  const amt = Number(amount);
  const amountBad = amount !== "" && (!Number.isInteger(amt) || amt < GIFT_MIN || amt > GIFT_MAX);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    // BR-17 — validate in the browser too, the server checks again
    if (!Number.isInteger(amt) || amt < GIFT_MIN || amt > GIFT_MAX) return setError(errorText(lang, "GIFT_AMOUNT"));
    if (!design) return setError(errorText(lang, "GIFT_DESIGN"));
    if (!channel) return setError(errorText(lang, "GIFT_CHANNEL"));
    setBusy(true);
    const r = await api<{ ok: boolean; giftCard?: Card; error?: string }>("/api/giftcards", {
      method: "POST",
      json: { amount: amt, design, channel, recipient, recipientName, senderName: sender, message },
    });
    setBusy(false);
    if (r.ok && r.giftCard) setResult(r.giftCard);
    else setError(errorText(lang, r.error ?? "SERVER"));
  };

  const doCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    setCheck(null);
    setCheckError(null);
    const code = checkCode.trim();
    if (!code) return;
    const r = await api<{ ok: boolean; giftCard?: Card; status?: string; error?: string }>(`/api/giftcards/${encodeURIComponent(code)}`);
    if (r.giftCard) setCheck({ card: r.giftCard, status: r.status ?? "valid" });
    if (r.error) setCheckError(errorText(lang, r.error));
  };

  return (
    <>
      <PageHead eyebrow={t("gift_eyebrow")} title={t("gift_title")} lead={t("gift_lead")} image="/assets/gift/giftcard-lotus.jpg" />
      <section className="section">
        <div className="container split" style={{ alignItems: "start" }}>
          <div className="sticky-desktop">
            <p className="label">{t("gift_preview")}</p>
            <GiftVisual design={result?.design ?? design ?? "gold"} amount={result?.amount ?? (amountBad ? 0 : amt)} code={result?.code} expires={result?.expiresOn} />
            {result && (
              <div className="mt-2" data-testid="gift-success">
                <p className="alert alert--ok"><Icon name="check" /> {t("gift_success")}</p>
                <dl className="summary-list mt-1">
                  <div><dt>{t("gift_code")}</dt><dd className="code-badge" style={{ fontSize: "1rem" }} data-testid="gift-code">{result.code}</dd></div>
                  <div><dt>{t("gift_value")}</dt><dd data-testid="gift-amount-result">{formatBaht(result.amount)}</dd></div>
                  <div><dt>{t("wallet_purchased", { date: "" }).trim()}</dt><dd>{formatDate(result.purchasedOn, lang)}</dd></div>
                  <div><dt>{t("gift_valid_until", { date: "" }).trim()}</dt><dd data-testid="gift-expiry" data-date={result.expiresOn}>{formatDate(result.expiresOn, lang)}</dd></div>
                </dl>
                <div className="sent-msg mt-2" data-testid="gift-sent-message">
                  <p className="sent-msg__via">
                    <Icon name="send" size={16} /> {t("gift_sent_via", { channel: result.channel === "line" ? "LINE" : t("channel_email"), to: result.recipient ?? "" })}
                  </p>
                  <p style={{ margin: 0 }}>
                    {t("gift_sent_body", { sender: result.senderName || "—", amount: formatBaht(result.amount), name: result.recipientName || "", code: result.code, date: formatDate(result.expiresOn, lang) })}
                  </p>
                  {result.message && <p style={{ margin: "6px 0 0", fontStyle: "italic" }}>“{result.message}”</p>}
                </div>
                <p className="hint mt-1" data-testid="gift-simulated-note">{t("gift_simulated")}</p>
                <button type="button" className="btn btn--ghost mt-1" onClick={() => setResult(null)} data-testid="gift-again">{t("book_another")}</button>
              </div>
            )}
          </div>

          <div>
            <form className="card card--pad" onSubmit={submit} noValidate data-testid="gift-form">
              <div className="field">
                <label htmlFor="g-amount">{t("gift_amount")}</label>
                <input id="g-amount" className="input" type="number" inputMode="numeric" min={GIFT_MIN} max={GIFT_MAX} step={1} value={amount} onChange={(e) => setAmount(e.target.value)} aria-invalid={amountBad} data-testid="gift-amount" />
                <div className="row">
                  {[500, 1000, 2000, 5000, 10000].map((v) => (
                    <button key={v} type="button" className={`chip ${amt === v ? "is-active" : ""}`} onClick={() => setAmount(String(v))} data-testid={`gift-quick-${v}`}>{formatBaht(v)}</button>
                  ))}
                </div>
              </div>
              <fieldset className="field" style={{ border: 0, padding: 0, margin: "0 0 16px" }}>
                <legend className="label" style={{ marginBottom: 6 }}>{t("gift_design")}</legend>
                <div className="gift-designs">
                  {GIFT_DESIGNS.map((d) => (
                    <button key={d} type="button" className={`gift-design ${design === d ? "is-active" : ""}`} aria-pressed={design === d} onClick={() => setDesign(d)} data-testid={`gift-design-${d}`}>
                      <img src={IMG[d]} alt={t(`design_${d}` as DictKey)} loading="lazy" />
                      <span>{t(`design_${d}` as DictKey)}</span>
                    </button>
                  ))}
                </div>
              </fieldset>
              <fieldset className="field" style={{ border: 0, padding: 0, margin: "0 0 16px" }}>
                <legend className="label" style={{ marginBottom: 6 }}>{t("gift_channel")}</legend>
                <div className="row">
                  <button type="button" className={`chip ${channel === "line" ? "is-active" : ""}`} aria-pressed={channel === "line"} onClick={() => setChannel("line")} data-testid="gift-channel-line">LINE</button>
                  <button type="button" className={`chip ${channel === "email" ? "is-active" : ""}`} aria-pressed={channel === "email"} onClick={() => setChannel("email")} data-testid="gift-channel-email">{t("channel_email")}</button>
                </div>
              </fieldset>
              <div className="grid grid--2" style={{ gap: 12 }}>
                <div className="field">
                  <label htmlFor="g-to">{channel === "email" ? t("gift_recipient_email") : t("gift_recipient_line")}</label>
                  <input id="g-to" className="input" type={channel === "email" ? "email" : "text"} value={recipient} onChange={(e) => setRecipient(e.target.value)} data-testid="gift-recipient" />
                </div>
                <div className="field">
                  <label htmlFor="g-name">{t("gift_recipient_name")}</label>
                  <input id="g-name" className="input" value={recipientName} onChange={(e) => setRecipientName(e.target.value)} data-testid="gift-recipient-name" />
                </div>
              </div>
              <div className="field">
                <label htmlFor="g-from">{t("gift_sender")}</label>
                <input id="g-from" className="input" value={sender} onChange={(e) => setSender(e.target.value)} data-testid="gift-sender" />
              </div>
              <div className="field">
                <label htmlFor="g-msg">{t("gift_message")}</label>
                <textarea id="g-msg" className="textarea" value={message} maxLength={300} onChange={(e) => setMessage(e.target.value)} data-testid="gift-message" />
              </div>
              {error && <p className="alert alert--error" role="alert" data-testid="gift-error">{error}</p>}
              <button type="submit" className="btn btn--gold btn--lg btn--block" disabled={busy} data-testid="gift-submit">
                <Icon name="gift" /> {t("gift_submit")}
              </button>
            </form>

            <form className="card card--pad mt-2" onSubmit={doCheck} data-testid="gift-check-form">
              <h2 style={{ fontSize: "1.25rem" }}>{t("gift_check_title")}</h2>
              <div className="row">
                <input className="input" style={{ flex: 1, minWidth: 180, textTransform: "uppercase" }} value={checkCode} onChange={(e) => setCheckCode(e.target.value)} placeholder="GIFT-2000-ORCHID" aria-label={t("gift_code")} data-testid="gift-check-code" />
                <button type="submit" className="btn btn--green" data-testid="gift-check-submit">{t("gift_check_btn")}</button>
              </div>
              {check && (
                <dl className="summary-list mt-2" data-testid="gift-check-result" data-status={check.status}>
                  <div><dt>{t("gift_code")}</dt><dd>{check.card.code}</dd></div>
                  <div><dt>{t("gift_balance")}</dt><dd data-testid="gift-check-balance">{formatBaht(check.card.balance ?? 0)}</dd></div>
                  <div><dt>{t("gift_valid_until", { date: "" }).trim()}</dt><dd data-testid="gift-check-expiry" data-date={check.card.expiresOn}>{formatDate(check.card.expiresOn, lang)}</dd></div>
                  {check.status === "valid" && <div><dt /><dd><span className="badge badge--ok" data-testid="gift-check-valid">{t("gift_valid")}</span></dd></div>}
                </dl>
              )}
              {checkError && <p className="alert alert--error mt-1" role="alert" data-testid="gift-check-error">{checkError}</p>}
            </form>
          </div>
        </div>
      </section>
    </>
  );
}
