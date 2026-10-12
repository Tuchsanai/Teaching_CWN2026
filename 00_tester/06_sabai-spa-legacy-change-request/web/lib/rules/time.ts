// วันที่/เวลาแบบ Asia/Bangkok (UTC+7 ไม่มี DST) · วันที่เป็นสตริง YYYY-MM-DD

export const BKK_OFFSET_MS = 7 * 3600 * 1000;
const DAY_MS = 86400000;

function parseDate(d: string): number {
  const [y, m, day] = d.split("-").map(Number);
  return Date.UTC(y, m - 1, day);
}

function fmtDate(ms: number): string {
  const d = new Date(ms);
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")}`;
}

export function isDateString(d: unknown): d is string {
  if (typeof d !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(d)) return false;
  return fmtDate(parseDate(d)) === d;
}

export function addDays(date: string, n: number): string {
  return fmtDate(parseDate(date) + n * DAY_MS);
}

/** จำนวนวันจาก a ถึง b (b − a) */
export function diffDays(a: string, b: string): number {
  return Math.round((parseDate(b) - parseDate(a)) / DAY_MS);
}

export function bangkokDate(at: Date): string {
  return fmtDate(at.getTime() + BKK_OFFSET_MS);
}

export function bangkokTime(at: Date): string {
  const d = new Date(at.getTime() + BKK_OFFSET_MS);
  return `${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")}`;
}

export function toInstant(date: string, time: string): Date {
  return new Date(`${date}T${time}:00+07:00`);
}

export function yearMonth(date: string): number {
  return Number(date.slice(0, 4)) * 100 + Number(date.slice(5, 7));
}

export function minutesOf(time: string): number {
  const [h, m] = time.split(":").map(Number);
  return h * 60 + m;
}

export function timeOf(minutes: number): string {
  return `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`;
}

export function isTimeString(t: unknown): t is string {
  return typeof t === "string" && /^([01]\d|2[0-3]):[0-5]\d$/.test(t);
}
