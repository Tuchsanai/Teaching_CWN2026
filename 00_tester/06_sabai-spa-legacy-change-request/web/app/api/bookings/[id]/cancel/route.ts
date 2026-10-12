import { cancelBooking } from "@/lib/server/booking.ts";
import { ApiError, handle, json } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/bookings/:id/cancel (FR-07, BR-07) — :id เป็นเลข id หรือรหัส B05 ก็ได้ */
export async function POST(_req: Request, ctx: { params: Promise<{ id: string }> }) {
  return handle(async () => {
    const { id } = await ctx.params;
    const n = Number(String(id).replace(/^B/i, ""));
    if (!Number.isInteger(n) || n <= 0) throw new ApiError(404, "NOT_FOUND");
    return json(await cancelBooking(n, await getSession()));
  });
}
