'use client';
// app/admin/charts.tsx (v3) — กราฟ SVG น้ำหนักเบา (ไม่ใช้ chart library) ใช้ใน /admin/eval และ /admin/load
import { useEffect, useState } from 'react';

export const SERIES = ['#ff8a3d', '#3fd6ff', '#b79cff', '#9aa4b5', '#3ddc97'];

/** true หลัง mount 1 เฟรม → ใช้เริ่ม transition จาก 0 */
export function useMounted(dep?: unknown) {
  const [on, setOn] = useState(false);
  useEffect(() => {
    setOn(false);
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setOn(true)));
    return () => cancelAnimationFrame(id);
  }, [dep]);
  return on;
}

export const pct = (v: number | null | undefined, digits = 0) =>
  v == null || Number.isNaN(v) ? '–' : `${(v * 100).toFixed(digits)}%`;

/** วงแหวนคะแนน 0..1 (lowerBetter = ยิ่งน้อยยิ่งดี เช่น CER) */
export function Gauge({ value, size = 92, lowerBetter = false, dep }: { value: number | null; size?: number; lowerBetter?: boolean; dep?: unknown }) {
  const on = useMounted(dep);
  const r = 38;
  const c = 2 * Math.PI * r;
  const v = value == null ? 0 : Math.max(0, Math.min(1, value));
  const good = lowerBetter ? 1 - Math.min(1, v * 3) : v;
  const color = good >= 0.85 ? '#3ddc97' : good >= 0.65 ? '#fbbf24' : '#ff6b6b';
  const shown = lowerBetter ? Math.min(1, v * 3) : v;
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className="ev-gauge" aria-hidden>
      <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="9" />
      <circle
        cx="50"
        cy="50"
        r={r}
        fill="none"
        stroke={color}
        strokeWidth="9"
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={on ? c * (1 - shown) : c}
        transform="rotate(-90 50 50)"
        style={{ transition: 'stroke-dashoffset 1.1s cubic-bezier(.22,1,.36,1)', filter: `drop-shadow(0 0 6px ${color}88)` }}
      />
      <text x="50" y="55" textAnchor="middle" className="ev-gauge-val">
        {value == null ? '–' : lowerBetter ? (v * 100).toFixed(1) + '%' : Math.round(v * 100) + '%'}
      </text>
    </svg>
  );
}

/** แท่งแนวนอน 0..1 */
export function Bar({ value, color = SERIES[0], dep, height = 8 }: { value: number; color?: string; dep?: unknown; height?: number }) {
  const on = useMounted(dep);
  return (
    <span className="ev-bar" style={{ height }}>
      <span
        style={{
          width: on ? `${Math.max(0, Math.min(1, value)) * 100}%` : '0%',
          background: `linear-gradient(90deg, ${color}, ${color}cc)`,
          boxShadow: `0 0 10px ${color}66`,
        }}
      />
    </span>
  );
}

export type LineSeries = { name: string; color: string; points: { x: number; y: number | null }[]; dashed?: boolean };

/** กราฟเส้น x = จำนวนผู้ใช้ (สเกล log2) · y = วินาที · threshold = เส้นประแนวนอน */
export function LineChart({
  series,
  threshold,
  yLabel = 'วินาที',
  xLabel = 'ผู้ใช้พร้อมกัน',
  dep,
  height = 300,
  testId,
}: {
  series: LineSeries[];
  threshold?: { y: number; label: string } | null;
  yLabel?: string;
  xLabel?: string;
  dep?: unknown;
  height?: number;
  testId?: string;
}) {
  const on = useMounted(dep);
  const W = 720;
  const H = height;
  const P = { l: 52, r: 20, t: 18, b: 44 };
  const xs = Array.from(new Set(series.flatMap((s) => s.points.map((p) => p.x)))).sort((a, b) => a - b);
  const ys = series.flatMap((s) => s.points.map((p) => p.y).filter((y): y is number => y != null));
  if (threshold) ys.push(threshold.y);
  const yMax = niceMax(Math.max(1, ...ys) * 1.08);
  const lx = (x: number) => Math.log2(Math.max(1, x));
  const xMin = lx(xs[0] ?? 1);
  const xMax = Math.max(xMin + 1, lx(xs[xs.length - 1] ?? 2));
  const X = (x: number) => P.l + ((lx(x) - xMin) / (xMax - xMin)) * (W - P.l - P.r);
  const Y = (y: number) => H - P.b - (y / yMax) * (H - P.t - P.b);
  const ticks = Array.from({ length: 5 }, (_, i) => (yMax / 4) * i);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="ev-line" data-testid={testId} role="img" aria-label={`${yLabel} เทียบ ${xLabel}`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={P.l} x2={W - P.r} y1={Y(t)} y2={Y(t)} stroke="rgba(255,255,255,0.07)" />
          <text x={P.l - 8} y={Y(t) + 4} textAnchor="end" className="ev-axis">
            {t % 1 ? t.toFixed(1) : t}
          </text>
        </g>
      ))}
      {xs.map((x) => (
        <text key={x} x={X(x)} y={H - P.b + 18} textAnchor="middle" className="ev-axis">
          {x}
        </text>
      ))}
      <text x={(W + P.l) / 2} y={H - 6} textAnchor="middle" className="ev-axis-title">
        {xLabel}
      </text>
      <text x={14} y={(H - P.b + P.t) / 2} textAnchor="middle" className="ev-axis-title" transform={`rotate(-90 14 ${(H - P.b + P.t) / 2})`}>
        {yLabel}
      </text>
      {threshold && (
        <g>
          <line x1={P.l} x2={W - P.r} y1={Y(threshold.y)} y2={Y(threshold.y)} stroke="#ff6b6b" strokeDasharray="6 5" strokeWidth="1.6" />
          <text x={W - P.r - 4} y={Y(threshold.y) - 6} textAnchor="end" className="ev-thr">
            {threshold.label}
          </text>
        </g>
      )}
      {series.map((s) => {
        const pts = s.points.filter((p) => p.y != null) as { x: number; y: number }[];
        if (!pts.length) return null;
        const d = pts.map((p, i) => `${i ? 'L' : 'M'}${X(p.x).toFixed(1)},${Y(p.y).toFixed(1)}`).join(' ');
        return (
          <g key={s.name}>
            <path
              d={d}
              fill="none"
              stroke={s.color}
              strokeWidth="2.6"
              strokeDasharray={s.dashed ? '5 5' : '1600'}
              strokeDashoffset={s.dashed ? 0 : on ? 0 : 1600}
              strokeLinejoin="round"
              style={{ transition: 'stroke-dashoffset 1.4s cubic-bezier(.22,1,.36,1)', filter: `drop-shadow(0 0 5px ${s.color}88)` }}
            />
            {pts.map((p) => (
              <circle key={p.x} cx={X(p.x)} cy={Y(p.y)} r={on ? 4 : 0} fill="#10141c" stroke={s.color} strokeWidth="2.2" style={{ transition: 'r .4s .9s' }}>
                <title>
                  {s.name} · {p.x} ผู้ใช้ · {p.y}
                </title>
              </circle>
            ))}
          </g>
        );
      })}
    </svg>
  );
}

function niceMax(v: number) {
  const p = Math.pow(10, Math.floor(Math.log10(v)));
  for (const m of [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]) if (v <= m * p) return m * p;
  return 10 * p;
}

export function Legend({ items }: { items: { name: string; color: string; dashed?: boolean }[] }) {
  return (
    <div className="ev-legend">
      {items.map((i) => (
        <span key={i.name}>
          <i style={{ background: i.dashed ? 'transparent' : i.color, borderColor: i.color }} className={i.dashed ? 'dashed' : ''} />
          {i.name}
        </span>
      ))}
    </div>
  );
}
