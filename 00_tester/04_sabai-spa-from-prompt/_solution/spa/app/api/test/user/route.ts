import { q1 } from "@/lib/server/db";
import { testResetAllowed } from "@/lib/server/env";
import { body, json } from "@/lib/server/http";
import { addDays, isDateStr } from "@/lib/time";
import { COURSE_DAYS } from "@/lib/rules";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** Test helper: set a member's total spend / points / birth month (only when ALLOW_TEST_RESET=1). */
export async function POST(req: Request) {
  if (!testResetAllowed()) return json({ ok: false, error: "NOT_FOUND" }, 404);
  const b = await body<{
    email?: string; totalSpent?: number; points?: number; birthMonth?: number; birthdayUsedYear?: number | null; coursePurchasedOn?: string; courseUsed?: number;
  }>(req);
  const u = await q1<{ id: number }>("SELECT id FROM users WHERE email = $1", [String(b.email ?? "").toLowerCase()]);
  if (!u) return json({ ok: false, error: "NOT_FOUND" }, 404);
  const int = (v: unknown) => (v === undefined || v === null ? null : Math.max(0, Math.floor(Number(v))));
  const month = b.birthMonth ? Math.min(12, Math.max(1, Math.floor(Number(b.birthMonth)))) : null;
  const row = await q1(
    `UPDATE users SET total_spent = COALESCE($2, total_spent), points = COALESCE($3, points), birth_month = COALESCE($4, birth_month),
       birthday_used_year = CASE WHEN $5::boolean THEN $6::int ELSE birthday_used_year END
     WHERE id = $1 RETURNING email, total_spent, points, birth_month, birthday_used_year`,
    [u.id, int(b.totalSpent), int(b.points), month, b.birthdayUsedYear !== undefined, b.birthdayUsedYear ?? null],
  );
  // optional: move the member's latest course (BR-15 day 180 / 181 tests) or set sessions used (BR-16)
  const course = await q1<{ id: number }>("SELECT id FROM courses WHERE user_id = $1 ORDER BY id DESC LIMIT 1", [u.id]);
  if (course && typeof b.coursePurchasedOn === "string" && isDateStr(b.coursePurchasedOn)) {
    await q1("UPDATE courses SET purchased_on = $2, expires_on = $3 WHERE id = $1", [course.id, b.coursePurchasedOn, addDays(b.coursePurchasedOn, COURSE_DAYS)]);
  }
  if (course && b.courseUsed !== undefined) {
    await q1("UPDATE courses SET used_sessions = LEAST(total_sessions, GREATEST(0, $2::int)) WHERE id = $1", [course.id, Math.floor(Number(b.courseUsed)) || 0]);
  }
  const c = course
    ? await q1("SELECT total_sessions, used_sessions, to_char(purchased_on,'YYYY-MM-DD') AS purchased_on, to_char(expires_on,'YYYY-MM-DD') AS expires_on FROM courses WHERE id = $1", [course.id])
    : null;
  return json({ ok: true, user: row, course: c });
}
