// Business Rules BR-01 … BR-07 against docs/TEST-DATA.md §3–§7 and §12.
import { describe, expect, it } from 'vitest';
import {
  HELMET_FAIL_MIN,
  MAX_FILE_BYTES,
  MAX_PHOTOS_PER_UPLOAD,
  MIN_PHOTOS_PER_UPLOAD,
  PASS_RATE_RED_BELOW_PERCENT,
  REPORT_READY_HOUR,
  REPORT_READY_MINUTE,
  VEST_FAIL_MIN,
  VEST_WARN_MIN,
  bangkokDate,
  bangkokIso,
  checkPhotoCount,
  formatPassRate,
  isCountAllowed,
  isRed,
  isReportReady,
  isSizeAllowed,
  isValidDateString,
  judge,
  passRate,
  uploadLimits,
} from '@/lib/rules';

describe('constants (DESIGN §9)', () => {
  it('has the documented thresholds', () => {
    expect(HELMET_FAIL_MIN).toBe(1);
    expect(VEST_FAIL_MIN).toBe(2);
    expect(VEST_WARN_MIN).toBe(1);
    expect(MAX_FILE_BYTES).toBe(15_728_640);
    expect(MAX_PHOTOS_PER_UPLOAD).toBe(50);
    expect(MIN_PHOTOS_PER_UPLOAD).toBe(1);
    expect(PASS_RATE_RED_BELOW_PERCENT).toBe(90);
    expect(REPORT_READY_HOUR).toBe(18);
    expect(REPORT_READY_MINUTE).toBe(0);
  });
});

describe('§4 judge(h, v) — BR-01 … BR-03', () => {
  const rows: [string, number, number, 'PASS' | 'WARN' | 'FAIL'][] = [
    ['R-1 h0_v0', 0, 0, 'PASS'],
    ['R-2 h1_v0', 1, 0, 'FAIL'],
    ['R-3 h2_v0', 2, 0, 'FAIL'],
    ['R-4 h0_v1', 0, 1, 'WARN'],
    ['R-5 h0_v2', 0, 2, 'FAIL'],
    ['R-6 h0_v3', 0, 3, 'FAIL'],
    ['R-7 h1_v1', 1, 1, 'FAIL'],
    ['R-8 h1_v3', 1, 3, 'FAIL'],
  ];
  it.each(rows)('%s → %s', (_id, h, v, expected) => {
    expect(judge(h, v)).toBe(expected);
  });

  it('rejects counts that are not non-negative integers', () => {
    expect(() => judge(-1, 0)).toThrow();
    expect(() => judge(0, 1.5)).toThrow();
    expect(() => judge(Number.NaN, 0)).toThrow();
  });
});

describe('§5 isSizeAllowed — BR-05', () => {
  const rows: [string, number, boolean][] = [
    ['F-1 14.9 MB', 15_623_782, true],
    ['F-2 15.0 MB', 15_728_640, true],
    ['F-3 15 MB + 1 byte', 15_728_641, false],
    ['F-4 15.1 MB', 15_833_498, false],
    ['F-5 ~200 KB', 200_000, true],
    ['F-6 ~300 KB', 300_000, true],
  ];
  it.each(rows)('%s (%i bytes) → %s', (_id, size, ok) => {
    expect(isSizeAllowed(size)).toBe(ok);
  });
});

describe('§6 photo count per upload — BR-06', () => {
  const rows: [string, number, 'OK' | 'TOO_FEW' | 'TOO_MANY'][] = [
    ['N-1', 0, 'TOO_FEW'],
    ['N-2', 1, 'OK'],
    ['N-3', 49, 'OK'],
    ['N-4', 50, 'OK'],
    ['N-5', 51, 'TOO_MANY'],
  ];
  it.each(rows)('%s: %i photos → %s', (_id, n, expected) => {
    expect(checkPhotoCount(n)).toBe(expected);
    expect(isCountAllowed(n)).toBe(expected === 'OK');
  });

  it('upload page limits come from the same rule', () => {
    const l = uploadLimits();
    expect(isCountAllowed(l.max_photos)).toBe(true);
    expect(isCountAllowed(l.max_photos + 1)).toBe(false);
    expect(l.max_photos).toBe(50);
    expect(l.max_file_bytes).toBe(15_728_640);
  });

  it('non-integers are never allowed', () => {
    expect(isCountAllowed(2.5)).toBe(false);
    expect(isCountAllowed(Number.NaN)).toBe(false);
  });
});

describe('§7 report readiness — BR-07 (Asia/Bangkok)', () => {
  const D3 = '2026-11-18';
  const rows: [string, string, boolean][] = [
    ['T-1 17:59:00', '2026-11-18T17:59:00+07:00', false],
    ['T-1 17:59:59', '2026-11-18T17:59:59+07:00', false],
    ['T-2 18:00:00', '2026-11-18T18:00:00+07:00', true],
    ['T-3 18:01:00', '2026-11-18T18:01:00+07:00', true],
    ['T-4 18:30:00', '2026-11-18T18:30:00+07:00', true],
    ['18:00 Bangkok = 11:00 UTC', '2026-11-18T11:00:00Z', true],
    ['10:59:59 UTC', '2026-11-18T10:59:59Z', false],
  ];
  it.each(rows)('%s → ready=%s', (_id, iso, ready) => {
    expect(isReportReady(new Date(iso), D3)).toBe(ready);
  });

  it('a past day is ready, a future day is not', () => {
    expect(isReportReady(new Date('2026-11-18T08:00:00+07:00'), '2026-11-17')).toBe(true);
    expect(isReportReady(new Date('2026-11-18T20:00:00+07:00'), '2026-11-19')).toBe(false);
  });

  it('upload_date follows Thai calendar date (T-4 … T-6)', () => {
    expect(bangkokDate(new Date('2026-11-18T18:30:00+07:00'))).toBe('2026-11-18'); // T-4
    expect(bangkokDate(new Date('2026-11-18T23:59:59+07:00'))).toBe('2026-11-18'); // T-5
    expect(bangkokDate(new Date('2026-11-19T00:00:00+07:00'))).toBe('2026-11-19'); // T-6
    expect(bangkokDate(new Date('2026-11-18T17:00:00Z'))).toBe('2026-11-19'); // T-6 in UTC
    expect(bangkokIso(new Date('2026-11-18T11:00:00Z'))).toBe('2026-11-18T18:00:00+07:00');
  });

  it('validates dates', () => {
    expect(isValidDateString('2026-11-18')).toBe(true);
    expect(isValidDateString('2026-02-30')).toBe(false);
    expect(isValidDateString('18/11/2026')).toBe(false);
    expect(() => isReportReady(new Date(), 'bad')).toThrow();
  });
});

describe('§3 pass rate and red flag — BR-04', () => {
  // [id, pass, with result, text, red]
  const rows: [string, number, number, string | null, boolean][] = [
    ['P-1 269/300', 269, 300, '89.67', true],
    ['P-2 270/300', 270, 300, '90.00', false],
    ['P-3 271/300', 271, 300, '90.33', false],
    ['P-4 no photo', 0, 0, null, false],
    ['P-5 9/10 (warn not counted)', 9, 10, '90.00', false],
    ['P-6 9/9 (failed not in divisor)', 9, 9, '100.00', false],
    ['P-7 270/300 after override', 270, 300, '90.00', false],
    ['P-8 8/10', 8, 10, '80.00', true],
    ['P-9 0/1', 0, 1, '0.00', true],
    ['T-4 1/2', 1, 2, '50.00', true],
  ];
  it.each(rows)('%s → %s, red=%s', (_id, pass, n, text, red) => {
    expect(formatPassRate(pass, n)).toBe(text);
    expect(isRed(pass, n)).toBe(red);
  });

  it('compares the unrounded value (89.67 would round to 90)', () => {
    expect(Math.round(passRate(269, 300)!)).toBe(90);
    expect(isRed(269, 300)).toBe(true);
    expect(passRate(0, 0)).toBeNull();
  });

  it('rejects impossible input', () => {
    expect(() => isRed(5, 4)).toThrow();
    expect(() => passRate(-1, 4)).toThrow();
  });
});

describe('§12 boundary coverage (below / equal / above)', () => {
  it('BR-01 (H = 1): R-1 / R-2 / R-3', () => {
    expect([judge(0, 0), judge(1, 0), judge(2, 0)]).toEqual(['PASS', 'FAIL', 'FAIL']);
  });
  it('BR-02 (V = 2): R-4 / R-5 / R-6', () => {
    expect([judge(0, 1), judge(0, 2), judge(0, 3)]).toEqual(['WARN', 'FAIL', 'FAIL']);
  });
  it('BR-03 (V = 1): R-1 / R-4 / R-5', () => {
    expect([judge(0, 0), judge(0, 1), judge(0, 2)]).toEqual(['PASS', 'WARN', 'FAIL']);
  });
  it('BR-04 (90%): P-1 / P-2 · P-5 · P-7 / P-3', () => {
    expect(isRed(269, 300)).toBe(true);
    expect([isRed(270, 300), isRed(9, 10), isRed(270, 300)]).toEqual([false, false, false]);
    expect(isRed(271, 300)).toBe(false);
  });
  it('BR-05 (15 MB): F-1 / F-2 / F-3 · F-4', () => {
    expect([isSizeAllowed(15_623_782), isSizeAllowed(15_728_640)]).toEqual([true, true]);
    expect([isSizeAllowed(15_728_641), isSizeAllowed(15_833_498)]).toEqual([false, false]);
  });
  it('BR-06 (50 photos): N-3 / N-4 / N-5', () => {
    expect([isCountAllowed(49), isCountAllowed(50), isCountAllowed(51)]).toEqual([true, true, false]);
  });
  it('BR-07 (18:00): T-1 / T-2 / T-3', () => {
    const d = '2026-11-18';
    expect([
      isReportReady(new Date('2026-11-18T17:59:00+07:00'), d),
      isReportReady(new Date('2026-11-18T18:00:00+07:00'), d),
      isReportReady(new Date('2026-11-18T18:01:00+07:00'), d),
    ]).toEqual([false, true, true]);
  });
});
