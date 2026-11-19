'use client';
/**
 * FR-21: แจ้งหัวหน้าทีม (และเจ้าของ) เมื่อมีงานปกติค้างเกินกำหนด — ตัวเลขข้างเมนู "ค้างเกินกำหนด"
 * อ่าน `overdue` จาก W23 GET /api/queue ทุก 60 วินาที (เมนูนี้แสดงเฉพาะหัวหน้าและเจ้าของ)
 */
import { useEffect, useState } from 'react';

export default function OverdueBadge() {
  const [n, setN] = useState<number | null>(null);
  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const res = await fetch('/api/queue', { cache: 'no-store', credentials: 'same-origin' });
        if (!res.ok) return;
        const body = (await res.json()) as { overdue?: number };
        if (alive) setN(typeof body.overdue === 'number' ? body.overdue : null);
      } catch {
        /* เงียบไว้: เป็นแค่ตัวช่วยแจ้งเตือน */
      }
    };
    load();
    const t = setInterval(load, 60_000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);
  if (!n) return null;
  return (
    <span className="badge warn" title={`งานปกติค้างเกิน 120 นาที ${n} ใบ`}>
      {n}
    </span>
  );
}
