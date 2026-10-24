import { rescheduleSlots } from "@/lib/server/booking.ts";
import { ApiError, getLang, handle, json } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** GET /api/bookings/:id/reschedule-slots?date=YYYY-MM-DD (CR-01) — รอบที่นักบำบัด (และห้องคู่) เดิมว่าง ไม่นับนัดตัวเอง */
export async function GET(req: Request, ctx: { params: Promise<{ id: string }> }) {
  return handle(async () => {
    const { id } = await ctx.params;
    const n = Number(String(id).replace(/^B/i, ""));
    if (!Number.isInteger(n) || n <= 0) throw new ApiError(404, "NOT_FOUND");
    const date = new URL(req.url).searchParams.get("date") ?? "";
    return json(await rescheduleSlots(n, date, await getSession(), await getLang()));
  });
}
