"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useApp, useReady } from "@/components/AppProvider";
import { Icon } from "@/components/Ornament";
import { PageHead, svcName, useServices } from "@/components/Shared";
import { classifySkin, SIM_FILTERS, type SkinType } from "@/lib/recommend";
import type { DictKey } from "@/lib/i18n";
import { formatBaht } from "@/lib/time";

const SAMPLE = "/assets/skin/sample-face.jpg";

type Result = { r: number; g: number; b: number; type: SkinType; brightness: number; redness: number; services: string[] };

/** Average colour of the centre 60 % of the picture, computed with <canvas> in the browser.
 *  The picture never leaves the device (FR-29, NFR-07, BR-25). */
function analyse(img: HTMLImageElement): Result {
  const size = 96;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d", { willReadFrequently: true })!;
  const sw = img.naturalWidth * 0.6;
  const sh = img.naturalHeight * 0.6;
  ctx.drawImage(img, img.naturalWidth * 0.2, img.naturalHeight * 0.2, sw, sh, 0, 0, size, size);
  const data = ctx.getImageData(0, 0, size, size).data;
  let r = 0, g = 0, b = 0;
  const n = data.length / 4;
  for (let i = 0; i < data.length; i += 4) {
    r += data[i];
    g += data[i + 1];
    b += data[i + 2];
  }
  r = Math.round(r / n);
  g = Math.round(g / n);
  b = Math.round(b / n);
  return { r, g, b, ...classifySkin(r, g, b) };
}

export default function SkinPage() {
  const { t, lang } = useApp();
  const services = useServices();
  const [src, setSrc] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [res, setRes] = useState<Result | null>(null);
  const [sim, setSim] = useState<string>("turmeric-facial");
  const [pos, setPos] = useState(50);
  const objectUrl = useRef<string | null>(null);
  useReady(!!services);

  useEffect(() => () => {
    if (objectUrl.current) URL.revokeObjectURL(objectUrl.current);
  }, []);

  const run = (url: string) => {
    setBusy(true);
    setRes(null);
    setSrc(url);
    const img = new Image();
    img.onload = () => {
      // short pause so the scan animation is visible; the work itself is instant
      setTimeout(() => {
        setRes(analyse(img));
        setBusy(false);
      }, 450);
    };
    img.onerror = () => setBusy(false);
    img.src = url;
  };

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (objectUrl.current) URL.revokeObjectURL(objectUrl.current);
    objectUrl.current = URL.createObjectURL(f); // local blob: URL — nothing is uploaded
    run(objectUrl.current);
    e.target.value = "";
  };

  const rgb = res ? `rgb(${res.r}, ${res.g}, ${res.b})` : "transparent";

  return (
    <>
      <PageHead eyebrow={t("skin_eyebrow")} title={t("skin_title")} lead={t("skin_lead")} image="/assets/treatments/turmeric-facial.jpg" />
      <section className="section">
        <div className="container">
          <p className="alert alert--ok" data-testid="skin-private"><Icon name="shield" /> {t("skin_private")}</p>
          <div className="split mt-2" style={{ alignItems: "start" }}>
            <div>
              <div className="skin-stage" data-testid="skin-stage">
                {src ? <img src={src} alt={t("skin_image_alt")} data-testid="skin-preview" /> : (
                  <div className="skin-empty"><div><Icon name="user" size={48} /><p className="mt-1">{t("sim_need_image")}</p></div></div>
                )}
                {busy && <div className="skin-stage__scan" aria-hidden="true" />}
              </div>
              <div className="row mt-2">
                <label className="btn btn--green" style={{ cursor: "pointer" }}>
                  <Icon name="user" /> {t("skin_pick")}
                  <input type="file" accept="image/*" capture="user" onChange={onFile} className="sr-only" data-testid="skin-file" />
                </label>
                <button type="button" className="btn btn--ghost" onClick={() => run(SAMPLE)} data-testid="skin-sample">
                  {t("skin_sample")}
                </button>
              </div>
            </div>

            <div>
              {busy && <p className="alert alert--info" role="status">{t("skin_analyzing")}</p>}
              {res && (
                <div className="card card--pad" data-testid="skin-result-card" style={{ animation: "up 300ms both" }}>
                  <p className="label">{t("skin_type")}</p>
                  <h2 data-testid="skin-result" data-type={res.type}>{t(`skin_type_${res.type}` as DictKey)}</h2>
                  <div className="row">
                    <span className="swatch" style={{ background: rgb }} aria-hidden="true" />
                    <span data-testid="skin-avg" data-r={res.r} data-g={res.g} data-b={res.b}>
                      {t("skin_avg")}: R {res.r} · G {res.g} · B {res.b}
                    </span>
                  </div>
                  <div className="mt-1">
                    <div className="metric"><span>{t("skin_brightness")}</span><b data-testid="skin-brightness">{res.brightness}</b></div>
                    <div className="metric"><span>{t("skin_redness")}</span><b data-testid="skin-redness">{res.redness}</b></div>
                  </div>
                  <h3 className="mt-2">{t("skin_recommend")}</h3>
                  <div className="rec-list" style={{ gridTemplateColumns: "1fr" }}>
                    {res.services.map((slug) => {
                      const s = services?.find((x) => x.slug === slug);
                      if (!s) return null;
                      return (
                        <div className="rec" key={slug} data-testid={`skin-rec-${slug}`}>
                          <img src={s.image} alt={svcName(s, lang)} />
                          <div>
                            <h3>{svcName(s, lang)}</h3>
                            <p>{t("minutes", { n: s.duration })} · {formatBaht(s.price)}</p>
                            <Link href={`/book?service=${slug}`} className="btn btn--green btn--sm" data-testid={`skin-book-${slug}`}>{t("book_now")}</Link>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <p className="alert alert--info mt-2" data-testid="skin-disclaimer">{t("skin_disclaimer")}</p>
                </div>
              )}
              <details className="card card--pad mt-2">
                <summary style={{ cursor: "pointer", fontWeight: 600, minHeight: 44, display: "flex", alignItems: "center" }}>{t("skin_rules")}</summary>
                <ul className="small" data-testid="skin-rules">
                  <li>{t("skin_rule_1")}</li>
                  <li>{t("skin_rule_2")}</li>
                  <li>{t("skin_rule_3")}</li>
                  <li>{t("skin_rule_4")}</li>
                </ul>
              </details>
            </div>
          </div>
        </div>
      </section>

      {/* FR-30 — before/after simulation with CSS filters on the same picture */}
      <section className="section section--paper" aria-labelledby="sim-title">
        <div className="container split" style={{ alignItems: "start" }}>
          <div>
            <h2 id="sim-title">{t("sim_title")}</h2>
            <p className="muted">{t("skin_private")}</p>
            <div className="field">
              <label htmlFor="sim-t">{t("sim_treatment")}</label>
              <select id="sim-t" className="select" value={sim} onChange={(e) => setSim(e.target.value)} data-testid="sim-treatment">
                {Object.keys(SIM_FILTERS).map((slug) => {
                  const s = services?.find((x) => x.slug === slug);
                  return <option key={slug} value={slug}>{s ? svcName(s, lang) : slug}</option>;
                })}
              </select>
            </div>
            <div className="field">
              <label htmlFor="sim-s">{t("sim_slider")}</label>
              <input id="sim-s" className="range" type="range" min={0} max={100} value={pos} onChange={(e) => setPos(Number(e.target.value))} data-testid="sim-slider" />
            </div>
            <p className="alert alert--error" data-testid="sim-label">{t("sim_label")}</p>
          </div>
          <div className="compare" style={{ ["--pos" as string]: `${pos}%` }} data-testid="sim-compare">
            <img src={src ?? SAMPLE} alt={`${t("before")} — ${t("skin_image_alt")}`} data-testid="sim-before" />
            <img src={src ?? SAMPLE} alt={`${t("sim_after")} — ${t("skin_image_alt")}`} className="compare__after" style={{ filter: SIM_FILTERS[sim] }} data-testid="sim-after" data-filter={SIM_FILTERS[sim]} />
            <span className="compare__line" aria-hidden="true" />
            <span className="compare__tag compare__tag--l">{t("before")}</span>
            <span className="compare__tag compare__tag--r">{t("sim_after")}</span>
            <span className="sim-label">{t("sim_label")}</span>
          </div>
        </div>
      </section>
    </>
  );
}
