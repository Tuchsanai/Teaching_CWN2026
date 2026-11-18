import type { Summary } from "@/lib/types";

export default function ResultPanel({ s, inferenceMs, roundtripMs, model }: { s: Summary; inferenceMs: number; roundtripMs: number; model: string }) {
  return (
    <div className="result">
      <div className={`verdict ${s.passed ? "pass" : "fail"}`}>
        <span className="verdict-icon">{s.passed ? "✓" : "✕"}</span>
        <div>
          <div className="verdict-title">{s.passed ? "ผ่าน" : "ไม่ผ่าน"}</div>
          <div className="verdict-sub">{s.passed ? "ไม่พบผู้ไม่สวมหมวกนิรภัย" : `พบผู้ไม่สวมหมวกนิรภัย ${s.noHardhat} คน`}</div>
        </div>
      </div>
      <div className="stats">
        <Stat label="จำนวนคน" value={s.persons} />
        <Stat label="สวมหมวก" value={s.hardhat} tone="good" />
        <Stat label="ไม่สวมหมวก" value={s.noHardhat} tone={s.noHardhat ? "bad" : undefined} />
        <Stat label="ไม่สวมเสื้อสะท้อนแสง" value={s.noVest} tone={s.noVest ? "warn" : undefined} />
        <Stat label="เวลาที่โมเดลใช้" value={`${inferenceMs.toFixed(1)} ms`} />
        <Stat label="เวลาส่งรูปไป-กลับ" value={`${Math.round(roundtripMs)} ms`} />
      </div>
      <p className="muted small">โมเดล {model} · เกณฑ์: ไม่ผ่านเมื่อพบ NO-Hardhat อย่างน้อย 1 กรอบ</p>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: string | number; tone?: "good" | "bad" | "warn" }) {
  return (
    <div className={`stat ${tone ?? ""}`}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
