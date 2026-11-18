"use client";
import { useEffect, useState } from "react";

export default function HealthBadge() {
  const [h, setH] = useState<{ ready: boolean; model?: string; error?: string } | null>(null);
  useEffect(() => {
    let alive = true;
    const tick = () => fetch("/api/health", { cache: "no-store" }).then((r) => r.json()).then((j) => alive && setH(j)).catch(() => alive && setH({ ready: false }));
    tick();
    const t = setInterval(tick, 15000);
    return () => { alive = false; clearInterval(t); };
  }, []);
  const cls = h === null ? "wait" : h.ready ? "ok" : "down";
  const text = h === null ? "กำลังตรวจ AI server…" : h.ready ? "AI server พร้อม" : "AI server ไม่พร้อม";
  return (
    <span className={`health ${cls}`} title={h?.model ?? h?.error ?? ""}>
      <span className="dot" />{text}
    </span>
  );
}
