// The seed (TEST-DATA §1–§3) gives the report values of P-1 … P-9 when aggregated
// the same way as GET /api/reports/daily (DESIGN §9.2).
import { describe, expect, it } from 'vitest';
import { SEED_SITES, SEED_USERS, __seedForTests } from '@/db/seed';
import { MAX_PHOTOS_PER_UPLOAD, formatPassRate, isRed } from '@/lib/rules';

const seed = __seedForTests.buildSeed();

function report(date: string, siteId: number) {
  const ps = seed.photos.filter((p) => p.upload_date === date && p.site_id === siteId);
  const done = ps.filter((p) => p.status === 'DONE');
  const pass = done.filter((p) => p.current_result === 'PASS').length;
  return {
    taken: ps.length,
    withResult: done.length,
    pass,
    fail: done.filter((p) => p.current_result === 'FAIL').length,
    h: done.reduce((s, p) => s + (p.model_h ?? 0), 0),
    edited: ps.filter((p) => p.is_overridden).length,
    failed: ps.filter((p) => p.status === 'FAILED').length,
    rate: formatPassRate(pass, done.length),
    red: isRed(pass, done.length),
  };
}

describe('seed counts', () => {
  it('3 sites · 5 users · 1,233 photos · unique ids', () => {
    expect(SEED_SITES.length).toBe(3);
    expect(SEED_USERS.length).toBe(5);
    expect(seed.photos.length).toBe(1233);
    expect(new Set(seed.photos.map((p) => p.id)).size).toBe(1233);
    for (const b of seed.batches) {
      const n = seed.photos.filter((p) => p.batch_id === b.id).length;
      expect(n).toBe(b.declared_count);
      expect(b.declared_count).toBeGreaterThanOrEqual(1);
      expect(b.declared_count).toBeLessThanOrEqual(MAX_PHOTOS_PER_UPLOAD);
    }
  });

  it('is deterministic', () => {
    const again = __seedForTests.buildSeed();
    expect(again.photos.map((p) => p.id)).toEqual(seed.photos.map((p) => p.id));
    expect(again.overridePhotoId).toBe(seed.overridePhotoId);
  });

  it('detections = H + V boxes per DONE photo', () => {
    for (const p of seed.photos.slice(0, 400)) {
      const n = seed.detections.filter((d) => d.photo_id === p.id).length;
      expect(n).toBe(p.status === 'DONE' ? (p.model_h ?? 0) + (p.model_v ?? 0) : 0);
    }
  });
});

describe('TEST-DATA §3 report rows', () => {
  const rows: [string, string, number, ReturnType<typeof report>['taken'], number, number, number, number, number, number, string | null, boolean][] = [
    // id, date, site, taken, withResult, pass, fail, h, edited, failed, rate, red
    ['P-1', '2026-11-16', 1, 300, 300, 269, 20, 15, 0, 0, '89.67', true],
    ['P-2', '2026-11-16', 2, 300, 300, 270, 20, 20, 0, 0, '90.00', false],
    ['P-3', '2026-11-16', 3, 300, 300, 271, 20, 20, 0, 0, '90.33', false],
    ['P-4', '2026-11-17', 1, 0, 0, 0, 0, 0, 0, 0, null, false],
    ['P-5', '2026-11-17', 2, 10, 10, 9, 0, 0, 0, 0, '90.00', false],
    ['P-6', '2026-11-17', 3, 10, 9, 9, 0, 0, 0, 1, '100.00', false],
    ['P-7', '2026-11-18', 1, 300, 300, 270, 19, 15, 1, 0, '90.00', false],
    ['P-8', '2026-11-18', 2, 12, 10, 8, 1, 1, 0, 0, '80.00', true],
    ['P-9', '2026-11-18', 3, 1, 1, 0, 1, 2, 0, 0, '0.00', true],
  ];
  it.each(rows)('%s', (_id, date, site, taken, withResult, pass, fail, h, edited, failed, rate, red) => {
    expect(report(date, site)).toEqual({ taken, withResult, pass, fail, h, edited, failed, rate, red });
  });

  it('problems view counts (FR-11): D1·SITE-A 31 · D3·SITE-A 30', () => {
    const problems = (date: string, site: number) =>
      seed.photos.filter(
        (p) => p.upload_date === date && p.site_id === site && p.status === 'DONE' &&
          (p.current_result === 'FAIL' || p.current_result === 'WARN'),
      ).length;
    expect(problems('2026-11-16', 1)).toBe(31);
    expect(problems('2026-11-18', 1)).toBe(30);
  });
});
