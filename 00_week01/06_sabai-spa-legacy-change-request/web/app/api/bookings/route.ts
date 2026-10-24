import { createBooking, parseBookingInput } from "@/lib/server/booking.ts";
import { getLang, handle, json, readJson } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/bookings — จองจริง: 201 · 409 เวลาถูกจอง/ราคาเปลี่ยน · 422 ผิดกฎ */
export async function POST(req: Request) {
  return handle(async () => {
    const body = await readJson(req);
    const lang = await getLang(body.lang);
    const res = await createBooking(parseBookingInput(body), await getSession(), lang);
    return json(res, 201);
  });
}
