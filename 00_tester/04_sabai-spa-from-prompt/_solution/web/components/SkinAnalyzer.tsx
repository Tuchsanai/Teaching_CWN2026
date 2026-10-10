"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

// FR-29 วิเคราะห์ผิวด้วย Canvas ในเบราว์เซอร์ ไม่อัปโหลด ไม่เก็บใน localStorage/IndexedDB (NFR-09)
// FR-30 ภาพจำลองก่อน/หลัง มีป้าย "ภาพจำลอง ผลจริงแต่ละคนต่างกัน" ทุกครั้ง · กฎตายตัว (NFR-15)

interface Metrics {
  brightness: number;
  redness: number;
  evenness: number;
}

type SkinType = "red" | "oily" | "dry" | "balanced";

const RECS: Record<SkinType, string[]> = {
  red: ["S07", "S04"],
  oily: ["S07", "S06"],
  dry: ["S07", "S06", "S04"],
  balanced: ["S07"],
};

/** ค่าเฉลี่ยความสว่าง ความแดง และความสม่ำเสมอจากพื้นที่กลางภาพ (ที่หน้ามักอยู่) */
export function measure(data: Uint8ClampedArray): Metrics {
  let sum = 0;
  let sumSq = 0;
  let red = 0;
  const n = data.length / 4;
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const y = 0.299 * r + 0.587 * g + 0.114 * b;
    sum += y;
    sumSq += y * y;
    red += r - (g + b) / 2;
  }
  const mean = sum / n;
  const sd = Math.sqrt(Math.max(0, sumSq / n - mean * mean));
  return {
    brightness: Math.round((mean / 255) * 100),
    redness: Math.round(Math.max(0, Math.min(100, (red / n) * 1.5))),
    evenness: Math.round(Math.max(0, 100 - sd)),
  };
}

export function classify(m: Metrics): SkinType {
  if (m.redness >= 45) return "red";
  if (m.brightness < 45) return "oily";
  if (m.evenness < 55) return "dry";
  return "balanced";
}

export function SkinAnalyzer({ sample, services }: { sample: string; services: Record<string, string> }) {
  const { t } = useI18n();
  const [accepted, setAccepted] = useState(false);
  const [src, setSrc] = useState<string | null>(null);
  const [result, setResult] = useState<{ m: Metrics; type: SkinType } | null>(null);
  const objectUrl = useRef<string | null>(null);

  useEffect(
    () => () => {
      if (objectUrl.current) URL.revokeObjectURL(objectUrl.current);
    },
    [],
  );

  const analyse = (url: string) => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement("canvas");
      const size = 160;
      c.width = size;
      c.height = size;
      const ctx = c.getContext("2d", { willReadFrequently: true });
      if (!ctx) return;
      const s = Math.min(img.naturalWidth, img.naturalHeight);
      ctx.drawImage(img, (img.naturalWidth - s) / 2, (img.naturalHeight - s) / 2, s, s, 0, 0, size, size);
      const d = ctx.getImageData(size * 0.3, size * 0.3, size * 0.4, size * 0.4).data;
      const m = measure(d);
      setResult({ m, type: classify(m) });
    };
    img.src = url;
  };

  const onFile = (f: File | undefined) => {
    if (!f) return;
    if (objectUrl.current) URL.revokeObjectURL(objectUrl.current);
    const url = URL.createObjectURL(f);
    objectUrl.current = url;
    setSrc(url);
    analyse(url);
  };

  const useSample = () => {
    setSrc(sample);
    analyse(sample);
  };

  return (
    <div className="card">
      <p className="alert alert-info" data-testid="skin-notice">
        {t("skin.notice")}
      </p>
      {!accepted ? (
        <button type="button" className="btn" onClick={() => setAccepted(true)} data-testid="skin-accept">
          {t("skin.accept")}
        </button>
      ) : (
        <div className="btn-row">
          <label className="btn btn-gold" htmlFor="selfie" style={{ marginBottom: 0 }}>
            {t("skin.choose")}
          </label>
          <input
            id="selfie"
            type="file"
            accept="image/*"
            capture="user"
            onChange={(e) => onFile(e.target.files?.[0])}
            style={{ position: "absolute", width: 1, height: 1, opacity: 0 }}
            aria-label={t("skin.choose")}
            data-testid="skin-file"
          />
          <button type="button" className="btn btn-ghost" onClick={useSample} data-testid="skin-sample">
            {t("skin.sample")}
          </button>
        </div>
      )}

      {result && src && (
        <>
          <h2 style={{ marginTop: 20 }}>{t("skin.result")}</h2>
          <p className="price" data-testid="skin-type" data-type={result.type}>
            {t(`skin.type.${result.type}`)}
          </p>
          <p className="small muted" data-testid="skin-metrics">
            {t("skin.metrics", { b: result.m.brightness, r: result.m.redness, u: result.m.evenness })}
          </p>
          <h3>{t("skin.recommend")}</h3>
          <ul className="booking-list" data-testid="skin-recs">
            {RECS[result.type].map((code) => (
              <li key={code} className="btn-row" data-testid={`skin-rec-${code}`}>
                <strong>{services[code]}</strong>
                <Link className="btn btn-sm" href={`/book?service=${code}`} data-testid={`skin-book-${code}`}>
                  {t("common.bookNow")}
                </Link>
              </li>
            ))}
          </ul>

          <h3 style={{ marginTop: 18 }}>{t("skin.sim")}</h3>
          <div className="sim-pair" data-testid="skin-sim">
            <figure>
              <img src={src} alt={t("skin.before")} />
              <figcaption>{t("skin.before")}</figcaption>
            </figure>
            <figure>
              <img src={src} alt={t("skin.after")} style={{ filter: "brightness(1.08) saturate(1.12) contrast(0.95) blur(0.5px)" }} />
              <figcaption>{t("skin.after")}</figcaption>
            </figure>
          </div>
          <strong className="sim-label" data-testid="sim-label">
            {t("skin.simLabel")}
          </strong>
        </>
      )}
    </div>
  );
}
