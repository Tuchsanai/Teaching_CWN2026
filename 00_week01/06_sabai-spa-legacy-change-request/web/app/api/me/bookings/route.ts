import { clock } from "@/lib/clock.ts";
import { getPool } from "@/lib/db.ts";
import { myBookings } from "@/lib/server/customer.ts";
import { ApiError, getLang, handle, json } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** GET /api/me/bookings — นัด + ประวัติ เรียงล่าสุด → เก่าสุด (FR-07, FR-17) */
export async function GET() {
  return handle(async () => {
    const s = await getSession();
    if (!s) throw new ApiError(401, "LOGIN_REQUIRED");
    const { now } = await clock();
    return json({ bookings: await myBookings(getPool(), s.uid, now, await getLang()) });
  });
}
