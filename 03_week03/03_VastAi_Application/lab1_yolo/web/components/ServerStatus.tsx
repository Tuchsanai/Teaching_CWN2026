"use client";
// ไฟสถานะการเชื่อมต่อ AI server ที่มุมขวาบน
import { useEffect, useState } from "react";

export default function ServerStatus() {
  const [s, setS] = useState<{ ok: boolean; model: string | null } | null>(null);
  useEffect(() => {
    const load = () => fetch("/api/health").then((r) => r.json()).then(setS).catch(() => setS({ ok: false, model: null }));
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);
  if (!s) return <span className="status">กำลังตรวจ AI server…</span>;
  return (
    <span className={`status ${s.ok ? "on" : "off"}`}>
      <i />
      {s.ok ? `AI server พร้อม · ${s.model}` : "ต่อ AI server ไม่ได้"}
    </span>
  );
}
