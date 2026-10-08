import { q } from "@/lib/server/db";
import { getNow } from "@/lib/server/clock";
import { handle, json } from "@/lib/server/http";
import { bookableRange, SHOP_PHONE } from "@/lib/time";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  return handle(async () => {
    const now = await getNow();
    const r = bookableRange(now);
    const hotels = await q<{ id: number; name: string; name_zh: string; distance_km: number }>(
      "SELECT id, name, name_zh, distance_km::float AS distance_km FROM hotels ORDER BY id",
    );
    return json({
      ok: true,
      now: now.toISOString(),
      today: r.today,
      bookable: { from: r.min, to: r.max },
      open: "10:00",
      close: "22:00",
      slotMinutes: 30,
      phone: SHOP_PHONE,
      hotels: hotels.map((h) => ({ id: h.id, name: h.name, nameZh: h.name_zh, distanceKm: Number(h.distance_km) })),
    });
  });
}
