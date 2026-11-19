/**
 * Authorization (DESIGN §5.2, §10 · FR-19–FR-22 · NFR-06).
 *
 * canAccess(user, action, siteId) is the single permission function. Every
 * Route Handler calls it on the server for every request:
 *   not logged in → 401 · role not allowed → 403 · resource of another site → 404.
 * Supervisor queries must always be filtered with siteScope(user) (WHERE site_id = …).
 */
import { NextResponse, type NextRequest } from 'next/server';
import { getSessionUser, type Role, type SessionUser } from './auth';

export type Action =
  // public (no session)
  | 'health.read'
  | 'auth.login'
  | 'test.reset'
  // any logged-in role
  | 'auth.logout'
  | 'auth.me'
  // supervisor of the site
  | 'upload.create'
  | 'upload.add_photo'
  // manager: all sites · supervisor: own site
  | 'upload.view'
  | 'photo.view'
  | 'photo.override'
  | 'override.history'
  // manager + executive: all sites · supervisor: own site
  | 'report.view';

type Rule = { public?: true; roles?: readonly Role[]; allSites?: readonly Role[] };

const RULES: Readonly<Record<Action, Rule>> = {
  'health.read': { public: true },
  'auth.login': { public: true },
  'test.reset': { public: true }, // gated by ENABLE_TEST_RESET + X-Test-Key in the route
  'auth.logout': { roles: ['manager', 'supervisor', 'executive'], allSites: ['manager', 'supervisor', 'executive'] },
  'auth.me': { roles: ['manager', 'supervisor', 'executive'], allSites: ['manager', 'supervisor', 'executive'] },
  'upload.create': { roles: ['supervisor'], allSites: [] },
  'upload.add_photo': { roles: ['supervisor'], allSites: [] },
  'upload.view': { roles: ['manager', 'supervisor'], allSites: ['manager'] },
  'photo.view': { roles: ['manager', 'supervisor'], allSites: ['manager'] },
  'photo.override': { roles: ['manager', 'supervisor'], allSites: ['manager'] },
  'override.history': { roles: ['manager', 'supervisor'], allSites: ['manager'] },
  'report.view': { roles: ['manager', 'supervisor', 'executive'], allSites: ['manager', 'executive'] },
};

export type Decision = { ok: true } | { ok: false; status: 401 | 403 | 404 };

const ALLOW: Decision = { ok: true };

/**
 * @param siteId site of the resource; undefined/null when the request does not
 *               target one site (lists are then filtered with siteScope()).
 */
export function canAccess(user: SessionUser | null, action: Action, siteId?: number | null): Decision {
  const rule = RULES[action];
  if (!rule) return { ok: false, status: 403 };
  if (rule.public) return ALLOW;
  if (!user) return { ok: false, status: 401 };
  if (!rule.roles?.includes(user.role)) return { ok: false, status: 403 };
  if (siteId === undefined || siteId === null) return ALLOW;
  if (rule.allSites?.includes(user.role)) return ALLOW;
  // Site-bound roles only see their own site; anything else "does not exist".
  return user.site_id !== null && user.site_id === siteId ? ALLOW : { ok: false, status: 404 };
}

/**
 * Site filter for queries: the supervisor's own site, or null (= all sites) for
 * roles that may see every site. Never null for a supervisor.
 */
export function siteScope(user: SessionUser): number | null {
  if (user.role === 'supervisor') {
    if (user.site_id === null) throw new Error('supervisor without site');
    return user.site_id;
  }
  return null;
}

/**
 * SQL condition that keeps a supervisor inside their own site (DESIGN §10).
 * For a supervisor it appends the site id to `params` and returns
 * ` AND <column> = $n`; for roles that see every site it returns ''.
 * Every query on site data (photos, upload_batches, detections, result_overrides
 * through photos) adds this condition, so a wrong id can never reach another site.
 */
export function siteCondition(user: SessionUser, column: string, params: unknown[]): string {
  if (!/^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)?$/.test(column)) throw new Error('bad column name');
  const scope = siteScope(user);
  if (scope === null) return '';
  params.push(scope);
  return ` AND ${column} = $${params.length}`;
}

const MESSAGES: Record<401 | 403 | 404, { error: string; message: string }> = {
  401: { error: 'UNAUTHORIZED', message: 'กรุณาเข้าสู่ระบบ' },
  403: { error: 'FORBIDDEN', message: 'บัญชีนี้ไม่มีสิทธิ์ทำรายการนี้' },
  404: { error: 'NOT_FOUND', message: 'ไม่พบข้อมูล' },
};

export function deny(status: 401 | 403 | 404): NextResponse {
  return NextResponse.json(MESSAGES[status], { status, headers: { 'Cache-Control': 'no-store' } });
}

export function denyDecision(d: Decision): NextResponse | null {
  return d.ok ? null : deny(d.status);
}

/**
 * Resolve the session user of the request and check `action` (no specific site).
 * Returns either the user or the error response to send.
 */
export async function requireAccess(
  req: NextRequest,
  action: Action,
): Promise<{ user: SessionUser; res?: undefined } | { user?: undefined; res: NextResponse }> {
  const user = await getSessionUser(req);
  const d = canAccess(user, action);
  if (!d.ok || !user) return { res: deny(d.ok ? 401 : d.status) };
  return { user };
}
