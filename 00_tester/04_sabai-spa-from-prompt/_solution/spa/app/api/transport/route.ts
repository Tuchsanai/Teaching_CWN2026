import { q1 } from "@/lib/server/db";
import { handle, json, reqLang } from "@/lib/server/http";
import { transportQuote } from "@/lib/rules";
import { errorText } from "@/lib/i18n";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** FR-19: GET /api/transport?hotelId=4&people=5 → distance, cars, fee */
export async function GET(req: Request) {
  return handle(async () => {
    const sp = new URL(req.url).searchParams;
    const people = Math.max(1, Number(sp.get("people") ?? "1") || 1);
    const lang = await reqLang();
    const h = await q1<{ id: number; name: string; distance_km: number }>(
      "SELECT id, name, distance_km::float AS distance_km FROM hotels WHERE id = $1",
      [Number(sp.get("hotelId")) || 0],
    );
    if (!h) return json({ ok: false, error: "HOTEL_REQUIRED", message: errorText(lang, "HOTEL_REQUIRED") }, 400);
    const t = transportQuote(Number(h.distance_km), people);
    const { ok: available, ...rest } = t;
    return json({ ok: true, available, hotel: { id: h.id, name: h.name }, people, ...rest, ...(t.ok ? {} : { error: t.code, message: errorText(lang, t.code) }) });
  });
}
