// รูปพร้อมกรอบที่โมเดลตรวจพบ (วาดด้วย SVG ทับรูป)
import { styleOf, type Detection } from "@/lib/ppe";

type Props = {
  src: string;
  width: number;
  height: number;
  detections: Detection[];
  hide?: string[];
  showLabels?: boolean;
};

export default function BoxedImage({ src, width, height, detections, hide = [], showLabels = true }: Props) {
  const fs = Math.max(12, Math.round(width / 30));
  const sw = Math.max(2, Math.round(width / 260));
  return (
    <div className="boxed" style={{ aspectRatio: `${width} / ${height}` }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt="รูปที่ตรวจ" />
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
        {detections
          .filter((d) => !hide.includes(d.class))
          .map((d, i) => {
            const [x1, y1, x2, y2] = d.box;
            const st = styleOf(d.class);
            const label = `${st.th} ${Math.round(d.confidence * 100)}%`;
            const tw = label.length * fs * 0.58 + 10;
            const ty = y1 - fs - 6 < 0 ? y1 : y1 - fs - 6;
            return (
              <g key={i}>
                <rect x={x1} y={y1} width={x2 - x1} height={y2 - y1} fill="none" stroke={st.color} strokeWidth={sw} rx={3} />
                {showLabels && (
                  <>
                    <rect x={x1} y={ty} width={tw} height={fs + 6} fill={st.color} rx={3} />
                    <text x={x1 + 5} y={ty + fs} fontSize={fs} fill="#fff" fontWeight={600}>
                      {label}
                    </text>
                  </>
                )}
              </g>
            );
          })}
      </svg>
    </div>
  );
}
