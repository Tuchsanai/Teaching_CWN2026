import { clock } from "@/lib/clock.ts";
import { isDateString } from "@/lib/rules/time.ts";
import { queueForDate } from "@/lib/server/admin.ts";
import { ApiError, getLang, handle, json } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** GET /api/admin/bookings?date=YYYY-MM-DD — ตารางคิว (owner เท่านั้น) */
export async function GET(req: Request) {
  return handle(async () => {
    const s = await getSession();
    if (!s) throw new ApiError(401, "LOGIN_REQUIRED");
    if (s.role !== "owner") throw new ApiError(403, "FORBIDDEN");
    const { today } = await clock();
    const date = new URL(req.url).searchParams.get("date") ?? today;
    if (!isDateString(date)) throw new ApiError(422, "BAD_REQUEST", { field: "date" });
    return json({ date, today, bookings: await queueForDate(date, await getLang()) });
  });
}
