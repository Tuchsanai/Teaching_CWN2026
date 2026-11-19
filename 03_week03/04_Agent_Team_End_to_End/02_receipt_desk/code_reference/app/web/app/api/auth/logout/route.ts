/**
 * W4 · POST /api/auth/logout — ผู้เข้าสู่ระบบ (ไม่มี session → 401)
 */
import { clearSessionCookie, logout, requireUser } from '../../_lib/auth';
import { handle, json } from '../../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export const POST = handle(async (request: Request) => {
  const user = await requireUser(request);
  await logout(user);
  return json({ ok: true }, 200, { 'Set-Cookie': clearSessionCookie(request) });
});
