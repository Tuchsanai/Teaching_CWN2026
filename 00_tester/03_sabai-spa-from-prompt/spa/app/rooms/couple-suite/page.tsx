"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, useApp, useReady } from "@/components/AppProvider";
import { Reveal } from "@/components/Reveal";
import { Icon, ThaiDivider } from "@/components/Ornament";
import { PageHead } from "@/components/Shared";
import { pick } from "@/lib/i18n";

type Room = { slug: string; image: string; capacity: number; name_th: string; name_en: string; name_zh: string; desc_th: string; desc_en: string; desc_zh: string };

const PANO = "/assets/rooms/room-couple-suite.jpg";
const RATIO = 1672 / 941;

/** FR-23: drag-to-rotate 360° view built with plain CSS transforms (no external library).
 *  The photo is mirrored every second tile so the strip wraps seamlessly all the way round. */
function Panorama({ label, onAngle }: { label: string; onAngle: (deg: number) => void }) {
  const { t } = useApp();
  const box = useRef<HTMLDivElement>(null);
  const strip = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  const [loaded, setLoaded] = useState(false);
  const [auto, setAuto] = useState(true);
  const [touched, setTouched] = useState(false);
  const pos = useRef(0);
  const vel = useRef(0);
  const drag = useRef<{ x: number; last: number; t: number } | null>(null);
  const autoRef = useRef(auto);
  autoRef.current = auto;

  const tileW = size.h * RATIO;
  const period = tileW * 2;
  const tiles = period > 0 ? Math.ceil((size.w + period) / tileW) + 2 : 0;

  const paint = useCallback(() => {
    if (!strip.current || period <= 0) return;
    const p = ((pos.current % period) + period) % period;
    strip.current.style.transform = `translate3d(${-p}px,0,0)`;
    const deg = Math.round((p / period) * 360) % 360;
    box.current?.setAttribute("data-angle", String(deg));
    onAngle(deg);
  }, [period, onAngle]);

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setSize({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el);
    const img = new Image();
    img.onload = () => setLoaded(true);
    img.src = PANO;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) setAuto(false);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    let raf = 0;
    const loop = () => {
      if (!drag.current) {
        if (Math.abs(vel.current) > 0.05) {
          pos.current += vel.current;
          vel.current *= 0.94;
        } else if (autoRef.current) {
          pos.current += 0.35;
        }
      }
      paint();
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [paint]);

  const step = (deg: number) => {
    setTouched(true);
    setAuto(false);
    vel.current = 0;
    pos.current += (deg / 360) * period;
    paint();
  };

  return (
    <div
      ref={box}
      className={`tour ${touched ? "is-touched" : ""}`}
      role="img"
      aria-label={label}
      tabIndex={0}
      data-testid="tour-360"
      data-angle="0"
      data-loaded={loaded ? "true" : "false"}
      onPointerDown={(e) => {
        (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
        drag.current = { x: e.clientX, last: e.clientX, t: performance.now() };
        vel.current = 0;
        setTouched(true);
        setAuto(false);
      }}
      onPointerMove={(e) => {
        if (!drag.current) return;
        const dx = e.clientX - drag.current.last;
        drag.current.last = e.clientX;
        pos.current -= dx;
        vel.current = -dx;
      }}
      onPointerUp={() => (drag.current = null)}
      onPointerCancel={() => (drag.current = null)}
      onKeyDown={(e) => {
        if (e.key === "ArrowLeft") { e.preventDefault(); step(-10); }
        if (e.key === "ArrowRight") { e.preventDefault(); step(10); }
      }}
    >
      <div ref={strip} className="tour__strip" aria-hidden="true">
        {Array.from({ length: tiles }, (_, i) => (
          <div key={i} className={`tour__tile ${i % 2 ? "tour__tile--flip" : ""}`} style={{ width: tileW, backgroundImage: `url(${PANO})` }} />
        ))}
      </div>
      <div className="tour__vignette" />
      <div className="tour__hint"><Icon name="drag" /> {t("rooms_drag")}</div>
      <div className="tour__hud">
        <span className="tour__pill">
          <span className="tour__compass" aria-hidden="true"><i id="compass-needle" /></span>
        </span>
        <div className="tour__controls">
          <button type="button" className="icon-btn" onClick={() => step(-30)} aria-label={t("rooms_left")} data-testid="tour-left"><Icon name="left" /></button>
          <button type="button" className="icon-btn" onClick={() => { setTouched(true); setAuto((a) => !a); }} aria-pressed={auto} aria-label={t("rooms_auto")} data-testid="tour-auto">
            <Icon name={auto ? "pause" : "play"} size={18} />
          </button>
          <button type="button" className="icon-btn" onClick={() => step(30)} aria-label={t("rooms_right")} data-testid="tour-right"><Icon name="right" /></button>
        </div>
      </div>
    </div>
  );
}

export default function CoupleSuitePage() {
  const { t, lang } = useApp();
  const [rooms, setRooms] = useState<Room[] | null>(null);
  const [angle, setAngle] = useState(0);
  const angleRef = useRef(0);
  useEffect(() => {
    api<{ ok: boolean; rooms: Room[] }>("/api/rooms").then((r) => r.ok && setRooms(r.rooms));
  }, []);
  useReady(!!rooms);
  const onAngle = useCallback((d: number) => {
    const needle = document.getElementById("compass-needle");
    if (needle) needle.style.transform = `rotate(${d}deg)`;
    if (Math.abs(d - angleRef.current) >= 5 || d === 0) {
      angleRef.current = d;
      setAngle(d);
    }
  }, []);
  const suite = rooms?.find((r) => r.slug === "couple-suite");

  return (
    <>
      <PageHead eyebrow={t("rooms_eyebrow")} title={t("rooms_title")} lead={t("rooms_lead")} image="/assets/rooms/room-couple-suite.jpg" />
      <section className="section" style={{ paddingTop: 40 }}>
        <div className="container">
          <Panorama label={t("rooms_title")} onAngle={onAngle} />
          <div className="row row--between mt-2">
            <div>
              <h2 style={{ marginBottom: 4 }}>{suite ? pick(suite, "name", lang) : "Couple Suite"}</h2>
              <p className="muted" style={{ margin: 0 }}>
                {suite ? pick(suite, "desc", lang) : ""} · {t("rooms_capacity", { n: 2 })} · <span>{t("rooms_angle")} <b data-testid="tour-angle">{angle}°</b></span>
              </p>
            </div>
            <Link href="/book?service=aroma-oil&people=2" className="btn btn--gold btn--lg" data-testid="tour-book">
              {t("rooms_book_this")} <Icon name="arrow" />
            </Link>
          </div>
        </div>
      </section>
      <section className="section section--paper">
        <div className="container">
          <div className="section-head">
            <h2>{t("rooms_others")}</h2>
            <ThaiDivider />
          </div>
          <div className="grid grid--3">
            {(rooms ?? []).map((r, i) => (
              <Reveal key={r.slug} delay={i * 80}>
                <article className="card card--hover svc-card" data-testid={`room-card-${r.slug}`}>
                  <div className="svc-card__media"><img src={r.image} alt={pick(r, "name", lang)} loading="lazy" /></div>
                  <div className="svc-card__body">
                    <h3>{pick(r, "name", lang)}</h3>
                    <p>{pick(r, "desc", lang)}</p>
                    <p className="small muted">{t("rooms_capacity", { n: r.capacity })}</p>
                  </div>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
