// canAccess(user, action, siteId) — DESIGN §5.2 and TEST-DATA §8.
import { describe, expect, it } from 'vitest';
import { canAccess, siteCondition, siteScope, type Action } from '@/lib/access';
import type { SessionUser } from '@/lib/auth';

const mk = (id: number, role: SessionUser['role'], site: number | null): SessionUser => ({
  id,
  email: `${role}${id}@sitesafe.test`,
  full_name: role,
  role,
  site_id: site,
  site_code: site === null ? null : `SITE-${'ABC'[site - 1]}`,
  site_name: null,
});

const U1 = mk(1, 'manager', null);
const U2 = mk(2, 'supervisor', 1); // SITE-A
const U5 = mk(5, 'executive', null);
const SITE_A = 1;
const SITE_B = 2;

const status = (u: SessionUser | null, a: Action, site?: number | null) => {
  const d = canAccess(u, a, site);
  return d.ok ? 200 : d.status;
};

describe('public routes', () => {
  it.each(['health.read', 'auth.login', 'test.reset'] as Action[])('%s needs no session', (a) => {
    expect(status(null, a)).toBe(200);
  });
});

describe('not logged in → 401 (A-1, A-2)', () => {
  it.each([
    'auth.logout', 'auth.me', 'upload.create', 'upload.add_photo', 'upload.view',
    'photo.view', 'photo.override', 'override.history', 'report.view',
  ] as Action[])('%s', (a) => {
    expect(status(null, a)).toBe(401);
    expect(status(null, a, SITE_B)).toBe(401);
  });
});

describe('executive: reports only (FR-19)', () => {
  it('A-7 cannot upload → 403', () => expect(status(U5, 'upload.create')).toBe(403));
  it('A-8 cannot override → 403', () => expect(status(U5, 'photo.override', SITE_B)).toBe(403));
  it('cannot list or open photos → 403', () => {
    expect(status(U5, 'photo.view')).toBe(403);
    expect(status(U5, 'photo.view', SITE_B)).toBe(403);
    expect(status(U5, 'upload.view', SITE_B)).toBe(403);
    expect(status(U5, 'override.history', SITE_B)).toBe(403);
  });
  it('A-9 reads every site report', () => {
    expect(status(U5, 'report.view')).toBe(200);
    expect(status(U5, 'report.view', SITE_B)).toBe(200);
    expect(siteScope(U5)).toBeNull();
  });
  it('may call me / logout', () => {
    expect(status(U5, 'auth.me')).toBe(200);
    expect(status(U5, 'auth.logout')).toBe(200);
  });
});

describe('supervisor: own site only (FR-20)', () => {
  it('uploads to own site only', () => {
    expect(status(U2, 'upload.create', SITE_A)).toBe(200);
    expect(status(U2, 'upload.add_photo', SITE_A)).toBe(200);
    expect(status(U2, 'upload.add_photo', SITE_B)).toBe(404);
  });
  it('A-4 photo of another site → 404', () => {
    expect(status(U2, 'photo.view', SITE_B)).toBe(404);
    expect(status(U2, 'photo.view', SITE_A)).toBe(200);
  });
  it('A-10 override of another site → 404', () => {
    expect(status(U2, 'photo.override', SITE_B)).toBe(404);
    expect(status(U2, 'photo.override', SITE_A)).toBe(200);
  });
  it('A-5 report scope is the own site', () => {
    expect(status(U2, 'report.view', SITE_A)).toBe(200);
    expect(status(U2, 'report.view', SITE_B)).toBe(404);
    expect(siteScope(U2)).toBe(SITE_A);
  });
  it('history of another site → 404', () => {
    expect(status(U2, 'override.history', SITE_B)).toBe(404);
  });
});

describe('manager: every site, no upload (FR-21)', () => {
  it('views, overrides and reads history on all sites', () => {
    for (const s of [1, 2, 3]) {
      expect(status(U1, 'photo.view', s)).toBe(200);
      expect(status(U1, 'photo.override', s)).toBe(200);
      expect(status(U1, 'override.history', s)).toBe(200);
      expect(status(U1, 'report.view', s)).toBe(200);
    }
    expect(siteScope(U1)).toBeNull();
  });
  it('does not upload (supervisor only)', () => {
    expect(status(U1, 'upload.create')).toBe(403);
  });
});

describe('defensive cases', () => {
  it('a supervisor without a site never gets a site resource', () => {
    const broken = mk(9, 'supervisor', null);
    expect(status(broken, 'photo.view', SITE_A)).toBe(404);
    expect(() => siteScope(broken)).toThrow();
  });
});

describe('siteCondition — supervisor SQL always carries WHERE site_id', () => {
  it('supervisor: appends its own site as the next parameter', () => {
    const params: unknown[] = ['photo-id'];
    expect(siteCondition(U2, 'p.site_id', params)).toBe(' AND p.site_id = $2');
    expect(params).toEqual(['photo-id', SITE_A]);
  });
  it('manager and executive: no site condition (all sites)', () => {
    const params: unknown[] = [];
    expect(siteCondition(U1, 'p.site_id', params)).toBe('');
    expect(siteCondition(U5, 'site_id', params)).toBe('');
    expect(params).toEqual([]);
  });
  it('a supervisor without a site is refused, never widened to all sites', () => {
    expect(() => siteCondition(mk(9, 'supervisor', null), 'p.site_id', [])).toThrow();
  });
  it('only plain column names are accepted', () => {
    expect(() => siteCondition(U2, 'p.site_id OR 1=1', [])).toThrow();
  });
});
