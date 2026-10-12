import { formatDate, type Lang } from "@/lib/i18n.ts";

/** FR-16 กราฟรอบเอว: 1 จุดต่อการวัด 1 ครั้ง แต่ละจุดบอกวันที่และรอบเอว (ซม.) */
export function WaistChart({ points, lang, title }: { points: { date: string; cm: number }[]; lang: Lang; title: string }) {
  const W = 520;
  const H = 320;
  const pad = { l: 50, r: 56, t: 36, b: 60 };
  const min = Math.floor(Math.min(...points.map((p) => p.cm)) - 1);
  const max = Math.ceil(Math.max(...points.map((p) => p.cm)) + 1);
  const x = (i: number) => pad.l + (points.length === 1 ? (W - pad.l - pad.r) / 2 : (i * (W - pad.l - pad.r)) / (points.length - 1));
  const y = (cm: number) => pad.t + ((max - cm) * (H - pad.t - pad.b)) / Math.max(1, max - min);
  const ticks = Array.from({ length: max - min + 1 }, (_, i) => min + i).filter((v, i, a) => a.length <= 8 || i % 2 === 0);
  const path = points.map((p, i) => `${i ? "L" : "M"}${x(i)},${y(p.cm)}`).join(" ");
  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title} data-testid="waist-chart">
        <rect x="0" y="0" width={W} height={H} rx="12" fill="#fffdf7" />
        {ticks.map((v) => (
          <g key={v}>
            <line x1={pad.l} x2={W - pad.r} y1={y(v)} y2={y(v)} stroke="#eadfc2" />
            <text x={pad.l - 8} y={y(v) + 5} textAnchor="end" fontSize="17" fill="#6a6656">
              {v}
            </text>
          </g>
        ))}
        <path d={path} fill="none" stroke="#3d6b3a" strokeWidth="3" />
        {points.map((p, i) => (
          <g key={p.date} data-testid={`waist-point-${i}`} data-date={p.date} data-cm={p.cm.toFixed(1)}>
            <circle cx={x(i)} cy={y(p.cm)} r="7" fill="#c39a45" stroke="#23422a" strokeWidth="2">
              <title>{`${formatDate(p.date, lang)} · ${p.cm.toFixed(1)} cm`}</title>
            </circle>
            <text x={x(i)} y={y(p.cm) - 14} textAnchor="middle" fontSize="19" fontWeight="700" fill="#23422a">
              {p.cm.toFixed(1)}
            </text>
            <text x={x(i)} y={H - pad.b + (i % 2 ? 46 : 26)} textAnchor="middle" fontSize="16" fill="#6a6656">
              {formatDate(p.date, lang)}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
