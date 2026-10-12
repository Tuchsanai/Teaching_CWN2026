import { rescheduleBooking } from "@/lib/server/booking.ts";
import { ApiError, getLang, handle, json, readJson } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/bookings/:id/reschedule {date, time} (CR-01) — ลูกค้าเลื่อนนัดของตัวเอง · :id เป็นเลข id หรือรหัส B05 ก็ได้ */
export async function POST(req: Request, ctx: { params: Promise<{ id: string }> }) {
  return handle(async () => {
    const { id } = await ctx.params;
    const n = Number(String(id).replace(/^B/i, ""));
    if (!Number.isInteger(n) || n <= 0) throw new ApiError(404, "NOT_FOUND");
    const body = await readJson(req);
    return json(await rescheduleBooking(n, body, await getSession(), await getLang()));
  });
}
