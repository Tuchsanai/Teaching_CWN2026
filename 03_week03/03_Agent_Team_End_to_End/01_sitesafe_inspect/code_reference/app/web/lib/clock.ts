/**
 * System clock of the web service (DESIGN §7.1, §7.2).
 *
 * Normally the real time. POST /api/test/reset may set it to a given instant
 * (for BR-07 and upload_date tests, TEST-DATA T-1 … T-6); the clock then stays
 * fixed at exactly that instant until the next reset, so a test set at
 * 23:59:59 still gets that day however long the upload takes.
 * State lives on globalThis so every route bundle in the process shares it.
 */
import { bangkokDate, bangkokIso } from './rules';

type ClockState = { fixedMs: number | null };

const KEY = Symbol.for('sitesafe.clock');
const g = globalThis as unknown as Record<symbol, ClockState | undefined>;

function state(): ClockState {
  let s = g[KEY];
  if (!s) {
    s = { fixedMs: null };
    g[KEY] = s;
  }
  return s;
}

/** Current system time: the instant set by the test reset, otherwise real time. */
export function now(): Date {
  const fixed = state().fixedMs;
  return new Date(fixed === null ? Date.now() : fixed);
}

/** Fix the clock at `instant` until the next call; null → real time. */
export function setNow(instant: Date | null): void {
  state().fixedMs = instant === null ? null : instant.getTime();
}

/** Today's date in Thailand (YYYY-MM-DD) according to the system clock. */
export function todayBangkok(): string {
  return bangkokDate(now());
}

/** Current system time as ISO 8601 with +07:00. */
export function nowIso(): string {
  return bangkokIso(now());
}

/** Parse an ISO 8601 timestamp that carries an explicit offset or Z. */
export function parseInstant(value: unknown): Date | null {
  if (typeof value !== 'string') return null;
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,9})?)?(Z|[+-]\d{2}:\d{2})$/.test(value)) return null;
  const t = Date.parse(value);
  return Number.isNaN(t) ? null : new Date(t);
}
