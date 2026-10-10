import { listTherapists } from "@/lib/server/catalog.ts";
import { getLang, handle, json } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

/** GET /api/therapists?min=4.5&service=S01 (BR-08) */
export async function GET(req: Request) {
  return handle(async () => {
    const sp = new URL(req.url).searchParams;
    const lang = await getLang(sp.get("lang"));
    let list = await listTherapists(lang);
    if (sp.get("min") === "4.5") list = list.filter((t) => t.passes45);
    const svc = sp.get("service")?.toUpperCase();
    if (svc) list = list.filter((t) => t.services.includes(svc));
    return json({ therapists: list });
  });
}
