import { cancelBooking } from "@/lib/server/booking";
import { currentUser } from "@/lib/server/auth";
import { fail, handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(_req: Request, ctx: { params: Promise<{ id: string }> }) {
  return handle(async () => {
    const user = await currentUser();
    if (!user) return fail("LOGIN_REQUIRED", 401);
    const id = Number((await ctx.params).id);
    if (!Number.isInteger(id)) return fail("NOT_FOUND", 404);
    return json({ ok: true, booking: await cancelBooking(id, user) });
  });
}
