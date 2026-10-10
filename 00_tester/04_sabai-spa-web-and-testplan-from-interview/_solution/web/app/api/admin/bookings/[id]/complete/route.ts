import { completeBooking } from "@/lib/server/booking.ts";
import { ApiError, handle, json, readJson } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/admin/bookings/:id/complete {waistCm?} — ใช้บริการเสร็จ (owner) */
export async function POST(req: Request, ctx: { params: Promise<{ id: string }> }) {
  return handle(async () => {
    const { id } = await ctx.params;
    const n = Number(String(id).replace(/^B/i, ""));
    if (!Number.isInteger(n) || n <= 0) throw new ApiError(404, "NOT_FOUND");
    const body = await readJson(req);
    let waist: number | null = null;
    if (body.waistCm !== undefined && body.waistCm !== null && body.waistCm !== "") {
      waist = Number(body.waistCm);
      if (!Number.isFinite(waist) || waist <= 0 || waist > 300) throw new ApiError(422, "BAD_REQUEST", { field: "waistCm" });
      waist = Math.round(waist * 10) / 10;
    }
    return json(await completeBooking(n, waist, await getSession()));
  });
}
