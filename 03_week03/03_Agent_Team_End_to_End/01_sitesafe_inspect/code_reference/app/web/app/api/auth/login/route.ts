// 2 · POST /api/auth/login — no login required (FR-18)
import { NextResponse, type NextRequest } from 'next/server';
import { canAccess, deny } from '@/lib/access';
import { authenticate, createSession, setSessionCookie } from '@/lib/auth';
import { apiError, isRecord, readJson, serverError } from '@/lib/http';
import { publicUser } from '@/lib/views';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  const d = canAccess(null, 'auth.login');
  if (!d.ok) return deny(d.status);

  const body = await readJson(req);
  if (!isRecord(body)) return apiError(400, 'BAD_REQUEST', 'รูปแบบคำขอไม่ถูกต้อง');
  try {
    const user = await authenticate(body.email, body.password);
    if (!user) {
      // Same answer for an unknown e-mail and a wrong password.
      return apiError(401, 'INVALID_CREDENTIALS', 'อีเมลหรือรหัสผ่านไม่ถูกต้อง');
    }
    const token = await createSession(user.id);
    const res = NextResponse.json({ user: publicUser(user) }, { status: 200, headers: { 'Cache-Control': 'no-store' } });
    setSessionCookie(res, token);
    return res;
  } catch (e) {
    return serverError('auth/login', e);
  }
}
