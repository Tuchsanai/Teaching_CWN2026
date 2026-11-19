/**
 * Session helpers for Server Components (pages and layouts).
 * The session is always resolved on the server from the HttpOnly cookie and
 * checked against the database by lib/auth — the browser never sees the token
 * or any key. Permissions come only from canAccess() in lib/access.
 */
import { cache } from 'react';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { NextRequest } from 'next/server';
import { canAccess, siteCondition, type Action } from '@/lib/access';
import { getSessionUser, type SessionUser } from '@/lib/auth';
import { pool } from '@/lib/db';
import { SESSION_COOKIE } from '@/lib/session-cookie';

/** Logged-in user of the current page request, or null (cached per request). */
export const currentUser = cache(async (): Promise<SessionUser | null> => {
  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  if (!token) return null;
  const req = new NextRequest('http://localhost/', {
    headers: { cookie: `${SESSION_COOKIE}=${token}` },
  });
  return getSessionUser(req);
});

/** The logged-in user; anyone else is sent to /login (FR-18). */
export async function requireUser(): Promise<SessionUser> {
  const user = await currentUser();
  if (!user) redirect('/login');
  return user;
}

export function can(user: SessionUser, action: Action, siteId?: number | null): boolean {
  return canAccess(user, action, siteId).ok;
}

/** Menu entries the role may see (DESIGN 7.4: hidden when not allowed; the API still decides). */
export function menuFor(user: SessionUser) {
  return {
    upload: can(user, 'upload.create'),
    photos: can(user, 'photo.view'),
    problems: can(user, 'photo.view'),
    report: can(user, 'report.view'),
  };
}

/** First page after login, by role. */
export function homePathFor(user: SessionUser): string {
  const m = menuFor(user);
  if (m.upload) return '/upload';
  if (m.problems) return '/photos/problems';
  return '/reports/daily';
}

export type SiteOption = { code: string; name: string };

/** Sites the user may see (supervisor: own site only), for the site filters. */
export async function visibleSites(user: SessionUser): Promise<SiteOption[]> {
  const params: unknown[] = [];
  const where = siteCondition(user, 'id', params);
  const r = await pool().query<SiteOption>(
    `SELECT code, name FROM sites WHERE true${where} ORDER BY code`,
    params,
  );
  return r.rows;
}

/** Only allow a relative in-app path as the post-login target. */
export function safeNextPath(raw: unknown): string | null {
  if (typeof raw !== 'string') return null;
  if (!raw.startsWith('/') || raw.startsWith('//') || raw.startsWith('/\\')) return null;
  if (raw.startsWith('/login') || raw.startsWith('/api/')) return null;
  return raw;
}
