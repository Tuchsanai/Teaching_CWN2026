// นาฬิกาเดียวของระบบ (NFR-13): app_setting.test_today → env TODAY → เวลาจริง
// ทุกกฎที่ใช้วันที่ (BR-03/07/13/14/16) ต้องเอา "ตอนนี้" จากไฟล์นี้เท่านั้น
import { query } from "./db.ts";
import { config } from "./config.ts";
import { bangkokDate } from "./rules/time.ts";

/** "2026-10-10T10:00" (ไม่มีโซน) ถือเป็นเวลาไทย */
export function parseClockValue(v: string): Date | null {
  const s = v.trim();
  if (!s) return null;
  const hasZone = /([+-]\d{2}:?\d{2}|Z)$/.test(s);
  const iso = /^\d{4}-\d{2}-\d{2}$/.test(s) ? `${s}T00:00:00+07:00` : hasZone ? s : `${s}+07:00`;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? null : d;
}

export async function now(): Promise<Date> {
  if (config.allowTestReset) {
    try {
      const r = await query<{ value: string }>("SELECT value FROM app_setting WHERE key = 'test_today'");
      const d = r.rows[0] ? parseClockValue(r.rows[0].value) : null;
      if (d) return d;
    } catch {
      // db ไม่พร้อม → ใช้ค่าถัดไป
    }
  }
  if (process.env.TODAY) {
    const d = parseClockValue(process.env.TODAY);
    if (d) return d;
  }
  return new Date();
}

export async function clock(): Promise<{ now: Date; today: string }> {
  const n = await now();
  return { now: n, today: bangkokDate(n) };
}
