import { toSatang } from "@/lib/db.ts";
import { formatBaht, toBaht } from "@/lib/money.ts";
import { transportQuote } from "@/lib/rules/transport.ts";
import { getHotel } from "@/lib/server/catalog.ts";
import { ApiError, getLang, handle, json } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

/** GET /api/transport?distance=12&people=5[&hotel=H04][&package=1] (BR-17, BR-18, BR-19) */
export async function GET(req: Request) {
  return handle(async () => {
    const sp = new URL(req.url).searchParams;
    await getLang(sp.get("lang"));
    const people = Number(sp.get("people") ?? 1);
    if (!Number.isInteger(people) || people < 1 || people > 6) throw new ApiError(422, "BAD_PEOPLE");
    let distance = sp.get("distance") === null || sp.get("distance") === "" ? NaN : Number(sp.get("distance"));
    const hotel = sp.get("hotel");
    if (hotel) {
      const h = await getHotel(hotel.toUpperCase());
      if (!h) throw new ApiError(422, "BAD_REQUEST", { field: "hotel" });
      distance = h.distanceKm;
    }
    const q = transportQuote(distance, people, sp.get("package") === "1");
    if (!q.ok) throw new ApiError(422, q.code);
    return json({
      distanceKm: q.distanceKm,
      people,
      vehicles: q.vehicles,
      perVehicle: toBaht(q.perVehicle),
      fee: toBaht(q.fee),
      feeLabel: formatBaht(q.fee),
      free: q.fee === toSatang(0),
    });
  });
}
