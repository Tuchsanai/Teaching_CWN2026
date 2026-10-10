import { isMood, recommendForMood } from "@/lib/bot/mood.ts";
import { listServices } from "@/lib/server/catalog.ts";
import { ApiError, getLang, handle, json } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

/** GET /api/mood?mood=stressed|tired|aches|insomnia (FR-27) */
export async function GET(req: Request) {
  return handle(async () => {
    const sp = new URL(req.url).searchParams;
    const mood = sp.get("mood");
    if (!isMood(mood)) throw new ApiError(422, "BAD_REQUEST", { field: "mood" });
    const lang = await getLang(sp.get("lang"));
    const rec = recommendForMood(mood, lang);
    const all = await listServices(lang);
    return json({ ...rec, services: rec.services.map((c) => all.find((s) => s.code === c)!) });
  });
}
