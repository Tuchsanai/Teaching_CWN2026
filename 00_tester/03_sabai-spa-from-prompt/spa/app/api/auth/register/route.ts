import { q1 } from "@/lib/server/db";
import { memberSummary, startSession, type UserRow } from "@/lib/server/auth";
import { hashPassword } from "@/lib/server/password";
import { body, fail, handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(req: Request) {
  return handle(async () => {
    const b = await body<{ name?: string; email?: string; password?: string; birthMonth?: number | string }>(req);
    const name = String(b.name ?? "").trim();
    const email = String(b.email ?? "").trim().toLowerCase();
    const password = String(b.password ?? "");
    const month = Number(b.birthMonth);
    if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || password.length < 8 || !(month >= 1 && month <= 12)) {
      return fail("REGISTER_INVALID");
    }
    const exists = await q1("SELECT id FROM users WHERE email = $1", [email]);
    if (exists) return fail("EMAIL_TAKEN", 409);
    const u = await q1<UserRow>(
      `INSERT INTO users (email, password_hash, name, name_en, birth_month) VALUES ($1,$2,$3,$3,$4)
       RETURNING id, email, name, name_en, birth_month, birth_day, total_spent, points, birthday_used_year`,
      [email, hashPassword(password), name.slice(0, 60), Math.floor(month)],
    );
    await startSession(u!.id);
    return json({ ok: true, user: await memberSummary(u!) }, 201);
  });
}
