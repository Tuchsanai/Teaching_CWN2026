// POST /api/admin/login {password} → set cookie bm_admin · DELETE → ออกจากระบบ
import { NextResponse } from 'next/server';
import { ADMIN_COOKIE, ADMIN_MAX_AGE, adminToken, checkPassword } from '../_auth';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  if (!checkPassword(body?.password)) {
    return NextResponse.json({ error: 'รหัสผ่านไม่ถูกต้อง' }, { status: 401 });
  }
  const res = NextResponse.json({ ok: true });
  res.cookies.set(ADMIN_COOKIE, adminToken(), { httpOnly: true, sameSite: 'lax', path: '/', maxAge: ADMIN_MAX_AGE });
  return res;
}

export async function DELETE() {
  const res = NextResponse.json({ ok: true });
  res.cookies.set(ADMIN_COOKIE, '', { httpOnly: true, sameSite: 'lax', path: '/', maxAge: 0 });
  return res;
}
