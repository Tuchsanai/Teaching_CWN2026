import { CLASS_COLOR, CLASS_TH, type Detection } from "@/lib/types";

export default function BoxedImage({ src, width, height, detections }: { src: string; width: number; height: number; detections: Detection[] }) {
  const sw = Math.max(2, Math.round(Math.max(width, height) / 300));
  const fs = Math.max(12, Math.round(Math.max(width, height) / 45));
  return (
    <div className="boxed">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="รูปพร้อมกรอบที่ตรวจพบ">
        <image href={src} x={0} y={0} width={width} height={height} />
        {detections.map((d, i) => {
          const [x1, y1, x2, y2] = d.box;
          const c = CLASS_COLOR[d.class] ?? "#0f172a";
          const label = `${CLASS_TH[d.class] ?? d.class} ${Math.round(d.confidence * 100)}%`;
          const ly = y1 - fs - 4 < 0 ? y1 : y1 - fs - 4;
          return (
            <g key={i}>
              <rect x={x1} y={y1} width={x2 - x1} height={y2 - y1} fill="none" stroke={c} strokeWidth={sw} />
              <rect x={x1} y={ly} width={label.length * fs * 0.55 + 8} height={fs + 4} fill={c} />
              <text x={x1 + 4} y={ly + fs} fontSize={fs} fill="#fff" fontFamily="inherit">{label}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
