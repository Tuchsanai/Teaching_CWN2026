/**
 * W3 · POST /api/auth/login — ทุกคน
 * body: {"email","password"} (JSON หรือ form) → 200 {"user":{...}} + cookie rd_session
 * ผิด → 401 {"error":"invalid_credentials"}
 */
import { SESSION_TTL_HOURS, login, sessionCookie } from '../../_lib/auth';
import { ApiError, badRequest, handle, json } from '../../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

async function readCredentials(request: Request): Promise<{ email: string; password: string }> {
  const type = request.headers.get('content-type') ?? '';
  let email: unknown;
  let password: unknown;
  if (type.includes('application/x-www-form-urlencoded') || type.includes('multipart/form-data')) {
    const form = await request.formData();
    email = form.get('email');
    password = form.get('password');
  } else {
    let body: Record<string, unknown>;
    try {
      body = (await request.json()) as Record<string, unknown>;
    } catch {
      throw badRequest('ต้องส่ง email และ password');
    }
    email = body?.email;
    password = body?.password;
  }
  if (typeof email !== 'string' || typeof password !== 'string' || !email.trim() || !password) {
    throw badRequest('ต้องส่ง email และ password');
  }
  return { email, password };
}

export const POST = handle(async (request: Request) => {
  const { email, password } = await readCredentials(request);
  const result = await login(email, password);
  if (!result) throw new ApiError(401, 'invalid_credentials', 'อีเมลหรือรหัสผ่านไม่ถูกต้อง');
  const { token: _token, ...user } = result.user;
  void _token;
  return json({ user }, 200, {
    'Set-Cookie': sessionCookie(request, result.cookieValue, SESSION_TTL_HOURS * 3600),
  });
});
