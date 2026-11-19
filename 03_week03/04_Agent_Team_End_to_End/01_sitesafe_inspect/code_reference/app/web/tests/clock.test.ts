// System clock set by the test reset (DESIGN §7.2) and upload_date in Thai time (FR-04, T-4 … T-6).
import { afterEach, describe, expect, it, vi } from 'vitest';
import { now, nowIso, parseInstant, setNow, todayBangkok } from '@/lib/clock';

afterEach(() => {
  setNow(null);
  vi.useRealTimers();
});

describe('clock', () => {
  it('defaults to real time', () => {
    expect(Math.abs(now().getTime() - Date.now())).toBeLessThan(1000);
  });

  it('can be set from the reset body', () => {
    setNow(parseInstant('2026-11-18T17:59:00+07:00'));
    expect(nowIso()).toBe('2026-11-18T17:59:00+07:00');
    expect(todayBangkok()).toBe('2026-11-18');
  });

  it('T-5: a set time stays fixed until the next reset, even as real time passes', () => {
    vi.useFakeTimers();
    setNow(parseInstant('2026-11-18T23:59:59+07:00'));
    vi.advanceTimersByTime(5_000);
    expect(nowIso()).toBe('2026-11-18T23:59:59+07:00');
    expect(todayBangkok()).toBe('2026-11-18');
    vi.advanceTimersByTime(24 * 3600 * 1000);
    expect(todayBangkok()).toBe('2026-11-18');
    // The next reset replaces it.
    setNow(parseInstant('2026-11-19T00:00:00+07:00'));
    expect(todayBangkok()).toBe('2026-11-19');
  });

  it('a reset without now returns to real time', () => {
    setNow(parseInstant('2026-11-18T23:59:59+07:00'));
    setNow(null);
    expect(Math.abs(now().getTime() - Date.now())).toBeLessThan(1000);
  });

  it('T-5 / T-6: day boundary is midnight Thai time, not UTC', () => {
    setNow(parseInstant('2026-11-18T23:59:59+07:00'));
    expect(todayBangkok()).toBe('2026-11-18');
    setNow(parseInstant('2026-11-18T17:00:00Z'));
    expect(todayBangkok()).toBe('2026-11-19');
  });

  it('parseInstant needs an explicit offset', () => {
    expect(parseInstant('2026-11-18T17:59:00')).toBeNull();
    expect(parseInstant('yesterday')).toBeNull();
    expect(parseInstant(42)).toBeNull();
    expect(parseInstant('2026-11-18T17:59:00Z')?.toISOString()).toBe('2026-11-18T17:59:00.000Z');
  });
});
