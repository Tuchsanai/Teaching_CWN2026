// 3 · POST /api/auth/logout — every role (FR-18)
import { NextResponse, type NextRequest } from 'next/server';
import { canAccess, deny } from '@/lib/access';
import { clearSessionCookie, destroySession, getSessionUser, readSessionToken } from '@/lib/auth';
import { serverError } from '@/lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const user = await getSessionUser(req);
    const d = canAccess(user, 'auth.logout');
    if (!d.ok) {
      const res = deny(d.status);
      clearSessionCookie(res);
      return res;
    }
    const token = readSessionToken(req);
    if (token) await destroySession(token);
    const res = NextResponse.json({ ok: true }, { headers: { 'Cache-Control': 'no-store' } });
    clearSessionCookie(res);
    return res;
  } catch (e) {
    return serverError('auth/logout', e);
  }
}
