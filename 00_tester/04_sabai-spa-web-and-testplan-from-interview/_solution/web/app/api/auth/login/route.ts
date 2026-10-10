import bcrypt from "bcryptjs";
import { NextResponse } from "next/server";
import { query } from "@/lib/db.ts";
import { ApiError, getLang, handle, readJson } from "@/lib/server/http.ts";
import { encodeSession, SESSION_COOKIE, sessionCookieOptions } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/auth/login {email, password} → ตั้ง cookie httpOnly */
export async function POST(req: Request) {
  return handle(async () => {
    const body = await readJson(req);
    await getLang(body.lang);
    const email = String(body.email ?? "").trim().toLowerCase();
    const password = String(body.password ?? "");
    const r = await query("SELECT id, name, email, role, password_hash FROM customer WHERE lower(email) = $1", [email]);
    const u = r.rows[0];
    if (!u || !u.password_hash || !(await bcrypt.compare(password, u.password_hash))) throw new ApiError(401, "LOGIN_FAILED");
    const res = NextResponse.json({ ok: true, user: { id: u.id, name: u.name, email: u.email, role: u.role } });
    res.cookies.set(SESSION_COOKIE, encodeSession({ uid: u.id, role: u.role }), sessionCookieOptions);
    return res;
  });
}
