import { q1 } from "@/lib/server/db";
import { memberSummary, startSession, type UserRow } from "@/lib/server/auth";
import { verifyPassword } from "@/lib/server/password";
import { body, fail, handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(req: Request) {
  return handle(async () => {
    const b = await body<{ email?: string; password?: string }>(req);
    const email = String(b.email ?? "").trim().toLowerCase();
    const u = await q1<UserRow & { password_hash: string }>("SELECT * FROM users WHERE email = $1", [email]);
    if (!u || !verifyPassword(String(b.password ?? ""), u.password_hash)) return fail("LOGIN_FAILED", 401);
    await startSession(u.id);
    return json({ ok: true, user: await memberSummary(u) });
  });
}
