"use client";

import { useState } from "react";
import { formatBaht } from "@/lib/money.ts";
import { useI18n } from "./I18nProvider.tsx";

/** FR-22 ใส่ระยะทาง/เลือกโรงแรม + จำนวนคน → ค่ารถและจำนวนคัน (BR-17, BR-18) คิดที่เซิร์ฟเวอร์ */
export function TransportCalc({ hotels }: { hotels: { code: string; name: string; distanceKm: number }[] }) {
  const { t } = useI18n();
  const [hotel, setHotel] = useState("");
  const [distance, setDistance] = useState("");
  const [people, setPeople] = useState(1);
  const [res, setRes] = useState<{ fee: number; vehicles: number; distanceKm: number } | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const calc = async () => {
    setErr(null);
    setRes(null);
    const q = new URLSearchParams({ people: String(people) });
    if (hotel) q.set("hotel", hotel);
    else q.set("distance", distance);
    const r = await fetch(`/api/transport?${q}`);
    const j = await r.json();
    if (r.ok) setRes(j);
    else setErr(j.message);
  };

  return (
    <div className="card">
      <p className="muted" data-testid="transport-rule">
        {t("transport.rule")}
      </p>
      <div className="field">
        <label htmlFor="tr-hotel">{t("book.hotel")}</label>
        <select id="tr-hotel" value={hotel} onChange={(e) => setHotel(e.target.value)} data-testid="transport-hotel">
          <option value="">{t("book.hotelOther")}</option>
          {hotels.map((h) => (
            <option key={h.code} value={h.code}>
              {h.name} · {h.distanceKm.toFixed(1)} {t("common.km")}
            </option>
          ))}
        </select>
      </div>
      {!hotel && (
        <div className="field">
          <label htmlFor="tr-dist">{t("book.distance")}</label>
          <input id="tr-dist" type="number" inputMode="decimal" step="0.1" min="0" value={distance} onChange={(e) => setDistance(e.target.value)} data-testid="transport-distance" />
        </div>
      )}
      <div className="field">
        <label htmlFor="tr-people">{t("book.people")}</label>
        <select id="tr-people" value={people} onChange={(e) => setPeople(Number(e.target.value))} data-testid="transport-people">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </div>
      <button type="button" className="btn" onClick={calc} data-testid="transport-calc">
        {t("transport.calc")}
      </button>
      {res && (
        <div className="alert alert-ok" data-testid="transport-result" aria-live="polite">
          <strong data-testid="transport-fee" data-amount={res.fee}>
            {t("transport.fee", { f: res.fee === 0 ? `${formatBaht(0)} (${t("common.free")})` : formatBaht(Math.round(res.fee * 100)) })}
          </strong>{" "}
          · <span data-testid="transport-vehicles">{t("transport.vehicles", { v: res.vehicles })}</span> · {res.distanceKm.toFixed(1)} {t("common.km")}
        </div>
      )}
      {err && (
        <div className="alert alert-error" role="alert" data-testid="transport-error">
          {err}
        </div>
      )}
    </div>
  );
}
