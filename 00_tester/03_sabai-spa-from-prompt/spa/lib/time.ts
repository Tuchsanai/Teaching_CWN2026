// Shared (server + browser) date/time helpers.
// All shop rules run in Bangkok time (UTC+7, no daylight saving),
// so we shift by a fixed offset instead of relying on the host TZ.

export const SHOP_PHONE = "02-123-4567";
export const OPEN_MIN = 10 * 60; // 10:00 (BR-01)
export const CLOSE_MIN = 22 * 60; // 22:00 (BR-01, BR-03)
export const SLOT_STEP = 30; // minutes (BR-02)
export const BOOK_MIN_DAYS = 1; // tomorrow (BR-05)
export const BOOK_MAX_DAYS = 30; // +30 days (BR-05)
export const CANCEL_HOURS = 24; // BR-09

const BKK_OFFSET_MS = 7 * 60 * 60 * 1000;
const DAY_MS = 24 * 60 * 60 * 1000;

export type BkkParts = { y: number; m: number; d: number; h: number; min: number; s: number; dow: number };

export function bkkParts(date: Date): BkkParts {
  const x = new Date(date.getTime() + BKK_OFFSET_MS);
  return {
    y: x.getUTCFullYear(),
    m: x.getUTCMonth() + 1,
    d: x.getUTCDate(),
    h: x.getUTCHours(),
    min: x.getUTCMinutes(),
    s: x.getUTCSeconds(),
    dow: x.getUTCDay(),
  };
}

/** "YYYY-MM-DD" of an instant, in Bangkok time */
export function bkkDate(date: Date): string {
  return new Date(date.getTime() + BKK_OFFSET_MS).toISOString().slice(0, 10);
}

export function isDateStr(s: unknown): s is string {
  if (typeof s !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
  const t = Date.parse(s + "T00:00:00Z");
  return !Number.isNaN(t) && new Date(t).toISOString().slice(0, 10) === s;
}

export function addDays(dateStr: string, n: number): string {
  const t = Date.parse(dateStr + "T00:00:00Z") + n * DAY_MS;
  return new Date(t).toISOString().slice(0, 10);
}

/** whole days from a to b (b - a) */
export function diffDays(a: string, b: string): number {
  return Math.round((Date.parse(b + "T00:00:00Z") - Date.parse(a + "T00:00:00Z")) / DAY_MS);
}

export function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

export function minToHHMM(m: number): string {
  return `${pad2(Math.floor(m / 60))}:${pad2(m % 60)}`;
}

export function hhmmToMin(s: unknown): number | null {
  if (typeof s !== "string" || !/^\d{2}:\d{2}$/.test(s)) return null;
  const [h, m] = s.split(":").map(Number);
  if (h > 23 || m > 59) return null;
  return h * 60 + m;
}

/** instant for a Bangkok wall-clock date + minutes after midnight */
export function bkkInstant(dateStr: string, minutes: number): Date {
  return new Date(`${dateStr}T${minToHHMM(minutes)}:00+07:00`);
}

/** every start time shown on the booking screen: 10:00 … 21:30 (BR-01, BR-02) */
export function allSlotStarts(): number[] {
  const out: number[] = [];
  for (let m = OPEN_MIN; m < CLOSE_MIN; m += SLOT_STEP) out.push(m);
  return out;
}

/** BR-01/02/03: on the 30-min grid, not before opening, and must finish by 22:00 */
export function slotFits(startMin: number, durationMin: number): boolean {
  return startMin >= OPEN_MIN && startMin % SLOT_STEP === 0 && startMin + durationMin <= CLOSE_MIN;
}

export function bookableRange(now: Date): { today: string; min: string; max: string } {
  const today = bkkDate(now);
  return { today, min: addDays(today, BOOK_MIN_DAYS), max: addDays(today, BOOK_MAX_DAYS) };
}

/** BR-05: tomorrow … +30 days (inclusive) */
export function isBookableDate(dateStr: string, now: Date): boolean {
  if (!isDateStr(dateStr)) return false;
  const { min, max } = bookableRange(now);
  return dateStr >= min && dateStr <= max;
}

/** BR-09: may cancel when the appointment is at least 24 h away */
export function canCancel(startAt: Date, now: Date): boolean {
  return startAt.getTime() - now.getTime() >= CANCEL_HOURS * 60 * 60 * 1000;
}

const LOCALES = { th: "th-TH-u-ca-gregory", en: "en-GB", zh: "zh-CN" } as const;

export function formatDate(dateStr: string, lang: "th" | "en" | "zh", withWeekday = false): string {
  if (!isDateStr(dateStr)) return dateStr;
  const d = new Date(dateStr + "T00:00:00Z");
  return new Intl.DateTimeFormat(LOCALES[lang], {
    timeZone: "UTC",
    day: "numeric",
    month: "short",
    year: "numeric",
    ...(withWeekday ? { weekday: "short" } : {}),
  }).format(d);
}

export function formatMonthYear(y: number, m: number, lang: "th" | "en" | "zh"): string {
  const d = new Date(Date.UTC(y, m - 1, 1));
  return new Intl.DateTimeFormat(LOCALES[lang], { timeZone: "UTC", month: "long", year: "numeric" }).format(d);
}

export function weekdayShort(lang: "th" | "en" | "zh"): string[] {
  // Sunday first
  const out: string[] = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(Date.UTC(2023, 0, 1 + i)); // 2023-01-01 is a Sunday
    out.push(new Intl.DateTimeFormat(LOCALES[lang], { timeZone: "UTC", weekday: "narrow" }).format(d));
  }
  return out;
}

export function formatBaht(n: number): string {
  const sign = n < 0 ? "-" : "";
  return `${sign}฿${Math.abs(Math.round(n)).toLocaleString("en-US")}`;
}
