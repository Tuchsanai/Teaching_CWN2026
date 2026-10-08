import { buildQuote, normalizeParams } from "@/lib/server/booking";
import { currentUser } from "@/lib/server/auth";
import { getNow } from "@/lib/server/clock";
import { body, handle, json, reqLang } from "@/lib/server/http";
import { errorText } from "@/lib/i18n";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** FR-06: price breakdown. Problems (gift card expired, too far, …) come back in "issues" with messages. */
export async function POST(req: Request) {
  return handle(async () => {
    const p = normalizeParams(await body(req));
    const user = await currentUser();
    const r = await buildQuote(p, user, await getNow());
    const lang = await reqLang();
    return json({
      ok: true,
      quote: r.quote,
      kind: r.kind,
      member: !!user,
      birthday: r.birthday,
      hotel: r.hotel ? { id: r.hotel.id, name: r.hotel.name, nameZh: r.hotel.name_zh, distanceKm: Number(r.hotel.distance_km) } : null,
      issues: r.issues.map((code) => ({ code, message: errorText(lang, code) })),
    });
  });
}
