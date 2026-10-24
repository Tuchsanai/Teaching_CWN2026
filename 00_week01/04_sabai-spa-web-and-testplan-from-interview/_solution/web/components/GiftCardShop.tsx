"use client";

import { useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

const DESIGNS = ["orchid", "lotus", "gold"] as const;

interface Bought {
  code: string;
  valueLabel: string;
  expiresLabel: string;
  sentMessage: string;
  preview: string;
  design: string;
}

interface Info {
  code: string;
  balanceLabel: string;
  expiresLabel: string;
  status: string;
  message: string;
}

/** FR-19 ซื้อ Gift Card (มูลค่า BR-15 · 3 ลาย · LINE/email แบบจำลอง) · FR-20 ตรวจยอด/วันหมดอายุ */
export function GiftCardShop({ images }: { images: Record<string, string> }) {
  const { t } = useI18n();
  const [value, setValue] = useState("1000");
  const [design, setDesign] = useState<(typeof DESIGNS)[number]>("orchid");
  const [channel, setChannel] = useState<"line" | "email">("line");
  const [recipient, setRecipient] = useState("");
  const [message, setMessage] = useState("");
  const [bought, setBought] = useState<Bought | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [info, setInfo] = useState<Info | null>(null);
  const [infoErr, setInfoErr] = useState<string | null>(null);

  const buy = async () => {
    setErr(null);
    setBought(null);
    const r = await fetch("/api/giftcards", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value: value.trim() === "" ? null : Number(value), design, channel, recipient, message }),
    });
    const j = await r.json();
    if (r.status === 201) setBought(j);
    else setErr(j.message);
  };

  const check = async () => {
    setInfo(null);
    setInfoErr(null);
    const r = await fetch(`/api/giftcards/${encodeURIComponent(code.trim())}`);
    const j = await r.json();
    if (r.ok) setInfo(j);
    else setInfoErr(j.message);
  };

  return (
    <>
      <section className="card" aria-labelledby="gc-buy">
        <h2 id="gc-buy">{t("gift.buy")}</h2>
        <div className="field">
          <label htmlFor="gc-value">{t("gift.value")}</label>
          <input id="gc-value" type="number" inputMode="numeric" min={500} max={10000} step={1} value={value} onChange={(e) => setValue(e.target.value)} data-testid="gc-value" />
        </div>
        <fieldset style={{ border: 0, padding: 0, margin: "0 0 14px" }}>
          <legend style={{ fontWeight: 600, marginBottom: 6 }}>{t("gift.design")}</legend>
          <div className="choice-grid">
            {DESIGNS.map((d) => (
              <label key={d} className="choice" data-testid={`gc-design-label-${d}`}>
                <input type="radio" name="design" value={d} checked={design === d} onChange={() => setDesign(d)} data-testid={`gc-design-${d}`} />
                {t(`design.${d}`)}
              </label>
            ))}
          </div>
        </fieldset>
        <div className="gc-preview" data-testid="gc-preview">
          <img src={images[design]} alt={t(`design.${design}`)} />
          <div className="gc-text">
            <strong>{t("brand")}</strong> · Gift Card {value ? `฿${Number(value).toLocaleString("en-US")}` : ""}
          </div>
        </div>
        <fieldset style={{ border: 0, padding: 0, margin: "14px 0" }}>
          <legend style={{ fontWeight: 600, marginBottom: 6 }}>{t("gift.channel")}</legend>
          <div className="choice-grid">
            {(["line", "email"] as const).map((c) => (
              <label key={c} className="choice" data-testid={`gc-channel-label-${c}`}>
                <input type="radio" name="channel" value={c} checked={channel === c} onChange={() => setChannel(c)} data-testid={`gc-channel-${c}`} />
                {t(`channel.${c}`)}
              </label>
            ))}
          </div>
        </fieldset>
        <div className="field">
          <label htmlFor="gc-to">{t("gift.recipient")}</label>
          <input id="gc-to" type="text" value={recipient} onChange={(e) => setRecipient(e.target.value)} data-testid="gc-recipient" />
        </div>
        <div className="field">
          <label htmlFor="gc-msg">{t("gift.message")}</label>
          <textarea id="gc-msg" value={message} onChange={(e) => setMessage(e.target.value)} data-testid="gc-message" />
        </div>
        <button type="button" className="btn btn-gold" onClick={buy} data-testid="gc-submit">
          {t("gift.submit")}
        </button>
        {err && (
          <div className="alert alert-error" role="alert" data-testid="gc-error">
            {err}
          </div>
        )}
        {bought && (
          <div className="alert alert-ok" data-testid="gc-result" aria-live="polite">
            <p data-testid="gc-sent">{bought.sentMessage}</p>
            <p>
              {t("gift.code")}: <strong data-testid="gc-code">{bought.code}</strong> · {bought.valueLabel}
            </p>
            <p data-testid="gc-expires">{bought.expiresLabel}</p>
            <p className="small">
              {t("gift.preview")}: <span data-testid="gc-preview-text">{bought.preview}</span>
            </p>
          </div>
        )}
      </section>

      <section className="card" aria-labelledby="gc-check">
        <h2 id="gc-check">{t("gift.check")}</h2>
        <div className="field">
          <label htmlFor="gc-code-in">{t("gift.code")}</label>
          <input id="gc-code-in" type="text" value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} placeholder="SABAI-GC-2000" data-testid="gc-check-code" />
        </div>
        <button type="button" className="btn" onClick={check} data-testid="gc-check-submit">
          {t("gift.checkBtn")}
        </button>
        {info && (
          <div className={`alert ${info.status === "ok" ? "alert-ok" : "alert-error"}`} data-testid="gc-check-result" data-status={info.status}>
            <p data-testid="gc-check-status">{info.message}</p>
            <p data-testid="gc-check-balance">{t("gift.balance", { b: info.balanceLabel })}</p>
            <p data-testid="gc-check-expires">{info.expiresLabel}</p>
          </div>
        )}
        {infoErr && (
          <div className="alert alert-error" role="alert" data-testid="gc-check-error">
            {infoErr}
          </div>
        )}
      </section>
    </>
  );
}
