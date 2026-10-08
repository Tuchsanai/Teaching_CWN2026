import { q1 } from "@/lib/server/db";
import { currentUser } from "@/lib/server/auth";
import { getNow } from "@/lib/server/clock";
import { fail, handle, json } from "@/lib/server/http";
import { addDays, bkkDate } from "@/lib/time";
import { COURSE_DAYS, COURSE_PRICE, COURSE_SERVICE, COURSE_SESSIONS } from "@/lib/rules";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** FR-12 / BR-15: buy a body-contouring course — ฿15,000, 11 sessions, valid 180 days from purchase */
export async function POST() {
  return handle(async () => {
    const u = await currentUser();
    if (!u) return fail("LOGIN_REQUIRED", 401);
    const today = bkkDate(await getNow());
    const expires = addDays(today, COURSE_DAYS);
    const c = await q1<{ id: number }>(
      `INSERT INTO courses (user_id, service_slug, total_sessions, used_sessions, price, purchased_on, expires_on) VALUES ($1,$2,$3,0,$4,$5,$6) RETURNING id`,
      [u.id, COURSE_SERVICE, COURSE_SESSIONS, COURSE_PRICE, today, expires],
    );
    return json({ ok: true, course: { id: c!.id, total: COURSE_SESSIONS, used: 0, left: COURSE_SESSIONS, price: COURSE_PRICE, purchasedOn: today, expiresOn: expires } }, 201);
  });
}
