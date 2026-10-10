"use client";

import { useEffect, useRef, useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

/** FR-33 ทัวร์ห้อง Couple Suite 360°: ลากเมาส์/ปัดนิ้วหมุนได้รอบ (NFR-18) · panorama 2:1 วนต่อกันซ้ายขวา */
export function Tour360({ src, onClose }: { src: string; onClose: () => void }) {
  const { t } = useI18n();
  const view = useRef<HTMLDivElement>(null);
  const [angle, setAngle] = useState(0);
  const [width, setWidth] = useState(0);
  const drag = useRef<{ x: number; a: number } | null>(null);
  const closeBtn = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const el = view.current;
    if (!el) return;
    const measure = () => setWidth(el.clientHeight * 2);
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    closeBtn.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => {
      ro.disconnect();
      window.removeEventListener("keydown", onKey);
    };
  }, [onClose]);

  const norm = (a: number) => ((a % 360) + 360) % 360;
  const offset = width ? -(norm(angle) / 360) * width : 0;

  const onDown = (e: React.PointerEvent) => {
    (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
    drag.current = { x: e.clientX, a: angle };
  };
  const onMove = (e: React.PointerEvent) => {
    if (!drag.current || !width) return;
    const dx = e.clientX - drag.current.x;
    setAngle(drag.current.a - (dx / width) * 360);
  };
  const onUp = () => {
    drag.current = null;
  };

  return (
    <div className="tour-dialog" role="dialog" aria-modal="true" aria-labelledby="tour-title" data-testid="tour-dialog">
      <div className="tour-box">
        <div className="btn-row" style={{ justifyContent: "space-between" }}>
          <h2 id="tour-title" style={{ margin: 0 }}>
            {t("book.tourTitle")}
          </h2>
          <button ref={closeBtn} type="button" className="btn btn-sm btn-ghost" onClick={onClose} data-testid="tour-close">
            {t("common.close")}
          </button>
        </div>
        <p className="muted small">{t("book.tourHint")}</p>
        <div
          ref={view}
          className="tour-view"
          role="slider"
          tabIndex={0}
          aria-label={t("book.tourTitle")}
          aria-valuemin={0}
          aria-valuemax={359}
          aria-valuenow={Math.round(norm(angle))}
          aria-valuetext={`${Math.round(norm(angle))}°`}
          data-testid="tour-view"
          data-angle={Math.round(norm(angle))}
          style={{ backgroundImage: `url(${src})`, backgroundPositionX: `${offset}px` }}
          onPointerDown={onDown}
          onPointerMove={onMove}
          onPointerUp={onUp}
          onPointerCancel={onUp}
          onKeyDown={(e) => {
            if (e.key === "ArrowLeft") setAngle((a) => a - 10);
            if (e.key === "ArrowRight") setAngle((a) => a + 10);
          }}
        />
        <p className="small" data-testid="tour-angle">
          {Math.round(norm(angle))}°
        </p>
      </div>
    </div>
  );
}
