import { createBooking, myBookings, normalizeParams } from "@/lib/server/booking";
import { currentUser } from "@/lib/server/auth";
import { body, fail, handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** create a booking — the server re-checks every rule inside one transaction */
export async function POST(req: Request) {
  return handle(async () => {
    const p = normalizeParams(await body(req));
    const user = await currentUser();
    const booking = await createBooking(p, user);
    return json({ ok: true, booking }, 201);
  });
}

export async function GET() {
  return handle(async () => {
    const user = await currentUser();
    if (!user) return fail("LOGIN_REQUIRED", 401);
    return json({ ok: true, bookings: await myBookings(user) });
  });
}
