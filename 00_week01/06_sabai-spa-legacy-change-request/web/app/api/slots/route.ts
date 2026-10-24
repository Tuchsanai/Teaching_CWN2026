import { availableSlots } from "@/lib/server/booking.ts";
import { getLang, handle, json } from "@/lib/server/http.ts";
import { BOOKING_TYPES, type BookingType } from "@/lib/rules/party.ts";
import { ApiError } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

/** GET /api/slots?service=S01&date=2026-10-11&type=single&people=1 */
export async function GET(req: Request) {
  return handle(async () => {
    const sp = new URL(req.url).searchParams;
    const lang = await getLang(sp.get("lang"));
    const type = (sp.get("type") ?? "single") as BookingType;
    if (!BOOKING_TYPES.includes(type)) throw new ApiError(422, "BAD_REQUEST", { field: "type" });
    const people = Number(sp.get("people") ?? (type === "couple" ? 2 : 1));
    const fallback = type === "package" ? "P01" : type === "course" ? "K01" : "";
    const serviceCode = (sp.get("service") ?? fallback).toUpperCase();
    return json(await availableSlots({ serviceCode, date: sp.get("date") ?? "", type, people }, lang));
  });
}
