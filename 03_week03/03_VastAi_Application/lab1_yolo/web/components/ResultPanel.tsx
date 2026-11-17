// สรุปผลตรวจ: สถานะผ่าน/ไม่ผ่าน ตัวเลขต่อประเภท เวลาที่โมเดลใช้ และรายการกรอบ
import { styleOf, type Detection, type Summary } from "@/lib/ppe";

type Props = { summary: Summary; detections: Detection[]; inference_ms: number; roundtrip_ms: number; model: string };

export default function ResultPanel({ summary, detections, inference_ms, roundtrip_ms, model }: Props) {
  const counts = new Map<string, number>();
  detections.forEach((d) => counts.set(d.class, (counts.get(d.class) ?? 0) + 1));
  return (
    <div className="result">
      <div className={`verdict ${summary.passed ? "pass" : "fail"}`}>
        <div className="verdict-badge">{summary.passed ? "ผ่าน" : "ไม่ผ่าน"}</div>
        <div>
          <div className="verdict-title">
            {summary.no_hardhat > 0 ? `พบคนไม่สวมหมวก ${summary.no_hardhat} คน` : "ไม่พบคนไม่สวมหมวก"}
          </div>
          <div className="verdict-sub">
            {summary.passed ? "ทุกคนในภาพสวมหมวกนิรภัย" : "ต้องแจ้งหัวหน้างานให้สวมหมวกนิรภัยก่อนเข้าพื้นที่"}
          </div>
        </div>
      </div>

      <div className="tiles">
        <div className="tile">
          <span className="tile-num">{summary.persons}</span>
          <span className="tile-lbl">คนในภาพ</span>
        </div>
        <div className="tile ok">
          <span className="tile-num">{summary.hardhat}</span>
          <span className="tile-lbl">สวมหมวก</span>
        </div>
        <div className="tile bad">
          <span className="tile-num">{summary.no_hardhat}</span>
          <span className="tile-lbl">ไม่สวมหมวก</span>
        </div>
        <div className="tile warn">
          <span className="tile-num">{summary.no_vest}</span>
          <span className="tile-lbl">ไม่สวมเสื้อสะท้อนแสง</span>
        </div>
      </div>

      <div className="timing">
        <span>
          โมเดลใช้เวลา <b>{inference_ms.toFixed(1)} ms</b> ต่อรูป
        </span>
        <span className="dot">·</span>
        <span>ส่งรูปไป-กลับ {Math.round(roundtrip_ms)} ms</span>
        <span className="dot">·</span>
        <span className="mono">{model}</span>
      </div>

      <div className="chips">
        {[...counts.entries()].map(([c, n]) => (
          <span key={c} className="chip" style={{ borderColor: styleOf(c).color }}>
            <i style={{ background: styleOf(c).color }} />
            {styleOf(c).th} × {n}
          </span>
        ))}
        {detections.length === 0 && <span className="muted">ไม่พบวัตถุในรูป</span>}
      </div>
    </div>
  );
}
