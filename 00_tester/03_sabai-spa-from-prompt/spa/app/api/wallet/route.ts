import { q } from "@/lib/server/db";
import { currentUser } from "@/lib/server/auth";
import { getNow } from "@/lib/server/clock";
import { pickCourse, userCourses } from "@/lib/server/booking";
import { fail, handle, json } from "@/lib/server/http";
import { bkkDate } from "@/lib/time";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** FR-13: course sessions left + gift cards (own data only, NFR-08) */
export async function GET() {
  return handle(async () => {
    const u = await currentUser();
    if (!u) return fail("LOGIN_REQUIRED", 401);
    const today = bkkDate(await getNow());
    const courses = await userCourses(u.id);
    const { course, problem } = pickCourse(courses, today);
    const gifts = await q(
      `SELECT code, amount, balance, design, channel, recipient, recipient_name, to_char(purchased_on,'YYYY-MM-DD') AS purchased_on,
              to_char(expires_on,'YYYY-MM-DD') AS expires_on FROM gift_cards WHERE buyer_user_id = $1 ORDER BY created_at DESC`,
      [u.id],
    );
    return json({
      ok: true,
      today,
      courses: courses.map((c) => ({
        id: c.id,
        total: c.total_sessions,
        used: c.used_sessions,
        left: c.total_sessions - c.used_sessions,
        purchasedOn: c.purchased_on,
        expiresOn: c.expires_on,
        expired: today > c.expires_on,
      })),
      canBookWithCourse: !!course,
      courseProblem: problem,
      giftCards: gifts.map((g) => ({ ...g, expired: today > (g.expires_on as string) })),
    });
  });
}
