import { q } from "@/lib/server/db";
import { currentUser, memberSummary } from "@/lib/server/auth";
import { myBookings } from "@/lib/server/booking";
import { fail, handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** FR-09, FR-14, FR-15 — only ever returns the logged-in member's own data (NFR-08) */
export async function GET() {
  return handle(async () => {
    const u = await currentUser();
    if (!u) return fail("LOGIN_REQUIRED", 401);
    const bookings = await myBookings(u);
    const waist = await q<{ date: string; cm: number }>(
      "SELECT to_char(measured_on,'YYYY-MM-DD') AS date, cm::float AS cm FROM waist_measurements WHERE user_id = $1 ORDER BY measured_on",
      [u.id],
    );
    const photos = await q("SELECT id, to_char(taken_on,'YYYY-MM-DD') AS date, kind, image FROM body_photos WHERE user_id = $1 ORDER BY taken_on", [u.id]);
    const first = waist[0]?.cm;
    const last = waist[waist.length - 1]?.cm;
    return json({
      ok: true,
      member: await memberSummary(u),
      upcoming: bookings.filter((b) => !b.past && b.status === "confirmed").reverse(),
      history: bookings.filter((b) => b.past && b.status === "confirmed"),
      cancelled: bookings.filter((b) => b.status === "cancelled"),
      waist: waist.map((w) => ({ date: w.date, cm: Number(w.cm) })),
      waistDrop: waist.length >= 2 ? Math.round((first - last) * 10) / 10 : 0,
      photos,
    });
  });
}
